"""
Professional Error Handling and Messages
=========================================

Centralized error handling system with user-friendly messages,
detailed context, and internationalization support.

Features:
- Custom exception hierarchy
- Detailed error messages
- User-friendly formatting
- Error codes for tracking
- Context preservation
- Suggestions for fixes
- Multi-language support

Author: Document Management System
Version: 1.0.0
Date: 2026-01-11
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import traceback
import sys


class ErrorCode(Enum):
    """Error codes for categorization and tracking"""

    # File Errors (1000-1999)
    FILE_NOT_FOUND = 1001
    FILE_READ_ERROR = 1002
    FILE_WRITE_ERROR = 1003
    FILE_PERMISSION_ERROR = 1004
    FILE_FORMAT_ERROR = 1005
    FILE_TOO_LARGE = 1006
    FILE_CORRUPTED = 1007

    # Processing Errors (2000-2999)
    PARSING_ERROR = 2001
    EXTRACTION_ERROR = 2002
    CONVERSION_ERROR = 2003
    VALIDATION_ERROR = 2004
    ENCODING_ERROR = 2005

    # NLP/ML Errors (3000-3999)
    NER_ERROR = 3001
    CLASSIFICATION_ERROR = 3002
    EMBEDDING_ERROR = 3003
    MODEL_LOAD_ERROR = 3004
    TOKENIZATION_ERROR = 3005

    # Database Errors (4000-4999)
    DB_CONNECTION_ERROR = 4001
    DB_QUERY_ERROR = 4002
    DB_INSERT_ERROR = 4003
    DB_UPDATE_ERROR = 4004
    DB_DELETE_ERROR = 4005

    # API Errors (5000-5999)
    API_REQUEST_ERROR = 5001
    API_RESPONSE_ERROR = 5002
    API_TIMEOUT_ERROR = 5003
    API_AUTH_ERROR = 5004
    API_RATE_LIMIT_ERROR = 5005

    # Configuration Errors (6000-6999)
    CONFIG_MISSING = 6001
    CONFIG_INVALID = 6002
    CONFIG_PARSE_ERROR = 6003

    # Security Errors (7000-7999)
    AUTH_ERROR = 7001
    PERMISSION_DENIED = 7002
    INVALID_TOKEN = 7003
    SECURITY_VIOLATION = 7004

    # General Errors (9000-9999)
    UNKNOWN_ERROR = 9001
    NOT_IMPLEMENTED = 9002
    DEPENDENCY_ERROR = 9003
    INTERNAL_ERROR = 9004


class DMSError(Exception):
    """
    Base exception class for Document Management System

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize DMS error

        Args:
            message: Main error message
            error_code: Error code for categorization
            details: Additional context details
            suggestions: List of suggestions to fix the error
            original_error: Original exception if wrapping
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.suggestions = suggestions or []
        self.original_error = original_error

        super().__init__(self.get_formatted_message())

    def get_formatted_message(self) -> str:
        """
        Get formatted error message with all context

        Returns:
            Formatted error message
        """
        lines = [
            f"\n{'=' * 70}",
            f"ERROR [{self.error_code.name}] (Code: {self.error_code.value})",
            f"{'=' * 70}",
            f"\n{self.message}\n"
        ]

        # Add details if present
        if self.details:
            lines.append("Details:")
            for key, value in self.details.items():
                lines.append(f"  • {key}: {value}")
            lines.append("")

        # Add suggestions if present
        if self.suggestions:
            lines.append("💡 Suggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")

        # Add original error if present
        if self.original_error:
            lines.append(f"Original Error: {type(self.original_error).__name__}: {str(self.original_error)}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary (for JSON serialization)

        Returns:
            Error as dictionary
        """
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions,
            "original_error": str(self.original_error) if self.original_error else None
        }


# =============================================================================
# Specific Exception Classes
# =============================================================================

class FileError(DMSError):
    """Base class for file-related errors"""
    pass


class FileNotFoundError(FileError):
    """File not found error"""

    def __init__(self, file_path: str, searched_paths: Optional[List[str]] = None):
        super().__init__(
            message=f"File not found: {file_path}",
            error_code=ErrorCode.FILE_NOT_FOUND,
            details={
                "file_path": file_path,
                "searched_paths": searched_paths or [file_path]
            },
            suggestions=[
                "Check if the file path is correct",
                "Verify that the file exists",
                "Check file permissions",
                f"Expected location: {file_path}"
            ]
        )


class FileReadError(FileError):
    """File reading error"""

    def __init__(self, file_path: str, reason: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Failed to read file: {file_path}",
            error_code=ErrorCode.FILE_READ_ERROR,
            details={
                "file_path": file_path,
                "reason": reason
            },
            suggestions=[
                "Check if file is not corrupted",
                "Verify file permissions",
                "Try opening the file manually to verify it's readable"
            ],
            original_error=original_error
        )


class FileFormatError(FileError):
    """Unsupported file format error"""

    def __init__(self, file_path: str, expected_formats: List[str], actual_format: Optional[str] = None):
        super().__init__(
            message=f"Unsupported file format: {file_path}",
            error_code=ErrorCode.FILE_FORMAT_ERROR,
            details={
                "file_path": file_path,
                "expected_formats": expected_formats,
                "actual_format": actual_format or "unknown"
            },
            suggestions=[
                f"Supported formats: {', '.join(expected_formats)}",
                "Convert the file to a supported format",
                "Check file extension matches actual content"
            ]
        )


class ProcessingError(DMSError):
    """Base class for processing errors"""
    pass


class ParsingError(ProcessingError):
    """Document parsing error"""

    def __init__(self, document_path: str, reason: str, line_number: Optional[int] = None):
        details = {
            "document_path": document_path,
            "reason": reason
        }
        if line_number:
            details["line_number"] = line_number

        super().__init__(
            message=f"Failed to parse document: {document_path}",
            error_code=ErrorCode.PARSING_ERROR,
            details=details,
            suggestions=[
                "Check if document is well-formed",
                "Try parsing with a different parser",
                "Validate document structure manually"
            ]
        )


class ValidationError(ProcessingError):
    """Data validation error"""

    def __init__(
        self,
        field_name: str,
        value: Any,
        validation_rule: str,
        expected: Optional[str] = None
    ):
        super().__init__(
            message=f"Validation failed for field: {field_name}",
            error_code=ErrorCode.VALIDATION_ERROR,
            details={
                "field_name": field_name,
                "value": str(value)[:100],  # Truncate long values
                "validation_rule": validation_rule,
                "expected": expected or "valid value"
            },
            suggestions=[
                f"Ensure {field_name} meets requirements: {validation_rule}",
                f"Expected: {expected}" if expected else "Check validation rules",
                "Verify input data format"
            ]
        )


class MLError(DMSError):
    """Base class for ML/NLP errors"""
    pass


class NERError(MLError):
    """Named Entity Recognition error"""

    def __init__(self, text: str, reason: str, model_name: Optional[str] = None):
        super().__init__(
            message="Named Entity Recognition failed",
            error_code=ErrorCode.NER_ERROR,
            details={
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "reason": reason,
                "model": model_name or "default"
            },
            suggestions=[
                "Ensure spaCy model is installed: python -m spacy download en_core_web_sm",
                "Check if text is valid UTF-8",
                "Try with a different language model"
            ]
        )


class ModelLoadError(MLError):
    """ML model loading error"""

    def __init__(self, model_name: str, reason: str):
        super().__init__(
            message=f"Failed to load model: {model_name}",
            error_code=ErrorCode.MODEL_LOAD_ERROR,
            details={
                "model_name": model_name,
                "reason": reason
            },
            suggestions=[
                f"Install model: python -m spacy download {model_name}",
                "Check if model files are not corrupted",
                "Verify model compatibility with current spaCy version",
                "Try reinstalling spaCy: pip install --upgrade spacy"
            ]
        )


class DatabaseError(DMSError):
    """Base class for database errors"""
    pass


class DBConnectionError(DatabaseError):
    """Database connection error"""

    def __init__(self, db_path: str, reason: str):
        super().__init__(
            message=f"Failed to connect to database: {db_path}",
            error_code=ErrorCode.DB_CONNECTION_ERROR,
            details={
                "db_path": db_path,
                "reason": reason
            },
            suggestions=[
                "Check if database file exists",
                "Verify database file permissions",
                "Ensure database is not locked by another process",
                "Try creating a new database"
            ]
        )


class DBQueryError(DatabaseError):
    """Database query error"""

    def __init__(self, query: str, reason: str, parameters: Optional[Dict] = None):
        super().__init__(
            message="Database query failed",
            error_code=ErrorCode.DB_QUERY_ERROR,
            details={
                "query": query[:200] + "..." if len(query) > 200 else query,
                "reason": reason,
                "parameters": parameters
            },
            suggestions=[
                "Check SQL syntax",
                "Verify table and column names",
                "Check parameter types and values",
                "Review database schema"
            ]
        )


class APIError(DMSError):
    """Base class for API errors"""
    pass


class APIAuthError(APIError):
    """API authentication error"""

    def __init__(self, endpoint: str, reason: str):
        super().__init__(
            message=f"Authentication failed for API: {endpoint}",
            error_code=ErrorCode.API_AUTH_ERROR,
            details={
                "endpoint": endpoint,
                "reason": reason
            },
            suggestions=[
                "Check API credentials",
                "Verify authentication token is valid",
                "Ensure API key is not expired",
                "Check environment variables: API_KEY, API_SECRET"
            ]
        )


class APIRateLimitError(APIError):
    """API rate limit exceeded"""

    def __init__(self, endpoint: str, retry_after: Optional[int] = None):
        suggestions = [
            "Reduce request frequency",
            "Implement exponential backoff",
            "Consider caching results"
        ]

        if retry_after:
            suggestions.insert(0, f"Retry after {retry_after} seconds")

        super().__init__(
            message=f"Rate limit exceeded for API: {endpoint}",
            error_code=ErrorCode.API_RATE_LIMIT_ERROR,
            details={
                "endpoint": endpoint,
                "retry_after": retry_after
            },
            suggestions=suggestions
        )


class ConfigError(DMSError):
    """Base class for configuration errors"""
    pass


class ConfigMissingError(ConfigError):
    """Missing configuration error"""

    def __init__(self, config_key: str, config_file: Optional[str] = None):
        super().__init__(
            message=f"Missing required configuration: {config_key}",
            error_code=ErrorCode.CONFIG_MISSING,
            details={
                "config_key": config_key,
                "config_file": config_file or "default"
            },
            suggestions=[
                f"Add {config_key} to configuration file",
                f"Set environment variable: {config_key}",
                "Check configuration template for required fields",
                f"Example: {config_key}=<value>"
            ]
        )


# =============================================================================
# Error Handler Utilities
# =============================================================================

def format_exception(exc: Exception, include_traceback: bool = True) -> str:
    """
    Format exception with optional traceback

    Args:
        exc: Exception to format
        include_traceback: Include full traceback

    Returns:
        Formatted exception string
    """
    if isinstance(exc, DMSError):
        return exc.get_formatted_message()

    lines = [
        f"\n{'=' * 70}",
        f"ERROR: {type(exc).__name__}",
        f"{'=' * 70}",
        f"\n{str(exc)}\n"
    ]

    if include_traceback:
        lines.append("Traceback:")
        lines.append(traceback.format_exc())

    lines.append("=" * 70)

    return "\n".join(lines)


def safe_execute(func, *args, error_message: str = "Operation failed", **kwargs):
    """
    Execute function with error handling

    Args:
        func: Function to execute
        *args: Positional arguments
        error_message: Custom error message
        **kwargs: Keyword arguments

    Returns:
        Function result or None on error

    Example:
        >>> result = safe_execute(risky_function, arg1, arg2, error_message="Custom error")
    """
    try:
        return func(*args, **kwargs)
    except DMSError:
        raise  # Re-raise our custom errors
    except Exception as e:
        print(f"❌ {error_message}: {str(e)}", file=sys.stderr)
        return None


def validate_and_raise(condition: bool, error: DMSError):
    """
    Validate condition and raise error if False

    Args:
        condition: Condition to check
        error: Error to raise

    Example:
        >>> validate_and_raise(file.exists(), FileNotFoundError(str(file)))
    """
    if not condition:
        raise error


# =============================================================================
# User-Friendly Error Messages (i18n ready)
# =============================================================================

ERROR_MESSAGES = {
    "en": {
        "file_not_found": "The file '{file_path}' could not be found.",
        "file_read_error": "Failed to read file '{file_path}': {reason}",
        "invalid_format": "The file format is not supported. Expected: {expected}",
        "parsing_failed": "Could not parse the document. Please check if it's valid.",
        "no_text_extracted": "No text could be extracted from the document.",
        "db_connection_failed": "Database connection failed. Please check configuration.",
        "api_timeout": "The request timed out. Please try again later.",
        "permission_denied": "Permission denied. Please check your access rights.",
        "internal_error": "An internal error occurred. Please contact support."
    },
    "de": {
        "file_not_found": "Die Datei '{file_path}' wurde nicht gefunden.",
        "file_read_error": "Fehler beim Lesen der Datei '{file_path}': {reason}",
        "invalid_format": "Das Dateiformat wird nicht unterstützt. Erwartet: {expected}",
        "parsing_failed": "Dokument konnte nicht geparst werden. Bitte überprüfen Sie die Gültigkeit.",
        "no_text_extracted": "Es konnte kein Text aus dem Dokument extrahiert werden.",
        "db_connection_failed": "Datenbankverbindung fehlgeschlagen. Bitte Konfiguration prüfen.",
        "api_timeout": "Die Anfrage wurde zeitüberschritten. Bitte versuchen Sie es später erneut.",
        "permission_denied": "Zugriff verweigert. Bitte überprüfen Sie Ihre Zugriffsrechte.",
        "internal_error": "Ein interner Fehler ist aufgetreten. Bitte kontaktieren Sie den Support."
    },
    "ru": {
        "file_not_found": "Файл '{file_path}' не найден.",
        "file_read_error": "Ошибка чтения файла '{file_path}': {reason}",
        "invalid_format": "Формат файла не поддерживается. Ожидается: {expected}",
        "parsing_failed": "Не удалось обработать документ. Проверьте его корректность.",
        "no_text_extracted": "Не удалось извлечь текст из документа.",
        "db_connection_failed": "Ошибка подключения к базе данных. Проверьте конфигурацию.",
        "api_timeout": "Превышено время ожидания. Попробуйте позже.",
        "permission_denied": "Доступ запрещён. Проверьте права доступа.",
        "internal_error": "Произошла внутренняя ошибка. Обратитесь в поддержку."
    }
}


def get_error_message(key: str, lang: str = "en", **kwargs) -> str:
    """
    Get localized error message

    Args:
        key: Message key
        lang: Language code (en, de, ru)
        **kwargs: Format parameters

    Returns:
        Formatted error message

    Example:
        >>> msg = get_error_message("file_not_found", lang="en", file_path="doc.pdf")
    """
    messages = ERROR_MESSAGES.get(lang, ERROR_MESSAGES["en"])
    template = messages.get(key, f"Error: {key}")
    return template.format(**kwargs)
