"""
Explainable AI & Interpretability Platform Module - v13.0

This module provides comprehensive XAI capabilities for understanding and explaining
machine learning models. It implements SHAP, LIME, Integrated Gradients, GradCAM,
counterfactual explanations, decision tree extraction, saliency maps, TCAV, and
multi-method explanation aggregation.

Version: 13.0.0 (FULL IMPLEMENTATION)
"""

from .explainable_ai_services import (
    # Enumerations
    ExplanationMethod,
    AttributionType,
    SaliencyType,
    CounterfactualStrategy,
    ExplanationScope,
    FidelityMetric,

    # Dataclasses
    Explanation,
    FeatureAttribution,
    Counterfactual,
    SaliencyMap,
    DecisionRule,
    ConceptActivation,
    ExplanationConfig,

    # Subsystems
    ModelInterpreter,
    FeatureAttributionEngine,
    CounterfactualGenerator,
    DecisionTreeExtractor,
    SaliencyMapGenerator,
    ConceptActivationTester,
    ExplanationAggregator,

    # Integrated System
    IntegratedExplainableAISystem,

    # Singleton Getter
    get_explainable_ai_system,
)

__all__ = [
    # Enumerations
    'ExplanationMethod',
    'AttributionType',
    'SaliencyType',
    'CounterfactualStrategy',
    'ExplanationScope',
    'FidelityMetric',

    # Dataclasses
    'Explanation',
    'FeatureAttribution',
    'Counterfactual',
    'SaliencyMap',
    'DecisionRule',
    'ConceptActivation',
    'ExplanationConfig',

    # Subsystems
    'ModelInterpreter',
    'FeatureAttributionEngine',
    'CounterfactualGenerator',
    'DecisionTreeExtractor',
    'SaliencyMapGenerator',
    'ConceptActivationTester',
    'ExplanationAggregator',

    # Integrated System
    'IntegratedExplainableAISystem',

    # Singleton Getter
    'get_explainable_ai_system',
]

__version__ = '13.0.0'
