# 🔧 DMS-Admin User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** System administration and management for Document Management System

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Commands](#commands)
   - [User Management](#user-management)
   - [Database Management](#database-management)
   - [Backup Management](#backup-management)
   - [System Management](#system-management)
   - [Audit Management](#audit-management)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)
6. [Security Best Practices](#security-best-practices)
7. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Overview

**dms-admin.py** is the primary administration tool for the Document Management System. It provides comprehensive system management capabilities including user management, database operations, backups, and audit logging.

### Key Features

- ✅ **User Management** - Create, list, and manage users with 2FA support
- ✅ **Database Administration** - View statistics and manage database health
- ✅ **Backup & Restore** - Create, list, and restore system backups
- ✅ **System Monitoring** - Health checks and system status
- ✅ **Audit Logging** - View and analyze audit logs

### When to Use

| Task | Command |
|------|---------|
| Add new users | `dms-admin.py users create` |
| Check system health | `dms-admin.py system check` |
| Create backup | `dms-admin.py backup create` |
| View audit logs | `dms-admin.py audit view` |
| Database statistics | `dms-admin.py database stats` |

---

## ⚡ Quick Start

### Installation

```bash
# Ensure you have the DMS installed
cd /path/to/daten20

# Make executable (Unix/Linux/Mac)
chmod +x dms-admin.py

# Verify installation
python dms-admin.py --version
```

### First-Time Setup

```bash
# 1. Check system status
python dms-admin.py system status

# 2. Run health checks
python dms-admin.py system check

# 3. View database stats
python dms-admin.py database stats

# 4. Create first backup
python dms-admin.py backup create --description "Initial backup"
```

---

## 📚 Commands

### User Management

#### 1. Create User

Create a new user account with specified role.

```bash
# Basic user creation
python dms-admin.py users create

# Interactive prompts:
# - Username: admin
# - Email: admin@example.com
# - Password: ********
# - Role: admin/user/viewer
```

**Example Output:**
```
✅ User created successfully
Username: admin
Email: admin@example.com
Role: admin
User ID: usr_abc123
```

**Roles:**
- **admin** - Full system access
- **user** - Standard user access
- **viewer** - Read-only access

#### 2. List Users

Display all users in the system.

```bash
python dms-admin.py users list

# Output:
# ID          Username    Email                   Role    2FA    Created
# usr_001     admin       admin@example.com       admin   Yes    2026-01-01
# usr_002     john        john@example.com        user    No     2026-01-05
# usr_003     viewer      viewer@example.com      viewer  No     2026-01-10
```

**Options:**
- View active users only
- Filter by role
- Export to CSV

#### 3. Enable 2FA

Enable Two-Factor Authentication for a user.

```bash
python dms-admin.py users enable-2fa --username admin

# Displays:
# 1. QR code in terminal
# 2. Manual setup code
# 3. Backup codes (save these!)
```

**Process:**
1. Run command
2. Scan QR code with authenticator app (Google Authenticator, Authy)
3. Save backup codes securely
4. Test login with 2FA code

---

### Database Management

#### Database Statistics

View comprehensive database statistics and health metrics.

```bash
python dms-admin.py database stats

# Output:
# Database Statistics
# ━━━━━━━━━━━━━━━━━━━
# Total Documents: 1,234
# Total Users: 56
# Total Services: 23
# Database Size: 256 MB
# Index Size: 48 MB
# Table Count: 12
# Connection Pool: 8/20
# Oldest Record: 2025-01-01
# Newest Record: 2026-01-18
```

**Metrics Displayed:**
- Record counts by table
- Database and index sizes
- Connection pool status
- Temporal data (oldest/newest records)
- Performance indicators

---

### Backup Management

#### 1. Create Backup

Create a new system backup.

```bash
# Basic backup
python dms-admin.py backup create

# Backup with description
python dms-admin.py backup create --description "Before v2.0 upgrade"

# Output:
# Creating backup...
# ✅ Backup created successfully
# Backup ID: backup_20260118_143022
# Location: backups/backup_20260118_143022.tar.gz
# Size: 256 MB
# Duration: 12.3 seconds
```

**What's Backed Up:**
- Database (SQLite/PostgreSQL dump)
- Uploaded documents
- Configuration files
- User data
- Logs (optional)

#### 2. List Backups

Display all available backups.

```bash
python dms-admin.py backup list

# Output:
# Backups
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ID                        Date        Size    Description
# backup_20260118_143022    2026-01-18  256 MB  Before v2.0 upgrade
# backup_20260115_090000    2026-01-15  248 MB  Weekly backup
# backup_20260110_100000    2026-01-10  240 MB  Monthly backup
```

#### 3. Restore Backup

Restore system from a backup.

```bash
# Interactive restore
python dms-admin.py backup restore

# Restore specific backup
python dms-admin.py backup restore --backup-id backup_20260118_143022

# ⚠️ WARNING: This will overwrite current data!
# Confirm? [y/N]: y
#
# Restoring backup...
# ✅ Backup restored successfully
# Duration: 18.7 seconds
```

**Safety Features:**
- Confirmation required
- Pre-restore backup created automatically
- Validation checks
- Rollback on failure

---

### System Management

#### 1. System Status

View current system status and metrics.

```bash
python dms-admin.py system status

# Output:
# System Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Status: ✅ Healthy
# Uptime: 7 days, 14 hours
# CPU Usage: 23%
# Memory: 2.1 GB / 8 GB (26%)
# Disk: 45 GB / 500 GB (9%)
# Active Connections: 12
# Request Rate: 45 req/min
# Error Rate: 0.02%
```

**Indicators:**
- ✅ Green - All systems operational
- ⚠️ Yellow - Warning, attention needed
- ❌ Red - Critical issue, action required

#### 2. Health Checks

Run comprehensive system health checks.

```bash
python dms-admin.py system check

# Output:
# Running Health Checks...
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ Database connection
# ✅ File system access
# ✅ Cache service
# ✅ Email service
# ✅ External APIs
# ⚠️ Disk space (85% used - warning threshold)
# ✅ Memory usage
# ✅ CPU usage
#
# Overall Status: ⚠️ Warning (1 issue)
```

**Checks Performed:**
- Database connectivity
- File system permissions
- Cache service (Redis/Memcached)
- Email configuration
- External API connectivity
- Resource usage (disk, memory, CPU)
- Network connectivity
- SSL certificate validity

---

### Audit Management

#### 1. View Audit Logs

View detailed audit log entries.

```bash
# View recent logs
python dms-admin.py audit view

# View logs with filters
python dms-admin.py audit view --user admin --action login --days 7

# Output:
# Audit Log
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Date                User     Action           Resource        IP Address
# 2026-01-18 14:30   admin    login            -               192.168.1.10
# 2026-01-18 14:32   admin    create_user      usr_abc123      192.168.1.10
# 2026-01-18 14:35   admin    backup_create    backup_123      192.168.1.10
# 2026-01-18 14:40   john     upload_document  doc_456         192.168.1.20
```

**Filter Options:**
- By user
- By action type
- By date range
- By IP address
- By resource

#### 2. Audit Statistics

View audit log statistics and analytics.

```bash
python dms-admin.py audit stats

# Output:
# Audit Statistics (Last 30 Days)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Total Events: 1,234
# Unique Users: 23
# Most Active User: admin (456 events)
# Most Common Action: document_view (567)
# Failed Logins: 12
# Successful Logins: 234
#
# Top Actions:
# 1. document_view: 567
# 2. document_upload: 234
# 3. user_login: 234
# 4. document_download: 156
# 5. settings_update: 43
```

---

## 🔄 Common Workflows

### Daily Operations

```bash
# Morning routine
python dms-admin.py system status
python dms-admin.py system check
python dms-admin.py audit stats

# Check for issues
python dms-admin.py database stats
```

### Weekly Maintenance

```bash
# Create weekly backup
python dms-admin.py backup create --description "Weekly backup $(date +%Y-%m-%d)"

# Review audit logs
python dms-admin.py audit view --days 7

# Check system health
python dms-admin.py system check
```

### New User Onboarding

```bash
# 1. Create user account
python dms-admin.py users create

# 2. Enable 2FA for security
python dms-admin.py users enable-2fa --username newuser

# 3. Verify user creation
python dms-admin.py users list

# 4. Check audit log
python dms-admin.py audit view --action create_user --days 1
```

### Disaster Recovery

```bash
# 1. List available backups
python dms-admin.py backup list

# 2. Verify system status
python dms-admin.py system status

# 3. Restore from backup
python dms-admin.py backup restore --backup-id <backup_id>

# 4. Verify restoration
python dms-admin.py system check
python dms-admin.py database stats
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Database connection failed"

```bash
# Check database status
python dms-admin.py database stats

# Run health checks
python dms-admin.py system check

# Check configuration
cat .env | grep DATABASE
```

**Solution:**
- Verify database is running
- Check connection credentials in `.env`
- Ensure network connectivity

#### Issue: "Backup creation failed"

```bash
# Check disk space
python dms-admin.py system status

# Verify backup directory permissions
ls -la backups/
```

**Solution:**
- Free up disk space
- Check directory permissions
- Verify write access

#### Issue: "User creation fails"

```bash
# Check database
python dms-admin.py database stats

# View recent audit logs
python dms-admin.py audit view --action create_user
```

**Solution:**
- Check database connectivity
- Verify email uniqueness
- Review validation errors

---

## 🔐 Security Best Practices

### User Management

1. **Enable 2FA** for all admin accounts
2. **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
3. **Regular audits** - Review user list monthly
4. **Principle of least privilege** - Grant minimum necessary permissions
5. **Remove inactive users** - Disable unused accounts

### Backup Security

1. **Encrypt backups** - Use encryption for sensitive data
2. **Offsite storage** - Store backups in separate location
3. **Test restores** - Verify backups work monthly
4. **Retention policy** - Keep 30 days of daily, 12 months of monthly backups
5. **Access control** - Restrict backup access to admins only

### Audit Logging

1. **Regular reviews** - Check logs weekly
2. **Alert on anomalies** - Monitor for suspicious activity
3. **Retention** - Keep logs for 90+ days
4. **Secure storage** - Protect logs from tampering
5. **Compliance** - Ensure logs meet regulatory requirements

---

## 💡 Tips & Best Practices

### General

- **Automate backups** - Schedule daily automated backups
- **Monitor regularly** - Check system status daily
- **Document changes** - Use descriptive backup descriptions
- **Test restores** - Practice disaster recovery quarterly
- **Keep updated** - Update DMS regularly for security patches

### Performance

- **Database maintenance** - Run vacuum/optimize monthly
- **Log rotation** - Rotate logs to prevent disk fills
- **Monitor resources** - Set up alerts for resource thresholds
- **Clean old data** - Archive or delete old records

### Security

- **Regular audits** - Review security settings monthly
- **Update credentials** - Rotate admin passwords quarterly
- **Review access** - Audit user permissions monthly
- **Patch promptly** - Apply security updates immediately
- **Backup verification** - Test backup integrity weekly

---

## 📊 Advanced Usage

### Scripting & Automation

```bash
#!/bin/bash
# Daily backup script

DATE=$(date +%Y-%m-%d)
DESCRIPTION="Automated daily backup $DATE"

python dms-admin.py backup create --description "$DESCRIPTION"

# Check if backup succeeded
if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $DATE"
else
    echo "❌ Backup failed: $DATE"
    # Send alert email
fi
```

### Monitoring Integration

```bash
# Export metrics for monitoring
python dms-admin.py system status --format json > /tmp/dms_status.json
python dms-admin.py database stats --format json > /tmp/dms_db_stats.json
```

---

## 🔗 Related Documentation

- [Enterprise Admin Guide](enterprise-admin.md) - Multi-tenant administration
- [User Guide](USER_GUIDE.md) - General user documentation
- [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md) - Common issues and solutions
- [Deployment Guide](../DEPLOYMENT_GUIDE.md) - Production deployment
- [Security Guide](../SECURITY_ENHANCEMENTS_GUIDE.md) - Security best practices

---

## 📞 Support

### Getting Help

```bash
# General help
python dms-admin.py --help

# Command-specific help
python dms-admin.py users --help
python dms-admin.py backup --help

# Version information
python dms-admin.py --version
```

### Reporting Issues

If you encounter issues:
1. Run `python dms-admin.py system check`
2. Check logs in `logs/` directory
3. Review [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md)
4. Create issue on GitHub with error details

---

**Last Updated:** 2026-01-18
**Version:** 1.0.0
**Status:** Production Ready
