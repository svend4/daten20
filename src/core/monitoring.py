"""
Monitoring and Metrics Module

Provides Prometheus metrics export and system monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
from functools import wraps
import time
import psutil
import logging

logger = logging.getLogger('dms.monitoring')


# Define metrics
REQUEST_COUNT = Counter(
    'dms_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'dms_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'dms_active_users',
    'Number of currently active users'
)

DATABASE_CONNECTIONS = Gauge(
    'dms_database_connections',
    'Number of active database connections'
)

CACHE_HITS = Counter(
    'dms_cache_hits_total',
    'Total cache hits'
)

CACHE_MISSES = Counter(
    'dms_cache_misses_total',
    'Total cache misses'
)

CPU_USAGE = Gauge(
    'dms_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'dms_memory_usage_bytes',
    'Memory usage in bytes'
)


def track_request_metrics(func):
    """Decorator to track request metrics."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            response = func(*args, **kwargs)
            status = response.status_code if hasattr(response, 'status_code') else 200

            duration = time.time() - start_time

            # Record metrics
            from flask import request
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=status
            ).inc()

            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(duration)

            return response

        except Exception as e:
            REQUEST_COUNT.labels(
                method=request.method if 'request' in dir() else 'unknown',
                endpoint=request.endpoint if 'request' in dir() and hasattr(request, 'endpoint') else 'unknown',
                status=500
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
