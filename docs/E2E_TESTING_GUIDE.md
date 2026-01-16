# E2E Testing Guide

## Document Management System - End-to-End Testing

**Version:** 1.0
**Date:** 2026-01-16
**Status:** Complete

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Page Object Models](#page-object-models)
- [Writing New Tests](#writing-new-tests)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

---

## Overview

This guide covers the end-to-end (E2E) testing framework for the Document Management System. E2E tests simulate real user interactions with the application using Playwright browser automation.

### What is E2E Testing?

End-to-end testing verifies that the complete application workflow functions correctly from the user's perspective. These tests:

- Run in a real browser (Chromium, Firefox, or WebKit)
- Simulate actual user interactions (clicks, typing, navigation)
- Test the entire application stack (frontend, backend, database)
- Validate user journeys and workflows

### Coverage

The E2E test suite includes **52 tests** covering:

1. **User Registration and First Upload** (11 tests)
   - Registration flow
   - Login functionality
   - First document upload experience

2. **Document Processing Pipeline** (11 tests)
   - Document upload (text, markdown)
   - Metadata extraction
   - Batch processing
   - Search integration

3. **Search and Filter** (14 tests)
   - Keyword search
   - Semantic search
   - Filters and sorting
   - Advanced search features

4. **Admin Operations** (16 tests)
   - User management
   - System management
   - Audit logging
   - Document management

---

## Architecture

### Technology Stack

- **Playwright** - Browser automation framework
- **pytest** - Test framework
- **pytest-playwright** - Pytest plugin for Playwright
- **Page Object Model (POM)** - Design pattern for test structure

### Directory Structure

```
tests/e2e/
├── conftest.py                        # Pytest fixtures and configuration
├── __init__.py
├── pages/                             # Page Object Models
│   ├── __init__.py
│   ├── base_page.py                   # Base class for all pages
│   ├── home_page.py                   # Home/Dashboard page
│   ├── login_page.py                  # Login page
│   ├── register_page.py               # Registration page
│   ├── document_upload_page.py        # Upload page
│   ├── search_page.py                 # Search page
│   └── admin_page.py                  # Admin page
├── test_user_registration_and_upload.py   # Registration & upload tests
├── test_document_processing.py            # Document processing tests
├── test_search_and_filter.py              # Search tests
└── test_admin_operations.py               # Admin tests
```

---

## Setup

### Prerequisites

- Python 3.9+
- Node.js (for Playwright browser installation)
- Document Management System running locally

### Installation

#### 1. Install Dependencies

```bash
# Install Playwright and pytest-playwright
pip install playwright pytest-playwright

# Install Playwright browsers
playwright install chromium
```

#### 2. Verify Installation

```bash
# Check Playwright installation
playwright --version

# List installed browsers
playwright list
```

#### 3. Start Application

E2E tests require the application to be running:

```bash
# Start the application (in a separate terminal)
python doc-dashboard.py

# Application should be accessible at http://localhost:5000
```

---

## Running Tests

### Run All E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run with Playwright trace (for debugging)
pytest tests/e2e/ --tracing on

# Run in headed mode (visible browser)
pytest tests/e2e/ --headed
```

### Run Specific Test Files

```bash
# Run registration tests only
pytest tests/e2e/test_user_registration_and_upload.py -v

# Run search tests only
pytest tests/e2e/test_search_and_filter.py -v

# Run admin tests only
pytest tests/e2e/test_admin_operations.py -v
```

### Run Specific Tests

```bash
# Run a single test
pytest tests/e2e/test_user_registration_and_upload.py::TestUserRegistration::test_01_registration_page_loads -v

# Run tests matching pattern
pytest tests/e2e/ -k "registration" -v

# Run tests with marker
pytest tests/e2e/ -m "e2e" -v
```

### Run with Different Browsers

```bash
# Run with Firefox
pytest tests/e2e/ --browser firefox

# Run with WebKit (Safari)
pytest tests/e2e/ --browser webkit

# Run with all browsers
pytest tests/e2e/ --browser chromium --browser firefox --browser webkit
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/e2e/ -n 4  # 4 parallel workers
```

---

## Test Structure

### Test Organization

Each test file contains multiple test classes:

```python
# test_user_registration_and_upload.py

class TestUserRegistration:
    """Test suite for user registration flow."""

    def test_01_registration_page_loads(self, page):
        """Test that registration page loads successfully."""
        # Test implementation

    def test_02_successful_registration(self, page):
        """Test successful user registration."""
        # Test implementation

class TestFirstDocumentUpload:
    """Test suite for first document upload experience."""

    def test_06_navigate_to_upload_page(self, page):
        """Test navigation to upload page."""
        # Test implementation

class TestUserJourneySummary:
    """Summary test for complete user journey."""

    def test_complete_registration_to_upload_journey(self, page):
        """Test complete user journey from registration to upload."""
        # Test implementation
```

### Test Naming Convention

- Tests are numbered sequentially: `test_01_`, `test_02_`, etc.
- Names are descriptive and indicate what is being tested
- Summary tests are placed at the end of each file

### Test Fixtures

Common fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def test_user():
    """Generate test user credentials."""
    return {
        "username": "testuser_abc123",
        "email": "test_abc123@example.com",
        "password": "TestPass123!"
    }

@pytest.fixture
def authenticated_page(page):
    """Create authenticated session."""
    # Register and login
    # Return authenticated page
```

---

## Page Object Models

### What is Page Object Model?

Page Object Model (POM) is a design pattern that:

- Creates a separate class for each page
- Encapsulates page elements and actions
- Makes tests more maintainable and readable
- Reduces code duplication

### Base Page

All page objects inherit from `BasePage`:

```python
from tests.e2e.pages.base_page import BasePage

class LoginPage(BasePage):
    # Selectors
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"

    def login(self, username: str, password: str):
        """Perform login action."""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
```

### Available Page Objects

1. **BasePage** - Base class with common functionality
   - `navigate_to(path)` - Navigate to URL
   - `click(selector)` - Click element
   - `fill(selector, value)` - Fill input
   - `wait_for_selector(selector)` - Wait for element
   - And many more...

2. **HomePage** - Home/Dashboard page
   - `open()` - Navigate to home
   - `click_upload_button()` - Go to upload
   - `navigate_to_admin()` - Go to admin

3. **LoginPage** - Login page
   - `open()` - Navigate to login
   - `login(username, password)` - Perform login
   - `get_error_message()` - Get error text

4. **RegisterPage** - Registration page
   - `open()` - Navigate to register
   - `register(...)` - Perform registration
   - `has_success()` - Check success

5. **DocumentUploadPage** - Upload page
   - `open()` - Navigate to upload
   - `upload_document(...)` - Upload file
   - `wait_for_upload_complete()` - Wait for upload

6. **SearchPage** - Search page
   - `open()` - Navigate to search
   - `search(query)` - Perform search
   - `enable_semantic_search()` - Enable semantic
   - `get_results()` - Get search results

7. **AdminPage** - Admin page
   - `open()` - Navigate to admin
   - `click_users_tab()` - Switch to users
   - `create_user(...)` - Create new user
   - `get_audit_log_count()` - Get audit entries

---

## Writing New Tests

### Step 1: Create Test File

```python
"""
E2E Tests for New Feature.

Description of what this test file covers.
"""

import pytest
from playwright.sync_api import Page
from tests.e2e.pages import HomePage, LoginPage

class TestNewFeature:
    """Test suite for new feature."""

    def test_01_feature_loads(self, page: Page):
        """
        Test that new feature page loads.

        Steps:
        1. Navigate to feature page
        2. Verify page elements

        Expected:
        - Page loads successfully
        - Elements are visible
        """
        # Test implementation
        assert True
```

### Step 2: Use Page Objects

```python
def test_02_feature_interaction(self, page: Page):
    """Test interaction with new feature."""
    # Use page objects
    home_page = HomePage(page)
    home_page.open()

    # Perform actions
    home_page.click_new_feature_button()

    # Verify results
    page.wait_for_timeout(1000)
    assert page.url.endswith("/new-feature")
```

### Step 3: Add Fixtures if Needed

```python
@pytest.fixture
def feature_data():
    """Test data for feature."""
    return {
        "name": "Test Feature",
        "value": 42
    }

def test_03_with_fixture(self, page: Page, feature_data):
    """Test using custom fixture."""
    # Use fixture data
    assert feature_data["value"] == 42
```

### Step 4: Run New Tests

```bash
pytest tests/e2e/test_new_feature.py -v
```

---

## Best Practices

### 1. Use Page Object Model

✅ **DO:**
```python
login_page = LoginPage(page)
login_page.login("user", "pass")
```

❌ **DON'T:**
```python
page.fill("#username", "user")
page.fill("#password", "pass")
page.click("#login-btn")
```

### 2. Use Descriptive Test Names

✅ **DO:**
```python
def test_user_can_upload_pdf_document(self, page):
    """Test that user can successfully upload a PDF document."""
```

❌ **DON'T:**
```python
def test_upload(self, page):
    """Test upload."""
```

### 3. Add Wait Times When Needed

```python
# Wait for page load
page.wait_for_load_state("networkidle")

# Wait for element
page.wait_for_selector("#results", timeout=5000)

# Wait for timeout (use sparingly)
page.wait_for_timeout(1000)
```

### 4. Use Fixtures for Setup

```python
@pytest.fixture
def authenticated_user(page):
    """Setup authenticated user."""
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("user", "pass")
    yield page
    # Cleanup if needed
```

### 5. Handle Errors Gracefully

```python
try:
    page.wait_for_selector("#element", timeout=3000)
except Exception:
    # Element not found, that's okay
    pass
```

### 6. Take Screenshots on Failure

Automatic screenshot is configured in `conftest.py`:

```python
@pytest.fixture
def screenshot_on_failure(request, page):
    """Take screenshot on test failure."""
    yield
    if request.node.rep_call.failed:
        page.screenshot(path=f"screenshots/{request.node.name}.png")
```

### 7. Clean Up Test Data

```python
@pytest.fixture
def test_file():
    """Create test file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test data")
        file_path = f.name

    yield file_path

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)
```

---

## Troubleshooting

### Common Issues

#### 1. Application Not Running

**Error:** `net::ERR_CONNECTION_REFUSED`

**Solution:**
```bash
# Start the application
python doc-dashboard.py

# Verify it's running
curl http://localhost:5000
```

#### 2. Browser Not Installed

**Error:** `Executable doesn't exist at /path/to/browser`

**Solution:**
```bash
playwright install chromium
```

#### 3. Element Not Found

**Error:** `waiting for selector "#element" to be visible`

**Solution:**
- Check if selector is correct
- Add longer timeout
- Check if element exists in the page
- Use flexible checks with `is_visible()`

#### 4. Tests Running Slow

**Solution:**
```bash
# Run in headless mode (default)
pytest tests/e2e/ --headed=false

# Run in parallel
pytest tests/e2e/ -n 4

# Reduce timeouts in tests
```

#### 5. Flaky Tests

**Causes:**
- Timing issues (race conditions)
- Network delays
- Dynamic content loading

**Solutions:**
- Add appropriate wait times
- Use `wait_for_selector()` instead of fixed timeouts
- Check for element visibility before interaction
- Make assertions flexible

### Debug Mode

Run tests with debug options:

```bash
# Show browser (headed mode)
pytest tests/e2e/ --headed

# Enable tracing
pytest tests/e2e/ --tracing on

# Slow down execution
pytest tests/e2e/ --slowmo 1000

# Pause on failure
pytest tests/e2e/ --pause-on-failure
```

### View Playwright Trace

```bash
# Generate trace
pytest tests/e2e/ --tracing on

# View trace
playwright show-trace trace.zip
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install playwright pytest-playwright
        playwright install --with-deps chromium

    - name: Start application
      run: |
        python doc-dashboard.py &
        sleep 10  # Wait for app to start

    - name: Run E2E tests
      run: |
        pytest tests/e2e/ -v --html=report.html

    - name: Upload test report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: e2e-test-report
        path: report.html

    - name: Upload screenshots
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: screenshots
        path: tests/e2e/screenshots/
```

### Running in Docker

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN playwright install

CMD ["pytest", "tests/e2e/", "-v"]
```

---

## Test Statistics

### Test Counts

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| User Registration & Upload | 11 | Registration, Login, First Upload |
| Document Processing | 11 | Upload, Metadata, Search Integration |
| Search & Filter | 14 | Keyword, Semantic, Filters |
| Admin Operations | 16 | Users, System, Audit, Documents |
| **Total** | **52** | **Complete E2E Coverage** |

### Execution Time

- **Average:** ~2-3 minutes (headless)
- **Per Test:** ~3-5 seconds
- **Parallel (4 workers):** ~1 minute

---

## Additional Resources

### Documentation

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [Page Object Model Pattern](https://playwright.dev/python/docs/pom)

### Related Guides

- [Integration Testing Guide](docs/INTEGRATION_TESTING_GUIDE.md)
- [CI/CD Guide](docs/CICD_GUIDE.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

## Summary

The E2E testing framework provides comprehensive coverage of the Document Management System's user-facing functionality. With 52 tests across 4 test suites, we ensure that all critical user journeys work as expected.

**Key Features:**
- ✅ 52 comprehensive E2E tests
- ✅ Page Object Model architecture
- ✅ Automatic screenshots on failure
- ✅ Flexible and maintainable tests
- ✅ CI/CD ready
- ✅ Parallel execution support

**Next Steps:**
1. Run the tests: `pytest tests/e2e/ -v`
2. Review test coverage
3. Add tests for new features
4. Integrate with CI/CD pipeline

---

**Version:** 1.0
**Last Updated:** 2026-01-16
**Status:** ✅ Complete and Production-Ready
