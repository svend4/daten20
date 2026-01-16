"""
Tests for Advanced Analytics Module
"""

import statistics
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

from src.core.advanced_analytics import (
    AdvancedAnalytics,
    AnalyticsReport,
    AnomalyDetection,
    Forecast,
    TrendData,
    get_advanced_analytics,
)


class TestDataClasses:
    """Test data classes"""

    def test_trend_data_creation(self):
        """Test TrendData creation"""
        trend = TrendData(period="2024-01", value=100.0, change=10.0, change_percent=11.1, trend="up")
        assert trend.period == "2024-01"
        assert trend.value == 100.0
        assert trend.change == 10.0
        assert trend.change_percent == 11.1
        assert trend.trend == "up"

    def test_forecast_creation(self):
        """Test Forecast creation"""
        forecast = Forecast(
            period="2024-02",
            predicted_value=105.0,
            confidence_interval_low=95.0,
            confidence_interval_high=115.0,
            confidence_level=0.95,
        )
        assert forecast.period == "2024-02"
        assert forecast.predicted_value == 105.0
        assert forecast.confidence_interval_low == 95.0
        assert forecast.confidence_interval_high == 115.0
        assert forecast.confidence_level == 0.95

    def test_anomaly_detection_creation(self):
        """Test AnomalyDetection creation"""
        anomaly = AnomalyDetection(
            date=datetime(2024, 1, 1),
            value=200.0,
            expected_value=50.0,
            deviation=150.0,
            is_anomaly=True,
            severity="high",
        )
        assert anomaly.date == datetime(2024, 1, 1)
        assert anomaly.value == 200.0
        assert anomaly.expected_value == 50.0
        assert anomaly.deviation == 150.0
        assert anomaly.is_anomaly is True
        assert anomaly.severity == "high"

    def test_analytics_report_creation(self):
        """Test AnalyticsReport creation"""
        report = AnalyticsReport(
            summary={"total": 100},
            trends=[],
            forecasts=[],
            anomalies=[],
            insights=["Insight 1"],
            recommendations=["Recommendation 1"],
        )
        assert report.summary == {"total": 100}
        assert report.insights == ["Insight 1"]
        assert report.recommendations == ["Recommendation 1"]


class TestAdvancedAnalytics:
    """Test AdvancedAnalytics class"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = Mock()
        db.conn = Mock()
        return db

    @pytest.fixture
    def analytics(self, mock_db):
        """Create AdvancedAnalytics instance"""
        return AdvancedAnalytics(mock_db)

    @pytest.fixture
    def sample_services(self):
        """Sample services data spanning multiple months with varying counts"""
        base_date = datetime(2024, 1, 1)
        services = []

        # Create services across 4 months with varying counts (8, 10, 11, 13)
        monthly_counts = [8, 10, 11, 13]
        service_id = 0

        for month, count in enumerate(monthly_counts):
            for day in range(count):
                service_id += 1
                date = base_date.replace(month=month + 1, day=day + 1)
                services.append(
                    {
                        "id": service_id,
                        "service_name": f"Service {service_id}",
                        "region": "EU" if service_id % 2 == 0 else "US",
                        "brutto_rate": 35.0 + (service_id % 30),  # Rates from 35 to 64
                        "hours_per_month": 160 + (service_id % 20),  # Hours from 160 to 179
                        "created_at": date.isoformat(),
                        "updated_at": date.isoformat(),
                    }
                )

        return services

    def test_init(self, mock_db):
        """Test initialization"""
        analytics = AdvancedAnalytics(mock_db)
        assert analytics.db == mock_db

    def test_generate_report_with_defaults(self, analytics, mock_db, sample_services):
        """Test generate_report with default dates"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        report = analytics.generate_report()

        assert isinstance(report, AnalyticsReport)
        assert report.summary is not None
        assert len(report.insights) > 0
        assert len(report.recommendations) > 0

    def test_generate_report_with_custom_dates(self, analytics, mock_db, sample_services):
        """Test generate_report with custom dates"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        report = analytics.generate_report(start_date, end_date)

        assert isinstance(report, AnalyticsReport)
        mock_db.conn.cursor.assert_called_once()

    def test_get_services_data(self, analytics, mock_db, sample_services):
        """Test _get_services_data"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        services = analytics._get_services_data(start_date, end_date)

        assert len(services) == 42  # 8+10+11+13 services across 4 months
        assert services[0]["service_name"] == "Service 1"
        cursor.execute.assert_called_once()

    def test_calculate_summary_empty(self, analytics):
        """Test _calculate_summary with empty data"""
        summary = analytics._calculate_summary([])

        assert summary["total_services"] == 0
        assert summary["avg_rate"] == 0
        assert summary["median_rate"] == 0
        assert summary["avg_hours"] == 0
        assert summary["total_monthly_cost"] == 0

    def test_calculate_summary_with_data(self, analytics, sample_services):
        """Test _calculate_summary with data"""
        summary = analytics._calculate_summary(sample_services)

        assert summary["total_services"] == 42
        assert summary["avg_rate"] > 0
        assert summary["median_rate"] > 0
        assert summary["avg_hours"] > 0
        assert summary["total_monthly_cost"] > 0
        assert "EU" in summary["services_by_region"]
        assert "US" in summary["services_by_region"]
        assert summary["services_by_region"]["EU"] == 21
        assert summary["services_by_region"]["US"] == 21

    def test_calculate_summary_rate_distribution(self, analytics, sample_services):
        """Test rate distribution calculation"""
        summary = analytics._calculate_summary(sample_services)

        rate_dist = summary["rate_distribution"]
        assert "0-30" in rate_dist
        assert "30-40" in rate_dist
        assert "40-50" in rate_dist
        assert "50-60" in rate_dist
        assert "60+" in rate_dist
        assert sum(rate_dist.values()) == 42

    def test_calculate_summary_single_service(self, analytics):
        """Test _calculate_summary with single service"""
        services = [{"brutto_rate": 50.0, "hours_per_month": 160, "region": "EU"}]

        summary = analytics._calculate_summary(services)

        assert summary["total_services"] == 1
        assert summary["avg_rate"] == 50.0
        assert summary["median_rate"] == 50.0
        assert summary["std_dev_rate"] == 0  # Single value has no std dev
        assert summary["total_monthly_cost"] == 8000.0

    def test_analyze_trends_empty(self, analytics):
        """Test _analyze_trends with empty data"""
        trends = analytics._analyze_trends([])
        assert len(trends) == 0

    def test_analyze_trends_with_data(self, analytics, sample_services):
        """Test _analyze_trends with data"""
        trends = analytics._analyze_trends(sample_services)

        assert len(trends) > 0
        assert all(isinstance(t, TrendData) for t in trends)

        # First month should have stable trend (no previous data)
        assert trends[0].trend == "stable"
        assert trends[0].change == 0

    def test_analyze_trends_upward(self, analytics):
        """Test upward trend detection"""
        base_date = datetime(2024, 1, 1)
        services = []

        # Create data with increasing trend
        for month in range(3):
            count = (month + 1) * 10  # 10, 20, 30 services per month
            for day in range(count):
                date = base_date + timedelta(days=month * 30 + day)
                services.append({"created_at": date.isoformat(), "brutto_rate": 50.0, "hours_per_month": 160})

        trends = analytics._analyze_trends(services)

        # Second and third months should show upward trend
        assert any(t.trend == "up" for t in trends[1:])

    def test_analyze_trends_downward(self, analytics):
        """Test downward trend detection"""
        base_date = datetime(2024, 1, 1)
        services = []

        # Create data with decreasing trend
        for month in range(3):
            count = (3 - month) * 10  # 30, 20, 10 services per month
            for day in range(count):
                date = base_date + timedelta(days=month * 30 + day)
                services.append({"created_at": date.isoformat(), "brutto_rate": 50.0, "hours_per_month": 160})

        trends = analytics._analyze_trends(services)

        # Should detect downward trend
        assert any(t.trend == "down" for t in trends[1:])

    def test_analyze_trends_invalid_dates(self, analytics):
        """Test _analyze_trends with invalid dates"""
        services = [{"created_at": "invalid-date"}, {"created_at": None}, {}]

        trends = analytics._analyze_trends(services)
        assert len(trends) == 0

    def test_generate_forecasts_insufficient_data(self, analytics):
        """Test _generate_forecasts with insufficient data"""
        services = [{"created_at": datetime(2024, 1, 1).isoformat()}, {"created_at": datetime(2024, 1, 2).isoformat()}]

        forecasts = analytics._generate_forecasts(services)
        assert len(forecasts) == 0

    def test_generate_forecasts_with_data(self, analytics, sample_services):
        """Test _generate_forecasts with sufficient data"""
        forecasts = analytics._generate_forecasts(sample_services)

        assert len(forecasts) == 3  # 3 months forecast
        assert all(isinstance(f, Forecast) for f in forecasts)
        assert all(f.predicted_value >= 0 for f in forecasts)
        assert all(f.confidence_interval_low >= 0 for f in forecasts)
        assert all(f.confidence_interval_high > f.confidence_interval_low for f in forecasts)

        # Confidence should decrease with horizon
        assert forecasts[0].confidence_level > forecasts[1].confidence_level
        assert forecasts[1].confidence_level > forecasts[2].confidence_level

    def test_generate_forecasts_linear_trend(self, analytics):
        """Test forecasting with linear trend"""
        base_date = datetime(2024, 1, 1)
        services = []

        # Create data with clear linear trend
        for month in range(6):
            count = 10 + month * 5  # 10, 15, 20, 25, 30, 35
            for i in range(count):
                date = base_date.replace(month=month + 1)
                services.append({"created_at": date.isoformat(), "brutto_rate": 50.0})

        forecasts = analytics._generate_forecasts(services)

        assert len(forecasts) == 3
        # Forecasts should follow increasing trend
        assert forecasts[0].predicted_value > 35

    def test_generate_forecasts_invalid_dates(self, analytics):
        """Test _generate_forecasts with invalid dates"""
        services = [{"created_at": "invalid"}, {"created_at": None}, {}] * 5

        forecasts = analytics._generate_forecasts(services)
        assert len(forecasts) == 0

    def test_detect_anomalies_insufficient_data(self, analytics):
        """Test _detect_anomalies with insufficient data"""
        services = [{"brutto_rate": 50.0, "created_at": datetime(2024, 1, i).isoformat()} for i in range(1, 6)]

        anomalies = analytics._detect_anomalies(services)
        assert len(anomalies) == 0

    def test_detect_anomalies_with_outliers(self, analytics):
        """Test anomaly detection with outliers"""
        base_date = datetime(2024, 1, 1)
        services = []

        # Normal values around 50
        for i in range(50):
            services.append({"brutto_rate": 50.0 + (i % 5), "created_at": (base_date + timedelta(days=i)).isoformat()})

        # Add clear outliers
        services.append(
            {"brutto_rate": 150.0, "created_at": (base_date + timedelta(days=50)).isoformat()}  # Way above normal
        )
        services.append(
            {"brutto_rate": 200.0, "created_at": (base_date + timedelta(days=51)).isoformat()}  # Even higher
        )

        anomalies = analytics._detect_anomalies(services)

        assert len(anomalies) > 0
        assert all(isinstance(a, AnomalyDetection) for a in anomalies)
        assert all(a.is_anomaly for a in anomalies)
        assert any(a.severity == "high" for a in anomalies)

    def test_detect_anomalies_severity_levels(self, analytics):
        """Test anomaly severity classification"""
        base_date = datetime(2024, 1, 1)
        services = []

        # Create data with known mean and std dev
        mean = 50.0
        std_dev = 10.0

        for i in range(50):
            services.append({"brutto_rate": mean, "created_at": (base_date + timedelta(days=i)).isoformat()})

        # Add anomalies with different z-scores
        services.append(
            {
                "brutto_rate": mean + 2.6 * std_dev,  # z > 2.5: medium
                "created_at": (base_date + timedelta(days=50)).isoformat(),
            }
        )
        services.append(
            {
                "brutto_rate": mean + 3.5 * std_dev,  # z > 3: high
                "created_at": (base_date + timedelta(days=51)).isoformat(),
            }
        )

        anomalies = analytics._detect_anomalies(services)

        assert len(anomalies) >= 2
        severities = {a.severity for a in anomalies}
        assert "medium" in severities or "high" in severities

    def test_detect_anomalies_invalid_data(self, analytics):
        """Test anomaly detection with invalid data"""
        services = [
            {"brutto_rate": None, "created_at": "invalid"},
            {},
            {"created_at": datetime(2024, 1, 1).isoformat()},
        ] * 5

        anomalies = analytics._detect_anomalies(services)
        assert len(anomalies) == 0

    def test_generate_insights_empty(self, analytics):
        """Test _generate_insights with empty summary"""
        summary = {
            "total_services": 0,
            "avg_rate": 0,
            "median_rate": 0,
            "services_by_region": {},
            "total_monthly_cost": 0,
        }

        insights = analytics._generate_insights(summary, [], [])

        assert len(insights) > 0
        assert any("0" in insight for insight in insights)

    def test_generate_insights_with_data(self, analytics, sample_services):
        """Test _generate_insights with data"""
        summary = analytics._calculate_summary(sample_services)
        trends = analytics._analyze_trends(sample_services)
        anomalies = []

        insights = analytics._generate_insights(summary, trends, anomalies)

        assert len(insights) > 0
        assert any("услуг" in insight.lower() for insight in insights)
        assert any("ставка" in insight.lower() for insight in insights)

    def test_generate_insights_upward_trend(self, analytics):
        """Test insights generation for upward trend"""
        summary = {"total_services": 100, "avg_rate": 50.0, "median_rate": 50.0}
        trends = [TrendData(period="2024-01", value=100, change=10, change_percent=11.0, trend="up")]

        insights = analytics._generate_insights(summary, trends, [])

        assert any("📈" in insight for insight in insights)
        assert any("выросло" in insight.lower() for insight in insights)

    def test_generate_insights_downward_trend(self, analytics):
        """Test insights generation for downward trend"""
        summary = {"total_services": 100, "avg_rate": 50.0, "median_rate": 50.0}
        trends = [TrendData(period="2024-01", value=90, change=-10, change_percent=-10.0, trend="down")]

        insights = analytics._generate_insights(summary, trends, [])

        assert any("📉" in insight for insight in insights)
        assert any("снизилось" in insight.lower() for insight in insights)

    def test_generate_insights_anomalies(self, analytics):
        """Test insights generation with anomalies"""
        summary = {"total_services": 100}
        anomalies = [
            AnomalyDetection(
                date=datetime(2024, 1, 1),
                value=200.0,
                expected_value=50.0,
                deviation=150.0,
                is_anomaly=True,
                severity="high",
            )
        ]

        insights = analytics._generate_insights(summary, [], anomalies)

        assert any("⚠️" in insight for insight in insights)
        assert any("аномальных" in insight.lower() for insight in insights)

    def test_generate_insights_regional(self, analytics):
        """Test insights generation with regional data"""
        summary = {
            "total_services": 100,
            "avg_rate": 50.0,
            "median_rate": 50.0,
            "services_by_region": {"EU": 60, "US": 40},
        }

        insights = analytics._generate_insights(summary, [], [])

        assert any("🏆" in insight for insight in insights)
        assert any("EU" in insight for insight in insights)

    def test_generate_recommendations_empty(self, analytics):
        """Test _generate_recommendations with minimal data"""
        summary = {"total_services": 0}

        recommendations = analytics._generate_recommendations(summary, [], [])

        assert isinstance(recommendations, list)

    def test_generate_recommendations_high_variability(self, analytics):
        """Test recommendation for high rate variability"""
        summary = {"total_services": 100, "avg_rate": 50.0, "std_dev_rate": 20.0}  # 40% of mean

        recommendations = analytics._generate_recommendations(summary, [], [])

        assert any("стандартизацию" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_declining_trend(self, analytics):
        """Test recommendation for declining trend"""
        summary = {"total_services": 100}
        trends = [
            TrendData(period="2024-01", value=100, change=-5, change_percent=-5.0, trend="down"),
            TrendData(period="2024-02", value=95, change=-5, change_percent=-5.3, trend="down"),
            TrendData(period="2024-03", value=90, change=-5, change_percent=-5.6, trend="down"),
        ]

        recommendations = analytics._generate_recommendations(summary, trends, [])

        assert any("снижение" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_negative_forecast(self, analytics):
        """Test recommendation for negative forecast"""
        summary = {"total_services": 100}
        forecasts = [
            Forecast(
                period="2024-02",
                predicted_value=80.0,  # Below 90% of current
                confidence_interval_low=70.0,
                confidence_interval_high=90.0,
                confidence_level=0.95,
            )
        ]

        recommendations = analytics._generate_recommendations(summary, [], forecasts)

        assert any("прогноз" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_limited_regions(self, analytics):
        """Test recommendation for limited regional coverage"""
        summary = {"total_services": 100, "services_by_region": {"EU": 100}}  # Only one region

        recommendations = analytics._generate_recommendations(summary, [], [])

        assert any("географического" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_low_hours(self, analytics):
        """Test recommendation for low average hours"""
        summary = {"total_services": 100, "avg_hours": 80.0}  # Below 100

        recommendations = analytics._generate_recommendations(summary, [], [])

        assert any("продолжительность" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_high_hours(self, analytics):
        """Test recommendation for high average hours"""
        summary = {"total_services": 100, "avg_hours": 200.0}  # Above 180

        recommendations = analytics._generate_recommendations(summary, [], [])

        assert any("продолжительность" in rec.lower() for rec in recommendations)


def test_get_advanced_analytics():
    """Test factory function"""
    mock_db = Mock()
    analytics = get_advanced_analytics(mock_db)

    assert isinstance(analytics, AdvancedAnalytics)
    assert analytics.db == mock_db


def test_integration_full_report():
    """Integration test for full report generation"""
    # Setup mock database
    mock_db = Mock()
    mock_db.conn = Mock()
    cursor = MagicMock()
    cursor.description = [
        ("id",),
        ("service_name",),
        ("region",),
        ("brutto_rate",),
        ("hours_per_month",),
        ("created_at",),
        ("updated_at",),
    ]

    # Create realistic data spanning multiple months
    base_date = datetime(2024, 1, 1)
    rows = []
    for month in range(4):  # 4 months of data
        for day in range(25):  # 25 services per month
            i = month * 25 + day
            date = base_date.replace(month=month + 1, day=day + 1)
            rows.append(
                (
                    i + 1,
                    f"Service {i + 1}",
                    "EU" if i % 3 == 0 else "US" if i % 3 == 1 else "APAC",
                    45.0 + (i % 20),
                    160 + (i % 40),
                    date.isoformat(),
                    date.isoformat(),
                )
            )

    cursor.fetchall.return_value = rows
    mock_db.conn.cursor.return_value = cursor

    # Generate report
    analytics = AdvancedAnalytics(mock_db)
    report = analytics.generate_report(base_date, base_date + timedelta(days=120))

    # Verify report structure
    assert isinstance(report, AnalyticsReport)
    assert report.summary["total_services"] == 100
    assert len(report.trends) > 0
    assert len(report.forecasts) > 0
    assert len(report.insights) > 0
    assert len(report.recommendations) > 0

    # Verify data quality
    assert report.summary["avg_rate"] > 0
    assert report.summary["total_monthly_cost"] > 0
    assert len(report.summary["services_by_region"]) == 3
