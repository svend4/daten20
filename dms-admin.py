#!/usr/bin/env python3
"""
Document Management System - Administration CLI

Comprehensive command-line utility for system administration.
"""

import click
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


@click.group()
@click.version_option(version='2.2.0', prog_name='DMS Admin CLI')
def cli():
    """Document Management System - Administration CLI"""
    pass


# ==========================================
# USER MANAGEMENT
# ==========================================

@cli.group()
def users():
    """User management commands"""
    pass


@users.command('create')
@click.option('--username', prompt=True, help='Username')
@click.option('--email', prompt=True, help='Email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password')
@click.option('--role', type=click.Choice(['admin', 'manager', 'editor', 'viewer', 'guest']), default='viewer', help='User role')
def create_user(username, email, password, role):
    """Create a new user"""
    from src.core.auth import get_auth_manager, Role

    auth = get_auth_manager()
    user = auth.create_user(username, email, password, Role(role))

    if user:
        click.echo(f"✓ User created successfully: {username} ({role})")
    else:
        click.echo(f"✗ Failed to create user (username or email already exists)", err=True)
        sys.exit(1)


@users.command('list')
def list_users():
    """List all users"""
    from src.core.auth import get_auth_manager
    import sqlite3

    conn = sqlite3.connect('data/db/users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT id, username, email, role, is_active FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()

    if not users:
        click.echo("No users found")
        return

    click.echo(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<10} {'Active':<6}")
    click.echo("-" * 75)

    for user in users:
        active = "Yes" if user['is_active'] else "No"
        click.echo(f"{user['id']:<5} {user['username']:<20} {user['email']:<30} {user['role']:<10} {active:<6}")

    click.echo(f"\nTotal users: {len(users)}\n")


@users.command('enable-2fa')
@click.argument('user_id', type=int)
def enable_2fa(user_id):
    """Enable 2FA for a user and show QR code"""
    from src.core.two_factor import get_two_factor_auth
    from src.core.auth import get_auth_manager

    auth = get_auth_manager()
    user = auth.load_user(user_id)

    if not user:
        click.echo(f"✗ User not found: {user_id}", err=True)
        sys.exit(1)

    tfa = get_two_factor_auth()

    # Generate secret and QR code
    secret = tfa.generate_secret(user_id, user.username)
    uri = tfa.get_provisioning_uri(user_id, user.username)

    click.echo(f"\n2FA Setup for user: {user.username}")
    click.echo(f"Secret: {secret}")
    click.echo(f"\nScan this URL with Google Authenticator:")
    click.echo(uri)
    click.echo(f"\nOr visit /admin/users/{user_id}/2fa in the web interface to see QR code\n")


# ==========================================
# BACKUP MANAGEMENT
# ==========================================

@cli.group()
def backup():
    """Backup management commands"""
    pass


@backup.command('create')
@click.option('--include-files', is_flag=True, default=True, help='Include uploaded files')
def create_backup(include_files):
    """Create a new backup"""
    from src.core.backup import get_backup_manager

    click.echo("Creating backup...")

    mgr = get_backup_manager()
    backup_path = mgr.create_backup(include_files=include_files)

    click.echo(f"✓ Backup created: {backup_path}")


@backup.command('list')
@click.option('--limit', default=10, help='Number of backups to show')
def list_backups(limit):
    """List available backups"""
    from src.core.backup import get_backup_manager

    mgr = get_backup_manager()
    backups = mgr.list_backups()[:limit]

    if not backups:
        click.echo("No backups found")
        return

    click.echo(f"\n{'Name':<40} {'Size':<12} {'Created':<20}")
    click.echo("-" * 75)

    for backup in backups:
        click.echo(f"{backup['name']:<40} {backup['size']:<12} {backup['created'][:19]}")

    click.echo(f"\nShowing {len(backups)} of {len(mgr.list_backups())} backups\n")


@backup.command('restore')
@click.argument('backup_path')
@click.confirmation_option(prompt='Are you sure you want to restore? This will overwrite current data!')
def restore_backup(backup_path):
    """Restore from a backup"""
    from src.core.backup import get_backup_manager

    click.echo(f"Restoring from: {backup_path}...")

    mgr = get_backup_manager()
    try:
        mgr.restore_backup(backup_path)
        click.echo("✓ Backup restored successfully")
    except Exception as e:
        click.echo(f"✗ Restore failed: {e}", err=True)
        sys.exit(1)


# ==========================================
# AUDIT LOG
# ==========================================

@cli.group()
def audit():
    """Audit log commands"""
    pass


@audit.command('view')
@click.option('--user-id', type=int, help='Filter by user ID')
@click.option('--action', help='Filter by action')
@click.option('--limit', default=50, help='Number of entries to show')
def view_audit(user_id, action, limit):
    """View audit log entries"""
    from src.core.audit import get_audit_logger

    auditor = get_audit_logger()
    entries = auditor.get_entries(
        user_id=user_id,
        action=action,
        limit=limit
    )

    if not entries:
        click.echo("No audit entries found")
        return

    click.echo(f"\n{'Timestamp':<20} {'User':<15} {'Action':<30} {'Status':<10}")
    click.echo("-" * 80)

    for entry in entries:
        timestamp = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        user = entry.username or 'system'
        click.echo(f"{timestamp:<20} {user:<15} {entry.action:<30} {entry.status:<10}")

    click.echo(f"\nShowing {len(entries)} entries\n")


@audit.command('stats')
@click.option('--days', default=7, help='Number of days to analyze')
def audit_stats(days):
    """View audit statistics"""
    from src.core.audit import get_audit_logger

    auditor = get_audit_logger()
    stats = auditor.get_statistics(days=days)

    click.echo(f"\nAudit Statistics (last {days} days)")
    click.echo("=" * 50)
    click.echo(f"Total entries: {stats['total_entries']}")
    click.echo(f"Failed operations: {stats['failed_operations']}")

    click.echo(f"\nBy severity level:")
    for level, count in stats['by_level'].items():
        click.echo(f"  {level}: {count}")

    click.echo(f"\nTop 10 actions:")
    for action, count in list(stats['top_actions'].items())[:10]:
        click.echo(f"  {action}: {count}")

    click.echo()


# ==========================================
# SYSTEM STATUS
# ==========================================

@cli.group()
def system():
    """System management commands"""
    pass


@system.command('status')
def system_status():
    """Show system status"""
    import psutil
    from src.core.database import Database

    click.echo("\nSystem Status")
    click.echo("=" * 50)

    # System metrics
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    click.echo(f"\nSystem Resources:")
    click.echo(f"  CPU Usage: {cpu}%")
    click.echo(f"  Memory: {memory.percent}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)")
    click.echo(f"  Disk: {disk.percent}% ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)")

    # Database stats
    try:
        db = Database()
        services = db.list_services()
        click.echo(f"\nDatabase:")
        click.echo(f"  Total services: {len(services)}")
    except Exception as e:
        click.echo(f"\nDatabase: Error - {e}")

    click.echo()


@system.command('check')
def system_check():
    """Run system health checks"""
    checks = []

    # Check database
    try:
        from src.core.database import Database
        db = Database()
        db.list_services()
        checks.append(("Database connection", True, "OK"))
    except Exception as e:
        checks.append(("Database connection", False, str(e)))

    # Check directories
    required_dirs = ['data', 'data/db', 'data/exports', 'logs']
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        checks.append((f"Directory: {dir_path}", exists, "Exists" if exists else "Missing"))

    # Check config
    env_exists = Path('.env').exists()
    checks.append(("Configuration file (.env)", env_exists, "Present" if env_exists else "Missing"))

    # Display results
    click.echo("\nSystem Health Check")
    click.echo("=" * 60)

    for check_name, passed, message in checks:
        status = "✓" if passed else "✗"
        click.echo(f"{status} {check_name:<40} {message}")

    click.echo()

    # Summary
    passed_count = sum(1 for _, passed, _ in checks if passed)
    total_count = len(checks)

    if passed_count == total_count:
        click.echo(f"All checks passed ({passed_count}/{total_count})")
    else:
        click.echo(f"Some checks failed ({passed_count}/{total_count})", err=True)
        sys.exit(1)


# ==========================================
# DATABASE MANAGEMENT
# ==========================================

@cli.group()
def database():
    """Database management commands"""
    pass


@database.command('stats')
def db_stats():
    """Show database statistics"""
    from src.core.database import Database

    db = Database()
    services = db.list_services()

    if not services:
        click.echo("No services in database")
        return

    # Calculate stats
    total = len(services)
    avg_rate = sum(s.financial.brutto_rate for s in services) / total

    # By region
    by_region = {}
    for s in services:
        region = s.basic_info.region
        by_region[region] = by_region.get(region, 0) + 1

    click.echo("\nDatabase Statistics")
    click.echo("=" * 50)
    click.echo(f"Total services: {total}")
    click.echo(f"Average rate: €{avg_rate:.2f}/hour")

    click.echo(f"\nServices by region:")
    for region, count in sorted(by_region.items(), key=lambda x: x[1], reverse=True):
        click.echo(f"  {region}: {count}")

    click.echo()


if __name__ == '__main__':
    cli()
