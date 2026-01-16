"""
Comprehensive Audit Logging System

Track all system activities, user actions, and data changes for compliance and security.
Provides detailed audit trails with search, filtering, and reporting capabilities.
"""

import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional

from flask import g, request

logger = logging.getLogger("dms.audit")


class AuditAction(str, Enum):
    """Audit action types."""

    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    PASSWORD_CHANGED = "auth.password_changed"

    # User management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_ROLE_CHANGED = "user.role_changed"

    # Service operations
    SERVICE_CREATED = "service.created"
    SERVICE_VIEWED = "service.viewed"
    SERVICE_UPDATED = "service.updated"
    SERVICE_DELETED = "service.deleted"

    # Data operations
    DATA_EXPORTED = "data.exported"
    DATA_IMPORTED = "data.imported"
    DOCUMENT_GENERATED = "document.generated"

    # System operations
    CONFIG_CHANGED = "system.config_changed"
    BACKUP_CREATED = "system.backup_created"
    BACKUP_RESTORED = "system.backup_restored"

    # API operations
    API_CALLED = "api.called"
    API_ERROR = "api.error"

    # Security events
    PERMISSION_DENIED = "security.permission_denied"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"


class AuditLevel(str, Enum):
    """Audit severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """Single audit log entry."""

    id: Optional[int] = None
    timestamp: datetime = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str = ""
    level: AuditLevel = AuditLevel.INFO
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "level": self.level.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status,
            "error_message": self.error_message,
        }


class AuditLogger:
    """Manage audit logging."""

    def __init__(self, db_path: str = "data/db/audit.db"):
        """
        Initialize audit logger.

        Args:
            db_path: Path to audit database
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize audit database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                level TEXT DEFAULT 'info',
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                status TEXT DEFAULT 'success',
                error_message TEXT
            )
        """
        )

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log (timestamp)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_log (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_action ON audit_log (action)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_resource ON audit_log (resource_type, resource_id)"
        )

        conn.commit()
        conn.close()
        logger.info("Audit database initialized")

    def log(
        self,
        action: AuditAction,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        level: AuditLevel = AuditLevel.INFO,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> int:
        """
        Log an audit entry.

        Args:
            action: Action being logged
            user_id: User ID performing action
            username: Username performing action
            level: Severity level
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details
            status: Operation status
            error_message: Error message if failed

        Returns:
            Audit entry ID
        """
        # Get request context if available
        ip_address = None
        user_agent = None

        try:
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get("User-Agent", "")[:500]
        except:
            pass

        entry = AuditEntry(
            user_id=user_id,
            username=username,
            action=action.value,
            level=level,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
        )

        return self._save_entry(entry)

    def _save_entry(self, entry: AuditEntry) -> int:
        """Save audit entry to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO audit_log (
                timestamp, user_id, username, action, level,
                resource_type, resource_id, details,
                ip_address, user_agent, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                entry.timestamp.isoformat(),
                entry.user_id,
                entry.username,
                entry.action,
                entry.level.value,
                entry.resource_type,
                entry.resource_id,
                json.dumps(entry.details),
                entry.ip_address,
                entry.user_agent,
                entry.status,
                entry.error_message,
            ),
        )

        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Log to system logger based on level
        log_msg = f"AUDIT: {entry.action} by {entry.username or 'system'} - {entry.status}"
        if entry.level == AuditLevel.CRITICAL:
            logger.critical(log_msg)
        elif entry.level == AuditLevel.ERROR:
            logger.error(log_msg)
        elif entry.level == AuditLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return entry_id

    def get_entries(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEntry]:
        """
        Retrieve audit entries with filters.

        Args:
            user_id: Filter by user ID
            action: Filter by action
            level: Filter by severity level
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum results
            offset: Results offset

        Returns:
            List of audit entries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        if action:
            query += " AND action = ?"
            params.append(action)

        if level:
            query += " AND level = ?"
            params.append(level.value)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        entries = []
        for row in rows:
            entry = AuditEntry(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                user_id=row["user_id"],
                username=row["username"],
                action=row["action"],
                level=AuditLevel(row["level"]),
                resource_type=row["resource_type"],
                resource_id=row["resource_id"],
                details=json.loads(row["details"]) if row["details"] else {},
                ip_address=row["ip_address"],
                user_agent=row["user_agent"],
                status=row["status"],
                error_message=row["error_message"],
            )
            entries.append(entry)

        return entries

    def get_user_activity(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user activity summary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT action, COUNT(*) as count
            FROM audit_log
            WHERE user_id = ?
            AND timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY action
            ORDER BY count DESC
        """,
            (user_id, days),
        )

        results = cursor.fetchall()
        conn.close()

        return [{"action": row[0], "count": row[1]} for row in results]

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get audit statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total entries
        cursor.execute(
            """
            SELECT COUNT(*) FROM audit_log
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """,
            (days,),
        )
        total = cursor.fetchone()[0]

        # By level
        cursor.execute(
            """
            SELECT level, COUNT(*) FROM audit_log
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY level
        """,
            (days,),
        )
        by_level = dict(cursor.fetchall())

        # By action
        cursor.execute(
            """
            SELECT action, COUNT(*) FROM audit_log
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY action
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """,
            (days,),
        )
        top_actions = dict(cursor.fetchall())

        # Failed operations
        cursor.execute(
            """
            SELECT COUNT(*) FROM audit_log
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            AND status = 'failed'
        """,
            (days,),
        )
        failed = cursor.fetchone()[0]

        conn.close()

        return {
            "total_entries": total,
            "by_level": by_level,
            "top_actions": top_actions,
            "failed_operations": failed,
            "period_days": days,
        }


# Decorator for automatic audit logging
def audit_log(action: AuditAction, resource_type: Optional[str] = None):
    """
    Decorator to automatically log function execution.

    Args:
        action: Action being performed
        resource_type: Type of resource

    Example:
        @audit_log(AuditAction.SERVICE_CREATED, 'service')
        def create_service(data):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auditor = get_audit_logger()

            # Get user info from context
            user_id = getattr(g, "user_id", None)
            username = getattr(g, "username", None)

            try:
                result = func(*args, **kwargs)

                # Log successful execution
                resource_id = None
                if hasattr(result, "id"):
                    resource_id = str(result.id)

                auditor.log(
                    action=action,
                    user_id=user_id,
                    username=username,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status="success",
                )

                return result

            except Exception as e:
                # Log failed execution
                auditor.log(
                    action=action,
                    user_id=user_id,
                    username=username,
                    level=AuditLevel.ERROR,
                    resource_type=resource_type,
                    status="failed",
                    error_message=str(e),
                )
                raise

        return wrapper

    return decorator


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Alias for backward compatibility
AuditService = AuditLogger
