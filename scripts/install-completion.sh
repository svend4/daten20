#!/usr/bin/env bash
# Installation script for doc-tools shell completion
#
# Usage:
#   ./scripts/install-completion.sh [bash|zsh|both]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPLETIONS_DIR="$PROJECT_ROOT/completions"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# Detect shell
detect_shell() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    else
        # Try to detect from $SHELL variable
        case "$SHELL" in
            */zsh)
                echo "zsh"
                ;;
            */bash)
                echo "bash"
                ;;
            *)
                echo "unknown"
                ;;
        esac
    fi
}

# Install Bash completion
install_bash_completion() {
    print_header "Installing Bash Completion"

    local completion_file="$COMPLETIONS_DIR/doc-tools-completion.bash"

    if [ ! -f "$completion_file" ]; then
        print_error "Completion file not found: $completion_file"
        return 1
    fi

    # Try system-wide installation first (requires sudo)
    if [ -w /etc/bash_completion.d ] || command -v sudo >/dev/null 2>&1; then
        print_info "Installing system-wide completion (may require sudo)..."

        if [ -w /etc/bash_completion.d ]; then
            cp "$completion_file" /etc/bash_completion.d/doc-tools
            print_success "System-wide completion installed to /etc/bash_completion.d/"
        elif sudo -n true 2>/dev/null; then
            sudo cp "$completion_file" /etc/bash_completion.d/doc-tools
            print_success "System-wide completion installed to /etc/bash_completion.d/"
        else
            print_warning "Sudo required for system-wide installation"
            print_info "Falling back to user-level installation..."
            install_bash_completion_user
        fi
    else
        print_info "Installing user-level completion..."
        install_bash_completion_user
    fi

    print_info "Completion will be available in new shell sessions"
    print_info "To enable in current session, run:"
    echo -e "  ${GREEN}source $completion_file${NC}"
}

install_bash_completion_user() {
    local completion_file="$COMPLETIONS_DIR/doc-tools-completion.bash"
    local user_completion_dir="$HOME/.bash_completion.d"

    # Create user completion directory
    mkdir -p "$user_completion_dir"

    # Copy completion file
    cp "$completion_file" "$user_completion_dir/doc-tools"
    print_success "User-level completion installed to ~/.bash_completion.d/"

    # Update .bashrc if needed
    local bashrc="$HOME/.bashrc"
    local source_line="source ~/.bash_completion.d/doc-tools"

    if [ -f "$bashrc" ]; then
        if ! grep -q "bash_completion.d/doc-tools" "$bashrc"; then
            echo "" >> "$bashrc"
            echo "# Doc-tools completion" >> "$bashrc"
            echo "$source_line" >> "$bashrc"
            print_success "Added completion source to ~/.bashrc"
        else
            print_info "Completion already configured in ~/.bashrc"
        fi
    else
        print_warning "~/.bashrc not found. Add this line manually:"
        echo -e "  ${GREEN}$source_line${NC}"
    fi
}

# Install Zsh completion
install_zsh_completion() {
    print_header "Installing Zsh Completion"

    local completion_file="$COMPLETIONS_DIR/doc-tools-completion.zsh"

    if [ ! -f "$completion_file" ]; then
        print_error "Completion file not found: $completion_file"
        return 1
    fi

    # Try system-wide installation first
    if [ -w /usr/share/zsh/site-functions ] || command -v sudo >/dev/null 2>&1; then
        print_info "Installing system-wide completion (may require sudo)..."

        if [ -w /usr/share/zsh/site-functions ]; then
            cp "$completion_file" /usr/share/zsh/site-functions/_doc-tools
            print_success "System-wide completion installed to /usr/share/zsh/site-functions/"
        elif sudo -n true 2>/dev/null; then
            sudo cp "$completion_file" /usr/share/zsh/site-functions/_doc-tools
            print_success "System-wide completion installed to /usr/share/zsh/site-functions/"
        else
            print_warning "Sudo required for system-wide installation"
            print_info "Falling back to user-level installation..."
            install_zsh_completion_user
        fi
    else
        print_info "Installing user-level completion..."
        install_zsh_completion_user
    fi

    print_info "Completion will be available in new shell sessions"
    print_info "To enable in current session, run:"
    echo -e "  ${GREEN}autoload -U compinit && compinit${NC}"
}

install_zsh_completion_user() {
    local completion_file="$COMPLETIONS_DIR/doc-tools-completion.zsh"
    local user_completion_dir="$HOME/.zsh/completion"

    # Create user completion directory
    mkdir -p "$user_completion_dir"

    # Copy completion file
    cp "$completion_file" "$user_completion_dir/_doc-tools"
    print_success "User-level completion installed to ~/.zsh/completion/"

    # Update .zshrc if needed
    local zshrc="$HOME/.zshrc"
    local fpath_line='fpath=(~/.zsh/completion $fpath)'
    local compinit_line='autoload -U compinit && compinit'

    if [ -f "$zshrc" ]; then
        local updated=0

        if ! grep -q "\.zsh/completion" "$zshrc"; then
            echo "" >> "$zshrc"
            echo "# Doc-tools completion" >> "$zshrc"
            echo "$fpath_line" >> "$zshrc"
            updated=1
        fi

        if ! grep -q "compinit" "$zshrc"; then
            echo "$compinit_line" >> "$zshrc"
            updated=1
        fi

        if [ $updated -eq 1 ]; then
            print_success "Added completion configuration to ~/.zshrc"
        else
            print_info "Completion already configured in ~/.zshrc"
        fi
    else
        print_warning "~/.zshrc not found. Add these lines manually:"
        echo -e "  ${GREEN}$fpath_line${NC}"
        echo -e "  ${GREEN}$compinit_line${NC}"
    fi
}

# Test completion
test_completion() {
    print_header "Testing Completion"

    local shell_type=$(detect_shell)

    print_info "Current shell: $shell_type"
    print_info "Available doc-* tools:"

    ls -1 "$PROJECT_ROOT"/*.py 2>/dev/null | grep "doc-" | while read tool; do
        echo "  ✓ $(basename "$tool")"
    done

    echo ""
    print_info "To test completion:"
    echo -e "  ${GREEN}1. Open a new terminal or source your shell config${NC}"
    echo -e "  ${GREEN}2. Type: doc-<TAB>${NC}"
    echo -e "  ${GREEN}3. Try: doc-processor.py <TAB>${NC}"
    echo -e "  ${GREEN}4. Run: doc-completion-help${NC}"
}

# Uninstall completion
uninstall_completion() {
    print_header "Uninstalling Completion"

    # Remove system-wide files
    if [ -f /etc/bash_completion.d/doc-tools ]; then
        if [ -w /etc/bash_completion.d ]; then
            rm /etc/bash_completion.d/doc-tools
            print_success "Removed /etc/bash_completion.d/doc-tools"
        elif command -v sudo >/dev/null 2>&1; then
            sudo rm /etc/bash_completion.d/doc-tools
            print_success "Removed /etc/bash_completion.d/doc-tools"
        fi
    fi

    if [ -f /usr/share/zsh/site-functions/_doc-tools ]; then
        if [ -w /usr/share/zsh/site-functions ]; then
            rm /usr/share/zsh/site-functions/_doc-tools
            print_success "Removed /usr/share/zsh/site-functions/_doc-tools"
        elif command -v sudo >/dev/null 2>&1; then
            sudo rm /usr/share/zsh/site-functions/_doc-tools
            print_success "Removed /usr/share/zsh/site-functions/_doc-tools"
        fi
    fi

    # Remove user-level files
    if [ -f "$HOME/.bash_completion.d/doc-tools" ]; then
        rm "$HOME/.bash_completion.d/doc-tools"
        print_success "Removed ~/.bash_completion.d/doc-tools"
    fi

    if [ -f "$HOME/.zsh/completion/_doc-tools" ]; then
        rm "$HOME/.zsh/completion/_doc-tools"
        print_success "Removed ~/.zsh/completion/_doc-tools"
    fi

    print_warning "Configuration in ~/.bashrc or ~/.zshrc not removed automatically"
    print_info "Remove these lines manually if desired"
}

# Show usage
show_usage() {
    cat <<EOF
Doc-tools Completion Installer

Usage:
  $0 [COMMAND]

Commands:
  bash              Install Bash completion only
  zsh               Install Zsh completion only
  both              Install both Bash and Zsh completion (default)
  test              Test completion installation
  uninstall         Remove all completion files
  help              Show this help message

Examples:
  $0                # Install for both shells
  $0 bash           # Install Bash completion only
  $0 test           # Test if completion works

EOF
}

# Main
main() {
    local command="${1:-both}"

    print_header "Doc-tools Shell Completion Installer"

    case "$command" in
        bash)
            install_bash_completion
            ;;
        zsh)
            install_zsh_completion
            ;;
        both)
            install_bash_completion
            install_zsh_completion
            ;;
        test)
            test_completion
            ;;
        uninstall)
            uninstall_completion
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac

    echo ""
    print_success "Installation complete!"
    echo ""
    print_info "Next steps:"
    echo -e "  ${GREEN}1. Open a new terminal (or source your shell config)${NC}"
    echo -e "  ${GREEN}2. Try: doc-<TAB>${NC}"
    echo -e "  ${GREEN}3. Run: doc-completion-help${NC}"
    echo ""
}

main "$@"
