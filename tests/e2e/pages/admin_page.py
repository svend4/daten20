"""
Admin Page Object Model for E2E tests.

This module provides the page object model for the admin page.
"""

from tests.e2e.pages.base_page import BasePage


class AdminPage(BasePage):
    """Page object model for the admin page."""

    # Selectors
    USERS_TAB = "#users-tab"
    DOCUMENTS_TAB = "#documents-tab"
    SYSTEM_TAB = "#system-tab"
    TENANTS_TAB = "#tenants-tab"
    AUDIT_TAB = "#audit-tab"

    # User management
    CREATE_USER_BUTTON = "#create-user-btn"
    USER_LIST = "#user-list"
    USER_ITEM = ".user-item"
    EDIT_USER_BUTTON = ".edit-user-btn"
    DELETE_USER_BUTTON = ".delete-user-btn"
    USERNAME_INPUT = "#username"
    EMAIL_INPUT = "#email"
    ROLE_SELECT = "#role"
    SAVE_USER_BUTTON = "#save-user-btn"

    # System management
    BACKUP_BUTTON = "#backup-btn"
    RESTORE_BUTTON = "#restore-btn"
    CLEAR_CACHE_BUTTON = "#clear-cache-btn"
    SYSTEM_STATUS = "#system-status"
    DATABASE_STATUS = "#database-status"
    REDIS_STATUS = "#redis-status"

    # Audit log
    AUDIT_LOG = "#audit-log"
    AUDIT_ITEM = ".audit-item"
    DATE_RANGE_FROM = "#date-from"
    DATE_RANGE_TO = "#date-to"
    AUDIT_FILTER_BUTTON = "#audit-filter-btn"

    # Messages
    SUCCESS_MESSAGE = ".success-message"
    ERROR_MESSAGE = ".error-message"
    CONFIRMATION_DIALOG = "#confirmation-dialog"
    CONFIRM_BUTTON = "#confirm-btn"
    CANCEL_BUTTON = "#cancel-btn"

    def __init__(self, page, base_url: str = "http://localhost:5000"):
        """
        Initialize the admin page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)

    def open(self) -> None:
        """Navigate to the admin page."""
        self.navigate_to("/admin")

    def is_loaded(self) -> bool:
        """
        Check if the admin page is loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        return self.is_visible(self.USERS_TAB)

    def click_users_tab(self) -> None:
        """Click the users tab."""
        self.click(self.USERS_TAB)

    def click_documents_tab(self) -> None:
        """Click the documents tab."""
        self.click(self.DOCUMENTS_TAB)

    def click_system_tab(self) -> None:
        """Click the system tab."""
        self.click(self.SYSTEM_TAB)

    def click_tenants_tab(self) -> None:
        """Click the tenants tab."""
        if self.is_visible(self.TENANTS_TAB):
            self.click(self.TENANTS_TAB)

    def click_audit_tab(self) -> None:
        """Click the audit tab."""
        self.click(self.AUDIT_TAB)

    # User management methods
    def click_create_user(self) -> None:
        """Click create user button."""
        self.click(self.CREATE_USER_BUTTON)

    def create_user(self, username: str, email: str, role: str = "user") -> None:
        """
        Create a new user.

        Args:
            username: Username
            email: Email address
            role: User role
        """
        self.click_create_user()
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.EMAIL_INPUT, email)
        self.select_option(self.ROLE_SELECT, role)
        self.click(self.SAVE_USER_BUTTON)

    def get_users_count(self) -> int:
        """
        Get number of users.

        Returns:
            Number of users
        """
        if not self.is_visible(self.USER_LIST):
            return 0

        users = self.page.query_selector_all(self.USER_ITEM)
        return len(users)

    def delete_user(self, index: int = 0) -> None:
        """
        Delete a user.

        Args:
            index: Index of user to delete (0-based)
        """
        delete_buttons = self.page.query_selector_all(self.DELETE_USER_BUTTON)
        if index < len(delete_buttons):
            delete_buttons[index].click()
            # Confirm deletion if confirmation dialog appears
            if self.is_visible(self.CONFIRMATION_DIALOG):
                self.click(self.CONFIRM_BUTTON)

    # System management methods
    def click_backup(self) -> None:
        """Click backup button."""
        self.click(self.BACKUP_BUTTON)

    def click_restore(self) -> None:
        """Click restore button."""
        self.click(self.RESTORE_BUTTON)

    def click_clear_cache(self) -> None:
        """Click clear cache button."""
        self.click(self.CLEAR_CACHE_BUTTON)

    def get_system_status(self) -> str:
        """
        Get system status.

        Returns:
            System status text
        """
        if self.is_visible(self.SYSTEM_STATUS):
            return self.get_text(self.SYSTEM_STATUS)
        return ""

    def get_database_status(self) -> str:
        """
        Get database status.

        Returns:
            Database status text
        """
        if self.is_visible(self.DATABASE_STATUS):
            return self.get_text(self.DATABASE_STATUS)
        return ""

    def get_redis_status(self) -> str:
        """
        Get Redis status.

        Returns:
            Redis status text
        """
        if self.is_visible(self.REDIS_STATUS):
            return self.get_text(self.REDIS_STATUS)
        return ""

    # Audit log methods
    def get_audit_log_count(self) -> int:
        """
        Get number of audit log entries.

        Returns:
            Number of audit log entries
        """
        if not self.is_visible(self.AUDIT_LOG):
            return 0

        entries = self.page.query_selector_all(self.AUDIT_ITEM)
        return len(entries)

    def filter_audit_log(self, date_from: str, date_to: str) -> None:
        """
        Filter audit log by date range.

        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
        """
        if self.is_visible(self.DATE_RANGE_FROM):
            self.fill(self.DATE_RANGE_FROM, date_from)
        if self.is_visible(self.DATE_RANGE_TO):
            self.fill(self.DATE_RANGE_TO, date_to)
        self.click(self.AUDIT_FILTER_BUTTON)

    # Common methods
    def get_success_message(self) -> str:
        """
        Get success message.

        Returns:
            Success message text
        """
        if self.is_visible(self.SUCCESS_MESSAGE):
            return self.get_text(self.SUCCESS_MESSAGE)
        return ""

    def get_error_message(self) -> str:
        """
        Get error message.

        Returns:
            Error message text
        """
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""

    def has_success(self) -> bool:
        """
        Check if success message is displayed.

        Returns:
            True if success message is visible
        """
        return self.is_visible(self.SUCCESS_MESSAGE)

    def has_error(self) -> bool:
        """
        Check if error message is displayed.

        Returns:
            True if error message is visible
        """
        return self.is_visible(self.ERROR_MESSAGE)
