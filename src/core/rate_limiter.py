"""
Rate Limiting Module

Provides rate limiting functionality to protect against:
- DoS attacks
- Brute force attempts
- API abuse
- Resource exhaustion

Strategies:
- Fixed window
- Sliding window
- Token bucket
- Leaky bucket
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from threading import Lock
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("dms.rate_limiter")


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            retry_after: Seconds until next request allowed
        """
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.

    Thread-safe implementation with per-client tracking.
    """

    def __init__(self, requests: int = 100, window: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests: Maximum requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed for client.

        Args:
            client_id: Unique client identifier (IP, user ID, API key)

        Returns:
            (is_allowed, retry_after_seconds)
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window

            # Clean up old requests
            self.clients[client_id] = [req_time for req_time in self.clients[client_id] if req_time > window_start]

            # Check if limit exceeded
            if len(self.clients[client_id]) >= self.requests:
                oldest_request = self.clients[client_id][0]
                retry_after = int(oldest_request + self.window - now) + 1
                return False, retry_after

            # Record new request
            self.clients[client_id].append(now)
            return True, None

    def reset(self, client_id: str):
        """Reset rate limit for specific client."""
        with self.lock:
            if client_id in self.clients:
                del self.clients[client_id]

    def get_remaining(self, client_id: str) -> int:
        """
        Get remaining requests for client.

        Args:
            client_id: Client identifier

        Returns:
            Number of remaining requests
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window

            # Count requests in current window
            current_requests = sum(1 for req_time in self.clients[client_id] if req_time > window_start)

            return max(0, self.requests - current_requests)

    def cleanup_old_clients(self, max_age: int = 3600):
        """
        Remove inactive clients from memory.

        Args:
            max_age: Maximum age in seconds for client data
        """
        with self.lock:
            now = time.time()
            cutoff = now - max_age

            # Find clients with no recent requests
            inactive_clients = [
                client_id for client_id, requests in self.clients.items() if not requests or requests[-1] < cutoff
            ]

            # Remove inactive clients
            for client_id in inactive_clients:
                del self.clients[client_id]

            if inactive_clients:
                logger.info(f"Cleaned up {len(inactive_clients)} inactive clients")


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter.

    More flexible than fixed window - allows bursts.
    """

    def __init__(self, capacity: int = 100, refill_rate: float = 10):
        """
        Initialize token bucket limiter.

        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict[str, float]] = {}
        self.lock = Lock()

    def is_allowed(self, client_id: str, tokens: int = 1) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed.

        Args:
            client_id: Client identifier
            tokens: Number of tokens required

        Returns:
            (is_allowed, retry_after_seconds)
        """
        with self.lock:
            now = time.time()

            # Initialize bucket for new client
            if client_id not in self.buckets:
                self.buckets[client_id] = {"tokens": float(self.capacity), "last_refill": now}

            bucket = self.buckets[client_id]

            # Refill tokens
            time_passed = now - bucket["last_refill"]
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + time_passed * self.refill_rate)
            bucket["last_refill"] = now

            # Check if enough tokens
            if bucket["tokens"] >= tokens:
                bucket["tokens"] -= tokens
                return True, None
            else:
                # Calculate retry after
                tokens_needed = tokens - bucket["tokens"]
                retry_after = int(tokens_needed / self.refill_rate) + 1
                return False, retry_after

    def reset(self, client_id: str):
        """Reset bucket for client."""
        with self.lock:
            if client_id in self.buckets:
                del self.buckets[client_id]


# Flask decorator for rate limiting
def rate_limit(requests: int = 100, window: int = 60, key_func: Optional[Callable] = None):
    """
    Decorator for Flask routes to add rate limiting.

    Args:
        requests: Maximum requests allowed
        window: Time window in seconds
        key_func: Optional function to extract client ID from request

    Example:
        @app.route('/api/data')
        @rate_limit(requests=10, window=60)
        def get_data():
            return {'data': 'value'}
    """
    limiter = RateLimiter(requests, window)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            if key_func:
                client_id = key_func()
            else:
                # Try to import Flask request
                try:
                    from flask import request

                    # Use IP + User-Agent as identifier
                    client_id = f"{request.remote_addr}:{request.headers.get('User-Agent', '')[:50]}"
                except ImportError:
                    # Fallback to generic identifier
                    client_id = "default"

            # Check rate limit
            is_allowed, retry_after = limiter.is_allowed(client_id)

            if not is_allowed:
                raise RateLimitExceeded(f"Rate limit exceeded: {requests} requests per {window} seconds", retry_after)

            # Add rate limit headers
            try:
                from flask import g

                g.rate_limit_remaining = limiter.get_remaining(client_id)
                g.rate_limit_limit = requests
                g.rate_limit_window = window
            except:
                pass

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Global rate limiters for different tiers
class GlobalRateLimiters:
    """Global rate limiters for different use cases."""

    # API rate limits
    api_default = RateLimiter(requests=100, window=60)  # 100 req/min
    api_strict = RateLimiter(requests=10, window=60)  # 10 req/min
    api_relaxed = RateLimiter(requests=1000, window=60)  # 1000 req/min

    # Authentication rate limits (prevent brute force)
    auth_login = RateLimiter(requests=5, window=60)  # 5 attempts/min
    auth_register = RateLimiter(requests=3, window=300)  # 3 reg/5min
    auth_password_reset = RateLimiter(requests=3, window=3600)  # 3/hour

    # Resource-intensive operations
    export_operations = RateLimiter(requests=10, window=300)  # 10/5min
    search_operations = RateLimiter(requests=50, window=60)  # 50/min

    # Token bucket for bursty traffic
    api_burst = TokenBucketRateLimiter(capacity=50, refill_rate=10)


# Convenience functions
def check_rate_limit(client_id: str, limiter: RateLimiter) -> bool:
    """
    Check rate limit and raise exception if exceeded.

    Args:
        client_id: Client identifier
        limiter: RateLimiter instance

    Returns:
        True if allowed

    Raises:
        RateLimitExceeded: If limit exceeded
    """
    is_allowed, retry_after = limiter.is_allowed(client_id)

    if not is_allowed:
        raise RateLimitExceeded("Rate limit exceeded. Please try again later.", retry_after)

    return True


def get_client_id_from_request() -> str:
    """
    Extract client identifier from Flask request.

    Returns:
        Client identifier string
    """
    try:
        from flask import request

        # Priority: API key > User ID > IP + User-Agent
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Try to get user ID from auth
        user_id = getattr(request, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fallback to IP + User-Agent
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")[:50]
        return f"ip:{ip}:{user_agent}"

    except ImportError:
        return "default"


# Flask error handler
def handle_rate_limit_exceeded(error: RateLimitExceeded):
    """
    Flask error handler for rate limit exceeded.

    Returns:
        JSON response with 429 status code
    """
    try:
        from flask import jsonify

        response = jsonify({"error": "rate_limit_exceeded", "message": error.message, "retry_after": error.retry_after})
        response.status_code = 429

        if error.retry_after:
            response.headers["Retry-After"] = str(error.retry_after)

        return response

    except ImportError:
        # Return dict for non-Flask usage
        return {"error": "rate_limit_exceeded", "message": error.message, "retry_after": error.retry_after}, 429


# Background task to cleanup old clients
def start_cleanup_task(limiter: RateLimiter, interval: int = 3600):
    """
    Start background task to cleanup old clients.

    Args:
        limiter: RateLimiter instance
        interval: Cleanup interval in seconds
    """
    import threading

    def cleanup_loop():
        while True:
            time.sleep(interval)
            limiter.cleanup_old_clients()
            logger.info("Rate limiter cleanup completed")

    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info(f"Started rate limiter cleanup task (interval: {interval}s)")


# Redis-backed rate limiter for distributed systems
class RedisRateLimiter:
    """
    Redis-backed rate limiter for distributed systems.

    Uses Redis for centralized rate limiting across multiple servers.
    """

    def __init__(self, requests: int = 100, window: int = 60, redis_client=None, prefix: str = "rate_limit"):
        """
        Initialize Redis rate limiter.

        Args:
            requests: Maximum requests allowed
            window: Time window in seconds
            redis_client: Redis client instance (optional)
            prefix: Key prefix for Redis
        """
        self.requests = requests
        self.window = window
        self.prefix = prefix
        self.redis_client = redis_client

        if self.redis_client is None:
            try:
                import redis
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis for rate limiting")
            except Exception as e:
                logger.warning(f"Redis not available, falling back to in-memory: {e}")
                self.fallback_limiter = RateLimiter(requests, window)
                self.redis_client = None

    def _get_key(self, client_id: str) -> str:
        """Get Redis key for client."""
        return f"{self.prefix}:{client_id}"

    def is_allowed(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed.

        Args:
            client_id: Client identifier

        Returns:
            (is_allowed, retry_after_seconds)
        """
        if self.redis_client is None:
            return self.fallback_limiter.is_allowed(client_id)

        try:
            key = self._get_key(client_id)
            now = time.time()

            # Use Redis sorted set to store timestamps
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, now - self.window)

            # Count current requests
            current_requests = self.redis_client.zcard(key)

            if current_requests >= self.requests:
                # Get oldest request to calculate retry_after
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = int(oldest_time + self.window - now) + 1
                    return False, retry_after
                return False, self.window

            # Add new request
            self.redis_client.zadd(key, {str(now): now})

            # Set expiration
            self.redis_client.expire(key, self.window * 2)

            return True, None

        except Exception as e:
            logger.error(f"Redis rate limiter error: {e}")
            # Fallback to allowing request on error
            return True, None

    def reset(self, client_id: str):
        """Reset rate limit for client."""
        if self.redis_client is None:
            self.fallback_limiter.reset(client_id)
            return

        try:
            key = self._get_key(client_id)
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis reset error: {e}")

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        if self.redis_client is None:
            return self.fallback_limiter.get_remaining(client_id)

        try:
            key = self._get_key(client_id)
            now = time.time()

            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, now - self.window)

            # Count current requests
            current_requests = self.redis_client.zcard(key)

            return max(0, self.requests - current_requests)

        except Exception as e:
            logger.error(f"Redis get_remaining error: {e}")
            return self.requests


# FastAPI middleware for rate limiting
class FastAPIRateLimitMiddleware:
    """
    FastAPI middleware for rate limiting.

    Usage:
        app.add_middleware(FastAPIRateLimitMiddleware, limiter=limiter)
    """

    def __init__(self, app, limiter: RateLimiter, key_func=None):
        """
        Initialize middleware.

        Args:
            app: FastAPI application
            limiter: RateLimiter instance
            key_func: Optional function to extract client ID from request
        """
        self.app = app
        self.limiter = limiter
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, request) -> str:
        """Default function to extract client ID from request."""
        # Priority: API key > User ID > IP
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Try to get user from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fallback to IP + User-Agent
        ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "")[:50]
        return f"ip:{ip}:{user_agent}"

    async def __call__(self, scope, receive, send):
        """Process request with rate limiting."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request
        from starlette.responses import JSONResponse

        request = Request(scope, receive)

        # Get client ID
        client_id = self.key_func(request)

        # Check rate limit
        is_allowed, retry_after = self.limiter.is_allowed(client_id)

        if not is_allowed:
            # Return 429 response
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)} if retry_after else {}
            )
            await response(scope, receive, send)
            return

        # Add rate limit headers
        remaining = self.limiter.get_remaining(client_id)

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"X-RateLimit-Limit", str(self.limiter.requests).encode()))
                headers.append((b"X-RateLimit-Remaining", str(remaining).encode()))
                headers.append((b"X-RateLimit-Reset", str(int(time.time() + self.limiter.window)).encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


# FastAPI dependency for rate limiting
def create_rate_limit_dependency(limiter: RateLimiter, key_func=None):
    """
    Create FastAPI dependency for rate limiting.

    Usage:
        rate_limit_dep = create_rate_limit_dependency(limiter)

        @app.get("/api/data")
        async def get_data(rate_limit: None = Depends(rate_limit_dep)):
            return {"data": "value"}
    """
    async def rate_limit_dependency(request):
        """Check rate limit for request."""
        # Get client ID
        if key_func:
            client_id = key_func(request)
        else:
            api_key = request.headers.get("X-API-Key")
            if api_key:
                client_id = f"api_key:{api_key}"
            else:
                ip = request.client.host if request.client else "unknown"
                user_agent = request.headers.get("User-Agent", "")[:50]
                client_id = f"ip:{ip}:{user_agent}"

        # Check rate limit
        is_allowed, retry_after = limiter.is_allowed(client_id)

        if not is_allowed:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)} if retry_after else {}
            )

        return None

    return rate_limit_dependency


# Rate limit tiers configuration
class RateLimitTier:
    """Rate limit tier configuration."""

    FREE = {"requests": 100, "window": 60, "name": "Free"}  # 100 req/min
    BASIC = {"requests": 500, "window": 60, "name": "Basic"}  # 500 req/min
    PREMIUM = {"requests": 2000, "window": 60, "name": "Premium"}  # 2000 req/min
    ENTERPRISE = {"requests": 10000, "window": 60, "name": "Enterprise"}  # 10000 req/min

    @classmethod
    def get_limiter(cls, tier: str, use_redis: bool = False) -> RateLimiter:
        """
        Get rate limiter for tier.

        Args:
            tier: Tier name (free, basic, premium, enterprise)
            use_redis: Whether to use Redis backend

        Returns:
            RateLimiter instance
        """
        tier_config = getattr(cls, tier.upper(), cls.FREE)

        if use_redis:
            return RedisRateLimiter(
                requests=tier_config["requests"],
                window=tier_config["window"],
                prefix=f"rate_limit:{tier.lower()}"
            )
        else:
            return RateLimiter(
                requests=tier_config["requests"],
                window=tier_config["window"]
            )


# Example usage
if __name__ == "__main__":
    # Test in-memory rate limiter
    print("=" * 60)
    print("Testing in-memory rate limiter (5 requests per 10 seconds)...")
    print("=" * 60)
    limiter = RateLimiter(requests=5, window=10)

    for i in range(10):
        is_allowed, retry_after = limiter.is_allowed("test_client")
        remaining = limiter.get_remaining("test_client")

        if is_allowed:
            print(f"Request {i+1}: ✅ Allowed (remaining: {remaining})")
        else:
            print(f"Request {i+1}: ❌ Rate limit exceeded (retry after: {retry_after}s)")

        time.sleep(1)

    print("\n" + "=" * 60)
    print("Testing Redis rate limiter...")
    print("=" * 60)

    # Test Redis rate limiter
    redis_limiter = RedisRateLimiter(requests=5, window=10)

    for i in range(7):
        is_allowed, retry_after = redis_limiter.is_allowed("test_redis_client")
        remaining = redis_limiter.get_remaining("test_redis_client")

        if is_allowed:
            print(f"Request {i+1}: ✅ Allowed (remaining: {remaining})")
        else:
            print(f"Request {i+1}: ❌ Rate limit exceeded (retry after: {retry_after}s)")

    print("\n" + "=" * 60)
    print("Testing rate limit tiers...")
    print("=" * 60)

    for tier_name in ["FREE", "BASIC", "PREMIUM", "ENTERPRISE"]:
        limiter_tier = RateLimitTier.get_limiter(tier_name)
        print(f"{tier_name}: {limiter_tier.requests} requests per {limiter_tier.window} seconds")
