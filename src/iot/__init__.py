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

Version: 3.6.0
"""

__version__ = '3.6.0'

# Device Manager
from .device_manager import (
    Device,
    DeviceStatus,
    DeviceType,
    DeviceShadow,
    Location,
    FirmwareVersion,
    DeviceGroup,
    DeviceManager,
    get_device_manager,
)

# MQTT Broker
from .mqtt_broker import (
    MQTTBroker,
    MQTTClient,
    MQTTMessage,
    QoSLevel,
    ClientSession,
    Subscription,
    get_mqtt_broker,
    create_mqtt_client,
)

# Edge Platform
from .edge_platform import (
    EdgePlatform,
    EdgeNode,
    EdgeFunction,
    EdgeNodeStatus,
    FunctionStatus,
    EdgeResources,
    get_edge_platform,
)

# Telemetry Pipeline
from .telemetry_pipeline import (
    TelemetryPipeline,
    TelemetryPoint,
    AggregatedData,
    AlertRule,
    Alert,
    TelemetryType,
    AggregationType,
    AlertSeverity,
    get_telemetry_pipeline,
)

# Device Protocols
from .device_protocols import (
    DeviceConnector,
    ProtocolType,
    ProtocolMessage,
    ConnectionConfig,
    MessageFormat,
    get_device_connector,
)

# IoT Security
from .iot_security import (
    IoTSecurity,
    Certificate,
    PreSharedKey,
    AccessControlEntry,
    AuthMethod,
    AccessLevel,
    get_iot_security,
)

# Legacy (backward compatibility)
from .iot_services import (
    Device as LegacyDevice,
    DeviceStatus as LegacyDeviceStatus,
    DeviceType as LegacyDeviceType,
    DeviceShadow as LegacyDeviceShadow,
    DeviceManager as LegacyDeviceManager,
    MQTTBroker as LegacyMQTTBroker,
    MQTTMessage as LegacyMQTTMessage,
    MQTTTopic,
    QoSLevel as LegacyQoSLevel,
    EdgeNode as LegacyEdgeNode,
    EdgeFunction as LegacyEdgeFunction,
    EdgePlatform as LegacyEdgePlatform,
    Telemetry,
    TelemetryPipeline as LegacyTelemetryPipeline,
)

__all__ = [
    # Device Manager
    'Device',
    'DeviceStatus',
    'DeviceType',
    'DeviceShadow',
    'Location',
    'FirmwareVersion',
    'DeviceGroup',
    'DeviceManager',
    'get_device_manager',

    # MQTT Broker
    'MQTTBroker',
    'MQTTClient',
    'MQTTMessage',
    'QoSLevel',
    'ClientSession',
    'Subscription',
    'get_mqtt_broker',
    'create_mqtt_client',

    # Edge Platform
    'EdgePlatform',
    'EdgeNode',
    'EdgeFunction',
    'EdgeNodeStatus',
    'FunctionStatus',
    'EdgeResources',
    'get_edge_platform',

    # Telemetry Pipeline
    'TelemetryPipeline',
    'TelemetryPoint',
    'AggregatedData',
    'AlertRule',
    'Alert',
    'TelemetryType',
    'AggregationType',
    'AlertSeverity',
    'get_telemetry_pipeline',

    # Device Protocols
    'DeviceConnector',
    'ProtocolType',
    'ProtocolMessage',
    'ConnectionConfig',
    'MessageFormat',
    'get_device_connector',

    # IoT Security
    'IoTSecurity',
    'Certificate',
    'PreSharedKey',
    'AccessControlEntry',
    'AuthMethod',
    'AccessLevel',
    'get_iot_security',

    # Legacy (backward compatibility)
    'LegacyDevice',
    'LegacyDeviceStatus',
    'LegacyDeviceType',
    'LegacyDeviceShadow',
    'LegacyDeviceManager',
    'LegacyMQTTBroker',
    'LegacyMQTTMessage',
    'MQTTTopic',
    'LegacyQoSLevel',
    'LegacyEdgeNode',
    'LegacyEdgeFunction',
    'LegacyEdgePlatform',
    'Telemetry',
    'LegacyTelemetryPipeline',
]
