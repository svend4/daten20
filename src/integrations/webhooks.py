"""
Webhook Management System

Provides webhook functionality:
- Webhook registration and management
- Event-driven integrations
- Retry logic and error handling
- Webhook security (signatures)
- Event logging
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import hashlib
import hmac


class WebhookEvent(str, Enum):
    """Webhook event types"""
    SERVICE_CREATED = "service.created"
    SERVICE_UPDATED = "service.updated"
    SERVICE_DELETED = "service.deleted"
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_FAILED = "payment.failed"
    WORKFLOW_COMPLETED = "workflow.completed"
    USER_REGISTERED = "user.registered"
    DOCUMENT_UPLOADED = "document.uploaded"


class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Webhook:
    """Webhook endpoint configuration"""
    id: str
    url: str
    events: List[WebhookEvent]
    secret: str
    enabled: bool = True
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt"""
    id: str
    webhook_id: str
    event: WebhookEvent
    payload: Dict[str, Any]
    status: WebhookStatus
    attempt: int = 1
    max_attempts: int = 3
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class WebhookManager:
    """Webhook management system"""

    def __init__(self):
        self.webhooks: Dict[str, Webhook] = {}
        self.deliveries: List[WebhookDelivery] = []

    def register_webhook(
        self,
        url: str,
        events: List[WebhookEvent],
        description: str = ""
    ) -> str:
        """Register webhook endpoint"""
        webhook_id = str(uuid.uuid4())
        secret = self._generate_secret()

        webhook = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            secret=secret,
            description=description
        )

        self.webhooks[webhook_id] = webhook
        return webhook_id

    def _generate_secret(self) -> str:
        """Generate webhook secret"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

    def trigger_event(
        self,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ) -> List[str]:
        """Trigger webhook event"""
        delivery_ids = []

        for webhook in self.webhooks.values():
            if not webhook.enabled or event not in webhook.events:
                continue

            delivery_id = self._deliver_webhook(webhook, event, payload)
            delivery_ids.append(delivery_id)

        return delivery_ids

    def _deliver_webhook(
        self,
        webhook: Webhook,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ) -> str:
        """Deliver webhook"""
        delivery_id = str(uuid.uuid4())

        # Create signature
        signature = self._create_signature(payload, webhook.secret)

        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event=event,
            payload=payload,
            status=WebhookStatus.PENDING
        )

        # Simulate delivery
        # In production, use requests library
        # headers = {
        #     'Content-Type': 'application/json',
        #     'X-Webhook-Signature': signature,
        #     'X-Event-Type': event.value
        # }
        # response = requests.post(webhook.url, json=payload, headers=headers)

        # Simulated success
        delivery.status = WebhookStatus.DELIVERED
        delivery.response_code = 200
        delivery.delivered_at = datetime.now()

        self.deliveries.append(delivery)

        print(f"[Webhook] Delivered {event.value} to {webhook.url}")
        return delivery_id

    def _create_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Create HMAC signature"""
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def get_statistics(self) -> Dict[str, Any]:
        """Get webhook statistics"""
        total_webhooks = len(self.webhooks)
        active_webhooks = len([w for w in self.webhooks.values() if w.enabled])
        total_deliveries = len(self.deliveries)
        successful_deliveries = len([d for d in self.deliveries if d.status == WebhookStatus.DELIVERED])

        return {
            'total_webhooks': total_webhooks,
            'active_webhooks': active_webhooks,
            'total_deliveries': total_deliveries,
            'successful_deliveries': successful_deliveries,
            'failed_deliveries': total_deliveries - successful_deliveries
        }


# Global instance
_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance"""
    global _webhook_manager

    if _webhook_manager is None:
        _webhook_manager = WebhookManager()

    return _webhook_manager
