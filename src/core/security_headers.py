"""
Security Headers Module

Comprehensive HTTP security headers to protect against XSS, clickjacking,
MIME sniffing, and other web vulnerabilities.

Features:
- XSS Protection headers
- Content Security Policy (CSP)
- Clickjacking protection
- MIME type sniffing prevention
- HTTPS enforcement (HSTS)
- Referrer policy
- Permissions policy
"""

from flask import Flask, Response, request
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeaders:
    """
    Security headers middleware for Flask applications.

    Automatically adds security headers to all HTTP responses to protect
    against common web vulnerabilities.
    """

    def __init__(self, app: Optional[Flask] = None, config: Optional[Dict] = None):
        """
        Initialize security headers.

        Args:
            app: Flask application instance
            config: Optional configuration dictionary
        """
        self.config = self._get_default_config()

        if config:
            self.config.update(config)

        if app:
            self.init_app(app)

    def _get_default_config(self) -> Dict[str, str]:
        """Get default security headers configuration."""
        return {
            # XSS Protection
            'X-XSS-Protection': '1; mode=block',

            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',

            # Clickjacking protection
            'X-Frame-Options': 'SAMEORIGIN',

            # HTTPS enforcement (1 year)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',

            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',

            # Content Security Policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://cdn.jsdelivr.net https://unpkg.com; "
                "connect-src 'self'; "
                "frame-ancestors 'self'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),

            # Permissions Policy (Feature Policy)
            'Permissions-Policy': (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            ),

            # Cross-Origin policies
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Embedder-Policy': 'require-corp',
            'Cross-Origin-Resource-Policy': 'same-origin',

            # Additional security headers
            'X-Permitted-Cross-Domain-Policies': 'none',
            'X-Download-Options': 'noopen',
        }

    def init_app(self, app: Flask):
        """
        Initialize security headers for Flask app.

        Args:
            app: Flask application instance
        """
        @app.after_request
        def add_security_headers(response: Response) -> Response:
            """Add security headers to every response."""
            # Skip if disabled for this route
            if hasattr(response, '_skip_security_headers') and response._skip_security_headers:
                return response

            # Add all configured headers
            for header, value in self.config.items():
                # Don't override existing headers
                if header not in response.headers:
                    response.headers[header] = value

            # Remove server header (security by obscurity)
            response.headers.pop('Server', None)

            # Add custom X-Powered-By header
            response.headers['X-Powered-By'] = 'Document Management System'

            return response

        logger.info("Security headers initialized")

    def set_header(self, header: str, value: str):
        """
        Set or update a security header.

        Args:
            header: Header name
            value: Header value
        """
        self.config[header] = value
        logger.debug(f"Security header updated: {header}")

    def remove_header(self, header: str):
        """
        Remove a security header.

        Args:
            header: Header name to remove
        """
        if header in self.config:
            del self.config[header]
            logger.debug(f"Security header removed: {header}")

    def get_csp_strict(self) -> str:
        """
        Get strict Content Security Policy.

        More restrictive CSP for production environments.

        Returns:
            Strict CSP string
        """
        return (
            "default-src 'none'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    def get_csp_relaxed(self) -> str:
        """
        Get relaxed Content Security Policy.

        More permissive CSP for development.

        Returns:
            Relaxed CSP string
        """
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    def enable_cors(
        self,
        origins: str = '*',
        methods: str = 'GET, POST, PUT, DELETE, OPTIONS',
        headers: str = 'Content-Type, Authorization',
        max_age: int = 3600
    ):
        """
        Enable CORS headers.

        Args:
            origins: Allowed origins
            methods: Allowed methods
            headers: Allowed headers
            max_age: Preflight cache duration
        """
        self.config.update({
            'Access-Control-Allow-Origin': origins,
            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': headers,
            'Access-Control-Max-Age': str(max_age),
        })
        logger.info(f"CORS enabled for origins: {origins}")


def create_security_headers(
    app: Flask,
    enable_hsts: bool = True,
    csp_mode: str = 'default',
    enable_cors: bool = False,
    cors_origins: str = '*'
) -> SecurityHeaders:
    """
    Create and configure security headers for Flask app.

    Args:
        app: Flask application
        enable_hsts: Enable HTTPS enforcement
        csp_mode: CSP mode ('strict', 'relaxed', 'default')
        enable_cors: Enable CORS
        cors_origins: CORS allowed origins

    Returns:
        Configured SecurityHeaders instance
    """
    security = SecurityHeaders(app)

    # Disable HSTS if requested (e.g., for local development)
    if not enable_hsts:
        security.remove_header('Strict-Transport-Security')
        logger.warning("HSTS disabled - not recommended for production!")

    # Set CSP based on mode
    if csp_mode == 'strict':
        security.set_header('Content-Security-Policy', security.get_csp_strict())
    elif csp_mode == 'relaxed':
        security.set_header('Content-Security-Policy', security.get_csp_relaxed())

    # Enable CORS if requested
    if enable_cors:
        security.enable_cors(origins=cors_origins)

    return security


def skip_security_headers():
    """
    Decorator to skip security headers for a specific route.

    Usage:
        @app.route('/api/public')
        @skip_security_headers()
        def public_api():
            return {'data': 'public'}
    """
    def decorator(f: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            response = f(*args, **kwargs)
            if isinstance(response, Response):
                response._skip_security_headers = True
            return response
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


# Global instance
_security_headers_instance: Optional[SecurityHeaders] = None


def get_security_headers() -> Optional[SecurityHeaders]:
    """Get global security headers instance."""
    return _security_headers_instance


def init_security_headers(
    app: Flask,
    enable_hsts: bool = True,
    csp_mode: str = 'default',
    enable_cors: bool = False,
    cors_origins: str = '*'
) -> SecurityHeaders:
    """
    Initialize security headers for Flask application.

    Args:
        app: Flask application
        enable_hsts: Enable HTTPS enforcement
        csp_mode: CSP mode ('strict', 'relaxed', 'default')
        enable_cors: Enable CORS
        cors_origins: CORS allowed origins

    Returns:
        SecurityHeaders instance
    """
    global _security_headers_instance

    _security_headers_instance = create_security_headers(
        app=app,
        enable_hsts=enable_hsts,
        csp_mode=csp_mode,
        enable_cors=enable_cors,
        cors_origins=cors_origins
    )

    logger.info("Security headers initialized for application")
    return _security_headers_instance


# Convenience function for quick setup
def secure_flask_app(
    app: Flask,
    production: bool = False,
    enable_cors: bool = False
) -> SecurityHeaders:
    """
    Quick setup for securing Flask application.

    Args:
        app: Flask application
        production: Whether this is production (enables stricter settings)
        enable_cors: Enable CORS

    Returns:
        SecurityHeaders instance
    """
    return init_security_headers(
        app=app,
        enable_hsts=production,
        csp_mode='strict' if production else 'default',
        enable_cors=enable_cors,
        cors_origins='*' if not production else 'self'
    )
