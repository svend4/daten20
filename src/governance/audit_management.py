"""
Audit Management System

Audit planning, finding tracking, remediation workflows, and compliance reporting.

Part of v3.8 Governance & Compliance implementation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class AuditType(Enum):
    """Types of audits."""
    INTERNAL = "internal"
    EXTERNAL = "external"
    REGULATORY = "regulatory"
    CERTIFICATION = "certification"


class Severity(Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class FindingStatus(Enum):
    """Status of audit findings."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ACCEPTED_RISK = "accepted_risk"


class AuditStatus(Enum):
    """Audit lifecycle status."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FIELDWORK = "fieldwork"
    REPORTING = "reporting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class AuditPlan:
    """Audit plan definition."""
    audit_id: str
    title: str
    audit_type: AuditType
    scope: str
    objectives: List[str]
    start_date: datetime
    end_date: datetime
    status: AuditStatus
    auditors: List[str] = field(default_factory=list)
    audit_framework: Optional[str] = None
    risk_areas: List[str] = field(default_factory=list)
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEvidence:
    """Supporting evidence for audit."""
    evidence_id: str
    audit_id: str
    finding_id: Optional[str] = None
    evidence_type: str = "document"
    file_path: str = ""
    description: str = ""
    collected_by: str = ""
    collected_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Remediation:
    """Corrective action for finding."""
    remediation_id: str
    finding_id: str
    action_plan: str
    assigned_to: str
    due_date: datetime
    status: FindingStatus
    priority: Severity
    progress_percentage: int = 0
    completed_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class AuditFinding:
    """Audit finding/observation."""
    finding_id: str
    audit_id: str
    title: str
    severity: Severity
    status: FindingStatus
    description: str
    impact: str
    recommendation: str
    control_reference: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    evidence_ids: List[str] = field(default_factory=list)
    remediation_id: Optional[str] = None
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    closed_date: Optional[datetime] = None


@dataclass
class AuditReport:
    """Audit report summary."""
    report_id: str
    audit_id: str
    executive_summary: str
    findings_summary: Dict[str, int]  # counts by severity
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    recommendations: List[str]
    conclusion: str
    generated_by: str = ""
    generated_date: datetime = field(default_factory=datetime.now)


class AuditPlanning:
    """Audit planning and scheduling."""

    def __init__(self):
        self.audits: Dict[str, AuditPlan] = {}

    async def create_audit_plan(
        self,
        title: str,
        audit_type: str,
        scope: str,
        objectives: List[str],
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> AuditPlan:
        """Create audit plan."""
        await asyncio.sleep(0.05)

        audit = AuditPlan(
            audit_id=str(uuid4()),
            title=title,
            audit_type=AuditType(audit_type),
            scope=scope,
            objectives=objectives,
            start_date=start_date,
            end_date=end_date,
            status=AuditStatus.PLANNED,
            auditors=kwargs.get("auditors", []),
            audit_framework=kwargs.get("audit_framework"),
            risk_areas=kwargs.get("risk_areas", []),
            created_by=kwargs.get("created_by", "")
        )

        self.audits[audit.audit_id] = audit

        logger.info(f"Created audit plan: {title}")
        return audit

    async def update_status(
        self,
        audit_id: str,
        status: str
    ) -> bool:
        """Update audit status."""
        await asyncio.sleep(0.02)

        if audit_id not in self.audits:
            return False

        audit = self.audits[audit_id]
        audit.status = AuditStatus(status)

        logger.info(f"Updated audit {audit_id} status to {status}")
        return True

    async def get_upcoming_audits(
        self,
        days_ahead: int = 90
    ) -> List[AuditPlan]:
        """Get upcoming audits."""
        cutoff = datetime.now() + timedelta(days=days_ahead)

        return [
            audit for audit in self.audits.values()
            if audit.start_date <= cutoff
            and audit.status in [AuditStatus.PLANNED, AuditStatus.IN_PROGRESS]
        ]


class FindingTracker:
    """Track audit findings."""

    def __init__(self):
        self.findings: Dict[str, AuditFinding] = {}

    async def create_finding(
        self,
        audit_id: str,
        title: str,
        severity: str,
        description: str,
        impact: str,
        recommendation: str,
        **kwargs
    ) -> AuditFinding:
        """Create audit finding."""
        await asyncio.sleep(0.05)

        finding = AuditFinding(
            finding_id=str(uuid4()),
            audit_id=audit_id,
            title=title,
            severity=Severity(severity),
            status=FindingStatus.OPEN,
            description=description,
            impact=impact,
            recommendation=recommendation,
            control_reference=kwargs.get("control_reference"),
            category=kwargs.get("category"),
            assigned_to=kwargs.get("assigned_to"),
            due_date=kwargs.get("due_date"),
            created_by=kwargs.get("created_by", "")
        )

        self.findings[finding.finding_id] = finding

        logger.info(f"Created {severity} finding: {title}")
        return finding

    async def update_status(
        self,
        finding_id: str,
        status: str,
        **kwargs
    ) -> bool:
        """Update finding status."""
        await asyncio.sleep(0.02)

        if finding_id not in self.findings:
            return False

        finding = self.findings[finding_id]
        finding.status = FindingStatus(status)

        if status == "closed":
            finding.closed_date = datetime.now()

        logger.info(f"Updated finding {finding_id} to {status}")
        return True

    async def get_findings_by_audit(
        self,
        audit_id: str,
        severity: Optional[str] = None
    ) -> List[AuditFinding]:
        """Get findings for audit."""
        findings = [f for f in self.findings.values() if f.audit_id == audit_id]

        if severity:
            severity_enum = Severity(severity)
            findings = [f for f in findings if f.severity == severity_enum]

        return sorted(findings, key=lambda x: (x.severity.value, x.created_date))

    async def get_open_findings(
        self,
        severity: Optional[str] = None
    ) -> List[AuditFinding]:
        """Get all open findings."""
        findings = [
            f for f in self.findings.values()
            if f.status in [FindingStatus.OPEN, FindingStatus.IN_PROGRESS]
        ]

        if severity:
            severity_enum = Severity(severity)
            findings = [f for f in findings if f.severity == severity_enum]

        return sorted(findings, key=lambda x: (x.severity.value, x.due_date or datetime.max))

    async def get_overdue_findings(self) -> List[AuditFinding]:
        """Get overdue findings."""
        now = datetime.now()

        return [
            f for f in self.findings.values()
            if f.status in [FindingStatus.OPEN, FindingStatus.IN_PROGRESS]
            and f.due_date
            and f.due_date < now
        ]


class RemediationTracker:
    """Track remediation efforts."""

    def __init__(self):
        self.remediations: Dict[str, Remediation] = {}

    async def create_remediation(
        self,
        finding_id: str,
        action_plan: str,
        assigned_to: str,
        due_date: datetime,
        priority: str
    ) -> Remediation:
        """Create remediation plan."""
        await asyncio.sleep(0.05)

        remediation = Remediation(
            remediation_id=str(uuid4()),
            finding_id=finding_id,
            action_plan=action_plan,
            assigned_to=assigned_to,
            due_date=due_date,
            status=FindingStatus.OPEN,
            priority=Severity(priority)
        )

        self.remediations[remediation.remediation_id] = remediation

        logger.info(f"Created remediation for finding {finding_id}")
        return remediation

    async def update_progress(
        self,
        remediation_id: str,
        progress: int,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Update remediation progress."""
        await asyncio.sleep(0.02)

        if remediation_id not in self.remediations:
            return False

        remediation = self.remediations[remediation_id]
        remediation.progress_percentage = min(100, max(0, progress))

        if status:
            remediation.status = FindingStatus(status)

        if notes:
            remediation.notes = notes

        if progress >= 100:
            remediation.status = FindingStatus.RESOLVED
            remediation.completed_date = datetime.now()

        logger.info(f"Updated remediation {remediation_id} to {progress}%")
        return True

    async def verify_remediation(
        self,
        remediation_id: str,
        verified_by: str
    ) -> bool:
        """Verify remediation completion."""
        await asyncio.sleep(0.05)

        if remediation_id not in self.remediations:
            return False

        remediation = self.remediations[remediation_id]
        remediation.verified_by = verified_by
        remediation.verification_date = datetime.now()
        remediation.status = FindingStatus.CLOSED

        logger.info(f"Verified remediation {remediation_id}")
        return True

    async def get_overdue_remediations(self) -> List[Remediation]:
        """Get overdue remediations."""
        now = datetime.now()

        return [
            r for r in self.remediations.values()
            if r.status in [FindingStatus.OPEN, FindingStatus.IN_PROGRESS]
            and r.due_date < now
        ]


class EvidenceManager:
    """Manage audit evidence."""

    def __init__(self):
        self.evidence: Dict[str, AuditEvidence] = {}

    async def add_evidence(
        self,
        audit_id: str,
        evidence_type: str,
        file_path: str,
        description: str,
        collected_by: str,
        finding_id: Optional[str] = None,
        **kwargs
    ) -> AuditEvidence:
        """Add audit evidence."""
        await asyncio.sleep(0.05)

        evidence = AuditEvidence(
            evidence_id=str(uuid4()),
            audit_id=audit_id,
            finding_id=finding_id,
            evidence_type=evidence_type,
            file_path=file_path,
            description=description,
            collected_by=collected_by,
            metadata=kwargs.get("metadata", {})
        )

        self.evidence[evidence.evidence_id] = evidence

        logger.info(f"Added evidence for audit {audit_id}")
        return evidence

    async def get_audit_evidence(
        self,
        audit_id: str
    ) -> List[AuditEvidence]:
        """Get all evidence for audit."""
        return [e for e in self.evidence.values() if e.audit_id == audit_id]

    async def get_finding_evidence(
        self,
        finding_id: str
    ) -> List[AuditEvidence]:
        """Get evidence for specific finding."""
        return [e for e in self.evidence.values() if e.finding_id == finding_id]


class AuditManager:
    """Main audit management system."""

    def __init__(self):
        self.planning = AuditPlanning()
        self.finding_tracker = FindingTracker()
        self.remediation_tracker = RemediationTracker()
        self.evidence_manager = EvidenceManager()
        self.reports: Dict[str, AuditReport] = {}

    async def create_audit_plan(
        self,
        title: str,
        audit_type: str,
        scope: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> AuditPlan:
        """Create audit plan."""
        objectives = kwargs.pop("objectives", ["Assess control effectiveness", "Identify gaps"])
        return await self.planning.create_audit_plan(
            title, audit_type, scope, objectives, start_date, end_date, **kwargs
        )

    async def create_finding(
        self,
        audit_id: str,
        title: str,
        severity: str,
        description: str,
        **kwargs
    ) -> AuditFinding:
        """Create audit finding."""
        impact = kwargs.pop("impact", "Potential control weakness")
        recommendation = kwargs.pop("recommendation", "Implement corrective measures")

        finding = await self.finding_tracker.create_finding(
            audit_id, title, severity, description, impact, recommendation, **kwargs
        )

        # Auto-create remediation if assigned
        if kwargs.get("assigned_to") and kwargs.get("due_date"):
            remediation = await self.remediation_tracker.create_remediation(
                finding_id=finding.finding_id,
                action_plan=recommendation,
                assigned_to=kwargs["assigned_to"],
                due_date=kwargs["due_date"],
                priority=severity
            )
            finding.remediation_id = remediation.remediation_id

        return finding

    async def update_remediation(
        self,
        finding_id: str,
        status: str,
        progress: int = 0,
        notes: Optional[str] = None
    ) -> bool:
        """Update remediation status."""
        # Find remediation for this finding
        for remediation in self.remediation_tracker.remediations.values():
            if remediation.finding_id == finding_id:
                await self.remediation_tracker.update_progress(
                    remediation.remediation_id, progress, status, notes
                )

                # Update finding status
                await self.finding_tracker.update_status(finding_id, status)
                return True

        return False

    async def add_evidence(
        self,
        audit_id: str,
        file_path: str,
        description: str,
        collected_by: str,
        **kwargs
    ) -> AuditEvidence:
        """Add audit evidence."""
        return await self.evidence_manager.add_evidence(
            audit_id, kwargs.get("evidence_type", "document"),
            file_path, description, collected_by, **kwargs
        )

    async def generate_report(
        self,
        audit_id: str,
        executive_summary: str,
        conclusion: str,
        generated_by: str
    ) -> AuditReport:
        """Generate audit report."""
        await asyncio.sleep(0.1)

        # Get all findings for audit
        findings = await self.finding_tracker.get_findings_by_audit(audit_id)

        # Count by severity
        findings_summary = {
            "critical": sum(1 for f in findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
        }

        # Collect recommendations
        recommendations = [f.recommendation for f in findings]

        report = AuditReport(
            report_id=str(uuid4()),
            audit_id=audit_id,
            executive_summary=executive_summary,
            findings_summary=findings_summary,
            total_findings=len(findings),
            critical_findings=findings_summary["critical"],
            high_findings=findings_summary["high"],
            medium_findings=findings_summary["medium"],
            low_findings=findings_summary["low"],
            recommendations=recommendations,
            conclusion=conclusion,
            generated_by=generated_by
        )

        self.reports[report.report_id] = report

        # Mark audit as completed
        await self.planning.update_status(audit_id, "completed")

        logger.info(f"Generated audit report for {audit_id}")
        return report

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get audit dashboard metrics."""
        await asyncio.sleep(0.1)

        open_findings = await self.finding_tracker.get_open_findings()
        overdue_findings = await self.finding_tracker.get_overdue_findings()
        overdue_remediations = await self.remediation_tracker.get_overdue_remediations()
        upcoming_audits = await self.planning.get_upcoming_audits(days_ahead=30)

        return {
            "total_audits": len(self.planning.audits),
            "active_audits": sum(
                1 for a in self.planning.audits.values()
                if a.status in [AuditStatus.IN_PROGRESS, AuditStatus.FIELDWORK]
            ),
            "upcoming_audits": len(upcoming_audits),
            "total_findings": len(self.finding_tracker.findings),
            "open_findings": len(open_findings),
            "critical_open": sum(1 for f in open_findings if f.severity == Severity.CRITICAL),
            "high_open": sum(1 for f in open_findings if f.severity == Severity.HIGH),
            "overdue_findings": len(overdue_findings),
            "overdue_remediations": len(overdue_remediations),
            "total_evidence": len(self.evidence_manager.evidence),
            "generated_at": datetime.now().isoformat()
        }


# Singleton instance
_audit_manager: Optional[AuditManager] = None


def get_audit_manager() -> AuditManager:
    """Get audit manager instance."""
    global _audit_manager
    if _audit_manager is None:
        _audit_manager = AuditManager()
    return _audit_manager
