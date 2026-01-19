"""
Base Page Object Model for E2E tests.

This module provides the base class for all page object models,
containing common functionality and utilities.
"""

from typing import Optional
from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page object models."""

    def __init__(self, page: Page, base_url: str = "http://localhost:5000"):
        """
        Initialize the base page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        self.page = page
        self.base_url = base_url

    def navigate_to(self, path: str = "/") -> None:
        """
        Navigate to a specific path.

        Args:
            path: URL path to navigate to
        """
        url = f"{self.base_url}{path}"
        self.page.goto(url)

    def get_title(self) -> str:
        """
        Get the page title.

        Returns:
            Page title
        """
        return self.page.title()

    def wait_for_url(self, url: str, timeout: int = 5000) -> None:
        """
        Wait for URL to match.

        Args:
            url: Expected URL pattern
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_url(url, timeout=timeout)

    def wait_for_selector(self, selector: str, timeout: int = 5000) -> None:
        """
        Wait for element to be visible.

        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector: str) -> None:
        """
        Click an element.

        Args:
            selector: CSS selector
        """
        self.page.click(selector)

    def fill(self, selector: str, value: str) -> None:
        """
        Fill an input field.

        Args:
            selector: CSS selector
            value: Value to fill
        """
        self.page.fill(selector, value)

    def get_text(self, selector: str) -> str:
        """
        Get text content of an element.

        Args:
            selector: CSS selector

        Returns:
            Text content
        """
        return self.page.text_content(selector) or ""

    def is_visible(self, selector: str) -> bool:
        """
        Check if element is visible.

        Args:
            selector: CSS selector

        Returns:
            True if visible, False otherwise
        """
        return self.page.is_visible(selector)

    def screenshot(self, path: str) -> None:
        """
        Take a screenshot.

        Args:
            path: Path to save screenshot
        """
        self.page.screenshot(path=path)

    def expect_visible(self, selector: str) -> None:
        """
        Assert that element is visible.

        Args:
            selector: CSS selector
        """
        expect(self.page.locator(selector)).to_be_visible()

    def expect_text(self, selector: str, text: str) -> None:
        """
        Assert that element contains text.

        Args:
            selector: CSS selector
            text: Expected text
        """
        expect(self.page.locator(selector)).to_contain_text(text)

    def select_option(self, selector: str, value: str) -> None:
        """
        Select an option from a dropdown.

        Args:
            selector: CSS selector
            value: Value to select
        """
        self.page.select_option(selector, value)

    def check(self, selector: str) -> None:
        """
        Check a checkbox.

        Args:
            selector: CSS selector
        """
        self.page.check(selector)

    def uncheck(self, selector: str) -> None:
        """
        Uncheck a checkbox.

        Args:
            selector: CSS selector
        """
        self.page.uncheck(selector)

    def upload_file(self, selector: str, file_path: str) -> None:
        """
        Upload a file.

        Args:
            selector: CSS selector of file input
            file_path: Path to file to upload
        """
        self.page.set_input_files(selector, file_path)

    def wait_for_load_state(self, state: str = "load") -> None:
        """
        Wait for page load state.

        Args:
            state: Load state ('load', 'domcontentloaded', 'networkidle')
        """
        self.page.wait_for_load_state(state)

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload()

    def go_back(self) -> None:
        """Navigate back in history."""
        self.page.go_back()

    def go_forward(self) -> None:
        """Navigate forward in history."""
        self.page.go_forward()

    def get_url(self) -> str:
        """
        Get current URL.

        Returns:
            Current page URL
        """
        return self.page.url

    def execute_script(self, script: str) -> Optional[any]:
        """
        Execute JavaScript.

        Args:
            script: JavaScript code to execute

        Returns:
            Result of script execution
        """
        return self.page.evaluate(script)

    def hover(self, selector: str) -> None:
        """
        Hover over an element.

        Args:
            selector: CSS selector
        """
        self.page.hover(selector)

    def press_key(self, key: str) -> None:
        """
        Press a keyboard key.

        Args:
            key: Key to press (e.g., 'Enter', 'Escape')
        """
        self.page.keyboard.press(key)
