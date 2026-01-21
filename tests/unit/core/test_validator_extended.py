"""
Comprehensive tests for validator.py module

Tests cover:
- ValidationRule class (3 tests)
- EnhancedValidator initialization (2 tests)
- Format validators (50+ tests):
  - URL, IBAN, BIC, postal codes, IP addresses
  - UUID, hex color, credit cards
  - Tax IDs, VAT IDs, SSN, passport, license plates
  - MAC addresses, ISBN, EAN, VIN
  - Bitcoin/Ethereum addresses, coordinates
  - Domain, JSON, file paths
- Content validators (15+ tests):
  - Age, username, password strength
  - Range, length, pattern, enum
  - Cross-field validation
- TemplateValidator class (20+ tests):
  - Variable validation (all data types)
  - Config validation
  - Financial validation
  - System settings validation
  - Template validation

Total: 90+ comprehensive test methods
Coverage target: 13.3% → 80%+
"""

import pytest
import re
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.core.validator import (
    ValidationRule,
    EnhancedValidator,
    TemplateValidator,
)
from src.models.template import Variable, ValidationResult


# ============================================================================
# ValidationRule Tests (3 tests)
# ============================================================================


class TestValidationRule:
    """Test ValidationRule class"""

    def test_init(self):
        """Test ValidationRule initialization"""
        rule = ValidationRule(
            field="test_field",
            validator=lambda x: x > 0,
            error_message="Value must be positive",
            severity="error",
        )

        assert rule.field == "test_field"
        assert callable(rule.validator)
        assert rule.error_message == "Value must be positive"
        assert rule.severity == "error"

    def test_validate_success(self):
        """Test successful validation"""
        rule = ValidationRule(
            field="age", validator=lambda x: x >= 18, error_message="Must be 18 or older"
        )

        is_valid, error = rule.validate(25)
        assert is_valid is True
        assert error is None

    def test_validate_failure(self):
        """Test failed validation"""
        rule = ValidationRule(
            field="age", validator=lambda x: x >= 18, error_message="Must be 18 or older"
        )

        is_valid, error = rule.validate(15)
        assert is_valid is False
        assert error == "Must be 18 or older"

    def test_validate_with_exception(self):
        """Test validation with exception"""
        rule = ValidationRule(
            field="test",
            validator=lambda x: int(x) > 0,  # Will fail for non-numeric values
            error_message="Must be positive number",
        )

        is_valid, error = rule.validate("not_a_number")
        assert is_valid is False
        assert "Must be positive number" in error
        assert "Exception:" in error


# ============================================================================
# EnhancedValidator Initialization Tests (2 tests)
# ============================================================================


class TestEnhancedValidatorInit:
    """Test EnhancedValidator initialization"""

    def test_init(self):
        """Test EnhancedValidator initialization"""
        validator = EnhancedValidator()

        assert isinstance(validator.custom_rules, list)
        assert len(validator.custom_rules) == 0
        assert hasattr(validator, "PATTERNS")
        assert isinstance(validator.PATTERNS, dict)

    def test_add_rule(self):
        """Test adding custom validation rule"""
        validator = EnhancedValidator()
        rule = ValidationRule(field="test", validator=lambda x: True, error_message="Test")

        validator.add_rule(rule)

        assert len(validator.custom_rules) == 1
        assert validator.custom_rules[0] == rule


# ============================================================================
# EnhancedValidator URL Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorURL:
    """Test URL validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_url_valid(self, validator):
        """Test valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com",
            "http://subdomain.example.com:8080",
            "https://example.com/path/to/page",
            "http://192.168.1.1",
            "http://localhost",
        ]

        for url in valid_urls:
            assert validator.validate_url(url) is True, f"Failed for: {url}"

    def test_validate_url_invalid(self, validator):
        """Test invalid URLs"""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",  # Not http/https
            "example.com",  # No protocol
            "http://",
            "",
        ]

        for url in invalid_urls:
            assert validator.validate_url(url) is False, f"Should fail for: {url}"

    def test_validate_url_empty(self, validator):
        """Test empty URL"""
        assert validator.validate_url("") is False
        assert validator.validate_url(None) is False

    def test_validate_url_case_insensitive(self, validator):
        """Test URL validation is case-insensitive"""
        assert validator.validate_url("HTTP://EXAMPLE.COM") is True
        assert validator.validate_url("HTTPS://EXAMPLE.COM") is True


# ============================================================================
# EnhancedValidator IBAN Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorIBAN:
    """Test IBAN validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_iban_valid(self, validator):
        """Test valid IBAN"""
        valid_ibans = [
            "DE89370400440532013000",
            "GB82WEST12345698765432",
            "FR1420041010050500013M02606",
        ]

        for iban in valid_ibans:
            assert validator.validate_iban(iban) is True, f"Failed for: {iban}"

    def test_validate_iban_with_spaces(self, validator):
        """Test IBAN with spaces (should be handled)"""
        assert validator.validate_iban("DE89 3704 0044 0532 0130 00") is True

    def test_validate_iban_invalid(self, validator):
        """Test invalid IBAN"""
        invalid_ibans = ["INVALID", "DE123", "12345678901234567890", ""]

        for iban in invalid_ibans:
            assert validator.validate_iban(iban) is False, f"Should fail for: {iban}"


# ============================================================================
# EnhancedValidator BIC Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorBIC:
    """Test BIC/SWIFT validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_bic_valid(self, validator):
        """Test valid BIC codes"""
        valid_bics = [
            "DEUTDEFF",  # 8 characters
            "DEUTDEFFXXX",  # 11 characters
            "COBADEFF",
            "COBADEFFXXX",
        ]

        for bic in valid_bics:
            assert validator.validate_bic(bic) is True, f"Failed for: {bic}"

    def test_validate_bic_case_handling(self, validator):
        """Test BIC case handling (converts to uppercase)"""
        assert validator.validate_bic("deutdeff") is True
        assert validator.validate_bic("DeutDeff") is True

    def test_validate_bic_invalid(self, validator):
        """Test invalid BIC codes"""
        invalid_bics = ["INVALID", "DE", "DEUTDE", "DEUTDEFFXXXX", ""]

        for bic in invalid_bics:
            assert validator.validate_bic(bic) is False, f"Should fail for: {bic}"


# ============================================================================
# EnhancedValidator Postal Code Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorPostalCode:
    """Test postal code validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_postal_code_de_valid(self, validator):
        """Test valid German postal codes"""
        valid_codes = ["12345", "01234", "99999"]

        for code in valid_codes:
            assert validator.validate_postal_code(code, "DE") is True, f"Failed for: {code}"

    def test_validate_postal_code_de_invalid(self, validator):
        """Test invalid German postal codes"""
        invalid_codes = ["1234", "123456", "ABCDE", ""]

        for code in invalid_codes:
            assert validator.validate_postal_code(code, "DE") is False, f"Should fail for: {code}"

    def test_validate_postal_code_general(self, validator):
        """Test general postal code validation"""
        valid_codes = ["ABC123", "12345", "SW1A 1AA"]

        for code in valid_codes:
            assert validator.validate_postal_code(code, "US") is True, f"Failed for: {code}"

    def test_validate_postal_code_empty(self, validator):
        """Test empty postal code"""
        assert validator.validate_postal_code("", "DE") is False


# ============================================================================
# EnhancedValidator IP Address Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorIPAddress:
    """Test IP address validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_ipv4_valid(self, validator):
        """Test valid IPv4 addresses"""
        valid_ips = ["192.168.1.1", "10.0.0.1", "127.0.0.1", "255.255.255.255"]

        for ip in valid_ips:
            assert validator.validate_ip_address(ip, 4) is True, f"Failed for: {ip}"

    def test_validate_ipv4_invalid(self, validator):
        """Test invalid IPv4 addresses"""
        invalid_ips = ["256.256.256.256", "192.168.1", "192.168.1.1.1", ""]

        for ip in invalid_ips:
            assert validator.validate_ip_address(ip, 4) is False, f"Should fail for: {ip}"

    def test_validate_ipv6_valid(self, validator):
        """Test valid IPv6 addresses"""
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "::1",
            "fe80::1",
        ]

        for ip in valid_ips:
            assert validator.validate_ip_address(ip, 6) is True, f"Failed for: {ip}"

    def test_validate_ip_default_version(self, validator):
        """Test IP validation with default version (IPv4)"""
        assert validator.validate_ip_address("192.168.1.1") is True

    def test_validate_ip_empty(self, validator):
        """Test empty IP address"""
        assert validator.validate_ip_address("", 4) is False


# ============================================================================
# EnhancedValidator UUID Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorUUID:
    """Test UUID validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_uuid_valid(self, validator):
        """Test valid UUIDs"""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "123e4567-e89b-12d3-a456-426614174000",
        ]

        for uuid in valid_uuids:
            assert validator.validate_uuid(uuid) is True, f"Failed for: {uuid}"

    def test_validate_uuid_invalid(self, validator):
        """Test invalid UUIDs"""
        invalid_uuids = [
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",
            "550e8400e29b41d4a716446655440000",  # No hyphens
            "",
        ]

        for uuid in invalid_uuids:
            assert validator.validate_uuid(uuid) is False, f"Should fail for: {uuid}"

    def test_validate_uuid_case_insensitive(self, validator):
        """Test UUID case insensitivity"""
        assert validator.validate_uuid("550E8400-E29B-41D4-A716-446655440000") is True


# ============================================================================
# EnhancedValidator Hex Color Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorHexColor:
    """Test hex color validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_hex_color_valid_6(self, validator):
        """Test valid 6-character hex colors"""
        valid_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000"]

        for color in valid_colors:
            assert validator.validate_hex_color(color) is True, f"Failed for: {color}"

    def test_validate_hex_color_valid_3(self, validator):
        """Test valid 3-character hex colors"""
        valid_colors = ["#F00", "#0F0", "#00F", "#FFF", "#000"]

        for color in valid_colors:
            assert validator.validate_hex_color(color) is True, f"Failed for: {color}"

    def test_validate_hex_color_without_hash(self, validator):
        """Test hex colors without # prefix"""
        assert validator.validate_hex_color("FF0000") is True
        assert validator.validate_hex_color("F00") is True

    def test_validate_hex_color_invalid(self, validator):
        """Test invalid hex colors"""
        invalid_colors = ["#GG0000", "#FF00", "#FFFFFFF", "red", ""]

        for color in invalid_colors:
            assert validator.validate_hex_color(color) is False, f"Should fail for: {color}"


# ============================================================================
# EnhancedValidator Credit Card Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorCreditCard:
    """Test credit card validation (Luhn algorithm)"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_credit_card_valid(self, validator):
        """Test valid credit card numbers"""
        valid_cards = [
            "4532015112830366",  # Visa
            "5425233430109903",  # Mastercard
            "374245455400126",  # Amex
        ]

        for card in valid_cards:
            assert validator.validate_credit_card(card) is True, f"Failed for: {card}"

    def test_validate_credit_card_with_spaces(self, validator):
        """Test credit card with spaces"""
        assert validator.validate_credit_card("4532 0151 1283 0366") is True

    def test_validate_credit_card_with_dashes(self, validator):
        """Test credit card with dashes"""
        assert validator.validate_credit_card("4532-0151-1283-0366") is True

    def test_validate_credit_card_invalid(self, validator):
        """Test invalid credit card numbers"""
        invalid_cards = [
            "1234567890123456",  # Wrong checksum
            "123",  # Too short
            "12345678901234567890",  # Too long
            "",
        ]

        for card in invalid_cards:
            assert validator.validate_credit_card(card) is False, f"Should fail for: {card}"


# ============================================================================
# EnhancedValidator Tax ID Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorTaxID:
    """Test tax ID validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_tax_id_de_valid(self, validator):
        """Test valid German tax ID"""
        assert validator.validate_tax_id("12345678901", "DE") is True

    def test_validate_tax_id_de_invalid(self, validator):
        """Test invalid German tax ID"""
        invalid_ids = ["123456789", "123456789012", "ABCDEFGHIJK", ""]

        for tax_id in invalid_ids:
            assert validator.validate_tax_id(tax_id, "DE") is False

    def test_validate_tax_id_unknown_country(self, validator):
        """Test tax ID for unknown country"""
        assert validator.validate_tax_id("12345678901", "US") is False


# ============================================================================
# EnhancedValidator VAT ID Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorVATID:
    """Test VAT ID validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_vat_id_de_valid(self, validator):
        """Test valid German VAT ID"""
        assert validator.validate_vat_id("DE123456789", "DE") is True

    def test_validate_vat_id_de_invalid(self, validator):
        """Test invalid German VAT ID"""
        invalid_ids = ["DE12345678", "DE1234567890", "123456789", ""]

        for vat_id in invalid_ids:
            assert validator.validate_vat_id(vat_id, "DE") is False

    def test_validate_vat_id_unknown_country(self, validator):
        """Test VAT ID for unknown country"""
        assert validator.validate_vat_id("GB123456789", "GB") is False


# ============================================================================
# EnhancedValidator MAC Address Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorMACAddress:
    """Test MAC address validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_mac_address_colon(self, validator):
        """Test MAC address with colons"""
        assert validator.validate_mac_address("00:11:22:33:44:55") is True
        assert validator.validate_mac_address("AA:BB:CC:DD:EE:FF") is True

    def test_validate_mac_address_hyphen(self, validator):
        """Test MAC address with hyphens"""
        assert validator.validate_mac_address("00-11-22-33-44-55") is True
        assert validator.validate_mac_address("AA-BB-CC-DD-EE-FF") is True

    def test_validate_mac_address_invalid(self, validator):
        """Test invalid MAC addresses"""
        invalid_macs = [
            "00:11:22:33:44",  # Too short
            "00:11:22:33:44:55:66",  # Too long
            "GG:11:22:33:44:55",  # Invalid character
            "",
        ]

        for mac in invalid_macs:
            assert validator.validate_mac_address(mac) is False


# ============================================================================
# EnhancedValidator SSN Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorSSN:
    """Test Social Security Number validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_ssn_us_valid(self, validator):
        """Test valid US SSN"""
        assert validator.validate_ssn("123-45-6789", "US") is True

    def test_validate_ssn_us_invalid(self, validator):
        """Test invalid US SSN"""
        invalid_ssns = ["123456789", "123-456-789", "12-34-5678", ""]

        for ssn in invalid_ssns:
            assert validator.validate_ssn(ssn, "US") is False

    def test_validate_ssn_unknown_country(self, validator):
        """Test SSN for unknown country"""
        assert validator.validate_ssn("123-45-6789", "DE") is False


# ============================================================================
# EnhancedValidator ISBN Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorISBN:
    """Test ISBN validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_isbn10_valid(self, validator):
        """Test valid ISBN-10"""
        # Valid ISBN-10 with correct checksum
        assert validator.validate_isbn("0471958697") is True
        assert validator.validate_isbn("0-306-40615-2") is True

    def test_validate_isbn10_with_x(self, validator):
        """Test ISBN-10 with X checksum"""
        assert validator.validate_isbn("043942089X") is True

    def test_validate_isbn13_valid(self, validator):
        """Test valid ISBN-13"""
        assert validator.validate_isbn("9780306406157") is True
        assert validator.validate_isbn("978-0-306-40615-7") is True

    def test_validate_isbn_invalid_checksum(self, validator):
        """Test ISBN with invalid checksum"""
        assert validator.validate_isbn("0471958698") is False  # Wrong checksum
        assert validator.validate_isbn("9780306406158") is False  # Wrong checksum

    def test_validate_isbn_invalid_format(self, validator):
        """Test invalid ISBN format"""
        invalid_isbns = ["123", "123456789012345", "ABCDEFGHIJ", ""]

        for isbn in invalid_isbns:
            assert validator.validate_isbn(isbn) is False


# ============================================================================
# EnhancedValidator EAN Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorEAN:
    """Test EAN-13 barcode validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_ean_valid(self, validator):
        """Test valid EAN-13"""
        # Valid EAN-13 with correct checksum
        assert validator.validate_ean("4006381333931") is True

    def test_validate_ean_invalid_checksum(self, validator):
        """Test EAN with invalid checksum"""
        assert validator.validate_ean("4006381333932") is False

    def test_validate_ean_invalid_format(self, validator):
        """Test invalid EAN format"""
        invalid_eans = ["123456789012", "12345678901234", "ABCDEFGHIJKLM", ""]

        for ean in invalid_eans:
            assert validator.validate_ean(ean) is False


# ============================================================================
# EnhancedValidator VIN Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorVIN:
    """Test Vehicle Identification Number validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_vin_valid(self, validator):
        """Test valid VIN"""
        assert validator.validate_vin("1HGBH41JXMN109186") is True

    def test_validate_vin_case_handling(self, validator):
        """Test VIN case handling"""
        assert validator.validate_vin("1hgbh41jxmn109186") is True

    def test_validate_vin_invalid_chars(self, validator):
        """Test VIN with invalid characters (I, O, Q not allowed)"""
        assert validator.validate_vin("1HGBH41JXMN109I86") is False  # Contains I
        assert validator.validate_vin("1HGBH41JXMN109O86") is False  # Contains O
        assert validator.validate_vin("1HGBH41JXMN109Q86") is False  # Contains Q

    def test_validate_vin_invalid_length(self, validator):
        """Test VIN with invalid length"""
        invalid_vins = ["1HGBH41JXMN10918", "1HGBH41JXMN1091866", ""]

        for vin in invalid_vins:
            assert validator.validate_vin(vin) is False


# ============================================================================
# EnhancedValidator Crypto Address Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorCryptoAddress:
    """Test cryptocurrency address validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_bitcoin_address_valid(self, validator):
        """Test valid Bitcoin address"""
        assert validator.validate_bitcoin_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") is True
        assert validator.validate_bitcoin_address("3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy") is True

    def test_validate_bitcoin_address_invalid(self, validator):
        """Test invalid Bitcoin address"""
        invalid_addrs = ["invalid", "0x1234567890", ""]

        for addr in invalid_addrs:
            assert validator.validate_bitcoin_address(addr) is False

    def test_validate_ethereum_address_valid(self, validator):
        """Test valid Ethereum address"""
        assert validator.validate_ethereum_address("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb") is True

    def test_validate_ethereum_address_invalid(self, validator):
        """Test invalid Ethereum address"""
        invalid_addrs = [
            "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",  # Too long
            "742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",  # No 0x prefix
            "",
        ]

        for addr in invalid_addrs:
            assert validator.validate_ethereum_address(addr) is False


# ============================================================================
# EnhancedValidator Coordinates Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorCoordinates:
    """Test geographic coordinates validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_coordinates_valid(self, validator):
        """Test valid coordinates"""
        is_valid, error = validator.validate_coordinates("52.5200", "13.4050")
        assert is_valid is True
        assert error is None

    def test_validate_coordinates_boundaries(self, validator):
        """Test coordinate boundaries"""
        # Valid boundaries
        assert validator.validate_coordinates("90", "180")[0] is True
        assert validator.validate_coordinates("-90", "-180")[0] is True
        assert validator.validate_coordinates("0", "0")[0] is True

    def test_validate_coordinates_invalid_latitude(self, validator):
        """Test invalid latitude"""
        is_valid, error = validator.validate_coordinates("91", "0")
        assert is_valid is False
        assert "latitude" in error.lower()

    def test_validate_coordinates_invalid_longitude(self, validator):
        """Test invalid longitude"""
        is_valid, error = validator.validate_coordinates("0", "181")
        assert is_valid is False
        assert "longitude" in error.lower()

    def test_validate_coordinates_empty(self, validator):
        """Test empty coordinates"""
        is_valid, error = validator.validate_coordinates("", "")
        assert is_valid is False
        assert "required" in error.lower()


# ============================================================================
# EnhancedValidator Passport Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorPassport:
    """Test passport validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_passport_de_valid(self, validator):
        """Test valid German passport"""
        assert validator.validate_passport("C01X00T47", "DE") is True

    def test_validate_passport_de_case_handling(self, validator):
        """Test passport case handling"""
        assert validator.validate_passport("c01x00t47", "DE") is True

    def test_validate_passport_invalid(self, validator):
        """Test invalid passport"""
        invalid_passports = ["123456789", "C01X00T471", "AB", ""]

        for passport in invalid_passports:
            assert validator.validate_passport(passport, "DE") is False


# ============================================================================
# EnhancedValidator License Plate Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorLicensePlate:
    """Test license plate validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_license_plate_de_valid(self, validator):
        """Test valid German license plate"""
        assert validator.validate_license_plate("B-AB 1234", "DE") is True
        assert validator.validate_license_plate("M-XY 123", "DE") is True

    def test_validate_license_plate_de_case_handling(self, validator):
        """Test license plate case handling"""
        assert validator.validate_license_plate("b-ab 1234", "DE") is True

    def test_validate_license_plate_invalid(self, validator):
        """Test invalid license plate"""
        invalid_plates = ["INVALID", "B-12345", ""]

        for plate in invalid_plates:
            assert validator.validate_license_plate(plate, "DE") is False


# ============================================================================
# EnhancedValidator File Path Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorFilePath:
    """Test file path validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_file_path_valid(self, validator):
        """Test valid file paths"""
        valid_paths = ["/home/user/file.txt", "C:\\Users\\user\\file.txt", "relative/path/file.txt"]

        for path in valid_paths:
            is_valid, error = validator.validate_file_path(path, must_exist=False)
            assert is_valid is True, f"Failed for: {path}"

    def test_validate_file_path_invalid_chars(self, validator):
        """Test file path with invalid characters"""
        invalid_paths = ['/home/user/file<>.txt', 'C:\\Users\\user\\file|.txt', 'path\\file?.txt']

        for path in invalid_paths:
            is_valid, error = validator.validate_file_path(path, must_exist=False)
            assert is_valid is False

    def test_validate_file_path_empty(self, validator):
        """Test empty file path"""
        is_valid, error = validator.validate_file_path("", must_exist=False)
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_file_path_must_exist(self, validator, tmp_path):
        """Test file path existence check"""
        # Non-existent file
        is_valid, error = validator.validate_file_path("/nonexistent/file.txt", must_exist=True)
        assert is_valid is False
        assert "does not exist" in error

        # Existing file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        is_valid, error = validator.validate_file_path(str(test_file), must_exist=True)
        assert is_valid is True


# ============================================================================
# EnhancedValidator Domain Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorDomain:
    """Test domain name validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_domain_valid(self, validator):
        """Test valid domain names"""
        valid_domains = ["example.com", "sub.example.com", "example.co.uk", "test-domain.org"]

        for domain in valid_domains:
            assert validator.validate_domain(domain) is True, f"Failed for: {domain}"

    def test_validate_domain_invalid(self, validator):
        """Test invalid domain names"""
        invalid_domains = ["invalid", "example", "example.", ".com", ""]

        for domain in invalid_domains:
            assert validator.validate_domain(domain) is False

    def test_validate_domain_case_insensitive(self, validator):
        """Test domain case insensitivity"""
        assert validator.validate_domain("EXAMPLE.COM") is True


# ============================================================================
# EnhancedValidator JSON Tests (4 tests)
# ============================================================================


class TestEnhancedValidatorJSON:
    """Test JSON validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_json_valid(self, validator):
        """Test valid JSON"""
        valid_json = ['{"key": "value"}', '[1, 2, 3]', '{"nested": {"key": "value"}}']

        for json_str in valid_json:
            is_valid, error = validator.validate_json(json_str)
            assert is_valid is True, f"Failed for: {json_str}"

    def test_validate_json_invalid(self, validator):
        """Test invalid JSON"""
        invalid_json = ['{"key": "value"', '{key: "value"}', "not json"]

        for json_str in invalid_json:
            is_valid, error = validator.validate_json(json_str)
            assert is_valid is False

    def test_validate_json_empty(self, validator):
        """Test empty JSON string"""
        is_valid, error = validator.validate_json("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_json_error_message(self, validator):
        """Test JSON error message contains details"""
        is_valid, error = validator.validate_json("{invalid}")
        assert is_valid is False
        assert "Invalid JSON" in error


# ============================================================================
# EnhancedValidator Age Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorAge:
    """Test age validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_age_valid(self, validator):
        """Test valid age"""
        is_valid, error = validator.validate_age(25)
        assert is_valid is True
        assert error is None

    def test_validate_age_boundaries(self, validator):
        """Test age boundaries"""
        assert validator.validate_age(0)[0] is True
        assert validator.validate_age(150)[0] is True

    def test_validate_age_too_low(self, validator):
        """Test age below minimum"""
        is_valid, error = validator.validate_age(-1)
        assert is_valid is False
        assert "at least" in error

    def test_validate_age_too_high(self, validator):
        """Test age above maximum"""
        is_valid, error = validator.validate_age(200)
        assert is_valid is False
        assert "at most" in error

    def test_validate_age_invalid_type(self, validator):
        """Test invalid age type"""
        is_valid, error = validator.validate_age("not a number")
        assert is_valid is False
        assert "must be a valid number" in error


# ============================================================================
# EnhancedValidator Username Tests (7 tests)
# ============================================================================


class TestEnhancedValidatorUsername:
    """Test username validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_username_valid(self, validator):
        """Test valid usernames"""
        valid_usernames = ["user123", "john_doe", "test_user_123"]

        for username in valid_usernames:
            is_valid, error = validator.validate_username(username)
            assert is_valid is True, f"Failed for: {username}"

    def test_validate_username_too_short(self, validator):
        """Test username too short"""
        is_valid, error = validator.validate_username("ab")
        assert is_valid is False
        assert "at least" in error

    def test_validate_username_too_long(self, validator):
        """Test username too long"""
        is_valid, error = validator.validate_username("a" * 21)
        assert is_valid is False
        assert "at most" in error

    def test_validate_username_empty(self, validator):
        """Test empty username"""
        is_valid, error = validator.validate_username("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_username_invalid_chars(self, validator):
        """Test username with invalid characters"""
        is_valid, error = validator.validate_username("user@name")
        assert is_valid is False
        assert "can only contain" in error

    def test_validate_username_special_allowed(self, validator):
        """Test username with allowed special characters"""
        is_valid, error = validator.validate_username("user.name-123", allow_special=True)
        assert is_valid is True

    def test_validate_username_custom_length(self, validator):
        """Test username with custom length constraints"""
        is_valid, error = validator.validate_username("ab", min_length=2, max_length=5)
        assert is_valid is True


# ============================================================================
# EnhancedValidator Password Strength Tests (8 tests)
# ============================================================================


class TestEnhancedValidatorPasswordStrength:
    """Test password strength validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_password_strength_strong(self, validator):
        """Test strong password"""
        is_valid, issues = validator.validate_password_strength("StrongP@ssw0rd!")
        assert is_valid is True
        assert len(issues) == 0

    def test_validate_password_strength_too_short(self, validator):
        """Test password too short"""
        is_valid, issues = validator.validate_password_strength("Sh0rt!")
        assert is_valid is False
        assert any("at least" in issue for issue in issues)

    def test_validate_password_strength_no_uppercase(self, validator):
        """Test password without uppercase"""
        is_valid, issues = validator.validate_password_strength("weakp@ssw0rd")
        assert is_valid is False
        assert any("uppercase" in issue for issue in issues)

    def test_validate_password_strength_no_lowercase(self, validator):
        """Test password without lowercase"""
        is_valid, issues = validator.validate_password_strength("WEAKP@SSW0RD")
        assert is_valid is False
        assert any("lowercase" in issue for issue in issues)

    def test_validate_password_strength_no_digit(self, validator):
        """Test password without digit"""
        is_valid, issues = validator.validate_password_strength("WeakP@ssword")
        assert is_valid is False
        assert any("digit" in issue for issue in issues)

    def test_validate_password_strength_no_special(self, validator):
        """Test password without special character"""
        is_valid, issues = validator.validate_password_strength("WeakPassword0")
        assert is_valid is False
        assert any("special" in issue for issue in issues)

    def test_validate_password_strength_empty(self, validator):
        """Test empty password"""
        is_valid, issues = validator.validate_password_strength("")
        assert is_valid is False
        assert any("empty" in issue.lower() for issue in issues)

    def test_validate_password_strength_custom_requirements(self, validator):
        """Test password with custom requirements"""
        is_valid, issues = validator.validate_password_strength(
            "simplepass", min_length=6, require_uppercase=False, require_special=False, require_digit=False
        )
        assert is_valid is True


# ============================================================================
# EnhancedValidator Range Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorRange:
    """Test numeric range validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_range_valid(self, validator):
        """Test value within range"""
        is_valid, error = validator.validate_range(50, min_value=0, max_value=100)
        assert is_valid is True
        assert error is None

    def test_validate_range_below_min(self, validator):
        """Test value below minimum"""
        is_valid, error = validator.validate_range(5, min_value=10)
        assert is_valid is False
        assert "at least" in error

    def test_validate_range_above_max(self, validator):
        """Test value above maximum"""
        is_valid, error = validator.validate_range(150, max_value=100)
        assert is_valid is False
        assert "at most" in error

    def test_validate_range_no_limits(self, validator):
        """Test range validation with no limits"""
        is_valid, error = validator.validate_range(999999)
        assert is_valid is True

    def test_validate_range_invalid_type(self, validator):
        """Test range validation with invalid type"""
        is_valid, error = validator.validate_range("not a number", min_value=0)
        assert is_valid is False
        assert "must be a number" in error


# ============================================================================
# EnhancedValidator Length Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorLength:
    """Test string length validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_length_valid(self, validator):
        """Test string within length range"""
        is_valid, error = validator.validate_length("hello", min_length=3, max_length=10)
        assert is_valid is True
        assert error is None

    def test_validate_length_too_short(self, validator):
        """Test string too short"""
        is_valid, error = validator.validate_length("hi", min_length=5)
        assert is_valid is False
        assert "at least" in error

    def test_validate_length_too_long(self, validator):
        """Test string too long"""
        is_valid, error = validator.validate_length("very long string", max_length=5)
        assert is_valid is False
        assert "at most" in error

    def test_validate_length_no_limits(self, validator):
        """Test length validation with no limits"""
        is_valid, error = validator.validate_length("any length string")
        assert is_valid is True

    def test_validate_length_invalid_type(self, validator):
        """Test length validation with non-string"""
        is_valid, error = validator.validate_length(123, min_length=1)
        assert is_valid is False
        assert "must be a string" in error


# ============================================================================
# EnhancedValidator Pattern Tests (3 tests)
# ============================================================================


class TestEnhancedValidatorPattern:
    """Test regex pattern validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_pattern_match(self, validator):
        """Test pattern match"""
        pattern = re.compile(r"^\d{3}-\d{2}-\d{4}$")
        is_valid, error = validator.validate_pattern("123-45-6789", pattern)
        assert is_valid is True
        assert error is None

    def test_validate_pattern_no_match(self, validator):
        """Test pattern no match"""
        pattern = re.compile(r"^\d{3}-\d{2}-\d{4}$")
        is_valid, error = validator.validate_pattern("invalid", pattern, "Custom error message")
        assert is_valid is False
        assert error == "Custom error message"

    def test_validate_pattern_invalid_type(self, validator):
        """Test pattern validation with non-string"""
        pattern = re.compile(r"^\d+$")
        is_valid, error = validator.validate_pattern(123, pattern)
        assert is_valid is False
        assert "must be a string" in error


# ============================================================================
# EnhancedValidator Enum Tests (5 tests)
# ============================================================================


class TestEnhancedValidatorEnum:
    """Test enum validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_enum_valid(self, validator):
        """Test value in allowed values"""
        is_valid, error = validator.validate_enum("red", ["red", "green", "blue"])
        assert is_valid is True
        assert error is None

    def test_validate_enum_invalid(self, validator):
        """Test value not in allowed values"""
        is_valid, error = validator.validate_enum("yellow", ["red", "green", "blue"])
        assert is_valid is False
        assert "must be one of" in error

    def test_validate_enum_case_insensitive(self, validator):
        """Test case-insensitive enum validation"""
        is_valid, error = validator.validate_enum("RED", ["red", "green", "blue"], case_sensitive=False)
        assert is_valid is True

    def test_validate_enum_case_sensitive(self, validator):
        """Test case-sensitive enum validation"""
        is_valid, error = validator.validate_enum("RED", ["red", "green", "blue"], case_sensitive=True)
        assert is_valid is False

    def test_validate_enum_numeric(self, validator):
        """Test enum with numeric values"""
        is_valid, error = validator.validate_enum(2, [1, 2, 3])
        assert is_valid is True


# ============================================================================
# EnhancedValidator Cross-Field Tests (8 tests)
# ============================================================================


class TestEnhancedValidatorCrossField:
    """Test cross-field validation"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_validate_cross_field_eq(self, validator):
        """Test equal comparison"""
        data = {"password": "test123", "confirm_password": "test123"}
        is_valid, error = validator.validate_cross_field(data, "password", "confirm_password", "eq")
        assert is_valid is True
        assert error is None

    def test_validate_cross_field_ne(self, validator):
        """Test not equal comparison"""
        data = {"field1": "value1", "field2": "value2"}
        is_valid, error = validator.validate_cross_field(data, "field1", "field2", "ne")
        assert is_valid is True

    def test_validate_cross_field_lt(self, validator):
        """Test less than comparison"""
        data = {"start_date": 1, "end_date": 2}
        is_valid, error = validator.validate_cross_field(data, "start_date", "end_date", "lt")
        assert is_valid is True

    def test_validate_cross_field_gt(self, validator):
        """Test greater than comparison"""
        data = {"max": 100, "min": 50}
        is_valid, error = validator.validate_cross_field(data, "max", "min", "gt")
        assert is_valid is True

    def test_validate_cross_field_missing_field(self, validator):
        """Test with missing field"""
        data = {"field1": "value1"}
        is_valid, error = validator.validate_cross_field(data, "field1", "field2", "eq")
        assert is_valid is False
        assert "must both be present" in error

    def test_validate_cross_field_custom_error(self, validator):
        """Test with custom error message"""
        data = {"password": "test123", "confirm_password": "different"}
        is_valid, error = validator.validate_cross_field(
            data, "password", "confirm_password", "eq", "Passwords must match"
        )
        assert is_valid is False
        assert error == "Passwords must match"

    def test_validate_cross_field_unknown_comparison(self, validator):
        """Test with unknown comparison"""
        data = {"field1": 1, "field2": 2}
        is_valid, error = validator.validate_cross_field(data, "field1", "field2", "unknown")
        assert is_valid is False
        assert "Unknown comparison" in error

    def test_validate_cross_field_comparison_error(self, validator):
        """Test comparison that raises exception"""
        data = {"field1": "string", "field2": 123}
        is_valid, error = validator.validate_cross_field(data, "field1", "field2", "lt")
        assert is_valid is False
        assert "Cannot compare" in error


# ============================================================================
# TemplateValidator Tests (30+ tests)
# ============================================================================


class TestTemplateValidatorInit:
    """Test TemplateValidator initialization"""

    def test_init(self):
        """Test TemplateValidator initialization"""
        validator = TemplateValidator()
        assert hasattr(validator, "enhanced")
        assert isinstance(validator.enhanced, EnhancedValidator)


class TestTemplateValidatorVariable:
    """Test variable validation"""

    @pytest.fixture
    def validator(self):
        return TemplateValidator()

    def test_validate_variable_required_missing(self, validator):
        """Test required variable with no value"""
        var = Variable(name="test_var", required=True, value=None)
        result = validator.validate_variable(var)
        assert result.is_valid is False
        assert "test_var" in result.missing_required

    def test_validate_variable_optional_missing(self, validator):
        """Test optional variable with no value"""
        var = Variable(name="test_var", required=False, value=None)
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_date_valid(self, validator):
        """Test valid date variable"""
        var = Variable(name="test_date", data_type="date", value="01.01.2024")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_date_invalid(self, validator):
        """Test invalid date variable"""
        var = Variable(name="test_date", data_type="date", value="invalid-date")
        result = validator.validate_variable(var)
        assert result.is_valid is False
        assert "test_date" in result.invalid_values

    def test_validate_variable_email_valid(self, validator):
        """Test valid email variable"""
        var = Variable(name="test_email", data_type="email", value="test@example.com")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_email_invalid(self, validator):
        """Test invalid email variable"""
        var = Variable(name="test_email", data_type="email", value="invalid-email")
        result = validator.validate_variable(var)
        assert result.is_valid is False

    def test_validate_variable_phone_valid(self, validator):
        """Test valid phone variable"""
        var = Variable(name="test_phone", data_type="phone", value="+49 123 456789")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_phone_invalid(self, validator):
        """Test invalid phone variable"""
        var = Variable(name="test_phone", data_type="phone", value="123")
        result = validator.validate_variable(var)
        assert result.is_valid is False

    def test_validate_variable_number_valid(self, validator):
        """Test valid number variable"""
        var = Variable(name="test_number", data_type="number", value="123.45")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_number_invalid(self, validator):
        """Test invalid number variable"""
        var = Variable(name="test_number", data_type="number", value="not-a-number")
        result = validator.validate_variable(var)
        assert result.is_valid is False

    def test_validate_variable_percentage_valid(self, validator):
        """Test valid percentage variable"""
        var = Variable(name="test_percent", data_type="percentage", value="50")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_percentage_invalid(self, validator):
        """Test invalid percentage variable (out of range)"""
        var = Variable(name="test_percent", data_type="percentage", value="150")
        result = validator.validate_variable(var)
        assert result.is_valid is False

    def test_validate_variable_url(self, validator):
        """Test URL variable"""
        var = Variable(name="test_url", data_type="url", value="https://example.com")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_iban(self, validator):
        """Test IBAN variable"""
        var = Variable(name="test_iban", data_type="iban", value="DE89370400440532013000")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_postal_code(self, validator):
        """Test postal code variable"""
        var = Variable(name="test_postal", data_type="postal_code", value="12345")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_ip_address(self, validator):
        """Test IP address variable"""
        var = Variable(name="test_ip", data_type="ip_address", value="192.168.1.1")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_uuid(self, validator):
        """Test UUID variable"""
        var = Variable(name="test_uuid", data_type="uuid", value="550e8400-e29b-41d4-a716-446655440000")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_hex_color(self, validator):
        """Test hex color variable"""
        var = Variable(name="test_color", data_type="hex_color", value="#FF0000")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_credit_card(self, validator):
        """Test credit card variable"""
        var = Variable(name="test_card", data_type="credit_card", value="4532015112830366")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_tax_id(self, validator):
        """Test tax ID variable"""
        var = Variable(name="test_tax", data_type="tax_id", value="12345678901")
        result = validator.validate_variable(var)
        assert result.is_valid is True

    def test_validate_variable_vat_id(self, validator):
        """Test VAT ID variable"""
        var = Variable(name="test_vat", data_type="vat_id", value="DE123456789")
        result = validator.validate_variable(var)
        assert result.is_valid is True


class TestTemplateValidatorConfig:
    """Test configuration validation"""

    @pytest.fixture
    def validator(self):
        return TemplateValidator()

    def test_validate_config_valid(self, validator):
        """Test valid configuration"""
        config = {
            "basic_info": {"service_name": "Test Service", "target_group": "Test Group", "region": "Test Region"},
            "financial": {"brutto_rate": "100.00"},
        }

        result = validator.validate_config(config)
        assert result.is_valid is True

    def test_validate_config_missing_required(self, validator):
        """Test configuration with missing required fields"""
        config = {"basic_info": {"service_name": "Test Service"}}

        result = validator.validate_config(config)
        assert result.is_valid is False
        assert len(result.missing_required) > 0

    def test_validate_config_invalid_brutto_rate(self, validator):
        """Test configuration with invalid brutto rate"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "-100"},
        }

        result = validator.validate_config(config)
        assert result.is_valid is False

    def test_validate_config_invalid_insurance_rates(self, validator):
        """Test configuration with invalid insurance rates"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "100", "insurance_rates": {"rv": "150"}},  # >100%
        }

        result = validator.validate_config(config)
        assert result.is_valid is False

    def test_validate_config_invalid_umlages(self, validator):
        """Test configuration with invalid umlages"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "100", "umlages": {"u1": "-5"}},  # <0%
        }

        result = validator.validate_config(config)
        assert result.is_valid is False

    def test_validate_config_invalid_region_coefficient(self, validator):
        """Test configuration with invalid region coefficient"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "100", "region_coefficient": "5"},  # >3
        }

        result = validator.validate_config(config)
        assert result.is_valid is False

    def test_validate_config_conflicting_settings(self, validator):
        """Test configuration with conflicting system settings"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "100"},
            "system_settings": {"use_umlages": True, "use_vacation_reserve": True},
        }

        result = validator.validate_config(config)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_config_invalid_surcharge_base(self, validator):
        """Test configuration with invalid surcharge base"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "100"},
            "system_settings": {"surcharge_base": "invalid"},
        }

        result = validator.validate_config(config)
        assert result.is_valid is False

    def test_validate_config_invalid_service_type(self, validator):
        """Test configuration with invalid service type"""
        config = {
            "basic_info": {"service_name": "Test", "target_group": "Test", "region": "Test"},
            "financial": {"brutto_rate": "100"},
            "system_settings": {"service_type": "invalid"},
        }

        result = validator.validate_config(config)
        assert result.is_valid is False


class TestTemplateValidatorFilledTemplate:
    """Test filled template validation"""

    @pytest.fixture
    def validator(self):
        return TemplateValidator()

    def test_validate_filled_template_all_valid(self, validator):
        """Test filled template with all valid variables"""
        variables = [
            Variable(name="var1", data_type="text", value="Test"),
            Variable(name="var2", data_type="number", value="123"),
            Variable(name="var3", data_type="email", value="test@example.com"),
        ]

        result = validator.validate_filled_template(variables)
        assert result.is_valid is True

    def test_validate_filled_template_some_invalid(self, validator):
        """Test filled template with some invalid variables"""
        variables = [
            Variable(name="var1", data_type="email", value="invalid-email"),
            Variable(name="var2", data_type="number", value="not-a-number"),
            Variable(name="var3", required=True, value=None),
        ]

        result = validator.validate_filled_template(variables)
        assert result.is_valid is False
        assert len(result.invalid_values) >= 2
        assert len(result.missing_required) >= 1

    def test_validate_filled_template_empty_list(self, validator):
        """Test filled template with empty variable list"""
        result = validator.validate_filled_template([])
        assert result.is_valid is True


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


class TestValidatorEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def validator(self):
        return EnhancedValidator()

    def test_none_values(self, validator):
        """Test validators handle None values correctly"""
        assert validator.validate_url(None) is False
        assert validator.validate_iban(None) is False
        assert validator.validate_uuid(None) is False

    def test_empty_string_values(self, validator):
        """Test validators handle empty strings correctly"""
        assert validator.validate_url("") is False
        assert validator.validate_iban("") is False
        assert validator.validate_bic("") is False

    def test_whitespace_handling(self, validator):
        """Test validators handle whitespace correctly"""
        # IBAN should handle spaces
        assert validator.validate_iban("DE89 3704 0044 0532 0130 00") is True
        # BIC should handle spaces
        assert validator.validate_bic("DEUT DEFF") is True

    def test_case_handling(self, validator):
        """Test validators handle case correctly"""
        # URLs are case-insensitive for protocol
        assert validator.validate_url("HTTP://EXAMPLE.COM") is True
        # Domains are case-insensitive
        assert validator.validate_domain("EXAMPLE.COM") is True

    def test_special_characters(self, validator):
        """Test validators handle special characters"""
        # Username with special chars when allowed
        is_valid, _ = validator.validate_username("user.name-123", allow_special=True)
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
