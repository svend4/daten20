"""
Self-Improving AI & Meta-Optimization Platform v24.0 (ENHANCED)

AI that autonomously improves its own performance through recursive self-improvement,
architecture search, hyperparameter optimization, meta-learning, advanced monitoring,
bottleneck analysis, adaptive learning, and continuous improvement orchestration.

New in v24.0:
- Advanced real-time performance monitoring with anomaly detection
- Intelligent bottleneck analyzer with optimization recommendations
- Adaptive learning rate and momentum controllers
- Continuous improvement orchestrator for autonomous optimization

Example usage:
    from self_improving import get_self_improving_system, get_continuous_improvement_orchestrator

    # Full system optimization
    system = get_self_improving_system()
    results = await system.full_system_optimization(task_data, current_performance=0.7)

    # Continuous improvement
    orchestrator = get_continuous_improvement_orchestrator()
    cycle_results = orchestrator.run_improvement_cycle(performance_metric=0.85)
"""

__version__ = "24.0.0"
__status__ = "ENHANCED"
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

# Advanced Monitoring (v24.0)
from .advanced_monitoring import (
    AdvancedMonitor,
    MetricType,
    AnomalyType,
    MetricSnapshot,
    Anomaly,
    TrendAnalysis,
    get_advanced_monitor,
)

# Bottleneck Analysis (v24.0)
from .bottleneck_analyzer import (
    BottleneckAnalyzer,
    BottleneckType,
    Severity,
    BottleneckProfile,
    ProfilingResult,
    get_bottleneck_analyzer,
)

# Adaptive Learning (v24.0)
from .adaptive_learning import (
    AdaptiveLearningController,
    AdaptiveMomentumController,
    LRScheduleType,
    LRScheduleConfig,
    LRState,
    PlateauState,
    get_adaptive_lr_controller,
    get_adaptive_momentum_controller,
)

# Continuous Improvement (v24.0)
from .continuous_improvement import (
    ContinuousImprovementOrchestrator,
    ImprovementPhase,
    ImprovementStatus,
    ImprovementAction,
    ImprovementResult,
    ContinuousImprovementConfig,
    get_continuous_improvement_orchestrator,
)

__all__ = [
    "__version__",
    "__status__",
    # Core Systems (v23.0)
    "RecursiveSelfImprovement",
    "NeuralArchitectureSearch",
    "HyperparameterOptimization",
    "PerformanceProfiling",
    "CodeGeneration",
    "MetaLearningOptimization",
    "SafetyValidation",
    "IntegratedSelfImprovingSystem",
    # Enums (v23.0)
    "ImprovementStrategy",
    "SearchAlgorithm",
    # Data Classes (v23.0)
    "Improvement",
    "Architecture",
    "HyperparameterConfig",
    "SelfImprovingConfig",
    # Singleton Getters (v23.0)
    "get_self_improvement_engine",
    "get_architecture_search",
    "get_hyperparameter_optimization",
    "get_performance_profiling",
    "get_code_generation",
    "get_meta_learning",
    "get_safety_validation",
    "get_self_improving_system",
    # Advanced Monitoring (v24.0)
    "AdvancedMonitor",
    "MetricType",
    "AnomalyType",
    "MetricSnapshot",
    "Anomaly",
    "TrendAnalysis",
    "get_advanced_monitor",
    # Bottleneck Analysis (v24.0)
    "BottleneckAnalyzer",
    "BottleneckType",
    "Severity",
    "BottleneckProfile",
    "ProfilingResult",
    "get_bottleneck_analyzer",
    # Adaptive Learning (v24.0)
    "AdaptiveLearningController",
    "AdaptiveMomentumController",
    "LRScheduleType",
    "LRScheduleConfig",
    "LRState",
    "PlateauState",
    "get_adaptive_lr_controller",
    "get_adaptive_momentum_controller",
    # Continuous Improvement (v24.0)
    "ContinuousImprovementOrchestrator",
    "ImprovementPhase",
    "ImprovementStatus",
    "ImprovementAction",
    "ImprovementResult",
    "ContinuousImprovementConfig",
    "get_continuous_improvement_orchestrator",
]
