"""
Enhanced validation utilities for template data and documents

Provides comprehensive validation with:
- Multiple data type validators
- Custom validation rules
- Range and pattern validation
- Cross-field validation
- Detailed error reporting
"""

from typing import Dict, Any, List, Optional, Callable, Pattern
from decimal import Decimal
import re
from ..models.template import ValidationResult, Variable
from ..utils.helpers import (
    validate_date, validate_email, validate_phone,
    validate_required_fields, parse_number
)


class ValidationRule:
    """
    Custom validation rule

    Allows defining custom validation logic with clear error messages
    """

    def __init__(
        self,
        field: str,
        validator: Callable[[Any], bool],
        error_message: str,
        severity: str = "error"
    ):
        """
        Initialize validation rule

        Args:
            field: Field name to validate
            validator: Function that returns True if valid
            error_message: Error message if validation fails
            severity: 'error' or 'warning'
        """
        self.field = field
        self.validator = validator
        self.error_message = error_message
        self.severity = severity

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate value against rule

        Returns:
            (is_valid, error_message)
        """
        try:
            is_valid = self.validator(value)
            return is_valid, None if is_valid else self.error_message
        except Exception as e:
            return False, f"{self.error_message} (Exception: {str(e)})"


class EnhancedValidator:
    """
    Enhanced validator with comprehensive validation capabilities
    """

    # Common regex patterns
    PATTERNS = {
        'url': re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        ),
        'iban': re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$'),
        'postal_code_de': re.compile(r'^\d{5}$'),
        'postal_code_general': re.compile(r'^[A-Z0-9\s-]{3,10}$', re.IGNORECASE),
        'ipv4': re.compile(r'^(\d{1,3}\.){3}\d{1,3}$'),
        'ipv6': re.compile(r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'),
        'uuid': re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        ),
        'hex_color': re.compile(r'^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'),
        'credit_card': re.compile(r'^\d{13,19}$'),
        'tax_id_de': re.compile(r'^\d{11}$'),  # German tax ID
        'vat_id_de': re.compile(r'^DE\d{9}$'),  # German VAT ID
    }

    def __init__(self):
        """Initialize enhanced validator"""
        self.custom_rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """Add custom validation rule"""
        self.custom_rules.append(rule)

    def validate_url(self, value: str) -> bool:
        """Validate URL format"""
        if not value:
            return False
        return bool(self.PATTERNS['url'].match(value))

    def validate_iban(self, value: str) -> bool:
        """Validate IBAN format"""
        if not value:
            return False
        # Remove spaces
        iban = value.replace(' ', '').upper()
        return bool(self.PATTERNS['iban'].match(iban))

    def validate_postal_code(self, value: str, country: str = 'DE') -> bool:
        """Validate postal code"""
        if not value:
            return False
        if country == 'DE':
            return bool(self.PATTERNS['postal_code_de'].match(value))
        return bool(self.PATTERNS['postal_code_general'].match(value))

    def validate_ip_address(self, value: str, version: int = 4) -> bool:
        """Validate IP address"""
        if not value:
            return False
        if version == 4:
            return bool(self.PATTERNS['ipv4'].match(value))
        elif version == 6:
            return bool(self.PATTERNS['ipv6'].match(value))
        return False

    def validate_uuid(self, value: str) -> bool:
        """Validate UUID format"""
        if not value:
            return False
        return bool(self.PATTERNS['uuid'].match(value))

    def validate_hex_color(self, value: str) -> bool:
        """Validate hex color code"""
        if not value:
            return False
        return bool(self.PATTERNS['hex_color'].match(value))

    def validate_credit_card(self, value: str) -> bool:
        """Validate credit card number format (Luhn algorithm)"""
        if not value:
            return False

        # Remove spaces and dashes
        number = value.replace(' ', '').replace('-', '')

        # Check format
        if not self.PATTERNS['credit_card'].match(number):
            return False

        # Luhn algorithm
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        return luhn_checksum(number) == 0

    def validate_tax_id(self, value: str, country: str = 'DE') -> bool:
        """Validate tax identification number"""
        if not value:
            return False
        if country == 'DE':
            return bool(self.PATTERNS['tax_id_de'].match(value))
        return False

    def validate_vat_id(self, value: str, country: str = 'DE') -> bool:
        """Validate VAT identification number"""
        if not value:
            return False
        if country == 'DE':
            return bool(self.PATTERNS['vat_id_de'].match(value))
        return False

    def validate_range(
        self,
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate numeric value is within range

        Returns:
            (is_valid, error_message)
        """
        try:
            num = float(value)

            if min_value is not None and num < min_value:
                return False, f"Value must be at least {min_value}"

            if max_value is not None and num > max_value:
                return False, f"Value must be at most {max_value}"

            return True, None
        except (ValueError, TypeError):
            return False, "Value must be a number"

    def validate_length(
        self,
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate string length

        Returns:
            (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, "Value must be a string"

        length = len(value)

        if min_length is not None and length < min_length:
            return False, f"Length must be at least {min_length} characters"

        if max_length is not None and length > max_length:
            return False, f"Length must be at most {max_length} characters"

        return True, None

    def validate_pattern(
        self,
        value: str,
        pattern: Pattern[str],
        error_message: str = "Value does not match required pattern"
    ) -> tuple[bool, Optional[str]]:
        """
        Validate value matches regex pattern

        Returns:
            (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, "Value must be a string"

        if pattern.match(value):
            return True, None

        return False, error_message

    def validate_enum(
        self,
        value: Any,
        allowed_values: List[Any],
        case_sensitive: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Validate value is one of allowed values

        Returns:
            (is_valid, error_message)
        """
        if case_sensitive:
            if value in allowed_values:
                return True, None
        else:
            # Case-insensitive comparison for strings
            if isinstance(value, str):
                value_lower = value.lower()
                allowed_lower = [str(v).lower() for v in allowed_values]
                if value_lower in allowed_lower:
                    return True, None
            elif value in allowed_values:
                return True, None

        allowed_str = ', '.join(str(v) for v in allowed_values)
        return False, f"Value must be one of: {allowed_str}"

    def validate_cross_field(
        self,
        data: Dict[str, Any],
        field1: str,
        field2: str,
        comparison: str,
        error_message: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate relationship between two fields

        Args:
            data: Dictionary containing both fields
            field1: First field name
            field2: Second field name
            comparison: 'eq', 'ne', 'lt', 'le', 'gt', 'ge'
            error_message: Custom error message

        Returns:
            (is_valid, error_message)
        """
        if field1 not in data or field2 not in data:
            return False, f"Fields {field1} and {field2} must both be present"

        val1 = data[field1]
        val2 = data[field2]

        try:
            if comparison == 'eq':
                is_valid = val1 == val2
                default_msg = f"{field1} must equal {field2}"
            elif comparison == 'ne':
                is_valid = val1 != val2
                default_msg = f"{field1} must not equal {field2}"
            elif comparison == 'lt':
                is_valid = val1 < val2
                default_msg = f"{field1} must be less than {field2}"
            elif comparison == 'le':
                is_valid = val1 <= val2
                default_msg = f"{field1} must be less than or equal to {field2}"
            elif comparison == 'gt':
                is_valid = val1 > val2
                default_msg = f"{field1} must be greater than {field2}"
            elif comparison == 'ge':
                is_valid = val1 >= val2
                default_msg = f"{field1} must be greater than or equal to {field2}"
            else:
                return False, f"Unknown comparison: {comparison}"

            if is_valid:
                return True, None

            return False, error_message or default_msg

        except Exception as e:
            return False, f"Cannot compare {field1} and {field2}: {str(e)}"


class TemplateValidator:
    """Validator for template data with enhanced capabilities"""

    def __init__(self):
        """Initialize validator"""
        self.enhanced = EnhancedValidator()

    def validate_variable(self, variable: Variable) -> ValidationResult:
        """
        Validate a single variable with enhanced validation

        Args:
            variable: Variable to validate

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Check if required variable has value
        if variable.required and variable.value is None:
            result.add_missing(variable.name)
            return result

        # If no value, skip type validation
        if variable.value is None:
            return result

        # Validate based on data type
        value = variable.value

        if variable.data_type == "date":
            if not validate_date(value):
                result.add_invalid(variable.name, "Invalid date format. Use DD.MM.YYYY")

        elif variable.data_type == "email":
            if not validate_email(value):
                result.add_invalid(variable.name, "Invalid email address")

        elif variable.data_type == "phone":
            if not validate_phone(value):
                result.add_invalid(variable.name, "Invalid phone number")

        elif variable.data_type == "number":
            if parse_number(value) is None:
                result.add_invalid(variable.name, "Invalid number format")

        elif variable.data_type == "percentage":
            num = parse_number(value)
            if num is None or num < 0 or num > 100:
                result.add_invalid(variable.name, "Invalid percentage (must be 0-100)")

        # Enhanced validators
        elif variable.data_type == "url":
            if not self.enhanced.validate_url(str(value)):
                result.add_invalid(variable.name, "Invalid URL format")

        elif variable.data_type == "iban":
            if not self.enhanced.validate_iban(str(value)):
                result.add_invalid(variable.name, "Invalid IBAN format")

        elif variable.data_type == "postal_code":
            if not self.enhanced.validate_postal_code(str(value)):
                result.add_invalid(variable.name, "Invalid postal code")

        elif variable.data_type == "ip_address":
            if not self.enhanced.validate_ip_address(str(value)):
                result.add_invalid(variable.name, "Invalid IP address")

        elif variable.data_type == "uuid":
            if not self.enhanced.validate_uuid(str(value)):
                result.add_invalid(variable.name, "Invalid UUID format")

        elif variable.data_type == "hex_color":
            if not self.enhanced.validate_hex_color(str(value)):
                result.add_invalid(variable.name, "Invalid hex color code")

        elif variable.data_type == "credit_card":
            if not self.enhanced.validate_credit_card(str(value)):
                result.add_invalid(variable.name, "Invalid credit card number")

        elif variable.data_type == "tax_id":
            if not self.enhanced.validate_tax_id(str(value)):
                result.add_invalid(variable.name, "Invalid tax identification number")

        elif variable.data_type == "vat_id":
            if not self.enhanced.validate_vat_id(str(value)):
                result.add_invalid(variable.name, "Invalid VAT identification number")

        return result

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate service configuration

        Args:
            config: Configuration dictionary

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Required fields
        required = [
            "basic_info.service_name",
            "basic_info.target_group",
            "basic_info.region",
            "financial.brutto_rate"
        ]

        missing = validate_required_fields(config, required)
        for field in missing:
            result.add_missing(field)

        # Validate financial data
        if "financial" in config:
            self._validate_financial(config["financial"], result)

        # Validate system settings
        if "system_settings" in config:
            self._validate_system_settings(config["system_settings"], result)

        return result

    def _validate_financial(self, financial: Dict[str, Any], result: ValidationResult) -> None:
        """Validate financial parameters"""
        # Check brutto_rate
        if "brutto_rate" in financial:
            rate = parse_number(str(financial["brutto_rate"]))
            if rate is None or rate <= 0:
                result.add_invalid("financial.brutto_rate", "Must be a positive number")

        # Validate insurance rates
        if "insurance_rates" in financial:
            for key, value in financial["insurance_rates"].items():
                num = parse_number(str(value))
                if num is None or num < 0 or num > 100:
                    result.add_invalid(f"financial.insurance_rates.{key}",
                                       "Must be a percentage between 0 and 100")

        # Validate umlages
        if "umlages" in financial:
            for key, value in financial["umlages"].items():
                num = parse_number(str(value))
                if num is None or num < 0 or num > 100:
                    result.add_invalid(f"financial.umlages.{key}",
                                       "Must be a percentage between 0 and 100")

        # Validate region coefficient
        if "region_coefficient" in financial:
            coef = parse_number(str(financial["region_coefficient"]))
            if coef is None or coef <= 0 or coef > 3:
                result.add_invalid("financial.region_coefficient",
                                   "Must be between 0 and 3")

    def _validate_system_settings(self, settings: Dict[str, Any], result: ValidationResult) -> None:
        """Validate system settings"""
        # Check umlages vs vacation reserve
        use_umlages = settings.get("use_umlages", True)
        use_reserve = settings.get("use_vacation_reserve", False)

        if use_umlages and use_reserve:
            result.add_error("Cannot use both umlages and vacation reserve simultaneously")

        # Check surcharge base
        valid_bases = ["full_cost", "brutto_only"]
        surcharge_base = settings.get("surcharge_base", "full_cost")
        if surcharge_base not in valid_bases:
            result.add_invalid("system_settings.surcharge_base",
                               f"Must be one of: {', '.join(valid_bases)}")

        # Check service type
        valid_types = ["domestic", "social", "medical", "professional", "educational"]
        service_type = settings.get("service_type", "social")
        if service_type not in valid_types:
            result.add_invalid("system_settings.service_type",
                               f"Must be one of: {', '.join(valid_types)}")

    def validate_filled_template(self, variables: List[Variable]) -> ValidationResult:
        """
        Validate filled template

        Args:
            variables: List of all variables

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        for var in variables:
            var_result = self.validate_variable(var)

            # Merge results
            result.errors.extend(var_result.errors)
            result.warnings.extend(var_result.warnings)
            result.missing_required.extend(var_result.missing_required)
            result.invalid_values.update(var_result.invalid_values)

            if not var_result.is_valid:
                result.is_valid = False

        return result

# Alias for backward compatibility
DocumentValidator = TemplateValidator
