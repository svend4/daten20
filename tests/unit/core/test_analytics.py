"""
Comprehensive tests for core/analytics.py module.

Tests analytics engine, service analysis, comparisons, forecasting,
time series generation, and recommendations.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch


# ============================================================================
# AnalyticsEngine Tests
# ============================================================================


class TestAnalyticsEngine:
    """Test AnalyticsEngine functionality."""

    @pytest.fixture
    def analytics_engine(self):
        """Create AnalyticsEngine instance."""
        from src.core.analytics import AnalyticsEngine

        return AnalyticsEngine()

    @pytest.fixture
    def sample_services(self):
        """Create sample services for testing."""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        services = []

        # Service 1: Berlin, standard, 35€
        services.append(
            Service(
                id=1,
                basic_info=BasicInfo(
                    service_name="Service Berlin 1",
                    target_group="Elderly",
                    region="Berlin"
                ),
                financial=Financial(
                    brutto_rate=35.0,
                    region_coefficient=1.0
                ),
                system_settings=SystemSettings(
                    service_type="standard",
                    use_umlages=False
                ),
                created_at=datetime(2024, 1, 15)
            )
        )

        # Service 2: Munich, premium, 45€
        services.append(
            Service(
                id=2,
                basic_info=BasicInfo(
                    service_name="Service Munich 1",
                    target_group="Disabled",
                    region="Munich"
                ),
                financial=Financial(
                    brutto_rate=45.0,
                    region_coefficient=1.1
                ),
                system_settings=SystemSettings(
                    service_type="premium",
                    use_umlages=True
                ),
                created_at=datetime(2024, 1, 20)
            )
        )

        # Service 3: Berlin, standard, 25€
        services.append(
            Service(
                id=3,
                basic_info=BasicInfo(
                    service_name="Service Berlin 2",
                    target_group="Children",
                    region="Berlin"
                ),
                financial=Financial(
                    brutto_rate=25.0,
                    region_coefficient=1.0
                ),
                system_settings=SystemSettings(
                    service_type="standard",
                    use_umlages=False
                ),
                created_at=datetime(2024, 2, 10)
            )
        )

        return services

    def test_analytics_engine_initialization(self, analytics_engine):
        """Test AnalyticsEngine initialization"""
        assert analytics_engine is not None
        assert analytics_engine.calculator is not None

    def test_analyze_services_empty(self, analytics_engine):
        """Test analyzing empty service list"""
        result = analytics_engine.analyze_services([])

        assert "error" in result
        assert result["error"] == "No services to analyze"

    def test_analyze_services_basic(self, analytics_engine, sample_services):
        """Test basic service analysis"""
        result = analytics_engine.analyze_services(sample_services)

        assert result["total_services"] == 3
        assert "by_region" in result
        assert "by_type" in result
        assert "financial_stats" in result
        assert "cost_distribution" in result
        assert "recommendations" in result

    def test_analyze_by_region(self, analytics_engine, sample_services):
        """Test analysis by region"""
        result = analytics_engine._analyze_by_region(sample_services)

        assert result["Berlin"] == 2
        assert result["Munich"] == 1

    def test_analyze_by_region_missing_region(self, analytics_engine):
        """Test analysis with services missing region"""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        service = Service(
            id=1,
            basic_info=BasicInfo(service_name="Test", target_group="Test", region=None),
            financial=Financial(brutto_rate=30.0),
            system_settings=SystemSettings(service_type="standard")
        )

        result = analytics_engine._analyze_by_region([service])

        assert "Не указан" in result
        assert result["Не указан"] == 1

    def test_analyze_by_type(self, analytics_engine, sample_services):
        """Test analysis by service type"""
        result = analytics_engine._analyze_by_type(sample_services)

        assert result["standard"] == 2
        assert result["premium"] == 1

    def test_analyze_by_type_missing_type(self, analytics_engine):
        """Test analysis with services missing type"""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        service = Service(
            id=1,
            basic_info=BasicInfo(service_name="Test", target_group="Test", region="Berlin"),
            financial=Financial(brutto_rate=30.0),
            system_settings=SystemSettings(service_type=None)
        )

        result = analytics_engine._analyze_by_type([service])

        assert "Не указан" in result

    def test_analyze_financial_stats(self, analytics_engine, sample_services):
        """Test financial statistics analysis"""
        result = analytics_engine._analyze_financial(sample_services)

        assert "brutto_rates" in result
        brutto = result["brutto_rates"]

        assert brutto["min"] == 25.0
        assert brutto["max"] == 45.0
        assert brutto["avg"] == 35.0  # (35 + 45 + 25) / 3

    def test_analyze_financial_empty(self, analytics_engine):
        """Test financial analysis with no services"""
        result = analytics_engine._analyze_financial([])

        assert result == {}

    def test_analyze_financial_median(self, analytics_engine, sample_services):
        """Test median calculation in financial analysis"""
        result = analytics_engine._analyze_financial(sample_services)

        brutto = result["brutto_rates"]
        assert brutto["median"] == 35.0  # Middle value of [25, 35, 45]

    def test_median_odd_count(self, analytics_engine):
        """Test median with odd number of values"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        median = analytics_engine._median(values)

        assert median == 3.0

    def test_median_even_count(self, analytics_engine):
        """Test median with even number of values"""
        values = [1.0, 2.0, 3.0, 4.0]
        median = analytics_engine._median(values)

        assert median == 2.5  # (2 + 3) / 2

    def test_analyze_cost_distribution(self, analytics_engine, sample_services):
        """Test cost distribution analysis"""
        result = analytics_engine._analyze_cost_distribution(sample_services)

        # Check that distribution buckets exist
        assert "0-20" in result
        assert "20-30" in result
        assert "30-40" in result
        assert "40-50" in result
        assert "50+" in result

    def test_generate_recommendations_rate_variation(self, analytics_engine):
        """Test recommendations for high rate variation"""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="S1", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=20.0),
                system_settings=SystemSettings(service_type="standard", use_umlages=False)
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="S2", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=50.0),
                system_settings=SystemSettings(service_type="standard", use_umlages=False)
            )
        ]

        recommendations = analytics_engine._generate_recommendations(services)

        # Should recommend standardization due to high variation (30€)
        assert any("разброс ставок" in r for r in recommendations)

    def test_generate_recommendations_few_regions(self, analytics_engine):
        """Test recommendations for limited regional coverage"""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="S1", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=30.0),
                system_settings=SystemSettings(service_type="standard")
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="S2", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=35.0),
                system_settings=SystemSettings(service_type="standard")
            )
        ]

        recommendations = analytics_engine._generate_recommendations(services)

        # Should recommend expansion (only 1 region)
        assert any("регионов" in r for r in recommendations)

    def test_generate_recommendations_mixed_calculation_modes(self, analytics_engine):
        """Test recommendations for mixed calculation modes"""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="S1", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=30.0),
                system_settings=SystemSettings(service_type="standard", use_umlages=True)
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="S2", target_group="T", region="Munich"),
                financial=Financial(brutto_rate=35.0),
                system_settings=SystemSettings(service_type="standard", use_umlages=False)
            )
        ]

        recommendations = analytics_engine._generate_recommendations(services)

        # Should recommend unification
        assert any("режимы расчета" in r for r in recommendations)


# ============================================================================
# Service Comparison Tests
# ============================================================================


class TestServiceComparison:
    """Test service comparison functionality."""

    @pytest.fixture
    def analytics_engine(self):
        """Create AnalyticsEngine instance."""
        from src.core.analytics import AnalyticsEngine

        return AnalyticsEngine()

    @pytest.fixture
    def services_for_comparison(self):
        """Create services for comparison."""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        return [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="Low Cost", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=25.0, region_coefficient=1.0),
                system_settings=SystemSettings(service_type="standard")
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="High Cost", target_group="T", region="Munich"),
                financial=Financial(brutto_rate=45.0, region_coefficient=1.1),
                system_settings=SystemSettings(service_type="premium")
            ),
            Service(
                id=3,
                basic_info=BasicInfo(service_name="Medium Cost", target_group="T", region="Hamburg"),
                financial=Financial(brutto_rate=35.0, region_coefficient=1.05),
                system_settings=SystemSettings(service_type="standard")
            )
        ]

    def test_compare_services_basic(self, analytics_engine, services_for_comparison):
        """Test basic service comparison"""
        result = analytics_engine.compare_services([1, 2], services_for_comparison)

        assert "services" in result
        assert "summary" in result
        assert len(result["services"]) == 2

    def test_compare_services_empty_ids(self, analytics_engine, services_for_comparison):
        """Test comparison with no matching IDs"""
        result = analytics_engine.compare_services([999], services_for_comparison)

        assert "error" in result
        assert result["error"] == "No services found for comparison"

    def test_compare_services_summary(self, analytics_engine, services_for_comparison):
        """Test comparison summary statistics"""
        result = analytics_engine.compare_services([1, 2, 3], services_for_comparison)

        assert "summary" in result
        summary = result["summary"]

        assert "min_rate" in summary
        assert "max_rate" in summary
        assert "avg_rate" in summary
        assert "difference" in summary

    def test_compare_services_single_service(self, analytics_engine, services_for_comparison):
        """Test comparison with single service"""
        result = analytics_engine.compare_services([1], services_for_comparison)

        assert len(result["services"]) == 1
        # Summary requires at least 2 services
        assert "summary" in result


# ============================================================================
# Cost Forecasting Tests
# ============================================================================


class TestCostForecasting:
    """Test cost forecasting functionality."""

    @pytest.fixture
    def analytics_engine(self):
        """Create AnalyticsEngine instance."""
        from src.core.analytics import AnalyticsEngine

        return AnalyticsEngine()

    @pytest.fixture
    def base_service(self):
        """Create base service for forecasting."""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        return Service(
            id=1,
            basic_info=BasicInfo(service_name="Base Service", target_group="Test", region="Berlin"),
            financial=Financial(brutto_rate=30.0, region_coefficient=1.0),
            system_settings=SystemSettings(service_type="standard")
        )

    def test_forecast_costs_basic(self, analytics_engine, base_service):
        """Test basic cost forecasting"""
        scenarios = [
            {"name": "Increase 10%", "brutto_rate_change": 10},
            {"name": "Decrease 5%", "brutto_rate_change": -5}
        ]

        result = analytics_engine.forecast_costs(base_service, scenarios)

        assert "base_service" in result
        assert "base_rate" in result
        assert "forecasts" in result
        assert len(result["forecasts"]) == 2

    def test_forecast_costs_empty_scenarios(self, analytics_engine, base_service):
        """Test forecasting with no scenarios"""
        result = analytics_engine.forecast_costs(base_service, [])

        assert result["forecasts"] == []

    def test_forecast_costs_rate_change(self, analytics_engine, base_service):
        """Test forecasting with rate changes"""
        scenarios = [{"name": "Increase 20%", "brutto_rate_change": 20}]

        result = analytics_engine.forecast_costs(base_service, scenarios)

        forecast = result["forecasts"][0]
        assert forecast["scenario_name"] == "Increase 20%"
        assert "final_rate" in forecast
        assert "change_percent" in forecast

    def test_forecast_costs_region_coefficient(self, analytics_engine, base_service):
        """Test forecasting with region coefficient changes"""
        scenarios = [{"name": "Different Region", "region_coefficient": 1.2}]

        result = analytics_engine.forecast_costs(base_service, scenarios)

        assert len(result["forecasts"]) == 1

    def test_calculate_change_percent(self, analytics_engine):
        """Test change percentage calculation"""
        change = analytics_engine._calculate_change_percent(100.0, 120.0)
        assert change == 20.0

        change = analytics_engine._calculate_change_percent(100.0, 80.0)
        assert change == -20.0

    def test_calculate_change_percent_zero_base(self, analytics_engine):
        """Test change percentage with zero base"""
        change = analytics_engine._calculate_change_percent(0.0, 100.0)
        assert change == 0


# ============================================================================
# Time Series Tests
# ============================================================================


class TestTimeSeries:
    """Test time series generation functionality."""

    @pytest.fixture
    def analytics_engine(self):
        """Create AnalyticsEngine instance."""
        from src.core.analytics import AnalyticsEngine

        return AnalyticsEngine()

    @pytest.fixture
    def time_series_services(self):
        """Create services with different creation dates."""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        services = []

        # January 2024
        for i in range(3):
            services.append(
                Service(
                    id=i + 1,
                    basic_info=BasicInfo(service_name=f"Jan {i}", target_group="T", region="Berlin"),
                    financial=Financial(brutto_rate=30.0 + i * 5),
                    system_settings=SystemSettings(service_type="standard"),
                    created_at=datetime(2024, 1, 15 + i)
                )
            )

        # February 2024
        for i in range(2):
            services.append(
                Service(
                    id=i + 4,
                    basic_info=BasicInfo(service_name=f"Feb {i}", target_group="T", region="Munich"),
                    financial=Financial(brutto_rate=35.0 + i * 5),
                    system_settings=SystemSettings(service_type="standard"),
                    created_at=datetime(2024, 2, 10 + i)
                )
            )

        return services

    def test_generate_time_series_by_month(self, analytics_engine, time_series_services):
        """Test time series generation grouped by month"""
        result = analytics_engine.generate_time_series(time_series_services, group_by="month")

        assert "2024-01" in result
        assert "2024-02" in result
        assert result["2024-01"]["count"] == 3
        assert result["2024-02"]["count"] == 2

    def test_generate_time_series_by_week(self, analytics_engine, time_series_services):
        """Test time series generation grouped by week"""
        result = analytics_engine.generate_time_series(time_series_services, group_by="week")

        # Should have week-based keys like "2024-W03"
        assert len(result) > 0
        assert any(key.startswith("2024-W") for key in result.keys())

    def test_generate_time_series_by_day(self, analytics_engine, time_series_services):
        """Test time series generation grouped by day"""
        result = analytics_engine.generate_time_series(time_series_services, group_by="day")

        # Should have day-based keys like "2024-01-15"
        assert len(result) > 0
        assert any("2024-01" in key for key in result.keys())

    def test_generate_time_series_avg_rate(self, analytics_engine, time_series_services):
        """Test average rate calculation in time series"""
        result = analytics_engine.generate_time_series(time_series_services, group_by="month")

        # Check that avg_rate is calculated
        for period_data in result.values():
            assert "avg_rate" in period_data
            assert period_data["avg_rate"] >= 0

    def test_generate_time_series_sorted(self, analytics_engine, time_series_services):
        """Test that time series is sorted by period"""
        result = analytics_engine.generate_time_series(time_series_services, group_by="month")

        keys = list(result.keys())
        # Should be sorted chronologically
        assert keys == sorted(keys)

    def test_generate_time_series_empty(self, analytics_engine):
        """Test time series with no services"""
        result = analytics_engine.generate_time_series([], group_by="month")

        assert result == {}

    def test_generate_time_series_no_created_dates(self, analytics_engine):
        """Test time series with services without created_at"""
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="Test", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=30.0),
                system_settings=SystemSettings(service_type="standard"),
                created_at=None
            )
        ]

        result = analytics_engine.generate_time_series(services, group_by="month")

        # Should handle gracefully
        assert isinstance(result, dict)


# ============================================================================
# Integration Tests
# ============================================================================


class TestAnalyticsIntegration:
    """Integration tests for analytics system."""

    def test_full_analytics_workflow(self):
        """Test complete analytics workflow"""
        from src.core.analytics import AnalyticsEngine
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        analytics = AnalyticsEngine()

        # Create diverse set of services
        services = []
        regions = ["Berlin", "Munich", "Hamburg"]
        types = ["standard", "premium"]

        for i in range(10):
            services.append(
                Service(
                    id=i + 1,
                    basic_info=BasicInfo(
                        service_name=f"Service {i}",
                        target_group="Elderly",
                        region=regions[i % 3]
                    ),
                    financial=Financial(
                        brutto_rate=25.0 + i * 3.0,
                        region_coefficient=1.0
                    ),
                    system_settings=SystemSettings(
                        service_type=types[i % 2],
                        use_umlages=(i % 2 == 0)
                    ),
                    created_at=datetime(2024, 1, 1) + timedelta(days=i * 5)
                )
            )

        # Run analysis
        report = analytics.analyze_services(services)

        assert report["total_services"] == 10
        assert len(report["by_region"]) == 3
        assert len(report["by_type"]) == 2
        assert "financial_stats" in report
        assert "recommendations" in report

    def test_comparison_and_forecasting_workflow(self):
        """Test comparison and forecasting together"""
        from src.core.analytics import AnalyticsEngine
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        analytics = AnalyticsEngine()

        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="Service A", target_group="T", region="Berlin"),
                financial=Financial(brutto_rate=30.0),
                system_settings=SystemSettings(service_type="standard")
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="Service B", target_group="T", region="Munich"),
                financial=Financial(brutto_rate=40.0),
                system_settings=SystemSettings(service_type="premium")
            )
        ]

        # Compare services
        comparison = analytics.compare_services([1, 2], services)
        assert len(comparison["services"]) == 2

        # Forecast for first service
        scenarios = [
            {"name": "Optimistic", "brutto_rate_change": 10},
            {"name": "Pessimistic", "brutto_rate_change": -5}
        ]
        forecast = analytics.forecast_costs(services[0], scenarios)
        assert len(forecast["forecasts"]) == 2

    def test_time_series_analysis_workflow(self):
        """Test time series analysis workflow"""
        from src.core.analytics import AnalyticsEngine
        from src.models.service import Service, BasicInfo, Financial, SystemSettings

        analytics = AnalyticsEngine()

        # Create services over 3 months
        services = []
        for month in range(1, 4):
            for day in range(1, 6):
                services.append(
                    Service(
                        id=len(services) + 1,
                        basic_info=BasicInfo(
                            service_name=f"Service M{month}D{day}",
                            target_group="T",
                            region="Berlin"
                        ),
                        financial=Financial(brutto_rate=30.0 + month * 2),
                        system_settings=SystemSettings(service_type="standard"),
                        created_at=datetime(2024, month, day)
                    )
                )

        # Generate time series
        monthly = analytics.generate_time_series(services, group_by="month")
        assert len(monthly) == 3
        assert all(data["count"] == 5 for data in monthly.values())

        # Analyze all services
        report = analytics.analyze_services(services)
        assert report["total_services"] == 15
