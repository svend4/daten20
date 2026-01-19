# 🚀 Complete Deployment Guide

**Document Management System - Comprehensive Deployment Reference**

Your complete guide to deploying the DMS system across all environments and platforms.

**Version:** 4.1.0
**Last Updated:** 2026-01-16
**Status:** Production Ready

---

## 📋 Table of Contents

### Quick Start
- [Which Deployment Option?](#-which-deployment-option)
- [Quick Deploy Commands](#-quick-deploy-commands)
- [5-Minute Docker Setup](#5-minute-docker-setup)

### Deployment Methods
1. [Docker Deployment](#1-docker-deployment)
2. [Kubernetes Deployment](#2-kubernetes-deployment)
3. [Cloud Platform Deployments](#3-cloud-platform-deployments)
4. [Manual Deployment](#4-manual-deployment)

### Configuration
5. [Environment Configuration](#5-environment-configuration)
6. [Database Setup](#6-database-setup)
7. [SSL/TLS Configuration](#7-ssltls-configuration)
8. [Security Hardening](#8-security-hardening)

### Operations
9. [CI/CD Integration](#9-cicd-integration)
10. [Monitoring & Logging](#10-monitoring--logging)
11. [Scaling Strategies](#11-scaling-strategies)
12. [Backup & Recovery](#12-backup--recovery)

### Advanced
13. [High Availability Setup](#13-high-availability-setup)
14. [Performance Optimization](#14-performance-optimization)
15. [Troubleshooting](#15-troubleshooting)

---

## 🎯 Which Deployment Option?

Choose your deployment strategy based on your needs:

### Decision Matrix

| Scenario | Recommended Deployment | Time | Difficulty | Link |
|----------|------------------------|------|------------|------|
| **Quick Testing** | Docker (Single Container) | 5 min | ⭐ Easy | [Jump →](#5-minute-docker-setup) |
| **Small Production** | Docker Compose | 30 min | ⭐⭐ Medium | [Jump →](#docker-compose-production) |
| **Medium Production** | Kubernetes (Single Cluster) | 2-4 hours | ⭐⭐⭐ Advanced | [Jump →](#kubernetes-single-cluster) |
| **Large Production** | Kubernetes (Multi-Cloud) | 1-2 days | ⭐⭐⭐⭐ Expert | [Jump →](#kubernetes-multi-cloud) |
| **AWS Focus** | ECS/EKS | 2-4 hours | ⭐⭐⭐ Advanced | [Jump →](#aws-deployment) |
| **Azure Focus** | AKS | 2-4 hours | ⭐⭐⭐ Advanced | [Jump →](#azure-deployment) |
| **GCP Focus** | GKE | 2-4 hours | ⭐⭐⭐ Advanced | [Jump →](#gcp-deployment) |
| **On-Premises** | Manual Install | 4-8 hours | ⭐⭐⭐ Advanced | [Jump →](#manual-deployment) |

### Quick Comparison

| Feature | Docker | Kubernetes | Cloud Managed | Manual |
|---------|--------|------------|---------------|--------|
| **Setup Time** | 5-30 min | 2-4 hours | 2-4 hours | 4-8 hours |
| **Auto-Scaling** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **High Availability** | ❌ No | ✅ Yes | ✅ Yes | Manual |
| **Cost** | $ Low | $$ Medium | $$$ High | $ Low |
| **Maintenance** | Low | Medium | Low | High |
| **Best For** | Dev/Test | Production | Enterprise | Custom |

---

## ⚡ Quick Deploy Commands

### Option 1: Docker (Fastest - 5 minutes)

```bash
# Clone and start
git clone https://github.com/svend4/daten20.git
cd daten20
cp .env.example .env
docker-compose up -d

# Access at http://localhost:5000
```

### Option 2: Kubernetes (Production - 1 hour)

```bash
# Prerequisites: kubectl configured
cd daten20/k8s/
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n dms
```

### Option 3: Cloud Platform (AWS ECS - 30 minutes)

```bash
# Prerequisites: AWS CLI configured
cd daten20/deploy/aws/
terraform init
terraform plan
terraform apply

# Get load balancer URL
terraform output load_balancer_url
```

---

## 🐳 1. Docker Deployment

### 5-Minute Docker Setup

**For development and testing:**

```bash
# Step 1: Clone repository
git clone https://github.com/svend4/daten20.git
cd daten20

# Step 2: Create environment file
cp .env.example .env

# Step 3: Edit critical variables
nano .env
# Set these:
# SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
# DATABASE_URL=sqlite:///data/dms.db
# FLASK_ENV=development

# Step 4: Build and start
docker-compose up -d

# Step 5: Initialize database
docker-compose exec web python -c "from src.core.database import Database; Database().init_db()"

# Step 6: Create admin user (optional)
docker-compose exec web python dms-admin.py users create \
    --username admin \
    --email admin@example.com \
    --password admin123 \
    --role admin

# Step 7: Verify
docker-compose ps
curl http://localhost:5000/health

# Access dashboard
open http://localhost:5000
```

**Result:** DMS running at `http://localhost:5000`

---

### Docker Compose Production

**For small production deployments with PostgreSQL and Redis:**

#### Step 1: Prepare Environment

```bash
# Create production directory
mkdir -p /opt/dms && cd /opt/dms

# Clone repository
git clone https://github.com/svend4/daten20.git .

# Create environment file
cp .env.example .env.production
```

#### Step 2: Configure Production Environment

Edit `.env.production`:

```bash
# Security
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=production
DEBUG=False

# Database (PostgreSQL)
DATABASE_URL=postgresql://dmsuser:secure_password@postgres:5432/dms_prod

# Redis Cache
REDIS_URL=redis://redis:6379/0

# API Configuration
API_RATE_LIMIT=1000
API_KEY_EXPIRY_DAYS=90

# Email (for notifications)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=notifications@example.com
MAIL_PASSWORD=<password>

# File Storage
UPLOAD_FOLDER=/app/data/uploads
MAX_CONTENT_LENGTH=104857600  # 100 MB

# Workers
WORKERS=4
THREADS=2
WORKER_CLASS=gthread
```

#### Step 3: Create Production Docker Compose

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: dms-postgres
    restart: always
    environment:
      POSTGRES_DB: dms_prod
      POSTGRES_USER: dmsuser
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - dms-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dmsuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: dms-redis
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - dms-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILD_ENV: production
    container_name: dms-web
    restart: always
    env_file:
      - .env.production
    environment:
      DATABASE_URL: postgresql://dmsuser:${POSTGRES_PASSWORD}@postgres:5432/dms_prod
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    networks:
      - dms-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    command: gunicorn -w 4 -b 0.0.0.0:8000 --worker-class gthread --threads 2 --timeout 120 src.web_app:app

  nginx:
    image: nginx:alpine
    container_name: dms-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./static:/usr/share/nginx/html/static:ro
    networks:
      - dms-network
    depends_on:
      - web
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Worker for background tasks
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dms-worker
    restart: always
    env_file:
      - .env.production
    environment:
      DATABASE_URL: postgresql://dmsuser:${POSTGRES_PASSWORD}@postgres:5432/dms_prod
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - dms-network
    depends_on:
      - postgres
      - redis
    command: celery -A src.tasks worker --loglevel=info

networks:
  dms-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

#### Step 4: Create Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream dms_app {
        server web:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web_limit:10m rate=30r/s;

    server {
        listen 80;
        server_name _;

        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name dms.example.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Logging
        access_log /var/log/nginx/dms_access.log;
        error_log /var/log/nginx/dms_error.log;

        # Max upload size
        client_max_body_size 100M;

        # Static files
        location /static/ {
            alias /usr/share/nginx/html/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # API endpoints with rate limiting
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

        # Web interface
        location / {
            limit_req zone=web_limit burst=50 nodelay;

            proxy_pass http://dms_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint (no rate limit)
        location /health {
            proxy_pass http://dms_app;
            access_log off;
        }
    }
}
```

#### Step 5: Deploy

```bash
# Create required directories
mkdir -p nginx/ssl data logs backups

# Generate self-signed SSL certificate (for testing)
# For production, use Let's Encrypt (see SSL section below)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem

# Set secure permissions
chmod 600 nginx/ssl/privkey.pem

# Start production services
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
docker-compose -f docker-compose.production.yml ps

# Initialize database
docker-compose -f docker-compose.production.yml exec web \
    python -c "from src.core.database import Database; Database().init_db()"

# Create admin user
docker-compose -f docker-compose.production.yml exec web \
    python dms-admin.py users create \
        --username admin \
        --email admin@example.com \
        --password <secure_password> \
        --role admin

# Check logs
docker-compose -f docker-compose.production.yml logs -f web
```

#### Step 6: Verify Deployment

```bash
# Check service status
docker-compose -f docker-compose.production.yml ps

# Test health endpoint
curl -k https://localhost/health

# Test API
curl -k https://localhost/api/v1/health

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Monitor resources
docker stats
```

---

### Docker Management Commands

```bash
# View logs
docker-compose logs -f web
docker-compose logs -f postgres

# Restart services
docker-compose restart web

# Stop services
docker-compose stop

# Start services
docker-compose start

# Complete shutdown
docker-compose down

# Rebuild after code changes
docker-compose build web
docker-compose up -d web

# Execute command in container
docker-compose exec web python dms-admin.py system status

# Database backup
docker-compose exec postgres pg_dump -U dmsuser dms_prod > backup_$(date +%Y%m%d).sql

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

---

## ☸️ 2. Kubernetes Deployment

### Kubernetes Single Cluster

**For production deployments with auto-scaling and high availability.**

#### Prerequisites

```bash
# Required tools
- kubectl 1.21+
- helm 3.0+ (optional, for easy deployment)
- Cloud provider CLI (aws/gcloud/az)

# Verify kubectl
kubectl version --client

# Verify cluster connection
kubectl get nodes
```

---

#### Option A: Using Helm Chart (Recommended)

**Step 1: Create Helm Chart**

Create `helm/dms/Chart.yaml`:

```yaml
apiVersion: v2
name: dms
description: Document Management System Helm Chart
type: application
version: 1.0.0
appVersion: "4.1.0"
```

Create `helm/dms/values.yaml`:

```yaml
# Default values for DMS deployment

replicaCount: 3

image:
  repository: dms
  pullPolicy: IfNotPresent
  tag: "4.1.0"

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: dms.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: dms-tls
      hosts:
        - dms.example.com

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    username: dmsuser
    password: changeMe123
    database: dms_prod
  primary:
    persistence:
      enabled: true
      size: 20Gi
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi

redis:
  enabled: true
  auth:
    enabled: true
    password: changeMe456
  master:
    persistence:
      enabled: true
      size: 5Gi
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

env:
  SECRET_KEY: "changeme-generate-32-byte-key"
  FLASK_ENV: "production"
  DEBUG: "False"
  API_RATE_LIMIT: "1000"
  WORKERS: "4"

persistence:
  enabled: true
  storageClass: "standard"
  accessMode: ReadWriteMany
  size: 50Gi
```

Create `helm/dms/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "dms.fullname" . }}
  labels:
    {{- include "dms.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "dms.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "dms.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: {{ include "dms.fullname" . }}
              key: secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "dms.fullname" . }}
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "dms.fullname" . }}
              key: redis-url
        {{- range $key, $value := .Values.env }}
        - name: {{ $key }}
          value: {{ $value | quote }}
        {{- end }}
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        {{- if .Values.persistence.enabled }}
        persistentVolumeClaim:
          claimName: {{ include "dms.fullname" . }}-data
        {{- else }}
        emptyDir: {}
        {{- end }}
      - name: logs
        {{- if .Values.persistence.enabled }}
        persistentVolumeClaim:
          claimName: {{ include "dms.fullname" . }}-logs
        {{- else }}
        emptyDir: {}
        {{- end }}
```

**Step 2: Install with Helm**

```bash
# Add Bitnami repo for PostgreSQL and Redis
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create namespace
kubectl create namespace dms

# Install chart
helm install dms ./helm/dms \
    --namespace dms \
    --set postgresql.auth.password=<secure_password> \
    --set redis.auth.password=<secure_password> \
    --set env.SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Check status
helm status dms -n dms

# View pods
kubectl get pods -n dms

# View services
kubectl get svc -n dms

# View ingress
kubectl get ingress -n dms
```

---

#### Option B: Manual Kubernetes Deployment

**Step 1: Create Namespace**

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dms
  labels:
    name: dms
    environment: production
```

Apply:
```bash
kubectl apply -f k8s/namespace.yaml
```

**Step 2: Create Secrets**

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dms-secrets
  namespace: dms
type: Opaque
stringData:
  SECRET_KEY: "<generate-with-python-secrets>"
  DATABASE_URL: "postgresql://dmsuser:password@postgres:5432/dms_prod"
  REDIS_URL: "redis://:password@redis:6379/0"
  POSTGRES_PASSWORD: "<secure_password>"
  REDIS_PASSWORD: "<secure_password>"
```

Apply:
```bash
kubectl apply -f k8s/secrets.yaml
```

**Step 3: Create ConfigMap**

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dms-config
  namespace: dms
data:
  FLASK_ENV: "production"
  DEBUG: "False"
  API_RATE_LIMIT: "1000"
  WORKERS: "4"
  LOG_LEVEL: "INFO"
```

Apply:
```bash
kubectl apply -f k8s/configmap.yaml
```

**Step 4: Create PostgreSQL Deployment**

Create `k8s/postgres-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: dms
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: dms_prod
        - name: POSTGRES_USER
          value: dmsuser
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: dms-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: dms
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: dms
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

Apply:
```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

**Step 5: Create Redis Deployment**

Create `k8s/redis-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: dms
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - --requirepass
        - $(REDIS_PASSWORD)
        - --appendonly
        - "yes"
        ports:
        - containerPort: 6379
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: dms-secrets
              key: REDIS_PASSWORD
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: dms
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  clusterIP: None
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: dms
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

Apply:
```bash
kubectl apply -f k8s/redis-deployment.yaml
```

**Step 6: Create DMS Application Deployment**

Create `k8s/dms-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dms-web
  namespace: dms
  labels:
    app: dms
    component: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dms
      component: web
  template:
    metadata:
      labels:
        app: dms
        component: web
    spec:
      containers:
      - name: dms
        image: dms:4.1.0
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: dms-secrets
              key: SECRET_KEY
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: dms-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: dms-secrets
              key: REDIS_URL
        envFrom:
        - configMapRef:
            name: dms-config
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: dms-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: dms-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: dms-web
  namespace: dms
spec:
  type: LoadBalancer
  selector:
    app: dms
    component: web
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dms-data-pvc
  namespace: dms
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dms-logs-pvc
  namespace: dms
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

Apply:
```bash
kubectl apply -f k8s/dms-deployment.yaml
```

**Step 7: Create Horizontal Pod Autoscaler**

Create `k8s/hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dms-web-hpa
  namespace: dms
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dms-web
  minReplicas: 2
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
      selectPolicy: Max
```

Apply:
```bash
kubectl apply -f k8s/hpa.yaml
```

**Step 8: Create Ingress**

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dms-ingress
  namespace: dms
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  tls:
  - hosts:
    - dms.example.com
    secretName: dms-tls
  rules:
  - host: dms.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dms-web
            port:
              number: 80
```

Apply:
```bash
kubectl apply -f k8s/ingress.yaml
```

**Step 9: Verify Deployment**

```bash
# Check all resources
kubectl get all -n dms

# Check pods
kubectl get pods -n dms
kubectl describe pod <pod-name> -n dms

# Check services
kubectl get svc -n dms

# Check ingress
kubectl get ingress -n dms
kubectl describe ingress dms-ingress -n dms

# Check HPA
kubectl get hpa -n dms

# View logs
kubectl logs -f deployment/dms-web -n dms

# Test health endpoint
kubectl port-forward svc/dms-web 8000:80 -n dms
curl http://localhost:8000/health
```

---

### Kubernetes Management Commands

```bash
# View all resources
kubectl get all -n dms

# View pods with more details
kubectl get pods -n dms -o wide

# Check pod logs
kubectl logs -f <pod-name> -n dms

# Execute command in pod
kubectl exec -it <pod-name> -n dms -- /bin/bash

# Scale deployment
kubectl scale deployment dms-web --replicas=5 -n dms

# Rolling update
kubectl set image deployment/dms-web dms=dms:4.1.1 -n dms

# Check rollout status
kubectl rollout status deployment/dms-web -n dms

# Rollback deployment
kubectl rollout undo deployment/dms-web -n dms

# View deployment history
kubectl rollout history deployment/dms-web -n dms

# Port forward for testing
kubectl port-forward svc/dms-web 8000:80 -n dms

# View events
kubectl get events -n dms --sort-by='.lastTimestamp'

# Delete all resources
kubectl delete namespace dms
```

---

## ☁️ 3. Cloud Platform Deployments

### AWS Deployment

#### Option 1: AWS ECS (Elastic Container Service)

**Step 1: Prerequisites**

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Install ECS CLI
sudo curl -Lo /usr/local/bin/ecs-cli \
    https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest
sudo chmod +x /usr/local/bin/ecs-cli

# Verify
aws --version
ecs-cli --version
```

**Step 2: Create ECS Cluster**

```bash
# Create cluster
aws ecs create-cluster --cluster-name dms-production

# Create VPC (if needed)
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=dms-vpc}]'

# Create subnets
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.2.0/24 --availability-zone us-east-1b
```

**Step 3: Create Task Definition**

Create `aws/ecs-task-definition.json`:

```json
{
  "family": "dms-web",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "dms-web",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/dms:4.1.0",
      "cpu": 1024,
      "memory": 2048,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:dms/secret-key"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:dms/database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dms-web",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://aws/ecs-task-definition.json
```

**Step 4: Create RDS Database**

```bash
# Create security group
aws ec2 create-security-group \
    --group-name dms-rds-sg \
    --description "DMS RDS Security Group" \
    --vpc-id <vpc-id>

# Add inbound rule for PostgreSQL
aws ec2 authorize-security-group-ingress \
    --group-id <sg-id> \
    --protocol tcp \
    --port 5432 \
    --cidr 10.0.0.0/16

# Create subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name dms-db-subnet-group \
    --db-subnet-group-description "DMS DB Subnet Group" \
    --subnet-ids <subnet-id-1> <subnet-id-2>

# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier dms-prod \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.4 \
    --master-username dmsadmin \
    --master-user-password <secure_password> \
    --allocated-storage 100 \
    --storage-type gp3 \
    --db-subnet-group-name dms-db-subnet-group \
    --vpc-security-group-ids <sg-id> \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --multi-az

# Wait for database to be available
aws rds wait db-instance-available --db-instance-identifier dms-prod

# Get endpoint
aws rds describe-db-instances \
    --db-instance-identifier dms-prod \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text
```

**Step 5: Create Application Load Balancer**

```bash
# Create ALB
aws elbv2 create-load-balancer \
    --name dms-alb \
    --subnets <subnet-id-1> <subnet-id-2> \
    --security-groups <sg-id> \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4

# Create target group
aws elbv2 create-target-group \
    --name dms-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id <vpc-id> \
    --target-type ip \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn <alb-arn> \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=<tg-arn>
```

**Step 6: Create ECS Service**

```bash
# Create service
aws ecs create-service \
    --cluster dms-production \
    --service-name dms-web \
    --task-definition dms-web:1 \
    --desired-count 3 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<subnet-id-1>,<subnet-id-2>],securityGroups=[<sg-id>],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<tg-arn>,containerName=dms-web,containerPort=8000" \
    --health-check-grace-period-seconds 60

# Enable auto-scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/dms-production/dms-web \
    --min-capacity 2 \
    --max-capacity 10

aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/dms-production/dms-web \
    --policy-name dms-cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://aws/scaling-policy.json
```

Create `aws/scaling-policy.json`:

```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleOutCooldown": 60,
  "ScaleInCooldown": 300
}
```

**Step 7: Verify**

```bash
# Check service status
aws ecs describe-services \
    --cluster dms-production \
    --services dms-web

# Check tasks
aws ecs list-tasks --cluster dms-production --service-name dms-web

# Get ALB DNS name
aws elbv2 describe-load-balancers \
    --names dms-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text

# Test
curl http://<alb-dns-name>/health
```

---

#### Option 2: AWS EKS (Elastic Kubernetes Service)

**Step 1: Install eksctl**

```bash
# Install eksctl
curl --silent --location "https://github.com/weks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Verify
eksctl version
```

**Step 2: Create EKS Cluster**

Create `aws/eks-cluster.yaml`:

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: dms-production
  region: us-east-1
  version: "1.28"

managedNodeGroups:
  - name: dms-nodes
    instanceType: t3.medium
    minSize: 2
    maxSize: 10
    desiredCapacity: 3
    volumeSize: 50
    ssh:
      allow: false
    labels:
      role: worker
    tags:
      Environment: production
      Project: dms

iam:
  withOIDC: true
```

Create cluster:

```bash
# Create EKS cluster (takes 15-20 minutes)
eksctl create cluster -f aws/eks-cluster.yaml

# Verify kubectl access
kubectl get nodes

# Install AWS Load Balancer Controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller/crds?ref=master"

helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=dms-production \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller
```

**Step 3: Deploy DMS to EKS**

Use the Kubernetes deployment files from [Section 2: Kubernetes Deployment](#kubernetes-single-cluster) with AWS-specific modifications:

```bash
# Deploy to EKS
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/dms-deployment.yaml
kubectl apply -f k8s/hpa.yaml

# Create AWS-specific ingress
kubectl apply -f aws/eks-ingress.yaml
```

Create `aws/eks-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dms-ingress
  namespace: dms
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:<account-id>:certificate/<cert-id>
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/healthcheck-path: /health
spec:
  rules:
  - host: dms.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dms-web
            port:
              number: 80
```

**Step 4: Verify**

```bash
# Get ingress address
kubectl get ingress -n dms

# Test
curl https://dms.example.com/health
```

---

### Azure Deployment

#### Azure AKS (Azure Kubernetes Service)

**Step 1: Prerequisites**

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Set subscription
az account set --subscription <subscription-id>
```

**Step 2: Create Resource Group**

```bash
az group create \
    --name dms-prod \
    --location eastus
```

**Step 3: Create AKS Cluster**

```bash
# Create AKS cluster
az aks create \
    --resource-group dms-prod \
    --name dms-aks \
    --node-count 3 \
    --node-vm-size Standard_D2s_v3 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --network-plugin azure \
    --enable-managed-identity \
    --enable-cluster-autoscaler \
    --min-count 2 \
    --max-count 10

# Get credentials
az aks get-credentials \
    --resource-group dms-prod \
    --name dms-aks

# Verify
kubectl get nodes
```

**Step 4: Create Azure Database for PostgreSQL**

```bash
az postgres flexible-server create \
    --resource-group dms-prod \
    --name dms-db \
    --location eastus \
    --admin-user dmsadmin \
    --admin-password <secure_password> \
    --sku-name Standard_D2s_v3 \
    --tier GeneralPurpose \
    --storage-size 128 \
    --version 15

# Create database
az postgres flexible-server db create \
    --resource-group dms-prod \
    --server-name dms-db \
    --database-name dms_prod

# Configure firewall (allow Azure services)
az postgres flexible-server firewall-rule create \
    --resource-group dms-prod \
    --name dms-db \
    --rule-name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Get connection string
az postgres flexible-server show \
    --resource-group dms-prod \
    --name dms-db \
    --query "fullyQualifiedDomainName" \
    --output tsv
```

**Step 5: Create Azure Cache for Redis**

```bash
az redis create \
    --resource-group dms-prod \
    --name dms-redis \
    --location eastus \
    --sku Standard \
    --vm-size c1 \
    --enable-non-ssl-port

# Get connection details
az redis show \
    --resource-group dms-prod \
    --name dms-redis \
    --query "[hostName,sslPort]" \
    --output tsv

# Get access keys
az redis list-keys \
    --resource-group dms-prod \
    --name dms-redis
```

**Step 6: Deploy DMS to AKS**

Use Kubernetes deployment files from [Section 2](#kubernetes-single-cluster):

```bash
# Deploy to AKS
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/dms-deployment.yaml
kubectl apply -f k8s/hpa.yaml

# Create Azure-specific ingress
kubectl apply -f azure/aks-ingress.yaml
```

Create `azure/aks-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dms-ingress
  namespace: dms
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - dms.example.com
    secretName: dms-tls
  rules:
  - host: dms.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dms-web
            port:
              number: 80
```

**Step 7: Verify**

```bash
# Check deployment
kubectl get all -n dms

# Get ingress IP
kubectl get ingress -n dms

# Test
curl https://dms.example.com/health
```

---

### GCP Deployment

#### GCP GKE (Google Kubernetes Engine)

**Step 1: Prerequisites**

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize
gcloud init

# Set project
gcloud config set project <project-id>
```

**Step 2: Create GKE Cluster**

```bash
# Create GKE cluster
gcloud container clusters create dms-production \
    --zone us-central1-a \
    --num-nodes 3 \
    --machine-type n1-standard-2 \
    --enable-autoscaling \
    --min-nodes 2 \
    --max-nodes 10 \
    --enable-autorepair \
    --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials dms-production --zone us-central1-a

# Verify
kubectl get nodes
```

**Step 3: Create Cloud SQL Instance (PostgreSQL)**

```bash
# Create Cloud SQL instance
gcloud sql instances create dms-db \
    --database-version=POSTGRES_15 \
    --tier=db-custom-2-7680 \
    --region=us-central1 \
    --backup \
    --backup-start-time=03:00

# Create database
gcloud sql databases create dms_prod --instance=dms-db

# Create user
gcloud sql users create dmsuser \
    --instance=dms-db \
    --password=<secure_password>

# Get connection name
gcloud sql instances describe dms-db \
    --format="value(connectionName)"
```

**Step 4: Create Memorystore (Redis)**

```bash
# Create Redis instance
gcloud redis instances create dms-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0

# Get connection details
gcloud redis instances describe dms-redis \
    --region=us-central1 \
    --format="value(host,port)"
```

**Step 5: Deploy DMS to GKE**

Use Kubernetes deployment files from [Section 2](#kubernetes-single-cluster):

```bash
# Deploy to GKE
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/dms-deployment.yaml
kubectl apply -f k8s/hpa.yaml

# Create GCP-specific ingress
kubectl apply -f gcp/gke-ingress.yaml
```

Create `gcp/gke-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dms-ingress
  namespace: dms
  annotations:
    kubernetes.io/ingress.class: "gce"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    ingress.gcp.kubernetes.io/pre-shared-cert: "dms-ssl-cert"
spec:
  tls:
  - hosts:
    - dms.example.com
    secretName: dms-tls
  rules:
  - host: dms.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dms-web
            port:
              number: 80
```

**Step 6: Verify**

```bash
# Check deployment
kubectl get all -n dms

# Get ingress IP
kubectl get ingress -n dms

# Test
curl https://dms.example.com/health
```

---

## 🔧 4. Manual Deployment

### Ubuntu/Debian Production Server

**For on-premises or custom deployments.**

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.11 python3.11-venv python3.11-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    build-essential \
    libpq-dev

# Create system user
sudo useradd -m -s /bin/bash dms
```

#### Step 2: Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE dms_prod;
CREATE USER dmsuser WITH ENCRYPTED PASSWORD '<secure_password>';
GRANT ALL PRIVILEGES ON DATABASE dms_prod TO dmsuser;
\q

# Configure PostgreSQL for network access (if needed)
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = '*'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: host    all             all             0.0.0.0/0               md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Step 3: Setup Redis

```bash
# Configure Redis
sudo nano /etc/redis/redis.conf
# Uncomment and set:
# requirepass <secure_password>
# maxmemory 512mb
# maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

#### Step 4: Deploy Application

```bash
# Switch to dms user
sudo su - dms

# Clone repository
git clone https://github.com/svend4/daten20.git /home/dms/dms
cd /home/dms/dms

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://dmsuser:<password>@localhost:5432/dms_prod
REDIS_URL=redis://:<password>@localhost:6379/0
WORKERS=4
EOF

# Initialize database
python -c "from src.core.database import Database; Database().init_db()"

# Create admin user
python dms-admin.py users create \
    --username admin \
    --email admin@example.com \
    --password <secure_password> \
    --role admin

# Test application
python src/web_app.py
# Press Ctrl+C to stop
```

#### Step 5: Configure Supervisor

```bash
# Exit dms user
exit

# Create supervisor config
sudo nano /etc/supervisor/conf.d/dms.conf
```

Add:

```ini
[program:dms-web]
command=/home/dms/dms/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 --worker-class gthread --threads 2 --timeout 120 src.web_app:app
directory=/home/dms/dms
user=dms
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/dms/dms/logs/web.log
environment=PATH="/home/dms/dms/venv/bin"

[program:dms-worker]
command=/home/dms/dms/venv/bin/celery -A src.tasks worker --loglevel=info
directory=/home/dms/dms
user=dms
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/dms/dms/logs/worker.log
environment=PATH="/home/dms/dms/venv/bin"
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start services
sudo supervisorctl start dms-web
sudo supervisorctl start dms-worker

# Check status
sudo supervisorctl status
```

#### Step 6: Configure Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/dms
```

Add:

```nginx
upstream dms_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name dms.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dms.example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/dms.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dms.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 100M;

    # Logging
    access_log /var/log/nginx/dms_access.log;
    error_log /var/log/nginx/dms_error.log;

    # Static files
    location /static/ {
        alias /home/dms/dms/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to application
    location / {
        proxy_pass http://dms_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://dms_app;
        access_log off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dms /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Step 7: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d dms.example.com

# Test auto-renewal
sudo certbot renew --dry-run

# Restart Nginx
sudo systemctl restart nginx
```

#### Step 8: Verify

```bash
# Check services
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Test application
curl https://dms.example.com/health

# View logs
sudo tail -f /home/dms/dms/logs/web.log
sudo tail -f /var/log/nginx/dms_access.log
```

---

## 🔐 5. Environment Configuration

### Production Environment Variables

Create comprehensive `.env.production`:

```bash
# ============================================
# DMS Production Configuration
# ============================================

# Security
SECRET_KEY="<generate-with-python-secrets-token-hex-32>"
FLASK_ENV="production"
DEBUG="False"
TESTING="False"

# Database
DATABASE_URL="postgresql://dmsuser:<password>@db.example.com:5432/dms_prod"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=False

# Redis Cache
REDIS_URL="redis://:<password>@redis.example.com:6379/0"
REDIS_POOL_SIZE=10
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# API Configuration
API_RATE_LIMIT=1000
API_KEY_EXPIRY_DAYS=90
API_MAX_REQUESTS_PER_HOUR=10000
API_ENABLE_CORS=True
API_CORS_ORIGINS="https://example.com,https://app.example.com"

# Authentication
JWT_SECRET_KEY="<generate-different-key>"
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE="Lax"

# File Storage
UPLOAD_FOLDER="/app/data/uploads"
MAX_CONTENT_LENGTH=104857600  # 100 MB
ALLOWED_EXTENSIONS="pdf,doc,docx,txt,jpg,png"

# Worker Configuration
WORKERS=4
THREADS=2
WORKER_CLASS="gthread"
TIMEOUT=120
KEEPALIVE=5

# Email (SMTP)
MAIL_SERVER="smtp.example.com"
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME="notifications@example.com"
MAIL_PASSWORD="<email_password>"
MAIL_DEFAULT_SENDER="DMS <noreply@example.com>"

# Logging
LOG_LEVEL="INFO"
LOG_FILE="/app/logs/__main__.log"
LOG_MAX_BYTES=10485760  # 10 MB
LOG_BACKUP_COUNT=5

# Monitoring
SENTRY_DSN="https://xxx@sentry.io/xxx"
SENTRY_ENVIRONMENT="production"
SENTRY_TRACES_SAMPLE_RATE=0.1

# Feature Flags
ENABLE_ANALYTICS=True
ENABLE_ML_FEATURES=True
ENABLE_WEBHOOKS=True
ENABLE_NOTIFICATIONS=True

# Performance
CACHE_DEFAULT_TIMEOUT=300
CACHE_THRESHOLD=1000
ASYNC_POOL_SIZE=10

# Security
ENABLE_RATE_LIMITING=True
ENABLE_CSRF_PROTECTION=True
ENABLE_IP_WHITELIST=False
TRUSTED_PROXIES="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

# Backup
BACKUP_ENABLED=True
BACKUP_SCHEDULE="0 3 * * *"  # 3 AM daily
BACKUP_RETENTION_DAYS=30
BACKUP_DESTINATION="/backups"

# Integrations
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx"
WEBHOOK_TIMEOUT=10
WEBHOOK_RETRY_ATTEMPTS=3
```

### Generating Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (different from SECRET_KEY)
python -c "import secrets; print(secrets.token_hex(32))"

# Generate API key
python -c "import secrets; print('dms_' + secrets.token_urlsafe(32))"

# Generate bcrypt hash for password
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
```

---

## 🗄️ 6. Database Setup

### PostgreSQL Production Configuration

#### Recommended Settings

Edit `postgresql.conf`:

```ini
# Memory Settings
shared_buffers = 4GB                # 25% of RAM
effective_cache_size = 12GB         # 75% of RAM
maintenance_work_mem = 1GB
work_mem = 50MB

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_wal_size = 4GB
min_wal_size = 1GB

# Planner Settings
random_page_cost = 1.1              # For SSD
effective_io_concurrency = 200      # For SSD

# Parallelism
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_min_duration_statement = 1000   # Log queries > 1 second

# Connection Settings
max_connections = 200
```

#### Database Initialization

```bash
# Connect to database
psql -h localhost -U dmsuser -d dms_prod

# Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

# Create indexes for performance
CREATE INDEX CONCURRENTLY idx_services_created_at ON services(created_at);
CREATE INDEX CONCURRENTLY idx_documents_status ON documents(status);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

# Analyze tables
ANALYZE;

# Exit
\q
```

#### Database Backup Script

Create `/home/dms/backup-database.sh`:

```bash
#!/bin/bash

# Configuration
DB_NAME="dms_prod"
DB_USER="dmsuser"
DB_HOST="localhost"
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dms_backup_$DATE.sql.gz"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting backup at $(date)"
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    echo "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "Backup failed!"
    exit 1
fi

# Remove old backups
find $BACKUP_DIR -name "dms_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "Removed backups older than $RETENTION_DAYS days"

echo "Backup completed at $(date)"
```

Make executable and schedule:

```bash
chmod +x /home/dms/backup-database.sh

# Add to crontab for daily backup at 3 AM
crontab -e
# Add: 0 3 * * * /home/dms/backup-database.sh >> /home/dms/logs/backup.log 2>&1
```

---

## 🔒 7. SSL/TLS Configuration

### Let's Encrypt (Free SSL)

#### For Docker Deployment

Add to `docker-compose.production.yml`:

```yaml
services:
  certbot:
    image: certbot/certbot
    container_name: dms-certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - ./nginx/certbot-webroot:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

Update nginx configuration to serve ACME challenge:

```nginx
location /.well-known/acme-challenge/ {
    root /var/www/certbot;
}
```

Obtain certificate:

```bash
# First time certificate request
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email admin@example.com \
    --agree-tos \
    --no-eff-email \
    -d dms.example.com

# Reload nginx
docker-compose exec nginx nginx -s reload
```

#### For Manual Deployment

Already covered in [Step 7 of Manual Deployment](#step-7-setup-ssl-with-lets-encrypt)

---

## 🛡️ 8. Security Hardening

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable

# Check status
sudo ufw status verbose
```

### Fail2ban for Brute Force Protection

```bash
# Install fail2ban
sudo apt install -y fail2ban

# Create jail configuration
sudo nano /etc/fail2ban/jail.local
```

Add:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/dms_error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/dms_error.log

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban

# Check status
sudo fail2ban-client status
```

### Security Headers

Already configured in [Nginx configuration](#step-6-configure-nginx)

### Database Security

```bash
# PostgreSQL security
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Use md5 or scram-sha-256 for authentication
# Limit connections by IP

# Redis security
sudo nano /etc/redis/redis.conf
# Set requirepass
# Disable dangerous commands:
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

---

## 🔄 9. CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy-production.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  DOCKER_IMAGE: dms
  DOCKER_TAG: ${{ github.sha }}
  K8S_NAMESPACE: dms

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}
            ${{ env.DOCKER_IMAGE }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-kubernetes:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Install kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Update deployment
        run: |
          export KUBECONFIG=kubeconfig
          kubectl set image deployment/dms-web \
            dms=${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }} \
            -n ${{ env.K8S_NAMESPACE }}

      - name: Wait for rollout
        run: |
          export KUBECONFIG=kubeconfig
          kubectl rollout status deployment/dms-web \
            -n ${{ env.K8S_NAMESPACE }} \
            --timeout=5m

      - name: Verify deployment
        run: |
          export KUBECONFIG=kubeconfig
          kubectl get pods -n ${{ env.K8S_NAMESPACE }}
          kubectl get svc -n ${{ env.K8S_NAMESPACE }}

  notify:
    needs: [test, build, deploy-kubernetes]
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Send notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          text: 'Deployment ${{ job.status }}: ${{ github.repository }}@${{ github.sha }}'
```

### GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: registry.gitlab.com/$CI_PROJECT_PATH
  K8S_NAMESPACE: dms

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=src --cov-report=xml
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA -t $DOCKER_IMAGE:latest .
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
    - docker push $DOCKER_IMAGE:latest
  only:
    - main

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  before_script:
    - echo "$KUBE_CONFIG" > kubeconfig
    - export KUBECONFIG=kubeconfig
  script:
    - kubectl set image deployment/dms-web dms=$DOCKER_IMAGE:$CI_COMMIT_SHA -n $K8S_NAMESPACE
    - kubectl rollout status deployment/dms-web -n $K8S_NAMESPACE --timeout=5m
  only:
    - main
  environment:
    name: production
    url: https://dms.example.com
```

---

## 📊 10. Monitoring & Logging

### Prometheus + Grafana

#### Deploy Monitoring Stack (Kubernetes)

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set grafana.adminPassword=<secure_password>

# Port forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Username: admin
# Password: <secure_password>
```

#### Application Metrics

Add to `src/monitoring.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response
import time

# Metrics
request_count = Counter('dms_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('dms_request_duration_seconds', 'Request duration')
active_connections = Gauge('dms_active_connections', 'Active connections')
database_size = Gauge('dms_database_size_bytes', 'Database size in bytes')

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_duration.observe(duration)
    request_count.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    return response
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

#### Docker Compose ELK

Create `docker-compose.elk.yml`:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_URL: http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

---

## 📈 11. Scaling Strategies

### Horizontal Scaling (Kubernetes)

```bash
# Manual scaling
kubectl scale deployment dms-web --replicas=10 -n dms

# Auto-scaling based on CPU
kubectl autoscale deployment dms-web \
    --cpu-percent=70 \
    --min=2 \
    --max=10 \
    -n dms

# Check HPA status
kubectl get hpa -n dms
```

### Vertical Scaling

Update resource limits in deployment:

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 2000m
    memory: 4Gi
```

### Database Scaling

#### Read Replicas (PostgreSQL)

```bash
# Create read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier dms-prod-replica \
    --source-db-instance-identifier dms-prod \
    --db-instance-class db.t3.medium
```

Update application to use read replica for queries:

```python
# Use read replica for SELECT queries
READ_DATABASE_URL = "postgresql://user:pass@replica.example.com:5432/dms_prod"
WRITE_DATABASE_URL = "postgresql://user:pass@primary.example.com:5432/dms_prod"
```

---

## 💾 12. Backup & Recovery

### Automated Backup Script

Create `/opt/dms/backup.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups/dms"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting DMS backup at $(date)"

# 1. Database backup
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U dmsuser dms_prod | \
    gzip > $BACKUP_DIR/database_$DATE.sql.gz

# 2. Application data backup
echo "Backing up application data..."
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/dms/data/

# 3. Configuration backup
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/dms/config/ /opt/dms/.env

# 4. Remove old backups
echo "Removing backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

# 5. Upload to S3 (optional)
# aws s3 sync $BACKUP_DIR s3://dms-backups/

echo "Backup completed at $(date)"

# Send notification
curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"DMS backup completed successfully\"}"
```

Schedule:

```bash
chmod +x /opt/dms/backup.sh
crontab -e
# Add: 0 3 * * * /opt/dms/backup.sh >> /var/log/dms-backup.log 2>&1
```

### Recovery Procedure

```bash
# 1. Stop services
docker-compose down

# 2. Restore database
gunzip < /backups/dms/database_20260116_030000.sql.gz | \
    docker-compose exec -T postgres psql -U dmsuser dms_prod

# 3. Restore data
tar -xzf /backups/dms/data_20260116_030000.tar.gz -C /

# 4. Restore configuration
tar -xzf /backups/dms/config_20260116_030000.tar.gz -C /

# 5. Start services
docker-compose up -d

# 6. Verify
curl http://localhost:5000/health
```

---

## 🔄 13. High Availability Setup

### Load Balancer Configuration

#### HAProxy Configuration

Create `/etc/haproxy/haproxy.cfg`:

```
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend dms_frontend
    bind *:80
    bind *:443 ssl crt /etc/haproxy/certs/dms.pem
    redirect scheme https code 301 if !{ ssl_fc }

    acl is_api path_beg /api
    acl is_health path /health

    use_backend dms_api if is_api
    use_backend dms_web if !is_api

    default_backend dms_web

backend dms_web
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200

    server web1 10.0.1.10:8000 check
    server web2 10.0.1.11:8000 check
    server web3 10.0.1.12:8000 check

backend dms_api
    balance roundrobin
    option httpchk GET /api/v1/health
    http-check expect status 200

    server api1 10.0.1.20:8000 check
    server api2 10.0.1.21:8000 check
    server api3 10.0.1.22:8000 check

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
```

---

## ⚡ 14. Performance Optimization

### Application Performance

```python
# Enable caching
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/v1/services')
@cache.cached(timeout=60, query_string=True)
def get_services():
    # Will be cached for 60 seconds
    pass
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX CONCURRENTLY idx_services_user_id ON services(user_id);
CREATE INDEX CONCURRENTLY idx_documents_created_at ON documents(created_at);

-- Analyze tables
ANALYZE services;
ANALYZE documents;

-- Vacuum
VACUUM ANALYZE;
```

### CDN Configuration

Use CloudFlare or AWS CloudFront for static assets:

```nginx
# Cache static files longer
location /static/ {
    alias /app/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 🔧 15. Troubleshooting

### Common Issues

#### Issue 1: Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n dms

# Check logs
kubectl logs <pod-name> -n dms

# Common fixes:
# - Check resource limits
# - Check secrets/configmaps
# - Check image pull policy
```

#### Issue 2: Database Connection Errors

```bash
# Test database connectivity
docker-compose exec web python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host:5432/db')
conn = engine.connect()
print('Connected!')
conn.close()
"

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection string
echo $DATABASE_URL
```

#### Issue 3: High Memory Usage

```bash
# Check memory usage
docker stats

# Reduce workers
# In .env: WORKERS=2

# Enable memory limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 2G
```

For more troubleshooting, see [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)

---

## 📚 Related Documentation

- **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)** - Complete troubleshooting reference
- **[CLI Tools Guide](user-guides/CLI_TOOLS_MASTER_GUIDE.md)** - CLI tools documentation
- **[API Documentation](API_DOCUMENTATION_GUIDE.md)** - API usage guide
- **[Architecture](ARCHITECTURE.md)** - System architecture
- **[Security Guide](SECURITY_GUIDE.md)** - Security best practices

---

## 📝 Changelog

### Version 4.1.0 (2026-01-16) - Phase 4 Task 44 ✅

- ✅ Created comprehensive deployment guide (1,500+ lines)
- ✅ Docker deployment (development + production)
- ✅ Kubernetes deployment (Helm + manual)
- ✅ Cloud platform guides (AWS ECS/EKS, Azure AKS, GCP GKE)
- ✅ Manual deployment (Ubuntu/Debian)
- ✅ CI/CD integration (GitHub Actions, GitLab CI)
- ✅ Monitoring setup (Prometheus, Grafana, ELK)
- ✅ High availability configuration
- ✅ Backup and recovery procedures
- ✅ Security hardening
- ✅ Performance optimization
- ✅ Troubleshooting section

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Maintained by:** DMS Development Team
**Status:** Production Ready

For deployment support, visit: https://github.com/svend4/daten20/issues
