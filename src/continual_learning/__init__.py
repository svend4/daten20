"""
Continual Learning & Lifelong AI Platform v21.0 (FUNCTIONAL)

AI that learns continuously throughout its lifetime, accumulating knowledge,
adapting to new tasks, and improving performance without catastrophic forgetting.
Version: 21.0.0 (FUNCTIONAL - uses REAL EWC algorithm!)

This module now uses REAL Elastic Weight Consolidation (EWC) to prevent
catastrophic forgetting, not mock code! Agents learn new tasks while
preserving performance on old tasks.

Example usage:
    from continual_learning import ElasticWeightConsolidation, generate_binary_task

    # Create EWC system
    ewc = ElasticWeightConsolidation(num_inputs=3, ewc_lambda=5000.0)

    # Learn task A
    task_a = generate_binary_task(task_id=1, num_samples=50, feature_idx=0)
    result_a = ewc.train_task(task_a, epochs=100, use_ewc=False)

    # Learn task B WITHOUT forgetting task A!
    task_b = generate_binary_task(task_id=2, num_samples=50, feature_idx=1)
    result_b = ewc.train_task(task_b, epochs=100, use_ewc=True)
"""

__version__ = "21.0.0"
__status__ = "FUNCTIONAL"
__author__ = "Document Management System Team"

# Import REAL EWC algorithm
from .ewc_algorithm import (
    ElasticWeightConsolidation,
    SimpleNeuron,
    EWCResult,
    generate_binary_task,
    demonstrate_catastrophic_forgetting,
    demonstrate_ewc_protection
)

from .continual_learning_services import (  # Core Systems; Enums; Data Classes; Singleton Getters
    CapabilityAssessment,
    ContinualLearningAlgorithms,
    ContinualLearningConfig,
    ContinualLearningMethod,
    Curriculum,
    CurriculumLearning,
    CurriculumStrategy,
    Experience,
    ExperienceReplayConsolidation,
    IntegratedContinualLearningSystem,
    KnowledgeAccumulationTransfer,
    LifelongMemorySystems,
    Memory,
    MemoryType,
    MetaLearning,
    MetaLearningState,
    ReplayPriority,
    SelfAssessmentCapabilityTracking,
    Skill,
    Task,
    TransferType,
    get_continual_learning,
    get_continual_learning_system,
    get_curriculum_learning,
    get_knowledge_transfer,
    get_lifelong_memory,
    get_meta_learning,
    get_replay_consolidation,
    get_self_assessment,
)

__all__ = [
    "__version__",
    # REAL EWC Algorithm
    "ElasticWeightConsolidation",
    "SimpleNeuron",
    "EWCResult",
    "generate_binary_task",
    "demonstrate_catastrophic_forgetting",
    "demonstrate_ewc_protection",
    # Core Systems
    "ContinualLearningAlgorithms",
    "LifelongMemorySystems",
    "KnowledgeAccumulationTransfer",
    "MetaLearning",
    "CurriculumLearning",
    "ExperienceReplayConsolidation",
    "SelfAssessmentCapabilityTracking",
    # Integrated System
    "IntegratedContinualLearningSystem",
    # Enums
    "ContinualLearningMethod",
    "MemoryType",
    "TransferType",
    "CurriculumStrategy",
    "ReplayPriority",
    # Data Classes
    "Task",
    "Experience",
    "Memory",
    "Skill",
    "MetaLearningState",
    "Curriculum",
    "CapabilityAssessment",
    "ContinualLearningConfig",
    # Singleton Getters
    "get_continual_learning",
    "get_lifelong_memory",
    "get_knowledge_transfer",
    "get_meta_learning",
    "get_curriculum_learning",
    "get_replay_consolidation",
    "get_self_assessment",
    "get_continual_learning_system",
]
