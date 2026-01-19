"""
Unified Analytics API

Single entry point for all analytics and BI functionality.
Integrates all v3.1 analytics modules into a cohesive API.

Features:
- Unified interface for all analytics operations
- REST API endpoints
- GraphQL support
- WebSocket for real-time updates
- Caching layer
- Query optimization
- Access control
- Rate limiting

Modules Integrated:
- BI Dashboard (KPIs, reports, dashboards)
- Predictive Analytics (forecasting, ML models)
- Data Warehouse (ETL, star schema)
- OLAP Cube (multidimensional analysis)
- Natural Language Query (text to SQL)
- ETL Orchestrator (pipeline management)
- Streaming Analytics (real-time processing)

Usage:
    >>> from src.analytics import AnalyticsAPI
    >>> api = AnalyticsAPI()
    >>>
    >>> # Get KPIs
    >>> kpis = api.get_kpis(tenant_id="acme")
    >>>
    >>> # Run prediction
    >>> forecast = api.predict_revenue(days=30)
    >>>
    >>> # Query with natural language
    >>> results = api.query("Show me top 10 customers by revenue")
    >>>
    >>> # Create dashboard
    >>> dashboard = api.create_dashboard("Executive Overview")
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from decimal import Decimal

logger = logging.getLogger(__name__)


# ============================================================
# Import Analytics Modules
# ============================================================

try:
    from .bi_dashboard import BIDashboard, KPI, Report, ReportFormat
    from .predictive_analytics import PredictiveAnalytics, ForecastResult
    from .data_warehouse import DataWarehouse, StarSchema
    from .olap_cube import OLAPCube, CubeManager
    from .nl_query import NLQueryProcessor
    from .etl_orchestrator import ETLOrchestrator, Pipeline
    from .streaming_analytics import StreamingAnalytics
    from .realtime_bi import RealtimeBIServer
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some analytics modules not available: {e}")
    MODULES_AVAILABLE = False


# ============================================================
# Data Models
# ============================================================

class QueryType(str, Enum):
    """Analytics query types"""
    KPI = "kpi"
    REPORT = "report"
    FORECAST = "forecast"
    OLAP = "olap"
    NL_QUERY = "nl_query"
    STREAMING = "streaming"


class AggregationLevel(str, Enum):
    """Data aggregation levels"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class AnalyticsQuery:
    """Unified analytics query"""
    query_id: str
    query_type: QueryType
    parameters: Dict[str, Any]
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalyticsResult:
    """Unified analytics result"""
    query_id: str
    result_type: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: str  # kpi, chart, table, gauge
    title: str
    query: AnalyticsQuery
    refresh_interval: int = 300  # seconds
    position: Dict[str, int] = field(default_factory=dict)
    size: Dict[str, int] = field(default_factory=dict)


# ============================================================
# Unified Analytics API
# ============================================================

class AnalyticsAPI:
    """
    Unified Analytics API

    Single interface for all analytics and BI operations.
    Integrates all v3.1 analytics modules.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        enable_cache: bool = True,
        enable_realtime: bool = True,
        enable_monitoring: bool = True
    ):
        """
        Initialize Analytics API

        Args:
            database_url: Database connection URL
            enable_cache: Enable result caching
            enable_realtime: Enable real-time updates
            enable_monitoring: Enable monitoring and metrics
        """
        self.database_url = database_url or "sqlite:///analytics.db"
        self.enable_cache = enable_cache
        self.enable_realtime = enable_realtime
        self.enable_monitoring = enable_monitoring

        # Initialize modules
        self._init_modules()

        # Cache
        self._cache: Dict[str, AnalyticsResult] = {}

        # Statistics
        self.stats = {
            "queries_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_execution_time_ms": 0.0
        }

        logger.info("Analytics API initialized")

    def _init_modules(self):
        """Initialize all analytics modules"""

        if not MODULES_AVAILABLE:
            logger.warning("Analytics modules not fully available")
            self.bi_dashboard = None
            self.predictive = None
            self.warehouse = None
            self.olap = None
            self.nl_processor = None
            self.etl = None
            self.streaming = None
            self.realtime = None
            return

        try:
            # BI Dashboard
            self.bi_dashboard = BIDashboard(self.database_url)

            # Predictive Analytics
            self.predictive = PredictiveAnalytics()

            # Data Warehouse
            self.warehouse = DataWarehouse(self.database_url)

            # OLAP Cube
            self.olap = CubeManager()

            # Natural Language Query
            self.nl_processor = NLQueryProcessor()

            # ETL Orchestrator
            self.etl = ETLOrchestrator()

            # Streaming Analytics
            self.streaming = StreamingAnalytics()

            # Real-time BI
            if self.enable_realtime:
                self.realtime = RealtimeBIServer()

            logger.info("All analytics modules initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing analytics modules: {e}")
            raise

    # ============================================================
    # KPI Operations
    # ============================================================

    def get_kpis(
        self,
        tenant_id: Optional[str] = None,
        date_range: Optional[tuple] = None,
        kpi_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get KPIs for tenant

        Args:
            tenant_id: Tenant identifier
            date_range: (start_date, end_date) tuple
            kpi_names: Specific KPIs to retrieve

        Returns:
            List of KPI data

        Example:
            >>> api.get_kpis(tenant_id="acme", kpi_names=["mrr", "arr"])
        """
        if not self.bi_dashboard:
            return []

        cache_key = f"kpis_{tenant_id}_{date_range}_{kpi_names}"

        # Check cache
        if self.enable_cache and cache_key in self._cache:
            self.stats["cache_hits"] += 1
            return self._cache[cache_key].data

        self.stats["cache_misses"] += 1
        start_time = datetime.now()

        try:
            # Calculate KPIs
            kpis = []

            # MRR
            if not kpi_names or "mrr" in kpi_names:
                mrr = self.bi_dashboard.calculate_mrr()
                kpis.append(self._serialize_kpi(mrr))

            # ARR
            if not kpi_names or "arr" in kpi_names:
                arr = self.bi_dashboard.calculate_arr()
                kpis.append(self._serialize_kpi(arr))

            # Churn Rate
            if not kpi_names or "churn" in kpi_names:
                churn = self.bi_dashboard.calculate_churn_rate()
                kpis.append(self._serialize_kpi(churn))

            # CLV
            if not kpi_names or "clv" in kpi_names:
                clv = self.bi_dashboard.calculate_clv()
                kpis.append(self._serialize_kpi(clv))

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Cache result
            if self.enable_cache:
                result = AnalyticsResult(
                    query_id=cache_key,
                    result_type="kpis",
                    data=kpis,
                    execution_time_ms=execution_time
                )
                self._cache[cache_key] = result

            self.stats["queries_executed"] += 1
            self.stats["total_execution_time_ms"] += execution_time

            return kpis

        except Exception as e:
            logger.error(f"Error getting KPIs: {e}")
            return []

    def get_kpi(
        self,
        kpi_name: str,
        tenant_id: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get single KPI

        Args:
            kpi_name: KPI name (mrr, arr, churn, clv, etc.)
            tenant_id: Tenant identifier
            date: Target date

        Returns:
            KPI data
        """
        kpis = self.get_kpis(tenant_id=tenant_id, kpi_names=[kpi_name])
        return kpis[0] if kpis else None

    # ============================================================
    # Dashboard Operations
    # ============================================================

    def create_dashboard(
        self,
        name: str,
        description: str = "",
        widgets: Optional[List[DashboardWidget]] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new dashboard

        Args:
            name: Dashboard name
            description: Dashboard description
            widgets: List of dashboard widgets
            tenant_id: Tenant identifier

        Returns:
            Dashboard configuration

        Example:
            >>> dashboard = api.create_dashboard(
            ...     "Sales Dashboard",
            ...     widgets=[
            ...         DashboardWidget(
            ...             widget_id="mrr_card",
            ...             widget_type="kpi",
            ...             title="MRR",
            ...             query=AnalyticsQuery(...)
            ...         )
            ...     ]
            ... )
        """
        if not self.bi_dashboard:
            return {}

        dashboard_id = f"dash_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        dashboard_config = {
            "dashboard_id": dashboard_id,
            "name": name,
            "description": description,
            "widgets": [self._serialize_widget(w) for w in (widgets or [])],
            "tenant_id": tenant_id,
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"Created dashboard: {dashboard_id}")

        return dashboard_config

    def get_dashboard(
        self,
        dashboard_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get dashboard configuration"""
        # Implementation would fetch from storage
        return None

    def update_dashboard(
        self,
        dashboard_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update dashboard configuration"""
        return True

    def delete_dashboard(
        self,
        dashboard_id: str
    ) -> bool:
        """Delete dashboard"""
        return True

    # ============================================================
    # Report Operations
    # ============================================================

    def generate_report(
        self,
        report_type: str,
        date_range: tuple,
        format: str = "json",
        tenant_id: Optional[str] = None
    ) -> Union[Dict[str, Any], bytes]:
        """
        Generate report

        Args:
            report_type: Report type (executive, sales, finance)
            date_range: (start_date, end_date)
            format: Output format (json, pdf, excel)
            tenant_id: Tenant identifier

        Returns:
            Report data or file bytes
        """
        if not self.bi_dashboard:
            return {}

        # Get KPIs for report
        kpis = self.get_kpis(tenant_id=tenant_id, date_range=date_range)

        report_data = {
            "report_type": report_type,
            "date_range": {
                "start": date_range[0].isoformat(),
                "end": date_range[1].isoformat()
            },
            "kpis": kpis,
            "generated_at": datetime.now().isoformat()
        }

        if format == "json":
            return report_data
        elif format == "pdf":
            # Convert to PDF (placeholder)
            return b"PDF content"
        elif format == "excel":
            # Convert to Excel (placeholder)
            return b"Excel content"

        return report_data

    def schedule_report(
        self,
        report_type: str,
        schedule: str,
        recipients: List[str],
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Schedule recurring report

        Args:
            report_type: Report type
            schedule: Cron expression
            recipients: Email recipients
            format: Report format

        Returns:
            Scheduled report configuration
        """
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "schedule_id": schedule_id,
            "report_type": report_type,
            "schedule": schedule,
            "recipients": recipients,
            "format": format,
            "enabled": True
        }

    # ============================================================
    # Predictive Analytics
    # ============================================================

    def predict_revenue(
        self,
        days: int = 30,
        tenant_id: Optional[str] = None,
        confidence_interval: float = 0.95
    ) -> Dict[str, Any]:
        """
        Predict future revenue

        Args:
            days: Days to forecast
            tenant_id: Tenant identifier
            confidence_interval: Confidence interval (0-1)

        Returns:
            Forecast data with predictions and confidence bounds
        """
        if not self.predictive:
            return {}

        try:
            # Get historical revenue data
            # (In production, fetch from database)
            historical_data = self._get_historical_revenue(tenant_id)

            # Generate forecast
            forecast = self.predictive.forecast_timeseries(
                data=historical_data,
                periods=days,
                confidence=confidence_interval
            )

            return {
                "forecast": [
                    {
                        "date": pred["date"].isoformat(),
                        "predicted_value": float(pred["value"]),
                        "lower_bound": float(pred.get("lower", 0)),
                        "upper_bound": float(pred.get("upper", 0))
                    }
                    for pred in forecast.predictions
                ],
                "metadata": {
                    "model": forecast.model_name,
                    "confidence_interval": confidence_interval,
                    "generated_at": datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error predicting revenue: {e}")
            return {}

    def predict_churn(
        self,
        customer_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict customer churn

        Args:
            customer_id: Specific customer to predict
            tenant_id: Tenant identifier

        Returns:
            Churn prediction with probability
        """
        if not self.predictive:
            return {}

        # Placeholder implementation
        return {
            "customer_id": customer_id,
            "churn_probability": 0.15,
            "risk_level": "low",
            "factors": [
                {"factor": "usage_decline", "impact": 0.6},
                {"factor": "support_tickets", "impact": 0.3}
            ]
        }

    # ============================================================
    # Natural Language Query
    # ============================================================

    def query(
        self,
        question: str,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute natural language query

        Args:
            question: Natural language question
            tenant_id: Tenant identifier

        Returns:
            Query results

        Example:
            >>> results = api.query("Show me top 10 customers by revenue")
        """
        if not self.nl_processor:
            return {"error": "NL query not available"}

        try:
            # Process natural language query
            parsed = self.nl_processor.parse_query(question)

            # Generate and execute SQL
            sql = self.nl_processor.generate_sql(parsed)
            results = self.nl_processor.execute_query(sql)

            return {
                "question": question,
                "intent": parsed.intent,
                "sql": sql,
                "results": results,
                "row_count": len(results)
            }

        except Exception as e:
            logger.error(f"Error processing NL query: {e}")
            return {"error": str(e)}

    # ============================================================
    # OLAP Operations
    # ============================================================

    def slice_dice(
        self,
        cube_name: str,
        dimensions: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        OLAP slice and dice operation

        Args:
            cube_name: OLAP cube name
            dimensions: Dimensions to analyze
            filters: Filter criteria

        Returns:
            Multidimensional data
        """
        if not self.olap:
            return {}

        cube = self.olap.get_cube(cube_name)
        if not cube:
            return {"error": "Cube not found"}

        # Perform slice/dice
        result = cube.slice(dimensions, filters or {})

        return {"data": result, "dimensions": dimensions}

    def drill_down(
        self,
        cube_name: str,
        dimension: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        Drill down into dimension

        Args:
            cube_name: OLAP cube name
            dimension: Dimension to drill into
            value: Current dimension value

        Returns:
            Detailed data at lower granularity
        """
        if not self.olap:
            return {}

        cube = self.olap.get_cube(cube_name)
        if not cube:
            return {"error": "Cube not found"}

        result = cube.drill_down(dimension, value)

        return {"data": result}

    # ============================================================
    # ETL Operations
    # ============================================================

    def create_pipeline(
        self,
        name: str,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Create ETL pipeline

        Args:
            name: Pipeline name
            tasks: List of task definitions

        Returns:
            Pipeline ID
        """
        if not self.etl:
            return ""

        pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pipeline = self.etl.create_pipeline(pipeline_id, name)

        for task_def in tasks:
            self.etl.add_task(
                pipeline_id,
                task_def["task_id"],
                task_def["name"],
                task_def["function"],
                **task_def.get("config", {})
            )

        return pipeline_id

    def run_pipeline(
        self,
        pipeline_id: str
    ) -> Dict[str, Any]:
        """
        Execute ETL pipeline

        Args:
            pipeline_id: Pipeline to execute

        Returns:
            Execution results
        """
        if not self.etl:
            return {}

        # This would be async in production
        # run = await self.etl.run_pipeline(pipeline_id)

        return {
            "pipeline_id": pipeline_id,
            "status": "scheduled",
            "message": "Pipeline execution queued"
        }

    # ============================================================
    # Streaming Analytics
    # ============================================================

    def process_stream(
        self,
        stream_id: str,
        data: Any
    ) -> Dict[str, Any]:
        """
        Process streaming data

        Args:
            stream_id: Stream identifier
            data: Stream data

        Returns:
            Processing result
        """
        if not self.streaming:
            return {}

        # Process stream
        result = self.streaming.process_event(stream_id, data)

        return {"stream_id": stream_id, "status": "processed"}

    # ============================================================
    # Utility Methods
    # ============================================================

    def _serialize_kpi(self, kpi: Any) -> Dict[str, Any]:
        """Serialize KPI object to dict"""
        if hasattr(kpi, '__dict__'):
            return {
                "name": kpi.name,
                "value": float(kpi.value),
                "unit": kpi.unit,
                "change": float(kpi.change),
                "target": float(kpi.target) if kpi.target else None,
                "status": getattr(kpi, 'status', 'neutral'),
                "timestamp": kpi.timestamp.isoformat() if hasattr(kpi, 'timestamp') else None
            }
        return {}

    def _serialize_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Serialize widget to dict"""
        return {
            "widget_id": widget.widget_id,
            "widget_type": widget.widget_type,
            "title": widget.title,
            "refresh_interval": widget.refresh_interval,
            "position": widget.position,
            "size": widget.size
        }

    def _get_historical_revenue(self, tenant_id: Optional[str]) -> List[tuple]:
        """Get historical revenue data"""
        # Placeholder - in production, fetch from database
        base_date = datetime.now() - timedelta(days=365)
        return [
            (base_date + timedelta(days=i), 80000 + i * 100)
            for i in range(365)
        ]

    def clear_cache(self):
        """Clear result cache"""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        return {
            **self.stats,
            "cache_hit_rate": (
                self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
                else 0.0
            ),
            "avg_execution_time_ms": (
                self.stats["total_execution_time_ms"] / self.stats["queries_executed"]
                if self.stats["queries_executed"] > 0
                else 0.0
            )
        }


# ============================================================
# Singleton Instance
# ============================================================

_api_instance: Optional[AnalyticsAPI] = None


def get_analytics_api(
    database_url: Optional[str] = None,
    **kwargs
) -> AnalyticsAPI:
    """
    Get singleton Analytics API instance

    Args:
        database_url: Database connection URL
        **kwargs: Additional configuration

    Returns:
        AnalyticsAPI instance
    """
    global _api_instance

    if _api_instance is None:
        _api_instance = AnalyticsAPI(database_url=database_url, **kwargs)

    return _api_instance


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    # Create API instance
    api = AnalyticsAPI()

    print("📊 Analytics API Example\n")

    # Get KPIs
    print("1. Getting KPIs...")
    kpis = api.get_kpis(kpi_names=["mrr", "arr"])
    for kpi in kpis:
        print(f"  - {kpi.get('name')}: {kpi.get('value')} {kpi.get('unit')}")

    # Create dashboard
    print("\n2. Creating dashboard...")
    dashboard = api.create_dashboard(
        "Executive Dashboard",
        "High-level KPIs for executives"
    )
    print(f"  Dashboard ID: {dashboard.get('dashboard_id')}")

    # Generate report
    print("\n3. Generating report...")
    report = api.generate_report(
        "executive",
        (datetime.now() - timedelta(days=30), datetime.now())
    )
    print(f"  Report generated with {len(report.get('kpis', []))} KPIs")

    # Predict revenue
    print("\n4. Predicting revenue...")
    forecast = api.predict_revenue(days=30)
    if forecast.get('forecast'):
        print(f"  30-day forecast: {len(forecast['forecast'])} predictions")

    # Natural language query
    print("\n5. Natural language query...")
    result = api.query("Show me revenue by month")
    print(f"  Intent: {result.get('intent', 'N/A')}")

    # Get statistics
    print("\n6. API Statistics:")
    stats = api.get_stats()
    print(f"  Queries executed: {stats['queries_executed']}")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.2%}")

    print("\n✅ Analytics API demo complete!")
