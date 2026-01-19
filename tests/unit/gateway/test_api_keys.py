"""
Unit tests for API Key Management System.

This module contains comprehensive unit tests for the API key management system,
including key generation, validation, rotation, and usage tracking.

Author: DMS Team
Date: 2026-01-18
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.gateway.api_keys import (
    APIKey,
    APIKeyStatus,
    APIKeyScope,
    APIKeyMetadata,
    APIKeyUsage,
    APIKeyManager,
    get_api_key_manager,
    create_api_key,
    validate_api_key
)


# ==================== FIXTURES ====================

@pytest.fixture
def api_key_manager():
    """Create fresh API key manager for each test."""
    return APIKeyManager()


@pytest.fixture
def sample_key_data():
    """Sample data for creating API keys."""
    return {
        'name': 'Test API Key',
        'owner_id': 'user_123',
        'scopes': {APIKeyScope.READ, APIKeyScope.WRITE},
        'description': 'Test key for unit testing',
        'ip_whitelist': ['192.168.1.1']
    }


@pytest.fixture
def created_key(api_key_manager, sample_key_data):
    """Create a sample API key for testing."""
    plain_key, api_key = api_key_manager.generate_key(**sample_key_data)
    return plain_key, api_key


# ==================== TEST DATA CLASSES ====================

class TestAPIKeyMetadata:
    """Test APIKeyMetadata data class."""

    def test_metadata_creation(self):
        """Test creating metadata."""
        metadata = APIKeyMetadata(
            name="Test Key",
            description="Test description",
            owner_id="user_123",
            ip_whitelist=["192.168.1.1"],
            tags=["test", "dev"]
        )

        assert metadata.name == "Test Key"
        assert metadata.description == "Test description"
        assert metadata.owner_id == "user_123"
        assert len(metadata.ip_whitelist) == 1
        assert len(metadata.tags) == 2

    def test_metadata_defaults(self):
        """Test metadata default values."""
        metadata = APIKeyMetadata(name="Test", owner_id="user_123")

        assert metadata.description is None
        assert metadata.ip_whitelist == []
        assert metadata.allowed_origins == []
        assert metadata.tags == []
        assert metadata.custom_data == {}


class TestAPIKeyUsage:
    """Test APIKeyUsage data class."""

    def test_usage_creation(self):
        """Test creating usage object."""
        usage = APIKeyUsage()

        assert usage.total_requests == 0
        assert usage.successful_requests == 0
        assert usage.failed_requests == 0
        assert usage.last_used_at is None

    def test_usage_tracking(self):
        """Test usage tracking."""
        usage = APIKeyUsage()
        usage.total_requests = 10
        usage.successful_requests = 8
        usage.failed_requests = 2
        usage.last_used_at = datetime.utcnow()

        assert usage.total_requests == 10
        assert usage.successful_requests == 8
        assert usage.failed_requests == 2
        assert usage.last_used_at is not None


class TestAPIKey:
    """Test APIKey data class."""

    def test_key_creation(self, created_key):
        """Test creating API key."""
        plain_key, api_key = created_key

        assert api_key.key_id is not None
        assert api_key.prefix == plain_key[:8]
        assert api_key.status == APIKeyStatus.ACTIVE
        assert APIKeyScope.READ in api_key.scopes
        assert APIKeyScope.WRITE in api_key.scopes

    def test_is_valid_active_key(self, created_key):
        """Test valid active key."""
        _, api_key = created_key
        assert api_key.is_valid() is True

    def test_is_valid_revoked_key(self, created_key):
        """Test revoked key is invalid."""
        _, api_key = created_key
        api_key.status = APIKeyStatus.REVOKED
        assert api_key.is_valid() is False

    def test_is_expired_with_expiration(self, created_key):
        """Test expired key detection."""
        _, api_key = created_key
        api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        assert api_key.is_expired() is True

    def test_is_not_expired(self, created_key):
        """Test non-expired key."""
        _, api_key = created_key
        api_key.expires_at = datetime.utcnow() + timedelta(days=30)
        assert api_key.is_expired() is False

    def test_has_scope_direct(self, created_key):
        """Test direct scope check."""
        _, api_key = created_key
        assert api_key.has_scope(APIKeyScope.READ) is True
        assert api_key.has_scope(APIKeyScope.WRITE) is True
        assert api_key.has_scope(APIKeyScope.DELETE) is False

    def test_has_scope_admin(self, created_key):
        """Test admin scope grants all permissions."""
        _, api_key = created_key
        api_key.scopes = {APIKeyScope.ADMIN}

        assert api_key.has_scope(APIKeyScope.READ) is True
        assert api_key.has_scope(APIKeyScope.WRITE) is True
        assert api_key.has_scope(APIKeyScope.DELETE) is True

    def test_is_ip_allowed_no_whitelist(self, created_key):
        """Test IP check with no whitelist (all allowed)."""
        _, api_key = created_key
        api_key.metadata.ip_whitelist = []

        assert api_key.is_ip_allowed("1.2.3.4") is True
        assert api_key.is_ip_allowed("192.168.1.1") is True

    def test_is_ip_allowed_with_whitelist(self, created_key):
        """Test IP check with whitelist."""
        _, api_key = created_key
        api_key.metadata.ip_whitelist = ["192.168.1.1", "10.0.0.1"]

        assert api_key.is_ip_allowed("192.168.1.1") is True
        assert api_key.is_ip_allowed("10.0.0.1") is True
        assert api_key.is_ip_allowed("1.2.3.4") is False

    def test_is_origin_allowed_no_restriction(self, created_key):
        """Test origin check with no restrictions."""
        _, api_key = created_key
        api_key.metadata.allowed_origins = []

        assert api_key.is_origin_allowed("https://example.com") is True
        assert api_key.is_origin_allowed("http://localhost") is True

    def test_is_origin_allowed_with_restriction(self, created_key):
        """Test origin check with restrictions."""
        _, api_key = created_key
        api_key.metadata.allowed_origins = ["https://app.example.com"]

        assert api_key.is_origin_allowed("https://app.example.com") is True
        assert api_key.is_origin_allowed("https://other.com") is False


# ==================== TEST API KEY MANAGER ====================

class TestAPIKeyManager:
    """Test APIKeyManager class."""

    def test_manager_initialization(self, api_key_manager):
        """Test manager initialization."""
        assert api_key_manager is not None
        assert len(api_key_manager.keys) == 0
        assert len(api_key_manager.key_by_prefix) == 0

    def test_generate_key(self, api_key_manager, sample_key_data):
        """Test key generation."""
        plain_key, api_key = api_key_manager.generate_key(**sample_key_data)

        # Check plain key format
        assert plain_key.startswith("dms_")
        assert len(plain_key) > 40

        # Check API key object
        assert api_key.key_id in api_key_manager.keys
        assert api_key.prefix in api_key_manager.key_by_prefix
        assert api_key.status == APIKeyStatus.ACTIVE

    def test_generate_key_with_expiration(self, api_key_manager, sample_key_data):
        """Test key generation with expiration."""
        sample_key_data['expires_in_days'] = 30
        plain_key, api_key = api_key_manager.generate_key(**sample_key_data)

        assert api_key.expires_at is not None
        assert api_key.expires_at > datetime.utcnow()
        days_diff = (api_key.expires_at - datetime.utcnow()).days
        assert 29 <= days_diff <= 30

    def test_hash_key_consistency(self, api_key_manager):
        """Test key hashing is consistent."""
        key = "test_key_123"
        hash1 = api_key_manager._hash_key(key)
        hash2 = api_key_manager._hash_key(key)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex = 64 chars

    def test_validate_key_success(self, api_key_manager, created_key):
        """Test successful key validation."""
        plain_key, _ = created_key

        valid, api_key, error = api_key_manager.validate_key(plain_key)

        assert valid is True
        assert api_key is not None
        assert error is None

    def test_validate_key_invalid(self, api_key_manager):
        """Test validation of invalid key."""
        valid, api_key, error = api_key_manager.validate_key("dms_invalid_key")

        assert valid is False
        assert api_key is None
        assert "Invalid" in error

    def test_validate_key_wrong_hash(self, api_key_manager, created_key):
        """Test validation with wrong key."""
        plain_key, api_key_obj = created_key

        # Modify the key slightly
        wrong_key = plain_key[:-1] + "x"

        valid, api_key, error = api_key_manager.validate_key(wrong_key)

        assert valid is False
        assert "Invalid" in error

    def test_validate_key_revoked(self, api_key_manager, created_key):
        """Test validation of revoked key."""
        plain_key, api_key = created_key
        api_key.status = APIKeyStatus.REVOKED

        valid, key, error = api_key_manager.validate_key(plain_key)

        assert valid is False
        assert "revoked" in error.lower()

    def test_validate_key_expired(self, api_key_manager, created_key):
        """Test validation of expired key."""
        plain_key, api_key = created_key
        api_key.expires_at = datetime.utcnow() - timedelta(days=1)

        valid, key, error = api_key_manager.validate_key(plain_key)

        assert valid is False

    def test_validate_key_with_scope(self, api_key_manager, created_key):
        """Test validation with required scope."""
        plain_key, _ = created_key

        # Should pass with READ scope
        valid, _, _ = api_key_manager.validate_key(
            plain_key,
            required_scope=APIKeyScope.READ
        )
        assert valid is True

        # Should fail with DELETE scope
        valid, _, error = api_key_manager.validate_key(
            plain_key,
            required_scope=APIKeyScope.DELETE
        )
        assert valid is False
        assert "scope" in error.lower()

    def test_validate_key_ip_whitelist(self, api_key_manager, created_key):
        """Test validation with IP whitelist."""
        plain_key, _ = created_key

        # Should pass with whitelisted IP
        valid, _, _ = api_key_manager.validate_key(
            plain_key,
            ip="192.168.1.1"
        )
        assert valid is True

        # Should fail with non-whitelisted IP
        valid, _, error = api_key_manager.validate_key(
            plain_key,
            ip="1.2.3.4"
        )
        assert valid is False
        assert "IP" in error

    def test_validate_key_origin(self, api_key_manager, sample_key_data):
        """Test validation with origin restriction."""
        sample_key_data['owner_id'] = 'user_456'
        plain_key, api_key = api_key_manager.generate_key(**sample_key_data)
        api_key.metadata.allowed_origins = ["https://app.example.com"]

        # Should pass with allowed origin
        valid, _, _ = api_key_manager.validate_key(
            plain_key,
            origin="https://app.example.com"
        )
        assert valid is True

        # Should fail with disallowed origin
        valid, _, error = api_key_manager.validate_key(
            plain_key,
            origin="https://evil.com"
        )
        assert valid is False
        assert "origin" in error.lower()

    def test_validate_key_updates_usage(self, api_key_manager, created_key):
        """Test that validation updates usage."""
        plain_key, api_key = created_key

        assert api_key.usage.last_used_at is None

        api_key_manager.validate_key(plain_key, ip="192.168.1.1")

        assert api_key.usage.last_used_at is not None
        assert api_key.usage.last_ip == "192.168.1.1"

    def test_revoke_key(self, api_key_manager, created_key):
        """Test key revocation."""
        _, api_key = created_key

        success = api_key_manager.revoke_key(
            api_key.key_id,
            revoked_by="admin",
            reason="Security incident"
        )

        assert success is True
        assert api_key.status == APIKeyStatus.REVOKED
        assert api_key.revoked_at is not None
        assert api_key.revoked_by == "admin"
        assert api_key.revoked_reason == "Security incident"

    def test_revoke_nonexistent_key(self, api_key_manager):
        """Test revoking non-existent key."""
        success = api_key_manager.revoke_key("nonexistent", "admin")
        assert success is False

    def test_rotate_key(self, api_key_manager, created_key):
        """Test key rotation."""
        old_plain_key, old_api_key = created_key
        old_key_id = old_api_key.key_id

        new_plain_key, new_api_key = api_key_manager.rotate_key(old_key_id)

        # Check new key
        assert new_plain_key is not None
        assert new_api_key is not None
        assert new_api_key.key_id != old_key_id
        assert new_api_key.status == APIKeyStatus.ACTIVE

        # Check same permissions
        assert new_api_key.scopes == old_api_key.scopes
        assert new_api_key.metadata.name == old_api_key.metadata.name
        assert new_api_key.metadata.owner_id == old_api_key.metadata.owner_id

        # Check old key revoked
        assert old_api_key.status == APIKeyStatus.REVOKED
        assert "rotated" in old_api_key.revoked_reason.lower()

        # Check new key works
        valid, _, _ = api_key_manager.validate_key(new_plain_key)
        assert valid is True

        # Check old key doesn't work
        valid, _, _ = api_key_manager.validate_key(old_plain_key)
        assert valid is False

    def test_rotate_nonexistent_key(self, api_key_manager):
        """Test rotating non-existent key."""
        new_key, new_api_key = api_key_manager.rotate_key("nonexistent")

        assert new_key is None
        assert new_api_key is None

    def test_update_key_scopes(self, api_key_manager, created_key):
        """Test updating key scopes."""
        _, api_key = created_key

        new_scopes = {APIKeyScope.READ, APIKeyScope.ADMIN}
        success = api_key_manager.update_key_scopes(api_key.key_id, new_scopes)

        assert success is True
        assert api_key.scopes == new_scopes

    def test_update_scopes_nonexistent_key(self, api_key_manager):
        """Test updating scopes of non-existent key."""
        success = api_key_manager.update_key_scopes(
            "nonexistent",
            {APIKeyScope.READ}
        )
        assert success is False

    def test_get_key(self, api_key_manager, created_key):
        """Test getting key by ID."""
        _, api_key = created_key

        retrieved = api_key_manager.get_key(api_key.key_id)

        assert retrieved is not None
        assert retrieved.key_id == api_key.key_id

    def test_get_nonexistent_key(self, api_key_manager):
        """Test getting non-existent key."""
        key = api_key_manager.get_key("nonexistent")
        assert key is None

    def test_list_keys_all(self, api_key_manager):
        """Test listing all keys."""
        # Create multiple keys
        for i in range(3):
            api_key_manager.generate_key(
                name=f"Key {i}",
                owner_id=f"user_{i}",
                scopes={APIKeyScope.READ}
            )

        keys = api_key_manager.list_keys()
        assert len(keys) == 3

    def test_list_keys_by_owner(self, api_key_manager):
        """Test listing keys by owner."""
        # Create keys for different owners
        api_key_manager.generate_key(
            name="Key 1",
            owner_id="user_1",
            scopes={APIKeyScope.READ}
        )
        api_key_manager.generate_key(
            name="Key 2",
            owner_id="user_2",
            scopes={APIKeyScope.READ}
        )
        api_key_manager.generate_key(
            name="Key 3",
            owner_id="user_1",
            scopes={APIKeyScope.READ}
        )

        user1_keys = api_key_manager.list_keys(owner_id="user_1")
        assert len(user1_keys) == 2

    def test_list_keys_by_status(self, api_key_manager):
        """Test listing keys by status."""
        # Create keys
        _, key1 = api_key_manager.generate_key(
            name="Key 1",
            owner_id="user_1",
            scopes={APIKeyScope.READ}
        )
        _, key2 = api_key_manager.generate_key(
            name="Key 2",
            owner_id="user_1",
            scopes={APIKeyScope.READ}
        )

        # Revoke one
        api_key_manager.revoke_key(key1.key_id, "admin")

        active_keys = api_key_manager.list_keys(status=APIKeyStatus.ACTIVE)
        assert len(active_keys) == 1

        revoked_keys = api_key_manager.list_keys(status=APIKeyStatus.REVOKED)
        assert len(revoked_keys) == 1

    def test_record_usage_success(self, api_key_manager, created_key):
        """Test recording successful usage."""
        _, api_key = created_key

        api_key_manager.record_usage(
            api_key.key_id,
            success=True,
            endpoint="/api/test"
        )

        assert api_key.usage.total_requests == 1
        assert api_key.usage.successful_requests == 1
        assert api_key.usage.failed_requests == 0
        assert api_key.usage.last_endpoint == "/api/test"

    def test_record_usage_failure(self, api_key_manager, created_key):
        """Test recording failed usage."""
        _, api_key = created_key

        api_key_manager.record_usage(api_key.key_id, success=False)

        assert api_key.usage.total_requests == 1
        assert api_key.usage.successful_requests == 0
        assert api_key.usage.failed_requests == 1

    def test_record_usage_multiple(self, api_key_manager, created_key):
        """Test recording multiple usages."""
        _, api_key = created_key

        for i in range(5):
            api_key_manager.record_usage(api_key.key_id, success=True)

        for i in range(2):
            api_key_manager.record_usage(api_key.key_id, success=False)

        assert api_key.usage.total_requests == 7
        assert api_key.usage.successful_requests == 5
        assert api_key.usage.failed_requests == 2

    def test_cleanup_expired_keys(self, api_key_manager):
        """Test cleanup of expired keys."""
        # Create expired key
        _, expired_key = api_key_manager.generate_key(
            name="Expired Key",
            owner_id="user_1",
            scopes={APIKeyScope.READ},
            expires_in_days=1
        )
        expired_key.expires_at = datetime.utcnow() - timedelta(days=1)

        # Create active key
        _, active_key = api_key_manager.generate_key(
            name="Active Key",
            owner_id="user_2",
            scopes={APIKeyScope.READ},
            expires_in_days=30
        )

        # Run cleanup
        api_key_manager.cleanup_expired_keys()

        # Check statuses
        assert expired_key.status == APIKeyStatus.EXPIRED
        assert active_key.status == APIKeyStatus.ACTIVE


# ==================== TEST CONVENIENCE FUNCTIONS ====================

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_api_key_manager(self):
        """Test getting global manager."""
        manager1 = get_api_key_manager()
        manager2 = get_api_key_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_create_api_key(self):
        """Test convenience function for creating key."""
        plain_key, api_key = create_api_key(
            name="Test Key",
            owner_id="user_123",
            scopes=["read", "write"]
        )

        assert plain_key.startswith("dms_")
        assert api_key.status == APIKeyStatus.ACTIVE
        assert APIKeyScope.READ in api_key.scopes
        assert APIKeyScope.WRITE in api_key.scopes

    def test_validate_api_key(self):
        """Test convenience function for validation."""
        plain_key, _ = create_api_key(
            name="Test Key",
            owner_id="user_123",
            scopes=["read"]
        )

        valid, api_key, error = validate_api_key(plain_key, required_scope="read")

        assert valid is True
        assert api_key is not None
        assert error is None


# ==================== TEST EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_scopes(self, api_key_manager):
        """Test creating key with empty scopes."""
        plain_key, api_key = api_key_manager.generate_key(
            name="No Scopes Key",
            owner_id="user_123",
            scopes=set()  # Empty
        )

        assert api_key is not None
        assert len(api_key.scopes) == 0

    def test_multiple_rotations(self, api_key_manager, created_key):
        """Test multiple key rotations."""
        _, original_key = created_key
        key_id = original_key.key_id

        # Rotate 3 times
        for i in range(3):
            new_key, new_api_key = api_key_manager.rotate_key(key_id)
            assert new_key is not None
            key_id = new_api_key.key_id

        # Original key should be revoked
        assert original_key.status == APIKeyStatus.REVOKED

    def test_validation_without_ip_or_origin(self, api_key_manager, created_key):
        """Test validation without IP or origin checks."""
        plain_key, _ = created_key

        valid, _, _ = api_key_manager.validate_key(
            plain_key,
            ip=None,
            origin=None
        )

        assert valid is True

    def test_key_with_all_scopes(self, api_key_manager):
        """Test key with all available scopes."""
        all_scopes = {
            APIKeyScope.READ,
            APIKeyScope.WRITE,
            APIKeyScope.DELETE,
            APIKeyScope.ADMIN,
            APIKeyScope.SERVICES_READ,
            APIKeyScope.SERVICES_WRITE
        }

        plain_key, api_key = api_key_manager.generate_key(
            name="Super Key",
            owner_id="admin",
            scopes=all_scopes
        )

        assert len(api_key.scopes) == len(all_scopes)

    def test_revoke_already_revoked_key(self, api_key_manager, created_key):
        """Test revoking already revoked key."""
        _, api_key = created_key

        # Revoke once
        api_key_manager.revoke_key(api_key.key_id, "admin", "First revocation")

        # Revoke again
        success = api_key_manager.revoke_key(
            api_key.key_id,
            "admin",
            "Second revocation"
        )

        assert success is True
        # Reason should be updated
        assert "Second" in api_key.revoked_reason

    def test_long_key_names_and_descriptions(self, api_key_manager):
        """Test keys with long names and descriptions."""
        long_name = "A" * 500
        long_description = "B" * 1000

        plain_key, api_key = api_key_manager.generate_key(
            name=long_name,
            owner_id="user_123",
            scopes={APIKeyScope.READ},
            description=long_description
        )

        assert api_key.metadata.name == long_name
        assert api_key.metadata.description == long_description

    def test_special_characters_in_metadata(self, api_key_manager):
        """Test special characters in metadata."""
        plain_key, api_key = api_key_manager.generate_key(
            name="Key with émojis 🔑",
            owner_id="user_👤",
            scopes={APIKeyScope.READ},
            description="Description with <html> & special chars!",
            metadata={"field": "value with 'quotes' and \"escapes\""}
        )

        assert "émojis" in api_key.metadata.name
        assert api_key.metadata.owner_id == "user_👤"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
