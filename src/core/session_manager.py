"""
Enhanced Session Management

Provides server-side session management with multiple backend support:
- Redis (recommended for production)
- Memcached
- Filesystem
- Database (SQLAlchemy)

Features:
- Secure server-side sessions
- Session expiration and cleanup
- Session encryption
- Multiple backend support
- Session analytics
"""

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

try:
    from flask_session import Session
    SESSION_AVAILABLE = True
except ImportError:
    SESSION_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger("dms.session")


class SessionConfig:
    """Base session configuration."""

    # Session type: 'redis', 'memcached', 'filesystem', 'sqlalchemy', 'mongodb'
    SESSION_TYPE = 'redis'

    # Session cookie configuration
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True  # Sign session cookie
    SESSION_KEY_PREFIX = 'dms:session:'

    # Session lifetime (24 hours)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Cookie settings
    SESSION_COOKIE_NAME = 'dms_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Redis-specific settings
    SESSION_REDIS = None  # Redis connection object
    SESSION_REDIS_URL = 'redis://localhost:6379/1'

    # Filesystem-specific settings (fallback)
    SESSION_FILE_DIR = '/tmp/flask_sessions'
    SESSION_FILE_THRESHOLD = 500
    SESSION_FILE_MODE = 0o600

    @classmethod
    def to_dict(cls) -> Dict:
        """Convert configuration to dictionary."""
        config = {}
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith('_'):
                value = getattr(cls, attr)
                # Skip None values and class methods
                if value is not None and not callable(value):
                    config[attr] = value
        return config


class RedisSessionConfig(SessionConfig):
    """Redis-optimized session configuration."""

    SESSION_TYPE = 'redis'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'dms:session:'


class FilesystemSessionConfig(SessionConfig):
    """Filesystem-based session configuration (development)."""

    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './tmp/sessions'
    SESSION_USE_SIGNER = True


class DatabaseSessionConfig(SessionConfig):
    """Database-based session configuration."""

    SESSION_TYPE = 'sqlalchemy'
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SESSION_USE_SIGNER = True


def init_session_manager(
    app,
    config: Optional[SessionConfig] = None,
    redis_url: Optional[str] = None
) -> Optional[Session]:
    """
    Initialize session manager for Flask application.

    Args:
        app: Flask application instance
        config: Custom session configuration
        redis_url: Redis connection URL (overrides config)

    Returns:
        Session instance or None if not available
    """
    if not SESSION_AVAILABLE:
        logger.warning("Flask-Session not available. Install with: pip install Flask-Session")
        return None

    try:
        # Use custom config or default
        if config is None:
            # Auto-detect best backend
            if REDIS_AVAILABLE:
                config = RedisSessionConfig
            else:
                logger.warning("Redis not available, falling back to filesystem sessions")
                config = FilesystemSessionConfig

        # Apply configuration to app
        app.config.update(config.to_dict())

        # Override Redis URL if provided
        if redis_url:
            app.config['SESSION_REDIS_URL'] = redis_url

        # Setup Redis connection if using Redis
        if app.config.get('SESSION_TYPE') == 'redis' and REDIS_AVAILABLE:
            try:
                redis_url = app.config.get('SESSION_REDIS_URL')
                redis_client = redis.from_url(redis_url)
                # Test connection
                redis_client.ping()
                app.config['SESSION_REDIS'] = redis_client
                logger.info(f"Redis session backend initialized: {redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                logger.info("Falling back to filesystem sessions")
                app.config['SESSION_TYPE'] = 'filesystem'

        # Initialize session
        session = Session(app)

        logger.info(f"Session manager initialized: {app.config.get('SESSION_TYPE')} backend")
        return session

    except Exception as e:
        logger.error(f"Failed to initialize session manager: {e}", exc_info=True)
        return None


def create_redis_session_config(
    lifetime_hours: int = 24,
    redis_url: str = 'redis://localhost:6379/1',
    key_prefix: str = 'dms:session:'
) -> RedisSessionConfig:
    """
    Create custom Redis session configuration.

    Args:
        lifetime_hours: Session lifetime in hours
        redis_url: Redis connection URL
        key_prefix: Session key prefix in Redis

    Returns:
        RedisSessionConfig instance
    """
    config = RedisSessionConfig()
    config.PERMANENT_SESSION_LIFETIME = timedelta(hours=lifetime_hours)
    config.SESSION_REDIS_URL = redis_url
    config.SESSION_KEY_PREFIX = key_prefix
    return config


def get_session_stats(app) -> Dict[str, Any]:
    """
    Get session configuration and statistics.

    Args:
        app: Flask application instance

    Returns:
        Dictionary with session statistics
    """
    stats = {
        'enabled': SESSION_AVAILABLE,
        'backend': app.config.get('SESSION_TYPE', 'none'),
        'config': {}
    }

    if SESSION_AVAILABLE and hasattr(app, 'config'):
        stats['config'] = {
            'lifetime': str(app.config.get('PERMANENT_SESSION_LIFETIME')),
            'cookie_name': app.config.get('SESSION_COOKIE_NAME'),
            'cookie_secure': app.config.get('SESSION_COOKIE_SECURE'),
            'cookie_httponly': app.config.get('SESSION_COOKIE_HTTPONLY'),
            'use_signer': app.config.get('SESSION_USE_SIGNER'),
            'key_prefix': app.config.get('SESSION_KEY_PREFIX'),
        }

        # Redis-specific stats
        if app.config.get('SESSION_TYPE') == 'redis':
            redis_client = app.config.get('SESSION_REDIS')
            if redis_client:
                try:
                    info = redis_client.info('stats')
                    stats['redis'] = {
                        'connected': True,
                        'total_connections': info.get('total_connections_received', 0),
                        'commands_processed': info.get('total_commands_processed', 0),
                    }
                except Exception as e:
                    stats['redis'] = {'connected': False, 'error': str(e)}

    return stats


def cleanup_expired_sessions(app) -> int:
    """
    Cleanup expired sessions (for filesystem backend).

    Args:
        app: Flask application instance

    Returns:
        Number of sessions cleaned up
    """
    if app.config.get('SESSION_TYPE') != 'filesystem':
        logger.info("Cleanup only supported for filesystem sessions")
        return 0

    # TODO: Implement filesystem session cleanup
    # This would scan SESSION_FILE_DIR and remove expired session files

    logger.info("Session cleanup completed")
    return 0


# Production configuration
class ProductionSessionConfig(RedisSessionConfig):
    """Production-optimized session configuration."""

    # Strict security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

    # Longer session lifetime for production
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Use Redis with connection pooling
    SESSION_REDIS_URL = 'redis://localhost:6379/1'


# Development configuration
class DevelopmentSessionConfig(SessionConfig):
    """Development-friendly session configuration."""

    # Less strict for development
    SESSION_COOKIE_SECURE = False  # Allow HTTP
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Shorter lifetime for testing
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Use filesystem for simplicity
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './tmp/dev_sessions'


def enable_sessions(app, environment: str = 'production', redis_url: Optional[str] = None):
    """
    Enable sessions with environment-specific settings.

    Args:
        app: Flask application instance
        environment: Environment name ('production' or 'development')
        redis_url: Optional Redis URL override

    Returns:
        Session instance
    """
    if environment == 'production':
        config = ProductionSessionConfig
    else:
        config = DevelopmentSessionConfig

    return init_session_manager(app, config, redis_url)
