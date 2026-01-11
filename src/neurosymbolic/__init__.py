"""
Neuro-Symbolic AI Platform Module (v14.0)

This module provides comprehensive neuro-symbolic AI capabilities combining
neural learning with symbolic reasoning.

Core Systems:
- Logic Tensor Network: Differentiable first-order logic
- Neural Module Network: Compositional visual reasoning
- Program Synthesis Engine: Inducing programs from examples
- Semantic Parser: NL to logical forms
- Differentiable Reasoner: Neural-symbolic inference
- Knowledge Graph Embedder: KG representations
- Hybrid Learning System: Joint neural-symbolic optimization

Example Usage:
    from neurosymbolic import get_logic_tensor_network
    
    ltn = get_logic_tensor_network()
    # Train with logical constraints
    await ltn.add_predicate("is_red", neural_network)
    await ltn.add_rule("forall x: is_red(x) -> is_colored(x)")
"""

from .neurosymbolic_services import (
    # Enums
    LogicOperator,
    ModuleType,
    SynthesisAlgorithm,
    ReasoningMode,
    
    # Data Classes
    Predicate,
    LogicRule,
    Module,
    Program,
    LogicalForm,
    Triple,
    
    # Service Classes
    LogicTensorNetwork,
    NeuralModuleNetwork,
    ProgramSynthesisEngine,
    SemanticParser,
    DifferentiableReasoner,
    KnowledgeGraphEmbedder,
    HybridLearningSystem,
    
    # Singleton Getters
    get_logic_tensor_network,
    get_neural_module_network,
    get_program_synthesis_engine,
    get_semantic_parser,
    get_differentiable_reasoner,
    get_knowledge_graph_embedder,
    get_hybrid_learning_system,
)

__version__ = '14.0.0'
__all__ = [
    'LogicOperator',
    'ModuleType',
    'SynthesisAlgorithm',
    'ReasoningMode',
    'Predicate',
    'LogicRule',
    'Module',
    'Program',
    'LogicalForm',
    'Triple',
    'LogicTensorNetwork',
    'NeuralModuleNetwork',
    'ProgramSynthesisEngine',
    'SemanticParser',
    'DifferentiableReasoner',
    'KnowledgeGraphEmbedder',
    'HybridLearningSystem',
    'get_logic_tensor_network',
    'get_neural_module_network',
    'get_program_synthesis_engine',
    'get_semantic_parser',
    'get_differentiable_reasoner',
    'get_knowledge_graph_embedder',
    'get_hybrid_learning_system',
]
