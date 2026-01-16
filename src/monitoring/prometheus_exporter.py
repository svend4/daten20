"""
Prometheus Metrics Exporter for Document Management System.

This module provides comprehensive metrics collection for monitoring
system performance, usage, and health.

Features:
- Request duration tracking
- Document processing metrics
- Database query performance
- Cache hit rates
- ML/AI model performance
- System resource usage
- Custom business metrics

Author: DMS Team
Date: 2026-01-16
"""

import time
import functools
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        Info,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not installed. Metrics collection disabled.")

logger = logging.getLogger(__name__)


@dataclass
class MetricConfig:
    """Configuration for a metric."""
    name: str
    description: str
    labels: list = None
    buckets: list = None  # For histograms


class MetricsRegistry:
    """
    Central registry for all application metrics.

    This class manages all Prometheus metrics for the DMS application.
    """

    def __init__(self):
        """Initialize metrics registry."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus client not available. Metrics disabled.")
            self.registry = None
            return

        self.registry = CollectorRegistry()
        self._init_metrics()

    def _init_metrics(self):
        """Initialize all metrics."""

        # ==================== REQUEST METRICS ====================

        # HTTP request duration
        self.http_request_duration = Histogram(
            'dms_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'status'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )

        # HTTP request count
        self.http_requests_total = Counter(
            'dms_http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        # Active requests
        self.http_requests_active = Gauge(
            'dms_http_requests_active',
            'Number of active HTTP requests',
            ['endpoint'],
            registry=self.registry
        )

        # ==================== DOCUMENT METRICS ====================

        # Document processing duration
        self.document_processing_duration = Histogram(
            'dms_document_processing_duration_seconds',
            'Document processing duration in seconds',
            ['operation', 'document_type', 'status'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
            registry=self.registry
        )

        # Documents processed
        self.documents_processed_total = Counter(
            'dms_documents_processed_total',
            'Total number of documents processed',
            ['operation', 'document_type', 'status'],
            registry=self.registry
        )

        # Document size
        self.document_size_bytes = Histogram(
            'dms_document_size_bytes',
            'Document size in bytes',
            ['document_type'],
            buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600],  # 1KB to 100MB
            registry=self.registry
        )

        # Active document processing
        self.documents_processing_active = Gauge(
            'dms_documents_processing_active',
            'Number of documents currently being processed',
            ['operation'],
            registry=self.registry
        )

        # ==================== DATABASE METRICS ====================

        # Database query duration
        self.db_query_duration = Histogram(
            'dms_db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry
        )

        # Database queries count
        self.db_queries_total = Counter(
            'dms_db_queries_total',
            'Total number of database queries',
            ['operation', 'table', 'status'],
            registry=self.registry
        )

        # Database connection pool
        self.db_connections_active = Gauge(
            'dms_db_connections_active',
            'Number of active database connections',
            registry=self.registry
        )

        self.db_connections_idle = Gauge(
            'dms_db_connections_idle',
            'Number of idle database connections',
            registry=self.registry
        )

        # ==================== CACHE METRICS ====================

        # Cache operations
        self.cache_operations_total = Counter(
            'dms_cache_operations_total',
            'Total number of cache operations',
            ['operation', 'result'],  # operation: get/set/delete, result: hit/miss/success/error
            registry=self.registry
        )

        # Cache hit rate (calculated)
        self.cache_hit_rate = Gauge(
            'dms_cache_hit_rate',
            'Cache hit rate (0-1)',
            ['cache_type'],
            registry=self.registry
        )

        # Cache size
        self.cache_size_bytes = Gauge(
            'dms_cache_size_bytes',
            'Cache size in bytes',
            ['cache_type'],
            registry=self.registry
        )

        # Cache items count
        self.cache_items_count = Gauge(
            'dms_cache_items_count',
            'Number of items in cache',
            ['cache_type'],
            registry=self.registry
        )

        # ==================== ML/AI METRICS ====================

        # ML model inference duration
        self.ml_inference_duration = Histogram(
            'dms_ml_inference_duration_seconds',
            'ML model inference duration in seconds',
            ['model_type', 'model_name'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry
        )

        # ML model predictions
        self.ml_predictions_total = Counter(
            'dms_ml_predictions_total',
            'Total number of ML predictions',
            ['model_type', 'model_name', 'status'],
            registry=self.registry
        )

        # NER entities extracted
        self.ner_entities_extracted = Counter(
            'dms_ner_entities_extracted_total',
            'Total number of entities extracted',
            ['entity_type'],
            registry=self.registry
        )

        # Translation operations
        self.translations_total = Counter(
            'dms_translations_total',
            'Total number of translations',
            ['source_lang', 'target_lang', 'backend'],
            registry=self.registry
        )

        # Semantic search operations
        self.semantic_searches_total = Counter(
            'dms_semantic_searches_total',
            'Total number of semantic searches',
            ['index_name'],
            registry=self.registry
        )

        # ==================== SYSTEM METRICS ====================

        # System info
        self.system_info = Info(
            'dms_system',
            'DMS system information',
            registry=self.registry
        )

        # Uptime
        self.uptime_seconds = Gauge(
            'dms_uptime_seconds',
            'System uptime in seconds',
            registry=self.registry
        )

        # Error count
        self.errors_total = Counter(
            'dms_errors_total',
            'Total number of errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        # ==================== BUSINESS METRICS ====================

        # Active users
        self.users_active = Gauge(
            'dms_users_active',
            'Number of active users',
            registry=self.registry
        )

        # Active sessions
        self.sessions_active = Gauge(
            'dms_sessions_active',
            'Number of active sessions',
            registry=self.registry
        )

        # API keys active
        self.api_keys_active = Gauge(
            'dms_api_keys_active',
            'Number of active API keys',
            registry=self.registry
        )

        # Storage usage
        self.storage_used_bytes = Gauge(
            'dms_storage_used_bytes',
            'Storage space used in bytes',
            ['storage_type'],
            registry=self.registry
        )

        logger.info("Prometheus metrics initialized successfully")

    def set_system_info(self, version: str, environment: str, **kwargs):
        """Set system information."""
        if not PROMETHEUS_AVAILABLE or not self.registry:
            return

        info = {
            'version': version,
            'environment': environment,
            **kwargs
        }
        self.system_info.info(info)

    def export_metrics(self) -> bytes:
        """Export metrics in Prometheus format."""
        if not PROMETHEUS_AVAILABLE or not self.registry:
            return b"# Prometheus client not available\n"

        return generate_latest(self.registry)


class PrometheusExporter:
    """
    Prometheus exporter for DMS application.

    This class provides high-level interface for tracking metrics.
    """

    def __init__(self):
        """Initialize exporter."""
        self.metrics = MetricsRegistry()
        self.start_time = time.time()

    def track_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.http_request_duration.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).observe(duration)

        self.metrics.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

    def track_document_processing(
        self,
        operation: str,
        document_type: str,
        status: str,
        duration: float,
        size_bytes: Optional[int] = None
    ):
        """Track document processing."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.document_processing_duration.labels(
            operation=operation,
            document_type=document_type,
            status=status
        ).observe(duration)

        self.metrics.documents_processed_total.labels(
            operation=operation,
            document_type=document_type,
            status=status
        ).inc()

        if size_bytes is not None:
            self.metrics.document_size_bytes.labels(
                document_type=document_type
            ).observe(size_bytes)

    def track_db_query(self, operation: str, table: str, duration: float, status: str = "success"):
        """Track database query."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.db_query_duration.labels(
            operation=operation,
            table=table
        ).observe(duration)

        self.metrics.db_queries_total.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()

    def track_cache_operation(self, operation: str, result: str, cache_type: str = "default"):
        """Track cache operation."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.cache_operations_total.labels(
            operation=operation,
            result=result
        ).inc()

    def update_cache_stats(self, cache_type: str, size_bytes: int, items_count: int, hit_rate: float):
        """Update cache statistics."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.cache_size_bytes.labels(cache_type=cache_type).set(size_bytes)
        self.metrics.cache_items_count.labels(cache_type=cache_type).set(items_count)
        self.metrics.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)

    def track_ml_inference(self, model_type: str, model_name: str, duration: float, status: str = "success"):
        """Track ML model inference."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.ml_inference_duration.labels(
            model_type=model_type,
            model_name=model_name
        ).observe(duration)

        self.metrics.ml_predictions_total.labels(
            model_type=model_type,
            model_name=model_name,
            status=status
        ).inc()

    def track_ner_entities(self, entity_type: str, count: int = 1):
        """Track NER entities extracted."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.ner_entities_extracted.labels(entity_type=entity_type).inc(count)

    def track_translation(self, source_lang: str, target_lang: str, backend: str):
        """Track translation operation."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.translations_total.labels(
            source_lang=source_lang,
            target_lang=target_lang,
            backend=backend
        ).inc()

    def track_semantic_search(self, index_name: str = "default"):
        """Track semantic search operation."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.semantic_searches_total.labels(index_name=index_name).inc()

    def track_error(self, error_type: str, component: str):
        """Track error."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.errors_total.labels(
            error_type=error_type,
            component=component
        ).inc()

    def update_system_metrics(
        self,
        active_users: Optional[int] = None,
        active_sessions: Optional[int] = None,
        active_api_keys: Optional[int] = None
    ):
        """Update system-wide metrics."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        # Update uptime
        uptime = time.time() - self.start_time
        self.metrics.uptime_seconds.set(uptime)

        if active_users is not None:
            self.metrics.users_active.set(active_users)

        if active_sessions is not None:
            self.metrics.sessions_active.set(active_sessions)

        if active_api_keys is not None:
            self.metrics.api_keys_active.set(active_api_keys)

    def update_storage_metrics(self, storage_type: str, used_bytes: int):
        """Update storage usage metrics."""
        if not PROMETHEUS_AVAILABLE or not self.metrics.registry:
            return

        self.metrics.storage_used_bytes.labels(storage_type=storage_type).set(used_bytes)

    def get_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        return self.metrics.export_metrics()


# Global exporter instance
_exporter: Optional[PrometheusExporter] = None


def get_exporter() -> PrometheusExporter:
    """Get global exporter instance."""
    global _exporter
    if _exporter is None:
        _exporter = PrometheusExporter()
    return _exporter


# ==================== DECORATORS ====================

def track_request_duration(endpoint: str = None):
    """
    Decorator to track HTTP request duration.

    Usage:
        @track_request_duration(endpoint='/api/documents')
        def process_document():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                raise
            finally:
                duration = time.time() - start_time
                exporter = get_exporter()
                exporter.track_http_request(
                    method="UNKNOWN",
                    endpoint=endpoint or func.__name__,
                    status=status,
                    duration=duration
                )

        return wrapper
    return decorator


def track_document_processing(operation: str, document_type: str = "unknown"):
    """
    Decorator to track document processing.

    Usage:
        @track_document_processing(operation='parse', document_type='pdf')
        def parse_pdf(file_path):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                exporter = get_exporter()
                exporter.track_document_processing(
                    operation=operation,
                    document_type=document_type,
                    status=status,
                    duration=duration
                )

        return wrapper
    return decorator


def track_database_query(operation: str, table: str):
    """
    Decorator to track database query.

    Usage:
        @track_database_query(operation='select', table='documents')
        def get_documents():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                exporter = get_exporter()
                exporter.track_db_query(
                    operation=operation,
                    table=table,
                    duration=duration,
                    status=status
                )

        return wrapper
    return decorator


def track_cache_hit(cache_type: str = "default"):
    """
    Decorator to track cache hit/miss.

    Usage:
        @track_cache_hit(cache_type='redis')
        def get_from_cache(key):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            exporter = get_exporter()
            if result is not None:
                exporter.track_cache_operation("get", "hit", cache_type)
            else:
                exporter.track_cache_operation("get", "miss", cache_type)

            return result

        return wrapper
    return decorator


# ==================== FLASK INTEGRATION ====================

def get_metrics_handler():
    """
    Get Flask handler for /metrics endpoint.

    Usage:
        from flask import Flask, Response
        from src.monitoring import get_metrics_handler

        app = Flask(__name__)

        @app.route('/metrics')
        def metrics():
            return get_metrics_handler()
    """
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus client not available\n", 200, {'Content-Type': 'text/plain'}

    exporter = get_exporter()
    metrics = exporter.get_metrics()

    return metrics, 200, {'Content-Type': CONTENT_TYPE_LATEST}


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example usage
    exporter = get_exporter()

    # Set system info
    exporter.metrics.set_system_info(
        version="4.0.0",
        environment="production",
        python_version="3.11"
    )

    # Track HTTP request
    exporter.track_http_request("GET", "/api/documents", 200, 0.123)

    # Track document processing
    exporter.track_document_processing(
        operation="parse",
        document_type="pdf",
        status="success",
        duration=1.5,
        size_bytes=1024000
    )

    # Track database query
    exporter.track_db_query("SELECT", "documents", 0.05)

    # Track cache operation
    exporter.track_cache_operation("get", "hit", "redis")

    # Track ML inference
    exporter.track_ml_inference("NER", "spacy-en", 0.234)

    # Update system metrics
    exporter.update_system_metrics(
        active_users=42,
        active_sessions=67,
        active_api_keys=15
    )

    # Print metrics
    print(exporter.get_metrics().decode('utf-8'))
