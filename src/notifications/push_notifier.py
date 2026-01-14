"""
Web Push Notifications

Sends browser push notifications using Web Push API (VAPID).

Features:
- Web Push API support (Chrome, Firefox, Edge, Safari)
- VAPID authentication
- Silent and visible notifications
- Action buttons
- Icons and images
- Data payload
- Subscription management

Configuration:
    Generate VAPID keys:
    ```python
    from pywebpush import vapid
    vapid_keys = vapid.Vapid()
    vapid_keys.generate_keys()
    print("Public:", vapid_keys.public_key)
    print("Private:", vapid_keys.private_key)
    ```

    Set environment variables:
    - VAPID_PUBLIC_KEY: Your public VAPID key
    - VAPID_PRIVATE_KEY: Your private VAPID key
    - VAPID_CLAIM_EMAIL: Contact email (e.g., mailto:admin@example.com)

Usage:
    >>> from src.notifications import send_push_notification
    >>> subscription = {
    ...     'endpoint': 'https://fcm.googleapis.com/...',
    ...     'keys': {'p256dh': '...', 'auth': '...'}
    ... }
    >>> result = send_push_notification(
    ...     subscription,
    ...     title='Hello',
    ...     body='This is a push notification',
    ...     icon='/icon.png'
    ... )
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os
import json
import logging

logger = logging.getLogger(__name__)


class NotificationUrgency(str, Enum):
    """Push notification urgency levels"""
    VERY_LOW = "very-low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class NotificationDirection(str, Enum):
    """Text direction"""
    AUTO = "auto"
    LTR = "ltr"
    RTL = "rtl"


@dataclass
class NotificationAction:
    """Notification action button"""
    action: str  # Action identifier
    title: str  # Button text
    icon: Optional[str] = None  # Button icon URL


@dataclass
class PushSubscription:
    """Push subscription information"""
    endpoint: str
    keys: Dict[str, str]  # Contains 'p256dh' and 'auth'
    user_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PushNotification:
    """Push notification payload"""
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None  # Small icon for status bar
    image: Optional[str] = None  # Large image
    tag: Optional[str] = None  # Notification group tag
    data: Optional[Dict[str, Any]] = None  # Custom data
    actions: List[NotificationAction] = field(default_factory=list)
    direction: NotificationDirection = NotificationDirection.AUTO
    lang: str = "en"
    vibrate: Optional[List[int]] = None  # Vibration pattern [200, 100, 200]
    silent: bool = False
    require_interaction: bool = False  # Stay on screen until user interacts
    renotify: bool = False  # Vibrate again if tag exists
    timestamp: Optional[int] = None

    def to_payload(self) -> Dict[str, Any]:
        """Convert to Web Push API payload."""
        payload = {
            'title': self.title,
            'body': self.body,
            'direction': self.direction.value,
            'lang': self.lang,
            'silent': self.silent,
            'requireInteraction': self.require_interaction,
            'renotify': self.renotify
        }

        if self.icon:
            payload['icon'] = self.icon
        if self.badge:
            payload['badge'] = self.badge
        if self.image:
            payload['image'] = self.image
        if self.tag:
            payload['tag'] = self.tag
        if self.data:
            payload['data'] = self.data
        if self.actions:
            payload['actions'] = [
                {'action': a.action, 'title': a.title, 'icon': a.icon}
                for a in self.actions
            ]
        if self.vibrate:
            payload['vibrate'] = self.vibrate
        if self.timestamp:
            payload['timestamp'] = self.timestamp

        return payload


@dataclass
class PushResult:
    """Push notification sending result"""
    success: bool
    subscription_id: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    expired: bool = False  # Subscription expired
    sent_at: Optional[datetime] = None


class WebPushNotifier:
    """
    Web Push notification service.

    Handles sending push notifications to browsers using Web Push API.
    """

    def __init__(
        self,
        vapid_public_key: Optional[str] = None,
        vapid_private_key: Optional[str] = None,
        vapid_claims: Optional[Dict[str, str]] = None
    ):
        """
        Initialize Web Push notifier.

        Args:
            vapid_public_key: VAPID public key (from env if not provided)
            vapid_private_key: VAPID private key (from env if not provided)
            vapid_claims: VAPID claims dict (from env if not provided)
        """
        self.vapid_public_key = vapid_public_key or os.getenv('VAPID_PUBLIC_KEY')
        self.vapid_private_key = vapid_private_key or os.getenv('VAPID_PRIVATE_KEY')

        if vapid_claims:
            self.vapid_claims = vapid_claims
        else:
            email = os.getenv('VAPID_CLAIM_EMAIL', 'mailto:admin@example.com')
            self.vapid_claims = {'sub': email}

        # Check if Web Push is configured
        self.enabled = bool(self.vapid_public_key and self.vapid_private_key)

        if self.enabled:
            try:
                from pywebpush import webpush, WebPushException
                self.webpush = webpush
                self.WebPushException = WebPushException
                logger.info("Web Push client initialized successfully")
            except ImportError:
                logger.warning("pywebpush library not installed. Run: pip install pywebpush")
                self.enabled = False
                self.webpush = None
                self.WebPushException = None
        else:
            logger.warning("Web Push not configured. Push notifications disabled.")
            self.webpush = None
            self.WebPushException = None

    def send_notification(
        self,
        subscription: PushSubscription,
        notification: PushNotification,
        urgency: NotificationUrgency = NotificationUrgency.NORMAL,
        ttl: int = 86400  # Time-to-live in seconds (default: 24 hours)
    ) -> PushResult:
        """
        Send push notification to a subscription.

        Args:
            subscription: Push subscription info
            notification: Notification to send
            urgency: Notification urgency
            ttl: Time-to-live in seconds

        Returns:
            Result of sending operation

        Example:
            >>> notifier = WebPushNotifier()
            >>> subscription = PushSubscription(
            ...     endpoint='https://fcm.googleapis.com/...',
            ...     keys={'p256dh': '...', 'auth': '...'}
            ... )
            >>> notification = PushNotification(
            ...     title='New Message',
            ...     body='You have a new message',
            ...     icon='/icon.png'
            ... )
            >>> result = notifier.send_notification(subscription, notification)
        """
        if not self.enabled:
            return PushResult(
                success=False,
                error="Web Push not configured. Check VAPID_* environment variables."
            )

        try:
            # Prepare subscription info for pywebpush
            subscription_info = {
                'endpoint': subscription.endpoint,
                'keys': subscription.keys
            }

            # Prepare payload
            payload = json.dumps(notification.to_payload())

            # Send push notification
            response = self.webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims,
                ttl=ttl,
                urgency=urgency.value
            )

            logger.info(f"Push notification sent: {response.status_code}")

            return PushResult(
                success=True,
                subscription_id=subscription.endpoint,
                status_code=response.status_code,
                sent_at=datetime.now()
            )

        except self.WebPushException as e:
            logger.error(f"Push notification failed: {e}")

            # Check if subscription expired (410 Gone or 404 Not Found)
            expired = False
            if hasattr(e, 'response') and e.response:
                status_code = e.response.status_code
                expired = status_code in [404, 410]

                if expired:
                    logger.warning(f"Subscription expired: {subscription.endpoint}")

            return PushResult(
                success=False,
                error=str(e),
                expired=expired
            )

        except Exception as e:
            logger.error(f"Unexpected error sending push: {e}")
            return PushResult(
                success=False,
                error=str(e)
            )

    def send_to_multiple(
        self,
        subscriptions: List[PushSubscription],
        notification: PushNotification,
        urgency: NotificationUrgency = NotificationUrgency.NORMAL,
        ttl: int = 86400
    ) -> Dict[str, PushResult]:
        """
        Send push notification to multiple subscriptions.

        Args:
            subscriptions: List of push subscriptions
            notification: Notification to send
            urgency: Notification urgency
            ttl: Time-to-live in seconds

        Returns:
            Dict mapping endpoint to result

        Example:
            >>> results = notifier.send_to_multiple(
            ...     subscriptions,
            ...     PushNotification(title='Announcement', body='Important update')
            ... )
            >>> success_count = sum(1 for r in results.values() if r.success)
        """
        results = {}

        for subscription in subscriptions:
            result = self.send_notification(subscription, notification, urgency, ttl)
            results[subscription.endpoint] = result

        # Log summary
        total = len(subscriptions)
        success = sum(1 for r in results.values() if r.success)
        expired = sum(1 for r in results.values() if r.expired)

        logger.info(f"Push notifications: {success}/{total} sent, {expired} expired")

        return results

    def send_silent_notification(
        self,
        subscription: PushSubscription,
        data: Dict[str, Any]
    ) -> PushResult:
        """
        Send silent push notification (background sync).

        Args:
            subscription: Push subscription
            data: Data payload

        Returns:
            Sending result

        Example:
            >>> result = notifier.send_silent_notification(
            ...     subscription,
            ...     {'type': 'sync', 'action': 'refresh'}
            ... )
        """
        notification = PushNotification(
            title='',
            body='',
            silent=True,
            data=data
        )

        return self.send_notification(
            subscription,
            notification,
            urgency=NotificationUrgency.LOW
        )

    @staticmethod
    def generate_vapid_keys() -> Dict[str, str]:
        """
        Generate new VAPID key pair.

        Returns:
            Dict with 'public_key' and 'private_key'

        Example:
            >>> keys = WebPushNotifier.generate_vapid_keys()
            >>> print("Public:", keys['public_key'])
            >>> print("Private:", keys['private_key'])
        """
        try:
            from pywebpush import Vapid

            vapid = Vapid()
            vapid.generate_keys()

            return {
                'public_key': vapid.public_key.decode('utf-8'),
                'private_key': vapid.private_key.decode('utf-8')
            }
        except ImportError:
            raise ImportError("pywebpush library required. Run: pip install pywebpush")


# ============================================================
# Convenience Functions
# ============================================================

_default_notifier: Optional[WebPushNotifier] = None


def get_push_notifier() -> WebPushNotifier:
    """Get default push notifier instance (singleton)."""
    global _default_notifier
    if _default_notifier is None:
        _default_notifier = WebPushNotifier()
    return _default_notifier


def send_push_notification(
    subscription: PushSubscription,
    title: str,
    body: str,
    icon: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    actions: Optional[List[NotificationAction]] = None,
    urgency: NotificationUrgency = NotificationUrgency.NORMAL
) -> PushResult:
    """
    Quick send push notification.

    Args:
        subscription: Push subscription
        title: Notification title
        body: Notification body
        icon: Icon URL
        data: Custom data
        actions: Action buttons
        urgency: Urgency level

    Returns:
        Sending result

    Example:
        >>> result = send_push_notification(
        ...     subscription,
        ...     'New Message',
        ...     'You have 3 new messages',
        ...     icon='/icon.png'
        ... )
    """
    notifier = get_push_notifier()

    notification = PushNotification(
        title=title,
        body=body,
        icon=icon,
        data=data,
        actions=actions or []
    )

    return notifier.send_notification(subscription, notification, urgency)


def send_notification_to_user(
    user_id: int,
    title: str,
    body: str,
    icon: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, PushResult]:
    """
    Send notification to all user's subscriptions.

    Args:
        user_id: User ID
        title: Notification title
        body: Notification body
        icon: Icon URL
        data: Custom data

    Returns:
        Dict of results per subscription

    Note:
        Requires database integration to fetch user subscriptions.
        This is a placeholder - implement with your database.
    """
    # TODO: Implement database integration
    # subscriptions = db.get_user_subscriptions(user_id)

    notifier = get_push_notifier()

    notification = PushNotification(
        title=title,
        body=body,
        icon=icon,
        data=data
    )

    # For now, return empty dict
    # Replace with: notifier.send_to_multiple(subscriptions, notification)
    logger.warning("send_notification_to_user: Database integration required")
    return {}


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    import sys

    # Check if configured
    notifier = WebPushNotifier()

    if not notifier.enabled:
        print("⚠️ Web Push not configured. Set environment variables:")
        print("   export VAPID_PUBLIC_KEY='your_public_key'")
        print("   export VAPID_PRIVATE_KEY='your_private_key'")
        print("   export VAPID_CLAIM_EMAIL='mailto:admin@example.com'")
        print("\n💡 Generate VAPID keys:")
        print("   python -c \"from src.notifications.push_notifier import WebPushNotifier; print(WebPushNotifier.generate_vapid_keys())\"")
        sys.exit(1)

    print("✅ Web Push configured")
    print(f"📧 Contact: {notifier.vapid_claims.get('sub')}")

    # Example subscription (replace with real subscription from browser)
    example_subscription = PushSubscription(
        endpoint='https://fcm.googleapis.com/fcm/send/...',
        keys={
            'p256dh': 'BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM=',
            'auth': 'tBHItJI5svbpez7KI4CCXg=='
        }
    )

    # Test notification
    notification = PushNotification(
        title='Test Notification',
        body='This is a test from DMS Push Notifier',
        icon='/icon.png',
        badge='/badge.png',
        actions=[
            NotificationAction('open', 'Open', '/icon-open.png'),
            NotificationAction('close', 'Close', '/icon-close.png')
        ],
        data={'url': '/dashboard', 'type': 'test'}
    )

    print("\n📱 Sending test push notification...")
    print("⚠️ Note: Requires valid subscription from browser")

    # Uncomment to actually send (needs real subscription):
    # result = notifier.send_notification(example_subscription, notification)
    # if result.success:
    #     print("✅ Push sent successfully!")
    # else:
    #     print(f"❌ Failed: {result.error}")
