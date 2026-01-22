"""
# SIMPLE VERSION - Unified Governance API - v3.8

This is a simplified/minimal API that can be expanded later with:
- More detailed compliance operations
- Advanced audit workflows
- Extended policy management features
- Additional reporting capabilities

Single interface for all governance and compliance operations.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

from .records_management import get_records_manager
from .compliance_frameworks import get_compliance_manager, Framework
from .ediscovery import get_ediscovery_manager
from .data_retention import get_retention_engine
from .audit_management import get_audit_manager, AuditType
from .policy_management import get_policy_manager

logger = logging.getLogger(__name__)


class GovernanceOperation(Enum):
    """Governance operation types"""
    CREATE_RECORD = "create_record"
    ASSESS_COMPLIANCE = "assess_compliance"
    CREATE_LEGAL_HOLD = "create_legal_hold"
    APPLY_RETENTION = "apply_retention"
    CREATE_AUDIT = "create_audit"
    PUBLISH_POLICY = "publish_policy"


@dataclass
class GovernanceConfig:
    """Configuration for Governance API"""
    default_framework: Framework = Framework.ISO27001
    enable_auto_compliance: bool = True
    enable_retention: bool = True
    audit_logging: bool = True


class GovernanceAPI:
    """
    # SIMPLE VERSION
    Unified Governance API - Single interface for governance operations

    Can be expanded with:
    - Advanced compliance reporting
    - Risk assessment workflows
    - Automated remediation
    - Integration with GRC tools
    """

    def __init__(self, config: Optional[GovernanceConfig] = None):
        """Initialize Governance API"""
        self.config = config or GovernanceConfig()

        # Initialize services
        self.records_manager = get_records_manager()
        self.compliance_manager = get_compliance_manager()
        self.ediscovery_manager = get_ediscovery_manager()
        self.retention_engine = get_retention_engine()
        self.audit_manager = get_audit_manager()
        self.policy_manager = get_policy_manager()

        # Statistics
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in GovernanceOperation},
            "records_created": 0,
            "holds_created": 0,
            "audits_completed": 0,
        }

        logger.info("Governance API initialized (SIMPLE VERSION)")

    def create_record(self, document_id: str, record_class: str, **kwargs) -> str:
        """Create governed record"""
        self._track(GovernanceOperation.CREATE_RECORD)
        record_id = self.records_manager.create_record(document_id, record_class, **kwargs)
        self.stats["records_created"] += 1
        return record_id

    def assess_compliance(self, framework: Framework, scope: str, **kwargs) -> Dict[str, Any]:
        """Assess compliance against framework"""
        self._track(GovernanceOperation.ASSESS_COMPLIANCE)
        return self.compliance_manager.assess(framework, scope, **kwargs)

    def create_legal_hold(self, case_name: str, custodians: List[str], **kwargs) -> str:
        """Create legal hold"""
        self._track(GovernanceOperation.CREATE_LEGAL_HOLD)
        hold_id = self.ediscovery_manager.create_hold(case_name, custodians, **kwargs)
        self.stats["holds_created"] += 1
        return hold_id

    def apply_retention_policy(self, document_id: str, policy_id: str, **kwargs) -> bool:
        """Apply retention policy"""
        self._track(GovernanceOperation.APPLY_RETENTION)
        return self.retention_engine.apply_policy(document_id, policy_id, **kwargs)

    def create_audit(self, audit_type: AuditType, scope: str, **kwargs) -> str:
        """Create audit plan"""
        self._track(GovernanceOperation.CREATE_AUDIT)
        return self.audit_manager.create_audit(audit_type, scope, **kwargs)

    def publish_policy(self, policy_id: str, recipients: List[str], **kwargs) -> bool:
        """Publish policy to recipients"""
        self._track(GovernanceOperation.PUBLISH_POLICY)
        return self.policy_manager.publish(policy_id, recipients, **kwargs)

    def _track(self, operation: GovernanceOperation):
        """Track operation statistics"""
        self.stats["total_operations"] += 1
        self.stats["by_operation"][operation.value] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self.stats


# Singleton
_governance_api = None


def get_governance_api(config: Optional[GovernanceConfig] = None) -> GovernanceAPI:
    """Get singleton Governance API instance"""
    global _governance_api
    if _governance_api is None:
        _governance_api = GovernanceAPI(config=config)
    return _governance_api
