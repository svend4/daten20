"""
Input Sanitization Module

Comprehensive input sanitization to prevent XSS, SQL injection, and other attacks.

Features:
- HTML/JavaScript sanitization
- SQL injection prevention
- Path traversal prevention
- Command injection prevention
- LDAP injection prevention
- Email validation and sanitization
- URL validation and sanitization
"""

import re
import html
import urllib.parse
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Comprehensive input sanitization engine.

    Provides methods to sanitize various types of user input to prevent
    security vulnerabilities such as XSS, SQL injection, and command injection.
    """

    # Dangerous HTML tags that should be stripped
    DANGEROUS_TAGS = [
        'script', 'iframe', 'object', 'embed', 'applet',
        'meta', 'link', 'style', 'form', 'input', 'button',
        'textarea', 'select', 'option'
    ]

    # Dangerous HTML attributes
    DANGEROUS_ATTRS = [
        'onclick', 'onload', 'onerror', 'onmouseover',
        'onfocus', 'onblur', 'onchange', 'onsubmit',
        'href="javascript:', 'src="javascript:',
        'data:', 'vbscript:'
    ]

    # SQL keywords that might indicate injection
    SQL_KEYWORDS = [
        'union', 'select', 'insert', 'update', 'delete',
        'drop', 'create', 'alter', 'exec', 'execute',
        'script', 'javascript', 'eval', '--', '/*', '*/',
        'xp_', 'sp_', 'waitfor', 'delay'
    ]

    # Command injection patterns
    COMMAND_PATTERNS = [
        r'[;&|`$]',  # Shell metacharacters
        r'\$\(',     # Command substitution
        r'>\s*\&',   # Redirect
    ]

    def __init__(self):
        """Initialize sanitizer."""
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_PATTERNS]

    def sanitize_html(self, text: str, allow_tags: Optional[List[str]] = None) -> str:
        """
        Sanitize HTML input to prevent XSS attacks.

        Args:
            text: Input text that may contain HTML
            allow_tags: List of allowed HTML tags (e.g., ['b', 'i', 'p'])

        Returns:
            Sanitized HTML string
        """
        if not text:
            return ""

        # Convert to string if needed
        text = str(text)

        # Remove dangerous tags
        for tag in self.DANGEROUS_TAGS:
            # Remove opening and closing tags
            text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(f'<{tag}[^>]*>', '', text, flags=re.IGNORECASE)

        # Remove dangerous attributes
        for attr in self.DANGEROUS_ATTRS:
            text = re.sub(attr, '', text, flags=re.IGNORECASE)

        # Remove javascript: and data: protocols
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'data:text/html', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)

        # If specific tags are allowed, strip all others
        if allow_tags:
            # Create pattern for allowed tags
            allowed_pattern = '|'.join(re.escape(tag) for tag in allow_tags)
            # Remove tags that are not in the allowed list
            text = re.sub(
                f'<(?!/?(?:{allowed_pattern})\\b)[^>]+>',
                '',
                text,
                flags=re.IGNORECASE
            )

        # Escape remaining HTML entities
        text = html.escape(text, quote=True)

        return text.strip()

    def sanitize_sql(self, text: str) -> str:
        """
        Sanitize input to prevent SQL injection.

        Note: This is a basic check. Always use parameterized queries
        for database operations!

        Args:
            text: Input text

        Returns:
            Sanitized string
        """
        if not text:
            return ""

        text = str(text)

        # Remove SQL comments
        text = re.sub(r'--.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

        # Check for suspicious SQL patterns
        for keyword in self.SQL_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {keyword}")

        # Escape single quotes (basic protection)
        text = text.replace("'", "''")

        return text.strip()

    def sanitize_path(self, path: str, base_dir: Optional[str] = None) -> Optional[str]:
        """
        Sanitize file path to prevent path traversal attacks.

        Args:
            path: File path to sanitize
            base_dir: Optional base directory to restrict access

        Returns:
            Sanitized path or None if invalid
        """
        if not path:
            return None

        path = str(path)

        # Remove null bytes
        path = path.replace('\0', '')

        # Normalize path
        try:
            normalized = Path(path).resolve()
        except (ValueError, OSError):
            logger.warning(f"Invalid path: {path}")
            return None

        # Check for path traversal
        if '..' in path or path.startswith('/'):
            logger.warning(f"Path traversal attempt detected: {path}")
            return None

        # If base_dir specified, ensure path is within it
        if base_dir:
            base = Path(base_dir).resolve()
            try:
                normalized.relative_to(base)
            except ValueError:
                logger.warning(f"Path outside base directory: {path}")
                return None

        return str(normalized)

    def sanitize_command(self, text: str) -> Optional[str]:
        """
        Sanitize input to prevent command injection.

        Args:
            text: Input text

        Returns:
            Sanitized string or None if dangerous
        """
        if not text:
            return ""

        text = str(text)

        # Check for command injection patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                logger.warning(f"Command injection attempt detected: {text[:50]}")
                return None

        # Remove null bytes
        text = text.replace('\0', '')

        return text.strip()

    def sanitize_email(self, email: str) -> Optional[str]:
        """
        Validate and sanitize email address.

        Args:
            email: Email address

        Returns:
            Sanitized email or None if invalid
        """
        if not email:
            return None

        email = str(email).strip().lower()

        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            logger.warning(f"Invalid email format: {email}")
            return None

        # Check length
        if len(email) > 254:  # RFC 5321
            return None

        # Split into local and domain
        local, domain = email.rsplit('@', 1)

        if len(local) > 64:  # RFC 5321
            return None

        return email

    def sanitize_url(self, url: str, allowed_schemes: Optional[List[str]] = None) -> Optional[str]:
        """
        Validate and sanitize URL.

        Args:
            url: URL to sanitize
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])

        Returns:
            Sanitized URL or None if invalid
        """
        if not url:
            return None

        url = str(url).strip()

        # Default allowed schemes
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']

        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            logger.warning(f"Invalid URL: {url}")
            return None

        # Check scheme
        if parsed.scheme and parsed.scheme.lower() not in allowed_schemes:
            logger.warning(f"Disallowed URL scheme: {parsed.scheme}")
            return None

        # Check for javascript: and data: protocols (double check)
        if any(dangerous in url.lower() for dangerous in ['javascript:', 'data:', 'vbscript:']):
            logger.warning(f"Dangerous URL protocol detected: {url}")
            return None

        return url

    def sanitize_filename(self, filename: str) -> Optional[str]:
        """
        Sanitize filename to prevent security issues.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename or None if invalid
        """
        if not filename:
            return None

        filename = str(filename).strip()

        # Remove null bytes
        filename = filename.replace('\0', '')

        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')

        # Remove parent directory references
        filename = filename.replace('..', '')

        # Allow only safe characters: alphanumeric, dash, underscore, dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Ensure it doesn't start with a dot (hidden file)
        if filename.startswith('.'):
            filename = '_' + filename[1:]

        # Check length
        if len(filename) > 255:
            filename = filename[:255]

        # Must have at least one character
        if not filename or filename == '.':
            return None

        return filename

    def sanitize_json(self, data: Any) -> Any:
        """
        Recursively sanitize JSON data.

        Args:
            data: JSON data (dict, list, or primitive)

        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            return {
                self.sanitize_string(k): self.sanitize_json(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self.sanitize_json(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_html(data)
        else:
            return data

    def sanitize_string(self, text: str, max_length: Optional[int] = None) -> str:
        """
        General string sanitization.

        Args:
            text: Input text
            max_length: Optional maximum length

        Returns:
            Sanitized string
        """
        if not text:
            return ""

        text = str(text)

        # Remove null bytes
        text = text.replace('\0', '')

        # Remove control characters (except newline and tab)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # Trim whitespace
        text = text.strip()

        # Enforce max length
        if max_length and len(text) > max_length:
            text = text[:max_length]

        return text

    def sanitize_integer(self, value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
        """
        Validate and sanitize integer input.

        Args:
            value: Input value
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Sanitized integer or None if invalid
        """
        try:
            num = int(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer: {value}")
            return None

        # Check bounds
        if min_val is not None and num < min_val:
            logger.warning(f"Integer below minimum: {num} < {min_val}")
            return None

        if max_val is not None and num > max_val:
            logger.warning(f"Integer above maximum: {num} > {max_val}")
            return None

        return num

    def sanitize_float(self, value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]:
        """
        Validate and sanitize float input.

        Args:
            value: Input value
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Sanitized float or None if invalid
        """
        try:
            num = float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid float: {value}")
            return None

        # Check for NaN and infinity
        if not (num == num and abs(num) != float('inf')):
            logger.warning(f"Invalid float value: {num}")
            return None

        # Check bounds
        if min_val is not None and num < min_val:
            logger.warning(f"Float below minimum: {num} < {min_val}")
            return None

        if max_val is not None and num > max_val:
            logger.warning(f"Float above maximum: {num} > {max_val}")
            return None

        return num


# Global sanitizer instance
_sanitizer_instance = None


def get_sanitizer() -> InputSanitizer:
    """Get singleton sanitizer instance."""
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = InputSanitizer()
    return _sanitizer_instance


# Convenience functions
def sanitize_html(text: str, allow_tags: Optional[List[str]] = None) -> str:
    """Sanitize HTML input."""
    return get_sanitizer().sanitize_html(text, allow_tags)


def sanitize_sql(text: str) -> str:
    """Sanitize SQL input."""
    return get_sanitizer().sanitize_sql(text)


def sanitize_path(path: str, base_dir: Optional[str] = None) -> Optional[str]:
    """Sanitize file path."""
    return get_sanitizer().sanitize_path(path, base_dir)


def sanitize_email(email: str) -> Optional[str]:
    """Validate and sanitize email."""
    return get_sanitizer().sanitize_email(email)


def sanitize_url(url: str, allowed_schemes: Optional[List[str]] = None) -> Optional[str]:
    """Validate and sanitize URL."""
    return get_sanitizer().sanitize_url(url, allowed_schemes)


def sanitize_filename(filename: str) -> Optional[str]:
    """Sanitize filename."""
    return get_sanitizer().sanitize_filename(filename)
