"""
Compliance Module

Provides compliance frameworks for:
- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOC 2 (Service Organization Control 2)
"""

from .gdpr import (
    ConsentPurpose,
    DataSubjectRight,
    GDPRComplianceEngine,
    LegalBasis,
    configure_gdpr_engine,
    get_gdpr_engine,
)
from .hipaa import AccessLevel, HIPAAComplianceEngine, PHICategory, configure_hipaa_engine, get_hipaa_engine
from .soc2 import ControlStatus, SOC2ComplianceEngine, TrustServiceCategory, configure_soc2_engine, get_soc2_engine

__all__ = [
    "GDPRComplianceEngine",
    "get_gdpr_engine",
    "configure_gdpr_engine",
    "HIPAAComplianceEngine",
    "get_hipaa_engine",
    "configure_hipaa_engine",
    "SOC2ComplianceEngine",
    "get_soc2_engine",
    "configure_soc2_engine",
    "DataSubjectRight",
    "ConsentPurpose",
    "LegalBasis",
    "PHICategory",
    "AccessLevel",
    "TrustServiceCategory",
    "ControlStatus",
]
