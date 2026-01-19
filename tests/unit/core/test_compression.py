"""
Unit tests for compression module (Flask response compression)
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

# Check if Flask is available
try:
    import flask
    from src.core.compression import (
        CompressionConfig,
        DevelopmentCompressionConfig,
        ProductionCompressionConfig,
        create_compression_config,
        enable_compression,
        get_compression_stats,
        init_compression,
    )

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    CompressionConfig = None
    ProductionCompressionConfig = None
    DevelopmentCompressionConfig = None
    create_compression_config = None
    enable_compression = None
    get_compression_stats = None
    init_compression = None

pytestmark = pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask module not available")


# ============================================================================
# CompressionConfig Tests
# ============================================================================


class TestCompressionConfig:
    """Test CompressionConfig class"""

    def test_default_config_values(self):
        """Test default configuration values"""
        config = CompressionConfig()

        assert config.COMPRESS_LEVEL == 6
        assert config.COMPRESS_MIN_SIZE == 500
        assert isinstance(config.COMPRESS_MIMETYPES, list)
        assert len(config.COMPRESS_MIMETYPES) > 0

    def test_default_mimetypes_includes_common_types(self):
        """Test default MIME types include common ones"""
        config = CompressionConfig()

        mimetypes = config.COMPRESS_MIMETYPES

        assert "text/html" in mimetypes
        assert "text/css" in mimetypes
        assert "application/json" in mimetypes
        assert "text/javascript" in mimetypes

    def test_default_algorithms(self):
        """Test default compression algorithms"""
        config = CompressionConfig()

        assert "gzip" in config.COMPRESS_ALGORITHM
        assert "deflate" in config.COMPRESS_ALGORITHM

    def test_compression_enabled_by_default(self):
        """Test compression is enabled by default"""
        config = CompressionConfig()

        assert config.COMPRESS_REGISTER is True

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = CompressionConfig()

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "COMPRESS_LEVEL" in config_dict
        assert "COMPRESS_MIN_SIZE" in config_dict
        assert "COMPRESS_MIMETYPES" in config_dict
        assert config_dict["COMPRESS_LEVEL"] == 6


# ============================================================================
# ProductionCompressionConfig Tests
# ============================================================================


class TestProductionCompressionConfig:
    """Test ProductionCompressionConfig class"""

    def test_production_config_higher_compression(self):
        """Test production uses higher compression level"""
        config = ProductionCompressionConfig()

        assert config.COMPRESS_LEVEL == 9

    def test_production_config_lower_threshold(self):
        """Test production has lower size threshold"""
        config = ProductionCompressionConfig()

        assert config.COMPRESS_MIN_SIZE == 200
        assert config.COMPRESS_MIN_SIZE < CompressionConfig.COMPRESS_MIN_SIZE

    def test_production_config_includes_brotli(self):
        """Test production includes brotli if available"""
        config = ProductionCompressionConfig()

        assert "br" in config.COMPRESS_ALGORITHM


# ============================================================================
# DevelopmentCompressionConfig Tests
# ============================================================================


class TestDevelopmentCompressionConfig:
    """Test DevelopmentCompressionConfig class"""

    def test_development_config_lower_compression(self):
        """Test development uses lower compression for speed"""
        config = DevelopmentCompressionConfig()

        assert config.COMPRESS_LEVEL == 4
        assert config.COMPRESS_LEVEL < CompressionConfig.COMPRESS_LEVEL

    def test_development_config_higher_threshold(self):
        """Test development has higher size threshold"""
        config = DevelopmentCompressionConfig()

        assert config.COMPRESS_MIN_SIZE == 1000
        assert config.COMPRESS_MIN_SIZE > CompressionConfig.COMPRESS_MIN_SIZE

    def test_development_config_gzip_only(self):
        """Test development uses gzip only for simplicity"""
        config = DevelopmentCompressionConfig()

        assert config.COMPRESS_ALGORITHM == ["gzip"]
        assert "deflate" not in config.COMPRESS_ALGORITHM


# ============================================================================
# init_compression Tests
# ============================================================================


class TestInitCompression:
    """Test init_compression function"""

    @pytest.fixture
    def mock_app(self):
        """Create mock Flask app"""
        app = Mock()
        app.config = {}
        return app

    @patch("src.core.compression.COMPRESS_AVAILABLE", False)
    def test_init_compression_not_available(self, mock_app):
        """Test initialization when Flask-Compress not available"""
        result = init_compression(mock_app)

        assert result is None

    @patch("src.core.compression.COMPRESS_AVAILABLE", True)
    @patch("src.core.compression.Compress")
    def test_init_compression_success(self, mock_compress_class, mock_app):
        """Test successful compression initialization"""
        mock_compress_instance = Mock()
        mock_compress_class.return_value = mock_compress_instance

        result = init_compression(mock_app)

        assert result == mock_compress_instance
        assert "COMPRESS_LEVEL" in mock_app.config
        assert "COMPRESS_MIN_SIZE" in mock_app.config

    @patch("src.core.compression.COMPRESS_AVAILABLE", True)
    @patch("src.core.compression.Compress")
    def test_init_compression_with_custom_config(self, mock_compress_class, mock_app):
        """Test initialization with custom configuration"""
        mock_compress_instance = Mock()
        mock_compress_class.return_value = mock_compress_instance

        custom_config = ProductionCompressionConfig()

        result = init_compression(mock_app, custom_config)

        assert result == mock_compress_instance
        assert mock_app.config["COMPRESS_LEVEL"] == 9

    @patch("src.core.compression.COMPRESS_AVAILABLE", True)
    @patch("src.core.compression.Compress")
    def test_init_compression_exception_handling(self, mock_compress_class, mock_app):
        """Test exception handling during initialization"""
        mock_compress_class.side_effect = Exception("Compression error")

        result = init_compression(mock_app)

        assert result is None


# ============================================================================
# create_compression_config Tests
# ============================================================================


class TestCreateCompressionConfig:
    """Test create_compression_config function"""

    def test_create_config_with_defaults(self):
        """Test creating config with default values"""
        config = create_compression_config()

        assert config.COMPRESS_LEVEL == 6
        assert config.COMPRESS_MIN_SIZE == 500

    def test_create_config_custom_level(self):
        """Test creating config with custom compression level"""
        config = create_compression_config(level=9)

        assert config.COMPRESS_LEVEL == 9

    def test_create_config_invalid_level(self):
        """Test creating config with invalid compression level"""
        config = create_compression_config(level=15)

        # Should use default when invalid
        assert config.COMPRESS_LEVEL == 6

    def test_create_config_custom_min_size(self):
        """Test creating config with custom minimum size"""
        config = create_compression_config(min_size=1000)

        assert config.COMPRESS_MIN_SIZE == 1000

    def test_create_config_custom_mimetypes(self):
        """Test creating config with custom MIME types"""
        custom_mimetypes = ["text/html", "application/json"]

        config = create_compression_config(mimetypes=custom_mimetypes)

        assert config.COMPRESS_MIMETYPES == custom_mimetypes

    def test_create_config_custom_algorithms(self):
        """Test creating config with custom algorithms"""
        custom_algorithms = ["gzip"]

        config = create_compression_config(algorithms=custom_algorithms)

        assert config.COMPRESS_ALGORITHM == custom_algorithms

    def test_create_config_invalid_algorithm(self):
        """Test filtering invalid compression algorithms"""
        invalid_algorithms = ["gzip", "invalid_algo", "deflate"]

        config = create_compression_config(algorithms=invalid_algorithms)

        assert "gzip" in config.COMPRESS_ALGORITHM
        assert "deflate" in config.COMPRESS_ALGORITHM
        assert "invalid_algo" not in config.COMPRESS_ALGORITHM

    @patch("src.core.compression.logger")
    def test_create_config_brotli_not_installed(self, mock_logger):
        """Test handling brotli when not installed"""
        with patch.dict("sys.modules", {"brotli": None}):
            config = create_compression_config(algorithms=["br", "gzip"])

            # Should filter out 'br' if not available
            assert "gzip" in config.COMPRESS_ALGORITHM


# ============================================================================
# get_compression_stats Tests
# ============================================================================


class TestGetCompressionStats:
    """Test get_compression_stats function"""

    @pytest.fixture
    def mock_app(self):
        """Create mock Flask app with compression config"""
        app = Mock()
        app.config = {
            "COMPRESS_LEVEL": 6,
            "COMPRESS_MIN_SIZE": 500,
            "COMPRESS_ALGORITHM": ["gzip", "deflate"],
            "COMPRESS_MIMETYPES": ["text/html", "application/json"],
        }
        return app

    @patch("src.core.compression.COMPRESS_AVAILABLE", True)
    def test_get_compression_stats(self, mock_app):
        """Test getting compression statistics"""
        stats = get_compression_stats(mock_app)

        assert stats["enabled"] is True
        assert "config" in stats
        assert stats["config"]["level"] == 6
        assert stats["config"]["min_size"] == 500

    @patch("src.core.compression.COMPRESS_AVAILABLE", False)
    def test_get_compression_stats_not_available(self):
        """Test getting stats when compression not available"""
        mock_app = Mock()

        stats = get_compression_stats(mock_app)

        assert stats["enabled"] is False

    @patch("src.core.compression.COMPRESS_AVAILABLE", True)
    def test_get_compression_stats_mimetypes_count(self, mock_app):
        """Test stats include MIME types count"""
        stats = get_compression_stats(mock_app)

        assert "mimetypes_count" in stats["config"]
        assert stats["config"]["mimetypes_count"] == 2


# ============================================================================
# enable_compression Tests
# ============================================================================


class TestEnableCompression:
    """Test enable_compression function"""

    @pytest.fixture
    def mock_app(self):
        """Create mock Flask app"""
        app = Mock()
        app.config = {}
        return app

    @patch("src.core.compression.init_compression")
    def test_enable_compression_production(self, mock_init, mock_app):
        """Test enabling compression for production"""
        mock_init.return_value = Mock()

        result = enable_compression(mock_app, environment="production")

        mock_init.assert_called_once()
        call_args = mock_init.call_args
        config_arg = call_args[0][1]

        assert isinstance(config_arg, type) or hasattr(config_arg, "COMPRESS_LEVEL")

    @patch("src.core.compression.init_compression")
    def test_enable_compression_development(self, mock_init, mock_app):
        """Test enabling compression for development"""
        mock_init.return_value = Mock()

        result = enable_compression(mock_app, environment="development")

        mock_init.assert_called_once()

    @patch("src.core.compression.init_compression")
    def test_enable_compression_default(self, mock_init, mock_app):
        """Test enabling compression with default environment"""
        mock_init.return_value = Mock()

        result = enable_compression(mock_app, environment="custom")

        mock_init.assert_called_once()


# ============================================================================
# Integration Tests
# ============================================================================


class TestCompressionIntegration:
    """Test compression integration scenarios"""

    def test_config_hierarchy(self):
        """Test configuration class hierarchy"""
        base_config = CompressionConfig()
        prod_config = ProductionCompressionConfig()
        dev_config = DevelopmentCompressionConfig()

        # Production should be more aggressive
        assert prod_config.COMPRESS_LEVEL > base_config.COMPRESS_LEVEL
        assert prod_config.COMPRESS_MIN_SIZE < base_config.COMPRESS_MIN_SIZE

        # Development should be less aggressive
        assert dev_config.COMPRESS_LEVEL < base_config.COMPRESS_LEVEL
        assert dev_config.COMPRESS_MIN_SIZE > base_config.COMPRESS_MIN_SIZE

    def test_to_dict_includes_all_settings(self):
        """Test to_dict includes all configuration settings"""
        config = CompressionConfig()

        config_dict = config.to_dict()

        assert "COMPRESS_LEVEL" in config_dict
        assert "COMPRESS_MIN_SIZE" in config_dict
        assert "COMPRESS_MIMETYPES" in config_dict
        assert "COMPRESS_ALGORITHM" in config_dict
        assert "COMPRESS_REGISTER" in config_dict

    def test_create_config_with_all_parameters(self):
        """Test creating config with all parameters specified"""
        config = create_compression_config(
            level=8, min_size=100, mimetypes=["text/html"], algorithms=["gzip", "deflate"]
        )

        assert config.COMPRESS_LEVEL == 8
        assert config.COMPRESS_MIN_SIZE == 100
        assert config.COMPRESS_MIMETYPES == ["text/html"]
        assert "gzip" in config.COMPRESS_ALGORITHM
        assert "deflate" in config.COMPRESS_ALGORITHM

    def test_compression_level_bounds(self):
        """Test compression level validation bounds"""
        # Valid levels (1-9)
        for level in range(1, 10):
            config = create_compression_config(level=level)
            assert config.COMPRESS_LEVEL == level

        # Invalid level
        config = create_compression_config(level=0)
        assert config.COMPRESS_LEVEL == 6  # Default

        config = create_compression_config(level=10)
        assert config.COMPRESS_LEVEL == 6  # Default

    def test_mime_types_coverage(self):
        """Test default MIME types cover major formats"""
        config = CompressionConfig()

        mimetypes = config.COMPRESS_MIMETYPES

        # Text formats
        assert any("text/" in mime for mime in mimetypes)

        # Application formats
        assert any("application/" in mime for mime in mimetypes)

        # Should have JSON
        assert any("json" in mime for mime in mimetypes)

        # Should have JavaScript
        assert any("javascript" in mime.lower() for mime in mimetypes)

    @patch("src.core.compression.COMPRESS_AVAILABLE", True)
    @patch("src.core.compression.Compress")
    def test_full_initialization_workflow(self, mock_compress_class):
        """Test complete initialization workflow"""
        mock_app = Mock()
        mock_app.config = {}

        mock_compress_instance = Mock()
        mock_compress_class.return_value = mock_compress_instance

        # Create custom config
        custom_config = create_compression_config(level=9, min_size=100)

        # Initialize compression
        result = init_compression(mock_app, custom_config)

        # Verify
        assert result == mock_compress_instance
        assert mock_app.config["COMPRESS_LEVEL"] == 9
        assert mock_app.config["COMPRESS_MIN_SIZE"] == 100
        mock_compress_class.assert_called_once_with(mock_app)
