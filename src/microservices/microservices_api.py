"""
Unified Microservices API

Single entry point for all microservices architecture functionality.
Integrates all v3.2 microservices modules into a cohesive API.

Features:
- Service registration and discovery
- API Gateway management
- Event-driven architecture (CQRS, Event Sourcing)
- Centralized configuration
- Distributed tracing
- Circuit breaker patterns
- Load balancing
- Health checks

Modules Integrated:
- Service Mesh (discovery, load balancing, circuit breakers)
- API Gateway (routing, rate limiting, authentication)
- Event Bus (events, commands, queries, sagas)
- Config Server (configuration, feature flags)
- Service Registry (Consul, Eureka integration)
- Distributed Tracing (OpenTelemetry, Jaeger, Zipkin)
- Container Orchestration (Kubernetes, Helm)

Usage:
    >>> from src.microservices import MicroservicesAPI
    >>> api = MicroservicesAPI()
    >>>
    >>> # Register service
    >>> api.register_service("user-service", "http://localhost:8080")
    >>>
    >>> # Discover services
    >>> services = api.discover_services("user-service")
    >>>
    >>> # Publish event
    >>> api.publish_event("UserCreated", {"user_id": 123})
    >>>
    >>> # Get configuration
    >>> config = api.get_config("database.url")
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Import Microservices Modules
# ============================================================

try:
    from .service_mesh import ServiceMesh, ServiceInstance, LoadBalancingAlgorithm
    from .api_gateway import APIGateway, Route, HTTPMethod
    from .event_bus import EventBus, Event, Command, EventPriority
    from .config_server import ConfigServer, FeatureFlag
    from .service_registry import ServiceRegistry, DiscoveryType
    from .distributed_tracing import Tracer, SpanKind
    from .orchestration import KubernetesManifest, DeploymentStrategy
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some microservices modules not available: {e}")
    MODULES_AVAILABLE = False


# ============================================================
# Data Models
# ============================================================

class ServiceType(str, Enum):
    """Service types"""
    WEB = "web"
    API = "api"
    WORKER = "worker"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class ServiceConfig:
    """Service configuration"""
    service_id: str
    name: str
    host: str
    port: int
    service_type: ServiceType = ServiceType.API
    health_check_path: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIRouteConfig:
    """API route configuration"""
    path: str
    method: str
    service_id: str
    rate_limit: Optional[int] = None
    auth_required: bool = False
    timeout: int = 30


# ============================================================
# Unified Microservices API
# ============================================================

class MicroservicesAPI:
    """
    Unified Microservices API

    Single interface for all microservices operations.
    Integrates all v3.2 microservices modules.
    """

    def __init__(
        self,
        enable_service_mesh: bool = True,
        enable_api_gateway: bool = True,
        enable_event_bus: bool = True,
        enable_config_server: bool = True,
        enable_tracing: bool = True
    ):
        """
        Initialize Microservices API

        Args:
            enable_service_mesh: Enable service mesh
            enable_api_gateway: Enable API gateway
            enable_event_bus: Enable event-driven architecture
            enable_config_server: Enable configuration server
            enable_tracing: Enable distributed tracing
        """
        self.enable_service_mesh = enable_service_mesh
        self.enable_api_gateway = enable_api_gateway
        self.enable_event_bus = enable_event_bus
        self.enable_config_server = enable_config_server
        self.enable_tracing = enable_tracing

        # Initialize modules
        self._init_modules()

        # Statistics
        self.stats = {
            "services_registered": 0,
            "events_published": 0,
            "routes_configured": 0,
            "traces_created": 0
        }

        logger.info("Microservices API initialized")

    def _init_modules(self):
        """Initialize all microservices modules"""

        if not MODULES_AVAILABLE:
            logger.warning("Microservices modules not fully available")
            self.service_mesh = None
            self.api_gateway = None
            self.event_bus = None
            self.config_server = None
            self.tracer = None
            return

        try:
            # Service Mesh
            if self.enable_service_mesh:
                self.service_mesh = ServiceMesh()
            else:
                self.service_mesh = None

            # API Gateway
            if self.enable_api_gateway:
                self.api_gateway = APIGateway()
            else:
                self.api_gateway = None

            # Event Bus
            if self.enable_event_bus:
                self.event_bus = EventBus()
            else:
                self.event_bus = None

            # Config Server
            if self.enable_config_server:
                self.config_server = ConfigServer()
            else:
                self.config_server = None

            # Distributed Tracing
            if self.enable_tracing:
                self.tracer = Tracer(service_name="microservices-api")
            else:
                self.tracer = None

            logger.info("All microservices modules initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing microservices modules: {e}")
            raise

    # ============================================================
    # Service Registry Operations
    # ============================================================

    def register_service(
        self,
        service_id: str,
        host: str,
        port: int,
        **kwargs
    ) -> bool:
        """
        Register service

        Args:
            service_id: Service identifier
            host: Service host
            port: Service port
            **kwargs: Additional metadata

        Returns:
            Success status

        Example:
            >>> api.register_service("user-service", "localhost", 8080)
        """
        if not self.service_mesh:
            logger.warning("Service mesh not enabled")
            return False

        try:
            instance = ServiceInstance(
                service_id=service_id,
                host=host,
                port=port,
                metadata=kwargs
            )

            self.service_mesh.register(instance)
            self.stats["services_registered"] += 1

            logger.info(f"Registered service: {service_id} at {host}:{port}")
            return True

        except Exception as e:
            logger.error(f"Error registering service: {e}")
            return False

    def deregister_service(
        self,
        service_id: str,
        instance_id: Optional[str] = None
    ) -> bool:
        """Deregister service"""
        if not self.service_mesh:
            return False

        try:
            self.service_mesh.deregister(service_id, instance_id)
            logger.info(f"Deregistered service: {service_id}")
            return True

        except Exception as e:
            logger.error(f"Error deregistering service: {e}")
            return False

    def discover_services(
        self,
        service_id: str
    ) -> List[Dict[str, Any]]:
        """
        Discover service instances

        Args:
            service_id: Service to discover

        Returns:
            List of service instances

        Example:
            >>> services = api.discover_services("user-service")
        """
        if not self.service_mesh:
            return []

        try:
            instances = self.service_mesh.discover(service_id)

            return [
                {
                    "service_id": inst.service_id,
                    "host": inst.host,
                    "port": inst.port,
                    "status": inst.status,
                    "metadata": inst.metadata
                }
                for inst in instances
            ]

        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            return []

    def get_service_health(
        self,
        service_id: str
    ) -> Dict[str, Any]:
        """Get service health status"""
        if not self.service_mesh:
            return {"status": "unknown"}

        try:
            health = self.service_mesh.check_health(service_id)

            return {
                "service_id": service_id,
                "status": health.status,
                "healthy_instances": health.healthy_count,
                "total_instances": health.total_count,
                "last_check": health.last_check.isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # API Gateway Operations
    # ============================================================

    def add_route(
        self,
        path: str,
        service_id: str,
        method: str = "GET",
        **kwargs
    ) -> bool:
        """
        Add API route

        Args:
            path: Route path (e.g., "/users/:id")
            service_id: Target service
            method: HTTP method
            **kwargs: Additional route configuration

        Returns:
            Success status

        Example:
            >>> api.add_route("/users", "user-service", "GET")
        """
        if not self.api_gateway:
            logger.warning("API gateway not enabled")
            return False

        try:
            route = Route(
                path=path,
                service_id=service_id,
                method=HTTPMethod(method.upper()),
                **kwargs
            )

            self.api_gateway.add_route(route)
            self.stats["routes_configured"] += 1

            logger.info(f"Added route: {method} {path} -> {service_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding route: {e}")
            return False

    def remove_route(
        self,
        path: str,
        method: str = "GET"
    ) -> bool:
        """Remove API route"""
        if not self.api_gateway:
            return False

        try:
            self.api_gateway.remove_route(path, HTTPMethod(method.upper()))
            logger.info(f"Removed route: {method} {path}")
            return True

        except Exception as e:
            logger.error(f"Error removing route: {e}")
            return False

    def list_routes(self) -> List[Dict[str, Any]]:
        """List all API routes"""
        if not self.api_gateway:
            return []

        try:
            routes = self.api_gateway.list_routes()

            return [
                {
                    "path": route.path,
                    "method": route.method.value,
                    "service_id": route.service_id,
                    "rate_limit": route.rate_limit,
                    "auth_required": route.auth_required
                }
                for route in routes
            ]

        except Exception as e:
            logger.error(f"Error listing routes: {e}")
            return []

    # ============================================================
    # Event-Driven Architecture Operations
    # ============================================================

    def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: str = "normal"
    ) -> bool:
        """
        Publish event

        Args:
            event_type: Event type
            data: Event data
            priority: Event priority (low/normal/high)

        Returns:
            Success status

        Example:
            >>> api.publish_event("UserCreated", {"user_id": 123})
        """
        if not self.event_bus:
            logger.warning("Event bus not enabled")
            return False

        try:
            event = Event(
                event_type=event_type,
                data=data,
                priority=EventPriority(priority.upper())
            )

            self.event_bus.publish(event)
            self.stats["events_published"] += 1

            logger.info(f"Published event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    def subscribe_event(
        self,
        event_type: str,
        handler: Callable
    ) -> bool:
        """
        Subscribe to event

        Args:
            event_type: Event type to subscribe to
            handler: Event handler function

        Returns:
            Success status
        """
        if not self.event_bus:
            return False

        try:
            self.event_bus.subscribe(event_type, handler)
            logger.info(f"Subscribed to event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Error subscribing to event: {e}")
            return False

    def send_command(
        self,
        command_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send command (CQRS pattern)

        Args:
            command_type: Command type
            data: Command data

        Returns:
            Command execution result
        """
        if not self.event_bus:
            return {"status": "error", "message": "Event bus not enabled"}

        try:
            command = Command(
                command_type=command_type,
                data=data
            )

            result = self.event_bus.send_command(command)

            return {
                "status": "success",
                "result": result
            }

        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # Configuration Operations
    # ============================================================

    def get_config(
        self,
        key: str,
        environment: str = "production",
        default: Any = None
    ) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            environment: Environment (dev/staging/production)
            default: Default value if not found

        Returns:
            Configuration value

        Example:
            >>> db_url = api.get_config("database.url")
        """
        if not self.config_server:
            return default

        try:
            value = self.config_server.get_config(key, environment)
            return value if value is not None else default

        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return default

    def set_config(
        self,
        key: str,
        value: Any,
        environment: str = "production"
    ) -> bool:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
            environment: Environment

        Returns:
            Success status
        """
        if not self.config_server:
            return False

        try:
            self.config_server.set_config(key, value, environment)
            logger.info(f"Set config: {key} = {value}")
            return True

        except Exception as e:
            logger.error(f"Error setting config: {e}")
            return False

    def get_feature_flag(
        self,
        flag_name: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Check feature flag

        Args:
            flag_name: Feature flag name
            user_id: User ID for user-specific flags

        Returns:
            Flag status (enabled/disabled)

        Example:
            >>> enabled = api.get_feature_flag("new_ui")
        """
        if not self.config_server:
            return False

        try:
            return self.config_server.is_feature_enabled(flag_name, user_id)

        except Exception as e:
            logger.error(f"Error checking feature flag: {e}")
            return False

    def set_feature_flag(
        self,
        flag_name: str,
        enabled: bool,
        rollout_percentage: float = 100.0
    ) -> bool:
        """
        Set feature flag

        Args:
            flag_name: Feature flag name
            enabled: Enable/disable flag
            rollout_percentage: Percentage rollout (0-100)

        Returns:
            Success status
        """
        if not self.config_server:
            return False

        try:
            flag = FeatureFlag(
                name=flag_name,
                enabled=enabled,
                rollout_percentage=rollout_percentage
            )

            self.config_server.set_feature_flag(flag)
            logger.info(f"Set feature flag: {flag_name} = {enabled}")
            return True

        except Exception as e:
            logger.error(f"Error setting feature flag: {e}")
            return False

    # ============================================================
    # Distributed Tracing Operations
    # ============================================================

    def start_trace(
        self,
        operation_name: str,
        **kwargs
    ) -> Optional[Any]:
        """
        Start distributed trace

        Args:
            operation_name: Name of operation
            **kwargs: Additional span attributes

        Returns:
            Span object

        Example:
            >>> span = api.start_trace("process_order")
            >>> # ... do work ...
            >>> api.end_trace(span)
        """
        if not self.tracer:
            return None

        try:
            span = self.tracer.start_span(
                operation_name,
                kind=SpanKind.INTERNAL,
                **kwargs
            )

            self.stats["traces_created"] += 1
            return span

        except Exception as e:
            logger.error(f"Error starting trace: {e}")
            return None

    def end_trace(
        self,
        span: Any,
        status: str = "ok"
    ):
        """End distributed trace"""
        if not self.tracer or not span:
            return

        try:
            span.set_status(status)
            span.end()

        except Exception as e:
            logger.error(f"Error ending trace: {e}")

    # ============================================================
    # Circuit Breaker Operations
    # ============================================================

    def enable_circuit_breaker(
        self,
        service_id: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60
    ) -> bool:
        """
        Enable circuit breaker for service

        Args:
            service_id: Service to protect
            failure_threshold: Failures before opening circuit
            timeout_seconds: Timeout before attempting reset

        Returns:
            Success status
        """
        if not self.service_mesh:
            return False

        try:
            self.service_mesh.enable_circuit_breaker(
                service_id,
                failure_threshold,
                timeout_seconds
            )

            logger.info(f"Enabled circuit breaker for: {service_id}")
            return True

        except Exception as e:
            logger.error(f"Error enabling circuit breaker: {e}")
            return False

    def get_circuit_state(
        self,
        service_id: str
    ) -> Dict[str, Any]:
        """Get circuit breaker state"""
        if not self.service_mesh:
            return {"state": "unknown"}

        try:
            state = self.service_mesh.get_circuit_state(service_id)

            return {
                "service_id": service_id,
                "state": state.state.value,
                "failure_count": state.failure_count,
                "last_failure": state.last_failure.isoformat() if state.last_failure else None
            }

        except Exception as e:
            logger.error(f"Error getting circuit state: {e}")
            return {"state": "error"}

    # ============================================================
    # Statistics Operations
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        return {
            **self.stats,
            "service_mesh_enabled": self.enable_service_mesh,
            "api_gateway_enabled": self.enable_api_gateway,
            "event_bus_enabled": self.enable_event_bus,
            "config_server_enabled": self.enable_config_server,
            "tracing_enabled": self.enable_tracing
        }


# ============================================================
# Singleton Instance
# ============================================================

_api_instance: Optional[MicroservicesAPI] = None


def get_microservices_api(**kwargs) -> MicroservicesAPI:
    """
    Get singleton Microservices API instance

    Args:
        **kwargs: Configuration options

    Returns:
        MicroservicesAPI instance
    """
    global _api_instance

    if _api_instance is None:
        _api_instance = MicroservicesAPI(**kwargs)

    return _api_instance


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    # Create API instance
    api = MicroservicesAPI()

    print("🚀 Microservices API Example\n")

    # Register service
    print("1. Registering service...")
    api.register_service("user-service", "localhost", 8080)

    # Add API route
    print("2. Adding API route...")
    api.add_route("/users", "user-service", "GET")

    # Publish event
    print("3. Publishing event...")
    api.publish_event("UserCreated", {"user_id": 123, "email": "user@example.com"})

    # Get configuration
    print("4. Getting configuration...")
    db_url = api.get_config("database.url", default="postgresql://localhost/db")
    print(f"  Database URL: {db_url}")

    # Check feature flag
    print("5. Checking feature flag...")
    new_ui_enabled = api.get_feature_flag("new_ui")
    print(f"  New UI enabled: {new_ui_enabled}")

    # Get statistics
    print("\n6. API Statistics:")
    stats = api.get_stats()
    print(f"  Services registered: {stats['services_registered']}")
    print(f"  Events published: {stats['events_published']}")
    print(f"  Routes configured: {stats['routes_configured']}")

    print("\n✅ Microservices API demo complete!")
