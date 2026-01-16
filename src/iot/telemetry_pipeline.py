"""
Telemetry Pipeline

High-throughput telemetry ingestion, transformation, aggregation,
time-series storage, and alerting engine.

Part of v3.6 IoT & Edge Computing implementation.
"""

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

logger = logging.getLogger(__name__)


class TelemetryType(Enum):
    """Telemetry data types."""

    NUMERIC = "numeric"
    STRING = "string"
    BOOLEAN = "boolean"
    JSON = "json"


class AggregationType(Enum):
    """Aggregation types."""

    AVG = "avg"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    STDDEV = "stddev"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TelemetryPoint:
    """Single telemetry data point."""

    device_id: str
    metric_name: str
    value: Union[float, int, str, bool, Dict]
    timestamp: datetime = field(default_factory=datetime.now)
    unit: Optional[str] = None
    quality: float = 1.0  # 0.0-1.0 quality indicator
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedData:
    """Aggregated telemetry data."""

    metric_name: str
    aggregation: AggregationType
    value: float
    start_time: datetime
    end_time: datetime
    sample_count: int
    device_ids: List[str] = field(default_factory=list)


@dataclass
class AlertRule:
    """Alert rule definition."""

    rule_id: str
    rule_name: str
    metric_name: str
    condition: str  # ">" | "<" | "==" | "!=" | "between"
    threshold: Union[float, tuple]  # Single value or (min, max) for between
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_seconds: int = 300  # Minimum time between alerts
    enabled: bool = True
    device_filter: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Triggered alert."""

    alert_id: str
    rule_id: str
    device_id: str
    metric_name: str
    value: Any
    threshold: Any
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


class SchemaValidator:
    """Validate telemetry data schema."""

    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}

    def register_schema(
        self,
        metric_name: str,
        data_type: TelemetryType,
        required_fields: Optional[List[str]] = None,
        valid_range: Optional[tuple] = None,
    ):
        """Register telemetry schema."""
        self.schemas[metric_name] = {
            "data_type": data_type,
            "required_fields": required_fields or [],
            "valid_range": valid_range,
        }

    def validate(self, point: TelemetryPoint) -> bool:
        """Validate telemetry point against schema."""
        schema = self.schemas.get(point.metric_name)
        if not schema:
            # No schema registered, accept all
            return True

        # Validate data type
        data_type = schema["data_type"]
        if data_type == TelemetryType.NUMERIC:
            if not isinstance(point.value, (int, float)):
                logger.error(f"Invalid type for {point.metric_name}: expected numeric")
                return False

            # Validate range
            if schema["valid_range"]:
                min_val, max_val = schema["valid_range"]
                if not (min_val <= point.value <= max_val):
                    logger.error(f"Value out of range: {point.value}")
                    return False

        return True


class DataTransformer:
    """Transform and normalize telemetry data."""

    def transform(self, point: TelemetryPoint, transformations: Optional[Dict[str, Callable]] = None) -> TelemetryPoint:
        """Apply transformations to telemetry point."""
        if not transformations:
            return point

        # Apply value transformation
        if "value" in transformations:
            point.value = transformations["value"](point.value)

        # Apply unit conversion
        if "unit" in transformations:
            point.value, point.unit = transformations["unit"](point.value, point.unit)

        return point

    def normalize(self, point: TelemetryPoint) -> TelemetryPoint:
        """Normalize telemetry data."""
        # Ensure timestamp is datetime
        if not isinstance(point.timestamp, datetime):
            point.timestamp = datetime.now()

        # Clamp quality to 0.0-1.0
        point.quality = max(0.0, min(1.0, point.quality))

        return point

    def convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between units."""
        # Simple unit conversions
        conversions = {
            ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
            ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
            ("m", "ft"): lambda v: v * 3.28084,
            ("ft", "m"): lambda v: v / 3.28084,
            ("kg", "lb"): lambda v: v * 2.20462,
            ("lb", "kg"): lambda v: v / 2.20462,
        }

        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            return conversions[key](value)

        return value


class TelemetryIngestion:
    """High-throughput telemetry data ingestion."""

    def __init__(self, max_queue_size: int = 10000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.validator = SchemaValidator()
        self.transformer = DataTransformer()
        self.ingestion_count = 0
        self.dropped_count = 0
        self.running = False

    async def ingest(self, point: TelemetryPoint) -> bool:
        """Ingest single telemetry point."""
        # Validate
        if not self.validator.validate(point):
            self.dropped_count += 1
            return False

        # Normalize
        point = self.transformer.normalize(point)

        # Queue for processing
        try:
            await self.queue.put(point)
            self.ingestion_count += 1
            return True
        except asyncio.QueueFull:
            logger.warning("Telemetry queue full, dropping data")
            self.dropped_count += 1
            return False

    async def ingest_batch(self, points: List[TelemetryPoint]) -> int:
        """Ingest batch of telemetry points."""
        success_count = 0

        for point in points:
            if await self.ingest(point):
                success_count += 1

        return success_count

    async def get_next(self) -> Optional[TelemetryPoint]:
        """Get next telemetry point from queue."""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            "ingestion_count": self.ingestion_count,
            "dropped_count": self.dropped_count,
            "queue_size": self.queue.qsize(),
            "drop_rate": self.dropped_count / max(self.ingestion_count + self.dropped_count, 1),
        }


class DataAggregator:
    """Aggregate telemetry data at edge."""

    def __init__(self):
        self.buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

    def add_point(self, point: TelemetryPoint):
        """Add point to aggregation buffer."""
        key = f"{point.device_id}:{point.metric_name}"
        self.buffers[key].append(point)

    def aggregate(
        self, device_id: str, metric_name: str, aggregation: AggregationType, time_window: Optional[timedelta] = None
    ) -> Optional[AggregatedData]:
        """Aggregate data for metric."""
        key = f"{device_id}:{metric_name}"
        buffer = self.buffers.get(key, deque())

        if not buffer:
            return None

        # Filter by time window
        if time_window:
            cutoff = datetime.now() - time_window
            points = [p for p in buffer if p.timestamp >= cutoff]
        else:
            points = list(buffer)

        if not points:
            return None

        # Extract numeric values
        try:
            values = [float(p.value) for p in points]
        except (ValueError, TypeError):
            logger.error(f"Non-numeric values in {metric_name}")
            return None

        # Calculate aggregation
        if aggregation == AggregationType.AVG:
            result = sum(values) / len(values)
        elif aggregation == AggregationType.SUM:
            result = sum(values)
        elif aggregation == AggregationType.MIN:
            result = min(values)
        elif aggregation == AggregationType.MAX:
            result = max(values)
        elif aggregation == AggregationType.COUNT:
            result = len(values)
        elif aggregation == AggregationType.STDDEV:
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            result = variance**0.5
        else:
            result = 0.0

        return AggregatedData(
            metric_name=metric_name,
            aggregation=aggregation,
            value=result,
            start_time=points[0].timestamp,
            end_time=points[-1].timestamp,
            sample_count=len(points),
            device_ids=[device_id],
        )


class TimeSeriesStore:
    """Time-series data storage."""

    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days
        self.data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100000))

    def store(self, point: TelemetryPoint):
        """Store telemetry point."""
        key = f"{point.device_id}:{point.metric_name}"
        self.data[key].append(point)

    def store_batch(self, points: List[TelemetryPoint]):
        """Store batch of points."""
        for point in points:
            self.store(point)

    def query(
        self,
        device_id: str,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[TelemetryPoint]:
        """Query time-series data."""
        key = f"{device_id}:{metric_name}"
        points = list(self.data.get(key, deque()))

        # Filter by time range
        if start_time:
            points = [p for p in points if p.timestamp >= start_time]

        if end_time:
            points = [p for p in points if p.timestamp <= end_time]

        # Apply limit
        if limit:
            points = points[-limit:]

        return points

    def cleanup_old_data(self):
        """Remove data older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed = 0

        for key, points in self.data.items():
            original_len = len(points)

            # Filter out old points
            self.data[key] = deque([p for p in points if p.timestamp >= cutoff], maxlen=points.maxlen)

            removed += original_len - len(self.data[key])

        logger.info(f"Cleaned up {removed} old telemetry points")
        return removed


class AlertingEngine:
    """Threshold-based alerting."""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.last_alert_time: Dict[str, datetime] = {}

    def add_rule(self, rule: AlertRule):
        """Add alert rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.rule_name}")

    def remove_rule(self, rule_id: str):
        """Remove alert rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def evaluate(self, point: TelemetryPoint) -> List[Alert]:
        """Evaluate telemetry point against alert rules."""
        triggered_alerts = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Check metric name matches
            if rule.metric_name != point.metric_name:
                continue

            # Check device filter
            if rule.device_filter and point.device_id not in rule.device_filter:
                continue

            # Check cooldown
            last_alert_key = f"{rule.rule_id}:{point.device_id}"
            last_alert = self.last_alert_time.get(last_alert_key)

            if last_alert:
                time_since_last = (datetime.now() - last_alert).total_seconds()
                if time_since_last < rule.cooldown_seconds:
                    continue

            # Evaluate condition
            if self._check_condition(point.value, rule.condition, rule.threshold):
                alert = Alert(
                    alert_id=str(uuid4()),
                    rule_id=rule.rule_id,
                    device_id=point.device_id,
                    metric_name=point.metric_name,
                    value=point.value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    message=f"{rule.rule_name}: {point.metric_name}={point.value} {rule.condition} {rule.threshold}",
                )

                triggered_alerts.append(alert)
                self.alerts.append(alert)
                self.last_alert_time[last_alert_key] = datetime.now()

                logger.warning(f"Alert triggered: {alert.message}")

        return triggered_alerts

    def _check_condition(self, value: Any, condition: str, threshold: Union[float, tuple]) -> bool:
        """Check if condition is met."""
        try:
            if condition == ">":
                return float(value) > threshold
            elif condition == "<":
                return float(value) < threshold
            elif condition == "==":
                return float(value) == threshold
            elif condition == "!=":
                return float(value) != threshold
            elif condition == "between":
                min_val, max_val = threshold
                return min_val <= float(value) <= max_val
        except (ValueError, TypeError):
            return False

        return False

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                logger.info(f"Alert {alert_id} acknowledged")
                return True

        return False

    def get_active_alerts(
        self, severity: Optional[AlertSeverity] = None, acknowledged: Optional[bool] = False
    ) -> List[Alert]:
        """Get active alerts."""
        alerts = self.alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]

        # Return most recent first
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)


class TelemetryPipeline:
    """Main telemetry processing pipeline."""

    def __init__(self):
        self.ingestion = TelemetryIngestion()
        self.aggregator = DataAggregator()
        self.store = TimeSeriesStore()
        self.alerting = AlertingEngine()
        self.running = False

    async def ingest(self, point: TelemetryPoint) -> bool:
        """Ingest telemetry point."""
        return await self.ingestion.ingest(point)

    async def ingest_batch(self, points: List[TelemetryPoint]) -> int:
        """Ingest batch of points."""
        return await self.ingestion.ingest_batch(points)

    async def start_pipeline(self):
        """Start processing pipeline."""
        self.running = True

        while self.running:
            # Get next point
            point = await self.ingestion.get_next()

            if point:
                # Add to aggregator
                self.aggregator.add_point(point)

                # Store in time-series
                self.store.store(point)

                # Evaluate alerts
                self.alerting.evaluate(point)

    async def stop_pipeline(self):
        """Stop processing pipeline."""
        self.running = False

    def query(
        self,
        device_ids: List[str],
        metric: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: Optional[str] = None,
        interval: Optional[timedelta] = None,
    ) -> Union[List[TelemetryPoint], List[AggregatedData]]:
        """Query telemetry data."""
        # Query data for each device
        all_points = []
        for device_id in device_ids:
            points = self.store.query(device_id=device_id, metric_name=metric, start_time=start_time, end_time=end_time)
            all_points.extend(points)

        # Return raw data if no aggregation
        if not aggregation:
            return all_points

        # Aggregate data
        aggregated_results = []
        for device_id in device_ids:
            result = self.aggregator.aggregate(
                device_id=device_id, metric_name=metric, aggregation=AggregationType(aggregation), time_window=interval
            )
            if result:
                aggregated_results.append(result)

        return aggregated_results

    def add_alert_rule(
        self, rule_name: str, metric_name: str, condition: str, threshold: Union[float, tuple], **kwargs
    ) -> AlertRule:
        """Add alert rule."""
        rule = AlertRule(
            rule_id=str(uuid4()),
            rule_name=rule_name,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            **kwargs,
        )

        self.alerting.add_rule(rule)
        return rule

    def get_active_alerts(self, **filters) -> List[Alert]:
        """Get active alerts."""
        return self.alerting.get_active_alerts(**filters)

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "ingestion": self.ingestion.get_stats(),
            "store_size": sum(len(points) for points in self.store.data.values()),
            "alert_rules": len(self.alerting.rules),
            "active_alerts": len([a for a in self.alerting.alerts if not a.acknowledged]),
        }


# Singleton instance
_telemetry_pipeline: Optional[TelemetryPipeline] = None


def get_telemetry_pipeline() -> TelemetryPipeline:
    """Get or create telemetry pipeline."""
    global _telemetry_pipeline

    if _telemetry_pipeline is None:
        _telemetry_pipeline = TelemetryPipeline()

    return _telemetry_pipeline
