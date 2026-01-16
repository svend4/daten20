"""
REST API for Analytics & BI Dashboard

Provides endpoints for Business Intelligence Dashboard,
KPI calculations, data export, and analytics queries.
"""

import io
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from flasgger import swag_from
from flask import Blueprint, jsonify, request, send_file

# Import analytics modules
from src.analytics.bi_dashboard import KPI, BIDashboard, ReportFormat, ReportFrequency
from src.analytics.data_mining import DataMiningEngine
from src.analytics.data_warehouse import DataWarehouse
from src.analytics.nl_query import NLQueryProcessor
from src.analytics.olap_cube import OLAPCube
from src.analytics.predictive_analytics import PredictiveAnalyticsEngine
from src.analytics.streaming_analytics import StreamProcessor

# Setup logger
logger = logging.getLogger("dms.api.analytics")

# Create Analytics API blueprint
api_analytics = Blueprint("api_analytics", __name__, url_prefix="/api/v1/analytics")

# Initialize analytics components
bi_dashboard = BIDashboard()
predictive_analytics = PredictiveAnalyticsEngine()
data_warehouse = DataWarehouse()
olap_cube = OLAPCube(name="default_cube")
data_mining = DataMiningEngine()
streaming_analytics = StreamProcessor()
nl_query = NLQueryProcessor()


# ==========================================
# DASHBOARD ENDPOINTS
# ==========================================


@api_analytics.route("/dashboard", methods=["GET"])
def get_dashboard():
    """
    Get BI Dashboard Data
    ---
    tags:
      - Analytics
    summary: Get executive BI dashboard data
    description: Returns KPIs, charts data, and analytics for the dashboard
    parameters:
      - name: dateRange
        in: query
        type: integer
        required: false
        description: Number of days to include (default 30)
        default: 30
      - name: tenant
        in: query
        type: string
        required: false
        description: Tenant ID filter (default all)
        default: all
      - name: comparisonPeriod
        in: query
        type: string
        required: false
        description: Comparison period (previous, year_ago, none)
        default: previous
    responses:
      200:
        description: Dashboard data retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            kpis:
              type: object
              description: Key Performance Indicators
            charts:
              type: object
              description: Chart data for visualizations
            timestamp:
              type: string
              format: date-time
      400:
        description: Invalid parameters
      500:
        description: Server error
    """
    try:
        # Parse parameters
        date_range = request.args.get("dateRange", 30, type=int)
        tenant_id = request.args.get("tenant", "all")
        comparison_period = request.args.get("comparisonPeriod", "previous")

        # Calculate date ranges
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)

        # Get dashboard data
        dashboard_data = bi_dashboard.create_executive_dashboard(tenant_id=tenant_id, date_range=(start_date, end_date))

        return (
            jsonify(
                {
                    "success": True,
                    "kpis": dashboard_data.get("kpis", {}),
                    "charts": dashboard_data.get("charts", {}),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Dashboard API error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@api_analytics.route("/kpi/<kpi_name>", methods=["GET"])
def get_kpi(kpi_name: str):
    """
    Get Specific KPI
    ---
    tags:
      - Analytics
    summary: Get specific KPI value
    description: Returns detailed information about a specific KPI
    parameters:
      - name: kpi_name
        in: path
        type: string
        required: true
        description: KPI name (mrr, arr, churn, clv, nrr, cac)
      - name: dateRange
        in: query
        type: integer
        required: false
        description: Number of days
        default: 30
    responses:
      200:
        description: KPI retrieved successfully
      404:
        description: KPI not found
      500:
        description: Server error
    """
    try:
        date_range = request.args.get("dateRange", 30, type=int)

        # Calculate KPI based on name
        kpi_calculators = {
            "mrr": bi_dashboard.kpi_calculator.calculate_mrr,
            "arr": lambda data: bi_dashboard.kpi_calculator.calculate_arr(
                bi_dashboard.kpi_calculator.calculate_mrr(data)
            ),
            "churn": bi_dashboard.kpi_calculator.calculate_churn_rate,
            "clv": bi_dashboard.kpi_calculator.calculate_clv,
            "nrr": bi_dashboard.kpi_calculator.calculate_nrr,
            "cac": bi_dashboard.kpi_calculator.calculate_cac,
        }

        if kpi_name not in kpi_calculators:
            return jsonify({"success": False, "error": f'KPI "{kpi_name}" not found'}), 404

        # Mock data for demo
        # TODO: Replace with actual data fetching
        mock_data = {"subscriptions": [], "churned_customers": 0, "total_customers_start": 0}

        # value = kpi_calculators[kpi_name](mock_data)

        return (
            jsonify(
                {
                    "success": True,
                    "kpi": kpi_name,
                    "value": 0,  # value,
                    "unit": "EUR" if kpi_name in ["mrr", "arr", "clv", "cac"] else "%",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"KPI API error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# PREDICTIVE ANALYTICS ENDPOINTS
# ==========================================


@api_analytics.route("/predict/revenue", methods=["POST"])
def predict_revenue():
    """
    Predict Future Revenue
    ---
    tags:
      - Predictive Analytics
    summary: Get revenue forecast
    description: Returns revenue predictions for specified period
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            months:
              type: integer
              description: Number of months to forecast
              default: 3
            model:
              type: string
              description: Model to use (arima, prophet, lstm)
              default: arima
    responses:
      200:
        description: Forecast generated successfully
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        months = data.get("months", 3)
        model = data.get("model", "arima")

        # Generate forecast
        forecast = predictive_analytics.forecast_revenue(months_ahead=months, model_type=model)

        return (
            jsonify({"success": True, "forecast": forecast, "model": model, "timestamp": datetime.now().isoformat()}),
            200,
        )

    except Exception as e:
        logger.error(f"Revenue prediction error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@api_analytics.route("/predict/churn", methods=["POST"])
def predict_churn():
    """
    Predict Customer Churn
    ---
    tags:
      - Predictive Analytics
    summary: Predict customer churn probability
    description: Returns churn predictions for customers
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            customer_ids:
              type: array
              items:
                type: string
              description: List of customer IDs to analyze
    responses:
      200:
        description: Predictions generated successfully
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        customer_ids = data.get("customer_ids", [])

        # Generate churn predictions
        predictions = predictive_analytics.predict_churn(customer_ids)

        return jsonify({"success": True, "predictions": predictions, "timestamp": datetime.now().isoformat()}), 200

    except Exception as e:
        logger.error(f"Churn prediction error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# DATA WAREHOUSE ENDPOINTS
# ==========================================


@api_analytics.route("/warehouse/etl", methods=["POST"])
def trigger_etl():
    """
    Trigger ETL Pipeline
    ---
    tags:
      - Data Warehouse
    summary: Trigger ETL data pipeline
    description: Starts the ETL process to update data warehouse
    parameters:
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            incremental:
              type: boolean
              description: Use incremental load
              default: true
    responses:
      202:
        description: ETL job started
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        incremental = data.get("incremental", True)

        # Trigger ETL
        job_id = data_warehouse.run_etl_pipeline(incremental=incremental)

        return (
            jsonify({"success": True, "job_id": job_id, "status": "started", "timestamp": datetime.now().isoformat()}),
            202,
        )

    except Exception as e:
        logger.error(f"ETL trigger error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@api_analytics.route("/warehouse/status", methods=["GET"])
def warehouse_status():
    """
    Get Data Warehouse Status
    ---
    tags:
      - Data Warehouse
    summary: Get warehouse status
    description: Returns status information about the data warehouse
    responses:
      200:
        description: Status retrieved successfully
      500:
        description: Server error
    """
    try:
        status = data_warehouse.get_status()

        return jsonify({"success": True, "status": status, "timestamp": datetime.now().isoformat()}), 200

    except Exception as e:
        logger.error(f"Warehouse status error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# OLAP CUBE ENDPOINTS
# ==========================================


@api_analytics.route("/olap/query", methods=["POST"])
def olap_query():
    """
    Execute OLAP Query
    ---
    tags:
      - OLAP
    summary: Execute OLAP cube query
    description: Performs multidimensional analysis query
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            dimensions:
              type: array
              items:
                type: string
              description: Dimensions to include
            measures:
              type: array
              items:
                type: string
              description: Measures to calculate
            filters:
              type: object
              description: Filter criteria
    responses:
      200:
        description: Query executed successfully
      400:
        description: Invalid query
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        dimensions = data.get("dimensions", [])
        measures = data.get("measures", [])
        filters = data.get("filters", {})

        # Execute OLAP query
        result = olap_cube.query(dimensions=dimensions, measures=measures, filters=filters)

        return jsonify({"success": True, "result": result, "timestamp": datetime.now().isoformat()}), 200

    except Exception as e:
        logger.error(f"OLAP query error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# DATA MINING ENDPOINTS
# ==========================================


@api_analytics.route("/mining/patterns", methods=["POST"])
def discover_patterns():
    """
    Discover Data Patterns
    ---
    tags:
      - Data Mining
    summary: Discover patterns in data
    description: Uses data mining algorithms to find patterns
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            algorithm:
              type: string
              description: Algorithm to use (apriori, fpgrowth, kmeans)
              default: apriori
            min_support:
              type: number
              description: Minimum support threshold
              default: 0.3
    responses:
      200:
        description: Patterns discovered
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        algorithm = data.get("algorithm", "apriori")
        min_support = data.get("min_support", 0.3)

        # Discover patterns
        patterns = data_mining.discover_patterns(algorithm=algorithm, min_support=min_support)

        return (
            jsonify(
                {"success": True, "patterns": patterns, "algorithm": algorithm, "timestamp": datetime.now().isoformat()}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Pattern discovery error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# NATURAL LANGUAGE QUERY ENDPOINTS
# ==========================================


@api_analytics.route("/query/natural", methods=["POST"])
def natural_language_query():
    """
    Natural Language Query
    ---
    tags:
      - Natural Language Query
    summary: Execute query in natural language
    description: Converts natural language to SQL and executes query
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            query:
              type: string
              description: Natural language query
              example: "Show me revenue for last month"
    responses:
      200:
        description: Query executed successfully
      400:
        description: Invalid query
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        query = data.get("query", "")

        if not query:
            return jsonify({"success": False, "error": "Query is required"}), 400

        # Execute NL query
        result = nl_query.execute_query(query)

        return (
            jsonify(
                {
                    "success": True,
                    "query": query,
                    "sql": result.get("sql", ""),
                    "result": result.get("data", []),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"NL query error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# EXPORT ENDPOINTS
# ==========================================


@api_analytics.route("/export", methods=["POST"])
def export_dashboard():
    """
    Export Dashboard
    ---
    tags:
      - Analytics
    summary: Export dashboard to various formats
    description: Exports dashboard data in PDF, Excel, PowerPoint, JSON, or CSV
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            format:
              type: string
              description: Export format
              enum: [pdf, excel, powerpoint, json, csv]
              default: pdf
            include:
              type: object
              properties:
                kpis:
                  type: boolean
                  default: true
                charts:
                  type: boolean
                  default: true
                rawData:
                  type: boolean
                  default: false
            filters:
              type: object
              description: Filters applied to dashboard
    responses:
      200:
        description: File exported successfully
        schema:
          type: file
      400:
        description: Invalid format
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}
        export_format = data.get("format", "pdf")
        include = data.get("include", {})
        filters = data.get("filters", {})

        # Validate format
        valid_formats = ["pdf", "excel", "powerpoint", "json", "csv"]
        if export_format not in valid_formats:
            return (
                jsonify({"success": False, "error": f'Invalid format. Must be one of: {", ".join(valid_formats)}'}),
                400,
            )

        # Generate export
        export_file = bi_dashboard.report_generator.generate_report(
            format=ReportFormat(export_format),
            include_kpis=include.get("kpis", True),
            include_charts=include.get("charts", True),
            include_raw_data=include.get("rawData", False),
            filters=filters,
        )

        # Determine MIME type
        mime_types = {
            "pdf": "application/pdf",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "powerpoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "json": "application/json",
            "csv": "text/csv",
        }

        return send_file(
            io.BytesIO(export_file),
            mimetype=mime_types[export_format],
            as_attachment=True,
            download_name=f'bi-dashboard-{datetime.now().strftime("%Y%m%d")}.{export_format}',
        )

    except Exception as e:
        logger.error(f"Export error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# SCHEDULED REPORTS ENDPOINTS
# ==========================================


@api_analytics.route("/reports/schedule", methods=["POST"])
def schedule_report():
    """
    Schedule Report
    ---
    tags:
      - Reports
    summary: Schedule recurring report
    description: Creates a scheduled report with specified frequency
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Report name
            frequency:
              type: string
              enum: [daily, weekly, monthly, quarterly]
              default: weekly
            format:
              type: string
              enum: [pdf, excel, powerpoint]
              default: pdf
            recipients:
              type: array
              items:
                type: string
              description: Email addresses
    responses:
      201:
        description: Report scheduled successfully
      400:
        description: Invalid parameters
      500:
        description: Server error
    """
    try:
        data = request.get_json() or {}

        report_id = bi_dashboard.report_scheduler.schedule_report(
            name=data.get("name", "Scheduled Report"),
            frequency=ReportFrequency(data.get("frequency", "weekly")),
            format=ReportFormat(data.get("format", "pdf")),
            recipients=data.get("recipients", []),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "report_id": report_id,
                    "message": "Report scheduled successfully",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Report scheduling error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@api_analytics.route("/reports/scheduled", methods=["GET"])
def list_scheduled_reports():
    """
    List Scheduled Reports
    ---
    tags:
      - Reports
    summary: Get list of scheduled reports
    description: Returns all scheduled reports
    responses:
      200:
        description: Reports retrieved successfully
      500:
        description: Server error
    """
    try:
        reports = bi_dashboard.report_scheduler.list_scheduled_reports()

        return (
            jsonify(
                {"success": True, "reports": reports, "count": len(reports), "timestamp": datetime.now().isoformat()}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"List scheduled reports error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# Error handlers
@api_analytics.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@api_analytics.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({"success": False, "error": "Internal server error"}), 500


# Helper function to initialize the blueprint in the main app
def init_analytics_api(app):
    """Initialize analytics API with the Flask app"""
    app.register_blueprint(api_analytics)
    logger.info("Analytics API initialized")
