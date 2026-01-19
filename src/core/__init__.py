"""
Core components for the Document Management System (v1.0-v2.3)

This module provides the foundational components:
- Database management
- Authentication & Authorization
- Document parsing & validation
- Export functionality
- Caching & Monitoring
- Backup & Audit

Note: Some imports are optional to avoid dependency issues.
"""

# Optional imports with fallbacks
try:
    from .database import Database
    from .database_universal import UniversalDatabase
except ImportError as e:
    print(f"Warning: Database not available: {e}")
    Database = None
    UniversalDatabase = None

try:
    from .auth import AuthService
except ImportError as e:
    print(f"Warning: AuthService not available (requires flask, jwt): {e}")
    AuthService = None

try:
    from .parser import TemplateParser
except ImportError as e:
    print(f"Warning: TemplateParser not available: {e}")
    TemplateParser = None

try:
    from .validator import TemplateValidator
except ImportError as e:
    print(f"Warning: TemplateValidator not available: {e}")
    TemplateValidator = None

from .exporter import DocumentExporter

try:
    from .cache import CacheService
except ImportError as e:
    print(f"Warning: CacheService not available: {e}")
    CacheService = None

try:
    from .monitoring import MonitoringService
except ImportError as e:
    print(f"Warning: MonitoringService not available: {e}")
    MonitoringService = None

try:
    from .backup import BackupService
except ImportError as e:
    print(f"Warning: BackupService not available: {e}")
    BackupService = None

try:
    from .audit import AuditService
except ImportError as e:
    print(f"Warning: AuditService not available: {e}")
    AuditService = None

from .logger import get_logger, setup_logger

__all__ = [
    # Database
    "Database",
    "UniversalDatabase",
    # Auth
    "AuthService",
    # Document Processing
    "TemplateParser",
    "TemplateValidator",
    "DocumentExporter",
    # Services
    "CacheService",
    "MonitoringService",
    "BackupService",
    "AuditService",
    # Logging
    "setup_logger",
    "get_logger",
]

__version__ = "2.5.1"
