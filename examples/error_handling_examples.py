#!/usr/bin/env python3
"""
Error Handling Examples
=======================

Demonstrates how to use the professional error handling system.

Author: Document Management System
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.errors import (
    # Exception classes
    FileNotFoundError,
    FileReadError,
    FileFormatError,
    ParsingError,
    ValidationError,
    NERError,
    ModelLoadError,
    DBConnectionError,
    APIAuthError,
    ConfigMissingError,
    # Utilities
    format_exception,
    safe_execute,
    validate_and_raise,
    get_error_message,
    ErrorCode
)


def example_1_file_not_found():
    """Example 1: File not found error"""
    print("\n" + "=" * 70)
    print("Example 1: File Not Found Error")
    print("=" * 70)

    try:
        raise FileNotFoundError(
            file_path="/path/to/nonexistent.pdf",
            searched_paths=[
                "/path/to/nonexistent.pdf",
                "/alternative/path/nonexistent.pdf"
            ]
        )
    except Exception as e:
        print(e)


def example_2_file_format_error():
    """Example 2: Unsupported file format"""
    print("\n" + "=" * 70)
    print("Example 2: File Format Error")
    print("=" * 70)

    try:
        raise FileFormatError(
            file_path="document.xyz",
            expected_formats=["pdf", "docx", "txt"],
            actual_format="xyz"
        )
    except Exception as e:
        print(e)


def example_3_validation_error():
    """Example 3: Validation error"""
    print("\n" + "=" * 70)
    print("Example 3: Validation Error")
    print("=" * 70)

    try:
        raise ValidationError(
            field_name="email",
            value="invalid-email",
            validation_rule="must be valid email address",
            expected="user@example.com"
        )
    except Exception as e:
        print(e)


def example_4_ner_error():
    """Example 4: NER processing error"""
    print("\n" + "=" * 70)
    print("Example 4: NER Error")
    print("=" * 70)

    try:
        raise NERError(
            text="Some sample text for NER processing" * 50,  # Long text
            reason="spaCy model not found",
            model_name="en_core_web_sm"
        )
    except Exception as e:
        print(e)


def example_5_db_connection_error():
    """Example 5: Database connection error"""
    print("\n" + "=" * 70)
    print("Example 5: Database Connection Error")
    print("=" * 70)

    try:
        raise DBConnectionError(
            db_path="/var/lib/dms/database.db",
            reason="database file is locked by another process"
        )
    except Exception as e:
        print(e)


def example_6_api_auth_error():
    """Example 6: API authentication error"""
    print("\n" + "=" * 70)
    print("Example 6: API Authentication Error")
    print("=" * 70)

    try:
        raise APIAuthError(
            endpoint="https://api.example.com/v1/documents",
            reason="invalid API key"
        )
    except Exception as e:
        print(e)


def example_7_config_missing():
    """Example 7: Missing configuration"""
    print("\n" + "=" * 70)
    print("Example 7: Config Missing Error")
    print("=" * 70)

    try:
        raise ConfigMissingError(
            config_key="DATABASE_URL",
            config_file="config/production.yml"
        )
    except Exception as e:
        print(e)


def example_8_error_to_dict():
    """Example 8: Convert error to dictionary"""
    print("\n" + "=" * 70)
    print("Example 8: Error to Dictionary (JSON-ready)")
    print("=" * 70)

    try:
        raise ValidationError(
            field_name="age",
            value="-5",
            validation_rule="must be positive integer",
            expected="0 or greater"
        )
    except Exception as e:
        error_dict = e.to_dict()
        print("Error as dictionary:")
        import json
        print(json.dumps(error_dict, indent=2))


def example_9_safe_execute():
    """Example 9: Safe execution wrapper"""
    print("\n" + "=" * 70)
    print("Example 9: Safe Execute Wrapper")
    print("=" * 70)

    def risky_operation(x, y):
        """Might fail"""
        return x / y

    # This will catch the error
    result = safe_execute(
        risky_operation,
        10,
        0,  # Division by zero!
        error_message="Division operation failed"
    )

    print(f"Result: {result}")  # Will be None


def example_10_validate_and_raise():
    """Example 10: Validation with custom error"""
    print("\n" + "=" * 70)
    print("Example 10: Validate and Raise")
    print("=" * 70)

    def process_file(file_path: str):
        """Process file with validation"""
        try:
            file = Path(file_path)

            # Validate file exists
            validate_and_raise(
                file.exists(),
                FileNotFoundError(file_path=str(file))
            )

            # Validate file is readable
            validate_and_raise(
                file.is_file(),
                FileReadError(
                    file_path=str(file),
                    reason="path is not a file"
                )
            )

            print(f"✓ File {file_path} is valid!")

        except Exception as e:
            print(e)

    # Test with non-existent file
    process_file("/path/to/nonexistent.txt")


def example_11_localized_messages():
    """Example 11: Localized error messages"""
    print("\n" + "=" * 70)
    print("Example 11: Localized Error Messages")
    print("=" * 70)

    file_path = "document.pdf"

    # English
    print("English:")
    msg_en = get_error_message("file_not_found", lang="en", file_path=file_path)
    print(f"  {msg_en}")

    # German
    print("\nGerman:")
    msg_de = get_error_message("file_not_found", lang="de", file_path=file_path)
    print(f"  {msg_de}")

    # Russian
    print("\nRussian:")
    msg_ru = get_error_message("file_not_found", lang="ru", file_path=file_path)
    print(f"  {msg_ru}")


def example_12_nested_errors():
    """Example 12: Nested/wrapped errors"""
    print("\n" + "=" * 70)
    print("Example 12: Nested Errors (Original Error Preserved)")
    print("=" * 70)

    try:
        try:
            # Simulate original error
            int("not a number")
        except ValueError as original:
            # Wrap in our custom error
            raise FileReadError(
                file_path="data.txt",
                reason="invalid number format in file",
                original_error=original
            )
    except Exception as e:
        print(e)


def example_13_parsing_error_with_line():
    """Example 13: Parsing error with line number"""
    print("\n" + "=" * 70)
    print("Example 13: Parsing Error with Line Number")
    print("=" * 70)

    try:
        raise ParsingError(
            document_path="document.xml",
            reason="unexpected closing tag",
            line_number=42
        )
    except Exception as e:
        print(e)


def example_14_model_load_error():
    """Example 14: ML model loading error"""
    print("\n" + "=" * 70)
    print("Example 14: Model Load Error")
    print("=" * 70)

    try:
        raise ModelLoadError(
            model_name="en_core_web_lg",
            reason="model files not found in spaCy data directory"
        )
    except Exception as e:
        print(e)


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 80)
    print(" " * 20 + "ERROR HANDLING EXAMPLES")
    print(" " * 15 + "Document Management System v4.1")
    print("=" * 80)

    examples = [
        example_1_file_not_found,
        example_2_file_format_error,
        example_3_validation_error,
        example_4_ner_error,
        example_5_db_connection_error,
        example_6_api_auth_error,
        example_7_config_missing,
        example_8_error_to_dict,
        example_9_safe_execute,
        example_10_validate_and_raise,
        example_11_localized_messages,
        example_12_nested_errors,
        example_13_parsing_error_with_line,
        example_14_model_load_error
    ]

    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\n\n⚠ Examples interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Example failed: {e}")

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Error handling examples")
    parser.add_argument(
        "--example",
        type=int,
        choices=range(1, 15),
        help="Run specific example (1-14)"
    )

    args = parser.parse_args()

    if args.example:
        # Run specific example
        examples = {
            1: example_1_file_not_found,
            2: example_2_file_format_error,
            3: example_3_validation_error,
            4: example_4_ner_error,
            5: example_5_db_connection_error,
            6: example_6_api_auth_error,
            7: example_7_config_missing,
            8: example_8_error_to_dict,
            9: example_9_safe_execute,
            10: example_10_validate_and_raise,
            11: example_11_localized_messages,
            12: example_12_nested_errors,
            13: example_13_parsing_error_with_line,
            14: example_14_model_load_error
        }
        examples[args.example]()
    else:
        # Run all examples
        run_all_examples()


if __name__ == "__main__":
    main()
