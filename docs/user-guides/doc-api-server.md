# 🚀 Doc-API-Server User Guide

**Version:** 1.0.0
**Type:** REST API Server
**Purpose:** High-performance FastAPI server for document intelligence

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Use Cases](#use-cases)
5. [Troubleshooting](#troubleshooting)
6. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Overview

**doc-api-server.py** provides a production-ready RESTful API for document processing, entity extraction, classification, and knowledge graph construction.

### Key Features

- ✅ **FastAPI Framework** - High-performance async API
- ✅ **OpenAPI/Swagger Docs** - Auto-generated interactive documentation
- ✅ **File Upload** - Support for PDF, DOCX, TXT (multipart/form-data)
- ✅ **Batch Processing** - Background job processing
- ✅ **CORS Enabled** - Cross-origin resource sharing
- ✅ **Type Safety** - Pydantic models for validation

### Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Validation:** Pydantic
- **Async:** Python asyncio
- **Docs:** OpenAPI 3.0 / Swagger UI

---

## ⚡ Quick Start

### 1. Start API Server

```bash
# Start on default port (8000)
python doc-api-server.py

# Output:
# ╔════════════════════════════════════════════════════════════════╗
# ║        Document Intelligence API v1.0.0                        ║
# ╠════════════════════════════════════════════════════════════════╣
# ║  🚀 High-performance RESTful API                               ║
# ║  🤖 AI-powered document analysis                               ║
# ╠════════════════════════════════════════════════════════════════╣
# ║  Server: http://127.0.0.1:8000
# ║  Docs:   http://127.0.0.1:8000/docs
# ║  Mode:   Development
# ╚════════════════════════════════════════════════════════════════╝
#
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Access API Documentation

```bash
# Open browser and navigate to:
http://localhost:8000/docs

# Interactive Swagger UI with:
# - All endpoints listed
# - Try-it-out functionality
# - Request/response schemas
# - Authentication options
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload and process document
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@document.pdf" \
  | jq '.'
```

---

## 📚 API Endpoints

### Root Endpoints

#### GET /

API information and navigation.

**Example:**
```bash
curl http://localhost:8000/

# Response:
{
  "name": "Document Intelligence API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/api/v1/health"
}
```

---

### System Endpoints

#### GET /api/v1/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600.5,
  "components": {
    "parser": "operational",
    "ner": "operational",
    "classifier": "operational",
    "relation_extractor": "operational",
    "knowledge_graph": "operational"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/health
```

---

#### GET /api/v1/stats

Get API usage statistics.

**Response:**
```json
{
  "total_requests": 142,
  "documents_processed": 35,
  "entities_extracted": 1523,
  "relations_extracted": 234
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/stats
```

---

### Document Endpoints

#### POST /api/v1/documents

Upload and process document.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF, DOCX, TXT)

**Query Parameters:**
- `build_graph` (optional): Build knowledge graph (boolean)

**Response:**
```json
{
  "document_id": "abc-123-def-456",
  "filename": "contract.pdf",
  "processed_at": "2026-01-14T10:30:00Z",
  "statistics": {
    "text_length": 5234,
    "word_count": 856,
    "entity_count": 23,
    "relation_count": 7
  },
  "classification": {
    "category": "LEGAL",
    "confidence": 0.87
  },
  "entities": [
    {
      "text": "Max Mustermann",
      "type": "PERSON",
      "start": 0,
      "end": 14,
      "confidence": 0.95
    }
  ],
  "relations": [
    {
      "source": "Max Mustermann",
      "source_type": "PERSON",
      "relation": "WORKS_AT",
      "target": "Acme Corp",
      "target_type": "ORGANIZATION",
      "confidence": 0.88
    }
  ],
  "knowledge_graph": null
}
```

**Examples:**

```bash
# Basic upload
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@document.pdf"

# With knowledge graph
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@document.pdf" \
  -F "build_graph=true"

# With API key (if auth enabled)
curl -X POST http://localhost:8000/api/v1/documents \
  -H "X-API-Key: your-api-key" \
  -F "file=@document.pdf"

# Save response to file
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@document.pdf" \
  -o results.json
```

---

### Extraction Endpoints

#### POST /api/v1/extract/entities

Extract entities from text.

**Request:**
```json
{
  "text": "Max Mustermann works at Acme Corp in Berlin.",
  "options": {}
}
```

**Query Parameters:**
- `entity_types` (optional): Comma-separated types (e.g., "PERSON,ORG")

**Response:**
```json
[
  {
    "text": "Max Mustermann",
    "type": "PERSON",
    "start": 0,
    "end": 14,
    "confidence": 0.95
  },
  {
    "text": "Acme Corp",
    "type": "ORGANIZATION",
    "start": 24,
    "end": 33,
    "confidence": 0.92
  },
  {
    "text": "Berlin",
    "type": "LOCATION",
    "start": 37,
    "end": 43,
    "confidence": 0.88
  }
]
```

**Examples:**

```bash
# Extract all entities
curl -X POST http://localhost:8000/api/v1/extract/entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Max Mustermann works at Acme Corp in Berlin."}'

# Extract specific types
curl -X POST "http://localhost:8000/api/v1/extract/entities?entity_types=PERSON,ORG" \
  -H "Content-Type: application/json" \
  -d '{"text": "Max Mustermann works at Acme Corp."}'
```

---

#### POST /api/v1/extract/relations

Extract relations from text.

**Request:**
```json
{
  "text": "Max Mustermann is the CEO of Acme Corp.",
  "options": {}
}
```

**Response:**
```json
[
  {
    "source": "Max Mustermann",
    "source_type": "PERSON",
    "relation": "WORKS_AT",
    "target": "Acme Corp",
    "target_type": "ORGANIZATION",
    "confidence": 0.88
  }
]
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/extract/relations \
  -H "Content-Type: application/json" \
  -d '{"text": "Max Mustermann is the CEO of Acme Corp."}'
```

---

#### POST /api/v1/classify

Classify document text.

**Request:**
```json
{
  "text": "This employment contract is entered into between...",
  "options": {}
}
```

**Response:**
```json
{
  "category": "LEGAL",
  "confidence": 0.87,
  "probabilities": {
    "LEGAL": 0.87,
    "BUSINESS": 0.08,
    "TECHNICAL": 0.03,
    "OTHER": 0.02
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "This employment contract..."}'
```

---

#### POST /api/v1/graph/build

Build knowledge graph from text.

**Request:**
```json
{
  "text": "Max works at Acme Corp. Jane manages TechStart.",
  "options": {}
}
```

**Query Parameters:**
- `export_format` (optional): json, cypher, graphml, adjacency

**Response:**
```json
{
  "nodes": [
    {
      "id": "node_1",
      "text": "Max",
      "type": "PERSON"
    },
    {
      "id": "node_2",
      "text": "Acme Corp",
      "type": "ORGANIZATION"
    }
  ],
  "edges": [
    {
      "source": "node_1",
      "target": "node_2",
      "relation_type": "WORKS_AT"
    }
  ]
}
```

**Examples:**

```bash
# JSON format (default)
curl -X POST http://localhost:8000/api/v1/graph/build \
  -H "Content-Type: application/json" \
  -d '{"text": "Max works at Acme Corp."}'

# Cypher format (Neo4j)
curl -X POST "http://localhost:8000/api/v1/graph/build?export_format=cypher" \
  -H "Content-Type: application/json" \
  -d '{"text": "Max works at Acme Corp."}'
```

---

### Batch Processing Endpoints

#### POST /api/v1/batch/process

Submit batch processing job.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: files[] (multiple files)

**Response:**
```json
{
  "job_id": "batch-abc-123",
  "status": "processing",
  "total_documents": 10,
  "processed": 0,
  "failed": 0,
  "created_at": "2026-01-14T10:30:00Z",
  "updated_at": "2026-01-14T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/batch/process \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@doc3.pdf"
```

---

#### GET /api/v1/batch/{job_id}

Get batch job status.

**Response:**
```json
{
  "job_id": "batch-abc-123",
  "status": "completed",
  "total_documents": 10,
  "processed": 10,
  "failed": 0,
  "created_at": "2026-01-14T10:30:00Z",
  "updated_at": "2026-01-14T10:35:00Z"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/batch/batch-abc-123
```

---

## 💼 Use Cases

### Use Case 1: Integrate with Web Application

**Scenario:** Add document intelligence to your web app.

```javascript
// Frontend JavaScript
async function processDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/api/v1/documents', {
    method: 'POST',
    body: formData
  });

  const results = await response.json();

  // Display entities
  results.entities.forEach(entity => {
    console.log(`${entity.type}: ${entity.text}`);
  });

  // Display classification
  console.log(`Category: ${results.classification.category}`);
}
```

**Why it's useful:** Easy integration with existing applications.

---

### Use Case 2: Microservices Architecture

**Scenario:** Use as microservice for document processing.

```bash
# Deploy API server
docker run -d -p 8000:8000 doc-api-server

# Other services call API
# Service A: Upload documents
curl -X POST http://api-server:8000/api/v1/documents \
  -F "file=@document.pdf"

# Service B: Extract entities
curl -X POST http://api-server:8000/api/v1/extract/entities \
  -H "Content-Type: application/json" \
  -d '{"text": "..."}'

# Service C: Build knowledge graph
curl -X POST http://api-server:8000/api/v1/graph/build \
  -H "Content-Type: application/json" \
  -d '{"text": "..."}'
```

**Why it's useful:** Decoupled architecture with dedicated service.

---

### Use Case 3: Batch Processing via API

**Scenario:** Process large batches through API.

```python
import requests

# Upload batch
files = [
    ('files', open('doc1.pdf', 'rb')),
    ('files', open('doc2.pdf', 'rb')),
    ('files', open('doc3.pdf', 'rb'))
]

response = requests.post(
    'http://localhost:8000/api/v1/batch/process',
    files=files
)

job = response.json()
job_id = job['job_id']

# Poll for completion
while True:
    status = requests.get(
        f'http://localhost:8000/api/v1/batch/{job_id}'
    ).json()

    if status['status'] == 'completed':
        print(f"Processed: {status['processed']}")
        break

    time.sleep(5)
```

**Why it's useful:** Programmatic batch processing.

---

## ❗ Troubleshooting

### Issue: "Server not starting"

**Error:** "Address already in use"

**Solutions:**

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill $(lsof -t -i:8000)

# Or use different port
python doc-api-server.py --port 8080
```

---

### Issue: "CORS errors in browser"

**Error:** "CORS policy: No 'Access-Control-Allow-Origin'"

**Solution:**

CORS is enabled by default for all origins. If still seeing errors:

```bash
# Check server logs
# CORS middleware should be loaded

# Verify headers in response
curl -I http://localhost:8000/api/v1/health

# Should see:
# Access-Control-Allow-Origin: *
```

---

### Issue: "Request timeout"

**Error:** "Request timeout after 60s"

**Causes:**
- Large file upload
- Slow processing

**Solutions:**

```bash
# Increase client timeout
curl --max-time 300 ...  # 5 minutes

# Or process asynchronously via batch endpoint
curl -X POST http://localhost:8000/api/v1/batch/process \
  -F "files=@large.pdf"
```

---

## 💡 Tips & Best Practices

### 1. Use Swagger UI for Development

```bash
# Start server
python doc-api-server.py

# Open Swagger UI
# http://localhost:8000/docs

# Features:
# - Test endpoints interactively
# - See request/response schemas
# - Try different parameters
# - Copy curl commands
```

### 2. Production Deployment

```bash
# Production mode with multiple workers
python doc-api-server.py \
  --host 0.0.0.0 \
  --port 8000 \
  --production \
  --workers 4

# With Gunicorn (recommended)
gunicorn doc-api-server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# With Docker
docker build -t doc-api-server .
docker run -d -p 8000:8000 doc-api-server
```

### 3. API Authentication

```bash
# Start with API key
python doc-api-server.py --api-key "your-secret-key"

# Clients must include header
curl -H "X-API-Key: your-secret-key" \
  http://localhost:8000/api/v1/health
```

### 4. Handle Errors Gracefully

```python
import requests

try:
    response = requests.post(
        'http://localhost:8000/api/v1/documents',
        files={'file': open('doc.pdf', 'rb')}
    )
    response.raise_for_status()
    results = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
```

### 5. Rate Limiting (Production)

```python
# Add rate limiting middleware (production)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/documents")
@limiter.limit("10/minute")
async def upload_document(...):
    ...
```

---

## 🔄 Related Tools

- **doc-dashboard.py** - Web UI (Flask-based)
- **doc-processor.py** - CLI equivalent
- **doc-batch-processor.py** - Batch processing

---

## 📊 Performance

### Expected Response Times

| Endpoint | Small Doc | Large Doc |
|----------|-----------|-----------|
| /documents | < 2s | < 10s |
| /extract/entities | < 0.5s | < 2s |
| /extract/relations | < 1s | < 3s |
| /classify | < 0.3s | < 1s |
| /graph/build | < 2s | < 8s |

### Scaling

```bash
# Vertical: More workers
python doc-api-server.py --workers 8

# Horizontal: Multiple instances behind load balancer
# Instance 1: :8001
# Instance 2: :8002
# Instance 3: :8003
# Load balancer: :8000 → {8001, 8002, 8003}
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
