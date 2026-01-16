#!/usr/bin/env python3
"""
Predictive Analytics Engine

Advanced forecasting and predictive modeling for business metrics.
Supports multiple algorithms and techniques for time series forecasting,
churn prediction, revenue forecasting, and capacity planning.

Key Features:
- ARIMA forecasting (AutoRegressive Integrated Moving Average)
- Prophet integration (Facebook's forecasting tool) - optional
- LSTM models (Long Short-Term Memory neural networks) - optional
- Churn prediction using machine learning
- Revenue forecasting
- Usage pattern prediction
- Capacity planning
- Seasonal trend detection
- Anomaly forecasting
- What-if scenario analysis
- Monte Carlo simulations
- Confidence intervals

Dependencies:
- Required: numpy, pandas, scikit-learn, statsmodels
- Optional: prophet, tensorflow/pytorch (for advanced models)
"""

import json
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Core dependencies (always available)
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. ML features disabled.")

# Optional dependencies
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import acf, adfuller, pacf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Warning: statsmodels not available. ARIMA forecasting disabled.")

try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Info: prophet not available. Prophet forecasting disabled.")


class ForecastMethod(str, Enum):
    """Forecasting methods"""

    ARIMA = "arima"
    PROPHET = "prophet"
    LSTM = "lstm"
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MOVING_AVERAGE = "moving_average"


class PredictionType(str, Enum):
    """Type of prediction"""

    REVENUE = "revenue"
    CHURN = "churn"
    USAGE = "usage"
    CAPACITY = "capacity"
    GROWTH = "growth"


@dataclass
class ForecastResult:
    """Forecast result with confidence intervals"""

    method: ForecastMethod
    predictions: List[float]
    dates: List[datetime]
    confidence_lower: List[float]
    confidence_upper: List[float]
    accuracy_metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChurnPrediction:
    """Churn prediction for a customer"""

    customer_id: str
    churn_probability: float
    risk_level: str  # "low", "medium", "high"
    contributing_factors: List[Dict[str, Any]]
    recommended_actions: List[str]
    prediction_date: datetime = field(default_factory=datetime.now)


@dataclass
class ScenarioAnalysis:
    """What-if scenario analysis result"""

    scenario_name: str
    assumptions: Dict[str, Any]
    predictions: Dict[str, List[float]]
    impact_summary: Dict[str, float]
    confidence_level: float


class ARIMAForecaster:
    """
    ARIMA (AutoRegressive Integrated Moving Average) forecasting

    Suitable for:
    - Time series with trends
    - Seasonal patterns
    - Short to medium-term forecasting
    """

    def __init__(self):
        self.model = None
        self.fitted_values = None

    def fit(
        self,
        data: List[float],
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
    ):
        """
        Fit ARIMA model

        Args:
            data: Historical time series data
            order: (p, d, q) parameters for ARIMA
                p: autoregressive order
                d: differencing order
                q: moving average order
            seasonal_order: (P, D, Q, s) for seasonal ARIMA
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels required for ARIMA forecasting")

        self.model = ARIMA(data, order=order, seasonal_order=seasonal_order)
        self.fitted_model = self.model.fit()
        self.fitted_values = self.fitted_model.fittedvalues

    def forecast(self, steps: int = 30, confidence_level: float = 0.95) -> ForecastResult:
        """
        Generate forecast

        Args:
            steps: Number of periods to forecast
            confidence_level: Confidence interval (default 95%)

        Returns:
            ForecastResult with predictions and confidence intervals
        """
        if self.fitted_model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        # Get forecast
        forecast_result = self.fitted_model.forecast(steps=steps)
        predictions = forecast_result.tolist() if hasattr(forecast_result, "tolist") else [forecast_result]

        # Get confidence intervals
        forecast_obj = self.fitted_model.get_forecast(steps=steps)
        conf_int = forecast_obj.conf_int(alpha=1 - confidence_level)

        # Generate future dates (assuming daily data)
        last_date = datetime.now()
        dates = [last_date + timedelta(days=i + 1) for i in range(steps)]

        # Calculate accuracy metrics on training data
        if self.fitted_values is not None and len(self.fitted_values) > 0:
            # Use in-sample accuracy as proxy
            mse = np.mean(
                (self.fitted_values - self.model.endog[len(self.model.endog) - len(self.fitted_values) :]) ** 2
            )
            rmse = np.sqrt(mse)
            mae = np.mean(
                np.abs(self.fitted_values - self.model.endog[len(self.model.endog) - len(self.fitted_values) :])
            )

            accuracy_metrics = {"mse": float(mse), "rmse": float(rmse), "mae": float(mae)}
        else:
            accuracy_metrics = {}

        return ForecastResult(
            method=ForecastMethod.ARIMA,
            predictions=predictions,
            dates=dates,
            confidence_lower=conf_int.iloc[:, 0].tolist(),
            confidence_upper=conf_int.iloc[:, 1].tolist(),
            accuracy_metrics=accuracy_metrics,
            metadata={"order": self.model.order},
        )

    def detect_stationarity(self, data: List[float]) -> Dict[str, Any]:
        """
        Test for stationarity using Augmented Dickey-Fuller test

        Returns:
            Dictionary with test results
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels required")

        result = adfuller(data)

        return {
            "adf_statistic": result[0],
            "p_value": result[1],
            "is_stationary": result[1] < 0.05,  # 5% significance level
            "critical_values": result[4],
            "used_lag": result[2],
        }


class ProphetForecaster:
    """
    Facebook Prophet forecasting

    Suitable for:
    - Time series with strong seasonal patterns
    - Multiple seasonality (daily, weekly, yearly)
    - Holiday effects
    - Missing data
    - Outliers
    """

    def __init__(self):
        self.model = None

    def fit(
        self,
        dates: List[datetime],
        values: List[float],
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
    ):
        """
        Fit Prophet model

        Args:
            dates: List of dates
            values: Corresponding values
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            daily_seasonality: Enable daily seasonality
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("prophet required. Install with: pip install prophet")

        # Prepare data in Prophet format
        df = pd.DataFrame({"ds": dates, "y": values})

        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
        )

        self.model.fit(df)

    def forecast(self, periods: int = 30) -> ForecastResult:
        """Generate forecast using Prophet"""
        if self.model is None:
            raise ValueError("Model not fitted")

        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods)

        # Generate forecast
        forecast_df = self.model.predict(future)

        # Extract last 'periods' predictions
        predictions = forecast_df["yhat"].tail(periods).tolist()
        dates = forecast_df["ds"].tail(periods).tolist()
        lower = forecast_df["yhat_lower"].tail(periods).tolist()
        upper = forecast_df["yhat_upper"].tail(periods).tolist()

        return ForecastResult(
            method=ForecastMethod.PROPHET,
            predictions=predictions,
            dates=dates,
            confidence_lower=lower,
            confidence_upper=upper,
            accuracy_metrics={},
            metadata={"periods": periods},
        )


class ChurnPredictor:
    """
    Customer churn prediction using machine learning

    Uses features such as:
    - Usage patterns
    - Engagement metrics
    - Support tickets
    - Payment history
    - Tenure
    """

    def __init__(self):
        self.model = None
        self.feature_names = []
        self.feature_importance = {}

    def train(self, training_data: List[Dict[str, Any]], target_column: str = "churned"):
        """
        Train churn prediction model

        Args:
            training_data: List of dictionaries with customer features
            target_column: Name of target variable (1 = churned, 0 = retained)
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        # Convert to DataFrame
        df = pd.DataFrame(training_data)

        # Separate features and target
        X = df.drop(columns=[target_column, "customer_id"], errors="ignore")
        y = df[target_column]

        self.feature_names = X.columns.tolist()

        # Train Random Forest classifier
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

        self.model.fit(X, y)

        # Store feature importance
        for name, importance in zip(self.feature_names, self.model.feature_importances_):
            self.feature_importance[name] = float(importance)

    def predict_churn(self, customer_data: Dict[str, Any]) -> ChurnPrediction:
        """
        Predict churn probability for a customer

        Args:
            customer_data: Dictionary with customer features

        Returns:
            ChurnPrediction object
        """
        if self.model is None:
            raise ValueError("Model not trained")

        customer_id = customer_data.get("customer_id", "unknown")

        # Prepare features
        features = pd.DataFrame([{k: v for k, v in customer_data.items() if k in self.feature_names}])

        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in features.columns:
                features[feature] = 0

        # Reorder columns to match training
        features = features[self.feature_names]

        # Predict probability
        churn_prob = self.model.predict_proba(features)[0][1]

        # Determine risk level
        if churn_prob < 0.3:
            risk_level = "low"
        elif churn_prob < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Get top contributing factors
        contributing_factors = []
        for feature, importance in sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
            contributing_factors.append(
                {"feature": feature, "importance": importance, "value": customer_data.get(feature, 0)}
            )

        # Generate recommendations
        recommendations = self._generate_recommendations(churn_prob, contributing_factors)

        return ChurnPrediction(
            customer_id=customer_id,
            churn_probability=float(churn_prob),
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommended_actions=recommendations,
        )

    def _generate_recommendations(self, churn_prob: float, factors: List[Dict]) -> List[str]:
        """Generate action recommendations based on churn risk"""
        recommendations = []

        if churn_prob > 0.7:
            recommendations.append("Immediate outreach - Customer Success Manager intervention")
            recommendations.append("Offer personalized retention discount")
            recommendations.append("Schedule executive business review")

        elif churn_prob > 0.3:
            recommendations.append("Proactive engagement - Send product tips and best practices")
            recommendations.append("Monitor usage closely")
            recommendations.append("Offer training session or webinar")

        # Factor-specific recommendations
        for factor in factors:
            if factor["feature"] == "support_tickets" and factor["value"] > 5:
                recommendations.append("Address support issues - escalate to senior support")

            if factor["feature"] == "usage_decline_pct" and factor["value"] < -30:
                recommendations.append("Re-engagement campaign - highlight new features")

        return recommendations


class RevenueForecaster:
    """
    Revenue forecasting using multiple methods

    Combines:
    - Historical trends
    - Seasonal patterns
    - Growth rates
    - Expansion/churn effects
    """

    def __init__(self):
        self.historical_data = []
        self.forecast_cache = {}

    def forecast_mrr(
        self,
        historical_mrr: List[Tuple[datetime, float]],
        months: int = 12,
        method: ForecastMethod = ForecastMethod.ARIMA,
    ) -> ForecastResult:
        """
        Forecast Monthly Recurring Revenue

        Args:
            historical_mrr: List of (date, mrr_value) tuples
            months: Number of months to forecast
            method: Forecasting method to use

        Returns:
            ForecastResult with MRR predictions
        """
        # Extract values
        dates = [d[0] for d in historical_mrr]
        values = [d[1] for d in historical_mrr]

        if method == ForecastMethod.ARIMA and STATSMODELS_AVAILABLE:
            forecaster = ARIMAForecaster()
            forecaster.fit(values, order=(1, 1, 1))
            return forecaster.forecast(steps=months)

        elif method == ForecastMethod.PROPHET and PROPHET_AVAILABLE:
            forecaster = ProphetForecaster()
            forecaster.fit(dates, values)
            return forecaster.forecast(periods=months)

        else:
            # Fallback: simple linear regression
            return self._linear_forecast(dates, values, months)

    def _linear_forecast(self, dates: List[datetime], values: List[float], periods: int) -> ForecastResult:
        """Simple linear regression forecast"""
        if not SKLEARN_AVAILABLE:
            # Ultra-simple fallback: use last value
            last_value = values[-1]
            predictions = [last_value] * periods
            last_date = dates[-1]
            future_dates = [last_date + timedelta(days=30 * i) for i in range(1, periods + 1)]

            return ForecastResult(
                method=ForecastMethod.LINEAR_REGRESSION,
                predictions=predictions,
                dates=future_dates,
                confidence_lower=[last_value * 0.9] * periods,
                confidence_upper=[last_value * 1.1] * periods,
                accuracy_metrics={},
            )

        # Convert dates to numeric
        X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
        y = np.array(values)

        # Fit model
        from sklearn.linear_model import LinearRegression

        model = LinearRegression()
        model.fit(X, y)

        # Forecast
        last_day = (dates[-1] - dates[0]).days
        future_X = np.array([last_day + 30 * i for i in range(1, periods + 1)]).reshape(-1, 1)
        predictions = model.predict(future_X).tolist()

        # Generate dates
        future_dates = [dates[-1] + timedelta(days=30 * i) for i in range(1, periods + 1)]

        # Simple confidence intervals (±10%)
        confidence_lower = [p * 0.9 for p in predictions]
        confidence_upper = [p * 1.1 for p in predictions]

        return ForecastResult(
            method=ForecastMethod.LINEAR_REGRESSION,
            predictions=predictions,
            dates=future_dates,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            accuracy_metrics={"r2": float(model.score(X, y))},
        )


class MonteCarloSimulator:
    """
    Monte Carlo simulation for scenario analysis

    Useful for:
    - Revenue uncertainty modeling
    - Risk analysis
    - Capacity planning under uncertainty
    """

    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations

    def simulate_revenue(
        self,
        base_mrr: float,
        growth_rate_mean: float,
        growth_rate_std: float,
        churn_rate_mean: float,
        churn_rate_std: float,
        months: int = 12,
    ) -> Dict[str, Any]:
        """
        Simulate revenue trajectories

        Args:
            base_mrr: Starting MRR
            growth_rate_mean: Average monthly growth rate (e.g., 0.05 = 5%)
            growth_rate_std: Standard deviation of growth rate
            churn_rate_mean: Average monthly churn rate (e.g., 0.03 = 3%)
            churn_rate_std: Standard deviation of churn rate
            months: Number of months to simulate

        Returns:
            Dictionary with simulation results
        """
        if not SKLEARN_AVAILABLE:
            # Simple fallback
            return {
                "mean_trajectory": [base_mrr * (1 + growth_rate_mean) ** i for i in range(months)],
                "percentile_5": [base_mrr * (1 + growth_rate_mean - growth_rate_std) ** i for i in range(months)],
                "percentile_95": [base_mrr * (1 + growth_rate_mean + growth_rate_std) ** i for i in range(months)],
                "simulations": [],
            }

        simulations = []

        for _ in range(self.n_simulations):
            trajectory = [base_mrr]

            for month in range(months):
                # Sample growth and churn rates
                growth = np.random.normal(growth_rate_mean, growth_rate_std)
                churn = np.random.normal(churn_rate_mean, churn_rate_std)

                # Ensure rates are in reasonable bounds
                growth = max(-0.5, min(0.5, growth))
                churn = max(0, min(0.5, churn))

                # Calculate next month's MRR
                current_mrr = trajectory[-1]
                next_mrr = current_mrr * (1 + growth - churn)
                trajectory.append(next_mrr)

            simulations.append(trajectory[1:])  # Exclude base_mrr

        # Calculate statistics
        simulations_array = np.array(simulations)

        mean_trajectory = np.mean(simulations_array, axis=0).tolist()
        percentile_5 = np.percentile(simulations_array, 5, axis=0).tolist()
        percentile_25 = np.percentile(simulations_array, 25, axis=0).tolist()
        percentile_75 = np.percentile(simulations_array, 75, axis=0).tolist()
        percentile_95 = np.percentile(simulations_array, 95, axis=0).tolist()

        return {
            "mean_trajectory": mean_trajectory,
            "percentile_5": percentile_5,
            "percentile_25": percentile_25,
            "percentile_75": percentile_75,
            "percentile_95": percentile_95,
            "simulations": simulations[:100],  # Return subset for visualization
        }


class PredictiveAnalyticsEngine:
    """
    Main Predictive Analytics Engine

    Unified interface for all predictive analytics capabilities.
    """

    def __init__(self):
        self.arima_forecaster = ARIMAForecaster() if STATSMODELS_AVAILABLE else None
        self.prophet_forecaster = ProphetForecaster() if PROPHET_AVAILABLE else None
        self.churn_predictor = ChurnPredictor()
        self.revenue_forecaster = RevenueForecaster()
        self.monte_carlo = MonteCarloSimulator()

        self.models = {}
        self.predictions_cache = {}

    def forecast_metric(
        self,
        metric_name: str,
        historical_data: List[Tuple[datetime, float]],
        periods: int = 30,
        method: ForecastMethod = ForecastMethod.ARIMA,
    ) -> ForecastResult:
        """
        Generic metric forecasting

        Args:
            metric_name: Name of metric (e.g., "api_calls", "storage_gb")
            historical_data: List of (date, value) tuples
            periods: Number of periods to forecast
            method: Forecasting method

        Returns:
            ForecastResult
        """
        cache_key = f"{metric_name}_{method.value}_{periods}"

        if cache_key in self.predictions_cache:
            cached = self.predictions_cache[cache_key]
            if (datetime.now() - cached["timestamp"]).seconds < 3600:  # 1 hour cache
                return cached["result"]

        # Perform forecast
        dates = [d[0] for d in historical_data]
        values = [d[1] for d in historical_data]

        if method == ForecastMethod.ARIMA and self.arima_forecaster:
            self.arima_forecaster.fit(values)
            result = self.arima_forecaster.forecast(steps=periods)

        elif method == ForecastMethod.PROPHET and self.prophet_forecaster:
            self.prophet_forecaster.fit(dates, values)
            result = self.prophet_forecaster.forecast(periods=periods)

        else:
            result = self.revenue_forecaster._linear_forecast(dates, values, periods)

        # Cache result
        self.predictions_cache[cache_key] = {"result": result, "timestamp": datetime.now()}

        return result

    def predict_customer_churn(self, customers: List[Dict[str, Any]]) -> List[ChurnPrediction]:
        """
        Batch churn prediction for multiple customers

        Args:
            customers: List of customer feature dictionaries

        Returns:
            List of ChurnPrediction objects
        """
        predictions = []

        for customer in customers:
            try:
                prediction = self.churn_predictor.predict_churn(customer)
                predictions.append(prediction)
            except Exception as e:
                # Log error but continue processing
                print(f"Error predicting churn for customer {customer.get('customer_id')}: {e}")

        return predictions

    def analyze_scenario(self, scenario_name: str, assumptions: Dict[str, Any]) -> ScenarioAnalysis:
        """
        What-if scenario analysis

        Args:
            scenario_name: Name of scenario
            assumptions: Dictionary of assumptions
                - base_mrr: Starting MRR
                - growth_rate: Expected growth rate
                - churn_rate: Expected churn rate
                - months: Forecast horizon

        Returns:
            ScenarioAnalysis with predictions
        """
        base_mrr = assumptions.get("base_mrr", 10000)
        growth_rate = assumptions.get("growth_rate", 0.05)
        churn_rate = assumptions.get("churn_rate", 0.03)
        months = assumptions.get("months", 12)

        # Run Monte Carlo simulation
        simulation_results = self.monte_carlo.simulate_revenue(
            base_mrr=base_mrr,
            growth_rate_mean=growth_rate,
            growth_rate_std=0.02,
            churn_rate_mean=churn_rate,
            churn_rate_std=0.01,
            months=months,
        )

        # Calculate impact summary
        final_mrr_mean = simulation_results["mean_trajectory"][-1]
        final_mrr_p5 = simulation_results["percentile_5"][-1]
        final_mrr_p95 = simulation_results["percentile_95"][-1]

        impact_summary = {
            "final_mrr_mean": final_mrr_mean,
            "final_mrr_best_case": final_mrr_p95,
            "final_mrr_worst_case": final_mrr_p5,
            "total_growth_pct": ((final_mrr_mean - base_mrr) / base_mrr) * 100,
        }

        return ScenarioAnalysis(
            scenario_name=scenario_name,
            assumptions=assumptions,
            predictions=simulation_results,
            impact_summary=impact_summary,
            confidence_level=0.90,
        )


# Singleton instance
_analytics_engine_instance = None
_instance_lock = threading.Lock()


def get_predictive_analytics() -> PredictiveAnalyticsEngine:
    """Get singleton Predictive Analytics Engine instance"""
    global _analytics_engine_instance

    if _analytics_engine_instance is None:
        with _instance_lock:
            if _analytics_engine_instance is None:
                _analytics_engine_instance = PredictiveAnalyticsEngine()

    return _analytics_engine_instance


if __name__ == "__main__":
    # Example usage
    engine = get_predictive_analytics()

    print("Predictive Analytics Engine initialized!")
    print(f"ARIMA available: {STATSMODELS_AVAILABLE}")
    print(f"Prophet available: {PROPHET_AVAILABLE}")
    print(f"scikit-learn available: {SKLEARN_AVAILABLE}")

    # Test scenario analysis
    scenario = engine.analyze_scenario(
        "Growth Scenario", {"base_mrr": 50000, "growth_rate": 0.08, "churn_rate": 0.02, "months": 12}
    )

    print(f"\nScenario: {scenario.scenario_name}")
    print(f"Final MRR (mean): €{scenario.impact_summary['final_mrr_mean']:,.2f}")
    print(f"Total growth: {scenario.impact_summary['total_growth_pct']:.1f}%")

    print("\nPredictive Analytics module loaded successfully!")
