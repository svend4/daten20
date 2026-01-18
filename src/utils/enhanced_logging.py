#!/usr/bin/env python3
"""
Enhanced Colored Logging Messages
==================================

Provides beautiful, colored, and context-rich logging messages for CLI tools.

Features:
- Color-coded log levels
- Icons and symbols
- Progress indicators
- Contextual information
- User-friendly messages
- Actionable suggestions

Author: Document Management System
Version: 1.0.0
"""

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class Icons:
    """Icons and symbols for different message types"""

    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    DEBUG = "⚙"
    QUESTION = "?"
    ARROW = "→"
    BULLET = "•"
    SPARKLES = "✨"
    FIRE = "🔥"
    ROCKET = "🚀"
    CLOCK = "⏱"
    DOCUMENT = "📄"
    FOLDER = "📁"
    CHECK = "✅"
    CROSS = "❌"
    HOURGLASS = "⏳"
    MAGNIFYING_GLASS = "🔍"
    LOCK = "🔒"
    KEY = "🔑"
    SHIELD = "🛡"
    CHART = "📊"
    GEAR = "⚙️"


class MessageLevel(Enum):
    """Message severity levels"""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and icons"""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLACK,
        logging.INFO: Colors.BRIGHT_BLUE,
        logging.WARNING: Colors.BRIGHT_YELLOW,
        logging.ERROR: Colors.BRIGHT_RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE + Colors.BOLD,
    }

    LEVEL_ICONS = {
        logging.DEBUG: Icons.DEBUG,
        logging.INFO: Icons.INFO,
        logging.WARNING: Icons.WARNING,
        logging.ERROR: Icons.ERROR,
        logging.CRITICAL: Icons.FIRE,
    }

    def __init__(self, use_colors: bool = True, show_icons: bool = True):
        """
        Initialize colored formatter

        Args:
            use_colors: Enable color output
            show_icons: Show icons for log levels
        """
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
        self.show_icons = show_icons

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and icons"""
        # Get color and icon for level
        color = self.LEVEL_COLORS.get(record.levelno, "")
        icon = self.LEVEL_ICONS.get(record.levelno, "")

        # Build message
        if self.use_colors:
            timestamp = f"{Colors.DIM}{self.formatTime(record, '%H:%M:%S')}{Colors.RESET}"
            level = f"{color}{record.levelname:8s}{Colors.RESET}"
            name = f"{Colors.CYAN}{record.name}{Colors.RESET}"
            message = record.getMessage()

            # Add icon if enabled
            if self.show_icons:
                formatted = f"{timestamp} {icon}  {level} {name} {Icons.ARROW} {message}"
            else:
                formatted = f"{timestamp} {level} {name} {Icons.ARROW} {message}"
        else:
            timestamp = self.formatTime(record, "%H:%M:%S")
            formatted = f"{timestamp} {record.levelname:8s} {record.name} → {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


class EnhancedLogger:
    """Enhanced logger with beautiful, informative messages"""

    def __init__(self, name: str, use_colors: bool = True, show_icons: bool = True):
        """
        Initialize enhanced logger

        Args:
            name: Logger name
            use_colors: Enable colored output
            show_icons: Show icons in messages
        """
        self.logger = logging.getLogger(name)
        self.use_colors = use_colors and sys.stdout.isatty()
        self.show_icons = show_icons

        # Setup colored handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(ColoredFormatter(use_colors, show_icons))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _colorize(self, text: str, color: str) -> str:
        """Colorize text if colors are enabled"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text

    def _icon(self, icon: str) -> str:
        """Return icon if icons are enabled"""
        return f"{icon} " if self.show_icons else ""

    def success(self, message: str, **context):
        """Log success message"""
        icon = self._icon(Icons.CHECK)
        colored_msg = self._colorize(message, Colors.BRIGHT_GREEN)
        self.logger.info(f"{icon}{colored_msg}", extra=context)

    def error_with_suggestion(self, error: str, suggestion: str, **context):
        """Log error with actionable suggestion"""
        icon = self._icon(Icons.CROSS)
        error_msg = self._colorize(f"Error: {error}", Colors.BRIGHT_RED)
        suggestion_msg = self._colorize(f"💡 Try: {suggestion}", Colors.BRIGHT_YELLOW)

        self.logger.error(f"{icon}{error_msg}\n   {suggestion_msg}", extra=context)

    def warning_with_action(self, warning: str, action: str, **context):
        """Log warning with recommended action"""
        icon = self._icon(Icons.WARNING)
        warning_msg = self._colorize(f"Warning: {warning}", Colors.BRIGHT_YELLOW)
        action_msg = self._colorize(f"→ Action: {action}", Colors.BRIGHT_CYAN)

        self.logger.warning(f"{icon}{warning_msg}\n   {action_msg}", extra=context)

    def operation_start(self, operation: str, **details):
        """Log operation start"""
        icon = self._icon(Icons.ROCKET)
        msg = self._colorize(f"Starting: {operation}", Colors.BRIGHT_BLUE)

        detail_str = ""
        if details:
            detail_str = " " + ", ".join(f"{k}={v}" for k, v in details.items())

        self.logger.info(f"{icon}{msg}{detail_str}")

    def operation_complete(self, operation: str, duration: Optional[float] = None, **results):
        """Log operation completion"""
        icon = self._icon(Icons.CHECK)
        msg = self._colorize(f"Completed: {operation}", Colors.BRIGHT_GREEN)

        if duration:
            duration_str = self._colorize(f"({duration:.2f}s)", Colors.DIM)
            msg = f"{msg} {duration_str}"

        result_str = ""
        if results:
            result_str = "\n   " + "\n   ".join(f"• {k}: {v}" for k, v in results.items())

        self.logger.info(f"{icon}{msg}{result_str}")

    def progress(self, current: int, total: int, operation: str):
        """Log progress update"""
        icon = self._icon(Icons.HOURGLASS)
        percent = (current / total * 100) if total > 0 else 0
        bar_length = 20
        filled = int(bar_length * current / total) if total > 0 else 0

        if self.use_colors:
            bar = Colors.BRIGHT_GREEN + "█" * filled + Colors.DIM + "░" * (bar_length - filled) + Colors.RESET
            msg = f"{icon}{operation}: [{bar}] {percent:.0f}% ({current}/{total})"
        else:
            bar = "=" * filled + "-" * (bar_length - filled)
            msg = f"{icon}{operation}: [{bar}] {percent:.0f}% ({current}/{total})"

        self.logger.info(msg)

    def file_operation(self, action: str, file_path: str, **details):
        """Log file operation"""
        icon = self._icon(Icons.DOCUMENT)
        action_msg = self._colorize(action, Colors.BRIGHT_CYAN)
        file_msg = self._colorize(file_path, Colors.UNDERLINE)

        detail_str = ""
        if details:
            detail_str = " - " + ", ".join(f"{k}={v}" for k, v in details.items())

        self.logger.info(f"{icon}{action_msg}: {file_msg}{detail_str}")

    def security_event(self, event_type: str, severity: str, details: str):
        """Log security event"""
        icon = self._icon(Icons.SHIELD)
        severity_colors = {
            "low": Colors.BRIGHT_GREEN,
            "medium": Colors.BRIGHT_YELLOW,
            "high": Colors.BRIGHT_RED,
            "critical": Colors.BG_RED + Colors.WHITE + Colors.BOLD,
        }

        color = severity_colors.get(severity.lower(), Colors.BRIGHT_YELLOW)
        severity_msg = self._colorize(f"[{severity.upper()}]", color)
        event_msg = self._colorize(event_type, Colors.BRIGHT_MAGENTA)

        self.logger.warning(f"{icon}{severity_msg} {event_msg}: {details}")

    def data_summary(self, title: str, data: Dict[str, Any]):
        """Log data summary with key-value pairs"""
        icon = self._icon(Icons.CHART)
        title_msg = self._colorize(title, Colors.BRIGHT_CYAN + Colors.BOLD)

        summary = f"{icon}{title_msg}"
        for key, value in data.items():
            key_colored = self._colorize(f"  • {key}:", Colors.BRIGHT_WHITE)
            value_colored = self._colorize(str(value), Colors.BRIGHT_GREEN)
            summary += f"\n{key_colored} {value_colored}"

        self.logger.info(summary)

    def validation_result(self, passed: bool, item: str, details: Optional[str] = None):
        """Log validation result"""
        if passed:
            icon = self._icon(Icons.CHECK)
            msg = self._colorize(f"✓ Valid: {item}", Colors.BRIGHT_GREEN)
        else:
            icon = self._icon(Icons.CROSS)
            msg = self._colorize(f"✗ Invalid: {item}", Colors.BRIGHT_RED)

        if details:
            msg += f"\n   {self._colorize(details, Colors.DIM)}"

        level = logging.INFO if passed else logging.WARNING
        self.logger.log(level, msg)

    def debug(self, message: str, **context):
        """Log debug message"""
        self.logger.debug(message, extra=context)

    def info(self, message: str, **context):
        """Log info message"""
        self.logger.info(message, extra=context)

    def warning(self, message: str, **context):
        """Log warning message"""
        self.logger.warning(message, extra=context)

    def error(self, message: str, **context):
        """Log error message"""
        self.logger.error(message, extra=context)

    def critical(self, message: str, **context):
        """Log critical message"""
        self.logger.critical(message, extra=context)


# Convenience functions
def get_enhanced_logger(name: str, use_colors: bool = True, show_icons: bool = True) -> EnhancedLogger:
    """
    Get an enhanced logger instance

    Args:
        name: Logger name
        use_colors: Enable colored output
        show_icons: Show icons in messages

    Returns:
        EnhancedLogger instance
    """
    return EnhancedLogger(name, use_colors, show_icons)


def setup_enhanced_logging(level: str = "INFO", use_colors: bool = True, show_icons: bool = True):
    """
    Setup enhanced logging globally

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Enable colored output
        show_icons: Show icons in messages
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add colored handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(use_colors, show_icons))
    root_logger.addHandler(handler)


__all__ = [
    "EnhancedLogger",
    "ColoredFormatter",
    "Colors",
    "Icons",
    "MessageLevel",
    "get_enhanced_logger",
    "setup_enhanced_logging",
]
