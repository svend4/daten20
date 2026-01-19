"""
IoT & Edge Computing Module - v3.6

Internet of Things device management and edge computing platform.

Modules:
- device_manager: Device registration, lifecycle, firmware updates, digital twins
- mqtt_broker: MQTT pub/sub messaging with QoS and topic routing
- edge_platform: Edge nodes, local processing, Lambda functions, cloud sync
- telemetry_pipeline: Data ingestion, transformation, aggregation, alerting
- device_protocols: Multi-protocol support (MQTT, CoAP, HTTP, Modbus)
- iot_security: Device authentication, certificates, ACL, encryption

Components:
- Device Manager: Device registry, shadows, grouping, health monitoring
- MQTT Broker: Pub/sub messaging, QoS 0/1/2, retained messages, wildcards
- Edge Platform: Edge nodes, functions, caching, stream processing
- Telemetry Pipeline: High-throughput ingestion, time-series storage, alerts
- Device Protocols: MQTT, CoAP, HTTP, Modbus with protocol translation
- IoT Security: X.509, PSK, JWT, ACL, firmware signing, encryption

Version: 3.6.0 (Complete)
"""

__version__ = "3.6.0"

# Unified IoT & Edge API
from .iot_edge_api import (
    IoTEdgeAPI,
    IoTEdgeConfig,
    IoTOperation,
    get_iot_edge_api,
    register_device,
    publish_telemetry,
    deploy_function,
)

# Device Manager
from .device_manager import (
    Device,
    DeviceGroup,
    DeviceManager,
    DeviceShadow,
    DeviceStatus,
    DeviceType,
    FirmwareVersion,
    Location,
    get_device_manager,
)

# Device Protocols
from .device_protocols import (
    ConnectionConfig,
    DeviceConnector,
    MessageFormat,
    ProtocolMessage,
    ProtocolType,
    get_device_connector,
)

# Edge Platform
from .edge_platform import (
    EdgeFunction,
    EdgeNode,
    EdgeNodeStatus,
    EdgePlatform,
    EdgeResources,
    FunctionStatus,
    get_edge_platform,
)

# IoT Security
from .iot_security import (
    AccessControlEntry,
    AccessLevel,
    AuthMethod,
    Certificate,
    IoTSecurity,
    PreSharedKey,
    get_iot_security,
)

# Legacy (backward compatibility)
from .iot_services import Device as LegacyDevice
from .iot_services import DeviceManager as LegacyDeviceManager
from .iot_services import DeviceShadow as LegacyDeviceShadow
from .iot_services import DeviceStatus as LegacyDeviceStatus
from .iot_services import DeviceType as LegacyDeviceType
from .iot_services import EdgeFunction as LegacyEdgeFunction
from .iot_services import EdgeNode as LegacyEdgeNode
from .iot_services import EdgePlatform as LegacyEdgePlatform
from .iot_services import MQTTBroker as LegacyMQTTBroker
from .iot_services import MQTTMessage as LegacyMQTTMessage
from .iot_services import (
    MQTTTopic,
)
from .iot_services import QoSLevel as LegacyQoSLevel
from .iot_services import (
    Telemetry,
)
from .iot_services import TelemetryPipeline as LegacyTelemetryPipeline

# MQTT Broker
from .mqtt_broker import (
    ClientSession,
    MQTTBroker,
    MQTTClient,
    MQTTMessage,
    QoSLevel,
    Subscription,
    create_mqtt_client,
    get_mqtt_broker,
)

# Telemetry Pipeline
from .telemetry_pipeline import (
    AggregatedData,
    AggregationType,
    Alert,
    AlertRule,
    AlertSeverity,
    TelemetryPipeline,
    TelemetryPoint,
    TelemetryType,
    get_telemetry_pipeline,
)

__all__ = [
    # Unified API
    'IoTEdgeAPI',
    'IoTEdgeConfig',
    'IoTOperation',
    'get_iot_edge_api',
    'register_device',
    'publish_telemetry',
    'deploy_function',

    # Device Manager
    "Device",
    "DeviceStatus",
    "DeviceType",
    "DeviceShadow",
    "Location",
    "FirmwareVersion",
    "DeviceGroup",
    "DeviceManager",
    "get_device_manager",
    # MQTT Broker
    "MQTTBroker",
    "MQTTClient",
    "MQTTMessage",
    "QoSLevel",
    "ClientSession",
    "Subscription",
    "get_mqtt_broker",
    "create_mqtt_client",
    # Edge Platform
    "EdgePlatform",
    "EdgeNode",
    "EdgeFunction",
    "EdgeNodeStatus",
    "FunctionStatus",
    "EdgeResources",
    "get_edge_platform",
    # Telemetry Pipeline
    "TelemetryPipeline",
    "TelemetryPoint",
    "AggregatedData",
    "AlertRule",
    "Alert",
    "TelemetryType",
    "AggregationType",
    "AlertSeverity",
    "get_telemetry_pipeline",
    # Device Protocols
    "DeviceConnector",
    "ProtocolType",
    "ProtocolMessage",
    "ConnectionConfig",
    "MessageFormat",
    "get_device_connector",
    # IoT Security
    "IoTSecurity",
    "Certificate",
    "PreSharedKey",
    "AccessControlEntry",
    "AuthMethod",
    "AccessLevel",
    "get_iot_security",
    # Legacy (backward compatibility)
    "LegacyDevice",
    "LegacyDeviceStatus",
    "LegacyDeviceType",
    "LegacyDeviceShadow",
    "LegacyDeviceManager",
    "LegacyMQTTBroker",
    "LegacyMQTTMessage",
    "MQTTTopic",
    "LegacyQoSLevel",
    "LegacyEdgeNode",
    "LegacyEdgeFunction",
    "LegacyEdgePlatform",
    "Telemetry",
    "LegacyTelemetryPipeline",
]
