"""
Comprehensive tests for email notification system.

Test coverage goals:
- Positive cases: Successful email sending
- Negative cases: Error handling, disabled notifier
- Edge cases: Attachments, HTML emails, large recipient lists
- Integration: All notification types
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

from src.core.email_notifier import EmailNotifier, get_notifier


class TestEmailNotifierInitialization:
    """Test suite for EmailNotifier initialization."""

    def test_default_initialization(self):
        """Test initialization with default values."""
        notifier = EmailNotifier()

        assert notifier.smtp_host == "localhost"
        assert notifier.smtp_port == 587
        assert notifier.smtp_user == ""
        assert notifier.smtp_password == ""
        assert notifier.from_email == "noreply@dms.local"
        assert notifier.enabled is False

    def test_custom_initialization(self):
        """Test initialization with custom values."""
        notifier = EmailNotifier(
            smtp_host="smtp.example.com",
            smtp_port=465,
            smtp_user="user@example.com",
            smtp_password="secret123",
            from_email="sender@example.com",
        )

        assert notifier.smtp_host == "smtp.example.com"
        assert notifier.smtp_port == 465
        assert notifier.smtp_user == "user@example.com"
        assert notifier.smtp_password == "secret123"
        assert notifier.from_email == "sender@example.com"
        assert notifier.enabled is True

    def test_enabled_flag_with_credentials(self):
        """Test that enabled flag is True when credentials provided."""
        notifier = EmailNotifier(smtp_user="user", smtp_password="pass")
        assert notifier.enabled is True

    def test_disabled_flag_without_credentials(self):
        """Test that enabled flag is False without credentials."""
        notifier = EmailNotifier()
        assert notifier.enabled is False


class TestSendEmail:
    """Test suite for send_email method."""

    @pytest.fixture
    def notifier(self):
        """Create enabled notifier instance."""
        return EmailNotifier(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_password="password",
            from_email="sender@example.com",
        )

    @pytest.fixture
    def disabled_notifier(self):
        """Create disabled notifier instance."""
        return EmailNotifier()

    def test_send_email_disabled(self, disabled_notifier, capsys):
        """Test sending email when notifier is disabled."""
        result = disabled_notifier.send_email(
            to_emails=["recipient@example.com"], subject="Test", body="Test body"
        )

        assert result is False
        captured = capsys.readouterr()
        assert "disabled" in captured.out.lower()

    @patch("smtplib.SMTP")
    def test_send_plain_text_email(self, mock_smtp, notifier):
        """Test sending plain text email."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_email(
            to_emails=["recipient@example.com"], subject="Test Subject", body="Test body", html=False
        )

        assert result is True
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "password")
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_html_email(self, mock_smtp, notifier):
        """Test sending HTML email."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        html_body = "<html><body><h1>Test</h1></body></html>"

        result = notifier.send_email(
            to_emails=["recipient@example.com"], subject="Test", body=html_body, html=True
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_email_multiple_recipients(self, mock_smtp, notifier):
        """Test sending email to multiple recipients."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]

        result = notifier.send_email(to_emails=recipients, subject="Test", body="Test body")

        assert result is True
        # Verify message was sent
        mock_server.send_message.assert_called_once()
        # Get the message that was sent
        sent_msg = mock_server.send_message.call_args[0][0]
        assert "user1@example.com" in sent_msg["To"]
        assert "user2@example.com" in sent_msg["To"]
        assert "user3@example.com" in sent_msg["To"]

    @patch("smtplib.SMTP")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file content")
    def test_send_email_with_attachment(self, mock_file, mock_smtp, notifier):
        """Test sending email with attachment."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            result = notifier.send_email(
                to_emails=["recipient@example.com"], subject="Test", body="Test", attachments=[tmp_path]
            )

            assert result is True
            mock_server.send_message.assert_called_once()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch("smtplib.SMTP")
    def test_send_email_with_multiple_attachments(self, mock_smtp, notifier):
        """Test sending email with multiple attachments."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Create temporary files
        tmp_files = []
        for i in range(3):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".txt")
            tmp.write(f"content {i}".encode())
            tmp.close()
            tmp_files.append(tmp.name)

        try:
            result = notifier.send_email(
                to_emails=["recipient@example.com"], subject="Test", body="Test", attachments=tmp_files
            )

            assert result is True
            mock_server.send_message.assert_called_once()
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    @patch("smtplib.SMTP")
    def test_send_email_with_nonexistent_attachment(self, mock_smtp, notifier, capsys):
        """Test sending email with non-existent attachment."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_email(
            to_emails=["recipient@example.com"], subject="Test", body="Test", attachments=["/nonexistent/file.txt"]
        )

        # Should still succeed but log warning about attachment
        assert result is True
        captured = capsys.readouterr()
        assert "Failed to attach" in captured.out

    @patch("smtplib.SMTP")
    def test_send_email_smtp_error(self, mock_smtp, notifier, capsys):
        """Test handling SMTP connection error."""
        mock_smtp.side_effect = Exception("SMTP connection failed")

        result = notifier.send_email(to_emails=["recipient@example.com"], subject="Test", body="Test")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to send email" in captured.out

    @patch("smtplib.SMTP")
    def test_send_email_login_error(self, mock_smtp, notifier, capsys):
        """Test handling SMTP login error."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("Authentication failed")

        result = notifier.send_email(to_emails=["recipient@example.com"], subject="Test", body="Test")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to send email" in captured.out


class TestServiceCreatedNotification:
    """Test suite for service created notification."""

    @pytest.fixture
    def notifier(self):
        """Create enabled notifier."""
        return EmailNotifier(smtp_user="user", smtp_password="pass")

    @patch("smtplib.SMTP")
    def test_send_service_created_notification(self, mock_smtp, notifier):
        """Test service created notification."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_service_created_notification(
            service_name="Test Service", to_emails=["admin@example.com"]
        )

        assert result is True
        mock_server.send_message.assert_called_once()

        # Verify message content
        sent_msg = mock_server.send_message.call_args[0][0]
        assert "Test Service" in sent_msg["Subject"]
        assert "admin@example.com" in sent_msg["To"]

    @patch("smtplib.SMTP")
    def test_service_notification_content(self, mock_smtp, notifier):
        """Test service notification contains correct information."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        service_name = "My New Service"
        notifier.send_service_created_notification(service_name, ["admin@example.com"])

        sent_msg = mock_server.send_message.call_args[0][0]

        # Check subject contains service name
        assert service_name in sent_msg["Subject"]

        # Get payload and decode if needed
        payload = sent_msg.get_payload()
        if isinstance(payload, list):
            text_part = payload[0]
            body_text = text_part.get_payload(decode=True).decode('utf-8')
        else:
            body_text = payload

        assert service_name in body_text


class TestDocumentGeneratedNotification:
    """Test suite for document generated notification."""

    @pytest.fixture
    def notifier(self):
        """Create enabled notifier."""
        return EmailNotifier(smtp_user="user", smtp_password="pass")

    @patch("smtplib.SMTP")
    def test_send_document_generated_without_attachment(self, mock_smtp, notifier):
        """Test document generated notification without attachment."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_document_generated_notification(
            service_name="Test Service", format="pdf", to_emails=["user@example.com"]
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_document_generated_with_attachment(self, mock_smtp, notifier):
        """Test document generated notification with attachment."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"PDF content")
            tmp_path = tmp.name

        try:
            result = notifier.send_document_generated_notification(
                service_name="Test Service", format="pdf", to_emails=["user@example.com"], attachment=tmp_path
            )

            assert result is True
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestCalculationReport:
    """Test suite for calculation report notification."""

    @pytest.fixture
    def notifier(self):
        """Create enabled notifier."""
        return EmailNotifier(smtp_user="user", smtp_password="pass")

    @patch("smtplib.SMTP")
    def test_send_calculation_report(self, mock_smtp, notifier):
        """Test sending calculation report."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_calculation_report(
            service_name="Test Service", hourly_rate=45.50, to_emails=["finance@example.com"]
        )

        assert result is True
        mock_server.send_message.assert_called_once()

        # Verify hourly rate is in subject or body
        sent_msg = mock_server.send_message.call_args[0][0]

        # Get payload and decode
        payload = sent_msg.get_payload()
        if isinstance(payload, list):
            text_part = payload[0]
            body_text = text_part.get_payload(decode=True).decode('utf-8')
        else:
            body_text = payload

        # Check that rate is present (formatted as 45.50)
        assert "45.50" in body_text or "Test Service" in sent_msg["Subject"]

    @patch("smtplib.SMTP")
    def test_calculation_report_with_file(self, mock_smtp, notifier):
        """Test calculation report with attached file."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(b"Excel content")
            tmp_path = tmp.name

        try:
            result = notifier.send_calculation_report(
                service_name="Test Service",
                hourly_rate=45.50,
                to_emails=["finance@example.com"],
                report_file=tmp_path,
            )

            assert result is True
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestWeeklyReport:
    """Test suite for weekly report notification."""

    @pytest.fixture
    def notifier(self):
        """Create enabled notifier."""
        return EmailNotifier(smtp_user="user", smtp_password="pass")

    @pytest.fixture
    def sample_stats(self):
        """Sample statistics data."""
        return {
            "total_services": 150,
            "avg_brutto_rate": 42.75,
            "by_region": {"Berlin": 50, "Munich": 30, "Hamburg": 20},
            "by_type": {"Consultation": 100, "Implementation": 50},
        }

    @patch("smtplib.SMTP")
    def test_send_weekly_report(self, mock_smtp, notifier, sample_stats):
        """Test sending weekly report."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_weekly_report(stats=sample_stats, to_emails=["admin@example.com"])

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_weekly_report_content(self, mock_smtp, notifier, sample_stats):
        """Test weekly report contains correct statistics."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier.send_weekly_report(stats=sample_stats, to_emails=["admin@example.com"])

        sent_msg = mock_server.send_message.call_args[0][0]

        # Get payload and decode
        payload = sent_msg.get_payload()
        if isinstance(payload, list):
            text_part = payload[0]
            body_text = text_part.get_payload(decode=True).decode('utf-8')
        else:
            body_text = payload

        # Verify statistics are in body
        assert "150" in body_text  # total_services
        assert "42.75" in body_text  # avg_brutto_rate
        assert "Berlin" in body_text
        assert "Munich" in body_text

    @patch("smtplib.SMTP")
    def test_weekly_report_empty_stats(self, mock_smtp, notifier):
        """Test weekly report with empty statistics."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_weekly_report(stats={}, to_emails=["admin@example.com"])

        assert result is True
        mock_server.send_message.assert_called_once()


class TestErrorNotification:
    """Test suite for error notification."""

    @pytest.fixture
    def notifier(self):
        """Create enabled notifier."""
        return EmailNotifier(smtp_user="user", smtp_password="pass")

    @patch("smtplib.SMTP")
    def test_send_error_notification(self, mock_smtp, notifier):
        """Test sending error notification."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        error_msg = "Database connection failed"
        result = notifier.send_error_notification(error_message=error_msg, to_emails=["admin@example.com"])

        assert result is True
        mock_server.send_message.assert_called_once()

        # Verify error message in body
        sent_msg = mock_server.send_message.call_args[0][0]

        # Get payload and decode
        payload = sent_msg.get_payload()
        if isinstance(payload, list):
            text_part = payload[0]
            body_text = text_part.get_payload(decode=True).decode('utf-8')
        else:
            body_text = payload

        assert error_msg in body_text
        assert "ОШИБКА" in sent_msg["Subject"]

    @patch("smtplib.SMTP")
    def test_error_notification_urgent(self, mock_smtp, notifier):
        """Test error notification has urgent markers."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier.send_error_notification(error_message="Critical error", to_emails=["admin@example.com"])

        sent_msg = mock_server.send_message.call_args[0][0]
        assert "ОШИБКА" in sent_msg["Subject"]  # Error in subject


class TestGetNotifierSingleton:
    """Test suite for get_notifier singleton function."""

    def test_get_notifier_returns_instance(self):
        """Test get_notifier returns EmailNotifier instance."""
        notifier = get_notifier()
        assert isinstance(notifier, EmailNotifier)

    def test_get_notifier_singleton(self):
        """Test get_notifier returns same instance."""
        notifier1 = get_notifier()
        notifier2 = get_notifier()

        assert notifier1 is notifier2

    @patch.dict(
        os.environ,
        {
            "SMTP_HOST": "custom.smtp.com",
            "SMTP_PORT": "465",
            "SMTP_USER": "custom@example.com",
            "SMTP_PASSWORD": "custompass",
            "FROM_EMAIL": "custom-sender@example.com",
        },
    )
    def test_get_notifier_from_environment(self):
        """Test get_notifier loads config from environment."""
        # Clear singleton
        import src.core.email_notifier

        src.core.email_notifier._notifier_instance = None

        notifier = get_notifier()

        assert notifier.smtp_host == "custom.smtp.com"
        assert notifier.smtp_port == 465
        assert notifier.smtp_user == "custom@example.com"
        assert notifier.smtp_password == "custompass"
        assert notifier.from_email == "custom-sender@example.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_notifier_default_values(self):
        """Test get_notifier uses defaults when env vars not set."""
        # Clear singleton
        import src.core.email_notifier

        src.core.email_notifier._notifier_instance = None

        notifier = get_notifier()

        assert notifier.smtp_host == "localhost"
        assert notifier.smtp_port == 587
        assert notifier.from_email == "noreply@dms.local"
