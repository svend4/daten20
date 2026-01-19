#!/bin/bash
# Install bash completions for daten20 CLI tools
# Usage: bash scripts/install_completions.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}daten20 CLI Completions Installer${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Detect shell
SHELL_NAME=$(basename "$SHELL")
echo -e "${BLUE}Detected shell:${NC} $SHELL_NAME"
echo ""

# Installation directory
COMPLETION_DIR="$HOME/.bash_completion.d"
COMPLETION_FILE="daten20_completion.sh"

# Create directory if it doesn't exist
if [ ! -d "$COMPLETION_DIR" ]; then
    echo -e "${YELLOW}Creating completion directory:${NC} $COMPLETION_DIR"
    mkdir -p "$COMPLETION_DIR"
fi

# Copy completion script
SOURCE_FILE="$(pwd)/scripts/completions/bash_completion.sh"
TARGET_FILE="$COMPLETION_DIR/$COMPLETION_FILE"

if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}Error: Source file not found:${NC} $SOURCE_FILE"
    echo -e "${YELLOW}Make sure you're running this script from the daten20 project root.${NC}"
    exit 1
fi

echo -e "${BLUE}Copying completion script...${NC}"
cp "$SOURCE_FILE" "$TARGET_FILE"
chmod +x "$TARGET_FILE"
echo -e "${GREEN}✓${NC} Completion script copied to: $TARGET_FILE"
echo ""

# Determine which RC file to update
RC_FILE="$HOME/.bashrc"
if [ "$SHELL_NAME" = "zsh" ]; then
    RC_FILE="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    # On macOS, .bash_profile is used instead of .bashrc
    if [[ "$OSTYPE" == "darwin"* ]]; then
        RC_FILE="$HOME/.bash_profile"
    fi
fi

echo -e "${BLUE}Shell configuration file:${NC} $RC_FILE"

# Add source line to RC file if not already present
SOURCE_LINE="source $TARGET_FILE"
if grep -q "$COMPLETION_FILE" "$RC_FILE" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Completion already configured in $RC_FILE"
else
    echo -e "${BLUE}Adding completion to:${NC} $RC_FILE"
    echo "" >> "$RC_FILE"
    echo "# daten20 CLI completions" >> "$RC_FILE"
    echo "$SOURCE_LINE" >> "$RC_FILE"
    echo -e "${GREEN}✓${NC} Completion added to $RC_FILE"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}To activate completions:${NC}"
echo "  1. Restart your terminal, OR"
echo "  2. Run: source $RC_FILE"
echo ""
echo -e "${BLUE}Test completions:${NC}"
echo "  doc-comparator.py <TAB>      # Press TAB to see commands"
echo "  doc-anonymizer.py --<TAB>    # Press TAB to see options"
echo "  doc-quality.py analyze <TAB> # Press TAB to see files"
echo ""
echo -e "${BLUE}Supported tools:${NC}"
echo "  • doc-comparator.py"
echo "  • doc-anonymizer.py"
echo "  • doc-quality.py"
echo "  • doc-master.py"
echo "  • doc-processor.py"
echo "  • doc-search.py"
echo "  • doc-merger.py"
echo "  • doc-splitter.py"
echo "  • dms-admin.py"
echo "  • enterprise-admin.py"
echo ""
echo -e "${GREEN}Enjoy your enhanced CLI experience!${NC}"
