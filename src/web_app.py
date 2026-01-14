#!/usr/bin/env python3
"""
Web Application - Flask веб-интерфейс

Полнофункциональный веб-интерфейс для управления документами
социальных услуг с REST API, dashboard и визуальными редакторами.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flasgger import Swagger

from src.core.database import Database
from src.core.parser import TemplateParser
from src.core.validator import TemplateValidator
from src.models.service import Service
from src.financial_calculator import FinancialCalculator
from src.document_generator import DocumentGenerator
from src.service_manager import ServiceManager
from src.utils.helpers import load_config, save_config
from src.utils.constants import SERVICE_TYPES, REGIONAL_COEFFICIENTS, FUNDING_SOURCES
from src.api_docs import api_docs_bp

# Initialize Flask app
app = Flask(__name__,
            template_folder='../web/templates',
            static_folder='../web/static')
app.secret_key = 'your-secret-key-change-in-production'  # Change in production!
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Swagger UI
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/api/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Document Management System API",
        "description": "REST API for Document Management System",
        "version": "4.1.0",
        "contact": {
            "name": "DMS Support",
            "url": "https://github.com/svend4/daten20"
        }
    },
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header"
        }
    },
    "security": [
        {
            "ApiKeyAuth": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Register API documentation blueprint
app.register_blueprint(api_docs_bp)

# Initialize components
db = Database()
calculator = FinancialCalculator()
generator = DocumentGenerator()
validator = TemplateValidator()
parser = TemplateParser('mSchablone')


# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    """Main dashboard page"""
    stats = db.get_statistics()
    recent_services = db.list_services(limit=5)

    return render_template('dashboard.html',
                          stats=stats,
                          recent_services=recent_services,
                          page='dashboard')


@app.route('/services')
def services_list():
    """List all services"""
    region = request.args.get('region')
    service_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    per_page = 20

    services = db.list_services(
        limit=per_page,
        offset=(page - 1) * per_page,
        region=region,
        service_type=service_type
    )

    return render_template('services_list.html',
                          services=services,
                          page='services',
                          current_page=page,
                          regions=REGIONAL_COEFFICIENTS.keys(),
                          service_types=SERVICE_TYPES)


@app.route('/services/<int:service_id>')
def service_detail(service_id):
    """Service detail page"""
    service = db.get_service(service_id)

    if not service:
        flash('Услуга не найдена', 'error')
        return redirect(url_for('services_list'))

    # Calculate cost breakdown
    breakdown = calculator.calculate_hourly_rate(service.financial)
    versions = db.get_service_versions(service_id)

    return render_template('service_detail.html',
                          service=service,
                          breakdown=breakdown,
                          versions=versions,
                          page='services')


@app.route('/services/new', methods=['GET', 'POST'])
def service_new():
    """Create new service"""
    if request.method == 'POST':
        try:
            # Build service from form data
            service = Service()

            # Basic info
            service.basic_info.service_name = request.form.get('service_name')
            service.basic_info.target_group = request.form.get('target_group')
            service.basic_info.region = request.form.get('region')
            service.basic_info.provider_type = request.form.get('provider_type')
            service.basic_info.document_date = request.form.get('document_date')
            service.basic_info.responsible_person = request.form.get('responsible_person')

            # Financial
            service.financial.brutto_rate = Decimal(request.form.get('brutto_rate', '0'))
            service.financial.materials_per_month = Decimal(request.form.get('materials_per_month', '0'))
            service.financial.admin_percent = Decimal(request.form.get('admin_percent', '5'))

            region_coef = REGIONAL_COEFFICIENTS.get(service.basic_info.region, 1.0)
            service.financial.region_coefficient = Decimal(str(region_coef))
            service.financial.is_saxony = (service.basic_info.region == 'Sachsen')

            # System settings
            service.system_settings.use_umlages = request.form.get('use_umlages') == 'true'
            service.system_settings.use_vacation_reserve = not service.system_settings.use_umlages
            service.system_settings.service_type = request.form.get('service_type', 'social')
            service.system_settings.surcharge_base = request.form.get('surcharge_base', 'full_cost')

            service.financial.use_umlages = service.system_settings.use_umlages
            service.financial.use_vacation_reserve = service.system_settings.use_vacation_reserve
            service.financial.surcharge_base = service.system_settings.surcharge_base

            # Funding
            service.funding.payer = request.form.get('payer', '')

            # Validate
            validation = validator.validate_config(service.to_dict())
            if not validation.is_valid:
                for error in validation.errors:
                    flash(error, 'error')
                return render_template('service_form.html',
                                     service=service,
                                     regions=REGIONAL_COEFFICIENTS.keys(),
                                     service_types=SERVICE_TYPES,
                                     funding_sources=FUNDING_SOURCES,
                                     page='services')

            # Save to database
            service_id = db.create_service(service)
            flash(f'Услуга "{service.basic_info.service_name}" создана успешно!', 'success')
            return redirect(url_for('service_detail', service_id=service_id))

        except Exception as e:
            flash(f'Ошибка при создании услуги: {str(e)}', 'error')

    # GET request - show form
    return render_template('service_form.html',
                          service=Service(),
                          regions=REGIONAL_COEFFICIENTS.keys(),
                          service_types=SERVICE_TYPES,
                          funding_sources=FUNDING_SOURCES,
                          page='services')


@app.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
def service_edit(service_id):
    """Edit existing service"""
    service = db.get_service(service_id)

    if not service:
        flash('Услуга не найдена', 'error')
        return redirect(url_for('services_list'))

    if request.method == 'POST':
        try:
            # Update service from form
            service.basic_info.service_name = request.form.get('service_name')
            service.basic_info.target_group = request.form.get('target_group')
            service.basic_info.region = request.form.get('region')
            service.basic_info.provider_type = request.form.get('provider_type')
            service.basic_info.document_date = request.form.get('document_date')
            service.basic_info.responsible_person = request.form.get('responsible_person')

            service.financial.brutto_rate = Decimal(request.form.get('brutto_rate', '0'))
            service.financial.materials_per_month = Decimal(request.form.get('materials_per_month', '0'))
            service.financial.admin_percent = Decimal(request.form.get('admin_percent', '5'))

            region_coef = REGIONAL_COEFFICIENTS.get(service.basic_info.region, 1.0)
            service.financial.region_coefficient = Decimal(str(region_coef))

            service.system_settings.use_umlages = request.form.get('use_umlages') == 'true'
            service.system_settings.service_type = request.form.get('service_type', 'social')

            db.update_service(service)
            flash('Услуга обновлена успешно!', 'success')
            return redirect(url_for('service_detail', service_id=service_id))

        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'error')

    return render_template('service_form.html',
                          service=service,
                          regions=REGIONAL_COEFFICIENTS.keys(),
                          service_types=SERVICE_TYPES,
                          funding_sources=FUNDING_SOURCES,
                          edit_mode=True,
                          page='services')


@app.route('/services/<int:service_id>/delete', methods=['POST'])
def service_delete(service_id):
    """Delete service"""
    if db.delete_service(service_id):
        flash('Услуга удалена', 'success')
    else:
        flash('Ошибка при удалении', 'error')

    return redirect(url_for('services_list'))


@app.route('/calculator', methods=['GET', 'POST'])
def calculator_page():
    """Financial calculator page"""
    result = None

    if request.method == 'POST':
        try:
            from src.models.financial import FinancialParameters

            params = FinancialParameters(
                brutto_rate=Decimal(request.form.get('brutto_rate', '0'))
            )

            region = request.form.get('region')
            if region:
                params.region_coefficient = Decimal(str(REGIONAL_COEFFICIENTS.get(region, 1.0)))

            params.materials_per_month = Decimal(request.form.get('materials', '0'))
            params.admin_percent = Decimal(request.form.get('admin', '5'))
            params.use_umlages = request.form.get('mode') != 'reserve'
            params.use_vacation_reserve = not params.use_umlages

            breakdown = calculator.calculate_hourly_rate(params)
            result = breakdown

        except Exception as e:
            flash(f'Ошибка расчета: {str(e)}', 'error')

    return render_template('calculator.html',
                          result=result,
                          regions=REGIONAL_COEFFICIENTS.keys(),
                          page='calculator')


@app.route('/generator', methods=['GET', 'POST'])
def generator_page():
    """Document generator page"""
    if request.method == 'POST':
        try:
            service_id = request.form.get('service_id')
            output_format = request.form.get('format', 'html')

            service = db.get_service(int(service_id))
            if not service:
                flash('Услуга не найдена', 'error')
                return redirect(url_for('generator_page'))

            # Generate document
            if not generator.load_template():
                flash('Ошибка загрузки шаблона', 'error')
                return redirect(url_for('generator_page'))

            filled_content = generator.fill_from_service(service)

            # Save to exports
            filename = f"service_{service_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            output_path = f"data/exports/{filename}"

            if output_format == 'html':
                generator.exporter.export_to_html(filled_content, output_path, service.basic_info.service_name)
            elif output_format == 'txt':
                generator.exporter.export_to_text(filled_content, output_path)
            elif output_format == 'md':
                generator.exporter.export_to_markdown(filled_content, output_path)

            flash(f'Документ создан: {filename}', 'success')
            return send_file(output_path, as_attachment=True)

        except Exception as e:
            flash(f'Ошибка генерации: {str(e)}', 'error')

    # List services for selection
    services = db.list_services(limit=100)

    return render_template('generator.html',
                          services=services,
                          page='generator')


@app.route('/analytics')
def analytics_page():
    """Analytics and reports page"""
    stats = db.get_statistics()

    # Get all services for analysis
    all_services = db.list_services(limit=1000)

    # Calculate additional stats
    if all_services:
        rates = [float(s.financial.brutto_rate) for s in all_services if s.financial.brutto_rate]
        stats['min_rate'] = min(rates) if rates else 0
        stats['max_rate'] = max(rates) if rates else 0
        stats['median_rate'] = sorted(rates)[len(rates)//2] if rates else 0

    return render_template('analytics.html',
                          stats=stats,
                          services=all_services,
                          page='analytics')


@app.route('/search')
def search_page():
    """Search services"""
    query = request.args.get('q', '')

    if query:
        services = db.search_services(query)
    else:
        services = []

    return render_template('search.html',
                          query=query,
                          services=services,
                          page='search')


# ==================== REST API ROUTES ====================

@app.route('/api/services', methods=['GET'])
def api_services_list():
    """API: List all services"""
    region = request.args.get('region')
    service_type = request.args.get('type')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    services = db.list_services(limit=limit, offset=offset, region=region, service_type=service_type)

    return jsonify({
        'success': True,
        'count': len(services),
        'services': [s.to_dict() for s in services]
    })


@app.route('/api/services/<int:service_id>', methods=['GET'])
def api_service_get(service_id):
    """API: Get service by ID"""
    service = db.get_service(service_id)

    if not service:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    return jsonify({
        'success': True,
        'service': service.to_dict()
    })


@app.route('/api/services', methods=['POST'])
def api_service_create():
    """API: Create new service"""
    try:
        data = request.get_json()
        service = Service.from_dict(data)

        # Validate
        validation = validator.validate_config(service.to_dict())
        if not validation.is_valid:
            return jsonify({
                'success': False,
                'errors': validation.errors,
                'missing': validation.missing_required
            }), 400

        # Create
        service_id = db.create_service(service)

        return jsonify({
            'success': True,
            'service_id': service_id,
            'message': 'Service created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/services/<int:service_id>', methods=['PUT'])
def api_service_update(service_id):
    """API: Update service"""
    try:
        service = db.get_service(service_id)
        if not service:
            return jsonify({'success': False, 'error': 'Service not found'}), 404

        data = request.get_json()
        updated_service = Service.from_dict(data)
        updated_service.id = service_id

        db.update_service(updated_service)

        return jsonify({
            'success': True,
            'message': 'Service updated successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/services/<int:service_id>', methods=['DELETE'])
def api_service_delete(service_id):
    """API: Delete service"""
    if db.delete_service(service_id):
        return jsonify({
            'success': True,
            'message': 'Service deleted successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404


@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API: Calculate service cost"""
    try:
        from src.models.financial import FinancialParameters

        data = request.get_json()

        params = FinancialParameters(
            brutto_rate=Decimal(str(data.get('brutto_rate', 0)))
        )

        if 'region' in data:
            params.region_coefficient = Decimal(str(REGIONAL_COEFFICIENTS.get(data['region'], 1.0)))

        if 'materials_per_month' in data:
            params.materials_per_month = Decimal(str(data['materials_per_month']))

        if 'admin_percent' in data:
            params.admin_percent = Decimal(str(data['admin_percent']))

        params.use_umlages = data.get('use_umlages', True)
        params.use_vacation_reserve = not params.use_umlages

        breakdown = calculator.calculate_hourly_rate(params)

        return jsonify({
            'success': True,
            'breakdown': breakdown.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/statistics', methods=['GET'])
def api_statistics():
    """API: Get statistics"""
    stats = db.get_statistics()

    return jsonify({
        'success': True,
        'statistics': stats
    })


@app.route('/api/search', methods=['GET'])
def api_search():
    """API: Search services"""
    query = request.args.get('q', '')

    if not query:
        return jsonify({
            'success': False,
            'error': 'Query parameter required'
        }), 400

    services = db.search_services(query)

    return jsonify({
        'success': True,
        'count': len(services),
        'services': [s.to_dict() for s in services]
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# ==================== TEMPLATE FILTERS ====================

@app.template_filter('currency')
def currency_filter(value):
    """Format as currency"""
    try:
        return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",").replace(" ", ".", 1)
    except:
        return value


@app.template_filter('percentage')
def percentage_filter(value):
    """Format as percentage"""
    try:
        return f"{float(value):.2f}%".replace(".", ",")
    except:
        return value


@app.template_filter('datetime')
def datetime_filter(value, format='%d.%m.%Y %H:%M'):
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
    os.makedirs('data/exports', exist_ok=True)

    # Run server
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
