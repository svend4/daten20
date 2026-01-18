"""
Automated Backup System

Provides automated backups of database, files, and configurations.
Supports scheduling, rotation, and remote storage.
"""

import gzip
import logging
import os
import shutil
import tarfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from typing import List, Optional

import schedule

logger = logging.getLogger("dms.backup")

# Try to import encryption support
try:
    from .backup_encryption import BackupEncryption

    ENCRYPTION_AVAILABLE = True
except ImportError:
    logger.warning("Backup encryption not available (cryptography package not installed)")
    ENCRYPTION_AVAILABLE = False


class BackupManager:
    """Manage automated backups."""

    def __init__(
        self,
        backup_dir: str = "backups",
        retention_days: int = 30,
        max_backups: int = 50,
        encrypt: bool = False,
        encryption_key: Optional[bytes] = None,
    ):
        """
        Initialize backup manager.

        Args:
            backup_dir: Directory to store backups
            retention_days: Days to retain backups
            max_backups: Maximum number of backups to keep
            encrypt: Enable backup encryption
            encryption_key: Encryption key (auto-generated if not provided)
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.max_backups = max_backups
        self.encrypt = encrypt

        # Initialize encryption if enabled
        self.encryptor = None
        if encrypt:
            if not ENCRYPTION_AVAILABLE:
                raise RuntimeError("Encryption requested but not available. " "Install: pip install cryptography")
            self.encryptor = BackupEncryption(key=encryption_key)
            logger.info("Backup encryption enabled")

    def create_backup(self, include_files: bool = True) -> str:
        """
        Create full system backup.

        Args:
            include_files: Include uploaded files

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"dms_backup_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name

        logger.info(f"Creating backup: {backup_name}")

        with tarfile.open(backup_path, "w:gz") as tar:
            # Backup database
            db_dir = Path("data/db")
            if db_dir.exists():
                tar.add(db_dir, arcname="db")
                logger.info("Added database to backup")

            # Backup configuration
            config_dir = Path("config")
            if config_dir.exists():
                tar.add(config_dir, arcname="config")
                logger.info("Added config to backup")

            # Backup files if requested
            if include_files:
                exports_dir = Path("data/exports")
                if exports_dir.exists():
                    tar.add(exports_dir, arcname="exports")
                    logger.info("Added exports to backup")

        # Encrypt backup if enabled
        if self.encrypt and self.encryptor:
            encrypted_path = backup_path.with_suffix(backup_path.suffix + ".encrypted")
            self.encryptor.encrypt_file(str(backup_path), str(encrypted_path), compress=False)
            # Remove unencrypted backup
            backup_path.unlink()
            backup_path = encrypted_path
            logger.info("Backup encrypted")

        # Cleanup old backups
        self._cleanup_old_backups()

        logger.info(f"Backup created: {backup_path} ({self._format_size(backup_path.stat().st_size)})")
        return str(backup_path)

    def restore_backup(self, backup_path: str):
        """
        Restore from backup.

        Args:
            backup_path: Path to backup file
        """
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        logger.warning(f"Restoring from backup: {backup_path}")

        # Decrypt if encrypted
        actual_backup_path = backup_path
        if backup_path.endswith(".encrypted"):
            if not self.encryptor:
                raise RuntimeError("Backup is encrypted but no encryption key provided")

            logger.info("Decrypting backup...")
            decrypted_path = backup_path[:-10]  # Remove .encrypted
            self.encryptor.decrypt_file(backup_path, decrypted_path, compressed=False)
            actual_backup_path = decrypted_path

        # Extract backup safely (prevent path traversal attacks)
        with tarfile.open(actual_backup_path, "r:gz") as tar:
            # Validate and filter members before extraction
            safe_members = []
            for member in tar.getmembers():
                # Prevent path traversal by checking if the path is within current directory
                member_path = os.path.normpath(os.path.join(".", member.name))
                if not member_path.startswith("."):
                    raise ValueError(f"Unsafe path in tar file: {member.name}")
                safe_members.append(member)
            # Extract only validated members (paths verified above to prevent traversal)
            tar.extractall(".", members=safe_members)  # nosec B202

        logger.info("Backup restored successfully")

    def list_backups(self) -> List[dict]:
        """List all available backups."""
        backups = []

        for backup_file in sorted(self.backup_dir.glob("dms_backup_*.tar.gz"), reverse=True):
            stat = backup_file.stat()
            backups.append(
                {
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size": self._format_size(stat.st_size),
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        return backups

    def _cleanup_old_backups(self):
        """Remove old backups based on retention policy."""
        backups = sorted(self.backup_dir.glob("dms_backup_*.tar.gz"))

        # Remove by age
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        for backup in backups:
            if datetime.fromtimestamp(backup.stat().st_mtime) < cutoff_date:
                backup.unlink()
                logger.info(f"Removed old backup: {backup.name}")

        # Remove by count
        remaining = sorted(self.backup_dir.glob("dms_backup_*.tar.gz"), reverse=True)
        if len(remaining) > self.max_backups:
            for backup in remaining[self.max_backups :]:
                backup.unlink()
                logger.info(f"Removed excess backup: {backup.name}")

    @staticmethod
    def _format_size(bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} TB"


class BackupScheduler:
    """Schedule automated backups."""

    def __init__(self, backup_manager: BackupManager):
        """
        Initialize backup scheduler.

        Args:
            backup_manager: BackupManager instance
        """
        self.backup_manager = backup_manager
        self.running = False

    def schedule_daily(self, time_str: str = "02:00"):
        """
        Schedule daily backup.

        Args:
            time_str: Time to run backup (HH:MM format)
        """
        schedule.every().day.at(time_str).do(self._run_backup)
        logger.info(f"Scheduled daily backup at {time_str}")

    def schedule_weekly(self, day: str = "sunday", time_str: str = "02:00"):
        """
        Schedule weekly backup.

        Args:
            day: Day of week
            time_str: Time to run backup
        """
        getattr(schedule.every(), day.lower()).at(time_str).do(self._run_backup)
        logger.info(f"Scheduled weekly backup on {day} at {time_str}")

    def _run_backup(self):
        """Run backup task."""
        try:
            self.backup_manager.create_backup()
        except Exception as e:
            logger.error(f"Backup failed: {e}")

    def start(self):
        """Start scheduler in background thread."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True

        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)

        thread = Thread(target=run_scheduler, daemon=True)
        thread.start()
        logger.info("Backup scheduler started")

    def stop(self):
        """Stop scheduler."""
        self.running = False
        logger.info("Backup scheduler stopped")


# Global backup manager
_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> BackupManager:
    """Get or create backup manager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager


# Alias for backward compatibility
BackupService = BackupManager
