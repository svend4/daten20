"""Tests for Account Lockout System"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta

from src.core.account_lockout import AccountLockoutManager, get_lockout_manager


@pytest.fixture
def temp_db():
    """Create temporary database."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Create users table
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    cursor.execute("INSERT INTO users (username, password_hash) VALUES ('testuser', 'hash')")
    conn.commit()
    conn.close()

    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def lockout_manager(temp_db):
    """Create lockout manager instance."""
    return AccountLockoutManager(db_path=temp_db, max_attempts=3, lockout_duration_minutes=5)


class TestAccountLockoutManager:
    """Test AccountLockoutManager."""

    def test_init(self, temp_db):
        """Test initialization."""
        manager = AccountLockoutManager(temp_db)
        assert manager.db_path == temp_db
        assert manager.max_attempts == 5

    def test_record_successful_login(self, lockout_manager):
        """Test recording successful login."""
        lockout_manager.record_login_attempt('testuser', success=True, ip_address='127.0.0.1')
        
        attempts = lockout_manager.get_recent_failed_attempts('testuser')
        assert attempts == 0

    def test_record_failed_login(self, lockout_manager):
        """Test recording failed login."""
        lockout_manager.record_login_attempt('testuser', success=False, ip_address='127.0.0.1')
        
        attempts = lockout_manager.get_recent_failed_attempts('testuser')
        assert attempts == 1

    def test_account_lockout_after_max_attempts(self, lockout_manager):
        """Test account locks after max attempts."""
        # Record 3 failed attempts (max_attempts=3)
        for i in range(3):
            lockout_manager.record_login_attempt('testuser', success=False)
        
        # Check if locked
        is_locked, unlock_at = lockout_manager.is_account_locked('testuser')
        assert is_locked is True
        assert unlock_at is not None

    def test_account_not_locked_before_max(self, lockout_manager):
        """Test account not locked before max attempts."""
        lockout_manager.record_login_attempt('testuser', success=False)
        lockout_manager.record_login_attempt('testuser', success=False)
        
        is_locked, _ = lockout_manager.is_account_locked('testuser')
        assert is_locked is False

    def test_clear_failed_attempts(self, lockout_manager):
        """Test clearing failed attempts."""
        lockout_manager.record_login_attempt('testuser', success=False)
        lockout_manager.record_login_attempt('testuser', success=False)
        
        lockout_manager.clear_failed_attempts('testuser')
        attempts = lockout_manager.get_recent_failed_attempts('testuser')
        assert attempts == 0

    def test_unlock_account(self, lockout_manager):
        """Test unlocking account."""
        # Lock account
        unlock_at = datetime.utcnow() + timedelta(minutes=30)
        lockout_manager.lock_account('testuser', unlock_at)
        
        # Unlock
        lockout_manager.unlock_account('testuser')
        
        is_locked, _ = lockout_manager.is_account_locked('testuser')
        assert is_locked is False

    def test_get_lockout_info(self, lockout_manager):
        """Test getting lockout info."""
        lockout_manager.record_login_attempt('testuser', success=False)
        
        info = lockout_manager.get_lockout_info('testuser')
        assert 'is_locked' in info
        assert 'failed_attempts' in info
        assert info['failed_attempts'] == 1
        assert info['remaining_attempts'] == 2

    def test_cleanup_expired_locks(self, lockout_manager):
        """Test cleaning up expired locks."""
        # Create expired lock
        unlock_at = datetime.utcnow() - timedelta(minutes=1)
        lockout_manager.lock_account('testuser', unlock_at)
        
        deleted = lockout_manager.cleanup_expired_locks()
        assert deleted >= 1

    def test_get_all_locked_accounts(self, lockout_manager):
        """Test getting all locked accounts."""
        unlock_at = datetime.utcnow() + timedelta(minutes=30)
        lockout_manager.lock_account('testuser', unlock_at)
        
        accounts = lockout_manager.get_all_locked_accounts()
        assert len(accounts) == 1
        assert accounts[0]['username'] == 'testuser'


class TestGlobalInstance:
    """Test global instance."""

    def test_get_lockout_manager(self, temp_db):
        """Test getting global instance."""
        manager1 = get_lockout_manager(temp_db)
        manager2 = get_lockout_manager(temp_db)
        assert manager1 is manager2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
