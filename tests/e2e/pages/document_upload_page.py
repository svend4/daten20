"""
Document Upload Page Object Model for E2E tests.

This module provides the page object model for the document upload page.
"""

from tests.e2e.pages.base_page import BasePage


class DocumentUploadPage(BasePage):
    """Page object model for the document upload page."""

    # Selectors
    FILE_INPUT = "#file-input"
    UPLOAD_BUTTON = "#upload-btn"
    FILE_LIST = "#file-list"
    UPLOAD_PROGRESS = "#upload-progress"
    SUCCESS_MESSAGE = ".success-message"
    ERROR_MESSAGE = ".error-message"
    DOCUMENT_TYPE_SELECT = "#document-type"
    TAGS_INPUT = "#tags-input"
    DESCRIPTION_TEXTAREA = "#description"
    CANCEL_BUTTON = "#cancel-btn"
    UPLOAD_FORM = "#upload-form"
    DRAG_DROP_ZONE = "#drag-drop-zone"

    def __init__(self, page, base_url: str = "http://localhost:5000"):
        """
        Initialize the document upload page.

        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)

    def open(self) -> None:
        """Navigate to the upload page."""
        self.navigate_to("/upload")

    def is_loaded(self) -> bool:
        """
        Check if the upload page is loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        return self.is_visible(self.UPLOAD_FORM) or self.is_visible(self.DRAG_DROP_ZONE)

    def select_file(self, file_path: str) -> None:
        """
        Select a file to upload.

        Args:
            file_path: Path to file
        """
        self.upload_file(self.FILE_INPUT, file_path)

    def click_upload(self) -> None:
        """Click the upload button."""
        self.click(self.UPLOAD_BUTTON)

    def select_document_type(self, doc_type: str) -> None:
        """
        Select document type.

        Args:
            doc_type: Document type to select
        """
        if self.is_visible(self.DOCUMENT_TYPE_SELECT):
            self.select_option(self.DOCUMENT_TYPE_SELECT, doc_type)

    def enter_tags(self, tags: str) -> None:
        """
        Enter tags.

        Args:
            tags: Tags to enter (comma-separated)
        """
        if self.is_visible(self.TAGS_INPUT):
            self.fill(self.TAGS_INPUT, tags)

    def enter_description(self, description: str) -> None:
        """
        Enter description.

        Args:
            description: Description to enter
        """
        if self.is_visible(self.DESCRIPTION_TEXTAREA):
            self.fill(self.DESCRIPTION_TEXTAREA, description)

    def upload_document(
        self,
        file_path: str,
        doc_type: str = "",
        tags: str = "",
        description: str = "",
    ) -> None:
        """
        Upload a document with metadata.

        Args:
            file_path: Path to file
            doc_type: Document type
            tags: Tags (comma-separated)
            description: Description
        """
        self.select_file(file_path)

        if doc_type:
            self.select_document_type(doc_type)

        if tags:
            self.enter_tags(tags)

        if description:
            self.enter_description(description)

        self.click_upload()

    def cancel_upload(self) -> None:
        """Cancel the upload."""
        if self.is_visible(self.CANCEL_BUTTON):
            self.click(self.CANCEL_BUTTON)

    def is_upload_in_progress(self) -> bool:
        """
        Check if upload is in progress.

        Returns:
            True if upload is in progress
        """
        return self.is_visible(self.UPLOAD_PROGRESS)

    def wait_for_upload_complete(self, timeout: int = 30000) -> None:
        """
        Wait for upload to complete.

        Args:
            timeout: Timeout in milliseconds
        """
        # Wait for progress bar to disappear
        self.page.wait_for_selector(
            self.UPLOAD_PROGRESS, state="hidden", timeout=timeout
        )

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

    def get_uploaded_files(self) -> list[str]:
        """
        Get list of uploaded files.

        Returns:
            List of file names
        """
        if not self.is_visible(self.FILE_LIST):
            return []

        files = self.page.query_selector_all(f"{self.FILE_LIST} .file-item")
        return [f.text_content() or "" for f in files]
