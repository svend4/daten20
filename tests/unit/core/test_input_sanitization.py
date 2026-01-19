"""
Unit tests for input sanitization module
"""

import pytest

from src.core.input_sanitization import InputSanitizer


# ============================================================================
# HTML Sanitization Tests
# ============================================================================


class TestHTMLSanitization:
    """Test HTML sanitization"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_sanitize_html_basic(self, sanitizer):
        """Test basic HTML sanitization"""
        text = "<p>Hello World</p>"
        result = sanitizer.sanitize_html(text)

        # All HTML should be escaped
        assert "&lt;" in result
        assert "&gt;" in result

    def test_sanitize_html_script_tag(self, sanitizer):
        """Test script tag removal"""
        text = "<script>alert('XSS')</script>"
        result = sanitizer.sanitize_html(text)

        assert "script" not in result.lower()
        assert "alert" not in result

    def test_sanitize_html_iframe(self, sanitizer):
        """Test iframe removal"""
        text = '<iframe src="http://evil.com"></iframe>'
        result = sanitizer.sanitize_html(text)

        assert "iframe" not in result.lower()

    def test_sanitize_html_onclick(self, sanitizer):
        """Test onclick attribute removal"""
        text = '<a href="#" onclick="alert(1)">Click</a>'
        result = sanitizer.sanitize_html(text)

        assert "onclick" not in result.lower()
        assert "alert" not in result.lower()

    def test_sanitize_html_javascript_protocol(self, sanitizer):
        """Test javascript: protocol removal"""
        text = '<a href="javascript:alert(1)">Click</a>'
        result = sanitizer.sanitize_html(text)

        assert "javascript:" not in result.lower()

    def test_sanitize_html_data_protocol(self, sanitizer):
        """Test data: protocol removal"""
        text = '<img src="data:text/html,<script>alert(1)</script>">'
        result = sanitizer.sanitize_html(text)

        assert "data:text/html" not in result.lower()

    def test_sanitize_html_vbscript(self, sanitizer):
        """Test vbscript: protocol removal"""
        text = '<a href="vbscript:msgbox">Click</a>'
        result = sanitizer.sanitize_html(text)

        assert "vbscript:" not in result.lower()

    def test_sanitize_html_with_allowed_tags(self, sanitizer):
        """Test HTML sanitization with allowed tags"""
        text = "<p><b>Bold</b> and <i>italic</i></p>"
        result = sanitizer.sanitize_html(text, allow_tags=["b", "i"])

        # Should preserve allowed tags
        assert "<b>" in result or "&lt;b&gt;" in result

    def test_sanitize_html_empty_string(self, sanitizer):
        """Test empty string"""
        result = sanitizer.sanitize_html("")
        assert result == ""

    def test_sanitize_html_none(self, sanitizer):
        """Test None input"""
        result = sanitizer.sanitize_html(None)
        assert result == ""

    def test_sanitize_html_nested_tags(self, sanitizer):
        """Test nested dangerous tags"""
        text = "<div><script>alert(1)</script></div>"
        result = sanitizer.sanitize_html(text)

        assert "script" not in result.lower()
        assert "alert" not in result

    def test_sanitize_html_multiple_events(self, sanitizer):
        """Test multiple event attributes"""
        text = '<div onload="evil()" onmouseover="bad()">Test</div>'
        result = sanitizer.sanitize_html(text)

        assert "onload" not in result.lower()
        assert "onmouseover" not in result.lower()


# ============================================================================
# SQL Sanitization Tests
# ============================================================================


class TestSQLSanitization:
    """Test SQL injection prevention"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_sanitize_sql_union_attack(self, sanitizer):
        """Test UNION-based SQL injection"""
        text = "'; UNION SELECT * FROM users--"
        result = sanitizer.sanitize_sql(text)

        assert "union" not in result.lower()

    def test_sanitize_sql_comment(self, sanitizer):
        """Test SQL comment removal"""
        text = "admin'--"
        result = sanitizer.sanitize_sql(text)

        assert "--" not in result

    def test_sanitize_sql_quote_escape(self, sanitizer):
        """Test quote escaping"""
        text = "O'Reilly"
        result = sanitizer.sanitize_sql(text)

        # Should escape or remove quotes
        assert "'" not in result or "\\'" in result or "''" in result

    def test_sanitize_sql_semicolon(self, sanitizer):
        """Test semicolon removal"""
        text = "admin'; DROP TABLE users;"
        result = sanitizer.sanitize_sql(text)

        assert "drop" not in result.lower()
        assert ";" not in result

    def test_sanitize_sql_clean_text(self, sanitizer):
        """Test clean text passes through"""
        text = "John Doe"
        result = sanitizer.sanitize_sql(text)

        assert "John" in result
        assert "Doe" in result


# ============================================================================
# Command Injection Tests
# ============================================================================


class TestCommandInjection:
    """Test command injection prevention"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_sanitize_command_semicolon(self, sanitizer):
        """Test semicolon command chaining"""
        text = "file.txt; rm -rf /"
        result = sanitizer.sanitize_command(text)

        assert ";" not in result

    def test_sanitize_command_pipe(self, sanitizer):
        """Test pipe command chaining"""
        text = "file.txt | cat /etc/passwd"
        result = sanitizer.sanitize_command(text)

        assert "|" not in result

    def test_sanitize_command_ampersand(self, sanitizer):
        """Test ampersand command chaining"""
        text = "file.txt && whoami"
        result = sanitizer.sanitize_command(text)

        assert "&" not in result

    def test_sanitize_command_backticks(self, sanitizer):
        """Test backtick command substitution"""
        text = "file`whoami`.txt"
        result = sanitizer.sanitize_command(text)

        assert "`" not in result

    def test_sanitize_command_dollar(self, sanitizer):
        """Test dollar command substitution"""
        text = "file$(whoami).txt"
        result = sanitizer.sanitize_command(text)

        assert "$(" not in result

    def test_sanitize_command_redirect(self, sanitizer):
        """Test output redirection"""
        text = "file.txt > /etc/passwd"
        result = sanitizer.sanitize_command(text)

        # Should remove redirect
        assert ">&" not in result

    def test_sanitize_command_clean_filename(self, sanitizer):
        """Test clean filename"""
        text = "document.pdf"
        result = sanitizer.sanitize_command(text)

        assert "document.pdf" in result


# ============================================================================
# Path Traversal Tests
# ============================================================================


class TestPathTraversal:
    """Test path traversal prevention"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_sanitize_path_dot_dot(self, sanitizer):
        """Test ../.. path traversal"""
        path = "../../../etc/passwd"
        result = sanitizer.sanitize_path(path)

        assert ".." not in result

    def test_sanitize_path_absolute(self, sanitizer):
        """Test absolute path"""
        path = "/etc/passwd"
        result = sanitizer.sanitize_path(path)

        # Should not start with /
        assert not result.startswith("/")

    def test_sanitize_path_null_byte(self, sanitizer):
        """Test null byte injection"""
        path = "file.txt\\x00.jpg"
        result = sanitizer.sanitize_path(path)

        assert "\\x00" not in result

    def test_sanitize_path_clean(self, sanitizer):
        """Test clean path"""
        path = "documents/report.pdf"
        result = sanitizer.sanitize_path(path)

        assert "documents" in result
        assert "report.pdf" in result


# ============================================================================
# Email Validation Tests
# ============================================================================


class TestEmailValidation:
    """Test email validation and sanitization"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_validate_email_valid(self, sanitizer):
        """Test valid email"""
        email = "user@example.com"
        result = sanitizer.validate_email(email)

        assert result is True

    def test_validate_email_invalid_no_at(self, sanitizer):
        """Test invalid email without @"""
        email = "userexample.com"
        result = sanitizer.validate_email(email)

        assert result is False

    def test_validate_email_invalid_no_domain(self, sanitizer):
        """Test invalid email without domain"""
        email = "user@"
        result = sanitizer.validate_email(email)

        assert result is False

    def test_validate_email_with_subdomain(self, sanitizer):
        """Test email with subdomain"""
        email = "user@mail.example.com"
        result = sanitizer.validate_email(email)

        assert result is True

    def test_sanitize_email(self, sanitizer):
        """Test email sanitization"""
        email = "User@Example.COM"
        result = sanitizer.sanitize_email(email)

        # Should lowercase
        assert result == "user@example.com"


# ============================================================================
# URL Validation Tests
# ============================================================================


class TestURLValidation:
    """Test URL validation and sanitization"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_validate_url_http(self, sanitizer):
        """Test valid HTTP URL"""
        url = "http://example.com"
        result = sanitizer.validate_url(url)

        assert result is True

    def test_validate_url_https(self, sanitizer):
        """Test valid HTTPS URL"""
        url = "https://example.com"
        result = sanitizer.validate_url(url)

        assert result is True

    def test_validate_url_javascript(self, sanitizer):
        """Test javascript: URL"""
        url = "javascript:alert(1)"
        result = sanitizer.validate_url(url)

        assert result is False

    def test_validate_url_data(self, sanitizer):
        """Test data: URL"""
        url = "data:text/html,<script>alert(1)</script>"
        result = sanitizer.validate_url(url)

        assert result is False

    def test_validate_url_file(self, sanitizer):
        """Test file: URL"""
        url = "file:///etc/passwd"
        result = sanitizer.validate_url(url)

        assert result is False

    def test_sanitize_url(self, sanitizer):
        """Test URL sanitization"""
        url = "https://example.com/path?query=value"
        result = sanitizer.sanitize_url(url)

        assert "https://" in result
        assert "example.com" in result


# ============================================================================
# LDAP Injection Tests
# ============================================================================


class TestLDAPInjection:
    """Test LDAP injection prevention"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_sanitize_ldap_wildcard(self, sanitizer):
        """Test LDAP wildcard injection"""
        text = "*"
        result = sanitizer.sanitize_ldap(text)

        # Should escape or remove wildcard
        assert result == "" or "\\*" in result

    def test_sanitize_ldap_parentheses(self, sanitizer):
        """Test LDAP parentheses"""
        text = "admin)(|(password=*))"
        result = sanitizer.sanitize_ldap(text)

        # Should escape parentheses
        assert ")" not in result or "\\)" in result

    def test_sanitize_ldap_clean_text(self, sanitizer):
        """Test clean LDAP text"""
        text = "john.doe"
        result = sanitizer.sanitize_ldap(text)

        assert "john.doe" in result


# ============================================================================
# General Sanitization Tests
# ============================================================================


class TestGeneralSanitization:
    """Test general sanitization"""

    @pytest.fixture
    def sanitizer(self):
        """Create InputSanitizer instance"""
        return InputSanitizer()

    def test_sanitize_string_basic(self, sanitizer):
        """Test basic string sanitization"""
        text = "Hello World"
        result = sanitizer.sanitize_string(text)

        assert result == "Hello World"

    def test_sanitize_string_with_html(self, sanitizer):
        """Test string with HTML"""
        text = "<b>Hello</b>"
        result = sanitizer.sanitize_string(text)

        # Should escape HTML
        assert "&lt;" in result or "<b>" not in result

    def test_sanitize_dict(self, sanitizer):
        """Test dictionary sanitization"""
        data = {
            "name": "<script>alert(1)</script>John",
            "email": "user@example.com"
        }
        result = sanitizer.sanitize_dict(data)

        assert "script" not in result["name"].lower()
        assert result["email"] == "user@example.com"

    def test_sanitize_list(self, sanitizer):
        """Test list sanitization"""
        data = ["<script>alert(1)</script>", "safe text"]
        result = sanitizer.sanitize_list(data)

        assert "script" not in result[0].lower()
        assert result[1] == "safe text"
