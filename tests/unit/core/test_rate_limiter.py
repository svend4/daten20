"""
Tests for rate limiter module.

Tests both basic and advanced rate limiting functionality:
- RateLimiter (sliding window)
- TokenBucketRateLimiter
- RedisRateLimiter (distributed)
- RateLimitTier (configuration)
- FastAPI integration
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.rate_limiter import (
    GlobalRateLimiters,
    RateLimiter,
    RateLimitExceeded,
    RateLimitTier,
    RedisRateLimiter,
    TokenBucketRateLimiter,
    check_rate_limit,
    create_rate_limit_dependency,
)


class TestRateLimiter:
    """Tests for RateLimiter (Sliding Window algorithm)."""

    def test_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests=5, window=60)
        client_id = "test_client_1"

        # Should allow 5 requests
        for i in range(5):
            allowed, retry_after = limiter.is_allowed(client_id)
            assert allowed, f"Request {i+1} should be allowed"

    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter(requests=3, window=60)
        client_id = "test_client_2"

        # Allow 3 requests
        for i in range(3):
            allowed, _ = limiter.is_allowed(client_id)
            assert allowed

        # 4th request should be blocked
        allowed, retry_after = limiter.is_allowed(client_id)
        assert not allowed
        assert retry_after > 0

    def test_resets_after_window(self):
        """Test that limit resets after window expires."""
        limiter = RateLimiter(requests=2, window=1)  # 1 second window
        client_id = "test_client_3"

        # Use up limit
        for i in range(2):
            allowed, _ = limiter.is_allowed(client_id)
            assert allowed

        # Should be blocked
        allowed, _ = limiter.is_allowed(client_id)
        assert not allowed

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        allowed, retry_after = limiter.is_allowed(client_id)
        assert allowed

    def test_different_clients_independent(self):
        """Test that different clients have independent limits."""
        limiter = RateLimiter(requests=2, window=60)

        # Client 1 uses up limit
        for i in range(2):
            allowed, _ = limiter.is_allowed("client_1")
            assert allowed

        # Client 1 should be blocked
        allowed, _ = limiter.is_allowed("client_1")
        assert not allowed

        # Client 2 should still be allowed
        allowed, _ = limiter.is_allowed("client_2")
        assert allowed

    def test_cleanup_removes_inactive_clients(self):
        """Test that cleanup removes inactive clients."""
        limiter = RateLimiter(requests=5, window=1)

        # Create some requests
        limiter.is_allowed("client_1")
        limiter.is_allowed("client_2")
        limiter.is_allowed("client_3")

        assert len(limiter.clients) == 3

        # Wait for window to expire
        time.sleep(1.1)

        # Cleanup should remove all clients
        limiter.cleanup_old_clients(max_age=0)
        assert len(limiter.clients) == 0


class TestTokenBucketRateLimiter:
    """Tests for TokenBucketRateLimiter."""

    def test_allows_requests_within_capacity(self):
        """Test that requests within capacity are allowed."""
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
        client_id = "test_client_1"

        # Should allow 5 requests (full bucket)
        for i in range(5):
            allowed, retry_after = limiter.is_allowed(client_id)
            assert allowed, f"Request {i+1} should be allowed"

    def test_blocks_when_bucket_empty(self):
        """Test that requests are blocked when bucket is empty."""
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate=1.0)
        client_id = "test_client_2"

        # Use up tokens
        for i in range(2):
            allowed, _ = limiter.is_allowed(client_id)
            assert allowed

        # Should be blocked
        allowed, retry_after = limiter.is_allowed(client_id)
        assert not allowed
        assert retry_after > 0

    def test_refills_tokens_over_time(self):
        """Test that tokens are refilled over time."""
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate=2.0)  # 2 tokens/sec
        client_id = "test_client_3"

        # Use up tokens
        for i in range(2):
            allowed, _ = limiter.is_allowed(client_id)
            assert allowed

        # Should be blocked
        allowed, _ = limiter.is_allowed(client_id)
        assert not allowed

        # Wait for refill (0.5 seconds = 1 token)
        time.sleep(0.6)

        # Should have 1 token now
        allowed, _ = limiter.is_allowed(client_id)
        assert allowed

    def test_supports_burst_traffic(self):
        """Test that bucket supports burst traffic."""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        client_id = "test_client_4"

        # Should allow burst of 10 requests
        for i in range(10):
            allowed, _ = limiter.is_allowed(client_id)
            assert allowed


class TestGlobalRateLimiters:
    """Tests for GlobalRateLimiters."""

    def test_auth_login_limiter_exists(self):
        """Test that auth_login limiter is configured."""
        assert GlobalRateLimiters.auth_login is not None
        assert GlobalRateLimiters.auth_login.requests == 5
        assert GlobalRateLimiters.auth_login.window == 60

    def test_api_default_limiter_exists(self):
        """Test that api_default limiter is configured."""
        assert GlobalRateLimiters.api_default is not None
        assert GlobalRateLimiters.api_default.requests == 100
        assert GlobalRateLimiters.api_default.window == 60

    def test_export_limiter_exists(self):
        """Test that export limiter is configured."""
        assert GlobalRateLimiters.export_operations is not None
        assert GlobalRateLimiters.export_operations.requests == 10
        assert GlobalRateLimiters.export_operations.window == 300


class TestRateLimitExceeded:
    """Tests for RateLimitExceeded exception."""

    def test_exception_creation(self):
        """Test exception can be created."""
        exc = RateLimitExceeded("Test message", retry_after=30)
        assert str(exc) == "Test message"
        assert exc.retry_after == 30

    def test_exception_raised(self):
        """Test exception can be raised and caught."""
        with pytest.raises(RateLimitExceeded) as exc_info:
            raise RateLimitExceeded("Rate limit exceeded", retry_after=60)

        assert exc_info.value.retry_after == 60


class TestRateLimiterThreadSafety:
    """Tests for thread safety of rate limiters."""

    def test_concurrent_requests(self):
        """Test that concurrent requests are handled correctly."""
        import threading

        limiter = RateLimiter(requests=100, window=60)
        client_id = "concurrent_client"
        results = []

        def make_request():
            allowed, _ = limiter.is_allowed(client_id)
            results.append(allowed)

        # Create 100 threads
        threads = [threading.Thread(target=make_request) for _ in range(100)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # All 100 requests should be allowed
        assert sum(results) == 100


class TestRedisRateLimiter:
    """Tests for RedisRateLimiter (distributed rate limiting)."""

    @pytest.mark.skipif(
        not pytest.importorskip("redis", minversion=None),
        reason="Redis not installed"
    )
    @patch("redis.Redis")
    def test_initialization_with_redis_available(self, mock_redis_class):
        """Test initialization when Redis is available."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=100, window=60)
        assert limiter.redis_client is not None
        mock_client.ping.assert_called_once()

    @patch("redis.Redis")
    def test_initialization_falls_back_without_redis(self, mock_redis_class):
        """Test fallback to in-memory when Redis unavailable."""
        mock_redis_class.side_effect = Exception("Connection refused")

        limiter = RedisRateLimiter(requests=100, window=60)
        assert limiter.redis_client is None
        assert hasattr(limiter, "fallback_limiter")

    @patch("redis.Redis")
    def test_allows_requests_with_redis(self, mock_redis_class):
        """Test allowing requests through Redis."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.zcard.return_value = 2  # 2 requests in window
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=5, window=60)
        is_allowed, retry_after = limiter.is_allowed("test_client")

        assert is_allowed is True
        assert retry_after is None
        mock_client.zadd.assert_called_once()
        mock_client.expire.assert_called_once()

    @patch("redis.Redis")
    def test_blocks_over_limit_with_redis(self, mock_redis_class):
        """Test blocking requests over limit with Redis."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.zcard.return_value = 5  # At limit
        mock_client.zrange.return_value = [(None, time.time())]
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=5, window=60)
        is_allowed, retry_after = limiter.is_allowed("test_client")

        assert is_allowed is False
        assert retry_after is not None

    @patch("redis.Redis")
    def test_get_remaining_with_redis(self, mock_redis_class):
        """Test getting remaining requests with Redis."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.zcard.return_value = 3
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=10, window=60)
        remaining = limiter.get_remaining("test_client")

        assert remaining == 7  # 10 - 3

    @patch("redis.Redis")
    def test_reset_with_redis(self, mock_redis_class):
        """Test reset functionality with Redis."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=5, window=60)
        limiter.reset("test_client")

        mock_client.delete.assert_called_once()

    @patch("redis.Redis")
    def test_redis_error_allows_request(self, mock_redis_class):
        """Test that Redis errors result in allowing request (fail-open)."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.zcard.side_effect = Exception("Redis timeout")
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=5, window=60)
        is_allowed, retry_after = limiter.is_allowed("test_client")

        # Should allow on error
        assert is_allowed is True


class TestRateLimitTier:
    """Tests for RateLimitTier configuration."""

    def test_tier_configurations_exist(self):
        """Test that all tier configurations are defined."""
        assert hasattr(RateLimitTier, "FREE")
        assert hasattr(RateLimitTier, "BASIC")
        assert hasattr(RateLimitTier, "PREMIUM")
        assert hasattr(RateLimitTier, "ENTERPRISE")

    def test_tier_limits_correct(self):
        """Test that tier limits are configured correctly."""
        assert RateLimitTier.FREE["requests"] == 100
        assert RateLimitTier.BASIC["requests"] == 500
        assert RateLimitTier.PREMIUM["requests"] == 2000
        assert RateLimitTier.ENTERPRISE["requests"] == 10000

    def test_get_limiter_free_tier(self):
        """Test getting limiter for FREE tier."""
        limiter = RateLimitTier.get_limiter("free")
        assert isinstance(limiter, RateLimiter)
        assert limiter.requests == 100
        assert limiter.window == 60

    def test_get_limiter_premium_tier(self):
        """Test getting limiter for PREMIUM tier."""
        limiter = RateLimitTier.get_limiter("premium")
        assert limiter.requests == 2000

    @patch("redis.Redis")
    def test_get_limiter_with_redis(self, mock_redis_class):
        """Test getting Redis limiter for tier."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client

        limiter = RateLimitTier.get_limiter("basic", use_redis=True)
        assert isinstance(limiter, RedisRateLimiter)
        assert limiter.requests == 500

    def test_get_limiter_invalid_tier_uses_free(self):
        """Test that invalid tier falls back to FREE."""
        limiter = RateLimitTier.get_limiter("invalid_tier")
        assert limiter.requests == 100  # FREE tier default


class TestFastAPIIntegration:
    """Tests for FastAPI integration."""

    def test_create_rate_limit_dependency(self):
        """Test creating rate limit dependency."""
        limiter = RateLimiter(requests=10, window=60)
        rate_limit_dep = create_rate_limit_dependency(limiter)
        assert rate_limit_dep is not None
        assert callable(rate_limit_dep)

    @pytest.mark.asyncio
    async def test_rate_limit_dependency_allows_request(self):
        """Test that dependency allows valid requests."""
        try:
            limiter = RateLimiter(requests=10, window=60)
            rate_limit_dep = create_rate_limit_dependency(limiter)

            # Mock request
            mock_request = Mock()
            mock_request.headers = Mock()
            mock_request.headers.get = Mock(return_value=None)
            mock_request.client = Mock()
            mock_request.client.host = "127.0.0.1"

            result = await rate_limit_dep(mock_request)
            assert result is None  # No exception
        except ImportError:
            pytest.skip("FastAPI not installed")

    @pytest.mark.asyncio
    async def test_rate_limit_dependency_blocks_over_limit(self):
        """Test that dependency raises HTTPException when over limit."""
        try:
            from fastapi import HTTPException

            limiter = RateLimiter(requests=1, window=60)
            rate_limit_dep = create_rate_limit_dependency(limiter)

            mock_request = Mock()
            mock_request.headers = Mock()
            mock_request.headers.get = Mock(return_value=None)
            mock_request.client = Mock()
            mock_request.client.host = "127.0.0.1"

            # First request allowed
            await rate_limit_dep(mock_request)

            # Second request blocked
            with pytest.raises(HTTPException) as exc_info:
                await rate_limit_dep(mock_request)

            assert exc_info.value.status_code == 429
            assert "rate_limit_exceeded" in str(exc_info.value.detail)
        except ImportError:
            pytest.skip("FastAPI not installed")


class TestCheckRateLimit:
    """Tests for check_rate_limit helper function."""

    def test_check_rate_limit_allows(self):
        """Test that check_rate_limit allows valid requests."""
        limiter = RateLimiter(requests=5, window=60)
        result = check_rate_limit("test_client", limiter)
        assert result is True

    def test_check_rate_limit_raises_exception(self):
        """Test that check_rate_limit raises exception when exceeded."""
        limiter = RateLimiter(requests=1, window=60)
        limiter.is_allowed("test_client")  # Use up limit

        with pytest.raises(RateLimitExceeded) as exc_info:
            check_rate_limit("test_client", limiter)

        assert "Rate limit exceeded" in exc_info.value.message
        assert exc_info.value.retry_after is not None


class TestEndToEndScenarios:
    """End-to-end integration tests."""

    def test_complete_rate_limiting_flow(self):
        """Test complete rate limiting workflow."""
        limiter = RateLimiter(requests=3, window=2)
        client_id = "e2e_client"

        # First 3 requests should succeed
        for i in range(3):
            is_allowed, _ = limiter.is_allowed(client_id)
            assert is_allowed is True
            remaining = limiter.get_remaining(client_id)
            assert remaining == 2 - i

        # 4th request should fail
        is_allowed, retry_after = limiter.is_allowed(client_id)
        assert is_allowed is False
        assert retry_after is not None

        # Wait for window to expire
        time.sleep(2.1)

        # Should work again
        is_allowed, _ = limiter.is_allowed(client_id)
        assert is_allowed is True

    def test_multiple_clients_independent_limits(self):
        """Test that multiple clients have independent limits."""
        limiter = RateLimiter(requests=2, window=60)

        # Client 1 uses limit
        limiter.is_allowed("client_1")
        limiter.is_allowed("client_1")
        is_allowed, _ = limiter.is_allowed("client_1")
        assert is_allowed is False

        # Client 2 should still work
        is_allowed, _ = limiter.is_allowed("client_2")
        assert is_allowed is True

    @patch("redis.Redis")
    def test_redis_distributed_rate_limiting(self, mock_redis_class):
        """Test distributed rate limiting with Redis."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.zcard.side_effect = [0, 1, 2]  # Simulating incremental usage
        mock_redis_class.return_value = mock_client

        limiter = RedisRateLimiter(requests=3, window=60)

        # Multiple requests
        for i in range(3):
            is_allowed, _ = limiter.is_allowed("distributed_client")
            assert is_allowed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
