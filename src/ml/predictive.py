"""
Predictive Analytics

Provides predictive models:
- Time series forecasting
- Trend analysis
- Regression models
- Classification models
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Forecast:
    """Forecast result"""

    timestamp: datetime
    value: float
    confidence_lower: float
    confidence_upper: float


class TimeSeriesForecaster:
    """Time series forecasting"""

    def __init__(self):
        self.history: List[Tuple[datetime, float]] = []

    def add_data_point(self, timestamp: datetime, value: float):
        """Add data point"""
        self.history.append((timestamp, value))
        self.history.sort(key=lambda x: x[0])

    def forecast(self, periods: int = 7) -> List[Forecast]:
        """Forecast future values"""
        if len(self.history) < 3:
            return []

        # Simple linear regression
        values = [v for _, v in self.history]
        trend = self._calculate_trend(values)
        mean = sum(values) / len(values)

        forecasts = []
        last_timestamp = self.history[-1][0]

        for i in range(1, periods + 1):
            # Linear projection
            predicted_value = values[-1] + (trend * i)

            # Confidence interval (±20%)
            confidence_range = predicted_value * 0.2

            forecast_timestamp = last_timestamp + timedelta(days=i)

            forecasts.append(
                Forecast(
                    timestamp=forecast_timestamp,
                    value=predicted_value,
                    confidence_lower=predicted_value - confidence_range,
                    confidence_upper=predicted_value + confidence_range,
                )
            )

        return forecasts

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope)"""
        n = len(values)
        if n < 2:
            return 0.0

        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator


class TrendAnalyzer:
    """Trend analysis"""

    def analyze_trend(self, data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Analyze trend in data"""
        if len(data) < 2:
            return {"trend": "insufficient_data"}

        values = [v for _, v in data]

        # Calculate trend
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        change_pct = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0

        if change_pct > 10:
            trend = "increasing"
        elif change_pct < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percentage": change_pct,
            "first_half_avg": first_avg,
            "second_half_avg": second_avg,
        }


class PredictiveAnalyticsEngine:
    """Main predictive analytics engine"""

    def __init__(self):
        self.forecaster = TimeSeriesForecaster()
        self.trend_analyzer = TrendAnalyzer()

    def forecast(self, periods: int = 7) -> List[Forecast]:
        """Generate forecast"""
        return self.forecaster.forecast(periods)

    def analyze(self, data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Analyze trends"""
        return self.trend_analyzer.analyze_trend(data)


# Global instance
_predictive_engine: Optional[PredictiveAnalyticsEngine] = None


def get_predictive_engine() -> PredictiveAnalyticsEngine:
    """Get global predictive analytics engine"""
    global _predictive_engine

    if _predictive_engine is None:
        _predictive_engine = PredictiveAnalyticsEngine()

    return _predictive_engine
