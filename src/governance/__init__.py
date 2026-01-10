"""
Governance & Compliance Module - v3.8

Enterprise governance, compliance frameworks, and records management.

Modules:
- governance_services: Unified governance and compliance services

Components:
- Records Management: Document lifecycle and retention
- Compliance Frameworks: ISO 27001, NIST CSF, PCI DSS, GDPR, HIPAA, SOC 2
- eDiscovery: Legal hold and search
- Data Retention: Automated retention and disposition
- Audit Management: Audit planning and findings
- Policy Management: Policy lifecycle and acknowledgment

Version: 3.8.0
"""

__version__ = '3.8.0'

from .governance_services import (
    # Records Management
    RecordClass,
    RecordLifecycleState,
    Record,
    RecordsManager,
    get_records_manager,
    # Compliance Frameworks
    ComplianceFramework,
    ControlStatus,
    Control,
    ComplianceManager,
    get_compliance_manager,
    # eDiscovery
    LegalHold,
    eDiscoveryManager,
    get_ediscovery_manager,
    # Data Retention
    RetentionPolicy,
    RetentionEngine,
    get_retention_engine,
    # Audit Management
    AuditSeverity,
    AuditFinding,
    AuditManager,
    get_audit_manager,
    # Policy Management
    Policy,
    PolicyManager,
    get_policy_manager,
)

__all__ = [
    # Records Management
    'RecordClass',
    'RecordLifecycleState',
    'Record',
    'RecordsManager',
    'get_records_manager',
    # Compliance Frameworks
    'ComplianceFramework',
    'ControlStatus',
    'Control',
    'ComplianceManager',
    'get_compliance_manager',
    # eDiscovery
    'LegalHold',
    'eDiscoveryManager',
    'get_ediscovery_manager',
    # Data Retention
    'RetentionPolicy',
    'RetentionEngine',
    'get_retention_engine',
    # Audit Management
    'AuditSeverity',
    'AuditFinding',
    'AuditManager',
    'get_audit_manager',
    # Policy Management
    'Policy',
    'PolicyManager',
    'get_policy_manager',
]
