# API Examples - Document Intelligence API

Practical examples for using the Document Intelligence API in different languages.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Health Check](#health-check)
- [Document Upload](#document-upload)
- [Entity Extraction](#entity-extraction)
- [Relation Extraction](#relation-extraction)
- [Document Classification](#document-classification)
- [Knowledge Graph](#knowledge-graph)
- [Batch Processing](#batch-processing)
- [Error Handling](#error-handling)

---

## Getting Started

### Base URL
```
Development: http://localhost:5000/api/v1
Production:  https://api.example.com/v1
```

### Prerequisites
- Python 3.9+ (for Python examples)
- Node.js 14+ (for JavaScript examples)
- curl (for shell examples)

---

## Authentication

API key authentication is optional. When enabled, include the key in headers:

```bash
X-API-Key: your-api-key-here
```

---

## Health Check

Check if the API is running and all components are healthy.

### cURL

```bash
curl -X GET http://localhost:5000/api/v1/health
```

### Python

```python
import requests

response = requests.get('http://localhost:5000/api/v1/health')
data = response.json()

print(f"Status: {data['status']}")
print(f"Version: {data['version']}")
print(f"Uptime: {data['uptime']} seconds")
print(f"Components: {data['components']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

async function healthCheck() {
    try {
        const response = await axios.get('http://localhost:5000/api/v1/health');
        console.log('Status:', response.data.status);
        console.log('Version:', response.data.version);
        console.log('Uptime:', response.data.uptime, 'seconds');
        console.log('Components:', response.data.components);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

healthCheck();
```

### Response

```json
{
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600.5,
    "components": {
        "database": "ok",
        "ner_engine": "ok",
        "classifier": "ok",
        "relation_extractor": "ok",
        "graph_builder": "ok"
    }
}
```

---

## Document Upload

Upload and process a document.

### cURL

```bash
curl -X POST http://localhost:5000/api/v1/documents \
  -H "X-API-Key: your-api-key" \
  -F "file=@contract.pdf" \
  -F "build_graph=false" \
  -F "extract_relations=true"
```

### Python

```python
import requests

def upload_document(file_path, api_key=None):
    url = 'http://localhost:5000/api/v1/documents'

    headers = {}
    if api_key:
        headers['X-API-Key'] = api_key

    files = {'file': open(file_path, 'rb')}
    data = {
        'build_graph': False,
        'extract_relations': True
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()

# Example usage
result = upload_document('contract.pdf', api_key='your-api-key')

print(f"Document ID: {result['document_id']}")
print(f"Classification: {result['classification']['category']} ({result['classification']['confidence']:.2%})")
print(f"Entities found: {len(result['entities'])}")
print(f"Relations found: {len(result['relations'])}")

# Print entities
for entity in result['entities']:
    print(f"  - {entity['text']} ({entity['type']}) - confidence: {entity['confidence']:.2%}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function uploadDocument(filePath, apiKey = null) {
    const url = 'http://localhost:5000/api/v1/documents';

    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('build_graph', 'false');
    form.append('extract_relations', 'true');

    const headers = form.getHeaders();
    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }

    try {
        const response = await axios.post(url, form, { headers });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Example usage
uploadDocument('contract.pdf', 'your-api-key')
    .then(result => {
        console.log('Document ID:', result.document_id);
        console.log('Classification:', result.classification.category);
        console.log('Entities found:', result.entities.length);
        console.log('Relations found:', result.relations.length);
    });
```

### Response

```json
{
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "contract.pdf",
    "processed_at": "2026-01-14T12:00:00Z",
    "statistics": {
        "pages": 5,
        "words": 1523,
        "characters": 9842
    },
    "classification": {
        "category": "contract",
        "confidence": 0.95,
        "probabilities": {
            "contract": 0.95,
            "invoice": 0.03,
            "report": 0.02
        }
    },
    "entities": [
        {
            "text": "John Doe",
            "type": "PERSON",
            "start": 45,
            "end": 53,
            "confidence": 0.98
        },
        {
            "text": "Acme Corp",
            "type": "ORG",
            "start": 120,
            "end": 129,
            "confidence": 0.96
        }
    ],
    "relations": [
        {
            "source": "John Doe",
            "source_type": "PERSON",
            "relation": "works_for",
            "target": "Acme Corp",
            "target_type": "ORG",
            "confidence": 0.89
        }
    ],
    "knowledge_graph": null
}
```

---

## Entity Extraction

Extract named entities from text.

### cURL

```bash
curl -X POST http://localhost:5000/api/v1/extract/entities \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "John Doe from Acme Corp signed the contract on January 15, 2026 for $50,000.",
    "options": {
      "min_confidence": 0.7
    }
  }'
```

### Python

```python
import requests

def extract_entities(text, api_key=None, min_confidence=0.7):
    url = 'http://localhost:5000/api/v1/extract/entities'

    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-API-Key'] = api_key

    payload = {
        'text': text,
        'options': {
            'min_confidence': min_confidence
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage
text = "John Doe from Acme Corp signed the contract on January 15, 2026 for $50,000."
result = extract_entities(text, api_key='your-api-key')

print(f"Found {result['count']} entities:")
for entity in result['entities']:
    print(f"  - {entity['text']} ({entity['type']}) - confidence: {entity['confidence']:.2%}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

async function extractEntities(text, apiKey = null, minConfidence = 0.7) {
    const url = 'http://localhost:5000/api/v1/extract/entities';

    const headers = {'Content-Type': 'application/json'};
    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }

    const payload = {
        text: text,
        options: {
            min_confidence: minConfidence
        }
    };

    try {
        const response = await axios.post(url, payload, { headers });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Example usage
const text = "John Doe from Acme Corp signed the contract on January 15, 2026 for $50,000.";
extractEntities(text, 'your-api-key')
    .then(result => {
        console.log(`Found ${result.count} entities:`);
        result.entities.forEach(entity => {
            console.log(`  - ${entity.text} (${entity.type}) - confidence: ${(entity.confidence * 100).toFixed(1)}%`);
        });
    });
```

### Response

```json
{
    "entities": [
        {
            "text": "John Doe",
            "type": "PERSON",
            "start": 0,
            "end": 8,
            "confidence": 0.98
        },
        {
            "text": "Acme Corp",
            "type": "ORG",
            "start": 14,
            "end": 23,
            "confidence": 0.96
        },
        {
            "text": "January 15, 2026",
            "type": "DATE",
            "start": 49,
            "end": 65,
            "confidence": 0.99
        },
        {
            "text": "$50,000",
            "type": "MONEY",
            "start": 70,
            "end": 77,
            "confidence": 0.97
        }
    ],
    "count": 4
}
```

---

## Relation Extraction

Extract semantic relations between entities.

### cURL

```bash
curl -X POST http://localhost:5000/api/v1/extract/relations \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "John Doe is the CEO of Acme Corp, headquartered in New York.",
    "options": {
      "min_confidence": 0.6
    }
  }'
```

### Python

```python
import requests

def extract_relations(text, api_key=None, min_confidence=0.6):
    url = 'http://localhost:5000/api/v1/extract/relations'

    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-API-Key'] = api_key

    payload = {
        'text': text,
        'options': {
            'min_confidence': min_confidence
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage
text = "John Doe is the CEO of Acme Corp, headquartered in New York."
result = extract_relations(text, api_key='your-api-key')

print(f"Found {result['count']} relations:")
for relation in result['relations']:
    print(f"  - {relation['source']} ({relation['source_type']}) "
          f"{relation['relation']} {relation['target']} ({relation['target_type']}) "
          f"- confidence: {relation['confidence']:.2%}")
```

### Response

```json
{
    "relations": [
        {
            "source": "John Doe",
            "source_type": "PERSON",
            "relation": "works_for",
            "target": "Acme Corp",
            "target_type": "ORG",
            "confidence": 0.92
        },
        {
            "source": "Acme Corp",
            "source_type": "ORG",
            "relation": "located_in",
            "target": "New York",
            "target_type": "GPE",
            "confidence": 0.88
        }
    ],
    "count": 2
}
```

---

## Document Classification

Classify documents into categories.

### cURL

```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "This agreement is made between Party A and Party B on this date..."
  }'
```

### Python

```python
import requests

def classify_document(text, api_key=None):
    url = 'http://localhost:5000/api/v1/classify'

    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-API-Key'] = api_key

    payload = {'text': text}

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage
text = "This agreement is made between Party A and Party B..."
result = classify_document(text, api_key='your-api-key')

print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']:.2%}")
print("Probabilities:")
for category, prob in result['probabilities'].items():
    print(f"  - {category}: {prob:.2%}")
```

### Response

```json
{
    "category": "contract",
    "confidence": 0.94,
    "probabilities": {
        "contract": 0.94,
        "letter": 0.03,
        "form": 0.02,
        "other": 0.01
    }
}
```

---

## Knowledge Graph

Build a knowledge graph from text.

### cURL

```bash
curl -X POST http://localhost:5000/api/v1/graph/build \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "John Doe works for Acme Corp in New York. Jane Smith is the CFO.",
    "format": "json"
  }'
```

### Python

```python
import requests

def build_knowledge_graph(text, format='json', api_key=None):
    url = 'http://localhost:5000/api/v1/graph/build'

    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-API-Key'] = api_key

    payload = {
        'text': text,
        'format': format
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage
text = "John Doe works for Acme Corp in New York. Jane Smith is the CFO."
result = build_knowledge_graph(text, format='json', api_key='your-api-key')

print(f"Nodes: {result['statistics']['node_count']}")
print(f"Edges: {result['statistics']['edge_count']}")

print("\nNodes:")
for node in result['nodes']:
    print(f"  - {node['label']} ({node['type']})")

print("\nEdges:")
for edge in result['edges']:
    print(f"  - {edge['source']} -> {edge['relation']} -> {edge['target']}")
```

---

## Batch Processing

Process multiple documents in batch.

### Python

```python
import requests
import time

def batch_process(file_paths, api_key=None):
    url = 'http://localhost:5000/api/v1/batch/process'

    headers = {}
    if api_key:
        headers['X-API-Key'] = api_key

    files = [('files', open(fp, 'rb')) for fp in file_paths]
    data = {'build_graph': False}

    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()

def check_batch_status(job_id, api_key=None):
    url = f'http://localhost:5000/api/v1/batch/{job_id}'

    headers = {}
    if api_key:
        headers['X-API-Key'] = api_key

    response = requests.get(url, headers=headers)
    return response.json()

# Example usage
file_paths = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']
batch_job = batch_process(file_paths, api_key='your-api-key')

job_id = batch_job['job_id']
print(f"Batch job created: {job_id}")
print(f"Total documents: {batch_job['total_documents']}")

# Poll for status
while True:
    status = check_batch_status(job_id, api_key='your-api-key')
    print(f"Status: {status['status']} - Processed: {status['processed']}/{status['total_documents']}")

    if status['status'] in ['completed', 'failed']:
        break

    time.sleep(5)

print(f"Batch job finished: {status['status']}")
print(f"Processed: {status['processed']}, Failed: {status['failed']}")
```

---

## Error Handling

### Python

```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, method='GET', **kwargs):
    """Safe API call with error handling."""
    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Check HTTP status
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        # HTTP error (4xx, 5xx)
        print(f"HTTP Error: {e.response.status_code}")
        if e.response.content:
            error_data = e.response.json()
            print(f"Error: {error_data.get('error')}")
            print(f"Message: {error_data.get('message')}")
        return None

    except requests.exceptions.ConnectionError:
        print("Connection Error: Unable to connect to API server")
        return None

    except requests.exceptions.Timeout:
        print("Timeout Error: Request took too long")
        return None

    except RequestException as e:
        print(f"Request Error: {e}")
        return None

    except ValueError as e:
        print(f"Value Error: {e}")
        return None

# Example usage
result = safe_api_call('http://localhost:5000/api/v1/health')
if result:
    print(f"API Status: {result['status']}")
else:
    print("Failed to call API")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

async function safeApiCall(url, method = 'GET', data = null, headers = {}) {
    try {
        let response;
        if (method === 'GET') {
            response = await axios.get(url, { headers });
        } else if (method === 'POST') {
            response = await axios.post(url, data, { headers });
        } else {
            throw new Error(`Unsupported method: ${method}`);
        }

        return response.data;

    } catch (error) {
        if (error.response) {
            // HTTP error (4xx, 5xx)
            console.error(`HTTP Error: ${error.response.status}`);
            console.error(`Error: ${error.response.data.error}`);
            console.error(`Message: ${error.response.data.message}`);
        } else if (error.request) {
            // Connection error
            console.error('Connection Error: Unable to connect to API server');
        } else {
            // Other errors
            console.error('Error:', error.message);
        }
        return null;
    }
}

// Example usage
safeApiCall('http://localhost:5000/api/v1/health')
    .then(result => {
        if (result) {
            console.log('API Status:', result.status);
        } else {
            console.log('Failed to call API');
        }
    });
```

---

## Common Errors

### 400 Bad Request
```json
{
    "error": "invalid_request",
    "message": "Invalid file format. Supported formats: pdf, docx, txt, html, md"
}
```

### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "Invalid API key"
}
```

### 404 Not Found
```json
{
    "error": "not_found",
    "message": "Document not found"
}
```

### 413 Payload Too Large
```json
{
    "error": "payload_too_large",
    "message": "File size exceeds maximum allowed size (50MB)"
}
```

### 429 Too Many Requests
```json
{
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 60 seconds."
}
```

### 500 Internal Server Error
```json
{
    "error": "internal_error",
    "message": "An internal server error occurred. Please try again later."
}
```

---

## Tips and Best Practices

1. **Rate Limiting**: Respect rate limits (100 req/min, 1000 req/hour)
2. **File Size**: Keep files under 50MB for optimal performance
3. **Batch Processing**: Use batch endpoints for multiple documents
4. **Error Handling**: Always implement proper error handling
5. **API Keys**: Keep API keys secure, never commit them to git
6. **Timeouts**: Set appropriate timeouts for long-running operations
7. **Caching**: Cache frequently accessed data to reduce API calls
8. **Pagination**: Use pagination for large result sets
9. **Compression**: Use gzip compression for large payloads
10. **Monitoring**: Monitor API usage and performance metrics

---

## Support

For questions or issues:
- Documentation: http://localhost:5000/docs
- GitHub Issues: https://github.com/yourusername/daten20/issues
- Email: support@example.com

---

**Document Intelligence API v1.0.0**
© 2026 Document Management System
