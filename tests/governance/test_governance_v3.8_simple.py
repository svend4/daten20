"""
# SIMPLE VERSION - Tests for Governance API v3.8

Integration tests for Unified Governance API.
Marked as SIMPLE for future expansion.
"""

import pytest
from unittest.mock import Mock, patch
from src.governance.governance_api_simple import (
    GovernanceAPI,
    get_governance_api,
    GovernanceConfig,
    GovernanceOperation
)
from src.governance.compliance_frameworks import Framework
from src.governance.audit_management import AuditType


class TestGovernanceAPISimple:
    """Test suite for Governance API v3.8 (SIMPLE VERSION)"""

    def test_api_initialization(self):
        """Test API initializes correctly"""
        api = GovernanceAPI()
        assert api is not None
        assert api.config is not None
        assert api.records_manager is not None
        assert api.compliance_manager is not None

    def test_singleton_pattern(self):
        """Test singleton returns same instance"""
        api1 = get_governance_api()
        api2 = get_governance_api()
        assert api1 is api2

    def test_create_record(self):
        """Test record creation"""
        api = GovernanceAPI()
        with patch.object(api.records_manager, 'create_record', return_value='REC-001'):
            record_id = api.create_record('DOC-123', 'financial')
            assert record_id == 'REC-001'
            assert api.stats['records_created'] == 1

    def test_assess_compliance(self):
        """Test compliance assessment"""
        api = GovernanceAPI()
        mock_result = {'compliant': True, 'score': 95}
        with patch.object(api.compliance_manager, 'assess', return_value=mock_result):
            result = api.assess_compliance(Framework.ISO27001, 'organization')
            assert result['compliant'] is True
            assert result['score'] == 95

    def test_create_legal_hold(self):
        """Test legal hold creation"""
        api = GovernanceAPI()
        with patch.object(api.ediscovery_manager, 'create_hold', return_value='HOLD-001'):
            hold_id = api.create_legal_hold('Case-2024', ['user1', 'user2'])
            assert hold_id == 'HOLD-001'
            assert api.stats['holds_created'] == 1

    def test_apply_retention_policy(self):
        """Test retention policy application"""
        api = GovernanceAPI()
        with patch.object(api.retention_engine, 'apply_policy', return_value=True):
            result = api.apply_retention_policy('DOC-123', 'POL-7YEAR')
            assert result is True

    def test_create_audit(self):
        """Test audit creation"""
        api = GovernanceAPI()
        with patch.object(api.audit_manager, 'create_audit', return_value='AUDIT-001'):
            audit_id = api.create_audit(AuditType.INTERNAL, 'IT department')
            assert audit_id == 'AUDIT-001'

    def test_publish_policy(self):
        """Test policy publishing"""
        api = GovernanceAPI()
        with patch.object(api.policy_manager, 'publish', return_value=True):
            result = api.publish_policy('POL-001', ['user1@example.com'])
            assert result is True

    def test_statistics_tracking(self):
        """Test operation statistics tracking"""
        api = GovernanceAPI()
        initial_ops = api.stats['total_operations']
        
        with patch.object(api.records_manager, 'create_record', return_value='REC-001'):
            api.create_record('DOC-123', 'financial')
        
        assert api.stats['total_operations'] == initial_ops + 1
        assert api.stats['by_operation'][GovernanceOperation.CREATE_RECORD.value] == 1

    def test_get_statistics(self):
        """Test statistics retrieval"""
        api = GovernanceAPI()
        stats = api.get_statistics()
        assert 'total_operations' in stats
        assert 'by_operation' in stats
        assert 'records_created' in stats

    def test_custom_config(self):
        """Test custom configuration"""
        config = GovernanceConfig(
            default_framework=Framework.GDPR,
            enable_auto_compliance=False,
            audit_logging=True
        )
        api = GovernanceAPI(config=config)
        assert api.config.default_framework == Framework.GDPR
        assert api.config.enable_auto_compliance is False


# Integration workflow tests
class TestGovernanceWorkflows:
    """Test complete governance workflows"""

    def test_full_compliance_workflow(self):
        """Test complete compliance workflow"""
        api = GovernanceAPI()
        
        # Create record
        with patch.object(api.records_manager, 'create_record', return_value='REC-001'):
            record_id = api.create_record('DOC-123', 'financial')
            assert record_id == 'REC-001'
        
        # Apply retention
        with patch.object(api.retention_engine, 'apply_policy', return_value=True):
            retention_applied = api.apply_retention_policy('DOC-123', 'POL-7YEAR')
            assert retention_applied is True
        
        # Assess compliance
        with patch.object(api.compliance_manager, 'assess', return_value={'compliant': True}):
            compliance = api.assess_compliance(Framework.ISO27001, 'document')
            assert compliance['compliant'] is True

    def test_ediscovery_workflow(self):
        """Test e-discovery workflow"""
        api = GovernanceAPI()
        
        # Create legal hold
        with patch.object(api.ediscovery_manager, 'create_hold', return_value='HOLD-001'):
            hold_id = api.create_legal_hold('Litigation-2024', ['custodian1'])
            assert hold_id == 'HOLD-001'
        
        # Create audit
        with patch.object(api.audit_manager, 'create_audit', return_value='AUDIT-001'):
            audit_id = api.create_audit(AuditType.LEGAL_HOLD, 'legal hold')
            assert audit_id == 'AUDIT-001'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
