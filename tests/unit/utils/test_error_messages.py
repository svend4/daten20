"""
Comprehensive tests for src/utils/error_messages.py

Tests enhanced error messages to achieve >75% coverage.
"""

import os
import sys
from unittest.mock import patch

import pytest

from src.utils.error_messages import (
    ConfigurationEnhancedError,
    DatabaseEnhancedError,
    DependencyMissingEnhancedError,
    EnhancedError,
    ERROR_TEMPLATES,
    FileNotFoundEnhancedError,
    InvalidFormatEnhancedError,
    PermissionEnhancedError,
    get_error_template,
)


class TestEnhancedError:
    """Test EnhancedError base class"""

    def test_enhanced_error_basic(self):
        """Test EnhancedError with only message"""
        error = EnhancedError("Something went wrong")
        assert "Something went wrong" in str(error)
        assert error.message == "Something went wrong"
        assert error.suggestion is None
        assert error.doc_link is None
        assert error.context == {}

    def test_enhanced_error_with_suggestion(self):
        """Test EnhancedError with suggestion"""
        error = EnhancedError("Error occurred", suggestion="Try restarting the application")
        assert "Error occurred" in str(error)
        assert "Try restarting the application" in str(error)
        assert "💡 SUGGESTION" in str(error)

    def test_enhanced_error_with_doc_link(self):
        """Test EnhancedError with documentation link"""
        error = EnhancedError("Error occurred", doc_link="https://docs.example.com/error")
        assert "Error occurred" in str(error)
        assert "https://docs.example.com/error" in str(error)
        assert "📖 DOCUMENTATION" in str(error)

    def test_enhanced_error_with_context(self):
        """Test EnhancedError with context"""
        context = {"user": "john", "action": "delete", "file": "test.txt"}
        error = EnhancedError("Operation failed", context=context)
        error_str = str(error)
        assert "Operation failed" in error_str
        assert "📋 CONTEXT" in error_str
        assert "user: john" in error_str
        assert "action: delete" in error_str
        assert "file: test.txt" in error_str

    def test_enhanced_error_with_all_params(self):
        """Test EnhancedError with all parameters"""
        context = {"detail": "value"}
        error = EnhancedError(
            message="Complete error",
            suggestion="Fix it this way",
            doc_link="https://docs.example.com",
            context=context,
        )
        error_str = str(error)
        assert "Complete error" in error_str
        assert "Fix it this way" in error_str
        assert "https://docs.example.com" in error_str
        assert "detail: value" in error_str
        assert "=" * 70 in error_str

    def test_enhanced_error_is_exception(self):
        """Test EnhancedError is an Exception"""
        error = EnhancedError("Test")
        assert isinstance(error, Exception)

    def test_enhanced_error_can_be_raised(self):
        """Test EnhancedError can be raised"""
        with pytest.raises(EnhancedError) as exc_info:
            raise EnhancedError("Test error")
        assert "Test error" in str(exc_info.value)


class TestFileNotFoundEnhancedError:
    """Test FileNotFoundEnhancedError class"""

    def test_file_not_found_relative_path(self):
        """Test FileNotFoundEnhancedError with relative path"""
        error = FileNotFoundEnhancedError("relative/path/file.txt")
        error_str = str(error)
        assert "File not found" in error_str
        assert "relative/path/file.txt" in error_str
        assert "relative" in error_str.lower()
        assert "absolute path" in error_str.lower()
        assert "Current directory" in error_str
        assert os.getcwd() in error_str

    def test_file_not_found_absolute_path_dir_exists(self, tmp_path):
        """Test FileNotFoundEnhancedError when directory exists"""
        # Create a directory but not the file
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()
        missing_file = test_dir / "missing.txt"

        error = FileNotFoundEnhancedError(str(missing_file))
        error_str = str(error)
        assert "File not found" in error_str
        assert "directory exists" in error_str.lower()
        assert "spelling" in error_str.lower()
        assert "extension" in error_str.lower()

    def test_file_not_found_dir_does_not_exist(self):
        """Test FileNotFoundEnhancedError when directory doesn't exist"""
        error = FileNotFoundEnhancedError("/nonexistent/path/to/file.txt")
        error_str = str(error)
        assert "File not found" in error_str
        assert "directory doesn't exist" in error_str.lower()
        assert "mkdir -p" in error_str

    def test_file_not_found_has_context(self):
        """Test FileNotFoundEnhancedError has proper context"""
        error = FileNotFoundEnhancedError("test.txt")
        assert error.context is not None
        assert "Current directory" in error.context
        assert "File path" in error.context
        assert "Parent directory exists" in error.context

    def test_file_not_found_has_doc_link(self):
        """Test FileNotFoundEnhancedError has documentation link"""
        error = FileNotFoundEnhancedError("test.txt")
        assert error.doc_link is not None
        assert "docs.example.com" in error.doc_link
        assert "file-not-found" in error.doc_link


class TestInvalidFormatEnhancedError:
    """Test InvalidFormatEnhancedError class"""

    def test_invalid_format_basic(self):
        """Test InvalidFormatEnhancedError with basic parameters"""
        error = InvalidFormatEnhancedError("file.xyz", ["json", "yaml"])
        error_str = str(error)
        assert "Invalid file format" in error_str
        assert "file.xyz" in error_str
        assert "json" in error_str
        assert "yaml" in error_str

    def test_invalid_format_with_detected(self):
        """Test InvalidFormatEnhancedError with detected format"""
        error = InvalidFormatEnhancedError("file.txt", ["json", "yaml", "xml"], detected_format="text/plain")
        error_str = str(error)
        assert "Invalid file format" in error_str
        assert "Expected formats: json, yaml, xml" in error_str
        assert "Detected format: text/plain" in error_str

    def test_invalid_format_suggestions(self):
        """Test InvalidFormatEnhancedError has proper suggestions"""
        error = InvalidFormatEnhancedError("data.csv", ["json"])
        error_str = str(error)
        assert "convert" in error_str.lower()
        assert "extension" in error_str.lower()
        assert "corrupted" in error_str.lower()

    def test_invalid_format_context(self):
        """Test InvalidFormatEnhancedError has proper context"""
        error = InvalidFormatEnhancedError("test.bin", ["json", "xml"], detected_format="binary")
        assert "File path" in error.context
        assert error.context["File path"] == "test.bin"
        assert "Expected formats" in error.context
        assert "json, xml" in error.context["Expected formats"]
        assert error.context["Detected format"] == "binary"

    def test_invalid_format_no_detected(self):
        """Test InvalidFormatEnhancedError without detected format"""
        error = InvalidFormatEnhancedError("file.unknown", ["pdf"])
        assert error.context["Detected format"] == "Unknown"


class TestDependencyMissingEnhancedError:
    """Test DependencyMissingEnhancedError class"""

    def test_dependency_missing_basic(self):
        """Test DependencyMissingEnhancedError with basic parameters"""
        error = DependencyMissingEnhancedError("numpy", "data analysis")
        error_str = str(error)
        assert "Missing required dependency: numpy" in error_str
        assert "data analysis" in error_str
        assert "pip install numpy" in error_str

    def test_dependency_missing_custom_install(self):
        """Test DependencyMissingEnhancedError with custom install command"""
        error = DependencyMissingEnhancedError("torch", "deep learning", install_command="pip install torch torchvision")
        error_str = str(error)
        assert "torch" in error_str
        assert "pip install torch torchvision" in error_str

    def test_dependency_missing_suggestions(self):
        """Test DependencyMissingEnhancedError has suggestions"""
        error = DependencyMissingEnhancedError("pandas", "CSV processing")
        error_str = str(error)
        assert "pip install -r requirements.txt" in error_str
        assert "CSV processing" in error_str

    def test_dependency_missing_context(self):
        """Test DependencyMissingEnhancedError has context"""
        error = DependencyMissingEnhancedError("sklearn", "machine learning")
        assert "Package" in error.context
        assert error.context["Package"] == "sklearn"
        assert "Feature" in error.context
        assert error.context["Feature"] == "machine learning"
        assert "Python version" in error.context
        assert f"{sys.version_info.major}.{sys.version_info.minor}" in error.context["Python version"]


class TestConfigurationEnhancedError:
    """Test ConfigurationEnhancedError class"""

    def test_configuration_error_basic(self):
        """Test ConfigurationEnhancedError with config key only"""
        error = ConfigurationEnhancedError("api_key")
        error_str = str(error)
        assert "Configuration error" in error_str
        assert "api_key" in error_str
        assert "Check your configuration file" in error_str

    def test_configuration_error_with_file(self):
        """Test ConfigurationEnhancedError with config file"""
        error = ConfigurationEnhancedError("database.host", config_file="/etc/app/config.yaml")
        error_str = str(error)
        assert "database.host" in error_str
        assert "/etc/app/config.yaml" in error_str

    def test_configuration_error_with_type(self):
        """Test ConfigurationEnhancedError with expected type"""
        error = ConfigurationEnhancedError("port", expected_type="integer")
        error_str = str(error)
        assert "port" in error_str
        assert "should be a integer" in error_str

    def test_configuration_error_env_var_suggestion(self):
        """Test ConfigurationEnhancedError suggests environment variable"""
        error = ConfigurationEnhancedError("api.key")
        error_str = str(error)
        assert "environment variable" in error_str.lower()
        assert "API_KEY" in error_str

    def test_configuration_error_context(self):
        """Test ConfigurationEnhancedError has proper context"""
        error = ConfigurationEnhancedError("timeout", config_file="config.json", expected_type="float")
        assert "Configuration key" in error.context
        assert error.context["Configuration key"] == "timeout"
        assert "Expected type" in error.context
        assert error.context["Expected type"] == "float"

    def test_configuration_error_context_file_exists(self, tmp_path):
        """Test ConfigurationEnhancedError checks if config file exists"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("test: value")

        error = ConfigurationEnhancedError("test", config_file=str(config_file))
        assert "Config file" in error.context
        assert "Config file exists" in error.context
        assert error.context["Config file exists"] is True


class TestDatabaseEnhancedError:
    """Test DatabaseEnhancedError class"""

    def test_database_error_basic(self):
        """Test DatabaseEnhancedError with operation only"""
        error = DatabaseEnhancedError("query")
        error_str = str(error)
        assert "Database error during query" in error_str
        assert "Common solutions" in error_str

    def test_database_error_with_original_error(self):
        """Test DatabaseEnhancedError with original error"""
        error = DatabaseEnhancedError("insert", original_error="UNIQUE constraint failed")
        error_str = str(error)
        assert "insert" in error_str
        assert "UNIQUE constraint failed" in error_str

    def test_database_error_connection_suggestions(self):
        """Test DatabaseEnhancedError for connection operation"""
        error = DatabaseEnhancedError("connection")
        error_str = str(error)
        assert "permissions" in error_str.lower()
        assert "locked" in error_str.lower()
        assert "corrupted" in error_str.lower()

    def test_database_error_init_suggestions(self):
        """Test DatabaseEnhancedError for init operation"""
        error = DatabaseEnhancedError("initialization")
        error_str = str(error)
        assert "initialize" in error_str.lower() or "init" in error_str.lower()
        assert "Database" in error_str
        assert "write permissions" in error_str.lower()

    def test_database_error_query_suggestions(self):
        """Test DatabaseEnhancedError for query operation"""
        error = DatabaseEnhancedError("SELECT")
        error_str = str(error)
        assert "sql" in error_str.lower() or "query" in error_str.lower()
        assert "schema" in error_str.lower()

    def test_database_error_with_db_path(self):
        """Test DatabaseEnhancedError with database path"""
        error = DatabaseEnhancedError("backup", db_path="/var/db/app.db")
        error_str = str(error)
        assert "backup" in error_str
        assert "/var/db/app.db" in error_str

    def test_database_error_context(self, tmp_path):
        """Test DatabaseEnhancedError has proper context"""
        db_file = tmp_path / "test.db"
        db_file.write_text("fake db")

        error = DatabaseEnhancedError("read", db_path=str(db_file), original_error="corrupt")
        assert "Operation" in error.context
        assert error.context["Operation"] == "read"
        assert "Original error" in error.context
        assert error.context["Original error"] == "corrupt"
        assert "Database path" in error.context
        assert "Database exists" in error.context
        assert error.context["Database exists"] is True


class TestPermissionEnhancedError:
    """Test PermissionEnhancedError class"""

    def test_permission_error_basic(self):
        """Test PermissionEnhancedError with path and operation"""
        error = PermissionEnhancedError("/protected/file.txt", "read")
        error_str = str(error)
        assert "Permission denied" in error_str
        assert "Cannot read" in error_str
        assert "/protected/file.txt" in error_str

    def test_permission_error_write_operation(self):
        """Test PermissionEnhancedError for write operation"""
        error = PermissionEnhancedError("/var/log/app.log", "write")
        error_str = str(error)
        assert "Cannot write" in error_str
        assert "/var/log/app.log" in error_str

    def test_permission_error_suggestions(self):
        """Test PermissionEnhancedError has proper suggestions"""
        error = PermissionEnhancedError("/data/file.txt", "modify")
        error_str = str(error)
        assert "chmod" in error_str
        assert "chown" in error_str
        assert "sudo" in error_str
        assert "different output directory" in error_str.lower()

    def test_permission_error_context_basic(self):
        """Test PermissionEnhancedError context for non-existent path"""
        error = PermissionEnhancedError("/nonexistent/file", "delete")
        assert "Path" in error.context
        assert error.context["Path"] == "/nonexistent/file"
        assert "Operation" in error.context
        assert error.context["Operation"] == "delete"
        assert "Path exists" in error.context
        assert error.context["Path exists"] is False

    @patch.dict(os.environ, {"USER": "testuser"})
    def test_permission_error_context_user(self):
        """Test PermissionEnhancedError includes current user"""
        error = PermissionEnhancedError("/tmp/test", "read")
        assert "Current user" in error.context
        assert error.context["Current user"] == "testuser"

    def test_permission_error_context_permissions(self, tmp_path):
        """Test PermissionEnhancedError includes file permissions"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        os.chmod(test_file, 0o644)

        error = PermissionEnhancedError(str(test_file), "execute")
        assert "Permissions" in error.context
        # Permissions should be octal string like "644"
        assert isinstance(error.context["Permissions"], str)

    def test_permission_error_context_cannot_stat(self):
        """Test PermissionEnhancedError when stat fails"""
        # Use a path that exists but might have issues with stat
        with patch("os.stat", side_effect=Exception("Cannot stat")):
            with patch("os.path.exists", return_value=True):
                error = PermissionEnhancedError("/test", "read")
                assert error.context["Permissions"] == "Cannot determine"


class TestErrorTemplates:
    """Test ERROR_TEMPLATES dictionary"""

    def test_error_templates_exist(self):
        """Test ERROR_TEMPLATES is defined"""
        assert ERROR_TEMPLATES is not None
        assert isinstance(ERROR_TEMPLATES, dict)

    def test_error_templates_has_file_empty(self):
        """Test ERROR_TEMPLATES has file_empty"""
        assert "file_empty" in ERROR_TEMPLATES
        template = ERROR_TEMPLATES["file_empty"]
        assert "message" in template
        assert "suggestion" in template
        assert "empty" in template["message"].lower()

    def test_error_templates_has_memory_error(self):
        """Test ERROR_TEMPLATES has memory_error"""
        assert "memory_error" in ERROR_TEMPLATES
        template = ERROR_TEMPLATES["memory_error"]
        assert "memory" in template["message"].lower()
        assert "smaller batches" in template["suggestion"].lower()

    def test_error_templates_has_timeout(self):
        """Test ERROR_TEMPLATES has timeout"""
        assert "timeout" in ERROR_TEMPLATES
        template = ERROR_TEMPLATES["timeout"]
        assert "timed out" in template["message"].lower()
        assert "increase the timeout" in template["suggestion"].lower()

    def test_error_templates_has_api_error(self):
        """Test ERROR_TEMPLATES has api_error"""
        assert "api_error" in ERROR_TEMPLATES
        template = ERROR_TEMPLATES["api_error"]
        assert "api" in template["message"].lower()
        assert "connectivity" in template["suggestion"].lower()

    def test_error_templates_structure(self):
        """Test all templates have required structure"""
        for key, template in ERROR_TEMPLATES.items():
            assert "message" in template, f"Template '{key}' missing 'message'"
            assert "suggestion" in template, f"Template '{key}' missing 'suggestion'"
            assert isinstance(template["message"], str)
            assert isinstance(template["suggestion"], str)


class TestGetErrorTemplate:
    """Test get_error_template function"""

    def test_get_error_template_file_empty(self):
        """Test get_error_template for file_empty"""
        template = get_error_template("file_empty")
        assert template is not None
        assert "message" in template
        assert "suggestion" in template
        assert "empty" in template["message"].lower()

    def test_get_error_template_memory_error(self):
        """Test get_error_template for memory_error"""
        template = get_error_template("memory_error")
        assert "memory" in template["message"].lower()

    def test_get_error_template_timeout(self):
        """Test get_error_template for timeout"""
        template = get_error_template("timeout")
        assert "timed out" in template["message"].lower()

    def test_get_error_template_api_error(self):
        """Test get_error_template for api_error"""
        template = get_error_template("api_error")
        assert "api" in template["message"].lower()

    def test_get_error_template_unknown(self):
        """Test get_error_template for unknown error type"""
        template = get_error_template("unknown_error_type_xyz")
        assert template is not None
        assert "message" in template
        assert "suggestion" in template
        assert "error occurred" in template["message"].lower()
        assert "logs" in template["suggestion"].lower()

    def test_get_error_template_returns_dict(self):
        """Test get_error_template returns dictionary"""
        template = get_error_template("timeout")
        assert isinstance(template, dict)


class TestIntegration:
    """Integration tests for error messages"""

    def test_all_enhanced_errors_inherit_from_enhanced_error(self):
        """Test all error classes inherit from EnhancedError"""
        assert issubclass(FileNotFoundEnhancedError, EnhancedError)
        assert issubclass(InvalidFormatEnhancedError, EnhancedError)
        assert issubclass(DependencyMissingEnhancedError, EnhancedError)
        assert issubclass(ConfigurationEnhancedError, EnhancedError)
        assert issubclass(DatabaseEnhancedError, EnhancedError)
        assert issubclass(PermissionEnhancedError, EnhancedError)

    def test_all_enhanced_errors_are_exceptions(self):
        """Test all error classes are Exceptions"""
        errors = [
            EnhancedError("test"),
            FileNotFoundEnhancedError("test.txt"),
            InvalidFormatEnhancedError("test.txt", ["json"]),
            DependencyMissingEnhancedError("pkg", "feature"),
            ConfigurationEnhancedError("key"),
            DatabaseEnhancedError("op"),
            PermissionEnhancedError("/path", "op"),
        ]
        for error in errors:
            assert isinstance(error, Exception)

    def test_all_enhanced_errors_can_be_raised(self):
        """Test all error classes can be raised and caught"""
        with pytest.raises(FileNotFoundEnhancedError):
            raise FileNotFoundEnhancedError("missing.txt")

        with pytest.raises(InvalidFormatEnhancedError):
            raise InvalidFormatEnhancedError("bad.xyz", ["json"])

        with pytest.raises(DependencyMissingEnhancedError):
            raise DependencyMissingEnhancedError("numpy", "math")

        with pytest.raises(ConfigurationEnhancedError):
            raise ConfigurationEnhancedError("api_key")

        with pytest.raises(DatabaseEnhancedError):
            raise DatabaseEnhancedError("insert")

        with pytest.raises(PermissionEnhancedError):
            raise PermissionEnhancedError("/path", "write")

    def test_error_messages_are_helpful(self):
        """Test error messages contain helpful information"""
        errors = [
            EnhancedError("Test", suggestion="Fix it", doc_link="http://example.com", context={"key": "value"}),
            FileNotFoundEnhancedError("test.txt"),
            InvalidFormatEnhancedError("test.xyz", ["json", "yaml"]),
            DependencyMissingEnhancedError("pandas", "data processing"),
            ConfigurationEnhancedError("api_key", "config.yaml", "string"),
            DatabaseEnhancedError("connection", "/db/app.db", "timeout"),
            PermissionEnhancedError("/var/log/app.log", "write"),
        ]

        for error in errors:
            error_str = str(error)
            # All errors should have structured output
            assert "=" in error_str
            # All should mention the core issue
            assert len(error_str) > 50  # Should be descriptive


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.utils.error_messages", "--cov-report=term-missing"])
