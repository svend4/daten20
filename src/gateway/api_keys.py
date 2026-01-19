"""
API Key Management

Provides API key generation, validation, rotation, and scope-based access control.
"""

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class APIKeyStatus(str, Enum):
    """API key status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class APIKeyScope(str, Enum):
    """API key permission scopes"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    # Service-specific scopes
    SERVICES_READ = "services:read"
    SERVICES_WRITE = "services:write"
    SERVICES_DELETE = "services:delete"
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    ANALYTICS_READ = "analytics:read"
    WEBHOOKS_MANAGE = "webhooks:manage"


@dataclass
class APIKeyMetadata:
    """API key metadata"""

    name: str
    description: Optional[str] = None
    owner_id: str = ""
    owner_email: Optional[str] = None
    ip_whitelist: List[str] = field(default_factory=list)
    allowed_origins: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIKeyUsage:
    """API key usage statistics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_used_at: Optional[datetime] = None
    last_ip: Optional[str] = None
    last_endpoint: Optional[str] = None


@dataclass
class APIKey:
    """API key object"""

    key_id: str
    key_hash: str  # Hashed API key (never store plain key)
    prefix: str  # First 8 chars for identification
    status: APIKeyStatus
    scopes: Set[APIKeyScope]
    metadata: APIKeyMetadata
    usage: APIKeyUsage = field(default_factory=APIKeyUsage)

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_rotated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None
    revoked_reason: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if key is expired"""
        if self.status == APIKeyStatus.EXPIRED:
            return True

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True

        return False

    def is_valid(self) -> bool:
        """Check if key is valid for use"""
        if self.status not in [APIKeyStatus.ACTIVE]:
            return False

        if self.is_expired():
            return False

        return True

    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if key has specific scope"""
        # Admin scope grants all permissions
        if APIKeyScope.ADMIN in self.scopes:
            return True

        return scope in self.scopes

    def is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        if not self.metadata.ip_whitelist:
            return True  # No whitelist = all IPs allowed

        return ip in self.metadata.ip_whitelist

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if not self.metadata.allowed_origins:
            return True  # No restriction = all origins allowed

        return origin in self.metadata.allowed_origins


class APIKeyManager:
    """API key manager"""

    def __init__(self):
        self.keys: Dict[str, APIKey] = {}
        self.key_by_prefix: Dict[str, str] = {}  # prefix -> key_id mapping

    def generate_key(
        self,
        name: str,
        owner_id: str,
        scopes: Set[APIKeyScope],
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, APIKey]:
        """
        Generate new API key

        Args:
            name: Key name
            owner_id: Owner user ID
            scopes: Permission scopes
            description: Key description
            expires_in_days: Days until expiration (None = never)
            ip_whitelist: List of allowed IPs
            metadata: Additional metadata

        Returns:
            Tuple of (plain_key, api_key_object)

        Note:
            Plain key is only returned once during generation.
            Store it securely - it cannot be recovered later.
        """
        # Generate random API key
        plain_key = self._generate_random_key()

        # Create key ID and prefix
        key_id = secrets.token_urlsafe(16)
        prefix = plain_key[:8]

        # Hash the key
        key_hash = self._hash_key(plain_key)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            prefix=prefix,
            status=APIKeyStatus.ACTIVE,
            scopes=scopes,
            metadata=APIKeyMetadata(
                name=name,
                description=description,
                owner_id=owner_id,
                ip_whitelist=ip_whitelist or [],
                custom_data=metadata or {},
            ),
            expires_at=expires_at,
        )

        # Store key
        self.keys[key_id] = api_key
        self.key_by_prefix[prefix] = key_id

        return plain_key, api_key

    def _generate_random_key(self) -> str:
        """Generate random API key"""
        return f"dms_{secrets.token_urlsafe(32)}"

    def _hash_key(self, key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def validate_key(
        self,
        key: str,
        required_scope: Optional[APIKeyScope] = None,
        ip: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> Tuple[bool, Optional[APIKey], Optional[str]]:
        """
        Validate API key

        Args:
            key: Plain API key
            required_scope: Required scope for this operation
            ip: Client IP address
            origin: Request origin

        Returns:
            Tuple of (valid, api_key_object, error_message)
        """
        # Find key by prefix
        prefix = key[:8] if len(key) >= 8 else key
        key_id = self.key_by_prefix.get(prefix)

        if not key_id:
            return False, None, "Invalid API key"

        api_key = self.keys.get(key_id)
        if not api_key:
            return False, None, "Invalid API key"

        # Verify key hash
        key_hash = self._hash_key(key)
        if key_hash != api_key.key_hash:
            return False, None, "Invalid API key"

        # Check if key is valid
        if not api_key.is_valid():
            return False, api_key, f"API key is {api_key.status.value}"

        # Check IP whitelist
        if ip and not api_key.is_ip_allowed(ip):
            return False, api_key, "IP address not whitelisted"

        # Check origin
        if origin and not api_key.is_origin_allowed(origin):
            return False, api_key, "Origin not allowed"

        # Check required scope
        if required_scope and not api_key.has_scope(required_scope):
            return False, api_key, f"Missing required scope: {required_scope.value}"

        # Update usage
        api_key.usage.last_used_at = datetime.utcnow()
        if ip:
            api_key.usage.last_ip = ip

        return True, api_key, None

    def revoke_key(self, key_id: str, revoked_by: str, reason: Optional[str] = None) -> bool:
        """
        Revoke API key

        Args:
            key_id: Key ID to revoke
            revoked_by: User ID who revoked the key
            reason: Reason for revocation

        Returns:
            True if key was revoked
        """
        api_key = self.keys.get(key_id)
        if not api_key:
            return False

        api_key.status = APIKeyStatus.REVOKED
        api_key.revoked_at = datetime.utcnow()
        api_key.revoked_by = revoked_by
        api_key.revoked_reason = reason

        return True

    def rotate_key(self, key_id: str) -> Tuple[Optional[str], Optional[APIKey]]:
        """
        Rotate API key (generate new key with same permissions)

        Args:
            key_id: Key ID to rotate

        Returns:
            Tuple of (new_plain_key, new_api_key_object)
        """
        old_key = self.keys.get(key_id)
        if not old_key:
            return None, None

        # Generate new key with same settings
        new_plain_key, new_api_key = self.generate_key(
            name=old_key.metadata.name,
            owner_id=old_key.metadata.owner_id,
            scopes=old_key.scopes,
            description=old_key.metadata.description,
            expires_in_days=None,  # Calculate from old key
            ip_whitelist=old_key.metadata.ip_whitelist,
            metadata=old_key.metadata.custom_data,
        )

        # Copy expiration from old key
        if old_key.expires_at:
            days_remaining = (old_key.expires_at - datetime.utcnow()).days
            if days_remaining > 0:
                new_api_key.expires_at = datetime.utcnow() + timedelta(days=days_remaining)

        new_api_key.last_rotated_at = datetime.utcnow()

        # Revoke old key
        self.revoke_key(key_id, old_key.metadata.owner_id, "Key rotated")

        return new_plain_key, new_api_key

    def update_key_scopes(self, key_id: str, scopes: Set[APIKeyScope]) -> bool:
        """
        Update API key scopes

        Args:
            key_id: Key ID
            scopes: New set of scopes

        Returns:
            True if updated
        """
        api_key = self.keys.get(key_id)
        if not api_key:
            return False

        api_key.scopes = scopes
        return True

    def get_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        return self.keys.get(key_id)

    def list_keys(self, owner_id: Optional[str] = None, status: Optional[APIKeyStatus] = None) -> List[APIKey]:
        """
        List API keys

        Args:
            owner_id: Filter by owner
            status: Filter by status

        Returns:
            List of API keys
        """
        keys = list(self.keys.values())

        if owner_id:
            keys = [k for k in keys if k.metadata.owner_id == owner_id]

        if status:
            keys = [k for k in keys if k.status == status]

        return keys

    def record_usage(self, key_id: str, success: bool, endpoint: Optional[str] = None):
        """
        Record API key usage

        Args:
            key_id: Key ID
            success: Whether request was successful
            endpoint: API endpoint used
        """
        api_key = self.keys.get(key_id)
        if not api_key:
            return

        api_key.usage.total_requests += 1

        if success:
            api_key.usage.successful_requests += 1
        else:
            api_key.usage.failed_requests += 1

        if endpoint:
            api_key.usage.last_endpoint = endpoint

    def cleanup_expired_keys(self):
        """Mark expired keys as expired"""
        now = datetime.utcnow()

        for api_key in self.keys.values():
            if api_key.expires_at and now > api_key.expires_at:
                if api_key.status == APIKeyStatus.ACTIVE:
                    api_key.status = APIKeyStatus.EXPIRED


# Global API key manager instance
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """Get global API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def create_api_key(name: str, owner_id: str, scopes: List[str], **kwargs) -> Tuple[str, APIKey]:
    """
    Create new API key

    Args:
        name: Key name
        owner_id: Owner user ID
        scopes: List of scope strings
        **kwargs: Additional arguments for generate_key

    Returns:
        Tuple of (plain_key, api_key_object)
    """
    manager = get_api_key_manager()

    # Convert scope strings to enums
    scope_set = {APIKeyScope(s) for s in scopes}

    return manager.generate_key(name=name, owner_id=owner_id, scopes=scope_set, **kwargs)


def validate_api_key(
    key: str, required_scope: Optional[str] = None, **kwargs
) -> Tuple[bool, Optional[APIKey], Optional[str]]:
    """
    Validate API key

    Args:
        key: Plain API key
        required_scope: Required scope string
        **kwargs: Additional arguments for validate_key

    Returns:
        Tuple of (valid, api_key_object, error_message)
    """
    manager = get_api_key_manager()

    scope = APIKeyScope(required_scope) if required_scope else None

    return manager.validate_key(key, scope, **kwargs)
