#!/bin/bash
# Install Zsh completions for daten20 CLI tools
# Usage: bash scripts/install_completions_zsh.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}daten20 Zsh Completions Installer${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Zsh is installed
if ! command -v zsh &> /dev/null; then
    echo -e "${YELLOW}⚠  Zsh is not installed${NC}"
    echo -e "  This script installs Zsh completions. You can still install them,"
    echo -e "  but they won't work until Zsh is installed."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Installation directory for Zsh completions
COMPLETION_DIR="$HOME/.zsh/completions"
COMPLETION_FILE="_daten20"

# Create directory if it doesn't exist
if [ ! -d "$COMPLETION_DIR" ]; then
    echo -e "${YELLOW}Creating completion directory:${NC} $COMPLETION_DIR"
    mkdir -p "$COMPLETION_DIR"
fi

# Copy completion script
SOURCE_FILE="$(pwd)/scripts/completions/zsh_completion.zsh"
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

# Zsh configuration file
ZSHRC="$HOME/.zshrc"

if [ ! -f "$ZSHRC" ]; then
    echo -e "${YELLOW}⚠  .zshrc not found, creating new file${NC}"
    touch "$ZSHRC"
fi

echo -e "${BLUE}Zsh configuration file:${NC} $ZSHRC"

# Check if fpath already includes the completion directory
if grep -q "$COMPLETION_DIR" "$ZSHRC" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Completion directory already in fpath"
else
    echo -e "${BLUE}Adding completion directory to fpath...${NC}"
    echo "" >> "$ZSHRC"
    echo "# daten20 CLI completions" >> "$ZSHRC"
    echo "fpath=($COMPLETION_DIR \$fpath)" >> "$ZSHRC"
    echo -e "${GREEN}✓${NC} Completion directory added to fpath"
fi

# Check if compinit is configured
if ! grep -q "autoload.*compinit" "$ZSHRC" 2>/dev/null; then
    echo -e "${BLUE}Configuring completion system...${NC}"
    echo "autoload -Uz compinit && compinit" >> "$ZSHRC"
    echo -e "${GREEN}✓${NC} Completion system configured"
else
    echo -e "${GREEN}✓${NC} Completion system already configured"
fi

# Check for bash completion compatibility (optional but helpful)
if ! grep -q "bashcompinit" "$ZSHRC" 2>/dev/null; then
    echo -e "${BLUE}Adding bash completion compatibility...${NC}"
    echo "autoload -Uz bashcompinit && bashcompinit" >> "$ZSHRC"
    echo -e "${GREEN}✓${NC} Bash completion compatibility added"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}To activate completions:${NC}"
echo "  1. Restart your terminal, OR"
echo "  2. Run: source $ZSHRC"
echo "  3. Rebuild completion cache: rm -f ~/.zcompdump && exec zsh"
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
echo -e "${YELLOW}Note:${NC} Zsh completion is more powerful than Bash:"
echo "  • Shows descriptions for commands"
echo "  • Better context-aware completion"
echo "  • Enhanced file type filtering"
echo ""
echo -e "${GREEN}Enjoy your enhanced Zsh CLI experience!${NC}"
