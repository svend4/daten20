"""
Configuration Management Module

Centralized configuration management for the Document Management System.
Supports environment variables, .env files, and multiple deployment environments.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Base configuration class with common settings."""

    # Application
    APP_NAME = "Document Management System"
    VERSION = "2.1.0"

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    EXPORT_DIR = DATA_DIR / "exports"
    TEMPLATE_DIR = DATA_DIR / "templates"
    LOG_DIR = BASE_DIR / "logs"

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('APP_PORT', 5000))

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATA_DIR}/db/services.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))

    # Security
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB

    # API
    API_VERSION = os.getenv('API_VERSION', 'v1')
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100/hour')
    API_KEY_REQUIRED = os.getenv('API_KEY_REQUIRED', 'false').lower() == 'true'

    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')

    # Email
    ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', 'false').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@dms.local')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@dms.local')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(LOG_DIR / 'app.log'))
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Features
    ENABLE_WEBHOOKS = os.getenv('ENABLE_WEBHOOKS', 'false').lower() == 'true'
    ENABLE_API_DOCS = os.getenv('ENABLE_API_DOCS', 'true').lower() == 'true'
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'false').lower() == 'true'

    # Swagger
    SWAGGER = {
        'title': APP_NAME,
        'version': VERSION,
        'description': 'REST API for Document Management System',
        'termsOfService': '',
        'contact': {
            'email': 'admin@dms.local'
        },
        'license': {
            'name': 'MIT',
            'url': 'https://opensource.org/licenses/MIT'
        }
    }

    # PDF Export
    PDF_TEMPLATE_DIR = TEMPLATE_DIR / 'pdf'
    PDF_LOGO_PATH = BASE_DIR / 'web' / 'static' / 'images' / 'logo.png'
    PDF_FONT_DIR = BASE_DIR / 'fonts'

    # Webhooks
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', 30))
    WEBHOOK_RETRY_COUNT = int(os.getenv('WEBHOOK_RETRY_COUNT', 3))

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        for directory in [cls.DATA_DIR, cls.EXPORT_DIR, cls.TEMPLATE_DIR, cls.LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        # Create database directory
        db_dir = cls.DATA_DIR / 'db'
        db_dir.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True

    # Override with environment variables for production
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production

    @classmethod
    def validate(cls):
        """Validate production configuration."""
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be set to a secure random string in production. "
                "Set the SECRET_KEY environment variable."
            )


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True

    # Use in-memory database for tests
    DATABASE_URL = 'sqlite:///:memory:'

    # Disable features that require external services
    ENABLE_EMAIL = False
    ENABLE_WEBHOOKS = False

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: Optional[str] = None) -> Config:
    """
    Get configuration object based on environment.

    Args:
        env: Environment name (development, production, testing).
             If None, uses FLASK_ENV environment variable.

    Returns:
        Configuration object for the specified environment.
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    config_class = config_by_name.get(env, DevelopmentConfig)

    # Validate production config
    if env == 'production':
        config_class.validate()

    # Ensure directories exist
    config_class.ensure_directories()

    return config_class


# Export current config
current_config = get_config()
