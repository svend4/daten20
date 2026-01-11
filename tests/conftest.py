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
