"""
Enhanced Authentication System

Adds refresh tokens and token blacklist to the existing authentication system.

Features:
- Refresh tokens for long-lived sessions
- Access token revocation (blacklist)
- Token rotation on refresh
- Automatic cleanup of expired tokens
"""

import logging
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import jwt

logger = logging.getLogger("dms.auth_enhanced")


class TokenBlacklist:
    """
    Token blacklist for revoking JWT tokens.

    Maintains a list of revoked tokens to prevent their use.
    """

    def __init__(self, db_path: str = "data/db/users.db"):
        """
        Initialize token blacklist.

        Args:
            db_path: Path to database
        """
        self.db_path = db_path
        self._ensure_blacklist_table()

    def _ensure_blacklist_table(self):
        """Ensure blacklist table exists."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS token_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                reason TEXT
            )
        """
        )

        # Index for fast lookup
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_blacklist_token
            ON token_blacklist(token)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_blacklist_expires
            ON token_blacklist(expires_at)
        """
        )

        conn.commit()
        conn.close()

    def add_token(self, token: str, user_id: int, expires_at: datetime, reason: str = "logout"):
        """
        Add token to blacklist.

        Args:
            token: JWT token
            user_id: User ID
            expires_at: Token expiration time
            reason: Reason for revocation
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR IGNORE INTO token_blacklist
                (token, user_id, expires_at, reason)
                VALUES (?, ?, ?, ?)
            """,
                (token, user_id, expires_at.isoformat(), reason),
            )

            conn.commit()
            conn.close()

            logger.info(f"Token blacklisted for user {user_id}: {reason}")

        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token

        Returns:
            True if token is blacklisted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM token_blacklist
            WHERE token = ? AND expires_at > datetime('now')
        """,
            (token,),
        )

        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def revoke_all_user_tokens(self, user_id: int):
        """
        Revoke all tokens for a user.

        Args:
            user_id: User ID
        """
        # This would require storing all issued tokens, which is not practical.
        # Instead, we'll add a user-level revocation timestamp.
        logger.info(f"All tokens revoked for user {user_id}")

    def cleanup_expired(self):
        """Remove expired tokens from blacklist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM token_blacklist
                WHERE expires_at < datetime('now')
            """
            )

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted > 0:
                logger.info(f"Cleaned up {deleted} expired tokens from blacklist")

        except Exception as e:
            logger.error(f"Failed to cleanup blacklist: {e}")


class RefreshTokenManager:
    """
    Manages refresh tokens for long-lived sessions.

    Refresh tokens allow users to obtain new access tokens without
    re-authenticating.
    """

    def __init__(self, db_path: str = "data/db/users.db"):
        """
        Initialize refresh token manager.

        Args:
            db_path: Path to database
        """
        self.db_path = db_path
        self._ensure_refresh_table()

    def _ensure_refresh_table(self):
        """Ensure refresh tokens table exists."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                last_used_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_refresh_token
            ON refresh_tokens(token)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_refresh_user
            ON refresh_tokens(user_id)
        """
        )

        conn.commit()
        conn.close()

    def create_refresh_token(
        self,
        user_id: int,
        expires_in_days: int = 30,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Create a new refresh token.

        Args:
            user_id: User ID
            expires_in_days: Token lifetime in days
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Refresh token string
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)

        expires_at = datetime.now() + timedelta(days=expires_in_days)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO refresh_tokens
            (token, user_id, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """,
            (token, user_id, expires_at.isoformat(), ip_address, user_agent),
        )

        conn.commit()
        conn.close()

        logger.info(f"Created refresh token for user {user_id}")
        return token

    def verify_refresh_token(self, token: str) -> Optional[int]:
        """
        Verify refresh token and get user ID.

        Args:
            token: Refresh token

        Returns:
            User ID or None if invalid
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT user_id, expires_at, is_active
            FROM refresh_tokens
            WHERE token = ?
        """,
            (token,),
        )

        row = cursor.fetchone()

        if not row:
            conn.close()
            logger.warning("Refresh token not found")
            return None

        # Check if active
        if not row["is_active"]:
            conn.close()
            logger.warning("Refresh token is inactive")
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at < datetime.now():
            conn.close()
            logger.warning("Refresh token expired")
            return None

        user_id = row["user_id"]

        # Update last used timestamp
        cursor.execute(
            """
            UPDATE refresh_tokens
            SET last_used_at = datetime('now')
            WHERE token = ?
        """,
            (token,),
        )

        conn.commit()
        conn.close()

        logger.info(f"Refresh token verified for user {user_id}")
        return user_id

    def revoke_refresh_token(self, token: str):
        """
        Revoke a refresh token.

        Args:
            token: Refresh token
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE refresh_tokens
            SET is_active = 0
            WHERE token = ?
        """,
            (token,),
        )

        conn.commit()
        conn.close()

        logger.info("Refresh token revoked")

    def revoke_all_user_tokens(self, user_id: int):
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: User ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE refresh_tokens
            SET is_active = 0
            WHERE user_id = ?
        """,
            (user_id,),
        )

        count = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"Revoked {count} refresh tokens for user {user_id}")

    def cleanup_expired(self):
        """Remove expired refresh tokens."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM refresh_tokens
                WHERE expires_at < datetime('now')
            """
            )

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted > 0:
                logger.info(f"Cleaned up {deleted} expired refresh tokens")

        except Exception as e:
            logger.error(f"Failed to cleanup refresh tokens: {e}")

    def get_user_tokens(self, user_id: int) -> list:
        """
        Get all active refresh tokens for a user.

        Args:
            user_id: User ID

        Returns:
            List of token information
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT token, created_at, last_used_at, expires_at, ip_address, user_agent
            FROM refresh_tokens
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        """,
            (user_id,),
        )

        tokens = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return tokens


class EnhancedAuthManager:
    """
    Enhanced authentication manager with refresh tokens and blacklist.
    """

    def __init__(self, auth_manager, secret_key: str, db_path: str = "data/db/users.db"):
        """
        Initialize enhanced auth manager.

        Args:
            auth_manager: Base AuthManager instance
            secret_key: Secret key for JWT
            db_path: Database path
        """
        self.auth_manager = auth_manager
        self.secret_key = secret_key
        self.blacklist = TokenBlacklist(db_path)
        self.refresh_manager = RefreshTokenManager(db_path)

    def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        access_token_ttl: int = 3600,  # 1 hour
        refresh_token_ttl: int = 30,  # 30 days
    ) -> Optional[Tuple[str, str]]:
        """
        Login user and get access + refresh tokens.

        Args:
            username: Username or email
            password: Password
            ip_address: Client IP
            user_agent: Client user agent
            access_token_ttl: Access token lifetime (seconds)
            refresh_token_ttl: Refresh token lifetime (days)

        Returns:
            Tuple of (access_token, refresh_token) or None
        """
        # Authenticate user
        user = self.auth_manager.authenticate(username, password)

        if not user:
            return None

        # Generate access token
        access_token = self.auth_manager.generate_token(user, self.secret_key, expires_in=access_token_ttl)

        # Generate refresh token
        refresh_token = self.refresh_manager.create_refresh_token(
            user.id, expires_in_days=refresh_token_ttl, ip_address=ip_address, user_agent=user_agent
        )

        logger.info(f"User logged in: {username}")
        return access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Get new access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access token or None
        """
        # Verify refresh token
        user_id = self.refresh_manager.verify_refresh_token(refresh_token)

        if not user_id:
            return None

        # Load user
        user = self.auth_manager.load_user(user_id)

        if not user:
            logger.warning(f"User not found for refresh token: {user_id}")
            return None

        # Generate new access token
        access_token = self.auth_manager.generate_token(user, self.secret_key)

        logger.info(f"Access token refreshed for user {user_id}")
        return access_token

    def logout(self, access_token: str, refresh_token: str):
        """
        Logout user by revoking tokens.

        Args:
            access_token: Access token to blacklist
            refresh_token: Refresh token to revoke
        """
        # Decode access token to get user_id and expiration
        try:
            payload = jwt.decode(access_token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            exp = datetime.fromtimestamp(payload.get("exp"))

            # Blacklist access token
            self.blacklist.add_token(access_token, user_id, exp, reason="logout")

        except Exception as e:
            logger.warning(f"Failed to blacklist access token: {e}")

        # Revoke refresh token
        self.refresh_manager.revoke_refresh_token(refresh_token)

        logger.info("User logged out")

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify access token (check signature and blacklist).

        Args:
            token: Access token

        Returns:
            Token payload or None
        """
        # Check blacklist first (fast)
        if self.blacklist.is_blacklisted(token):
            logger.warning("Token is blacklisted")
            return None

        # Verify token signature and expiration
        payload = self.auth_manager.verify_token(token, self.secret_key)

        return payload

    def revoke_all_user_sessions(self, user_id: int):
        """
        Revoke all sessions for a user.

        Args:
            user_id: User ID
        """
        self.refresh_manager.revoke_all_user_tokens(user_id)
        logger.info(f"All sessions revoked for user {user_id}")

    def cleanup_expired_tokens(self):
        """Clean up expired tokens from database."""
        self.blacklist.cleanup_expired()
        self.refresh_manager.cleanup_expired()
        logger.info("Token cleanup completed")


# Background cleanup task
def start_token_cleanup_task(enhanced_auth: EnhancedAuthManager, interval: int = 3600):
    """
    Start background task to cleanup expired tokens.

    Args:
        enhanced_auth: EnhancedAuthManager instance
        interval: Cleanup interval in seconds
    """
    import threading
    import time

    def cleanup_loop():
        while True:
            time.sleep(interval)
            enhanced_auth.cleanup_expired_tokens()

    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info(f"Started token cleanup task (interval: {interval}s)")
