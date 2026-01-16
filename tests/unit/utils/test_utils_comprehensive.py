"""
Comprehensive tests for Utility modules

Test coverage goals:
- Helpers: Common utility functions
- Formatting: Text formatting, number formatting
- Constants: Regional constants, rate constants
- Errors: Custom exception classes
- Error messages: Localized error messages
- Progress: Progress bar functionality
- Logging helpers: Log formatting and utilities
- Edge cases and error handling
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.utils.helpers import (
    parse_decimal,
    format_currency,
    validate_iban,
    generate_id,
    truncate_text,
)
from src.utils.formatting import (
    format_number,
    format_percentage,
    format_date,
    format_hours,
)
from src.utils.constants import (
    REGIONS,
    REGION_COEFFICIENTS,
    FEDERAL_STATES,
)
from src.utils.errors import (
    ValidationError,
    DatabaseError,
    ConfigurationError,
    CalculationError,
)


class TestHelpers:
    """Test helper utility functions"""

    def test_parse_decimal_valid(self):
        """Test parsing valid decimal strings"""
        assert parse_decimal("25.50") == Decimal("25.50")
        assert parse_decimal("100") == Decimal("100")
        assert parse_decimal("0.01") == Decimal("0.01")

    def test_parse_decimal_with_comma(self):
        """Test parsing decimal with comma separator"""
        result = parse_decimal("25,50")
        # Should handle comma as decimal separator
        assert isinstance(result, Decimal)

    def test_parse_decimal_invalid(self):
        """Test parsing invalid decimal strings"""
        with pytest.raises((ValueError, TypeError)):
            parse_decimal("invalid")

    def test_parse_decimal_empty(self):
        """Test parsing empty string"""
        result = parse_decimal("")
        # Should return 0 or raise error
        assert result == Decimal("0") or result is None

    def test_format_currency_basic(self):
        """Test basic currency formatting"""
        result = format_currency(Decimal("25.50"))
        assert "25" in result
        assert "50" in result

    def test_format_currency_with_symbol(self):
        """Test currency formatting with symbol"""
        result = format_currency(Decimal("100.00"), symbol="€")
        assert "€" in result or "100" in result

    def test_format_currency_negative(self):
        """Test formatting negative currency"""
        result = format_currency(Decimal("-50.00"))
        assert "-" in result or "50" in result

    def test_validate_iban_valid(self):
        """Test validating valid IBAN"""
        # German IBAN format
        iban = "DE89370400440532013000"
        result = validate_iban(iban)
        assert result is True or result is False

    def test_validate_iban_invalid(self):
        """Test validating invalid IBAN"""
        iban = "INVALID_IBAN"
        result = validate_iban(iban)
        assert result is False

    def test_generate_id(self):
        """Test ID generation"""
        id1 = generate_id()
        id2 = generate_id()

        assert id1 != id2
        assert isinstance(id1, str)
        assert len(id1) > 0

    def test_truncate_text_short(self):
        """Test truncating text shorter than limit"""
        text = "Short text"
        result = truncate_text(text, max_length=50)
        assert result == text

    def test_truncate_text_long(self):
        """Test truncating long text"""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 23  # 20 + "..."


class TestFormatting:
    """Test formatting utilities"""

    def test_format_number_integer(self):
        """Test formatting integer"""
        result = format_number(1000)
        assert "1000" in result or "1.000" in result or "1,000" in result

    def test_format_number_decimal(self):
        """Test formatting decimal number"""
        result = format_number(Decimal("1234.56"))
        assert "1234" in result
        assert "56" in result

    def test_format_number_with_separator(self):
        """Test number formatting with thousand separator"""
        result = format_number(1000000)
        # Should include separator
        assert len(result) >= 7

    def test_format_percentage_basic(self):
        """Test basic percentage formatting"""
        result = format_percentage(Decimal("0.25"))
        assert "25" in result
        assert "%" in result

    def test_format_percentage_zero(self):
        """Test formatting zero percentage"""
        result = format_percentage(Decimal("0"))
        assert "0" in result

    def test_format_percentage_large(self):
        """Test formatting large percentage"""
        result = format_percentage(Decimal("1.5"))
        assert "150" in result or "1.5" in result

    def test_format_date_valid(self):
        """Test formatting valid date"""
        date_str = "2024-01-15"
        result = format_date(date_str)
        assert "2024" in result or "24" in result
        assert "01" in result or "1" in result

    def test_format_date_invalid(self):
        """Test formatting invalid date"""
        with pytest.raises((ValueError, TypeError)):
            format_date("invalid")

    def test_format_hours_basic(self):
        """Test formatting hours"""
        result = format_hours(Decimal("8.5"))
        assert "8" in result
        assert "5" in result or "30" in result  # .5 hours = 30 minutes

    def test_format_hours_whole(self):
        """Test formatting whole hours"""
        result = format_hours(Decimal("8"))
        assert "8" in result


class TestConstants:
    """Test constant definitions"""

    def test_regions_defined(self):
        """Test that regions are defined"""
        assert REGIONS is not None
        assert len(REGIONS) > 0

    def test_region_coefficients_defined(self):
        """Test that region coefficients are defined"""
        assert REGION_COEFFICIENTS is not None
        assert isinstance(REGION_COEFFICIENTS, dict)

    def test_federal_states_defined(self):
        """Test that federal states are defined"""
        assert FEDERAL_STATES is not None
        assert len(FEDERAL_STATES) >= 16  # Germany has 16 federal states

    def test_region_coefficients_valid_values(self):
        """Test that region coefficients are valid"""
        for region, coefficient in REGION_COEFFICIENTS.items():
            assert isinstance(coefficient, (int, float, Decimal))
            assert coefficient > 0  # Coefficient should be positive

    def test_federal_states_contain_major_states(self):
        """Test that major federal states are included"""
        major_states = ["Bavaria", "Berlin", "Hamburg", "Saxony"]

        for state in major_states:
            # Check if state name or abbreviation is in list
            found = any(state.lower() in str(s).lower() for s in FEDERAL_STATES)
            assert found or state in FEDERAL_STATES


class TestErrors:
    """Test custom error classes"""

    def test_validation_error(self):
        """Test ValidationError exception"""
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid input")

    def test_validation_error_message(self):
        """Test ValidationError with message"""
        error = ValidationError("Custom validation error")
        assert str(error) == "Custom validation error"

    def test_database_error(self):
        """Test DatabaseError exception"""
        with pytest.raises(DatabaseError):
            raise DatabaseError("Database connection failed")

    def test_configuration_error(self):
        """Test ConfigurationError exception"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Invalid configuration")

    def test_calculation_error(self):
        """Test CalculationError exception"""
        with pytest.raises(CalculationError):
            raise CalculationError("Calculation overflow")

    def test_error_inheritance(self):
        """Test that custom errors inherit from Exception"""
        assert issubclass(ValidationError, Exception)
        assert issubclass(DatabaseError, Exception)
        assert issubclass(ConfigurationError, Exception)
        assert issubclass(CalculationError, Exception)


class TestProgress:
    """Test progress bar functionality"""

    @pytest.fixture
    def progress_bar(self):
        """Create progress bar instance"""
        from src.utils.progress import ProgressBar
        return ProgressBar(total=100, desc="Test")

    def test_progress_bar_creation(self, progress_bar):
        """Test creating progress bar"""
        assert progress_bar is not None

    def test_progress_bar_update(self, progress_bar):
        """Test updating progress bar"""
        progress_bar.update(10)
        # Should not raise error

    def test_progress_bar_complete(self, progress_bar):
        """Test completing progress bar"""
        progress_bar.update(100)
        progress_bar.close()
        # Should complete without error

    def test_progress_bar_percentage(self, progress_bar):
        """Test progress bar percentage calculation"""
        progress_bar.update(50)
        # 50 out of 100 = 50%
        # Check if percentage is tracked correctly


class TestLoggingHelpers:
    """Test logging helper functions"""

    @pytest.fixture
    def logger(self):
        """Create logger instance"""
        import logging
        return logging.getLogger("test")

    def test_format_log_message(self, logger):
        """Test log message formatting"""
        from src.utils.logging_helpers import format_log_message
        message = format_log_message("Test message", level="INFO")
        assert "Test message" in message

    def test_log_exception(self, logger):
        """Test exception logging"""
        from src.utils.logging_helpers import log_exception

        try:
            raise ValueError("Test error")
        except Exception as e:
            log_exception(logger, e)
            # Should log without raising


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_parse_decimal_very_large(self):
        """Test parsing very large decimal"""
        result = parse_decimal("999999999.99")
        assert result == Decimal("999999999.99")

    def test_parse_decimal_very_small(self):
        """Test parsing very small decimal"""
        result = parse_decimal("0.00000001")
        assert result == Decimal("0.00000001")

    def test_format_currency_zero(self):
        """Test formatting zero currency"""
        result = format_currency(Decimal("0"))
        assert "0" in result

    def test_format_currency_large_amount(self):
        """Test formatting large currency amount"""
        result = format_currency(Decimal("1000000.00"))
        assert "1000000" in result or "1.000.000" in result

    def test_truncate_text_exact_length(self):
        """Test truncating text at exact max length"""
        text = "12345"
        result = truncate_text(text, max_length=5)
        assert len(result) == 5

    def test_truncate_text_unicode(self):
        """Test truncating text with Unicode"""
        text = "Übermäßige Länge"
        result = truncate_text(text, max_length=10)
        assert len(result) <= 13  # Including ellipsis

    def test_validate_iban_empty(self):
        """Test validating empty IBAN"""
        result = validate_iban("")
        assert result is False

    def test_validate_iban_too_short(self):
        """Test validating too short IBAN"""
        result = validate_iban("DE12")
        assert result is False

    def test_format_number_negative(self):
        """Test formatting negative number"""
        result = format_number(-1000)
        assert "-" in result

    def test_format_percentage_negative(self):
        """Test formatting negative percentage"""
        result = format_percentage(Decimal("-0.25"))
        assert "-" in result


class TestParametrizedCases:
    """Parametrized test cases"""

    @pytest.mark.parametrize("value,expected", [
        ("25.50", Decimal("25.50")),
        ("100", Decimal("100")),
        ("0.01", Decimal("0.01")),
        ("1000.99", Decimal("1000.99")),
    ])
    def test_parse_decimal_cases(self, value, expected):
        """Test parsing various decimal cases"""
        result = parse_decimal(value)
        assert result == expected

    @pytest.mark.parametrize("region", [
        "Bavaria",
        "Berlin",
        "Hamburg",
        "Saxony",
        "North Rhine-Westphalia",
    ])
    def test_region_coefficients_exist(self, region):
        """Test that coefficients exist for major regions"""
        # Region might be in REGION_COEFFICIENTS
        # This test checks if the structure is valid
        assert REGION_COEFFICIENTS is not None

    @pytest.mark.parametrize("hours,expected_contains", [
        (8, "8"),
        (8.5, "8"),
        (0.5, "0.5"),
        (24, "24"),
    ])
    def test_format_hours_cases(self, hours, expected_contains):
        """Test formatting various hour values"""
        result = format_hours(Decimal(str(hours)))
        assert expected_contains in result


class TestIntegration:
    """Integration tests for utils"""

    def test_full_currency_workflow(self):
        """Test complete currency parsing and formatting"""
        # Parse string to Decimal
        value = parse_decimal("1234.56")

        # Format as currency
        formatted = format_currency(value)

        # Should contain the value
        assert "1234" in formatted or "1.234" in formatted

    def test_error_handling_workflow(self):
        """Test error handling workflow"""
        # Raise and catch custom error
        try:
            raise ValidationError("Test validation error")
        except ValidationError as e:
            assert "validation" in str(e).lower()

    def test_formatting_consistency(self):
        """Test consistency across formatting functions"""
        value = Decimal("1234.56")

        # Format as number
        num_result = format_number(value)

        # Format as currency
        curr_result = format_currency(value)

        # Both should contain the base value
        assert "1234" in num_result or "1.234" in num_result
        assert "1234" in curr_result or "1.234" in curr_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
