"""
SMS Notifications via Twilio

Sends SMS notifications for important events, verification codes, and alerts.

Configuration:
    Set environment variables:
    - TWILIO_ACCOUNT_SID: Your Twilio Account SID
    - TWILIO_AUTH_TOKEN: Your Twilio Auth Token
    - TWILIO_FROM_NUMBER: Your Twilio phone number (+1234567890)

Usage:
    >>> from src.notifications import send_sms, SMSPriority
    >>> result = send_sms('+12345678900', 'Hello from DMS!', SMSPriority.HIGH)
    >>> if result.success:
    ...     print(f"Sent: {result.message_id}")
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os
import logging

logger = logging.getLogger(__name__)


class SMSPriority(str, Enum):
    """SMS priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class SMSMessage:
    """SMS message structure"""
    to: str  # Phone number in E.164 format (+country_code + number)
    body: str
    from_: Optional[str] = None
    priority: SMSPriority = SMSPriority.NORMAL
    callback_url: Optional[str] = None
    max_price: Optional[float] = None  # Maximum price willing to pay


@dataclass
class SMSResult:
    """SMS sending result"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    cost: Optional[float] = None
    sent_at: Optional[datetime] = None
    status: Optional[str] = None

    def __post_init__(self):
        if self.sent_at is None and self.success:
            self.sent_at = datetime.now()


class TwilioSMSNotifier:
    """
    Twilio SMS notification service.

    Handles sending SMS messages via Twilio API.
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        """
        Initialize Twilio SMS notifier.

        Args:
            account_sid: Twilio Account SID (from env if not provided)
            auth_token: Twilio Auth Token (from env if not provided)
            from_number: Sender phone number (from env if not provided)
        """
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_FROM_NUMBER')

        # Check if Twilio is configured
        self.enabled = bool(self.account_sid and self.auth_token and self.from_number)

        if self.enabled:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS client initialized successfully")
            except ImportError:
                logger.warning("Twilio library not installed. Run: pip install twilio")
                self.enabled = False
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
                self.client = None
        else:
            logger.warning("Twilio not configured. SMS notifications disabled.")
            self.client = None

    def send_sms(self, message: SMSMessage) -> SMSResult:
        """
        Send SMS message.

        Args:
            message: SMS message to send

        Returns:
            Result of sending operation

        Example:
            >>> notifier = TwilioSMSNotifier()
            >>> msg = SMSMessage(to='+12345678900', body='Test message')
            >>> result = notifier.send_sms(msg)
            >>> print(f"Success: {result.success}")
        """
        if not self.enabled:
            logger.warning("SMS not configured, message not sent")
            return SMSResult(
                success=False,
                error="SMS service not configured. Check TWILIO_* environment variables."
            )

        try:
            # Validate phone number format
            if not message.to.startswith('+'):
                logger.error(f"Invalid phone format: {message.to}")
                return SMSResult(
                    success=False,
                    error=f"Phone number must be in E.164 format (+country_code + number). Got: {message.to}"
                )

            # Prepare message parameters
            params = {
                'to': message.to,
                'from_': message.from_ or self.from_number,
                'body': message.body
            }

            if message.callback_url:
                params['status_callback'] = message.callback_url

            if message.max_price:
                params['max_price'] = message.max_price

            # Send via Twilio
            twilio_message = self.client.messages.create(**params)

            logger.info(f"SMS sent successfully: {twilio_message.sid} to {message.to}")

            return SMSResult(
                success=True,
                message_id=twilio_message.sid,
                status=twilio_message.status,
                sent_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Failed to send SMS to {message.to}: {e}")
            return SMSResult(
                success=False,
                error=str(e)
            )

    def send_bulk_sms(
        self,
        phone_numbers: List[str],
        body: str,
        priority: SMSPriority = SMSPriority.NORMAL
    ) -> Dict[str, SMSResult]:
        """
        Send SMS to multiple recipients.

        Args:
            phone_numbers: List of phone numbers (E.164 format)
            body: Message body (same for all recipients)
            priority: Message priority

        Returns:
            Dict mapping phone number to sending result

        Example:
            >>> notifier = TwilioSMSNotifier()
            >>> results = notifier.send_bulk_sms(
            ...     ['+12345678900', '+10987654321'],
            ...     'Bulk message'
            ... )
            >>> success_count = sum(1 for r in results.values() if r.success)
            >>> print(f"{success_count} messages sent")
        """
        results = {}

        for phone in phone_numbers:
            message = SMSMessage(
                to=phone,
                body=body,
                priority=priority
            )
            result = self.send_sms(message)
            results[phone] = result

        # Log summary
        total = len(phone_numbers)
        success = sum(1 for r in results.values() if r.success)
        logger.info(f"Bulk SMS: {success}/{total} sent successfully")

        return results

    def send_verification_code(
        self,
        phone: str,
        code: str,
        expiry_minutes: int = 10
    ) -> SMSResult:
        """
        Send verification code via SMS.

        Args:
            phone: Phone number (E.164 format)
            code: Verification code (typically 6 digits)
            expiry_minutes: Code validity period in minutes

        Returns:
            Sending result

        Example:
            >>> notifier = TwilioSMSNotifier()
            >>> result = notifier.send_verification_code('+12345678900', '123456')
        """
        body = (
            f"Your verification code is: {code}\n"
            f"Valid for {expiry_minutes} minutes.\n"
            f"Do not share this code with anyone."
        )

        message = SMSMessage(
            to=phone,
            body=body,
            priority=SMSPriority.HIGH
        )

        return self.send_sms(message)

    def send_alert(
        self,
        phone: str,
        alert_message: str,
        alert_type: str = "ALERT"
    ) -> SMSResult:
        """
        Send alert notification.

        Args:
            phone: Phone number (E.164 format)
            alert_message: Alert message
            alert_type: Type of alert (ALERT, WARNING, CRITICAL, etc.)

        Returns:
            Sending result

        Example:
            >>> notifier = TwilioSMSNotifier()
            >>> result = notifier.send_alert(
            ...     '+12345678900',
            ...     'System backup failed',
            ...     'CRITICAL'
            ... )
        """
        body = f"⚠️ {alert_type}: {alert_message}"

        message = SMSMessage(
            to=phone,
            body=body,
            priority=SMSPriority.URGENT
        )

        return self.send_sms(message)

    def send_2fa_code(
        self,
        phone: str,
        code: str,
        app_name: str = "DMS"
    ) -> SMSResult:
        """
        Send two-factor authentication code.

        Args:
            phone: Phone number
            code: 2FA code
            app_name: Application name

        Returns:
            Sending result
        """
        body = (
            f"{app_name} Security Code: {code}\n"
            f"If you didn't request this, please contact support immediately."
        )

        message = SMSMessage(
            to=phone,
            body=body,
            priority=SMSPriority.URGENT
        )

        return self.send_sms(message)

    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Check message delivery status.

        Args:
            message_id: Twilio message SID

        Returns:
            Message status information or None if not found

        Example:
            >>> notifier = TwilioSMSNotifier()
            >>> status = notifier.get_message_status('SM123456')
            >>> if status:
            ...     print(f"Status: {status['status']}")
        """
        if not self.enabled:
            return None

        try:
            message = self.client.messages(message_id).fetch()

            return {
                'sid': message.sid,
                'status': message.status,  # queued, sending, sent, failed, delivered, undelivered
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'date_sent': message.date_sent,
                'date_created': message.date_created,
                'price': message.price,
                'price_unit': message.price_unit,
                'error_code': message.error_code,
                'error_message': message.error_message
            }

        except Exception as e:
            logger.error(f"Failed to fetch message status for {message_id}: {e}")
            return None

    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """
        Get Twilio account balance.

        Returns:
            Account balance information

        Example:
            >>> notifier = TwilioSMSNotifier()
            >>> balance = notifier.get_account_balance()
            >>> if balance:
            ...     print(f"Balance: {balance['balance']} {balance['currency']}")
        """
        if not self.enabled:
            return None

        try:
            balance = self.client.api.accounts(self.account_sid).balance.fetch()

            return {
                'balance': balance.balance,
                'currency': balance.currency
            }

        except Exception as e:
            logger.error(f"Failed to fetch account balance: {e}")
            return None


# ============================================================
# Convenience Functions
# ============================================================

_default_notifier: Optional[TwilioSMSNotifier] = None


def get_sms_notifier() -> TwilioSMSNotifier:
    """
    Get default SMS notifier instance (singleton).

    Returns:
        Shared TwilioSMSNotifier instance
    """
    global _default_notifier
    if _default_notifier is None:
        _default_notifier = TwilioSMSNotifier()
    return _default_notifier


def send_sms(
    to: str,
    body: str,
    priority: SMSPriority = SMSPriority.NORMAL
) -> SMSResult:
    """
    Quick send SMS using default notifier.

    Args:
        to: Phone number (E.164 format: +12345678900)
        body: Message body (max 160 characters for single SMS)
        priority: Priority level

    Returns:
        Sending result

    Example:
        >>> from src.notifications import send_sms, SMSPriority
        >>> result = send_sms('+12345678900', 'Hello World!', SMSPriority.HIGH)
        >>> if result.success:
        ...     print(f"✅ Sent: {result.message_id}")
        ... else:
        ...     print(f"❌ Failed: {result.error}")
    """
    notifier = get_sms_notifier()
    message = SMSMessage(to=to, body=body, priority=priority)
    return notifier.send_sms(message)


def send_verification_sms(phone: str, code: str, expiry_minutes: int = 10) -> SMSResult:
    """
    Quick send verification code.

    Args:
        phone: Phone number (E.164 format)
        code: Verification code
        expiry_minutes: Code expiry time

    Returns:
        Sending result

    Example:
        >>> result = send_verification_sms('+12345678900', '123456')
    """
    notifier = get_sms_notifier()
    return notifier.send_verification_code(phone, code, expiry_minutes)


def send_alert_sms(phone: str, alert: str, alert_type: str = "ALERT") -> SMSResult:
    """
    Quick send alert notification.

    Args:
        phone: Phone number (E.164 format)
        alert: Alert message
        alert_type: Alert type

    Returns:
        Sending result

    Example:
        >>> result = send_alert_sms('+12345678900', 'Server down', 'CRITICAL')
    """
    notifier = get_sms_notifier()
    return notifier.send_alert(phone, alert, alert_type)


def send_2fa_sms(phone: str, code: str, app_name: str = "DMS") -> SMSResult:
    """
    Quick send 2FA code.

    Args:
        phone: Phone number
        code: 2FA code
        app_name: Application name

    Returns:
        Sending result
    """
    notifier = get_sms_notifier()
    return notifier.send_2fa_code(phone, code, app_name)


# ============================================================
# Example Usage & Testing
# ============================================================

if __name__ == "__main__":
    import sys

    # Test SMS sending (requires Twilio credentials in environment)
    notifier = TwilioSMSNotifier()

    if not notifier.enabled:
        print("⚠️ SMS not configured. Set environment variables:")
        print("   export TWILIO_ACCOUNT_SID='your_account_sid'")
        print("   export TWILIO_AUTH_TOKEN='your_auth_token'")
        print("   export TWILIO_FROM_NUMBER='+1234567890'")
        sys.exit(1)

    # Check balance
    balance = notifier.get_account_balance()
    if balance:
        print(f"💰 Account balance: {balance['balance']} {balance['currency']}")

    # Send test message (replace with actual number)
    test_number = os.getenv('TEST_PHONE_NUMBER', '+12345678900')

    print(f"\n📱 Sending test SMS to {test_number}...")

    result = send_sms(
        test_number,
        'Test message from DMS SMS Notifier',
        SMSPriority.NORMAL
    )

    if result.success:
        print(f"✅ SMS sent successfully!")
        print(f"   Message ID: {result.message_id}")
        print(f"   Status: {result.status}")
        print(f"   Sent at: {result.sent_at}")

        # Check status
        if result.message_id:
            import time
            time.sleep(2)  # Wait for status update
            status = notifier.get_message_status(result.message_id)
            if status:
                print(f"\n📊 Message status:")
                print(f"   Delivery status: {status['status']}")
                print(f"   Price: {status['price']} {status['price_unit']}")
    else:
        print(f"❌ Failed to send SMS!")
        print(f"   Error: {result.error}")
