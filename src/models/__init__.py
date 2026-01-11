"""
Data models for services, templates, and financial calculations (v1.0-v2.3)

Core data models for the document management system:
- Service models (BasicInfo, Funding, etc.)
- Financial models and calculations
- Template definitions
"""

from .service import Service, BasicInfo, Funding, SystemSettings, ServiceConfig
from .financial import FinancialParameters, FinancialData
from .template import Template, TemplateField

__all__ = [
    # Service Models
    "Service",
    "BasicInfo",
    "Funding",
    "SystemSettings",
    "ServiceConfig",
    # Financial Models
    "FinancialParameters",
    "FinancialData",
    # Template Models
    "Template",
    "TemplateField",
]

__version__ = "2.3.0"
