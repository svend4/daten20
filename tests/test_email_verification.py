"""
Tests for Email Verification and Password Reset System
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from src.core.email_verification import EmailVerificationManager, get_email_verification_manager
from src.core.email_notifier import EmailNotifier
from flask_bcrypt import Bcrypt


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize database with users table
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            is_active INTEGER DEFAULT 1,
            email_verified INTEGER DEFAULT 0,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert test user
    cursor.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    ''', ('testuser', 'test@example.com', 'hashed_password'))

    conn.commit()
    conn.close()

    yield path

    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def email_manager(temp_db):
    """Create email verification manager instance."""
    return EmailVerificationManager(
        db_path=temp_db,
        email_notifier=None,  # Disable email sending for tests
        base_url='http://test.local'
    )


@pytest.fixture
def bcrypt_instance():
    """Create Bcrypt instance."""
    return Bcrypt()


class TestEmailVerificationManager:
    """Test EmailVerificationManager class."""

    def test_init_database(self, email_manager, temp_db):
        """Test database initialization."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN (
                'email_verification_tokens',
                'password_reset_tokens'
            )
        """)
        tables = [row[0] for row in cursor.fetchall()]

        assert 'email_verification_tokens' in tables
        assert 'password_reset_tokens' in tables

        # Check if email_verified column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        assert 'email_verified' in columns

        conn.close()

    def test_generate_verification_token(self, email_manager, temp_db):
        """Test generating verification token."""
        token = email_manager.generate_verification_token(
            user_id=1,
            email='test@example.com',
            ip_address='127.0.0.1'
        )

        assert token is not None
        assert len(token) > 0

        # Verify token in database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, token, ip_address
            FROM email_verification_tokens
            WHERE token = ?
        ''', (token,))

        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 1
        assert row[1] == token
        assert row[2] == '127.0.0.1'

    def test_generate_verification_token_invalidates_old(self, email_manager, temp_db):
        """Test that generating new token invalidates old ones."""
        # Generate first token
        token1 = email_manager.generate_verification_token(1, 'test@example.com')

        # Generate second token
        token2 = email_manager.generate_verification_token(1, 'test@example.com')

        assert token1 != token2

        # Verify first token is invalidated (expired)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT expires_at FROM email_verification_tokens
            WHERE token = ?
        ''', (token1,))

        row = cursor.fetchone()
        conn.close()

        expires_at = datetime.fromisoformat(row[0])
        assert expires_at < datetime.utcnow()

    def test_send_verification_email_without_notifier(self, email_manager):
        """Test sending verification email without email notifier."""
        success, result = email_manager.send_verification_email(
            user_id=1,
            email='test@example.com',
            username='testuser',
            ip_address='127.0.0.1'
        )

        assert success is True
        # Should return token when email notifier is disabled
        assert len(result) > 0

    def test_verify_email_success(self, email_manager, temp_db):
        """Test successful email verification."""
        # Generate token
        token = email_manager.generate_verification_token(1, 'test@example.com')

        # Verify email
        success, message, user_id = email_manager.verify_email(token)

        assert success is True
        assert user_id == 1
        assert 'successfully' in message.lower()

        # Check database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check user email_verified status
        cursor.execute('SELECT email_verified FROM users WHERE id = ?', (1,))
        assert cursor.fetchone()[0] == 1

        # Check token verified_at
        cursor.execute('''
            SELECT verified_at FROM email_verification_tokens WHERE token = ?
        ''', (token,))
        assert cursor.fetchone()[0] is not None

        conn.close()

    def test_verify_email_invalid_token(self, email_manager):
        """Test verification with invalid token."""
        success, message, user_id = email_manager.verify_email('invalid_token_123')

        assert success is False
        assert user_id is None
        assert 'invalid' in message.lower()

    def test_verify_email_already_verified(self, email_manager, temp_db):
        """Test verification of already verified email."""
        # Generate and verify token
        token = email_manager.generate_verification_token(1, 'test@example.com')
        email_manager.verify_email(token)

        # Try to verify again
        success, message, user_id = email_manager.verify_email(token)

        assert success is True
        assert 'already verified' in message.lower()

    def test_verify_email_expired_token(self, email_manager, temp_db):
        """Test verification with expired token."""
        # Generate token
        token = email_manager.generate_verification_token(1, 'test@example.com', expires_in=-3600)

        # Try to verify
        success, message, user_id = email_manager.verify_email(token)

        assert success is False
        assert user_id is None
        assert 'expired' in message.lower()

    def test_generate_password_reset_token(self, email_manager, temp_db):
        """Test generating password reset token."""
        token = email_manager.generate_password_reset_token(
            user_id=1,
            email='test@example.com',
            ip_address='127.0.0.1'
        )

        assert token is not None
        assert len(token) > 0

        # Verify token in database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, token, ip_address
            FROM password_reset_tokens
            WHERE token = ?
        ''', (token,))

        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 1
        assert row[1] == token
        assert row[2] == '127.0.0.1'

    def test_send_password_reset_email_without_notifier(self, email_manager):
        """Test sending password reset email without email notifier."""
        success, result = email_manager.send_password_reset_email(
            email='test@example.com',
            ip_address='127.0.0.1'
        )

        assert success is True
        # Should return token when email notifier is disabled
        assert len(result) > 0

    def test_send_password_reset_email_nonexistent_user(self, email_manager):
        """Test sending password reset email for non-existent user."""
        success, message = email_manager.send_password_reset_email(
            email='nonexistent@example.com',
            ip_address='127.0.0.1'
        )

        # Should return success for security (don't reveal if email exists)
        assert success is True
        assert 'sent' in message.lower() or 'exists' in message.lower()

    def test_verify_reset_token_success(self, email_manager):
        """Test verifying valid reset token."""
        token = email_manager.generate_password_reset_token(1, 'test@example.com')

        valid, message, user_id = email_manager.verify_reset_token(token)

        assert valid is True
        assert user_id == 1
        assert 'valid' in message.lower()

    def test_verify_reset_token_invalid(self, email_manager):
        """Test verifying invalid reset token."""
        valid, message, user_id = email_manager.verify_reset_token('invalid_token_123')

        assert valid is False
        assert user_id is None
        assert 'invalid' in message.lower()

    def test_verify_reset_token_expired(self, email_manager):
        """Test verifying expired reset token."""
        token = email_manager.generate_password_reset_token(
            1, 'test@example.com', expires_in=-3600
        )

        valid, message, user_id = email_manager.verify_reset_token(token)

        assert valid is False
        assert user_id is None
        assert 'expired' in message.lower()

    def test_reset_password_success(self, email_manager, temp_db, bcrypt_instance):
        """Test successful password reset."""
        # Generate token
        token = email_manager.generate_password_reset_token(1, 'test@example.com')

        # Reset password
        success, message = email_manager.reset_password(
            token=token,
            new_password='new_password_123',
            bcrypt_instance=bcrypt_instance,
            ip_address='127.0.0.1'
        )

        assert success is True
        assert 'successfully' in message.lower()

        # Verify password was changed
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (1,))
        new_hash = cursor.fetchone()[0]

        # Verify new password
        assert bcrypt_instance.check_password_hash(new_hash, 'new_password_123')

        # Verify token was marked as used
        cursor.execute('''
            SELECT used_at FROM password_reset_tokens WHERE token = ?
        ''', (token,))
        assert cursor.fetchone()[0] is not None

        conn.close()

    def test_reset_password_invalid_token(self, email_manager, bcrypt_instance):
        """Test password reset with invalid token."""
        success, message = email_manager.reset_password(
            token='invalid_token_123',
            new_password='new_password_123',
            bcrypt_instance=bcrypt_instance
        )

        assert success is False
        assert 'invalid' in message.lower()

    def test_reset_password_used_token(self, email_manager, bcrypt_instance):
        """Test password reset with already used token."""
        # Generate and use token
        token = email_manager.generate_password_reset_token(1, 'test@example.com')
        email_manager.reset_password(
            token=token,
            new_password='new_password_123',
            bcrypt_instance=bcrypt_instance
        )

        # Try to use again
        success, message = email_manager.reset_password(
            token=token,
            new_password='another_password',
            bcrypt_instance=bcrypt_instance
        )

        assert success is False
        assert 'used' in message.lower()

    def test_is_email_verified(self, email_manager, temp_db):
        """Test checking if email is verified."""
        # Initially not verified
        assert email_manager.is_email_verified(1) is False

        # Verify email
        token = email_manager.generate_verification_token(1, 'test@example.com')
        email_manager.verify_email(token)

        # Should be verified now
        assert email_manager.is_email_verified(1) is True

    def test_cleanup_expired_tokens(self, email_manager, temp_db):
        """Test cleaning up expired tokens."""
        # Generate expired tokens
        email_manager.generate_verification_token(1, 'test@example.com', expires_in=-3600)
        email_manager.generate_password_reset_token(1, 'test@example.com', expires_in=-3600)

        # Run cleanup
        stats = email_manager.cleanup_expired_tokens()

        assert stats['verification_tokens_deleted'] > 0
        assert stats['reset_tokens_deleted'] > 0

    def test_multiple_reset_tokens_invalidation(self, email_manager, temp_db):
        """Test that new reset token invalidates old ones."""
        # Generate first token
        token1 = email_manager.generate_password_reset_token(1, 'test@example.com')

        # Generate second token
        token2 = email_manager.generate_password_reset_token(1, 'test@example.com')

        assert token1 != token2

        # Verify first token is invalidated
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT expires_at FROM password_reset_tokens WHERE token = ?
        ''', (token1,))

        row = cursor.fetchone()
        expires_at = datetime.fromisoformat(row[0])
        assert expires_at < datetime.utcnow()

        conn.close()


class TestGlobalInstance:
    """Test global instance management."""

    def test_get_email_verification_manager(self):
        """Test getting global instance."""
        manager1 = get_email_verification_manager()
        manager2 = get_email_verification_manager()

        # Should return same instance
        assert manager1 is manager2


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def test_complete_email_verification_workflow(self, email_manager):
        """Test complete email verification workflow."""
        # 1. Send verification email
        success, token = email_manager.send_verification_email(
            user_id=1,
            email='test@example.com',
            username='testuser'
        )
        assert success is True

        # 2. Verify email
        success, message, user_id = email_manager.verify_email(token)
        assert success is True
        assert user_id == 1

        # 3. Check verification status
        assert email_manager.is_email_verified(1) is True

    def test_complete_password_reset_workflow(self, email_manager, bcrypt_instance):
        """Test complete password reset workflow."""
        # 1. Request password reset
        success, token = email_manager.send_password_reset_email(
            email='test@example.com'
        )
        assert success is True

        # 2. Verify token
        valid, message, user_id = email_manager.verify_reset_token(token)
        assert valid is True
        assert user_id == 1

        # 3. Reset password
        success, message = email_manager.reset_password(
            token=token,
            new_password='secure_new_password_123',
            bcrypt_instance=bcrypt_instance
        )
        assert success is True

        # 4. Verify token can't be reused
        success, message = email_manager.reset_password(
            token=token,
            new_password='another_password',
            bcrypt_instance=bcrypt_instance
        )
        assert success is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
