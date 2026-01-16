"""
API Authentication Module

Provides API key-based authentication for REST API endpoints.
Includes API key generation, validation, and management.
"""

import hashlib
import logging
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Callable, Optional

from flask import g, jsonify, request

logger = logging.getLogger("dms.api_auth")


class APIKeyManager:
    """
    API key manager for REST API authentication.

    Manages API key generation, validation, and storage.
    """

    def __init__(self, db_path: str = "data/db/users.db"):
        """
        Initialize API key manager.

        Args:
            db_path: Path to database
        """
        self.db_path = db_path
        self._ensure_api_keys_table()

    def _ensure_api_keys_table(self):
        """Ensure API keys table exists."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                name TEXT NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                permissions TEXT DEFAULT '[]',
                rate_limit INTEGER DEFAULT 1000,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

        # Indexes
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_api_key_hash
            ON api_keys(key_hash)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_api_key_prefix
            ON api_keys(key_prefix)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_api_key_user
            ON api_keys(user_id)
        """
        )

        conn.commit()
        conn.close()

        logger.debug("API keys table ensured")

    def generate_api_key(
        self,
        name: str,
        user_id: Optional[int] = None,
        expires_in_days: Optional[int] = None,
        permissions: Optional[list] = None,
        rate_limit: int = 1000,
    ) -> str:
        """
        Generate new API key.

        Args:
            name: Key name/description
            user_id: Associated user ID
            expires_in_days: Expiration in days (None = no expiration)
            permissions: List of permissions
            rate_limit: Request rate limit per hour

        Returns:
            API key string
        """
        # Generate secure random key
        key = f"dms_{secrets.token_urlsafe(32)}"

        # Hash for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Key prefix for identification (first 8 chars after prefix)
        key_prefix = key[:12]  # "dms_" + first 8 chars

        # Calculate expiration
        expires_at = None
        if expires_in_days is not None:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        import json

        permissions_json = json.dumps(permissions or [])

        cursor.execute(
            """
            INSERT INTO api_keys
            (key_hash, key_prefix, name, user_id, expires_at, permissions, rate_limit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (key_hash, key_prefix, name, user_id, expires_at, permissions_json, rate_limit),
        )

        conn.commit()
        conn.close()

        logger.info(f"API key generated: {key_prefix}... (name: {name})")
        return key

    def validate_api_key(self, api_key: str) -> Optional[dict]:
        """
        Validate API key and return key info.

        Args:
            api_key: API key to validate

        Returns:
            Key info dict or None if invalid
        """
        if not api_key or not api_key.startswith("dms_"):
            return None

        # Hash key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM api_keys
            WHERE key_hash = ? AND is_active = 1
        """,
            (key_hash,),
        )

        row = cursor.fetchone()

        if not row:
            conn.close()
            logger.debug("API key not found or inactive")
            return None

        # Check expiration
        if row["expires_at"]:
            expires_at = datetime.fromisoformat(row["expires_at"])
            if expires_at < datetime.now():
                conn.close()
                logger.debug("API key expired")
                return None

        # Update last used timestamp
        cursor.execute(
            """
            UPDATE api_keys
            SET last_used_at = datetime('now')
            WHERE key_hash = ?
        """,
            (key_hash,),
        )

        conn.commit()

        # Convert to dict
        key_info = dict(row)
        conn.close()

        # Parse JSON fields
        import json

        key_info["permissions"] = json.loads(key_info["permissions"])
        key_info["metadata"] = json.loads(key_info["metadata"])

        logger.debug(f"API key validated: {key_info['key_prefix']}...")
        return key_info

    def revoke_api_key(self, api_key: str):
        """
        Revoke API key.

        Args:
            api_key: API key to revoke
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE api_keys
            SET is_active = 0
            WHERE key_hash = ?
        """,
            (key_hash,),
        )

        conn.commit()
        conn.close()

        logger.info("API key revoked")

    def list_api_keys(self, user_id: Optional[int] = None) -> list:
        """
        List API keys.

        Args:
            user_id: Filter by user ID (optional)

        Returns:
            List of API key info
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute(
                """
                SELECT id, key_prefix, name, created_at, last_used_at,
                       expires_at, is_active, permissions, rate_limit
                FROM api_keys
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
            """,
                (user_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, key_prefix, name, user_id, created_at, last_used_at,
                       expires_at, is_active, permissions, rate_limit
                FROM api_keys
                WHERE is_active = 1
                ORDER BY created_at DESC
            """
            )

        keys = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return keys

    def cleanup_expired_keys(self):
        """Remove expired API keys."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current time in ISO format to match stored format
            current_time = datetime.now().isoformat()

            cursor.execute(
                """
                DELETE FROM api_keys
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """,
                (current_time,),
            )

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted > 0:
                logger.info(f"Cleaned up {deleted} expired API keys")

        except Exception as e:
            logger.error(f"Failed to cleanup expired API keys: {e}")


# Global instance
api_key_manager = APIKeyManager()


def require_api_key(permissions: Optional[list] = None):
    """
    Decorator to require API key authentication.

    Usage:
        @app.route('/api/endpoint')
        @require_api_key()
        def endpoint():
            return jsonify({'status': 'ok'})

        # With permissions check
        @app.route('/api/admin/endpoint')
        @require_api_key(permissions=['admin'])
        def admin_endpoint():
            return jsonify({'status': 'ok'})

    Args:
        permissions: Required permissions (optional)

    Returns:
        Decorated view function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")

            # Handle Bearer token format
            if api_key and api_key.startswith("Bearer "):
                api_key = api_key[7:]

            # Validate key
            key_info = api_key_manager.validate_api_key(api_key)

            if not key_info:
                return jsonify({"success": False, "error": "Invalid or missing API key"}), 401

            # Check permissions
            if permissions:
                key_permissions = key_info.get("permissions", [])
                if not any(perm in key_permissions for perm in permissions):
                    return jsonify({"success": False, "error": "Insufficient permissions"}), 403

            # Store key info in request context
            g.api_key_info = key_info

            # Call original function
            return f(*args, **kwargs)

        return wrapped

    return decorator


def optional_api_key(f: Callable) -> Callable:
    """
    Decorator for optional API key authentication.

    Validates API key if present, but doesn't require it.

    Usage:
        @app.route('/api/public')
        @optional_api_key
        def public_endpoint():
            if hasattr(g, 'api_key_info'):
                # Authenticated request
                ...
            else:
                # Anonymous request
                ...

    Args:
        f: View function

    Returns:
        Decorated function
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")

        if api_key:
            # Handle Bearer token format
            if api_key.startswith("Bearer "):
                api_key = api_key[7:]

            # Validate key
            key_info = api_key_manager.validate_api_key(api_key)

            if key_info:
                g.api_key_info = key_info

        # Call original function
        return f(*args, **kwargs)

    return wrapped


# Example usage
if __name__ == "__main__":
    import json

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create manager
    manager = APIKeyManager()

    # Generate API key
    key = manager.generate_api_key(
        name="Test API Key", user_id=1, expires_in_days=30, permissions=["read", "write"], rate_limit=5000
    )

    print(f"\nGenerated API key: {key}")
    print(f"Keep this secret! It won't be shown again.\n")

    # Validate key
    info = manager.validate_api_key(key)
    if info:
        print("Key validation successful!")
        print(f"Key info: {json.dumps(info, indent=2, default=str)}\n")

    # List keys
    keys = manager.list_api_keys(user_id=1)
    print(f"User has {len(keys)} API key(s):")
    for k in keys:
        print(f"  - {k['key_prefix']}... ({k['name']})")

    # Revoke key
    manager.revoke_api_key(key)
    print(f"\nKey revoked")

    # Try to validate again
    info = manager.validate_api_key(key)
    if not info:
        print("Key validation failed (as expected after revocation)")
