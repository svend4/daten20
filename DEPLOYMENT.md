# 🚀 Production Deployment Guide

Comprehensive guide for deploying the Document Management System to production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Web Server Setup](#web-server-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup and Recovery](#backup-and-recovery)
10. [Security Hardening](#security-hardening)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **RAM**: Minimum 2GB, Recommended 4GB+
- **CPU**: 2+ cores recommended
- **Disk**: 10GB+ free space
- **Network**: Ports 80, 443, 5000 accessible

### Software Requirements

```bash
# Docker deployment
- Docker 20.10+
- Docker Compose 2.0+

# Manual deployment
- Python 3.11+
- Nginx 1.18+
- Supervisor (optional, for process management)
```

---

## Quick Start with Docker

### Option 1: Basic Docker Deployment

```bash
# 1. Clone repository
git clone <repository-url>
cd daten20

# 2. Create environment file
cp .env.example .env

# 3. Edit environment variables
nano .env  # Set SECRET_KEY and other variables

# 4. Build and start
docker-compose up -d

# 5. Check status
docker-compose ps
docker-compose logs -f web
```

Application will be available at `http://localhost:5000`

### Option 2: Production with Nginx and Redis

```bash
# Start with all production services
docker-compose --profile with-redis --profile with-nginx up -d

# View logs
docker-compose logs -f
```

Application will be available at `http://localhost` (port 80)

### Docker Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Access container shell
docker-compose exec web bash

# View resource usage
docker stats
```

---

## Manual Installation

### Step 1: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
                    nginx supervisor git curl

# CentOS/RHEL
sudo dnf install -y python3.11 python3-pip nginx supervisor git curl
```

### Step 2: Create Application User

```bash
# Create dedicated user for security
sudo useradd -m -s /bin/bash dms
sudo su - dms
```

### Step 3: Clone and Setup Application

```bash
# Clone repository
git clone <repository-url> /home/dms/app
cd /home/dms/app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/db data/exports data/templates logs

# Set permissions
chmod 750 data logs
```

### Step 4: Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy the output to SECRET_KEY in .env
```

### Step 5: Initialize Database

```bash
# Run database migrations (if using Alembic)
# flask db upgrade

# Or initialize manually
python3 -c "from src.core.database import Database; db = Database(); print('Database initialized')"
```

---

## Configuration

### Environment Variables

Edit `.env` file with your production settings:

```bash
# Application
FLASK_ENV=production
DEBUG=false
SECRET_KEY=<your-secure-secret-key>
APP_PORT=5000

# Database
DATABASE_URL=sqlite:///data/db/services.db
# Or PostgreSQL: postgresql://user:password@localhost:5432/dms

# Email (Optional)
ENABLE_EMAIL=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# Cache (with Redis)
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
PERMANENT_SESSION_LIFETIME=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Critical Production Settings

**MUST CHANGE:**
- `SECRET_KEY`: Generate strong random key
- `SMTP_PASSWORD`: Real email credentials
- `ADMIN_EMAIL`: Your admin email

**RECOMMENDED:**
- Use PostgreSQL instead of SQLite for production
- Enable Redis caching for better performance
- Set up email notifications

---

## Database Setup

### Using SQLite (Development/Small Production)

```bash
# Already configured by default
# Database file: data/db/services.db
```

### Using PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE dms_production;
CREATE USER dms_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE dms_production TO dms_user;
\q

# Update .env
DATABASE_URL=postgresql://dms_user:secure-password@localhost:5432/dms_production

# Install PostgreSQL adapter
pip install psycopg2-binary
```

---

## Web Server Setup

### Option 1: Gunicorn Only (Simple)

```bash
# Start with gunicorn
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --threads 2 \
         --timeout 60 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         src.web_app:app
```

### Option 2: Nginx + Gunicorn (Recommended)

#### 1. Create Supervisor Configuration

```bash
# /etc/supervisor/conf.d/dms.conf
[program:dms]
command=/home/dms/app/venv/bin/gunicorn --bind 127.0.0.1:5000 \
        --workers 4 --threads 2 --timeout 60 \
        --access-logfile /home/dms/app/logs/access.log \
        --error-logfile /home/dms/app/logs/error.log \
        src.web_app:app
directory=/home/dms/app
user=dms
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/dms/app/logs/supervisor.log
environment=PATH="/home/dms/app/venv/bin"
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start dms
sudo supervisorctl status dms
```

#### 2. Configure Nginx

```bash
# /etc/nginx/sites-available/dms
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 16M;

    location /static/ {
        alias /home/dms/app/web/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS Configuration

### Option 1: Let's Encrypt (Free, Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### Option 2: Self-Signed Certificate (Development)

```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem

# Update nginx configuration
# listen 443 ssl;
# ssl_certificate /etc/nginx/ssl/cert.pem;
# ssl_certificate_key /etc/nginx/ssl/key.pem;
```

---

## Monitoring and Logging

### Log Files

```bash
# Application logs
tail -f /home/dms/app/logs/app.log
tail -f /home/dms/app/logs/api.log
tail -f /home/dms/app/logs/errors.log

# Gunicorn logs
tail -f /home/dms/app/logs/access.log
tail -f /home/dms/app/logs/error.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Supervisor logs
sudo tail -f /home/dms/app/logs/supervisor.log
```

### Log Rotation

```bash
# /etc/logrotate.d/dms
/home/dms/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 dms dms
    sharedscripts
    postrotate
        sudo supervisorctl restart dms
    endscript
}
```

### Health Checks

```bash
# Application health
curl http://localhost:5000/api/health

# Detailed status
curl http://localhost:5000/api/statistics
```

---

## Backup and Recovery

### Database Backup

```bash
# SQLite backup
cp data/db/services.db backups/services_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL backup
pg_dump -U dms_user dms_production > backups/dms_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
# /home/dms/backup.sh
BACKUP_DIR=/home/dms/backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cp /home/dms/app/data/db/services.db $BACKUP_DIR/services_$DATE.db

# Backup exports
tar -czf $BACKUP_DIR/exports_$DATE.tar.gz /home/dms/app/data/exports/

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Add to crontab
crontab -e
# Daily backup at 2 AM
0 2 * * * /home/dms/backup.sh
```

### Restore from Backup

```bash
# Stop application
sudo supervisorctl stop dms

# Restore database
cp backups/services_YYYYMMDD_HHMMSS.db data/db/services.db

# Start application
sudo supervisorctl start dms
```

---

## Security Hardening

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
sudo ufw status
```

### File Permissions

```bash
# Restrict permissions
chmod 750 /home/dms/app
chmod 640 /home/dms/app/.env
chmod 750 /home/dms/app/data
chmod 750 /home/dms/app/logs

# Restrict database access
chmod 600 /home/dms/app/data/db/services.db
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS with valid certificate
- [ ] Configure firewall
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Regular backups
- [ ] Monitor error logs
- [ ] Restrict database access

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
tail -f logs/error.log

# Check supervisor
sudo supervisorctl status dms

# Test manually
source venv/bin/activate
python src/web_app.py
```

### Database Errors

```bash
# Check database permissions
ls -la data/db/

# Reinitialize database
python -c "from src.core.database import Database; Database()"
```

### Nginx 502 Bad Gateway

```bash
# Check if application is running
sudo supervisorctl status dms

# Check Gunicorn logs
tail -f logs/error.log

# Restart services
sudo supervisorctl restart dms
sudo systemctl restart nginx
```

### High Memory Usage

```bash
# Reduce Gunicorn workers
# Edit /etc/supervisor/conf.d/dms.conf
# --workers 2  # Reduce from 4

# Enable Redis caching
# Edit .env: CACHE_TYPE=redis
```

---

## Performance Optimization

### Enable Caching

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Update .env
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0
```

### Database Optimization

```bash
# For PostgreSQL
# Add indexes for frequently queried fields
# Regularly VACUUM ANALYZE
```

---

## Update Procedure

```bash
# 1. Backup
/home/dms/backup.sh

# 2. Pull updates
cd /home/dms/app
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart application
sudo supervisorctl restart dms

# 5. Verify
curl http://localhost:5000/api/health
```

---

## Support

For issues and support:
- Check logs: `logs/*.log`
- GitHub Issues: <repository-url>/issues
- Email: admin@yourdomain.com

---

**Last Updated:** January 2026
**Version:** 2.1.0
