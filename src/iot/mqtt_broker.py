"""
MQTT Broker & Messaging

MQTT 3.1.1/5.0 broker implementation with pub/sub, QoS, retained messages,
topic routing, and session persistence.

Part of v3.6 IoT & Edge Computing implementation.
"""

import asyncio
import hashlib
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class QoSLevel(Enum):
    """MQTT Quality of Service levels."""
    AT_MOST_ONCE = 0  # Fire and forget
    AT_LEAST_ONCE = 1  # Acknowledged delivery
    EXACTLY_ONCE = 2  # Assured delivery


class MessageType(Enum):
    """MQTT message types."""
    CONNECT = "connect"
    CONNACK = "connack"
    PUBLISH = "publish"
    PUBACK = "puback"
    SUBSCRIBE = "subscribe"
    SUBACK = "suback"
    UNSUBSCRIBE = "unsubscribe"
    UNSUBACK = "unsuback"
    PINGREQ = "pingreq"
    PINGRESP = "pingresp"
    DISCONNECT = "disconnect"


@dataclass
class MQTTMessage:
    """MQTT message structure."""
    topic: str
    payload: Any
    qos: QoSLevel = QoSLevel.AT_MOST_ONCE
    retain: bool = False
    message_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duplicate: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid4())


@dataclass
class Subscription:
    """Client subscription to topic."""
    client_id: str
    topic: str
    qos: QoSLevel
    callback: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ClientSession:
    """MQTT client session."""
    client_id: str
    clean_session: bool
    connected: bool = True
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    subscriptions: Dict[str, Subscription] = field(default_factory=dict)
    pending_messages: List[MQTTMessage] = field(default_factory=list)
    will_message: Optional[MQTTMessage] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TopicMatcher:
    """Match MQTT topics with wildcards."""

    @staticmethod
    def match(topic_filter: str, topic: str) -> bool:
        """
        Match topic against filter with wildcards.
        + = single level wildcard
        # = multi-level wildcard
        """
        # Split into levels
        filter_levels = topic_filter.split('/')
        topic_levels = topic.split('/')

        # # must be last and alone
        if '#' in filter_levels[:-1]:
            return False

        if '#' in filter_levels[-1] and filter_levels[-1] != '#':
            return False

        # Match levels
        for i, filter_level in enumerate(filter_levels):
            # Multi-level wildcard matches rest
            if filter_level == '#':
                return True

            # Need more topic levels
            if i >= len(topic_levels):
                return False

            # Single level wildcard
            if filter_level == '+':
                continue

            # Exact match required
            if filter_level != topic_levels[i]:
                return False

        # All levels matched, check same length
        return len(filter_levels) == len(topic_levels)

    @staticmethod
    def validate_topic(topic: str, is_filter: bool = False) -> bool:
        """Validate topic format."""
        if not topic:
            return False

        # Topic cannot start with $
        if topic.startswith('$'):
            return False

        # Check wildcards
        if not is_filter:
            if '+' in topic or '#' in topic:
                return False

        return True


class RetainedMessages:
    """Storage for retained messages."""

    def __init__(self):
        self.messages: Dict[str, MQTTMessage] = {}

    def store(self, message: MQTTMessage):
        """Store retained message."""
        if message.retain:
            if message.payload:  # Empty payload removes retained message
                self.messages[message.topic] = message
                logger.debug(f"Retained message on topic {message.topic}")
            else:
                self.messages.pop(message.topic, None)
                logger.debug(f"Removed retained message on topic {message.topic}")

    def get_matching(self, topic_filter: str) -> List[MQTTMessage]:
        """Get retained messages matching topic filter."""
        matching = []

        for topic, message in self.messages.items():
            if TopicMatcher.match(topic_filter, topic):
                matching.append(message)

        return matching

    def clear(self, topic: Optional[str] = None):
        """Clear retained messages."""
        if topic:
            self.messages.pop(topic, None)
        else:
            self.messages.clear()


class QoSHandler:
    """Handle QoS message acknowledgments."""

    def __init__(self):
        self.pending_acks: Dict[str, MQTTMessage] = {}
        self.acknowledged: Set[str] = set()

    async def send_with_qos(
        self,
        message: MQTTMessage,
        send_func: Callable
    ) -> bool:
        """Send message with QoS handling."""
        if message.qos == QoSLevel.AT_MOST_ONCE:
            # QoS 0 - just send
            await send_func(message)
            return True

        elif message.qos == QoSLevel.AT_LEAST_ONCE:
            # QoS 1 - wait for PUBACK
            self.pending_acks[message.message_id] = message
            await send_func(message)

            # Wait for acknowledgment (with timeout)
            try:
                await asyncio.wait_for(
                    self._wait_for_ack(message.message_id),
                    timeout=5.0
                )
                return True
            except asyncio.TimeoutError:
                logger.warning(f"QoS 1 timeout for message {message.message_id}")
                return False

        elif message.qos == QoSLevel.EXACTLY_ONCE:
            # QoS 2 - two-phase commit
            # Simplified implementation
            self.pending_acks[message.message_id] = message
            await send_func(message)

            try:
                await asyncio.wait_for(
                    self._wait_for_ack(message.message_id),
                    timeout=10.0
                )
                return True
            except asyncio.TimeoutError:
                logger.warning(f"QoS 2 timeout for message {message.message_id}")
                return False

    async def _wait_for_ack(self, message_id: str):
        """Wait for message acknowledgment."""
        while message_id not in self.acknowledged:
            await asyncio.sleep(0.1)

    def acknowledge(self, message_id: str):
        """Acknowledge message receipt."""
        self.acknowledged.add(message_id)
        self.pending_acks.pop(message_id, None)
        logger.debug(f"Message {message_id} acknowledged")


class Topic:
    """MQTT topic management."""

    def __init__(self, name: str):
        self.name = name
        self.subscriptions: List[Subscription] = []
        self.message_count: int = 0
        self.last_message: Optional[datetime] = None

    def add_subscription(self, subscription: Subscription):
        """Add subscription to topic."""
        self.subscriptions.append(subscription)

    def remove_subscription(self, client_id: str):
        """Remove client subscription."""
        self.subscriptions = [
            sub for sub in self.subscriptions
            if sub.client_id != client_id
        ]

    def get_subscribers(self) -> List[Subscription]:
        """Get all subscribers."""
        return self.subscriptions

    def record_message(self):
        """Record message published to topic."""
        self.message_count += 1
        self.last_message = datetime.now()


class MQTTBroker:
    """MQTT broker implementation."""

    def __init__(self):
        self.clients: Dict[str, ClientSession] = {}
        self.topics: Dict[str, Topic] = {}
        self.retained = RetainedMessages()
        self.qos_handler = QoSHandler()
        self.message_queue: asyncio.Queue = asyncio.Queue()

        # Statistics
        self.stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'active_clients': 0,
            'total_subscriptions': 0
        }

    async def connect(
        self,
        client_id: str,
        clean_session: bool = True,
        will_message: Optional[MQTTMessage] = None,
        **kwargs
    ) -> bool:
        """Handle client connection."""
        # Check if client already connected
        if client_id in self.clients:
            existing = self.clients[client_id]
            if existing.connected:
                logger.warning(f"Client {client_id} already connected, disconnecting old session")
                await self.disconnect(client_id)

        # Create session
        session = ClientSession(
            client_id=client_id,
            clean_session=clean_session,
            will_message=will_message,
            metadata=kwargs
        )

        self.clients[client_id] = session
        self.stats['active_clients'] = len([c for c in self.clients.values() if c.connected])

        logger.info(f"Client {client_id} connected (clean_session={clean_session})")
        return True

    async def disconnect(self, client_id: str, send_will: bool = False):
        """Handle client disconnection."""
        session = self.clients.get(client_id)
        if not session:
            return

        # Send Last Will and Testament if requested
        if send_will and session.will_message:
            await self.publish(
                topic=session.will_message.topic,
                payload=session.will_message.payload,
                qos=session.will_message.qos,
                retain=session.will_message.retain,
                client_id=client_id
            )

        # Clean session
        if session.clean_session:
            # Remove subscriptions
            for topic_name in list(session.subscriptions.keys()):
                await self.unsubscribe(client_id, topic_name)

            # Remove session
            del self.clients[client_id]
        else:
            # Keep session but mark disconnected
            session.connected = False

        self.stats['active_clients'] = len([c for c in self.clients.values() if c.connected])

        logger.info(f"Client {client_id} disconnected")

    async def publish(
        self,
        topic: str,
        payload: Any,
        qos: int = 0,
        retain: bool = False,
        client_id: Optional[str] = None
    ) -> bool:
        """Publish message to topic."""
        # Validate topic
        if not TopicMatcher.validate_topic(topic):
            logger.error(f"Invalid topic: {topic}")
            return False

        # Create message
        message = MQTTMessage(
            topic=topic,
            payload=payload,
            qos=QoSLevel(qos),
            retain=retain
        )

        # Store retained message
        if retain:
            self.retained.store(message)

        # Get or create topic
        if topic not in self.topics:
            self.topics[topic] = Topic(topic)

        topic_obj = self.topics[topic]
        topic_obj.record_message()

        # Route to subscribers
        await self._route_message(message)

        # Update statistics
        self.stats['messages_published'] += 1

        logger.debug(f"Published to {topic} (QoS {qos}, retain={retain})")
        return True

    async def _route_message(self, message: MQTTMessage):
        """Route message to matching subscribers."""
        delivered = 0

        for client_id, session in self.clients.items():
            if not session.connected:
                continue

            for sub_topic, subscription in session.subscriptions.items():
                if TopicMatcher.match(sub_topic, message.topic):
                    # Deliver message to subscriber
                    await self._deliver_message(session, message, subscription)
                    delivered += 1

        self.stats['messages_delivered'] += delivered
        logger.debug(f"Message delivered to {delivered} subscribers")

    async def _deliver_message(
        self,
        session: ClientSession,
        message: MQTTMessage,
        subscription: Subscription
    ):
        """Deliver message to specific subscriber."""
        # Adjust QoS to subscription level
        delivery_qos = min(message.qos, subscription.qos)

        # Call subscription callback
        if subscription.callback:
            try:
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(message.topic, message.payload)
                else:
                    subscription.callback(message.topic, message.payload)
            except Exception as e:
                logger.error(f"Subscription callback error: {e}")

        # Queue message if client offline
        if not session.connected:
            session.pending_messages.append(message)

        session.last_activity = datetime.now()

    async def subscribe(
        self,
        client_id: str,
        topic: str,
        qos: int = 0,
        callback: Optional[Callable] = None
    ) -> bool:
        """Subscribe client to topic."""
        # Validate topic filter
        if not TopicMatcher.validate_topic(topic, is_filter=True):
            logger.error(f"Invalid topic filter: {topic}")
            return False

        session = self.clients.get(client_id)
        if not session:
            logger.error(f"Client {client_id} not connected")
            return False

        # Create subscription
        subscription = Subscription(
            client_id=client_id,
            topic=topic,
            qos=QoSLevel(qos),
            callback=callback
        )

        # Add to session
        session.subscriptions[topic] = subscription

        # Send retained messages
        retained_messages = self.retained.get_matching(topic)
        for msg in retained_messages:
            await self._deliver_message(session, msg, subscription)

        self.stats['total_subscriptions'] = sum(
            len(s.subscriptions) for s in self.clients.values()
        )

        logger.info(f"Client {client_id} subscribed to {topic} (QoS {qos})")
        return True

    async def unsubscribe(self, client_id: str, topic: str) -> bool:
        """Unsubscribe client from topic."""
        session = self.clients.get(client_id)
        if not session:
            return False

        # Remove subscription
        if topic in session.subscriptions:
            del session.subscriptions[topic]

            self.stats['total_subscriptions'] = sum(
                len(s.subscriptions) for s in self.clients.values()
            )

            logger.info(f"Client {client_id} unsubscribed from {topic}")
            return True

        return False

    async def ping(self, client_id: str):
        """Handle client ping (keep-alive)."""
        session = self.clients.get(client_id)
        if session:
            session.last_activity = datetime.now()

    async def deliver_pending_messages(self, client_id: str):
        """Deliver pending messages to reconnected client."""
        session = self.clients.get(client_id)
        if not session:
            return

        pending = session.pending_messages[:]
        session.pending_messages.clear()

        for message in pending:
            # Find matching subscription
            for topic_filter, subscription in session.subscriptions.items():
                if TopicMatcher.match(topic_filter, message.topic):
                    await self._deliver_message(session, message, subscription)

        logger.info(f"Delivered {len(pending)} pending messages to {client_id}")

    def get_client(self, client_id: str) -> Optional[ClientSession]:
        """Get client session."""
        return self.clients.get(client_id)

    def list_clients(self, connected_only: bool = True) -> List[ClientSession]:
        """List client sessions."""
        clients = list(self.clients.values())

        if connected_only:
            clients = [c for c in clients if c.connected]

        return clients

    def get_topic_stats(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get statistics for topic."""
        topic_obj = self.topics.get(topic)
        if not topic_obj:
            return None

        return {
            'name': topic_obj.name,
            'subscribers': len(topic_obj.subscriptions),
            'message_count': topic_obj.message_count,
            'last_message': topic_obj.last_message
        }

    def get_broker_stats(self) -> Dict[str, Any]:
        """Get broker statistics."""
        return {
            **self.stats,
            'total_clients': len(self.clients),
            'total_topics': len(self.topics),
            'retained_messages': len(self.retained.messages)
        }

    async def cleanup_inactive_clients(self, timeout_seconds: int = 3600):
        """Clean up inactive client sessions."""
        now = datetime.now()
        inactive = []

        for client_id, session in self.clients.items():
            if not session.connected:
                continue

            inactive_time = (now - session.last_activity).total_seconds()
            if inactive_time > timeout_seconds:
                inactive.append(client_id)

        for client_id in inactive:
            logger.info(f"Cleaning up inactive client {client_id}")
            await self.disconnect(client_id, send_will=True)

        return len(inactive)


class MQTTClient:
    """MQTT client for publishing/subscribing."""

    def __init__(self, client_id: str, broker: MQTTBroker):
        self.client_id = client_id
        self.broker = broker
        self.connected = False

    async def connect(
        self,
        clean_session: bool = True,
        will_topic: Optional[str] = None,
        will_payload: Optional[Any] = None,
        will_qos: int = 0
    ) -> bool:
        """Connect to broker."""
        will_message = None
        if will_topic and will_payload:
            will_message = MQTTMessage(
                topic=will_topic,
                payload=will_payload,
                qos=QoSLevel(will_qos)
            )

        self.connected = await self.broker.connect(
            client_id=self.client_id,
            clean_session=clean_session,
            will_message=will_message
        )

        return self.connected

    async def disconnect(self):
        """Disconnect from broker."""
        await self.broker.disconnect(self.client_id)
        self.connected = False

    async def publish(
        self,
        topic: str,
        payload: Any,
        qos: int = 0,
        retain: bool = False
    ) -> bool:
        """Publish message."""
        if not self.connected:
            logger.error(f"Client {self.client_id} not connected")
            return False

        return await self.broker.publish(
            topic=topic,
            payload=payload,
            qos=qos,
            retain=retain,
            client_id=self.client_id
        )

    async def subscribe(
        self,
        topic: str,
        qos: int = 0,
        callback: Optional[Callable] = None
    ) -> bool:
        """Subscribe to topic."""
        if not self.connected:
            logger.error(f"Client {self.client_id} not connected")
            return False

        return await self.broker.subscribe(
            client_id=self.client_id,
            topic=topic,
            qos=qos,
            callback=callback
        )

    async def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from topic."""
        if not self.connected:
            return False

        return await self.broker.unsubscribe(self.client_id, topic)


# Singleton broker instance
_mqtt_broker: Optional[MQTTBroker] = None


def get_mqtt_broker() -> MQTTBroker:
    """Get or create MQTT broker."""
    global _mqtt_broker

    if _mqtt_broker is None:
        _mqtt_broker = MQTTBroker()

    return _mqtt_broker


def create_mqtt_client(client_id: str) -> MQTTClient:
    """Create MQTT client."""
    broker = get_mqtt_broker()
    return MQTTClient(client_id, broker)
