"""
Unit Tests for BI Dashboard Module

Tests for Business Intelligence Dashboard functionality including:
- KPI calculations
- Dashboard building
- Report generation
- Data visualization
"""

import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

from src.analytics.bi_dashboard import (
    KPI,
    BIDashboard,
    ChartData,
    ChartType,
    DashboardBuilder,
    KPICalculator,
    ReportFormat,
    ReportFrequency,
    ReportGenerator,
    ReportScheduler,
)


class TestKPICalculator(unittest.TestCase):
    """Test KPI calculation methods"""

    def setUp(self):
        self.calculator = KPICalculator()

    def test_calculate_mrr_monthly_subscriptions(self):
        """Test MRR calculation with monthly subscriptions"""
        subscriptions = [
            {"status": "active", "billing_cycle": "monthly", "amount": 100},
            {"status": "active", "billing_cycle": "monthly", "amount": 200},
            {"status": "active", "billing_cycle": "monthly", "amount": 150},
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal("450"))

    def test_calculate_mrr_yearly_subscriptions(self):
        """Test MRR calculation with yearly subscriptions"""
        subscriptions = [{"status": "active", "billing_cycle": "yearly", "amount": 1200}]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal("100"))  # 1200 / 12

    def test_calculate_mrr_mixed_subscriptions(self):
        """Test MRR calculation with mixed billing cycles"""
        subscriptions = [
            {"status": "active", "billing_cycle": "monthly", "amount": 100},
            {"status": "active", "billing_cycle": "yearly", "amount": 1200},
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal("200"))  # 100 + (1200/12)

    def test_calculate_mrr_excludes_inactive(self):
        """Test that inactive subscriptions are excluded from MRR"""
        subscriptions = [
            {"status": "active", "billing_cycle": "monthly", "amount": 100},
            {"status": "canceled", "billing_cycle": "monthly", "amount": 200},
            {"status": "paused", "billing_cycle": "monthly", "amount": 150},
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal("100"))

    def test_calculate_arr_from_mrr(self):
        """Test ARR calculation from MRR"""
        mrr = Decimal("1000")
        arr = self.calculator.calculate_arr(mrr)
        self.assertEqual(arr, Decimal("12000"))

    def test_calculate_churn_rate(self):
        """Test churn rate calculation"""
        churn_rate = self.calculator.calculate_churn_rate(
            churned_customers=50, total_customers_start=1000, period_days=30
        )
        self.assertEqual(churn_rate, 5.0)  # (50/1000) * 100

    def test_calculate_churn_rate_zero_customers(self):
        """Test churn rate with zero customers"""
        churn_rate = self.calculator.calculate_churn_rate(churned_customers=0, total_customers_start=0, period_days=30)
        self.assertEqual(churn_rate, 0.0)

    def test_calculate_clv(self):
        """Test Customer Lifetime Value calculation"""
        clv = self.calculator.calculate_clv(
            avg_revenue_per_user=Decimal("100"), avg_customer_lifespan_months=24, gross_margin=0.8
        )
        self.assertEqual(clv, Decimal("1920.00"))  # 100 * 24 * 0.8

    def test_calculate_nrr(self):
        """Test Net Revenue Retention calculation"""
        nrr = self.calculator.calculate_nrr(
            revenue_start=Decimal("10000"), expansion_revenue=Decimal("2000"), churned_revenue=Decimal("1000")
        )
        self.assertEqual(nrr, 110.0)  # ((10000 + 2000 - 1000) / 10000) * 100

    def test_calculate_nrr_zero_start_revenue(self):
        """Test NRR with zero starting revenue"""
        nrr = self.calculator.calculate_nrr(
            revenue_start=Decimal("0"), expansion_revenue=Decimal("1000"), churned_revenue=Decimal("0")
        )
        self.assertEqual(nrr, 0.0)

    def test_calculate_cac(self):
        """Test Customer Acquisition Cost calculation"""
        cac = self.calculator.calculate_cac(sales_marketing_costs=Decimal("50000"), new_customers=100)
        self.assertEqual(cac, Decimal("500.00"))

    def test_calculate_cac_zero_customers(self):
        """Test CAC with zero new customers"""
        cac = self.calculator.calculate_cac(sales_marketing_costs=Decimal("50000"), new_customers=0)
        self.assertEqual(cac, Decimal("0"))

    def test_calculate_arpu(self):
        """Test Average Revenue Per User calculation"""
        arpu = self.calculator.calculate_arpu(total_revenue=Decimal("100000"), total_users=1000)
        self.assertEqual(arpu, Decimal("100.00"))

    def test_calculate_arpu_zero_users(self):
        """Test ARPU with zero users"""
        arpu = self.calculator.calculate_arpu(total_revenue=Decimal("100000"), total_users=0)
        self.assertEqual(arpu, Decimal("0"))


class TestDashboardBuilder(unittest.TestCase):
    """Test Dashboard Builder functionality"""

    def setUp(self):
        self.builder = DashboardBuilder()

    def test_add_kpi_widget(self):
        """Test adding KPI widget to dashboard"""
        kpi = KPI(name="Test KPI", value=100.0, unit="EUR", change_percentage=5.0, trend="up")

        self.builder.add_kpi_widget(kpi=kpi, position={"row": 0, "col": 0}, size={"width": 3, "height": 2})

        self.assertEqual(len(self.builder.widgets), 1)
        self.assertEqual(self.builder.widgets[0]["type"], "kpi")
        self.assertEqual(self.builder.widgets[0]["kpi"].name, "Test KPI")

    def test_add_chart_widget(self):
        """Test adding chart widget to dashboard"""
        chart = ChartData(
            chart_type=ChartType.LINE,
            title="Test Chart",
            data={},
            labels=["A", "B", "C"],
            datasets=[{"label": "Data", "data": [1, 2, 3]}],
        )

        self.builder.add_chart_widget(chart=chart, position={"row": 1, "col": 0}, size={"width": 6, "height": 4})

        self.assertEqual(len(self.builder.widgets), 1)
        self.assertEqual(self.builder.widgets[0]["type"], "chart")
        self.assertEqual(self.builder.widgets[0]["chart"].title, "Test Chart")

    def test_build_dashboard(self):
        """Test building complete dashboard configuration"""
        kpi = KPI(name="MRR", value=1000.0, unit="EUR", change_percentage=5.0, trend="up")

        self.builder.add_kpi_widget(kpi, {"row": 0, "col": 0}, {"width": 3, "height": 2})

        dashboard_config = self.builder.build()

        self.assertIn("widgets", dashboard_config)
        self.assertIn("layout", dashboard_config)
        self.assertIn("created_at", dashboard_config)
        self.assertEqual(len(dashboard_config["widgets"]), 1)


class TestReportGenerator(unittest.TestCase):
    """Test Report Generator functionality"""

    def setUp(self):
        self.generator = ReportGenerator()
        from src.analytics.bi_dashboard import Report

        self.test_report = Report(
            id="test-report-123",
            name="Test Report",
            description="Test Description",
            kpis=[
                KPI("MRR", 1000.0, "EUR", 5.0, "up"),
                KPI("ARR", 12000.0, "EUR", 5.0, "up")
            ],
            charts=[],
            filters={},
            created_at=datetime.now(),
            created_by="test_user",
            format=ReportFormat.PDF
        )

    def test_generate_report_pdf(self):
        """Test PDF report generation"""
        result = self.generator.generate_pdf(self.test_report)

        # PDF should be bytes
        self.assertIsInstance(result, bytes)
        # PDF should have content
        self.assertGreater(len(result), 0)
        # PDF should start with PDF header
        self.assertTrue(result.startswith(b'%PDF'))

    def test_generate_report_excel(self):
        """Test Excel report generation"""
        result = self.generator.generate_excel(self.test_report)

        # Excel should be bytes
        self.assertIsInstance(result, bytes)
        # Excel should have content
        self.assertGreater(len(result), 0)

    def test_generate_report_json(self):
        """Test JSON report generation"""
        result = self.generator.generate_json(self.test_report)

        # JSON generation should work without mocking
        self.assertIsInstance(result, str)
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        self.assertEqual(parsed["id"], "test-report-123")
        self.assertEqual(parsed["name"], "Test Report")

    def test_generate_report_powerpoint(self):
        """Test PowerPoint report generation"""
        result = self.generator.generate_powerpoint(self.test_report)

        # PowerPoint should be bytes
        self.assertIsInstance(result, bytes)
        # PowerPoint should have content
        self.assertGreater(len(result), 0)
        # PowerPoint files start with PK (ZIP format)
        self.assertTrue(result.startswith(b'PK'))

    def test_generate_report_csv(self):
        """Test CSV report generation"""
        result = self.generator.generate_csv(self.test_report)

        # CSV should be string
        self.assertIsInstance(result, str)
        # Should contain header
        self.assertIn("KPI,Value,Unit", result)
        # Should contain KPI data
        self.assertIn("MRR", result)
        self.assertIn("ARR", result)


class TestReportScheduler(unittest.TestCase):
    """Test Report Scheduler functionality"""

    def setUp(self):
        self.dashboard = Mock()
        self.scheduler = ReportScheduler(parent_dashboard=self.dashboard)
        from src.analytics.bi_dashboard import ScheduledReport

        self.test_scheduled_report = ScheduledReport(
            id="test-scheduled-123",
            report_id="report-456",
            name="Weekly Report",
            frequency=ReportFrequency.WEEKLY,
            recipients=["user@example.com"],
            format=ReportFormat.PDF,
            filters={},
            enabled=True
        )

    def test_schedule_report(self):
        """Test scheduling a new report"""
        self.scheduler.schedule_report(self.test_scheduled_report)

        self.assertIn(self.test_scheduled_report.id, self.scheduler.scheduled_reports)
        scheduled = self.scheduler.scheduled_reports[self.test_scheduled_report.id]
        self.assertEqual(scheduled.name, "Weekly Report")
        self.assertIsNotNone(scheduled.next_run)

    def test_unschedule_report(self):
        """Test unscheduling a report"""
        self.scheduler.schedule_report(self.test_scheduled_report)
        self.assertIn(self.test_scheduled_report.id, self.scheduler.scheduled_reports)

        self.scheduler.unschedule_report(self.test_scheduled_report.id)
        self.assertNotIn(self.test_scheduled_report.id, self.scheduler.scheduled_reports)

    def test_calculate_next_run_daily(self):
        """Test next run calculation for daily frequency"""
        next_run = self.scheduler._calculate_next_run(ReportFrequency.DAILY)
        expected = datetime.now() + timedelta(days=1)

        # Check if next run is approximately tomorrow
        self.assertAlmostEqual(next_run.timestamp(), expected.timestamp(), delta=60)  # Within 1 minute

    def test_calculate_next_run_weekly(self):
        """Test next run calculation for weekly frequency"""
        next_run = self.scheduler._calculate_next_run(ReportFrequency.WEEKLY)
        expected = datetime.now() + timedelta(weeks=1)

        self.assertAlmostEqual(next_run.timestamp(), expected.timestamp(), delta=3600)  # Within 1 hour

    def test_list_scheduled_reports(self):
        """Test listing all scheduled reports"""
        from src.analytics.bi_dashboard import ScheduledReport

        report1 = ScheduledReport(
            id="report-1",
            report_id="r1",
            name="Report 1",
            frequency=ReportFrequency.DAILY,
            recipients=[],
            format=ReportFormat.PDF,
            filters={}
        )
        report2 = ScheduledReport(
            id="report-2",
            report_id="r2",
            name="Report 2",
            frequency=ReportFrequency.WEEKLY,
            recipients=[],
            format=ReportFormat.EXCEL,
            filters={}
        )

        self.scheduler.schedule_report(report1)
        self.scheduler.schedule_report(report2)

        reports = self.scheduler.scheduled_reports

        self.assertEqual(len(reports), 2)
        self.assertIn("report-1", reports)
        self.assertIn("report-2", reports)

    def test_get_execution_history(self):
        """Test getting execution history"""
        # Initially empty
        history = self.scheduler.get_execution_history()
        self.assertEqual(len(history), 0)

        # Add some executions manually for testing
        self.scheduler.execution_history.append({
            "report_id": "test-report",
            "executed_at": datetime.now(),
            "status": "success"
        })

        history = self.scheduler.get_execution_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["status"], "success")

    def test_get_execution_history_with_filter(self):
        """Test getting execution history with report filter"""
        # Add multiple executions
        self.scheduler.execution_history.append({
            "report_id": "report-1",
            "executed_at": datetime.now(),
            "status": "success"
        })
        self.scheduler.execution_history.append({
            "report_id": "report-2",
            "executed_at": datetime.now(),
            "status": "failed"
        })

        # Filter by report ID
        history = self.scheduler.get_execution_history(report_id="report-1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["report_id"], "report-1")

    def test_calculate_next_run_monthly(self):
        """Test next run calculation for monthly frequency"""
        next_run = self.scheduler._calculate_next_run(ReportFrequency.MONTHLY)
        expected = datetime.now() + timedelta(days=30)

        # Should be approximately 30 days from now
        delta_seconds = abs((next_run - expected).total_seconds())
        self.assertLess(delta_seconds, 3600)  # Within 1 hour

    def test_calculate_next_run_quarterly(self):
        """Test next run calculation for quarterly frequency"""
        next_run = self.scheduler._calculate_next_run(ReportFrequency.QUARTERLY)
        expected = datetime.now() + timedelta(days=90)

        # Should be approximately 90 days from now
        delta_seconds = abs((next_run - expected).total_seconds())
        self.assertLess(delta_seconds, 7200)  # Within 2 hours


class TestBIDashboard(unittest.TestCase):
    """Test main BIDashboard class"""

    def setUp(self):
        self.dashboard = BIDashboard()

    @patch.object(BIDashboard, "_fetch_subscriptions")
    def test_create_executive_dashboard(self, mock_fetch):
        """Test creating executive dashboard"""
        mock_fetch.return_value = [{"status": "active", "billing_cycle": "monthly", "amount": 1000}]

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        dashboard_config = self.dashboard.create_executive_dashboard(
            tenant_id="test_tenant", date_range=(start_date, end_date)
        )

        self.assertIsInstance(dashboard_config, dict)
        # Check for expected keys
        # Actual implementation may vary

    def test_dashboard_has_required_components(self):
        """Test that dashboard has all required components"""
        self.assertIsNotNone(self.dashboard.kpi_calculator)
        self.assertIsNotNone(self.dashboard.dashboard_builder)
        self.assertIsNotNone(self.dashboard.report_generator)
        self.assertIsNotNone(self.dashboard.report_scheduler)

    def test_create_custom_report(self):
        """Test creating custom report"""
        kpis = [KPI("Test KPI", 100.0, "EUR", 5.0, "up")]
        charts = []

        report = self.dashboard.create_custom_report(
            name="Custom Report",
            description="Test Description",
            kpis=kpis,
            charts=charts,
            filters={},
            created_by="test_user"
        )

        self.assertIsNotNone(report.id)
        self.assertEqual(report.name, "Custom Report")
        self.assertIn(report.id, self.dashboard.reports)

    def test_export_report_pdf(self):
        """Test exporting report as PDF"""
        kpis = [KPI("Test", 100.0, "EUR", 5.0, "up")]
        report = self.dashboard.create_custom_report(
            name="Test Report",
            description="Test",
            kpis=kpis,
            charts=[],
            filters={},
            created_by="test_user"
        )

        pdf_data = self.dashboard.export_report(report.id, ReportFormat.PDF)

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b'%PDF'))

    def test_export_report_excel(self):
        """Test exporting report as Excel"""
        kpis = [KPI("Test", 100.0, "EUR", 5.0, "up")]
        report = self.dashboard.create_custom_report(
            name="Test Report",
            description="Test",
            kpis=kpis,
            charts=[],
            filters={},
            created_by="test_user"
        )

        excel_data = self.dashboard.export_report(report.id, ReportFormat.EXCEL)

        self.assertIsInstance(excel_data, bytes)
        self.assertGreater(len(excel_data), 0)

    def test_schedule_report(self):
        """Test scheduling a report"""
        kpis = [KPI("Test", 100.0, "EUR", 5.0, "up")]
        report = self.dashboard.create_custom_report(
            name="Test Report",
            description="Test",
            kpis=kpis,
            charts=[],
            filters={},
            created_by="test_user"
        )

        scheduled = self.dashboard.schedule_report(
            report_id=report.id,
            name="Weekly Scheduled Report",
            frequency=ReportFrequency.WEEKLY,
            recipients=["user@example.com"],
            format=ReportFormat.PDF,
            filters={}
        )

        self.assertIsNotNone(scheduled.id)
        self.assertEqual(scheduled.name, "Weekly Scheduled Report")
        self.assertIn(scheduled.id, self.dashboard.report_scheduler.scheduled_reports)


class TestChartData(unittest.TestCase):
    """Test ChartData dataclass"""

    def test_create_chart_data(self):
        """Test creating ChartData instance"""
        chart = ChartData(
            chart_type=ChartType.LINE,
            title="Test Chart",
            data={"test": "data"},
            labels=["A", "B", "C"],
            datasets=[{"label": "Data", "data": [1, 2, 3]}],
            options={"responsive": True},
        )

        self.assertEqual(chart.chart_type, ChartType.LINE)
        self.assertEqual(chart.title, "Test Chart")
        self.assertEqual(len(chart.labels), 3)
        self.assertEqual(len(chart.datasets), 1)
        self.assertTrue(chart.options["responsive"])


class TestKPIDataclass(unittest.TestCase):
    """Test KPI dataclass"""

    def test_create_kpi(self):
        """Test creating KPI instance"""
        kpi = KPI(
            name="Monthly Revenue",
            value=10000.0,
            unit="EUR",
            change_percentage=5.5,
            trend="up",
            target=12000.0,
            description="Total monthly revenue",
        )

        self.assertEqual(kpi.name, "Monthly Revenue")
        self.assertEqual(kpi.value, 10000.0)
        self.assertEqual(kpi.unit, "EUR")
        self.assertEqual(kpi.change_percentage, 5.5)
        self.assertEqual(kpi.trend, "up")
        self.assertEqual(kpi.target, 12000.0)
        self.assertIsInstance(kpi.timestamp, datetime)


if __name__ == "__main__":
    unittest.main()
