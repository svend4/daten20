# 📋 Production Deployment Checklist

Complete checklist for deploying DMS to production.

---

## Pre-Deployment

### Security
- [ ] Generate strong `SECRET_KEY` (64+ characters)
- [ ] Change all default passwords
- [ ] Review and update `.env` with production values
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Enable 2FA for all admin users
- [ ] Review file permissions (640 for .env, 750 for directories)
- [ ] Disable debug mode (`DEBUG=false`)

### Configuration
- [ ] Set `FLASK_ENV=production`
- [ ] Configure database (PostgreSQL recommended for production)
- [ ] Set up Redis for caching
- [ ] Configure SMTP for email notifications
- [ ] Set appropriate session timeouts
- [ ] Configure CORS allowed origins
- [ ] Set up logging levels and rotation

### Infrastructure
- [ ] Provision servers/containers
- [ ] Set up load balancer
- [ ] Configure DNS
- [ ] Obtain SSL/TLS certificates
- [ ] Set up CDN (if needed)
- [ ] Configure backup storage

---

## Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3-pip nginx supervisor redis-server

# Create application user
sudo useradd -m -s /bin/bash dms
```

### 2. Application Deployment
```bash
# Clone repository
cd /home/dms
sudo -u dms git clone <repo-url> app
cd app

# Create virtual environment
sudo -u dms python3.11 -m venv venv
sudo -u dms venv/bin/pip install -r requirements.txt

# Configure environment
sudo -u dms cp .env.example .env
# Edit .env with production values

# Initialize database
sudo -u dms venv/bin/python -c "from src.core.database import Database; Database()"

# Create admin user
sudo -u dms venv/bin/python dms-admin.py users create
```

### 3. Configure Supervisor
```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/dms.conf
```

```ini
[program:dms]
command=/home/dms/app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 src.web_app:app
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
```

### 4. Configure Nginx
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/dms
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/dms/app/web/static/;
        expires 30d;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Configure SSL
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## Post-Deployment

### Monitoring Setup
- [ ] Set up Prometheus for metrics
- [ ] Configure Grafana dashboards
- [ ] Set up log aggregation (ELK/Loki)
- [ ] Configure uptime monitoring
- [ ] Set up alerts for errors and downtime

### Backup Setup
```bash
# Configure automated backups
# Add to crontab for dms user
crontab -e
```

```cron
# Daily backup at 2 AM
0 2 * * * cd /home/dms/app && /home/dms/app/venv/bin/python dms-admin.py backup create

# Weekly database backup
0 3 * * 0 pg_dump -U dms_user dms_production > /home/dms/backups/weekly_$(date +\%Y\%m\%d).sql
```

- [ ] Test backup restoration
- [ ] Configure off-site backup storage
- [ ] Set up backup monitoring/alerts

### Security Hardening
```bash
# Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Restrict file permissions
sudo chmod 640 /home/dms/app/.env
sudo chmod 750 /home/dms/app/data
sudo chmod 750 /home/dms/app/logs

# Set up fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

- [ ] Enable 2FA for all admin users
- [ ] Configure API rate limiting
- [ ] Set up audit logging
- [ ] Review and restrict user permissions
- [ ] Implement IP whitelisting (if applicable)

### Performance Optimization
- [ ] Enable Redis caching
- [ ] Configure CDN for static files
- [ ] Optimize database indexes
- [ ] Enable gzip compression in Nginx
- [ ] Set up connection pooling
- [ ] Configure appropriate worker counts

---

## Testing

### Functional Testing
- [ ] Test user login/logout
- [ ] Test service creation/editing
- [ ] Test document generation
- [ ] Test email notifications
- [ ] Test file uploads/downloads
- [ ] Test API endpoints
- [ ] Test GraphQL queries
- [ ] Test WebSocket connections

### Security Testing
- [ ] Run security scan (bandit, safety)
- [ ] Test HTTPS enforcement
- [ ] Verify CORS configuration
- [ ] Test rate limiting
- [ ] Verify authentication flows
- [ ] Test 2FA functionality
- [ ] Check audit logging

### Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 http://your-domain.com/

# Or with wrk
wrk -t12 -c400 -d30s http://your-domain.com/
```

- [ ] Test under expected load
- [ ] Test database performance
- [ ] Test caching effectiveness
- [ ] Monitor resource usage
- [ ] Test backup/restore time

---

## Monitoring & Maintenance

### Daily
- [ ] Check application logs for errors
- [ ] Monitor system resources
- [ ] Review security logs
- [ ] Check backup completion

### Weekly
- [ ] Review audit logs
- [ ] Analyze performance metrics
- [ ] Check disk space usage
- [ ] Review user activity

### Monthly
- [ ] Update dependencies (security patches)
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Review and update documentation
- [ ] Security audit
- [ ] Performance optimization review

---

## Rollback Plan

### If deployment fails:

1. **Stop new version**
   ```bash
   sudo supervisorctl stop dms
   ```

2. **Restore previous version**
   ```bash
   cd /home/dms/app
   git checkout <previous-tag>
   ```

3. **Restore database (if needed)**
   ```bash
   python dms-admin.py backup restore <backup-file>
   ```

4. **Restart application**
   ```bash
   sudo supervisorctl start dms
   ```

---

## Documentation

- [ ] Document deployment procedure
- [ ] Document backup/restore procedure
- [ ] Document monitoring setup
- [ ] Document troubleshooting steps
- [ ] Create runbooks for common issues
- [ ] Document emergency procedures

---

## Compliance & Legal

- [ ] Review data privacy requirements
- [ ] Implement GDPR compliance (if applicable)
- [ ] Set up data retention policies
- [ ] Configure audit logging for compliance
- [ ] Review terms of service
- [ ] Update privacy policy

---

## Go-Live Checklist

**Final checks before going live:**

- [ ] All pre-deployment items complete
- [ ] All deployment steps executed successfully
- [ ] All post-deployment items complete
- [ ] All tests passing
- [ ] Monitoring and alerts configured
- [ ] Backups tested and verified
- [ ] Documentation complete and accessible
- [ ] Team trained on new system
- [ ] Support procedures in place
- [ ] Rollback plan tested and ready

---

## Support Contacts

- **System Admin:** _______________________
- **Database Admin:** _____________________
- **Security Team:** ______________________
- **On-call Engineer:** ___________________

---

**Production deployment complete!** ✅

Remember to:
- Monitor logs closely for first 24-48 hours
- Have rollback plan ready
- Keep communication channels open
- Document any issues encountered

---

Last updated: January 2026
Version: 2.2.0
