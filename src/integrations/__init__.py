"""
Integrations Module

Provides external integrations with:
- ERP systems (SAP, Oracle, Dynamics)
- CRM systems (Salesforce, HubSpot, Zoho)
- Payment gateways (Stripe, PayPal, Square)
- Webhooks
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

__all__ = [
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
    'WebhookEvent'
]
