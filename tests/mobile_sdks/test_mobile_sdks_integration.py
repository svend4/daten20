"""
Integration tests for v3.3 Mobile & Cross-Platform SDKs
Tests verify SDK structure, configuration files, and basic functionality.
"""

import pytest
import os
import json
from pathlib import Path

# Base mobile SDKs directory
MOBILE_SDKS_DIR = Path(__file__).parent.parent.parent / "mobile_sdks"


class TestiOSSDK:
    """Tests for iOS SDK (Swift)"""

    def test_ios_structure_exists(self):
        """Test iOS SDK directory structure"""
        ios_dir = MOBILE_SDKS_DIR / "ios"
        assert ios_dir.exists(), "iOS SDK directory should exist"
        assert (ios_dir / "Package.swift").exists(), "Package.swift should exist"

    def test_ios_sources_exist(self):
        """Test iOS source files exist"""
        sources_dir = MOBILE_SDKS_DIR / "ios" / "Sources" / "DMSSDK"
        assert sources_dir.exists(), "iOS Sources directory should exist"
        assert (sources_dir / "DMSClient.swift").exists(), "DMSClient.swift should exist"
        assert (sources_dir / "Models.swift").exists(), "Models.swift should exist"

    def test_ios_client_implementation(self):
        """Test iOS client has required implementation"""
        client_file = MOBILE_SDKS_DIR / "ios" / "Sources" / "DMSSDK" / "DMSClient.swift"
        content = client_file.read_text()

        # Check for key features
        assert "class DMSClient" in content, "DMSClient class should be defined"
        assert "func configure" in content, "Configure method should exist"
        assert "func login" in content, "Login method should exist"
        assert "func getDocuments" in content, "GetDocuments method should exist"
        assert "func uploadDocument" in content, "UploadDocument method should exist"
        assert "func downloadDocument" in content, "DownloadDocument method should exist"
        assert "func connectWebSocket" in content, "ConnectWebSocket method should exist"

    def test_ios_models_implementation(self):
        """Test iOS models are properly defined"""
        models_file = MOBILE_SDKS_DIR / "ios" / "Sources" / "DMSSDK" / "Models.swift"
        content = models_file.read_text()

        # Check for key models
        assert "struct AuthResponse" in content, "AuthResponse model should be defined"
        assert "struct User" in content, "User model should be defined"
        assert "struct Document" in content, "Document model should be defined"
        assert "enum DocumentStatus" in content, "DocumentStatus enum should be defined"
        assert "struct DashboardResponse" in content, "DashboardResponse model should be defined"
        assert "struct Notification" in content, "Notification model should be defined"


class TestAndroidSDK:
    """Tests for Android SDK (Kotlin)"""

    def test_android_structure_exists(self):
        """Test Android SDK directory structure"""
        android_dir = MOBILE_SDKS_DIR / "android"
        assert android_dir.exists(), "Android SDK directory should exist"
        assert (android_dir / "build.gradle.kts").exists(), "build.gradle.kts should exist"

    def test_android_sources_exist(self):
        """Test Android source files exist"""
        sources_dir = MOBILE_SDKS_DIR / "android" / "src" / "main" / "kotlin" / "com" / "example" / "dms_sdk"
        assert sources_dir.exists(), "Android sources directory should exist"
        assert (sources_dir / "DMSClient.kt").exists(), "DMSClient.kt should exist"
        assert (sources_dir / "Models.kt").exists(), "Models.kt should exist"

    def test_android_client_implementation(self):
        """Test Android client has required implementation"""
        client_file = MOBILE_SDKS_DIR / "android" / "src" / "main" / "kotlin" / "com" / "example" / "dms_sdk" / "DMSClient.kt"
        content = client_file.read_text()

        # Check for key features
        assert "class DMSClient" in content, "DMSClient class should be defined"
        assert "fun configure" in content, "Configure method should exist"
        assert "suspend fun login" in content, "Login method should exist"
        assert "suspend fun getDocuments" in content, "GetDocuments method should exist"
        assert "suspend fun uploadDocument" in content, "UploadDocument method should exist"
        assert "suspend fun downloadDocument" in content, "DownloadDocument method should exist"
        assert "fun connectWebSocket" in content, "ConnectWebSocket method should exist"

    def test_android_models_implementation(self):
        """Test Android models are properly defined"""
        models_file = MOBILE_SDKS_DIR / "android" / "src" / "main" / "kotlin" / "com" / "example" / "dms_sdk" / "Models.kt"
        content = models_file.read_text()

        # Check for key models
        assert "data class AuthResponse" in content, "AuthResponse model should be defined"
        assert "data class User" in content, "User model should be defined"
        assert "data class Document" in content, "Document model should be defined"
        assert "enum class DocumentStatus" in content, "DocumentStatus enum should be defined"
        assert "data class DashboardResponse" in content, "DashboardResponse model should be defined"
        assert "data class Notification" in content, "Notification model should be defined"


class TestReactNativeSDK:
    """Tests for React Native SDK (TypeScript)"""

    def test_react_native_structure_exists(self):
        """Test React Native SDK directory structure"""
        rn_dir = MOBILE_SDKS_DIR / "react_native"
        assert rn_dir.exists(), "React Native SDK directory should exist"
        assert (rn_dir / "package.json").exists(), "package.json should exist"

    def test_react_native_sources_exist(self):
        """Test React Native source files exist"""
        src_dir = MOBILE_SDKS_DIR / "react_native" / "src"
        assert src_dir.exists(), "React Native src directory should exist"
        assert (src_dir / "DMSClient.ts").exists(), "DMSClient.ts should exist"
        assert (src_dir / "types.ts").exists(), "types.ts should exist"

    def test_react_native_package_json(self):
        """Test package.json configuration"""
        package_file = MOBILE_SDKS_DIR / "react_native" / "package.json"
        with open(package_file) as f:
            package_data = json.load(f)

        assert package_data["name"] == "@dms/react-native-sdk", "Package name should be correct"
        assert "version" in package_data, "Package should have version"
        assert "main" in package_data, "Package should have main entry"

    def test_react_native_client_implementation(self):
        """Test React Native client has required implementation"""
        client_file = MOBILE_SDKS_DIR / "react_native" / "src" / "DMSClient.ts"
        content = client_file.read_text()

        # Check for key features
        assert "class DMSClient" in content, "DMSClient class should be defined"
        assert "configure" in content, "Configure method should exist"
        assert "login" in content, "Login method should exist"
        assert "getDocuments" in content, "GetDocuments method should exist"
        assert "uploadDocument" in content, "UploadDocument method should exist"
        assert "downloadDocument" in content, "DownloadDocument method should exist"
        assert "connectWebSocket" in content, "ConnectWebSocket method should exist"

    def test_react_native_types_implementation(self):
        """Test React Native types are properly defined"""
        types_file = MOBILE_SDKS_DIR / "react_native" / "src" / "types.ts"
        content = types_file.read_text()

        # Check for key types
        assert "interface AuthResponse" in content, "AuthResponse interface should be defined"
        assert "interface User" in content, "User interface should be defined"
        assert "interface Document" in content, "Document interface should be defined"
        assert "enum DocumentStatus" in content, "DocumentStatus enum should be defined"
        assert "interface DashboardResponse" in content, "DashboardResponse interface should be defined"
        assert "interface Notification" in content, "Notification interface should be defined"


class TestFlutterSDK:
    """Tests for Flutter SDK (Dart)"""

    def test_flutter_structure_exists(self):
        """Test Flutter SDK directory structure"""
        flutter_dir = MOBILE_SDKS_DIR / "flutter"
        assert flutter_dir.exists(), "Flutter SDK directory should exist"
        assert (flutter_dir / "pubspec.yaml").exists(), "pubspec.yaml should exist"

    def test_flutter_sources_exist(self):
        """Test Flutter source files exist"""
        lib_dir = MOBILE_SDKS_DIR / "flutter" / "lib"
        assert lib_dir.exists(), "Flutter lib directory should exist"
        assert (lib_dir / "dms_sdk.dart").exists(), "dms_sdk.dart should exist"

        src_dir = lib_dir / "src"
        assert src_dir.exists(), "Flutter src directory should exist"
        assert (src_dir / "dms_client.dart").exists(), "dms_client.dart should exist"
        assert (src_dir / "models.dart").exists(), "models.dart should exist"
        assert (src_dir / "errors.dart").exists(), "errors.dart should exist"

    def test_flutter_pubspec_yaml(self):
        """Test pubspec.yaml configuration"""
        pubspec_file = MOBILE_SDKS_DIR / "flutter" / "pubspec.yaml"
        content = pubspec_file.read_text()

        assert "name: dms_sdk" in content, "Package name should be correct"
        assert "description:" in content, "Package should have description"
        assert "version:" in content, "Package should have version"

    def test_flutter_client_implementation(self):
        """Test Flutter client has required implementation"""
        client_file = MOBILE_SDKS_DIR / "flutter" / "lib" / "src" / "dms_client.dart"
        content = client_file.read_text()

        # Check for key features
        assert "class DMSClient" in content, "DMSClient class should be defined"
        assert "void configure" in content, "Configure method should exist"
        assert "request(" in content, "Request method should exist"
        assert "uploadFile(" in content, "UploadFile method should exist"
        assert "downloadFile(" in content, "DownloadFile method should exist"

    def test_flutter_models_implementation(self):
        """Test Flutter models are properly defined"""
        models_file = MOBILE_SDKS_DIR / "flutter" / "lib" / "src" / "models.dart"
        content = models_file.read_text()

        # Check for key models
        assert "class AuthResponse" in content, "AuthResponse class should be defined"
        assert "class User" in content, "User class should be defined"
        assert "class Document" in content, "Document class should be defined"
        assert "enum DocumentStatus" in content, "DocumentStatus enum should be defined"
        assert "class DashboardResponse" in content, "DashboardResponse class should be defined"
        assert "class Notification" in content, "Notification class should be defined"

    def test_flutter_services_implementation(self):
        """Test Flutter services are properly defined"""
        src_dir = MOBILE_SDKS_DIR / "flutter" / "lib" / "src"

        # Check services exist
        assert (src_dir / "auth_service.dart").exists(), "auth_service.dart should exist"
        assert (src_dir / "document_service.dart").exists(), "document_service.dart should exist"
        assert (src_dir / "analytics_service.dart").exists(), "analytics_service.dart should exist"
        assert (src_dir / "notification_service.dart").exists(), "notification_service.dart should exist"
        assert (src_dir / "websocket_service.dart").exists(), "websocket_service.dart should exist"


class TestCrossSDKConsistency:
    """Tests for consistency across all SDKs"""

    def test_all_sdks_have_authentication(self):
        """Test all SDKs implement authentication"""
        # iOS
        ios_content = (MOBILE_SDKS_DIR / "ios" / "Sources" / "DMSSDK" / "DMSClient.swift").read_text()
        assert "func login" in ios_content, "iOS SDK should have login"
        assert "func logout" in ios_content, "iOS SDK should have logout"

        # Android
        android_content = (MOBILE_SDKS_DIR / "android" / "src" / "main" / "kotlin" / "com" / "example" / "dms_sdk" / "DMSClient.kt").read_text()
        assert "suspend fun login" in android_content, "Android SDK should have login"
        assert "suspend fun logout" in android_content, "Android SDK should have logout"

        # React Native
        rn_content = (MOBILE_SDKS_DIR / "react_native" / "src" / "DMSClient.ts").read_text()
        assert "login" in rn_content, "React Native SDK should have login"
        assert "logout" in rn_content, "React Native SDK should have logout"

        # Flutter
        flutter_content = (MOBILE_SDKS_DIR / "flutter" / "lib" / "src" / "auth_service.dart").read_text()
        assert "login" in flutter_content, "Flutter SDK should have login"
        assert "logout" in flutter_content, "Flutter SDK should have logout"

    def test_all_sdks_have_document_operations(self):
        """Test all SDKs implement document operations"""
        operations = ["get", "create", "update", "delete", "upload", "download"]

        # iOS
        ios_content = (MOBILE_SDKS_DIR / "ios" / "Sources" / "DMSSDK" / "DMSClient.swift").read_text().lower()
        for op in operations:
            assert op in ios_content, f"iOS SDK should have {op} operation"

        # Android
        android_content = (MOBILE_SDKS_DIR / "android" / "src" / "main" / "kotlin" / "com" / "example" / "dms_sdk" / "DMSClient.kt").read_text().lower()
        for op in operations:
            assert op in android_content, f"Android SDK should have {op} operation"

        # React Native
        rn_content = (MOBILE_SDKS_DIR / "react_native" / "src" / "DMSClient.ts").read_text().lower()
        for op in operations:
            assert op in rn_content, f"React Native SDK should have {op} operation"

        # Flutter
        flutter_content = (MOBILE_SDKS_DIR / "flutter" / "lib" / "src" / "document_service.dart").read_text().lower()
        for op in operations:
            assert op in flutter_content, f"Flutter SDK should have {op} operation"

    def test_all_sdks_have_websocket_support(self):
        """Test all SDKs implement WebSocket support"""
        # iOS
        ios_content = (MOBILE_SDKS_DIR / "ios" / "Sources" / "DMSSDK" / "DMSClient.swift").read_text()
        assert "WebSocket" in ios_content, "iOS SDK should have WebSocket support"

        # Android
        android_content = (MOBILE_SDKS_DIR / "android" / "src" / "main" / "kotlin" / "com" / "example" / "dms_sdk" / "DMSClient.kt").read_text()
        assert "WebSocket" in android_content, "Android SDK should have WebSocket support"

        # React Native
        rn_content = (MOBILE_SDKS_DIR / "react_native" / "src" / "DMSClient.ts").read_text()
        assert "WebSocket" in rn_content, "React Native SDK should have WebSocket support"

        # Flutter
        flutter_content = (MOBILE_SDKS_DIR / "flutter" / "lib" / "src" / "websocket_service.dart").read_text()
        assert "WebSocket" in flutter_content, "Flutter SDK should have WebSocket support"


class TestSDKDocumentation:
    """Tests for SDK documentation"""

    def test_readme_exists(self):
        """Test README exists for mobile SDKs"""
        readme = MOBILE_SDKS_DIR / "README.md"
        assert readme.exists(), "README.md should exist"

    def test_readme_content(self):
        """Test README has required content"""
        readme = MOBILE_SDKS_DIR / "README.md"
        content = readme.read_text()

        # Check for key sections
        assert "iOS SDK" in content, "README should document iOS SDK"
        assert "Android SDK" in content, "README should document Android SDK"
        assert "React Native SDK" in content, "README should document React Native SDK"
        assert "Flutter Plugin" in content, "README should document Flutter Plugin"
        assert "Installation" in content or "Getting Started" in content, "README should have installation instructions"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
