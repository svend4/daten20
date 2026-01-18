# 🔍 Distributed Tracing Guide

**Complete Guide to Distributed Tracing in DMS**

Your comprehensive resource for implementing and using distributed tracing with OpenTelemetry and Jaeger.

**Version:** 1.0
**Last Updated:** 2026-01-16
**Status:** Production Ready

---

## 📋 Table of Contents

### Quick Start
- [What is Distributed Tracing?](#what-is-distributed-tracing)
- [5-Minute Quick Start](#5-minute-quick-start)
- [Architecture Overview](#architecture-overview)

### Setup & Configuration
1. [Installation](#1-installation)
2. [Jaeger Setup](#2-jaeger-setup)
3. [Application Configuration](#3-application-configuration)

### Usage
4. [Basic Usage](#4-basic-usage)
5. [Advanced Patterns](#5-advanced-patterns)
6. [Best Practices](#6-best-practices)

### Operations
7. [Viewing Traces](#7-viewing-traces)
8. [Performance Optimization](#8-performance-optimization)
9. [Troubleshooting](#9-troubleshooting)

### Reference
10. [API Reference](#10-api-reference)
11. [Configuration Reference](#11-configuration-reference)
12. [Examples](#12-examples)

---

## What is Distributed Tracing?

### Overview

Distributed tracing is a method for tracking requests as they flow through a distributed system. It helps you:

- **Debug Complex Issues**: See exactly where errors occur across services
- **Optimize Performance**: Identify bottlenecks and slow operations
- **Understand Dependencies**: Visualize service interactions
- **Monitor Production**: Track real-time performance metrics

### Key Concepts

**Trace**: The complete journey of a request through your system
```
User Request → API → Database → ML Service → Response
    └─────────────── One Trace ────────────────┘
```

**Span**: A single operation within a trace
```
Trace: Process Document
├── Span: fetch_document (50ms)
├── Span: parse_pdf (200ms)
│   ├── Span: extract_text (150ms)
│   └── Span: extract_images (50ms)
├── Span: analyze_content (300ms)
│   ├── Span: ner_extraction (200ms)
│   └── Span: classification (100ms)
└── Span: save_results (30ms)

Total Duration: 580ms
```

**Attributes**: Key-value metadata attached to spans
```python
{
    "http.method": "POST",
    "http.status_code": 200,
    "document.id": 123,
    "user.id": "user@example.com"
}
```

---

## 5-Minute Quick Start

### Step 1: Start Jaeger

```bash
# Start Jaeger using docker-compose
docker-compose -f docker-compose.monitoring.yml up -d jaeger

# Verify Jaeger is running
curl http://localhost:14269/
# Should return: OK

# Open Jaeger UI
open http://localhost:16686
```

### Step 2: Install Dependencies

```bash
# Install OpenTelemetry packages
pip install opentelemetry-api>=1.22.0
pip install opentelemetry-sdk>=1.22.0
pip install opentelemetry-instrumentation-flask>=0.42b0
pip install opentelemetry-exporter-jaeger>=1.22.0
```

### Step 3: Initialize Tracing

```python
from flask import Flask
from src.core.tracing import init_tracing

app = Flask(__name__)

# Initialize tracing (call once at startup)
init_tracing(
    app_name="my-service",
    environment="development",
    jaeger_host="localhost",
    jaeger_port=6831
)
```

### Step 4: Add Tracing to Your Code

```python
from src.core.tracing import traced

@traced(name="process_document")
def process_document(doc_id):
    # Your code here
    return result
```

### Step 5: Generate Some Traces

```bash
# Make some requests
curl http://localhost:5000/api/documents

# View traces in Jaeger UI
open http://localhost:16686
# Select service: "my-service"
# Click "Find Traces"
```

**Done!** 🎉 You're now tracing requests!

---

## Architecture Overview

### Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│             │     │              │     │             │
│  DMS App    │────▶│   Jaeger     │────▶│  Jaeger UI  │
│  (Python)   │     │   Agent      │     │  (Browser)  │
│             │     │              │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
      │                     │                     │
      │ Spans               │ Spans               │ View
      │ (UDP 6831)          │ (HTTP 14268)        │ (HTTP 16686)
      │                     │                     │
      ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│           OpenTelemetry SDK (Python)                │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Flask   │  │ Requests │  │SQLAlchemy│         │
│  │  Instru  │  │  Instru  │  │  Instru  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **Application**: DMS app creates spans for operations
2. **SDK**: OpenTelemetry SDK batches spans
3. **Exporter**: Sends batches to Jaeger Agent (UDP 6831)
4. **Agent**: Forwards spans to Jaeger Collector
5. **Storage**: Jaeger stores traces in BadgerDB/Cassandra
6. **UI**: Users query traces via Jaeger UI (port 16686)

---

## 1. Installation

### Prerequisites

```bash
# Python 3.9+
python --version

# Docker (for Jaeger)
docker --version
```

### Install OpenTelemetry Packages

```bash
# Core packages
pip install opentelemetry-api>=1.22.0
pip install opentelemetry-sdk>=1.22.0

# Instrumentation libraries
pip install opentelemetry-instrumentation-flask>=0.42b0
pip install opentelemetry-instrumentation-requests>=0.42b0
pip install opentelemetry-instrumentation-sqlalchemy>=0.42b0

# Exporters
pip install opentelemetry-exporter-jaeger>=1.22.0
pip install opentelemetry-exporter-otlp>=1.22.0
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

### Verify Installation

```python
import opentelemetry
print(f"OpenTelemetry version: {opentelemetry.__version__}")
# Output: OpenTelemetry version: 1.22.0
```

---

## 2. Jaeger Setup

### Option 1: Docker Compose (Recommended)

```bash
# Start full monitoring stack (Prometheus, Grafana, Jaeger)
docker-compose -f docker-compose.monitoring.yml up -d

# Or start just Jaeger
docker-compose -f docker-compose.monitoring.yml up -d jaeger

# Verify services
docker-compose -f docker-compose.monitoring.yml ps
```

**Jaeger Ports:**
- **16686**: Jaeger UI (web interface)
- **14268**: Jaeger Collector HTTP
- **14250**: Jaeger Collector gRPC
- **6831**: Jaeger Agent (Thrift compact UDP) ← Most commonly used
- **6832**: Jaeger Agent (Thrift binary UDP)
- **4317**: OTLP gRPC endpoint
- **4318**: OTLP HTTP endpoint
- **9411**: Zipkin compatible endpoint

### Option 2: Docker Run (Quick Test)

```bash
# Run Jaeger all-in-one (memory storage)
docker run -d --name jaeger \
  -p 6831:6831/udp \
  -p 16686:16686 \
  -p 14268:14268 \
  jaegertracing/all-in-one:1.52
```

### Option 3: Kubernetes

```yaml
# k8s/jaeger-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:1.52
        ports:
        - containerPort: 16686
          name: ui
        - containerPort: 6831
          protocol: UDP
          name: agent-udp
        - containerPort: 14268
          name: collector
        env:
        - name: SPAN_STORAGE_TYPE
          value: "badger"
        - name: BADGER_EPHEMERAL
          value: "false"
        - name: BADGER_DIRECTORY_VALUE
          value: "/badger/data"
        volumeMounts:
        - name: jaeger-data
          mountPath: /badger
      volumes:
      - name: jaeger-data
        persistentVolumeClaim:
          claimName: jaeger-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
spec:
  selector:
    app: jaeger
  ports:
  - name: ui
    port: 16686
  - name: agent-udp
    port: 6831
    protocol: UDP
  - name: collector
    port: 14268
```

Deploy:

```bash
kubectl apply -f k8s/jaeger-deployment.yaml
kubectl port-forward svc/jaeger 16686:16686
```

### Verify Jaeger is Running

```bash
# Check health
curl http://localhost:14269/
# Response: OK

# Open UI
open http://localhost:16686
# Should see Jaeger UI
```

---

## 3. Application Configuration

### Basic Configuration

```python
# app.py or __init__.py
from flask import Flask
from src.core.tracing import init_tracing, shutdown_tracing

app = Flask(__name__)

# Initialize tracing at application startup
init_tracing(
    app_name="dms-api",
    environment="production",
    jaeger_host="localhost",
    jaeger_port=6831
)

# Cleanup on shutdown
@app.teardown_appcontext
def cleanup(exception=None):
    shutdown_tracing()

if __name__ == "__main__":
    app.run()
```

### Environment Variables Configuration

```bash
# .env
OTEL_SERVICE_NAME=dms-api
OTEL_ENVIRONMENT=production
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831
OTEL_TRACES_SAMPLER=always_on  # or: parentbased_always_on, parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=1.0  # Sampling rate (0.0 to 1.0)
```

```python
import os
from src.core.tracing import init_tracing

init_tracing(
    app_name=os.getenv("OTEL_SERVICE_NAME", "dms"),
    environment=os.getenv("OTEL_ENVIRONMENT", "development"),
    jaeger_host=os.getenv("JAEGER_AGENT_HOST", "localhost"),
    jaeger_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
    sample_rate=float(os.getenv("OTEL_TRACES_SAMPLER_ARG", "1.0"))
)
```

### Multiple Services Configuration

For microservices architectures:

```python
# Service 1: API
init_tracing(
    app_name="dms-api",
    environment="production"
)

# Service 2: Worker
init_tracing(
    app_name="dms-worker",
    environment="production"
)

# Service 3: ML Service
init_tracing(
    app_name="dms-ml",
    environment="production"
)
```

All services send traces to the same Jaeger instance, allowing you to see cross-service traces.

---

## 4. Basic Usage

### Using Decorators

#### 1. Simple Function Tracing

```python
from src.core.tracing import traced

@traced(name="calculate_similarity")
def calculate_similarity(doc1, doc2):
    # Your code here
    return similarity_score
```

#### 2. API Endpoint Tracing

```python
from flask import Flask, jsonify
from src.core.tracing import traced_api

app = Flask(__name__)

@app.route("/api/documents")
@traced_api("/api/documents")
def list_documents():
    documents = fetch_documents()
    return jsonify(documents)
```

#### 3. Database Operation Tracing

```python
from src.core.tracing import traced_db

@traced_db("SELECT", "documents")
def fetch_documents():
    return db.session.query(Document).all()

@traced_db("INSERT", "documents")
def create_document(data):
    doc = Document(**data)
    db.session.add(doc)
    db.session.commit()
    return doc
```

#### 4. ML Operation Tracing

```python
from src.core.tracing import traced_ml

@traced_ml("bert", "predict")
def extract_entities(text):
    return ner_model.predict(text)

@traced_ml("sklearn", "train")
def train_classifier(X, y):
    model.fit(X, y)
    return model
```

### Adding Custom Attributes

```python
from src.core.tracing import traced, add_span_attribute

@traced(name="process_document")
def process_document(doc_id):
    # Add attributes to current span
    add_span_attribute("document.id", doc_id)
    add_span_attribute("document.type", "pdf")
    add_span_attribute("user.id", current_user.id)

    # Your processing logic
    result = do_processing()

    add_span_attribute("result.status", "success")
    return result
```

### Adding Events

```python
from src.core.tracing import traced, add_span_event

@traced(name="upload_document")
def upload_document(file):
    # Add event when something notable happens
    add_span_event("file_received", {
        "filename": file.filename,
        "size_bytes": file.size
    })

    # Processing
    save_file(file)

    add_span_event("file_saved", {
        "path": file.path
    })
```

### Manual Span Creation

For fine-grained control:

```python
from src.core.tracing import create_span

def complex_operation():
    # Phase 1
    with create_span("phase1_load_data", {"source": "database"}):
        data = load_data()

    # Phase 2
    with create_span("phase2_transform", {"rows": len(data)}):
        transformed = transform_data(data)

    # Phase 3
    with create_span("phase3_save", {"destination": "s3"}):
        save_data(transformed)
```

---

## 5. Advanced Patterns

### Pattern 1: Distributed Context Propagation

When calling external services, context is automatically propagated:

```python
import requests
from src.core.tracing import traced

@traced(name="call_external_api")
def call_external_api():
    # OpenTelemetry automatically injects trace context
    # into HTTP headers (traceparent, tracestate)
    response = requests.get("https://api.example.com/data")
    return response.json()
```

The remote service (if also instrumented) will create spans as children of this span.

### Pattern 2: Async Operations

```python
import asyncio
from opentelemetry import trace

async def async_operation():
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("async_operation"):
        result = await fetch_async_data()
        return result

# Usage
asyncio.run(async_operation())
```

### Pattern 3: Background Tasks

```python
from celery import Celery
from src.core.tracing import traced

celery = Celery('tasks')

@celery.task
@traced(name="background_task")
def process_document_async(doc_id):
    # Trace context is preserved in background tasks
    document = Document.query.get(doc_id)
    result = process(document)
    return result
```

### Pattern 4: Sampling Strategies

Not all traces need to be collected. Use sampling to reduce overhead:

```python
# config/jaeger-sampling.json
{
  "service_strategies": [
    {
      "service": "dms-api",
      "type": "probabilistic",
      "param": 0.1,  # Sample 10% of traces
      "operation_strategies": [
        {
          "operation": "health_check",
          "type": "probabilistic",
          "param": 0.01  # Sample only 1% of health checks
        },
        {
          "operation": "process_document",
          "type": "probabilistic",
          "param": 1.0  # Sample 100% of document processing
        }
      ]
    }
  ],
  "default_strategy": {
    "type": "probabilistic",
    "param": 0.5  # Sample 50% by default
  }
}
```

### Pattern 5: Custom Exporters

Use multiple exporters simultaneously:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Export to Jaeger
jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Also export to OTLP Collector
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# And log to console (development only)
console_exporter = ConsoleSpanExporter()
provider.add_span_processor(BatchSpanProcessor(console_exporter))
```

---

## 6. Best Practices

### DO ✅

1. **Trace Critical Paths**
   ```python
   @traced_api("/api/orders")  # Critical business logic
   def create_order():
       pass
   ```

2. **Add Meaningful Attributes**
   ```python
   add_span_attribute("order.id", order_id)
   add_span_attribute("order.total", total_amount)
   add_span_attribute("customer.tier", "premium")
   ```

3. **Use Descriptive Span Names**
   ```python
   @traced(name="db.select.orders.by_customer")  # Good
   @traced(name="query")  # Bad - too generic
   ```

4. **Record Exceptions**
   ```python
   @traced(record_exception=True)
   def risky_operation():
       # Exceptions are automatically captured
       pass
   ```

5. **Use Sampling in Production**
   - Sample 100% during development
   - Sample 10-50% in production (high traffic)
   - Sample 100% for errors (always trace failures)

### DON'T ❌

1. **Don't Trace Everything**
   ```python
   # Bad - too granular
   @traced
   def add(a, b):
       return a + b
   ```

2. **Don't Add Sensitive Data**
   ```python
   # Bad - PII exposure
   add_span_attribute("user.password", password)
   add_span_attribute("credit_card", cc_number)

   # Good - sanitized
   add_span_attribute("user.email_hash", hash(email))
   add_span_attribute("payment.last4", cc[-4:])
   ```

3. **Don't Block on Tracing**
   - Use async exporters
   - Use batching
   - Set reasonable timeouts

4. **Don't Forget to Cleanup**
   ```python
   # Always call shutdown to flush pending spans
   @app.teardown_appcontext
   def cleanup(exception=None):
       shutdown_tracing()
   ```

---

## 7. Viewing Traces

### Jaeger UI Overview

Access Jaeger UI at: **http://localhost:16686**

#### Main Interface

```
┌─────────────────────────────────────────────────────────┐
│ Jaeger UI                                        [...]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Service: [dms-api      ▼]                             │
│  Operation: [All         ▼]                            │
│  Tags: [                    ]                          │
│  Lookback: [1h           ▼]                            │
│  Min Duration: [         ]  Max Duration: [         ]   │
│                                                         │
│                  [Find Traces]                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Search Traces

1. **By Service**: Select your service (e.g., `dms-api`)
2. **By Operation**: Filter by operation (e.g., `api./api/documents`)
3. **By Tags**: Filter by custom tags:
   ```
   http.status_code=500
   user.id=user@example.com
   error=true
   ```
4. **By Duration**: Find slow traces:
   ```
   Min Duration: 1s
   Max Duration: 10s
   ```

#### Trace Details

Click a trace to see details:

```
Trace: process_document (542ms)
├── api.POST./api/documents [200ms]
│   ├── db.select.documents [50ms]
│   │   └── SQL: SELECT * FROM documents WHERE id=?
│   ├── ml.ner.extract [300ms]
│   │   ├── load_model [100ms]
│   │   └── predict [200ms]
│   └── ml.classify [100ms]
└── db.update.documents [42ms]
```

#### Span Details

Click a span to see:

- Duration
- Start time
- Tags/Attributes
- Events/Logs
- Stack traces (if error)

---

## 8. Performance Optimization

### Sampling Configuration

Reduce overhead by sampling:

```json
// config/jaeger-sampling.json
{
  "default_strategy": {
    "type": "probabilistic",
    "param": 0.1  // 10% sampling
  }
}
```

Sampling types:

- **always_on**: Sample 100% (development)
- **always_off**: Sample 0% (disable tracing)
- **probabilistic**: Sample X% randomly
- **parentbased**: Inherit from parent span
- **rate_limiting**: Max N traces per second

### Batch Processing

Configure batch span processor:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,        # Queue size before blocking
    schedule_delay_millis=5000, # Export every 5 seconds
    max_export_batch_size=512,  # Batch size for export
    export_timeout_millis=30000 # Export timeout
)
```

### Resource Limits

Set resource limits:

```python
# Limit span attributes
from opentelemetry.sdk.trace import TracerProvider

provider = TracerProvider(
    resource=resource,
    span_limits=SpanLimits(
        max_attributes=128,
        max_events=128,
        max_links=128,
        max_attribute_length=1024
    )
)
```

---

## 9. Troubleshooting

### Issue 1: No Traces in Jaeger UI

**Symptoms:** Traces not appearing in Jaeger UI

**Diagnosis:**

```bash
# 1. Check Jaeger is running
curl http://localhost:14269/
# Should return: OK

# 2. Check Jaeger agent port is accessible
nc -zv localhost 6831
# Should connect successfully

# 3. Enable console exporter to see spans locally
```

```python
init_tracing(
    app_name="dms-api",
    enable_console=True  # Print spans to console
)
```

**Solution:**

- Verify `JAEGER_AGENT_HOST` and `JAEGER_AGENT_PORT`
- Check firewall/network settings
- Ensure spans are being created (check console output)

### Issue 2: High Memory Usage

**Symptoms:** Application memory grows over time

**Diagnosis:**

```bash
# Monitor memory
docker stats dms-api
```

**Solution:**

- Reduce sampling rate
- Reduce batch size
- Set max queue size
- Call `shutdown_tracing()` on app teardown

### Issue 3: Spans Missing Attributes

**Symptoms:** Spans don't have expected attributes

**Diagnosis:**

```python
from opentelemetry import trace

span = trace.get_current_span()
print(f"Span recording: {span.is_recording()}")
print(f"Span attributes: {span.attributes}")
```

**Solution:**

- Ensure span is recording
- Check attribute limits
- Verify instrumentation is enabled

### Issue 4: Broken Trace Context

**Symptoms:** Spans not connected in trace tree

**Diagnosis:**

- Check context propagation
- Verify headers in HTTP requests

**Solution:**

```python
# Manual context propagation
from opentelemetry.propagate import inject, extract
from opentelemetry import trace

# Sending side
headers = {}
inject(headers)
requests.get(url, headers=headers)

# Receiving side
ctx = extract(request.headers)
with tracer.start_as_current_span("operation", context=ctx):
    # Your code
```

---

## 10. API Reference

### `init_tracing()`

Initialize distributed tracing.

```python
def init_tracing(
    app_name: str = "dms",
    environment: str = "development",
    jaeger_host: Optional[str] = None,
    jaeger_port: Optional[int] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console: bool = False,
    sample_rate: float = 1.0,
) -> trace.Tracer
```

**Parameters:**
- `app_name`: Service name (appears in Jaeger UI)
- `environment`: Deployment environment
- `jaeger_host`: Jaeger agent hostname
- `jaeger_port`: Jaeger agent port (default 6831)
- `otlp_endpoint`: OTLP collector endpoint
- `enable_console`: Enable console logging
- `sample_rate`: Sampling rate (0.0 to 1.0)

**Returns:** Tracer instance

---

### `@traced()`

Decorator to trace a function.

```python
def traced(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
) -> Callable
```

**Parameters:**
- `name`: Custom span name (default: function name)
- `attributes`: Initial span attributes
- `record_exception`: Record exceptions in span

**Example:**

```python
@traced(name="calculate_score", attributes={"version": "v2"})
def calculate_score(data):
    return score
```

---

### `add_span_attribute()`

Add attribute to current span.

```python
def add_span_attribute(key: str, value: Any)
```

**Example:**

```python
add_span_attribute("user.id", user_id)
add_span_attribute("operation.success", True)
```

---

### `add_span_event()`

Add event to current span.

```python
def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None)
```

**Example:**

```python
add_span_event("cache_hit", {"key": cache_key})
add_span_event("validation_failed", {"reason": "invalid_email"})
```

---

### `create_span()`

Create a new span context manager.

```python
def create_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
)
```

**Example:**

```python
with create_span("database_query", {"table": "users"}):
    results = db.execute(query)
```

---

### `shutdown_tracing()`

Shutdown tracing and flush pending spans.

```python
def shutdown_tracing()
```

**Example:**

```python
@app.teardown_appcontext
def cleanup(exception=None):
    shutdown_tracing()
```

---

## 11. Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_SERVICE_NAME` | `"dms"` | Service name |
| `OTEL_ENVIRONMENT` | `"development"` | Environment |
| `JAEGER_AGENT_HOST` | `"localhost"` | Jaeger agent host |
| `JAEGER_AGENT_PORT` | `6831` | Jaeger agent port |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | - | OTLP endpoint |
| `OTEL_TRACES_SAMPLER` | `"always_on"` | Sampler type |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Sampler argument |

### Jaeger Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 16686 | HTTP | Jaeger UI |
| 14268 | HTTP | Jaeger Collector |
| 14250 | gRPC | Jaeger Collector |
| 6831 | UDP | Jaeger Agent (Thrift compact) |
| 6832 | UDP | Jaeger Agent (Thrift binary) |
| 4317 | gRPC | OTLP endpoint |
| 4318 | HTTP | OTLP endpoint |
| 9411 | HTTP | Zipkin endpoint |

---

## 12. Examples

### Example 1: Basic Flask App

```python
from flask import Flask, jsonify
from src.core.tracing import init_tracing, traced_api

app = Flask(__name__)
init_tracing(app_name="my-api")

@app.route("/users")
@traced_api("/users")
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

if __name__ == "__main__":
    app.run()
```

### Example 2: Multi-Service Trace

```python
# Service A: API Gateway
@traced_api("/api/process")
def process_request():
    # Call Service B
    response = requests.post("http://service-b:5000/analyze")
    return response.json()

# Service B: ML Service
@traced_ml("bert", "analyze")
def analyze_text(text):
    return model.predict(text)
```

Trace will show:

```
Trace: process_request (500ms)
├── Service A: api.POST./api/process [500ms]
│   └── http.POST.http://service-b:5000/analyze [450ms]
│       └── Service B: ml.bert.analyze [400ms]
```

### Example 3: Database Tracing

```python
@traced_db("SELECT", "users")
def get_user(user_id):
    user = User.query.get(user_id)
    add_span_attribute("user.found", user is not None)
    return user

@traced_db("INSERT", "orders")
def create_order(data):
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    add_span_event("order_created", {"order_id": order.id})
    return order
```

For more examples, see: `examples/tracing_example.py`

---

## 📚 Related Documentation

- **[Monitoring Guide](MONITORING_GUIDE.md)** - Prometheus & Grafana
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)** - Common issues

---

## 📞 Support

**Issues:** https://github.com/svend4/daten20/issues
**Jaeger Docs:** https://www.jaegertracing.io/docs/
**OpenTelemetry Docs:** https://opentelemetry.io/docs/

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Maintained by:** DMS Development Team

For distributed tracing support, visit: https://github.com/svend4/daten20/issues
