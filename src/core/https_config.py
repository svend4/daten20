"""
HTTPS Configuration Module

Provides HTTPS/TLS configuration for production deployments.
Includes SSL context setup, certificate management, and security headers.
"""

import logging
import os
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger("dms.https_config")


class HTTPSConfig:
    """
    HTTPS/TLS configuration manager.

    Handles SSL certificate setup, security headers, and HTTPS enforcement.
    """

    def __init__(self, cert_path: Optional[str] = None, key_path: Optional[str] = None):
        """
        Initialize HTTPS configuration.

        Args:
            cert_path: Path to SSL certificate file
            key_path: Path to SSL private key file
        """
        self.cert_path = cert_path or os.getenv("SSL_CERT_PATH", "certs/cert.pem")
        self.key_path = key_path or os.getenv("SSL_KEY_PATH", "certs/key.pem")

    def create_ssl_context(self, protocol: int = ssl.PROTOCOL_TLS_SERVER) -> ssl.SSLContext:
        """
        Create SSL context for HTTPS server.

        Args:
            protocol: SSL protocol version

        Returns:
            Configured SSL context

        Raises:
            FileNotFoundError: If certificate files not found
            ssl.SSLError: If certificate is invalid
        """
        # Verify certificate files exist
        if not os.path.exists(self.cert_path):
            raise FileNotFoundError(f"SSL certificate not found: {self.cert_path}")
        if not os.path.exists(self.key_path):
            raise FileNotFoundError(f"SSL private key not found: {self.key_path}")

        # Create SSL context
        context = ssl.SSLContext(protocol)

        # Security settings
        context.minimum_version = ssl.TLSVersion.TLSv1_2  # TLS 1.2 minimum
        context.maximum_version = ssl.TLSVersion.TLSv1_3  # TLS 1.3 preferred

        # Cipher suite (strong ciphers only)
        context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")

        # Load certificate and key
        try:
            context.load_cert_chain(self.cert_path, self.key_path)
            logger.info(f"SSL certificate loaded: {self.cert_path}")
        except ssl.SSLError as e:
            logger.error(f"Failed to load SSL certificate: {e}")
            raise

        # Verify mode
        context.verify_mode = ssl.CERT_NONE  # Client certificates not required

        # Options
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_SINGLE_DH_USE
        context.options |= ssl.OP_SINGLE_ECDH_USE

        return context

    def get_security_headers(self) -> Dict[str, str]:
        """
        Get HTTP security headers.

        Returns:
            Dictionary of security headers
        """
        return {
            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            # Content security
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),
            # XSS protection
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Permissions policy
            "Permissions-Policy": (
                "geolocation=(), " "microphone=(), " "camera=(), " "payment=(), " "usb=(), " "magnetometer=()"
            ),
        }

    def generate_self_signed_cert(self, days_valid: int = 365, common_name: str = "localhost") -> Tuple[str, str]:
        """
        Generate self-signed certificate for development.

        Args:
            days_valid: Certificate validity in days
            common_name: Common name for certificate

        Returns:
            Tuple of (cert_path, key_path)

        Note:
            Requires cryptography package
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.x509.oid import NameOID
        except ImportError:
            raise ImportError(
                "cryptography package required for certificate generation. " "Install with: pip install cryptography"
            )

        # Generate private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Generate certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "NRW"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Cologne"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DMS Dev"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=days_valid))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName(common_name),
                        x509.DNSName("localhost"),
                        x509.DNSName("127.0.0.1"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # Create certs directory
        cert_dir = Path(self.cert_path).parent
        cert_dir.mkdir(parents=True, exist_ok=True)

        # Write certificate
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write private key
        with open(self.key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        logger.info(f"Self-signed certificate generated: {self.cert_path}")
        return self.cert_path, self.key_path

    def check_certificate_expiry(self) -> Optional[int]:
        """
        Check certificate expiration.

        Returns:
            Days until expiration, or None if not found

        Note:
            Requires cryptography package
        """
        if not os.path.exists(self.cert_path):
            return None

        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            logger.warning("cryptography package not available for certificate check")
            return None

        try:
            with open(self.cert_path, "rb") as f:
                cert_data = f.read()

            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            expiry = cert.not_valid_after
            now = datetime.utcnow()

            if expiry < now:
                logger.warning("SSL certificate has expired!")
                return 0

            days_left = (expiry - now).days
            if days_left < 30:
                logger.warning(f"SSL certificate expires in {days_left} days")
            else:
                logger.info(f"SSL certificate valid for {days_left} days")

            return days_left

        except Exception as e:
            logger.error(f"Failed to check certificate expiry: {e}")
            return None


def configure_flask_https(app, https_config: HTTPSConfig):
    """
    Configure Flask app with HTTPS settings.

    Args:
        app: Flask application
        https_config: HTTPSConfig instance
    """

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        """Add security headers to response."""
        headers = https_config.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        return response

    # Force HTTPS in production
    @app.before_request
    def force_https():
        """Redirect HTTP to HTTPS in production."""
        from flask import redirect, request

        if app.config.get("ENV") == "production":
            if request.url.startswith("http://"):
                url = request.url.replace("http://", "https://", 1)
                return redirect(url, code=301)

    logger.info("Flask HTTPS configuration applied")


def run_https_server(
    app, host: str = "0.0.0.0", port: int = 5443, cert_path: Optional[str] = None, key_path: Optional[str] = None
):
    """
    Run Flask app with HTTPS.

    Args:
        app: Flask application
        host: Host address
        port: Port number (default: 5443 for HTTPS)
        cert_path: SSL certificate path
        key_path: SSL private key path
    """
    https_config = HTTPSConfig(cert_path, key_path)

    # Configure Flask
    configure_flask_https(app, https_config)

    # Create SSL context
    try:
        ssl_context = https_config.create_ssl_context()
    except FileNotFoundError:
        logger.warning("SSL certificates not found, generating self-signed certificate")
        https_config.generate_self_signed_cert()
        ssl_context = https_config.create_ssl_context()

    # Check certificate expiry
    https_config.check_certificate_expiry()

    # Run server
    logger.info(f"Starting HTTPS server on {host}:{port}")
    app.run(host=host, port=port, ssl_context=ssl_context, debug=False)  # Never debug in HTTPS mode


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create HTTPS config
    config = HTTPSConfig()

    # Generate self-signed cert for development
    cert, key = config.generate_self_signed_cert()
    print(f"Certificate: {cert}")
    print(f"Private key: {key}")

    # Create SSL context
    context = config.create_ssl_context()
    print(f"SSL context created: {context}")

    # Check expiry
    days = config.check_certificate_expiry()
    print(f"Certificate expires in {days} days")

    # Print security headers
    headers = config.get_security_headers()
    print("\nSecurity headers:")
    for name, value in headers.items():
        print(f"  {name}: {value}")
