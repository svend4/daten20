"""
Login Page Object Model for E2E tests.

This module provides the page object model for the login page.
"""

from tests.e2e.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object model for the login page."""

    # Selectors
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"
    REGISTER_LINK = "#register-link"
    FORGOT_PASSWORD_LINK = "#forgot-password-link"
    ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    LOGIN_FORM = "#login-form"
    REMEMBER_ME_CHECKBOX = "#remember-me"

    def __init__(self, page, base_url: str = "http://localhost:5000"):
        """
        Initialize the login page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)

    def open(self) -> None:
        """Navigate to the login page."""
        self.navigate_to("/login")

    def is_loaded(self) -> bool:
        """
        Check if the login page is loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        return self.is_visible(self.LOGIN_FORM)

    def enter_username(self, username: str) -> None:
        """
        Enter username.

        Args:
            username: Username to enter
        """
        self.fill(self.USERNAME_INPUT, username)

    def enter_password(self, password: str) -> None:
        """
        Enter password.

        Args:
            password: Password to enter
        """
        self.fill(self.PASSWORD_INPUT, password)

    def click_login(self) -> None:
        """Click the login button."""
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str, remember_me: bool = False) -> None:
        """
        Perform login action.

        Args:
            username: Username
            password: Password
            remember_me: Whether to check "Remember Me" checkbox
        """
        self.enter_username(username)
        self.enter_password(password)

        if remember_me and self.is_visible(self.REMEMBER_ME_CHECKBOX):
            self.check(self.REMEMBER_ME_CHECKBOX)

        self.click_login()

    def click_register_link(self) -> None:
        """Click the register link."""
        if self.is_visible(self.REGISTER_LINK):
            self.click(self.REGISTER_LINK)

    def click_forgot_password_link(self) -> None:
        """Click the forgot password link."""
        if self.is_visible(self.FORGOT_PASSWORD_LINK):
            self.click(self.FORGOT_PASSWORD_LINK)

    def get_error_message(self) -> str:
        """
        Get error message if visible.

        Returns:
            Error message text or empty string
        """
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""

    def has_error(self) -> bool:
        """
        Check if error message is displayed.

        Returns:
            True if error is visible
        """
        return self.is_visible(self.ERROR_MESSAGE)

    def get_success_message(self) -> str:
        """
        Get success message if visible.

        Returns:
            Success message text or empty string
        """
        if self.is_visible(self.SUCCESS_MESSAGE):
            return self.get_text(self.SUCCESS_MESSAGE)
        return ""
