"""
Self-Improving AI & Meta-Optimization Platform v23.0

AI that autonomously improves its own performance through recursive self-improvement,
architecture search, hyperparameter optimization, and meta-learning.

Example usage:
    from self_improving import get_self_improving_system

    # Full system optimization
    system = get_self_improving_system()
    results = await system.full_system_optimization(task_data, current_performance=0.7)
"""

__version__ = "23.0.0"
__author__ = "Document Management System Team"

from .self_improving_services import (  # Core Systems; Enums; Data Classes; Singleton Getters
    Architecture,
    CodeGeneration,
    HyperparameterConfig,
    HyperparameterOptimization,
    Improvement,
    ImprovementStrategy,
    IntegratedSelfImprovingSystem,
    MetaLearningOptimization,
    NeuralArchitectureSearch,
    PerformanceProfiling,
    RecursiveSelfImprovement,
    SafetyValidation,
    SearchAlgorithm,
    SelfImprovingConfig,
    get_architecture_search,
    get_code_generation,
    get_hyperparameter_optimization,
    get_meta_learning,
    get_performance_profiling,
    get_safety_validation,
    get_self_improvement_engine,
    get_self_improving_system,
)

__all__ = [
    "__version__",
    # Core Systems
    "RecursiveSelfImprovement",
    "NeuralArchitectureSearch",
    "HyperparameterOptimization",
    "PerformanceProfiling",
    "CodeGeneration",
    "MetaLearningOptimization",
    "SafetyValidation",
    # Integrated System
    "IntegratedSelfImprovingSystem",
    # Enums
    "ImprovementStrategy",
    "SearchAlgorithm",
    # Data Classes
    "Improvement",
    "Architecture",
    "HyperparameterConfig",
    "SelfImprovingConfig",
    # Singleton Getters
    "get_self_improvement_engine",
    "get_architecture_search",
    "get_hyperparameter_optimization",
    "get_performance_profiling",
    "get_code_generation",
    "get_meta_learning",
    "get_safety_validation",
    "get_self_improving_system",
]
