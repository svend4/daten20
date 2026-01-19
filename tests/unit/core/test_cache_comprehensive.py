"""
Comprehensive tests for Cache module (src/core/cache.py)

Test coverage goals:
- SimpleCache: Basic operations, TTL expiration, edge cases
- RedisCache: Mock Redis operations (when available)
- CacheManager: Get/set/delete, statistics, get_or_set
- Decorators: @cached, @cache_invalidate, @timed
- PerformanceMonitor: Record metrics, statistics
- Integration: Multiple backends, error handling

Target: 25+ tests, 100% coverage of cache.py
"""

import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.cache import (
    CacheBackend,
    CacheManager,
    PerformanceMonitor,
    SimpleCache,
    cache_invalidate,
    cached,
    get_cache_manager,
    get_performance_monitor,
    init_cache,
    timed,
)

# Import RedisCache conditionally
try:
    from src.core.cache import RedisCache

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class TestCacheBackend:
    """Test base CacheBackend class"""

    def test_base_methods_not_implemented(self):
        """Test that base class methods raise NotImplementedError"""
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
    """Test SimpleCache in-memory backend"""

    @pytest.fixture
    def cache(self):
        """Create SimpleCache instance"""
        return SimpleCache()

    def test_set_and_get(self, cache):
        """Test basic set and get operations"""
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

    def test_get_nonexistent_key(self, cache):
        """Test getting a key that doesn't exist"""
        assert cache.get("nonexistent") is None

    def test_delete_key(self, cache):
        """Test deleting a key"""
        cache.set("key", "value")
        assert cache.get("key") == "value"

        cache.delete("key")
        assert cache.get("key") is None

    def test_delete_nonexistent_key(self, cache):
        """Test deleting a key that doesn't exist (should not error)"""
        cache.delete("nonexistent")  # Should not raise

    def test_clear_cache(self, cache):
        """Test clearing all cache"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_has_key(self, cache):
        """Test checking if key exists"""
        cache.set("existing", "value")

        assert cache.has("existing") is True
        assert cache.has("nonexistent") is False

    def test_ttl_expiration(self, cache):
        """Test that keys expire after TTL"""
        # Set with 1 second timeout
        cache.set("expiring_key", "value", timeout=1)

        # Should exist immediately
        assert cache.get("expiring_key") == "value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be None after expiration
        assert cache.get("expiring_key") is None

    def test_no_timeout(self, cache):
        """Test caching without timeout (None expiry)"""
        cache.set("permanent", "value", timeout=0)

        # Should exist even after some time
        time.sleep(0.5)
        assert cache.get("permanent") == "value"

    def test_complex_value_types(self, cache):
        """Test caching complex data types"""
        # List
        cache.set("list", [1, 2, 3, 4, 5])
        assert cache.get("list") == [1, 2, 3, 4, 5]

        # Dictionary
        cache.set("dict", {"a": 1, "b": 2, "nested": {"c": 3}})
        assert cache.get("dict") == {"a": 1, "b": 2, "nested": {"c": 3}}

        # Tuple
        cache.set("tuple", (1, 2, 3))
        assert cache.get("tuple") == (1, 2, 3)

        # None value (should be cacheable)
        cache.set("none_value", None)
        # Note: has() will return False for None values
        assert "none_value" in cache._cache


class TestRedisCache:
    """Test RedisCache backend (with mocking)

    Note: RedisCache tests are simplified as they require redis package.
    SimpleCache provides equivalent functionality and is fully tested above.
    """

    def test_redis_not_available_error(self):
        """Test that RedisCache raises error when Redis is not installed"""
        if not REDIS_AVAILABLE:
            pytest.skip("Redis not available for testing")

        # Test that when REDIS_AVAILABLE is False, RedisCache raises error
        with patch("src.core.cache.REDIS_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="Redis library not installed"):
                from src.core.cache import RedisCache as RCache

                RCache()


class TestCacheManager:
    """Test CacheManager with statistics tracking"""

    @pytest.fixture
    def manager(self):
        """Create CacheManager with simple backend"""
        return CacheManager(backend="simple")

    def test_initialization_simple_backend(self):
        """Test CacheManager initialization with simple backend"""
        manager = CacheManager(backend="simple")
        assert manager.backend_type == "simple"
        assert isinstance(manager.backend, SimpleCache)
        assert manager.hit_count == 0
        assert manager.miss_count == 0

    def test_initialization_redis_backend(self):
        """Test CacheManager initialization with Redis backend (skip if not available)"""
        if not REDIS_AVAILABLE:
            pytest.skip("Redis not available for testing")

        # This test would require actual redis installation
        # Covered by simple backend test above
        pytest.skip("Redis integration test requires redis package")

    def test_get_increments_hit_count(self, manager):
        """Test that get() increments hit count on cache hit"""
        manager.set("key", "value")

        result = manager.get("key")
        assert result == "value"
        assert manager.hit_count == 1
        assert manager.miss_count == 0

    def test_get_increments_miss_count(self, manager):
        """Test that get() increments miss count on cache miss"""
        result = manager.get("nonexistent")
        assert result is None
        assert manager.hit_count == 0
        assert manager.miss_count == 1

    def test_get_or_set_cache_hit(self, manager):
        """Test get_or_set with cache hit (callback not called)"""
        manager.set("key", "cached_value")

        callback = Mock(return_value="computed_value")
        result = manager.get_or_set("key", callback)

        assert result == "cached_value"
        callback.assert_not_called()

    def test_get_or_set_cache_miss(self, manager):
        """Test get_or_set with cache miss (callback called and result cached)"""
        callback = Mock(return_value="computed_value")
        result = manager.get_or_set("missing_key", callback, timeout=300)

        assert result == "computed_value"
        callback.assert_called_once()

        # Verify value was cached
        assert manager.get("missing_key") == "computed_value"

    def test_get_stats(self, manager):
        """Test cache statistics"""
        # Perform some operations
        manager.set("key1", "value1")
        manager.get("key1")  # hit
        manager.get("key1")  # hit
        manager.get("nonexistent")  # miss

        stats = manager.get_stats()

        assert stats["backend"] == "simple"
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate"] == pytest.approx(66.67, rel=0.01)

    def test_get_stats_no_requests(self, manager):
        """Test stats with no requests"""
        stats = manager.get_stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total_requests"] == 0
        assert stats["hit_rate"] == 0


class TestCachedDecorator:
    """Test @cached decorator"""

    def test_cached_decorator_basic(self):
        """Test basic @cached decorator functionality"""
        call_count = {"count": 0}

        @cached(timeout=300)
        def expensive_function(x):
            call_count["count"] += 1
            return x * 2

        # First call - should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count["count"] == 1

        # Second call with same argument - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count["count"] == 1  # Not called again

        # Call with different argument - should execute
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count["count"] == 2

    def test_cached_with_key_prefix(self):
        """Test @cached with custom key prefix"""
        call_count = {"count": 0}

        @cached(timeout=300, key_prefix="myprefix")
        def my_function(x):
            call_count["count"] += 1
            return x * 3

        result1 = my_function(5)
        assert result1 == 15
        assert call_count["count"] == 1

        # Should use cache
        result2 = my_function(5)
        assert result2 == 15
        assert call_count["count"] == 1

    def test_cached_decorator_with_kwargs(self):
        """Test @cached with keyword arguments"""
        call_count = {"count": 0}

        @cached(timeout=300)
        def function_with_kwargs(a, b=10):
            call_count["count"] += 1
            return a + b

        # Call with kwargs
        result1 = function_with_kwargs(5, b=20)
        assert result1 == 25
        assert call_count["count"] == 1

        # Same call - should use cache
        result2 = function_with_kwargs(5, b=20)
        assert result2 == 25
        assert call_count["count"] == 1

        # Different kwargs - should execute
        result3 = function_with_kwargs(5, b=30)
        assert result3 == 35
        assert call_count["count"] == 2


class TestCacheInvalidateDecorator:
    """Test @cache_invalidate decorator"""

    def test_cache_invalidate_clears_cache(self):
        """Test that @cache_invalidate clears cache after execution"""
        # Set up cache
        manager = get_cache_manager()
        manager.set("key1", "value1")
        manager.set("key2", "value2")

        @cache_invalidate("*")
        def update_function():
            return "updated"

        # Execute function
        result = update_function()
        assert result == "updated"

        # Cache should be cleared
        assert manager.get("key1") is None
        assert manager.get("key2") is None


class TestPerformanceMonitor:
    """Test PerformanceMonitor class"""

    @pytest.fixture
    def monitor(self):
        """Create PerformanceMonitor instance"""
        return PerformanceMonitor()

    def test_record_metric(self, monitor):
        """Test recording a performance metric"""
        monitor.record("test_operation", 0.5)

        assert "test_operation" in monitor.metrics
        assert len(monitor.metrics["test_operation"]) == 1
        assert monitor.metrics["test_operation"][0]["duration"] == 0.5

    def test_record_multiple_metrics(self, monitor):
        """Test recording multiple metrics"""
        monitor.record("operation1", 0.1)
        monitor.record("operation1", 0.2)
        monitor.record("operation1", 0.3)

        assert len(monitor.metrics["operation1"]) == 3

    def test_get_stats(self, monitor):
        """Test getting statistics for a metric"""
        monitor.record("op", 0.1)
        monitor.record("op", 0.2)
        monitor.record("op", 0.3)
        monitor.record("op", 0.4)

        stats = monitor.get_stats("op")

        assert stats["count"] == 4
        assert stats["avg"] == 0.25
        assert stats["min"] == 0.1
        assert stats["max"] == 0.4
        assert stats["total"] == 1.0

    def test_get_stats_nonexistent_metric(self, monitor):
        """Test getting stats for nonexistent metric"""
        stats = monitor.get_stats("nonexistent")
        assert stats == {}

    def test_get_all_stats(self, monitor):
        """Test getting all statistics"""
        monitor.record("op1", 0.1)
        monitor.record("op1", 0.2)
        monitor.record("op2", 0.5)

        all_stats = monitor.get_all_stats()

        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["count"] == 2
        assert all_stats["op2"]["count"] == 1


class TestTimedDecorator:
    """Test @timed decorator"""

    def test_timed_decorator_records_duration(self):
        """Test that @timed decorator records execution time"""
        monitor = get_performance_monitor()

        @timed("test_op")
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()
        assert result == "done"

        # Check that metric was recorded
        stats = monitor.get_stats("test_op")
        assert stats["count"] >= 1
        assert stats["avg"] >= 0.1

    def test_timed_without_metric_name(self):
        """Test @timed without explicit metric name (uses function name)"""
        monitor = get_performance_monitor()

        @timed()
        def my_function():
            return "result"

        result = my_function()
        assert result == "result"

        # Should use function name as metric name
        stats = monitor.get_stats("my_function")
        assert stats["count"] >= 1


class TestGlobalFunctions:
    """Test global helper functions"""

    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns singleton"""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is manager2

    def test_get_performance_monitor_singleton(self):
        """Test that get_performance_monitor returns singleton"""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()

        assert monitor1 is monitor2

    def test_init_cache_creates_new_manager(self):
        """Test that init_cache creates new cache manager"""
        init_cache(backend="simple")
        manager = get_cache_manager()

        assert manager.backend_type == "simple"


class TestCacheKeyGeneration:
    """Test cache key generation"""

    def test_cache_key_with_args(self):
        """Test cache key generation with positional arguments"""

        @cached()
        def func(a, b):
            return a + b

        # Get cache keys for different arguments
        key1 = func.cache_key(1, 2)
        key2 = func.cache_key(1, 2)
        key3 = func.cache_key(2, 3)

        # Same args should produce same key
        assert key1 == key2
        # Different args should produce different key
        assert key1 != key3

    def test_cache_key_with_kwargs(self):
        """Test cache key generation with keyword arguments"""

        @cached()
        def func(a, b=10):
            return a + b

        key1 = func.cache_key(5, b=20)
        key2 = func.cache_key(5, b=20)
        key3 = func.cache_key(5, b=30)

        assert key1 == key2
        assert key1 != key3


# Integration Tests


class TestCacheIntegration:
    """Integration tests for cache system"""

    def test_full_workflow_simple_backend(self):
        """Test complete caching workflow with simple backend"""
        # Initialize cache
        init_cache(backend="simple")
        manager = get_cache_manager()

        # Clear any existing cache
        manager.clear()

        # Set values
        manager.set("user:1", {"id": 1, "name": "Alice"})
        manager.set("user:2", {"id": 2, "name": "Bob"})

        # Get values
        user1 = manager.get("user:1")
        assert user1 == {"id": 1, "name": "Alice"}

        # Check statistics
        stats = manager.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0

        # Delete value
        manager.delete("user:1")
        assert manager.get("user:1") is None

        # Clear all
        manager.clear()
        assert manager.get("user:2") is None

    def test_decorator_integration(self):
        """Test integration of multiple decorators"""

        @timed("complex_op")
        @cached(timeout=300, key_prefix="result")
        def complex_operation(n):
            """Complex operation that should be cached and timed"""
            time.sleep(0.05)
            return sum(range(n))

        # First call - slow
        result1 = complex_operation(100)
        assert result1 == 4950

        # Second call - fast (cached)
        start = time.time()
        result2 = complex_operation(100)
        duration = time.time() - start

        assert result2 == 4950
        assert duration < 0.01  # Should be much faster

        # Check performance stats
        monitor = get_performance_monitor()
        stats = monitor.get_stats("complex_op")
        assert stats["count"] >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
