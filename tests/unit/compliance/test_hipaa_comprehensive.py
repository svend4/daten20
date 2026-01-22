"""
Comprehensive HIPAA Compliance Tests

Tests for HIPAA (Health Insurance Portability and Accountability Act) compliance module.
Covers PHI protection, access controls, encryption, breach notification, and safeguards.
"""

import base64
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.compliance.hipaa import (
    AccessControlManager,
    AccessLevel,
    AccessLog,
    BreachNotificationManager,
    BreachRiskLevel,
    BusinessAssociate,
    EncryptionManager,
    HIPAAComplianceEngine,
    PHICategory,
    PHIField,
    PHIIdentifier,
    RiskAssessment,
    SafeguardType,
    SecurityIncident,
    configure_hipaa_engine,
    get_hipaa_engine,
)


# =============================================================================
# SMALL TESTS - Enums and Dataclasses
# =============================================================================


@pytest.mark.small
class TestEnums:
    """Test HIPAA enum values"""

    def test_phi_category_enum(self):
        """Test PHICategory enum has required identifiers"""
        assert PHICategory.NAMES == "names"
        assert PHICategory.SSN == "social_security_numbers"
        assert PHICategory.EMAIL == "email_addresses"
        assert PHICategory.DIAGNOSIS == "diagnosis"
        assert PHICategory.TREATMENT == "treatment"
        assert PHICategory.BIOMETRIC == "biometric_identifiers"

    def test_safeguard_type_enum(self):
        """Test SafeguardType enum (HIPAA Security Rule)"""
        assert SafeguardType.ADMINISTRATIVE == "administrative"
        assert SafeguardType.PHYSICAL == "physical"
        assert SafeguardType.TECHNICAL == "technical"

    def test_access_level_enum(self):
        """Test AccessLevel enum values"""
        assert AccessLevel.NO_ACCESS == "no_access"
        assert AccessLevel.READ_ONLY == "read_only"
        assert AccessLevel.LIMITED == "limited"
        assert AccessLevel.FULL == "full"

    def test_breach_risk_level_enum(self):
        """Test BreachRiskLevel enum"""
        assert BreachRiskLevel.LOW == "low"
        assert BreachRiskLevel.MODERATE == "moderate"
        assert BreachRiskLevel.HIGH == "high"


@pytest.mark.small
class TestDataclasses:
    """Test HIPAA dataclass creation"""

    def test_phi_field_dataclass(self):
        """Test PHIField dataclass"""
        field = PHIField(field_name="ssn", category=PHICategory.SSN, encrypted=True, anonymized=False)

        assert field.field_name == "ssn"
        assert field.category == PHICategory.SSN
        assert field.encrypted is True
        assert field.minimum_necessary is True

    def test_access_log_dataclass(self):
        """Test AccessLog dataclass for audit controls"""
        log = AccessLog(
            id="log_123",
            user_id=1,
            username="doctor_smith",
            phi_resource="patient_records",
            action="view",
            timestamp=datetime.now(),
            ip_address="192.168.1.100",
            success=True,
            data_accessed=["diagnosis", "medication"],
        )

        assert log.user_id == 1
        assert log.action == "view"
        assert log.success is True
        assert len(log.data_accessed) == 2

    def test_business_associate_dataclass(self):
        """Test BusinessAssociate (BAA) dataclass"""
        ba = BusinessAssociate(
            id="ba_123",
            name="Cloud Storage Provider",
            contact_email="compliance@provider.com",
            baa_signed=True,
            baa_signed_date=datetime.now(),
            baa_expiry_date=datetime.now() + timedelta(days=1095),
            services_provided=["Data Storage", "Backup"],
            phi_categories_accessed=[PHICategory.DIAGNOSIS, PHICategory.TREATMENT],
            security_assessment_date=datetime.now(),
            compliant=True,
        )

        assert ba.name == "Cloud Storage Provider"
        assert ba.baa_signed is True
        assert len(ba.services_provided) == 2

    def test_security_incident_dataclass(self):
        """Test SecurityIncident dataclass"""
        incident = SecurityIncident(
            id="inc_123",
            reported_at=datetime.now(),
            incident_type="Unauthorized Access",
            description="Unauthorized login attempt",
            severity=BreachRiskLevel.HIGH,
            phi_compromised=True,
            affected_individuals=250,
        )

        assert incident.incident_type == "Unauthorized Access"
        assert incident.phi_compromised is True
        assert incident.affected_individuals == 250
        assert incident.resolved is False

    def test_risk_assessment_dataclass(self):
        """Test RiskAssessment dataclass (§164.308(a)(1)(ii)(A))"""
        assessment = RiskAssessment(
            id="ra_123",
            conducted_date=datetime.now(),
            conducted_by="Security Officer",
            scope="Full system assessment",
            threats_identified=[{"threat": "Malware", "likelihood": "medium"}],
            vulnerabilities_identified=[{"vuln": "Unpatched systems", "severity": "high"}],
            current_security_measures=["Firewall", "Antivirus", "Encryption"],
            recommended_actions=[{"action": "Patch systems", "priority": "high"}],
            next_assessment_date=datetime.now() + timedelta(days=365),
        )

        assert assessment.conducted_by == "Security Officer"
        assert len(assessment.threats_identified) == 1
        assert len(assessment.current_security_measures) == 3


# =============================================================================
# MEDIUM TESTS - Class Methods
# =============================================================================


@pytest.mark.medium
class TestPHIIdentifier:
    """Test PHI identification and anonymization"""

    def test_identify_phi_ssn(self):
        """Test identifying SSN in data"""
        identifier = PHIIdentifier()

        data = {"name": "John Doe", "ssn": "123-45-6789", "address": "123 Main St"}

        phi_fields = identifier.identify_phi(data)

        assert len(phi_fields) > 0
        assert any(f.category == PHICategory.SSN for f in phi_fields)

    def test_identify_phi_email(self):
        """Test identifying email addresses"""
        identifier = PHIIdentifier()

        data = {"patient_id": "12345", "contact": "patient@example.com"}

        phi_fields = identifier.identify_phi(data)

        assert len(phi_fields) > 0
        assert any(f.category == PHICategory.EMAIL for f in phi_fields)

    def test_anonymize_phi(self):
        """Test PHI anonymization (de-identification §164.514)"""
        identifier = PHIIdentifier()

        data = {"name": "John Doe", "ssn": "123-45-6789", "diagnosis": "Diabetes"}

        anonymized = identifier.anonymize_phi(data, ["name", "ssn"])

        assert anonymized["name"] != "John Doe"
        assert anonymized["ssn"] != "123-45-6789"
        assert anonymized["diagnosis"] == "Diabetes"  # Not anonymized


@pytest.mark.medium
class TestAccessControlManager:
    """Test PHI access control (§164.308(a)(3))"""

    def test_authorize_user(self):
        """Test authorizing user for PHI access"""
        manager = AccessControlManager()

        manager.authorize_user(user_id=1, access_level=AccessLevel.READ_ONLY)

        assert 1 in manager.authorized_users
        assert manager.authorized_users[1] == AccessLevel.READ_ONLY

    def test_revoke_access(self):
        """Test revoking PHI access (Termination procedures)"""
        manager = AccessControlManager()

        manager.authorize_user(user_id=1, access_level=AccessLevel.FULL)
        manager.revoke_access(user_id=1)

        assert 1 not in manager.authorized_users

    def test_check_access_authorized(self):
        """Test checking access for authorized user"""
        manager = AccessControlManager()

        manager.authorize_user(user_id=1, access_level=AccessLevel.FULL)

        has_access = manager.check_access(user_id=1, required_level=AccessLevel.READ_ONLY)

        assert has_access is True

    def test_check_access_insufficient(self):
        """Test checking access with insufficient level"""
        manager = AccessControlManager()

        manager.authorize_user(user_id=1, access_level=AccessLevel.READ_ONLY)

        has_access = manager.check_access(user_id=1, required_level=AccessLevel.FULL)

        assert has_access is False

    def test_log_access(self):
        """Test logging PHI access (Audit controls §164.308(a)(1)(ii)(D))"""
        manager = AccessControlManager()

        manager.log_access(
            user_id=1,
            username="doctor_smith",
            phi_resource="patient_123",
            action="view",
            ip_address="192.168.1.100",
            success=True,
            data_accessed=["diagnosis"],
        )

        assert len(manager.access_logs) == 1
        assert manager.access_logs[0].username == "doctor_smith"

    def test_get_access_report(self):
        """Test generating access report for auditing"""
        manager = AccessControlManager()

        # Create multiple access logs
        for i in range(5):
            manager.log_access(
                user_id=i,
                username=f"user_{i}",
                phi_resource="records",
                action="view",
                ip_address="192.168.1.1",
                success=True,
            )

        report = manager.get_access_report()

        assert len(report) == 5

    def test_get_access_report_filtered_by_user(self):
        """Test access report filtered by user"""
        manager = AccessControlManager()

        manager.log_access(user_id=1, username="user1", phi_resource="r1", action="view", ip_address="1.1.1.1", success=True)
        manager.log_access(user_id=2, username="user2", phi_resource="r2", action="view", ip_address="1.1.1.1", success=True)

        report = manager.get_access_report(user_id=1)

        assert len(report) == 1
        assert report[0].user_id == 1

    def test_detect_anomalies_unusual_time(self):
        """Test detecting anomalous access patterns"""
        manager = AccessControlManager()

        # Create log at unusual time (3 AM)
        unusual_time = datetime.now().replace(hour=3, minute=0, second=0)

        with patch("src.compliance.hipaa.datetime") as mock_datetime:
            mock_datetime.now.return_value = unusual_time

            manager.log_access(
                user_id=1, username="user1", phi_resource="records", action="view", ip_address="1.1.1.1", success=True
            )

        anomalies = manager.detect_anomalies()

        assert len(anomalies) > 0
        assert any(a["type"] == "unusual_time" for a in anomalies)


@pytest.mark.medium
class TestEncryptionManager:
    """Test PHI encryption (§164.312(a)(2)(iv))"""

    def test_generate_key(self):
        """Test encryption key generation"""
        manager = EncryptionManager()

        assert manager.encryption_key is not None
        assert len(manager.encryption_key) == 64  # 32 bytes in hex

    def test_encrypt_phi(self):
        """Test PHI data encryption"""
        manager = EncryptionManager()

        plaintext = "Patient has diabetes"

        encrypted = manager.encrypt_phi(plaintext)

        assert encrypted != plaintext
        assert isinstance(encrypted, str)

    def test_decrypt_phi(self):
        """Test PHI data decryption"""
        manager = EncryptionManager()

        plaintext = "Confidential medical data"
        encrypted = manager.encrypt_phi(plaintext)
        decrypted = manager.decrypt_phi(encrypted)

        assert decrypted == plaintext

    def test_encrypt_in_transit(self):
        """Test encryption in transit (TLS 1.2+)"""
        manager = EncryptionManager()

        config = manager.encrypt_in_transit()

        assert config["tls_version"] >= "1.2"
        assert "AES" in config["cipher_suite"]
        assert config["certificate_valid"] is True


@pytest.mark.medium
class TestBreachNotificationManager:
    """Test breach notification (§164.400-414)"""

    def test_report_incident(self):
        """Test reporting security incident"""
        manager = BreachNotificationManager()

        incident_id = manager.report_incident(
            incident_type="Unauthorized Access",
            description="Hacker accessed patient database",
            phi_compromised=True,
            affected_individuals=100,
        )

        assert incident_id is not None
        assert incident_id in manager.incidents

    def test_assess_breach_risk_high(self):
        """Test breach risk assessment - high risk (500+ individuals)"""
        manager = BreachNotificationManager()

        risk = manager._assess_breach_risk(phi_compromised=True, affected_count=600)

        assert risk == BreachRiskLevel.HIGH

    def test_assess_breach_risk_moderate(self):
        """Test breach risk assessment - moderate"""
        manager = BreachNotificationManager()

        risk = manager._assess_breach_risk(phi_compromised=True, affected_count=100)

        assert risk == BreachRiskLevel.MODERATE

    def test_assess_breach_risk_low(self):
        """Test breach risk assessment - low"""
        manager = BreachNotificationManager()

        risk = manager._assess_breach_risk(phi_compromised=False, affected_count=10)

        assert risk == BreachRiskLevel.LOW

    def test_generate_breach_report(self):
        """Test generating breach report for HHS"""
        manager = BreachNotificationManager()

        incident_id = manager.report_incident(
            incident_type="Data Breach", description="Laptop stolen", phi_compromised=True, affected_individuals=50
        )

        report = manager.generate_breach_report(incident_id)

        assert "incident_id" in report
        assert report["affected_individuals"] == 50


@pytest.mark.medium
class TestHIPAAComplianceEngine:
    """Test HIPAA compliance engine"""

    def test_engine_initialization(self):
        """Test HIPAA engine initialization"""
        engine = HIPAAComplianceEngine()

        assert engine.phi_identifier is not None
        assert engine.access_control is not None
        assert engine.encryption is not None
        assert engine.breach_notification is not None

    def test_register_business_associate(self):
        """Test registering Business Associate"""
        engine = HIPAAComplianceEngine()

        ba_id = engine.register_business_associate(
            name="Cloud Provider",
            contact_email="legal@cloudprovider.com",
            services_provided=["Data Storage", "Backup"],
            phi_categories=[PHICategory.DIAGNOSIS, PHICategory.TREATMENT],
        )

        assert ba_id is not None
        assert ba_id in engine.business_associates
        assert engine.business_associates[ba_id].baa_signed is False

    def test_sign_baa(self):
        """Test signing Business Associate Agreement"""
        engine = HIPAAComplianceEngine()

        ba_id = engine.register_business_associate(
            name="Provider", contact_email="legal@provider.com", services_provided=["Storage"], phi_categories=[PHICategory.NAMES]
        )

        result = engine.sign_baa(ba_id, expiry_years=3)

        assert result is True
        assert engine.business_associates[ba_id].baa_signed is True
        assert engine.business_associates[ba_id].baa_signed_date is not None

    def test_conduct_risk_assessment(self):
        """Test conducting security risk assessment"""
        engine = HIPAAComplianceEngine()

        assessment_id = engine.conduct_risk_assessment(conducted_by="Security Officer", scope="Full system")

        assert assessment_id is not None
        assert len(engine.risk_assessments) == 1

    def test_record_training(self):
        """Test recording HIPAA training (§164.308(a)(5))"""
        engine = HIPAAComplianceEngine()

        engine.record_training(user_id=1)
        engine.record_training(user_id=1)  # Second training

        assert 1 in engine.training_records
        assert len(engine.training_records[1]) == 2

    def test_check_training_current(self):
        """Test checking if training is current"""
        engine = HIPAAComplianceEngine()

        engine.record_training(user_id=1)

        is_current = engine.check_training_current(user_id=1)

        assert is_current is True

    def test_check_training_expired(self):
        """Test checking expired training"""
        engine = HIPAAComplianceEngine()

        engine.record_training(user_id=1)

        # Set training to 2 years ago
        engine.training_records[1][0] = datetime.now() - timedelta(days=730)

        is_current = engine.check_training_current(user_id=1)

        assert is_current is False

    def test_get_compliance_status(self):
        """Test getting overall HIPAA compliance status"""
        engine = HIPAAComplianceEngine()

        # Setup some compliance items
        engine.record_training(user_id=1)
        engine.access_control.authorize_user(user_id=1, access_level=AccessLevel.FULL)
        engine.conduct_risk_assessment(conducted_by="Officer", scope="System")

        status = engine.get_compliance_status()

        assert "administrative_safeguards" in status
        assert "technical_safeguards" in status
        assert "physical_safeguards" in status
        assert status["administrative_safeguards"]["trained_users"] == 1


# =============================================================================
# LARGE TESTS - End-to-End Workflows
# =============================================================================


@pytest.mark.large
@pytest.mark.integration
class TestHIPAAWorkflows:
    """Test complete HIPAA compliance workflows"""

    def test_complete_phi_access_workflow(self):
        """Test complete PHI access workflow with authorization and logging"""
        engine = HIPAAComplianceEngine()

        # Step 1: Train user
        engine.record_training(user_id=1)

        # Step 2: Authorize user
        engine.access_control.authorize_user(user_id=1, access_level=AccessLevel.FULL)

        # Step 3: Check access
        has_access = engine.access_control.check_access(user_id=1, required_level=AccessLevel.READ_ONLY)
        assert has_access is True

        # Step 4: Log access
        engine.access_control.log_access(
            user_id=1,
            username="doctor_smith",
            phi_resource="patient_records",
            action="view",
            ip_address="192.168.1.100",
            success=True,
            data_accessed=["diagnosis", "treatment"],
        )

        # Step 5: Verify audit log
        assert len(engine.access_control.access_logs) == 1
        assert engine.access_control.access_logs[0].success is True

    def test_breach_notification_workflow(self, capsys):
        """Test complete breach notification workflow"""
        engine = HIPAAComplianceEngine()

        # Step 1: Report breach (500+ individuals)
        incident_id = engine.breach_notification.report_incident(
            incident_type="Data Breach",
            description="Database server hacked",
            phi_compromised=True,
            affected_individuals=550,
        )

        # Step 2: Verify auto-notification triggered
        captured = capsys.readouterr()
        assert "Notifying HHS" in captured.out
        assert "Notifying prominent media" in captured.out

        # Step 3: Generate breach report
        report = engine.breach_notification.generate_breach_report(incident_id)

        assert report["affected_individuals"] == 550
        assert report["breach_type"] == "Data Breach"

    def test_business_associate_compliance_workflow(self):
        """Test Business Associate Agreement workflow"""
        engine = HIPAAComplianceEngine()

        # Step 1: Register Business Associate
        ba_id = engine.register_business_associate(
            name="Medical Billing Service",
            contact_email="compliance@billing.com",
            services_provided=["Billing", "Claims Processing"],
            phi_categories=[PHICategory.NAMES, PHICategory.SSN, PHICategory.DIAGNOSIS],
        )

        # Step 2: Verify not yet signed
        ba = engine.business_associates[ba_id]
        assert ba.baa_signed is False

        # Step 3: Sign BAA
        engine.sign_baa(ba_id, expiry_years=3)

        # Step 4: Verify BAA signed
        assert ba.baa_signed is True
        assert ba.baa_expiry_date > datetime.now()

        # Step 5: Check in compliance status
        status = engine.get_compliance_status()
        assert status["business_associates"]["active_baas"] == 1

    def test_security_risk_assessment_workflow(self):
        """Test complete security risk assessment workflow"""
        engine = HIPAAComplianceEngine()

        # Step 1: Conduct risk assessment
        assessment_id = engine.conduct_risk_assessment(
            conducted_by="Chief Security Officer", scope="Enterprise-wide security assessment"
        )

        # Step 2: Add identified threats
        assessment = engine.risk_assessments[0]
        assessment.threats_identified = [
            {"threat": "Ransomware", "likelihood": "high", "impact": "critical"},
            {"threat": "Insider threats", "likelihood": "medium", "impact": "high"},
            {"threat": "DDoS attacks", "likelihood": "low", "impact": "medium"},
        ]

        # Step 3: Add vulnerabilities
        assessment.vulnerabilities_identified = [
            {"vulnerability": "Unpatched servers", "severity": "high"},
            {"vulnerability": "Weak passwords", "severity": "medium"},
        ]

        # Step 4: Document current security measures
        assessment.current_security_measures = [
            "Firewall",
            "Antivirus",
            "Encryption at rest",
            "Encryption in transit",
            "Multi-factor authentication",
            "Regular backups",
        ]

        # Step 5: Recommend actions
        assessment.recommended_actions = [
            {"action": "Implement automated patching", "priority": "high", "timeline": "30 days"},
            {"action": "Enforce password policy", "priority": "high", "timeline": "immediate"},
            {"action": "Conduct penetration testing", "priority": "medium", "timeline": "90 days"},
        ]

        # Verify assessment complete
        assert len(assessment.threats_identified) == 3
        assert len(assessment.vulnerabilities_identified) == 2
        assert len(assessment.recommended_actions) == 3

    def test_training_compliance_workflow(self):
        """Test HIPAA training compliance workflow"""
        engine = HIPAAComplianceEngine()

        # Step 1: Train multiple users
        for user_id in range(1, 11):
            engine.record_training(user_id)

        # Step 2: Verify all training current
        current_count = sum(1 for uid in range(1, 11) if engine.check_training_current(uid))
        assert current_count == 10

        # Step 3: Simulate expired training for user 5
        engine.training_records[5][0] = datetime.now() - timedelta(days=400)

        # Step 4: Verify user 5 needs retraining
        assert engine.check_training_current(5) is False

        # Step 5: Retrain user 5
        engine.record_training(5)

        # Step 6: Verify now current
        assert engine.check_training_current(5) is True

    def test_complete_compliance_scenario(self):
        """Test complete HIPAA compliance scenario"""
        engine = HIPAAComplianceEngine()

        # Step 1: Administrative Safeguards
        engine.record_training(user_id=1)
        engine.record_training(user_id=2)
        engine.access_control.authorize_user(user_id=1, access_level=AccessLevel.FULL)
        engine.access_control.authorize_user(user_id=2, access_level=AccessLevel.LIMITED)

        # Step 2: Technical Safeguards
        phi_data = "Patient has diabetes type 2"
        encrypted_phi = engine.encryption.encrypt_phi(phi_data)
        assert encrypted_phi != phi_data

        # Step 3: Business Associate Management
        ba_id = engine.register_business_associate(
            name="Cloud Storage", contact_email="legal@cloud.com", services_provided=["Storage"], phi_categories=[PHICategory.DIAGNOSIS]
        )
        engine.sign_baa(ba_id, expiry_years=3)

        # Step 4: Risk Management
        engine.conduct_risk_assessment(conducted_by="Security Officer", scope="Full system")

        # Step 5: Access logging
        engine.access_control.log_access(
            user_id=1, username="doctor", phi_resource="records", action="view", ip_address="1.1.1.1", success=True
        )

        # Step 6: Get compliance status
        status = engine.get_compliance_status()

        # Verify all components
        assert status["administrative_safeguards"]["trained_users"] == 2
        assert status["technical_safeguards"]["encryption_in_transit"] is True
        assert status["business_associates"]["active_baas"] == 1
        assert status["risk_management"]["recent_assessments"] == 1

    def test_phi_identification_and_encryption_workflow(self):
        """Test PHI identification and encryption workflow"""
        engine = HIPAAComplianceEngine()

        # Step 1: Identify PHI in patient data
        patient_data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "diagnosis": "Hypertension",
        }

        phi_fields = engine.phi_identifier.identify_phi(patient_data)

        # Step 2: Verify PHI identified
        assert len(phi_fields) > 0
        phi_categories = [f.category for f in phi_fields]
        assert PHICategory.SSN in phi_categories
        assert PHICategory.EMAIL in phi_categories

        # Step 3: Anonymize sensitive fields
        anonymized = engine.phi_identifier.anonymize_phi(patient_data, ["name", "ssn"])

        assert anonymized["name"] != "John Doe"
        assert anonymized["ssn"] != "123-45-6789"
        assert anonymized["diagnosis"] == "Hypertension"  # Medical data preserved

        # Step 4: Encrypt remaining PHI
        encrypted_diagnosis = engine.encryption.encrypt_phi(anonymized["diagnosis"])

        assert encrypted_diagnosis != "Hypertension"

        # Step 5: Verify decryption works
        decrypted = engine.encryption.decrypt_phi(encrypted_diagnosis)

        assert decrypted == "Hypertension"
