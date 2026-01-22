"""
Continual Learning & Lifelong AI Platform v21.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 20-50x faster, full features, requires numpy

AI that learns continuously throughout its lifetime, accumulating knowledge,
adapting to new tasks, and improving performance without catastrophic forgetting.

Version: 21.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "21.0.0"

# ALWAYS import Pure Python version (baseline, always available)
from .continual_learning_services import (
    # Enums
    ContinualLearningMethod,
    MemoryType,
    TransferType,
    CurriculumStrategy,
    ReplayPriority,
    
    # Dataclasses
    Task,
    Experience,
    Memory,
    Skill,
    MetaLearningState,
    Curriculum,
    CapabilityAssessment,
    
    # Classes (Pure Python - simplified)
    ContinualLearningAlgorithms as ContinualLearningAlgorithmsPython,
    LifelongMemorySystem as LifelongMemorySystemPython,
    KnowledgeTransferSystem as KnowledgeTransferSystemPython,
    MetaLearningSystem as MetaLearningSystemPython,
    CurriculumLearningSystem as CurriculumLearningSystemPython,
    ExperienceReplaySystem as ExperienceReplaySystemPython,
    SelfAssessmentSystem as SelfAssessmentSystemPython,
    IntegratedContinualLearningSystem as IntegratedContinualLearningSystemPython,
    
    # Singletons (Pure Python)
    get_continual_learning_algorithms as get_continual_learning_algorithms_python,
    get_lifelong_memory_system as get_lifelong_memory_system_python,
    get_knowledge_transfer_system as get_knowledge_transfer_system_python,
    get_meta_learning_system as get_meta_learning_system_python,
    get_curriculum_learning_system as get_curriculum_learning_system_python,
    get_experience_replay_system as get_experience_replay_system_python,
    get_self_assessment_system as get_self_assessment_system_python,
    get_integrated_continual_learning_system as get_integrated_continual_learning_system_python,
)

# TRY to import NumPy version (optional, faster, full features)
try:
    from .continual_learning_services_numpy import (
        # Classes (NumPy version - full features)
        ContinualLearningAlgorithms as ContinualLearningAlgorithmsNumpy,
        LifelongMemorySystems as LifelongMemorySystemNumpy,
        KnowledgeAccumulationTransfer as KnowledgeTransferSystemNumpy,
        MetaLearning as MetaLearningSystemNumpy,
        CurriculumLearning as CurriculumLearningSystemNumpy,
        ExperienceReplayConsolidation as ExperienceReplaySystemNumpy,
        SelfAssessmentCapabilityTracking as SelfAssessmentSystemNumpy,
        IntegratedContinualLearningSystem as IntegratedContinualLearningSystemNumpy,
        
        # Singletons (NumPy version)
        get_continual_learning as get_continual_learning_algorithms_numpy,
        get_lifelong_memory as get_lifelong_memory_system_numpy,
        get_knowledge_transfer as get_knowledge_transfer_system_numpy,
        get_meta_learning as get_meta_learning_system_numpy,
        get_curriculum_learning as get_curriculum_learning_system_numpy,
        get_replay_consolidation as get_experience_replay_system_numpy,
        get_self_assessment as get_self_assessment_system_numpy,
        get_continual_learning_system as get_integrated_continual_learning_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (20-50x faster, full features)
    ContinualLearningAlgorithms = ContinualLearningAlgorithmsNumpy
    LifelongMemorySystem = LifelongMemorySystemNumpy
    KnowledgeTransferSystem = KnowledgeTransferSystemNumpy
    MetaLearningSystem = MetaLearningSystemNumpy
    CurriculumLearningSystem = CurriculumLearningSystemNumpy
    ExperienceReplaySystem = ExperienceReplaySystemNumpy
    SelfAssessmentSystem = SelfAssessmentSystemNumpy
    IntegratedContinualLearningSystem = IntegratedContinualLearningSystemNumpy
    
    # Use NumPy getters
    get_continual_learning_algorithms = get_continual_learning_algorithms_numpy
    get_lifelong_memory_system = get_lifelong_memory_system_numpy
    get_knowledge_transfer_system = get_knowledge_transfer_system_numpy
    get_meta_learning_system = get_meta_learning_system_numpy
    get_curriculum_learning_system = get_curriculum_learning_system_numpy
    get_experience_replay_system = get_experience_replay_system_numpy
    get_self_assessment_system = get_self_assessment_system_numpy
    get_integrated_continual_learning_system = get_integrated_continual_learning_system_numpy
else:
    # NumPy not available - use Pure Python (simplified)
    ContinualLearningAlgorithms = ContinualLearningAlgorithmsPython
    LifelongMemorySystem = LifelongMemorySystemPython
    KnowledgeTransferSystem = KnowledgeTransferSystemPython
    MetaLearningSystem = MetaLearningSystemPython
    CurriculumLearningSystem = CurriculumLearningSystemPython
    ExperienceReplaySystem = ExperienceReplaySystemPython
    SelfAssessmentSystem = SelfAssessmentSystemPython
    IntegratedContinualLearningSystem = IntegratedContinualLearningSystemPython
    
    # Use Pure Python getters
    get_continual_learning_algorithms = get_continual_learning_algorithms_python
    get_lifelong_memory_system = get_lifelong_memory_system_python
    get_knowledge_transfer_system = get_knowledge_transfer_system_python
    get_meta_learning_system = get_meta_learning_system_python
    get_curriculum_learning_system = get_curriculum_learning_system_python
    get_experience_replay_system = get_experience_replay_system_python
    get_self_assessment_system = get_self_assessment_system_python
    get_integrated_continual_learning_system = get_integrated_continual_learning_system_python

__all__ = [
    # Version
    "__version__",
    
    # Enums
    "ContinualLearningMethod",
    "MemoryType",
    "TransferType",
    "CurriculumStrategy",
    "ReplayPriority",
    
    # Dataclasses
    "Task",
    "Experience",
    "Memory",
    "Skill",
    "MetaLearningState",
    "Curriculum",
    "CapabilityAssessment",
    
    # Core Systems (auto-select best version)
    "ContinualLearningAlgorithms",
    "LifelongMemorySystem",
    "KnowledgeTransferSystem",
    "MetaLearningSystem",
    "CurriculumLearningSystem",
    "ExperienceReplaySystem",
    "SelfAssessmentSystem",
    "IntegratedContinualLearningSystem",
    
    # Pure Python versions (always available)
    "ContinualLearningAlgorithmsPython",
    "LifelongMemorySystemPython",
    "KnowledgeTransferSystemPython",
    "MetaLearningSystemPython",
    "CurriculumLearningSystemPython",
    "ExperienceReplaySystemPython",
    "SelfAssessmentSystemPython",
    "IntegratedContinualLearningSystemPython",
    
    # Singletons
    "get_continual_learning_algorithms",
    "get_lifelong_memory_system",
    "get_knowledge_transfer_system",
    "get_meta_learning_system",
    "get_curriculum_learning_system",
    "get_experience_replay_system",
    "get_self_assessment_system",
    "get_integrated_continual_learning_system",
    
    # Pure Python singleton getters
    "get_continual_learning_algorithms_python",
    "get_lifelong_memory_system_python",
    "get_knowledge_transfer_system_python",
    "get_meta_learning_system_python",
    "get_curriculum_learning_system_python",
    "get_experience_replay_system_python",
    "get_self_assessment_system_python",
    "get_integrated_continual_learning_system_python",
    
    # Dual-version flag
    "HAS_NUMPY",
]
