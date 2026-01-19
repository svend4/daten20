"""
Unit tests for comprehensive validators module
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.core.comprehensive_validators import (
    DocumentValidator,
    ValidationError,
    ValidationResult,
)


# ============================================================================
# ValidationError Tests
# ============================================================================


class TestValidationError:
    """Test ValidationError class"""

    def test_create_error(self):
        """Test creating validation error"""
        error = ValidationError(
            field="username",
            message="Username is required",
            severity="error"
        )

        assert error.field == "username"
        assert error.message == "Username is required"
        assert error.severity == "error"

    def test_default_severity(self):
        """Test default severity is 'error'"""
        error = ValidationError(field="test", message="Test")

        assert error.severity == "error"

    def test_with_code(self):
        """Test error with code"""
        error = ValidationError(
            field="email",
            message="Invalid email format",
            code="INVALID_EMAIL"
        )

        assert error.code == "INVALID_EMAIL"

    def test_default_code(self):
        """Test default error code"""
        error = ValidationError(field="test", message="Test")

        assert error.code == "VALIDATION_ERROR"

    def test_to_dict(self):
        """Test converting to dictionary"""
        error = ValidationError(
            field="age",
            message="Age must be positive",
            severity="error",
            code="INVALID_AGE"
        )

        result = error.to_dict()

        assert result["field"] == "age"
        assert result["message"] == "Age must be positive"
        assert result["severity"] == "error"
        assert result["code"] == "INVALID_AGE"

    def test_str_representation(self):
        """Test string representation"""
        error = ValidationError(
            field="password",
            message="Password too short",
            severity="error"
        )

        str_repr = str(error)

        assert "ERROR" in str_repr
        assert "password" in str_repr
        assert "Password too short" in str_repr


# ============================================================================
# ValidationResult Tests
# ============================================================================


class TestValidationResult:
    """Test ValidationResult class"""

    def test_create_result(self):
        """Test creating validation result"""
        result = ValidationResult()

        assert result.errors == []
        assert result.warnings == []
        assert result.info == []

    def test_add_error(self):
        """Test adding error"""
        result = ValidationResult()

        result.add_error("username", "Username is required")

        assert len(result.errors) == 1
        assert result.errors[0].field == "username"
        assert result.errors[0].severity == "error"

    def test_add_error_with_code(self):
        """Test adding error with code"""
        result = ValidationResult()

        result.add_error("email", "Invalid email", code="INVALID_EMAIL")

        assert result.errors[0].code == "INVALID_EMAIL"

    def test_add_warning(self):
        """Test adding warning"""
        result = ValidationResult()

        result.add_warning("age", "Age seems unusual")

        assert len(result.warnings) == 1
        assert result.warnings[0].field == "age"
        assert result.warnings[0].severity == "warning"

    def test_add_info(self):
        """Test adding info message"""
        result = ValidationResult()

        result.add_info("status", "Validation complete")

        assert len(result.info) == 1
        assert result.info[0].severity == "info"

    def test_is_valid_no_errors(self):
        """Test is_valid returns True when no errors"""
        result = ValidationResult()

        assert result.is_valid is True

    def test_is_valid_with_warnings(self):
        """Test is_valid returns True even with warnings"""
        result = ValidationResult()
        result.add_warning("field", "Warning message")

        assert result.is_valid is True

    def test_is_valid_with_errors(self):
        """Test is_valid returns False with errors"""
        result = ValidationResult()
        result.add_error("field", "Error message")

        assert result.is_valid is False

    def test_has_warnings(self):
        """Test has_warnings property"""
        result = ValidationResult()

        assert result.has_warnings is False

        result.add_warning("field", "Warning")

        assert result.has_warnings is True

    def test_get_messages_all(self):
        """Test getting all messages"""
        result = ValidationResult()
        result.add_error("field1", "Error 1")
        result.add_warning("field2", "Warning 1")
        result.add_info("field3", "Info 1")

        messages = result.get_messages()

        assert len(messages) == 3

    def test_get_messages_by_severity(self):
        """Test getting messages filtered by severity"""
        result = ValidationResult()
        result.add_error("field1", "Error 1")
        result.add_error("field2", "Error 2")
        result.add_warning("field3", "Warning 1")

        errors = result.get_messages(severity="error")

        assert len(errors) == 2
        assert all("ERROR" in msg for msg in errors)

    def test_get_messages_warnings_only(self):
        """Test getting warnings only"""
        result = ValidationResult()
        result.add_error("field1", "Error 1")
        result.add_warning("field2", "Warning 1")
        result.add_warning("field3", "Warning 2")

        warnings = result.get_messages(severity="warning")

        assert len(warnings) == 2
        assert all("WARNING" in msg for msg in warnings)

    def test_to_dict(self):
        """Test converting result to dict"""
        result = ValidationResult()
        result.add_error("field1", "Error 1")
        result.add_warning("field2", "Warning 1")

        data = result.to_dict()

        assert data["is_valid"] is False
        assert data["has_warnings"] is True
        assert len(data["errors"]) == 1
        assert len(data["warnings"]) == 1
        assert len(data["info"]) == 0

    def test_to_dict_valid_result(self):
        """Test to_dict for valid result"""
        result = ValidationResult()

        data = result.to_dict()

        assert data["is_valid"] is True
        assert data["has_warnings"] is False


# ============================================================================
# DocumentValidator Tests
# ============================================================================


class TestDocumentValidator:
    """Test DocumentValidator class"""

    @pytest.fixture
    def temp_file(self):
        """Create temporary file"""
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.write(fd, b"Test content")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def temp_pdf(self):
        """Create temporary PDF-like file"""
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.write(fd, b"%PDF-1.4 test content")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_validate_file_path_exists(self, temp_file):
        """Test validating existing file path"""
        is_valid, error = DocumentValidator.validate_file_path(temp_file)

        assert is_valid is True
        assert error is None

    def test_validate_file_path_not_exists(self):
        """Test validating non-existent file"""
        is_valid, error = DocumentValidator.validate_file_path("/nonexistent/file.txt")

        assert is_valid is False
        assert "does not exist" in error

    def test_validate_file_path_empty(self):
        """Test validating empty path"""
        is_valid, error = DocumentValidator.validate_file_path("")

        assert is_valid is False
        assert "required" in error

    def test_validate_file_path_is_directory(self):
        """Test validating directory path"""
        temp_dir = tempfile.mkdtemp()
        try:
            is_valid, error = DocumentValidator.validate_file_path(temp_dir)

            assert is_valid is False
            assert "not a file" in error
        finally:
            os.rmdir(temp_dir)

    def test_validate_file_type_allowed(self, temp_pdf):
        """Test validating allowed file type"""
        is_valid, error = DocumentValidator.validate_file_type(
            temp_pdf,
            allowed_types=['.pdf', '.docx']
        )

        assert is_valid is True
        assert error is None

    def test_validate_file_type_not_allowed(self, temp_file):
        """Test validating disallowed file type"""
        is_valid, error = DocumentValidator.validate_file_type(
            temp_file,
            allowed_types=['.pdf', '.docx']
        )

        assert is_valid is False
        assert "not allowed" in error
        assert ".txt" in error

    def test_validate_file_type_empty_path(self):
        """Test validating file type with empty path"""
        is_valid, error = DocumentValidator.validate_file_type("", ['.pdf'])

        assert is_valid is False
        assert "required" in error

    def test_validate_file_type_case_insensitive(self):
        """Test file type validation is case insensitive"""
        # Create file with uppercase extension
        fd, path = tempfile.mkstemp(suffix=".PDF")
        os.write(fd, b"Test")
        os.close(fd)

        try:
            is_valid, error = DocumentValidator.validate_file_type(
                path,
                allowed_types=['.pdf']
            )

            assert is_valid is True
        finally:
            os.unlink(path)

    def test_validate_file_size_under_limit(self, temp_file):
        """Test validating file size under limit"""
        is_valid, error = DocumentValidator.validate_file_size(
            temp_file,
            max_size_mb=1.0
        )

        assert is_valid is True
        assert error is None

    def test_validate_file_size_over_limit(self):
        """Test validating file size over limit"""
        # Create large file
        fd, path = tempfile.mkstemp()
        # Write 2 MB of data
        os.write(fd, b'x' * (2 * 1024 * 1024))
        os.close(fd)

        try:
            is_valid, error = DocumentValidator.validate_file_size(
                path,
                max_size_mb=1.0
            )

            assert is_valid is False
            assert "exceeds maximum" in error
        finally:
            os.unlink(path)

    def test_validate_file_size_not_exists(self):
        """Test validating size of non-existent file"""
        is_valid, error = DocumentValidator.validate_file_size(
            "/nonexistent/file.txt"
        )

        assert is_valid is False
        assert "does not exist" in error

    def test_validate_file_size_empty_path(self):
        """Test validating file size with empty path"""
        is_valid, error = DocumentValidator.validate_file_size("")

        assert is_valid is False
        assert "required" in error

    def test_validate_file_size_custom_limit(self, temp_file):
        """Test validating with custom size limit"""
        is_valid, error = DocumentValidator.validate_file_size(
            temp_file,
            max_size_mb=100.0
        )

        assert is_valid is True


# ============================================================================
# Integration Tests
# ============================================================================


class TestValidationIntegration:
    """Test validation integration scenarios"""

    def test_multiple_errors(self):
        """Test collecting multiple errors"""
        result = ValidationResult()

        result.add_error("username", "Username is required")
        result.add_error("email", "Email is invalid")
        result.add_error("password", "Password too short")

        assert result.is_valid is False
        assert len(result.errors) == 3

    def test_mixed_severity(self):
        """Test mixed error severities"""
        result = ValidationResult()

        result.add_error("critical_field", "Critical error")
        result.add_warning("optional_field", "Optional warning")
        result.add_info("status", "Validation info")

        assert result.is_valid is False
        assert result.has_warnings is True
        assert len(result.get_messages()) == 3

    def test_document_validation_workflow(self):
        """Test complete document validation workflow"""
        # Create test file
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.write(fd, b"PDF content")
        os.close(fd)

        try:
            result = ValidationResult()

            # Validate path
            is_valid, error = DocumentValidator.validate_file_path(path)
            if not is_valid:
                result.add_error("file_path", error)

            # Validate type
            is_valid, error = DocumentValidator.validate_file_type(
                path, ['.pdf', '.docx']
            )
            if not is_valid:
                result.add_error("file_type", error)

            # Validate size
            is_valid, error = DocumentValidator.validate_file_size(path, max_size_mb=10)
            if not is_valid:
                result.add_error("file_size", error)

            # All validations should pass
            assert result.is_valid is True
        finally:
            os.unlink(path)

    def test_validation_result_serialization(self):
        """Test validation result can be serialized"""
        result = ValidationResult()
        result.add_error("field1", "Error 1", code="ERR_001")
        result.add_warning("field2", "Warning 1", code="WARN_001")

        data = result.to_dict()

        # Should be JSON-serializable
        import json
        json_str = json.dumps(data)

        assert json_str is not None
        assert "field1" in json_str
        assert "field2" in json_str
