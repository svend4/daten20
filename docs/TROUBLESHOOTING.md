# Troubleshooting Guide

Comprehensive guide for solving common issues with Document Management System.

---

## Installation Issues

### Python version incompatibility
**Problem:** SyntaxError or ModuleNotFoundError during installation

**Solution:**
```bash
# Check Python version (must be 3.9+)
python --version
```

### pip install fails
**Problem:** pip install -r requirements.txt fails

**Solution:**
```bash
pip install --upgrade pip setuptools wheel
```

## Runtime Errors

### Import Errors
**Problem:** ModuleNotFoundError: No module named 'src'

**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database not initialized
**Problem:** sqlite3.OperationalError: no such table

**Solution:**
```bash
python -c "from src.core.database import Database; Database().init_db()"
```

## Performance Problems

### Slow processing
Use parallel processing:
```bash
python doc-batch-processor.py input/ --workers 4
```

### High memory usage
Process in smaller batches

## Getting Help

1. Check logs: logs/app.log
2. Search GitHub Issues
3. Create new issue with error details
