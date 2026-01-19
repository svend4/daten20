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

__version__ = "3.8.0"

# Audit Management
from .audit_management import (
    AuditEvidence,
    AuditFinding,
    AuditManager,
    AuditPlan,
    AuditReport,
    AuditStatus,
    AuditType,
    FindingStatus,
    Remediation,
    Severity,
    get_audit_manager,
)

# Compliance Frameworks
from .compliance_frameworks import (
    ComplianceManager,
    ComplianceScore,
    Control,
    ControlAssessment,
    ControlStatus,
)
from .compliance_frameworks import Evidence as ComplianceEvidence
from .compliance_frameworks import (
    Framework,
    RiskLevel,
    get_compliance_manager,
)

# Data Retention
from .data_retention import (
    AppliedRetention,
    DispositionAction,
    DispositionQueueItem,
    HoldType,
    RetentionEngine,
    RetentionException,
    RetentionHold,
    RetentionPolicy,
    TriggerEvent,
    get_retention_engine,
)

# eDiscovery
from .ediscovery import (
    ChainOfCustodyEntry,
    CollectedDocument,
    Collection,
    Custodian,
    ExportFormat,
    ExportPackage,
    HoldStatus,
    LegalHold,
    SearchQuery,
    eDiscoveryManager,
    get_ediscovery_manager,
)

# Policy Management
from .policy_management import (
    Acknowledgment,
    AcknowledgmentStatus,
    Attestation,
    Distribution,
    Policy,
    PolicyCategory,
    PolicyManager,
    PolicyStatus,
    PolicyVersion,
    get_policy_manager,
)

# Records Management
from .records_management import (
    DispositionItem,
)
from .records_management import LegalHold as RecordLegalHold
from .records_management import (
    LifecycleState,
    Record,
    RecordClass,
    RecordsManager,
    RetentionSchedule,
)
from .records_management import TriggerEvent as RecordTriggerEvent
from .records_management import (
    VitalRecord,
    get_records_manager,
)

__all__ = [
    # Records Management
    "RecordsManager",
    "RecordClass",
    "LifecycleState",
    "RecordTriggerEvent",
    "RetentionSchedule",
    "Record",
    "RecordLegalHold",
    "DispositionItem",
    "VitalRecord",
    "get_records_manager",
    # Compliance Frameworks
    "ComplianceManager",
    "Framework",
    "ControlStatus",
    "RiskLevel",
    "Control",
    "ComplianceEvidence",
    "ControlAssessment",
    "ComplianceScore",
    "get_compliance_manager",
    # eDiscovery
    "eDiscoveryManager",
    "HoldStatus",
    "ExportFormat",
    "Custodian",
    "LegalHold",
    "SearchQuery",
    "CollectedDocument",
    "Collection",
    "ExportPackage",
    "ChainOfCustodyEntry",
    "get_ediscovery_manager",
    # Data Retention
    "RetentionEngine",
    "TriggerEvent",
    "DispositionAction",
    "HoldType",
    "RetentionPolicy",
    "AppliedRetention",
    "RetentionHold",
    "DispositionQueueItem",
    "RetentionException",
    "get_retention_engine",
    # Audit Management
    "AuditManager",
    "AuditType",
    "Severity",
    "FindingStatus",
    "AuditStatus",
    "AuditPlan",
    "AuditEvidence",
    "Remediation",
    "AuditFinding",
    "AuditReport",
    "get_audit_manager",
    # Policy Management
    "PolicyManager",
    "PolicyStatus",
    "PolicyCategory",
    "AcknowledgmentStatus",
    "PolicyVersion",
    "Policy",
    "Acknowledgment",
    "Attestation",
    "Distribution",
    "get_policy_manager",
]
