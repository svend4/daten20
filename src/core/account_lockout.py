"""
Account Lockout System

Protects against brute-force attacks by tracking failed login attempts
and temporarily locking accounts after exceeding threshold.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger('dms.account_lockout')


class AccountLockoutManager:
    """Manage account lockout after failed login attempts."""

    def __init__(
        self,
        db_path: str = 'data/db/users.db',
        max_attempts: int = 5,
        lockout_duration_minutes: int = 30,
        attempt_window_minutes: int = 15
    ):
        """
        Initialize account lockout manager.

        Args:
            db_path: Path to user database
            max_attempts: Maximum failed attempts before lockout
            lockout_duration_minutes: Lockout duration in minutes
            attempt_window_minutes: Time window to track attempts
        """
        self.db_path = db_path
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.attempt_window = timedelta(minutes=attempt_window_minutes)
        self._init_database()
        logger.info(f"Account lockout initialized: max_attempts={max_attempts}, lockout={lockout_duration_minutes}min")

    def _init_database(self):
        """Initialize lockout tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Login attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT,
                success INTEGER DEFAULT 0,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT
            )
        ''')

        # Account locks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                unlock_at TIMESTAMP NOT NULL,
                reason TEXT DEFAULT 'too_many_failed_attempts',
                locked_by TEXT DEFAULT 'system'
            )
        ''')

        # Add locked_until column to users if not exists
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN locked_until TIMESTAMP NULL')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_attempts_username ON login_attempts(username, attempted_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_locks_username ON account_locks(username)')

        conn.commit()
        conn.close()

    def record_login_attempt(self, username: str, success: bool, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Record login attempt."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO login_attempts (username, success, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (username, 1 if success else 0, ip_address, user_agent))

        conn.commit()
        conn.close()

        if success:
            # Clear failed attempts on successful login
            self.clear_failed_attempts(username)
            logger.info(f"Successful login recorded for: {username}")
        else:
            # Check if should lock account
            self._check_and_lock(username)
            logger.warning(f"Failed login attempt recorded for: {username}")

    def _check_and_lock(self, username: str):
        """Check if account should be locked and lock it."""
        failed_count = self.get_recent_failed_attempts(username)

        if failed_count >= self.max_attempts:
            unlock_at = datetime.utcnow() + self.lockout_duration
            self.lock_account(username, unlock_at, reason='too_many_failed_attempts')
            logger.warning(f"Account locked due to {failed_count} failed attempts: {username}")

    def get_recent_failed_attempts(self, username: str) -> int:
        """Get count of recent failed attempts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = datetime.utcnow() - self.attempt_window

        cursor.execute('''
            SELECT COUNT(*) FROM login_attempts
            WHERE username = ? AND success = 0
            AND attempted_at >= ?
        ''', (username, cutoff_time.isoformat()))

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def is_account_locked(self, username: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is locked.

        Returns:
            Tuple of (is_locked, unlock_at)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check account_locks table
        cursor.execute('''
            SELECT unlock_at FROM account_locks
            WHERE username = ?
        ''', (username,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, None

        unlock_at = datetime.fromisoformat(row[0])

        # Check if lock expired
        if unlock_at <= datetime.utcnow():
            self.unlock_account(username)
            return False, None

        return True, unlock_at

    def lock_account(self, username: str, unlock_at: datetime, reason: str = 'manual', locked_by: str = 'system'):
        """Lock account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO account_locks
            (username, unlock_at, reason, locked_by)
            VALUES (?, ?, ?, ?)
        ''', (username, unlock_at.isoformat(), reason, locked_by))

        # Update users table
        cursor.execute('''
            UPDATE users
            SET locked_until = ?
            WHERE username = ?
        ''', (unlock_at.isoformat(), username))

        conn.commit()
        conn.close()

        logger.info(f"Account locked: {username} until {unlock_at}")

    def unlock_account(self, username: str):
        """Unlock account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM account_locks WHERE username = ?', (username,))

        cursor.execute('''
            UPDATE users
            SET locked_until = NULL
            WHERE username = ?
        ''', (username,))

        conn.commit()
        conn.close()

        logger.info(f"Account unlocked: {username}")

    def clear_failed_attempts(self, username: str):
        """Clear failed login attempts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete old failed attempts
        cutoff_time = datetime.utcnow() - self.attempt_window

        cursor.execute('''
            DELETE FROM login_attempts
            WHERE username = ? AND success = 0 AND attempted_at < ?
        ''', (username, cutoff_time.isoformat()))

        conn.commit()
        conn.close()

    def get_lockout_info(self, username: str) -> Dict:
        """Get lockout information for user."""
        is_locked, unlock_at = self.is_account_locked(username)
        failed_attempts = self.get_recent_failed_attempts(username)

        return {
            'is_locked': is_locked,
            'unlock_at': unlock_at.isoformat() if unlock_at else None,
            'failed_attempts': failed_attempts,
            'max_attempts': self.max_attempts,
            'remaining_attempts': max(0, self.max_attempts - failed_attempts)
        }

    def cleanup_expired_locks(self) -> int:
        """Remove expired locks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM account_locks
            WHERE unlock_at <= ?
        ''', (datetime.utcnow().isoformat(),))

        deleted = cursor.rowcount

        # Clean users table
        cursor.execute('''
            UPDATE users
            SET locked_until = NULL
            WHERE locked_until IS NOT NULL AND locked_until <= ?
        ''', (datetime.utcnow().isoformat(),))

        conn.commit()
        conn.close()

        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired locks")

        return deleted

    def get_all_locked_accounts(self) -> list:
        """Get all currently locked accounts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, locked_at, unlock_at, reason
            FROM account_locks
            WHERE unlock_at > ?
            ORDER BY locked_at DESC
        ''', (datetime.utcnow().isoformat(),))

        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'username': row[0],
                'locked_at': row[1],
                'unlock_at': row[2],
                'reason': row[3]
            })

        conn.close()
        return accounts


# Global instance
_lockout_manager: Optional[AccountLockoutManager] = None


def get_lockout_manager(
    db_path: str = 'data/db/users.db',
    max_attempts: int = 5,
    lockout_duration_minutes: int = 30
) -> AccountLockoutManager:
    """Get or create account lockout manager instance."""
    global _lockout_manager
    if _lockout_manager is None:
        _lockout_manager = AccountLockoutManager(
            db_path=db_path,
            max_attempts=max_attempts,
            lockout_duration_minutes=lockout_duration_minutes
        )
    return _lockout_manager
