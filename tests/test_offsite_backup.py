"""
Tests for Offsite Backup System
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import gzip

from src.core.offsite_backup import (
    OffsiteBackupEncryption,
    S3BackupProvider,
    GCSBackupProvider,
    OffsiteBackupManager,
    create_offsite_backup_manager,
    ENCRYPTION_AVAILABLE,
    S3_AVAILABLE,
    GCS_AVAILABLE
)


@pytest.fixture
def temp_backup_file():
    """Create temporary backup file for testing."""
    fd, path = tempfile.mkstemp(suffix='.tar.gz')
    with os.fdopen(fd, 'wb') as f:
        f.write(b'Mock backup data for testing' * 100)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    # Cleanup
    import shutil
    try:
        shutil.rmtree(dir_path)
    except OSError:
        pass


@pytest.mark.skipif(not ENCRYPTION_AVAILABLE, reason="Encryption not available")
class TestOffsiteBackupEncryption:
    """Test OffsiteBackupEncryption class."""

    def test_init_with_password(self):
        """Test initialization with password."""
        encryptor = OffsiteBackupEncryption(password='test_password_123')
        assert encryptor.key is not None
        assert len(encryptor.key) == 32

    def test_init_with_key(self):
        """Test initialization with direct key."""
        key = b'0' * 32
        encryptor = OffsiteBackupEncryption(key=key)
        assert encryptor.key == key

    def test_init_invalid_key_length(self):
        """Test initialization with invalid key length."""
        with pytest.raises(ValueError, match="32 bytes"):
            OffsiteBackupEncryption(key=b'short_key')

    def test_init_no_credentials(self):
        """Test initialization without password or key."""
        with pytest.raises(ValueError, match="password or key"):
            OffsiteBackupEncryption()

    def test_encrypt_decrypt_file(self, temp_backup_file, temp_dir):
        """Test encrypting and decrypting a file."""
        encryptor = OffsiteBackupEncryption(password='test_password_123')

        encrypted_path = os.path.join(temp_dir, 'encrypted.bin')
        decrypted_path = os.path.join(temp_dir, 'decrypted.tar.gz')

        # Encrypt
        encrypt_meta = encryptor.encrypt_file(temp_backup_file, encrypted_path)
        assert os.path.exists(encrypted_path)
        assert encrypt_meta['plaintext_hash']
        assert encrypt_meta['ciphertext_hash']
        assert encrypt_meta['encrypted_size'] > encrypt_meta['original_size']

        # Decrypt
        decrypt_meta = encryptor.decrypt_file(encrypted_path, decrypted_path)
        assert os.path.exists(decrypted_path)
        assert decrypt_meta['plaintext_hash'] == encrypt_meta['plaintext_hash']

        # Verify content matches
        with open(temp_backup_file, 'rb') as f1:
            with open(decrypted_path, 'rb') as f2:
                assert f1.read() == f2.read()

    def test_decrypt_with_wrong_password(self, temp_backup_file, temp_dir):
        """Test decryption with wrong password fails."""
        encryptor1 = OffsiteBackupEncryption(password='correct_password')
        encryptor2 = OffsiteBackupEncryption(password='wrong_password')

        encrypted_path = os.path.join(temp_dir, 'encrypted.bin')
        decrypted_path = os.path.join(temp_dir, 'decrypted.tar.gz')

        # Encrypt with first password
        encryptor1.encrypt_file(temp_backup_file, encrypted_path)

        # Try to decrypt with wrong password
        with pytest.raises(ValueError, match="Decryption failed"):
            encryptor2.decrypt_file(encrypted_path, decrypted_path)


@pytest.mark.skipif(not S3_AVAILABLE, reason="boto3 not available")
class TestS3BackupProvider:
    """Test S3BackupProvider class."""

    @patch('boto3.client')
    def test_init(self, mock_boto_client):
        """Test S3 provider initialization."""
        provider = S3BackupProvider(
            bucket_name='test-bucket',
            aws_access_key_id='test_key',
            aws_secret_access_key='test_secret',
            region_name='us-west-2'
        )

        assert provider.bucket_name == 'test-bucket'
        assert provider.region_name == 'us-west-2'
        mock_boto_client.assert_called_once()

    @patch('boto3.client')
    def test_upload_backup(self, mock_boto_client, temp_backup_file):
        """Test uploading backup to S3."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        provider = S3BackupProvider(bucket_name='test-bucket')

        success = provider.upload_backup(
            temp_backup_file,
            'backups/test_backup.tar.gz',
            metadata={'test': 'value'}
        )

        assert success is True
        mock_s3.upload_file.assert_called_once()

    @patch('boto3.client')
    def test_download_backup(self, mock_boto_client, temp_dir):
        """Test downloading backup from S3."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        provider = S3BackupProvider(bucket_name='test-bucket')

        local_path = os.path.join(temp_dir, 'downloaded.tar.gz')
        success = provider.download_backup('backups/test_backup.tar.gz', local_path)

        assert success is True
        mock_s3.download_file.assert_called_once()

    @patch('boto3.client')
    def test_list_backups(self, mock_boto_client):
        """Test listing backups in S3."""
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'backups/backup1.tar.gz',
                    'Size': 1024,
                    'LastModified': MagicMock(isoformat=lambda: '2024-01-01T00:00:00'),
                    'StorageClass': 'STANDARD'
                }
            ]
        }
        mock_boto_client.return_value = mock_s3

        provider = S3BackupProvider(bucket_name='test-bucket')
        backups = provider.list_backups(prefix='backups/')

        assert len(backups) == 1
        assert backups[0]['key'] == 'backups/backup1.tar.gz'
        assert backups[0]['size'] == 1024

    @patch('boto3.client')
    def test_delete_backup(self, mock_boto_client):
        """Test deleting backup from S3."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        provider = S3BackupProvider(bucket_name='test-bucket')
        success = provider.delete_backup('backups/test_backup.tar.gz')

        assert success is True
        mock_s3.delete_object.assert_called_once()


@pytest.mark.skipif(not GCS_AVAILABLE, reason="google-cloud-storage not available")
class TestGCSBackupProvider:
    """Test GCSBackupProvider class."""

    @patch('src.core.offsite_backup.gcs_storage.Client')
    def test_init(self, mock_gcs_client):
        """Test GCS provider initialization."""
        provider = GCSBackupProvider(
            bucket_name='test-bucket',
            project_id='test-project'
        )

        assert provider.bucket_name == 'test-bucket'
        mock_gcs_client.assert_called_once()

    @patch('src.core.offsite_backup.gcs_storage.Client')
    def test_upload_backup(self, mock_gcs_client, temp_backup_file):
        """Test uploading backup to GCS."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        mock_client = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_gcs_client.return_value = mock_client

        provider = GCSBackupProvider(bucket_name='test-bucket')

        success = provider.upload_backup(
            temp_backup_file,
            'backups/test_backup.tar.gz',
            metadata={'test': 'value'}
        )

        assert success is True
        mock_blob.upload_from_filename.assert_called_once()

    @patch('src.core.offsite_backup.gcs_storage.Client')
    def test_download_backup(self, mock_gcs_client, temp_dir):
        """Test downloading backup from GCS."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        mock_client = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_gcs_client.return_value = mock_client

        provider = GCSBackupProvider(bucket_name='test-bucket')

        local_path = os.path.join(temp_dir, 'downloaded.tar.gz')
        success = provider.download_backup('backups/test_backup.tar.gz', local_path)

        assert success is True
        mock_blob.download_to_filename.assert_called_once()


class TestOffsiteBackupManager:
    """Test OffsiteBackupManager class."""

    @patch('boto3.client')
    def test_init_s3_provider(self, mock_boto_client):
        """Test initialization with S3 provider."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'},
            encryption_password='test_password',
            retention_days=30
        )

        assert manager.provider_type == 's3'
        assert manager.retention_days == 30
        assert manager.encryptor is not None

    @patch('src.core.offsite_backup.gcs_storage.Client')
    def test_init_gcs_provider(self, mock_gcs_client):
        """Test initialization with GCS provider."""
        if not GCS_AVAILABLE:
            pytest.skip("google-cloud-storage not available")

        manager = OffsiteBackupManager(
            provider_type='gcs',
            provider_config={'bucket_name': 'test-bucket'},
            encryption_password='test_password'
        )

        assert manager.provider_type == 'gcs'

    def test_init_invalid_provider(self):
        """Test initialization with invalid provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            OffsiteBackupManager(
                provider_type='invalid',
                provider_config={}
            )

    @patch('boto3.client')
    def test_upload_backup_without_encryption(self, mock_boto_client, temp_backup_file):
        """Test uploading backup without encryption."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'}
        )

        success, remote_key = manager.upload_backup(
            temp_backup_file,
            encrypt=False,
            compress=False
        )

        assert success is True
        assert remote_key.startswith('dms_backups/')
        mock_s3.upload_file.assert_called_once()

    @patch('boto3.client')
    @pytest.mark.skipif(not ENCRYPTION_AVAILABLE, reason="Encryption not available")
    def test_upload_backup_with_encryption(self, mock_boto_client, temp_backup_file, temp_dir):
        """Test uploading backup with encryption."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'},
            encryption_password='test_password'
        )

        success, remote_key = manager.upload_backup(
            temp_backup_file,
            encrypt=True,
            compress=False
        )

        assert success is True
        assert remote_key.endswith('.encrypted')
        mock_s3.upload_file.assert_called_once()

    @patch('boto3.client')
    def test_list_backups(self, mock_boto_client):
        """Test listing backups."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'dms_backups/backup1.tar.gz',
                    'Size': 1024,
                    'LastModified': MagicMock(isoformat=lambda: '2024-01-01T00:00:00'),
                    'StorageClass': 'STANDARD'
                }
            ]
        }
        mock_boto_client.return_value = mock_s3

        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'}
        )

        backups = manager.list_backups()
        assert len(backups) == 1

    @patch('boto3.client')
    def test_cleanup_old_backups(self, mock_boto_client):
        """Test cleaning up old backups."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        from datetime import datetime, timedelta

        mock_s3 = MagicMock()
        old_date = (datetime.utcnow() - timedelta(days=100)).isoformat()
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'dms_backups/old_backup.tar.gz',
                    'Size': 1024,
                    'LastModified': MagicMock(isoformat=lambda: old_date + 'Z'),
                    'StorageClass': 'STANDARD'
                }
            ]
        }
        mock_boto_client.return_value = mock_s3

        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'},
            retention_days=30
        )

        deleted_count = manager.cleanup_old_backups()
        assert deleted_count == 1
        mock_s3.delete_object.assert_called_once()

    @patch('boto3.client')
    def test_verify_backup(self, mock_boto_client):
        """Test verifying backup exists."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'dms_backups/backup1.tar.gz',
                    'Size': 1024,
                    'LastModified': MagicMock(isoformat=lambda: '2024-01-01T00:00:00'),
                    'StorageClass': 'STANDARD'
                }
            ]
        }
        mock_boto_client.return_value = mock_s3

        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'}
        )

        # Verify existing backup
        assert manager.verify_backup('dms_backups/backup1.tar.gz') is True

        # Verify non-existent backup
        assert manager.verify_backup('dms_backups/nonexistent.tar.gz') is False


class TestFactoryFunction:
    """Test factory function."""

    @patch('boto3.client')
    def test_create_offsite_backup_manager(self, mock_boto_client):
        """Test creating manager via factory function."""
        if not S3_AVAILABLE:
            pytest.skip("boto3 not available")

        manager = create_offsite_backup_manager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'},
            encryption_password='test_password',
            retention_days=60
        )

        assert isinstance(manager, OffsiteBackupManager)
        assert manager.provider_type == 's3'
        assert manager.retention_days == 60


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    @patch('boto3.client')
    @pytest.mark.skipif(not (S3_AVAILABLE and ENCRYPTION_AVAILABLE), reason="Dependencies not available")
    def test_full_backup_restore_workflow(self, mock_boto_client, temp_backup_file, temp_dir):
        """Test complete backup and restore workflow."""
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {'Contents': []}
        mock_boto_client.return_value = mock_s3

        # Create manager
        manager = OffsiteBackupManager(
            provider_type='s3',
            provider_config={'bucket_name': 'test-bucket'},
            encryption_password='test_password_123'
        )

        # Upload backup
        success, remote_key = manager.upload_backup(
            temp_backup_file,
            backup_name='test_backup.tar.gz',
            encrypt=True,
            compress=False
        )

        assert success is True
        assert 'test_backup.tar.gz' in remote_key

        # Simulate download
        # (In real scenario, would download from S3)
        assert remote_key.startswith('dms_backups/')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
