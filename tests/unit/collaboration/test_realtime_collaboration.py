"""
Unit Tests for Real-time Collaboration

Tests for collaborative editing features including:
- Operational Transformation
- Document management
- Presence tracking
- Version history
"""

import pytest
from datetime import datetime

from src.collaboration.realtime import (
    ConnectionStatus,
    DocumentManager,
    Operation,
    OperationalTransform,
    OperationType,
    PresenceManager,
    RealtimeEngine,
    VersionHistory,
)


class TestOperationalTransform:
    """Tests for Operational Transformation engine."""

    def setup_method(self):
        """Setup test environment."""
        self.ot = OperationalTransform()

    def test_insert_operation(self):
        """Test INSERT operation."""
        content = "Hello World"
        operation = Operation(type=OperationType.INSERT, position=6, content="Beautiful ")

        result = self.ot.apply_operation(content, operation)

        assert result == "Hello Beautiful World"

    def test_delete_operation(self):
        """Test DELETE operation."""
        content = "Hello Beautiful World"
        operation = Operation(type=OperationType.DELETE, position=6, length=10)

        result = self.ot.apply_operation(content, operation)

        assert result == "Hello World"

    def test_retain_operation(self):
        """Test RETAIN operation."""
        content = "Hello World"
        operation = Operation(type=OperationType.RETAIN, position=0, length=5)

        result = self.ot.apply_operation(content, operation)

        assert result == "Hello World"  # No change

    def test_transform_insert_insert_before(self):
        """Test transforming two INSERT operations (first comes before)."""
        op1 = Operation(type=OperationType.INSERT, position=5, content="A")
        op2 = Operation(type=OperationType.INSERT, position=10, content="B")

        transformed_op1, transformed_op2 = self.ot.transform_operations(op1, op2, True)

        assert transformed_op1.position == 5
        assert transformed_op2.position == 11  # Adjusted for op1's insert

    def test_transform_insert_insert_same_position(self):
        """Test transforming two INSERT operations at same position."""
        op1 = Operation(type=OperationType.INSERT, position=5, content="A")
        op2 = Operation(type=OperationType.INSERT, position=5, content="B")

        transformed_op1, transformed_op2 = self.ot.transform_operations(op1, op2, True)

        assert transformed_op1.position == 5
        assert transformed_op2.position == 6  # op1 is first, so op2 shifts

    def test_transform_insert_delete(self):
        """Test transforming INSERT and DELETE operations."""
        op1 = Operation(type=OperationType.INSERT, position=5, content="ABC")
        op2 = Operation(type=OperationType.DELETE, position=10, length=5)

        transformed_op1, transformed_op2 = self.ot.transform_operations(op1, op2, True)

        assert transformed_op1.position == 5
        assert transformed_op2.position == 13  # Adjusted for op1's insert

    def test_transform_delete_delete_no_overlap(self):
        """Test transforming two DELETE operations with no overlap."""
        op1 = Operation(type=OperationType.DELETE, position=5, length=3)
        op2 = Operation(type=OperationType.DELETE, position=10, length=3)

        transformed_op1, transformed_op2 = self.ot.transform_operations(op1, op2, True)

        assert transformed_op1.position == 5
        assert transformed_op2.position == 7  # Adjusted for op1's delete

    def test_compose_insert_insert(self):
        """Test composing two consecutive INSERT operations."""
        op1 = Operation(type=OperationType.INSERT, position=5, content="ABC")
        op2 = Operation(type=OperationType.INSERT, position=8, content="DEF")

        composed = self.ot.compose_operations(op1, op2)

        assert composed is not None
        assert composed.type == OperationType.INSERT
        assert composed.position == 5
        assert composed.content == "ABCDEF"

    def test_compose_delete_delete(self):
        """Test composing two consecutive DELETE operations."""
        op1 = Operation(type=OperationType.DELETE, position=5, length=3)
        op2 = Operation(type=OperationType.DELETE, position=5, length=2)

        composed = self.ot.compose_operations(op1, op2)

        assert composed is not None
        assert composed.type == OperationType.DELETE
        assert composed.position == 5
        assert composed.length == 5


class TestDocumentManager:
    """Tests for Document Manager."""

    def setup_method(self):
        """Setup test environment."""
        self.manager = DocumentManager()

    def test_create_document(self):
        """Test document creation."""
        doc_id = self.manager.create_document("Test Doc", "Initial content")

        assert doc_id is not None
        assert doc_id in self.manager.documents

        document = self.manager.get_document(doc_id)
        assert document.name == "Test Doc"
        assert document.content == "Initial content"
        assert document.revision == 0

    def test_apply_operation_insert(self):
        """Test applying INSERT operation to document."""
        doc_id = self.manager.create_document("Test", "Hello")
        operation = Operation(type=OperationType.INSERT, position=5, content=" World")

        success, new_revision = self.manager.apply_operation(doc_id, 1, operation, 0)

        assert success is True
        assert new_revision == 1

        document = self.manager.get_document(doc_id)
        assert document.content == "Hello World"
        assert document.revision == 1

    def test_apply_operation_delete(self):
        """Test applying DELETE operation to document."""
        doc_id = self.manager.create_document("Test", "Hello World")
        operation = Operation(type=OperationType.DELETE, position=5, length=6)

        success, new_revision = self.manager.apply_operation(doc_id, 1, operation, 0)

        assert success is True
        assert new_revision == 1

        document = self.manager.get_document(doc_id)
        assert document.content == "Hello"

    def test_apply_operation_wrong_revision(self):
        """Test applying operation with wrong revision (OT needed)."""
        doc_id = self.manager.create_document("Test", "Hello")

        # Apply first operation
        op1 = Operation(type=OperationType.INSERT, position=5, content=" World")
        self.manager.apply_operation(doc_id, 1, op1, 0)

        # Apply second operation based on old revision (should be transformed)
        op2 = Operation(type=OperationType.INSERT, position=0, content="Hey ")
        success, new_revision = self.manager.apply_operation(doc_id, 2, op2, 0)

        assert success is True
        document = self.manager.get_document(doc_id)
        assert "Hey" in document.content

    def test_get_operations_since(self):
        """Test getting operations since a revision."""
        doc_id = self.manager.create_document("Test", "")

        # Apply multiple operations
        op1 = Operation(type=OperationType.INSERT, position=0, content="A")
        op2 = Operation(type=OperationType.INSERT, position=1, content="B")
        op3 = Operation(type=OperationType.INSERT, position=2, content="C")

        self.manager.apply_operation(doc_id, 1, op1, 0)
        self.manager.apply_operation(doc_id, 1, op2, 1)
        self.manager.apply_operation(doc_id, 1, op3, 2)

        # Get operations since revision 1
        operations = self.manager.get_operations_since(doc_id, 1)

        assert len(operations) == 2  # op2 and op3
        assert operations[0].operation.content == "B"
        assert operations[1].operation.content == "C"


class TestPresenceManager:
    """Tests for Presence Manager."""

    def setup_method(self):
        """Setup test environment."""
        self.doc_manager = DocumentManager()
        self.presence_manager = PresenceManager()

        # Create a test document
        self.doc_id = self.doc_manager.create_document("Test", "")

    def test_join_document(self):
        """Test user joining document."""
        success = self.presence_manager.join_document(self.doc_id, 1, "Alice", self.doc_manager)

        assert success is True

        active_users = self.presence_manager.get_active_users(self.doc_id, self.doc_manager)
        assert len(active_users) == 1
        assert active_users[0].user_id == 1
        assert active_users[0].username == "Alice"

    def test_leave_document(self):
        """Test user leaving document."""
        self.presence_manager.join_document(self.doc_id, 1, "Alice", self.doc_manager)
        success = self.presence_manager.leave_document(self.doc_id, 1, self.doc_manager)

        assert success is True

        active_users = self.presence_manager.get_active_users(self.doc_id, self.doc_manager)
        assert len(active_users) == 0

    def test_update_cursor(self):
        """Test updating user cursor position."""
        self.presence_manager.join_document(self.doc_id, 1, "Alice", self.doc_manager)

        success = self.presence_manager.update_cursor(self.doc_id, 1, 10, None, None, self.doc_manager)

        assert success is True

        document = self.doc_manager.get_document(self.doc_id)
        user = document.active_users[1]
        assert user.cursor.position == 10

    def test_multiple_users(self):
        """Test multiple users in same document."""
        self.presence_manager.join_document(self.doc_id, 1, "Alice", self.doc_manager)
        self.presence_manager.join_document(self.doc_id, 2, "Bob", self.doc_manager)
        self.presence_manager.join_document(self.doc_id, 3, "Charlie", self.doc_manager)

        active_users = self.presence_manager.get_active_users(self.doc_id, self.doc_manager)

        assert len(active_users) == 3
        usernames = [u.username for u in active_users]
        assert "Alice" in usernames
        assert "Bob" in usernames
        assert "Charlie" in usernames


class TestVersionHistory:
    """Tests for Version History."""

    def setup_method(self):
        """Setup test environment."""
        self.version_history = VersionHistory()
        self.doc_manager = DocumentManager()

        # Create a test document
        self.doc_id = self.doc_manager.create_document("Test", "Initial content")

    def test_create_snapshot(self):
        """Test creating snapshot."""
        snapshot_id = self.version_history.create_snapshot(self.doc_id, "Version 1", 0, 1)

        assert snapshot_id is not None

        snapshot = self.version_history.get_snapshot(snapshot_id)
        assert snapshot.document_id == self.doc_id
        assert snapshot.content == "Version 1"
        assert snapshot.revision == 0
        assert snapshot.created_by == 1

    def test_get_document_snapshots(self):
        """Test getting document snapshots."""
        # Create multiple snapshots
        self.version_history.create_snapshot(self.doc_id, "V1", 0, 1)
        self.version_history.create_snapshot(self.doc_id, "V2", 1, 1)
        self.version_history.create_snapshot(self.doc_id, "V3", 2, 1)

        snapshots = self.version_history.get_document_snapshots(self.doc_id)

        assert len(snapshots) == 3
        assert snapshots[0].content == "V1"
        assert snapshots[1].content == "V2"
        assert snapshots[2].content == "V3"

    def test_restore_snapshot(self):
        """Test restoring from snapshot."""
        # Modify document
        op = Operation(type=OperationType.INSERT, position=0, content="New ")
        self.doc_manager.apply_operation(self.doc_id, 1, op, 0)

        # Create snapshot of modified state
        snapshot_id = self.version_history.create_snapshot(
            self.doc_id, self.doc_manager.get_document(self.doc_id).content, 1, 1
        )

        # Modify again
        op2 = Operation(type=OperationType.INSERT, position=0, content="More ")
        self.doc_manager.apply_operation(self.doc_id, 1, op2, 1)

        # Restore snapshot
        success = self.version_history.restore_snapshot(self.doc_id, snapshot_id, self.doc_manager)

        assert success is True

        document = self.doc_manager.get_document(self.doc_id)
        assert "New " in document.content
        assert "More " not in document.content


class TestRealtimeEngine:
    """Tests for Realtime Engine (integration tests)."""

    def setup_method(self):
        """Setup test environment."""
        self.engine = RealtimeEngine()

    def test_create_and_connect(self):
        """Test creating document and connecting users."""
        doc_id = self.engine.document_manager.create_document("Test", "Hello")

        result = self.engine.connect_user(doc_id, 1, "Alice")

        assert "document" in result
        assert result["document"]["id"] == doc_id
        assert result["document"]["content"] == "Hello"
        assert len(result["active_users"]) == 1

    def test_handle_operation(self):
        """Test handling operation through engine."""
        doc_id = self.engine.document_manager.create_document("Test", "Hello")
        self.engine.connect_user(doc_id, 1, "Alice")

        operation = Operation(type=OperationType.INSERT, position=5, content=" World")
        result = self.engine.handle_operation(doc_id, 1, operation, 0)

        assert result["success"] is True
        assert result["revision"] == 1

        document = self.engine.document_manager.get_document(doc_id)
        assert document.content == "Hello World"

    def test_create_snapshot_through_engine(self):
        """Test creating snapshot through engine."""
        doc_id = self.engine.document_manager.create_document("Test", "Content")

        snapshot_id = self.engine.create_snapshot(doc_id, 1)

        assert snapshot_id is not None

        snapshot = self.engine.version_history.get_snapshot(snapshot_id)
        assert snapshot.content == "Content"

    def test_get_statistics(self):
        """Test getting statistics."""
        doc_id = self.engine.document_manager.create_document("Test", "")
        self.engine.connect_user(doc_id, 1, "Alice")

        # Apply some operations
        op = Operation(type=OperationType.INSERT, position=0, content="Test")
        self.engine.handle_operation(doc_id, 1, op, 0)

        # Get statistics
        stats = self.engine.get_statistics(doc_id)

        assert stats["document_id"] == doc_id
        assert stats["revision"] == 1
        assert stats["active_users"] == 1
        assert stats["operations_count"] == 1

    def test_disconnect_user(self):
        """Test disconnecting user."""
        doc_id = self.engine.document_manager.create_document("Test", "")
        self.engine.connect_user(doc_id, 1, "Alice")

        # Verify user connected
        stats_before = self.engine.get_statistics(doc_id)
        assert stats_before["active_users"] == 1

        # Disconnect
        self.engine.disconnect_user(doc_id, 1)

        # Verify user disconnected
        stats_after = self.engine.get_statistics(doc_id)
        assert stats_after["active_users"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
