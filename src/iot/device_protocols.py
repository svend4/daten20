"""
Device Protocols

Multi-protocol support for IoT devices including MQTT, CoAP, HTTP, Modbus,
and WebSocket with protocol translation and connection management.

Part of v3.6 IoT & Edge Computing implementation.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ProtocolType(Enum):
    """Supported protocol types."""
    MQTT = "mqtt"
    COAP = "coap"
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    MODBUS_TCP = "modbus_tcp"
    MODBUS_RTU = "modbus_rtu"


class MessageFormat(Enum):
    """Message serialization formats."""
    JSON = "json"
    CBOR = "cbor"
    PROTOBUF = "protobuf"
    XML = "xml"
    PLAIN_TEXT = "text"


@dataclass
class ProtocolMessage:
    """Generic protocol message."""
    protocol: ProtocolType
    endpoint: str  # topic, URL, register address, etc.
    payload: Any
    format: MessageFormat = MessageFormat.JSON
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConnectionConfig:
    """Protocol connection configuration."""
    protocol: ProtocolType
    host: str
    port: int
    use_tls: bool = False
    timeout: int = 30
    keepalive: int = 60
    auto_reconnect: bool = True
    credentials: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Connection:
    """Active protocol connection."""
    connection_id: str
    config: ConnectionConfig
    connected: bool = False
    connected_at: Optional[datetime] = None
    last_activity: datetime = field(default_factory=datetime.now)
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0


class BaseProtocol(ABC):
    """Base class for protocol implementations."""

    def __init__(self, connection_config: ConnectionConfig):
        self.config = connection_config
        self.connected = False
        self.callbacks: Dict[str, List[Callable]] = {}

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to endpoint."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from endpoint."""
        pass

    @abstractmethod
    async def send(self, message: ProtocolMessage) -> bool:
        """Send message."""
        pass

    @abstractmethod
    async def receive(self) -> Optional[ProtocolMessage]:
        """Receive message."""
        pass

    def register_callback(self, event: str, callback: Callable):
        """Register event callback."""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    async def _trigger_callback(self, event: str, *args, **kwargs):
        """Trigger registered callbacks."""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Callback error: {e}")


class MQTTProtocol(BaseProtocol):
    """MQTT protocol implementation."""

    async def connect(self) -> bool:
        """Connect to MQTT broker."""
        logger.info(f"Connecting to MQTT broker at {self.config.host}:{self.config.port}")

        # Mock connection
        await asyncio.sleep(0.1)

        self.connected = True
        await self._trigger_callback('connected')

        return True

    async def disconnect(self):
        """Disconnect from MQTT broker."""
        self.connected = False
        await self._trigger_callback('disconnected')
        logger.info("Disconnected from MQTT broker")

    async def send(self, message: ProtocolMessage) -> bool:
        """Publish MQTT message."""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return False

        logger.debug(f"Publishing to {message.endpoint}: {message.payload}")
        await asyncio.sleep(0.01)  # Simulate network delay

        return True

    async def receive(self) -> Optional[ProtocolMessage]:
        """Receive MQTT message (mock)."""
        if not self.connected:
            return None

        # Mock receive
        await asyncio.sleep(0.1)

        return None

    async def subscribe(self, topic: str, qos: int = 0):
        """Subscribe to MQTT topic."""
        if not self.connected:
            return False

        logger.info(f"Subscribed to topic: {topic} (QoS {qos})")
        return True


class CoAPProtocol(BaseProtocol):
    """CoAP (Constrained Application Protocol) implementation."""

    async def connect(self) -> bool:
        """Connect to CoAP server."""
        logger.info(f"Connecting to CoAP server at {self.config.host}:{self.config.port}")

        # Mock connection
        await asyncio.sleep(0.1)

        self.connected = True
        return True

    async def disconnect(self):
        """Disconnect from CoAP server."""
        self.connected = False
        logger.info("Disconnected from CoAP server")

    async def send(self, message: ProtocolMessage) -> bool:
        """Send CoAP request."""
        if not self.connected:
            return False

        logger.debug(f"CoAP request to {message.endpoint}")
        await asyncio.sleep(0.01)

        return True

    async def receive(self) -> Optional[ProtocolMessage]:
        """Receive CoAP response."""
        if not self.connected:
            return None

        # Mock receive
        await asyncio.sleep(0.1)

        return None

    async def get(self, path: str) -> Optional[Any]:
        """CoAP GET request."""
        message = ProtocolMessage(
            protocol=ProtocolType.COAP,
            endpoint=path,
            payload=None,
            metadata={'method': 'GET'}
        )

        if await self.send(message):
            return await self.receive()

        return None

    async def post(self, path: str, payload: Any) -> bool:
        """CoAP POST request."""
        message = ProtocolMessage(
            protocol=ProtocolType.COAP,
            endpoint=path,
            payload=payload,
            metadata={'method': 'POST'}
        )

        return await self.send(message)


class HTTPProtocol(BaseProtocol):
    """HTTP/HTTPS protocol implementation."""

    async def connect(self) -> bool:
        """Connect to HTTP server (establish session)."""
        logger.info(f"Connecting to HTTP server at {self.config.host}:{self.config.port}")

        self.connected = True
        return True

    async def disconnect(self):
        """Close HTTP session."""
        self.connected = False
        logger.info("HTTP session closed")

    async def send(self, message: ProtocolMessage) -> bool:
        """Send HTTP request."""
        if not self.connected:
            return False

        method = message.metadata.get('method', 'POST')
        logger.debug(f"HTTP {method} to {message.endpoint}")

        # Mock HTTP request
        await asyncio.sleep(0.05)

        return True

    async def receive(self) -> Optional[ProtocolMessage]:
        """Receive HTTP response."""
        # Mock response
        await asyncio.sleep(0.05)

        return None

    async def get(self, path: str) -> Optional[Any]:
        """HTTP GET request."""
        message = ProtocolMessage(
            protocol=ProtocolType.HTTP,
            endpoint=path,
            payload=None,
            metadata={'method': 'GET'}
        )

        if await self.send(message):
            response = await self.receive()
            return response.payload if response else None

        return None

    async def post(self, path: str, payload: Any) -> Optional[Any]:
        """HTTP POST request."""
        message = ProtocolMessage(
            protocol=ProtocolType.HTTP,
            endpoint=path,
            payload=payload,
            metadata={'method': 'POST'}
        )

        if await self.send(message):
            response = await self.receive()
            return response.payload if response else None

        return None


class ModbusProtocol(BaseProtocol):
    """Modbus TCP/RTU protocol implementation."""

    async def connect(self) -> bool:
        """Connect to Modbus device."""
        logger.info(f"Connecting to Modbus device at {self.config.host}:{self.config.port}")

        # Mock connection
        await asyncio.sleep(0.1)

        self.connected = True
        return True

    async def disconnect(self):
        """Disconnect from Modbus device."""
        self.connected = False
        logger.info("Disconnected from Modbus device")

    async def send(self, message: ProtocolMessage) -> bool:
        """Send Modbus request."""
        if not self.connected:
            return False

        logger.debug(f"Modbus write to register {message.endpoint}")
        await asyncio.sleep(0.01)

        return True

    async def receive(self) -> Optional[ProtocolMessage]:
        """Receive Modbus response."""
        if not self.connected:
            return None

        # Mock receive
        await asyncio.sleep(0.01)

        return None

    async def read_holding_registers(
        self,
        address: int,
        count: int = 1
    ) -> Optional[List[int]]:
        """Read holding registers."""
        if not self.connected:
            return None

        logger.debug(f"Reading {count} registers from address {address}")

        # Mock read
        await asyncio.sleep(0.01)
        return [0] * count

    async def write_single_register(
        self,
        address: int,
        value: int
    ) -> bool:
        """Write single register."""
        if not self.connected:
            return False

        logger.debug(f"Writing {value} to register {address}")

        # Mock write
        await asyncio.sleep(0.01)
        return True


class ProtocolAdapter:
    """Translate between different protocols."""

    def translate(
        self,
        message: ProtocolMessage,
        target_protocol: ProtocolType
    ) -> ProtocolMessage:
        """Translate message to target protocol."""
        if message.protocol == target_protocol:
            return message

        # MQTT to HTTP translation
        if message.protocol == ProtocolType.MQTT and target_protocol == ProtocolType.HTTP:
            return ProtocolMessage(
                protocol=ProtocolType.HTTP,
                endpoint=f"/mqtt/{message.endpoint}",
                payload=message.payload,
                format=message.format,
                metadata={'original_topic': message.endpoint}
            )

        # HTTP to MQTT translation
        if message.protocol == ProtocolType.HTTP and target_protocol == ProtocolType.MQTT:
            topic = message.metadata.get('original_topic', 'devices/data')
            return ProtocolMessage(
                protocol=ProtocolType.MQTT,
                endpoint=topic,
                payload=message.payload,
                format=message.format
            )

        # Generic translation
        return ProtocolMessage(
            protocol=target_protocol,
            endpoint=message.endpoint,
            payload=message.payload,
            format=message.format,
            metadata={**message.metadata, 'translated_from': message.protocol.value}
        )


class MessageSerializer:
    """Serialize/deserialize messages in different formats."""

    @staticmethod
    def serialize(payload: Any, format: MessageFormat) -> bytes:
        """Serialize payload to bytes."""
        if format == MessageFormat.JSON:
            return json.dumps(payload).encode('utf-8')

        elif format == MessageFormat.PLAIN_TEXT:
            return str(payload).encode('utf-8')

        elif format == MessageFormat.CBOR:
            # Mock CBOR encoding
            return json.dumps(payload).encode('utf-8')

        elif format == MessageFormat.PROTOBUF:
            # Mock Protobuf encoding
            return json.dumps(payload).encode('utf-8')

        else:
            return str(payload).encode('utf-8')

    @staticmethod
    def deserialize(data: bytes, format: MessageFormat) -> Any:
        """Deserialize bytes to payload."""
        if format == MessageFormat.JSON:
            return json.loads(data.decode('utf-8'))

        elif format == MessageFormat.PLAIN_TEXT:
            return data.decode('utf-8')

        elif format == MessageFormat.CBOR:
            # Mock CBOR decoding
            return json.loads(data.decode('utf-8'))

        elif format == MessageFormat.PROTOBUF:
            # Mock Protobuf decoding
            return json.loads(data.decode('utf-8'))

        else:
            return data.decode('utf-8')


class ConnectionPool:
    """Manage pool of protocol connections."""

    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.connections: Dict[str, Connection] = {}
        self.protocols: Dict[str, BaseProtocol] = {}

    async def get_connection(
        self,
        connection_id: str,
        config: ConnectionConfig
    ) -> Optional[BaseProtocol]:
        """Get or create connection."""
        # Check existing connection
        if connection_id in self.protocols:
            protocol = self.protocols[connection_id]
            if protocol.connected:
                return protocol

        # Check pool capacity
        if len(self.connections) >= self.max_connections:
            logger.warning("Connection pool at capacity")
            return None

        # Create new protocol
        protocol = self._create_protocol(config)

        # Connect
        if await protocol.connect():
            connection = Connection(
                connection_id=connection_id,
                config=config,
                connected=True,
                connected_at=datetime.now()
            )

            self.connections[connection_id] = connection
            self.protocols[connection_id] = protocol

            return protocol

        return None

    def _create_protocol(self, config: ConnectionConfig) -> BaseProtocol:
        """Create protocol instance."""
        if config.protocol == ProtocolType.MQTT:
            return MQTTProtocol(config)
        elif config.protocol == ProtocolType.COAP:
            return CoAPProtocol(config)
        elif config.protocol in [ProtocolType.HTTP, ProtocolType.HTTPS]:
            return HTTPProtocol(config)
        elif config.protocol in [ProtocolType.MODBUS_TCP, ProtocolType.MODBUS_RTU]:
            return ModbusProtocol(config)
        else:
            raise ValueError(f"Unsupported protocol: {config.protocol}")

    async def release_connection(self, connection_id: str):
        """Release connection."""
        if connection_id in self.protocols:
            protocol = self.protocols[connection_id]
            await protocol.disconnect()

            del self.protocols[connection_id]
            del self.connections[connection_id]

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            'active_connections': len(self.connections),
            'max_connections': self.max_connections,
            'by_protocol': self._count_by_protocol()
        }

    def _count_by_protocol(self) -> Dict[str, int]:
        """Count connections by protocol type."""
        counts = {}
        for conn in self.connections.values():
            protocol = conn.config.protocol.value
            counts[protocol] = counts.get(protocol, 0) + 1
        return counts


class DeviceConnector:
    """High-level device connection manager."""

    def __init__(self):
        self.connection_pool = ConnectionPool()
        self.adapter = ProtocolAdapter()
        self.serializer = MessageSerializer()

    async def connect_device(
        self,
        device_id: str,
        protocol: str,
        host: str,
        port: int,
        **kwargs
    ) -> bool:
        """Connect to device."""
        config = ConnectionConfig(
            protocol=ProtocolType(protocol),
            host=host,
            port=port,
            **kwargs
        )

        protocol_instance = await self.connection_pool.get_connection(device_id, config)

        return protocol_instance is not None

    async def disconnect_device(self, device_id: str):
        """Disconnect device."""
        await self.connection_pool.release_connection(device_id)

    async def send_message(
        self,
        device_id: str,
        endpoint: str,
        payload: Any,
        protocol: Optional[str] = None
    ) -> bool:
        """Send message to device."""
        protocol_instance = self.connection_pool.protocols.get(device_id)

        if not protocol_instance:
            logger.error(f"Device {device_id} not connected")
            return False

        # Create message
        message = ProtocolMessage(
            protocol=protocol_instance.config.protocol,
            endpoint=endpoint,
            payload=payload
        )

        # Send
        return await protocol_instance.send(message)

    async def receive_message(self, device_id: str) -> Optional[ProtocolMessage]:
        """Receive message from device."""
        protocol_instance = self.connection_pool.protocols.get(device_id)

        if not protocol_instance:
            return None

        return await protocol_instance.receive()

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return self.connection_pool.get_stats()


# Singleton instance
_device_connector: Optional[DeviceConnector] = None


def get_device_connector() -> DeviceConnector:
    """Get or create device connector."""
    global _device_connector

    if _device_connector is None:
        _device_connector = DeviceConnector()

    return _device_connector
