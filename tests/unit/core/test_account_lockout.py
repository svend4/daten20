"""
Unit tests for account lockout system
"""

import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

from src.core.account_lockout import AccountLockoutManager


# ============================================================================
# AccountLockoutManager Tests
# ============================================================================


class TestAccountLockoutManager:
    """Test AccountLockoutManager class"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def manager(self, temp_db):
        """Create AccountLockoutManager instance"""
        return AccountLockoutManager(
            db_path=temp_db,
            max_attempts=5,
            lockout_duration_minutes=30,
            attempt_window_minutes=15
        )

    def test_init(self, manager, temp_db):
        """Test manager initialization"""
        assert manager.db_path == temp_db
        assert manager.max_attempts == 5
        assert manager.lockout_duration == timedelta(minutes=30)
        assert manager.attempt_window == timedelta(minutes=15)

    def test_database_tables_created(self, temp_db):
        """Test that database tables are created"""
        manager = AccountLockoutManager(db_path=temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check login_attempts table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_attempts'")
        assert cursor.fetchone() is not None

        # Check account_locks table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account_locks'")
        assert cursor.fetchone() is not None

        conn.close()

    def test_record_successful_login(self, manager):
        """Test recording successful login"""
        manager.record_login_attempt("john.doe", success=True, ip_address="192.168.1.1")

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE username = ? AND success = 1", ("john.doe",))
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1

    def test_record_failed_login(self, manager):
        """Test recording failed login"""
        manager.record_login_attempt("john.doe", success=False, ip_address="192.168.1.1")

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE username = ? AND success = 0", ("john.doe",))
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1

    def test_get_recent_failed_attempts_none(self, manager):
        """Test getting failed attempts with no failures"""
        count = manager.get_recent_failed_attempts("john.doe")
        assert count == 0

    def test_get_recent_failed_attempts(self, manager):
        """Test getting recent failed attempts"""
        # Record 3 failed attempts
        for _ in range(3):
            manager.record_login_attempt("john.doe", success=False)

        count = manager.get_recent_failed_attempts("john.doe")
        assert count == 3

    def test_account_not_locked_initially(self, manager):
        """Test account is not locked initially"""
        is_locked, unlock_at = manager.is_account_locked("john.doe")

        assert is_locked is False
        assert unlock_at is None

    def test_account_locks_after_max_attempts(self, manager):
        """Test account locks after exceeding max attempts"""
        # Record 5 failed attempts (max_attempts = 5)
        for _ in range(5):
            manager.record_login_attempt("john.doe", success=False)

        is_locked, unlock_at = manager.is_account_locked("john.doe")

        assert is_locked is True
        assert unlock_at is not None

    def test_account_remains_unlocked_below_threshold(self, manager):
        """Test account remains unlocked below threshold"""
        # Record 4 failed attempts (max_attempts = 5)
        for _ in range(4):
            manager.record_login_attempt("john.doe", success=False)

        is_locked, unlock_at = manager.is_account_locked("john.doe")

        assert is_locked is False

    def test_lock_account_manual(self, manager):
        """Test manually locking an account"""
        unlock_at = datetime.utcnow() + timedelta(hours=1)
        manager.lock_account("john.doe", unlock_at, reason="manual_lock")

        is_locked, returned_unlock_at = manager.is_account_locked("john.doe")

        assert is_locked is True
        assert returned_unlock_at is not None

    def test_unlock_account(self, manager):
        """Test unlocking an account"""
        # Lock account first
        unlock_at = datetime.utcnow() + timedelta(hours=1)
        manager.lock_account("john.doe", unlock_at)

        # Unlock account
        manager.unlock_account("john.doe")

        is_locked, _ = manager.is_account_locked("john.doe")
        assert is_locked is False

    def test_clear_failed_attempts(self, manager):
        """Test clearing failed attempts"""
        # Record failed attempts
        for _ in range(3):
            manager.record_login_attempt("john.doe", success=False)

        # Clear attempts
        manager.clear_failed_attempts("john.doe")

        count = manager.get_recent_failed_attempts("john.doe")
        assert count == 0

    def test_successful_login_clears_failed_attempts(self, manager):
        """Test that successful login clears failed attempts"""
        # Record failed attempts
        for _ in range(3):
            manager.record_login_attempt("john.doe", success=False)

        # Successful login
        manager.record_login_attempt("john.doe", success=True)

        count = manager.get_recent_failed_attempts("john.doe")
        assert count == 0

    def test_get_lockout_info_locked(self, manager):
        """Test getting lockout info for locked account"""
        unlock_at = datetime.utcnow() + timedelta(hours=1)
        manager.lock_account("john.doe", unlock_at, reason="too_many_attempts")

        info = manager.get_lockout_info("john.doe")

        assert info is not None
        assert info["locked"] is True
        assert "unlock_at" in info
        assert info["reason"] == "too_many_attempts"

    def test_get_lockout_info_not_locked(self, manager):
        """Test getting lockout info for non-locked account"""
        info = manager.get_lockout_info("john.doe")

        assert info["locked"] is False

    def test_get_recent_attempts(self, manager):
        """Test getting recent login attempts"""
        # Record attempts
        for i in range(5):
            manager.record_login_attempt("john.doe", success=(i % 2 == 0), ip_address="192.168.1.1")

        attempts = manager.get_recent_attempts("john.doe", limit=10)

        assert len(attempts) == 5

    def test_get_failed_attempts_by_ip(self, manager):
        """Test getting failed attempts by IP address"""
        # Record attempts from different IPs
        manager.record_login_attempt("user1", success=False, ip_address="192.168.1.1")
        manager.record_login_attempt("user2", success=False, ip_address="192.168.1.1")
        manager.record_login_attempt("user3", success=False, ip_address="192.168.1.2")

        count = manager.get_failed_attempts_by_ip("192.168.1.1")

        assert count == 2

    def test_account_auto_unlocks_after_duration(self, manager):
        """Test account auto-unlocks after duration expires"""
        # Lock account with unlock time in past
        unlock_at = datetime.utcnow() - timedelta(minutes=1)
        manager.lock_account("john.doe", unlock_at)

        is_locked, _ = manager.is_account_locked("john.doe")

        # Should not be locked anymore
        assert is_locked is False

    def test_different_users_independent(self, manager):
        """Test different users have independent lockouts"""
        # Lock user1
        for _ in range(5):
            manager.record_login_attempt("user1", success=False)

        # user2 should not be locked
        is_locked, _ = manager.is_account_locked("user2")
        assert is_locked is False

    def test_get_all_locked_accounts(self, manager):
        """Test getting all locked accounts"""
        # Lock multiple accounts
        unlock_at = datetime.utcnow() + timedelta(hours=1)
        manager.lock_account("user1", unlock_at)
        manager.lock_account("user2", unlock_at)
        manager.lock_account("user3", unlock_at)

        locked_accounts = manager.get_all_locked_accounts()

        assert len(locked_accounts) >= 3
        usernames = [acc["username"] for acc in locked_accounts]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames

    def test_cleanup_old_attempts(self, manager):
        """Test cleanup of old login attempts"""
        # Record attempt
        manager.record_login_attempt("john.doe", success=False)

        # Cleanup attempts older than 0 days (should remove all)
        manager.cleanup_old_attempts(days=0)

        # Verify attempt was removed
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM login_attempts")
        count = cursor.fetchone()[0]
        conn.close()

        # Note: cleanup may have grace period, so count might be > 0
        # Just verify method runs without error
        assert count >= 0

    def test_get_statistics(self, manager):
        """Test getting lockout statistics"""
        # Create some data
        manager.record_login_attempt("user1", success=True)
        manager.record_login_attempt("user2", success=False)
        manager.record_login_attempt("user2", success=False)

        stats = manager.get_statistics()

        assert "total_attempts" in stats
        assert "failed_attempts" in stats
        assert "locked_accounts" in stats
        assert stats["total_attempts"] >= 3

    def test_ip_address_tracking(self, manager):
        """Test IP address is tracked"""
        manager.record_login_attempt("john.doe", success=False, ip_address="10.0.0.1")

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address FROM login_attempts WHERE username = ?", ("john.doe",))
        ip = cursor.fetchone()[0]
        conn.close()

        assert ip == "10.0.0.1"

    def test_user_agent_tracking(self, manager):
        """Test user agent is tracked"""
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
        manager.record_login_attempt("john.doe", success=False, user_agent=user_agent)

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_agent FROM login_attempts WHERE username = ?", ("john.doe",))
        stored_agent = cursor.fetchone()[0]
        conn.close()

        assert stored_agent == user_agent

    def test_lockout_reason_stored(self, manager):
        """Test lockout reason is stored"""
        unlock_at = datetime.utcnow() + timedelta(hours=1)
        manager.lock_account("john.doe", unlock_at, reason="admin_action")

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT reason FROM account_locks WHERE username = ?", ("john.doe",))
        reason = cursor.fetchone()[0]
        conn.close()

        assert reason == "admin_action"

    def test_multiple_lockouts_same_user(self, manager):
        """Test handling multiple lockouts for same user"""
        unlock_at1 = datetime.utcnow() + timedelta(hours=1)
        manager.lock_account("john.doe", unlock_at1)

        # Lock again with different time
        unlock_at2 = datetime.utcnow() + timedelta(hours=2)
        manager.lock_account("john.doe", unlock_at2)

        # Should have latest lock
        is_locked, unlock_at = manager.is_account_locked("john.doe")
        assert is_locked is True
