"""
Governance & Compliance Module - v3.8

Enterprise governance and compliance capabilities including records management,
compliance frameworks (ISO 27001, NIST CSF, PCI DSS, GDPR, HIPAA, SOC 2),
eDiscovery, data retention, audit management, and policy management.

Modules:
- records_management: Document lifecycle and retention management
- compliance_frameworks: ISO 27001, NIST CSF, PCI DSS, GDPR, HIPAA, SOC 2
- ediscovery: Legal hold, search, collection, and export
- data_retention: Automated retention policies and disposition
- audit_management: Audit planning, findings, and remediation
- policy_management: Policy lifecycle and acknowledgment tracking

Version: 3.8.0
"""

__version__ = '3.8.0'

# Records Management
from .records_management import (
    RecordsManager,
    RecordClass,
    LifecycleState,
    TriggerEvent as RecordTriggerEvent,
    RetentionSchedule,
    Record,
    LegalHold as RecordLegalHold,
    DispositionItem,
    VitalRecord,
    get_records_manager,
)

# Compliance Frameworks
from .compliance_frameworks import (
    ComplianceManager,
    Framework,
    ControlStatus,
    RiskLevel,
    Control,
    Evidence as ComplianceEvidence,
    ControlAssessment,
    ComplianceScore,
    get_compliance_manager,
)

# eDiscovery
from .ediscovery import (
    eDiscoveryManager,
    HoldStatus,
    ExportFormat,
    Custodian,
    LegalHold,
    SearchQuery,
    CollectedDocument,
    Collection,
    ExportPackage,
    ChainOfCustodyEntry,
    get_ediscovery_manager,
)

# Data Retention
from .data_retention import (
    RetentionEngine,
    TriggerEvent,
    DispositionAction,
    HoldType,
    RetentionPolicy,
    AppliedRetention,
    RetentionHold,
    DispositionQueueItem,
    RetentionException,
    get_retention_engine,
)

# Audit Management
from .audit_management import (
    AuditManager,
    AuditType,
    Severity,
    FindingStatus,
    AuditStatus,
    AuditPlan,
    AuditEvidence,
    Remediation,
    AuditFinding,
    AuditReport,
    get_audit_manager,
)

# Policy Management
from .policy_management import (
    PolicyManager,
    PolicyStatus,
    PolicyCategory,
    AcknowledgmentStatus,
    PolicyVersion,
    Policy,
    Acknowledgment,
    Attestation,
    Distribution,
    get_policy_manager,
)

__all__ = [
    # Records Management
    'RecordsManager',
    'RecordClass',
    'LifecycleState',
    'RecordTriggerEvent',
    'RetentionSchedule',
    'Record',
    'RecordLegalHold',
    'DispositionItem',
    'VitalRecord',
    'get_records_manager',

    # Compliance Frameworks
    'ComplianceManager',
    'Framework',
    'ControlStatus',
    'RiskLevel',
    'Control',
    'ComplianceEvidence',
    'ControlAssessment',
    'ComplianceScore',
    'get_compliance_manager',

    # eDiscovery
    'eDiscoveryManager',
    'HoldStatus',
    'ExportFormat',
    'Custodian',
    'LegalHold',
    'SearchQuery',
    'CollectedDocument',
    'Collection',
    'ExportPackage',
    'ChainOfCustodyEntry',
    'get_ediscovery_manager',

    # Data Retention
    'RetentionEngine',
    'TriggerEvent',
    'DispositionAction',
    'HoldType',
    'RetentionPolicy',
    'AppliedRetention',
    'RetentionHold',
    'DispositionQueueItem',
    'RetentionException',
    'get_retention_engine',

    # Audit Management
    'AuditManager',
    'AuditType',
    'Severity',
    'FindingStatus',
    'AuditStatus',
    'AuditPlan',
    'AuditEvidence',
    'Remediation',
    'AuditFinding',
    'AuditReport',
    'get_audit_manager',

    # Policy Management
    'PolicyManager',
    'PolicyStatus',
    'PolicyCategory',
    'AcknowledgmentStatus',
    'PolicyVersion',
    'Policy',
    'Acknowledgment',
    'Attestation',
    'Distribution',
    'get_policy_manager',
]
