"""
🤖 AGI-Ready Platform Services v4.5.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 10-50x faster, full features, requires numpy

Complete AGI implementation with multi-modal reasoning, continual learning,
meta-learning, knowledge graphs, cognitive architecture.

Version: 4.5.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "4.5.0"

# ALWAYS import Pure Python version
from .agi_services import (
    # Enums
    ModalityType,
    LearningStrategy,
    MetaLearningAlgorithm,
    
    # Dataclasses
    MultiModalInput,
    ReasoningStep,
    LearningTask,
    
    # Classes (Pure Python)
    MultiModalReasoner as MultiModalReasonerPython,
    ContinualLearner as ContinualLearnerPython,
    MetaLearningSystem as MetaLearningSystemPython,
    KnowledgeGraphEngine as KnowledgeGraphEnginePython,
    CognitiveArchitecture as CognitiveArchitecturePython,
    TransferLearningEngine as TransferLearningEnginePython,
    EthicalAIFramework as EthicalAIFrameworkPython,
    
    # Singletons (Pure Python)
    get_multi_modal_reasoner as get_multi_modal_reasoner_python,
    get_continual_learner as get_continual_learner_python,
    get_meta_learning_system as get_meta_learning_system_python,
    get_knowledge_graph as get_knowledge_graph_python,
    get_cognitive_architecture as get_cognitive_architecture_python,
    get_transfer_learning as get_transfer_learning_python,
    get_ethical_framework as get_ethical_framework_python,
)

# TRY to import NumPy version
try:
    from .agi_services_numpy import (
        MultiModalReasoner as MultiModalReasonerNumpy,
        ContinualLearner as ContinualLearnerNumpy,
        MetaLearningSystem as MetaLearningSystemNumpy,
        KnowledgeGraphEngine as KnowledgeGraphEngineNumpy,
        CognitiveArchitecture as CognitiveArchitectureNumpy,
        TransferLearningEngine as TransferLearningEngineNumpy,
        EthicalAIFramework as EthicalAIFrameworkNumpy,
        
        get_multi_modal_reasoner as get_multi_modal_reasoner_numpy,
        get_continual_learner as get_continual_learner_numpy,
        get_meta_learning_system as get_meta_learning_system_numpy,
        get_knowledge_graph as get_knowledge_graph_numpy,
        get_cognitive_architecture as get_cognitive_architecture_numpy,
        get_transfer_learning as get_transfer_learning_numpy,
        get_ethical_framework as get_ethical_framework_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases
if HAS_NUMPY:
    MultiModalReasoner = MultiModalReasonerNumpy
    ContinualLearner = ContinualLearnerNumpy
    MetaLearningSystem = MetaLearningSystemNumpy
    KnowledgeGraphEngine = KnowledgeGraphEngineNumpy
    CognitiveArchitecture = CognitiveArchitectureNumpy
    TransferLearningEngine = TransferLearningEngineNumpy
    EthicalAIFramework = EthicalAIFrameworkNumpy
    
    get_multi_modal_reasoner = get_multi_modal_reasoner_numpy
    get_continual_learner = get_continual_learner_numpy
    get_meta_learning_system = get_meta_learning_system_numpy
    get_knowledge_graph = get_knowledge_graph_numpy
    get_cognitive_architecture = get_cognitive_architecture_numpy
    get_transfer_learning = get_transfer_learning_numpy
    get_ethical_framework = get_ethical_framework_numpy
else:
    MultiModalReasoner = MultiModalReasonerPython
    ContinualLearner = ContinualLearnerPython
    MetaLearningSystem = MetaLearningSystemPython
    KnowledgeGraphEngine = KnowledgeGraphEnginePython
    CognitiveArchitecture = CognitiveArchitecturePython
    TransferLearningEngine = TransferLearningEnginePython
    EthicalAIFramework = EthicalAIFrameworkPython
    
    get_multi_modal_reasoner = get_multi_modal_reasoner_python
    get_continual_learner = get_continual_learner_python
    get_meta_learning_system = get_meta_learning_system_python
    get_knowledge_graph = get_knowledge_graph_python
    get_cognitive_architecture = get_cognitive_architecture_python
    get_transfer_learning = get_transfer_learning_python
    get_ethical_framework = get_ethical_framework_python

__all__ = [
    "__version__",
    "ModalityType",
    "LearningStrategy",
    "MetaLearningAlgorithm",
    "MultiModalInput",
    "ReasoningStep",
    "LearningTask",
    "MultiModalReasoner",
    "ContinualLearner",
    "MetaLearningSystem",
    "KnowledgeGraphEngine",
    "CognitiveArchitecture",
    "TransferLearningEngine",
    "EthicalAIFramework",
    "get_multi_modal_reasoner",
    "get_continual_learner",
    "get_meta_learning_system",
    "get_knowledge_graph",
    "get_cognitive_architecture",
    "get_transfer_learning",
    "get_ethical_framework",
    "HAS_NUMPY",
]
