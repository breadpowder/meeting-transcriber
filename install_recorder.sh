#!/bin/bash
# Installation script for Meeting Transcriber recorder utility

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Meeting Transcriber - Recorder Installation${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project directory: $PROJECT_DIR"
echo ""

if [ -d "$HOME/.local/bin" ]; then
    INSTALL_DIR="$HOME/.local/bin"
elif [ -d "$HOME/bin" ]; then
    INSTALL_DIR="$HOME/bin"
else
    INSTALL_DIR="$HOME/.local/bin"
    echo -e "${YELLOW}Creating directory: $INSTALL_DIR${NC}"
    mkdir -p "$INSTALL_DIR"
fi

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}Warning: $INSTALL_DIR is not in PATH.${NC}"
    echo "Add this line to your shell profile:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

SCRIPT_PATH="$PROJECT_DIR/record.sh"
INSTALL_PATH="$INSTALL_DIR/record"

if [ -L "$INSTALL_PATH" ] || [ -f "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}Removing existing installation: $INSTALL_PATH${NC}"
    rm -f "$INSTALL_PATH"
fi

chmod +x "$SCRIPT_PATH"
echo -e "${GREEN}Creating symlink:${NC} $INSTALL_PATH -> $SCRIPT_PATH"
ln -s "$SCRIPT_PATH" "$INSTALL_PATH"

# Export RECORDER_HOME for current shell and persist
# Add to multiple shell config files for better compatibility
SHELL_CONFIGS=()

# Determine shell-specific config files
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIGS+=("$HOME/.bashrc")
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIGS+=("$HOME/.zshrc")
else
    case "$SHELL" in
        */bash) SHELL_CONFIGS+=("$HOME/.bashrc") ;;
        */zsh) SHELL_CONFIGS+=("$HOME/.zshrc") ;;
    esac
fi

# Also add to .profile for login shells
if [ -f "$HOME/.profile" ]; then
    SHELL_CONFIGS+=("$HOME/.profile")
fi

echo ""
echo -e "${BLUE}Setting RECORDER_HOME environment variable...${NC}"

for SHELL_RC in "${SHELL_CONFIGS[@]}"; do
    if [ -f "$SHELL_RC" ]; then
        if grep -q "RECORDER_HOME" "$SHELL_RC" 2>/dev/null; then
            echo -e "${YELLOW}RECORDER_HOME already configured in $SHELL_RC${NC}"
        else
            {
                echo ""
                echo "# Meeting Transcriber recorder configuration"
                echo "export RECORDER_HOME=\"$PROJECT_DIR\""
            } >> "$SHELL_RC"
            echo -e "${GREEN}✓ Added RECORDER_HOME to $SHELL_RC${NC}"
        fi
    fi
done

export RECORDER_HOME="$PROJECT_DIR"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo "Command installed as: ${BLUE}record${NC}"
echo "Project location:      ${BLUE}$PROJECT_DIR${NC}"
echo ""
echo "Usage examples:"
echo "  record --name daily-sync"
echo "  record --duration 900"
echo ""
echo -e "${YELLOW}Important: Reload your shell configuration:${NC}"
echo "  source ~/.bashrc"
echo ""
echo "Or simply open a new terminal window."
echo ""
