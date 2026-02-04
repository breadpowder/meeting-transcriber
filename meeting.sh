#!/bin/bash
# Meeting Transcriber - Unified record and transcribe workflow
# Records audio, then automatically transcribes with detailed notes when stopped

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
TRANSCRIBE_SCRIPT="$PROJECT_ROOT/transcribe.sh"

# Verify required files exist
if [ ! -f "$START_SCRIPT" ]; then
    echo -e "${RED}Error: cannot locate start_recording.sh at${NC} $START_SCRIPT"
    echo "Ensure RECORDER_HOME or TRANSCRIBER_HOME points to the repository root."
    exit 1
fi

if [ ! -f "$TRANSCRIBE_SCRIPT" ]; then
    echo -e "${RED}Error: cannot locate transcribe.sh at${NC} $TRANSCRIBE_SCRIPT"
    exit 1
fi

# Default transcription mode
TRANSCRIBE_MODE="--detailed-notes"
TRANSCRIBE_ARGS=()
RECORD_ARGS=()
GPT_MODEL=""

# Help message
show_help() {
    cat <<EOF
${BLUE}Meeting Transcriber - Unified Record & Transcribe${NC}

Usage: meeting.sh [options]

This script records audio and automatically transcribes it when you stop recording.
Press Ctrl+C to stop recording - transcription will start automatically.

Recording Options:
  --name LABEL        Meeting name/label for filename
  --duration SECONDS  Max recording duration (default: 3600, max: 7200)
  --device ALSA       ALSA capture device for Linux (default: default)
  --pulse-host HOST   PulseAudio host for macOS (default: host.docker.internal:4713)
  --image IMAGE       Docker image tag (default: meeting-recorder:latest)

Transcription Options:
  --detailed-notes    Generate detailed notes (default)
  --summary-only      Generate concise summary instead of detailed notes
  --skip-summary      Transcript only, no AI processing
  -m, --model MODEL   GPT model for notes/summary (default: gpt-4o-mini)

Examples:
  meeting.sh --name daily-sync
  meeting.sh --name standup --duration 900
  meeting.sh --name quick-chat --summary-only
  meeting.sh --name important -m gpt-4o

Output:
  Recording:    $PROJECT_ROOT/input/<name>_<timestamp>.mp3
  Transcript:   $PROJECT_ROOT/output/<name>_transcript.txt
  Notes/Summary: $PROJECT_ROOT/output/<name>_detailed_notes.md (or _summary.md)
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            ;;
        # Recording args
        --name|--duration|--device|--pulse-host|--image)
            RECORD_ARGS+=("$1" "$2")
            shift 2
            ;;
        # Transcription mode args
        --detailed-notes)
            TRANSCRIBE_MODE="--detailed-notes"
            shift
            ;;
        --summary-only)
            TRANSCRIBE_MODE=""
            shift
            ;;
        --skip-summary)
            TRANSCRIBE_MODE="--skip-summary"
            shift
            ;;
        -m|--model)
            GPT_MODEL="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Build transcription args
if [ -n "$TRANSCRIBE_MODE" ]; then
    TRANSCRIBE_ARGS+=("$TRANSCRIBE_MODE")
fi
if [ -n "$GPT_MODEL" ]; then
    TRANSCRIBE_ARGS+=("-m" "$GPT_MODEL")
fi

# Check Docker availability
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon not reachable.${NC}"
    echo "Start Docker or ensure your user has permission to access /var/run/docker.sock."
    exit 1
fi

# Ensure input directory exists
mkdir -p "$PROJECT_ROOT/input"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Meeting Transcriber - Unified Workflow${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""
echo -e "${GREEN}Recording will start. Press Ctrl+C to stop and begin transcription.${NC}"
echo ""

# Create temp file to capture recording output
TEMP_OUTPUT=$(mktemp)
trap "rm -f $TEMP_OUTPUT" EXIT

# Run recording and capture output
# Use a subshell to handle the recording and capture its output
set +e  # Don't exit on error (Ctrl+C causes non-zero exit)
"$START_SCRIPT" "${RECORD_ARGS[@]}" 2>&1 | tee "$TEMP_OUTPUT"
RECORD_EXIT=${PIPESTATUS[0]}
set -e

# Check for recording errors (exit code 1 = error, 130 = Ctrl+C which is expected)
# Exit codes 128+ are signals (130 = 128 + SIGINT), which are normal for Ctrl+C stop
if [ "$RECORD_EXIT" -ne 0 ] && [ "$RECORD_EXIT" -lt 128 ]; then
    echo -e "${RED}Error: Recording failed (exit code $RECORD_EXIT).${NC}"
    exit 1
fi

# Extract recording file path from output
RECORDING_FILE=$(grep "^RECORDING_FILE:" "$TEMP_OUTPUT" | tail -1 | cut -d: -f2-)

if [ -z "$RECORDING_FILE" ]; then
    # Fallback: try to find the most recent file in input/
    echo -e "${YELLOW}Warning: Could not capture recording filename from output.${NC}"
    RECORDING_FILE=$(ls -t "$PROJECT_ROOT/input/"*.mp3 2>/dev/null | head -1)
    if [ -z "$RECORDING_FILE" ]; then
        echo -e "${RED}Error: No recording file found.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Using most recent recording: $RECORDING_FILE${NC}"
fi

# Verify recording file exists
if [ ! -f "$RECORDING_FILE" ]; then
    echo -e "${RED}Error: Recording file not found: $RECORDING_FILE${NC}"
    exit 1
fi

FILENAME=$(basename "$RECORDING_FILE")
echo ""
echo -e "${GREEN}Recording complete: $FILENAME${NC}"
echo ""

# Start transcription
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Starting Transcription...${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

"$TRANSCRIBE_SCRIPT" "$RECORDING_FILE" "${TRANSCRIBE_ARGS[@]}"

echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}Meeting processing complete!${NC}"
echo -e "${GREEN}=====================================================================${NC}"
