"""
Comprehensive tests for logging helpers

Tests advanced logging utilities including performance logging,
audit logging, structured logging, and message templates.

Session 23 - 70+ tests
"""

import logging
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from src.utils.logging_helpers import (
    AuditLogger,
    LogMessageTemplates,
    PerformanceLogger,
    StructuredLogger,
    get_audit_logger,
    get_performance_logger,
    get_structured_logger,
)


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing"""
    logger = MagicMock(spec=logging.Logger)
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.log = MagicMock()
    return logger


@pytest.fixture
def temp_audit_log(tmp_path):
    """Create a temporary audit log file"""
    return tmp_path / "audit.log"


class TestPerformanceLogger:
    """Test PerformanceLogger class"""

    def test_performance_logger_initialization(self, mock_logger):
        """Test PerformanceLogger initialization"""
        perf_logger = PerformanceLogger(mock_logger)
        assert perf_logger.logger is mock_logger

    def test_measure_context_manager_success(self, mock_logger):
        """Test measure context manager with successful operation"""
        perf_logger = PerformanceLogger(mock_logger)

        with perf_logger.measure("test_operation", doc_id=123):
            time.sleep(0.01)  # Simulate work

        # Check that starting and completion messages were logged
        assert mock_logger.info.call_count == 2
        start_call = mock_logger.info.call_args_list[0]
        complete_call = mock_logger.info.call_args_list[1]

        assert "[PERF] Starting: test_operation" in start_call[0][0]
        assert "[PERF] Completed: test_operation" in complete_call[0][0]
        assert "context" in complete_call[1]["extra"]
        assert complete_call[1]["extra"]["context"]["status"] == "success"

    def test_measure_context_manager_with_exception(self, mock_logger):
        """Test measure context manager when operation raises exception"""
        perf_logger = PerformanceLogger(mock_logger)

        with pytest.raises(ValueError):
            with perf_logger.measure("failing_operation", task_id=456):
                raise ValueError("Test error")

        # Check that starting message was logged
        assert mock_logger.info.call_count == 1
        # Check that error was logged
        assert mock_logger.error.call_count == 1
        error_call = mock_logger.error.call_args_list[0]
        assert "[PERF] Failed: failing_operation" in error_call[0][0]
        assert "Test error" in error_call[0][0]
        assert error_call[1]["extra"]["context"]["status"] == "failed"

    def test_measure_includes_duration(self, mock_logger):
        """Test measure includes duration in context"""
        perf_logger = PerformanceLogger(mock_logger)

        with perf_logger.measure("timed_operation"):
            time.sleep(0.01)

        complete_call = mock_logger.info.call_args_list[1]
        assert "duration_seconds" in complete_call[1]["extra"]["context"]
        assert complete_call[1]["extra"]["context"]["duration_seconds"] > 0

    def test_measure_includes_custom_context(self, mock_logger):
        """Test measure includes custom context fields"""
        perf_logger = PerformanceLogger(mock_logger)

        with perf_logger.measure("custom_op", user="alice", doc_type="pdf"):
            pass

        start_call = mock_logger.info.call_args_list[0]
        assert start_call[1]["extra"]["context"]["user"] == "alice"
        assert start_call[1]["extra"]["context"]["doc_type"] == "pdf"

    def test_timed_decorator_success(self, mock_logger):
        """Test timed decorator with successful function"""
        perf_logger = PerformanceLogger(mock_logger)

        @perf_logger.timed("custom_operation")
        def test_func(x, y):
            time.sleep(0.01)
            return x + y

        result = test_func(2, 3)

        assert result == 5
        assert mock_logger.debug.call_count == 1
        assert mock_logger.info.call_count == 1
        info_call = mock_logger.info.call_args_list[0]
        assert "[PERF] Completed: custom_operation" in info_call[0][0]

    def test_timed_decorator_with_exception(self, mock_logger):
        """Test timed decorator when function raises exception"""
        perf_logger = PerformanceLogger(mock_logger)

        @perf_logger.timed("failing_func")
        def failing_func():
            raise RuntimeError("Function failed")

        with pytest.raises(RuntimeError):
            failing_func()

        assert mock_logger.error.call_count == 1
        error_call = mock_logger.error.call_args_list[0]
        assert "[PERF] Failed: failing_func" in error_call[0][0]
        assert "Function failed" in error_call[0][0]

    def test_timed_decorator_default_name(self, mock_logger):
        """Test timed decorator uses function name as default"""
        perf_logger = PerformanceLogger(mock_logger)

        @perf_logger.timed()
        def my_custom_function():
            return "result"

        result = my_custom_function()

        assert result == "result"
        info_call = mock_logger.info.call_args_list[0]
        assert "my_custom_function" in info_call[0][0]

    def test_timed_decorator_preserves_function_metadata(self, mock_logger):
        """Test timed decorator preserves function metadata"""
        perf_logger = PerformanceLogger(mock_logger)

        @perf_logger.timed()
        def documented_function():
            """This is a documented function"""
            pass

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a documented function"

    def test_timed_decorator_includes_duration(self, mock_logger):
        """Test timed decorator includes duration in extra"""
        perf_logger = PerformanceLogger(mock_logger)

        @perf_logger.timed()
        def timed_func():
            time.sleep(0.01)

        timed_func()

        info_call = mock_logger.info.call_args_list[0]
        assert "duration_seconds" in info_call[1]["extra"]
        assert info_call[1]["extra"]["duration_seconds"] > 0


class TestAuditLogger:
    """Test AuditLogger class"""

    def test_audit_logger_initialization_without_file(self, mock_logger):
        """Test AuditLogger initialization without audit file"""
        audit_logger = AuditLogger(mock_logger)
        assert audit_logger.logger is mock_logger
        assert audit_logger.audit_log_path is None

    def test_audit_logger_initialization_with_file(self, mock_logger, temp_audit_log):
        """Test AuditLogger initialization with audit file"""
        audit_logger = AuditLogger(mock_logger, temp_audit_log)
        assert audit_logger.logger is mock_logger
        assert audit_logger.audit_log_path == temp_audit_log

    def test_log_action_basic(self, mock_logger):
        """Test basic audit action logging"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_action("create", "alice", "document123", status="success")

        assert mock_logger.info.call_count == 1
        call_args = mock_logger.info.call_args_list[0]
        assert "[AUDIT]" in call_args[0][0]
        assert "CREATE" in call_args[0][0]
        assert "alice" in call_args[0][0]
        assert "document123" in call_args[0][0]

    def test_log_action_includes_timestamp(self, mock_logger):
        """Test log_action includes timestamp in audit data"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_action("read", "bob", "file.pdf")

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert "timestamp" in audit_data
        assert audit_data["action"] == "read"
        assert audit_data["user"] == "bob"
        assert audit_data["resource"] == "file.pdf"

    def test_log_action_with_additional_details(self, mock_logger):
        """Test log_action with additional details"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_action("update", "charlie", "record456", status="success", ip="192.168.1.1", changes=3)

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["ip"] == "192.168.1.1"
        assert audit_data["changes"] == 3

    def test_log_access_granted(self, mock_logger):
        """Test logging granted access"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_access("alice", "/admin/panel", granted=True)

        call_args = mock_logger.info.call_args_list[0]
        assert "access" in call_args[0][0].lower()
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["action"] == "access"
        assert audit_data["status"] == "granted"

    def test_log_access_denied(self, mock_logger):
        """Test logging denied access"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_access("bob", "/admin/panel", granted=False, reason="insufficient permissions")

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["status"] == "denied"
        assert audit_data["reason"] == "insufficient permissions"

    def test_log_access_without_reason(self, mock_logger):
        """Test log_access without reason"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_access("user", "resource", granted=True)

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert "reason" not in audit_data

    def test_log_data_access(self, mock_logger):
        """Test logging data access for GDPR compliance"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_data_access("alice", "user_records", "read", count=15)

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["action"] == "data_access"
        assert audit_data["resource"] == "user_records"
        assert audit_data["operation"] == "read"
        assert audit_data["record_count"] == 15

    def test_log_data_access_default_count(self, mock_logger):
        """Test log_data_access with default count"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_data_access("bob", "documents", "export")

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["record_count"] == 1

    def test_log_pii_access(self, mock_logger):
        """Test logging PII access"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_pii_access("charlie", "email_addresses", "customer support")

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["action"] == "pii_access"
        assert audit_data["resource"] == "email_addresses"
        assert audit_data["purpose"] == "customer support"
        assert audit_data["compliance"] == "GDPR"

    def test_log_configuration_change(self, mock_logger):
        """Test logging configuration changes"""
        audit_logger = AuditLogger(mock_logger)
        audit_logger.log_configuration_change("admin", "max_file_size", "10MB", "50MB")

        call_args = mock_logger.info.call_args_list[0]
        audit_data = call_args[1]["extra"]["audit_data"]
        assert audit_data["action"] == "config_change"
        assert audit_data["resource"] == "max_file_size"
        assert audit_data["old_value"] == "10MB"
        assert audit_data["new_value"] == "50MB"


class TestStructuredLogger:
    """Test StructuredLogger class"""

    def test_structured_logger_initialization(self, mock_logger):
        """Test StructuredLogger initialization"""
        struct_logger = StructuredLogger(mock_logger)
        assert struct_logger.logger is mock_logger

    def test_log_request_success(self, mock_logger):
        """Test logging successful HTTP request"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_request("GET", "/api/documents", user="alice", status_code=200, duration=0.15)

        assert mock_logger.info.call_count == 1
        call_args = mock_logger.info.call_args_list[0]
        assert "[API]" in call_args[0][0]
        assert "GET" in call_args[0][0]
        assert "/api/documents" in call_args[0][0]

        context = call_args[1]["extra"]["context"]
        assert context["method"] == "GET"
        assert context["status_code"] == 200
        assert context["duration_ms"] == 150.0

    def test_log_request_error(self, mock_logger):
        """Test logging HTTP request with error status"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_request("POST", "/api/upload", status_code=500)

        assert mock_logger.warning.call_count == 1
        call_args = mock_logger.warning.call_args_list[0]
        assert "500" in call_args[0][0]

    def test_log_request_client_error(self, mock_logger):
        """Test logging HTTP request with 4xx status"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_request("GET", "/api/data", status_code=404)

        assert mock_logger.warning.call_count == 1

    def test_log_request_without_optional_fields(self, mock_logger):
        """Test log_request without optional fields"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_request("GET", "/api/health")

        call_args = mock_logger.info.call_args_list[0]
        context = call_args[1]["extra"]["context"]
        assert context["user"] is None
        assert context["status_code"] is None
        assert context["duration_ms"] is None

    def test_log_request_with_extra_fields(self, mock_logger):
        """Test log_request with additional fields"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_request("POST", "/api/data", ip="192.168.1.1", request_id="abc123")

        call_args = mock_logger.info.call_args_list[0]
        context = call_args[1]["extra"]["context"]
        assert context["ip"] == "192.168.1.1"
        assert context["request_id"] == "abc123"

    def test_log_operation_started(self, mock_logger):
        """Test logging operation with started status"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_operation("document_processing", "started", entity_type="document", entity_id="doc123")

        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args_list[0]
        assert call_args[0][0] == logging.DEBUG
        assert "[OP]" in call_args[0][1]
        assert "started" in call_args[0][1]

    def test_log_operation_completed(self, mock_logger):
        """Test logging operation with completed status"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_operation("export", "completed", entity_type="report", entity_id="rpt456")

        call_args = mock_logger.log.call_args_list[0]
        assert call_args[0][0] == logging.INFO

    def test_log_operation_failed(self, mock_logger):
        """Test logging operation with failed status"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_operation("import", "failed", error="Invalid format")

        call_args = mock_logger.log.call_args_list[0]
        assert call_args[0][0] == logging.ERROR

    def test_log_operation_without_entity(self, mock_logger):
        """Test log_operation without entity information"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_operation("backup", "completed")

        call_args = mock_logger.log.call_args_list[0]
        assert "backup" in call_args[0][1]
        assert "completed" in call_args[0][1]

    def test_log_operation_with_details(self, mock_logger):
        """Test log_operation with additional details"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_operation("migration", "completed", records_migrated=1000, duration=45.2)

        call_args = mock_logger.log.call_args_list[0]
        context = call_args[1]["extra"]["context"]
        assert context["records_migrated"] == 1000
        assert context["duration"] == 45.2

    def test_log_security_event_low_severity(self, mock_logger):
        """Test logging security event with low severity"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_security_event("login_attempt", "low", "User login from new device")

        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args_list[0]
        assert call_args[0][0] == logging.WARNING
        assert "[SECURITY]" in call_args[0][1]

    def test_log_security_event_high_severity(self, mock_logger):
        """Test logging security event with high severity"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_security_event("intrusion_attempt", "high", "Multiple failed login attempts")

        call_args = mock_logger.log.call_args_list[0]
        assert call_args[0][0] == logging.ERROR

    def test_log_security_event_critical_severity(self, mock_logger):
        """Test logging security event with critical severity"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_security_event("data_breach", "critical", "Unauthorized data access detected")

        call_args = mock_logger.log.call_args_list[0]
        assert call_args[0][0] == logging.ERROR

    def test_log_security_event_includes_timestamp(self, mock_logger):
        """Test security event includes timestamp"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_security_event("suspicious_activity", "medium", "Unusual access pattern")

        call_args = mock_logger.log.call_args_list[0]
        context = call_args[1]["extra"]["context"]
        assert "timestamp" in context

    def test_log_security_event_with_details(self, mock_logger):
        """Test security event with additional details"""
        struct_logger = StructuredLogger(mock_logger)
        struct_logger.log_security_event("failed_auth", "medium", "Failed authentication", ip="192.168.1.1", attempts=5)

        call_args = mock_logger.log.call_args_list[0]
        context = call_args[1]["extra"]["context"]
        assert context["ip"] == "192.168.1.1"
        assert context["attempts"] == 5

    def test_log_error_basic(self, mock_logger):
        """Test logging error with basic information"""
        struct_logger = StructuredLogger(mock_logger)
        error = ValueError("Invalid input")
        struct_logger.log_error(error)

        assert mock_logger.error.call_count == 1
        call_args = mock_logger.error.call_args_list[0]
        assert "[ERROR]" in call_args[0][0]
        assert "ValueError" in call_args[0][0]
        assert "Invalid input" in call_args[0][0]
        assert call_args[1]["exc_info"] is True

    def test_log_error_with_context(self, mock_logger):
        """Test logging error with context"""
        struct_logger = StructuredLogger(mock_logger)
        error = RuntimeError("Processing failed")
        context = {"document_id": "doc123", "step": "extraction"}
        struct_logger.log_error(error, context=context)

        call_args = mock_logger.error.call_args_list[0]
        error_context = call_args[1]["extra"]["context"]
        assert error_context["document_id"] == "doc123"
        assert error_context["step"] == "extraction"

    def test_log_error_with_user_message(self, mock_logger):
        """Test logging error with user-friendly message"""
        struct_logger = StructuredLogger(mock_logger)
        error = ConnectionError("Database connection lost")
        struct_logger.log_error(error, user_message="Please try again later")

        call_args = mock_logger.error.call_args_list[0]
        error_context = call_args[1]["extra"]["context"]
        assert error_context["user_message"] == "Please try again later"

    def test_log_error_includes_error_type(self, mock_logger):
        """Test log_error includes error type in context"""
        struct_logger = StructuredLogger(mock_logger)
        error = KeyError("missing_key")
        struct_logger.log_error(error)

        call_args = mock_logger.error.call_args_list[0]
        error_context = call_args[1]["extra"]["context"]
        assert error_context["error_type"] == "KeyError"
        assert error_context["error_message"] == "'missing_key'"


class TestLogMessageTemplates:
    """Test LogMessageTemplates class"""

    def test_document_templates_exist(self):
        """Test document operation templates exist"""
        assert hasattr(LogMessageTemplates, "DOCUMENT_PARSED")
        assert hasattr(LogMessageTemplates, "DOCUMENT_SAVED")
        assert hasattr(LogMessageTemplates, "DOCUMENT_DELETED")
        assert hasattr(LogMessageTemplates, "DOCUMENT_EXPORTED")

    def test_user_templates_exist(self):
        """Test user operation templates exist"""
        assert hasattr(LogMessageTemplates, "USER_LOGIN")
        assert hasattr(LogMessageTemplates, "USER_LOGOUT")
        assert hasattr(LogMessageTemplates, "USER_CREATED")
        assert hasattr(LogMessageTemplates, "USER_UPDATED")
        assert hasattr(LogMessageTemplates, "USER_DELETED")

    def test_system_templates_exist(self):
        """Test system operation templates exist"""
        assert hasattr(LogMessageTemplates, "SYSTEM_STARTUP")
        assert hasattr(LogMessageTemplates, "SYSTEM_SHUTDOWN")
        assert hasattr(LogMessageTemplates, "SYSTEM_ERROR")
        assert hasattr(LogMessageTemplates, "SYSTEM_HEALTH_CHECK")

    def test_processing_templates_exist(self):
        """Test processing operation templates exist"""
        assert hasattr(LogMessageTemplates, "PROCESSING_STARTED")
        assert hasattr(LogMessageTemplates, "PROCESSING_COMPLETED")
        assert hasattr(LogMessageTemplates, "PROCESSING_FAILED")
        assert hasattr(LogMessageTemplates, "PROCESSING_PROGRESS")

    def test_database_templates_exist(self):
        """Test database operation templates exist"""
        assert hasattr(LogMessageTemplates, "DB_QUERY")
        assert hasattr(LogMessageTemplates, "DB_CONNECTION")
        assert hasattr(LogMessageTemplates, "DB_MIGRATION")
        assert hasattr(LogMessageTemplates, "DB_BACKUP")

    def test_api_templates_exist(self):
        """Test API operation templates exist"""
        assert hasattr(LogMessageTemplates, "API_CALL")
        assert hasattr(LogMessageTemplates, "API_AUTH_SUCCESS")
        assert hasattr(LogMessageTemplates, "API_AUTH_FAILED")
        assert hasattr(LogMessageTemplates, "API_RATE_LIMIT")

    def test_security_templates_exist(self):
        """Test security event templates exist"""
        assert hasattr(LogMessageTemplates, "SECURITY_ACCESS_DENIED")
        assert hasattr(LogMessageTemplates, "SECURITY_SUSPICIOUS")
        assert hasattr(LogMessageTemplates, "SECURITY_VIOLATION")

    def test_template_format_basic(self):
        """Test basic template formatting"""
        result = LogMessageTemplates.format(LogMessageTemplates.USER_LOGIN, username="alice", ip="192.168.1.1")
        assert "alice" in result
        assert "192.168.1.1" in result
        assert "[USER]" in result

    def test_template_format_document_parsed(self):
        """Test formatting document parsed template"""
        result = LogMessageTemplates.format(
            LogMessageTemplates.DOCUMENT_PARSED, doc_name="report.pdf", size=1024000, pages=50
        )
        assert "report.pdf" in result
        assert "1024000" in result
        assert "50" in result

    def test_template_format_processing_progress(self):
        """Test formatting processing progress template"""
        result = LogMessageTemplates.format(
            LogMessageTemplates.PROCESSING_PROGRESS, task_id="task123", percent=75, current=75, total=100
        )
        assert "task123" in result
        assert "75%" in result
        assert "75/100" in result

    def test_template_format_api_call(self):
        """Test formatting API call template"""
        result = LogMessageTemplates.format(
            LogMessageTemplates.API_CALL, method="POST", endpoint="/api/upload", status_code=201, duration=250
        )
        assert "POST" in result
        assert "/api/upload" in result
        assert "201" in result
        assert "250" in result

    def test_template_format_system_startup(self):
        """Test formatting system startup template"""
        result = LogMessageTemplates.format(LogMessageTemplates.SYSTEM_STARTUP, service_name="DocumentMS", version="2.0")
        assert "DocumentMS" in result
        assert "2.0" in result


class TestConvenienceFunctions:
    """Test convenience functions for logger creation"""

    def test_get_performance_logger_default_name(self):
        """Test get_performance_logger with default name"""
        perf_logger = get_performance_logger()
        assert isinstance(perf_logger, PerformanceLogger)
        assert perf_logger.logger.name == "performance"

    def test_get_performance_logger_custom_name(self):
        """Test get_performance_logger with custom name"""
        perf_logger = get_performance_logger("custom_perf")
        assert isinstance(perf_logger, PerformanceLogger)
        assert perf_logger.logger.name == "custom_perf"

    def test_get_audit_logger_default_name(self):
        """Test get_audit_logger with default name"""
        audit_logger = get_audit_logger()
        assert isinstance(audit_logger, AuditLogger)
        assert audit_logger.logger.name == "audit"

    def test_get_audit_logger_custom_name(self):
        """Test get_audit_logger with custom name"""
        audit_logger = get_audit_logger("custom_audit")
        assert isinstance(audit_logger, AuditLogger)
        assert audit_logger.logger.name == "custom_audit"

    def test_get_audit_logger_with_path(self, tmp_path):
        """Test get_audit_logger with audit log path"""
        audit_path = tmp_path / "audit.log"
        audit_logger = get_audit_logger(audit_log_path=audit_path)
        assert isinstance(audit_logger, AuditLogger)
        assert audit_logger.audit_log_path == audit_path

    def test_get_structured_logger(self):
        """Test get_structured_logger"""
        struct_logger = get_structured_logger("my_logger")
        assert isinstance(struct_logger, StructuredLogger)
        assert struct_logger.logger.name == "my_logger"


class TestIntegrationScenarios:
    """Test integration scenarios with multiple loggers"""

    def test_performance_and_audit_together(self, mock_logger):
        """Test using performance and audit logging together"""
        perf_logger = PerformanceLogger(mock_logger)
        audit_logger = AuditLogger(mock_logger)

        with perf_logger.measure("sensitive_operation", user="alice"):
            audit_logger.log_pii_access("alice", "customer_emails", "marketing campaign")

        # Both loggers should have logged
        assert mock_logger.info.call_count == 3  # 2 from perf, 1 from audit

    def test_structured_logger_error_flow(self, mock_logger):
        """Test structured logger handling full error flow"""
        struct_logger = StructuredLogger(mock_logger)

        # Start operation
        struct_logger.log_operation("import", "started", entity_type="dataset", entity_id="ds123")

        # Log error
        try:
            raise ValueError("Invalid data format")
        except ValueError as e:
            struct_logger.log_error(e, context={"dataset_id": "ds123"})

        # Failed operation
        struct_logger.log_operation("import", "failed", entity_type="dataset", entity_id="ds123", error="Invalid data")

        assert mock_logger.log.call_count == 2  # started and failed operations
        assert mock_logger.error.call_count == 1  # error log

    def test_full_request_lifecycle(self, mock_logger):
        """Test logging full request lifecycle"""
        struct_logger = StructuredLogger(mock_logger)
        perf_logger = PerformanceLogger(mock_logger)

        with perf_logger.measure("api_request"):
            struct_logger.log_request("POST", "/api/documents", user="bob", status_code=201, duration=0.45)

        # Request logged and performance measured
        assert mock_logger.info.call_count == 3  # start, request, complete
