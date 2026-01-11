# 🚀 Quick Start Guide

Get started with Document Management System in 5 minutes!

---

## Method 1: Automated Setup (Recommended)

### Step 1: Clone & Setup
```bash
git clone <repository-url>
cd daten20

# Run automated setup
python setup.py
```

The setup script will:
- ✅ Check Python version
- ✅ Create necessary directories
- ✅ Generate `.env` file with secure keys
- ✅ Install dependencies
- ✅ Initialize database
- ✅ Create admin user

### Step 2: Start Application
```bash
# Development
python src/web_app.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 src.web_app:app
```

### Step 3: Access
- **Web UI:** http://localhost:5000
- **API Docs:** http://localhost:5000/apidocs
- **GraphQL:** http://localhost:5000/graphql
- **Metrics:** http://localhost:5000/metrics

---

## Method 2: Docker (Fastest)

### Step 1: Start with Docker
```bash
# Copy environment template
cp .env.example .env

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 2: Create Admin User
```bash
docker-compose exec web python dms-admin.py users create
```

### Step 3: Access
- **Web UI:** http://localhost:5000

---

## Method 3: Manual Setup

### Step 1: Prerequisites
```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # Set SECRET_KEY and other settings
```

### Step 3: Initialize
```bash
# Create directories
mkdir -p data/db data/exports logs backups

# Initialize database
python -c "from src.core.database import Database; Database()"

# Create admin user
python dms-admin.py users create \
  --username admin \
  --email admin@example.com \
  --role admin
```

### Step 4: Run
```bash
python src/web_app.py
```

---

## First Steps After Installation

### 1. Login
- Navigate to http://localhost:5000
- Login with your admin credentials

### 2. Create Your First Service
```bash
# Via CLI
python src/interactive_editor.py

# Via Web UI
# Navigate to "Services" → "Create New"

# Via API
curl -X POST http://localhost:5000/api/v1/services \
  -H "Content-Type: application/json" \
  -d '{"service_name": "Shopping Assistance", "region": "Bavaria"}'
```

### 3. Enable 2FA (Recommended)
```bash
# For your admin account
python dms-admin.py users enable-2fa 1

# Or via Web UI
# Navigate to Profile → Security → Enable 2FA
```

### 4. Setup Automated Backups
```python
# In Python
from src.core.backup import get_backup_manager, BackupScheduler

mgr = get_backup_manager()
scheduler = BackupScheduler(mgr)
scheduler.schedule_daily(time_str="02:00")  # 2 AM daily
scheduler.start()
```

---

## Common Tasks

### Create Backup
```bash
python dms-admin.py backup create
```

### View Audit Log
```bash
python dms-admin.py audit view --limit 50
```

### List Users
```bash
python dms-admin.py users list
```

### Check System Status
```bash
python dms-admin.py system status
```

### Run Health Check
```bash
python dms-admin.py system check
```

---

## Development Workflow

### 1. Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_financial_calculator.py -v
```

### 2. Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

### 3. Generate Documentation
```bash
# API documentation automatically available at /apidocs
# GraphQL documentation at /graphql
```

---

## Production Deployment

### Quick Production Deployment
```bash
# 1. Update .env for production
FLASK_ENV=production
DEBUG=false
SECRET_KEY=<generated-secret>

# 2. Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  src.web_app:app

# 3. Or with Docker
docker-compose --profile with-redis --profile with-nginx up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive production guide.

---

## Kubernetes Deployment

### Deploy to K8s
```bash
# Apply configurations
kubectl apply -f k8s/base/

# Check status
kubectl get pods -l app=dms
kubectl get services

# View logs
kubectl logs -f deployment/dms-app
```

---

## Troubleshooting

### Application won't start
```bash
# Check logs
tail -f logs/app.log

# Run health check
python dms-admin.py system check

# Verify dependencies
pip install -r requirements.txt
```

### Database errors
```bash
# Reinitialize database
rm data/db/*.db
python -c "from src.core.database import Database; Database()"
```

### Port already in use
```bash
# Change port in .env
APP_PORT=5001

# Or specify when running
python src/web_app.py --port 5001
```

---

## Next Steps

- 📖 Read [README.md](README.md) for detailed documentation
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- 📝 Check [CHANGELOG_v2.2.md](CHANGELOG_v2.2.md) for latest features
- 🏗️ Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

## Getting Help

- **CLI Help:** `python dms-admin.py --help`
- **System Status:** `python dms-admin.py system status`
- **Audit Logs:** `python dms-admin.py audit view`
- **Documentation:** See `/docs` directory

---

**Ready to go!** 🎉
