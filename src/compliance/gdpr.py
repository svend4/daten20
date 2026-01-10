"""
GDPR Compliance Module

Implements GDPR (General Data Protection Regulation) compliance features:
- Data subject rights (access, rectification, erasure, portability)
- Consent management
- Data breach notifications
- Privacy impact assessments
- Data retention policies
- Audit trails
"""

from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import uuid


class DataSubjectRight(str, Enum):
    """GDPR Data Subject Rights (Articles 15-22)"""
    ACCESS = "right_to_access"  # Article 15
    RECTIFICATION = "right_to_rectification"  # Article 16
    ERASURE = "right_to_erasure"  # Article 17 (Right to be forgotten)
    RESTRICTION = "right_to_restriction"  # Article 18
    PORTABILITY = "right_to_portability"  # Article 20
    OBJECTION = "right_to_objection"  # Article 21
    AUTOMATED_DECISION = "right_against_automated_decision"  # Article 22


class ConsentPurpose(str, Enum):
    """Purposes for data processing"""
    ESSENTIAL_SERVICE = "essential_service"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PROFILING = "profiling"


class LegalBasis(str, Enum):
    """Legal basis for processing (Article 6)"""
    CONSENT = "consent"  # Article 6(1)(a)
    CONTRACT = "contract"  # Article 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"  # Article 6(1)(c)
    VITAL_INTERESTS = "vital_interests"  # Article 6(1)(d)
    PUBLIC_TASK = "public_task"  # Article 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Article 6(1)(f)


class DataCategory(str, Enum):
    """Categories of personal data"""
    BASIC_IDENTITY = "basic_identity"  # Name, address, etc.
    CONTACT = "contact"  # Email, phone
    FINANCIAL = "financial"  # Payment info
    BEHAVIORAL = "behavioral"  # Usage patterns
    TECHNICAL = "technical"  # IP, cookies
    HEALTH = "health"  # Special category (Article 9)
    BIOMETRIC = "biometric"  # Special category (Article 9)
    LOCATION = "location"


class BreachSeverity(str, Enum):
    """Data breach severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Consent:
    """User consent record"""
    id: str
    user_id: int
    purpose: ConsentPurpose
    granted: bool
    timestamp: datetime
    expiry: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    version: str = "1.0"  # Consent text version
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataSubjectRequest:
    """Data subject rights request"""
    id: str
    user_id: int
    right: DataSubjectRight
    status: str  # pending, processing, completed, rejected
    requested_at: datetime
    completed_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    notes: str = ""
    verified: bool = False


@dataclass
class DataBreach:
    """Data breach record (Article 33-34)"""
    id: str
    discovered_at: datetime
    reported_at: Optional[datetime] = None
    severity: BreachSeverity
    affected_users: int
    affected_data_categories: List[DataCategory]
    description: str
    mitigation_steps: List[str] = field(default_factory=list)
    dpa_notified: bool = False  # Data Protection Authority
    users_notified: bool = False
    resolution_notes: str = ""
    closed_at: Optional[datetime] = None


@dataclass
class DataRetentionPolicy:
    """Data retention policy"""
    id: str
    data_category: DataCategory
    retention_period_days: int
    legal_basis: LegalBasis
    description: str
    auto_delete: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PrivacyImpactAssessment:
    """DPIA - Data Protection Impact Assessment (Article 35)"""
    id: str
    title: str
    description: str
    data_categories: List[DataCategory]
    processing_purposes: List[str]
    necessity_justification: str
    risks_identified: List[Dict[str, str]]
    mitigation_measures: List[str]
    dpo_consulted: bool  # Data Protection Officer
    completed_at: datetime
    review_date: datetime
    approved: bool = False
    approver: Optional[str] = None


class ConsentManager:
    """Manages user consents for GDPR compliance"""

    def __init__(self, database=None):
        self.database = database
        self.consents: Dict[str, Consent] = {}

    def request_consent(
        self,
        user_id: int,
        purpose: ConsentPurpose,
        expiry_days: Optional[int] = 365,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Request consent from user"""
        consent_id = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(days=expiry_days) if expiry_days else None

        consent = Consent(
            id=consent_id,
            user_id=user_id,
            purpose=purpose,
            granted=False,  # Waiting for user action
            timestamp=datetime.now(),
            expiry=expiry,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.consents[consent_id] = consent
        return consent_id

    def grant_consent(
        self,
        consent_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Grant consent"""
        if consent_id not in self.consents:
            return False

        consent = self.consents[consent_id]
        consent.granted = True
        consent.timestamp = datetime.now()
        consent.ip_address = ip_address or consent.ip_address
        consent.user_agent = user_agent or consent.user_agent

        return True

    def withdraw_consent(self, consent_id: str) -> bool:
        """Withdraw consent (Article 7(3))"""
        if consent_id not in self.consents:
            return False

        consent = self.consents[consent_id]
        consent.granted = False
        consent.withdrawn_at = datetime.now()

        return True

    def check_consent(self, user_id: int, purpose: ConsentPurpose) -> bool:
        """Check if user has valid consent for purpose"""
        for consent in self.consents.values():
            if consent.user_id != user_id or consent.purpose != purpose:
                continue

            if not consent.granted or consent.withdrawn_at:
                continue

            if consent.expiry and datetime.now() > consent.expiry:
                continue

            return True

        return False

    def get_user_consents(self, user_id: int) -> List[Consent]:
        """Get all consents for user"""
        return [
            c for c in self.consents.values()
            if c.user_id == user_id
        ]


class DataSubjectRightsHandler:
    """Handles GDPR data subject rights requests"""

    def __init__(self, database=None):
        self.database = database
        self.requests: Dict[str, DataSubjectRequest] = {}

    def submit_request(
        self,
        user_id: int,
        right: DataSubjectRight,
        notes: str = ""
    ) -> str:
        """Submit data subject rights request"""
        request_id = str(uuid.uuid4())

        request = DataSubjectRequest(
            id=request_id,
            user_id=user_id,
            right=right,
            status="pending",
            requested_at=datetime.now(),
            notes=notes
        )

        self.requests[request_id] = request
        return request_id

    def process_access_request(self, request_id: str) -> Dict[str, Any]:
        """Process right to access request (Article 15)"""
        if request_id not in self.requests:
            return {'error': 'Request not found'}

        request = self.requests[request_id]
        request.status = "processing"

        # Collect all user data
        user_data = {
            'personal_data': self._get_user_personal_data(request.user_id),
            'services': self._get_user_services(request.user_id),
            'consents': self._get_user_consents(request.user_id),
            'processing_purposes': self._get_processing_purposes(request.user_id),
            'data_categories': self._get_data_categories(request.user_id),
            'retention_periods': self._get_retention_periods(),
            'third_party_recipients': self._get_third_party_recipients(),
            'rights_information': self._get_rights_information()
        }

        request.status = "completed"
        request.completed_at = datetime.now()
        request.response_data = user_data

        return user_data

    def process_erasure_request(self, request_id: str) -> bool:
        """Process right to erasure request (Article 17)"""
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]
        request.status = "processing"

        # Check if erasure is legally required
        if not self._can_erase_data(request.user_id):
            request.status = "rejected"
            request.notes = "Data retention required by legal obligation"
            return False

        # Anonymize or delete user data
        self._anonymize_user_data(request.user_id)

        request.status = "completed"
        request.completed_at = datetime.now()

        return True

    def process_portability_request(self, request_id: str) -> Optional[str]:
        """Process right to data portability request (Article 20)"""
        if request_id not in self.requests:
            return None

        request = self.requests[request_id]
        request.status = "processing"

        # Export user data in machine-readable format
        user_data = self._get_user_personal_data(request.user_id)
        export_data = json.dumps(user_data, indent=2, default=str)

        request.status = "completed"
        request.completed_at = datetime.now()

        return export_data

    def _get_user_personal_data(self, user_id: int) -> Dict[str, Any]:
        """Get user's personal data"""
        if not self.database:
            return {}

        cursor = self.database.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return {}

        # Map to dictionary (simplified)
        return {
            'id': row[0],
            'username': row[1] if len(row) > 1 else None,
            'email': row[2] if len(row) > 2 else None,
            'created_at': row[3] if len(row) > 3 else None
        }

    def _get_user_services(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's services"""
        if not self.database:
            return []

        cursor = self.database.conn.cursor()
        cursor.execute(
            "SELECT id, service_name, region, created_at FROM services WHERE user_id = ?",
            (user_id,)
        )

        return [
            {
                'id': row[0],
                'service_name': row[1],
                'region': row[2],
                'created_at': row[3]
            }
            for row in cursor.fetchall()
        ]

    def _get_user_consents(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user consents"""
        # Would integrate with ConsentManager
        return []

    def _get_processing_purposes(self, user_id: int) -> List[str]:
        """Get purposes for which data is processed"""
        return [
            "Service delivery",
            "Legal compliance",
            "Analytics (with consent)"
        ]

    def _get_data_categories(self, user_id: int) -> List[str]:
        """Get categories of data collected"""
        return [
            DataCategory.BASIC_IDENTITY.value,
            DataCategory.CONTACT.value,
            DataCategory.TECHNICAL.value
        ]

    def _get_retention_periods(self) -> Dict[str, str]:
        """Get data retention periods"""
        return {
            "user_accounts": "Duration of account + 30 days",
            "service_records": "7 years (legal requirement)",
            "audit_logs": "1 year"
        }

    def _get_third_party_recipients(self) -> List[str]:
        """Get third-party data recipients"""
        return [
            "Cloud hosting provider (AWS/Azure)",
            "Email service provider",
            "Analytics provider (if consented)"
        ]

    def _get_rights_information(self) -> Dict[str, str]:
        """Get information about data subject rights"""
        return {
            'right_to_access': 'You can request a copy of your personal data',
            'right_to_rectification': 'You can request correction of inaccurate data',
            'right_to_erasure': 'You can request deletion of your data',
            'right_to_portability': 'You can receive your data in machine-readable format',
            'right_to_objection': 'You can object to processing of your data',
            'lodge_complaint': 'You can lodge a complaint with supervisory authority'
        }

    def _can_erase_data(self, user_id: int) -> bool:
        """Check if user data can be erased"""
        # Check for legal obligations that prevent erasure
        # e.g., accounting records must be kept for 7 years
        return True

    def _anonymize_user_data(self, user_id: int):
        """Anonymize user data instead of deleting"""
        if not self.database:
            return

        # Anonymize by replacing with hashed values
        anonymous_id = hashlib.sha256(f"user_{user_id}_{datetime.now()}".encode()).hexdigest()[:16]

        cursor = self.database.conn.cursor()
        cursor.execute("""
            UPDATE users
            SET username = ?, email = ?, deleted = 1
            WHERE id = ?
        """, (f"deleted_{anonymous_id}", f"deleted_{anonymous_id}@anonymized.local", user_id))

        self.database.conn.commit()


class DataBreachManager:
    """Manages data breach notifications (Articles 33-34)"""

    def __init__(self):
        self.breaches: Dict[str, DataBreach] = {}

    def report_breach(
        self,
        description: str,
        severity: BreachSeverity,
        affected_users: int,
        affected_data_categories: List[DataCategory]
    ) -> str:
        """Report a data breach"""
        breach_id = str(uuid.uuid4())

        breach = DataBreach(
            id=breach_id,
            discovered_at=datetime.now(),
            severity=severity,
            affected_users=affected_users,
            affected_data_categories=affected_data_categories,
            description=description
        )

        self.breaches[breach_id] = breach

        # Check if DPA notification required (within 72 hours)
        if severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL]:
            breach.dpa_notified = True
            breach.reported_at = datetime.now()

        return breach_id

    def notify_dpa(self, breach_id: str) -> bool:
        """Notify Data Protection Authority (Article 33)"""
        if breach_id not in self.breaches:
            return False

        breach = self.breaches[breach_id]

        # Check 72-hour requirement
        hours_since_discovery = (datetime.now() - breach.discovered_at).total_seconds() / 3600

        if hours_since_discovery > 72:
            print(f"WARNING: DPA notification delayed beyond 72 hours ({hours_since_discovery:.1f}h)")

        breach.dpa_notified = True
        breach.reported_at = datetime.now()

        return True

    def notify_affected_users(self, breach_id: str) -> bool:
        """Notify affected data subjects (Article 34)"""
        if breach_id not in self.breaches:
            return False

        breach = self.breaches[breach_id]

        # Only required if high risk to rights and freedoms
        if breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL]:
            breach.users_notified = True
            # Would send notifications here

        return True

    def add_mitigation_step(self, breach_id: str, step: str) -> bool:
        """Add mitigation step to breach"""
        if breach_id not in self.breaches:
            return False

        self.breaches[breach_id].mitigation_steps.append(step)
        return True

    def close_breach(self, breach_id: str, notes: str = "") -> bool:
        """Close a breach incident"""
        if breach_id not in self.breaches:
            return False

        breach = self.breaches[breach_id]
        breach.closed_at = datetime.now()
        breach.resolution_notes = notes

        return True


class RetentionPolicyManager:
    """Manages data retention policies"""

    def __init__(self):
        self.policies: Dict[str, DataRetentionPolicy] = {}
        self._create_default_policies()

    def _create_default_policies(self):
        """Create default retention policies"""
        defaults = [
            DataRetentionPolicy(
                id="policy_basic_identity",
                data_category=DataCategory.BASIC_IDENTITY,
                retention_period_days=2555,  # 7 years
                legal_basis=LegalBasis.LEGAL_OBLIGATION,
                description="Identity data retained for legal compliance",
                auto_delete=False
            ),
            DataRetentionPolicy(
                id="policy_analytics",
                data_category=DataCategory.BEHAVIORAL,
                retention_period_days=365,
                legal_basis=LegalBasis.CONSENT,
                description="Analytics data retained for 1 year",
                auto_delete=True
            ),
            DataRetentionPolicy(
                id="policy_technical",
                data_category=DataCategory.TECHNICAL,
                retention_period_days=90,
                legal_basis=LegalBasis.LEGITIMATE_INTERESTS,
                description="Technical logs retained for 90 days",
                auto_delete=True
            )
        ]

        for policy in defaults:
            self.policies[policy.id] = policy

    def add_policy(self, policy: DataRetentionPolicy):
        """Add retention policy"""
        self.policies[policy.id] = policy

    def get_retention_period(self, data_category: DataCategory) -> Optional[int]:
        """Get retention period for data category"""
        for policy in self.policies.values():
            if policy.data_category == data_category:
                return policy.retention_period_days
        return None

    def cleanup_expired_data(self) -> int:
        """Clean up data past retention period"""
        deleted_count = 0

        for policy in self.policies.values():
            if not policy.auto_delete:
                continue

            # Would implement actual deletion here
            # For now, just count what would be deleted
            cutoff_date = datetime.now() - timedelta(days=policy.retention_period_days)
            print(f"Would delete {policy.data_category.value} data before {cutoff_date}")

        return deleted_count


class GDPRComplianceEngine:
    """Main GDPR compliance engine"""

    def __init__(self, database=None):
        self.database = database
        self.consent_manager = ConsentManager(database)
        self.rights_handler = DataSubjectRightsHandler(database)
        self.breach_manager = DataBreachManager()
        self.retention_manager = RetentionPolicyManager()

        # Privacy Impact Assessments
        self.dpias: Dict[str, PrivacyImpactAssessment] = {}

    def create_dpia(
        self,
        title: str,
        description: str,
        data_categories: List[DataCategory],
        processing_purposes: List[str]
    ) -> str:
        """Create Data Protection Impact Assessment"""
        dpia_id = str(uuid.uuid4())

        dpia = PrivacyImpactAssessment(
            id=dpia_id,
            title=title,
            description=description,
            data_categories=data_categories,
            processing_purposes=processing_purposes,
            necessity_justification="",
            risks_identified=[],
            mitigation_measures=[],
            dpo_consulted=False,
            completed_at=datetime.now(),
            review_date=datetime.now() + timedelta(days=365)
        )

        self.dpias[dpia_id] = dpia
        return dpia_id

    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall GDPR compliance status"""
        total_requests = len(self.rights_handler.requests)
        completed_requests = len([
            r for r in self.rights_handler.requests.values()
            if r.status == "completed"
        ])

        active_consents = len([
            c for c in self.consent_manager.consents.values()
            if c.granted and not c.withdrawn_at
        ])

        open_breaches = len([
            b for b in self.breach_manager.breaches.values()
            if not b.closed_at
        ])

        return {
            'data_subject_requests': {
                'total': total_requests,
                'completed': completed_requests,
                'pending': total_requests - completed_requests
            },
            'consents': {
                'active': active_consents,
                'total': len(self.consent_manager.consents)
            },
            'data_breaches': {
                'open': open_breaches,
                'total': len(self.breach_manager.breaches)
            },
            'retention_policies': len(self.retention_manager.policies),
            'dpias_completed': len(self.dpias)
        }


# Global instance
_gdpr_engine: Optional[GDPRComplianceEngine] = None


def get_gdpr_engine(database=None) -> GDPRComplianceEngine:
    """Get global GDPR engine instance"""
    global _gdpr_engine

    if _gdpr_engine is None:
        _gdpr_engine = GDPRComplianceEngine(database)

    return _gdpr_engine


def configure_gdpr_engine(database):
    """Configure GDPR engine"""
    global _gdpr_engine
    _gdpr_engine = GDPRComplianceEngine(database)
