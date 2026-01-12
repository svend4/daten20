#!/usr/bin/env python3
"""
Scheduled Reports Examples

This script demonstrates how to use the scheduled reports feature in the BI Dashboard.

Features:
- Schedule reports for automatic generation
- Send reports via email
- Support for multiple formats (PDF, Excel, PowerPoint)
- Flexible scheduling (daily, weekly, monthly, quarterly)
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.analytics.bi_dashboard import (
    BIDashboard,
    Report,
    ReportFormat,
    ReportFrequency,
    ScheduledReport,
    KPI
)
from datetime import datetime
import time


def example_1_basic_scheduled_report():
    """Example 1: Basic scheduled report setup"""
    print("\n" + "="*70)
    print("Example 1: Basic Scheduled Report")
    print("="*70 + "\n")

    # Create dashboard
    dashboard = BIDashboard()

    # Create a sample report
    report = Report(
        id="monthly_kpi_report",
        name="Monthly KPI Report",
        description="Monthly business KPIs and metrics",
        kpis=[
            KPI(
                name="Monthly Recurring Revenue",
                value="$125,000",
                unit="USD",
                change_percentage=8.5,
                trend="up"
            ),
            KPI(
                name="Active Customers",
                value="450",
                unit="customers",
                change_percentage=12.0,
                trend="up"
            ),
            KPI(
                name="Churn Rate",
                value="2.3",
                unit="%",
                change_percentage=-0.5,
                trend="down"
            )
        ],
        charts=[],
        filters={},
        created_at=datetime.now(),
        created_by="admin@example.com",
        format=ReportFormat.PDF
    )

    # Add report to dashboard
    dashboard.reports[report.id] = report

    # Schedule the report
    scheduled_report = dashboard.schedule_report(
        report_id=report.id,
        name="Monthly Executive Summary",
        frequency=ReportFrequency.MONTHLY,
        recipients=["executive@example.com", "cfo@example.com"],
        format=ReportFormat.PDF
    )

    print(f"✅ Report scheduled successfully!")
    print(f"   Report ID: {scheduled_report.id}")
    print(f"   Name: {scheduled_report.name}")
    print(f"   Frequency: {scheduled_report.frequency.value}")
    print(f"   Format: {scheduled_report.format.value}")
    print(f"   Recipients: {', '.join(scheduled_report.recipients)}")
    print(f"   Next Run: {scheduled_report.next_run.strftime('%Y-%m-%d %H:%M')}")


def example_2_multiple_formats():
    """Example 2: Schedule same report in multiple formats"""
    print("\n" + "="*70)
    print("Example 2: Multiple Format Scheduling")
    print("="*70 + "\n")

    dashboard = BIDashboard()

    # Create report
    report = Report(
        id="weekly_metrics",
        name="Weekly Metrics Report",
        description="Weekly business metrics and trends",
        kpis=[
            KPI(name="Weekly Revenue", value="$28,500", unit="USD",
                change_percentage=5.2, trend="up"),
            KPI(name="New Signups", value="42", unit="users",
                change_percentage=18.0, trend="up")
        ],
        charts=[],
        filters={},
        created_at=datetime.now(),
        created_by="admin@example.com",
        format=ReportFormat.PDF
    )

    dashboard.reports[report.id] = report

    # Schedule PDF version for executives
    pdf_schedule = dashboard.schedule_report(
        report_id=report.id,
        name="Weekly Metrics (Executive PDF)",
        frequency=ReportFrequency.WEEKLY,
        recipients=["ceo@example.com"],
        format=ReportFormat.PDF
    )

    # Schedule Excel version for analysts
    excel_schedule = dashboard.schedule_report(
        report_id=report.id,
        name="Weekly Metrics (Analyst Excel)",
        frequency=ReportFrequency.WEEKLY,
        recipients=["analyst@example.com", "data-team@example.com"],
        format=ReportFormat.EXCEL
    )

    # Schedule PowerPoint for sales team
    ppt_schedule = dashboard.schedule_report(
        report_id=report.id,
        name="Weekly Metrics (Sales PowerPoint)",
        frequency=ReportFrequency.WEEKLY,
        recipients=["sales@example.com"],
        format=ReportFormat.POWERPOINT
    )

    print("✅ Report scheduled in 3 formats:")
    print(f"   📄 PDF for executives - Next run: {pdf_schedule.next_run.strftime('%Y-%m-%d')}")
    print(f"   📊 Excel for analysts - Next run: {excel_schedule.next_run.strftime('%Y-%m-%d')}")
    print(f"   📽️  PowerPoint for sales - Next run: {ppt_schedule.next_run.strftime('%Y-%m-%d')}")


def example_3_different_frequencies():
    """Example 3: Schedule reports with different frequencies"""
    print("\n" + "="*70)
    print("Example 3: Different Scheduling Frequencies")
    print("="*70 + "\n")

    dashboard = BIDashboard()

    # Create different reports
    reports = [
        ("daily_ops", "Daily Operations Report", ReportFrequency.DAILY),
        ("weekly_sales", "Weekly Sales Report", ReportFrequency.WEEKLY),
        ("monthly_finance", "Monthly Financial Report", ReportFrequency.MONTHLY),
        ("quarterly_board", "Quarterly Board Report", ReportFrequency.QUARTERLY)
    ]

    for report_id, report_name, frequency in reports:
        report = Report(
            id=report_id,
            name=report_name,
            description=f"{frequency.value.capitalize()} business report",
            kpis=[
                KPI(name="Sample Metric", value="100", unit="units",
                    change_percentage=5.0, trend="up")
            ],
            charts=[],
            filters={},
            created_at=datetime.now(),
            created_by="admin@example.com",
            format=ReportFormat.PDF
        )
        dashboard.reports[report_id] = report

        scheduled = dashboard.schedule_report(
            report_id=report_id,
            name=report_name,
            frequency=frequency,
            recipients=["team@example.com"],
            format=ReportFormat.PDF
        )

        print(f"✅ {report_name}")
        print(f"   Frequency: {frequency.value}")
        print(f"   Next run: {scheduled.next_run.strftime('%Y-%m-%d %H:%M')}\n")


def example_4_scheduler_control():
    """Example 4: Start and stop the scheduler"""
    print("\n" + "="*70)
    print("Example 4: Scheduler Control")
    print("="*70 + "\n")

    dashboard = BIDashboard()
    scheduler = dashboard.report_scheduler

    # Create and schedule a report
    report = Report(
        id="test_report",
        name="Test Report",
        description="Test scheduled report",
        kpis=[],
        charts=[],
        filters={},
        created_at=datetime.now(),
        created_by="admin@example.com",
        format=ReportFormat.PDF
    )
    dashboard.reports[report.id] = report

    dashboard.schedule_report(
        report_id=report.id,
        name="Test Scheduled Report",
        frequency=ReportFrequency.DAILY,
        recipients=["test@example.com"],
        format=ReportFormat.PDF
    )

    print("📋 Scheduled Reports:", len(scheduler.scheduled_reports))

    # Start scheduler
    print("\n🚀 Starting scheduler...")
    scheduler.start_scheduler()
    print("✅ Scheduler is running:", scheduler._running)

    # Let it run for a moment
    time.sleep(2)

    # Stop scheduler
    print("\n⏸️  Stopping scheduler...")
    scheduler.stop_scheduler()
    print("✅ Scheduler stopped:", not scheduler._running)

    # Check execution history
    print(f"\n📊 Execution History: {len(scheduler.execution_history)} executions")


def example_5_unschedule_report():
    """Example 5: Unschedule a report"""
    print("\n" + "="*70)
    print("Example 5: Unscheduling Reports")
    print("="*70 + "\n")

    dashboard = BIDashboard()

    # Create and schedule report
    report = Report(
        id="temp_report",
        name="Temporary Report",
        description="This will be unscheduled",
        kpis=[],
        charts=[],
        filters={},
        created_at=datetime.now(),
        created_by="admin@example.com",
        format=ReportFormat.PDF
    )
    dashboard.reports[report.id] = report

    scheduled = dashboard.schedule_report(
        report_id=report.id,
        name="Temp Scheduled Report",
        frequency=ReportFrequency.DAILY,
        recipients=["temp@example.com"],
        format=ReportFormat.PDF
    )

    print(f"✅ Report scheduled: {scheduled.id}")
    print(f"   Scheduled reports count: {len(dashboard.report_scheduler.scheduled_reports)}")

    # Unschedule
    dashboard.report_scheduler.unschedule_report(scheduled.id)
    print(f"\n🗑️  Report unscheduled")
    print(f"   Scheduled reports count: {len(dashboard.report_scheduler.scheduled_reports)}")


def example_6_filters_and_customization():
    """Example 6: Scheduled reports with filters"""
    print("\n" + "="*70)
    print("Example 6: Reports with Filters")
    print("="*70 + "\n")

    dashboard = BIDashboard()

    # Create report with filters
    report = Report(
        id="regional_report",
        name="Regional Sales Report",
        description="Sales metrics filtered by region",
        kpis=[
            KPI(name="Regional Revenue", value="$85,000", unit="USD",
                change_percentage=7.2, trend="up")
        ],
        charts=[],
        filters={
            "region": "North America",
            "product_line": "Enterprise",
            "date_range": "last_30_days"
        },
        created_at=datetime.now(),
        created_by="admin@example.com",
        format=ReportFormat.EXCEL
    )

    dashboard.reports[report.id] = report

    # Schedule with custom filters
    scheduled = dashboard.schedule_report(
        report_id=report.id,
        name="North America Enterprise Report",
        frequency=ReportFrequency.MONTHLY,
        recipients=["na-sales@example.com", "enterprise-team@example.com"],
        format=ReportFormat.EXCEL,
        filters={
            "region": "North America",
            "product_line": "Enterprise"
        }
    )

    print("✅ Regional report scheduled")
    print(f"   Filters: {scheduled.filters}")
    print(f"   Recipients: {', '.join(scheduled.recipients)}")
    print(f"   Next run: {scheduled.next_run.strftime('%Y-%m-%d')}")


def example_7_list_scheduled_reports():
    """Example 7: List all scheduled reports"""
    print("\n" + "="*70)
    print("Example 7: List Scheduled Reports")
    print("="*70 + "\n")

    dashboard = BIDashboard()

    # Schedule multiple reports
    for i in range(3):
        report = Report(
            id=f"report_{i}",
            name=f"Report {i+1}",
            description=f"Test report {i+1}",
            kpis=[],
            charts=[],
            filters={},
            created_at=datetime.now(),
            created_by="admin@example.com",
            format=ReportFormat.PDF
        )
        dashboard.reports[report.id] = report

        dashboard.schedule_report(
            report_id=report.id,
            name=f"Scheduled Report {i+1}",
            frequency=[ReportFrequency.DAILY, ReportFrequency.WEEKLY, ReportFrequency.MONTHLY][i],
            recipients=[f"user{i}@example.com"],
            format=ReportFormat.PDF
        )

    # List all scheduled reports
    print("📋 All Scheduled Reports:\n")
    for scheduled_id, scheduled in dashboard.report_scheduler.scheduled_reports.items():
        print(f"   • {scheduled.name}")
        print(f"     ID: {scheduled_id[:8]}...")
        print(f"     Frequency: {scheduled.frequency.value}")
        print(f"     Format: {scheduled.format.value}")
        print(f"     Next Run: {scheduled.next_run.strftime('%Y-%m-%d %H:%M')}")
        print()


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("SCHEDULED REPORTS EXAMPLES")
    print("="*70)

    examples = [
        ("1", "Basic Scheduled Report", example_1_basic_scheduled_report),
        ("2", "Multiple Format Scheduling", example_2_multiple_formats),
        ("3", "Different Frequencies", example_3_different_frequencies),
        ("4", "Scheduler Control", example_4_scheduler_control),
        ("5", "Unscheduling Reports", example_5_unschedule_report),
        ("6", "Reports with Filters", example_6_filters_and_customization),
        ("7", "List Scheduled Reports", example_7_list_scheduled_reports),
    ]

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        for num, name, func in examples:
            if num == example_num:
                func()
                return
        print(f"❌ Example {example_num} not found")
        print("\nAvailable examples:")
        for num, name, _ in examples:
            print(f"   {num}. {name}")
    else:
        # Run all examples
        for _, _, func in examples:
            try:
                func()
            except Exception as e:
                print(f"❌ Error: {e}")

        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED")
        print("="*70 + "\n")

        print("💡 TIP: Run specific example with:")
        print("   python examples/scheduled_reports_example.py <number>")
        print("\nAvailable examples:")
        for num, name, _ in examples:
            print(f"   {num}. {name}")


if __name__ == "__main__":
    main()
