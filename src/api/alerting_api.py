"""
REST API for Enhanced Alerting System.

This module provides REST API endpoints for managing alerts, alert rules,
and notification channels.

Endpoints:
- POST /api/alerts/rules - Create alert rule
- GET /api/alerts/rules - List all rules
- GET /api/alerts/rules/<rule_id> - Get specific rule
- PUT /api/alerts/rules/<rule_id> - Update rule
- DELETE /api/alerts/rules/<rule_id> - Delete rule
- POST /api/alerts/rules/<rule_id>/enable - Enable rule
- POST /api/alerts/rules/<rule_id>/disable - Disable rule
- GET /api/alerts - List all alerts
- GET /api/alerts/active - List active alerts
- GET /api/alerts/<alert_id> - Get specific alert
- POST /api/alerts/<alert_id>/acknowledge - Acknowledge alert
- POST /api/alerts/<alert_id>/resolve - Resolve alert
- GET /api/alerts/statistics - Get alert statistics
- GET /api/alerts/history - Get alert history
- POST /api/alerts/channels/email - Configure email channel
- POST /api/alerts/channels/slack - Configure Slack channel
- POST /api/alerts/channels/webhook - Configure webhook channel
- POST /api/alerts/check - Manually check metric against rules
- GET /api/alerts/health - Health check

Author: DMS Team
Date: 2026-01-18
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging
import time

from src.monitoring.enhanced_alerting import (
    EnhancedAlertManager,
    AlertRule,
    Alert,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    ThresholdOperator,
    EmailConfig,
    SlackConfig,
    WebhookConfig,
    get_alert_manager
)

logger = logging.getLogger(__name__)

# Create Blueprint
alerting_bp = Blueprint('alerting', __name__, url_prefix='/api/alerts')

# Global alert manager
alert_manager: EnhancedAlertManager = None


def get_manager() -> EnhancedAlertManager:
    """Get or create alert manager instance."""
    global alert_manager
    if alert_manager is None:
        alert_manager = get_alert_manager()
    return alert_manager


# ==================== HELPER FUNCTIONS ====================

def parse_severity(severity_str: str) -> AlertSeverity:
    """Parse severity string to enum."""
    severity_map = {
        'critical': AlertSeverity.CRITICAL,
        'error': AlertSeverity.ERROR,
        'warning': AlertSeverity.WARNING,
        'info': AlertSeverity.INFO
    }
    return severity_map.get(severity_str.lower(), AlertSeverity.INFO)


def parse_operator(operator_str: str) -> ThresholdOperator:
    """Parse operator string to enum."""
    operator_map = {
        'gt': ThresholdOperator.GT,
        'gte': ThresholdOperator.GTE,
        'lt': ThresholdOperator.LT,
        'lte': ThresholdOperator.LTE,
        'eq': ThresholdOperator.EQ,
        'neq': ThresholdOperator.NEQ
    }
    return operator_map.get(operator_str.lower(), ThresholdOperator.GT)


def parse_channels(channels_list: list) -> list:
    """Parse channel strings to enums."""
    channel_map = {
        'email': NotificationChannel.EMAIL,
        'slack': NotificationChannel.SLACK,
        'webhook': NotificationChannel.WEBHOOK,
        'console': NotificationChannel.CONSOLE,
        'alertmanager': NotificationChannel.ALERTMANAGER
    }
    return [channel_map[c.lower()] for c in channels_list if c.lower() in channel_map]


def rule_to_dict(rule: AlertRule) -> Dict[str, Any]:
    """Convert AlertRule to dictionary."""
    return {
        'id': rule.id,
        'name': rule.name,
        'description': rule.description,
        'metric_name': rule.metric_name,
        'threshold': rule.threshold,
        'operator': rule.operator.value,
        'severity': rule.severity.value,
        'enabled': rule.enabled,
        'channels': [c.value for c in rule.channels],
        'check_interval': rule.check_interval,
        'cooldown_period': rule.cooldown_period,
        'tags': rule.tags,
        'last_triggered': rule.last_triggered
    }


# ==================== ALERT RULES ENDPOINTS ====================

@alerting_bp.route('/rules', methods=['POST'])
def create_rule():
    """
    Create new alert rule.

    Request JSON:
    {
        "id": "high_cpu",
        "name": "High CPU Usage",
        "description": "CPU usage exceeded threshold",
        "metric_name": "cpu_usage",
        "threshold": 85.0,
        "operator": "gt",
        "severity": "warning",
        "channels": ["email", "slack"],
        "check_interval": 60,
        "cooldown_period": 300,
        "tags": {"environment": "production"}
    }

    Returns:
        201: Rule created successfully
        400: Invalid request data
        409: Rule with this ID already exists
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['id', 'name', 'metric_name', 'threshold', 'operator', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if rule already exists
        manager = get_manager()
        if manager.get_rule(data['id']):
            return jsonify({'error': 'Rule with this ID already exists'}), 409

        # Create rule
        rule = AlertRule(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            metric_name=data['metric_name'],
            threshold=float(data['threshold']),
            operator=parse_operator(data['operator']),
            severity=parse_severity(data['severity']),
            enabled=data.get('enabled', True),
            channels=parse_channels(data.get('channels', [])),
            check_interval=data.get('check_interval', 60),
            cooldown_period=data.get('cooldown_period', 300),
            tags=data.get('tags', {})
        )

        # Add rule
        manager.add_rule(rule)

        return jsonify({
            'message': 'Rule created successfully',
            'rule': rule_to_dict(rule)
        }), 201

    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/rules', methods=['GET'])
def list_rules():
    """
    List all alert rules.

    Query Parameters:
        enabled: Filter by enabled status (true/false)
        severity: Filter by severity (critical/error/warning/info)

    Returns:
        200: List of rules
    """
    try:
        manager = get_manager()
        rules = manager.get_all_rules()

        # Apply filters
        enabled_filter = request.args.get('enabled')
        if enabled_filter is not None:
            enabled = enabled_filter.lower() == 'true'
            rules = [r for r in rules if r.enabled == enabled]

        severity_filter = request.args.get('severity')
        if severity_filter:
            severity = parse_severity(severity_filter)
            rules = [r for r in rules if r.severity == severity]

        return jsonify({
            'count': len(rules),
            'rules': [rule_to_dict(r) for r in rules]
        }), 200

    except Exception as e:
        logger.error(f"Error listing rules: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/rules/<rule_id>', methods=['GET'])
def get_rule(rule_id: str):
    """
    Get specific alert rule.

    Returns:
        200: Rule details
        404: Rule not found
    """
    try:
        manager = get_manager()
        rule = manager.get_rule(rule_id)

        if not rule:
            return jsonify({'error': 'Rule not found'}), 404

        return jsonify(rule_to_dict(rule)), 200

    except Exception as e:
        logger.error(f"Error getting rule: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id: str):
    """
    Update alert rule.

    Returns:
        200: Rule updated successfully
        404: Rule not found
        400: Invalid request data
    """
    try:
        manager = get_manager()
        existing_rule = manager.get_rule(rule_id)

        if not existing_rule:
            return jsonify({'error': 'Rule not found'}), 404

        data = request.get_json()

        # Update rule fields
        updated_rule = AlertRule(
            id=rule_id,
            name=data.get('name', existing_rule.name),
            description=data.get('description', existing_rule.description),
            metric_name=data.get('metric_name', existing_rule.metric_name),
            threshold=float(data.get('threshold', existing_rule.threshold)),
            operator=parse_operator(data.get('operator', existing_rule.operator.value)),
            severity=parse_severity(data.get('severity', existing_rule.severity.value)),
            enabled=data.get('enabled', existing_rule.enabled),
            channels=parse_channels(data.get('channels', [c.value for c in existing_rule.channels])),
            check_interval=data.get('check_interval', existing_rule.check_interval),
            cooldown_period=data.get('cooldown_period', existing_rule.cooldown_period),
            tags=data.get('tags', existing_rule.tags),
            last_triggered=existing_rule.last_triggered
        )

        manager.update_rule(updated_rule)

        return jsonify({
            'message': 'Rule updated successfully',
            'rule': rule_to_dict(updated_rule)
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error updating rule: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id: str):
    """
    Delete alert rule.

    Returns:
        200: Rule deleted successfully
        404: Rule not found
    """
    try:
        manager = get_manager()
        success = manager.remove_rule(rule_id)

        if not success:
            return jsonify({'error': 'Rule not found'}), 404

        return jsonify({'message': 'Rule deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/rules/<rule_id>/enable', methods=['POST'])
def enable_rule(rule_id: str):
    """Enable alert rule."""
    try:
        manager = get_manager()
        success = manager.enable_rule(rule_id)

        if not success:
            return jsonify({'error': 'Rule not found'}), 404

        return jsonify({'message': 'Rule enabled successfully'}), 200

    except Exception as e:
        logger.error(f"Error enabling rule: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/rules/<rule_id>/disable', methods=['POST'])
def disable_rule(rule_id: str):
    """Disable alert rule."""
    try:
        manager = get_manager()
        success = manager.disable_rule(rule_id)

        if not success:
            return jsonify({'error': 'Rule not found'}), 404

        return jsonify({'message': 'Rule disabled successfully'}), 200

    except Exception as e:
        logger.error(f"Error disabling rule: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ==================== ALERTS ENDPOINTS ====================

@alerting_bp.route('/', methods=['GET'])
def list_alerts():
    """
    List all alerts.

    Query Parameters:
        status: Filter by status (active/resolved/acknowledged/silenced)
        severity: Filter by severity (critical/error/warning/info)
        limit: Maximum number of results (default: 100)

    Returns:
        200: List of alerts
    """
    try:
        manager = get_manager()
        alerts = list(manager.alerts.values())

        # Apply filters
        status_filter = request.args.get('status')
        if status_filter:
            status = AlertStatus(status_filter.lower())
            alerts = [a for a in alerts if a.status == status]

        severity_filter = request.args.get('severity')
        if severity_filter:
            severity = parse_severity(severity_filter)
            alerts = [a for a in alerts if a.severity == severity]

        # Limit results
        limit = int(request.args.get('limit', 100))
        alerts = alerts[-limit:]

        return jsonify({
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts]
        }), 200

    except Exception as e:
        logger.error(f"Error listing alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/active', methods=['GET'])
def list_active_alerts():
    """
    List active alerts.

    Returns:
        200: List of active alerts
    """
    try:
        manager = get_manager()
        alerts = manager.get_active_alerts()

        return jsonify({
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts]
        }), 200

    except Exception as e:
        logger.error(f"Error listing active alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/<alert_id>', methods=['GET'])
def get_alert(alert_id: str):
    """
    Get specific alert.

    Returns:
        200: Alert details
        404: Alert not found
    """
    try:
        manager = get_manager()
        alert = manager.get_alert(alert_id)

        if not alert:
            return jsonify({'error': 'Alert not found'}), 404

        return jsonify(alert.to_dict()), 200

    except Exception as e:
        logger.error(f"Error getting alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id: str):
    """
    Acknowledge alert.

    Request JSON:
    {
        "acknowledged_by": "admin"
    }

    Returns:
        200: Alert acknowledged
        404: Alert not found
        400: Invalid request
    """
    try:
        data = request.get_json()
        acknowledged_by = data.get('acknowledged_by', 'unknown')

        manager = get_manager()
        success = manager.acknowledge_alert(alert_id, acknowledged_by)

        if not success:
            return jsonify({'error': 'Alert not found'}), 404

        return jsonify({'message': 'Alert acknowledged successfully'}), 200

    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id: str):
    """
    Resolve alert.

    Returns:
        200: Alert resolved
        404: Alert not found
    """
    try:
        manager = get_manager()
        success = manager.resolve_alert(alert_id)

        if not success:
            return jsonify({'error': 'Alert not found'}), 404

        return jsonify({'message': 'Alert resolved successfully'}), 200

    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get alert statistics.

    Returns:
        200: Alert statistics
    """
    try:
        manager = get_manager()
        stats = manager.get_statistics()

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/history', methods=['GET'])
def get_history():
    """
    Get alert history.

    Query Parameters:
        limit: Maximum number of results (default: 100)

    Returns:
        200: Alert history
    """
    try:
        limit = int(request.args.get('limit', 100))

        manager = get_manager()
        history = manager.get_alert_history(limit=limit)

        return jsonify({
            'count': len(history),
            'alerts': [a.to_dict() for a in history]
        }), 200

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ==================== CHANNEL CONFIGURATION ====================

@alerting_bp.route('/channels/email', methods=['POST'])
def configure_email_channel():
    """
    Configure email notification channel.

    Request JSON:
    {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "alerts@example.com",
        "smtp_password": "password",
        "from_addr": "alerts@example.com",
        "to_addrs": ["admin@example.com"],
        "use_tls": true
    }

    Returns:
        200: Channel configured successfully
        400: Invalid configuration
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'smtp_host' not in data or 'to_addrs' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        config = EmailConfig(
            smtp_host=data['smtp_host'],
            smtp_port=data.get('smtp_port', 587),
            smtp_user=data.get('smtp_user'),
            smtp_password=data.get('smtp_password'),
            from_addr=data.get('from_addr', 'alerts@dms.local'),
            to_addrs=data['to_addrs'],
            use_tls=data.get('use_tls', True)
        )

        manager = get_manager()
        manager.add_email_channel(config)

        return jsonify({'message': 'Email channel configured successfully'}), 200

    except Exception as e:
        logger.error(f"Error configuring email channel: {str(e)}")
        return jsonify({'error': f'Configuration error: {str(e)}'}), 400


@alerting_bp.route('/channels/slack', methods=['POST'])
def configure_slack_channel():
    """
    Configure Slack notification channel.

    Request JSON:
    {
        "webhook_url": "https://hooks.slack.com/services/...",
        "channel": "#alerts",
        "username": "DMS Alerts",
        "icon_emoji": ":warning:"
    }

    Returns:
        200: Channel configured successfully
        400: Invalid configuration
    """
    try:
        data = request.get_json()

        if 'webhook_url' not in data:
            return jsonify({'error': 'Missing webhook_url'}), 400

        config = SlackConfig(
            webhook_url=data['webhook_url'],
            channel=data.get('channel'),
            username=data.get('username', 'DMS Alerts'),
            icon_emoji=data.get('icon_emoji', ':warning:')
        )

        manager = get_manager()
        manager.add_slack_channel(config)

        return jsonify({'message': 'Slack channel configured successfully'}), 200

    except Exception as e:
        logger.error(f"Error configuring Slack channel: {str(e)}")
        return jsonify({'error': f'Configuration error: {str(e)}'}), 400


@alerting_bp.route('/channels/webhook', methods=['POST'])
def configure_webhook_channel():
    """
    Configure webhook notification channel.

    Request JSON:
    {
        "url": "https://example.com/webhook",
        "method": "POST",
        "headers": {"Authorization": "Bearer token"},
        "timeout": 10
    }

    Returns:
        200: Channel configured successfully
        400: Invalid configuration
    """
    try:
        data = request.get_json()

        if 'url' not in data:
            return jsonify({'error': 'Missing url'}), 400

        config = WebhookConfig(
            url=data['url'],
            method=data.get('method', 'POST'),
            headers=data.get('headers', {}),
            timeout=data.get('timeout', 10)
        )

        manager = get_manager()
        manager.add_webhook_channel(config)

        return jsonify({'message': 'Webhook channel configured successfully'}), 200

    except Exception as e:
        logger.error(f"Error configuring webhook channel: {str(e)}")
        return jsonify({'error': f'Configuration error: {str(e)}'}), 400


# ==================== UTILITY ENDPOINTS ====================

@alerting_bp.route('/check', methods=['POST'])
def check_metric():
    """
    Manually check a metric against rules.

    Request JSON:
    {
        "metric_name": "cpu_usage",
        "value": 92.5
    }

    Returns:
        200: Check completed (may have triggered alerts)
        400: Invalid request
    """
    try:
        data = request.get_json()

        if 'metric_name' not in data or 'value' not in data:
            return jsonify({'error': 'Missing metric_name or value'}), 400

        metric_name = data['metric_name']
        value = float(data['value'])

        manager = get_manager()
        manager.check_metric(metric_name, value)

        # Get any alerts that were just triggered
        active_alerts = manager.get_active_alerts()
        recent_alerts = [
            a for a in active_alerts
            if (time.time() - a.timestamp.timestamp()) < 5  # Last 5 seconds
        ]

        return jsonify({
            'message': 'Metric check completed',
            'metric_name': metric_name,
            'value': value,
            'alerts_triggered': len(recent_alerts),
            'new_alerts': [a.to_dict() for a in recent_alerts]
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error checking metric: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@alerting_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        200: Service is healthy
    """
    try:
        manager = get_manager()
        stats = manager.get_statistics()

        return jsonify({
            'status': 'healthy',
            'configured_channels': stats['configured_channels'],
            'total_rules': stats['total_rules'],
            'enabled_rules': stats['enabled_rules'],
            'active_alerts': stats['active_alerts']
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@alerting_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@alerting_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(alerting_bp)

    # Add console channel for testing
    manager = get_manager()
    manager.add_console_channel()

    print("Alerting API server starting...")
    print("Available endpoints:")
    print("  POST   /api/alerts/rules - Create rule")
    print("  GET    /api/alerts/rules - List rules")
    print("  GET    /api/alerts/rules/<id> - Get rule")
    print("  PUT    /api/alerts/rules/<id> - Update rule")
    print("  DELETE /api/alerts/rules/<id> - Delete rule")
    print("  GET    /api/alerts - List alerts")
    print("  GET    /api/alerts/active - List active alerts")
    print("  GET    /api/alerts/statistics - Get statistics")
    print("  POST   /api/alerts/check - Check metric")
    print("  GET    /api/alerts/health - Health check")

    app.run(host='0.0.0.0', port=5002, debug=True)
