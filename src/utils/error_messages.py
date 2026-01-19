"""
Enhanced Error Messages Module
===============================

Provides helpful error messages with suggestions for common issues.

Features:
- Context-aware error messages
- Actionable suggestions
- Links to documentation
- Common troubleshooting steps
"""

import os
import sys
from typing import Any, Dict, Optional


class EnhancedError(Exception):
    """Base class for enhanced errors with suggestions."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        doc_link: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize enhanced error.

        Args:
            message: Error message
            suggestion: Helpful suggestion for fixing the error
            doc_link: Link to relevant documentation
            context: Additional context information
        """
        self.message = message
        self.suggestion = suggestion
        self.doc_link = doc_link
        self.context = context or {}

        # Build full message
        full_message = f"\n{'=' * 70}\n"
        full_message += f"❌ ERROR: {message}\n"

        if suggestion:
            full_message += f"\n💡 SUGGESTION: {suggestion}\n"

        if doc_link:
            full_message += f"\n📖 DOCUMENTATION: {doc_link}\n"

        if context:
            full_message += f"\n📋 CONTEXT:\n"
            for key, value in context.items():
                full_message += f"   • {key}: {value}\n"

        full_message += f"{'=' * 70}\n"

        super().__init__(full_message)


class FileNotFoundEnhancedError(EnhancedError):
    """Enhanced error for file not found."""

    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"

        # Check if it's a path issue
        if not os.path.isabs(file_path):
            suggestion = (
                f"The path '{file_path}' is relative. Try using an absolute path:\n"
                f"   Example: {os.path.abspath(file_path)}\n"
                f"Or ensure you're running from the correct directory."
            )
        elif os.path.exists(os.path.dirname(file_path)):
            suggestion = (
                f"The directory exists but the file doesn't. Check:\n"
                f"   1. File name spelling\n"
                f"   2. File extension\n"
                f"   3. Run 'ls {os.path.dirname(file_path)}' to see available files"
            )
        else:
            suggestion = f"The directory doesn't exist. Create it first:\n" f"   mkdir -p {os.path.dirname(file_path)}"

        context = {
            "Current directory": os.getcwd(),
            "File path": file_path,
            "Parent directory exists": os.path.exists(os.path.dirname(file_path)),
        }

        super().__init__(
            message=message,
            suggestion=suggestion,
            doc_link="https://docs.example.com/troubleshooting#file-not-found",
            context=context,
        )


class InvalidFormatEnhancedError(EnhancedError):
    """Enhanced error for invalid file format."""

    def __init__(self, file_path: str, expected_formats: list, detected_format: Optional[str] = None):
        message = f"Invalid file format: {file_path}"

        expected_str = ", ".join(expected_formats)
        suggestion = f"Expected formats: {expected_str}\n"

        if detected_format:
            suggestion += f"Detected format: {detected_format}\n\n"

        suggestion += (
            f"Solutions:\n"
            f"   1. Convert the file to a supported format\n"
            f"   2. Check if the file extension is correct\n"
            f"   3. Verify the file is not corrupted"
        )

        context = {
            "File path": file_path,
            "Expected formats": expected_str,
            "Detected format": detected_format or "Unknown",
        }

        super().__init__(
            message=message,
            suggestion=suggestion,
            doc_link="https://docs.example.com/supported-formats",
            context=context,
        )


class DependencyMissingEnhancedError(EnhancedError):
    """Enhanced error for missing dependencies."""

    def __init__(self, package_name: str, feature: str, install_command: Optional[str] = None):
        message = f"Missing required dependency: {package_name}"

        install_cmd = install_command or f"pip install {package_name}"

        suggestion = (
            f"The package '{package_name}' is required for {feature}.\n\n"
            f"Install it using:\n"
            f"   {install_cmd}\n\n"
            f"Or install all dependencies:\n"
            f"   pip install -r requirements.txt"
        )

        context = {
            "Package": package_name,
            "Feature": feature,
            "Install command": install_cmd,
            "Python version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }

        super().__init__(
            message=message, suggestion=suggestion, doc_link="https://docs.example.com/installation", context=context
        )


class ConfigurationEnhancedError(EnhancedError):
    """Enhanced error for configuration issues."""

    def __init__(self, config_key: str, config_file: Optional[str] = None, expected_type: Optional[str] = None):
        message = f"Configuration error: Missing or invalid '{config_key}'"

        suggestion = f"Check your configuration file"
        if config_file:
            suggestion += f" ({config_file})"
        suggestion += ":\n\n"

        if expected_type:
            suggestion += f"   '{config_key}' should be a {expected_type}\n\n"

        suggestion += (
            f"Example configuration:\n"
            f"   {config_key}: <value>\n\n"
            f"Or set as environment variable:\n"
            f"   export {config_key.upper().replace('.', '_')}=<value>"
        )

        context = {"Configuration key": config_key, "Expected type": expected_type or "Not specified"}

        if config_file:
            context["Config file"] = config_file
            context["Config file exists"] = os.path.exists(config_file)

        super().__init__(
            message=message, suggestion=suggestion, doc_link="https://docs.example.com/configuration", context=context
        )


class DatabaseEnhancedError(EnhancedError):
    """Enhanced error for database issues."""

    def __init__(self, operation: str, db_path: Optional[str] = None, original_error: Optional[str] = None):
        message = f"Database error during {operation}"

        if original_error:
            message += f": {original_error}"

        suggestion = "Common solutions:\n"

        if "connection" in operation.lower():
            suggestion += (
                f"   1. Check database file permissions\n"
                f"   2. Ensure database file is not locked by another process\n"
                f"   3. Verify database file is not corrupted\n\n"
            )
        elif "init" in operation.lower():
            suggestion += (
                f"   1. Initialize the database:\n"
                f"      python -c 'from src.core.database import Database; Database().init_db()'\n"
                f"   2. Check write permissions in the database directory\n\n"
            )
        else:
            suggestion += (
                f"   1. Check the SQL query syntax\n"
                f"   2. Verify table schema\n"
                f"   3. Check for data type mismatches\n\n"
            )

        if db_path:
            suggestion += f"Database location: {db_path}\n"

        context = {"Operation": operation, "Original error": original_error or "Not specified"}

        if db_path:
            context["Database path"] = db_path
            context["Database exists"] = os.path.exists(db_path) if db_path else False

        super().__init__(
            message=message, suggestion=suggestion, doc_link="https://docs.example.com/database", context=context
        )


class PermissionEnhancedError(EnhancedError):
    """Enhanced error for permission issues."""

    def __init__(self, path: str, operation: str):
        message = f"Permission denied: Cannot {operation} {path}"

        suggestion = (
            f"The current user doesn't have permission to {operation} this file/directory.\n\n"
            f"Solutions:\n"
            f"   1. Change file permissions:\n"
            f"      chmod +rw {path}\n\n"
            f"   2. Change ownership:\n"
            f"      sudo chown $USER {path}\n\n"
            f"   3. Run with elevated permissions (not recommended):\n"
            f"      sudo <command>\n\n"
            f"   4. Use a different output directory where you have write access"
        )

        context = {
            "Path": path,
            "Operation": operation,
            "Current user": os.getenv("USER", "unknown"),
            "Path exists": os.path.exists(path),
        }

        if os.path.exists(path):
            try:
                import stat

                st = os.stat(path)
                context["Permissions"] = oct(st.st_mode)[-3:]
            except:
                context["Permissions"] = "Cannot determine"

        super().__init__(
            message=message,
            suggestion=suggestion,
            doc_link="https://docs.example.com/troubleshooting#permissions",
            context=context,
        )


# Common error message templates
ERROR_TEMPLATES = {
    "file_empty": {
        "message": "The file is empty",
        "suggestion": "Ensure the file contains data. Check if the file was properly created or downloaded.",
    },
    "memory_error": {
        "message": "Out of memory",
        "suggestion": (
            "The operation requires too much memory. Try:\n"
            "   1. Process smaller batches of files\n"
            "   2. Increase system memory\n"
            "   3. Close other applications\n"
            "   4. Use the --low-memory flag if available"
        ),
    },
    "timeout": {
        "message": "Operation timed out",
        "suggestion": (
            "The operation took too long. Try:\n"
            "   1. Increase the timeout value with --timeout flag\n"
            "   2. Check network connectivity if accessing remote resources\n"
            "   3. Process fewer files at once\n"
            "   4. Check system performance"
        ),
    },
    "api_error": {
        "message": "API request failed",
        "suggestion": (
            "The API request encountered an error. Check:\n"
            "   1. Network connectivity\n"
            "   2. API key/credentials are correct\n"
            "   3. API endpoint URL is correct\n"
            "   4. API rate limits haven't been exceeded\n"
            "   5. API service status"
        ),
    },
}


def get_error_template(error_type: str) -> Dict[str, str]:
    """Get error message template by type."""
    return ERROR_TEMPLATES.get(
        error_type, {"message": "An error occurred", "suggestion": "Please check the logs for more details."}
    )
