# Embedding Cache System - Complete Guide

## Overview

The Embedding Cache system provides high-performance caching for text embeddings, dramatically reducing computational costs and latency in semantic search and NLP operations.

**Key Benefits:**
- **50-100x faster** repeated embedding retrieval
- **Reduced API costs** for cloud embedding services (OpenAI, Cohere, etc.)
- **Lower resource usage** (CPU/GPU)
- **Distributed caching** with Redis support
- **Automatic fallback** to in-memory cache

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Integration Examples](#integration-examples)
7. [Configuration](#configuration)
8. [Performance Tuning](#performance-tuning)
9. [Monitoring](#monitoring)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Usage (No Redis)

```python
from src.ml.embedding_cache import EmbeddingCache
import numpy as np

# Create cache (in-memory only)
cache = EmbeddingCache(
    redis_url=None,  # No Redis
    memory_cache_size=1000,
    default_ttl=3600,  # 1 hour
)

# Cache an embedding
text = "machine learning"
embedding = np.array([0.1, 0.2, 0.3, ...])  # 384-dim vector
cache.set(text, embedding)

# Retrieve embedding (instant!)
cached_embedding = cache.get(text)
if cached_embedding is not None:
    print("Cache hit!")
```

### With Redis (Production)

```python
# Create cache with Redis
cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    redis_db=0,
    memory_cache_size=1000,
    default_ttl=3600,
)

# Same API as above
cache.set("text", embedding)
cached = cache.get("text")
```

### With Semantic Search

```python
from src.ml.semantic_search import SemanticSearchEngine

# Create search engine with caching
engine = SemanticSearchEngine(
    model_name="all-MiniLM-L6-v2",
    cache_embeddings=True,
    redis_url="redis://localhost:6379",  # Optional
    cache_ttl=3600,
)

# Embeddings are cached automatically!
results = engine.search("artificial intelligence")
```

---

## Architecture

### Two-Tier Caching

```
┌─────────────────────────────────────────┐
│  Application (Semantic Search, NER)     │
└───────────────┬─────────────────────────┘
                │
        ┌───────▼────────┐
        │ Embedding Cache│
        └───────┬────────┘
                │
     ┌──────────┴──────────┐
     │                     │
┌────▼─────┐        ┌─────▼──────┐
│  Redis   │        │  In-Memory │
│  (L1)    │◄──────►│  LRU (L2)  │
└──────────┘        └────────────┘
```

**How it works:**

1. **GET Request:**
   - Check Redis (if enabled)
   - If miss, check in-memory cache
   - If miss, return None (needs computation)

2. **SET Request:**
   - Store in in-memory cache (always)
   - Store in Redis (if enabled)

3. **Benefits:**
   - Redis: Distributed, persistent, shared across instances
   - In-memory: Ultra-fast, local fallback

---

## Installation

### Required Dependencies

```bash
# Core dependency (always required)
pip install numpy

# Optional: Redis support
pip install redis

# For semantic search integration
pip install sentence-transformers faiss-cpu
```

### Redis Setup (Optional but Recommended)

#### Docker

```bash
# Start Redis with Docker
docker run -d \
  --name redis-embeddings \
  -p 6379:6379 \
  redis:7-alpine
```

#### Native Installation

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Verify
redis-cli ping
# Should return: PONG
```

---

## Basic Usage

### Creating a Cache

```python
from src.ml.embedding_cache import EmbeddingCache

# In-memory only (development)
cache = EmbeddingCache(
    redis_url=None,
    memory_cache_size=1000,
)

# With Redis (production)
cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    redis_db=0,
    redis_password="your_password",  # If required
    memory_cache_size=1000,
    default_ttl=3600,  # 1 hour expiration
)
```

### Set & Get

```python
import numpy as np

# Create embedding (example)
text = "Hello world"
embedding = np.random.rand(384).astype(np.float32)

# Cache it
cache.set(text, embedding)

# Retrieve it
cached_emb = cache.get(text)
if cached_emb is not None:
    print(f"Cache hit! Shape: {cached_emb.shape}")
else:
    print("Cache miss - need to compute")
```

### Batch Operations

```python
# Cache multiple embeddings efficiently
texts = [
    "machine learning",
    "deep learning",
    "neural networks",
]

embeddings = [
    np.random.rand(384).astype(np.float32)
    for _ in texts
]

# Batch set (uses Redis pipeline for efficiency)
cache.set_batch(texts, embeddings)

# Batch get (uses Redis MGET)
cached = cache.get_batch(texts)

for text, emb in zip(texts, cached):
    if emb is not None:
        print(f"{text}: cached ✓")
    else:
        print(f"{text}: not cached ✗")
```

---

## Advanced Features

### Time-To-Live (TTL)

```python
# Default TTL for all entries
cache = EmbeddingCache(default_ttl=3600)  # 1 hour

# Per-entry TTL
cache.set("short_lived", embedding, ttl=300)  # 5 minutes
cache.set("long_lived", embedding, ttl=86400)  # 24 hours
cache.set("no_expiry", embedding, ttl=None)  # Never expires
```

### Custom Key Prefixes

```python
# Separate caches for different models
bert_cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    key_prefix="bert:",
)

roberta_cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    key_prefix="roberta:",
)
```

### Key Hashing

```python
# Use MD5 hashing for consistent key lengths
cache = EmbeddingCache(use_hash_keys=True)

# Long text gets hashed to short key
long_text = "a" * 10000
cache.set(long_text, embedding)  # Key: "emb:5f4dcc3b5aa7..."
```

### Metrics Tracking

```python
# Get detailed metrics
metrics = cache.get_metrics()

print(f"Total requests: {metrics.total_requests}")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Redis enabled: {metrics.redis_enabled}")

# Dictionary format
metrics_dict = metrics.to_dict()
```

### Health Monitoring

```python
# Check cache health
health = cache.health_check()

print(f"Memory cache: {health['memory_cache']}")
print(f"Redis cache: {health['redis_cache']}")
print(f"Overall: {health['overall']}")

# Output:
# Memory cache: healthy
# Redis cache: healthy
# Overall: healthy
```

---

## Integration Examples

### With Semantic Search

```python
from src.ml.semantic_search import SemanticSearchEngine

# Create engine with Redis caching
engine = SemanticSearchEngine(
    model_name="all-MiniLM-L6-v2",
    cache_embeddings=True,
    redis_url="redis://localhost:6379",
    cache_ttl=3600,
    memory_cache_size=1000,
)

# Index documents (embeddings cached automatically)
docs = [
    {"id": "1", "text": "Machine learning tutorial"},
    {"id": "2", "text": "Deep learning with PyTorch"},
]
engine.index_documents(docs)

# Search (query embedding cached)
results = engine.search("neural networks")

# Check cache metrics
metrics = engine.get_cache_metrics()
print(f"Cache hit rate: {metrics['hit_rate']:.1f}%")
```

### Custom Embedding Function

```python
from sentence_transformers import SentenceTransformer

# Initialize model and cache
model = SentenceTransformer("all-MiniLM-L6-v2")
cache = EmbeddingCache(redis_url="redis://localhost:6379")

def encode_with_cache(texts):
    """Encode texts with caching"""
    # Check cache first
    cached_embeddings = cache.get_batch(texts)

    # Find uncached texts
    uncached_texts = []
    uncached_indices = []

    for i, (text, emb) in enumerate(zip(texts, cached_embeddings)):
        if emb is None:
            uncached_texts.append(text)
            uncached_indices.append(i)

    # Encode uncached texts
    if uncached_texts:
        new_embeddings = model.encode(uncached_texts)
        cache.set_batch(uncached_texts, new_embeddings)

        # Merge cached and new
        all_embeddings = []
        uncached_idx = 0

        for i, cached_emb in enumerate(cached_embeddings):
            if cached_emb is None:
                all_embeddings.append(new_embeddings[uncached_idx])
                uncached_idx += 1
            else:
                all_embeddings.append(cached_emb)

        return all_embeddings

    return cached_embeddings

# Usage
texts = ["text1", "text2", "text3"]
embeddings = encode_with_cache(texts)
```

### With RAG Pipeline

```python
class RAGPipeline:
    def __init__(self):
        self.cache = EmbeddingCache(
            redis_url="redis://localhost:6379",
            default_ttl=7200,  # 2 hours
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_query(self, query: str):
        """Embed query with caching"""
        # Check cache
        cached = self.cache.get(query)
        if cached is not None:
            return cached

        # Compute and cache
        embedding = self.model.encode(query)
        self.cache.set(query, embedding)

        return embedding

    def embed_documents(self, docs: List[str]):
        """Embed documents with batch caching"""
        cached = self.cache.get_batch(docs)

        # Find uncached
        to_encode = [
            doc for doc, emb in zip(docs, cached)
            if emb is None
        ]

        if to_encode:
            new_embs = self.model.encode(to_encode)
            self.cache.set_batch(to_encode, new_embs)

        # Return all embeddings
        # (implementation depends on your needs)
        return self.cache.get_batch(docs)
```

---

## Configuration

### Cache Sizes

```python
# Small cache (memory-constrained environments)
cache = EmbeddingCache(memory_cache_size=100)

# Medium cache (default)
cache = EmbeddingCache(memory_cache_size=1000)

# Large cache (high-volume production)
cache = EmbeddingCache(memory_cache_size=10000)
```

**Memory Usage Estimation:**
- 384-dim embedding: ~1.5 KB
- 768-dim embedding: ~3 KB
- 1536-dim embedding: ~6 KB

For 1000 embeddings (384-dim): ~1.5 MB

### TTL Strategies

```python
# Short TTL (frequently changing data)
cache = EmbeddingCache(default_ttl=300)  # 5 minutes

# Medium TTL (general purpose)
cache = EmbeddingCache(default_ttl=3600)  # 1 hour

# Long TTL (stable data)
cache = EmbeddingCache(default_ttl=86400)  # 24 hours

# No TTL (manual eviction only)
cache = EmbeddingCache(default_ttl=None)
```

### Redis Configuration

```python
# Production configuration
cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    redis_db=1,  # Use separate DB
    redis_password="secure_password",
    memory_cache_size=5000,
    default_ttl=3600,
    key_prefix="prod:emb:",
    use_hash_keys=True,
)

# Development configuration
cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    redis_db=15,  # Separate dev DB
    memory_cache_size=100,
    default_ttl=300,
    key_prefix="dev:emb:",
)
```

---

## Performance Tuning

### Benchmark Results

Based on testing with 384-dim embeddings:

| Operation | Without Cache | With Cache | Speedup |
|-----------|--------------|------------|---------|
| Single embedding | 20-50ms | <0.5ms | **50-100x** |
| Batch (10 embeddings) | 100-200ms | <5ms | **40x** |
| Batch (100 embeddings) | 800-1500ms | <50ms | **30x** |

### Optimization Tips

#### 1. Use Batch Operations

```python
# Bad: Individual operations
for text in texts:
    cache.set(text, encode(text))

# Good: Batch operations
embeddings = encode(texts)
cache.set_batch(texts, embeddings)
```

**Benefit:** Redis pipeline reduces round-trips (10-20x faster for batches)

#### 2. Enable Redis for Multi-Instance Deployments

```python
# Without Redis: Each instance has separate cache
cache1 = EmbeddingCache(redis_url=None)  # Instance 1
cache2 = EmbeddingCache(redis_url=None)  # Instance 2
# No cache sharing - 50% hit rate at best

# With Redis: Shared cache across instances
cache1 = EmbeddingCache(redis_url="redis://...")  # Instance 1
cache2 = EmbeddingCache(redis_url="redis://...")  # Instance 2
# Shared cache - 90%+ hit rate possible
```

#### 3. Tune Cache Size

```python
# Monitor cache evictions
metrics = cache.get_metrics()

if metrics.evictions > metrics.sets * 0.5:
    # Too many evictions - increase size
    cache = EmbeddingCache(memory_cache_size=5000)
```

#### 4. Use Appropriate TTL

```python
# For stable datasets (documentation, FAQs)
cache = EmbeddingCache(default_ttl=86400)  # 24 hours

# For dynamic data (user queries, real-time content)
cache = EmbeddingCache(default_ttl=1800)  # 30 minutes
```

#### 5. Monitor Hit Rate

```python
import time

def log_cache_stats(cache, interval=60):
    """Log cache statistics periodically"""
    while True:
        metrics = cache.get_metrics()
        print(f"Hit rate: {metrics.hit_rate:.1f}%")
        print(f"Total requests: {metrics.total_requests}")

        if metrics.hit_rate < 50:
            print("WARNING: Low hit rate!")

        time.sleep(interval)

# Run in background thread
import threading
threading.Thread(
    target=log_cache_stats,
    args=(cache,),
    daemon=True
).start()
```

---

## Monitoring

### Key Metrics

```python
metrics = cache.get_metrics()

# Performance metrics
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Miss rate: {metrics.miss_rate:.1f}%")
print(f"Total requests: {metrics.total_requests}")

# Operation counts
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Sets: {metrics.sets}")
print(f"Evictions: {metrics.evictions}")

# Resource usage
print(f"Total size: {metrics.total_size_mb:.2f} MB")
print(f"Uptime: {metrics.uptime_seconds:.0f}s")

# Configuration
print(f"Redis enabled: {metrics.redis_enabled}")
```

### Prometheus Integration

```python
from prometheus_client import Counter, Gauge, Histogram

# Define metrics
cache_hits = Counter('embedding_cache_hits_total', 'Total cache hits')
cache_misses = Counter('embedding_cache_misses_total', 'Total cache misses')
cache_hit_rate = Gauge('embedding_cache_hit_rate', 'Cache hit rate percentage')
cache_size = Gauge('embedding_cache_size_bytes', 'Cache size in bytes')

# Update metrics periodically
def update_prometheus_metrics(cache):
    metrics = cache.get_metrics()

    cache_hits.inc(metrics.hits)
    cache_misses.inc(metrics.misses)
    cache_hit_rate.set(metrics.hit_rate)
    cache_size.set(metrics.total_size_bytes)

    cache.reset_metrics()  # Reset for next interval
```

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log cache events
cache = EmbeddingCache(redis_url="redis://localhost:6379")

def log_cache_operations(cache):
    """Log important cache events"""
    metrics = cache.get_metrics()

    if metrics.hit_rate < 30:
        logger.warning(f"Low cache hit rate: {metrics.hit_rate:.1f}%")

    if metrics.errors > 0:
        logger.error(f"Cache errors: {metrics.errors}")

    if metrics.evictions > metrics.sets * 0.8:
        logger.warning("High eviction rate - consider increasing cache size")
```

---

## Best Practices

### 1. Always Use Caching in Production

```python
# Production setup
cache = EmbeddingCache(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
    memory_cache_size=5000,
    default_ttl=3600,
)
```

### 2. Configure Appropriate TTL

```python
# Match TTL to data volatility
stable_data_cache = EmbeddingCache(default_ttl=86400)  # 24h
dynamic_data_cache = EmbeddingCache(default_ttl=1800)  # 30min
```

### 3. Monitor Cache Health

```python
# Periodic health checks
def check_cache_health(cache):
    health = cache.health_check()

    if health["overall"] != "healthy":
        alert_ops_team(health)
```

### 4. Use Batch Operations

```python
# Batch operations are 10-20x faster
cache.set_batch(texts, embeddings)  # Good
```

### 5. Handle Cache Failures Gracefully

```python
def get_embedding_with_fallback(text, model, cache):
    """Get embedding with cache fallback"""
    # Try cache first
    try:
        cached = cache.get(text)
        if cached is not None:
            return cached
    except Exception as e:
        logger.warning(f"Cache error: {e}")

    # Compute if cache miss or error
    embedding = model.encode(text)

    # Try to cache result
    try:
        cache.set(text, embedding)
    except Exception as e:
        logger.warning(f"Cache set error: {e}")

    return embedding
```

### 6. Clear Cache Periodically in Long-Running Services

```python
import schedule

def clear_cache_daily(cache):
    """Clear cache daily at 2 AM"""
    cache.clear()
    cache.reset_metrics()
    logger.info("Cache cleared and metrics reset")

schedule.every().day.at("02:00").do(clear_cache_daily, cache)
```

### 7. Separate Caches for Different Models

```python
# Different caches for different embedding models
small_model_cache = EmbeddingCache(key_prefix="small:")
large_model_cache = EmbeddingCache(key_prefix="large:")
```

---

## Troubleshooting

### Low Hit Rate

**Symptom:** Cache hit rate < 30%

**Causes:**
- Unique/non-repeated queries
- Cache size too small
- Text normalization issues

**Solutions:**

```python
# 1. Normalize text before caching
def normalize_text(text):
    return text.lower().strip()

text = normalize_text("Hello World ")
cache.set(text, embedding)

# 2. Increase cache size
cache = EmbeddingCache(memory_cache_size=10000)

# 3. Increase TTL
cache = EmbeddingCache(default_ttl=7200)  # 2 hours
```

### High Memory Usage

**Symptom:** Application using too much RAM

**Causes:**
- Cache size too large
- Large embedding dimensions

**Solutions:**

```python
# 1. Reduce cache size
cache = EmbeddingCache(memory_cache_size=500)

# 2. Use Redis instead of in-memory
cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    memory_cache_size=100,  # Small in-memory cache
)

# 3. Clear cache periodically
cache.clear()
```

### Redis Connection Issues

**Symptom:** "Redis connection failed" warnings

**Causes:**
- Redis not running
- Network issues
- Wrong credentials

**Solutions:**

```python
# 1. Verify Redis is running
# docker ps | grep redis
# redis-cli ping

# 2. Check connection settings
cache = EmbeddingCache(
    redis_url="redis://localhost:6379",
    redis_password="your_password",  # If required
)

# 3. Test health
health = cache.health_check()
print(health)

# 4. Cache still works with in-memory fallback
# No action needed - automatic fallback
```

### Slow Performance

**Symptom:** Cache operations slow

**Causes:**
- Network latency to Redis
- Large batch sizes
- Not using batch operations

**Solutions:**

```python
# 1. Use batch operations
cache.set_batch(texts, embeddings)  # Not individual sets

# 2. Use local in-memory cache for read-heavy workloads
cache = EmbeddingCache(
    redis_url=None,  # Local only
    memory_cache_size=10000,
)

# 3. Optimize batch size
cache.set_batch(texts[:100], embeddings[:100])  # Smaller batches
```

---

## API Reference

### EmbeddingCache

```python
class EmbeddingCache:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        memory_cache_size: int = 1000,
        default_ttl: Optional[int] = None,
        key_prefix: str = "emb:",
        use_hash_keys: bool = True,
    )
```

**Methods:**

- `get(text: str) -> Optional[np.ndarray]`: Get embedding
- `set(text: str, embedding: np.ndarray, ttl: Optional[int] = None) -> bool`: Store embedding
- `get_batch(texts: List[str]) -> List[Optional[np.ndarray]]`: Get multiple embeddings
- `set_batch(texts: List[str], embeddings: List[np.ndarray], ttl: Optional[int] = None) -> int`: Store multiple embeddings
- `delete(text: str) -> bool`: Delete embedding
- `clear() -> None`: Clear all embeddings
- `get_size() -> Dict[str, int]`: Get cache sizes
- `get_metrics() -> CacheMetrics`: Get performance metrics
- `reset_metrics() -> None`: Reset metrics
- `health_check() -> Dict[str, Any]`: Health check

---

## Conclusion

The Embedding Cache system provides significant performance improvements for embedding-heavy workloads. By following the best practices and monitoring guidelines in this document, you can achieve:

- **50-100x faster** embedding retrieval
- **Lower costs** for cloud embedding APIs
- **Better scalability** with distributed Redis caching
- **High availability** with automatic fallback

For questions or issues, refer to the troubleshooting section or contact the DMS team.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-18
**Author:** DMS Team
