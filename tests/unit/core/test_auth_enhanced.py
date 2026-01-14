"""
Tests for enhanced authentication module (refresh tokens and blacklist).
"""

import pytest
import jwt
import time
import tempfile
import os
from datetime import datetime, timedelta
from src.core.auth_enhanced import (
    TokenBlacklist,
    RefreshTokenManager,
    EnhancedAuthManager
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    yield temp_file.name
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except:
        pass


class TestTokenBlacklist:
    """Tests for TokenBlacklist."""

    def test_add_token_to_blacklist(self, temp_db):
        """Test adding token to blacklist."""
        blacklist = TokenBlacklist(temp_db)
        token = "test_token_123"
        user_id = 1
        expires_at = datetime.now() + timedelta(hours=1)

        blacklist.add_token(token, user_id, expires_at, reason="test")

        # Token should be blacklisted
        assert blacklist.is_blacklisted(token)

    def test_token_not_in_blacklist(self, temp_db):
        """Test token that's not in blacklist."""
        blacklist = TokenBlacklist(temp_db)
        token = "non_existent_token"

        assert not blacklist.is_blacklisted(token)

    def test_expired_token_not_blacklisted(self, temp_db):
        """Test that expired tokens are not considered blacklisted."""
        blacklist = TokenBlacklist(temp_db)
        token = "expired_token"
        user_id = 1
        expires_at = datetime.now() - timedelta(hours=1)  # Expired

        blacklist.add_token(token, user_id, expires_at)

        # Should not be blacklisted (expired)
        assert not blacklist.is_blacklisted(token)

    def test_cleanup_expired_tokens(self, temp_db):
        """Test cleanup of expired tokens."""
        blacklist = TokenBlacklist(temp_db)

        # Add expired token
        expired_token = "expired_token"
        blacklist.add_token(
            expired_token, 1,
            datetime.now() - timedelta(hours=1)
        )

        # Add active token
        active_token = "active_token"
        blacklist.add_token(
            active_token, 2,
            datetime.now() + timedelta(hours=1)
        )

        # Cleanup
        blacklist.cleanup_expired()

        # Expired should be gone, active should remain
        assert not blacklist.is_blacklisted(expired_token)
        assert blacklist.is_blacklisted(active_token)

    def test_add_duplicate_token(self, temp_db):
        """Test adding duplicate token (should not error)."""
        blacklist = TokenBlacklist(temp_db)
        token = "duplicate_token"
        expires_at = datetime.now() + timedelta(hours=1)

        # Add twice
        blacklist.add_token(token, 1, expires_at)
        blacklist.add_token(token, 1, expires_at)  # Should not error

        assert blacklist.is_blacklisted(token)


class TestRefreshTokenManager:
    """Tests for RefreshTokenManager."""

    def test_create_refresh_token(self, temp_db):
        """Test creating refresh token."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        token = manager.create_refresh_token(
            user_id,
            expires_in_days=30,
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        assert token is not None
        assert len(token) > 20  # Should be reasonably long

    def test_verify_valid_refresh_token(self, temp_db):
        """Test verifying valid refresh token."""
        manager = RefreshTokenManager(temp_db)
        user_id = 42

        # Create token
        token = manager.create_refresh_token(user_id, expires_in_days=30)

        # Verify token
        verified_user_id = manager.verify_refresh_token(token)
        assert verified_user_id == user_id

    def test_verify_invalid_refresh_token(self, temp_db):
        """Test verifying invalid refresh token."""
        manager = RefreshTokenManager(temp_db)

        # Try to verify non-existent token
        result = manager.verify_refresh_token("invalid_token_xyz")
        assert result is None

    def test_verify_expired_refresh_token(self, temp_db):
        """Test verifying expired refresh token."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        # Create token that expires immediately
        token = manager.create_refresh_token(user_id, expires_in_days=0)

        # Wait a moment
        time.sleep(0.1)

        # Should be expired
        result = manager.verify_refresh_token(token)
        assert result is None

    def test_revoke_refresh_token(self, temp_db):
        """Test revoking refresh token."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        # Create token
        token = manager.create_refresh_token(user_id)

        # Verify it works
        assert manager.verify_refresh_token(token) == user_id

        # Revoke it
        manager.revoke_refresh_token(token)

        # Should no longer work
        assert manager.verify_refresh_token(token) is None

    def test_revoke_all_user_tokens(self, temp_db):
        """Test revoking all tokens for a user."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        # Create multiple tokens
        token1 = manager.create_refresh_token(user_id)
        token2 = manager.create_refresh_token(user_id)
        token3 = manager.create_refresh_token(user_id)

        # All should work
        assert manager.verify_refresh_token(token1) == user_id
        assert manager.verify_refresh_token(token2) == user_id
        assert manager.verify_refresh_token(token3) == user_id

        # Revoke all
        manager.revoke_all_user_tokens(user_id)

        # None should work
        assert manager.verify_refresh_token(token1) is None
        assert manager.verify_refresh_token(token2) is None
        assert manager.verify_refresh_token(token3) is None

    def test_get_user_tokens(self, temp_db):
        """Test getting all tokens for a user."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        # Create tokens
        token1 = manager.create_refresh_token(user_id, ip_address="192.168.1.1")
        token2 = manager.create_refresh_token(user_id, ip_address="192.168.1.2")

        # Get tokens
        tokens = manager.get_user_tokens(user_id)

        assert len(tokens) == 2
        assert any(t['token'] == token1 for t in tokens)
        assert any(t['token'] == token2 for t in tokens)

    def test_cleanup_expired_refresh_tokens(self, temp_db):
        """Test cleanup of expired refresh tokens."""
        manager = RefreshTokenManager(temp_db)

        # Create expired token
        expired_token = manager.create_refresh_token(1, expires_in_days=0)
        time.sleep(0.1)

        # Create active token
        active_token = manager.create_refresh_token(2, expires_in_days=30)

        # Cleanup
        manager.cleanup_expired()

        # Expired should not verify, active should
        assert manager.verify_refresh_token(expired_token) is None
        assert manager.verify_refresh_token(active_token) == 2

    def test_token_last_used_updated(self, temp_db):
        """Test that last_used_at is updated on verification."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        # Create token
        token = manager.create_refresh_token(user_id)

        # Verify (should update last_used_at)
        manager.verify_refresh_token(token)

        # Get token info
        tokens = manager.get_user_tokens(user_id)
        assert len(tokens) == 1
        assert tokens[0]['last_used_at'] is not None


class TestEnhancedAuthManagerIntegration:
    """Integration tests for EnhancedAuthManager."""

    class MockAuthManager:
        """Mock auth manager for testing."""

        def authenticate(self, username, password):
            """Mock authenticate."""
            if username == "valid_user" and password == "valid_pass":
                class MockUser:
                    id = 1
                    username = "valid_user"
                return MockUser()
            return None

        def generate_token(self, user, secret_key, expires_in=3600):
            """Mock generate token."""
            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.now() + timedelta(seconds=expires_in)
            }
            return jwt.encode(payload, secret_key, algorithm='HS256')

        def verify_token(self, token, secret_key):
            """Mock verify token."""
            try:
                return jwt.decode(token, secret_key, algorithms=['HS256'])
            except:
                return None

        def load_user(self, user_id):
            """Mock load user."""
            if user_id == 1:
                class MockUser:
                    id = 1
                    username = "valid_user"
                return MockUser()
            return None

    def test_login_success(self, temp_db):
        """Test successful login."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        result = enhanced.login("valid_user", "valid_pass")
        assert result is not None

        access_token, refresh_token = result
        assert access_token is not None
        assert refresh_token is not None

    def test_login_failure(self, temp_db):
        """Test failed login."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        result = enhanced.login("invalid_user", "invalid_pass")
        assert result is None

    def test_refresh_access_token(self, temp_db):
        """Test refreshing access token."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        # Login to get tokens
        access_token, refresh_token = enhanced.login("valid_user", "valid_pass")

        # Refresh access token
        new_access_token = enhanced.refresh_access_token(refresh_token)
        assert new_access_token is not None
        assert new_access_token != access_token  # Should be different

    def test_refresh_with_invalid_token(self, temp_db):
        """Test refreshing with invalid token."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        result = enhanced.refresh_access_token("invalid_refresh_token")
        assert result is None

    def test_logout(self, temp_db):
        """Test logout revokes tokens."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        # Login
        access_token, refresh_token = enhanced.login("valid_user", "valid_pass")

        # Logout
        enhanced.logout(access_token, refresh_token)

        # Access token should be blacklisted
        assert enhanced.blacklist.is_blacklisted(access_token)

        # Refresh token should not work
        result = enhanced.refresh_access_token(refresh_token)
        assert result is None

    def test_verify_access_token_valid(self, temp_db):
        """Test verifying valid access token."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        # Login
        access_token, _ = enhanced.login("valid_user", "valid_pass")

        # Verify
        payload = enhanced.verify_access_token(access_token)
        assert payload is not None
        assert payload['user_id'] == 1

    def test_verify_access_token_blacklisted(self, temp_db):
        """Test verifying blacklisted token."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        # Login
        access_token, refresh_token = enhanced.login("valid_user", "valid_pass")

        # Logout (blacklists token)
        enhanced.logout(access_token, refresh_token)

        # Try to verify
        payload = enhanced.verify_access_token(access_token)
        assert payload is None  # Should be rejected

    def test_revoke_all_user_sessions(self, temp_db):
        """Test revoking all sessions for a user."""
        mock_auth = self.MockAuthManager()
        enhanced = EnhancedAuthManager(
            mock_auth,
            secret_key="test_secret",
            db_path=temp_db
        )

        # Login multiple times
        _, refresh1 = enhanced.login("valid_user", "valid_pass")
        _, refresh2 = enhanced.login("valid_user", "valid_pass")

        # Both should work
        assert enhanced.refresh_access_token(refresh1) is not None
        assert enhanced.refresh_access_token(refresh2) is not None

        # Revoke all
        enhanced.revoke_all_user_sessions(1)

        # Both should fail
        assert enhanced.refresh_access_token(refresh1) is None
        assert enhanced.refresh_access_token(refresh2) is None


class TestSecurityFeatures:
    """Tests for security features."""

    def test_refresh_tokens_are_unique(self, temp_db):
        """Test that each refresh token is unique."""
        manager = RefreshTokenManager(temp_db)
        user_id = 1

        tokens = set()
        for _ in range(100):
            token = manager.create_refresh_token(user_id)
            tokens.add(token)

        # All tokens should be unique
        assert len(tokens) == 100

    def test_refresh_token_length(self, temp_db):
        """Test that refresh tokens are sufficiently long."""
        manager = RefreshTokenManager(temp_db)
        token = manager.create_refresh_token(1)

        # Should be at least 32 characters (256 bits)
        assert len(token) >= 32

    def test_blacklist_prevents_reuse(self, temp_db):
        """Test that blacklist prevents token reuse."""
        blacklist = TokenBlacklist(temp_db)
        token = "reusable_token"
        expires_at = datetime.now() + timedelta(hours=1)

        # Blacklist token
        blacklist.add_token(token, 1, expires_at)

        # Multiple checks should all return True
        assert blacklist.is_blacklisted(token)
        assert blacklist.is_blacklisted(token)
        assert blacklist.is_blacklisted(token)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
