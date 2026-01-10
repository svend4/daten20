"""
Compliance Module

Provides compliance frameworks for:
- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOC 2 (Service Organization Control 2)
"""

from .gdpr import (
    GDPRComplianceEngine,
    get_gdpr_engine,
    configure_gdpr_engine,
    DataSubjectRight,
    ConsentPurpose,
    LegalBasis
)

from .hipaa import (
    HIPAAComplianceEngine,
    get_hipaa_engine,
    configure_hipaa_engine,
    PHICategory,
    AccessLevel
)

from .soc2 import (
    SOC2ComplianceEngine,
    get_soc2_engine,
    configure_soc2_engine,
    TrustServiceCategory,
    ControlStatus
)

__all__ = [
    'GDPRComplianceEngine',
    'get_gdpr_engine',
    'configure_gdpr_engine',
    'HIPAAComplianceEngine',
    'get_hipaa_engine',
    'configure_hipaa_engine',
    'SOC2ComplianceEngine',
    'get_soc2_engine',
    'configure_soc2_engine',
    'DataSubjectRight',
    'ConsentPurpose',
    'LegalBasis',
    'PHICategory',
    'AccessLevel',
    'TrustServiceCategory',
    'ControlStatus'
]
