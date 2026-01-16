"""
Security Middleware

Provides HTTPS enforcement and CSRF protection for Flask applications.

Features:
- HTTPS redirect
- Secure headers (HSTS, CSP, X-Frame-Options, etc.)
- CSRF token generation and validation
- Session security
"""

import hashlib
import hmac
import logging
import secrets
from functools import wraps
from typing import List, Optional

from flask import Flask, abort, g, request, session
from werkzeug.security import safe_str_cmp

logger = logging.getLogger("dms.security")


class CSRFProtection:
    """
    CSRF (Cross-Site Request Forgery) Protection.

    Generates and validates CSRF tokens for forms and AJAX requests.
    """

    def __init__(self, app: Optional[Flask] = None, secret_key: Optional[str] = None):
        """
        Initialize CSRF protection.

        Args:
            app: Flask application
            secret_key: Secret key for HMAC
        """
        self.app = app
        self.secret_key = secret_key
        self.exempt_views = set()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize with Flask app.

        Args:
            app: Flask application
        """
        self.app = app

        # Use app secret key if not provided
        if not self.secret_key:
            self.secret_key = app.config.get("SECRET_KEY")

        if not self.secret_key:
            raise ValueError("SECRET_KEY must be set for CSRF protection")

        # Register before_request handler
        app.before_request(self._csrf_protect)

        # Register template context processor
        @app.context_processor
        def csrf_token():
            return dict(csrf_token=self.generate_csrf_token)

        logger.info("CSRF protection initialized")

    def _csrf_protect(self):
        """Protect against CSRF attacks."""
        # Skip for GET, HEAD, OPTIONS, TRACE (safe methods)
        if request.method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            return

        # Skip for API endpoints with token authentication
        if self._is_api_endpoint():
            return

        # Skip if view is exempt
        if request.endpoint in self.exempt_views:
            return

        # Get CSRF token from request
        token = self._get_csrf_token_from_request()

        if not token:
            logger.warning(f"CSRF token missing for {request.endpoint}")
            abort(400, "CSRF token missing")

        # Validate token
        if not self.validate_csrf_token(token):
            logger.warning(f"CSRF token invalid for {request.endpoint}")
            abort(403, "CSRF token invalid")

    def _is_api_endpoint(self) -> bool:
        """Check if current endpoint is API endpoint."""
        return request.path.startswith("/api/")

    def _get_csrf_token_from_request(self) -> Optional[str]:
        """Get CSRF token from request."""
        # Check form data
        token = request.form.get("csrf_token")

        # Check headers (for AJAX)
        if not token:
            token = request.headers.get("X-CSRF-Token")

        return token

    def generate_csrf_token(self) -> str:
        """
        Generate CSRF token for current session.

        Returns:
            CSRF token string
        """
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_hex(32)

        return session["_csrf_token"]

    def validate_csrf_token(self, token: str) -> bool:
        """
        Validate CSRF token.

        Args:
            token: CSRF token to validate

        Returns:
            True if valid
        """
        session_token = session.get("_csrf_token")

        if not session_token:
            return False

        # Use constant-time comparison
        return safe_str_cmp(token, session_token)

    def exempt(self, view):
        """
        Decorator to exempt view from CSRF protection.

        Args:
            view: View function
        """
        if isinstance(view, str):
            self.exempt_views.add(view)
            return view
        else:
            self.exempt_views.add(view.__name__)
            return view


class HTTPSRedirect:
    """
    HTTPS redirect middleware.

    Redirects HTTP requests to HTTPS in production.
    """

    def __init__(self, app: Optional[Flask] = None, permanent: bool = True):
        """
        Initialize HTTPS redirect.

        Args:
            app: Flask application
            permanent: Use 301 (permanent) instead of 302 redirect
        """
        self.app = app
        self.permanent = permanent

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize with Flask app.

        Args:
            app: Flask application
        """
        self.app = app

        # Only enable in production
        if not app.debug:
            app.before_request(self._redirect_to_https)
            logger.info("HTTPS redirect enabled")

    def _redirect_to_https(self):
        """Redirect HTTP to HTTPS."""
        if not request.is_secure:
            from flask import redirect

            url = request.url.replace("http://", "https://", 1)
            code = 301 if self.permanent else 302

            logger.debug(f"Redirecting to HTTPS: {url}")
            return redirect(url, code=code)


class SecurityHeaders:
    """
    Security headers middleware.

    Adds security-related HTTP headers to responses.
    """

    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize security headers.

        Args:
            app: Flask application
        """
        self.app = app

        # Default headers
        self.headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": ("geolocation=(), microphone=(), camera=()"),
        }

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize with Flask app.

        Args:
            app: Flask application
        """
        self.app = app
        app.after_request(self._add_security_headers)
        logger.info("Security headers enabled")

    def _add_security_headers(self, response):
        """Add security headers to response."""
        for header, value in self.headers.items():
            response.headers[header] = value
        return response

    def set_header(self, name: str, value: str):
        """
        Set custom security header.

        Args:
            name: Header name
            value: Header value
        """
        self.headers[name] = value


class SessionSecurity:
    """
    Session security enhancements.

    Adds security features to Flask sessions.
    """

    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize session security.

        Args:
            app: Flask application
        """
        self.app = app

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize with Flask app.

        Args:
            app: Flask application
        """
        self.app = app

        # Configure session security
        app.config.update(
            SESSION_COOKIE_SECURE=True,  # Only send over HTTPS
            SESSION_COOKIE_HTTPONLY=True,  # Not accessible via JavaScript
            SESSION_COOKIE_SAMESITE="Lax",  # CSRF protection
            PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
        )

        # Add session fingerprinting
        app.before_request(self._check_session_fingerprint)
        app.after_request(self._set_session_fingerprint)

        logger.info("Session security enabled")

    def _check_session_fingerprint(self):
        """Check session fingerprint to detect hijacking."""
        if "_fingerprint" in session:
            current_fingerprint = self._generate_fingerprint()

            if not safe_str_cmp(session["_fingerprint"], current_fingerprint):
                logger.warning("Session fingerprint mismatch - possible hijacking")
                session.clear()

    def _set_session_fingerprint(self, response):
        """Set session fingerprint."""
        if "_fingerprint" not in session:
            session["_fingerprint"] = self._generate_fingerprint()
        return response

    def _generate_fingerprint(self) -> str:
        """
        Generate session fingerprint from request metadata.

        Returns:
            Fingerprint string
        """
        # Use User-Agent and Accept-Language for fingerprinting
        user_agent = request.headers.get("User-Agent", "")
        accept_language = request.headers.get("Accept-Language", "")

        data = f"{user_agent}:{accept_language}"

        # Hash the data
        return hashlib.sha256(data.encode()).hexdigest()


def init_security(app: Flask, enable_https: bool = False):
    """
    Initialize all security features.

    Args:
        app: Flask application
        enable_https: Enable HTTPS redirect (only in production)
    """
    # CSRF Protection
    csrf = CSRFProtection(app)
    app.csrf = csrf

    # Security Headers
    security_headers = SecurityHeaders(app)
    app.security_headers = security_headers

    # Session Security
    session_security = SessionSecurity(app)
    app.session_security = session_security

    # HTTPS Redirect (optional, only in production)
    if enable_https and not app.debug:
        https_redirect = HTTPSRedirect(app)
        app.https_redirect = https_redirect

    logger.info("All security features initialized")


# Decorators


def csrf_exempt(view):
    """
    Decorator to exempt view from CSRF protection.

    Example:
        @app.route('/webhook', methods=['POST'])
        @csrf_exempt
        def webhook():
            return 'OK'
    """
    from flask import current_app

    if hasattr(current_app, "csrf"):
        current_app.csrf.exempt(view)

    return view


def require_https(f):
    """
    Decorator to require HTTPS for specific view.

    Example:
        @app.route('/login', methods=['POST'])
        @require_https
        def login():
            # ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure:
            logger.warning(f"HTTPS required for {f.__name__}")
            abort(403, "HTTPS required")
        return f(*args, **kwargs)

    return decorated_function
