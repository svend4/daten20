"""
Comprehensive tests for Data Models

Test coverage goals:
- BasicInfo: Field validation, defaults
- Funding: Payer information, documents list
- SystemSettings: Configuration options
- Service: Complete model, serialization/deserialization
- Financial models: CostBreakdown, FinancialParameters
- Template model: Template structure
- Model validation and constraints
- Serialization to dict/JSON
- Edge cases and error handling
"""

import pytest
import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from src.models.service import (
    BasicInfo,
    Funding,
    SystemSettings,
    # ServiceConfig,  # Does not exist - use SystemSettings directly
    Service,
)
from src.models.financial import (
    InsuranceRates,
    Umlages,
    FinancialParameters,
    CostBreakdown,
    ServiceCost,
    # HourlyRate,  # Does not exist yet - tests commented out
)
from src.models.template import (
    Variable,
    Block,
    TemplateStructure,
    # Template, TemplateVariable, TemplateBlock,  # Do not exist - tests commented out
)


class TestBasicInfo:
    """Test BasicInfo model"""

    def test_default_creation(self):
        """Test BasicInfo with defaults"""
        info = BasicInfo()

        assert info.service_name == ""
        assert info.target_group == ""
        assert info.region == ""
        assert info.document_version == "1.0"

    def test_creation_with_values(self):
        """Test BasicInfo with provided values"""
        info = BasicInfo(
            service_name="Shopping Assistance",
            target_group="Elderly",
            region="Bavaria",
            provider_type="Private",
            document_date="2024-01-15",
            document_version="2.0",
            responsible_person="John Doe"
        )

        assert info.service_name == "Shopping Assistance"
        assert info.target_group == "Elderly"
        assert info.region == "Bavaria"
        assert info.provider_type == "Private"
        assert info.document_date == "2024-01-15"
        assert info.document_version == "2.0"
        assert info.responsible_person == "John Doe"

    def test_partial_initialization(self):
        """Test BasicInfo with partial data"""
        info = BasicInfo(
            service_name="Test Service",
            region="Berlin"
        )

        assert info.service_name == "Test Service"
        assert info.region == "Berlin"
        assert info.target_group == ""  # Default value

    def test_modify_fields(self):
        """Test modifying BasicInfo fields"""
        info = BasicInfo()
        info.service_name = "Updated Service"
        info.region = "Hamburg"

        assert info.service_name == "Updated Service"
        assert info.region == "Hamburg"


class TestFunding:
    """Test Funding model"""

    def test_default_creation(self):
        """Test Funding with defaults"""
        funding = Funding()

        assert funding.payer == ""
        assert funding.documents == []

    def test_creation_with_payer(self):
        """Test Funding with payer"""
        funding = Funding(
            payer="Health Insurance",
            documents=["doc1.pdf", "doc2.pdf"]
        )

        assert funding.payer == "Health Insurance"
        assert len(funding.documents) == 2
        assert "doc1.pdf" in funding.documents

    def test_add_document(self):
        """Test adding documents to funding"""
        funding = Funding(payer="Insurance")
        funding.documents.append("new_doc.pdf")

        assert len(funding.documents) == 1
        assert funding.documents[0] == "new_doc.pdf"

    def test_empty_documents_list(self):
        """Test funding with no documents"""
        funding = Funding(payer="Self-Pay")

        assert funding.documents == []
        assert isinstance(funding.documents, list)


class TestSystemSettings:
    """Test SystemSettings model"""

    def test_default_settings(self):
        """Test default system settings"""
        settings = SystemSettings()

        assert settings.use_umlages is True
        assert settings.use_vacation_reserve is False
        assert settings.surcharge_base == "full_cost"
        assert settings.service_type == "social"

    def test_custom_settings(self):
        """Test custom system settings"""
        settings = SystemSettings(
            use_umlages=False,
            use_vacation_reserve=True,
            surcharge_base="brutto_only",
            service_type="medical"
        )

        assert settings.use_umlages is False
        assert settings.use_vacation_reserve is True
        assert settings.surcharge_base == "brutto_only"
        assert settings.service_type == "medical"

    # NOTE: ServiceConfig does not exist - use SystemSettings directly
    # def test_service_config_alias(self):
    #     """Test ServiceConfig alias"""
    #     # ServiceConfig is an alias for SystemSettings
    #     config = ServiceConfig()
    #
    #     assert config.use_umlages is True
    #     assert isinstance(config, SystemSettings)

    @pytest.mark.parametrize("service_type", [
        "domestic", "social", "medical", "professional", "educational"
    ])
    def test_service_types(self, service_type):
        """Test different service types"""
        settings = SystemSettings(service_type=service_type)

        assert settings.service_type == service_type


class TestInsuranceRates:
    """Test InsuranceRates model"""

    def test_default_rates(self):
        """Test default insurance rates"""
        rates = InsuranceRates()

        assert rates.kv_er == Decimal("0")
        assert rates.pv_er == Decimal("0")
        assert rates.rv_er == Decimal("0")
        assert rates.av_er == Decimal("0")
        assert rates.uv_er == Decimal("0")

    def test_custom_rates(self):
        """Test custom insurance rates"""
        rates = InsuranceRates(
            kv_er=Decimal("7.3"),
            pv_er=Decimal("1.525"),
            rv_er=Decimal("9.3"),
            av_er=Decimal("1.2"),
            uv_er=Decimal("1.6")
        )

        assert rates.kv_er == Decimal("7.3")
        assert rates.pv_er == Decimal("1.525")
        assert rates.rv_er == Decimal("9.3")

    def test_rates_precision(self):
        """Test decimal precision"""
        rates = InsuranceRates(kv_er=Decimal("7.30000"))

        # Decimal preserves precision
        assert rates.kv_er == Decimal("7.3")


class TestUmlages:
    """Test Umlages model"""

    def test_default_umlages(self):
        """Test default Umlages"""
        umlages = Umlages()

        assert umlages.u1 == Decimal("0")
        assert umlages.u2 == Decimal("0")
        assert umlages.u3 == Decimal("0")

    def test_custom_umlages(self):
        """Test custom Umlages"""
        umlages = Umlages(
            u1=Decimal("0.9"),
            u2=Decimal("0.39"),
            u3=Decimal("0.11")
        )

        assert umlages.u1 == Decimal("0.9")
        assert umlages.u2 == Decimal("0.39")
        assert umlages.u3 == Decimal("0.11")


class TestFinancialParameters:
    """Test FinancialParameters model"""

    def test_default_parameters(self):
        """Test default financial parameters"""
        params = FinancialParameters()

        assert params.brutto_rate == Decimal("0")
        assert params.materials_per_month == Decimal("0")
        assert params.admin_percent == Decimal("0")
        assert params.region_coefficient == Decimal("1.0")

    def test_complete_parameters(self):
        """Test complete financial parameters"""
        params = FinancialParameters(
            brutto_rate=Decimal("25.00"),
            insurance_rates=InsuranceRates(
                kv_er=Decimal("7.3"),
                pv_er=Decimal("1.525")
            ),
            umlages=Umlages(u1=Decimal("0.9")),
            materials_per_month=Decimal("50.00"),
            admin_percent=Decimal("5.5"),
            region_coefficient=Decimal("1.05")
        )

        assert params.brutto_rate == Decimal("25.00")
        assert params.materials_per_month == Decimal("50.00")
        assert params.admin_percent == Decimal("5.5")


class TestService:
    """Test complete Service model"""

    def test_default_service(self):
        """Test Service with defaults"""
        service = Service()

        assert service.id is None
        assert isinstance(service.basic_info, BasicInfo)
        assert isinstance(service.financial, FinancialParameters)
        assert isinstance(service.system_settings, SystemSettings)
        assert isinstance(service.funding, Funding)
        assert service.version == 1

    def test_complete_service(self):
        """Test Service with complete data"""
        service = Service(
            id=1,
            basic_info=BasicInfo(
                service_name="Shopping Assistance",
                region="Bavaria"
            ),
            financial=FinancialParameters(
                brutto_rate=Decimal("25.00")
            ),
            system_settings=SystemSettings(
                use_umlages=True
            ),
            funding=Funding(payer="Health Insurance"),
            created_at=datetime.now(),
            version=1
        )

        assert service.id == 1
        assert service.basic_info.service_name == "Shopping Assistance"
        assert service.financial.brutto_rate == Decimal("25.00")
        assert service.system_settings.use_umlages is True
        assert service.funding.payer == "Health Insurance"

    def test_service_to_dict(self):
        """Test converting Service to dictionary"""
        service = Service(
            id=1,
            basic_info=BasicInfo(service_name="Test Service", region="Berlin"),
            financial=FinancialParameters(brutto_rate=Decimal("20.00"))
        )

        service_dict = service.to_dict()

        assert isinstance(service_dict, dict)
        assert service_dict["id"] == 1
        assert service_dict["basic_info"]["service_name"] == "Test Service"
        assert float(service_dict["financial"]["brutto_rate"]) == 20.00

    def test_service_custom_fields(self):
        """Test Service custom fields"""
        service = Service()
        service.custom_fields["notes"] = "Important note"
        service.custom_fields["priority"] = "high"

        assert service.custom_fields["notes"] == "Important note"
        assert service.custom_fields["priority"] == "high"

    def test_service_metadata(self):
        """Test Service metadata fields"""
        now = datetime.now()
        service = Service(
            created_at=now,
            updated_at=now,
            version=2
        )

        assert service.created_at == now
        assert service.updated_at == now
        assert service.version == 2

    # NOTE: HourlyRate class does not exist yet
    # def test_service_cost_breakdown(self):
    #     """Test Service with cost breakdown"""
    #     cost_breakdown = CostBreakdown(
    #         netto=Decimal("20.00"),
    #         brutto=Decimal("25.00"),
    #         hourly_rate=HourlyRate(base_rate=Decimal("25.00"))
    #     )
    #
    #     service = Service(cost_breakdown=cost_breakdown)
    #
    #     assert service.cost_breakdown is not None
    #     assert service.cost_breakdown.netto == Decimal("20.00")


# NOTE: HourlyRate class does not exist yet - tests commented out
"""
class TestHourlyRate:
    # Test HourlyRate model

    def test_default_hourly_rate(self):
        # Test default hourly rate
        rate = HourlyRate()

        assert rate.base_rate == Decimal("0")

    def test_custom_hourly_rate(self):
        # Test custom hourly rate
        rate = HourlyRate(
            base_rate=Decimal("25.00"),
            with_overhead=Decimal("30.00")
        )

        assert rate.base_rate == Decimal("25.00")
        assert rate.with_overhead == Decimal("30.00")
"""


class TestCostBreakdown:
    """Test CostBreakdown model"""

    def test_default_cost_breakdown(self):
        """Test default cost breakdown"""
        breakdown = CostBreakdown()

        assert breakdown.netto == Decimal("0")
        assert breakdown.brutto == Decimal("0")

    def test_complete_cost_breakdown(self):
        """Test complete cost breakdown"""
        breakdown = CostBreakdown(
            netto=Decimal("20.00"),
            brutto=Decimal("25.00"),
            social_contributions=Decimal("3.00"),
            materials=Decimal("2.00"),
            admin_overhead=Decimal("1.00"),
            # hourly_rate=HourlyRate(base_rate=Decimal("25.00"))  # HourlyRate does not exist
        )

        assert breakdown.netto == Decimal("20.00")
        assert breakdown.brutto == Decimal("25.00")
        assert breakdown.social_contributions == Decimal("3.00")


# NOTE: Template, TemplateVariable classes do not exist yet - tests commented out
"""
class TestTemplate:
    # Test Template model

    def test_default_template(self):
        # Test default template
        template = Template()

        assert template.name == ""
        assert template.content == ""
        assert template.variables == []

    def test_template_with_content(self):
        # Test template with content
        template = Template(
            name="Service Template",
            content="Service: {{service_name}}",
            variables=[TemplateVariable(name="service_name", type="string")]
        )

        assert template.name == "Service Template"
        assert "{{service_name}}" in template.content
        assert len(template.variables) == 1


class TestTemplateVariable:
    # Test TemplateVariable model

    def test_template_variable(self):
        # Test template variable
        var = TemplateVariable(
            name="service_name",
            type="string",
            default_value="Default Service",
            required=True
        )

        assert var.name == "service_name"
        assert var.type == "string"
        assert var.default_value == "Default Service"
        assert var.required is True
"""


class TestSerialization:
    """Test model serialization"""

    def test_service_json_serialization(self):
        """Test serializing Service to JSON"""
        service = Service(
            id=1,
            basic_info=BasicInfo(service_name="Test", region="Berlin"),
            financial=FinancialParameters(brutto_rate=Decimal("25.00"))
        )

        service_dict = service.to_dict()
        json_str = json.dumps(service_dict)

        # Should be valid JSON
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["id"] == 1

    def test_service_from_dict(self):
        """Test creating Service from dictionary"""
        # TODO: Implement from_dict method if needed
        pass


class TestModelValidation:
    """Test model validation"""

    def test_negative_brutto_rate(self):
        """Test handling negative brutto rate"""
        # Models use Decimal, no built-in validation
        params = FinancialParameters(brutto_rate=Decimal("-10.00"))

        # Should allow negative (validation should be in business logic)
        assert params.brutto_rate == Decimal("-10.00")

    def test_empty_service_name(self):
        """Test service with empty name"""
        info = BasicInfo(service_name="")

        assert info.service_name == ""

    def test_invalid_region(self):
        """Test service with invalid region"""
        # No validation in model, accepts any string
        info = BasicInfo(region="InvalidRegion")

        assert info.region == "InvalidRegion"


class TestEdgeCases:
    """Test edge cases"""

    def test_very_large_decimal(self):
        """Test very large decimal values"""
        params = FinancialParameters(
            brutto_rate=Decimal("999999.99")
        )

        assert params.brutto_rate == Decimal("999999.99")

    def test_very_small_decimal(self):
        """Test very small decimal values"""
        params = FinancialParameters(
            brutto_rate=Decimal("0.01")
        )

        assert params.brutto_rate == Decimal("0.01")

    def test_unicode_in_service_name(self):
        """Test Unicode characters in service name"""
        info = BasicInfo(
            service_name="Übermäßige Pflege",
            region="München"
        )

        assert info.service_name == "Übermäßige Pflege"
        assert info.region == "München"

    def test_very_long_service_name(self):
        """Test very long service name"""
        long_name = "A" * 1000
        info = BasicInfo(service_name=long_name)

        assert len(info.service_name) == 1000

    def test_special_characters(self):
        """Test special characters in fields"""
        info = BasicInfo(
            service_name="Service & Co. <Special>",
            responsible_person="O'Brien"
        )

        assert "&" in info.service_name
        assert "'" in info.responsible_person


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
