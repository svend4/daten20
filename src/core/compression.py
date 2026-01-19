"""
Response Compression Middleware

Provides automatic response compression for Flask applications.
Supports gzip, deflate, and brotli compression algorithms.

Features:
- Automatic content negotiation based on Accept-Encoding header
- Configurable compression level
- Minimum size threshold
- Selective compression based on content type
- Performance monitoring
"""

import logging
from typing import Dict, List, Optional

try:
    from flask_compress import Compress
    COMPRESS_AVAILABLE = True
except ImportError:
    COMPRESS_AVAILABLE = False

logger = logging.getLogger("dms.compression")


class CompressionConfig:
    """Configuration for response compression."""

    # Default compression level (1-9, higher = more compression)
    COMPRESS_LEVEL = 6

    # Minimum response size to compress (bytes)
    COMPRESS_MIN_SIZE = 500

    # MIME types to compress
    COMPRESS_MIMETYPES = [
        'text/html',
        'text/css',
        'text/xml',
        'text/plain',
        'text/javascript',
        'application/json',
        'application/javascript',
        'application/xml',
        'application/xhtml+xml',
        'application/rss+xml',
        'application/atom+xml',
        'application/x-javascript',
        'image/svg+xml',
    ]

    # Enable brotli compression (requires brotli package)
    COMPRESS_ALGORITHM = ['gzip', 'deflate']  # Add 'br' for brotli

    # Enable compression by default
    COMPRESS_REGISTER = True

    @classmethod
    def to_dict(cls) -> Dict:
        """Convert configuration to dictionary."""
        return {
            'COMPRESS_LEVEL': cls.COMPRESS_LEVEL,
            'COMPRESS_MIN_SIZE': cls.COMPRESS_MIN_SIZE,
            'COMPRESS_MIMETYPES': cls.COMPRESS_MIMETYPES,
            'COMPRESS_ALGORITHM': cls.COMPRESS_ALGORITHM,
            'COMPRESS_REGISTER': cls.COMPRESS_REGISTER,
        }


def init_compression(app, config: Optional[CompressionConfig] = None):
    """
    Initialize compression for Flask application.

    Args:
        app: Flask application instance
        config: Custom compression configuration

    Returns:
        Compress instance or None if not available
    """
    if not COMPRESS_AVAILABLE:
        logger.warning("Flask-Compress not available. Install with: pip install Flask-Compress")
        return None

    try:
        # Use custom config or default
        if config is None:
            config = CompressionConfig

        # Apply configuration to app
        app.config.update(config.to_dict())

        # Initialize compression
        compress = Compress(app)

        logger.info("Response compression initialized successfully")
        logger.debug(f"Compression config: {config.to_dict()}")

        return compress

    except Exception as e:
        logger.error(f"Failed to initialize compression: {e}", exc_info=True)
        return None


def create_compression_config(
    level: int = 6,
    min_size: int = 500,
    mimetypes: Optional[List[str]] = None,
    algorithms: Optional[List[str]] = None
) -> CompressionConfig:
    """
    Create custom compression configuration.

    Args:
        level: Compression level (1-9)
        min_size: Minimum response size in bytes
        mimetypes: List of MIME types to compress
        algorithms: List of compression algorithms

    Returns:
        CompressionConfig instance
    """
    config = CompressionConfig()

    # Validate and set compression level
    if 1 <= level <= 9:
        config.COMPRESS_LEVEL = level
    else:
        logger.warning(f"Invalid compression level {level}, using default (6)")

    # Set minimum size
    if min_size > 0:
        config.COMPRESS_MIN_SIZE = min_size

    # Set MIME types
    if mimetypes is not None:
        config.COMPRESS_MIMETYPES = mimetypes

    # Set algorithms
    if algorithms is not None:
        # Validate algorithms
        valid_algorithms = ['gzip', 'deflate', 'br']
        filtered_algorithms = [alg for alg in algorithms if alg in valid_algorithms]

        if 'br' in filtered_algorithms:
            try:
                import brotli  # noqa: F401
            except ImportError:
                logger.warning("Brotli requested but not installed. Install with: pip install brotli")
                filtered_algorithms.remove('br')

        config.COMPRESS_ALGORITHM = filtered_algorithms

    return config


# Production-optimized configuration
class ProductionCompressionConfig(CompressionConfig):
    """Production-optimized compression configuration."""

    # Higher compression for production
    COMPRESS_LEVEL = 9

    # Lower threshold for production
    COMPRESS_MIN_SIZE = 200

    # Add brotli for modern browsers
    COMPRESS_ALGORITHM = ['br', 'gzip', 'deflate']


# Development configuration
class DevelopmentCompressionConfig(CompressionConfig):
    """Development-friendly compression configuration."""

    # Lower compression for faster responses
    COMPRESS_LEVEL = 4

    # Higher threshold to skip small responses
    COMPRESS_MIN_SIZE = 1000

    # Only gzip for simplicity
    COMPRESS_ALGORITHM = ['gzip']


def get_compression_stats(app) -> Dict:
    """
    Get compression statistics from application.

    Args:
        app: Flask application instance

    Returns:
        Dictionary with compression statistics
    """
    stats = {
        'enabled': COMPRESS_AVAILABLE,
        'config': {}
    }

    if COMPRESS_AVAILABLE and hasattr(app, 'config'):
        stats['config'] = {
            'level': app.config.get('COMPRESS_LEVEL'),
            'min_size': app.config.get('COMPRESS_MIN_SIZE'),
            'algorithms': app.config.get('COMPRESS_ALGORITHM'),
            'mimetypes_count': len(app.config.get('COMPRESS_MIMETYPES', [])),
        }

    return stats


# Convenience function
def enable_compression(app, environment: str = 'production'):
    """
    Enable compression with environment-specific settings.

    Args:
        app: Flask application instance
        environment: Environment name ('production', 'development', or 'custom')

    Returns:
        Compress instance
    """
    if environment == 'production':
        config = ProductionCompressionConfig
    elif environment == 'development':
        config = DevelopmentCompressionConfig
    else:
        config = CompressionConfig

    return init_compression(app, config)
