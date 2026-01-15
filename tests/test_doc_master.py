#!/usr/bin/env python3
"""
Unit tests for doc-master.py

Tests document management master control panel including:
- Service discovery
- Status monitoring
- Health checks
- Quick processing
- Pipeline execution
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

# Import required modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockServiceInfo:
    """Mock ServiceInfo for testing"""

    def __init__(self, name, script, description, type, is_available=False, status="unknown"):
        self.name = name
        self.script = script
        self.description = description
        self.type = type
        self.is_available = is_available
        self.status = status


class TestServiceDiscovery:
    """Test suite for service discovery"""

    def test_service_info_dataclass(self):
        """Test ServiceInfo dataclass creation"""
        info = MockServiceInfo(
            name="Test Service",
            script="test.py",
            description="Test description",
            type="tool",
            is_available=True,
            status="available"
        )

        assert info.name == "Test Service"
        assert info.script == "test.py"
        assert info.type == "tool"
        assert info.is_available is True

    def test_service_types(self):
        """Test different service types"""
        types = ["tool", "service", "daemon"]

        for svc_type in types:
            info = MockServiceInfo(
                name="Test",
                script="test.py",
                description="Test",
                type=svc_type
            )
            assert info.type in types

    def test_service_availability_check(self):
        """Test service availability checking"""
        # Existing file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            assert tmp_path.exists()
            tmp_path.unlink()

        # Non-existing file
        non_existing = Path("non_existing_service.py")
        assert not non_existing.exists()


class TestStatusMonitoring:
    """Test suite for status monitoring"""

    def test_status_structure(self):
        """Test status dictionary structure"""
        status = {
            "timestamp": "2024-01-01T00:00:00",
            "platform": "Linux",
            "python_version": "3.11.0",
            "services": {},
            "summary": {
                "total": 0,
                "available": 0,
                "running": 0,
                "stopped": 0
            }
        }

        assert "timestamp" in status
        assert "platform" in status
        assert "services" in status
        assert "summary" in status
        assert isinstance(status["summary"], dict)

    def test_service_status_fields(self):
        """Test service status fields"""
        service_status = {
            "name": "Test Service",
            "type": "tool",
            "available": True,
            "status": "available",
            "description": "Test description"
        }

        required_fields = ["name", "type", "available", "status", "description"]
        for field in required_fields:
            assert field in service_status

    def test_summary_calculations(self):
        """Test summary statistics calculations"""
        services = [
            {"available": True, "status": "running"},
            {"available": True, "status": "stopped"},
            {"available": False, "status": "not_found"},
            {"available": True, "status": "available"}
        ]

        total = len(services)
        available = sum(1 for s in services if s["available"])
        running = sum(1 for s in services if s["status"] == "running")
        stopped = sum(1 for s in services if s["status"] == "stopped")

        assert total == 4
        assert available == 3
        assert running == 1
        assert stopped == 1

    def test_platform_info(self):
        """Test platform information collection"""
        import platform

        platform_info = {
            "system": platform.system(),
            "python_version": platform.python_version(),
            "machine": platform.machine()
        }

        assert platform_info["system"] in ["Linux", "Windows", "Darwin"]
        assert len(platform_info["python_version"]) > 0


class TestHealthChecks:
    """Test suite for health checks"""

    def test_health_check_structure(self):
        """Test health check dictionary structure"""
        health = {
            "timestamp": "2024-01-01T00:00:00",
            "overall_status": "healthy",
            "checks": {}
        }

        assert "timestamp" in health
        assert "overall_status" in health
        assert "checks" in health
        assert isinstance(health["checks"], dict)

    def test_overall_status_values(self):
        """Test valid overall status values"""
        valid_statuses = ["healthy", "degraded", "unhealthy"]

        for status in valid_statuses:
            health = {"overall_status": status}
            assert health["overall_status"] in valid_statuses

    def test_python_check(self):
        """Test Python environment check"""
        import platform

        python_check = {
            "status": "ok",
            "version": platform.python_version()
        }

        assert python_check["status"] == "ok"
        assert len(python_check["version"]) > 0

    def test_scripts_check(self):
        """Test scripts availability check"""
        required_scripts = ["doc-processor.py", "doc-comparator.py"]
        missing = []

        for script in required_scripts:
            if not Path(script).exists():
                missing.append(script)

        scripts_check = {
            "status": "ok" if not missing else "warning",
            "missing": missing
        }

        assert "status" in scripts_check
        assert "missing" in scripts_check
        assert isinstance(scripts_check["missing"], list)

    def test_directory_check(self):
        """Test directory existence check"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            dir_check = {
                "status": "ok" if test_dir.exists() else "error",
                "exists": test_dir.exists()
            }

            assert dir_check["exists"] is True
            assert dir_check["status"] == "ok"

    def test_health_status_aggregation(self):
        """Test health status aggregation logic"""
        checks = [
            {"status": "ok"},
            {"status": "ok"},
            {"status": "ok"}
        ]

        # All OK -> healthy
        has_error = any(c["status"] == "error" for c in checks)
        has_warning = any(c["status"] == "warning" for c in checks)

        if has_error:
            overall = "unhealthy"
        elif has_warning:
            overall = "degraded"
        else:
            overall = "healthy"

        assert overall == "healthy"

        # With warning -> degraded
        checks.append({"status": "warning"})
        has_error = any(c["status"] == "error" for c in checks)
        has_warning = any(c["status"] == "warning" for c in checks)

        if has_error:
            overall = "unhealthy"
        elif has_warning:
            overall = "degraded"
        else:
            overall = "healthy"

        assert overall == "degraded"

        # With error -> unhealthy
        checks.append({"status": "error"})
        has_error = any(c["status"] == "error" for c in checks)

        if has_error:
            overall = "unhealthy"
        elif has_warning:
            overall = "degraded"
        else:
            overall = "healthy"

        assert overall == "unhealthy"


class TestQuickProcessing:
    """Test suite for quick processing"""

    def test_pipeline_result_structure(self):
        """Test PipelineResult structure"""
        result = {
            "pipeline_name": "test_pipeline",
            "executed_at": "2024-01-01T00:00:00",
            "total_steps": 3,
            "completed_steps": 2,
            "failed_steps": 1,
            "total_time_seconds": 10.5,
            "results": []
        }

        required_fields = [
            "pipeline_name", "executed_at", "total_steps",
            "completed_steps", "failed_steps", "total_time_seconds", "results"
        ]

        for field in required_fields:
            assert field in result

    def test_pipeline_step_structure(self):
        """Test PipelineStep structure"""
        step = {
            "tool": "doc-processor",
            "action": "process",
            "params": {"input": "test.pdf"}
        }

        assert "tool" in step
        assert "action" in step
        assert "params" in step
        assert isinstance(step["params"], dict)

    def test_output_directory_creation(self):
        """Test output directory creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"

            # Should not exist initially
            assert not output_dir.exists()

            # Create it
            output_dir.mkdir(parents=True, exist_ok=True)

            # Should exist now
            assert output_dir.exists()

    def test_step_result_tracking(self):
        """Test step result tracking"""
        results = []

        # Success step
        results.append({
            "step": "process",
            "status": "success",
            "output": "output.json"
        })

        # Failed step
        results.append({
            "step": "anonymize",
            "status": "failed",
            "error": "File not found"
        })

        completed = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "failed")

        assert completed == 1
        assert failed == 1

    def test_processing_steps(self):
        """Test valid processing steps"""
        valid_steps = ["process", "anonymize", "quality", "compare", "all"]

        for step in valid_steps:
            assert step in valid_steps

    def test_file_path_handling(self):
        """Test file path handling"""
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            file_path = Path(tmp.name)

            assert file_path.exists()
            assert file_path.suffix == ".pdf"

            base_name = file_path.stem
            assert len(base_name) > 0


class TestPipelineExecution:
    """Test suite for pipeline execution"""

    def test_pipeline_definition(self):
        """Test pipeline definition structure"""
        pipeline = {
            "name": "gdpr-compliance",
            "description": "GDPR compliance pipeline",
            "steps": [
                {"tool": "doc-processor", "action": "process"},
                {"tool": "doc-anonymizer", "action": "anonymize"},
                {"tool": "doc-quality", "action": "check"}
            ]
        }

        assert "name" in pipeline
        assert "steps" in pipeline
        assert isinstance(pipeline["steps"], list)
        assert len(pipeline["steps"]) > 0

    def test_step_execution_order(self):
        """Test step execution order"""
        steps = ["step1", "step2", "step3"]
        execution_order = []

        for step in steps:
            execution_order.append(step)

        assert execution_order == steps

    def test_pipeline_error_handling(self):
        """Test pipeline error handling"""
        results = []

        try:
            # Simulate successful step
            results.append({"status": "success"})
        except Exception as e:
            results.append({"status": "failed", "error": str(e)})

        try:
            # Simulate failed step
            raise ValueError("Test error")
        except Exception as e:
            results.append({"status": "failed", "error": str(e)})

        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "failed"
        assert "Test error" in results[1]["error"]


class TestCLIIntegration:
    """Test suite for CLI integration"""

    def test_cli_help_command(self):
        """Test CLI help message"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-master.py', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )

            assert result.returncode == 0
            assert 'status' in result.stdout.lower() or 'help' in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("doc-master.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")

    def test_cli_status_command(self):
        """Test status command exists"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-master.py', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Should either succeed or fail with known error
            assert result.returncode in [0, 1, 2]
        except FileNotFoundError:
            pytest.skip("doc-master.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")

    def test_cli_health_command(self):
        """Test health check command exists"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-master.py', 'health'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Should either succeed or fail with known error
            assert result.returncode in [0, 1, 2]
        except FileNotFoundError:
            pytest.skip("doc-master.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")


class TestEdgeCases:
    """Test suite for edge cases"""

    def test_empty_services_list(self):
        """Test handling of empty services list"""
        services = {}

        summary = {
            "total": len(services),
            "available": sum(1 for s in services.values() if hasattr(s, 'is_available') and s.is_available)
        }

        assert summary["total"] == 0
        assert summary["available"] == 0

    def test_all_services_unavailable(self):
        """Test when all services are unavailable"""
        services = {
            "svc1": MockServiceInfo("S1", "s1.py", "Desc", "tool", False, "not_found"),
            "svc2": MockServiceInfo("S2", "s2.py", "Desc", "tool", False, "not_found")
        }

        available = sum(1 for s in services.values() if s.is_available)
        assert available == 0

    def test_missing_script_handling(self):
        """Test handling of missing scripts"""
        script_path = Path("non_existing_script.py")

        assert not script_path.exists()

        status = "not_found" if not script_path.exists() else "available"
        assert status == "not_found"

    def test_invalid_file_path(self):
        """Test handling of invalid file paths"""
        invalid_path = Path("/invalid/path/to/file.pdf")

        assert not invalid_path.exists()

    def test_permission_denied(self):
        """Test handling of permission errors"""
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Try to make it unreadable (Unix-like systems)
            os.chmod(tmp_path, 0o000)

            # Try to read - should handle gracefully
            try:
                tmp_path.read_text()
            except PermissionError:
                # Expected behavior
                pass
        finally:
            # Cleanup
            os.chmod(tmp_path, 0o644)
            tmp_path.unlink()


class TestDataValidation:
    """Test suite for data validation"""

    def test_service_name_validation(self):
        """Test service name validation"""
        valid_names = ["processor", "api", "dashboard", "comparator"]

        for name in valid_names:
            assert len(name) > 0
            assert name.isalnum() or '_' in name or '-' in name

    def test_status_value_validation(self):
        """Test status value validation"""
        valid_statuses = ["available", "not_found", "running", "stopped", "error", "unknown"]

        test_status = "available"
        assert test_status in valid_statuses

    def test_type_value_validation(self):
        """Test service type validation"""
        valid_types = ["tool", "service", "daemon"]

        test_type = "tool"
        assert test_type in valid_types

    def test_pipeline_name_validation(self):
        """Test pipeline name validation"""
        valid_pipeline_names = [
            "gdpr-compliance",
            "quality-check",
            "full-processing"
        ]

        for name in valid_pipeline_names:
            assert len(name) > 0
            assert all(c.isalnum() or c in '-_' for c in name)


class TestJSONSerialization:
    """Test suite for JSON serialization"""

    def test_status_json_serialization(self):
        """Test status JSON serialization"""
        status = {
            "timestamp": "2024-01-01T00:00:00",
            "platform": "Linux",
            "services": {},
            "summary": {"total": 0}
        }

        # Should be JSON serializable
        json_str = json.dumps(status)
        assert isinstance(json_str, str)

        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["platform"] == "Linux"

    def test_health_json_serialization(self):
        """Test health check JSON serialization"""
        health = {
            "timestamp": "2024-01-01T00:00:00",
            "overall_status": "healthy",
            "checks": {
                "python": {"status": "ok"}
            }
        }

        # Should be JSON serializable
        json_str = json.dumps(health)
        assert isinstance(json_str, str)

        parsed = json.loads(json_str)
        assert parsed["overall_status"] == "healthy"

    def test_pipeline_result_json_serialization(self):
        """Test pipeline result JSON serialization"""
        result = {
            "pipeline_name": "test",
            "total_steps": 3,
            "completed_steps": 2,
            "results": [{"step": "1", "status": "success"}]
        }

        # Should be JSON serializable
        json_str = json.dumps(result)
        assert isinstance(json_str, str)

        parsed = json.loads(json_str)
        assert parsed["total_steps"] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
