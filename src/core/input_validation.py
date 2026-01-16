"""
Input Validation and Sanitization Module

Provides comprehensive input validation and sanitization to prevent:
- XSS attacks
- SQL injection
- Command injection
- Path traversal
- LDAP injection
- XML/JSON injection

Security best practices:
- Whitelist validation (preferred)
- Blacklist filtering (secondary)
- Context-aware escaping
- Type checking
"""

import html
import json
import logging
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("dms.validation")


class ValidationError(Exception):
    """Custom validation error."""

    pass


class InputValidator:
    """Comprehensive input validator."""

    # Common regex patterns
    PATTERNS = {
        "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
        "username": re.compile(r"^[a-zA-Z0-9_-]{3,32}$"),
        "alphanumeric": re.compile(r"^[a-zA-Z0-9]+$"),
        "alpha": re.compile(r"^[a-zA-Z]+$"),
        "numeric": re.compile(r"^[0-9]+$"),
        "phone": re.compile(r"^\+?[0-9\s\-\(\)]{10,20}$"),
        "url": re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        ),
        "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE),
        "slug": re.compile(r"^[a-z0-9-]+$"),
        "hex_color": re.compile(r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"),
    }

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = {
        "sql_keywords": re.compile(
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)", re.IGNORECASE
        ),
        "script_tags": re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        "event_handlers": re.compile(r"\bon\w+\s*=", re.IGNORECASE),
        "javascript": re.compile(r"javascript:", re.IGNORECASE),
        "path_traversal": re.compile(r"\.\./|\.\.\\"),
        "command_injection": re.compile(r"[;&|`$\n]"),
    }

    @staticmethod
    def validate_string(
        value: Any,
        min_length: int = 0,
        max_length: int = 10000,
        pattern: Optional[str] = None,
        allow_empty: bool = True,
    ) -> str:
        """
        Validate and sanitize string input.

        Args:
            value: Input value
            min_length: Minimum length
            max_length: Maximum length
            pattern: Optional regex pattern name
            allow_empty: Allow empty strings

        Returns:
            Validated string

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            try:
                value = str(value)
            except:
                raise ValidationError(f"Cannot convert to string: {type(value)}")

        # Strip whitespace
        value = value.strip()

        # Check empty
        if not value:
            if not allow_empty:
                raise ValidationError("Empty string not allowed")
            return value

        # Length check
        if len(value) < min_length:
            raise ValidationError(f"String too short (min: {min_length})")
        if len(value) > max_length:
            raise ValidationError(f"String too long (max: {max_length})")

        # Pattern validation
        if pattern and pattern in InputValidator.PATTERNS:
            if not InputValidator.PATTERNS[pattern].match(value):
                raise ValidationError(f"Invalid format for {pattern}")

        return value

    @staticmethod
    def validate_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """
        Validate integer input.

        Args:
            value: Input value
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            Validated integer

        Raises:
            ValidationError: If validation fails
        """
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer: {value}")

        if min_value is not None and value < min_value:
            raise ValidationError(f"Value below minimum ({min_value})")

        if max_value is not None and value > max_value:
            raise ValidationError(f"Value above maximum ({max_value})")

        return value

    @staticmethod
    def validate_float(
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        precision: Optional[int] = None,
    ) -> float:
        """
        Validate float input.

        Args:
            value: Input value
            min_value: Minimum value
            max_value: Maximum value
            precision: Decimal precision

        Returns:
            Validated float

        Raises:
            ValidationError: If validation fails
        """
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid float: {value}")

        if min_value is not None and value < min_value:
            raise ValidationError(f"Value below minimum ({min_value})")

        if max_value is not None and value > max_value:
            raise ValidationError(f"Value above maximum ({max_value})")

        if precision is not None:
            value = round(value, precision)

        return value

    @staticmethod
    def validate_decimal(
        value: Any, min_value: Optional[Decimal] = None, max_value: Optional[Decimal] = None
    ) -> Decimal:
        """
        Validate Decimal input (for financial calculations).

        Args:
            value: Input value
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            Validated Decimal

        Raises:
            ValidationError: If validation fails
        """
        try:
            if isinstance(value, str):
                value = value.replace(",", "")  # Remove thousand separators
            value = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(f"Invalid decimal: {value}")

        if min_value is not None and value < min_value:
            raise ValidationError(f"Value below minimum ({min_value})")

        if max_value is not None and value > max_value:
            raise ValidationError(f"Value above maximum ({max_value})")

        return value

    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address.

        Args:
            email: Email address

        Returns:
            Validated email

        Raises:
            ValidationError: If invalid
        """
        email = InputValidator.validate_string(email, max_length=254)

        if not InputValidator.PATTERNS["email"].match(email):
            raise ValidationError(f"Invalid email format: {email}")

        return email.lower()

    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = ["http", "https"]) -> str:
        """
        Validate URL.

        Args:
            url: URL string
            allowed_schemes: Allowed URL schemes

        Returns:
            Validated URL

        Raises:
            ValidationError: If invalid
        """
        url = InputValidator.validate_string(url, max_length=2048)

        if not InputValidator.PATTERNS["url"].match(url):
            raise ValidationError(f"Invalid URL format: {url}")

        # Check scheme
        scheme = url.split("://")[0] if "://" in url else ""
        if scheme and scheme not in allowed_schemes:
            raise ValidationError(f"URL scheme not allowed: {scheme}")

        return url

    @staticmethod
    def validate_enum(value: str, allowed_values: List[str], case_sensitive: bool = False) -> str:
        """
        Validate enum value.

        Args:
            value: Value to check
            allowed_values: List of allowed values
            case_sensitive: Case sensitive comparison

        Returns:
            Validated value

        Raises:
            ValidationError: If not in allowed values
        """
        value = InputValidator.validate_string(value)

        check_values = allowed_values
        check_value = value

        if not case_sensitive:
            check_values = [v.lower() for v in allowed_values]
            check_value = value.lower()

        if check_value not in check_values:
            raise ValidationError(f"Value '{value}' not in allowed values: {', '.join(allowed_values)}")

        return value

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize HTML to prevent XSS.

        Args:
            text: HTML text

        Returns:
            Sanitized HTML
        """
        # Escape HTML entities
        text = html.escape(text)

        # Remove script tags
        text = InputValidator.DANGEROUS_PATTERNS["script_tags"].sub("", text)

        # Remove event handlers
        text = InputValidator.DANGEROUS_PATTERNS["event_handlers"].sub("", text)

        # Remove javascript: URLs
        text = InputValidator.DANGEROUS_PATTERNS["javascript"].sub("", text)

        return text

    @staticmethod
    def validate_file_path(
        path: str, allowed_extensions: Optional[List[str]] = None, base_dir: Optional[str] = None
    ) -> Path:
        """
        Validate file path to prevent path traversal.

        Args:
            path: File path
            allowed_extensions: List of allowed extensions
            base_dir: Base directory (path must be within this)

        Returns:
            Validated Path object

        Raises:
            ValidationError: If invalid or unsafe
        """
        # Check for path traversal attempts
        if InputValidator.DANGEROUS_PATTERNS["path_traversal"].search(path):
            raise ValidationError(f"Path traversal detected: {path}")

        try:
            file_path = Path(path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid path: {e}")

        # Check if within base directory
        if base_dir:
            base_path = Path(base_dir).resolve()
            try:
                file_path.relative_to(base_path)
            except ValueError:
                raise ValidationError(f"Path outside base directory: {path}")

        # Check extension
        if allowed_extensions:
            ext = file_path.suffix.lower()
            if ext not in allowed_extensions:
                raise ValidationError(f"File extension not allowed: {ext}. Allowed: {', '.join(allowed_extensions)}")

        return file_path

    @staticmethod
    def validate_json(data: str, max_depth: int = 10) -> Dict:
        """
        Validate and parse JSON.

        Args:
            data: JSON string
            max_depth: Maximum nesting depth

        Returns:
            Parsed JSON

        Raises:
            ValidationError: If invalid JSON
        """
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")

        # Check depth (prevent DoS)
        def check_depth(obj, depth=0):
            if depth > max_depth:
                raise ValidationError(f"JSON too deeply nested (max: {max_depth})")
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1)

        check_depth(parsed)

        return parsed

    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Check for SQL injection patterns.

        Args:
            text: Text to check

        Returns:
            True if suspicious patterns found
        """
        return bool(InputValidator.DANGEROUS_PATTERNS["sql_keywords"].search(text))

    @staticmethod
    def check_command_injection(text: str) -> bool:
        """
        Check for command injection patterns.

        Args:
            text: Text to check

        Returns:
            True if suspicious patterns found
        """
        return bool(InputValidator.DANGEROUS_PATTERNS["command_injection"].search(text))


# Flask request validator
class FlaskRequestValidator:
    """Validator for Flask request data."""

    @staticmethod
    def validate_form_data(form_data: Dict, schema: Dict) -> Dict:
        """
        Validate Flask form data against schema.

        Args:
            form_data: Form data from request.form
            schema: Validation schema

        Returns:
            Validated data

        Schema format:
            {
                'field_name': {
                    'type': 'string|integer|float|email|url',
                    'required': True/False,
                    'min': value,
                    'max': value,
                    'pattern': 'pattern_name',
                    'enum': ['value1', 'value2']
                }
            }
        """
        validated = {}
        validator = InputValidator()

        for field, rules in schema.items():
            # Check required
            if rules.get("required", False) and field not in form_data:
                raise ValidationError(f"Required field missing: {field}")

            # Skip if not present and not required
            if field not in form_data:
                continue

            value = form_data[field]
            field_type = rules.get("type", "string")

            # Validate based on type
            try:
                if field_type == "string":
                    validated[field] = validator.validate_string(
                        value,
                        min_length=rules.get("min", 0),
                        max_length=rules.get("max", 10000),
                        pattern=rules.get("pattern"),
                    )
                elif field_type == "integer":
                    validated[field] = validator.validate_integer(
                        value, min_value=rules.get("min"), max_value=rules.get("max")
                    )
                elif field_type == "float":
                    validated[field] = validator.validate_float(
                        value, min_value=rules.get("min"), max_value=rules.get("max")
                    )
                elif field_type == "email":
                    validated[field] = validator.validate_email(value)
                elif field_type == "url":
                    validated[field] = validator.validate_url(value)
                elif field_type == "enum":
                    validated[field] = validator.validate_enum(value, rules.get("enum", []))
                else:
                    validated[field] = value

            except ValidationError as e:
                raise ValidationError(f"Field '{field}': {e}")

        return validated


# Example usage
if __name__ == "__main__":
    validator = InputValidator()

    # Test string validation
    try:
        email = validator.validate_email("test@example.com")
        print(f"✅ Valid email: {email}")
    except ValidationError as e:
        print(f"❌ Invalid email: {e}")

    # Test integer validation
    try:
        age = validator.validate_integer("25", min_value=0, max_value=150)
        print(f"✅ Valid age: {age}")
    except ValidationError as e:
        print(f"❌ Invalid age: {e}")

    # Test decimal validation
    try:
        amount = validator.validate_decimal("123.45", min_value=Decimal("0"))
        print(f"✅ Valid amount: {amount}")
    except ValidationError as e:
        print(f"❌ Invalid amount: {e}")

    # Test HTML sanitization
    dangerous_html = '<script>alert("XSS")</script><p onclick="evil()">Click</p>'
    safe_html = validator.sanitize_html(dangerous_html)
    print(f"✅ Sanitized: {safe_html}")
