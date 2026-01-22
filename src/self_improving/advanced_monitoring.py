"""
Advanced Self-Monitoring & Metrics Tracking Module

Real-time performance monitoring with:
- Multi-dimensional metrics tracking
- Anomaly detection
- Trend analysis
- Predictive performance modeling
- Resource utilization tracking
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
import statistics


class MetricType(Enum):
    """Types of metrics to track"""
    PERFORMANCE = "performance"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY = "memory"
    ACCURACY = "accuracy"
    LOSS = "loss"
    CUSTOM = "custom"


class AnomalyType(Enum):
    """Types of anomalies detected"""
    SPIKE = "spike"
    DIP = "dip"
    PLATEAU = "plateau"
    DEGRADATION = "degradation"
    OSCILLATION = "oscillation"


@dataclass
class MetricSnapshot:
    """Single metric snapshot at a point in time"""
    timestamp: float
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Anomaly:
    """Detected anomaly in metrics"""
    anomaly_id: str
    anomaly_type: AnomalyType
    metric_type: MetricType
    timestamp: float
    severity: float  # 0.0 - 1.0
    description: str
    affected_values: List[float]


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    metric_type: MetricType
    trend_direction: str  # "improving", "degrading", "stable"
    slope: float
    confidence: float
    prediction_next: float
    time_window: int


class AdvancedMonitor:
    """
    Advanced monitoring system for self-improving AI.

    Tracks multiple metrics, detects anomalies, analyzes trends,
    and predicts future performance.
    """

    def __init__(self,
                 history_size: int = 1000,
                 anomaly_threshold: float = 2.0):
        """
        Initialize advanced monitor.

        Args:
            history_size: Maximum number of snapshots to keep per metric
            anomaly_threshold: Standard deviations for anomaly detection
        """
        self.history_size = history_size
        self.anomaly_threshold = anomaly_threshold

        # Metric histories (metric_type -> deque of snapshots)
        self.metric_histories: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=history_size)
            for metric_type in MetricType
        }

        # Detected anomalies
        self.anomalies: List[Anomaly] = []

        # Performance baselines
        self.baselines: Dict[MetricType, float] = {}

        # Monitoring state
        self.monitoring_start_time = time.time()
        self.total_snapshots = 0

    def record_metric(self,
                     metric_type: MetricType,
                     value: float,
                     metadata: Optional[Dict[str, Any]] = None) -> MetricSnapshot:
        """
        Record a metric snapshot.

        Args:
            metric_type: Type of metric
            value: Metric value
            metadata: Optional additional information

        Returns:
            Created metric snapshot
        """
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            metric_type=metric_type,
            value=value,
            metadata=metadata or {}
        )

        self.metric_histories[metric_type].append(snapshot)
        self.total_snapshots += 1

        # Check for anomalies
        self._detect_anomaly(metric_type, value)

        return snapshot

    def _detect_anomaly(self, metric_type: MetricType, current_value: float):
        """
        Detect anomalies in metric values.

        Uses statistical analysis (z-score) to identify outliers.
        """
        history = self.metric_histories[metric_type]

        if len(history) < 10:  # Need sufficient history
            return

        # Get recent values
        recent_values = [s.value for s in list(history)[-50:]]

        # Calculate statistics
        mean = statistics.mean(recent_values)
        try:
            stdev = statistics.stdev(recent_values)
        except statistics.StatisticsError:
            return  # All values are identical

        if stdev == 0:
            return

        # Z-score
        z_score = abs((current_value - mean) / stdev)

        if z_score > self.anomaly_threshold:
            # Determine anomaly type
            if current_value > mean:
                anomaly_type = AnomalyType.SPIKE
            else:
                anomaly_type = AnomalyType.DIP

            anomaly = Anomaly(
                anomaly_id=f"anomaly_{len(self.anomalies)}_{time.time()}",
                anomaly_type=anomaly_type,
                metric_type=metric_type,
                timestamp=time.time(),
                severity=min(z_score / 5.0, 1.0),  # Normalize severity
                description=f"{anomaly_type.value} detected: {current_value:.4f} (mean: {mean:.4f}, z-score: {z_score:.2f})",
                affected_values=[current_value]
            )

            self.anomalies.append(anomaly)

    def analyze_trend(self,
                     metric_type: MetricType,
                     window_size: int = 50) -> TrendAnalysis:
        """
        Analyze trend for a metric.

        Args:
            metric_type: Type of metric to analyze
            window_size: Number of recent snapshots to consider

        Returns:
            Trend analysis results
        """
        history = self.metric_histories[metric_type]

        if len(history) < 2:
            return TrendAnalysis(
                metric_type=metric_type,
                trend_direction="unknown",
                slope=0.0,
                confidence=0.0,
                prediction_next=0.0,
                time_window=0
            )

        # Get recent values
        recent = list(history)[-window_size:]
        values = [s.value for s in recent]

        # Simple linear regression (least squares)
        n = len(values)
        x = list(range(n))

        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Determine trend direction
        if abs(slope) < 0.001:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "improving"
        else:
            trend_direction = "degrading"

        # Calculate confidence (R-squared)
        if len(values) > 1:
            try:
                variance = statistics.variance(values)
                if variance == 0:
                    confidence = 1.0
                else:
                    # Simplified R-squared calculation
                    intercept = y_mean - slope * x_mean
                    predictions = [slope * xi + intercept for xi in x]
                    residuals = sum((values[i] - predictions[i]) ** 2 for i in range(n))
                    total_variance = sum((v - y_mean) ** 2 for v in values)
                    confidence = max(0.0, 1.0 - (residuals / total_variance if total_variance != 0 else 0))
            except:
                confidence = 0.5
        else:
            confidence = 0.0

        # Predict next value
        intercept = y_mean - slope * x_mean
        prediction_next = slope * n + intercept

        return TrendAnalysis(
            metric_type=metric_type,
            trend_direction=trend_direction,
            slope=slope,
            confidence=confidence,
            prediction_next=prediction_next,
            time_window=len(recent)
        )

    def set_baseline(self, metric_type: MetricType, baseline_value: float):
        """Set performance baseline for a metric"""
        self.baselines[metric_type] = baseline_value

    def get_baseline_comparison(self, metric_type: MetricType) -> Optional[Dict[str, Any]]:
        """
        Compare current performance to baseline.

        Args:
            metric_type: Type of metric

        Returns:
            Comparison statistics or None if no baseline set
        """
        if metric_type not in self.baselines:
            return None

        history = self.metric_histories[metric_type]
        if len(history) == 0:
            return None

        baseline = self.baselines[metric_type]
        current = history[-1].value

        improvement = ((current - baseline) / baseline) * 100 if baseline != 0 else 0.0

        return {
            "baseline": baseline,
            "current": current,
            "improvement_percent": improvement,
            "is_better": current > baseline if metric_type != MetricType.LOSS else current < baseline
        }

    def get_summary_statistics(self, metric_type: MetricType) -> Dict[str, Any]:
        """
        Get summary statistics for a metric.

        Args:
            metric_type: Type of metric

        Returns:
            Summary statistics dictionary
        """
        history = self.metric_histories[metric_type]

        if len(history) == 0:
            return {
                "count": 0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
                "stddev": 0.0
            }

        values = [s.value for s in history]

        stats = {
            "count": len(values),
            "mean": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values)
        }

        if len(values) >= 2:
            stats["stddev"] = statistics.stdev(values)
        else:
            stats["stddev"] = 0.0

        return stats

    def get_recent_anomalies(self,
                            count: int = 10,
                            metric_type: Optional[MetricType] = None) -> List[Anomaly]:
        """
        Get recent anomalies.

        Args:
            count: Maximum number of anomalies to return
            metric_type: Optional filter by metric type

        Returns:
            List of recent anomalies
        """
        anomalies = self.anomalies

        if metric_type:
            anomalies = [a for a in anomalies if a.metric_type == metric_type]

        return sorted(anomalies, key=lambda a: a.timestamp, reverse=True)[:count]

    def predict_performance(self,
                           metric_type: MetricType,
                           steps_ahead: int = 10) -> List[float]:
        """
        Predict future performance using trend analysis.

        Args:
            metric_type: Type of metric
            steps_ahead: Number of steps to predict ahead

        Returns:
            List of predicted values
        """
        trend = self.analyze_trend(metric_type)

        # Use linear extrapolation
        current_value = trend.prediction_next
        predictions = []

        for i in range(steps_ahead):
            predicted = current_value + (trend.slope * i)
            predictions.append(predicted)

        return predictions

    def get_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report.

        Returns:
            Monitoring report dictionary
        """
        report = {
            "monitoring_duration": time.time() - self.monitoring_start_time,
            "total_snapshots": self.total_snapshots,
            "metrics": {},
            "anomalies": {
                "total": len(self.anomalies),
                "by_severity": {
                    "high": len([a for a in self.anomalies if a.severity > 0.7]),
                    "medium": len([a for a in self.anomalies if 0.3 < a.severity <= 0.7]),
                    "low": len([a for a in self.anomalies if a.severity <= 0.3])
                },
                "recent": [
                    {
                        "type": a.anomaly_type.value,
                        "metric": a.metric_type.value,
                        "severity": a.severity,
                        "description": a.description
                    }
                    for a in self.get_recent_anomalies(5)
                ]
            }
        }

        # Add metrics summaries
        for metric_type in MetricType:
            if len(self.metric_histories[metric_type]) > 0:
                stats = self.get_summary_statistics(metric_type)
                trend = self.analyze_trend(metric_type)
                baseline_comp = self.get_baseline_comparison(metric_type)

                report["metrics"][metric_type.value] = {
                    "statistics": stats,
                    "trend": {
                        "direction": trend.trend_direction,
                        "slope": trend.slope,
                        "confidence": trend.confidence
                    },
                    "baseline_comparison": baseline_comp
                }

        return report


# Singleton
_advanced_monitor_instance = None


def get_advanced_monitor() -> AdvancedMonitor:
    """Get singleton instance of AdvancedMonitor"""
    global _advanced_monitor_instance
    if _advanced_monitor_instance is None:
        _advanced_monitor_instance = AdvancedMonitor()
    return _advanced_monitor_instance
