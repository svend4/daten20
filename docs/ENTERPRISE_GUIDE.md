# Enterprise Features Usage Guide (v3.0)

Complete guide to using the enterprise-grade features in the Document Management System.

## Table of Contents

1. [Overview](#overview)
2. [Multi-Tenancy](#multi-tenancy)
3. [Billing & Subscriptions](#billing--subscriptions)
4. [White-Labeling](#white-labeling)
5. [Monitoring & Metrics](#monitoring--metrics)
6. [Horizontal Scaling](#horizontal-scaling)
7. [Tenant Portal](#tenant-portal)
8. [Production Deployment](#production-deployment)

---

## Overview

The enterprise module (`src/enterprise/`) provides production-ready SaaS capabilities:

- **Multi-tenancy** - Isolate data between organizations
- **Billing** - Subscription management and payment processing
- **White-labeling** - Custom branding per tenant
- **Monitoring** - Metrics, alerts, and health checks
- **Scaling** - Load balancing and auto-scaling
- **Portal** - Self-service tenant management

### Quick Start

```python
from src.enterprise import (
    get_tenant_manager,
    get_billing_engine,
    get_whitelabel_manager,
    get_monitoring_engine,
    get_scaling_engine,
    get_tenant_portal
)

# Initialize services
tenant_manager = get_tenant_manager()
billing_engine = get_billing_engine()
portal = get_tenant_portal(tenant_id)
```

---

## Multi-Tenancy

### Isolation Strategies

Choose the right isolation strategy for your needs:

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **DATABASE_PER_TENANT** | Strong isolation, easy backup | Higher cost, complex management | Enterprise clients |
| **SCHEMA_PER_TENANT** | Good isolation, shared infrastructure | Medium complexity | Most SaaS apps |
| **SHARED_DATABASE** | Cost-effective, simple | Weaker isolation, complex queries | Small tenants |

### Creating a Tenant

```python
from src.enterprise import get_tenant_manager, IsolationStrategy, SubscriptionTier

tenant_manager = get_tenant_manager()

tenant = tenant_manager.create_tenant(
    name="Acme Corporation",
    tier=SubscriptionTier.PROFESSIONAL,
    isolation_strategy=IsolationStrategy.SCHEMA_PER_TENANT,
    settings={
        "company_domain": "acme.com",
        "industry": "Technology"
    }
)

print(f"Tenant created: {tenant.id}")
```

### Tenant Context

Use tenant context to ensure data isolation:

```python
from src.enterprise import TenantContextManager

# Set current tenant
TenantContextManager.set_tenant_id(tenant.id)

# Get current tenant
current_tenant = TenantContextManager.get_tenant_id()

# Clear context
TenantContextManager.clear()
```

### Resource Quotas

Resource limits are enforced per subscription plan:

```python
# Check quota usage
usage = tenant_manager.check_quota_usage(tenant.id)

print(f"Users: {usage['users_count']}/{usage['users_limit']}")
print(f"Storage: {usage['storage_gb']:.1f}/{usage['storage_limit']} GB")
print(f"Documents: {usage['documents_count']}/{usage['documents_limit']}")
```

---

## Billing & Subscriptions

### Subscription Plans

Four built-in plans are available:

| Plan | Monthly | Yearly | Users | Storage | Documents | API Calls/mo |
|------|---------|--------|-------|---------|-----------|--------------|
| **FREE** | €0 | €0 | 1 | 1 GB | 100 | 1,000 |
| **STARTER** | €29 | €290 | 5 | 10 GB | 1,000 | 10,000 |
| **PROFESSIONAL** | €99 | €990 | 25 | 100 GB | 10,000 | 100,000 |
| **ENTERPRISE** | €499 | €4,990 | Unlimited | 1 TB | Unlimited | Unlimited |

### Creating a Subscription

```python
from src.enterprise import get_billing_engine, BillingCycle

billing_engine = get_billing_engine()

subscription = billing_engine.create_subscription(
    tenant_id=tenant.id,
    plan_id='professional',
    billing_cycle=BillingCycle.YEARLY,
    payment_method_id='pm_xxxx',
    trial=True  # 14-day trial
)
```

### Usage Metering

Track usage to bill for overages:

```python
usage_meter = billing_engine.usage_meter

# Record API calls
usage_meter.record_usage(
    tenant_id=tenant.id,
    subscription_id=subscription.id,
    metric_name='api_calls',
    quantity=1500
)

# Get usage for period
from datetime import datetime, timedelta

end = datetime.now()
start = end - timedelta(days=30)

total_usage = usage_meter.get_usage(
    tenant_id=tenant.id,
    metric_name='api_calls',
    start_date=start,
    end_date=end
)

print(f"API calls this month: {total_usage:,}")
```

### Invoicing

Invoices are generated automatically:

```python
# Generate invoice manually
invoice = billing_engine.bill_subscription(subscription.id)

print(f"Invoice {invoice.invoice_number}")
print(f"Total: €{invoice.total}")
print(f"Due: {invoice.due_date.strftime('%Y-%m-%d')}")

# Process payment
from src.enterprise import PaymentMethod

payment = billing_engine.payment_processor.create_payment(
    invoice=invoice,
    payment_method=PaymentMethod.STRIPE
)

success = billing_engine.payment_processor.process_payment(payment.id)
```

### Changing Plans

```python
# Upgrade to enterprise
new_subscription = billing_engine.create_subscription(
    tenant_id=tenant.id,
    plan_id='enterprise',
    billing_cycle=BillingCycle.YEARLY
)

# Cancel old subscription
billing_engine.cancel_subscription(subscription.id, immediate=False)
```

---

## White-Labeling

### Custom Branding

```python
from src.enterprise import get_whitelabel_manager, ColorScheme, ThemeMode

whitelabel_manager = get_whitelabel_manager()

# Create configuration
config = whitelabel_manager.create_config(
    tenant_id=tenant.id,
    company_name="Acme Corporation",
    domain="app.acme.com"
)

# Set custom colors
custom_colors = ColorScheme(
    primary="#0066CC",
    secondary="#FF6600",
    success="#00CC66",
    background="#FFFFFF",
    text_primary="#333333"
)

whitelabel_manager.update_branding(
    tenant_id=tenant.id,
    color_scheme=custom_colors,
    theme_mode=ThemeMode.LIGHT
)
```

### Custom Domain

```python
# Register custom domain
success = whitelabel_manager.register_custom_domain(
    tenant_id=tenant.id,
    domain="app.acme.com"
)

# Verify domain ownership
verified = whitelabel_manager.domain_manager.verify_domain_ownership(
    domain="app.acme.com",
    verification_token="xxxx"
)
```

### Email Templates

```python
# Customize email template
template = whitelabel_manager.customize_email_template(
    tenant_id=tenant.id,
    template_id='welcome',
    customizations={
        'subject': 'Welcome to {{company_name}}!',
        'html_body': '<h1>Welcome!</h1><p>{{user_name}}</p>'
    }
)

# Render email
email = whitelabel_manager.render_email(
    tenant_id=tenant.id,
    template_id='welcome',
    variables={
        'user_name': 'John Doe',
        'login_url': 'https://app.acme.com/login'
    }
)

print(f"Subject: {email['subject']}")
print(f"HTML: {email['html_body']}")
```

### Theme Generation

```python
# Get complete theme bundle
theme = whitelabel_manager.get_theme_bundle(tenant.id)

# Apply to web application
css = theme['light_css']
# Inject into HTML: <style>{css}</style>
```

---

## Monitoring & Metrics

### Metrics Collection

```python
from src.enterprise import get_monitoring_engine

monitoring_engine = get_monitoring_engine()

# Record custom metrics
monitoring_engine.metrics_collector.record_counter(
    name='api_requests_total',
    value=1.0,
    labels={'endpoint': '/api/documents', 'method': 'GET'}
)

monitoring_engine.metrics_collector.record_histogram(
    name='api_response_time_ms',
    value=45.2,
    labels={'endpoint': '/api/documents'}
)

# Get statistics
stats = monitoring_engine.metrics_collector.calculate_statistics(
    name='api_response_time_ms',
    start_time=datetime.now() - timedelta(hours=1)
)

print(f"Avg response time: {stats['avg']:.1f}ms")
print(f"P95: {stats['p95']:.1f}ms")
print(f"P99: {stats['p99']:.1f}ms")
```

### Performance Monitoring

```python
# Track HTTP request
monitoring_engine.performance_monitor.track_request(
    endpoint='/api/documents',
    method='GET',
    duration_ms=45.2,
    status_code=200
)

# Track database query
monitoring_engine.performance_monitor.track_database_query(
    query_type='SELECT',
    duration_ms=12.5
)

# Get performance summary
summary = monitoring_engine.performance_monitor.get_performance_summary()
print(summary)
```

### Health Checks

```python
# Register health check
monitoring_engine.health_check_manager.register_health_check(
    name='database',
    check_func=lambda: check_database_connection()
)

# Run all health checks
results = monitoring_engine.health_check_manager.run_all_health_checks()

# Get overall health
health = monitoring_engine.health_check_manager.get_overall_health()
print(f"System health: {health.value}")
```

### Alerts

```python
from src.enterprise import AlertSeverity

# Add alert rule
monitoring_engine.alert_manager.add_alert_rule(
    name='High CPU Usage',
    metric_name='system_cpu_usage_percent',
    condition='>',
    threshold=80.0,
    severity=AlertSeverity.WARNING,
    message='CPU usage is high: {value}%'
)

# Register notification handler
def send_email_alert(alert):
    # Send email notification
    print(f"Alert: {alert.name} - {alert.message}")

monitoring_engine.alert_manager.register_notification_handler(send_email_alert)

# Evaluate rules
monitoring_engine.alert_manager.evaluate_rules()
```

---

## Horizontal Scaling

### Service Registration

```python
from src.enterprise import get_scaling_engine

scaling_engine = get_scaling_engine()
scaling_engine.start()

# Register service instances
for i in range(3):
    instance = scaling_engine.register_service_instance(
        service_name='document-api',
        instance_id=f'api-{i+1}',
        host=f'10.0.1.{i+10}',
        port=8000,
        weight=1
    )
```

### Load Balancing

```python
from src.enterprise import LoadBalancingAlgorithm

# Route request
instance = scaling_engine.route_request(
    service_name='document-api',
    session_id='user-123',  # For sticky sessions
    client_ip='192.168.1.100'  # For IP hash
)

print(f"Route to: {instance.host}:{instance.port}")
```

### Auto-Scaling

```python
from src.enterprise import ScalingConfig

# Configure auto-scaling
config = ScalingConfig(
    min_instances=2,
    max_instances=10,
    target_cpu_percent=70.0,
    target_memory_percent=80.0,
    scale_up_cooldown_seconds=300,
    scale_down_cooldown_seconds=600
)

# Evaluate scaling needs
action = scaling_engine.auto_scaler.evaluate_scaling(
    service_name='document-api',
    current_cpu_percent=85.0,
    current_memory_percent=75.0,
    current_rps=150.0
)

if action == 'scale_up':
    scaling_engine.auto_scaler.scale_up('document-api')
```

### Circuit Breaker

```python
# Get circuit breaker
circuit_breaker = scaling_engine.get_circuit_breaker('document-api')

# Call with circuit breaker
try:
    result = circuit_breaker.call(
        make_api_request,
        'https://api.example.com/data'
    )
except Exception as e:
    print(f"Circuit open: {e}")
```

---

## Tenant Portal

### Dashboard

```python
from src.enterprise import get_tenant_portal

portal = get_tenant_portal(tenant.id)

# Get complete dashboard
dashboard = portal.dashboard.get_dashboard_summary()

print(f"Tenant: {dashboard['tenant']['name']}")
print(f"Plan: {dashboard['subscription']['plan']}")
print(f"Usage: {dashboard['usage']}")
print(f"Health: {dashboard['health']['overall']}")

# Get usage analytics
analytics = portal.dashboard.get_usage_analytics(
    metric='api_calls',
    days=30
)

print(f"Total API calls: {analytics['statistics']['total']}")
print(f"Average per day: {analytics['statistics']['average']}")
```

### Billing Management

```python
# View subscription
subscription = portal.billing.get_subscription_details()
print(f"Plan: {subscription['plan']['name']}")
print(f"Price: €{subscription['plan']['price_monthly']}/month")

# View invoices
invoices = portal.billing.get_invoices(limit=10)
for invoice in invoices:
    print(f"{invoice['invoice_number']}: €{invoice['amount']['total']}")

# Change plan
result = portal.billing.change_plan(
    new_plan_id='enterprise',
    billing_cycle='yearly'
)

# Cancel subscription
result = portal.billing.cancel_subscription(immediate=False)
```

### Team Management

```python
# List team members
members = portal.team.list_members()

for member in members:
    print(f"{member['name']} ({member['role']})")

# Invite member
result = portal.team.invite_member(
    email='john@example.com',
    name='John Doe',
    role='admin',
    permissions=['manage:users', 'view:analytics']
)

# Update role
result = portal.team.update_member_role(
    member_id='member-123',
    new_role='viewer'
)
```

### API Keys

```python
# Create API key
api_key = portal.api_keys.create_api_key(
    name='Production API',
    scopes=['read:documents', 'write:documents'],
    expires_in_days=365
)

print(f"API Key: {api_key['key']}")
print("⚠️  Save this key! It won't be shown again.")

# List keys
keys = portal.api_keys.list_api_keys()

# Revoke key
portal.api_keys.revoke_api_key('key-123')
```

### Webhooks

```python
# Create webhook
webhook = portal.webhooks.create_webhook(
    name='Document Events',
    url='https://example.com/webhook',
    events=['document.created', 'document.updated', 'document.deleted']
)

print(f"Webhook ID: {webhook['id']}")
print(f"Secret: {webhook['secret']}")

# List webhooks
webhooks = portal.webhooks.list_webhooks()

for webhook in webhooks:
    print(f"{webhook['name']}: {webhook['delivery_stats']['success_rate']:.1f}% success")

# Test webhook
result = portal.webhooks.test_webhook('webhook-123')
```

---

## Production Deployment

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dms

# Redis
REDIS_URL=redis://localhost:6379/0

# Monitoring
PROMETHEUS_PORT=9090
METRICS_ENABLED=true

# Scaling
LOAD_BALANCER_ALGORITHM=round_robin
MIN_INSTANCES=2
MAX_INSTANCES=10

# Billing
STRIPE_API_KEY=sk_live_xxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxx
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    image: dms:v3.0
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=dms
      - POSTGRES_USER=dms
      - POSTGRES_PASSWORD=secret

  redis:
    image: redis:7

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dms-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dms-api
  template:
    metadata:
      labels:
        app: dms-api
    spec:
      containers:
      - name: dms-api
        image: dms:v3.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: dms-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: dms-api
spec:
  selector:
    app: dms-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Monitoring Setup

```python
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'dms'
    static_configs:
      - targets: ['localhost:8000']
```

### Security Checklist

- [ ] Enable HTTPS with valid SSL certificate
- [ ] Rotate API keys regularly
- [ ] Enable two-factor authentication for admin accounts
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Use secrets management (Vault, AWS Secrets Manager)
- [ ] Enable CORS with proper origins
- [ ] Configure CSP headers

---

## Support

For questions and support:
- Documentation: `/docs`
- Issues: GitHub Issues
- Email: support@example.com

## License

MIT License - see LICENSE file for details.
