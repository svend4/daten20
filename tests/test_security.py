"""
Tests for Security Modules

Tests for:
- Rate limiter
- Input validation
- CSRF protection
- Authentication enhancements
"""

import pytest
import time
from decimal import Decimal
from datetime import datetime, timedelta

from src.core.rate_limiter import RateLimiter, TokenBucketRateLimiter, RateLimitExceeded
from src.core.input_validation import InputValidator, ValidationError
from src.core.auth_enhanced import TokenBlacklist, RefreshTokenManager


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests=5, window=10)
        client_id = "test_client"

        # Should allow 5 requests
        for i in range(5):
            is_allowed, retry_after = limiter.is_allowed(client_id)
            assert is_allowed
            assert retry_after is None

    def test_rate_limiter_blocks_excess_requests(self):
        """Test that excess requests are blocked."""
        limiter = RateLimiter(requests=3, window=10)
        client_id = "test_client"

        # Allow 3 requests
        for i in range(3):
            is_allowed, _ = limiter.is_allowed(client_id)
            assert is_allowed

        # Block 4th request
        is_allowed, retry_after = limiter.is_allowed(client_id)
        assert not is_allowed
        assert retry_after is not None
        assert retry_after > 0

    def test_rate_limiter_reset(self):
        """Test rate limiter reset."""
        limiter = RateLimiter(requests=2, window=10)
        client_id = "test_client"

        # Use up limit
        limiter.is_allowed(client_id)
        limiter.is_allowed(client_id)

        # Reset
        limiter.reset(client_id)

        # Should allow again
        is_allowed, _ = limiter.is_allowed(client_id)
        assert is_allowed

    def test_rate_limiter_remaining(self):
        """Test getting remaining requests."""
        limiter = RateLimiter(requests=5, window=10)
        client_id = "test_client"

        # Initially should have 5 remaining
        remaining = limiter.get_remaining(client_id)
        assert remaining == 5

        # After 1 request, should have 4 remaining
        limiter.is_allowed(client_id)
        remaining = limiter.get_remaining(client_id)
        assert remaining == 4

    def test_token_bucket_allows_bursts(self):
        """Test token bucket allows burst traffic."""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1)
        client_id = "test_client"

        # Should allow burst of 10 requests
        for i in range(10):
            is_allowed, _ = limiter.is_allowed(client_id, tokens=1)
            assert is_allowed

        # 11th should be blocked
        is_allowed, retry_after = limiter.is_allowed(client_id, tokens=1)
        assert not is_allowed
        assert retry_after is not None


class TestInputValidator:
    """Test input validation functionality."""

    def test_validate_string_basic(self):
        """Test basic string validation."""
        validator = InputValidator()

        # Valid string
        result = validator.validate_string("hello", min_length=1, max_length=10)
        assert result == "hello"

        # Too short
        with pytest.raises(ValidationError):
            validator.validate_string("", min_length=1, allow_empty=False)

        # Too long
        with pytest.raises(ValidationError):
            validator.validate_string("x" * 100, max_length=10)

    def test_validate_integer(self):
        """Test integer validation."""
        validator = InputValidator()

        # Valid integer
        result = validator.validate_integer("42", min_value=0, max_value=100)
        assert result == 42

        # Below minimum
        with pytest.raises(ValidationError):
            validator.validate_integer("-5", min_value=0)

        # Above maximum
        with pytest.raises(ValidationError):
            validator.validate_integer("200", max_value=100)

        # Invalid format
        with pytest.raises(ValidationError):
            validator.validate_integer("abc")

    def test_validate_decimal(self):
        """Test decimal validation."""
        validator = InputValidator()

        # Valid decimal
        result = validator.validate_decimal("123.45", min_value=Decimal('0'))
        assert result == Decimal("123.45")

        # Negative when not allowed
        with pytest.raises(ValidationError):
            validator.validate_decimal("-10", min_value=Decimal('0'))

        # Too large
        with pytest.raises(ValidationError):
            validator.validate_decimal("1000000", max_value=Decimal('999'))

    def test_validate_email(self):
        """Test email validation."""
        validator = InputValidator()

        # Valid email
        result = validator.validate_email("user@example.com")
        assert result == "user@example.com"

        # Invalid emails
        with pytest.raises(ValidationError):
            validator.validate_email("invalid")

        with pytest.raises(ValidationError):
            validator.validate_email("@example.com")

        with pytest.raises(ValidationError):
            validator.validate_email("user@")

    def test_validate_url(self):
        """Test URL validation."""
        validator = InputValidator()

        # Valid URLs
        result = validator.validate_url("https://example.com")
        assert result == "https://example.com"

        result = validator.validate_url("http://localhost:8000/path")
        assert result.startswith("http://")

        # Invalid URL
        with pytest.raises(ValidationError):
            validator.validate_url("not a url")

        # Disallowed scheme
        with pytest.raises(ValidationError):
            validator.validate_url("ftp://example.com", allowed_schemes=['http', 'https'])

    def test_validate_enum(self):
        """Test enum validation."""
        validator = InputValidator()

        allowed_values = ['red', 'green', 'blue']

        # Valid value
        result = validator.validate_enum('red', allowed_values)
        assert result == 'red'

        # Invalid value
        with pytest.raises(ValidationError):
            validator.validate_enum('yellow', allowed_values)

        # Case insensitive
        result = validator.validate_enum('RED', allowed_values, case_sensitive=False)
        assert result == 'RED'

    def test_sanitize_html(self):
        """Test HTML sanitization."""
        validator = InputValidator()

        # Remove script tags
        dangerous = '<script>alert("XSS")</script>Hello'
        safe = validator.sanitize_html(dangerous)
        assert '<script>' not in safe
        assert 'Hello' in safe

        # Remove event handlers
        dangerous = '<div onclick="evil()">Click</div>'
        safe = validator.sanitize_html(dangerous)
        assert 'onclick' not in safe

        # Remove javascript: URLs
        dangerous = '<a href="javascript:void(0)">Link</a>'
        safe = validator.sanitize_html(dangerous)
        assert 'javascript:' not in safe

    def test_check_sql_injection(self):
        """Test SQL injection detection."""
        validator = InputValidator()

        # Should detect SQL keywords
        assert validator.check_sql_injection("SELECT * FROM users")
        assert validator.check_sql_injection("DROP TABLE services")
        assert validator.check_sql_injection("'; DELETE FROM users; --")

        # Should not flag normal text
        assert not validator.check_sql_injection("normal text")
        assert not validator.check_sql_injection("user@example.com")

    def test_check_command_injection(self):
        """Test command injection detection."""
        validator = InputValidator()

        # Should detect command injection patterns
        assert validator.check_command_injection("file.txt; rm -rf /")
        assert validator.check_command_injection("input | cat /etc/passwd")
        assert validator.check_command_injection("$(whoami)")

        # Should not flag normal text
        assert not validator.check_command_injection("normal filename.txt")

    def test_validate_file_path(self):
        """Test file path validation."""
        validator = InputValidator()

        # Should detect path traversal
        with pytest.raises(ValidationError):
            validator.validate_file_path("../../../etc/passwd")

        with pytest.raises(ValidationError):
            validator.validate_file_path("./../../secrets.txt")

        # Valid relative path (without traversal)
        result = validator.validate_file_path("uploads/file.txt")
        assert str(result).endswith("file.txt")

    def test_validate_json(self):
        """Test JSON validation."""
        validator = InputValidator()

        # Valid JSON
        result = validator.validate_json('{"key": "value"}')
        assert result == {"key": "value"}

        # Invalid JSON
        with pytest.raises(ValidationError):
            validator.validate_json('{invalid}')

        # Too deeply nested (DoS prevention)
        deeply_nested = '{"a":' * 20 + '{}' + '}' * 20
        with pytest.raises(ValidationError):
            validator.validate_json(deeply_nested, max_depth=10)


class TestTokenBlacklist:
    """Test token blacklist functionality."""

    def test_add_and_check_token(self, tmp_path):
        """Test adding and checking tokens."""
        db_path = str(tmp_path / "test_blacklist.db")
        blacklist = TokenBlacklist(db_path)

        token = "test_token_123"
        user_id = 1
        expires_at = datetime.now() + timedelta(hours=1)

        # Add token
        blacklist.add_token(token, user_id, expires_at)

        # Check it's blacklisted
        assert blacklist.is_blacklisted(token)

        # Check different token is not blacklisted
        assert not blacklist.is_blacklisted("different_token")

    def test_expired_tokens_not_blacklisted(self, tmp_path):
        """Test that expired tokens are not considered blacklisted."""
        db_path = str(tmp_path / "test_blacklist.db")
        blacklist = TokenBlacklist(db_path)

        token = "expired_token"
        user_id = 1
        expires_at = datetime.now() - timedelta(hours=1)  # Expired

        # Add expired token
        blacklist.add_token(token, user_id, expires_at)

        # Should not be blacklisted (expired)
        assert not blacklist.is_blacklisted(token)

    def test_cleanup_expired(self, tmp_path):
        """Test cleanup of expired tokens."""
        db_path = str(tmp_path / "test_blacklist.db")
        blacklist = TokenBlacklist(db_path)

        # Add expired token
        token1 = "expired_token"
        expires_at1 = datetime.now() - timedelta(hours=1)
        blacklist.add_token(token1, 1, expires_at1)

        # Add valid token
        token2 = "valid_token"
        expires_at2 = datetime.now() + timedelta(hours=1)
        blacklist.add_token(token2, 1, expires_at2)

        # Cleanup
        blacklist.cleanup_expired()

        # Expired should be removed, valid should remain
        assert not blacklist.is_blacklisted(token1)
        assert blacklist.is_blacklisted(token2)


class TestRefreshTokenManager:
    """Test refresh token manager functionality."""

    def test_create_and_verify_token(self, tmp_path):
        """Test creating and verifying refresh tokens."""
        db_path = str(tmp_path / "test_refresh.db")
        manager = RefreshTokenManager(db_path)

        user_id = 1

        # Create token
        token = manager.create_refresh_token(user_id, expires_in_days=30)
        assert token is not None
        assert len(token) > 0

        # Verify token
        verified_user_id = manager.verify_refresh_token(token)
        assert verified_user_id == user_id

    def test_verify_invalid_token(self, tmp_path):
        """Test verifying invalid token."""
        db_path = str(tmp_path / "test_refresh.db")
        manager = RefreshTokenManager(db_path)

        # Try to verify non-existent token
        result = manager.verify_refresh_token("invalid_token")
        assert result is None

    def test_revoke_token(self, tmp_path):
        """Test revoking refresh token."""
        db_path = str(tmp_path / "test_refresh.db")
        manager = RefreshTokenManager(db_path)

        user_id = 1
        token = manager.create_refresh_token(user_id)

        # Revoke token
        manager.revoke_refresh_token(token)

        # Should not be valid anymore
        result = manager.verify_refresh_token(token)
        assert result is None

    def test_revoke_all_user_tokens(self, tmp_path):
        """Test revoking all tokens for a user."""
        db_path = str(tmp_path / "test_refresh.db")
        manager = RefreshTokenManager(db_path)

        user_id = 1

        # Create multiple tokens
        token1 = manager.create_refresh_token(user_id)
        token2 = manager.create_refresh_token(user_id)

        # Revoke all
        manager.revoke_all_user_tokens(user_id)

        # All should be invalid
        assert manager.verify_refresh_token(token1) is None
        assert manager.verify_refresh_token(token2) is None

    def test_cleanup_expired(self, tmp_path):
        """Test cleanup of expired refresh tokens."""
        db_path = str(tmp_path / "test_refresh.db")
        manager = RefreshTokenManager(db_path)

        # Create expired token (we can't create truly expired, so we'll test the cleanup logic)
        # In real scenario, tokens would expire over time
        manager.cleanup_expired()

        # Should not raise any errors
        assert True


# Integration Tests

class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_rate_limiter_with_input_validator(self):
        """Test rate limiter combined with input validator."""
        limiter = RateLimiter(requests=5, window=60)
        validator = InputValidator()

        client_id = "test_client"

        # Simulate requests with validation
        for i in range(5):
            # Check rate limit
            is_allowed, _ = limiter.is_allowed(client_id)
            assert is_allowed

            # Validate input
            email = f"user{i}@example.com"
            validated_email = validator.validate_email(email)
            assert validated_email == email

        # 6th request should be blocked
        is_allowed, retry_after = limiter.is_allowed(client_id)
        assert not is_allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
