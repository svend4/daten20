"""
Explainable AI & Interpretability Module (v13.0)

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 20-50% faster, full features, requires numpy

The best available version is automatically selected.

Core Systems:
- SHAP Explainer: SHapley values
- LIME Explainer: Local interpretable explanations  
- Feature Importance: Feature attribution
- Integrated Gradients: Neural network explanations
- Counterfactuals: What-if analysis

Version: 13.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

# ALWAYS import Pure Python version (baseline, always available)
from .explainable_services import (
    # Enums
    ExplanationMethod,
    ModelType,
    
    # Dataclasses
    Explanation,
    ExplainableAIConfig,
    
    # Classes (Pure Python - simplified)
    SHAPExplainer as SHAPExplainerPython,
    LIMEExplainer as LIMEExplainerPython,
    FeatureImportanceAnalyzer as FeatureImportanceAnalyzerPython,
    IntegratedExplainableSystem as IntegratedExplainableSystemPython,
    
    # Singleton
    get_explainable_system as get_explainable_system_python,
)

# TRY to import NumPy version (optional, faster, more features)
try:
    from .explainable_services_numpy import (
        # Additional enums from NumPy version
        AttributionMethod,
        SaliencyType,
        
        # Additional dataclasses from NumPy version
        SHAPValue,
        LIMEExplanation,
        Attribution,
        Counterfactual,
        DecisionRule,
        SaliencyMap,
        ConceptActivationVector,
        TCAVScore,
        AggregatedExplanation,
        
        # Full feature classes (NumPy version)
        ModelInterpreter as ModelInterpreterNumpy,
        FeatureAttributionEngine as FeatureAttributionEngineNumpy,
        CounterfactualGenerator as CounterfactualGeneratorNumpy,
        DecisionTreeExtractor as DecisionTreeExtractorNumpy,
        SaliencyMapGenerator as SaliencyMapGeneratorNumpy,
        ConceptActivationTester as ConceptActivationTesterNumpy,
        ExplanationAggregator as ExplanationAggregatorNumpy,
        
        # Singleton getters (NumPy version)
        get_model_interpreter as get_model_interpreter_numpy,
        get_feature_attribution as get_feature_attribution_numpy,
        get_counterfactual_generator as get_counterfactual_generator_numpy,
        get_decision_tree_extractor as get_decision_tree_extractor_numpy,
        get_saliency_map_generator as get_saliency_map_generator_numpy,
        get_concept_activation_tester as get_concept_activation_tester_numpy,
        get_explanation_aggregator as get_explanation_aggregator_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (20-50% faster, more features)
    ModelInterpreter = ModelInterpreterNumpy
    FeatureAttributionEngine = FeatureAttributionEngineNumpy
    CounterfactualGenerator = CounterfactualGeneratorNumpy
    DecisionTreeExtractor = DecisionTreeExtractorNumpy
    SaliencyMapGenerator = SaliencyMapGeneratorNumpy
    ConceptActivationTester = ConceptActivationTesterNumpy
    ExplanationAggregator = ExplanationAggregatorNumpy
    
    # Use NumPy getters
    get_model_interpreter = get_model_interpreter_numpy
    get_feature_attribution = get_feature_attribution_numpy
    get_counterfactual_generator = get_counterfactual_generator_numpy
    get_decision_tree_extractor = get_decision_tree_extractor_numpy
    get_saliency_map_generator = get_saliency_map_generator_numpy
    get_concept_activation_tester = get_concept_activation_tester_numpy
    get_explanation_aggregator = get_explanation_aggregator_numpy
    
    # Main system (use NumPy integrated system if available)
    IntegratedExplainableSystem = IntegratedExplainableSystemPython  # Pure Python OK
    get_explainable_system = get_explainable_system_python
    
else:
    # NumPy not available - use Pure Python (simplified)
    # Map to simplified Pure Python versions
    ModelInterpreter = IntegratedExplainableSystemPython
    IntegratedExplainableSystem = IntegratedExplainableSystemPython
    get_explainable_system = get_explainable_system_python
    
    # Pure Python doesn't have these advanced features
    FeatureAttributionEngine = None
    CounterfactualGenerator = None
    DecisionTreeExtractor = None
    SaliencyMapGenerator = None
    ConceptActivationTester = None
    ExplanationAggregator = None
    
    # Getters return None for unavailable features
    get_model_interpreter = get_explainable_system_python
    get_feature_attribution = lambda: None
    get_counterfactual_generator = lambda: None
    get_decision_tree_extractor = lambda: None
    get_saliency_map_generator = lambda: None
    get_concept_activation_tester = lambda: None
    get_explanation_aggregator = lambda: None
    
    # Define missing enums/dataclasses as None
    AttributionMethod = None
    SaliencyType = None
    SHAPValue = None
    LIMEExplanation = None
    Attribution = None
    Counterfactual = None
    DecisionRule = None
    SaliencyMap = None
    ConceptActivationVector = None
    TCAVScore = None
    AggregatedExplanation = None

__version__ = "13.0.0"

__all__ = [
    # Enums
    "ExplanationMethod",
    "ModelType",
    
    # Dataclasses
    "Explanation",
    "ExplainableAIConfig",
    
    # Core classes (auto-select best version)
    "IntegratedExplainableSystem",
    "ModelInterpreter",
    
    # Pure Python versions (always available)
    "SHAPExplainerPython",
    "LIMEExplainerPython",
    "FeatureImportanceAnalyzerPython",
    "IntegratedExplainableSystemPython",
    "get_explainable_system_python",
    
    # Singleton getters
    "get_explainable_system",
    "get_model_interpreter",
    
    # Dual-version flag
    "HAS_NUMPY",
]

# Add NumPy-only features to __all__ if available
if HAS_NUMPY:
    __all__.extend([
        "AttributionMethod",
        "SaliencyType",
        "SHAPValue",
        "LIMEExplanation",
        "Attribution",
        "Counterfactual",
        "DecisionRule",
        "SaliencyMap",
        "ConceptActivationVector",
        "TCAVScore",
        "AggregatedExplanation",
        "FeatureAttributionEngine",
        "CounterfactualGenerator",
        "DecisionTreeExtractor",
        "SaliencyMapGenerator",
        "ConceptActivationTester",
        "ExplanationAggregator",
        "get_feature_attribution",
        "get_counterfactual_generator",
        "get_decision_tree_extractor",
        "get_saliency_map_generator",
        "get_concept_activation_tester",
        "get_explanation_aggregator",
    ])
