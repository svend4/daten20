#!/usr/bin/env python3
"""
Business Intelligence Dashboard Usage Examples

Demonstrates how to use the BI Dashboard module for:
- Creating executive dashboards
- Calculating KPIs
- Generating reports in multiple formats
- Scheduling automated reports
- Building custom dashboards

Author: Claude AI
Date: 2026-01-16
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics.bi_dashboard import (
    BIDashboard,
    ChartData,
    ChartType,
    KPI,
    KPICalculator,
    ReportFormat,
    ReportFrequency,
    get_bi_dashboard,
)


def example_1_kpi_calculation():
    """Example 1: Calculate business KPIs"""
    print("=" * 60)
    print("Example 1: KPI Calculation")
    print("=" * 60)

    calculator = KPICalculator()

    # Sample subscription data
    subscriptions = [
        {"status": "active", "billing_cycle": "monthly", "amount": 99},
        {"status": "active", "billing_cycle": "monthly", "amount": 199},
        {"status": "active", "billing_cycle": "yearly", "amount": 990},
        {"status": "active", "billing_cycle": "monthly", "amount": 49},
    ]

    # Calculate MRR and ARR
    mrr = calculator.calculate_mrr(subscriptions)
    arr = calculator.calculate_arr(mrr)

    print(f"\n📊 Revenue Metrics:")
    print(f"  MRR (Monthly Recurring Revenue): €{mrr:,.2f}")
    print(f"  ARR (Annual Recurring Revenue): €{arr:,.2f}")

    # Calculate other KPIs
    churn_rate = calculator.calculate_churn_rate(
        churned_customers=5, total_customers_start=100, period_days=30
    )
    print(f"\n📉 Customer Metrics:")
    print(f"  Churn Rate: {churn_rate}%")

    # Calculate CLV
    clv = calculator.calculate_clv(
        avg_revenue_per_user=mrr / 4,  # 4 active subscriptions
        avg_customer_lifespan_months=24,
        gross_margin=0.8,
    )
    print(f"  Customer Lifetime Value: €{clv:,.2f}")

    # Calculate CAC
    cac = calculator.calculate_cac(sales_marketing_costs=10000, new_customers=50)
    print(f"  Customer Acquisition Cost: €{cac:,.2f}")

    # Calculate LTV:CAC ratio
    ltv_cac_ratio = calculator.calculate_ltv_cac_ratio(clv, cac)
    print(f"  LTV:CAC Ratio: {ltv_cac_ratio:.2f} (healthy if > 3.0)")

    print()


def example_2_executive_dashboard():
    """Example 2: Create executive dashboard"""
    print("=" * 60)
    print("Example 2: Executive Dashboard")
    print("=" * 60)

    dashboard = get_bi_dashboard()

    # Create dashboard for a tenant
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    exec_dashboard = dashboard.create_executive_dashboard(
        tenant_id="company-123", date_range=(start_date, end_date)
    )

    print(f"\n✅ Executive Dashboard Created!")
    print(f"  Widgets: {len(exec_dashboard.get('widgets', []))}")
    print(f"  KPIs: {len(exec_dashboard.get('kpis', []))}")

    # Display KPIs
    if "kpis" in exec_dashboard:
        print("\n📊 Key Performance Indicators:")
        for kpi in exec_dashboard["kpis"]:
            trend_symbol = "↑" if kpi.trend == "up" else "↓" if kpi.trend == "down" else "→"
            print(f"  {kpi.name}: {kpi.value:,.2f} {kpi.unit}")
            print(f"    Change: {kpi.change_percentage:+.2f}% {trend_symbol}")
            if kpi.target:
                progress = (kpi.value / kpi.target) * 100
                print(f"    Target: {kpi.target:,.2f} ({progress:.1f}% achieved)")

    print()


def example_3_custom_report():
    """Example 3: Create and export custom report"""
    print("=" * 60)
    print("Example 3: Custom Report Generation")
    print("=" * 60)

    dashboard = get_bi_dashboard()

    # Create KPIs
    kpis = [
        KPI(
            name="Monthly Revenue",
            value=50000.0,
            unit="EUR",
            change_percentage=12.5,
            trend="up",
            target=55000.0,
            description="Total monthly revenue from all sources",
        ),
        KPI(
            name="Active Users",
            value=1250.0,
            unit="users",
            change_percentage=8.3,
            trend="up",
            target=1500.0,
            description="Number of active monthly users",
        ),
        KPI(
            name="Conversion Rate",
            value=3.2,
            unit="%",
            change_percentage=-2.1,
            trend="down",
            target=4.0,
            description="Trial to paid conversion rate",
        ),
    ]

    # Create charts
    charts = [
        ChartData(
            chart_type=ChartType.LINE,
            title="Revenue Trend (Last 6 Months)",
            data={},
            labels=["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets=[
                {
                    "label": "Revenue (EUR)",
                    "data": [42000, 44000, 46000, 48000, 49000, 50000],
                }
            ],
        ),
        ChartData(
            chart_type=ChartType.BAR,
            title="User Growth",
            data={},
            labels=["Q1", "Q2", "Q3", "Q4"],
            datasets=[{"label": "New Users", "data": [250, 300, 350, 350]}],
        ),
    ]

    # Create custom report
    report = dashboard.create_custom_report(
        name="Monthly Business Review - December 2025",
        description="Comprehensive monthly business performance report",
        kpis=kpis,
        charts=charts,
        filters={"period": "2025-12", "region": "EMEA"},
        created_by="CFO",
    )

    print(f"\n✅ Custom Report Created!")
    print(f"  Report ID: {report.id}")
    print(f"  Name: {report.name}")
    print(f"  KPIs: {len(report.kpis)}")
    print(f"  Charts: {len(report.charts)}")

    # Export to different formats
    print("\n📄 Exporting report to multiple formats...")

    # Export to PDF
    pdf_data = dashboard.export_report(report.id, ReportFormat.PDF)
    pdf_path = "/tmp/business_review.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_data)
    print(f"  ✓ PDF: {pdf_path} ({len(pdf_data):,} bytes)")

    # Export to Excel
    excel_data = dashboard.export_report(report.id, ReportFormat.EXCEL)
    excel_path = "/tmp/business_review.xlsx"
    with open(excel_path, "wb") as f:
        f.write(excel_data)
    print(f"  ✓ Excel: {excel_path} ({len(excel_data):,} bytes)")

    # Export to PowerPoint
    ppt_data = dashboard.export_report(report.id, ReportFormat.POWERPOINT)
    ppt_path = "/tmp/business_review.pptx"
    with open(ppt_path, "wb") as f:
        f.write(ppt_data)
    print(f"  ✓ PowerPoint: {ppt_path} ({len(ppt_data):,} bytes)")

    # Export to JSON
    json_data = dashboard.export_report(report.id, ReportFormat.JSON)
    json_path = "/tmp/business_review.json"
    with open(json_path, "wb") as f:
        f.write(json_data)
    print(f"  ✓ JSON: {json_path} ({len(json_data):,} bytes)")

    # Export to CSV
    csv_data = dashboard.export_report(report.id, ReportFormat.CSV)
    csv_path = "/tmp/business_review.csv"
    with open(csv_path, "wb") as f:
        f.write(csv_data)
    print(f"  ✓ CSV: {csv_path} ({len(csv_data):,} bytes)")

    print()


def example_4_scheduled_reports():
    """Example 4: Schedule automated reports"""
    print("=" * 60)
    print("Example 4: Scheduled Reports")
    print("=" * 60)

    dashboard = get_bi_dashboard()

    # First, create a report to schedule
    kpis = [
        KPI(
            name="Weekly Revenue",
            value=12500.0,
            unit="EUR",
            change_percentage=5.0,
            trend="up",
        )
    ]

    report = dashboard.create_custom_report(
        name="Weekly Performance Report",
        description="Automated weekly performance summary",
        kpis=kpis,
        charts=[],
        filters={},
        created_by="system",
    )

    # Schedule the report
    scheduled = dashboard.schedule_report(
        report_id=report.id,
        name="Weekly Performance Report - Automated",
        frequency=ReportFrequency.WEEKLY,
        recipients=["ceo@company.com", "cfo@company.com", "coo@company.com"],
        format=ReportFormat.PDF,
        filters={},
    )

    print(f"\n✅ Report Scheduled!")
    print(f"  Schedule ID: {scheduled.id}")
    print(f"  Report Name: {scheduled.name}")
    print(f"  Frequency: {scheduled.frequency.value}")
    print(f"  Recipients: {len(scheduled.recipients)}")
    for recipient in scheduled.recipients:
        print(f"    - {recipient}")
    print(f"  Format: {scheduled.format.value.upper()}")
    print(f"  Next Run: {scheduled.next_run}")

    # Show scheduler info
    print(f"\n📅 Scheduler Status:")
    print(f"  Active Schedules: {len(dashboard.report_scheduler.scheduled_reports)}")
    print(f"  Execution History: {len(dashboard.report_scheduler.execution_history)} runs")

    print()


def example_5_custom_dashboard():
    """Example 5: Build custom dashboard with widgets"""
    print("=" * 60)
    print("Example 5: Custom Dashboard with Widgets")
    print("=" * 60)

    from src.analytics.bi_dashboard import DashboardBuilder

    builder = DashboardBuilder()

    # Add KPI widgets (row 0)
    kpis = [
        KPI("MRR", 45000.0, "EUR", 10.0, "up", target=50000.0),
        KPI("ARR", 540000.0, "EUR", 10.0, "up", target=600000.0),
        KPI("Churn", 3.5, "%", -0.5, "down", target=3.0),
        KPI("NRR", 115.0, "%", 5.0, "up", target=120.0),
    ]

    for i, kpi in enumerate(kpis):
        builder.add_kpi_widget(kpi, position={"row": 0, "col": i * 3}, size={"width": 3, "height": 2})

    # Add chart widgets (row 2)
    revenue_chart = ChartData(
        chart_type=ChartType.LINE,
        title="Revenue Trend",
        data={},
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets=[{"label": "MRR (EUR)", "data": [40000, 41000, 42000, 43000, 44000, 45000]}],
    )

    user_chart = ChartData(
        chart_type=ChartType.BAR,
        title="User Growth",
        data={},
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets=[{"label": "Active Users", "data": [900, 950, 1000, 1100, 1200, 1250]}],
    )

    builder.add_chart_widget(revenue_chart, position={"row": 2, "col": 0}, size={"width": 6, "height": 4})

    builder.add_chart_widget(user_chart, position={"row": 2, "col": 6}, size={"width": 6, "height": 4})

    # Add table widget (row 6)
    builder.add_table_widget(
        title="Top Products by Revenue",
        headers=["Product", "Revenue (EUR)", "Growth %"],
        rows=[
            ["Premium Plan", "€25,000", "+15%"],
            ["Business Plan", "€15,000", "+12%"],
            ["Starter Plan", "€5,000", "+8%"],
        ],
        position={"row": 6, "col": 0},
        size={"width": 12, "height": 3},
    )

    # Build dashboard configuration
    dashboard_config = builder.build()

    print(f"\n✅ Custom Dashboard Built!")
    print(f"  Total Widgets: {len(dashboard_config['widgets'])}")

    widget_types = {}
    for widget in dashboard_config["widgets"]:
        widget_type = widget["type"]
        widget_types[widget_type] = widget_types.get(widget_type, 0) + 1

    print(f"\n📊 Widget Breakdown:")
    for widget_type, count in widget_types.items():
        print(f"  {widget_type.upper()}: {count}")

    print(f"\n⚙️  Layout:")
    print(f"  Grid Columns: {dashboard_config['layout']['columns']}")
    print(f"  Created: {dashboard_config['created_at']}")

    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("BI DASHBOARD USAGE EXAMPLES")
    print("=" * 60)
    print()

    try:
        example_1_kpi_calculation()
        example_2_executive_dashboard()
        example_3_custom_report()
        example_4_scheduled_reports()
        example_5_custom_dashboard()

        print("=" * 60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("📁 Generated Files:")
        print("  /tmp/business_review.pdf")
        print("  /tmp/business_review.xlsx")
        print("  /tmp/business_review.pptx")
        print("  /tmp/business_review.json")
        print("  /tmp/business_review.csv")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
