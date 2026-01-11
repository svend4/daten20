"""
Continual Learning & Lifelong AI Platform v21.0

AI that learns continuously throughout its lifetime, accumulating knowledge,
adapting to new tasks, and improving performance without catastrophic forgetting.

Example usage:
    from continual_learning import get_continual_learning, get_lifelong_memory

    # Learn new task without forgetting
    cl_system = get_continual_learning()
    performance = await cl_system.learn_task(new_task, method=ContinualLearningMethod.EWC)

    # Store and retrieve lifelong memories
    memory_system = get_lifelong_memory()
    memory = await memory_system.encode_memory(experience, MemoryType.EPISODIC)
"""

__version__ = '21.0.0'
__author__ = 'Document Management System Team'

from .continual_learning_services import (
    # Core Systems
    ContinualLearningAlgorithms,
    LifelongMemorySystems,
    KnowledgeAccumulationTransfer,
    MetaLearning,
    CurriculumLearning,
    ExperienceReplayConsolidation,
    SelfAssessmentCapabilityTracking,

    # Enums
    ContinualLearningMethod,
    MemoryType,
    TransferType,
    CurriculumStrategy,
    ReplayPriority,

    # Data Classes
    Task,
    Experience,
    Memory,
    Skill,
    MetaLearningState,
    Curriculum,
    CapabilityAssessment,

    # Singleton Getters
    get_continual_learning,
    get_lifelong_memory,
    get_knowledge_transfer,
    get_meta_learning,
    get_curriculum_learning,
    get_replay_consolidation,
    get_self_assessment,
)

__all__ = [
    '__version__',

    # Core Systems
    'ContinualLearningAlgorithms',
    'LifelongMemorySystems',
    'KnowledgeAccumulationTransfer',
    'MetaLearning',
    'CurriculumLearning',
    'ExperienceReplayConsolidation',
    'SelfAssessmentCapabilityTracking',

    # Enums
    'ContinualLearningMethod',
    'MemoryType',
    'TransferType',
    'CurriculumStrategy',
    'ReplayPriority',

    # Data Classes
    'Task',
    'Experience',
    'Memory',
    'Skill',
    'MetaLearningState',
    'Curriculum',
    'CapabilityAssessment',

    # Singleton Getters
    'get_continual_learning',
    'get_lifelong_memory',
    'get_knowledge_transfer',
    'get_meta_learning',
    'get_curriculum_learning',
    'get_replay_consolidation',
    'get_self_assessment',
]
