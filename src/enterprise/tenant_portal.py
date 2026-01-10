"""
Tenant Portal API

Provides REST API endpoints for tenant self-service portal:
- Dashboard with analytics and insights
- Billing and subscription management
- Team and user management
- White-label customization
- API keys and webhooks management
- Usage tracking and reporting
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import secrets
import hashlib


class APIKeyStatus(str, Enum):
    """API key status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"


class WebhookEvent(str, Enum):
    """Webhook event types"""
    DOCUMENT_CREATED = "document.created"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_DELETED = "document.deleted"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAID = "invoice.paid"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"


@dataclass
class APIKey:
    """API key for tenant"""
    id: str
    tenant_id: str
    name: str
    key: str  # Hashed in production
    key_prefix: str  # First 8 chars for display

    status: APIKeyStatus = APIKeyStatus.ACTIVE
    scopes: List[str] = field(default_factory=list)

    # Usage
    total_requests: int = 0
    last_used_at: Optional[datetime] = None

    # Expiration
    expires_at: Optional[datetime] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Webhook:
    """Webhook configuration"""
    id: str
    tenant_id: str
    name: str
    url: str

    events: List[WebhookEvent] = field(default_factory=list)
    secret: str = ""  # For signature verification

    # Status
    is_active: bool = True

    # Delivery
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    last_delivery_at: Optional[datetime] = None
    last_delivery_status: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamMember:
    """Team member"""
    id: str
    tenant_id: str
    user_id: str
    email: str
    name: str

    role: str = "member"  # owner, admin, member, viewer

    # Status
    status: str = "active"  # active, invited, suspended
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None

    # Permissions
    permissions: List[str] = field(default_factory=list)

    # Activity
    last_login_at: Optional[datetime] = None

    created_at: datetime = field(default_factory=datetime.now)


class DashboardService:
    """Tenant dashboard service"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary statistics"""
        from .multitenancy import get_tenant_manager
        from .billing import get_billing_engine
        from .monitoring import get_monitoring_engine

        tenant_manager = get_tenant_manager()
        billing_engine = get_billing_engine()
        monitoring_engine = get_monitoring_engine()

        # Get tenant info
        tenant = tenant_manager.get_tenant(self.tenant_id)

        # Get subscription info
        subscription = next(
            (s for s in billing_engine.subscriptions.values()
             if s.tenant_id == self.tenant_id),
            None
        )

        plan = None
        if subscription:
            plan = billing_engine.plan_manager.get_plan(subscription.plan_id)

        # Get usage info
        now = datetime.now()
        period_start = subscription.current_period_start if subscription else now - timedelta(days=30)
        usage = billing_engine.usage_meter.get_usage_by_subscription(
            subscription.id if subscription else "",
            period_start,
            now
        ) if subscription else {}

        # Calculate usage percentages
        usage_percentage = {}
        if plan and subscription:
            if 'api_calls' in usage:
                usage_percentage['api_calls'] = (usage['api_calls'] / plan.max_api_calls_per_month) * 100
            if 'storage_gb' in usage:
                usage_percentage['storage'] = (usage['storage_gb'] / plan.max_storage_gb) * 100
            if 'documents' in usage:
                usage_percentage['documents'] = (usage['documents'] / plan.max_documents) * 100

        # Get billing summary
        billing_summary = billing_engine.get_billing_summary(self.tenant_id)

        # Get system health
        health_checks = monitoring_engine.health_check_manager.results

        return {
            'tenant': {
                'id': self.tenant_id,
                'name': tenant.name if tenant else 'Unknown',
                'status': tenant.status.value if tenant else 'unknown',
                'created_at': tenant.created_at.isoformat() if tenant else None
            },
            'subscription': {
                'plan': plan.name if plan else 'No subscription',
                'status': subscription.status if subscription else 'none',
                'billing_cycle': subscription.billing_cycle.value if subscription else None,
                'current_period_end': subscription.current_period_end.isoformat() if subscription else None,
                'trial_end': subscription.trial_end.isoformat() if subscription and subscription.trial_end else None
            },
            'usage': {
                'current': usage,
                'percentage': usage_percentage,
                'limits': {
                    'api_calls': plan.max_api_calls_per_month if plan else 0,
                    'storage_gb': plan.max_storage_gb if plan else 0,
                    'documents': plan.max_documents if plan else 0,
                    'users': plan.max_users if plan else 0
                } if plan else {}
            },
            'billing': billing_summary,
            'health': {
                'overall': monitoring_engine.health_check_manager.get_overall_health().value,
                'checks': {name: check.status.value for name, check in health_checks.items()}
            },
            'timestamp': now.isoformat()
        }

    def get_usage_analytics(
        self,
        metric: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage analytics for specific metric"""
        from .billing import get_billing_engine

        billing_engine = get_billing_engine()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get daily usage
        daily_usage = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            usage = billing_engine.usage_meter.get_usage(
                self.tenant_id,
                metric,
                current_date,
                next_date
            )

            daily_usage.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'value': usage
            })

            current_date = next_date

        # Calculate statistics
        values = [d['value'] for d in daily_usage]
        total = sum(values)
        avg = total / len(values) if values else 0
        max_val = max(values) if values else 0

        return {
            'metric': metric,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'daily': daily_usage,
            'statistics': {
                'total': total,
                'average': avg,
                'peak': max_val
            }
        }


class BillingManagementService:
    """Billing management service"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def get_subscription_details(self) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        from .billing import get_billing_engine

        billing_engine = get_billing_engine()

        subscription = next(
            (s for s in billing_engine.subscriptions.values()
             if s.tenant_id == self.tenant_id),
            None
        )

        if not subscription:
            return None

        plan = billing_engine.plan_manager.get_plan(subscription.plan_id)

        return {
            'subscription_id': subscription.id,
            'plan': {
                'id': plan.id if plan else None,
                'name': plan.name if plan else 'Unknown',
                'description': plan.description if plan else '',
                'price_monthly': float(plan.price_monthly) if plan else 0,
                'price_yearly': float(plan.price_yearly) if plan else 0,
                'features': [
                    {
                        'name': f.name,
                        'description': f.description,
                        'included': f.included,
                        'limit': f.limit,
                        'unit': f.unit
                    }
                    for f in plan.features
                ] if plan else []
            },
            'billing_cycle': subscription.billing_cycle.value,
            'status': subscription.status,
            'current_period': {
                'start': subscription.current_period_start.isoformat(),
                'end': subscription.current_period_end.isoformat()
            },
            'trial': {
                'active': subscription.status == 'trialing',
                'start': subscription.trial_start.isoformat() if subscription.trial_start else None,
                'end': subscription.trial_end.isoformat() if subscription.trial_end else None
            },
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'cancelled_at': subscription.cancelled_at.isoformat() if subscription.cancelled_at else None
        }

    def get_invoices(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get invoices for tenant"""
        from .billing import get_billing_engine

        billing_engine = get_billing_engine()

        # Get invoices for tenant
        invoices = [
            inv for inv in billing_engine.invoice_generator.invoices.values()
            if inv.tenant_id == self.tenant_id
        ]

        # Sort by date (newest first)
        invoices.sort(key=lambda x: x.issued_at, reverse=True)

        # Limit results
        invoices = invoices[:limit]

        return [
            {
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'status': inv.status.value,
                'amount': {
                    'subtotal': float(inv.subtotal),
                    'tax': float(inv.tax),
                    'discount': float(inv.discount),
                    'total': float(inv.total),
                    'currency': inv.currency
                },
                'line_items': [
                    {
                        'description': item.description,
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price),
                        'amount': float(item.amount)
                    }
                    for item in inv.line_items
                ],
                'dates': {
                    'issued': inv.issued_at.isoformat(),
                    'due': inv.due_date.isoformat(),
                    'paid': inv.paid_at.isoformat() if inv.paid_at else None
                },
                'payment_method': inv.payment_method.value if inv.payment_method else None
            }
            for inv in invoices
        ]

    def get_available_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans"""
        from .billing import get_billing_engine

        billing_engine = get_billing_engine()
        plans = billing_engine.plan_manager.list_plans(public_only=True)

        return [
            {
                'id': plan.id,
                'name': plan.name,
                'description': plan.description,
                'pricing': {
                    'monthly': float(plan.price_monthly),
                    'yearly': float(plan.price_yearly),
                    'currency': plan.currency
                },
                'features': [
                    {
                        'name': f.name,
                        'description': f.description,
                        'included': f.included,
                        'limit': f.limit,
                        'unit': f.unit
                    }
                    for f in plan.features
                ],
                'limits': {
                    'users': plan.max_users,
                    'storage_gb': plan.max_storage_gb,
                    'documents': plan.max_documents,
                    'api_calls_per_month': plan.max_api_calls_per_month
                },
                'trial_days': plan.trial_days
            }
            for plan in plans
        ]

    def change_plan(self, new_plan_id: str, billing_cycle: str) -> Dict[str, Any]:
        """Change subscription plan"""
        from .billing import get_billing_engine, BillingCycle

        billing_engine = get_billing_engine()

        # Get current subscription
        subscription = next(
            (s for s in billing_engine.subscriptions.values()
             if s.tenant_id == self.tenant_id),
            None
        )

        if not subscription:
            return {'success': False, 'error': 'No active subscription'}

        # Update subscription
        subscription.plan_id = new_plan_id
        subscription.billing_cycle = BillingCycle(billing_cycle)
        subscription.updated_at = datetime.now()

        return {
            'success': True,
            'message': 'Plan changed successfully',
            'new_plan': new_plan_id,
            'billing_cycle': billing_cycle
        }

    def cancel_subscription(self, immediate: bool = False) -> Dict[str, Any]:
        """Cancel subscription"""
        from .billing import get_billing_engine

        billing_engine = get_billing_engine()

        # Get current subscription
        subscription = next(
            (s for s in billing_engine.subscriptions.values()
             if s.tenant_id == self.tenant_id),
            None
        )

        if not subscription:
            return {'success': False, 'error': 'No active subscription'}

        success = billing_engine.cancel_subscription(subscription.id, immediate)

        return {
            'success': success,
            'message': 'Subscription cancelled' if immediate else 'Subscription will cancel at period end',
            'cancelled_at': datetime.now().isoformat() if immediate else None,
            'active_until': subscription.current_period_end.isoformat() if not immediate else None
        }


class TeamManagementService:
    """Team management service"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.team_members: Dict[str, TeamMember] = {}

    def list_members(self) -> List[Dict[str, Any]]:
        """List team members"""
        members = [m for m in self.team_members.values() if m.tenant_id == self.tenant_id]

        return [
            {
                'id': m.id,
                'user_id': m.user_id,
                'email': m.email,
                'name': m.name,
                'role': m.role,
                'status': m.status,
                'permissions': m.permissions,
                'joined_at': m.joined_at.isoformat() if m.joined_at else None,
                'last_login_at': m.last_login_at.isoformat() if m.last_login_at else None
            }
            for m in members
        ]

    def invite_member(
        self,
        email: str,
        name: str,
        role: str = "member",
        permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Invite new team member"""
        member_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        member = TeamMember(
            id=member_id,
            tenant_id=self.tenant_id,
            user_id=user_id,
            email=email,
            name=name,
            role=role,
            status="invited",
            invited_at=datetime.now(),
            permissions=permissions or []
        )

        self.team_members[member_id] = member

        return {
            'success': True,
            'member_id': member_id,
            'email': email,
            'status': 'invited'
        }

    def remove_member(self, member_id: str) -> Dict[str, Any]:
        """Remove team member"""
        member = self.team_members.get(member_id)

        if not member or member.tenant_id != self.tenant_id:
            return {'success': False, 'error': 'Member not found'}

        if member.role == 'owner':
            return {'success': False, 'error': 'Cannot remove owner'}

        del self.team_members[member_id]

        return {'success': True, 'message': 'Member removed'}

    def update_member_role(self, member_id: str, new_role: str) -> Dict[str, Any]:
        """Update member role"""
        member = self.team_members.get(member_id)

        if not member or member.tenant_id != self.tenant_id:
            return {'success': False, 'error': 'Member not found'}

        if member.role == 'owner':
            return {'success': False, 'error': 'Cannot change owner role'}

        member.role = new_role

        return {'success': True, 'new_role': new_role}


class APIKeyService:
    """API key management service"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.api_keys: Dict[str, APIKey] = {}

    def create_api_key(
        self,
        name: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create new API key"""
        key_id = str(uuid.uuid4())

        # Generate API key
        raw_key = secrets.token_urlsafe(32)
        key_prefix = raw_key[:8]

        # Hash key for storage
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        api_key = APIKey(
            id=key_id,
            tenant_id=self.tenant_id,
            name=name,
            key=hashed_key,
            key_prefix=key_prefix,
            scopes=scopes or [],
            expires_at=expires_at
        )

        self.api_keys[key_id] = api_key

        return {
            'id': key_id,
            'key': raw_key,  # Return raw key only once
            'prefix': key_prefix,
            'name': name,
            'scopes': scopes or [],
            'expires_at': expires_at.isoformat() if expires_at else None,
            'warning': 'Save this key securely. It will not be shown again.'
        }

    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List API keys"""
        keys = [k for k in self.api_keys.values() if k.tenant_id == self.tenant_id]

        return [
            {
                'id': k.id,
                'name': k.name,
                'prefix': k.key_prefix,
                'status': k.status.value,
                'scopes': k.scopes,
                'usage': {
                    'total_requests': k.total_requests,
                    'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None
                },
                'expires_at': k.expires_at.isoformat() if k.expires_at else None,
                'created_at': k.created_at.isoformat()
            }
            for k in keys
        ]

    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke API key"""
        api_key = self.api_keys.get(key_id)

        if not api_key or api_key.tenant_id != self.tenant_id:
            return {'success': False, 'error': 'API key not found'}

        api_key.status = APIKeyStatus.REVOKED

        return {'success': True, 'message': 'API key revoked'}


class WebhookService:
    """Webhook management service"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.webhooks: Dict[str, Webhook] = {}

    def create_webhook(
        self,
        name: str,
        url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Create new webhook"""
        webhook_id = str(uuid.uuid4())

        # Generate secret for signature verification
        secret = secrets.token_urlsafe(32)

        webhook = Webhook(
            id=webhook_id,
            tenant_id=self.tenant_id,
            name=name,
            url=url,
            events=[WebhookEvent(e) for e in events],
            secret=secret
        )

        self.webhooks[webhook_id] = webhook

        return {
            'id': webhook_id,
            'name': name,
            'url': url,
            'events': events,
            'secret': secret,
            'is_active': True
        }

    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List webhooks"""
        webhooks = [w for w in self.webhooks.values() if w.tenant_id == self.tenant_id]

        return [
            {
                'id': w.id,
                'name': w.name,
                'url': w.url,
                'events': [e.value for e in w.events],
                'is_active': w.is_active,
                'delivery_stats': {
                    'total': w.total_deliveries,
                    'successful': w.successful_deliveries,
                    'failed': w.failed_deliveries,
                    'success_rate': (w.successful_deliveries / w.total_deliveries * 100) if w.total_deliveries > 0 else 0
                },
                'last_delivery': {
                    'at': w.last_delivery_at.isoformat() if w.last_delivery_at else None,
                    'status': w.last_delivery_status
                },
                'created_at': w.created_at.isoformat()
            }
            for w in webhooks
        ]

    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Delete webhook"""
        webhook = self.webhooks.get(webhook_id)

        if not webhook or webhook.tenant_id != self.tenant_id:
            return {'success': False, 'error': 'Webhook not found'}

        del self.webhooks[webhook_id]

        return {'success': True, 'message': 'Webhook deleted'}

    def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Send test event to webhook"""
        webhook = self.webhooks.get(webhook_id)

        if not webhook or webhook.tenant_id != self.tenant_id:
            return {'success': False, 'error': 'Webhook not found'}

        # In production, send actual HTTP request to webhook URL
        # For now, simulate success

        return {
            'success': True,
            'message': 'Test event sent',
            'url': webhook.url,
            'response_time_ms': 150
        }


class TenantPortalAPI:
    """Main Tenant Portal API"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.dashboard = DashboardService(tenant_id)
        self.billing = BillingManagementService(tenant_id)
        self.team = TeamManagementService(tenant_id)
        self.api_keys = APIKeyService(tenant_id)
        self.webhooks = WebhookService(tenant_id)

    def get_portal_data(self) -> Dict[str, Any]:
        """Get complete portal data"""
        return {
            'dashboard': self.dashboard.get_dashboard_summary(),
            'subscription': self.billing.get_subscription_details(),
            'team': self.team.list_members(),
            'api_keys': self.api_keys.list_api_keys(),
            'webhooks': self.webhooks.list_webhooks()
        }


# Global tenant portals
_tenant_portals: Dict[str, TenantPortalAPI] = {}


def get_tenant_portal(tenant_id: str) -> TenantPortalAPI:
    """Get tenant portal instance"""
    if tenant_id not in _tenant_portals:
        _tenant_portals[tenant_id] = TenantPortalAPI(tenant_id)

    return _tenant_portals[tenant_id]
