# Analytics & Business Intelligence (v3.1) - Complete Guide

**Version:** 3.1.0
**Release Date:** January 2026
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Key Features](#key-features)
4. [Quick Start](#quick-start)
5. [Dashboard Guide](#dashboard-guide)
6. [KPI Metrics](#kpi-metrics)
7. [API Reference](#api-reference)
8. [Predictive Analytics](#predictive-analytics)
9. [Data Warehouse](#data-warehouse)
10. [OLAP Cube](#olap-cube)
11. [Data Mining](#data-mining)
12. [Natural Language Queries](#natural-language-queries)
13. [Streaming Analytics](#streaming-analytics)
14. [Reports & Exports](#reports-exports)
15. [Best Practices](#best-practices)
16. [Troubleshooting](#troubleshooting)

---

## Overview

The Analytics & BI module provides comprehensive business intelligence capabilities for enterprise customers. It includes real-time dashboards, predictive analytics, data warehousing, and advanced analytics features.

### What's New in v3.1

- ✅ **Executive BI Dashboard** with 6 core KPIs
- ✅ **Predictive Analytics Engine** (revenue forecasting, churn prediction)
- ✅ **Data Warehouse** with star schema and ETL pipelines
- ✅ **OLAP Cube Engine** for multidimensional analysis
- ✅ **Data Mining** capabilities (pattern discovery, clustering)
- ✅ **Real-time Streaming Analytics** with Kafka integration
- ✅ **Natural Language Query** interface
- ✅ **Automated Report Scheduling** (daily, weekly, monthly, quarterly)
- ✅ **Multi-format Export** (PDF, Excel, PowerPoint, JSON, CSV)

### Business Value

- **Faster Decision Making**: Real-time insights and KPIs
- **Revenue Optimization**: Predictive analytics for forecasting
- **Customer Retention**: Churn prediction and prevention
- **Operational Efficiency**: Automated reporting and analytics
- **Data-Driven Culture**: Self-service analytics for all teams

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BI Dashboard UI                       │
│  (Web Interface + Charts.js Visualizations)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                REST API Layer                            │
│  (/api/v1/analytics/*)                                  │
└────┬────────┬────────┬────────┬────────┬───────────────┘
     │        │        │        │        │
     ↓        ↓        ↓        ↓        ↓
┌─────────┐ ┌──────┐ ┌────────┐ ┌─────┐ ┌────────┐
│   BI    │ │Predict│ │  Data  │ │OLAP │ │ Data   │
│Dashboard│ │Analytics│ │Warehouse│ │Cube │ │ Mining │
└─────────┘ └──────┘ └────────┘ └─────┘ └────────┘
     │        │        │        │        │
     └────────┴────────┴────────┴────────┘
                      │
                      ↓
            ┌──────────────────┐
            │   PostgreSQL     │
            │  Data Warehouse  │
            └──────────────────┘
```

### Component Details

#### Frontend Layer
- **HTML Templates**: `/web/templates/bi/dashboard.html`
- **JavaScript**: `/web/static/js/bi/bi-charts.js`, `dashboard.js`
- **CSS**: `/web/static/css/bi/dashboard.css`
- **Framework**: Chart.js 4.4.0 for visualizations

#### Backend Layer
- **API Module**: `src/api_analytics.py` (18 endpoints)
- **BI Dashboard**: `src/analytics/bi_dashboard.py` (1353 lines)
- **Predictive Analytics**: `src/analytics/predictive_analytics.py` (840 lines)
- **Data Warehouse**: `src/analytics/data_warehouse.py` (654 lines)
- **OLAP Cube**: `src/analytics/olap_cube.py` (557 lines)
- **Data Mining**: `src/analytics/data_mining.py` (303 lines)
- **Streaming Analytics**: `src/analytics/streaming_analytics.py` (646 lines)
- **NL Query**: `src/analytics/nl_query.py` (603 lines)

#### Data Layer
- **Operational Database**: SQLite/PostgreSQL for transactional data
- **Data Warehouse**: PostgreSQL with star schema
- **Cache Layer**: Redis for real-time metrics
- **Event Stream**: Kafka for streaming analytics

---

## Key Features

### 1. Executive Dashboard

**Real-time KPI Monitoring**
- 6 Core KPIs: MRR, ARR, Churn Rate, CLV, NRR, CAC
- Interactive charts with drill-down capabilities
- Customizable widgets and layouts
- Auto-refresh (configurable interval)

**Visualizations**
- Revenue Trend (Line Chart)
- Revenue Breakdown (Pie Chart)
- Customer Growth (Bar Chart)
- Churn Analysis (Multi-axis Line Chart)
- Cohort Analysis (Heatmap)

### 2. Predictive Analytics

**Revenue Forecasting**
- ARIMA time series forecasting
- Prophet for trend analysis
- LSTM for complex patterns
- 85%+ forecast accuracy (MAPE < 15%)

**Churn Prediction**
- Machine learning models
- Feature engineering (20+ features)
- 70%+ prediction precision
- Early warning system

### 3. Data Warehouse

**Star Schema Design**
- Fact Tables: document_facts, usage_facts, revenue_facts
- Dimension Tables: dim_users, dim_tenants, dim_time, dim_documents
- SCD Type 2 for historical tracking

**ETL Pipelines**
- Incremental and full loads
- Data quality checks
- Materialized views for performance
- <30 minute ETL runtime

### 4. OLAP Cube

**Multidimensional Analysis**
- Slice & dice operations
- Roll-up & drill-down
- Pivot table functionality
- MDX query support

**Performance**
- Cube build time: <5 minutes
- Query response: <1s (cached)
- 10+ dimension support
- 1M+ fact handling

### 5. Data Mining

**Pattern Discovery**
- Apriori algorithm for association rules
- FP-Growth optimization
- Market basket analysis
- Customer segmentation

**Clustering**
- K-means clustering
- DBSCAN (density-based)
- Hierarchical clustering
- 80%+ clustering accuracy

### 6. Real-time Streaming

**Event Processing**
- Kafka integration
- Stream processing framework
- Windowing operations (tumbling, sliding, session)
- Complex event processing

**Performance**
- Processing latency: <100ms (p95)
- Throughput: >10k events/second
- Zero data loss guarantee
- Auto-recovery from failures

### 7. Natural Language Queries

**Text-to-SQL**
- Intent recognition
- Entity extraction
- Query generation and validation
- 85%+ query accuracy

**Capabilities**
- 50+ supported query patterns
- Multi-language support (3 languages)
- Response time: <2s
- Natural language responses

---

## Quick Start

### 1. Access the Dashboard

Navigate to: `http://localhost:5000/bi/dashboard`

Or use the API:
```bash
curl http://localhost:5000/api/v1/analytics/dashboard
```

### 2. Basic Dashboard Usage

```python
from src.analytics.bi_dashboard import BIDashboard
from datetime import datetime, timedelta

# Initialize dashboard
dashboard = BIDashboard()

# Create executive dashboard
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

dashboard_data = dashboard.create_executive_dashboard(
    tenant_id='your_tenant_id',
    date_range=(start_date, end_date)
)

print(dashboard_data)
```

### 3. API Examples

**Get Dashboard Data:**
```bash
curl -X GET "http://localhost:5000/api/v1/analytics/dashboard?dateRange=30&tenant=all"
```

**Get Specific KPI:**
```bash
curl -X GET "http://localhost:5000/api/v1/analytics/kpi/mrr"
```

**Predict Revenue:**
```bash
curl -X POST "http://localhost:5000/api/v1/analytics/predict/revenue" \
  -H "Content-Type: application/json" \
  -d '{"months": 3, "model": "arima"}'
```

**Natural Language Query:**
```bash
curl -X POST "http://localhost:5000/api/v1/analytics/query/natural" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me revenue for last month"}'
```

---

## Dashboard Guide

### Using the Web Interface

#### 1. Filters Panel

**Date Range Selection:**
- Last 7 Days
- Last 30 Days (default)
- Last 90 Days
- Last 6 Months
- Last Year
- Custom Range

**Tenant Filter:**
- All Tenants (default)
- Select specific tenant

**Comparison Period:**
- Previous Period (default)
- Same Period Last Year
- No Comparison

#### 2. KPI Cards

Each KPI card displays:
- **Current Value**: Large, prominent number
- **Trend Indicator**: ↑ (up), ↓ (down), → (stable)
- **Change Percentage**: vs comparison period
- **Hover**: Additional details and context

**Color Coding:**
- Blue: Primary metrics (MRR, ARR)
- Green: Positive metrics (CLV, NRR)
- Red: Warning metrics (Churn)
- Orange: Cost metrics (CAC)

#### 3. Charts

**Interactions:**
- **Hover**: View detailed data points
- **Click Legend**: Toggle dataset visibility
- **Download**: Export chart as PNG
- **Fullscreen**: Expand chart for detailed view

**Available Charts:**
1. Revenue Trend (Line) - MRR over time
2. Revenue Breakdown (Pie) - By plan type
3. Customer Growth (Bar) - New, churned, net growth
4. Churn Analysis (Multi-axis) - Churn rate vs total customers
5. Cohort Analysis (Heatmap) - Retention by cohort

#### 4. Export Options

**Formats:**
- PDF: Complete report with charts
- Excel: Data tables and summaries
- PowerPoint: Presentation-ready slides
- JSON: Raw data for integration
- CSV: Data for spreadsheet analysis

**Include Options:**
- KPI Metrics
- Charts
- Raw Data

#### 5. Customization

**Dashboard Layout:**
- Drag & drop widgets
- Resize widgets
- Show/hide specific KPIs
- Save custom layouts

**Auto-Refresh:**
- Default: 5 minutes
- Manual refresh available
- Real-time updates via WebSocket (optional)

---

## KPI Metrics

### 1. MRR (Monthly Recurring Revenue)

**Definition:**
Total predictable revenue generated per month from active subscriptions.

**Calculation:**
```python
MRR = Σ(Monthly Subscriptions) + Σ(Yearly Subscriptions / 12)
```

**Formula in Code:**
```python
mrr = calculator.calculate_mrr(subscriptions)
```

**What's Included:**
- Active monthly subscriptions
- Annual subscriptions (normalized to monthly)

**What's Excluded:**
- One-time fees
- Canceled subscriptions
- Trial accounts

**Target:** Typically 10-30% month-over-month growth

---

### 2. ARR (Annual Recurring Revenue)

**Definition:**
Annualized version of MRR, representing yearly revenue run rate.

**Calculation:**
```python
ARR = MRR × 12
```

**Formula in Code:**
```python
arr = calculator.calculate_arr(mrr)
```

**Use Cases:**
- Investor reporting
- Valuation calculations
- Long-term planning

**Target:** 10x-100x annual growth for early stage, 30-50% for mature

---

### 3. Churn Rate

**Definition:**
Percentage of customers who cancel their subscription in a given period.

**Calculation:**
```python
Churn Rate = (Churned Customers / Total Customers at Start) × 100
```

**Formula in Code:**
```python
churn_rate = calculator.calculate_churn_rate(
    churned_customers=50,
    total_customers_start=1000,
    period_days=30
)
```

**Types:**
- **Customer Churn**: Percentage of customers lost
- **Revenue Churn**: Percentage of revenue lost
- **Net Churn**: Includes expansion revenue

**Target:**
- SaaS: <5% monthly, <60% annual
- Enterprise: <2% monthly, <20% annual

---

### 4. CLV (Customer Lifetime Value)

**Definition:**
Total revenue expected from a customer over their entire relationship.

**Calculation:**
```python
CLV = ARPU × Avg Customer Lifespan (months) × Gross Margin
```

**Formula in Code:**
```python
clv = calculator.calculate_clv(
    avg_revenue_per_user=Decimal('100'),
    avg_customer_lifespan_months=24,
    gross_margin=0.8
)
```

**Components:**
- **ARPU**: Average revenue per user per month
- **Lifespan**: Average months customer stays
- **Gross Margin**: Typically 70-90% for SaaS

**Target:** CLV should be 3x-5x CAC

---

### 5. NRR (Net Revenue Retention)

**Definition:**
Percentage of recurring revenue retained from existing customers, including expansions.

**Calculation:**
```python
NRR = ((Revenue Start + Expansion - Churn) / Revenue Start) × 100
```

**Formula in Code:**
```python
nrr = calculator.calculate_nrr(
    revenue_start=Decimal('10000'),
    expansion_revenue=Decimal('2000'),
    churned_revenue=Decimal('1000')
)
```

**Interpretation:**
- **>100%**: Revenue growing from existing customers
- **100%**: Breaking even (churn = expansion)
- **<100%**: Losing revenue from existing customers

**Target:**
- Good: >100%
- Great: >110%
- Excellent: >120%

---

### 6. CAC (Customer Acquisition Cost)

**Definition:**
Average cost to acquire a new customer.

**Calculation:**
```python
CAC = Total Sales & Marketing Costs / New Customers Acquired
```

**Formula in Code:**
```python
cac = calculator.calculate_cac(
    sales_marketing_costs=Decimal('50000'),
    new_customers=100
)
```

**Components:**
- Sales team salaries
- Marketing spend
- Tools and software
- Advertising costs

**Target:**
- CLV/CAC ratio: >3
- Payback period: <12 months

---

## API Reference

### Base URL

```
http://localhost:5000/api/v1/analytics
```

### Authentication

Include your API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

#### 1. Dashboard

**GET /dashboard**

Get complete dashboard data with KPIs and charts.

**Query Parameters:**
- `dateRange` (int): Number of days (default: 30)
- `tenant` (string): Tenant ID or 'all' (default: 'all')
- `comparisonPeriod` (string): 'previous', 'year_ago', 'none' (default: 'previous')

**Response:**
```json
{
  "success": true,
  "kpis": {
    "mrr": {
      "value": 122000,
      "unit": "EUR",
      "change": 3.4,
      "trend": "up"
    },
    "arr": {...},
    "churn": {...},
    "clv": {...},
    "nrr": {...},
    "cac": {...}
  },
  "charts": {...},
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 2. KPI Endpoints

**GET /kpi/{kpi_name}**

Get specific KPI value.

**KPI Names:** `mrr`, `arr`, `churn`, `clv`, `nrr`, `cac`

**Response:**
```json
{
  "success": true,
  "kpi": "mrr",
  "value": 122000,
  "unit": "EUR",
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 3. Predictive Analytics

**POST /predict/revenue**

Forecast future revenue.

**Request Body:**
```json
{
  "months": 3,
  "model": "arima"
}
```

**Response:**
```json
{
  "success": true,
  "forecast": [
    {"month": 1, "value": 125000, "confidence_low": 120000, "confidence_high": 130000},
    {"month": 2, "value": 128000, "confidence_low": 122000, "confidence_high": 134000},
    {"month": 3, "value": 131000, "confidence_low": 124000, "confidence_high": 138000}
  ],
  "model": "arima",
  "timestamp": "2026-01-16T12:00:00"
}
```

**POST /predict/churn**

Predict customer churn probability.

**Request Body:**
```json
{
  "customer_ids": ["cust_1", "cust_2"]
}
```

**Response:**
```json
{
  "success": true,
  "predictions": [
    {"customer_id": "cust_1", "churn_probability": 0.15, "risk_level": "low"},
    {"customer_id": "cust_2", "churn_probability": 0.75, "risk_level": "high"}
  ],
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 4. Data Warehouse

**POST /warehouse/etl**

Trigger ETL pipeline.

**Request Body:**
```json
{
  "incremental": true
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "etl_123456",
  "status": "started",
  "timestamp": "2026-01-16T12:00:00"
}
```

**GET /warehouse/status**

Get data warehouse status.

**Response:**
```json
{
  "success": true,
  "status": {
    "last_etl_run": "2026-01-16T11:00:00",
    "next_scheduled_run": "2026-01-16T13:00:00",
    "fact_table_rows": 1500000,
    "data_freshness_minutes": 15
  },
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 5. OLAP Cube

**POST /olap/query**

Execute OLAP query.

**Request Body:**
```json
{
  "dimensions": ["region", "product"],
  "measures": ["revenue", "units"],
  "filters": {
    "date": "2024-01"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "data": [[...], [...]],
    "dimensions": ["region", "product"],
    "measures": ["revenue", "units"]
  },
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 6. Data Mining

**POST /mining/patterns**

Discover data patterns.

**Request Body:**
```json
{
  "algorithm": "apriori",
  "min_support": 0.3
}
```

**Response:**
```json
{
  "success": true,
  "patterns": [
    {
      "items": ["product_a", "product_b"],
      "support": 0.45,
      "confidence": 0.85,
      "lift": 2.3
    }
  ],
  "algorithm": "apriori",
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 7. Natural Language Query

**POST /query/natural**

Execute natural language query.

**Request Body:**
```json
{
  "query": "Show me revenue for last month"
}
```

**Response:**
```json
{
  "success": true,
  "query": "Show me revenue for last month",
  "sql": "SELECT SUM(revenue) FROM revenue_facts WHERE date >= '2025-12-01' AND date < '2026-01-01'",
  "result": [
    {"revenue": 122000}
  ],
  "timestamp": "2026-01-16T12:00:00"
}
```

#### 8. Export

**POST /export**

Export dashboard to various formats.

**Request Body:**
```json
{
  "format": "pdf",
  "include": {
    "kpis": true,
    "charts": true,
    "rawData": false
  },
  "filters": {
    "dateRange": 30
  }
}
```

**Response:** Binary file download

#### 9. Scheduled Reports

**POST /reports/schedule**

Schedule recurring report.

**Request Body:**
```json
{
  "name": "Weekly Executive Report",
  "frequency": "weekly",
  "format": "pdf",
  "recipients": ["exec@example.com"]
}
```

**Response:**
```json
{
  "success": true,
  "report_id": "report_123456",
  "message": "Report scheduled successfully",
  "timestamp": "2026-01-16T12:00:00"
}
```

**GET /reports/scheduled**

List all scheduled reports.

**Response:**
```json
{
  "success": true,
  "reports": [
    {
      "id": "report_123456",
      "name": "Weekly Executive Report",
      "frequency": "weekly",
      "format": "pdf",
      "next_run": "2026-01-23T09:00:00"
    }
  ],
  "count": 1,
  "timestamp": "2026-01-16T12:00:00"
}
```

---

## Best Practices

### 1. Performance Optimization

**Dashboard Loading:**
- Use date range filters to limit data
- Enable caching for frequently accessed data
- Implement pagination for large datasets
- Use materialized views for complex queries

**API Usage:**
- Use appropriate date ranges
- Implement rate limiting
- Cache responses client-side
- Use compression for large payloads

### 2. Data Quality

**ETL Pipeline:**
- Schedule ETL during off-peak hours
- Monitor data quality metrics
- Implement data validation rules
- Set up alerts for data anomalies

**KPI Calculations:**
- Validate input data before calculation
- Handle edge cases (zero division, null values)
- Use appropriate data types (Decimal for money)
- Log calculation errors

### 3. Security

**API Security:**
- Use HTTPS for all API calls
- Implement proper authentication
- Validate and sanitize all inputs
- Use rate limiting to prevent abuse

**Data Access:**
- Implement role-based access control
- Log all data access
- Encrypt sensitive data
- Regular security audits

### 4. Monitoring

**Key Metrics:**
- Dashboard load time (<2s target)
- API response time (<500ms target)
- ETL pipeline duration (<30min target)
- Data freshness (<5min target)

**Alerts:**
- ETL pipeline failures
- API error rate >1%
- Data quality issues
- Performance degradation

---

## Troubleshooting

### Common Issues

#### 1. Dashboard Not Loading

**Symptoms:** Blank page or loading spinner

**Solutions:**
- Check browser console for JavaScript errors
- Verify API endpoint is accessible
- Check network tab for failed requests
- Clear browser cache

#### 2. Incorrect KPI Values

**Symptoms:** KPIs showing unexpected values

**Solutions:**
- Verify date range filters
- Check tenant filter settings
- Validate input data quality
- Review calculation logic

#### 3. Slow Dashboard Performance

**Symptoms:** Dashboard takes >5s to load

**Solutions:**
- Reduce date range
- Enable caching
- Optimize database queries
- Add database indexes

#### 4. ETL Pipeline Failures

**Symptoms:** Data warehouse not updating

**Solutions:**
- Check ETL job logs
- Verify database connectivity
- Validate source data format
- Check disk space

#### 5. API Rate Limit Errors

**Symptoms:** 429 Too Many Requests

**Solutions:**
- Implement exponential backoff
- Reduce request frequency
- Use caching
- Contact support for higher limits

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- **Documentation:** https://docs.example.com/analytics
- **Support Email:** support@example.com
- **GitHub Issues:** https://github.com/example/dms/issues
- **Community Forum:** https://community.example.com

---

## Appendix

### A. Glossary

- **ARIMA**: AutoRegressive Integrated Moving Average (forecasting model)
- **CAC**: Customer Acquisition Cost
- **CLV**: Customer Lifetime Value
- **CQRS**: Command Query Responsibility Segregation
- **ETL**: Extract, Transform, Load
- **MDX**: Multidimensional Expressions (query language)
- **NRR**: Net Revenue Retention
- **OLAP**: Online Analytical Processing
- **SCD**: Slowly Changing Dimension

### B. Supported Browsers

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### C. Database Requirements

- PostgreSQL 12+ (recommended)
- SQLite 3.35+ (development only)
- Redis 6+ (for caching)
- Kafka 2.8+ (for streaming)

### D. License

Copyright © 2026 Your Company. All rights reserved.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Contributors:** Engineering Team
