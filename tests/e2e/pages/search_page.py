"""
Search Page Object Model for E2E tests.

This module provides the page object model for the search page.
"""

from tests.e2e.pages.base_page import BasePage


class SearchPage(BasePage):
    """Page object model for the search page."""

    # Selectors
    SEARCH_INPUT = "#search-input"
    SEARCH_BUTTON = "#search-btn"
    SEARCH_RESULTS = "#search-results"
    RESULT_ITEM = ".result-item"
    NO_RESULTS_MESSAGE = "#no-results"
    FILTERS_SECTION = "#filters"
    DATE_FILTER = "#date-filter"
    TYPE_FILTER = "#type-filter"
    TAGS_FILTER = "#tags-filter"
    SORT_SELECT = "#sort-by"
    SEMANTIC_SEARCH_CHECKBOX = "#semantic-search"
    ADVANCED_SEARCH_LINK = "#advanced-search"
    RESULTS_COUNT = "#results-count"
    PAGINATION = ".pagination"

    def __init__(self, page, base_url: str = "http://localhost:5000"):
        """
        Initialize the search page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)

    def open(self) -> None:
        """Navigate to the search page."""
        self.navigate_to("/search")

    def is_loaded(self) -> bool:
        """
        Check if the search page is loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        return self.is_visible(self.SEARCH_INPUT)

    def enter_search_query(self, query: str) -> None:
        """
        Enter search query.

        Args:
            query: Search query
        """
        self.fill(self.SEARCH_INPUT, query)

    def click_search(self) -> None:
        """Click the search button."""
        self.click(self.SEARCH_BUTTON)

    def search(self, query: str, semantic: bool = False) -> None:
        """
        Perform a search.

        Args:
            query: Search query
            semantic: Enable semantic search
        """
        self.enter_search_query(query)

        if semantic and self.is_visible(self.SEMANTIC_SEARCH_CHECKBOX):
            self.check(self.SEMANTIC_SEARCH_CHECKBOX)

        self.click_search()

    def enable_semantic_search(self) -> None:
        """Enable semantic search."""
        if self.is_visible(self.SEMANTIC_SEARCH_CHECKBOX):
            self.check(self.SEMANTIC_SEARCH_CHECKBOX)

    def disable_semantic_search(self) -> None:
        """Disable semantic search."""
        if self.is_visible(self.SEMANTIC_SEARCH_CHECKBOX):
            self.uncheck(self.SEMANTIC_SEARCH_CHECKBOX)

    def select_date_filter(self, date_filter: str) -> None:
        """
        Select date filter.

        Args:
            date_filter: Date filter option
        """
        if self.is_visible(self.DATE_FILTER):
            self.select_option(self.DATE_FILTER, date_filter)

    def select_type_filter(self, type_filter: str) -> None:
        """
        Select type filter.

        Args:
            type_filter: Type filter option
        """
        if self.is_visible(self.TYPE_FILTER):
            self.select_option(self.TYPE_FILTER, type_filter)

    def select_sort_option(self, sort_option: str) -> None:
        """
        Select sort option.

        Args:
            sort_option: Sort option
        """
        if self.is_visible(self.SORT_SELECT):
            self.select_option(self.SORT_SELECT, sort_option)

    def get_results_count(self) -> int:
        """
        Get number of search results.

        Returns:
            Number of results
        """
        if not self.is_visible(self.SEARCH_RESULTS):
            return 0

        results = self.page.query_selector_all(self.RESULT_ITEM)
        return len(results)

    def get_results(self) -> list[str]:
        """
        Get list of search results.

        Returns:
            List of result titles
        """
        if not self.is_visible(self.SEARCH_RESULTS):
            return []

        results = self.page.query_selector_all(self.RESULT_ITEM)
        return [r.text_content() or "" for r in results]

    def click_result(self, index: int = 0) -> None:
        """
        Click a search result.

        Args:
            index: Index of result to click (0-based)
        """
        results = self.page.query_selector_all(self.RESULT_ITEM)
        if index < len(results):
            results[index].click()

    def has_results(self) -> bool:
        """
        Check if there are search results.

        Returns:
            True if results are present
        """
        return self.is_visible(self.SEARCH_RESULTS) and self.get_results_count() > 0

    def has_no_results_message(self) -> bool:
        """
        Check if no results message is displayed.

        Returns:
            True if no results message is visible
        """
        return self.is_visible(self.NO_RESULTS_MESSAGE)

    def click_advanced_search(self) -> None:
        """Click advanced search link."""
        if self.is_visible(self.ADVANCED_SEARCH_LINK):
            self.click(self.ADVANCED_SEARCH_LINK)

    def wait_for_results(self, timeout: int = 10000) -> None:
        """
        Wait for search results to load.

        Args:
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_selector(
            f"{self.SEARCH_RESULTS}, {self.NO_RESULTS_MESSAGE}", timeout=timeout
        )
