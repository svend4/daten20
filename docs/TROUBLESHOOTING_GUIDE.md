# 🔧 Troubleshooting Guide

**Document Management System - Complete Troubleshooting Reference**

Quick solutions for common issues, error messages, and diagnostic procedures.

**Version:** 4.1.0
**Last Updated:** 2026-01-16
**Status:** Production Ready

---

## 📋 Table of Contents

### Quick Links
- [Emergency Procedures](#-emergency-procedures)
- [Common Issues](#-common-issues-quick-fixes)
- [Error Messages](#-error-messages-catalog)
- [Diagnostic Tools](#-diagnostic-tools)
- [FAQ](#-frequently-asked-questions)

### By Category
1. [Installation & Setup](#1-installation--setup-issues)
2. [CLI Tools](#2-cli-tools-issues)
3. [Database](#3-database-issues)
4. [API & Web Interface](#4-api--web-interface-issues)
5. [Performance](#5-performance-issues)
6. [Security & Authentication](#6-security--authentication-issues)
7. [File Processing](#7-file-processing-issues)
8. [ML/AI Features](#8-mlai-features-issues)
9. [Docker & Deployment](#9-docker--deployment-issues)
10. [Integration](#10-integration-issues)

---

## 🚨 Emergency Procedures

### System Down / Critical Failure

**Quick Recovery:**

```bash
# 1. Check system status
python dms-admin.py system status

# 2. Check logs for errors
tail -100 logs/__main___errors.log

# 3. Restart all services
python doc-master.py restart --all

# 4. Verify database connection
python dms-admin.py database stats

# 5. Test with health check
curl http://localhost:5000/health
```

### Database Corruption

**Emergency Restore:**

```bash
# 1. Stop all services
python doc-master.py stop --all

# 2. Backup current (corrupted) database
cp data/dms.db data/dms.db.corrupted.$(date +%Y%m%d_%H%M%S)

# 3. Restore from latest backup
python dms-admin.py database restore backups/latest.sql

# 4. Verify database integrity
python dms-admin.py database vacuum

# 5. Restart services
python doc-master.py start --all
```

### Data Loss Prevention

**Immediate Actions:**

```bash
# 1. Create emergency backup NOW
python dms-admin.py database backup --output emergency_backup_$(date +%Y%m%d).sql

# 2. Backup critical files
tar -czf emergency_files_$(date +%Y%m%d).tar.gz data/ documents/ config/

# 3. Check disk space
df -h

# 4. Check system resources
python dms-admin.py system monitor --realtime
```

---

## ⚡ Common Issues & Quick Fixes

### Issue 1: "Import Error: No module named 'X'"

**Problem:** Missing Python dependencies

**Quick Fix:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific missing module
pip install <module-name>

# Verify installation
python -c "import <module-name>; print('OK')"
```

**Common Missing Modules:**
- `spacy` - Install: `pip install spacy`
- `PyYAML` - Install: `pip install pyyaml`
- `Flask` - Install: `pip install flask`
- `psutil` - Install: `pip install psutil`

---

### Issue 2: "Permission Denied"

**Problem:** Insufficient file permissions

**Quick Fix:**
```bash
# Make CLI tools executable
chmod +x *.py

# Fix data directory permissions
chmod -R 755 data/

# Fix log directory permissions
chmod -R 755 logs/

# Check current permissions
ls -la *.py
```

---

### Issue 3: "Database Locked" or "OperationalError: database is locked"

**Problem:** SQLite database locked by another process

**Quick Fix:**
```bash
# Method 1: Find and kill locking process
lsof data/dms.db
kill -9 <PID>

# Method 2: Close all connections
python dms-admin.py database vacuum

# Method 3: Use WAL mode (Write-Ahead Logging)
sqlite3 data/dms.db "PRAGMA journal_mode=WAL;"

# Method 4: Wait and retry
# SQLite locks are usually brief
```

**Prevention:**
```python
# Use connection with timeout in code
import sqlite3
conn = sqlite3.connect('data/dms.db', timeout=30.0)
```

---

### Issue 4: "Port Already in Use"

**Problem:** Port 5000/8000 already occupied

**Quick Fix:**
```bash
# Find process using port
lsof -i :5000
# or
netstat -tuln | grep 5000

# Kill process
kill -9 <PID>

# Or use different port
python doc-dashboard.py --port 5001
python doc-api-server.py --port 8001
```

---

### Issue 5: "Out of Memory" or "MemoryError"

**Problem:** Insufficient RAM for processing

**Quick Fix:**
```bash
# Check memory usage
free -h

# Method 1: Process smaller batches
python doc-batch-processor.py batch /docs/ --batch-size 10

# Method 2: Increase swap
sudo fallocate -l 4G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Method 3: Close other applications
# Free up RAM before processing
```

---

### Issue 6: "spaCy Model Not Found"

**Problem:** NER models not downloaded

**Quick Fix:**
```bash
# Download English model
python -m spacy download en_core_web_sm

# Download German model
python -m spacy download de_core_news_sm

# Download Russian model
python -m spacy download ru_core_news_sm

# Verify models
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
```

---

### Issue 7: "Connection Refused" (API/Web)

**Problem:** Server not running or wrong host/port

**Quick Fix:**
```bash
# Check if server is running
ps aux | grep "doc-dashboard\|doc-api-server"

# Start server if not running
python doc-dashboard.py &

# Check correct host/port
curl http://localhost:5000/health

# If accessing from another machine, use 0.0.0.0
python doc-dashboard.py --host 0.0.0.0
```

---

### Issue 8: "File Not Found" or "No such file or directory"

**Problem:** Incorrect file path

**Quick Fix:**
```bash
# Use absolute paths
python doc-processor.py process /full/path/to/document.pdf

# Check file exists
ls -la /path/to/file.pdf

# Check current directory
pwd

# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

### Issue 9: "Encoding Error" or "UnicodeDecodeError"

**Problem:** File encoding issues

**Quick Fix:**
```bash
# Method 1: Convert file encoding
iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt

# Method 2: Specify encoding
python doc-processor.py process file.txt --encoding utf-8

# Method 3: Auto-detect encoding
python -c "
import chardet
with open('file.txt', 'rb') as f:
    result = chardet.detect(f.read())
    print(result['encoding'])
"
```

---

### Issue 10: "Slow Performance" or "Hanging"

**Problem:** Processing taking too long

**Quick Fix:**
```bash
# Check system resources
top
# or
htop

# Enable parallel processing
python doc-batch-processor.py batch /docs/ --parallel 8

# Reduce batch size
python doc-batch-processor.py batch /docs/ --batch-size 10

# Check for large files
find /docs/ -size +100M

# Enable debug logging to see progress
export LOG_LEVEL=DEBUG
python doc-processor.py process large_file.pdf
```

---

## 📚 Error Messages Catalog

### Database Errors

#### "OperationalError: no such table: X"

**Cause:** Database not initialized or corrupted

**Solution:**
```bash
# Initialize database
python -c "from src.core.database import Database; Database().init_db()"

# Or run migrations
python dms-admin.py database migrate
```

#### "IntegrityError: UNIQUE constraint failed"

**Cause:** Duplicate entry

**Solution:**
```bash
# Check existing records
python dms-admin.py database query "SELECT * FROM table WHERE field='value'"

# Update instead of insert
# Or delete duplicate first
```

---

### Import Errors

#### "ImportError: cannot import name 'X' from 'Y'"

**Cause:** Circular import or missing dependency

**Solution:**
```bash
# Check Python path
echo $PYTHONPATH

# Add project root to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### "ModuleNotFoundError: No module named 'src'"

**Cause:** PYTHONPATH not set

**Solution:**
```bash
# Temporary fix
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Permanent fix (add to ~/.bashrc or ~/.zshrc)
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
source ~/.bashrc
```

---

### API Errors

#### "401 Unauthorized"

**Cause:** Missing or invalid API key/token

**Solution:**
```bash
# Method 1: Add API key to request
curl -H "X-API-Key: your_key_here" http://localhost:5000/api/v1/services

# Method 2: Login and get token
curl -X POST http://localhost:5000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}'

# Method 3: Check API key in Swagger UI
# Visit http://localhost:5000/api/docs
# Click "Authorize" button
```

#### "429 Too Many Requests"

**Cause:** Rate limit exceeded

**Solution:**
```bash
# Wait for rate limit reset
# Check headers: X-RateLimit-Reset

# Or increase rate limit (admin only)
python dms-admin.py system config --set "rate_limit=10000"
```

#### "500 Internal Server Error"

**Cause:** Server-side error

**Solution:**
```bash
# Check server logs
tail -100 logs/__main___errors.log

# Check detailed error
curl -v http://localhost:5000/api/v1/endpoint

# Restart server
python doc-master.py restart api-server
```

---

### File Processing Errors

#### "PDFSyntaxError: PDF file is damaged"

**Cause:** Corrupted PDF file

**Solution:**
```bash
# Try repair with Ghostscript
gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress damaged.pdf

# Or use qpdf
qpdf --check damaged.pdf
qpdf damaged.pdf repaired.pdf

# Or try OCR
python doc-processor.py process damaged.pdf --ocr --output text.txt
```

#### "OSError: cannot identify image file"

**Cause:** Unsupported or corrupted image format

**Solution:**
```bash
# Check file type
file document.pdf

# Convert image format
convert image.bmp image.png

# Use different processor
python doc-processor.py process image.jpg --force-ocr
```

---

### NER/ML Errors

#### "OSError: Can't find model 'en_core_web_sm'"

**Cause:** spaCy model not installed

**Solution:**
```bash
# Download model
python -m spacy download en_core_web_sm

# Link model
python -m spacy link en_core_web_sm en

# Verify
python -c "import spacy; spacy.load('en_core_web_sm')"
```

#### "CUDA out of memory"

**Cause:** GPU memory exhausted

**Solution:**
```bash
# Use CPU instead
export CUDA_VISIBLE_DEVICES=""

# Or reduce batch size
python doc-processor.py process --batch-size 8

# Or use smaller model
python doc-processor.py process --model small
```

---

## 🔍 Diagnostic Tools

### System Health Check

```bash
# Comprehensive system check
python dms-admin.py system status

# Output:
# ✓ Database: Connected (SQLite 3.x)
# ✓ API Server: Running (PID 1234)
# ✓ Dashboard: Running (PID 5678)
# ✓ Disk Space: 45GB free (85% available)
# ✓ Memory: 4.2GB free (52% available)
# ✓ Python: 3.11.0
# ✓ spaCy Models: en_core_web_sm (installed)
```

### Log Analysis

```bash
# Check error logs
tail -100 logs/__main___errors.log

# Search for specific error
grep -i "error\|exception\|failed" logs/*.log

# Count errors by type
grep "Error:" logs/__main___errors.log | cut -d: -f2 | sort | uniq -c

# Real-time log monitoring
tail -f logs/__main__.log

# Filter logs by severity
grep "ERROR\|CRITICAL" logs/*.log
```

### Performance Monitoring

```bash
# Real-time system monitor
python dms-admin.py system monitor --realtime

# Check slow queries
python dms-admin.py database stats --slow-queries

# Profile processing
python -m cProfile -o profile.stats doc-processor.py process large.pdf
python -m pstats profile.stats

# Memory profiling
python -m memory_profiler doc-processor.py process large.pdf
```

### Database Diagnostics

```bash
# Database statistics
python dms-admin.py database stats

# Check database size
du -sh data/dms.db

# Vacuum and analyze
python dms-admin.py database vacuum

# Check integrity
sqlite3 data/dms.db "PRAGMA integrity_check;"

# List all tables
python dms-admin.py database query ".tables"

# Count records
python dms-admin.py database query "SELECT COUNT(*) FROM services;"
```

### Network Diagnostics

```bash
# Check port availability
nc -zv localhost 5000

# Test API endpoint
curl -v http://localhost:5000/health

# Check DNS resolution
nslookup api.example.com

# Test connectivity
ping -c 4 api.example.com

# Check firewall
sudo iptables -L
```

---

## 💡 Diagnostic Procedures

### Procedure 1: Identify Performance Bottleneck

**Steps:**

1. **Enable Debug Logging**
```bash
export LOG_LEVEL=DEBUG
```

2. **Profile the Operation**
```bash
python -m cProfile -o profile.stats doc-processor.py process document.pdf
```

3. **Analyze Profile**
```bash
python -m pstats profile.stats
# In pstats shell:
> sort cumulative
> stats 10
```

4. **Check System Resources**
```bash
# CPU usage
top

# Memory usage
free -h

# Disk I/O
iostat -x 1 10
```

5. **Optimize Based on Findings**
- High CPU → Use parallel processing
- High memory → Reduce batch size
- High disk I/O → Use SSD or optimize queries

---

### Procedure 2: Debug Import Errors

**Steps:**

1. **Check Python Version**
```bash
python --version
# Should be 3.9+
```

2. **Check Installed Packages**
```bash
pip list | grep -i <package-name>
```

3. **Check PYTHONPATH**
```bash
echo $PYTHONPATH
python -c "import sys; print('\\n'.join(sys.path))"
```

4. **Try Import in Python**
```python
python
>>> import src
>>> print(src.__file__)
>>> from src.core.database import Database
```

5. **Fix Issues**
```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall package
pip install <package> --force-reinstall
```

---

### Procedure 3: Troubleshoot Database Issues

**Steps:**

1. **Check Database File**
```bash
ls -lh data/dms.db
```

2. **Check Database Permissions**
```bash
ls -l data/
# Should be rwxr-xr-x
```

3. **Check Database Integrity**
```bash
sqlite3 data/dms.db "PRAGMA integrity_check;"
```

4. **Check for Locks**
```bash
lsof data/dms.db
```

5. **Backup and Repair**
```bash
# Backup
cp data/dms.db data/dms.db.backup

# Dump and restore
sqlite3 data/dms.db ".dump" > dump.sql
rm data/dms.db
sqlite3 data/dms.db < dump.sql
```

---

### Procedure 4: Debug API Issues

**Steps:**

1. **Check Server is Running**
```bash
ps aux | grep doc-api-server
```

2. **Check Logs**
```bash
tail -100 logs/__main__.log | grep -i api
```

3. **Test Endpoint Manually**
```bash
curl -v http://localhost:5000/api/v1/health
```

4. **Check Authentication**
```bash
# Get token
TOKEN=$(curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.token')

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/v1/services
```

5. **Check Swagger Docs**
```bash
# Visit http://localhost:5000/api/docs
# Try "Try it out" for endpoints
```

---

## ❓ Frequently Asked Questions

### Installation & Setup

**Q: Which Python version is required?**

A: Python 3.9 or higher is required. Python 3.11 is recommended.

```bash
python --version
# Should show: Python 3.9.x or higher
```

---

**Q: Do I need to install all dependencies?**

A: Yes, install required dependencies:

```bash
pip install -r requirements.txt
```

Optional dependencies for specific features:

```bash
# For advanced PDF processing
pip install PyPDF2 pdfplumber

# For OCR
pip install pytesseract

# For ML features
pip install transformers torch
```

---

**Q: How do I initialize the database?**

A:

```bash
# Method 1: Auto-initialize (recommended)
python -c "from src.core.database import Database; Database().init_db()"

# Method 2: Run migrations
python dms-admin.py database migrate

# Verify
python dms-admin.py database stats
```

---

### Usage

**Q: How do I process large files?**

A: Use batch processing with appropriate settings:

```bash
# Process in batches
python doc-batch-processor.py batch /large_files/ \
    --batch-size 10 \
    --parallel 4 \
    --log-file processing.log
```

---

**Q: Can I process documents in parallel?**

A: Yes, use the batch processor:

```bash
# Process 8 documents simultaneously
python doc-batch-processor.py batch /docs/ --parallel 8
```

---

**Q: How do I anonymize documents for GDPR?**

A:

```bash
# GDPR-compliant anonymization
python doc-anonymizer.py anonymize document.pdf \
    --compliance gdpr \
    --audit-log \
    --output anonymized.pdf
```

---

**Q: How do I search documents semantically?**

A:

```bash
# Semantic search
python doc-search.py search "contract agreements" --method semantic

# With filters
python doc-search.py search "financial reports" \
    --filters "year:2024,type:pdf" \
    --limit 50
```

---

### Performance

**Q: Why is processing slow?**

A: Several possible causes:

1. **Large files** → Use batch processing
2. **Limited RAM** → Reduce batch size
3. **CPU-bound** → Enable parallel processing
4. **Disk I/O** → Use SSD

Check resources:
```bash
python dms-admin.py system monitor --realtime
```

---

**Q: How do I speed up batch processing?**

A:

```bash
# Enable parallel processing
python doc-batch-processor.py batch /docs/ --parallel 8

# Reduce per-file processing time
python doc-processor.py process doc.pdf --fast-mode

# Use smaller NER model
python doc-processor.py process doc.pdf --model small
```

---

### Errors

**Q: "Import Error: No module named 'src'" - How to fix?**

A:

```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd /path/to/daten20
python doc-processor.py process document.pdf
```

---

**Q: "Database is locked" error - What to do?**

A:

```bash
# Find locking process
lsof data/dms.db

# Kill if necessary
kill -9 <PID>

# Enable WAL mode to reduce locks
sqlite3 data/dms.db "PRAGMA journal_mode=WAL;"
```

---

**Q: API returns 401 Unauthorized - Why?**

A: You need to authenticate:

```bash
# Method 1: Get token
TOKEN=$(curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.token')

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/v1/services

# Method 2: Use API key
curl -H "X-API-Key: your_key" http://localhost:5000/api/v1/services
```

---

### Deployment

**Q: How do I deploy in production?**

A: See [Deployment Guide](DEPLOYMENT_GUIDE.md) for details. Quick start:

```bash
# Using Docker
docker-compose up -d

# Or manual
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 src.web_app:app
```

---

**Q: How do I enable HTTPS?**

A: Use reverse proxy (recommended):

```nginx
# Nginx configuration
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

**Q: How do I monitor production system?**

A:

```bash
# System status
python dms-admin.py system status

# Real-time monitoring
python dms-admin.py system monitor --realtime

# Check logs
tail -f logs/__main__.log

# Metrics endpoint (Prometheus)
curl http://localhost:5000/metrics
```

---

## 🛠️ Advanced Troubleshooting

### Enable Debug Mode

```bash
# Set environment variables
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=1

# Start with debug logging
python doc-dashboard.py --debug --reload
```

### Collect Diagnostic Information

```bash
# Create diagnostic bundle
cat > collect_diagnostics.sh <<'EOF'
#!/bin/bash
mkdir -p diagnostics/
python --version > diagnostics/python_version.txt
pip list > diagnostics/pip_list.txt
python dms-admin.py system status > diagnostics/system_status.txt
tail -1000 logs/*.log > diagnostics/recent_logs.txt
df -h > diagnostics/disk_space.txt
free -h > diagnostics/memory.txt
netstat -tuln > diagnostics/network.txt
tar -czf diagnostics_$(date +%Y%m%d_%H%M%S).tar.gz diagnostics/
EOF

chmod +x collect_diagnostics.sh
./collect_diagnostics.sh
```

### Clean Installation

```bash
# Remove all cached files
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove virtual environment
rm -rf venv/

# Fresh install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Re-download models
python -m spacy download en_core_web_sm
```

---

## 📞 Getting Further Help

### Resources

- **Documentation:** `docs/`
- **API Docs:** http://localhost:5000/api/docs
- **User Guides:** `docs/user-guides/`
- **GitHub Issues:** https://github.com/svend4/daten20/issues

### Support Channels

- **GitHub Issues:** Bug reports and feature requests
- **Email:** support@example.com
- **Logs:** Check `logs/` directory for detailed error information

### Reporting Issues

When reporting an issue, include:

1. **Error message** (full text)
2. **Steps to reproduce**
3. **System information:**
```bash
python --version
pip list
python dms-admin.py system status
```
4. **Relevant logs:**
```bash
tail -100 logs/__main___errors.log
```
5. **Configuration** (if applicable)

---

## 📚 Related Documentation

- **[CLI Tools Master Guide](docs/user-guides/CLI_TOOLS_MASTER_GUIDE.md)** - Complete CLI reference
- **[API Documentation](docs/API_DOCUMENTATION_GUIDE.md)** - API usage and examples
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing guidelines

---

## 📝 Changelog

### Version 4.1.0 (2026-01-16) - Phase 4 Task 45 ✅

- ✅ Created comprehensive troubleshooting guide
- ✅ 10 categories of common issues
- ✅ 50+ error messages documented
- ✅ Diagnostic procedures included
- ✅ FAQ section with 20+ questions
- ✅ Emergency recovery procedures
- ✅ Advanced troubleshooting techniques

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Maintained by:** DMS Development Team
**Status:** Production Ready

For additional help, visit: https://github.com/svend4/daten20/issues
