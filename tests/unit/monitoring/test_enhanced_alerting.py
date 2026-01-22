"""
Unit tests for Enhanced Alerting System.

This module contains comprehensive unit tests for the enhanced alerting system,
including alert rules, notification channels, and alert management.

Author: DMS Team
Date: 2026-01-18
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
import smtplib
import requests

from src.monitoring.enhanced_alerting import (
    AlertRule,
    Alert,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    ThresholdOperator,
    EmailConfig,
    SlackConfig,
    WebhookConfig,
    EmailNotificationChannel,
    SlackNotificationChannel,
    WebhookNotificationChannel,
    ConsoleNotificationChannel,
    EnhancedAlertManager,
    get_alert_manager
)


# ==================== FIXTURES ====================

@pytest.fixture
def alert_rule():
    """Create sample alert rule."""
    return AlertRule(
        id="test_rule_1",
        name="Test Alert Rule",
        description="Test alert for unit testing",
        metric_name="test_metric",
        threshold=80.0,
        operator=ThresholdOperator.GT,
        severity=AlertSeverity.WARNING,
        enabled=True,
        channels=[NotificationChannel.CONSOLE],
        check_interval=60,
        cooldown_period=300,
        tags={"environment": "test"}
    )


@pytest.fixture
def alert(alert_rule):
    """Create sample alert."""
    return Alert(
        id="alert_1",
        rule_id=alert_rule.id,
        name=alert_rule.name,
        severity=alert_rule.severity,
        status=AlertStatus.ACTIVE,
        message="Test alert message",
        description="Test alert description",
        metric_value=95.0,
        threshold=80.0,
        tags={"test": "true"}
    )


@pytest.fixture
def email_config():
    """Create email configuration."""
    return EmailConfig(
        smtp_host="smtp.test.com",
        smtp_port=587,
        smtp_user="test@test.com",
        smtp_password="password",
        from_addr="alerts@test.com",
        to_addrs=["admin@test.com"],
        use_tls=True
    )


@pytest.fixture
def slack_config():
    """Create Slack configuration."""
    return SlackConfig(
        webhook_url="https://hooks.slack.com/test",
        channel="#alerts",
        username="Test Bot",
        icon_emoji=":robot:"
    )


@pytest.fixture
def webhook_config():
    """Create webhook configuration."""
    return WebhookConfig(
        url="https://example.com/webhook",
        method="POST",
        headers={"Authorization": "Bearer token"},
        timeout=10
    )


@pytest.fixture
def alert_manager():
    """Create fresh alert manager for each test."""
    manager = EnhancedAlertManager()
    manager.add_console_channel()
    return manager


# ==================== TEST DATA CLASSES ====================

class TestAlertRule:
    """Test AlertRule data class."""

    def test_alert_rule_creation(self, alert_rule):
        """Test creating alert rule."""
        assert alert_rule.id == "test_rule_1"
        assert alert_rule.name == "Test Alert Rule"
        assert alert_rule.threshold == 80.0
        assert alert_rule.operator == ThresholdOperator.GT
        assert alert_rule.severity == AlertSeverity.WARNING
        assert alert_rule.enabled is True

    def test_should_trigger_gt(self, alert_rule):
        """Test threshold trigger with GT operator."""
        alert_rule.operator = ThresholdOperator.GT
        alert_rule.threshold = 80.0

        assert alert_rule.should_trigger(85.0) is True
        assert alert_rule.should_trigger(80.0) is False
        assert alert_rule.should_trigger(75.0) is False

    def test_should_trigger_gte(self, alert_rule):
        """Test threshold trigger with GTE operator."""
        alert_rule.operator = ThresholdOperator.GTE
        alert_rule.threshold = 80.0

        assert alert_rule.should_trigger(85.0) is True
        assert alert_rule.should_trigger(80.0) is True
        assert alert_rule.should_trigger(75.0) is False

    def test_should_trigger_lt(self, alert_rule):
        """Test threshold trigger with LT operator."""
        alert_rule.operator = ThresholdOperator.LT
        alert_rule.threshold = 20.0

        assert alert_rule.should_trigger(15.0) is True
        assert alert_rule.should_trigger(20.0) is False
        assert alert_rule.should_trigger(25.0) is False

    def test_should_trigger_disabled_rule(self, alert_rule):
        """Test that disabled rules don't trigger."""
        alert_rule.enabled = False
        assert alert_rule.should_trigger(95.0) is False

    def test_cooldown_period(self, alert_rule):
        """Test cooldown period prevents rapid alerts."""
        alert_rule.cooldown_period = 10  # 10 seconds

        # First trigger should work
        assert alert_rule.should_trigger(85.0) is True
        alert_rule.last_triggered = time.time()

        # Immediate second trigger should fail (cooldown)
        assert alert_rule.should_trigger(85.0) is False

        # After cooldown should work again
        alert_rule.last_triggered = time.time() - 11
        assert alert_rule.should_trigger(85.0) is True


class TestAlert:
    """Test Alert data class."""

    def test_alert_creation(self, alert):
        """Test creating alert."""
        assert alert.id == "alert_1"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.status == AlertStatus.ACTIVE
        assert alert.metric_value == 95.0
        assert alert.threshold == 80.0

    def test_alert_to_dict(self, alert):
        """Test converting alert to dictionary."""
        alert_dict = alert.to_dict()

        assert alert_dict['id'] == alert.id
        assert alert_dict['severity'] == alert.severity.value
        assert alert_dict['status'] == alert.status.value
        assert alert_dict['metric_value'] == alert.metric_value
        assert 'timestamp' in alert_dict


# ==================== TEST NOTIFICATION CHANNELS ====================

class TestEmailNotificationChannel:
    """Test email notification channel."""

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, email_config, alert):
        """Test successful email sending."""
        channel = EmailNotificationChannel(email_config)

        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Send alert
        result = channel.send(alert)

        assert result is True
        mock_server.send_message.assert_called_once()
        assert mock_server.starttls.called
        assert mock_server.login.called

    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, email_config, alert):
        """Test email sending failure."""
        channel = EmailNotificationChannel(email_config)

        # Mock SMTP server to raise exception
        mock_smtp.side_effect = Exception("SMTP error")

        # Send alert
        result = channel.send(alert)

        assert result is False

    def test_create_html_content(self, email_config, alert):
        """Test HTML email content creation."""
        channel = EmailNotificationChannel(email_config)
        html = channel._create_html_content(alert)

        assert alert.name in html
        assert alert.message in html
        assert str(alert.metric_value) in html
        assert "WARNING" in html.upper()


class TestSlackNotificationChannel:
    """Test Slack notification channel."""

    @patch('requests.post')
    def test_send_slack_success(self, mock_post, slack_config, alert):
        """Test successful Slack notification."""
        channel = SlackNotificationChannel(slack_config)

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Send alert
        result = channel.send(alert)

        assert result is True
        mock_post.assert_called_once()

        # Check payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'attachments' in payload
        assert payload['username'] == slack_config.username

    @patch('requests.post')
    def test_send_slack_failure(self, mock_post, slack_config, alert):
        """Test Slack notification failure."""
        channel = SlackNotificationChannel(slack_config)

        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # Send alert
        result = channel.send(alert)

        assert result is False

    @patch('requests.post')
    def test_send_slack_exception(self, mock_post, slack_config, alert):
        """Test Slack notification with exception."""
        channel = SlackNotificationChannel(slack_config)

        # Mock exception
        mock_post.side_effect = Exception("Network error")

        # Send alert
        result = channel.send(alert)

        assert result is False


class TestWebhookNotificationChannel:
    """Test webhook notification channel."""

    @patch('requests.request')
    def test_send_webhook_success(self, mock_request, webhook_config, alert):
        """Test successful webhook notification."""
        channel = WebhookNotificationChannel(webhook_config)

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Send alert
        result = channel.send(alert)

        assert result is True
        mock_request.assert_called_once()

        # Check call parameters
        call_args = mock_request.call_args
        assert call_args[1]['method'] == webhook_config.method
        assert call_args[1]['url'] == webhook_config.url
        assert call_args[1]['headers'] == webhook_config.headers

    @patch('requests.request')
    def test_send_webhook_failure(self, mock_request, webhook_config, alert):
        """Test webhook notification failure."""
        channel = WebhookNotificationChannel(webhook_config)

        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response

        # Send alert
        result = channel.send(alert)

        assert result is False


class TestConsoleNotificationChannel:
    """Test console notification channel."""

    def test_send_console(self, alert, capsys):
        """Test console notification."""
        channel = ConsoleNotificationChannel()

        result = channel.send(alert)

        assert result is True

        # Check console output
        captured = capsys.readouterr()
        assert alert.name in captured.out
        assert alert.message in captured.out


# ==================== TEST ENHANCED ALERT MANAGER ====================

class TestEnhancedAlertManager:
    """Test EnhancedAlertManager."""

    def test_manager_initialization(self, alert_manager):
        """Test manager initialization."""
        assert alert_manager is not None
        assert len(alert_manager.rules) == 0
        assert len(alert_manager.alerts) == 0
        assert NotificationChannel.CONSOLE in alert_manager.channels

    def test_add_channel(self, alert_manager, email_config):
        """Test adding notification channel."""
        alert_manager.add_email_channel(email_config)
        assert NotificationChannel.EMAIL in alert_manager.channels

    def test_add_rule(self, alert_manager, alert_rule):
        """Test adding alert rule."""
        result = alert_manager.add_rule(alert_rule)

        assert result is True
        assert alert_rule.id in alert_manager.rules
        assert alert_manager.get_rule(alert_rule.id) == alert_rule

    def test_remove_rule(self, alert_manager, alert_rule):
        """Test removing alert rule."""
        alert_manager.add_rule(alert_rule)
        result = alert_manager.remove_rule(alert_rule.id)

        assert result is True
        assert alert_rule.id not in alert_manager.rules

    def test_remove_nonexistent_rule(self, alert_manager):
        """Test removing non-existent rule."""
        result = alert_manager.remove_rule("nonexistent")
        assert result is False

    def test_update_rule(self, alert_manager, alert_rule):
        """Test updating alert rule."""
        alert_manager.add_rule(alert_rule)

        # Update rule
        alert_rule.threshold = 90.0
        result = alert_manager.update_rule(alert_rule)

        assert result is True
        updated_rule = alert_manager.get_rule(alert_rule.id)
        assert updated_rule.threshold == 90.0

    def test_enable_disable_rule(self, alert_manager, alert_rule):
        """Test enabling and disabling rules."""
        alert_manager.add_rule(alert_rule)

        # Disable
        result = alert_manager.disable_rule(alert_rule.id)
        assert result is True
        assert alert_manager.get_rule(alert_rule.id).enabled is False

        # Enable
        result = alert_manager.enable_rule(alert_rule.id)
        assert result is True
        assert alert_manager.get_rule(alert_rule.id).enabled is True

    def test_get_all_rules(self, alert_manager):
        """Test getting all rules."""
        # Add multiple rules
        for i in range(3):
            rule = AlertRule(
                id=f"rule_{i}",
                name=f"Rule {i}",
                description="Test",
                metric_name="test",
                threshold=80.0,
                operator=ThresholdOperator.GT,
                severity=AlertSeverity.WARNING
            )
            alert_manager.add_rule(rule)

        rules = alert_manager.get_all_rules()
        assert len(rules) == 3

    def test_trigger_alert(self, alert_manager, alert_rule):
        """Test triggering an alert."""
        alert_manager.add_rule(alert_rule)

        # Trigger alert
        alert = alert_manager.trigger_alert(alert_rule, 95.0)

        assert alert is not None
        assert alert.rule_id == alert_rule.id
        assert alert.metric_value == 95.0
        assert alert.status == AlertStatus.ACTIVE
        assert len(alert_manager.alerts) == 1
        assert alert_manager.stats['total_alerts'] == 1

    def test_check_metric_triggers_alert(self, alert_manager, alert_rule):
        """Test that checking metric triggers alert."""
        alert_manager.add_rule(alert_rule)

        # Check metric above threshold
        alert_manager.check_metric(alert_rule.metric_name, 95.0)

        # Should have triggered alert
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].metric_value == 95.0

    def test_check_metric_no_trigger(self, alert_manager, alert_rule):
        """Test that checking metric below threshold doesn't trigger."""
        alert_manager.add_rule(alert_rule)

        # Check metric below threshold
        alert_manager.check_metric(alert_rule.metric_name, 75.0)

        # Should not have triggered alert
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 0

    def test_resolve_alert(self, alert_manager, alert_rule):
        """Test resolving an alert."""
        alert_manager.add_rule(alert_rule)
        alert = alert_manager.trigger_alert(alert_rule, 95.0)

        # Resolve alert
        result = alert_manager.resolve_alert(alert.id)

        assert result is True
        resolved_alert = alert_manager.get_alert(alert.id)
        assert resolved_alert.status == AlertStatus.RESOLVED
        assert resolved_alert.resolved_at is not None

    def test_acknowledge_alert(self, alert_manager, alert_rule):
        """Test acknowledging an alert."""
        alert_manager.add_rule(alert_rule)
        alert = alert_manager.trigger_alert(alert_rule, 95.0)

        # Acknowledge alert
        result = alert_manager.acknowledge_alert(alert.id, "admin")

        assert result is True
        ack_alert = alert_manager.get_alert(alert.id)
        assert ack_alert.status == AlertStatus.ACKNOWLEDGED
        assert ack_alert.acknowledged_by == "admin"
        assert ack_alert.acknowledged_at is not None

    def test_get_active_alerts(self, alert_manager, alert_rule):
        """Test getting active alerts."""
        alert_manager.add_rule(alert_rule)

        # Trigger multiple alerts
        alert1 = alert_manager.trigger_alert(alert_rule, 85.0)
        time.sleep(0.1)
        alert_rule.last_triggered = None  # Reset cooldown
        alert2 = alert_manager.trigger_alert(alert_rule, 90.0)

        # Resolve one
        alert_manager.resolve_alert(alert1.id)

        # Get active alerts
        active = alert_manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].id == alert2.id

    def test_get_alerts_by_severity(self, alert_manager):
        """Test getting alerts by severity."""
        # Add rules with different severities
        rule1 = AlertRule(
            id="critical_rule",
            name="Critical Rule",
            description="Test",
            metric_name="test",
            threshold=90.0,
            operator=ThresholdOperator.GT,
            severity=AlertSeverity.CRITICAL
        )
        rule2 = AlertRule(
            id="warning_rule",
            name="Warning Rule",
            description="Test",
            metric_name="test2",
            threshold=80.0,
            operator=ThresholdOperator.GT,
            severity=AlertSeverity.WARNING
        )

        alert_manager.add_rule(rule1)
        alert_manager.add_rule(rule2)

        # Trigger alerts
        alert_manager.trigger_alert(rule1, 95.0)
        alert_manager.trigger_alert(rule2, 85.0)

        # Get critical alerts
        critical_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL

    def test_get_alert_history(self, alert_manager, alert_rule):
        """Test getting alert history."""
        alert_manager.add_rule(alert_rule)

        # Trigger multiple alerts
        for i in range(5):
            alert_rule.last_triggered = None  # Reset cooldown
            alert_manager.trigger_alert(alert_rule, 85.0 + i)
            time.sleep(0.01)

        # Get history
        history = alert_manager.get_alert_history(limit=3)
        assert len(history) == 3

    def test_get_statistics(self, alert_manager, alert_rule):
        """Test getting alert statistics."""
        alert_manager.add_rule(alert_rule)
        alert_manager.trigger_alert(alert_rule, 95.0)

        stats = alert_manager.get_statistics()

        assert stats['total_alerts'] == 1
        assert stats['active_alerts'] == 1
        assert stats['total_rules'] == 1
        assert stats['enabled_rules'] == 1
        assert 'alerts_by_severity' in stats
        assert 'channel_success' in stats

    def test_reset_statistics(self, alert_manager, alert_rule):
        """Test resetting statistics."""
        alert_manager.add_rule(alert_rule)
        alert_manager.trigger_alert(alert_rule, 95.0)

        # Reset
        alert_manager.reset_statistics()

        stats = alert_manager.get_statistics()
        assert stats['total_alerts'] == 0

    def test_multiple_channels_notification(self, alert_manager, alert_rule, email_config, slack_config):
        """Test notification through multiple channels."""
        # Add multiple channels
        alert_manager.add_email_channel(email_config)
        alert_manager.add_slack_channel(slack_config)

        # Set rule to use multiple channels
        alert_rule.channels = [NotificationChannel.EMAIL, NotificationChannel.SLACK]
        alert_manager.add_rule(alert_rule)

        # Mock the send methods
        with patch.object(EmailNotificationChannel, 'send', return_value=True):
            with patch.object(SlackNotificationChannel, 'send', return_value=True):
                # Trigger alert
                alert = alert_manager.trigger_alert(alert_rule, 95.0)

                assert alert is not None
                assert alert_manager.stats['channel_success']['email'] >= 1
                assert alert_manager.stats['channel_success']['slack'] >= 1


# ==================== TEST CONVENIENCE FUNCTIONS ====================

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_alert_manager(self):
        """Test getting global alert manager."""
        manager1 = get_alert_manager()
        manager2 = get_alert_manager()

        # Should return same instance
        assert manager1 is manager2


# ==================== TEST EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_alert_rule_with_eq_operator(self):
        """Test alert rule with EQ operator."""
        rule = AlertRule(
            id="eq_test",
            name="Equal Test",
            description="Test",
            metric_name="test",
            threshold=100.0,
            operator=ThresholdOperator.EQ,
            severity=AlertSeverity.INFO
        )

        assert rule.should_trigger(100.0) is True
        assert rule.should_trigger(99.0) is False
        assert rule.should_trigger(101.0) is False

    def test_alert_rule_with_neq_operator(self):
        """Test alert rule with NEQ operator."""
        rule = AlertRule(
            id="neq_test",
            name="Not Equal Test",
            description="Test",
            metric_name="test",
            threshold=0.0,
            operator=ThresholdOperator.NEQ,
            severity=AlertSeverity.INFO
        )

        assert rule.should_trigger(1.0) is True
        assert rule.should_trigger(0.0) is False

    def test_alert_with_empty_tags(self):
        """Test alert with empty tags."""
        alert = Alert(
            id="test",
            rule_id="rule1",
            name="Test",
            severity=AlertSeverity.INFO,
            status=AlertStatus.ACTIVE,
            message="Test",
            description="Test",
            metric_value=50.0,
            threshold=60.0,
            tags={}
        )

        alert_dict = alert.to_dict()
        assert 'tags' in alert_dict
        assert alert_dict['tags'] == {}

    def test_notification_channel_with_invalid_config(self):
        """Test notification channel with minimal config."""
        config = EmailConfig(
            smtp_host="localhost",
            to_addrs=[]  # Empty recipients
        )

        channel = EmailNotificationChannel(config)
        assert channel.config.to_addrs == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
