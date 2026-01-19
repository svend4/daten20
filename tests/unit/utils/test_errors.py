"""
Comprehensive tests for error handling system

Tests the custom error hierarchy, error formatting,
internationalization, and utility functions.

Session 22 - 60+ tests
"""

import json
import sys
from io import StringIO

import pytest

from src.utils.errors import (
    APIAuthError,
    APIError,
    APIRateLimitError,
    ConfigError,
    ConfigMissingError,
    DatabaseError,
    DBConnectionError,
    DBQueryError,
    DMSError,
    ErrorCode,
    FileError,
    FileFormatError,
    FileNotFoundError,
    FileReadError,
    MLError,
    ModelLoadError,
    NERError,
    ParsingError,
    ProcessingError,
    ValidationError,
    format_exception,
    get_error_message,
    safe_execute,
    validate_and_raise,
)
from src.utils.errors import ERROR_MESSAGES


class TestErrorCode:
    """Test ErrorCode enum"""

    def test_error_code_enum_exists(self):
        """Test ErrorCode enum is defined"""
        assert ErrorCode is not None

    def test_file_error_codes(self):
        """Test file error codes are in 1000-1999 range"""
        file_codes = [
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.FILE_READ_ERROR,
            ErrorCode.FILE_WRITE_ERROR,
            ErrorCode.FILE_PERMISSION_ERROR,
            ErrorCode.FILE_FORMAT_ERROR,
            ErrorCode.FILE_TOO_LARGE,
            ErrorCode.FILE_CORRUPTED,
        ]
        for code in file_codes:
            assert 1000 <= code.value < 2000

    def test_processing_error_codes(self):
        """Test processing error codes are in 2000-2999 range"""
        processing_codes = [
            ErrorCode.PARSING_ERROR,
            ErrorCode.EXTRACTION_ERROR,
            ErrorCode.CONVERSION_ERROR,
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.ENCODING_ERROR,
        ]
        for code in processing_codes:
            assert 2000 <= code.value < 3000

    def test_ml_error_codes(self):
        """Test ML/NLP error codes are in 3000-3999 range"""
        ml_codes = [
            ErrorCode.NER_ERROR,
            ErrorCode.CLASSIFICATION_ERROR,
            ErrorCode.EMBEDDING_ERROR,
            ErrorCode.MODEL_LOAD_ERROR,
            ErrorCode.TOKENIZATION_ERROR,
        ]
        for code in ml_codes:
            assert 3000 <= code.value < 4000

    def test_database_error_codes(self):
        """Test database error codes are in 4000-4999 range"""
        db_codes = [
            ErrorCode.DB_CONNECTION_ERROR,
            ErrorCode.DB_QUERY_ERROR,
            ErrorCode.DB_INSERT_ERROR,
            ErrorCode.DB_UPDATE_ERROR,
            ErrorCode.DB_DELETE_ERROR,
        ]
        for code in db_codes:
            assert 4000 <= code.value < 5000

    def test_api_error_codes(self):
        """Test API error codes are in 5000-5999 range"""
        api_codes = [
            ErrorCode.API_REQUEST_ERROR,
            ErrorCode.API_RESPONSE_ERROR,
            ErrorCode.API_TIMEOUT_ERROR,
            ErrorCode.API_AUTH_ERROR,
            ErrorCode.API_RATE_LIMIT_ERROR,
        ]
        for code in api_codes:
            assert 5000 <= code.value < 6000

    def test_config_error_codes(self):
        """Test config error codes are in 6000-6999 range"""
        config_codes = [
            ErrorCode.CONFIG_MISSING,
            ErrorCode.CONFIG_INVALID,
            ErrorCode.CONFIG_PARSE_ERROR,
        ]
        for code in config_codes:
            assert 6000 <= code.value < 7000

    def test_security_error_codes(self):
        """Test security error codes are in 7000-7999 range"""
        security_codes = [
            ErrorCode.AUTH_ERROR,
            ErrorCode.PERMISSION_DENIED,
            ErrorCode.INVALID_TOKEN,
            ErrorCode.SECURITY_VIOLATION,
        ]
        for code in security_codes:
            assert 7000 <= code.value < 8000

    def test_general_error_codes(self):
        """Test general error codes are in 9000-9999 range"""
        general_codes = [
            ErrorCode.UNKNOWN_ERROR,
            ErrorCode.NOT_IMPLEMENTED,
            ErrorCode.DEPENDENCY_ERROR,
            ErrorCode.INTERNAL_ERROR,
        ]
        for code in general_codes:
            assert 9000 <= code.value < 10000

    def test_error_code_has_name(self):
        """Test error codes have proper names"""
        assert ErrorCode.FILE_NOT_FOUND.name == "FILE_NOT_FOUND"
        assert ErrorCode.PARSING_ERROR.name == "PARSING_ERROR"
        assert ErrorCode.DB_CONNECTION_ERROR.name == "DB_CONNECTION_ERROR"

    def test_error_code_unique_values(self):
        """Test all error codes have unique values"""
        values = [code.value for code in ErrorCode]
        assert len(values) == len(set(values))


class TestDMSError:
    """Test DMSError base exception class"""

    def test_dms_error_creation_minimal(self):
        """Test creating DMSError with minimal parameters"""
        error = DMSError("Test error")
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.UNKNOWN_ERROR
        assert error.details == {}
        assert error.suggestions == []
        assert error.original_error is None

    def test_dms_error_creation_full(self):
        """Test creating DMSError with all parameters"""
        original = ValueError("Original error")
        error = DMSError(
            message="Test error",
            error_code=ErrorCode.FILE_NOT_FOUND,
            details={"key": "value"},
            suggestions=["Suggestion 1", "Suggestion 2"],
            original_error=original,
        )
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.FILE_NOT_FOUND
        assert error.details == {"key": "value"}
        assert error.suggestions == ["Suggestion 1", "Suggestion 2"]
        assert error.original_error is original

    def test_dms_error_formatted_message_basic(self):
        """Test formatted message for basic error"""
        error = DMSError("Test error", error_code=ErrorCode.FILE_NOT_FOUND)
        message = error.get_formatted_message()
        assert "ERROR [FILE_NOT_FOUND]" in message
        assert "(Code: 1001)" in message
        assert "Test error" in message
        assert "=" * 70 in message

    def test_dms_error_formatted_message_with_details(self):
        """Test formatted message includes details"""
        error = DMSError("Test error", details={"file": "test.txt", "size": 1024})
        message = error.get_formatted_message()
        assert "Details:" in message
        assert "file: test.txt" in message
        assert "size: 1024" in message

    def test_dms_error_formatted_message_with_suggestions(self):
        """Test formatted message includes suggestions"""
        error = DMSError("Test error", suggestions=["Try this", "Or that"])
        message = error.get_formatted_message()
        assert "💡 Suggestions:" in message
        assert "1. Try this" in message
        assert "2. Or that" in message

    def test_dms_error_formatted_message_with_original(self):
        """Test formatted message includes original error"""
        original = ValueError("Original error")
        error = DMSError("Test error", original_error=original)
        message = error.get_formatted_message()
        assert "Original Error:" in message
        assert "ValueError" in message
        assert "Original error" in message

    def test_dms_error_to_dict_minimal(self):
        """Test converting error to dictionary (minimal)"""
        error = DMSError("Test error")
        data = error.to_dict()
        assert data["error_code"] == 9001
        assert data["error_name"] == "UNKNOWN_ERROR"
        assert data["message"] == "Test error"
        assert data["details"] == {}
        assert data["suggestions"] == []
        assert data["original_error"] is None

    def test_dms_error_to_dict_full(self):
        """Test converting error to dictionary (full)"""
        original = ValueError("Original")
        error = DMSError(
            message="Test",
            error_code=ErrorCode.FILE_NOT_FOUND,
            details={"key": "value"},
            suggestions=["Try this"],
            original_error=original,
        )
        data = error.to_dict()
        assert data["error_code"] == 1001
        assert data["error_name"] == "FILE_NOT_FOUND"
        assert data["message"] == "Test"
        assert data["details"] == {"key": "value"}
        assert data["suggestions"] == ["Try this"]
        assert data["original_error"] == "Original"  # str() of ValueError returns just the message

    def test_dms_error_is_exception(self):
        """Test DMSError inherits from Exception"""
        error = DMSError("Test")
        assert isinstance(error, Exception)

    def test_dms_error_str_representation(self):
        """Test string representation of DMSError"""
        error = DMSError("Test error")
        error_str = str(error)
        assert "Test error" in error_str


class TestFileErrors:
    """Test file-related error classes"""

    def test_file_error_inherits_from_dms_error(self):
        """Test FileError inherits from DMSError"""
        error = FileError("Test")
        assert isinstance(error, DMSError)

    def test_file_not_found_error_basic(self):
        """Test FileNotFoundError creation"""
        error = FileNotFoundError("/path/to/file.txt")
        assert error.error_code == ErrorCode.FILE_NOT_FOUND
        assert "File not found" in error.message
        assert error.details["file_path"] == "/path/to/file.txt"
        assert len(error.suggestions) > 0

    def test_file_not_found_error_with_searched_paths(self):
        """Test FileNotFoundError with searched paths"""
        paths = ["/path1", "/path2", "/path3"]
        error = FileNotFoundError("/file.txt", searched_paths=paths)
        assert error.details["searched_paths"] == paths

    def test_file_read_error_basic(self):
        """Test FileReadError creation"""
        error = FileReadError("/file.txt", "Permission denied")
        assert error.error_code == ErrorCode.FILE_READ_ERROR
        assert "Failed to read file" in error.message
        assert error.details["file_path"] == "/file.txt"
        assert error.details["reason"] == "Permission denied"

    def test_file_read_error_with_original(self):
        """Test FileReadError with original error"""
        original = IOError("Original error")
        error = FileReadError("/file.txt", "Cannot read", original_error=original)
        assert error.original_error is original

    def test_file_format_error_basic(self):
        """Test FileFormatError creation"""
        error = FileFormatError("/file.xyz", ["txt", "pdf", "docx"])
        assert error.error_code == ErrorCode.FILE_FORMAT_ERROR
        assert "Unsupported file format" in error.message
        assert error.details["file_path"] == "/file.xyz"
        assert error.details["expected_formats"] == ["txt", "pdf", "docx"]

    def test_file_format_error_with_actual_format(self):
        """Test FileFormatError with actual format"""
        error = FileFormatError("/file.xyz", ["txt", "pdf"], actual_format="xyz")
        assert error.details["actual_format"] == "xyz"


class TestProcessingErrors:
    """Test processing-related error classes"""

    def test_processing_error_inherits_from_dms_error(self):
        """Test ProcessingError inherits from DMSError"""
        error = ProcessingError("Test")
        assert isinstance(error, DMSError)

    def test_parsing_error_basic(self):
        """Test ParsingError creation"""
        error = ParsingError("/doc.xml", "Invalid XML syntax")
        assert error.error_code == ErrorCode.PARSING_ERROR
        assert "Failed to parse document" in error.message
        assert error.details["document_path"] == "/doc.xml"
        assert error.details["reason"] == "Invalid XML syntax"

    def test_parsing_error_with_line_number(self):
        """Test ParsingError with line number"""
        error = ParsingError("/doc.xml", "Invalid tag", line_number=42)
        assert error.details["line_number"] == 42

    def test_validation_error_basic(self):
        """Test ValidationError creation"""
        error = ValidationError("email", "invalid@", "Must be valid email")
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert "Validation failed for field: email" in error.message
        assert error.details["field_name"] == "email"
        assert error.details["value"] == "invalid@"
        assert error.details["validation_rule"] == "Must be valid email"

    def test_validation_error_with_expected(self):
        """Test ValidationError with expected value"""
        error = ValidationError("age", -5, "Must be positive", expected="positive integer")
        assert error.details["expected"] == "positive integer"

    def test_validation_error_truncates_long_values(self):
        """Test ValidationError truncates long values"""
        long_value = "x" * 200
        error = ValidationError("field", long_value, "Rule")
        assert len(error.details["value"]) == 100


class TestMLErrors:
    """Test ML/NLP-related error classes"""

    def test_ml_error_inherits_from_dms_error(self):
        """Test MLError inherits from DMSError"""
        error = MLError("Test")
        assert isinstance(error, DMSError)

    def test_ner_error_basic(self):
        """Test NERError creation"""
        error = NERError("Sample text for NER", "Model not found")
        assert error.error_code == ErrorCode.NER_ERROR
        assert "Named Entity Recognition failed" in error.message
        assert error.details["text_length"] == len("Sample text for NER")
        assert error.details["reason"] == "Model not found"

    def test_ner_error_with_model_name(self):
        """Test NERError with model name"""
        error = NERError("Text", "Error", model_name="en_core_web_sm")
        assert error.details["model"] == "en_core_web_sm"

    def test_ner_error_truncates_long_text(self):
        """Test NERError truncates long text in preview"""
        long_text = "x" * 200
        error = NERError(long_text, "Error")
        assert len(error.details["text_preview"]) == 103  # 100 + "..."

    def test_model_load_error_basic(self):
        """Test ModelLoadError creation"""
        error = ModelLoadError("en_core_web_sm", "Model files not found")
        assert error.error_code == ErrorCode.MODEL_LOAD_ERROR
        assert "Failed to load model: en_core_web_sm" in error.message
        assert error.details["model_name"] == "en_core_web_sm"
        assert error.details["reason"] == "Model files not found"
        assert len(error.suggestions) > 0


class TestDatabaseErrors:
    """Test database-related error classes"""

    def test_database_error_inherits_from_dms_error(self):
        """Test DatabaseError inherits from DMSError"""
        error = DatabaseError("Test")
        assert isinstance(error, DMSError)

    def test_db_connection_error_basic(self):
        """Test DBConnectionError creation"""
        error = DBConnectionError("/data/db.sqlite", "Database locked")
        assert error.error_code == ErrorCode.DB_CONNECTION_ERROR
        assert "Failed to connect to database" in error.message
        assert error.details["db_path"] == "/data/db.sqlite"
        assert error.details["reason"] == "Database locked"

    def test_db_query_error_basic(self):
        """Test DBQueryError creation"""
        query = "SELECT * FROM users WHERE id = ?"
        error = DBQueryError(query, "Table not found")
        assert error.error_code == ErrorCode.DB_QUERY_ERROR
        assert "Database query failed" in error.message
        assert query in error.details["query"]
        assert error.details["reason"] == "Table not found"

    def test_db_query_error_with_parameters(self):
        """Test DBQueryError with parameters"""
        params = {"id": 123, "name": "Test"}
        error = DBQueryError("SELECT * FROM users", "Error", parameters=params)
        assert error.details["parameters"] == params

    def test_db_query_error_truncates_long_query(self):
        """Test DBQueryError truncates long queries"""
        long_query = "SELECT * FROM table WHERE " + " AND ".join([f"field{i}=?" for i in range(100)])
        error = DBQueryError(long_query, "Error")
        assert len(error.details["query"]) == 203  # 200 + "..."


class TestAPIErrors:
    """Test API-related error classes"""

    def test_api_error_inherits_from_dms_error(self):
        """Test APIError inherits from DMSError"""
        error = APIError("Test")
        assert isinstance(error, DMSError)

    def test_api_auth_error_basic(self):
        """Test APIAuthError creation"""
        error = APIAuthError("https://api.example.com", "Invalid credentials")
        assert error.error_code == ErrorCode.API_AUTH_ERROR
        assert "Authentication failed for API" in error.message
        assert error.details["endpoint"] == "https://api.example.com"
        assert error.details["reason"] == "Invalid credentials"

    def test_api_rate_limit_error_basic(self):
        """Test APIRateLimitError creation"""
        error = APIRateLimitError("https://api.example.com")
        assert error.error_code == ErrorCode.API_RATE_LIMIT_ERROR
        assert "Rate limit exceeded" in error.message
        assert error.details["endpoint"] == "https://api.example.com"

    def test_api_rate_limit_error_with_retry_after(self):
        """Test APIRateLimitError with retry_after"""
        error = APIRateLimitError("https://api.example.com", retry_after=60)
        assert error.details["retry_after"] == 60
        assert "Retry after 60 seconds" in error.suggestions[0]


class TestConfigErrors:
    """Test configuration-related error classes"""

    def test_config_error_inherits_from_dms_error(self):
        """Test ConfigError inherits from DMSError"""
        error = ConfigError("Test")
        assert isinstance(error, DMSError)

    def test_config_missing_error_basic(self):
        """Test ConfigMissingError creation"""
        error = ConfigMissingError("API_KEY")
        assert error.error_code == ErrorCode.CONFIG_MISSING
        assert "Missing required configuration: API_KEY" in error.message
        assert error.details["config_key"] == "API_KEY"

    def test_config_missing_error_with_file(self):
        """Test ConfigMissingError with config file"""
        error = ConfigMissingError("API_KEY", config_file="config.yaml")
        assert error.details["config_file"] == "config.yaml"


class TestUtilityFunctions:
    """Test utility functions for error handling"""

    def test_format_exception_dms_error(self):
        """Test formatting DMSError"""
        error = DMSError("Test error", error_code=ErrorCode.FILE_NOT_FOUND)
        formatted = format_exception(error)
        assert "ERROR [FILE_NOT_FOUND]" in formatted
        assert "Test error" in formatted

    def test_format_exception_standard_error(self):
        """Test formatting standard exception"""
        error = ValueError("Test value error")
        formatted = format_exception(error)
        assert "ERROR: ValueError" in formatted
        assert "Test value error" in formatted

    def test_format_exception_without_traceback(self):
        """Test formatting exception without traceback"""
        error = ValueError("Test")
        formatted = format_exception(error, include_traceback=False)
        assert "Traceback:" not in formatted

    def test_format_exception_with_traceback(self):
        """Test formatting exception with traceback"""
        error = ValueError("Test")
        formatted = format_exception(error, include_traceback=True)
        assert "Traceback:" in formatted

    def test_safe_execute_success(self):
        """Test safe_execute with successful function"""

        def successful_func(x, y):
            return x + y

        result = safe_execute(successful_func, 2, 3)
        assert result == 5

    def test_safe_execute_standard_error(self):
        """Test safe_execute with standard exception"""

        def failing_func():
            raise ValueError("Test error")

        result = safe_execute(failing_func, error_message="Custom error")
        assert result is None

    def test_safe_execute_dms_error_reraises(self):
        """Test safe_execute re-raises DMSError"""

        def dms_failing_func():
            raise DMSError("Test DMS error")

        with pytest.raises(DMSError):
            safe_execute(dms_failing_func)

    def test_validate_and_raise_true_condition(self):
        """Test validate_and_raise with true condition"""
        # Should not raise
        validate_and_raise(True, DMSError("Should not raise"))

    def test_validate_and_raise_false_condition(self):
        """Test validate_and_raise with false condition"""
        error = DMSError("Test error")
        with pytest.raises(DMSError) as exc_info:
            validate_and_raise(False, error)
        assert exc_info.value is error


class TestInternationalization:
    """Test internationalization support"""

    def test_error_messages_structure(self):
        """Test ERROR_MESSAGES has expected structure"""
        assert "en" in ERROR_MESSAGES
        assert "de" in ERROR_MESSAGES
        assert "ru" in ERROR_MESSAGES

    def test_error_messages_english(self):
        """Test English error messages"""
        en_messages = ERROR_MESSAGES["en"]
        assert "file_not_found" in en_messages
        assert "db_connection_failed" in en_messages
        assert "permission_denied" in en_messages

    def test_error_messages_german(self):
        """Test German error messages"""
        de_messages = ERROR_MESSAGES["de"]
        assert "file_not_found" in de_messages
        assert "Datei" in de_messages["file_not_found"]

    def test_error_messages_russian(self):
        """Test Russian error messages"""
        ru_messages = ERROR_MESSAGES["ru"]
        assert "file_not_found" in ru_messages
        assert "Файл" in ru_messages["file_not_found"]

    def test_get_error_message_english(self):
        """Test get_error_message for English"""
        msg = get_error_message("file_not_found", lang="en", file_path="test.txt")
        assert "test.txt" in msg
        assert "could not be found" in msg

    def test_get_error_message_german(self):
        """Test get_error_message for German"""
        msg = get_error_message("file_not_found", lang="de", file_path="test.txt")
        assert "test.txt" in msg
        assert "nicht gefunden" in msg

    def test_get_error_message_russian(self):
        """Test get_error_message for Russian"""
        msg = get_error_message("file_not_found", lang="ru", file_path="test.txt")
        assert "test.txt" in msg
        assert "не найден" in msg

    def test_get_error_message_default_language(self):
        """Test get_error_message defaults to English"""
        msg = get_error_message("file_not_found", file_path="test.txt")
        assert "test.txt" in msg
        assert "could not be found" in msg

    def test_get_error_message_invalid_language(self):
        """Test get_error_message with invalid language falls back to English"""
        msg = get_error_message("file_not_found", lang="xx", file_path="test.txt")
        assert "test.txt" in msg

    def test_get_error_message_invalid_key(self):
        """Test get_error_message with invalid key"""
        msg = get_error_message("nonexistent_key", lang="en")
        assert "Error: nonexistent_key" in msg

    def test_get_error_message_with_multiple_params(self):
        """Test get_error_message with multiple parameters"""
        msg = get_error_message("file_read_error", lang="en", file_path="test.txt", reason="Permission denied")
        assert "test.txt" in msg
        assert "Permission denied" in msg

    def test_error_messages_consistency(self):
        """Test all languages have the same keys"""
        en_keys = set(ERROR_MESSAGES["en"].keys())
        de_keys = set(ERROR_MESSAGES["de"].keys())
        ru_keys = set(ERROR_MESSAGES["ru"].keys())
        assert en_keys == de_keys == ru_keys


class TestErrorInheritanceHierarchy:
    """Test error class inheritance hierarchy"""

    def test_all_file_errors_inherit_from_file_error(self):
        """Test all file error classes inherit from FileError"""
        assert issubclass(FileNotFoundError, FileError)
        assert issubclass(FileReadError, FileError)
        assert issubclass(FileFormatError, FileError)

    def test_all_processing_errors_inherit_from_processing_error(self):
        """Test all processing error classes inherit from ProcessingError"""
        assert issubclass(ParsingError, ProcessingError)
        assert issubclass(ValidationError, ProcessingError)

    def test_all_ml_errors_inherit_from_ml_error(self):
        """Test all ML error classes inherit from MLError"""
        assert issubclass(NERError, MLError)
        assert issubclass(ModelLoadError, MLError)

    def test_all_database_errors_inherit_from_database_error(self):
        """Test all database error classes inherit from DatabaseError"""
        assert issubclass(DBConnectionError, DatabaseError)
        assert issubclass(DBQueryError, DatabaseError)

    def test_all_api_errors_inherit_from_api_error(self):
        """Test all API error classes inherit from APIError"""
        assert issubclass(APIAuthError, APIError)
        assert issubclass(APIRateLimitError, APIError)

    def test_all_config_errors_inherit_from_config_error(self):
        """Test all config error classes inherit from ConfigError"""
        assert issubclass(ConfigMissingError, ConfigError)

    def test_all_category_errors_inherit_from_dms_error(self):
        """Test all category base classes inherit from DMSError"""
        assert issubclass(FileError, DMSError)
        assert issubclass(ProcessingError, DMSError)
        assert issubclass(MLError, DMSError)
        assert issubclass(DatabaseError, DMSError)
        assert issubclass(APIError, DMSError)
        assert issubclass(ConfigError, DMSError)


class TestErrorEdgeCases:
    """Test edge cases and special scenarios"""

    def test_dms_error_with_none_details(self):
        """Test DMSError with None details becomes empty dict"""
        error = DMSError("Test", details=None)
        assert error.details == {}

    def test_dms_error_with_none_suggestions(self):
        """Test DMSError with None suggestions becomes empty list"""
        error = DMSError("Test", suggestions=None)
        assert error.suggestions == []

    def test_dms_error_json_serializable(self):
        """Test DMSError.to_dict() is JSON serializable"""
        error = DMSError(
            "Test", error_code=ErrorCode.FILE_NOT_FOUND, details={"key": "value"}, suggestions=["Try this"]
        )
        data = error.to_dict()
        # Should not raise
        json_str = json.dumps(data)
        assert json_str is not None

    def test_error_with_very_long_message(self):
        """Test error with very long message"""
        long_message = "Error: " + "x" * 1000
        error = DMSError(long_message)
        assert error.message == long_message

    def test_error_with_unicode_characters(self):
        """Test error with unicode characters"""
        error = DMSError("Test error: 测试错误 тест ошибка 🔥")
        assert "测试错误" in error.message
        assert "тест" in error.message

    def test_safe_execute_with_kwargs(self):
        """Test safe_execute with keyword arguments"""

        def func_with_kwargs(a, b, c=10):
            return a + b + c

        result = safe_execute(func_with_kwargs, 1, 2, c=20)
        assert result == 23

    def test_nested_error_wrapping(self):
        """Test wrapping errors in multiple levels"""
        original = ValueError("Original")
        middle = DMSError("Middle", original_error=original)
        outer = DMSError("Outer", original_error=middle)

        assert outer.original_error is middle
        assert middle.original_error is original
