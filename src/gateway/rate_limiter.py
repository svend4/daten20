"""
API Gateway Rate Limiter

Implements rate limiting and throttling for API endpoints using
Token Bucket and Sliding Window algorithms.
"""

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms"""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(str, Enum):
    """Rate limit scope"""

    USER = "user"
    API_KEY = "api_key"
    IP = "ip"
    ENDPOINT = "endpoint"
    GLOBAL = "global"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    max_requests: int
    window_seconds: int
    burst_allowance: int = 0  # Additional burst capacity
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    scope: RateLimitScope = RateLimitScope.USER


@dataclass
class RateLimitResult:
    """Result of rate limit check"""

    allowed: bool
    remaining: int
    reset_at: datetime
    retry_after: Optional[int] = None  # Seconds until next request allowed
    limit: int = 0
    current_usage: int = 0


class TokenBucket:
    """Token Bucket algorithm implementation"""

    def __init__(self, capacity: int, refill_rate: float, initial_tokens: Optional[int] = None):  # Tokens per second
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = initial_tokens if initial_tokens is not None else capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill

        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate

        if tokens_to_add > 0:
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now

    def get_available_tokens(self) -> int:
        """Get number of available tokens"""
        with self.lock:
            self._refill()
            return int(self.tokens)

    def time_until_tokens(self, required_tokens: int) -> float:
        """Get time in seconds until required tokens are available"""
        with self.lock:
            self._refill()

            if self.tokens >= required_tokens:
                return 0.0

            tokens_needed = required_tokens - self.tokens
            return tokens_needed / self.refill_rate


class SlidingWindow:
    """Sliding Window algorithm implementation"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
        self.lock = threading.Lock()

    def allow_request(self) -> Tuple[bool, int]:
        """
        Check if request is allowed

        Returns:
            Tuple of (allowed, remaining_requests)
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Remove old requests outside window
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()

            # Check if under limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                remaining = self.max_requests - len(self.requests)
                return True, remaining

            remaining = 0
            return False, remaining

    def get_reset_time(self) -> datetime:
        """Get time when window resets"""
        if not self.requests:
            return datetime.utcnow()

        oldest_request = self.requests[0]
        reset_at = oldest_request + self.window_seconds
        return datetime.fromtimestamp(reset_at)

    def get_remaining_requests(self) -> int:
        """Get number of remaining requests in current window"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Remove old requests
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()

            return self.max_requests - len(self.requests)


class FixedWindow:
    """Fixed Window algorithm implementation"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.count = 0
        self.window_start = time.time()
        self.lock = threading.Lock()

    def allow_request(self) -> Tuple[bool, int]:
        """
        Check if request is allowed

        Returns:
            Tuple of (allowed, remaining_requests)
        """
        with self.lock:
            now = time.time()

            # Check if we need to reset window
            if now - self.window_start >= self.window_seconds:
                self.count = 0
                self.window_start = now

            # Check if under limit
            if self.count < self.max_requests:
                self.count += 1
                remaining = self.max_requests - self.count
                return True, remaining

            return False, 0

    def get_reset_time(self) -> datetime:
        """Get time when window resets"""
        reset_at = self.window_start + self.window_seconds
        return datetime.fromtimestamp(reset_at)


class RateLimiter:
    """Rate limiter implementation"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.limiters: Dict[str, Any] = {}
        self.lock = threading.Lock()

    def _get_limiter_key(self, identifier: str) -> str:
        """Get unique key for rate limiter"""
        return f"{self.config.scope.value}:{identifier}"

    def _get_or_create_limiter(self, identifier: str) -> Any:
        """Get or create rate limiter for identifier"""
        key = self._get_limiter_key(identifier)

        with self.lock:
            if key not in self.limiters:
                if self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    capacity = self.config.max_requests + self.config.burst_allowance
                    refill_rate = self.config.max_requests / self.config.window_seconds
                    self.limiters[key] = TokenBucket(capacity, refill_rate)

                elif self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                    self.limiters[key] = SlidingWindow(self.config.max_requests, self.config.window_seconds)

                elif self.config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                    self.limiters[key] = FixedWindow(self.config.max_requests, self.config.window_seconds)

            return self.limiters[key]

    def check_rate_limit(self, identifier: str) -> RateLimitResult:
        """
        Check if request should be rate limited

        Args:
            identifier: Unique identifier (user_id, api_key, ip, etc.)

        Returns:
            Rate limit result
        """
        limiter = self._get_or_create_limiter(identifier)

        if self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            allowed = limiter.consume(1)
            remaining = limiter.get_available_tokens()
            retry_after = None if allowed else int(limiter.time_until_tokens(1))

            reset_at = datetime.utcnow() + timedelta(seconds=self.config.window_seconds)

            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_at=reset_at,
                retry_after=retry_after,
                limit=self.config.max_requests,
                current_usage=self.config.max_requests - remaining,
            )

        elif self.config.algorithm in [RateLimitAlgorithm.SLIDING_WINDOW, RateLimitAlgorithm.FIXED_WINDOW]:
            allowed, remaining = limiter.allow_request()
            reset_at = limiter.get_reset_time()

            retry_after = None
            if not allowed:
                retry_after = int((reset_at - datetime.utcnow()).total_seconds())

            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_at=reset_at,
                retry_after=retry_after,
                limit=self.config.max_requests,
                current_usage=self.config.max_requests - remaining,
            )

        return RateLimitResult(
            allowed=True, remaining=self.config.max_requests, reset_at=datetime.utcnow(), limit=self.config.max_requests
        )

    def reset_limit(self, identifier: str):
        """Reset rate limit for identifier"""
        key = self._get_limiter_key(identifier)

        with self.lock:
            if key in self.limiters:
                del self.limiters[key]


class MultiLevelRateLimiter:
    """Rate limiter with multiple levels (per-user, per-endpoint, global)"""

    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

    def add_limiter(self, name: str, config: RateLimitConfig):
        """Add rate limiter with specific configuration"""
        self.limiters[name] = RateLimiter(config)

    def check_rate_limits(self, identifiers: Dict[str, str]) -> Tuple[bool, List[RateLimitResult]]:
        """
        Check rate limits across all configured limiters

        Args:
            identifiers: Dictionary mapping limiter name to identifier

        Returns:
            Tuple of (all_allowed, results)
        """
        results = []
        all_allowed = True

        for name, limiter in self.limiters.items():
            identifier = identifiers.get(name)
            if identifier:
                result = limiter.check_rate_limit(identifier)
                results.append(result)

                if not result.allowed:
                    all_allowed = False

        return all_allowed, results

    def get_most_restrictive_result(self, results: List[RateLimitResult]) -> RateLimitResult:
        """Get most restrictive rate limit result"""
        if not results:
            return RateLimitResult(allowed=True, remaining=0, reset_at=datetime.utcnow())

        # Return first disallowed result, or result with least remaining
        disallowed = [r for r in results if not r.allowed]
        if disallowed:
            return disallowed[0]

        return min(results, key=lambda r: r.remaining)


# Pre-configured rate limit tiers
RATE_LIMIT_TIERS = {
    "free": RateLimitConfig(
        max_requests=100,
        window_seconds=3600,  # 100 requests per hour
        burst_allowance=10,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        scope=RateLimitScope.USER,
    ),
    "basic": RateLimitConfig(
        max_requests=1000,
        window_seconds=3600,  # 1000 requests per hour
        burst_allowance=50,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        scope=RateLimitScope.USER,
    ),
    "premium": RateLimitConfig(
        max_requests=10000,
        window_seconds=3600,  # 10000 requests per hour
        burst_allowance=100,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        scope=RateLimitScope.USER,
    ),
    "enterprise": RateLimitConfig(
        max_requests=100000,
        window_seconds=3600,  # 100000 requests per hour
        burst_allowance=1000,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        scope=RateLimitScope.USER,
    ),
}


# Global rate limiter instance
_global_rate_limiter: Optional[MultiLevelRateLimiter] = None


def get_rate_limiter() -> MultiLevelRateLimiter:
    """Get global rate limiter instance"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = MultiLevelRateLimiter()

        # Add default limiters
        _global_rate_limiter.add_limiter("user", RATE_LIMIT_TIERS["basic"])
        _global_rate_limiter.add_limiter(
            "global",
            RateLimitConfig(
                max_requests=100000,
                window_seconds=60,  # 100k requests per minute globally
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                scope=RateLimitScope.GLOBAL,
            ),
        )

    return _global_rate_limiter


def configure_rate_limiter(tier: str = "basic"):
    """Configure global rate limiter with specific tier"""
    limiter = get_rate_limiter()

    if tier in RATE_LIMIT_TIERS:
        limiter.add_limiter("user", RATE_LIMIT_TIERS[tier])
