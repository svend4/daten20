# Week 2-4: CI/CD, Testing & Documentation

Продолжение детального плана реализации v4.2

---

## Week 2: CI/CD Pipeline Setup

### Day 8-9: GitHub Actions CI/CD

#### Задача 2.1: Настройка GitHub Actions
**Файлы:** `.github/workflows/*.yml` (множество файлов)

**Шаг 1: Main CI Pipeline**
Создать `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop, claude/* ]
  pull_request:
    branches: [ main, develop ]

jobs:
  # Job 1: Code Quality
  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install black isort flake8 mypy bandit safety

      - name: Run Black (Code Formatting)
        run: black --check src/ tests/

      - name: Run isort (Import Sorting)
        run: isort --check-only src/ tests/

      - name: Run Flake8 (Linting)
        run: flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__

      - name: Run MyPy (Type Checking)
        run: mypy src/ --ignore-missing-imports

      - name: Run Bandit (Security Linting)
        run: bandit -r src/ -ll

      - name: Check Dependencies (Safety)
        run: safety check --json

  # Job 2: Unit Tests
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: code-quality

    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y tesseract-ocr

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist

      - name: Run Unit Tests
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term \
            -n auto \
            -v

      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

      - name: Archive Coverage Report
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report-${{ matrix.python-version }}
          path: htmlcov/

  # Job 3: Integration Tests
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: unit-tests

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest

      - name: Run Integration Tests
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest tests/integration/ -v --tb=short

  # Job 4: Security Scan
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: code-quality

    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Job 5: Build Docker Image
  docker-build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: dms:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Test Docker image
        run: |
          docker run --rm dms:latest python --version

  # Job 6: Documentation Build
  docs-build:
    name: Build Documentation
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

      - name: Build docs
        run: |
          cd docs
          make html

      - name: Upload docs artifact
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/_build/html/
```

**Шаг 2: CD Pipeline для Production**
Создать `.github/workflows/cd-production.yml`:

```yaml
name: CD - Production Deployment

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  # Deploy to production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://dms.production.com

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Extract version from tag
        id: extract_version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            dms:${{ steps.extract_version.outputs.VERSION }}
            dms:latest

      - name: Deploy to Kubernetes
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG_PRODUCTION }}
        run: |
          kubectl set image deployment/dms \
            dms=dms:${{ steps.extract_version.outputs.VERSION }}
          kubectl rollout status deployment/dms

      - name: Run Database Migrations
        env:
          DATABASE_URL: ${{ secrets.PRODUCTION_DATABASE_URL }}
        run: |
          python -m alembic upgrade head

      - name: Verify Deployment
        run: |
          curl -f https://dms.production.com/health || exit 1

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            Production deployment of version ${{ steps.extract_version.outputs.VERSION }} completed!
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        if: always()

  # Rollback on failure
  rollback:
    name: Rollback on Failure
    runs-on: ubuntu-latest
    needs: deploy-production
    if: failure()

    steps:
      - name: Rollback Kubernetes deployment
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG_PRODUCTION }}
        run: |
          kubectl rollout undo deployment/dms
          kubectl rollout status deployment/dms

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: 'failure'
          text: 'Production deployment failed and was rolled back!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Шаг 3: Staging Deployment**
Создать `.github/workflows/cd-staging.yml`:

```yaml
name: CD - Staging Deployment

on:
  push:
    branches:
      - develop

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://dms.staging.com

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to staging
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG_STAGING }}
        run: |
          # Build image
          docker build -t dms:staging .

          # Deploy
          kubectl set image deployment/dms dms=dms:staging
          kubectl rollout status deployment/dms

      - name: Run E2E tests
        run: |
          npm run test:e2e -- --base-url=https://dms.staging.com

      - name: Performance tests
        run: |
          locust -f locustfile.py \
            --headless \
            --users 100 \
            --spawn-rate 10 \
            --run-time 5m \
            --host https://dms.staging.com
```

---

### Day 10-11: Pre-commit Hooks & Code Quality

#### Задача 2.2: Pre-commit Configuration
**Файл:** `.pre-commit-config.yaml`

```yaml
# Pre-commit hooks configuration
# Install: pip install pre-commit && pre-commit install

repos:
  # Code formatting
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.9

  # Import sorting
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  # Linting
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [
          "--max-line-length=100",
          "--extend-ignore=E203,W503"
        ]

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]

  # Security linting
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-ll", "-r", "src/"]

  # YAML validation
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key

  # Dockerfile linting
  - repo: https://github.com/hadolint/hadolint
    rev: v2.12.0
    hooks:
      - id: hadolint-docker

  # Shell script linting
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.6
    hooks:
      - id: shellcheck

  # Python docstring formatting
  - repo: https://github.com/PyCQA/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: ["--convention=google"]

  # Commit message linting
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.13.0
    hooks:
      - id: commitizen
```

**Инструкции по установке:**

```bash
# 1. Установить pre-commit
pip install pre-commit

# 2. Установить хуки
pre-commit install

# 3. Запустить на всех файлах (первый раз)
pre-commit run --all-files

# 4. Обновить хуки
pre-commit autoupdate
```

---

### Day 12-13: Automated Testing Infrastructure

#### Задача 2.3: Pytest Configuration
**Файл:** `pytest.ini`

```ini
[pytest]
# Pytest configuration
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Coverage settings
addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=75
    -n auto

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    security: marks tests as security tests
    performance: marks tests as performance tests
    smoke: marks tests as smoke tests
    regression: marks tests as regression tests

# Test discovery
norecursedirs = .git .tox dist build *.egg

# Logging
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S

# Warnings
filterwarnings =
    error
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

**Файл:** `conftest.py` (корневой)

```python
"""
Pytest configuration and fixtures.
"""
import pytest
import os
import tempfile
from typing import Generator
from src.core.database import Database
from src.core.auth import AuthManager


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing."""
    from src.web_app import app as flask_app

    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False

    yield flask_app


@pytest.fixture(scope="session")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def test_db() -> Generator:
    """Create temporary test database."""
    # Create temp database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.init_db()

    yield db

    # Cleanup
    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def auth_manager(test_db):
    """Create auth manager for testing."""
    return AuthManager(test_db)


@pytest.fixture(scope="function")
def test_user(auth_manager):
    """Create test user."""
    user = auth_manager.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!",
        role="user"
    )
    return user


@pytest.fixture(scope="function")
def admin_user(auth_manager):
    """Create admin user."""
    user = auth_manager.create_user(
        username="admin",
        email="admin@example.com",
        password="AdminPass123!",
        role="administrator"
    )
    return user


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return {
        'title': 'Test Document',
        'content': 'This is test content.',
        'type': 'text/plain',
        'metadata': {'author': 'Test Author'}
    }


@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration."""
    test_config = {
        'DATABASE_PATH': ':memory:',
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'TESTING': True
    }

    for key, value in test_config.items():
        monkeypatch.setenv(key, str(value))

    return test_config


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    yield
    # Reset any singletons here
    pass


# Markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
```

---

### Day 14: Performance Testing Setup

#### Задача 2.4: Load Testing Infrastructure
**Файл:** `locustfile.py` (улучшенный)

```python
"""
Load testing with Locust.

Usage:
    locust -f locustfile.py
    locust -f locustfile.py --headless --users 100 --spawn-rate 10 -H http://localhost:5000
"""
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import random
import json
import logging

logger = logging.getLogger(__name__)


class DocumentUser(FastHttpUser):
    """Simulate document management user."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    weight = 3  # 3x more likely than admin users

    def on_start(self):
        """Login before starting tasks."""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
        else:
            logger.error("Login failed!")

    @task(10)  # 10x more likely than other tasks
    def view_dashboard(self):
        """View main dashboard."""
        self.client.get("/")

    @task(5)
    def list_documents(self):
        """List documents."""
        self.client.get(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(3)
    def search_documents(self):
        """Search for documents."""
        query = random.choice([
            "financial report",
            "meeting notes",
            "project plan",
            "budget"
        ])

        self.client.get(
            f"/api/v1/search?q={query}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(2)
    def view_document(self):
        """View a random document."""
        doc_id = random.randint(1, 1000)
        self.client.get(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def create_document(self):
        """Create a new document."""
        doc_data = {
            "title": f"Test Document {random.randint(1, 10000)}",
            "content": "This is test content for load testing.",
            "type": "text/plain"
        }

        self.client.post(
            "/api/v1/documents",
            json=doc_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )


class AdminUser(FastHttpUser):
    """Simulate admin user."""

    wait_time = between(2, 5)
    weight = 1

    def on_start(self):
        """Login as admin."""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')

    @task(5)
    def view_analytics(self):
        """View analytics dashboard."""
        self.client.get(
            "/api/v1/analytics/dashboard",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(3)
    def view_users(self):
        """View user list."""
        self.client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def export_data(self):
        """Export data."""
        self.client.post(
            "/api/v1/export",
            json={"format": "excel", "type": "documents"},
            headers={"Authorization": f"Bearer {self.token}"}
        )


# Event listeners for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    logger.info("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    logger.info("Load test completed!")
    logger.info(f"Total requests: {environment.stats.total.num_requests}")
    logger.info(f"Total failures: {environment.stats.total.num_failures}")
    logger.info(f"Median response time: {environment.stats.total.median_response_time}ms")
    logger.info(f"95th percentile: {environment.stats.total.get_response_time_percentile(0.95)}ms")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests."""
    if response_time > 1000:  # Log requests slower than 1 second
        logger.warning(f"Slow request: {name} took {response_time}ms")
```

---

## Week 3: Test Coverage Enhancement

### Day 15-17: Comprehensive Unit Tests

#### Задача 3.1: Core Module Tests
**Файл:** `tests/unit/test_validators.py`

```python
"""
Comprehensive tests for validators module.
"""
import pytest
from datetime import datetime, timedelta
from src.core.validators import (
    StringValidator,
    EmailValidator,
    PhoneValidator,
    NumberValidator,
    DateValidator,
    SchemaValidator,
    validate_email,
    validate_phone,
    validate_positive_number
)


class TestStringValidator:
    """Test string validation."""

    def test_valid_string(self):
        """Test valid string."""
        validator = StringValidator(min_length=2, max_length=10)
        result = validator.validate("hello")

        assert result.is_valid
        assert len(result.errors) == 0

    def test_string_too_short(self):
        """Test string too short."""
        validator = StringValidator(min_length=5)
        result = validator.validate("hi")

        assert not result.is_valid
        assert "Minimum length" in result.errors[0]

    def test_string_too_long(self):
        """Test string too long."""
        validator = StringValidator(max_length=5)
        result = validator.validate("toolongstring")

        assert not result.is_valid
        assert "Maximum length" in result.errors[0]

    def test_pattern_validation(self):
        """Test pattern matching."""
        validator = StringValidator(pattern=r'^[A-Z][a-z]+$')

        # Valid
        assert validator.validate("Hello").is_valid

        # Invalid
        assert not validator.validate("hello").is_valid
        assert not validator.validate("HELLO").is_valid

    def test_allowed_values(self):
        """Test allowed values."""
        validator = StringValidator(allowed_values=['red', 'green', 'blue'])

        assert validator.validate('red').is_valid
        assert not validator.validate('yellow').is_valid

    def test_required_field(self):
        """Test required field."""
        validator = StringValidator(required=True)
        assert not validator.validate(None).is_valid
        assert not validator.validate("").is_valid

    def test_optional_field(self):
        """Test optional field."""
        validator = StringValidator(required=False)
        result = validator.validate(None)
        assert result.is_valid


class TestEmailValidator:
    """Test email validation."""

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "first.last@example.co.uk",
        "user+tag@example.com",
        "test123@test-domain.org"
    ])
    def test_valid_emails(self, email):
        """Test valid email addresses."""
        assert validate_email(email).is_valid

    @pytest.mark.parametrize("email", [
        "invalid",
        "@example.com",
        "user@",
        "user@@example.com",
        "user..name@example.com",
        "user@.com"
    ])
    def test_invalid_emails(self, email):
        """Test invalid email addresses."""
        assert not validate_email(email).is_valid

    def test_empty_email(self):
        """Test empty email."""
        assert not validate_email("").is_valid
        assert not validate_email(None).is_valid


class TestNumberValidator:
    """Test number validation."""

    def test_valid_number(self):
        """Test valid number."""
        validator = NumberValidator(min_value=0, max_value=100)

        assert validator.validate(50).is_valid
        assert validator.validate(0).is_valid
        assert validator.validate(100).is_valid

    def test_out_of_range(self):
        """Test out of range."""
        validator = NumberValidator(min_value=0, max_value=100)

        assert not validator.validate(-1).is_valid
        assert not validator.validate(101).is_valid

    def test_integer_only(self):
        """Test integer only validation."""
        validator = NumberValidator(integer_only=True)

        assert validator.validate(5).is_valid
        assert not validator.validate(5.5).is_valid

    def test_positive_only(self):
        """Test positive only."""
        validator = NumberValidator(positive_only=True)

        assert validator.validate(1).is_valid
        assert validator.validate(0).is_valid
        assert not validator.validate(-1).is_valid

    def test_string_to_number_conversion(self):
        """Test string conversion."""
        validator = NumberValidator()

        assert validator.validate("123").is_valid
        assert validator.validate("123.45").is_valid
        assert not validator.validate("abc").is_valid


class TestDateValidator:
    """Test date validation."""

    def test_valid_date(self):
        """Test valid date."""
        validator = DateValidator()
        assert validator.validate(datetime.now()).is_valid

    def test_future_date(self):
        """Test future date validation."""
        validator = DateValidator(allow_future=False)
        future = datetime.now() + timedelta(days=1)

        assert not validator.validate(future).is_valid

    def test_past_date(self):
        """Test past date validation."""
        validator = DateValidator(allow_past=False)
        past = datetime.now() - timedelta(days=1)

        assert not validator.validate(past).is_valid

    def test_date_range(self):
        """Test date range."""
        min_date = datetime(2020, 1, 1)
        max_date = datetime(2025, 12, 31)
        validator = DateValidator(min_date=min_date, max_date=max_date)

        # Valid
        assert validator.validate(datetime(2023, 6, 15)).is_valid

        # Too early
        assert not validator.validate(datetime(2019, 1, 1)).is_valid

        # Too late
        assert not validator.validate(datetime(2026, 1, 1)).is_valid

    def test_iso_string_parsing(self):
        """Test ISO string parsing."""
        validator = DateValidator()

        assert validator.validate("2023-06-15").is_valid
        assert not validator.validate("invalid-date").is_valid


class TestSchemaValidator:
    """Test schema validation."""

    def test_valid_schema(self):
        """Test valid schema."""
        schema = SchemaValidator({
            'name': StringValidator(min_length=2, max_length=50),
            'email': EmailValidator(),
            'age': NumberValidator(min_value=0, max_value=150, integer_only=True)
        })

        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        }

        result = schema.validate(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_invalid_schema(self):
        """Test invalid schema."""
        schema = SchemaValidator({
            'name': StringValidator(min_length=2),
            'email': EmailValidator()
        })

        data = {
            'name': 'J',  # Too short
            'email': 'invalid-email'  # Invalid
        }

        result = schema.validate(data)
        assert not result.is_valid
        assert len(result.errors) == 2

    def test_missing_fields(self):
        """Test missing required fields."""
        schema = SchemaValidator({
            'name': StringValidator(required=True),
            'email': EmailValidator()
        })

        data = {
            'email': 'test@example.com'
            # name is missing
        }

        result = schema.validate(data)
        assert not result.is_valid


# Integration tests
class TestValidatorIntegration:
    """Integration tests for validators."""

    def test_user_registration_validation(self):
        """Test complete user registration validation."""
        user_schema = SchemaValidator({
            'username': StringValidator(
                min_length=3,
                max_length=20,
                pattern=r'^[a-zA-Z0-9_]+$'
            ),
            'email': EmailValidator(),
            'password': StringValidator(
                min_length=8,
                pattern=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])'
            ),
            'age': NumberValidator(
                min_value=13,
                integer_only=True
            )
        })

        # Valid user
        valid_user = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!',
            'age': 25
        }
        assert user_schema.validate(valid_user).is_valid

        # Invalid username
        invalid_user = {
            'username': 'ab',  # Too short
            'email': 'john@example.com',
            'password': 'SecurePass123!',
            'age': 25
        }
        assert not user_schema.validate(invalid_user).is_valid
```

**Продолжение тестов в следующей секции...**

---

## Week 4: Documentation & Performance

*(Будет добавлено в следующей части)*

---

**Статус документа:** Week 2-4 Complete (Part 1 of 2)
**Следующая часть:** Week 4 + Phase 2 (Analytics & BI)
