# 🚀 Production Deployment Guide

**daten20 Document Management System**

Complete guide for deploying daten20 to production environment with best practices for security, performance, and reliability.

---

## Deployment Checklist

✅ Generate secret keys
✅ Configure SSL/TLS
✅ Setup reverse proxy (Nginx)
✅ Configure database (PostgreSQL)
✅ Setup Redis cache
✅ Enable monitoring (Sentry, Prometheus)
✅ Configure backups
✅ Security hardening
✅ Performance optimization

---

## Quick Start

```bash
# 1. Install on server
git clone https://github.com/svend4/daten20.git /opt/daten20
cd /opt/daten20

# 2. Setup environment
cp config/production.env.example .env
# Edit .env with production values

# 3. Install dependencies
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup systemd service
sudo cp config/daten20.service /etc/systemd/system/
sudo systemctl enable daten20
sudo systemctl start daten20

# 5. Configure Nginx
sudo cp config/nginx-production.conf /etc/nginx/sites-available/daten20
sudo ln -s /etc/nginx/sites-available/daten20 /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

See full documentation for detailed instructions.

---

**Status:** ✅ Production Ready
**Version:** 1.0.0
