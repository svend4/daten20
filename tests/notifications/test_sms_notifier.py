"""
Tests for SMS Notifier

Tests Twilio SMS notification functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.notifications.sms_notifier import (
    TwilioSMSNotifier,
    SMSMessage,
    SMSPriority,
    SMSResult,
    send_sms,
    send_verification_sms,
    send_alert_sms,
    send_2fa_sms
)


class TestSMSMessage:
    """Test SMSMessage dataclass."""

    def test_create_sms_message(self):
        """Test creating SMS message."""
        msg = SMSMessage(
            to='+12345678900',
            body='Test message'
        )

        assert msg.to == '+12345678900'
        assert msg.body == 'Test message'
        assert msg.priority == SMSPriority.NORMAL
        assert msg.from_ is None

    def test_sms_message_with_priority(self):
        """Test SMS message with priority."""
        msg = SMSMessage(
            to='+12345678900',
            body='Urgent message',
            priority=SMSPriority.URGENT
        )

        assert msg.priority == SMSPriority.URGENT


class TestSMSResult:
    """Test SMSResult dataclass."""

    def test_successful_result(self):
        """Test successful sending result."""
        result = SMSResult(
            success=True,
            message_id='SM123456'
        )

        assert result.success
        assert result.message_id == 'SM123456'
        assert result.error is None
        assert isinstance(result.sent_at, datetime)

    def test_failed_result(self):
        """Test failed sending result."""
        result = SMSResult(
            success=False,
            error='Invalid credentials'
        )

        assert not result.success
        assert result.error == 'Invalid credentials'
        assert result.message_id is None


class TestTwilioSMSNotifier:
    """Test Twilio SMS notifier."""

    @patch('src.notifications.sms_notifier.Client')
    def test_initialization_with_credentials(self, mock_client_class):
        """Test initialization with explicit credentials."""
        notifier = TwilioSMSNotifier(
            account_sid='AC123456',
            auth_token='token123',
            from_number='+1234567890'
        )

        assert notifier.enabled
        assert notifier.account_sid == 'AC123456'
        assert notifier.auth_token == 'token123'
        assert notifier.from_number == '+1234567890'
        mock_client_class.assert_called_once_with('AC123456', 'token123')

    def test_initialization_without_credentials(self):
        """Test initialization without credentials."""
        notifier = TwilioSMSNotifier()

        # Should be disabled if no credentials in environment
        if not notifier.enabled:
            assert notifier.client is None

    @patch('src.notifications.sms_notifier.Client')
    def test_send_sms_success(self, mock_client_class):
        """Test successful SMS sending."""
        # Setup mock
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123456789'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token123',
            from_number='+1234567890'
        )

        message = SMSMessage(
            to='+0987654321',
            body='Test message'
        )

        result = notifier.send_sms(message)

        assert result.success
        assert result.message_id == 'SM123456789'
        assert result.status == 'queued'
        assert isinstance(result.sent_at, datetime)
        mock_client.messages.create.assert_called_once()

    def test_send_sms_not_configured(self):
        """Test SMS when not configured."""
        notifier = TwilioSMSNotifier()  # No credentials

        if not notifier.enabled:
            message = SMSMessage(
                to='+1234567890',
                body='Test'
            )

            result = notifier.send_sms(message)

            assert not result.success
            assert 'not configured' in result.error

    @patch('src.notifications.sms_notifier.Client')
    def test_invalid_phone_format(self, mock_client_class):
        """Test invalid phone number format."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        message = SMSMessage(
            to='1234567890',  # Missing + sign
            body='Test'
        )

        result = notifier.send_sms(message)

        assert not result.success
        assert 'E.164 format' in result.error

    @patch('src.notifications.sms_notifier.Client')
    def test_send_sms_with_error(self, mock_client_class):
        """Test SMS sending with Twilio error."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception('Network error')
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        message = SMSMessage(
            to='+0987654321',
            body='Test'
        )

        result = notifier.send_sms(message)

        assert not result.success
        assert 'Network error' in result.error

    @patch('src.notifications.sms_notifier.Client')
    def test_send_bulk_sms(self, mock_client_class):
        """Test bulk SMS sending."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        phones = ['+1111111111', '+2222222222', '+3333333333']
        results = notifier.send_bulk_sms(phones, 'Bulk message')

        assert len(results) == 3
        assert all(r.success for r in results.values())
        assert mock_client.messages.create.call_count == 3

    @patch('src.notifications.sms_notifier.Client')
    def test_send_verification_code(self, mock_client_class):
        """Test verification code sending."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        result = notifier.send_verification_code('+0987654321', '123456')

        assert result.success
        # Verify message contains code
        call_args = mock_client.messages.create.call_args
        assert '123456' in call_args[1]['body']
        assert 'verification code' in call_args[1]['body'].lower()

    @patch('src.notifications.sms_notifier.Client')
    def test_send_alert(self, mock_client_class):
        """Test alert sending."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        result = notifier.send_alert(
            '+0987654321',
            'System failure',
            'CRITICAL'
        )

        assert result.success
        # Verify alert format
        call_args = mock_client.messages.create.call_args
        assert 'CRITICAL' in call_args[1]['body']
        assert 'System failure' in call_args[1]['body']

    @patch('src.notifications.sms_notifier.Client')
    def test_send_2fa_code(self, mock_client_class):
        """Test 2FA code sending."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        result = notifier.send_2fa_code('+0987654321', '654321', 'MyApp')

        assert result.success
        call_args = mock_client.messages.create.call_args
        assert '654321' in call_args[1]['body']
        assert 'MyApp' in call_args[1]['body']

    @patch('src.notifications.sms_notifier.Client')
    def test_get_message_status(self, mock_client_class):
        """Test getting message status."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'delivered'
        mock_message.to = '+1111111111'
        mock_message.from_ = '+2222222222'
        mock_message.body = 'Test'
        mock_message.date_sent = datetime.now()
        mock_message.date_created = datetime.now()
        mock_message.price = '-0.0075'
        mock_message.price_unit = 'USD'
        mock_message.error_code = None
        mock_message.error_message = None

        mock_client.messages.return_value.fetch.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        status = notifier.get_message_status('SM123')

        assert status is not None
        assert status['sid'] == 'SM123'
        assert status['status'] == 'delivered'
        assert status['price'] == '-0.0075'

    @patch('src.notifications.sms_notifier.Client')
    def test_get_account_balance(self, mock_client_class):
        """Test getting account balance."""
        mock_client = MagicMock()
        mock_balance = Mock()
        mock_balance.balance = '15.50'
        mock_balance.currency = 'USD'

        mock_client.api.accounts.return_value.balance.fetch.return_value = mock_balance
        mock_client_class.return_value = mock_client

        notifier = TwilioSMSNotifier(
            account_sid='AC123',
            auth_token='token',
            from_number='+1234567890'
        )

        balance = notifier.get_account_balance()

        assert balance is not None
        assert balance['balance'] == '15.50'
        assert balance['currency'] == 'USD'


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('src.notifications.sms_notifier.Client')
    def test_send_sms_function(self, mock_client_class):
        """Test send_sms convenience function."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        # Mock environment variables
        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'AC123',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_FROM_NUMBER': '+1234567890'
        }):
            result = send_sms('+0987654321', 'Test message')

            assert result.success
            assert result.message_id == 'SM123'

    @patch('src.notifications.sms_notifier.Client')
    def test_send_verification_sms_function(self, mock_client_class):
        """Test send_verification_sms convenience function."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'AC123',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_FROM_NUMBER': '+1234567890'
        }):
            result = send_verification_sms('+0987654321', '123456')

            assert result.success

    @patch('src.notifications.sms_notifier.Client')
    def test_send_alert_sms_function(self, mock_client_class):
        """Test send_alert_sms convenience function."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'AC123',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_FROM_NUMBER': '+1234567890'
        }):
            result = send_alert_sms('+0987654321', 'Alert message', 'WARNING')

            assert result.success

    @patch('src.notifications.sms_notifier.Client')
    def test_send_2fa_sms_function(self, mock_client_class):
        """Test send_2fa_sms convenience function."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'AC123',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_FROM_NUMBER': '+1234567890'
        }):
            result = send_2fa_sms('+0987654321', '654321')

            assert result.success


# Integration tests (require actual Twilio credentials)
@pytest.mark.integration
@pytest.mark.skipif(
    not all([
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN'),
        os.getenv('TWILIO_FROM_NUMBER'),
        os.getenv('TEST_PHONE_NUMBER')
    ]),
    reason="Twilio credentials or test phone not configured"
)
class TestTwilioIntegration:
    """Integration tests with real Twilio API."""

    def test_real_sms_send(self):
        """Test real SMS sending (requires credentials)."""
        import os
        notifier = TwilioSMSNotifier()

        result = notifier.send_sms(SMSMessage(
            to=os.getenv('TEST_PHONE_NUMBER'),
            body='Integration test message'
        ))

        assert result.success
        assert result.message_id is not None

    def test_real_verification_code(self):
        """Test real verification code sending."""
        import os
        notifier = TwilioSMSNotifier()

        result = notifier.send_verification_code(
            os.getenv('TEST_PHONE_NUMBER'),
            '123456'
        )

        assert result.success

    def test_real_balance_check(self):
        """Test real balance check."""
        notifier = TwilioSMSNotifier()
        balance = notifier.get_account_balance()

        assert balance is not None
        assert 'balance' in balance
        assert 'currency' in balance
