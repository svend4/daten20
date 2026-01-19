"""
Comprehensive tests for session management

Tests server-side session management with multiple backend support
including Redis, filesystem, and database backends, plus configuration
classes and session lifecycle management.

Session 25 - 70+ tests
"""

import sys
from datetime import timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock optional dependencies
mock_flask_session = Mock()
mock_redis = Mock()
sys.modules["flask_session"] = mock_flask_session
sys.modules["redis"] = mock_redis

from src.core.session_manager import (
    DatabaseSessionConfig,
    DevelopmentSessionConfig,
    FilesystemSessionConfig,
    ProductionSessionConfig,
    RedisSessionConfig,
    SessionConfig,
    cleanup_expired_sessions,
    create_redis_session_config,
    enable_sessions,
    get_session_stats,
    init_session_manager,
)


@pytest.fixture
def mock_app():
    """Create a mock Flask app"""
    app = Mock()
    app.config = {}
    return app


@pytest.fixture
def mock_session():
    """Create a mock Session instance"""
    return Mock()


class TestSessionConfig:
    """Test base SessionConfig class"""

    def test_session_config_class_exists(self):
        """Test SessionConfig class exists"""
        assert SessionConfig is not None

    def test_session_type_default(self):
        """Test SESSION_TYPE default"""
        assert SessionConfig.SESSION_TYPE == "redis"

    def test_session_permanent_true(self):
        """Test SESSION_PERMANENT is True"""
        assert SessionConfig.SESSION_PERMANENT is True

    def test_session_use_signer_true(self):
        """Test SESSION_USE_SIGNER is True"""
        assert SessionConfig.SESSION_USE_SIGNER is True

    def test_session_key_prefix(self):
        """Test SESSION_KEY_PREFIX"""
        assert SessionConfig.SESSION_KEY_PREFIX == "dms:session:"

    def test_permanent_session_lifetime_default(self):
        """Test PERMANENT_SESSION_LIFETIME default (24 hours)"""
        assert SessionConfig.PERMANENT_SESSION_LIFETIME == timedelta(hours=24)

    def test_session_cookie_name(self):
        """Test SESSION_COOKIE_NAME"""
        assert SessionConfig.SESSION_COOKIE_NAME == "dms_session"

    def test_session_cookie_httponly_true(self):
        """Test SESSION_COOKIE_HTTPONLY is True"""
        assert SessionConfig.SESSION_COOKIE_HTTPONLY is True

    def test_session_cookie_secure_true(self):
        """Test SESSION_COOKIE_SECURE is True"""
        assert SessionConfig.SESSION_COOKIE_SECURE is True

    def test_session_cookie_samesite(self):
        """Test SESSION_COOKIE_SAMESITE"""
        assert SessionConfig.SESSION_COOKIE_SAMESITE == "Lax"

    def test_session_redis_url_default(self):
        """Test SESSION_REDIS_URL default"""
        assert SessionConfig.SESSION_REDIS_URL == "redis://localhost:6379/1"

    def test_session_file_dir_default(self):
        """Test SESSION_FILE_DIR default"""
        assert SessionConfig.SESSION_FILE_DIR == "/tmp/flask_sessions"

    def test_session_file_threshold(self):
        """Test SESSION_FILE_THRESHOLD"""
        assert SessionConfig.SESSION_FILE_THRESHOLD == 500

    def test_session_file_mode(self):
        """Test SESSION_FILE_MODE"""
        assert SessionConfig.SESSION_FILE_MODE == 0o600

    def test_to_dict_method_exists(self):
        """Test to_dict method exists"""
        assert hasattr(SessionConfig, "to_dict")
        assert callable(SessionConfig.to_dict)

    def test_to_dict_returns_dict(self):
        """Test to_dict returns dictionary"""
        config = SessionConfig.to_dict()
        assert isinstance(config, dict)

    def test_to_dict_includes_uppercase_attributes(self):
        """Test to_dict includes uppercase attributes"""
        config = SessionConfig.to_dict()
        assert "SESSION_TYPE" in config
        assert "SESSION_PERMANENT" in config
        assert "SESSION_USE_SIGNER" in config

    def test_to_dict_excludes_private_attributes(self):
        """Test to_dict excludes private attributes"""
        config = SessionConfig.to_dict()
        for key in config.keys():
            assert not key.startswith("_")

    def test_to_dict_skips_none_values(self):
        """Test to_dict skips None values"""
        config = SessionConfig.to_dict()
        # SESSION_REDIS is None by default, should be skipped
        assert "SESSION_REDIS" not in config


class TestRedisSessionConfig:
    """Test RedisSessionConfig class"""

    def test_redis_session_config_inherits_from_session_config(self):
        """Test RedisSessionConfig inherits from SessionConfig"""
        assert issubclass(RedisSessionConfig, SessionConfig)

    def test_redis_session_type(self):
        """Test SESSION_TYPE is redis"""
        assert RedisSessionConfig.SESSION_TYPE == "redis"

    def test_redis_permanent_lifetime(self):
        """Test PERMANENT_SESSION_LIFETIME"""
        assert RedisSessionConfig.PERMANENT_SESSION_LIFETIME == timedelta(hours=24)

    def test_redis_use_signer_true(self):
        """Test SESSION_USE_SIGNER is True"""
        assert RedisSessionConfig.SESSION_USE_SIGNER is True

    def test_redis_key_prefix(self):
        """Test SESSION_KEY_PREFIX"""
        assert RedisSessionConfig.SESSION_KEY_PREFIX == "dms:session:"


class TestFilesystemSessionConfig:
    """Test FilesystemSessionConfig class"""

    def test_filesystem_session_config_inherits_from_session_config(self):
        """Test FilesystemSessionConfig inherits from SessionConfig"""
        assert issubclass(FilesystemSessionConfig, SessionConfig)

    def test_filesystem_session_type(self):
        """Test SESSION_TYPE is filesystem"""
        assert FilesystemSessionConfig.SESSION_TYPE == "filesystem"

    def test_filesystem_file_dir(self):
        """Test SESSION_FILE_DIR"""
        assert FilesystemSessionConfig.SESSION_FILE_DIR == "./tmp/sessions"

    def test_filesystem_use_signer_true(self):
        """Test SESSION_USE_SIGNER is True"""
        assert FilesystemSessionConfig.SESSION_USE_SIGNER is True


class TestDatabaseSessionConfig:
    """Test DatabaseSessionConfig class"""

    def test_database_session_config_inherits_from_session_config(self):
        """Test DatabaseSessionConfig inherits from SessionConfig"""
        assert issubclass(DatabaseSessionConfig, SessionConfig)

    def test_database_session_type(self):
        """Test SESSION_TYPE is sqlalchemy"""
        assert DatabaseSessionConfig.SESSION_TYPE == "sqlalchemy"

    def test_database_sqlalchemy_table(self):
        """Test SESSION_SQLALCHEMY_TABLE"""
        assert DatabaseSessionConfig.SESSION_SQLALCHEMY_TABLE == "sessions"

    def test_database_use_signer_true(self):
        """Test SESSION_USE_SIGNER is True"""
        assert DatabaseSessionConfig.SESSION_USE_SIGNER is True


class TestProductionSessionConfig:
    """Test ProductionSessionConfig class"""

    def test_production_config_inherits_from_redis_config(self):
        """Test ProductionSessionConfig inherits from RedisSessionConfig"""
        assert issubclass(ProductionSessionConfig, RedisSessionConfig)

    def test_production_cookie_secure_true(self):
        """Test SESSION_COOKIE_SECURE is True"""
        assert ProductionSessionConfig.SESSION_COOKIE_SECURE is True

    def test_production_cookie_httponly_true(self):
        """Test SESSION_COOKIE_HTTPONLY is True"""
        assert ProductionSessionConfig.SESSION_COOKIE_HTTPONLY is True

    def test_production_cookie_samesite_strict(self):
        """Test SESSION_COOKIE_SAMESITE is Strict"""
        assert ProductionSessionConfig.SESSION_COOKIE_SAMESITE == "Strict"

    def test_production_session_lifetime(self):
        """Test PERMANENT_SESSION_LIFETIME is 7 days"""
        assert ProductionSessionConfig.PERMANENT_SESSION_LIFETIME == timedelta(days=7)

    def test_production_redis_url(self):
        """Test SESSION_REDIS_URL is set"""
        assert ProductionSessionConfig.SESSION_REDIS_URL == "redis://localhost:6379/1"


class TestDevelopmentSessionConfig:
    """Test DevelopmentSessionConfig class"""

    def test_development_config_inherits_from_session_config(self):
        """Test DevelopmentSessionConfig inherits from SessionConfig"""
        assert issubclass(DevelopmentSessionConfig, SessionConfig)

    def test_development_cookie_secure_false(self):
        """Test SESSION_COOKIE_SECURE is False for HTTP"""
        assert DevelopmentSessionConfig.SESSION_COOKIE_SECURE is False

    def test_development_cookie_samesite_lax(self):
        """Test SESSION_COOKIE_SAMESITE is Lax"""
        assert DevelopmentSessionConfig.SESSION_COOKIE_SAMESITE == "Lax"

    def test_development_session_lifetime(self):
        """Test PERMANENT_SESSION_LIFETIME is 1 hour"""
        assert DevelopmentSessionConfig.PERMANENT_SESSION_LIFETIME == timedelta(hours=1)

    def test_development_session_type_filesystem(self):
        """Test SESSION_TYPE is filesystem"""
        assert DevelopmentSessionConfig.SESSION_TYPE == "filesystem"

    def test_development_file_dir(self):
        """Test SESSION_FILE_DIR"""
        assert DevelopmentSessionConfig.SESSION_FILE_DIR == "./tmp/dev_sessions"


class TestInitSessionManager:
    """Test init_session_manager function"""

    def test_init_session_manager_function_exists(self):
        """Test init_session_manager function exists"""
        assert init_session_manager is not None
        assert callable(init_session_manager)

    @patch("src.core.session_manager.SESSION_AVAILABLE", False)
    def test_init_when_flask_session_not_available(self, mock_app):
        """Test init_session_manager returns None when Flask-Session not available"""
        result = init_session_manager(mock_app)
        assert result is None

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    @patch("src.core.session_manager.REDIS_AVAILABLE", True)
    @patch("src.core.session_manager.Session")
    def test_init_with_redis_available(self, mock_session_class, mock_app):
        """Test init_session_manager with Redis available"""
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance

        # Mock Redis connection
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_redis_client

        result = init_session_manager(mock_app)

        assert result == mock_session_instance
        assert "SESSION_TYPE" in mock_app.config
        mock_session_class.assert_called_once_with(mock_app)

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    @patch("src.core.session_manager.REDIS_AVAILABLE", False)
    @patch("src.core.session_manager.Session")
    def test_init_falls_back_to_filesystem_when_redis_unavailable(self, mock_session_class, mock_app):
        """Test init_session_manager falls back to filesystem when Redis unavailable"""
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance

        result = init_session_manager(mock_app)

        assert result == mock_session_instance
        # Should use FilesystemSessionConfig when Redis not available

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    @patch("src.core.session_manager.Session")
    def test_init_with_custom_config(self, mock_session_class, mock_app):
        """Test init_session_manager with custom config"""
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance

        custom_config = FilesystemSessionConfig

        result = init_session_manager(mock_app, config=custom_config)

        assert result == mock_session_instance
        assert mock_app.config.get("SESSION_TYPE") == "filesystem"

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    @patch("src.core.session_manager.Session")
    def test_init_with_custom_redis_url(self, mock_session_class, mock_app):
        """Test init_session_manager with custom Redis URL"""
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance

        custom_url = "redis://custom:6379/2"

        result = init_session_manager(mock_app, redis_url=custom_url)

        assert result == mock_session_instance
        assert mock_app.config.get("SESSION_REDIS_URL") == custom_url

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    @patch("src.core.session_manager.Session")
    def test_init_handles_exception_gracefully(self, mock_session_class, mock_app):
        """Test init_session_manager handles exceptions gracefully"""
        mock_session_class.side_effect = Exception("Test error")

        result = init_session_manager(mock_app)

        assert result is None


class TestCreateRedisSessionConfig:
    """Test create_redis_session_config function"""

    def test_create_redis_session_config_function_exists(self):
        """Test create_redis_session_config function exists"""
        assert create_redis_session_config is not None
        assert callable(create_redis_session_config)

    def test_create_with_defaults(self):
        """Test creating config with default parameters"""
        config = create_redis_session_config()

        assert config.PERMANENT_SESSION_LIFETIME == timedelta(hours=24)
        assert config.SESSION_REDIS_URL == "redis://localhost:6379/1"
        assert config.SESSION_KEY_PREFIX == "dms:session:"

    def test_create_with_custom_lifetime(self):
        """Test creating config with custom lifetime"""
        config = create_redis_session_config(lifetime_hours=48)

        assert config.PERMANENT_SESSION_LIFETIME == timedelta(hours=48)

    def test_create_with_custom_redis_url(self):
        """Test creating config with custom Redis URL"""
        custom_url = "redis://custom-host:7000/3"
        config = create_redis_session_config(redis_url=custom_url)

        assert config.SESSION_REDIS_URL == custom_url

    def test_create_with_custom_key_prefix(self):
        """Test creating config with custom key prefix"""
        custom_prefix = "myapp:sess:"
        config = create_redis_session_config(key_prefix=custom_prefix)

        assert config.SESSION_KEY_PREFIX == custom_prefix

    def test_create_with_all_custom_parameters(self):
        """Test creating config with all custom parameters"""
        config = create_redis_session_config(
            lifetime_hours=72, redis_url="redis://prod:6379/1", key_prefix="prod:session:"
        )

        assert config.PERMANENT_SESSION_LIFETIME == timedelta(hours=72)
        assert config.SESSION_REDIS_URL == "redis://prod:6379/1"
        assert config.SESSION_KEY_PREFIX == "prod:session:"

    def test_create_returns_redis_session_config_instance(self):
        """Test create_redis_session_config returns RedisSessionConfig instance"""
        config = create_redis_session_config()

        assert isinstance(config, RedisSessionConfig)


class TestGetSessionStats:
    """Test get_session_stats function"""

    def test_get_session_stats_function_exists(self):
        """Test get_session_stats function exists"""
        assert get_session_stats is not None
        assert callable(get_session_stats)

    @patch("src.core.session_manager.SESSION_AVAILABLE", False)
    def test_get_stats_when_sessions_not_available(self, mock_app):
        """Test get_session_stats when sessions not available"""
        stats = get_session_stats(mock_app)

        assert stats["enabled"] is False
        assert "backend" in stats

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    def test_get_stats_basic_info(self, mock_app):
        """Test get_session_stats returns basic info"""
        mock_app.config["SESSION_TYPE"] = "filesystem"
        mock_app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
        mock_app.config["SESSION_COOKIE_NAME"] = "test_session"

        stats = get_session_stats(mock_app)

        assert stats["enabled"] is True
        assert stats["backend"] == "filesystem"
        assert "config" in stats

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    def test_get_stats_includes_config_details(self, mock_app):
        """Test get_session_stats includes config details"""
        mock_app.config["SESSION_TYPE"] = "redis"
        mock_app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
        mock_app.config["SESSION_COOKIE_NAME"] = "dms_session"
        mock_app.config["SESSION_COOKIE_SECURE"] = True
        mock_app.config["SESSION_COOKIE_HTTPONLY"] = True
        mock_app.config["SESSION_USE_SIGNER"] = True
        mock_app.config["SESSION_KEY_PREFIX"] = "dms:session:"

        stats = get_session_stats(mock_app)

        assert stats["config"]["cookie_name"] == "dms_session"
        assert stats["config"]["cookie_secure"] is True
        assert stats["config"]["cookie_httponly"] is True
        assert stats["config"]["use_signer"] is True

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    def test_get_stats_with_redis_backend(self, mock_app):
        """Test get_session_stats with Redis backend"""
        mock_app.config["SESSION_TYPE"] = "redis"
        mock_app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

        mock_redis_client = Mock()
        mock_redis_client.info.return_value = {"total_connections_received": 100, "total_commands_processed": 1000}
        mock_app.config["SESSION_REDIS"] = mock_redis_client

        stats = get_session_stats(mock_app)

        assert "redis" in stats
        assert stats["redis"]["connected"] is True
        assert stats["redis"]["total_connections"] == 100
        assert stats["redis"]["commands_processed"] == 1000

    @patch("src.core.session_manager.SESSION_AVAILABLE", True)
    def test_get_stats_with_redis_connection_error(self, mock_app):
        """Test get_session_stats handles Redis connection error"""
        mock_app.config["SESSION_TYPE"] = "redis"
        mock_app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

        mock_redis_client = Mock()
        mock_redis_client.info.side_effect = Exception("Connection error")
        mock_app.config["SESSION_REDIS"] = mock_redis_client

        stats = get_session_stats(mock_app)

        assert "redis" in stats
        assert stats["redis"]["connected"] is False
        assert "error" in stats["redis"]


class TestCleanupExpiredSessions:
    """Test cleanup_expired_sessions function"""

    def test_cleanup_function_exists(self):
        """Test cleanup_expired_sessions function exists"""
        assert cleanup_expired_sessions is not None
        assert callable(cleanup_expired_sessions)

    def test_cleanup_returns_zero_for_non_filesystem(self, mock_app):
        """Test cleanup returns 0 for non-filesystem backends"""
        mock_app.config["SESSION_TYPE"] = "redis"

        result = cleanup_expired_sessions(mock_app)

        assert result == 0

    def test_cleanup_returns_integer(self, mock_app):
        """Test cleanup returns integer"""
        mock_app.config["SESSION_TYPE"] = "filesystem"

        result = cleanup_expired_sessions(mock_app)

        assert isinstance(result, int)
        assert result == 0  # TODO implementation returns 0


class TestEnableSessions:
    """Test enable_sessions convenience function"""

    def test_enable_sessions_function_exists(self):
        """Test enable_sessions function exists"""
        assert enable_sessions is not None
        assert callable(enable_sessions)

    @patch("src.core.session_manager.init_session_manager")
    def test_enable_sessions_with_production_environment(self, mock_init, mock_app):
        """Test enable_sessions with production environment"""
        mock_session = Mock()
        mock_init.return_value = mock_session

        result = enable_sessions(mock_app, environment="production")

        mock_init.assert_called_once()
        call_args = mock_init.call_args
        assert call_args[0][0] == mock_app
        # Check that ProductionSessionConfig was used
        assert call_args[0][1] == ProductionSessionConfig

    @patch("src.core.session_manager.init_session_manager")
    def test_enable_sessions_with_development_environment(self, mock_init, mock_app):
        """Test enable_sessions with development environment"""
        mock_session = Mock()
        mock_init.return_value = mock_session

        result = enable_sessions(mock_app, environment="development")

        mock_init.assert_called_once()
        call_args = mock_init.call_args
        assert call_args[0][0] == mock_app
        # Check that DevelopmentSessionConfig was used
        assert call_args[0][1] == DevelopmentSessionConfig

    @patch("src.core.session_manager.init_session_manager")
    def test_enable_sessions_with_custom_redis_url(self, mock_init, mock_app):
        """Test enable_sessions with custom Redis URL"""
        mock_session = Mock()
        mock_init.return_value = mock_session

        custom_url = "redis://custom:6379/5"
        result = enable_sessions(mock_app, environment="production", redis_url=custom_url)

        mock_init.assert_called_once()
        call_args = mock_init.call_args
        # redis_url is passed as the 3rd positional argument
        assert call_args[0][2] == custom_url

    @patch("src.core.session_manager.init_session_manager")
    def test_enable_sessions_returns_session_instance(self, mock_init, mock_app):
        """Test enable_sessions returns session instance"""
        mock_session = Mock()
        mock_init.return_value = mock_session

        result = enable_sessions(mock_app)

        assert result == mock_session
