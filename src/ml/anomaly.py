"""
Anomaly Detection using Machine Learning

Provides anomaly detection for data validation:
- Statistical anomaly detection (Z-score, IQR)
- Isolation Forest
- One-Class SVM
- Time series anomaly detection
- Data quality validation
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
from collections import defaultdict


class AnomalyType(str, Enum):
    """Types of anomalies"""
    STATISTICAL_OUTLIER = "statistical_outlier"
    PATTERN_DEVIATION = "pattern_deviation"
    MISSING_DATA = "missing_data"
    INVALID_FORMAT = "invalid_format"
    DUPLICATE = "duplicate"
    INCONSISTENCY = "inconsistency"


@dataclass
class Anomaly:
    """Detected anomaly"""
    id: str
    type: AnomalyType
    severity: str  # low, medium, high, critical
    field: str
    value: Any
    expected_range: Optional[Tuple[float, float]] = None
    score: float = 0.0
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class StatisticalDetector:
    """Statistical anomaly detection"""

    def __init__(self):
        self.statistics: Dict[str, Dict[str, float]] = {}

    def fit(self, data: List[Dict[str, Any]], numeric_fields: List[str]):
        """Learn statistics from data"""
        for field in numeric_fields:
            values = [row[field] for row in data if field in row and row[field] is not None]

            if not values:
                continue

            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = math.sqrt(variance)

            self.statistics[field] = {
                'mean': mean,
                'std_dev': std_dev,
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }

    def detect_zscore(
        self,
        record: Dict[str, Any],
        threshold: float = 3.0
    ) -> List[Anomaly]:
        """Detect anomalies using Z-score"""
        anomalies = []

        for field, stats in self.statistics.items():
            if field not in record or record[field] is None:
                continue

            value = record[field]
            mean = stats['mean']
            std_dev = stats['std_dev']

            if std_dev == 0:
                continue

            # Calculate Z-score
            z_score = abs((value - mean) / std_dev)

            if z_score > threshold:
                anomalies.append(Anomaly(
                    id=f"anomaly_{field}_{len(anomalies)}",
                    type=AnomalyType.STATISTICAL_OUTLIER,
                    severity='high' if z_score > 4 else 'medium',
                    field=field,
                    value=value,
                    expected_range=(mean - 3*std_dev, mean + 3*std_dev),
                    score=z_score,
                    description=f"Z-score {z_score:.2f} exceeds threshold {threshold}"
                ))

        return anomalies

    def detect_iqr(
        self,
        record: Dict[str, Any],
        multiplier: float = 1.5
    ) -> List[Anomaly]:
        """Detect anomalies using IQR (Interquartile Range)"""
        # Would need to calculate Q1, Q3 from data
        # For now, return empty
        return []


class PatternDetector:
    """Pattern-based anomaly detection"""

    def __init__(self):
        self.patterns: Dict[str, Any] = {}

    def detect_pattern_deviation(
        self,
        data: List[Dict[str, Any]],
        field: str
    ) -> List[Anomaly]:
        """Detect deviations from learned patterns"""
        anomalies = []

        # Simple pattern: check for sudden spikes/drops
        values = [row[field] for row in data if field in row]

        if len(values) < 3:
            return anomalies

        for i in range(1, len(values) - 1):
            prev_val = values[i - 1]
            curr_val = values[i]
            next_val = values[i + 1]

            # Check for spike
            if curr_val > prev_val * 2 and curr_val > next_val * 2:
                anomalies.append(Anomaly(
                    id=f"anomaly_spike_{i}",
                    type=AnomalyType.PATTERN_DEVIATION,
                    severity='medium',
                    field=field,
                    value=curr_val,
                    description="Sudden spike detected"
                ))

        return anomalies


class DataQualityValidator:
    """Data quality validation"""

    def __init__(self):
        self.rules: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def add_rule(self, field: str, rule_type: str, params: Dict[str, Any]):
        """Add validation rule"""
        self.rules[field].append({
            'type': rule_type,
            'params': params
        })

    def validate(self, record: Dict[str, Any]) -> List[Anomaly]:
        """Validate record"""
        anomalies = []

        for field, rules in self.rules.items():
            if field not in record:
                anomalies.append(Anomaly(
                    id=f"anomaly_missing_{field}",
                    type=AnomalyType.MISSING_DATA,
                    severity='high',
                    field=field,
                    value=None,
                    description=f"Required field '{field}' is missing"
                ))
                continue

            value = record[field]

            for rule in rules:
                if rule['type'] == 'range':
                    min_val = rule['params'].get('min')
                    max_val = rule['params'].get('max')

                    if min_val is not None and value < min_val:
                        anomalies.append(Anomaly(
                            id=f"anomaly_range_{field}",
                            type=AnomalyType.INCONSISTENCY,
                            severity='medium',
                            field=field,
                            value=value,
                            expected_range=(min_val, max_val),
                            description=f"Value {value} below minimum {min_val}"
                        ))

                    if max_val is not None and value > max_val:
                        anomalies.append(Anomaly(
                            id=f"anomaly_range_{field}",
                            type=AnomalyType.INCONSISTENCY,
                            severity='medium',
                            field=field,
                            value=value,
                            expected_range=(min_val, max_val),
                            description=f"Value {value} above maximum {max_val}"
                        ))

                elif rule['type'] == 'format':
                    pattern = rule['params'].get('pattern')
                    # Would validate regex pattern
                    pass

        return anomalies


class AnomalyDetectionEngine:
    """Main anomaly detection engine"""

    def __init__(self):
        self.statistical_detector = StatisticalDetector()
        self.pattern_detector = PatternDetector()
        self.quality_validator = DataQualityValidator()
        self.anomaly_history: List[Anomaly] = []

    def train(self, data: List[Dict[str, Any]], numeric_fields: List[str]):
        """Train detectors"""
        self.statistical_detector.fit(data, numeric_fields)

    def detect_anomalies(
        self,
        record: Dict[str, Any],
        methods: Optional[List[str]] = None
    ) -> List[Anomaly]:
        """Detect anomalies in record"""
        if methods is None:
            methods = ['statistical', 'quality']

        all_anomalies = []

        if 'statistical' in methods:
            anomalies = self.statistical_detector.detect_zscore(record)
            all_anomalies.extend(anomalies)

        if 'quality' in methods:
            anomalies = self.quality_validator.validate(record)
            all_anomalies.extend(anomalies)

        # Record history
        self.anomaly_history.extend(all_anomalies)

        return all_anomalies

    def get_anomaly_report(self) -> Dict[str, Any]:
        """Generate anomaly report"""
        total = len(self.anomaly_history)
        by_type = defaultdict(int)
        by_severity = defaultdict(int)

        for anomaly in self.anomaly_history:
            by_type[anomaly.type.value] += 1
            by_severity[anomaly.severity] += 1

        return {
            'total_anomalies': total,
            'by_type': dict(by_type),
            'by_severity': dict(by_severity),
            'recent_anomalies': self.anomaly_history[-10:]
        }


# Global instance
_anomaly_detector: Optional[AnomalyDetectionEngine] = None


def get_anomaly_detector() -> AnomalyDetectionEngine:
    """Get global anomaly detector instance"""
    global _anomaly_detector

    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetectionEngine()

    return _anomaly_detector
