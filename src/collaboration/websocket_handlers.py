"""
WebSocket Handlers for Real-time Collaboration

Provides WebSocket event handlers for collaborative editing.
Integrates RealtimeEngine with Flask-SocketIO.
"""

import logging
from typing import Any, Dict, Optional

from flask import request
from flask_socketio import emit, join_room, leave_room

from src.collaboration.realtime import Operation, OperationType, get_realtime_engine
from src.core.websockets import socketio

logger = logging.getLogger("dms.collaboration.websocket")


# Store session data: sid -> {user_id, username, document_id}
_sessions: Dict[str, Dict[str, Any]] = {}


# ==================== Document Collaboration Events ====================


@socketio.on("collab:join_document")
def handle_join_document(data):
    """
    User joins a collaborative editing session.

    Expected data:
    {
        "document_id": str,
        "user_id": int,
        "username": str
    }
    """
    try:
        document_id = data.get("document_id")
        user_id = data.get("user_id")
        username = data.get("username")

        if not all([document_id, user_id, username]):
            emit("collab:error", {"message": "Missing required fields"})
            return

        # Get realtime engine
        engine = get_realtime_engine()

        # Connect user to document
        result = engine.connect_user(document_id, user_id, username)

        if "error" in result:
            emit("collab:error", {"message": result["error"]})
            return

        # Join Socket.IO room for this document
        join_room(f"document_{document_id}")

        # Store session info
        _sessions[request.sid] = {
            "user_id": user_id,
            "username": username,
            "document_id": document_id,
        }

        # Send document state to user
        emit("collab:document_state", result)

        # Notify other users
        emit(
            "collab:user_joined",
            {"user_id": user_id, "username": username},
            room=f"document_{document_id}",
            skip_sid=request.sid,
        )

        logger.info(f"User {username} ({user_id}) joined document {document_id}")

    except Exception as e:
        logger.error(f"Error in join_document: {e}")
        emit("collab:error", {"message": str(e)})


@socketio.on("collab:leave_document")
def handle_leave_document(data=None):
    """User leaves a collaborative editing session."""
    try:
        if request.sid not in _sessions:
            return

        session = _sessions[request.sid]
        document_id = session["document_id"]
        user_id = session["user_id"]
        username = session["username"]

        # Get realtime engine
        engine = get_realtime_engine()

        # Disconnect user
        engine.disconnect_user(document_id, user_id)

        # Leave Socket.IO room
        leave_room(f"document_{document_id}")

        # Remove session
        del _sessions[request.sid]

        # Notify other users
        emit(
            "collab:user_left",
            {"user_id": user_id, "username": username},
            room=f"document_{document_id}",
        )

        logger.info(f"User {username} ({user_id}) left document {document_id}")

    except Exception as e:
        logger.error(f"Error in leave_document: {e}")


@socketio.on("collab:edit")
def handle_edit_operation(data):
    """
    Handle edit operation from user.

    Expected data:
    {
        "operation": {
            "type": "insert" | "delete" | "retain",
            "position": int,
            "content": str (for insert),
            "length": int (for delete/retain)
        },
        "client_revision": int
    }
    """
    try:
        if request.sid not in _sessions:
            emit("collab:error", {"message": "Not connected to document"})
            return

        session = _sessions[request.sid]
        document_id = session["document_id"]
        user_id = session["user_id"]

        operation_data = data.get("operation")
        client_revision = data.get("client_revision", 0)

        if not operation_data:
            emit("collab:error", {"message": "Missing operation"})
            return

        # Parse operation
        try:
            op_type = OperationType(operation_data["type"])
            operation = Operation(
                type=op_type,
                position=operation_data["position"],
                content=operation_data.get("content"),
                length=operation_data.get("length"),
            )
        except (KeyError, ValueError) as e:
            emit("collab:error", {"message": f"Invalid operation: {e}"})
            return

        # Get realtime engine
        engine = get_realtime_engine()

        # Apply operation
        result = engine.handle_operation(document_id, user_id, operation, client_revision)

        if "error" in result:
            emit("collab:error", {"message": result["error"]})
            return

        # Send acknowledgment to sender
        emit("collab:ack", {"revision": result["revision"]})

        # Broadcast operation to other users
        emit(
            "collab:remote_edit",
            {
                "user_id": user_id,
                "operation": result["operation"],
                "revision": result["revision"],
            },
            room=f"document_{document_id}",
            skip_sid=request.sid,
        )

        logger.debug(
            f"Applied {op_type.value} operation from user {user_id} "
            f"at position {operation.position} (revision {result['revision']})"
        )

    except Exception as e:
        logger.error(f"Error in edit_operation: {e}")
        emit("collab:error", {"message": str(e)})


@socketio.on("collab:cursor")
def handle_cursor_update(data):
    """
    Handle cursor position update.

    Expected data:
    {
        "position": int,
        "selection_start": int (optional),
        "selection_end": int (optional)
    }
    """
    try:
        if request.sid not in _sessions:
            return

        session = _sessions[request.sid]
        document_id = session["document_id"]
        user_id = session["user_id"]

        position = data.get("position", 0)
        selection_start = data.get("selection_start")
        selection_end = data.get("selection_end")

        # Get realtime engine
        engine = get_realtime_engine()

        # Update cursor
        engine.handle_cursor_update(document_id, user_id, position, selection_start, selection_end)

        # Broadcast cursor update to other users
        emit(
            "collab:cursor_update",
            {
                "user_id": user_id,
                "position": position,
                "selection_start": selection_start,
                "selection_end": selection_end,
            },
            room=f"document_{document_id}",
            skip_sid=request.sid,
        )

    except Exception as e:
        logger.error(f"Error in cursor_update: {e}")


@socketio.on("collab:create_snapshot")
def handle_create_snapshot(data=None):
    """Create a snapshot of the current document state."""
    try:
        if request.sid not in _sessions:
            emit("collab:error", {"message": "Not connected to document"})
            return

        session = _sessions[request.sid]
        document_id = session["document_id"]
        user_id = session["user_id"]

        # Get realtime engine
        engine = get_realtime_engine()

        # Create snapshot
        snapshot_id = engine.create_snapshot(document_id, user_id)

        if snapshot_id:
            emit("collab:snapshot_created", {"snapshot_id": snapshot_id})
            logger.info(f"Snapshot {snapshot_id} created for document {document_id} by user {user_id}")
        else:
            emit("collab:error", {"message": "Failed to create snapshot"})

    except Exception as e:
        logger.error(f"Error in create_snapshot: {e}")
        emit("collab:error", {"message": str(e)})


@socketio.on("collab:get_statistics")
def handle_get_statistics(data=None):
    """Get document statistics."""
    try:
        if request.sid not in _sessions:
            emit("collab:error", {"message": "Not connected to document"})
            return

        session = _sessions[request.sid]
        document_id = session["document_id"]

        # Get realtime engine
        engine = get_realtime_engine()

        # Get statistics
        stats = engine.get_statistics(document_id)

        emit("collab:statistics", stats)

    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        emit("collab:error", {"message": str(e)})


# ==================== Disconnect Handler ====================


@socketio.on("disconnect")
def handle_disconnect_collab():
    """Handle user disconnection."""
    try:
        if request.sid in _sessions:
            # Clean up session
            handle_leave_document()

    except Exception as e:
        logger.error(f"Error in disconnect handler: {e}")


# ==================== Utility Functions ====================


def get_session_info(sid: str) -> Optional[Dict[str, Any]]:
    """Get session information by socket ID."""
    return _sessions.get(sid)


def get_active_sessions() -> Dict[str, Dict[str, Any]]:
    """Get all active sessions."""
    return _sessions.copy()


def broadcast_to_document(document_id: str, event: str, data: Dict[str, Any], exclude_sid: Optional[str] = None):
    """Broadcast event to all users in a document."""
    socketio.emit(event, data, room=f"document_{document_id}", skip_sid=exclude_sid)


logger.info("Collaboration WebSocket handlers loaded")
