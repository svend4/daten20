"""
Unit tests for CLI Auto-Completion
===================================

Tests the CLI completion functionality.
"""

import os
import sys
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.utils.cli_completion import CLICompletion


class TestCLICompletion:
    """Test suite for CLICompletion"""

    @pytest.fixture
    def completion(self):
        """Create CLICompletion instance."""
        return CLICompletion()

    def test_initialization(self, completion):
        """Test CLICompletion initialization."""
        assert completion is not None
        assert completion.project_root is not None
        assert completion.TOOLS is not None
        assert len(completion.TOOLS) > 0

    def test_tools_configuration(self, completion):
        """Test that all tools are properly configured."""
        expected_tools = [
            "doc-processor",
            "doc-comparator",
            "doc-anonymizer",
            "doc-quality",
            "doc-master",
            "doc-search",
            "doc-dashboard",
            "doc-api-server",
            "doc-batch-processor",
            "doc-merger",
            "doc-splitter",
        ]

        for tool in expected_tools:
            assert tool in completion.TOOLS
            assert "commands" in completion.TOOLS[tool]
            assert "options" in completion.TOOLS[tool]
            assert len(completion.TOOLS[tool]["commands"]) > 0
            assert len(completion.TOOLS[tool]["options"]) > 0

    def test_generate_bash_completion(self, completion):
        """Test Bash completion script generation."""
        script = completion.generate_bash_completion()

        assert isinstance(script, str)
        assert len(script) > 0
        assert "Bash completion" in script
        assert "_dms_completion" in script
        assert "COMPREPLY" in script
        assert "complete -F" in script

        # Check that all tools are included
        for tool in completion.TOOLS:
            assert tool in script

    def test_bash_completion_structure(self, completion):
        """Test Bash completion script has correct structure."""
        script = completion.generate_bash_completion()

        # Should have function definition
        assert "_dms_completion()" in script
        # Should have case statement
        assert "case" in script
        # Should register completion for each tool
        for tool in completion.TOOLS:
            assert f"complete -F _dms_completion {tool}" in script

    def test_generate_zsh_completion(self, completion):
        """Test Zsh completion script generation."""
        script = completion.generate_zsh_completion()

        assert isinstance(script, str)
        assert len(script) > 0
        assert "Zsh completion" in script
        assert "#compdef" in script
        assert "_dms_completion" in script
        assert "_arguments" in script

        # Check that all tools are included
        for tool in completion.TOOLS:
            assert tool in script

    def test_zsh_completion_structure(self, completion):
        """Test Zsh completion script has correct structure."""
        script = completion.generate_zsh_completion()

        # Should have compdef directive
        assert "#compdef" in script
        # Should have function definition
        assert "_dms_completion()" in script
        # Should have case statement
        assert "case" in script
        # Should use _arguments
        assert "_arguments" in script

    def test_generate_fish_completion(self, completion):
        """Test Fish completion script generation."""
        script = completion.generate_fish_completion()

        assert isinstance(script, str)
        assert len(script) > 0
        assert "Fish completion" in script
        assert "complete -c" in script

        # Check that all tools are included
        for tool in completion.TOOLS:
            assert tool in script

    def test_fish_completion_structure(self, completion):
        """Test Fish completion script has correct structure."""
        script = completion.generate_fish_completion()

        # Should have complete commands
        assert "complete -c" in script
        # Should have subcommand completions
        assert "__fish_use_subcommand" in script

        # Check each tool has command and option completions
        for tool, config in completion.TOOLS.items():
            for command in config["commands"]:
                assert command in script

    def test_detect_shell_bash(self, completion):
        """Test shell detection for Bash."""
        with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            shell = completion.detect_shell()
            assert shell == "bash"

    def test_detect_shell_zsh(self, completion):
        """Test shell detection for Zsh."""
        with patch.dict(os.environ, {"SHELL": "/usr/bin/zsh"}):
            shell = completion.detect_shell()
            assert shell == "zsh"

    def test_detect_shell_fish(self, completion):
        """Test shell detection for Fish."""
        with patch.dict(os.environ, {"SHELL": "/usr/local/bin/fish"}):
            shell = completion.detect_shell()
            assert shell == "fish"

    def test_detect_shell_unknown(self, completion):
        """Test shell detection with unknown shell."""
        with patch.dict(os.environ, {"SHELL": "/bin/csh"}):
            shell = completion.detect_shell()
            assert shell is None

    def test_detect_shell_no_env(self, completion):
        """Test shell detection without SHELL env variable."""
        with patch.dict(os.environ, {}, clear=True):
            shell = completion.detect_shell()
            assert shell is None

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @patch("builtins.print")
    def test_install_completion_bash(self, mock_print, mock_mkdir, mock_file, completion):
        """Test installing Bash completion."""
        result = completion.install_completion("bash")

        assert result is True
        mock_mkdir.assert_called_once()
        mock_file.assert_called_once()
        assert mock_print.called

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @patch("builtins.print")
    def test_install_completion_zsh(self, mock_print, mock_mkdir, mock_file, completion):
        """Test installing Zsh completion."""
        result = completion.install_completion("zsh")

        assert result is True
        mock_mkdir.assert_called()
        mock_file.assert_called_once()
        assert mock_print.called

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @patch("builtins.print")
    def test_install_completion_fish(self, mock_print, mock_mkdir, mock_file, completion):
        """Test installing Fish completion."""
        result = completion.install_completion("fish")

        assert result is True
        mock_mkdir.assert_called()
        mock_file.assert_called_once()
        assert mock_print.called

    @patch("builtins.print")
    def test_install_completion_unsupported(self, mock_print, completion):
        """Test installing completion for unsupported shell."""
        result = completion.install_completion("csh")

        assert result is False
        assert mock_print.called

    @patch("builtins.print")
    @patch.dict(os.environ, {}, clear=True)
    def test_install_completion_no_shell(self, mock_print, completion):
        """Test installing completion without shell detection."""
        result = completion.install_completion()

        assert result is False
        assert mock_print.called

    @patch("builtins.print")
    def test_list_tools(self, mock_print, completion):
        """Test listing available tools."""
        completion.list_tools()

        assert mock_print.called
        # Check that output mentions tools
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        for tool in completion.TOOLS:
            assert tool in output

    def test_all_tools_have_commands(self, completion):
        """Test that all tools have at least one command."""
        for tool, config in completion.TOOLS.items():
            assert len(config["commands"]) >= 1, f"{tool} has no commands"

    def test_all_tools_have_options(self, completion):
        """Test that all tools have at least one option."""
        for tool, config in completion.TOOLS.items():
            assert len(config["options"]) >= 1, f"{tool} has no options"

    def test_options_start_with_dashes(self, completion):
        """Test that all options start with '--'."""
        for tool, config in completion.TOOLS.items():
            for option in config["options"]:
                assert option.startswith("--"), f"Invalid option format: {option}"

    def test_commands_are_lowercase(self, completion):
        """Test that all commands are lowercase."""
        for tool, config in completion.TOOLS.items():
            for command in config["commands"]:
                assert command.islower() or "-" in command, f"Command not lowercase: {command}"

    def test_no_duplicate_commands(self, completion):
        """Test that tools don't have duplicate commands."""
        for tool, config in completion.TOOLS.items():
            commands = config["commands"]
            assert len(commands) == len(set(commands)), f"{tool} has duplicate commands"

    def test_no_duplicate_options(self, completion):
        """Test that tools don't have duplicate options."""
        for tool, config in completion.TOOLS.items():
            options = config["options"]
            assert len(options) == len(set(options)), f"{tool} has duplicate options"


class TestCLICompletionIntegration:
    """Integration tests for CLI completion."""

    @pytest.fixture
    def completion(self):
        """Create CLICompletion instance."""
        return CLICompletion()

    def test_generate_all_completions(self, completion):
        """Test generating all completion types."""
        bash_script = completion.generate_bash_completion()
        zsh_script = completion.generate_zsh_completion()
        fish_script = completion.generate_fish_completion()

        assert len(bash_script) > 0
        assert len(zsh_script) > 0
        assert len(fish_script) > 0

        # All should be different
        assert bash_script != zsh_script
        assert bash_script != fish_script
        assert zsh_script != fish_script

    def test_completion_consistency(self, completion):
        """Test that all completions include all tools."""
        bash_script = completion.generate_bash_completion()
        zsh_script = completion.generate_zsh_completion()
        fish_script = completion.generate_fish_completion()

        for tool in completion.TOOLS:
            assert tool in bash_script, f"{tool} missing from Bash completion"
            assert tool in zsh_script, f"{tool} missing from Zsh completion"
            assert tool in fish_script, f"{tool} missing from Fish completion"

    def test_shell_detection_workflow(self, completion):
        """Test complete shell detection workflow."""
        shells = ["bash", "zsh", "fish"]

        for shell in shells:
            with patch.dict(os.environ, {"SHELL": f"/bin/{shell}"}):
                detected = completion.detect_shell()
                assert detected == shell


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
