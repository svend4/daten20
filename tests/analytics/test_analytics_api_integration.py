"""
Integration Tests for Analytics API v3.1

Tests comprehensive integration of all analytics modules:
- BI Dashboard
- Predictive Analytics
- Data Warehouse
- OLAP Cube
- Natural Language Query
- ETL Orchestrator
- Streaming Analytics
- Real-time BI
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.analytics import (
    AnalyticsAPI,
    get_analytics_api,
    ETLOrchestrator,
    QueryType,
    AggregationLevel
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def analytics_api():
    """Create Analytics API instance for testing"""
    with patch('src.analytics.analytics_api.MODULES_AVAILABLE', True):
        api = AnalyticsAPI(
            database_url="sqlite:///:memory:",
            enable_cache=True,
            enable_realtime=False,  # Disable for unit tests
            enable_monitoring=True
        )
        return api


@pytest.fixture
def mock_bi_dashboard():
    """Mock BI Dashboard"""
    mock = Mock()

    # Mock KPI objects
    mock_mrr = Mock()
    mock_mrr.name = "MRR"
    mock_mrr.value = 100000
    mock_mrr.unit = "USD"
    mock_mrr.change = 12.5
    mock_mrr.target = 110000
    mock_mrr.timestamp = datetime.now()

    mock.calculate_mrr.return_value = mock_mrr
    mock.calculate_arr.return_value = mock_mrr
    mock.calculate_churn_rate.return_value = mock_mrr
    mock.calculate_clv.return_value = mock_mrr

    return mock


# ============================================================
# Analytics API Initialization Tests
# ============================================================

def test_analytics_api_initialization():
    """Test Analytics API initializes correctly"""
    api = AnalyticsAPI(database_url="sqlite:///:memory:")

    assert api.database_url is not None
    assert api.enable_cache is True
    assert api.stats["queries_executed"] == 0


def test_analytics_api_singleton():
    """Test Analytics API singleton pattern"""
    api1 = get_analytics_api()
    api2 = get_analytics_api()

    assert api1 is api2


# ============================================================
# KPI Operations Tests
# ============================================================

def test_get_kpis_success(analytics_api, mock_bi_dashboard):
    """Test getting KPIs"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    kpis = analytics_api.get_kpis(tenant_id="test_tenant")

    assert isinstance(kpis, list)
    assert len(kpis) > 0
    assert all('name' in kpi for kpi in kpis)
    assert all('value' in kpi for kpi in kpis)


def test_get_kpis_with_filter(analytics_api, mock_bi_dashboard):
    """Test getting specific KPIs"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    kpis = analytics_api.get_kpis(
        tenant_id="test_tenant",
        kpi_names=["mrr", "arr"]
    )

    assert len(kpis) == 2
    kpi_names = [kpi['name'] for kpi in kpis]
    assert "MRR" in kpi_names or any("MRR" in name for name in kpi_names)


def test_get_single_kpi(analytics_api, mock_bi_dashboard):
    """Test getting single KPI"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    kpi = analytics_api.get_kpi("mrr", tenant_id="test_tenant")

    assert kpi is not None
    assert 'name' in kpi
    assert 'value' in kpi


def test_get_kpis_caching(analytics_api, mock_bi_dashboard):
    """Test KPI result caching"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    # First call - cache miss
    kpis1 = analytics_api.get_kpis(tenant_id="test_tenant")
    cache_misses_1 = analytics_api.stats["cache_misses"]

    # Second call - cache hit
    kpis2 = analytics_api.get_kpis(tenant_id="test_tenant")
    cache_hits = analytics_api.stats["cache_hits"]

    assert cache_hits > 0
    assert kpis1 == kpis2


# ============================================================
# Dashboard Operations Tests
# ============================================================

def test_create_dashboard(analytics_api):
    """Test creating dashboard"""
    dashboard = analytics_api.create_dashboard(
        "Test Dashboard",
        "Test description",
        tenant_id="test_tenant"
    )

    assert dashboard is not None
    assert 'dashboard_id' in dashboard
    assert dashboard['name'] == "Test Dashboard"
    assert dashboard['tenant_id'] == "test_tenant"


def test_create_dashboard_with_widgets(analytics_api):
    """Test creating dashboard with widgets"""
    from src.analytics.analytics_api import DashboardWidget, AnalyticsQuery

    widget = DashboardWidget(
        widget_id="test_widget",
        widget_type="kpi",
        title="MRR Widget",
        query=AnalyticsQuery(
            query_id="test_query",
            query_type=QueryType.KPI,
            parameters={"kpi_name": "mrr"}
        )
    )

    dashboard = analytics_api.create_dashboard(
        "Dashboard with Widgets",
        widgets=[widget]
    )

    assert len(dashboard['widgets']) == 1
    assert dashboard['widgets'][0]['widget_id'] == "test_widget"


# ============================================================
# Report Operations Tests
# ============================================================

def test_generate_report_json(analytics_api, mock_bi_dashboard):
    """Test generating JSON report"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    report = analytics_api.generate_report(
        "executive",
        (datetime.now() - timedelta(days=30), datetime.now()),
        format="json"
    )

    assert isinstance(report, dict)
    assert 'report_type' in report
    assert 'date_range' in report
    assert 'kpis' in report


def test_generate_report_pdf(analytics_api, mock_bi_dashboard):
    """Test generating PDF report"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    report = analytics_api.generate_report(
        "executive",
        (datetime.now() - timedelta(days=30), datetime.now()),
        format="pdf"
    )

    assert isinstance(report, bytes)


def test_schedule_report(analytics_api):
    """Test scheduling report"""
    schedule = analytics_api.schedule_report(
        "executive",
        "0 9 * * *",  # Daily at 9 AM
        ["admin@example.com"],
        format="pdf"
    )

    assert 'schedule_id' in schedule
    assert schedule['enabled'] is True
    assert schedule['schedule'] == "0 9 * * *"


# ============================================================
# Predictive Analytics Tests
# ============================================================

def test_predict_revenue(analytics_api):
    """Test revenue prediction"""
    with patch.object(analytics_api, 'predictive') as mock_predictive:
        mock_forecast = Mock()
        mock_forecast.predictions = [
            {"date": datetime.now(), "value": 100000, "lower": 90000, "upper": 110000}
        ]
        mock_forecast.model_name = "ARIMA"

        mock_predictive.forecast_timeseries.return_value = mock_forecast

        forecast = analytics_api.predict_revenue(days=30)

        assert 'forecast' in forecast
        assert 'metadata' in forecast
        assert len(forecast['forecast']) > 0


def test_predict_churn(analytics_api):
    """Test churn prediction"""
    prediction = analytics_api.predict_churn(customer_id="cust_123")

    assert 'customer_id' in prediction
    assert 'churn_probability' in prediction
    assert 'risk_level' in prediction


# ============================================================
# Natural Language Query Tests
# ============================================================

def test_nl_query_success(analytics_api):
    """Test natural language query"""
    with patch.object(analytics_api, 'nl_processor') as mock_nl:
        mock_parsed = Mock()
        mock_parsed.intent = "aggregate"

        mock_nl.parse_query.return_value = mock_parsed
        mock_nl.generate_sql.return_value = "SELECT * FROM customers"
        mock_nl.execute_query.return_value = [{"id": 1, "name": "Test"}]

        result = analytics_api.query("Show me top customers")

        assert 'question' in result
        assert 'intent' in result
        assert 'sql' in result
        assert 'results' in result


def test_nl_query_error_handling(analytics_api):
    """Test NL query error handling"""
    with patch.object(analytics_api, 'nl_processor') as mock_nl:
        mock_nl.parse_query.side_effect = Exception("Parse error")

        result = analytics_api.query("Invalid query")

        assert 'error' in result


# ============================================================
# OLAP Operations Tests
# ============================================================

def test_slice_dice(analytics_api):
    """Test OLAP slice and dice"""
    with patch.object(analytics_api, 'olap') as mock_olap:
        mock_cube = Mock()
        mock_cube.slice.return_value = {"data": [1, 2, 3]}
        mock_olap.get_cube.return_value = mock_cube

        result = analytics_api.slice_dice(
            "sales_cube",
            ["region", "product"],
            {"year": 2024}
        )

        assert 'data' in result
        assert 'dimensions' in result


def test_drill_down(analytics_api):
    """Test OLAP drill down"""
    with patch.object(analytics_api, 'olap') as mock_olap:
        mock_cube = Mock()
        mock_cube.drill_down.return_value = {"data": [1, 2, 3]}
        mock_olap.get_cube.return_value = mock_cube

        result = analytics_api.drill_down("sales_cube", "region", "US")

        assert 'data' in result


# ============================================================
# ETL Operations Tests
# ============================================================

def test_create_pipeline(analytics_api):
    """Test creating ETL pipeline"""
    with patch.object(analytics_api, 'etl') as mock_etl:
        mock_pipeline = Mock()
        mock_pipeline.pipeline_id = "test_pipeline"
        mock_etl.create_pipeline.return_value = mock_pipeline

        async def dummy_task():
            pass

        pipeline_id = analytics_api.create_pipeline(
            "Test Pipeline",
            [
                {
                    "task_id": "task1",
                    "name": "Test Task",
                    "function": dummy_task
                }
            ]
        )

        assert pipeline_id == "test_pipeline"


def test_run_pipeline(analytics_api):
    """Test running ETL pipeline"""
    result = analytics_api.run_pipeline("test_pipeline")

    assert 'pipeline_id' in result
    assert 'status' in result


# ============================================================
# Streaming Analytics Tests
# ============================================================

def test_process_stream(analytics_api):
    """Test processing streaming data"""
    with patch.object(analytics_api, 'streaming') as mock_streaming:
        mock_streaming.process_event.return_value = True

        result = analytics_api.process_stream(
            "test_stream",
            {"event": "page_view", "user_id": "user123"}
        )

        assert 'stream_id' in result
        assert result['status'] == "processed"


# ============================================================
# Cache Operations Tests
# ============================================================

def test_cache_clearing(analytics_api, mock_bi_dashboard):
    """Test cache clearing"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    # Populate cache
    analytics_api.get_kpis(tenant_id="test_tenant")
    assert len(analytics_api._cache) > 0

    # Clear cache
    analytics_api.clear_cache()
    assert len(analytics_api._cache) == 0


# ============================================================
# Statistics Tests
# ============================================================

def test_get_stats(analytics_api, mock_bi_dashboard):
    """Test getting API statistics"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    # Execute some queries
    analytics_api.get_kpis(tenant_id="test1")
    analytics_api.get_kpis(tenant_id="test2")

    stats = analytics_api.get_stats()

    assert 'queries_executed' in stats
    assert stats['queries_executed'] > 0
    assert 'cache_hit_rate' in stats
    assert 'avg_execution_time_ms' in stats


# ============================================================
# Error Handling Tests
# ============================================================

def test_api_without_modules():
    """Test API behavior when modules not available"""
    with patch('src.analytics.analytics_api.MODULES_AVAILABLE', False):
        api = AnalyticsAPI()

        kpis = api.get_kpis()
        assert kpis == []

        forecast = api.predict_revenue()
        assert forecast == {}


# ============================================================
# Integration Flow Tests
# ============================================================

@pytest.mark.integration
def test_full_analytics_workflow(analytics_api, mock_bi_dashboard):
    """Test complete analytics workflow"""
    analytics_api.bi_dashboard = mock_bi_dashboard

    # 1. Get KPIs
    kpis = analytics_api.get_kpis(tenant_id="acme")
    assert len(kpis) > 0

    # 2. Create dashboard
    dashboard = analytics_api.create_dashboard(
        "ACME Dashboard",
        tenant_id="acme"
    )
    assert dashboard['dashboard_id'] is not None

    # 3. Generate report
    report = analytics_api.generate_report(
        "executive",
        (datetime.now() - timedelta(days=30), datetime.now())
    )
    assert report['report_type'] == "executive"

    # 4. Get predictions
    with patch.object(analytics_api, 'predictive') as mock_predictive:
        mock_forecast = Mock()
        mock_forecast.predictions = [
            {"date": datetime.now(), "value": 100000}
        ]
        mock_forecast.model_name = "ARIMA"
        mock_predictive.forecast_timeseries.return_value = mock_forecast

        forecast = analytics_api.predict_revenue(days=30)
        assert 'forecast' in forecast

    # 5. Check statistics
    stats = analytics_api.get_stats()
    assert stats['queries_executed'] > 0


# ============================================================
# Performance Tests
# ============================================================

@pytest.mark.performance
def test_kpi_query_performance(analytics_api, mock_bi_dashboard):
    """Test KPI query performance"""
    import time

    analytics_api.bi_dashboard = mock_bi_dashboard

    start = time.time()
    for i in range(100):
        analytics_api.get_kpis(tenant_id=f"tenant_{i}")
    duration = time.time() - start

    assert duration < 5.0  # Should complete 100 queries in <5 seconds
    print(f"\n⏱️  100 KPI queries in {duration:.2f}s ({duration/100*1000:.2f}ms avg)")


@pytest.mark.performance
def test_cache_performance(analytics_api, mock_bi_dashboard):
    """Test cache performance improvement"""
    import time

    analytics_api.bi_dashboard = mock_bi_dashboard

    # First call (cache miss)
    start = time.time()
    kpis1 = analytics_api.get_kpis(tenant_id="test")
    uncached_time = time.time() - start

    # Second call (cache hit)
    start = time.time()
    kpis2 = analytics_api.get_kpis(tenant_id="test")
    cached_time = time.time() - start

    # Cache should be faster
    assert cached_time < uncached_time
    print(f"\n⚡ Cache speedup: {uncached_time/cached_time:.1f}x faster")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
