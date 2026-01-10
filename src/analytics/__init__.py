"""
Analytics Module - v3.1

Advanced Analytics & Business Intelligence components.

Modules:
- bi_dashboard: Business Intelligence dashboards and KPI tracking
- predictive_analytics: Forecasting and predictive modeling
- data_warehouse: Data warehousing (coming soon)
- olap_cube: OLAP cube engine (coming soon)
- data_mining: Data mining and pattern discovery (coming soon)
- streaming_analytics: Real-time streaming analytics (coming soon)
- nlq_engine: Natural language query interface (coming soon)
"""

from .bi_dashboard import (
    get_bi_dashboard,
    BIDashboard,
    KPICalculator,
    DashboardBuilder,
    ReportGenerator,
    ReportScheduler,
    KPI,
    ChartData,
    Report,
    ScheduledReport,
    ReportFormat,
    ReportFrequency,
    ChartType
)

from .predictive_analytics import (
    get_predictive_analytics,
    PredictiveAnalyticsEngine,
    ARIMAForecaster,
    ProphetForecaster,
    ChurnPredictor,
    RevenueForecaster,
    MonteCarloSimulator,
    ForecastResult,
    ChurnPrediction,
    ScenarioAnalysis,
    ForecastMethod,
    PredictionType
)

__all__ = [
    # BI Dashboard
    'get_bi_dashboard',
    'BIDashboard',
    'KPICalculator',
    'DashboardBuilder',
    'ReportGenerator',
    'ReportScheduler',
    'KPI',
    'ChartData',
    'Report',
    'ScheduledReport',
    'ReportFormat',
    'ReportFrequency',
    'ChartType',
    
    # Predictive Analytics
    'get_predictive_analytics',
    'PredictiveAnalyticsEngine',
    'ARIMAForecaster',
    'ProphetForecaster',
    'ChurnPredictor',
    'RevenueForecaster',
    'MonteCarloSimulator',
    'ForecastResult',
    'ChurnPrediction',
    'ScenarioAnalysis',
    'ForecastMethod',
    'PredictionType',
]

__version__ = '3.1.0'
