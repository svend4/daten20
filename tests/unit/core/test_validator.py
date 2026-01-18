"""
Comprehensive tests for src/core/validator.py

Tests all validation functionality including:
- ValidationRule class
- EnhancedValidator class (40+ validation methods)
- TemplateValidator class
"""

import pytest
import re
from decimal import Decimal
from typing import Any, Dict
from unittest.mock import Mock, patch

from src.core.validator import ValidationRule, EnhancedValidator, TemplateValidator
from src.models.template import Variable, ValidationResult


class TestValidationRule:
    """Tests for ValidationRule class"""

    def test_initialization(self):
        """Test ValidationRule initialization"""
        rule = ValidationRule(
            field="email",
            validator=lambda x: "@" in x,
            error_message="Must contain @",
            severity="error"
        )

        assert rule.field == "email"
        assert rule.error_message == "Must contain @"
        assert rule.severity == "error"

    def test_validate_success(self):
        """Test successful validation"""
        rule = ValidationRule(
            field="age",
            validator=lambda x: x >= 18,
            error_message="Must be 18 or older"
        )

        is_valid, error = rule.validate(25)
        assert is_valid is True
        assert error is None

    def test_validate_failure(self):
        """Test failed validation"""
        rule = ValidationRule(
            field="age",
            validator=lambda x: x >= 18,
            error_message="Must be 18 or older"
        )

        is_valid, error = rule.validate(15)
        assert is_valid is False
        assert error == "Must be 18 or older"

    def test_validate_exception(self):
        """Test validation with exception"""
        rule = ValidationRule(
            field="number",
            validator=lambda x: int(x) > 0,
            error_message="Must be positive"
        )

        is_valid, error = rule.validate("invalid")
        assert is_valid is False
        assert "Exception" in error

    def test_warning_severity(self):
        """Test warning severity"""
        rule = ValidationRule(
            field="test",
            validator=lambda x: True,
            error_message="Warning message",
            severity="warning"
        )

        assert rule.severity == "warning"


class TestEnhancedValidator:
    """Tests for EnhancedValidator class"""

    def setup_method(self):
        """Setup test fixture"""
        self.validator = EnhancedValidator()

    # URL validation tests
    def test_validate_url_valid(self):
        """Test valid URLs"""
        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "https://sub.domain.example.com",
            "http://localhost",
            "http://192.168.1.1",
            "https://example.com:8080",
            "https://example.com/path/to/page",
            "https://example.com/path?query=value",
        ]

        for url in valid_urls:
            assert self.validator.validate_url(url) is True, f"Failed for {url}"

    def test_validate_url_invalid(self):
        """Test invalid URLs"""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com",  # Not http/https
            "example.com",  # Missing protocol
            "http://",  # Incomplete
        ]

        for url in invalid_urls:
            assert self.validator.validate_url(url) is False, f"Should fail for {url}"

    # IBAN validation tests
    def test_validate_iban_valid(self):
        """Test valid IBANs"""
        valid_ibans = [
            "DE89370400440532013000",
            "GB82WEST12345698765432",
            "FR1420041010050500013M02606",
            "IT60X0542811101000000123456",
        ]

        for iban in valid_ibans:
            assert self.validator.validate_iban(iban) is True, f"Failed for {iban}"

    def test_validate_iban_with_spaces(self):
        """Test IBAN with spaces (should be removed)"""
        iban = "DE89 3704 0044 0532 0130 00"
        assert self.validator.validate_iban(iban) is True

    def test_validate_iban_invalid(self):
        """Test invalid IBANs"""
        invalid_ibans = [
            "",
            "12345",
            "INVALID",
            "DE1234",  # Too short
        ]

        for iban in invalid_ibans:
            assert self.validator.validate_iban(iban) is False, f"Should fail for {iban}"

    # BIC validation tests
    def test_validate_bic_valid(self):
        """Test valid BIC codes"""
        valid_bics = [
            "DEUTDEFF",
            "DEUTDEFFXXX",
            "COBADEFF",
            "COBADEFFXXX",
        ]

        for bic in valid_bics:
            assert self.validator.validate_bic(bic) is True, f"Failed for {bic}"

    def test_validate_bic_invalid(self):
        """Test invalid BIC codes"""
        invalid_bics = [
            "",
            "INVALID",
            "12345678",
            "DEUT",  # Too short
        ]

        for bic in invalid_bics:
            assert self.validator.validate_bic(bic) is False, f"Should fail for {bic}"

    # Postal code validation tests
    def test_validate_postal_code_de(self):
        """Test German postal codes"""
        assert self.validator.validate_postal_code("10115", "DE") is True
        assert self.validator.validate_postal_code("80331", "DE") is True
        assert self.validator.validate_postal_code("12345", "DE") is True
        assert self.validator.validate_postal_code("1234", "DE") is False
        assert self.validator.validate_postal_code("123456", "DE") is False

    def test_validate_postal_code_general(self):
        """Test general postal codes"""
        assert self.validator.validate_postal_code("SW1A 1AA", "UK") is True
        assert self.validator.validate_postal_code("75001", "FR") is True

    # IP address validation tests
    def test_validate_ip_address_v4(self):
        """Test IPv4 addresses"""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "127.0.0.1",
            "255.255.255.255",
        ]

        for ip in valid_ips:
            assert self.validator.validate_ip_address(ip, version=4) is True

    def test_validate_ip_address_v4_invalid(self):
        """Test invalid IPv4 addresses"""
        invalid_ips = [
            "",
            "256.256.256.256",
            "192.168.1",
            "invalid",
        ]

        for ip in invalid_ips:
            assert self.validator.validate_ip_address(ip, version=4) is False

    def test_validate_ip_address_v6(self):
        """Test IPv6 addresses"""
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "::1",
            "fe80::1",
        ]

        for ip in valid_ips:
            assert self.validator.validate_ip_address(ip, version=6) is True

    # UUID validation tests
    def test_validate_uuid_valid(self):
        """Test valid UUIDs"""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "123e4567-e89b-12d3-a456-426614174000",
        ]

        for uuid in valid_uuids:
            assert self.validator.validate_uuid(uuid) is True

    def test_validate_uuid_invalid(self):
        """Test invalid UUIDs"""
        invalid_uuids = [
            "",
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
        ]

        for uuid in invalid_uuids:
            assert self.validator.validate_uuid(uuid) is False

    # Hex color validation tests
    def test_validate_hex_color_valid(self):
        """Test valid hex color codes"""
        valid_colors = [
            "#FFFFFF",
            "#000000",
            "#FF5733",
            "FFFFFF",  # Without #
            "#FFF",  # Short form
            "ABC",  # Short form without #
        ]

        for color in valid_colors:
            assert self.validator.validate_hex_color(color) is True

    def test_validate_hex_color_invalid(self):
        """Test invalid hex color codes"""
        invalid_colors = [
            "",
            "#GGGGGG",
            "#12",  # Too short
            "#1234567",  # Too long
            "invalid",
        ]

        for color in invalid_colors:
            assert self.validator.validate_hex_color(color) is False

    # Credit card validation tests
    def test_validate_credit_card_valid(self):
        """Test valid credit card numbers (using Luhn algorithm)"""
        # Valid test cards
        valid_cards = [
            "4532015112830366",  # Visa
            "5425233430109903",  # Mastercard
            "374245455400126",   # Amex
            "6011111111111117",  # Discover
        ]

        for card in valid_cards:
            assert self.validator.validate_credit_card(card) is True, f"Failed for {card}"

    def test_validate_credit_card_with_spaces(self):
        """Test credit card with spaces"""
        card = "4532 0151 1283 0366"
        assert self.validator.validate_credit_card(card) is True

    def test_validate_credit_card_invalid(self):
        """Test invalid credit card numbers"""
        invalid_cards = [
            "",
            "1234567890123456",  # Fails Luhn check
            "123",  # Too short
            "12345678901234567890",  # Too long
        ]

        for card in invalid_cards:
            assert self.validator.validate_credit_card(card) is False

    # Tax ID validation tests
    def test_validate_tax_id_de(self):
        """Test German tax ID"""
        assert self.validator.validate_tax_id("12345678901", "DE") is True
        assert self.validator.validate_tax_id("1234567890", "DE") is False  # Too short
        assert self.validator.validate_tax_id("", "DE") is False

    # VAT ID validation tests
    def test_validate_vat_id_de(self):
        """Test German VAT ID"""
        assert self.validator.validate_vat_id("DE123456789", "DE") is True
        assert self.validator.validate_vat_id("DE12345678", "DE") is False  # Too short
        assert self.validator.validate_vat_id("", "DE") is False

    # MAC address validation tests
    def test_validate_mac_address_valid(self):
        """Test valid MAC addresses"""
        valid_macs = [
            "00:1B:44:11:3A:B7",
            "00-1B-44-11-3A-B7",
            "AA:BB:CC:DD:EE:FF",
        ]

        for mac in valid_macs:
            assert self.validator.validate_mac_address(mac) is True

    def test_validate_mac_address_invalid(self):
        """Test invalid MAC addresses"""
        invalid_macs = [
            "",
            "00:1B:44:11:3A",  # Too short
            "00:1B:44:11:3A:B7:FF",  # Too long
            "GG:HH:II:JJ:KK:LL",  # Invalid hex
        ]

        for mac in invalid_macs:
            assert self.validator.validate_mac_address(mac) is False

    # SSN validation tests
    def test_validate_ssn_us(self):
        """Test US Social Security Numbers"""
        assert self.validator.validate_ssn("123-45-6789", "US") is True
        assert self.validator.validate_ssn("123456789", "US") is False  # Missing dashes
        assert self.validator.validate_ssn("", "US") is False

    # ISBN validation tests
    def test_validate_isbn10_valid(self):
        """Test valid ISBN-10"""
        # ISBN-10 with valid checksums
        assert self.validator.validate_isbn("0306406152") is True
        assert self.validator.validate_isbn("0-306-40615-2") is True  # With dashes

    def test_validate_isbn13_valid(self):
        """Test valid ISBN-13"""
        # ISBN-13 with valid checksums
        assert self.validator.validate_isbn("9780306406157") is True
        assert self.validator.validate_isbn("978-0-306-40615-7") is True  # With dashes

    def test_validate_isbn_invalid(self):
        """Test invalid ISBNs"""
        invalid_isbns = [
            "",
            "1234567890",  # Wrong checksum
            "123",  # Too short
            "invalid",
        ]

        for isbn in invalid_isbns:
            assert self.validator.validate_isbn(isbn) is False

    # EAN validation tests
    def test_validate_ean_valid(self):
        """Test valid EAN-13"""
        # Valid EAN-13 barcodes
        valid_eans = [
            "5901234123457",
            "4006381333931",
        ]

        for ean in valid_eans:
            assert self.validator.validate_ean(ean) is True

    def test_validate_ean_invalid(self):
        """Test invalid EAN-13"""
        invalid_eans = [
            "",
            "123456789012",  # Wrong length
            "5901234123456",  # Wrong checksum
        ]

        for ean in invalid_eans:
            assert self.validator.validate_ean(ean) is False

    # VIN validation tests
    def test_validate_vin_valid(self):
        """Test valid VINs"""
        valid_vins = [
            "1HGBH41JXMN109186",
            "5YJSA1E14HF000001",
        ]

        for vin in valid_vins:
            assert self.validator.validate_vin(vin) is True

    def test_validate_vin_invalid(self):
        """Test invalid VINs"""
        invalid_vins = [
            "",
            "1HGBH41JXMN10918",  # Too short
            "1HGBH41JXMN1091866",  # Too long
            "1HGBH41JXIN109186",  # Contains I
            "1HGBH41JXON109186",  # Contains O
            "1HGBH41JXQN109186",  # Contains Q
        ]

        for vin in invalid_vins:
            assert self.validator.validate_vin(vin) is False

    # Bitcoin address validation tests
    def test_validate_bitcoin_address_valid(self):
        """Test valid Bitcoin addresses"""
        valid_addresses = [
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy",
        ]

        for addr in valid_addresses:
            assert self.validator.validate_bitcoin_address(addr) is True

    def test_validate_bitcoin_address_invalid(self):
        """Test invalid Bitcoin addresses"""
        invalid_addresses = [
            "",
            "invalid",
            "0A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Starts with 0
        ]

        for addr in invalid_addresses:
            assert self.validator.validate_bitcoin_address(addr) is False

    # Ethereum address validation tests
    def test_validate_ethereum_address_valid(self):
        """Test valid Ethereum addresses"""
        valid_addresses = [
            "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
            "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        ]

        for addr in valid_addresses:
            assert self.validator.validate_ethereum_address(addr) is True

    def test_validate_ethereum_address_invalid(self):
        """Test invalid Ethereum addresses"""
        invalid_addresses = [
            "",
            "invalid",
            "5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",  # Missing 0x
            "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeA",  # Too short
        ]

        for addr in invalid_addresses:
            assert self.validator.validate_ethereum_address(addr) is False

    # Coordinates validation tests
    def test_validate_coordinates_valid(self):
        """Test valid coordinates"""
        is_valid, error = self.validator.validate_coordinates("52.5200", "13.4050")
        assert is_valid is True
        assert error is None

    def test_validate_coordinates_invalid_latitude(self):
        """Test invalid latitude"""
        is_valid, error = self.validator.validate_coordinates("91", "13.4050")
        assert is_valid is False
        assert "latitude" in error.lower()

    def test_validate_coordinates_invalid_longitude(self):
        """Test invalid longitude"""
        is_valid, error = self.validator.validate_coordinates("52.5200", "181")
        assert is_valid is False
        assert "longitude" in error.lower()

    def test_validate_coordinates_missing(self):
        """Test missing coordinates"""
        is_valid, error = self.validator.validate_coordinates("", "13.4050")
        assert is_valid is False
        assert "required" in error.lower()

    # Passport validation tests
    def test_validate_passport_de(self):
        """Test German passport numbers"""
        assert self.validator.validate_passport("C01X00T47", "DE") is True
        assert self.validator.validate_passport("", "DE") is False
        assert self.validator.validate_passport("123456789", "DE") is False  # Wrong format

    # License plate validation tests
    def test_validate_license_plate_de(self):
        """Test German license plates"""
        valid_plates = [
            "B-AB 1234",
            "M-A 123",
            "HH-XY 9999",
        ]

        for plate in valid_plates:
            assert self.validator.validate_license_plate(plate, "DE") is True

    def test_validate_license_plate_de_invalid(self):
        """Test invalid German license plates"""
        invalid_plates = [
            "",
            "123-ABC-456",
            "INVALID",
        ]

        for plate in invalid_plates:
            assert self.validator.validate_license_plate(plate, "DE") is False

    # File path validation tests
    def test_validate_file_path_valid(self):
        """Test valid file paths"""
        is_valid, error = self.validator.validate_file_path("/path/to/file.txt")
        assert is_valid is True
        assert error is None

    def test_validate_file_path_empty(self):
        """Test empty file path"""
        is_valid, error = self.validator.validate_file_path("")
        assert is_valid is False
        assert "cannot be empty" in error.lower()

    def test_validate_file_path_invalid_chars(self):
        """Test file path with invalid characters"""
        is_valid, error = self.validator.validate_file_path("path/with<invalid>chars")
        assert is_valid is False
        assert "invalid characters" in error.lower()

    @patch('pathlib.Path.exists')
    def test_validate_file_path_must_exist_true(self, mock_exists):
        """Test file path that must exist (exists)"""
        mock_exists.return_value = True
        is_valid, error = self.validator.validate_file_path("/path/to/file.txt", must_exist=True)
        assert is_valid is True
        assert error is None

    @patch('pathlib.Path.exists')
    def test_validate_file_path_must_exist_false(self, mock_exists):
        """Test file path that must exist (doesn't exist)"""
        mock_exists.return_value = False
        is_valid, error = self.validator.validate_file_path("/path/to/file.txt", must_exist=True)
        assert is_valid is False
        assert "does not exist" in error.lower()

    # Domain validation tests
    def test_validate_domain_valid(self):
        """Test valid domain names"""
        valid_domains = [
            "example.com",
            "sub.example.com",
            "my-domain.co.uk",
        ]

        for domain in valid_domains:
            assert self.validator.validate_domain(domain) is True

    def test_validate_domain_invalid(self):
        """Test invalid domain names"""
        invalid_domains = [
            "",
            "invalid",
            "-example.com",
            "example",
        ]

        for domain in invalid_domains:
            assert self.validator.validate_domain(domain) is False

    # JSON validation tests
    def test_validate_json_valid(self):
        """Test valid JSON"""
        is_valid, error = self.validator.validate_json('{"key": "value"}')
        assert is_valid is True
        assert error is None

    def test_validate_json_invalid(self):
        """Test invalid JSON"""
        is_valid, error = self.validator.validate_json('{invalid json}')
        assert is_valid is False
        assert "Invalid JSON" in error

    def test_validate_json_empty(self):
        """Test empty JSON"""
        is_valid, error = self.validator.validate_json("")
        assert is_valid is False
        assert "cannot be empty" in error.lower()

    # Age validation tests
    def test_validate_age_valid(self):
        """Test valid ages"""
        is_valid, error = self.validator.validate_age(25)
        assert is_valid is True
        assert error is None

    def test_validate_age_too_young(self):
        """Test age too young"""
        is_valid, error = self.validator.validate_age(-5)
        assert is_valid is False
        assert "at least" in error.lower()

    def test_validate_age_too_old(self):
        """Test age too old"""
        is_valid, error = self.validator.validate_age(200)
        assert is_valid is False
        assert "at most" in error.lower()

    def test_validate_age_custom_range(self):
        """Test age with custom range"""
        is_valid, error = self.validator.validate_age(15, min_age=18, max_age=65)
        assert is_valid is False
        assert "at least 18" in error.lower()

    def test_validate_age_invalid_type(self):
        """Test invalid age type"""
        is_valid, error = self.validator.validate_age("invalid")
        assert is_valid is False
        assert "valid number" in error.lower()

    # Username validation tests
    def test_validate_username_valid(self):
        """Test valid usernames"""
        is_valid, error = self.validator.validate_username("john_doe")
        assert is_valid is True
        assert error is None

    def test_validate_username_too_short(self):
        """Test username too short"""
        is_valid, error = self.validator.validate_username("ab")
        assert is_valid is False
        assert "at least" in error.lower()

    def test_validate_username_too_long(self):
        """Test username too long"""
        is_valid, error = self.validator.validate_username("a" * 21)
        assert is_valid is False
        assert "at most" in error.lower()

    def test_validate_username_invalid_chars(self):
        """Test username with invalid characters"""
        is_valid, error = self.validator.validate_username("john@doe")
        assert is_valid is False
        assert "can only contain" in error.lower()

    def test_validate_username_with_special_allowed(self):
        """Test username with special characters allowed"""
        is_valid, error = self.validator.validate_username("john.doe-123", allow_special=True)
        assert is_valid is True
        assert error is None

    # Password strength validation tests
    def test_validate_password_strength_strong(self):
        """Test strong password"""
        is_valid, issues = self.validator.validate_password_strength("Passw0rd!")
        assert is_valid is True
        assert len(issues) == 0

    def test_validate_password_strength_too_short(self):
        """Test password too short"""
        is_valid, issues = self.validator.validate_password_strength("Pass1!")
        assert is_valid is False
        assert any("at least" in issue for issue in issues)

    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase"""
        is_valid, issues = self.validator.validate_password_strength("password123!")
        assert is_valid is False
        assert any("uppercase" in issue for issue in issues)

    def test_validate_password_strength_no_lowercase(self):
        """Test password without lowercase"""
        is_valid, issues = self.validator.validate_password_strength("PASSWORD123!")
        assert is_valid is False
        assert any("lowercase" in issue for issue in issues)

    def test_validate_password_strength_no_digit(self):
        """Test password without digit"""
        is_valid, issues = self.validator.validate_password_strength("Password!")
        assert is_valid is False
        assert any("digit" in issue for issue in issues)

    def test_validate_password_strength_no_special(self):
        """Test password without special character"""
        is_valid, issues = self.validator.validate_password_strength("Password123")
        assert is_valid is False
        assert any("special" in issue for issue in issues)

    def test_validate_password_strength_custom_requirements(self):
        """Test password with custom requirements"""
        is_valid, issues = self.validator.validate_password_strength(
            "password",
            min_length=4,
            require_uppercase=False,
            require_lowercase=True,
            require_digit=False,
            require_special=False
        )
        assert is_valid is True
        assert len(issues) == 0

    # Range validation tests
    def test_validate_range_valid(self):
        """Test value within range"""
        is_valid, error = self.validator.validate_range(50, min_value=0, max_value=100)
        assert is_valid is True
        assert error is None

    def test_validate_range_too_low(self):
        """Test value below minimum"""
        is_valid, error = self.validator.validate_range(-5, min_value=0)
        assert is_valid is False
        assert "at least" in error.lower()

    def test_validate_range_too_high(self):
        """Test value above maximum"""
        is_valid, error = self.validator.validate_range(150, max_value=100)
        assert is_valid is False
        assert "at most" in error.lower()

    def test_validate_range_invalid_type(self):
        """Test invalid value type"""
        is_valid, error = self.validator.validate_range("invalid", min_value=0, max_value=100)
        assert is_valid is False
        assert "number" in error.lower()

    # Length validation tests
    def test_validate_length_valid(self):
        """Test string within length range"""
        is_valid, error = self.validator.validate_length("hello", min_length=3, max_length=10)
        assert is_valid is True
        assert error is None

    def test_validate_length_too_short(self):
        """Test string too short"""
        is_valid, error = self.validator.validate_length("ab", min_length=3)
        assert is_valid is False
        assert "at least" in error.lower()

    def test_validate_length_too_long(self):
        """Test string too long"""
        is_valid, error = self.validator.validate_length("a" * 11, max_length=10)
        assert is_valid is False
        assert "at most" in error.lower()

    def test_validate_length_invalid_type(self):
        """Test invalid value type"""
        is_valid, error = self.validator.validate_length(123, min_length=1, max_length=10)
        assert is_valid is False
        assert "string" in error.lower()

    # Pattern validation tests
    def test_validate_pattern_valid(self):
        """Test value matching pattern"""
        pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
        is_valid, error = self.validator.validate_pattern("123-456-7890", pattern)
        assert is_valid is True
        assert error is None

    def test_validate_pattern_invalid(self):
        """Test value not matching pattern"""
        pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
        is_valid, error = self.validator.validate_pattern("invalid", pattern)
        assert is_valid is False
        assert "does not match" in error.lower()

    def test_validate_pattern_custom_error(self):
        """Test pattern validation with custom error message"""
        pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
        is_valid, error = self.validator.validate_pattern(
            "invalid",
            pattern,
            error_message="Must be in format XXX-XXX-XXXX"
        )
        assert is_valid is False
        assert error == "Must be in format XXX-XXX-XXXX"

    def test_validate_pattern_invalid_type(self):
        """Test pattern validation with non-string value"""
        pattern = re.compile(r"^\d+$")
        is_valid, error = self.validator.validate_pattern(123, pattern)
        assert is_valid is False
        assert "string" in error.lower()

    # Enum validation tests
    def test_validate_enum_valid(self):
        """Test value in allowed values"""
        is_valid, error = self.validator.validate_enum("red", ["red", "green", "blue"])
        assert is_valid is True
        assert error is None

    def test_validate_enum_invalid(self):
        """Test value not in allowed values"""
        is_valid, error = self.validator.validate_enum("yellow", ["red", "green", "blue"])
        assert is_valid is False
        assert "must be one of" in error.lower()

    def test_validate_enum_case_insensitive(self):
        """Test case-insensitive enum validation"""
        is_valid, error = self.validator.validate_enum("RED", ["red", "green", "blue"], case_sensitive=False)
        assert is_valid is True
        assert error is None

    def test_validate_enum_case_sensitive(self):
        """Test case-sensitive enum validation"""
        is_valid, error = self.validator.validate_enum("RED", ["red", "green", "blue"], case_sensitive=True)
        assert is_valid is False
        assert "must be one of" in error.lower()

    # Cross-field validation tests
    def test_validate_cross_field_eq(self):
        """Test cross-field equality"""
        data = {"password": "secret", "confirm_password": "secret"}
        is_valid, error = self.validator.validate_cross_field(data, "password", "confirm_password", "eq")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_ne(self):
        """Test cross-field inequality"""
        data = {"field1": "value1", "field2": "value2"}
        is_valid, error = self.validator.validate_cross_field(data, "field1", "field2", "ne")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_lt(self):
        """Test cross-field less than"""
        data = {"start_date": 1, "end_date": 2}
        is_valid, error = self.validator.validate_cross_field(data, "start_date", "end_date", "lt")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_le(self):
        """Test cross-field less than or equal"""
        data = {"value1": 1, "value2": 1}
        is_valid, error = self.validator.validate_cross_field(data, "value1", "value2", "le")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_gt(self):
        """Test cross-field greater than"""
        data = {"value1": 10, "value2": 5}
        is_valid, error = self.validator.validate_cross_field(data, "value1", "value2", "gt")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_ge(self):
        """Test cross-field greater than or equal"""
        data = {"value1": 10, "value2": 10}
        is_valid, error = self.validator.validate_cross_field(data, "value1", "value2", "ge")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_missing_field(self):
        """Test cross-field with missing field"""
        data = {"field1": "value"}
        is_valid, error = self.validator.validate_cross_field(data, "field1", "field2", "eq")
        assert is_valid is False
        assert "must both be present" in error.lower()

    def test_validate_cross_field_unknown_comparison(self):
        """Test cross-field with unknown comparison"""
        data = {"field1": "value1", "field2": "value2"}
        is_valid, error = self.validator.validate_cross_field(data, "field1", "field2", "unknown")
        assert is_valid is False
        assert "Unknown comparison" in error

    def test_validate_cross_field_custom_error(self):
        """Test cross-field with custom error message"""
        data = {"password": "secret1", "confirm_password": "secret2"}
        is_valid, error = self.validator.validate_cross_field(
            data,
            "password",
            "confirm_password",
            "eq",
            error_message="Passwords do not match"
        )
        assert is_valid is False
        assert error == "Passwords do not match"

    # Custom rules tests
    def test_add_rule(self):
        """Test adding custom validation rule"""
        rule = ValidationRule(
            field="test",
            validator=lambda x: x > 0,
            error_message="Must be positive"
        )

        self.validator.add_rule(rule)
        assert len(self.validator.custom_rules) == 1
        assert self.validator.custom_rules[0] == rule


class TestTemplateValidator:
    """Tests for TemplateValidator class"""

    def setup_method(self):
        """Setup test fixture"""
        self.validator = TemplateValidator()

    def test_initialization(self):
        """Test TemplateValidator initialization"""
        assert self.validator.enhanced is not None
        assert isinstance(self.validator.enhanced, EnhancedValidator)

    def test_validate_variable_required_missing(self):
        """Test validation of required variable without value"""
        variable = Variable(name="test", value=None, required=True)
        result = self.validator.validate_variable(variable)

        assert result.is_valid is False
        assert "test" in result.missing_required

    def test_validate_variable_optional_missing(self):
        """Test validation of optional variable without value"""
        variable = Variable(name="test", value=None, required=False)
        result = self.validator.validate_variable(variable)

        assert result.is_valid is True
        assert len(result.missing_required) == 0

    def test_validate_variable_email_valid(self):
        """Test validation of valid email variable"""
        variable = Variable(name="email", value="test@example.com", data_type="email")
        result = self.validator.validate_variable(variable)

        assert result.is_valid is True

    def test_validate_variable_email_invalid(self):
        """Test validation of invalid email variable"""
        variable = Variable(name="email", value="invalid-email", data_type="email")
        result = self.validator.validate_variable(variable)

        assert result.is_valid is False
        assert "email" in result.invalid_values

    def test_validate_variable_url_valid(self):
        """Test validation of valid URL variable"""
        variable = Variable(name="website", value="https://example.com", data_type="url")
        result = self.validator.validate_variable(variable)

        assert result.is_valid is True

    def test_validate_variable_url_invalid(self):
        """Test validation of invalid URL variable"""
        variable = Variable(name="website", value="not-a-url", data_type="url")
        result = self.validator.validate_variable(variable)

        assert result.is_valid is False
        assert "website" in result.invalid_values

    def test_validate_variable_iban_valid(self):
        """Test validation of valid IBAN variable"""
        variable = Variable(name="iban", value="DE89370400440532013000", data_type="iban")
        result = self.validator.validate_variable(variable)

        assert result.is_valid is True

    def test_validate_variable_iban_invalid(self):
        """Test validation of invalid IBAN variable"""
        variable = Variable(name="iban", value="INVALID", data_type="iban")
        result = self.validator.validate_variable(variable)

        assert result.is_valid is False
        assert "iban" in result.invalid_values

    def test_validate_filled_template(self):
        """Test validation of filled template with multiple variables"""
        variables = [
            Variable(name="name", value="John Doe", required=True),
            Variable(name="email", value="john@example.com", data_type="email"),
            Variable(name="website", value="https://example.com", data_type="url"),
        ]

        result = self.validator.validate_filled_template(variables)
        assert result.is_valid is True

    def test_validate_filled_template_with_errors(self):
        """Test validation of filled template with errors"""
        variables = [
            Variable(name="name", value=None, required=True),  # Missing required
            Variable(name="email", value="invalid-email", data_type="email"),  # Invalid
        ]

        result = self.validator.validate_filled_template(variables)
        assert result.is_valid is False
        assert "name" in result.missing_required
        assert "email" in result.invalid_values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
