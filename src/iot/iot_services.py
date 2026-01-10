"""
IoT & Edge Computing Services - v3.6

Comprehensive IoT device management and edge computing platform.
"""

import asyncio
import hashlib
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Set, Union
from uuid import uuid4


# ============================================================================
# Device Management
# ============================================================================


class DeviceStatus(Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    PROVISIONING = "provisioning"
    DEACTIVATED = "deactivated"


class DeviceType(Enum):
    """Device type"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    CAMERA = "camera"
    CONTROLLER = "controller"


@dataclass
class Location:
    """Physical location"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    room: Optional[str] = None
    floor: Optional[int] = None
    building: Optional[str] = None
    address: Optional[str] = None


@dataclass
class DeviceShadow:
    """Device shadow (digital twin)"""
    desired: Dict[str, Any] = field(default_factory=dict)
    reported: Dict[str, Any] = field(default_factory=dict)
    delta: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    last_updated: datetime = field(default_factory=datetime.now)

    def update_desired(self, state: Dict[str, Any]):
        """Update desired state and calculate delta"""
        self.desired.update(state)
        self._calculate_delta()
        self.version += 1
        self.last_updated = datetime.now()

    def update_reported(self, state: Dict[str, Any]):
        """Update reported state and calculate delta"""
        self.reported.update(state)
        self._calculate_delta()
        self.version += 1
        self.last_updated = datetime.now()

    def _calculate_delta(self):
        """Calculate delta between desired and reported"""
        self.delta = {}
        for key, value in self.desired.items():
            if key not in self.reported or self.reported[key] != value:
                self.delta[key] = value


@dataclass
class Device:
    """IoT Device"""
    device_id: str
    device_name: str
    device_type: DeviceType
    status: DeviceStatus = DeviceStatus.PROVISIONING
    last_seen: Optional[datetime] = None
    firmware_version: str = "1.0.0"
    location: Optional[Location] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    shadow: DeviceShadow = field(default_factory=DeviceShadow)
    groups: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_online(self) -> bool:
        """Check if device is online"""
        if not self.last_seen:
            return False
        return (datetime.now() - self.last_seen) < timedelta(minutes=5)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type.value,
            'status': self.status.value,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'firmware_version': self.firmware_version,
            'location': self.location.__dict__ if self.location else None,
            'metadata': self.metadata,
            'shadow': {
                'desired': self.shadow.desired,
                'reported': self.shadow.reported,
                'delta': self.shadow.delta,
                'version': self.shadow.version
            },
            'groups': self.groups,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class DeviceManager:
    """
    IoT Device Manager

    Manages device registration, lifecycle, and shadows.
    """

    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._groups: Dict[str, Set[str]] = defaultdict(set)
        self._lock = Lock()

    def register_device(
        self,
        device_id: str,
        device_name: str,
        device_type: DeviceType,
        location: Optional[Location] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Device:
        """Register a new device"""
        with self._lock:
            if device_id in self._devices:
                raise ValueError(f"Device {device_id} already registered")

            device = Device(
                device_id=device_id,
                device_name=device_name,
                device_type=device_type,
                location=location,
                metadata=metadata or {}
            )
            self._devices[device_id] = device
            return device

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self._devices.get(device_id)

    def update_device(
        self,
        device_id: str,
        **updates
    ) -> Optional[Device]:
        """Update device properties"""
        device = self.get_device(device_id)
        if not device:
            return None

        with self._lock:
            for key, value in updates.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            device.updated_at = datetime.now()
            return device

    def deactivate_device(self, device_id: str) -> bool:
        """Deactivate device"""
        device = self.get_device(device_id)
        if not device:
            return False

        device.status = DeviceStatus.DEACTIVATED
        device.updated_at = datetime.now()
        return True

    def delete_device(self, device_id: str) -> bool:
        """Delete device"""
        with self._lock:
            if device_id in self._devices:
                device = self._devices[device_id]
                # Remove from groups
                for group in device.groups:
                    self._groups[group].discard(device_id)
                del self._devices[device_id]
                return True
            return False

    def heartbeat(self, device_id: str):
        """Update device last seen timestamp"""
        device = self.get_device(device_id)
        if device:
            device.last_seen = datetime.now()
            if device.status != DeviceStatus.ONLINE:
                device.status = DeviceStatus.ONLINE

    def update_shadow(
        self,
        device_id: str,
        desired: Optional[Dict[str, Any]] = None,
        reported: Optional[Dict[str, Any]] = None
    ) -> Optional[DeviceShadow]:
        """Update device shadow"""
        device = self.get_device(device_id)
        if not device:
            return None

        with self._lock:
            if desired:
                device.shadow.update_desired(desired)
            if reported:
                device.shadow.update_reported(reported)
            return device.shadow

    def add_to_group(self, device_id: str, group: str):
        """Add device to group"""
        device = self.get_device(device_id)
        if device and group not in device.groups:
            device.groups.append(group)
            self._groups[group].add(device_id)

    def remove_from_group(self, device_id: str, group: str):
        """Remove device from group"""
        device = self.get_device(device_id)
        if device and group in device.groups:
            device.groups.remove(group)
            self._groups[group].discard(device_id)

    def get_devices_by_group(self, group: str) -> List[Device]:
        """Get all devices in a group"""
        device_ids = self._groups.get(group, set())
        return [self._devices[did] for did in device_ids if did in self._devices]

    def list_devices(
        self,
        status: Optional[DeviceStatus] = None,
        device_type: Optional[DeviceType] = None,
        group: Optional[str] = None
    ) -> List[Device]:
        """List devices with filters"""
        devices = list(self._devices.values())

        if status:
            devices = [d for d in devices if d.status == status]
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        if group:
            devices = [d for d in devices if group in d.groups]

        return devices

    def get_statistics(self) -> Dict[str, Any]:
        """Get device statistics"""
        total = len(self._devices)
        online = sum(1 for d in self._devices.values() if d.is_online())
        by_type = defaultdict(int)
        by_status = defaultdict(int)

        for device in self._devices.values():
            by_type[device.device_type.value] += 1
            by_status[device.status.value] += 1

        return {
            'total_devices': total,
            'online_devices': online,
            'offline_devices': total - online,
            'by_type': dict(by_type),
            'by_status': dict(by_status),
            'groups': len(self._groups)
        }


# Singleton instance
_device_manager: Optional[DeviceManager] = None


def get_device_manager() -> DeviceManager:
    """Get singleton device manager instance"""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager


# ============================================================================
# MQTT Broker
# ============================================================================


class QoSLevel(Enum):
    """Quality of Service levels"""
    AT_MOST_ONCE = 0    # Fire and forget
    AT_LEAST_ONCE = 1   # Acknowledged delivery
    EXACTLY_ONCE = 2    # Assured delivery


@dataclass
class MQTTMessage:
    """MQTT message"""
    topic: str
    payload: Union[str, bytes, Dict[str, Any]]
    qos: QoSLevel = QoSLevel.AT_MOST_ONCE
    retain: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid4()))

    def to_bytes(self) -> bytes:
        """Convert payload to bytes"""
        if isinstance(self.payload, bytes):
            return self.payload
        elif isinstance(self.payload, dict):
            return json.dumps(self.payload).encode('utf-8')
        else:
            return str(self.payload).encode('utf-8')

    def to_dict(self) -> Dict[str, Any]:
        """Convert payload to dictionary"""
        if isinstance(self.payload, dict):
            return self.payload
        elif isinstance(self.payload, bytes):
            try:
                return json.loads(self.payload.decode('utf-8'))
            except:
                return {'data': self.payload.decode('utf-8', errors='ignore')}
        else:
            try:
                return json.loads(str(self.payload))
            except:
                return {'data': str(self.payload)}


@dataclass
class MQTTTopic:
    """MQTT topic"""
    name: str
    subscribers: Set[str] = field(default_factory=set)
    retained_message: Optional[MQTTMessage] = None

    def matches(self, pattern: str) -> bool:
        """Check if topic matches pattern with wildcards"""
        # Convert MQTT wildcards to regex
        # + matches single level
        # # matches multiple levels
        regex_pattern = pattern.replace('+', '[^/]+').replace('#', '.*')
        regex_pattern = f"^{regex_pattern}$"
        return bool(re.match(regex_pattern, self.name))


class MQTTBroker:
    """
    MQTT Broker

    Lightweight message broker with pub/sub and QoS support.
    """

    def __init__(self):
        self._topics: Dict[str, MQTTTopic] = {}
        self._subscriptions: Dict[str, Dict[str, QoSLevel]] = defaultdict(dict)
        self._message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._retained_messages: Dict[str, MQTTMessage] = {}
        self._lock = Lock()
        self._stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'active_subscriptions': 0
        }

    async def publish(
        self,
        topic: str,
        payload: Union[str, bytes, Dict[str, Any]],
        qos: QoSLevel = QoSLevel.AT_MOST_ONCE,
        retain: bool = False
    ) -> MQTTMessage:
        """Publish message to topic"""
        message = MQTTMessage(
            topic=topic,
            payload=payload,
            qos=qos,
            retain=retain
        )

        with self._lock:
            # Store retained message
            if retain:
                self._retained_messages[topic] = message

            # Get or create topic
            if topic not in self._topics:
                self._topics[topic] = MQTTTopic(name=topic)

            topic_obj = self._topics[topic]
            if retain:
                topic_obj.retained_message = message

            self._stats['messages_published'] += 1

        # Deliver to subscribers
        await self._deliver_message(message)

        return message

    async def subscribe(
        self,
        client_id: str,
        topic_pattern: str,
        qos: QoSLevel = QoSLevel.AT_MOST_ONCE,
        callback: Optional[Callable] = None
    ):
        """Subscribe to topic pattern"""
        with self._lock:
            self._subscriptions[client_id][topic_pattern] = qos

            if callback:
                self._message_handlers[f"{client_id}:{topic_pattern}"].append(callback)

            self._stats['active_subscriptions'] = sum(
                len(subs) for subs in self._subscriptions.values()
            )

        # Deliver retained messages for matching topics
        for topic_name, message in self._retained_messages.items():
            if self._topic_matches(topic_name, topic_pattern):
                if callback:
                    await callback(topic_name, message.to_dict())

    def unsubscribe(self, client_id: str, topic_pattern: str):
        """Unsubscribe from topic pattern"""
        with self._lock:
            if client_id in self._subscriptions:
                self._subscriptions[client_id].pop(topic_pattern, None)
                handler_key = f"{client_id}:{topic_pattern}"
                if handler_key in self._message_handlers:
                    del self._message_handlers[handler_key]

            self._stats['active_subscriptions'] = sum(
                len(subs) for subs in self._subscriptions.values()
            )

    async def _deliver_message(self, message: MQTTMessage):
        """Deliver message to matching subscribers"""
        delivery_count = 0

        for client_id, subscriptions in self._subscriptions.items():
            for topic_pattern, qos in subscriptions.items():
                if self._topic_matches(message.topic, topic_pattern):
                    # Call handlers
                    handler_key = f"{client_id}:{topic_pattern}"
                    handlers = self._message_handlers.get(handler_key, [])

                    for handler in handlers:
                        try:
                            await handler(message.topic, message.to_dict())
                            delivery_count += 1
                        except Exception as e:
                            print(f"Error in message handler: {e}")

        with self._lock:
            self._stats['messages_delivered'] += delivery_count

    def _topic_matches(self, topic: str, pattern: str) -> bool:
        """Check if topic matches pattern"""
        topic_obj = MQTTTopic(name=topic)
        return topic_obj.matches(pattern)

    def get_statistics(self) -> Dict[str, Any]:
        """Get broker statistics"""
        return {
            'topics': len(self._topics),
            'subscriptions': self._stats['active_subscriptions'],
            'messages_published': self._stats['messages_published'],
            'messages_delivered': self._stats['messages_delivered'],
            'retained_messages': len(self._retained_messages)
        }


# Singleton instance
_mqtt_broker: Optional[MQTTBroker] = None


def get_mqtt_broker() -> MQTTBroker:
    """Get singleton MQTT broker instance"""
    global _mqtt_broker
    if _mqtt_broker is None:
        _mqtt_broker = MQTTBroker()
    return _mqtt_broker


# ============================================================================
# Edge Computing Platform
# ============================================================================


@dataclass
class EdgeFunction:
    """Edge computing function"""
    function_id: str
    function_name: str
    code: str
    runtime: str = "python3.9"
    trigger: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    memory_mb: int = 128
    timeout_seconds: int = 30
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeNode:
    """Edge computing node"""
    node_id: str
    node_name: str
    status: str = "online"
    location: Optional[Location] = None
    cpu_cores: int = 4
    memory_mb: int = 4096
    disk_gb: int = 32
    functions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.now)

    def is_healthy(self) -> bool:
        """Check if node is healthy"""
        if self.status != "online":
            return False
        return (datetime.now() - self.last_heartbeat) < timedelta(minutes=2)


class EdgePlatform:
    """
    Edge Computing Platform

    Manages edge nodes and deploys functions for local processing.
    """

    def __init__(self):
        self._nodes: Dict[str, EdgeNode] = {}
        self._functions: Dict[str, EdgeFunction] = {}
        self._deployments: Dict[str, Set[str]] = defaultdict(set)
        self._cache: Dict[str, Any] = {}
        self._lock = Lock()

    def register_node(
        self,
        node_id: str,
        node_name: str,
        location: Optional[Location] = None,
        cpu_cores: int = 4,
        memory_mb: int = 4096,
        disk_gb: int = 32
    ) -> EdgeNode:
        """Register edge node"""
        with self._lock:
            if node_id in self._nodes:
                raise ValueError(f"Node {node_id} already registered")

            node = EdgeNode(
                node_id=node_id,
                node_name=node_name,
                location=location,
                cpu_cores=cpu_cores,
                memory_mb=memory_mb,
                disk_gb=disk_gb
            )
            self._nodes[node_id] = node
            return node

    def get_node(self, node_id: str) -> Optional[EdgeNode]:
        """Get edge node by ID"""
        return self._nodes.get(node_id)

    def list_nodes(self, status: Optional[str] = None) -> List[EdgeNode]:
        """List edge nodes"""
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        return nodes

    def deploy_function(
        self,
        function_name: str,
        code: str,
        node_id: str,
        trigger: Optional[str] = None,
        runtime: str = "python3.9",
        memory_mb: int = 128,
        timeout_seconds: int = 30
    ) -> EdgeFunction:
        """Deploy function to edge node"""
        node = self.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        function_id = str(uuid4())
        function = EdgeFunction(
            function_id=function_id,
            function_name=function_name,
            code=code,
            runtime=runtime,
            trigger=trigger,
            memory_mb=memory_mb,
            timeout_seconds=timeout_seconds
        )

        with self._lock:
            self._functions[function_id] = function
            self._deployments[node_id].add(function_id)
            node.functions.append(function_id)

        return function

    def execute_function(
        self,
        function_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute edge function"""
        function = self._functions.get(function_id)
        if not function:
            raise ValueError(f"Function {function_id} not found")

        try:
            # Create execution environment
            local_env = {'data': input_data}

            # Execute function code
            exec(function.code, {}, local_env)

            # Get result from 'process' function
            if 'process' in local_env:
                result = local_env['process'](input_data)
                return {
                    'success': True,
                    'result': result,
                    'function_id': function_id
                }
            else:
                return {
                    'success': False,
                    'error': 'No process() function found',
                    'function_id': function_id
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'function_id': function_id
            }

    def cache_set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in edge cache"""
        with self._lock:
            expiry = time.time() + ttl_seconds
            self._cache[key] = {'value': value, 'expiry': expiry}

    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from edge cache"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry['expiry']:
                    return entry['value']
                else:
                    del self._cache[key]
            return None

    def cache_delete(self, key: str):
        """Delete value from edge cache"""
        with self._lock:
            self._cache.pop(key, None)

    def update_node_metrics(
        self,
        node_id: str,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float
    ):
        """Update node metrics"""
        node = self.get_node(node_id)
        if node:
            node.metrics = {
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage,
                'disk_usage_percent': disk_usage,
                'timestamp': datetime.now().isoformat()
            }
            node.last_heartbeat = datetime.now()

    def get_statistics(self) -> Dict[str, Any]:
        """Get edge platform statistics"""
        total_nodes = len(self._nodes)
        healthy_nodes = sum(1 for n in self._nodes.values() if n.is_healthy())

        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'total_functions': len(self._functions),
            'total_deployments': sum(len(deps) for deps in self._deployments.values()),
            'cache_entries': len(self._cache)
        }


# Singleton instance
_edge_platform: Optional[EdgePlatform] = None


def get_edge_platform() -> EdgePlatform:
    """Get singleton edge platform instance"""
    global _edge_platform
    if _edge_platform is None:
        _edge_platform = EdgePlatform()
    return _edge_platform


# ============================================================================
# Telemetry Pipeline
# ============================================================================


@dataclass
class Telemetry:
    """Telemetry data point"""
    device_id: str
    metric_name: str
    value: Union[float, int, str, bool]
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    quality: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'device_id': self.device_id,
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'quality': self.quality,
            'metadata': self.metadata
        }


class TelemetryPipeline:
    """
    Telemetry Data Pipeline

    Ingests, stores, and queries time-series telemetry data.
    """

    def __init__(self):
        self._data: Dict[str, List[Telemetry]] = defaultdict(list)
        self._lock = Lock()
        self._stats = {
            'ingested': 0,
            'queries': 0
        }

    def ingest(self, telemetry: Telemetry):
        """Ingest telemetry data"""
        key = f"{telemetry.device_id}:{telemetry.metric_name}"

        with self._lock:
            self._data[key].append(telemetry)
            self._stats['ingested'] += 1

            # Keep only last 10,000 points per metric
            if len(self._data[key]) > 10000:
                self._data[key] = self._data[key][-10000:]

    def ingest_batch(self, telemetry_list: List[Telemetry]):
        """Ingest multiple telemetry points"""
        for telemetry in telemetry_list:
            self.ingest(telemetry)

    def query(
        self,
        device_id: str,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Telemetry]:
        """Query telemetry data"""
        key = f"{device_id}:{metric_name}"

        with self._lock:
            self._stats['queries'] += 1
            data = self._data.get(key, [])

        # Filter by time range
        if start_time:
            data = [t for t in data if t.timestamp >= start_time]
        if end_time:
            data = [t for t in data if t.timestamp <= end_time]

        # Apply limit
        data = data[-limit:]

        return data

    def query_latest(
        self,
        device_id: str,
        metric_name: str
    ) -> Optional[Telemetry]:
        """Query latest telemetry value"""
        key = f"{device_id}:{metric_name}"

        with self._lock:
            data = self._data.get(key, [])
            return data[-1] if data else None

    def aggregate(
        self,
        device_id: str,
        metric_name: str,
        aggregation: str = "avg",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[float]:
        """Aggregate telemetry data"""
        data = self.query(device_id, metric_name, start_time, end_time)

        if not data:
            return None

        # Extract numeric values
        values = []
        for t in data:
            if isinstance(t.value, (int, float)):
                values.append(float(t.value))

        if not values:
            return None

        # Compute aggregation
        if aggregation == "avg":
            return sum(values) / len(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "count":
            return float(len(values))
        else:
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get telemetry statistics"""
        total_metrics = len(self._data)
        total_points = sum(len(data) for data in self._data.values())

        return {
            'total_metrics': total_metrics,
            'total_data_points': total_points,
            'ingested': self._stats['ingested'],
            'queries': self._stats['queries']
        }


# Singleton instance
_telemetry_pipeline: Optional[TelemetryPipeline] = None


def get_telemetry_pipeline() -> TelemetryPipeline:
    """Get singleton telemetry pipeline instance"""
    global _telemetry_pipeline
    if _telemetry_pipeline is None:
        _telemetry_pipeline = TelemetryPipeline()
    return _telemetry_pipeline
