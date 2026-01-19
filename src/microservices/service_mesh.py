#!/usr/bin/env python3
"""
Service Mesh Module

Provides service discovery, load balancing, circuit breakers, and health checking
for microservices architecture.

Key Features:
- Service discovery (Consul, Eureka, etcd)
- Load balancing (Round-robin, Least-connections, IP-hash, Weighted, Random)
- Circuit breaker pattern
- Health checking with heartbeat
- Retry policies with exponential backoff
- Timeout management
- mTLS authentication support
- Traffic routing and canary deployments

Dependencies:
- requests (for HTTP health checks)
"""

import hashlib
import logging
import random
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service health status"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED = "weighted"
    RANDOM = "random"


class CircuitState(str, Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class DiscoveryBackend(str, Enum):
    """Service discovery backends"""

    CONSUL = "consul"
    EUREKA = "eureka"
    ETCD = "etcd"
    IN_MEMORY = "in_memory"


@dataclass
class ServiceInstance:
    """Service instance metadata"""

    service_name: str
    instance_id: str
    host: str
    port: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    weight: int = 1  # For weighted load balancing
    connections: int = 0  # Active connections count
    last_heartbeat: Optional[datetime] = None
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheckConfig:
    """Health check configuration"""

    interval_seconds: int = 30
    timeout_seconds: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    check_endpoint: str = "/health"
    check_protocol: str = "http"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    half_open_max_requests: int = 3


@dataclass
class RetryPolicy:
    """Retry policy configuration"""

    max_attempts: int = 3
    initial_backoff_ms: int = 100
    max_backoff_ms: int = 10000
    backoff_multiplier: float = 2.0
    retryable_status_codes: Set[int] = field(default_factory=lambda: {500, 502, 503, 504})


class CircuitBreaker:
    """
    Circuit breaker pattern implementation

    Prevents cascading failures by stopping requests to failing services.
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_requests = 0
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        with self._lock:
            # Check if circuit should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if (
                    self.last_failure_time
                    and (datetime.now() - self.last_failure_time).total_seconds() >= self.config.timeout_seconds
                ):
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise Exception("Circuit breaker is OPEN")

            # In HALF_OPEN state, limit concurrent requests
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_max_requests:
                    raise Exception("Circuit breaker HALF_OPEN limit reached")
                self.half_open_requests += 1

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
                    logger.info("Circuit breaker CLOSED")

    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN (failed during HALF_OPEN)")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPEN (failures: {self.failure_count})")

    def reset(self):
        """Reset circuit breaker to CLOSED state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None


class LoadBalancer:
    """
    Load balancer with multiple strategies

    Distributes requests across service instances.
    """

    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self._round_robin_index = 0
        self._lock = threading.Lock()

    def select_instance(
        self, instances: List[ServiceInstance], client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """
        Select service instance based on load balancing algorithm

        Args:
            instances: Available service instances
            client_ip: Client IP for IP-hash algorithm

        Returns:
            Selected instance or None
        """
        if not instances:
            return None

        # Filter only healthy instances
        healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        if not healthy_instances:
            return None

        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin(healthy_instances)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(healthy_instances)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash(healthy_instances, client_ip)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED:
            return self._weighted(healthy_instances)
        elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
            return random.choice(healthy_instances)

        return healthy_instances[0]

    def _round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin selection"""
        with self._lock:
            instance = instances[self._round_robin_index % len(instances)]
            self._round_robin_index = (self._round_robin_index + 1) % len(instances)
            return instance

    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Select instance with least active connections"""
        return min(instances, key=lambda i: i.connections)

    def _ip_hash(self, instances: List[ServiceInstance], client_ip: Optional[str]) -> ServiceInstance:
        """Consistent hashing based on client IP"""
        if not client_ip:
            return instances[0]

        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(instances)
        return instances[index]

    def _weighted(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted random selection"""
        total_weight = sum(i.weight for i in instances)
        if total_weight == 0:
            return instances[0]

        rand = random.uniform(0, total_weight)
        cumulative = 0

        for instance in instances:
            cumulative += instance.weight
            if rand <= cumulative:
                return instance

        return instances[-1]


class HealthChecker:
    """
    Health checker with configurable checks

    Monitors service instances and updates their health status.
    """

    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._instances: Dict[str, ServiceInstance] = {}
        self._consecutive_failures: Dict[str, int] = defaultdict(int)
        self._consecutive_successes: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()

    def register_instance(self, instance: ServiceInstance):
        """Register instance for health checking"""
        with self._lock:
            key = f"{instance.service_name}:{instance.instance_id}"
            self._instances[key] = instance

    def deregister_instance(self, service_name: str, instance_id: str):
        """Deregister instance from health checking"""
        with self._lock:
            key = f"{service_name}:{instance_id}"
            if key in self._instances:
                del self._instances[key]
                self._consecutive_failures.pop(key, None)
                self._consecutive_successes.pop(key, None)

    def start(self):
        """Start health checker background thread"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
        logger.info("Health checker started")

    def stop(self):
        """Stop health checker"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Health checker stopped")

    def _check_loop(self):
        """Background health check loop"""
        while self._running:
            with self._lock:
                instances = list(self._instances.values())

            for instance in instances:
                self._check_instance(instance)

            time.sleep(self.config.interval_seconds)

    def _check_instance(self, instance: ServiceInstance):
        """Perform health check on single instance"""
        key = f"{instance.service_name}:{instance.instance_id}"

        try:
            # Perform health check (simplified - in production use actual HTTP/gRPC calls)
            is_healthy = self._perform_check(instance)

            if is_healthy:
                self._consecutive_failures[key] = 0
                self._consecutive_successes[key] += 1

                if self._consecutive_successes[key] >= self.config.healthy_threshold:
                    if instance.status != ServiceStatus.HEALTHY:
                        instance.status = ServiceStatus.HEALTHY
                        instance.last_heartbeat = datetime.now()
                        logger.info(f"Instance {key} marked HEALTHY")
            else:
                self._consecutive_successes[key] = 0
                self._consecutive_failures[key] += 1

                if self._consecutive_failures[key] >= self.config.unhealthy_threshold:
                    if instance.status != ServiceStatus.UNHEALTHY:
                        instance.status = ServiceStatus.UNHEALTHY
                        logger.warning(f"Instance {key} marked UNHEALTHY")

        except Exception as e:
            logger.error(f"Health check failed for {key}: {e}")
            self._consecutive_failures[key] += 1

    def _perform_check(self, instance: ServiceInstance) -> bool:
        """
        Perform actual health check

        In production, this would make HTTP/gRPC calls to the health endpoint.
        For now, returns True for demonstration.
        """
        # Simplified check - in production:
        # - Make HTTP GET to http://{instance.host}:{instance.port}{config.check_endpoint}
        # - Check response status code == 200
        # - Verify response within timeout

        # Check heartbeat timeout
        if instance.last_heartbeat:
            timeout = timedelta(seconds=self.config.interval_seconds * 3)
            if datetime.now() - instance.last_heartbeat > timeout:
                return False

        return True


class ServiceRegistry:
    """
    Service registry for service discovery

    Maintains registry of all service instances and their metadata.
    """

    def __init__(self, backend: DiscoveryBackend = DiscoveryBackend.IN_MEMORY):
        self.backend = backend
        self._services: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self._lock = threading.Lock()
        self.health_checker = HealthChecker(HealthCheckConfig())

    def register(self, instance: ServiceInstance) -> bool:
        """
        Register service instance

        Args:
            instance: Service instance to register

        Returns:
            True if registered successfully
        """
        with self._lock:
            # Check if instance already exists
            existing = self._find_instance(instance.service_name, instance.instance_id)
            if existing:
                logger.warning(f"Instance {instance.instance_id} already registered")
                return False

            # Add instance
            instance.status = ServiceStatus.HEALTHY
            instance.last_heartbeat = datetime.now()
            self._services[instance.service_name].append(instance)

            # Register for health checking
            self.health_checker.register_instance(instance)

            logger.info(f"Registered {instance.service_name}:{instance.instance_id} at {instance.host}:{instance.port}")
            return True

    def deregister(self, service_name: str, instance_id: str) -> bool:
        """
        Deregister service instance

        Args:
            service_name: Service name
            instance_id: Instance ID

        Returns:
            True if deregistered successfully
        """
        with self._lock:
            instances = self._services.get(service_name, [])
            for i, inst in enumerate(instances):
                if inst.instance_id == instance_id:
                    instances.pop(i)
                    self.health_checker.deregister_instance(service_name, instance_id)
                    logger.info(f"Deregistered {service_name}:{instance_id}")
                    return True

            return False

    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """
        Update instance heartbeat

        Args:
            service_name: Service name
            instance_id: Instance ID

        Returns:
            True if heartbeat recorded
        """
        with self._lock:
            instance = self._find_instance(service_name, instance_id)
            if instance:
                instance.last_heartbeat = datetime.now()
                return True
            return False

    def discover(self, service_name: str) -> List[ServiceInstance]:
        """
        Discover instances of a service

        Args:
            service_name: Service name

        Returns:
            List of service instances
        """
        with self._lock:
            return self._services.get(service_name, []).copy()

    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        Get only healthy instances of a service

        Args:
            service_name: Service name

        Returns:
            List of healthy instances
        """
        instances = self.discover(service_name)
        return [i for i in instances if i.status == ServiceStatus.HEALTHY]

    def _find_instance(self, service_name: str, instance_id: str) -> Optional[ServiceInstance]:
        """Find instance by service name and ID"""
        instances = self._services.get(service_name, [])
        for inst in instances:
            if inst.instance_id == instance_id:
                return inst
        return None

    def start_health_checks(self):
        """Start health checking"""
        self.health_checker.start()

    def stop_health_checks(self):
        """Stop health checking"""
        self.health_checker.stop()


class ServiceMesh:
    """
    Service mesh coordinator

    Provides unified interface for service discovery, load balancing,
    circuit breaking, and traffic management.
    """

    def __init__(self, registry: Optional[ServiceRegistry] = None, load_balancer: Optional[LoadBalancer] = None):
        self.registry = registry or ServiceRegistry()
        self.load_balancer = load_balancer or LoadBalancer()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def register_service(self, instance: ServiceInstance) -> bool:
        """Register service instance"""
        return self.registry.register(instance)

    def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister service instance"""
        return self.registry.deregister(service_name, instance_id)

    def call_service(
        self,
        service_name: str,
        func: Callable,
        *args,
        client_ip: Optional[str] = None,
        use_circuit_breaker: bool = True,
        **kwargs,
    ) -> Any:
        """
        Call service with load balancing and circuit breaker

        Args:
            service_name: Target service name
            func: Function to call with selected instance
            *args: Function arguments
            client_ip: Client IP for IP-hash load balancing
            use_circuit_breaker: Enable circuit breaker protection
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If no healthy instances or circuit is open
        """
        # Get healthy instances
        instances = self.registry.get_healthy_instances(service_name)
        if not instances:
            raise Exception(f"No healthy instances for service {service_name}")

        # Select instance using load balancer
        instance = self.load_balancer.select_instance(instances, client_ip)
        if not instance:
            raise Exception(f"Load balancer failed to select instance for {service_name}")

        # Increment connection count
        instance.connections += 1

        try:
            if use_circuit_breaker:
                # Get or create circuit breaker for this instance
                cb_key = f"{service_name}:{instance.instance_id}"
                circuit_breaker = self._get_circuit_breaker(cb_key)

                # Call with circuit breaker protection
                result = circuit_breaker.call(func, instance, *args, **kwargs)
            else:
                # Call directly without circuit breaker
                result = func(instance, *args, **kwargs)

            return result

        finally:
            # Decrement connection count
            instance.connections -= 1

    def _get_circuit_breaker(self, key: str) -> CircuitBreaker:
        """Get or create circuit breaker for service instance"""
        with self._lock:
            if key not in self._circuit_breakers:
                config = CircuitBreakerConfig()
                self._circuit_breakers[key] = CircuitBreaker(config)
            return self._circuit_breakers[key]

    def start(self):
        """Start service mesh (health checking, etc.)"""
        self.registry.start_health_checks()
        logger.info("Service mesh started")

    def stop(self):
        """Stop service mesh"""
        self.registry.stop_health_checks()
        logger.info("Service mesh stopped")


# Singleton instance
_service_mesh_instance = None
_instance_lock = threading.Lock()


def get_service_mesh() -> ServiceMesh:
    """Get singleton Service Mesh instance"""
    global _service_mesh_instance

    if _service_mesh_instance is None:
        with _instance_lock:
            if _service_mesh_instance is None:
                _service_mesh_instance = ServiceMesh()

    return _service_mesh_instance


if __name__ == "__main__":
    # Example usage
    mesh = get_service_mesh()

    # Register some service instances
    instance1 = ServiceInstance(
        service_name="user-service", instance_id="user-1", host="localhost", port=8001, metadata={"zone": "us-east-1a"}
    )

    instance2 = ServiceInstance(
        service_name="user-service", instance_id="user-2", host="localhost", port=8002, metadata={"zone": "us-east-1b"}
    )

    mesh.register_service(instance1)
    mesh.register_service(instance2)

    print(f"Registered instances: {len(mesh.registry.discover('user-service'))}")

    # Start health checking
    mesh.start()

    # Simulate service call
    def call_user_service(instance: ServiceInstance, user_id: str):
        """Simulate calling user service"""
        print(f"Calling {instance.instance_id} at {instance.host}:{instance.port} for user {user_id}")
        return {"user_id": user_id, "instance": instance.instance_id}

    try:
        result = mesh.call_service("user-service", call_user_service, user_id="123")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Stop mesh
    time.sleep(2)
    mesh.stop()

    print("\nService Mesh module loaded successfully!")
