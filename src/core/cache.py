"""
Caching and Performance Optimization Module

Provides caching mechanisms, query optimization, and performance monitoring.
Supports multiple backends: Simple (in-memory), Redis, and Memcached.
"""

import hashlib
import logging
import pickle
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger("dms.cache")


class CacheBackend:
    """Base class for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError

    def set(self, key: str, value: Any, timeout: int = 300):
        """Set value in cache with optional timeout."""
        raise NotImplementedError

    def delete(self, key: str):
        """Delete key from cache."""
        raise NotImplementedError

    def clear(self):
        """Clear all cache."""
        raise NotImplementedError

    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError


class SimpleCache(CacheBackend):
    """Simple in-memory cache implementation."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key: (value, expiry_time)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        # Check expiry
        if expiry and datetime.now() > expiry:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, timeout: int = 300):
        """Set value in cache."""
        expiry = datetime.now() + timedelta(seconds=timeout) if timeout else None
        self._cache[key] = (value, expiry)

    def delete(self, key: str):
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Clear all cache."""
        self._cache.clear()

    def has(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None


class RedisCache(CacheBackend):
    """Redis-based cache implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
        """
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis library not installed. Install with: pip install redis")

        self.client = redis.from_url(redis_url, decode_responses=False)
        logger.info(f"Connected to Redis: {redis_url}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, timeout: int = 300):
        """Set value in Redis."""
        try:
            serialized = pickle.dumps(value)
            self.client.setex(key, timeout, serialized)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")

    def delete(self, key: str):
        """Delete key from Redis."""
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")

    def clear(self):
        """Clear all Redis cache."""
        try:
            self.client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

    def has(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False


class CacheManager:
    """Manage caching with multiple backends."""

    def __init__(self, backend: str = "simple", **kwargs):
        """
        Initialize cache manager.

        Args:
            backend: Cache backend type ('simple', 'redis')
            **kwargs: Additional arguments for backend
        """
        self.backend_type = backend

        if backend == "redis":
            redis_url = kwargs.get("redis_url", "redis://localhost:6379/0")
            self.backend = RedisCache(redis_url)
        else:
            self.backend = SimpleCache()

        self.hit_count = 0
        self.miss_count = 0

        logger.info(f"Cache manager initialized with {backend} backend")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.backend.get(key)

        if value is not None:
            self.hit_count += 1
            logger.debug(f"Cache HIT: {key}")
        else:
            self.miss_count += 1
            logger.debug(f"Cache MISS: {key}")

        return value

    def set(self, key: str, value: Any, timeout: int = 300):
        """Set value in cache."""
        self.backend.set(key, value, timeout)
        logger.debug(f"Cache SET: {key} (timeout={timeout}s)")

    def delete(self, key: str):
        """Delete key from cache."""
        self.backend.delete(key)
        logger.debug(f"Cache DELETE: {key}")

    def clear(self):
        """Clear all cache."""
        self.backend.clear()
        logger.info("Cache cleared")

    def get_or_set(self, key: str, callback: Callable, timeout: int = 300) -> Any:
        """
        Get value from cache or compute and cache it.

        Args:
            key: Cache key
            callback: Function to compute value if not cached
            timeout: Cache timeout in seconds

        Returns:
            Cached or computed value
        """
        value = self.get(key)

        if value is None:
            value = callback()
            self.set(key, value, timeout)

        return value

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0

        return {
            "backend": self.backend_type,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "total_requests": total,
            "hit_rate": round(hit_rate, 2),
        }


# Caching decorators


def cached(timeout: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key

    Example:
        @cached(timeout=600, key_prefix='user')
        def get_user(user_id):
            return User.query.get(user_id)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)

            # Try to get from cache
            cache = get_cache_manager()
            result = cache.get(cache_key)

            if result is not None:
                return result

            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)

            return result

        # Add cache control methods
        wrapper.cache_clear = lambda: get_cache_manager().clear()
        wrapper.cache_key = lambda *args, **kwargs: _generate_cache_key(func, args, kwargs, key_prefix)

        return wrapper

    return decorator


def cache_invalidate(key_pattern: str):
    """
    Decorator to invalidate cache after function execution.

    Args:
        key_pattern: Pattern of cache keys to invalidate

    Example:
        @cache_invalidate('user:*')
        def update_user(user_id, data):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate matching cache keys
            cache = get_cache_manager()
            # Simple implementation - clear all for now
            # In production, implement pattern matching
            cache.clear()

            return result

        return wrapper

    return decorator


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """
    Generate cache key from function and arguments.

    Args:
        func: Function object
        args: Positional arguments
        kwargs: Keyword arguments
        prefix: Key prefix

    Returns:
        Cache key string
    """
    # Build key from function name and arguments
    key_parts = [prefix, func.__module__, func.__name__]

    # Add args
    for arg in args:
        key_parts.append(str(arg))

    # Add sorted kwargs
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    key_string = ":".join(key_parts)

    # Hash if too long
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    return key_string


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        self.metrics: Dict[str, list] = {}

    def record(self, name: str, duration: float):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append({"duration": duration, "timestamp": datetime.now()})

    def get_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}

        durations = [m["duration"] for m in self.metrics[name]]

        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "total": sum(durations),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all metrics."""
        return {name: self.get_stats(name) for name in self.metrics}


def timed(metric_name: Optional[str] = None):
    """
    Decorator to measure function execution time.

    Args:
        metric_name: Name for the metric (uses function name if None)

    Example:
        @timed('database_query')
        def query_database():
            ...
    """

    def decorator(func):
        name = metric_name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor = get_performance_monitor()
                monitor.record(name, duration)

                if duration > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation: {name} took {duration:.2f}s")

        return wrapper

    return decorator


# Global instances
_cache_manager: Optional[CacheManager] = None
_performance_monitor: Optional[PerformanceMonitor] = None


def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def init_cache(backend: str = "simple", **kwargs):
    """
    Initialize cache system.

    Args:
        backend: Cache backend type
        **kwargs: Additional backend arguments
    """
    global _cache_manager
    _cache_manager = CacheManager(backend, **kwargs)
    logger.info(f"Cache system initialized: {backend}")


# Alias for backward compatibility
CacheService = CacheManager
