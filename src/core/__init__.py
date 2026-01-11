"""
Core components for the Document Management System (v1.0-v2.3)

This module provides the foundational components:
- Database management
- Authentication & Authorization
- Document parsing & validation
- Export functionality
- Caching & Monitoring
- Backup & Audit
"""

from .database import Database
from .auth import AuthService
from .parser import TemplateParser
from .validator import TemplateValidator
from .exporter import DocumentExporter
from .cache import CacheService
from .monitoring import MonitoringService
from .backup import BackupService
from .audit import AuditService
from .logger import setup_logger, get_logger

__all__ = [
    # Database
    "Database",
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

__version__ = "2.3.0"
