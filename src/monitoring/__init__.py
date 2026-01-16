"""
Monitoring and metrics collection module for DMS.

This module provides Prometheus metrics exporter, alerting system,
and monitoring utilities.
"""

from .prometheus_exporter import (
    PrometheusExporter,
    MetricsRegistry,
    track_request_duration,
    track_document_processing,
    track_database_query,
    track_cache_hit,
    get_metrics_handler,
)

from .alerting import (
    AlertManager,
    Alert,
    Silence,
    AlertSeverity,
    AlertComponent,
    setup_alerting,
    send_alert,
    send_critical,
    send_warning,
)

__all__ = [
    # Metrics
    "PrometheusExporter",
    "MetricsRegistry",
    "track_request_duration",
    "track_document_processing",
    "track_database_query",
    "track_cache_hit",
    "get_metrics_handler",
    # Alerting
    "AlertManager",
    "Alert",
    "Silence",
    "AlertSeverity",
    "AlertComponent",
    "setup_alerting",
    "send_alert",
    "send_critical",
    "send_warning",
]
