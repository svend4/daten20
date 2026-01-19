"""
Page Object Models for E2E tests.

This package contains page object models for all pages in the application.
"""

from tests.e2e.pages.admin_page import AdminPage
from tests.e2e.pages.base_page import BasePage
from tests.e2e.pages.document_upload_page import DocumentUploadPage
from tests.e2e.pages.home_page import HomePage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.register_page import RegisterPage
from tests.e2e.pages.search_page import SearchPage

__all__ = [
    "BasePage",
    "HomePage",
    "LoginPage",
    "RegisterPage",
    "DocumentUploadPage",
    "SearchPage",
    "AdminPage",
]
