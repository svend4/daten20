"""
AI Safety, Robustness & Alignment Platform v18.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 20-50x faster, full features, requires numpy

The best available version is automatically selected.

Comprehensive system for ensuring AI systems are safe, robust, aligned with
human values, and trustworthy.

Version: 18.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "18.0.0"

# ALWAYS import Pure Python version (baseline, always available)
from .ai_safety_services import (
    # Enums
    AttackType,
    AlignmentMethod,
    FairnessMetric,
    PrivacyMechanism,
    
    # Dataclasses
    AdversarialExample,
    RobustnessMetrics,
    AlignmentResult,
    SafetyAlert,
    UncertaintyEstimate,
    FairnessReport,
    PrivacyAudit,
    GovernanceRecord,
    AISafetyConfig,
    
    # Classes (Pure Python - simplified)
    AdversarialRobustnessSystem as AdversarialRobustnessSystemPython,
    ModelAlignmentSystem as ModelAlignmentSystemPython,
    SafetyMonitoringRedTeaming as SafetyMonitoringRedTeamingPython,
    UncertaintyQuantification as UncertaintyQuantificationPython,
    FairnessBiasMitigation as FairnessBiasMitigationPython,
    PrivacyDifferentialPrivacy as PrivacyDifferentialPrivacyPython,
    AIGovernanceAuditing as AIGovernanceAuditingPython,
    IntegratedAISafetySystem as IntegratedAISafetySystemPython,
    
    # Singletons (Pure Python)
    get_adversarial_robustness_system as get_adversarial_robustness_system_python,
    get_model_alignment_system as get_model_alignment_system_python,
    get_safety_monitoring_red_teaming as get_safety_monitoring_red_teaming_python,
    get_uncertainty_quantification as get_uncertainty_quantification_python,
    get_fairness_bias_mitigation as get_fairness_bias_mitigation_python,
    get_privacy_differential_privacy as get_privacy_differential_privacy_python,
    get_ai_governance_auditing as get_ai_governance_auditing_python,
    get_ai_safety_system as get_ai_safety_system_python,
)

# TRY to import NumPy version (optional, faster, full features)
try:
    from .ai_safety_services_numpy import (
        # Classes (NumPy version - full features)
        AdversarialRobustnessSystem as AdversarialRobustnessSystemNumpy,
        ModelAlignmentSystem as ModelAlignmentSystemNumpy,
        SafetyMonitoringRedTeaming as SafetyMonitoringRedTeamingNumpy,
        UncertaintyQuantification as UncertaintyQuantificationNumpy,
        FairnessBiasMitigation as FairnessBiasMitigationNumpy,
        PrivacyDifferentialPrivacy as PrivacyDifferentialPrivacyNumpy,
        AIGovernanceAuditing as AIGovernanceAuditingNumpy,
        IntegratedAISafetySystem as IntegratedAISafetySystemNumpy,
        
        # Singletons (NumPy version)
        get_adversarial_robustness_system as get_adversarial_robustness_system_numpy,
        get_model_alignment_system as get_model_alignment_system_numpy,
        get_safety_monitoring_red_teaming as get_safety_monitoring_red_teaming_numpy,
        get_uncertainty_quantification as get_uncertainty_quantification_numpy,
        get_fairness_bias_mitigation as get_fairness_bias_mitigation_numpy,
        get_privacy_differential_privacy as get_privacy_differential_privacy_numpy,
        get_ai_governance_auditing as get_ai_governance_auditing_numpy,
        get_ai_safety_system as get_ai_safety_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (20-50x faster, more features)
    AdversarialRobustnessSystem = AdversarialRobustnessSystemNumpy
    ModelAlignmentSystem = ModelAlignmentSystemNumpy
    SafetyMonitoringRedTeaming = SafetyMonitoringRedTeamingNumpy
    UncertaintyQuantification = UncertaintyQuantificationNumpy
    FairnessBiasMitigation = FairnessBiasMitigationNumpy
    PrivacyDifferentialPrivacy = PrivacyDifferentialPrivacyNumpy
    AIGovernanceAuditing = AIGovernanceAuditingNumpy
    IntegratedAISafetySystem = IntegratedAISafetySystemNumpy
    
    # Use NumPy getters
    get_adversarial_robustness_system = get_adversarial_robustness_system_numpy
    get_model_alignment_system = get_model_alignment_system_numpy
    get_safety_monitoring_red_teaming = get_safety_monitoring_red_teaming_numpy
    get_uncertainty_quantification = get_uncertainty_quantification_numpy
    get_fairness_bias_mitigation = get_fairness_bias_mitigation_numpy
    get_privacy_differential_privacy = get_privacy_differential_privacy_numpy
    get_ai_governance_auditing = get_ai_governance_auditing_numpy
    get_ai_safety_system = get_ai_safety_system_numpy
else:
    # NumPy not available - use Pure Python (simplified)
    AdversarialRobustnessSystem = AdversarialRobustnessSystemPython
    ModelAlignmentSystem = ModelAlignmentSystemPython
    SafetyMonitoringRedTeaming = SafetyMonitoringRedTeamingPython
    UncertaintyQuantification = UncertaintyQuantificationPython
    FairnessBiasMitigation = FairnessBiasMitigationPython
    PrivacyDifferentialPrivacy = PrivacyDifferentialPrivacyPython
    AIGovernanceAuditing = AIGovernanceAuditingPython
    IntegratedAISafetySystem = IntegratedAISafetySystemPython
    
    # Use Pure Python getters
    get_adversarial_robustness_system = get_adversarial_robustness_system_python
    get_model_alignment_system = get_model_alignment_system_python
    get_safety_monitoring_red_teaming = get_safety_monitoring_red_teaming_python
    get_uncertainty_quantification = get_uncertainty_quantification_python
    get_fairness_bias_mitigation = get_fairness_bias_mitigation_python
    get_privacy_differential_privacy = get_privacy_differential_privacy_python
    get_ai_governance_auditing = get_ai_governance_auditing_python
    get_ai_safety_system = get_ai_safety_system_python

__all__ = [
    # Version
    "__version__",
    
    # Enums
    "AttackType",
    "AlignmentMethod",
    "FairnessMetric",
    "PrivacyMechanism",
    
    # Dataclasses
    "AdversarialExample",
    "RobustnessMetrics",
    "AlignmentResult",
    "SafetyAlert",
    "UncertaintyEstimate",
    "FairnessReport",
    "PrivacyAudit",
    "GovernanceRecord",
    "AISafetyConfig",
    
    # Core Systems (auto-select best version)
    "AdversarialRobustnessSystem",
    "ModelAlignmentSystem",
    "SafetyMonitoringRedTeaming",
    "UncertaintyQuantification",
    "FairnessBiasMitigation",
    "PrivacyDifferentialPrivacy",
    "AIGovernanceAuditing",
    "IntegratedAISafetySystem",
    
    # Pure Python versions (always available)
    "AdversarialRobustnessSystemPython",
    "ModelAlignmentSystemPython",
    "SafetyMonitoringRedTeamingPython",
    "UncertaintyQuantificationPython",
    "FairnessBiasMitigationPython",
    "PrivacyDifferentialPrivacyPython",
    "AIGovernanceAuditingPython",
    "IntegratedAISafetySystemPython",
    
    # Singletons
    "get_adversarial_robustness_system",
    "get_model_alignment_system",
    "get_safety_monitoring_red_teaming",
    "get_uncertainty_quantification",
    "get_fairness_bias_mitigation",
    "get_privacy_differential_privacy",
    "get_ai_governance_auditing",
    "get_ai_safety_system",
    
    # Pure Python singleton getters
    "get_adversarial_robustness_system_python",
    "get_model_alignment_system_python",
    "get_safety_monitoring_red_teaming_python",
    "get_uncertainty_quantification_python",
    "get_fairness_bias_mitigation_python",
    "get_privacy_differential_privacy_python",
    "get_ai_governance_auditing_python",
    "get_ai_safety_system_python",
    
    # Dual-version flag
    "HAS_NUMPY",
]
