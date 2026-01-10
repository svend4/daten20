"""
Governance & Compliance Services - v3.8

Enterprise governance, compliance management, and records lifecycle.
"""

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


# ============================================================================
# Records Management
# ============================================================================


class RecordClass(Enum):
    """Standard record classifications"""
    FINANCIAL = "financial_records"
    LEGAL = "legal_records"
    HR = "hr_records"
    CONTRACTS = "contracts"
    CORRESPONDENCE = "correspondence"
    TECHNICAL = "technical_documentation"
    MARKETING = "marketing_materials"


class RecordLifecycleState(Enum):
    """Record lifecycle states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DISPOSED = "disposed"
    LEGAL_HOLD = "legal_hold"


@dataclass
class Record:
    """Document record"""
    record_id: str
    document_id: str
    record_class: RecordClass
    title: str
    lifecycle_state: RecordLifecycleState = RecordLifecycleState.ACTIVE
    retention_years: int = 7
    retention_start: Optional[datetime] = None
    disposition_date: Optional[datetime] = None
    legal_holds: List[str] = field(default_factory=list)
    is_vital: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def can_dispose(self) -> bool:
        """Check if record can be disposed"""
        if self.legal_holds:
            return False
        if self.is_vital:
            return False
        if not self.disposition_date:
            return False
        return datetime.now() >= self.disposition_date


class RecordsManager:
    """
    Records Management System

    Manages document lifecycle, retention, and disposition.
    """

    def __init__(self):
        self._records: Dict[str, Record] = {}
        self._legal_holds: Dict[str, Set[str]] = defaultdict(set)
        self._lock = Lock()
        self._stats = {
            'total_records': 0,
            'disposed_records': 0,
            'vital_records': 0
        }

    def declare_record(
        self,
        document_id: str,
        record_class: RecordClass,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Record:
        """Declare document as record"""
        record_id = str(uuid4())

        record = Record(
            record_id=record_id,
            document_id=document_id,
            record_class=record_class,
            title=title,
            metadata=metadata or {}
        )

        with self._lock:
            self._records[record_id] = record
            self._stats['total_records'] += 1

        return record

    def apply_retention(
        self,
        record_id: str,
        retention_years: int,
        trigger_event: str = "creation"
    ) -> Optional[Record]:
        """Apply retention schedule to record"""
        record = self._records.get(record_id)
        if not record:
            return None

        with self._lock:
            record.retention_years = retention_years
            record.retention_start = datetime.now()
            record.disposition_date = (
                record.retention_start + timedelta(days=365 * retention_years)
            )

        return record

    def place_legal_hold(
        self,
        record_id: str,
        case_id: str,
        reason: str
    ) -> bool:
        """Place legal hold on record"""
        record = self._records.get(record_id)
        if not record:
            return False

        with self._lock:
            if case_id not in record.legal_holds:
                record.legal_holds.append(case_id)
                self._legal_holds[case_id].add(record_id)
                record.lifecycle_state = RecordLifecycleState.LEGAL_HOLD

        return True

    def release_legal_hold(
        self,
        record_id: str,
        case_id: str
    ) -> bool:
        """Release legal hold on record"""
        record = self._records.get(record_id)
        if not record:
            return False

        with self._lock:
            if case_id in record.legal_holds:
                record.legal_holds.remove(case_id)
                self._legal_holds[case_id].discard(record_id)

                # Restore previous state if no more holds
                if not record.legal_holds:
                    record.lifecycle_state = RecordLifecycleState.ACTIVE

        return True

    def mark_vital(self, record_id: str) -> bool:
        """Mark record as vital"""
        record = self._records.get(record_id)
        if not record:
            return False

        with self._lock:
            record.is_vital = True
            self._stats['vital_records'] += 1

        return True

    def dispose_record(self, record_id: str) -> bool:
        """Dispose of record (if eligible)"""
        record = self._records.get(record_id)
        if not record:
            return False

        if not record.can_dispose():
            return False

        with self._lock:
            record.lifecycle_state = RecordLifecycleState.DISPOSED
            self._stats['disposed_records'] += 1

        return True

    def get_disposition_queue(self, days_ahead: int = 30) -> List[Record]:
        """Get records eligible for disposition"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        eligible = []
        for record in self._records.values():
            if (record.disposition_date and
                record.disposition_date <= cutoff_date and
                record.can_dispose()):
                eligible.append(record)

        return eligible

    def get_statistics(self) -> Dict[str, Any]:
        """Get records management statistics"""
        by_class = defaultdict(int)
        by_state = defaultdict(int)

        for record in self._records.values():
            by_class[record.record_class.value] += 1
            by_state[record.lifecycle_state.value] += 1

        return {
            'total_records': self._stats['total_records'],
            'disposed_records': self._stats['disposed_records'],
            'vital_records': self._stats['vital_records'],
            'by_class': dict(by_class),
            'by_state': dict(by_state),
            'legal_holds_active': len(self._legal_holds)
        }


# Singleton instance
_records_manager: Optional[RecordsManager] = None


def get_records_manager() -> RecordsManager:
    """Get singleton records manager instance"""
    global _records_manager
    if _records_manager is None:
        _records_manager = RecordsManager()
    return _records_manager


# ============================================================================
# Compliance Frameworks
# ============================================================================


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    ISO_27001 = "iso_27001"
    NIST_CSF = "nist_csf"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC_2 = "soc_2"


class ControlStatus(Enum):
    """Control implementation status"""
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class Control:
    """Compliance control"""
    control_id: str
    framework: ComplianceFramework
    title: str
    description: str
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    evidence: List[str] = field(default_factory=list)
    assessment_date: Optional[datetime] = None
    assessor: Optional[str] = None
    notes: Optional[str] = None
    risk_level: str = "medium"


class ComplianceManager:
    """
    Compliance Framework Manager

    Manages compliance controls and assessments.
    """

    def __init__(self):
        self._controls: Dict[str, Control] = {}
        self._frameworks = self._initialize_frameworks()
        self._lock = Lock()

    def _initialize_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance frameworks"""
        return {
            ComplianceFramework.ISO_27001.value: {
                'name': 'ISO/IEC 27001:2013',
                'domains': 14,
                'controls': 114,
                'description': 'Information Security Management System'
            },
            ComplianceFramework.NIST_CSF.value: {
                'name': 'NIST Cybersecurity Framework',
                'functions': 5,
                'controls': 108,
                'description': 'Identify, Protect, Detect, Respond, Recover'
            },
            ComplianceFramework.PCI_DSS.value: {
                'name': 'PCI DSS v4.0',
                'requirements': 12,
                'controls': 200,
                'description': 'Payment Card Industry Data Security Standard'
            },
            ComplianceFramework.GDPR.value: {
                'name': 'GDPR',
                'principles': 7,
                'controls': 99,
                'description': 'General Data Protection Regulation'
            },
            ComplianceFramework.HIPAA.value: {
                'name': 'HIPAA',
                'safeguards': 3,
                'controls': 45,
                'description': 'Health Insurance Portability and Accountability Act'
            },
            ComplianceFramework.SOC_2.value: {
                'name': 'SOC 2 Type II',
                'criteria': 5,
                'controls': 64,
                'description': 'Trust Services Criteria'
            }
        }

    def add_control(
        self,
        framework: ComplianceFramework,
        control_id: str,
        title: str,
        description: str,
        risk_level: str = "medium"
    ) -> Control:
        """Add control to framework"""
        control = Control(
            control_id=control_id,
            framework=framework,
            title=title,
            description=description,
            risk_level=risk_level
        )

        with self._lock:
            key = f"{framework.value}:{control_id}"
            self._controls[key] = control

        return control

    def assess_control(
        self,
        framework: ComplianceFramework,
        control_id: str,
        status: ControlStatus,
        evidence: Optional[List[str]] = None,
        notes: Optional[str] = None,
        assessor: Optional[str] = None
    ) -> Optional[Control]:
        """Assess control implementation"""
        key = f"{framework.value}:{control_id}"
        control = self._controls.get(key)

        if not control:
            return None

        with self._lock:
            control.status = status
            if evidence:
                control.evidence.extend(evidence)
            control.notes = notes
            control.assessor = assessor
            control.assessment_date = datetime.now()

        return control

    def get_compliance_score(
        self,
        framework: ComplianceFramework
    ) -> Dict[str, Any]:
        """Calculate compliance score for framework"""
        controls = [
            c for c in self._controls.values()
            if c.framework == framework
        ]

        if not controls:
            return {'score': 0, 'total_controls': 0}

        total = len(controls)
        implemented = sum(
            1 for c in controls
            if c.status == ControlStatus.IMPLEMENTED
        )
        partial = sum(
            1 for c in controls
            if c.status == ControlStatus.PARTIALLY_IMPLEMENTED
        )

        # Calculate weighted score
        score = ((implemented * 1.0) + (partial * 0.5)) / total * 100

        return {
            'framework': framework.value,
            'score': round(score, 1),
            'total_controls': total,
            'implemented': implemented,
            'partially_implemented': partial,
            'not_implemented': total - implemented - partial
        }

    def get_gaps(
        self,
        framework: ComplianceFramework
    ) -> List[Control]:
        """Get compliance gaps (not implemented controls)"""
        return [
            c for c in self._controls.values()
            if c.framework == framework and
            c.status == ControlStatus.NOT_IMPLEMENTED
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get compliance statistics"""
        by_framework = defaultdict(int)
        by_status = defaultdict(int)

        for control in self._controls.values():
            by_framework[control.framework.value] += 1
            by_status[control.status.value] += 1

        return {
            'total_controls': len(self._controls),
            'by_framework': dict(by_framework),
            'by_status': dict(by_status),
            'frameworks_tracked': len(self._frameworks)
        }


# Singleton instance
_compliance_manager: Optional[ComplianceManager] = None


def get_compliance_manager() -> ComplianceManager:
    """Get singleton compliance manager instance"""
    global _compliance_manager
    if _compliance_manager is None:
        _compliance_manager = ComplianceManager()
    return _compliance_manager


# ============================================================================
# eDiscovery
# ============================================================================


@dataclass
class LegalHold:
    """Legal hold"""
    hold_id: str
    case_name: str
    case_number: str
    start_date: datetime
    end_date: Optional[datetime] = None
    custodians: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    records_on_hold: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """eDiscovery search result"""
    collection_id: str
    query: str
    total_hits: int
    documents: List[Dict[str, Any]] = field(default_factory=list)
    custodians: List[str] = field(default_factory=list)
    date_range: Optional[tuple] = None


class eDiscoveryManager:
    """
    eDiscovery Platform

    Manages legal holds and document discovery.
    """

    def __init__(self):
        self._legal_holds: Dict[str, LegalHold] = {}
        self._collections: Dict[str, SearchResult] = {}
        self._lock = Lock()

    def create_legal_hold(
        self,
        case_name: str,
        case_number: str,
        custodians: List[str],
        keywords: Optional[List[str]] = None,
        start_date: Optional[datetime] = None
    ) -> LegalHold:
        """Create legal hold"""
        hold_id = str(uuid4())

        hold = LegalHold(
            hold_id=hold_id,
            case_name=case_name,
            case_number=case_number,
            start_date=start_date or datetime.now(),
            custodians=custodians,
            keywords=keywords or []
        )

        with self._lock:
            self._legal_holds[hold_id] = hold

        return hold

    def search(
        self,
        legal_hold_id: str,
        query: str,
        date_range: Optional[tuple] = None,
        custodians: Optional[List[str]] = None
    ) -> SearchResult:
        """Search for responsive documents"""
        hold = self._legal_holds.get(legal_hold_id)
        if not hold:
            raise ValueError(f"Legal hold {legal_hold_id} not found")

        collection_id = str(uuid4())

        # In real implementation, perform search across repositories
        result = SearchResult(
            collection_id=collection_id,
            query=query,
            total_hits=0,  # Would be actual search results
            custodians=custodians or hold.custodians,
            date_range=date_range
        )

        with self._lock:
            self._collections[collection_id] = result

        return result

    def export_collection(
        self,
        collection_id: str,
        format: str = "pst",
        include_metadata: bool = True,
        deduplicate: bool = True
    ) -> Dict[str, Any]:
        """Export collection for legal review"""
        collection = self._collections.get(collection_id)
        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        export_id = str(uuid4())

        return {
            'export_id': export_id,
            'collection_id': collection_id,
            'format': format,
            'total_documents': collection.total_hits,
            'export_path': f"/exports/{export_id}.{format}",
            'include_metadata': include_metadata,
            'deduplicated': deduplicate
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get eDiscovery statistics"""
        active_holds = sum(
            1 for h in self._legal_holds.values()
            if h.end_date is None
        )

        total_custodians = len(set(
            c for h in self._legal_holds.values()
            for c in h.custodians
        ))

        return {
            'total_legal_holds': len(self._legal_holds),
            'active_holds': active_holds,
            'total_collections': len(self._collections),
            'total_custodians': total_custodians
        }


# Singleton instance
_ediscovery_manager: Optional[eDiscoveryManager] = None


def get_ediscovery_manager() -> eDiscoveryManager:
    """Get singleton eDiscovery manager instance"""
    global _ediscovery_manager
    if _ediscovery_manager is None:
        _ediscovery_manager = eDiscoveryManager()
    return _ediscovery_manager


# ============================================================================
# Data Retention
# ============================================================================


@dataclass
class RetentionPolicy:
    """Data retention policy"""
    policy_id: str
    name: str
    description: str
    retention_period: timedelta
    trigger_event: str = "creation_date"
    applies_to: Dict[str, Any] = field(default_factory=dict)
    disposition_action: str = "permanent_delete"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DispositionItem:
    """Item scheduled for disposition"""
    disposition_id: str
    record_id: str
    scheduled_date: datetime
    policy_id: str
    approved: bool = False
    approver: Optional[str] = None
    approval_date: Optional[datetime] = None


class RetentionEngine:
    """
    Data Retention Engine

    Automates retention and disposition.
    """

    def __init__(self):
        self._policies: Dict[str, RetentionPolicy] = {}
        self._disposition_queue: Dict[str, DispositionItem] = {}
        self._lock = Lock()

    def create_policy(
        self,
        name: str,
        description: str,
        retention_period: timedelta,
        trigger_event: str = "creation_date",
        applies_to: Optional[Dict[str, Any]] = None,
        disposition_action: str = "permanent_delete"
    ) -> RetentionPolicy:
        """Create retention policy"""
        policy_id = str(uuid4())

        policy = RetentionPolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            retention_period=retention_period,
            trigger_event=trigger_event,
            applies_to=applies_to or {},
            disposition_action=disposition_action
        )

        with self._lock:
            self._policies[policy_id] = policy

        return policy

    def schedule_disposition(
        self,
        record_id: str,
        policy_id: str,
        scheduled_date: datetime
    ) -> DispositionItem:
        """Schedule record for disposition"""
        disposition_id = str(uuid4())

        item = DispositionItem(
            disposition_id=disposition_id,
            record_id=record_id,
            scheduled_date=scheduled_date,
            policy_id=policy_id
        )

        with self._lock:
            self._disposition_queue[disposition_id] = item

        return item

    def approve_disposition(
        self,
        disposition_id: str,
        approver: str,
        notes: Optional[str] = None
    ) -> bool:
        """Approve disposition"""
        item = self._disposition_queue.get(disposition_id)
        if not item:
            return False

        with self._lock:
            item.approved = True
            item.approver = approver
            item.approval_date = datetime.now()

        return True

    def get_disposition_queue(
        self,
        days_ahead: int = 30,
        requires_approval: bool = False
    ) -> List[DispositionItem]:
        """Get disposition queue"""
        cutoff = datetime.now() + timedelta(days=days_ahead)

        items = [
            item for item in self._disposition_queue.values()
            if item.scheduled_date <= cutoff
        ]

        if requires_approval:
            items = [item for item in items if not item.approved]

        return items

    def get_statistics(self) -> Dict[str, Any]:
        """Get retention statistics"""
        pending = sum(1 for i in self._disposition_queue.values() if not i.approved)
        approved = sum(1 for i in self._disposition_queue.values() if i.approved)

        return {
            'total_policies': len(self._policies),
            'disposition_queue': len(self._disposition_queue),
            'pending_approval': pending,
            'approved': approved
        }


# Singleton instance
_retention_engine: Optional[RetentionEngine] = None


def get_retention_engine() -> RetentionEngine:
    """Get singleton retention engine instance"""
    global _retention_engine
    if _retention_engine is None:
        _retention_engine = RetentionEngine()
    return _retention_engine


# ============================================================================
# Audit Management
# ============================================================================


class AuditSeverity(Enum):
    """Audit finding severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class AuditFinding:
    """Audit finding"""
    finding_id: str
    audit_id: str
    title: str
    severity: AuditSeverity
    description: str
    control_reference: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "open"
    progress: int = 0
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditPlan:
    """Audit plan"""
    audit_id: str
    title: str
    audit_type: str
    scope: str
    start_date: datetime
    end_date: datetime
    auditors: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class AuditManager:
    """
    Audit Management System

    Manages audit planning and findings.
    """

    def __init__(self):
        self._audit_plans: Dict[str, AuditPlan] = {}
        self._findings: Dict[str, AuditFinding] = {}
        self._lock = Lock()

    def create_audit_plan(
        self,
        title: str,
        audit_type: str,
        scope: str,
        start_date: datetime,
        end_date: datetime,
        auditors: Optional[List[str]] = None
    ) -> AuditPlan:
        """Create audit plan"""
        audit_id = str(uuid4())

        plan = AuditPlan(
            audit_id=audit_id,
            title=title,
            audit_type=audit_type,
            scope=scope,
            start_date=start_date,
            end_date=end_date,
            auditors=auditors or []
        )

        with self._lock:
            self._audit_plans[audit_id] = plan

        return plan

    def create_finding(
        self,
        audit_id: str,
        title: str,
        severity: AuditSeverity,
        description: str,
        control_reference: Optional[str] = None,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None
    ) -> AuditFinding:
        """Create audit finding"""
        finding_id = str(uuid4())

        finding = AuditFinding(
            finding_id=finding_id,
            audit_id=audit_id,
            title=title,
            severity=severity,
            description=description,
            control_reference=control_reference,
            assigned_to=assigned_to,
            due_date=due_date
        )

        with self._lock:
            self._findings[finding_id] = finding

            # Add to audit plan
            plan = self._audit_plans.get(audit_id)
            if plan:
                plan.findings.append(finding_id)

        return finding

    def update_remediation(
        self,
        finding_id: str,
        status: str,
        progress: int,
        notes: Optional[str] = None
    ) -> Optional[AuditFinding]:
        """Update finding remediation status"""
        finding = self._findings.get(finding_id)
        if not finding:
            return None

        with self._lock:
            finding.status = status
            finding.progress = progress
            if notes:
                finding.notes = notes

        return finding

    def get_overdue_findings(self) -> List[AuditFinding]:
        """Get overdue findings"""
        now = datetime.now()
        return [
            f for f in self._findings.values()
            if f.due_date and f.due_date < now and f.status != "closed"
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics"""
        by_severity = defaultdict(int)
        by_status = defaultdict(int)

        for finding in self._findings.values():
            by_severity[finding.severity.value] += 1
            by_status[finding.status] += 1

        return {
            'total_audits': len(self._audit_plans),
            'total_findings': len(self._findings),
            'by_severity': dict(by_severity),
            'by_status': dict(by_status),
            'overdue_findings': len(self.get_overdue_findings())
        }


# Singleton instance
_audit_manager: Optional[AuditManager] = None


def get_audit_manager() -> AuditManager:
    """Get singleton audit manager instance"""
    global _audit_manager
    if _audit_manager is None:
        _audit_manager = AuditManager()
    return _audit_manager


# ============================================================================
# Policy Management
# ============================================================================


@dataclass
class PolicyVersion:
    """Policy version"""
    version_id: str
    version_number: int
    content: str
    effective_date: datetime
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Acknowledgment:
    """Policy acknowledgment"""
    acknowledgment_id: str
    policy_id: str
    user_id: str
    acknowledged_at: datetime = field(default_factory=datetime.now)


@dataclass
class Policy:
    """Policy document"""
    policy_id: str
    title: str
    category: str
    current_version: int = 1
    versions: List[PolicyVersion] = field(default_factory=list)
    requires_acknowledgment: bool = False
    acknowledgments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class PolicyManager:
    """
    Policy Management System

    Manages policy lifecycle and acknowledgment.
    """

    def __init__(self):
        self._policies: Dict[str, Policy] = {}
        self._acknowledgments: Dict[str, Acknowledgment] = {}
        self._lock = Lock()

    def create_policy(
        self,
        title: str,
        category: str,
        content: str,
        effective_date: datetime,
        requires_acknowledgment: bool = False
    ) -> Policy:
        """Create new policy"""
        policy_id = str(uuid4())
        version_id = str(uuid4())

        version = PolicyVersion(
            version_id=version_id,
            version_number=1,
            content=content,
            effective_date=effective_date
        )

        policy = Policy(
            policy_id=policy_id,
            title=title,
            category=category,
            versions=[version],
            requires_acknowledgment=requires_acknowledgment
        )

        with self._lock:
            self._policies[policy_id] = policy

        return policy

    def acknowledge_policy(
        self,
        policy_id: str,
        user_id: str
    ) -> Acknowledgment:
        """Acknowledge policy"""
        policy = self._policies.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")

        ack_id = str(uuid4())

        acknowledgment = Acknowledgment(
            acknowledgment_id=ack_id,
            policy_id=policy_id,
            user_id=user_id
        )

        with self._lock:
            self._acknowledgments[ack_id] = acknowledgment
            policy.acknowledgments.append(ack_id)

        return acknowledgment

    def get_acknowledgment_status(
        self,
        policy_id: str
    ) -> Dict[str, Any]:
        """Get policy acknowledgment status"""
        policy = self._policies.get(policy_id)
        if not policy:
            return {}

        total_acks = len(policy.acknowledgments)
        # In real implementation, would calculate against total users
        total_users = 500  # Placeholder

        return {
            'policy_id': policy_id,
            'total_users': total_users,
            'acknowledged': total_acks,
            'pending': total_users - total_acks,
            'acknowledgment_rate': (total_acks / total_users * 100) if total_users > 0 else 0
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get policy statistics"""
        by_category = defaultdict(int)
        requires_ack = 0

        for policy in self._policies.values():
            by_category[policy.category] += 1
            if policy.requires_acknowledgment:
                requires_ack += 1

        return {
            'total_policies': len(self._policies),
            'by_category': dict(by_category),
            'requires_acknowledgment': requires_ack,
            'total_acknowledgments': len(self._acknowledgments)
        }


# Singleton instance
_policy_manager: Optional[PolicyManager] = None


def get_policy_manager() -> PolicyManager:
    """Get singleton policy manager instance"""
    global _policy_manager
    if _policy_manager is None:
        _policy_manager = PolicyManager()
    return _policy_manager
