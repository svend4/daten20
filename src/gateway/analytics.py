"""
API Gateway Analytics

Provides real-time analytics and metrics for API usage including
request metrics, error tracking, latency analysis, and anomaly detection.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class TimeWindow(str, Enum):
    """Time window for aggregation"""
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1mo"


@dataclass
class RequestMetrics:
    """Request metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    requests_per_second: float = 0.0


@dataclass
class EndpointMetrics:
    """Metrics for specific endpoint"""
    endpoint: str
    method: str
    metrics: RequestMetrics = field(default_factory=RequestMetrics)
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    response_times: List[float] = field(default_factory=list)


@dataclass
class ClientMetrics:
    """Metrics for specific client"""
    client_id: str
    client_type: str  # "user", "api_key", "ip"
    metrics: RequestMetrics = field(default_factory=RequestMetrics)
    endpoints_used: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class TimeSeriesPoint:
    """Time series data point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    timestamp: datetime
    metric: str
    current_value: float
    expected_value: float
    deviation: float
    severity: str  # "low", "medium", "high", "critical"
    description: str


class MetricsCollector:
    """Collects and aggregates metrics"""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.response_times: deque = deque(maxlen=window_size)
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = datetime.utcnow()

    def record_request(
        self,
        status_code: int,
        response_time_ms: float
    ):
        """
        Record a request

        Args:
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
        """
        self.total_requests += 1
        self.response_times.append(response_time_ms)
        self.status_codes[status_code] += 1

        if 200 <= status_code < 400:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

    def get_metrics(self) -> RequestMetrics:
        """Get aggregated metrics"""
        if not self.response_times:
            return RequestMetrics()

        response_times_list = list(self.response_times)

        # Calculate percentiles
        p50 = statistics.median(response_times_list)
        p95 = self._percentile(response_times_list, 95)
        p99 = self._percentile(response_times_list, 99)

        # Calculate error rate
        error_rate = (
            self.failed_requests / self.total_requests
            if self.total_requests > 0
            else 0.0
        )

        # Calculate requests per second
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        rps = self.total_requests / elapsed if elapsed > 0 else 0.0

        return RequestMetrics(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            error_rate=error_rate,
            avg_response_time_ms=statistics.mean(response_times_list),
            p50_response_time_ms=p50,
            p95_response_time_ms=p95,
            p99_response_time_ms=p99,
            requests_per_second=rps
        )

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        index = min(index, len(sorted_data) - 1)

        return sorted_data[index]

    def reset(self):
        """Reset metrics"""
        self.response_times.clear()
        self.status_codes.clear()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = datetime.utcnow()


class APIAnalytics:
    """API analytics engine"""

    def __init__(self):
        # Global metrics
        self.global_collector = MetricsCollector()

        # Per-endpoint metrics
        self.endpoint_collectors: Dict[str, MetricsCollector] = {}

        # Per-client metrics
        self.client_collectors: Dict[str, MetricsCollector] = {}

        # Time series data
        self.time_series: Dict[str, List[TimeSeriesPoint]] = defaultdict(list)

        # Geographic distribution
        self.geographic_distribution: Dict[str, int] = defaultdict(int)

        # Anomaly detection
        self.anomalies: List[AnomalyAlert] = []
        self.baseline_metrics: Dict[str, float] = {}

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        client_id: Optional[str] = None,
        client_type: str = "unknown",
        country: Optional[str] = None
    ):
        """
        Record API request

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            client_id: Client identifier
            client_type: Type of client (user, api_key, ip)
            country: Client country
        """
        # Record global metrics
        self.global_collector.record_request(status_code, response_time_ms)

        # Record endpoint metrics
        endpoint_key = f"{method}:{endpoint}"
        if endpoint_key not in self.endpoint_collectors:
            self.endpoint_collectors[endpoint_key] = MetricsCollector()
        self.endpoint_collectors[endpoint_key].record_request(status_code, response_time_ms)

        # Record client metrics
        if client_id:
            if client_id not in self.client_collectors:
                self.client_collectors[client_id] = MetricsCollector()
            self.client_collectors[client_id].record_request(status_code, response_time_ms)

        # Record geographic distribution
        if country:
            self.geographic_distribution[country] += 1

        # Record time series
        now = datetime.utcnow()
        self.time_series["requests"].append(
            TimeSeriesPoint(timestamp=now, value=1.0)
        )
        self.time_series["response_time"].append(
            TimeSeriesPoint(timestamp=now, value=response_time_ms)
        )

        # Check for anomalies
        self._check_anomalies(response_time_ms)

    def get_global_metrics(self) -> RequestMetrics:
        """Get global metrics"""
        return self.global_collector.get_metrics()

    def get_endpoint_metrics(
        self,
        top_n: int = 10
    ) -> List[EndpointMetrics]:
        """
        Get endpoint metrics

        Args:
            top_n: Return top N endpoints by request count

        Returns:
            List of endpoint metrics
        """
        endpoint_metrics = []

        for endpoint_key, collector in self.endpoint_collectors.items():
            method, endpoint = endpoint_key.split(":", 1)
            metrics = collector.get_metrics()

            endpoint_metrics.append(EndpointMetrics(
                endpoint=endpoint,
                method=method,
                metrics=metrics,
                status_codes=dict(collector.status_codes),
                response_times=list(collector.response_times)
            ))

        # Sort by total requests
        endpoint_metrics.sort(key=lambda x: x.metrics.total_requests, reverse=True)

        return endpoint_metrics[:top_n]

    def get_client_metrics(
        self,
        top_n: int = 10
    ) -> List[ClientMetrics]:
        """
        Get client metrics

        Args:
            top_n: Return top N clients by request count

        Returns:
            List of client metrics
        """
        client_metrics = []

        for client_id, collector in self.client_collectors.items():
            metrics = collector.get_metrics()

            client_metrics.append(ClientMetrics(
                client_id=client_id,
                client_type="unknown",  # Would need to track this
                metrics=metrics
            ))

        # Sort by total requests
        client_metrics.sort(key=lambda x: x.metrics.total_requests, reverse=True)

        return client_metrics[:top_n]

    def get_time_series(
        self,
        metric: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        window: TimeWindow = TimeWindow.MINUTE
    ) -> List[TimeSeriesPoint]:
        """
        Get time series data

        Args:
            metric: Metric name
            start_time: Start time (default: 1 hour ago)
            end_time: End time (default: now)
            window: Aggregation window

        Returns:
            List of time series points
        """
        if metric not in self.time_series:
            return []

        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=1)

        if not end_time:
            end_time = datetime.utcnow()

        # Filter by time range
        points = [
            p for p in self.time_series[metric]
            if start_time <= p.timestamp <= end_time
        ]

        # Aggregate by window
        aggregated = self._aggregate_time_series(points, window)

        return aggregated

    def _aggregate_time_series(
        self,
        points: List[TimeSeriesPoint],
        window: TimeWindow
    ) -> List[TimeSeriesPoint]:
        """Aggregate time series data by window"""
        if not points:
            return []

        # Get window duration in seconds
        window_seconds = {
            TimeWindow.MINUTE: 60,
            TimeWindow.FIVE_MINUTES: 300,
            TimeWindow.HOUR: 3600,
            TimeWindow.DAY: 86400,
            TimeWindow.WEEK: 604800,
            TimeWindow.MONTH: 2592000,
        }[window]

        # Group points by window
        windows: Dict[datetime, List[float]] = defaultdict(list)

        for point in points:
            # Round timestamp to window
            window_start = datetime.fromtimestamp(
                (point.timestamp.timestamp() // window_seconds) * window_seconds
            )
            windows[window_start].append(point.value)

        # Aggregate each window
        aggregated = []
        for window_start, values in sorted(windows.items()):
            aggregated.append(TimeSeriesPoint(
                timestamp=window_start,
                value=sum(values),  # Sum for counter metrics
                metadata={"count": len(values)}
            ))

        return aggregated

    def get_geographic_distribution(self) -> Dict[str, int]:
        """Get geographic distribution of requests"""
        return dict(self.geographic_distribution)

    def _check_anomalies(self, response_time_ms: float):
        """Check for anomalies in metrics"""
        # Simple anomaly detection based on deviation from baseline

        # Update baseline (rolling average)
        if "response_time" not in self.baseline_metrics:
            self.baseline_metrics["response_time"] = response_time_ms
        else:
            # Exponential moving average
            alpha = 0.1
            self.baseline_metrics["response_time"] = (
                alpha * response_time_ms +
                (1 - alpha) * self.baseline_metrics["response_time"]
            )

        # Check if current value deviates significantly
        baseline = self.baseline_metrics["response_time"]
        deviation = abs(response_time_ms - baseline) / baseline if baseline > 0 else 0

        # Trigger alert if deviation > 200%
        if deviation > 2.0:
            severity = "critical" if deviation > 5.0 else "high" if deviation > 3.0 else "medium"

            alert = AnomalyAlert(
                timestamp=datetime.utcnow(),
                metric="response_time",
                current_value=response_time_ms,
                expected_value=baseline,
                deviation=deviation,
                severity=severity,
                description=f"Response time ({response_time_ms:.2f}ms) is {deviation*100:.1f}% higher than baseline ({baseline:.2f}ms)"
            )

            self.anomalies.append(alert)

            # Keep only recent anomalies (last 100)
            if len(self.anomalies) > 100:
                self.anomalies = self.anomalies[-100:]

    def get_anomalies(
        self,
        since: Optional[datetime] = None,
        severity: Optional[str] = None
    ) -> List[AnomalyAlert]:
        """
        Get anomaly alerts

        Args:
            since: Get anomalies since this time
            severity: Filter by severity

        Returns:
            List of anomaly alerts
        """
        alerts = self.anomalies

        if since:
            alerts = [a for a in alerts if a.timestamp >= since]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts


# Global analytics instance
_api_analytics: Optional[APIAnalytics] = None


def get_api_analytics() -> APIAnalytics:
    """Get global API analytics instance"""
    global _api_analytics
    if _api_analytics is None:
        _api_analytics = APIAnalytics()
    return _api_analytics


def record_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    response_time_ms: float,
    **kwargs
):
    """
    Record API request for analytics

    Args:
        endpoint: API endpoint
        method: HTTP method
        status_code: HTTP status code
        response_time_ms: Response time in milliseconds
        **kwargs: Additional parameters (client_id, country, etc.)
    """
    analytics = get_api_analytics()
    analytics.record_request(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time_ms=response_time_ms,
        **kwargs
    )
