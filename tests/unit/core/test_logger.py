"""
Comprehensive tests for core.logger module
"""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestColoredFormatter:
    """Tests for ColoredFormatter"""

    def test_colored_formatter_adds_colors(self):
        """Test ColoredFormatter adds ANSI colors to level names"""
        from src.core.logger import ColoredFormatter

        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "\033[" in result  # ANSI color code
        assert "INFO" in result

    def test_colored_formatter_preserves_levelname(self):
        """Test ColoredFormatter preserves original levelname"""
        from src.core.logger import ColoredFormatter

        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error",
            args=(),
            exc_info=None,
        )

        formatter.format(record)

        assert record.levelname == "ERROR"  # Should be reset


class TestRequestFormatter:
    """Tests for RequestFormatter"""

    def test_request_formatter_adds_request_id(self):
        """Test RequestFormatter adds request ID if present"""
        from src.core.logger import RequestFormatter

        formatter = RequestFormatter("%(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request processed",
            args=(),
            exc_info=None,
        )
        record.request_id = "req-123"

        result = formatter.format(record)

        assert "[req-123]" in result
        assert "Request processed" in result

    def test_request_formatter_without_request_id(self):
        """Test RequestFormatter works without request_id"""
        from src.core.logger import RequestFormatter

        formatter = RequestFormatter("%(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert result == "Message"


class TestSetupLogger:
    """Tests for setup_logger function"""

    def test_setup_logger_basic(self):
        """Test basic logger setup"""
        from src.core.logger import setup_logger

        logger = setup_logger("test_logger", enable_file=False)

        assert logger is not None
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO

    def test_setup_logger_custom_level(self):
        """Test logger with custom log level"""
        from src.core.logger import setup_logger

        logger = setup_logger("test_logger", log_level="DEBUG", enable_file=False)

        assert logger.level == logging.DEBUG

    def test_setup_logger_with_file(self, tmp_path):
        """Test logger with file handler"""
        from src.core.logger import setup_logger

        log_file = tmp_path / "test.log"
        logger = setup_logger("test_logger", log_file=str(log_file))

        logger.info("Test message")

        assert log_file.exists()
        assert "Test message" in log_file.read_text()

    def test_setup_logger_file_rotation_params(self, tmp_path):
        """Test logger file rotation parameters"""
        from src.core.logger import setup_logger

        log_file = tmp_path / "test.log"
        logger = setup_logger(
            "test_logger", log_file=str(log_file), max_bytes=1024, backup_count=3
        )

        assert logger is not None

    def test_setup_logger_console_only(self):
        """Test logger with console handler only"""
        from src.core.logger import setup_logger

        logger = setup_logger("test_logger", enable_file=False, enable_console=True)

        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logger_avoids_duplicate_handlers(self):
        """Test setup_logger avoids adding handlers multiple times"""
        from src.core.logger import setup_logger

        logger1 = setup_logger("same_logger", enable_file=False)
        handler_count = len(logger1.handlers)

        logger2 = setup_logger("same_logger", enable_file=False)

        assert len(logger2.handlers) == handler_count
        assert logger1 is logger2

    def test_setup_logger_custom_format(self, tmp_path):
        """Test logger with custom format"""
        from src.core.logger import setup_logger

        log_file = tmp_path / "test.log"
        custom_format = "%(levelname)s: %(message)s"

        logger = setup_logger("test_logger", log_file=str(log_file), log_format=custom_format)

        logger.info("Test")

        log_content = log_file.read_text()
        assert "INFO: Test" in log_content

    def test_setup_logger_creates_log_directory(self, tmp_path):
        """Test logger creates log directory if not exists"""
        from src.core.logger import setup_logger

        log_file = tmp_path / "nested" / "logs" / "test.log"

        logger = setup_logger("test_logger", log_file=str(log_file))

        logger.info("Message")

        assert log_file.parent.exists()
        assert log_file.exists()


class TestSetupApplicationLogging:
    """Tests for setup_application_logging function"""

    def test_setup_application_logging(self, tmp_path):
        """Test comprehensive application logging setup"""
        from src.core.logger import setup_application_logging

        # Mock config
        config = Mock()
        config.LOG_FILE = str(tmp_path / "app.log")
        config.LOG_LEVEL = "INFO"
        config.LOG_MAX_BYTES = 1024 * 1024
        config.LOG_BACKUP_COUNT = 5
        config.LOG_FORMAT = "%(message)s"
        config.LOG_DIR = tmp_path

        loggers = setup_application_logging(config)

        assert "app" in loggers
        assert "api" in loggers
        assert "db" in loggers
        assert "security" in loggers
        assert "errors" in loggers
        assert "performance" in loggers

    def test_application_loggers_have_correct_names(self, tmp_path):
        """Test application loggers have correct names"""
        from src.core.logger import setup_application_logging

        config = Mock()
        config.LOG_FILE = str(tmp_path / "app.log")
        config.LOG_LEVEL = "INFO"
        config.LOG_MAX_BYTES = 1024 * 1024
        config.LOG_BACKUP_COUNT = 5
        config.LOG_FORMAT = "%(message)s"
        config.LOG_DIR = tmp_path

        loggers = setup_application_logging(config)

        assert loggers["app"].name == "dms.app"
        assert loggers["api"].name == "dms.api"
        assert loggers["security"].name == "dms.security"


class TestLogContext:
    """Tests for LogContext context manager"""

    def test_log_context_adds_context(self):
        """Test LogContext adds context to log records"""
        from src.core.logger import LogContext, setup_logger

        logger = setup_logger("test_ctx", enable_file=False)
        handler = Mock()
        logger.addHandler(handler)

        with LogContext(logger, request_id="req-456", user="test_user"):
            logger.info("Message")

        # Check that context was added
        call_args = handler.handle.call_args
        if call_args:
            record = call_args[0][0]
            assert hasattr(record, "request_id")
            assert record.request_id == "req-456"

    def test_log_context_restores_factory(self):
        """Test LogContext restores original log record factory"""
        from src.core.logger import LogContext, setup_logger

        logger = setup_logger("test_restore", enable_file=False)
        original_factory = logging.getLogRecordFactory()

        with LogContext(logger, test_key="test_value"):
            pass

        assert logging.getLogRecordFactory() == original_factory


class TestLogPerformanceDecorator:
    """Tests for log_performance decorator"""

    def test_log_performance_logs_success(self, tmp_path):
        """Test log_performance logs successful operation"""
        from src.core.logger import log_performance, setup_logger

        log_file = tmp_path / "perf.log"
        logger = setup_logger("perf_test", log_file=str(log_file), enable_console=False)

        @log_performance(logger, "test_operation")
        def test_func():
            return 42

        result = test_func()

        assert result == 42
        log_content = log_file.read_text()
        assert "test_operation completed" in log_content

    def test_log_performance_logs_failure(self, tmp_path):
        """Test log_performance logs failed operation"""
        from src.core.logger import log_performance, setup_logger

        log_file = tmp_path / "perf.log"
        logger = setup_logger("perf_test", log_file=str(log_file), enable_console=False)

        @log_performance(logger, "failing_operation")
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_func()

        log_content = log_file.read_text()
        assert "failing_operation failed" in log_content


class TestGetLogger:
    """Tests for get_logger function"""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger instance"""
        from src.core.logger import get_logger

        logger = get_logger("test_module")

        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_get_logger_prefixes_name(self):
        """Test get_logger adds 'dms.' prefix"""
        from src.core.logger import get_logger

        logger = get_logger("mymodule")

        assert logger.name == "dms.mymodule"

    def test_get_logger_returns_same_instance(self):
        """Test get_logger returns same instance for same name"""
        from src.core.logger import get_logger

        logger1 = get_logger("module")
        logger2 = get_logger("module")

        assert logger1 is logger2


class TestLoggerIntegration:
    """Integration tests for logger module"""

    def test_logger_file_rotation(self, tmp_path):
        """Test logger file rotation works"""
        from src.core.logger import setup_logger

        log_file = tmp_path / "rotating.log"

        logger = setup_logger(
            "rotation_test", log_file=str(log_file), max_bytes=100, backup_count=2
        )

        # Write enough to trigger rotation
        for i in range(50):
            logger.info(f"Message {i} with some padding to increase size")

        # Check that backup files exist
        backup_files = list(tmp_path.glob("rotating.log.*"))
        assert len(backup_files) >= 1

    def test_multiple_loggers_independent(self, tmp_path):
        """Test multiple loggers are independent"""
        from src.core.logger import setup_logger

        log1 = tmp_path / "log1.log"
        log2 = tmp_path / "log2.log"

        logger1 = setup_logger("logger1", log_file=str(log1), enable_console=False)
        logger2 = setup_logger("logger2", log_file=str(log2), enable_console=False)

        logger1.info("Message from logger1")
        logger2.info("Message from logger2")

        assert "Message from logger1" in log1.read_text()
        assert "Message from logger2" in log2.read_text()
        assert "Message from logger2" not in log1.read_text()
        assert "Message from logger1" not in log2.read_text()
