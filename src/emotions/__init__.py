"""
❤️ Emotional Consciousness Platform v7.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 10-50x faster, full features, requires numpy

Computational models of emotions, empathy, affective computing,
and emotional intelligence.

Version: 7.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "7.0.0"

# ALWAYS import Pure Python version
from .emotions_services import (
    # Enums
    EmotionType,
    EmotionRegulationStrategy,
    EmpathyType,
    EmotionalTone,
    
    # Dataclasses
    Emotion,
    EmotionalState,
    
    # Classes (Pure Python - simplified)
    EmotionalAwarenessEngine as EmotionalAwarenessEnginePython,
    AffectiveComputingSystem as AffectiveComputingSystemPython,
    EmpathySimulator as EmpathySimulatorPython,
    EmotionalIntelligenceSystem as EmotionalIntelligenceSystemPython,
    EmotionalMemorySystem as EmotionalMemorySystemPython,
    EmotionalDecisionMaking as EmotionalDecisionMakingPython,
    EmotionalExpressionGenerator as EmotionalExpressionGeneratorPython,
    
    # Singletons (Pure Python)
    get_emotional_awareness_engine as get_emotional_awareness_engine_python,
    get_affective_system as get_affective_system_python,
    get_empathy_simulator as get_empathy_simulator_python,
    get_emotional_intelligence_system as get_emotional_intelligence_system_python,
    get_emotional_memory_system as get_emotional_memory_system_python,
    get_emotional_decision_system as get_emotional_decision_system_python,
    get_expression_generator as get_expression_generator_python,
)

# TRY to import NumPy version
try:
    from .emotions_services_numpy import (
        # Classes (NumPy version - full features)
        EmotionalAwarenessEngine as EmotionalAwarenessEngineNumpy,
        AffectiveComputingSystem as AffectiveComputingSystemNumpy,
        EmpathySimulator as EmpathySimulatorNumpy,
        EmotionalIntelligenceSystem as EmotionalIntelligenceSystemNumpy,
        EmotionalMemorySystem as EmotionalMemorySystemNumpy,
        EmotionalDecisionMaking as EmotionalDecisionMakingNumpy,
        EmotionalExpressionGenerator as EmotionalExpressionGeneratorNumpy,
        
        # Singletons (NumPy version)
        get_emotional_awareness_engine as get_emotional_awareness_engine_numpy,
        get_affective_system as get_affective_system_numpy,
        get_empathy_simulator as get_empathy_simulator_numpy,
        get_emotional_intelligence_system as get_emotional_intelligence_system_numpy,
        get_emotional_memory_system as get_emotional_memory_system_numpy,
        get_emotional_decision_system as get_emotional_decision_system_numpy,
        get_expression_generator as get_expression_generator_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases
if HAS_NUMPY:
    EmotionalAwarenessEngine = EmotionalAwarenessEngineNumpy
    AffectiveComputingSystem = AffectiveComputingSystemNumpy
    EmpathySimulator = EmpathySimulatorNumpy
    EmotionalIntelligenceSystem = EmotionalIntelligenceSystemNumpy
    EmotionalMemorySystem = EmotionalMemorySystemNumpy
    EmotionalDecisionMaking = EmotionalDecisionMakingNumpy
    EmotionalExpressionGenerator = EmotionalExpressionGeneratorNumpy
    
    get_emotional_awareness_engine = get_emotional_awareness_engine_numpy
    get_affective_system = get_affective_system_numpy
    get_empathy_simulator = get_empathy_simulator_numpy
    get_emotional_intelligence_system = get_emotional_intelligence_system_numpy
    get_emotional_memory_system = get_emotional_memory_system_numpy
    get_emotional_decision_system = get_emotional_decision_system_numpy
    get_expression_generator = get_expression_generator_numpy
else:
    EmotionalAwarenessEngine = EmotionalAwarenessEnginePython
    AffectiveComputingSystem = AffectiveComputingSystemPython
    EmpathySimulator = EmpathySimulatorPython
    EmotionalIntelligenceSystem = EmotionalIntelligenceSystemPython
    EmotionalMemorySystem = EmotionalMemorySystemPython
    EmotionalDecisionMaking = EmotionalDecisionMakingPython
    EmotionalExpressionGenerator = EmotionalExpressionGeneratorPython
    
    get_emotional_awareness_engine = get_emotional_awareness_engine_python
    get_affective_system = get_affective_system_python
    get_empathy_simulator = get_empathy_simulator_python
    get_emotional_intelligence_system = get_emotional_intelligence_system_python
    get_emotional_memory_system = get_emotional_memory_system_python
    get_emotional_decision_system = get_emotional_decision_system_python
    get_expression_generator = get_expression_generator_python

__all__ = [
    "__version__",
    "EmotionType",
    "EmotionRegulationStrategy",
    "EmpathyType",
    "EmotionalTone",
    "Emotion",
    "EmotionalState",
    "EmotionalAwarenessEngine",
    "AffectiveComputingSystem",
    "EmpathySimulator",
    "EmotionalIntelligenceSystem",
    "EmotionalMemorySystem",
    "EmotionalDecisionMaking",
    "EmotionalExpressionGenerator",
    "get_emotional_awareness_engine",
    "get_affective_system",
    "get_empathy_simulator",
    "get_emotional_intelligence_system",
    "get_emotional_memory_system",
    "get_emotional_decision_system",
    "get_expression_generator",
    "HAS_NUMPY",
]
