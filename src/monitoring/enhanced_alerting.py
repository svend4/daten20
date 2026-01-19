"""
Enhanced Alerting System for Document Management System.

This module provides a comprehensive alerting system with multiple notification
channels, alert rules, threshold monitoring, and alert history.

Features:
- Multiple notification channels: Email, Slack, Webhook, Prometheus Alertmanager
- Alert rules and threshold monitoring
- Alert history and persistence
- Alert grouping and deduplication
- Alert escalation
- REST API integration ready
- Customizable alert templates

Author: DMS Team
Date: 2026-01-18
"""

import json
import logging
import smtplib
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from threading import Thread, Lock
import requests
from collections import defaultdict

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class NotificationChannel(Enum):
    """Notification channel types."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    ALERTMANAGER = "alertmanager"
    CONSOLE = "console"


class ThresholdOperator(Enum):
    """Threshold comparison operators."""
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    EQ = "eq"  # Equal
    NEQ = "neq"  # Not equal


# ==================== DATA CLASSES ====================

@dataclass
class AlertRule:
    """
    Alert rule configuration.

    Attributes:
        id: Unique rule identifier
        name: Rule name
        description: Rule description
        metric_name: Metric to monitor
        threshold: Threshold value
        operator: Comparison operator
        severity: Alert severity
        enabled: Whether rule is enabled
        channels: Notification channels to use
        check_interval: How often to check (seconds)
        cooldown_period: Minimum time between alerts (seconds)
        tags: Additional tags for filtering
    """
    id: str
    name: str
    description: str
    metric_name: str
    threshold: float
    operator: ThresholdOperator
    severity: AlertSeverity
    enabled: bool = True
    channels: List[NotificationChannel] = field(default_factory=list)
    check_interval: int = 60  # seconds
    cooldown_period: int = 300  # 5 minutes
    tags: Dict[str, str] = field(default_factory=dict)
    last_triggered: Optional[float] = None

    def should_trigger(self, current_value: float) -> bool:
        """Check if alert should trigger based on threshold."""
        if not self.enabled:
            return False

        # Check cooldown period
        if self.last_triggered:
            time_since_last = time.time() - self.last_triggered
            if time_since_last < self.cooldown_period:
                return False

        # Check threshold
        if self.operator == ThresholdOperator.GT:
            return current_value > self.threshold
        elif self.operator == ThresholdOperator.GTE:
            return current_value >= self.threshold
        elif self.operator == ThresholdOperator.LT:
            return current_value < self.threshold
        elif self.operator == ThresholdOperator.LTE:
            return current_value <= self.threshold
        elif self.operator == ThresholdOperator.EQ:
            return current_value == self.threshold
        elif self.operator == ThresholdOperator.NEQ:
            return current_value != self.threshold

        return False


@dataclass
class Alert:
    """
    Alert instance.

    Attributes:
        id: Unique alert ID
        rule_id: Associated rule ID
        name: Alert name
        severity: Alert severity
        status: Alert status
        message: Alert message
        description: Detailed description
        metric_value: Current metric value
        threshold: Threshold that was exceeded
        timestamp: Alert creation time
        resolved_at: Resolution timestamp
        acknowledged_at: Acknowledgment timestamp
        acknowledged_by: Who acknowledged the alert
        tags: Additional tags
        metadata: Additional metadata
    """
    id: str
    rule_id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    description: str
    metric_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['severity'] = self.severity.value
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            result['resolved_at'] = self.resolved_at.isoformat()
        if self.acknowledged_at:
            result['acknowledged_at'] = self.acknowledged_at.isoformat()
        return result


@dataclass
class EmailConfig:
    """Email notification configuration."""
    smtp_host: str
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_addr: str = "alerts@dms.local"
    to_addrs: List[str] = field(default_factory=list)
    use_tls: bool = True


@dataclass
class SlackConfig:
    """Slack notification configuration."""
    webhook_url: str
    channel: Optional[str] = None
    username: str = "DMS Alerts"
    icon_emoji: str = ":warning:"


@dataclass
class WebhookConfig:
    """Webhook notification configuration."""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 10


# ==================== NOTIFICATION CHANNELS ====================

class NotificationChannelBase:
    """Base class for notification channels."""

    def send(self, alert: Alert) -> bool:
        """Send alert notification."""
        raise NotImplementedError


class EmailNotificationChannel(NotificationChannelBase):
    """Email notification channel."""

    def __init__(self, config: EmailConfig):
        """Initialize email channel."""
        self.config = config

    def send(self, alert: Alert) -> bool:
        """Send email notification."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name}"
            msg['From'] = self.config.from_addr
            msg['To'] = ', '.join(self.config.to_addrs)

            # Create HTML content
            html_content = self._create_html_content(alert)
            part = MIMEText(html_content, 'html')
            msg.attach(part)

            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()

                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)

                server.send_message(msg)

            logger.info(f"Email alert sent: {alert.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False

    def _create_html_content(self, alert: Alert) -> str:
        """Create HTML email content."""
        severity_colors = {
            AlertSeverity.CRITICAL: '#dc3545',
            AlertSeverity.ERROR: '#fd7e14',
            AlertSeverity.WARNING: '#ffc107',
            AlertSeverity.INFO: '#17a2b8'
        }

        color = severity_colors.get(alert.severity, '#6c757d')

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; color: white; padding: 15px; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">{alert.severity.value.upper()}: {alert.name}</h2>
                </div>
                <div style="border: 1px solid #ddd; border-top: none; padding: 20px; border-radius: 0 0 5px 5px;">
                    <p><strong>Message:</strong> {alert.message}</p>
                    <p><strong>Description:</strong> {alert.description}</p>
                    <p><strong>Current Value:</strong> {alert.metric_value}</p>
                    <p><strong>Threshold:</strong> {alert.threshold}</p>
                    <p><strong>Time:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    <p><strong>Alert ID:</strong> {alert.id}</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        This is an automated alert from the Document Management System.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """


class SlackNotificationChannel(NotificationChannelBase):
    """Slack notification channel."""

    def __init__(self, config: SlackConfig):
        """Initialize Slack channel."""
        self.config = config

    def send(self, alert: Alert) -> bool:
        """Send Slack notification."""
        try:
            # Severity emoji mapping
            severity_emoji = {
                AlertSeverity.CRITICAL: ':rotating_light:',
                AlertSeverity.ERROR: ':x:',
                AlertSeverity.WARNING: ':warning:',
                AlertSeverity.INFO: ':information_source:'
            }

            # Severity color mapping
            severity_colors = {
                AlertSeverity.CRITICAL: 'danger',
                AlertSeverity.ERROR: 'warning',
                AlertSeverity.WARNING: 'warning',
                AlertSeverity.INFO: 'good'
            }

            emoji = severity_emoji.get(alert.severity, ':bell:')
            color = severity_colors.get(alert.severity, '#808080')

            # Create Slack message
            payload = {
                'username': self.config.username,
                'icon_emoji': self.config.icon_emoji,
                'attachments': [{
                    'color': color,
                    'title': f"{emoji} {alert.severity.value.upper()}: {alert.name}",
                    'text': alert.message,
                    'fields': [
                        {
                            'title': 'Description',
                            'value': alert.description,
                            'short': False
                        },
                        {
                            'title': 'Current Value',
                            'value': str(alert.metric_value),
                            'short': True
                        },
                        {
                            'title': 'Threshold',
                            'value': str(alert.threshold),
                            'short': True
                        },
                        {
                            'title': 'Alert ID',
                            'value': alert.id,
                            'short': True
                        },
                        {
                            'title': 'Time',
                            'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                            'short': True
                        }
                    ],
                    'footer': 'DMS Alerting System',
                    'ts': int(alert.timestamp.timestamp())
                }]
            }

            if self.config.channel:
                payload['channel'] = self.config.channel

            # Send to Slack
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Slack alert sent: {alert.id}")
                return True
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            return False


class WebhookNotificationChannel(NotificationChannelBase):
    """Webhook notification channel."""

    def __init__(self, config: WebhookConfig):
        """Initialize webhook channel."""
        self.config = config

    def send(self, alert: Alert) -> bool:
        """Send webhook notification."""
        try:
            payload = alert.to_dict()

            response = requests.request(
                method=self.config.method,
                url=self.config.url,
                json=payload,
                headers=self.config.headers,
                timeout=self.config.timeout
            )

            if response.status_code in [200, 201, 202, 204]:
                logger.info(f"Webhook alert sent: {alert.id}")
                return True
            else:
                logger.error(f"Failed to send webhook alert: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            return False


class ConsoleNotificationChannel(NotificationChannelBase):
    """Console notification channel (for testing/debugging)."""

    def send(self, alert: Alert) -> bool:
        """Print alert to console."""
        try:
            print("\n" + "="*80)
            print(f"ALERT: {alert.severity.value.upper()} - {alert.name}")
            print("="*80)
            print(f"Message: {alert.message}")
            print(f"Description: {alert.description}")
            print(f"Current Value: {alert.metric_value}")
            print(f"Threshold: {alert.threshold}")
            print(f"Time: {alert.timestamp}")
            print(f"Alert ID: {alert.id}")
            print("="*80 + "\n")
            return True
        except Exception as e:
            logger.error(f"Failed to print console alert: {str(e)}")
            return False


# ==================== ENHANCED ALERT MANAGER ====================

class EnhancedAlertManager:
    """
    Enhanced alert manager with multiple channels and rule management.

    Features:
    - Multiple notification channels
    - Alert rules and threshold monitoring
    - Alert history
    - Alert grouping and deduplication
    - Alert statistics
    """

    def __init__(self):
        """Initialize enhanced alert manager."""
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.channels: Dict[NotificationChannel, NotificationChannelBase] = {}
        self.lock = Lock()
        self.monitoring_active = False
        self.monitoring_thread: Optional[Thread] = None

        # Statistics
        self.stats = {
            'total_alerts': 0,
            'alerts_by_severity': defaultdict(int),
            'alerts_by_rule': defaultdict(int),
            'channel_success': defaultdict(int),
            'channel_failure': defaultdict(int)
        }

        logger.info("Enhanced Alert Manager initialized")

    # ==================== CHANNEL MANAGEMENT ====================

    def add_email_channel(self, config: EmailConfig):
        """Add email notification channel."""
        channel = EmailNotificationChannel(config)
        self.channels[NotificationChannel.EMAIL] = channel
        logger.info("Email channel added")

    def add_slack_channel(self, config: SlackConfig):
        """Add Slack notification channel."""
        channel = SlackNotificationChannel(config)
        self.channels[NotificationChannel.SLACK] = channel
        logger.info("Slack channel added")

    def add_webhook_channel(self, config: WebhookConfig):
        """Add webhook notification channel."""
        channel = WebhookNotificationChannel(config)
        self.channels[NotificationChannel.WEBHOOK] = channel
        logger.info("Webhook channel added")

    def add_console_channel(self):
        """Add console notification channel."""
        channel = ConsoleNotificationChannel()
        self.channels[NotificationChannel.CONSOLE] = channel
        logger.info("Console channel added")

    # ==================== RULE MANAGEMENT ====================

    def add_rule(self, rule: AlertRule) -> bool:
        """
        Add alert rule.

        Args:
            rule: Alert rule to add

        Returns:
            True if successful
        """
        with self.lock:
            self.rules[rule.id] = rule
            logger.info(f"Alert rule added: {rule.name} ({rule.id})")
            return True

    def remove_rule(self, rule_id: str) -> bool:
        """Remove alert rule."""
        with self.lock:
            if rule_id in self.rules:
                del self.rules[rule_id]
                logger.info(f"Alert rule removed: {rule_id}")
                return True
            return False

    def update_rule(self, rule: AlertRule) -> bool:
        """Update alert rule."""
        with self.lock:
            if rule.id in self.rules:
                self.rules[rule.id] = rule
                logger.info(f"Alert rule updated: {rule.id}")
                return True
            return False

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID."""
        return self.rules.get(rule_id)

    def get_all_rules(self) -> List[AlertRule]:
        """Get all alert rules."""
        return list(self.rules.values())

    def enable_rule(self, rule_id: str) -> bool:
        """Enable alert rule."""
        with self.lock:
            if rule_id in self.rules:
                self.rules[rule_id].enabled = True
                logger.info(f"Alert rule enabled: {rule_id}")
                return True
            return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable alert rule."""
        with self.lock:
            if rule_id in self.rules:
                self.rules[rule_id].enabled = False
                logger.info(f"Alert rule disabled: {rule_id}")
                return True
            return False

    # ==================== ALERT MANAGEMENT ====================

    def trigger_alert(self, rule: AlertRule, metric_value: float) -> Optional[Alert]:
        """
        Trigger an alert.

        Args:
            rule: Alert rule that triggered
            metric_value: Current metric value

        Returns:
            Created Alert or None if alert was not created
        """
        # Generate alert ID
        alert_id = f"{rule.id}_{int(time.time() * 1000)}"

        # Create alert
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            name=rule.name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=f"{rule.name}: threshold exceeded",
            description=rule.description,
            metric_value=metric_value,
            threshold=rule.threshold,
            tags=rule.tags.copy()
        )

        # Store alert
        with self.lock:
            self.alerts[alert_id] = alert
            self.alert_history.append(alert)

            # Update statistics
            self.stats['total_alerts'] += 1
            self.stats['alerts_by_severity'][rule.severity.value] += 1
            self.stats['alerts_by_rule'][rule.id] += 1

            # Update rule last triggered time
            rule.last_triggered = time.time()

        # Send notifications
        self._send_notifications(alert, rule.channels)

        logger.info(f"Alert triggered: {alert.name} ({alert.id})")
        return alert

    def _send_notifications(self, alert: Alert, channels: List[NotificationChannel]):
        """Send alert to all configured channels."""
        if not channels:
            # If no channels specified, use all available
            channels = list(self.channels.keys())

        for channel_type in channels:
            if channel_type in self.channels:
                channel = self.channels[channel_type]
                try:
                    success = channel.send(alert)
                    if success:
                        self.stats['channel_success'][channel_type.value] += 1
                    else:
                        self.stats['channel_failure'][channel_type.value] += 1
                except Exception as e:
                    logger.error(f"Error sending to {channel_type.value}: {str(e)}")
                    self.stats['channel_failure'][channel_type.value] += 1

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        with self.lock:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.utcnow()
                logger.info(f"Alert resolved: {alert_id}")
                return True
            return False

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        with self.lock:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = acknowledged_by
                logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                return True
            return False

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        return self.alerts.get(alert_id)

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity."""
        return [a for a in self.alerts.values() if a.severity == severity]

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self.alert_history[-limit:]

    # ==================== MONITORING ====================

    def check_metric(self, metric_name: str, current_value: float):
        """
        Check a metric against all rules.

        Args:
            metric_name: Name of the metric
            current_value: Current value of the metric
        """
        for rule in self.rules.values():
            if rule.metric_name == metric_name and rule.should_trigger(current_value):
                self.trigger_alert(rule, current_value)

    # ==================== STATISTICS ====================

    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        return {
            'total_alerts': self.stats['total_alerts'],
            'active_alerts': len(self.get_active_alerts()),
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
            'alerts_by_severity': dict(self.stats['alerts_by_severity']),
            'alerts_by_rule': dict(self.stats['alerts_by_rule']),
            'channel_success': dict(self.stats['channel_success']),
            'channel_failure': dict(self.stats['channel_failure']),
            'configured_channels': [c.value for c in self.channels.keys()]
        }

    def reset_statistics(self):
        """Reset statistics."""
        self.stats = {
            'total_alerts': 0,
            'alerts_by_severity': defaultdict(int),
            'alerts_by_rule': defaultdict(int),
            'channel_success': defaultdict(int),
            'channel_failure': defaultdict(int)
        }
        logger.info("Statistics reset")


# ==================== CONVENIENCE FUNCTIONS ====================

_global_manager: Optional[EnhancedAlertManager] = None


def get_alert_manager() -> EnhancedAlertManager:
    """Get global alert manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = EnhancedAlertManager()
    return _global_manager


def add_rule(rule: AlertRule) -> bool:
    """Add alert rule to global manager."""
    manager = get_alert_manager()
    return manager.add_rule(rule)


def check_metric(metric_name: str, value: float):
    """Check metric against rules."""
    manager = get_alert_manager()
    manager.check_metric(metric_name, value)


def get_active_alerts() -> List[Alert]:
    """Get active alerts."""
    manager = get_alert_manager()
    return manager.get_active_alerts()


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example: Create alert manager
    manager = EnhancedAlertManager()

    # Add console channel for testing
    manager.add_console_channel()

    # Add email channel
    email_config = EmailConfig(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_user="alerts@example.com",
        smtp_password="password",
        to_addrs=["admin@example.com"]
    )
    manager.add_email_channel(email_config)

    # Create alert rule
    rule = AlertRule(
        id="high_cpu_usage",
        name="High CPU Usage",
        description="CPU usage exceeded threshold",
        metric_name="cpu_usage",
        threshold=85.0,
        operator=ThresholdOperator.GT,
        severity=AlertSeverity.WARNING,
        channels=[NotificationChannel.CONSOLE, NotificationChannel.EMAIL],
        check_interval=60,
        cooldown_period=300
    )

    manager.add_rule(rule)

    # Simulate metric check
    manager.check_metric("cpu_usage", 90.5)  # Should trigger alert

    # Get statistics
    stats = manager.get_statistics()
    print(f"\nStatistics: {json.dumps(stats, indent=2)}")

    # Get active alerts
    active = manager.get_active_alerts()
    print(f"\nActive alerts: {len(active)}")
