"""
Web Push Notifications

Implements Web Push API for browser notifications.
"""

import base64
import json
import secrets
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class NotificationUrgency(str, Enum):
    """Notification urgency levels"""

    VERY_LOW = "very-low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class NotificationAction(str, Enum):
    """Standard notification actions"""

    VIEW = "view"
    OPEN = "open"
    DISMISS = "dismiss"
    REPLY = "reply"
    ARCHIVE = "archive"


@dataclass
class PushSubscription:
    """Push subscription from browser"""

    endpoint: str
    keys: Dict[str, str]
    user_id: Optional[int] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


@dataclass
class NotificationPayload:
    """Push notification payload"""

    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    image: Optional[str] = None
    tag: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, str]]] = None
    urgency: NotificationUrgency = NotificationUrgency.NORMAL
    ttl: int = 86400  # Time to live in seconds (default 24h)
    silent: bool = False
    require_interaction: bool = False


class WebPushManager:
    """Manages Web Push notifications"""

    def __init__(
        self,
        vapid_private_key: Optional[str] = None,
        vapid_public_key: Optional[str] = None,
        vapid_subject: str = "mailto:admin@example.com",
    ):
        self.vapid_private_key = vapid_private_key or self._generate_vapid_keys()[0]
        self.vapid_public_key = vapid_public_key or self._generate_vapid_keys()[1]
        self.vapid_subject = vapid_subject

        # Store subscriptions
        self.subscriptions: Dict[str, PushSubscription] = {}

        # Notification history
        self.sent_notifications: List[Dict[str, Any]] = []

    def _generate_vapid_keys(self) -> tuple:
        """Generate VAPID keys for development"""
        # In production, use proper VAPID key generation
        # from pywebpush import generate_vapid_keys
        private_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")
        public_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")
        return private_key, public_key

    def get_public_key(self) -> str:
        """Get VAPID public key for client subscription"""
        return self.vapid_public_key

    def subscribe(self, subscription: PushSubscription) -> bool:
        """Register a push subscription"""
        try:
            # Store subscription by endpoint
            subscription.created_at = datetime.now()
            self.subscriptions[subscription.endpoint] = subscription
            return True
        except Exception as e:
            print(f"Failed to register subscription: {e}")
            return False

    def unsubscribe(self, endpoint: str) -> bool:
        """Unregister a push subscription"""
        if endpoint in self.subscriptions:
            del self.subscriptions[endpoint]
            return True
        return False

    def get_subscriptions_for_user(self, user_id: int) -> List[PushSubscription]:
        """Get all subscriptions for a user"""
        return [sub for sub in self.subscriptions.values() if sub.user_id == user_id]

    def send_notification(self, subscription: PushSubscription, payload: NotificationPayload) -> bool:
        """Send push notification to a subscription"""
        try:
            # Build notification data
            notification_data = {
                "title": payload.title,
                "body": payload.body,
                "icon": payload.icon or "/static/img/icon-192x192.png",
                "badge": payload.badge or "/static/img/badge-72x72.png",
            }

            if payload.image:
                notification_data["image"] = payload.image

            if payload.tag:
                notification_data["tag"] = payload.tag

            if payload.data:
                notification_data["data"] = payload.data

            if payload.actions:
                notification_data["actions"] = payload.actions

            if payload.silent:
                notification_data["silent"] = True

            if payload.require_interaction:
                notification_data["requireInteraction"] = True

            # In real implementation with pywebpush:
            # from pywebpush import webpush
            # webpush(
            #     subscription_info={
            #         "endpoint": subscription.endpoint,
            #         "keys": subscription.keys
            #     },
            #     data=json.dumps(notification_data),
            #     vapid_private_key=self.vapid_private_key,
            #     vapid_claims={
            #         "sub": self.vapid_subject
            #     },
            #     ttl=payload.ttl,
            #     urgency=payload.urgency.value
            # )

            # Simulated success
            subscription.last_used = datetime.now()

            # Log notification
            self.sent_notifications.append(
                {
                    "endpoint": subscription.endpoint,
                    "user_id": subscription.user_id,
                    "payload": notification_data,
                    "sent_at": datetime.now(),
                    "status": "sent",
                }
            )

            print(f"[Push] Sent to {subscription.endpoint[:50]}...: {payload.title}")
            return True

        except Exception as e:
            print(f"Failed to send push notification: {e}")
            self.sent_notifications.append(
                {
                    "endpoint": subscription.endpoint,
                    "user_id": subscription.user_id,
                    "payload": payload.title,
                    "sent_at": datetime.now(),
                    "status": "failed",
                    "error": str(e),
                }
            )
            return False

    def send_to_user(self, user_id: int, payload: NotificationPayload) -> int:
        """Send notification to all user's subscriptions"""
        subscriptions = self.get_subscriptions_for_user(user_id)
        success_count = 0

        for subscription in subscriptions:
            if self.send_notification(subscription, payload):
                success_count += 1

        return success_count

    def broadcast(self, payload: NotificationPayload) -> int:
        """Send notification to all subscriptions"""
        success_count = 0

        for subscription in self.subscriptions.values():
            if self.send_notification(subscription, payload):
                success_count += 1

        return success_count

    def get_statistics(self) -> Dict[str, Any]:
        """Get push notification statistics"""
        total = len(self.sent_notifications)
        if total == 0:
            return {
                "total": 0,
                "sent": 0,
                "failed": 0,
                "success_rate": 0.0,
                "active_subscriptions": len(self.subscriptions),
            }

        sent = len([n for n in self.sent_notifications if n["status"] == "sent"])
        failed = len([n for n in self.sent_notifications if n["status"] == "failed"])

        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "success_rate": (sent / total * 100) if total > 0 else 0.0,
            "active_subscriptions": len(self.subscriptions),
        }

    # Convenience methods for common notifications

    def notify_service_created(self, user_id: int, service_name: str, region: str):
        """Notify about new service"""
        payload = NotificationPayload(
            title="New Service Created",
            body=f"Service '{service_name}' created in {region}",
            icon="/static/img/service-icon.png",
            tag="service_created",
            data={"type": "service_created", "service_name": service_name},
            actions=[{"action": "view", "title": "View Service"}, {"action": "dismiss", "title": "Dismiss"}],
        )
        return self.send_to_user(user_id, payload)

    def notify_approval_required(self, user_id: int, item_name: str):
        """Notify about approval requirement"""
        payload = NotificationPayload(
            title="Approval Required",
            body=f"Please review and approve: {item_name}",
            icon="/static/img/approval-icon.png",
            tag="approval_required",
            data={"type": "approval_required", "item": item_name},
            urgency=NotificationUrgency.HIGH,
            require_interaction=True,
            actions=[{"action": "view", "title": "Review"}, {"action": "dismiss", "title": "Later"}],
        )
        return self.send_to_user(user_id, payload)

    def notify_document_ready(self, user_id: int, doc_name: str):
        """Notify that document is ready"""
        payload = NotificationPayload(
            title="Document Ready",
            body=f"Your document '{doc_name}' is ready for download",
            icon="/static/img/document-icon.png",
            tag="document_ready",
            data={"type": "document_ready", "document": doc_name},
            actions=[{"action": "open", "title": "Download"}, {"action": "dismiss", "title": "Later"}],
        )
        return self.send_to_user(user_id, payload)

    def notify_system_alert(self, message: str, urgency: NotificationUrgency = NotificationUrgency.NORMAL):
        """Broadcast system alert to all users"""
        payload = NotificationPayload(
            title="System Alert",
            body=message,
            icon="/static/img/alert-icon.png",
            tag="system_alert",
            data={"type": "system_alert"},
            urgency=urgency,
            require_interaction=(urgency == NotificationUrgency.HIGH),
        )
        return self.broadcast(payload)

    def notify_task_completed(self, user_id: int, task_name: str, success: bool = True):
        """Notify about task completion"""
        payload = NotificationPayload(
            title="Task Completed" if success else "Task Failed",
            body=f"{task_name} {'completed successfully' if success else 'failed'}",
            icon="/static/img/task-icon.png",
            tag="task_completed",
            data={"type": "task_completed", "task": task_name, "success": success},
        )
        return self.send_to_user(user_id, payload)

    def notify_reminder(self, user_id: int, message: str):
        """Send reminder notification"""
        payload = NotificationPayload(
            title="Reminder",
            body=message,
            icon="/static/img/reminder-icon.png",
            tag="reminder",
            data={"type": "reminder"},
            require_interaction=True,
        )
        return self.send_to_user(user_id, payload)


# Service Worker JavaScript code
SERVICE_WORKER_JS = """
// service-worker.js
self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();

        const options = {
            body: data.body,
            icon: data.icon || '/static/img/icon-192x192.png',
            badge: data.badge || '/static/img/badge-72x72.png',
            data: data.data || {},
            actions: data.actions || [],
            tag: data.tag || 'notification',
            requireInteraction: data.requireInteraction || false,
            silent: data.silent || false
        };

        if (data.image) {
            options.image = data.image;
        }

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    const action = event.action;
    const data = event.notification.data;

    if (action === 'view' || action === 'open') {
        // Open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    } else if (action === 'dismiss') {
        // Just close
        return;
    } else {
        // Default action - open app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
"""

# Client-side subscription JavaScript
SUBSCRIPTION_JS = """
// push-subscription.js
async function subscribeToPush() {
    try {
        // Register service worker
        const registration = await navigator.serviceWorker.register('/service-worker.js');

        // Wait for service worker to be ready
        await navigator.serviceWorker.ready;

        // Get VAPID public key from server
        const response = await fetch('/api/push/public-key');
        const {publicKey} = await response.json();

        // Subscribe
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicKey)
        });

        // Send subscription to server
        await fetch('/api/push/subscribe', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(subscription)
        });

        console.log('Subscribed to push notifications');
        return true;
    } catch (error) {
        console.error('Failed to subscribe to push notifications:', error);
        return false;
    }
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Request permission and subscribe
if ('serviceWorker' in navigator && 'PushManager' in window) {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            subscribeToPush();
        }
    });
}
"""


# Global instance
_push_manager: Optional[WebPushManager] = None


def get_push_manager() -> WebPushManager:
    """Get global push manager instance"""
    global _push_manager

    if _push_manager is None:
        _push_manager = WebPushManager()

    return _push_manager


def configure_push_manager(
    vapid_private_key: str, vapid_public_key: str, vapid_subject: str = "mailto:admin@example.com"
):
    """Configure push manager"""
    global _push_manager
    _push_manager = WebPushManager(vapid_private_key, vapid_public_key, vapid_subject)
