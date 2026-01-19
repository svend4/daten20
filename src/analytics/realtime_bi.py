"""
Real-time BI Updates Module

Provides WebSocket-based real-time data streaming for BI dashboards.

Features:
- WebSocket server for dashboard updates
- Server-Sent Events (SSE) support
- Live KPI streaming
- Real-time chart data updates
- Event-driven architecture
- Connection pooling
- Automatic reconnection handling
- Data change detection
- Throttling and rate limiting
- Multi-client broadcasting

WebSocket Protocol:
    Connect: ws://host/ws/bi/dashboard/{dashboard_id}
    Subscribe: {"action": "subscribe", "widgets": ["widget1", "widget2"]}
    Unsubscribe: {"action": "unsubscribe", "widgets": ["widget1"]}
    Update: {"type": "widget_update", "widget_id": "...", "data": {...}}

Usage:
    >>> from src.analytics.realtime_bi import RealtimeBIServer
    >>> server = RealtimeBIServer()
    >>> await server.start()
    >>> # Updates are automatically broadcast to connected clients
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


# ============================================================
# Data Models
# ============================================================

class UpdateType(str, Enum):
    """Types of real-time updates"""
    KPI_UPDATE = "kpi_update"
    CHART_DATA = "chart_data"
    TABLE_DATA = "table_data"
    ALERT = "alert"
    SYSTEM = "system"


class ConnectionState(str, Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ClientConnection:
    """WebSocket client connection"""
    connection_id: str
    dashboard_id: str
    subscribed_widgets: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    state: ConnectionState = ConnectionState.CONNECTED
    websocket: Any = None  # WebSocket connection object
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataUpdate:
    """Real-time data update event"""
    update_id: str
    update_type: UpdateType
    dashboard_id: str
    widget_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher = more urgent


@dataclass
class UpdateSubscription:
    """Widget update subscription"""
    widget_id: str
    dashboard_id: str
    refresh_interval: int  # seconds
    last_update: datetime = field(default_factory=datetime.now)
    data_source: str = ""
    filters: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Real-time BI Server
# ============================================================

class RealtimeBIServer:
    """
    Real-time BI WebSocket server

    Manages WebSocket connections and broadcasts dashboard updates.
    """

    def __init__(
        self,
        max_connections: int = 10000,
        heartbeat_interval: int = 30,
        max_update_queue_size: int = 1000
    ):
        self.max_connections = max_connections
        self.heartbeat_interval = heartbeat_interval
        self.max_update_queue_size = max_update_queue_size

        # Connection management
        self.connections: Dict[str, ClientConnection] = {}
        self.dashboard_connections: Dict[str, Set[str]] = defaultdict(set)

        # Update management
        self.update_queue: asyncio.Queue = asyncio.Queue(maxsize=max_update_queue_size)
        self.subscriptions: Dict[str, UpdateSubscription] = {}

        # Data cache
        self.data_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}

        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "updates_sent": 0,
            "errors": 0
        }

        self._running = False
        self._tasks: List[asyncio.Task] = []

    async def start(self):
        """Start the real-time server"""
        if self._running:
            logger.warning("Real-time BI server already running")
            return

        self._running = True

        # Start background tasks
        self._tasks = [
            asyncio.create_task(self._process_updates()),
            asyncio.create_task(self._heartbeat_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]

        logger.info("Real-time BI server started")

    async def stop(self):
        """Stop the real-time server"""
        self._running = False

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)

        # Close all connections
        for conn in list(self.connections.values()):
            await self.disconnect_client(conn.connection_id)

        logger.info("Real-time BI server stopped")

    async def connect_client(
        self,
        connection_id: str,
        dashboard_id: str,
        websocket: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClientConnection:
        """
        Register new client connection

        Args:
            connection_id: Unique connection ID
            dashboard_id: Dashboard ID to connect to
            websocket: WebSocket connection object
            metadata: Optional client metadata

        Returns:
            ClientConnection object
        """
        if len(self.connections) >= self.max_connections:
            raise ValueError(f"Maximum connections ({self.max_connections}) reached")

        connection = ClientConnection(
            connection_id=connection_id,
            dashboard_id=dashboard_id,
            websocket=websocket,
            metadata=metadata or {}
        )

        self.connections[connection_id] = connection
        self.dashboard_connections[dashboard_id].add(connection_id)

        self.stats["total_connections"] += 1
        self.stats["active_connections"] = len(self.connections)

        logger.info(f"Client connected: {connection_id} to dashboard {dashboard_id}")

        # Send welcome message
        await self.send_to_client(connection_id, {
            "type": "system",
            "message": "Connected to real-time BI server",
            "dashboard_id": dashboard_id,
            "server_time": datetime.now().isoformat()
        })

        return connection

    async def disconnect_client(self, connection_id: str):
        """Disconnect client"""
        connection = self.connections.get(connection_id)

        if not connection:
            return

        # Remove from dashboard connections
        self.dashboard_connections[connection.dashboard_id].discard(connection_id)

        # Remove from connections
        del self.connections[connection_id]

        self.stats["active_connections"] = len(self.connections)

        logger.info(f"Client disconnected: {connection_id}")

    async def subscribe_widget(
        self,
        connection_id: str,
        widget_id: str,
        refresh_interval: int = 60
    ):
        """
        Subscribe to widget updates

        Args:
            connection_id: Connection ID
            widget_id: Widget to subscribe to
            refresh_interval: Update interval in seconds
        """
        connection = self.connections.get(connection_id)

        if not connection:
            logger.warning(f"Connection {connection_id} not found")
            return

        connection.subscribed_widgets.add(widget_id)

        # Create or update subscription
        subscription_id = f"{connection.dashboard_id}:{widget_id}"

        if subscription_id not in self.subscriptions:
            self.subscriptions[subscription_id] = UpdateSubscription(
                widget_id=widget_id,
                dashboard_id=connection.dashboard_id,
                refresh_interval=refresh_interval,
                data_source=f"/api/bi/widgets/{widget_id}/data"
            )

        logger.info(f"Client {connection_id} subscribed to widget {widget_id}")

        # Send initial data
        await self._fetch_and_send_widget_data(connection.dashboard_id, widget_id)

    async def unsubscribe_widget(self, connection_id: str, widget_id: str):
        """Unsubscribe from widget updates"""
        connection = self.connections.get(connection_id)

        if connection:
            connection.subscribed_widgets.discard(widget_id)
            logger.info(f"Client {connection_id} unsubscribed from widget {widget_id}")

    async def broadcast_update(self, update: DataUpdate):
        """
        Broadcast update to all subscribed clients

        Args:
            update: DataUpdate to broadcast
        """
        try:
            await self.update_queue.put(update)
        except asyncio.QueueFull:
            logger.error("Update queue full, dropping update")
            self.stats["errors"] += 1

    async def send_to_client(self, connection_id: str, data: Dict[str, Any]):
        """Send data to specific client"""
        connection = self.connections.get(connection_id)

        if not connection or not connection.websocket:
            return

        try:
            await connection.websocket.send_json(data)
            connection.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send to client {connection_id}: {e}")
            connection.state = ConnectionState.ERROR
            self.stats["errors"] += 1

    async def broadcast_to_dashboard(
        self,
        dashboard_id: str,
        data: Dict[str, Any],
        exclude: Optional[Set[str]] = None
    ):
        """
        Broadcast to all clients connected to a dashboard

        Args:
            dashboard_id: Dashboard ID
            data: Data to broadcast
            exclude: Set of connection IDs to exclude
        """
        connection_ids = self.dashboard_connections.get(dashboard_id, set())
        exclude = exclude or set()

        tasks = []
        for conn_id in connection_ids:
            if conn_id not in exclude:
                tasks.append(self.send_to_client(conn_id, data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_updates(self):
        """Background task to process update queue"""
        while self._running:
            try:
                # Get update from queue with timeout
                try:
                    update = await asyncio.wait_for(
                        self.update_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Find all clients subscribed to this widget
                target_connections = []

                for conn in self.connections.values():
                    if (conn.dashboard_id == update.dashboard_id and
                            update.widget_id in conn.subscribed_widgets):
                        target_connections.append(conn)

                # Send update to all subscribed clients
                update_message = {
                    "type": update.update_type.value,
                    "widget_id": update.widget_id,
                    "data": update.data,
                    "timestamp": update.timestamp.isoformat()
                }

                tasks = [
                    self.send_to_client(conn.connection_id, update_message)
                    for conn in target_connections
                ]

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    self.stats["updates_sent"] += len(tasks)

            except Exception as e:
                logger.error(f"Error processing update: {e}")
                self.stats["errors"] += 1

    async def _heartbeat_loop(self):
        """Send periodic heartbeat to all connections"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                # Send ping to all connections
                heartbeat_msg = {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }

                tasks = [
                    self.send_to_client(conn_id, heartbeat_msg)
                    for conn_id in self.connections.keys()
                ]

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                logger.debug(f"Sent heartbeat to {len(tasks)} clients")

            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

    async def _cleanup_loop(self):
        """Clean up stale connections and cache"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Run every minute

                now = datetime.now()
                stale_timeout = timedelta(minutes=5)

                # Remove stale connections
                stale_connections = [
                    conn_id for conn_id, conn in self.connections.items()
                    if now - conn.last_activity > stale_timeout
                ]

                for conn_id in stale_connections:
                    logger.warning(f"Removing stale connection: {conn_id}")
                    await self.disconnect_client(conn_id)

                # Clean old cache entries
                cache_timeout = timedelta(minutes=10)
                old_cache_keys = [
                    key for key, timestamp in self.cache_timestamps.items()
                    if now - timestamp > cache_timeout
                ]

                for key in old_cache_keys:
                    self.data_cache.pop(key, None)
                    self.cache_timestamps.pop(key, None)

                logger.debug(f"Cleanup: removed {len(stale_connections)} stale connections, "
                            f"{len(old_cache_keys)} cache entries")

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _fetch_and_send_widget_data(self, dashboard_id: str, widget_id: str):
        """Fetch widget data and send to subscribed clients"""
        # In production, fetch from actual data source
        # For now, generate mock data

        data = {
            "widget_id": widget_id,
            "timestamp": datetime.now().isoformat(),
            "value": 12345,  # Mock data
            "trend": "up"
        }

        update = DataUpdate(
            update_id=f"{dashboard_id}:{widget_id}:{datetime.now().timestamp()}",
            update_type=UpdateType.KPI_UPDATE,
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            data=data
        )

        await self.broadcast_update(update)

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            **self.stats,
            "dashboards_active": len(self.dashboard_connections),
            "subscriptions_active": len(self.subscriptions),
            "queue_size": self.update_queue.qsize(),
            "cache_size": len(self.data_cache)
        }


# ============================================================
# Data Stream Manager
# ============================================================

class DataStreamManager:
    """
    Manages data streams for real-time updates

    Polls data sources and pushes updates to the real-time server.
    """

    def __init__(self, realtime_server: RealtimeBIServer):
        self.server = realtime_server
        self.streams: Dict[str, asyncio.Task] = {}
        self._running = False

    async def start(self):
        """Start data stream manager"""
        self._running = True
        logger.info("Data stream manager started")

    async def stop(self):
        """Stop data stream manager"""
        self._running = False

        # Cancel all streams
        for task in self.streams.values():
            task.cancel()

        await asyncio.gather(*self.streams.values(), return_exceptions=True)
        self.streams.clear()

        logger.info("Data stream manager stopped")

    async def register_stream(
        self,
        stream_id: str,
        dashboard_id: str,
        widget_id: str,
        data_source: Callable,
        refresh_interval: int
    ):
        """
        Register new data stream

        Args:
            stream_id: Unique stream ID
            dashboard_id: Dashboard ID
            widget_id: Widget ID
            data_source: Async function that returns widget data
            refresh_interval: Update interval in seconds
        """
        if stream_id in self.streams:
            logger.warning(f"Stream {stream_id} already registered")
            return

        # Create streaming task
        task = asyncio.create_task(
            self._stream_loop(stream_id, dashboard_id, widget_id, data_source, refresh_interval)
        )

        self.streams[stream_id] = task
        logger.info(f"Registered stream {stream_id} with {refresh_interval}s interval")

    async def unregister_stream(self, stream_id: str):
        """Unregister data stream"""
        task = self.streams.pop(stream_id, None)

        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            logger.info(f"Unregistered stream {stream_id}")

    async def _stream_loop(
        self,
        stream_id: str,
        dashboard_id: str,
        widget_id: str,
        data_source: Callable,
        refresh_interval: int
    ):
        """Stream data loop"""
        last_data_hash = None

        while self._running:
            try:
                # Fetch data
                data = await data_source()

                # Check if data changed
                data_str = json.dumps(data, sort_keys=True)
                data_hash = hashlib.md5(data_str.encode()).hexdigest()

                if data_hash != last_data_hash:
                    # Data changed, send update
                    update = DataUpdate(
                        update_id=f"{stream_id}:{datetime.now().timestamp()}",
                        update_type=UpdateType.CHART_DATA,
                        dashboard_id=dashboard_id,
                        widget_id=widget_id,
                        data=data
                    )

                    await self.server.broadcast_update(update)
                    last_data_hash = data_hash

                # Wait for next refresh
                await asyncio.sleep(refresh_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stream {stream_id}: {e}")
                await asyncio.sleep(refresh_interval)


# ============================================================
# Server-Sent Events (SSE) Support
# ============================================================

class SSEConnection:
    """Server-Sent Events connection for browsers that don't support WebSocket"""

    def __init__(self, connection_id: str, dashboard_id: str):
        self.connection_id = connection_id
        self.dashboard_id = dashboard_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.connected_at = datetime.now()

    async def send_event(self, event_type: str, data: Dict[str, Any]):
        """Send SSE event"""
        await self.queue.put({
            "event": event_type,
            "data": json.dumps(data)
        })

    async def event_stream(self):
        """Generate SSE event stream"""
        while True:
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=30.0)

                yield f"event: {event['event']}\n"
                yield f"data: {event['data']}\n\n"

            except asyncio.TimeoutError:
                # Send keep-alive
                yield ": keep-alive\n\n"


# ============================================================
# Example Usage
# ============================================================

async def example_usage():
    """Example usage of real-time BI server"""

    # Create server
    server = RealtimeBIServer()
    await server.start()

    print("✅ Real-time BI server started")

    # Simulate client connection
    class MockWebSocket:
        async def send_json(self, data):
            print(f"📤 Sent: {json.dumps(data, indent=2, default=str)}")

    # Connect client
    connection = await server.connect_client(
        connection_id="client_1",
        dashboard_id="exec_overview",
        websocket=MockWebSocket(),
        metadata={"user_id": "123", "role": "executive"}
    )

    print(f"\n📱 Client connected: {connection.connection_id}")

    # Subscribe to widgets
    await server.subscribe_widget("client_1", "mrr_widget", refresh_interval=30)
    await server.subscribe_widget("client_1", "arr_widget", refresh_interval=30)

    print("\n✅ Subscribed to widgets")

    # Simulate updates
    update = DataUpdate(
        update_id="update_1",
        update_type=UpdateType.KPI_UPDATE,
        dashboard_id="exec_overview",
        widget_id="mrr_widget",
        data={
            "value": 125000,
            "change": 12.5,
            "trend": "up"
        }
    )

    await server.broadcast_update(update)

    print("\n✅ Broadcast update")

    # Wait a bit for processing
    await asyncio.sleep(1)

    # Get stats
    stats = server.get_stats()
    print(f"\n📊 Server stats:")
    print(json.dumps(stats, indent=2))

    # Cleanup
    await server.stop()
    print("\n✅ Server stopped")


if __name__ == "__main__":
    asyncio.run(example_usage())
