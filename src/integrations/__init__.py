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

__version__ = "3.7.0"

# Calendar & Scheduling
from .calendar import (
    CalendarEvent,
    CalendarManager,
    CalendarProvider,
    get_calendar_client,
)

# Cloud Storage
from .cloud_storage import (
    CloudFile,
    FilePermission,
    SharePermission,
    StorageManager,
    StorageProvider,
    get_storage_manager,
)

# Communication Platforms
from .communication import (
    Channel,
    CommunicationManager,
    Message,
    MessageFormatter,
    Platform,
    WebhookManager,
    get_communication_client,
)
from .crm import CRMEntityType, CRMIntegrationEngine, CRMSystem, configure_crm_engine, get_crm_engine

# Legacy integrations (v2.8)
from .erp import EntityType, ERPIntegrationEngine, ERPSystem, configure_erp_engine, get_erp_engine

# E-Signature
from .esignature import (
    ESignatureManager,
    SignatureProvider,
    SignatureRequest,
    SignatureStatus,
    Signer,
    get_esignature_client,
)

# File Conversion
from .file_conversion import (
    ConversionResult,
    FileConverter,
    FileFormat,
    get_file_converter,
)
from .payments import (
    PaymentGateway,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
    configure_payment_gateway,
    get_payment_gateway,
)

# Productivity Suite
from .productivity import (
    Document,
    DocumentEditor,
    Email,
    EmailClient,
    ProductivityManager,
    ProductivitySuite,
    Spreadsheet,
    SpreadsheetManager,
    get_productivity_client,
)
from .webhooks import WebhookEvent
from .webhooks import WebhookManager as LegacyWebhookManager
from .webhooks import get_webhook_manager

__all__ = [
    # Cloud Storage
    "StorageManager",
    "StorageProvider",
    "CloudFile",
    "SharePermission",
    "FilePermission",
    "get_storage_manager",
    # Productivity Suite
    "ProductivityManager",
    "ProductivitySuite",
    "Document",
    "Spreadsheet",
    "Email",
    "DocumentEditor",
    "SpreadsheetManager",
    "EmailClient",
    "get_productivity_client",
    # Communication Platforms
    "CommunicationManager",
    "Platform",
    "Channel",
    "Message",
    "MessageFormatter",
    "WebhookManager",
    "get_communication_client",
    # E-Signature
    "ESignatureManager",
    "SignatureProvider",
    "SignatureRequest",
    "SignatureStatus",
    "Signer",
    "get_esignature_client",
    # Calendar & Scheduling
    "CalendarManager",
    "CalendarProvider",
    "CalendarEvent",
    "get_calendar_client",
    # File Conversion
    "FileConverter",
    "FileFormat",
    "ConversionResult",
    "get_file_converter",
    # Legacy (v2.8)
    "ERPIntegrationEngine",
    "get_erp_engine",
    "configure_erp_engine",
    "CRMIntegrationEngine",
    "get_crm_engine",
    "configure_crm_engine",
    "PaymentGateway",
    "get_payment_gateway",
    "configure_payment_gateway",
    "LegacyWebhookManager",
    "get_webhook_manager",
    "ERPSystem",
    "EntityType",
    "CRMSystem",
    "CRMEntityType",
    "PaymentProvider",
    "PaymentMethod",
    "PaymentStatus",
    "WebhookEvent",
]
