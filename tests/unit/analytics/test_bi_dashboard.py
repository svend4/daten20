"""
Unit Tests for BI Dashboard Module

Tests for Business Intelligence Dashboard functionality including:
- KPI calculations
- Dashboard building
- Report generation
- Data visualization
"""

import unittest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.analytics.bi_dashboard import (
    BIDashboard,
    KPICalculator,
    DashboardBuilder,
    ReportGenerator,
    ReportScheduler,
    KPI,
    ChartData,
    ChartType,
    ReportFormat,
    ReportFrequency
)


class TestKPICalculator(unittest.TestCase):
    """Test KPI calculation methods"""

    def setUp(self):
        self.calculator = KPICalculator()

    def test_calculate_mrr_monthly_subscriptions(self):
        """Test MRR calculation with monthly subscriptions"""
        subscriptions = [
            {'status': 'active', 'billing_cycle': 'monthly', 'amount': 100},
            {'status': 'active', 'billing_cycle': 'monthly', 'amount': 200},
            {'status': 'active', 'billing_cycle': 'monthly', 'amount': 150}
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal('450'))

    def test_calculate_mrr_yearly_subscriptions(self):
        """Test MRR calculation with yearly subscriptions"""
        subscriptions = [
            {'status': 'active', 'billing_cycle': 'yearly', 'amount': 1200}
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal('100'))  # 1200 / 12

    def test_calculate_mrr_mixed_subscriptions(self):
        """Test MRR calculation with mixed billing cycles"""
        subscriptions = [
            {'status': 'active', 'billing_cycle': 'monthly', 'amount': 100},
            {'status': 'active', 'billing_cycle': 'yearly', 'amount': 1200}
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal('200'))  # 100 + (1200/12)

    def test_calculate_mrr_excludes_inactive(self):
        """Test that inactive subscriptions are excluded from MRR"""
        subscriptions = [
            {'status': 'active', 'billing_cycle': 'monthly', 'amount': 100},
            {'status': 'canceled', 'billing_cycle': 'monthly', 'amount': 200},
            {'status': 'paused', 'billing_cycle': 'monthly', 'amount': 150}
        ]

        mrr = self.calculator.calculate_mrr(subscriptions)
        self.assertEqual(mrr, Decimal('100'))

    def test_calculate_arr_from_mrr(self):
        """Test ARR calculation from MRR"""
        mrr = Decimal('1000')
        arr = self.calculator.calculate_arr(mrr)
        self.assertEqual(arr, Decimal('12000'))

    def test_calculate_churn_rate(self):
        """Test churn rate calculation"""
        churn_rate = self.calculator.calculate_churn_rate(
            churned_customers=50,
            total_customers_start=1000,
            period_days=30
        )
        self.assertEqual(churn_rate, 5.0)  # (50/1000) * 100

    def test_calculate_churn_rate_zero_customers(self):
        """Test churn rate with zero customers"""
        churn_rate = self.calculator.calculate_churn_rate(
            churned_customers=0,
            total_customers_start=0,
            period_days=30
        )
        self.assertEqual(churn_rate, 0.0)

    def test_calculate_clv(self):
        """Test Customer Lifetime Value calculation"""
        clv = self.calculator.calculate_clv(
            avg_revenue_per_user=Decimal('100'),
            avg_customer_lifespan_months=24,
            gross_margin=0.8
        )
        self.assertEqual(clv, Decimal('1920.00'))  # 100 * 24 * 0.8

    def test_calculate_nrr(self):
        """Test Net Revenue Retention calculation"""
        nrr = self.calculator.calculate_nrr(
            revenue_start=Decimal('10000'),
            expansion_revenue=Decimal('2000'),
            churned_revenue=Decimal('1000')
        )
        self.assertEqual(nrr, 110.0)  # ((10000 + 2000 - 1000) / 10000) * 100

    def test_calculate_nrr_zero_start_revenue(self):
        """Test NRR with zero starting revenue"""
        nrr = self.calculator.calculate_nrr(
            revenue_start=Decimal('0'),
            expansion_revenue=Decimal('1000'),
            churned_revenue=Decimal('0')
        )
        self.assertEqual(nrr, 0.0)

    def test_calculate_cac(self):
        """Test Customer Acquisition Cost calculation"""
        cac = self.calculator.calculate_cac(
            sales_marketing_costs=Decimal('50000'),
            new_customers=100
        )
        self.assertEqual(cac, Decimal('500.00'))

    def test_calculate_cac_zero_customers(self):
        """Test CAC with zero new customers"""
        cac = self.calculator.calculate_cac(
            sales_marketing_costs=Decimal('50000'),
            new_customers=0
        )
        self.assertEqual(cac, Decimal('0'))

    def test_calculate_arpu(self):
        """Test Average Revenue Per User calculation"""
        arpu = self.calculator.calculate_arpu(
            total_revenue=Decimal('100000'),
            total_users=1000
        )
        self.assertEqual(arpu, Decimal('100.00'))

    def test_calculate_arpu_zero_users(self):
        """Test ARPU with zero users"""
        arpu = self.calculator.calculate_arpu(
            total_revenue=Decimal('100000'),
            total_users=0
        )
        self.assertEqual(arpu, Decimal('0'))


class TestDashboardBuilder(unittest.TestCase):
    """Test Dashboard Builder functionality"""

    def setUp(self):
        self.builder = DashboardBuilder()

    def test_add_kpi_widget(self):
        """Test adding KPI widget to dashboard"""
        kpi = KPI(
            name="Test KPI",
            value=100.0,
            unit="EUR",
            change_percentage=5.0,
            trend="up"
        )

        self.builder.add_kpi_widget(
            kpi=kpi,
            position={"row": 0, "col": 0},
            size={"width": 3, "height": 2}
        )

        self.assertEqual(len(self.builder.widgets), 1)
        self.assertEqual(self.builder.widgets[0]['type'], 'kpi')
        self.assertEqual(self.builder.widgets[0]['data']['name'], "Test KPI")

    def test_add_chart_widget(self):
        """Test adding chart widget to dashboard"""
        chart = ChartData(
            chart_type=ChartType.LINE,
            title="Test Chart",
            data={},
            labels=["A", "B", "C"],
            datasets=[{"label": "Data", "data": [1, 2, 3]}]
        )

        self.builder.add_chart_widget(
            chart=chart,
            position={"row": 1, "col": 0},
            size={"width": 6, "height": 4}
        )

        self.assertEqual(len(self.builder.widgets), 1)
        self.assertEqual(self.builder.widgets[0]['type'], 'chart')
        self.assertEqual(self.builder.widgets[0]['data'].title, "Test Chart")

    def test_build_dashboard(self):
        """Test building complete dashboard configuration"""
        kpi = KPI(
            name="MRR",
            value=1000.0,
            unit="EUR",
            change_percentage=5.0,
            trend="up"
        )

        self.builder.add_kpi_widget(kpi, {"row": 0, "col": 0}, {"width": 3, "height": 2})

        dashboard_config = self.builder.build()

        self.assertIn('widgets', dashboard_config)
        self.assertIn('layout', dashboard_config)
        self.assertIn('metadata', dashboard_config)
        self.assertEqual(len(dashboard_config['widgets']), 1)


class TestReportGenerator(unittest.TestCase):
    """Test Report Generator functionality"""

    def setUp(self):
        self.generator = ReportGenerator()

    def test_generate_report_pdf(self):
        """Test PDF report generation"""
        # Mock data
        kpis = [
            KPI("MRR", 1000.0, "EUR", 5.0, "up"),
            KPI("ARR", 12000.0, "EUR", 5.0, "up")
        ]

        # This will fail without actual implementation
        # but tests the interface
        with patch.object(self.generator, '_generate_pdf') as mock_pdf:
            mock_pdf.return_value = b'PDF_DATA'

            result = self.generator.generate_report(
                format=ReportFormat.PDF,
                kpis=kpis,
                include_kpis=True,
                include_charts=False
            )

            mock_pdf.assert_called_once()

    def test_generate_report_excel(self):
        """Test Excel report generation"""
        kpis = [KPI("MRR", 1000.0, "EUR", 5.0, "up")]

        with patch.object(self.generator, '_generate_excel') as mock_excel:
            mock_excel.return_value = b'EXCEL_DATA'

            result = self.generator.generate_report(
                format=ReportFormat.EXCEL,
                kpis=kpis,
                include_kpis=True
            )

            mock_excel.assert_called_once()

    def test_generate_report_json(self):
        """Test JSON report generation"""
        kpis = [KPI("MRR", 1000.0, "EUR", 5.0, "up")]

        result = self.generator.generate_report(
            format=ReportFormat.JSON,
            kpis=kpis,
            include_kpis=True
        )

        # JSON generation should work without mocking
        self.assertIsInstance(result, bytes)


class TestReportScheduler(unittest.TestCase):
    """Test Report Scheduler functionality"""

    def setUp(self):
        self.dashboard = Mock()
        self.scheduler = ReportScheduler(parent_dashboard=self.dashboard)

    def test_schedule_report(self):
        """Test scheduling a new report"""
        report_id = self.scheduler.schedule_report(
            name="Weekly Report",
            frequency=ReportFrequency.WEEKLY,
            format=ReportFormat.PDF,
            recipients=["user@example.com"]
        )

        self.assertIsInstance(report_id, str)
        self.assertIn(report_id, self.scheduler.scheduled_reports)

    def test_unschedule_report(self):
        """Test unscheduling a report"""
        report_id = self.scheduler.schedule_report(
            name="Test Report",
            frequency=ReportFrequency.DAILY,
            format=ReportFormat.PDF,
            recipients=[]
        )

        result = self.scheduler.unschedule_report(report_id)
        self.assertTrue(result)
        self.assertNotIn(report_id, self.scheduler.scheduled_reports)

    def test_calculate_next_run_daily(self):
        """Test next run calculation for daily frequency"""
        next_run = self.scheduler.calculate_next_run(ReportFrequency.DAILY)
        expected = datetime.now() + timedelta(days=1)

        # Check if next run is approximately tomorrow
        self.assertAlmostEqual(
            next_run.timestamp(),
            expected.timestamp(),
            delta=60  # Within 1 minute
        )

    def test_calculate_next_run_weekly(self):
        """Test next run calculation for weekly frequency"""
        next_run = self.scheduler.calculate_next_run(ReportFrequency.WEEKLY)
        expected = datetime.now() + timedelta(weeks=1)

        self.assertAlmostEqual(
            next_run.timestamp(),
            expected.timestamp(),
            delta=3600  # Within 1 hour
        )

    def test_list_scheduled_reports(self):
        """Test listing all scheduled reports"""
        self.scheduler.schedule_report("Report 1", ReportFrequency.DAILY, ReportFormat.PDF, [])
        self.scheduler.schedule_report("Report 2", ReportFrequency.WEEKLY, ReportFormat.EXCEL, [])

        reports = self.scheduler.list_scheduled_reports()

        self.assertEqual(len(reports), 2)
        self.assertTrue(all('id' in r for r in reports))
        self.assertTrue(all('name' in r for r in reports))


class TestBIDashboard(unittest.TestCase):
    """Test main BIDashboard class"""

    def setUp(self):
        self.dashboard = BIDashboard()

    @patch.object(BIDashboard, '_fetch_subscriptions')
    def test_create_executive_dashboard(self, mock_fetch):
        """Test creating executive dashboard"""
        mock_fetch.return_value = [
            {'status': 'active', 'billing_cycle': 'monthly', 'amount': 1000}
        ]

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        dashboard_config = self.dashboard.create_executive_dashboard(
            tenant_id='test_tenant',
            date_range=(start_date, end_date)
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


class TestChartData(unittest.TestCase):
    """Test ChartData dataclass"""

    def test_create_chart_data(self):
        """Test creating ChartData instance"""
        chart = ChartData(
            chart_type=ChartType.LINE,
            title="Test Chart",
            data={'test': 'data'},
            labels=["A", "B", "C"],
            datasets=[{"label": "Data", "data": [1, 2, 3]}],
            options={'responsive': True}
        )

        self.assertEqual(chart.chart_type, ChartType.LINE)
        self.assertEqual(chart.title, "Test Chart")
        self.assertEqual(len(chart.labels), 3)
        self.assertEqual(len(chart.datasets), 1)
        self.assertTrue(chart.options['responsive'])


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
            description="Total monthly revenue"
        )

        self.assertEqual(kpi.name, "Monthly Revenue")
        self.assertEqual(kpi.value, 10000.0)
        self.assertEqual(kpi.unit, "EUR")
        self.assertEqual(kpi.change_percentage, 5.5)
        self.assertEqual(kpi.trend, "up")
        self.assertEqual(kpi.target, 12000.0)
        self.assertIsInstance(kpi.timestamp, datetime)


if __name__ == '__main__':
    unittest.main()
