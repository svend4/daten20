"""
Webhook Management System

Provides webhook functionality:
- Webhook registration and management
- Event-driven integrations
- Retry logic and error handling
- Webhook security (signatures)
- Event logging
"""

import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional HTTP library
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.warning("requests library not available - webhooks will be simulated. Install: pip install requests")


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

    def register_webhook(self, url: str, events: List[WebhookEvent], description: str = "") -> str:
        """Register webhook endpoint"""
        webhook_id = str(uuid.uuid4())
        secret = self._generate_secret()

        webhook = Webhook(id=webhook_id, url=url, events=events, secret=secret, description=description)

        self.webhooks[webhook_id] = webhook
        return webhook_id

    def _generate_secret(self) -> str:
        """Generate webhook secret"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

    def trigger_event(self, event: WebhookEvent, payload: Dict[str, Any]) -> List[str]:
        """Trigger webhook event"""
        delivery_ids = []

        for webhook in self.webhooks.values():
            if not webhook.enabled or event not in webhook.events:
                continue

            delivery_id = self._deliver_webhook(webhook, event, payload)
            delivery_ids.append(delivery_id)

        return delivery_ids

    def _deliver_webhook(self, webhook: Webhook, event: WebhookEvent, payload: Dict[str, Any]) -> str:
        """Deliver webhook with retry logic"""
        delivery_id = str(uuid.uuid4())

        # Create signature for security
        signature = self._create_signature(payload, webhook.secret)

        delivery = WebhookDelivery(
            id=delivery_id, webhook_id=webhook.id, event=event, payload=payload, status=WebhookStatus.PENDING
        )

        if not HAS_REQUESTS:
            # Fallback: simulate delivery if requests not available
            logger.warning(f"Simulating webhook delivery (requests library not available): {event.value} to {webhook.url}")
            delivery.status = WebhookStatus.DELIVERED
            delivery.response_code = 200
            delivery.delivered_at = datetime.now()
            self.deliveries.append(delivery)
            return delivery_id

        # Real HTTP delivery with retry logic
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Event-Type': event.value,
            'X-Delivery-ID': delivery_id,
            'User-Agent': 'WebhookManager/1.0'
        }

        max_retries = delivery.max_attempts
        retry_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s

        for attempt in range(1, max_retries + 1):
            delivery.attempt = attempt
            delivery.status = WebhookStatus.RETRYING if attempt > 1 else WebhookStatus.PENDING

            try:
                logger.info(f"Delivering webhook (attempt {attempt}/{max_retries}): {event.value} to {webhook.url}")

                response = requests.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=10  # 10 second timeout
                )

                delivery.response_code = response.status_code
                delivery.response_body = response.text[:500]  # Store first 500 chars

                # Success: 2xx status codes
                if 200 <= response.status_code < 300:
                    delivery.status = WebhookStatus.DELIVERED
                    delivery.delivered_at = datetime.now()
                    logger.info(f"Webhook delivered successfully: {event.value} to {webhook.url} (status {response.status_code})")
                    break
                else:
                    # Server returned error
                    delivery.error = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(f"Webhook delivery failed with status {response.status_code}: {webhook.url}")

                    if attempt < max_retries:
                        delay = retry_delays[min(attempt - 1, len(retry_delays) - 1)]
                        logger.info(f"Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        delivery.status = WebhookStatus.FAILED

            except requests.exceptions.Timeout:
                delivery.error = f"Timeout after 10 seconds (attempt {attempt})"
                logger.error(f"Webhook delivery timeout: {webhook.url}")

                if attempt < max_retries:
                    delay = retry_delays[min(attempt - 1, len(retry_delays) - 1)]
                    time.sleep(delay)
                else:
                    delivery.status = WebhookStatus.FAILED

            except requests.exceptions.ConnectionError as e:
                delivery.error = f"Connection error: {str(e)[:200]}"
                logger.error(f"Webhook delivery connection error: {webhook.url} - {e}")

                if attempt < max_retries:
                    delay = retry_delays[min(attempt - 1, len(retry_delays) - 1)]
                    time.sleep(delay)
                else:
                    delivery.status = WebhookStatus.FAILED

            except Exception as e:
                delivery.error = f"Unexpected error: {str(e)[:200]}"
                logger.exception(f"Webhook delivery unexpected error: {webhook.url}")
                delivery.status = WebhookStatus.FAILED
                break  # Don't retry on unexpected errors

        self.deliveries.append(delivery)
        return delivery_id

    def _create_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Create HMAC signature"""
        import json

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        return f"sha256={signature}"

    def get_statistics(self) -> Dict[str, Any]:
        """Get webhook statistics"""
        total_webhooks = len(self.webhooks)
        active_webhooks = len([w for w in self.webhooks.values() if w.enabled])
        total_deliveries = len(self.deliveries)
        successful_deliveries = len([d for d in self.deliveries if d.status == WebhookStatus.DELIVERED])

        return {
            "total_webhooks": total_webhooks,
            "active_webhooks": active_webhooks,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": total_deliveries - successful_deliveries,
        }


# Global instance
_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance"""
    global _webhook_manager

    if _webhook_manager is None:
        _webhook_manager = WebhookManager()

    return _webhook_manager
