"""
Tests for HTTPS configuration module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.core.https_config import HTTPSConfig


class TestHTTPSConfig:
    """Tests for HTTPSConfig."""

    def test_initialization(self):
        """Test HTTPS config initialization."""
        config = HTTPSConfig()
        assert config.cert_path is not None
        assert config.key_path is not None

    def test_initialization_with_paths(self):
        """Test initialization with custom paths."""
        config = HTTPSConfig(cert_path="custom/cert.pem", key_path="custom/key.pem")
        assert config.cert_path == "custom/cert.pem"
        assert config.key_path == "custom/key.pem"

    def test_get_security_headers(self):
        """Test security headers generation."""
        config = HTTPSConfig()
        headers = config.get_security_headers()

        # Check required headers present
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers

    def test_hsts_header_value(self):
        """Test HSTS header has correct value."""
        config = HTTPSConfig()
        headers = config.get_security_headers()

        hsts = headers["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_csp_header_present(self):
        """Test CSP header is present and not empty."""
        config = HTTPSConfig()
        headers = config.get_security_headers()

        csp = headers["Content-Security-Policy"]
        assert len(csp) > 0
        assert "default-src 'self'" in csp

    def test_x_frame_options_deny(self):
        """Test X-Frame-Options is set to DENY."""
        config = HTTPSConfig()
        headers = config.get_security_headers()

        assert headers["X-Frame-Options"] == "DENY"

    def test_x_content_type_options(self):
        """Test X-Content-Type-Options is nosniff."""
        config = HTTPSConfig()
        headers = config.get_security_headers()

        assert headers["X-Content-Type-Options"] == "nosniff"


class TestSelfSignedCertificate:
    """Tests for self-signed certificate generation."""

    @pytest.fixture
    def temp_cert_dir(self):
        """Create temporary directory for certificates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_self_signed_cert(self, temp_cert_dir):
        """Test self-signed certificate generation."""
        try:
            import cryptography
        except ImportError:
            pytest.skip("cryptography package not installed")

        cert_path = os.path.join(temp_cert_dir, "cert.pem")
        key_path = os.path.join(temp_cert_dir, "key.pem")

        config = HTTPSConfig(cert_path=cert_path, key_path=key_path)

        # Generate certificate
        generated_cert, generated_key = config.generate_self_signed_cert(days_valid=365, common_name="localhost")

        # Check files created
        assert os.path.exists(generated_cert)
        assert os.path.exists(generated_key)

        # Check files are not empty
        assert os.path.getsize(generated_cert) > 0
        assert os.path.getsize(generated_key) > 0

    def test_generate_cert_custom_validity(self, temp_cert_dir):
        """Test certificate generation with custom validity period."""
        try:
            import cryptography
        except ImportError:
            pytest.skip("cryptography package not installed")

        cert_path = os.path.join(temp_cert_dir, "cert.pem")
        key_path = os.path.join(temp_cert_dir, "key.pem")

        config = HTTPSConfig(cert_path=cert_path, key_path=key_path)

        # Generate certificate valid for 30 days
        cert, key = config.generate_self_signed_cert(days_valid=30, common_name="test.local")

        assert os.path.exists(cert)
        assert os.path.exists(key)

    def test_check_certificate_expiry(self, temp_cert_dir):
        """Test certificate expiry checking."""
        try:
            import cryptography
        except ImportError:
            pytest.skip("cryptography package not installed")

        cert_path = os.path.join(temp_cert_dir, "cert.pem")
        key_path = os.path.join(temp_cert_dir, "key.pem")

        config = HTTPSConfig(cert_path=cert_path, key_path=key_path)

        # Generate certificate
        config.generate_self_signed_cert(days_valid=365)

        # Check expiry
        days_left = config.check_certificate_expiry()

        assert days_left is not None
        assert days_left > 0
        assert days_left <= 365

    def test_check_expiry_no_cert(self):
        """Test expiry check when certificate doesn't exist."""
        config = HTTPSConfig(cert_path="nonexistent/cert.pem", key_path="nonexistent/key.pem")

        days_left = config.check_certificate_expiry()
        assert days_left is None


class TestSSLContext:
    """Tests for SSL context creation."""

    @pytest.fixture
    def temp_cert_dir(self):
        """Create temporary directory for certificates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_ssl_context_missing_cert(self):
        """Test SSL context creation fails with missing certificate."""
        config = HTTPSConfig(cert_path="nonexistent/cert.pem", key_path="nonexistent/key.pem")

        with pytest.raises(FileNotFoundError) as exc_info:
            config.create_ssl_context()

        assert "SSL certificate not found" in str(exc_info.value)

    def test_create_ssl_context_success(self, temp_cert_dir):
        """Test SSL context creation with valid certificate."""
        try:
            import ssl

            import cryptography
        except ImportError:
            pytest.skip("cryptography package not installed")

        cert_path = os.path.join(temp_cert_dir, "cert.pem")
        key_path = os.path.join(temp_cert_dir, "key.pem")

        config = HTTPSConfig(cert_path=cert_path, key_path=key_path)

        # Generate certificate first
        config.generate_self_signed_cert()

        # Create SSL context
        context = config.create_ssl_context()

        assert context is not None
        assert isinstance(context, ssl.SSLContext)

        # Verify TLS version settings
        assert context.minimum_version == ssl.TLSVersion.TLSv1_2


class TestFlaskIntegration:
    """Tests for Flask integration."""

    def test_configure_flask_https(self):
        """Test Flask HTTPS configuration."""
        try:
            from flask import Flask

            from src.core.https_config import configure_flask_https
        except ImportError:
            pytest.skip("Flask not installed")

        app = Flask(__name__)
        app.config["ENV"] = "production"
        config = HTTPSConfig()

        # Configure Flask
        configure_flask_https(app, config)

        # Check before_request handler registered
        assert len(app.before_request_funcs.get(None, [])) > 0

        # Check after_request handler registered
        assert len(app.after_request_funcs.get(None, [])) > 0


class TestEnvironmentVariables:
    """Tests for environment variable support."""

    def test_cert_path_from_env(self, monkeypatch):
        """Test certificate path from environment variable."""
        monkeypatch.setenv("SSL_CERT_PATH", "/custom/cert.pem")
        monkeypatch.setenv("SSL_KEY_PATH", "/custom/key.pem")

        config = HTTPSConfig()

        assert config.cert_path == "/custom/cert.pem"
        assert config.key_path == "/custom/key.pem"


class TestSecurityBestPractices:
    """Tests for security best practices."""

    def test_no_sslv2_sslv3(self, temp_cert_dir):
        """Test that SSLv2 and SSLv3 are disabled."""
        try:
            import ssl

            import cryptography
        except ImportError:
            pytest.skip("cryptography package not installed")

        cert_path = os.path.join(temp_cert_dir, "cert.pem")
        key_path = os.path.join(temp_cert_dir, "key.pem")

        config = HTTPSConfig(cert_path=cert_path, key_path=key_path)
        config.generate_self_signed_cert()

        context = config.create_ssl_context()

        # Check that old SSL/TLS versions are disabled
        assert context.options & ssl.OP_NO_SSLv2
        assert context.options & ssl.OP_NO_SSLv3
        assert context.options & ssl.OP_NO_TLSv1
        assert context.options & ssl.OP_NO_TLSv1_1

    def test_strong_ciphers_only(self, temp_cert_dir):
        """Test that only strong cipher suites are allowed."""
        try:
            import ssl

            import cryptography
        except ImportError:
            pytest.skip("cryptography package not installed")

        cert_path = os.path.join(temp_cert_dir, "cert.pem")
        key_path = os.path.join(temp_cert_dir, "key.pem")

        config = HTTPSConfig(cert_path=cert_path, key_path=key_path)
        config.generate_self_signed_cert()

        context = config.create_ssl_context()

        # Get cipher list
        ciphers = context.get_ciphers()

        # Check that we have some ciphers configured
        assert len(ciphers) > 0

        # Check for strong cipher suites (ECDHE, AES-GCM)
        cipher_names = [c["name"] for c in ciphers]
        has_strong_cipher = any("ECDHE" in name or "CHACHA20" in name for name in cipher_names)
        assert has_strong_cipher


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
