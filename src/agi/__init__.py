"""
🤖 AGI-Ready Platform Module

Provides foundational infrastructure for Artificial General Intelligence with
multi-modal reasoning, continual learning, meta-learning, knowledge graphs,
cognitive architecture, transfer learning, and ethical AI frameworks.

Version: 4.5.0
"""

__version__ = "4.5.0"

from .agi_services import (  # Multi-Modal Reasoning; Continual Learning; Meta-Learning; Knowledge Graph; Cognitive Architecture; Transfer Learning; Ethical AI
    AdaptationResult,
    AttentionState,
    BiasReport,
    CognitiveArchitecture,
    ContinualLearner,
    Domain,
    Entity,
    EthicalAIFramework,
    EthicalConstraint,
    EthicalPrinciple,
    ExplanationResult,
    FewShotTask,
    Goal,
    InferenceType,
    KnowledgeGraphEngine,
    LearningMetrics,
    LearningStrategy,
    LearningTask,
    MemoryItem,
    MemoryType,
    MetaLearningAlgorithm,
    MetaLearningSystem,
    ModalityType,
    MultiModalInput,
    MultiModalReasoner,
    ReasoningStep,
    Relation,
    TransferLearningHub,
    TransferMethod,
    TransferResult,
    TransferTask,
    Triple,
    get_cognitive_architecture,
    get_continual_learner,
    get_ethical_framework,
    get_knowledge_graph,
    get_meta_learning_system,
    get_multi_modal_reasoner,
    get_transfer_hub,
)

__all__ = [
    # Multi-Modal Reasoning
    "ModalityType",
    "MultiModalInput",
    "ReasoningStep",
    "MultiModalReasoner",
    "get_multi_modal_reasoner",
    # Continual Learning
    "LearningStrategy",
    "LearningTask",
    "LearningMetrics",
    "ContinualLearner",
    "get_continual_learner",
    # Meta-Learning
    "MetaLearningAlgorithm",
    "FewShotTask",
    "AdaptationResult",
    "MetaLearningSystem",
    "get_meta_learning_system",
    # Knowledge Graph
    "Entity",
    "Relation",
    "Triple",
    "InferenceType",
    "KnowledgeGraphEngine",
    "get_knowledge_graph",
    # Cognitive Architecture
    "MemoryType",
    "MemoryItem",
    "Goal",
    "AttentionState",
    "CognitiveArchitecture",
    "get_cognitive_architecture",
    # Transfer Learning
    "TransferMethod",
    "Domain",
    "TransferTask",
    "TransferResult",
    "TransferLearningHub",
    "get_transfer_hub",
    # Ethical AI
    "EthicalPrinciple",
    "EthicalConstraint",
    "BiasReport",
    "ExplanationResult",
    "EthicalAIFramework",
    "get_ethical_framework",
]
