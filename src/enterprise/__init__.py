"""
Enterprise Features Module

Provides enterprise-grade capabilities:
- Multi-tenancy with data isolation
- White-labeling and customization
- Advanced monitoring and metrics
- Horizontal scaling and load balancing
"""

from .multitenancy import (
    IsolationStrategy,
    TenantStatus,
    SubscriptionPlan,
    Tenant,
    TenantManager,
    TenantContextManager,
    get_tenant_manager
)

from .whitelabel import (
    ThemeMode,
    BrandingElement,
    ColorScheme,
    Typography,
    WhiteLabelConfig,
    WhiteLabelManager,
    get_whitelabel_manager
)

from .monitoring import (
    MetricType,
    AlertSeverity,
    HealthStatus,
    MonitoringEngine,
    get_monitoring_engine
)

from .scaling import (
    LoadBalancingAlgorithm,
    ServiceStatus,
    ScalingPolicy,
    ServiceInstance,
    ScalingConfig,
    ScalingEngine,
    get_scaling_engine
)

__all__ = [
    # Multi-tenancy
    'IsolationStrategy',
    'TenantStatus',
    'SubscriptionPlan',
    'Tenant',
    'TenantManager',
    'TenantContextManager',
    'get_tenant_manager',

    # White-labeling
    'ThemeMode',
    'BrandingElement',
    'ColorScheme',
    'Typography',
    'WhiteLabelConfig',
    'WhiteLabelManager',
    'get_whitelabel_manager',

    # Monitoring
    'MetricType',
    'AlertSeverity',
    'HealthStatus',
    'MonitoringEngine',
    'get_monitoring_engine',

    # Scaling
    'LoadBalancingAlgorithm',
    'ServiceStatus',
    'ScalingPolicy',
    'ServiceInstance',
    'ScalingConfig',
    'ScalingEngine',
    'get_scaling_engine',
]
