# Logging in Daten20

Comprehensive logging guide for the Document Management & AI Platform.

## Overview

Daten20 uses a centralized logging system with support for:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation and retention
- JSON formatting for structured logs
- Console and file handlers
- Integration with monitoring systems (Prometheus/Grafana)

## Quick Start

### Basic Usage

```python
from src.core.logger import setup_logger, get_logger

# Setup logger for a module
logger = get_logger(__name__)

# Log messages
logger.debug("Detailed debug information")
logger.info("General information message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error!")
```

### Using the Centralized Configuration

```python
from src.core.logging_config import LoggingConfig, setup_logger

# Setup with default configuration
logger = setup_logger('my_module')

# Setup with custom configuration
logger = LoggingConfig.setup(
    logger_name='custom_module',
    log_level=logging.DEBUG,
    enable_console=True,
    enable_file=True,
    enable_json=True,  # Use JSON formatting
    rotation_size=20 * 1024 * 1024,  # 20 MB
    backup_count=10
)
```

## Configuration Options

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (operation failed)
- **CRITICAL**: Critical errors (system failure)

### Log Formatters

#### Standard Format
```
2026-01-11 10:30:45 - module.name - INFO - Message text
```

#### JSON Format (Structured Logging)
```json
{
  "timestamp": "2026-01-11T10:30:45.123456",
  "level": "INFO",
  "logger": "dms.database",
  "message": "Service created successfully",
  "module": "database",
  "function": "create_service",
  "line": 163,
  "extra_fields": {
    "service_id": 42,
    "service_name": "Test Service"
  }
}
```

## Examples by Module

### Database Module

```python
from src.core.database import Database

# Logging is automatic in all database operations
db = Database()

# This logs:
# INFO: Initializing database at daten20.db
# DEBUG: Database directory ensured: /path/to/db
# DEBUG: Services table created/verified
# INFO: Database schema setup complete

# Create a service
service_id = db.create_service(service)
# INFO: Creating new service: Test Service
# DEBUG: Service created with ID: 1
# DEBUG: Financial data saved for service 1
# DEBUG: Initial version created for service 1
# INFO: Service created successfully: ID=1, name=Test Service
```

### Custom Module Logging

```python
from src.core.logger import get_logger

logger = get_logger(__name__)

def process_data(data):
    """Process data with logging"""
    try:
        logger.info(f"Processing {len(data)} items")

        for i, item in enumerate(data):
            logger.debug(f"Processing item {i}: {item}")
            # Process item

        logger.info("Processing completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        raise
```

### Context Logging

```python
from src.core.logger import LogContext, get_logger

logger = get_logger(__name__)

# Add context to log messages
with LogContext(logger, request_id='12345', user_id=42):
    logger.info("Processing user request")
    # Logs will include request_id and user_id
```

### Performance Logging

```python
from src.core.logger import log_performance, get_logger

logger = get_logger(__name__)

@log_performance(logger, 'data_calculation')
def calculate_complex_data():
    # Expensive operation
    result = perform_calculation()
    return result

# Automatically logs:
# INFO: data_calculation completed in 2.345s
```

## Log Files

### Default Log Structure

```
logs/
├── daten20.log              # Main application log
├── daten20_errors.log       # Error-only log
├── api.log                  # API requests
├── database.log             # Database operations
├── security.log             # Security events
├── performance.log          # Performance metrics
└── ai/                      # AI module logs
    ├── nlp.log
    ├── ml.log
    └── analytics.log
```

### Log Rotation

- **Default rotation size**: 10 MB per file
- **Default backup count**: 5 files
- **Naming**: `filename.log`, `filename.log.1`, `filename.log.2`, etc.

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good
logger.debug(f"SQL query: {query}")          # Diagnostic info
logger.info(f"Service created: ID={id}")     # Important events
logger.warning(f"Cache miss for key={key}")  # Non-critical issues
logger.error(f"Failed to connect: {e}")      # Errors
logger.critical(f"Database corrupted!")      # System failure

# ❌ Bad
logger.info(f"SQL query: {query}")           # Too verbose
logger.error(f"Service created: ID={id}")    # Wrong level
```

### 2. Log Exceptions Properly

```python
# ✅ Good
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # exc_info=True includes full traceback

# ❌ Bad
try:
    risky_operation()
except Exception as e:
    logger.error(f"Error: {e}")  # No traceback
```

### 3. Include Context

```python
# ✅ Good
logger.info(f"Service created successfully: ID={service_id}, name={name}")

# ❌ Bad
logger.info("Service created")  # No useful details
```

### 4. Don't Log Sensitive Data

```python
# ✅ Good
logger.info(f"User logged in: user_id={user_id}")

# ❌ Bad
logger.info(f"User logged in: password={password}")  # Security risk!
```

### 5. Use Structured Logging for Monitoring

```python
from src.core.logging_config import LoggingConfig

# Enable JSON logging for parsing by monitoring tools
logger = LoggingConfig.setup(
    logger_name='analytics',
    enable_json=True
)

# Logs can be parsed by Prometheus, Grafana, ELK stack, etc.
LoggingConfig.log_with_context(
    logger,
    logging.INFO,
    "Model training completed",
    model_name="bert-base",
    accuracy=0.95,
    training_time=3600
)
```

## Integration with Monitoring

### Prometheus

Logs can be exported to Prometheus for metrics visualization:

```python
from src.core.monitoring import MonitoringService

monitoring = MonitoringService()
monitoring.track_operation('service_creation', duration=0.123)
```

### Grafana

Use JSON-formatted logs with Loki for visualization in Grafana:

```python
logger = LoggingConfig.setup(
    logger_name='my_service',
    enable_json=True
)
```

Configure Grafana Loki to tail log files and create dashboards.

## Environment-Specific Configuration

### Development

```python
# Verbose logging to console
logger = setup_logger(
    'dev',
    log_level='DEBUG',
    enable_console=True,
    enable_file=True
)
```

### Production

```python
# Minimal console logging, comprehensive file logging
logger = setup_logger(
    'prod',
    log_level='INFO',
    enable_console=False,  # Reduce console noise
    enable_file=True,
    enable_json=True,      # Structured logs
    rotation_size=50 * 1024 * 1024,  # 50 MB
    backup_count=20        # Keep 20 backups
)
```

### Testing

```python
# Suppress most logs during tests
logger = setup_logger(
    'test',
    log_level='ERROR',     # Only errors
    enable_console=False
)
```

## Troubleshooting

### Issue: Logs not appearing

**Solution**: Check log level configuration
```python
logger.setLevel(logging.DEBUG)  # Ensure level allows your messages
```

### Issue: Too many log files

**Solution**: Adjust rotation and backup settings
```python
logger = setup_logger(
    'my_module',
    rotation_size=100 * 1024 * 1024,  # Larger files
    backup_count=3                     # Fewer backups
)
```

### Issue: Performance impact

**Solution**: Use appropriate log levels and async logging
```python
# Don't log in tight loops
for item in huge_list:
    # ❌ Bad
    logger.debug(f"Processing {item}")

# ✅ Good
logger.info(f"Processing {len(huge_list)} items")
for item in huge_list:
    # Process without logging
pass
logger.info("Processing complete")
```

## API Reference

### setup_logger()

```python
def setup_logger(
    name: Optional[str] = None,
    log_level: int = logging.INFO,
    **kwargs
) -> logging.Logger
```

Setup and return a configured logger.

**Parameters:**
- `name`: Logger name (default: None = root logger)
- `log_level`: Logging level (default: INFO)
- `**kwargs`: Additional configuration options

**Returns:** Configured Logger instance

### get_logger()

```python
def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger
```

Get a logger instance with the specified name.

**Parameters:**
- `name`: Logger name (usually `__name__`)
- `log_level`: Optional log level override

**Returns:** Logger instance

### LoggingConfig.log_with_context()

```python
@classmethod
def log_with_context(
    cls,
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any
) -> None
```

Log message with additional context fields.

**Parameters:**
- `logger`: Logger instance
- `level`: Log level
- `message`: Log message
- `**context`: Additional context fields (added to JSON output)

## See Also

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Structured Logging Best Practices](https://www.loggly.com/use-cases/structured-logging/)
