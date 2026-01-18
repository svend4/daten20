"""
Backup Encryption Module

Provides encryption and decryption for backup files.
Uses Fernet (symmetric encryption) for secure backup storage.
"""

import gzip
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger("dms.backup_encryption")


class BackupEncryption:
    """
    Backup encryption manager.

    Encrypts and decrypts backup files using Fernet symmetric encryption.
    """

    def __init__(self, key: Optional[bytes] = None, key_file: Optional[str] = None):
        """
        Initialize backup encryption.

        Args:
            key: Encryption key (32 bytes)
            key_file: Path to encryption key file

        Note:
            Requires cryptography package
        """
        try:
            from cryptography.fernet import Fernet

            self.Fernet = Fernet
        except ImportError:
            raise ImportError(
                "cryptography package required for backup encryption. " "Install with: pip install cryptography"
            )

        # Load or generate key
        if key:
            self.key = key
        elif key_file:
            self.key = self._load_key(key_file)
        else:
            # Use environment variable or generate new key
            key_str = os.getenv("BACKUP_ENCRYPTION_KEY")
            if key_str:
                self.key = key_str.encode()
            else:
                logger.warning("No encryption key provided, generating new key")
                self.key = self.generate_key()

        # Create cipher
        self.cipher = self.Fernet(self.key)

    @staticmethod
    def generate_key() -> bytes:
        """
        Generate new encryption key.

        Returns:
            32-byte encryption key
        """
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        logger.info("New encryption key generated")
        return key

    def _load_key(self, key_file: str) -> bytes:
        """
        Load encryption key from file.

        Args:
            key_file: Path to key file

        Returns:
            Encryption key

        Raises:
            FileNotFoundError: If key file not found
        """
        key_path = Path(key_file)
        if not key_path.exists():
            raise FileNotFoundError(f"Encryption key file not found: {key_file}")

        with open(key_path, "rb") as f:
            key = f.read().strip()

        logger.info(f"Encryption key loaded from {key_file}")
        return key

    def save_key(self, key_file: str):
        """
        Save encryption key to file.

        Args:
            key_file: Path to save key

        Note:
            This file should be kept secure and backed up separately
        """
        key_path = Path(key_file)
        key_path.parent.mkdir(parents=True, exist_ok=True)

        with open(key_path, "wb") as f:
            f.write(self.key)

        # Set secure permissions (owner read/write only)
        os.chmod(key_path, 0o600)

        logger.info(f"Encryption key saved to {key_file}")

    def encrypt_file(self, input_file: str, output_file: Optional[str] = None, compress: bool = True) -> str:
        """
        Encrypt file.

        Args:
            input_file: Path to file to encrypt
            output_file: Path to encrypted output (optional)
            compress: Compress before encrypting

        Returns:
            Path to encrypted file

        Raises:
            FileNotFoundError: If input file not found
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Default output path
        if not output_file:
            output_file = f"{input_file}.encrypted"

        # Read file
        with open(input_path, "rb") as f:
            data = f.read()

        # Compress if requested
        if compress:
            data = gzip.compress(data)

        # Encrypt
        encrypted_data = self.cipher.encrypt(data)

        # Write encrypted file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(encrypted_data)

        logger.info(f"File encrypted: {input_file} -> {output_file} " f"(compressed: {compress})")
        return str(output_path)

    def decrypt_file(self, input_file: str, output_file: Optional[str] = None, compressed: bool = True) -> str:
        """
        Decrypt file.

        Args:
            input_file: Path to encrypted file
            output_file: Path to decrypted output (optional)
            compressed: Whether file was compressed before encryption

        Returns:
            Path to decrypted file

        Raises:
            FileNotFoundError: If input file not found
            InvalidToken: If decryption fails (wrong key or corrupted file)
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Default output path
        if not output_file:
            if input_file.endswith(".encrypted"):
                output_file = input_file[:-10]  # Remove .encrypted
            else:
                output_file = f"{input_file}.decrypted"

        # Read encrypted file
        with open(input_path, "rb") as f:
            encrypted_data = f.read()

        # Decrypt
        try:
            data = self.cipher.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

        # Decompress if needed
        if compressed:
            try:
                data = gzip.decompress(data)
            except Exception as e:
                logger.error(f"Decompression failed: {e}")
                raise

        # Write decrypted file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(data)

        logger.info(f"File decrypted: {input_file} -> {output_file} " f"(compressed: {compressed})")
        return str(output_path)

    def encrypt_backup(self, backup_dir: str, output_file: str, metadata: Optional[dict] = None) -> str:
        """
        Create encrypted backup of directory.

        Args:
            backup_dir: Directory to backup
            output_file: Path to encrypted backup file
            metadata: Optional metadata to include

        Returns:
            Path to encrypted backup

        Raises:
            FileNotFoundError: If backup directory not found
        """
        import io
        import tarfile

        backup_path = Path(backup_dir)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

        # Create tar archive in memory
        tar_buffer = io.BytesIO()

        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            tar.add(backup_path, arcname=backup_path.name)

        tar_data = tar_buffer.getvalue()

        # Add metadata
        if metadata is None:
            metadata = {}

        metadata["backup_dir"] = str(backup_path)
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["size_bytes"] = len(tar_data)

        # Combine metadata and data
        metadata_json = json.dumps(metadata).encode()
        metadata_length = len(metadata_json).to_bytes(4, "big")

        combined_data = metadata_length + metadata_json + tar_data

        # Encrypt
        encrypted_data = self.cipher.encrypt(combined_data)

        # Write encrypted backup
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(encrypted_data)

        logger.info(f"Encrypted backup created: {backup_dir} -> {output_file} " f"({len(tar_data)} bytes)")
        return str(output_path)

    def restore_backup(self, backup_file: str, output_dir: str, verify_metadata: bool = True) -> dict:
        """
        Restore encrypted backup.

        Args:
            backup_file: Path to encrypted backup
            output_dir: Directory to restore to
            verify_metadata: Verify backup metadata

        Returns:
            Backup metadata

        Raises:
            FileNotFoundError: If backup file not found
            ValueError: If backup is invalid
        """
        import io
        import tarfile

        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        # Read encrypted backup
        with open(backup_path, "rb") as f:
            encrypted_data = f.read()

        # Decrypt
        try:
            combined_data = self.cipher.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Backup decryption failed: {e}")
            raise ValueError("Invalid backup file or wrong encryption key")

        # Extract metadata
        metadata_length = int.from_bytes(combined_data[:4], "big")
        metadata_json = combined_data[4 : 4 + metadata_length]
        tar_data = combined_data[4 + metadata_length :]

        metadata = json.loads(metadata_json.decode())

        # Verify metadata if requested
        if verify_metadata:
            if metadata.get("size_bytes") != len(tar_data):
                raise ValueError("Backup integrity check failed")

        # Extract tar archive
        tar_buffer = io.BytesIO(tar_data)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        with tarfile.open(fileobj=tar_buffer, mode="r:gz") as tar:
            # Validate and filter members before extraction (prevent path traversal)
            safe_members = []
            for member in tar.getmembers():
                # Prevent path traversal by checking if the path is within output directory
                member_path = os.path.normpath(os.path.join(output_path, member.name))
                if not member_path.startswith(str(output_path)):
                    raise ValueError(f"Unsafe path in tar file: {member.name}")
                safe_members.append(member)
            # Extract only validated members (paths verified above to prevent traversal)
            tar.extractall(output_path, members=safe_members)  # nosec B202

        logger.info(f"Backup restored: {backup_file} -> {output_dir} " f"(timestamp: {metadata.get('timestamp')})")
        return metadata


# Example usage
if __name__ == "__main__":
    import shutil
    import tempfile

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create temp directory for testing
    test_dir = Path(tempfile.mkdtemp())
    print(f"\nTest directory: {test_dir}\n")

    try:
        # Generate encryption key
        key = BackupEncryption.generate_key()
        print(f"Encryption key: {key.decode()}\n")

        # Create encryptor
        encryptor = BackupEncryption(key=key)

        # Save key for later use
        key_file = test_dir / "backup.key"
        encryptor.save_key(str(key_file))
        print(f"Key saved to: {key_file}\n")

        # Create test file
        test_file = test_dir / "test.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for backup encryption\n" * 100)

        # Encrypt file
        encrypted = encryptor.encrypt_file(str(test_file))
        print(f"File encrypted: {encrypted}")
        print(f"Encrypted size: {Path(encrypted).stat().st_size} bytes\n")

        # Decrypt file
        decrypted = encryptor.decrypt_file(encrypted)
        print(f"File decrypted: {decrypted}\n")

        # Verify content
        with open(test_file, "r") as f1:
            with open(decrypted, "r") as f2:
                if f1.read() == f2.read():
                    print("✓ File content verified\n")

        # Create backup directory
        backup_dir = test_dir / "backup_test"
        backup_dir.mkdir()
        (backup_dir / "file1.txt").write_text("File 1 content")
        (backup_dir / "file2.txt").write_text("File 2 content")
        (backup_dir / "subdir").mkdir()
        (backup_dir / "subdir" / "file3.txt").write_text("File 3 content")

        # Create encrypted backup
        backup_file = test_dir / "backup.enc"
        encryptor.encrypt_backup(str(backup_dir), str(backup_file), metadata={"description": "Test backup"})
        print(f"Backup created: {backup_file}")
        print(f"Backup size: {backup_file.stat().st_size} bytes\n")

        # Restore backup
        restore_dir = test_dir / "restored"
        metadata = encryptor.restore_backup(str(backup_file), str(restore_dir))
        print(f"Backup restored to: {restore_dir}")
        print(f"Metadata: {json.dumps(metadata, indent=2)}\n")

        # List restored files
        print("Restored files:")
        for file in sorted(restore_dir.rglob("*")):
            if file.is_file():
                print(f"  - {file.relative_to(restore_dir)}")

    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\nTest directory cleaned up")
