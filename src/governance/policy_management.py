"""
Policy Management System

Policy lifecycle, version control, distribution, acknowledgment tracking,
and attestation workflows.

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


class PolicyStatus(Enum):
    """Policy status."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PolicyCategory(Enum):
    """Policy categories."""

    INFORMATION_SECURITY = "information_security"
    DATA_PRIVACY = "data_privacy"
    HR = "hr"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    LEGAL = "legal"


class AcknowledgmentStatus(Enum):
    """Acknowledgment status."""

    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    OVERDUE = "overdue"
    EXEMPTED = "exempted"


@dataclass
class PolicyVersion:
    """Policy version."""

    version_id: str
    policy_id: str
    version_number: str
    content: str
    changes_summary: Optional[str] = None
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None


@dataclass
class Policy:
    """Policy document."""

    policy_id: str
    title: str
    category: PolicyCategory
    status: PolicyStatus
    current_version_id: str
    owner: str
    effective_date: datetime
    review_frequency: timedelta
    next_review_date: datetime
    requires_acknowledgment: bool = True
    requires_attestation: bool = False
    applies_to: List[str] = field(default_factory=list)  # user groups/roles
    tags: Set[str] = field(default_factory=set)
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Acknowledgment:
    """User policy acknowledgment."""

    acknowledgment_id: str
    policy_id: str
    version_id: str
    user_id: str
    user_email: str
    status: AcknowledgmentStatus
    distributed_date: datetime
    due_date: datetime
    acknowledged_date: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class Attestation:
    """Compliance attestation."""

    attestation_id: str
    policy_id: str
    user_id: str
    user_email: str
    attestation_text: str
    attested: bool = False
    attested_date: Optional[datetime] = None
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Distribution:
    """Policy distribution campaign."""

    distribution_id: str
    policy_id: str
    version_id: str
    recipients: List[str]  # user_ids or group names
    distribution_date: datetime
    due_date: datetime
    message: Optional[str] = None
    total_recipients: int = 0
    acknowledged_count: int = 0
    pending_count: int = 0
    overdue_count: int = 0
    distributed_by: str = ""


class VersionControl:
    """Policy version control."""

    def __init__(self):
        self.versions: Dict[str, PolicyVersion] = {}

    async def create_version(
        self, policy_id: str, version_number: str, content: str, created_by: str, changes_summary: Optional[str] = None
    ) -> PolicyVersion:
        """Create new policy version."""
        await asyncio.sleep(0.05)

        version = PolicyVersion(
            version_id=str(uuid4()),
            policy_id=policy_id,
            version_number=version_number,
            content=content,
            changes_summary=changes_summary,
            created_by=created_by,
        )

        self.versions[version.version_id] = version

        logger.info(f"Created policy version {version_number} for {policy_id}")
        return version

    async def approve_version(self, version_id: str, approved_by: str) -> bool:
        """Approve policy version."""
        await asyncio.sleep(0.02)

        if version_id not in self.versions:
            return False

        version = self.versions[version_id]
        version.approved_by = approved_by
        version.approved_date = datetime.now()

        logger.info(f"Approved version {version_id}")
        return True

    async def get_policy_versions(self, policy_id: str) -> List[PolicyVersion]:
        """Get all versions of policy."""
        versions = [v for v in self.versions.values() if v.policy_id == policy_id]
        return sorted(versions, key=lambda x: x.created_date, reverse=True)


class AcknowledgmentTracker:
    """Track policy acknowledgments."""

    def __init__(self):
        self.acknowledgments: Dict[str, Acknowledgment] = {}

    async def create_acknowledgment(
        self, policy_id: str, version_id: str, user_id: str, user_email: str, due_date: datetime
    ) -> Acknowledgment:
        """Create acknowledgment requirement."""
        await asyncio.sleep(0.02)

        ack = Acknowledgment(
            acknowledgment_id=str(uuid4()),
            policy_id=policy_id,
            version_id=version_id,
            user_id=user_id,
            user_email=user_email,
            status=AcknowledgmentStatus.PENDING,
            distributed_date=datetime.now(),
            due_date=due_date,
        )

        self.acknowledgments[ack.acknowledgment_id] = ack

        logger.info(f"Created acknowledgment for {user_email}")
        return ack

    async def record_acknowledgment(
        self, acknowledgment_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> bool:
        """Record user acknowledgment."""
        await asyncio.sleep(0.02)

        if acknowledgment_id not in self.acknowledgments:
            return False

        ack = self.acknowledgments[acknowledgment_id]
        ack.status = AcknowledgmentStatus.ACKNOWLEDGED
        ack.acknowledged_date = datetime.now()
        ack.ip_address = ip_address
        ack.user_agent = user_agent

        logger.info(f"Recorded acknowledgment from {ack.user_email}")
        return True

    async def get_policy_acknowledgments(self, policy_id: str, status: Optional[str] = None) -> List[Acknowledgment]:
        """Get acknowledgments for policy."""
        acks = [a for a in self.acknowledgments.values() if a.policy_id == policy_id]

        if status:
            status_enum = AcknowledgmentStatus(status)
            acks = [a for a in acks if a.status == status_enum]

        return acks

    async def get_overdue_acknowledgments(self) -> List[Acknowledgment]:
        """Get overdue acknowledgments."""
        now = datetime.now()

        overdue = [
            a for a in self.acknowledgments.values() if a.status == AcknowledgmentStatus.PENDING and a.due_date < now
        ]

        # Update status
        for ack in overdue:
            ack.status = AcknowledgmentStatus.OVERDUE

        return overdue

    async def get_user_pending_acknowledgments(self, user_id: str) -> List[Acknowledgment]:
        """Get pending acknowledgments for user."""
        return [
            a
            for a in self.acknowledgments.values()
            if a.user_id == user_id and a.status == AcknowledgmentStatus.PENDING
        ]


class AttestationManager:
    """Manage compliance attestations."""

    def __init__(self):
        self.attestations: Dict[str, Attestation] = {}

    async def create_attestation(
        self, policy_id: str, user_id: str, user_email: str, attestation_text: str, **kwargs
    ) -> Attestation:
        """Create attestation requirement."""
        await asyncio.sleep(0.02)

        attestation = Attestation(
            attestation_id=str(uuid4()),
            policy_id=policy_id,
            user_id=user_id,
            user_email=user_email,
            attestation_text=attestation_text,
            **kwargs,
        )

        self.attestations[attestation.attestation_id] = attestation

        logger.info(f"Created attestation for {user_email}")
        return attestation

    async def record_attestation(self, attestation_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record attestation."""
        await asyncio.sleep(0.02)

        if attestation_id not in self.attestations:
            return False

        attestation = self.attestations[attestation_id]
        attestation.attested = True
        attestation.attested_date = datetime.now()

        if metadata:
            attestation.metadata.update(metadata)

        logger.info(f"Recorded attestation from {attestation.user_email}")
        return True

    async def get_pending_attestations(self, user_id: Optional[str] = None) -> List[Attestation]:
        """Get pending attestations."""
        attestations = [a for a in self.attestations.values() if not a.attested]

        if user_id:
            attestations = [a for a in attestations if a.user_id == user_id]

        return attestations


class PolicyManager:
    """Main policy management system."""

    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.version_control = VersionControl()
        self.acknowledgment_tracker = AcknowledgmentTracker()
        self.attestation_manager = AttestationManager()
        self.distributions: Dict[str, Distribution] = {}

    async def create_policy(
        self,
        title: str,
        category: str,
        content: str,
        owner: str,
        effective_date: datetime,
        review_frequency: timedelta,
        **kwargs,
    ) -> Policy:
        """Create new policy."""
        await asyncio.sleep(0.05)

        policy_id = str(uuid4())

        # Create initial version
        version = await self.version_control.create_version(
            policy_id=policy_id, version_number="1.0", content=content, created_by=kwargs.get("created_by", owner)
        )

        # Create policy
        policy = Policy(
            policy_id=policy_id,
            title=title,
            category=PolicyCategory(category),
            status=PolicyStatus.DRAFT,
            current_version_id=version.version_id,
            owner=owner,
            effective_date=effective_date,
            review_frequency=review_frequency,
            next_review_date=effective_date + review_frequency,
            requires_acknowledgment=kwargs.get("requires_acknowledgment", True),
            requires_attestation=kwargs.get("requires_attestation", False),
            applies_to=kwargs.get("applies_to", ["all_employees"]),
            tags=set(kwargs.get("tags", [])),
            created_by=kwargs.get("created_by", owner),
        )

        self.policies[policy_id] = policy

        logger.info(f"Created policy: {title}")
        return policy

    async def update_policy(
        self, policy_id: str, content: str, updated_by: str, changes_summary: str, version_number: str = "1.1"
    ) -> PolicyVersion:
        """Update policy with new version."""
        await asyncio.sleep(0.05)

        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self.policies[policy_id]

        # Create new version
        version = await self.version_control.create_version(
            policy_id=policy_id,
            version_number=version_number,
            content=content,
            created_by=updated_by,
            changes_summary=changes_summary,
        )

        # Update policy
        policy.current_version_id = version.version_id
        policy.status = PolicyStatus.REVIEW

        logger.info(f"Updated policy {policy_id} to version {version_number}")
        return version

    async def approve_policy(self, policy_id: str, approved_by: str) -> bool:
        """Approve policy."""
        await asyncio.sleep(0.02)

        if policy_id not in self.policies:
            return False

        policy = self.policies[policy_id]
        policy.status = PolicyStatus.APPROVED

        # Approve current version
        await self.version_control.approve_version(policy.current_version_id, approved_by)

        logger.info(f"Approved policy {policy_id}")
        return True

    async def publish_policy(self, policy_id: str) -> bool:
        """Publish policy."""
        await asyncio.sleep(0.02)

        if policy_id not in self.policies:
            return False

        policy = self.policies[policy_id]

        if policy.status != PolicyStatus.APPROVED:
            logger.warning(f"Cannot publish unapproved policy {policy_id}")
            return False

        policy.status = PolicyStatus.PUBLISHED

        logger.info(f"Published policy {policy_id}")
        return True

    async def distribute_policy(
        self, policy_id: str, recipients: List[str], due_date: datetime, **kwargs
    ) -> Distribution:
        """Distribute policy to users."""
        await asyncio.sleep(0.1)

        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self.policies[policy_id]

        distribution = Distribution(
            distribution_id=str(uuid4()),
            policy_id=policy_id,
            version_id=policy.current_version_id,
            recipients=recipients,
            distribution_date=datetime.now(),
            due_date=due_date,
            message=kwargs.get("message"),
            total_recipients=len(recipients),
            distributed_by=kwargs.get("distributed_by", "system"),
        )

        self.distributions[distribution.distribution_id] = distribution

        # Create acknowledgments if required
        if policy.requires_acknowledgment:
            for recipient in recipients:
                await self.acknowledgment_tracker.create_acknowledgment(
                    policy_id=policy_id,
                    version_id=policy.current_version_id,
                    user_id=recipient,
                    user_email=f"{recipient}@company.com",
                    due_date=due_date,
                )

        logger.info(f"Distributed policy {policy_id} to {len(recipients)} recipients")
        return distribution

    async def acknowledge_policy(self, policy_id: str, user_id: str, **kwargs) -> bool:
        """Record user acknowledgment."""
        # Find acknowledgment for this user/policy
        for ack in self.acknowledgment_tracker.acknowledgments.values():
            if ack.policy_id == policy_id and ack.user_id == user_id and ack.status == AcknowledgmentStatus.PENDING:
                return await self.acknowledgment_tracker.record_acknowledgment(
                    ack.acknowledgment_id, ip_address=kwargs.get("ip_address"), user_agent=kwargs.get("user_agent")
                )

        return False

    async def get_acknowledgment_status(self, policy_id: str) -> Dict[str, Any]:
        """Get acknowledgment status for policy."""
        await asyncio.sleep(0.05)

        acks = await self.acknowledgment_tracker.get_policy_acknowledgments(policy_id)

        total = len(acks)
        acknowledged = sum(1 for a in acks if a.status == AcknowledgmentStatus.ACKNOWLEDGED)
        pending = sum(1 for a in acks if a.status == AcknowledgmentStatus.PENDING)
        overdue = sum(1 for a in acks if a.status == AcknowledgmentStatus.OVERDUE)

        return {
            "policy_id": policy_id,
            "total": total,
            "acknowledged": acknowledged,
            "pending": pending,
            "overdue": overdue,
            "rate": (acknowledged / total * 100) if total > 0 else 100.0,
        }

    async def get_policies_due_for_review(self, days_ahead: int = 90) -> List[Policy]:
        """Get policies due for review."""
        cutoff = datetime.now() + timedelta(days=days_ahead)

        return [
            p for p in self.policies.values() if p.next_review_date <= cutoff and p.status == PolicyStatus.PUBLISHED
        ]

    async def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        await asyncio.sleep(0.1)

        total_policies = len(self.policies)
        published = sum(1 for p in self.policies.values() if p.status == PolicyStatus.PUBLISHED)
        due_for_review = len(await self.get_policies_due_for_review(days_ahead=30))
        overdue_acks = len(await self.acknowledgment_tracker.get_overdue_acknowledgments())

        return {
            "total_policies": total_policies,
            "published_policies": published,
            "draft_policies": sum(1 for p in self.policies.values() if p.status == PolicyStatus.DRAFT),
            "policies_due_for_review": due_for_review,
            "total_acknowledgments": len(self.acknowledgment_tracker.acknowledgments),
            "overdue_acknowledgments": overdue_acks,
            "total_distributions": len(self.distributions),
            "generated_at": datetime.now().isoformat(),
        }


# Singleton instance
_policy_manager: Optional[PolicyManager] = None


def get_policy_manager() -> PolicyManager:
    """Get policy manager instance."""
    global _policy_manager
    if _policy_manager is None:
        _policy_manager = PolicyManager()
    return _policy_manager
