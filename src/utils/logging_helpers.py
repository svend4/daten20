#!/usr/bin/env python3
"""
Enhanced Logging Helpers for Daten20

Provides advanced logging utilities:
- Performance logging with timing
- Audit logging for compliance
- Structured logging helpers
- Log message templates
- Request/response logging
- Error tracking integration
"""

import functools
import json
import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class PerformanceLogger:
    """Performance logging with timing and metrics"""

    def __init__(self, logger: logging.Logger):
        """
        Initialize performance logger

        Args:
            logger: Logger instance to use
        """
        self.logger = logger

    @contextmanager
    def measure(self, operation: str, **context):
        """
        Context manager to measure operation time

        Args:
            operation: Name of the operation
            **context: Additional context fields

        Example:
            with perf_logger.measure("document_parsing", doc_id=123):
                parse_document()
        """
        start_time = time.time()
        self.logger.info(f"[PERF] Starting: {operation}", extra={"context": context})

        try:
            yield
            duration = time.time() - start_time
            self.logger.info(
                f"[PERF] Completed: {operation} in {duration:.2f}s",
                extra={"context": {**context, "duration_seconds": duration, "status": "success"}},
            )
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"[PERF] Failed: {operation} after {duration:.2f}s - {str(e)}",
                extra={"context": {**context, "duration_seconds": duration, "status": "failed", "error": str(e)}},
            )
            raise

    def timed(self, operation: Optional[str] = None):
        """
        Decorator to measure function execution time

        Args:
            operation: Optional operation name (defaults to function name)

        Example:
            @perf_logger.timed("process_document")
            def process_doc(doc_id):
                ...
        """

        def decorator(func):
            op_name = operation or func.__name__

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                self.logger.debug(f"[PERF] Starting: {op_name}")

                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.logger.info(
                        f"[PERF] Completed: {op_name} in {duration:.2f}s", extra={"duration_seconds": duration}
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.error(
                        f"[PERF] Failed: {op_name} after {duration:.2f}s - {str(e)}",
                        extra={"duration_seconds": duration, "error": str(e)},
                    )
                    raise

            return wrapper

        return decorator


class AuditLogger:
    """Audit logging for compliance and security"""

    def __init__(self, logger: logging.Logger, audit_log_path: Optional[Path] = None):
        """
        Initialize audit logger

        Args:
            logger: Logger instance
            audit_log_path: Path to audit log file (optional, separate from main logs)
        """
        self.logger = logger
        self.audit_log_path = audit_log_path

        # Setup separate audit log file if specified
        if audit_log_path:
            audit_handler = logging.FileHandler(audit_log_path)
            audit_handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s - AUDIT - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            audit_handler.setFormatter(formatter)
            self.logger.addHandler(audit_handler)

    def log_action(self, action: str, user: str, resource: str, status: str = "success", **details):
        """
        Log an audit event

        Args:
            action: Action performed (create, read, update, delete, etc.)
            user: User who performed the action
            resource: Resource affected
            status: Status of action (success, failed, denied)
            **details: Additional details
        """
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user": user,
            "resource": resource,
            "status": status,
            **details,
        }

        self.logger.info(f"[AUDIT] {action.upper()} {resource} by {user} - {status}", extra={"audit_data": audit_data})

    def log_access(self, user: str, resource: str, granted: bool, reason: Optional[str] = None):
        """Log access attempt"""
        status = "granted" if granted else "denied"
        details = {"reason": reason} if reason else {}
        self.log_action("access", user, resource, status, **details)

    def log_data_access(self, user: str, data_type: str, operation: str, count: int = 1):
        """Log data access for GDPR compliance"""
        self.log_action("data_access", user, data_type, "success", operation=operation, record_count=count)

    def log_pii_access(self, user: str, pii_type: str, purpose: str):
        """Log PII (Personally Identifiable Information) access"""
        self.log_action("pii_access", user, pii_type, "success", purpose=purpose, compliance="GDPR")

    def log_configuration_change(self, user: str, config_key: str, old_value: Any, new_value: Any):
        """Log configuration changes"""
        self.log_action(
            "config_change", user, config_key, "success", old_value=str(old_value), new_value=str(new_value)
        )


class StructuredLogger:
    """Structured logging with consistent message templates"""

    def __init__(self, logger: logging.Logger):
        """
        Initialize structured logger

        Args:
            logger: Logger instance
        """
        self.logger = logger

    def log_request(
        self,
        method: str,
        endpoint: str,
        user: Optional[str] = None,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        **extra,
    ):
        """
        Log HTTP request

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            user: User making request
            status_code: Response status code
            duration: Request duration in seconds
            **extra: Additional fields
        """
        context = {
            "method": method,
            "endpoint": endpoint,
            "user": user,
            "status_code": status_code,
            "duration_ms": duration * 1000 if duration else None,
            **extra,
        }

        if status_code and status_code >= 400:
            self.logger.warning(f"[API] {method} {endpoint} - {status_code}", extra={"context": context})
        else:
            self.logger.info(f"[API] {method} {endpoint}", extra={"context": context})

    def log_operation(
        self, operation: str, status: str, entity_type: Optional[str] = None, entity_id: Optional[str] = None, **details
    ):
        """
        Log business operation

        Args:
            operation: Operation name
            status: Operation status (started, completed, failed)
            entity_type: Type of entity (document, user, etc.)
            entity_id: Entity identifier
            **details: Additional details
        """
        context = {
            "operation": operation,
            "status": status,
            "entity_type": entity_type,
            "entity_id": entity_id,
            **details,
        }

        level = logging.INFO
        if status == "failed":
            level = logging.ERROR
        elif status == "started":
            level = logging.DEBUG

        self.logger.log(
            level,
            f"[OP] {operation} - {status}" + (f" ({entity_type}:{entity_id})" if entity_id else ""),
            extra={"context": context},
        )

    def log_security_event(self, event_type: str, severity: str, description: str, **details):
        """
        Log security event

        Args:
            event_type: Type of security event
            severity: Severity (low, medium, high, critical)
            description: Event description
            **details: Additional details
        """
        context = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            **details,
        }

        level = logging.WARNING
        if severity in ["high", "critical"]:
            level = logging.ERROR

        self.logger.log(
            level, f"[SECURITY] {event_type} - {severity.upper()} - {description}", extra={"context": context}
        )

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, user_message: Optional[str] = None):
        """
        Log error with context

        Args:
            error: Exception instance
            context: Additional context
            user_message: User-friendly error message
        """
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_message": user_message,
            **(context or {}),
        }

        self.logger.error(
            f"[ERROR] {type(error).__name__}: {str(error)}", exc_info=True, extra={"context": error_context}
        )


class LogMessageTemplates:
    """Pre-defined log message templates for consistency"""

    # Document operations
    DOCUMENT_PARSED = "[DOC] Parsed document: {doc_name} ({size} bytes, {pages} pages)"
    DOCUMENT_SAVED = "[DOC] Saved document: {doc_id} to {path}"
    DOCUMENT_DELETED = "[DOC] Deleted document: {doc_id}"
    DOCUMENT_EXPORTED = "[DOC] Exported document: {doc_id} to {format}"

    # User operations
    USER_LOGIN = "[USER] Login: {username} from {ip}"
    USER_LOGOUT = "[USER] Logout: {username}"
    USER_CREATED = "[USER] Created user: {username} with role {role}"
    USER_UPDATED = "[USER] Updated user: {username}"
    USER_DELETED = "[USER] Deleted user: {username}"

    # System operations
    SYSTEM_STARTUP = "[SYSTEM] Starting {service_name} v{version}"
    SYSTEM_SHUTDOWN = "[SYSTEM] Shutting down {service_name}"
    SYSTEM_ERROR = "[SYSTEM] System error in {component}: {error}"
    SYSTEM_HEALTH_CHECK = "[SYSTEM] Health check: {status} - {details}"

    # Processing operations
    PROCESSING_STARTED = "[PROC] Started processing: {task_id} - {task_type}"
    PROCESSING_COMPLETED = "[PROC] Completed processing: {task_id} in {duration}s"
    PROCESSING_FAILED = "[PROC] Failed processing: {task_id} - {error}"
    PROCESSING_PROGRESS = "[PROC] Progress: {task_id} - {percent}% ({current}/{total})"

    # Database operations
    DB_QUERY = "[DB] Query executed: {query_type} in {duration}ms"
    DB_CONNECTION = "[DB] Database connection: {status}"
    DB_MIGRATION = "[DB] Migration: {version} - {status}"
    DB_BACKUP = "[DB] Backup created: {backup_file}"

    # API operations
    API_CALL = "[API] {method} {endpoint} - {status_code} ({duration}ms)"
    API_AUTH_SUCCESS = "[API] Authentication successful: {user}"
    API_AUTH_FAILED = "[API] Authentication failed: {reason}"
    API_RATE_LIMIT = "[API] Rate limit exceeded: {user} - {endpoint}"

    # Security events
    SECURITY_ACCESS_DENIED = "[SEC] Access denied: {user} to {resource} - {reason}"
    SECURITY_SUSPICIOUS = "[SEC] Suspicious activity: {description} from {ip}"
    SECURITY_VIOLATION = "[SEC] Security violation: {type} by {user}"

    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """
        Format template with values

        Args:
            template: Template string
            **kwargs: Template variables

        Returns:
            Formatted string
        """
        return template.format(**kwargs)


# Convenience functions for quick setup
def get_performance_logger(logger_name: str = "performance") -> PerformanceLogger:
    """Get a performance logger instance"""
    logger = logging.getLogger(logger_name)
    return PerformanceLogger(logger)


def get_audit_logger(logger_name: str = "audit", audit_log_path: Optional[Path] = None) -> AuditLogger:
    """Get an audit logger instance"""
    logger = logging.getLogger(logger_name)
    return AuditLogger(logger, audit_log_path)


def get_structured_logger(logger_name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    logger = logging.getLogger(logger_name)
    return StructuredLogger(logger)


__all__ = [
    "PerformanceLogger",
    "AuditLogger",
    "StructuredLogger",
    "LogMessageTemplates",
    "get_performance_logger",
    "get_audit_logger",
    "get_structured_logger",
]
