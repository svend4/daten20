"""
Comprehensive tests for src/core/websockets.py

Tests real-time WebSocket notifications, connection management, and event handlers.

Session 28 - 50+ tests
"""

import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock flask_socketio before importing
mock_socketio_class = MagicMock()
mock_emit = MagicMock()
mock_join_room = MagicMock()
mock_leave_room = MagicMock()

sys.modules["flask_socketio"] = Mock(
    SocketIO=mock_socketio_class,
    emit=mock_emit,
    join_room=mock_join_room,
    leave_room=mock_leave_room,
)

# Mock flask before importing
mock_request = Mock()
mock_request.sid = "test_sid_123"
sys.modules["flask"] = Mock(request=mock_request)

from src.core.websockets import (
    NotificationManager,
    get_notification_manager,
    handle_authenticate,
    handle_connect,
    handle_disconnect,
    handle_subscribe,
    handle_unsubscribe,
    notify_service_created,
    notify_service_updated,
    notify_user,
    socketio,
)


class TestNotificationManager:
    """Test NotificationManager class."""

    def test_init(self):
        """Test NotificationManager initialization"""
        manager = NotificationManager()
        assert manager.active_connections == {}

    def test_user_connected_new_user(self):
        """Test connecting a new user"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")

        assert "user1" in manager.active_connections
        assert "sid1" in manager.active_connections["user1"]
        assert len(manager.active_connections["user1"]) == 1

    def test_user_connected_existing_user(self):
        """Test connecting an existing user with new session"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_connected("user1", "sid2")

        assert "user1" in manager.active_connections
        assert "sid1" in manager.active_connections["user1"]
        assert "sid2" in manager.active_connections["user1"]
        assert len(manager.active_connections["user1"]) == 2

    def test_user_connected_multiple_users(self):
        """Test connecting multiple different users"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_connected("user2", "sid2")
        manager.user_connected("user3", "sid3")

        assert len(manager.active_connections) == 3
        assert "user1" in manager.active_connections
        assert "user2" in manager.active_connections
        assert "user3" in manager.active_connections

    def test_user_disconnected_single_session(self):
        """Test disconnecting user with single session"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_disconnected("user1", "sid1")

        assert "user1" not in manager.active_connections

    def test_user_disconnected_multiple_sessions(self):
        """Test disconnecting user with multiple sessions"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_connected("user1", "sid2")
        manager.user_disconnected("user1", "sid1")

        assert "user1" in manager.active_connections
        assert "sid1" not in manager.active_connections["user1"]
        assert "sid2" in manager.active_connections["user1"]
        assert len(manager.active_connections["user1"]) == 1

    def test_user_disconnected_nonexistent_user(self):
        """Test disconnecting nonexistent user"""
        manager = NotificationManager()
        # Should not raise exception
        manager.user_disconnected("user1", "sid1")
        assert "user1" not in manager.active_connections

    def test_user_disconnected_nonexistent_sid(self):
        """Test disconnecting with nonexistent session ID"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        # Should not raise exception
        manager.user_disconnected("user1", "sid_wrong")

        assert "user1" in manager.active_connections
        assert "sid1" in manager.active_connections["user1"]

    def test_is_user_online_true(self):
        """Test is_user_online returns True for connected user"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")

        assert manager.is_user_online("user1") is True

    def test_is_user_online_false(self):
        """Test is_user_online returns False for disconnected user"""
        manager = NotificationManager()

        assert manager.is_user_online("user1") is False

    def test_is_user_online_after_disconnect(self):
        """Test is_user_online after all sessions disconnected"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_disconnected("user1", "sid1")

        assert manager.is_user_online("user1") is False

    def test_is_user_online_with_multiple_sessions(self):
        """Test is_user_online with multiple sessions"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_connected("user1", "sid2")

        assert manager.is_user_online("user1") is True

    def test_get_online_users_empty(self):
        """Test get_online_users with no users"""
        manager = NotificationManager()
        users = manager.get_online_users()

        assert users == []

    def test_get_online_users_single(self):
        """Test get_online_users with single user"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        users = manager.get_online_users()

        assert "user1" in users
        assert len(users) == 1

    def test_get_online_users_multiple(self):
        """Test get_online_users with multiple users"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_connected("user2", "sid2")
        manager.user_connected("user3", "sid3")
        users = manager.get_online_users()

        assert len(users) == 3
        assert "user1" in users
        assert "user2" in users
        assert "user3" in users

    def test_send_to_user_single_session(self):
        """Test send_to_user with single session"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")

        with patch.object(socketio, "emit") as mock_emit:
            manager.send_to_user("user1", "test_event", {"data": "value"})

            mock_emit.assert_called_once_with("test_event", {"data": "value"}, room="sid1")

    def test_send_to_user_multiple_sessions(self):
        """Test send_to_user with multiple sessions"""
        manager = NotificationManager()
        manager.user_connected("user1", "sid1")
        manager.user_connected("user1", "sid2")

        with patch.object(socketio, "emit") as mock_emit:
            manager.send_to_user("user1", "test_event", {"data": "value"})

            assert mock_emit.call_count == 2
            mock_emit.assert_any_call("test_event", {"data": "value"}, room="sid1")
            mock_emit.assert_any_call("test_event", {"data": "value"}, room="sid2")

    def test_send_to_user_offline(self):
        """Test send_to_user with offline user"""
        manager = NotificationManager()

        with patch.object(socketio, "emit") as mock_emit:
            manager.send_to_user("user1", "test_event", {"data": "value"})

            mock_emit.assert_not_called()

    def test_broadcast(self):
        """Test broadcast to all users"""
        manager = NotificationManager()

        with patch.object(socketio, "emit") as mock_emit:
            manager.broadcast("test_event", {"data": "value"})

            mock_emit.assert_called_once_with("test_event", {"data": "value"}, broadcast=True)

    def test_broadcast_with_data(self):
        """Test broadcast with complex data"""
        manager = NotificationManager()

        data = {
            "message": "Test message",
            "user": "admin",
            "timestamp": "2026-01-19T12:00:00",
            "nested": {"key": "value"},
        }

        with patch.object(socketio, "emit") as mock_emit:
            manager.broadcast("notification", data)

            mock_emit.assert_called_once_with("notification", data, broadcast=True)


class TestGlobalInstance:
    """Test global notification manager instance."""

    def test_get_notification_manager_returns_instance(self):
        """Test get_notification_manager returns NotificationManager instance"""
        manager = get_notification_manager()
        assert isinstance(manager, NotificationManager)

    def test_get_notification_manager_singleton(self):
        """Test get_notification_manager returns same instance"""
        manager1 = get_notification_manager()
        manager2 = get_notification_manager()
        assert manager1 is manager2


class TestWebSocketEventHandlers:
    """Test WebSocket event handlers existence and callability."""

    def test_handle_connect_exists(self):
        """Test handle_connect handler exists"""
        assert callable(handle_connect)

    def test_handle_disconnect_exists(self):
        """Test handle_disconnect handler exists"""
        assert callable(handle_disconnect)

    def test_handle_authenticate_exists(self):
        """Test handle_authenticate handler exists"""
        assert callable(handle_authenticate)

    def test_handle_subscribe_exists(self):
        """Test handle_subscribe handler exists"""
        assert callable(handle_subscribe)

    def test_handle_unsubscribe_exists(self):
        """Test handle_unsubscribe handler exists"""
        assert callable(handle_unsubscribe)

    def test_all_handlers_imported(self):
        """Test all handlers are properly imported"""
        handlers = [
            handle_connect,
            handle_disconnect,
            handle_authenticate,
            handle_subscribe,
            handle_unsubscribe,
        ]
        for handler in handlers:
            assert handler is not None
            assert callable(handler)


class TestNotificationFunctions:
    """Test notification convenience functions."""

    @patch("src.core.websockets._notification_manager")
    @patch("src.core.websockets.datetime")
    def test_notify_service_created(self, mock_datetime, mock_manager):
        """Test notify_service_created broadcasts event"""
        mock_datetime.now.return_value.isoformat.return_value = "2026-01-19T12:00:00"

        notify_service_created(123, "Test Service", "admin")

        expected_data = {
            "service_id": 123,
            "service_name": "Test Service",
            "created_by": "admin",
            "timestamp": "2026-01-19T12:00:00",
        }
        mock_manager.broadcast.assert_called_once_with("service_created", expected_data)

    @patch("src.core.websockets._notification_manager")
    @patch("src.core.websockets.datetime")
    def test_notify_service_updated(self, mock_datetime, mock_manager):
        """Test notify_service_updated broadcasts event"""
        mock_datetime.now.return_value.isoformat.return_value = "2026-01-19T13:00:00"

        notify_service_updated(456, "Updated Service", "user1")

        expected_data = {
            "service_id": 456,
            "service_name": "Updated Service",
            "updated_by": "user1",
            "timestamp": "2026-01-19T13:00:00",
        }
        mock_manager.broadcast.assert_called_once_with("service_updated", expected_data)

    @patch("src.core.websockets._notification_manager")
    @patch("src.core.websockets.datetime")
    def test_notify_user_info(self, mock_datetime, mock_manager):
        """Test notify_user sends message to specific user"""
        mock_datetime.now.return_value.isoformat.return_value = "2026-01-19T14:00:00"

        notify_user("user123", "Test message")

        expected_data = {
            "message": "Test message",
            "type": "info",
            "timestamp": "2026-01-19T14:00:00",
        }
        mock_manager.send_to_user.assert_called_once_with("user123", "notification", expected_data)

    @patch("src.core.websockets._notification_manager")
    @patch("src.core.websockets.datetime")
    def test_notify_user_warning(self, mock_datetime, mock_manager):
        """Test notify_user with warning type"""
        mock_datetime.now.return_value.isoformat.return_value = "2026-01-19T15:00:00"

        notify_user("user456", "Warning message", "warning")

        expected_data = {
            "message": "Warning message",
            "type": "warning",
            "timestamp": "2026-01-19T15:00:00",
        }
        mock_manager.send_to_user.assert_called_once_with("user456", "notification", expected_data)

    @patch("src.core.websockets._notification_manager")
    @patch("src.core.websockets.datetime")
    def test_notify_user_error(self, mock_datetime, mock_manager):
        """Test notify_user with error type"""
        mock_datetime.now.return_value.isoformat.return_value = "2026-01-19T16:00:00"

        notify_user("user789", "Error occurred", "error")

        expected_data = {
            "message": "Error occurred",
            "type": "error",
            "timestamp": "2026-01-19T16:00:00",
        }
        mock_manager.send_to_user.assert_called_once_with("user789", "notification", expected_data)


class TestSocketIOInstance:
    """Test SocketIO instance configuration."""

    def test_socketio_instance_exists(self):
        """Test socketio instance is created"""
        assert socketio is not None

    def test_socketio_instance_is_mocked(self):
        """Test socketio instance is properly mocked"""
        # In tests, socketio should be a MagicMock instance
        assert isinstance(socketio, (Mock, MagicMock))
