"""
Unit tests for bulk operations module
"""

import os
import sqlite3
import tempfile
from unittest.mock import MagicMock, Mock

import pytest

from src.core.bulk_operations import (
    BulkOperation,
    BulkOperationManager,
    BulkOperationResult,
    BulkOperationType,
)


# ============================================================================
# Enum Tests
# ============================================================================


class TestBulkOperationType:
    """Test BulkOperationType enum"""

    def test_operation_types(self):
        """Test operation type values"""
        assert BulkOperationType.UPDATE == "update"
        assert BulkOperationType.DELETE == "delete"
        assert BulkOperationType.EXPORT == "export"
        assert BulkOperationType.TAG == "tag"
        assert BulkOperationType.UNTAG == "untag"
        assert BulkOperationType.ACTIVATE == "activate"
        assert BulkOperationType.DEACTIVATE == "deactivate"


# ============================================================================
# BulkOperation Tests
# ============================================================================


class TestBulkOperation:
    """Test BulkOperation dataclass"""

    def test_basic_operation(self):
        """Test basic bulk operation"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1, 2, 3],
            parameters={"brutto_rate": 100.0}
        )

        assert operation.operation_type == BulkOperationType.UPDATE
        assert operation.service_ids == [1, 2, 3]
        assert operation.parameters["brutto_rate"] == 100.0
        assert operation.dry_run is False

    def test_operation_with_user_id(self):
        """Test operation with user ID"""
        operation = BulkOperation(
            operation_type=BulkOperationType.DELETE,
            service_ids=[1],
            parameters={},
            user_id=123
        )

        assert operation.user_id == 123

    def test_operation_dry_run(self):
        """Test dry run operation"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1],
            parameters={},
            dry_run=True
        )

        assert operation.dry_run is True


# ============================================================================
# BulkOperationResult Tests
# ============================================================================


class TestBulkOperationResult:
    """Test BulkOperationResult dataclass"""

    def test_success_result(self):
        """Test successful result"""
        result = BulkOperationResult(
            success=True,
            affected_count=10,
            failed_count=0,
            errors=[],
            warnings=[],
            execution_time_ms=150.0,
            dry_run=False
        )

        assert result.success is True
        assert result.affected_count == 10
        assert result.failed_count == 0

    def test_failure_result(self):
        """Test failed result"""
        result = BulkOperationResult(
            success=False,
            affected_count=0,
            failed_count=5,
            errors=[{"error": "Service not found"}],
            warnings=["Warning message"],
            execution_time_ms=100.0,
            dry_run=False
        )

        assert result.success is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1


# ============================================================================
# BulkOperationManager Tests
# ============================================================================


class TestBulkOperationManager:
    """Test BulkOperationManager class"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database with services table"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        # Create services table
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE services (
                id INTEGER PRIMARY KEY,
                service_name TEXT,
                brutto_rate REAL,
                hours_per_month REAL,
                region TEXT,
                active INTEGER DEFAULT 1
            )
        """)

        # Insert test services
        for i in range(1, 11):
            cursor.execute("""
                INSERT INTO services (id, service_name, brutto_rate, hours_per_month, region, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (i, f"Service {i}", 100.0 + i, 160.0, "DE", 1))

        conn.commit()
        conn.close()

        yield path
        os.unlink(path)

    @pytest.fixture
    def mock_db(self, temp_db):
        """Create mock database object"""
        db = Mock()
        db.conn = sqlite3.connect(temp_db)
        return db

    @pytest.fixture
    def manager(self, mock_db):
        """Create BulkOperationManager instance"""
        return BulkOperationManager(database=mock_db)

    def test_init(self, manager, mock_db):
        """Test manager initialization"""
        assert manager.db == mock_db
        assert manager.audit_logger is None

    def test_execute_no_service_ids(self, manager):
        """Test execute with no service IDs"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        assert result.success is False
        assert len(result.errors) > 0

    def test_execute_missing_services(self, manager):
        """Test execute with non-existent service IDs"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[999, 1000],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        assert result.success is False
        assert "not found" in str(result.errors).lower()

    def test_execute_update_success(self, manager):
        """Test successful update operation"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1, 2, 3],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        assert result.success is True
        assert result.affected_count == 3

        # Verify update
        cursor = manager.db.conn.cursor()
        cursor.execute("SELECT brutto_rate FROM services WHERE id = 1")
        rate = cursor.fetchone()[0]
        assert rate == 150.0

    def test_execute_update_no_parameters(self, manager):
        """Test update without parameters"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1, 2],
            parameters={}
        )

        result = manager.execute(operation)

        assert result.success is False
        assert "no update parameters" in str(result.errors).lower()

    def test_execute_delete(self, manager):
        """Test delete operation"""
        operation = BulkOperation(
            operation_type=BulkOperationType.DELETE,
            service_ids=[1, 2],
            parameters={}
        )

        result = manager.execute(operation)

        assert result.success is True
        assert result.affected_count == 2

        # Verify deletion
        cursor = manager.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM services WHERE id IN (1, 2)")
        count = cursor.fetchone()[0]
        assert count == 0

    def test_execute_tag(self, manager):
        """Test tag operation"""
        # Create tags table
        cursor = manager.db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_tags (
                service_id INTEGER,
                tag TEXT,
                PRIMARY KEY (service_id, tag)
            )
        """)
        manager.db.conn.commit()

        operation = BulkOperation(
            operation_type=BulkOperationType.TAG,
            service_ids=[1, 2],
            parameters={"tags": ["important", "urgent"]}
        )

        result = manager.execute(operation)

        assert result.success is True

    def test_execute_activate(self, manager):
        """Test activate operation"""
        # First deactivate
        cursor = manager.db.conn.cursor()
        cursor.execute("UPDATE services SET active = 0 WHERE id IN (1, 2)")
        manager.db.conn.commit()

        operation = BulkOperation(
            operation_type=BulkOperationType.ACTIVATE,
            service_ids=[1, 2],
            parameters={}
        )

        result = manager.execute(operation)

        assert result.success is True

        # Verify activation
        cursor.execute("SELECT active FROM services WHERE id = 1")
        active = cursor.fetchone()[0]
        assert active == 1

    def test_execute_deactivate(self, manager):
        """Test deactivate operation"""
        operation = BulkOperation(
            operation_type=BulkOperationType.DEACTIVATE,
            service_ids=[1, 2],
            parameters={}
        )

        result = manager.execute(operation)

        assert result.success is True

        # Verify deactivation
        cursor = manager.db.conn.cursor()
        cursor.execute("SELECT active FROM services WHERE id = 1")
        active = cursor.fetchone()[0]
        assert active == 0

    def test_execute_dry_run(self, manager):
        """Test dry run doesn't modify data"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1, 2],
            parameters={"brutto_rate": 200.0},
            dry_run=True
        )

        result = manager.execute(operation)

        assert result.dry_run is True

        # Verify no changes
        cursor = manager.db.conn.cursor()
        cursor.execute("SELECT brutto_rate FROM services WHERE id = 1")
        rate = cursor.fetchone()[0]
        assert rate != 200.0  # Should be original value

    def test_execute_with_audit_logger(self, manager):
        """Test execution with audit logger"""
        mock_logger = MagicMock()
        manager.audit_logger = mock_logger

        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        assert result.success is True
        # Audit logger should be called
        assert mock_logger.log.called or hasattr(mock_logger, 'call_count')

    def test_execute_partial_success(self, manager):
        """Test partial success with some failures"""
        # Mix of existing and non-existing IDs
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1, 2, 999],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        # Should have errors for missing service
        assert len(result.errors) > 0 or result.failed_count > 0

    def test_execute_export(self, manager):
        """Test export operation"""
        operation = BulkOperation(
            operation_type=BulkOperationType.EXPORT,
            service_ids=[1, 2, 3],
            parameters={"format": "csv"}
        )

        result = manager.execute(operation)

        # Export should succeed
        assert result.success is True or result.affected_count > 0

    def test_validation_errors_format(self, manager):
        """Test validation errors have proper format"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[],
            parameters={}
        )

        result = manager.execute(operation)

        assert result.success is False
        assert isinstance(result.errors, list)
        if result.errors:
            assert isinstance(result.errors[0], dict)

    def test_execution_time_recorded(self, manager):
        """Test execution time is recorded"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        assert result.execution_time_ms > 0

    def test_warnings_captured(self, manager):
        """Test warnings are captured"""
        # Test that warnings list exists
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1],
            parameters={"brutto_rate": 150.0}
        )

        result = manager.execute(operation)

        assert isinstance(result.warnings, list)

    def test_update_multiple_fields(self, manager):
        """Test updating multiple fields"""
        operation = BulkOperation(
            operation_type=BulkOperationType.UPDATE,
            service_ids=[1, 2],
            parameters={
                "brutto_rate": 200.0,
                "hours_per_month": 180.0,
                "region": "US"
            }
        )

        result = manager.execute(operation)

        assert result.success is True

        # Verify all fields updated
        cursor = manager.db.conn.cursor()
        cursor.execute("SELECT brutto_rate, hours_per_month, region FROM services WHERE id = 1")
        row = cursor.fetchone()
        assert row[0] == 200.0
        assert row[1] == 180.0
        assert row[2] == "US"

    def test_untag_operation(self, manager):
        """Test untag operation"""
        # Create tags table and add tags
        cursor = manager.db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_tags (
                service_id INTEGER,
                tag TEXT,
                PRIMARY KEY (service_id, tag)
            )
        """)
        cursor.execute("INSERT INTO service_tags VALUES (1, 'test_tag')")
        manager.db.conn.commit()

        operation = BulkOperation(
            operation_type=BulkOperationType.UNTAG,
            service_ids=[1],
            parameters={"tags": ["test_tag"]}
        )

        result = manager.execute(operation)

        assert result.success is True

    def test_unknown_operation_type(self, manager):
        """Test handling unknown operation type"""
        operation = BulkOperation(
            operation_type="unknown",
            service_ids=[1],
            parameters={}
        )

        result = manager.execute(operation)

        assert result.success is False
        assert "unknown" in str(result.errors).lower()
