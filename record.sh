#!/bin/bash
# Meeting Transcriber - System-level audio recording utility
# Launches the Docker-based recorder from any location

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Determine project root: prefer RECORDER_HOME, fallback to TRANSCRIBER_HOME, then script dir
if [ -n "$RECORDER_HOME" ]; then
    PROJECT_ROOT="$RECORDER_HOME"
elif [ -n "$TRANSCRIBER_HOME" ]; then
    PROJECT_ROOT="$TRANSCRIBER_HOME"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$SCRIPT_DIR"
fi

START_SCRIPT="$PROJECT_ROOT/scripts/start_recording.sh"
DOCKERFILE="$PROJECT_ROOT/Dockerfile.recording"

if [ ! -f "$START_SCRIPT" ]; then
    echo -e "${RED}Error: cannot locate start_recording.sh at${NC} $START_SCRIPT"
    echo "Ensure RECORDER_HOME or TRANSCRIBER_HOME points to the repository root."
    exit 1
fi

if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}Error: Dockerfile.recording not found at${NC} $DOCKERFILE"
    exit 1
fi

# Help message
if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    cat <<EOF
${BLUE}Meeting Transcriber - Desktop Recording Utility${NC}

Usage: record.sh [options]

Options (forwarded to start_recording.sh):
  --name LABEL        Optional filename label (saved as ./input/<timestamp>_<label>.mp3)
  --duration SECONDS  Recording duration (max 3600, default 3600)
  --device ALSA       ALSA capture device for Linux hosts (default: default)
  --pulse-host HOST   PulseAudio host for macOS (default: host.docker.internal:4713)
  --image IMAGE       Docker image tag (default: meeting-recorder:latest)

Examples:
  record.sh --name daily-sync
  record.sh --duration 600
  record.sh --device hw:1,0 --name notes

Recordings are stored under: $PROJECT_ROOT/input/
EOF
    exit 0
fi

# Check Docker availability
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon not reachable.${NC}"
    echo "Start Docker or ensure your user has permission to access /var/run/docker.sock."
    exit 1
fi

mkdir -p "$PROJECT_ROOT/input"

echo -e "${BLUE}Starting recording using project at:${NC} $PROJECT_ROOT"

exec "$START_SCRIPT" "$@"
