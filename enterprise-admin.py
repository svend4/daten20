#!/usr/bin/env python3
"""
Enterprise Administration CLI Tool

Command-line interface for managing enterprise features in v3.0:
- Tenant management
- Billing and subscriptions
- Monitoring and metrics
- Scaling configuration
- White-label customization
- Portal management

Usage:
    python enterprise-admin.py tenant list
    python enterprise-admin.py tenant create "Company Name"
    python enterprise-admin.py billing invoice-generate <tenant-id>
    python enterprise-admin.py monitoring health-check
    python enterprise-admin.py scaling status
"""

import argparse
import sys
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Import enterprise modules
try:
    from src.enterprise import (
        BillingCycle,
        ColorScheme,
        IsolationStrategy,
        SubscriptionTier,
        get_billing_engine,
        get_monitoring_engine,
        get_scaling_engine,
        get_tenant_manager,
        get_tenant_portal,
        get_whitelabel_manager,
    )
except ImportError:
    print("Error: Enterprise modules not found. Please ensure the project is properly set up.")
    sys.exit(1)


class EnterpriseAdmin:
    """Enterprise administration CLI"""

    def __init__(self):
        self.tenant_manager = get_tenant_manager()
        self.billing_engine = get_billing_engine()
        self.monitoring_engine = get_monitoring_engine()
        self.scaling_engine = get_scaling_engine()
        self.whitelabel_manager = get_whitelabel_manager()

    # =========================================================================
    # TENANT MANAGEMENT
    # =========================================================================

    def tenant_list(self):
        """List all tenants"""
        print("\n📋 TENANT LIST")
        print("=" * 80)

        if not self.tenant_manager.tenants:
            print("No tenants found.")
            return

        print(f"{'ID':<12} {'Name':<25} {'Tier':<15} {'Status':<12} {'Created':<12}")
        print("-" * 80)

        for tenant in self.tenant_manager.tenants.values():
            print(
                f"{tenant.id[:10]:<12} {tenant.name[:24]:<25} "
                f"{tenant.tier.value:<15} {tenant.status.value:<12} "
                f"{tenant.created_at.strftime('%Y-%m-%d'):<12}"
            )

        print(f"\nTotal: {len(self.tenant_manager.tenants)} tenants")

    def tenant_create(self, name: str, tier: str = "free", isolation: str = "schema"):
        """Create new tenant"""
        print(f"\n✨ Creating tenant: {name}")
        print("-" * 80)

        try:
            tier_enum = SubscriptionTier(tier)
            isolation_enum = IsolationStrategy(
                f"{isolation}_per_tenant" if isolation != "shared" else "shared_database"
            )

            tenant = self.tenant_manager.create_tenant(name=name, tier=tier_enum, isolation_strategy=isolation_enum)

            print(f"✅ Tenant created successfully!")
            print(f"   ID: {tenant.id}")
            print(f"   Name: {tenant.name}")
            print(f"   Tier: {tenant.tier.value}")
            print(f"   Isolation: {tenant.isolation_strategy.value}")
            print(f"   Status: {tenant.status.value}")

        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def tenant_info(self, tenant_id: str):
        """Show tenant information"""
        tenant = self.tenant_manager.get_tenant(tenant_id)

        if not tenant:
            print(f"❌ Tenant not found: {tenant_id}")
            sys.exit(1)

        print(f"\n📊 TENANT INFORMATION")
        print("=" * 80)
        print(f"ID:               {tenant.id}")
        print(f"Name:             {tenant.name}")
        print(f"Tier:             {tenant.tier.value}")
        print(f"Isolation:        {tenant.isolation_strategy.value}")
        print(f"Status:           {tenant.status.value}")
        print(f"Created:          {tenant.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database:         {tenant.database_name or 'N/A'}")
        print(f"Schema:           {tenant.schema_name or 'N/A'}")

        # Show resource usage
        usage = self.tenant_manager.check_quota_usage(tenant_id)
        if usage:
            print(f"\nResource Usage:")
            print(f"  Users:          {usage['users_count']}/{usage['users_limit']}")
            print(f"  Storage:        {usage['storage_gb']:.2f}/{usage['storage_limit']} GB")
            print(f"  Documents:      {usage['documents_count']}/{usage['documents_limit']}")

    def tenant_delete(self, tenant_id: str, confirm: bool = False):
        """Delete tenant"""
        if not confirm:
            print("⚠️  Warning: This will permanently delete the tenant and all data!")
            print("   Use --confirm to proceed")
            sys.exit(1)

        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            print(f"❌ Tenant not found: {tenant_id}")
            sys.exit(1)

        print(f"🗑️  Deleting tenant: {tenant.name}")

        success = self.tenant_manager.deprovision_tenant(tenant_id)

        if success:
            print("✅ Tenant deleted successfully")
        else:
            print("❌ Failed to delete tenant")
            sys.exit(1)

    # =========================================================================
    # BILLING MANAGEMENT
    # =========================================================================

    def billing_list_plans(self):
        """List subscription plans"""
        print("\n💰 SUBSCRIPTION PLANS")
        print("=" * 80)

        plans = self.billing_engine.plan_manager.list_plans()

        for plan in plans:
            print(f"\n{plan.name.upper()}")
            print(f"  Monthly:  €{plan.price_monthly}")
            print(f"  Yearly:   €{plan.price_yearly} (save €{(plan.price_monthly * 12) - plan.price_yearly})")
            print(f"  Users:    {plan.max_users if plan.max_users < 999999 else 'Unlimited'}")
            print(f"  Storage:  {plan.max_storage_gb} GB")
            print(f"  Documents: {plan.max_documents if plan.max_documents < 999999 else 'Unlimited'}")
            print(f"  API Calls: {plan.max_api_calls_per_month:,}/month")
            if plan.trial_days > 0:
                print(f"  Trial:    {plan.trial_days} days")

    def billing_create_subscription(self, tenant_id: str, plan_id: str, billing_cycle: str = "monthly"):
        """Create subscription for tenant"""
        print(f"\n💳 Creating subscription for tenant {tenant_id[:10]}...")

        try:
            cycle = BillingCycle(billing_cycle)

            subscription = self.billing_engine.create_subscription(
                tenant_id=tenant_id, plan_id=plan_id, billing_cycle=cycle, trial=True
            )

            print("✅ Subscription created!")
            print(f"   Plan: {plan_id.upper()}")
            print(f"   Billing: {billing_cycle}")
            print(f"   Status: {subscription.status}")
            print(
                f"   Period: {subscription.current_period_start.strftime('%Y-%m-%d')} - "
                f"{subscription.current_period_end.strftime('%Y-%m-%d')}"
            )

            if subscription.trial_end:
                print(f"   Trial ends: {subscription.trial_end.strftime('%Y-%m-%d')}")

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def billing_generate_invoice(self, tenant_id: str):
        """Generate invoice for tenant"""
        print(f"\n📄 Generating invoice for tenant {tenant_id[:10]}...")

        # Find subscription
        subscription = next((s for s in self.billing_engine.subscriptions.values() if s.tenant_id == tenant_id), None)

        if not subscription:
            print("❌ No subscription found for this tenant")
            sys.exit(1)

        invoice = self.billing_engine.bill_subscription(subscription.id)

        if invoice:
            print("✅ Invoice generated!")
            print(f"   Invoice #: {invoice.invoice_number}")
            print(f"   Total: €{invoice.total}")
            print(f"   Due: {invoice.due_date.strftime('%Y-%m-%d')}")
            print(f"   Status: {invoice.status.value}")
        else:
            print("⚠️  No invoice generated (possibly in trial period)")

    def billing_summary(self, tenant_id: str):
        """Show billing summary for tenant"""
        summary = self.billing_engine.get_billing_summary(tenant_id)

        if not summary:
            print(f"❌ No billing data found for tenant {tenant_id}")
            sys.exit(1)

        print("\n💰 BILLING SUMMARY")
        print("=" * 80)
        print(f"Plan:             {summary['subscription']['plan']}")
        print(f"Status:           {summary['subscription']['status']}")
        print(f"Billing Cycle:    {summary['subscription']['billing_cycle']}")
        print(f"\nInvoices:")
        print(f"  Total:          {summary['invoices']['total']}")
        print(f"  Paid:           {summary['invoices']['paid']}")
        print(f"  Outstanding:    {summary['invoices']['outstanding']}")
        print(f"\nAmounts:")
        print(f"  Total Paid:     €{summary['amounts']['total_paid']:.2f}")
        print(f"  Outstanding:    €{summary['amounts']['total_outstanding']:.2f}")

    # =========================================================================
    # MONITORING
    # =========================================================================

    def monitoring_health_check(self):
        """Run system health checks"""
        print("\n🏥 SYSTEM HEALTH CHECK")
        print("=" * 80)

        # Run health checks
        results = self.monitoring_engine.health_check_manager.run_all_health_checks()

        if not results:
            print("No health checks configured")
            return

        for name, check in results.items():
            status_icon = "✅" if check.status.value == "healthy" else "❌"
            print(f"{status_icon} {name:<20} {check.status.value:<12} " f"({check.response_time_ms:.1f}ms)")

        # Overall health
        overall = self.monitoring_engine.health_check_manager.get_overall_health()
        print(f"\nOverall Status: {overall.value.upper()}")

    def monitoring_metrics(self):
        """Show system metrics"""
        print("\n📊 SYSTEM METRICS")
        print("=" * 80)

        # Collect metrics
        self.monitoring_engine.collect_all_metrics()

        # Resource usage
        usage = self.monitoring_engine.resource_monitor.get_resource_usage()
        print(f"\nResource Usage:")
        print(f"  CPU:            {usage['cpu_percent']:.1f}%")
        print(f"  Memory:         {usage['memory_percent']:.1f}%")
        print(f"  Disk:           {usage['disk_percent']:.1f}%")

        # Performance summary
        perf = self.monitoring_engine.performance_monitor.get_performance_summary()
        if perf.get("http_requests"):
            print(f"\nHTTP Requests (last hour):")
            print(f"  Count:          {perf['http_requests'].get('count', 0)}")
            print(f"  Avg:            {perf['http_requests'].get('avg', 0):.1f}ms")
            print(f"  P95:            {perf['http_requests'].get('p95', 0):.1f}ms")

    def monitoring_alerts(self):
        """Show active alerts"""
        print("\n🚨 ACTIVE ALERTS")
        print("=" * 80)

        alerts = self.monitoring_engine.alert_manager.get_active_alerts()

        if not alerts:
            print("No active alerts")
            return

        for alert in alerts:
            severity_icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}
            icon = severity_icons.get(alert.severity.value, "⚠️")

            print(f"{icon} [{alert.severity.value.upper()}] {alert.name}")
            print(f"   {alert.message}")
            print(f"   Created: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

    # =========================================================================
    # SCALING
    # =========================================================================

    def scaling_status(self):
        """Show scaling status"""
        print("\n⚖️  SCALING STATUS")
        print("=" * 80)

        status = self.scaling_engine.get_cluster_status()

        if not status:
            print("No services registered")
            return

        for service_name, service_info in status.items():
            print(f"\n{service_name}:")
            print(f"  Total Instances:    {service_info['total_instances']}")
            print(f"  Healthy Instances:  {service_info['healthy_instances']}")
            print(f"  Total Requests:     {service_info['total_requests']:,}")

            if service_info["instances"]:
                print(f"\n  Instances:")
                for instance in service_info["instances"]:
                    status_icon = "✅" if instance["status"] == "healthy" else "❌"
                    print(
                        f"    {status_icon} {instance['id']:<15} "
                        f"{instance['host']}:{instance['port']:<6} "
                        f"({instance['active_connections']} conn, "
                        f"{instance['total_requests']:,} req)"
                    )

    def scaling_register_instance(self, service_name: str, instance_id: str, host: str, port: int):
        """Register service instance"""
        print(f"\n📝 Registering instance: {instance_id}")

        instance = self.scaling_engine.register_service_instance(
            service_name=service_name, instance_id=instance_id, host=host, port=port
        )

        print(f"✅ Instance registered!")
        print(f"   Service: {service_name}")
        print(f"   ID: {instance_id}")
        print(f"   Address: {host}:{port}")

    # =========================================================================
    # WHITE-LABEL
    # =========================================================================

    def whitelabel_setup(self, tenant_id: str, company_name: str, domain: Optional[str] = None):
        """Setup white-label configuration"""
        print(f"\n🎨 Setting up white-label for: {company_name}")

        config = self.whitelabel_manager.create_config(tenant_id=tenant_id, company_name=company_name, domain=domain)

        print("✅ White-label configuration created!")
        print(f"   Company: {company_name}")
        if domain:
            print(f"   Domain: {domain}")

    # =========================================================================
    # PORTAL
    # =========================================================================

    def portal_dashboard(self, tenant_id: str):
        """Show tenant portal dashboard"""
        portal = get_tenant_portal(tenant_id)
        dashboard = portal.dashboard.get_dashboard_summary()

        print("\n📊 TENANT DASHBOARD")
        print("=" * 80)
        print(f"Tenant:           {dashboard['tenant']['name']}")
        print(f"Status:           {dashboard['tenant']['status']}")
        print(f"\nSubscription:")
        print(f"  Plan:           {dashboard['subscription']['plan']}")
        print(f"  Status:         {dashboard['subscription']['status']}")
        print(f"\nCurrent Usage:")

        usage = dashboard["usage"]
        if "api_calls" in usage["current"]:
            print(f"  API Calls:      {usage['current']['api_calls']:,.0f} / " f"{usage['limits']['api_calls']:,}")

        if "storage_gb" in usage["current"]:
            print(f"  Storage:        {usage['current']['storage_gb']:.1f} GB / " f"{usage['limits']['storage_gb']} GB")

        if "documents" in usage["current"]:
            print(f"  Documents:      {usage['current']['documents']:,.0f} / " f"{usage['limits']['documents']:,}")

        print(f"\nSystem Health:    {dashboard['health']['overall'].upper()}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enterprise Administration CLI for v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s tenant list
  %(prog)s tenant create "Acme Corp" --tier professional
  %(prog)s tenant info <tenant-id>
  %(prog)s tenant delete <tenant-id> --confirm

  %(prog)s billing plans
  %(prog)s billing subscribe <tenant-id> professional --cycle yearly
  %(prog)s billing invoice <tenant-id>
  %(prog)s billing summary <tenant-id>

  %(prog)s monitoring health
  %(prog)s monitoring metrics
  %(prog)s monitoring alerts

  %(prog)s scaling status
  %(prog)s scaling register <service> <instance-id> <host> <port>

  %(prog)s whitelabel setup <tenant-id> "Company Name" --domain app.example.com

  %(prog)s portal dashboard <tenant-id>
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Tenant commands
    tenant_parser = subparsers.add_parser("tenant", help="Tenant management")
    tenant_subparsers = tenant_parser.add_subparsers(dest="subcommand")

    tenant_subparsers.add_parser("list", help="List all tenants")

    tenant_create = tenant_subparsers.add_parser("create", help="Create new tenant")
    tenant_create.add_argument("name", help="Tenant name")
    tenant_create.add_argument("--tier", default="free", choices=["free", "starter", "professional", "enterprise"])
    tenant_create.add_argument("--isolation", default="schema", choices=["database", "schema", "shared"])

    tenant_info = tenant_subparsers.add_parser("info", help="Show tenant information")
    tenant_info.add_argument("tenant_id", help="Tenant ID")

    tenant_delete = tenant_subparsers.add_parser("delete", help="Delete tenant")
    tenant_delete.add_argument("tenant_id", help="Tenant ID")
    tenant_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # Billing commands
    billing_parser = subparsers.add_parser("billing", help="Billing management")
    billing_subparsers = billing_parser.add_subparsers(dest="subcommand")

    billing_subparsers.add_parser("plans", help="List subscription plans")

    billing_subscribe = billing_subparsers.add_parser("subscribe", help="Create subscription")
    billing_subscribe.add_argument("tenant_id", help="Tenant ID")
    billing_subscribe.add_argument("plan_id", choices=["free", "starter", "professional", "enterprise"])
    billing_subscribe.add_argument("--cycle", default="monthly", choices=["monthly", "quarterly", "yearly"])

    billing_invoice = billing_subparsers.add_parser("invoice", help="Generate invoice")
    billing_invoice.add_argument("tenant_id", help="Tenant ID")

    billing_summary = billing_subparsers.add_parser("summary", help="Show billing summary")
    billing_summary.add_argument("tenant_id", help="Tenant ID")

    # Monitoring commands
    monitoring_parser = subparsers.add_parser("monitoring", help="Monitoring and metrics")
    monitoring_subparsers = monitoring_parser.add_subparsers(dest="subcommand")

    monitoring_subparsers.add_parser("health", help="Run health checks")
    monitoring_subparsers.add_parser("metrics", help="Show system metrics")
    monitoring_subparsers.add_parser("alerts", help="Show active alerts")

    # Scaling commands
    scaling_parser = subparsers.add_parser("scaling", help="Scaling management")
    scaling_subparsers = scaling_parser.add_subparsers(dest="subcommand")

    scaling_subparsers.add_parser("status", help="Show scaling status")

    scaling_register = scaling_subparsers.add_parser("register", help="Register service instance")
    scaling_register.add_argument("service", help="Service name")
    scaling_register.add_argument("instance_id", help="Instance ID")
    scaling_register.add_argument("host", help="Host address")
    scaling_register.add_argument("port", type=int, help="Port number")

    # White-label commands
    whitelabel_parser = subparsers.add_parser("whitelabel", help="White-label management")
    whitelabel_subparsers = whitelabel_parser.add_subparsers(dest="subcommand")

    whitelabel_setup = whitelabel_subparsers.add_parser("setup", help="Setup white-label config")
    whitelabel_setup.add_argument("tenant_id", help="Tenant ID")
    whitelabel_setup.add_argument("company_name", help="Company name")
    whitelabel_setup.add_argument("--domain", help="Custom domain")

    # Portal commands
    portal_parser = subparsers.add_parser("portal", help="Portal management")
    portal_subparsers = portal_parser.add_subparsers(dest="subcommand")

    portal_dashboard = portal_subparsers.add_parser("dashboard", help="Show portal dashboard")
    portal_dashboard.add_argument("tenant_id", help="Tenant ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    admin = EnterpriseAdmin()

    try:
        # Tenant commands
        if args.command == "tenant":
            if args.subcommand == "list":
                admin.tenant_list()
            elif args.subcommand == "create":
                admin.tenant_create(args.name, args.tier, args.isolation)
            elif args.subcommand == "info":
                admin.tenant_info(args.tenant_id)
            elif args.subcommand == "delete":
                admin.tenant_delete(args.tenant_id, args.confirm)

        # Billing commands
        elif args.command == "billing":
            if args.subcommand == "plans":
                admin.billing_list_plans()
            elif args.subcommand == "subscribe":
                admin.billing_create_subscription(args.tenant_id, args.plan_id, args.cycle)
            elif args.subcommand == "invoice":
                admin.billing_generate_invoice(args.tenant_id)
            elif args.subcommand == "summary":
                admin.billing_summary(args.tenant_id)

        # Monitoring commands
        elif args.command == "monitoring":
            if args.subcommand == "health":
                admin.monitoring_health_check()
            elif args.subcommand == "metrics":
                admin.monitoring_metrics()
            elif args.subcommand == "alerts":
                admin.monitoring_alerts()

        # Scaling commands
        elif args.command == "scaling":
            if args.subcommand == "status":
                admin.scaling_status()
            elif args.subcommand == "register":
                admin.scaling_register_instance(args.service, args.instance_id, args.host, args.port)

        # White-label commands
        elif args.command == "whitelabel":
            if args.subcommand == "setup":
                admin.whitelabel_setup(args.tenant_id, args.company_name, args.domain)

        # Portal commands
        elif args.command == "portal":
            if args.subcommand == "dashboard":
                admin.portal_dashboard(args.tenant_id)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
