#!/usr/bin/env python3
"""
CLI Auto-Completion Support
============================

Provides auto-completion support for all CLI tools in the Document Management System.

Features:
- Bash completion scripts
- Zsh completion scripts
- Fish completion scripts
- Command discovery
- Argument suggestions
- File path completion
- Dynamic option completion

Usage:
    # Generate completion script for bash
    python -m src.utils.cli_completion bash > ~/.bash_completion.d/dms

    # Generate completion script for zsh
    python -m src.utils.cli_completion zsh > ~/.zsh/completion/_dms

    # Generate completion script for fish
    python -m src.utils.cli_completion fish > ~/.config/fish/completions/dms.fish

    # Install completion for current shell
    python -m src.utils.cli_completion install

Author: Document Management System
Version: 1.0.0
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class CLICompletion:
    """Manages CLI auto-completion for all DMS tools."""

    # All CLI tools in the system
    TOOLS = {
        "doc-processor": {
            "commands": ["process", "batch", "validate"],
            "options": ["--output", "--format", "--quality", "--verbose"],
        },
        "doc-comparator": {
            "commands": ["compare", "versions", "entities", "semantic"],
            "options": ["--report", "--output", "--threshold", "--verbose"],
        },
        "doc-anonymizer": {
            "commands": ["anonymize", "scan", "deanonymize", "batch"],
            "options": ["--strategy", "--compliance", "--reversible", "--output"],
        },
        "doc-quality": {
            "commands": ["analyze", "batch", "report"],
            "options": ["--dimensions", "--threshold", "--output", "--format"],
        },
        "doc-master": {
            "commands": ["status", "health", "quick-process", "pipeline"],
            "options": ["--verbose", "--json", "--steps", "--output"],
        },
        "doc-search": {
            "commands": ["search", "index", "query"],
            "options": ["--query", "--limit", "--format", "--output"],
        },
        "doc-dashboard": {"commands": ["start", "stop", "status"], "options": ["--port", "--host", "--debug"]},
        "doc-api-server": {
            "commands": ["start", "stop", "status"],
            "options": ["--port", "--host", "--workers", "--debug"],
        },
        "doc-batch-processor": {
            "commands": ["process", "status", "cancel"],
            "options": ["--input", "--output", "--workers", "--format"],
        },
        "doc-merger": {"commands": ["merge", "batch"], "options": ["--output", "--format", "--order", "--verbose"]},
        "doc-splitter": {"commands": ["split", "batch"], "options": ["--output", "--method", "--size", "--verbose"]},
    }

    def __init__(self):
        """Initialize CLI completion."""
        self.project_root = Path(__file__).parent.parent.parent

    def generate_bash_completion(self) -> str:
        """Generate bash completion script."""
        script = """# Bash completion for Document Management System
# Source this file in your ~/.bashrc or save to /etc/bash_completion.d/

_dms_completion() {
    local cur prev words cword
    _init_completion || return

    local tools="doc-processor doc-comparator doc-anonymizer doc-quality doc-master doc-search doc-dashboard doc-api-server doc-batch-processor doc-merger doc-splitter"

    # Complete tool names
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$tools" -- "$cur") )
        return
    fi

    local tool="${words[1]}"

    case "$tool" in
"""

        for tool, config in self.TOOLS.items():
            commands = " ".join(config["commands"])
            options = " ".join(config["options"])

            script += f"""        {tool})
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "{commands}" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "{options}" -- "$cur") )
            fi
            ;;
"""

        script += """    esac
}

# Register completion for all tools
"""
        for tool in self.TOOLS.keys():
            script += f"complete -F _dms_completion {tool}\n"

        return script

    def generate_zsh_completion(self) -> str:
        """Generate zsh completion script."""
        script = """#compdef doc-processor doc-comparator doc-anonymizer doc-quality doc-master doc-search doc-dashboard doc-api-server doc-batch-processor doc-merger doc-splitter

# Zsh completion for Document Management System

_dms_completion() {
    local context state state_descr line
    typeset -A opt_args

    local tool="$words[1]"

    case "$tool" in
"""

        for tool, config in self.TOOLS.items():
            commands = " ".join(config["commands"])

            script += f"""        {tool})
            _arguments \\
"""
            for option in config["options"]:
                script += f"                '{option}[{option.strip('--')}]' \\\n"

            script += f"""                '1: :({commands})' \\
                '*::arg:->args'
            ;;
"""

        script += """    esac
}

_dms_completion "$@"
"""
        return script

    def generate_fish_completion(self) -> str:
        """Generate fish completion script."""
        script = "# Fish completion for Document Management System\n\n"

        for tool, config in self.TOOLS.items():
            # Add command completions
            for command in config["commands"]:
                script += f"complete -c {tool} -n '__fish_use_subcommand' -a '{command}' -d '{command} command'\n"

            # Add option completions
            for option in config["options"]:
                opt_name = option.strip("--")
                script += f"complete -c {tool} -l {opt_name} -d '{opt_name} option'\n"

            script += "\n"

        return script

    def detect_shell(self) -> Optional[str]:
        """Detect the current shell."""
        shell = os.environ.get("SHELL", "")

        if "bash" in shell:
            return "bash"
        elif "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        else:
            return None

    def install_completion(self, shell: Optional[str] = None) -> bool:
        """Install completion for the specified or detected shell."""
        if shell is None:
            shell = self.detect_shell()

        if shell is None:
            print("Could not detect shell. Please specify manually.")
            return False

        if shell == "bash":
            completion_dir = Path.home() / ".bash_completion.d"
            completion_dir.mkdir(exist_ok=True)
            completion_file = completion_dir / "dms"

            with open(completion_file, "w") as f:
                f.write(self.generate_bash_completion())

            print(f"Bash completion installed to {completion_file}")
            print(f"Add this line to your ~/.bashrc:")
            print(f"  source {completion_file}")

        elif shell == "zsh":
            completion_dir = Path.home() / ".zsh" / "completion"
            completion_dir.mkdir(parents=True, exist_ok=True)
            completion_file = completion_dir / "_dms"

            with open(completion_file, "w") as f:
                f.write(self.generate_zsh_completion())

            print(f"Zsh completion installed to {completion_file}")
            print(f"Add these lines to your ~/.zshrc:")
            print(f"  fpath=({completion_dir} $fpath)")
            print(f"  autoload -Uz compinit && compinit")

        elif shell == "fish":
            completion_dir = Path.home() / ".config" / "fish" / "completions"
            completion_dir.mkdir(parents=True, exist_ok=True)
            completion_file = completion_dir / "dms.fish"

            with open(completion_file, "w") as f:
                f.write(self.generate_fish_completion())

            print(f"Fish completion installed to {completion_file}")
            print("Completions will be automatically loaded by fish.")

        else:
            print(f"Unsupported shell: {shell}")
            return False

        return True

    def list_tools(self) -> None:
        """List all available tools and their commands."""
        print("Available CLI Tools:\n")

        for tool, config in self.TOOLS.items():
            print(f"  {tool}")
            print(f"    Commands: {', '.join(config['commands'])}")
            print(f"    Options: {', '.join(config['options'])}")
            print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CLI Auto-Completion for Document Management System")

    parser.add_argument(
        "action",
        nargs="?",
        choices=["bash", "zsh", "fish", "install", "list"],
        default="list",
        help="Action to perform (default: list)",
    )

    parser.add_argument(
        "--shell",
        choices=["bash", "zsh", "fish"],
        help="Shell to install completion for (auto-detected if not specified)",
    )

    args = parser.parse_args()

    completion = CLICompletion()

    if args.action == "bash":
        print(completion.generate_bash_completion())
    elif args.action == "zsh":
        print(completion.generate_zsh_completion())
    elif args.action == "fish":
        print(completion.generate_fish_completion())
    elif args.action == "install":
        completion.install_completion(args.shell)
    elif args.action == "list":
        completion.list_tools()


if __name__ == "__main__":
    main()
