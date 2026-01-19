"""
Microservices Module - v3.2

Microservices architecture components for enterprise scalability.

Modules:
- service_mesh: Service discovery, load balancing, circuit breakers
- api_gateway: API routing, protocol translation, rate limiting
- event_bus: Event-driven architecture with CQRS and Event Sourcing
- config_server: Centralized configuration management
- service_registry: Service registration, discovery, and health monitoring
- distributed_tracing: OpenTelemetry integration with Jaeger/Zipkin support
- orchestration: Kubernetes operators and container orchestration

Version: 3.2.0 (Complete)
"""

__version__ = "3.2.0"

# API Gateway
from .api_gateway import (
    APIGateway,
    APIKey,
    AuthManager,
    AuthMethod,
    HTTPMethod,
    Protocol,
    RateLimitAlgorithm,
    RateLimitConfig,
    Request,
    Response,
    ResponseCache,
    Route,
    Router,
    SlidingWindowRateLimiter,
    TokenBucket,
    get_api_gateway,
)

# Configuration Management
from .config_server import (
    ConfigChangeEvent,
    ConfigChangeType,
    ConfigServer,
    ConfigStore,
    ConfigValue,
    Environment,
    FeatureFlag,
    FeatureFlagManager,
    FeatureFlagType,
    get_config_server,
)

# Distributed Tracing
from .distributed_tracing import (
    ConsoleSpanExporter,
    JaegerSpanExporter,
    Span,
    SpanContext,
    SpanEvent,
    SpanExporter,
    SpanKind,
    SpanLink,
)
from .distributed_tracing import SpanStatus as TracingSpanStatus
from .distributed_tracing import (
    Trace,
    TraceAnalyzer,
    Tracer,
    TracingBackend,
    ZipkinSpanExporter,
)

# Event-Driven Architecture
from .event_bus import (
    Command,
    CommandBus,
    CommandStatus,
    Event,
    EventBus,
    EventPriority,
    EventSourcingRepository,
    EventStore,
    Projection,
    Query,
    QueryBus,
    Saga,
    get_command_bus,
    get_event_bus,
    get_event_store,
    get_query_bus,
)

# Container Orchestration
from .orchestration import (
    AutoscalingConfig,
    ContainerSpec,
    DeploymentController,
    DeploymentStrategy,
    HelmChartGenerator,
    KubernetesManifest,
    KubernetesOperator,
    NetworkPolicyRule,
    Probe,
    ProbeType,
    ResourceRequirements,
    ResourceType,
)

# Service Mesh
from .service_mesh import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    DiscoveryBackend,
    HealthCheckConfig,
    HealthChecker,
    LoadBalancer,
    LoadBalancingAlgorithm,
    RetryPolicy,
    ServiceInstance,
    ServiceMesh,
    ServiceRegistry,
    ServiceStatus,
    get_service_mesh,
)

# Service Registry & Discovery
from .service_registry import (
    ConsulServiceRegistry,
    DiscoveryType,
    EurekaServiceRegistry,
    HealthCheck,
    LoadMetrics,
)
from .service_registry import ServiceInstance as RegistryServiceInstance
from .service_registry import (
    ServiceMetadata,
)
from .service_registry import ServiceRegistry as RegistryServiceRegistry
from .service_registry import ServiceStatus as RegistryServiceStatus
from .service_registry import (
    deregister_service,
    discover_services,
    get_registry,
    register_service,
)

__all__ = [
    # Service Mesh
    "ServiceMesh",
    "ServiceRegistry",
    "ServiceInstance",
    "LoadBalancer",
    "CircuitBreaker",
    "HealthChecker",
    "ServiceStatus",
    "LoadBalancingAlgorithm",
    "CircuitState",
    "DiscoveryBackend",
    "HealthCheckConfig",
    "CircuitBreakerConfig",
    "RetryPolicy",
    "get_service_mesh",
    # API Gateway
    "APIGateway",
    "Router",
    "Route",
    "AuthManager",
    "APIKey",
    "ResponseCache",
    "TokenBucket",
    "SlidingWindowRateLimiter",
    "Request",
    "Response",
    "Protocol",
    "AuthMethod",
    "HTTPMethod",
    "RateLimitAlgorithm",
    "RateLimitConfig",
    "get_api_gateway",
    # Event-Driven Architecture
    "EventBus",
    "EventStore",
    "CommandBus",
    "QueryBus",
    "Event",
    "Command",
    "Query",
    "Projection",
    "Saga",
    "EventSourcingRepository",
    "EventPriority",
    "CommandStatus",
    "get_event_store",
    "get_event_bus",
    "get_command_bus",
    "get_query_bus",
    # Configuration Management
    "ConfigServer",
    "ConfigStore",
    "FeatureFlagManager",
    "FeatureFlag",
    "ConfigValue",
    "ConfigChangeEvent",
    "Environment",
    "FeatureFlagType",
    "ConfigChangeType",
    "get_config_server",
    # Service Registry & Discovery
    "RegistryServiceRegistry",
    "ConsulServiceRegistry",
    "EurekaServiceRegistry",
    "RegistryServiceInstance",
    "ServiceMetadata",
    "HealthCheck",
    "LoadMetrics",
    "RegistryServiceStatus",
    "DiscoveryType",
    "get_registry",
    "register_service",
    "deregister_service",
    "discover_services",
    # Distributed Tracing
    "Tracer",
    "Span",
    "SpanContext",
    "Trace",
    "SpanEvent",
    "SpanLink",
    "SpanKind",
    "TracingSpanStatus",
    "SpanExporter",
    "ConsoleSpanExporter",
    "JaegerSpanExporter",
    "ZipkinSpanExporter",
    "TracingBackend",
    "TraceAnalyzer",
    # Container Orchestration
    "KubernetesManifest",
    "HelmChartGenerator",
    "KubernetesOperator",
    "DeploymentController",
    "ContainerSpec",
    "ResourceRequirements",
    "Probe",
    "AutoscalingConfig",
    "NetworkPolicyRule",
    "DeploymentStrategy",
    "ResourceType",
    "ProbeType",
]
