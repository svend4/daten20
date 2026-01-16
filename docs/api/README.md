# Daten20 API Documentation

REST API documentation for the Daten20 Enterprise Document Management & AI Platform.

## Overview

The Daten20 API provides programmatic access to:
- Document management
- Service planning and management
- User authentication and authorization
- Analytics and reporting
- Search functionality
- AI/ML capabilities (v3-v30)

## Base URL

```
Production: https://api.daten20.example.com/api
Staging: https://staging-api.daten20.example.com/api
Local: http://localhost:5000/api
```

## Authentication

The API uses JWT (JSON Web Token) authentication.

### Getting a Token

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com"
  },
  "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header:

```bash
Authorization: Bearer <your_token>
```

## Quick Start

### 1. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### 2. List Services

```bash
curl -X GET http://localhost:5000/api/services \
  -H "Authorization: Bearer <token>"
```

### 3. Create a Service

```bash
curl -X POST http://localhost:5000/api/services \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Healthcare Service",
    "description": "Primary healthcare service",
    "type": "Healthcare"
  }'
```

### 4. Upload a Document

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "title=Important Document"
```

## OpenAPI Specification

Full API specification is available in OpenAPI 3.0 format:

- **YAML**: [openapi.yaml](./openapi.yaml)
- **Interactive Documentation**: 
  - Swagger UI: http://localhost:5000/api/docs
  - ReDoc: http://localhost:5000/api/redoc

## API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login |
| POST | `/auth/logout` | User logout |
| POST | `/auth/register` | User registration |

### Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/services` | List all services |
| POST | `/services` | Create new service |
| GET | `/services/{id}` | Get service by ID |
| PUT | `/services/{id}` | Update service |
| DELETE | `/services/{id}` | Delete service |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/documents` | List all documents |
| POST | `/documents/upload` | Upload document |
| GET | `/documents/{id}` | Get document by ID |
| GET | `/documents/{id}/download` | Download document |
| DELETE | `/documents/{id}` | Delete document |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user |
| GET | `/users` | List all users |
| POST | `/users` | Create user |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/statistics` | Get system statistics |
| GET | `/analytics/dashboard` | Get dashboard data |
| POST | `/analytics/report` | Generate report |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search` | Search all entities |
| POST | `/search/advanced` | Advanced search |

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/export/pdf` | Export as PDF |
| GET | `/export/excel` | Export as Excel |
| GET | `/export/json` | Export as JSON |
| GET | `/export/csv` | Export as CSV |

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 413 | Payload Too Large |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## Rate Limiting

API requests are rate-limited:
- **Authenticated**: 1000 requests/hour
- **Unauthenticated**: 100 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

```
GET /api/services?page=2&limit=20
```

Response includes pagination metadata:
```json
{
  "services": [...],
  "total": 150,
  "page": 2,
  "limit": 20,
  "pages": 8
}
```

## Error Handling

All errors follow consistent format:

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "code": "VAL_001",
  "details": {
    "field": "email",
    "issue": "Invalid email format"
  }
}
```

## Versioning

The API uses URL versioning:
- Current version: v1 (default)
- Version is included in URL: `/api/v1/services`

## CORS

CORS is enabled for:
- Allowed origins: Configured in environment
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed headers: Authorization, Content-Type

## Webhooks

Subscribe to events:

```bash
POST /api/webhooks
{
  "url": "https://your-app.com/webhook",
  "events": ["service.created", "document.uploaded"]
}
```

## SDKs & Libraries

### Python

```python
from daten20 import Client

client = Client(api_key="your_api_key")
services = client.services.list()
```

### JavaScript

```javascript
import { Daten20 } from '@daten20/sdk';

const client = new Daten20({ apiKey: 'your_api_key' });
const services = await client.services.list();
```

## Support

- **Documentation**: https://docs.daten20.example.com
- **API Status**: https://status.daten20.example.com
- **Support Email**: support@daten20.example.com
- **GitHub Issues**: https://github.com/yourusername/daten20/issues

## 🛠️ Tools & Scripts

### Generate OpenAPI Specification

Auto-generate OpenAPI spec from Flask routes:

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
```

### Validate OpenAPI Specification

Validate OpenAPI specs:

```bash
# Validate default spec
python scripts/validate_openapi_spec.py

# Validate specific file
python scripts/validate_openapi_spec.py docs/api/openapi_complete.yaml

# Strict mode
python scripts/validate_openapi_spec.py --strict
```

## 📊 API Statistics

**Current Coverage (2026-01-16):**

- **Total Paths:** 48
- **Total Operations:** 61
- **Total Schemas:** 9
- **Total Tags:** 12
- **Validation:** ✅ All specs validated successfully

## Changelog

### v4.1.0 (2026-01-16) - Phase 4 Task 41 ✅
- ✅ Created auto-generation script for OpenAPI docs (scripts/generate_openapi_spec.py)
- ✅ Created validation script for OpenAPI specs (scripts/validate_openapi_spec.py)
- ✅ Generated complete OpenAPI spec (48 paths, 61 operations)
- ✅ Added comprehensive API documentation guide (API_DOCUMENTATION_GUIDE.md)
- ✅ All specs validated successfully

### v30.0.0 (2026-01-11)
- Added AI/ML endpoints (v3-v30)
- Enhanced analytics capabilities
- Improved search functionality

### v2.3.0 (2024-01-01)
- Added GraphQL endpoint
- WebSocket support for real-time updates
- Enhanced security features

### v2.0.0 (2023-06-01)
- Initial REST API release
- Basic CRUD operations
- Authentication system
