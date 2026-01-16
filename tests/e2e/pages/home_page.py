"""
Home Page Object Model for E2E tests.

This module provides the page object model for the home/dashboard page.
"""

from tests.e2e.pages.base_page import BasePage


class HomePage(BasePage):
    """Page object model for the home/dashboard page."""

    # Selectors
    STATS_SECTION = "#stats-section"
    UPLOAD_BUTTON = "#upload-btn"
    SEARCH_BUTTON = "#search-btn"
    RECENT_DOCUMENTS = "#recent-documents"
    USER_MENU = "#user-menu"
    LOGOUT_LINK = "#logout-link"
    DOCUMENTS_COUNT = "#documents-count"
    USERS_COUNT = "#users-count"
    STORAGE_USED = "#storage-used"
    WELCOME_MESSAGE = ".welcome-message"
    NAVIGATION_MENU = "nav.main-nav"
    DOCUMENTS_LINK = "a[href='/documents']"
    SEARCH_LINK = "a[href='/search']"
    UPLOAD_LINK = "a[href='/upload']"
    ADMIN_LINK = "a[href='/admin']"

    def __init__(self, page, base_url: str = "http://localhost:5000"):
        """
        Initialize the home page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)

    def open(self) -> None:
        """Navigate to the home page."""
        self.navigate_to("/")

    def is_loaded(self) -> bool:
        """
        Check if the home page is loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        return self.is_visible(self.WELCOME_MESSAGE) or self.is_visible(self.NAVIGATION_MENU)

    def get_documents_count(self) -> str:
        """
        Get the documents count from stats.

        Returns:
            Documents count as string
        """
        if self.is_visible(self.DOCUMENTS_COUNT):
            return self.get_text(self.DOCUMENTS_COUNT)
        return "0"

    def get_users_count(self) -> str:
        """
        Get the users count from stats.

        Returns:
            Users count as string
        """
        if self.is_visible(self.USERS_COUNT):
            return self.get_text(self.USERS_COUNT)
        return "0"

    def get_storage_used(self) -> str:
        """
        Get the storage used from stats.

        Returns:
            Storage used as string
        """
        if self.is_visible(self.STORAGE_USED):
            return self.get_text(self.STORAGE_USED)
        return "0 MB"

    def click_upload_button(self) -> None:
        """Click the upload button."""
        if self.is_visible(self.UPLOAD_BUTTON):
            self.click(self.UPLOAD_BUTTON)
        elif self.is_visible(self.UPLOAD_LINK):
            self.click(self.UPLOAD_LINK)

    def click_search_button(self) -> None:
        """Click the search button."""
        if self.is_visible(self.SEARCH_BUTTON):
            self.click(self.SEARCH_BUTTON)
        elif self.is_visible(self.SEARCH_LINK):
            self.click(self.SEARCH_LINK)

    def navigate_to_documents(self) -> None:
        """Navigate to documents page."""
        if self.is_visible(self.DOCUMENTS_LINK):
            self.click(self.DOCUMENTS_LINK)

    def navigate_to_admin(self) -> None:
        """Navigate to admin page."""
        if self.is_visible(self.ADMIN_LINK):
            self.click(self.ADMIN_LINK)

    def logout(self) -> None:
        """Logout from the application."""
        if self.is_visible(self.USER_MENU):
            self.click(self.USER_MENU)
            self.wait_for_selector(self.LOGOUT_LINK)
            self.click(self.LOGOUT_LINK)

    def get_recent_documents(self) -> list[str]:
        """
        Get list of recent documents.

        Returns:
            List of document names
        """
        if not self.is_visible(self.RECENT_DOCUMENTS):
            return []

        # Get all document items
        documents = self.page.query_selector_all(f"{self.RECENT_DOCUMENTS} .document-item")
        return [doc.text_content() or "" for doc in documents]

    def has_stats_section(self) -> bool:
        """
        Check if stats section is visible.

        Returns:
            True if stats section is visible
        """
        return self.is_visible(self.STATS_SECTION)
