# Analytics & BI Module v3.1 - User Guide

**Version:** 3.1.0  
**Status:** Production Ready  
**Created:** 2026-01-10

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Business Intelligence Dashboard](#business-intelligence-dashboard)
3. [Predictive Analytics](#predictive-analytics)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)

---

## Overview

The Analytics & BI module provides enterprise-grade business intelligence and predictive analytics capabilities.

### Key Features

**Business Intelligence Dashboard:**
- Executive KPI tracking (MRR, ARR, Churn, CLV, NRR, CAC)
- Custom dashboard builder
- Report generation (PDF, Excel, PowerPoint, CSV, JSON)
- Scheduled reports (daily, weekly, monthly, quarterly)
- Real-time data visualization
- Drill-down analytics

**Predictive Analytics:**
- ARIMA forecasting
- Prophet integration (Facebook's forecasting library)
- LSTM models (optional, with TensorFlow/PyTorch)
- Customer churn prediction
- Revenue forecasting
- Monte Carlo simulations
- What-if scenario analysis
- Confidence intervals

---

## Business Intelligence Dashboard

### Quick Start

```python
from src.analytics import get_bi_dashboard
from datetime import datetime, timedelta

# Get dashboard instance
dashboard = get_bi_dashboard()

# Create executive dashboard
exec_dashboard = dashboard.create_executive_dashboard(
    tenant_id="acme-corp",
    date_range=(datetime.now() - timedelta(days=30), datetime.now())
)

print(f"KPIs: {len(exec_dashboard['kpis'])}")
print(f"Widgets: {len(exec_dashboard['widgets'])}")
```

### Calculate KPIs

```python
from src.analytics import KPICalculator
from decimal import Decimal

calc = KPICalculator()

# Sample subscription data
subscriptions = [
    {"status": "active", "billing_cycle": "monthly", "amount": 99},
    {"status": "active", "billing_cycle": "monthly", "amount": 299},
    {"status": "active", "billing_cycle": "yearly", "amount": 990},
]

# Calculate metrics
mrr = calc.calculate_mrr(subscriptions)
arr = calc.calculate_arr(mrr)
churn_rate = calc.calculate_churn_rate(
    churned_customers=5,
    total_customers_start=100
)

print(f"MRR: €{mrr}")
print(f"ARR: €{arr}")
print(f"Churn Rate: {churn_rate}%")
```

### Build Custom Dashboard

```python
from src.analytics import DashboardBuilder, KPI, ChartData, ChartType

builder = DashboardBuilder()

# Add KPI widget
mrr_kpi = KPI(
    name="Monthly Recurring Revenue",
    value=99000.0,
    unit="EUR",
    change_percentage=8.5,
    trend="up",
    target=100000.0
)

builder.add_kpi_widget(
    mrr_kpi,
    position={"row": 0, "col": 0},
    size={"width": 3, "height": 2}
)

# Add chart widget
revenue_chart = ChartData(
    chart_type=ChartType.LINE,
    title="Revenue Trend",
    data={},
    labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets=[{
        "label": "MRR",
        "data": [85000, 88000, 92000, 95000, 97000, 99000]
    }]
)

builder.add_chart_widget(
    revenue_chart,
    position={"row": 2, "col": 0},
    size={"width": 6, "height": 4}
)

# Build dashboard
dashboard_config = builder.build()
```

### Generate Reports

```python
from src.analytics import ReportFormat

dashboard = get_bi_dashboard()

# Create custom report
report = dashboard.create_custom_report(
    name="Monthly Business Review",
    description="Monthly KPIs and performance metrics",
    kpis=[mrr_kpi],  # List of KPI objects
    charts=[revenue_chart],  # List of ChartData objects
    filters={"tenant_id": "acme-corp"},
    created_by="admin@acme.com"
)

# Export to PDF
pdf_bytes = dashboard.export_report(report.id, ReportFormat.PDF)

# Export to Excel
excel_bytes = dashboard.export_report(report.id, ReportFormat.EXCEL)

# Export to JSON
json_str = dashboard.export_report(report.id, ReportFormat.JSON)
```

### Schedule Reports

```python
from src.analytics import ReportFrequency, ReportFormat

# Schedule weekly report
scheduled = dashboard.schedule_report(
    report_id=report.id,
    name="Weekly Executive Summary",
    frequency=ReportFrequency.WEEKLY,
    recipients=["ceo@acme.com", "cfo@acme.com"],
    format=ReportFormat.PDF,
    filters={}
)

print(f"Report scheduled: {scheduled.next_run}")
```

---

## Predictive Analytics

### Quick Start

```python
from src.analytics import get_predictive_analytics
from datetime import datetime, timedelta

# Get analytics engine
engine = get_predictive_analytics()

# Forecast a metric
historical_data = [
    (datetime.now() - timedelta(days=30-i), 1000 + i*10)
    for i in range(30)
]

forecast = engine.forecast_metric(
    metric_name="api_calls",
    historical_data=historical_data,
    periods=7,  # 7 days ahead
    method=ForecastMethod.ARIMA
)

print(f"Forecast for next 7 days: {forecast.predictions}")
print(f"Confidence interval: {forecast.confidence_lower} - {forecast.confidence_upper}")
```

### Revenue Forecasting

```python
from src.analytics import ForecastMethod

# Historical MRR data
historical_mrr = [
    (datetime(2025, 1, 1), 50000),
    (datetime(2025, 2, 1), 52000),
    (datetime(2025, 3, 1), 55000),
    (datetime(2025, 4, 1), 57500),
    (datetime(2025, 5, 1), 60000),
    (datetime(2025, 6, 1), 63000),
]

# Forecast next 12 months
forecast = engine.revenue_forecaster.forecast_mrr(
    historical_mrr=historical_mrr,
    months=12,
    method=ForecastMethod.ARIMA
)

print("12-Month MRR Forecast:")
for date, value, lower, upper in zip(
    forecast.dates,
    forecast.predictions,
    forecast.confidence_lower,
    forecast.confidence_upper
):
    print(f"{date.strftime('%Y-%m')}: €{value:,.2f} (€{lower:,.2f} - €{upper:,.2f})")
```

### Churn Prediction

```python
# Training data (historical customer data with churn labels)
training_data = [
    {
        "customer_id": "cust1",
        "usage_decline_pct": -15.5,
        "support_tickets": 3,
        "login_frequency": 12,
        "feature_usage_score": 65,
        "tenure_months": 24,
        "churned": 0  # 0 = retained, 1 = churned
    },
    {
        "customer_id": "cust2",
        "usage_decline_pct": -45.2,
        "support_tickets": 8,
        "login_frequency": 2,
        "feature_usage_score": 25,
        "tenure_months": 6,
        "churned": 1
    },
    # ... more training examples
]

# Train churn model
engine.churn_predictor.train(training_data)

# Predict churn for new customer
customer_data = {
    "customer_id": "cust_new",
    "usage_decline_pct": -30.0,
    "support_tickets": 5,
    "login_frequency": 4,
    "feature_usage_score": 40,
    "tenure_months": 12
}

prediction = engine.churn_predictor.predict_churn(customer_data)

print(f"Customer: {prediction.customer_id}")
print(f"Churn Probability: {prediction.churn_probability:.1%}")
print(f"Risk Level: {prediction.risk_level}")
print(f"Recommended Actions:")
for action in prediction.recommended_actions:
    print(f"  - {action}")
```

### Scenario Analysis

```python
# What-if analysis: "What if we achieve 10% monthly growth?"
scenario = engine.analyze_scenario(
    scenario_name="Aggressive Growth",
    assumptions={
        "base_mrr": 100000,
        "growth_rate": 0.10,  # 10% monthly growth
        "churn_rate": 0.02,   # 2% monthly churn
        "months": 12
    }
)

print(f"Scenario: {scenario.scenario_name}")
print(f"\nResults after 12 months:")
print(f"  Mean MRR: €{scenario.impact_summary['final_mrr_mean']:,.2f}")
print(f"  Best Case (95th percentile): €{scenario.impact_summary['final_mrr_best_case']:,.2f}")
print(f"  Worst Case (5th percentile): €{scenario.impact_summary['final_mrr_worst_case']:,.2f}")
print(f"  Total Growth: {scenario.impact_summary['total_growth_pct']:.1f}%")
```

### Monte Carlo Simulation

```python
# Run Monte Carlo simulation
simulation = engine.monte_carlo.simulate_revenue(
    base_mrr=50000,
    growth_rate_mean=0.08,
    growth_rate_std=0.03,
    churn_rate_mean=0.025,
    churn_rate_std=0.01,
    months=12
)

print("Monte Carlo Simulation (1000 runs):")
print(f"Mean trajectory (final month): €{simulation['mean_trajectory'][-1]:,.2f}")
print(f"90% Confidence Interval: €{simulation['percentile_5'][-1]:,.2f} - €{simulation['percentile_95'][-1]:,.2f}")
```

---

## API Reference

### BIDashboard

**Methods:**
- `create_executive_dashboard(tenant_id, date_range)` - Create executive KPI dashboard
- `create_custom_report(name, description, kpis, charts, filters, created_by)` - Create custom report
- `export_report(report_id, format)` - Export report in specified format
- `schedule_report(report_id, name, frequency, recipients, format, filters)` - Schedule automatic reports

### KPICalculator

**Methods:**
- `calculate_mrr(subscriptions)` - Calculate Monthly Recurring Revenue
- `calculate_arr(mrr)` - Calculate Annual Recurring Revenue
- `calculate_churn_rate(churned_customers, total_customers_start, period_days)` - Calculate churn rate
- `calculate_clv(avg_revenue_per_user, avg_customer_lifespan_months, gross_margin)` - Calculate Customer Lifetime Value
- `calculate_nrr(revenue_start, expansion_revenue, churned_revenue)` - Calculate Net Revenue Retention
- `calculate_cac(sales_marketing_costs, new_customers)` - Calculate Customer Acquisition Cost
- `calculate_arpu(total_revenue, total_users)` - Calculate Average Revenue Per User
- `calculate_ltv_cac_ratio(clv, cac)` - Calculate LTV:CAC ratio

### PredictiveAnalyticsEngine

**Methods:**
- `forecast_metric(metric_name, historical_data, periods, method)` - Forecast any metric
- `predict_customer_churn(customers)` - Batch churn prediction
- `analyze_scenario(scenario_name, assumptions)` - What-if scenario analysis

### ChurnPredictor

**Methods:**
- `train(training_data, target_column)` - Train churn prediction model
- `predict_churn(customer_data)` - Predict churn for single customer

### RevenueForecaster

**Methods:**
- `forecast_mrr(historical_mrr, months, method)` - Forecast Monthly Recurring Revenue

---

## Configuration

### Dependencies

**Required:**
```bash
pip install numpy pandas scikit-learn
```

**Optional (for advanced features):**
```bash
# ARIMA forecasting
pip install statsmodels

# Prophet forecasting
pip install prophet

# LSTM models
pip install tensorflow
# OR
pip install torch
```

### Environment Variables

```bash
# Analytics cache TTL (seconds)
ANALYTICS_CACHE_TTL=300

# Monte Carlo simulations
MONTE_CARLO_SIMULATIONS=1000

# Report storage path
ANALYTICS_REPORTS_PATH=/var/lib/dms/reports
```

---

## Performance Considerations

### Caching
- KPI calculations are cached for 5 minutes by default
- Forecast results are cached for 1 hour
- Clear cache with `analytics_engine.predictions_cache.clear()`

### Optimization Tips
1. Use ARIMA for short-term forecasts (<90 days)
2. Use Prophet for long-term forecasts with seasonality
3. Batch churn predictions to reduce overhead
4. Schedule heavy reports during off-peak hours
5. Use materialized views for frequently accessed metrics

---

## Troubleshooting

### Common Issues

**Issue: ARIMA not available**
```
Solution: Install statsmodels
pip install statsmodels
```

**Issue: Prophet not available**
```
Solution: Install prophet (requires pystan)
pip install prophet
```

**Issue: Out of memory during forecast**
```
Solution: Reduce forecast horizon or use lighter method (linear regression)
```

---

## Changelog

### v3.1.0 (2026-01-10)
- Initial release
- Business Intelligence Dashboard
- Predictive Analytics Engine
- KPI calculation framework
- Report generation and scheduling
- Churn prediction
- Revenue forecasting
- Monte Carlo simulations

---

**Next Features (v3.2):**
- Data Warehouse integration
- OLAP Cube engine
- Real-time streaming analytics
- Natural Language Query interface

For questions and support, contact: support@dms-enterprise.com
