# 📚 Database Migrations Guide
## Comprehensive Guide to Managing Database Schema Changes

**Document Version:** 1.0
**Created:** 2026-01-18
**Last Updated:** 2026-01-18
**Tool:** Alembic + Custom Migration System
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Migration System Architecture](#migration-system-architecture)
4. [Installation & Setup](#installation--setup)
5. [Creating Migrations](#creating-migrations)
6. [Applying Migrations](#applying-migrations)
7. [Rolling Back Migrations](#rolling-back-migrations)
8. [Advanced Usage](#advanced-usage)
9. [Best Practices](#best-practices)
10. [CI/CD Integration](#cicd-integration)
11. [Troubleshooting](#troubleshooting)
12. [API Reference](#api-reference)
13. [Examples](#examples)

---

## 🎯 Overview

### What are Database Migrations?

Database migrations are version-controlled changes to your database schema. They allow you to:

- **Track schema changes** over time
- **Apply changes consistently** across environments (development, staging, production)
- **Rollback changes** if something goes wrong
- **Collaborate** with team members without schema conflicts
- **Deploy safely** with automated schema updates

### Why Use Migrations?

❌ **Without migrations:**
```sql
-- Manual SQL scripts
-- No version tracking
-- No rollback capability
-- Hard to synchronize across environments
CREATE TABLE users (...);
ALTER TABLE users ADD COLUMN email VARCHAR(255);
```

✅ **With migrations:**
```python
# Version controlled
# Automatic tracking
# Easy rollback
# Consistent across environments
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255)))

def downgrade():
    op.drop_column('users', 'email')
```

### Dual Migration System

This project uses **two migration systems**:

1. **Alembic** (Primary) - Standard SQLAlchemy migration tool
   - Automatic schema detection
   - Industry standard
   - Rich feature set
   - Better for complex schemas

2. **Custom Migration System** (Legacy) - Project-specific migrations
   - Located in `src/core/migrations.py`
   - Simpler API
   - Integrated with existing codebase
   - Maintained for backward compatibility

**Recommendation:** Use **Alembic** for new migrations.

---

## 🚀 Quick Start

### 5-Minute Setup

```bash
# 1. Install dependencies
pip install alembic==1.13.1

# 2. Check migration status
./scripts/check_migrations.sh

# 3. Apply migrations
python scripts/migrate.py upgrade

# 4. Create a new migration
python scripts/migrate.py create "add_new_table"
```

### First Migration Workflow

```bash
# 1. Make changes to models in src/core/db_models.py
vim src/core/db_models.py

# 2. Generate migration automatically
alembic revision --autogenerate -m "add email to users"

# 3. Review generated migration
cat alembic/versions/20260118_1200_abc123_add_email_to_users.py

# 4. Apply migration
alembic upgrade head

# 5. Verify
alembic current
```

---

## 🏗️ Migration System Architecture

### Directory Structure

```
daten20/
├── alembic/                    # Alembic migrations directory
│   ├── versions/              # Migration scripts
│   │   └── 20260118_0949_c1d2a2b4eb3a_initial_database_schema.py
│   ├── env.py                 # Alembic environment configuration
│   ├── README                 # Alembic readme
│   └── script.py.mako        # Migration template
├── alembic.ini                # Alembic configuration
├── src/
│   └── core/
│       ├── db_models.py      # SQLAlchemy ORM models
│       ├── database.py       # Database manager
│       └── migrations.py     # Custom migration system (legacy)
├── scripts/
│   ├── migrate.py            # Migration management CLI
│   └── check_migrations.sh   # Migration status checker
└── docs/
    └── DATABASE_MIGRATIONS_GUIDE.md  # This file
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Developer Workflow                        │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Modify Models in src/core/db_models.py                  │
│     - Add/remove columns                                    │
│     - Add/remove tables                                     │
│     - Add/remove indexes                                    │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Generate Migration (Alembic Autogenerate)               │
│     $ alembic revision --autogenerate -m "description"      │
│     - Compares models with current database                 │
│     - Generates migration script                            │
│     - Creates upgrade() and downgrade() functions           │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Review Generated Migration                              │
│     - Check upgrade() function                              │
│     - Check downgrade() function                            │
│     - Add manual changes if needed                          │
│     - Verify SQL operations                                 │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Apply Migration                                         │
│     $ alembic upgrade head                                  │
│     - Connects to database                                  │
│     - Runs upgrade() function                               │
│     - Updates alembic_version table                         │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Verify & Commit                                         │
│     $ alembic current                                       │
│     $ git add alembic/versions/                             │
│     $ git commit -m "Add migration for..."                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Setup

### Prerequisites

```bash
# Python 3.9+
python --version

# SQLAlchemy 2.0+
pip list | grep SQLAlchemy

# Alembic 1.13+
pip list | grep alembic
```

### Install Alembic

```bash
# Install via pip
pip install alembic==1.13.1

# Or add to requirements.txt
echo "alembic==1.13.1" >> requirements.txt
pip install -r requirements.txt

# Verify installation
alembic --version
```

### Initialize Alembic (Already Done)

This project is already initialized. If you need to initialize from scratch:

```bash
# Initialize Alembic (creates alembic/ directory)
alembic init alembic

# Configure alembic.ini
vim alembic.ini
# Set: sqlalchemy.url = sqlite:///data/dms.db

# Configure env.py to import models
vim alembic/env.py
# Add: from src.core.db_models import Base
# Set: target_metadata = Base.metadata
```

### Configuration Files

#### alembic.ini

```ini
[alembic]
# Path to migration scripts
script_location = alembic

# Migration file naming template (with timestamp)
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Database URL (can be overridden by environment variable)
sqlalchemy.url = sqlite:///data/dms.db

[post_write_hooks]
# Auto-format migrations with Black
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 120 REVISION_SCRIPT_FILENAME
```

#### alembic/env.py

```python
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models for autogenerate
from src.core.db_models import Base

config = context.config
target_metadata = Base.metadata

# Support environment variable override
if os.getenv("SQLALCHEMY_DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("SQLALCHEMY_DATABASE_URL"))

# ... (rest of configuration)
```

---

## ✏️ Creating Migrations

### Automatic Migration Generation (Recommended)

Alembic can automatically detect schema changes by comparing your models with the current database.

```bash
# 1. Modify models in src/core/db_models.py
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    # Add new field
    phone = Column(String, nullable=True)

# 2. Generate migration automatically
alembic revision --autogenerate -m "add phone to users"

# Output:
# Generating /path/to/alembic/versions/20260118_1200_abc123_add_phone_to_users.py ... done

# 3. Review generated migration
cat alembic/versions/20260118_1200_abc123_add_phone_to_users.py
```

### Manual Migration Creation

For complex changes that autogenerate can't detect:

```bash
# Create empty migration
alembic revision -m "custom_complex_migration"

# Edit the generated file manually
vim alembic/versions/20260118_1200_xyz789_custom_complex_migration.py
```

Example manual migration:

```python
"""custom complex migration

Revision ID: xyz789
Revises: abc123
Create Date: 2026-01-18 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xyz789'
down_revision = 'abc123'

def upgrade() -> None:
    # Add column
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))

    # Create index
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # Execute raw SQL
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    # Make column non-nullable
    op.alter_column('users', 'created_at', nullable=False)

def downgrade() -> None:
    op.drop_index('ix_users_created_at', 'users')
    op.drop_column('users', 'created_at')
```

### Using Helper Scripts

```bash
# Create migration with helper script
python scripts/migrate.py create "add new field"

# With auto-detection
python scripts/migrate.py create "add new field" --autogenerate

# Without auto-detection
python scripts/migrate.py create "add new field" --no-autogenerate
```

---

## ⬆️ Applying Migrations

### Upgrade to Latest Version

```bash
# Upgrade to latest (head)
alembic upgrade head

# Or using helper script
python scripts/migrate.py upgrade

# Output:
# INFO  [alembic.runtime.migration] Running upgrade -> abc123, add phone to users
# INFO  [alembic.runtime.migration] Running upgrade abc123 -> xyz789, custom complex migration
```

### Upgrade to Specific Version

```bash
# Upgrade to specific revision
alembic upgrade abc123

# Upgrade one step
alembic upgrade +1

# Upgrade two steps
alembic upgrade +2
```

### Check Current Version

```bash
# Show current version
alembic current

# Output:
# abc123 (head)

# Or using helper script
python scripts/migrate.py status
```

### Show Migration History

```bash
# Show all migrations
alembic history

# Show recent migrations
alembic history | head -20

# Show with verbose details
alembic history -v

# Or using helper script
python scripts/migrate.py history
python scripts/migrate.py history --verbose
```

---

## ⬇️ Rolling Back Migrations

### Downgrade Operations

```bash
# Downgrade one step
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Downgrade to base (empty database)
alembic downgrade base

# Or using helper script
python scripts/migrate.py downgrade
python scripts/migrate.py downgrade -1
python scripts/migrate.py downgrade abc123
```

### Safety Considerations

⚠️ **Warning:** Downgrading can result in data loss!

- Always backup before downgrading
- Test downgrades in development first
- Some operations are not reversible (e.g., dropping tables with data)
- Review the `downgrade()` function before executing

```bash
# Backup database before downgrade
cp data/dms.db data/dms.db.backup.$(date +%Y%m%d_%H%M%S)

# Then downgrade
alembic downgrade -1

# If something goes wrong, restore
mv data/dms.db.backup.20260118_120000 data/dms.db
```

---

## 🔧 Advanced Usage

### Working with Branches

Alembic supports branching for parallel development:

```bash
# Create branch from specific revision
alembic revision -m "feature A" --head=abc123 --branch-label=feature_a

# Merge branches
alembic merge -m "merge feature_a into main" heads

# Show current heads
alembic heads
```

### Stamping Database

Set database version without running migrations:

```bash
# Stamp to current head (useful for existing databases)
alembic stamp head

# Stamp to specific version
alembic stamp abc123

# Or using helper script
python scripts/migrate.py stamp
python scripts/migrate.py stamp abc123
```

### Environment Variable Configuration

Override database URL via environment variable:

```bash
# Development database
export SQLALCHEMY_DATABASE_URL="sqlite:///data/dev.db"
alembic upgrade head

# Production database
export SQLALCHEMY_DATABASE_URL="postgresql://user:pass@localhost/proddb"
alembic upgrade head

# Test database
export SQLALCHEMY_DATABASE_URL="sqlite:///:memory:"
alembic upgrade head
```

### Generating SQL Without Execution

Preview SQL that will be executed:

```bash
# Generate SQL for upgrade
alembic upgrade head --sql > upgrade.sql

# Review SQL
cat upgrade.sql

# Apply manually if needed
sqlite3 data/dms.db < upgrade.sql
```

### Offline Migrations

Generate migrations without database connection:

```bash
# Generate upgrade SQL offline
alembic upgrade head --sql --offline > migrations.sql

# Apply on production server
scp migrations.sql production:/tmp/
ssh production "sqlite3 /var/lib/dms/dms.db < /tmp/migrations.sql"
```

---

## 💡 Best Practices

### 1. Always Review Autogenerated Migrations

Alembic's autogenerate is smart but not perfect:

```python
# Example: Autogenerate might miss this
# Manually add data migration
def upgrade() -> None:
    # Generated
    op.add_column('users', sa.Column('status', sa.String(), nullable=True))

    # Add manually: Set default for existing rows
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")

    # Make non-nullable
    op.alter_column('users', 'status', nullable=False)
```

### 2. Write Reversible Migrations

Always implement `downgrade()`:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('deleted_at', sa.DateTime()))

def downgrade() -> None:
    op.drop_column('users', 'deleted_at')
```

### 3. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Verify
alembic current

# Test downgrade
alembic downgrade -1

# Upgrade again
alembic upgrade head
```

### 4. Version Control Migrations

```bash
# Always commit migrations
git add alembic/versions/
git commit -m "Add migration: add phone to users"

# Never edit committed migrations
# Create a new migration instead
```

### 5. Use Descriptive Names

```bash
# Good ✅
alembic revision --autogenerate -m "add_email_verification_fields"
alembic revision --autogenerate -m "create_audit_log_table"

# Bad ❌
alembic revision --autogenerate -m "update"
alembic revision --autogenerate -m "fix"
```

### 6. Handle Data Migrations Carefully

```python
# Good ✅
def upgrade() -> None:
    # Add nullable first
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

    # Populate data
    op.execute("""
        UPDATE users
        SET full_name = first_name || ' ' || last_name
        WHERE full_name IS NULL
    """)

    # Make non-nullable
    op.alter_column('users', 'full_name', nullable=False)

# Bad ❌
def upgrade() -> None:
    # This will fail if table has existing rows
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=False))
```

### 7. Backup Before Production Migrations

```bash
# Production migration checklist
1. Backup database
2. Test migration in staging
3. Announce maintenance window
4. Apply migration
5. Verify application works
6. Monitor for issues
```

---

## 🔄 CI/CD Integration

### GitHub Actions

Add to `.github/workflows/migrations.yml`:

```yaml
name: Database Migrations

on:
  pull_request:
    paths:
      - 'alembic/versions/**'
      - 'src/core/db_models.py'

jobs:
  check-migrations:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Check migration status
      run: |
        ./scripts/check_migrations.sh

    - name: Test upgrade
      run: |
        alembic upgrade head

    - name: Test downgrade
      run: |
        alembic downgrade -1

    - name: Test re-upgrade
      run: |
        alembic upgrade head
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for pending model changes without migration

# Check if db_models.py changed
if git diff --cached --name-only | grep -q "src/core/db_models.py"; then
    echo "⚠️  db_models.py changed. Did you create a migration?"
    echo "Run: alembic revision --autogenerate -m 'description'"

    # Optional: Block commit
    # exit 1
fi
```

### Deployment Scripts

```bash
# deploy.sh
#!/bin/bash
set -e

echo "Deploying application..."

# 1. Backup database
./scripts/backup_database.sh

# 2. Run migrations
alembic upgrade head

# 3. Restart application
systemctl restart dms-app

# 4. Verify
./scripts/check_migrations.sh

echo "Deployment complete!"
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: "Target database is not up to date"

```bash
# Error
ERROR [alembic.runtime.migration] Target database is not up to date.

# Solution
alembic upgrade head
```

#### Issue 2: "Can't locate revision identified by 'abc123'"

```bash
# Error
FAILED: Can't locate revision identified by 'abc123'

# Solution: Revision doesn't exist in versions/
# Check available revisions
alembic history

# Stamp to a valid revision or head
alembic stamp head
```

#### Issue 3: "Multiple head revisions are present"

```bash
# Error
ERROR [alembic.runtime.migration] Multiple head revisions are present

# Solution: Merge heads
alembic merge -m "merge heads" heads
alembic upgrade head
```

#### Issue 4: "FAILED: Could not find entrypoint console_scripts.black"

```bash
# Error during migration creation
FAILED: Could not find entrypoint console_scripts.black

# Solution: Install black
pip install black

# Or disable black hook in alembic.ini
# Comment out: hooks = black
```

#### Issue 5: Migration fails midway

```bash
# Error
ERROR [alembic.runtime.migration] Error during upgrade

# Solution: Rollback and fix
alembic downgrade -1

# Edit migration file
vim alembic/versions/problem_migration.py

# Try again
alembic upgrade head
```

### Debug Mode

```bash
# Enable verbose logging
alembic --log-level DEBUG upgrade head

# Or in alembic.ini
[logger_alembic]
level = DEBUG
```

### Manual Intervention

```bash
# Connect to database
sqlite3 data/dms.db

# Check current version
SELECT * FROM alembic_version;

# Manually update version (use with caution!)
UPDATE alembic_version SET version_num = 'abc123';
.quit

# Verify
alembic current
```

---

## 📚 API Reference

### Alembic Commands

| Command | Description | Example |
|---------|-------------|---------|
| `upgrade` | Upgrade to a later version | `alembic upgrade head` |
| `downgrade` | Revert to a previous version | `alembic downgrade -1` |
| `current` | Display current revision | `alembic current` |
| `history` | List changeset history | `alembic history` |
| `heads` | Show current available heads | `alembic heads` |
| `revision` | Create a new revision | `alembic revision -m "msg"` |
| `stamp` | Set version without migration | `alembic stamp head` |
| `merge` | Merge two revisions together | `alembic merge heads` |

### Helper Script Commands

```bash
# scripts/migrate.py
python scripts/migrate.py upgrade [target]      # Upgrade database
python scripts/migrate.py downgrade [target]    # Downgrade database
python scripts/migrate.py status                # Show current status
python scripts/migrate.py history [--verbose]   # Show history
python scripts/migrate.py create "description"  # Create migration
python scripts/migrate.py heads                 # Show heads
python scripts/migrate.py stamp [revision]      # Stamp version

# scripts/check_migrations.sh
./scripts/check_migrations.sh                   # Check migration status
```

### Migration Operations

Common operations in migration files:

```python
from alembic import op
import sqlalchemy as sa

# Tables
op.create_table('users', ...)
op.drop_table('users')
op.rename_table('old_name', 'new_name')

# Columns
op.add_column('users', sa.Column('email', sa.String()))
op.drop_column('users', 'email')
op.alter_column('users', 'email', new_column_name='email_address')
op.alter_column('users', 'email', nullable=False)

# Indexes
op.create_index('ix_users_email', 'users', ['email'])
op.drop_index('ix_users_email', 'users')

# Constraints
op.create_foreign_key('fk_users_tenant', 'users', 'tenants', ['tenant_id'], ['id'])
op.drop_constraint('fk_users_tenant', 'users', type_='foreignkey')

# Raw SQL
op.execute("UPDATE users SET status = 'active'")

# Batch operations (for SQLite)
with op.batch_alter_table('users') as batch_op:
    batch_op.add_column(sa.Column('phone', sa.String()))
    batch_op.create_index('ix_users_phone', ['phone'])
```

---

## 📝 Examples

### Example 1: Add Column

```python
"""add email verification fields

Revision ID: def456
Revises: abc123
Create Date: 2026-01-18
"""

from alembic import op
import sqlalchemy as sa

revision = 'def456'
down_revision = 'abc123'

def upgrade() -> None:
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('verification_token', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('verified_at', sa.DateTime(), nullable=True))

    # Create index
    op.create_index('ix_users_email_verified', 'users', ['email_verified'])

def downgrade() -> None:
    op.drop_index('ix_users_email_verified', 'users')
    op.drop_column('users', 'verified_at')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'email_verified')
```

### Example 2: Create Table

```python
"""create audit log table

Revision ID: ghi789
Revises: def456
Create Date: 2026-01-18
"""

from alembic import op
import sqlalchemy as sa

revision = 'ghi789'
down_revision = 'def456'

def upgrade() -> None:
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('details_json', sa.Text(), default='{}'),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp()),
    )

    # Indexes
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # Foreign key
    op.create_foreign_key(
        'fk_audit_logs_user',
        'audit_logs', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    op.drop_constraint('fk_audit_logs_user', 'audit_logs', type_='foreignkey')
    op.drop_index('ix_audit_logs_created_at', 'audit_logs')
    op.drop_index('ix_audit_logs_action', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_table('audit_logs')
```

### Example 3: Data Migration

```python
"""migrate user roles to new format

Revision ID: jkl012
Revises: ghi789
Create Date: 2026-01-18
"""

from alembic import op
import sqlalchemy as sa

revision = 'jkl012'
down_revision = 'ghi789'

def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('role', sa.String(), nullable=True))

    # Migrate data from is_admin to role
    op.execute("""
        UPDATE users
        SET role = CASE
            WHEN is_admin = 1 THEN 'admin'
            ELSE 'user'
        END
    """)

    # Make non-nullable
    op.alter_column('users', 'role', nullable=False)

    # Drop old column
    op.drop_column('users', 'is_admin')

    # Create index
    op.create_index('ix_users_role', 'users', ['role'])

def downgrade() -> None:
    # Add back is_admin column
    op.add_column('users', sa.Column('is_admin', sa.Integer(), default=0))

    # Migrate data back
    op.execute("""
        UPDATE users
        SET is_admin = CASE
            WHEN role = 'admin' THEN 1
            ELSE 0
        END
    """)

    # Drop new column
    op.drop_index('ix_users_role', 'users')
    op.drop_column('users', 'role')
```

---

## 🎓 Learning Resources

### Official Documentation

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Migration Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

### Internal Resources

- `src/core/db_models.py` - ORM Models
- `src/core/database.py` - Database Manager
- `src/core/migrations.py` - Custom Migration System
- `scripts/migrate.py` - Migration CLI
- `scripts/check_migrations.sh` - Status Checker

---

## 📞 Support

### Getting Help

1. Check this guide
2. Run `./scripts/check_migrations.sh`
3. Check migration history: `alembic history`
4. Check Alembic docs: https://alembic.sqlalchemy.org/
5. Review migration files in `alembic/versions/`

### Reporting Issues

When reporting migration issues, include:

1. Output of `./scripts/check_migrations.sh`
2. Output of `alembic current`
3. Error message (full traceback)
4. Database type and version
5. Alembic version: `alembic --version`

---

## ✅ Checklist

### Before Creating Migration

- [ ] Models updated in `src/core/db_models.py`
- [ ] Changes tested locally
- [ ] Migration description is clear

### After Creating Migration

- [ ] Migration file reviewed
- [ ] `upgrade()` function is correct
- [ ] `downgrade()` function is correct
- [ ] Data migrations handled properly
- [ ] Migration tested (upgrade + downgrade)

### Before Deploying

- [ ] Backup database
- [ ] Test migration in staging
- [ ] Review migration one more time
- [ ] Plan rollback strategy
- [ ] Announce maintenance window (if needed)

---

**Document Status:** ✅ Complete
**Maintained By:** Development Team
**Last Review:** 2026-01-18
**Next Review:** 2026-04-18

---

## Quick Reference Card

```bash
# Common Commands
alembic upgrade head          # Apply all migrations
alembic downgrade -1          # Rollback one step
alembic current               # Show current version
alembic history               # Show all migrations
alembic revision --autogenerate -m "msg"  # Create migration

# Helper Scripts
./scripts/check_migrations.sh           # Check status
python scripts/migrate.py upgrade       # Upgrade
python scripts/migrate.py status        # Status
python scripts/migrate.py create "msg"  # Create

# Files to Know
alembic.ini                   # Configuration
alembic/env.py               # Environment setup
src/core/db_models.py        # ORM models
alembic/versions/            # Migration files
```

---

**End of Guide** 📚
