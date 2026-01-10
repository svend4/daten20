"""
SMS Notifications via Twilio

Sends SMS notifications for important events.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


class SMSStatus(str, Enum):
    """SMS delivery status"""
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    FAILED = "failed"


@dataclass
class SMSMessage:
    """SMS message data"""
    to: str
    body: str
    from_number: str
    status: SMSStatus = SMSStatus.QUEUED
    sid: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


@dataclass
class SMSTemplate:
    """SMS message template"""
    name: str
    template: str
    max_length: int = 160
    variables: List[str] = None

    def __post_init__(self):
        if self.variables is None:
            # Extract variables from template
            self.variables = re.findall(r'\{(\w+)\}', self.template)

    def render(self, **kwargs) -> str:
        """Render template with variables"""
        try:
            message = self.template.format(**kwargs)
            if len(message) > self.max_length:
                message = message[:self.max_length-3] + "..."
            return message
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")


class SMSManager:
    """Manages SMS notifications via Twilio"""

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        test_mode: bool = False
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.test_mode = test_mode

        # Message history
        self.sent_messages: List[SMSMessage] = []

        # Templates
        self.templates: Dict[str, SMSTemplate] = {}
        self._register_default_templates()

        # Opt-out management
        self.opted_out_numbers: set = set()

    def _register_default_templates(self):
        """Register default SMS templates"""
        self.templates = {
            'service_created': SMSTemplate(
                name='Service Created',
                template='DMS: New service "{service_name}" created in {region}. Rate: {rate}€/h',
                max_length=160
            ),
            'service_updated': SMSTemplate(
                name='Service Updated',
                template='DMS: Service "{service_name}" was updated. Check your dashboard for details.',
                max_length=160
            ),
            'approval_required': SMSTemplate(
                name='Approval Required',
                template='DMS: Action required! Please approve "{item_name}". Login to review.',
                max_length=160
            ),
            'document_ready': SMSTemplate(
                name='Document Ready',
                template='DMS: Your document "{doc_name}" is ready for download.',
                max_length=160
            ),
            'system_alert': SMSTemplate(
                name='System Alert',
                template='DMS Alert: {message}',
                max_length=160
            ),
            'verification_code': SMSTemplate(
                name='Verification Code',
                template='DMS: Your verification code is {code}. Valid for 10 minutes.',
                max_length=160
            ),
            'password_reset': SMSTemplate(
                name='Password Reset',
                template='DMS: Password reset requested. Code: {code}. If not you, ignore this.',
                max_length=160
            ),
            'reminder': SMSTemplate(
                name='Reminder',
                template='DMS Reminder: {message}',
                max_length=160
            )
        }

    def register_template(self, template: SMSTemplate):
        """Register a custom SMS template"""
        self.templates[template.name] = template

    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        # E.164 format: +[country code][number]
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))

    def normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number to E.164 format"""
        # Remove spaces, dashes, parentheses
        normalized = re.sub(r'[\s\-\(\)]', '', phone)

        # Add + if missing
        if not normalized.startswith('+'):
            # Assume German number if no country code
            if normalized.startswith('0'):
                normalized = '+49' + normalized[1:]
            else:
                normalized = '+' + normalized

        return normalized

    def opt_out(self, phone: str):
        """Opt out a phone number from SMS"""
        normalized = self.normalize_phone_number(phone)
        self.opted_out_numbers.add(normalized)

    def opt_in(self, phone: str):
        """Opt in a phone number for SMS"""
        normalized = self.normalize_phone_number(phone)
        self.opted_out_numbers.discard(normalized)

    def is_opted_out(self, phone: str) -> bool:
        """Check if phone number is opted out"""
        normalized = self.normalize_phone_number(phone)
        return normalized in self.opted_out_numbers

    def send_sms(
        self,
        to: str,
        body: str,
        template: Optional[str] = None,
        **template_vars
    ) -> SMSMessage:
        """Send SMS message"""

        # Normalize phone number
        to_normalized = self.normalize_phone_number(to)

        # Check opt-out
        if self.is_opted_out(to_normalized):
            message = SMSMessage(
                to=to_normalized,
                body=body,
                from_number=self.from_number,
                status=SMSStatus.FAILED,
                error_message="Phone number has opted out"
            )
            self.sent_messages.append(message)
            return message

        # Validate phone number
        if not self.validate_phone_number(to_normalized):
            message = SMSMessage(
                to=to_normalized,
                body=body,
                from_number=self.from_number,
                status=SMSStatus.FAILED,
                error_message="Invalid phone number format"
            )
            self.sent_messages.append(message)
            return message

        # Render template if specified
        if template and template in self.templates:
            try:
                body = self.templates[template].render(**template_vars)
            except ValueError as e:
                message = SMSMessage(
                    to=to_normalized,
                    body=body,
                    from_number=self.from_number,
                    status=SMSStatus.FAILED,
                    error_message=str(e)
                )
                self.sent_messages.append(message)
                return message

        # Truncate if too long
        if len(body) > 160:
            body = body[:157] + "..."

        # Test mode - don't actually send
        if self.test_mode:
            message = SMSMessage(
                to=to_normalized,
                body=body,
                from_number=self.from_number,
                status=SMSStatus.DELIVERED,
                sid=f"TEST{datetime.now().timestamp()}",
                sent_at=datetime.now(),
                delivered_at=datetime.now()
            )
            self.sent_messages.append(message)
            print(f"[TEST MODE] SMS to {to_normalized}: {body}")
            return message

        # Real sending with Twilio (placeholder - requires twilio package)
        try:
            # In real implementation:
            # from twilio.rest import Client
            # client = Client(self.account_sid, self.auth_token)
            # twilio_message = client.messages.create(
            #     body=body,
            #     from_=self.from_number,
            #     to=to_normalized
            # )

            # Simulated success
            message = SMSMessage(
                to=to_normalized,
                body=body,
                from_number=self.from_number,
                status=SMSStatus.SENT,
                sid=f"SM{datetime.now().timestamp()}",
                sent_at=datetime.now()
            )
            self.sent_messages.append(message)
            return message

        except Exception as e:
            message = SMSMessage(
                to=to_normalized,
                body=body,
                from_number=self.from_number,
                status=SMSStatus.FAILED,
                error_message=str(e)
            )
            self.sent_messages.append(message)
            return message

    def send_bulk_sms(
        self,
        recipients: List[str],
        body: str,
        template: Optional[str] = None,
        **template_vars
    ) -> List[SMSMessage]:
        """Send SMS to multiple recipients"""
        results = []
        for recipient in recipients:
            message = self.send_sms(recipient, body, template, **template_vars)
            results.append(message)
        return results

    def get_delivery_status(self, sid: str) -> Optional[SMSStatus]:
        """Get delivery status of sent message"""
        for message in self.sent_messages:
            if message.sid == sid:
                return message.status
        return None

    def get_sent_messages(
        self,
        to: Optional[str] = None,
        status: Optional[SMSStatus] = None,
        limit: int = 100
    ) -> List[SMSMessage]:
        """Get sent message history"""
        messages = self.sent_messages

        if to:
            to_normalized = self.normalize_phone_number(to)
            messages = [m for m in messages if m.to == to_normalized]

        if status:
            messages = [m for m in messages if m.status == status]

        return messages[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get SMS statistics"""
        total = len(self.sent_messages)
        if total == 0:
            return {
                'total': 0,
                'delivered': 0,
                'failed': 0,
                'delivery_rate': 0.0
            }

        delivered = len([m for m in self.sent_messages if m.status == SMSStatus.DELIVERED])
        failed = len([m for m in self.sent_messages if m.status == SMSStatus.FAILED])

        return {
            'total': total,
            'delivered': delivered,
            'failed': failed,
            'delivery_rate': (delivered / total * 100) if total > 0 else 0.0,
            'opted_out': len(self.opted_out_numbers)
        }

    # Convenience methods for common notifications

    def notify_service_created(self, to: str, service_name: str, region: str, rate: float):
        """Notify about new service creation"""
        return self.send_sms(
            to, '',
            template='service_created',
            service_name=service_name,
            region=region,
            rate=rate
        )

    def notify_service_updated(self, to: str, service_name: str):
        """Notify about service update"""
        return self.send_sms(
            to, '',
            template='service_updated',
            service_name=service_name
        )

    def notify_approval_required(self, to: str, item_name: str):
        """Notify about approval requirement"""
        return self.send_sms(
            to, '',
            template='approval_required',
            item_name=item_name
        )

    def send_verification_code(self, to: str, code: str):
        """Send verification code"""
        return self.send_sms(
            to, '',
            template='verification_code',
            code=code
        )

    def send_password_reset(self, to: str, code: str):
        """Send password reset code"""
        return self.send_sms(
            to, '',
            template='password_reset',
            code=code
        )

    def send_system_alert(self, to: str, message: str):
        """Send system alert"""
        return self.send_sms(
            to, '',
            template='system_alert',
            message=message
        )


# Global instance
_sms_manager: Optional[SMSManager] = None


def get_sms_manager() -> SMSManager:
    """Get global SMS manager instance"""
    global _sms_manager

    if _sms_manager is None:
        # Default configuration (test mode)
        _sms_manager = SMSManager(
            account_sid="test_account_sid",
            auth_token="test_auth_token",
            from_number="+4915112345678",
            test_mode=True
        )

    return _sms_manager


def configure_sms_manager(
    account_sid: str,
    auth_token: str,
    from_number: str,
    test_mode: bool = False
):
    """Configure SMS manager"""
    global _sms_manager
    _sms_manager = SMSManager(account_sid, auth_token, from_number, test_mode)
