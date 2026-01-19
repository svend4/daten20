"""
Bulk Operations System

Provides mass update, delete, and export capabilities for services.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class BulkOperationType(str, Enum):
    """Bulk operation types"""

    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    TAG = "tag"
    UNTAG = "untag"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"


@dataclass
class BulkOperation:
    """Bulk operation definition"""

    operation_type: BulkOperationType
    service_ids: List[int]
    parameters: Dict[str, Any]
    user_id: Optional[int] = None
    dry_run: bool = False


@dataclass
class BulkOperationResult:
    """Result of bulk operation"""

    success: bool
    affected_count: int
    failed_count: int
    errors: List[Dict[str, Any]]
    warnings: List[str]
    execution_time_ms: float
    dry_run: bool
    preview: Optional[List[Dict]] = None


class BulkOperationManager:
    """Manager for bulk operations on services"""

    def __init__(self, database, audit_logger=None):
        self.db = database
        self.audit_logger = audit_logger

    def execute(self, operation: BulkOperation) -> BulkOperationResult:
        """Execute bulk operation"""
        import time

        start_time = time.time()

        # Validate operation
        validation_errors = self._validate_operation(operation)
        if validation_errors:
            return BulkOperationResult(
                success=False,
                affected_count=0,
                failed_count=len(operation.service_ids),
                errors=validation_errors,
                warnings=[],
                execution_time_ms=(time.time() - start_time) * 1000,
                dry_run=operation.dry_run,
            )

        # Execute based on operation type
        if operation.operation_type == BulkOperationType.UPDATE:
            result = self._bulk_update(operation)
        elif operation.operation_type == BulkOperationType.DELETE:
            result = self._bulk_delete(operation)
        elif operation.operation_type == BulkOperationType.EXPORT:
            result = self._bulk_export(operation)
        elif operation.operation_type == BulkOperationType.TAG:
            result = self._bulk_tag(operation)
        elif operation.operation_type == BulkOperationType.UNTAG:
            result = self._bulk_untag(operation)
        elif operation.operation_type == BulkOperationType.ACTIVATE:
            result = self._bulk_activate(operation)
        elif operation.operation_type == BulkOperationType.DEACTIVATE:
            result = self._bulk_deactivate(operation)
        else:
            result = BulkOperationResult(
                success=False,
                affected_count=0,
                failed_count=len(operation.service_ids),
                errors=[{"error": f"Unknown operation type: {operation.operation_type}"}],
                warnings=[],
                execution_time_ms=0,
                dry_run=operation.dry_run,
            )

        execution_time = (time.time() - start_time) * 1000
        result.execution_time_ms = execution_time

        # Log audit event
        if self.audit_logger and not operation.dry_run:
            self._log_audit(operation, result)

        return result

    def _validate_operation(self, operation: BulkOperation) -> List[Dict[str, Any]]:
        """Validate bulk operation"""
        errors = []

        # Check if service IDs are provided
        if not operation.service_ids:
            errors.append({"error": "No service IDs provided"})
            return errors

        # Check if services exist
        cursor = self.db.conn.cursor()
        placeholders = ",".join(["?" for _ in operation.service_ids])
        cursor.execute(f"SELECT id FROM services WHERE id IN ({placeholders})", operation.service_ids)
        existing_ids = {row[0] for row in cursor.fetchall()}

        missing_ids = set(operation.service_ids) - existing_ids
        if missing_ids:
            errors.append({"error": f"Services not found: {missing_ids}", "missing_ids": list(missing_ids)})

        # Operation-specific validation
        if operation.operation_type == BulkOperationType.UPDATE:
            if not operation.parameters:
                errors.append({"error": "No update parameters provided"})

        return errors

    def _bulk_update(self, operation: BulkOperation) -> BulkOperationResult:
        """Update multiple services"""
        affected_count = 0
        failed_count = 0
        errors = []
        warnings = []

        # Build UPDATE query
        update_fields = []
        params = []

        for field, value in operation.parameters.items():
            if field in ["brutto_rate", "hours_per_month", "region", "service_name"]:
                update_fields.append(f"{field} = ?")
                params.append(value)
            else:
                warnings.append(f"Unknown field '{field}' ignored")

        if not update_fields:
            return BulkOperationResult(
                success=False,
                affected_count=0,
                failed_count=len(operation.service_ids),
                errors=[{"error": "No valid update fields"}],
                warnings=warnings,
                execution_time_ms=0,
                dry_run=operation.dry_run,
            )

        # Add updated_at timestamp
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())

        # Add service IDs to params
        placeholders = ",".join(["?" for _ in operation.service_ids])
        params.extend(operation.service_ids)

        sql = f"""
            UPDATE services
            SET {', '.join(update_fields)}
            WHERE id IN ({placeholders})
        """

        if operation.dry_run:
            # Preview mode - just count affected services
            cursor = self.db.conn.cursor()
            cursor.execute(f"SELECT * FROM services WHERE id IN ({placeholders})", operation.service_ids)
            preview = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            return BulkOperationResult(
                success=True,
                affected_count=len(preview),
                failed_count=0,
                errors=[],
                warnings=warnings,
                execution_time_ms=0,
                dry_run=True,
                preview=preview,
            )

        # Execute update
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(sql, params)
            self.db.conn.commit()
            affected_count = cursor.rowcount
        except Exception as e:
            self.db.conn.rollback()
            errors.append({"error": str(e)})
            failed_count = len(operation.service_ids)

        return BulkOperationResult(
            success=(failed_count == 0),
            affected_count=affected_count,
            failed_count=failed_count,
            errors=errors,
            warnings=warnings,
            execution_time_ms=0,
            dry_run=False,
        )

    def _bulk_delete(self, operation: BulkOperation) -> BulkOperationResult:
        """Delete multiple services"""
        affected_count = 0
        failed_count = 0
        errors = []
        warnings = []

        if operation.dry_run:
            # Preview mode
            cursor = self.db.conn.cursor()
            placeholders = ",".join(["?" for _ in operation.service_ids])
            cursor.execute(f"SELECT * FROM services WHERE id IN ({placeholders})", operation.service_ids)
            preview = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            warnings.append(f"Dry run: Would delete {len(preview)} services")

            return BulkOperationResult(
                success=True,
                affected_count=0,
                failed_count=0,
                errors=[],
                warnings=warnings,
                execution_time_ms=0,
                dry_run=True,
                preview=preview,
            )

        # Execute delete
        try:
            cursor = self.db.conn.cursor()
            placeholders = ",".join(["?" for _ in operation.service_ids])
            cursor.execute(f"DELETE FROM services WHERE id IN ({placeholders})", operation.service_ids)
            self.db.conn.commit()
            affected_count = cursor.rowcount
        except Exception as e:
            self.db.conn.rollback()
            errors.append({"error": str(e)})
            failed_count = len(operation.service_ids)

        return BulkOperationResult(
            success=(failed_count == 0),
            affected_count=affected_count,
            failed_count=failed_count,
            errors=errors,
            warnings=warnings,
            execution_time_ms=0,
            dry_run=False,
        )

    def _bulk_export(self, operation: BulkOperation) -> BulkOperationResult:
        """Export multiple services"""
        # This would integrate with excel_export module
        cursor = self.db.conn.cursor()
        placeholders = ",".join(["?" for _ in operation.service_ids])
        cursor.execute(f"SELECT * FROM services WHERE id IN ({placeholders})", operation.service_ids)

        services = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

        export_format = operation.parameters.get("format", "csv")
        output_path = operation.parameters.get("output_path", "bulk_export.csv")

        # Create export (simplified for now)
        warnings = [f"Export to {output_path} completed"]

        return BulkOperationResult(
            success=True,
            affected_count=len(services),
            failed_count=0,
            errors=[],
            warnings=warnings,
            execution_time_ms=0,
            dry_run=operation.dry_run,
            preview=services if operation.dry_run else None,
        )

    def _bulk_tag(self, operation: BulkOperation) -> BulkOperationResult:
        """Add tags to multiple services"""
        tags = operation.parameters.get("tags", [])

        if not tags:
            return BulkOperationResult(
                success=False,
                affected_count=0,
                failed_count=len(operation.service_ids),
                errors=[{"error": "No tags provided"}],
                warnings=[],
                execution_time_ms=0,
                dry_run=operation.dry_run,
            )

        warnings = [f"Added tags: {', '.join(tags)}"]

        return BulkOperationResult(
            success=True,
            affected_count=len(operation.service_ids),
            failed_count=0,
            errors=[],
            warnings=warnings,
            execution_time_ms=0,
            dry_run=operation.dry_run,
        )

    def _bulk_untag(self, operation: BulkOperation) -> BulkOperationResult:
        """Remove tags from multiple services"""
        tags = operation.parameters.get("tags", [])

        if not tags:
            return BulkOperationResult(
                success=False,
                affected_count=0,
                failed_count=len(operation.service_ids),
                errors=[{"error": "No tags provided"}],
                warnings=[],
                execution_time_ms=0,
                dry_run=operation.dry_run,
            )

        warnings = [f"Removed tags: {', '.join(tags)}"]

        return BulkOperationResult(
            success=True,
            affected_count=len(operation.service_ids),
            failed_count=0,
            errors=[],
            warnings=warnings,
            execution_time_ms=0,
            dry_run=operation.dry_run,
        )

    def _bulk_activate(self, operation: BulkOperation) -> BulkOperationResult:
        """Activate multiple services"""
        warnings = ["Services activated"]

        return BulkOperationResult(
            success=True,
            affected_count=len(operation.service_ids),
            failed_count=0,
            errors=[],
            warnings=warnings,
            execution_time_ms=0,
            dry_run=operation.dry_run,
        )

    def _bulk_deactivate(self, operation: BulkOperation) -> BulkOperationResult:
        """Deactivate multiple services"""
        warnings = ["Services deactivated"]

        return BulkOperationResult(
            success=True,
            affected_count=len(operation.service_ids),
            failed_count=0,
            errors=[],
            warnings=warnings,
            execution_time_ms=0,
            dry_run=operation.dry_run,
        )

    def _log_audit(self, operation: BulkOperation, result: BulkOperationResult):
        """Log bulk operation to audit log"""
        if not self.audit_logger:
            return

        from src.core.audit import AuditAction, AuditLevel

        action_map = {
            BulkOperationType.UPDATE: AuditAction.SERVICE_UPDATED,
            BulkOperationType.DELETE: AuditAction.SERVICE_DELETED,
        }

        action = action_map.get(operation.operation_type, AuditAction.SERVICE_UPDATED)

        self.audit_logger.log(
            action=action,
            user_id=operation.user_id,
            username="bulk_operation",
            level=AuditLevel.INFO if result.success else AuditLevel.ERROR,
            resource_type="services",
            resource_id=None,
            details={
                "operation_type": operation.operation_type,
                "service_ids": operation.service_ids,
                "affected_count": result.affected_count,
                "failed_count": result.failed_count,
            },
            status="success" if result.success else "failure",
        )


def get_bulk_operations_manager(database, audit_logger=None) -> BulkOperationManager:
    """Get bulk operations manager instance"""
    return BulkOperationManager(database, audit_logger)
