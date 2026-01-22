"""
Redis Pub/Sub for Collaborative Editing

Provides Redis-based message broker for scaling WebSocket servers.
Enables multiple server instances to share real-time updates.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional

import redis

logger = logging.getLogger("dms.collaboration.redis")


class RedisPubSubManager:
    """
    Redis Pub/Sub Manager for Collaborative Editing.

    Allows multiple WebSocket server instances to communicate
    and broadcast events across all connected clients.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", channel_prefix: str = "collab"):
        """
        Initialize Redis Pub/Sub manager.

        Args:
            redis_url: Redis connection URL
            channel_prefix: Prefix for all pub/sub channels
        """
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix

        # Redis clients
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

        # Event handlers
        self.handlers: Dict[str, Callable] = {}

        # Connection state
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to Redis server.

        Returns:
            bool: True if connection successful
        """
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            # Test connection
            self.redis_client.ping()

            # Create pub/sub client
            self.pubsub = self.redis_client.pubsub()

            self.connected = True
            logger.info(f"Connected to Redis at {self.redis_url}")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from Redis server."""
        try:
            if self.pubsub:
                self.pubsub.close()
                self.pubsub = None

            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None

            self.connected = False
            logger.info("Disconnected from Redis")

        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")

    def publish_event(self, document_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Publish event to Redis channel.

        Args:
            document_id: Document ID
            event_type: Event type (e.g., 'edit', 'cursor', 'join', 'leave')
            data: Event data

        Returns:
            bool: True if published successfully
        """
        if not self.connected or not self.redis_client:
            logger.warning("Not connected to Redis, cannot publish event")
            return False

        try:
            channel = self._get_channel(document_id)

            message = {
                "event_type": event_type,
                "data": data,
            }

            message_json = json.dumps(message)

            # Publish to channel
            self.redis_client.publish(channel, message_json)

            logger.debug(f"Published {event_type} to {channel}")

            return True

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    def subscribe_document(self, document_id: str, handler: Callable[[str, Dict[str, Any]], None]):
        """
        Subscribe to document events.

        Args:
            document_id: Document ID to subscribe to
            handler: Callback function to handle events
                     Signature: handler(event_type: str, data: dict)
        """
        if not self.connected or not self.pubsub:
            logger.warning("Not connected to Redis, cannot subscribe")
            return

        try:
            channel = self._get_channel(document_id)

            # Subscribe to channel
            self.pubsub.subscribe(channel)

            # Store handler
            self.handlers[channel] = handler

            logger.info(f"Subscribed to {channel}")

        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")

    def unsubscribe_document(self, document_id: str):
        """
        Unsubscribe from document events.

        Args:
            document_id: Document ID to unsubscribe from
        """
        if not self.pubsub:
            return

        try:
            channel = self._get_channel(document_id)

            # Unsubscribe from channel
            self.pubsub.unsubscribe(channel)

            # Remove handler
            if channel in self.handlers:
                del self.handlers[channel]

            logger.info(f"Unsubscribed from {channel}")

        except Exception as e:
            logger.error(f"Error unsubscribing from channel: {e}")

    def listen(self, timeout: int = 1):
        """
        Listen for messages on subscribed channels.

        This should be called in a background thread/task.

        Args:
            timeout: Timeout in seconds for receiving messages
        """
        if not self.connected or not self.pubsub:
            logger.warning("Not connected to Redis, cannot listen")
            return

        try:
            # Listen for messages
            message = self.pubsub.get_message(timeout=timeout)

            if message and message["type"] == "message":
                channel = message["channel"]
                data_json = message["data"]

                try:
                    data = json.loads(data_json)
                    event_type = data.get("event_type")
                    event_data = data.get("data")

                    # Call handler
                    if channel in self.handlers:
                        self.handlers[channel](event_type, event_data)

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")

        except Exception as e:
            logger.error(f"Error listening for messages: {e}")

    def _get_channel(self, document_id: str) -> str:
        """
        Get Redis channel name for document.

        Args:
            document_id: Document ID

        Returns:
            str: Channel name
        """
        return f"{self.channel_prefix}:document:{document_id}"

    def set_document_lock(self, document_id: str, user_id: int, ttl: int = 30) -> bool:
        """
        Set a lock on document for a user (for exclusive editing).

        Args:
            document_id: Document ID
            user_id: User ID
            ttl: Time-to-live in seconds

        Returns:
            bool: True if lock acquired
        """
        if not self.connected or not self.redis_client:
            return False

        try:
            lock_key = f"{self.channel_prefix}:lock:{document_id}"

            # Try to set lock (NX = only if not exists)
            result = self.redis_client.set(lock_key, user_id, nx=True, ex=ttl)

            return bool(result)

        except Exception as e:
            logger.error(f"Error setting document lock: {e}")
            return False

    def release_document_lock(self, document_id: str, user_id: int) -> bool:
        """
        Release lock on document.

        Args:
            document_id: Document ID
            user_id: User ID

        Returns:
            bool: True if lock released
        """
        if not self.connected or not self.redis_client:
            return False

        try:
            lock_key = f"{self.channel_prefix}:lock:{document_id}"

            # Check if user owns the lock
            current_lock = self.redis_client.get(lock_key)

            if current_lock and int(current_lock) == user_id:
                self.redis_client.delete(lock_key)
                return True

            return False

        except Exception as e:
            logger.error(f"Error releasing document lock: {e}")
            return False

    def get_document_lock_owner(self, document_id: str) -> Optional[int]:
        """
        Get the owner of the document lock.

        Args:
            document_id: Document ID

        Returns:
            Optional[int]: User ID of lock owner, or None if no lock
        """
        if not self.connected or not self.redis_client:
            return None

        try:
            lock_key = f"{self.channel_prefix}:lock:{document_id}"
            lock_owner = self.redis_client.get(lock_key)

            return int(lock_owner) if lock_owner else None

        except Exception as e:
            logger.error(f"Error getting document lock owner: {e}")
            return None

    def cache_document_state(self, document_id: str, state: Dict[str, Any], ttl: int = 3600):
        """
        Cache document state in Redis.

        Args:
            document_id: Document ID
            state: Document state to cache
            ttl: Time-to-live in seconds
        """
        if not self.connected or not self.redis_client:
            return

        try:
            cache_key = f"{self.channel_prefix}:cache:{document_id}"
            state_json = json.dumps(state)

            self.redis_client.setex(cache_key, ttl, state_json)

        except Exception as e:
            logger.error(f"Error caching document state: {e}")

    def get_cached_document_state(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached document state from Redis.

        Args:
            document_id: Document ID

        Returns:
            Optional[Dict]: Document state, or None if not cached
        """
        if not self.connected or not self.redis_client:
            return None

        try:
            cache_key = f"{self.channel_prefix}:cache:{document_id}"
            state_json = self.redis_client.get(cache_key)

            if state_json:
                return json.loads(state_json)

            return None

        except Exception as e:
            logger.error(f"Error getting cached document state: {e}")
            return None

    def clear_document_cache(self, document_id: str):
        """
        Clear cached document state.

        Args:
            document_id: Document ID
        """
        if not self.connected or not self.redis_client:
            return

        try:
            cache_key = f"{self.channel_prefix}:cache:{document_id}"
            self.redis_client.delete(cache_key)

        except Exception as e:
            logger.error(f"Error clearing document cache: {e}")


# Global instance
_redis_pubsub: Optional[RedisPubSubManager] = None


def get_redis_pubsub(redis_url: str = "redis://localhost:6379/0") -> RedisPubSubManager:
    """
    Get global Redis Pub/Sub manager instance.

    Args:
        redis_url: Redis connection URL

    Returns:
        RedisPubSubManager: Redis Pub/Sub manager instance
    """
    global _redis_pubsub

    if _redis_pubsub is None:
        _redis_pubsub = RedisPubSubManager(redis_url)
        _redis_pubsub.connect()

    return _redis_pubsub


def configure_redis_pubsub(redis_url: str = "redis://localhost:6379/0"):
    """
    Configure Redis Pub/Sub manager.

    Args:
        redis_url: Redis connection URL
    """
    global _redis_pubsub

    _redis_pubsub = RedisPubSubManager(redis_url)
    _redis_pubsub.connect()


logger.info("Redis Pub/Sub manager loaded")
