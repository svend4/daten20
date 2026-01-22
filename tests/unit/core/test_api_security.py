"""
Unit tests for API security module
"""

import hashlib
import os
import sqlite3
import tempfile
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# Check if Flask is available
try:
    import flask
    from src.core.api_security import (
        APIKeyManager,
        RateLimiter,
        RequestTracker,
        get_api_key_manager,
        get_request_tracker,
        rate_limit,
        require_api_key,
    )
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Create dummy imports to allow file to load
    APIKeyManager = None
    RateLimiter = None
    RequestTracker = None
    get_api_key_manager = None
    get_request_tracker = None
    rate_limit = None
    require_api_key = None

pytestmark = pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")


# ============================================================================
# RateLimiter Tests
# ============================================================================


class TestRateLimiter:
    """Test RateLimiter class"""

    def test_init(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(rate=100, per=3600)

        assert limiter.rate == 100
        assert limiter.per == 3600

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_is_allowed_first_request(self, mock_request):
        """Test first request is allowed"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        limiter = RateLimiter(rate=10, per=60)

        assert limiter.is_allowed() is True

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_is_allowed_under_limit(self, mock_request):
        """Test requests under limit are allowed"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        limiter = RateLimiter(rate=10, per=60)

        # Make 5 requests
        for _ in range(5):
            assert limiter.is_allowed() is True

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_is_allowed_exceeds_limit(self, mock_request):
        """Test requests exceeding limit are blocked"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        limiter = RateLimiter(rate=5, per=60)

        # Make 5 requests (all should pass)
        for _ in range(5):
            assert limiter.is_allowed() is True

        # 6th request should fail
        assert limiter.is_allowed() is False

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_is_allowed_with_user_id(self, mock_request):
        """Test rate limiting with user ID"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = 123

        limiter = RateLimiter(rate=5, per=60)

        # Should use user:123 as identifier
        for _ in range(5):
            assert limiter.is_allowed() is True

        assert limiter.is_allowed() is False

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_is_allowed_different_ips(self, mock_request):
        """Test rate limiting for different IPs"""
        limiter = RateLimiter(rate=2, per=60)

        # IP 1
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True

        # IP 2 should have separate limit
        mock_request.remote_addr = "192.168.1.2"
        assert limiter.is_allowed() is True

    def test_is_allowed_with_custom_identifier(self):
        """Test rate limiting with custom identifier"""
        limiter = RateLimiter(rate=3, per=60)

        for _ in range(3):
            assert limiter.is_allowed(identifier="custom-id") is True

        assert limiter.is_allowed(identifier="custom-id") is False

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_get_reset_time(self, mock_request):
        """Test get_reset_time"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        limiter = RateLimiter(rate=10, per=60)

        reset_time = limiter.get_reset_time()

        # Should be 0 initially (bucket is full)
        assert reset_time == 0

        # Make requests
        for _ in range(10):
            limiter.is_allowed()

        reset_time = limiter.get_reset_time()

        # Should have reset time now
        assert reset_time > 0

    @pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
    @patch("src.core.api_security.request")
    def test_token_refill(self, mock_request):
        """Test token refill over time"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        # Small window for faster testing
        limiter = RateLimiter(rate=2, per=2)

        # Exhaust tokens
        limiter.is_allowed()
        limiter.is_allowed()
        assert limiter.is_allowed() is False

        # Wait for tokens to refill
        time.sleep(1.5)

        # Should have at least 1 token now
        assert limiter.is_allowed() is True


# ============================================================================
# APIKeyManager Tests
# ============================================================================


class TestAPIKeyManager:
    """Test APIKeyManager class"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def manager(self, temp_db):
        """Create APIKeyManager instance"""
        return APIKeyManager(db_path=temp_db)

    def test_init(self, manager, temp_db):
        """Test APIKeyManager initialization"""
        assert manager.db_path == temp_db

        # Check database was created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None

    def test_generate_key(self, manager):
        """Test generating API key"""
        key = manager.generate_key(user_id=123, name="Test Key", scopes=["read", "write"])

        assert key.startswith("dms_")
        assert len(key) > 20

    def test_generate_key_with_expiration(self, manager):
        """Test generating key with expiration"""
        key = manager.generate_key(user_id=123, name="Temp Key", expires_in_days=30)

        assert key.startswith("dms_")

    def test_verify_key_valid(self, manager):
        """Test verifying valid API key"""
        key = manager.generate_key(user_id=123, name="Test Key", scopes=["read", "write"])

        key_info = manager.verify_key(key)

        assert key_info is not None
        assert key_info["user_id"] == 123
        assert key_info["name"] == "Test Key"
        assert "read" in key_info["scopes"]
        assert "write" in key_info["scopes"]

    def test_verify_key_invalid(self, manager):
        """Test verifying invalid API key"""
        key_info = manager.verify_key("dms_invalid_key_123")

        assert key_info is None

    def test_verify_key_expired(self, manager):
        """Test verifying expired API key"""
        # Generate key with 0 days expiration (will be in the past)
        key = manager.generate_key(user_id=123, name="Expired Key", expires_in_days=0)

        # Manually set expiration to past
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("UPDATE api_keys SET expires_at = ? WHERE key_hash = ?", (past_date, key_hash))
        conn.commit()
        conn.close()

        key_info = manager.verify_key(key)

        assert key_info is None

    def test_verify_key_updates_last_used(self, manager):
        """Test that verify_key updates last_used timestamp"""
        key = manager.generate_key(user_id=123, name="Test Key")

        # Verify key
        manager.verify_key(key)

        # Check last_used was updated
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        conn = sqlite3.connect(manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT last_used FROM api_keys WHERE key_hash = ?", (key_hash,))
        row = cursor.fetchone()
        conn.close()

        assert row["last_used"] is not None

    def test_revoke_key(self, manager):
        """Test revoking API key"""
        key = manager.generate_key(user_id=123, name="Test Key")

        # Get key ID
        key_info = manager.verify_key(key)
        key_id = key_info["id"]

        # Revoke key
        manager.revoke_key(key_id)

        # Verify key no longer works
        key_info = manager.verify_key(key)
        assert key_info is None

    def test_generate_key_without_scopes(self, manager):
        """Test generating key without scopes"""
        key = manager.generate_key(user_id=123, name="No Scopes Key")

        key_info = manager.verify_key(key)

        assert key_info is not None
        assert key_info["scopes"] == []

    def test_multiple_keys_same_user(self, manager):
        """Test generating multiple keys for same user"""
        key1 = manager.generate_key(user_id=123, name="Key 1", scopes=["read"])
        key2 = manager.generate_key(user_id=123, name="Key 2", scopes=["write"])

        key_info1 = manager.verify_key(key1)
        key_info2 = manager.verify_key(key2)

        assert key_info1 is not None
        assert key_info2 is not None
        assert key1 != key2


# ============================================================================
# RequestTracker Tests
# ============================================================================


class TestRequestTracker:
    """Test RequestTracker class"""

    def test_init(self):
        """Test RequestTracker initialization"""
        tracker = RequestTracker()

        assert tracker.requests == []
        assert tracker.max_history == 10000

    def test_track_request(self):
        """Test tracking a request"""
        tracker = RequestTracker()

        tracker.track(endpoint="/api/services", method="GET", status_code=200, duration=0.05)

        assert len(tracker.requests) == 1
        assert tracker.requests[0]["endpoint"] == "/api/services"
        assert tracker.requests[0]["method"] == "GET"
        assert tracker.requests[0]["status_code"] == 200
        assert tracker.requests[0]["duration"] == 0.05

    def test_track_multiple_requests(self):
        """Test tracking multiple requests"""
        tracker = RequestTracker()

        tracker.track("/api/services", "GET", 200, 0.05)
        tracker.track("/api/services", "POST", 201, 0.08)
        tracker.track("/api/calculate", "POST", 200, 0.15)

        assert len(tracker.requests) == 3

    def test_track_limits_history(self):
        """Test that tracker limits history size"""
        tracker = RequestTracker()
        tracker.max_history = 100

        # Track 150 requests
        for i in range(150):
            tracker.track(f"/api/endpoint{i}", "GET", 200, 0.05)

        # Should keep only last 100
        assert len(tracker.requests) == 100

    def test_get_stats_empty(self):
        """Test get_stats with no requests"""
        tracker = RequestTracker()

        stats = tracker.get_stats()

        assert stats == {}

    def test_get_stats(self):
        """Test get_stats with requests"""
        tracker = RequestTracker()

        tracker.track("/api/services", "GET", 200, 0.05)
        tracker.track("/api/services", "POST", 201, 0.08)
        tracker.track("/api/calculate", "POST", 200, 0.12)
        tracker.track("/api/services", "GET", 404, 0.03)

        stats = tracker.get_stats()

        assert stats["total_requests"] == 4
        assert stats["avg_duration_ms"] == 70.0  # (50+80+120+30)/4
        assert "/api/services" in stats["by_endpoint"]
        assert stats["by_endpoint"]["/api/services"] == 3
        assert stats["by_status"][200] == 2
        assert stats["by_status"][201] == 1
        assert stats["by_status"][404] == 1


# ============================================================================
# Decorator Tests
# ============================================================================


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
class TestRateLimitDecorator:
    """Test rate_limit decorator"""

    @patch("src.core.api_security.request")
    @patch("src.core.api_security.jsonify")
    def test_rate_limit_allows_under_limit(self, mock_jsonify, mock_request):
        """Test rate_limit decorator allows requests under limit"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        @rate_limit(rate=10, per=60)
        def test_endpoint():
            return "success"

        # First request should succeed
        result = test_endpoint()
        assert result == "success"

    @patch("src.core.api_security.request")
    @patch("src.core.api_security.jsonify")
    def test_rate_limit_blocks_over_limit(self, mock_jsonify, mock_request):
        """Test rate_limit decorator blocks requests over limit"""
        mock_request.remote_addr = "192.168.1.1"
        mock_request.user_id = None

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_jsonify.return_value = mock_response

        @rate_limit(rate=2, per=60)
        def test_endpoint():
            return "success"

        # Make 2 requests (should succeed)
        test_endpoint()
        test_endpoint()

        # 3rd request should be rate limited
        response = test_endpoint()
        assert response.status_code == 429


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")
class TestRequireAPIKeyDecorator:
    """Test require_api_key decorator"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def manager(self, temp_db):
        """Create APIKeyManager"""
        return APIKeyManager(db_path=temp_db)

    @patch("src.core.api_security.request")
    @patch("src.core.api_security.get_api_key_manager")
    @patch("src.core.api_security.jsonify")
    def test_require_api_key_missing_key(self, mock_jsonify, mock_get_manager, mock_request):
        """Test decorator rejects request without API key"""
        mock_request.headers.get.return_value = None
        mock_jsonify.return_value = ({"error": "API key required"}, 401)

        @require_api_key()
        def test_endpoint():
            return "success"

        response, status_code = test_endpoint()
        assert status_code == 401

    @patch("src.core.api_security.request")
    @patch("src.core.api_security.get_api_key_manager")
    @patch("src.core.api_security.jsonify")
    def test_require_api_key_invalid_key(self, mock_jsonify, mock_get_manager, mock_request):
        """Test decorator rejects invalid API key"""
        mock_request.headers.get.return_value = "invalid_key"
        mock_request.remote_addr = "192.168.1.1"

        mock_manager = MagicMock()
        mock_manager.verify_key.return_value = None
        mock_get_manager.return_value = mock_manager

        mock_jsonify.return_value = ({"error": "Invalid API key"}, 401)

        @require_api_key()
        def test_endpoint():
            return "success"

        response, status_code = test_endpoint()
        assert status_code == 401

    @patch("src.core.api_security.request")
    @patch("src.core.api_security.get_api_key_manager")
    def test_require_api_key_valid_key(self, mock_get_manager, mock_request):
        """Test decorator allows valid API key"""
        mock_request.headers.get.return_value = "valid_key"

        mock_manager = MagicMock()
        mock_manager.verify_key.return_value = {"id": 1, "user_id": 123, "scopes": ["read", "write"]}
        mock_get_manager.return_value = mock_manager

        @require_api_key()
        def test_endpoint():
            return "success"

        result = test_endpoint()
        assert result == "success"

    @patch("src.core.api_security.request")
    @patch("src.core.api_security.get_api_key_manager")
    @patch("src.core.api_security.jsonify")
    def test_require_api_key_insufficient_scopes(self, mock_jsonify, mock_get_manager, mock_request):
        """Test decorator rejects key with insufficient scopes"""
        mock_request.headers.get.return_value = "valid_key"
        mock_request.remote_addr = "192.168.1.1"

        mock_manager = MagicMock()
        mock_manager.verify_key.return_value = {"id": 1, "user_id": 123, "scopes": ["read"]}
        mock_get_manager.return_value = mock_manager

        mock_jsonify.return_value = ({"error": "Insufficient permissions"}, 403)

        @require_api_key(scopes=["write"])
        def test_endpoint():
            return "success"

        response, status_code = test_endpoint()
        assert status_code == 403


# ============================================================================
# Global Instance Tests
# ============================================================================


class TestGlobalInstances:
    """Test global instance functions"""

    def test_get_request_tracker(self):
        """Test get_request_tracker returns singleton"""
        tracker1 = get_request_tracker()
        tracker2 = get_request_tracker()

        assert tracker1 is tracker2
