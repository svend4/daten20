"""
API Gateway Module

Provides comprehensive API gateway functionality including request routing,
rate limiting, API key management, request/response logging, and analytics.
"""

# Core Gateway
from src.gateway.core import (
    HTTPMethod,
    RouteStatus,
    Route,
    Request,
    Response,
    CircuitBreakerState,
    APIGateway,
    get_gateway,
)

# Rate Limiting
from src.gateway.rate_limiter import (
    RateLimitAlgorithm,
    RateLimitScope,
    RateLimitConfig,
    RateLimitResult,
    TokenBucket,
    SlidingWindow,
    FixedWindow,
    RateLimiter,
    MultiLevelRateLimiter,
    RATE_LIMIT_TIERS,
    get_rate_limiter,
    configure_rate_limiter,
)

# API Key Management
from src.gateway.api_keys import (
    APIKeyStatus,
    APIKeyScope,
    APIKeyMetadata,
    APIKeyUsage,
    APIKey,
    APIKeyManager,
    get_api_key_manager,
    create_api_key,
    validate_api_key,
)

# Request/Response Logging
from src.gateway.request_logging import (
    LogLevel,
    SanitizationLevel,
    RequestLog,
    ResponseLog,
    APILogEntry,
    DataSanitizer,
    RequestLogger,
    get_request_logger,
    configure_request_logger,
)

# Analytics
from src.gateway.analytics import (
    MetricType,
    TimeWindow,
    RequestMetrics,
    EndpointMetrics,
    ClientMetrics,
    TimeSeriesPoint,
    AnomalyAlert,
    MetricsCollector,
    APIAnalytics,
    get_api_analytics,
    record_api_request,
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
