"""
Comprehensive tests for src/utils/helpers.py

Tests all helper functions to achieve >80% coverage.
"""

import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from src.utils.helpers import (
    extract_variables,
    validate_date,
    validate_email,
    validate_phone,
    format_currency,
    format_percentage,
    round_currency,
    load_config,
    save_config,
    ensure_dir,
    get_timestamp,
    get_date_string,
    sanitize_filename,
    truncate_text,
    deep_merge,
    validate_required_fields,
    parse_number,
    format_block_title,
    chunk_list,
    calculate_percentage,
)


class TestExtractVariables:
    """Test extract_variables function"""

    def test_extract_single_variable(self):
        """Test extracting single variable"""
        text = "Hello {Name}"
        result = extract_variables(text)
        assert "Name" in result
        assert len(result) == 1

    def test_extract_multiple_variables(self):
        """Test extracting multiple variables"""
        text = "{First_Name} {Last_Name} lives in {City}"
        result = extract_variables(text)
        assert "First_Name" in result
        assert "Last_Name" in result
        assert "City" in result

    def test_extract_duplicate_variables(self):
        """Test extracting duplicate variables (should be unique)"""
        text = "{Name} loves {Name}"
        result = extract_variables(text)
        assert len(result) == 1
        assert "Name" in result

    def test_extract_no_variables(self):
        """Test text with no variables"""
        text = "No variables here"
        result = extract_variables(text)
        assert len(result) == 0

    def test_extract_empty_text(self):
        """Test empty text"""
        result = extract_variables("")
        assert len(result) == 0


class TestValidateDate:
    """Test validate_date function"""

    def test_validate_valid_date(self):
        """Test validating a valid date"""
        assert validate_date("15.01.2026") is True
        assert validate_date("29.02.2024") is True  # Leap year

    def test_validate_invalid_format(self):
        """Test invalidating wrong format"""
        assert validate_date("2026-01-15") is False
        assert validate_date("15/01/2026") is False
        assert validate_date("15.1.2026") is False  # Single digit month

    def test_validate_invalid_date_values(self):
        """Test invalidating invalid date values"""
        assert validate_date("32.01.2026") is False  # Invalid day
        assert validate_date("15.13.2026") is False  # Invalid month
        assert validate_date("29.02.2025") is False  # Not a leap year

    def test_validate_empty_string(self):
        """Test validating empty string"""
        assert validate_date("") is False


class TestValidateEmail:
    """Test validate_email function"""

    def test_validate_valid_emails(self):
        """Test validating valid email addresses"""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user@example.co.uk") is True
        assert validate_email("user123@test-domain.org") is True

    def test_validate_invalid_emails(self):
        """Test invalidating invalid email addresses"""
        assert validate_email("notanemail") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False


class TestValidatePhone:
    """Test validate_phone function"""

    def test_validate_valid_phones(self):
        """Test validating valid phone numbers"""
        assert validate_phone("+49 123 456789") is True
        assert validate_phone("0123 456789") is True
        assert validate_phone("+1-555-1234") is True

    def test_validate_invalid_phones(self):
        """Test invalidating invalid phone numbers"""
        assert validate_phone("abc") is False
        assert validate_phone("") is False


class TestFormatCurrency:
    """Test format_currency function"""

    def test_format_currency_default(self):
        """Test currency formatting with default € symbol"""
        result = format_currency(25.50)
        assert "€" in result
        assert "25" in result
        assert "50" in result

    def test_format_currency_custom_symbol(self):
        """Test currency formatting with custom symbol"""
        result = format_currency(100.00, currency="$")
        assert "$" in result
        assert "100" in result

    def test_format_currency_large_number(self):
        """Test currency formatting with large number"""
        result = format_currency(1234.56)
        assert "€" in result


class TestFormatPercentage:
    """Test format_percentage function"""

    def test_format_percentage_default(self):
        """Test percentage formatting with default decimals"""
        result = format_percentage(25.50)
        assert "%" in result
        assert "25" in result

    def test_format_percentage_custom_decimals(self):
        """Test percentage formatting with custom decimals"""
        result = format_percentage(33.333, decimals=1)
        assert "%" in result

    def test_format_percentage_zero(self):
        """Test percentage formatting with zero"""
        result = format_percentage(0)
        assert "0" in result
        assert "%" in result


class TestRoundCurrency:
    """Test round_currency function"""

    def test_round_currency_up(self):
        """Test rounding up"""
        result = round_currency(25.555)
        assert result == Decimal("25.56")

    def test_round_currency_down(self):
        """Test rounding down"""
        result = round_currency(25.554)
        assert result == Decimal("25.55")

    def test_round_currency_exact(self):
        """Test no rounding needed"""
        result = round_currency(25.50)
        assert result == Decimal("25.50")

    def test_round_currency_returns_decimal(self):
        """Test return type is Decimal"""
        result = round_currency(10.00)
        assert isinstance(result, Decimal)


class TestLoadConfig:
    """Test load_config function"""

    def test_load_json_config(self, tmp_path):
        """Test loading JSON config"""
        config_data = {"key": "value", "number": 42}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        result = load_config(str(config_file))
        assert result == config_data

    def test_load_yaml_config(self, tmp_path):
        """Test loading YAML config"""
        config_data = {"key": "value", "list": [1, 2, 3]}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))
        assert result["key"] == "value"

    def test_load_yml_config(self, tmp_path):
        """Test loading .yml config"""
        config_data = {"test": True}
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))
        assert result["test"] is True

    def test_load_config_file_not_found(self):
        """Test loading non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.json")

    def test_load_config_unsupported_format(self, tmp_path):
        """Test loading unsupported file format"""
        config_file = tmp_path / "config.txt"
        config_file.write_text("data")

        with pytest.raises(ValueError, match="Unsupported file format"):
            load_config(str(config_file))


class TestSaveConfig:
    """Test save_config function"""

    def test_save_json_config(self, tmp_path):
        """Test saving JSON config"""
        config_data = {"key": "value", "number": 42}
        config_file = tmp_path / "subdir" / "config.json"

        save_config(config_data, str(config_file))

        assert config_file.exists()
        loaded = json.loads(config_file.read_text())
        assert loaded == config_data

    def test_save_yaml_config(self, tmp_path):
        """Test saving YAML config"""
        config_data = {"key": "value", "list": [1, 2, 3]}
        config_file = tmp_path / "config.yaml"

        save_config(config_data, str(config_file))

        assert config_file.exists()
        loaded = yaml.safe_load(config_file.read_text())
        assert loaded["key"] == "value"

    def test_save_config_creates_directory(self, tmp_path):
        """Test that save_config creates missing directories"""
        config_file = tmp_path / "new" / "nested" / "dir" / "config.json"
        save_config({"test": True}, str(config_file))

        assert config_file.exists()

    def test_save_config_unsupported_format(self, tmp_path):
        """Test saving unsupported file format"""
        config_file = tmp_path / "config.txt"

        with pytest.raises(ValueError, match="Unsupported file format"):
            save_config({"data": "test"}, str(config_file))


class TestEnsureDir:
    """Test ensure_dir function"""

    def test_ensure_dir_creates_directory(self, tmp_path):
        """Test creating a new directory"""
        new_dir = tmp_path / "new_directory"
        ensure_dir(str(new_dir))

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_dir_existing_directory(self, tmp_path):
        """Test with existing directory (should not raise error)"""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        ensure_dir(str(existing_dir))  # Should not raise
        assert existing_dir.exists()

    def test_ensure_dir_nested_path(self, tmp_path):
        """Test creating nested directories"""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        ensure_dir(str(nested_dir))

        assert nested_dir.exists()


class TestTimestamp:
    """Test timestamp functions"""

    def test_get_timestamp(self):
        """Test get_timestamp returns ISO format"""
        result = get_timestamp()
        assert isinstance(result, str)
        assert "T" in result  # ISO format includes T

        # Should be parseable
        datetime.fromisoformat(result)

    def test_get_date_string_default(self):
        """Test get_date_string with default format"""
        result = get_date_string()
        assert isinstance(result, str)
        assert "." in result  # DD.MM.YYYY format

    def test_get_date_string_custom_format(self):
        """Test get_date_string with custom format"""
        result = get_date_string(fmt="%Y-%m-%d")
        assert isinstance(result, str)
        assert "-" in result


class TestSanitizeFilename:
    """Test sanitize_filename function"""

    def test_sanitize_filename_invalid_chars(self):
        """Test removing invalid characters"""
        result = sanitize_filename('file<name>:with"invalid/chars.txt')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result

    def test_sanitize_filename_leading_trailing(self):
        """Test removing leading/trailing spaces and dots"""
        result = sanitize_filename("  .filename.txt.  ")
        assert not result.startswith(" ")
        assert not result.startswith(".")
        assert not result.endswith(" ")
        assert not result.endswith(".")

    def test_sanitize_filename_clean(self):
        """Test sanitizing already clean filename"""
        clean_name = "clean_filename.txt"
        result = sanitize_filename(clean_name)
        assert result == clean_name


class TestTruncateText:
    """Test truncate_text function"""

    def test_truncate_short_text(self):
        """Test truncating text shorter than max"""
        text = "Short"
        result = truncate_text(text, max_length=50)
        assert result == text

    def test_truncate_long_text(self):
        """Test truncating long text"""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test truncating with custom suffix"""
        text = "Long text here"
        result = truncate_text(text, max_length=10, suffix="…")
        assert result.endswith("…")
        assert len(result) == 10


class TestDeepMerge:
    """Test deep_merge function"""

    def test_deep_merge_simple(self):
        """Test merging simple dictionaries"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = deep_merge(dict1, dict2)

        assert result["a"] == 1
        assert result["b"] == 3  # Overridden
        assert result["c"] == 4

    def test_deep_merge_nested(self):
        """Test merging nested dictionaries"""
        dict1 = {"nested": {"a": 1, "b": 2}}
        dict2 = {"nested": {"b": 3, "c": 4}}
        result = deep_merge(dict1, dict2)

        assert result["nested"]["a"] == 1
        assert result["nested"]["b"] == 3
        assert result["nested"]["c"] == 4

    def test_deep_merge_no_override(self):
        """Test merging doesn't override non-dict values with dicts"""
        dict1 = {"key": "value"}
        dict2 = {"key": {"nested": "data"}}
        result = deep_merge(dict1, dict2)

        assert result["key"] == {"nested": "data"}


class TestValidateRequiredFields:
    """Test validate_required_fields function"""

    def test_validate_all_present(self):
        """Test validation with all required fields present"""
        data = {"name": "John", "age": 30}
        required = ["name", "age"]
        missing = validate_required_fields(data, required)

        assert len(missing) == 0

    def test_validate_missing_field(self):
        """Test validation with missing field"""
        data = {"name": "John"}
        required = ["name", "age"]
        missing = validate_required_fields(data, required)

        assert "age" in missing

    def test_validate_empty_field(self):
        """Test validation with empty field"""
        data = {"name": ""}
        required = ["name"]
        missing = validate_required_fields(data, required)

        assert "name" in missing

    def test_validate_none_field(self):
        """Test validation with None field"""
        data = {"name": None}
        required = ["name"]
        missing = validate_required_fields(data, required)

        assert "name" in missing

    def test_validate_nested_field(self):
        """Test validation with nested field using dot notation"""
        data = {"user": {"name": "John", "age": 30}}
        required = ["user.name", "user.age"]
        missing = validate_required_fields(data, required)

        assert len(missing) == 0

    def test_validate_nested_field_missing(self):
        """Test validation with missing nested field"""
        data = {"user": {"name": "John"}}
        required = ["user.name", "user.age"]
        missing = validate_required_fields(data, required)

        assert "user.age" in missing


class TestParseNumber:
    """Test parse_number function"""

    def test_parse_number_english(self):
        """Test parsing English format number"""
        assert parse_number("1234.56") == 1234.56

    def test_parse_number_german(self):
        """Test parsing German format number"""
        assert parse_number("1.234,56") == 1234.56

    def test_parse_number_integer(self):
        """Test parsing integer"""
        assert parse_number("42") == 42.0

    def test_parse_number_with_whitespace(self):
        """Test parsing number with whitespace"""
        assert parse_number("  123.45  ") == 123.45

    def test_parse_number_invalid(self):
        """Test parsing invalid number"""
        assert parse_number("abc") is None

    def test_parse_number_empty(self):
        """Test parsing empty string"""
        assert parse_number("") is None
        assert parse_number(None) is None


class TestFormatBlockTitle:
    """Test format_block_title function"""

    def test_format_block_title_zero(self):
        """Test formatting block title with ID 0"""
        result = format_block_title(0, "Introduction")
        assert "0. Introduction" in result

    def test_format_block_title_nonzero(self):
        """Test formatting block title with non-zero ID"""
        result = format_block_title(1, "Section One")
        assert "БЛОК 1: Section One" in result

    def test_format_block_title_large_id(self):
        """Test formatting block title with large ID"""
        result = format_block_title(99, "Final Section")
        assert "БЛОК 99" in result
        assert "Final Section" in result


class TestChunkList:
    """Test chunk_list function"""

    def test_chunk_list_exact(self):
        """Test chunking list with exact division"""
        lst = [1, 2, 3, 4, 5, 6]
        result = chunk_list(lst, 2)

        assert len(result) == 3
        assert result[0] == [1, 2]
        assert result[1] == [3, 4]
        assert result[2] == [5, 6]

    def test_chunk_list_remainder(self):
        """Test chunking list with remainder"""
        lst = [1, 2, 3, 4, 5]
        result = chunk_list(lst, 2)

        assert len(result) == 3
        assert result[2] == [5]

    def test_chunk_list_single_chunk(self):
        """Test chunking into single chunk"""
        lst = [1, 2, 3]
        result = chunk_list(lst, 10)

        assert len(result) == 1
        assert result[0] == [1, 2, 3]

    def test_chunk_list_empty(self):
        """Test chunking empty list"""
        result = chunk_list([], 2)
        assert len(result) == 0


class TestCalculatePercentage:
    """Test calculate_percentage function"""

    def test_calculate_percentage_normal(self):
        """Test normal percentage calculation"""
        result = calculate_percentage(25, 100)
        assert result == 25.0

    def test_calculate_percentage_half(self):
        """Test 50% calculation"""
        result = calculate_percentage(50, 100)
        assert result == 50.0

    def test_calculate_percentage_over_hundred(self):
        """Test percentage over 100%"""
        result = calculate_percentage(150, 100)
        assert result == 150.0

    def test_calculate_percentage_zero_whole(self):
        """Test percentage with zero whole"""
        result = calculate_percentage(10, 0)
        assert result == 0.0

    def test_calculate_percentage_fractional(self):
        """Test fractional percentage"""
        result = calculate_percentage(33.33, 100)
        assert result == pytest.approx(33.33, rel=0.01)


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.utils.helpers", "--cov-report=term-missing"])
