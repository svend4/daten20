"""Helper functions for the Document Management System"""

import re
import os
import json
import yaml
from datetime import datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP

from .constants import VARIABLE_PATTERN, DATE_PATTERN, EMAIL_PATTERN, PHONE_PATTERN


def extract_variables(text: str) -> List[str]:
    """
    Extract all variables from text in format {Variable_Name}

    Args:
        text: Text to search for variables

    Returns:
        List of unique variable names (without braces)
    """
    matches = re.findall(VARIABLE_PATTERN, text)
    return list(set(matches))


def validate_date(date_str: str) -> bool:
    """
    Validate date string in DD.MM.YYYY format

    Args:
        date_str: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    if not re.match(DATE_PATTERN, date_str):
        return False

    try:
        day, month, year = map(int, date_str.split('.'))
        datetime(year, month, day)
        return True
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """Validate email address"""
    return bool(re.match(EMAIL_PATTERN, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    return bool(re.match(PHONE_PATTERN, phone))


def format_currency(amount: float, currency: str = "€") -> str:
    """
    Format number as currency

    Args:
        amount: Amount to format
        currency: Currency symbol

    Returns:
        Formatted string (e.g., "25,50 €")
    """
    return f"{amount:,.2f} {currency}".replace(",", " ").replace(".", ",").replace(" ", ".", 1)


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format number as percentage

    Args:
        value: Value to format
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "25,50%")
    """
    formatted = f"{value:.{decimals}f}%".replace(".", ",")
    return formatted


def round_currency(amount: float) -> Decimal:
    """
    Round amount to 2 decimal places using ROUND_HALF_UP

    Args:
        amount: Amount to round

    Returns:
        Rounded Decimal
    """
    return Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON or YAML file

    Args:
        file_path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    with open(file_path, 'r', encoding='utf-8') as f:
        if ext == '.json':
            return json.load(f)
        elif ext in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use .json or .yaml")


def save_config(config: Dict[str, Any], file_path: str) -> None:
    """
    Save configuration to JSON or YAML file

    Args:
        config: Configuration dictionary
        file_path: Path to save file

    Raises:
        ValueError: If file format is not supported
    """
    ext = os.path.splitext(file_path)[1].lower()

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        if ext == '.json':
            json.dump(config, f, ensure_ascii=False, indent=2)
        elif ext in ['.yaml', '.yml']:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use .json or .yaml")


def ensure_dir(directory: str) -> None:
    """
    Ensure directory exists, create if it doesn't

    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def get_date_string(fmt: str = "%d.%m.%Y") -> str:
    """
    Get current date as formatted string

    Args:
        fmt: Date format string

    Returns:
        Formatted date string
    """
    return datetime.now().strftime(fmt)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    return filename


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries

    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge (overrides dict1)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
    """
    Validate that all required fields are present and not empty

    Args:
        data: Dictionary to validate
        required_fields: List of required field names (can use dot notation for nested fields)

    Returns:
        List of missing or empty fields
    """
    missing = []

    for field in required_fields:
        parts = field.split('.')
        value = data

        try:
            for part in parts:
                value = value[part]

            # Check if value is empty
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        except (KeyError, TypeError):
            missing.append(field)

    return missing


def parse_number(value: str) -> Optional[float]:
    """
    Parse number from string, handling both German and English formats

    Args:
        value: String to parse

    Returns:
        Parsed number or None if invalid
    """
    if not value:
        return None

    # Remove whitespace
    value = value.strip()

    # Handle German format (1.234,56)
    if ',' in value:
        value = value.replace('.', '').replace(',', '.')

    try:
        return float(value)
    except ValueError:
        return None


def format_block_title(block_id: int, title: str) -> str:
    """
    Format block title with ID

    Args:
        block_id: Block number
        title: Block title

    Returns:
        Formatted string
    """
    if block_id == 0:
        return f"{block_id}. {title}"
    else:
        return f"БЛОК {block_id}: {title}"


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage

    Args:
        part: Part value
        whole: Whole value

    Returns:
        Percentage (0-100)
    """
    if whole == 0:
        return 0.0
    return (part / whole) * 100
