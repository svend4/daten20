"""
Compliance Framework Management

Support for ISO 27001, NIST CSF, PCI DSS, GDPR, HIPAA, SOC 2 compliance
frameworks with control assessment, evidence management, and scoring.

Part of v3.8 Governance & Compliance implementation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class Framework(Enum):
    """Supported compliance frameworks."""

    ISO_27001 = "iso_27001"
    NIST_CSF = "nist_csf"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC_2 = "soc_2"


class ControlStatus(Enum):
    """Control implementation status."""

    NOT_IMPLEMENTED = "not_implemented"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    NOT_APPLICABLE = "not_applicable"


class RiskLevel(Enum):
    """Risk assessment levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Control:
    """Compliance control definition."""

    control_id: str
    framework: Framework
    domain: str
    title: str
    description: str
    objective: str
    implementation_guidance: Optional[str] = None
    testing_procedure: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    mapped_controls: List[str] = field(default_factory=list)  # Cross-framework mapping


@dataclass
class Evidence:
    """Supporting evidence for control."""

    evidence_id: str
    control_id: str
    evidence_type: str  # document, screenshot, log, report
    file_path: str
    description: str
    collected_date: datetime = field(default_factory=datetime.now)
    collected_by: Optional[str] = None
    valid_until: Optional[datetime] = None


@dataclass
class ControlAssessment:
    """Control assessment/testing result."""

    assessment_id: str
    control_id: str
    status: ControlStatus
    assessor: str
    assessment_date: datetime
    evidence_ids: List[str] = field(default_factory=list)
    findings: Optional[str] = None
    remediation_required: bool = False
    remediation_plan: Optional[str] = None
    remediation_due_date: Optional[datetime] = None
    notes: Optional[str] = None
    next_assessment_date: Optional[datetime] = None


@dataclass
class ComplianceScore:
    """Compliance scoring result."""

    framework: Framework
    scope: str
    score: float  # 0-100
    total_controls: int
    implemented: int
    in_progress: int
    not_implemented: int
    not_applicable: int
    critical_gaps: int
    high_gaps: int
    calculated_date: datetime = field(default_factory=datetime.now)


class FrameworkBuilder:
    """Build compliance framework controls."""

    @staticmethod
    def build_iso_27001() -> List[Control]:
        """Build ISO 27001 controls (Annex A)."""
        controls = []

        # A.5 - Information security policies
        controls.extend(
            [
                Control(
                    control_id="A.5.1.1",
                    framework=Framework.ISO_27001,
                    domain="Information Security Policies",
                    title="Policies for information security",
                    description="Information security policy and topic-specific policies defined and approved",
                    objective="Provide management direction and support for information security",
                    risk_level=RiskLevel.HIGH,
                ),
                Control(
                    control_id="A.5.1.2",
                    framework=Framework.ISO_27001,
                    domain="Information Security Policies",
                    title="Review of policies",
                    description="Policies reviewed at planned intervals or significant changes",
                    objective="Ensure policies remain suitable and effective",
                    risk_level=RiskLevel.MEDIUM,
                ),
            ]
        )

        # A.6 - Organization of information security
        controls.extend(
            [
                Control(
                    control_id="A.6.1.1",
                    framework=Framework.ISO_27001,
                    domain="Internal Organization",
                    title="Information security roles and responsibilities",
                    description="Security responsibilities defined and allocated",
                    objective="Establish management framework for security",
                    risk_level=RiskLevel.HIGH,
                ),
                Control(
                    control_id="A.6.2.1",
                    framework=Framework.ISO_27001,
                    domain="Mobile Devices",
                    title="Mobile device policy",
                    description="Policy and supporting security measures for mobile devices",
                    objective="Protect information on mobile devices",
                    risk_level=RiskLevel.MEDIUM,
                ),
            ]
        )

        # A.8 - Asset management
        controls.extend(
            [
                Control(
                    control_id="A.8.1.1",
                    framework=Framework.ISO_27001,
                    domain="Asset Management",
                    title="Inventory of assets",
                    description="Assets identified and inventory maintained",
                    objective="Identify organizational assets and protection responsibilities",
                    risk_level=RiskLevel.HIGH,
                    mapped_controls=["NIST.ID.AM-1"],
                ),
                Control(
                    control_id="A.8.1.2",
                    framework=Framework.ISO_27001,
                    domain="Asset Management",
                    title="Ownership of assets",
                    description="Assets maintained in inventory are owned",
                    objective="Ensure appropriate protection of assets",
                    risk_level=RiskLevel.MEDIUM,
                ),
                Control(
                    control_id="A.8.2.1",
                    framework=Framework.ISO_27001,
                    domain="Information Classification",
                    title="Classification of information",
                    description="Information classified according to legal requirements and value",
                    objective="Ensure appropriate level of protection",
                    risk_level=RiskLevel.HIGH,
                ),
            ]
        )

        # A.9 - Access control
        controls.extend(
            [
                Control(
                    control_id="A.9.1.1",
                    framework=Framework.ISO_27001,
                    domain="Access Control",
                    title="Access control policy",
                    description="Policy established and documented for access control",
                    objective="Limit access to information and systems",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["NIST.PR.AC-1", "PCI.7.1"],
                ),
                Control(
                    control_id="A.9.2.1",
                    framework=Framework.ISO_27001,
                    domain="User Access Management",
                    title="User registration",
                    description="Formal process for user access provisioning",
                    objective="Ensure authorized user access",
                    risk_level=RiskLevel.HIGH,
                ),
                Control(
                    control_id="A.9.2.5",
                    framework=Framework.ISO_27001,
                    domain="User Access Management",
                    title="Review of user access rights",
                    description="Asset owners review user access rights at regular intervals",
                    objective="Ensure continued appropriateness of access",
                    risk_level=RiskLevel.HIGH,
                ),
            ]
        )

        # A.12 - Operations security
        controls.extend(
            [
                Control(
                    control_id="A.12.1.1",
                    framework=Framework.ISO_27001,
                    domain="Operations Security",
                    title="Documented operating procedures",
                    description="Operating procedures documented and available",
                    objective="Ensure correct and secure operations",
                    risk_level=RiskLevel.MEDIUM,
                ),
                Control(
                    control_id="A.12.3.1",
                    framework=Framework.ISO_27001,
                    domain="Backup",
                    title="Information backup",
                    description="Backup copies taken and tested regularly",
                    objective="Maintain availability and integrity",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["NIST.PR.IP-4"],
                ),
                Control(
                    control_id="A.12.4.1",
                    framework=Framework.ISO_27001,
                    domain="Logging",
                    title="Event logging",
                    description="Event logs recording activities maintained",
                    objective="Detect unauthorized activities",
                    risk_level=RiskLevel.HIGH,
                    mapped_controls=["NIST.PR.PT-1", "PCI.10.1"],
                ),
            ]
        )

        # A.14 - System acquisition
        controls.extend(
            [
                Control(
                    control_id="A.14.2.1",
                    framework=Framework.ISO_27001,
                    domain="Secure Development",
                    title="Secure development policy",
                    description="Rules for software development established",
                    objective="Ensure security in systems development",
                    risk_level=RiskLevel.HIGH,
                ),
            ]
        )

        # A.18 - Compliance
        controls.extend(
            [
                Control(
                    control_id="A.18.1.1",
                    framework=Framework.ISO_27001,
                    domain="Compliance",
                    title="Identification of applicable legislation",
                    description="Legal requirements identified and documented",
                    objective="Avoid breach of legal obligations",
                    risk_level=RiskLevel.CRITICAL,
                ),
            ]
        )

        return controls

    @staticmethod
    def build_nist_csf() -> List[Control]:
        """Build NIST Cybersecurity Framework controls."""
        controls = []

        # Identify (ID)
        controls.extend(
            [
                Control(
                    control_id="ID.AM-1",
                    framework=Framework.NIST_CSF,
                    domain="Asset Management",
                    title="Physical devices and systems inventoried",
                    description="Maintain inventory of physical devices and systems",
                    objective="Know what needs protection",
                    risk_level=RiskLevel.HIGH,
                    mapped_controls=["A.8.1.1"],
                ),
                Control(
                    control_id="ID.AM-2",
                    framework=Framework.NIST_CSF,
                    domain="Asset Management",
                    title="Software platforms and applications inventoried",
                    description="Maintain software inventory",
                    objective="Know what software is running",
                    risk_level=RiskLevel.HIGH,
                ),
                Control(
                    control_id="ID.RA-1",
                    framework=Framework.NIST_CSF,
                    domain="Risk Assessment",
                    title="Asset vulnerabilities identified and documented",
                    description="Identify and document vulnerabilities",
                    objective="Understand security weaknesses",
                    risk_level=RiskLevel.CRITICAL,
                ),
            ]
        )

        # Protect (PR)
        controls.extend(
            [
                Control(
                    control_id="PR.AC-1",
                    framework=Framework.NIST_CSF,
                    domain="Access Control",
                    title="Identities and credentials managed",
                    description="Manage identities and credentials for authorized access",
                    objective="Control who has access",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["A.9.1.1", "PCI.8.1"],
                ),
                Control(
                    control_id="PR.DS-1",
                    framework=Framework.NIST_CSF,
                    domain="Data Security",
                    title="Data-at-rest protected",
                    description="Protect data at rest using encryption",
                    objective="Prevent unauthorized data disclosure",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["PCI.3.4"],
                ),
                Control(
                    control_id="PR.IP-4",
                    framework=Framework.NIST_CSF,
                    domain="Information Protection",
                    title="Backups managed",
                    description="Backup information is managed and tested",
                    objective="Ensure data recovery capability",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["A.12.3.1"],
                ),
                Control(
                    control_id="PR.PT-1",
                    framework=Framework.NIST_CSF,
                    domain="Protective Technology",
                    title="Audit/log records determined and documented",
                    description="Determine and document audit logs",
                    objective="Enable detection of security events",
                    risk_level=RiskLevel.HIGH,
                    mapped_controls=["A.12.4.1", "PCI.10.1"],
                ),
            ]
        )

        # Detect (DE)
        controls.extend(
            [
                Control(
                    control_id="DE.CM-1",
                    framework=Framework.NIST_CSF,
                    domain="Security Monitoring",
                    title="Network monitored",
                    description="Monitor network for anomalous activity",
                    objective="Detect cybersecurity events",
                    risk_level=RiskLevel.HIGH,
                ),
            ]
        )

        # Respond (RS)
        controls.extend(
            [
                Control(
                    control_id="RS.RP-1",
                    framework=Framework.NIST_CSF,
                    domain="Response Planning",
                    title="Response plan executed",
                    description="Execute response plan during incidents",
                    objective="Respond to detected events",
                    risk_level=RiskLevel.HIGH,
                ),
            ]
        )

        # Recover (RC)
        controls.extend(
            [
                Control(
                    control_id="RC.RP-1",
                    framework=Framework.NIST_CSF,
                    domain="Recovery Planning",
                    title="Recovery plan executed",
                    description="Execute recovery plan during/after incidents",
                    objective="Restore capabilities after incidents",
                    risk_level=RiskLevel.CRITICAL,
                ),
            ]
        )

        return controls

    @staticmethod
    def build_pci_dss() -> List[Control]:
        """Build PCI DSS controls."""
        controls = []

        # Requirement 1: Firewalls
        controls.append(
            Control(
                control_id="PCI.1.1",
                framework=Framework.PCI_DSS,
                domain="Network Security",
                title="Firewall configuration standards",
                description="Establish firewall and router configuration standards",
                objective="Protect cardholder data",
                risk_level=RiskLevel.CRITICAL,
            )
        )

        # Requirement 3: Protect stored data
        controls.extend(
            [
                Control(
                    control_id="PCI.3.4",
                    framework=Framework.PCI_DSS,
                    domain="Data Protection",
                    title="Cardholder data unreadable",
                    description="Render PAN unreadable using encryption",
                    objective="Protect stored cardholder data",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["PR.DS-1"],
                ),
            ]
        )

        # Requirement 7: Restrict access
        controls.extend(
            [
                Control(
                    control_id="PCI.7.1",
                    framework=Framework.PCI_DSS,
                    domain="Access Control",
                    title="Limit access to system components",
                    description="Limit access based on need-to-know",
                    objective="Ensure only authorized access",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["A.9.1.1", "PR.AC-1"],
                ),
            ]
        )

        # Requirement 8: Identify users
        controls.extend(
            [
                Control(
                    control_id="PCI.8.1",
                    framework=Framework.PCI_DSS,
                    domain="User Management",
                    title="Assign unique ID",
                    description="Assign unique ID to each user",
                    objective="Ensure accountability",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["PR.AC-1"],
                ),
            ]
        )

        # Requirement 10: Track access
        controls.extend(
            [
                Control(
                    control_id="PCI.10.1",
                    framework=Framework.PCI_DSS,
                    domain="Logging",
                    title="Implement audit trails",
                    description="Link all access to individual users",
                    objective="Enable tracking of activities",
                    risk_level=RiskLevel.CRITICAL,
                    mapped_controls=["A.12.4.1", "PR.PT-1"],
                ),
            ]
        )

        return controls


class ComplianceManager:
    """Main compliance framework manager."""

    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self.assessments: Dict[str, ControlAssessment] = {}
        self.evidence: Dict[str, Evidence] = {}
        self._initialize_frameworks()

    def _initialize_frameworks(self):
        """Initialize compliance frameworks."""
        builder = FrameworkBuilder()

        # Load all frameworks
        all_controls = []
        all_controls.extend(builder.build_iso_27001())
        all_controls.extend(builder.build_nist_csf())
        all_controls.extend(builder.build_pci_dss())

        for control in all_controls:
            self.controls[control.control_id] = control

        logger.info(f"Initialized {len(self.controls)} compliance controls")

    async def get_framework_controls(self, framework: str, domain: Optional[str] = None) -> List[Control]:
        """Get controls for framework."""
        await asyncio.sleep(0.05)

        framework_enum = Framework(framework)
        controls = [c for c in self.controls.values() if c.framework == framework_enum]

        if domain:
            controls = [c for c in controls if c.domain == domain]

        return controls

    async def assess_control(
        self,
        control_id: str,
        status: str,
        assessor: str,
        evidence: Optional[List[str]] = None,
        notes: Optional[str] = None,
        remediation_required: bool = False,
    ) -> ControlAssessment:
        """Assess control implementation."""
        await asyncio.sleep(0.1)

        if control_id not in self.controls:
            raise ValueError(f"Control {control_id} not found")

        assessment = ControlAssessment(
            assessment_id=str(uuid4()),
            control_id=control_id,
            status=ControlStatus(status),
            assessor=assessor,
            assessment_date=datetime.now(),
            evidence_ids=evidence or [],
            notes=notes,
            remediation_required=remediation_required,
            next_assessment_date=datetime.now() + timedelta(days=365),
        )

        self.assessments[assessment.assessment_id] = assessment

        logger.info(f"Assessed control {control_id}: {status}")
        return assessment

    async def add_evidence(
        self,
        control_id: str,
        evidence_type: str,
        file_path: str,
        description: str,
        collected_by: str,
        valid_days: Optional[int] = None,
    ) -> Evidence:
        """Add evidence for control."""
        await asyncio.sleep(0.05)

        valid_until = None
        if valid_days:
            valid_until = datetime.now() + timedelta(days=valid_days)

        evidence = Evidence(
            evidence_id=str(uuid4()),
            control_id=control_id,
            evidence_type=evidence_type,
            file_path=file_path,
            description=description,
            collected_by=collected_by,
            valid_until=valid_until,
        )

        self.evidence[evidence.evidence_id] = evidence

        logger.info(f"Added evidence for {control_id}: {description}")
        return evidence

    async def get_compliance_score(self, framework: str, scope: str = "all") -> ComplianceScore:
        """Calculate compliance score."""
        await asyncio.sleep(0.2)

        framework_enum = Framework(framework)
        controls = [c for c in self.controls.values() if c.framework == framework_enum]

        # Get latest assessment for each control
        control_status = {}
        for assessment in self.assessments.values():
            if assessment.control_id in [c.control_id for c in controls]:
                if (
                    assessment.control_id not in control_status
                    or assessment.assessment_date > control_status[assessment.control_id].assessment_date
                ):
                    control_status[assessment.control_id] = assessment

        # Count by status
        implemented = sum(1 for a in control_status.values() if a.status == ControlStatus.IMPLEMENTED)
        in_progress = sum(1 for a in control_status.values() if a.status == ControlStatus.IN_PROGRESS)
        not_implemented = sum(1 for a in control_status.values() if a.status == ControlStatus.NOT_IMPLEMENTED)
        not_applicable = sum(1 for a in control_status.values() if a.status == ControlStatus.NOT_APPLICABLE)

        # Calculate score (implemented / (total - not_applicable))
        total = len(controls)
        applicable = total - not_applicable
        score = (implemented / applicable * 100) if applicable > 0 else 0.0

        # Count critical gaps
        critical_gaps = sum(
            1
            for c in controls
            if c.control_id in control_status
            and control_status[c.control_id].status != ControlStatus.IMPLEMENTED
            and c.risk_level == RiskLevel.CRITICAL
        )

        high_gaps = sum(
            1
            for c in controls
            if c.control_id in control_status
            and control_status[c.control_id].status != ControlStatus.IMPLEMENTED
            and c.risk_level == RiskLevel.HIGH
        )

        return ComplianceScore(
            framework=framework_enum,
            scope=scope,
            score=round(score, 2),
            total_controls=total,
            implemented=implemented,
            in_progress=in_progress,
            not_implemented=not_implemented,
            not_applicable=not_applicable,
            critical_gaps=critical_gaps,
            high_gaps=high_gaps,
        )

    async def get_gap_analysis(self, framework: str, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get gap analysis for framework."""
        await asyncio.sleep(0.1)

        framework_enum = Framework(framework)
        controls = [c for c in self.controls.values() if c.framework == framework_enum]

        if risk_level:
            risk_enum = RiskLevel(risk_level)
            controls = [c for c in controls if c.risk_level == risk_enum]

        gaps = []
        for control in controls:
            # Find latest assessment
            assessment = None
            for a in self.assessments.values():
                if a.control_id == control.control_id:
                    if assessment is None or a.assessment_date > assessment.assessment_date:
                        assessment = a

            # Include if not implemented or in progress
            if assessment and assessment.status in [ControlStatus.NOT_IMPLEMENTED, ControlStatus.IN_PROGRESS]:
                gaps.append(
                    {
                        "control_id": control.control_id,
                        "title": control.title,
                        "domain": control.domain,
                        "risk_level": control.risk_level.value,
                        "status": assessment.status.value,
                        "remediation_required": assessment.remediation_required,
                        "remediation_due": (
                            assessment.remediation_due_date.isoformat() if assessment.remediation_due_date else None
                        ),
                    }
                )

        return sorted(gaps, key=lambda x: (x["risk_level"], x["control_id"]))

    async def get_control_mapping(self, control_id: str) -> Dict[str, Any]:
        """Get cross-framework control mapping."""
        await asyncio.sleep(0.05)

        if control_id not in self.controls:
            return {}

        control = self.controls[control_id]

        # Find mapped controls
        mapped = []
        for mapped_id in control.mapped_controls:
            if mapped_id in self.controls:
                mapped_control = self.controls[mapped_id]
                mapped.append(
                    {
                        "control_id": mapped_control.control_id,
                        "framework": mapped_control.framework.value,
                        "title": mapped_control.title,
                    }
                )

        # Find controls that map to this one
        reverse_mapped = []
        for other in self.controls.values():
            if control_id in other.mapped_controls:
                reverse_mapped.append(
                    {"control_id": other.control_id, "framework": other.framework.value, "title": other.title}
                )

        return {
            "control_id": control_id,
            "framework": control.framework.value,
            "title": control.title,
            "maps_to": mapped,
            "mapped_by": reverse_mapped,
        }


# Singleton instance
_compliance_manager: Optional[ComplianceManager] = None


def get_compliance_manager() -> ComplianceManager:
    """Get compliance manager instance."""
    global _compliance_manager
    if _compliance_manager is None:
        _compliance_manager = ComplianceManager()
    return _compliance_manager
