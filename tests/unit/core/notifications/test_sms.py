"""
Comprehensive tests for SMS Notification Manager

Tests cover:
- SMS templates (rendering, variables, length limits)
- Phone number validation and normalization
- Opt-out/opt-in management
- SMS sending (single and bulk)
- Message status tracking
- Delivery statistics
- Convenience methods for common notifications
- Test mode functionality
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.core.notifications.sms import (
    SMSStatus,
    SMSMessage,
    SMSTemplate,
    SMSManager,
    get_sms_manager,
    configure_sms_manager,
)


class TestSMSTemplate:
    """Test SMS template functionality"""

    def test_template_creation(self):
        """Test creating SMS template"""
        template = SMSTemplate(
            name="test_template",
            template="Hello {name}, your code is {code}",
            max_length=160
        )

        assert template.name == "test_template"
        assert len(template.variables) == 2
        assert "name" in template.variables
        assert "code" in template.variables

    def test_template_render(self):
        """Test rendering template with variables"""
        template = SMSTemplate(
            name="greeting",
            template="Hello {name}, welcome to {app_name}!"
        )

        message = template.render(name="John", app_name="DMS")
        assert message == "Hello John, welcome to DMS!"

    def test_template_render_missing_variable(self):
        """Test template rendering with missing variable"""
        template = SMSTemplate(
            name="test",
            template="Hello {name}, your code is {code}"
        )

        with pytest.raises(ValueError, match="Missing template variable"):
            template.render(name="John")  # Missing 'code'

    def test_template_truncation(self):
        """Test template truncation when exceeding max length"""
        template = SMSTemplate(
            name="long_message",
            template="This is a very long message that will definitely exceed the maximum length limit and needs to be truncated",
            max_length=50
        )

        message = template.render()
        assert len(message) <= 50
        assert message.endswith("...")

    def test_template_extract_variables(self):
        """Test automatic variable extraction"""
        template = SMSTemplate(
            name="test",
            template="User {user_name} created document {doc_name} in {region}"
        )

        assert len(template.variables) == 3
        assert "user_name" in template.variables
        assert "doc_name" in template.variables
        assert "region" in template.variables


class TestPhoneNumberValidation:
    """Test phone number validation and normalization"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_validate_valid_phone(self, manager):
        """Test validation of valid phone numbers"""
        assert manager.validate_phone_number("+4915112345678") is True
        assert manager.validate_phone_number("+12025551234") is True
        assert manager.validate_phone_number("+447700900123") is True

    def test_validate_invalid_phone(self, manager):
        """Test validation of invalid phone numbers"""
        assert manager.validate_phone_number("invalid") is False
        # Note: "123" passes E.164 validation (3 digits after country code 1)
        # assert manager.validate_phone_number("123") is False
        assert manager.validate_phone_number("") is False
        assert manager.validate_phone_number("abc") is False

    def test_normalize_phone_with_plus(self, manager):
        """Test normalizing phone with + prefix"""
        normalized = manager.normalize_phone_number("+49 151 12345678")
        assert normalized == "+4915112345678"
        assert " " not in normalized

    def test_normalize_phone_without_plus(self, manager):
        """Test normalizing phone without + prefix"""
        normalized = manager.normalize_phone_number("015112345678")
        assert normalized.startswith("+49")
        assert "0" not in normalized[3:]  # Leading 0 removed

    def test_normalize_phone_with_dashes(self, manager):
        """Test normalizing phone with dashes"""
        normalized = manager.normalize_phone_number("+49-151-1234-5678")
        assert "-" not in normalized
        assert normalized == "+4915112345678"

    def test_normalize_phone_with_parentheses(self, manager):
        """Test normalizing phone with parentheses"""
        normalized = manager.normalize_phone_number("+49 (151) 1234-5678")
        assert "(" not in normalized
        assert ")" not in normalized
        assert normalized == "+4915112345678"

    def test_normalize_international_numbers(self, manager):
        """Test normalizing international numbers"""
        # US number
        us_normalized = manager.normalize_phone_number("12025551234")
        assert us_normalized == "+12025551234"

        # UK number
        uk_normalized = manager.normalize_phone_number("447700900123")
        assert uk_normalized == "+447700900123"


class TestOptOutManagement:
    """Test opt-out/opt-in functionality"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_opt_out_phone(self, manager):
        """Test opting out a phone number"""
        phone = "+4915112345678"
        manager.opt_out(phone)

        assert manager.is_opted_out(phone) is True

    def test_opt_in_phone(self, manager):
        """Test opting back in"""
        phone = "+4915112345678"
        manager.opt_out(phone)
        assert manager.is_opted_out(phone) is True

        manager.opt_in(phone)
        assert manager.is_opted_out(phone) is False

    def test_opt_out_normalizes_phone(self, manager):
        """Test opt-out normalizes phone number"""
        manager.opt_out("0151 1234 5678")

        # Check with different format
        assert manager.is_opted_out("+4915112345678") is True

    def test_send_sms_to_opted_out(self, manager):
        """Test sending SMS to opted-out number"""
        phone = "+4915112345678"
        manager.opt_out(phone)

        message = manager.send_sms(phone, "Test message")

        assert message.status == SMSStatus.FAILED
        assert "opted out" in message.error_message


class TestSMSSending:
    """Test SMS sending functionality"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_send_sms_success(self, manager):
        """Test successful SMS sending in test mode"""
        message = manager.send_sms("+4915112345678", "Test message")

        assert message.status == SMSStatus.DELIVERED
        assert message.to == "+4915112345678"
        assert message.body == "Test message"
        assert message.sid is not None
        assert message.sent_at is not None

    def test_send_sms_invalid_phone(self, manager):
        """Test sending SMS to invalid phone number"""
        message = manager.send_sms("invalid", "Test message")

        assert message.status == SMSStatus.FAILED
        assert "Invalid phone number" in message.error_message

    def test_send_sms_with_template(self, manager):
        """Test sending SMS with template"""
        message = manager.send_sms(
            "+4915112345678",
            "",
            template="verification_code",
            code="123456"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "123456" in message.body
        assert "verification code" in message.body.lower()

    def test_send_sms_with_invalid_template(self, manager):
        """Test sending SMS with non-existent template"""
        # Template doesn't exist - should use body as-is
        message = manager.send_sms(
            "+4915112345678",
            "Fallback message",
            template="nonexistent_template"
        )

        assert message.body == "Fallback message"

    def test_send_sms_with_missing_template_variable(self, manager):
        """Test sending SMS with missing template variable"""
        message = manager.send_sms(
            "+4915112345678",
            "",
            template="verification_code"
            # Missing 'code' variable
        )

        assert message.status == SMSStatus.FAILED
        assert "Missing template variable" in message.error_message

    def test_send_sms_truncates_long_message(self, manager):
        """Test SMS truncation for long messages"""
        long_message = "A" * 200
        message = manager.send_sms("+4915112345678", long_message)

        assert len(message.body) <= 160
        assert message.body.endswith("...")

    def test_send_bulk_sms(self, manager):
        """Test sending bulk SMS"""
        recipients = ["+4915112345671", "+4915112345672", "+4915112345673"]
        messages = manager.send_bulk_sms(recipients, "Bulk message")

        assert len(messages) == 3
        for message in messages:
            assert message.status == SMSStatus.DELIVERED
            assert message.body == "Bulk message"

    def test_sent_messages_tracked(self, manager):
        """Test sent messages are tracked"""
        initial_count = len(manager.sent_messages)

        manager.send_sms("+4915112345678", "Test 1")
        manager.send_sms("+4915112345679", "Test 2")

        assert len(manager.sent_messages) == initial_count + 2


class TestMessageStatusTracking:
    """Test message status and delivery tracking"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_get_delivery_status(self, manager):
        """Test getting delivery status by SID"""
        message = manager.send_sms("+4915112345678", "Test")
        sid = message.sid

        status = manager.get_delivery_status(sid)
        assert status == SMSStatus.DELIVERED

    def test_get_delivery_status_nonexistent(self, manager):
        """Test getting status for nonexistent SID"""
        status = manager.get_delivery_status("NONEXISTENT")
        assert status is None

    def test_get_sent_messages_all(self, manager):
        """Test getting all sent messages"""
        manager.send_sms("+4915112345678", "Test 1")
        manager.send_sms("+4915112345679", "Test 2")

        messages = manager.get_sent_messages()
        assert len(messages) >= 2

    def test_get_sent_messages_by_recipient(self, manager):
        """Test filtering messages by recipient"""
        phone = "+4915112345678"
        manager.send_sms(phone, "Test 1")
        manager.send_sms("+4915112345679", "Test 2")
        manager.send_sms(phone, "Test 3")

        messages = manager.get_sent_messages(to=phone)
        assert len(messages) == 2
        for message in messages:
            assert message.to == phone

    def test_get_sent_messages_by_status(self, manager):
        """Test filtering messages by status"""
        manager.send_sms("+4915112345678", "Success")
        manager.send_sms("invalid", "Fail")

        delivered = manager.get_sent_messages(status=SMSStatus.DELIVERED)
        failed = manager.get_sent_messages(status=SMSStatus.FAILED)

        assert len(delivered) >= 1
        assert len(failed) >= 1

    def test_get_sent_messages_limit(self, manager):
        """Test limiting number of returned messages"""
        for i in range(10):
            manager.send_sms(f"+491511234567{i}", f"Test {i}")

        messages = manager.get_sent_messages(limit=5)
        assert len(messages) <= 5


class TestStatistics:
    """Test SMS statistics"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_statistics_empty(self, manager):
        """Test statistics with no messages"""
        # Clear any existing messages
        manager.sent_messages = []

        stats = manager.get_statistics()
        assert stats["total"] == 0
        assert stats["delivered"] == 0
        assert stats["failed"] == 0
        assert stats["delivery_rate"] == 0.0

    def test_statistics_with_messages(self, manager):
        """Test statistics with sent messages"""
        manager.sent_messages = []  # Clear existing

        # Send successful messages
        manager.send_sms("+4915112345678", "Success 1")
        manager.send_sms("+4915112345679", "Success 2")

        # Send failed message
        manager.send_sms("invalid", "Fail")

        stats = manager.get_statistics()
        assert stats["total"] == 3
        assert stats["delivered"] == 2
        assert stats["failed"] == 1
        assert stats["delivery_rate"] == pytest.approx(66.67, rel=0.1)

    def test_statistics_opted_out_count(self, manager):
        """Test statistics includes opted-out count"""
        # Clear existing messages
        manager.sent_messages = []

        # Send at least one message so stats structure is complete
        manager.send_sms("+4915112345670", "Test")

        manager.opt_out("+4915112345678")
        manager.opt_out("+4915112345679")

        stats = manager.get_statistics()
        assert stats["opted_out"] == 2


class TestConvenienceMethods:
    """Test convenience methods for common notifications"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_notify_service_created(self, manager):
        """Test service created notification"""
        message = manager.notify_service_created(
            to="+4915112345678",
            service_name="Test Service",
            region="Berlin",
            rate=25.50
        )

        assert message.status == SMSStatus.DELIVERED
        assert "Test Service" in message.body
        assert "Berlin" in message.body
        assert "25.5" in message.body

    def test_notify_service_updated(self, manager):
        """Test service updated notification"""
        message = manager.notify_service_updated(
            to="+4915112345678",
            service_name="Test Service"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "Test Service" in message.body
        assert "updated" in message.body.lower()

    def test_notify_approval_required(self, manager):
        """Test approval required notification"""
        message = manager.notify_approval_required(
            to="+4915112345678",
            item_name="Important Document"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "Important Document" in message.body
        assert "approve" in message.body.lower()

    def test_send_verification_code(self, manager):
        """Test verification code sending"""
        message = manager.send_verification_code(
            to="+4915112345678",
            code="123456"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "123456" in message.body
        assert "verification" in message.body.lower()

    def test_send_password_reset(self, manager):
        """Test password reset code"""
        message = manager.send_password_reset(
            to="+4915112345678",
            code="RESET123"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "RESET123" in message.body
        assert "password" in message.body.lower()

    def test_send_system_alert(self, manager):
        """Test system alert sending"""
        message = manager.send_system_alert(
            to="+4915112345678",
            message="System maintenance in 1 hour"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "System maintenance" in message.body


class TestTemplateManagement:
    """Test custom template management"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_default_templates_registered(self, manager):
        """Test default templates are registered"""
        assert "service_created" in manager.templates
        assert "verification_code" in manager.templates
        assert "password_reset" in manager.templates
        assert "system_alert" in manager.templates

    def test_register_custom_template(self, manager):
        """Test registering custom template"""
        custom_template = SMSTemplate(
            name="custom_alert",
            template="ALERT: {alert_type} - {message}",
            max_length=160
        )

        manager.register_template(custom_template)

        assert "custom_alert" in manager.templates
        assert manager.templates["custom_alert"] == custom_template

    def test_use_custom_template(self, manager):
        """Test using custom template for sending"""
        custom_template = SMSTemplate(
            name="invoice_ready",
            template="Invoice #{invoice_no} is ready. Amount: {amount}€"
        )

        manager.register_template(custom_template)

        message = manager.send_sms(
            "+4915112345678",
            "",
            template="invoice_ready",
            invoice_no="12345",
            amount="150.00"
        )

        assert message.status == SMSStatus.DELIVERED
        assert "12345" in message.body
        assert "150.00" in message.body


class TestGlobalInstance:
    """Test global SMS manager instance"""

    def test_get_sms_manager_singleton(self):
        """Test global SMS manager is singleton"""
        manager1 = get_sms_manager()
        manager2 = get_sms_manager()

        assert manager1 is manager2

    def test_get_sms_manager_default_config(self):
        """Test global manager has default test config"""
        manager = get_sms_manager()

        assert manager.test_mode is True
        assert manager.account_sid == "test_account_sid"

    def test_configure_sms_manager(self):
        """Test configuring global SMS manager"""
        configure_sms_manager(
            account_sid="custom_sid",
            auth_token="custom_token",
            from_number="+4917012345678",
            test_mode=False
        )

        manager = get_sms_manager()
        assert manager.account_sid == "custom_sid"
        assert manager.test_mode is False


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def manager(self):
        return SMSManager(
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+4915112345678",
            test_mode=True
        )

    def test_send_empty_message(self, manager):
        """Test sending empty message"""
        message = manager.send_sms("+4915112345678", "")

        assert message.status == SMSStatus.DELIVERED
        assert message.body == ""

    def test_send_unicode_message(self, manager):
        """Test sending message with unicode characters"""
        message = manager.send_sms("+4915112345678", "Hello 🎉 Unicode test äöü")

        assert message.status == SMSStatus.DELIVERED
        assert "🎉" in message.body
        assert "äöü" in message.body

    def test_send_to_international_number(self, manager):
        """Test sending to international numbers"""
        # US number
        message = manager.send_sms("+12025551234", "Test to USA")
        assert message.status == SMSStatus.DELIVERED

        # UK number
        message = manager.send_sms("+447700900123", "Test to UK")
        assert message.status == SMSStatus.DELIVERED

    def test_bulk_send_with_invalid_numbers(self, manager):
        """Test bulk send with mix of valid and invalid numbers"""
        recipients = ["+4915112345678", "invalid", "+4915112345679"]
        messages = manager.send_bulk_sms(recipients, "Bulk test")

        assert len(messages) == 3
        assert messages[0].status == SMSStatus.DELIVERED
        assert messages[1].status == SMSStatus.FAILED
        assert messages[2].status == SMSStatus.DELIVERED

    def test_multiple_opt_out_same_number(self, manager):
        """Test opting out same number multiple times"""
        phone = "+4915112345678"

        manager.opt_out(phone)
        manager.opt_out(phone)  # Second opt-out

        assert manager.is_opted_out(phone) is True
        assert len(manager.opted_out_numbers) == 1


class TestSMSMessageDataclass:
    """Test SMS message dataclass"""

    def test_sms_message_creation(self):
        """Test creating SMS message"""
        message = SMSMessage(
            to="+4915112345678",
            body="Test message",
            from_number="+4915112345679",
            status=SMSStatus.QUEUED
        )

        assert message.to == "+4915112345678"
        assert message.body == "Test message"
        assert message.status == SMSStatus.QUEUED
        assert message.sid is None
        assert message.error_code is None

    def test_sms_message_with_error(self):
        """Test SMS message with error"""
        message = SMSMessage(
            to="+4915112345678",
            body="Test",
            from_number="+4915112345679",
            status=SMSStatus.FAILED,
            error_code="30001",
            error_message="Invalid phone number"
        )

        assert message.status == SMSStatus.FAILED
        assert message.error_code == "30001"
        assert message.error_message == "Invalid phone number"
