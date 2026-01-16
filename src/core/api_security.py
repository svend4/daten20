"""
API Security Module

Provides rate limiting, CORS configuration, and API key management.
Protects API endpoints from abuse and unauthorized access.
"""

import hashlib
import logging
import secrets
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Dict, List, Optional

from flask import jsonify, request

logger = logging.getLogger("dms.api_security")


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: int = 100, per: int = 3600):
        """
        Initialize rate limiter.

        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {"tokens": rate, "last_update": time.time()})

    def _get_identifier(self) -> str:
        """Get identifier for rate limiting (IP + User)."""
        ip = request.remote_addr
        user_id = getattr(request, "user_id", None)

        if user_id:
            return f"user:{user_id}"
        return f"ip:{ip}"

    def _refill_tokens(self, bucket: Dict):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket["last_update"]

        # Calculate tokens to add
        tokens_to_add = (elapsed / self.per) * self.rate
        bucket["tokens"] = min(self.rate, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now

    def is_allowed(self, identifier: Optional[str] = None) -> bool:
        """
        Check if request is allowed.

        Args:
            identifier: Optional custom identifier

        Returns:
            True if request is allowed
        """
        if identifier is None:
            identifier = self._get_identifier()

        bucket = self.buckets[identifier]
        self._refill_tokens(bucket)

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True

        return False

    def get_reset_time(self, identifier: Optional[str] = None) -> float:
        """Get time until rate limit resets."""
        if identifier is None:
            identifier = self._get_identifier()

        bucket = self.buckets[identifier]
        self._refill_tokens(bucket)

        if bucket["tokens"] >= self.rate:
            return 0

        # Time to refill 1 token
        time_per_token = self.per / self.rate
        return time_per_token


class APIKeyManager:
    """Manage API keys for authentication."""

    def __init__(self, db_path: str = "data/db/api_keys.db"):
        """
        Initialize API key manager.

        Args:
            db_path: Path to API keys database
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize API keys database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                user_id INTEGER,
                name TEXT,
                scopes TEXT,
                enabled INTEGER DEFAULT 1,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("API keys database initialized")

    def generate_key(
        self, user_id: int, name: str, scopes: Optional[List[str]] = None, expires_in_days: Optional[int] = None
    ) -> str:
        """
        Generate new API key.

        Args:
            user_id: User ID owning the key
            name: Key name/description
            scopes: List of allowed scopes
            expires_in_days: Expiration in days (None for no expiration)

        Returns:
            Generated API key
        """
        # Generate random key
        key = f"dms_{secrets.token_urlsafe(32)}"
        key_prefix = key[:12]  # Store prefix for display
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO api_keys (key_hash, key_prefix, user_id, name, scopes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (key_hash, key_prefix, user_id, name, ",".join(scopes or []), expires_at),
        )

        conn.commit()
        conn.close()

        logger.info(f"Generated API key '{name}' for user {user_id}")
        return key

    def verify_key(self, key: str) -> Optional[Dict]:
        """
        Verify API key and return key info.

        Args:
            key: API key to verify

        Returns:
            Key info dict or None if invalid
        """
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM api_keys
            WHERE key_hash = ? AND enabled = 1
        """,
            (key_hash,),
        )

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # Check expiration
        if row["expires_at"]:
            expires_at = datetime.fromisoformat(row["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"Expired API key used: {row['key_prefix']}")
                conn.close()
                return None

        # Update last used
        cursor.execute(
            """
            UPDATE api_keys
            SET last_used = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (row["id"],),
        )

        conn.commit()
        conn.close()

        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "name": row["name"],
            "scopes": row["scopes"].split(",") if row["scopes"] else [],
        }

    def revoke_key(self, key_id: int):
        """Revoke API key."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE api_keys
            SET enabled = 0
            WHERE id = ?
        """,
            (key_id,),
        )

        conn.commit()
        conn.close()

        logger.info(f"Revoked API key {key_id}")


# CORS Configuration
CORS_CONFIG = {
    "origins": ["http://localhost:3000", "http://localhost:5000", "https://yourdomain.com"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "X-Requested-With"],
    "expose_headers": ["Content-Range", "X-Content-Range", "X-Total-Count"],
    "max_age": 3600,
    "supports_credentials": True,
}


def configure_cors(app):
    """
    Configure CORS for Flask app.

    Args:
        app: Flask application
    """
    from flask_cors import CORS

    CORS(app, **CORS_CONFIG)
    logger.info("CORS configured")


# Decorators


def rate_limit(rate: int = 100, per: int = 3600):
    """
    Decorator for rate limiting endpoints.

    Args:
        rate: Number of requests allowed
        per: Time period in seconds

    Example:
        @app.route('/api/endpoint')
        @rate_limit(rate=10, per=60)  # 10 requests per minute
        def endpoint():
            ...
    """
    limiter = RateLimiter(rate=rate, per=per)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed():
                reset_time = limiter.get_reset_time()

                response = jsonify({"error": "Rate limit exceeded", "retry_after": int(reset_time)})
                response.status_code = 429
                response.headers["Retry-After"] = str(int(reset_time))

                logger.warning(f"Rate limit exceeded for {request.remote_addr}")
                return response

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_api_key(scopes: Optional[List[str]] = None):
    """
    Decorator to require API key authentication.

    Args:
        scopes: Required scopes

    Example:
        @app.route('/api/endpoint')
        @require_api_key(scopes=['read', 'write'])
        def endpoint():
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get("X-API-Key")

            if not api_key:
                return jsonify({"error": "API key required"}), 401

            # Verify key
            key_manager = get_api_key_manager()
            key_info = key_manager.verify_key(api_key)

            if not key_info:
                logger.warning(f"Invalid API key from {request.remote_addr}")
                return jsonify({"error": "Invalid API key"}), 401

            # Check scopes
            if scopes:
                key_scopes = set(key_info["scopes"])
                required_scopes = set(scopes)

                if not required_scopes.issubset(key_scopes):
                    logger.warning(f"Insufficient scopes for API key {key_info['id']}")
                    return jsonify({"error": "Insufficient permissions"}), 403

            # Attach key info to request
            request.api_key_info = key_info

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Global instances
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """Get or create API key manager instance."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


# Request tracking middleware
class RequestTracker:
    """Track API requests for monitoring."""

    def __init__(self):
        self.requests = []
        self.max_history = 10000

    def track(self, endpoint: str, method: str, status_code: int, duration: float):
        """Track request."""
        self.requests.append(
            {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration": duration,
                "timestamp": datetime.now(),
            }
        )

        # Keep only recent requests
        if len(self.requests) > self.max_history:
            self.requests = self.requests[-self.max_history :]

    def get_stats(self) -> Dict:
        """Get request statistics."""
        if not self.requests:
            return {}

        total = len(self.requests)
        avg_duration = sum(r["duration"] for r in self.requests) / total

        by_endpoint = defaultdict(int)
        by_status = defaultdict(int)

        for req in self.requests:
            by_endpoint[req["endpoint"]] += 1
            by_status[req["status_code"]] += 1

        return {
            "total_requests": total,
            "avg_duration_ms": round(avg_duration * 1000, 2),
            "by_endpoint": dict(by_endpoint),
            "by_status": dict(by_status),
        }


_request_tracker = RequestTracker()


def get_request_tracker() -> RequestTracker:
    """Get request tracker instance."""
    return _request_tracker
