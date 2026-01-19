"""
Comprehensive tests for configuration management

Tests the centralized configuration system including base Config class,
environment-specific configs (Development/Production/Testing), and
configuration factory function.

Session 24 - 60+ tests
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock dotenv if not available
try:
    import dotenv
except ImportError:
    sys.modules["dotenv"] = Mock()

from src.config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    config_by_name,
    get_config,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Clear environment variables before each test"""
    env_vars = [
        "SECRET_KEY",
        "FLASK_ENV",
        "DEBUG",
        "HOST",
        "APP_PORT",
        "DATABASE_URL",
        "ENABLE_EMAIL",
        "SMTP_HOST",
        "SMTP_PORT",
        "LOG_LEVEL",
        "API_VERSION",
        "MAX_CONTENT_LENGTH",
        "ENABLE_WEBHOOKS",
        "CACHE_TYPE",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


class TestBaseConfig:
    """Test base Config class"""

    def test_config_class_exists(self):
        """Test Config class is defined"""
        assert Config is not None

    def test_app_name_default(self):
        """Test default application name"""
        assert Config.APP_NAME == "Document Management System"

    def test_version_defined(self):
        """Test version is defined"""
        assert hasattr(Config, "VERSION")
        assert isinstance(Config.VERSION, str)
        assert Config.VERSION == "2.1.0"

    def test_base_dir_is_path(self):
        """Test BASE_DIR is a Path object"""
        assert isinstance(Config.BASE_DIR, Path)

    def test_data_dir_under_base(self):
        """Test DATA_DIR is under BASE_DIR"""
        assert Config.DATA_DIR.parent == Config.BASE_DIR or str(Config.DATA_DIR).startswith(str(Config.BASE_DIR))

    def test_export_dir_under_data(self):
        """Test EXPORT_DIR is under DATA_DIR"""
        assert Config.EXPORT_DIR.parent == Config.DATA_DIR

    def test_template_dir_under_data(self):
        """Test TEMPLATE_DIR is under DATA_DIR"""
        assert Config.TEMPLATE_DIR.parent == Config.DATA_DIR

    def test_log_dir_under_base(self):
        """Test LOG_DIR is under BASE_DIR"""
        assert Config.LOG_DIR.parent == Config.BASE_DIR or str(Config.LOG_DIR).startswith(str(Config.BASE_DIR))

    def test_secret_key_default(self):
        """Test default SECRET_KEY"""
        assert Config.SECRET_KEY == "dev-secret-key-change-in-production"

    def test_flask_env_default(self):
        """Test default FLASK_ENV"""
        assert Config.FLASK_ENV == "development"

    def test_debug_default_false(self):
        """Test DEBUG defaults to False"""
        assert Config.DEBUG is False

    def test_host_default(self):
        """Test default HOST"""
        assert Config.HOST == "0.0.0.0"

    def test_port_default(self):
        """Test default PORT"""
        assert Config.PORT == 5000

    def test_port_is_integer(self):
        """Test PORT is an integer"""
        assert isinstance(Config.PORT, int)

    def test_database_url_default(self):
        """Test default DATABASE_URL"""
        assert "sqlite" in Config.DATABASE_URL.lower()
        assert "services.db" in Config.DATABASE_URL

    def test_sqlalchemy_track_modifications_false(self):
        """Test SQLALCHEMY_TRACK_MODIFICATIONS is False"""
        assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False

    def test_sqlalchemy_echo_false(self):
        """Test SQLALCHEMY_ECHO is False by default"""
        assert Config.SQLALCHEMY_ECHO is False

    def test_session_cookie_secure_true(self):
        """Test SESSION_COOKIE_SECURE defaults to True"""
        assert Config.SESSION_COOKIE_SECURE is True

    def test_session_cookie_httponly_true(self):
        """Test SESSION_COOKIE_HTTPONLY defaults to True"""
        assert Config.SESSION_COOKIE_HTTPONLY is True

    def test_session_cookie_samesite_default(self):
        """Test SESSION_COOKIE_SAMESITE default"""
        assert Config.SESSION_COOKIE_SAMESITE == "Lax"

    def test_permanent_session_lifetime_default(self):
        """Test PERMANENT_SESSION_LIFETIME default"""
        assert Config.PERMANENT_SESSION_LIFETIME == 3600
        assert isinstance(Config.PERMANENT_SESSION_LIFETIME, int)

    def test_max_content_length_default(self):
        """Test MAX_CONTENT_LENGTH default (16MB)"""
        assert Config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
        assert isinstance(Config.MAX_CONTENT_LENGTH, int)

    def test_api_version_default(self):
        """Test API_VERSION default"""
        assert Config.API_VERSION == "v1"

    def test_api_rate_limit_default(self):
        """Test API_RATE_LIMIT default"""
        assert Config.API_RATE_LIMIT == "100/hour"

    def test_api_key_required_default_false(self):
        """Test API_KEY_REQUIRED defaults to False"""
        assert Config.API_KEY_REQUIRED is False

    def test_cache_type_default(self):
        """Test CACHE_TYPE default"""
        assert Config.CACHE_TYPE == "simple"

    def test_cache_default_timeout(self):
        """Test CACHE_DEFAULT_TIMEOUT default"""
        assert Config.CACHE_DEFAULT_TIMEOUT == 300
        assert isinstance(Config.CACHE_DEFAULT_TIMEOUT, int)

    def test_cache_redis_url_default(self):
        """Test CACHE_REDIS_URL default"""
        assert "redis://" in Config.CACHE_REDIS_URL
        assert "localhost" in Config.CACHE_REDIS_URL

    def test_enable_email_default_false(self):
        """Test ENABLE_EMAIL defaults to False"""
        assert Config.ENABLE_EMAIL is False

    def test_smtp_host_default(self):
        """Test SMTP_HOST default"""
        assert Config.SMTP_HOST == "localhost"

    def test_smtp_port_default(self):
        """Test SMTP_PORT default"""
        assert Config.SMTP_PORT == 587
        assert isinstance(Config.SMTP_PORT, int)

    def test_smtp_use_tls_default_true(self):
        """Test SMTP_USE_TLS defaults to True"""
        assert Config.SMTP_USE_TLS is True

    def test_smtp_use_ssl_default_false(self):
        """Test SMTP_USE_SSL defaults to False"""
        assert Config.SMTP_USE_SSL is False

    def test_from_email_default(self):
        """Test FROM_EMAIL default"""
        assert Config.FROM_EMAIL == "noreply@dms.local"

    def test_admin_email_default(self):
        """Test ADMIN_EMAIL default"""
        assert Config.ADMIN_EMAIL == "admin@dms.local"

    def test_log_level_default(self):
        """Test LOG_LEVEL default"""
        assert Config.LOG_LEVEL == "INFO"

    def test_log_max_bytes_default(self):
        """Test LOG_MAX_BYTES default (10MB)"""
        assert Config.LOG_MAX_BYTES == 10 * 1024 * 1024
        assert isinstance(Config.LOG_MAX_BYTES, int)

    def test_log_backup_count_default(self):
        """Test LOG_BACKUP_COUNT default"""
        assert Config.LOG_BACKUP_COUNT == 5
        assert isinstance(Config.LOG_BACKUP_COUNT, int)

    def test_log_format_defined(self):
        """Test LOG_FORMAT is defined"""
        assert hasattr(Config, "LOG_FORMAT")
        assert "%(asctime)s" in Config.LOG_FORMAT
        assert "%(levelname)s" in Config.LOG_FORMAT

    def test_enable_webhooks_default_false(self):
        """Test ENABLE_WEBHOOKS defaults to False"""
        assert Config.ENABLE_WEBHOOKS is False

    def test_enable_api_docs_default_true(self):
        """Test ENABLE_API_DOCS defaults to True"""
        assert Config.ENABLE_API_DOCS is True

    def test_enable_metrics_default_false(self):
        """Test ENABLE_METRICS defaults to False"""
        assert Config.ENABLE_METRICS is False

    def test_swagger_config_exists(self):
        """Test SWAGGER config dictionary exists"""
        assert hasattr(Config, "SWAGGER")
        assert isinstance(Config.SWAGGER, dict)

    def test_swagger_has_required_fields(self):
        """Test SWAGGER has required fields"""
        assert "title" in Config.SWAGGER
        assert "version" in Config.SWAGGER
        assert "description" in Config.SWAGGER

    def test_webhook_timeout_default(self):
        """Test WEBHOOK_TIMEOUT default"""
        assert Config.WEBHOOK_TIMEOUT == 30
        assert isinstance(Config.WEBHOOK_TIMEOUT, int)

    def test_webhook_retry_count_default(self):
        """Test WEBHOOK_RETRY_COUNT default"""
        assert Config.WEBHOOK_RETRY_COUNT == 3
        assert isinstance(Config.WEBHOOK_RETRY_COUNT, int)

    def test_ensure_directories_method_exists(self):
        """Test ensure_directories method exists"""
        assert hasattr(Config, "ensure_directories")
        assert callable(Config.ensure_directories)


class TestDevelopmentConfig:
    """Test DevelopmentConfig class"""

    def test_development_config_inherits_from_config(self):
        """Test DevelopmentConfig inherits from Config"""
        assert issubclass(DevelopmentConfig, Config)

    def test_development_debug_true(self):
        """Test DEBUG is True in development"""
        assert DevelopmentConfig.DEBUG is True

    def test_development_flask_env(self):
        """Test FLASK_ENV is development"""
        assert DevelopmentConfig.FLASK_ENV == "development"

    def test_development_session_cookie_secure_false(self):
        """Test SESSION_COOKIE_SECURE is False in development"""
        assert DevelopmentConfig.SESSION_COOKIE_SECURE is False

    def test_development_sqlalchemy_echo_true(self):
        """Test SQLALCHEMY_ECHO is True in development"""
        assert DevelopmentConfig.SQLALCHEMY_ECHO is True

    def test_development_log_level_debug(self):
        """Test LOG_LEVEL is DEBUG in development"""
        assert DevelopmentConfig.LOG_LEVEL == "DEBUG"


class TestProductionConfig:
    """Test ProductionConfig class"""

    def test_production_config_inherits_from_config(self):
        """Test ProductionConfig inherits from Config"""
        assert issubclass(ProductionConfig, Config)

    def test_production_debug_false(self):
        """Test DEBUG is False in production"""
        assert ProductionConfig.DEBUG is False

    def test_production_flask_env(self):
        """Test FLASK_ENV is production"""
        assert ProductionConfig.FLASK_ENV == "production"

    def test_production_session_cookie_secure_true(self):
        """Test SESSION_COOKIE_SECURE is True in production"""
        assert ProductionConfig.SESSION_COOKIE_SECURE is True

    def test_production_validate_method_exists(self):
        """Test validate method exists"""
        assert hasattr(ProductionConfig, "validate")
        assert callable(ProductionConfig.validate)

    def test_production_validate_raises_without_secret_key(self, monkeypatch):
        """Test validate raises error if SECRET_KEY not set"""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        # Force reload of SECRET_KEY
        with patch.object(ProductionConfig, "SECRET_KEY", "dev-secret-key-change-in-production"):
            with pytest.raises(ValueError) as exc_info:
                ProductionConfig.validate()
            assert "SECRET_KEY" in str(exc_info.value)

    def test_production_validate_raises_with_dev_secret_key(self):
        """Test validate raises error if using dev SECRET_KEY"""
        with patch.object(ProductionConfig, "SECRET_KEY", "dev-secret-key-change-in-production"):
            with pytest.raises(ValueError) as exc_info:
                ProductionConfig.validate()
            assert "SECRET_KEY" in str(exc_info.value)


class TestTestingConfig:
    """Test TestingConfig class"""

    def test_testing_config_inherits_from_config(self):
        """Test TestingConfig inherits from Config"""
        assert issubclass(TestingConfig, Config)

    def test_testing_testing_true(self):
        """Test TESTING is True"""
        assert TestingConfig.TESTING is True

    def test_testing_debug_true(self):
        """Test DEBUG is True in testing"""
        assert TestingConfig.DEBUG is True

    def test_testing_database_url_memory(self):
        """Test DATABASE_URL uses in-memory SQLite"""
        assert TestingConfig.DATABASE_URL == "sqlite:///:memory:"

    def test_testing_disable_email(self):
        """Test ENABLE_EMAIL is False in testing"""
        assert TestingConfig.ENABLE_EMAIL is False

    def test_testing_disable_webhooks(self):
        """Test ENABLE_WEBHOOKS is False in testing"""
        assert TestingConfig.ENABLE_WEBHOOKS is False

    def test_testing_csrf_disabled(self):
        """Test WTF_CSRF_ENABLED is False in testing"""
        assert TestingConfig.WTF_CSRF_ENABLED is False


class TestConfigByName:
    """Test config_by_name dictionary"""

    def test_config_by_name_exists(self):
        """Test config_by_name dictionary exists"""
        assert config_by_name is not None
        assert isinstance(config_by_name, dict)

    def test_config_by_name_has_development(self):
        """Test config_by_name has development key"""
        assert "development" in config_by_name
        assert config_by_name["development"] == DevelopmentConfig

    def test_config_by_name_has_production(self):
        """Test config_by_name has production key"""
        assert "production" in config_by_name
        assert config_by_name["production"] == ProductionConfig

    def test_config_by_name_has_testing(self):
        """Test config_by_name has testing key"""
        assert "testing" in config_by_name
        assert config_by_name["testing"] == TestingConfig

    def test_config_by_name_has_default(self):
        """Test config_by_name has default key"""
        assert "default" in config_by_name
        assert config_by_name["default"] == DevelopmentConfig


class TestGetConfig:
    """Test get_config factory function"""

    def test_get_config_function_exists(self):
        """Test get_config function exists"""
        assert get_config is not None
        assert callable(get_config)

    def test_get_config_returns_development_by_default(self, clean_env, monkeypatch):
        """Test get_config returns DevelopmentConfig by default"""
        monkeypatch.delenv("FLASK_ENV", raising=False)
        with patch.object(Config, "ensure_directories"):
            config = get_config()
            assert config == DevelopmentConfig

    def test_get_config_returns_development_when_specified(self, clean_env):
        """Test get_config returns DevelopmentConfig when specified"""
        with patch.object(Config, "ensure_directories"):
            config = get_config("development")
            assert config == DevelopmentConfig

    def test_get_config_returns_testing_when_specified(self, clean_env):
        """Test get_config returns TestingConfig when specified"""
        with patch.object(Config, "ensure_directories"):
            config = get_config("testing")
            assert config == TestingConfig

    def test_get_config_reads_flask_env_variable(self, clean_env, monkeypatch):
        """Test get_config reads FLASK_ENV environment variable"""
        monkeypatch.setenv("FLASK_ENV", "testing")
        with patch.object(Config, "ensure_directories"):
            config = get_config()
            assert config == TestingConfig

    def test_get_config_calls_ensure_directories(self, clean_env):
        """Test get_config calls ensure_directories"""
        with patch.object(Config, "ensure_directories") as mock_ensure:
            get_config("development")
            mock_ensure.assert_called_once()

    def test_get_config_unknown_environment_uses_default(self, clean_env):
        """Test get_config uses default for unknown environment"""
        with patch.object(Config, "ensure_directories"):
            config = get_config("unknown_env")
            assert config == DevelopmentConfig


class TestEnvironmentVariableOverrides:
    """Test configuration values can be overridden with environment variables"""

    def test_secret_key_from_env(self, clean_env, monkeypatch):
        """Test SECRET_KEY can be set from environment"""
        monkeypatch.setenv("SECRET_KEY", "custom-secret-key")
        # Re-import to get new env value
        from importlib import reload
        import src.config as config_module

        reload(config_module)
        assert config_module.Config.SECRET_KEY == "custom-secret-key"

    def test_debug_true_from_env(self, clean_env, monkeypatch):
        """Test DEBUG can be set to True from environment"""
        monkeypatch.setenv("DEBUG", "true")
        from importlib import reload
        import src.config as config_module

        reload(config_module)
        assert config_module.Config.DEBUG is True

    def test_debug_false_from_env(self, clean_env, monkeypatch):
        """Test DEBUG can be set to False from environment"""
        monkeypatch.setenv("DEBUG", "false")
        from importlib import reload
        import src.config as config_module

        reload(config_module)
        assert config_module.Config.DEBUG is False

    def test_port_from_env(self, clean_env, monkeypatch):
        """Test PORT can be set from environment"""
        monkeypatch.setenv("APP_PORT", "8080")
        from importlib import reload
        import src.config as config_module

        reload(config_module)
        assert config_module.Config.PORT == 8080

    def test_host_from_env(self, clean_env, monkeypatch):
        """Test HOST can be set from environment"""
        monkeypatch.setenv("HOST", "127.0.0.1")
        from importlib import reload
        import src.config as config_module

        reload(config_module)
        assert config_module.Config.HOST == "127.0.0.1"

    def test_api_version_from_env(self, clean_env, monkeypatch):
        """Test API_VERSION can be set from environment"""
        monkeypatch.setenv("API_VERSION", "v2")
        from importlib import reload
        import src.config as config_module

        reload(config_module)
        assert config_module.Config.API_VERSION == "v2"
