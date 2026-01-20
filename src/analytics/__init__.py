"""
Analytics Module - v3.1 (Pure Python Compatible)

Advanced Analytics & Business Intelligence components.
"""

# Import what we can, skip what we can't
try:
    from .data_mining import (
        ClusteringEngine,
        AssociationRuleMiner,
        AssociationRule,
        Cluster,
        AprioriMiner,
        DataMiningEngine,
        get_data_mining_engine,
    )
except ImportError as e:
    print(f"Warning: Could not import from data_mining: {e}")
    ClusteringEngine = None
    AssociationRuleMiner = None

try:
    from .data_warehouse import (
        DataWarehouse,
        DimensionTable,
        FactTable,
        get_data_warehouse,
    )
except ImportError as e:
    print(f"Warning: Could not import from data_warehouse: {e}")
    DataWarehouse = None

try:
    from .olap_cube import (
        OLAPCube,
        get_olap_cube,
        get_cube_manager,
    )
except ImportError as e:
    print(f"Warning: Could not import from olap_cube: {e}")
    OLAPCube = None

try:
    from .predictive_analytics import (
        TimeSeriesForecaster,
        RegressionModel,
        ClassificationModel,
        Forecast,
        PredictionResult,
    )
except ImportError as e:
    print(f"Warning: Could not import from predictive_analytics: {e}")
    TimeSeriesForecaster = None

# Keep other imports as before
try:
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
except ImportError:
    pass

__all__ = [
    "ClusteringEngine",
    "AssociationRuleMiner",
    "DataWarehouse",
    "OLAPCube",
    "TimeSeriesForecaster",
    "RegressionModel",
    "ClassificationModel",
]
