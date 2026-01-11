"""
Webhook System

Provides webhook functionality for integrating with external systems.
Supports event-based notifications with retry logic and delivery tracking.
"""

import requests
import json
import time
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
import logging
from threading import Thread
from queue import Queue
import sqlite3

logger = logging.getLogger('dms.webhooks')


class WebhookEvent(str, Enum):
    """Supported webhook events."""
    SERVICE_CREATED = "service.created"
    SERVICE_UPDATED = "service.updated"
    SERVICE_DELETED = "service.deleted"
    DOCUMENT_GENERATED = "document.generated"
    CALCULATION_COMPLETED = "calculation.completed"
    EXPORT_COMPLETED = "export.completed"
    ERROR_OCCURRED = "error.occurred"


class WebhookStatus(str, Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    SENDING = "sending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class WebhookConfig:
    """Configuration for a webhook endpoint."""
    url: str
    events: List[WebhookEvent]
    secret: Optional[str] = None
    enabled: bool = True
    retry_count: int = 3
    timeout: int = 30
    custom_headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class WebhookDelivery:
    """Record of a webhook delivery attempt."""
    id: Optional[int] = None
    webhook_id: int = 0
    event: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    status: WebhookStatus = WebhookStatus.PENDING
    attempt_count: int = 0
    last_attempt: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class WebhookManager:
    """Manage webhook registrations and deliveries."""

    def __init__(self, db_path: str = 'data/db/webhooks.db'):
        """
        Initialize webhook manager.

        Args:
            db_path: Path to webhook database
        """
        self.db_path = db_path
        self.webhooks: Dict[int, WebhookConfig] = {}
        self.delivery_queue = Queue()
        self._init_database()
        self._load_webhooks()
        self._start_delivery_worker()

    def _init_database(self):
        """Initialize webhook database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Webhooks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                events TEXT NOT NULL,
                secret TEXT,
                enabled INTEGER DEFAULT 1,
                retry_count INTEGER DEFAULT 3,
                timeout INTEGER DEFAULT 30,
                custom_headers TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Deliveries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id INTEGER NOT NULL,
                event TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                attempt_count INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                response_code INTEGER,
                response_body TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Webhook database initialized")

    def _load_webhooks(self):
        """Load webhooks from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM webhooks WHERE enabled = 1')
        rows = cursor.fetchall()

        for row in rows:
            webhook = WebhookConfig(
                url=row['url'],
                events=[WebhookEvent(e) for e in json.loads(row['events'])],
                secret=row['secret'],
                enabled=bool(row['enabled']),
                retry_count=row['retry_count'],
                timeout=row['timeout'],
                custom_headers=json.loads(row['custom_headers']) if row['custom_headers'] else {},
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            self.webhooks[row['id']] = webhook

        conn.close()
        logger.info(f"Loaded {len(self.webhooks)} webhooks")

    def register_webhook(self, webhook: WebhookConfig) -> int:
        """
        Register a new webhook.

        Args:
            webhook: Webhook configuration

        Returns:
            Webhook ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO webhooks (url, events, secret, enabled, retry_count, timeout, custom_headers, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            webhook.url,
            json.dumps([e.value for e in webhook.events]),
            webhook.secret,
            int(webhook.enabled),
            webhook.retry_count,
            webhook.timeout,
            json.dumps(webhook.custom_headers),
            json.dumps(webhook.metadata)
        ))

        webhook_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.webhooks[webhook_id] = webhook
        logger.info(f"Registered webhook {webhook_id}: {webhook.url}")

        return webhook_id

    def unregister_webhook(self, webhook_id: int):
        """
        Unregister a webhook.

        Args:
            webhook_id: Webhook ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('UPDATE webhooks SET enabled = 0 WHERE id = ?', (webhook_id,))
        conn.commit()
        conn.close()

        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]

        logger.info(f"Unregistered webhook {webhook_id}")

    def trigger_event(self, event: WebhookEvent, payload: Dict[str, Any]):
        """
        Trigger a webhook event.

        Args:
            event: Event type
            payload: Event payload
        """
        # Find webhooks listening for this event
        matching_webhooks = [
            (wh_id, wh_config)
            for wh_id, wh_config in self.webhooks.items()
            if event in wh_config.events and wh_config.enabled
        ]

        if not matching_webhooks:
            logger.debug(f"No webhooks registered for event: {event}")
            return

        # Queue deliveries
        for webhook_id, webhook_config in matching_webhooks:
            delivery = WebhookDelivery(
                webhook_id=webhook_id,
                event=event.value,
                payload=payload
            )

            # Save delivery to database
            delivery_id = self._save_delivery(delivery)
            delivery.id = delivery_id

            # Queue for sending
            self.delivery_queue.put((webhook_id, delivery))

        logger.info(f"Queued {len(matching_webhooks)} webhook deliveries for event: {event}")

    def _save_delivery(self, delivery: WebhookDelivery) -> int:
        """Save delivery record to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO webhook_deliveries (
                webhook_id, event, payload, status, attempt_count,
                last_attempt, response_code, response_body, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            delivery.webhook_id,
            delivery.event,
            json.dumps(delivery.payload),
            delivery.status.value,
            delivery.attempt_count,
            delivery.last_attempt.isoformat() if delivery.last_attempt else None,
            delivery.response_code,
            delivery.response_body,
            delivery.error_message
        ))

        delivery_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return delivery_id

    def _update_delivery(self, delivery: WebhookDelivery):
        """Update delivery record in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE webhook_deliveries
            SET status = ?, attempt_count = ?, last_attempt = ?,
                response_code = ?, response_body = ?, error_message = ?
            WHERE id = ?
        ''', (
            delivery.status.value,
            delivery.attempt_count,
            delivery.last_attempt.isoformat() if delivery.last_attempt else None,
            delivery.response_code,
            delivery.response_body,
            delivery.error_message,
            delivery.id
        ))

        conn.commit()
        conn.close()

    def _send_webhook(self, webhook_id: int, delivery: WebhookDelivery) -> bool:
        """
        Send webhook HTTP request.

        Args:
            webhook_id: Webhook ID
            delivery: Delivery record

        Returns:
            True if successful
        """
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            logger.error(f"Webhook {webhook_id} not found")
            return False

        delivery.attempt_count += 1
        delivery.last_attempt = datetime.now()
        delivery.status = WebhookStatus.SENDING

        # Prepare payload
        webhook_payload = {
            'event': delivery.event,
            'timestamp': datetime.now().isoformat(),
            'data': delivery.payload
        }

        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DMS-Webhook/2.1',
            **webhook.custom_headers
        }

        # Add signature if secret is configured
        if webhook.secret:
            signature = self._generate_signature(webhook_payload, webhook.secret)
            headers['X-Webhook-Signature'] = signature

        try:
            # Send request
            response = requests.post(
                webhook.url,
                json=webhook_payload,
                headers=headers,
                timeout=webhook.timeout
            )

            delivery.response_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit size

            # Check if successful
            if 200 <= response.status_code < 300:
                delivery.status = WebhookStatus.SUCCESS
                logger.info(f"Webhook delivered successfully: {webhook_id} -> {webhook.url}")
                return True
            else:
                delivery.status = WebhookStatus.FAILED
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(f"Webhook delivery failed: {webhook_id} -> {webhook.url} ({response.status_code})")
                return False

        except requests.RequestException as e:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = str(e)[:500]
            logger.error(f"Webhook delivery error: {webhook_id} -> {webhook.url}: {e}")
            return False

        finally:
            self._update_delivery(delivery)

    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """
        Generate HMAC signature for webhook payload.

        Args:
            payload: Webhook payload
            secret: Webhook secret

        Returns:
            Hex signature
        """
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return signature

    def _start_delivery_worker(self):
        """Start background worker for webhook delivery."""
        def worker():
            while True:
                try:
                    webhook_id, delivery = self.delivery_queue.get()
                    webhook = self.webhooks.get(webhook_id)

                    if not webhook:
                        continue

                    # Try to send
                    success = self._send_webhook(webhook_id, delivery)

                    # Retry if failed
                    if not success and delivery.attempt_count < webhook.retry_count:
                        # Exponential backoff
                        retry_delay = 2 ** delivery.attempt_count
                        logger.info(f"Retrying webhook {webhook_id} in {retry_delay}s")
                        time.sleep(retry_delay)

                        delivery.status = WebhookStatus.RETRYING
                        self._update_delivery(delivery)
                        self.delivery_queue.put((webhook_id, delivery))

                    self.delivery_queue.task_done()

                except Exception as e:
                    logger.error(f"Webhook delivery worker error: {e}")

        # Start worker thread
        worker_thread = Thread(target=worker, daemon=True)
        worker_thread.start()
        logger.info("Webhook delivery worker started")

    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get webhook delivery statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total deliveries
        cursor.execute('SELECT COUNT(*) FROM webhook_deliveries')
        total = cursor.fetchone()[0]

        # By status
        cursor.execute('SELECT status, COUNT(*) FROM webhook_deliveries GROUP BY status')
        by_status = dict(cursor.fetchall())

        # Recent failures
        cursor.execute('''
            SELECT webhook_id, event, error_message, created_at
            FROM webhook_deliveries
            WHERE status = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (WebhookStatus.FAILED.value,))
        recent_failures = cursor.fetchall()

        conn.close()

        return {
            'total_deliveries': total,
            'by_status': by_status,
            'recent_failures': recent_failures,
            'active_webhooks': len(self.webhooks)
        }


# Global webhook manager instance
_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    """Get or create webhook manager instance."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager
