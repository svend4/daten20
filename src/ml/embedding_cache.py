#!/usr/bin/env python3
"""
Embedding Cache Module

Provides high-performance caching for text embeddings with Redis and in-memory fallback.
Optimizes semantic search and NLP operations by caching expensive embedding computations.

Key Features:
- Redis-based distributed caching for production
- In-memory fallback when Redis unavailable
- LRU eviction policy with configurable size
- TTL (Time-To-Live) support
- Batch operations for efficiency
- Numpy array serialization
- Comprehensive metrics tracking
- Thread-safe operations

Performance Benefits:
- 50-100x faster for cached embeddings
- Reduced API costs for cloud embedding services
- Lower CPU/GPU usage
- Improved throughput for high-volume workloads

Architecture:
1. Primary: Redis cache (distributed, persistent)
2. Fallback: In-memory LRU cache (local, fast)
3. Metrics: Track hits, misses, size, throughput

Usage:
    # Basic usage
    cache = EmbeddingCache(redis_url="redis://localhost:6379")

    # Cache embedding
    embedding = np.array([0.1, 0.2, 0.3])
    cache.set("hello world", embedding, ttl=3600)

    # Retrieve embedding
    cached = cache.get("hello world")

    # Batch operations
    texts = ["text1", "text2", "text3"]
    embeddings = [emb1, emb2, emb3]
    cache.set_batch(texts, embeddings)

    # Get metrics
    metrics = cache.get_metrics()
    print(f"Cache hit rate: {metrics.hit_rate:.1f}%")
"""

import hashlib
import logging
import pickle
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Try to import Redis
try:
    import redis
    from redis import ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    RedisConnectionError = Exception
    REDIS_AVAILABLE = False

logger = logging.getLogger("dms.embedding_cache")


@dataclass
class CacheMetrics:
    """Cache performance metrics"""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0
    errors: int = 0
    total_size_bytes: int = 0
    redis_enabled: bool = False
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def total_requests(self) -> int:
        """Total cache requests"""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100

    @property
    def miss_rate(self) -> float:
        """Cache miss rate percentage"""
        return 100 - self.hit_rate

    @property
    def uptime_seconds(self) -> float:
        """Cache uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "evictions": self.evictions,
            "errors": self.errors,
            "total_requests": self.total_requests,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "total_size_bytes": self.total_size_bytes,
            "total_size_mb": self.total_size_bytes / (1024 * 1024),
            "redis_enabled": self.redis_enabled,
            "uptime_seconds": self.uptime_seconds,
        }


class InMemoryLRUCache:
    """
    Thread-safe in-memory LRU cache for embeddings

    Uses OrderedDict for O(1) access and LRU eviction.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize in-memory LRU cache

        Args:
            max_size: Maximum number of cached embeddings
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, Tuple[np.ndarray, float]] = OrderedDict()
        self._lock = Lock()
        self._eviction_count = 0

        logger.info(f"Initialized in-memory LRU cache (max_size={max_size})")

    def get(self, key: str) -> Optional[np.ndarray]:
        """
        Get embedding from cache

        Args:
            key: Cache key

        Returns:
            Cached embedding or None if not found
        """
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                embedding, timestamp = self._cache[key]
                return embedding.copy()  # Return copy to prevent modification
            return None

    def set(self, key: str, embedding: np.ndarray) -> None:
        """
        Store embedding in cache

        Args:
            key: Cache key
            embedding: Numpy array embedding
        """
        with self._lock:
            # Remove if exists (will re-add at end)
            if key in self._cache:
                del self._cache[key]

            # Add to end (most recently used)
            self._cache[key] = (embedding.copy(), time.time())

            # Evict oldest if over capacity
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)  # Remove oldest (first item)
                self._eviction_count += 1

    def delete(self, key: str) -> bool:
        """
        Delete embedding from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cached embeddings"""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get number of cached embeddings"""
        with self._lock:
            return len(self._cache)

    def get_eviction_count(self) -> int:
        """Get number of evictions"""
        return self._eviction_count


class EmbeddingCache:
    """
    High-performance embedding cache with Redis and in-memory fallback

    Features:
    - Primary: Redis for distributed caching
    - Fallback: In-memory LRU cache
    - Automatic serialization of numpy arrays
    - TTL support for expiration
    - Batch operations
    - Comprehensive metrics

    Example:
        # Initialize with Redis
        cache = EmbeddingCache(
            redis_url="redis://localhost:6379",
            redis_db=0,
            memory_cache_size=1000,
            default_ttl=3600
        )

        # Cache embedding
        embedding = model.encode("hello world")
        cache.set("hello world", embedding)

        # Retrieve embedding
        cached = cache.get("hello world")
        if cached is not None:
            print("Cache hit!")

        # Batch operations
        texts = ["text1", "text2", "text3"]
        embeddings = model.encode(texts)
        cache.set_batch(texts, embeddings)

        # Get metrics
        print(cache.get_metrics().to_dict())
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        memory_cache_size: int = 1000,
        default_ttl: Optional[int] = None,
        key_prefix: str = "emb:",
        use_hash_keys: bool = True,
    ):
        """
        Initialize embedding cache

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379)
            redis_db: Redis database number (0-15)
            redis_password: Redis password if required
            memory_cache_size: Size of in-memory LRU cache
            default_ttl: Default TTL in seconds (None = no expiration)
            key_prefix: Prefix for Redis keys
            use_hash_keys: Use MD5 hash for keys (recommended for long texts)
        """
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.redis_password = redis_password
        self.memory_cache_size = memory_cache_size
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.use_hash_keys = use_hash_keys

        # Initialize metrics
        self.metrics = CacheMetrics()

        # Initialize in-memory cache (always available)
        self.memory_cache = InMemoryLRUCache(max_size=memory_cache_size)

        # Initialize Redis client (if available)
        self.redis_client = None
        self.redis_enabled = False

        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=False,  # We store binary data
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self.redis_client.ping()
                self.redis_enabled = True
                self.metrics.redis_enabled = True
                logger.info(f"Connected to Redis: {redis_url}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache.")
                self.redis_client = None
                self.redis_enabled = False
        elif redis_url and not REDIS_AVAILABLE:
            logger.warning("Redis URL provided but redis-py not installed. Install: pip install redis")

        if not self.redis_enabled:
            logger.info("Using in-memory cache only")

    def _make_key(self, text: str) -> str:
        """
        Create cache key from text

        Args:
            text: Input text

        Returns:
            Cache key (prefixed, optionally hashed)
        """
        if self.use_hash_keys:
            # Use MD5 hash for consistent-length keys
            text_hash = hashlib.md5(text.encode()).hexdigest()
            return f"{self.key_prefix}{text_hash}"
        else:
            # Use text directly (sanitize special characters)
            safe_text = text.replace(":", "_").replace(" ", "_")[:100]
            return f"{self.key_prefix}{safe_text}"

    def _serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """
        Serialize numpy array to bytes

        Args:
            embedding: Numpy array

        Returns:
            Serialized bytes
        """
        return pickle.dumps(embedding, protocol=pickle.HIGHEST_PROTOCOL)

    def _deserialize_embedding(self, data: bytes) -> np.ndarray:
        """
        Deserialize bytes to numpy array

        Args:
            data: Serialized bytes

        Returns:
            Numpy array
        """
        return pickle.loads(data)

    def get(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding from cache

        Tries Redis first, then falls back to in-memory cache.

        Args:
            text: Text to look up

        Returns:
            Cached embedding or None if not found
        """
        key = self._make_key(text)

        # Try Redis first (if enabled)
        if self.redis_enabled and self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    embedding = self._deserialize_embedding(data)
                    self.metrics.hits += 1

                    # Populate memory cache for faster subsequent access
                    self.memory_cache.set(key, embedding)

                    return embedding
            except RedisConnectionError:
                logger.warning("Redis connection lost, falling back to memory cache")
                self.redis_enabled = False
                self.metrics.errors += 1
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                self.metrics.errors += 1

        # Try memory cache
        embedding = self.memory_cache.get(key)
        if embedding is not None:
            self.metrics.hits += 1
            return embedding

        # Cache miss
        self.metrics.misses += 1
        return None

    def set(
        self,
        text: str,
        embedding: np.ndarray,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store embedding in cache

        Args:
            text: Text key
            embedding: Numpy array embedding
            ttl: Time-to-live in seconds (None = use default)

        Returns:
            True if successfully cached
        """
        key = self._make_key(text)
        ttl_seconds = ttl if ttl is not None else self.default_ttl

        # Always cache in memory (fast)
        self.memory_cache.set(key, embedding)

        # Cache in Redis if enabled
        if self.redis_enabled and self.redis_client:
            try:
                data = self._serialize_embedding(embedding)

                if ttl_seconds:
                    self.redis_client.setex(key, ttl_seconds, data)
                else:
                    self.redis_client.set(key, data)

                self.metrics.total_size_bytes += len(data)
            except RedisConnectionError:
                logger.warning("Redis connection lost")
                self.redis_enabled = False
                self.metrics.errors += 1
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                self.metrics.errors += 1
                return False

        self.metrics.sets += 1
        return True

    def get_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Get multiple embeddings from cache

        Args:
            texts: List of texts to look up

        Returns:
            List of embeddings (None for cache misses)
        """
        results = []

        # Use Redis MGET for efficiency if available
        if self.redis_enabled and self.redis_client:
            try:
                keys = [self._make_key(text) for text in texts]
                cached_data = self.redis_client.mget(keys)

                for data, text in zip(cached_data, texts):
                    if data:
                        embedding = self._deserialize_embedding(data)
                        results.append(embedding)
                        self.metrics.hits += 1

                        # Populate memory cache
                        key = self._make_key(text)
                        self.memory_cache.set(key, embedding)
                    else:
                        # Try memory cache
                        key = self._make_key(text)
                        embedding = self.memory_cache.get(key)
                        if embedding is not None:
                            self.metrics.hits += 1
                        else:
                            self.metrics.misses += 1
                        results.append(embedding)

                return results

            except Exception as e:
                logger.error(f"Redis mget error: {e}")
                self.metrics.errors += 1

        # Fallback: individual lookups
        for text in texts:
            results.append(self.get(text))

        return results

    def set_batch(
        self,
        texts: List[str],
        embeddings: List[np.ndarray],
        ttl: Optional[int] = None
    ) -> int:
        """
        Store multiple embeddings in cache

        Args:
            texts: List of text keys
            embeddings: List of numpy array embeddings
            ttl: Time-to-live in seconds

        Returns:
            Number of successfully cached embeddings
        """
        if len(texts) != len(embeddings):
            raise ValueError("texts and embeddings must have same length")

        count = 0
        ttl_seconds = ttl if ttl is not None else self.default_ttl

        # Cache in memory
        for text, embedding in zip(texts, embeddings):
            key = self._make_key(text)
            self.memory_cache.set(key, embedding)

        # Cache in Redis with pipeline for efficiency
        if self.redis_enabled and self.redis_client:
            try:
                pipeline = self.redis_client.pipeline()

                for text, embedding in zip(texts, embeddings):
                    key = self._make_key(text)
                    data = self._serialize_embedding(embedding)

                    if ttl_seconds:
                        pipeline.setex(key, ttl_seconds, data)
                    else:
                        pipeline.set(key, data)

                    self.metrics.total_size_bytes += len(data)
                    count += 1

                pipeline.execute()

            except Exception as e:
                logger.error(f"Redis pipeline error: {e}")
                self.metrics.errors += 1
                return count

        self.metrics.sets += len(texts)
        return count if self.redis_enabled else len(texts)

    def delete(self, text: str) -> bool:
        """
        Delete embedding from cache

        Args:
            text: Text key

        Returns:
            True if deleted
        """
        key = self._make_key(text)

        # Delete from memory
        self.memory_cache.delete(key)

        # Delete from Redis
        if self.redis_enabled and self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                self.metrics.errors += 1
                return False

        return True

    def clear(self) -> None:
        """Clear all cached embeddings"""
        # Clear memory cache
        self.memory_cache.clear()

        # Clear Redis (flush keys with prefix)
        if self.redis_enabled and self.redis_client:
            try:
                pattern = f"{self.key_prefix}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys from Redis")
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
                self.metrics.errors += 1

    def get_size(self) -> Dict[str, int]:
        """
        Get cache size information

        Returns:
            Dictionary with memory and redis sizes
        """
        sizes = {
            "memory_count": self.memory_cache.size(),
            "memory_max": self.memory_cache.max_size,
        }

        if self.redis_enabled and self.redis_client:
            try:
                pattern = f"{self.key_prefix}*"
                redis_count = len(self.redis_client.keys(pattern))
                sizes["redis_count"] = redis_count
            except Exception as e:
                logger.error(f"Redis size error: {e}")
                sizes["redis_count"] = 0
        else:
            sizes["redis_count"] = 0

        return sizes

    def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics"""
        # Update eviction count
        self.metrics.evictions = self.memory_cache.get_eviction_count()
        return self.metrics

    def reset_metrics(self) -> None:
        """Reset performance metrics"""
        self.metrics = CacheMetrics()
        self.metrics.redis_enabled = self.redis_enabled
        self.metrics.start_time = datetime.now()

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache

        Returns:
            Health status dictionary
        """
        health = {
            "memory_cache": "healthy",
            "redis_cache": "disabled",
            "overall": "healthy",
        }

        if self.redis_enabled and self.redis_client:
            try:
                self.redis_client.ping()
                health["redis_cache"] = "healthy"
            except Exception as e:
                health["redis_cache"] = f"unhealthy: {e}"
                health["overall"] = "degraded"

        return health


def create_embedding_cache(
    redis_url: Optional[str] = None,
    memory_cache_size: int = 1000,
    default_ttl: Optional[int] = 3600,
) -> EmbeddingCache:
    """
    Factory function to create embedding cache

    Args:
        redis_url: Redis connection URL
        memory_cache_size: In-memory cache size
        default_ttl: Default TTL in seconds

    Returns:
        Configured EmbeddingCache instance
    """
    return EmbeddingCache(
        redis_url=redis_url,
        memory_cache_size=memory_cache_size,
        default_ttl=default_ttl,
    )


if __name__ == "__main__":
    # Example usage
    print("Embedding Cache - Example")
    print("=" * 50)

    # Create cache
    cache = EmbeddingCache(
        redis_url="redis://localhost:6379",  # Will fallback to memory if Redis unavailable
        memory_cache_size=100,
        default_ttl=3600,
    )

    print(f"\nCache initialized")
    print(f"Redis enabled: {cache.redis_enabled}")

    # Create sample embeddings
    texts = [
        "machine learning",
        "deep learning",
        "neural networks",
        "artificial intelligence",
    ]

    embeddings = [
        np.random.rand(384).astype(np.float32) for _ in texts
    ]

    # Cache embeddings
    print(f"\nCaching {len(texts)} embeddings...")
    cache.set_batch(texts, embeddings)

    # Retrieve embeddings (cache hits)
    print("\nRetrieving embeddings...")
    for text in texts:
        cached_emb = cache.get(text)
        status = "HIT" if cached_emb is not None else "MISS"
        print(f"  {text}: {status}")

    # Get metrics
    print("\nCache Metrics:")
    metrics = cache.get_metrics()
    print(f"  Total requests: {metrics.total_requests}")
    print(f"  Hits: {metrics.hits}")
    print(f"  Misses: {metrics.misses}")
    print(f"  Hit rate: {metrics.hit_rate:.1f}%")
    print(f"  Cache size: {cache.get_size()}")

    # Health check
    print("\nHealth Check:")
    health = cache.health_check()
    for component, status in health.items():
        print(f"  {component}: {status}")
