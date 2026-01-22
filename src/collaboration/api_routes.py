"""
REST API Routes for Real-time Collaboration

Provides HTTP endpoints for managing collaborative documents.
"""

import logging
from typing import Dict, List, Optional

from flask import Blueprint, jsonify, request

from src.collaboration.realtime import get_realtime_engine

logger = logging.getLogger("dms.collaboration.api")

# Create Blueprint
collab_api = Blueprint("collab_api", __name__, url_prefix="/api/v1/collaboration")


# ==================== Document Management ====================


@collab_api.route("/documents", methods=["POST"])
def create_document():
    """
    Create a new collaborative document.

    Request body:
    {
        "name": str,
        "initial_content": str (optional)
    }

    Returns:
    {
        "document_id": str,
        "name": str,
        "revision": int
    }
    """
    try:
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"error": "Missing required field: name"}), 400

        name = data["name"]
        initial_content = data.get("initial_content", "")

        # Get realtime engine
        engine = get_realtime_engine()

        # Create document
        document_id = engine.document_manager.create_document(name, initial_content)

        return (
            jsonify(
                {
                    "document_id": document_id,
                    "name": name,
                    "revision": 0,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating document: {e}")
        return jsonify({"error": str(e)}), 500


@collab_api.route("/documents/<document_id>", methods=["GET"])
def get_document(document_id: str):
    """
    Get document details.

    Returns:
    {
        "id": str,
        "name": str,
        "content": str,
        "revision": int,
        "active_users": int,
        "last_modified": str
    }
    """
    try:
        # Get realtime engine
        engine = get_realtime_engine()

        # Get document
        document = engine.document_manager.get_document(document_id)

        if not document:
            return jsonify({"error": "Document not found"}), 404

        # Get active users count
        active_users = engine.presence_manager.get_active_users(document_id, engine.document_manager)

        return jsonify(
            {
                "id": document.id,
                "name": document.name,
                "content": document.content,
                "revision": document.revision,
                "active_users": len(active_users),
                "last_modified": document.last_modified.isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return jsonify({"error": str(e)}), 500


@collab_api.route("/documents/<document_id>/statistics", methods=["GET"])
def get_document_statistics(document_id: str):
    """
    Get document statistics.

    Returns:
    {
        "document_id": str,
        "revision": int,
        "content_length": int,
        "active_users": int,
        "operations_count": int,
        "snapshots_count": int,
        "last_modified": str
    }
    """
    try:
        # Get realtime engine
        engine = get_realtime_engine()

        # Get statistics
        stats = engine.get_statistics(document_id)

        if not stats:
            return jsonify({"error": "Document not found"}), 404

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Version History ====================


@collab_api.route("/documents/<document_id>/snapshots", methods=["POST"])
def create_snapshot(document_id: str):
    """
    Create a snapshot of the document.

    Request body:
    {
        "created_by": int (optional)
    }

    Returns:
    {
        "snapshot_id": str
    }
    """
    try:
        data = request.get_json() or {}
        created_by = data.get("created_by")

        # Get realtime engine
        engine = get_realtime_engine()

        # Create snapshot
        snapshot_id = engine.create_snapshot(document_id, created_by)

        if not snapshot_id:
            return jsonify({"error": "Failed to create snapshot"}), 500

        return jsonify({"snapshot_id": snapshot_id}), 201

    except Exception as e:
        logger.error(f"Error creating snapshot: {e}")
        return jsonify({"error": str(e)}), 500


@collab_api.route("/documents/<document_id>/snapshots", methods=["GET"])
def list_snapshots(document_id: str):
    """
    List all snapshots for a document.

    Query params:
    - limit: int (default 50)

    Returns:
    {
        "snapshots": [
            {
                "id": str,
                "revision": int,
                "created_at": str,
                "created_by": int | null
            },
            ...
        ]
    }
    """
    try:
        limit = request.args.get("limit", 50, type=int)

        # Get realtime engine
        engine = get_realtime_engine()

        # Get snapshots
        snapshots = engine.version_history.get_document_snapshots(document_id, limit)

        return jsonify(
            {
                "snapshots": [
                    {
                        "id": s.id,
                        "revision": s.revision,
                        "created_at": s.created_at.isoformat(),
                        "created_by": s.created_by,
                    }
                    for s in snapshots
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error listing snapshots: {e}")
        return jsonify({"error": str(e)}), 500


@collab_api.route("/snapshots/<snapshot_id>", methods=["GET"])
def get_snapshot(snapshot_id: str):
    """
    Get snapshot details.

    Returns:
    {
        "id": str,
        "document_id": str,
        "revision": int,
        "content": str,
        "created_at": str,
        "created_by": int | null
    }
    """
    try:
        # Get realtime engine
        engine = get_realtime_engine()

        # Get snapshot
        snapshot = engine.version_history.get_snapshot(snapshot_id)

        if not snapshot:
            return jsonify({"error": "Snapshot not found"}), 404

        return jsonify(
            {
                "id": snapshot.id,
                "document_id": snapshot.document_id,
                "revision": snapshot.revision,
                "content": snapshot.content,
                "created_at": snapshot.created_at.isoformat(),
                "created_by": snapshot.created_by,
            }
        )

    except Exception as e:
        logger.error(f"Error getting snapshot: {e}")
        return jsonify({"error": str(e)}), 500


@collab_api.route("/documents/<document_id>/restore/<snapshot_id>", methods=["POST"])
def restore_snapshot(document_id: str, snapshot_id: str):
    """
    Restore document from snapshot.

    Returns:
    {
        "success": bool,
        "revision": int
    }
    """
    try:
        # Get realtime engine
        engine = get_realtime_engine()

        # Restore snapshot
        success = engine.version_history.restore_snapshot(document_id, snapshot_id, engine.document_manager)

        if not success:
            return jsonify({"error": "Failed to restore snapshot"}), 500

        # Get updated document
        document = engine.document_manager.get_document(document_id)

        return jsonify({"success": True, "revision": document.revision if document else 0})

    except Exception as e:
        logger.error(f"Error restoring snapshot: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Active Users ====================


@collab_api.route("/documents/<document_id>/users", methods=["GET"])
def get_active_users(document_id: str):
    """
    Get active users in document.

    Returns:
    {
        "users": [
            {
                "user_id": int,
                "username": str,
                "cursor_position": int,
                "color": str,
                "status": str,
                "last_seen": str
            },
            ...
        ]
    }
    """
    try:
        # Get realtime engine
        engine = get_realtime_engine()

        # Get active users
        users = engine.presence_manager.get_active_users(document_id, engine.document_manager)

        return jsonify(
            {
                "users": [
                    {
                        "user_id": u.user_id,
                        "username": u.username,
                        "cursor_position": u.cursor.position if u.cursor else 0,
                        "color": u.cursor.color if u.cursor else "#0d6efd",
                        "status": u.status.value,
                        "last_seen": u.last_seen.isoformat(),
                    }
                    for u in users
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error getting active users: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Operations History ====================


@collab_api.route("/documents/<document_id>/operations", methods=["GET"])
def get_operations_history(document_id: str):
    """
    Get operations history for document.

    Query params:
    - since_revision: int (optional)
    - limit: int (default 100)

    Returns:
    {
        "operations": [
            {
                "id": str,
                "user_id": int,
                "type": str,
                "position": int,
                "content": str | null,
                "length": int | null,
                "revision": int,
                "timestamp": str
            },
            ...
        ]
    }
    """
    try:
        since_revision = request.args.get("since_revision", 0, type=int)
        limit = request.args.get("limit", 100, type=int)

        # Get realtime engine
        engine = get_realtime_engine()

        # Get operations
        operations = engine.document_manager.get_operations_since(document_id, since_revision)

        # Apply limit
        operations = operations[:limit]

        return jsonify(
            {
                "operations": [
                    {
                        "id": op.id,
                        "user_id": op.user_id,
                        "type": op.operation.type.value,
                        "position": op.operation.position,
                        "content": op.operation.content,
                        "length": op.operation.length,
                        "revision": op.revision,
                        "timestamp": op.timestamp.isoformat(),
                    }
                    for op in operations
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error getting operations: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Health Check ====================


@collab_api.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns:
    {
        "status": "ok",
        "active_documents": int,
        "active_sessions": int
    }
    """
    try:
        engine = get_realtime_engine()

        active_documents = len(engine.document_manager.documents)
        active_sessions = sum(len(users) for users in engine.connections.values())

        return jsonify(
            {
                "status": "ok",
                "active_documents": active_documents,
                "active_sessions": active_sessions,
            }
        )

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


logger.info("Collaboration API routes loaded")
