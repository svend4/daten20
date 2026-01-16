"""
IoT Security & Authentication

Device authentication, X.509 certificate management, pre-shared keys,
access control, firmware signing, and encryption.

Part of v3.6 IoT & Edge Computing implementation.
"""

import hashlib
import hmac
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods."""

    X509_CERTIFICATE = "x509"
    PSK = "psk"  # Pre-shared key
    JWT_TOKEN = "jwt"
    API_KEY = "api_key"
    NONE = "none"


class AccessLevel(Enum):
    """Device access levels."""

    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


@dataclass
class Certificate:
    """X.509 certificate."""

    cert_id: str
    common_name: str
    device_id: str
    public_key: str
    fingerprint: str
    issuer: str = "IoT CA"
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if certificate is valid."""
        if self.revoked:
            return False

        if self.expires_at and datetime.now() > self.expires_at:
            return False

        return True


@dataclass
class PreSharedKey:
    """Pre-shared key for device authentication."""

    key_id: str
    device_id: str
    key_value: str  # Hashed key
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    enabled: bool = True


@dataclass
class DeviceCredentials:
    """Device authentication credentials."""

    device_id: str
    auth_method: AuthMethod
    credentials: Any  # Certificate, PSK, or token
    access_level: AccessLevel = AccessLevel.READ_WRITE
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None


@dataclass
class AccessControlEntry:
    """Access control list entry."""

    ace_id: str
    device_id: str
    resource: str  # topic, endpoint, register, etc.
    permissions: Set[str] = field(default_factory=set)  # read, write, delete
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FirmwareSignature:
    """Firmware signature for secure boot."""

    firmware_version: str
    signature: str
    algorithm: str = "sha256"
    public_key_id: str = ""
    signed_at: datetime = field(default_factory=datetime.now)


class DeviceAuthenticator:
    """Device authentication manager."""

    def __init__(self):
        self.credentials: Dict[str, DeviceCredentials] = {}
        self.authenticated_devices: Set[str] = set()

    def register_credentials(
        self,
        device_id: str,
        auth_method: AuthMethod,
        credentials: Any,
        access_level: AccessLevel = AccessLevel.READ_WRITE,
    ):
        """Register device credentials."""
        device_creds = DeviceCredentials(
            device_id=device_id, auth_method=auth_method, credentials=credentials, access_level=access_level
        )

        self.credentials[device_id] = device_creds

        logger.info(f"Registered credentials for device {device_id} ({auth_method.value})")

    async def authenticate(self, device_id: str, credentials: Any) -> bool:
        """Authenticate device."""
        device_creds = self.credentials.get(device_id)

        if not device_creds:
            logger.warning(f"No credentials found for device {device_id}")
            return False

        # Authenticate based on method
        if device_creds.auth_method == AuthMethod.X509_CERTIFICATE:
            success = self._authenticate_x509(device_creds.credentials, credentials)

        elif device_creds.auth_method == AuthMethod.PSK:
            success = self._authenticate_psk(device_creds.credentials, credentials)

        elif device_creds.auth_method == AuthMethod.JWT_TOKEN:
            success = self._authenticate_jwt(device_creds.credentials, credentials)

        elif device_creds.auth_method == AuthMethod.API_KEY:
            success = self._authenticate_api_key(device_creds.credentials, credentials)

        else:
            success = False

        if success:
            self.authenticated_devices.add(device_id)
            device_creds.last_used = datetime.now()
            logger.info(f"Device {device_id} authenticated successfully")

        return success

    def _authenticate_x509(self, stored_cert: Certificate, provided_cert: Certificate) -> bool:
        """Authenticate using X.509 certificate."""
        if not stored_cert.is_valid():
            logger.warning("Certificate is invalid or revoked")
            return False

        # Compare fingerprints
        return stored_cert.fingerprint == provided_cert.fingerprint

    def _authenticate_psk(self, stored_psk: PreSharedKey, provided_key: str) -> bool:
        """Authenticate using pre-shared key."""
        if not stored_psk.enabled:
            return False

        # Check expiry
        if stored_psk.expires_at and datetime.now() > stored_psk.expires_at:
            return False

        # Compare hashed keys
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return stored_psk.key_value == provided_hash

    def _authenticate_jwt(self, stored_token: str, provided_token: str) -> bool:
        """Authenticate using JWT token."""
        # Simplified JWT validation
        return stored_token == provided_token

    def _authenticate_api_key(self, stored_key: str, provided_key: str) -> bool:
        """Authenticate using API key."""
        return hmac.compare_digest(stored_key, provided_key)

    def is_authenticated(self, device_id: str) -> bool:
        """Check if device is authenticated."""
        return device_id in self.authenticated_devices

    def revoke_authentication(self, device_id: str):
        """Revoke device authentication."""
        self.authenticated_devices.discard(device_id)
        logger.info(f"Revoked authentication for device {device_id}")


class CertificateManager:
    """X.509 certificate management."""

    def __init__(self):
        self.certificates: Dict[str, Certificate] = {}
        self.ca_public_key = "CA_PUBLIC_KEY"  # Mock CA key

    def issue_certificate(self, device_id: str, common_name: str, validity_days: int = 365) -> Certificate:
        """Issue new certificate for device."""
        # Generate certificate (mock)
        cert_id = str(uuid4())
        public_key = f"PUBLIC_KEY_{device_id}"
        fingerprint = hashlib.sha256(public_key.encode()).hexdigest()

        cert = Certificate(
            cert_id=cert_id,
            common_name=common_name,
            device_id=device_id,
            public_key=public_key,
            fingerprint=fingerprint,
            expires_at=datetime.now() + timedelta(days=validity_days),
        )

        self.certificates[cert_id] = cert

        logger.info(f"Issued certificate {cert_id} for device {device_id}")
        return cert

    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        """Get certificate by ID."""
        return self.certificates.get(cert_id)

    def revoke_certificate(self, cert_id: str) -> bool:
        """Revoke certificate."""
        cert = self.certificates.get(cert_id)

        if cert:
            cert.revoked = True
            cert.revoked_at = datetime.now()
            logger.info(f"Revoked certificate {cert_id}")
            return True

        return False

    def verify_certificate(self, cert: Certificate) -> bool:
        """Verify certificate validity and signature."""
        if not cert.is_valid():
            return False

        # Verify signature (mock)
        # In production, would verify against CA public key
        return True

    def rotate_certificate(self, old_cert_id: str, validity_days: int = 365) -> Optional[Certificate]:
        """Rotate certificate (issue new, revoke old)."""
        old_cert = self.certificates.get(old_cert_id)

        if not old_cert:
            return None

        # Issue new certificate
        new_cert = self.issue_certificate(
            device_id=old_cert.device_id, common_name=old_cert.common_name, validity_days=validity_days
        )

        # Revoke old certificate
        self.revoke_certificate(old_cert_id)

        logger.info(f"Rotated certificate for device {old_cert.device_id}")
        return new_cert


class PSKManager:
    """Pre-shared key management."""

    def __init__(self):
        self.keys: Dict[str, PreSharedKey] = {}

    def generate_psk(self, device_id: str, validity_days: Optional[int] = None) -> PreSharedKey:
        """Generate pre-shared key for device."""
        # Generate random key
        key_value = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key_value.encode()).hexdigest()

        key_id = str(uuid4())

        expires_at = None
        if validity_days:
            expires_at = datetime.now() + timedelta(days=validity_days)

        psk = PreSharedKey(key_id=key_id, device_id=device_id, key_value=key_hash, expires_at=expires_at)

        self.keys[key_id] = psk

        logger.info(f"Generated PSK for device {device_id}")

        # Return unhashed key (only time it's available)
        psk.key_value = key_value
        return psk

    def get_psk(self, key_id: str) -> Optional[PreSharedKey]:
        """Get PSK by ID."""
        return self.keys.get(key_id)

    def revoke_psk(self, key_id: str) -> bool:
        """Revoke PSK."""
        psk = self.keys.get(key_id)

        if psk:
            psk.enabled = False
            logger.info(f"Revoked PSK {key_id}")
            return True

        return False

    def rotate_psk(self, old_key_id: str) -> Optional[PreSharedKey]:
        """Rotate PSK (generate new, revoke old)."""
        old_psk = self.keys.get(old_key_id)

        if not old_psk:
            return None

        # Generate new PSK
        new_psk = self.generate_psk(old_psk.device_id)

        # Revoke old PSK
        self.revoke_psk(old_key_id)

        logger.info(f"Rotated PSK for device {old_psk.device_id}")
        return new_psk


class AccessControl:
    """Device-level access control."""

    def __init__(self):
        self.acl: Dict[str, List[AccessControlEntry]] = {}

    def add_rule(self, device_id: str, resource: str, permissions: Set[str]) -> AccessControlEntry:
        """Add access control rule."""
        ace_id = str(uuid4())

        ace = AccessControlEntry(ace_id=ace_id, device_id=device_id, resource=resource, permissions=permissions)

        if device_id not in self.acl:
            self.acl[device_id] = []

        self.acl[device_id].append(ace)

        logger.info(f"Added ACL rule for device {device_id}: {resource} -> {permissions}")
        return ace

    def check_permission(self, device_id: str, resource: str, permission: str) -> bool:
        """Check if device has permission for resource."""
        device_rules = self.acl.get(device_id, [])

        for ace in device_rules:
            if not ace.enabled:
                continue

            # Check exact match or wildcard
            if ace.resource == resource or ace.resource == "*":
                if permission in ace.permissions or "*" in ace.permissions:
                    return True

        return False

    def remove_rule(self, ace_id: str) -> bool:
        """Remove access control rule."""
        for device_id, rules in self.acl.items():
            for i, ace in enumerate(rules):
                if ace.ace_id == ace_id:
                    rules.pop(i)
                    logger.info(f"Removed ACL rule {ace_id}")
                    return True

        return False


class SecureBoot:
    """Firmware signature verification for secure boot."""

    def __init__(self):
        self.signatures: Dict[str, FirmwareSignature] = {}
        self.public_keys: Dict[str, str] = {}

    def register_public_key(self, key_id: str, public_key: str):
        """Register public key for signature verification."""
        self.public_keys[key_id] = public_key
        logger.info(f"Registered public key {key_id}")

    def sign_firmware(self, firmware_version: str, firmware_data: bytes, private_key_id: str) -> FirmwareSignature:
        """Sign firmware for secure boot."""
        # Calculate signature (mock)
        signature = hashlib.sha256(firmware_data).hexdigest()

        firmware_sig = FirmwareSignature(
            firmware_version=firmware_version, signature=signature, public_key_id=private_key_id
        )

        self.signatures[firmware_version] = firmware_sig

        logger.info(f"Signed firmware {firmware_version}")
        return firmware_sig

    def verify_firmware(self, firmware_version: str, firmware_data: bytes) -> bool:
        """Verify firmware signature."""
        signature = self.signatures.get(firmware_version)

        if not signature:
            logger.error(f"No signature found for firmware {firmware_version}")
            return False

        # Verify signature (mock)
        calculated_signature = hashlib.sha256(firmware_data).hexdigest()

        if calculated_signature != signature.signature:
            logger.error("Firmware signature verification failed")
            return False

        logger.info(f"Firmware {firmware_version} signature verified")
        return True


class EncryptionManager:
    """Data encryption for IoT communications."""

    def __init__(self):
        self.device_keys: Dict[str, bytes] = {}

    def generate_key(self, device_id: str) -> bytes:
        """Generate encryption key for device."""
        # Generate random key
        key = secrets.token_bytes(32)  # 256-bit key

        self.device_keys[device_id] = key

        logger.info(f"Generated encryption key for device {device_id}")
        return key

    def encrypt(self, device_id: str, data: bytes) -> bytes:
        """Encrypt data for device."""
        key = self.device_keys.get(device_id)

        if not key:
            logger.error(f"No encryption key for device {device_id}")
            return data

        # Mock encryption (in production would use AES-GCM or similar)
        encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

        return encrypted

    def decrypt(self, device_id: str, encrypted_data: bytes) -> bytes:
        """Decrypt data from device."""
        key = self.device_keys.get(device_id)

        if not key:
            logger.error(f"No encryption key for device {device_id}")
            return encrypted_data

        # Mock decryption
        decrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_data)])

        return decrypted


class IoTSecurity:
    """Main IoT security service."""

    def __init__(self):
        self.authenticator = DeviceAuthenticator()
        self.cert_manager = CertificateManager()
        self.psk_manager = PSKManager()
        self.access_control = AccessControl()
        self.secure_boot = SecureBoot()
        self.encryption = EncryptionManager()

    async def authenticate_device(self, device_id: str, credentials: Any) -> bool:
        """Authenticate device."""
        return await self.authenticator.authenticate(device_id, credentials)

    def issue_certificate(self, device_id: str, common_name: str, **kwargs) -> Certificate:
        """Issue device certificate."""
        return self.cert_manager.issue_certificate(device_id, common_name, **kwargs)

    def generate_psk(self, device_id: str, **kwargs) -> PreSharedKey:
        """Generate pre-shared key."""
        return self.psk_manager.generate_psk(device_id, **kwargs)

    def add_access_rule(self, device_id: str, resource: str, permissions: Set[str]) -> AccessControlEntry:
        """Add access control rule."""
        return self.access_control.add_rule(device_id, resource, permissions)

    def check_access(self, device_id: str, resource: str, permission: str) -> bool:
        """Check device access permission."""
        # First check authentication
        if not self.authenticator.is_authenticated(device_id):
            return False

        # Then check ACL
        return self.access_control.check_permission(device_id, resource, permission)

    def sign_firmware(self, version: str, data: bytes, key_id: str) -> FirmwareSignature:
        """Sign firmware."""
        return self.secure_boot.sign_firmware(version, data, key_id)

    def verify_firmware(self, version: str, data: bytes) -> bool:
        """Verify firmware signature."""
        return self.secure_boot.verify_firmware(version, data)


# Singleton instance
_iot_security: Optional[IoTSecurity] = None


def get_iot_security() -> IoTSecurity:
    """Get or create IoT security service."""
    global _iot_security

    if _iot_security is None:
        _iot_security = IoTSecurity()

    return _iot_security
