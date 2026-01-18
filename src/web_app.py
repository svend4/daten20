#!/usr/bin/env python3
"""
Web Application - Flask веб-интерфейс

Полнофункциональный веб-интерфейс для управления документами
социальных услуг с REST API, dashboard и визуальными редакторами.
"""

import json
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flasgger import Swagger
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.utils import secure_filename

from src.api_docs import api_docs_bp
from src.core.csrf_protection import csrf, csrf_exempt
from src.core.database import Database
from src.core.https_config import HTTPSConfig, configure_flask_https
from src.core.input_validation import FlaskRequestValidator, InputValidator, ValidationError
from src.core.parser import TemplateParser
from src.core.rate_limiter import (
    GlobalRateLimiters,
    RateLimitExceeded,
    get_client_id_from_request,
    handle_rate_limit_exceeded,
    rate_limit,
)
from src.core.validator import TemplateValidator
from src.document_generator import DocumentGenerator
from src.financial_calculator import FinancialCalculator
from src.models.service import Service
from src.service_manager import ServiceManager
from src.utils.constants import FUNDING_SOURCES, REGIONAL_COEFFICIENTS, SERVICE_TYPES
from src.utils.helpers import load_config, save_config

# Initialize Flask app
app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")  # Change in production!
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["ENV"] = os.getenv("FLASK_ENV", "development")

# Initialize HTTPS configuration
https_config = HTTPSConfig()
if app.config["ENV"] == "production":
    configure_flask_https(app, https_config)

# Initialize CSRF protection
csrf.init_app(app)

# Initialize Swagger UI
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Document Management System API",
        "description": "REST API for Document Management System",
        "version": "4.1.0",
        "contact": {"name": "DMS Support", "url": "https://github.com/svend4/daten20"},
    },
    "securityDefinitions": {"ApiKeyAuth": {"type": "apiKey", "name": "X-API-Key", "in": "header"}},
    "security": [{"ApiKeyAuth": []}],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Register API documentation blueprint
app.register_blueprint(api_docs_bp)

# Initialize components
db = Database()
calculator = FinancialCalculator()
generator = DocumentGenerator()
validator = TemplateValidator()
parser = TemplateParser("mSchablone")


# ==================== WEB ROUTES ====================


@app.route("/")
def index():
    """Main dashboard page"""
    stats = db.get_statistics()
    recent_services = db.list_services(limit=5)

    return render_template("dashboard.html", stats=stats, recent_services=recent_services, page="dashboard")


@app.route("/services")
def services_list():
    """List all services"""
    region = request.args.get("region")
    service_type = request.args.get("type")
    page = int(request.args.get("page", 1))
    per_page = 20

    services = db.list_services(limit=per_page, offset=(page - 1) * per_page, region=region, service_type=service_type)

    return render_template(
        "services_list.html",
        services=services,
        page="services",
        current_page=page,
        regions=REGIONAL_COEFFICIENTS.keys(),
        service_types=SERVICE_TYPES,
    )


@app.route("/services/<int:service_id>")
def service_detail(service_id):
    """Service detail page"""
    service = db.get_service(service_id)

    if not service:
        flash("Услуга не найдена", "error")
        return redirect(url_for("services_list"))

    # Calculate cost breakdown
    breakdown = calculator.calculate_hourly_rate(service.financial)
    versions = db.get_service_versions(service_id)

    return render_template(
        "service_detail.html", service=service, breakdown=breakdown, versions=versions, page="services"
    )


@app.route("/services/new", methods=["GET", "POST"])
@rate_limit(requests=20, window=300)  # 20 creates per 5 minutes
def service_new():
    """Create new service"""
    if request.method == "POST":
        try:
            # Input validation
            input_validator = InputValidator()

            # Build service from form data
            service = Service()

            # Basic info with validation
            service.basic_info.service_name = input_validator.validate_string(
                request.form.get("service_name", ""), min_length=1, max_length=200
            )
            service.basic_info.target_group = input_validator.validate_string(
                request.form.get("target_group", ""), max_length=500
            )
            service.basic_info.region = input_validator.validate_enum(
                request.form.get("region", ""), list(REGIONAL_COEFFICIENTS.keys())
            )
            service.basic_info.provider_type = input_validator.validate_string(
                request.form.get("provider_type", ""), max_length=100
            )
            service.basic_info.document_date = request.form.get("document_date")
            service.basic_info.responsible_person = input_validator.validate_string(
                request.form.get("responsible_person", ""), max_length=200
            )

            # Financial with validation
            service.financial.brutto_rate = input_validator.validate_decimal(
                request.form.get("brutto_rate", "0"), min_value=Decimal("0"), max_value=Decimal("1000000")
            )
            service.financial.materials_per_month = input_validator.validate_decimal(
                request.form.get("materials_per_month", "0"), min_value=Decimal("0"), max_value=Decimal("1000000")
            )
            service.financial.admin_percent = input_validator.validate_decimal(
                request.form.get("admin_percent", "5"), min_value=Decimal("0"), max_value=Decimal("100")
            )

            region_coef = REGIONAL_COEFFICIENTS.get(service.basic_info.region, 1.0)
            service.financial.region_coefficient = Decimal(str(region_coef))
            service.financial.is_saxony = service.basic_info.region == "Sachsen"

            # System settings
            service.system_settings.use_umlages = request.form.get("use_umlages") == "true"
            service.system_settings.use_vacation_reserve = not service.system_settings.use_umlages
            service.system_settings.service_type = request.form.get("service_type", "social")
            service.system_settings.surcharge_base = request.form.get("surcharge_base", "full_cost")

            service.financial.use_umlages = service.system_settings.use_umlages
            service.financial.use_vacation_reserve = service.system_settings.use_vacation_reserve
            service.financial.surcharge_base = service.system_settings.surcharge_base

            # Funding
            service.funding.payer = request.form.get("payer", "")

            # Validate
            validation = validator.validate_config(service.to_dict())
            if not validation.is_valid:
                for error in validation.errors:
                    flash(error, "error")
                return render_template(
                    "service_form.html",
                    service=service,
                    regions=REGIONAL_COEFFICIENTS.keys(),
                    service_types=SERVICE_TYPES,
                    funding_sources=FUNDING_SOURCES,
                    page="services",
                )

            # Save to database
            service_id = db.create_service(service)
            flash(f'Услуга "{service.basic_info.service_name}" создана успешно!', "success")
            return redirect(url_for("service_detail", service_id=service_id))

        except Exception as e:
            flash(f"Ошибка при создании услуги: {str(e)}", "error")

    # GET request - show form
    return render_template(
        "service_form.html",
        service=Service(),
        regions=REGIONAL_COEFFICIENTS.keys(),
        service_types=SERVICE_TYPES,
        funding_sources=FUNDING_SOURCES,
        page="services",
    )


@app.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
@rate_limit(requests=30, window=300)  # 30 edits per 5 minutes
def service_edit(service_id):
    """Edit existing service"""
    service = db.get_service(service_id)

    if not service:
        flash("Услуга не найдена", "error")
        return redirect(url_for("services_list"))

    if request.method == "POST":
        try:
            # Input validation
            input_validator = InputValidator()

            # Update service from form with validation
            service.basic_info.service_name = input_validator.validate_string(
                request.form.get("service_name", ""), min_length=1, max_length=200
            )
            service.basic_info.target_group = input_validator.validate_string(
                request.form.get("target_group", ""), max_length=500
            )
            service.basic_info.region = input_validator.validate_enum(
                request.form.get("region", ""), list(REGIONAL_COEFFICIENTS.keys())
            )
            service.basic_info.provider_type = input_validator.validate_string(
                request.form.get("provider_type", ""), max_length=100
            )
            service.basic_info.document_date = request.form.get("document_date")
            service.basic_info.responsible_person = input_validator.validate_string(
                request.form.get("responsible_person", ""), max_length=200
            )

            service.financial.brutto_rate = input_validator.validate_decimal(
                request.form.get("brutto_rate", "0"), min_value=Decimal("0"), max_value=Decimal("1000000")
            )
            service.financial.materials_per_month = input_validator.validate_decimal(
                request.form.get("materials_per_month", "0"), min_value=Decimal("0"), max_value=Decimal("1000000")
            )
            service.financial.admin_percent = input_validator.validate_decimal(
                request.form.get("admin_percent", "5"), min_value=Decimal("0"), max_value=Decimal("100")
            )

            region_coef = REGIONAL_COEFFICIENTS.get(service.basic_info.region, 1.0)
            service.financial.region_coefficient = Decimal(str(region_coef))

            service.system_settings.use_umlages = request.form.get("use_umlages") == "true"
            service.system_settings.service_type = request.form.get("service_type", "social")

            db.update_service(service)
            flash("Услуга обновлена успешно!", "success")
            return redirect(url_for("service_detail", service_id=service_id))

        except Exception as e:
            flash(f"Ошибка при обновлении: {str(e)}", "error")

    return render_template(
        "service_form.html",
        service=service,
        regions=REGIONAL_COEFFICIENTS.keys(),
        service_types=SERVICE_TYPES,
        funding_sources=FUNDING_SOURCES,
        edit_mode=True,
        page="services",
    )


@app.route("/services/<int:service_id>/delete", methods=["POST"])
@rate_limit(requests=10, window=300)  # 10 deletes per 5 minutes
def service_delete(service_id):
    """Delete service"""
    if db.delete_service(service_id):
        flash("Услуга удалена", "success")
    else:
        flash("Ошибка при удалении", "error")

    return redirect(url_for("services_list"))


@app.route("/calculator", methods=["GET", "POST"])
@rate_limit(requests=50, window=60)  # 50 calculations per minute
def calculator_page():
    """Financial calculator page"""
    result = None

    if request.method == "POST":
        try:
            from src.models.financial import FinancialParameters

            # Input validation
            input_validator = InputValidator()

            # Validate brutto_rate
            brutto_rate = input_validator.validate_decimal(
                request.form.get("brutto_rate", "0"), min_value=Decimal("0"), max_value=Decimal("1000000")
            )

            params = FinancialParameters(brutto_rate=brutto_rate)

            region = request.form.get("region")
            if region:
                # Validate region
                region = input_validator.validate_enum(region, list(REGIONAL_COEFFICIENTS.keys()))
                params.region_coefficient = Decimal(str(REGIONAL_COEFFICIENTS.get(region, 1.0)))

            # Validate materials
            materials = input_validator.validate_decimal(
                request.form.get("materials", "0"), min_value=Decimal("0"), max_value=Decimal("1000000")
            )
            params.materials_per_month = materials

            # Validate admin percent
            admin = input_validator.validate_decimal(
                request.form.get("admin", "5"), min_value=Decimal("0"), max_value=Decimal("100")
            )
            params.admin_percent = admin
            params.use_umlages = request.form.get("mode") != "reserve"
            params.use_vacation_reserve = not params.use_umlages

            breakdown = calculator.calculate_hourly_rate(params)
            result = breakdown

        except Exception as e:
            flash(f"Ошибка расчета: {str(e)}", "error")

    return render_template("calculator.html", result=result, regions=REGIONAL_COEFFICIENTS.keys(), page="calculator")


@app.route("/generator", methods=["GET", "POST"])
@rate_limit(requests=10, window=300)  # 10 document generations per 5 minutes
def generator_page():
    """Document generator page"""
    if request.method == "POST":
        try:
            service_id = request.form.get("service_id")
            output_format = request.form.get("format", "html")

            service = db.get_service(int(service_id))
            if not service:
                flash("Услуга не найдена", "error")
                return redirect(url_for("generator_page"))

            # Generate document
            if not generator.load_template():
                flash("Ошибка загрузки шаблона", "error")
                return redirect(url_for("generator_page"))

            filled_content = generator.fill_from_service(service)

            # Save to exports
            filename = f"service_{service_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            output_path = f"data/exports/{filename}"

            if output_format == "html":
                generator.exporter.export_to_html(filled_content, output_path, service.basic_info.service_name)
            elif output_format == "txt":
                generator.exporter.export_to_text(filled_content, output_path)
            elif output_format == "md":
                generator.exporter.export_to_markdown(filled_content, output_path)

            flash(f"Документ создан: {filename}", "success")
            return send_file(output_path, as_attachment=True)

        except Exception as e:
            flash(f"Ошибка генерации: {str(e)}", "error")

    # List services for selection
    services = db.list_services(limit=100)

    return render_template("generator.html", services=services, page="generator")


@app.route("/analytics")
def analytics_page():
    """Analytics and reports page"""
    stats = db.get_statistics()

    # Get all services for analysis
    all_services = db.list_services(limit=1000)

    # Calculate additional stats
    if all_services:
        rates = [float(s.financial.brutto_rate) for s in all_services if s.financial.brutto_rate]
        stats["min_rate"] = min(rates) if rates else 0
        stats["max_rate"] = max(rates) if rates else 0
        stats["median_rate"] = sorted(rates)[len(rates) // 2] if rates else 0

    return render_template("analytics.html", stats=stats, services=all_services, page="analytics")


@app.route("/search")
def search_page():
    """Search services"""
    query = request.args.get("q", "")

    if query:
        services = db.search_services(query)
    else:
        services = []

    return render_template("search.html", query=query, services=services, page="search")


# ==================== REST API ROUTES ====================


@app.route("/api/services", methods=["GET"])
@rate_limit(requests=100, window=60)  # 100 requests per minute
@csrf_exempt
def api_services_list():
    """API: List all services"""
    # Input validation
    input_validator = InputValidator()

    region = request.args.get("region")
    service_type = request.args.get("type")

    # Validate limit and offset
    limit = input_validator.validate_integer(request.args.get("limit", 100), min_value=1, max_value=1000)
    offset = input_validator.validate_integer(request.args.get("offset", 0), min_value=0)

    # Validate region if provided
    if region:
        region = input_validator.validate_enum(region, list(REGIONAL_COEFFICIENTS.keys()))

    # Validate service_type if provided
    if service_type:
        service_type = input_validator.validate_enum(service_type, list(SERVICE_TYPES.keys()))

    services = db.list_services(limit=limit, offset=offset, region=region, service_type=service_type)

    return jsonify({"success": True, "count": len(services), "services": [s.to_dict() for s in services]})


@app.route("/api/services/<int:service_id>", methods=["GET"])
@rate_limit(requests=100, window=60)  # 100 requests per minute
@csrf_exempt
def api_service_get(service_id):
    """API: Get service by ID"""
    # Input validation
    input_validator = InputValidator()
    service_id = input_validator.validate_integer(service_id, min_value=1)

    service = db.get_service(service_id)

    if not service:
        return jsonify({"success": False, "error": "Service not found"}), 404

    return jsonify({"success": True, "service": service.to_dict()})


@app.route("/api/services", methods=["POST"])
@rate_limit(requests=10, window=60)  # 10 creates per minute (stricter limit)
@csrf_exempt
def api_service_create():
    """API: Create new service"""
    try:
        data = request.get_json()

        # Input validation
        input_validator = InputValidator()

        # Validate basic info fields
        if "basic_info" in data:
            basic = data["basic_info"]
            if "service_name" in basic:
                basic["service_name"] = input_validator.validate_string(
                    basic["service_name"], min_length=1, max_length=200
                )
            if "target_group" in basic:
                basic["target_group"] = input_validator.validate_string(basic["target_group"], max_length=500)
            if "region" in basic:
                basic["region"] = input_validator.validate_enum(basic["region"], list(REGIONAL_COEFFICIENTS.keys()))
            if "responsible_person" in basic:
                basic["responsible_person"] = input_validator.validate_string(
                    basic["responsible_person"], max_length=200
                )

        # Validate financial fields
        if "financial" in data:
            financial = data["financial"]
            if "brutto_rate" in financial:
                financial["brutto_rate"] = input_validator.validate_decimal(
                    financial["brutto_rate"], min_value=Decimal("0")
                )
            if "materials_per_month" in financial:
                financial["materials_per_month"] = input_validator.validate_decimal(
                    financial["materials_per_month"], min_value=Decimal("0")
                )
            if "admin_percent" in financial:
                financial["admin_percent"] = input_validator.validate_decimal(
                    financial["admin_percent"], min_value=Decimal("0"), max_value=Decimal("100")
                )

        service = Service.from_dict(data)

        # Validate
        validation = validator.validate_config(service.to_dict())
        if not validation.is_valid:
            return jsonify({"success": False, "errors": validation.errors, "missing": validation.missing_required}), 400

        # Create
        service_id = db.create_service(service)

        return jsonify({"success": True, "service_id": service_id, "message": "Service created successfully"}), 201

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/services/<int:service_id>", methods=["PUT"])
@rate_limit(requests=20, window=60)  # 20 updates per minute
@csrf_exempt
def api_service_update(service_id):
    """API: Update service"""
    try:
        # Validate service_id
        input_validator = InputValidator()
        service_id = input_validator.validate_integer(service_id, min_value=1)

        service = db.get_service(service_id)
        if not service:
            return jsonify({"success": False, "error": "Service not found"}), 404

        data = request.get_json()

        # Input validation (same as create)
        if "basic_info" in data:
            basic = data["basic_info"]
            if "service_name" in basic:
                basic["service_name"] = input_validator.validate_string(
                    basic["service_name"], min_length=1, max_length=200
                )
            if "target_group" in basic:
                basic["target_group"] = input_validator.validate_string(basic["target_group"], max_length=500)
            if "region" in basic:
                basic["region"] = input_validator.validate_enum(basic["region"], list(REGIONAL_COEFFICIENTS.keys()))

        if "financial" in data:
            financial = data["financial"]
            if "brutto_rate" in financial:
                financial["brutto_rate"] = input_validator.validate_decimal(
                    financial["brutto_rate"], min_value=Decimal("0")
                )
            if "materials_per_month" in financial:
                financial["materials_per_month"] = input_validator.validate_decimal(
                    financial["materials_per_month"], min_value=Decimal("0")
                )
            if "admin_percent" in financial:
                financial["admin_percent"] = input_validator.validate_decimal(
                    financial["admin_percent"], min_value=Decimal("0"), max_value=Decimal("100")
                )

        updated_service = Service.from_dict(data)
        updated_service.id = service_id

        db.update_service(updated_service)

        return jsonify({"success": True, "message": "Service updated successfully"})

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/services/<int:service_id>", methods=["DELETE"])
@rate_limit(requests=10, window=60)  # 10 deletes per minute (stricter limit)
@csrf_exempt
def api_service_delete(service_id):
    """API: Delete service"""
    # Input validation
    input_validator = InputValidator()
    service_id = input_validator.validate_integer(service_id, min_value=1)

    if db.delete_service(service_id):
        return jsonify({"success": True, "message": "Service deleted successfully"})
    else:
        return jsonify({"success": False, "error": "Service not found"}), 404


@app.route("/api/calculate", methods=["POST"])
@rate_limit(requests=50, window=60)  # 50 calculations per minute
@csrf_exempt
def api_calculate():
    """API: Calculate service cost"""
    try:
        from src.models.financial import FinancialParameters

        data = request.get_json()

        # Input validation
        input_validator = InputValidator()

        # Validate brutto_rate
        brutto_rate = input_validator.validate_decimal(
            data.get("brutto_rate", 0), min_value=Decimal("0"), max_value=Decimal("1000000")  # Max 1M per hour
        )

        params = FinancialParameters(brutto_rate=brutto_rate)

        # Validate region
        if "region" in data:
            region = input_validator.validate_enum(data["region"], list(REGIONAL_COEFFICIENTS.keys()))
            params.region_coefficient = Decimal(str(REGIONAL_COEFFICIENTS.get(region, 1.0)))

        # Validate materials
        if "materials_per_month" in data:
            materials = input_validator.validate_decimal(
                data["materials_per_month"], min_value=Decimal("0"), max_value=Decimal("1000000")
            )
            params.materials_per_month = materials

        # Validate admin percent
        if "admin_percent" in data:
            admin = input_validator.validate_decimal(
                data["admin_percent"], min_value=Decimal("0"), max_value=Decimal("100")
            )
            params.admin_percent = admin

        params.use_umlages = data.get("use_umlages", True)
        params.use_vacation_reserve = not params.use_umlages

        breakdown = calculator.calculate_hourly_rate(params)

        return jsonify({"success": True, "breakdown": breakdown.to_dict()})

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/statistics", methods=["GET"])
@rate_limit(requests=100, window=60)  # 100 requests per minute
@csrf_exempt
def api_statistics():
    """API: Get statistics"""
    stats = db.get_statistics()

    return jsonify({"success": True, "statistics": stats})


@app.route("/api/search", methods=["GET"])
@rate_limit(requests=50, window=60)  # 50 searches per minute
@csrf_exempt
def api_search():
    """API: Search services"""
    query = request.args.get("q", "")

    if not query:
        return jsonify({"success": False, "error": "Query parameter required"}), 400

    # Input validation
    input_validator = InputValidator()

    # Validate search query
    query = input_validator.validate_string(query, min_length=1, max_length=200)

    # Check for SQL injection attempts
    if input_validator.check_sql_injection(query):
        return jsonify({"success": False, "error": "Invalid search query"}), 400

    # Sanitize query
    query = input_validator.sanitize_html(query)

    services = db.search_services(query)

    return jsonify({"success": True, "count": len(services), "services": [s.to_dict() for s in services]})


# ==================== ERROR HANDLERS ====================


@app.errorhandler(RateLimitExceeded)
def rate_limit_exceeded_handler(error):
    """Rate limit exceeded handler"""
    return handle_rate_limit_exceeded(error)


@app.errorhandler(ValidationError)
def validation_error_handler(error):
    """Validation error handler"""
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "validation_error", "message": str(error)}), 400
    flash(str(error), "error")
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Not found"}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    return render_template("500.html"), 500


# ==================== TEMPLATE FILTERS ====================


@app.template_filter("currency")
def currency_filter(value):
    """Format as currency"""
    try:
        return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",").replace(" ", ".", 1)
    except:
        return value


@app.template_filter("percentage")
def percentage_filter(value):
    """Format as percentage"""
    try:
        return f"{float(value):.2f}%".replace(".", ",")
    except:
        return value


@app.template_filter("datetime")
def datetime_filter(value, format="%d.%m.%Y %H:%M"):
    """Format datetime"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value

    if isinstance(value, datetime):
        return value.strftime(format)

    return value


# ==================== MAIN ====================


def main():
    """Run Flask development server"""
    print("=" * 60)
    print("Document Management System - Web Interface")
    print("=" * 60)
    print()
    print("Starting Flask development server...")
    print("Access the application at: http://localhost:5000")
    print()
    print("Available endpoints:")
    print("  - Dashboard:     http://localhost:5000/")
    print("  - Services:      http://localhost:5000/services")
    print("  - Calculator:    http://localhost:5000/calculator")
    print("  - Generator:     http://localhost:5000/generator")
    print("  - Analytics:     http://localhost:5000/analytics")
    print("  - API:           http://localhost:5000/api/")
    print("  - API Docs:      http://localhost:5000/api/docs (Swagger UI)")
    print("  - API ReDoc:     http://localhost:5000/api/redoc")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Create necessary directories
    os.makedirs("data/exports", exist_ok=True)

    # Run server (debug mode controlled by environment variable)
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
