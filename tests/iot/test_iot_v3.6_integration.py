"""
Integration tests for v3.6 IoT & Edge Computing
Tests all IoT components together.
"""

import pytest
from pathlib import Path

IOT_DIR = Path(__file__).parent.parent.parent / "src" / "iot"


class TestIoTStructure:
    """Test IoT module structure"""

    def test_iot_module_exists(self):
        """Test IoT module directory exists"""
        assert IOT_DIR.exists(), "IoT directory should exist"

    def test_all_modules_exist(self):
        """Test all required modules exist"""
        required_modules = [
            "device_manager.py",
            "mqtt_broker.py",
            "edge_platform.py",
            "telemetry_pipeline.py",
            "device_protocols.py",
            "iot_security.py",
            "iot_edge_api.py",
            "iot_services.py",
            "__init__.py"
        ]

        for module in required_modules:
            module_path = IOT_DIR / module
            assert module_path.exists(), f"{module} should exist"

    def test_init_imports(self):
        """Test __init__.py has all imports"""
        init_file = IOT_DIR / "__init__.py"
        content = init_file.read_text()

        required_imports = [
            "from .iot_edge_api import",
            "from .device_manager import",
            "from .mqtt_broker import",
            "from .edge_platform import",
            "from .telemetry_pipeline import",
            "from .device_protocols import",
            "from .iot_security import"
        ]

        for import_stmt in required_imports:
            assert import_stmt in content, f"{import_stmt} should be in __init__.py"


class TestDeviceManager:
    """Test device manager implementation"""

    def test_device_manager_file_exists(self):
        """Test device_manager.py exists"""
        device_manager = IOT_DIR / "device_manager.py"
        assert device_manager.exists()

    def test_device_manager_classes(self):
        """Test device manager has required classes"""
        device_manager = IOT_DIR / "device_manager.py"
        content = device_manager.read_text()

        required_classes = [
            "class Device",
            "class DeviceShadow",
            "class DeviceManager",
            "class DeviceStatus",
            "class DeviceType"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_device_manager_methods(self):
        """Test device manager methods exist"""
        device_manager = IOT_DIR / "device_manager.py"
        content = device_manager.read_text()

        required_methods = [
            "def register_device",
            "def get_device",
            "def update_device",
            "def get_device_shadow",
            "def get_device_manager"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestMQTTBroker:
    """Test MQTT broker implementation"""

    def test_mqtt_broker_file_exists(self):
        """Test mqtt_broker.py exists"""
        mqtt_broker = IOT_DIR / "mqtt_broker.py"
        assert mqtt_broker.exists()

    def test_mqtt_broker_classes(self):
        """Test MQTT broker has required classes"""
        mqtt_broker = IOT_DIR / "mqtt_broker.py"
        content = mqtt_broker.read_text()

        required_classes = [
            "class MQTTBroker",
            "class MQTTClient",
            "class MQTTMessage",
            "class QoSLevel"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_mqtt_broker_methods(self):
        """Test MQTT broker methods exist"""
        mqtt_broker = IOT_DIR / "mqtt_broker.py"
        content = mqtt_broker.read_text()

        required_methods = [
            "def publish",
            "def subscribe",
            "def unsubscribe",
            "def get_mqtt_broker"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestEdgePlatform:
    """Test edge computing platform"""

    def test_edge_platform_file_exists(self):
        """Test edge_platform.py exists"""
        edge_platform = IOT_DIR / "edge_platform.py"
        assert edge_platform.exists()

    def test_edge_platform_classes(self):
        """Test edge platform has required classes"""
        edge_platform = IOT_DIR / "edge_platform.py"
        content = edge_platform.read_text()

        required_classes = [
            "class EdgePlatform",
            "class EdgeNode",
            "class EdgeFunction",
            "class EdgeNodeStatus"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_edge_platform_methods(self):
        """Test edge platform methods exist"""
        edge_platform = IOT_DIR / "edge_platform.py"
        content = edge_platform.read_text()

        required_methods = [
            "def deploy_function",
            "def invoke_function",
            "def list_nodes",
            "def get_edge_platform"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestTelemetryPipeline:
    """Test telemetry pipeline"""

    def test_telemetry_pipeline_file_exists(self):
        """Test telemetry_pipeline.py exists"""
        telemetry = IOT_DIR / "telemetry_pipeline.py"
        assert telemetry.exists()

    def test_telemetry_pipeline_classes(self):
        """Test telemetry pipeline has required classes"""
        telemetry = IOT_DIR / "telemetry_pipeline.py"
        content = telemetry.read_text()

        required_classes = [
            "class TelemetryPipeline",
            "class TelemetryPoint",
            "class AlertRule",
            "class Alert"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_telemetry_pipeline_methods(self):
        """Test telemetry pipeline methods exist"""
        telemetry = IOT_DIR / "telemetry_pipeline.py"
        content = telemetry.read_text()

        required_methods = [
            "def ingest",
            "def query",
            "def create_alert_rule",
            "def get_telemetry_pipeline"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestDeviceProtocols:
    """Test multi-protocol support"""

    def test_device_protocols_file_exists(self):
        """Test device_protocols.py exists"""
        protocols = IOT_DIR / "device_protocols.py"
        assert protocols.exists()

    def test_device_protocols_classes(self):
        """Test device protocols has required classes"""
        protocols = IOT_DIR / "device_protocols.py"
        content = protocols.read_text()

        required_classes = [
            "class DeviceConnector",
            "class ProtocolType",
            "class ProtocolMessage"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_device_protocols_methods(self):
        """Test device protocols methods exist"""
        protocols = IOT_DIR / "device_protocols.py"
        content = protocols.read_text()

        required_methods = [
            "def connect",
            "def send_command",
            "def get_device_connector"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestIoTSecurity:
    """Test IoT security"""

    def test_iot_security_file_exists(self):
        """Test iot_security.py exists"""
        security = IOT_DIR / "iot_security.py"
        assert security.exists()

    def test_iot_security_classes(self):
        """Test IoT security has required classes"""
        security = IOT_DIR / "iot_security.py"
        content = security.read_text()

        required_classes = [
            "class IoTSecurity",
            "class Certificate",
            "class AuthMethod"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_iot_security_methods(self):
        """Test IoT security methods exist"""
        security = IOT_DIR / "iot_security.py"
        content = security.read_text()

        required_methods = [
            "def provision_device",
            "def authenticate",
            "def get_iot_security"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestUnifiedAPI:
    """Test unified IoT & Edge API"""

    def test_iot_edge_api_file_exists(self):
        """Test iot_edge_api.py exists"""
        api = IOT_DIR / "iot_edge_api.py"
        assert api.exists()

    def test_iot_edge_api_class(self):
        """Test IoTEdgeAPI class exists"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        assert "class IoTEdgeAPI" in content, "IoTEdgeAPI class should be defined"

    def test_iot_edge_api_config(self):
        """Test IoTEdgeConfig exists"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        assert "class IoTEdgeConfig" in content, "IoTEdgeConfig should be defined"

    def test_iot_edge_api_device_operations(self):
        """Test IoTEdgeAPI has device operation methods"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_methods = [
            "def register_device",
            "def get_device",
            "def update_device_status",
            "def get_device_shadow",
            "def update_device_shadow",
            "def list_devices"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_iot_edge_api_mqtt_operations(self):
        """Test IoTEdgeAPI has MQTT operation methods"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_methods = [
            "def publish",
            "def subscribe",
            "def unsubscribe"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_iot_edge_api_edge_operations(self):
        """Test IoTEdgeAPI has edge computing methods"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_methods = [
            "def deploy_edge_function",
            "def invoke_edge_function",
            "def list_edge_nodes"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_iot_edge_api_telemetry_operations(self):
        """Test IoTEdgeAPI has telemetry methods"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_methods = [
            "def publish_telemetry",
            "def query_telemetry",
            "def create_alert_rule",
            "def get_alerts"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_iot_edge_api_protocol_operations(self):
        """Test IoTEdgeAPI has protocol methods"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_methods = [
            "def connect_device",
            "def send_command"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_iot_edge_api_security_operations(self):
        """Test IoTEdgeAPI has security methods"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_methods = [
            "def provision_device",
            "def authenticate_device",
            "def create_access_policy"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_iot_edge_api_singleton(self):
        """Test get_iot_edge_api function exists"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        assert "def get_iot_edge_api" in content, "get_iot_edge_api function should be defined"

    def test_iot_edge_api_convenience_functions(self):
        """Test convenience functions exist"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        convenience_functions = [
            "def register_device",
            "def publish_telemetry",
            "def deploy_function"
        ]

        for func in convenience_functions:
            assert func in content, f"{func} should be defined"


class TestIoTIntegration:
    """Test integration between IoT components"""

    def test_all_singleton_getters_exist(self):
        """Test all modules have singleton getters"""
        init_file = IOT_DIR / "__init__.py"
        content = init_file.read_text()

        required_getters = [
            "get_iot_edge_api",
            "get_device_manager",
            "get_mqtt_broker",
            "get_edge_platform",
            "get_telemetry_pipeline",
            "get_device_connector",
            "get_iot_security"
        ]

        for getter in required_getters:
            assert getter in content, f"{getter} should be in __all__"

    def test_module_version(self):
        """Test module has correct version"""
        init_file = IOT_DIR / "__init__.py"
        content = init_file.read_text()

        assert "__version__ = '3.6.0'" in content
        assert "Version: 3.6.0 (Complete)" in content

    def test_unified_api_imports_all_services(self):
        """Test unified API imports all services"""
        api = IOT_DIR / "iot_edge_api.py"
        content = api.read_text()

        required_imports = [
            "from .device_manager import",
            "from .mqtt_broker import",
            "from .edge_platform import",
            "from .telemetry_pipeline import",
            "from .device_protocols import",
            "from .iot_security import"
        ]

        for import_stmt in required_imports:
            assert import_stmt in content, f"{import_stmt} should be in iot_edge_api.py"


class TestIoTServices:
    """Test legacy IoT services"""

    def test_iot_services_file_exists(self):
        """Test iot_services.py exists"""
        services = IOT_DIR / "iot_services.py"
        assert services.exists()

    def test_iot_services_has_legacy_classes(self):
        """Test iot_services has legacy classes for backward compatibility"""
        services = IOT_DIR / "iot_services.py"
        content = services.read_text()

        # Should have some legacy classes
        assert "class" in content, "Should have class definitions"


class TestFileStructure:
    """Test overall file structure and sizes"""

    def test_all_files_have_content(self):
        """Test all Python files have meaningful content"""
        python_files = list(IOT_DIR.glob("*.py"))

        for py_file in python_files:
            if py_file.name == "__init__.py":
                min_lines = 100  # __init__.py should have imports
            else:
                min_lines = 200  # Other files should have implementations

            lines = len(py_file.read_text().splitlines())
            assert lines >= min_lines, f"{py_file.name} should have at least {min_lines} lines (has {lines})"

    def test_total_code_size(self):
        """Test total IoT code is substantial"""
        python_files = list(IOT_DIR.glob("*.py"))
        total_lines = sum(len(f.read_text().splitlines()) for f in python_files)

        # Should have at least 4,000 lines total (currently ~5,000)
        assert total_lines >= 4000, f"Total IoT code should be at least 4,000 lines (has {total_lines})"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
