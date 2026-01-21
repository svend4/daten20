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

### By directory
```bash
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests
pytest tests/e2e/          # E2E tests
pytest tests/performance/  # Performance tests
```

### By size (recommended)
```bash
# Using script (recommended)
./scripts/run_tests_by_size.sh small   # Fast tests (< 1s)
./scripts/run_tests_by_size.sh medium  # Integration tests (< 5min)
./scripts/run_tests_by_size.sh large   # E2E tests (may be slow)
./scripts/run_tests_by_size.sh quick   # Small + Medium (recommended for dev)
./scripts/run_tests_by_size.sh ci      # Optimized for CI/CD

# Using pytest directly
pytest -m small                    # Only small tests
pytest -m medium                   # Only medium tests
pytest -m large                    # Only large tests
pytest -m "small or medium"        # Small and medium
pytest -m "not large"              # Everything except large
```

### By type
```bash
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m e2e           # End-to-end tests
pytest -m security      # Security tests
pytest -m performance   # Performance tests
```

### With coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Advanced options
```bash
# Verbose output with coverage
./scripts/run_tests_by_size.sh small -v -c

# Run in parallel
./scripts/run_tests_by_size.sh medium -p

# Show slowest tests
./scripts/run_tests_by_size.sh small --durations 10

# Stop on first failure
./scripts/run_tests_by_size.sh quick -f

# Run specific tests
./scripts/run_tests_by_size.sh small -k "test_password"
```

## Test Markers

### By Type
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests

### By Size (Google Test Sizes)
- `@pytest.mark.small` - Small/fast tests (< 1s, no I/O, no network)
- `@pytest.mark.medium` - Medium tests (< 5min, local resources allowed)
- `@pytest.mark.large` - Large/extended tests (full integration, may be slow)

### Other
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.smoke` - Smoke tests
- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.enterprise` - Enterprise features tests

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

## Test Size Strategy

Tests are organized by size following Google Test Sizes standard:

- **Small tests**: Fast unit tests, no I/O, < 1 second
- **Medium tests**: Integration tests, local resources, < 5 minutes
- **Large tests**: E2E tests, full integration, may be slow

See [Test Sizes Guide](../docs/TEST_SIZES_GUIDE.md) for detailed documentation and examples.

### Test Examples

Example tests demonstrating proper test sizing:
- `tests/examples/test_size_examples_small.py` - Small test examples
- `tests/examples/test_size_examples_medium.py` - Medium test examples
- `tests/examples/test_size_examples_large.py` - Large test examples

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
