"""
Unified IoT & Edge API - v3.6

Single interface for all IoT and edge computing operations.
Provides simplified API for device management, telemetry, edge processing.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from .device_manager import get_device_manager, DeviceStatus, DeviceType
from .mqtt_broker import get_mqtt_broker, QoSLevel
from .edge_platform import get_edge_platform, EdgeNodeStatus
from .telemetry_pipeline import get_telemetry_pipeline, TelemetryType, AlertSeverity
from .device_protocols import get_device_connector, ProtocolType
from .iot_security import get_iot_security, AuthMethod

logger = logging.getLogger(__name__)


class IoTOperation(Enum):
    """IoT operation types"""
    REGISTER_DEVICE = "register_device"
    UPDATE_DEVICE = "update_device"
    PUBLISH_TELEMETRY = "publish_telemetry"
    SUBSCRIBE_TOPIC = "subscribe_topic"
    DEPLOY_FUNCTION = "deploy_function"
    CREATE_ALERT = "create_alert"
    AUTHENTICATE = "authenticate"
    PROVISION = "provision"


@dataclass
class IoTEdgeConfig:
    """Configuration for IoT & Edge API"""
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    enable_tls: bool = True
    enable_edge: bool = True
    enable_security: bool = True
    max_devices: int = 10000
    telemetry_batch_size: int = 1000
    telemetry_flush_interval: int = 5


class IoTEdgeAPI:
    """
    Unified IoT & Edge API - Single interface for all IoT operations

    This class provides a simplified, unified interface to all IoT services:
    - Device management (registration, lifecycle, shadows, firmware)
    - MQTT messaging (pub/sub, topics, QoS)
    - Edge computing (functions, nodes, local processing)
    - Telemetry pipeline (ingestion, aggregation, alerting)
    - Multi-protocol support (MQTT, CoAP, HTTP, Modbus)
    - IoT security (authentication, certificates, ACL)

    Example:
        api = get_iot_edge_api()

        # Register device
        device = api.register_device("sensor-001", device_type="temperature")

        # Publish telemetry
        api.publish_telemetry("sensor-001", "temperature", 22.5, unit="celsius")

        # Deploy edge function
        api.deploy_edge_function("process-temp", code=lambda data: data * 1.8 + 32)
    """

    def __init__(
        self,
        config: Optional[IoTEdgeConfig] = None,
        enable_device_manager: bool = True,
        enable_mqtt: bool = True,
        enable_edge: bool = True,
        enable_telemetry: bool = True,
        enable_protocols: bool = True,
        enable_security: bool = True
    ):
        """Initialize IoT & Edge API with services"""
        self.config = config or IoTEdgeConfig()

        # Initialize services
        self.device_manager = get_device_manager() if enable_device_manager else None
        self.mqtt_broker = get_mqtt_broker() if enable_mqtt else None
        self.edge_platform = get_edge_platform() if enable_edge else None
        self.telemetry_pipeline = get_telemetry_pipeline() if enable_telemetry else None
        self.device_connector = get_device_connector() if enable_protocols else None
        self.iot_security = get_iot_security() if enable_security else None

        # Statistics
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in IoTOperation},
            "devices_registered": 0,
            "telemetry_points": 0,
            "messages_published": 0,
            "edge_functions": 0,
            "alerts_triggered": 0,
        }

        logger.info("IoT & Edge API initialized with all services")

    # ==================== Device Management ====================

    def register_device(
        self,
        device_id: str,
        device_name: str,
        device_type: DeviceType,
        location: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Register new IoT device

        Args:
            device_id: Unique device identifier
            device_name: Human-readable name
            device_type: Type of device
            location: Physical location
            metadata: Custom metadata

        Returns:
            Device information
        """
        if not self.device_manager:
            raise ValueError("Device manager not enabled")

        self._track_operation(IoTOperation.REGISTER_DEVICE)

        device = self.device_manager.register_device(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            location=location,
            metadata=metadata or {},
            **kwargs
        )

        self.stats["devices_registered"] += 1

        return {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type.value,
            "status": device.status.value,
            "registered_at": device.registered_at.isoformat()
        }

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device information"""
        if not self.device_manager:
            raise ValueError("Device manager not enabled")

        device = self.device_manager.get_device(device_id)
        if not device:
            return None

        return {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type.value,
            "status": device.status.value,
            "last_seen": device.last_seen.isoformat() if device.last_seen else None,
            "firmware_version": device.firmware_version,
            "location": device.location,
            "metadata": device.metadata
        }

    def update_device_status(
        self,
        device_id: str,
        status: DeviceStatus,
        **kwargs
    ) -> bool:
        """Update device status"""
        if not self.device_manager:
            raise ValueError("Device manager not enabled")

        self._track_operation(IoTOperation.UPDATE_DEVICE)

        return self.device_manager.update_device_status(
            device_id=device_id,
            status=status,
            **kwargs
        )

    def get_device_shadow(self, device_id: str) -> Dict[str, Any]:
        """Get device shadow (digital twin)"""
        if not self.device_manager:
            raise ValueError("Device manager not enabled")

        shadow = self.device_manager.get_device_shadow(device_id)

        return {
            "desired": shadow.desired,
            "reported": shadow.reported,
            "delta": shadow.delta,
            "version": shadow.version,
            "last_updated": shadow.last_updated.isoformat()
        }

    def update_device_shadow(
        self,
        device_id: str,
        desired: Optional[Dict[str, Any]] = None,
        reported: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Update device shadow"""
        if not self.device_manager:
            raise ValueError("Device manager not enabled")

        shadow = self.device_manager.update_device_shadow(
            device_id=device_id,
            desired=desired,
            reported=reported,
            **kwargs
        )

        return {
            "version": shadow.version,
            "delta": shadow.delta
        }

    def list_devices(
        self,
        status: Optional[DeviceStatus] = None,
        device_type: Optional[DeviceType] = None,
        group: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List devices with filters"""
        if not self.device_manager:
            raise ValueError("Device manager not enabled")

        devices = self.device_manager.list_devices(
            status=status,
            device_type=device_type,
            group=group,
            **kwargs
        )

        return [
            {
                "device_id": d.device_id,
                "device_name": d.device_name,
                "device_type": d.device_type.value,
                "status": d.status.value
            }
            for d in devices
        ]

    # ==================== MQTT Messaging ====================

    def publish(
        self,
        topic: str,
        payload: Any,
        qos: QoSLevel = QoSLevel.AT_MOST_ONCE,
        retain: bool = False,
        **kwargs
    ) -> bool:
        """
        Publish message to MQTT topic

        Args:
            topic: MQTT topic
            payload: Message payload
            qos: Quality of Service level
            retain: Whether to retain message

        Returns:
            Success status
        """
        if not self.mqtt_broker:
            raise ValueError("MQTT broker not enabled")

        self._track_operation(IoTOperation.PUBLISH_TELEMETRY)

        success = self.mqtt_broker.publish(
            topic=topic,
            payload=payload,
            qos=qos,
            retain=retain,
            **kwargs
        )

        if success:
            self.stats["messages_published"] += 1

        return success

    def subscribe(
        self,
        topic: str,
        callback: Callable[[str, Any], None],
        qos: QoSLevel = QoSLevel.AT_LEAST_ONCE,
        **kwargs
    ) -> str:
        """Subscribe to MQTT topic"""
        if not self.mqtt_broker:
            raise ValueError("MQTT broker not enabled")

        self._track_operation(IoTOperation.SUBSCRIBE_TOPIC)

        subscription_id = self.mqtt_broker.subscribe(
            topic=topic,
            callback=callback,
            qos=qos,
            **kwargs
        )

        return subscription_id

    def unsubscribe(self, topic: str, subscription_id: Optional[str] = None) -> bool:
        """Unsubscribe from MQTT topic"""
        if not self.mqtt_broker:
            raise ValueError("MQTT broker not enabled")

        return self.mqtt_broker.unsubscribe(topic, subscription_id)

    # ==================== Edge Computing ====================

    def deploy_edge_function(
        self,
        function_name: str,
        code: Callable,
        node_id: Optional[str] = None,
        runtime: str = "python3.9",
        memory_mb: int = 128,
        timeout_sec: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Deploy function to edge node

        Args:
            function_name: Function name
            code: Function code (callable)
            node_id: Target edge node ID
            runtime: Runtime environment
            memory_mb: Memory limit
            timeout_sec: Execution timeout

        Returns:
            Deployment information
        """
        if not self.edge_platform:
            raise ValueError("Edge platform not enabled")

        self._track_operation(IoTOperation.DEPLOY_FUNCTION)

        function = self.edge_platform.deploy_function(
            function_name=function_name,
            code=code,
            node_id=node_id,
            runtime=runtime,
            memory_mb=memory_mb,
            timeout_sec=timeout_sec,
            **kwargs
        )

        self.stats["edge_functions"] += 1

        return {
            "function_id": function.function_id,
            "function_name": function.function_name,
            "node_id": function.node_id,
            "status": function.status.value,
            "deployed_at": function.deployed_at.isoformat()
        }

    def invoke_edge_function(
        self,
        function_name: str,
        input_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Invoke edge function"""
        if not self.edge_platform:
            raise ValueError("Edge platform not enabled")

        result = self.edge_platform.invoke_function(
            function_name=function_name,
            input_data=input_data,
            **kwargs
        )

        return {
            "output": result.output,
            "execution_time_ms": result.execution_time_ms,
            "memory_used_mb": result.memory_used_mb,
            "logs": result.logs
        }

    def list_edge_nodes(
        self,
        status: Optional[EdgeNodeStatus] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List edge nodes"""
        if not self.edge_platform:
            raise ValueError("Edge platform not enabled")

        nodes = self.edge_platform.list_nodes(status=status, **kwargs)

        return [
            {
                "node_id": n.node_id,
                "node_name": n.node_name,
                "status": n.status.value,
                "location": n.location,
                "resources": {
                    "cpu_usage": n.resources.cpu_usage,
                    "memory_usage_mb": n.resources.memory_usage_mb,
                    "disk_usage_mb": n.resources.disk_usage_mb
                }
            }
            for n in nodes
        ]

    # ==================== Telemetry ====================

    def publish_telemetry(
        self,
        device_id: str,
        metric_name: str,
        value: Any,
        unit: Optional[str] = None,
        telemetry_type: TelemetryType = TelemetryType.NUMERIC,
        **kwargs
    ) -> bool:
        """
        Publish telemetry data

        Args:
            device_id: Device ID
            metric_name: Metric name
            value: Metric value
            unit: Unit of measurement
            telemetry_type: Type of telemetry

        Returns:
            Success status
        """
        if not self.telemetry_pipeline:
            raise ValueError("Telemetry pipeline not enabled")

        self._track_operation(IoTOperation.PUBLISH_TELEMETRY)

        success = self.telemetry_pipeline.ingest(
            device_id=device_id,
            metric_name=metric_name,
            value=value,
            unit=unit,
            telemetry_type=telemetry_type,
            **kwargs
        )

        if success:
            self.stats["telemetry_points"] += 1

        return success

    def query_telemetry(
        self,
        device_id: str,
        metric_name: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Query telemetry data"""
        if not self.telemetry_pipeline:
            raise ValueError("Telemetry pipeline not enabled")

        points = self.telemetry_pipeline.query(
            device_id=device_id,
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            **kwargs
        )

        return [
            {
                "timestamp": p.timestamp.isoformat(),
                "metric_name": p.metric_name,
                "value": p.value,
                "unit": p.unit
            }
            for p in points
        ]

    def create_alert_rule(
        self,
        rule_name: str,
        device_id: str,
        metric_name: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity,
        **kwargs
    ) -> str:
        """Create alert rule for telemetry"""
        if not self.telemetry_pipeline:
            raise ValueError("Telemetry pipeline not enabled")

        self._track_operation(IoTOperation.CREATE_ALERT)

        rule_id = self.telemetry_pipeline.create_alert_rule(
            rule_name=rule_name,
            device_id=device_id,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            severity=severity,
            **kwargs
        )

        return rule_id

    def get_alerts(
        self,
        device_id: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Get triggered alerts"""
        if not self.telemetry_pipeline:
            raise ValueError("Telemetry pipeline not enabled")

        alerts = self.telemetry_pipeline.get_alerts(
            device_id=device_id,
            severity=severity,
            limit=limit,
            **kwargs
        )

        return [
            {
                "alert_id": a.alert_id,
                "device_id": a.device_id,
                "metric_name": a.metric_name,
                "severity": a.severity.value,
                "message": a.message,
                "triggered_at": a.triggered_at.isoformat()
            }
            for a in alerts
        ]

    # ==================== Multi-Protocol Support ====================

    def connect_device(
        self,
        device_id: str,
        protocol: ProtocolType,
        connection_config: Dict[str, Any],
        **kwargs
    ) -> bool:
        """Connect device using specified protocol"""
        if not self.device_connector:
            raise ValueError("Device connector not enabled")

        return self.device_connector.connect(
            device_id=device_id,
            protocol=protocol,
            config=connection_config,
            **kwargs
        )

    def send_command(
        self,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send command to device"""
        if not self.device_connector:
            raise ValueError("Device connector not enabled")

        response = self.device_connector.send_command(
            device_id=device_id,
            command=command,
            parameters=parameters or {},
            **kwargs
        )

        return {
            "status": response.status,
            "result": response.result,
            "execution_time_ms": response.execution_time_ms
        }

    # ==================== Security ====================

    def provision_device(
        self,
        device_id: str,
        auth_method: AuthMethod,
        credentials: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Provision device with security credentials

        Args:
            device_id: Device ID
            auth_method: Authentication method
            credentials: Security credentials

        Returns:
            Provisioning information
        """
        if not self.iot_security:
            raise ValueError("IoT security not enabled")

        self._track_operation(IoTOperation.PROVISION)

        provision_info = self.iot_security.provision_device(
            device_id=device_id,
            auth_method=auth_method,
            credentials=credentials,
            **kwargs
        )

        return provision_info

    def authenticate_device(
        self,
        device_id: str,
        credentials: Dict[str, Any],
        **kwargs
    ) -> bool:
        """Authenticate device"""
        if not self.iot_security:
            raise ValueError("IoT security not enabled")

        self._track_operation(IoTOperation.AUTHENTICATE)

        return self.iot_security.authenticate(
            device_id=device_id,
            credentials=credentials,
            **kwargs
        )

    def create_access_policy(
        self,
        device_id: str,
        resources: List[str],
        actions: List[str],
        **kwargs
    ) -> str:
        """Create access control policy for device"""
        if not self.iot_security:
            raise ValueError("IoT security not enabled")

        policy_id = self.iot_security.create_policy(
            device_id=device_id,
            resources=resources,
            actions=actions,
            **kwargs
        )

        return policy_id

    # ==================== Utility Methods ====================

    def _track_operation(self, operation: IoTOperation):
        """Track operation statistics"""
        self.stats["total_operations"] += 1
        self.stats["by_operation"][operation.value] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get API usage statistics

        Returns:
            Dict with usage statistics
        """
        return {
            **self.stats,
            "services_enabled": {
                "device_manager": self.device_manager is not None,
                "mqtt_broker": self.mqtt_broker is not None,
                "edge_platform": self.edge_platform is not None,
                "telemetry_pipeline": self.telemetry_pipeline is not None,
                "device_connector": self.device_connector is not None,
                "iot_security": self.iot_security is not None,
            }
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        health = {
            "status": "healthy",
            "services": {}
        }

        if self.device_manager:
            health["services"]["device_manager"] = self.device_manager.get_health()

        if self.mqtt_broker:
            health["services"]["mqtt_broker"] = self.mqtt_broker.get_health()

        if self.edge_platform:
            health["services"]["edge_platform"] = self.edge_platform.get_health()

        if self.telemetry_pipeline:
            health["services"]["telemetry_pipeline"] = self.telemetry_pipeline.get_health()

        return health


# Singleton
_iot_edge_api = None


def get_iot_edge_api(config: Optional[IoTEdgeConfig] = None) -> IoTEdgeAPI:
    """
    Get singleton IoT & Edge API instance

    Args:
        config: Optional configuration

    Returns:
        IoT & Edge API instance
    """
    global _iot_edge_api
    if _iot_edge_api is None:
        _iot_edge_api = IoTEdgeAPI(config=config)
    return _iot_edge_api


# Convenience functions

def register_device(device_id: str, device_name: str, device_type: DeviceType, **kwargs) -> Dict[str, Any]:
    """Convenience function for device registration"""
    api = get_iot_edge_api()
    return api.register_device(device_id, device_name, device_type, **kwargs)


def publish_telemetry(device_id: str, metric_name: str, value: Any, **kwargs) -> bool:
    """Convenience function for publishing telemetry"""
    api = get_iot_edge_api()
    return api.publish_telemetry(device_id, metric_name, value, **kwargs)


def deploy_function(function_name: str, code: Callable, **kwargs) -> Dict[str, Any]:
    """Convenience function for deploying edge functions"""
    api = get_iot_edge_api()
    return api.deploy_edge_function(function_name, code, **kwargs)
