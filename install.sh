#!/bin/bash
# Installation script for Meeting Transcriber system-level utility
# This script installs transcribe.sh to PATH and sets up the environment

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Meeting Transcriber - System Installation${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Project directory: $PROJECT_DIR"
echo ""

# Determine installation location
if [ -d "$HOME/.local/bin" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    echo -e "${GREEN}Installing to user directory: $INSTALL_DIR${NC}"
elif [ -d "$HOME/bin" ]; then
    INSTALL_DIR="$HOME/bin"
    echo -e "${GREEN}Installing to user directory: $INSTALL_DIR${NC}"
else
    # Create ~/.local/bin if it doesn't exist
    INSTALL_DIR="$HOME/.local/bin"
    echo -e "${YELLOW}Creating directory: $INSTALL_DIR${NC}"
    mkdir -p "$INSTALL_DIR"
fi

echo ""

# Check if install directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}Warning: $INSTALL_DIR is not in your PATH${NC}"
    echo ""
    echo "Add the following line to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    read -p "Press Enter to continue..."
    echo ""
fi

# Create symlink to transcribe.sh
SCRIPT_PATH="$PROJECT_DIR/transcribe.sh"
INSTALL_PATH="$INSTALL_DIR/transcribe"

if [ -L "$INSTALL_PATH" ] || [ -f "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}Removing existing installation: $INSTALL_PATH${NC}"
    rm -f "$INSTALL_PATH"
fi

echo -e "${GREEN}Creating symlink: $INSTALL_PATH -> $SCRIPT_PATH${NC}"
ln -s "$SCRIPT_PATH" "$INSTALL_PATH"
chmod +x "$SCRIPT_PATH"

# Create symlink to meeting.sh (unified workflow)
MEETING_SCRIPT="$PROJECT_DIR/meeting.sh"
MEETING_INSTALL="$INSTALL_DIR/meeting"

if [ -L "$MEETING_INSTALL" ] || [ -f "$MEETING_INSTALL" ]; then
    echo -e "${YELLOW}Removing existing installation: $MEETING_INSTALL${NC}"
    rm -f "$MEETING_INSTALL"
fi

echo -e "${GREEN}Creating symlink: $MEETING_INSTALL -> $MEETING_SCRIPT${NC}"
ln -s "$MEETING_SCRIPT" "$MEETING_INSTALL"
chmod +x "$MEETING_SCRIPT"

# Set up environment variable
SHELL_RC=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    # Try to detect shell from $SHELL
    case "$SHELL" in
        */bash)
            SHELL_RC="$HOME/.bashrc"
            ;;
        */zsh)
            SHELL_RC="$HOME/.zshrc"
            ;;
        *)
            SHELL_RC="$HOME/.profile"
            ;;
    esac
fi

echo ""
echo -e "${BLUE}Setting up TRANSCRIBER_HOME environment variable...${NC}"
echo ""

# Check if TRANSCRIBER_HOME is already set
if grep -q "TRANSCRIBER_HOME" "$SHELL_RC" 2>/dev/null; then
    echo -e "${YELLOW}TRANSCRIBER_HOME already configured in $SHELL_RC${NC}"
    echo "Current value will be preserved"
else
    echo "Adding TRANSCRIBER_HOME to $SHELL_RC"
    echo "" >> "$SHELL_RC"
    echo "# Meeting Transcriber configuration" >> "$SHELL_RC"
    echo "export TRANSCRIBER_HOME=\"$PROJECT_DIR\"" >> "$SHELL_RC"
    echo "" >> "$SHELL_RC"
    echo -e "${GREEN}✓ Added to $SHELL_RC${NC}"
fi

# Set for current session
export TRANSCRIBER_HOME="$PROJECT_DIR"

echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""
echo "Commands installed:"
echo "  ${BLUE}transcribe${NC} - Transcribe existing audio files"
echo "  ${BLUE}meeting${NC}    - Record and auto-transcribe (unified workflow)"
echo ""
echo "Project location: ${BLUE}$PROJECT_DIR${NC}"
echo ""
echo "Usage:"
echo "  ${BLUE}meeting --name daily-sync${NC}"
echo "      Record audio, press Ctrl+C to stop, auto-transcribes with detailed notes"
echo ""
echo "  ${BLUE}transcribe meeting.mp3${NC}"
echo "      Transcribe an existing audio file"
echo ""
echo "To use immediately:"
echo "  source $SHELL_RC"
echo "  meeting --help"
echo ""
echo "Or simply open a new terminal window"
echo ""
