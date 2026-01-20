"""
Neuro-Symbolic AI Platform Module (v14.0)

This module provides comprehensive neuro-symbolic AI capabilities combining
neural learning with symbolic reasoning.

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (portable)
- NumPy: 5-15% faster, requires numpy

The best available version is automatically selected.

Core Systems:
- Logic Tensor Network: Differentiable first-order logic
- Neural Module Network: Compositional visual reasoning
- Program Synthesis: Inducing programs from examples
- Semantic Parser: NL to logical forms
- Differentiable Reasoner: Neural-symbolic inference
- Knowledge Graph: KG representations with embeddings

Version: 14.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

# ALWAYS import Pure Python version (baseline, always available)
from .neurosymbolic_services import (
    # Enumerations
    LogicOperator,
    ModuleType,
    SynthesisAlgorithm,
    ReasoningMode,
    EmbeddingModel,
    TNorm,

    # Dataclasses
    Predicate,
    LogicRule,
    Module,
    Program,
    LogicalForm,
    Triple,
    NeurosymbolicConfig,

    # Subsystems (Pure Python versions)
    KnowledgeGraph as KnowledgeGraphPython,
    LogicTensorNetwork as LogicTensorNetworkPython,
    NeuralModuleNetwork as NeuralModuleNetworkPython,
    ProgramSynthesizer as ProgramSynthesizerPython,
    SemanticParser as SemanticParserPython,
    DifferentiableReasoner as DifferentiableReasonerPython,

    # Integrated System (Pure Python)
    IntegratedNeurosymbolicSystem as IntegratedNeurosymbolicSystemPython,

    # Singleton Getter (Pure Python)
    get_neurosymbolic_system as get_neurosymbolic_system_python,
)

# TRY to import NumPy version (optional, faster)
try:
    from .neurosymbolic_services_numpy import (
        # Subsystems (NumPy versions - more classes in NumPy version)
        KnowledgeGraphEmbedder as KnowledgeGraphEmbedderNumpy,
        LogicTensorNetwork as LogicTensorNetworkNumpy,
        NeuralModuleNetwork as NeuralModuleNetworkNumpy,
        ProgramSynthesisEngine as ProgramSynthesisEngineNumpy,
        SemanticParser as SemanticParserNumpy,
        DifferentiableReasoner as DifferentiableReasonerNumpy,
        HybridLearningSystem as HybridLearningSystemNumpy,

        # Integrated System (NumPy)
        IntegratedNeurosymbolicSystem as IntegratedNeurosymbolicSystemNumpy,

        # Singleton Getters (NumPy)
        get_logic_tensor_network as get_logic_tensor_network_numpy,
        get_neural_module_network as get_neural_module_network_numpy,
        get_program_synthesis_engine as get_program_synthesis_engine_numpy,
        get_semantic_parser as get_semantic_parser_numpy,
        get_differentiable_reasoner as get_differentiable_reasoner_numpy,
        get_knowledge_graph_embedder as get_knowledge_graph_embedder_numpy,
        get_hybrid_learning_system as get_hybrid_learning_system_numpy,
        get_neurosymbolic_system as get_neurosymbolic_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (5-15% faster, more features)
    KnowledgeGraph = KnowledgeGraphEmbedderNumpy  # NumPy version has embedder
    LogicTensorNetwork = LogicTensorNetworkNumpy
    NeuralModuleNetwork = NeuralModuleNetworkNumpy
    ProgramSynthesizer = ProgramSynthesisEngineNumpy  # Different name in NumPy
    SemanticParser = SemanticParserNumpy
    DifferentiableReasoner = DifferentiableReasonerNumpy
    IntegratedNeurosymbolicSystem = IntegratedNeurosymbolicSystemNumpy
    get_neurosymbolic_system = get_neurosymbolic_system_numpy

    # Additional NumPy-only classes
    KnowledgeGraphEmbedder = KnowledgeGraphEmbedderNumpy
    HybridLearningSystem = HybridLearningSystemNumpy
    ProgramSynthesisEngine = ProgramSynthesisEngineNumpy

    # Additional NumPy-only getters
    get_logic_tensor_network = get_logic_tensor_network_numpy
    get_neural_module_network = get_neural_module_network_numpy
    get_program_synthesis_engine = get_program_synthesis_engine_numpy
    get_semantic_parser = get_semantic_parser_numpy
    get_differentiable_reasoner = get_differentiable_reasoner_numpy
    get_knowledge_graph_embedder = get_knowledge_graph_embedder_numpy
    get_hybrid_learning_system = get_hybrid_learning_system_numpy
else:
    # NumPy not available - use Pure Python (portable but simpler)
    KnowledgeGraph = KnowledgeGraphPython
    LogicTensorNetwork = LogicTensorNetworkPython
    NeuralModuleNetwork = NeuralModuleNetworkPython
    ProgramSynthesizer = ProgramSynthesizerPython
    SemanticParser = SemanticParserPython
    DifferentiableReasoner = DifferentiableReasonerPython
    IntegratedNeurosymbolicSystem = IntegratedNeurosymbolicSystemPython
    get_neurosymbolic_system = get_neurosymbolic_system_python

    # Pure Python doesn't have these separate getters - use main getter
    get_logic_tensor_network = lambda: None  # Not available in Pure Python
    get_neural_module_network = lambda: None
    get_program_synthesis_engine = lambda: None
    get_semantic_parser = lambda: None
    get_differentiable_reasoner = lambda: None
    get_knowledge_graph_embedder = lambda: None
    get_hybrid_learning_system = lambda: None

    # Aliases for compatibility
    KnowledgeGraphEmbedder = KnowledgeGraphPython  # Pure Python uses KnowledgeGraph
    HybridLearningSystem = None  # Not available in Pure Python
    ProgramSynthesisEngine = ProgramSynthesizerPython  # Same class, different name

__version__ = "14.0.0"

__all__ = [
    # Enumerations
    "LogicOperator",
    "ModuleType",
    "SynthesisAlgorithm",
    "ReasoningMode",
    "EmbeddingModel",
    "TNorm",

    # Dataclasses
    "Predicate",
    "LogicRule",
    "Module",
    "Program",
    "LogicalForm",
    "Triple",
    "NeurosymbolicConfig",

    # Subsystems (auto-select best version)
    "KnowledgeGraph",
    "LogicTensorNetwork",
    "NeuralModuleNetwork",
    "ProgramSynthesizer",
    "SemanticParser",
    "DifferentiableReasoner",
    "KnowledgeGraphEmbedder",  # NumPy-only (alias to KnowledgeGraph in Pure Python)
    "HybridLearningSystem",  # NumPy-only (None in Pure Python)
    "ProgramSynthesisEngine",  # Alias for ProgramSynthesizer

    # Pure Python versions (always available)
    "KnowledgeGraphPython",
    "LogicTensorNetworkPython",
    "NeuralModuleNetworkPython",
    "ProgramSynthesizerPython",
    "SemanticParserPython",
    "DifferentiableReasonerPython",
    "IntegratedNeurosymbolicSystemPython",
    "get_neurosymbolic_system_python",

    # Integrated System
    "IntegratedNeurosymbolicSystem",

    # Singleton Getters
    "get_logic_tensor_network",
    "get_neural_module_network",
    "get_program_synthesis_engine",
    "get_semantic_parser",
    "get_differentiable_reasoner",
    "get_knowledge_graph_embedder",
    "get_hybrid_learning_system",
    "get_neurosymbolic_system",

    # Dual-version flag
    "HAS_NUMPY",
]

# Add NumPy versions to __all__ if available
if HAS_NUMPY:
    __all__.extend([
        "KnowledgeGraphEmbedderNumpy",
        "LogicTensorNetworkNumpy",
        "NeuralModuleNetworkNumpy",
        "ProgramSynthesisEngineNumpy",
        "SemanticParserNumpy",
        "DifferentiableReasonerNumpy",
        "HybridLearningSystemNumpy",
        "IntegratedNeurosymbolicSystemNumpy",
        "get_neurosymbolic_system_numpy",
        "get_logic_tensor_network_numpy",
        "get_neural_module_network_numpy",
        "get_program_synthesis_engine_numpy",
        "get_semantic_parser_numpy",
        "get_differentiable_reasoner_numpy",
        "get_knowledge_graph_embedder_numpy",
        "get_hybrid_learning_system_numpy",
    ])
