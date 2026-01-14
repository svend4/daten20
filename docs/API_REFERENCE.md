# 🔌 API REFERENCE - daten20 Platform

**Version:** 1.0.0
**Base URL:** `http://localhost:8080/api/v1`
**Authentication:** Bearer JWT Token
**Content-Type:** `application/json`

---

## 📋 TABLE OF CONTENTS

1. [Authentication](#authentication)
2. [Variant A: Analytics & BI](#variant-a-analytics--bi)
3. [Variant B: Service Management](#variant-b-service-management)
4. [Variant C: Dashboard](#variant-c-dashboard)
5. [Error Responses](#error-responses)
6. [Rate Limiting](#rate-limiting)

---

## 🔐 AUTHENTICATION

### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization_id": "ORG-001" // optional
}
```

**Response:** `201 Created`
```json
{
  "id": "USR-12345",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2026-01-14T10:30:00Z"
}
```

---

### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900, // 15 minutes
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "USR-12345",
    "email": "user@example.com",
    "role": "user"
  }
}
```

---

### Refresh Token

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### Get Current User

```http
GET /auth/me
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "id": "USR-12345",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "organization_id": "ORG-001",
  "created_at": "2025-12-01T10:00:00Z",
  "last_login": "2026-01-14T10:30:00Z"
}
```

---

## 📊 VARIANT A: ANALYTICS & BI

Base Path: `/analytics`

### KPIs

#### Get MRR (Monthly Recurring Revenue)

```http
GET /analytics/kpi/mrr
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `date` (optional): YYYY-MM-DD format, defaults to today

**Response:** `200 OK`
```json
{
  "metric": "MRR",
  "value": 125000.50,
  "currency": "EUR",
  "date": "2026-01-31",
  "change_percentage": 5.2,
  "trend": "up"
}
```

---

#### Get ARR (Annual Recurring Revenue)

```http
GET /analytics/kpi/arr
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "metric": "ARR",
  "value": 1500000.00,
  "currency": "EUR",
  "date": "2026-01-14",
  "mrr_based": true
}
```

---

#### Get Churn Rate

```http
GET /analytics/kpi/churn-rate
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date`: YYYY-MM-DD (required)
- `end_date`: YYYY-MM-DD (required)

**Response:** `200 OK`
```json
{
  "metric": "Churn Rate",
  "value": 3.5,
  "unit": "percentage",
  "period": {
    "start": "2025-12-01",
    "end": "2026-01-14"
  },
  "customers_lost": 28,
  "customers_start": 800
}
```

---

#### Get Customer Lifetime Value (CLV)

```http
GET /analytics/kpi/clv
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `cohort` (optional): Customer cohort identifier

**Response:** `200 OK`
```json
{
  "metric": "CLV",
  "value": 8500.00,
  "currency": "EUR",
  "cohort": "2024-Q1",
  "calculation_method": "predictive",
  "confidence": 0.87
}
```

---

#### Get All KPIs

```http
GET /analytics/kpi/all
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "date": "2026-01-14",
  "kpis": {
    "MRR": 125000.50,
    "ARR": 1500000.00,
    "churn_rate": 3.5,
    "CLV": 8500.00,
    "NRR": 112.5,
    "CAC": 1200.00,
    "ARPU": 156.25,
    "LTV_CAC_ratio": 7.08
  }
}
```

---

### Dashboards

#### List Dashboards

```http
GET /analytics/dashboards
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `skip` (optional): Pagination offset, default 0
- `limit` (optional): Max results, default 20

**Response:** `200 OK`
```json
{
  "total": 5,
  "dashboards": [
    {
      "id": "DASH-001",
      "name": "Executive Dashboard",
      "description": "High-level KPIs for C-suite",
      "template": "executive",
      "owner_id": "USR-12345",
      "created_at": "2025-12-01T10:00:00Z",
      "updated_at": "2026-01-10T15:30:00Z",
      "widget_count": 8
    },
    // ...
  ]
}
```

---

#### Get Dashboard

```http
GET /analytics/dashboards/{dashboard_id}
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "id": "DASH-001",
  "name": "Executive Dashboard",
  "description": "High-level KPIs for C-suite",
  "layout": {
    "columns": 12,
    "widgets": [
      {
        "id": "WIDGET-001",
        "type": "kpi_card",
        "position": {"x": 0, "y": 0, "w": 3, "h": 2},
        "config": {
          "metric": "MRR",
          "comparison": "previous_month"
        },
        "data_source": "/analytics/kpi/mrr"
      },
      {
        "id": "WIDGET-002",
        "type": "line_chart",
        "position": {"x": 3, "y": 0, "w": 9, "h": 4},
        "config": {
          "x_axis": "date",
          "y_axis": "revenue",
          "period": "last_12_months"
        },
        "data_source": "/analytics/trends/revenue"
      }
    ]
  }
}
```

---

#### Create Dashboard

```http
POST /analytics/dashboards
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "My Custom Dashboard",
  "description": "Custom analytics dashboard",
  "template": "blank", // or "executive", "sales", "marketing"
  "layout": {
    "columns": 12,
    "widgets": [
      {
        "type": "kpi_card",
        "position": {"x": 0, "y": 0, "w": 3, "h": 2},
        "config": {
          "metric": "MRR"
        }
      }
    ]
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "DASH-NEW",
  "name": "My Custom Dashboard",
  "description": "Custom analytics dashboard",
  "template": "blank",
  "owner_id": "USR-12345",
  "created_at": "2026-01-14T10:30:00Z",
  "layout": { /* ... */ }
}
```

---

### Predictive Analytics

#### Generate Revenue Forecast

```http
POST /analytics/forecast/revenue
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "periods": 12, // months to forecast
  "model": "arima", // or "prophet"
  "confidence": 0.95,
  "include_seasonality": true
}
```

**Response:** `200 OK`
```json
{
  "forecast_id": "FCST-001",
  "model": "arima",
  "periods": 12,
  "created_at": "2026-01-14T10:30:00Z",
  "accuracy_metrics": {
    "rmse": 2450.30,
    "mae": 1820.50,
    "mape": 3.2,
    "r2_score": 0.87
  },
  "forecast": [
    {
      "period": "2026-02",
      "predicted_value": 128500.00,
      "lower_bound": 122000.00,
      "upper_bound": 135000.00,
      "confidence": 0.95
    },
    // ... 11 more periods
  ]
}
```

---

#### Predict Customer Churn

```http
POST /analytics/churn/predict
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "customer_ids": ["CUST-001", "CUST-002"], // optional
  "threshold": 0.7, // churn probability threshold
  "limit": 100 // max results
}
```

**Response:** `200 OK`
```json
{
  "prediction_id": "PRED-001",
  "model": "random_forest",
  "model_version": "1.0.2",
  "created_at": "2026-01-14T10:30:00Z",
  "results": [
    {
      "customer_id": "CUST-001",
      "churn_probability": 0.82,
      "risk_level": "high",
      "top_factors": [
        {"feature": "low_engagement", "importance": 0.35},
        {"feature": "payment_failures", "importance": 0.28},
        {"feature": "support_tickets", "importance": 0.22}
      ]
    },
    {
      "customer_id": "CUST-002",
      "churn_probability": 0.15,
      "risk_level": "low",
      "top_factors": [/* ... */]
    }
  ]
}
```

---

#### Run Monte Carlo Simulation

```http
POST /analytics/simulations/monte-carlo
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "base_revenue": 125000.00,
  "growth_rate": {
    "mean": 5.0, // percentage
    "std": 2.0
  },
  "churn_rate": {
    "mean": 3.5,
    "std": 1.0
  },
  "periods": 12,
  "n_simulations": 10000
}
```

**Response:** `200 OK`
```json
{
  "simulation_id": "SIM-001",
  "n_simulations": 10000,
  "periods": 12,
  "results": {
    "final_revenue": {
      "mean": 185000.00,
      "median": 182500.00,
      "std": 18500.00,
      "min": 142000.00,
      "max": 245000.00
    },
    "var_95": 156000.00, // Value at Risk (5th percentile)
    "cvar_95": 148000.00, // Conditional VaR
    "probability_above_target": 0.72 // P(revenue > target)
  },
  "distributions": [
    {
      "period": 1,
      "mean": 132500.00,
      "percentile_5": 125000.00,
      "percentile_95": 142000.00
    },
    // ... 11 more periods
  ]
}
```

---

### Data Warehouse

#### List ETL Pipelines

```http
GET /analytics/etl/pipelines
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "pipelines": [
    {
      "id": "PIPE-001",
      "name": "Daily Revenue ETL",
      "schedule": "0 2 * * *", // cron expression
      "source": "production_db",
      "status": "active",
      "last_run": "2026-01-14T02:00:00Z",
      "next_run": "2026-01-15T02:00:00Z",
      "success_rate": 98.5
    }
  ]
}
```

---

#### Run ETL Pipeline

```http
POST /analytics/etl/pipelines/{pipeline_id}/run
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "mode": "incremental", // or "full_refresh"
  "notify_on_completion": true
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "JOB-12345",
  "pipeline_id": "PIPE-001",
  "status": "running",
  "started_at": "2026-01-14T10:30:00Z",
  "estimated_duration": 120 // seconds
}
```

---

### OLAP Cube

#### Execute OLAP Query

```http
POST /analytics/olap/query
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "cube": "sales_cube",
  "operation": "slice",
  "dimensions": ["product", "region", "date"],
  "measures": ["revenue", "quantity"],
  "filters": {
    "date": {
      "year": 2025
    }
  },
  "aggregation": "sum"
}
```

**Response:** `200 OK`
```json
{
  "query_id": "QUERY-001",
  "execution_time_ms": 450,
  "results": [
    {
      "product": "Product A",
      "region": "US",
      "date": "2025-01",
      "revenue": 45000.00,
      "quantity": 320
    },
    // ...
  ],
  "total_rows": 24
}
```

---

### Reports

#### Generate Report

```http
POST /analytics/reports/generate
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "type": "executive_summary", // or "detailed", "custom"
  "format": "pdf", // or "excel", "powerpoint", "csv"
  "data_sources": [
    "kpis",
    "revenue_trends",
    "customer_growth"
  ],
  "period": {
    "start": "2025-12-01",
    "end": "2026-01-14"
  },
  "options": {
    "include_charts": true,
    "include_raw_data": false,
    "branding": "company_logo"
  }
}
```

**Response:** `202 Accepted`
```json
{
  "report_id": "REP-001",
  "status": "generating",
  "estimated_time": 30, // seconds
  "download_url": "/analytics/reports/REP-001/download" // available when complete
}
```

---

#### Download Report

```http
GET /analytics/reports/{report_id}/download
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
- Content-Type: application/pdf (or appropriate format)
- Binary file download

---

## 🏥 VARIANT B: SERVICE MANAGEMENT

Base Path: `/services`

### Services

#### List Services

```http
GET /services
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `category` (optional): Filter by category
- `status` (optional): Filter by status (active, inactive, archived)
- `provider_id` (optional): Filter by provider
- `skip` (optional): Pagination offset
- `limit` (optional): Max results

**Response:** `200 OK`
```json
{
  "total": 45,
  "services": [
    {
      "id": "SRV-001",
      "name": "Personal Care Assistant",
      "category": "household",
      "subcategory": "personal_hygiene",
      "status": "active",
      "base_hourly_rate": 25.50,
      "regional_coefficient": 1.0,
      "provider": {
        "id": "PROV-001",
        "name": "Care Plus GmbH"
      },
      "created_at": "2025-11-01T10:00:00Z"
    },
    // ...
  ]
}
```

---

#### Get Service

```http
GET /services/{service_id}
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "id": "SRV-001",
  "name": "Personal Care Assistant",
  "category": "household",
  "subcategory": "personal_hygiene",
  "status": "active",
  "description_short": "Assistance with daily personal care activities",
  "description_medium": "Professional support for hygiene, grooming, and dressing...",
  "description_long": "Comprehensive personal care assistance including...",
  "financial": {
    "base_hourly_rate": 25.50,
    "regional_coefficient": 1.0,
    "overhead_percentage": 15.0,
    "effective_rate": 29.33
  },
  "provider": {
    "id": "PROV-001",
    "name": "Care Plus GmbH",
    "contact_email": "info@careplus.de",
    "is_certified": true
  },
  "specifications": [
    {
      "key": "qualification_required",
      "value": "Altenpfleger / Gesundheitspfleger",
      "data_type": "string"
    },
    {
      "key": "min_hours_per_week",
      "value": "10",
      "data_type": "number",
      "unit": "hours"
    }
  ],
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2026-01-10T14:20:00Z",
  "version": 2
}
```

---

#### Create Service

```http
POST /services
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Mobility Support",
  "category": "social",
  "subcategory": "outdoor_activities",
  "description_short": "Accompaniment for outdoor activities",
  "description_medium": "Professional support for social participation...",
  "base_hourly_rate": 22.00,
  "regional_coefficient": 1.1,
  "overhead_percentage": 15.0,
  "provider_id": "PROV-002",
  "specifications": [
    {
      "key": "driver_license_required",
      "value": "true",
      "data_type": "boolean"
    },
    {
      "key": "max_distance_km",
      "value": "50",
      "data_type": "number",
      "unit": "kilometers"
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "SRV-NEW",
  "name": "Mobility Support",
  // ... full service object
}
```

---

#### Update Service

```http
PUT /services/{service_id}
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "base_hourly_rate": 23.50,
  "status": "active"
}
```

**Response:** `200 OK`
```json
{
  "id": "SRV-001",
  // ... updated service object
  "version": 3
}
```

---

#### Delete Service

```http
DELETE /services/{service_id}
Authorization: Bearer {access_token}
```

**Response:** `204 No Content`

---

### Financial Calculations

#### Calculate Employer Contributions

```http
POST /finance/calculate-contributions
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "gross_salary": 3500.00,
  "has_children": true,
  "regional_zone": "west",
  "risk_class": "low"
}
```

**Response:** `200 OK`
```json
{
  "gross_salary": 3500.00,
  "contributions": {
    "KV": 255.50, // Krankenversicherung (7.3%)
    "PV": 53.38,  // Pflegeversicherung (1.525%)
    "RV": 325.50, // Rentenversicherung (9.3%)
    "AV": 42.00,  // Arbeitslosenversicherung (1.2%)
    "UV": 35.00,  // Unfallversicherung (1.0% low risk)
    "total": 711.38
  },
  "employer_total_cost": 4211.38,
  "employee_share": 676.38 // approximate
}
```

---

#### Calculate Service Cost

```http
POST /finance/calculate-service-cost
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "hourly_rate": 25.50,
  "hours_per_month": 80,
  "include_contributions": true,
  "regional_coefficient": 1.1,
  "overhead_percentage": 15.0
}
```

**Response:** `200 OK`
```json
{
  "base_cost": 2040.00,
  "regional_adjusted": 2244.00,
  "contributions": {
    "KV": 163.81,
    "PV": 34.22,
    "RV": 208.69,
    "AV": 26.93,
    "UV": 22.44,
    "total": 456.09
  },
  "cost_with_contributions": 2700.09,
  "overhead": 405.01,
  "total_cost": 3105.10,
  "vat": 589.97,
  "total_with_vat": 3695.07
}
```

---

#### Create Budget Plan

```http
POST /finance/create-budget-plan
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "services": [
    {
      "name": "Personal Care",
      "category": "household",
      "hourly_rate": 25.50,
      "hours_per_month": 80,
      "regional_coefficient": 1.0
    },
    {
      "name": "Mobility Support",
      "category": "social",
      "hourly_rate": 22.00,
      "hours_per_month": 40,
      "regional_coefficient": 1.1
    }
  ],
  "months": 12
}
```

**Response:** `200 OK`
```json
{
  "budget_id": "BUDGET-001",
  "monthly_total": 4832.50,
  "annual_total": 57990.00,
  "services": [
    {
      "name": "Personal Care",
      "category": "household",
      "monthly_cost": 3105.10,
      "annual_cost": 37261.20,
      "details": {/* service cost breakdown */}
    },
    {
      "name": "Mobility Support",
      "category": "social",
      "monthly_cost": 1727.40,
      "annual_cost": 20728.80,
      "details": {/* service cost breakdown */}
    }
  ],
  "breakdown_by_category": {
    "household": 37261.20,
    "social": 20728.80
  },
  "breakdown_by_cost_type": {
    "base_cost": 42960.00,
    "contributions": 8940.50,
    "overhead": 6090.00,
    "vat": 0.00
  }
}
```

---

### Templates

#### Parse mSchablone Template

```http
POST /templates/parse
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body:**
- `file`: mSchablone template file (multipart upload)

**Response:** `200 OK`
```json
{
  "template_id": "TMPL-001",
  "version": "1.0",
  "parsed_at": "2026-01-14T10:30:00Z",
  "service_identification": {
    "service_id": "LEIST-2024-001",
    "name": "Grundpflege",
    "category": "household",
    "provider_name": "Pflegedienst Müller GmbH"
  },
  "financial_parameters": {
    "base_hourly_rate": 28.50,
    "employer_contributions": {
      "KV": 7.3,
      "PV": 1.525,
      "RV": 9.3,
      "AV": 1.2,
      "UV": 1.6
    },
    "regional_coefficient": 1.05
  },
  "categories": {
    "household": [/* services */],
    "social": [/* services */]
  },
  "validation_errors": []
}
```

---

### Reports

#### Generate Service Catalog (PDF)

```http
POST /reports/service-catalog
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "format": "pdf",
  "filters": {
    "category": "household",
    "status": "active"
  },
  "include_pricing": true
}
```

**Response:** `202 Accepted`
```json
{
  "report_id": "REP-SERV-001",
  "status": "generating",
  "download_url": "/reports/REP-SERV-001/download"
}
```

---

## 📊 VARIANT C: DASHBOARD

Base Path: `/dashboard`

### Overview Data

#### Get Dashboard Overview

```http
GET /dashboard/overview
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

**Response:** `200 OK`
```json
{
  "date_range": {
    "start": "2025-12-01",
    "end": "2026-01-14"
  },
  "kpis": {
    "total_revenue": 550000.00,
    "revenue_change": 5.2,
    "active_customers": 450,
    "customer_change": 12,
    "mrr": 125000.00,
    "mrr_change": 3.8,
    "churn_rate": 3.5,
    "churn_change": -0.5
  },
  "revenue_trend": [
    {"date": "2025-12", "revenue": 120000},
    {"date": "2026-01", "revenue": 125000}
  ],
  "customer_trend": [
    {"date": "2025-12", "customers": 438},
    {"date": "2026-01", "customers": 450}
  ],
  "category_breakdown": [
    {"category": "Sales", "revenue": 220000},
    {"category": "Marketing", "revenue": 110000},
    {"category": "Product", "revenue": 150000},
    {"category": "Operations", "revenue": 70000}
  ]
}
```

---

### Data Export

#### Export Data

```http
POST /dashboard/export
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "format": "csv", // or "excel"
  "data_type": "revenue_trend", // or "customer_trend", "all"
  "start_date": "2025-01-01",
  "end_date": "2026-01-14"
}
```

**Response:** `200 OK`
- Content-Type: text/csv (or application/vnd.ms-excel)
- Binary file download

---

## ⚠️ ERROR RESPONSES

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {/* optional additional context */},
    "timestamp": "2026-01-14T10:30:00Z",
    "request_id": "REQ-12345"
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_REQUEST` | Request validation failed |
| 401 | `UNAUTHORIZED` | Authentication required or failed |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource conflict (e.g., duplicate) |
| 422 | `VALIDATION_ERROR` | Data validation failed |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_SERVER_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

### Example Error Responses

**401 Unauthorized:**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "timestamp": "2026-01-14T10:30:00Z",
    "request_id": "REQ-12345"
  }
}
```

**422 Validation Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "email",
          "message": "Invalid email format"
        },
        {
          "field": "hourly_rate",
          "message": "Must be a positive number"
        }
      ]
    },
    "timestamp": "2026-01-14T10:30:00Z",
    "request_id": "REQ-12345"
  }
}
```

---

## 🚦 RATE LIMITING

**Limits:**
- **Standard Users:** 100 requests per minute
- **Premium Users:** 1000 requests per minute
- **Service Accounts:** 5000 requests per minute

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1673694000
```

**Rate Limit Exceeded Response (429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 42 seconds.",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_at": "2026-01-14T10:31:00Z"
    },
    "timestamp": "2026-01-14T10:30:18Z"
  }
}
```

---

## 📖 ADDITIONAL RESOURCES

- **OpenAPI/Swagger UI:** `http://localhost:8080/docs`
- **ReDoc Documentation:** `http://localhost:8080/redoc`
- **Postman Collection:** [Download](./postman_collection.json)
- **Code Examples:** See [examples/](../examples/) directory

---

## 🔄 VERSIONING

API versioning is handled via URL path (`/api/v1/`, `/api/v2/`, etc.).

**Current Version:** v1
**Deprecated Versions:** None
**Upcoming:** v2 (Q3 2026)

---

## 📞 SUPPORT

For API support:
- **Email:** api-support@daten20.com
- **Slack:** #api-support
- **GitHub Issues:** https://github.com/your-org/daten20/issues

---

**Document Status:** ✅ Complete
**Last Updated:** 2026-01-14
**Next Document:** [README.md](../README.md)
