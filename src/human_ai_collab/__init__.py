"""
Human-AI Collaboration & Augmentation Platform v20.0

Seamless collaboration between humans and AI through mixed-initiative interaction,
shared understanding, capability augmentation, and transparent cooperation.

Example usage:
    from human_ai_collab import get_collaborative_task_management, get_human_intent_understanding

    # Decompose task and allocate roles
    task_mgmt = get_collaborative_task_management()
    subtasks = await task_mgmt.decompose_task("Build a web application")
    for task in subtasks:
        role = await task_mgmt.allocate_role(task)

    # Understand user intent
    intent_system = get_human_intent_understanding()
    intent = await intent_system.understand_intent("Help me analyze this data")
"""

__version__ = "20.0.0"
__author__ = "Document Management System Team"

from .human_ai_collab_services import (  # Core Systems; Enums; Data Classes; Singleton Getters
    AICapabilityMatching,
    AugmentationResult,
    AugmentationType,
    Capability,
    CollaborativeTask,
    CollaborativeTaskManagement,
    ControlMode,
    Explanation,
    ExplanationType,
    HumanAICollabConfig,
    HumanIntentUnderstanding,
    HumanPerformanceAugmentation,
    Intent,
    IntentType,
    IntegratedHumanAICollabSystem,
    MentalModel,
    MixedInitiativeControl,
    SharedMentalModels,
    TaskRole,
    TrustMetrics,
    TrustTransparencyExplainability,
    get_ai_capability_matching,
    get_collaborative_task_management,
    get_human_ai_collab_system,
    get_human_intent_understanding,
    get_human_performance_augmentation,
    get_mixed_initiative_control,
    get_shared_mental_models,
    get_trust_transparency_explainability,
)

__all__ = [
    "__version__",
    # Core Systems
    "CollaborativeTaskManagement",
    "HumanIntentUnderstanding",
    "AICapabilityMatching",
    "SharedMentalModels",
    "MixedInitiativeControl",
    "HumanPerformanceAugmentation",
    "TrustTransparencyExplainability",
    # Integrated System
    "IntegratedHumanAICollabSystem",
    # Enums
    "TaskRole",
    "IntentType",
    "ControlMode",
    "AugmentationType",
    "ExplanationType",
    # Data Classes
    "CollaborativeTask",
    "Intent",
    "Capability",
    "MentalModel",
    "AugmentationResult",
    "Explanation",
    "TrustMetrics",
    "HumanAICollabConfig",
    # Singleton Getters
    "get_collaborative_task_management",
    "get_human_intent_understanding",
    "get_ai_capability_matching",
    "get_shared_mental_models",
    "get_mixed_initiative_control",
    "get_human_performance_augmentation",
    "get_trust_transparency_explainability",
    "get_human_ai_collab_system",
]
