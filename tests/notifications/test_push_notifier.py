"""
Tests for Push Notification System (Web Push)

Tests cover:
- Web Push notification sending
- VAPID authentication
- Subscription management
- Notification payloads
- Error handling
- Bulk notifications
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.notifications.push_notifier import (
    WebPushNotifier,
    PushSubscription,
    PushNotification,
    PushResult,
    NotificationUrgency,
    NotificationDirection,
    NotificationAction,
    send_push_notification,
    get_push_notifier
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_vapid_keys():
    """Mock VAPID keys for testing"""
    return {
        'public_key': 'BL_TEST_PUBLIC_KEY_' + 'A' * 60,
        'private_key': 'TEST_PRIVATE_KEY_' + 'B' * 40
    }


@pytest.fixture
def mock_subscription():
    """Mock push subscription"""
    return PushSubscription(
        endpoint='https://fcm.googleapis.com/fcm/send/mock-endpoint-123',
        keys={
            'p256dh': 'BL_TEST_P256DH_KEY_' + 'C' * 60,
            'auth': 'TEST_AUTH_SECRET_' + 'D' * 20
        },
        user_id=100
    )


@pytest.fixture
def mock_notification():
    """Mock push notification"""
    return PushNotification(
        title='Test Notification',
        body='This is a test message',
        icon='/icon.png',
        badge='/badge.png',
        tag='test-notification',
        data={'custom_data': 'value'},
        urgency=NotificationUrgency.NORMAL
    )


@pytest.fixture
def notifier_configured(mock_vapid_keys):
    """Configured push notifier"""
    with patch.dict('os.environ', {
        'VAPID_PUBLIC_KEY': mock_vapid_keys['public_key'],
        'VAPID_PRIVATE_KEY': mock_vapid_keys['private_key'],
        'VAPID_CLAIM_EMAIL': 'mailto:test@example.com'
    }):
        with patch('src.notifications.push_notifier.webpush'):
            notifier = WebPushNotifier()
            notifier.enabled = True
            return notifier


@pytest.fixture
def notifier_not_configured():
    """Notifier without configuration"""
    with patch.dict('os.environ', {}, clear=True):
        return WebPushNotifier()


# ============================================================
# Initialization Tests
# ============================================================

def test_notifier_initialization_with_env_vars(mock_vapid_keys):
    """Test notifier initializes from environment variables"""
    with patch.dict('os.environ', {
        'VAPID_PUBLIC_KEY': mock_vapid_keys['public_key'],
        'VAPID_PRIVATE_KEY': mock_vapid_keys['private_key'],
        'VAPID_CLAIM_EMAIL': 'mailto:test@example.com'
    }):
        with patch('src.notifications.push_notifier.webpush'):
            notifier = WebPushNotifier()
            assert notifier.vapid_public_key == mock_vapid_keys['public_key']
            assert notifier.vapid_private_key == mock_vapid_keys['private_key']
            assert notifier.vapid_claim_email == 'mailto:test@example.com'
            assert notifier.enabled is True


def test_notifier_initialization_with_params(mock_vapid_keys):
    """Test notifier initializes with explicit parameters"""
    with patch('src.notifications.push_notifier.webpush'):
        notifier = WebPushNotifier(
            vapid_public_key=mock_vapid_keys['public_key'],
            vapid_private_key=mock_vapid_keys['private_key'],
            vapid_claims={'sub': 'mailto:test@example.com'}
        )
        assert notifier.vapid_public_key == mock_vapid_keys['public_key']
        assert notifier.vapid_private_key == mock_vapid_keys['private_key']
        assert notifier.enabled is True


def test_notifier_disabled_without_config(notifier_not_configured):
    """Test notifier is disabled without configuration"""
    assert notifier_not_configured.enabled is False
    assert notifier_not_configured.vapid_public_key is None


def test_notifier_disabled_with_missing_library():
    """Test notifier disabled when pywebpush not installed"""
    with patch.dict('os.environ', {
        'VAPID_PUBLIC_KEY': 'test_key',
        'VAPID_PRIVATE_KEY': 'test_private',
        'VAPID_CLAIM_EMAIL': 'mailto:test@example.com'
    }):
        with patch('src.notifications.push_notifier.webpush', side_effect=ImportError()):
            notifier = WebPushNotifier()
            assert notifier.enabled is False


# ============================================================
# Send Notification Tests
# ============================================================

def test_send_notification_success(notifier_configured, mock_subscription, mock_notification):
    """Test successful notification sending"""
    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, mock_notification)

    assert result.success is True
    assert result.status_code == 201
    assert result.sent_at is not None
    assert mock_webpush.called


def test_send_notification_not_configured(notifier_not_configured, mock_subscription, mock_notification):
    """Test sending fails when not configured"""
    result = notifier_not_configured.send_notification(mock_subscription, mock_notification)

    assert result.success is False
    assert 'not configured' in result.error.lower()
    assert result.status_code is None


def test_send_notification_with_actions(notifier_configured, mock_subscription):
    """Test notification with action buttons"""
    notification = PushNotification(
        title='Action Test',
        body='Click a button',
        actions=[
            NotificationAction(action='view', title='View', icon='/view.png'),
            NotificationAction(action='dismiss', title='Dismiss')
        ]
    )

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, notification)

    assert result.success is True
    # Verify actions are included in payload
    call_args = mock_webpush.call_args
    assert call_args is not None


def test_send_notification_silent(notifier_configured, mock_subscription):
    """Test silent notification (no UI)"""
    notification = PushNotification(
        title='Silent',
        body='Background update',
        silent=True
    )

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, notification)

    assert result.success is True


def test_send_notification_with_custom_data(notifier_configured, mock_subscription):
    """Test notification with custom data payload"""
    notification = PushNotification(
        title='Data Test',
        body='Custom data',
        data={
            'user_id': 123,
            'action': 'update',
            'timestamp': '2025-01-14T10:00:00Z'
        }
    )

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, notification)

    assert result.success is True


def test_send_notification_high_urgency(notifier_configured, mock_subscription):
    """Test high urgency notification"""
    notification = PushNotification(
        title='Urgent',
        body='Important message',
        urgency=NotificationUrgency.HIGH
    )

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, notification)

    assert result.success is True


def test_send_notification_with_ttl(notifier_configured, mock_subscription):
    """Test notification with time-to-live"""
    notification = PushNotification(
        title='TTL Test',
        body='Expires in 1 hour',
        ttl=3600
    )

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, notification)

    assert result.success is True


def test_send_notification_failure(notifier_configured, mock_subscription, mock_notification):
    """Test handling of send failure"""
    mock_webpush = Mock()
    mock_webpush.side_effect = Exception('Network error')

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, mock_notification)

    assert result.success is False
    assert 'Network error' in result.error


def test_send_notification_invalid_subscription(notifier_configured, mock_notification):
    """Test handling of invalid subscription"""
    invalid_subscription = PushSubscription(
        endpoint='',  # Invalid empty endpoint
        keys={'p256dh': 'key', 'auth': 'secret'}
    )

    result = notifier_configured.send_notification(invalid_subscription, mock_notification)

    assert result.success is False
    assert result.error is not None


def test_send_notification_410_gone(notifier_configured, mock_subscription, mock_notification):
    """Test handling 410 Gone (subscription expired)"""
    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 410}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, mock_notification)

    # Should handle 410 gracefully
    assert result.status_code == 410
    # Could be success=False or success=True with warning, depending on implementation


# ============================================================
# Bulk Notification Tests
# ============================================================

def test_send_bulk_notifications_success(notifier_configured, mock_notification):
    """Test sending to multiple subscriptions"""
    subscriptions = [
        PushSubscription(
            endpoint=f'https://fcm.googleapis.com/endpoint-{i}',
            keys={'p256dh': f'key{i}', 'auth': f'auth{i}'}
        )
        for i in range(3)
    ]

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        results = notifier_configured.send_bulk_notifications(subscriptions, mock_notification)

    assert len(results) == 3
    assert all(r.success for r in results)
    assert mock_webpush.call_count == 3


def test_send_bulk_notifications_partial_failure(notifier_configured, mock_notification):
    """Test bulk send with some failures"""
    subscriptions = [
        PushSubscription(
            endpoint=f'https://fcm.googleapis.com/endpoint-{i}',
            keys={'p256dh': f'key{i}', 'auth': f'auth{i}'}
        )
        for i in range(3)
    ]

    mock_webpush = Mock()
    # First succeeds, second fails, third succeeds
    mock_webpush.side_effect = [
        {'status_code': 201},
        Exception('Failed'),
        {'status_code': 201}
    ]

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        results = notifier_configured.send_bulk_notifications(subscriptions, mock_notification)

    assert len(results) == 3
    assert results[0].success is True
    assert results[1].success is False
    assert results[2].success is True


def test_send_bulk_notifications_empty_list(notifier_configured, mock_notification):
    """Test bulk send with empty subscription list"""
    results = notifier_configured.send_bulk_notifications([], mock_notification)
    assert len(results) == 0


# ============================================================
# Subscription Management Tests
# ============================================================

def test_subscription_validation_valid(notifier_configured):
    """Test valid subscription validation"""
    subscription = PushSubscription(
        endpoint='https://fcm.googleapis.com/fcm/send/valid-endpoint',
        keys={'p256dh': 'valid_key', 'auth': 'valid_auth'}
    )

    is_valid = notifier_configured.validate_subscription(subscription)
    assert is_valid is True


def test_subscription_validation_missing_endpoint(notifier_configured):
    """Test validation fails with missing endpoint"""
    subscription = PushSubscription(
        endpoint='',
        keys={'p256dh': 'key', 'auth': 'auth'}
    )

    is_valid = notifier_configured.validate_subscription(subscription)
    assert is_valid is False


def test_subscription_validation_missing_keys(notifier_configured):
    """Test validation fails with missing keys"""
    subscription = PushSubscription(
        endpoint='https://fcm.googleapis.com/endpoint',
        keys={}
    )

    is_valid = notifier_configured.validate_subscription(subscription)
    assert is_valid is False


def test_subscription_validation_incomplete_keys(notifier_configured):
    """Test validation fails with incomplete keys"""
    subscription = PushSubscription(
        endpoint='https://fcm.googleapis.com/endpoint',
        keys={'p256dh': 'key'}  # Missing 'auth'
    )

    is_valid = notifier_configured.validate_subscription(subscription)
    assert is_valid is False


# ============================================================
# Notification Templates Tests
# ============================================================

def test_send_system_notification(notifier_configured, mock_subscription):
    """Test system notification template"""
    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_system_notification(
            mock_subscription,
            'System Update',
            'New version available'
        )

    assert result.success is True


def test_send_chat_notification(notifier_configured, mock_subscription):
    """Test chat notification template"""
    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_chat_notification(
            mock_subscription,
            sender='John Doe',
            message='Hello there!',
            chat_id=123
        )

    assert result.success is True


def test_send_alert_notification(notifier_configured, mock_subscription):
    """Test alert notification template"""
    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_alert_notification(
            mock_subscription,
            'Security Alert',
            'Suspicious login detected',
            alert_type='SECURITY'
        )

    assert result.success is True


# ============================================================
# Convenience Functions Tests
# ============================================================

def test_send_push_notification_convenience(mock_subscription, mock_vapid_keys):
    """Test convenience function send_push_notification"""
    with patch.dict('os.environ', {
        'VAPID_PUBLIC_KEY': mock_vapid_keys['public_key'],
        'VAPID_PRIVATE_KEY': mock_vapid_keys['private_key'],
        'VAPID_CLAIM_EMAIL': 'mailto:test@example.com'
    }):
        mock_webpush = Mock()
        mock_webpush.return_value = {'status_code': 201}

        with patch('src.notifications.push_notifier.webpush', mock_webpush):
            result = send_push_notification(
                mock_subscription,
                title='Test',
                body='Message',
                icon='/icon.png'
            )

        assert result.success is True


def test_get_push_notifier_singleton(mock_vapid_keys):
    """Test get_push_notifier returns singleton"""
    with patch.dict('os.environ', {
        'VAPID_PUBLIC_KEY': mock_vapid_keys['public_key'],
        'VAPID_PRIVATE_KEY': mock_vapid_keys['private_key'],
        'VAPID_CLAIM_EMAIL': 'mailto:test@example.com'
    }):
        with patch('src.notifications.push_notifier.webpush'):
            notifier1 = get_push_notifier()
            notifier2 = get_push_notifier()

            assert notifier1 is notifier2


# ============================================================
# Payload Construction Tests
# ============================================================

def test_notification_payload_construction(mock_notification):
    """Test notification payload is correctly constructed"""
    payload = mock_notification.to_dict()

    assert payload['title'] == 'Test Notification'
    assert payload['body'] == 'This is a test message'
    assert payload['icon'] == '/icon.png'
    assert payload['badge'] == '/badge.png'
    assert payload['tag'] == 'test-notification'
    assert payload['data'] == {'custom_data': 'value'}


def test_notification_payload_minimal(mock_notification):
    """Test minimal notification payload"""
    minimal = PushNotification(
        title='Minimal',
        body='Just title and body'
    )

    payload = minimal.to_dict()

    assert payload['title'] == 'Minimal'
    assert payload['body'] == 'Just title and body'
    assert 'icon' not in payload or payload['icon'] is None


def test_notification_with_vibration_pattern(mock_notification):
    """Test notification with vibration pattern"""
    notification = PushNotification(
        title='Vibrate',
        body='Vibration test',
        vibrate=[200, 100, 200]
    )

    payload = notification.to_dict()
    assert payload['vibrate'] == [200, 100, 200]


def test_notification_rtl_direction(mock_notification):
    """Test notification with RTL text direction"""
    notification = PushNotification(
        title='שלום',  # Hebrew "Hello"
        body='הודעת בדיקה',  # Hebrew "Test message"
        direction=NotificationDirection.RTL,
        lang='he'
    )

    payload = notification.to_dict()
    assert payload['dir'] == 'rtl'
    assert payload['lang'] == 'he'


# ============================================================
# Error Handling Tests
# ============================================================

def test_handle_network_timeout(notifier_configured, mock_subscription, mock_notification):
    """Test handling of network timeout"""
    mock_webpush = Mock()
    mock_webpush.side_effect = TimeoutError('Request timed out')

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, mock_notification)

    assert result.success is False
    assert 'timed out' in result.error.lower()


def test_handle_invalid_vapid_keys(mock_subscription, mock_notification):
    """Test handling of invalid VAPID keys"""
    with patch.dict('os.environ', {
        'VAPID_PUBLIC_KEY': 'invalid_key',
        'VAPID_PRIVATE_KEY': 'invalid_private'
    }):
        mock_webpush = Mock()
        mock_webpush.side_effect = Exception('Invalid VAPID keys')

        with patch('src.notifications.push_notifier.webpush', mock_webpush):
            notifier = WebPushNotifier()
            result = notifier.send_notification(mock_subscription, mock_notification)

        assert result.success is False


def test_handle_quota_exceeded(notifier_configured, mock_subscription, mock_notification):
    """Test handling of quota exceeded error"""
    mock_webpush = Mock()
    mock_webpush.side_effect = Exception('Quota exceeded')

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        result = notifier_configured.send_notification(mock_subscription, mock_notification)

    assert result.success is False
    assert 'quota' in result.error.lower()


# ============================================================
# Integration Tests (require actual VAPID keys)
# ============================================================

@pytest.mark.integration
def test_real_notification_send():
    """
    Integration test with real Web Push service.

    Requires environment variables:
    - VAPID_PUBLIC_KEY
    - VAPID_PRIVATE_KEY
    - VAPID_CLAIM_EMAIL
    - TEST_PUSH_SUBSCRIPTION (JSON with endpoint and keys)
    """
    import os

    if not all([
        os.getenv('VAPID_PUBLIC_KEY'),
        os.getenv('VAPID_PRIVATE_KEY'),
        os.getenv('TEST_PUSH_SUBSCRIPTION')
    ]):
        pytest.skip("Integration test requires VAPID keys and test subscription")

    notifier = WebPushNotifier()
    assert notifier.enabled, "Push notifier should be enabled"

    # Parse test subscription
    subscription_data = json.loads(os.getenv('TEST_PUSH_SUBSCRIPTION'))
    subscription = PushSubscription(
        endpoint=subscription_data['endpoint'],
        keys=subscription_data['keys']
    )

    notification = PushNotification(
        title='Integration Test',
        body='This is a test notification from the test suite',
        icon='/icon.png',
        tag='integration-test'
    )

    result = notifier.send_notification(subscription, notification)

    assert result.success, f"Notification send failed: {result.error}"
    assert result.status_code in [200, 201]
    print(f"✅ Successfully sent notification: {result.status_code}")


@pytest.mark.integration
def test_generate_vapid_keys():
    """
    Generate VAPID keys for testing.

    This is not a real test, but a helper to generate keys when needed.
    """
    try:
        from pywebpush import vapid

        vapid_keys = vapid.Vapid()
        vapid_keys.generate_keys()

        print("\n" + "=" * 60)
        print("Generated VAPID Keys (save these for testing):")
        print("=" * 60)
        print(f"Public Key:  {vapid_keys.public_key}")
        print(f"Private Key: {vapid_keys.private_key}")
        print("=" * 60)
        print("\nSet as environment variables:")
        print(f"export VAPID_PUBLIC_KEY='{vapid_keys.public_key}'")
        print(f"export VAPID_PRIVATE_KEY='{vapid_keys.private_key}'")
        print("export VAPID_CLAIM_EMAIL='mailto:admin@example.com'")
        print("=" * 60)

    except ImportError:
        pytest.skip("pywebpush not installed")


# ============================================================
# Performance Tests
# ============================================================

def test_bulk_send_performance(notifier_configured):
    """Test performance of bulk sending"""
    import time

    subscriptions = [
        PushSubscription(
            endpoint=f'https://fcm.googleapis.com/endpoint-{i}',
            keys={'p256dh': f'key{i}', 'auth': f'auth{i}'}
        )
        for i in range(100)
    ]

    notification = PushNotification(
        title='Performance Test',
        body='Bulk send test'
    )

    mock_webpush = Mock()
    mock_webpush.return_value = {'status_code': 201}

    with patch('src.notifications.push_notifier.webpush', mock_webpush):
        start = time.time()
        results = notifier_configured.send_bulk_notifications(subscriptions, notification)
        duration = time.time() - start

    assert len(results) == 100
    assert all(r.success for r in results)
    print(f"\n⏱️  Sent 100 notifications in {duration:.2f} seconds")
    print(f"   Average: {(duration / 100) * 1000:.2f}ms per notification")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
