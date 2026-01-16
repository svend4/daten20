"""
Tests for input validation module.
"""

from decimal import Decimal

import pytest

from src.core.input_validation import FlaskRequestValidator, InputValidator, ValidationError


class TestInputValidator:
    """Tests for InputValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()

    # String validation tests
    def test_validate_string_valid(self):
        """Test valid string validation."""
        result = self.validator.validate_string("Hello", min_length=1, max_length=10)
        assert result == "Hello"

    def test_validate_string_too_short(self):
        """Test string that's too short."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_string("Hi", min_length=5)
        assert "at least 5 characters" in str(exc_info.value)

    def test_validate_string_too_long(self):
        """Test string that's too long."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_string("Hello World!", max_length=5)
        assert "at most 5 characters" in str(exc_info.value)

    def test_validate_string_empty_not_allowed(self):
        """Test empty string when not allowed."""
        with pytest.raises(ValidationError):
            self.validator.validate_string("", min_length=1)

    def test_validate_string_pattern_match(self):
        """Test string pattern matching."""
        result = self.validator.validate_string("user123", pattern=r"^[a-z0-9]+$")
        assert result == "user123"

    def test_validate_string_pattern_no_match(self):
        """Test string pattern not matching."""
        with pytest.raises(ValidationError):
            self.validator.validate_string("user@123", pattern=r"^[a-z0-9]+$")

    # Integer validation tests
    def test_validate_integer_valid(self):
        """Test valid integer validation."""
        result = self.validator.validate_integer(42, min_value=0, max_value=100)
        assert result == 42

    def test_validate_integer_from_string(self):
        """Test integer validation from string."""
        result = self.validator.validate_integer("42", min_value=0, max_value=100)
        assert result == 42

    def test_validate_integer_too_small(self):
        """Test integer below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_integer(-5, min_value=0)
        assert "at least 0" in str(exc_info.value)

    def test_validate_integer_too_large(self):
        """Test integer above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_integer(150, max_value=100)
        assert "at most 100" in str(exc_info.value)

    def test_validate_integer_invalid_format(self):
        """Test invalid integer format."""
        with pytest.raises(ValidationError):
            self.validator.validate_integer("not_a_number")

    # Float validation tests
    def test_validate_float_valid(self):
        """Test valid float validation."""
        result = self.validator.validate_float(3.14, min_value=0.0, max_value=10.0)
        assert result == 3.14

    def test_validate_float_from_string(self):
        """Test float validation from string."""
        result = self.validator.validate_float("3.14", min_value=0.0)
        assert result == 3.14

    def test_validate_float_too_small(self):
        """Test float below minimum."""
        with pytest.raises(ValidationError):
            self.validator.validate_float(-5.0, min_value=0.0)

    def test_validate_float_too_large(self):
        """Test float above maximum."""
        with pytest.raises(ValidationError):
            self.validator.validate_float(150.0, max_value=100.0)

    # Decimal validation tests
    def test_validate_decimal_valid(self):
        """Test valid decimal validation."""
        result = self.validator.validate_decimal("19.99", min_value=Decimal("0"))
        assert result == Decimal("19.99")

    def test_validate_decimal_from_number(self):
        """Test decimal validation from number."""
        result = self.validator.validate_decimal(19.99)
        assert result == Decimal("19.99")

    def test_validate_decimal_too_small(self):
        """Test decimal below minimum."""
        with pytest.raises(ValidationError):
            self.validator.validate_decimal("-5.00", min_value=Decimal("0"))

    def test_validate_decimal_too_large(self):
        """Test decimal above maximum."""
        with pytest.raises(ValidationError):
            self.validator.validate_decimal("150.00", max_value=Decimal("100"))

    # Email validation tests
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "user+tag@example.com",
            "user_name@example-domain.com",
        ]
        for email in valid_emails:
            result = self.validator.validate_email(email)
            assert result == email

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = ["not_an_email", "@example.com", "user@", "user @example.com", "user@example"]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                self.validator.validate_email(email)

    # URL validation tests
    def test_validate_url_valid(self):
        """Test valid URLs."""
        valid_urls = ["https://example.com", "http://example.com/path", "https://sub.example.com:8080/path?query=value"]
        for url in valid_urls:
            result = self.validator.validate_url(url)
            assert result == url

    def test_validate_url_invalid_scheme(self):
        """Test URL with invalid scheme."""
        with pytest.raises(ValidationError):
            self.validator.validate_url("ftp://example.com", allowed_schemes=["http", "https"])

    def test_validate_url_invalid_format(self):
        """Test invalid URL format."""
        with pytest.raises(ValidationError):
            self.validator.validate_url("not a url")

    # Enum validation tests
    def test_validate_enum_valid(self):
        """Test valid enum value."""
        allowed = ["apple", "banana", "orange"]
        result = self.validator.validate_enum("apple", allowed)
        assert result == "apple"

    def test_validate_enum_invalid(self):
        """Test invalid enum value."""
        allowed = ["apple", "banana", "orange"]
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_enum("grape", allowed)
        assert "not one of allowed values" in str(exc_info.value)

    def test_validate_enum_case_insensitive(self):
        """Test case-insensitive enum validation."""
        allowed = ["Apple", "Banana", "Orange"]
        result = self.validator.validate_enum("apple", allowed, case_sensitive=False)
        assert result == "Apple"

    # File path validation tests
    def test_validate_file_path_safe(self):
        """Test safe file path."""
        result = self.validator.validate_file_path("documents/file.txt", base_directory="/home/user")
        assert result == "documents/file.txt"

    def test_validate_file_path_traversal_attempt(self):
        """Test path traversal attempt."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_file_path("../../etc/passwd")
        assert "Path traversal" in str(exc_info.value)

    def test_validate_file_path_invalid_extension(self):
        """Test file with invalid extension."""
        with pytest.raises(ValidationError):
            self.validator.validate_file_path("file.exe", allowed_extensions=[".txt", ".pdf", ".doc"])

    # XSS protection tests
    def test_sanitize_html_script_removed(self):
        """Test that script tags are removed."""
        result = self.validator.sanitize_html("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_sanitize_html_event_handlers_removed(self):
        """Test that event handlers are removed."""
        result = self.validator.sanitize_html("<div onclick='alert(1)'>Click</div>")
        assert "onclick" not in result
        assert "Click" in result

    def test_sanitize_html_javascript_urls_removed(self):
        """Test that javascript: URLs are removed."""
        result = self.validator.sanitize_html("<a href='javascript:alert(1)'>Link</a>")
        assert "javascript:" not in result

    # SQL injection detection tests
    def test_check_sql_injection_clean(self):
        """Test clean input (no SQL)."""
        result = self.validator.check_sql_injection("normal search query")
        assert result is False

    def test_check_sql_injection_detected(self):
        """Test SQL injection patterns detected."""
        sql_patterns = ["SELECT * FROM users", "DROP TABLE users", "'; DELETE FROM users--", "1' OR '1'='1"]
        for pattern in sql_patterns:
            result = self.validator.check_sql_injection(pattern)
            assert result is True, f"SQL injection not detected in: {pattern}"

    # Command injection detection tests
    def test_check_command_injection_clean(self):
        """Test clean input (no commands)."""
        result = self.validator.check_command_injection("normal filename.txt")
        assert result is False

    def test_check_command_injection_detected(self):
        """Test command injection patterns detected."""
        cmd_patterns = ["file.txt; rm -rf /", "file.txt | cat /etc/passwd", "file.txt && ls", "$(whoami)", "`id`"]
        for pattern in cmd_patterns:
            result = self.validator.check_command_injection(pattern)
            assert result is True, f"Command injection not detected in: {pattern}"

    # JSON validation tests
    def test_validate_json_valid(self):
        """Test valid JSON."""
        json_str = '{"name": "test", "value": 123}'
        result = self.validator.validate_json(json_str, max_depth=5)
        assert result["name"] == "test"
        assert result["value"] == 123

    def test_validate_json_invalid(self):
        """Test invalid JSON."""
        with pytest.raises(ValidationError):
            self.validator.validate_json('{"invalid": json}')

    def test_validate_json_too_deep(self):
        """Test JSON that exceeds max depth."""
        deep_json = '{"a": {"b": {"c": {"d": {"e": {"f": "too deep"}}}}}}'
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_json(deep_json, max_depth=3)
        assert "exceeds maximum depth" in str(exc_info.value)


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_exception_creation(self):
        """Test exception can be created."""
        exc = ValidationError("Test error")
        assert str(exc) == "Test error"

    def test_exception_raised(self):
        """Test exception can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Validation failed")
        assert "Validation failed" in str(exc_info.value)


class TestInputValidatorEdgeCases:
    """Tests for edge cases and corner cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()

    def test_validate_string_with_unicode(self):
        """Test string validation with Unicode characters."""
        result = self.validator.validate_string("Привет мир 🌍")
        assert result == "Привет мир 🌍"

    def test_validate_integer_zero(self):
        """Test integer validation with zero."""
        result = self.validator.validate_integer(0, min_value=0)
        assert result == 0

    def test_validate_decimal_very_small(self):
        """Test decimal validation with very small number."""
        result = self.validator.validate_decimal("0.0001")
        assert result == Decimal("0.0001")

    def test_validate_email_with_special_chars(self):
        """Test email with special but valid characters."""
        result = self.validator.validate_email("user+tag123@example.com")
        assert result == "user+tag123@example.com"

    def test_sanitize_html_preserves_safe_tags(self):
        """Test that sanitization preserves safe HTML."""
        result = self.validator.sanitize_html("<p>Safe <b>content</b></p>")
        assert "<p>" in result or "Safe" in result
        assert "content" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
