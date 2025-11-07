#!/bin/bash
# Meeting Transcriber - System-level audio transcription utility
# Can be run from anywhere after installation

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Determine the project root directory
# If TRANSCRIBER_HOME is set, use it; otherwise detect from script location
if [ -n "$TRANSCRIBER_HOME" ]; then
    PROJECT_ROOT="$TRANSCRIBER_HOME"
else
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$SCRIPT_DIR"
fi

# Verify project root has required files
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo -e "${RED}Error: Cannot find docker-compose.yml${NC}"
    echo "Expected at: $PROJECT_ROOT/docker-compose.yml"
    echo ""
    echo "Please set TRANSCRIBER_HOME environment variable to the project directory:"
    echo "  export TRANSCRIBER_HOME=/path/to/speech-to-text"
    exit 1
fi

# Print usage
if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo -e "${BLUE}Meeting Transcriber - Simple Audio Transcription${NC}"
    echo ""
    echo "Usage: transcribe.sh <path-to-audio-file> [options]"
    echo ""
    echo "Examples:"
    echo "  transcribe.sh meeting.mp3"
    echo "  transcribe.sh meeting.mp3 --detailed-notes"
    echo "  transcribe.sh meeting.mp3 --skip-summary"
    echo "  transcribe.sh meeting.mp3 -m gpt-4o"
    echo "  transcribe.sh /path/to/meeting.wav -o /app/output/custom"
    echo ""
    echo "Common Options:"
    echo "  --skip-summary        Transcribe only, no AI processing"
    echo "  --detailed-notes      Generate detailed notes (preserves all details)"
    echo "  -m, --model MODEL     GPT model for summary/notes (default: gpt-4o-mini)"
    echo "  -o, --output DIR      Output directory (default: /app/output)"
    echo "  -l, --language LANG   Force language (en or zh)"
    echo "  -v, --verbose         Verbose logging"
    echo ""
    echo "Output Location:"
    echo "  All results are saved to: $PROJECT_ROOT/output/"
    echo "  - Transcripts:      <filename>_transcript.txt"
    echo "  - Summaries:        <filename>_summary.md"
    echo "  - Detailed Notes:   <filename>_detailed_notes.md (with --detailed-notes)"
    echo ""
    echo "Project Location: $PROJECT_ROOT"
    exit 0
fi

AUDIO_FILE="$1"
shift  # Remove first argument, keep rest as options

# Convert to absolute path if relative
if [[ "$AUDIO_FILE" != /* ]]; then
    # Relative path - resolve from current working directory
    AUDIO_DIR="$(cd "$(dirname "$AUDIO_FILE")" 2>/dev/null && pwd)" || AUDIO_DIR="$(pwd)"
    AUDIO_FILE="$AUDIO_DIR/$(basename "$AUDIO_FILE")"
fi

# Check if file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo -e "${RED}Error: File '$AUDIO_FILE' not found${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if .env exists in project root
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Expected at: $PROJECT_ROOT/.env"
    echo ""
    echo "Please create .env in the project directory with your OPENAI_API_KEY"
    echo ""
    echo "Example .env content:"
    echo "OPENAI_API_KEY=sk-proj-your-key-here"
    echo "WHISPER_MODEL=large-v3"
    echo "WHISPER_DEVICE=cuda"
    echo ""
    echo "To create it:"
    echo "  cd $PROJECT_ROOT"
    echo "  nano .env  # or use your preferred editor"
    exit 1
fi

# Get filename
FILENAME=$(basename "$AUDIO_FILE")

# Create audio directory in project root if it doesn't exist
mkdir -p "$PROJECT_ROOT/audio"

# Copy to audio directory if not already there
if [ ! -f "$PROJECT_ROOT/audio/$FILENAME" ]; then
    echo -e "${YELLOW}Copying audio file to $PROJECT_ROOT/audio/...${NC}"
    mv "$AUDIO_FILE" "$PROJECT_ROOT/audio/$FILENAME"
    echo -e "${GREEN}✓ Audio file copied${NC}"
fi

# Run transcription from project directory
echo ""
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Transcribing: $FILENAME${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

# Change to project directory to run docker compose
cd "$PROJECT_ROOT"
docker compose run --rm meeting-transcriber transcribe "/app/audio/$FILENAME" "$@"

# Check if output was created
BASENAME="${FILENAME%.*}"
if [ -f "$PROJECT_ROOT/output/${BASENAME}_transcript.txt" ]; then
    echo ""
    echo -e "${GREEN}=====================================================================${NC}"
    echo -e "${GREEN}✓ Transcription Complete!${NC}"
    echo -e "${GREEN}=====================================================================${NC}"
    echo ""
    echo -e "${GREEN}Results saved to: $PROJECT_ROOT/output/${NC}"
    echo "  Transcript:      ${BASENAME}_transcript.txt"
    if [ -f "$PROJECT_ROOT/output/${BASENAME}_summary.md" ]; then
        echo "  Summary:         ${BASENAME}_summary.md"
    fi
    if [ -f "$PROJECT_ROOT/output/${BASENAME}_detailed_notes.md" ]; then
        echo "  Detailed Notes:  ${BASENAME}_detailed_notes.md"
    fi
    echo ""
else
    echo -e "${YELLOW}Note: Check $PROJECT_ROOT/output/ directory for results${NC}"
fi
