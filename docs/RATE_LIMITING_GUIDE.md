# Rate Limiting Guide

## Overview

The Document Management System includes comprehensive rate limiting to protect against:
- DoS attacks
- Brute force attempts
- API abuse
- Resource exhaustion

## Features

- **Multiple Algorithms**: Sliding window, token bucket
- **Distributed Support**: Redis backend for multi-server deployments
- **FastAPI Integration**: Middleware and dependency injection
- **Tier-Based Limits**: FREE, BASIC, PREMIUM, ENTERPRISE
- **Graceful Degradation**: Fails open on errors
- **Thread-Safe**: Safe for concurrent access

## Quick Start

### Basic Usage (In-Memory)

```python
from src.core.rate_limiter import RateLimiter

# Create limiter: 100 requests per minute
limiter = RateLimiter(requests=100, window=60)

# Check if request is allowed
is_allowed, retry_after = limiter.is_allowed("client_id")

if not is_allowed:
    print(f"Rate limit exceeded. Retry after {retry_after} seconds")
else:
    # Process request
    remaining = limiter.get_remaining("client_id")
    print(f"Request allowed. {remaining} remaining")
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from src.core.rate_limiter import (
    RateLimitTier,
    FastAPIRateLimitMiddleware,
    create_rate_limit_dependency
)

app = FastAPI()

# Option 1: Global middleware (all endpoints)
limiter = RateLimitTier.get_limiter("free")
app.add_middleware(FastAPIRateLimitMiddleware, limiter=limiter)

# Option 2: Per-endpoint dependency
rate_limit_dep = create_rate_limit_dependency(limiter)

@app.get("/api/data")
async def get_data(rate_limit: None = Depends(rate_limit_dep)):
    return {"data": "value"}
```

### Redis Backend (Distributed)

```python
from src.core.rate_limiter import RedisRateLimiter

# Automatically connects to Redis or falls back to in-memory
limiter = RedisRateLimiter(
    requests=100,
    window=60,
    prefix="myapp"
)

# Use same as regular RateLimiter
is_allowed, retry_after = limiter.is_allowed("client_id")
```

## Rate Limit Tiers

### Tier Configuration

| Tier | Requests/Minute | Use Case |
|------|-----------------|----------|
| **FREE** | 100 | Free tier users, testing |
| **BASIC** | 500 | Basic paid tier |
| **PREMIUM** | 2,000 | Premium users |
| **ENTERPRISE** | 10,000 | Enterprise customers |

### Using Tiers

```python
from src.core.rate_limiter import RateLimitTier

# Get limiter for specific tier
free_limiter = RateLimitTier.get_limiter("free")
premium_limiter = RateLimitTier.get_limiter("premium")

# Use Redis for distributed setups
enterprise_limiter = RateLimitTier.get_limiter(
    "enterprise",
    use_redis=True
)
```

## Algorithms

### 1. Sliding Window (RateLimiter)

**How it works:**
- Tracks timestamp of each request
- Removes requests outside time window
- Rejects if count exceeds limit

**Best for:**
- General API rate limiting
- Consistent enforcement
- Simple use cases

**Example:**
```python
limiter = RateLimiter(requests=10, window=60)  # 10 req/min
```

### 2. Token Bucket (TokenBucketRateLimiter)

**How it works:**
- Tokens refill at constant rate
- Each request consumes tokens
- Allows controlled bursts

**Best for:**
- Bursty traffic patterns
- Gradual rate limiting
- Resource-intensive operations

**Example:**
```python
limiter = TokenBucketRateLimiter(
    capacity=100,      # Max burst size
    refill_rate=10     # 10 tokens/second
)
```

### 3. Redis-Backed (RedisRateLimiter)

**How it works:**
- Uses Redis sorted sets for storage
- Distributed across multiple servers
- Falls back to in-memory if Redis unavailable

**Best for:**
- Multi-server deployments
- Horizontal scaling
- Centralized tracking

**Example:**
```python
limiter = RedisRateLimiter(
    requests=100,
    window=60,
    redis_client=redis_client  # Optional
)
```

## API Server Integration

### Running with Rate Limits

```bash
# Default (FREE tier, in-memory)
python doc-api-server.py

# Specify tier
python doc-api-server.py --rate-limit-tier premium

# Use Redis for distributed rate limiting
python doc-api-server.py --rate-limit-tier enterprise --use-redis-rate-limit

# Environment variables
export RATE_LIMIT_TIER=PREMIUM
export USE_REDIS_RATE_LIMIT=true
python doc-api-server.py
```

### Response Headers

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

### Error Response (429)

When rate limit is exceeded:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 30
}
```

HTTP Headers:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

## Advanced Usage

### Custom Client Identification

```python
def custom_key_func(request):
    """Custom function to extract client ID."""
    # Use API key if available
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api:{api_key}"

    # Use authenticated user ID
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    # Fallback to IP
    return f"ip:{request.client.host}"

# Use with middleware
app.add_middleware(
    FastAPIRateLimitMiddleware,
    limiter=limiter,
    key_func=custom_key_func
)
```

### Different Limits per Endpoint

```python
# Strict limits for authentication
auth_limiter = RateLimiter(requests=5, window=60)
auth_dep = create_rate_limit_dependency(auth_limiter)

@app.post("/api/auth/login")
async def login(rate_limit: None = Depends(auth_dep)):
    # Only 5 login attempts per minute
    pass

# Relaxed limits for data access
data_limiter = RateLimiter(requests=100, window=60)
data_dep = create_rate_limit_dependency(data_limiter)

@app.get("/api/data")
async def get_data(rate_limit: None = Depends(data_dep)):
    # 100 requests per minute
    pass
```

### Resetting Client Limits

```python
# Reset specific client (e.g., after payment)
limiter.reset("client_id")

# Cleanup inactive clients (memory management)
limiter.cleanup_old_clients(max_age=3600)  # 1 hour
```

### Background Cleanup Task

```python
from src.core.rate_limiter import start_cleanup_task

# Start background task to clean up old clients
start_cleanup_task(limiter, interval=3600)  # Every hour
```

## Production Deployment

### Redis Setup

**1. Install Redis:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

**2. Configure Redis:**
```python
import redis
from src.core.rate_limiter import RedisRateLimiter

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

limiter = RedisRateLimiter(
    requests=1000,
    window=60,
    redis_client=redis_client,
    prefix="myapp:ratelimit"
)
```

**3. Redis Cluster (High Availability):**
```python
from redis.cluster import RedisCluster

redis_cluster = RedisCluster(
    host='localhost',
    port=7000,
    decode_responses=True
)

limiter = RedisRateLimiter(
    requests=10000,
    window=60,
    redis_client=redis_cluster
)
```

### Monitoring

**Check rate limiter status:**
```python
# Get statistics
client_count = len(limiter.clients)
print(f"Active clients: {client_count}")

# Check specific client
remaining = limiter.get_remaining("client_id")
print(f"Remaining requests: {remaining}")
```

**Logging:**
```python
import logging

# Rate limiter logs important events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dms.rate_limiter")

# Logs include:
# - Client cleanup operations
# - Redis connection status
# - Error conditions
```

## Best Practices

### 1. Choose Appropriate Limits

```python
# Too strict - users frustrated
limiter = RateLimiter(requests=10, window=3600)  # Only 10/hour

# Too relaxed - no protection
limiter = RateLimiter(requests=100000, window=1)  # 100k/second

# Good balance
limiter = RateLimiter(requests=100, window=60)  # 100/minute
```

### 2. Use Different Limits for Different Operations

```python
# Expensive operations
export_limiter = RateLimiter(requests=10, window=300)  # 10 per 5min

# Cheap operations
read_limiter = RateLimiter(requests=1000, window=60)  # 1000/min

# Authentication
auth_limiter = RateLimiter(requests=5, window=60)  # 5/min
```

### 3. Fail Open, Not Closed

```python
# Rate limiter fails open on errors
# Better to allow request than deny legitimate users

try:
    is_allowed, retry_after = limiter.is_allowed(client_id)
except Exception as e:
    logger.error(f"Rate limiter error: {e}")
    is_allowed = True  # Allow on error
```

### 4. Use Redis for Multi-Server Deployments

```python
# ❌ Don't use in-memory with multiple servers
# Each server tracks separately, limits not enforced

# ✅ Use Redis for distributed tracking
limiter = RedisRateLimiter(requests=100, window=60)
```

### 5. Monitor and Adjust

```python
# Track rate limit hits
rate_limit_exceeded_count = 0

def track_rate_limit():
    global rate_limit_exceeded_count
    is_allowed, retry_after = limiter.is_allowed(client_id)

    if not is_allowed:
        rate_limit_exceeded_count += 1
        logger.warning(
            f"Rate limit exceeded for {client_id}. "
            f"Total: {rate_limit_exceeded_count}"
        )

    return is_allowed, retry_after

# If too many hits, consider increasing limits
# If too few, limits may be too relaxed
```

## Testing

### Unit Tests

```python
import pytest
from src.core.rate_limiter import RateLimiter

def test_rate_limiting():
    limiter = RateLimiter(requests=3, window=60)

    # First 3 should succeed
    for i in range(3):
        is_allowed, _ = limiter.is_allowed("test_client")
        assert is_allowed is True

    # 4th should fail
    is_allowed, retry_after = limiter.is_allowed("test_client")
    assert is_allowed is False
    assert retry_after > 0
```

### Integration Tests

```python
from fastapi.testclient import TestClient

def test_rate_limit_integration():
    client = TestClient(app)

    # Make requests up to limit
    for i in range(100):
        response = client.get("/api/data")
        assert response.status_code == 200

    # Next request should be rate limited
    response = client.get("/api/data")
    assert response.status_code == 429
    assert "retry_after" in response.json()
```

### Load Tests

```python
import asyncio
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_data(self):
        response = self.client.get("/api/data")

        if response.status_code == 429:
            # Rate limited
            retry_after = response.headers.get("Retry-After")
            print(f"Rate limited. Retry after {retry_after}s")
```

## Troubleshooting

### High Rate Limit Rejections

**Problem:** Too many 429 responses

**Solutions:**
1. Increase limits for tier
2. Use token bucket for burst traffic
3. Check for misbehaving clients
4. Implement client-side backoff

### Redis Connection Issues

**Problem:** "Redis not available, falling back to in-memory"

**Solutions:**
1. Check Redis server is running: `redis-cli ping`
2. Verify connection settings (host, port)
3. Check network connectivity
4. Review firewall rules

### Memory Usage Growing

**Problem:** limiter.clients dictionary growing indefinitely

**Solutions:**
```python
# Enable automatic cleanup
from src.core.rate_limiter import start_cleanup_task
start_cleanup_task(limiter, interval=3600)

# Or manual cleanup
limiter.cleanup_old_clients(max_age=7200)
```

### Inconsistent Limits Across Servers

**Problem:** Different servers enforcing different limits

**Solution:**
```python
# Use Redis for centralized tracking
limiter = RedisRateLimiter(requests=100, window=60)
```

## API Reference

### RateLimiter

```python
class RateLimiter:
    def __init__(self, requests: int, window: int)
    def is_allowed(self, client_id: str) -> tuple[bool, Optional[int]]
    def get_remaining(self, client_id: str) -> int
    def reset(self, client_id: str) -> None
    def cleanup_old_clients(self, max_age: int) -> None
```

### TokenBucketRateLimiter

```python
class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float)
    def is_allowed(self, client_id: str, tokens: int = 1) -> tuple[bool, Optional[int]]
    def reset(self, client_id: str) -> None
```

### RedisRateLimiter

```python
class RedisRateLimiter:
    def __init__(
        self,
        requests: int,
        window: int,
        redis_client=None,
        prefix: str = "rate_limit"
    )
    # Same methods as RateLimiter
```

### RateLimitTier

```python
class RateLimitTier:
    FREE = {"requests": 100, "window": 60}
    BASIC = {"requests": 500, "window": 60}
    PREMIUM = {"requests": 2000, "window": 60}
    ENTERPRISE = {"requests": 10000, "window": 60}

    @classmethod
    def get_limiter(cls, tier: str, use_redis: bool = False) -> RateLimiter
```

## Examples

See full examples in:
- `src/core/rate_limiter.py` - Module implementation
- `tests/unit/core/test_rate_limiter.py` - Comprehensive tests
- `doc-api-server.py` - Production integration

## Support

For questions or issues:
- Check test files for usage examples
- Review error logs for specific issues
- Consult production deployment guide
- Contact system administrator

---

**Last Updated:** 2026-01-18
**Version:** 1.0.0
**Status:** Production Ready ✅
