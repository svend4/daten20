"""
Unit tests for security headers module
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

# Check if Flask is available
try:
    import flask
    from src.core.security_headers import (
        SecurityHeaders,
        create_security_headers,
        init_security_headers,
        secure_flask_app,
        skip_security_headers,
    )
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    SecurityHeaders = None
    create_security_headers = None
    init_security_headers = None
    secure_flask_app = None
    skip_security_headers = None

pytestmark = pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")


# ============================================================================
# SecurityHeaders Tests
# ============================================================================


class TestSecurityHeaders:
    """Test SecurityHeaders class"""

    def test_init_without_app(self):
        """Test initialization without app"""
        security = SecurityHeaders()

        assert security.config is not None
        assert "X-XSS-Protection" in security.config

    def test_init_with_custom_config(self):
        """Test initialization with custom config"""
        custom_config = {"Custom-Header": "CustomValue"}
        security = SecurityHeaders(config=custom_config)

        assert "Custom-Header" in security.config
        assert security.config["Custom-Header"] == "CustomValue"

    def test_default_config_has_xss_protection(self):
        """Test default config includes XSS protection"""
        security = SecurityHeaders()

        assert "X-XSS-Protection" in security.config
        assert "1; mode=block" in security.config["X-XSS-Protection"]

    def test_default_config_has_content_type_options(self):
        """Test default config includes content type options"""
        security = SecurityHeaders()

        assert "X-Content-Type-Options" in security.config
        assert security.config["X-Content-Type-Options"] == "nosniff"

    def test_default_config_has_frame_options(self):
        """Test default config includes frame options"""
        security = SecurityHeaders()

        assert "X-Frame-Options" in security.config
        assert "SAMEORIGIN" in security.config["X-Frame-Options"]

    def test_default_config_has_hsts(self):
        """Test default config includes HSTS"""
        security = SecurityHeaders()

        assert "Strict-Transport-Security" in security.config
        assert "max-age" in security.config["Strict-Transport-Security"]

    def test_default_config_has_csp(self):
        """Test default config includes CSP"""
        security = SecurityHeaders()

        assert "Content-Security-Policy" in security.config
        assert "default-src" in security.config["Content-Security-Policy"]

    def test_default_config_has_referrer_policy(self):
        """Test default config includes referrer policy"""
        security = SecurityHeaders()

        assert "Referrer-Policy" in security.config

    def test_default_config_has_permissions_policy(self):
        """Test default config includes permissions policy"""
        security = SecurityHeaders()

        assert "Permissions-Policy" in security.config

    def test_default_config_has_cross_origin_policies(self):
        """Test default config includes cross-origin policies"""
        security = SecurityHeaders()

        assert "Cross-Origin-Opener-Policy" in security.config
        assert "Cross-Origin-Embedder-Policy" in security.config
        assert "Cross-Origin-Resource-Policy" in security.config

    def test_set_header(self):
        """Test setting a header"""
        security = SecurityHeaders()

        security.set_header("Test-Header", "TestValue")

        assert security.config["Test-Header"] == "TestValue"

    def test_remove_header(self):
        """Test removing a header"""
        security = SecurityHeaders()
        security.config["Test-Header"] = "TestValue"

        security.remove_header("Test-Header")

        assert "Test-Header" not in security.config

    def test_remove_nonexistent_header(self):
        """Test removing non-existent header"""
        security = SecurityHeaders()

        # Should not raise error
        security.remove_header("NonExistent")

    def test_get_csp_strict(self):
        """Test getting strict CSP"""
        security = SecurityHeaders()

        csp = security.get_csp_strict()

        assert "default-src 'none'" in csp
        assert "script-src 'self'" in csp
        assert "unsafe-inline" not in csp

    def test_get_csp_relaxed(self):
        """Test getting relaxed CSP"""
        security = SecurityHeaders()

        csp = security.get_csp_relaxed()

        assert "default-src 'self'" in csp
        assert "unsafe-inline" in csp
        assert "unsafe-eval" in csp

    def test_enable_cors_default(self):
        """Test enabling CORS with defaults"""
        security = SecurityHeaders()

        security.enable_cors()

        assert "Access-Control-Allow-Origin" in security.config
        assert security.config["Access-Control-Allow-Origin"] == "*"

    def test_enable_cors_custom_origins(self):
        """Test enabling CORS with custom origins"""
        security = SecurityHeaders()

        security.enable_cors(origins="https://example.com")

        assert security.config["Access-Control-Allow-Origin"] == "https://example.com"

    def test_enable_cors_custom_methods(self):
        """Test enabling CORS with custom methods"""
        security = SecurityHeaders()

        security.enable_cors(methods="GET, POST")

        assert security.config["Access-Control-Allow-Methods"] == "GET, POST"

    def test_enable_cors_custom_headers(self):
        """Test enabling CORS with custom headers"""
        security = SecurityHeaders()

        security.enable_cors(headers="Content-Type, X-Custom")

        assert security.config["Access-Control-Allow-Headers"] == "Content-Type, X-Custom"

    def test_enable_cors_custom_max_age(self):
        """Test enabling CORS with custom max age"""
        security = SecurityHeaders()

        security.enable_cors(max_age=7200)

        assert security.config["Access-Control-Max-Age"] == "7200"


# ============================================================================
# Flask Integration Tests
# ============================================================================


class TestFlaskIntegration:
    """Test Flask integration"""

    @pytest.fixture
    def mock_app(self):
        """Create mock Flask app"""
        app = Mock()
        app.after_request = Mock()
        return app

    def test_init_app(self, mock_app):
        """Test initializing with Flask app"""
        security = SecurityHeaders()
        security.init_app(mock_app)

        # Should register after_request handler
        assert mock_app.after_request.called

    def test_init_with_app_in_constructor(self):
        """Test initialization with app in constructor"""
        mock_app = Mock()
        mock_app.after_request = Mock()

        security = SecurityHeaders(app=mock_app)

        assert mock_app.after_request.called


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestHelperFunctions:
    """Test helper functions"""

    @pytest.fixture
    def mock_app(self):
        """Create mock Flask app"""
        app = Mock()
        app.after_request = Mock()
        return app

    def test_create_security_headers(self, mock_app):
        """Test create_security_headers function"""
        security = create_security_headers(mock_app)

        assert security is not None
        assert isinstance(security, SecurityHeaders)

    def test_create_security_headers_disable_hsts(self, mock_app):
        """Test disabling HSTS"""
        security = create_security_headers(mock_app, enable_hsts=False)

        assert "Strict-Transport-Security" not in security.config

    def test_create_security_headers_strict_csp(self, mock_app):
        """Test strict CSP mode"""
        security = create_security_headers(mock_app, csp_mode="strict")

        assert "default-src 'none'" in security.config["Content-Security-Policy"]

    def test_create_security_headers_relaxed_csp(self, mock_app):
        """Test relaxed CSP mode"""
        security = create_security_headers(mock_app, csp_mode="relaxed")

        assert "unsafe-inline" in security.config["Content-Security-Policy"]

    def test_create_security_headers_enable_cors(self, mock_app):
        """Test enabling CORS"""
        security = create_security_headers(mock_app, enable_cors=True)

        assert "Access-Control-Allow-Origin" in security.config

    def test_create_security_headers_custom_cors_origins(self, mock_app):
        """Test custom CORS origins"""
        security = create_security_headers(mock_app, enable_cors=True, cors_origins="https://example.com")

        assert security.config["Access-Control-Allow-Origin"] == "https://example.com"

    def test_init_security_headers(self, mock_app):
        """Test init_security_headers function"""
        security = init_security_headers(mock_app)

        assert security is not None

    def test_secure_flask_app_development(self, mock_app):
        """Test secure_flask_app for development"""
        security = secure_flask_app(mock_app, production=False)

        # HSTS should be disabled for development
        assert "Strict-Transport-Security" not in security.config

    def test_secure_flask_app_production(self, mock_app):
        """Test secure_flask_app for production"""
        security = secure_flask_app(mock_app, production=True)

        # HSTS should be enabled for production
        assert "Strict-Transport-Security" in security.config
        # CSP should be strict
        assert "default-src 'none'" in security.config["Content-Security-Policy"]

    def test_secure_flask_app_with_cors(self, mock_app):
        """Test secure_flask_app with CORS"""
        security = secure_flask_app(mock_app, enable_cors=True)

        assert "Access-Control-Allow-Origin" in security.config


# ============================================================================
# Decorator Tests
# ============================================================================


class TestSkipSecurityHeadersDecorator:
    """Test skip_security_headers decorator"""

    def test_decorator_basic(self):
        """Test basic decorator functionality"""
        from flask import Response

        @skip_security_headers()
        def test_view():
            return Response("test")

        response = test_view()

        # Should have skip flag
        assert hasattr(response, "_skip_security_headers")
        assert response._skip_security_headers is True

    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function name"""

        @skip_security_headers()
        def test_view():
            return "test"

        assert test_view.__name__ == "test_view"

    def test_decorator_with_non_response(self):
        """Test decorator with non-Response return"""

        @skip_security_headers()
        def test_view():
            return "test"

        result = test_view()

        # Should return original value
        assert result == "test"


# ============================================================================
# CSP Policy Tests
# ============================================================================


class TestCSPPolicies:
    """Test Content Security Policy configurations"""

    def test_default_csp_allows_self(self):
        """Test default CSP allows 'self'"""
        security = SecurityHeaders()

        csp = security.config["Content-Security-Policy"]

        assert "default-src 'self'" in csp

    def test_default_csp_allows_inline_scripts(self):
        """Test default CSP allows inline scripts"""
        security = SecurityHeaders()

        csp = security.config["Content-Security-Policy"]

        assert "unsafe-inline" in csp

    def test_strict_csp_denies_default(self):
        """Test strict CSP denies default sources"""
        security = SecurityHeaders()

        csp = security.get_csp_strict()

        assert "default-src 'none'" in csp

    def test_strict_csp_no_inline_scripts(self):
        """Test strict CSP doesn't allow inline scripts"""
        security = SecurityHeaders()

        csp = security.get_csp_strict()

        assert "unsafe-inline" not in csp
        assert "unsafe-eval" not in csp

    def test_relaxed_csp_allows_https(self):
        """Test relaxed CSP allows https sources"""
        security = SecurityHeaders()

        csp = security.get_csp_relaxed()

        assert "https:" in csp

    def test_csp_includes_frame_ancestors(self):
        """Test CSP includes frame-ancestors"""
        security = SecurityHeaders()

        csp = security.config["Content-Security-Policy"]

        assert "frame-ancestors" in csp


# ============================================================================
# Security Header Values Tests
# ============================================================================


class TestSecurityHeaderValues:
    """Test specific security header values"""

    def test_xss_protection_value(self):
        """Test XSS protection value"""
        security = SecurityHeaders()

        assert security.config["X-XSS-Protection"] == "1; mode=block"

    def test_content_type_options_value(self):
        """Test content type options value"""
        security = SecurityHeaders()

        assert security.config["X-Content-Type-Options"] == "nosniff"

    def test_frame_options_value(self):
        """Test frame options value"""
        security = SecurityHeaders()

        assert security.config["X-Frame-Options"] == "SAMEORIGIN"

    def test_hsts_includes_max_age(self):
        """Test HSTS includes max-age"""
        security = SecurityHeaders()

        hsts = security.config["Strict-Transport-Security"]

        assert "max-age=" in hsts
        assert "includeSubDomains" in hsts

    def test_referrer_policy_value(self):
        """Test referrer policy value"""
        security = SecurityHeaders()

        assert "strict-origin" in security.config["Referrer-Policy"]

    def test_permissions_policy_disables_features(self):
        """Test permissions policy disables sensitive features"""
        security = SecurityHeaders()

        policy = security.config["Permissions-Policy"]

        assert "geolocation=()" in policy
        assert "microphone=()" in policy
        assert "camera=()" in policy

    def test_cross_origin_opener_policy(self):
        """Test cross-origin opener policy"""
        security = SecurityHeaders()

        assert security.config["Cross-Origin-Opener-Policy"] == "same-origin"

    def test_cross_origin_embedder_policy(self):
        """Test cross-origin embedder policy"""
        security = SecurityHeaders()

        assert security.config["Cross-Origin-Embedder-Policy"] == "require-corp"
