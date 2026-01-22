"""
Unit tests for logging configuration module
"""

import json
import logging
import os
import tempfile
from pathlib import Path

import pytest

from src.core.logging_config import (
    JSONFormatter,
    LoggingConfig,
    get_logger,
    setup_logger,
)


# ============================================================================
# JSONFormatter Tests
# ============================================================================


class TestJSONFormatter:
    """Test JSONFormatter class"""

    def test_format_simple_message(self):
        """Test formatting simple log message"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test_module"
        record.funcName = "test_function"

        result = formatter.format(record)

        # Should be valid JSON
        data = json.loads(result)
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["logger"] == "test"
        assert data["module"] == "test_module"
        assert data["function"] == "test_function"
        assert data["line"] == 10

    def test_format_includes_timestamp(self):
        """Test formatted message includes timestamp"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test"

        result = formatter.format(record)
        data = json.loads(result)

        assert "timestamp" in data
        # Timestamp should be ISO format
        assert "T" in data["timestamp"]

    def test_format_with_exception(self):
        """Test formatting with exception info"""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        record.module = "test"
        record.funcName = "test"

        result = formatter.format(record)
        data = json.loads(result)

        assert "exception" in data
        assert "ValueError" in data["exception"]
        assert "Test error" in data["exception"]

    def test_format_with_extra_fields(self):
        """Test formatting with extra context fields"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test"
        record.extra_fields = {"user_id": 123, "request_id": "abc-123"}

        result = formatter.format(record)
        data = json.loads(result)

        assert data["user_id"] == 123
        assert data["request_id"] == "abc-123"


# ============================================================================
# LoggingConfig Tests
# ============================================================================


class TestLoggingConfig:
    """Test LoggingConfig class"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_setup_creates_log_directory(self, temp_log_dir):
        """Test setup creates log directory"""
        log_dir = temp_log_dir / "logs"

        logger = LoggingConfig.setup(log_dir=log_dir, logger_name="test")

        assert log_dir.exists()
        assert logger is not None

    def test_setup_returns_logger(self, temp_log_dir):
        """Test setup returns configured logger"""
        logger = LoggingConfig.setup(log_dir=temp_log_dir, logger_name="test")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test"

    def test_setup_with_log_level(self, temp_log_dir):
        """Test setup with custom log level"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            log_level=logging.DEBUG
        )

        assert logger.level == logging.DEBUG

    def test_setup_creates_log_file(self, temp_log_dir):
        """Test setup creates log file"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_file=True
        )

        log_file = temp_log_dir / "test.log"
        assert log_file.exists()

    def test_setup_creates_error_log_file(self, temp_log_dir):
        """Test setup creates separate error log file"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_file=True
        )

        error_log = temp_log_dir / "test_errors.log"
        assert error_log.exists()

    def test_setup_console_handler(self, temp_log_dir):
        """Test setup adds console handler"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_console=True,
            enable_file=False
        )

        # Should have console handler
        assert len(logger.handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_setup_file_handler(self, temp_log_dir):
        """Test setup adds file handler"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_console=False,
            enable_file=True
        )

        # Should have rotating file handlers
        assert len(logger.handlers) >= 1
        assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)

    def test_setup_with_json_format(self, temp_log_dir):
        """Test setup with JSON formatter"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_console=False,
            enable_file=True,
            enable_json=True
        )

        # Check if any handler uses JSON formatter
        json_formatters = [h.formatter for h in logger.handlers if isinstance(h.formatter, JSONFormatter)]
        assert len(json_formatters) > 0

    def test_setup_removes_existing_handlers(self, temp_log_dir):
        """Test setup removes existing handlers"""
        # Setup twice with same logger name
        logger1 = LoggingConfig.setup(log_dir=temp_log_dir, logger_name="test")
        initial_count = len(logger1.handlers)

        logger2 = LoggingConfig.setup(log_dir=temp_log_dir, logger_name="test")

        # Should not have duplicated handlers
        assert len(logger2.handlers) == initial_count

    def test_get_logger(self, temp_log_dir):
        """Test getting logger"""
        logger = LoggingConfig.get_logger("my_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "my_module"

    def test_get_logger_with_level(self, temp_log_dir):
        """Test getting logger with custom level"""
        logger = LoggingConfig.get_logger("my_module", log_level=logging.WARNING)

        assert logger.level == logging.WARNING

    def test_log_with_context(self, temp_log_dir):
        """Test logging with context"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_json=True
        )

        # Should not raise error
        LoggingConfig.log_with_context(
            logger, logging.INFO, "Test message",
            user_id=123, request_id="abc"
        )

    def test_rotation_settings(self, temp_log_dir):
        """Test rotation settings are applied"""
        rotation_size = 5 * 1024 * 1024  # 5 MB
        backup_count = 3

        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_file=True,
            rotation_size=rotation_size,
            backup_count=backup_count
        )

        # Check rotating file handlers
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                assert handler.maxBytes == rotation_size
                assert handler.backupCount == backup_count


# ============================================================================
# Convenience Functions Tests
# ============================================================================


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_setup_logger(self, temp_log_dir):
        """Test setup_logger convenience function"""
        logger = setup_logger("test_app", log_level=logging.INFO, log_dir=temp_log_dir)

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_app"

    def test_setup_logger_default_level(self, temp_log_dir):
        """Test setup_logger with default level"""
        logger = setup_logger("test_app", log_dir=temp_log_dir)

        assert logger.level == logging.INFO

    def test_get_logger_function(self):
        """Test get_logger convenience function"""
        logger = get_logger("my_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "my_module"

    def test_get_logger_with_level_function(self):
        """Test get_logger with custom level"""
        logger = get_logger("my_module", log_level=logging.ERROR)

        assert logger.level == logging.ERROR


# ============================================================================
# Integration Tests
# ============================================================================


class TestLoggingIntegration:
    """Test logging integration"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_log_messages_written_to_file(self, temp_log_dir):
        """Test log messages are written to file"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_console=False,
            enable_file=True
        )

        logger.info("Test info message")
        logger.warning("Test warning message")

        log_file = temp_log_dir / "test.log"
        content = log_file.read_text()

        assert "Test info message" in content
        assert "Test warning message" in content

    def test_error_messages_in_error_log(self, temp_log_dir):
        """Test error messages go to error log"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_file=True
        )

        logger.error("Test error message")

        error_log = temp_log_dir / "test_errors.log"
        content = error_log.read_text()

        assert "Test error message" in content

    def test_json_logging(self, temp_log_dir):
        """Test JSON logging format"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            enable_console=False,
            enable_file=True,
            enable_json=True
        )

        logger.info("JSON test message")

        log_file = temp_log_dir / "test.log"
        content = log_file.read_text()

        # Should be parseable as JSON
        lines = content.strip().split('\n')
        for line in lines:
            if line:  # Skip empty lines
                data = json.loads(line)
                if data.get("message") == "JSON test message":
                    assert data["level"] == "INFO"
                    break

    def test_multiple_loggers(self, temp_log_dir):
        """Test multiple loggers with different names"""
        logger1 = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="app1",
            enable_file=True
        )
        logger2 = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="app2",
            enable_file=True
        )

        logger1.info("App1 message")
        logger2.info("App2 message")

        app1_log = temp_log_dir / "app1.log"
        app2_log = temp_log_dir / "app2.log"

        assert app1_log.exists()
        assert app2_log.exists()
        assert "App1 message" in app1_log.read_text()
        assert "App2 message" in app2_log.read_text()

    def test_log_levels_filtering(self, temp_log_dir):
        """Test log level filtering"""
        logger = LoggingConfig.setup(
            log_dir=temp_log_dir,
            logger_name="test",
            log_level=logging.WARNING,
            enable_console=False,
            enable_file=True
        )

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        log_file = temp_log_dir / "test.log"
        content = log_file.read_text()

        # Only WARNING and above should be logged
        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" in content
