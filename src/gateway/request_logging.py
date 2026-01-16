"""
API Gateway Request/Response Logging

Provides comprehensive logging of API requests and responses with
payload sanitization, PII redaction, and log aggregation support.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class LogLevel(str, Enum):
    """Log levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SanitizationLevel(str, Enum):
    """Sanitization levels"""

    NONE = "none"  # No sanitization
    BASIC = "basic"  # Redact passwords, tokens
    STRICT = "strict"  # Redact all PII
    FULL = "full"  # Redact everything sensitive


@dataclass
class RequestLog:
    """API request log entry"""

    request_id: str
    timestamp: datetime
    method: str
    path: str
    query_params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ResponseLog:
    """API response log entry"""

    request_id: str
    timestamp: datetime
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    response_time_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class APILogEntry:
    """Combined API log entry"""

    request: RequestLog
    response: ResponseLog
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request": {
                "id": self.request.request_id,
                "timestamp": self.request.timestamp.isoformat(),
                "method": self.request.method,
                "path": self.request.path,
                "query": self.request.query_params,
                "headers": self.request.headers,
                "body": self.request.body,
                "ip": self.request.ip_address,
                "user_agent": self.request.user_agent,
                "user_id": self.request.user_id,
                "api_key_id": self.request.api_key_id,
                "session_id": self.request.session_id,
            },
            "response": {
                "timestamp": self.response.timestamp.isoformat(),
                "status_code": self.response.status_code,
                "headers": self.response.headers,
                "body": self.response.body,
                "response_time_ms": self.response.response_time_ms,
                "error": self.response.error,
            },
            "metadata": self.metadata,
        }


class DataSanitizer:
    """Data sanitizer for redacting sensitive information"""

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = {
        "password": re.compile(r'("password"\s*:\s*")[^"]*(")', re.IGNORECASE),
        "token": re.compile(r'("(?:token|api[_-]?key|secret)"\s*:\s*")[^"]*(")', re.IGNORECASE),
        "auth": re.compile(r"(Authorization:\s*)\S+", re.IGNORECASE),
        "bearer": re.compile(r"(Bearer\s+)\S+", re.IGNORECASE),
        "basic": re.compile(r"(Basic\s+)\S+", re.IGNORECASE),
    }

    PII_PATTERNS = {
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    }

    # Fields to always redact
    SENSITIVE_FIELDS = {
        "password",
        "token",
        "api_key",
        "apikey",
        "secret",
        "authorization",
        "auth",
        "credentials",
        "private_key",
    }

    PII_FIELDS = {
        "email",
        "phone",
        "ssn",
        "social_security",
        "credit_card",
        "card_number",
        "address",
        "dob",
        "date_of_birth",
    }

    def sanitize(self, data: Any, level: SanitizationLevel = SanitizationLevel.BASIC) -> Any:
        """
        Sanitize data based on level

        Args:
            data: Data to sanitize
            level: Sanitization level

        Returns:
            Sanitized data
        """
        if level == SanitizationLevel.NONE:
            return data

        if isinstance(data, dict):
            return self._sanitize_dict(data, level)
        elif isinstance(data, list):
            return [self.sanitize(item, level) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data, level)

        return data

    def _sanitize_dict(self, data: Dict[str, Any], level: SanitizationLevel) -> Dict[str, Any]:
        """Sanitize dictionary"""
        sanitized = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Check if field should be redacted
            should_redact = False

            if level in [SanitizationLevel.BASIC, SanitizationLevel.STRICT, SanitizationLevel.FULL]:
                should_redact = any(field in key_lower for field in self.SENSITIVE_FIELDS)

            if level in [SanitizationLevel.STRICT, SanitizationLevel.FULL]:
                should_redact = should_redact or any(field in key_lower for field in self.PII_FIELDS)

            if should_redact:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = self.sanitize(value, level)

        return sanitized

    def _sanitize_string(self, data: str, level: SanitizationLevel) -> str:
        """Sanitize string"""
        result = data

        # Always redact sensitive patterns at BASIC level and above
        if level in [SanitizationLevel.BASIC, SanitizationLevel.STRICT, SanitizationLevel.FULL]:
            for pattern in self.SENSITIVE_PATTERNS.values():
                result = pattern.sub(r"\1[REDACTED]\2", result)

        # Redact PII at STRICT level and above
        if level in [SanitizationLevel.STRICT, SanitizationLevel.FULL]:
            for pattern_name, pattern in self.PII_PATTERNS.items():
                if pattern_name == "email":
                    result = pattern.sub("[EMAIL_REDACTED]", result)
                elif pattern_name == "phone":
                    result = pattern.sub("[PHONE_REDACTED]", result)
                elif pattern_name == "ssn":
                    result = pattern.sub("[SSN_REDACTED]", result)
                elif pattern_name == "credit_card":
                    result = pattern.sub("[CC_REDACTED]", result)

        return result


class RequestLogger:
    """Request/response logger"""

    def __init__(
        self,
        sanitization_level: SanitizationLevel = SanitizationLevel.BASIC,
        max_body_size: int = 10000,  # Max bytes to log
        log_headers: bool = True,
        log_body: bool = True,
    ):
        self.sanitizer = DataSanitizer()
        self.sanitization_level = sanitization_level
        self.max_body_size = max_body_size
        self.log_headers = log_headers
        self.log_body = log_body
        self.logs: Dict[str, APILogEntry] = {}

    def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        **kwargs,
    ) -> RequestLog:
        """
        Log API request

        Args:
            request_id: Unique request ID
            method: HTTP method
            path: Request path
            query_params: Query parameters
            headers: Request headers
            body: Request body
            **kwargs: Additional fields (ip, user_id, etc.)

        Returns:
            Request log entry
        """
        # Sanitize data
        if query_params:
            query_params = self.sanitizer.sanitize(query_params, self.sanitization_level)

        if headers and self.log_headers:
            headers = self.sanitizer.sanitize(headers, self.sanitization_level)
        else:
            headers = {}

        if body and self.log_body:
            # Truncate if too large
            if len(body) > self.max_body_size:
                body = body[: self.max_body_size] + "... [TRUNCATED]"
            body = self.sanitizer.sanitize(body, self.sanitization_level)
        else:
            body = None

        request_log = RequestLog(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            method=method,
            path=path,
            query_params=query_params or {},
            headers=headers,
            body=body,
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
            user_id=kwargs.get("user_id"),
            api_key_id=kwargs.get("api_key_id"),
            session_id=kwargs.get("session_id"),
        )

        return request_log

    def log_response(
        self,
        request_id: str,
        status_code: int,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        response_time_ms: float = 0.0,
        error: Optional[str] = None,
    ) -> ResponseLog:
        """
        Log API response

        Args:
            request_id: Request ID
            status_code: HTTP status code
            headers: Response headers
            body: Response body
            response_time_ms: Response time in milliseconds
            error: Error message if failed

        Returns:
            Response log entry
        """
        # Sanitize data
        if headers and self.log_headers:
            headers = self.sanitizer.sanitize(headers, self.sanitization_level)
        else:
            headers = {}

        if body and self.log_body:
            # Truncate if too large
            if len(body) > self.max_body_size:
                body = body[: self.max_body_size] + "... [TRUNCATED]"
            body = self.sanitizer.sanitize(body, self.sanitization_level)
        else:
            body = None

        response_log = ResponseLog(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            status_code=status_code,
            headers=headers,
            body=body,
            response_time_ms=response_time_ms,
            error=error,
        )

        return response_log

    def log_complete_request(
        self, request_log: RequestLog, response_log: ResponseLog, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log complete request/response pair

        Args:
            request_log: Request log
            response_log: Response log
            metadata: Additional metadata
        """
        entry = APILogEntry(request=request_log, response=response_log, metadata=metadata or {})

        self.logs[request_log.request_id] = entry

        # Write to actual log (in production, send to ELK, Splunk, etc.)
        self._write_log(entry)

    def _write_log(self, entry: APILogEntry):
        """Write log entry to storage"""
        # In production, send to log aggregation service
        # For now, just print JSON
        log_data = entry.to_dict()
        print(json.dumps(log_data, indent=2))

    def get_log(self, request_id: str) -> Optional[APILogEntry]:
        """Get log entry by request ID"""
        return self.logs.get(request_id)

    def search_logs(
        self,
        method: Optional[str] = None,
        path_pattern: Optional[str] = None,
        status_code: Optional[int] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[APILogEntry]:
        """
        Search logs

        Args:
            method: Filter by HTTP method
            path_pattern: Filter by path pattern (regex)
            status_code: Filter by status code
            user_id: Filter by user ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum results

        Returns:
            List of matching log entries
        """
        results = []
        path_regex = re.compile(path_pattern) if path_pattern else None

        for entry in self.logs.values():
            # Apply filters
            if method and entry.request.method != method:
                continue

            if path_regex and not path_regex.search(entry.request.path):
                continue

            if status_code and entry.response.status_code != status_code:
                continue

            if user_id and entry.request.user_id != user_id:
                continue

            if start_time and entry.request.timestamp < start_time:
                continue

            if end_time and entry.request.timestamp > end_time:
                continue

            results.append(entry)

            if len(results) >= limit:
                break

        return results


# Global request logger instance
_request_logger: Optional[RequestLogger] = None


def get_request_logger() -> RequestLogger:
    """Get global request logger instance"""
    global _request_logger
    if _request_logger is None:
        _request_logger = RequestLogger()
    return _request_logger


def configure_request_logger(
    sanitization_level: str = "basic", max_body_size: int = 10000, log_headers: bool = True, log_body: bool = True
):
    """Configure global request logger"""
    global _request_logger
    _request_logger = RequestLogger(
        sanitization_level=SanitizationLevel(sanitization_level),
        max_body_size=max_body_size,
        log_headers=log_headers,
        log_body=log_body,
    )
