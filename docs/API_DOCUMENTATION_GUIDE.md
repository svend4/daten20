# 📚 API Documentation Guide

**Document Management System - Version 4.1**

Complete guide for API documentation, including Swagger/OpenAPI, usage examples, and best practices.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Accessing API Documentation](#accessing-api-documentation)
3. [OpenAPI Specification](#openapi-specification)
4. [API Endpoints Summary](#api-endpoints-summary)
5. [Authentication](#authentication)
6. [Rate Limiting](#rate-limiting)
7. [Using the Documentation](#using-the-documentation)
8. [Generating Documentation](#generating-documentation)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 📖 Overview

The Document Management System provides comprehensive REST API documentation using:

- **Swagger UI** - Interactive API explorer
- **ReDoc** - Beautiful API reference documentation
- **OpenAPI 3.0** - Machine-readable API specification
- **Auto-generated docs** - Always up-to-date with code

### Key Features

✅ **Interactive Testing** - Try API calls directly from browser
✅ **Complete Reference** - All endpoints documented
✅ **Code Examples** - Request/response samples in multiple languages
✅ **Schema Validation** - Request/response validation
✅ **Authentication** - API key and JWT token support
✅ **Versioning** - Multiple API versions supported

---

## 🌐 Accessing API Documentation

### Local Development

Once the server is running, access the documentation at:

| Interface | URL | Description |
|-----------|-----|-------------|
| **API Index** | http://localhost:5000/api/ | Documentation home page |
| **Swagger UI** | http://localhost:5000/api/docs | Interactive API explorer |
| **ReDoc** | http://localhost:5000/api/redoc | Beautiful API reference |
| **OpenAPI YAML** | http://localhost:5000/api/openapi.yaml | OpenAPI spec (YAML) |
| **OpenAPI JSON** | http://localhost:5000/api/openapi.json | OpenAPI spec (JSON) |

### Starting the Server

```bash
# Start Flask web app (includes API)
python src/web_app.py

# Or using the CLI tool
doc-api-server.py --host 0.0.0.0 --port 5000

# With debug mode
doc-api-server.py --debug
```

### Production URLs

In production, documentation is available at:

- **Swagger UI**: https://api.yourdomain.com/api/docs
- **ReDoc**: https://api.yourdomain.com/api/redoc
- **OpenAPI Spec**: https://api.yourdomain.com/api/openapi.yaml

---

## 📄 OpenAPI Specification

### File Locations

The OpenAPI specification files are located in:

```
docs/api/
├── openapi.yaml              # Main OpenAPI 3.0 spec (manual)
├── OPENAPI_SPEC.yaml         # Extended spec with examples
├── openapi_complete.yaml     # Auto-generated complete spec
├── API_USER_GUIDE.md         # User guide
├── API_USAGE_GUIDE.md        # Usage examples
└── examples/                 # Code examples
    ├── python_client.py
    ├── javascript_client.js
    └── curl_examples.sh
```

### Specification Structure

```yaml
openapi: 3.0.3
info:
  title: Document Management System API
  version: 4.1.0
  description: Comprehensive REST API with AI/ML capabilities

servers:
  - url: http://localhost:5000
    description: Local development
  - url: https://api.example.com
    description: Production

security:
  - ApiKeyAuth: []
  - BearerAuth: []

paths:
  /api/v1/health:
    get:
      summary: Health check
      tags: [System]
      responses:
        '200':
          description: API is healthy

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    BearerAuth:
      type: http
      scheme: bearer
```

---

## 🔌 API Endpoints Summary

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

### Document Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload document |
| POST | `/api/v1/documents/process` | Process document |
| GET | `/api/v1/documents/{id}` | Get document |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Analytics & BI

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/dashboard` | Get dashboard data |
| GET | `/api/v1/analytics/kpi/{name}` | Get specific KPI |
| POST | `/api/v1/analytics/predict/revenue` | Revenue forecast |
| POST | `/api/v1/analytics/predict/churn` | Churn prediction |
| POST | `/api/v1/analytics/export` | Export dashboard |

### Machine Learning

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ml/extract` | Extract entities |
| POST | `/api/v1/ml/classify` | Classify document |
| POST | `/api/v1/ml/knowledge-graph` | Build knowledge graph |

### Batch Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/batch/process` | Batch process documents |
| GET | `/api/v1/batch/{id}` | Get batch status |

---

## 🔐 Authentication

### API Key Authentication

Include your API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" \
     https://api.example.com/api/v1/services
```

**Python Example:**

```python
import requests

headers = {
    'X-API-Key': 'your_api_key_here'
}

response = requests.get('https://api.example.com/api/v1/services', headers=headers)
print(response.json())
```

### JWT Token Authentication

For user-specific operations, use JWT tokens:

```bash
# 1. Login to get token
curl -X POST https://api.example.com/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "pass"}'

# Response: {"token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}

# 2. Use token in subsequent requests
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     https://api.example.com/api/v1/services
```

**Python Example:**

```python
import requests

# Login
login_response = requests.post(
    'https://api.example.com/api/v1/auth/login',
    json={'username': 'user', 'password': 'pass'}
)
token = login_response.json()['token']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.example.com/api/v1/services', headers=headers)
```

### Getting API Keys

To obtain an API key:

1. **Web Interface**: Dashboard → Settings → API Keys → Generate New Key
2. **CLI Tool**: `doc-admin.py api-key create --name "My App" --scope read,write`
3. **Admin Panel**: Contact administrator for enterprise keys

---

## ⚡ Rate Limiting

API calls are rate-limited based on subscription tier:

| Tier | Rate Limit | Burst |
|------|------------|-------|
| **Free** | 100 requests/hour | 10/minute |
| **Standard** | 1,000 requests/hour | 50/minute |
| **Enterprise** | Unlimited | 500/minute |

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

When rate limit is exceeded (HTTP 429):

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 3600,
  "limit": 1000,
  "remaining": 0
}
```

**Python Example:**

```python
import time
import requests

def api_call_with_retry(url, headers):
    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

# Usage
response = api_call_with_retry('https://api.example.com/api/v1/services', headers)
```

---

## 📖 Using the Documentation

### Swagger UI Features

**1. Interactive Testing**

- Click on any endpoint to expand
- Click "Try it out" button
- Fill in parameters
- Click "Execute" to make real API calls

**2. Schema Explorer**

- View request/response schemas
- See required/optional fields
- Check data types and formats

**3. Authentication**

- Click "Authorize" button (🔓 icon)
- Enter your API key or JWT token
- All subsequent requests will include auth

**4. Code Generation**

- After executing a request, see code examples
- Available languages: curl, Python, JavaScript, Java, etc.

### ReDoc Features

**1. Navigation**

- Left sidebar with hierarchical navigation
- Search box to find specific endpoints
- Smooth scrolling

**2. Detailed Schemas**

- Expandable request/response schemas
- Nested object visualization
- Example values

**3. Download Spec**

- Download OpenAPI spec in YAML/JSON
- Use for client code generation

---

## 🛠️ Generating Documentation

### Auto-Generate from Code

The OpenAPI specification can be auto-generated from Flask routes:

```bash
# Generate fresh documentation
python scripts/generate_openapi_spec.py \
    --output docs/api/openapi_generated.yaml \
    --validate

# Merge with existing documentation
python scripts/generate_openapi_spec.py \
    --merge docs/api/openapi.yaml \
    --output docs/api/openapi_complete.yaml \
    --validate

# Generate JSON format
python scripts/generate_openapi_spec.py \
    --format json \
    --output docs/api/openapi.json
```

### Keeping Documentation Up-to-Date

**Method 1: Manual Updates**

Edit `docs/api/openapi.yaml` directly:

```yaml
paths:
  /api/v1/new-endpoint:
    post:
      summary: New endpoint
      tags: [Services]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
      responses:
        '201':
          description: Created successfully
```

**Method 2: Docstring Annotations**

Add Swagger annotations to Flask routes:

```python
@api_v1.route('/services', methods=['POST'])
def create_service():
    """
    Create a new service
    ---
    tags:
      - Services
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Service created successfully
        schema:
          $ref: '#/components/schemas/Service'
      400:
        description: Invalid input
    """
    # Implementation...
```

**Method 3: CI/CD Integration**

Add to `.github/workflows/ci.yml`:

```yaml
- name: Generate OpenAPI docs
  run: |
    python scripts/generate_openapi_spec.py \
      --merge docs/api/openapi.yaml \
      --output docs/api/openapi_complete.yaml \
      --validate

- name: Check for changes
  run: |
    git diff --exit-code docs/api/openapi_complete.yaml || \
      echo "::warning::OpenAPI spec needs update"
```

---

## ✨ Best Practices

### 1. Always Document New Endpoints

When adding a new API endpoint:

- ✅ Add docstring with operation description
- ✅ Specify request/response schemas
- ✅ Include example values
- ✅ Document error responses
- ✅ Add appropriate tags

### 2. Use Consistent Schemas

Define reusable schemas in `components/schemas`:

```yaml
components:
  schemas:
    Service:
      type: object
      required: [id, name]
      properties:
        id:
          type: integer
          format: int64
        name:
          type: string
          maxLength: 200
        description:
          type: string
```

### 3. Document Error Responses

Always document possible error responses:

```yaml
responses:
  '400':
    description: Bad request
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
  '401':
    description: Unauthorized
  '404':
    description: Not found
  '500':
    description: Internal server error
```

### 4. Provide Examples

Include example requests and responses:

```yaml
requestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/Service'
      examples:
        basic:
          summary: Basic service
          value:
            name: "Shopping Assistance"
            description: "Help with grocery shopping"
```

### 5. Version Your API

Use URL versioning:

- `/api/v1/services` - Current version
- `/api/v2/services` - New version (breaking changes)

Document deprecated endpoints:

```yaml
/api/v1/old-endpoint:
  get:
    deprecated: true
    summary: Old endpoint (use /api/v2/new-endpoint instead)
```

---

## 🔧 Troubleshooting

### Documentation Not Loading

**Problem:** Swagger UI shows "Failed to load API definition"

**Solutions:**

1. Check OpenAPI spec syntax:
```bash
python scripts/generate_openapi_spec.py \
    --merge docs/api/openapi.yaml \
    --validate
```

2. Verify server is running:
```bash
curl http://localhost:5000/api/openapi.yaml
```

3. Check CORS settings in `src/web_app.py`

### Routes Not Appearing

**Problem:** New routes don't show in documentation

**Solutions:**

1. Regenerate documentation:
```bash
python scripts/generate_openapi_spec.py \
    --merge docs/api/openapi.yaml \
    --output docs/api/openapi_complete.yaml
```

2. Check route decorator format:
```python
# Correct
@api_v1.route('/endpoint', methods=['GET'])

# May not be detected
@app.route('/endpoint')
```

3. Clear browser cache

### Authentication Not Working

**Problem:** "Unauthorized" errors when testing

**Solutions:**

1. Click "Authorize" button in Swagger UI
2. Enter valid API key or JWT token
3. Check token expiration
4. Verify API key scope/permissions

### Invalid OpenAPI Spec

**Problem:** Validation errors

**Solutions:**

1. Use online validator: https://editor.swagger.io/
2. Check YAML syntax: `yamllint docs/api/openapi.yaml`
3. Verify schema references exist
4. Check for circular references

---

## 📚 Additional Resources

### Tools

- **Swagger Editor**: https://editor.swagger.io/
- **Swagger Codegen**: Generate client libraries
- **Postman**: Import OpenAPI spec for testing
- **Insomnia**: Alternative API client

### Documentation

- **OpenAPI Specification**: https://swagger.io/specification/
- **Swagger UI**: https://swagger.io/tools/swagger-ui/
- **ReDoc**: https://redocly.com/redoc/

### Code Examples

See `docs/api/examples/` for:
- Python client examples
- JavaScript/Node.js examples
- cURL command examples
- Postman collections

---

## 📝 Changelog

### Version 4.1.0 (2026-01-16)

- ✅ Created auto-generation script for OpenAPI docs
- ✅ Added comprehensive API documentation guide
- ✅ Merged and validated all API endpoints (48 total)
- ✅ Added 12 categorized tags
- ✅ Included authentication and rate limiting docs
- ✅ Created troubleshooting guide

---

**Maintained by:** DMS Development Team
**Last Updated:** 2026-01-16
**API Version:** v1
**OpenAPI Version:** 3.0.3

For questions or issues, please contact: support@example.com
