"""
API Documentation Routes
========================

Swagger UI and ReDoc integration for API documentation.
"""

from flask import Blueprint, send_from_directory, render_template_string
import os
import yaml

api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api')

# Path to OpenAPI spec
OPENAPI_SPEC_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'api', 'openapi.yaml')


@api_docs_bp.route('/openapi.yaml')
def openapi_spec():
    """
    Serve OpenAPI specification file
    ---
    tags:
      - Documentation
    responses:
      200:
        description: OpenAPI specification in YAML format
    """
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'docs', 'api'),
        'openapi.yaml',
        mimetype='text/yaml'
    )


@api_docs_bp.route('/openapi.json')
def openapi_spec_json():
    """
    Serve OpenAPI specification as JSON
    ---
    tags:
      - Documentation
    responses:
      200:
        description: OpenAPI specification in JSON format
    """
    import json

    with open(OPENAPI_SPEC_PATH, 'r') as f:
        spec = yaml.safe_load(f)

    return json.dumps(spec), 200, {'Content-Type': 'application/json'}


@api_docs_bp.route('/docs')
def swagger_ui():
    """
    Swagger UI for API documentation
    """
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DMS API Documentation - Swagger UI</title>
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.0/swagger-ui.min.css">
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.0/swagger-ui-bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.0/swagger-ui-standalone-preset.min.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/api/openapi.yaml",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


@api_docs_bp.route('/redoc')
def redoc_ui():
    """
    ReDoc UI for API documentation
    """
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DMS API Documentation - ReDoc</title>
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <redoc spec-url="/api/openapi.yaml"></redoc>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html)


@api_docs_bp.route('/')
def api_root():
    """
    API documentation index page
    """
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DMS API Documentation</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 60px;
                max-width: 800px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 20px;
                font-weight: 700;
            }
            .subtitle {
                color: #666;
                font-size: 1.2em;
                margin-bottom: 40px;
            }
            .version {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-bottom: 30px;
            }
            .links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .link-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-decoration: none;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .link-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            .link-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
            }
            .link-title {
                font-size: 1.3em;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .link-desc {
                font-size: 0.9em;
                opacity: 0.9;
            }
            .features {
                margin-top: 50px;
                text-align: left;
            }
            .features h2 {
                color: #333;
                margin-bottom: 20px;
            }
            .feature-list {
                list-style: none;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }
            .feature-list li {
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                color: #555;
            }
            .feature-list li:before {
                content: "✓ ";
                color: #667eea;
                font-weight: bold;
                margin-right: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 Document Management System</h1>
            <div class="version">v4.1.0</div>
            <p class="subtitle">
                Comprehensive REST API with AI/ML capabilities
            </p>

            <div class="links">
                <a href="/api/docs" class="link-card">
                    <div class="link-icon">📖</div>
                    <div class="link-title">Swagger UI</div>
                    <div class="link-desc">Interactive API documentation</div>
                </a>

                <a href="/api/redoc" class="link-card">
                    <div class="link-icon">📚</div>
                    <div class="link-title">ReDoc</div>
                    <div class="link-desc">Beautiful API reference</div>
                </a>

                <a href="/api/openapi.yaml" class="link-card">
                    <div class="link-icon">📄</div>
                    <div class="link-title">OpenAPI Spec</div>
                    <div class="link-desc">Download YAML spec</div>
                </a>

                <a href="/api/openapi.json" class="link-card">
                    <div class="link-icon">{ }</div>
                    <div class="link-title">OpenAPI JSON</div>
                    <div class="link-desc">Download JSON spec</div>
                </a>
            </div>

            <div class="features">
                <h2>✨ API Features</h2>
                <ul class="feature-list">
                    <li>Document processing and analysis</li>
                    <li>Named Entity Recognition (NER)</li>
                    <li>Document classification</li>
                    <li>Knowledge graph construction</li>
                    <li>Financial calculations</li>
                    <li>Service management</li>
                    <li>Batch processing</li>
                    <li>Full-text search</li>
                    <li>API key authentication</li>
                    <li>Rate limiting</li>
                    <li>RESTful design</li>
                    <li>OpenAPI 3.0 compliant</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)
