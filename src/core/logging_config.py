"""
Centralized logging configuration for Daten20 (v1.0-v30.0)

Provides structured logging with:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation and retention policies
- JSON formatting for structured logs
- Console and file handlers
- Integration with monitoring systems
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class LoggingConfig:
    """Centralized logging configuration manager"""

    DEFAULT_LOG_DIR = Path("logs")
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def setup(
        cls,
        log_dir: Optional[Path] = None,
        log_level: int = DEFAULT_LOG_LEVEL,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = False,
        rotation_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        logger_name: Optional<str> = None,
    ) -> logging.Logger:
        """
        Setup logging configuration

        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console output
            enable_file: Enable file output
            enable_json: Use JSON format for file output
            rotation_size: Max size per log file in bytes
            backup_count: Number of backup files to keep
            logger_name: Name of the logger (None = root logger)

        Returns:
            Configured logger instance
        """
        # Create log directory
        if log_dir is None:
            log_dir = cls.DEFAULT_LOG_DIR
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Get or create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_formatter = logging.Formatter(
                cls.DEFAULT_FORMAT,
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # File handler with rotation
        if enable_file:
            log_file = log_dir / f"{logger_name or 'daten20'}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=rotation_size,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setLevel(log_level)

            if enable_json:
                file_formatter = JSONFormatter()
            else:
                file_formatter = logging.Formatter(
                    cls.DEFAULT_FORMAT,
                    datefmt="%Y-%m-%d %H:%M:%S"
                )

            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Error file handler (always enabled if file logging is enabled)
        if enable_file:
            error_log_file = log_dir / f"{logger_name or 'daten20'}_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=rotation_size,
                backupCount=backup_count,
                encoding="utf-8"
            )
            error_handler.setLevel(logging.ERROR)

            if enable_json:
                error_formatter = JSONFormatter()
            else:
                error_formatter = logging.Formatter(
                    cls.DEFAULT_FORMAT,
                    datefmt="%Y-%m-%d %H:%M:%S"
                )

            error_handler.setFormatter(error_formatter)
            logger.addHandler(error_handler)

        logger.info(f"Logging configured for {logger_name or 'root'}")

        return logger

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_level: Optional[int] = None
    ) -> logging.Logger:
        """
        Get a logger with the specified name

        Args:
            name: Logger name (usually __name__)
            log_level: Optional log level override

        Returns:
            Logger instance
        """
        logger = logging.getLogger(name)

        if log_level is not None:
            logger.setLevel(log_level)
        elif not logger.handlers:
            # Setup default configuration if not already configured
            return cls.setup(logger_name=name)

        return logger

    @classmethod
    def log_with_context(
        cls,
        logger: logging.Logger,
        level: int,
        message: str,
        **context: Any
    ) -> None:
        """
        Log message with additional context

        Args:
            logger: Logger instance
            level: Log level
            message: Log message
            **context: Additional context fields
        """
        extra = {"extra_fields": context}
        logger.log(level, message, extra=extra)


# Convenience functions
def setup_logger(
    name: Optional[str] = None,
    log_level: int = logging.INFO,
    **kwargs
) -> logging.Logger:
    """Setup and return a configured logger"""
    return LoggingConfig.setup(logger_name=name, log_level=log_level, **kwargs)


def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """Get a logger instance"""
    return LoggingConfig.get_logger(name, log_level)


# Module-level logger for this file
_logger = get_logger(__name__)


__all__ = [
    "LoggingConfig",
    "JSONFormatter",
    "setup_logger",
    "get_logger",
]
