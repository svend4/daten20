"""
Analytics Module - v3.2

Advanced Analytics & Business Intelligence components.

Modules:
- bi_dashboard: Business Intelligence dashboards and KPI tracking ✅
- predictive_analytics: Forecasting and predictive modeling ✅
- data_warehouse: Data warehousing with ETL pipelines ✅
- olap_cube: OLAP cube engine for multidimensional analysis ✅
- data_mining: Data mining and pattern discovery ✅
- streaming_analytics: Real-time streaming analytics ✅
- nl_query: Natural language query interface ✅
- anomaly_detection: Anomaly detection and outlier identification ✅
"""

from .bi_dashboard import (
    KPI,
    BIDashboard,
    ChartData,
    ChartType,
    DashboardBuilder,
    KPICalculator,
    Report,
    ReportFormat,
    ReportFrequency,
    ReportGenerator,
    ReportScheduler,
    ScheduledReport,
    get_bi_dashboard,
)
from .data_mining import (
    AprioriMiner,
    AssociationRule,
    Cluster,
    ClusteringEngine,
    DataMiningEngine,
    get_data_mining_engine,
)
from .data_warehouse import (
    DataQualityChecker,
    DataWarehouse,
    DimensionTable,
    ETLJob,
    ETLPipeline,
    FactTable,
    IncrementalLoader,
    SCDType,
    StarSchema,
    TableType,
    get_data_warehouse,
)
from .nl_query import (
    AggregateFunction,
    Entity,
    EntityExtractor,
    IntentClassifier,
    NLQueryProcessor,
    ParsedQuery,
    QueryGenerator,
    QueryIntent,
    TimeGranularity,
    TimeRange,
    get_nl_processor,
)
from .olap_cube import AggregationType, CubeManager, Dimension, MDXQueryEngine, Measure, OLAPCube, get_cube_manager
from .predictive_analytics import (
    ARIMAForecaster,
    ChurnPrediction,
    ChurnPredictor,
    ForecastMethod,
    ForecastResult,
    MonteCarloSimulator,
    PredictionType,
    PredictiveAnalyticsEngine,
    ProphetForecaster,
    RevenueForecaster,
    ScenarioAnalysis,
    get_predictive_analytics,
)
from .streaming_analytics import (
    AggregationType,
    ComplexEventProcessor,
    EventType,
    StreamAggregator,
    StreamEvent,
    StreamMetrics,
    StreamProcessor,
    Window,
    WindowManager,
    WindowType,
    get_stream_processor,
)
from .anomaly_detection import (
    Anomaly,
    AnomalyDetectionEngine,
    AnomalyDetectionResult,
    AnomalyMethod,
    AnomalySeverity,
    MLDetector,
    RealTimeDetector,
    StatisticalDetector,
    TimeSeriesDetector,
    get_anomaly_engine,
)

__all__ = [
    # BI Dashboard
    "get_bi_dashboard",
    "BIDashboard",
    "KPICalculator",
    "DashboardBuilder",
    "ReportGenerator",
    "ReportScheduler",
    "KPI",
    "ChartData",
    "Report",
    "ScheduledReport",
    "ReportFormat",
    "ReportFrequency",
    "ChartType",
    # Predictive Analytics
    "get_predictive_analytics",
    "PredictiveAnalyticsEngine",
    "ARIMAForecaster",
    "ProphetForecaster",
    "ChurnPredictor",
    "RevenueForecaster",
    "MonteCarloSimulator",
    "ForecastResult",
    "ChurnPrediction",
    "ScenarioAnalysis",
    "ForecastMethod",
    "PredictionType",
    # Data Warehouse
    "get_data_warehouse",
    "DataWarehouse",
    "StarSchema",
    "ETLPipeline",
    "IncrementalLoader",
    "DataQualityChecker",
    "DimensionTable",
    "FactTable",
    "ETLJob",
    "SCDType",
    "TableType",
    # OLAP Cube
    "get_cube_manager",
    "CubeManager",
    "OLAPCube",
    "MDXQueryEngine",
    "Dimension",
    "Measure",
    "AggregationType",
    # Data Mining
    "get_data_mining_engine",
    "DataMiningEngine",
    "ClusteringEngine",
    "AprioriMiner",
    "AssociationRule",
    "Cluster",
    # Streaming Analytics
    "get_stream_processor",
    "StreamProcessor",
    "WindowManager",
    "StreamAggregator",
    "ComplexEventProcessor",
    "StreamEvent",
    "Window",
    "StreamMetrics",
    "WindowType",
    "EventType",
    # Natural Language Query
    "get_nl_processor",
    "NLQueryProcessor",
    "IntentClassifier",
    "EntityExtractor",
    "QueryGenerator",
    "ParsedQuery",
    "Entity",
    "TimeRange",
    "QueryIntent",
    "AggregateFunction",
    "TimeGranularity",
    # Anomaly Detection
    "get_anomaly_engine",
    "AnomalyDetectionEngine",
    "StatisticalDetector",
    "MLDetector",
    "TimeSeriesDetector",
    "RealTimeDetector",
    "Anomaly",
    "AnomalyDetectionResult",
    "AnomalyMethod",
    "AnomalySeverity",
]

__version__ = "3.2.0"
