# 🏢 Enterprise-Admin User Guide

**Version:** 3.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Multi-tenant enterprise administration and management

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Commands](#commands)
   - [Tenant Management](#tenant-management)
   - [Billing Management](#billing-management)
   - [Monitoring & Metrics](#monitoring--metrics)
   - [Scaling Management](#scaling-management)
   - [White-Label Management](#white-label-management)
   - [Portal Management](#portal-management)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)
6. [Enterprise Best Practices](#enterprise-best-practices)
7. [Tips & Advanced Usage](#tips--advanced-usage)

---

## 🎯 Overview

**enterprise-admin.py** is the enterprise-grade administration tool for managing multi-tenant Document Management System deployments. It provides comprehensive tenant lifecycle management, billing, monitoring, and white-label customization.

### Key Features

- ✅ **Multi-Tenant Management** - Create, manage, and isolate customer tenants
- ✅ **Subscription Billing** - Multiple pricing tiers with flexible billing cycles
- ✅ **Enterprise Monitoring** - Health checks, metrics, and alerting
- ✅ **Auto-Scaling** - Service registration and load balancing
- ✅ **White-Label** - Custom branding for each tenant
- ✅ **Admin Portal** - Web-based management dashboard

### Architecture

```
┌─────────────────────────────────────────┐
│     Enterprise Admin CLI                │
├─────────────────────────────────────────┤
│  Tenant │ Billing │ Monitor │ Scale     │
│    Mgmt │   Mgmt  │   Mgmt  │   Mgmt    │
├─────────────────────────────────────────┤
│         Multi-Tenant Database            │
│   ┌────────┐  ┌────────┐  ┌────────┐   │
│   │Tenant A│  │Tenant B│  │Tenant C│   │
│   └────────┘  └────────┘  └────────┘   │
└─────────────────────────────────────────┘
```

### When to Use

| Task | Command |
|------|---------|
| Create new customer | `enterprise-admin.py tenant create` |
| Manage subscriptions | `enterprise-admin.py billing subscribe` |
| Monitor system health | `enterprise-admin.py monitoring health` |
| Scale services | `enterprise-admin.py scaling register` |
| Custom branding | `enterprise-admin.py whitelabel setup` |

---

## ⚡ Quick Start

### Installation

```bash
# Ensure you have DMS installed
cd /path/to/daten20

# Make executable (Unix/Linux/Mac)
chmod +x enterprise-admin.py

# Verify installation
python enterprise-admin.py --help
```

### First-Time Setup

```bash
# 1. List subscription plans
python enterprise-admin.py billing plans

# 2. Create first tenant
python enterprise-admin.py tenant create "Acme Corporation" --tier professional

# 3. Check system health
python enterprise-admin.py monitoring health

# 4. View tenant dashboard
python enterprise-admin.py portal dashboard <tenant-id>
```

---

## 📚 Commands

### Tenant Management

Multi-tenant isolation and lifecycle management.

#### 1. List Tenants

Display all tenants in the system.

```bash
python enterprise-admin.py tenant list

# Output:
# Tenants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ID              Name              Tier          Status    Created      Users
# tenant_abc123   Acme Corp         professional  active    2026-01-01   45
# tenant_def456   TechStart Inc     starter       active    2026-01-05   12
# tenant_ghi789   Enterprise Co     enterprise    active    2026-01-10   156
# tenant_jkl012   Small Biz LLC     starter       trial     2026-01-15   3
```

**Tenant Tiers:**
- **starter** - Small teams (up to 10 users)
- **professional** - Growing businesses (up to 50 users)
- **enterprise** - Large organizations (unlimited users)
- **custom** - Tailored solutions

#### 2. Create Tenant

Create a new tenant with specified tier.

```bash
# Basic tenant creation
python enterprise-admin.py tenant create "Acme Corporation"

# Create with specific tier
python enterprise-admin.py tenant create "TechStart Inc" --tier professional

# Create with trial period
python enterprise-admin.py tenant create "Small Biz LLC" --tier starter --trial-days 30

# Output:
# ✅ Tenant created successfully
# Tenant ID: tenant_abc123
# Name: Acme Corporation
# Tier: professional
# Status: active
# Created: 2026-01-18
# Admin User: admin@acmecorp.com
# Admin Password: [Generated secure password]
```

**Options:**
- `--tier` - Subscription tier (starter/professional/enterprise)
- `--trial-days` - Trial period in days
- `--custom-domain` - Custom domain for tenant
- `--admin-email` - Admin user email

#### 3. Tenant Information

View detailed information about a specific tenant.

```bash
python enterprise-admin.py tenant info tenant_abc123

# Output:
# Tenant Information
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ID: tenant_abc123
# Name: Acme Corporation
# Tier: professional
# Status: active
# Created: 2026-01-01
# Last Login: 2026-01-18 14:30
#
# Subscription:
#   Plan: Professional Plan
#   Billing Cycle: monthly
#   Price: $99/month
#   Next Billing: 2026-02-01
#   Status: active
#
# Usage:
#   Users: 45 / 50 (90%)
#   Storage: 12.3 GB / 100 GB (12.3%)
#   Documents: 1,234
#   API Calls: 45,678 (this month)
#
# Features Enabled:
#   ✅ Advanced Analytics
#   ✅ SSO Integration
#   ✅ API Access
#   ✅ Custom Branding
#   ❌ White-label Portal (Enterprise only)
#   ❌ Dedicated Support (Enterprise only)
```

#### 4. Delete Tenant

Delete a tenant (requires confirmation).

```bash
# Delete with confirmation
python enterprise-admin.py tenant delete tenant_abc123 --confirm

# ⚠️ WARNING: This will permanently delete:
# - All tenant data
# - All users
# - All documents
# - All billing history
#
# Are you absolutely sure? Type 'DELETE' to confirm: DELETE
#
# Deleting tenant...
# ✅ Tenant deleted successfully
# Deleted: tenant_abc123 (Acme Corporation)
```

**Safety Features:**
- Requires explicit `--confirm` flag
- Requires typing 'DELETE' to confirm
- Creates final backup before deletion
- Logs deletion in audit trail
- Sends notification to admin

---

### Billing Management

Subscription and revenue management.

#### 1. List Plans

Display all available subscription plans.

```bash
python enterprise-admin.py billing plans

# Output:
# Subscription Plans
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Plan          Monthly    Yearly      Users    Storage    Features
# Starter       $29        $290        10       10 GB      Basic
# Professional  $99        $990        50       100 GB     Advanced
# Enterprise    $499       $4,990      Unlimited 1 TB      Full Suite
# Custom        Contact    Contact     Custom   Custom     Custom
#
# Features by Plan:
#
# Starter:
#   ✅ Document Management
#   ✅ Basic Search
#   ✅ Email Support
#   ❌ Advanced Analytics
#   ❌ SSO Integration
#
# Professional:
#   ✅ All Starter Features
#   ✅ Advanced Analytics
#   ✅ API Access
#   ✅ Custom Branding
#   ✅ Priority Support
#   ❌ White-label
#
# Enterprise:
#   ✅ All Professional Features
#   ✅ White-label Portal
#   ✅ SSO Integration
#   ✅ Dedicated Support
#   ✅ SLA Guarantee
#   ✅ Custom Development
```

#### 2. Create Subscription

Subscribe a tenant to a plan.

```bash
# Monthly subscription
python enterprise-admin.py billing subscribe tenant_abc123 professional

# Yearly subscription (discounted)
python enterprise-admin.py billing subscribe tenant_abc123 professional --cycle yearly

# Custom pricing
python enterprise-admin.py billing subscribe tenant_abc123 custom --price 299 --cycle monthly

# Output:
# ✅ Subscription created successfully
# Tenant: tenant_abc123 (Acme Corporation)
# Plan: Professional
# Billing Cycle: monthly
# Price: $99/month
# First Billing: 2026-02-01
# Payment Method: [Setup required]
#
# Next Steps:
# 1. Configure payment method
# 2. Send invoice to customer
# 3. Activate subscription
```

**Options:**
- `--cycle` - Billing cycle (monthly/yearly)
- `--price` - Custom pricing
- `--trial-days` - Free trial period
- `--auto-renew` - Auto-renewal (default: true)

#### 3. Generate Invoice

Generate billing invoice for a tenant.

```bash
python enterprise-admin.py billing invoice tenant_abc123

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INVOICE #INV-2026-01-001
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Bill To:                           Invoice Date: 2026-01-18
# Acme Corporation                   Due Date: 2026-02-01
# tenant_abc123                      Payment Terms: Net 15
# admin@acmecorp.com
#
# Description                        Qty    Unit Price    Amount
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Professional Plan (Monthly)        1      $99.00        $99.00
# Additional Users (5)               5      $10.00        $50.00
# Extra Storage (50 GB)              1      $20.00        $20.00
#                                                  Subtotal: $169.00
#                                                  Tax (8%): $13.52
#                                                    Total: $182.52
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Invoice saved to: invoices/INV-2026-01-001.pdf
# Email sent to: admin@acmecorp.com
```

#### 4. Billing Summary

View billing summary and revenue metrics.

```bash
python enterprise-admin.py billing summary tenant_abc123

# Output:
# Billing Summary - Acme Corporation (tenant_abc123)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Current Period: January 2026
#
# Subscription:
#   Plan: Professional
#   Price: $99/month
#   Status: Active
#   Next Billing: 2026-02-01
#
# Usage Charges:
#   Additional Users: $50.00 (5 users × $10)
#   Extra Storage: $20.00 (50 GB × $0.40/GB)
#   API Overage: $15.00 (5,000 calls × $0.003)
#   Total Usage: $85.00
#
# Total This Month: $184.00
# YTD Total: $1,104.00
#
# Payment History:
#   2026-01-01: $182.52 (Paid)
#   2025-12-01: $169.00 (Paid)
#   2025-11-01: $169.00 (Paid)
#
# Payment Status: ✅ Current (no overdue invoices)
```

---

### Monitoring & Metrics

System health monitoring and performance metrics.

#### 1. Health Checks

Run comprehensive health checks across all tenants.

```bash
python enterprise-admin.py monitoring health

# Output:
# Enterprise Health Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Overall Status: ✅ Healthy
#
# System Components:
#   ✅ Database Cluster (3/3 nodes healthy)
#   ✅ Application Servers (5/5 instances running)
#   ✅ Cache Layer (Redis) - 99.9% hit rate
#   ✅ Message Queue (RabbitMQ) - 0 messages in queue
#   ✅ File Storage (S3) - All buckets accessible
#   ⚠️ Search Engine (Elasticsearch) - 1 yellow index
#
# Tenant Health:
#   ✅ 45 tenants - All healthy
#   ✅ 1,234 active users
#   ✅ 12,345 documents processed today
#   ✅ 0 failed jobs in last 24h
#
# Resource Usage:
#   CPU: 45% average across cluster
#   Memory: 62% average
#   Disk: 38% average
#   Network: 120 Mbps average
#
# Warnings:
#   ⚠️ Elasticsearch index 'documents-2026-01' has 1 unassigned shard
#   Recommendation: Increase cluster size or rebalance
```

#### 2. System Metrics

View detailed system metrics and KPIs.

```bash
python enterprise-admin.py monitoring metrics

# Output:
# Enterprise Metrics (Last 24 Hours)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Business Metrics:
#   Active Tenants: 45
#   Total Users: 1,234
#   Documents Processed: 12,345
#   API Calls: 456,789
#   Revenue (MTD): $45,678
#
# Performance Metrics:
#   Avg Response Time: 120ms (p95: 350ms, p99: 890ms)
#   Request Rate: 1,234 req/min
#   Error Rate: 0.02% (9 errors / 456,789 requests)
#   Uptime: 99.98% (8m downtime in last 30 days)
#
# Resource Metrics:
#   CPU Usage: 45% (peak: 78%)
#   Memory Usage: 62% (peak: 85%)
#   Disk I/O: 450 MB/s read, 120 MB/s write
#   Network: 120 Mbps in, 180 Mbps out
#
# Database Metrics:
#   Queries/sec: 1,234
#   Avg Query Time: 12ms
#   Slow Queries: 23 (>1s)
#   Connection Pool: 80% utilized
#
# Cache Metrics:
#   Hit Rate: 99.2%
#   Eviction Rate: 0.5%
#   Memory Usage: 4.2 GB / 8 GB
```

#### 3. Active Alerts

View active monitoring alerts.

```bash
python enterprise-admin.py monitoring alerts

# Output:
# Active Alerts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Severity  Component         Message                         Since
# ⚠️ Warning Database         Slow queries detected (>1s)     2h ago
# ⚠️ Warning Elasticsearch    Yellow index status             6h ago
# ℹ️ Info    Storage          80% usage on tenant_xyz789      1d ago
#
# Recent Resolved Alerts (Last 24h):
#   ✅ High CPU usage - Resolved 3h ago
#   ✅ Memory pressure - Resolved 12h ago
#   ✅ Network latency spike - Resolved 18h ago
#
# Alert Configuration:
#   - Email notifications: ON
#   - Slack integration: ON
#   - PagerDuty: ON (critical only)
#   - Webhook: https://alerts.example.com/webhook
```

---

### Scaling Management

Service discovery and load balancing for horizontal scaling.

#### 1. Scaling Status

View current scaling configuration and service instances.

```bash
python enterprise-admin.py scaling status

# Output:
# Scaling Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Service Mesh:
#   Service Discovery: Consul
#   Load Balancer: HAProxy
#   Auto-scaling: Enabled
#
# Registered Services:
#
# api-server:
#   Instances: 5
#   Health: ✅ 5/5 healthy
#   Load: 45% average
#   Endpoints:
#     - api-1.internal:8000 (healthy, 42% load)
#     - api-2.internal:8000 (healthy, 48% load)
#     - api-3.internal:8000 (healthy, 46% load)
#     - api-4.internal:8000 (healthy, 43% load)
#     - api-5.internal:8000 (healthy, 46% load)
#
# worker-queue:
#   Instances: 3
#   Health: ✅ 3/3 healthy
#   Queue Size: 12 jobs
#   Processing Rate: 45 jobs/min
#
# database:
#   Primary: db-primary.internal:5432 (healthy)
#   Replicas: 2 (both healthy)
#   Replication Lag: <1s
#
# Auto-scaling Rules:
#   - Scale up at 80% CPU for 5 minutes
#   - Scale down at 30% CPU for 15 minutes
#   - Min instances: 2
#   - Max instances: 10
```

#### 2. Register Service

Register a new service instance for load balancing.

```bash
python enterprise-admin.py scaling register api-server api-6 api-6.internal 8000

# Output:
# ✅ Service registered successfully
# Service: api-server
# Instance ID: api-6
# Host: api-6.internal
# Port: 8000
# Health Check: http://api-6.internal:8000/health
# Status: Healthy
#
# Load Balancer Updated:
#   Total Instances: 6
#   Routing Configuration: Round-robin
#   Health Check Interval: 10s
#
# Traffic Distribution:
#   api-1: 16.7%
#   api-2: 16.7%
#   api-3: 16.7%
#   api-4: 16.7%
#   api-5: 16.7%
#   api-6: 16.7% (new)
```

---

### White-Label Management

Custom branding and domain configuration per tenant.

#### Setup White-Label

Configure custom branding for a tenant.

```bash
python enterprise-admin.py whitelabel setup tenant_abc123 "Acme Document System" \
  --domain app.acmecorp.com \
  --logo https://cdn.acmecorp.com/logo.png \
  --primary-color "#003366" \
  --secondary-color "#66CCFF"

# Output:
# ✅ White-label configuration created
# Tenant: tenant_abc123 (Acme Corporation)
#
# Branding:
#   Application Name: Acme Document System
#   Domain: app.acmecorp.com
#   Logo URL: https://cdn.acmecorp.com/logo.png
#   Primary Color: #003366
#   Secondary Color: #66CCFF
#
# DNS Configuration Required:
#   Add CNAME record:
#   app.acmecorp.com → dms.example.com
#
# SSL Certificate:
#   Status: Pending
#   Type: Let's Encrypt
#   Auto-renewal: Enabled
#
# Next Steps:
#   1. Configure DNS CNAME record
#   2. Wait for SSL certificate (5-10 minutes)
#   3. Test custom domain: https://app.acmecorp.com
```

**Customizable Elements:**
- Application name
- Custom domain
- Logo and favicon
- Color scheme (primary/secondary/accent)
- Custom CSS
- Email templates
- Login page customization

---

### Portal Management

Admin portal and dashboard access.

#### Portal Dashboard

Launch or view tenant admin portal.

```bash
python enterprise-admin.py portal dashboard tenant_abc123

# Output:
# Portal Dashboard - Acme Corporation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Portal URL: https://portal.example.com/tenant/tenant_abc123
# Admin Login: admin@acmecorp.com
# Last Access: 2026-01-18 14:30
#
# Quick Stats:
#   Users: 45 / 50
#   Storage: 12.3 GB / 100 GB
#   Documents: 1,234
#   API Calls (today): 5,678
#
# Recent Activity:
#   - Document uploaded: contract_v2.pdf (2 minutes ago)
#   - User logged in: john.doe@acmecorp.com (5 minutes ago)
#   - Report generated: monthly_summary.pdf (1 hour ago)
#
# Alerts:
#   ⚠️ Approaching user limit (45/50 - 90%)
#   ℹ️ Subscription renewal in 14 days
#
# Portal Features:
#   ✅ User Management
#   ✅ Document Library
#   ✅ Analytics Dashboard
#   ✅ Billing & Invoices
#   ✅ Settings & Configuration
#   ✅ API Keys Management
#   ✅ Audit Logs
```

---

## 🔄 Common Workflows

### New Customer Onboarding

```bash
# 1. Create tenant
python enterprise-admin.py tenant create "New Company Inc" --tier professional --trial-days 30

# 2. Setup subscription
TENANT_ID="<tenant-id-from-step-1>"
python enterprise-admin.py billing subscribe $TENANT_ID professional --cycle yearly

# 3. Configure white-label (Enterprise tier only)
python enterprise-admin.py whitelabel setup $TENANT_ID "New Company Docs" \
  --domain docs.newcompany.com

# 4. Verify setup
python enterprise-admin.py tenant info $TENANT_ID
python enterprise-admin.py portal dashboard $TENANT_ID
```

### Monthly Billing Run

```bash
# 1. Generate all invoices
python enterprise-admin.py tenant list | while read TENANT_ID; do
  python enterprise-admin.py billing invoice $TENANT_ID
done

# 2. Check for overdue payments
python enterprise-admin.py billing summary --status overdue

# 3. Send reminder emails
# (automated via cron job)
```

### System Health Monitoring

```bash
# Morning health check routine
python enterprise-admin.py monitoring health
python enterprise-admin.py monitoring alerts
python enterprise-admin.py scaling status

# Check for anomalies
python enterprise-admin.py monitoring metrics | grep "Error Rate"
```

### Scale-Up Operations

```bash
# 1. Check current load
python enterprise-admin.py scaling status

# 2. Add new instance
python enterprise-admin.py scaling register api-server api-7 new-host.internal 8000

# 3. Verify load distribution
python enterprise-admin.py scaling status
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Tenant creation fails"

```bash
# Check database connectivity
python enterprise-admin.py monitoring health

# View recent errors
tail -f logs/enterprise-admin.log
```

**Solution:**
- Verify database is running
- Check disk space
- Review error logs

#### Issue: "White-label domain not working"

```bash
# Check DNS configuration
dig app.acmecorp.com CNAME

# Verify SSL certificate
python enterprise-admin.py whitelabel status tenant_abc123
```

**Solution:**
- Verify CNAME record is configured
- Wait for SSL certificate generation (5-10 minutes)
- Check domain points to correct endpoint

#### Issue: "High error rate"

```bash
# Check metrics
python enterprise-admin.py monitoring metrics

# View active alerts
python enterprise-admin.py monitoring alerts

# Check service health
python enterprise-admin.py scaling status
```

**Solution:**
- Review error logs
- Check service instances
- Consider scaling up

---

## 🎯 Enterprise Best Practices

### Tenant Management

1. **Use tiers appropriately** - Match customer size to tier
2. **Trial periods** - 14-30 day trials for new customers
3. **Gradual migration** - Plan upgrades during low-usage periods
4. **Regular reviews** - Quarterly tenant usage reviews
5. **Cleanup inactive** - Remove or suspend unused tenants

### Billing & Revenue

1. **Automated invoicing** - Schedule monthly invoice generation
2. **Payment tracking** - Monitor overdue accounts weekly
3. **Usage alerts** - Notify customers before overage charges
4. **Annual incentives** - Offer discounts for yearly commitments
5. **Clear pricing** - Transparent pricing documentation

### Monitoring

1. **Proactive monitoring** - Check health daily
2. **Alert fatigue** - Tune alerts to reduce noise
3. **SLA tracking** - Monitor uptime and response times
4. **Capacity planning** - Review metrics monthly for trends
5. **Incident response** - Document and review incidents

### Scaling

1. **Auto-scaling** - Use auto-scaling for predictable loads
2. **Load testing** - Test before major customer launches
3. **Gradual rollout** - Deploy changes incrementally
4. **Redundancy** - Maintain at least 2 instances per service
5. **Health checks** - Configure health checks for all services

---

## 💡 Tips & Advanced Usage

### Automation Scripts

```bash
#!/bin/bash
# Daily enterprise operations script

echo "=== Daily Enterprise Operations ==="

# 1. Health check
echo "Running health checks..."
python enterprise-admin.py monitoring health > /tmp/health.log

# 2. Check alerts
echo "Checking alerts..."
python enterprise-admin.py monitoring alerts > /tmp/alerts.log

# 3. Generate metrics report
echo "Generating metrics..."
python enterprise-admin.py monitoring metrics > /tmp/metrics.log

# 4. Check for trial expiration
echo "Checking trials..."
python enterprise-admin.py tenant list --status trial --expiring-soon

# 5. Backup tenant data
echo "Creating backups..."
# (backup script here)

echo "✅ Daily operations complete"
```

### Monitoring Integration

```bash
# Export metrics to monitoring system (Prometheus format)
python enterprise-admin.py monitoring metrics --format prometheus > /var/lib/prometheus/textfile/dms.prom

# Send alerts to Slack
python enterprise-admin.py monitoring alerts --format json | \
  jq '.[] | select(.severity=="critical")' | \
  curl -X POST https://hooks.slack.com/... -d @-
```

### Bulk Operations

```bash
# Upgrade all starter tenants to professional
python enterprise-admin.py tenant list --tier starter | \
  while read TENANT_ID; do
    python enterprise-admin.py billing subscribe $TENANT_ID professional
  done

# Generate invoices for all active tenants
python enterprise-admin.py tenant list --status active | \
  while read TENANT_ID; do
    python enterprise-admin.py billing invoice $TENANT_ID
  done
```

---

## 🔗 Related Documentation

- [DMS Admin Guide](dms-admin.md) - Single-tenant administration
- [Enterprise Guide](../ENTERPRISE_GUIDE.md) - Enterprise features overview
- [Deployment Guide](../DEPLOYMENT_GUIDE.md) - Production deployment
- [Monitoring Guide](../GRAFANA_DASHBOARDS_GUIDE.md) - Grafana dashboards
- [Billing Guide](../BILLING_GUIDE.md) - Billing system documentation

---

## 📞 Support

### Getting Help

```bash
# General help
python enterprise-admin.py --help

# Command-specific help
python enterprise-admin.py tenant --help
python enterprise-admin.py billing --help
python enterprise-admin.py monitoring --help
```

### Enterprise Support

For enterprise customers:
- **Email:** enterprise-support@example.com
- **Phone:** +1-800-ENTERPRISE (24/7)
- **Slack:** #enterprise-support
- **Dedicated Success Manager:** Contact your CSM

---

**Last Updated:** 2026-01-18
**Version:** 3.0.0
**Status:** Production Ready
