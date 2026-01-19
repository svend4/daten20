"""
Pytest configuration and fixtures for E2E tests.

This module provides Playwright fixtures and configuration for E2E testing.
"""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test using Playwright"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running test"
    )


# Playwright fixtures
@pytest.fixture(scope="session")
def browser_type_launch_args():
    """
    Browser launch arguments.

    Returns:
        dict: Arguments for browser launch
    """
    return {
        "headless": True,  # Run in headless mode by default
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
        ],
    }


@pytest.fixture(scope="session")
def browser_context_args():
    """
    Browser context arguments.

    Returns:
        dict: Arguments for browser context
    """
    return {
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def context(browser: Browser, browser_context_args):
    """
    Create a new browser context for each test.

    Args:
        browser: Playwright browser instance
        browser_context_args: Context arguments

    Yields:
        BrowserContext: New browser context
    """
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """
    Create a new page for each test.

    Args:
        context: Browser context

    Yields:
        Page: New page instance
    """
    page = context.new_page()
    yield page
    page.close()


# Application-specific fixtures
@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the application.

    Returns:
        str: Base URL
    """
    return "http://localhost:5000"


@pytest.fixture
def screenshot_on_failure(request, page: Page):
    """
    Take screenshot on test failure.

    Args:
        request: Pytest request fixture
        page: Playwright page
    """
    yield

    if request.node.rep_call.failed:
        # Create screenshots directory if it doesn't exist
        import os
        from pathlib import Path

        screenshots_dir = Path("tests/e2e/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Take screenshot
        screenshot_path = screenshots_dir / f"{request.node.name}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"\nScreenshot saved: {screenshot_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Make test result available to fixtures.

    This allows the screenshot_on_failure fixture to access test results.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# Helper fixtures for common operations
@pytest.fixture
def test_user():
    """
    Generate test user credentials.

    Returns:
        dict: User credentials
    """
    import random
    import string

    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "username": f"testuser_{random_suffix}",
        "email": f"test_{random_suffix}@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def admin_user():
    """
    Generate admin user credentials.

    Returns:
        dict: Admin credentials
    """
    import random
    import string

    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "username": f"admin_{random_suffix}",
        "email": f"admin_{random_suffix}@example.com",
        "password": "AdminPass123!",
        "role": "admin",
    }


# Performance tracking
@pytest.fixture(autouse=True)
def track_test_time(request):
    """
    Track test execution time.

    Args:
        request: Pytest request fixture
    """
    import time

    start_time = time.time()
    yield
    end_time = time.time()
    duration = end_time - start_time

    if duration > 10:  # Warn for slow tests (> 10 seconds)
        print(f"\n⚠️  Slow test: {request.node.name} took {duration:.2f}s")


# Cleanup fixtures
@pytest.fixture(scope="session", autouse=True)
def cleanup_screenshots():
    """
    Cleanup old screenshots before test run.
    """
    import shutil
    from pathlib import Path

    screenshots_dir = Path("tests/e2e/screenshots")
    if screenshots_dir.exists():
        # Clear old screenshots
        for file in screenshots_dir.glob("*.png"):
            try:
                file.unlink()
            except Exception:
                pass

    yield

    # Can add post-test cleanup here if needed


# Test data fixtures
@pytest.fixture
def sample_text_file():
    """
    Create a sample text file for testing.

    Yields:
        str: Path to temporary file
    """
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write("Sample Document\n")
        f.write("=" * 40 + "\n\n")
        f.write("This is a sample document for E2E testing.\n")
        f.write("It contains multiple lines of text.\n\n")
        f.write("Keywords: test, sample, document, e2e\n")
        file_path = f.name

    yield file_path

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def sample_markdown_file():
    """
    Create a sample markdown file for testing.

    Yields:
        str: Path to temporary file
    """
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("# Sample Markdown\n\n")
        f.write("## Section 1\n\n")
        f.write("This is a **markdown** document.\n\n")
        f.write("## Section 2\n\n")
        f.write("- Item 1\n")
        f.write("- Item 2\n")
        f.write("- Item 3\n")
        file_path = f.name

    yield file_path

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)


# Wait helpers
@pytest.fixture
def wait_for_element():
    """
    Helper function to wait for element.

    Returns:
        callable: Wait function
    """

    def _wait(page: Page, selector: str, timeout: int = 5000):
        """
        Wait for element to be visible.

        Args:
            page: Playwright page
            selector: CSS selector
            timeout: Timeout in milliseconds

        Returns:
            bool: True if element appeared, False otherwise
        """
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False

    return _wait


@pytest.fixture
def wait_for_navigation():
    """
    Helper function to wait for navigation.

    Returns:
        callable: Wait function
    """

    def _wait(page: Page, url_pattern: str = None, timeout: int = 5000):
        """
        Wait for navigation to complete.

        Args:
            page: Playwright page
            url_pattern: Optional URL pattern to wait for
            timeout: Timeout in milliseconds

        Returns:
            bool: True if navigation completed
        """
        try:
            if url_pattern:
                page.wait_for_url(url_pattern, timeout=timeout)
            else:
                page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except Exception:
            return False

    return _wait
