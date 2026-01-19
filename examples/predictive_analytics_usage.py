#!/usr/bin/env python3
"""
Predictive Analytics Usage Examples

Demonstrates how to use the Predictive Analytics Engine for:
- Revenue forecasting
- Churn prediction
- Scenario analysis
- Monte Carlo simulations

Requirements:
- Basic: Works without any ML libraries (fallback methods)
- Full features: Install statsmodels, prophet, scikit-learn
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analytics.predictive_analytics import (
    ForecastMethod,
    get_predictive_analytics,
    SKLEARN_AVAILABLE,
    STATSMODELS_AVAILABLE,
    PROPHET_AVAILABLE,
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_subsection(title: str):
    """Print subsection header"""
    print(f"\n--- {title} ---\n")


def example_1_revenue_forecasting():
    """Example 1: Revenue Forecasting with MRR"""
    print_section("Example 1: Revenue Forecasting")

    engine = get_predictive_analytics()

    # Historical MRR data (12 months)
    base_date = datetime(2024, 1, 1)
    mrr_history = []
    for i in range(12):
        date = base_date + timedelta(days=30 * i)
        mrr = 10000 + i * 800  # Growing MRR
        mrr_history.append((date, float(mrr)))

    print("Historical MRR (last 6 months):")
    for date, mrr in mrr_history[-6:]:
        print(f"  {date.strftime('%Y-%m')}: ${mrr:,.2f}")

    # Forecast next 6 months
    print_subsection("Forecasting next 6 months")

    method = ForecastMethod.ARIMA if STATSMODELS_AVAILABLE else ForecastMethod.LINEAR_REGRESSION
    print(f"Using method: {method}")

    result = engine.revenue_forecaster.forecast_mrr(
        mrr_history,
        months=6,
        method=method
    )

    print("\nForecast Results:")
    for i, (date, pred, lower, upper) in enumerate(
        zip(result.dates, result.predictions, result.confidence_lower, result.confidence_upper)
    ):
        print(f"  {date.strftime('%Y-%m')}: ${pred:,.2f} (${lower:,.2f} - ${upper:,.2f})")

    if result.accuracy_metrics:
        print(f"\nAccuracy Metrics:")
        for metric, value in result.accuracy_metrics.items():
            print(f"  {metric.upper()}: {value:.2f}")


def example_2_churn_prediction():
    """Example 2: Customer Churn Prediction"""
    print_section("Example 2: Customer Churn Prediction")

    if not SKLEARN_AVAILABLE:
        print("⚠️  scikit-learn not available. Skipping churn prediction example.")
        print("   Install with: pip install scikit-learn")
        return

    engine = get_predictive_analytics()

    # Training data (100 customers)
    print("Training churn prediction model...")
    training_data = []

    # Churned customers (25)
    for i in range(25):
        training_data.append({
            "customer_id": f"churn-{i}",
            "usage_days": 3 + i % 10,  # Low usage
            "support_tickets": 5 + i % 5,  # Many tickets
            "usage_decline_pct": -40 - i % 30,  # Declining usage
            "tenure_days": 30 + i * 3,  # Short tenure
            "churned": 1
        })

    # Retained customers (75)
    for i in range(75):
        training_data.append({
            "customer_id": f"retain-{i}",
            "usage_days": 20 + i % 10,  # High usage
            "support_tickets": 1 + i % 3,  # Few tickets
            "usage_decline_pct": 5 + i % 20,  # Growing usage
            "tenure_days": 180 + i * 5,  # Long tenure
            "churned": 0
        })

    engine.churn_predictor.train(training_data)
    print(f"Model trained on {len(training_data)} customers")

    # Feature importance
    print("\nTop 5 Features by Importance:")
    for feature, importance in sorted(
        engine.churn_predictor.feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]:
        print(f"  {feature}: {importance:.3f}")

    # Predict churn for test customers
    print_subsection("Predicting churn for test customers")

    test_customers = [
        {
            "customer_id": "test-high-risk",
            "usage_days": 2,
            "support_tickets": 10,
            "usage_decline_pct": -60,
            "tenure_days": 20
        },
        {
            "customer_id": "test-medium-risk",
            "usage_days": 12,
            "support_tickets": 4,
            "usage_decline_pct": -15,
            "tenure_days": 90
        },
        {
            "customer_id": "test-low-risk",
            "usage_days": 25,
            "support_tickets": 1,
            "usage_decline_pct": 20,
            "tenure_days": 365
        }
    ]

    for customer in test_customers:
        prediction = engine.churn_predictor.predict_churn(customer)

        print(f"\nCustomer: {prediction.customer_id}")
        print(f"  Churn Probability: {prediction.churn_probability:.1%}")
        print(f"  Risk Level: {prediction.risk_level.upper()}")

        print(f"  Top Contributing Factors:")
        for factor in prediction.contributing_factors[:3]:
            print(f"    - {factor['feature']}: {factor['value']} (importance: {factor['importance']:.2f})")

        print(f"  Recommended Actions:")
        for action in prediction.recommended_actions[:2]:
            print(f"    - {action}")


def example_3_scenario_analysis():
    """Example 3: What-if Scenario Analysis"""
    print_section("Example 3: What-if Scenario Analysis")

    engine = get_predictive_analytics()

    scenarios = [
        {
            "name": "Base Case",
            "base_mrr": 50000,
            "growth_rate": 0.05,  # 5% monthly growth
            "churn_rate": 0.03,   # 3% monthly churn
        },
        {
            "name": "Optimistic",
            "base_mrr": 50000,
            "growth_rate": 0.10,  # 10% growth
            "churn_rate": 0.02,   # 2% churn
        },
        {
            "name": "Pessimistic",
            "base_mrr": 50000,
            "growth_rate": 0.02,  # 2% growth
            "churn_rate": 0.08,   # 8% churn
        }
    ]

    print(f"Initial MRR: ${scenarios[0]['base_mrr']:,}\n")

    for scenario_config in scenarios:
        print_subsection(f"Scenario: {scenario_config['name']}")

        print(f"Assumptions:")
        print(f"  - Monthly Growth Rate: {scenario_config['growth_rate']:.1%}")
        print(f"  - Monthly Churn Rate: {scenario_config['churn_rate']:.1%}")

        scenario_config["months"] = 12
        scenario = engine.analyze_scenario(
            scenario_config["name"],
            scenario_config
        )

        print(f"\n12-Month Projections:")
        print(f"  Mean Final MRR: ${scenario.impact_summary['final_mrr_mean']:,.2f}")
        print(f"  Best Case (P95): ${scenario.impact_summary['final_mrr_best_case']:,.2f}")
        print(f"  Worst Case (P5): ${scenario.impact_summary['final_mrr_worst_case']:,.2f}")
        print(f"  Total Growth: {scenario.impact_summary['total_growth_pct']:.1f}%")

        # Show trajectory
        print(f"\n  Monthly Trajectory (mean):")
        for month in [0, 3, 6, 9, 11]:  # Show selected months
            mrr = scenario.predictions["mean_trajectory"][month]
            print(f"    Month {month+1}: ${mrr:,.2f}")


def example_4_usage_forecasting():
    """Example 4: Generic Metric Forecasting"""
    print_section("Example 4: Generic Metric Forecasting")

    engine = get_predictive_analytics()

    # Simulate API usage growth
    base_date = datetime(2024, 1, 1)
    api_calls_history = []

    for i in range(30):
        date = base_date + timedelta(days=i)
        calls = 50000 + i * 2000 + (i % 7) * 1000  # Growth with weekly pattern
        api_calls_history.append((date, float(calls)))

    print("Historical API Calls (last 7 days):")
    for date, calls in api_calls_history[-7:]:
        print(f"  {date.strftime('%Y-%m-%d')}: {calls:,.0f} calls")

    # Forecast next 7 days
    print_subsection("Forecasting next 7 days")

    result = engine.forecast_metric(
        metric_name="api_calls",
        historical_data=api_calls_history,
        periods=7,
        method=ForecastMethod.LINEAR_REGRESSION
    )

    print("\nForecast:")
    for date, pred in zip(result.dates, result.predictions):
        print(f"  {date.strftime('%Y-%m-%d')}: {pred:,.0f} calls")

    # Calculate capacity needs
    max_forecast = max(result.predictions)
    print(f"\nCapacity Planning:")
    print(f"  Peak forecast: {max_forecast:,.0f} calls/day")
    print(f"  Recommended capacity (20% buffer): {max_forecast * 1.2:,.0f} calls/day")


def example_5_monte_carlo_simulation():
    """Example 5: Monte Carlo Simulation"""
    print_section("Example 5: Monte Carlo Simulation")

    if not SKLEARN_AVAILABLE:
        print("⚠️  scikit-learn not available. Skipping Monte Carlo example.")
        print("   Install with: pip install scikit-learn numpy")
        return

    engine = get_predictive_analytics()

    print("Running Monte Carlo simulation with 1000 iterations...")
    print("This models revenue uncertainty over 12 months.\n")

    result = engine.monte_carlo.simulate_revenue(
        base_mrr=100000,
        growth_rate_mean=0.05,    # 5% average growth
        growth_rate_std=0.02,     # ±2% variability
        churn_rate_mean=0.03,     # 3% average churn
        churn_rate_std=0.01,      # ±1% variability
        months=12
    )

    print("Results (MRR projections):")
    print(f"\n  Starting MRR: $100,000\n")

    # Show key milestones
    for month in [3, 6, 9, 12]:
        idx = month - 1
        mean = result["mean_trajectory"][idx]
        p5 = result["percentile_5"][idx]
        p25 = result["percentile_25"][idx]
        p75 = result["percentile_75"][idx]
        p95 = result["percentile_95"][idx]

        print(f"  Month {month}:")
        print(f"    P5:  ${p5:>10,.0f}  (worst case)")
        print(f"    P25: ${p25:>10,.0f}")
        print(f"    Mean: ${mean:>10,.0f}")
        print(f"    P75: ${p75:>10,.0f}")
        print(f"    P95: ${p95:>10,.0f}  (best case)\n")

    # Final statistics
    final_mean = result["mean_trajectory"][-1]
    final_p5 = result["percentile_5"][-1]
    final_p95 = result["percentile_95"][-1]

    print(f"After 12 months:")
    print(f"  Expected (mean): ${final_mean:,.0f}")
    print(f"  Range (90% confidence): ${final_p5:,.0f} - ${final_p95:,.0f}")
    print(f"  Expected growth: {((final_mean - 100000) / 100000 * 100):.1f}%")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  PREDICTIVE ANALYTICS ENGINE - USAGE EXAMPLES")
    print("=" * 70)

    print("\nLibrary Availability:")
    print(f"  ✓ statsmodels (ARIMA): {'Yes' if STATSMODELS_AVAILABLE else 'No'}")
    print(f"  ✓ prophet (Facebook Prophet): {'Yes' if PROPHET_AVAILABLE else 'No'}")
    print(f"  ✓ scikit-learn (ML models): {'Yes' if SKLEARN_AVAILABLE else 'No'}")

    if not any([STATSMODELS_AVAILABLE, PROPHET_AVAILABLE, SKLEARN_AVAILABLE]):
        print("\n⚠️  No ML libraries available. Using fallback methods only.")
        print("   For full functionality, install:")
        print("   pip install statsmodels prophet scikit-learn numpy pandas")

    try:
        # Run examples
        example_1_revenue_forecasting()
        example_2_churn_prediction()
        example_3_scenario_analysis()
        example_4_usage_forecasting()
        example_5_monte_carlo_simulation()

        print("\n" + "=" * 70)
        print("  ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
