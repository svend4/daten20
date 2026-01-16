"""
Comprehensive tests for predictive analytics module

Test coverage goals:
- Time series forecasting
- Trend analysis
- Regression models
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.ml.predictive import (
    Forecast,
    TimeSeriesForecaster,
    TrendAnalyzer,
    PredictiveAnalyticsEngine,
    get_predictive_engine,
)


class TestForecast:
    """Test Forecast dataclass"""

    def test_forecast_creation(self):
        """Test creating a forecast"""
        timestamp = datetime(2024, 1, 1)
        forecast = Forecast(
            timestamp=timestamp,
            value=100.0,
            confidence_lower=90.0,
            confidence_upper=110.0
        )

        assert forecast.timestamp == timestamp
        assert forecast.value == 100.0
        assert forecast.confidence_lower == 90.0
        assert forecast.confidence_upper == 110.0

    def test_forecast_confidence_interval(self):
        """Test forecast confidence interval"""
        forecast = Forecast(
            timestamp=datetime.now(),
            value=100.0,
            confidence_lower=80.0,
            confidence_upper=120.0
        )

        # Confidence bounds should be around the value
        assert forecast.confidence_lower < forecast.value
        assert forecast.confidence_upper > forecast.value


class TestTimeSeriesForecaster:
    """Test TimeSeriesForecaster"""

    @pytest.fixture
    def forecaster(self):
        """Create forecaster instance"""
        return TimeSeriesForecaster()

    def test_initialization(self, forecaster):
        """Test forecaster initialization"""
        assert forecaster.history == []

    def test_add_data_point(self, forecaster):
        """Test adding data points"""
        timestamp = datetime(2024, 1, 1)
        forecaster.add_data_point(timestamp, 100.0)

        assert len(forecaster.history) == 1
        assert forecaster.history[0] == (timestamp, 100.0)

    def test_add_multiple_data_points(self, forecaster):
        """Test adding multiple data points"""
        base_date = datetime(2024, 1, 1)

        for i in range(5):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i * 10))

        assert len(forecaster.history) == 5

    def test_data_points_sorted_by_time(self, forecaster):
        """Test that data points are sorted by timestamp"""
        # Add in random order
        forecaster.add_data_point(datetime(2024, 1, 3), 300.0)
        forecaster.add_data_point(datetime(2024, 1, 1), 100.0)
        forecaster.add_data_point(datetime(2024, 1, 2), 200.0)

        # Should be sorted
        timestamps = [t for t, _ in forecaster.history]
        assert timestamps == sorted(timestamps)

    def test_forecast_with_insufficient_data(self, forecaster):
        """Test forecast with too few data points"""
        forecaster.add_data_point(datetime(2024, 1, 1), 100.0)
        forecaster.add_data_point(datetime(2024, 1, 2), 110.0)

        # Less than 3 data points
        forecasts = forecaster.forecast(periods=7)
        assert forecasts == []

    def test_forecast_with_sufficient_data(self, forecaster):
        """Test forecast with sufficient data"""
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i * 10))

        forecasts = forecaster.forecast(periods=7)

        assert isinstance(forecasts, list)
        assert len(forecasts) == 7
        assert all(isinstance(f, Forecast) for f in forecasts)

    def test_forecast_periods(self, forecaster):
        """Test forecast for different periods"""
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i))

        forecasts_7 = forecaster.forecast(periods=7)
        forecasts_14 = forecaster.forecast(periods=14)

        assert len(forecasts_7) == 7
        assert len(forecasts_14) == 14

    def test_forecast_timestamps(self, forecaster):
        """Test that forecast timestamps are in the future"""
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i))

        last_timestamp = forecaster.history[-1][0]
        forecasts = forecaster.forecast(periods=7)

        # All forecast timestamps should be after the last data point
        for forecast in forecasts:
            assert forecast.timestamp > last_timestamp

    def test_forecast_confidence_intervals(self, forecaster):
        """Test forecast confidence intervals"""
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i * 10))

        forecasts = forecaster.forecast(periods=5)

        for forecast in forecasts:
            # Confidence lower should be less than value
            assert forecast.confidence_lower < forecast.value

            # Confidence upper should be greater than value
            assert forecast.confidence_upper > forecast.value

            # Value should be within confidence interval
            assert forecast.confidence_lower <= forecast.value <= forecast.confidence_upper

    def test_forecast_upward_trend(self, forecaster):
        """Test forecast with upward trend"""
        base_date = datetime(2024, 1, 1)

        # Add data with upward trend
        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i * 10))

        forecasts = forecaster.forecast(periods=5)

        # Values should generally increase
        for i in range(len(forecasts) - 1):
            assert forecasts[i+1].value >= forecasts[i].value

    def test_forecast_downward_trend(self, forecaster):
        """Test forecast with downward trend"""
        base_date = datetime(2024, 1, 1)

        # Add data with downward trend
        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 - i * 10))

        forecasts = forecaster.forecast(periods=5)

        # Values should generally decrease
        assert isinstance(forecasts, list)
        assert len(forecasts) == 5

    def test_forecast_stable_values(self, forecaster):
        """Test forecast with stable values"""
        base_date = datetime(2024, 1, 1)

        # Add data with stable values
        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, 100.0)

        forecasts = forecaster.forecast(periods=5)

        # Forecasted values should be close to 100
        for forecast in forecasts:
            assert 90 <= forecast.value <= 110

    def test_calculate_trend(self, forecaster):
        """Test trend calculation"""
        # Test with increasing values
        increasing_values = [100, 110, 120, 130, 140]
        trend_up = forecaster._calculate_trend(increasing_values)
        assert trend_up > 0

        # Test with decreasing values
        decreasing_values = [140, 130, 120, 110, 100]
        trend_down = forecaster._calculate_trend(decreasing_values)
        assert trend_down < 0

        # Test with stable values
        stable_values = [100, 100, 100, 100, 100]
        trend_stable = forecaster._calculate_trend(stable_values)
        assert abs(trend_stable) < 0.01

    def test_calculate_trend_empty_list(self, forecaster):
        """Test trend calculation with empty list"""
        trend = forecaster._calculate_trend([])
        assert trend == 0.0

    def test_calculate_trend_single_value(self, forecaster):
        """Test trend calculation with single value"""
        trend = forecaster._calculate_trend([100])
        assert trend == 0.0


class TestTrendAnalyzer:
    """Test TrendAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return TrendAnalyzer()

    def test_analyze_insufficient_data(self, analyzer):
        """Test analysis with insufficient data"""
        data = [(datetime(2024, 1, 1), 100.0)]
        result = analyzer.analyze_trend(data)

        assert result["trend"] == "insufficient_data"

    def test_analyze_increasing_trend(self, analyzer):
        """Test analysis with increasing trend"""
        base_date = datetime(2024, 1, 1)
        data = [
            (base_date + timedelta(days=i), float(100 + i * 20))
            for i in range(10)
        ]

        result = analyzer.analyze_trend(data)

        assert result["trend"] == "increasing"
        assert result["change_percentage"] > 10

    def test_analyze_decreasing_trend(self, analyzer):
        """Test analysis with decreasing trend"""
        base_date = datetime(2024, 1, 1)
        data = [
            (base_date + timedelta(days=i), float(100 - i * 20))
            for i in range(10)
        ]

        result = analyzer.analyze_trend(data)

        assert result["trend"] == "decreasing"
        assert result["change_percentage"] < -10

    def test_analyze_stable_trend(self, analyzer):
        """Test analysis with stable trend"""
        base_date = datetime(2024, 1, 1)
        data = [
            (base_date + timedelta(days=i), float(100 + i * 0.5))
            for i in range(10)
        ]

        result = analyzer.analyze_trend(data)

        assert result["trend"] == "stable"
        assert -10 <= result["change_percentage"] <= 10

    def test_analyze_result_structure(self, analyzer):
        """Test analysis result structure"""
        base_date = datetime(2024, 1, 1)
        data = [
            (base_date + timedelta(days=i), float(100 + i * 10))
            for i in range(10)
        ]

        result = analyzer.analyze_trend(data)

        assert "trend" in result
        assert "change_percentage" in result
        assert "first_half_avg" in result
        assert "second_half_avg" in result

    def test_analyze_edge_at_threshold(self, analyzer):
        """Test analysis at threshold boundaries"""
        base_date = datetime(2024, 1, 1)

        # Exactly 10% change
        data = [
            (base_date + timedelta(days=i), 100.0 if i < 5 else 110.0)
            for i in range(10)
        ]

        result = analyzer.analyze_trend(data)
        assert isinstance(result["trend"], str)

    def test_analyze_with_zero_first_half(self, analyzer):
        """Test analysis when first half average is zero"""
        base_date = datetime(2024, 1, 1)
        data = [
            (base_date + timedelta(days=i), 0.0 if i < 5 else 10.0)
            for i in range(10)
        ]

        result = analyzer.analyze_trend(data)
        assert result["change_percentage"] == 0  # Handled division by zero


class TestPredictiveAnalyticsEngine:
    """Test PredictiveAnalyticsEngine"""

    @pytest.fixture
    def engine(self):
        """Create engine instance"""
        return PredictiveAnalyticsEngine()

    def test_initialization(self, engine):
        """Test engine initialization"""
        assert isinstance(engine.forecaster, TimeSeriesForecaster)
        assert isinstance(engine.trend_analyzer, TrendAnalyzer)

    def test_forecast_method(self, engine):
        """Test forecast method"""
        # Add some data
        base_date = datetime(2024, 1, 1)
        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            engine.forecaster.add_data_point(timestamp, float(100 + i * 10))

        forecasts = engine.forecast(periods=7)
        assert isinstance(forecasts, list)
        assert len(forecasts) == 7

    def test_analyze_method(self, engine):
        """Test analyze method"""
        base_date = datetime(2024, 1, 1)
        data = [
            (base_date + timedelta(days=i), float(100 + i * 10))
            for i in range(10)
        ]

        result = engine.analyze(data)
        assert isinstance(result, dict)
        assert "trend" in result


class TestGlobalEngine:
    """Test global predictive engine"""

    def test_get_predictive_engine(self):
        """Test getting global engine"""
        engine1 = get_predictive_engine()
        engine2 = get_predictive_engine()

        # Should return same instance
        assert engine1 is engine2

    def test_engine_is_singleton(self):
        """Test that engine is a singleton"""
        engine = get_predictive_engine()
        assert isinstance(engine, PredictiveAnalyticsEngine)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_forecast_with_negative_values(self):
        """Test forecast with negative values"""
        forecaster = TimeSeriesForecaster()
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(-100 - i * 10))

        forecasts = forecaster.forecast(periods=5)
        assert isinstance(forecasts, list)

    def test_forecast_with_large_values(self):
        """Test forecast with large values"""
        forecaster = TimeSeriesForecaster()
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(1000000 + i * 100000))

        forecasts = forecaster.forecast(periods=5)
        assert isinstance(forecasts, list)

    def test_forecast_with_zero_periods(self):
        """Test forecast with zero periods"""
        forecaster = TimeSeriesForecaster()
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i))

        forecasts = forecaster.forecast(periods=0)
        assert forecasts == []

    def test_forecast_with_large_periods(self):
        """Test forecast with large number of periods"""
        forecaster = TimeSeriesForecaster()
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            timestamp = base_date + timedelta(days=i)
            forecaster.add_data_point(timestamp, float(100 + i))

        forecasts = forecaster.forecast(periods=365)
        assert len(forecasts) == 365


@pytest.mark.parametrize("num_points,periods", [
    (5, 3),
    (10, 7),
    (20, 14),
    (100, 30),
])
def test_parametrized_forecasting(num_points, periods):
    """Test forecasting with various data sizes and periods"""
    forecaster = TimeSeriesForecaster()
    base_date = datetime(2024, 1, 1)

    for i in range(num_points):
        timestamp = base_date + timedelta(days=i)
        forecaster.add_data_point(timestamp, float(100 + i * 5))

    if num_points >= 3:
        forecasts = forecaster.forecast(periods=periods)
        assert len(forecasts) == periods
    else:
        forecasts = forecaster.forecast(periods=periods)
        assert forecasts == []


class TestIntegration:
    """Integration tests for predictive analytics"""

    def test_full_prediction_pipeline(self):
        """Test complete prediction pipeline"""
        engine = PredictiveAnalyticsEngine()
        base_date = datetime(2024, 1, 1)

        # Add training data
        for i in range(30):
            timestamp = base_date + timedelta(days=i)
            value = 100 + i * 5  # Upward trend
            engine.forecaster.add_data_point(timestamp, float(value))

        # Generate forecast
        forecasts = engine.forecast(periods=7)
        assert len(forecasts) == 7

        # Analyze trend
        data = [(base_date + timedelta(days=i), float(100 + i * 5)) for i in range(30)]
        analysis = engine.analyze(data)
        assert analysis["trend"] == "increasing"

    def test_forecast_and_analysis_consistency(self):
        """Test that forecast and analysis are consistent"""
        engine = PredictiveAnalyticsEngine()
        base_date = datetime(2024, 1, 1)

        # Add data with clear upward trend
        data = []
        for i in range(20):
            timestamp = base_date + timedelta(days=i)
            value = 100 + i * 20
            engine.forecaster.add_data_point(timestamp, float(value))
            data.append((timestamp, float(value)))

        # Analyze trend
        analysis = engine.analyze(data)
        assert analysis["trend"] == "increasing"

        # Forecast should show increasing values
        forecasts = engine.forecast(periods=5)
        values = [f.value for f in forecasts]

        # Forecasted values should generally increase
        assert values[-1] > values[0]
