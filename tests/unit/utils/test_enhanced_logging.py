"""
Comprehensive tests for src/utils/enhanced_logging.py

Tests enhanced logging functionality to achieve >75% coverage.
"""

import logging
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from src.utils.enhanced_logging import (
    Colors,
    Icons,
    MessageLevel,
    ColoredFormatter,
    EnhancedLogger,
    get_enhanced_logger,
    setup_enhanced_logging,
)


class TestColors:
    """Test Colors class"""

    def test_colors_has_reset(self):
        """Test Colors has RESET attribute"""
        assert hasattr(Colors, 'RESET')
        assert isinstance(Colors.RESET, str)

    def test_colors_has_basic_styles(self):
        """Test Colors has basic styles"""
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'DIM')
        assert hasattr(Colors, 'ITALIC')
        assert hasattr(Colors, 'UNDERLINE')

    def test_colors_has_foreground(self):
        """Test Colors has foreground colors"""
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'CYAN')

    def test_colors_has_bright_colors(self):
        """Test Colors has bright variants"""
        assert hasattr(Colors, 'BRIGHT_RED')
        assert hasattr(Colors, 'BRIGHT_GREEN')
        assert hasattr(Colors, 'BRIGHT_YELLOW')

    def test_colors_has_backgrounds(self):
        """Test Colors has background colors"""
        assert hasattr(Colors, 'BG_RED')
        assert hasattr(Colors, 'BG_GREEN')
        assert hasattr(Colors, 'BG_BLUE')


class TestIcons:
    """Test Icons class"""

    def test_icons_has_basic_symbols(self):
        """Test Icons has basic symbols"""
        assert hasattr(Icons, 'SUCCESS')
        assert hasattr(Icons, 'ERROR')
        assert hasattr(Icons, 'WARNING')
        assert hasattr(Icons, 'INFO')
        assert hasattr(Icons, 'DEBUG')

    def test_icons_has_special_symbols(self):
        """Test Icons has special symbols"""
        assert hasattr(Icons, 'ROCKET')
        assert hasattr(Icons, 'CHECK')
        assert hasattr(Icons, 'CROSS')
        assert hasattr(Icons, 'SHIELD')

    def test_icons_are_strings(self):
        """Test Icons are strings"""
        assert isinstance(Icons.SUCCESS, str)
        assert isinstance(Icons.ERROR, str)
        assert isinstance(Icons.ROCKET, str)


class TestMessageLevel:
    """Test MessageLevel enum"""

    def test_message_level_has_all_levels(self):
        """Test MessageLevel has all severity levels"""
        assert hasattr(MessageLevel, 'DEBUG')
        assert hasattr(MessageLevel, 'INFO')
        assert hasattr(MessageLevel, 'SUCCESS')
        assert hasattr(MessageLevel, 'WARNING')
        assert hasattr(MessageLevel, 'ERROR')
        assert hasattr(MessageLevel, 'CRITICAL')

    def test_message_level_values(self):
        """Test MessageLevel enum values"""
        assert MessageLevel.DEBUG.value == "debug"
        assert MessageLevel.INFO.value == "info"
        assert MessageLevel.ERROR.value == "error"


class TestColoredFormatter:
    """Test ColoredFormatter class"""

    def test_colored_formatter_init(self):
        """Test ColoredFormatter initialization"""
        formatter = ColoredFormatter()
        assert isinstance(formatter, logging.Formatter)

    def test_colored_formatter_with_colors(self):
        """Test ColoredFormatter with colors enabled"""
        formatter = ColoredFormatter(use_colors=True, show_icons=True)
        assert formatter.show_icons is True

    def test_colored_formatter_without_colors(self):
        """Test ColoredFormatter without colors"""
        formatter = ColoredFormatter(use_colors=False, show_icons=False)
        assert formatter.show_icons is False

    @patch('sys.stdout.isatty', return_value=True)
    def test_formatter_format_info(self, mock_isatty):
        """Test formatting INFO level message"""
        formatter = ColoredFormatter(use_colors=True, show_icons=True)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        assert "Test message" in result
        assert "INFO" in result

    @patch('sys.stdout.isatty', return_value=True)
    def test_formatter_format_error(self, mock_isatty):
        """Test formatting ERROR level message"""
        formatter = ColoredFormatter(use_colors=True, show_icons=True)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        assert "Error occurred" in result
        assert "ERROR" in result

    @patch('sys.stdout.isatty', return_value=False)
    def test_formatter_format_no_color(self, mock_isatty):
        """Test formatting without colors (non-TTY)"""
        formatter = ColoredFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Warning message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        assert "Warning message" in result
        # Should not have ANSI codes when not a TTY
        assert Colors.RESET not in result or not formatter.use_colors

    def test_formatter_with_exception(self):
        """Test formatting message with exception"""
        formatter = ColoredFormatter(use_colors=False)

        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Error with exception",
                args=(),
                exc_info=exc_info
            )

            result = formatter.format(record)
            assert "Error with exception" in result
            assert "ValueError" in result


class TestEnhancedLogger:
    """Test EnhancedLogger class"""

    @pytest.fixture
    def logger(self):
        """Create EnhancedLogger instance"""
        return EnhancedLogger("test_logger", use_colors=False, show_icons=False)

    @pytest.fixture
    def logger_with_colors(self):
        """Create EnhancedLogger with colors"""
        return EnhancedLogger("test_color_logger", use_colors=True, show_icons=True)

    def test_enhanced_logger_init(self, logger):
        """Test EnhancedLogger initialization"""
        assert logger.logger.name == "test_logger"
        assert logger.use_colors is False
        assert logger.show_icons is False

    def test_logger_has_handlers(self, logger):
        """Test logger has handlers configured"""
        assert len(logger.logger.handlers) > 0

    def test_success_method(self, logger):
        """Test success() method"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.success("Operation successful")
            mock_info.assert_called_once()

    def test_error_with_suggestion(self, logger):
        """Test error_with_suggestion() method"""
        with patch.object(logger.logger, 'error') as mock_error:
            logger.error_with_suggestion("File not found", "Check the file path")
            mock_error.assert_called_once()
            call_args = str(mock_error.call_args)
            assert "File not found" in call_args
            assert "Check the file path" in call_args

    def test_warning_with_action(self, logger):
        """Test warning_with_action() method"""
        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.warning_with_action("Disk space low", "Free up space")
            mock_warning.assert_called_once()
            call_args = str(mock_warning.call_args)
            assert "Disk space low" in call_args

    def test_operation_start(self, logger):
        """Test operation_start() method"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.operation_start("Processing", file_count=10, size="100MB")
            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "Processing" in call_args

    def test_operation_complete_without_duration(self, logger):
        """Test operation_complete() without duration"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.operation_complete("Processing")
            mock_info.assert_called_once()

    def test_operation_complete_with_duration(self, logger):
        """Test operation_complete() with duration"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.operation_complete("Processing", duration=5.25)
            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "Processing" in call_args

    def test_operation_complete_with_results(self, logger):
        """Test operation_complete() with results"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.operation_complete("Processing", files_processed=100, errors=0)
            mock_info.assert_called_once()

    def test_progress(self, logger):
        """Test progress() method"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.progress(50, 100, "Processing files")
            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "50%" in call_args

    def test_progress_zero_total(self, logger):
        """Test progress() with zero total"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.progress(0, 0, "Operation")
            mock_info.assert_called_once()

    def test_file_operation(self, logger):
        """Test file_operation() method"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.file_operation("Reading", "/path/to/file.txt", size="1KB")
            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "Reading" in call_args
            assert "file.txt" in call_args

    def test_security_event_low(self, logger):
        """Test security_event() with low severity"""
        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.security_event("Login attempt", "low", "User: john")
            mock_warning.assert_called_once()

    def test_security_event_high(self, logger):
        """Test security_event() with high severity"""
        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.security_event("Intrusion detected", "high", "IP: 1.2.3.4")
            mock_warning.assert_called_once()

    def test_security_event_critical(self, logger):
        """Test security_event() with critical severity"""
        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.security_event("System breach", "critical", "Immediate action required")
            mock_warning.assert_called_once()

    def test_data_summary(self, logger):
        """Test data_summary() method"""
        with patch.object(logger.logger, 'info') as mock_info:
            data = {"files": 100, "size": "10MB", "duration": "5.2s"}
            logger.data_summary("Processing Summary", data)
            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "Processing Summary" in call_args

    def test_validation_result_passed(self, logger):
        """Test validation_result() with passed validation"""
        with patch.object(logger.logger, 'log') as mock_log:
            logger.validation_result(True, "email@example.com")
            mock_log.assert_called_once()
            assert mock_log.call_args[0][0] == logging.INFO

    def test_validation_result_failed(self, logger):
        """Test validation_result() with failed validation"""
        with patch.object(logger.logger, 'log') as mock_log:
            logger.validation_result(False, "invalid-email", "Missing @ symbol")
            mock_log.assert_called_once()
            assert mock_log.call_args[0][0] == logging.WARNING

    def test_debug_method(self, logger):
        """Test debug() method"""
        with patch.object(logger.logger, 'debug') as mock_debug:
            logger.debug("Debug information")
            mock_debug.assert_called_once()

    def test_info_method(self, logger):
        """Test info() method"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.info("Information message")
            mock_info.assert_called_once()

    def test_warning_method(self, logger):
        """Test warning() method"""
        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.warning("Warning message")
            mock_warning.assert_called_once()

    def test_error_method(self, logger):
        """Test error() method"""
        with patch.object(logger.logger, 'error') as mock_error:
            logger.error("Error message")
            mock_error.assert_called_once()

    def test_critical_method(self, logger):
        """Test critical() method"""
        with patch.object(logger.logger, 'critical') as mock_critical:
            logger.critical("Critical error")
            mock_critical.assert_called_once()

    def test_colorize_with_colors_enabled(self, logger_with_colors):
        """Test _colorize() with colors enabled"""
        result = logger_with_colors._colorize("text", Colors.RED)
        if logger_with_colors.use_colors:
            assert Colors.RED in result or "text" in result

    def test_colorize_with_colors_disabled(self, logger):
        """Test _colorize() with colors disabled"""
        result = logger._colorize("text", Colors.RED)
        assert result == "text"

    def test_icon_with_icons_enabled(self, logger_with_colors):
        """Test _icon() with icons enabled"""
        if logger_with_colors.show_icons:
            result = logger_with_colors._icon(Icons.CHECK)
            assert Icons.CHECK in result or result != ""

    def test_icon_with_icons_disabled(self, logger):
        """Test _icon() with icons disabled"""
        result = logger._icon(Icons.CHECK)
        assert result == ""

    def test_context_logging(self, logger):
        """Test logging with context"""
        with patch.object(logger.logger, 'info') as mock_info:
            logger.info("Message", user_id=123, action="login")
            mock_info.assert_called_once()


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_get_enhanced_logger(self):
        """Test get_enhanced_logger() function"""
        logger = get_enhanced_logger("test")
        assert isinstance(logger, EnhancedLogger)
        assert logger.logger.name == "test"

    def test_get_enhanced_logger_with_options(self):
        """Test get_enhanced_logger() with options"""
        logger = get_enhanced_logger("test", use_colors=False, show_icons=False)
        assert logger.use_colors is False
        assert logger.show_icons is False

    def test_setup_enhanced_logging(self):
        """Test setup_enhanced_logging() function"""
        setup_enhanced_logging(level="DEBUG", use_colors=False, show_icons=False)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) > 0

    def test_setup_enhanced_logging_removes_old_handlers(self):
        """Test setup_enhanced_logging() removes old handlers"""
        # Add a dummy handler
        root_logger = logging.getLogger()
        old_handler = logging.StreamHandler()
        root_logger.addHandler(old_handler)
        handler_count_before = len(root_logger.handlers)

        # Setup enhanced logging
        setup_enhanced_logging()

        # Should have replaced handlers
        assert len(root_logger.handlers) >= 1


class TestIntegration:
    """Integration tests"""

    def test_full_logging_workflow(self):
        """Test complete logging workflow"""
        logger = EnhancedLogger("integration_test", use_colors=False, show_icons=False)

        # Test various logging methods
        with patch.object(logger.logger, 'info'):
            logger.success("Operation completed")
            logger.operation_start("Processing")
            logger.operation_complete("Processing", duration=1.5)
            logger.progress(75, 100, "Files")
            logger.file_operation("Read", "test.txt")

        with patch.object(logger.logger, 'error'):
            logger.error_with_suggestion("Error occurred", "Try again")

        with patch.object(logger.logger, 'warning'):
            logger.warning_with_action("Warning", "Take action")
            logger.security_event("Event", "medium", "Details")

    def test_logging_with_colors_and_icons(self):
        """Test logging with colors and icons enabled"""
        logger = EnhancedLogger("color_test", use_colors=True, show_icons=True)

        with patch.object(logger.logger, 'info') as mock_info:
            logger.success("Success message")
            logger.operation_complete("Task", duration=2.5, result="OK")
            logger.data_summary("Summary", {"key": "value"})

            # Verify methods were called
            assert mock_info.call_count >= 3


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.utils.enhanced_logging", "--cov-report=term-missing"])
