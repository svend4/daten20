"""
API Module

REST API endpoints for the Document Management System.
"""

from flask import Flask

__version__ = "1.0.0"


def register_blueprints(app: Flask):
    """
    Register all API blueprints with the Flask app

    Args:
        app: Flask application instance
    """
    # Import blueprints
    try:
        from src.api.semantic_search_api import semantic_search_bp
        app.register_blueprint(semantic_search_bp)
    except ImportError:
        pass

    try:
        from src.api.translation_api import translation_bp
        app.register_blueprint(translation_bp)
    except ImportError:
        pass
