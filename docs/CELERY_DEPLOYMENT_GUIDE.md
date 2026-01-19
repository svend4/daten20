# 🚀 Celery Deployment Guide

## Production Deployment for DMS Async Task Queue

**Version:** 1.0.0
**Date:** 2026-01-18
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Redis Setup](#redis-setup)
4. [Systemd Deployment](#systemd-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Supervisor Deployment](#supervisor-deployment)
7. [Environment Configuration](#environment-configuration)
8. [Monitoring](#monitoring)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## 🎯 Overview

This guide covers production deployment of Celery workers for the Document Management System's async task processing.

### Architecture Components

- **Celery Workers**: Execute async tasks (document processing, ML operations)
- **Celery Beat**: Periodic task scheduler (backups, health checks)
- **Redis**: Message broker and result backend
- **Flower**: Web-based monitoring UI (optional)

### Production Requirements

- Linux server (Ubuntu 20.04+ or RHEL 8+)
- Python 3.8+
- Redis 6.0+
- 4+ CPU cores (recommended)
- 8+ GB RAM (recommended)
- Systemd or Docker

---

## 📦 Prerequisites

### 1. System Packages

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv redis-server supervisor

# RHEL/CentOS
sudo yum install -y python3-pip python3-virtualenv redis supervisor
```

### 2. Python Dependencies

```bash
# Create virtual environment
python3 -m venv /opt/dms/venv
source /opt/dms/venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install celery[redis] flower
```

### 3. Application Setup

```bash
# Clone repository
git clone https://github.com/yourusername/dms.git /opt/dms
cd /opt/dms

# Install application
pip install -e .
```

---

## 🔴 Redis Setup

### Option 1: System Redis (Recommended for Production)

#### Ubuntu/Debian

```bash
# Install Redis
sudo apt-get install -y redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Make these changes:
# bind 127.0.0.1  # Listen only on localhost (secure)
# maxmemory 2gb   # Set memory limit
# maxmemory-policy allkeys-lru  # Eviction policy
# save 900 1      # Persistence settings
# save 300 10
# save 60 10000

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping  # Should return PONG
```

#### RHEL/CentOS

```bash
# Install Redis
sudo yum install -y redis

# Configure Redis
sudo nano /etc/redis.conf
# (Make same changes as above)

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Verify
redis-cli ping
```

### Option 2: Docker Redis

```bash
# Run Redis container
docker run -d \
  --name dms-redis \
  --restart always \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine redis-server \
    --maxmemory 2gb \
    --maxmemory-policy allkeys-lru \
    --save 900 1 \
    --save 300 10 \
    --save 60 10000

# Verify
docker exec dms-redis redis-cli ping
```

### Redis Security

```bash
# Set password (recommended for production)
sudo nano /etc/redis/redis.conf

# Add:
requirepass YOUR_STRONG_PASSWORD

# Restart Redis
sudo systemctl restart redis-server

# Update connection URL
export CELERY_BROKER_URL="redis://:YOUR_STRONG_PASSWORD@localhost:6379/0"
```

---

## 🖥️ Systemd Deployment

### 1. Create Celery Worker Service

```bash
sudo nano /etc/systemd/system/celery-worker.service
```

**Content:**

```ini
[Unit]
Description=DMS Celery Worker
After=network.target redis.service
Requires=redis.service

[Service]
Type=forking
User=dms
Group=dms
WorkingDirectory=/opt/dms
Environment="PATH=/opt/dms/venv/bin"
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
Environment="CELERY_RESULT_BACKEND=redis://localhost:6379/0"
Environment="C_FORCE_ROOT=false"

ExecStart=/opt/dms/venv/bin/celery -A src.core.celery_app multi start worker1 \
  --pidfile=/var/run/celery/%n.pid \
  --logfile=/var/log/celery/%n%I.log \
  --loglevel=INFO \
  --concurrency=4 \
  --max-tasks-per-child=1000

ExecStop=/opt/dms/venv/bin/celery -A src.core.celery_app multi stopwait worker1 \
  --pidfile=/var/run/celery/%n.pid

ExecReload=/opt/dms/venv/bin/celery -A src.core.celery_app multi restart worker1 \
  --pidfile=/var/run/celery/%n.pid \
  --logfile=/var/log/celery/%n%I.log \
  --loglevel=INFO \
  --concurrency=4

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Create Celery Beat Service

```bash
sudo nano /etc/systemd/system/celery-beat.service
```

**Content:**

```ini
[Unit]
Description=DMS Celery Beat Scheduler
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=dms
Group=dms
WorkingDirectory=/opt/dms
Environment="PATH=/opt/dms/venv/bin"
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
Environment="CELERY_RESULT_BACKEND=redis://localhost:6379/0"

ExecStart=/opt/dms/venv/bin/celery -A src.core.celery_app beat \
  --pidfile=/var/run/celery/beat.pid \
  --logfile=/var/log/celery/beat.log \
  --loglevel=INFO

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Setup Directories and Permissions

```bash
# Create user
sudo useradd -r -s /bin/false dms

# Create directories
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown -R dms:dms /var/log/celery /var/run/celery
sudo chown -R dms:dms /opt/dms

# Set permissions
sudo chmod 755 /var/log/celery /var/run/celery
```

### 4. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat

# Start services
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Check status
sudo systemctl status celery-worker
sudo systemctl status celery-beat

# View logs
sudo journalctl -u celery-worker -f
sudo journalctl -u celery-beat -f
```

### 5. Management Commands

```bash
# Restart workers
sudo systemctl restart celery-worker

# Stop workers
sudo systemctl stop celery-worker

# Reload configuration (graceful restart)
sudo systemctl reload celery-worker

# View worker stats
celery -A src.core.celery_app inspect stats

# View active tasks
celery -A src.core.celery_app inspect active

# Purge all tasks
celery -A src.core.celery_app purge
```

---

## 🐳 Docker Deployment

### 1. Dockerfile for Celery Worker

Create `docker/Dockerfile.celery`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir celery[redis] flower

COPY . .

# Create non-root user
RUN useradd -m -u 1000 celery && \
    chown -R celery:celery /app

USER celery

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD celery -A src.core.celery_app inspect ping -d celery@$HOSTNAME || exit 1

# Default command
CMD ["celery", "-A", "src.core.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
```

### 2. Docker Compose

Create `docker-compose.celery.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: dms-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: >
      redis-server
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  celery-worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.celery
    container_name: dms-celery-worker
    restart: always
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - C_FORCE_ROOT=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    command: >
      celery -A src.core.celery_app worker
      --loglevel=info
      --concurrency=4
      --max-tasks-per-child=1000

  celery-beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.celery
    container_name: dms-celery-beat
    restart: always
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    command: >
      celery -A src.core.celery_app beat
      --loglevel=info

  flower:
    build:
      context: .
      dockerfile: docker/Dockerfile.celery
    container_name: dms-flower
    restart: always
    depends_on:
      - redis
      - celery-worker
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    ports:
      - "5555:5555"
    command: >
      celery -A src.core.celery_app flower
      --port=5555

volumes:
  redis-data:

networks:
  default:
    name: dms-network
```

### 3. Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.celery.yml up -d

# View logs
docker-compose -f docker-compose.celery.yml logs -f celery-worker

# Scale workers
docker-compose -f docker-compose.celery.yml up -d --scale celery-worker=4

# Stop services
docker-compose -f docker-compose.celery.yml down

# Restart worker
docker-compose -f docker-compose.celery.yml restart celery-worker
```

### 4. Docker Management Commands

```bash
# Check worker status
docker exec dms-celery-worker celery -A src.core.celery_app inspect stats

# View active tasks
docker exec dms-celery-worker celery -A src.core.celery_app inspect active

# Purge tasks
docker exec dms-celery-worker celery -A src.core.celery_app purge

# Access Flower UI
open http://localhost:5555
```

---

## 🔧 Supervisor Deployment

### 1. Install Supervisor

```bash
# Ubuntu/Debian
sudo apt-get install -y supervisor

# RHEL/CentOS
sudo yum install -y supervisor
```

### 2. Configure Celery Worker

Create `/etc/supervisor/conf.d/celery-worker.conf`:

```ini
[program:celery-worker]
command=/opt/dms/venv/bin/celery -A src.core.celery_app worker --loglevel=info --concurrency=4 --max-tasks-per-child=1000
directory=/opt/dms
user=dms
group=dms
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stopasgroup=true
killasgroup=true
priority=998
environment=PATH="/opt/dms/venv/bin",CELERY_BROKER_URL="redis://localhost:6379/0",CELERY_RESULT_BACKEND="redis://localhost:6379/0"
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_err.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

### 3. Configure Celery Beat

Create `/etc/supervisor/conf.d/celery-beat.conf`:

```ini
[program:celery-beat]
command=/opt/dms/venv/bin/celery -A src.core.celery_app beat --loglevel=info
directory=/opt/dms
user=dms
group=dms
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=60
priority=999
environment=PATH="/opt/dms/venv/bin",CELERY_BROKER_URL="redis://localhost:6379/0",CELERY_RESULT_BACKEND="redis://localhost:6379/0"
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_err.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

### 4. Start Services

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start services
sudo supervisorctl start celery-worker
sudo supervisorctl start celery-beat

# Check status
sudo supervisorctl status

# View logs
sudo tail -f /var/log/celery/worker.log
```

### 5. Management Commands

```bash
# Restart worker
sudo supervisorctl restart celery-worker

# Stop worker
sudo supervisorctl stop celery-worker

# Start all
sudo supervisorctl start all

# Status
sudo supervisorctl status all
```

---

## 🔐 Environment Configuration

### 1. Environment Variables

Create `/opt/dms/.env`:

```bash
# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Worker Configuration
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
CELERY_WORKER_PREFETCH_MULTIPLIER=4

# Task Configuration
CELERY_TASK_ACKS_LATE=true
CELERY_TASK_REJECT_ON_WORKER_LOST=true
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3300

# Result Backend Configuration
CELERY_RESULT_EXPIRES=3600
CELERY_RESULT_PERSISTENT=true

# Beat Configuration
CELERY_BEAT_SCHEDULE_FILENAME=/opt/dms/data/celerybeat-schedule

# Logging
CELERY_LOG_LEVEL=INFO
```

### 2. Load Environment

```bash
# In systemd service
EnvironmentFile=/opt/dms/.env

# In supervisor config
environment=...

# In Docker
env_file:
  - .env

# Manual
source /opt/dms/.env
```

---

## 📊 Monitoring

### 1. Flower Setup

#### Systemd

Create `/etc/systemd/system/flower.service`:

```ini
[Unit]
Description=DMS Flower Monitoring
After=network.target redis.service celery-worker.service
Requires=redis.service

[Service]
Type=simple
User=dms
Group=dms
WorkingDirectory=/opt/dms
Environment="PATH=/opt/dms/venv/bin"
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"

ExecStart=/opt/dms/venv/bin/celery -A src.core.celery_app flower \
  --port=5555 \
  --basic_auth=admin:YOUR_PASSWORD

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable flower
sudo systemctl start flower
```

#### Access Flower

```bash
# Local
open http://localhost:5555

# Remote (with SSH tunnel)
ssh -L 5555:localhost:5555 user@server
open http://localhost:5555
```

### 2. Monitoring Metrics

```bash
# Worker stats
celery -A src.core.celery_app inspect stats

# Active tasks
celery -A src.core.celery_app inspect active

# Scheduled tasks
celery -A src.core.celery_app inspect scheduled

# Registered tasks
celery -A src.core.celery_app inspect registered

# Worker pool info
celery -A src.core.celery_app inspect pool_info
```

### 3. Health Checks

Create monitoring script `/opt/dms/scripts/celery_health.sh`:

```bash
#!/bin/bash

# Check worker is responding
celery -A src.core.celery_app inspect ping -d celery@$(hostname) > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Celery worker is healthy"
    exit 0
else
    echo "❌ Celery worker is not responding"
    exit 1
fi
```

Add to cron:

```bash
# Check every 5 minutes
*/5 * * * * /opt/dms/scripts/celery_health.sh
```

---

## ⚡ Performance Tuning

### 1. Worker Concurrency

```bash
# CPU-bound tasks (ML operations)
# Set concurrency = CPU cores
--concurrency=4

# I/O-bound tasks (file operations)
# Set concurrency = 2 * CPU cores
--concurrency=8
```

### 2. Prefetch Settings

```bash
# Low prefetch for long tasks
CELERY_WORKER_PREFETCH_MULTIPLIER=1

# Higher prefetch for short tasks
CELERY_WORKER_PREFETCH_MULTIPLIER=4
```

### 3. Task Acknowledgement

```bash
# Late ack (better fault tolerance)
CELERY_TASK_ACKS_LATE=true

# Early ack (better performance)
CELERY_TASK_ACKS_LATE=false
```

### 4. Memory Management

```bash
# Restart worker after N tasks (prevent memory leaks)
--max-tasks-per-child=1000

# Restart worker after memory limit
--max-memory-per-child=1000000  # 1GB
```

### 5. Redis Tuning

```bash
# In /etc/redis/redis.conf

# Increase max memory
maxmemory 4gb

# Use LRU eviction
maxmemory-policy allkeys-lru

# Disable persistence (if acceptable)
save ""

# Or optimize persistence
save 900 1
save 300 10
```

---

## 🐛 Troubleshooting

### Issue 1: Worker Not Starting

**Symptoms:**
```
Error: Cannot connect to redis://localhost:6379/0
```

**Solutions:**

1. Check Redis is running:
```bash
redis-cli ping
sudo systemctl status redis
```

2. Check connection URL:
```bash
echo $CELERY_BROKER_URL
```

3. Test Redis connection:
```bash
redis-cli -h localhost -p 6379 ping
```

---

### Issue 2: Tasks Not Being Processed

**Symptoms:**
```
Tasks stuck in PENDING state
```

**Solutions:**

1. Check worker is running:
```bash
celery -A src.core.celery_app inspect active
```

2. Check task routing:
```bash
celery -A src.core.celery_app inspect registered
```

3. Purge old tasks:
```bash
celery -A src.core.celery_app purge
```

---

### Issue 3: Memory Issues

**Symptoms:**
```
Worker killed by OOM
```

**Solutions:**

1. Reduce concurrency:
```bash
--concurrency=2
```

2. Set max tasks per child:
```bash
--max-tasks-per-child=100
```

3. Increase system memory or swap

---

### Issue 4: Slow Performance

**Symptoms:**
```
Tasks taking too long
```

**Solutions:**

1. Increase worker concurrency:
```bash
--concurrency=8
```

2. Scale workers:
```bash
# Systemd
sudo systemctl start celery-worker@2

# Docker
docker-compose up -d --scale celery-worker=4
```

3. Optimize Redis:
```bash
# Disable persistence
save ""
```

---

## 🔄 Maintenance

### 1. Log Rotation

Create `/etc/logrotate.d/celery`:

```
/var/log/celery/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 dms dms
    sharedscripts
    postrotate
        systemctl reload celery-worker > /dev/null 2>&1 || true
    endscript
}
```

### 2. Backup Procedures

```bash
# Backup Redis data
redis-cli BGSAVE

# Copy Redis dump
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb

# Backup Celery beat schedule
cp /opt/dms/data/celerybeat-schedule /backup/celerybeat-$(date +%Y%m%d)
```

### 3. Update Procedures

```bash
# 1. Pull latest code
cd /opt/dms
git pull

# 2. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 3. Restart workers (graceful)
sudo systemctl reload celery-worker

# 4. Restart beat (if needed)
sudo systemctl restart celery-beat

# 5. Verify
celery -A src.core.celery_app inspect stats
```

### 4. Monitoring Tasks

```bash
# Daily: Check worker health
celery -A src.core.celery_app inspect ping

# Weekly: Check queue size
redis-cli LLEN celery

# Monthly: Review logs
sudo journalctl -u celery-worker --since "1 month ago" | grep ERROR
```

---

## 📚 Additional Resources

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
- [DMS Async Processing Guide](ASYNC_PROCESSING_GUIDE.md)

---

## ✅ Production Checklist

Before deploying to production:

- [ ] Redis secured with password
- [ ] Firewall configured (only necessary ports open)
- [ ] Systemd services enabled
- [ ] Log rotation configured
- [ ] Monitoring setup (Flower)
- [ ] Health checks configured
- [ ] Backup procedures in place
- [ ] Worker concurrency tuned
- [ ] Memory limits configured
- [ ] Environment variables secured
- [ ] SSL/TLS configured (if remote Redis)
- [ ] Alerts configured (email, Slack)

---

**Last Updated:** 2026-01-18
**Version:** 1.0.0
**Status:** ✅ Production Ready
