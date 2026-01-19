"""
Enterprise Features Module

Provides enterprise-grade capabilities:
- Multi-tenancy with data isolation
- White-labeling and customization
- Advanced monitoring and metrics
- Horizontal scaling and load balancing
- Billing and subscriptions
- Tenant self-service portal
"""

from .billing import SubscriptionPlan  # Full plan dataclass with pricing
from .billing import (
    BillingCycle,
    BillingEngine,
    Invoice,
    InvoiceStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Subscription,
    get_billing_engine,
)
from .monitoring import AlertSeverity, HealthStatus, MetricType, MonitoringEngine, get_monitoring_engine
from .multitenancy import (
    IsolationStrategy,
)
from .multitenancy import SubscriptionPlan as SubscriptionTier  # Enum of plan tiers
from .multitenancy import (
    Tenant,
    TenantContextManager,
    TenantManager,
    TenantStatus,
    get_tenant_manager,
)
from .scaling import (
    LoadBalancingAlgorithm,
    ScalingConfig,
    ScalingEngine,
    ScalingPolicy,
    ServiceInstance,
    ServiceStatus,
    get_scaling_engine,
)
from .tenant_portal import APIKey, APIKeyStatus, TeamMember, TenantPortalAPI, Webhook, WebhookEvent, get_tenant_portal
from .whitelabel import (
    BrandingElement,
    ColorScheme,
    ThemeMode,
    Typography,
    WhiteLabelConfig,
    WhiteLabelManager,
    get_whitelabel_manager,
)

__all__ = [
    # Multi-tenancy
    "IsolationStrategy",
    "TenantStatus",
    "SubscriptionTier",  # Renamed from SubscriptionPlan to avoid conflict
    "Tenant",
    "TenantManager",
    "TenantContextManager",
    "get_tenant_manager",
    # White-labeling
    "ThemeMode",
    "BrandingElement",
    "ColorScheme",
    "Typography",
    "WhiteLabelConfig",
    "WhiteLabelManager",
    "get_whitelabel_manager",
    # Monitoring
    "MetricType",
    "AlertSeverity",
    "HealthStatus",
    "MonitoringEngine",
    "get_monitoring_engine",
    # Scaling
    "LoadBalancingAlgorithm",
    "ServiceStatus",
    "ScalingPolicy",
    "ServiceInstance",
    "ScalingConfig",
    "ScalingEngine",
    "get_scaling_engine",
    # Billing
    "BillingCycle",
    "PaymentStatus",
    "InvoiceStatus",
    "PaymentMethod",
    "SubscriptionPlan",
    "Subscription",
    "Invoice",
    "Payment",
    "BillingEngine",
    "get_billing_engine",
    # Tenant Portal
    "APIKeyStatus",
    "WebhookEvent",
    "APIKey",
    "Webhook",
    "TeamMember",
    "TenantPortalAPI",
    "get_tenant_portal",
]
