"""
AI Safety, Robustness & Alignment Platform v18.0

Comprehensive system for ensuring AI systems are safe, robust, aligned with
human values, and trustworthy.

This module provides:
- Adversarial robustness against attacks (FGSM, PGD, C&W)
- Model alignment with human values (RLHF, constitutional AI)
- Continuous safety monitoring and red-teaming
- Uncertainty quantification and OOD detection
- Fairness metrics and bias mitigation
- Privacy-preserving training (differential privacy)
- AI governance and auditing (model cards, compliance)

Example usage:
    from ai_safety import get_adversarial_robustness_system

    robustness = get_adversarial_robustness_system()

    # Generate adversarial example
    adv_example = await robustness.generate_adversarial_example(
        input_data=image,
        true_label=5,
        model_prediction=5,
        attack_type=AttackType.PGD
    )

    # Evaluate robustness
    metrics = await robustness.evaluate_robustness(
        model_id="resnet50",
        test_dataset_size=1000
    )
"""

__version__ = "18.0.0"
__author__ = "Document Management System Team"

# Import main service classes
from .ai_safety_services import (  # Core Systems; Enums; Data Classes; Singleton Getters
    AdversarialExample,
    AdversarialRobustnessSystem,
    AIGovernanceAuditing,
    AISafetyConfig,
    AlignmentMethod,
    AlignmentResult,
    AttackType,
    FairnessBiasMitigation,
    FairnessMetric,
    FairnessReport,
    GovernanceRecord,
    IntegratedAISafetySystem,
    ModelAlignmentSystem,
    PrivacyAudit,
    PrivacyDifferentialPrivacy,
    PrivacyMechanism,
    RobustnessMetrics,
    SafetyAlert,
    SafetyMonitoringRedTeaming,
    UncertaintyEstimate,
    UncertaintyQuantification,
    get_adversarial_robustness_system,
    get_ai_governance_auditing,
    get_ai_safety_system,
    get_fairness_bias_mitigation,
    get_model_alignment_system,
    get_privacy_differential_privacy,
    get_safety_monitoring_red_teaming,
    get_uncertainty_quantification,
)

__all__ = [
    # Version
    "__version__",
    # Core Systems
    "AdversarialRobustnessSystem",
    "ModelAlignmentSystem",
    "SafetyMonitoringRedTeaming",
    "UncertaintyQuantification",
    "FairnessBiasMitigation",
    "PrivacyDifferentialPrivacy",
    "AIGovernanceAuditing",
    # Integrated System
    "IntegratedAISafetySystem",
    # Enums
    "AttackType",
    "AlignmentMethod",
    "FairnessMetric",
    "PrivacyMechanism",
    # Data Classes
    "AdversarialExample",
    "RobustnessMetrics",
    "AlignmentResult",
    "SafetyAlert",
    "UncertaintyEstimate",
    "FairnessReport",
    "PrivacyAudit",
    "GovernanceRecord",
    "AISafetyConfig",
    # Singleton Getters
    "get_adversarial_robustness_system",
    "get_model_alignment_system",
    "get_safety_monitoring_red_teaming",
    "get_uncertainty_quantification",
    "get_fairness_bias_mitigation",
    "get_privacy_differential_privacy",
    "get_ai_governance_auditing",
    "get_ai_safety_system",
]
