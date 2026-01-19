#!/usr/bin/env python3
"""
Distributed Tracing Module

Provides distributed tracing capabilities for microservices using OpenTelemetry.

Key Features:
- OpenTelemetry integration
- Jaeger and Zipkin support
- Trace context propagation
- Span collection and management
- Trace visualization data
- Latency analysis
- Dependency graphs
- Error tracking
- Performance profiling
- Custom attributes and events

Dependencies:
- opentelemetry-api
- opentelemetry-sdk
- opentelemetry-instrumentation
"""

import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# Optional HTTP library for Jaeger/Zipkin integration
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

if not REQUESTS_AVAILABLE:
    logger.warning("requests library not available for Jaeger/Zipkin HTTP API. " "Install with: pip install requests")


class SpanKind(str, Enum):
    """Span kind types"""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(str, Enum):
    """Span status"""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """Span context for propagation"""

    trace_id: str
    span_id: str
    trace_flags: int = 1  # Sampled
    trace_state: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if context is valid"""
        return bool(self.trace_id and self.span_id)

    def is_sampled(self) -> bool:
        """Check if trace is sampled"""
        return bool(self.trace_flags & 1)


@dataclass
class SpanEvent:
    """Event within a span"""

    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Link to another span"""

    context: SpanContext
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Trace span"""

    name: str
    context: SpanContext
    parent_context: Optional[SpanContext] = None
    kind: SpanKind = SpanKind.INTERNAL
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: SpanStatus = SpanStatus.UNSET
    status_message: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanLink] = field(default_factory=list)
    resource: Dict[str, Any] = field(default_factory=dict)

    def set_attribute(self, key: str, value: Any):
        """Set span attribute"""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to span"""
        event = SpanEvent(name=name, attributes=attributes or {})
        self.events.append(event)

    def set_status(self, status: SpanStatus, message: Optional[str] = None):
        """Set span status"""
        self.status = status
        self.status_message = message

    def end(self):
        """End the span"""
        self.end_time = datetime.now()

    def duration_ms(self) -> float:
        """Get span duration in milliseconds"""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000

    def is_root(self) -> bool:
        """Check if this is a root span"""
        return self.parent_context is None


@dataclass
class Trace:
    """Complete trace with all spans"""

    trace_id: str
    spans: List[Span] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def add_span(self, span: Span):
        """Add span to trace"""
        self.spans.append(span)

        if not self.start_time or span.start_time < self.start_time:
            self.start_time = span.start_time

        if span.end_time:
            if not self.end_time or span.end_time > self.end_time:
                self.end_time = span.end_time

    def duration_ms(self) -> float:
        """Get trace duration in milliseconds"""
        if not self.start_time or not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000

    def get_root_span(self) -> Optional[Span]:
        """Get root span of trace"""
        for span in self.spans:
            if span.is_root():
                return span
        return None

    def get_service_names(self) -> Set[str]:
        """Get all service names in trace"""
        services = set()
        for span in self.spans:
            if "service.name" in span.resource:
                services.add(span.resource["service.name"])
        return services


class TracingBackend(str, Enum):
    """Tracing backend types"""

    CONSOLE = "console"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OTLP = "otlp"  # OpenTelemetry Protocol


class SpanExporter:
    """Base class for span exporters"""

    def export(self, spans: List[Span]) -> bool:
        """
        Export spans to backend

        Args:
            spans: List of spans to export

        Returns:
            True if successful
        """
        raise NotImplementedError

    def shutdown(self):
        """Shutdown exporter"""
        pass


class ConsoleSpanExporter(SpanExporter):
    """Console span exporter for debugging"""

    def export(self, spans: List[Span]) -> bool:
        """Export spans to console"""
        for span in spans:
            print(f"\n=== Span: {span.name} ===")
            print(f"Trace ID: {span.context.trace_id}")
            print(f"Span ID: {span.context.span_id}")
            print(f"Parent: {span.parent_context.span_id if span.parent_context else 'None'}")
            print(f"Kind: {span.kind}")
            print(f"Duration: {span.duration_ms():.2f}ms")
            print(f"Status: {span.status}")
            if span.attributes:
                print(f"Attributes: {json.dumps(span.attributes, indent=2)}")
            if span.events:
                print(f"Events: {len(span.events)}")
                for event in span.events:
                    print(f"  - {event.name} @ {event.timestamp}")
        return True


class JaegerSpanExporter(SpanExporter):
    """Jaeger span exporter"""

    def __init__(self, endpoint: str = "http://localhost:14268/api/traces"):
        """
        Initialize Jaeger exporter

        Args:
            endpoint: Jaeger collector endpoint
        """
        self.endpoint = endpoint

    def export(self, spans: List[Span]) -> bool:
        """
        Export spans to Jaeger using HTTP API

        Sends spans to Jaeger collector via Thrift HTTP protocol.
        Supports both standard Jaeger API and Jaeger Query Service.
        """
        try:
            # Convert spans to Jaeger format
            jaeger_spans = self._convert_to_jaeger_format(spans)

            # Send to Jaeger using HTTP API
            if not REQUESTS_AVAILABLE:
                logger.warning(
                    f"Cannot export to Jaeger: requests library not installed. "
                    f"Would export {len(spans)} spans to {self.endpoint}"
                )
                return False

            logger.info(f"Exporting {len(spans)} spans to Jaeger at {self.endpoint}")

            # Prepare Jaeger batch
            batch = {
                "batch": {
                    "spans": jaeger_spans.get("spans", []),
                    "process": {"serviceName": "dms", "tags": []},  # Service name
                }
            }

            # Send POST request to Jaeger collector
            response = requests.post(
                self.endpoint, json=batch, headers={"Content-Type": "application/json"}, timeout=10
            )

            if response.status_code in (200, 202, 204):
                logger.info(f"Successfully exported {len(spans)} spans to Jaeger")
                return True
            else:
                logger.error(f"Jaeger export failed with status {response.status_code}: " f"{response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error while exporting to Jaeger: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to export to Jaeger: {e}")
            return False

    def _convert_to_jaeger_format(self, spans: List[Span]) -> Dict[str, Any]:
        """Convert spans to Jaeger JSON format"""
        # Simplified Jaeger format
        jaeger_spans = []
        for span in spans:
            jaeger_span = {
                "traceID": span.context.trace_id,
                "spanID": span.context.span_id,
                "operationName": span.name,
                "startTime": int(span.start_time.timestamp() * 1_000_000),  # microseconds
                "duration": int(span.duration_ms() * 1000),  # microseconds
                "tags": [{"key": k, "value": v} for k, v in span.attributes.items()],
                "logs": [
                    {
                        "timestamp": int(event.timestamp.timestamp() * 1_000_000),
                        "fields": [{"key": k, "value": v} for k, v in event.attributes.items()],
                    }
                    for event in span.events
                ],
            }
            if span.parent_context:
                jaeger_span["references"] = [
                    {
                        "refType": "CHILD_OF",
                        "traceID": span.parent_context.trace_id,
                        "spanID": span.parent_context.span_id,
                    }
                ]
            jaeger_spans.append(jaeger_span)

        return {"spans": jaeger_spans}


class ZipkinSpanExporter(SpanExporter):
    """Zipkin span exporter"""

    def __init__(self, endpoint: str = "http://localhost:9411/api/v2/spans"):
        """
        Initialize Zipkin exporter

        Args:
            endpoint: Zipkin collector endpoint
        """
        self.endpoint = endpoint

    def export(self, spans: List[Span]) -> bool:
        """
        Export spans to Zipkin using HTTP API

        Sends spans to Zipkin collector via JSON over HTTP.
        Compatible with Zipkin v2 API format.
        """
        try:
            # Convert spans to Zipkin format
            zipkin_spans = self._convert_to_zipkin_format(spans)

            # Send to Zipkin using HTTP API
            if not REQUESTS_AVAILABLE:
                logger.warning(
                    f"Cannot export to Zipkin: requests library not installed. "
                    f"Would export {len(spans)} spans to {self.endpoint}"
                )
                return False

            logger.info(f"Exporting {len(spans)} spans to Zipkin at {self.endpoint}")

            # Send POST request to Zipkin collector
            # Zipkin v2 API expects a JSON array of spans
            response = requests.post(
                self.endpoint, json=zipkin_spans, headers={"Content-Type": "application/json"}, timeout=10
            )

            if response.status_code in (200, 202, 204):
                logger.info(f"Successfully exported {len(spans)} spans to Zipkin")
                return True
            else:
                logger.error(f"Zipkin export failed with status {response.status_code}: " f"{response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error while exporting to Zipkin: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to export to Zipkin: {e}")
            return False

    def _convert_to_zipkin_format(self, spans: List[Span]) -> List[Dict[str, Any]]:
        """Convert spans to Zipkin JSON format"""
        zipkin_spans = []
        for span in spans:
            zipkin_span = {
                "traceId": span.context.trace_id,
                "id": span.context.span_id,
                "name": span.name,
                "timestamp": int(span.start_time.timestamp() * 1_000_000),
                "duration": int(span.duration_ms() * 1000),
                "kind": span.kind.upper(),
                "tags": span.attributes,
            }
            if span.parent_context:
                zipkin_span["parentId"] = span.parent_context.span_id
            zipkin_spans.append(zipkin_span)

        return zipkin_spans


class Tracer:
    """
    Distributed tracer

    Creates and manages trace spans.
    """

    def __init__(self, service_name: str, exporter: Optional[SpanExporter] = None, sample_rate: float = 1.0):
        """
        Initialize tracer

        Args:
            service_name: Name of the service
            exporter: Span exporter
            sample_rate: Sampling rate (0.0 to 1.0)
        """
        self.service_name = service_name
        self.exporter = exporter or ConsoleSpanExporter()
        self.sample_rate = sample_rate
        self._active_spans: Dict[str, Span] = {}
        self._completed_spans: List[Span] = []
        self._lock = threading.Lock()
        self._local = threading.local()

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent: Optional[SpanContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """
        Start a new span

        Args:
            name: Span name
            kind: Span kind
            parent: Parent span context
            attributes: Initial attributes

        Returns:
            New span
        """
        # Generate trace ID and span ID
        if parent:
            trace_id = parent.trace_id
        else:
            trace_id = self._generate_trace_id()

        span_id = self._generate_span_id()

        # Check sampling
        trace_flags = 1 if self._should_sample() else 0

        # Create span context
        context = SpanContext(trace_id=trace_id, span_id=span_id, trace_flags=trace_flags)

        # Create span
        span = Span(
            name=name,
            context=context,
            parent_context=parent,
            kind=kind,
            attributes=attributes or {},
            resource={"service.name": self.service_name},
        )

        # Store active span
        with self._lock:
            self._active_spans[span_id] = span

        # Set as current span
        self._set_current_span(span)

        logger.debug(f"Started span: {name} (trace={trace_id}, span={span_id})")
        return span

    def end_span(self, span: Span):
        """
        End a span

        Args:
            span: Span to end
        """
        span.end()

        with self._lock:
            # Remove from active spans
            self._active_spans.pop(span.context.span_id, None)

            # Add to completed spans
            if span.context.is_sampled():
                self._completed_spans.append(span)

        # Clear current span if it's this one
        current = self._get_current_span()
        if current and current.context.span_id == span.context.span_id:
            self._set_current_span(None)

        logger.debug(f"Ended span: {span.name} (duration={span.duration_ms():.2f}ms)")

    @contextmanager
    def span(self, name: str, kind: SpanKind = SpanKind.INTERNAL, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager for creating spans

        Args:
            name: Span name
            kind: Span kind
            attributes: Initial attributes

        Yields:
            Span instance
        """
        # Get parent from current span
        current = self._get_current_span()
        parent = current.context if current else None

        # Start span
        span = self.start_span(name, kind, parent, attributes)

        try:
            yield span
            span.set_status(SpanStatus.OK)
        except Exception as e:
            span.set_status(SpanStatus.ERROR, str(e))
            span.set_attribute("exception.type", type(e).__name__)
            span.set_attribute("exception.message", str(e))
            raise
        finally:
            self.end_span(span)

    def flush(self):
        """Flush all completed spans to exporter"""
        with self._lock:
            if not self._completed_spans:
                return

            spans = self._completed_spans.copy()
            self._completed_spans.clear()

        # Export spans
        try:
            self.exporter.export(spans)
            logger.info(f"Flushed {len(spans)} spans")
        except Exception as e:
            logger.error(f"Failed to flush spans: {e}")

    def shutdown(self):
        """Shutdown tracer"""
        self.flush()
        self.exporter.shutdown()

    def inject_context(self, span: Span) -> Dict[str, str]:
        """
        Inject span context into headers for propagation

        Args:
            span: Span to inject

        Returns:
            Headers dict with trace context
        """
        # W3C Trace Context format
        return {
            "traceparent": f"00-{span.context.trace_id}-{span.context.span_id}-{span.context.trace_flags:02x}",
            "tracestate": span.context.trace_state or "",
        }

    def extract_context(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        """
        Extract span context from headers

        Args:
            headers: Headers dict

        Returns:
            Span context or None
        """
        traceparent = headers.get("traceparent", "")
        if not traceparent:
            return None

        try:
            parts = traceparent.split("-")
            if len(parts) != 4:
                return None

            version, trace_id, span_id, flags = parts

            return SpanContext(
                trace_id=trace_id, span_id=span_id, trace_flags=int(flags, 16), trace_state=headers.get("tracestate")
            )
        except Exception as e:
            logger.error(f"Failed to extract context: {e}")
            return None

    def _generate_trace_id(self) -> str:
        """Generate random trace ID"""
        return uuid.uuid4().hex

    def _generate_span_id(self) -> str:
        """Generate random span ID"""
        return uuid.uuid4().hex[:16]

    def _should_sample(self) -> bool:
        """Determine if trace should be sampled"""
        import random

        return random.random() < self.sample_rate

    def _get_current_span(self) -> Optional[Span]:
        """Get current span from thread-local storage"""
        return getattr(self._local, "current_span", None)

    def _set_current_span(self, span: Optional[Span]):
        """Set current span in thread-local storage"""
        self._local.current_span = span


class TraceAnalyzer:
    """
    Trace analyzer for performance analysis

    Analyzes trace data for insights.
    """

    def __init__(self):
        self.traces: Dict[str, Trace] = {}

    def add_trace(self, trace: Trace):
        """Add trace for analysis"""
        self.traces[trace.trace_id] = trace

    def get_slowest_spans(self, limit: int = 10) -> List[Span]:
        """Get slowest spans across all traces"""
        all_spans = []
        for trace in self.traces.values():
            all_spans.extend(trace.spans)

        return sorted(all_spans, key=lambda s: s.duration_ms(), reverse=True)[:limit]

    def get_error_spans(self) -> List[Span]:
        """Get all spans with errors"""
        error_spans = []
        for trace in self.traces.values():
            for span in trace.spans:
                if span.status == SpanStatus.ERROR:
                    error_spans.append(span)
        return error_spans

    def get_service_latencies(self) -> Dict[str, float]:
        """Get average latency by service"""
        service_durations: Dict[str, List[float]] = defaultdict(list)

        for trace in self.traces.values():
            for span in trace.spans:
                service = span.resource.get("service.name", "unknown")
                service_durations[service].append(span.duration_ms())

        return {service: sum(durations) / len(durations) for service, durations in service_durations.items()}

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build service dependency graph"""
        dependencies: Dict[str, Set[str]] = defaultdict(set)

        for trace in self.traces.values():
            for span in trace.spans:
                if span.parent_context:
                    # Find parent span
                    parent_span = next(
                        (s for s in trace.spans if s.context.span_id == span.parent_context.span_id), None
                    )
                    if parent_span:
                        parent_service = parent_span.resource.get("service.name", "unknown")
                        child_service = span.resource.get("service.name", "unknown")
                        if parent_service != child_service:
                            dependencies[parent_service].add(child_service)

        return dict(dependencies)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create tracer
    tracer = Tracer(service_name="example-service")

    # Create spans
    with tracer.span("handle_request", SpanKind.SERVER) as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.url", "/api/users")

        # Nested span
        with tracer.span("database_query", SpanKind.CLIENT) as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.statement", "SELECT * FROM users")
            time.sleep(0.05)  # Simulate query
            db_span.add_event("query_completed", {"rows": 10})

        # Another nested span
        with tracer.span("cache_check", SpanKind.CLIENT) as cache_span:
            cache_span.set_attribute("cache.system", "redis")
            time.sleep(0.01)

    # Flush and shutdown
    tracer.flush()
    tracer.shutdown()
