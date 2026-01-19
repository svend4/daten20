"""
Alerting System for Document Management System.

This module provides programmatic interface for sending alerts
to Prometheus Alertmanager from Python code.

Features:
- Send alerts programmatically
- Query active alerts
- Silence alerts
- Integration with Flask
- Custom alert templates

Author: DMS Team
Date: 2026-01-16
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertComponent(Enum):
    """System components."""
    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    ML = "ml"
    SECURITY = "security"
    SYSTEM = "system"
    BUSINESS = "business"


@dataclass
class Alert:
    """
    Alert data structure.

    Attributes:
        name: Alert name (e.g., "HighErrorRate")
        severity: Alert severity (critical, warning, info)
        component: System component
        summary: Short description
        description: Detailed description
        instance: Instance identifier (optional)
        additional_labels: Additional labels (optional)
    """
    name: str
    severity: AlertSeverity
    component: AlertComponent
    summary: str
    description: str
    instance: Optional[str] = None
    additional_labels: Optional[Dict[str, str]] = None

    def to_alertmanager_format(self) -> Dict[str, Any]:
        """Convert to Alertmanager API format."""
        alert_dict = {
            "labels": {
                "alertname": self.name,
                "severity": self.severity.value,
                "component": self.component.value,
            },
            "annotations": {
                "summary": self.summary,
                "description": self.description,
            },
            "startsAt": datetime.utcnow().isoformat() + "Z",
        }

        # Add instance label if provided
        if self.instance:
            alert_dict["labels"]["instance"] = self.instance

        # Add additional labels if provided
        if self.additional_labels:
            alert_dict["labels"].update(self.additional_labels)

        return alert_dict


@dataclass
class Silence:
    """
    Silence configuration.

    Attributes:
        matchers: Label matchers (e.g., {"alertname": "HighErrorRate"})
        duration: Silence duration in hours
        comment: Reason for silence
        created_by: Who created the silence
    """
    matchers: Dict[str, str]
    duration: float  # hours
    comment: str
    created_by: str

    def to_alertmanager_format(self) -> Dict[str, Any]:
        """Convert to Alertmanager API format."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=self.duration)

        matchers_list = [
            {
                "name": key,
                "value": value,
                "isRegex": False
            }
            for key, value in self.matchers.items()
        ]

        return {
            "matchers": matchers_list,
            "startsAt": start_time.isoformat() + "Z",
            "endsAt": end_time.isoformat() + "Z",
            "createdBy": self.created_by,
            "comment": self.comment,
        }


class AlertManager:
    """
    Client for Prometheus Alertmanager API.

    This class provides methods to:
    - Send alerts programmatically
    - Query active alerts
    - Create and manage silences
    - Check Alertmanager health
    """

    def __init__(self, alertmanager_url: str = "http://localhost:9093"):
        """
        Initialize AlertManager client.

        Args:
            alertmanager_url: Alertmanager API URL
        """
        self.base_url = alertmanager_url.rstrip('/')
        self.api_v1 = f"{self.base_url}/api/v1"
        self.api_v2 = f"{self.base_url}/api/v2"

    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert to Alertmanager.

        Args:
            alert: Alert to send

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager = AlertManager()
            >>> alert = Alert(
            ...     name="HighErrorRate",
            ...     severity=AlertSeverity.WARNING,
            ...     component=AlertComponent.APPLICATION,
            ...     summary="Error rate is high",
            ...     description="Error rate: 15 errors/sec (threshold: 10)"
            ... )
            >>> manager.send_alert(alert)
            True
        """
        try:
            alert_data = [alert.to_alertmanager_format()]

            response = requests.post(
                f"{self.api_v1}/alerts",
                json=alert_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"Alert '{alert.name}' sent successfully")
                return True
            else:
                logger.error(f"Failed to send alert: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False

    def send_critical_alert(
        self,
        name: str,
        component: AlertComponent,
        summary: str,
        description: str,
        **kwargs
    ) -> bool:
        """
        Send a critical severity alert.

        Args:
            name: Alert name
            component: System component
            summary: Short description
            description: Detailed description
            **kwargs: Additional labels

        Returns:
            True if successful, False otherwise
        """
        alert = Alert(
            name=name,
            severity=AlertSeverity.CRITICAL,
            component=component,
            summary=summary,
            description=description,
            additional_labels=kwargs
        )
        return self.send_alert(alert)

    def send_warning_alert(
        self,
        name: str,
        component: AlertComponent,
        summary: str,
        description: str,
        **kwargs
    ) -> bool:
        """Send a warning severity alert."""
        alert = Alert(
            name=name,
            severity=AlertSeverity.WARNING,
            component=component,
            summary=summary,
            description=description,
            additional_labels=kwargs
        )
        return self.send_alert(alert)

    def get_alerts(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Get active alerts from Alertmanager.

        Args:
            filters: Optional filters (e.g., {"severity": "critical"})

        Returns:
            List of active alerts

        Example:
            >>> manager = AlertManager()
            >>> alerts = manager.get_alerts({"severity": "critical"})
            >>> for alert in alerts:
            ...     print(f"{alert['labels']['alertname']}: {alert['annotations']['summary']}")
        """
        try:
            params = {}
            if filters:
                # Convert filters to Alertmanager query format
                filter_str = ",".join([f'{k}="{v}"' for k, v in filters.items()])
                params['filter'] = f"{{{filter_str}}}"

            response = requests.get(
                f"{self.api_v2}/alerts",
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get alerts: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return []

    def create_silence(self, silence: Silence) -> Optional[str]:
        """
        Create a silence in Alertmanager.

        Args:
            silence: Silence configuration

        Returns:
            Silence ID if successful, None otherwise

        Example:
            >>> manager = AlertManager()
            >>> silence = Silence(
            ...     matchers={"alertname": "HighErrorRate"},
            ...     duration=2.0,  # 2 hours
            ...     comment="Deploying new version",
            ...     created_by="admin"
            ... )
            >>> silence_id = manager.create_silence(silence)
        """
        try:
            silence_data = silence.to_alertmanager_format()

            response = requests.post(
                f"{self.api_v2}/silences",
                json=silence_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code in [200, 201]:
                result = response.json()
                silence_id = result.get('silenceID')
                logger.info(f"Silence created: {silence_id}")
                return silence_id
            else:
                logger.error(f"Failed to create silence: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating silence: {str(e)}")
            return None

    def delete_silence(self, silence_id: str) -> bool:
        """
        Delete a silence.

        Args:
            silence_id: Silence ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.api_v2}/silence/{silence_id}",
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"Silence deleted: {silence_id}")
                return True
            else:
                logger.error(f"Failed to delete silence: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error deleting silence: {str(e)}")
            return False

    def get_silences(self) -> List[Dict[str, Any]]:
        """
        Get all active silences.

        Returns:
            List of active silences
        """
        try:
            response = requests.get(
                f"{self.api_v2}/silences",
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get silences: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error getting silences: {str(e)}")
            return []

    def health_check(self) -> bool:
        """
        Check if Alertmanager is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/-/healthy",
                timeout=5
            )
            return response.status_code == 200

        except Exception:
            return False


# ==================== FLASK INTEGRATION ====================

def setup_alerting(app, alertmanager_url: str = "http://localhost:9093"):
    """
    Setup alerting for Flask application.

    Args:
        app: Flask application
        alertmanager_url: Alertmanager URL

    Example:
        from flask import Flask
        from src.monitoring.alerting import setup_alerting

        app = Flask(__name__)
        setup_alerting(app)
    """
    alert_manager = AlertManager(alertmanager_url)

    # Add alert manager to app context
    app.alert_manager = alert_manager

    # Add error handler to send alerts on unhandled exceptions
    @app.errorhandler(500)
    def handle_500(error):
        alert_manager.send_critical_alert(
            name="UnhandledServerError",
            component=AlertComponent.APPLICATION,
            summary="Unhandled server error occurred",
            description=f"Error: {str(error)}",
            endpoint=error.description if hasattr(error, 'description') else "unknown"
        )
        return "Internal Server Error", 500

    logger.info("Alerting system configured")


# ==================== CONVENIENCE FUNCTIONS ====================

_default_manager: Optional[AlertManager] = None


def get_alert_manager(alertmanager_url: str = "http://localhost:9093") -> AlertManager:
    """Get or create default AlertManager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = AlertManager(alertmanager_url)
    return _default_manager


def send_alert(alert: Alert) -> bool:
    """Send alert using default manager."""
    manager = get_alert_manager()
    return manager.send_alert(alert)


def send_critical(name: str, component: AlertComponent, summary: str, description: str) -> bool:
    """Send critical alert using default manager."""
    manager = get_alert_manager()
    return manager.send_critical_alert(name, component, summary, description)


def send_warning(name: str, component: AlertComponent, summary: str, description: str) -> bool:
    """Send warning alert using default manager."""
    manager = get_alert_manager()
    return manager.send_warning_alert(name, component, summary, description)


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example 1: Send a critical alert
    manager = AlertManager("http://localhost:9093")

    critical_alert = Alert(
        name="DatabaseConnectionFailed",
        severity=AlertSeverity.CRITICAL,
        component=AlertComponent.DATABASE,
        summary="Cannot connect to database",
        description="Database connection failed after 3 retries. PostgreSQL may be down.",
        instance="postgres-1"
    )
    manager.send_alert(critical_alert)

    # Example 2: Send a warning alert (shortcut)
    manager.send_warning_alert(
        name="HighMemoryUsage",
        component=AlertComponent.SYSTEM,
        summary="Memory usage is high",
        description="Memory usage: 87% (threshold: 85%)"
    )

    # Example 3: Get active alerts
    alerts = manager.get_alerts({"severity": "critical"})
    print(f"Active critical alerts: {len(alerts)}")

    # Example 4: Create a silence
    silence = Silence(
        matchers={"alertname": "HighErrorRate"},
        duration=2.0,  # 2 hours
        comment="Deploying new version, errors expected",
        created_by="admin"
    )
    silence_id = manager.create_silence(silence)

    # Example 5: Health check
    is_healthy = manager.health_check()
    print(f"Alertmanager healthy: {is_healthy}")
