"""
Integrations Module - v3.7

Provides external integrations with:
- ERP systems (SAP, Oracle, Dynamics)
- CRM systems (Salesforce, HubSpot, Zoho)
- Payment gateways (Stripe, PayPal, Square)
- Webhooks
- Cloud Storage (Google Drive, Dropbox, OneDrive, S3)
- Productivity Suites (Google Workspace, Microsoft 365)
- Communication Platforms (Slack, Teams, Discord)
- E-Signature Services (DocuSign, Adobe Sign)
- Calendar Integration (Google Calendar, Outlook)
- File Conversion (Documents, Images, Spreadsheets)

Version: 3.7.0
"""

from .erp import (
    ERPIntegrationEngine,
    get_erp_engine,
    configure_erp_engine,
    ERPSystem,
    EntityType
)

from .crm import (
    CRMIntegrationEngine,
    get_crm_engine,
    configure_crm_engine,
    CRMSystem,
    CRMEntityType
)

from .payments import (
    PaymentGateway,
    get_payment_gateway,
    configure_payment_gateway,
    PaymentProvider,
    PaymentMethod,
    PaymentStatus
)

from .webhooks import (
    WebhookManager,
    get_webhook_manager,
    WebhookEvent
)

# v3.7 Advanced Integrations
from .integration_services import (
    # Cloud Storage
    CloudStorageProvider,
    StorageManager,
    get_storage_manager,
    # Productivity
    ProductivityProvider,
    ProductivityClient,
    get_productivity_client,
    # Communication
    CommunicationProvider,
    CommunicationClient,
    get_communication_client,
    # E-Signature
    ESignatureProvider,
    ESignatureClient,
    SignatureRequest,
    SignatureStatus,
    get_esignature_client,
    # Calendar
    CalendarProvider,
    CalendarClient,
    CalendarEvent,
    get_calendar_client,
    # File Conversion
    FileConverter,
    get_file_converter,
)

__all__ = [
    # v2.8 Integrations
    'ERPIntegrationEngine',
    'get_erp_engine',
    'configure_erp_engine',
    'CRMIntegrationEngine',
    'get_crm_engine',
    'configure_crm_engine',
    'PaymentGateway',
    'get_payment_gateway',
    'configure_payment_gateway',
    'WebhookManager',
    'get_webhook_manager',
    'ERPSystem',
    'EntityType',
    'CRMSystem',
    'CRMEntityType',
    'PaymentProvider',
    'PaymentMethod',
    'PaymentStatus',
    'WebhookEvent',
    # v3.7 Cloud Storage
    'CloudStorageProvider',
    'StorageManager',
    'get_storage_manager',
    # v3.7 Productivity
    'ProductivityProvider',
    'ProductivityClient',
    'get_productivity_client',
    # v3.7 Communication
    'CommunicationProvider',
    'CommunicationClient',
    'get_communication_client',
    # v3.7 E-Signature
    'ESignatureProvider',
    'ESignatureClient',
    'SignatureRequest',
    'SignatureStatus',
    'get_esignature_client',
    # v3.7 Calendar
    'CalendarProvider',
    'CalendarClient',
    'CalendarEvent',
    'get_calendar_client',
    # v3.7 File Conversion
    'FileConverter',
    'get_file_converter',
]
