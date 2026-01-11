"""
Multi-Tenancy Framework

Provides multi-tenant architecture with:
- Tenant isolation strategies
- Data separation (database per tenant, schema per tenant, shared database)
- Tenant context management
- Tenant provisioning and lifecycle
- Cross-tenant operations
- Resource quotas and limits
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading


class IsolationStrategy(str, Enum):
    """Data isolation strategies"""
    DATABASE_PER_TENANT = "database_per_tenant"  # Most isolated
    SCHEMA_PER_TENANT = "schema_per_tenant"      # Medium isolation
    SHARED_DATABASE = "shared_database"          # Least isolated, most efficient


class TenantStatus(str, Enum):
    """Tenant lifecycle status"""
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPROVISIONING = "deprovisioning"
    ARCHIVED = "archived"


class SubscriptionPlan(str, Enum):
    """Subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class ResourceQuota:
    """Resource quota limits"""
    max_users: int = 10
    max_services: int = 100
    max_storage_gb: int = 10
    max_api_calls_per_day: int = 10000
    max_workflows: int = 10
    max_integrations: int = 5


@dataclass
class Tenant:
    """Multi-tenant organization"""
    id: str
    name: str
    slug: str  # URL-friendly identifier
    domain: Optional[str] = None
    status: TenantStatus = TenantStatus.PROVISIONING
    isolation_strategy: IsolationStrategy = IsolationStrategy.SHARED_DATABASE
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    quota: ResourceQuota = field(default_factory=ResourceQuota)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Database connection info (for database-per-tenant)
    database_host: Optional[str] = None
    database_name: Optional[str] = None
    database_schema: Optional[str] = None


@dataclass
class TenantUsage:
    """Tenant resource usage tracking"""
    tenant_id: str
    users_count: int = 0
    services_count: int = 0
    storage_used_gb: float = 0.0
    api_calls_today: int = 0
    workflows_count: int = 0
    integrations_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TenantContext:
    """Current tenant context"""
    tenant_id: str
    tenant_name: str
    user_id: Optional[int] = None
    permissions: List[str] = field(default_factory=list)


# Thread-local storage for tenant context
_tenant_context = threading.local()


class TenantContextManager:
    """Manages tenant context for requests"""

    @staticmethod
    def set_context(tenant_id: str, tenant_name: str, user_id: Optional[int] = None):
        """Set current tenant context"""
        _tenant_context.current = TenantContext(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            user_id=user_id
        )

    @staticmethod
    def get_context() -> Optional[TenantContext]:
        """Get current tenant context"""
        return getattr(_tenant_context, 'current', None)

    @staticmethod
    def clear_context():
        """Clear tenant context"""
        if hasattr(_tenant_context, 'current'):
            delattr(_tenant_context, 'current')

    @staticmethod
    def get_tenant_id() -> Optional[str]:
        """Get current tenant ID"""
        context = TenantContextManager.get_context()
        return context.tenant_id if context else None


class TenantProvisioner:
    """Provisions new tenants"""

    def __init__(self):
        self.provisioning_steps = [
            self._create_database_resources,
            self._create_default_data,
            self._setup_integrations,
            self._configure_security,
            self._activate_tenant
        ]

    def provision_tenant(
        self,
        name: str,
        slug: str,
        plan: SubscriptionPlan,
        isolation_strategy: IsolationStrategy
    ) -> Tenant:
        """Provision new tenant"""
        tenant_id = str(uuid.uuid4())

        # Create tenant
        tenant = Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            status=TenantStatus.PROVISIONING,
            isolation_strategy=isolation_strategy,
            subscription_plan=plan,
            quota=self._get_quota_for_plan(plan)
        )

        # Execute provisioning steps
        for step in self.provisioning_steps:
            try:
                step(tenant)
            except Exception as e:
                print(f"[Provisioning] Step failed: {e}")
                tenant.status = TenantStatus.SUSPENDED
                raise

        return tenant

    def _create_database_resources(self, tenant: Tenant):
        """Create database resources based on isolation strategy"""
        if tenant.isolation_strategy == IsolationStrategy.DATABASE_PER_TENANT:
            # Create separate database
            tenant.database_name = f"tenant_{tenant.slug}"
            tenant.database_host = "localhost"  # Or load balancer
            print(f"[Provisioning] Created database: {tenant.database_name}")

        elif tenant.isolation_strategy == IsolationStrategy.SCHEMA_PER_TENANT:
            # Create schema in shared database
            tenant.database_schema = f"tenant_{tenant.slug}"
            print(f"[Provisioning] Created schema: {tenant.database_schema}")

        else:  # SHARED_DATABASE
            # Just use tenant_id filtering
            print(f"[Provisioning] Using shared database with tenant_id filtering")

    def _create_default_data(self, tenant: Tenant):
        """Create default data for tenant"""
        print(f"[Provisioning] Creating default data for {tenant.name}")
        # Create default admin user, settings, etc.

    def _setup_integrations(self, tenant: Tenant):
        """Setup default integrations"""
        print(f"[Provisioning] Setting up integrations for {tenant.name}")

    def _configure_security(self, tenant: Tenant):
        """Configure security settings"""
        print(f"[Provisioning] Configuring security for {tenant.name}")

    def _activate_tenant(self, tenant: Tenant):
        """Activate tenant"""
        tenant.status = TenantStatus.ACTIVE
        print(f"[Provisioning] Tenant {tenant.name} activated")

    def _get_quota_for_plan(self, plan: SubscriptionPlan) -> ResourceQuota:
        """Get resource quota for subscription plan"""
        quotas = {
            SubscriptionPlan.FREE: ResourceQuota(
                max_users=5,
                max_services=50,
                max_storage_gb=5,
                max_api_calls_per_day=1000,
                max_workflows=3,
                max_integrations=2
            ),
            SubscriptionPlan.STARTER: ResourceQuota(
                max_users=10,
                max_services=200,
                max_storage_gb=20,
                max_api_calls_per_day=10000,
                max_workflows=10,
                max_integrations=5
            ),
            SubscriptionPlan.PROFESSIONAL: ResourceQuota(
                max_users=50,
                max_services=1000,
                max_storage_gb=100,
                max_api_calls_per_day=100000,
                max_workflows=50,
                max_integrations=20
            ),
            SubscriptionPlan.ENTERPRISE: ResourceQuota(
                max_users=999999,
                max_services=999999,
                max_storage_gb=999999,
                max_api_calls_per_day=999999999,
                max_workflows=999999,
                max_integrations=999999
            )
        }

        return quotas.get(plan, quotas[SubscriptionPlan.FREE])


class TenantManager:
    """Manages tenant lifecycle"""

    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_usage: Dict[str, TenantUsage] = {}
        self.provisioner = TenantProvisioner()

    def create_tenant(
        self,
        name: str,
        slug: str,
        plan: SubscriptionPlan = SubscriptionPlan.FREE,
        isolation_strategy: IsolationStrategy = IsolationStrategy.SHARED_DATABASE,
        domain: Optional[str] = None
    ) -> Tenant:
        """Create new tenant"""
        # Check if slug is unique
        if any(t.slug == slug for t in self.tenants.values()):
            raise ValueError(f"Tenant slug '{slug}' already exists")

        # Provision tenant
        tenant = self.provisioner.provision_tenant(name, slug, plan, isolation_strategy)

        if domain:
            tenant.domain = domain

        self.tenants[tenant.id] = tenant

        # Initialize usage tracking
        self.tenant_usage[tenant.id] = TenantUsage(tenant_id=tenant.id)

        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug"""
        for tenant in self.tenants.values():
            if tenant.slug == slug:
                return tenant
        return None

    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        for tenant in self.tenants.values():
            if tenant.domain == domain:
                return tenant
        return None

    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Suspend tenant (e.g., for non-payment)"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False

        tenant.status = TenantStatus.SUSPENDED
        tenant.metadata['suspension_reason'] = reason
        tenant.metadata['suspended_at'] = datetime.now().isoformat()

        print(f"[Tenant] Suspended {tenant.name}: {reason}")
        return True

    def reactivate_tenant(self, tenant_id: str) -> bool:
        """Reactivate suspended tenant"""
        tenant = self.get_tenant(tenant_id)
        if not tenant or tenant.status != TenantStatus.SUSPENDED:
            return False

        tenant.status = TenantStatus.ACTIVE
        tenant.metadata.pop('suspension_reason', None)
        tenant.metadata['reactivated_at'] = datetime.now().isoformat()

        print(f"[Tenant] Reactivated {tenant.name}")
        return True

    def upgrade_plan(self, tenant_id: str, new_plan: SubscriptionPlan) -> bool:
        """Upgrade tenant subscription plan"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False

        old_plan = tenant.subscription_plan
        tenant.subscription_plan = new_plan
        tenant.quota = self.provisioner._get_quota_for_plan(new_plan)

        print(f"[Tenant] Upgraded {tenant.name} from {old_plan} to {new_plan}")
        return True

    def check_quota(self, tenant_id: str, resource: str) -> bool:
        """Check if tenant is within quota limits"""
        tenant = self.get_tenant(tenant_id)
        usage = self.tenant_usage.get(tenant_id)

        if not tenant or not usage:
            return False

        quota_checks = {
            'users': usage.users_count < tenant.quota.max_users,
            'services': usage.services_count < tenant.quota.max_services,
            'storage': usage.storage_used_gb < tenant.quota.max_storage_gb,
            'api_calls': usage.api_calls_today < tenant.quota.max_api_calls_per_day,
            'workflows': usage.workflows_count < tenant.quota.max_workflows,
            'integrations': usage.integrations_count < tenant.quota.max_integrations
        }

        return quota_checks.get(resource, True)

    def increment_usage(self, tenant_id: str, resource: str, amount: int = 1):
        """Increment resource usage"""
        usage = self.tenant_usage.get(tenant_id)
        if not usage:
            return

        if resource == 'users':
            usage.users_count += amount
        elif resource == 'services':
            usage.services_count += amount
        elif resource == 'api_calls':
            usage.api_calls_today += amount
        elif resource == 'workflows':
            usage.workflows_count += amount
        elif resource == 'integrations':
            usage.integrations_count += amount

        usage.last_updated = datetime.now()

    def get_tenant_statistics(self) -> Dict[str, Any]:
        """Get overall tenant statistics"""
        total_tenants = len(self.tenants)
        active_tenants = len([t for t in self.tenants.values() if t.status == TenantStatus.ACTIVE])
        suspended_tenants = len([t for t in self.tenants.values() if t.status == TenantStatus.SUSPENDED])

        by_plan = {}
        for tenant in self.tenants.values():
            plan = tenant.subscription_plan.value
            by_plan[plan] = by_plan.get(plan, 0) + 1

        by_strategy = {}
        for tenant in self.tenants.values():
            strategy = tenant.isolation_strategy.value
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1

        return {
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'suspended_tenants': suspended_tenants,
            'by_plan': by_plan,
            'by_isolation_strategy': by_strategy
        }


class DataIsolationMiddleware:
    """Middleware to enforce tenant data isolation"""

    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager

    def filter_query_by_tenant(self, query: str, table: str) -> str:
        """Add tenant_id filter to SQL query"""
        tenant_id = TenantContextManager.get_tenant_id()

        if not tenant_id:
            raise ValueError("No tenant context set")

        # Add WHERE clause or AND condition
        if 'WHERE' in query.upper():
            return query + f" AND {table}.tenant_id = '{tenant_id}'"
        else:
            return query + f" WHERE {table}.tenant_id = '{tenant_id}'"

    def inject_tenant_id(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Inject tenant_id into data"""
        tenant_id = TenantContextManager.get_tenant_id()

        if not tenant_id:
            raise ValueError("No tenant context set")

        data['tenant_id'] = tenant_id
        return data

    def validate_tenant_access(self, resource_tenant_id: str) -> bool:
        """Validate that current tenant can access resource"""
        current_tenant_id = TenantContextManager.get_tenant_id()

        if not current_tenant_id:
            return False

        return current_tenant_id == resource_tenant_id


# Global instance
_tenant_manager: Optional[TenantManager] = None


def get_tenant_manager() -> TenantManager:
    """Get global tenant manager instance"""
    global _tenant_manager

    if _tenant_manager is None:
        _tenant_manager = TenantManager()

    return _tenant_manager


def configure_tenant_manager():
    """Configure tenant manager"""
    global _tenant_manager
    _tenant_manager = TenantManager()
