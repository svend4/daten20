"""
Email Verification and Password Reset System

Provides secure email verification and password reset functionality
with time-limited tokens and comprehensive logging.
"""

import logging
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import jwt

from .email_notifier import EmailNotifier

logger = logging.getLogger("dms.email_verification")


class EmailVerificationManager:
    """Manage email verification and password reset processes."""

    def __init__(
        self,
        db_path: str = "data/db/users.db",
        email_notifier: Optional[EmailNotifier] = None,
        base_url: str = "http://localhost:5000",
    ):
        """
        Initialize email verification manager.

        Args:
            db_path: Path to user database
            email_notifier: EmailNotifier instance
            base_url: Base URL for verification links
        """
        self.db_path = db_path
        self.email_notifier = email_notifier
        self.base_url = base_url.rstrip("/")
        self._init_database()

    def _init_database(self):
        """Initialize email verification tables."""
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Add email_verified column to users table if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
            logger.info("Added email_verified column to users table")
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Create email verification tokens table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )

        # Create password reset tokens table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )

        # Create indexes for faster lookups
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_email_verification_user_id
            ON email_verification_tokens(user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_email_verification_token
            ON email_verification_tokens(token)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_password_reset_user_id
            ON password_reset_tokens(user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_password_reset_token
            ON password_reset_tokens(token)
        """
        )

        conn.commit()
        conn.close()
        logger.info("Email verification database initialized")

    def generate_verification_token(
        self, user_id: int, email: str, expires_in: int = 86400, ip_address: Optional[str] = None  # 24 hours
    ) -> str:
        """
        Generate email verification token.

        Args:
            user_id: User ID
            email: User email address
            expires_in: Token expiration in seconds (default 24 hours)
            ip_address: IP address of the request

        Returns:
            Verification token
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Invalidate any existing tokens for this user
        cursor.execute(
            """
            UPDATE email_verification_tokens
            SET expires_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND verified_at IS NULL
        """,
            (user_id,),
        )

        # Insert new token
        cursor.execute(
            """
            INSERT INTO email_verification_tokens (user_id, token, expires_at, ip_address)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, token, expires_at.isoformat(), ip_address),
        )

        conn.commit()
        conn.close()

        logger.info(f"Generated email verification token for user {user_id}")
        return token

    def send_verification_email(
        self, user_id: int, email: str, username: str, ip_address: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send email verification email.

        Args:
            user_id: User ID
            email: User email address
            username: Username
            ip_address: IP address of the request

        Returns:
            Tuple of (success, message/token)
        """
        if not self.email_notifier or not self.email_notifier.enabled:
            # For development: return token directly
            token = self.generate_verification_token(user_id, email, ip_address=ip_address)
            verification_url = f"{self.base_url}/verify-email?token={token}"
            logger.warning(f"Email notifications disabled. Verification URL: {verification_url}")
            return True, token

        # Generate token
        token = self.generate_verification_token(user_id, email, ip_address=ip_address)
        verification_url = f"{self.base_url}/verify-email?token={token}"

        # Prepare email
        subject = "Verify Your Email - Document Management System"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .code {{
                    background: #e9ecef;
                    padding: 10px;
                    border-radius: 4px;
                    font-family: monospace;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Email Verification</h1>
                </div>
                <div class="content">
                    <h2>Hello {username}!</h2>
                    <p>Thank you for registering with Document Management System.</p>
                    <p>Please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <div class="code">{verification_url}</div>
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    <p>If you didn't create an account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Document Management System</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Email Verification - Document Management System

        Hello {username}!

        Thank you for registering with Document Management System.

        Please verify your email address by visiting this link:
        {verification_url}

        This link will expire in 24 hours.

        If you didn't create an account, please ignore this email.

        ---
        Document Management System
        This is an automated email. Please do not reply.
        """

        # Send email
        success = self.email_notifier.send_email(to_emails=[email], subject=subject, body=html_body, html=True)

        if success:
            logger.info(f"Verification email sent to {email}")
            return True, "Verification email sent successfully"
        else:
            logger.error(f"Failed to send verification email to {email}")
            return False, "Failed to send verification email"

    def verify_email(self, token: str, ip_address: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Verify email with token.

        Args:
            token: Verification token
            ip_address: IP address of the request

        Returns:
            Tuple of (success, message, user_id)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Find token
            cursor.execute(
                """
                SELECT user_id, expires_at, verified_at
                FROM email_verification_tokens
                WHERE token = ?
            """,
                (token,),
            )

            row = cursor.fetchone()

            if not row:
                logger.warning(f"Invalid verification token: {token[:10]}...")
                return False, "Invalid verification token", None

            user_id, expires_at, verified_at = row

            # Check if already verified
            if verified_at:
                logger.info(f"Email already verified for user {user_id}")
                return True, "Email already verified", user_id

            # Check if expired
            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                logger.warning(f"Expired verification token for user {user_id}")
                return False, "Verification token has expired", None

            # Mark as verified
            cursor.execute(
                """
                UPDATE email_verification_tokens
                SET verified_at = CURRENT_TIMESTAMP
                WHERE token = ?
            """,
                (token,),
            )

            # Update user email_verified status
            cursor.execute(
                """
                UPDATE users
                SET email_verified = 1
                WHERE id = ?
            """,
                (user_id,),
            )

            conn.commit()
            logger.info(f"Email verified successfully for user {user_id}")
            return True, "Email verified successfully", user_id

        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False, f"Error verifying email: {e}", None

        finally:
            conn.close()

    def generate_password_reset_token(
        self, user_id: int, email: str, expires_in: int = 3600, ip_address: Optional[str] = None  # 1 hour
    ) -> str:
        """
        Generate password reset token.

        Args:
            user_id: User ID
            email: User email address
            expires_in: Token expiration in seconds (default 1 hour)
            ip_address: IP address of the request

        Returns:
            Reset token
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Invalidate any existing tokens for this user
        cursor.execute(
            """
            UPDATE password_reset_tokens
            SET expires_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND used_at IS NULL
        """,
            (user_id,),
        )

        # Insert new token
        cursor.execute(
            """
            INSERT INTO password_reset_tokens (user_id, token, expires_at, ip_address)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, token, expires_at.isoformat(), ip_address),
        )

        conn.commit()
        conn.close()

        logger.info(f"Generated password reset token for user {user_id}")
        return token

    def send_password_reset_email(self, email: str, ip_address: Optional[str] = None) -> Tuple[bool, str]:
        """
        Send password reset email.

        Args:
            email: User email address
            ip_address: IP address of the request

        Returns:
            Tuple of (success, message)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Find user by email
        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE email = ? AND is_active = 1
        """,
            (email,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            # For security, don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return True, "If the email exists, a reset link has been sent"

        user_id, username, user_email = row

        if not self.email_notifier or not self.email_notifier.enabled:
            # For development: return token directly
            token = self.generate_password_reset_token(user_id, user_email, ip_address=ip_address)
            reset_url = f"{self.base_url}/reset-password?token={token}"
            logger.warning(f"Email notifications disabled. Reset URL: {reset_url}")
            return True, token

        # Generate token
        token = self.generate_password_reset_token(user_id, user_email, ip_address=ip_address)
        reset_url = f"{self.base_url}/reset-password?token={token}"

        # Prepare email
        subject = "Password Reset Request - Document Management System"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #dc3545;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .code {{
                    background: #e9ecef;
                    padding: 10px;
                    border-radius: 4px;
                    font-family: monospace;
                    word-break: break-all;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {username}!</h2>
                    <p>We received a request to reset your password for your Document Management System account.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <div class="code">{reset_url}</div>
                    <div class="warning">
                        <strong>⚠️ Important Security Information:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Your password will remain unchanged until you access the link above</li>
                        </ul>
                    </div>
                    <p>If you're having trouble, contact your system administrator.</p>
                </div>
                <div class="footer">
                    <p>Document Management System</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Password Reset Request - Document Management System

        Hello {username}!

        We received a request to reset your password for your Document Management System account.

        Click this link to reset your password:
        {reset_url}

        IMPORTANT:
        - This link will expire in 1 hour
        - If you didn't request this reset, please ignore this email
        - Your password will remain unchanged until you access the link above

        ---
        Document Management System
        This is an automated email. Please do not reply.
        """

        # Send email
        success = self.email_notifier.send_email(to_emails=[user_email], subject=subject, body=html_body, html=True)

        if success:
            logger.info(f"Password reset email sent to {user_email}")
            return True, "Password reset email sent successfully"
        else:
            logger.error(f"Failed to send password reset email to {user_email}")
            # For security, don't reveal failure details to user
            return True, "If the email exists, a reset link has been sent"

    def verify_reset_token(self, token: str) -> Tuple[bool, str, Optional[int]]:
        """
        Verify password reset token.

        Args:
            token: Reset token

        Returns:
            Tuple of (valid, message, user_id)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Find token
            cursor.execute(
                """
                SELECT user_id, expires_at, used_at
                FROM password_reset_tokens
                WHERE token = ?
            """,
                (token,),
            )

            row = cursor.fetchone()

            if not row:
                logger.warning(f"Invalid reset token: {token[:10]}...")
                return False, "Invalid reset token", None

            user_id, expires_at, used_at = row

            # Check if already used
            if used_at:
                logger.warning(f"Reset token already used for user {user_id}")
                return False, "Reset token has already been used", None

            # Check if expired
            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                logger.warning(f"Expired reset token for user {user_id}")
                return False, "Reset token has expired", None

            return True, "Token is valid", user_id

        except Exception as e:
            logger.error(f"Error verifying reset token: {e}")
            return False, f"Error verifying token: {e}", None

        finally:
            conn.close()

    def reset_password(
        self, token: str, new_password: str, bcrypt_instance, ip_address: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Reset password using token.

        Args:
            token: Reset token
            new_password: New password (plain text)
            bcrypt_instance: Bcrypt instance for hashing
            ip_address: IP address of the request

        Returns:
            Tuple of (success, message)
        """
        # Verify token
        valid, message, user_id = self.verify_reset_token(token)
        if not valid:
            return False, message

        try:
            # Hash new password
            password_hash = bcrypt_instance.generate_password_hash(new_password).decode("utf-8")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update password
            cursor.execute(
                """
                UPDATE users
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (password_hash, user_id),
            )

            # Mark token as used
            cursor.execute(
                """
                UPDATE password_reset_tokens
                SET used_at = CURRENT_TIMESTAMP
                WHERE token = ?
            """,
                (token,),
            )

            conn.commit()
            conn.close()

            logger.info(f"Password reset successful for user {user_id}")
            return True, "Password reset successfully"

        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False, f"Error resetting password: {e}"

    def is_email_verified(self, user_id: int) -> bool:
        """
        Check if user's email is verified.

        Args:
            user_id: User ID

        Returns:
            True if email is verified
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT email_verified
            FROM users
            WHERE id = ?
        """,
            (user_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            return True
        return False

    def cleanup_expired_tokens(self) -> Dict[str, int]:
        """
        Clean up expired tokens from database.

        Returns:
            Dictionary with cleanup statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Delete expired verification tokens
            cursor.execute(
                """
                DELETE FROM email_verification_tokens
                WHERE expires_at < ? AND verified_at IS NULL
            """,
                (datetime.utcnow().isoformat(),),
            )
            verification_deleted = cursor.rowcount

            # Delete expired reset tokens
            cursor.execute(
                """
                DELETE FROM password_reset_tokens
                WHERE expires_at < ? AND used_at IS NULL
            """,
                (datetime.utcnow().isoformat(),),
            )
            reset_deleted = cursor.rowcount

            conn.commit()

            logger.info(f"Cleaned up {verification_deleted} verification tokens and {reset_deleted} reset tokens")

            return {"verification_tokens_deleted": verification_deleted, "reset_tokens_deleted": reset_deleted}

        except Exception as e:
            logger.error(f"Error cleaning up tokens: {e}")
            return {"verification_tokens_deleted": 0, "reset_tokens_deleted": 0, "error": str(e)}

        finally:
            conn.close()


# Global instance
_email_verification_manager: Optional[EmailVerificationManager] = None


def get_email_verification_manager(
    db_path: str = "data/db/users.db",
    email_notifier: Optional[EmailNotifier] = None,
    base_url: str = "http://localhost:5000",
) -> EmailVerificationManager:
    """Get or create email verification manager instance."""
    global _email_verification_manager
    if _email_verification_manager is None:
        _email_verification_manager = EmailVerificationManager(
            db_path=db_path, email_notifier=email_notifier, base_url=base_url
        )
    return _email_verification_manager
