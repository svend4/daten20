# Production Deployment Guide - v3.0

Complete guide for deploying the Document Management System with enterprise features to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Scaling Configuration](#scaling-configuration)
7. [Security Hardening](#security-hardening)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum (Small deployment):**
- 2 CPU cores
- 4 GB RAM
- 50 GB SSD storage
- Ubuntu 22.04 LTS or later

**Recommended (Production):**
- 4-8 CPU cores
- 16-32 GB RAM
- 200 GB SSD storage (+ separate storage for documents)
- Load balancer (HAProxy/Nginx)
- PostgreSQL 15+ with replication
- Redis cluster

### Software Dependencies

```bash
# System packages
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    postgresql-client redis-tools nginx certbot \
    git build-essential libpq-dev

# Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

---

## Infrastructure Setup

### 1. Cloud Provider Setup

#### AWS

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create subnets
aws ec2 create-subnet --vpc-id vpc-xxxx \
    --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier dms-prod \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.4 \
    --master-username dmsadmin \
    --master-user-password <password> \
    --allocated-storage 100

# Create ElastiCache Redis
aws elasticache create-cache-cluster \
    --cache-cluster-id dms-cache \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

#### Azure

```bash
# Create resource group
az group create --name dms-prod --location eastus

# Create PostgreSQL
az postgres flexible-server create \
    --resource-group dms-prod \
    --name dms-db \
    --sku-name Standard_D2s_v3 \
    --storage-size 128

# Create Redis
az redis create \
    --resource-group dms-prod \
    --name dms-cache \
    --location eastus \
    --sku Standard \
    --vm-size c1
```

### 2. DNS Configuration

```bash
# Point domain to load balancer
# A record: app.yourdomain.com → <load-balancer-ip>
# A record: api.yourdomain.com → <load-balancer-ip>

# Verify DNS
dig app.yourdomain.com
```

### 3. SSL Certificate

```bash
# Using Let's Encrypt
sudo certbot certonly --standalone \
    -d app.yourdomain.com \
    -d api.yourdomain.com \
    --email admin@yourdomain.com \
    --agree-tos \
    --non-interactive

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Database Configuration

### 1. PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE dms_production;

-- Create user
CREATE USER dms_app WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dms_production TO dms_app;

-- Connect to database
\c dms_production

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schema for each tenant (schema-per-tenant strategy)
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_example;

-- Grant schema access
GRANT ALL ON SCHEMA tenant_acme TO dms_app;
GRANT ALL ON SCHEMA tenant_example TO dms_app;
```

### 2. Connection Pooling

```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)
```

### 3. Read Replicas

```python
# For read-heavy operations
read_engine = create_engine(
    READ_REPLICA_URL,
    poolclass=QueuePool,
    pool_size=30
)

# Use read replica for reports
with read_engine.connect() as conn:
    result = conn.execute("SELECT * FROM documents WHERE ...")
```

---

## Application Deployment

### 1. Environment Configuration

Create `.env.production`:

```bash
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Database
DATABASE_URL=postgresql://dms_app:password@db.example.com:5432/dms_production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://cache.example.com:6379/0
REDIS_POOL_SIZE=10

# Security
ALLOWED_HOSTS=app.yourdomain.com,api.yourdomain.com
CORS_ORIGINS=https://app.yourdomain.com
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

# Monitoring
SENTRY_DSN=https://xxxx@sentry.io/yyyy
PROMETHEUS_PORT=9090

# Billing
STRIPE_API_KEY=sk_live_xxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxx

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=<password>
SMTP_TLS=true

# Storage
S3_BUCKET=dms-documents-prod
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>

# Scaling
MIN_INSTANCES=3
MAX_INSTANCES=10
AUTO_SCALING_ENABLED=true
```

### 2. Docker Deployment

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    gunicorn==21.2.0 \
    gevent==23.9.1

# Copy application
COPY src/ ./src/
COPY web/ ./web/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 dms && chown -R dms:dms /app
USER dms

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "gevent", \
     "--worker-connections", "1000", \
     "--max-requests", "10000", \
     "--max-requests-jitter", "1000", \
     "--timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "src.web_app:app"]
```

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.production
    image: dms:v3.0-prod
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    env_file:
      - .env.production
    networks:
      - dms-network
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    networks:
      - dms-network
    depends_on:
      - app
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dms_production
      POSTGRES_USER: dms_app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - dms-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - dms-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - dms-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - dms-network
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  dms-network:
    driver: bridge
```

### 3. Nginx Configuration

```nginx
# nginx.conf
upstream dms_app {
    least_conn;
    server app:8000 max_fails=3 fail_timeout=30s;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=web_limit:10m rate=30r/s;

server {
    listen 80;
    server_name app.yourdomain.com api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.yourdomain.com api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/dms_access.log combined;
    error_log /var/log/nginx/dms_error.log warn;

    # Max upload size
    client_max_body_size 100M;

    # API routes with rate limiting
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://dms_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Web routes
    location / {
        limit_req zone=web_limit burst=50 nodelay;

        proxy_pass http://dms_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://dms_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files
    location /static/ {
        alias /app/web/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        proxy_pass http://dms_app;
        access_log off;
    }
}
```

### 4. Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Deploying DMS v3.0 to production..."

# Pull latest code
git pull origin main

# Build Docker image
docker-compose -f docker-compose.production.yml build

# Run database migrations
docker-compose -f docker-compose.production.yml run --rm app \
    python -m alembic upgrade head

# Stop old containers
docker-compose -f docker-compose.production.yml down

# Start new containers
docker-compose -f docker-compose.production.yml up -d

# Wait for health check
echo "Waiting for application to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost/health; then
        echo "✅ Application is healthy!"
        break
    fi
    sleep 2
done

# Show logs
docker-compose -f docker-compose.production.yml logs --tail=50 app

echo "✅ Deployment complete!"
```

---

## Monitoring & Logging

### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'

scrape_configs:
  - job_name: 'dms'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 2. Alert Rules

```yaml
# alerts.yml
groups:
  - name: dms_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests/sec"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_ms_bucket[5m])) > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile is {{ $value }}ms"

      - alert: HighCPUUsage
        expr: system_cpu_usage_percent > 85
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"
```

### 3. Centralized Logging

```python
# config/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_production_logging():
    """Setup production logging with JSON format"""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
```

---

## Scaling Configuration

### 1. Horizontal Pod Autoscaler (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dms-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dms-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Database Connection Pooling

Adjust based on load:
```
Total connections = (workers × threads × instances) + overhead
Example: (4 workers × 10 threads × 3 instances) + 20 = 140 connections
```

---

## Security Hardening

### 1. Firewall Rules

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Secrets Management

Use AWS Secrets Manager or HashiCorp Vault:

```python
import boto3

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

DATABASE_PASSWORD = get_secret('dms/database/password')
```

---

## Backup & Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dms_backup_$DATE.sql.gz"

# Create backup
pg_dump -h localhost -U dms_app dms_production | gzip > "$BACKUP_FILE"

# Upload to S3
aws s3 cp "$BACKUP_FILE" s3://dms-backups/database/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "✅ Backup completed: $BACKUP_FILE"
```

### 2. Automated Backups

```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-db.sh
0 3 * * * /usr/local/bin/backup-redis.sh
0 4 * * * /usr/local/bin/backup-files.sh
```

---

## Performance Tuning

### 1. PostgreSQL Tuning

```sql
-- postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB
max_connections = 200
```

### 2. Redis Tuning

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

---

## Troubleshooting

### Common Issues

**High CPU Usage:**
```bash
# Check processes
docker stats

# Check slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

**Memory Leaks:**
```bash
# Monitor memory
free -h
docker stats --no-stream

# Restart containers
docker-compose restart app
```

**Database Connection Pool Exhausted:**
```python
# Increase pool size in config
engine = create_engine(DATABASE_URL, pool_size=30, max_overflow=60)
```

---

## Support

For production issues:
- Emergency: ops@yourdomain.com
- Status Page: status.yourdomain.com
- Monitoring: grafana.yourdomain.com

---

**Document Version:** v3.0
**Last Updated:** 2026-01-10
**Maintained By:** DevOps Team
