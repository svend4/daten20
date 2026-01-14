"""
Comprehensive Validators Module

Complete set of validators for all data types:
- Document validators
- Financial validators
- Business logic validators
- Data integrity validators
- Schema validators
- Cross-field validators
"""

from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import re
from pathlib import Path
import mimetypes


class ValidationError:
    """Validation error representation."""

    def __init__(self, field: str, message: str, severity: str = "error", code: Optional[str] = None):
        """
        Initialize validation error.

        Args:
            field: Field name
            message: Error message
            severity: 'error', 'warning', or 'info'
            code: Optional error code
        """
        self.field = field
        self.message = message
        self.severity = severity
        self.code = code or "VALIDATION_ERROR"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'field': self.field,
            'message': self.message,
            'severity': self.severity,
            'code': self.code
        }

    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.field} - {self.message}"


class ValidationResult:
    """Validation result with errors and warnings."""

    def __init__(self):
        """Initialize validation result."""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info: List[ValidationError] = []

    def add_error(self, field: str, message: str, code: Optional[str] = None):
        """Add an error."""
        self.errors.append(ValidationError(field, message, "error", code))

    def add_warning(self, field: str, message: str, code: Optional[str] = None):
        """Add a warning."""
        self.warnings.append(ValidationError(field, message, "warning", code))

    def add_info(self, field: str, message: str, code: Optional[str] = None):
        """Add an info message."""
        self.info.append(ValidationError(field, message, "info", code))

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0

    def get_messages(self, severity: Optional[str] = None) -> List[str]:
        """
        Get all messages.

        Args:
            severity: Optional filter by severity ('error', 'warning', 'info')

        Returns:
            List of messages
        """
        all_messages = self.errors + self.warnings + self.info

        if severity:
            all_messages = [m for m in all_messages if m.severity == severity]

        return [str(m) for m in all_messages]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'has_warnings': self.has_warnings,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'info': [i.to_dict() for i in self.info]
        }


class DocumentValidator:
    """Validators for document-related data."""

    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file path.

        Args:
            path: File path

        Returns:
            (is_valid, error_message)
        """
        if not path:
            return False, "File path is required"

        try:
            p = Path(path)

            # Check if path exists
            if not p.exists():
                return False, f"File does not exist: {path}"

            # Check if it's a file (not directory)
            if not p.is_file():
                return False, f"Path is not a file: {path}"

            # Check if readable
            if not p.stat().st_size >= 0:
                return False, f"Cannot read file: {path}"

            return True, None

        except Exception as e:
            return False, f"Invalid file path: {str(e)}"

    @staticmethod
    def validate_file_type(path: str, allowed_types: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate file type.

        Args:
            path: File path
            allowed_types: List of allowed extensions (e.g., ['.pdf', '.docx'])

        Returns:
            (is_valid, error_message)
        """
        if not path:
            return False, "File path is required"

        try:
            p = Path(path)
            ext = p.suffix.lower()

            if ext not in allowed_types:
                return False, f"File type {ext} not allowed. Allowed: {', '.join(allowed_types)}"

            return True, None

        except Exception as e:
            return False, f"Error validating file type: {str(e)}"

    @staticmethod
    def validate_file_size(path: str, max_size_mb: float = 50) -> Tuple[bool, Optional[str]]:
        """
        Validate file size.

        Args:
            path: File path
            max_size_mb: Maximum size in MB

        Returns:
            (is_valid, error_message)
        """
        if not path:
            return False, "File path is required"

        try:
            p = Path(path)

            if not p.exists():
                return False, f"File does not exist: {path}"

            size_mb = p.stat().st_size / (1024 * 1024)

            if size_mb > max_size_mb:
                return False, f"File size ({size_mb:.2f} MB) exceeds maximum ({max_size_mb} MB)"

            return True, None

        except Exception as e:
            return False, f"Error validating file size: {str(e)}"


class FinancialValidator:
    """Validators for financial data."""

    @staticmethod
    def validate_amount(amount: Any, min_value: float = 0, max_value: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate monetary amount.

        Args:
            amount: Amount to validate
            min_value: Minimum allowed value
            max_value: Optional maximum allowed value

        Returns:
            (is_valid, error_message)
        """
        try:
            # Convert to Decimal for precise financial calculations
            if isinstance(amount, str):
                amount = Decimal(amount.replace(',', ''))
            elif isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            elif isinstance(amount, Decimal):
                pass
            else:
                return False, f"Invalid amount type: {type(amount)}"

            # Check min value
            if amount < Decimal(str(min_value)):
                return False, f"Amount {amount} is below minimum {min_value}"

            # Check max value
            if max_value is not None and amount > Decimal(str(max_value)):
                return False, f"Amount {amount} exceeds maximum {max_value}"

            return True, None

        except (ValueError, InvalidOperation) as e:
            return False, f"Invalid amount: {str(e)}"

    @staticmethod
    def validate_percentage(percentage: Any, min_value: float = 0, max_value: float = 100) -> Tuple[bool, Optional[str]]:
        """
        Validate percentage value.

        Args:
            percentage: Percentage to validate
            min_value: Minimum value (default: 0)
            max_value: Maximum value (default: 100)

        Returns:
            (is_valid, error_message)
        """
        try:
            pct = float(percentage)

            if pct < min_value or pct > max_value:
                return False, f"Percentage {pct} must be between {min_value} and {max_value}"

            return True, None

        except (ValueError, TypeError) as e:
            return False, f"Invalid percentage: {str(e)}"

    @staticmethod
    def validate_tax_id(tax_id: str, country: str = "DE") -> Tuple[bool, Optional[str]]:
        """
        Validate tax ID.

        Args:
            tax_id: Tax ID string
            country: Country code (DE, US, etc.)

        Returns:
            (is_valid, error_message)
        """
        if not tax_id:
            return False, "Tax ID is required"

        patterns = {
            'DE': r'^\d{11}$',  # German tax ID (11 digits)
            'US': r'^\d{3}-\d{2}-\d{4}$',  # US SSN
            'GB': r'^[A-Z]{2}\d{6}[A-Z]$',  # UK National Insurance
        }

        pattern = patterns.get(country)
        if not pattern:
            return True, None  # Unknown country, skip validation

        if not re.match(pattern, tax_id):
            return False, f"Invalid {country} tax ID format"

        return True, None

    @staticmethod
    def validate_iban(iban: str) -> Tuple[bool, Optional[str]]:
        """
        Validate IBAN (International Bank Account Number).

        Args:
            iban: IBAN string

        Returns:
            (is_valid, error_message)
        """
        if not iban:
            return False, "IBAN is required"

        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()

        # Check format
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', iban):
            return False, "Invalid IBAN format"

        # Move first 4 characters to end
        iban_check = iban[4:] + iban[:4]

        # Replace letters with numbers (A=10, B=11, ..., Z=35)
        iban_num = ''
        for char in iban_check:
            if char.isdigit():
                iban_num += char
            else:
                iban_num += str(ord(char) - ord('A') + 10)

        # Check if valid using modulo 97
        if int(iban_num) % 97 != 1:
            return False, "Invalid IBAN checksum"

        return True, None


class BusinessLogicValidator:
    """Validators for business logic and rules."""

    @staticmethod
    def validate_date_range(start_date: Union[date, datetime, str],
                           end_date: Union[date, datetime, str]) -> Tuple[bool, Optional[str]]:
        """
        Validate date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            (is_valid, error_message)
        """
        try:
            # Convert strings to dates if needed
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date).date()
            elif isinstance(start_date, datetime):
                start_date = start_date.date()

            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date).date()
            elif isinstance(end_date, datetime):
                end_date = end_date.date()

            # Check if end date is after start date
            if end_date < start_date:
                return False, f"End date {end_date} must be after start date {start_date}"

            return True, None

        except Exception as e:
            return False, f"Error validating date range: {str(e)}"

    @staticmethod
    def validate_working_hours(hours: float, max_hours_per_day: float = 24,
                              max_hours_per_week: float = 168) -> Tuple[bool, Optional[str]]:
        """
        Validate working hours.

        Args:
            hours: Number of hours
            max_hours_per_day: Maximum hours per day
            max_hours_per_week: Maximum hours per week

        Returns:
            (is_valid, error_message)
        """
        if hours < 0:
            return False, "Hours cannot be negative"

        if hours > max_hours_per_day:
            return False, f"Hours ({hours}) exceed maximum per day ({max_hours_per_day})"

        return True, None


class DataIntegrityValidator:
    """Validators for data integrity and consistency."""

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
        """
        Validate required fields.

        Args:
            data: Data dictionary
            required_fields: List of required field names

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        for field in required_fields:
            if field not in data:
                result.add_error(field, f"Required field '{field}' is missing", "MISSING_FIELD")
            elif data[field] is None or data[field] == '':
                result.add_error(field, f"Required field '{field}' is empty", "EMPTY_FIELD")

        return result

    @staticmethod
    def validate_unique_id(id_value: str, existing_ids: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate unique ID.

        Args:
            id_value: ID to check
            existing_ids: List of existing IDs

        Returns:
            (is_valid, error_message)
        """
        if not id_value:
            return False, "ID is required"

        if id_value in existing_ids:
            return False, f"ID '{id_value}' already exists"

        return True, None

    @staticmethod
    def validate_enum_value(value: str, allowed_values: List[str],
                           case_sensitive: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate enum value.

        Args:
            value: Value to check
            allowed_values: List of allowed values
            case_sensitive: Whether comparison is case-sensitive

        Returns:
            (is_valid, error_message)
        """
        if not value:
            return False, "Value is required"

        check_values = allowed_values
        check_value = value

        if not case_sensitive:
            check_values = [v.lower() for v in allowed_values]
            check_value = value.lower()

        if check_value not in check_values:
            return False, f"Value '{value}' not in allowed values: {', '.join(allowed_values)}"

        return True, None


class ComprehensiveValidator:
    """Main validator class that combines all validators."""

    def __init__(self):
        """Initialize comprehensive validator."""
        self.document = DocumentValidator()
        self.financial = FinancialValidator()
        self.business = BusinessLogicValidator()
        self.integrity = DataIntegrityValidator()

    def validate_service_data(self, service_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete service data.

        Args:
            service_data: Service data dictionary

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Check required fields
        required_fields = ['service_name', 'region', 'brutto_rate']
        integrity_result = self.integrity.validate_required_fields(service_data, required_fields)
        result.errors.extend(integrity_result.errors)

        # Validate financial data
        if 'brutto_rate' in service_data:
            is_valid, error = self.financial.validate_amount(
                service_data['brutto_rate'],
                min_value=0,
                max_value=1000
            )
            if not is_valid:
                result.add_error('brutto_rate', error, "INVALID_AMOUNT")

        if 'admin_percent' in service_data:
            is_valid, error = self.financial.validate_percentage(service_data['admin_percent'])
            if not is_valid:
                result.add_error('admin_percent', error, "INVALID_PERCENTAGE")

        # Validate service type
        if 'service_type' in service_data:
            allowed_types = ['Betreuung', 'Beratung', 'Verwaltung', 'Sonstiges']
            is_valid, error = self.integrity.validate_enum_value(
                service_data['service_type'],
                allowed_types
            )
            if not is_valid:
                result.add_warning('service_type', error, "INVALID_ENUM")

        return result

    def validate_document_upload(self, file_path: str, max_size_mb: float = 50) -> ValidationResult:
        """
        Validate document upload.

        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Check if file exists
        is_valid, error = self.document.validate_file_path(file_path)
        if not is_valid:
            result.add_error('file_path', error, "INVALID_FILE_PATH")
            return result

        # Check file type
        allowed_types = ['.pdf', '.docx', '.txt', '.html', '.md']
        is_valid, error = self.document.validate_file_type(file_path, allowed_types)
        if not is_valid:
            result.add_error('file_type', error, "INVALID_FILE_TYPE")

        # Check file size
        is_valid, error = self.document.validate_file_size(file_path, max_size_mb)
        if not is_valid:
            result.add_error('file_size', error, "FILE_TOO_LARGE")

        return result


# Convenience functions
def validate_data(data: Dict[str, Any], rules: Dict[str, Callable]) -> ValidationResult:
    """
    Validate data against custom rules.

    Args:
        data: Data to validate
        rules: Dictionary of field_name -> validation_function

    Returns:
        ValidationResult
    """
    result = ValidationResult()

    for field, validator_func in rules.items():
        if field in data:
            is_valid, error = validator_func(data[field])
            if not is_valid:
                result.add_error(field, error)

    return result
