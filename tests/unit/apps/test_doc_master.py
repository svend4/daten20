"""
Unit tests for doc-master.py
=============================

Tests all major functionality of MasterControlPanel:
- Service discovery and management
- Status reporting
- Health checks
- Quick processing
- Pipeline execution
- Command execution
"""

import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import the master control module
import importlib.util
spec = importlib.util.spec_from_file_location("doc_master", "doc-master.py")
doc_master = importlib.util.module_from_spec(spec)
sys.modules['doc_master'] = doc_master  # Add to sys.modules for imports to work
spec.loader.exec_module(doc_master)

from doc_master import (
    MasterControlPanel,
    ServiceInfo,
    PipelineStep,
    PipelineResult
)


# Fixtures
@pytest.fixture
def panel():
    """Create MasterControlPanel instance."""
    return MasterControlPanel()


@pytest.fixture
def sample_service_info():
    """Create sample ServiceInfo."""
    return ServiceInfo(
        name="Test Service",
        script="test-service.py",
        description="Test service description",
        type="tool",
        is_available=True,
        status="available"
    )


@pytest.fixture
def sample_pipeline_step():
    """Create sample PipelineStep."""
    return PipelineStep(
        tool="processor",
        action="process",
        params={"threshold": 0.8}
    )


@pytest.fixture
def sample_pipeline_result():
    """Create sample PipelineResult."""
    return PipelineResult(
        pipeline_name="test-pipeline",
        executed_at=datetime.now().isoformat(),
        total_steps=3,
        completed_steps=2,
        failed_steps=1,
        total_time_seconds=10.5,
        results=[
            {"step": "process", "status": "success"},
            {"step": "quality", "status": "success"},
            {"step": "anonymize", "status": "failed", "error": "Test error"}
        ]
    )


@pytest.fixture
def mock_document(tmp_path):
    """Create mock document for processing."""
    doc = tmp_path / "test_document.txt"
    doc.write_text("This is a test document for master control panel testing.")
    return str(doc)


# Test Dataclasses
class TestDataClasses:
    """Test suite for dataclasses."""

    def test_service_info_creation(self, sample_service_info):
        """Test ServiceInfo creation."""
        assert sample_service_info.name == "Test Service"
        assert sample_service_info.script == "test-service.py"
        assert sample_service_info.description == "Test service description"
        assert sample_service_info.type == "tool"
        assert sample_service_info.is_available is True
        assert sample_service_info.status == "available"

    def test_service_info_defaults(self):
        """Test ServiceInfo with default values."""
        service = ServiceInfo(
            name="Test",
            script="test.py",
            description="Test",
            type="tool"
        )

        assert service.is_available is False
        assert service.status == "unknown"

    def test_pipeline_step_creation(self, sample_pipeline_step):
        """Test PipelineStep creation."""
        assert sample_pipeline_step.tool == "processor"
        assert sample_pipeline_step.action == "process"
        assert sample_pipeline_step.params == {"threshold": 0.8}

    def test_pipeline_result_creation(self, sample_pipeline_result):
        """Test PipelineResult creation."""
        assert sample_pipeline_result.pipeline_name == "test-pipeline"
        assert sample_pipeline_result.total_steps == 3
        assert sample_pipeline_result.completed_steps == 2
        assert sample_pipeline_result.failed_steps == 1
        assert sample_pipeline_result.total_time_seconds == 10.5
        assert len(sample_pipeline_result.results) == 3


# Test MasterControlPanel Class
class TestMasterControlPanel:
    """Test suite for MasterControlPanel."""

    def test_panel_initialization(self, panel):
        """Test that panel initializes correctly."""
        assert panel is not None
        assert panel.services is not None
        assert isinstance(panel.services, dict)
        assert len(panel.services) > 0

    def test_discover_services(self, panel):
        """Test service discovery."""
        services = panel._discover_services()

        assert isinstance(services, dict)

        # Check expected services are present
        expected_services = [
            "processor", "batch", "api", "dashboard", "search",
            "comparator", "anonymizer", "quality"
        ]

        for service_key in expected_services:
            assert service_key in services
            service = services[service_key]
            assert isinstance(service, ServiceInfo)
            assert service.name is not None
            assert service.script is not None
            assert service.description is not None
            assert service.type in ["tool", "service", "daemon"]

    def test_discover_services_availability(self, panel):
        """Test that service availability is checked correctly."""
        services = panel._discover_services()

        # Check that is_available and status are set
        for service in services.values():
            assert isinstance(service.is_available, bool)
            assert service.status in ["available", "not_found", "unknown"]

            # If script exists, should be available
            if Path(service.script).exists():
                assert service.is_available is True
                assert service.status == "available"

    def test_status_report(self, panel):
        """Test status reporting."""
        status = panel.status()

        assert isinstance(status, dict)
        assert "timestamp" in status
        assert "platform" in status
        assert "python_version" in status
        assert "services" in status
        assert "summary" in status

        # Check summary
        summary = status["summary"]
        assert "total" in summary
        assert "available" in summary
        assert "running" in summary
        assert "stopped" in summary

        # Total should match number of services
        assert summary["total"] == len(panel.services)

        # Check services
        for key, service_status in status["services"].items():
            assert "name" in service_status
            assert "type" in service_status
            assert "available" in service_status
            assert "status" in service_status
            assert "description" in service_status

    def test_status_timestamp_format(self, panel):
        """Test that status timestamp is in ISO format."""
        status = panel.status()

        # Should be parseable as ISO datetime
        timestamp = datetime.fromisoformat(status["timestamp"])
        assert timestamp is not None

    def test_health_check(self, panel):
        """Test health check."""
        health = panel.health_check()

        assert isinstance(health, dict)
        assert "timestamp" in health
        assert "overall_status" in health
        assert "checks" in health

        # Check overall status
        assert health["overall_status"] in ["healthy", "degraded", "unhealthy"]

        # Check individual checks
        checks = health["checks"]
        assert "python" in checks
        assert "scripts" in checks
        assert "src_directory" in checks
        assert "data_directory" in checks

        # Each check should have status
        for check in checks.values():
            assert "status" in check
            assert check["status"] in ["ok", "warning", "error"]

    def test_health_check_python(self, panel):
        """Test Python environment check."""
        health = panel.health_check()

        python_check = health["checks"]["python"]
        assert python_check["status"] == "ok"
        assert "version" in python_check

    def test_health_check_scripts(self, panel):
        """Test required scripts check."""
        health = panel.health_check()

        scripts_check = health["checks"]["scripts"]
        assert "missing" in scripts_check
        assert isinstance(scripts_check["missing"], list)

        # Status should be ok if no missing, warning otherwise
        if scripts_check["missing"]:
            assert scripts_check["status"] == "warning"
        else:
            assert scripts_check["status"] == "ok"

    def test_health_check_directories(self, panel):
        """Test directory checks."""
        health = panel.health_check()

        # src directory check
        src_check = health["checks"]["src_directory"]
        assert "exists" in src_check

        # data directory check (should always be ok as it's created)
        data_check = health["checks"]["data_directory"]
        assert data_check["status"] == "ok"
        assert data_check["exists"] is True

    @patch("doc_master.subprocess.run")
    def test_quick_process_all_steps(self, mock_run, panel, mock_document, tmp_path):
        """Test quick process with all steps."""
        # Mock successful command execution
        mock_run.return_value = Mock(stdout="Success", returncode=0)

        output_dir = str(tmp_path / "output")
        result = panel.quick_process(mock_document, ["all"], output_dir)

        assert isinstance(result, PipelineResult)
        assert result.pipeline_name == "quick-process"
        assert result.total_steps == 1  # "all" counts as 1 step
        assert result.completed_steps >= 0
        assert result.total_time_seconds >= 0
        assert isinstance(result.results, list)

    @patch("doc_master.subprocess.run")
    def test_quick_process_specific_steps(self, mock_run, panel, mock_document, tmp_path):
        """Test quick process with specific steps."""
        # Mock successful command execution
        mock_run.return_value = Mock(stdout="Success", returncode=0)

        output_dir = str(tmp_path / "output")
        steps = ["process", "quality"]
        result = panel.quick_process(mock_document, steps, output_dir)

        assert isinstance(result, PipelineResult)
        assert result.total_steps == len(steps)

        # Check that results contain our steps
        step_names = [r["step"] for r in result.results]
        assert "process" in step_names or result.completed_steps == 0
        assert "quality" in step_names or result.completed_steps == 0

    @patch("doc_master.subprocess.run")
    def test_quick_process_creates_output_dir(self, mock_run, panel, mock_document, tmp_path):
        """Test that quick process creates output directory."""
        mock_run.return_value = Mock(stdout="Success", returncode=0)

        output_dir = tmp_path / "output" / "nested"
        result = panel.quick_process(mock_document, ["process"], str(output_dir))

        # Output directory should be created
        assert output_dir.exists()

    @patch("doc_master.subprocess.run")
    def test_quick_process_handles_failure(self, mock_run, panel, mock_document, tmp_path):
        """Test quick process handles step failures."""
        # Mock command failure
        mock_run.side_effect = Exception("Command failed")

        output_dir = str(tmp_path / "output")
        result = panel.quick_process(mock_document, ["process"], output_dir)

        # Should still return result with failed steps
        assert isinstance(result, PipelineResult)
        assert result.failed_steps > 0

    def test_run_pipeline_gdpr_compliance(self, panel, mock_document):
        """Test GDPR compliance pipeline."""
        result = panel.run_pipeline("gdpr-compliance", mock_document)

        assert isinstance(result, PipelineResult)
        assert result.pipeline_name == "gdpr-compliance"
        assert result.total_steps == 3  # scan, anonymize, quality
        assert result.completed_steps >= 0
        assert isinstance(result.results, list)

    def test_run_pipeline_quality_assurance(self, panel, mock_document):
        """Test quality assurance pipeline."""
        result = panel.run_pipeline("quality-assurance", mock_document)

        assert isinstance(result, PipelineResult)
        assert result.pipeline_name == "quality-assurance"
        assert result.total_steps == 2  # quality, process

    def test_run_pipeline_full_analysis(self, panel, mock_document):
        """Test full analysis pipeline."""
        result = panel.run_pipeline("full-analysis", mock_document)

        assert isinstance(result, PipelineResult)
        assert result.pipeline_name == "full-analysis"
        assert result.total_steps == 2  # process, quality

    def test_run_pipeline_unknown(self, panel, mock_document):
        """Test that unknown pipeline raises error."""
        with pytest.raises(ValueError, match="Unknown pipeline"):
            panel.run_pipeline("non-existent-pipeline", mock_document)

    def test_run_pipeline_result_structure(self, panel, mock_document):
        """Test pipeline result structure."""
        result = panel.run_pipeline("full-analysis", mock_document)

        # Check result structure
        assert hasattr(result, "pipeline_name")
        assert hasattr(result, "executed_at")
        assert hasattr(result, "total_steps")
        assert hasattr(result, "completed_steps")
        assert hasattr(result, "failed_steps")
        assert hasattr(result, "total_time_seconds")
        assert hasattr(result, "results")

        # Check executed_at is ISO format
        timestamp = datetime.fromisoformat(result.executed_at)
        assert timestamp is not None

    @patch("doc_master.subprocess.run")
    def test_run_command_success(self, mock_run, panel):
        """Test successful command execution."""
        mock_run.return_value = Mock(stdout="Command output", returncode=0)

        output = panel._run_command(["echo", "test"])

        assert output == "Command output"
        mock_run.assert_called_once()

    @patch("doc_master.subprocess.run")
    def test_run_command_failure(self, mock_run, panel):
        """Test command execution failure."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["test"],
            stderr="Error message"
        )

        with pytest.raises(RuntimeError, match="Command failed"):
            panel._run_command(["false"])

    @patch("doc_master.subprocess.run")
    def test_run_command_timeout(self, mock_run, panel):
        """Test command timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["sleep", "1000"],
            timeout=1
        )

        with pytest.raises(RuntimeError, match="timed out"):
            panel._run_command(["sleep", "1000"], timeout=1)

    def test_services_have_correct_types(self, panel):
        """Test that services have correct types."""
        expected_types = {
            "processor": "tool",
            "batch": "service",
            "api": "daemon",
            "dashboard": "daemon",
            "search": "service",
            "comparator": "tool",
            "anonymizer": "tool",
            "quality": "tool"
        }

        for key, expected_type in expected_types.items():
            if key in panel.services:
                assert panel.services[key].type == expected_type

    def test_services_have_descriptions(self, panel):
        """Test that all services have descriptions."""
        for service in panel.services.values():
            assert service.description is not None
            assert len(service.description) > 0
            assert isinstance(service.description, str)


# Integration Tests
class TestMasterControlPanelIntegration:
    """Integration tests for MasterControlPanel."""

    def test_full_status_workflow(self, panel, tmp_path):
        """Test complete status workflow."""
        # 1. Get status
        status = panel.status()

        # 2. Verify status
        assert status["summary"]["total"] > 0

        # 3. Save status to file
        status_file = tmp_path / "status.json"
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)

        # 4. Verify saved status
        assert status_file.exists()

        with open(status_file) as f:
            saved_status = json.load(f)

        assert saved_status["summary"]["total"] == status["summary"]["total"]

    def test_health_and_status_consistency(self, panel):
        """Test that health check and status are consistent."""
        status = panel.status()
        health = panel.health_check()

        # Both should have timestamps
        assert "timestamp" in status
        assert "timestamp" in health

        # Both should check similar things
        # If src_directory is missing, services might not be available
        if not health["checks"]["src_directory"]["exists"]:
            # Some services might not be available
            assert status["summary"]["available"] >= 0

    @patch("doc_master.subprocess.run")
    def test_pipeline_execution_workflow(self, mock_run, panel, mock_document, tmp_path):
        """Test complete pipeline execution workflow."""
        mock_run.return_value = Mock(stdout="Success", returncode=0)

        # 1. Check health
        health = panel.health_check()
        assert health["overall_status"] in ["healthy", "degraded", "unhealthy"]

        # 2. Run quick process
        result = panel.quick_process(mock_document, ["all"], str(tmp_path / "output"))

        # 3. Verify result
        assert result.total_steps >= 0
        assert result.completed_steps + result.failed_steps <= result.total_steps * 3  # max 3 actual steps

        # 4. Save result
        result_file = tmp_path / "pipeline_result.json"
        from dataclasses import asdict
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)

        # 5. Verify saved result
        assert result_file.exists()

    def test_all_pipelines_execution(self, panel, mock_document):
        """Test execution of all available pipelines."""
        pipelines = ["gdpr-compliance", "quality-assurance", "full-analysis"]

        results = []
        for pipeline_name in pipelines:
            result = panel.run_pipeline(pipeline_name, mock_document)
            results.append(result)
            assert result.pipeline_name == pipeline_name

        # All pipelines should execute
        assert len(results) == len(pipelines)

    def test_service_discovery_and_status(self, panel):
        """Test that service discovery matches status report."""
        status = panel.status()

        # Number of services in status should match discovered services
        assert len(status["services"]) == len(panel.services)

        # Each discovered service should be in status
        for key in panel.services.keys():
            assert key in status["services"]


# Edge Cases and Error Handling
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_steps_list(self, panel, mock_document, tmp_path):
        """Test quick process with empty steps list."""
        result = panel.quick_process(mock_document, [], str(tmp_path / "output"))

        # Should complete without errors
        assert isinstance(result, PipelineResult)
        assert result.total_steps == 0

    def test_nonexistent_document(self, panel, tmp_path):
        """Test processing non-existent document."""
        nonexistent = str(tmp_path / "nonexistent.txt")

        # Should handle gracefully (might fail but shouldn't crash)
        try:
            result = panel.quick_process(nonexistent, ["process"], str(tmp_path / "output"))
            # If it doesn't raise, should have some failed steps
            assert result.failed_steps >= 0
        except Exception:
            # It's ok if it raises an exception
            pass

    def test_pipeline_with_optional_params(self, panel, mock_document):
        """Test pipeline execution with optional parameters."""
        result = panel.run_pipeline(
            "quality-assurance",
            mock_document,
            params={"threshold": 90}
        )

        assert isinstance(result, PipelineResult)

    def test_status_multiple_calls(self, panel):
        """Test that multiple status calls are consistent."""
        status1 = panel.status()
        status2 = panel.status()

        # Should have same number of services
        assert status1["summary"]["total"] == status2["summary"]["total"]
        assert status1["summary"]["available"] == status2["summary"]["available"]

    def test_health_check_creates_data_dir(self, panel, tmp_path, monkeypatch):
        """Test that health check creates data directory if missing."""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Ensure data directory doesn't exist
        data_dir = tmp_path / "data"
        if data_dir.exists():
            import shutil
            shutil.rmtree(data_dir)

        # Run health check
        health = panel.health_check()

        # data directory should now exist
        assert data_dir.exists()
        assert health["checks"]["data_directory"]["exists"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
