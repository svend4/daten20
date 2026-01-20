"""
Continual Learning & Lifelong AI Platform v21.0 (FUNCTIONAL)

AI that learns continuously throughout its lifetime, accumulating knowledge,
adapting to new tasks, and improving performance without catastrophic forgetting.
Version: 21.0.0 (FUNCTIONAL - uses REAL EWC algorithm!)

This module now uses REAL Elastic Weight Consolidation (EWC) to prevent
catastrophic forgetting, not mock code! Agents learn new tasks while
preserving performance on old tasks.

Two implementations available:
1. Pure Python (default): Zero dependencies, works everywhere
2. NumPy version: 10-100x faster, requires numpy

Example usage (Pure Python):
    from continual_learning import ElasticWeightConsolidation, generate_binary_task

    # Create EWC system (pure Python, zero dependencies)
    ewc = ElasticWeightConsolidation(num_inputs=3, ewc_lambda=5000.0)

    # Learn task A
    task_a = generate_binary_task(task_id=1, num_samples=50, feature_idx=0)
    result_a = ewc.train_task(task_a, epochs=100, use_ewc=False)

    # Learn task B WITHOUT forgetting task A!
    task_b = generate_binary_task(task_id=2, num_samples=50, feature_idx=1)
    result_b = ewc.train_task(task_b, epochs=100, use_ewc=True)

Example usage (NumPy - 10-100x faster):
    from continual_learning import ElasticWeightConsolidationNumpy, HAS_NUMPY

    if HAS_NUMPY:
        # Use NumPy version (much faster!)
        ewc = ElasticWeightConsolidationNumpy(num_inputs=3, ewc_lambda=5000.0)
        # ... same API as pure Python version
    else:
        # Fallback to pure Python
        from continual_learning import ElasticWeightConsolidation
        ewc = ElasticWeightConsolidation(num_inputs=3, ewc_lambda=5000.0)
"""

__version__ = "21.0.0"
__status__ = "FUNCTIONAL"
__author__ = "Document Management System Team"

# Import REAL EWC algorithm (Pure Python - always available)
from .ewc_algorithm import (
    ElasticWeightConsolidation,
    SimpleNeuron,
    EWCResult,
    generate_binary_task,
    demonstrate_catastrophic_forgetting,
    demonstrate_ewc_protection
)

# Import NumPy-accelerated version (optional, 10-100x faster)
try:
    from .ewc_algorithm_numpy import (
        ElasticWeightConsolidationNumpy,
        SimpleNeuronNumpy,
        EWCResult as EWCResultNumpy,
        generate_binary_task as generate_binary_task_numpy,
        demonstrate_catastrophic_forgetting as demonstrate_catastrophic_forgetting_numpy,
        demonstrate_ewc_protection as demonstrate_ewc_protection_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Import legacy services (requires numpy - only if available)
try:
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
    HAS_SERVICES = True
except ImportError:
    # Services not available (numpy required)
    HAS_SERVICES = False

__all__ = [
    "__version__",
    # REAL EWC Algorithm (Pure Python - default)
    "ElasticWeightConsolidation",
    "SimpleNeuron",
    "EWCResult",
    "generate_binary_task",
    "demonstrate_catastrophic_forgetting",
    "demonstrate_ewc_protection",
    # Version flags
    "HAS_NUMPY",
    "HAS_SERVICES",
]

# Add legacy services to exports if available (requires numpy)
if HAS_SERVICES:
    __all__.extend([
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
    ])

# Add NumPy versions to exports if available
if HAS_NUMPY:
    __all__.extend([
        "ElasticWeightConsolidationNumpy",
        "SimpleNeuronNumpy",
        "EWCResultNumpy",
        "generate_binary_task_numpy",
        "demonstrate_catastrophic_forgetting_numpy",
        "demonstrate_ewc_protection_numpy",
    ])
