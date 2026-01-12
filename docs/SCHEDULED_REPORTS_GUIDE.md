# Scheduled Reports Guide

Complete guide to using scheduled reports in the BI Dashboard.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Features](#features)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

Scheduled Reports automatically generate and email business reports on a recurring basis. This feature supports:

- **Multiple formats**: PDF, Excel, PowerPoint
- **Flexible scheduling**: Daily, weekly, monthly, quarterly
- **Email delivery**: Send to multiple recipients
- **Custom filters**: Apply filters to scheduled reports
- **Execution history**: Track all report executions

### Use Cases

1. **Executive Dashboards**: Daily/weekly KPI summaries
2. **Financial Reports**: Monthly financial statements
3. **Sales Reports**: Weekly sales performance
4. **Compliance Reports**: Quarterly regulatory reports
5. **Team Updates**: Automated team performance reports

---

## Quick Start

### 1. Create a Report

```python
from src.analytics.bi_dashboard import BIDashboard, Report, ReportFormat, KPI
from datetime import datetime

dashboard = BIDashboard()

report = Report(
    id="monthly_kpis",
    name="Monthly KPI Report",
    description="Key business metrics",
    kpis=[
        KPI(name="Revenue", value="$125K", unit="USD",
            change_percentage=8.5, trend="up"),
        KPI(name="Customers", value="450", unit="count",
            change_percentage=12.0, trend="up")
    ],
    charts=[],
    filters={},
    created_at=datetime.now(),
    created_by="admin@example.com",
    format=ReportFormat.PDF
)

dashboard.reports[report.id] = report
```

### 2. Schedule the Report

```python
from src.analytics.bi_dashboard import ReportFrequency

scheduled = dashboard.schedule_report(
    report_id="monthly_kpis",
    name="Monthly Executive Summary",
    frequency=ReportFrequency.MONTHLY,
    recipients=["ceo@example.com", "cfo@example.com"],
    format=ReportFormat.PDF
)

print(f"Report scheduled! Next run: {scheduled.next_run}")
```

### 3. Start the Scheduler

```python
# Start the background scheduler
dashboard.report_scheduler.start_scheduler()

# Scheduler runs in background thread
# Reports will be generated and emailed automatically
```

---

## Features

### Supported Frequencies

| Frequency | Description | Schedule Calculation |
|-----------|-------------|---------------------|
| `DAILY` | Every day | +1 day |
| `WEEKLY` | Every week | +7 days |
| `MONTHLY` | Every month | +30 days |
| `QUARTERLY` | Every quarter | +90 days |

### Supported Export Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| `PDF` | .pdf | Executive summaries, presentations |
| `EXCEL` | .xlsx | Data analysis, detailed tables |
| `POWERPOINT` | .pptx | Presentations, stakeholder meetings |

### Email Delivery

Reports are automatically:
- Generated in the requested format
- Attached to email
- Sent to all recipients
- Tracked in execution history

### Execution History

Every execution is tracked with:
- Execution timestamp
- Status (success/failed/partial)
- Recipients list
- Error details (if any)
- Email delivery status

---

## API Reference

### ScheduledReport Class

```python
@dataclass
class ScheduledReport:
    id: str                          # Unique ID
    report_id: str                   # ID of report to generate
    name: str                        # Display name
    frequency: ReportFrequency       # How often to run
    recipients: List[str]            # Email addresses
    format: ReportFormat             # Export format
    filters: Dict[str, Any]          # Optional filters
    enabled: bool = True             # Enable/disable
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
```

### BIDashboard.schedule_report()

Schedule a report for automatic generation.

```python
def schedule_report(
    self,
    report_id: str,
    name: str,
    frequency: ReportFrequency,
    recipients: List[str],
    format: ReportFormat,
    filters: Optional[Dict[str, Any]] = None
) -> ScheduledReport
```

**Parameters:**
- `report_id`: ID of existing report
- `name`: Display name for schedule
- `frequency`: When to run (DAILY, WEEKLY, MONTHLY, QUARTERLY)
- `recipients`: List of email addresses
- `format`: Export format (PDF, EXCEL, POWERPOINT)
- `filters`: Optional filters to apply

**Returns:**
- `ScheduledReport` object with scheduling details

**Example:**
```python
scheduled = dashboard.schedule_report(
    report_id="sales_report",
    name="Weekly Sales Summary",
    frequency=ReportFrequency.WEEKLY,
    recipients=["sales@example.com"],
    format=ReportFormat.EXCEL
)
```

### ReportScheduler.start_scheduler()

Start the background scheduler thread.

```python
scheduler = dashboard.report_scheduler
scheduler.start_scheduler()
```

### ReportScheduler.stop_scheduler()

Stop the scheduler thread.

```python
scheduler.stop_scheduler()
```

### ReportScheduler.unschedule_report()

Remove a scheduled report.

```python
scheduler.unschedule_report(report_id="schedule_id")
```

### ReportScheduler.get_execution_history()

Get execution history for a scheduled report.

```python
history = scheduler.get_execution_history(
    scheduled_report_id="schedule_id",
    limit=10
)
```

---

## Examples

### Example 1: Daily Operations Report

```python
# Daily report for operations team
dashboard.schedule_report(
    report_id="daily_ops",
    name="Daily Operations Metrics",
    frequency=ReportFrequency.DAILY,
    recipients=["ops-team@example.com"],
    format=ReportFormat.PDF
)
```

### Example 2: Weekly Sales Report (Multiple Formats)

```python
# PDF for executives
dashboard.schedule_report(
    report_id="weekly_sales",
    name="Weekly Sales (Executive PDF)",
    frequency=ReportFrequency.WEEKLY,
    recipients=["ceo@example.com"],
    format=ReportFormat.PDF
)

# Excel for analysts
dashboard.schedule_report(
    report_id="weekly_sales",
    name="Weekly Sales (Analyst Excel)",
    frequency=ReportFrequency.WEEKLY,
    recipients=["analytics@example.com"],
    format=ReportFormat.EXCEL
)

# PowerPoint for sales team
dashboard.schedule_report(
    report_id="weekly_sales",
    name="Weekly Sales (Sales PowerPoint)",
    frequency=ReportFrequency.WEEKLY,
    recipients=["sales@example.com"],
    format=ReportFormat.POWERPOINT
)
```

### Example 3: Regional Reports with Filters

```python
# North America report
dashboard.schedule_report(
    report_id="regional_sales",
    name="North America Sales Report",
    frequency=ReportFrequency.MONTHLY,
    recipients=["na-sales@example.com"],
    format=ReportFormat.EXCEL,
    filters={"region": "North America"}
)

# Europe report
dashboard.schedule_report(
    report_id="regional_sales",
    name="Europe Sales Report",
    frequency=ReportFrequency.MONTHLY,
    recipients=["eu-sales@example.com"],
    format=ReportFormat.EXCEL,
    filters={"region": "Europe"}
)
```

### Example 4: Quarterly Board Report

```python
dashboard.schedule_report(
    report_id="board_metrics",
    name="Quarterly Board Report",
    frequency=ReportFrequency.QUARTERLY,
    recipients=[
        "board@example.com",
        "investors@example.com"
    ],
    format=ReportFormat.POWERPOINT,
    filters={"level": "executive"}
)
```

### Example 5: Disable/Enable Scheduled Report

```python
# Get scheduled report
scheduler = dashboard.report_scheduler
scheduled = scheduler.scheduled_reports["schedule_id"]

# Disable temporarily
scheduled.enabled = False

# Enable again
scheduled.enabled = True
```

### Example 6: Check Execution History

```python
scheduler = dashboard.report_scheduler

# Get all executions
history = scheduler.execution_history

print(f"Total executions: {len(history)}")

# Recent executions
for execution in history[-5:]:
    print(f"Report: {execution['report_id']}")
    print(f"Status: {execution['status']}")
    print(f"Time: {execution['executed_at']}")
    print(f"Recipients: {execution['recipients']}")
    print()
```

---

## Best Practices

### 1. Choose Appropriate Frequency

- **Daily**: Operational metrics, customer support
- **Weekly**: Sales, marketing, team performance
- **Monthly**: Financial reports, HR metrics
- **Quarterly**: Board reports, strategic reviews

### 2. Format Selection

- **PDF**: Best for read-only reports, executive summaries
- **Excel**: Best for data analysis, detailed tables
- **PowerPoint**: Best for presentations, visual storytelling

### 3. Recipient Management

```python
# Group by role
executives = ["ceo@example.com", "cfo@example.com"]
analysts = ["data-team@example.com", "analytics@example.com"]
sales = ["sales-team@example.com"]

# Schedule for each group
dashboard.schedule_report(
    report_id="kpi_dashboard",
    name="Executive KPIs",
    frequency=ReportFrequency.DAILY,
    recipients=executives,
    format=ReportFormat.PDF
)
```

### 4. Error Handling

```python
# Check execution history for failures
scheduler = dashboard.report_scheduler

failed = [e for e in scheduler.execution_history if e['status'] == 'failed']

if failed:
    print(f"⚠️  {len(failed)} failed executions")
    for failure in failed:
        print(f"Report: {failure['report_id']}")
        print(f"Error: {failure.get('error', 'Unknown')}")
```

### 5. Resource Management

```python
# Start scheduler only in production
import os

if os.getenv('ENVIRONMENT') == 'production':
    scheduler.start_scheduler()
else:
    print("Scheduler not started in non-production environment")
```

### 6. Testing Schedules

```python
# Test with manual execution before scheduling
scheduled = dashboard.schedule_report(
    report_id="test_report",
    name="Test Schedule",
    frequency=ReportFrequency.DAILY,
    recipients=["test@example.com"],
    format=ReportFormat.PDF
)

# Manually execute once to test
scheduler._execute_scheduled_report(scheduled)

# Check execution was successful
latest = scheduler.execution_history[-1]
assert latest['status'] == 'success', "Test execution failed"

# Then start scheduler
scheduler.start_scheduler()
```

---

## Troubleshooting

### Reports Not Being Sent

**Problem**: Scheduled reports are not being generated/sent.

**Solutions**:

1. **Check scheduler is running**:
   ```python
   assert scheduler._running, "Scheduler is not running"
   ```

2. **Check next_run time**:
   ```python
   for s in scheduler.scheduled_reports.values():
       print(f"{s.name}: Next run {s.next_run}")
   ```

3. **Check enabled status**:
   ```python
   for s in scheduler.scheduled_reports.values():
       if not s.enabled:
           print(f"⚠️  {s.name} is disabled")
   ```

### Email Delivery Failures

**Problem**: Reports are generated but emails aren't sent.

**Solutions**:

1. **Check email configuration**:
   ```python
   from src.core.email_notifier import get_notifier

   notifier = get_notifier()
   # Verify SMTP settings
   ```

2. **Check execution history**:
   ```python
   for execution in scheduler.execution_history:
       if execution.get('email_sent') == False:
           print(f"Email failed: {execution.get('email_error')}")
   ```

### Report Generation Errors

**Problem**: Report generation fails.

**Solutions**:

1. **Check report exists**:
   ```python
   report_id = scheduled.report_id
   assert report_id in dashboard.reports, f"Report {report_id} not found"
   ```

2. **Check format support**:
   ```python
   # Ensure required libraries are installed
   # PDF: weasyprint
   # Excel: openpyxl
   # PowerPoint: python-pptx
   ```

3. **Review execution errors**:
   ```python
   failures = [e for e in scheduler.execution_history if e['status'] == 'failed']
   for f in failures:
       print(f"Error: {f.get('error')}")
   ```

### Memory Issues

**Problem**: Scheduler consuming too much memory.

**Solutions**:

1. **Limit execution history**:
   ```python
   # Keep only last 100 executions
   scheduler.execution_history = scheduler.execution_history[-100:]
   ```

2. **Stop scheduler when not needed**:
   ```python
   scheduler.stop_scheduler()
   ```

### Timezone Issues

**Problem**: Reports running at wrong times.

**Solutions**:

1. **Use timezone-aware datetimes**:
   ```python
   from datetime import datetime, timezone

   now = datetime.now(timezone.utc)
   ```

2. **Configure system timezone**:
   ```bash
   export TZ="America/New_York"
   ```

---

## Configuration

### Email Settings

Configure email in `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=reports@example.com
```

### Scheduler Settings

Configure scheduler behavior:

```python
# Custom check interval (default: 60 seconds)
import time

def custom_scheduler_loop(self):
    while self._running:
        # Your scheduling logic
        time.sleep(30)  # Check every 30 seconds

# Replace scheduler loop
scheduler._scheduler_loop = custom_scheduler_loop
```

---

## Performance Tips

### 1. Batch Report Generation

For multiple reports, generate in batches:

```python
# Group reports by frequency
daily_reports = [s for s in scheduler.scheduled_reports.values()
                 if s.frequency == ReportFrequency.DAILY]

# Generate all daily reports at once (e.g., 6am)
```

### 2. Async Report Generation

For large reports, consider async generation:

```python
import asyncio

async def generate_report_async(report):
    # Generate report asynchronously
    pass
```

### 3. Caching

Cache report data to speed up generation:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_report_data(report_id, date):
    # Fetch and cache report data
    pass
```

---

## Integration

### With CI/CD

```yaml
# .github/workflows/scheduled-reports.yml
name: Test Scheduled Reports

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run scheduled reports tests
        run: |
          python -m pytest tests/unit/analytics/test_scheduled_reports.py
```

### With Docker

```dockerfile
# Start scheduler in Docker container
CMD ["python", "-c", "from src.analytics.bi_dashboard import BIDashboard; \
     dashboard = BIDashboard(); \
     dashboard.report_scheduler.start_scheduler(); \
     import time; time.sleep(86400)"]
```

---

## Summary

Scheduled Reports provide:
- ✅ Automatic report generation
- ✅ Email delivery
- ✅ Multiple formats (PDF, Excel, PowerPoint)
- ✅ Flexible scheduling (daily, weekly, monthly, quarterly)
- ✅ Execution history and error tracking
- ✅ Custom filters and customization
- ✅ Production-ready implementation

For more examples, see: `examples/scheduled_reports_example.py`

For tests, see: `tests/unit/analytics/test_scheduled_reports.py`

---

**Related Documentation:**
- [BI Dashboard Guide](./BI_DASHBOARD_GUIDE.md)
- [Report Builder Guide](./REPORT_BUILDER_GUIDE.md)
- [Email Notifications](./EMAIL_NOTIFICATIONS.md)
