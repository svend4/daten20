#!/usr/bin/env python3
"""
Unit Tests for Scheduled Reports Feature

Tests the scheduled report functionality including:
- Report scheduling
- Frequency calculations
- Scheduler control
- Email delivery simulation
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.analytics.bi_dashboard import (
    KPI,
    BIDashboard,
    Report,
    ReportFormat,
    ReportFrequency,
    ReportScheduler,
    ScheduledReport,
)


class TestScheduledReports(unittest.TestCase):
    """Test scheduled reports functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.dashboard = BIDashboard()
        self.scheduler = ReportScheduler(parent_dashboard=self.dashboard)

        # Create sample report
        self.sample_report = Report(
            id="test_report",
            name="Test Report",
            description="Test report for scheduling",
            kpis=[KPI(name="Test KPI", value="100", unit="units", change_percentage=5.0, trend="up")],
            charts=[],
            filters={},
            created_at=datetime.now(),
            created_by="test@example.com",
            format=ReportFormat.PDF,
        )
        self.dashboard.reports[self.sample_report.id] = self.sample_report

    def test_schedule_report_creation(self):
        """Test creating a scheduled report"""
        scheduled = ScheduledReport(
            id="test_schedule_1",
            report_id=self.sample_report.id,
            name="Test Scheduled Report",
            frequency=ReportFrequency.DAILY,
            recipients=["test@example.com"],
            format=ReportFormat.PDF,
            filters={},
        )

        self.assertEqual(scheduled.report_id, self.sample_report.id)
        self.assertEqual(scheduled.frequency, ReportFrequency.DAILY)
        self.assertEqual(len(scheduled.recipients), 1)
        self.assertEqual(scheduled.format, ReportFormat.PDF)

    def test_calculate_next_run_daily(self):
        """Test daily frequency calculation"""
        now = datetime.now()
        next_run = self.scheduler._calculate_next_run(ReportFrequency.DAILY, from_time=now)

        expected = now + timedelta(days=1)
        self.assertAlmostEqual(next_run.timestamp(), expected.timestamp(), delta=1)  # 1 second tolerance

    def test_calculate_next_run_weekly(self):
        """Test weekly frequency calculation"""
        now = datetime.now()
        next_run = self.scheduler._calculate_next_run(ReportFrequency.WEEKLY, from_time=now)

        expected = now + timedelta(weeks=1)
        self.assertAlmostEqual(next_run.timestamp(), expected.timestamp(), delta=1)

    def test_calculate_next_run_monthly(self):
        """Test monthly frequency calculation"""
        now = datetime.now()
        next_run = self.scheduler._calculate_next_run(ReportFrequency.MONTHLY, from_time=now)

        expected = now + timedelta(days=30)
        self.assertAlmostEqual(next_run.timestamp(), expected.timestamp(), delta=1)

    def test_calculate_next_run_quarterly(self):
        """Test quarterly frequency calculation"""
        now = datetime.now()
        next_run = self.scheduler._calculate_next_run(ReportFrequency.QUARTERLY, from_time=now)

        expected = now + timedelta(days=90)
        self.assertAlmostEqual(next_run.timestamp(), expected.timestamp(), delta=1)

    def test_schedule_report(self):
        """Test scheduling a report"""
        scheduled = ScheduledReport(
            id="test_schedule_2",
            report_id=self.sample_report.id,
            name="Test Schedule",
            frequency=ReportFrequency.DAILY,
            recipients=["user@example.com"],
            format=ReportFormat.PDF,
            filters={},
        )

        self.scheduler.schedule_report(scheduled)

        self.assertIn(scheduled.id, self.scheduler.scheduled_reports)
        self.assertIsNotNone(scheduled.next_run)

    def test_unschedule_report(self):
        """Test unscheduling a report"""
        scheduled = ScheduledReport(
            id="test_schedule_3",
            report_id=self.sample_report.id,
            name="Test Schedule",
            frequency=ReportFrequency.DAILY,
            recipients=["user@example.com"],
            format=ReportFormat.PDF,
            filters={},
        )

        self.scheduler.schedule_report(scheduled)
        self.assertIn(scheduled.id, self.scheduler.scheduled_reports)

        self.scheduler.unschedule_report(scheduled.id)
        self.assertNotIn(scheduled.id, self.scheduler.scheduled_reports)

    def test_scheduler_start_stop(self):
        """Test starting and stopping the scheduler"""
        self.assertFalse(self.scheduler._running)

        self.scheduler.start_scheduler()
        self.assertTrue(self.scheduler._running)
        self.assertIsNotNone(self.scheduler._thread)

        self.scheduler.stop_scheduler()
        self.assertFalse(self.scheduler._running)

    def test_multiple_scheduled_reports(self):
        """Test scheduling multiple reports"""
        frequencies = [ReportFrequency.DAILY, ReportFrequency.WEEKLY, ReportFrequency.MONTHLY]

        for i, freq in enumerate(frequencies):
            scheduled = ScheduledReport(
                id=f"test_schedule_{i}",
                report_id=self.sample_report.id,
                name=f"Test Schedule {i}",
                frequency=freq,
                recipients=[f"user{i}@example.com"],
                format=ReportFormat.PDF,
                filters={},
            )
            self.scheduler.schedule_report(scheduled)

        self.assertEqual(len(self.scheduler.scheduled_reports), 3)

    def test_scheduled_report_with_filters(self):
        """Test scheduled report with custom filters"""
        filters = {"region": "North America", "product": "Enterprise"}

        scheduled = ScheduledReport(
            id="filtered_schedule",
            report_id=self.sample_report.id,
            name="Filtered Report",
            frequency=ReportFrequency.WEEKLY,
            recipients=["analyst@example.com"],
            format=ReportFormat.EXCEL,
            filters=filters,
        )

        self.assertEqual(scheduled.filters, filters)
        self.assertEqual(scheduled.format, ReportFormat.EXCEL)

    def test_execution_history_tracking(self):
        """Test that execution history is tracked"""
        initial_count = len(self.scheduler.execution_history)

        # Create scheduled report
        scheduled = ScheduledReport(
            id="history_test",
            report_id=self.sample_report.id,
            name="History Test",
            frequency=ReportFrequency.DAILY,
            recipients=["test@example.com"],
            format=ReportFormat.PDF,
            filters={},
        )
        scheduled.next_run = datetime.now() - timedelta(minutes=1)  # Set to past

        self.scheduler.schedule_report(scheduled)

        # Manually trigger execution (without email)
        self.scheduler._execute_scheduled_report(scheduled)

        # Check history was recorded
        self.assertGreater(len(self.scheduler.execution_history), initial_count)

    def test_dashboard_schedule_integration(self):
        """Test scheduling through dashboard interface"""
        scheduled = self.dashboard.schedule_report(
            report_id=self.sample_report.id,
            name="Dashboard Integration Test",
            frequency=ReportFrequency.WEEKLY,
            recipients=["integration@example.com"],
            format=ReportFormat.PDF,
        )

        self.assertIsNotNone(scheduled)
        self.assertEqual(scheduled.report_id, self.sample_report.id)
        self.assertIn(scheduled.id, self.dashboard.report_scheduler.scheduled_reports)

    def test_multiple_formats_same_report(self):
        """Test scheduling same report in different formats"""
        formats = [ReportFormat.PDF, ReportFormat.EXCEL, ReportFormat.POWERPOINT]

        for fmt in formats:
            scheduled = self.dashboard.schedule_report(
                report_id=self.sample_report.id,
                name=f"Test {fmt.value} Report",
                frequency=ReportFrequency.MONTHLY,
                recipients=[f"{fmt.value}@example.com"],
                format=fmt,
            )
            self.assertEqual(scheduled.format, fmt)

        # All 3 should be scheduled
        self.assertEqual(len(self.dashboard.report_scheduler.scheduled_reports), 3)

    @patch("src.analytics.bi_dashboard.ReportGenerator")
    def test_report_generation_called(self, mock_generator):
        """Test that report generation is called during execution"""
        # This is a simplified test - full integration would need email mocking
        scheduled = ScheduledReport(
            id="generation_test",
            report_id=self.sample_report.id,
            name="Generation Test",
            frequency=ReportFrequency.DAILY,
            recipients=["test@example.com"],
            format=ReportFormat.PDF,
            filters={},
        )

        # Execute the scheduled report
        # Note: This will fail gracefully without actual email setup
        self.scheduler._execute_scheduled_report(scheduled)

        # Check that execution was attempted (history recorded)
        self.assertGreater(len(self.scheduler.execution_history), 0)


class TestScheduledReportIntegration(unittest.TestCase):
    """Integration tests for scheduled reports"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.dashboard = BIDashboard()

    def test_end_to_end_scheduling(self):
        """Test complete scheduling workflow"""
        # 1. Create report
        report = Report(
            id="integration_report",
            name="Integration Test Report",
            description="E2E test report",
            kpis=[KPI(name="Revenue", value="$50,000", unit="USD", change_percentage=10.0, trend="up")],
            charts=[],
            filters={},
            created_at=datetime.now(),
            created_by="test@example.com",
            format=ReportFormat.PDF,
        )
        self.dashboard.reports[report.id] = report

        # 2. Schedule report
        scheduled = self.dashboard.schedule_report(
            report_id=report.id,
            name="E2E Scheduled Report",
            frequency=ReportFrequency.WEEKLY,
            recipients=["recipient@example.com"],
            format=ReportFormat.PDF,
        )

        # 3. Verify scheduling
        self.assertIsNotNone(scheduled)
        self.assertIsNotNone(scheduled.next_run)

        # 4. Verify it's in scheduler
        self.assertIn(scheduled.id, self.dashboard.report_scheduler.scheduled_reports)

        # 5. Unschedule
        self.dashboard.report_scheduler.unschedule_report(scheduled.id)
        self.assertNotIn(scheduled.id, self.dashboard.report_scheduler.scheduled_reports)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestScheduledReports))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduledReportIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
