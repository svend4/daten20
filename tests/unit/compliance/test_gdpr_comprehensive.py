"""
Comprehensive GDPR Compliance Tests

Tests for GDPR (General Data Protection Regulation) compliance module.
Covers all enums, dataclasses, and classes with Small/Medium/Large test sizes.
"""

import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.compliance.gdpr import (
    BreachSeverity,
    Consent,
    ConsentManager,
    ConsentPurpose,
    DataBreach,
    DataBreachManager,
    DataCategory,
    DataRetentionPolicy,
    DataSubjectRequest,
    DataSubjectRight,
    DataSubjectRightsHandler,
    GDPRComplianceEngine,
    LegalBasis,
    PrivacyImpactAssessment,
    RetentionPolicyManager,
    configure_gdpr_engine,
    get_gdpr_engine,
)


# =============================================================================
# SMALL TESTS - Enums and Dataclasses
# =============================================================================


@pytest.mark.small
class TestEnums:
    """Test GDPR enum values"""

    def test_data_subject_right_enum(self):
        """Test DataSubjectRight enum has all required rights"""
        assert DataSubjectRight.ACCESS == "right_to_access"
        assert DataSubjectRight.RECTIFICATION == "right_to_rectification"
        assert DataSubjectRight.ERASURE == "right_to_erasure"
        assert DataSubjectRight.RESTRICTION == "right_to_restriction"
        assert DataSubjectRight.PORTABILITY == "right_to_portability"
        assert DataSubjectRight.OBJECTION == "right_to_objection"
        assert DataSubjectRight.AUTOMATED_DECISION == "right_against_automated_decision"

    def test_consent_purpose_enum(self):
        """Test ConsentPurpose enum values"""
        assert ConsentPurpose.ESSENTIAL_SERVICE == "essential_service"
        assert ConsentPurpose.MARKETING == "marketing"
        assert ConsentPurpose.ANALYTICS == "analytics"
        assert ConsentPurpose.PERSONALIZATION == "personalization"
        assert ConsentPurpose.THIRD_PARTY_SHARING == "third_party_sharing"
        assert ConsentPurpose.PROFILING == "profiling"

    def test_legal_basis_enum(self):
        """Test LegalBasis enum (Article 6 GDPR)"""
        assert LegalBasis.CONSENT == "consent"
        assert LegalBasis.CONTRACT == "contract"
        assert LegalBasis.LEGAL_OBLIGATION == "legal_obligation"
        assert LegalBasis.VITAL_INTERESTS == "vital_interests"
        assert LegalBasis.PUBLIC_TASK == "public_task"
        assert LegalBasis.LEGITIMATE_INTERESTS == "legitimate_interests"

    def test_data_category_enum(self):
        """Test DataCategory enum values"""
        assert DataCategory.BASIC_IDENTITY == "basic_identity"
        assert DataCategory.CONTACT == "contact"
        assert DataCategory.FINANCIAL == "financial"
        assert DataCategory.BEHAVIORAL == "behavioral"
        assert DataCategory.TECHNICAL == "technical"
        assert DataCategory.HEALTH == "health"
        assert DataCategory.BIOMETRIC == "biometric"
        assert DataCategory.LOCATION == "location"

    def test_breach_severity_enum(self):
        """Test BreachSeverity enum values"""
        assert BreachSeverity.LOW == "low"
        assert BreachSeverity.MEDIUM == "medium"
        assert BreachSeverity.HIGH == "high"
        assert BreachSeverity.CRITICAL == "critical"


@pytest.mark.small
class TestDataclasses:
    """Test GDPR dataclass creation"""

    def test_consent_dataclass(self):
        """Test Consent dataclass creation"""
        consent = Consent(
            id="consent_123",
            user_id=1,
            purpose=ConsentPurpose.MARKETING,
            granted=True,
            timestamp=datetime.now(),
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert consent.id == "consent_123"
        assert consent.user_id == 1
        assert consent.purpose == ConsentPurpose.MARKETING
        assert consent.granted is True
        assert consent.ip_address == "192.168.1.1"
        assert consent.version == "1.0"

    def test_data_subject_request_dataclass(self):
        """Test DataSubjectRequest dataclass"""
        request = DataSubjectRequest(
            id="req_123",
            user_id=1,
            right=DataSubjectRight.ACCESS,
            status="pending",
            requested_at=datetime.now(),
            notes="User requests all data",
        )

        assert request.id == "req_123"
        assert request.right == DataSubjectRight.ACCESS
        assert request.status == "pending"
        assert request.verified is False

    def test_data_breach_dataclass(self):
        """Test DataBreach dataclass"""
        breach = DataBreach(
            id="breach_123",
            discovered_at=datetime.now(),
            severity=BreachSeverity.HIGH,
            affected_users=1000,
            affected_data_categories=[DataCategory.CONTACT, DataCategory.FINANCIAL],
            description="Unauthorized access to database",
        )

        assert breach.id == "breach_123"
        assert breach.severity == BreachSeverity.HIGH
        assert breach.affected_users == 1000
        assert len(breach.affected_data_categories) == 2
        assert breach.dpa_notified is False

    def test_data_retention_policy_dataclass(self):
        """Test DataRetentionPolicy dataclass"""
        policy = DataRetentionPolicy(
            id="policy_123",
            data_category=DataCategory.FINANCIAL,
            retention_period_days=2555,  # 7 years
            legal_basis=LegalBasis.LEGAL_OBLIGATION,
            description="Financial records retention",
        )

        assert policy.id == "policy_123"
        assert policy.data_category == DataCategory.FINANCIAL
        assert policy.retention_period_days == 2555
        assert policy.auto_delete is True

    def test_privacy_impact_assessment_dataclass(self):
        """Test PrivacyImpactAssessment (DPIA) dataclass"""
        dpia = PrivacyImpactAssessment(
            id="dpia_123",
            title="New AI Feature Assessment",
            description="Assessing AI-based profiling feature",
            data_categories=[DataCategory.BEHAVIORAL, DataCategory.BIOMETRIC],
            processing_purposes=["Personalization", "Security"],
            necessity_justification="Required for feature",
            risks_identified=[{"risk": "Bias in AI", "likelihood": "medium"}],
            mitigation_measures=["Regular audits", "Bias testing"],
            dpo_consulted=True,
            completed_at=datetime.now(),
            review_date=datetime.now() + timedelta(days=365),
        )

        assert dpia.id == "dpia_123"
        assert len(dpia.data_categories) == 2
        assert dpia.dpo_consulted is True
        assert dpia.approved is False


# =============================================================================
# MEDIUM TESTS - Class Methods
# =============================================================================


@pytest.mark.medium
class TestConsentManager:
    """Test ConsentManager class"""

    def test_request_consent(self):
        """Test requesting consent from user"""
        manager = ConsentManager()

        consent_id = manager.request_consent(
            user_id=1, purpose=ConsentPurpose.MARKETING, expiry_days=365, ip_address="192.168.1.1"
        )

        assert consent_id is not None
        assert consent_id in manager.consents
        assert manager.consents[consent_id].granted is False  # Waiting for grant
        assert manager.consents[consent_id].user_id == 1

    def test_grant_consent(self):
        """Test granting consent"""
        manager = ConsentManager()

        consent_id = manager.request_consent(user_id=1, purpose=ConsentPurpose.ANALYTICS)

        result = manager.grant_consent(consent_id, ip_address="192.168.1.1", user_agent="Mozilla/5.0")

        assert result is True
        assert manager.consents[consent_id].granted is True
        assert manager.consents[consent_id].ip_address == "192.168.1.1"

    def test_grant_consent_nonexistent(self):
        """Test granting consent for non-existent consent_id"""
        manager = ConsentManager()

        result = manager.grant_consent("nonexistent_id")

        assert result is False

    def test_withdraw_consent(self):
        """Test withdrawing consent (Article 7(3))"""
        manager = ConsentManager()

        consent_id = manager.request_consent(user_id=1, purpose=ConsentPurpose.MARKETING)
        manager.grant_consent(consent_id)

        result = manager.withdraw_consent(consent_id)

        assert result is True
        assert manager.consents[consent_id].granted is False
        assert manager.consents[consent_id].withdrawn_at is not None

    def test_check_consent_valid(self):
        """Test checking valid consent"""
        manager = ConsentManager()

        consent_id = manager.request_consent(user_id=1, purpose=ConsentPurpose.ANALYTICS, expiry_days=365)
        manager.grant_consent(consent_id)

        has_consent = manager.check_consent(user_id=1, purpose=ConsentPurpose.ANALYTICS)

        assert has_consent is True

    def test_check_consent_withdrawn(self):
        """Test checking withdrawn consent"""
        manager = ConsentManager()

        consent_id = manager.request_consent(user_id=1, purpose=ConsentPurpose.MARKETING)
        manager.grant_consent(consent_id)
        manager.withdraw_consent(consent_id)

        has_consent = manager.check_consent(user_id=1, purpose=ConsentPurpose.MARKETING)

        assert has_consent is False

    def test_check_consent_expired(self):
        """Test checking expired consent"""
        manager = ConsentManager()

        consent_id = manager.request_consent(user_id=1, purpose=ConsentPurpose.ANALYTICS, expiry_days=0)
        manager.grant_consent(consent_id)

        # Set expiry to past
        manager.consents[consent_id].expiry = datetime.now() - timedelta(days=1)

        has_consent = manager.check_consent(user_id=1, purpose=ConsentPurpose.ANALYTICS)

        assert has_consent is False

    def test_get_user_consents(self):
        """Test getting all consents for a user"""
        manager = ConsentManager()

        manager.request_consent(user_id=1, purpose=ConsentPurpose.MARKETING)
        manager.request_consent(user_id=1, purpose=ConsentPurpose.ANALYTICS)
        manager.request_consent(user_id=2, purpose=ConsentPurpose.MARKETING)

        user1_consents = manager.get_user_consents(user_id=1)

        assert len(user1_consents) == 2


@pytest.mark.medium
class TestDataSubjectRightsHandler:
    """Test DataSubjectRightsHandler class"""

    def test_submit_request(self):
        """Test submitting data subject rights request"""
        handler = DataSubjectRightsHandler()

        request_id = handler.submit_request(
            user_id=1, right=DataSubjectRight.ACCESS, notes="I want my data"
        )

        assert request_id is not None
        assert request_id in handler.requests
        assert handler.requests[request_id].status == "pending"

    def test_process_access_request(self):
        """Test processing right to access request (Article 15)"""
        handler = DataSubjectRightsHandler()

        request_id = handler.submit_request(user_id=1, right=DataSubjectRight.ACCESS)

        user_data = handler.process_access_request(request_id)

        assert user_data is not None
        assert "personal_data" in user_data
        assert "rights_information" in user_data
        assert handler.requests[request_id].status == "completed"

    def test_process_access_request_nonexistent(self):
        """Test processing access request for non-existent request"""
        handler = DataSubjectRightsHandler()

        result = handler.process_access_request("nonexistent_id")

        assert "error" in result

    def test_process_erasure_request_success(self):
        """Test processing right to erasure (Article 17)"""
        # Mock database
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        handler = DataSubjectRightsHandler(database=mock_db)

        request_id = handler.submit_request(user_id=1, right=DataSubjectRight.ERASURE)

        result = handler.process_erasure_request(request_id)

        assert result is True
        assert handler.requests[request_id].status == "completed"

    def test_process_erasure_request_rejected(self):
        """Test erasure request rejection when legally required"""
        handler = DataSubjectRightsHandler()

        request_id = handler.submit_request(user_id=1, right=DataSubjectRight.ERASURE)

        # Mock _can_erase_data to return False
        with patch.object(handler, "_can_erase_data", return_value=False):
            result = handler.process_erasure_request(request_id)

        assert result is False
        assert handler.requests[request_id].status == "rejected"

    def test_process_portability_request(self):
        """Test right to data portability (Article 20)"""
        handler = DataSubjectRightsHandler()

        request_id = handler.submit_request(user_id=1, right=DataSubjectRight.PORTABILITY)

        export_data = handler.process_portability_request(request_id)

        assert export_data is not None
        assert isinstance(export_data, str)
        assert handler.requests[request_id].status == "completed"

        # Verify JSON format
        parsed = json.loads(export_data)
        assert isinstance(parsed, dict)


@pytest.mark.medium
class TestDataBreachManager:
    """Test DataBreachManager class"""

    def test_report_breach(self):
        """Test reporting a data breach"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="Unauthorized database access",
            severity=BreachSeverity.HIGH,
            affected_users=500,
            affected_data_categories=[DataCategory.CONTACT, DataCategory.FINANCIAL],
        )

        assert breach_id is not None
        assert breach_id in manager.breaches
        assert manager.breaches[breach_id].affected_users == 500

    def test_report_high_severity_auto_notifies_dpa(self):
        """Test high severity breach auto-notifies DPA"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="Critical breach",
            severity=BreachSeverity.CRITICAL,
            affected_users=10000,
            affected_data_categories=[DataCategory.FINANCIAL, DataCategory.HEALTH],
        )

        assert manager.breaches[breach_id].dpa_notified is True
        assert manager.breaches[breach_id].reported_at is not None

    def test_notify_dpa(self):
        """Test notifying Data Protection Authority (Article 33)"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="Data leak", severity=BreachSeverity.MEDIUM, affected_users=100, affected_data_categories=[DataCategory.CONTACT]
        )

        result = manager.notify_dpa(breach_id)

        assert result is True
        assert manager.breaches[breach_id].dpa_notified is True

    def test_notify_dpa_72_hour_warning(self, capsys):
        """Test DPA notification warns if beyond 72 hours"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="Old breach", severity=BreachSeverity.LOW, affected_users=10, affected_data_categories=[DataCategory.TECHNICAL]
        )

        # Set discovered_at to 80 hours ago
        manager.breaches[breach_id].discovered_at = datetime.now() - timedelta(hours=80)

        manager.notify_dpa(breach_id)

        captured = capsys.readouterr()
        assert "WARNING: DPA notification delayed beyond 72 hours" in captured.out

    def test_notify_affected_users(self):
        """Test notifying affected users (Article 34)"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="High risk breach",
            severity=BreachSeverity.HIGH,
            affected_users=1000,
            affected_data_categories=[DataCategory.FINANCIAL],
        )

        result = manager.notify_affected_users(breach_id)

        assert result is True
        assert manager.breaches[breach_id].users_notified is True

    def test_add_mitigation_step(self):
        """Test adding mitigation steps"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="Breach", severity=BreachSeverity.MEDIUM, affected_users=50, affected_data_categories=[DataCategory.CONTACT]
        )

        manager.add_mitigation_step(breach_id, "Changed all passwords")
        manager.add_mitigation_step(breach_id, "Implemented 2FA")

        assert len(manager.breaches[breach_id].mitigation_steps) == 2

    def test_close_breach(self):
        """Test closing a breach incident"""
        manager = DataBreachManager()

        breach_id = manager.report_breach(
            description="Resolved breach",
            severity=BreachSeverity.LOW,
            affected_users=5,
            affected_data_categories=[DataCategory.TECHNICAL],
        )

        result = manager.close_breach(breach_id, notes="All issues resolved")

        assert result is True
        assert manager.breaches[breach_id].closed_at is not None
        assert manager.breaches[breach_id].resolution_notes == "All issues resolved"


@pytest.mark.medium
class TestRetentionPolicyManager:
    """Test RetentionPolicyManager class"""

    def test_default_policies_created(self):
        """Test default retention policies are created"""
        manager = RetentionPolicyManager()

        assert len(manager.policies) >= 3
        assert "policy_basic_identity" in manager.policies
        assert "policy_analytics" in manager.policies
        assert "policy_technical" in manager.policies

    def test_add_policy(self):
        """Test adding custom retention policy"""
        manager = RetentionPolicyManager()

        policy = DataRetentionPolicy(
            id="custom_policy",
            data_category=DataCategory.HEALTH,
            retention_period_days=3650,  # 10 years
            legal_basis=LegalBasis.LEGAL_OBLIGATION,
            description="Health data retention",
        )

        manager.add_policy(policy)

        assert "custom_policy" in manager.policies

    def test_get_retention_period(self):
        """Test getting retention period for data category"""
        manager = RetentionPolicyManager()

        period = manager.get_retention_period(DataCategory.BEHAVIORAL)

        assert period == 365  # Analytics data

    def test_get_retention_period_not_found(self):
        """Test getting retention period for unknown category"""
        manager = RetentionPolicyManager()

        period = manager.get_retention_period(DataCategory.HEALTH)

        assert period is None

    def test_cleanup_expired_data(self, capsys):
        """Test cleanup of expired data"""
        manager = RetentionPolicyManager()

        deleted_count = manager.cleanup_expired_data()

        captured = capsys.readouterr()
        assert "Would delete" in captured.out


@pytest.mark.medium
class TestGDPRComplianceEngine:
    """Test GDPRComplianceEngine main class"""

    def test_engine_initialization(self):
        """Test GDPR engine initialization"""
        engine = GDPRComplianceEngine()

        assert engine.consent_manager is not None
        assert engine.rights_handler is not None
        assert engine.breach_manager is not None
        assert engine.retention_manager is not None

    def test_create_dpia(self):
        """Test creating Data Protection Impact Assessment"""
        engine = GDPRComplianceEngine()

        dpia_id = engine.create_dpia(
            title="AI Profiling Feature",
            description="New AI-based user profiling",
            data_categories=[DataCategory.BEHAVIORAL, DataCategory.BIOMETRIC],
            processing_purposes=["Personalization", "Recommendations"],
        )

        assert dpia_id is not None
        assert dpia_id in engine.dpias
        assert len(engine.dpias[dpia_id].data_categories) == 2

    def test_get_compliance_status(self):
        """Test getting overall compliance status"""
        engine = GDPRComplianceEngine()

        # Create some test data
        engine.consent_manager.request_consent(user_id=1, purpose=ConsentPurpose.MARKETING)
        engine.rights_handler.submit_request(user_id=1, right=DataSubjectRight.ACCESS)
        engine.breach_manager.report_breach(
            description="Test", severity=BreachSeverity.LOW, affected_users=1, affected_data_categories=[DataCategory.TECHNICAL]
        )

        status = engine.get_compliance_status()

        assert "data_subject_requests" in status
        assert status["data_subject_requests"]["total"] == 1
        assert status["consents"]["total"] == 1
        assert status["data_breaches"]["total"] == 1

    def test_get_gdpr_engine_singleton(self):
        """Test global GDPR engine singleton"""
        engine1 = get_gdpr_engine()
        engine2 = get_gdpr_engine()

        assert engine1 is engine2

    def test_configure_gdpr_engine(self):
        """Test configuring GDPR engine"""
        mock_db = Mock()

        configure_gdpr_engine(mock_db)

        engine = get_gdpr_engine()
        assert engine.database is mock_db


# =============================================================================
# LARGE TESTS - End-to-End Workflows
# =============================================================================


@pytest.mark.large
@pytest.mark.integration
class TestGDPRWorkflows:
    """Test complete GDPR workflows"""

    def test_full_consent_workflow(self):
        """Test complete consent workflow: request → grant → use → withdraw"""
        manager = ConsentManager()

        # Step 1: Request consent
        consent_id = manager.request_consent(
            user_id=1, purpose=ConsentPurpose.MARKETING, expiry_days=365, ip_address="192.168.1.1"
        )
        assert consent_id is not None

        # Step 2: User grants consent
        result = manager.grant_consent(consent_id, ip_address="192.168.1.1", user_agent="Mozilla/5.0")
        assert result is True

        # Step 3: Check consent before processing
        has_consent = manager.check_consent(user_id=1, purpose=ConsentPurpose.MARKETING)
        assert has_consent is True

        # Step 4: User withdraws consent
        withdrawn = manager.withdraw_consent(consent_id)
        assert withdrawn is True

        # Step 5: Check consent is now invalid
        has_consent_after = manager.check_consent(user_id=1, purpose=ConsentPurpose.MARKETING)
        assert has_consent_after is False

    def test_right_to_be_forgotten_workflow(self):
        """Test complete right to be forgotten workflow"""
        # Mock database
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        handler = DataSubjectRightsHandler(database=mock_db)

        # Step 1: User submits erasure request
        request_id = handler.submit_request(
            user_id=1, right=DataSubjectRight.ERASURE, notes="Please delete all my data"
        )

        # Step 2: Process erasure request
        result = handler.process_erasure_request(request_id)

        # Step 3: Verify completion
        assert result is True
        assert handler.requests[request_id].status == "completed"
        assert handler.requests[request_id].completed_at is not None

    def test_data_portability_workflow(self):
        """Test complete data portability workflow"""
        handler = DataSubjectRightsHandler()

        # Step 1: User requests data export
        request_id = handler.submit_request(
            user_id=1, right=DataSubjectRight.PORTABILITY, notes="Export my data"
        )

        # Step 2: Process portability request
        export_data = handler.process_portability_request(request_id)

        # Step 3: Verify export
        assert export_data is not None
        assert isinstance(export_data, str)

        # Step 4: Validate JSON format
        parsed = json.loads(export_data)
        assert isinstance(parsed, dict)

        # Step 5: Verify request completed
        assert handler.requests[request_id].status == "completed"

    def test_data_breach_notification_workflow(self):
        """Test complete data breach notification workflow"""
        manager = DataBreachManager()

        # Step 1: Discover and report breach
        breach_id = manager.report_breach(
            description="Unauthorized access to customer database",
            severity=BreachSeverity.HIGH,
            affected_users=5000,
            affected_data_categories=[DataCategory.CONTACT, DataCategory.FINANCIAL],
        )

        # Step 2: Notify DPA (within 72 hours - Article 33)
        dpa_result = manager.notify_dpa(breach_id)
        assert dpa_result is True

        # Step 3: Notify affected users (Article 34)
        users_result = manager.notify_affected_users(breach_id)
        assert users_result is True

        # Step 4: Add mitigation steps
        manager.add_mitigation_step(breach_id, "Patched vulnerability")
        manager.add_mitigation_step(breach_id, "Reset user passwords")
        manager.add_mitigation_step(breach_id, "Enhanced monitoring")

        # Step 5: Close breach
        close_result = manager.close_breach(breach_id, notes="Vulnerability fixed, all users notified")
        assert close_result is True

        # Verify final state
        breach = manager.breaches[breach_id]
        assert breach.dpa_notified is True
        assert breach.users_notified is True
        assert len(breach.mitigation_steps) == 3
        assert breach.closed_at is not None

    def test_complete_gdpr_compliance_scenario(self):
        """Test complete GDPR compliance scenario across all components"""
        engine = GDPRComplianceEngine()

        # Step 1: Request and grant consent
        consent_id = engine.consent_manager.request_consent(
            user_id=1, purpose=ConsentPurpose.ANALYTICS, expiry_days=365
        )
        engine.consent_manager.grant_consent(consent_id)

        # Step 2: User exercises right to access
        access_request_id = engine.rights_handler.submit_request(
            user_id=1, right=DataSubjectRight.ACCESS
        )
        user_data = engine.rights_handler.process_access_request(access_request_id)
        assert "personal_data" in user_data

        # Step 3: Data breach occurs
        breach_id = engine.breach_manager.report_breach(
            description="Security incident",
            severity=BreachSeverity.MEDIUM,
            affected_users=100,
            affected_data_categories=[DataCategory.CONTACT],
        )

        # Step 4: Handle breach
        engine.breach_manager.notify_dpa(breach_id)
        engine.breach_manager.add_mitigation_step(breach_id, "Security patch applied")
        engine.breach_manager.close_breach(breach_id)

        # Step 5: Create DPIA for new feature
        dpia_id = engine.create_dpia(
            title="New Analytics Feature",
            description="Enhanced user analytics",
            data_categories=[DataCategory.BEHAVIORAL],
            processing_purposes=["Analytics"],
        )

        # Step 6: Check overall compliance status
        status = engine.get_compliance_status()

        assert status["data_subject_requests"]["total"] == 1
        assert status["data_subject_requests"]["completed"] == 1
        assert status["consents"]["active"] == 1
        assert status["data_breaches"]["total"] == 1
        assert status["data_breaches"]["open"] == 0
        assert status["dpias_completed"] == 1

    def test_multi_user_consent_management(self):
        """Test consent management for multiple users"""
        manager = ConsentManager()

        # Create consents for multiple users and purposes
        users = [1, 2, 3]
        purposes = [ConsentPurpose.MARKETING, ConsentPurpose.ANALYTICS, ConsentPurpose.PERSONALIZATION]

        consent_ids = {}

        for user_id in users:
            for purpose in purposes:
                consent_id = manager.request_consent(user_id=user_id, purpose=purpose)
                manager.grant_consent(consent_id)
                consent_ids[(user_id, purpose)] = consent_id

        # Verify all consents are valid
        for user_id in users:
            for purpose in purposes:
                assert manager.check_consent(user_id, purpose) is True

        # User 2 withdraws all consents
        user2_consents = manager.get_user_consents(user_id=2)
        for consent in user2_consents:
            manager.withdraw_consent(consent.id)

        # Verify user 2 has no valid consents
        for purpose in purposes:
            assert manager.check_consent(2, purpose) is False

        # Verify other users still have valid consents
        assert manager.check_consent(1, ConsentPurpose.MARKETING) is True
        assert manager.check_consent(3, ConsentPurpose.ANALYTICS) is True

    def test_retention_policy_compliance(self):
        """Test data retention policy compliance"""
        manager = RetentionPolicyManager()

        # Verify default policies exist
        assert len(manager.policies) >= 3

        # Add custom policy for health data
        health_policy = DataRetentionPolicy(
            id="health_retention",
            data_category=DataCategory.HEALTH,
            retention_period_days=3650,  # 10 years
            legal_basis=LegalBasis.LEGAL_OBLIGATION,
            description="Health records retention",
            auto_delete=False,
        )
        manager.add_policy(health_policy)

        # Verify retention periods
        assert manager.get_retention_period(DataCategory.HEALTH) == 3650
        assert manager.get_retention_period(DataCategory.BEHAVIORAL) == 365
        assert manager.get_retention_period(DataCategory.TECHNICAL) == 90

        # Test cleanup
        deleted_count = manager.cleanup_expired_data()
        assert deleted_count == 0  # Mock implementation

    def test_dpia_lifecycle(self):
        """Test complete DPIA (Data Protection Impact Assessment) lifecycle"""
        engine = GDPRComplianceEngine()

        # Step 1: Create DPIA for high-risk processing
        dpia_id = engine.create_dpia(
            title="Biometric Authentication System",
            description="Implement facial recognition for user authentication",
            data_categories=[DataCategory.BIOMETRIC, DataCategory.BASIC_IDENTITY],
            processing_purposes=["Authentication", "Security"],
        )

        dpia = engine.dpias[dpia_id]

        # Step 2: Document necessity
        dpia.necessity_justification = "Required for secure authentication"

        # Step 3: Identify risks
        dpia.risks_identified = [
            {"risk": "Biometric data breach", "likelihood": "medium", "impact": "high"},
            {"risk": "False positives/negatives", "likelihood": "low", "impact": "medium"},
            {"risk": "Surveillance concerns", "likelihood": "high", "impact": "medium"},
        ]

        # Step 4: Define mitigation measures
        dpia.mitigation_measures = [
            "Encrypt biometric templates at rest and in transit",
            "Regular security audits",
            "User consent and opt-out options",
            "Data minimization - store only templates, not raw images",
            "Regular accuracy testing",
        ]

        # Step 5: DPO consultation
        dpia.dpo_consulted = True

        # Step 6: Approval
        dpia.approved = True
        dpia.approver = "DPO - John Doe"

        # Verify DPIA completeness
        assert len(dpia.risks_identified) == 3
        assert len(dpia.mitigation_measures) == 5
        assert dpia.dpo_consulted is True
        assert dpia.approved is True

    def test_access_request_with_database(self):
        """Test access request with mocked database integration"""
        # Mock database with user data
        mock_db = MagicMock()
        mock_cursor = MagicMock()

        # Mock user data
        mock_cursor.fetchone.return_value = (1, "testuser", "test@example.com", "2024-01-01")
        mock_cursor.fetchall.return_value = [
            (1, "DocumentService", "us-east-1", "2024-01-01"),
            (2, "AnalyticsService", "eu-west-1", "2024-01-15"),
        ]

        mock_db.conn.cursor.return_value = mock_cursor

        handler = DataSubjectRightsHandler(database=mock_db)

        # Submit and process access request
        request_id = handler.submit_request(user_id=1, right=DataSubjectRight.ACCESS)
        user_data = handler.process_access_request(request_id)

        # Verify data structure
        assert "personal_data" in user_data
        assert "services" in user_data
        assert "rights_information" in user_data

        # Verify personal data
        personal_data = user_data["personal_data"]
        assert personal_data["id"] == 1
        assert personal_data["username"] == "testuser"
        assert personal_data["email"] == "test@example.com"

        # Verify services
        assert len(user_data["services"]) == 2
