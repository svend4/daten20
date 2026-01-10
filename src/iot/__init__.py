"""
IoT & Edge Computing Module - v3.6

Internet of Things device management and edge computing platform.

Modules:
- iot_services: Unified IoT and edge computing services

Components:
- Device Manager: Device registration, lifecycle, shadows
- MQTT Broker: Pub/Sub messaging with QoS support
- Edge Platform: Edge computing nodes with local processing
- Telemetry Pipeline: Data ingestion and time-series storage
- Device Security: Authentication, certificates, encryption

Version: 3.6.0
"""

__version__ = '3.6.0'

from .iot_services import (
    # Device Management
    Device,
    DeviceStatus,
    DeviceType,
    DeviceShadow,
    DeviceManager,
    get_device_manager,
    # MQTT Broker
    MQTTBroker,
    MQTTMessage,
    MQTTTopic,
    QoSLevel,
    get_mqtt_broker,
    # Edge Platform
    EdgeNode,
    EdgeFunction,
    EdgePlatform,
    get_edge_platform,
    # Telemetry
    Telemetry,
    TelemetryPipeline,
    get_telemetry_pipeline,
)

__all__ = [
    # Device Management
    'Device',
    'DeviceStatus',
    'DeviceType',
    'DeviceShadow',
    'DeviceManager',
    'get_device_manager',
    # MQTT Broker
    'MQTTBroker',
    'MQTTMessage',
    'MQTTTopic',
    'QoSLevel',
    'get_mqtt_broker',
    # Edge Platform
    'EdgeNode',
    'EdgeFunction',
    'EdgePlatform',
    'get_edge_platform',
    # Telemetry
    'Telemetry',
    'TelemetryPipeline',
    'get_telemetry_pipeline',
]
