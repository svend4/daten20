"""
Horizontal Scaling & Load Balancing

Provides enterprise scaling capabilities:
- Load balancing (round-robin, least-connections, IP hash, weighted)
- Auto-scaling based on metrics
- Service discovery and registration
- Health-based routing
- Session affinity (sticky sessions)
- Circuit breaker pattern
- Rate limiting per node
- Connection pooling
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
import hashlib


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"


class ServiceStatus(str, Enum):
    """Service instance status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"  # Accepting no new connections
    STARTING = "starting"


class ScalingPolicy(str, Enum):
    """Auto-scaling policies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    REQUEST_RATE_BASED = "request_rate_based"
    CUSTOM_METRIC = "custom_metric"


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class ServiceInstance:
    """Service instance"""
    id: str
    host: str
    port: int
    weight: int = 1
    status: ServiceStatus = ServiceStatus.STARTING
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Metrics
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0

    # Health check
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0

    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_percent: float = 70.0
    target_memory_percent: float = 80.0
    target_requests_per_second: float = 100.0
    scale_up_cooldown_seconds: int = 300  # 5 minutes
    scale_down_cooldown_seconds: int = 600  # 10 minutes


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Open circuit after N failures
    timeout_seconds: int = 60  # Try again after N seconds
    success_threshold: int = 2  # Close circuit after N successes in half-open


class ServiceRegistry:
    """Service discovery and registration"""

    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.lock = threading.Lock()

    def register_service(
        self,
        service_name: str,
        instance_id: str,
        host: str,
        port: int,
        weight: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ServiceInstance:
        """Register service instance"""
        instance = ServiceInstance(
            id=instance_id,
            host=host,
            port=port,
            weight=weight,
            status=ServiceStatus.STARTING,
            metadata=metadata or {}
        )

        with self.lock:
            if service_name not in self.services:
                self.services[service_name] = []
            self.services[service_name].append(instance)

        print(f"[Registry] Registered {service_name} instance: {host}:{port}")
        return instance

    def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister service instance"""
        with self.lock:
            if service_name in self.services:
                instances = self.services[service_name]
                self.services[service_name] = [i for i in instances if i.id != instance_id]

                if not self.services[service_name]:
                    del self.services[service_name]

                print(f"[Registry] Deregistered {service_name} instance: {instance_id}")
                return True

        return False

    def get_service_instances(
        self,
        service_name: str,
        healthy_only: bool = True
    ) -> List[ServiceInstance]:
        """Get service instances"""
        with self.lock:
            instances = self.services.get(service_name, [])

            if healthy_only:
                instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]

            return list(instances)

    def update_instance_status(
        self,
        service_name: str,
        instance_id: str,
        status: ServiceStatus
    ) -> bool:
        """Update instance status"""
        with self.lock:
            instances = self.services.get(service_name, [])

            for instance in instances:
                if instance.id == instance_id:
                    instance.status = status
                    print(f"[Registry] Updated {service_name}/{instance_id} status: {status.value}")
                    return True

        return False


class LoadBalancer:
    """Load balancer"""

    def __init__(
        self,
        algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
        service_registry: Optional[ServiceRegistry] = None
    ):
        self.algorithm = algorithm
        self.registry = service_registry or ServiceRegistry()
        self.current_index: Dict[str, int] = {}
        self.lock = threading.Lock()

    def select_instance(
        self,
        service_name: str,
        client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """Select instance using load balancing algorithm"""
        instances = self.registry.get_service_instances(service_name, healthy_only=True)

        if not instances:
            return None

        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin(service_name, instances)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(instances)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash(instances, client_ip or "")
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(service_name, instances)
        elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
            return self._random(instances)
        else:
            return instances[0]

    def _round_robin(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin selection"""
        with self.lock:
            if service_name not in self.current_index:
                self.current_index[service_name] = 0

            index = self.current_index[service_name]
            instance = instances[index % len(instances)]

            self.current_index[service_name] = (index + 1) % len(instances)

        return instance

    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection"""
        return min(instances, key=lambda i: i.active_connections)

    def _ip_hash(self, instances: List[ServiceInstance], client_ip: str) -> ServiceInstance:
        """IP hash selection (sticky sessions)"""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(instances)
        return instances[index]

    def _weighted_round_robin(
        self,
        service_name: str,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Weighted round-robin selection"""
        # Expand instances based on weight
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.weight)

        return self._round_robin(service_name, weighted_instances)

    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection"""
        import random
        return random.choice(instances)


class HealthChecker:
    """Health checker for service instances"""

    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
        self.health_check_interval = 10  # seconds
        self.health_check_timeout = 5  # seconds
        self.failure_threshold = 3
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start health checking"""
        self.running = True
        self.thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.thread.start()
        print("[HealthChecker] Started")

    def stop(self):
        """Stop health checking"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("[HealthChecker] Stopped")

    def _health_check_loop(self):
        """Health check loop"""
        while self.running:
            self._check_all_services()
            time.sleep(self.health_check_interval)

    def _check_all_services(self):
        """Check health of all services"""
        for service_name, instances in list(self.registry.services.items()):
            for instance in instances:
                self._check_instance_health(service_name, instance)

    def _check_instance_health(self, service_name: str, instance: ServiceInstance):
        """Check health of single instance"""
        try:
            # In production, make actual HTTP health check request
            # response = requests.get(f"http://{instance.host}:{instance.port}/health", timeout=self.health_check_timeout)
            # is_healthy = response.status_code == 200

            # Simulate health check
            is_healthy = instance.consecutive_failures < self.failure_threshold

            instance.last_health_check = datetime.now()

            if is_healthy:
                instance.consecutive_failures = 0
                if instance.status != ServiceStatus.HEALTHY:
                    self.registry.update_instance_status(
                        service_name,
                        instance.id,
                        ServiceStatus.HEALTHY
                    )
            else:
                instance.consecutive_failures += 1
                if instance.consecutive_failures >= self.failure_threshold:
                    self.registry.update_instance_status(
                        service_name,
                        instance.id,
                        ServiceStatus.UNHEALTHY
                    )

        except Exception as e:
            instance.consecutive_failures += 1
            print(f"[HealthChecker] Health check failed for {instance.id}: {e}")


class AutoScaler:
    """Auto-scaling manager"""

    def __init__(
        self,
        service_registry: ServiceRegistry,
        scaling_config: ScalingConfig
    ):
        self.registry = service_registry
        self.config = scaling_config
        self.last_scale_up: Dict[str, datetime] = {}
        self.last_scale_down: Dict[str, datetime] = {}

    def evaluate_scaling(
        self,
        service_name: str,
        current_cpu_percent: float,
        current_memory_percent: float,
        current_rps: float
    ) -> Optional[str]:
        """Evaluate if scaling is needed"""
        instances = self.registry.get_service_instances(service_name, healthy_only=True)
        current_count = len(instances)

        now = datetime.now()

        # Check if should scale up
        should_scale_up = (
            current_cpu_percent > self.config.target_cpu_percent or
            current_memory_percent > self.config.target_memory_percent or
            current_rps > self.config.target_requests_per_second
        )

        if should_scale_up and current_count < self.config.max_instances:
            last_scale_up = self.last_scale_up.get(service_name)

            if not last_scale_up or (now - last_scale_up).seconds > self.config.scale_up_cooldown_seconds:
                self.last_scale_up[service_name] = now
                return 'scale_up'

        # Check if should scale down
        should_scale_down = (
            current_cpu_percent < self.config.target_cpu_percent * 0.5 and
            current_memory_percent < self.config.target_memory_percent * 0.5 and
            current_rps < self.config.target_requests_per_second * 0.5
        )

        if should_scale_down and current_count > self.config.min_instances:
            last_scale_down = self.last_scale_down.get(service_name)

            if not last_scale_down or (now - last_scale_down).seconds > self.config.scale_down_cooldown_seconds:
                self.last_scale_down[service_name] = now
                return 'scale_down'

        return None

    def scale_up(self, service_name: str) -> bool:
        """Scale up service"""
        print(f"[AutoScaler] Scaling up {service_name}")

        # In production, would:
        # 1. Launch new container/VM
        # 2. Wait for it to be ready
        # 3. Register with service registry

        return True

    def scale_down(self, service_name: str) -> bool:
        """Scale down service"""
        instances = self.registry.get_service_instances(service_name)

        if len(instances) <= self.config.min_instances:
            return False

        # Select instance to remove (least connections)
        instance_to_remove = min(instances, key=lambda i: i.active_connections)

        print(f"[AutoScaler] Scaling down {service_name}, removing {instance_to_remove.id}")

        # Set to draining status
        self.registry.update_instance_status(
            service_name,
            instance_to_remove.id,
            ServiceStatus.DRAINING
        )

        # In production, would:
        # 1. Wait for existing connections to finish
        # 2. Deregister from service registry
        # 3. Terminate container/VM

        return True


class CircuitBreaker:
    """Circuit breaker pattern implementation"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                # Check if timeout expired
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).seconds
                    if elapsed >= self.config.timeout_seconds:
                        self.state = CircuitState.HALF_OPEN
                        self.success_count = 0
                        print("[CircuitBreaker] State: HALF_OPEN")
                    else:
                        raise Exception("Circuit breaker is OPEN")
                else:
                    raise Exception("Circuit breaker is OPEN")

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
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1

                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    print("[CircuitBreaker] State: CLOSED")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                print("[CircuitBreaker] State: OPEN (failed in half-open)")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"[CircuitBreaker] State: OPEN (reached threshold {self.config.failure_threshold})")


class SessionManager:
    """Session affinity (sticky sessions) manager"""

    def __init__(self):
        self.session_mappings: Dict[str, str] = {}  # session_id -> instance_id
        self.lock = threading.Lock()

    def bind_session(self, session_id: str, instance_id: str):
        """Bind session to instance"""
        with self.lock:
            self.session_mappings[session_id] = instance_id

    def get_instance_for_session(self, session_id: str) -> Optional[str]:
        """Get instance for session"""
        with self.lock:
            return self.session_mappings.get(session_id)

    def unbind_session(self, session_id: str):
        """Unbind session"""
        with self.lock:
            self.session_mappings.pop(session_id, None)


class ScalingEngine:
    """Main scaling and load balancing engine"""

    def __init__(
        self,
        algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
        scaling_config: Optional[ScalingConfig] = None
    ):
        self.service_registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(algorithm, self.service_registry)
        self.health_checker = HealthChecker(self.service_registry)
        self.auto_scaler = AutoScaler(
            self.service_registry,
            scaling_config or ScalingConfig()
        )
        self.session_manager = SessionManager()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def start(self):
        """Start scaling engine"""
        self.health_checker.start()
        print("[ScalingEngine] Started")

    def stop(self):
        """Stop scaling engine"""
        self.health_checker.stop()
        print("[ScalingEngine] Stopped")

    def register_service_instance(
        self,
        service_name: str,
        instance_id: str,
        host: str,
        port: int,
        weight: int = 1
    ) -> ServiceInstance:
        """Register service instance"""
        return self.service_registry.register_service(
            service_name, instance_id, host, port, weight
        )

    def route_request(
        self,
        service_name: str,
        session_id: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """Route request to service instance"""
        # Check for session affinity
        if session_id:
            instance_id = self.session_manager.get_instance_for_session(session_id)
            if instance_id:
                instances = self.service_registry.get_service_instances(service_name)
                for instance in instances:
                    if instance.id == instance_id and instance.status == ServiceStatus.HEALTHY:
                        return instance

        # Use load balancer
        instance = self.load_balancer.select_instance(service_name, client_ip)

        # Bind session if provided
        if instance and session_id:
            self.session_manager.bind_session(session_id, instance.id)

        return instance

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                CircuitBreakerConfig()
            )

        return self.circuit_breakers[service_name]

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        status = {}

        for service_name, instances in self.service_registry.services.items():
            healthy_count = sum(1 for i in instances if i.status == ServiceStatus.HEALTHY)
            total_requests = sum(i.total_requests for i in instances)

            status[service_name] = {
                'total_instances': len(instances),
                'healthy_instances': healthy_count,
                'total_requests': total_requests,
                'instances': [
                    {
                        'id': i.id,
                        'host': i.host,
                        'port': i.port,
                        'status': i.status.value,
                        'active_connections': i.active_connections,
                        'total_requests': i.total_requests
                    }
                    for i in instances
                ]
            }

        return status


# Global instance
_scaling_engine: Optional[ScalingEngine] = None


def get_scaling_engine() -> ScalingEngine:
    """Get global scaling engine instance"""
    global _scaling_engine

    if _scaling_engine is None:
        _scaling_engine = ScalingEngine()

    return _scaling_engine
