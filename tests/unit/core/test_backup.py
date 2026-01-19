"""
Comprehensive tests for core/backup.py module.

Tests backup creation, restoration, scheduling, encryption, retention policies,
and security features (path traversal protection).
"""

import os
import tarfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


# ============================================================================
# BackupManager Tests
# ============================================================================


class TestBackupManager:
    """Test BackupManager functionality."""

    @pytest.fixture
    def backup_dir(self, tmp_path):
        """Create temporary backup directory."""
        return tmp_path / "backups"

    @pytest.fixture
    def manager(self, backup_dir):
        """Create BackupManager instance."""
        from src.core.backup import BackupManager

        return BackupManager(
            backup_dir=str(backup_dir), retention_days=30, max_backups=50, encrypt=False
        )

    def test_backup_manager_initialization(self, backup_dir):
        """Test BackupManager initialization"""
        from src.core.backup import BackupManager

        manager = BackupManager(backup_dir=str(backup_dir))

        assert manager.backup_dir == backup_dir
        assert manager.retention_days == 30
        assert manager.max_backups == 50
        assert manager.encrypt is False
        assert backup_dir.exists()

    def test_backup_manager_custom_settings(self, backup_dir):
        """Test BackupManager with custom settings"""
        from src.core.backup import BackupManager

        manager = BackupManager(
            backup_dir=str(backup_dir), retention_days=7, max_backups=10, encrypt=False
        )

        assert manager.retention_days == 7
        assert manager.max_backups == 10

    @patch("src.core.backup.ENCRYPTION_AVAILABLE", False)
    def test_backup_manager_encryption_unavailable(self, backup_dir):
        """Test BackupManager raises error when encryption unavailable"""
        from src.core.backup import BackupManager

        with pytest.raises(RuntimeError, match="Encryption requested but not available"):
            BackupManager(backup_dir=str(backup_dir), encrypt=True)

    @patch("src.core.backup.ENCRYPTION_AVAILABLE", True)
    @patch("src.core.backup.BackupEncryption")
    def test_backup_manager_encryption_available(self, mock_encryption_class, backup_dir):
        """Test BackupManager with encryption enabled"""
        from src.core.backup import BackupManager

        mock_encryptor = Mock()
        mock_encryption_class.return_value = mock_encryptor

        manager = BackupManager(backup_dir=str(backup_dir), encrypt=True, encryption_key=b"testkey")

        assert manager.encrypt is True
        assert manager.encryptor is mock_encryptor
        mock_encryption_class.assert_called_once_with(key=b"testkey")

    def test_create_backup_basic(self, manager, tmp_path):
        """Test basic backup creation"""
        # Create some test data
        data_dir = Path("data/db")
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "test.db").write_text("test data")

        backup_path = manager.create_backup(include_files=False)

        assert Path(backup_path).exists()
        assert backup_path.endswith(".tar.gz")
        assert "dms_backup_" in backup_path

        # Cleanup
        (data_dir / "test.db").unlink()
        data_dir.rmdir()
        data_dir.parent.rmdir()

    def test_create_backup_includes_database(self, manager, tmp_path):
        """Test backup includes database"""
        # Create test database
        db_dir = Path("data/db")
        db_dir.mkdir(parents=True, exist_ok=True)
        db_file = db_dir / "services.db"
        db_file.write_text("database content")

        backup_path = manager.create_backup(include_files=False)

        # Verify backup contains database
        with tarfile.open(backup_path, "r:gz") as tar:
            names = tar.getnames()
            assert any("db" in name for name in names)

        # Cleanup
        db_file.unlink()
        db_dir.rmdir()
        db_dir.parent.rmdir()

    def test_create_backup_includes_config(self, manager, tmp_path):
        """Test backup includes configuration"""
        # Create test config
        config_dir = Path("config")
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "settings.json"
        config_file.write_text('{"test": "config"}')

        backup_path = manager.create_backup(include_files=False)

        # Verify backup contains config
        with tarfile.open(backup_path, "r:gz") as tar:
            names = tar.getnames()
            assert any("config" in name for name in names)

        # Cleanup
        config_file.unlink()
        config_dir.rmdir()

    def test_create_backup_with_files(self, manager, tmp_path):
        """Test backup includes files when requested"""
        # Create test exports
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        export_file = exports_dir / "export.pdf"
        export_file.write_text("export content")

        backup_path = manager.create_backup(include_files=True)

        # Verify backup contains exports
        with tarfile.open(backup_path, "r:gz") as tar:
            names = tar.getnames()
            assert any("exports" in name for name in names)

        # Cleanup
        export_file.unlink()
        exports_dir.rmdir()
        exports_dir.parent.rmdir()

    def test_create_backup_without_files(self, manager, tmp_path):
        """Test backup excludes files when not requested"""
        # Create test exports
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        export_file = exports_dir / "export.pdf"
        export_file.write_text("export content")

        backup_path = manager.create_backup(include_files=False)

        # Verify backup does not contain exports
        with tarfile.open(backup_path, "r:gz") as tar:
            names = tar.getnames()
            assert not any("exports" in name for name in names)

        # Cleanup
        export_file.unlink()
        exports_dir.rmdir()
        exports_dir.parent.rmdir()

    def test_restore_backup_nonexistent(self, manager):
        """Test restore raises error for nonexistent backup"""
        with pytest.raises(FileNotFoundError):
            manager.restore_backup("nonexistent.tar.gz")

    def test_restore_backup_basic(self, manager, tmp_path):
        """Test basic backup restoration"""
        # Create a test backup file
        backup_file = tmp_path / "test_backup.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            # Create temporary file to add
            temp_file = tmp_path / "test.txt"
            temp_file.write_text("test content")
            tar.add(temp_file, arcname="db/test.txt")

        # Restore
        manager.restore_backup(str(backup_file))

        # Verify restored file
        restored_file = Path("data/db/test.txt")
        assert restored_file.exists()
        assert restored_file.read_text() == "test content"

        # Cleanup
        restored_file.unlink()
        restored_file.parent.rmdir()
        restored_file.parent.parent.rmdir()

    def test_restore_backup_path_traversal_double_dot(self, manager, tmp_path):
        """Test restore prevents path traversal with .."""
        # Create malicious backup
        backup_file = tmp_path / "malicious.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            temp_file = tmp_path / "malicious.txt"
            temp_file.write_text("malicious")
            # Try to escape with ../
            tar.add(temp_file, arcname="../etc/passwd")

        # Restore should raise error
        with pytest.raises(ValueError, match="path traversal"):
            manager.restore_backup(str(backup_file))

    def test_restore_backup_path_traversal_absolute(self, manager, tmp_path):
        """Test restore prevents absolute paths"""
        # Create malicious backup
        backup_file = tmp_path / "malicious.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            temp_file = tmp_path / "malicious.txt"
            temp_file.write_text("malicious")
            # Try absolute path
            tar.add(temp_file, arcname="/etc/passwd")

        # Restore should raise error
        with pytest.raises(ValueError, match="Absolute path not allowed"):
            manager.restore_backup(str(backup_file))

    def test_restore_backup_path_traversal_windows(self, manager, tmp_path):
        """Test restore prevents Windows absolute paths"""
        # Create malicious backup
        backup_file = tmp_path / "malicious.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            temp_file = tmp_path / "malicious.txt"
            temp_file.write_text("malicious")
            # Try Windows absolute path
            tar.add(temp_file, arcname="C:\\Windows\\System32\\malware.exe")

        # Restore should raise error
        with pytest.raises(ValueError, match="Absolute path not allowed"):
            manager.restore_backup(str(backup_file))

    def test_restore_backup_url_encoded_traversal(self, manager, tmp_path):
        """Test restore prevents URL-encoded path traversal"""
        # Create malicious backup
        backup_file = tmp_path / "malicious.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            temp_file = tmp_path / "malicious.txt"
            temp_file.write_text("malicious")
            # Try URL-encoded traversal: %2e%2e%2f = ../
            tar.add(temp_file, arcname="db/%2e%2e%2fetc/passwd")

        # Restore should raise error
        with pytest.raises(ValueError, match="Unsafe path"):
            manager.restore_backup(str(backup_file))

    def test_restore_backup_symlink_traversal(self, manager, tmp_path):
        """Test restore prevents symlink path traversal"""
        # Create malicious backup with symlink
        backup_file = tmp_path / "malicious.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            # Create symlink info
            symlink = tarfile.TarInfo(name="db/malicious_link")
            symlink.type = tarfile.SYMTYPE
            symlink.linkname = "../../etc/passwd"
            tar.addfile(symlink)

        # Restore should raise error
        with pytest.raises(ValueError, match="Unsafe symlink"):
            manager.restore_backup(str(backup_file))

    def test_list_backups_empty(self, manager):
        """Test listing backups when none exist"""
        backups = manager.list_backups()
        assert backups == []

    def test_list_backups_multiple(self, manager, backup_dir):
        """Test listing multiple backups"""
        # Create test backup files
        for i in range(3):
            backup_file = backup_dir / f"dms_backup_2024010{i}_120000.tar.gz"
            backup_file.write_text(f"backup {i}")
            time.sleep(0.01)  # Ensure different timestamps

        backups = manager.list_backups()

        assert len(backups) == 3
        # Should be sorted reverse chronological
        assert "20240102" in backups[0]["name"]
        assert "size" in backups[0]
        assert "created" in backups[0]

    def test_cleanup_old_backups_by_age(self, manager, backup_dir):
        """Test cleanup removes old backups by age"""
        # Create old backup
        old_backup = backup_dir / "dms_backup_20200101_120000.tar.gz"
        old_backup.write_text("old backup")

        # Set modification time to old date
        old_time = (datetime.now() - timedelta(days=60)).timestamp()
        os.utime(old_backup, (old_time, old_time))

        # Create recent backup
        recent_backup = backup_dir / "dms_backup_20240101_120000.tar.gz"
        recent_backup.write_text("recent backup")

        # Run cleanup
        manager._cleanup_old_backups()

        # Old backup should be removed
        assert not old_backup.exists()
        assert recent_backup.exists()

    def test_cleanup_old_backups_by_count(self, manager, backup_dir):
        """Test cleanup removes excess backups"""
        # Set low max_backups
        manager.max_backups = 5

        # Create 10 backups
        for i in range(10):
            backup_file = backup_dir / f"dms_backup_2024010{i:02d}_120000.tar.gz"
            backup_file.write_text(f"backup {i}")
            time.sleep(0.01)

        # Run cleanup
        manager._cleanup_old_backups()

        # Should keep only 5 most recent
        remaining = list(backup_dir.glob("dms_backup_*.tar.gz"))
        assert len(remaining) == 5

    def test_format_size_bytes(self):
        """Test format_size for bytes"""
        from src.core.backup import BackupManager

        assert BackupManager._format_size(500) == "500.00 B"

    def test_format_size_kb(self):
        """Test format_size for kilobytes"""
        from src.core.backup import BackupManager

        assert BackupManager._format_size(1536) == "1.50 KB"

    def test_format_size_mb(self):
        """Test format_size for megabytes"""
        from src.core.backup import BackupManager

        assert BackupManager._format_size(1048576 * 5) == "5.00 MB"

    def test_format_size_gb(self):
        """Test format_size for gigabytes"""
        from src.core.backup import BackupManager

        assert BackupManager._format_size(1073741824 * 2) == "2.00 GB"

    @patch("src.core.backup.ENCRYPTION_AVAILABLE", True)
    @patch("src.core.backup.BackupEncryption")
    def test_create_backup_with_encryption(self, mock_encryption_class, manager, tmp_path):
        """Test creating encrypted backup"""
        # Setup encryption
        mock_encryptor = Mock()
        mock_encryption_class.return_value = mock_encryptor
        manager.encrypt = True
        manager.encryptor = mock_encryptor

        # Create test data
        db_dir = Path("data/db")
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "test.db").write_text("test")

        backup_path = manager.create_backup(include_files=False)

        # Should call encrypt_file
        mock_encryptor.encrypt_file.assert_called_once()
        assert backup_path.endswith(".encrypted")

        # Cleanup
        (db_dir / "test.db").unlink()
        db_dir.rmdir()
        db_dir.parent.rmdir()

    @patch("src.core.backup.ENCRYPTION_AVAILABLE", True)
    @patch("src.core.backup.BackupEncryption")
    def test_restore_encrypted_backup(self, mock_encryption_class, tmp_path):
        """Test restoring encrypted backup"""
        from src.core.backup import BackupManager

        # Setup
        mock_encryptor = Mock()
        mock_encryption_class.return_value = mock_encryptor

        manager = BackupManager(
            backup_dir=str(tmp_path / "backups"), encrypt=True, encryption_key=b"testkey"
        )

        # Create encrypted backup file
        backup_file = tmp_path / "test.tar.gz.encrypted"
        backup_file.write_text("encrypted data")

        # Create decrypted version that will be "decrypted"
        decrypted_file = tmp_path / "test.tar.gz"
        with tarfile.open(decrypted_file, "w:gz") as tar:
            temp_file = tmp_path / "test.txt"
            temp_file.write_text("test")
            tar.add(temp_file, arcname="db/test.txt")

        # Mock decrypt to copy decrypted file
        def mock_decrypt(src, dst, compressed):
            import shutil
            shutil.copy(decrypted_file, dst)

        mock_encryptor.decrypt_file.side_effect = mock_decrypt

        # Restore
        manager.restore_backup(str(backup_file))

        # Should call decrypt_file
        mock_encryptor.decrypt_file.assert_called_once()

        # Cleanup
        restored = Path("data/db/test.txt")
        if restored.exists():
            restored.unlink()
            restored.parent.rmdir()
            restored.parent.parent.rmdir()

    def test_restore_encrypted_without_key(self, manager, tmp_path):
        """Test restoring encrypted backup without key raises error"""
        # Create encrypted backup file
        backup_file = tmp_path / "test.tar.gz.encrypted"
        backup_file.write_text("encrypted data")

        # Restore should raise error
        with pytest.raises(RuntimeError, match="encrypted but no encryption key"):
            manager.restore_backup(str(backup_file))


# ============================================================================
# BackupScheduler Tests
# ============================================================================


class TestBackupScheduler:
    """Test BackupScheduler functionality."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create BackupManager instance."""
        from src.core.backup import BackupManager

        return BackupManager(backup_dir=str(tmp_path / "backups"))

    @pytest.fixture
    def scheduler(self, manager):
        """Create BackupScheduler instance."""
        from src.core.backup import BackupScheduler

        return BackupScheduler(manager)

    def test_scheduler_initialization(self, scheduler, manager):
        """Test BackupScheduler initialization"""
        assert scheduler.backup_manager is manager
        assert scheduler.running is False

    @patch("src.core.backup.schedule")
    def test_schedule_daily(self, mock_schedule, scheduler):
        """Test scheduling daily backup"""
        mock_job = Mock()
        mock_schedule.every.return_value.day.at.return_value.do = Mock(return_value=mock_job)

        scheduler.schedule_daily("03:00")

        mock_schedule.every.return_value.day.at.assert_called_once_with("03:00")

    @patch("src.core.backup.schedule")
    def test_schedule_weekly(self, mock_schedule, scheduler):
        """Test scheduling weekly backup"""
        mock_job = Mock()
        mock_monday = Mock()
        mock_monday.at.return_value.do = Mock(return_value=mock_job)
        mock_schedule.every.return_value.monday = mock_monday

        scheduler.schedule_weekly("monday", "04:00")

        mock_monday.at.assert_called_once_with("04:00")

    def test_run_backup_success(self, scheduler, manager):
        """Test _run_backup executes successfully"""
        manager.create_backup = Mock(return_value="/backups/test.tar.gz")

        scheduler._run_backup()

        manager.create_backup.assert_called_once()

    def test_run_backup_error(self, scheduler, manager):
        """Test _run_backup handles errors"""
        manager.create_backup = Mock(side_effect=Exception("Backup failed"))

        # Should not raise
        scheduler._run_backup()

    @patch("src.core.backup.Thread")
    @patch("src.core.backup.schedule")
    def test_start_scheduler(self, mock_schedule, mock_thread_class, scheduler):
        """Test starting scheduler"""
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        scheduler.start()

        assert scheduler.running is True
        mock_thread_class.assert_called_once()
        mock_thread.start.assert_called_once()

    def test_start_already_running(self, scheduler):
        """Test starting scheduler when already running"""
        scheduler.running = True

        # Should not crash
        scheduler.start()

    def test_stop_scheduler(self, scheduler):
        """Test stopping scheduler"""
        scheduler.running = True

        scheduler.stop()

        assert scheduler.running is False


# ============================================================================
# Global Instance Tests
# ============================================================================


class TestGlobalInstance:
    """Test global backup manager instance."""

    def test_get_backup_manager_singleton(self):
        """Test get_backup_manager returns singleton"""
        from src.core.backup import get_backup_manager

        # Reset global
        import src.core.backup

        src.core.backup._backup_manager = None

        manager1 = get_backup_manager()
        manager2 = get_backup_manager()

        assert manager1 is manager2

    def test_backup_service_alias(self):
        """Test BackupService is alias for BackupManager"""
        from src.core.backup import BackupManager, BackupService

        assert BackupService is BackupManager


# ============================================================================
# Integration Tests
# ============================================================================


class TestBackupIntegration:
    """Integration tests for backup system."""

    def test_full_backup_restore_cycle(self, tmp_path):
        """Test complete backup and restore cycle"""
        from src.core.backup import BackupManager

        # Setup
        backup_dir = tmp_path / "backups"
        manager = BackupManager(backup_dir=str(backup_dir))

        # Create test data
        db_dir = Path("data/db")
        db_dir.mkdir(parents=True, exist_ok=True)
        db_file = db_dir / "test.db"
        db_file.write_text("original data")

        # Create backup
        backup_path = manager.create_backup(include_files=False)
        assert Path(backup_path).exists()

        # Modify data
        db_file.write_text("modified data")

        # Restore backup
        manager.restore_backup(backup_path)

        # Verify restoration
        assert db_file.read_text() == "original data"

        # Cleanup
        db_file.unlink()
        db_dir.rmdir()
        db_dir.parent.rmdir()

    def test_multiple_backups_with_cleanup(self, tmp_path):
        """Test creating multiple backups with cleanup"""
        from src.core.backup import BackupManager

        # Setup with low retention
        backup_dir = tmp_path / "backups"
        manager = BackupManager(backup_dir=str(backup_dir), max_backups=3)

        # Create test data
        db_dir = Path("data/db")
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "test.db").write_text("test")

        # Create 5 backups
        for i in range(5):
            manager.create_backup(include_files=False)
            time.sleep(0.01)

        # Should only keep 3
        backups = manager.list_backups()
        assert len(backups) <= 3

        # Cleanup
        (db_dir / "test.db").unlink()
        db_dir.rmdir()
        db_dir.parent.rmdir()

    @patch("src.core.backup.schedule")
    def test_scheduled_backup_execution(self, mock_schedule, tmp_path):
        """Test scheduled backup execution"""
        from src.core.backup import BackupManager, BackupScheduler

        # Setup
        backup_dir = tmp_path / "backups"
        manager = BackupManager(backup_dir=str(backup_dir))
        scheduler = BackupScheduler(manager)

        # Create test data
        db_dir = Path("data/db")
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "test.db").write_text("test")

        # Schedule and run
        scheduler.schedule_daily("02:00")
        scheduler._run_backup()

        # Verify backup created
        backups = manager.list_backups()
        assert len(backups) >= 1

        # Cleanup
        (db_dir / "test.db").unlink()
        db_dir.rmdir()
        db_dir.parent.rmdir()
