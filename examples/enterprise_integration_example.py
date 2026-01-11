"""
Enterprise Features Integration Example

Demonstrates how to use all v3.0 enterprise features together:
- Multi-tenancy with data isolation
- Billing and subscriptions
- White-labeling and customization
- Monitoring and metrics
- Horizontal scaling
- Tenant portal API

This example shows a complete SaaS application setup.
"""

from datetime import datetime, timedelta
from decimal import Decimal

# Import enterprise features
from src.enterprise import (
    # Multi-tenancy
    get_tenant_manager,
    IsolationStrategy,
    SubscriptionTier,

    # Billing
    get_billing_engine,
    BillingCycle,

    # White-labeling
    get_whitelabel_manager,
    ColorScheme,
    ThemeMode,

    # Monitoring
    get_monitoring_engine,
    AlertSeverity,

    # Scaling
    get_scaling_engine,
    LoadBalancingAlgorithm,

    # Tenant Portal
    get_tenant_portal
)


def setup_complete_saas_platform():
    """
    Complete SaaS platform setup example
    Demonstrates integration of all enterprise features
    """

    print("=" * 80)
    print("ENTERPRISE SAAS PLATFORM SETUP - v3.0")
    print("=" * 80)
    print()

    # =========================================================================
    # STEP 1: Initialize Enterprise Services
    # =========================================================================
    print("STEP 1: Initializing enterprise services...")
    print("-" * 80)

    tenant_manager = get_tenant_manager()
    billing_engine = get_billing_engine()
    whitelabel_manager = get_whitelabel_manager()
    monitoring_engine = get_monitoring_engine()
    scaling_engine = get_scaling_engine()

    # Start monitoring and scaling engines
    monitoring_engine.collect_all_metrics()
    scaling_engine.start()

    print("✓ Tenant Manager initialized")
    print("✓ Billing Engine initialized")
    print("✓ White-label Manager initialized")
    print("✓ Monitoring Engine initialized")
    print("✓ Scaling Engine initialized")
    print()

    # =========================================================================
    # STEP 2: Create Multi-Tenant Organization
    # =========================================================================
    print("STEP 2: Creating multi-tenant organization...")
    print("-" * 80)

    # Create tenant with schema-per-tenant isolation
    tenant = tenant_manager.create_tenant(
        name="Acme Corporation",
        tier=SubscriptionTier.PROFESSIONAL,
        isolation_strategy=IsolationStrategy.SCHEMA_PER_TENANT,
        settings={
            "company_domain": "acme-corp.com",
            "industry": "Technology",
            "country": "Germany"
        }
    )

    print(f"✓ Tenant created: {tenant.name}")
    print(f"  - ID: {tenant.id}")
    print(f"  - Tier: {tenant.tier.value}")
    print(f"  - Isolation: {tenant.isolation_strategy.value}")
    print(f"  - Status: {tenant.status.value}")
    print()

    # =========================================================================
    # STEP 3: Setup Billing & Subscription
    # =========================================================================
    print("STEP 3: Setting up billing and subscription...")
    print("-" * 80)

    # Create subscription for the tenant
    subscription = billing_engine.create_subscription(
        tenant_id=tenant.id,
        plan_id='professional',
        billing_cycle=BillingCycle.YEARLY,
        trial=True
    )

    print(f"✓ Subscription created")
    print(f"  - Plan: PROFESSIONAL")
    print(f"  - Billing: {subscription.billing_cycle.value}")
    print(f"  - Status: {subscription.status}")
    print(f"  - Trial ends: {subscription.trial_end.strftime('%Y-%m-%d') if subscription.trial_end else 'N/A'}")
    print()

    # Record some usage
    print("Recording usage metrics...")
    usage_meter = billing_engine.usage_meter

    usage_meter.record_usage(tenant.id, subscription.id, 'api_calls', 1500)
    usage_meter.record_usage(tenant.id, subscription.id, 'storage_gb', 15.5)
    usage_meter.record_usage(tenant.id, subscription.id, 'documents', 250)

    print("✓ Usage metrics recorded")
    print("  - API calls: 1,500")
    print("  - Storage: 15.5 GB")
    print("  - Documents: 250")
    print()

    # =========================================================================
    # STEP 4: Configure White-Labeling
    # =========================================================================
    print("STEP 4: Configuring white-label branding...")
    print("-" * 80)

    # Create white-label configuration
    whitelabel_config = whitelabel_manager.create_config(
        tenant_id=tenant.id,
        company_name="Acme Corporation",
        domain="app.acme-corp.com"
    )

    # Customize branding
    acme_colors = ColorScheme(
        primary="#0066CC",
        secondary="#FF6600",
        success="#00CC66",
        background="#FFFFFF",
        text_primary="#333333"
    )

    whitelabel_manager.update_branding(
        tenant_id=tenant.id,
        color_scheme=acme_colors,
        theme_mode=ThemeMode.LIGHT
    )

    print(f"✓ White-label configuration created")
    print(f"  - Company: {whitelabel_config.company_name}")
    print(f"  - Domain: {whitelabel_config.domain}")
    print(f"  - Primary color: {acme_colors.primary}")
    print(f"  - Theme: {ThemeMode.LIGHT.value}")
    print()

    # Register custom domain
    domain_registered = whitelabel_manager.domain_manager.register_domain(
        tenant.id,
        "app.acme-corp.com"
    )

    if domain_registered:
        print("✓ Custom domain registered: app.acme-corp.com")
    print()

    # =========================================================================
    # STEP 5: Setup Monitoring & Alerts
    # =========================================================================
    print("STEP 5: Setting up monitoring and alerts...")
    print("-" * 80)

    # Add custom alert rule
    monitoring_engine.alert_manager.add_alert_rule(
        name=f"High API Usage - {tenant.name}",
        metric_name='api_requests_per_minute',
        condition='>',
        threshold=100.0,
        severity=AlertSeverity.WARNING,
        message=f"Tenant {tenant.name} exceeding API rate limit"
    )

    print("✓ Alert rule created: High API Usage")

    # Add notification handler
    def send_alert_notification(alert):
        print(f"  📧 Alert notification: {alert.name} - {alert.message}")

    monitoring_engine.alert_manager.register_notification_handler(
        send_alert_notification
    )

    print("✓ Notification handler registered")

    # Collect system metrics
    monitoring_engine.resource_monitor.collect_metrics()

    resource_usage = monitoring_engine.resource_monitor.get_resource_usage()
    print(f"✓ Current resource usage:")
    print(f"  - CPU: {resource_usage['cpu_percent']:.1f}%")
    print(f"  - Memory: {resource_usage['memory_percent']:.1f}%")
    print(f"  - Disk: {resource_usage['disk_percent']:.1f}%")
    print()

    # =========================================================================
    # STEP 6: Configure Horizontal Scaling
    # =========================================================================
    print("STEP 6: Configuring horizontal scaling...")
    print("-" * 80)

    # Register service instances
    service_name = "document-api"

    for i in range(3):
        instance = scaling_engine.register_service_instance(
            service_name=service_name,
            instance_id=f"doc-api-{i+1}",
            host=f"10.0.1.{i+10}",
            port=8000 + i,
            weight=1
        )
        print(f"✓ Service instance registered: {instance.id} ({instance.host}:{instance.port})")

    # Update instances to healthy status
    for i in range(3):
        scaling_engine.service_registry.update_instance_status(
            service_name,
            f"doc-api-{i+1}",
            ServiceStatus.HEALTHY
        )

    print()
    print(f"✓ Load balancer configured: {LoadBalancingAlgorithm.ROUND_ROBIN.value}")
    print(f"✓ 3 healthy instances available")
    print()

    # =========================================================================
    # STEP 7: Create Tenant Portal Access
    # =========================================================================
    print("STEP 7: Setting up tenant portal...")
    print("-" * 80)

    # Get tenant portal
    portal = get_tenant_portal(tenant.id)

    # Create API key
    api_key_result = portal.api_keys.create_api_key(
        name="Production API Key",
        scopes=["read:documents", "write:documents", "read:analytics"],
        expires_in_days=365
    )

    print("✓ API key created")
    print(f"  - Name: {api_key_result['name']}")
    print(f"  - Prefix: {api_key_result['prefix']}...")
    print(f"  - Scopes: {', '.join(api_key_result['scopes'])}")
    print(f"  - Expires: {api_key_result['expires_at'][:10] if api_key_result['expires_at'] else 'Never'}")
    print()

    # Create webhook
    webhook_result = portal.webhooks.create_webhook(
        name="Document Events",
        url="https://acme-corp.com/webhooks/documents",
        events=['document.created', 'document.updated', 'document.deleted']
    )

    print("✓ Webhook configured")
    print(f"  - Name: {webhook_result['name']}")
    print(f"  - URL: {webhook_result['url']}")
    print(f"  - Events: {', '.join(webhook_result['events'])}")
    print()

    # Invite team member
    team_result = portal.team.invite_member(
        email="john.doe@acme-corp.com",
        name="John Doe",
        role="admin",
        permissions=["manage:users", "manage:documents", "view:analytics"]
    )

    print("✓ Team member invited")
    print(f"  - Email: {team_result['email']}")
    print(f"  - Role: admin")
    print(f"  - Status: {team_result['status']}")
    print()

    # =========================================================================
    # STEP 8: Get Dashboard Summary
    # =========================================================================
    print("STEP 8: Retrieving tenant dashboard...")
    print("-" * 80)

    dashboard = portal.dashboard.get_dashboard_summary()

    print("📊 TENANT DASHBOARD SUMMARY")
    print()
    print(f"Tenant: {dashboard['tenant']['name']}")
    print(f"Status: {dashboard['tenant']['status']}")
    print()

    print("Subscription:")
    print(f"  Plan: {dashboard['subscription']['plan']}")
    print(f"  Status: {dashboard['subscription']['status']}")
    print(f"  Billing cycle: {dashboard['subscription']['billing_cycle']}")
    print()

    print("Current Usage:")
    if 'api_calls' in dashboard['usage']['current']:
        api_calls = dashboard['usage']['current']['api_calls']
        api_limit = dashboard['usage']['limits']['api_calls']
        api_pct = dashboard['usage']['percentage'].get('api_calls', 0)
        print(f"  API calls: {api_calls:,.0f} / {api_limit:,} ({api_pct:.1f}%)")

    if 'storage_gb' in dashboard['usage']['current']:
        storage = dashboard['usage']['current']['storage_gb']
        storage_limit = dashboard['usage']['limits']['storage_gb']
        storage_pct = dashboard['usage']['percentage'].get('storage', 0)
        print(f"  Storage: {storage:.1f} GB / {storage_limit} GB ({storage_pct:.1f}%)")

    if 'documents' in dashboard['usage']['current']:
        docs = dashboard['usage']['current']['documents']
        docs_limit = dashboard['usage']['limits']['documents']
        docs_pct = dashboard['usage']['percentage'].get('documents', 0)
        print(f"  Documents: {docs:,.0f} / {docs_limit:,} ({docs_pct:.1f}%)")

    print()
    print(f"System Health: {dashboard['health']['overall'].upper()}")
    print()

    # =========================================================================
    # STEP 9: Simulate Request Routing
    # =========================================================================
    print("STEP 9: Simulating request routing...")
    print("-" * 80)

    print("Routing 5 requests through load balancer:")
    for i in range(5):
        instance = scaling_engine.route_request(service_name)
        if instance:
            print(f"  Request {i+1} → {instance.id} ({instance.host}:{instance.port})")

    print()

    # =========================================================================
    # STEP 10: Get Billing Summary
    # =========================================================================
    print("STEP 10: Retrieving billing summary...")
    print("-" * 80)

    billing_summary = billing_engine.get_billing_summary(tenant.id)

    print("💰 BILLING SUMMARY")
    print()
    print(f"Plan: {billing_summary['subscription']['plan']}")
    print(f"Status: {billing_summary['subscription']['status']}")
    print(f"Billing cycle: {billing_summary['subscription']['billing_cycle']}")
    print()

    print("Invoices:")
    print(f"  Total: {billing_summary['invoices']['total']}")
    print(f"  Paid: {billing_summary['invoices']['paid']}")
    print(f"  Outstanding: {billing_summary['invoices']['outstanding']}")
    print()

    print("Amounts:")
    print(f"  Total paid: €{billing_summary['amounts']['total_paid']:.2f}")
    print(f"  Outstanding: €{billing_summary['amounts']['total_outstanding']:.2f}")
    print()

    # =========================================================================
    # COMPLETION
    # =========================================================================
    print("=" * 80)
    print("✅ ENTERPRISE SAAS PLATFORM SETUP COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Tenant: {tenant.name}")
    print(f"  - Subscription: PROFESSIONAL (yearly)")
    print(f"  - Custom domain: app.acme-corp.com")
    print(f"  - Service instances: 3 healthy")
    print(f"  - API keys: 1 active")
    print(f"  - Webhooks: 1 configured")
    print(f"  - Team members: 1 invited")
    print(f"  - System health: {dashboard['health']['overall']}")
    print()
    print("The platform is now ready for production use! 🚀")
    print()

    # Stop scaling engine
    scaling_engine.stop()

    return {
        'tenant': tenant,
        'subscription': subscription,
        'whitelabel_config': whitelabel_config,
        'dashboard': dashboard,
        'billing_summary': billing_summary
    }


def demonstrate_usage_metering():
    """
    Demonstrates usage metering and overage billing
    """
    print()
    print("=" * 80)
    print("USAGE METERING & OVERAGE BILLING EXAMPLE")
    print("=" * 80)
    print()

    billing_engine = get_billing_engine()

    # Get subscription (from previous setup)
    tenant_id = "example-tenant-id"
    subscription = next(
        (s for s in billing_engine.subscriptions.values()
         if s.tenant_id == tenant_id),
        None
    )

    if not subscription:
        print("Note: Run setup_complete_saas_platform() first")
        return

    plan = billing_engine.plan_manager.get_plan(subscription.plan_id)

    print(f"Plan: {plan.name}")
    print(f"API calls limit: {plan.max_api_calls_per_month:,}/month")
    print()

    # Simulate usage over time
    print("Simulating API usage over 30 days...")

    usage_meter = billing_engine.usage_meter
    start_date = datetime.now() - timedelta(days=30)

    total_calls = 0
    for day in range(30):
        date = start_date + timedelta(days=day)
        daily_calls = 3500 + (day * 100)  # Increasing usage

        usage_meter.record_usage(
            tenant_id=tenant_id,
            subscription_id=subscription.id,
            metric_name='api_calls',
            quantity=daily_calls
        )

        total_calls += daily_calls

    print(f"✓ Total API calls recorded: {total_calls:,}")
    print()

    # Check for overage
    if total_calls > plan.max_api_calls_per_month:
        overage = total_calls - plan.max_api_calls_per_month
        overage_cost = Decimal(str(overage)) * Decimal("0.01")

        print(f"⚠️  OVERAGE DETECTED")
        print(f"   Limit: {plan.max_api_calls_per_month:,} calls")
        print(f"   Used: {total_calls:,} calls")
        print(f"   Overage: {overage:,} calls")
        print(f"   Additional charge: €{overage_cost:.2f}")
    else:
        remaining = plan.max_api_calls_per_month - total_calls
        print(f"✓ Within limits")
        print(f"  Remaining: {remaining:,} calls")

    print()


def demonstrate_white_label_customization():
    """
    Demonstrates white-label customization capabilities
    """
    print()
    print("=" * 80)
    print("WHITE-LABEL CUSTOMIZATION EXAMPLE")
    print("=" * 80)
    print()

    whitelabel_manager = get_whitelabel_manager()
    tenant_id = "example-tenant-id"

    # Get theme bundle
    theme_bundle = whitelabel_manager.get_theme_bundle(tenant_id)

    if theme_bundle and theme_bundle.get('light_css'):
        print("Generated Theme CSS Preview:")
        print("-" * 80)
        css_lines = theme_bundle['light_css'].split('\n')[:20]
        print('\n'.join(css_lines))
        print("...")
        print()

    # Render email with branding
    email_content = whitelabel_manager.render_email(
        tenant_id=tenant_id,
        template_id='welcome',
        variables={
            'user_name': 'John Doe',
            'login_url': 'https://app.acme-corp.com/login'
        }
    )

    if email_content:
        print("Branded Email Preview:")
        print("-" * 80)
        print(f"Subject: {email_content['subject']}")
        print()
        print("HTML Body (excerpt):")
        html_lines = email_content['html_body'].split('\n')[:10]
        print('\n'.join(html_lines))
        print("...")
        print()


if __name__ == '__main__':
    # Run complete setup
    result = setup_complete_saas_platform()

    # Demonstrate usage metering
    # demonstrate_usage_metering()

    # Demonstrate white-label customization
    # demonstrate_white_label_customization()

    print("✅ All examples completed successfully!")
