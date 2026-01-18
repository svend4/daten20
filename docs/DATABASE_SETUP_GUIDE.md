# Database Setup Guide

## Multi-Database Support

The Document Management System now supports multiple database backends:

- **SQLite** - Default, file-based database (good for development)
- **PostgreSQL** - Production-grade relational database (recommended for production)
- **MySQL/MariaDB** - Alternative production database

## Quick Start

### SQLite (Default)

No configuration needed! The system automatically creates a SQLite database at:
```
data/db/services.db
```

### PostgreSQL Setup

#### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download installer from: https://www.postgresql.org/download/windows/

#### 2. Create Database and User

```bash
# Login as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE dms;
CREATE USER dms_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE dms TO dms_user;

# Exit psql
\q
```

#### 3. Configure Application

Set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://dms_user:your_secure_password@localhost/dms"
```

Or add to `.env` file:
```ini
DATABASE_URL=postgresql://dms_user:your_secure_password@localhost/dms
```

#### 4. Test Connection

```python
from src.core.database_universal import UniversalDatabase

db = UniversalDatabase(database_url="postgresql://dms_user:password@localhost/dms")
print(db.health_check())
```

### MySQL/MariaDB Setup

#### 1. Install MySQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

#### 2. Create Database and User

```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE dms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON dms.* TO 'dms_user'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

#### 3. Configure Application

```bash
export DATABASE_URL="mysql+pymysql://dms_user:your_secure_password@localhost/dms"
```

Or add to `.env` file:
```ini
DATABASE_URL=mysql+pymysql://dms_user:your_secure_password@localhost/dms
```

## Database URL Format

### General Format
```
dialect+driver://username:password@host:port/database
```

### Examples

**SQLite:**
```
sqlite:///path/to/database.db
sqlite:////absolute/path/to/database.db
```

**PostgreSQL:**
```
postgresql://user:password@localhost/dbname
postgresql://user:password@localhost:5432/dbname
postgresql+psycopg2://user:password@localhost/dbname
```

**MySQL:**
```
mysql+pymysql://user:password@localhost/dbname
mysql+pymysql://user:password@localhost:3306/dbname
```

**Remote Database:**
```
postgresql://user:password@db.example.com:5432/dbname
mysql+pymysql://user:password@db.example.com:3306/dbname
```

## Migration from SQLite to PostgreSQL/MySQL

Use the migration tool to transfer data:

```bash
# Migrate from SQLite to PostgreSQL
python tools/database_migration_tool.py \
    --source sqlite:///data/db/services.db \
    --target postgresql://user:password@localhost/dms \
    --verify

# Migrate from SQLite to MySQL
python tools/database_migration_tool.py \
    --source sqlite:///data/db/services.db \
    --target mysql+pymysql://user:password@localhost/dms \
    --verify
```

### Migration Steps

1. **Backup your SQLite database:**
   ```bash
   cp data/db/services.db data/db/services.db.backup
   ```

2. **Set up target database** (PostgreSQL or MySQL)

3. **Run migration:**
   ```bash
   python tools/database_migration_tool.py \
       --source sqlite:///data/db/services.db \
       --target postgresql://user:password@localhost/dms \
       --batch-size 100 \
       --verify
   ```

4. **Update .env file** with new DATABASE_URL

5. **Test the application**

## Connection Pooling

The UniversalDatabase class automatically configures connection pooling:

```python
db = UniversalDatabase(
    database_url="postgresql://user:password@localhost/dms",
    pool_size=5,           # Number of connections to maintain
    max_overflow=10,       # Maximum additional connections
    pool_timeout=30        # Connection timeout in seconds
)
```

### Recommended Pool Settings

**Development:**
- pool_size: 2-5
- max_overflow: 5-10

**Production:**
- pool_size: 10-20
- max_overflow: 20-30

**High-Traffic:**
- pool_size: 20-50
- max_overflow: 50-100

## Performance Tuning

### PostgreSQL

**postgresql.conf:**
```ini
# Increase shared buffers for better performance
shared_buffers = 256MB

# Increase work memory
work_mem = 16MB

# Increase maintenance work memory
maintenance_work_mem = 128MB

# Optimize for SSD
random_page_cost = 1.1

# Enable JIT compilation (PostgreSQL 11+)
jit = on
```

**Create indexes:**
```sql
-- Already created automatically, but you can add custom indexes
CREATE INDEX idx_services_created_at ON services(created_at);
CREATE INDEX idx_services_name_trgm ON services USING gin(name gin_trgm_ops);
```

### MySQL

**my.cnf:**
```ini
[mysqld]
# InnoDB buffer pool size (70-80% of RAM for dedicated server)
innodb_buffer_pool_size = 1G

# InnoDB log file size
innodb_log_file_size = 256M

# Query cache (if using MySQL < 8.0)
query_cache_size = 64M
query_cache_type = 1

# Max connections
max_connections = 200
```

## Backup and Recovery

### PostgreSQL

**Backup:**
```bash
# Full backup
pg_dump -U dms_user -d dms -F c -b -v -f dms_backup.dump

# Schema only
pg_dump -U dms_user -d dms -s -f dms_schema.sql

# Data only
pg_dump -U dms_user -d dms -a -f dms_data.sql
```

**Restore:**
```bash
# Restore from custom format
pg_restore -U dms_user -d dms -v dms_backup.dump

# Restore from SQL
psql -U dms_user -d dms -f dms_backup.sql
```

### MySQL

**Backup:**
```bash
# Full backup
mysqldump -u dms_user -p dms > dms_backup.sql

# Compressed backup
mysqldump -u dms_user -p dms | gzip > dms_backup.sql.gz
```

**Restore:**
```bash
# Restore from SQL
mysql -u dms_user -p dms < dms_backup.sql

# Restore from compressed
gunzip < dms_backup.sql.gz | mysql -u dms_user -p dms
```

## Monitoring

### Health Check

```python
from src.core.database_universal import UniversalDatabase

db = UniversalDatabase()
status = db.health_check()
print(status)
# {'status': 'healthy', 'database_type': 'postgresql', 'url': 'postgresql://***@localhost/dms'}
```

### Statistics

```python
stats = db.get_statistics()
print(stats)
# {
#   'total_services': 150,
#   'by_region': {'EU': 100, 'US': 50},
#   'by_type': {'basic': 80, 'premium': 70},
#   'avg_brutto_rate': 45.50,
#   'database_type': 'postgresql'
# }
```

## Troubleshooting

### Connection Errors

**PostgreSQL:**
```
FATAL: password authentication failed for user "dms_user"
```
→ Check password in DATABASE_URL and PostgreSQL permissions

**MySQL:**
```
Access denied for user 'dms_user'@'localhost'
```
→ Verify user creation and GRANT permissions

### Performance Issues

**Slow queries:**
1. Check indexes: `EXPLAIN ANALYZE SELECT ...`
2. Monitor connection pool usage
3. Increase pool_size if needed

**Too many connections:**
```
FATAL: sorry, too many clients already
```
→ Increase max_connections in PostgreSQL config or reduce pool_size

### Migration Issues

**Duplicate key errors:**
```
IntegrityError: duplicate key value violates unique constraint
```
→ Target database may already contain data. Clear it first:
```sql
TRUNCATE TABLE services, financial_data, versions, subscriptions CASCADE;
```

## Security Best Practices

1. **Use strong passwords** for database users
2. **Enable SSL/TLS** for remote connections:
   ```
   postgresql://user:pass@host/db?sslmode=require
   mysql+pymysql://user:pass@host/db?ssl=true
   ```
3. **Restrict database access** to application host only
4. **Regular backups** - automated daily backups
5. **Monitor access logs** for suspicious activity
6. **Use read-only users** for reporting/analytics

## Environment-Specific Configuration

### Development (.env.dev)
```ini
DATABASE_URL=sqlite:///data/db/services_dev.db
```

### Staging (.env.staging)
```ini
DATABASE_URL=postgresql://dms_user:secure_password@staging-db.local/dms
```

### Production (.env.prod)
```ini
DATABASE_URL=postgresql://dms_user:very_secure_password@prod-db.local:5432/dms?sslmode=require
```

Load environment-specific config:
```bash
cp .env.prod .env
python app.py
```

## Support

For issues or questions:
- Check logs in `logs/app.log`
- Run health check: `db.health_check()`
- Verify connection: `psql -U dms_user -d dms` (PostgreSQL)
- Test migration tool with small dataset first

---

**Updated:** 2026-01-18
**Version:** 2.5.1
