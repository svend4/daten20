#!/usr/bin/env python3
"""
Logging Examples - Demonstrating enhanced logging features

Shows how to use:
- Performance logging
- Audit logging
- Structured logging
- Log message templates
"""

import logging
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logging_helpers import (
    PerformanceLogger,
    AuditLogger,
    StructuredLogger,
    LogMessageTemplates,
    get_performance_logger,
    get_audit_logger,
    get_structured_logger
)
from src.core.logging_config import setup_logger


def example_1_performance_logging():
    """Example 1: Performance logging with timing"""
    print("\n" + "="*60)
    print("Example 1: Performance Logging")
    print("="*60)

    # Setup logger
    logger = setup_logger("perf_example", log_level=logging.INFO)
    perf_logger = PerformanceLogger(logger)

    # Method 1: Context manager
    print("\n1. Using context manager:")
    with perf_logger.measure("document_parsing", doc_id=123, doc_name="example.pdf"):
        # Simulate processing
        time.sleep(0.5)
        print("   Processing document...")

    # Method 2: Decorator
    print("\n2. Using decorator:")

    @perf_logger.timed("data_processing")
    def process_data(items):
        time.sleep(0.3)
        return len(items)

    result = process_data([1, 2, 3, 4, 5])
    print(f"   Processed {result} items")


def example_2_audit_logging():
    """Example 2: Audit logging for compliance"""
    print("\n" + "="*60)
    print("Example 2: Audit Logging")
    print("="*60)

    # Setup logger
    logger = setup_logger("audit_example", log_level=logging.INFO)
    audit_logger = AuditLogger(logger, Path("logs/audit.log"))

    print("\n1. Logging user actions:")
    audit_logger.log_action(
        action="create",
        user="john.smith",
        resource="document/contract_2026.pdf",
        status="success",
        ip_address="192.168.1.100"
    )

    print("\n2. Logging access attempts:")
    audit_logger.log_access(
        user="jane.doe",
        resource="confidential/salary_data.xlsx",
        granted=False,
        reason="Insufficient permissions"
    )

    print("\n3. Logging PII access (GDPR compliance):")
    audit_logger.log_pii_access(
        user="admin",
        pii_type="customer_emails",
        purpose="Marketing campaign analysis"
    )

    print("\n4. Logging configuration changes:")
    audit_logger.log_configuration_change(
        user="admin",
        config_key="max_file_size",
        old_value="10MB",
        new_value="50MB"
    )


def example_3_structured_logging():
    """Example 3: Structured logging"""
    print("\n" + "="*60)
    print("Example 3: Structured Logging")
    print("="*60)

    # Setup logger
    logger = setup_logger("structured_example", log_level=logging.INFO)
    struct_logger = StructuredLogger(logger)

    print("\n1. Logging API requests:")
    struct_logger.log_request(
        method="POST",
        endpoint="/api/v1/documents",
        user="john.smith",
        status_code=201,
        duration=0.234,
        request_size=1024
    )

    print("\n2. Logging business operations:")
    struct_logger.log_operation(
        operation="document_export",
        status="completed",
        entity_type="document",
        entity_id="doc_12345",
        export_format="pdf",
        file_size=524288
    )

    print("\n3. Logging security events:")
    struct_logger.log_security_event(
        event_type="failed_login",
        severity="medium",
        description="Multiple failed login attempts detected",
        username="unknown",
        ip_address="192.168.1.200",
        attempt_count=5
    )

    print("\n4. Logging errors with context:")
    try:
        # Simulate error
        raise ValueError("Invalid document format")
    except Exception as e:
        struct_logger.log_error(
            error=e,
            context={
                "document_id": "doc_789",
                "format": "unknown",
                "user": "jane.doe"
            },
            user_message="The document format is not supported"
        )


def example_4_log_templates():
    """Example 4: Using log message templates"""
    print("\n" + "="*60)
    print("Example 4: Log Message Templates")
    print("="*60)

    logger = setup_logger("templates_example", log_level=logging.INFO)

    print("\n1. Document operations:")
    msg = LogMessageTemplates.format(
        LogMessageTemplates.DOCUMENT_PARSED,
        doc_name="report.pdf",
        size=2048000,
        pages=15
    )
    logger.info(msg)

    print("\n2. User operations:")
    msg = LogMessageTemplates.format(
        LogMessageTemplates.USER_LOGIN,
        username="john.smith",
        ip="192.168.1.100"
    )
    logger.info(msg)

    print("\n3. System operations:")
    msg = LogMessageTemplates.format(
        LogMessageTemplates.SYSTEM_STARTUP,
        service_name="DocumentService",
        version="4.1.0"
    )
    logger.info(msg)

    print("\n4. Processing operations:")
    msg = LogMessageTemplates.format(
        LogMessageTemplates.PROCESSING_PROGRESS,
        task_id="task_456",
        percent=75,
        current=75,
        total=100
    )
    logger.info(msg)

    print("\n5. Database operations:")
    msg = LogMessageTemplates.format(
        LogMessageTemplates.DB_QUERY,
        query_type="SELECT",
        duration=12.5
    )
    logger.info(msg)


def example_5_combined_usage():
    """Example 5: Combined usage in real application"""
    print("\n" + "="*60)
    print("Example 5: Combined Usage")
    print("="*60)

    # Setup loggers
    logger = setup_logger("app_example", log_level=logging.INFO)
    perf_logger = PerformanceLogger(logger)
    audit_logger = AuditLogger(logger)
    struct_logger = StructuredLogger(logger)

    # Simulate document processing workflow
    print("\n1. User uploads document:")
    user = "john.smith"
    doc_id = "doc_999"

    # Log user action (audit)
    audit_logger.log_action(
        action="upload",
        user=user,
        resource=f"document/{doc_id}",
        status="success"
    )

    print("\n2. Process document (with performance tracking):")
    with perf_logger.measure("document_processing", doc_id=doc_id, user=user):
        # Simulate processing
        time.sleep(0.4)

        # Log operations
        struct_logger.log_operation(
            operation="text_extraction",
            status="completed",
            entity_type="document",
            entity_id=doc_id,
            extracted_chars=15000
        )

    print("\n3. Export document:")
    # Log API request
    struct_logger.log_request(
        method="POST",
        endpoint=f"/api/v1/documents/{doc_id}/export",
        user=user,
        status_code=200,
        duration=0.15
    )

    # Log audit
    audit_logger.log_action(
        action="export",
        user=user,
        resource=f"document/{doc_id}",
        status="success",
        export_format="pdf"
    )

    print("\n4. User downloads file:")
    # Log data access
    audit_logger.log_data_access(
        user=user,
        data_type="document",
        operation="download",
        count=1
    )


def example_6_error_scenarios():
    """Example 6: Error logging scenarios"""
    print("\n" + "="*60)
    print("Example 6: Error Scenarios")
    print("="*60)

    logger = setup_logger("error_example", log_level=logging.INFO)
    struct_logger = StructuredLogger(logger)
    audit_logger = AuditLogger(logger)

    print("\n1. File not found error:")
    try:
        open("nonexistent_file.txt")
    except FileNotFoundError as e:
        struct_logger.log_error(
            error=e,
            context={"file_path": "nonexistent_file.txt", "operation": "read"},
            user_message="The requested file could not be found"
        )

    print("\n2. Authentication failure:")
    struct_logger.log_security_event(
        event_type="authentication_failed",
        severity="medium",
        description="Invalid credentials provided",
        username="unknown_user",
        ip_address="192.168.1.150"
    )

    print("\n3. Authorization failure:")
    audit_logger.log_access(
        user="guest_user",
        resource="admin/settings",
        granted=False,
        reason="User role 'guest' has no access to admin resources"
    )


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*60)
    print("ENHANCED LOGGING EXAMPLES")
    print("="*60)

    try:
        example_1_performance_logging()
        example_2_audit_logging()
        example_3_structured_logging()
        example_4_log_templates()
        example_5_combined_usage()
        example_6_error_scenarios()

        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED ✅")
        print("="*60)
        print("\nCheck logs/ directory for generated log files:")
        print("  - logs/perf_example.log")
        print("  - logs/audit_example.log & logs/audit.log")
        print("  - logs/structured_example.log")
        print("  - logs/templates_example.log")
        print("  - logs/app_example.log")
        print("  - logs/error_example.log")
        print("\n")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
