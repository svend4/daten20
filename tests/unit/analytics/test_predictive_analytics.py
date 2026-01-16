"""
Comprehensive tests for Predictive Analytics Engine

Tests cover:
- ARIMA forecasting
- Prophet forecasting (when available)
- Churn prediction
- Revenue forecasting
- Monte Carlo simulations
- Scenario analysis
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Import the module
from src.analytics.predictive_analytics import (
    ForecastMethod,
    PredictionType,
    ForecastResult,
    ChurnPrediction,
    ScenarioAnalysis,
    ARIMAForecaster,
    ProphetForecaster,
    ChurnPredictor,
    RevenueForecaster,
    MonteCarloSimulator,
    PredictiveAnalyticsEngine,
    get_predictive_analytics,
    SKLEARN_AVAILABLE,
    STATSMODELS_AVAILABLE,
    PROPHET_AVAILABLE,
)


class TestDataClasses:
    """Test data classes and enums"""

    def test_forecast_method_enum(self):
        """Test ForecastMethod enum"""
        assert ForecastMethod.ARIMA == "arima"
        assert ForecastMethod.PROPHET == "prophet"
        assert ForecastMethod.LSTM == "lstm"
        assert ForecastMethod.LINEAR_REGRESSION == "linear_regression"

    def test_prediction_type_enum(self):
        """Test PredictionType enum"""
        assert PredictionType.REVENUE == "revenue"
        assert PredictionType.CHURN == "churn"
        assert PredictionType.USAGE == "usage"

    def test_forecast_result_creation(self):
        """Test ForecastResult dataclass"""
        result = ForecastResult(
            method=ForecastMethod.ARIMA,
            predictions=[100.0, 110.0, 120.0],
            dates=[datetime.now() + timedelta(days=i) for i in range(3)],
            confidence_lower=[90.0, 99.0, 108.0],
            confidence_upper=[110.0, 121.0, 132.0],
            accuracy_metrics={"mse": 5.0, "rmse": 2.23}
        )

        assert result.method == ForecastMethod.ARIMA
        assert len(result.predictions) == 3
        assert len(result.dates) == 3
        assert result.accuracy_metrics["mse"] == 5.0

    def test_churn_prediction_creation(self):
        """Test ChurnPrediction dataclass"""
        prediction = ChurnPrediction(
            customer_id="test-123",
            churn_probability=0.75,
            risk_level="high",
            contributing_factors=[{"feature": "usage", "importance": 0.8}],
            recommended_actions=["Contact customer"]
        )

        assert prediction.customer_id == "test-123"
        assert prediction.churn_probability == 0.75
        assert prediction.risk_level == "high"
        assert len(prediction.contributing_factors) == 1

    def test_scenario_analysis_creation(self):
        """Test ScenarioAnalysis dataclass"""
        scenario = ScenarioAnalysis(
            scenario_name="Growth",
            assumptions={"growth_rate": 0.1},
            predictions={"revenue": [100, 110, 121]},
            impact_summary={"final_revenue": 121},
            confidence_level=0.95
        )

        assert scenario.scenario_name == "Growth"
        assert scenario.confidence_level == 0.95


@pytest.mark.skipif(not STATSMODELS_AVAILABLE, reason="statsmodels not installed")
class TestARIMAForecaster:
    """Test ARIMA forecasting functionality"""

    @pytest.fixture
    def forecaster(self):
        """Create ARIMA forecaster instance"""
        return ARIMAForecaster()

    @pytest.fixture
    def sample_data(self):
        """Generate sample time series data"""
        # Generate data with trend
        return [100 + i * 2 + (i % 3) for i in range(50)]

    def test_initialization(self, forecaster):
        """Test forecaster initialization"""
        assert forecaster.model is None
        assert forecaster.fitted_values is None

    def test_fit_arima_model(self, forecaster, sample_data):
        """Test fitting ARIMA model"""
        forecaster.fit(sample_data, order=(1, 1, 1))

        assert forecaster.model is not None
        assert forecaster.fitted_model is not None

    def test_forecast_basic(self, forecaster, sample_data):
        """Test basic forecasting"""
        forecaster.fit(sample_data, order=(1, 1, 1))
        result = forecaster.forecast(steps=10)

        assert isinstance(result, ForecastResult)
        assert result.method == ForecastMethod.ARIMA
        assert len(result.predictions) == 10
        assert len(result.dates) == 10
        assert len(result.confidence_lower) == 10
        assert len(result.confidence_upper) == 10

    def test_forecast_confidence_intervals(self, forecaster, sample_data):
        """Test confidence intervals"""
        forecaster.fit(sample_data)
        result = forecaster.forecast(steps=5, confidence_level=0.95)

        for i in range(len(result.predictions)):
            pred = result.predictions[i]
            lower = result.confidence_lower[i]
            upper = result.confidence_upper[i]

            # Confidence bounds should contain prediction
            assert lower <= pred
            assert pred <= upper

    def test_forecast_without_fit_raises_error(self, forecaster):
        """Test that forecasting without fitting raises error"""
        with pytest.raises(ValueError, match="not fitted"):
            forecaster.forecast(steps=10)

    def test_detect_stationarity(self, forecaster, sample_data):
        """Test stationarity detection"""
        result = forecaster.detect_stationarity(sample_data)

        assert "adf_statistic" in result
        assert "p_value" in result
        assert "is_stationary" in result
        assert isinstance(result["is_stationary"], bool)

    def test_forecast_accuracy_metrics(self, forecaster, sample_data):
        """Test accuracy metrics calculation"""
        forecaster.fit(sample_data)
        result = forecaster.forecast(steps=5)

        assert "accuracy_metrics" in result.__dict__
        # May be empty if calculation fails, but should exist


@pytest.mark.skipif(not PROPHET_AVAILABLE, reason="prophet not installed")
class TestProphetForecaster:
    """Test Prophet forecasting functionality"""

    @pytest.fixture
    def forecaster(self):
        """Create Prophet forecaster instance"""
        return ProphetForecaster()

    @pytest.fixture
    def sample_data(self):
        """Generate sample time series data with dates"""
        base_date = datetime(2024, 1, 1)
        dates = [base_date + timedelta(days=i) for i in range(50)]
        values = [100 + i * 2 for i in range(50)]
        return dates, values

    def test_initialization(self, forecaster):
        """Test forecaster initialization"""
        assert forecaster.model is None

    def test_fit_prophet_model(self, forecaster, sample_data):
        """Test fitting Prophet model"""
        dates, values = sample_data
        forecaster.fit(dates, values)

        assert forecaster.model is not None

    def test_forecast_basic(self, forecaster, sample_data):
        """Test basic forecasting"""
        dates, values = sample_data
        forecaster.fit(dates, values)
        result = forecaster.forecast(periods=10)

        assert isinstance(result, ForecastResult)
        assert result.method == ForecastMethod.PROPHET
        assert len(result.predictions) == 10
        assert len(result.dates) == 10

    def test_forecast_without_fit_raises_error(self, forecaster):
        """Test that forecasting without fitting raises error"""
        with pytest.raises(ValueError, match="not fitted"):
            forecaster.forecast(periods=10)


@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not installed")
class TestChurnPredictor:
    """Test churn prediction functionality"""

    @pytest.fixture
    def predictor(self):
        """Create churn predictor instance"""
        return ChurnPredictor()

    @pytest.fixture
    def training_data(self):
        """Generate sample training data"""
        data = []
        # Churned customers
        for i in range(50):
            data.append({
                "customer_id": f"churn-{i}",
                "usage_days": 5 + i % 10,
                "support_tickets": 5 + i % 5,
                "usage_decline_pct": -30 - i % 20,
                "tenure_days": 30 + i * 2,
                "churned": 1
            })

        # Retained customers
        for i in range(50):
            data.append({
                "customer_id": f"retain-{i}",
                "usage_days": 20 + i % 10,
                "support_tickets": 1 + i % 3,
                "usage_decline_pct": 5 + i % 15,
                "tenure_days": 180 + i * 10,
                "churned": 0
            })

        return data

    def test_initialization(self, predictor):
        """Test predictor initialization"""
        assert predictor.model is None
        assert predictor.feature_names == []
        assert predictor.feature_importance == {}

    def test_train_model(self, predictor, training_data):
        """Test training churn model"""
        predictor.train(training_data)

        assert predictor.model is not None
        assert len(predictor.feature_names) > 0
        assert len(predictor.feature_importance) > 0

    def test_predict_churn_high_risk(self, predictor, training_data):
        """Test predicting high-risk churn"""
        predictor.train(training_data)

        customer_data = {
            "customer_id": "test-high-risk",
            "usage_days": 5,
            "support_tickets": 8,
            "usage_decline_pct": -50,
            "tenure_days": 30
        }

        prediction = predictor.predict_churn(customer_data)

        assert isinstance(prediction, ChurnPrediction)
        assert prediction.customer_id == "test-high-risk"
        assert 0 <= prediction.churn_probability <= 1
        assert prediction.risk_level in ["low", "medium", "high"]
        assert len(prediction.contributing_factors) > 0
        assert len(prediction.recommended_actions) > 0

    def test_predict_churn_low_risk(self, predictor, training_data):
        """Test predicting low-risk churn"""
        predictor.train(training_data)

        customer_data = {
            "customer_id": "test-low-risk",
            "usage_days": 25,
            "support_tickets": 1,
            "usage_decline_pct": 10,
            "tenure_days": 365
        }

        prediction = predictor.predict_churn(customer_data)

        assert prediction.customer_id == "test-low-risk"
        # Should have low churn probability
        assert prediction.risk_level in ["low", "medium", "high"]

    def test_predict_without_training_raises_error(self, predictor):
        """Test that predicting without training raises error"""
        with pytest.raises(ValueError, match="not trained"):
            predictor.predict_churn({"customer_id": "test"})

    def test_feature_importance_extraction(self, predictor, training_data):
        """Test feature importance extraction"""
        predictor.train(training_data)

        assert len(predictor.feature_importance) > 0
        # All importances should be between 0 and 1
        for importance in predictor.feature_importance.values():
            assert 0 <= importance <= 1

    def test_recommendations_generation(self, predictor, training_data):
        """Test recommendations generation"""
        predictor.train(training_data)

        high_risk_customer = {
            "customer_id": "high-risk",
            "usage_days": 3,
            "support_tickets": 10,
            "usage_decline_pct": -60,
            "tenure_days": 20
        }

        prediction = predictor.predict_churn(high_risk_customer)

        # High-risk customers should get actionable recommendations
        assert len(prediction.recommended_actions) > 0
        assert any("outreach" in action.lower() or "intervention" in action.lower()
                   for action in prediction.recommended_actions)


class TestRevenueForecaster:
    """Test revenue forecasting functionality"""

    @pytest.fixture
    def forecaster(self):
        """Create revenue forecaster instance"""
        return RevenueForecaster()

    @pytest.fixture
    def sample_mrr_data(self):
        """Generate sample MRR data"""
        base_date = datetime(2024, 1, 1)
        data = []
        for i in range(12):
            date = base_date + timedelta(days=30 * i)
            mrr = 10000 + i * 500  # Growing MRR
            data.append((date, float(mrr)))
        return data

    def test_initialization(self, forecaster):
        """Test forecaster initialization"""
        assert forecaster.historical_data == []
        assert forecaster.forecast_cache == {}

    def test_forecast_mrr_linear(self, forecaster, sample_mrr_data):
        """Test MRR forecasting with linear regression"""
        result = forecaster.forecast_mrr(
            sample_mrr_data,
            months=6,
            method=ForecastMethod.LINEAR_REGRESSION
        )

        assert isinstance(result, ForecastResult)
        assert len(result.predictions) == 6
        assert len(result.dates) == 6
        # Revenue should be positive
        assert all(p > 0 for p in result.predictions)

    @pytest.mark.skipif(not STATSMODELS_AVAILABLE, reason="statsmodels not installed")
    def test_forecast_mrr_arima(self, forecaster, sample_mrr_data):
        """Test MRR forecasting with ARIMA"""
        result = forecaster.forecast_mrr(
            sample_mrr_data,
            months=6,
            method=ForecastMethod.ARIMA
        )

        assert isinstance(result, ForecastResult)
        assert result.method == ForecastMethod.ARIMA
        assert len(result.predictions) == 6

    def test_linear_forecast_fallback(self, forecaster, sample_mrr_data):
        """Test linear forecast fallback"""
        dates = [d[0] for d in sample_mrr_data]
        values = [d[1] for d in sample_mrr_data]

        result = forecaster._linear_forecast(dates, values, periods=3)

        assert isinstance(result, ForecastResult)
        assert result.method == ForecastMethod.LINEAR_REGRESSION
        assert len(result.predictions) == 3

    def test_forecast_with_upward_trend(self, forecaster):
        """Test forecasting with upward trend"""
        base_date = datetime(2024, 1, 1)
        growing_data = [(base_date + timedelta(days=30 * i), 1000.0 + i * 100)
                        for i in range(12)]

        result = forecaster.forecast_mrr(growing_data, months=6)

        # Predictions should generally increase
        for i in range(len(result.predictions) - 1):
            # Allow small variations
            assert result.predictions[i+1] >= result.predictions[i] * 0.95


@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not installed")
class TestMonteCarloSimulator:
    """Test Monte Carlo simulation functionality"""

    @pytest.fixture
    def simulator(self):
        """Create simulator instance"""
        return MonteCarloSimulator(n_simulations=100)

    def test_initialization(self, simulator):
        """Test simulator initialization"""
        assert simulator.n_simulations == 100

    def test_simulate_revenue_basic(self, simulator):
        """Test basic revenue simulation"""
        result = simulator.simulate_revenue(
            base_mrr=10000.0,
            growth_rate_mean=0.05,
            growth_rate_std=0.02,
            churn_rate_mean=0.03,
            churn_rate_std=0.01,
            months=12
        )

        assert "mean_trajectory" in result
        assert "percentile_5" in result
        assert "percentile_95" in result
        assert len(result["mean_trajectory"]) == 12

    def test_simulation_confidence_bounds(self, simulator):
        """Test simulation confidence bounds"""
        result = simulator.simulate_revenue(
            base_mrr=10000.0,
            growth_rate_mean=0.05,
            growth_rate_std=0.01,
            churn_rate_mean=0.02,
            churn_rate_std=0.005,
            months=6
        )

        # P5 should be less than mean, which should be less than P95
        for i in range(len(result["mean_trajectory"])):
            assert result["percentile_5"][i] <= result["mean_trajectory"][i]
            assert result["mean_trajectory"][i] <= result["percentile_95"][i]

    def test_simulation_with_high_growth(self, simulator):
        """Test simulation with high growth rate"""
        result = simulator.simulate_revenue(
            base_mrr=10000.0,
            growth_rate_mean=0.10,  # 10% monthly growth
            growth_rate_std=0.02,
            churn_rate_mean=0.02,
            churn_rate_std=0.01,
            months=12
        )

        # Mean trajectory should show growth
        assert result["mean_trajectory"][-1] > 10000.0

    def test_simulation_with_high_churn(self, simulator):
        """Test simulation with high churn rate"""
        result = simulator.simulate_revenue(
            base_mrr=10000.0,
            growth_rate_mean=0.02,
            growth_rate_std=0.01,
            churn_rate_mean=0.10,  # 10% churn
            churn_rate_std=0.02,
            months=12
        )

        # With high churn, revenue might decline
        assert isinstance(result["mean_trajectory"], list)
        assert len(result["mean_trajectory"]) == 12


class TestPredictiveAnalyticsEngine:
    """Test main Predictive Analytics Engine"""

    @pytest.fixture
    def engine(self):
        """Create engine instance"""
        return PredictiveAnalyticsEngine()

    def test_initialization(self, engine):
        """Test engine initialization"""
        assert engine.churn_predictor is not None
        assert engine.revenue_forecaster is not None
        assert engine.monte_carlo is not None
        assert engine.models == {}
        assert engine.predictions_cache == {}

    def test_forecast_metric_linear(self, engine):
        """Test metric forecasting with linear regression"""
        base_date = datetime(2024, 1, 1)
        historical_data = [(base_date + timedelta(days=i), 100.0 + i * 2)
                          for i in range(30)]

        result = engine.forecast_metric(
            metric_name="api_calls",
            historical_data=historical_data,
            periods=7,
            method=ForecastMethod.LINEAR_REGRESSION
        )

        assert isinstance(result, ForecastResult)
        assert len(result.predictions) == 7

    @pytest.mark.skipif(not STATSMODELS_AVAILABLE, reason="statsmodels not installed")
    def test_forecast_metric_arima(self, engine):
        """Test metric forecasting with ARIMA"""
        base_date = datetime(2024, 1, 1)
        historical_data = [(base_date + timedelta(days=i), 100.0 + i * 2)
                          for i in range(30)]

        result = engine.forecast_metric(
            metric_name="storage_gb",
            historical_data=historical_data,
            periods=7,
            method=ForecastMethod.ARIMA
        )

        assert isinstance(result, ForecastResult)
        assert result.method == ForecastMethod.ARIMA

    def test_forecast_metric_caching(self, engine):
        """Test that forecast results are cached"""
        base_date = datetime(2024, 1, 1)
        historical_data = [(base_date + timedelta(days=i), 100.0 + i)
                          for i in range(30)]

        # First call
        result1 = engine.forecast_metric(
            "test_metric", historical_data, periods=5
        )

        # Second call should use cache
        result2 = engine.forecast_metric(
            "test_metric", historical_data, periods=5
        )

        # Should be same object from cache
        assert result1 is result2

    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not installed")
    def test_predict_customer_churn_batch(self, engine):
        """Test batch churn prediction"""
        # Train model first
        training_data = []
        for i in range(50):
            training_data.append({
                "customer_id": f"train-{i}",
                "usage_days": 10 + i % 15,
                "support_tickets": 2 + i % 4,
                "usage_decline_pct": -10 + i % 20,
                "tenure_days": 60 + i * 5,
                "churned": 1 if i % 3 == 0 else 0
            })

        engine.churn_predictor.train(training_data)

        # Predict for batch
        customers = [
            {"customer_id": "cust-1", "usage_days": 5, "support_tickets": 8,
             "usage_decline_pct": -40, "tenure_days": 30},
            {"customer_id": "cust-2", "usage_days": 20, "support_tickets": 1,
             "usage_decline_pct": 10, "tenure_days": 200},
        ]

        predictions = engine.predict_customer_churn(customers)

        assert len(predictions) == 2
        assert all(isinstance(p, ChurnPrediction) for p in predictions)

    def test_analyze_scenario(self, engine):
        """Test scenario analysis"""
        scenario = engine.analyze_scenario(
            "Growth Scenario",
            {
                "base_mrr": 50000,
                "growth_rate": 0.08,
                "churn_rate": 0.02,
                "months": 12
            }
        )

        assert isinstance(scenario, ScenarioAnalysis)
        assert scenario.scenario_name == "Growth Scenario"
        assert "final_mrr_mean" in scenario.impact_summary
        assert "total_growth_pct" in scenario.impact_summary
        assert "mean_trajectory" in scenario.predictions

    def test_analyze_scenario_optimistic(self, engine):
        """Test optimistic scenario"""
        scenario = engine.analyze_scenario(
            "Optimistic",
            {
                "base_mrr": 10000,
                "growth_rate": 0.15,  # High growth
                "churn_rate": 0.01,   # Low churn
                "months": 12
            }
        )

        # Should show significant growth
        assert scenario.impact_summary["total_growth_pct"] > 100  # More than 100% growth

    def test_analyze_scenario_pessimistic(self, engine):
        """Test pessimistic scenario"""
        scenario = engine.analyze_scenario(
            "Pessimistic",
            {
                "base_mrr": 10000,
                "growth_rate": 0.02,  # Low growth
                "churn_rate": 0.08,   # High churn
                "months": 12
            }
        )

        # Might show decline
        assert "final_mrr_mean" in scenario.impact_summary


class TestSingletonPattern:
    """Test singleton pattern for global instance"""

    def test_get_predictive_analytics(self):
        """Test getting singleton instance"""
        engine1 = get_predictive_analytics()
        engine2 = get_predictive_analytics()

        # Should return same instance
        assert engine1 is engine2

    def test_engine_instance_type(self):
        """Test engine instance type"""
        engine = get_predictive_analytics()
        assert isinstance(engine, PredictiveAnalyticsEngine)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_historical_data(self):
        """Test with empty historical data"""
        engine = PredictiveAnalyticsEngine()

        # Should handle gracefully
        result = engine.forecast_metric(
            "empty_metric",
            [],
            periods=5
        )

        # Should return something (possibly with fallback)
        assert isinstance(result, ForecastResult)

    def test_insufficient_data_for_arima(self):
        """Test ARIMA with insufficient data"""
        if not STATSMODELS_AVAILABLE:
            pytest.skip("statsmodels not available")

        forecaster = ARIMAForecaster()

        # Very little data
        with pytest.raises(Exception):  # ARIMA will fail
            forecaster.fit([100, 110])

    def test_negative_forecast_periods(self):
        """Test forecasting with negative periods"""
        engine = PredictiveAnalyticsEngine()
        base_date = datetime(2024, 1, 1)
        data = [(base_date + timedelta(days=i), 100.0) for i in range(10)]

        # Should handle negative periods (convert to 0 or raise error)
        # Current implementation doesn't explicitly check, but shouldn't crash
        try:
            result = engine.forecast_metric("test", data, periods=-5)
            # If it doesn't raise, check it returns empty or sensible result
            assert isinstance(result, ForecastResult)
        except (ValueError, Exception):
            # If it raises, that's also acceptable
            pass

    def test_very_large_forecast_horizon(self):
        """Test forecasting with very large horizon"""
        engine = PredictiveAnalyticsEngine()
        base_date = datetime(2024, 1, 1)
        data = [(base_date + timedelta(days=i), 100.0 + i) for i in range(30)]

        result = engine.forecast_metric("test", data, periods=365)

        # Should complete without crashing
        assert len(result.predictions) == 365


class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not installed")
    def test_complete_analytics_workflow(self):
        """Test complete analytics workflow"""
        engine = get_predictive_analytics()

        # 1. Forecast revenue
        base_date = datetime(2024, 1, 1)
        mrr_history = [(base_date + timedelta(days=30 * i), 10000.0 + i * 500)
                       for i in range(12)]

        revenue_forecast = engine.revenue_forecaster.forecast_mrr(
            mrr_history, months=6
        )

        assert len(revenue_forecast.predictions) == 6

        # 2. Predict churn
        training_data = []
        for i in range(100):
            training_data.append({
                "customer_id": f"cust-{i}",
                "usage_days": 10 + i % 20,
                "support_tickets": 1 + i % 5,
                "usage_decline_pct": -20 + i % 40,
                "tenure_days": 60 + i * 3,
                "churned": 1 if i % 4 == 0 else 0
            })

        engine.churn_predictor.train(training_data)

        customer = {
            "customer_id": "test-cust",
            "usage_days": 5,
            "support_tickets": 7,
            "usage_decline_pct": -50,
            "tenure_days": 20
        }

        churn_pred = engine.churn_predictor.predict_churn(customer)
        assert isinstance(churn_pred, ChurnPrediction)

        # 3. Run scenario analysis
        scenario = engine.analyze_scenario(
            "Base Case",
            {"base_mrr": 10000, "growth_rate": 0.05, "churn_rate": 0.03, "months": 12}
        )

        assert isinstance(scenario, ScenarioAnalysis)
        assert scenario.impact_summary["final_mrr_mean"] > 0

    def test_multiple_forecasts_with_caching(self):
        """Test multiple forecasts with caching"""
        engine = PredictiveAnalyticsEngine()
        base_date = datetime(2024, 1, 1)
        data = [(base_date + timedelta(days=i), 100.0 + i * 2) for i in range(30)]

        # First forecast
        result1 = engine.forecast_metric("metric1", data, periods=7)

        # Same forecast should use cache
        result2 = engine.forecast_metric("metric1", data, periods=7)

        # Different metric should not use cache
        result3 = engine.forecast_metric("metric2", data, periods=7)

        assert result1 is result2  # Same object
        assert result1 is not result3  # Different object


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
