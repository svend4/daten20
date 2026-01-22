"""
Comprehensive SOC 2 Compliance Tests

Tests for SOC 2 (Service Organization Control 2) compliance framework.
Covers Trust Services Criteria: Security, Availability, Processing Integrity,
Confidentiality, and Privacy.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.compliance.soc2 import (
    AuditLog,
    AvailabilityControls,
    ChangeManager,
    ChangeRequest,
    ChangeRiskLevel,
    ConfidentialityControls,
    Control,
    ControlStatus,
    Evidence,
    Incident,
    IncidentManager,
    IncidentSeverity,
    PrivacyControls,
    ProcessingIntegrityControls,
    SOC2ComplianceEngine,
    SecurityControls,
    TrustServiceCategory,
    Vendor,
)


# =============================================================================
# SMALL TESTS - Enums and Dataclasses
# =============================================================================


@pytest.mark.small
class TestEnums:
    """Test SOC 2 enum values"""

    def test_trust_service_category_enum(self):
        """Test TrustServiceCategory enum (TSC)"""
        assert TrustServiceCategory.SECURITY == "security"
        assert TrustServiceCategory.AVAILABILITY == "availability"
        assert TrustServiceCategory.PROCESSING_INTEGRITY == "processing_integrity"
        assert TrustServiceCategory.CONFIDENTIALITY == "confidentiality"
        assert TrustServiceCategory.PRIVACY == "privacy"

    def test_control_status_enum(self):
        """Test ControlStatus enum"""
        assert ControlStatus.NOT_IMPLEMENTED == "not_implemented"
        assert ControlStatus.PARTIALLY_IMPLEMENTED == "partially_implemented"
        assert ControlStatus.IMPLEMENTED == "implemented"
        assert ControlStatus.OPERATING_EFFECTIVELY == "operating_effectively"
        assert ControlStatus.NEEDS_IMPROVEMENT == "needs_improvement"

    def test_incident_severity_enum(self):
        """Test IncidentSeverity enum"""
        assert IncidentSeverity.LOW == "low"
        assert IncidentSeverity.MEDIUM == "medium"
        assert IncidentSeverity.HIGH == "high"
        assert IncidentSeverity.CRITICAL == "critical"

    def test_change_risk_level_enum(self):
        """Test ChangeRiskLevel enum"""
        assert ChangeRiskLevel.LOW == "low"
        assert ChangeRiskLevel.MEDIUM == "medium"
        assert ChangeRiskLevel.HIGH == "high"


@pytest.mark.small
class TestDataclasses:
    """Test SOC 2 dataclass creation"""

    def test_control_dataclass(self):
        """Test Control dataclass"""
        control = Control(
            id="CC1.1",
            category=TrustServiceCategory.SECURITY,
            title="Management Philosophy",
            description="Management demonstrates commitment",
            control_activity="Code of conduct reviewed annually",
            frequency="annually",
            owner="Management",
            status=ControlStatus.IMPLEMENTED,
        )

        assert control.id == "CC1.1"
        assert control.category == TrustServiceCategory.SECURITY
        assert control.status == ControlStatus.IMPLEMENTED

    def test_evidence_dataclass(self):
        """Test Evidence dataclass"""
        evidence = Evidence(
            id="ev_123",
            control_id="CC1.1",
            collected_date=datetime.now(),
            collected_by="Auditor",
            evidence_type="document",
            description="Code of conduct signed documents",
            file_path="/evidence/code_of_conduct.pdf",
        )

        assert evidence.control_id == "CC1.1"
        assert evidence.evidence_type == "document"

    def test_incident_dataclass(self):
        """Test Incident dataclass"""
        incident = Incident(
            id="inc_123",
            title="Security Incident",
            description="Unauthorized access attempt",
            category=TrustServiceCategory.SECURITY,
            severity=IncidentSeverity.HIGH,
            detected_at=datetime.now(),
            detected_by="SOC Team",
            affected_systems=["Web Server", "Database"],
        )

        assert incident.severity == IncidentSeverity.HIGH
        assert len(incident.affected_systems) == 2

    def test_change_request_dataclass(self):
        """Test ChangeRequest dataclass"""
        change = ChangeRequest(
            id="chg_123",
            title="Database Schema Update",
            description="Add new table for reporting",
            requested_by="Dev Team",
            requested_at=datetime.now(),
            risk_level=ChangeRiskLevel.MEDIUM,
            affected_systems=["Database"],
            rollback_plan="Restore from backup",
            testing_plan="Test in staging environment",
        )

        assert change.risk_level == ChangeRiskLevel.MEDIUM
        assert change.approved is False

    def test_vendor_dataclass(self):
        """Test Vendor dataclass"""
        vendor = Vendor(
            id="ven_123",
            name="Cloud Storage Provider",
            services_provided=["Data Storage", "CDN"],
            criticality="high",
            data_access=True,
            soc2_report=True,
            soc2_report_date=datetime.now(),
        )

        assert vendor.criticality == "high"
        assert vendor.soc2_report is True

    def test_audit_log_dataclass(self):
        """Test AuditLog dataclass"""
        log = AuditLog(
            id="log_123",
            timestamp=datetime.now(),
            user="admin",
            action="UPDATE",
            resource="user_permissions",
            ip_address="192.168.1.100",
            result="success",
            details={"permissions_added": ["admin"]},
        )

        assert log.action == "UPDATE"
        assert log.result == "success"


# =============================================================================
# MEDIUM TESTS - Class Methods
# =============================================================================


@pytest.mark.medium
class TestSecurityControls:
    """Test Security Controls (Common Criteria)"""

    def test_initialize_security_controls(self):
        """Test initialization of security controls (CC1-CC9)"""
        controls = SecurityControls()

        assert len(controls.controls) > 0
        assert "CC1.1" in controls.controls
        assert "CC5.1" in controls.controls  # Logical Access Controls
        assert "CC9.1" in controls.controls  # Encryption

    def test_security_control_structure(self):
        """Test security control has correct structure"""
        controls = SecurityControls()

        cc1 = controls.controls["CC1.1"]

        assert cc1.category == TrustServiceCategory.SECURITY
        assert cc1.frequency is not None
        assert cc1.owner is not None


@pytest.mark.medium
class TestAvailabilityControls:
    """Test Availability Controls"""

    def test_initialize_availability_controls(self):
        """Test initialization of availability controls"""
        controls = AvailabilityControls()

        assert len(controls.controls) > 0
        assert "A1.1" in controls.controls  # Availability Monitoring
        assert "A1.2" in controls.controls  # Capacity Planning

    def test_availability_control_category(self):
        """Test availability controls have correct category"""
        controls = AvailabilityControls()

        for control in controls.controls.values():
            assert control.category == TrustServiceCategory.AVAILABILITY


@pytest.mark.medium
class TestProcessingIntegrityControls:
    """Test Processing Integrity Controls"""

    def test_initialize_pi_controls(self):
        """Test initialization of processing integrity controls"""
        controls = ProcessingIntegrityControls()

        assert len(controls.controls) > 0
        assert "PI1.1" in controls.controls  # Data Input Validation
        assert "PI1.2" in controls.controls  # Processing Accuracy

    def test_pi_control_category(self):
        """Test PI controls have correct category"""
        controls = ProcessingIntegrityControls()

        for control in controls.controls.values():
            assert control.category == TrustServiceCategory.PROCESSING_INTEGRITY


@pytest.mark.medium
class TestConfidentialityControls:
    """Test Confidentiality Controls"""

    def test_initialize_confidentiality_controls(self):
        """Test initialization of confidentiality controls"""
        controls = ConfidentialityControls()

        assert len(controls.controls) > 0
        assert "C1.1" in controls.controls  # Data Classification
        assert "C1.3" in controls.controls  # Secure Disposal

    def test_confidentiality_control_category(self):
        """Test confidentiality controls have correct category"""
        controls = ConfidentialityControls()

        for control in controls.controls.values():
            assert control.category == TrustServiceCategory.CONFIDENTIALITY


@pytest.mark.medium
class TestPrivacyControls:
    """Test Privacy Controls"""

    def test_initialize_privacy_controls(self):
        """Test initialization of privacy controls (P1-P8)"""
        controls = PrivacyControls()

        assert len(controls.controls) > 0
        assert "P1.1" in controls.controls  # Privacy Notice
        assert "P2.1" in controls.controls  # Consent Management
        assert "P3.1" in controls.controls  # Data Subject Rights

    def test_privacy_control_category(self):
        """Test privacy controls have correct category"""
        controls = PrivacyControls()

        for control in controls.controls.values():
            assert control.category == TrustServiceCategory.PRIVACY


@pytest.mark.medium
class TestIncidentManager:
    """Test Incident Manager"""

    def test_create_incident(self):
        """Test creating security incident"""
        manager = IncidentManager()

        incident_id = manager.create_incident(
            title="Database Breach",
            description="Unauthorized database access",
            category=TrustServiceCategory.SECURITY,
            severity=IncidentSeverity.HIGH,
            affected_systems=["Database", "API"],
            detected_by="SOC Team",
        )

        assert incident_id is not None
        assert incident_id in manager.incidents

    def test_resolve_incident(self):
        """Test resolving incident"""
        manager = IncidentManager()

        incident_id = manager.create_incident(
            title="Issue", description="Problem", category=TrustServiceCategory.SECURITY, severity=IncidentSeverity.MEDIUM, affected_systems=["System"], detected_by="User"
        )

        manager.resolve_incident(
            incident_id,
            root_cause="Database connection timeout",
            resolution="Restarted service and increased connection pool",
            lessons_learned=["Monitor connection pool metrics", "Add connection timeout alerts"],
        )

        incident = manager.incidents[incident_id]
        assert incident.root_cause is not None
        assert incident.resolution is not None
        assert incident.resolved_at is not None
        assert len(incident.lessons_learned) == 2

    def test_get_open_incidents(self):
        """Test getting open incidents"""
        manager = IncidentManager()

        # Create open incident
        manager.create_incident(
            title="Open", description="Issue", category=TrustServiceCategory.SECURITY, severity=IncidentSeverity.MEDIUM, affected_systems=["S"], detected_by="U"
        )

        # Create resolved incident
        inc_id = manager.create_incident(
            title="Resolved", description="Fixed", category=TrustServiceCategory.SECURITY, severity=IncidentSeverity.LOW, affected_systems=["S"], detected_by="U"
        )
        manager.resolve_incident(inc_id, root_cause="User error", resolution="Fixed", lessons_learned=[])

        open_incidents = manager.get_open_incidents()

        assert len(open_incidents) == 1


@pytest.mark.medium
class TestChangeManager:
    """Test Change Manager"""

    def test_create_change_request(self):
        """Test creating change request"""
        manager = ChangeManager()

        change_id = manager.create_change_request(
            title="Deploy New Feature",
            description="Deploy user profile feature",
            requested_by="Product Team",
            risk_level=ChangeRiskLevel.MEDIUM,
            affected_systems=["Web App", "API"],
            rollback_plan="Revert deployment",
            testing_plan="QA testing in staging",
        )

        assert change_id is not None
        assert change_id in manager.changes

    def test_approve_change(self):
        """Test approving change request"""
        manager = ChangeManager()

        change_id = manager.create_change_request(
            title="Change", description="Desc", requested_by="Team", risk_level=ChangeRiskLevel.LOW, affected_systems=["S"], rollback_plan="R", testing_plan="T"
        )

        manager.approve_change(change_id, approved_by="CAB Lead")

        change = manager.changes[change_id]
        assert change.approved is True
        assert change.approved_by == "CAB Lead"

    def test_implement_change(self):
        """Test implementing change"""
        manager = ChangeManager()

        change_id = manager.create_change_request(
            title="Change", description="Desc", requested_by="Team", risk_level=ChangeRiskLevel.LOW, affected_systems=["S"], rollback_plan="R", testing_plan="T"
        )

        manager.approve_change(change_id, approved_by="CAB")
        manager.implement_change(change_id)

        change = manager.changes[change_id]
        assert change.implemented is True
        assert change.implemented_at is not None

    def test_get_pending_changes(self):
        """Test getting pending change requests"""
        manager = ChangeManager()

        # Pending change
        manager.create_change_request(
            title="Pending", description="D", requested_by="T", risk_level=ChangeRiskLevel.LOW, affected_systems=["S"], rollback_plan="R", testing_plan="T"
        )

        # Approved change
        chg_id = manager.create_change_request(
            title="Approved", description="D", requested_by="T", risk_level=ChangeRiskLevel.LOW, affected_systems=["S"], rollback_plan="R", testing_plan="T"
        )
        manager.approve_change(chg_id, "CAB")

        pending = [c for c in manager.changes.values() if not c.approved]

        assert len(pending) == 1


@pytest.mark.medium
class TestSOC2ComplianceEngine:
    """Test SOC 2 Compliance Engine"""

    def test_engine_initialization(self):
        """Test SOC 2 engine initialization"""
        engine = SOC2ComplianceEngine()

        assert engine.security_controls is not None
        assert engine.availability_controls is not None
        assert engine.pi_controls is not None
        assert engine.confidentiality_controls is not None
        assert engine.privacy_controls is not None

    def test_register_vendor(self):
        """Test registering vendor"""
        engine = SOC2ComplianceEngine()

        vendor_id = engine.register_vendor(
            name="AWS", services=["Cloud Infrastructure"], criticality="critical", data_access=True
        )

        assert vendor_id is not None
        assert vendor_id in engine.vendors

    def test_vendor_soc2_report(self):
        """Test vendor SOC 2 report tracking"""
        engine = SOC2ComplianceEngine()

        vendor_id = engine.register_vendor(
            name="Vendor", services=["Service"], criticality="high", data_access=True
        )

        # Update vendor with SOC 2 report
        vendor = engine.vendors[vendor_id]
        vendor.soc2_report = True
        vendor.soc2_report_date = datetime.now()
        vendor.last_assessment = datetime.now()

        assert vendor.soc2_report is True
        assert vendor.last_assessment is not None

    def test_collect_evidence(self):
        """Test collecting control evidence"""
        engine = SOC2ComplianceEngine()

        evidence_id = engine.collect_evidence(
            control_id="CC1.1",
            evidence_type="document",
            description="Code of conduct signed",
            collected_by="Compliance Team",
            file_path="/docs/code_of_conduct.pdf",
        )

        assert evidence_id is not None
        assert any(e.id == evidence_id for e in engine.evidence)

    def test_log_audit_event(self):
        """Test logging audit event"""
        engine = SOC2ComplianceEngine()

        engine.log_audit_event(
            user="admin", action="UPDATE", resource="user_roles", ip_address="192.168.1.1", result="success", details={"role": "admin"}
        )

        assert len(engine.audit_logs) == 1

    def test_generate_compliance_report(self):
        """Test generating overall compliance report"""
        engine = SOC2ComplianceEngine()

        report = engine.generate_compliance_report()

        assert "total_controls" in report
        assert "compliance_score" in report
        assert "controls_by_status" in report
        assert "controls_by_category" in report
        assert report["total_controls"] > 0


# =============================================================================
# LARGE TESTS - End-to-End Workflows
# =============================================================================


@pytest.mark.large
@pytest.mark.integration
class TestSOC2Workflows:
    """Test complete SOC 2 workflows"""

    def test_complete_control_testing_workflow(self):
        """Test complete control testing workflow"""
        engine = SOC2ComplianceEngine()

        # Step 1: Identify control to test
        control_id = "CC5.1"  # Logical Access Controls

        # Step 2: Collect evidence
        evidence_id1 = engine.collect_evidence(
            control_id=control_id,
            evidence_type="screenshot",
            description="RBAC configuration",
            collected_by="Auditor",
            file_path="/evidence/rbac_config.png",
        )

        evidence_id2 = engine.collect_evidence(
            control_id=control_id, evidence_type="log", description="Access logs", collected_by="Auditor", file_path="/logs/access.log"
        )

        # Step 3: Verify evidence collected
        assert any(e.id == evidence_id1 for e in engine.evidence)
        assert any(e.id == evidence_id2 for e in engine.evidence)

        # Step 4: Update control test results
        control = engine.security_controls.controls[control_id]
        control.last_tested = datetime.now()
        control.test_results = "Control operating effectively"

        # Verify workflow completed
        assert control.last_tested is not None
        assert control.test_results is not None

    def test_incident_management_workflow(self):
        """Test complete incident management workflow"""
        engine = SOC2ComplianceEngine()

        # Step 1: Incident detected
        incident_id = engine.incident_manager.create_incident(
            title="Unauthorized Access Attempt",
            description="Multiple failed login attempts detected",
            category=TrustServiceCategory.SECURITY,
            severity=IncidentSeverity.HIGH,
            affected_systems=["Authentication Service"],
            detected_by="SIEM",
        )

        # Step 2 & 3: Investigation and Resolution
        engine.incident_manager.resolve_incident(
            incident_id,
            root_cause="Brute force attack from compromised IP",
            resolution="IP blocked, MFA enforced, credentials rotated",
            lessons_learned=["Implement rate limiting", "Add IP reputation checking"],
        )

        # Step 5: Log for audit
        engine.log_audit_event(
            user="security_team", action="RESOLVE_INCIDENT", resource=f"incident_{incident_id}", ip_address="internal", result="success", details={"incident_id": incident_id}
        )

        # Verify workflow completed
        incident = engine.incident_manager.incidents[incident_id]
        assert incident.resolved_at is not None
        assert len(incident.lessons_learned) == 2

    def test_change_management_workflow(self):
        """Test complete change management workflow"""
        engine = SOC2ComplianceEngine()

        # Step 1: Submit change request
        change_id = engine.change_manager.create_change_request(
            title="Deploy Security Patch",
            description="Apply critical security patch to web servers",
            requested_by="Security Team",
            risk_level=ChangeRiskLevel.HIGH,
            affected_systems=["Web Server 1", "Web Server 2", "Load Balancer"],
            rollback_plan="Restore from snapshot, revert load balancer config",
            testing_plan="Test in staging, verify functionality, monitor logs",
        )

        # Step 2: Change approval (CAB)
        engine.change_manager.approve_change(change_id, approved_by="Change Advisory Board")

        # Step 3: Log approval
        engine.log_audit_event(
            user="CAB", action="APPROVE_CHANGE", resource=f"change_{change_id}", ip_address="internal", result="success", details={"change_id": change_id}
        )

        # Step 4: Implement change
        engine.change_manager.implement_change(change_id)

        # Step 5: Log implementation
        engine.log_audit_event(
            user="ops_team", action="IMPLEMENT_CHANGE", resource=f"change_{change_id}", ip_address="internal", result="success", details={"change_id": change_id}
        )

        # Verify workflow completed
        change = engine.change_manager.changes[change_id]
        assert change.approved is True
        assert change.implemented is True

    def test_vendor_management_workflow(self):
        """Test complete vendor management workflow"""
        engine = SOC2ComplianceEngine()

        # Step 1: Register new vendor
        vendor_id = engine.register_vendor(
            name="Cloud Security Provider",
            services=["WAF", "DDoS Protection", "Threat Intelligence"],
            criticality="critical",
            data_access=True,
        )

        # Step 2: Request SOC 2 report
        vendor = engine.vendors[vendor_id]
        assert vendor.soc2_report is False

        # Step 3: Conduct vendor assessment
        vendor.last_assessment = datetime.now()
        vendor.assessment_notes = "Vendor provides critical security services. SOC 2 Type II report requested."

        # Step 4: Receive and validate SOC 2 report
        vendor.soc2_report = True
        vendor.soc2_report_date = datetime.now()

        # Step 5: Log vendor review
        engine.log_audit_event(
            user="procurement", action="VENDOR_ASSESSMENT", resource=f"vendor_{vendor_id}", ip_address="internal", result="success", details={"vendor_id": vendor_id, "soc2_received": True}
        )

        # Verify workflow completed
        assert vendor.last_assessment is not None
        assert vendor.soc2_report is True

    def test_complete_audit_preparation_workflow(self):
        """Test complete SOC 2 audit preparation workflow"""
        engine = SOC2ComplianceEngine()

        # Step 1: Collect evidence for multiple controls
        controls_to_test = ["CC1.1", "CC5.1", "A1.1", "PI1.1", "C1.1", "P1.1"]

        for control_id in controls_to_test:
            engine.collect_evidence(
                control_id=control_id,
                evidence_type="document",
                description=f"Evidence for {control_id}",
                collected_by="Compliance Team",
                file_path=f"/evidence/{control_id}.pdf",
            )

        # Step 2: Verify all controls have evidence
        assert len(engine.evidence) == len(controls_to_test)

        # Step 3: Add vendors
        vendor1 = engine.register_vendor(name="AWS", services=["Cloud"], criticality="critical", data_access=True)
        vendor2 = engine.register_vendor(name="Datadog", services=["Monitoring"], criticality="high", data_access=False)

        # Mark vendors as having SOC 2 reports
        engine.vendors[vendor1].soc2_report = True
        engine.vendors[vendor2].soc2_report = True

        # Step 4: Generate compliance status report
        report = engine.generate_compliance_report()

        # Verify audit readiness
        assert report["total_controls"] > 0
        assert report["evidence_collected"] > 0
        assert report["vendors_managed"] == 2

    def test_multi_category_compliance_scenario(self):
        """Test compliance across all five trust service categories"""
        engine = SOC2ComplianceEngine()

        # Security
        engine.log_audit_event(user="admin", action="LOGIN", resource="system", ip_address="192.168.1.1", result="success", details={})

        # Availability
        incident_id = engine.incident_manager.create_incident(
            title="Service Degradation",
            description="High latency detected",
            category=TrustServiceCategory.AVAILABILITY,
            severity=IncidentSeverity.MEDIUM,
            affected_systems=["API"],
            detected_by="Monitoring",
        )
        engine.incident_manager.resolve_incident(
            incident_id, root_cause="High traffic load", resolution="Scaled up instances", lessons_learned=["Add auto-scaling"]
        )

        # Processing Integrity
        engine.collect_evidence(
            control_id="PI1.1", evidence_type="test_results", description="Input validation tests", collected_by="QA", file_path="/tests/validation.xml"
        )

        # Confidentiality
        engine.collect_evidence(
            control_id="C1.1", evidence_type="document", description="Data classification matrix", collected_by="Security", file_path="/docs/classification.pdf"
        )

        # Privacy
        engine.collect_evidence(
            control_id="P1.1", evidence_type="document", description="Privacy policy", collected_by="Legal", file_path="/docs/privacy_policy.pdf"
        )

        # Verify all categories addressed
        report = engine.generate_compliance_report()

        assert report["total_controls"] > 0
        assert "security" in report["controls_by_category"]
        assert "availability" in report["controls_by_category"]
        assert "processing_integrity" in report["controls_by_category"]
        assert "confidentiality" in report["controls_by_category"]
        assert "privacy" in report["controls_by_category"]
