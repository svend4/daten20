"""
Tests for API authentication module.
"""

import os
import tempfile
import time

import pytest
from flask import Flask, g

from src.core.api_auth import APIKeyManager, optional_api_key, require_api_key


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_file.close()
    yield temp_file.name
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except:
        pass


@pytest.fixture
def api_key_manager(temp_db):
    """Create API key manager with temp database."""
    return APIKeyManager(temp_db)


class TestAPIKeyGeneration:
    """Tests for API key generation."""

    def test_generate_api_key(self, api_key_manager):
        """Test API key generation."""
        key = api_key_manager.generate_api_key(name="Test Key", user_id=1)

        assert key is not None
        assert key.startswith("dms_")
        assert len(key) > 40  # Should be reasonably long

    def test_generate_key_with_permissions(self, api_key_manager):
        """Test generating key with permissions."""
        key = api_key_manager.generate_api_key(name="Admin Key", user_id=1, permissions=["read", "write", "admin"])

        assert key.startswith("dms_")

        # Validate and check permissions
        info = api_key_manager.validate_api_key(key)
        assert info is not None
        assert "read" in info["permissions"]
        assert "write" in info["permissions"]
        assert "admin" in info["permissions"]

    def test_generate_key_with_expiration(self, api_key_manager):
        """Test generating key with expiration."""
        key = api_key_manager.generate_api_key(name="Temp Key", user_id=1, expires_in_days=30)

        assert key.startswith("dms_")

        # Validate key
        info = api_key_manager.validate_api_key(key)
        assert info is not None
        assert info["expires_at"] is not None

    def test_generate_key_with_rate_limit(self, api_key_manager):
        """Test generating key with rate limit."""
        key = api_key_manager.generate_api_key(name="Limited Key", user_id=1, rate_limit=5000)

        # Validate and check rate limit
        info = api_key_manager.validate_api_key(key)
        assert info is not None
        assert info["rate_limit"] == 5000

    def test_generate_multiple_keys(self, api_key_manager):
        """Test generating multiple keys."""
        keys = []
        for i in range(5):
            key = api_key_manager.generate_api_key(name=f"Key {i}", user_id=1)
            keys.append(key)

        # All keys should be unique
        assert len(set(keys)) == 5

        # All keys should be valid
        for key in keys:
            info = api_key_manager.validate_api_key(key)
            assert info is not None


class TestAPIKeyValidation:
    """Tests for API key validation."""

    def test_validate_valid_key(self, api_key_manager):
        """Test validating valid API key."""
        key = api_key_manager.generate_api_key(name="Valid Key", user_id=1)

        info = api_key_manager.validate_api_key(key)
        assert info is not None
        assert info["user_id"] == 1
        assert info["is_active"] == 1

    def test_validate_invalid_key(self, api_key_manager):
        """Test validating invalid API key."""
        info = api_key_manager.validate_api_key("dms_invalid_key_12345")
        assert info is None

    def test_validate_wrong_prefix(self, api_key_manager):
        """Test validating key with wrong prefix."""
        info = api_key_manager.validate_api_key("wrong_prefix_key")
        assert info is None

    def test_validate_empty_key(self, api_key_manager):
        """Test validating empty key."""
        info = api_key_manager.validate_api_key("")
        assert info is None

    def test_validate_none_key(self, api_key_manager):
        """Test validating None key."""
        info = api_key_manager.validate_api_key(None)
        assert info is None

    def test_validate_expired_key(self, api_key_manager):
        """Test validating expired key."""
        # Create key that expires immediately
        key = api_key_manager.generate_api_key(name="Expired Key", user_id=1, expires_in_days=0)

        # Wait a moment
        time.sleep(0.1)

        # Key should be expired
        info = api_key_manager.validate_api_key(key)
        assert info is None

    def test_validate_inactive_key(self, api_key_manager):
        """Test validating inactive key."""
        # Generate key
        key = api_key_manager.generate_api_key(name="To Be Revoked", user_id=1)

        # Revoke key
        api_key_manager.revoke_api_key(key)

        # Key should not validate
        info = api_key_manager.validate_api_key(key)
        assert info is None

    def test_validate_updates_last_used(self, api_key_manager):
        """Test validation updates last_used_at."""
        key = api_key_manager.generate_api_key(name="Test Key", user_id=1)

        # First validation
        info1 = api_key_manager.validate_api_key(key)
        last_used_1 = info1["last_used_at"]

        # Wait a moment
        time.sleep(0.2)

        # Second validation
        info2 = api_key_manager.validate_api_key(key)
        last_used_2 = info2["last_used_at"]

        # Last used should be updated
        assert last_used_2 > last_used_1


class TestAPIKeyRevocation:
    """Tests for API key revocation."""

    def test_revoke_api_key(self, api_key_manager):
        """Test revoking API key."""
        key = api_key_manager.generate_api_key(name="To Revoke", user_id=1)

        # Key should be valid
        assert api_key_manager.validate_api_key(key) is not None

        # Revoke key
        api_key_manager.revoke_api_key(key)

        # Key should no longer be valid
        assert api_key_manager.validate_api_key(key) is None

    def test_revoke_nonexistent_key(self, api_key_manager):
        """Test revoking nonexistent key (should not error)."""
        api_key_manager.revoke_api_key("dms_nonexistent_key")
        # Should complete without error


class TestAPIKeyListing:
    """Tests for API key listing."""

    def test_list_api_keys(self, api_key_manager):
        """Test listing API keys."""
        # Create some keys
        for i in range(3):
            api_key_manager.generate_api_key(name=f"Key {i}", user_id=1)

        # List keys
        keys = api_key_manager.list_api_keys(user_id=1)

        assert len(keys) == 3
        for key in keys:
            assert "key_prefix" in key
            assert "name" in key
            assert "created_at" in key

    def test_list_keys_by_user(self, api_key_manager):
        """Test listing keys filtered by user."""
        # Create keys for different users
        api_key_manager.generate_api_key(name="User 1 Key 1", user_id=1)
        api_key_manager.generate_api_key(name="User 1 Key 2", user_id=1)
        api_key_manager.generate_api_key(name="User 2 Key", user_id=2)

        # List keys for user 1
        keys_user1 = api_key_manager.list_api_keys(user_id=1)
        assert len(keys_user1) == 2

        # List keys for user 2
        keys_user2 = api_key_manager.list_api_keys(user_id=2)
        assert len(keys_user2) == 1

    def test_list_all_keys(self, api_key_manager):
        """Test listing all keys."""
        # Create keys for different users
        api_key_manager.generate_api_key(name="Key 1", user_id=1)
        api_key_manager.generate_api_key(name="Key 2", user_id=2)

        # List all keys (no user filter)
        all_keys = api_key_manager.list_api_keys()
        assert len(all_keys) >= 2

    def test_list_excludes_revoked(self, api_key_manager):
        """Test listing excludes revoked keys."""
        # Create and revoke a key
        key = api_key_manager.generate_api_key(name="To Revoke", user_id=1)
        api_key_manager.revoke_api_key(key)

        # Create active key
        api_key_manager.generate_api_key(name="Active", user_id=1)

        # List should only show active key
        keys = api_key_manager.list_api_keys(user_id=1)
        assert len(keys) == 1
        assert keys[0]["name"] == "Active"


class TestAPIKeyCleanup:
    """Tests for API key cleanup."""

    def test_cleanup_expired_keys(self, api_key_manager):
        """Test cleanup of expired keys."""
        # Create expired key
        key1 = api_key_manager.generate_api_key(name="Expired", user_id=1, expires_in_days=0)

        # Create active key
        key2 = api_key_manager.generate_api_key(name="Active", user_id=1, expires_in_days=30)

        # Wait for expiration
        time.sleep(0.1)

        # Run cleanup
        api_key_manager.cleanup_expired_keys()

        # Expired key should be gone from database
        keys = api_key_manager.list_api_keys(user_id=1)
        assert len(keys) == 1
        assert keys[0]["name"] == "Active"


class TestFlaskDecorators:
    """Tests for Flask decorators."""

    @pytest.fixture
    def app(self, temp_db):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        # Create API key manager and key
        manager = APIKeyManager(temp_db)
        key = manager.generate_api_key(name="Test Key", user_id=1, permissions=["read", "write"])

        app.config["TEST_API_KEY"] = key
        return app

    def test_require_api_key_decorator_no_key(self, app):
        """Test require_api_key blocks request without key."""

        @app.route("/protected")
        @require_api_key()
        def protected():
            return {"status": "ok"}

        client = app.test_client()
        response = client.get("/protected")

        assert response.status_code == 401
        data = response.get_json()
        assert "Invalid or missing API key" in data["error"]

    def test_require_api_key_decorator_valid_key(self, app):
        """Test require_api_key allows request with valid key."""

        @app.route("/protected")
        @require_api_key()
        def protected():
            return {"status": "ok"}

        client = app.test_client()
        key = app.config["TEST_API_KEY"]

        response = client.get("/protected", headers={"X-API-Key": key})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

    def test_require_api_key_with_permissions(self, app):
        """Test require_api_key with permission check."""

        @app.route("/admin")
        @require_api_key(permissions=["admin"])
        def admin():
            return {"status": "ok"}

        client = app.test_client()
        key = app.config["TEST_API_KEY"]  # Has 'read', 'write' but not 'admin'

        response = client.get("/admin", headers={"X-API-Key": key})

        assert response.status_code == 403
        data = response.get_json()
        assert "Insufficient permissions" in data["error"]

    def test_optional_api_key_decorator(self, app):
        """Test optional_api_key decorator."""

        @app.route("/maybe-protected")
        @optional_api_key
        def maybe_protected():
            if hasattr(g, "api_key_info"):
                return {"authenticated": True, "user_id": g.api_key_info["user_id"]}
            else:
                return {"authenticated": False}

        client = app.test_client()

        # Without key
        response = client.get("/maybe-protected")
        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] == False

        # With key
        key = app.config["TEST_API_KEY"]
        response = client.get("/maybe-protected", headers={"X-API-Key": key})
        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] == True
        assert data["user_id"] == 1

    def test_bearer_token_format(self, app):
        """Test Bearer token format support."""

        @app.route("/bearer-test")
        @require_api_key()
        def bearer_test():
            return {"status": "ok"}

        client = app.test_client()
        key = app.config["TEST_API_KEY"]

        response = client.get("/bearer-test", headers={"Authorization": f"Bearer {key}"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"


class TestAPIKeySecurity:
    """Tests for API key security features."""

    def test_key_format(self, api_key_manager):
        """Test API key has correct format."""
        key = api_key_manager.generate_api_key(name="Format Test", user_id=1)

        # Should start with dms_
        assert key.startswith("dms_")

        # Should contain only valid base64 characters
        key_part = key[4:]  # Remove 'dms_' prefix
        import string

        valid_chars = string.ascii_letters + string.digits + "-_"
        assert all(c in valid_chars for c in key_part)

    def test_key_stored_as_hash(self, api_key_manager, temp_db):
        """Test API keys are stored as hashes, not plaintext."""
        key = api_key_manager.generate_api_key(name="Hash Test", user_id=1)

        # Check database directly
        import sqlite3

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("SELECT key_hash FROM api_keys WHERE name = ?", ("Hash Test",))
        row = cursor.fetchone()
        conn.close()

        stored_hash = row[0]

        # Stored value should not be the plaintext key
        assert stored_hash != key

        # Stored value should be a hash (64 hex chars for SHA-256)
        assert len(stored_hash) == 64
        assert all(c in "0123456789abcdef" for c in stored_hash)

    def test_key_prefix_for_identification(self, api_key_manager):
        """Test key prefix is stored for identification."""
        key = api_key_manager.generate_api_key(name="Prefix Test", user_id=1)

        # Get key info
        info = api_key_manager.validate_api_key(key)

        # Prefix should match first part of key
        assert key.startswith(info["key_prefix"])


class TestAPIKeyMetadata:
    """Tests for API key metadata."""

    def test_key_creation_timestamp(self, api_key_manager):
        """Test key has creation timestamp."""
        key = api_key_manager.generate_api_key(name="Timestamp Test", user_id=1)

        info = api_key_manager.validate_api_key(key)
        assert "created_at" in info
        assert info["created_at"] is not None

    def test_key_last_used_tracking(self, api_key_manager):
        """Test key tracks last used time."""
        key = api_key_manager.generate_api_key(name="Usage Test", user_id=1)

        # Use key
        api_key_manager.validate_api_key(key)

        # Check last used
        info = api_key_manager.validate_api_key(key)
        assert info["last_used_at"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
