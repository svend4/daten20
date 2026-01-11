"""Pytest configuration and fixtures"""

import pytest
from decimal import Decimal

from src.models.service import Service, BasicInfo, Funding, SystemSettings
from src.models.financial import FinancialParameters


@pytest.fixture
def sample_service():
    """Create a sample service for testing"""
    service = Service()

    service.basic_info = BasicInfo(
        service_name="Test Service",
        target_group="Test Group",
        region="Berlin",
        provider_type="Qualified",
        document_date="01.01.2026",
        document_version="1.0",
        responsible_person="Test Person"
    )

    service.financial = FinancialParameters(
        brutto_rate=Decimal("25.00")
    )
    service.financial.materials_per_month = Decimal("50.00")
    service.financial.admin_percent = Decimal("5.0")
    service.financial.region_coefficient = Decimal("1.20")

    service.system_settings = SystemSettings(
        use_umlages=True,
        use_vacation_reserve=False,
        surcharge_base="full_cost",
        service_type="social"
    )

    service.funding = Funding(
        payer="Test Payer",
        documents=["Doc1", "Doc2"]
    )

    return service


@pytest.fixture
def sample_financial_params():
    """Create sample financial parameters"""
    params = FinancialParameters(brutto_rate=Decimal("25.00"))
    params.materials_per_month = Decimal("50.00")
    params.admin_percent = Decimal("5.0")
    params.region_coefficient = Decimal("1.20")
    params.use_umlages = True
    params.use_vacation_reserve = False

    return params


# ============================================================================
# General fixtures for document management applications
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Alias for tmp_path with cleanup."""
    return tmp_path


@pytest.fixture
def sample_text():
    """Return sample text for testing."""
    return """
    This is a sample document for testing.
    It contains multiple lines and sentences.
    Email: john.doe@example.com
    Phone: +49 123 456 789
    Date: 15.03.2025

    The document has sufficient content for quality analysis.
    """


@pytest.fixture
def sample_document_with_pii(tmp_path):
    """Create sample document with PII for testing."""
    doc_path = tmp_path / "pii_document.txt"
    content = """
    Personal Information Document
    ============================

    Name: John Doe
    Email: john.doe@example.com
    Phone: +49 123 456 789
    Address: Musterstraße 123, 12345 Berlin
    IBAN: DE89370400440532013000
    Date of Birth: 15.03.1990

    This document contains personal identifiable information.
    """
    doc_path.write_text(content)
    return doc_path


@pytest.fixture
def sample_quality_document(tmp_path):
    """Create sample document for quality testing."""
    doc_path = tmp_path / "quality_document.txt"
    content = """
    High Quality Document
    ====================

    This document demonstrates good quality with:
    - Clear structure and formatting
    - Proper punctuation and grammar
    - Reasonable sentence length
    - Valid contact information

    Contact: info@example.com
    Phone: +49 123 456 789
    Date: 15.03.2025

    The content is well-organized and easy to read.
    Each sentence is concise and focused.
    """
    doc_path.write_text(content)
    return doc_path


@pytest.fixture
def sample_comparison_docs(tmp_path):
    """Create two documents for comparison testing."""
    doc1_path = tmp_path / "doc1.txt"
    doc2_path = tmp_path / "doc2.txt"

    doc1_content = """
    Document Version 1
    =================

    This is the first version of the document.
    It contains some text for comparison.
    Email: original@example.com
    """

    doc2_content = """
    Document Version 2
    =================

    This is the second version of the document.
    It contains some modified text for comparison.
    Email: modified@example.com
    Date: 15.03.2025
    """

    doc1_path.write_text(doc1_content)
    doc2_path.write_text(doc2_content)

    return doc1_path, doc2_path


# ============================================================================
# pytest configuration hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'unit' marker to all tests in tests/unit/
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add 'integration' marker to all tests in tests/integration/
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
