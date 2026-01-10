#!/usr/bin/env python3
"""
Business Intelligence Dashboard Module

Provides comprehensive business intelligence and KPI tracking for enterprise customers.
Features executive dashboards, custom report builders, scheduled reports, and drill-down analytics.

Key Features:
- Executive KPI dashboard (MRR, ARR, Churn, CLV, NRR, CAC)
- Real-time data visualization
- Custom report builder
- Scheduled reports (daily, weekly, monthly)
- Export to PDF, Excel, PowerPoint
- Drill-down analytics
- Filter & dimension management
- Calculated metrics
- Trend analysis
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import threading
from collections import defaultdict


class ReportFormat(str, Enum):
    """Report export formats"""
    PDF = "pdf"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    JSON = "json"
    CSV = "csv"


class ReportFrequency(str, Enum):
    """Report scheduling frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ChartType(str, Enum):
    """Chart types for visualizations"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"


@dataclass
class KPI:
    """Key Performance Indicator"""
    name: str
    value: float
    unit: str
    change_percentage: float  # vs previous period
    trend: str  # "up", "down", "stable"
    target: Optional[float] = None
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChartData:
    """Chart data structure"""
    chart_type: ChartType
    title: str
    data: Dict[str, Any]
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    """BI Report"""
    id: str
    name: str
    description: str
    kpis: List[KPI]
    charts: List[ChartData]
    filters: Dict[str, Any]
    created_at: datetime
    created_by: str
    format: ReportFormat


@dataclass
class ScheduledReport:
    """Scheduled report configuration"""
    id: str
    report_id: str
    name: str
    frequency: ReportFrequency
    recipients: List[str]  # email addresses
    format: ReportFormat
    filters: Dict[str, Any]
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class KPICalculator:
    """
    Calculate business KPIs from raw data

    Calculates metrics such as:
    - MRR (Monthly Recurring Revenue)
    - ARR (Annual Recurring Revenue)
    - Churn Rate
    - Customer Lifetime Value (CLV)
    - Net Revenue Retention (NRR)
    - Customer Acquisition Cost (CAC)
    - ARPU (Average Revenue Per User)
    """

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.cache_timestamps = {}

    def calculate_mrr(self, subscriptions: List[Dict]) -> Decimal:
        """
        Calculate Monthly Recurring Revenue

        Args:
            subscriptions: List of active subscriptions

        Returns:
            Total MRR in decimal
        """
        mrr = Decimal("0")

        for sub in subscriptions:
            if sub.get('status') != 'active':
                continue

            if sub.get('billing_cycle') == 'monthly':
                mrr += Decimal(str(sub.get('amount', 0)))
            elif sub.get('billing_cycle') == 'yearly':
                # Convert yearly to monthly
                mrr += Decimal(str(sub.get('amount', 0))) / Decimal("12")

        return mrr

    def calculate_arr(self, mrr: Decimal) -> Decimal:
        """Calculate Annual Recurring Revenue from MRR"""
        return mrr * Decimal("12")

    def calculate_churn_rate(
        self,
        churned_customers: int,
        total_customers_start: int,
        period_days: int = 30
    ) -> float:
        """
        Calculate customer churn rate

        Args:
            churned_customers: Number of customers who churned
            total_customers_start: Total customers at start of period
            period_days: Period length in days

        Returns:
            Churn rate as percentage
        """
        if total_customers_start == 0:
            return 0.0

        # Monthly churn rate
        monthly_churn = (churned_customers / total_customers_start) * 100

        # Annualize if needed
        if period_days != 30:
            monthly_churn = monthly_churn * (30 / period_days)

        return round(monthly_churn, 2)

    def calculate_clv(
        self,
        avg_revenue_per_user: Decimal,
        avg_customer_lifespan_months: int,
        gross_margin: float = 0.8
    ) -> Decimal:
        """
        Calculate Customer Lifetime Value

        Args:
            avg_revenue_per_user: ARPU (monthly)
            avg_customer_lifespan_months: Average months customer stays
            gross_margin: Gross profit margin (default 80%)

        Returns:
            CLV in decimal
        """
        clv = avg_revenue_per_user * Decimal(str(avg_customer_lifespan_months)) * Decimal(str(gross_margin))
        return clv.quantize(Decimal("0.01"))

    def calculate_nrr(
        self,
        revenue_start: Decimal,
        expansion_revenue: Decimal,
        churned_revenue: Decimal
    ) -> float:
        """
        Calculate Net Revenue Retention

        Args:
            revenue_start: Revenue at start of period
            expansion_revenue: Revenue from upgrades/expansion
            churned_revenue: Revenue lost from churn

        Returns:
            NRR as percentage
        """
        if revenue_start == 0:
            return 0.0

        revenue_end = revenue_start + expansion_revenue - churned_revenue
        nrr = (revenue_end / revenue_start) * 100

        return round(nrr, 2)

    def calculate_cac(
        self,
        sales_marketing_costs: Decimal,
        new_customers: int
    ) -> Decimal:
        """
        Calculate Customer Acquisition Cost

        Args:
            sales_marketing_costs: Total sales & marketing spend
            new_customers: Number of new customers acquired

        Returns:
            CAC per customer
        """
        if new_customers == 0:
            return Decimal("0")

        cac = sales_marketing_costs / Decimal(str(new_customers))
        return cac.quantize(Decimal("0.01"))

    def calculate_arpu(self, total_revenue: Decimal, total_users: int) -> Decimal:
        """Calculate Average Revenue Per User"""
        if total_users == 0:
            return Decimal("0")

        arpu = total_revenue / Decimal(str(total_users))
        return arpu.quantize(Decimal("0.01"))

    def calculate_ltv_cac_ratio(self, clv: Decimal, cac: Decimal) -> float:
        """
        Calculate LTV:CAC ratio

        Healthy SaaS businesses typically have ratio > 3.0
        """
        if cac == 0:
            return 0.0

        ratio = float(clv / cac)
        return round(ratio, 2)

    def get_kpi_trend(self, current: float, previous: float) -> Tuple[float, str]:
        """
        Determine KPI trend

        Returns:
            (change_percentage, trend_direction)
        """
        if previous == 0:
            return (0.0, "stable")

        change = ((current - previous) / previous) * 100

        if abs(change) < 1:
            trend = "stable"
        elif change > 0:
            trend = "up"
        else:
            trend = "down"

        return (round(change, 2), trend)


class DashboardBuilder:
    """
    Build custom dashboards with widgets

    Supports multiple widget types:
    - KPI cards
    - Line charts
    - Bar charts
    - Pie charts
    - Tables
    - Heatmaps
    """

    def __init__(self):
        self.widgets = []
        self.layout = {"rows": [], "columns": 12}

    def add_kpi_widget(
        self,
        kpi: KPI,
        position: Dict[str, int],
        size: Dict[str, int] = {"width": 3, "height": 2}
    ):
        """Add KPI card widget"""
        widget = {
            "type": "kpi",
            "kpi": kpi,
            "position": position,
            "size": size
        }
        self.widgets.append(widget)
        return self

    def add_chart_widget(
        self,
        chart: ChartData,
        position: Dict[str, int],
        size: Dict[str, int] = {"width": 6, "height": 4}
    ):
        """Add chart widget"""
        widget = {
            "type": "chart",
            "chart": chart,
            "position": position,
            "size": size
        }
        self.widgets.append(widget)
        return self

    def add_table_widget(
        self,
        title: str,
        headers: List[str],
        rows: List[List[Any]],
        position: Dict[str, int],
        size: Dict[str, int] = {"width": 12, "height": 4}
    ):
        """Add table widget"""
        widget = {
            "type": "table",
            "title": title,
            "headers": headers,
            "rows": rows,
            "position": position,
            "size": size
        }
        self.widgets.append(widget)
        return self

    def build(self) -> Dict[str, Any]:
        """Build dashboard configuration"""
        return {
            "widgets": self.widgets,
            "layout": self.layout,
            "created_at": datetime.now().isoformat()
        }


class ReportGenerator:
    """
    Generate reports in various formats

    Supports:
    - PDF reports
    - Excel workbooks
    - PowerPoint presentations
    - JSON data
    - CSV exports
    """

    def __init__(self):
        self.templates = {}

    def generate_pdf(self, report: Report) -> bytes:
        """
        Generate PDF report

        Args:
            report: Report configuration

        Returns:
            PDF file as bytes
        """
        # TODO: Implement with ReportLab or WeasyPrint
        # This is a placeholder implementation

        pdf_content = f"""
        PDF REPORT: {report.name}
        Generated: {datetime.now()}

        KPIs:
        {self._format_kpis_text(report.kpis)}

        Charts: {len(report.charts)} visualizations included

        Filters: {json.dumps(report.filters, indent=2)}
        """

        return pdf_content.encode('utf-8')

    def generate_excel(self, report: Report) -> bytes:
        """
        Generate Excel workbook

        Creates multiple sheets:
        - Summary (KPIs)
        - Data tables
        - Charts
        """
        # TODO: Implement with openpyxl or xlsxwriter
        # Placeholder implementation

        excel_data = {
            "summary": self._kpis_to_dict(report.kpis),
            "charts": [chart.title for chart in report.charts],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_name": report.name
            }
        }

        return json.dumps(excel_data, indent=2).encode('utf-8')

    def generate_powerpoint(self, report: Report) -> bytes:
        """Generate PowerPoint presentation"""
        # TODO: Implement with python-pptx
        # Placeholder

        ppt_content = f"PowerPoint: {report.name}\nSlides: {len(report.charts) + 1}"
        return ppt_content.encode('utf-8')

    def generate_json(self, report: Report) -> str:
        """Generate JSON report"""
        report_dict = {
            "id": report.id,
            "name": report.name,
            "description": report.description,
            "kpis": self._kpis_to_dict(report.kpis),
            "charts": [self._chart_to_dict(chart) for chart in report.charts],
            "filters": report.filters,
            "created_at": report.created_at.isoformat(),
            "created_by": report.created_by
        }

        return json.dumps(report_dict, indent=2)

    def generate_csv(self, report: Report) -> str:
        """Generate CSV export of KPIs"""
        csv_lines = ["KPI,Value,Unit,Change %,Trend,Target"]

        for kpi in report.kpis:
            line = f"{kpi.name},{kpi.value},{kpi.unit},{kpi.change_percentage},{kpi.trend},{kpi.target or ''}"
            csv_lines.append(line)

        return "\n".join(csv_lines)

    def _format_kpis_text(self, kpis: List[KPI]) -> str:
        """Format KPIs as text"""
        lines = []
        for kpi in kpis:
            line = f"- {kpi.name}: {kpi.value} {kpi.unit} ({kpi.change_percentage:+.2f}% {kpi.trend})"
            lines.append(line)
        return "\n".join(lines)

    def _kpis_to_dict(self, kpis: List[KPI]) -> List[Dict]:
        """Convert KPIs to dictionary"""
        return [
            {
                "name": kpi.name,
                "value": kpi.value,
                "unit": kpi.unit,
                "change_percentage": kpi.change_percentage,
                "trend": kpi.trend,
                "target": kpi.target,
                "description": kpi.description
            }
            for kpi in kpis
        ]

    def _chart_to_dict(self, chart: ChartData) -> Dict:
        """Convert chart to dictionary"""
        return {
            "type": chart.chart_type.value,
            "title": chart.title,
            "data": chart.data,
            "labels": chart.labels,
            "datasets": chart.datasets,
            "options": chart.options
        }


class ReportScheduler:
    """
    Schedule and execute reports automatically

    Features:
    - Cron-like scheduling
    - Email delivery
    - Retry on failure
    - Execution history
    """

    def __init__(self):
        self.scheduled_reports: Dict[str, ScheduledReport] = {}
        self.execution_history = []
        self._running = False
        self._thread = None

    def schedule_report(self, scheduled_report: ScheduledReport):
        """Schedule a report for automatic execution"""
        self.scheduled_reports[scheduled_report.id] = scheduled_report

        # Calculate next run time
        scheduled_report.next_run = self._calculate_next_run(
            scheduled_report.frequency
        )

    def unschedule_report(self, report_id: str):
        """Remove scheduled report"""
        if report_id in self.scheduled_reports:
            del self.scheduled_reports[report_id]

    def start_scheduler(self):
        """Start background scheduler thread"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()

    def stop_scheduler(self):
        """Stop scheduler thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self._running:
            now = datetime.now()

            for report in self.scheduled_reports.values():
                if not report.enabled:
                    continue

                if report.next_run and now >= report.next_run:
                    self._execute_scheduled_report(report)

            # Sleep for 60 seconds between checks
            import time
            time.sleep(60)

    def _execute_scheduled_report(self, scheduled_report: ScheduledReport):
        """Execute scheduled report and send to recipients"""
        try:
            # Record execution
            execution = {
                "report_id": scheduled_report.report_id,
                "scheduled_report_id": scheduled_report.id,
                "executed_at": datetime.now(),
                "status": "success",
                "recipients": scheduled_report.recipients
            }

            # TODO: Generate actual report and send emails
            # For now, just record execution

            self.execution_history.append(execution)

            # Update last run and calculate next run
            scheduled_report.last_run = datetime.now()
            scheduled_report.next_run = self._calculate_next_run(
                scheduled_report.frequency,
                from_time=scheduled_report.last_run
            )

        except Exception as e:
            execution = {
                "report_id": scheduled_report.report_id,
                "executed_at": datetime.now(),
                "status": "failed",
                "error": str(e)
            }
            self.execution_history.append(execution)

    def _calculate_next_run(
        self,
        frequency: ReportFrequency,
        from_time: Optional[datetime] = None
    ) -> datetime:
        """Calculate next run time based on frequency"""
        base_time = from_time or datetime.now()

        if frequency == ReportFrequency.DAILY:
            return base_time + timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            return base_time + timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            # Approximate monthly as 30 days
            return base_time + timedelta(days=30)
        elif frequency == ReportFrequency.QUARTERLY:
            return base_time + timedelta(days=90)

        return base_time + timedelta(days=1)

    def get_execution_history(
        self,
        report_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get execution history"""
        history = self.execution_history

        if report_id:
            history = [h for h in history if h.get('report_id') == report_id]

        return history[-limit:]


class BIDashboard:
    """
    Main Business Intelligence Dashboard

    Provides unified interface for:
    - KPI calculation and tracking
    - Custom dashboard building
    - Report generation and scheduling
    - Trend analysis
    - Drill-down analytics
    """

    def __init__(self):
        self.kpi_calculator = KPICalculator()
        self.dashboard_builder = DashboardBuilder()
        self.report_generator = ReportGenerator()
        self.report_scheduler = ReportScheduler()

        self.dashboards: Dict[str, Dict] = {}
        self.reports: Dict[str, Report] = {}

    def create_executive_dashboard(
        self,
        tenant_id: str,
        date_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """
        Create executive KPI dashboard

        Args:
            tenant_id: Tenant ID
            date_range: (start_date, end_date)

        Returns:
            Dashboard configuration with KPIs and charts
        """
        start_date, end_date = date_range

        # Get data (placeholder - would fetch from database)
        subscriptions = self._fetch_subscriptions(tenant_id, end_date)
        previous_subscriptions = self._fetch_subscriptions(
            tenant_id,
            start_date - timedelta(days=30)
        )

        # Calculate KPIs
        mrr = self.kpi_calculator.calculate_mrr(subscriptions)
        previous_mrr = self.kpi_calculator.calculate_mrr(previous_subscriptions)
        mrr_change, mrr_trend = self.kpi_calculator.get_kpi_trend(
            float(mrr), float(previous_mrr)
        )

        arr = self.kpi_calculator.calculate_arr(mrr)

        # Create KPI objects
        kpis = [
            KPI(
                name="Monthly Recurring Revenue",
                value=float(mrr),
                unit="EUR",
                change_percentage=mrr_change,
                trend=mrr_trend,
                target=100000.0,
                description="Total monthly recurring revenue"
            ),
            KPI(
                name="Annual Recurring Revenue",
                value=float(arr),
                unit="EUR",
                change_percentage=mrr_change * 12,  # Approximation
                trend=mrr_trend,
                target=1200000.0,
                description="Annualized recurring revenue"
            )
        ]

        # Build dashboard
        builder = DashboardBuilder()

        # Add KPI widgets
        for i, kpi in enumerate(kpis):
            builder.add_kpi_widget(
                kpi,
                position={"row": 0, "col": i * 3},
                size={"width": 3, "height": 2}
            )

        # Add revenue trend chart
        revenue_chart = ChartData(
            chart_type=ChartType.LINE,
            title="Revenue Trend",
            data={},
            labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets=[
                {
                    "label": "MRR",
                    "data": [85000, 88000, 92000, 95000, 97000, float(mrr)]
                }
            ]
        )

        builder.add_chart_widget(
            revenue_chart,
            position={"row": 2, "col": 0},
            size={"width": 6, "height": 4}
        )

        dashboard = builder.build()
        dashboard["kpis"] = kpis

        return dashboard

    def create_custom_report(
        self,
        name: str,
        description: str,
        kpis: List[KPI],
        charts: List[ChartData],
        filters: Dict[str, Any],
        created_by: str
    ) -> Report:
        """Create custom report"""
        import uuid

        report = Report(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            kpis=kpis,
            charts=charts,
            filters=filters,
            created_at=datetime.now(),
            created_by=created_by,
            format=ReportFormat.JSON
        )

        self.reports[report.id] = report
        return report

    def export_report(self, report_id: str, format: ReportFormat) -> bytes:
        """Export report in specified format"""
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report.format = format

        if format == ReportFormat.PDF:
            return self.report_generator.generate_pdf(report)
        elif format == ReportFormat.EXCEL:
            return self.report_generator.generate_excel(report)
        elif format == ReportFormat.POWERPOINT:
            return self.report_generator.generate_powerpoint(report)
        elif format == ReportFormat.JSON:
            return self.report_generator.generate_json(report).encode('utf-8')
        elif format == ReportFormat.CSV:
            return self.report_generator.generate_csv(report).encode('utf-8')

        raise ValueError(f"Unsupported format: {format}")

    def schedule_report(
        self,
        report_id: str,
        name: str,
        frequency: ReportFrequency,
        recipients: List[str],
        format: ReportFormat,
        filters: Optional[Dict[str, Any]] = None
    ) -> ScheduledReport:
        """Schedule automatic report generation"""
        import uuid

        scheduled_report = ScheduledReport(
            id=str(uuid.uuid4()),
            report_id=report_id,
            name=name,
            frequency=frequency,
            recipients=recipients,
            format=format,
            filters=filters or {}
        )

        self.report_scheduler.schedule_report(scheduled_report)
        return scheduled_report

    def _fetch_subscriptions(
        self,
        tenant_id: str,
        as_of_date: datetime
    ) -> List[Dict]:
        """Fetch subscriptions data (placeholder)"""
        # TODO: Fetch from actual database
        # This is a placeholder implementation
        return [
            {
                "id": "sub1",
                "tenant_id": tenant_id,
                "status": "active",
                "billing_cycle": "monthly",
                "amount": 99.00
            }
        ]


# Singleton instance
_bi_dashboard_instance = None
_instance_lock = threading.Lock()


def get_bi_dashboard() -> BIDashboard:
    """Get singleton BI Dashboard instance"""
    global _bi_dashboard_instance

    if _bi_dashboard_instance is None:
        with _instance_lock:
            if _bi_dashboard_instance is None:
                _bi_dashboard_instance = BIDashboard()

    return _bi_dashboard_instance


if __name__ == "__main__":
    # Example usage
    dashboard = get_bi_dashboard()

    # Create executive dashboard
    exec_dashboard = dashboard.create_executive_dashboard(
        tenant_id="tenant123",
        date_range=(datetime.now() - timedelta(days=30), datetime.now())
    )

    print("Executive Dashboard Created!")
    print(f"KPIs: {len(exec_dashboard.get('kpis', []))}")
    print(f"Widgets: {len(exec_dashboard.get('widgets', []))}")

    # Calculate KPIs
    calc = KPICalculator()

    subscriptions = [
        {"status": "active", "billing_cycle": "monthly", "amount": 99},
        {"status": "active", "billing_cycle": "yearly", "amount": 990},
    ]

    mrr = calc.calculate_mrr(subscriptions)
    arr = calc.calculate_arr(mrr)

    print(f"\nMRR: €{mrr}")
    print(f"ARR: €{arr}")

    print("\nBI Dashboard module loaded successfully!")
