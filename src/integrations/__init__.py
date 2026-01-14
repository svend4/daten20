"""
Integrations Module - v3.7

Advanced enterprise integrations with cloud storage, productivity suites,
communication platforms, e-signature services, calendar, and file conversion.

Modules:
- cloud_storage: Google Drive, Dropbox, OneDrive, S3, Azure Blob
- productivity: Google Workspace, Microsoft 365, Docs, Sheets, Email
- communication: Slack, Microsoft Teams, Discord messaging
- esignature: DocuSign, Adobe Sign digital signatures
- calendar: Google Calendar, Outlook event management
- file_conversion: Document, image, spreadsheet format conversion

Legacy:
- erp: ERP system integrations (SAP, Oracle, Dynamics)
- crm: CRM integrations (Salesforce, HubSpot, Zoho)
- payments: Payment gateways (Stripe, PayPal, Square)
- webhooks: Webhook management

Version: 3.7.0
"""

__version__ = '3.7.0'

# Cloud Storage
from .cloud_storage import (
    StorageManager,
    StorageProvider,
    CloudFile,
    SharePermission,
    FilePermission,
    get_storage_manager,
)

# Productivity Suite
from .productivity import (
    ProductivityManager,
    ProductivitySuite,
    Document,
    Spreadsheet,
    Email,
    DocumentEditor,
    SpreadsheetManager,
    EmailClient,
    get_productivity_client,
)

# Communication Platforms
from .communication import (
    CommunicationManager,
    Platform,
    Channel,
    Message,
    MessageFormatter,
    WebhookManager,
    get_communication_client,
)

# E-Signature
from .esignature import (
    ESignatureManager,
    SignatureProvider,
    SignatureRequest,
    SignatureStatus,
    Signer,
    get_esignature_client,
)

# Calendar & Scheduling
from .calendar import (
    CalendarManager,
    CalendarProvider,
    CalendarEvent,
    get_calendar_client,
)

# File Conversion
from .file_conversion import (
    FileConverter,
    FileFormat,
    ConversionResult,
    get_file_converter,
)

# Legacy integrations (v2.8)
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
    WebhookManager as LegacyWebhookManager,
    get_webhook_manager,
    WebhookEvent
)

__all__ = [
    # Cloud Storage
    'StorageManager',
    'StorageProvider',
    'CloudFile',
    'SharePermission',
    'FilePermission',
    'get_storage_manager',

    # Productivity Suite
    'ProductivityManager',
    'ProductivitySuite',
    'Document',
    'Spreadsheet',
    'Email',
    'DocumentEditor',
    'SpreadsheetManager',
    'EmailClient',
    'get_productivity_client',

    # Communication Platforms
    'CommunicationManager',
    'Platform',
    'Channel',
    'Message',
    'MessageFormatter',
    'WebhookManager',
    'get_communication_client',

    # E-Signature
    'ESignatureManager',
    'SignatureProvider',
    'SignatureRequest',
    'SignatureStatus',
    'Signer',
    'get_esignature_client',

    # Calendar & Scheduling
    'CalendarManager',
    'CalendarProvider',
    'CalendarEvent',
    'get_calendar_client',

    # File Conversion
    'FileConverter',
    'FileFormat',
    'ConversionResult',
    'get_file_converter',

    # Legacy (v2.8)
    'ERPIntegrationEngine',
    'get_erp_engine',
    'configure_erp_engine',
    'CRMIntegrationEngine',
    'get_crm_engine',
    'configure_crm_engine',
    'PaymentGateway',
    'get_payment_gateway',
    'configure_payment_gateway',
    'LegacyWebhookManager',
    'get_webhook_manager',
    'ERPSystem',
    'EntityType',
    'CRMSystem',
    'CRMEntityType',
    'PaymentProvider',
    'PaymentMethod',
    'PaymentStatus',
    'WebhookEvent',
]
