"""
Two-Factor Authentication (2FA) Module

Provides TOTP-based two-factor authentication for enhanced security.
Supports QR code generation, backup codes, and recovery options.
"""

import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from typing import Optional, List, Tuple
from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger('dms.2fa')


class TwoFactorAuth:
    """Manage two-factor authentication for users."""

    def __init__(self, db_path: str = 'data/db/users.db'):
        """
        Initialize 2FA manager.

        Args:
            db_path: Path to user database
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize 2FA tables in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 2FA secrets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS two_factor_secrets (
                user_id INTEGER PRIMARY KEY,
                secret TEXT NOT NULL,
                enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Backup codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("2FA database initialized")

    def generate_secret(self, user_id: int, username: str) -> str:
        """
        Generate 2FA secret for user.

        Args:
            user_id: User ID
            username: Username for QR code

        Returns:
            Base32 secret
        """
        secret = pyotp.random_base32()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Save secret (not enabled yet)
        cursor.execute('''
            INSERT OR REPLACE INTO two_factor_secrets (user_id, secret, enabled)
            VALUES (?, ?, 0)
        ''', (user_id, secret))

        conn.commit()
        conn.close()

        logger.info(f"Generated 2FA secret for user {user_id}")
        return secret

    def get_provisioning_uri(self, user_id: int, username: str, issuer: str = "DMS") -> str:
        """
        Get provisioning URI for QR code.

        Args:
            user_id: User ID
            username: Username
            issuer: Application name

        Returns:
            Provisioning URI
        """
        secret = self.get_secret(user_id)
        if not secret:
            secret = self.generate_secret(user_id, username)

        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)

    def generate_qr_code(self, user_id: int, username: str) -> str:
        """
        Generate QR code as base64 image.

        Args:
            user_id: User ID
            username: Username

        Returns:
            Base64 encoded QR code image
        """
        uri = self.get_provisioning_uri(user_id, username)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_token(self, user_id: int, token: str) -> bool:
        """
        Verify TOTP token.

        Args:
            user_id: User ID
            token: 6-digit TOTP token

        Returns:
            True if valid
        """
        secret = self.get_secret(user_id)
        if not secret:
            logger.warning(f"No 2FA secret for user {user_id}")
            return False

        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(token, valid_window=1)  # Allow 1 window tolerance

        if is_valid:
            logger.info(f"Valid 2FA token for user {user_id}")
        else:
            logger.warning(f"Invalid 2FA token for user {user_id}")

        return is_valid

    def enable_2fa(self, user_id: int, verification_token: str) -> bool:
        """
        Enable 2FA after verifying initial token.

        Args:
            user_id: User ID
            verification_token: Initial verification token

        Returns:
            True if enabled successfully
        """
        if not self.verify_token(user_id, verification_token):
            logger.warning(f"Failed to enable 2FA: invalid token for user {user_id}")
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE two_factor_secrets
            SET enabled = 1, verified_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

        logger.info(f"Enabled 2FA for user {user_id}")
        return True

    def disable_2fa(self, user_id: int):
        """
        Disable 2FA for user.

        Args:
            user_id: User ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM two_factor_secrets WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM backup_codes WHERE user_id = ?', (user_id,))

        conn.commit()
        conn.close()

        logger.info(f"Disabled 2FA for user {user_id}")

    def is_enabled(self, user_id: int) -> bool:
        """Check if 2FA is enabled for user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT enabled FROM two_factor_secrets
            WHERE user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        return bool(row and row[0])

    def get_secret(self, user_id: int) -> Optional[str]:
        """Get user's 2FA secret."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT secret FROM two_factor_secrets
            WHERE user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None

    def generate_backup_codes(self, user_id: int, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.

        Args:
            user_id: User ID
            count: Number of codes to generate

        Returns:
            List of backup codes
        """
        codes = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete existing codes
        cursor.execute('DELETE FROM backup_codes WHERE user_id = ?', (user_id,))

        for _ in range(count):
            # Generate random code (8 characters)
            code = secrets.token_hex(4).upper()
            codes.append(code)

            # Hash and store
            code_hash = hashlib.sha256(code.encode()).hexdigest()

            cursor.execute('''
                INSERT INTO backup_codes (user_id, code_hash)
                VALUES (?, ?)
            ''', (user_id, code_hash))

        conn.commit()
        conn.close()

        logger.info(f"Generated {count} backup codes for user {user_id}")
        return codes

    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """
        Verify and consume backup code.

        Args:
            user_id: User ID
            code: Backup code

        Returns:
            True if valid and not used
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Find unused code
        cursor.execute('''
            SELECT id FROM backup_codes
            WHERE user_id = ? AND code_hash = ? AND used = 0
        ''', (user_id, code_hash))

        row = cursor.fetchone()

        if row:
            # Mark as used
            cursor.execute('''
                UPDATE backup_codes
                SET used = 1, used_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row[0],))

            conn.commit()
            conn.close()

            logger.info(f"Used backup code for user {user_id}")
            return True

        conn.close()
        logger.warning(f"Invalid or used backup code for user {user_id}")
        return False

    def get_remaining_backup_codes(self, user_id: int) -> int:
        """Get count of remaining backup codes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM backup_codes
            WHERE user_id = ? AND used = 0
        ''', (user_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count


# Global 2FA instance
_two_factor_auth: Optional[TwoFactorAuth] = None


def get_two_factor_auth() -> TwoFactorAuth:
    """Get or create 2FA manager instance."""
    global _two_factor_auth
    if _two_factor_auth is None:
        _two_factor_auth = TwoFactorAuth()
    return _two_factor_auth


# Helper functions

def require_2fa(func):
    """
    Decorator to require 2FA verification.

    Example:
        @require_2fa
        @login_required
        def sensitive_operation():
            ...
    """
    from functools import wraps
    from flask import session, redirect, url_for

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if 2FA is verified in session
        if not session.get('2fa_verified'):
            return redirect(url_for('auth.verify_2fa'))

        return func(*args, **kwargs)

    return wrapper
