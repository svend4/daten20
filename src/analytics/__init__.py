"""
Analytics Module - v3.1

Advanced Analytics & Business Intelligence components.

Modules:
- bi_dashboard: Business Intelligence dashboards and KPI tracking ✅
- predictive_analytics: Forecasting and predictive modeling ✅
- data_warehouse: Data warehousing with ETL pipelines ✅
- olap_cube: OLAP cube engine for multidimensional analysis ✅
- data_mining: Data mining and pattern discovery ✅
- streaming_analytics: Real-time streaming analytics ✅
- nl_query: Natural language query interface ✅
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

from .data_warehouse import (
    get_data_warehouse,
    DataWarehouse,
    StarSchema,
    ETLPipeline,
    IncrementalLoader,
    DataQualityChecker,
    DimensionTable,
    FactTable,
    ETLJob,
    SCDType,
    TableType
)

from .olap_cube import (
    get_cube_manager,
    CubeManager,
    OLAPCube,
    MDXQueryEngine,
    Dimension,
    Measure,
    AggregationType
)

from .data_mining import (
    get_data_mining_engine,
    DataMiningEngine,
    ClusteringEngine,
    AprioriMiner,
    AssociationRule,
    Cluster
)

from .streaming_analytics import (
    get_stream_processor,
    StreamProcessor,
    WindowManager,
    StreamAggregator,
    ComplexEventProcessor,
    StreamEvent,
    Window,
    StreamMetrics,
    WindowType,
    AggregationType,
    EventType
)

from .nl_query import (
    get_nl_processor,
    NLQueryProcessor,
    IntentClassifier,
    EntityExtractor,
    QueryGenerator,
    ParsedQuery,
    Entity,
    TimeRange,
    QueryIntent,
    AggregateFunction,
    TimeGranularity
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

    # Data Warehouse
    'get_data_warehouse',
    'DataWarehouse',
    'StarSchema',
    'ETLPipeline',
    'IncrementalLoader',
    'DataQualityChecker',
    'DimensionTable',
    'FactTable',
    'ETLJob',
    'SCDType',
    'TableType',

    # OLAP Cube
    'get_cube_manager',
    'CubeManager',
    'OLAPCube',
    'MDXQueryEngine',
    'Dimension',
    'Measure',
    'AggregationType',

    # Data Mining
    'get_data_mining_engine',
    'DataMiningEngine',
    'ClusteringEngine',
    'AprioriMiner',
    'AssociationRule',
    'Cluster',

    # Streaming Analytics
    'get_stream_processor',
    'StreamProcessor',
    'WindowManager',
    'StreamAggregator',
    'ComplexEventProcessor',
    'StreamEvent',
    'Window',
    'StreamMetrics',
    'WindowType',
    'EventType',

    # Natural Language Query
    'get_nl_processor',
    'NLQueryProcessor',
    'IntentClassifier',
    'EntityExtractor',
    'QueryGenerator',
    'ParsedQuery',
    'Entity',
    'TimeRange',
    'QueryIntent',
    'AggregateFunction',
    'TimeGranularity',
]

__version__ = '3.1.1'
