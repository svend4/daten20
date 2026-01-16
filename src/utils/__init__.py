"""
Utility functions and helpers (v1.0-v2.3)

Common utilities:
- Constants and configuration values
- Formatting functions (currency, dates, etc.)
- Helper functions
"""

from .constants import (
    EXPORT_FORMATS,
    FUNDING_SOURCES,
    REGIONAL_COEFFICIENTS,
    SERVICE_TYPES,
)
from .formatting import (
    format_currency,
    format_date,
    format_percentage,
    truncate_text,
)
from .helpers import (
    get_date_string,
    load_config,
    round_currency,
    sanitize_filename,
    save_config,
)

__all__ = [
    # Constants
    "SERVICE_TYPES",
    "REGIONAL_COEFFICIENTS",
    "FUNDING_SOURCES",
    "EXPORT_FORMATS",
    # Formatting
    "format_currency",
    "format_percentage",
    "format_date",
    "truncate_text",
    # Helpers
    "load_config",
    "save_config",
    "get_date_string",
    "sanitize_filename",
    "round_currency",
]

__version__ = "2.3.0"
