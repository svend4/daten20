"""
Microservices Module - v3.2

Microservices architecture components for enterprise scalability.

Modules:
- service_mesh: Service discovery, load balancing, circuit breakers
- api_gateway: API routing, protocol translation, rate limiting
- event_bus: Event-driven architecture with CQRS and Event Sourcing
- config_server: Centralized configuration management
- distributed_tracing: OpenTelemetry integration (future)
- container_orchestration: Kubernetes operators (future)

Version: 3.2.0
"""

__version__ = '3.2.0'

# Service Mesh
from .service_mesh import (
    ServiceMesh,
    ServiceRegistry,
    ServiceInstance,
    LoadBalancer,
    CircuitBreaker,
    HealthChecker,
    ServiceStatus,
    LoadBalancingAlgorithm,
    CircuitState,
    DiscoveryBackend,
    HealthCheckConfig,
    CircuitBreakerConfig,
    RetryPolicy,
    get_service_mesh
)

# API Gateway
from .api_gateway import (
    APIGateway,
    Router,
    Route,
    AuthManager,
    APIKey,
    ResponseCache,
    TokenBucket,
    SlidingWindowRateLimiter,
    Request,
    Response,
    Protocol,
    AuthMethod,
    HTTPMethod,
    RateLimitAlgorithm,
    RateLimitConfig,
    get_api_gateway
)

# Event-Driven Architecture
from .event_bus import (
    EventBus,
    EventStore,
    CommandBus,
    QueryBus,
    Event,
    Command,
    Query,
    Projection,
    Saga,
    EventSourcingRepository,
    EventPriority,
    CommandStatus,
    get_event_store,
    get_event_bus,
    get_command_bus,
    get_query_bus
)

# Configuration Management
from .config_server import (
    ConfigServer,
    ConfigStore,
    FeatureFlagManager,
    FeatureFlag,
    ConfigValue,
    ConfigChangeEvent,
    Environment,
    FeatureFlagType,
    ConfigChangeType,
    get_config_server
)

__all__ = [
    # Service Mesh
    'ServiceMesh',
    'ServiceRegistry',
    'ServiceInstance',
    'LoadBalancer',
    'CircuitBreaker',
    'HealthChecker',
    'ServiceStatus',
    'LoadBalancingAlgorithm',
    'CircuitState',
    'DiscoveryBackend',
    'HealthCheckConfig',
    'CircuitBreakerConfig',
    'RetryPolicy',
    'get_service_mesh',
    # API Gateway
    'APIGateway',
    'Router',
    'Route',
    'AuthManager',
    'APIKey',
    'ResponseCache',
    'TokenBucket',
    'SlidingWindowRateLimiter',
    'Request',
    'Response',
    'Protocol',
    'AuthMethod',
    'HTTPMethod',
    'RateLimitAlgorithm',
    'RateLimitConfig',
    'get_api_gateway',
    # Event-Driven Architecture
    'EventBus',
    'EventStore',
    'CommandBus',
    'QueryBus',
    'Event',
    'Command',
    'Query',
    'Projection',
    'Saga',
    'EventSourcingRepository',
    'EventPriority',
    'CommandStatus',
    'get_event_store',
    'get_event_bus',
    'get_command_bus',
    'get_query_bus',
    # Configuration Management
    'ConfigServer',
    'ConfigStore',
    'FeatureFlagManager',
    'FeatureFlag',
    'ConfigValue',
    'ConfigChangeEvent',
    'Environment',
    'FeatureFlagType',
    'ConfigChangeType',
    'get_config_server',
]
