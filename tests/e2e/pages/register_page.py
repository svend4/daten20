"""
Register Page Object Model for E2E tests.

This module provides the page object model for the registration page.
"""

from tests.e2e.pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page object model for the registration page."""

    # Selectors
    USERNAME_INPUT = "#username"
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    CONFIRM_PASSWORD_INPUT = "#confirm-password"
    FIRST_NAME_INPUT = "#first-name"
    LAST_NAME_INPUT = "#last-name"
    REGISTER_BUTTON = "#register-btn"
    LOGIN_LINK = "#login-link"
    ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    REGISTER_FORM = "#register-form"
    TERMS_CHECKBOX = "#accept-terms"

    def __init__(self, page, base_url: str = "http://localhost:5000"):
        """
        Initialize the register page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)

    def open(self) -> None:
        """Navigate to the registration page."""
        self.navigate_to("/register")

    def is_loaded(self) -> bool:
        """
        Check if the registration page is loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        return self.is_visible(self.REGISTER_FORM)

    def enter_username(self, username: str) -> None:
        """
        Enter username.

        Args:
            username: Username to enter
        """
        self.fill(self.USERNAME_INPUT, username)

    def enter_email(self, email: str) -> None:
        """
        Enter email.

        Args:
            email: Email to enter
        """
        self.fill(self.EMAIL_INPUT, email)

    def enter_password(self, password: str) -> None:
        """
        Enter password.

        Args:
            password: Password to enter
        """
        self.fill(self.PASSWORD_INPUT, password)

    def enter_confirm_password(self, password: str) -> None:
        """
        Enter confirm password.

        Args:
            password: Confirm password to enter
        """
        self.fill(self.CONFIRM_PASSWORD_INPUT, password)

    def enter_first_name(self, first_name: str) -> None:
        """
        Enter first name.

        Args:
            first_name: First name to enter
        """
        if self.is_visible(self.FIRST_NAME_INPUT):
            self.fill(self.FIRST_NAME_INPUT, first_name)

    def enter_last_name(self, last_name: str) -> None:
        """
        Enter last name.

        Args:
            last_name: Last name to enter
        """
        if self.is_visible(self.LAST_NAME_INPUT):
            self.fill(self.LAST_NAME_INPUT, last_name)

    def accept_terms(self) -> None:
        """Accept terms and conditions."""
        if self.is_visible(self.TERMS_CHECKBOX):
            self.check(self.TERMS_CHECKBOX)

    def click_register(self) -> None:
        """Click the register button."""
        self.click(self.REGISTER_BUTTON)

    def register(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        accept_terms: bool = True,
    ) -> None:
        """
        Perform registration action.

        Args:
            username: Username
            email: Email address
            password: Password
            first_name: First name (optional)
            last_name: Last name (optional)
            accept_terms: Whether to accept terms
        """
        self.enter_username(username)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_confirm_password(password)

        if first_name:
            self.enter_first_name(first_name)

        if last_name:
            self.enter_last_name(last_name)

        if accept_terms:
            self.accept_terms()

        self.click_register()

    def click_login_link(self) -> None:
        """Click the login link."""
        if self.is_visible(self.LOGIN_LINK):
            self.click(self.LOGIN_LINK)

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

    def has_success(self) -> bool:
        """
        Check if success message is displayed.

        Returns:
            True if success is visible
        """
        return self.is_visible(self.SUCCESS_MESSAGE)
