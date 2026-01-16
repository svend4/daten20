"""
Advanced Monitoring & Metrics System

Provides enterprise monitoring capabilities:
- Performance metrics (response times, throughput)
- Resource usage monitoring (CPU, memory, disk, network)
- Application health checks
- Alert management with escalation
- Log aggregation and analysis
- Distributed tracing
- Custom metric dashboards
- SLA monitoring
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MetricType(str, Enum):
    """Metric types"""

    COUNTER = "counter"  # Always increasing
    GAUGE = "gauge"  # Can go up and down
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"  # Summary statistics


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class HealthStatus(str, Enum):
    """Health check status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class Metric:
    """Metric data point"""

    name: str
    value: float
    type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class Alert:
    """Alert definition"""

    id: str
    name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check result"""

    name: str
    status: HealthStatus
    response_time_ms: float
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceSpan:
    """Distributed trace span"""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    duration_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


class MetricsCollector:
    """Collects and stores metrics"""

    def __init__(self, retention_hours: int = 24):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.retention_hours = retention_hours
        self.lock = threading.Lock()

    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Record counter metric"""
        metric = Metric(name=name, value=value, type=MetricType.COUNTER, labels=labels or {}, unit="count")
        self._store_metric(metric)

    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, unit: str = ""):
        """Record gauge metric"""
        metric = Metric(name=name, value=value, type=MetricType.GAUGE, labels=labels or {}, unit=unit)
        self._store_metric(metric)

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, unit: str = ""):
        """Record histogram metric"""
        metric = Metric(name=name, value=value, type=MetricType.HISTOGRAM, labels=labels or {}, unit=unit)
        self._store_metric(metric)

    def _store_metric(self, metric: Metric):
        """Store metric"""
        with self.lock:
            self.metrics[metric.name].append(metric)

    def get_metrics(
        self, name: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> List[Metric]:
        """Get metrics by name and time range"""
        with self.lock:
            metrics = list(self.metrics.get(name, []))

        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return metrics

    def get_latest_metric(self, name: str) -> Optional[Metric]:
        """Get latest metric value"""
        with self.lock:
            metrics = self.metrics.get(name)
            return metrics[-1] if metrics else None

    def calculate_statistics(
        self, name: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Calculate statistics for metrics"""
        metrics = self.get_metrics(name, start_time, end_time)

        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p50": self._percentile(values, 50),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99),
        }

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


class PerformanceMonitor:
    """Monitors application performance"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector

    def track_request(self, endpoint: str, method: str, duration_ms: float, status_code: int):
        """Track HTTP request"""
        labels = {"endpoint": endpoint, "method": method, "status": str(status_code)}

        self.collector.record_counter("http_requests_total", 1.0, labels)
        self.collector.record_histogram("http_request_duration_ms", duration_ms, labels, "ms")

    def track_database_query(self, query_type: str, duration_ms: float):
        """Track database query"""
        labels = {"query_type": query_type}

        self.collector.record_counter("db_queries_total", 1.0, labels)
        self.collector.record_histogram("db_query_duration_ms", duration_ms, labels, "ms")

    def track_cache_operation(self, operation: str, hit: bool):
        """Track cache operations"""
        labels = {"operation": operation, "result": "hit" if hit else "miss"}

        self.collector.record_counter("cache_operations_total", 1.0, labels)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        http_stats = self.collector.calculate_statistics("http_request_duration_ms", start_time=one_hour_ago)

        db_stats = self.collector.calculate_statistics("db_query_duration_ms", start_time=one_hour_ago)

        return {"http_requests": http_stats, "database_queries": db_stats, "timestamp": now.isoformat()}


class ResourceMonitor:
    """Monitors system resources"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector

    def collect_metrics(self):
        """Collect system resource metrics"""
        # In production, use psutil for actual metrics
        import random

        # CPU usage
        self.collector.record_gauge("system_cpu_usage_percent", random.uniform(10, 90), unit="%")

        # Memory usage
        self.collector.record_gauge("system_memory_usage_bytes", random.uniform(1e9, 8e9), unit="bytes")
        self.collector.record_gauge("system_memory_usage_percent", random.uniform(20, 80), unit="%")

        # Disk usage
        self.collector.record_gauge("system_disk_usage_bytes", random.uniform(10e9, 100e9), unit="bytes")
        self.collector.record_gauge("system_disk_usage_percent", random.uniform(30, 70), unit="%")

        # Network I/O
        self.collector.record_counter("system_network_bytes_sent", random.uniform(1e6, 1e9), {"direction": "sent"})
        self.collector.record_counter(
            "system_network_bytes_received", random.uniform(1e6, 1e9), {"direction": "received"}
        )

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        cpu = self.collector.get_latest_metric("system_cpu_usage_percent")
        memory = self.collector.get_latest_metric("system_memory_usage_percent")
        disk = self.collector.get_latest_metric("system_disk_usage_percent")

        return {
            "cpu_percent": cpu.value if cpu else 0,
            "memory_percent": memory.value if memory else 0,
            "disk_percent": disk.value if disk else 0,
        }


class HealthCheckManager:
    """Manages health checks"""

    def __init__(self):
        self.health_checks: Dict[str, Callable[[], HealthCheck]] = {}
        self.results: Dict[str, HealthCheck] = {}

    def register_health_check(self, name: str, check_func: Callable[[], bool]):
        """Register health check"""
        self.health_checks[name] = check_func

    def run_health_check(self, name: str) -> HealthCheck:
        """Run single health check"""
        if name not in self.health_checks:
            return HealthCheck(
                name=name, status=HealthStatus.UNHEALTHY, response_time_ms=0, message="Health check not found"
            )

        start_time = time.time()
        try:
            check_func = self.health_checks[name]
            is_healthy = check_func()

            duration_ms = (time.time() - start_time) * 1000

            result = HealthCheck(
                name=name,
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                response_time_ms=duration_ms,
                message="OK" if is_healthy else "Check failed",
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthCheck(name=name, status=HealthStatus.UNHEALTHY, response_time_ms=duration_ms, message=str(e))

        self.results[name] = result
        return result

    def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all health checks"""
        for name in self.health_checks:
            self.run_health_check(name)

        return self.results

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health"""
        if not self.results:
            return HealthStatus.UNHEALTHY

        unhealthy_count = sum(1 for r in self.results.values() if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in self.results.values() if r.status == HealthStatus.DEGRADED)

        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_handlers: List[Callable[[Alert], None]] = []

    def add_alert_rule(
        self, name: str, metric_name: str, condition: str, threshold: float, severity: AlertSeverity, message: str = ""
    ):
        """Add alert rule"""
        self.alert_rules.append(
            {
                "name": name,
                "metric_name": metric_name,
                "condition": condition,
                "threshold": threshold,
                "severity": severity,
                "message": message,
            }
        )

    def register_notification_handler(self, handler: Callable[[Alert], None]):
        """Register notification handler"""
        self.notification_handlers.append(handler)

    def evaluate_rules(self):
        """Evaluate all alert rules"""
        for rule in self.alert_rules:
            metric = self.collector.get_latest_metric(rule["metric_name"])

            if not metric:
                continue

            should_alert = self._evaluate_condition(metric.value, rule["condition"], rule["threshold"])

            if should_alert:
                self._trigger_alert(rule, metric.value)

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        else:
            return False

    def _trigger_alert(self, rule: Dict[str, Any], current_value: float):
        """Trigger alert"""
        alert_id = f"alert_{rule['name']}_{int(time.time())}"

        # Check if alert already exists and is active
        existing_alert = next(
            (a for a in self.alerts.values() if a.name == rule["name"] and a.status == AlertStatus.ACTIVE), None
        )

        if existing_alert:
            return  # Don't create duplicate alert

        alert = Alert(
            id=alert_id,
            name=rule["name"],
            condition=rule["condition"],
            threshold=rule["threshold"],
            severity=rule["severity"],
            message=rule["message"].format(value=current_value),
            metadata={"current_value": current_value},
        )

        self.alerts[alert_id] = alert

        # Send notifications
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"[Alert] Notification handler failed: {e}")

        print(f"[Alert] {alert.severity.value.upper()}: {alert.name} - {alert.message}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()

        print(f"[Alert] Acknowledged: {alert.name}")
        return True

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()

        print(f"[Alert] Resolved: {alert.name}")
        return True

    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]


class DistributedTracer:
    """Distributed tracing"""

    def __init__(self):
        self.traces: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.lock = threading.Lock()

    def start_span(
        self, trace_id: str, span_id: str, operation_name: str, parent_span_id: Optional[str] = None
    ) -> TraceSpan:
        """Start trace span"""
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.now(),
            duration_ms=0,
        )

        return span

    def finish_span(self, span: TraceSpan):
        """Finish trace span"""
        span.duration_ms = (datetime.now() - span.start_time).total_seconds() * 1000

        with self.lock:
            self.traces[span.trace_id].append(span)

    def add_span_tag(self, span: TraceSpan, key: str, value: Any):
        """Add tag to span"""
        span.tags[key] = value

    def add_span_log(self, span: TraceSpan, message: str, data: Optional[Dict[str, Any]] = None):
        """Add log to span"""
        span.logs.append({"timestamp": datetime.now().isoformat(), "message": message, "data": data or {}})

    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get trace by ID"""
        with self.lock:
            return list(self.traces.get(trace_id, []))


class LogAggregator:
    """Log aggregation and analysis"""

    def __init__(self, max_logs: int = 10000):
        self.logs: deque = deque(maxlen=max_logs)
        self.lock = threading.Lock()

    def log(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Add log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": metadata or {},
        }

        with self.lock:
            self.logs.append(log_entry)

    def search_logs(
        self,
        query: str,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Search logs"""
        with self.lock:
            logs = list(self.logs)

        # Filter by level
        if level:
            logs = [log for log in logs if log["level"] == level]

        # Filter by time
        if start_time:
            start_str = start_time.isoformat()
            logs = [log for log in logs if log["timestamp"] >= start_str]
        if end_time:
            end_str = end_time.isoformat()
            logs = [log for log in logs if log["timestamp"] <= end_str]

        # Filter by query
        if query:
            logs = [log for log in logs if query.lower() in log["message"].lower()]

        return logs


class MonitoringEngine:
    """Main monitoring engine"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.performance_monitor = PerformanceMonitor(self.metrics_collector)
        self.resource_monitor = ResourceMonitor(self.metrics_collector)
        self.health_check_manager = HealthCheckManager()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.tracer = DistributedTracer()
        self.log_aggregator = LogAggregator()

        # Setup default alert rules
        self._setup_default_alerts()

        # Setup default health checks
        self._setup_default_health_checks()

    def _setup_default_alerts(self):
        """Setup default alert rules"""
        self.alert_manager.add_alert_rule(
            name="High CPU Usage",
            metric_name="system_cpu_usage_percent",
            condition=">",
            threshold=80,
            severity=AlertSeverity.WARNING,
            message="CPU usage is {value:.1f}%",
        )

        self.alert_manager.add_alert_rule(
            name="Critical CPU Usage",
            metric_name="system_cpu_usage_percent",
            condition=">",
            threshold=95,
            severity=AlertSeverity.CRITICAL,
            message="CPU usage is critically high: {value:.1f}%",
        )

        self.alert_manager.add_alert_rule(
            name="High Memory Usage",
            metric_name="system_memory_usage_percent",
            condition=">",
            threshold=85,
            severity=AlertSeverity.WARNING,
            message="Memory usage is {value:.1f}%",
        )

    def _setup_default_health_checks(self):
        """Setup default health checks"""
        self.health_check_manager.register_health_check(
            "database", lambda: True  # Would check actual database connection
        )

        self.health_check_manager.register_health_check("cache", lambda: True)  # Would check cache connection

    def collect_all_metrics(self):
        """Collect all system metrics"""
        self.resource_monitor.collect_metrics()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        return {
            "system_health": self.health_check_manager.get_overall_health().value,
            "health_checks": {name: check.status.value for name, check in self.health_check_manager.results.items()},
            "resource_usage": self.resource_monitor.get_resource_usage(),
            "performance": self.performance_monitor.get_performance_summary(),
            "active_alerts": [
                {"id": alert.id, "name": alert.name, "severity": alert.severity.value, "message": alert.message}
                for alert in self.alert_manager.get_active_alerts()
            ],
            "timestamp": datetime.now().isoformat(),
        }


# Global instance
_monitoring_engine: Optional[MonitoringEngine] = None


def get_monitoring_engine() -> MonitoringEngine:
    """Get global monitoring engine instance"""
    global _monitoring_engine

    if _monitoring_engine is None:
        _monitoring_engine = MonitoringEngine()

    return _monitoring_engine
