"""
Tests for backup encryption module.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Check if cryptography is available
try:
    from src.core.backup_encryption import BackupEncryption

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="cryptography package not installed")


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    # Cleanup
    try:
        shutil.rmtree(tmpdir)
    except:
        pass


@pytest.fixture
def encryption_key():
    """Generate encryption key for testing."""
    if ENCRYPTION_AVAILABLE:
        return BackupEncryption.generate_key()
    return None


@pytest.fixture
def encryptor(encryption_key):
    """Create encryptor instance."""
    if ENCRYPTION_AVAILABLE:
        return BackupEncryption(key=encryption_key)
    return None


class TestBackupEncryption:
    """Tests for BackupEncryption class."""

    def test_initialization_with_key(self, encryption_key):
        """Test initialization with key."""
        encryptor = BackupEncryption(key=encryption_key)
        assert encryptor.key == encryption_key
        assert encryptor.cipher is not None

    def test_initialization_with_key_file(self, temp_dir, encryption_key):
        """Test initialization with key file."""
        # Save key to file
        key_file = os.path.join(temp_dir, "test.key")
        with open(key_file, "wb") as f:
            f.write(encryption_key)

        # Initialize with key file
        encryptor = BackupEncryption(key_file=key_file)
        assert encryptor.key == encryption_key

    def test_initialization_missing_key_file(self):
        """Test initialization with missing key file."""
        with pytest.raises(FileNotFoundError):
            BackupEncryption(key_file="/nonexistent/key.file")

    def test_generate_key(self):
        """Test key generation."""
        key = BackupEncryption.generate_key()

        assert key is not None
        assert len(key) > 0
        # Fernet keys are 44 bytes (base64 encoded 32 bytes)
        assert len(key) == 44

    def test_generate_keys_are_unique(self):
        """Test that generated keys are unique."""
        keys = [BackupEncryption.generate_key() for _ in range(10)]

        # All keys should be unique
        assert len(set(keys)) == 10


class TestFileEncryption:
    """Tests for file encryption."""

    def test_encrypt_file(self, encryptor, temp_dir):
        """Test file encryption."""
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = b"This is test content for encryption"
        with open(test_file, "wb") as f:
            f.write(test_content)

        # Encrypt file
        encrypted_file = encryptor.encrypt_file(test_file)

        # Check encrypted file exists
        assert os.path.exists(encrypted_file)

        # Check encrypted content is different from original
        with open(encrypted_file, "rb") as f:
            encrypted_content = f.read()
        assert encrypted_content != test_content

    def test_encrypt_file_custom_output(self, encryptor, temp_dir):
        """Test file encryption with custom output path."""
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "wb") as f:
            f.write(b"test content")

        # Encrypt with custom output
        output_file = os.path.join(temp_dir, "custom_encrypted.bin")
        encrypted_file = encryptor.encrypt_file(test_file, output_file)

        assert encrypted_file == output_file
        assert os.path.exists(output_file)

    def test_encrypt_missing_file(self, encryptor, temp_dir):
        """Test encrypting nonexistent file."""
        with pytest.raises(FileNotFoundError):
            encryptor.encrypt_file("/nonexistent/file.txt")

    def test_encrypt_with_compression(self, encryptor, temp_dir):
        """Test encryption with compression."""
        # Create test file with repetitive content (compresses well)
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = b"A" * 10000  # Repetitive content
        with open(test_file, "wb") as f:
            f.write(test_content)

        # Encrypt with compression
        encrypted_file = encryptor.encrypt_file(test_file, compress=True)

        # Encrypted+compressed should be smaller than just encrypted
        encrypted_size = os.path.getsize(encrypted_file)
        assert encrypted_size < len(test_content)

    def test_encrypt_without_compression(self, encryptor, temp_dir):
        """Test encryption without compression."""
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = b"test content"
        with open(test_file, "wb") as f:
            f.write(test_content)

        # Encrypt without compression
        encrypted_file = encryptor.encrypt_file(test_file, compress=False)
        assert os.path.exists(encrypted_file)


class TestFileDecryption:
    """Tests for file decryption."""

    def test_decrypt_file(self, encryptor, temp_dir):
        """Test file decryption."""
        # Create and encrypt file
        test_file = os.path.join(temp_dir, "test.txt")
        original_content = b"Original content to decrypt"
        with open(test_file, "wb") as f:
            f.write(original_content)

        encrypted_file = encryptor.encrypt_file(test_file)

        # Decrypt file
        decrypted_file = encryptor.decrypt_file(encrypted_file)

        # Check decrypted content matches original
        with open(decrypted_file, "rb") as f:
            decrypted_content = f.read()
        assert decrypted_content == original_content

    def test_decrypt_file_custom_output(self, encryptor, temp_dir):
        """Test file decryption with custom output path."""
        # Create and encrypt file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "wb") as f:
            f.write(b"test")

        encrypted_file = encryptor.encrypt_file(test_file)

        # Decrypt with custom output
        output_file = os.path.join(temp_dir, "custom_decrypted.txt")
        decrypted_file = encryptor.decrypt_file(encrypted_file, output_file)

        assert decrypted_file == output_file
        assert os.path.exists(output_file)

    def test_decrypt_missing_file(self, encryptor):
        """Test decrypting nonexistent file."""
        with pytest.raises(FileNotFoundError):
            encryptor.decrypt_file("/nonexistent/encrypted.file")

    def test_decrypt_with_wrong_key(self, temp_dir):
        """Test decryption fails with wrong key."""
        # Create and encrypt with one key
        key1 = BackupEncryption.generate_key()
        encryptor1 = BackupEncryption(key=key1)

        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "wb") as f:
            f.write(b"secret content")

        encrypted_file = encryptor1.encrypt_file(test_file)

        # Try to decrypt with different key
        key2 = BackupEncryption.generate_key()
        encryptor2 = BackupEncryption(key=key2)

        with pytest.raises(Exception):  # Should raise decryption error
            encryptor2.decrypt_file(encrypted_file)

    def test_decrypt_compressed(self, encryptor, temp_dir):
        """Test decrypting compressed file."""
        # Create and encrypt with compression
        test_file = os.path.join(temp_dir, "test.txt")
        original_content = b"test content with compression"
        with open(test_file, "wb") as f:
            f.write(original_content)

        encrypted_file = encryptor.encrypt_file(test_file, compress=True)

        # Decrypt
        decrypted_file = encryptor.decrypt_file(encrypted_file, compressed=True)

        # Check content matches
        with open(decrypted_file, "rb") as f:
            decrypted_content = f.read()
        assert decrypted_content == original_content


class TestKeyManagement:
    """Tests for key management."""

    def test_save_key(self, encryptor, temp_dir):
        """Test saving encryption key to file."""
        key_file = os.path.join(temp_dir, "saved.key")

        # Save key
        encryptor.save_key(key_file)

        # Check file exists
        assert os.path.exists(key_file)

        # Check file contains key
        with open(key_file, "rb") as f:
            saved_key = f.read()
        assert saved_key.strip() == encryptor.key

    def test_save_key_permissions(self, encryptor, temp_dir):
        """Test saved key has secure permissions."""
        key_file = os.path.join(temp_dir, "saved.key")

        # Save key
        encryptor.save_key(key_file)

        # Check file permissions (owner read/write only)
        import stat

        file_stat = os.stat(key_file)
        file_mode = stat.S_IMODE(file_stat.st_mode)

        # Should be 0600 (owner read/write)
        assert file_mode == 0o600

    def test_load_key(self, temp_dir):
        """Test loading encryption key from file."""
        # Generate and save key
        key1 = BackupEncryption.generate_key()
        key_file = os.path.join(temp_dir, "test.key")

        encryptor1 = BackupEncryption(key=key1)
        encryptor1.save_key(key_file)

        # Load key in new encryptor
        encryptor2 = BackupEncryption(key_file=key_file)

        assert encryptor2.key == key1


class TestBackupDirectory:
    """Tests for directory backup."""

    def test_encrypt_backup(self, encryptor, temp_dir):
        """Test encrypting directory backup."""
        # Create test directory
        backup_dir = os.path.join(temp_dir, "to_backup")
        os.makedirs(backup_dir)

        # Add some files
        with open(os.path.join(backup_dir, "file1.txt"), "w") as f:
            f.write("Content 1")
        with open(os.path.join(backup_dir, "file2.txt"), "w") as f:
            f.write("Content 2")

        # Create subdirectory
        subdir = os.path.join(backup_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file3.txt"), "w") as f:
            f.write("Content 3")

        # Create encrypted backup
        output_file = os.path.join(temp_dir, "backup.enc")
        backup_path = encryptor.encrypt_backup(backup_dir, output_file, metadata={"description": "Test backup"})

        assert os.path.exists(backup_path)
        assert os.path.getsize(backup_path) > 0

    def test_encrypt_backup_metadata(self, encryptor, temp_dir):
        """Test backup includes metadata."""
        # Create test directory
        backup_dir = os.path.join(temp_dir, "to_backup")
        os.makedirs(backup_dir)
        with open(os.path.join(backup_dir, "test.txt"), "w") as f:
            f.write("test")

        # Create backup with metadata
        output_file = os.path.join(temp_dir, "backup.enc")
        metadata = {"description": "Test backup", "version": "1.0", "custom_field": "custom_value"}

        encryptor.encrypt_backup(backup_dir, output_file, metadata=metadata)

        # Restore and check metadata
        restore_dir = os.path.join(temp_dir, "restored")
        restored_metadata = encryptor.restore_backup(output_file, restore_dir)

        assert restored_metadata["description"] == "Test backup"
        assert restored_metadata["version"] == "1.0"
        assert restored_metadata["custom_field"] == "custom_value"
        assert "timestamp" in restored_metadata
        assert "size_bytes" in restored_metadata

    def test_restore_backup(self, encryptor, temp_dir):
        """Test restoring encrypted backup."""
        # Create and backup directory
        backup_dir = os.path.join(temp_dir, "to_backup")
        os.makedirs(backup_dir)

        # Add files
        with open(os.path.join(backup_dir, "file1.txt"), "w") as f:
            f.write("Content 1")

        subdir = os.path.join(backup_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file2.txt"), "w") as f:
            f.write("Content 2")

        # Create encrypted backup
        backup_file = os.path.join(temp_dir, "backup.enc")
        encryptor.encrypt_backup(backup_dir, backup_file)

        # Restore backup
        restore_dir = os.path.join(temp_dir, "restored")
        metadata = encryptor.restore_backup(backup_file, restore_dir)

        assert metadata is not None

        # Check restored files
        restored_backup_dir = os.path.join(restore_dir, "to_backup")
        assert os.path.exists(restored_backup_dir)
        assert os.path.exists(os.path.join(restored_backup_dir, "file1.txt"))
        assert os.path.exists(os.path.join(restored_backup_dir, "subdir", "file2.txt"))

        # Check content
        with open(os.path.join(restored_backup_dir, "file1.txt"), "r") as f:
            assert f.read() == "Content 1"

    def test_restore_backup_integrity_check(self, encryptor, temp_dir):
        """Test backup integrity verification."""
        # Create backup
        backup_dir = os.path.join(temp_dir, "to_backup")
        os.makedirs(backup_dir)
        with open(os.path.join(backup_dir, "test.txt"), "w") as f:
            f.write("test")

        backup_file = os.path.join(temp_dir, "backup.enc")
        encryptor.encrypt_backup(backup_dir, backup_file)

        # Restore with integrity check
        restore_dir = os.path.join(temp_dir, "restored")
        metadata = encryptor.restore_backup(backup_file, restore_dir, verify_metadata=True)

        assert metadata is not None

    def test_backup_missing_directory(self, encryptor, temp_dir):
        """Test backup of nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            encryptor.encrypt_backup("/nonexistent/directory", os.path.join(temp_dir, "backup.enc"))


class TestRoundTripEncryption:
    """Tests for complete encrypt/decrypt cycles."""

    def test_round_trip_small_file(self, encryptor, temp_dir):
        """Test encrypt/decrypt cycle with small file."""
        # Create test file
        test_file = os.path.join(temp_dir, "small.txt")
        original_content = b"Small file content"
        with open(test_file, "wb") as f:
            f.write(original_content)

        # Encrypt
        encrypted = encryptor.encrypt_file(test_file)

        # Decrypt
        decrypted = encryptor.decrypt_file(encrypted)

        # Verify
        with open(decrypted, "rb") as f:
            assert f.read() == original_content

    def test_round_trip_large_file(self, encryptor, temp_dir):
        """Test encrypt/decrypt cycle with large file."""
        # Create large test file (1MB)
        test_file = os.path.join(temp_dir, "large.bin")
        original_content = os.urandom(1024 * 1024)
        with open(test_file, "wb") as f:
            f.write(original_content)

        # Encrypt
        encrypted = encryptor.encrypt_file(test_file)

        # Decrypt
        decrypted = encryptor.decrypt_file(encrypted)

        # Verify
        with open(decrypted, "rb") as f:
            assert f.read() == original_content

    def test_round_trip_binary_file(self, encryptor, temp_dir):
        """Test encrypt/decrypt cycle with binary file."""
        # Create binary test file
        test_file = os.path.join(temp_dir, "binary.bin")
        original_content = bytes(range(256))
        with open(test_file, "wb") as f:
            f.write(original_content)

        # Encrypt and decrypt
        encrypted = encryptor.encrypt_file(test_file)
        decrypted = encryptor.decrypt_file(encrypted)

        # Verify
        with open(decrypted, "rb") as f:
            assert f.read() == original_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
