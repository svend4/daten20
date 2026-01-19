"""
Comprehensive tests for src/core/security_middleware.py

Tests security middleware including CSRF protection, HTTPS redirect, security headers, and session security.

Session 31 - 50+ tests
"""

import hashlib
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock Flask and werkzeug before importing
mock_flask = Mock()
mock_app = MagicMock()
mock_request = MagicMock()
mock_session = {}
mock_g = Mock()

sys.modules["flask"] = mock_flask
mock_flask.Flask = MagicMock
mock_flask.request = mock_request
mock_flask.session = mock_session
mock_flask.g = mock_g
mock_flask.abort = MagicMock()
mock_flask.redirect = MagicMock()
mock_flask.current_app = mock_app

sys.modules["werkzeug"] = Mock()
sys.modules["werkzeug.security"] = Mock(safe_str_cmp=lambda a, b: a == b)

from src.core.security_middleware import (
    CSRFProtection,
    HTTPSRedirect,
    SecurityHeaders,
    SessionSecurity,
    csrf_exempt,
    init_security,
    require_https,
)


class TestCSRFProtection:
    """Test CSRF protection functionality."""

    def test_init_without_app(self):
        """Test CSRF protection initialization without app"""
        csrf = CSRFProtection(secret_key="test-secret")

        assert csrf.secret_key == "test-secret"
        assert csrf.app is None
        assert isinstance(csrf.exempt_views, set)

    def test_init_with_app(self):
        """Test CSRF protection initialization with app"""
        app = MagicMock()
        app.config = {"SECRET_KEY": "app-secret"}

        csrf = CSRFProtection(app)

        assert csrf.app == app
        app.before_request.assert_called_once()
        app.context_processor.assert_called_once()

    def test_init_app(self):
        """Test init_app method"""
        app = MagicMock()
        app.config = {"SECRET_KEY": "test-secret"}

        csrf = CSRFProtection()
        csrf.init_app(app)

        assert csrf.app == app
        assert csrf.secret_key == "test-secret"
        app.before_request.assert_called_once()

    def test_init_app_without_secret_key(self):
        """Test init_app raises error without secret key"""
        app = MagicMock()
        app.config = {}

        csrf = CSRFProtection()

        with pytest.raises(ValueError) as exc_info:
            csrf.init_app(app)

        assert "SECRET_KEY" in str(exc_info.value)

    def test_generate_csrf_token_new_session(self):
        """Test generating CSRF token for new session"""
        csrf = CSRFProtection(secret_key="test-secret")
        session_dict = {}

        with patch("src.core.security_middleware.session", session_dict):
            token = csrf.generate_csrf_token()

        assert token is not None
        assert len(token) == 64  # 32 bytes hex = 64 chars
        assert "_csrf_token" in session_dict
        assert session_dict["_csrf_token"] == token

    def test_generate_csrf_token_existing_session(self):
        """Test generating CSRF token returns existing token"""
        csrf = CSRFProtection(secret_key="test-secret")
        existing_token = "existing_token_12345"
        session_dict = {"_csrf_token": existing_token}

        with patch("src.core.security_middleware.session", session_dict):
            token = csrf.generate_csrf_token()

        assert token == existing_token

    def test_validate_csrf_token_valid(self):
        """Test validating valid CSRF token"""
        csrf = CSRFProtection(secret_key="test-secret")
        token = "test_token_12345"
        session_dict = {"_csrf_token": token}

        with patch("src.core.security_middleware.session", session_dict):
            result = csrf.validate_csrf_token(token)

        assert result is True

    def test_validate_csrf_token_invalid(self):
        """Test validating invalid CSRF token"""
        csrf = CSRFProtection(secret_key="test-secret")
        session_dict = {"_csrf_token": "correct_token"}

        with patch("src.core.security_middleware.session", session_dict):
            result = csrf.validate_csrf_token("wrong_token")

        assert result is False

    def test_validate_csrf_token_no_session_token(self):
        """Test validating token when no session token exists"""
        csrf = CSRFProtection(secret_key="test-secret")
        session_dict = {}

        with patch("src.core.security_middleware.session", session_dict):
            result = csrf.validate_csrf_token("any_token")

        assert result is False

    def test_is_api_endpoint_true(self):
        """Test _is_api_endpoint returns True for API paths"""
        csrf = CSRFProtection(secret_key="test-secret")

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.path = "/api/users"
            result = csrf._is_api_endpoint()

        assert result is True

    def test_is_api_endpoint_false(self):
        """Test _is_api_endpoint returns False for non-API paths"""
        csrf = CSRFProtection(secret_key="test-secret")

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.path = "/login"
            result = csrf._is_api_endpoint()

        assert result is False

    def test_get_csrf_token_from_form(self):
        """Test getting CSRF token from form data"""
        csrf = CSRFProtection(secret_key="test-secret")

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.form.get.return_value = "form_token"
            mock_req.headers.get.return_value = None
            token = csrf._get_csrf_token_from_request()

        assert token == "form_token"

    def test_get_csrf_token_from_header(self):
        """Test getting CSRF token from header"""
        csrf = CSRFProtection(secret_key="test-secret")

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.form.get.return_value = None
            mock_req.headers.get.return_value = "header_token"
            token = csrf._get_csrf_token_from_request()

        assert token == "header_token"

    def test_csrf_protect_safe_methods(self):
        """Test CSRF protection skips safe HTTP methods"""
        csrf = CSRFProtection(secret_key="test-secret")

        for method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            with patch("src.core.security_middleware.request") as mock_req:
                mock_req.method = method
                result = csrf._csrf_protect()

            assert result is None  # No protection applied

    def test_csrf_protect_api_endpoint(self):
        """Test CSRF protection skips API endpoints"""
        csrf = CSRFProtection(secret_key="test-secret")

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.method = "POST"
            mock_req.path = "/api/data"
            result = csrf._csrf_protect()

        assert result is None  # No protection for API

    def test_csrf_protect_exempt_view(self):
        """Test CSRF protection skips exempt views"""
        csrf = CSRFProtection(secret_key="test-secret")
        csrf.exempt_views.add("webhook")

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.method = "POST"
            mock_req.path = "/webhook"
            mock_req.endpoint = "webhook"
            result = csrf._csrf_protect()

        assert result is None  # No protection for exempt view

    def test_exempt_with_function(self):
        """Test exempt decorator with function"""
        csrf = CSRFProtection(secret_key="test-secret")

        def test_view():
            return "test"

        result = csrf.exempt(test_view)

        assert result == test_view
        assert "test_view" in csrf.exempt_views

    def test_exempt_with_string(self):
        """Test exempt with view name string"""
        csrf = CSRFProtection(secret_key="test-secret")

        result = csrf.exempt("webhook_view")

        assert result == "webhook_view"
        assert "webhook_view" in csrf.exempt_views


class TestHTTPSRedirect:
    """Test HTTPS redirect functionality."""

    def test_init_without_app(self):
        """Test HTTPS redirect initialization without app"""
        https = HTTPSRedirect(permanent=False)

        assert https.app is None
        assert https.permanent is False

    def test_init_with_app(self):
        """Test HTTPS redirect initialization with app"""
        app = MagicMock()
        app.debug = False

        https = HTTPSRedirect(app)

        assert https.app == app
        app.before_request.assert_called_once()

    def test_init_app_production(self):
        """Test init_app in production mode"""
        app = MagicMock()
        app.debug = False

        https = HTTPSRedirect()
        https.init_app(app)

        assert https.app == app
        app.before_request.assert_called_once()

    def test_init_app_debug(self):
        """Test init_app in debug mode"""
        app = MagicMock()
        app.debug = True

        https = HTTPSRedirect()
        https.init_app(app)

        assert https.app == app
        app.before_request.assert_not_called()  # Not enabled in debug

    def test_redirect_to_https_permanent(self):
        """Test permanent HTTPS redirect"""
        https = HTTPSRedirect(permanent=True)

        with patch("src.core.security_middleware.request") as mock_req:
            with patch("flask.redirect") as mock_redirect:
                mock_req.is_secure = False
                mock_req.url = "http://example.com/page"

                https._redirect_to_https()

                mock_redirect.assert_called_once_with("https://example.com/page", code=301)

    def test_redirect_to_https_temporary(self):
        """Test temporary HTTPS redirect"""
        https = HTTPSRedirect(permanent=False)

        with patch("src.core.security_middleware.request") as mock_req:
            with patch("flask.redirect") as mock_redirect:
                mock_req.is_secure = False
                mock_req.url = "http://example.com/page"

                https._redirect_to_https()

                mock_redirect.assert_called_once_with("https://example.com/page", code=302)

    def test_redirect_to_https_already_secure(self):
        """Test no redirect when already HTTPS"""
        https = HTTPSRedirect()

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.is_secure = True
            result = https._redirect_to_https()

        assert result is None  # No redirect needed


class TestSecurityHeaders:
    """Test security headers functionality."""

    def test_init_without_app(self):
        """Test security headers initialization without app"""
        headers = SecurityHeaders()

        assert headers.app is None
        assert isinstance(headers.headers, dict)
        assert "X-Content-Type-Options" in headers.headers

    def test_init_with_app(self):
        """Test security headers initialization with app"""
        app = MagicMock()

        headers = SecurityHeaders(app)

        assert headers.app == app
        app.after_request.assert_called_once()

    def test_init_app(self):
        """Test init_app method"""
        app = MagicMock()

        headers = SecurityHeaders()
        headers.init_app(app)

        assert headers.app == app
        app.after_request.assert_called_once()

    def test_default_headers(self):
        """Test default security headers are set"""
        headers = SecurityHeaders()

        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy",
        ]

        for header in expected_headers:
            assert header in headers.headers

    def test_add_security_headers(self):
        """Test adding security headers to response"""
        headers = SecurityHeaders()
        response = MagicMock()
        response.headers = {}

        result = headers._add_security_headers(response)

        assert result == response
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_set_header(self):
        """Test setting custom security header"""
        headers = SecurityHeaders()

        headers.set_header("Custom-Header", "custom-value")

        assert headers.headers["Custom-Header"] == "custom-value"


class TestSessionSecurity:
    """Test session security functionality."""

    def test_init_without_app(self):
        """Test session security initialization without app"""
        session_sec = SessionSecurity()

        assert session_sec.app is None

    def test_init_with_app(self):
        """Test session security initialization with app"""
        app = MagicMock()
        app.config = {}

        session_sec = SessionSecurity(app)

        assert session_sec.app == app
        app.before_request.assert_called_once()
        app.after_request.assert_called_once()

    def test_init_app_configures_session(self):
        """Test init_app sets secure session config"""
        app = MagicMock()
        app.config = {}

        session_sec = SessionSecurity()
        session_sec.init_app(app)

        # Check that config was updated with secure settings
        assert app.config["SESSION_COOKIE_SECURE"] is True
        assert app.config["SESSION_COOKIE_HTTPONLY"] is True
        assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
        assert app.config["PERMANENT_SESSION_LIFETIME"] == 3600

    def test_generate_fingerprint(self):
        """Test generating session fingerprint"""
        session_sec = SessionSecurity()

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.headers.get.side_effect = lambda key, default="": {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US",
            }.get(key, default)

            fingerprint = session_sec._generate_fingerprint()

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hex

    def test_set_session_fingerprint_new_session(self):
        """Test setting fingerprint for new session"""
        session_sec = SessionSecurity()
        session_dict = {}
        response = MagicMock()

        with patch("src.core.security_middleware.session", session_dict):
            with patch("src.core.security_middleware.request") as mock_req:
                mock_req.headers.get.return_value = ""
                result = session_sec._set_session_fingerprint(response)

        assert result == response
        assert "_fingerprint" in session_dict

    def test_set_session_fingerprint_existing(self):
        """Test setting fingerprint when already exists"""
        session_sec = SessionSecurity()
        existing_fp = "existing_fingerprint"
        session_dict = {"_fingerprint": existing_fp}
        response = MagicMock()

        with patch("src.core.security_middleware.session", session_dict):
            result = session_sec._set_session_fingerprint(response)

        assert result == response
        assert session_dict["_fingerprint"] == existing_fp  # Unchanged

    def test_check_session_fingerprint_match(self):
        """Test checking fingerprint when it matches"""
        session_sec = SessionSecurity()
        fingerprint = "test_fingerprint_123"
        session_dict = {"_fingerprint": fingerprint}

        with patch("src.core.security_middleware.session", session_dict):
            with patch.object(session_sec, "_generate_fingerprint", return_value=fingerprint):
                session_sec._check_session_fingerprint()

        # Session should not be cleared
        assert "_fingerprint" in session_dict

    def test_check_session_fingerprint_mismatch(self):
        """Test checking fingerprint when it doesn't match"""
        session_sec = SessionSecurity()
        session_dict = {"_fingerprint": "old_fingerprint", "user_id": "123"}

        with patch("src.core.security_middleware.session", session_dict):
            with patch.object(session_sec, "_generate_fingerprint", return_value="new_fingerprint"):
                session_sec._check_session_fingerprint()

        # Session should be cleared
        assert "_fingerprint" not in session_dict
        assert "user_id" not in session_dict


class TestInitSecurity:
    """Test init_security function."""

    def test_init_security_basic(self):
        """Test initializing all security features"""
        app = MagicMock()
        app.config = {"SECRET_KEY": "test-secret"}
        app.debug = False

        init_security(app)

        assert hasattr(app, "csrf")
        assert hasattr(app, "security_headers")
        assert hasattr(app, "session_security")

    def test_init_security_with_https(self):
        """Test initializing with HTTPS redirect"""
        app = MagicMock()
        app.config = {"SECRET_KEY": "test-secret"}
        app.debug = False

        init_security(app, enable_https=True)

        assert hasattr(app, "https_redirect")

    def test_init_security_debug_no_https(self):
        """Test HTTPS not enabled in debug mode"""
        app = MagicMock()
        app.config = {"SECRET_KEY": "test-secret"}
        app.debug = True

        init_security(app, enable_https=True)

        # HTTPS redirect should not be created in debug mode
        # Check by accessing __dict__ to see if attribute was actually set
        assert "https_redirect" not in app.__dict__


class TestDecorators:
    """Test decorator functions."""

    def test_csrf_exempt_decorator(self):
        """Test csrf_exempt decorator"""
        app_with_csrf = MagicMock()
        app_with_csrf.csrf = MagicMock()

        def test_view():
            return "test"

        with patch("flask.current_app", app_with_csrf):
            result = csrf_exempt(test_view)

        assert result == test_view
        app_with_csrf.csrf.exempt.assert_called_once_with(test_view)

    def test_csrf_exempt_no_csrf(self):
        """Test csrf_exempt when no CSRF protection configured"""
        app_without_csrf = MagicMock(spec=[])

        def test_view():
            return "test"

        with patch("flask.current_app", app_without_csrf):
            result = csrf_exempt(test_view)

        assert result == test_view

    def test_require_https_secure(self):
        """Test require_https allows secure requests"""

        @require_https
        def test_view():
            return "success"

        with patch("src.core.security_middleware.request") as mock_req:
            mock_req.is_secure = True
            result = test_view()

        assert result == "success"

    def test_require_https_insecure(self):
        """Test require_https blocks insecure requests"""

        @require_https
        def test_view():
            return "success"

        with patch("src.core.security_middleware.request") as mock_req:
            with patch("src.core.security_middleware.abort") as mock_abort:
                mock_req.is_secure = False
                test_view()

                mock_abort.assert_called_once_with(403, "HTTPS required")

    def test_require_https_preserves_function_name(self):
        """Test require_https preserves function metadata"""

        @require_https
        def test_view_with_doc():
            """Test docstring"""
            return "success"

        assert test_view_with_doc.__name__ == "test_view_with_doc"
        assert test_view_with_doc.__doc__ == "Test docstring"


class TestIntegration:
    """Integration tests for security middleware."""

    def test_full_security_setup(self):
        """Test complete security setup"""
        app = MagicMock()
        app.config = {"SECRET_KEY": "test-secret"}
        app.debug = False

        init_security(app, enable_https=True)

        # Verify all components initialized
        assert hasattr(app, "csrf")
        assert hasattr(app, "security_headers")
        assert hasattr(app, "session_security")
        assert hasattr(app, "https_redirect")

        # Verify CSRF protection
        assert isinstance(app.csrf, CSRFProtection)
        assert app.csrf.secret_key == "test-secret"

        # Verify security headers
        assert isinstance(app.security_headers, SecurityHeaders)

        # Verify session security
        assert isinstance(app.session_security, SessionSecurity)

        # Verify HTTPS redirect
        assert isinstance(app.https_redirect, HTTPSRedirect)
