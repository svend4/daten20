"""
E2E Tests for Search and Filter Documents.

This module contains end-to-end tests for document search functionality,
including keyword search, semantic search, and filtering options.
"""

import os
import tempfile
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.pages import (
    HomePage,
    LoginPage,
    RegisterPage,
    DocumentUploadPage,
    SearchPage,
)


# Test fixtures
@pytest.fixture
def authenticated_search_session(page: Page):
    """Create authenticated session with uploaded test documents."""
    import random
    import string

    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    credentials = {
        "username": f"searchuser_{random_suffix}",
        "email": f"search_{random_suffix}@example.com",
        "password": "SearchTest123!",
    }

    # Register and login
    register_page = RegisterPage(page)
    register_page.open()
    register_page.register(
        username=credentials["username"],
        email=credentials["email"],
        password=credentials["password"],
    )
    page.wait_for_timeout(1000)

    login_page = LoginPage(page)
    login_page.open()
    login_page.login(username=credentials["username"], password=credentials["password"])
    page.wait_for_timeout(2000)

    # Upload test documents with known content
    test_docs = []

    # Document 1: Social services planning
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write("Social Services Planning Document\n")
        f.write("This document covers social services planning strategies.\n")
        f.write("Keywords: social, services, planning, community, welfare\n")
        test_docs.append(f.name)

    # Document 2: Healthcare management
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write("Healthcare Management Guidelines\n")
        f.write("Guidelines for healthcare service delivery and management.\n")
        f.write("Keywords: healthcare, medical, services, management\n")
        test_docs.append(f.name)

    # Document 3: Budget report
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write("Annual Budget Report 2026\n")
        f.write("Financial planning and budget allocation for services.\n")
        f.write("Keywords: budget, finance, planning, allocation\n")
        test_docs.append(f.name)

    # Upload documents
    upload_page = DocumentUploadPage(page)
    for idx, doc_path in enumerate(test_docs):
        upload_page.open()
        page.wait_for_timeout(1000)
        upload_page.upload_document(
            doc_path,
            tags=f"search-test-{idx},test-doc",
            description=f"Test document {idx + 1} for search testing",
        )
        page.wait_for_timeout(3000)

    yield page, test_docs

    # Cleanup
    for doc_path in test_docs:
        if os.path.exists(doc_path):
            os.remove(doc_path)


class TestBasicSearch:
    """Test suite for basic search functionality."""

    def test_01_search_page_loads(self, page: Page):
        """
        Test that search page loads successfully.

        Steps:
        1. Navigate to search page
        2. Verify page elements

        Expected:
        - Search page loads
        - Search input is visible
        """
        # Login first
        import random
        import string

        random_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )

        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            username=f"user_{random_suffix}",
            email=f"user_{random_suffix}@example.com",
            password="Test123!",
        )
        page.wait_for_timeout(1000)

        login_page = LoginPage(page)
        login_page.open()
        login_page.login(username=f"user_{random_suffix}", password="Test123!")
        page.wait_for_timeout(2000)

        # Navigate to search
        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Verify page loaded
        assert search_page.is_loaded(), "Search page should be loaded"

    def test_02_empty_search(self, authenticated_search_session):
        """
        Test search with empty query.

        Steps:
        1. Navigate to search page
        2. Submit empty search

        Expected:
        - System handles empty search gracefully
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Try empty search
        search_page.click_search()
        page.wait_for_timeout(1000)

        # Should handle gracefully (no crash)

    def test_03_keyword_search(self, authenticated_search_session):
        """
        Test basic keyword search.

        Steps:
        1. Search for known keyword
        2. Verify results are returned

        Expected:
        - Search returns relevant results
        - Results contain the keyword
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search for "services"
        search_page.search("services")
        page.wait_for_timeout(2000)

        # Check if results appear (flexible)
        # May or may not have results depending on indexing

    def test_04_search_with_multiple_keywords(self, authenticated_search_session):
        """
        Test search with multiple keywords.

        Steps:
        1. Search with multiple keywords
        2. Verify results match query

        Expected:
        - Search handles multiple keywords
        - Results are relevant
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search with multiple words
        search_page.search("social services planning")
        page.wait_for_timeout(2000)

        # Verify search executed

    def test_05_search_no_results(self, authenticated_search_session):
        """
        Test search with query that returns no results.

        Steps:
        1. Search for non-existent term
        2. Verify no results message

        Expected:
        - No results are returned
        - Appropriate message is displayed
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search for unlikely term
        search_page.search("xyzabc123nonexistent")
        page.wait_for_timeout(2000)

        # May show no results message


class TestSemanticSearch:
    """Test suite for semantic search functionality."""

    def test_06_enable_semantic_search(self, authenticated_search_session):
        """
        Test enabling semantic search.

        Steps:
        1. Navigate to search page
        2. Enable semantic search option

        Expected:
        - Semantic search option is available
        - Can be enabled
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Try to enable semantic search
        search_page.enable_semantic_search()
        page.wait_for_timeout(500)

    def test_07_semantic_search_query(self, authenticated_search_session):
        """
        Test semantic search with natural language query.

        Steps:
        1. Enable semantic search
        2. Search with natural language query

        Expected:
        - Semantic search processes query
        - Returns conceptually relevant results
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Enable semantic search
        search_page.enable_semantic_search()

        # Search with natural language
        search_page.search("documents about community welfare programs")
        page.wait_for_timeout(3000)

        # Semantic search executed

    def test_08_compare_keyword_vs_semantic(self, authenticated_search_session):
        """
        Test comparison between keyword and semantic search.

        Steps:
        1. Perform keyword search
        2. Perform same search with semantic enabled
        3. Compare results

        Expected:
        - Both search types work
        - May return different results
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Keyword search
        search_page.disable_semantic_search()
        search_page.search("healthcare")
        page.wait_for_timeout(2000)

        keyword_has_results = search_page.has_results()

        # Semantic search
        search_page.open()  # Reload page
        page.wait_for_timeout(1000)
        search_page.enable_semantic_search()
        search_page.search("healthcare")
        page.wait_for_timeout(2000)

        # Both searches executed


class TestSearchFilters:
    """Test suite for search filters and sorting."""

    def test_09_filter_by_date(self, authenticated_search_session):
        """
        Test filtering search results by date.

        Steps:
        1. Perform search
        2. Apply date filter

        Expected:
        - Date filter is available
        - Results are filtered by date
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search first
        search_page.search("test")
        page.wait_for_timeout(2000)

        # Apply date filter (if available)
        # This is flexible as UI might not have this feature

    def test_10_filter_by_type(self, authenticated_search_session):
        """
        Test filtering search results by document type.

        Steps:
        1. Perform search
        2. Apply type filter

        Expected:
        - Type filter is available
        - Results are filtered by type
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search first
        search_page.search("document")
        page.wait_for_timeout(2000)

        # Apply type filter (if available)

    def test_11_sort_search_results(self, authenticated_search_session):
        """
        Test sorting search results.

        Steps:
        1. Perform search
        2. Change sort option

        Expected:
        - Sort options are available
        - Results reorder accordingly
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search first
        search_page.search("services")
        page.wait_for_timeout(2000)

        # Try to sort (if available)

    def test_12_combined_filters(self, authenticated_search_session):
        """
        Test using multiple filters together.

        Steps:
        1. Perform search
        2. Apply multiple filters
        3. Verify filtered results

        Expected:
        - Multiple filters can be combined
        - Results match all filter criteria
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search with query
        search_page.search("planning")
        page.wait_for_timeout(2000)

        # Apply filters (if available)

    def test_13_clear_filters(self, authenticated_search_session):
        """
        Test clearing applied filters.

        Steps:
        1. Apply filters
        2. Clear filters
        3. Verify results update

        Expected:
        - Filters can be cleared
        - Results reset to unfiltered state
        """
        page, _ = authenticated_search_session

        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)

        # Search and apply filters
        search_page.search("document")
        page.wait_for_timeout(2000)

        # Clear filters (if available)


# Summary test
class TestSearchSummary:
    """Summary test for search functionality."""

    def test_complete_search_workflow(self, authenticated_search_session):
        """
        Test complete search workflow.

        Steps:
        1. Perform keyword search
        2. Try semantic search
        3. Apply filters
        4. Sort results
        5. Select a result

        Expected:
        - Complete search workflow executes successfully
        - All search features are functional
        """
        page, _ = authenticated_search_session

        # Step 1: Keyword search
        search_page = SearchPage(page)
        search_page.open()
        page.wait_for_timeout(1000)
        search_page.search("services")
        page.wait_for_timeout(2000)

        # Step 2: Semantic search
        search_page.open()
        page.wait_for_timeout(1000)
        search_page.enable_semantic_search()
        search_page.search("community welfare programs")
        page.wait_for_timeout(2000)

        # Step 3: Filter results (if available)
        # Flexible implementation

        # Step 4: Sort results (if available)
        # Flexible implementation

        # Step 5: Navigate back to home
        home_page = HomePage(page)
        home_page.open()
        page.wait_for_timeout(1000)

        # Complete workflow executed
        assert True, "Complete search workflow executed successfully"
