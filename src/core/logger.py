"""
Comprehensive Logging System

Centralized logging configuration for the Document Management System.
Supports multiple handlers, log rotation, and structured logging.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record):
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"

        # Format the message
        result = super().format(record)

        # Reset levelname for other handlers
        record.levelname = levelname

        return result


class RequestFormatter(logging.Formatter):
    """Formatter for HTTP request logging."""

    def format(self, record):
        """Format log record with request context."""
        # Add request ID if available
        if hasattr(record, "request_id"):
            record.msg = f"[{record.request_id}] {record.msg}"

        return super().format(record)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Enable console output
        enable_file: Enable file output
        log_format: Custom log format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler with colors
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if enable_file and log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def setup_application_logging(config) -> dict:
    """
    Set up comprehensive application logging.

    Args:
        config: Application configuration object

    Returns:
        Dictionary of configured loggers
    """
    loggers = {}

    # Main application logger
    loggers["app"] = setup_logger(
        "dms.app",
        log_file=config.LOG_FILE,
        log_level=config.LOG_LEVEL,
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        log_format=config.LOG_FORMAT,
    )

    # API logger
    loggers["api"] = setup_logger(
        "dms.api",
        log_file=str(config.LOG_DIR / "api.log"),
        log_level=config.LOG_LEVEL,
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Database logger
    loggers["db"] = setup_logger(
        "dms.database",
        log_file=str(config.LOG_DIR / "database.log"),
        log_level=config.LOG_LEVEL,
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Security logger (separate file for security events)
    loggers["security"] = setup_logger(
        "dms.security",
        log_file=str(config.LOG_DIR / "security.log"),
        log_level="INFO",  # Always log security events
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=10,  # Keep more security logs
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Error logger (separate file for errors only)
    error_logger = setup_logger(
        "dms.errors",
        log_file=str(config.LOG_DIR / "errors.log"),
        log_level="ERROR",
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        enable_console=False,  # Don't duplicate to console
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
    )
    loggers["errors"] = error_logger

    # Performance logger
    loggers["performance"] = setup_logger(
        "dms.performance",
        log_file=str(config.LOG_DIR / "performance.log"),
        log_level="INFO",
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        enable_console=False,
        log_format="%(asctime)s - %(message)s",
    )

    return loggers


class LogContext:
    """Context manager for adding context to log messages."""

    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = None

    def __enter__(self):
        """Enter context and add context to logger."""
        self.old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original factory."""
        logging.setLogRecordFactory(self.old_factory)


def log_performance(logger: logging.Logger, operation: str):
    """
    Decorator to log performance of functions.

    Args:
        logger: Logger instance
        operation: Description of the operation

    Example:
        @log_performance(logger, 'calculate_costs')
        def calculate_costs():
            ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"{operation} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"{operation} failed after {duration:.3f}s: {str(e)}")
                raise

        return wrapper

    return decorator


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(f"dms.{name}")


# Example usage
if __name__ == "__main__":
    # Example: Set up logger
    logger = setup_logger("test", log_file="logs/test.log", log_level="DEBUG")

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Example: Log context
    with LogContext(logger, request_id="12345"):
        logger.info("Processing request")

    # Example: Performance logging
    perf_logger = get_logger("performance")

    @log_performance(perf_logger, "test_operation")
    def test_function():
        import time

        time.sleep(0.1)

    test_function()
