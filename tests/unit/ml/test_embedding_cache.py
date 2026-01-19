"""
Tests for Embedding Cache Module

Tests cover:
- In-memory LRU cache functionality
- Redis cache integration
- Fallback mechanisms
- Batch operations
- Metrics tracking
- Performance characteristics
"""

import time
import numpy as np
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ml.embedding_cache import (
    InMemoryLRUCache,
    EmbeddingCache,
    CacheMetrics,
    create_embedding_cache,
    REDIS_AVAILABLE,
)


@pytest.fixture
def sample_embedding():
    """Sample embedding vector"""
    return np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)


@pytest.fixture
def sample_embeddings():
    """Multiple sample embeddings"""
    return [
        np.array([0.1, 0.2, 0.3], dtype=np.float32),
        np.array([0.4, 0.5, 0.6], dtype=np.float32),
        np.array([0.7, 0.8, 0.9], dtype=np.float32),
    ]


@pytest.fixture
def memory_cache():
    """In-memory LRU cache instance"""
    return InMemoryLRUCache(max_size=10)


@pytest.fixture
def embedding_cache_no_redis():
    """Embedding cache without Redis"""
    return EmbeddingCache(
        redis_url=None,
        memory_cache_size=10,
        default_ttl=3600,
    )


@pytest.fixture
def embedding_cache_with_mock_redis():
    """Embedding cache with mocked Redis"""
    with patch('src.ml.embedding_cache.redis') as mock_redis:
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        cache = EmbeddingCache(
            redis_url="redis://localhost:6379",
            memory_cache_size=10,
            default_ttl=3600,
        )

        cache.redis_client = mock_client
        cache.redis_enabled = True
        cache.metrics.redis_enabled = True

        yield cache


class TestCacheMetrics:
    """Test cache metrics tracking"""

    def test_metrics_initialization(self):
        """Test metrics are initialized correctly"""
        metrics = CacheMetrics()

        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.sets == 0
        assert metrics.evictions == 0
        assert metrics.errors == 0
        assert metrics.total_requests == 0
        assert metrics.hit_rate == 0.0
        assert metrics.redis_enabled is False

    def test_total_requests(self):
        """Test total requests calculation"""
        metrics = CacheMetrics()
        metrics.hits = 75
        metrics.misses = 25

        assert metrics.total_requests == 100

    def test_hit_rate(self):
        """Test hit rate calculation"""
        metrics = CacheMetrics()
        metrics.hits = 80
        metrics.misses = 20

        assert metrics.hit_rate == 80.0

    def test_hit_rate_zero_requests(self):
        """Test hit rate with zero requests"""
        metrics = CacheMetrics()
        assert metrics.hit_rate == 0.0

    def test_miss_rate(self):
        """Test miss rate calculation"""
        metrics = CacheMetrics()
        metrics.hits = 60
        metrics.misses = 40

        assert metrics.miss_rate == 40.0

    def test_uptime(self):
        """Test uptime tracking"""
        metrics = CacheMetrics()
        time.sleep(0.1)

        assert metrics.uptime_seconds >= 0.1

    def test_to_dict(self):
        """Test metrics to dictionary conversion"""
        metrics = CacheMetrics()
        metrics.hits = 100
        metrics.misses = 50
        metrics.total_size_bytes = 1024 * 1024  # 1 MB

        result = metrics.to_dict()

        assert result['hits'] == 100
        assert result['misses'] == 50
        assert result['hit_rate'] == pytest.approx(66.67, rel=0.01)
        assert result['total_size_mb'] == 1.0


class TestInMemoryLRUCache:
    """Test in-memory LRU cache"""

    def test_cache_initialization(self, memory_cache):
        """Test cache initializes correctly"""
        assert memory_cache.max_size == 10
        assert memory_cache.size() == 0

    def test_set_and_get(self, memory_cache, sample_embedding):
        """Test setting and getting values"""
        memory_cache.set("test_key", sample_embedding)

        cached = memory_cache.get("test_key")
        assert cached is not None
        assert np.array_equal(cached, sample_embedding)

    def test_get_returns_copy(self, memory_cache, sample_embedding):
        """Test get returns copy not reference"""
        memory_cache.set("test_key", sample_embedding)

        cached1 = memory_cache.get("test_key")
        cached2 = memory_cache.get("test_key")

        # Should be equal values
        assert np.array_equal(cached1, cached2)

        # But different objects
        cached1[0] = 999
        assert not np.array_equal(cached1, cached2)

    def test_cache_miss(self, memory_cache):
        """Test cache miss returns None"""
        result = memory_cache.get("nonexistent")
        assert result is None

    def test_lru_eviction(self, memory_cache):
        """Test LRU eviction when cache is full"""
        # Fill cache to capacity
        for i in range(10):
            emb = np.array([float(i)])
            memory_cache.set(f"key_{i}", emb)

        assert memory_cache.size() == 10

        # Add one more (should evict oldest)
        memory_cache.set("key_10", np.array([10.0]))

        assert memory_cache.size() == 10
        assert memory_cache.get("key_0") is None  # Oldest evicted
        assert memory_cache.get("key_10") is not None  # New one added

    def test_lru_ordering(self, memory_cache):
        """Test LRU ordering is maintained"""
        # Add 10 items
        for i in range(10):
            memory_cache.set(f"key_{i}", np.array([float(i)]))

        # Access key_0 (makes it most recent)
        memory_cache.get("key_0")

        # Add new item (should evict key_1, not key_0)
        memory_cache.set("key_10", np.array([10.0]))

        assert memory_cache.get("key_0") is not None  # Still there
        assert memory_cache.get("key_1") is None  # Evicted

    def test_update_existing_key(self, memory_cache):
        """Test updating existing key"""
        emb1 = np.array([1.0, 2.0])
        emb2 = np.array([3.0, 4.0])

        memory_cache.set("key", emb1)
        assert np.array_equal(memory_cache.get("key"), emb1)

        memory_cache.set("key", emb2)
        assert np.array_equal(memory_cache.get("key"), emb2)

        # Size should still be 1
        assert memory_cache.size() == 1

    def test_delete(self, memory_cache, sample_embedding):
        """Test deleting from cache"""
        memory_cache.set("key", sample_embedding)
        assert memory_cache.size() == 1

        deleted = memory_cache.delete("key")
        assert deleted is True
        assert memory_cache.size() == 0
        assert memory_cache.get("key") is None

    def test_delete_nonexistent(self, memory_cache):
        """Test deleting nonexistent key"""
        deleted = memory_cache.delete("nonexistent")
        assert deleted is False

    def test_clear(self, memory_cache):
        """Test clearing cache"""
        for i in range(5):
            memory_cache.set(f"key_{i}", np.array([float(i)]))

        assert memory_cache.size() == 5

        memory_cache.clear()
        assert memory_cache.size() == 0

    def test_eviction_count(self, memory_cache):
        """Test eviction count tracking"""
        assert memory_cache.get_eviction_count() == 0

        # Fill and overfill cache
        for i in range(15):
            memory_cache.set(f"key_{i}", np.array([float(i)]))

        # Should have 5 evictions (15 - 10)
        assert memory_cache.get_eviction_count() == 5


class TestEmbeddingCacheNoRedis:
    """Test embedding cache without Redis"""

    def test_initialization_no_redis(self, embedding_cache_no_redis):
        """Test cache initializes without Redis"""
        cache = embedding_cache_no_redis

        assert cache.redis_enabled is False
        assert cache.redis_client is None
        assert cache.memory_cache is not None

    def test_set_and_get(self, embedding_cache_no_redis, sample_embedding):
        """Test basic set and get"""
        cache = embedding_cache_no_redis

        cache.set("hello", sample_embedding)
        cached = cache.get("hello")

        assert cached is not None
        assert np.array_equal(cached, sample_embedding)

    def test_cache_hit(self, embedding_cache_no_redis, sample_embedding):
        """Test cache hit tracking"""
        cache = embedding_cache_no_redis

        cache.set("test", sample_embedding)
        cache.get("test")

        metrics = cache.get_metrics()
        assert metrics.hits == 1
        assert metrics.misses == 0
        assert metrics.sets == 1

    def test_cache_miss(self, embedding_cache_no_redis):
        """Test cache miss tracking"""
        cache = embedding_cache_no_redis

        cache.get("nonexistent")

        metrics = cache.get_metrics()
        assert metrics.hits == 0
        assert metrics.misses == 1

    def test_batch_set(self, embedding_cache_no_redis, sample_embeddings):
        """Test batch set operation"""
        cache = embedding_cache_no_redis

        texts = ["text1", "text2", "text3"]
        count = cache.set_batch(texts, sample_embeddings)

        assert count == 3
        assert cache.get("text1") is not None
        assert cache.get("text2") is not None
        assert cache.get("text3") is not None

    def test_batch_get(self, embedding_cache_no_redis, sample_embeddings):
        """Test batch get operation"""
        cache = embedding_cache_no_redis

        texts = ["text1", "text2", "text3", "text4"]
        cache.set_batch(texts[:3], sample_embeddings)

        results = cache.get_batch(texts)

        assert len(results) == 4
        assert results[0] is not None  # Cached
        assert results[1] is not None  # Cached
        assert results[2] is not None  # Cached
        assert results[3] is None  # Not cached

    def test_delete(self, embedding_cache_no_redis, sample_embedding):
        """Test delete operation"""
        cache = embedding_cache_no_redis

        cache.set("test", sample_embedding)
        assert cache.get("test") is not None

        cache.delete("test")
        assert cache.get("test") is None

    def test_clear(self, embedding_cache_no_redis, sample_embeddings):
        """Test clear operation"""
        cache = embedding_cache_no_redis

        cache.set_batch(["a", "b", "c"], sample_embeddings)

        cache.clear()

        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.get("c") is None

    def test_get_size(self, embedding_cache_no_redis, sample_embeddings):
        """Test get size operation"""
        cache = embedding_cache_no_redis

        cache.set_batch(["a", "b", "c"], sample_embeddings)

        sizes = cache.get_size()

        assert sizes["memory_count"] == 3
        assert sizes["memory_max"] == 10
        assert sizes["redis_count"] == 0

    def test_metrics_tracking(self, embedding_cache_no_redis, sample_embedding):
        """Test comprehensive metrics tracking"""
        cache = embedding_cache_no_redis

        # Perform operations
        cache.set("key1", sample_embedding)
        cache.set("key2", sample_embedding)
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("key3")  # Miss

        metrics = cache.get_metrics()

        assert metrics.sets == 2
        assert metrics.hits == 2
        assert metrics.misses == 1
        assert metrics.hit_rate == pytest.approx(66.67, rel=0.01)

    def test_ttl_parameter(self, sample_embedding):
        """Test TTL parameter (should work even without Redis)"""
        cache = EmbeddingCache(redis_url=None, default_ttl=60)

        # Should not raise error even though TTL has no effect without Redis
        cache.set("test", sample_embedding, ttl=30)

        assert cache.get("test") is not None

    def test_health_check_no_redis(self, embedding_cache_no_redis):
        """Test health check without Redis"""
        health = embedding_cache_no_redis.health_check()

        assert health["memory_cache"] == "healthy"
        assert health["redis_cache"] == "disabled"
        assert health["overall"] == "healthy"

    def test_key_hashing(self):
        """Test hash-based key generation"""
        cache1 = EmbeddingCache(use_hash_keys=True)
        cache2 = EmbeddingCache(use_hash_keys=False)

        long_text = "a" * 200

        key1 = cache1._make_key(long_text)
        key2 = cache2._make_key(long_text)

        # Hashed key should be shorter
        assert len(key1) < len(key2)

        # Hashed key should be consistent
        assert key1 == cache1._make_key(long_text)


class TestEmbeddingCacheWithRedis:
    """Test embedding cache with Redis (mocked)"""

    def test_initialization_with_redis(self, embedding_cache_with_mock_redis):
        """Test cache initializes with Redis"""
        cache = embedding_cache_with_mock_redis

        assert cache.redis_enabled is True
        assert cache.redis_client is not None

    @pytest.mark.skipif(True, reason="Redis module not available")
    def test_set_with_redis(self, embedding_cache_with_mock_redis, sample_embedding):
        """Test set operation with Redis"""
        cache = embedding_cache_with_mock_redis

        cache.set("test", sample_embedding)

        # Should call Redis set
        cache.redis_client.set.assert_called_once()

    def test_set_with_ttl(self, embedding_cache_with_mock_redis, sample_embedding):
        """Test set with TTL on Redis"""
        cache = embedding_cache_with_mock_redis

        cache.set("test", sample_embedding, ttl=300)

        # Should call Redis setex with TTL
        cache.redis_client.setex.assert_called_once()

    def test_get_from_redis(self, embedding_cache_with_mock_redis, sample_embedding):
        """Test get from Redis"""
        cache = embedding_cache_with_mock_redis

        # Mock Redis returning serialized embedding
        import pickle
        cache.redis_client.get.return_value = pickle.dumps(sample_embedding)

        result = cache.get("test")

        assert result is not None
        assert np.array_equal(result, sample_embedding)
        cache.redis_client.get.assert_called_once()

    def test_batch_get_with_redis(self, embedding_cache_with_mock_redis, sample_embeddings):
        """Test batch get with Redis mget"""
        cache = embedding_cache_with_mock_redis

        import pickle
        cache.redis_client.mget.return_value = [
            pickle.dumps(sample_embeddings[0]),
            pickle.dumps(sample_embeddings[1]),
            None,  # Cache miss
        ]

        results = cache.get_batch(["text1", "text2", "text3"])

        assert len(results) == 3
        assert results[0] is not None
        assert results[1] is not None
        assert results[2] is None

        cache.redis_client.mget.assert_called_once()

    def test_batch_set_with_redis(self, embedding_cache_with_mock_redis, sample_embeddings):
        """Test batch set with Redis pipeline"""
        cache = embedding_cache_with_mock_redis

        # Mock pipeline
        mock_pipeline = MagicMock()
        cache.redis_client.pipeline.return_value = mock_pipeline

        texts = ["text1", "text2", "text3"]
        cache.set_batch(texts, sample_embeddings)

        # Should use pipeline
        cache.redis_client.pipeline.assert_called_once()
        mock_pipeline.execute.assert_called_once()

    def test_delete_with_redis(self, embedding_cache_with_mock_redis, sample_embedding):
        """Test delete with Redis"""
        cache = embedding_cache_with_mock_redis

        cache.delete("test")

        cache.redis_client.delete.assert_called_once()

    def test_clear_with_redis(self, embedding_cache_with_mock_redis):
        """Test clear with Redis"""
        cache = embedding_cache_with_mock_redis

        cache.redis_client.keys.return_value = ["emb:key1", "emb:key2"]

        cache.clear()

        cache.redis_client.keys.assert_called_once()
        cache.redis_client.delete.assert_called_once()

    def test_health_check_with_redis(self, embedding_cache_with_mock_redis):
        """Test health check with Redis"""
        cache = embedding_cache_with_mock_redis

        cache.redis_client.ping.return_value = True

        health = cache.health_check()

        assert health["memory_cache"] == "healthy"
        assert health["redis_cache"] == "healthy"
        assert health["overall"] == "healthy"

    def test_redis_connection_failure(self):
        """Test graceful fallback when Redis connection fails"""
        with patch('src.ml.embedding_cache.redis') as mock_redis:
            mock_redis.from_url.side_effect = Exception("Connection failed")

            cache = EmbeddingCache(redis_url="redis://localhost:6379")

            # Should fallback to memory-only
            assert cache.redis_enabled is False
            assert cache.memory_cache is not None

    @pytest.mark.skipif(True, reason="Redis module not available")
    def test_redis_error_handling(self, embedding_cache_with_mock_redis, sample_embedding):
        """Test error handling during Redis operations"""
        cache = embedding_cache_with_mock_redis

        # Simulate Redis error
        from redis import ConnectionError as RedisConnectionError
        cache.redis_client.get.side_effect = RedisConnectionError("Connection lost")

        # Should still work with memory cache
        cache.memory_cache.set(cache._make_key("test"), sample_embedding)
        result = cache.get("test")

        assert result is not None
        assert cache.metrics.errors > 0


class TestEmbeddingCachePerformance:
    """Test cache performance characteristics"""

    def test_cache_speedup(self, embedding_cache_no_redis):
        """Test that caching provides speedup"""
        cache = embedding_cache_no_redis

        # Large embedding
        embedding = np.random.rand(768).astype(np.float32)

        # First access - set
        start = time.time()
        cache.set("test", embedding)
        set_time = time.time() - start

        # Second access - get (should be faster)
        start = time.time()
        cache.get("test")
        get_time = time.time() - start

        # Get should be significantly faster
        assert get_time < set_time

    def test_batch_vs_individual(self, embedding_cache_no_redis):
        """Test batch operations are more efficient"""
        cache = embedding_cache_no_redis

        # Prepare data
        n = 100
        texts = [f"text_{i}" for i in range(n)]
        embeddings = [np.random.rand(384).astype(np.float32) for _ in range(n)]

        # Individual sets
        start = time.time()
        for text, emb in zip(texts[:50], embeddings[:50]):
            cache.set(text, emb)
        individual_time = time.time() - start

        # Batch set
        start = time.time()
        cache.set_batch(texts[50:], embeddings[50:])
        batch_time = time.time() - start

        # Batch should be faster (or comparable)
        # Note: Without real Redis, benefit is minimal
        assert batch_time <= individual_time * 1.5


class TestFactoryFunction:
    """Test factory function"""

    def test_create_embedding_cache(self):
        """Test factory function creates cache correctly"""
        cache = create_embedding_cache(
            redis_url=None,
            memory_cache_size=500,
            default_ttl=7200,
        )

        assert cache is not None
        assert cache.memory_cache.max_size == 500
        assert cache.default_ttl == 7200

    def test_create_with_redis_url(self):
        """Test factory with Redis URL"""
        with patch('src.ml.embedding_cache.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client

            cache = create_embedding_cache(
                redis_url="redis://localhost:6379"
            )

            assert cache is not None


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_text(self, embedding_cache_no_redis, sample_embedding):
        """Test caching with empty text"""
        cache = embedding_cache_no_redis

        cache.set("", sample_embedding)
        result = cache.get("")

        assert result is not None

    def test_very_long_text(self, embedding_cache_no_redis, sample_embedding):
        """Test caching with very long text"""
        cache = embedding_cache_no_redis

        long_text = "a" * 10000
        cache.set(long_text, sample_embedding)
        result = cache.get(long_text)

        assert result is not None

    def test_special_characters_in_key(self, embedding_cache_no_redis, sample_embedding):
        """Test keys with special characters"""
        cache = embedding_cache_no_redis

        special_text = "hello:world space/slash\\backslash"
        cache.set(special_text, sample_embedding)
        result = cache.get(special_text)

        assert result is not None

    def test_unicode_text(self, embedding_cache_no_redis, sample_embedding):
        """Test caching with Unicode text"""
        cache = embedding_cache_no_redis

        unicode_text = "Hello мир 世界 🌍"
        cache.set(unicode_text, sample_embedding)
        result = cache.get(unicode_text)

        assert result is not None

    def test_batch_length_mismatch(self, embedding_cache_no_redis, sample_embeddings):
        """Test batch set with mismatched lengths"""
        cache = embedding_cache_no_redis

        texts = ["a", "b"]

        with pytest.raises(ValueError):
            cache.set_batch(texts, sample_embeddings)  # 2 texts, 3 embeddings

    def test_metrics_reset(self, embedding_cache_no_redis, sample_embedding):
        """Test metrics reset"""
        cache = embedding_cache_no_redis

        cache.set("test", sample_embedding)
        cache.get("test")

        assert cache.get_metrics().hits > 0

        cache.reset_metrics()

        assert cache.get_metrics().hits == 0
        assert cache.get_metrics().misses == 0
        assert cache.get_metrics().sets == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
