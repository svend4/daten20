"""
Примеры малых (small) тестов

Small тесты должны:
- Выполняться быстро (< 1 секунда)
- Не использовать I/O (файлы, БД, сеть)
- Не иметь внешних зависимостей
- Быть детерминированными
- Тестировать одну единицу кода
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Пометить весь модуль как small тесты
pytestmark = [pytest.mark.small, pytest.mark.unit]


class TestPasswordValidator:
    """Примеры small тестов для валидатора паролей"""

    def test_password_length_validation(self):
        """Test password length requirements - pure logic, no I/O"""
        from src.utils.validators import validate_password_length

        # Too short
        assert validate_password_length("123") is False

        # Minimum length
        assert validate_password_length("12345678") is True

        # Long password
        assert validate_password_length("a" * 50) is True

    def test_password_complexity(self):
        """Test password complexity requirements"""
        from src.utils.validators import validate_password_complexity

        # No uppercase
        assert validate_password_complexity("lowercase123!") is False

        # No lowercase
        assert validate_password_complexity("UPPERCASE123!") is False

        # No digits
        assert validate_password_complexity("LowerUpper!") is False

        # No special chars
        assert validate_password_complexity("LowerUpper123") is False

        # All requirements met
        assert validate_password_complexity("LowerUpper123!") is True

    def test_password_common_patterns(self):
        """Test detection of common password patterns"""
        from src.utils.validators import contains_common_pattern

        # Sequential numbers
        assert contains_common_pattern("12345678") is True

        # Keyboard patterns
        assert contains_common_pattern("qwerty123") is True

        # Common words
        assert contains_common_pattern("Password123!") is True

        # Random pattern
        assert contains_common_pattern("Xk9#mP2$qL") is False


class TestDocumentParser:
    """Примеры small тестов для парсера документов с моками"""

    def test_parse_metadata_from_bytes(self):
        """Test parsing metadata without file I/O"""
        from src.core.parser import DocumentParser

        # Mock document content
        mock_pdf_content = b'%PDF-1.7\n%%Title: Test Document\n%%Author: Test User'

        parser = DocumentParser()
        metadata = parser.parse_metadata_from_bytes(mock_pdf_content)

        assert metadata is not None
        assert metadata['format'] == 'PDF'
        assert metadata['version'] == '1.7'
        assert 'Test Document' in metadata.get('title', '')

    def test_detect_document_type(self):
        """Test document type detection from content"""
        from src.core.parser import DocumentParser

        parser = DocumentParser()

        # PDF signature
        assert parser.detect_type(b'%PDF-1.4') == 'PDF'

        # Word document signature
        assert parser.detect_type(b'PK\x03\x04') == 'DOCX'

        # Plain text
        assert parser.detect_type(b'This is plain text') == 'TXT'

        # Unknown format
        assert parser.detect_type(b'\x00\x00\x00\xFF') == 'UNKNOWN'

    @patch('src.core.parser.extract_text')
    def test_parse_with_mocked_extraction(self, mock_extract):
        """Test parser with mocked text extraction"""
        from src.core.parser import DocumentParser

        # Setup mock
        mock_extract.return_value = "Extracted text content"

        parser = DocumentParser()
        result = parser.parse_document(b'mock content')

        assert result['text'] == "Extracted text content"
        mock_extract.assert_called_once()


class TestTextUtils:
    """Примеры small тестов для утилит работы с текстом"""

    def test_clean_whitespace(self):
        """Test whitespace cleaning"""
        from src.utils.text import clean_whitespace

        # Multiple spaces
        assert clean_whitespace("hello  world") == "hello world"

        # Tabs
        assert clean_whitespace("hello\tworld") == "hello world"

        # Newlines
        assert clean_whitespace("hello\nworld") == "hello world"

        # Mixed
        assert clean_whitespace("  hello \t\n world  ") == "hello world"

    def test_truncate_text(self):
        """Test text truncation"""
        from src.utils.text import truncate_text

        text = "This is a long text that needs truncation"

        # Normal truncation
        result = truncate_text(text, max_length=20)
        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

        # No truncation needed
        result = truncate_text(text, max_length=100)
        assert result == text

        # Exact length
        result = truncate_text(text, max_length=len(text))
        assert result == text

    def test_extract_numbers(self):
        """Test number extraction from text"""
        from src.utils.text import extract_numbers

        # Single number
        assert extract_numbers("Price: 100") == [100]

        # Multiple numbers
        assert extract_numbers("2023-01-15") == [2023, 1, 15]

        # Decimal numbers
        assert extract_numbers("Total: 99.99") == [99.99]

        # No numbers
        assert extract_numbers("No numbers here") == []

    def test_count_words(self):
        """Test word counting"""
        from src.utils.text import count_words

        assert count_words("hello world") == 2
        assert count_words("hello  world") == 2  # Multiple spaces
        assert count_words("") == 0
        assert count_words("   ") == 0
        assert count_words("one") == 1


class TestDataValidation:
    """Примеры small тестов для валидации данных"""

    def test_email_validation(self):
        """Test email validation logic"""
        from src.utils.validators import is_valid_email

        # Valid emails
        assert is_valid_email("user@example.com") is True
        assert is_valid_email("user.name@example.co.uk") is True
        assert is_valid_email("user+tag@example.com") is True

        # Invalid emails
        assert is_valid_email("invalid") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("user@") is False
        assert is_valid_email("user @example.com") is False

    def test_phone_validation(self):
        """Test phone number validation"""
        from src.utils.validators import is_valid_phone

        # Valid formats
        assert is_valid_phone("+1234567890") is True
        assert is_valid_phone("+1-234-567-8900") is True
        assert is_valid_phone("(123) 456-7890") is True

        # Invalid formats
        assert is_valid_phone("123") is False
        assert is_valid_phone("abc123def") is False
        assert is_valid_phone("") is False

    def test_url_validation(self):
        """Test URL validation"""
        from src.utils.validators import is_valid_url

        # Valid URLs
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/path") is True
        assert is_valid_url("https://sub.example.com:8080/path?q=1") is True

        # Invalid URLs
        assert is_valid_url("not a url") is False
        assert is_valid_url("ftp://invalid") is False
        assert is_valid_url("") is False


class TestMathUtils:
    """Примеры small тестов для математических утилит"""

    def test_percentage_calculation(self):
        """Test percentage calculations"""
        from src.utils.math import calculate_percentage

        assert calculate_percentage(50, 100) == 50.0
        assert calculate_percentage(25, 100) == 25.0
        assert calculate_percentage(1, 3) == pytest.approx(33.33, rel=0.01)

        # Edge cases
        assert calculate_percentage(0, 100) == 0.0
        assert calculate_percentage(100, 100) == 100.0

        # Division by zero
        with pytest.raises(ValueError):
            calculate_percentage(50, 0)

    def test_round_to_decimal(self):
        """Test decimal rounding"""
        from src.utils.math import round_to_decimal

        assert round_to_decimal(3.14159, 2) == 3.14
        assert round_to_decimal(3.14159, 4) == 3.1416
        assert round_to_decimal(10, 2) == 10.0

    def test_clamp_value(self):
        """Test value clamping"""
        from src.utils.math import clamp

        # Within range
        assert clamp(5, 0, 10) == 5

        # Below minimum
        assert clamp(-5, 0, 10) == 0

        # Above maximum
        assert clamp(15, 0, 10) == 10

        # Edge cases
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10


class TestDateUtils:
    """Примеры small тестов для утилит работы с датами"""

    def test_is_business_day(self):
        """Test business day detection"""
        from datetime import datetime
        from src.utils.date import is_business_day

        # Monday (business day)
        monday = datetime(2024, 1, 1)  # Was a Monday
        assert is_business_day(monday) is True

        # Saturday (weekend)
        saturday = datetime(2024, 1, 6)
        assert is_business_day(saturday) is False

        # Sunday (weekend)
        sunday = datetime(2024, 1, 7)
        assert is_business_day(sunday) is False

    def test_days_between(self):
        """Test calculating days between dates"""
        from datetime import datetime
        from src.utils.date import days_between

        date1 = datetime(2024, 1, 1)
        date2 = datetime(2024, 1, 10)

        assert days_between(date1, date2) == 9

        # Same date
        assert days_between(date1, date1) == 0

        # Reversed order
        assert days_between(date2, date1) == -9


# Пример теста с параметризацией для small тестов
@pytest.mark.parametrize("input_value,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("MixedCase", "MIXEDCASE"),
    ("with spaces", "WITH SPACES"),
])
def test_uppercase_conversion(input_value, expected):
    """Test uppercase conversion with multiple inputs"""
    assert input_value.upper() == expected


@pytest.mark.parametrize("a,b,expected_sum", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
    (-5, -3, -8),
])
def test_addition(a, b, expected_sum):
    """Test basic addition"""
    assert a + b == expected_sum
