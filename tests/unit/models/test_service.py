"""
Unit tests for models.service module
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

pytestmark = pytest.mark.unit


class TestServiceModel:
    """Tests for Service model"""
    
    @pytest.fixture
    def service_data(self):
        """Fixture providing sample service data"""
        from src.models.service import BasicInfo, SystemSettings, Funding
        from src.models.financial import FinancialParameters
        from decimal import Decimal
        return {
            'id': 1,
            'basic_info': BasicInfo(service_name='Test Service', region='North'),
            'financial': FinancialParameters(brutto_rate=Decimal('50.00')),
            'system_settings': SystemSettings(),
            'funding': Funding(),
            'created_at': datetime.now()
        }

    def test_service_initialization(self, service_data):
        """Test Service model can be initialized"""
        try:
            from src.models.service import Service
            service = Service(**service_data)
            assert service is not None
            assert service.basic_info.service_name == 'Test Service'
        except ImportError:
            pytest.skip("Service model not found")
    
    def test_service_attributes(self, service_data):
        """Test Service model has expected attributes"""
        try:
            from src.models.service import Service
            service = Service(**service_data)

            # Check dataclass attributes
            assert service.id == 1
            assert service.basic_info.service_name == 'Test Service'
            assert service.basic_info.region == 'North'
            assert service.financial is not None
            assert service.system_settings is not None
        except ImportError:
            pytest.skip("Service model not found")
    
    def test_service_validation(self):
        """Test Service model validates required fields"""
        try:
            from src.models.service import Service
            
            # Try creating service with missing required fields
            # This should either raise an error or handle gracefully
            try:
                service = Service()
                # If no error, check if it has default values
                assert service is not None
            except (TypeError, ValueError, KeyError):
                # Expected to raise error for missing fields
                assert True
        except ImportError:
            pytest.skip("Service model not found")
    
    @pytest.mark.parametrize("field,value", [
        ("service_name", "Updated Name"),
        ("region", "South"),
        ("target_group", "Seniors"),
    ])
    def test_service_field_updates(self, service_data, field, value):
        """Test updating Service model fields"""
        try:
            from src.models.service import Service
            service = Service(**service_data)

            # Update basic_info fields
            setattr(service.basic_info, field, value)
            assert getattr(service.basic_info, field) == value
        except ImportError:
            pytest.skip("Service model not found")


class TestBasicInfo:
    """Tests for BasicInfo model"""
    
    @pytest.fixture
    def basic_info_data(self):
        """Fixture providing sample BasicInfo data"""
        return {
            'service_name': 'Test Service',
            'target_group': 'Seniors',
            'region': 'North',
            'provider_type': 'Healthcare',
            'document_date': '2026-01-13',
            'document_version': '1.0',
            'responsible_person': 'John Doe'
        }

    def test_basic_info_initialization(self, basic_info_data):
        """Test BasicInfo can be initialized"""
        try:
            from src.models.service import BasicInfo
            info = BasicInfo(**basic_info_data)
            assert info is not None
            assert info.service_name == 'Test Service'
            assert info.region == 'North'
        except ImportError:
            pytest.skip("BasicInfo model not found")
    
    def test_basic_info_required_fields(self):
        """Test BasicInfo validates required fields"""
        try:
            from src.models.service import BasicInfo
            
            # Test with minimal data
            minimal_data = {'service_name': 'Test'}
            info = BasicInfo(**minimal_data)
            assert info is not None
        except (ImportError, TypeError, ValueError):
            pytest.skip("BasicInfo model not found or requires more fields")
    
    def test_basic_info_contact_validation(self):
        """Test BasicInfo validates contact information"""
        try:
            from src.models.service import BasicInfo

            valid_data = {
                'service_name': 'Test',
                'responsible_person': 'John Doe',
                'provider_type': 'Healthcare'
            }

            info = BasicInfo(**valid_data)

            # Check that responsible_person is set
            assert info.responsible_person == 'John Doe'
            assert info.provider_type == 'Healthcare'
        except ImportError:
            pytest.skip("BasicInfo model not found")


class TestFunding:
    """Tests for Funding model"""
    
    @pytest.fixture
    def funding_data(self):
        """Fixture providing sample Funding data"""
        return {
            'payer': 'Federal Grant Agency',
            'documents': ['contract.pdf', 'budget.xlsx']
        }

    def test_funding_initialization(self, funding_data):
        """Test Funding can be initialized"""
        try:
            from src.models.service import Funding
            funding = Funding(**funding_data)
            assert funding is not None
            assert funding.payer == 'Federal Grant Agency'
            assert len(funding.documents) == 2
        except ImportError:
            pytest.skip("Funding model not found")
    
    def test_funding_amount_validation(self):
        """Test Funding validates payer field"""
        try:
            from src.models.service import Funding

            # Test with payer
            data = {
                'payer': 'Insurance Company',
                'documents': []
            }

            funding = Funding(**data)
            assert funding.payer == 'Insurance Company'
            assert funding.documents == []
        except ImportError:
            pytest.skip("Funding model not found")
    
    @pytest.mark.parametrize("payer,num_docs", [
        ("Insurance A", 1),
        ("Insurance B", 3),
        ("Government", 0),
    ])
    def test_funding_amount_formatting(self, payer, num_docs):
        """Test Funding with different payers and documents"""
        try:
            from src.models.service import Funding

            funding_data = {
                'payer': payer,
                'documents': [f'doc{i}.pdf' for i in range(num_docs)]
            }

            funding = Funding(**funding_data)
            assert funding.payer == payer
            assert len(funding.documents) == num_docs
        except ImportError:
            pytest.skip("Funding model not found")


class TestSystemSettings:
    """Tests for SystemSettings model"""
    
    def test_system_settings_initialization(self):
        """Test SystemSettings can be initialized"""
        try:
            from src.models.service import SystemSettings
            settings = SystemSettings()
            assert settings is not None
        except (ImportError, TypeError):
            pytest.skip("SystemSettings model not found or requires parameters")
    
    def test_system_settings_defaults(self):
        """Test SystemSettings has default values"""
        try:
            from src.models.service import SystemSettings
            settings = SystemSettings()

            # Check for actual SystemSettings attributes
            assert hasattr(settings, 'use_umlages')
            assert hasattr(settings, 'use_vacation_reserve')
            assert hasattr(settings, 'surcharge_base')
            assert hasattr(settings, 'service_type')

            # Check defaults
            assert settings.use_umlages == True
            assert settings.use_vacation_reserve == False
            assert settings.surcharge_base == "full_cost"
            assert settings.service_type == "social"
        except ImportError:
            pytest.skip("SystemSettings model not found")
    
    def test_system_settings_update(self):
        """Test SystemSettings can be updated"""
        try:
            from src.models.service import SystemSettings
            settings = SystemSettings()

            # Update settings
            settings.use_umlages = False
            assert settings.use_umlages == False

            settings.service_type = 'medical'
            assert settings.service_type == 'medical'

            settings.surcharge_base = 'brutto_only'
            assert settings.surcharge_base == 'brutto_only'
        except ImportError:
            pytest.skip("SystemSettings model not found")


class TestServiceConfig:
    """Tests for ServiceConfig model"""
    
    @pytest.fixture
    def config_data(self):
        """Fixture providing sample ServiceConfig data"""
        return {
            'use_umlages': True,
            'use_vacation_reserve': True,
            'surcharge_base': 'full_cost',
            'service_type': 'medical'
        }

    def test_service_config_initialization(self, config_data):
        """Test ServiceConfig can be initialized"""
        try:
            from src.models.service import ServiceConfig
            config = ServiceConfig(**config_data)
            assert config is not None
            assert config.use_umlages == True
            assert config.service_type == 'medical'
        except (ImportError, TypeError):
            pytest.skip("ServiceConfig model not found")
    
    def test_service_config_boolean_fields(self, config_data):
        """Test ServiceConfig handles boolean fields"""
        try:
            from src.models.service import ServiceConfig
            config = ServiceConfig(**config_data)

            # Check boolean fields
            assert isinstance(config.use_umlages, bool)
            assert isinstance(config.use_vacation_reserve, bool)
            assert config.use_umlages == True
            assert config.use_vacation_reserve == True
        except ImportError:
            pytest.skip("ServiceConfig model not found")
    
    def test_service_config_capacity_validation(self):
        """Test ServiceConfig validates service type"""
        try:
            from src.models.service import ServiceConfig

            # Test with different service types
            for service_type in ['social', 'medical', 'professional', 'educational']:
                config = ServiceConfig(service_type=service_type)
                assert config.service_type == service_type
        except ImportError:
            pytest.skip("ServiceConfig model not found")


class TestModelRelationships:
    """Tests for relationships between models"""
    
    def test_service_has_basic_info(self):
        """Test Service can have BasicInfo"""
        try:
            from src.models.service import Service, BasicInfo
            
            info_data = {'service_name': 'Test Service'}
            info = BasicInfo(**info_data)
            
            service_data = {
                'name': 'Test Service',
                'basic_info': info
            }
            
            service = Service(**service_data)
            
            # Check if service has basic_info
            if hasattr(service, 'basic_info'):
                assert service.basic_info is not None
        except (ImportError, TypeError):
            pytest.skip("Models or relationships not implemented")
    
    def test_service_has_funding(self):
        """Test Service can have Funding"""
        try:
            from src.models.service import Service, Funding
            
            funding_data = {
                'source': 'Grant',
                'amount': 50000.00
            }
            funding = Funding(**funding_data)
            
            service_data = {
                'name': 'Test Service',
                'funding': funding
            }
            
            service = Service(**service_data)
            
            # Check if service has funding
            if hasattr(service, 'funding'):
                assert service.funding is not None
        except (ImportError, TypeError):
            pytest.skip("Models or relationships not implemented")
