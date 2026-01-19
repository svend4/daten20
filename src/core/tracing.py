"""
Distributed Tracing Module - Phase 4 TASK 38

This module provides distributed tracing capabilities using OpenTelemetry.
Supports Jaeger, Zipkin, and OTLP (OpenTelemetry Protocol) exporters.

Features:
- Automatic instrumentation for Flask, SQLAlchemy, Requests
- Custom span creation decorators
- Context propagation across services
- Performance metrics collection
- Error tracking and logging

Usage:
    from src.core.tracing import init_tracing, traced

    # Initialize tracing (call once at app startup)
    init_tracing(app_name="dms-api", environment="production")

    # Use decorator for custom spans
    @traced(name="process_document")
    def process_document(doc_id):
        # Your code here
        pass

Author: DMS Development Team
Date: 2026-01-16
"""

import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[trace.Tracer] = None
_is_initialized: bool = False


def get_tracer() -> trace.Tracer:
    """
    Get the global tracer instance.

    Returns:
        Tracer: OpenTelemetry tracer instance

    Raises:
        RuntimeError: If tracing is not initialized
    """
    global _tracer
    if _tracer is None:
        raise RuntimeError(
            "Tracing not initialized. Call init_tracing() first."
        )
    return _tracer


def init_tracing(
    app_name: str = "dms",
    environment: str = "development",
    jaeger_host: Optional[str] = None,
    jaeger_port: Optional[int] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console: bool = False,
    sample_rate: float = 1.0,
) -> trace.Tracer:
    """
    Initialize distributed tracing with OpenTelemetry.

    Args:
        app_name: Name of the application
        environment: Deployment environment (development, staging, production)
        jaeger_host: Jaeger agent host (default: localhost)
        jaeger_port: Jaeger agent port (default: 6831)
        otlp_endpoint: OTLP collector endpoint (e.g., http://localhost:4317)
        enable_console: Enable console exporter for debugging
        sample_rate: Sampling rate (0.0 to 1.0, default 1.0 = 100%)

    Returns:
        Tracer: Configured OpenTelemetry tracer

    Example:
        >>> init_tracing(
        ...     app_name="dms-api",
        ...     environment="production",
        ...     jaeger_host="jaeger.example.com",
        ...     jaeger_port=6831
        ... )
    """
    global _tracer, _is_initialized

    if _is_initialized:
        logger.warning("Tracing already initialized, skipping...")
        return _tracer

    # Get configuration from environment variables if not provided
    jaeger_host = jaeger_host or os.getenv("JAEGER_AGENT_HOST", "localhost")
    jaeger_port = jaeger_port or int(os.getenv("JAEGER_AGENT_PORT", "6831"))
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    # Create resource with service information
    resource = Resource(
        attributes={
            SERVICE_NAME: app_name,
            "environment": environment,
            "service.version": os.getenv("APP_VERSION", "1.0.0"),
            "deployment.environment": environment,
        }
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure exporters based on environment
    exporters_configured = False

    # 1. Jaeger Exporter (primary for production)
    try:
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        logger.info(
            f"Jaeger exporter configured: {jaeger_host}:{jaeger_port}"
        )
        exporters_configured = True
    except Exception as e:
        logger.warning(f"Failed to configure Jaeger exporter: {e}")

    # 2. OTLP Exporter (for OpenTelemetry Collector)
    if otlp_endpoint:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(f"OTLP exporter configured: {otlp_endpoint}")
            exporters_configured = True
        except Exception as e:
            logger.warning(f"Failed to configure OTLP exporter: {e}")

    # 3. Console Exporter (for development/debugging)
    if enable_console or (environment == "development" and not exporters_configured):
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("Console exporter configured (development mode)")
        exporters_configured = True

    if not exporters_configured:
        logger.warning(
            "No trace exporters configured! Spans will be dropped. "
            "Set JAEGER_AGENT_HOST or OTEL_EXPORTER_OTLP_ENDPOINT."
        )

    # Set the global tracer provider
    trace.set_tracer_provider(provider)

    # Create tracer
    _tracer = trace.get_tracer(__name__)

    # Auto-instrument libraries
    _auto_instrument()

    _is_initialized = True
    logger.info(
        f"Distributed tracing initialized for '{app_name}' "
        f"in '{environment}' environment"
    )

    return _tracer


def _auto_instrument():
    """
    Automatically instrument supported libraries.

    Instruments:
    - Flask: HTTP requests and responses
    - Requests: Outgoing HTTP requests
    - SQLAlchemy: Database queries
    """
    try:
        # Flask instrumentation
        FlaskInstrumentor().instrument()
        logger.info("Flask auto-instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument Flask: {e}")

    try:
        # Requests instrumentation
        RequestsInstrumentor().instrument()
        logger.info("Requests auto-instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument Requests: {e}")

    try:
        # SQLAlchemy instrumentation
        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy auto-instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument SQLAlchemy: {e}")


def traced(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
) -> Callable:
    """
    Decorator to trace a function or method.

    Creates a new span for the decorated function and automatically
    captures exceptions.

    Args:
        name: Custom span name (default: function name)
        attributes: Additional span attributes
        record_exception: Whether to record exceptions in the span

    Returns:
        Decorated function

    Example:
        >>> @traced(name="fetch_user", attributes={"db": "postgres"})
        ... def get_user(user_id: int):
        ...     return User.query.get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get tracer
            try:
                tracer = get_tracer()
            except RuntimeError:
                # Tracing not initialized, execute without tracing
                return func(*args, **kwargs)

            # Determine span name
            span_name = name or f"{func.__module__}.{func.__name__}"

            # Start span
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.namespace", func.__module__)

                try:
                    # Execute function
                    result = func(*args, **kwargs)

                    # Mark span as successful
                    span.set_status(Status(StatusCode.OK))

                    return result

                except Exception as e:
                    # Record exception
                    if record_exception:
                        span.record_exception(e)

                    # Mark span as error
                    span.set_status(
                        Status(StatusCode.ERROR, str(e))
                    )

                    # Re-raise exception
                    raise

        return wrapper
    return decorator


def add_span_attribute(key: str, value: Any):
    """
    Add an attribute to the current span.

    Args:
        key: Attribute key
        value: Attribute value

    Example:
        >>> def process_document(doc_id):
        ...     add_span_attribute("document.id", doc_id)
        ...     # Processing logic
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Add an event to the current span.

    Args:
        name: Event name
        attributes: Event attributes

    Example:
        >>> def upload_file(file):
        ...     add_span_event("file.uploaded", {"size": len(file.read())})
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes or {})


def create_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    Create a new span context manager.

    Args:
        name: Span name
        attributes: Span attributes

    Returns:
        Span context manager

    Example:
        >>> with create_span("database_query", {"query": "SELECT ..."}):
        ...     result = db.execute(query)
    """
    try:
        tracer = get_tracer()
    except RuntimeError:
        # Return a no-op context manager
        from contextlib import nullcontext
        return nullcontext()

    span = tracer.start_span(name)

    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return trace.use_span(span, end_on_exit=True)


# Convenience decorators for common operations


def traced_api(endpoint: str):
    """
    Decorator for API endpoint tracing.

    Args:
        endpoint: API endpoint name

    Example:
        >>> @traced_api("/api/users")
        ... def get_users():
        ...     return User.query.all()
    """
    return traced(
        name=f"api.{endpoint}",
        attributes={"http.endpoint": endpoint}
    )


def traced_db(operation: str, table: Optional[str] = None):
    """
    Decorator for database operation tracing.

    Args:
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name

    Example:
        >>> @traced_db("SELECT", "users")
        ... def get_user(user_id):
        ...     return User.query.get(user_id)
    """
    attrs = {"db.operation": operation}
    if table:
        attrs["db.table"] = table

    return traced(
        name=f"db.{operation.lower()}.{table or 'unknown'}",
        attributes=attrs
    )


def traced_ml(model_name: str, operation: str):
    """
    Decorator for ML operation tracing.

    Args:
        model_name: ML model name
        operation: Operation (train, predict, evaluate)

    Example:
        >>> @traced_ml("bert", "predict")
        ... def predict(text):
        ...     return model.predict(text)
    """
    return traced(
        name=f"ml.{model_name}.{operation}",
        attributes={
            "ml.model": model_name,
            "ml.operation": operation
        }
    )


def shutdown_tracing():
    """
    Shutdown tracing and flush all pending spans.

    Call this during application shutdown to ensure all traces are exported.

    Example:
        >>> @app.teardown_appcontext
        ... def shutdown(exception=None):
        ...     shutdown_tracing()
    """
    global _is_initialized

    if not _is_initialized:
        return

    try:
        # Get the tracer provider
        provider = trace.get_tracer_provider()

        # Force flush all pending spans
        if hasattr(provider, "force_flush"):
            provider.force_flush()
            logger.info("Flushed all pending traces")

        # Shutdown the provider
        if hasattr(provider, "shutdown"):
            provider.shutdown()
            logger.info("Tracing shutdown complete")

    except Exception as e:
        logger.error(f"Error during tracing shutdown: {e}")

    _is_initialized = False


# Example usage and testing
if __name__ == "__main__":
    # Initialize tracing
    init_tracing(
        app_name="dms-test",
        environment="development",
        enable_console=True
    )

    # Example 1: Using decorator
    @traced(name="example_function", attributes={"user": "test"})
    def example_function(x: int) -> int:
        add_span_attribute("input.value", x)
        result = x * 2
        add_span_event("calculation_complete", {"result": result})
        return result

    # Example 2: Using context manager
    with create_span("manual_span", {"operation": "test"}):
        result = example_function(42)
        print(f"Result: {result}")

    # Example 3: API endpoint
    @traced_api("/api/test")
    def api_endpoint():
        return {"status": "ok"}

    api_endpoint()

    # Shutdown
    shutdown_tracing()

    print("Tracing test complete!")
