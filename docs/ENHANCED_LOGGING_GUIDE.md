# 📊 Enhanced Logging Guide
## Comprehensive Logging System for Daten20

---

## 🎯 Overview

The enhanced logging system provides production-ready logging capabilities with:

- ✅ **Performance Logging** - Measure operation timing and metrics
- ✅ **Audit Logging** - Compliance and security audit trails (GDPR, HIPAA)
- ✅ **Structured Logging** - Consistent, parseable log messages
- ✅ **Message Templates** - Pre-defined templates for consistency
- ✅ **Context Enrichment** - Add metadata to log entries
- ✅ **Multiple Handlers** - Console, file, JSON, error-specific logs

---

## 🚀 Quick Start

### Basic Setup

```python
from src.core.logging_config import setup_logger
from src.utils.logging_helpers import (
    PerformanceLogger,
    AuditLogger,
    StructuredLogger
)

# Setup basic logger
logger = setup_logger("my_app", log_level=logging.INFO)

# Create specialized loggers
perf_logger = PerformanceLogger(logger)
audit_logger = AuditLogger(logger)
struct_logger = StructuredLogger(logger)
```

---

## 📈 Performance Logging

### Measuring Operation Time

**Method 1: Context Manager**

```python
with perf_logger.measure("document_parsing", doc_id=123):
    parse_document()
# Logs: [PERF] Starting: document_parsing
# Logs: [PERF] Completed: document_parsing in 1.23s
```

**Method 2: Decorator**

```python
@perf_logger.timed("data_processing")
def process_data(items):
    # Process items
    return results
```

### Use Cases
- API endpoint response times
- Database query performance
- File I/O operations
- ML model inference time
- Batch processing duration

---

## 🔒 Audit Logging

### Compliance-Ready Audit Trails

**Log User Actions**

```python
audit_logger.log_action(
    action="create",
    user="john.smith",
    resource="document/contract.pdf",
    status="success",
    ip_address="192.168.1.100"
)
```

**Log Access Attempts**

```python
audit_logger.log_access(
    user="jane.doe",
    resource="confidential/data.xlsx",
    granted=False,
    reason="Insufficient permissions"
)
```

**Log PII Access (GDPR Compliance)**

```python
audit_logger.log_pii_access(
    user="admin",
    pii_type="customer_emails",
    purpose="Marketing analysis"
)
```

**Log Configuration Changes**

```python
audit_logger.log_configuration_change(
    user="admin",
    config_key="max_file_size",
    old_value="10MB",
    new_value="50MB"
)
```

### Compliance Features

**GDPR Requirements:**
- ✅ Who accessed what data
- ✅ When data was accessed
- ✅ Purpose of data access
- ✅ Tamper-proof audit trail

**HIPAA Requirements:**
- ✅ User authentication logs
- ✅ Data access logs
- ✅ Security event logs
- ✅ System activity logs

---

## 📝 Structured Logging

### Consistent, Parseable Log Messages

**Log HTTP Requests**

```python
struct_logger.log_request(
    method="POST",
    endpoint="/api/v1/documents",
    user="john.smith",
    status_code=201,
    duration=0.234,
    request_size=1024
)
```

**Log Business Operations**

```python
struct_logger.log_operation(
    operation="document_export",
    status="completed",
    entity_type="document",
    entity_id="doc_12345",
    export_format="pdf"
)
```

**Log Security Events**

```python
struct_logger.log_security_event(
    event_type="failed_login",
    severity="high",
    description="Multiple failed attempts",
    username="unknown",
    attempt_count=5
)
```

**Log Errors with Context**

```python
try:
    risky_operation()
except Exception as e:
    struct_logger.log_error(
        error=e,
        context={
            "user": "john.smith",
            "operation": "export",
            "doc_id": "123"
        },
        user_message="Export failed. Please try again."
    )
```

---

## 📋 Log Message Templates

### Pre-defined Templates for Consistency

```python
from src.utils.logging_helpers import LogMessageTemplates

# Document operations
msg = LogMessageTemplates.format(
    LogMessageTemplates.DOCUMENT_PARSED,
    doc_name="report.pdf",
    size=2048000,
    pages=15
)
logger.info(msg)
# Output: [DOC] Parsed document: report.pdf (2048000 bytes, 15 pages)

# User operations
msg = LogMessageTemplates.format(
    LogMessageTemplates.USER_LOGIN,
    username="john.smith",
    ip="192.168.1.100"
)
logger.info(msg)
# Output: [USER] Login: john.smith from 192.168.1.100

# System operations
msg = LogMessageTemplates.format(
    LogMessageTemplates.SYSTEM_STARTUP,
    service_name="DocumentService",
    version="4.1.0"
)
logger.info(msg)
# Output: [SYSTEM] Starting DocumentService v4.1.0
```

### Available Templates

**Document Operations:**
- `DOCUMENT_PARSED` - Document parsing completed
- `DOCUMENT_SAVED` - Document saved to storage
- `DOCUMENT_DELETED` - Document removed
- `DOCUMENT_EXPORTED` - Document exported to format

**User Operations:**
- `USER_LOGIN` - User logged in
- `USER_LOGOUT` - User logged out
- `USER_CREATED` - New user created
- `USER_UPDATED` - User profile updated
- `USER_DELETED` - User removed

**System Operations:**
- `SYSTEM_STARTUP` - Service starting
- `SYSTEM_SHUTDOWN` - Service stopping
- `SYSTEM_ERROR` - System error occurred
- `SYSTEM_HEALTH_CHECK` - Health status

**Processing Operations:**
- `PROCESSING_STARTED` - Task started
- `PROCESSING_COMPLETED` - Task finished
- `PROCESSING_FAILED` - Task failed
- `PROCESSING_PROGRESS` - Progress update

**Database Operations:**
- `DB_QUERY` - Query executed
- `DB_CONNECTION` - Connection status
- `DB_MIGRATION` - Migration applied
- `DB_BACKUP` - Backup created

**API Operations:**
- `API_CALL` - API request/response
- `API_AUTH_SUCCESS` - Authentication successful
- `API_AUTH_FAILED` - Authentication failed
- `API_RATE_LIMIT` - Rate limit exceeded

**Security Events:**
- `SECURITY_ACCESS_DENIED` - Access denied
- `SECURITY_SUSPICIOUS` - Suspicious activity
- `SECURITY_VIOLATION` - Security violation

---

## 🔧 Advanced Configuration

### JSON Logging

```python
from src.core.logging_config import setup_logger

logger = setup_logger(
    "my_app",
    enable_json=True  # Enable JSON format
)
```

### Separate Audit Log File

```python
from pathlib import Path
from src.utils.logging_helpers import AuditLogger

audit_logger = AuditLogger(
    logger,
    audit_log_path=Path("logs/security_audit.log")
)
```

### Custom Log Rotation

```python
logger = setup_logger(
    "my_app",
    rotation_size=50 * 1024 * 1024,  # 50 MB
    backup_count=10  # Keep 10 backup files
)
```

### Multiple Log Levels

```python
# Different levels for console and file
logger = setup_logger(
    "my_app",
    log_level=logging.DEBUG,  # File logs everything
    enable_console=True  # Console at INFO level
)
```

---

## 💡 Best Practices

### 1. Use Appropriate Log Levels

```python
logger.debug("Detailed diagnostic info")  # Development only
logger.info("General informational")      # Normal operations
logger.warning("Warning condition")       # Potential issues
logger.error("Error condition")           # Errors occurred
logger.critical("Critical failure")       # System failure
```

### 2. Add Context to Logs

```python
# Good - with context
logger.info("Document processed", extra={
    "doc_id": "123",
    "user": "john",
    "duration": 1.5
})

# Bad - no context
logger.info("Document processed")
```

### 3. Use Structured Logging for APIs

```python
# API endpoints should use structured logging
@app.route("/api/documents", methods=["POST"])
def create_document():
    start_time = time.time()

    try:
        doc = process_document(request.files["file"])

        struct_logger.log_request(
            method="POST",
            endpoint="/api/documents",
            user=current_user.username,
            status_code=201,
            duration=time.time() - start_time
        )

        return jsonify(doc), 201
    except Exception as e:
        struct_logger.log_error(e, context={"user": current_user.username})
        return jsonify({"error": str(e)}), 500
```

### 4. Always Log Security Events

```python
# Authentication
if not authenticate(username, password):
    struct_logger.log_security_event(
        event_type="failed_login",
        severity="medium",
        description="Invalid credentials",
        username=username,
        ip_address=request.remote_addr
    )

# Authorization
if not has_permission(user, resource):
    audit_logger.log_access(
        user=user.username,
        resource=resource,
        granted=False,
        reason="Insufficient permissions"
    )
```

### 5. Performance Logging for Critical Operations

```python
# Measure database queries
with perf_logger.measure("database_query", query_type="SELECT"):
    results = db.execute(query)

# Measure file operations
with perf_logger.measure("file_upload", file_size=file.size):
    save_file(file)

# Measure API calls
with perf_logger.measure("external_api_call", service="payment_gateway"):
    response = requests.post(api_url, data=payload)
```

---

## 📊 Log Analysis

### Parsing JSON Logs

```python
import json

with open("logs/my_app.log") as f:
    for line in f:
        if line.startswith("{"):  # JSON log
            log_entry = json.loads(line)

            if log_entry["level"] == "ERROR":
                print(f"Error: {log_entry['message']}")
                print(f"  Time: {log_entry['timestamp']}")
                print(f"  Module: {log_entry['module']}")
```

### Extracting Performance Metrics

```bash
# Extract all performance logs
grep "\[PERF\]" logs/my_app.log

# Find slow operations (> 5 seconds)
grep "\[PERF\]" logs/my_app.log | grep -E "[5-9]\.[0-9]+s|[0-9]{2,}\.[0-9]+s"
```

### Security Monitoring

```bash
# Check failed login attempts
grep "failed_login" logs/audit.log

# Check access denials
grep "Access denied" logs/audit.log

# Check PII access
grep "pii_access" logs/audit.log
```

---

## 🧪 Testing

### Example Test

```python
def test_performance_logging(caplog):
    """Test performance logging"""
    logger = setup_logger("test")
    perf_logger = PerformanceLogger(logger)

    with perf_logger.measure("test_operation"):
        time.sleep(0.1)

    assert "[PERF] Starting: test_operation" in caplog.text
    assert "[PERF] Completed: test_operation" in caplog.text
```

---

## 📚 Complete Example

```python
from src.core.logging_config import setup_logger
from src.utils.logging_helpers import (
    PerformanceLogger,
    AuditLogger,
    StructuredLogger,
    LogMessageTemplates
)

# Setup
logger = setup_logger("document_service", log_level=logging.INFO)
perf_logger = PerformanceLogger(logger)
audit_logger = AuditLogger(logger)
struct_logger = StructuredLogger(logger)

def process_document_upload(file, user):
    """Process document upload with comprehensive logging"""

    # Log user action
    audit_logger.log_action(
        action="upload",
        user=user.username,
        resource=f"document/{file.filename}",
        status="started"
    )

    # Measure processing time
    with perf_logger.measure("document_upload",
                            filename=file.filename,
                            user=user.username):
        try:
            # Process file
            doc = save_document(file)

            # Log success
            msg = LogMessageTemplates.format(
                LogMessageTemplates.DOCUMENT_SAVED,
                doc_id=doc.id,
                path=doc.path
            )
            logger.info(msg)

            # Log operation
            struct_logger.log_operation(
                operation="document_upload",
                status="completed",
                entity_type="document",
                entity_id=doc.id,
                file_size=file.size
            )

            # Update audit
            audit_logger.log_action(
                action="upload",
                user=user.username,
                resource=f"document/{doc.id}",
                status="success"
            )

            return doc

        except Exception as e:
            # Log error
            struct_logger.log_error(
                error=e,
                context={
                    "filename": file.filename,
                    "user": user.username,
                    "file_size": file.size
                },
                user_message="Failed to upload document"
            )

            # Log failed audit
            audit_logger.log_action(
                action="upload",
                user=user.username,
                resource=f"document/{file.filename}",
                status="failed",
                error=str(e)
            )

            raise
```

---

## 🎯 Summary

### Key Benefits

1. **Performance Monitoring** - Track slow operations
2. **Compliance** - GDPR/HIPAA audit trails
3. **Security** - Detect suspicious activity
4. **Debugging** - Rich context for troubleshooting
5. **Analytics** - Extract business metrics from logs
6. **Consistency** - Standardized log format

### When to Use What

| Use Case | Logger Type |
|----------|------------|
| Operation timing | PerformanceLogger |
| User actions | AuditLogger |
| API requests | StructuredLogger |
| Security events | StructuredLogger |
| Errors | StructuredLogger |
| Standard messages | LogMessageTemplates |

### Next Steps

1. ✅ Review examples in `examples/logging_examples.py`
2. ✅ Run examples: `python examples/logging_examples.py`
3. ✅ Integrate into your applications
4. ✅ Set up log aggregation (ELK, Splunk, etc.)
5. ✅ Create log dashboards and alerts

---

**Version:** 1.0
**Date:** 2026-01-12
**Status:** ✅ Production-Ready
