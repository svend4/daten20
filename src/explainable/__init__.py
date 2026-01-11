"""
Explainable AI & Interpretability Module (v13.0)

This module provides comprehensive explainability and interpretability tools
for understanding and interpreting complex machine learning models.

Core Systems:
- Model Interpreter: SHAP, LIME, permutation importance, partial dependence
- Feature Attribution: Integrated Gradients, GradCAM, attention analysis
- Counterfactual Generator: Optimization, genetic algorithms, DiCE
- Decision Tree Extractor: Surrogate trees, rules, anchors
- Saliency Map Generator: Visual explanations for images
- Concept Activation Tester: TCAV, concept discovery
- Explanation Aggregator: Multi-method ensemble, validation

Example Usage:
    from explainable import get_model_interpreter, get_explanation_aggregator

    # Register model
    interpreter = get_model_interpreter()
    await interpreter.register_model(
        model_id="my_model",
        model=trained_model,
        model_type=ModelType.NEURAL_NETWORK
    )

    # Get SHAP explanation
    shap_values = await interpreter.explain_shap(
        model_id="my_model",
        instance=input_data
    )

    # Aggregate multiple explanations
    aggregator = get_explanation_aggregator()
    consensus = await aggregator.aggregate_explanations(
        [shap_exp, lime_exp, perm_imp]
    )
"""

from .explainable_services import (
    # Enums
    ExplanationMethod,
    ModelType,
    AttributionMethod,
    SaliencyType,

    # Data Classes
    Explanation,
    SHAPValue,
    LIMEExplanation,
    Attribution,
    Counterfactual,
    DecisionRule,
    SaliencyMap,
    ConceptActivationVector,
    TCAVScore,
    AggregatedExplanation,

    # Service Classes
    ModelInterpreter,
    FeatureAttributionEngine,
    CounterfactualGenerator,
    DecisionTreeExtractor,
    SaliencyMapGenerator,
    ConceptActivationTester,
    ExplanationAggregator,

    # Singleton Getters
    get_model_interpreter,
    get_feature_attribution,
    get_counterfactual_generator,
    get_decision_tree_extractor,
    get_saliency_map_generator,
    get_concept_activation_tester,
    get_explanation_aggregator,
)

__version__ = '13.0.0'
__all__ = [
    # Enums
    'ExplanationMethod',
    'ModelType',
    'AttributionMethod',
    'SaliencyType',

    # Data Classes
    'Explanation',
    'SHAPValue',
    'LIMEExplanation',
    'Attribution',
    'Counterfactual',
    'DecisionRule',
    'SaliencyMap',
    'ConceptActivationVector',
    'TCAVScore',
    'AggregatedExplanation',

    # Service Classes
    'ModelInterpreter',
    'FeatureAttributionEngine',
    'CounterfactualGenerator',
    'DecisionTreeExtractor',
    'SaliencyMapGenerator',
    'ConceptActivationTester',
    'ExplanationAggregator',

    # Singleton Getters
    'get_model_interpreter',
    'get_feature_attribution',
    'get_counterfactual_generator',
    'get_decision_tree_extractor',
    'get_saliency_map_generator',
    'get_concept_activation_tester',
    'get_explanation_aggregator',
]
