# Test Suite for Daten20

Comprehensive test suite for the Document Management & AI Platform.

## Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── core/          # Tests for core functionality
│   ├── models/        # Tests for data models
│   └── utils/         # Tests for utilities
├── integration/       # Integration tests for APIs and services
├── performance/       # Performance and load tests
├── fixtures/          # Test fixtures and mock data
├── conftest.py        # Pytest configuration and fixtures
└── README.md          # This file
```

## Running Tests

### All tests
```bash
pytest
```

### Unit tests only
```bash
pytest tests/unit/
```

### Integration tests
```bash
pytest tests/integration/
```

### Performance tests
```bash
pytest tests/performance/ -m performance
```

### With coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.security` - Security tests

## Writing Tests

### Unit Test Example
```python
import pytest
from src.core.database import Database

class TestDatabase:
    def test_connection(self):
        db = Database()
        assert db.connect()
    
    def test_query(self):
        db = Database()
        result = db.query("SELECT 1")
        assert result is not None
```

### Integration Test Example
```python
import pytest
from flask import Flask

def test_api_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
```

## Coverage Goals

- **v1-v10 modules**: >80% coverage
- **v11-v20 modules**: >60% coverage
- **v21-v30 modules**: >40% coverage (conceptual/theoretical)

## Continuous Integration

Tests are automatically run on:
- Every push to main branch
- Every pull request
- Nightly builds

See `.github/workflows/` for CI/CD configuration.
