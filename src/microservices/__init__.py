"""
Microservices Module - v3.2

Microservices architecture components for enterprise scalability.

Modules:
- service_mesh: Service discovery, load balancing, circuit breakers ✅
- api_gateway: API routing, protocol translation, rate limiting ✅
- event_bus: Event-driven architecture with CQRS and Event Sourcing ✅
- config_server: Centralized configuration management ✅
- service_registry: Service registration, discovery, and health monitoring ✅
- distributed_tracing: OpenTelemetry integration with Jaeger/Zipkin support ✅
- orchestration: Kubernetes operators and container orchestration ✅
- microservices_api: Unified Microservices API (single entry point) ✅

Version: 3.2.0 (Complete)
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

# Service Registry & Discovery
from .service_registry import (
    ServiceRegistry as RegistryServiceRegistry,
    ConsulServiceRegistry,
    EurekaServiceRegistry,
    ServiceInstance as RegistryServiceInstance,
    ServiceMetadata,
    HealthCheck,
    LoadMetrics,
    ServiceStatus as RegistryServiceStatus,
    DiscoveryType,
    get_registry,
    register_service,
    deregister_service,
    discover_services
)

# Distributed Tracing
from .distributed_tracing import (
    Tracer,
    Span,
    SpanContext,
    Trace,
    SpanEvent,
    SpanLink,
    SpanKind,
    SpanStatus as TracingSpanStatus,
    SpanExporter,
    ConsoleSpanExporter,
    JaegerSpanExporter,
    ZipkinSpanExporter,
    TracingBackend,
    TraceAnalyzer
)

# Container Orchestration
from .orchestration import (
    KubernetesManifest,
    HelmChartGenerator,
    KubernetesOperator,
    DeploymentController,
    ContainerSpec,
    ResourceRequirements,
    Probe,
    AutoscalingConfig,
    NetworkPolicyRule,
    DeploymentStrategy,
    ResourceType,
    ProbeType
)

# Unified Microservices API
from .microservices_api import (
    get_microservices_api,
    MicroservicesAPI,
    ServiceHealth,
    RouteConfig,
    EventHandler,
    TraceContext
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
    # Service Registry & Discovery
    'RegistryServiceRegistry',
    'ConsulServiceRegistry',
    'EurekaServiceRegistry',
    'RegistryServiceInstance',
    'ServiceMetadata',
    'HealthCheck',
    'LoadMetrics',
    'RegistryServiceStatus',
    'DiscoveryType',
    'get_registry',
    'register_service',
    'deregister_service',
    'discover_services',
    # Distributed Tracing
    'Tracer',
    'Span',
    'SpanContext',
    'Trace',
    'SpanEvent',
    'SpanLink',
    'SpanKind',
    'TracingSpanStatus',
    'SpanExporter',
    'ConsoleSpanExporter',
    'JaegerSpanExporter',
    'ZipkinSpanExporter',
    'TracingBackend',
    'TraceAnalyzer',
    # Container Orchestration
    'KubernetesManifest',
    'HelmChartGenerator',
    'KubernetesOperator',
    'DeploymentController',
    'ContainerSpec',
    'ResourceRequirements',
    'Probe',
    'AutoscalingConfig',
    'NetworkPolicyRule',
    'DeploymentStrategy',
    'ResourceType',
    'ProbeType',
    # Unified Microservices API
    'get_microservices_api',
    'MicroservicesAPI',
    'ServiceHealth',
    'RouteConfig',
    'EventHandler',
    'TraceContext',
]
