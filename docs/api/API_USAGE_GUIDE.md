# 📖 API Usage Guide

**Document Management System API v4.1.0**

Comprehensive guide for using the DMS REST API with AI/ML capabilities.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [Quick Start Examples](#quick-start-examples)
5. [API Endpoints](#api-endpoints)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Best Practices](#best-practices)

---

## 🚀 Getting Started

### Prerequisites

- API key (for production endpoints)
- HTTP client (curl, Postman, or programming language HTTP library)
- Basic understanding of REST APIs

### Documentation Links

- **Swagger UI**: http://localhost:5000/api/docs (Interactive API testing)
- **ReDoc**: http://localhost:5000/api/redoc (Beautiful API reference)
- **OpenAPI Spec**: http://localhost:5000/api/openapi.yaml (Machine-readable spec)

---

## 🔐 Authentication

### API Key Authentication

Include your API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:5000/api/v1/services
```

### Getting an API Key

1. Sign up at http://localhost:5000/signup
2. Navigate to Settings → API Keys
3. Generate a new API key
4. Copy and securely store your key

**⚠️ Security Warning**: Never commit API keys to version control!

---

## 🌐 Base URLs

| Environment | Base URL | Description |
|-------------|----------|-------------|
| **Local (Flask)** | `http://localhost:5000` | Flask web application |
| **Local (FastAPI)** | `http://localhost:8000` | FastAPI document intelligence |
| **Staging** | `https://staging-api.example.com` | Staging environment |
| **Production** | `https://api.example.com` | Production environment |

All API endpoints are prefixed with `/api/v1/`.

---

## 🎯 Quick Start Examples

### Health Check

Check if the API is running:

```bash
curl http://localhost:5000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "4.1.0",
  "api_version": "v1",
  "database": "connected",
  "components": {
    "parser": "operational",
    "ner": "operational",
    "classifier": "operational"
  }
}
```

### List Services

Get a list of all services:

```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/services?limit=10&offset=0"
```

Response:
```json
{
  "total": 42,
  "count": 10,
  "services": [
    {
      "id": 1,
      "service_name": "Shopping Assistance",
      "region": "Bavaria",
      "brutto_rate": 45.50,
      "created_at": "2026-01-14T10:00:00Z"
    }
  ]
}
```

### Create a Service

Create a new service:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "service_name": "Shopping Assistance",
    "target_group": "Elderly",
    "region": "Bavaria",
    "brutto_rate": 45.50,
    "materials_per_month": 100.00,
    "admin_percent": 5.0
  }' \
  http://localhost:5000/api/v1/services
```

### Upload Document

Upload and process a document with AI:

```bash
curl -X POST \
  -H "X-API-Key: your_key" \
  -F "file=@document.pdf" \
  -F "build_graph=true" \
  http://localhost:8000/api/v1/documents
```

Response:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "processed_at": "2026-01-14T10:30:00Z",
  "statistics": {
    "text_length": 5234,
    "word_count": 856,
    "entity_count": 23,
    "relation_count": 12
  },
  "classification": {
    "category": "SOCIAL_SERVICES",
    "confidence": 0.92
  },
  "entities": [
    {
      "text": "John Doe",
      "type": "PERSON",
      "start": 0,
      "end": 8,
      "confidence": 0.95
    }
  ]
}
```

### Extract Entities

Extract named entities from text:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "text": "John Doe works at Acme Corporation in New York."
  }' \
  "http://localhost:8000/api/v1/extract/entities?entity_types=PERSON,ORG,LOC"
```

Response:
```json
[
  {
    "text": "John Doe",
    "type": "PERSON",
    "start": 0,
    "end": 8,
    "confidence": 0.95
  },
  {
    "text": "Acme Corporation",
    "type": "ORG",
    "start": 18,
    "end": 34,
    "confidence": 0.92
  },
  {
    "text": "New York",
    "type": "LOC",
    "start": 38,
    "end": 46,
    "confidence": 0.98
  }
]
```

---

## 📚 API Endpoints

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/stats` | API statistics |

### Service Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/services` | List all services |
| POST | `/api/v1/services` | Create new service |
| GET | `/api/v1/services/{id}` | Get service details |
| PUT | `/api/v1/services/{id}` | Update service |
| DELETE | `/api/v1/services/{id}` | Delete service |

### Document Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents` | Upload & process document |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### AI/ML Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/extract/entities` | Extract entities (NER) |
| POST | `/api/v1/extract/relations` | Extract relations |
| POST | `/api/v1/classify` | Classify document |
| POST | `/api/v1/graph/build` | Build knowledge graph |

### Batch Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/batch/process` | Submit batch job |
| GET | `/api/v1/batch/{job_id}` | Get batch job status |

### Financial

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/calculate` | Calculate hourly rate |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search` | Search services |

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": "Invalid input",
  "details": "Field 'brutto_rate' must be a positive number",
  "code": "VALIDATION_ERROR"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## 🚦 Rate Limiting

### Limits by Tier

| Tier | Requests/Hour | Requests/Day |
|------|---------------|--------------|
| **Free** | 100 | 1,000 |
| **Standard** | 1,000 | 10,000 |
| **Enterprise** | Unlimited | Unlimited |

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642176000
```

### Handling Rate Limits

When you receive a `429 Too Many Requests` response:

1. Check the `Retry-After` header
2. Wait for the specified time
3. Retry your request

```bash
# Example with exponential backoff
for i in {1..5}; do
  response=$(curl -w "%{http_code}" -H "X-API-Key: $API_KEY" \
    http://localhost:5000/api/v1/services)

  if [ "$response" != "429" ]; then
    break
  fi

  sleep $((2 ** i))
done
```

---

## 💡 Best Practices

### 1. Always Use HTTPS in Production

```bash
# ❌ BAD
curl http://api.example.com/api/v1/services

# ✅ GOOD
curl https://api.example.com/api/v1/services
```

### 2. Handle Errors Gracefully

```python
import requests

try:
    response = requests.get(
        'http://localhost:5000/api/v1/services',
        headers={'X-API-Key': api_key},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 3. Use Pagination

```bash
# Fetch results in pages
curl "http://localhost:5000/api/v1/services?limit=50&offset=0"
curl "http://localhost:5000/api/v1/services?limit=50&offset=50"
curl "http://localhost:5000/api/v1/services?limit=50&offset=100"
```

### 4. Cache Responses

Cache responses when appropriate to reduce API calls:

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=100)
def get_service(service_id):
    response = requests.get(
        f'http://localhost:5000/api/v1/services/{service_id}',
        headers={'X-API-Key': api_key}
    )
    return response.json()
```

### 5. Use Batch Endpoints

For processing multiple documents, use batch endpoints:

```bash
# ❌ BAD - Multiple single requests
for file in *.pdf; do
  curl -X POST -F "file=@$file" http://localhost:8000/api/v1/documents
done

# ✅ GOOD - Single batch request
curl -X POST \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@doc3.pdf" \
  http://localhost:8000/api/v1/batch/process
```

### 6. Monitor API Usage

Track your API usage to avoid hitting rate limits:

```bash
curl -H "X-API-Key: $API_KEY" \
  http://localhost:5000/api/v1/stats
```

### 7. Version Your API Calls

Always specify the API version in your calls:

```python
BASE_URL = "http://localhost:5000/api/v1"

# ✅ GOOD - Version specified
response = requests.get(f"{BASE_URL}/services")
```

---

## 🔗 Code Examples

### Python

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:5000/api/v1"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# List services
response = requests.get(f"{BASE_URL}/services", headers=headers)
services = response.json()

# Create service
new_service = {
    "service_name": "Shopping Assistance",
    "brutto_rate": 45.50,
    "region": "Bavaria"
}
response = requests.post(
    f"{BASE_URL}/services",
    json=new_service,
    headers=headers
)
created_service = response.json()
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'http://localhost:5000/api/v1';

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

// List services
axios.get(`${BASE_URL}/services`, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error));

// Create service
const newService = {
  service_name: 'Shopping Assistance',
  brutto_rate: 45.50,
  region: 'Bavaria'
};

axios.post(`${BASE_URL}/services`, newService, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

### cURL

```bash
#!/bin/bash

API_KEY="your_api_key_here"
BASE_URL="http://localhost:5000/api/v1"

# List services
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/services"

# Create service
curl -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "Shopping Assistance",
    "brutto_rate": 45.50,
    "region": "Bavaria"
  }' \
  "$BASE_URL/services"
```

---

## 📞 Support

- **Documentation**: http://localhost:5000/api/docs
- **GitHub**: https://github.com/svend4/daten20
- **Email**: support@example.com
- **Issues**: https://github.com/svend4/daten20/issues

---

## 📝 Changelog

### v4.1.0 (2026-01-14)
- ✅ Complete OpenAPI 3.0 specification
- ✅ Swagger UI integration
- ✅ ReDoc integration
- ✅ 17 API endpoints
- ✅ Full AI/ML capabilities
- ✅ Comprehensive documentation

---

**Last Updated**: 2026-01-14
**API Version**: 4.1.0
