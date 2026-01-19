"""
SOC 2 Compliance Framework

Implements SOC 2 (Service Organization Control 2) Trust Services Criteria (TSC):
- Security (Common Criteria - CC)
- Availability
- Processing Integrity
- Confidentiality
- Privacy

Based on AICPA Trust Services Criteria framework.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class TrustServiceCategory(str, Enum):
    """Trust Services Categories"""

    SECURITY = "security"  # CC - Common Criteria
    AVAILABILITY = "availability"
    PROCESSING_INTEGRITY = "processing_integrity"
    CONFIDENTIALITY = "confidentiality"
    PRIVACY = "privacy"


class ControlStatus(str, Enum):
    """Control implementation status"""

    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    OPERATING_EFFECTIVELY = "operating_effectively"
    NEEDS_IMPROVEMENT = "needs_improvement"


class IncidentSeverity(str, Enum):
    """Incident severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeRiskLevel(str, Enum):
    """Change risk assessment levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Control:
    """SOC 2 Control"""

    id: str
    category: TrustServiceCategory
    title: str
    description: str
    control_activity: str
    frequency: str  # daily, weekly, monthly, quarterly, annually
    owner: str
    status: ControlStatus
    last_tested: Optional[datetime] = None
    test_results: Optional[str] = None
    evidence_location: Optional[str] = None
    deficiencies: List[str] = field(default_factory=list)
    remediation_plan: Optional[str] = None


@dataclass
class Evidence:
    """Evidence for control testing"""

    id: str
    control_id: str
    collected_date: datetime
    collected_by: str
    evidence_type: str  # document, screenshot, log, observation
    description: str
    file_path: Optional[str] = None
    notes: str = ""


@dataclass
class Incident:
    """Security/operational incident"""

    id: str
    title: str
    description: str
    category: TrustServiceCategory
    severity: IncidentSeverity
    detected_at: datetime
    detected_by: str
    affected_systems: List[str]
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class ChangeRequest:
    """Change management request"""

    id: str
    title: str
    description: str
    requested_by: str
    requested_at: datetime
    risk_level: ChangeRiskLevel
    affected_systems: List[str]
    rollback_plan: str
    testing_plan: str
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    implemented: bool = False
    implemented_at: Optional[datetime] = None


@dataclass
class Vendor:
    """Third-party vendor"""

    id: str
    name: str
    services_provided: List[str]
    criticality: str  # low, medium, high, critical
    data_access: bool
    soc2_report: bool
    soc2_report_date: Optional[datetime] = None
    contract_expiry: Optional[datetime] = None
    last_assessment: Optional[datetime] = None
    assessment_notes: str = ""


@dataclass
class AuditLog:
    """Audit log entry"""

    id: str
    timestamp: datetime
    user: str
    action: str
    resource: str
    ip_address: str
    result: str  # success, failure
    details: Dict[str, Any] = field(default_factory=dict)


class SecurityControls:
    """CC (Common Criteria) - Security Controls"""

    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self._initialize_security_controls()

    def _initialize_security_controls(self):
        """Initialize Security controls (CC1-CC9)"""
        controls = [
            # CC1: Control Environment
            Control(
                id="CC1.1",
                category=TrustServiceCategory.SECURITY,
                title="Management Philosophy and Operating Style",
                description="Management demonstrates commitment to integrity and ethical values",
                control_activity="Code of conduct reviewed and signed annually by all employees",
                frequency="annually",
                owner="Management",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="CC1.2",
                category=TrustServiceCategory.SECURITY,
                title="Board Independence and Oversight",
                description="Board demonstrates independence and exercises oversight",
                control_activity="Quarterly board meetings with security updates",
                frequency="quarterly",
                owner="Board",
                status=ControlStatus.IMPLEMENTED,
            ),
            # CC2: Communication and Information
            Control(
                id="CC2.1",
                category=TrustServiceCategory.SECURITY,
                title="Internal Communication",
                description="Information needed to support functioning of internal control is communicated",
                control_activity="Monthly security awareness training and communications",
                frequency="monthly",
                owner="Security Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            # CC3: Risk Assessment
            Control(
                id="CC3.1",
                category=TrustServiceCategory.SECURITY,
                title="Risk Identification",
                description="Organization identifies risks to achievement of objectives",
                control_activity="Annual risk assessment conducted",
                frequency="annually",
                owner="Risk Manager",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="CC3.2",
                category=TrustServiceCategory.SECURITY,
                title="Risk Analysis",
                description="Analyzes identified risks",
                control_activity="Risk scoring and prioritization",
                frequency="annually",
                owner="Risk Manager",
                status=ControlStatus.IMPLEMENTED,
            ),
            # CC4: Monitoring Activities
            Control(
                id="CC4.1",
                category=TrustServiceCategory.SECURITY,
                title="Ongoing Monitoring",
                description="Ongoing monitoring activities conducted",
                control_activity="SIEM monitoring and alerting 24/7",
                frequency="daily",
                owner="SOC Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            # CC5: Control Activities
            Control(
                id="CC5.1",
                category=TrustServiceCategory.SECURITY,
                title="Logical Access Controls",
                description="Restricts logical access to authorized users",
                control_activity="Role-based access control (RBAC) implemented",
                frequency="daily",
                owner="Security Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            Control(
                id="CC5.2",
                category=TrustServiceCategory.SECURITY,
                title="Multi-Factor Authentication",
                description="MFA required for accessing sensitive systems",
                control_activity="MFA enforced for all admin accounts",
                frequency="daily",
                owner="Security Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            # CC6: Logical and Physical Access
            Control(
                id="CC6.1",
                category=TrustServiceCategory.SECURITY,
                title="Access Reviews",
                description="Periodic reviews of access rights",
                control_activity="Quarterly access reviews conducted",
                frequency="quarterly",
                owner="Security Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="CC6.2",
                category=TrustServiceCategory.SECURITY,
                title="Password Policy",
                description="Strong password requirements enforced",
                control_activity="Password complexity and rotation enforced",
                frequency="daily",
                owner="IT Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            # CC7: System Operations
            Control(
                id="CC7.1",
                category=TrustServiceCategory.SECURITY,
                title="Vulnerability Management",
                description="Identifies and manages vulnerabilities",
                control_activity="Monthly vulnerability scans conducted",
                frequency="monthly",
                owner="Security Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="CC7.2",
                category=TrustServiceCategory.SECURITY,
                title="Patch Management",
                description="Security patches applied timely",
                control_activity="Critical patches applied within 30 days",
                frequency="monthly",
                owner="IT Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            # CC8: Change Management
            Control(
                id="CC8.1",
                category=TrustServiceCategory.SECURITY,
                title="Change Authorization",
                description="Changes authorized before implementation",
                control_activity="CAB approval required for production changes",
                frequency="daily",
                owner="Change Manager",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            Control(
                id="CC8.2",
                category=TrustServiceCategory.SECURITY,
                title="Change Testing",
                description="Changes tested before deployment",
                control_activity="Test environment validation required",
                frequency="daily",
                owner="Development Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            # CC9: Risk Mitigation
            Control(
                id="CC9.1",
                category=TrustServiceCategory.SECURITY,
                title="Encryption",
                description="Data encrypted in transit and at rest",
                control_activity="TLS 1.2+ and AES-256 encryption enforced",
                frequency="daily",
                owner="Security Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            Control(
                id="CC9.2",
                category=TrustServiceCategory.SECURITY,
                title="Backup and Recovery",
                description="Data backed up and recoverable",
                control_activity="Daily backups with quarterly restoration tests",
                frequency="daily",
                owner="IT Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
        ]

        for control in controls:
            self.controls[control.id] = control


class AvailabilityControls:
    """Availability Controls (A1)"""

    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self._initialize_availability_controls()

    def _initialize_availability_controls(self):
        """Initialize Availability controls"""
        controls = [
            Control(
                id="A1.1",
                category=TrustServiceCategory.AVAILABILITY,
                title="System Availability Monitoring",
                description="Monitors system availability and performance",
                control_activity="24/7 uptime monitoring with alerts",
                frequency="daily",
                owner="Operations Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            Control(
                id="A1.2",
                category=TrustServiceCategory.AVAILABILITY,
                title="Capacity Planning",
                description="Plans for capacity to meet service commitments",
                control_activity="Quarterly capacity reviews and projections",
                frequency="quarterly",
                owner="Infrastructure Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="A1.3",
                category=TrustServiceCategory.AVAILABILITY,
                title="Incident Response",
                description="Incidents detected and responded to timely",
                control_activity="Incident response procedures with SLAs",
                frequency="daily",
                owner="Operations Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
        ]

        for control in controls:
            self.controls[control.id] = control


class ProcessingIntegrityControls:
    """Processing Integrity Controls (PI1)"""

    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self._initialize_pi_controls()

    def _initialize_pi_controls(self):
        """Initialize Processing Integrity controls"""
        controls = [
            Control(
                id="PI1.1",
                category=TrustServiceCategory.PROCESSING_INTEGRITY,
                title="Data Input Validation",
                description="Input data validated for completeness and accuracy",
                control_activity="Input validation rules implemented in application",
                frequency="daily",
                owner="Development Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            Control(
                id="PI1.2",
                category=TrustServiceCategory.PROCESSING_INTEGRITY,
                title="Processing Accuracy",
                description="Data processed accurately and completely",
                control_activity="Automated testing and reconciliation",
                frequency="daily",
                owner="QA Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="PI1.3",
                category=TrustServiceCategory.PROCESSING_INTEGRITY,
                title="Error Handling",
                description="Processing errors detected and corrected",
                control_activity="Error logging and alerting system",
                frequency="daily",
                owner="Development Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
        ]

        for control in controls:
            self.controls[control.id] = control


class ConfidentialityControls:
    """Confidentiality Controls (C1)"""

    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self._initialize_confidentiality_controls()

    def _initialize_confidentiality_controls(self):
        """Initialize Confidentiality controls"""
        controls = [
            Control(
                id="C1.1",
                category=TrustServiceCategory.CONFIDENTIALITY,
                title="Data Classification",
                description="Confidential information identified and classified",
                control_activity="Data classification policy and procedures",
                frequency="annually",
                owner="Security Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="C1.2",
                category=TrustServiceCategory.CONFIDENTIALITY,
                title="Confidentiality Agreements",
                description="Confidentiality agreements signed by personnel",
                control_activity="NDAs signed by all employees and contractors",
                frequency="annually",
                owner="HR Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="C1.3",
                category=TrustServiceCategory.CONFIDENTIALITY,
                title="Secure Disposal",
                description="Confidential information securely disposed",
                control_activity="Secure deletion and shredding procedures",
                frequency="daily",
                owner="IT Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
        ]

        for control in controls:
            self.controls[control.id] = control


class PrivacyControls:
    """Privacy Controls (P1-P8)"""

    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self._initialize_privacy_controls()

    def _initialize_privacy_controls(self):
        """Initialize Privacy controls"""
        controls = [
            Control(
                id="P1.1",
                category=TrustServiceCategory.PRIVACY,
                title="Privacy Notice",
                description="Privacy notice provided to data subjects",
                control_activity="Privacy policy published and accessible",
                frequency="annually",
                owner="Privacy Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="P2.1",
                category=TrustServiceCategory.PRIVACY,
                title="Consent Management",
                description="Consent obtained for data collection and use",
                control_activity="Consent management system implemented",
                frequency="daily",
                owner="Privacy Team",
                status=ControlStatus.OPERATING_EFFECTIVELY,
            ),
            Control(
                id="P3.1",
                category=TrustServiceCategory.PRIVACY,
                title="Data Subject Rights",
                description="Data subject rights requests processed",
                control_activity="DSR portal and procedures",
                frequency="daily",
                owner="Privacy Team",
                status=ControlStatus.IMPLEMENTED,
            ),
            Control(
                id="P4.1",
                category=TrustServiceCategory.PRIVACY,
                title="Data Retention",
                description="Personal data retained per policy",
                control_activity="Data retention schedules and automated deletion",
                frequency="monthly",
                owner="Privacy Team",
                status=ControlStatus.IMPLEMENTED,
            ),
        ]

        for control in controls:
            self.controls[control.id] = control


class IncidentManager:
    """Manages incidents for SOC 2"""

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}

    def create_incident(
        self,
        title: str,
        description: str,
        category: TrustServiceCategory,
        severity: IncidentSeverity,
        detected_by: str,
        affected_systems: List[str],
    ) -> str:
        """Create new incident"""
        incident_id = str(uuid.uuid4())

        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            detected_at=datetime.now(),
            detected_by=detected_by,
            affected_systems=affected_systems,
        )

        self.incidents[incident_id] = incident
        return incident_id

    def resolve_incident(self, incident_id: str, root_cause: str, resolution: str, lessons_learned: List[str]) -> bool:
        """Resolve incident"""
        if incident_id not in self.incidents:
            return False

        incident = self.incidents[incident_id]
        incident.root_cause = root_cause
        incident.resolution = resolution
        incident.lessons_learned = lessons_learned
        incident.resolved_at = datetime.now()

        return True

    def get_open_incidents(self) -> List[Incident]:
        """Get all open incidents"""
        return [i for i in self.incidents.values() if not i.resolved_at]


class ChangeManager:
    """Manages changes for SOC 2"""

    def __init__(self):
        self.changes: Dict[str, ChangeRequest] = {}

    def create_change_request(
        self,
        title: str,
        description: str,
        requested_by: str,
        risk_level: ChangeRiskLevel,
        affected_systems: List[str],
        rollback_plan: str,
        testing_plan: str,
    ) -> str:
        """Create change request"""
        change_id = str(uuid.uuid4())

        change = ChangeRequest(
            id=change_id,
            title=title,
            description=description,
            requested_by=requested_by,
            requested_at=datetime.now(),
            risk_level=risk_level,
            affected_systems=affected_systems,
            rollback_plan=rollback_plan,
            testing_plan=testing_plan,
        )

        self.changes[change_id] = change
        return change_id

    def approve_change(self, change_id: str, approved_by: str) -> bool:
        """Approve change request"""
        if change_id not in self.changes:
            return False

        change = self.changes[change_id]
        change.approved = True
        change.approved_by = approved_by
        change.approved_at = datetime.now()

        return True

    def implement_change(self, change_id: str) -> bool:
        """Mark change as implemented"""
        if change_id not in self.changes:
            return False

        change = self.changes[change_id]

        if not change.approved:
            return False

        change.implemented = True
        change.implemented_at = datetime.now()

        return True


class SOC2ComplianceEngine:
    """Main SOC 2 compliance engine"""

    def __init__(self):
        self.security_controls = SecurityControls()
        self.availability_controls = AvailabilityControls()
        self.pi_controls = ProcessingIntegrityControls()
        self.confidentiality_controls = ConfidentialityControls()
        self.privacy_controls = PrivacyControls()

        self.incident_manager = IncidentManager()
        self.change_manager = ChangeManager()

        # Evidence collection
        self.evidence: List[Evidence] = []

        # Vendors
        self.vendors: Dict[str, Vendor] = {}

        # Audit logs
        self.audit_logs: List[AuditLog] = []

    def get_all_controls(self) -> Dict[str, Control]:
        """Get all controls across all categories"""
        all_controls = {}

        all_controls.update(self.security_controls.controls)
        all_controls.update(self.availability_controls.controls)
        all_controls.update(self.pi_controls.controls)
        all_controls.update(self.confidentiality_controls.controls)
        all_controls.update(self.privacy_controls.controls)

        return all_controls

    def collect_evidence(
        self, control_id: str, evidence_type: str, description: str, collected_by: str, file_path: Optional[str] = None
    ) -> str:
        """Collect evidence for control"""
        evidence_id = str(uuid.uuid4())

        evidence = Evidence(
            id=evidence_id,
            control_id=control_id,
            collected_date=datetime.now(),
            collected_by=collected_by,
            evidence_type=evidence_type,
            description=description,
            file_path=file_path,
        )

        self.evidence.append(evidence)
        return evidence_id

    def test_control(self, control_id: str, tester: str, results: str) -> bool:
        """Test control effectiveness"""
        controls = self.get_all_controls()

        if control_id not in controls:
            return False

        control = controls[control_id]
        control.last_tested = datetime.now()
        control.test_results = results

        # Update status based on results
        if "deficiency" in results.lower():
            control.status = ControlStatus.NEEDS_IMPROVEMENT
        elif "effective" in results.lower():
            control.status = ControlStatus.OPERATING_EFFECTIVELY
        else:
            control.status = ControlStatus.IMPLEMENTED

        return True

    def register_vendor(self, name: str, services: List[str], criticality: str, data_access: bool) -> str:
        """Register third-party vendor"""
        vendor_id = str(uuid.uuid4())

        vendor = Vendor(
            id=vendor_id,
            name=name,
            services_provided=services,
            criticality=criticality,
            data_access=data_access,
            soc2_report=False,
        )

        self.vendors[vendor_id] = vendor
        return vendor_id

    def log_audit_event(
        self,
        user: str,
        action: str,
        resource: str,
        ip_address: str,
        result: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log audit event"""
        log = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user=user,
            action=action,
            resource=resource,
            ip_address=ip_address,
            result=result,
            details=details or {},
        )

        self.audit_logs.append(log)

        # Retain logs for at least 1 year
        cutoff = datetime.now() - timedelta(days=365)
        self.audit_logs = [log for log in self.audit_logs if log.timestamp > cutoff]

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate SOC 2 compliance status report"""
        all_controls = self.get_all_controls()

        # Count controls by status
        status_counts = {}
        for control in all_controls.values():
            status = control.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by category
        category_counts = {}
        for control in all_controls.values():
            cat = control.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Calculate compliance score
        operating_effectively = status_counts.get(ControlStatus.OPERATING_EFFECTIVELY.value, 0)
        total_controls = len(all_controls)
        compliance_score = (operating_effectively / total_controls * 100) if total_controls > 0 else 0

        return {
            "total_controls": total_controls,
            "compliance_score": f"{compliance_score:.1f}%",
            "controls_by_status": status_counts,
            "controls_by_category": category_counts,
            "evidence_collected": len(self.evidence),
            "open_incidents": len(self.incident_manager.get_open_incidents()),
            "pending_changes": len([c for c in self.change_manager.changes.values() if not c.implemented]),
            "vendors_managed": len(self.vendors),
            "audit_logs": len(self.audit_logs),
        }


# Global instance
_soc2_engine: Optional[SOC2ComplianceEngine] = None


def get_soc2_engine() -> SOC2ComplianceEngine:
    """Get global SOC 2 engine instance"""
    global _soc2_engine

    if _soc2_engine is None:
        _soc2_engine = SOC2ComplianceEngine()

    return _soc2_engine


def configure_soc2_engine():
    """Configure SOC 2 engine"""
    global _soc2_engine
    _soc2_engine = SOC2ComplianceEngine()
