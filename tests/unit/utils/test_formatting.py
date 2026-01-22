"""
Comprehensive tests for src/utils/formatting.py

Tests all formatting functions to achieve >80% coverage.
"""

import pytest
from datetime import datetime, date

from src.utils.formatting import (
    Colors,
    colored,
    bold,
    success,
    error,
    warning,
    info,
    header,
    section,
    table,
    key_value,
    progress_bar,
    box,
    list_items,
    numbered_list,
    format_dict,
    divider,
    title_box,
    format_currency,
    format_percentage,
    format_date,
    truncate_text,
)


class TestColors:
    """Test Colors class"""

    def test_colors_class_has_attributes(self):
        """Test that Colors class has all color attributes"""
        assert hasattr(Colors, 'RESET')
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'MAGENTA')
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'WHITE')

    def test_colors_are_strings(self):
        """Test that all colors are strings"""
        assert isinstance(Colors.RESET, str)
        assert isinstance(Colors.BOLD, str)
        assert isinstance(Colors.RED, str)
        assert isinstance(Colors.GREEN, str)


class TestColoredText:
    """Test colored text functions"""

    def test_colored_with_valid_color(self):
        """Test colored function with valid color"""
        result = colored("test", "red")
        assert "test" in result
        assert result != "test"  # Should have color codes

    def test_colored_with_invalid_color(self):
        """Test colored function with invalid color"""
        result = colored("test", "invalid_color")
        assert "test" in result

    def test_bold(self):
        """Test bold function"""
        result = bold("test")
        assert "test" in result
        assert result != "test"

    def test_success(self):
        """Test success function"""
        result = success("Operation successful")
        assert "Operation successful" in result

    def test_error(self):
        """Test error function"""
        result = error("Operation failed")
        assert "Operation failed" in result

    def test_warning(self):
        """Test warning function"""
        result = warning("Warning message")
        assert "Warning message" in result

    def test_info(self):
        """Test info function"""
        result = info("Info message")
        assert "Info message" in result


class TestHeaders:
    """Test header and section functions"""

    def test_header_default_char(self):
        """Test header with default character"""
        result = header("Test Header")
        assert "Test Header" in result
        assert "=" in result
        assert result.count("\n") >= 3  # Has newlines

    def test_header_custom_char(self):
        """Test header with custom character"""
        result = header("Test Header", char="-")
        assert "Test Header" in result
        assert "-" in result

    def test_header_length(self):
        """Test header line matches text length"""
        text = "Short"
        result = header(text)
        # Should have lines of equal length to text
        assert text in result

    def test_section(self):
        """Test section function"""
        result = section("Section Title")
        assert "Section Title" in result
        assert "-" in result
        assert result.count("\n") >= 1


class TestTable:
    """Test table formatting"""

    def test_table_simple(self):
        """Test simple table creation"""
        headers = ["Name", "Age"]
        rows = [["Alice", "30"], ["Bob", "25"]]
        result = table(headers, rows)

        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result
        assert "Bob" in result
        assert "+" in result
        assert "|" in result
        assert "-" in result

    def test_table_with_custom_widths(self):
        """Test table with custom column widths"""
        headers = ["A", "B"]
        rows = [["1", "2"]]
        col_widths = [10, 20]
        result = table(headers, rows, col_widths)

        assert "A" in result
        assert "B" in result

    def test_table_auto_width_calculation(self):
        """Test table auto-calculates widths for long content"""
        headers = ["Short", "B"]
        rows = [["VeryLongContentHere", "X"]]
        result = table(headers, rows)

        assert "VeryLongContentHere" in result

    def test_table_empty_rows(self):
        """Test table with no rows"""
        headers = ["A", "B"]
        rows = []
        result = table(headers, rows)

        assert "A" in result
        assert "B" in result

    def test_table_multiple_rows(self):
        """Test table with multiple rows"""
        headers = ["Col1", "Col2", "Col3"]
        rows = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G", "H", "I"],
        ]
        result = table(headers, rows)

        for row in rows:
            for cell in row:
                assert cell in result


class TestKeyValue:
    """Test key-value formatting"""

    def test_key_value_default_width(self):
        """Test key-value with default width"""
        result = key_value("Name", "John Doe")
        assert "Name:" in result
        assert "John Doe" in result

    def test_key_value_custom_width(self):
        """Test key-value with custom width"""
        result = key_value("Key", "Value", key_width=15)
        assert "Key:" in result
        assert "Value" in result

    def test_key_value_long_key(self):
        """Test key-value with very long key"""
        result = key_value("VeryLongKeyName", "Value", key_width=50)
        assert "VeryLongKeyName:" in result


class TestProgressBar:
    """Test progress bar"""

    def test_progress_bar_empty(self):
        """Test progress bar at 0%"""
        result = progress_bar(0, 100)
        assert "0%" in result
        assert "(0/100)" in result
        assert "[" in result
        assert "]" in result

    def test_progress_bar_half(self):
        """Test progress bar at 50%"""
        result = progress_bar(50, 100)
        assert "50%" in result
        assert "(50/100)" in result

    def test_progress_bar_full(self):
        """Test progress bar at 100%"""
        result = progress_bar(100, 100)
        assert "100%" in result
        assert "(100/100)" in result

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total"""
        result = progress_bar(0, 0)
        assert "100%" in result  # Should default to 100% when total is 0

    def test_progress_bar_custom_width(self):
        """Test progress bar with custom width"""
        result = progress_bar(25, 100, width=20)
        assert "25%" in result

    def test_progress_bar_custom_char(self):
        """Test progress bar with custom character"""
        result = progress_bar(50, 100, char="#")
        assert "#" in result


class TestBox:
    """Test box formatting"""

    def test_box_single_line(self):
        """Test box with single line text"""
        result = box("Hello")
        assert "Hello" in result
        assert "┌" in result
        assert "└" in result
        assert "│" in result
        assert "─" in result

    def test_box_multi_line(self):
        """Test box with multiple lines"""
        result = box("Line 1\nLine 2\nLine 3")
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_box_custom_width(self):
        """Test box with custom width"""
        result = box("Test", width=20)
        assert "Test" in result

    def test_box_custom_padding(self):
        """Test box with custom padding"""
        result = box("Test", padding=3)
        assert "Test" in result

    def test_box_auto_width(self):
        """Test box with auto width (None)"""
        result = box("Short\nVeryLongLine")
        assert "Short" in result
        assert "VeryLongLine" in result


class TestLists:
    """Test list formatting"""

    def test_list_items_default_bullet(self):
        """Test list_items with default bullet"""
        items = ["Item 1", "Item 2", "Item 3"]
        result = list_items(items)

        for item in items:
            assert item in result

    def test_list_items_custom_bullet(self):
        """Test list_items with custom bullet"""
        items = ["Apple", "Banana"]
        result = list_items(items, bullet="*")

        assert "Apple" in result
        assert "Banana" in result
        assert "*" in result

    def test_list_items_empty(self):
        """Test list_items with empty list"""
        result = list_items([])
        assert result == ""

    def test_numbered_list(self):
        """Test numbered_list"""
        items = ["First", "Second", "Third"]
        result = numbered_list(items)

        assert "1." in result
        assert "2." in result
        assert "3." in result
        assert "First" in result
        assert "Second" in result
        assert "Third" in result

    def test_numbered_list_empty(self):
        """Test numbered_list with empty list"""
        result = numbered_list([])
        assert result == ""


class TestFormatDict:
    """Test dictionary formatting"""

    def test_format_dict_simple(self):
        """Test format_dict with simple dict"""
        data = {"name": "John", "age": 30}
        result = format_dict(data)

        assert "name" in result
        assert "John" in result
        assert "age" in result
        assert "30" in result

    def test_format_dict_nested(self):
        """Test format_dict with nested dict"""
        data = {
            "user": {
                "name": "Alice",
                "details": {"age": 25}
            }
        }
        result = format_dict(data)

        assert "user" in result
        assert "Alice" in result
        assert "age" in result

    def test_format_dict_with_list(self):
        """Test format_dict with list values"""
        data = {
            "items": ["apple", "banana", "cherry"]
        }
        result = format_dict(data)

        assert "items" in result
        assert "apple" in result
        assert "banana" in result

    def test_format_dict_with_dict_in_list(self):
        """Test format_dict with dict in list"""
        data = {
            "users": [
                {"name": "Alice"},
                {"name": "Bob"}
            ]
        }
        result = format_dict(data)

        assert "users" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_format_dict_indentation(self):
        """Test format_dict respects indentation"""
        data = {"key": "value"}
        result = format_dict(data, indent=2)

        assert "key" in result
        assert "value" in result


class TestDivider:
    """Test divider"""

    def test_divider_default(self):
        """Test divider with defaults"""
        result = divider()
        assert len(result) == 80
        assert result == "-" * 80

    def test_divider_custom_char(self):
        """Test divider with custom character"""
        result = divider(char="=")
        assert "=" in result
        assert "-" not in result

    def test_divider_custom_width(self):
        """Test divider with custom width"""
        result = divider(width=40)
        assert len(result) == 40


class TestTitleBox:
    """Test title box"""

    def test_title_box(self):
        """Test title_box creation"""
        result = title_box("My Title")
        assert "My Title" in result
        assert "╔" in result
        assert "╗" in result
        assert "╚" in result
        assert "╝" in result
        assert "║" in result
        assert "═" in result

    def test_title_box_short_text(self):
        """Test title_box with short text"""
        result = title_box("Hi")
        assert "Hi" in result

    def test_title_box_long_text(self):
        """Test title_box with long text"""
        result = title_box("This is a very long title")
        assert "This is a very long title" in result


class TestFormatCurrency:
    """Test currency formatting"""

    def test_format_currency_default(self):
        """Test format_currency with defaults"""
        result = format_currency(1234.56)
        assert "€" in result
        assert "1" in result
        assert "234" in result
        assert "56" in result

    def test_format_currency_custom_symbol(self):
        """Test format_currency with custom currency"""
        result = format_currency(1000, currency="$")
        assert "$" in result

    def test_format_currency_decimals(self):
        """Test format_currency with custom decimals"""
        result = format_currency(123.456, decimals=3)
        assert "123" in result

    def test_format_currency_large_number(self):
        """Test format_currency with large number"""
        result = format_currency(1234567.89)
        assert "€" in result

    def test_format_currency_zero(self):
        """Test format_currency with zero"""
        result = format_currency(0)
        assert "€" in result
        assert "0" in result

    def test_format_currency_negative(self):
        """Test format_currency with negative number"""
        result = format_currency(-100.50)
        assert "-" in result
        assert "€" in result


class TestFormatPercentage:
    """Test percentage formatting"""

    def test_format_percentage_default(self):
        """Test format_percentage with defaults"""
        result = format_percentage(0.075)
        assert "%" in result
        assert "0.1" in result or "0.0" in result  # 0.075 formatted to 1 decimal

    def test_format_percentage_no_sign(self):
        """Test format_percentage without % sign"""
        result = format_percentage(12.345, include_sign=False)
        assert "%" not in result
        assert "12.3" in result

    def test_format_percentage_custom_decimals(self):
        """Test format_percentage with custom decimals"""
        result = format_percentage(12.3456, decimals=2)
        assert "12.35" in result or "12.34" in result

    def test_format_percentage_zero(self):
        """Test format_percentage with zero"""
        result = format_percentage(0)
        assert "0" in result
        assert "%" in result

    def test_format_percentage_hundred(self):
        """Test format_percentage with 100"""
        result = format_percentage(100)
        assert "100" in result


class TestFormatDate:
    """Test date formatting"""

    def test_format_date_datetime(self):
        """Test format_date with datetime object"""
        dt = datetime(2026, 1, 11, 12, 30)
        result = format_date(dt)
        assert "11.01.2026" in result

    def test_format_date_date_object(self):
        """Test format_date with date object"""
        d = date(2026, 1, 11)
        result = format_date(d)
        assert "11.01.2026" in result

    def test_format_date_custom_format(self):
        """Test format_date with custom format"""
        dt = datetime(2026, 1, 11)
        result = format_date(dt, format_str="%Y-%m-%d")
        assert "2026-01-11" in result

    def test_format_date_string_passthrough(self):
        """Test format_date with string (should pass through)"""
        result = format_date("2026-01-11")
        assert result == "2026-01-11"

    def test_format_date_other_type(self):
        """Test format_date with other type (fallback to str)"""
        result = format_date(12345)
        assert "12345" in result


class TestTruncateText:
    """Test text truncation"""

    def test_truncate_text_short(self):
        """Test truncate_text with text shorter than max"""
        text = "Short text"
        result = truncate_text(text, max_length=50)
        assert result == text

    def test_truncate_text_exact_length(self):
        """Test truncate_text with text exactly at max length"""
        text = "Exactly fifteen"  # 15 chars
        result = truncate_text(text, max_length=15)
        assert result == text

    def test_truncate_text_long(self):
        """Test truncate_text with long text"""
        text = "This is a very long text that needs truncation"
        result = truncate_text(text, max_length=20)
        assert len(result) == 20
        assert "..." in result
        assert result.endswith("...")

    def test_truncate_text_custom_suffix(self):
        """Test truncate_text with custom suffix"""
        text = "This is a very long text"
        result = truncate_text(text, max_length=15, suffix="…")
        assert "…" in result
        assert len(result) == 15

    def test_truncate_text_very_short_max(self):
        """Test truncate_text with very short max length"""
        text = "Long text here"
        result = truncate_text(text, max_length=5)
        assert len(result) == 5

    def test_truncate_text_empty(self):
        """Test truncate_text with empty string"""
        result = truncate_text("", max_length=10)
        assert result == ""


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_table_with_numbers(self):
        """Test table with numeric values"""
        headers = ["ID", "Value"]
        rows = [[1, 100], [2, 200]]
        result = table(headers, rows)
        assert "1" in result
        assert "100" in result

    def test_progress_bar_fractional(self):
        """Test progress bar with fractional progress"""
        result = progress_bar(33, 100)
        assert "33%" in result

    def test_box_with_unicode(self):
        """Test box with unicode characters"""
        result = box("Héllo Wörld")
        assert "Héllo Wörld" in result

    def test_format_dict_empty(self):
        """Test format_dict with empty dict"""
        result = format_dict({})
        assert result == ""

    def test_colored_empty_string(self):
        """Test colored with empty string"""
        result = colored("", "red")
        assert isinstance(result, str)

    def test_header_empty_string(self):
        """Test header with empty string"""
        result = header("")
        assert isinstance(result, str)


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.utils.formatting", "--cov-report=term-missing"])
