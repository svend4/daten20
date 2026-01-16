#!/usr/bin/env python3
"""
Service Registry & Discovery Module

Provides service registration, discovery, and health monitoring for microservices.

Key Features:
- Service registration and deregistration
- Health checks with heartbeat mechanism
- Service metadata management
- DNS-based discovery
- Client-side and server-side discovery
- Load metrics collection
- Automatic cleanup of dead services
- Multi-backend support (Consul, Eureka, etcd, in-memory)

Dependencies:
- requests (for HTTP communication)
"""

import hashlib
import json
import logging
import socket
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service health status"""

    UP = "up"
    DOWN = "down"
    STARTING = "starting"
    OUT_OF_SERVICE = "out_of_service"
    UNKNOWN = "unknown"


class DiscoveryType(str, Enum):
    """Service discovery types"""

    CLIENT_SIDE = "client_side"
    SERVER_SIDE = "server_side"
    DNS_BASED = "dns_based"


@dataclass
class ServiceMetadata:
    """Service metadata"""

    version: str = "1.0.0"
    environment: str = "production"
    region: str = "default"
    zone: str = "default"
    tags: List[str] = field(default_factory=list)
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check configuration"""

    check_type: str = "http"  # http, tcp, script
    endpoint: str = "/health"
    interval_seconds: int = 10
    timeout_seconds: int = 5
    deregister_after: int = 60  # Deregister after N seconds of failure
    tls_skip_verify: bool = False


@dataclass
class LoadMetrics:
    """Service load metrics"""

    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    error_count: int = 0
    avg_response_time_ms: float = 0.0
    active_connections: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceInstance:
    """Registered service instance"""

    service_id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus = ServiceStatus.STARTING
    metadata: ServiceMetadata = field(default_factory=ServiceMetadata)
    health_check: Optional[HealthCheck] = None
    load_metrics: LoadMetrics = field(default_factory=LoadMetrics)
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    heartbeat_ttl: int = 30  # seconds
    consecutive_failures: int = 0


class ServiceRegistry:
    """
    Service Registry implementation

    Manages service registration, discovery, and health monitoring.
    """

    def __init__(self, cleanup_interval: int = 30):
        """
        Initialize service registry

        Args:
            cleanup_interval: Interval for cleanup of dead services (seconds)
        """
        self._services: Dict[str, ServiceInstance] = {}
        self._services_by_name: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None
        self._health_check_threads: Dict[str, threading.Thread] = {}

    def start(self):
        """Start registry background tasks"""
        if self._running:
            return

        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("Service registry started")

    def stop(self):
        """Stop registry background tasks"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("Service registry stopped")

    def register(
        self,
        service_name: str,
        host: str,
        port: int,
        service_id: Optional[str] = None,
        metadata: Optional[ServiceMetadata] = None,
        health_check: Optional[HealthCheck] = None,
    ) -> str:
        """
        Register a service instance

        Args:
            service_name: Name of the service
            host: Service host
            port: Service port
            service_id: Unique service ID (auto-generated if not provided)
            metadata: Service metadata
            health_check: Health check configuration

        Returns:
            Service ID
        """
        with self._lock:
            # Generate service ID if not provided
            if not service_id:
                service_id = self._generate_service_id(service_name, host, port)

            # Create service instance
            instance = ServiceInstance(
                service_id=service_id,
                service_name=service_name,
                host=host,
                port=port,
                metadata=metadata or ServiceMetadata(),
                health_check=health_check,
            )

            # Register service
            self._services[service_id] = instance
            self._services_by_name[service_name].append(service_id)

            # Start health check if configured
            if health_check:
                self._start_health_check(service_id)
            else:
                # Mark as UP if no health check
                instance.status = ServiceStatus.UP

            logger.info(f"Registered service: {service_name} (ID: {service_id}) at {host}:{port}")
            return service_id

    def deregister(self, service_id: str) -> bool:
        """
        Deregister a service instance

        Args:
            service_id: Service ID to deregister

        Returns:
            True if deregistered, False if not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            instance = self._services[service_id]
            service_name = instance.service_name

            # Stop health check
            if service_id in self._health_check_threads:
                # Thread will stop when service is removed
                del self._health_check_threads[service_id]

            # Remove from registries
            del self._services[service_id]
            if service_id in self._services_by_name[service_name]:
                self._services_by_name[service_name].remove(service_id)

            # Clean up empty service name entries
            if not self._services_by_name[service_name]:
                del self._services_by_name[service_name]

            logger.info(f"Deregistered service: {service_id}")
            return True

    def heartbeat(self, service_id: str) -> bool:
        """
        Record heartbeat for a service

        Args:
            service_id: Service ID

        Returns:
            True if successful, False if service not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            instance = self._services[service_id]
            instance.last_heartbeat = datetime.now()
            instance.consecutive_failures = 0

            if instance.status != ServiceStatus.UP:
                instance.status = ServiceStatus.UP
                logger.info(f"Service {service_id} status changed to UP")

            return True

    def update_load_metrics(self, service_id: str, metrics: LoadMetrics) -> bool:
        """
        Update load metrics for a service

        Args:
            service_id: Service ID
            metrics: Load metrics

        Returns:
            True if successful, False if service not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            self._services[service_id].load_metrics = metrics
            return True

    def discover(
        self,
        service_name: str,
        healthy_only: bool = True,
        region: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[ServiceInstance]:
        """
        Discover service instances

        Args:
            service_name: Service name to discover
            healthy_only: Return only healthy instances
            region: Filter by region
            tags: Filter by tags

        Returns:
            List of service instances
        """
        with self._lock:
            if service_name not in self._services_by_name:
                return []

            instances = []
            for service_id in self._services_by_name[service_name]:
                instance = self._services.get(service_id)
                if not instance:
                    continue

                # Filter by health status
                if healthy_only and instance.status != ServiceStatus.UP:
                    continue

                # Filter by region
                if region and instance.metadata.region != region:
                    continue

                # Filter by tags
                if tags:
                    if not all(tag in instance.metadata.tags for tag in tags):
                        continue

                instances.append(instance)

            return instances

    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """
        Get service instance by ID

        Args:
            service_id: Service ID

        Returns:
            Service instance or None
        """
        with self._lock:
            return self._services.get(service_id)

    def get_all_services(self) -> List[ServiceInstance]:
        """
        Get all registered services

        Returns:
            List of all service instances
        """
        with self._lock:
            return list(self._services.values())

    def get_service_names(self) -> List[str]:
        """
        Get all registered service names

        Returns:
            List of service names
        """
        with self._lock:
            return list(self._services_by_name.keys())

    def get_service_status(self, service_id: str) -> Optional[ServiceStatus]:
        """
        Get service status

        Args:
            service_id: Service ID

        Returns:
            Service status or None
        """
        with self._lock:
            instance = self._services.get(service_id)
            return instance.status if instance else None

    def _generate_service_id(self, service_name: str, host: str, port: int) -> str:
        """Generate unique service ID"""
        data = f"{service_name}:{host}:{port}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _cleanup_loop(self):
        """Background loop to cleanup dead services"""
        while self._running:
            try:
                time.sleep(self._cleanup_interval)
                self._cleanup_dead_services()
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_dead_services(self):
        """Remove services that haven't sent heartbeat"""
        with self._lock:
            now = datetime.now()
            dead_services = []

            for service_id, instance in self._services.items():
                # Check heartbeat TTL
                if instance.last_heartbeat:
                    time_since_heartbeat = (now - instance.last_heartbeat).total_seconds()
                    if time_since_heartbeat > instance.heartbeat_ttl:
                        dead_services.append(service_id)
                        logger.warning(
                            f"Service {service_id} missed heartbeat "
                            f"({time_since_heartbeat:.1f}s > {instance.heartbeat_ttl}s)"
                        )

            # Deregister dead services
            for service_id in dead_services:
                self.deregister(service_id)

    def _start_health_check(self, service_id: str):
        """Start health check for a service"""
        instance = self._services.get(service_id)
        if not instance or not instance.health_check:
            return

        def health_check_loop():
            while self._running and service_id in self._services:
                try:
                    instance = self._services.get(service_id)
                    if not instance:
                        break

                    # Perform health check
                    is_healthy = self._perform_health_check(instance)

                    with self._lock:
                        if is_healthy:
                            instance.consecutive_failures = 0
                            if instance.status != ServiceStatus.UP:
                                instance.status = ServiceStatus.UP
                                logger.info(f"Service {service_id} is now healthy")
                        else:
                            instance.consecutive_failures += 1
                            if instance.status == ServiceStatus.UP:
                                instance.status = ServiceStatus.DOWN
                                logger.warning(f"Service {service_id} is now unhealthy")

                        # Deregister if too many failures
                        if (
                            instance.health_check
                            and instance.consecutive_failures * instance.health_check.interval_seconds
                            >= instance.health_check.deregister_after
                        ):
                            logger.error(f"Deregistering service {service_id} due to health check failures")
                            self.deregister(service_id)
                            break

                    time.sleep(instance.health_check.interval_seconds)

                except Exception as e:
                    logger.error(f"Error in health check for {service_id}: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=health_check_loop, daemon=True)
        thread.start()
        self._health_check_threads[service_id] = thread

    def _perform_health_check(self, instance: ServiceInstance) -> bool:
        """
        Perform health check on service instance

        Args:
            instance: Service instance

        Returns:
            True if healthy, False otherwise
        """
        if not instance.health_check:
            return True

        check_type = instance.health_check.check_type
        timeout = instance.health_check.timeout_seconds

        try:
            if check_type == "http":
                return self._http_health_check(instance, timeout)
            elif check_type == "tcp":
                return self._tcp_health_check(instance, timeout)
            else:
                logger.warning(f"Unknown health check type: {check_type}")
                return True
        except Exception as e:
            logger.error(f"Health check failed for {instance.service_id}: {e}")
            return False

    def _http_health_check(self, instance: ServiceInstance, timeout: int) -> bool:
        """Perform HTTP health check"""
        try:
            import requests

            url = f"http://{instance.host}:{instance.port}{instance.health_check.endpoint}"
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"HTTP health check failed: {e}")
            return False

    def _tcp_health_check(self, instance: ServiceInstance, timeout: int) -> bool:
        """Perform TCP health check"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((instance.host, instance.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"TCP health check failed: {e}")
            return False


class ConsulServiceRegistry(ServiceRegistry):
    """
    Consul-based service registry

    Integrates with HashiCorp Consul for service discovery.
    Uses Consul HTTP API for all operations.
    """

    def __init__(self, consul_url: str = "http://localhost:8500", **kwargs):
        """
        Initialize Consul registry

        Args:
            consul_url: Consul API URL
        """
        super().__init__(**kwargs)
        self.consul_url = consul_url.rstrip("/")

        # Check if requests is available
        try:
            import requests

            self.requests = requests
        except ImportError:
            logger.warning(
                "requests library not available. Consul integration will not work. "
                "Install with: pip install requests"
            )
            self.requests = None

    def register(
        self,
        service_name: str,
        host: str,
        port: int,
        service_id: Optional[str] = None,
        metadata: Optional[ServiceMetadata] = None,
        health_check: Optional[HealthCheck] = None,
    ) -> str:
        """
        Register service with Consul

        Args:
            service_name: Name of the service
            host: Service host
            port: Service port
            service_id: Optional service ID
            metadata: Service metadata
            health_check: Health check configuration

        Returns:
            Service ID
        """
        # First register locally
        service_id = super().register(service_name, host, port, service_id, metadata, health_check)

        # Then register with Consul
        if not self.requests:
            logger.warning("Cannot register with Consul: requests not available")
            return service_id

        try:
            # Prepare Consul service definition
            consul_service = {
                "ID": service_id,
                "Name": service_name,
                "Address": host,
                "Port": port,
                "Tags": metadata.tags if metadata else [],
                "Meta": metadata.metadata if metadata else {},
            }

            # Add health check if provided
            if health_check:
                consul_service["Check"] = {
                    "HTTP": health_check.url,
                    "Interval": f"{health_check.interval}s",
                    "Timeout": f"{health_check.timeout}s",
                }

            # Register with Consul
            response = self.requests.put(
                f"{self.consul_url}/v1/agent/service/register", json=consul_service, timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Service {service_id} registered with Consul")
            else:
                logger.error(f"Failed to register with Consul: {response.status_code} - " f"{response.text[:200]}")

        except Exception as e:
            logger.error(f"Error registering with Consul: {e}")

        return service_id

    def deregister(self, service_id: str) -> bool:
        """
        Deregister service from Consul

        Args:
            service_id: Service ID to deregister

        Returns:
            True if successful
        """
        # Deregister locally
        result = super().deregister(service_id)

        # Deregister from Consul
        if not self.requests:
            return result

        try:
            response = self.requests.put(f"{self.consul_url}/v1/agent/service/deregister/{service_id}", timeout=10)

            if response.status_code == 200:
                logger.info(f"Service {service_id} deregistered from Consul")
            else:
                logger.error(f"Failed to deregister from Consul: {response.status_code}")

        except Exception as e:
            logger.error(f"Error deregistering from Consul: {e}")

        return result

    def sync_from_consul(self) -> int:
        """
        Sync service catalog from Consul

        Fetches all services from Consul and updates local registry.

        Returns:
            Number of services synced
        """
        if not self.requests:
            logger.warning("Cannot sync from Consul: requests not available")
            return 0

        try:
            # Get all services from Consul
            response = self.requests.get(f"{self.consul_url}/v1/catalog/services", timeout=10)

            if response.status_code != 200:
                logger.error(f"Failed to fetch Consul services: {response.status_code}")
                return 0

            services = response.json()
            synced_count = 0

            # Sync each service
            for service_name in services.keys():
                # Get service details
                detail_response = self.requests.get(f"{self.consul_url}/v1/catalog/service/{service_name}", timeout=10)

                if detail_response.status_code == 200:
                    service_instances = detail_response.json()

                    for instance in service_instances:
                        # Register in local registry
                        try:
                            super().register(
                                service_name=service_name,
                                host=instance.get("ServiceAddress", instance.get("Address")),
                                port=instance.get("ServicePort"),
                                service_id=instance.get("ServiceID"),
                                metadata=ServiceMetadata(
                                    tags=instance.get("ServiceTags", []), metadata=instance.get("ServiceMeta", {})
                                ),
                            )
                            synced_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to sync service {service_name}: {e}")

            logger.info(f"Synced {synced_count} services from Consul")
            return synced_count

        except Exception as e:
            logger.error(f"Error syncing from Consul: {e}")
            return 0


class EurekaServiceRegistry(ServiceRegistry):
    """
    Eureka-based service registry

    Integrates with Netflix Eureka for service discovery.
    Uses Eureka REST API for all operations.
    """

    def __init__(self, eureka_url: str = "http://localhost:8761/eureka", **kwargs):
        """
        Initialize Eureka registry

        Args:
            eureka_url: Eureka server URL
        """
        super().__init__(**kwargs)
        self.eureka_url = eureka_url.rstrip("/")
        self._heartbeat_threads: Dict[str, threading.Thread] = {}
        self._heartbeat_interval = 30  # seconds

        # Check if requests is available
        try:
            import requests

            self.requests = requests
        except ImportError:
            logger.warning(
                "requests library not available. Eureka integration will not work. "
                "Install with: pip install requests"
            )
            self.requests = None

    def register(
        self,
        service_name: str,
        host: str,
        port: int,
        service_id: Optional[str] = None,
        metadata: Optional[ServiceMetadata] = None,
        health_check: Optional[HealthCheck] = None,
    ) -> str:
        """
        Register service with Eureka

        Args:
            service_name: Name of the service
            host: Service host
            port: Service port
            service_id: Optional service ID
            metadata: Service metadata
            health_check: Health check configuration

        Returns:
            Service ID
        """
        # First register locally
        service_id = super().register(service_name, host, port, service_id, metadata, health_check)

        # Then register with Eureka
        if not self.requests:
            logger.warning("Cannot register with Eureka: requests not available")
            return service_id

        try:
            # Prepare Eureka instance definition
            eureka_instance = {
                "instance": {
                    "instanceId": service_id,
                    "hostName": host,
                    "app": service_name.upper(),
                    "ipAddr": host,
                    "status": "UP",
                    "port": {"$": port, "@enabled": "true"},
                    "dataCenterInfo": {
                        "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                        "name": "MyOwn",
                    },
                    "metadata": metadata.metadata if metadata else {},
                }
            }

            # Register with Eureka
            response = self.requests.post(
                f"{self.eureka_url}/apps/{service_name.upper()}",
                json=eureka_instance,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code in (200, 204):
                logger.info(f"Service {service_id} registered with Eureka")

                # Start heartbeat thread
                self._start_heartbeat(service_id, service_name)
            else:
                logger.error(f"Failed to register with Eureka: {response.status_code} - " f"{response.text[:200]}")

        except Exception as e:
            logger.error(f"Error registering with Eureka: {e}")

        return service_id

    def deregister(self, service_id: str) -> bool:
        """
        Deregister service from Eureka

        Args:
            service_id: Service ID to deregister

        Returns:
            True if successful
        """
        # Stop heartbeat thread
        self._stop_heartbeat(service_id)

        # Get service info for Eureka deregistration
        instance = self.get_instance(service_id)

        # Deregister locally
        result = super().deregister(service_id)

        # Deregister from Eureka
        if not self.requests or not instance:
            return result

        try:
            app_name = instance.service_name.upper()
            response = self.requests.delete(f"{self.eureka_url}/apps/{app_name}/{service_id}", timeout=10)

            if response.status_code in (200, 204):
                logger.info(f"Service {service_id} deregistered from Eureka")
            else:
                logger.error(f"Failed to deregister from Eureka: {response.status_code}")

        except Exception as e:
            logger.error(f"Error deregistering from Eureka: {e}")

        return result

    def _start_heartbeat(self, service_id: str, service_name: str):
        """
        Start heartbeat thread for service

        Args:
            service_id: Service ID
            service_name: Service name
        """

        def heartbeat_loop():
            while self._running and service_id in self._heartbeat_threads:
                try:
                    self._send_heartbeat(service_id, service_name)
                    time.sleep(self._heartbeat_interval)
                except Exception as e:
                    logger.error(f"Heartbeat error for {service_id}: {e}")

        thread = threading.Thread(target=heartbeat_loop, daemon=True, name=f"eureka-heartbeat-{service_id}")
        self._heartbeat_threads[service_id] = thread
        thread.start()
        logger.info(f"Started heartbeat for service {service_id}")

    def _stop_heartbeat(self, service_id: str):
        """
        Stop heartbeat thread for service

        Args:
            service_id: Service ID
        """
        if service_id in self._heartbeat_threads:
            del self._heartbeat_threads[service_id]
            logger.info(f"Stopped heartbeat for service {service_id}")

    def _send_heartbeat(self, service_id: str, service_name: str) -> bool:
        """
        Send heartbeat to Eureka

        Args:
            service_id: Service ID
            service_name: Service name

        Returns:
            True if successful
        """
        if not self.requests:
            return False

        try:
            response = self.requests.put(f"{self.eureka_url}/apps/{service_name.upper()}/{service_id}", timeout=10)

            if response.status_code == 200:
                logger.debug(f"Heartbeat sent for service {service_id}")
                return True
            else:
                logger.warning(f"Heartbeat failed for {service_id}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending heartbeat for {service_id}: {e}")
            return False

    def fetch_from_eureka(self) -> int:
        """
        Fetch service catalog from Eureka

        Fetches all services from Eureka and updates local registry.

        Returns:
            Number of services fetched
        """
        if not self.requests:
            logger.warning("Cannot fetch from Eureka: requests not available")
            return 0

        try:
            # Get all applications from Eureka
            response = self.requests.get(f"{self.eureka_url}/apps", headers={"Accept": "application/json"}, timeout=10)

            if response.status_code != 200:
                logger.error(f"Failed to fetch Eureka apps: {response.status_code}")
                return 0

            apps_data = response.json()
            fetched_count = 0

            # Parse Eureka response
            applications = apps_data.get("applications", {}).get("application", [])

            # Handle single application case
            if isinstance(applications, dict):
                applications = [applications]

            for app in applications:
                app_name = app.get("name", "").lower()
                instances = app.get("instance", [])

                # Handle single instance case
                if isinstance(instances, dict):
                    instances = [instances]

                for instance in instances:
                    try:
                        # Register in local registry
                        super().register(
                            service_name=app_name,
                            host=instance.get("ipAddr", instance.get("hostName")),
                            port=instance.get("port", {}).get("$", 0),
                            service_id=instance.get("instanceId"),
                            metadata=ServiceMetadata(metadata=instance.get("metadata", {})),
                        )
                        fetched_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to fetch instance {instance.get('instanceId')}: {e}")

            logger.info(f"Fetched {fetched_count} services from Eureka")
            return fetched_count

        except Exception as e:
            logger.error(f"Error fetching from Eureka: {e}")
            return 0


# Singleton registry instance
_default_registry: Optional[ServiceRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> ServiceRegistry:
    """
    Get default service registry instance

    Returns:
        Default service registry
    """
    global _default_registry

    if _default_registry is None:
        with _registry_lock:
            if _default_registry is None:
                _default_registry = ServiceRegistry()
                _default_registry.start()

    return _default_registry


def register_service(service_name: str, host: str, port: int, **kwargs) -> str:
    """
    Register service with default registry

    Args:
        service_name: Service name
        host: Service host
        port: Service port
        **kwargs: Additional registration parameters

    Returns:
        Service ID
    """
    return get_registry().register(service_name, host, port, **kwargs)


def deregister_service(service_id: str) -> bool:
    """
    Deregister service from default registry

    Args:
        service_id: Service ID

    Returns:
        True if successful
    """
    return get_registry().deregister(service_id)


def discover_services(service_name: str, **kwargs) -> List[ServiceInstance]:
    """
    Discover services from default registry

    Args:
        service_name: Service name
        **kwargs: Discovery filters

    Returns:
        List of service instances
    """
    return get_registry().discover(service_name, **kwargs)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create registry
    registry = ServiceRegistry()
    registry.start()

    # Register services
    service_id1 = registry.register(
        service_name="user-service",
        host="localhost",
        port=8001,
        metadata=ServiceMetadata(version="1.0.0", tags=["api", "users"]),
        health_check=HealthCheck(check_type="tcp", interval_seconds=5),
    )

    service_id2 = registry.register(
        service_name="user-service",
        host="localhost",
        port=8002,
        metadata=ServiceMetadata(version="1.0.0", tags=["api", "users"]),
    )

    # Discover services
    instances = registry.discover("user-service")
    print(f"\nFound {len(instances)} instances of user-service:")
    for instance in instances:
        print(f"  - {instance.host}:{instance.port} (Status: {instance.status})")

    # Send heartbeat
    registry.heartbeat(service_id1)

    # Update load metrics
    metrics = LoadMetrics(cpu_usage=45.5, memory_usage=62.3, request_count=1000, avg_response_time_ms=23.5)
    registry.update_load_metrics(service_id1, metrics)

    # Get service info
    service = registry.get_service(service_id1)
    if service:
        print(f"\nService {service_id1}:")
        print(f"  Status: {service.status}")
        print(f"  Load: CPU={service.load_metrics.cpu_usage}%, " f"MEM={service.load_metrics.memory_usage}%")

    # Cleanup
    time.sleep(2)
    registry.deregister(service_id1)
    registry.deregister(service_id2)
    registry.stop()
