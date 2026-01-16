"""
Real-time Notifications with WebSockets

Provides WebSocket support for real-time updates and notifications.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger("dms.websockets")


# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading", logger=True, engineio_logger=False)


class NotificationManager:
    """Manage real-time notifications."""

    def __init__(self):
        self.active_connections: Dict[str, List[str]] = {}  # user_id: [sid1, sid2, ...]

    def user_connected(self, user_id: str, sid: str):
        """Track user connection."""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(sid)
        logger.info(f"User {user_id} connected (sid: {sid})")

    def user_disconnected(self, user_id: str, sid: str):
        """Track user disconnection."""
        if user_id in self.active_connections:
            if sid in self.active_connections[user_id]:
                self.active_connections[user_id].remove(sid)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected (sid: {sid})")

    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online."""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

    def get_online_users(self) -> List[str]:
        """Get list of online user IDs."""
        return list(self.active_connections.keys())

    def send_to_user(self, user_id: str, event: str, data: Dict[str, Any]):
        """Send notification to specific user."""
        if user_id in self.active_connections:
            for sid in self.active_connections[user_id]:
                socketio.emit(event, data, room=sid)
            logger.debug(f"Sent {event} to user {user_id}")

    def broadcast(self, event: str, data: Dict[str, Any]):
        """Broadcast to all connected users."""
        socketio.emit(event, data, broadcast=True)
        logger.debug(f"Broadcast {event} to all users")


# Global notification manager
_notification_manager = NotificationManager()


def get_notification_manager() -> NotificationManager:
    """Get notification manager instance."""
    return _notification_manager


# WebSocket event handlers


@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit("connected", {"status": "success", "message": "Connected to DMS server"})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on("authenticate")
def handle_authenticate(data):
    """Handle user authentication."""
    user_id = data.get("user_id")
    token = data.get("token")

    # Verify token (simplified)
    if user_id and token:
        _notification_manager.user_connected(user_id, request.sid)
        join_room(f"user_{user_id}")
        emit("authenticated", {"status": "success"})
        logger.info(f"User {user_id} authenticated")
    else:
        emit("authenticated", {"status": "error", "message": "Invalid credentials"})


@socketio.on("subscribe")
def handle_subscribe(data):
    """Subscribe to specific channels."""
    channel = data.get("channel")
    if channel:
        join_room(channel)
        emit("subscribed", {"channel": channel, "status": "success"})
        logger.debug(f"Client {request.sid} subscribed to {channel}")


@socketio.on("unsubscribe")
def handle_unsubscribe(data):
    """Unsubscribe from channels."""
    channel = data.get("channel")
    if channel:
        leave_room(channel)
        emit("unsubscribed", {"channel": channel, "status": "success"})
        logger.debug(f"Client {request.sid} unsubscribed from {channel}")


# Notification functions


def notify_service_created(service_id: int, service_name: str, created_by: str):
    """Notify about new service creation."""
    _notification_manager.broadcast(
        "service_created",
        {
            "service_id": service_id,
            "service_name": service_name,
            "created_by": created_by,
            "timestamp": datetime.now().isoformat(),
        },
    )


def notify_service_updated(service_id: int, service_name: str, updated_by: str):
    """Notify about service update."""
    _notification_manager.broadcast(
        "service_updated",
        {
            "service_id": service_id,
            "service_name": service_name,
            "updated_by": updated_by,
            "timestamp": datetime.now().isoformat(),
        },
    )


def notify_user(user_id: str, message: str, type: str = "info"):
    """Send notification to specific user."""
    _notification_manager.send_to_user(
        user_id, "notification", {"message": message, "type": type, "timestamp": datetime.now().isoformat()}
    )


from flask import request
