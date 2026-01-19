"""
API Gateway Module

Provides comprehensive API gateway functionality including request routing,
rate limiting, API key management, request/response logging, and analytics.
"""

# Analytics
from src.gateway.analytics import (
    AnomalyAlert,
    APIAnalytics,
    ClientMetrics,
    EndpointMetrics,
    MetricsCollector,
    MetricType,
    RequestMetrics,
    TimeSeriesPoint,
    TimeWindow,
    get_api_analytics,
    record_api_request,
)

# API Key Management
from src.gateway.api_keys import (
    APIKey,
    APIKeyManager,
    APIKeyMetadata,
    APIKeyScope,
    APIKeyStatus,
    APIKeyUsage,
    create_api_key,
    get_api_key_manager,
    validate_api_key,
)

# Core Gateway
from src.gateway.core import (
    APIGateway,
    CircuitBreakerState,
    HTTPMethod,
    Request,
    Response,
    Route,
    RouteStatus,
    get_gateway,
)

# Rate Limiting
from src.gateway.rate_limiter import (
    RATE_LIMIT_TIERS,
    FixedWindow,
    MultiLevelRateLimiter,
    RateLimitAlgorithm,
    RateLimitConfig,
    RateLimiter,
    RateLimitResult,
    RateLimitScope,
    SlidingWindow,
    TokenBucket,
    configure_rate_limiter,
    get_rate_limiter,
)

# Request/Response Logging
from src.gateway.request_logging import (
    APILogEntry,
    DataSanitizer,
    LogLevel,
    RequestLog,
    RequestLogger,
    ResponseLog,
    SanitizationLevel,
    configure_request_logger,
    get_request_logger,
)

__all__ = [
    # Core
    "HTTPMethod",
    "RouteStatus",
    "Route",
    "Request",
    "Response",
    "CircuitBreakerState",
    "APIGateway",
    "get_gateway",
    # Rate Limiting
    "RateLimitAlgorithm",
    "RateLimitScope",
    "RateLimitConfig",
    "RateLimitResult",
    "TokenBucket",
    "SlidingWindow",
    "FixedWindow",
    "RateLimiter",
    "MultiLevelRateLimiter",
    "RATE_LIMIT_TIERS",
    "get_rate_limiter",
    "configure_rate_limiter",
    # API Keys
    "APIKeyStatus",
    "APIKeyScope",
    "APIKeyMetadata",
    "APIKeyUsage",
    "APIKey",
    "APIKeyManager",
    "get_api_key_manager",
    "create_api_key",
    "validate_api_key",
    # Logging
    "LogLevel",
    "SanitizationLevel",
    "RequestLog",
    "ResponseLog",
    "APILogEntry",
    "DataSanitizer",
    "RequestLogger",
    "get_request_logger",
    "configure_request_logger",
    # Analytics
    "MetricType",
    "TimeWindow",
    "RequestMetrics",
    "EndpointMetrics",
    "ClientMetrics",
    "TimeSeriesPoint",
    "AnomalyAlert",
    "MetricsCollector",
    "APIAnalytics",
    "get_api_analytics",
    "record_api_request",
]
