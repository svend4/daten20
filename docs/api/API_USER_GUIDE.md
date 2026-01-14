# Document Intelligence API - User Guide

Complete guide for using the Document Intelligence API.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Use Cases](#use-cases)
6. [SDKs and Tools](#sdks-and-tools)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

The Document Intelligence API provides AI-powered document analysis capabilities including:

- **Document Processing**: Upload and parse documents (PDF, DOCX, TXT, HTML, MD)
- **Named Entity Recognition (NER)**: Extract people, organizations, locations, dates, money
- **Relation Extraction**: Identify relationships between entities
- **Document Classification**: Categorize documents automatically
- **Knowledge Graph**: Build graph representations of document content
- **Batch Processing**: Process multiple documents at once

### Key Features

✅ **High Performance**: FastAPI-based async processing
✅ **Multiple Formats**: Supports PDF, DOCX, TXT, HTML, Markdown
✅ **AI/ML Powered**: spaCy, scikit-learn, TensorFlow
✅ **Production Ready**: Rate limiting, authentication, logging
✅ **Well Documented**: OpenAPI/Swagger UI, ReDoc
✅ **Easy Integration**: RESTful API, Python/JS examples

---

## Getting Started

### Prerequisites

- Python 3.9+ or Node.js 14+
- API server running (see Installation)
- Basic understanding of RESTful APIs

### Installation

#### Start API Server

```bash
# Option 1: Simple start
python doc-api-server.py

# Option 2: Custom port
python doc-api-server.py --host 0.0.0.0 --port 8000

# Option 3: Production mode with API key
python doc-api-server.py --production --api-key YOUR_SECRET_KEY
```

The API will be available at:
- **Main API**: http://localhost:5000/api/v1
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

#### Install Client Libraries

**Python:**
```bash
pip install requests
```

**JavaScript:**
```bash
npm install axios
```

---

## Authentication

### API Key Authentication (Optional)

When running in production mode, include the API key in request headers:

```bash
X-API-Key: your-api-key-here
```

**Example:**
```python
import requests

headers = {'X-API-Key': 'your-api-key'}
response = requests.get('http://localhost:5000/api/v1/health', headers=headers)
```

### No Authentication (Development)

In development mode, no authentication is required:

```python
response = requests.get('http://localhost:5000/api/v1/health')
```

---

## API Endpoints

### Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/documents` | POST | Upload document |
| `/documents/{id}` | GET | Get document |
| `/documents/{id}` | DELETE | Delete document |
| `/extract/entities` | POST | Extract entities |
| `/extract/relations` | POST | Extract relations |
| `/classify` | POST | Classify document |
| `/graph/build` | POST | Build knowledge graph |
| `/batch/process` | POST | Batch process |
| `/batch/{job_id}` | GET | Get batch status |
| `/stats` | GET | Get statistics |

### Base URL Structure

```
http://localhost:5000/api/v1/{endpoint}
```

---

## Use Cases

### 1. Contract Analysis

**Scenario**: Extract key information from legal contracts

```python
# Upload contract
response = requests.post(
    'http://localhost:5000/api/v1/documents',
    files={'file': open('contract.pdf', 'rb')},
    data={'extract_relations': True}
)

contract = response.json()

# Find parties involved
parties = [e for e in contract['entities'] if e['type'] == 'PERSON' or e['type'] == 'ORG']

# Find dates
dates = [e for e in contract['entities'] if e['type'] == 'DATE']

# Find monetary values
money = [e for e in contract['entities'] if e['type'] == 'MONEY']

print(f"Parties: {[p['text'] for p in parties]}")
print(f"Dates: {[d['text'] for d in dates]}")
print(f"Amounts: {[m['text'] for m in money]}")
```

### 2. Document Classification

**Scenario**: Automatically categorize incoming documents

```python
documents = ['invoice.pdf', 'contract.pdf', 'report.pdf']

for doc in documents:
    response = requests.post(
        'http://localhost:5000/api/v1/documents',
        files={'file': open(doc, 'rb')}
    )
    result = response.json()

    category = result['classification']['category']
    confidence = result['classification']['confidence']

    print(f"{doc}: {category} ({confidence:.1%})")
    # invoice.pdf: invoice (94%)
    # contract.pdf: contract (96%)
    # report.pdf: report (91%)
```

### 3. Entity Extraction from Text

**Scenario**: Extract entities from unstructured text

```python
text = """
Apple Inc. announced a new partnership with Google on January 15, 2026.
The deal is worth $500 million. Tim Cook and Sundar Pichai will lead
the initiative from their offices in Cupertino and Mountain View.
"""

response = requests.post(
    'http://localhost:5000/api/v1/extract/entities',
    json={'text': text}
)

entities = response.json()['entities']

# Group by type
by_type = {}
for entity in entities:
    entity_type = entity['type']
    if entity_type not in by_type:
        by_type[entity_type] = []
    by_type[entity_type].append(entity['text'])

print("Organizations:", by_type.get('ORG', []))
# ['Apple Inc.', 'Google']

print("People:", by_type.get('PERSON', []))
# ['Tim Cook', 'Sundar Pichai']

print("Locations:", by_type.get('GPE', []))
# ['Cupertino', 'Mountain View']

print("Dates:", by_type.get('DATE', []))
# ['January 15, 2026']

print("Money:", by_type.get('MONEY', []))
# ['$500 million']
```

### 4. Relationship Mapping

**Scenario**: Identify relationships in organizational data

```python
text = """
John Doe is the CEO of Acme Corp, headquartered in New York.
Jane Smith serves as CFO and reports to John Doe.
The company was founded by Bob Johnson in 2010.
"""

response = requests.post(
    'http://localhost:5000/api/v1/extract/relations',
    json={'text': text}
)

relations = response.json()['relations']

for rel in relations:
    print(f"{rel['source']} --[{rel['relation']}]--> {rel['target']}")
# John Doe --[works_for]--> Acme Corp
# Acme Corp --[located_in]--> New York
# Jane Smith --[reports_to]--> John Doe
```

### 5. Knowledge Graph Building

**Scenario**: Build a knowledge graph for research papers

```python
text = """
Machine Learning is a subset of Artificial Intelligence.
Neural Networks are a key component of Deep Learning.
Deep Learning is a type of Machine Learning used in Computer Vision.
"""

response = requests.post(
    'http://localhost:5000/api/v1/graph/build',
    json={
        'text': text,
        'format': 'json'
    }
)

graph = response.json()

print(f"Nodes: {graph['statistics']['node_count']}")
print(f"Edges: {graph['statistics']['edge_count']}")

# Visualize relationships
for edge in graph['edges']:
    print(f"{edge['source']} -> {edge['relation']} -> {edge['target']}")
```

### 6. Batch Document Processing

**Scenario**: Process hundreds of documents overnight

```python
import glob
import time

# Get all PDFs
pdf_files = glob.glob('documents/*.pdf')

# Submit batch job
response = requests.post(
    'http://localhost:5000/api/v1/batch/process',
    files=[('files', open(f, 'rb')) for f in pdf_files]
)

job_id = response.json()['job_id']
print(f"Batch job started: {job_id}")

# Poll for status
while True:
    status_response = requests.get(
        f'http://localhost:5000/api/v1/batch/{job_id}'
    )
    status = status_response.json()

    print(f"Progress: {status['processed']}/{status['total_documents']}")

    if status['status'] in ['completed', 'failed']:
        break

    time.sleep(10)  # Wait 10 seconds

print(f"Job {status['status']}!")
print(f"Processed: {status['processed']}, Failed: {status['failed']}")
```

---

## SDKs and Tools

### Python SDK (Recommended)

Create a Python wrapper for easier use:

```python
# doc_intelligence_client.py
import requests
from typing import Optional, Dict, Any, List

class DocumentIntelligenceClient:
    def __init__(self, base_url: str = "http://localhost:5000/api/v1", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def upload_document(self, file_path: str, **options) -> Dict[str, Any]:
        """Upload and process a document."""
        files = {'file': open(file_path, 'rb')}
        response = requests.post(
            f"{self.base_url}/documents",
            files=files,
            data=options,
            headers={'X-API-Key': self.api_key} if self.api_key else {}
        )
        return response.json()

    def extract_entities(self, text: str, **options) -> Dict[str, Any]:
        """Extract entities from text."""
        payload = {'text': text, 'options': options}
        response = requests.post(
            f"{self.base_url}/extract/entities",
            json=payload,
            headers=self._get_headers()
        )
        return response.json()

    def extract_relations(self, text: str, **options) -> Dict[str, Any]:
        """Extract relations from text."""
        payload = {'text': text, 'options': options}
        response = requests.post(
            f"{self.base_url}/extract/relations",
            json=payload,
            headers=self._get_headers()
        )
        return response.json()

    def classify(self, text: str) -> Dict[str, Any]:
        """Classify document."""
        payload = {'text': text}
        response = requests.post(
            f"{self.base_url}/classify",
            json=payload,
            headers=self._get_headers()
        )
        return response.json()

    def build_graph(self, text: str, format: str = 'json') -> Dict[str, Any]:
        """Build knowledge graph."""
        payload = {'text': text, 'format': format}
        response = requests.post(
            f"{self.base_url}/graph/build",
            json=payload,
            headers=self._get_headers()
        )
        return response.json()

# Usage
client = DocumentIntelligenceClient(api_key='your-api-key')

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Upload document
result = client.upload_document('contract.pdf', extract_relations=True)
print(f"Entities found: {len(result['entities'])}")

# Extract entities
entities = client.extract_entities("John Doe works for Acme Corp.")
print(f"Entities: {entities['count']}")
```

### JavaScript SDK

```javascript
// doc-intelligence-client.js
const axios = require('axios');

class DocumentIntelligenceClient {
    constructor(baseUrl = 'http://localhost:5000/api/v1', apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    _getHeaders() {
        const headers = {'Content-Type': 'application/json'};
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        return headers;
    }

    async healthCheck() {
        const response = await axios.get(`${this.baseUrl}/health`);
        return response.data;
    }

    async extractEntities(text, options = {}) {
        const payload = {text, options};
        const response = await axios.post(
            `${this.baseUrl}/extract/entities`,
            payload,
            {headers: this._getHeaders()}
        );
        return response.data;
    }

    async classify(text) {
        const payload = {text};
        const response = await axios.post(
            `${this.baseUrl}/classify`,
            payload,
            {headers: this._getHeaders()}
        );
        return response.data;
    }
}

module.exports = DocumentIntelligenceClient;

// Usage
const client = new DocumentIntelligenceClient('http://localhost:5000/api/v1', 'your-api-key');

client.healthCheck()
    .then(health => console.log('API Status:', health.status));

client.extractEntities('John Doe works for Acme Corp.')
    .then(result => console.log('Entities:', result.count));
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
try:
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raise exception for 4xx/5xx
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    error_data = e.response.json()
    print(f"Message: {error_data['message']}")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API server")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 2. Rate Limiting

Respect rate limits:

```python
import time
from requests.exceptions import HTTPError

def rate_limited_request(url, **kwargs):
    try:
        response = requests.post(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        if e.response.status_code == 429:  # Rate limit exceeded
            retry_after = int(e.response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return rate_limited_request(url, **kwargs)  # Retry
        else:
            raise
```

### 3. File Size Optimization

Keep files under 50MB:

```python
import os

def upload_if_size_ok(file_path, max_size_mb=50):
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if file_size_mb > max_size_mb:
        print(f"File too large: {file_size_mb:.1f}MB (max {max_size_mb}MB)")
        return None

    return upload_document(file_path)
```

### 4. Caching

Cache frequently accessed data:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def extract_entities_cached(text_hash):
    # Actual API call
    return extract_entities(text)

def get_entities(text):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return extract_entities_cached(text_hash)
```

### 5. Batch Processing

Use batch endpoints for multiple documents:

```python
# Good: Batch processing
batch_response = requests.post(
    '/api/v1/batch/process',
    files=[('files', open(f, 'rb')) for f in file_list]
)

# Bad: Individual requests
for file in file_list:
    requests.post('/api/v1/documents', files={'file': open(file, 'rb')})
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused

**Problem**: Cannot connect to API server

**Solution**:
```bash
# Check if server is running
curl http://localhost:5000/api/v1/health

# Start server if not running
python doc-api-server.py
```

#### 2. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install fastapi uvicorn[standard] python-multipart
```

#### 3. Rate Limit Exceeded

**Problem**: `429 Too Many Requests`

**Solution**:
- Wait for retry-after period
- Reduce request rate
- Use batch endpoints
- Implement exponential backoff

#### 4. File Upload Failed

**Problem**: `400 Bad Request: Invalid file format`

**Solution**:
- Check file format (supported: PDF, DOCX, TXT, HTML, MD)
- Ensure file is not corrupted
- Check file size (max 50MB)

#### 5. Low Confidence Scores

**Problem**: Entity confidence scores too low

**Solution**:
```python
# Adjust min_confidence threshold
result = client.extract_entities(
    text,
    min_confidence=0.5  # Lower threshold
)
```

---

## FAQ

### General

**Q: Is the API free to use?**
A: Yes, when self-hosted. Rate limits apply.

**Q: What formats are supported?**
A: PDF, DOCX, TXT, HTML, Markdown

**Q: Is there a file size limit?**
A: Yes, 50MB per file

**Q: Can I use this in production?**
A: Yes, with proper API key authentication

### Technical

**Q: How accurate is the NER?**
A: 85-95% depending on text quality and entity type

**Q: What languages are supported?**
A: English (primary), German, Russian, Ukrainian, Polish, French

**Q: Can I train custom models?**
A: Yes, see ML documentation

**Q: Is there a GraphQL API?**
A: Yes, available at `/graphql`

### Performance

**Q: How fast is document processing?**
A: 2-5 seconds for a 10-page PDF

**Q: What's the rate limit?**
A: 100 requests/minute, 1000 requests/hour (default)

**Q: Can I increase rate limits?**
A: Yes, configure in API server settings

---

## Support

### Documentation
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI Spec**: [OPENAPI_SPEC.yaml](OPENAPI_SPEC.yaml)
- **Examples**: [API_EXAMPLES.md](examples/API_EXAMPLES.md)

### Contact
- **GitHub**: https://github.com/yourusername/daten20
- **Email**: support@example.com
- **Issues**: https://github.com/yourusername/daten20/issues

---

**Document Intelligence API v1.0.0**
**Last Updated:** 2026-01-14
© 2026 Document Management System
