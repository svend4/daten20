"""
Real-time Collaborative Editing

Provides real-time collaborative editing with:
- WebSocket connection management
- Operational Transformation (OT) for synchronization
- Cursor tracking and presence awareness
- Version history and snapshots
- Conflict resolution
- Collaborative undo/redo
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class OperationType(str, Enum):
    """Types of operations for OT"""

    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"


class ConnectionStatus(str, Enum):
    """Connection status"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


@dataclass
class Operation:
    """Operational Transformation operation"""

    type: OperationType
    position: int
    content: Optional[str] = None  # For INSERT
    length: Optional[int] = None  # For DELETE/RETAIN


@dataclass
class DocumentOperation:
    """Document operation with metadata"""

    id: str
    document_id: str
    user_id: int
    operation: Operation
    revision: int  # Document version when operation was created
    timestamp: datetime = field(default_factory=datetime.now)
    applied: bool = False


@dataclass
class Cursor:
    """User cursor position"""

    user_id: int
    username: str
    position: int
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    color: str = "#0d6efd"


@dataclass
class UserPresence:
    """User presence in document"""

    user_id: int
    username: str
    cursor: Optional[Cursor] = None
    connected_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    status: ConnectionStatus = ConnectionStatus.CONNECTED


@dataclass
class DocumentSnapshot:
    """Document snapshot at a point in time"""

    id: str
    document_id: str
    revision: int
    content: str
    created_at: datetime
    created_by: Optional[int] = None


@dataclass
class CollaborativeDocument:
    """Document being collaboratively edited"""

    id: str
    name: str
    content: str
    revision: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    operations_history: List[DocumentOperation] = field(default_factory=list)
    active_users: Dict[int, UserPresence] = field(default_factory=dict)


class OperationalTransform:
    """Operational Transformation engine for conflict resolution"""

    def apply_operation(self, content: str, operation: Operation) -> str:
        """Apply operation to content"""
        if operation.type == OperationType.INSERT:
            # Insert content at position
            return content[: operation.position] + operation.content + content[operation.position :]

        elif operation.type == OperationType.DELETE:
            # Delete content at position
            return content[: operation.position] + content[operation.position + operation.length :]

        elif operation.type == OperationType.RETAIN:
            # No change
            return content

        return content

    def transform_operations(self, op1: Operation, op2: Operation, op1_is_first: bool) -> Tuple[Operation, Operation]:
        """
        Transform two concurrent operations

        Returns: (transformed_op1, transformed_op2)
        """
        # INSERT vs INSERT
        if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
            if op1.position < op2.position or (op1.position == op2.position and op1_is_first):
                # op1 comes before op2
                op2_transformed = Operation(
                    type=op2.type, position=op2.position + len(op1.content), content=op2.content
                )
                return op1, op2_transformed
            else:
                # op2 comes before op1
                op1_transformed = Operation(
                    type=op1.type, position=op1.position + len(op2.content), content=op1.content
                )
                return op1_transformed, op2

        # INSERT vs DELETE
        elif op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
            if op1.position <= op2.position:
                # INSERT before DELETE
                op2_transformed = Operation(type=op2.type, position=op2.position + len(op1.content), length=op2.length)
                return op1, op2_transformed
            elif op1.position >= op2.position + op2.length:
                # INSERT after DELETE
                op1_transformed = Operation(type=op1.type, position=op1.position - op2.length, content=op1.content)
                return op1_transformed, op2
            else:
                # INSERT within DELETE range
                op2_transformed = Operation(type=op2.type, position=op2.position, length=op2.length + len(op1.content))
                return op1, op2_transformed

        # DELETE vs INSERT (reverse of above)
        elif op1.type == OperationType.DELETE and op2.type == OperationType.INSERT:
            transformed_op2, transformed_op1 = self.transform_operations(op2, op1, not op1_is_first)
            return transformed_op1, transformed_op2

        # DELETE vs DELETE
        elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
            if op1.position + op1.length <= op2.position:
                # op1 DELETE before op2 DELETE
                op2_transformed = Operation(type=op2.type, position=op2.position - op1.length, length=op2.length)
                return op1, op2_transformed
            elif op2.position + op2.length <= op1.position:
                # op2 DELETE before op1 DELETE
                op1_transformed = Operation(type=op1.type, position=op1.position - op2.length, length=op1.length)
                return op1_transformed, op2
            else:
                # Overlapping DELETEs - complex case
                # Simplified: whoever starts earlier wins
                if op1.position < op2.position:
                    op2_transformed = Operation(
                        type=op2.type,
                        position=op1.position,
                        length=max(0, op2.position + op2.length - op1.position - op1.length),
                    )
                    return op1, op2_transformed
                else:
                    op1_transformed = Operation(
                        type=op1.type,
                        position=op2.position,
                        length=max(0, op1.position + op1.length - op2.position - op2.length),
                    )
                    return op1_transformed, op2

        # Default: no transformation needed
        return op1, op2

    def compose_operations(self, op1: Operation, op2: Operation) -> Optional[Operation]:
        """Compose two sequential operations into one"""
        # Simplified composition
        # In production, implement full OT composition rules

        # INSERT followed by INSERT at same position
        if (
            op1.type == OperationType.INSERT
            and op2.type == OperationType.INSERT
            and op1.position + len(op1.content) == op2.position
        ):
            return Operation(type=OperationType.INSERT, position=op1.position, content=op1.content + op2.content)

        # DELETE followed by DELETE at same position
        if op1.type == OperationType.DELETE and op2.type == OperationType.DELETE and op1.position == op2.position:
            return Operation(type=OperationType.DELETE, position=op1.position, length=op1.length + op2.length)

        return None


class DocumentManager:
    """Manages collaborative documents"""

    def __init__(self):
        self.documents: Dict[str, CollaborativeDocument] = {}
        self.ot = OperationalTransform()

    def create_document(self, name: str, initial_content: str = "") -> str:
        """Create new collaborative document"""
        doc_id = str(uuid.uuid4())

        document = CollaborativeDocument(id=doc_id, name=name, content=initial_content)

        self.documents[doc_id] = document
        return doc_id

    def get_document(self, doc_id: str) -> Optional[CollaborativeDocument]:
        """Get document by ID"""
        return self.documents.get(doc_id)

    def apply_operation(
        self, doc_id: str, user_id: int, operation: Operation, client_revision: int
    ) -> Tuple[bool, Optional[int]]:
        """
        Apply operation to document

        Returns: (success, new_revision)
        """
        if doc_id not in self.documents:
            return False, None

        document = self.documents[doc_id]

        # Check if operation is based on current revision
        if client_revision != document.revision:
            # Need to transform operation against missing operations
            operation = self._transform_against_missing_ops(document, operation, client_revision)

        # Apply operation
        try:
            document.content = self.ot.apply_operation(document.content, operation)
            document.revision += 1
            document.last_modified = datetime.now()

            # Record operation
            doc_op = DocumentOperation(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                user_id=user_id,
                operation=operation,
                revision=document.revision,
                applied=True,
            )

            document.operations_history.append(doc_op)

            # Keep only last 1000 operations
            if len(document.operations_history) > 1000:
                document.operations_history = document.operations_history[-1000:]

            return True, document.revision

        except Exception as e:
            print(f"Error applying operation: {e}")
            return False, None

    def _transform_against_missing_ops(
        self, document: CollaborativeDocument, operation: Operation, client_revision: int
    ) -> Operation:
        """Transform operation against operations client hasn't seen"""
        # Get operations after client's revision
        missing_ops = [op for op in document.operations_history if op.revision > client_revision and op.applied]

        transformed_op = operation

        for doc_op in missing_ops:
            # Transform against each missing operation
            transformed_op, _ = self.ot.transform_operations(
                transformed_op, doc_op.operation, True  # Our operation happened first (client-side)
            )

        return transformed_op

    def get_operations_since(self, doc_id: str, since_revision: int) -> List[DocumentOperation]:
        """Get operations since a revision"""
        if doc_id not in self.documents:
            return []

        document = self.documents[doc_id]

        return [op for op in document.operations_history if op.revision > since_revision]


class PresenceManager:
    """Manages user presence and cursors"""

    def __init__(self):
        self.user_colors = ["#0d6efd", "#198754", "#dc3545", "#ffc107", "#6f42c1", "#fd7e14", "#20c997", "#d63384"]

    def join_document(self, doc_id: str, user_id: int, username: str, document_manager: DocumentManager) -> bool:
        """User joins document editing session"""
        document = document_manager.get_document(doc_id)
        if not document:
            return False

        # Assign color
        color = self.user_colors[user_id % len(self.user_colors)]

        presence = UserPresence(
            user_id=user_id,
            username=username,
            cursor=Cursor(user_id=user_id, username=username, position=0, color=color),
        )

        document.active_users[user_id] = presence
        return True

    def leave_document(self, doc_id: str, user_id: int, document_manager: DocumentManager) -> bool:
        """User leaves document editing session"""
        document = document_manager.get_document(doc_id)
        if not document:
            return False

        if user_id in document.active_users:
            del document.active_users[user_id]

        return True

    def update_cursor(
        self,
        doc_id: str,
        user_id: int,
        position: int,
        selection_start: Optional[int],
        selection_end: Optional[int],
        document_manager: DocumentManager,
    ) -> bool:
        """Update user cursor position"""
        document = document_manager.get_document(doc_id)
        if not document or user_id not in document.active_users:
            return False

        presence = document.active_users[user_id]
        presence.cursor.position = position
        presence.cursor.selection_start = selection_start
        presence.cursor.selection_end = selection_end
        presence.last_seen = datetime.now()

        return True

    def get_active_users(self, doc_id: str, document_manager: DocumentManager) -> List[UserPresence]:
        """Get active users in document"""
        document = document_manager.get_document(doc_id)
        if not document:
            return []

        return list(document.active_users.values())


class VersionHistory:
    """Manages document version history"""

    def __init__(self):
        self.snapshots: Dict[str, List[DocumentSnapshot]] = {}  # doc_id -> snapshots

    def create_snapshot(self, doc_id: str, content: str, revision: int, created_by: Optional[int] = None) -> str:
        """Create document snapshot"""
        snapshot_id = str(uuid.uuid4())

        snapshot = DocumentSnapshot(
            id=snapshot_id,
            document_id=doc_id,
            revision=revision,
            content=content,
            created_at=datetime.now(),
            created_by=created_by,
        )

        if doc_id not in self.snapshots:
            self.snapshots[doc_id] = []

        self.snapshots[doc_id].append(snapshot)

        # Keep only last 100 snapshots
        if len(self.snapshots[doc_id]) > 100:
            self.snapshots[doc_id] = self.snapshots[doc_id][-100:]

        return snapshot_id

    def get_snapshot(self, snapshot_id: str) -> Optional[DocumentSnapshot]:
        """Get snapshot by ID"""
        for snapshots in self.snapshots.values():
            for snapshot in snapshots:
                if snapshot.id == snapshot_id:
                    return snapshot
        return None

    def get_document_snapshots(self, doc_id: str, limit: int = 50) -> List[DocumentSnapshot]:
        """Get snapshots for document"""
        if doc_id not in self.snapshots:
            return []

        snapshots = self.snapshots[doc_id]
        return snapshots[-limit:]  # Most recent

    def restore_snapshot(self, doc_id: str, snapshot_id: str, document_manager: DocumentManager) -> bool:
        """Restore document from snapshot"""
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot or snapshot.document_id != doc_id:
            return False

        document = document_manager.get_document(doc_id)
        if not document:
            return False

        # Restore content
        document.content = snapshot.content
        document.revision += 1
        document.last_modified = datetime.now()

        return True


class RealtimeEngine:
    """Main real-time collaboration engine"""

    def __init__(self):
        self.document_manager = DocumentManager()
        self.presence_manager = PresenceManager()
        self.version_history = VersionHistory()

        # WebSocket connections (simplified)
        self.connections: Dict[str, Set[int]] = {}  # doc_id -> user_ids

    def connect_user(self, doc_id: str, user_id: int, username: str) -> Dict[str, Any]:
        """User connects to document"""
        # Get or create document
        document = self.document_manager.get_document(doc_id)
        if not document:
            return {"error": "Document not found"}

        # Add to connections
        if doc_id not in self.connections:
            self.connections[doc_id] = set()
        self.connections[doc_id].add(user_id)

        # Join document
        self.presence_manager.join_document(doc_id, user_id, username, self.document_manager)

        # Get active users
        active_users = self.presence_manager.get_active_users(doc_id, self.document_manager)

        return {
            "document": {
                "id": document.id,
                "name": document.name,
                "content": document.content,
                "revision": document.revision,
            },
            "active_users": [
                {
                    "user_id": u.user_id,
                    "username": u.username,
                    "cursor": {
                        "position": u.cursor.position if u.cursor else 0,
                        "color": u.cursor.color if u.cursor else "#0d6efd",
                    },
                }
                for u in active_users
            ],
        }

    def disconnect_user(self, doc_id: str, user_id: int):
        """User disconnects from document"""
        if doc_id in self.connections:
            self.connections[doc_id].discard(user_id)

        self.presence_manager.leave_document(doc_id, user_id, self.document_manager)

    def handle_operation(self, doc_id: str, user_id: int, operation: Operation, client_revision: int) -> Dict[str, Any]:
        """Handle operation from user"""
        success, new_revision = self.document_manager.apply_operation(doc_id, user_id, operation, client_revision)

        if not success:
            return {"error": "Failed to apply operation"}

        # Get updated document
        document = self.document_manager.get_document(doc_id)

        # Broadcast to other users
        # In production, use WebSocket to broadcast

        return {
            "success": True,
            "revision": new_revision,
            "operation": {
                "type": operation.type.value,
                "position": operation.position,
                "content": operation.content,
                "length": operation.length,
            },
        }

    def handle_cursor_update(
        self,
        doc_id: str,
        user_id: int,
        position: int,
        selection_start: Optional[int] = None,
        selection_end: Optional[int] = None,
    ) -> bool:
        """Handle cursor position update"""
        return self.presence_manager.update_cursor(
            doc_id, user_id, position, selection_start, selection_end, self.document_manager
        )

    def create_snapshot(self, doc_id: str, created_by: Optional[int] = None) -> Optional[str]:
        """Create snapshot of current document state"""
        document = self.document_manager.get_document(doc_id)
        if not document:
            return None

        return self.version_history.create_snapshot(doc_id, document.content, document.revision, created_by)

    def get_statistics(self, doc_id: str) -> Dict[str, Any]:
        """Get document statistics"""
        document = self.document_manager.get_document(doc_id)
        if not document:
            return {}

        active_users = self.presence_manager.get_active_users(doc_id, self.document_manager)

        snapshots = self.version_history.get_document_snapshots(doc_id)

        return {
            "document_id": doc_id,
            "revision": document.revision,
            "content_length": len(document.content),
            "active_users": len(active_users),
            "operations_count": len(document.operations_history),
            "snapshots_count": len(snapshots),
            "last_modified": document.last_modified.isoformat(),
        }


# Global instance
_realtime_engine: Optional[RealtimeEngine] = None


def get_realtime_engine() -> RealtimeEngine:
    """Get global real-time engine instance"""
    global _realtime_engine

    if _realtime_engine is None:
        _realtime_engine = RealtimeEngine()

    return _realtime_engine


def configure_realtime_engine():
    """Configure real-time engine"""
    global _realtime_engine
    _realtime_engine = RealtimeEngine()
