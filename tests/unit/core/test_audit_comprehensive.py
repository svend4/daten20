"""
Comprehensive tests for Audit Logging module (src/core/audit.py)

Test coverage goals:
- AuditAction & AuditLevel enums
- AuditEntry dataclass (initialization, to_dict, defaults)
- AuditLogger class (initialization, database creation, logging)
- Audit retrieval (get_entries with filters, pagination)
- Statistics and activity reports
- Decorator (@audit_log for automatic logging)
- Flask request context handling
- Error handling

Target: 20+ tests, 90%+ coverage of audit.py
"""

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.audit import (
    AuditAction,
    AuditEntry,
    AuditLevel,
    AuditLogger,
    audit_log,
    get_audit_logger,
)


class TestAuditEnums:
    """Test Audit enum types"""

    def test_audit_action_values(self):
        """Test AuditAction enum has expected values"""
        # Authentication actions
        assert AuditAction.LOGIN.value == "auth.login"
        assert AuditAction.LOGOUT.value == "auth.logout"
        assert AuditAction.LOGIN_FAILED.value == "auth.login_failed"

        # User management
        assert AuditAction.USER_CREATED.value == "user.created"
        assert AuditAction.USER_UPDATED.value == "user.updated"

        # Service operations
        assert AuditAction.SERVICE_CREATED.value == "service.created"
        assert AuditAction.SERVICE_VIEWED.value == "service.viewed"

    def test_audit_level_values(self):
        """Test AuditLevel enum has expected values"""
        assert AuditLevel.INFO.value == "info"
        assert AuditLevel.WARNING.value == "warning"
        assert AuditLevel.ERROR.value == "error"
        assert AuditLevel.CRITICAL.value == "critical"


class TestAuditEntry:
    """Test AuditEntry dataclass"""

    def test_audit_entry_initialization(self):
        """Test AuditEntry initialization with defaults"""
        entry = AuditEntry(
            user_id=1,
            username="testuser",
            action="test.action",
        )

        assert entry.user_id == 1
        assert entry.username == "testuser"
        assert entry.action == "test.action"
        assert entry.level == AuditLevel.INFO
        assert entry.status == "success"
        assert entry.details == {}
        assert entry.error_message is None
        assert isinstance(entry.timestamp, datetime)

    def test_audit_entry_with_all_fields(self):
        """Test AuditEntry with all fields specified"""
        timestamp = datetime.now()
        details = {"key": "value", "count": 42}

        entry = AuditEntry(
            id=123,
            timestamp=timestamp,
            user_id=5,
            username="admin",
            action=AuditAction.SERVICE_CREATED.value,
            level=AuditLevel.WARNING,
            resource_type="service",
            resource_id="service-123",
            details=details,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            status="failed",
            error_message="Test error",
        )

        assert entry.id == 123
        assert entry.timestamp == timestamp
        assert entry.user_id == 5
        assert entry.username == "admin"
        assert entry.action == AuditAction.SERVICE_CREATED.value
        assert entry.level == AuditLevel.WARNING
        assert entry.resource_type == "service"
        assert entry.resource_id == "service-123"
        assert entry.details == details
        assert entry.ip_address == "192.168.1.1"
        assert entry.user_agent == "Mozilla/5.0"
        assert entry.status == "failed"
        assert entry.error_message == "Test error"

    def test_audit_entry_to_dict(self):
        """Test converting AuditEntry to dictionary"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        entry = AuditEntry(
            id=1,
            timestamp=timestamp,
            user_id=10,
            username="user",
            action="test.action",
            level=AuditLevel.INFO,
            resource_type="document",
            resource_id="doc-1",
            details={"field": "value"},
            ip_address="127.0.0.1",
            user_agent="TestAgent",
            status="success",
        )

        result = entry.to_dict()

        assert result["id"] == 1
        assert result["timestamp"] == timestamp.isoformat()
        assert result["user_id"] == 10
        assert result["username"] == "user"
        assert result["action"] == "test.action"
        assert result["level"] == "info"
        assert result["resource_type"] == "document"
        assert result["resource_id"] == "doc-1"
        assert result["details"] == {"field": "value"}
        assert result["ip_address"] == "127.0.0.1"
        assert result["user_agent"] == "TestAgent"
        assert result["status"] == "success"


class TestAuditLogger:
    """Test AuditLogger class"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def audit_logger(self, temp_db):
        """Create AuditLogger with temporary database"""
        return AuditLogger(db_path=temp_db)

    def test_initialization_creates_database(self, temp_db):
        """Test that initialization creates database and table"""
        logger = AuditLogger(db_path=temp_db)

        # Verify database file exists
        assert os.path.exists(temp_db)

        # Verify table structure
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "audit_log"

    def test_log_basic_entry(self, audit_logger, temp_db):
        """Test logging a basic audit entry"""
        entry_id = audit_logger.log(
            action=AuditAction.LOGIN,
            user_id=1,
            username="testuser",
        )

        assert entry_id > 0

        # Verify entry was saved
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[3] == "testuser"  # username
        assert row[4] == AuditAction.LOGIN.value  # action

    def test_log_with_all_parameters(self, audit_logger, temp_db):
        """Test logging with all parameters"""
        entry_id = audit_logger.log(
            action=AuditAction.SERVICE_CREATED,
            user_id=5,
            username="admin",
            level=AuditLevel.WARNING,
            resource_type="service",
            resource_id="svc-123",
            details={"name": "New Service", "type": "api"},
            status="success",
        )

        assert entry_id > 0

        # Verify all fields
        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()

        assert row["user_id"] == 5
        assert row["username"] == "admin"
        assert row["action"] == AuditAction.SERVICE_CREATED.value
        assert row["level"] == "warning"
        assert row["resource_type"] == "service"
        assert row["resource_id"] == "svc-123"
        assert json.loads(row["details"]) == {"name": "New Service", "type": "api"}
        assert row["status"] == "success"

    def test_log_with_flask_request_context(self, audit_logger):
        """Test logging captures Flask request context (IP, User-Agent)"""
        # Mock Flask request context
        mock_request = Mock()
        mock_request.remote_addr = "192.168.1.100"
        mock_request.headers = {"User-Agent": "TestBrowser/1.0"}

        with patch("src.core.audit.request", mock_request):
            entry_id = audit_logger.log(
                action=AuditAction.API_CALLED,
                user_id=1,
                username="api_user",
            )

        assert entry_id > 0

        # Verify request context was captured
        entries = audit_logger.get_entries()
        assert len(entries) > 0
        entry = entries[0]
        assert entry.ip_address == "192.168.1.100"
        assert entry.user_agent == "TestBrowser/1.0"

    def test_log_failure_with_error_message(self, audit_logger):
        """Test logging a failed operation with error message"""
        entry_id = audit_logger.log(
            action=AuditAction.SERVICE_UPDATED,
            user_id=1,
            username="user",
            level=AuditLevel.ERROR,
            status="failed",
            error_message="Validation failed: Invalid input",
        )

        assert entry_id > 0

        entries = audit_logger.get_entries()
        entry = entries[0]
        assert entry.status == "failed"
        assert entry.level == AuditLevel.ERROR
        assert entry.error_message == "Validation failed: Invalid input"

    def test_get_entries_no_filters(self, audit_logger):
        """Test retrieving all entries without filters"""
        # Add multiple entries
        audit_logger.log(AuditAction.LOGIN, user_id=1, username="user1")
        audit_logger.log(AuditAction.LOGOUT, user_id=1, username="user1")
        audit_logger.log(AuditAction.LOGIN, user_id=2, username="user2")

        entries = audit_logger.get_entries()

        assert len(entries) == 3
        # Should be ordered by timestamp descending (newest first)
        assert entries[0].action == AuditAction.LOGIN.value
        assert entries[0].username == "user2"

    def test_get_entries_filter_by_user(self, audit_logger):
        """Test filtering entries by user_id"""
        audit_logger.log(AuditAction.LOGIN, user_id=1, username="user1")
        audit_logger.log(AuditAction.LOGOUT, user_id=1, username="user1")
        audit_logger.log(AuditAction.LOGIN, user_id=2, username="user2")

        entries = audit_logger.get_entries(user_id=1)

        assert len(entries) == 2
        assert all(e.user_id == 1 for e in entries)

    def test_get_entries_filter_by_action(self, audit_logger):
        """Test filtering entries by action"""
        audit_logger.log(AuditAction.LOGIN, user_id=1, username="user1")
        audit_logger.log(AuditAction.LOGOUT, user_id=1, username="user1")
        audit_logger.log(AuditAction.LOGIN, user_id=2, username="user2")

        entries = audit_logger.get_entries(action=AuditAction.LOGIN.value)

        assert len(entries) == 2
        assert all(e.action == AuditAction.LOGIN.value for e in entries)

    def test_get_entries_filter_by_level(self, audit_logger):
        """Test filtering entries by audit level"""
        audit_logger.log(AuditAction.LOGIN, user_id=1, username="user1", level=AuditLevel.INFO)
        audit_logger.log(
            AuditAction.LOGIN_FAILED, user_id=1, username="user1", level=AuditLevel.WARNING
        )
        audit_logger.log(
            AuditAction.PERMISSION_DENIED, user_id=2, username="user2", level=AuditLevel.ERROR
        )

        entries = audit_logger.get_entries(level=AuditLevel.ERROR)

        assert len(entries) == 1
        assert entries[0].level == AuditLevel.ERROR

    def test_get_entries_filter_by_date_range(self, audit_logger):
        """Test filtering entries by date range"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Log entry with specific timestamp
        entry_id = audit_logger.log(AuditAction.LOGIN, user_id=1, username="user1")

        # Get entries in date range
        entries = audit_logger.get_entries(start_date=yesterday, end_date=tomorrow)

        assert len(entries) >= 1
        assert any(e.id == entry_id for e in entries)

    def test_get_entries_pagination(self, audit_logger):
        """Test pagination of entries"""
        # Add 10 entries
        for i in range(10):
            audit_logger.log(AuditAction.LOGIN, user_id=i, username=f"user{i}")

        # Get first page (5 entries)
        page1 = audit_logger.get_entries(limit=5, offset=0)
        assert len(page1) == 5

        # Get second page (next 5 entries)
        page2 = audit_logger.get_entries(limit=5, offset=5)
        assert len(page2) == 5

        # Entries should be different
        assert page1[0].id != page2[0].id

    def test_get_user_activity(self, audit_logger):
        """Test getting user activity summary"""
        user_id = 10

        # Log various actions for user
        audit_logger.log(AuditAction.LOGIN, user_id=user_id, username="testuser")
        audit_logger.log(AuditAction.LOGIN, user_id=user_id, username="testuser")
        audit_logger.log(AuditAction.SERVICE_VIEWED, user_id=user_id, username="testuser")
        audit_logger.log(AuditAction.LOGOUT, user_id=user_id, username="testuser")

        activity = audit_logger.get_user_activity(user_id, days=30)

        # Should have activity for LOGIN (2), SERVICE_VIEWED (1), LOGOUT (1)
        assert len(activity) > 0
        actions = {item["action"]: item["count"] for item in activity}
        assert actions.get(AuditAction.LOGIN.value, 0) == 2

    def test_get_statistics(self, audit_logger):
        """Test getting audit statistics"""
        # Log various entries with different levels and statuses
        audit_logger.log(AuditAction.LOGIN, user_id=1, username="user1", level=AuditLevel.INFO)
        audit_logger.log(AuditAction.LOGOUT, user_id=1, username="user1", level=AuditLevel.INFO)
        audit_logger.log(
            AuditAction.LOGIN_FAILED,
            user_id=2,
            username="user2",
            level=AuditLevel.WARNING,
            status="failed",
        )
        audit_logger.log(
            AuditAction.PERMISSION_DENIED,
            user_id=3,
            username="user3",
            level=AuditLevel.ERROR,
            status="failed",
        )

        stats = audit_logger.get_statistics(days=7)

        assert stats["total_entries"] >= 4
        assert stats["by_level"].get("info", 0) >= 2
        assert stats["by_level"].get("warning", 0) >= 1
        assert stats["by_level"].get("error", 0) >= 1
        assert stats["failed_operations"] >= 2
        assert stats["period_days"] == 7
        assert "top_actions" in stats


class TestAuditDecorator:
    """Test @audit_log decorator"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def audit_logger_instance(self, temp_db):
        """Create and set global audit logger"""
        import src.core.audit as audit_module

        logger = AuditLogger(db_path=temp_db)
        audit_module._audit_logger = logger
        yield logger
        audit_module._audit_logger = None

    def test_decorator_logs_successful_execution(self, audit_logger_instance):
        """Test that decorator logs successful function execution"""

        @audit_log(AuditAction.SERVICE_CREATED, resource_type="service")
        def create_service(name):
            class MockService:
                id = 123

            return MockService()

        # Create a simple mock object for g
        mock_g = type("MockG", (), {"user_id": 5, "username": "admin"})()

        # Mock Flask g context and request
        with patch("src.core.audit.g", mock_g), patch("src.core.audit.request", None):
            result = create_service("test_service")
            assert result.id == 123

        # Verify audit entry was created
        entries = audit_logger_instance.get_entries()
        assert len(entries) == 1
        entry = entries[0]
        assert entry.action == AuditAction.SERVICE_CREATED.value
        assert entry.user_id == 5
        assert entry.username == "admin"
        assert entry.resource_type == "service"
        assert entry.resource_id == "123"
        assert entry.status == "success"

    def test_decorator_logs_failed_execution(self, audit_logger_instance):
        """Test that decorator logs failed function execution"""

        @audit_log(AuditAction.SERVICE_UPDATED, resource_type="service")
        def update_service(service_id):
            raise ValueError("Invalid service ID")

        # Create a simple mock object for g
        mock_g = type("MockG", (), {"user_id": 5, "username": "admin"})()

        # Mock Flask g context and request
        with patch("src.core.audit.g", mock_g), patch("src.core.audit.request", None):
            with pytest.raises(ValueError, match="Invalid service ID"):
                update_service(999)

        # Verify audit entry was created with error
        entries = audit_logger_instance.get_entries()
        assert len(entries) == 1
        entry = entries[0]
        assert entry.action == AuditAction.SERVICE_UPDATED.value
        assert entry.level == AuditLevel.ERROR
        assert entry.status == "failed"
        assert "Invalid service ID" in entry.error_message

    def test_decorator_without_flask_context(self, audit_logger_instance):
        """Test decorator works without Flask context (g)"""

        @audit_log(AuditAction.API_CALLED)
        def api_function():
            return "result"

        # No Flask context
        with patch("src.core.audit.g", None):
            result = api_function()
            assert result == "result"

        # Verify audit entry was created (with None user_id/username)
        entries = audit_logger_instance.get_entries()
        assert len(entries) == 1
        entry = entries[0]
        assert entry.action == AuditAction.API_CALLED.value
        assert entry.user_id is None


class TestGlobalFunctions:
    """Test global helper functions"""

    def test_get_audit_logger_singleton(self):
        """Test that get_audit_logger returns singleton"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()

        assert logger1 is logger2

    def test_get_audit_logger_creates_instance(self):
        """Test that get_audit_logger creates AuditLogger instance"""
        import src.core.audit as audit_module

        # Reset global instance
        audit_module._audit_logger = None

        logger = get_audit_logger()

        assert logger is not None
        assert isinstance(logger, AuditLogger)


class TestIntegration:
    """Integration tests for audit system"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_complete_audit_workflow(self, temp_db):
        """Test complete audit logging workflow"""
        logger = AuditLogger(db_path=temp_db)

        # User login
        login_id = logger.log(
            action=AuditAction.LOGIN,
            user_id=1,
            username="john_doe",
            level=AuditLevel.INFO,
            details={"method": "password"},
        )
        assert login_id > 0

        # User creates service
        service_id = logger.log(
            action=AuditAction.SERVICE_CREATED,
            user_id=1,
            username="john_doe",
            resource_type="service",
            resource_id="svc-001",
            details={"name": "My Service"},
        )
        assert service_id > 0

        # User updates service
        update_id = logger.log(
            action=AuditAction.SERVICE_UPDATED,
            user_id=1,
            username="john_doe",
            resource_type="service",
            resource_id="svc-001",
            details={"changes": ["name", "description"]},
        )
        assert update_id > 0

        # User logs out
        logout_id = logger.log(
            action=AuditAction.LOGOUT,
            user_id=1,
            username="john_doe",
        )
        assert logout_id > 0

        # Verify all entries
        entries = logger.get_entries(user_id=1)
        assert len(entries) == 4

        # Verify user activity
        activity = logger.get_user_activity(user_id=1, days=1)
        assert len(activity) > 0

        # Verify statistics
        stats = logger.get_statistics(days=1)
        assert stats["total_entries"] >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
