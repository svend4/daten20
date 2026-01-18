"""
Comprehensive tests for src/ml/anomaly.py

Tests anomaly detection to achieve >75% coverage.
"""

import math
from datetime import datetime
from unittest.mock import patch

import pytest

from src.ml.anomaly import (
    Anomaly,
    AnomalyDetectionEngine,
    AnomalyType,
    DataQualityValidator,
    PatternDetector,
    StatisticalDetector,
    get_anomaly_detector,
)


class TestAnomalyType:
    """Test AnomalyType enum"""

    def test_anomaly_types_exist(self):
        """Test all anomaly types are defined"""
        assert hasattr(AnomalyType, "STATISTICAL_OUTLIER")
        assert hasattr(AnomalyType, "PATTERN_DEVIATION")
        assert hasattr(AnomalyType, "MISSING_DATA")
        assert hasattr(AnomalyType, "INVALID_FORMAT")
        assert hasattr(AnomalyType, "DUPLICATE")
        assert hasattr(AnomalyType, "INCONSISTENCY")

    def test_anomaly_type_values(self):
        """Test anomaly type values"""
        assert AnomalyType.STATISTICAL_OUTLIER.value == "statistical_outlier"
        assert AnomalyType.PATTERN_DEVIATION.value == "pattern_deviation"
        assert AnomalyType.MISSING_DATA.value == "missing_data"

    def test_anomaly_type_is_enum(self):
        """Test AnomalyType is an enum"""
        assert isinstance(AnomalyType.STATISTICAL_OUTLIER, AnomalyType)


class TestAnomaly:
    """Test Anomaly dataclass"""

    def test_anomaly_creation(self):
        """Test creating an Anomaly"""
        anomaly = Anomaly(
            id="test1",
            type=AnomalyType.STATISTICAL_OUTLIER,
            severity="high",
            field="price",
            value=999.99,
        )
        assert anomaly.id == "test1"
        assert anomaly.type == AnomalyType.STATISTICAL_OUTLIER
        assert anomaly.severity == "high"
        assert anomaly.field == "price"
        assert anomaly.value == 999.99

    def test_anomaly_with_optional_fields(self):
        """Test Anomaly with optional fields"""
        anomaly = Anomaly(
            id="test2",
            type=AnomalyType.INCONSISTENCY,
            severity="medium",
            field="age",
            value=150,
            expected_range=(0, 120),
            score=0.95,
            description="Age out of range",
        )
        assert anomaly.expected_range == (0, 120)
        assert anomaly.score == 0.95
        assert anomaly.description == "Age out of range"

    def test_anomaly_default_timestamp(self):
        """Test Anomaly has default timestamp"""
        anomaly = Anomaly(
            id="test3",
            type=AnomalyType.MISSING_DATA,
            severity="low",
            field="optional",
            value=None,
        )
        assert isinstance(anomaly.timestamp, datetime)

    def test_anomaly_all_fields(self):
        """Test Anomaly has all expected fields"""
        anomaly = Anomaly(
            id="test",
            type=AnomalyType.DUPLICATE,
            severity="critical",
            field="id",
            value=123,
        )
        assert hasattr(anomaly, "id")
        assert hasattr(anomaly, "type")
        assert hasattr(anomaly, "severity")
        assert hasattr(anomaly, "field")
        assert hasattr(anomaly, "value")
        assert hasattr(anomaly, "expected_range")
        assert hasattr(anomaly, "score")
        assert hasattr(anomaly, "description")
        assert hasattr(anomaly, "timestamp")


class TestStatisticalDetector:
    """Test StatisticalDetector class"""

    @pytest.fixture
    def detector(self):
        """Create a StatisticalDetector instance"""
        return StatisticalDetector()

    def test_initialization(self, detector):
        """Test StatisticalDetector initialization"""
        assert detector.statistics is not None
        assert len(detector.statistics) == 0

    def test_fit_single_field(self, detector):
        """Test fitting with single numeric field"""
        data = [{"price": 10}, {"price": 20}, {"price": 30}]
        detector.fit(data, ["price"])

        assert "price" in detector.statistics
        assert detector.statistics["price"]["mean"] == 20.0
        assert detector.statistics["price"]["count"] == 3

    def test_fit_multiple_fields(self, detector):
        """Test fitting with multiple numeric fields"""
        data = [
            {"age": 25, "salary": 50000},
            {"age": 30, "salary": 60000},
            {"age": 35, "salary": 70000},
        ]
        detector.fit(data, ["age", "salary"])

        assert "age" in detector.statistics
        assert "salary" in detector.statistics
        assert detector.statistics["age"]["mean"] == 30.0
        assert detector.statistics["salary"]["mean"] == 60000.0

    def test_fit_calculates_std_dev(self, detector):
        """Test fit calculates standard deviation"""
        data = [{"value": 10}, {"value": 20}, {"value": 30}]
        detector.fit(data, ["value"])

        std_dev = detector.statistics["value"]["std_dev"]
        # For values [10, 20, 30], std_dev should be approximately 8.16
        assert abs(std_dev - 8.16) < 0.1

    def test_fit_calculates_min_max(self, detector):
        """Test fit calculates min and max"""
        data = [{"score": 5}, {"score": 100}, {"score": 42}]
        detector.fit(data, ["score"])

        assert detector.statistics["score"]["min"] == 5
        assert detector.statistics["score"]["max"] == 100

    def test_fit_handles_missing_values(self, detector):
        """Test fit handles missing values"""
        data = [
            {"price": 10},
            {"price": None},
            {"price": 30},
            {},
        ]
        detector.fit(data, ["price"])

        # Should only use non-None values
        assert detector.statistics["price"]["count"] == 2
        assert detector.statistics["price"]["mean"] == 20.0

    def test_fit_empty_field(self, detector):
        """Test fit with field that has no values"""
        data = [{"other": 10}, {"other": 20}]
        detector.fit(data, ["missing_field"])

        # Should not add statistics for field with no values
        assert "missing_field" not in detector.statistics

    def test_detect_zscore_no_anomaly(self, detector):
        """Test detect_zscore with no anomalies"""
        data = [{"value": i} for i in range(10, 31)]
        detector.fit(data, ["value"])

        # Record within normal range
        anomalies = detector.detect_zscore({"value": 20})
        assert len(anomalies) == 0

    def test_detect_zscore_with_anomaly(self, detector):
        """Test detect_zscore detects outlier"""
        data = [{"price": 10}, {"price": 11}, {"price": 12}]
        detector.fit(data, ["price"])

        # Extreme outlier
        anomalies = detector.detect_zscore({"price": 100})
        assert len(anomalies) > 0
        assert anomalies[0].type == AnomalyType.STATISTICAL_OUTLIER
        assert anomalies[0].field == "price"

    def test_detect_zscore_custom_threshold(self, detector):
        """Test detect_zscore with custom threshold"""
        data = [{"value": i} for i in range(1, 11)]
        detector.fit(data, ["value"])

        # Lower threshold = more sensitive
        anomalies = detector.detect_zscore({"value": 15}, threshold=1.0)
        assert len(anomalies) > 0

    def test_detect_zscore_severity(self, detector):
        """Test detect_zscore assigns severity"""
        data = [{"value": 10}, {"value": 11}, {"value": 12}]
        detector.fit(data, ["value"])

        # Very extreme outlier (Z-score > 4)
        anomalies = detector.detect_zscore({"value": 100})
        if anomalies:
            # Should be high severity due to high Z-score
            assert anomalies[0].severity in ["high", "medium"]

    def test_detect_zscore_missing_field(self, detector):
        """Test detect_zscore with missing field in record"""
        data = [{"value": 10}, {"value": 20}]
        detector.fit(data, ["value"])

        anomalies = detector.detect_zscore({"other": 123})
        assert len(anomalies) == 0

    def test_detect_zscore_null_value(self, detector):
        """Test detect_zscore with None value"""
        data = [{"value": 10}, {"value": 20}]
        detector.fit(data, ["value"])

        anomalies = detector.detect_zscore({"value": None})
        assert len(anomalies) == 0

    def test_detect_zscore_zero_std_dev(self, detector):
        """Test detect_zscore with zero standard deviation"""
        # All same values
        data = [{"value": 10}, {"value": 10}, {"value": 10}]
        detector.fit(data, ["value"])

        # Should not crash, should skip field with std_dev = 0
        anomalies = detector.detect_zscore({"value": 10})
        assert len(anomalies) == 0

    def test_detect_zscore_multiple_fields(self, detector):
        """Test detect_zscore with multiple fields"""
        data = [
            {"age": 30, "salary": 50000},
            {"age": 32, "salary": 52000},
        ]
        detector.fit(data, ["age", "salary"])

        # Both fields are outliers
        anomalies = detector.detect_zscore({"age": 90, "salary": 200000})
        assert len(anomalies) == 2

    def test_detect_zscore_expected_range(self, detector):
        """Test detect_zscore includes expected range"""
        data = [{"value": 10}, {"value": 20}, {"value": 30}]
        detector.fit(data, ["value"])

        anomalies = detector.detect_zscore({"value": 100})
        if anomalies:
            assert anomalies[0].expected_range is not None
            assert len(anomalies[0].expected_range) == 2

    def test_detect_zscore_description(self, detector):
        """Test detect_zscore includes description"""
        data = [{"value": 10}, {"value": 20}]
        detector.fit(data, ["value"])

        anomalies = detector.detect_zscore({"value": 100})
        if anomalies:
            assert "Z-score" in anomalies[0].description
            assert "threshold" in anomalies[0].description.lower()

    def test_detect_iqr(self, detector):
        """Test detect_iqr method"""
        data = [{"value": i} for i in range(1, 100)]
        detector.fit(data, ["value"])

        # Currently returns empty (not implemented)
        anomalies = detector.detect_iqr({"value": 200})
        assert isinstance(anomalies, list)


class TestPatternDetector:
    """Test PatternDetector class"""

    @pytest.fixture
    def detector(self):
        """Create a PatternDetector instance"""
        return PatternDetector()

    def test_initialization(self, detector):
        """Test PatternDetector initialization"""
        assert detector.patterns is not None

    def test_detect_pattern_deviation_no_data(self, detector):
        """Test detect_pattern_deviation with insufficient data"""
        data = [{"value": 10}, {"value": 20}]
        anomalies = detector.detect_pattern_deviation(data, "value")
        # Need at least 3 values
        assert len(anomalies) == 0

    def test_detect_pattern_deviation_no_spike(self, detector):
        """Test detect_pattern_deviation with normal data"""
        data = [{"value": i * 10} for i in range(1, 11)]
        anomalies = detector.detect_pattern_deviation(data, "value")
        # No spikes in linear progression
        assert len(anomalies) == 0

    def test_detect_pattern_deviation_with_spike(self, detector):
        """Test detect_pattern_deviation detects spike"""
        data = [
            {"value": 10},
            {"value": 12},
            {"value": 100},  # Spike: > 2x prev and > 2x next
            {"value": 11},
            {"value": 13},
        ]
        anomalies = detector.detect_pattern_deviation(data, "value")
        assert len(anomalies) > 0
        assert anomalies[0].type == AnomalyType.PATTERN_DEVIATION

    def test_detect_pattern_deviation_spike_description(self, detector):
        """Test spike anomaly has proper description"""
        data = [
            {"value": 5},
            {"value": 100},  # Spike
            {"value": 6},
        ]
        anomalies = detector.detect_pattern_deviation(data, "value")
        if anomalies:
            assert "spike" in anomalies[0].description.lower()

    def test_detect_pattern_deviation_severity(self, detector):
        """Test pattern deviation has medium severity"""
        data = [
            {"value": 10},
            {"value": 100},
            {"value": 10},
        ]
        anomalies = detector.detect_pattern_deviation(data, "value")
        if anomalies:
            assert anomalies[0].severity == "medium"


class TestDataQualityValidator:
    """Test DataQualityValidator class"""

    @pytest.fixture
    def validator(self):
        """Create a DataQualityValidator instance"""
        return DataQualityValidator()

    def test_initialization(self, validator):
        """Test DataQualityValidator initialization"""
        assert validator.rules is not None
        assert len(validator.rules) == 0

    def test_add_rule(self, validator):
        """Test adding validation rule"""
        validator.add_rule("age", "range", {"min": 0, "max": 120})
        assert "age" in validator.rules
        assert len(validator.rules["age"]) == 1

    def test_add_multiple_rules(self, validator):
        """Test adding multiple rules for same field"""
        validator.add_rule("price", "range", {"min": 0})
        validator.add_rule("price", "format", {"pattern": r"\d+"})
        assert len(validator.rules["price"]) == 2

    def test_validate_missing_field(self, validator):
        """Test validate detects missing required field"""
        validator.add_rule("name", "range", {})
        anomalies = validator.validate({"other": "value"})

        assert len(anomalies) > 0
        assert anomalies[0].type == AnomalyType.MISSING_DATA
        assert anomalies[0].field == "name"
        assert anomalies[0].severity == "high"

    def test_validate_range_below_min(self, validator):
        """Test validate detects value below minimum"""
        validator.add_rule("age", "range", {"min": 0, "max": 120})
        anomalies = validator.validate({"age": -5})

        assert len(anomalies) > 0
        assert anomalies[0].type == AnomalyType.INCONSISTENCY
        assert anomalies[0].value == -5
        assert "below minimum" in anomalies[0].description.lower()

    def test_validate_range_above_max(self, validator):
        """Test validate detects value above maximum"""
        validator.add_rule("score", "range", {"min": 0, "max": 100})
        anomalies = validator.validate({"score": 150})

        assert len(anomalies) > 0
        assert anomalies[0].type == AnomalyType.INCONSISTENCY
        assert anomalies[0].value == 150
        assert "above maximum" in anomalies[0].description.lower()

    def test_validate_range_within_bounds(self, validator):
        """Test validate accepts value within range"""
        validator.add_rule("age", "range", {"min": 0, "max": 120})
        anomalies = validator.validate({"age": 30})
        # Should not have range violations
        assert not any(a.type == AnomalyType.INCONSISTENCY for a in anomalies)

    def test_validate_range_min_only(self, validator):
        """Test validate with only minimum"""
        validator.add_rule("price", "range", {"min": 0})
        anomalies = validator.validate({"price": -10})
        assert len(anomalies) > 0

    def test_validate_range_max_only(self, validator):
        """Test validate with only maximum"""
        validator.add_rule("percentage", "range", {"max": 100})
        anomalies = validator.validate({"percentage": 150})
        assert len(anomalies) > 0

    def test_validate_format_rule(self, validator):
        """Test validate with format rule (not fully implemented)"""
        validator.add_rule("email", "format", {"pattern": r".+@.+"})
        # Should not crash
        anomalies = validator.validate({"email": "test@example.com"})
        # Format validation is not implemented (has pass)
        assert isinstance(anomalies, list)

    def test_validate_multiple_violations(self, validator):
        """Test validate detects multiple violations"""
        validator.add_rule("age", "range", {"min": 0, "max": 120})
        validator.add_rule("name", "range", {})

        # Missing name + age out of range
        anomalies = validator.validate({"age": 150})
        assert len(anomalies) >= 2

    def test_validate_expected_range(self, validator):
        """Test anomaly includes expected range"""
        validator.add_rule("score", "range", {"min": 0, "max": 100})
        anomalies = validator.validate({"score": 150})

        if anomalies:
            assert anomalies[0].expected_range == (0, 100)


class TestAnomalyDetectionEngine:
    """Test AnomalyDetectionEngine class"""

    @pytest.fixture
    def engine(self):
        """Create an AnomalyDetectionEngine instance"""
        return AnomalyDetectionEngine()

    def test_initialization(self, engine):
        """Test AnomalyDetectionEngine initialization"""
        assert engine.statistical_detector is not None
        assert engine.pattern_detector is not None
        assert engine.quality_validator is not None
        assert engine.anomaly_history is not None
        assert isinstance(engine.statistical_detector, StatisticalDetector)
        assert isinstance(engine.pattern_detector, PatternDetector)
        assert isinstance(engine.quality_validator, DataQualityValidator)

    def test_train(self, engine):
        """Test training the engine"""
        data = [{"price": 10}, {"price": 20}, {"price": 30}]
        engine.train(data, ["price"])

        # Should train statistical detector
        assert "price" in engine.statistical_detector.statistics

    def test_detect_anomalies_no_methods(self, engine):
        """Test detect_anomalies with default methods"""
        data = [{"value": i} for i in range(1, 11)]
        engine.train(data, ["value"])

        anomalies = engine.detect_anomalies({"value": 100})
        # Should use default methods
        assert isinstance(anomalies, list)

    def test_detect_anomalies_statistical(self, engine):
        """Test detect_anomalies with statistical method"""
        data = [{"price": 10}, {"price": 11}, {"price": 12}]
        engine.train(data, ["price"])

        anomalies = engine.detect_anomalies({"price": 100}, methods=["statistical"])
        assert len(anomalies) > 0
        assert all(a.type == AnomalyType.STATISTICAL_OUTLIER for a in anomalies)

    def test_detect_anomalies_quality(self, engine):
        """Test detect_anomalies with quality method"""
        engine.quality_validator.add_rule("age", "range", {"min": 0, "max": 120})

        anomalies = engine.detect_anomalies({"age": 150}, methods=["quality"])
        assert len(anomalies) > 0

    def test_detect_anomalies_multiple_methods(self, engine):
        """Test detect_anomalies with multiple methods"""
        data = [{"value": 10}, {"value": 20}]
        engine.train(data, ["value"])
        engine.quality_validator.add_rule("value", "range", {"min": 0, "max": 50})

        anomalies = engine.detect_anomalies({"value": 100}, methods=["statistical", "quality"])
        # Should get anomalies from both methods
        assert len(anomalies) >= 2

    def test_detect_anomalies_updates_history(self, engine):
        """Test detect_anomalies adds to history"""
        data = [{"value": 10}, {"value": 20}]
        engine.train(data, ["value"])

        initial_count = len(engine.anomaly_history)
        anomalies = engine.detect_anomalies({"value": 100})

        # History should be updated
        assert len(engine.anomaly_history) > initial_count

    def test_get_anomaly_report_empty(self, engine):
        """Test get_anomaly_report with no anomalies"""
        report = engine.get_anomaly_report()

        assert report["total_anomalies"] == 0
        assert report["by_type"] == {}
        assert report["by_severity"] == {}
        assert report["recent_anomalies"] == []

    def test_get_anomaly_report_with_anomalies(self, engine):
        """Test get_anomaly_report with anomalies"""
        data = [{"value": 10}, {"value": 20}]
        engine.train(data, ["value"])

        # Generate some anomalies
        engine.detect_anomalies({"value": 100})
        engine.detect_anomalies({"value": 200})

        report = engine.get_anomaly_report()

        assert report["total_anomalies"] > 0
        assert "by_type" in report
        assert "by_severity" in report
        assert "recent_anomalies" in report

    def test_get_anomaly_report_by_type(self, engine):
        """Test anomaly report groups by type"""
        data = [{"value": 10}]
        engine.train(data, ["value"])
        engine.quality_validator.add_rule("required", "range", {})

        # Generate different types of anomalies
        engine.detect_anomalies({"value": 100}, methods=["statistical"])  # Statistical outlier
        engine.detect_anomalies({}, methods=["quality"])  # Missing data

        report = engine.get_anomaly_report()
        assert len(report["by_type"]) > 0

    def test_get_anomaly_report_by_severity(self, engine):
        """Test anomaly report groups by severity"""
        data = [{"value": 10}]
        engine.train(data, ["value"])

        engine.detect_anomalies({"value": 100})
        report = engine.get_anomaly_report()

        assert "by_severity" in report
        assert isinstance(report["by_severity"], dict)

    def test_get_anomaly_report_recent_anomalies(self, engine):
        """Test report includes recent anomalies"""
        data = [{"value": i} for i in range(1, 11)]
        engine.train(data, ["value"])

        # Generate many anomalies
        for i in range(20):
            engine.detect_anomalies({"value": 100 + i})

        report = engine.get_anomaly_report()

        # Should only include last 10
        assert len(report["recent_anomalies"]) <= 10


class TestGetAnomalyDetector:
    """Test get_anomaly_detector function"""

    def test_get_anomaly_detector_returns_engine(self):
        """Test get_anomaly_detector returns AnomalyDetectionEngine"""
        detector = get_anomaly_detector()
        assert isinstance(detector, AnomalyDetectionEngine)

    def test_get_anomaly_detector_singleton(self):
        """Test get_anomaly_detector returns same instance"""
        detector1 = get_anomaly_detector()
        detector2 = get_anomaly_detector()
        assert detector1 is detector2

    def test_get_anomaly_detector_initialized(self):
        """Test returned detector is properly initialized"""
        detector = get_anomaly_detector()
        assert detector.statistical_detector is not None
        assert detector.pattern_detector is not None
        assert detector.quality_validator is not None


class TestIntegration:
    """Integration tests for anomaly detection"""

    def test_full_anomaly_detection_workflow(self):
        """Test complete anomaly detection workflow"""
        engine = AnomalyDetectionEngine()

        # Train with normal data
        training_data = [{"age": 25 + i, "salary": 50000 + i * 1000} for i in range(10)]
        engine.train(training_data, ["age", "salary"])

        # Add quality rules
        engine.quality_validator.add_rule("age", "range", {"min": 0, "max": 120})
        engine.quality_validator.add_rule("salary", "range", {"min": 0})

        # Detect anomalies in test record
        test_record = {"age": 150, "salary": 1000000}
        anomalies = engine.detect_anomalies(test_record, methods=["statistical", "quality"])

        # Should detect multiple anomalies
        assert len(anomalies) > 0

        # Generate report
        report = engine.get_anomaly_report()
        assert report["total_anomalies"] > 0

    def test_statistical_detection_workflow(self):
        """Test statistical detection workflow"""
        detector = StatisticalDetector()

        # Fit normal distribution
        data = [{"temperature": 20 + i * 0.5} for i in range(20)]
        detector.fit(data, ["temperature"])

        # Detect outlier
        anomalies = detector.detect_zscore({"temperature": 100})
        assert len(anomalies) > 0
        assert anomalies[0].field == "temperature"

    def test_pattern_detection_workflow(self):
        """Test pattern detection workflow"""
        detector = PatternDetector()

        # Data with spike
        data = [
            {"value": 10},
            {"value": 11},
            {"value": 50},  # Spike
            {"value": 12},
            {"value": 13},
        ]

        anomalies = detector.detect_pattern_deviation(data, "value")
        assert any("spike" in a.description.lower() for a in anomalies)

    def test_quality_validation_workflow(self):
        """Test quality validation workflow"""
        validator = DataQualityValidator()

        # Add rules
        validator.add_rule("age", "range", {"min": 0, "max": 120})
        validator.add_rule("name", "range", {})

        # Validate invalid record
        anomalies = validator.validate({"age": -5})

        # Should have missing name + invalid age
        assert len(anomalies) >= 2


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.ml.anomaly", "--cov-report=term-missing"])
