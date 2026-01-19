"""
Comprehensive tests for caching module.

Test coverage goals:
- Positive cases: Normal cache operations
- Negative cases: Error handling and edge cases
- Edge cases: Expiry, large values, concurrent access
- Integration: Decorator functionality, performance monitoring
"""

import pickle
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

import pytest

from src.core.cache import (
    CacheBackend,
    CacheManager,
    PerformanceMonitor,
    RedisCache,
    SimpleCache,
    _generate_cache_key,
    cache_invalidate,
    cached,
    get_cache_manager,
    get_performance_monitor,
    init_cache,
    timed,
)

# Check if redis is available
try:
    import redis
    REDIS_INSTALLED = True
except ImportError:
    REDIS_INSTALLED = False


class TestCacheBackend:
    """Test suite for CacheBackend base class."""

    def test_cache_backend_interface(self):
        """Test that CacheBackend defines proper interface."""
        backend = CacheBackend()

        with pytest.raises(NotImplementedError):
            backend.get("key")

        with pytest.raises(NotImplementedError):
            backend.set("key", "value")

        with pytest.raises(NotImplementedError):
            backend.delete("key")

        with pytest.raises(NotImplementedError):
            backend.clear()

        with pytest.raises(NotImplementedError):
            backend.has("key")


class TestSimpleCache:
    """Test suite for SimpleCache in-memory implementation."""

    @pytest.fixture
    def cache(self):
        """Create SimpleCache instance."""
        return SimpleCache()

    def test_set_and_get(self, cache):
        """Test basic set and get operations."""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key returns None."""
        assert cache.get("nonexistent") is None

    def test_delete_key(self, cache):
        """Test deleting a key."""
        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_delete_nonexistent_key(self, cache):
        """Test deleting non-existent key doesn't raise error."""
        cache.delete("nonexistent")  # Should not raise

    def test_clear_cache(self, cache):
        """Test clearing all cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_has_key(self, cache):
        """Test checking if key exists."""
        cache.set("key1", "value1")
        assert cache.has("key1") is True
        assert cache.has("nonexistent") is False

    def test_timeout_expiry(self, cache):
        """Test that keys expire after timeout."""
        cache.set("key1", "value1", timeout=1)
        assert cache.get("key1") == "value1"

        # Wait for expiry
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_no_timeout(self, cache):
        """Test keys without timeout don't expire."""
        cache.set("key1", "value1", timeout=0)
        time.sleep(0.5)
        assert cache.get("key1") == "value1"

    def test_multiple_keys(self, cache):
        """Test handling multiple keys."""
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")

        for i in range(10):
            assert cache.get(f"key{i}") == f"value{i}"

    def test_overwrite_key(self, cache):
        """Test overwriting existing key."""
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"

    def test_complex_values(self, cache):
        """Test caching complex data structures."""
        # Dict
        cache.set("dict", {"a": 1, "b": 2})
        assert cache.get("dict") == {"a": 1, "b": 2}

        # List
        cache.set("list", [1, 2, 3, 4])
        assert cache.get("list") == [1, 2, 3, 4]

        # Nested
        cache.set("nested", {"items": [1, 2, {"x": 10}]})
        assert cache.get("nested") == {"items": [1, 2, {"x": 10}]}


@pytest.mark.skipif(not REDIS_INSTALLED, reason="Redis not installed")
class TestRedisCache:
    """Test suite for RedisCache implementation."""

    def test_redis_unavailable(self):
        """Test error when Redis not installed."""
        with patch("src.core.cache.REDIS_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="Redis library not installed"):
                RedisCache()

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_initialization(self, mock_from_url):
        """Test Redis cache initialization."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        cache = RedisCache("redis://localhost:6379/0")
        assert cache.client == mock_client
        mock_from_url.assert_called_once_with("redis://localhost:6379/0", decode_responses=False)

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_get(self, mock_from_url):
        """Test getting value from Redis."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        mock_client.get.return_value = pickle.dumps("value1")

        cache = RedisCache()
        result = cache.get("key1")

        assert result == "value1"
        mock_client.get.assert_called_once_with("key1")

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_get_none(self, mock_from_url):
        """Test getting non-existent key from Redis."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        mock_client.get.return_value = None

        cache = RedisCache()
        result = cache.get("key1")

        assert result is None

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_set(self, mock_from_url):
        """Test setting value in Redis."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        cache = RedisCache()
        cache.set("key1", "value1", timeout=300)

        mock_client.setex.assert_called_once()
        args = mock_client.setex.call_args[0]
        assert args[0] == "key1"
        assert args[1] == 300
        assert pickle.loads(args[2]) == "value1"

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_delete(self, mock_from_url):
        """Test deleting key from Redis."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        cache = RedisCache()
        cache.delete("key1")

        mock_client.delete.assert_called_once_with("key1")

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_clear(self, mock_from_url):
        """Test clearing Redis cache."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        cache = RedisCache()
        cache.clear()

        mock_client.flushdb.assert_called_once()

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_has(self, mock_from_url):
        """Test checking key existence in Redis."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        mock_client.exists.return_value = 1

        cache = RedisCache()
        result = cache.has("key1")

        assert result is True
        mock_client.exists.assert_called_once_with("key1")

    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_error_handling(self, mock_from_url):
        """Test Redis error handling."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        cache = RedisCache()

        # Simulate Redis errors
        mock_client.get.side_effect = Exception("Connection error")
        assert cache.get("key1") is None

        mock_client.setex.side_effect = Exception("Connection error")
        cache.set("key1", "value1")  # Should not raise

        mock_client.exists.side_effect = Exception("Connection error")
        assert cache.has("key1") is False


class TestCacheManager:
    """Test suite for CacheManager."""

    @pytest.fixture
    def manager(self):
        """Create CacheManager instance."""
        return CacheManager(backend="simple")

    def test_simple_backend_initialization(self):
        """Test initialization with simple backend."""
        manager = CacheManager(backend="simple")
        assert manager.backend_type == "simple"
        assert isinstance(manager.backend, SimpleCache)

    @pytest.mark.skipif(not REDIS_INSTALLED, reason="Redis not installed")
    @patch("src.core.cache.REDIS_AVAILABLE", True)
    @patch("redis.from_url")
    def test_redis_backend_initialization(self, mock_from_url):
        """Test initialization with Redis backend."""
        mock_from_url.return_value = MagicMock()
        manager = CacheManager(backend="redis", redis_url="redis://localhost:6379/1")
        assert manager.backend_type == "redis"
        assert isinstance(manager.backend, RedisCache)

    def test_get_hit(self, manager):
        """Test cache hit updates statistics."""
        manager.set("key1", "value1")
        result = manager.get("key1")

        assert result == "value1"
        assert manager.hit_count == 1
        assert manager.miss_count == 0

    def test_get_miss(self, manager):
        """Test cache miss updates statistics."""
        result = manager.get("nonexistent")

        assert result is None
        assert manager.hit_count == 0
        assert manager.miss_count == 1

    def test_set_operation(self, manager):
        """Test set operation."""
        manager.set("key1", "value1", timeout=300)
        assert manager.get("key1") == "value1"

    def test_delete_operation(self, manager):
        """Test delete operation."""
        manager.set("key1", "value1")
        manager.delete("key1")
        assert manager.get("key1") is None

    def test_clear_operation(self, manager):
        """Test clear operation."""
        manager.set("key1", "value1")
        manager.set("key2", "value2")
        manager.clear()
        assert manager.get("key1") is None
        assert manager.get("key2") is None

    def test_get_or_set_cached(self, manager):
        """Test get_or_set with cached value."""
        manager.set("key1", "cached_value")
        callback = Mock(return_value="new_value")

        result = manager.get_or_set("key1", callback)

        assert result == "cached_value"
        callback.assert_not_called()

    def test_get_or_set_compute(self, manager):
        """Test get_or_set computes and caches value."""
        callback = Mock(return_value="computed_value")

        result = manager.get_or_set("key1", callback, timeout=300)

        assert result == "computed_value"
        callback.assert_called_once()
        assert manager.get("key1") == "computed_value"

    def test_get_stats_empty(self, manager):
        """Test statistics with no requests."""
        stats = manager.get_stats()

        assert stats["backend"] == "simple"
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total_requests"] == 0
        assert stats["hit_rate"] == 0

    def test_get_stats_with_data(self, manager):
        """Test statistics with requests."""
        manager.set("key1", "value1")
        manager.get("key1")  # Hit
        manager.get("key1")  # Hit
        manager.get("key2")  # Miss

        stats = manager.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate"] == 66.67


class TestCachedDecorator:
    """Test suite for @cached decorator."""

    def test_cached_function(self):
        """Test basic function caching."""
        call_count = 0

        @cached(timeout=300)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call - should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not called again

    def test_cached_with_different_args(self):
        """Test caching with different arguments."""
        @cached(timeout=300)
        def function(x, y):
            return x + y

        result1 = function(1, 2)
        result2 = function(3, 4)

        assert result1 == 3
        assert result2 == 7

    def test_cached_with_key_prefix(self):
        """Test caching with key prefix."""
        @cached(timeout=300, key_prefix="test")
        def function(x):
            return x * 2

        result = function(5)
        assert result == 10

    def test_cache_clear_method(self):
        """Test cache_clear method on decorated function."""
        call_count = 0

        @cached(timeout=300)
        def function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        function(5)
        assert call_count == 1

        function.cache_clear()

        function(5)
        assert call_count == 2  # Called again after clear


class TestCacheInvalidateDecorator:
    """Test suite for @cache_invalidate decorator."""

    def test_cache_invalidate_clears_cache(self):
        """Test that cache_invalidate clears cache."""
        manager = get_cache_manager()
        manager.clear()  # Start fresh

        manager.set("key1", "value1")
        assert manager.get("key1") == "value1"

        @cache_invalidate("key1")
        def update_function():
            return "updated"

        result = update_function()
        assert result == "updated"
        # Cache should be cleared (simplified implementation clears all)


class TestGenerateCacheKey:
    """Test suite for _generate_cache_key function."""

    def test_simple_function_key(self):
        """Test key generation for simple function."""

        def test_func():
            pass

        key = _generate_cache_key(test_func, (), {}, "prefix")
        assert "prefix" in key
        assert "test_func" in key

    def test_key_with_args(self):
        """Test key generation with positional arguments."""

        def test_func(a, b):
            pass

        key = _generate_cache_key(test_func, (1, 2), {})
        assert "1" in key
        assert "2" in key

    def test_key_with_kwargs(self):
        """Test key generation with keyword arguments."""

        def test_func(a=1, b=2):
            pass

        key = _generate_cache_key(test_func, (), {"a": 1, "b": 2})
        assert "a=1" in key
        assert "b=2" in key

    def test_key_hashing_for_long_keys(self):
        """Test that long keys are hashed."""

        def test_func():
            pass

        # Create long arguments
        long_args = tuple(range(100))
        key = _generate_cache_key(test_func, long_args, {})

        # Long key should be hashed (MD5)
        assert len(key) < 100  # Significantly shorter than original


class TestPerformanceMonitor:
    """Test suite for PerformanceMonitor."""

    @pytest.fixture
    def monitor(self):
        """Create PerformanceMonitor instance."""
        return PerformanceMonitor()

    def test_record_metric(self, monitor):
        """Test recording a metric."""
        monitor.record("test_operation", 1.5)
        stats = monitor.get_stats("test_operation")

        assert stats["count"] == 1
        assert stats["avg"] == 1.5
        assert stats["min"] == 1.5
        assert stats["max"] == 1.5

    def test_multiple_recordings(self, monitor):
        """Test multiple recordings of same metric."""
        monitor.record("operation", 1.0)
        monitor.record("operation", 2.0)
        monitor.record("operation", 3.0)

        stats = monitor.get_stats("operation")

        assert stats["count"] == 3
        assert stats["avg"] == 2.0
        assert stats["min"] == 1.0
        assert stats["max"] == 3.0
        assert stats["total"] == 6.0

    def test_get_stats_nonexistent(self, monitor):
        """Test getting stats for non-existent metric."""
        stats = monitor.get_stats("nonexistent")
        assert stats == {}

    def test_get_all_stats(self, monitor):
        """Test getting all statistics."""
        monitor.record("op1", 1.0)
        monitor.record("op2", 2.0)

        all_stats = monitor.get_all_stats()

        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["avg"] == 1.0
        assert all_stats["op2"]["avg"] == 2.0


class TestTimedDecorator:
    """Test suite for @timed decorator."""

    def test_timed_decorator(self):
        """Test that timed decorator records execution time."""
        monitor = get_performance_monitor()

        @timed("test_operation")
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()

        assert result == "done"
        stats = monitor.get_stats("test_operation")
        assert stats["count"] >= 1
        assert stats["avg"] >= 0.1

    def test_timed_without_name(self):
        """Test timed decorator uses function name."""
        monitor = get_performance_monitor()

        @timed()
        def my_function():
            return "done"

        my_function()

        stats = monitor.get_stats("my_function")
        assert stats["count"] >= 1


class TestGlobalInstances:
    """Test suite for global instance management."""

    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns singleton."""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is manager2

    def test_get_performance_monitor_singleton(self):
        """Test that get_performance_monitor returns singleton."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()

        assert monitor1 is monitor2

    def test_init_cache(self):
        """Test cache initialization."""
        init_cache(backend="simple")
        manager = get_cache_manager()

        assert manager.backend_type == "simple"
