"""Formatting utilities for CLI and output"""

from typing import Dict, List, Any
from .constants import COLORS, ICONS


class Colors:
    """ANSI color codes for terminal output"""
    RESET = COLORS["reset"]
    BOLD = COLORS["bold"]
    RED = COLORS["red"]
    GREEN = COLORS["green"]
    YELLOW = COLORS["yellow"]
    BLUE = COLORS["blue"]
    MAGENTA = COLORS["magenta"]
    CYAN = COLORS["cyan"]
    WHITE = COLORS["white"]


def colored(text: str, color: str) -> str:
    """
    Return colored text for terminal

    Args:
        text: Text to color
        color: Color name (red, green, yellow, blue, magenta, cyan, white)

    Returns:
        Colored text string
    """
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def bold(text: str) -> str:
    """Return bold text"""
    return f"{COLORS['bold']}{text}{COLORS['reset']}"


def success(text: str) -> str:
    """Return success message (green with checkmark)"""
    return colored(f"{ICONS['success']} {text}", "green")


def error(text: str) -> str:
    """Return error message (red with X)"""
    return colored(f"{ICONS['error']} {text}", "red")


def warning(text: str) -> str:
    """Return warning message (yellow with warning icon)"""
    return colored(f"{ICONS['warning']} {text}", "yellow")


def info(text: str) -> str:
    """Return info message (blue with info icon)"""
    return colored(f"{ICONS['info']} {text}", "blue")


def header(text: str, char: str = "=") -> str:
    """
    Create a header with decorative line

    Args:
        text: Header text
        char: Character to use for line

    Returns:
        Formatted header
    """
    line = char * len(text)
    return f"\n{bold(line)}\n{bold(text)}\n{bold(line)}\n"


def section(text: str) -> str:
    """Create a section header"""
    return f"\n{bold(colored(text, 'cyan'))}\n{'-' * len(text)}"


def table(headers: List[str], rows: List[List[str]], col_widths: List[int] = None) -> str:
    """
    Create a formatted table

    Args:
        headers: List of header strings
        rows: List of row data (each row is a list of strings)
        col_widths: Optional list of column widths

    Returns:
        Formatted table string
    """
    if not col_widths:
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Add padding
    col_widths = [w + 2 for w in col_widths]

    # Create separator
    separator = "+" + "+".join(["-" * w for w in col_widths]) + "+"

    # Create header
    header_row = "|" + "|".join([f" {h:<{col_widths[i]-1}}" for i, h in enumerate(headers)]) + "|"

    # Create rows
    data_rows = []
    for row in rows:
        row_str = "|" + "|".join([f" {str(cell):<{col_widths[i]-1}}" for i, cell in enumerate(row)]) + "|"
        data_rows.append(row_str)

    # Combine
    result = [separator, header_row, separator]
    result.extend(data_rows)
    result.append(separator)

    return "\n".join(result)


def key_value(key: str, value: str, key_width: int = 30) -> str:
    """
    Format key-value pair

    Args:
        key: Key name
        value: Value
        key_width: Width for key column

    Returns:
        Formatted string
    """
    return f"{bold(key + ':'):<{key_width}} {value}"


def progress_bar(current: int, total: int, width: int = 50, char: str = "█") -> str:
    """
    Create a progress bar

    Args:
        current: Current progress
        total: Total items
        width: Width of progress bar
        char: Character to use for filled portion

    Returns:
        Formatted progress bar
    """
    if total == 0:
        percentage = 100
        filled = width
    else:
        percentage = int((current / total) * 100)
        filled = int((current / total) * width)

    bar = char * filled + "░" * (width - filled)
    return f"[{bar}] {percentage}% ({current}/{total})"


def box(text: str, width: int = None, padding: int = 1) -> str:
    """
    Create a box around text

    Args:
        text: Text to box
        width: Width of box (auto if None)
        padding: Padding around text

    Returns:
        Boxed text
    """
    lines = text.split('\n')
    if width is None:
        width = max(len(line) for line in lines) + (padding * 2)

    top = "┌" + "─" * width + "┐"
    bottom = "└" + "─" * width + "┘"

    boxed_lines = [top]
    for line in lines:
        padded_line = " " * padding + line.ljust(width - padding * 2) + " " * padding
        boxed_lines.append("│" + padded_line + "│")
    boxed_lines.append(bottom)

    return "\n".join(boxed_lines)


def list_items(items: List[str], bullet: str = None) -> str:
    """
    Format a list of items

    Args:
        items: List of items
        bullet: Bullet character (default from ICONS)

    Returns:
        Formatted list
    """
    if bullet is None:
        bullet = ICONS['bullet']

    return "\n".join([f"  {bullet} {item}" for item in items])


def numbered_list(items: List[str]) -> str:
    """
    Format a numbered list

    Args:
        items: List of items

    Returns:
        Formatted numbered list
    """
    return "\n".join([f"  {i+1}. {item}" for i, item in enumerate(items)])


def format_dict(data: Dict[str, Any], indent: int = 0) -> str:
    """
    Format dictionary for display

    Args:
        data: Dictionary to format
        indent: Indentation level

    Returns:
        Formatted string
    """
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{bold(key)}:")
            lines.append(format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{bold(key)}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(format_dict(item, indent + 1))
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            lines.append(f"{prefix}{bold(key)}: {value}")

    return "\n".join(lines)


def divider(char: str = "-", width: int = 80) -> str:
    """Create a divider line"""
    return char * width


def title_box(text: str) -> str:
    """Create a fancy title box"""
    width = len(text) + 4
    top = "╔" + "═" * width + "╗"
    middle = "║  " + text + "  ║"
    bottom = "╚" + "═" * width + "╝"
    return "\n".join([top, middle, bottom])

# ========== Additional formatting functions ==========

def format_currency(amount: float, currency: str = "€", decimals: int = 2) -> str:
    """
    Format a number as currency

    Args:
        amount: Amount to format
        currency: Currency symbol (default: €)
        decimals: Number of decimal places

    Returns:
        Formatted currency string

    Examples:
        >>> format_currency(1234.56)
        '1.234,56 €'
        >>> format_currency(1000, currency="$")
        '1.000,00 $'
    """
    # Format with German-style thousands separator (.) and decimal comma (,)
    formatted = f"{amount:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted} {currency}"


def format_percentage(value: float, decimals: int = 1, include_sign: bool = True) -> str:
    """
    Format a number as percentage

    Args:
        value: Value to format (e.g., 0.075 for 7.5%)
        decimals: Number of decimal places
        include_sign: Whether to include % sign

    Returns:
        Formatted percentage string

    Examples:
        >>> format_percentage(0.075)
        '7.5%'
        >>> format_percentage(12.345, decimals=2)
        '12.35%'
    """
    formatted = f"{value:.{decimals}f}"
    return f"{formatted}%" if include_sign else formatted


def format_date(date_obj, format_str: str = "%d.%m.%Y") -> str:
    """
    Format a date object as string

    Args:
        date_obj: datetime or date object (or string to pass through)
        format_str: Format string (default: DD.MM.YYYY)

    Returns:
        Formatted date string

    Examples:
        >>> from datetime import datetime
        >>> format_date(datetime(2026, 1, 11))
        '11.01.2026'
    """
    from datetime import datetime, date

    # If already a string, return as-is
    if isinstance(date_obj, str):
        return date_obj

    # If datetime or date object, format it
    if isinstance(date_obj, (datetime, date)):
        return date_obj.strftime(format_str)

    # Fallback
    return str(date_obj)


def truncate_text(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add (default: ...)

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("This is a very long text", max_length=15)
        'This is a ve...'
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
