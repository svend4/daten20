"""
Monitoring and Metrics Module

Provides Prometheus metrics export and system monitoring.
"""

import logging
import time
from functools import wraps

import psutil
from flask import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

logger = logging.getLogger("dms.monitoring")


# Define metrics
REQUEST_COUNT = Counter("dms_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])

REQUEST_DURATION = Histogram("dms_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"])

ACTIVE_USERS = Gauge("dms_active_users", "Number of currently active users")

DATABASE_CONNECTIONS = Gauge("dms_database_connections", "Number of active database connections")

CACHE_HITS = Counter("dms_cache_hits_total", "Total cache hits")

CACHE_MISSES = Counter("dms_cache_misses_total", "Total cache misses")

CPU_USAGE = Gauge("dms_cpu_usage_percent", "CPU usage percentage")

MEMORY_USAGE = Gauge("dms_memory_usage_bytes", "Memory usage in bytes")


def track_request_metrics(func):
    """Decorator to track request metrics."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            response = func(*args, **kwargs)
            status = response.status_code if hasattr(response, "status_code") else 200

            duration = time.time() - start_time

            # Record metrics
            from flask import request

            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint or "unknown", status=status).inc()

            REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint or "unknown").observe(duration)

            return response

        except Exception as e:
            REQUEST_COUNT.labels(
                method=request.method if "request" in dir() else "unknown",
                endpoint=request.endpoint if "request" in dir() and hasattr(request, "endpoint") else "unknown",
                status=500,
            ).inc()
            raise

    return wrapper


def update_system_metrics():
    """Update system-level metrics."""
    try:
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().used)
    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")


def metrics_endpoint():
    """Prometheus metrics endpoint."""
    update_system_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


class MonitoringService:
    """
    Monitoring service for tracking system metrics and performance.

    Provides a centralized interface for Prometheus metrics and system monitoring.
    """

    def __init__(self):
        """Initialize monitoring service"""
        self.logger = logging.getLogger("dms.monitoring")

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def track_cache_hit(self):
        """Record cache hit"""
        CACHE_HITS.inc()

    def track_cache_miss(self):
        """Record cache miss"""
        CACHE_MISSES.inc()

    def set_active_users(self, count: int):
        """Set number of active users"""
        ACTIVE_USERS.set(count)

    def set_database_connections(self, count: int):
        """Set number of active database connections"""
        DATABASE_CONNECTIONS.set(count)

    def update_system_metrics(self):
        """Update system-level metrics (CPU, memory)"""
        update_system_metrics()

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        self.update_system_metrics()
        return generate_latest().decode('utf-8')

    def get_metrics_endpoint(self):
        """Get Flask Response for metrics endpoint"""
        return metrics_endpoint()
