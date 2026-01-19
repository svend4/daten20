"""
Advanced Integration & Optimization Module

This module provides comprehensive integration and optimization capabilities
across all platform modules. It implements universal integration, meta-learning,
emergent synergy detection, holistic performance monitoring, adaptive resource
management, unified knowledge graphs, and continuous self-improvement.

Version: 9.0.0
"""

from .optimization_services import (  # Enums; Data Classes; Services; Singleton Getters
    AdaptiveResourceManager,
    EmergentSynergyEngine,
    HolisticPerformanceMonitor,
    IntegrationPipeline,
    IntegrationType,
    KnowledgeNode,
    MetaLearningOptimizer,
    ModuleCapability,
    OptimizationResult,
    OptimizationStrategy,
    PerformanceMetric,
    PerformanceSnapshot,
    ResourceAllocation,
    ResourceType,
    SelfImprovementAction,
    SelfImprovementEngine,
    SynergyDetection,
    SynergyType,
    UnifiedKnowledgeGraph,
    UniversalIntegrationHub,
    get_improvement_engine,
    get_integration_hub,
    get_knowledge_graph,
    get_meta_optimizer,
    get_performance_monitor,
    get_resource_manager,
    get_synergy_engine,
)

__all__ = [
    # Enums
    "IntegrationType",
    "OptimizationStrategy",
    "SynergyType",
    "ResourceType",
    "PerformanceMetric",
    # Data Classes
    "ModuleCapability",
    "IntegrationPipeline",
    "OptimizationResult",
    "SynergyDetection",
    "PerformanceSnapshot",
    "ResourceAllocation",
    "KnowledgeNode",
    "SelfImprovementAction",
    # Services
    "UniversalIntegrationHub",
    "MetaLearningOptimizer",
    "EmergentSynergyEngine",
    "HolisticPerformanceMonitor",
    "AdaptiveResourceManager",
    "UnifiedKnowledgeGraph",
    "SelfImprovementEngine",
    # Singleton Getters
    "get_integration_hub",
    "get_meta_optimizer",
    "get_synergy_engine",
    "get_performance_monitor",
    "get_resource_manager",
    "get_knowledge_graph",
    "get_improvement_engine",
]

__version__ = "9.0.0"
