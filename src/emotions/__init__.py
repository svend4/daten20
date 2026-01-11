"""
❤️ Emotional Consciousness Platform

Provides computational models of emotions, empathy, affective computing,
and emotional intelligence based on affective neuroscience and psychology.

IMPORTANT: This module simulates emotional processing computationally.
It does NOT experience genuine emotions, feelings, or subjective affective
experiences. These are functional models for improved human-AI interaction.

Version: 7.0.0
"""

__version__ = '7.0.0'

from .emotions_services import (
    # Emotional Awareness Engine
    EmotionType,
    Emotion,
    EmotionalState,
    AppraisalResult,
    EmotionalAwarenessEngine,
    get_emotional_awareness_engine,

    # Affective Computing System
    EmotionRegulationStrategy,
    Mood,
    AffectiveResponse,
    AffectiveComputingSystem,
    get_affective_system,

    # Empathy Simulator
    EmpathyType,
    PerspectiveTaking,
    EmpatheticResponse,
    EmpathySimulator,
    get_empathy_simulator,

    # Emotional Intelligence System
    EmotionalSkill,
    EQAssessment,
    SkillApplication,
    EmotionalIntelligenceSystem,
    get_eq_system,

    # Emotional Memory System
    EmotionalMemory,
    MemoryQuery,
    EmotionalMemorySystem,
    get_emotional_memory,

    # Emotional Decision Making
    DecisionOption,
    EmotionalValuation,
    EmotionalDecision,
    EmotionalDecisionMaking,
    get_emotional_decision_system,

    # Emotional Expression Generator
    EmotionalTone,
    CulturalContext,
    FacialExpression,
    EmotionalExpressionGenerator,
    get_expression_generator,
)

__all__ = [
    # Emotional Awareness Engine
    'EmotionType',
    'Emotion',
    'EmotionalState',
    'AppraisalResult',
    'EmotionalAwarenessEngine',
    'get_emotional_awareness_engine',

    # Affective Computing System
    'EmotionRegulationStrategy',
    'Mood',
    'AffectiveResponse',
    'AffectiveComputingSystem',
    'get_affective_system',

    # Empathy Simulator
    'EmpathyType',
    'PerspectiveTaking',
    'EmpatheticResponse',
    'EmpathySimulator',
    'get_empathy_simulator',

    # Emotional Intelligence System
    'EmotionalSkill',
    'EQAssessment',
    'SkillApplication',
    'EmotionalIntelligenceSystem',
    'get_eq_system',

    # Emotional Memory System
    'EmotionalMemory',
    'MemoryQuery',
    'EmotionalMemorySystem',
    'get_emotional_memory',

    # Emotional Decision Making
    'DecisionOption',
    'EmotionalValuation',
    'EmotionalDecision',
    'EmotionalDecisionMaking',
    'get_emotional_decision_system',

    # Emotional Expression Generator
    'EmotionalTone',
    'CulturalContext',
    'FacialExpression',
    'EmotionalExpressionGenerator',
    'get_expression_generator',
]
