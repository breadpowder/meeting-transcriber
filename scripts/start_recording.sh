#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

IMAGE_TAG="meeting-recorder:latest"
MAX_DURATION=7200
duration="${MAX_DURATION}"
user_label=""
alsa_device="default"
pulse_host=""

usage() {
  cat <<'EOF'
Usage: start_recording.sh [--name LABEL] [--duration SECONDS] [--device ALSA_DEVICE] [--pulse-host HOST[:PORT]] [--image IMAGE_TAG]

Records microphone input to ./input/<timestamp>_<label>.mp3 using Docker.

Options:
  --name LABEL        Optional descriptive label appended to the filename.
  --duration SECONDS  Recording duration in seconds (max 3600, default 3600).
  --device ALSA       ALSA capture device for Linux hosts (default: default).
  --pulse-host HOST   PulseAudio server for macOS (default: host.docker.internal:4713).
  --image IMAGE       Docker image tag to use (default: meeting-recorder:latest).
  -h, --help          Show this help.
EOF
}

sanitize_label() {
  local input="$1"
  input="$(echo "${input}" | tr '[:upper:]' '[:lower:]')"
  input="$(echo "${input}" | tr ' ' '-' | tr -cd '[:alnum:]._%\-')"
  echo "${input}"
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker CLI not found in PATH." >&2
    exit 1
  fi
}

ensure_image() {
  if docker image inspect "${IMAGE_TAG}" >/dev/null 2>&1; then
    return
  fi
  local dockerfile="${REPO_ROOT}/Dockerfile.recording"
  if [[ ! -f "${dockerfile}" ]]; then
    echo "Error: ${dockerfile} not found; cannot build ${IMAGE_TAG}." >&2
    exit 1
  fi
  echo "Docker image ${IMAGE_TAG} not found. Building with ${dockerfile}..."
  docker build -f "${dockerfile}" -t "${IMAGE_TAG}" "${REPO_ROOT}"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name)
        [[ $# -lt 2 ]] && { echo "Error: --name requires a value." >&2; exit 1; }
        user_label="$(sanitize_label "$2")"
        shift 2
        ;;
      --duration)
        [[ $# -lt 2 ]] && { echo "Error: --duration requires a value." >&2; exit 1; }
        if ! [[ "$2" =~ ^[0-9]+$ ]]; then
          echo "Error: --duration must be an integer." >&2
          exit 1
        fi
        duration="$2"
        shift 2
        ;;
      --device)
        [[ $# -lt 2 ]] && { echo "Error: --device requires a value." >&2; exit 1; }
        alsa_device="$2"
        shift 2
        ;;
      --pulse-host)
        [[ $# -lt 2 ]] && { echo "Error: --pulse-host requires a value." >&2; exit 1; }
        pulse_host="$2"
        shift 2
        ;;
      --image)
        [[ $# -lt 2 ]] && { echo "Error: --image requires a value." >&2; exit 1; }
        IMAGE_TAG="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Error: Unknown option $1" >&2
        usage
        exit 1
        ;;
    esac
  done
}

finalize_duration() {
  if (( duration > MAX_DURATION )); then
    echo "Warning: duration capped at ${MAX_DURATION} seconds." >&2
    duration="${MAX_DURATION}"
  elif (( duration == 0 )); then
    echo "Error: duration must be greater than zero." >&2
    exit 1
  fi
}

prepare_output_path() {
  local timestamp
  timestamp="$(date +"%Y%m%d_%H%M%S")"
  local base="${timestamp}"
  if [[ -n "${user_label}" ]]; then
    base="${user_label}_${base}"
  fi

  mkdir -p "${REPO_ROOT}/input"
  local file="input/${base}.mp3"
  local counter=1
  while [[ -e "${REPO_ROOT}/${file}" ]]; do
    file="input/${base}_${counter}.mp3"
    ((counter++))
  done
  RECORDING_PATH="${REPO_ROOT}/${file}"
  RELATIVE_PATH="${file}"
}

build_docker_args() {
  DOCKER_ARGS=(--rm --interactive)
  # Only add --tty if connected to a terminal
  if [ -t 0 ]; then
    DOCKER_ARGS+=("--tty")
  fi
  DOCKER_ARGS+=("--name" "recorder_${RANDOM}")
  DOCKER_ARGS+=("--volume" "${REPO_ROOT}/input:/recordings")

  case "${HOST_OS}" in
    linux)
      # Run container as current user for proper permissions
      DOCKER_ARGS+=("--user" "$(id -u):$(id -g)")

      # Add audio group access for ALSA devices
      local audio_gid
      audio_gid=$(getent group audio | cut -d: -f3 2>/dev/null || echo "29")
      DOCKER_ARGS+=("--group-add" "${audio_gid}")

      # Enable IPC for PulseAudio shared memory
      DOCKER_ARGS+=("--ipc=host")

      if [[ -d "/dev/snd" ]]; then
        DOCKER_ARGS+=("--device" "/dev/snd")
      else
        echo "Warning: /dev/snd not present; ALSA capture may fail." >&2
      fi
      if [[ -n "${XDG_RUNTIME_DIR:-}" && -S "${XDG_RUNTIME_DIR}/pulse/native" ]]; then
        DOCKER_ARGS+=("--volume" "${XDG_RUNTIME_DIR}/pulse/native:/run/pulse/native")
        DOCKER_ARGS+=("--env" "PULSE_SERVER=unix:/run/pulse/native")

        # Set HOME for PulseAudio config and mount pulse directory for authentication
        DOCKER_ARGS+=("--env" "HOME=/home/user")
        local pulse_config="${HOME}/.config/pulse"
        if [[ -d "${pulse_config}" ]]; then
          DOCKER_ARGS+=("--volume" "${pulse_config}:/home/user/.config/pulse:ro")
        fi

        INPUT_FORMAT="pulse"
        INPUT_SOURCE="@DEFAULT_SOURCE@"
      else
        INPUT_FORMAT="alsa"
        INPUT_SOURCE="${alsa_device}"
      fi
      ;;
    darwin)
      local server="${pulse_host:-host.docker.internal:4713}"
      DOCKER_ARGS+=("--env" "PULSE_SERVER=tcp:${server}")
      INPUT_FORMAT="pulse"
      INPUT_SOURCE="@DEFAULT_SOURCE@"
      ;;
    *)
      echo "Error: unsupported host OS '${HOST_OS}'." >&2
      exit 1
      ;;
  esac
}

run_container() {
  local ffmpeg_cmd=(
    "-hide_banner"
    "-loglevel" "info"
    "-f" "${INPUT_FORMAT}"
    "-ac" "2"
    "-ar" "44100"
    "-i" "${INPUT_SOURCE}"
    "-t" "${duration}"
    "-c:a" "libmp3lame"
    "-b:a" "192k"
    "/recordings/$(basename "${RECORDING_PATH}")"
  )

  echo "Recording to ${RELATIVE_PATH}"
  echo "Running: docker run ${DOCKER_ARGS[*]} ${IMAGE_TAG} ${ffmpeg_cmd[*]}"

  docker run "${DOCKER_ARGS[@]}" "${IMAGE_TAG}" "${ffmpeg_cmd[@]}"
}

main() {
  parse_args "$@"
  finalize_duration
  ensure_docker
  ensure_image
  HOST_OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
  prepare_output_path
  build_docker_args
  run_container
  echo "Recording saved to ${RELATIVE_PATH}"
  echo "RECORDING_FILE:${RECORDING_PATH}"
}

main "$@"
