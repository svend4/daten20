"""
Tests for rate limiter module.
"""

import time

import pytest

from src.core.rate_limiter import GlobalRateLimiters, RateLimiter, RateLimitExceeded, TokenBucketRateLimiter


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
        limiter.cleanup()
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
        assert GlobalRateLimiters.export is not None
        assert GlobalRateLimiters.export.requests == 10
        assert GlobalRateLimiters.export.window == 300


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
