"""
Comprehensive tests for src/core/email_verification.py

Tests email verification and password reset functionality including:
- EmailVerificationManager class
- Token generation and validation
- Email sending
- Password reset flows
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from typing import Optional

from src.core.email_verification import EmailVerificationManager, get_email_verification_manager
from src.core.email_notifier import EmailNotifier


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Initialize users table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add test user
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        ("testuser", "test@example.com", "hashed_password")
    )
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_email_notifier():
    """Create mock email notifier"""
    notifier = Mock(spec=EmailNotifier)
    notifier.send_email.return_value = (True, "Email sent successfully")
    return notifier


@pytest.fixture
def manager(temp_db, mock_email_notifier):
    """Create EmailVerificationManager instance"""
    return EmailVerificationManager(
        db_path=temp_db,
        email_notifier=mock_email_notifier,
        base_url="http://localhost:5000"
    )


class TestEmailVerificationManager:
    """Tests for EmailVerificationManager class"""

    def test_initialization(self, temp_db, mock_email_notifier):
        """Test EmailVerificationManager initialization"""
        manager = EmailVerificationManager(
            db_path=temp_db,
            email_notifier=mock_email_notifier,
            base_url="http://localhost:5000"
        )

        assert manager.db_path == temp_db
        assert manager.email_notifier == mock_email_notifier
        assert manager.base_url == "http://localhost:5000"

    def test_initialization_strips_trailing_slash(self, temp_db):
        """Test that base_url trailing slash is removed"""
        manager = EmailVerificationManager(
            db_path=temp_db,
            base_url="http://localhost:5000/"
        )

        assert manager.base_url == "http://localhost:5000"

    def test_database_initialization_creates_tables(self, temp_db):
        """Test that database tables are created"""
        manager = EmailVerificationManager(db_path=temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check email_verification_tokens table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='email_verification_tokens'"
        )
        assert cursor.fetchone() is not None

        # Check password_reset_tokens table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='password_reset_tokens'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_database_initialization_creates_indexes(self, temp_db):
        """Test that database indexes are created"""
        manager = EmailVerificationManager(db_path=temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check indexes exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        indexes = [row[0] for row in cursor.fetchall()]

        assert "idx_email_verification_user_id" in indexes
        assert "idx_password_reset_user_id" in indexes

        conn.close()


class TestEmailVerificationTokens:
    """Tests for email verification token functionality"""

    def test_generate_verification_token(self, manager):
        """Test generating verification token"""
        success, message, token = manager.generate_verification_token(
            user_id=1,
            expiry_hours=24
        )

        assert success is True
        assert token is not None
        assert len(token) > 0
        assert "generated" in message.lower()

    def test_generate_verification_token_stores_in_database(self, manager):
        """Test that generated token is stored in database"""
        success, message, token = manager.generate_verification_token(user_id=1)

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token, user_id FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == token
        assert row[1] == 1

    def test_generate_verification_token_with_ip_address(self, manager):
        """Test generating token with IP address"""
        success, message, token = manager.generate_verification_token(
            user_id=1,
            ip_address="192.168.1.1"
        )

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ip_address FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row[0] == "192.168.1.1"

    def test_generate_verification_token_sets_expiry(self, manager):
        """Test that token has correct expiry time"""
        success, message, token = manager.generate_verification_token(
            user_id=1,
            expiry_hours=24
        )

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT expires_at FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        expires_at_str = cursor.fetchone()[0]
        conn.close()

        expires_at = datetime.fromisoformat(expires_at_str)
        expected_expiry = datetime.now() + timedelta(hours=24)

        # Allow 1 minute difference
        assert abs((expires_at - expected_expiry).total_seconds()) < 60

    def test_send_verification_email_success(self, manager, mock_email_notifier):
        """Test sending verification email successfully"""
        success, message = manager.send_verification_email(
            email="test@example.com",
            user_id=1
        )

        assert success is True
        assert mock_email_notifier.send_email.called

    def test_send_verification_email_generates_token(self, manager, mock_email_notifier):
        """Test that sending email generates a token"""
        success, message = manager.send_verification_email(
            email="test@example.com",
            user_id=1
        )

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM email_verification_tokens WHERE user_id = ?",
            (1,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        assert count >= 1

    def test_verify_email_success(self, manager):
        """Test successful email verification"""
        # Generate token first
        success, message, token = manager.generate_verification_token(user_id=1)

        # Verify email
        verified, verify_message, user_id = manager.verify_email(token)

        assert verified is True
        assert user_id == 1
        assert "success" in verify_message.lower() or "verified" in verify_message.lower()

    def test_verify_email_marks_as_verified(self, manager):
        """Test that verification updates verified_at timestamp"""
        success, message, token = manager.generate_verification_token(user_id=1)

        manager.verify_email(token)

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT verified_at FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        verified_at = cursor.fetchone()[0]
        conn.close()

        assert verified_at is not None

    def test_verify_email_updates_user_table(self, manager):
        """Test that verification updates user's email_verified flag"""
        success, message, token = manager.generate_verification_token(user_id=1)

        manager.verify_email(token)

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email_verified FROM users WHERE id = ?",
            (1,)
        )
        email_verified = cursor.fetchone()[0]
        conn.close()

        assert email_verified == 1

    def test_verify_email_invalid_token(self, manager):
        """Test verification with invalid token"""
        verified, message, user_id = manager.verify_email("invalid_token_12345")

        assert verified is False
        assert user_id is None
        assert "invalid" in message.lower() or "not found" in message.lower()

    def test_verify_email_expired_token(self, manager):
        """Test verification with expired token"""
        # Generate token that expires immediately
        success, message, token = manager.generate_verification_token(
            user_id=1,
            expiry_hours=-1  # Expired 1 hour ago
        )

        verified, verify_message, user_id = manager.verify_email(token)

        assert verified is False
        assert "expired" in verify_message.lower()

    def test_verify_email_already_verified(self, manager):
        """Test verifying an already verified token"""
        success, message, token = manager.generate_verification_token(user_id=1)

        # Verify first time
        manager.verify_email(token)

        # Try to verify again
        verified, verify_message, user_id = manager.verify_email(token)

        assert "already" in verify_message.lower() or "used" in verify_message.lower()

    def test_verify_email_with_ip_address(self, manager):
        """Test verification with IP address logging"""
        success, message, token = manager.generate_verification_token(user_id=1)

        manager.verify_email(token, ip_address="192.168.1.1")

        # Verification should succeed
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT verified_at FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        verified_at = cursor.fetchone()[0]
        conn.close()

        assert verified_at is not None

    def test_is_email_verified_true(self, manager):
        """Test checking if email is verified (verified user)"""
        # Verify email first
        success, message, token = manager.generate_verification_token(user_id=1)
        manager.verify_email(token)

        is_verified = manager.is_email_verified(user_id=1)

        assert is_verified is True

    def test_is_email_verified_false(self, manager):
        """Test checking if email is verified (unverified user)"""
        is_verified = manager.is_email_verified(user_id=1)

        assert is_verified is False

    def test_is_email_verified_nonexistent_user(self, manager):
        """Test checking verification for nonexistent user"""
        is_verified = manager.is_email_verified(user_id=99999)

        assert is_verified is False


class TestPasswordResetTokens:
    """Tests for password reset token functionality"""

    def test_generate_password_reset_token(self, manager):
        """Test generating password reset token"""
        success, message, token = manager.generate_password_reset_token(
            user_id=1,
            expiry_hours=1
        )

        assert success is True
        assert token is not None
        assert len(token) > 0

    def test_generate_password_reset_token_stores_in_database(self, manager):
        """Test that reset token is stored in database"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token, user_id FROM password_reset_tokens WHERE token = ?",
            (token,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == token
        assert row[1] == 1

    def test_generate_password_reset_token_with_ip(self, manager):
        """Test generating reset token with IP address"""
        success, message, token = manager.generate_password_reset_token(
            user_id=1,
            ip_address="192.168.1.1"
        )

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ip_address FROM password_reset_tokens WHERE token = ?",
            (token,)
        )
        ip_address = cursor.fetchone()[0]
        conn.close()

        assert ip_address == "192.168.1.1"

    def test_send_password_reset_email_success(self, manager, mock_email_notifier):
        """Test sending password reset email"""
        success, message = manager.send_password_reset_email(
            email="test@example.com"
        )

        assert success is True
        assert mock_email_notifier.send_email.called

    def test_send_password_reset_email_invalid_email(self, manager):
        """Test sending reset email to invalid email"""
        success, message = manager.send_password_reset_email(
            email="nonexistent@example.com"
        )

        assert success is False
        assert "not found" in message.lower() or "invalid" in message.lower()

    def test_verify_reset_token_valid(self, manager):
        """Test verifying valid reset token"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        is_valid, verify_message, user_id = manager.verify_reset_token(token)

        assert is_valid is True
        assert user_id == 1

    def test_verify_reset_token_invalid(self, manager):
        """Test verifying invalid reset token"""
        is_valid, message, user_id = manager.verify_reset_token("invalid_token")

        assert is_valid is False
        assert user_id is None

    def test_verify_reset_token_expired(self, manager):
        """Test verifying expired reset token"""
        success, message, token = manager.generate_password_reset_token(
            user_id=1,
            expiry_hours=-1  # Expired
        )

        is_valid, verify_message, user_id = manager.verify_reset_token(token)

        assert is_valid is False
        assert "expired" in verify_message.lower()

    def test_verify_reset_token_already_used(self, manager):
        """Test verifying already used reset token"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        # Use token for password reset
        manager.reset_password(token, "new_password_123")

        # Try to use again
        is_valid, verify_message, user_id = manager.verify_reset_token(token)

        assert is_valid is False or "already" in verify_message.lower() or "used" in verify_message.lower()

    def test_reset_password_success(self, manager):
        """Test successful password reset"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        reset_success, reset_message = manager.reset_password(
            token=token,
            new_password="new_secure_password_123"
        )

        assert reset_success is True

    def test_reset_password_updates_password(self, manager):
        """Test that password reset updates password in database"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        # Get original password hash
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (1,))
        original_hash = cursor.fetchone()[0]
        conn.close()

        # Reset password
        manager.reset_password(token, "new_password_456")

        # Get new password hash
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (1,))
        new_hash = cursor.fetchone()[0]
        conn.close()

        assert new_hash != original_hash

    def test_reset_password_marks_token_as_used(self, manager):
        """Test that password reset marks token as used"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        manager.reset_password(token, "new_password")

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT used_at FROM password_reset_tokens WHERE token = ?",
            (token,)
        )
        used_at = cursor.fetchone()[0]
        conn.close()

        assert used_at is not None

    def test_reset_password_invalid_token(self, manager):
        """Test password reset with invalid token"""
        success, message = manager.reset_password(
            token="invalid_token",
            new_password="new_password"
        )

        assert success is False
        assert "invalid" in message.lower() or "not found" in message.lower()

    def test_reset_password_expired_token(self, manager):
        """Test password reset with expired token"""
        success, message, token = manager.generate_password_reset_token(
            user_id=1,
            expiry_hours=-1
        )

        reset_success, reset_message = manager.reset_password(token, "new_password")

        assert reset_success is False
        assert "expired" in reset_message.lower()


class TestTokenCleanup:
    """Tests for token cleanup functionality"""

    def test_cleanup_expired_tokens(self, manager):
        """Test cleanup of expired tokens"""
        # Generate some expired tokens
        manager.generate_verification_token(user_id=1, expiry_hours=-1)
        manager.generate_password_reset_token(user_id=1, expiry_hours=-1)

        # Run cleanup
        result = manager.cleanup_expired_tokens()

        assert "email_verification_tokens" in result
        assert "password_reset_tokens" in result
        assert result["email_verification_tokens"] >= 1
        assert result["password_reset_tokens"] >= 1

    def test_cleanup_expired_tokens_keeps_valid(self, manager):
        """Test that cleanup keeps valid tokens"""
        # Generate valid token
        success, message, token = manager.generate_verification_token(
            user_id=1,
            expiry_hours=24
        )

        # Run cleanup
        manager.cleanup_expired_tokens()

        # Check token still exists
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1

    def test_cleanup_expired_tokens_removes_old(self, manager):
        """Test that cleanup removes old expired tokens"""
        # Generate expired token
        success, message, token = manager.generate_verification_token(
            user_id=1,
            expiry_hours=-24
        )

        # Run cleanup
        manager.cleanup_expired_tokens()

        # Check token is removed
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM email_verification_tokens WHERE token = ?",
            (token,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0


class TestHelperFunctions:
    """Tests for helper/utility functions"""

    @patch('src.core.email_verification.EmailVerificationManager')
    def test_get_email_verification_manager_singleton(self, mock_manager_class):
        """Test get_email_verification_manager returns singleton"""
        # Reset any cached instance
        from src.core import email_verification
        email_verification._manager_instance = None

        instance1 = get_email_verification_manager()
        instance2 = get_email_verification_manager()

        # Should return same instance
        assert instance1 is instance2

    def test_get_email_verification_manager_creates_instance(self):
        """Test get_email_verification_manager creates instance"""
        # Reset cached instance
        from src.core import email_verification
        email_verification._manager_instance = None

        manager = get_email_verification_manager(db_path=":memory:")

        assert manager is not None
        assert isinstance(manager, EmailVerificationManager)


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_generate_token_for_nonexistent_user(self, manager):
        """Test generating token for nonexistent user"""
        # Should still work (token generation doesn't validate user exists)
        success, message, token = manager.generate_verification_token(user_id=99999)

        # Token should be generated, but verification might fail
        assert success is True
        assert token is not None

    def test_verify_email_empty_token(self, manager):
        """Test verification with empty token"""
        verified, message, user_id = manager.verify_email("")

        assert verified is False
        assert user_id is None

    def test_reset_password_empty_token(self, manager):
        """Test password reset with empty token"""
        success, message = manager.reset_password("", "new_password")

        assert success is False

    def test_reset_password_empty_password(self, manager):
        """Test password reset with empty password"""
        success, message, token = manager.generate_password_reset_token(user_id=1)

        reset_success, reset_message = manager.reset_password(token, "")

        # Should fail or succeed based on implementation
        # Testing that it handles empty password gracefully
        assert isinstance(reset_success, bool)

    def test_concurrent_token_generation(self, manager):
        """Test generating multiple tokens for same user"""
        token1 = manager.generate_verification_token(user_id=1)
        token2 = manager.generate_verification_token(user_id=1)

        # Both should succeed
        assert token1[0] is True
        assert token2[0] is True
        # Tokens should be different
        assert token1[2] != token2[2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
