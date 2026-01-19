"""
Comprehensive tests for Web Push Notifications

Tests cover:
- VAPID key generation
- Push subscription management (subscribe, unsubscribe)
- Notification payload creation
- Push notification sending (single, to user, broadcast)
- Notification history and statistics
- Convenience methods for common notifications
- Global singleton instance
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.core.notifications.push import (
    NotificationUrgency,
    NotificationAction,
    PushSubscription,
    NotificationPayload,
    WebPushManager,
    get_push_manager,
    configure_push_manager,
)


class TestVAPIDKeys:
    """Test VAPID key generation and management"""

    def test_vapid_keys_generated_by_default(self):
        """Test VAPID keys are generated if not provided"""
        manager = WebPushManager()

        assert manager.vapid_private_key is not None
        assert manager.vapid_public_key is not None
        assert len(manager.vapid_private_key) > 0
        assert len(manager.vapid_public_key) > 0

    def test_vapid_keys_can_be_provided(self):
        """Test custom VAPID keys can be provided"""
        private_key = "test_private_key"
        public_key = "test_public_key"

        manager = WebPushManager(
            vapid_private_key=private_key,
            vapid_public_key=public_key
        )

        assert manager.vapid_private_key == private_key
        assert manager.vapid_public_key == public_key

    def test_get_public_key(self):
        """Test getting public key for client"""
        manager = WebPushManager(vapid_public_key="test_public")

        public_key = manager.get_public_key()
        assert public_key == "test_public"

    def test_vapid_subject_default(self):
        """Test default VAPID subject"""
        manager = WebPushManager()

        assert manager.vapid_subject == "mailto:admin@example.com"

    def test_vapid_subject_custom(self):
        """Test custom VAPID subject"""
        manager = WebPushManager(vapid_subject="mailto:custom@example.com")

        assert manager.vapid_subject == "mailto:custom@example.com"


class TestPushSubscription:
    """Test push subscription management"""

    @pytest.fixture
    def manager(self):
        return WebPushManager()

    @pytest.fixture
    def subscription(self):
        return PushSubscription(
            endpoint="https://fcm.googleapis.com/fcm/send/test123",
            keys={"p256dh": "test_p256dh", "auth": "test_auth"},
            user_id=1,
            user_agent="Mozilla/5.0"
        )

    def test_subscribe_new_subscription(self, manager, subscription):
        """Test registering a new subscription"""
        result = manager.subscribe(subscription)

        assert result is True
        assert subscription.endpoint in manager.subscriptions
        assert subscription.created_at is not None

    def test_subscribe_multiple_subscriptions(self, manager):
        """Test subscribing multiple endpoints"""
        sub1 = PushSubscription(
            endpoint="https://endpoint1.com",
            keys={"p256dh": "key1", "auth": "auth1"},
            user_id=1
        )
        sub2 = PushSubscription(
            endpoint="https://endpoint2.com",
            keys={"p256dh": "key2", "auth": "auth2"},
            user_id=1
        )

        manager.subscribe(sub1)
        manager.subscribe(sub2)

        assert len(manager.subscriptions) == 2

    def test_unsubscribe_existing(self, manager, subscription):
        """Test unsubscribing an existing subscription"""
        manager.subscribe(subscription)

        result = manager.unsubscribe(subscription.endpoint)

        assert result is True
        assert subscription.endpoint not in manager.subscriptions

    def test_unsubscribe_nonexistent(self, manager):
        """Test unsubscribing a non-existent subscription"""
        result = manager.unsubscribe("https://nonexistent.com")

        assert result is False

    def test_get_subscriptions_for_user(self, manager):
        """Test getting all subscriptions for a user"""
        sub1 = PushSubscription(
            endpoint="https://endpoint1.com",
            keys={"p256dh": "key1", "auth": "auth1"},
            user_id=1
        )
        sub2 = PushSubscription(
            endpoint="https://endpoint2.com",
            keys={"p256dh": "key2", "auth": "auth2"},
            user_id=1
        )
        sub3 = PushSubscription(
            endpoint="https://endpoint3.com",
            keys={"p256dh": "key3", "auth": "auth3"},
            user_id=2
        )

        manager.subscribe(sub1)
        manager.subscribe(sub2)
        manager.subscribe(sub3)

        user1_subs = manager.get_subscriptions_for_user(1)
        assert len(user1_subs) == 2
        for sub in user1_subs:
            assert sub.user_id == 1

    def test_get_subscriptions_for_user_none(self, manager):
        """Test getting subscriptions for user with no subscriptions"""
        subs = manager.get_subscriptions_for_user(999)

        assert len(subs) == 0


class TestNotificationPayload:
    """Test notification payload creation"""

    def test_minimal_payload(self):
        """Test creating minimal notification payload"""
        payload = NotificationPayload(
            title="Test Title",
            body="Test Body"
        )

        assert payload.title == "Test Title"
        assert payload.body == "Test Body"
        assert payload.urgency == NotificationUrgency.NORMAL
        assert payload.ttl == 86400
        assert payload.silent is False

    def test_full_payload(self):
        """Test creating full notification payload"""
        actions = [
            {"action": "view", "title": "View"},
            {"action": "dismiss", "title": "Dismiss"}
        ]

        payload = NotificationPayload(
            title="Test",
            body="Body",
            icon="/icon.png",
            badge="/badge.png",
            image="/image.png",
            tag="test_tag",
            data={"key": "value"},
            actions=actions,
            urgency=NotificationUrgency.HIGH,
            ttl=3600,
            silent=True,
            require_interaction=True
        )

        assert payload.icon == "/icon.png"
        assert payload.badge == "/badge.png"
        assert payload.image == "/image.png"
        assert payload.tag == "test_tag"
        assert payload.data == {"key": "value"}
        assert payload.actions == actions
        assert payload.urgency == NotificationUrgency.HIGH
        assert payload.ttl == 3600
        assert payload.silent is True
        assert payload.require_interaction is True

    def test_urgency_levels(self):
        """Test all urgency levels"""
        for urgency in [
            NotificationUrgency.VERY_LOW,
            NotificationUrgency.LOW,
            NotificationUrgency.NORMAL,
            NotificationUrgency.HIGH
        ]:
            payload = NotificationPayload(
                title="Test",
                body="Body",
                urgency=urgency
            )
            assert payload.urgency == urgency


class TestSendingNotifications:
    """Test sending push notifications"""

    @pytest.fixture
    def manager(self):
        return WebPushManager()

    @pytest.fixture
    def subscription(self):
        return PushSubscription(
            endpoint="https://fcm.googleapis.com/fcm/send/test123",
            keys={"p256dh": "test_p256dh", "auth": "test_auth"},
            user_id=1
        )

    @pytest.fixture
    def payload(self):
        return NotificationPayload(
            title="Test Notification",
            body="This is a test"
        )

    def test_send_notification_success(self, manager, subscription, payload):
        """Test successful notification sending"""
        manager.subscribe(subscription)

        result = manager.send_notification(subscription, payload)

        assert result is True
        assert len(manager.sent_notifications) == 1
        assert manager.sent_notifications[0]["status"] == "sent"
        assert manager.sent_notifications[0]["payload"]["title"] == "Test Notification"

    def test_send_notification_updates_last_used(self, manager, subscription, payload):
        """Test sending updates subscription's last_used"""
        manager.subscribe(subscription)
        original_last_used = subscription.last_used

        manager.send_notification(subscription, payload)

        assert subscription.last_used is not None
        if original_last_used:
            assert subscription.last_used >= original_last_used

    def test_send_notification_with_all_fields(self, manager, subscription):
        """Test sending notification with all optional fields"""
        payload = NotificationPayload(
            title="Full Notification",
            body="All fields",
            icon="/icon.png",
            badge="/badge.png",
            image="/image.png",
            tag="full_test",
            data={"key": "value"},
            actions=[{"action": "view", "title": "View"}],
            silent=True,
            require_interaction=True
        )
        manager.subscribe(subscription)

        result = manager.send_notification(subscription, payload)

        assert result is True
        sent = manager.sent_notifications[0]["payload"]
        assert sent["icon"] == "/icon.png"
        assert sent["badge"] == "/badge.png"
        assert sent["image"] == "/image.png"
        assert sent["tag"] == "full_test"
        assert sent["data"] == {"key": "value"}
        assert "silent" in sent
        assert "requireInteraction" in sent

    def test_send_to_user_single_subscription(self, manager, payload):
        """Test sending to user with single subscription"""
        sub = PushSubscription(
            endpoint="https://endpoint1.com",
            keys={"p256dh": "key1", "auth": "auth1"},
            user_id=1
        )
        manager.subscribe(sub)

        count = manager.send_to_user(1, payload)

        assert count == 1
        assert len(manager.sent_notifications) == 1

    def test_send_to_user_multiple_subscriptions(self, manager, payload):
        """Test sending to user with multiple subscriptions"""
        sub1 = PushSubscription(
            endpoint="https://endpoint1.com",
            keys={"p256dh": "key1", "auth": "auth1"},
            user_id=1
        )
        sub2 = PushSubscription(
            endpoint="https://endpoint2.com",
            keys={"p256dh": "key2", "auth": "auth2"},
            user_id=1
        )
        manager.subscribe(sub1)
        manager.subscribe(sub2)

        count = manager.send_to_user(1, payload)

        assert count == 2
        assert len(manager.sent_notifications) == 2

    def test_send_to_user_no_subscriptions(self, manager, payload):
        """Test sending to user with no subscriptions"""
        count = manager.send_to_user(999, payload)

        assert count == 0
        assert len(manager.sent_notifications) == 0

    def test_broadcast(self, manager, payload):
        """Test broadcasting to all subscriptions"""
        for i in range(3):
            sub = PushSubscription(
                endpoint=f"https://endpoint{i}.com",
                keys={"p256dh": f"key{i}", "auth": f"auth{i}"},
                user_id=i
            )
            manager.subscribe(sub)

        count = manager.broadcast(payload)

        assert count == 3
        assert len(manager.sent_notifications) == 3

    def test_broadcast_empty(self, manager, payload):
        """Test broadcasting with no subscriptions"""
        count = manager.broadcast(payload)

        assert count == 0


class TestStatistics:
    """Test notification statistics"""

    @pytest.fixture
    def manager(self):
        return WebPushManager()

    def test_statistics_empty(self, manager):
        """Test statistics with no notifications"""
        stats = manager.get_statistics()

        assert stats["total"] == 0
        assert stats["sent"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["active_subscriptions"] == 0

    def test_statistics_with_notifications(self, manager):
        """Test statistics with sent notifications"""
        sub = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1
        )
        manager.subscribe(sub)

        payload = NotificationPayload(title="Test", body="Body")

        # Send multiple notifications
        for _ in range(3):
            manager.send_notification(sub, payload)

        stats = manager.get_statistics()
        assert stats["total"] == 3
        assert stats["sent"] == 3
        assert stats["failed"] == 0
        assert stats["success_rate"] == 100.0
        assert stats["active_subscriptions"] == 1

    def test_statistics_active_subscriptions(self, manager):
        """Test statistics includes active subscriptions count"""
        for i in range(5):
            sub = PushSubscription(
                endpoint=f"https://endpoint{i}.com",
                keys={"p256dh": f"key{i}", "auth": f"auth{i}"},
                user_id=i
            )
            manager.subscribe(sub)

        stats = manager.get_statistics()
        assert stats["active_subscriptions"] == 5


class TestConvenienceMethods:
    """Test convenience methods for common notifications"""

    @pytest.fixture
    def manager(self):
        return WebPushManager()

    @pytest.fixture
    def setup_user_subscription(self, manager):
        """Setup a subscription for user 1"""
        sub = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1
        )
        manager.subscribe(sub)

    def test_notify_service_created(self, manager, setup_user_subscription):
        """Test service created notification"""
        count = manager.notify_service_created(1, "Test Service", "Berlin")

        assert count == 1
        assert len(manager.sent_notifications) == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "Test Service" in sent["body"]
        assert "Berlin" in sent["body"]
        assert sent["tag"] == "service_created"

    def test_notify_approval_required(self, manager, setup_user_subscription):
        """Test approval required notification"""
        count = manager.notify_approval_required(1, "Important Document")

        assert count == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "Important Document" in sent["body"]
        assert sent["tag"] == "approval_required"
        assert "requireInteraction" in sent

    def test_notify_document_ready(self, manager, setup_user_subscription):
        """Test document ready notification"""
        count = manager.notify_document_ready(1, "Report.pdf")

        assert count == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "Report.pdf" in sent["body"]
        assert sent["tag"] == "document_ready"

    def test_notify_system_alert_broadcast(self, manager):
        """Test system alert broadcasts to all users"""
        # Setup multiple subscriptions
        for i in range(3):
            sub = PushSubscription(
                endpoint=f"https://endpoint{i}.com",
                keys={"p256dh": f"key{i}", "auth": f"auth{i}"},
                user_id=i
            )
            manager.subscribe(sub)

        count = manager.notify_system_alert("Server maintenance in 1 hour")

        assert count == 3
        assert len(manager.sent_notifications) == 3

    def test_notify_system_alert_high_urgency(self, manager, setup_user_subscription):
        """Test system alert with high urgency"""
        count = manager.notify_system_alert(
            "Critical system error",
            urgency=NotificationUrgency.HIGH
        )

        assert count == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "requireInteraction" in sent

    def test_notify_task_completed_success(self, manager, setup_user_subscription):
        """Test task completion notification (success)"""
        count = manager.notify_task_completed(1, "Data Export", success=True)

        assert count == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "Data Export" in sent["body"]
        assert "completed successfully" in sent["body"]

    def test_notify_task_completed_failure(self, manager, setup_user_subscription):
        """Test task completion notification (failure)"""
        count = manager.notify_task_completed(1, "Data Import", success=False)

        assert count == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "Data Import" in sent["body"]
        assert "failed" in sent["body"]

    def test_notify_reminder(self, manager, setup_user_subscription):
        """Test reminder notification"""
        count = manager.notify_reminder(1, "Meeting starts in 15 minutes")

        assert count == 1
        sent = manager.sent_notifications[0]["payload"]
        assert "Meeting starts in 15 minutes" in sent["body"]
        assert sent["tag"] == "reminder"
        assert "requireInteraction" in sent


class TestGlobalInstance:
    """Test global push manager instance"""

    def test_get_push_manager_singleton(self):
        """Test global push manager is singleton"""
        manager1 = get_push_manager()
        manager2 = get_push_manager()

        assert manager1 is manager2

    def test_get_push_manager_initialized(self):
        """Test global manager is properly initialized"""
        manager = get_push_manager()

        assert manager.vapid_private_key is not None
        assert manager.vapid_public_key is not None
        assert isinstance(manager.subscriptions, dict)

    def test_configure_push_manager(self):
        """Test configuring global push manager"""
        configure_push_manager(
            vapid_private_key="custom_private",
            vapid_public_key="custom_public",
            vapid_subject="mailto:custom@example.com"
        )

        manager = get_push_manager()
        assert manager.vapid_private_key == "custom_private"
        assert manager.vapid_public_key == "custom_public"
        assert manager.vapid_subject == "mailto:custom@example.com"


class TestNotificationHistory:
    """Test notification history tracking"""

    @pytest.fixture
    def manager(self):
        return WebPushManager()

    @pytest.fixture
    def subscription(self):
        return PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1
        )

    def test_notification_history_records_endpoint(self, manager, subscription):
        """Test history records endpoint"""
        manager.subscribe(subscription)
        payload = NotificationPayload(title="Test", body="Body")

        manager.send_notification(subscription, payload)

        assert manager.sent_notifications[0]["endpoint"] == subscription.endpoint

    def test_notification_history_records_user_id(self, manager, subscription):
        """Test history records user ID"""
        manager.subscribe(subscription)
        payload = NotificationPayload(title="Test", body="Body")

        manager.send_notification(subscription, payload)

        assert manager.sent_notifications[0]["user_id"] == 1

    def test_notification_history_records_timestamp(self, manager, subscription):
        """Test history records sent timestamp"""
        manager.subscribe(subscription)
        payload = NotificationPayload(title="Test", body="Body")

        manager.send_notification(subscription, payload)

        assert "sent_at" in manager.sent_notifications[0]
        assert isinstance(manager.sent_notifications[0]["sent_at"], datetime)

    def test_notification_history_multiple_notifications(self, manager, subscription):
        """Test history tracks multiple notifications"""
        manager.subscribe(subscription)

        for i in range(5):
            payload = NotificationPayload(title=f"Test {i}", body="Body")
            manager.send_notification(subscription, payload)

        assert len(manager.sent_notifications) == 5


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def manager(self):
        return WebPushManager()

    def test_send_to_unsubscribed_endpoint(self, manager):
        """Test sending to unsubscribed endpoint"""
        subscription = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1
        )
        payload = NotificationPayload(title="Test", body="Body")

        # Send without subscribing first
        result = manager.send_notification(subscription, payload)

        # Should still succeed (manager doesn't check if subscribed)
        assert result is True

    def test_subscribe_same_endpoint_twice(self, manager):
        """Test subscribing same endpoint twice (updates)"""
        sub1 = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key1", "auth": "auth1"},
            user_id=1
        )
        sub2 = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key2", "auth": "auth2"},
            user_id=2
        )

        manager.subscribe(sub1)
        manager.subscribe(sub2)

        # Should have only one subscription (latest)
        assert len(manager.subscriptions) == 1
        assert manager.subscriptions["https://endpoint.com"].user_id == 2

    def test_broadcast_to_empty_subscriptions(self, manager):
        """Test broadcast with no subscriptions"""
        payload = NotificationPayload(title="Test", body="Body")

        count = manager.broadcast(payload)

        assert count == 0
        assert len(manager.sent_notifications) == 0

    def test_notification_with_empty_title(self, manager):
        """Test notification with empty title"""
        subscription = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1
        )
        manager.subscribe(subscription)

        payload = NotificationPayload(title="", body="Body with no title")
        result = manager.send_notification(subscription, payload)

        assert result is True
        assert manager.sent_notifications[0]["payload"]["title"] == ""

    def test_notification_with_unicode(self, manager):
        """Test notification with unicode characters"""
        subscription = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1
        )
        manager.subscribe(subscription)

        payload = NotificationPayload(
            title="Überschrift 🎉",
            body="Körper mit äöü und emoji 🚀"
        )
        result = manager.send_notification(subscription, payload)

        assert result is True
        sent = manager.sent_notifications[0]["payload"]
        assert "🎉" in sent["title"]
        assert "🚀" in sent["body"]


class TestDataClasses:
    """Test dataclass functionality"""

    def test_push_subscription_creation(self):
        """Test creating PushSubscription"""
        sub = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"}
        )

        assert sub.endpoint == "https://endpoint.com"
        assert sub.keys == {"p256dh": "key", "auth": "auth"}
        assert sub.user_id is None
        assert sub.user_agent is None

    def test_push_subscription_with_optional_fields(self):
        """Test PushSubscription with all fields"""
        now = datetime.now()
        sub = PushSubscription(
            endpoint="https://endpoint.com",
            keys={"p256dh": "key", "auth": "auth"},
            user_id=1,
            user_agent="Mozilla/5.0",
            created_at=now,
            last_used=now
        )

        assert sub.user_id == 1
        assert sub.user_agent == "Mozilla/5.0"
        assert sub.created_at == now
        assert sub.last_used == now

    def test_notification_payload_defaults(self):
        """Test NotificationPayload default values"""
        payload = NotificationPayload(title="Test", body="Body")

        assert payload.icon is None
        assert payload.badge is None
        assert payload.image is None
        assert payload.tag is None
        assert payload.data is None
        assert payload.actions is None
        assert payload.urgency == NotificationUrgency.NORMAL
        assert payload.ttl == 86400
        assert payload.silent is False
        assert payload.require_interaction is False
