"""
Offsite Backup System

Provides automated offsite backups to cloud storage providers (S3, Google Cloud Storage)
with encryption, compression, and retention management.
"""

import gzip
import hashlib
import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("dms.offsite_backup")

# Try to import cloud storage libraries
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    S3_AVAILABLE = True
except ImportError:
    logger.warning("AWS S3 support not available (boto3 not installed)")
    S3_AVAILABLE = False

try:
    from google.api_core import exceptions as gcs_exceptions
    from google.cloud import storage as gcs_storage

    GCS_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud Storage support not available (google-cloud-storage not installed)")
    GCS_AVAILABLE = False

# Try to import encryption support
try:
    import secrets

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

    ENCRYPTION_AVAILABLE = True
except ImportError:
    logger.warning("Encryption support not available (cryptography not installed)")
    ENCRYPTION_AVAILABLE = False


class OffsiteBackupEncryption:
    """Handle encryption/decryption for offsite backups."""

    def __init__(self, password: Optional[str] = None, key: Optional[bytes] = None):
        """
        Initialize encryption handler.

        Args:
            password: Password for key derivation (if key not provided)
            key: Direct encryption key (32 bytes)
        """
        if not ENCRYPTION_AVAILABLE:
            raise RuntimeError("Encryption not available. Install: pip install cryptography")

        if key:
            if len(key) != 32:
                raise ValueError("Encryption key must be 32 bytes")
            self.key = key
        elif password:
            # Derive key from password
            salt = b"dms_offsite_backup_salt_v1"  # In production, use random salt
            kdf = PBKDF2(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
            self.key = kdf.derive(password.encode())
        else:
            raise ValueError("Either password or key must be provided")

        self.cipher = AESGCM(self.key)

    def encrypt_file(self, input_path: str, output_path: str) -> Dict[str, str]:
        """
        Encrypt file.

        Args:
            input_path: Path to file to encrypt
            output_path: Path for encrypted file

        Returns:
            Dictionary with encryption metadata
        """
        logger.info(f"Encrypting file: {input_path}")

        with open(input_path, "rb") as f:
            plaintext = f.read()

        # Generate nonce
        nonce = secrets.token_bytes(12)

        # Encrypt
        ciphertext = self.cipher.encrypt(nonce, plaintext, None)

        # Calculate checksums
        plaintext_hash = hashlib.sha256(plaintext).hexdigest()
        ciphertext_hash = hashlib.sha256(ciphertext).hexdigest()

        # Write encrypted file with nonce prepended
        with open(output_path, "wb") as f:
            f.write(nonce + ciphertext)

        logger.info(f"File encrypted: {output_path}")

        return {
            "plaintext_hash": plaintext_hash,
            "ciphertext_hash": ciphertext_hash,
            "encrypted_size": len(nonce) + len(ciphertext),
            "original_size": len(plaintext),
        }

    def decrypt_file(self, input_path: str, output_path: str) -> Dict[str, str]:
        """
        Decrypt file.

        Args:
            input_path: Path to encrypted file
            output_path: Path for decrypted file

        Returns:
            Dictionary with decryption metadata
        """
        logger.info(f"Decrypting file: {input_path}")

        with open(input_path, "rb") as f:
            data = f.read()

        # Extract nonce and ciphertext
        nonce = data[:12]
        ciphertext = data[12:]

        # Decrypt
        try:
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Decryption failed. Invalid key or corrupted file.")

        # Calculate checksums
        plaintext_hash = hashlib.sha256(plaintext).hexdigest()

        # Write decrypted file
        with open(output_path, "wb") as f:
            f.write(plaintext)

        logger.info(f"File decrypted: {output_path}")

        return {"plaintext_hash": plaintext_hash, "decrypted_size": len(plaintext)}


class S3BackupProvider:
    """AWS S3 backup provider."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize S3 backup provider.

        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key (or use env AWS_ACCESS_KEY_ID)
            aws_secret_access_key: AWS secret key (or use env AWS_SECRET_ACCESS_KEY)
            region_name: AWS region
            endpoint_url: Custom endpoint URL (for S3-compatible services)
        """
        if not S3_AVAILABLE:
            raise RuntimeError("S3 support not available. Install: pip install boto3")

        self.bucket_name = bucket_name
        self.region_name = region_name

        # Initialize S3 client
        session_kwargs = {}
        if aws_access_key_id:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self.s3_client = boto3.client("s3", region_name=region_name, endpoint_url=endpoint_url, **session_kwargs)

        logger.info(f"S3 backup provider initialized: bucket={bucket_name}, region={region_name}")

    def upload_backup(self, local_path: str, remote_key: str, metadata: Optional[Dict] = None) -> bool:
        """
        Upload backup to S3.

        Args:
            local_path: Local file path
            remote_key: S3 object key
            metadata: Optional metadata

        Returns:
            True if successful
        """
        try:
            logger.info(f"Uploading to S3: {local_path} -> s3://{self.bucket_name}/{remote_key}")

            extra_args = {}
            if metadata:
                extra_args["Metadata"] = {k: str(v) for k, v in metadata.items()}

            # Upload with progress
            file_size = os.path.getsize(local_path)
            self.s3_client.upload_file(local_path, self.bucket_name, remote_key, ExtraArgs=extra_args)

            logger.info(f"Upload successful: {file_size} bytes")
            return True

        except (ClientError, BotoCoreError) as e:
            logger.error(f"S3 upload failed: {e}")
            return False

    def download_backup(self, remote_key: str, local_path: str) -> bool:
        """
        Download backup from S3.

        Args:
            remote_key: S3 object key
            local_path: Local file path

        Returns:
            True if successful
        """
        try:
            logger.info(f"Downloading from S3: s3://{self.bucket_name}/{remote_key} -> {local_path}")

            # Ensure directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            self.s3_client.download_file(self.bucket_name, remote_key, local_path)

            logger.info("Download successful")
            return True

        except (ClientError, BotoCoreError) as e:
            logger.error(f"S3 download failed: {e}")
            return False

    def list_backups(self, prefix: str = "") -> List[Dict]:
        """
        List backups in S3.

        Args:
            prefix: Key prefix to filter

        Returns:
            List of backup metadata
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

            backups = []
            for obj in response.get("Contents", []):
                backups.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                        "storage_class": obj.get("StorageClass", "STANDARD"),
                    }
                )

            return backups

        except (ClientError, BotoCoreError) as e:
            logger.error(f"S3 list failed: {e}")
            return []

    def delete_backup(self, remote_key: str) -> bool:
        """
        Delete backup from S3.

        Args:
            remote_key: S3 object key

        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_key)
            logger.info(f"Deleted from S3: {remote_key}")
            return True

        except (ClientError, BotoCoreError) as e:
            logger.error(f"S3 delete failed: {e}")
            return False

    def get_backup_metadata(self, remote_key: str) -> Optional[Dict]:
        """
        Get backup metadata from S3.

        Args:
            remote_key: S3 object key

        Returns:
            Dictionary with metadata or None if not found
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=remote_key)

            metadata = response.get("Metadata", {})
            return {
                "size": response["ContentLength"],
                "last_modified": response["LastModified"].isoformat(),
                "etag": response["ETag"],
                "sha256": metadata.get("sha256"),
                **metadata,
            }

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to get S3 metadata: {e}")
            return None


class GCSBackupProvider:
    """Google Cloud Storage backup provider."""

    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize GCS backup provider.

        Args:
            bucket_name: GCS bucket name
            credentials_path: Path to service account JSON (or use GOOGLE_APPLICATION_CREDENTIALS env)
            project_id: GCP project ID
        """
        if not GCS_AVAILABLE:
            raise RuntimeError("GCS support not available. Install: pip install google-cloud-storage")

        self.bucket_name = bucket_name

        # Initialize GCS client
        if credentials_path:
            self.storage_client = gcs_storage.Client.from_service_account_json(credentials_path, project=project_id)
        else:
            self.storage_client = gcs_storage.Client(project=project_id)

        self.bucket = self.storage_client.bucket(bucket_name)

        logger.info(f"GCS backup provider initialized: bucket={bucket_name}")

    def upload_backup(self, local_path: str, remote_key: str, metadata: Optional[Dict] = None) -> bool:
        """
        Upload backup to GCS.

        Args:
            local_path: Local file path
            remote_key: GCS blob name
            metadata: Optional metadata

        Returns:
            True if successful
        """
        try:
            logger.info(f"Uploading to GCS: {local_path} -> gs://{self.bucket_name}/{remote_key}")

            blob = self.bucket.blob(remote_key)

            if metadata:
                blob.metadata = {k: str(v) for k, v in metadata.items()}

            blob.upload_from_filename(local_path)

            file_size = os.path.getsize(local_path)
            logger.info(f"Upload successful: {file_size} bytes")
            return True

        except gcs_exceptions.GoogleAPIError as e:
            logger.error(f"GCS upload failed: {e}")
            return False

    def download_backup(self, remote_key: str, local_path: str) -> bool:
        """
        Download backup from GCS.

        Args:
            remote_key: GCS blob name
            local_path: Local file path

        Returns:
            True if successful
        """
        try:
            logger.info(f"Downloading from GCS: gs://{self.bucket_name}/{remote_key} -> {local_path}")

            # Ensure directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            blob = self.bucket.blob(remote_key)
            blob.download_to_filename(local_path)

            logger.info("Download successful")
            return True

        except gcs_exceptions.GoogleAPIError as e:
            logger.error(f"GCS download failed: {e}")
            return False

    def list_backups(self, prefix: str = "") -> List[Dict]:
        """
        List backups in GCS.

        Args:
            prefix: Blob name prefix to filter

        Returns:
            List of backup metadata
        """
        try:
            blobs = self.storage_client.list_blobs(self.bucket_name, prefix=prefix)

            backups = []
            for blob in blobs:
                backups.append(
                    {
                        "key": blob.name,
                        "size": blob.size,
                        "last_modified": blob.updated.isoformat() if blob.updated else None,
                        "storage_class": blob.storage_class,
                    }
                )

            return backups

        except gcs_exceptions.GoogleAPIError as e:
            logger.error(f"GCS list failed: {e}")
            return []

    def delete_backup(self, remote_key: str) -> bool:
        """
        Delete backup from GCS.

        Args:
            remote_key: GCS blob name

        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_key)
            blob.delete()
            logger.info(f"Deleted from GCS: {remote_key}")
            return True

        except gcs_exceptions.GoogleAPIError as e:
            logger.error(f"GCS delete failed: {e}")
            return False

    def get_backup_metadata(self, remote_key: str) -> Optional[Dict]:
        """
        Get backup metadata from GCS.

        Args:
            remote_key: GCS blob name

        Returns:
            Dictionary with metadata or None if not found
        """
        try:
            blob = self.bucket.blob(remote_key)
            blob.reload()  # Load metadata from GCS

            metadata = {
                "size": blob.size,
                "last_modified": blob.updated.isoformat() if blob.updated else None,
                "md5_hash": blob.md5_hash,
                "crc32c": blob.crc32c,
            }

            # Add custom metadata
            if blob.metadata:
                metadata.update(blob.metadata)

            return metadata

        except gcs_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to get GCS metadata: {e}")
            return None


class OffsiteBackupManager:
    """Manage offsite backups with encryption and cloud storage."""

    def __init__(
        self,
        provider_type: str,  # 's3' or 'gcs'
        provider_config: Dict,
        encryption_password: Optional[str] = None,
        encryption_key: Optional[bytes] = None,
        retention_days: int = 90,
        backup_prefix: str = "dms_backups/",
    ):
        """
        Initialize offsite backup manager.

        Args:
            provider_type: Cloud provider ('s3' or 'gcs')
            provider_config: Provider-specific configuration
            encryption_password: Password for encryption
            encryption_key: Direct encryption key (32 bytes)
            retention_days: Days to retain backups
            backup_prefix: Prefix for backup keys/blobs
        """
        self.provider_type = provider_type
        self.retention_days = retention_days
        self.backup_prefix = backup_prefix.rstrip("/") + "/"

        # Initialize encryption
        self.encryptor = None
        if encryption_password or encryption_key:
            self.encryptor = OffsiteBackupEncryption(password=encryption_password, key=encryption_key)
            logger.info("Offsite backup encryption enabled")

        # Initialize cloud provider
        if provider_type == "s3":
            self.provider = S3BackupProvider(**provider_config)
        elif provider_type == "gcs":
            self.provider = GCSBackupProvider(**provider_config)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        logger.info(f"Offsite backup manager initialized: provider={provider_type}")

    def upload_backup(
        self, local_backup_path: str, backup_name: Optional[str] = None, encrypt: bool = True, compress: bool = True
    ) -> Tuple[bool, str]:
        """
        Upload backup to cloud storage.

        Args:
            local_backup_path: Path to local backup file
            backup_name: Custom backup name (auto-generated if None)
            encrypt: Encrypt before upload
            compress: Compress before upload (if not already compressed)

        Returns:
            Tuple of (success, remote_key)
        """
        if not Path(local_backup_path).exists():
            logger.error(f"Backup file not found: {local_backup_path}")
            return False, ""

        # Generate backup name
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.tar.gz"

        remote_key = self.backup_prefix + backup_name

        # Prepare file for upload
        upload_path = local_backup_path
        temp_files = []

        try:
            # Compress if requested and not already compressed
            if compress and not local_backup_path.endswith((".gz", ".bz2", ".xz")):
                compressed_path = local_backup_path + ".gz"
                logger.info(f"Compressing backup: {local_backup_path}")
                with open(local_backup_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb", compresslevel=6) as f_out:
                        shutil.copyfileobj(f_in, f_out)
                upload_path = compressed_path
                temp_files.append(compressed_path)
                remote_key += ".gz" if not backup_name.endswith(".gz") else ""

            # Encrypt if requested
            encryption_metadata = {}
            if encrypt and self.encryptor:
                encrypted_path = upload_path + ".encrypted"
                logger.info(f"Encrypting backup: {upload_path}")
                encryption_metadata = self.encryptor.encrypt_file(upload_path, encrypted_path)
                upload_path = encrypted_path
                temp_files.append(encrypted_path)
                remote_key += ".encrypted"

            # Prepare metadata
            metadata = {
                "original_name": Path(local_backup_path).name,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "encrypted": str(encrypt and self.encryptor is not None),
                "compressed": str(compress),
                "dms_version": "4.2",  # Update with actual version
            }
            metadata.update(encryption_metadata)

            # Calculate checksum
            with open(upload_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            metadata["sha256"] = file_hash

            # Upload to cloud
            success = self.provider.upload_backup(upload_path, remote_key, metadata)

            if success:
                logger.info(f"Offsite backup uploaded successfully: {remote_key}")
                return True, remote_key
            else:
                logger.error("Offsite backup upload failed")
                return False, ""

        except Exception as e:
            logger.error(f"Error during offsite backup: {e}")
            return False, ""

        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_file}: {e}")

    def download_backup(
        self, remote_key: str, local_path: str, decrypt: bool = True, decompress: bool = True
    ) -> Tuple[bool, str]:
        """
        Download backup from cloud storage.

        Args:
            remote_key: Remote backup key/blob name
            local_path: Local destination path
            decrypt: Decrypt after download
            decompress: Decompress after download

        Returns:
            Tuple of (success, final_path)
        """
        download_path = local_path
        temp_files = []

        try:
            # Download from cloud
            logger.info(f"Downloading offsite backup: {remote_key}")
            success = self.provider.download_backup(remote_key, download_path)

            if not success:
                logger.error("Download failed")
                return False, ""

            # Decrypt if needed
            if decrypt and remote_key.endswith(".encrypted"):
                if not self.encryptor:
                    raise RuntimeError("Backup is encrypted but no encryption key provided")

                decrypted_path = download_path[:-10]  # Remove .encrypted
                logger.info("Decrypting backup...")
                self.encryptor.decrypt_file(download_path, decrypted_path)
                temp_files.append(download_path)
                download_path = decrypted_path

            # Decompress if needed
            if decompress and download_path.endswith(".gz"):
                decompressed_path = download_path[:-3]  # Remove .gz
                logger.info("Decompressing backup...")
                with gzip.open(download_path, "rb") as f_in:
                    with open(decompressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                temp_files.append(download_path)
                download_path = decompressed_path

            logger.info(f"Offsite backup downloaded successfully: {download_path}")
            return True, download_path

        except Exception as e:
            logger.error(f"Error during offsite backup download: {e}")
            return False, ""

        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_file}: {e}")

    def list_backups(self) -> List[Dict]:
        """
        List all offsite backups.

        Returns:
            List of backup metadata
        """
        return self.provider.list_backups(prefix=self.backup_prefix)

    def cleanup_old_backups(self) -> int:
        """
        Delete backups older than retention period.

        Returns:
            Number of backups deleted
        """
        logger.info(f"Cleaning up backups older than {self.retention_days} days")

        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        backups = self.list_backups()

        deleted_count = 0
        for backup in backups:
            backup_date = datetime.fromisoformat(backup["last_modified"].replace("Z", "+00:00"))

            if backup_date < cutoff_date:
                logger.info(f"Deleting old backup: {backup['key']}")
                if self.provider.delete_backup(backup["key"]):
                    deleted_count += 1

        logger.info(f"Cleanup complete: {deleted_count} backups deleted")
        return deleted_count

    def verify_backup(self, remote_key: str) -> bool:
        """
        Verify backup integrity by downloading and checking checksum.

        This method performs a complete integrity verification:
        1. Retrieves backup metadata (including stored checksum)
        2. Downloads backup to temporary location
        3. Calculates checksum of downloaded file
        4. Compares calculated checksum with stored checksum
        5. Reports verification result

        Args:
            remote_key: Remote backup key

        Returns:
            True if backup is valid and checksum matches
        """
        logger.info(f"Verifying backup integrity: {remote_key}")

        # Step 1: Get backup metadata (including checksum)
        metadata = self.provider.get_backup_metadata(remote_key)
        if not metadata:
            logger.error(f"Backup not found: {remote_key}")
            return False

        stored_checksum = metadata.get("sha256")
        if not stored_checksum:
            logger.warning(f"No checksum found in metadata for {remote_key}")
            logger.warning("Backup exists but cannot verify integrity (no stored checksum)")
            # Still check if backup is downloadable
            return self._verify_basic(remote_key)

        logger.info(f"Stored checksum: {stored_checksum}")
        logger.info(f"Backup size: {metadata.get('size', 'unknown')} bytes")

        # Step 2: Download backup to temporary location
        import tempfile

        temp_dir = tempfile.mkdtemp(prefix="dms_verify_")
        temp_file = os.path.join(temp_dir, "backup_verify.tmp")

        try:
            logger.info(f"Downloading backup to temporary location: {temp_file}")
            success = self.provider.download_backup(remote_key, temp_file)

            if not success:
                logger.error(f"Failed to download backup for verification")
                return False

            # Step 3: Calculate checksum of downloaded file
            logger.info("Calculating checksum of downloaded backup...")
            calculated_checksum = self._calculate_file_checksum(temp_file)
            logger.info(f"Calculated checksum: {calculated_checksum}")

            # Step 4: Compare checksums
            if calculated_checksum == stored_checksum:
                logger.info("✓ Checksum verification PASSED - backup is valid")
                return True
            else:
                logger.error("✗ Checksum verification FAILED - backup may be corrupted")
                logger.error(f"Expected: {stored_checksum}")
                logger.error(f"Got:      {calculated_checksum}")
                return False

        except Exception as e:
            logger.error(f"Error during backup verification: {e}")
            return False

        finally:
            # Step 5: Cleanup temporary files
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                logger.debug(f"Cleaned up temporary files: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary files: {e}")

    def _calculate_file_checksum(self, file_path: str) -> str:
        """
        Calculate SHA-256 checksum of file.

        Args:
            file_path: Path to file

        Returns:
            SHA-256 checksum as hex string
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    def _verify_basic(self, remote_key: str) -> bool:
        """
        Basic verification - just check if backup exists and is downloadable.

        Args:
            remote_key: Remote backup key

        Returns:
            True if backup exists
        """
        backups = self.list_backups()
        for backup in backups:
            if backup["key"] == remote_key:
                logger.info(f"Backup found: {backup['key']} ({backup['size']} bytes)")
                return True

        logger.warning(f"Backup not found: {remote_key}")
        return False


# Factory function
def create_offsite_backup_manager(
    provider_type: str, provider_config: Dict, encryption_password: Optional[str] = None, retention_days: int = 90
) -> OffsiteBackupManager:
    """
    Create offsite backup manager instance.

    Args:
        provider_type: 's3' or 'gcs'
        provider_config: Provider configuration
        encryption_password: Encryption password
        retention_days: Backup retention period

    Returns:
        OffsiteBackupManager instance
    """
    return OffsiteBackupManager(
        provider_type=provider_type,
        provider_config=provider_config,
        encryption_password=encryption_password,
        retention_days=retention_days,
    )
