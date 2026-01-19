"""
Emergent Intelligence & Complex Systems Platform v24.0

AI systems demonstrating emergent behaviors through collective intelligence,
self-organization, and synergistic interactions between components.

Example usage:
    from emergent_intelligence import get_emergent_intelligence_system

    # Create emergent collective problem solving
    system = get_emergent_intelligence_system()
    result = await system.emergent_collective_problem_solving(
        problem_description="optimize global supply chain",
        num_swarms=5,
        systems_to_integrate=["logistics", "finance", "forecasting"]
    )
"""

__version__ = "24.0.0"
__author__ = "Document Management System Team"

from .emergent_intelligence_services import (
    # Core Systems
    AdaptiveComplexSystems,
    CollectiveIntelligence,
    EmergentProblemSolving,
    HolisticOptimization,
    IntegratedEmergentIntelligenceSystem,
    MultiSystemIntegration,
    SelfOrganization,
    SynergyDetection,
    # Data Classes
    EmergentIntelligenceConfig,
    # Singleton Getters
    get_adaptive_complex_systems,
    get_collective_intelligence,
    get_emergent_intelligence_system,
    get_emergent_problem_solving,
    get_holistic_optimization,
    get_multi_system_integration,
    get_self_organization,
    get_synergy_detection,
)

__all__ = [
    "__version__",
    # Core Systems
    "MultiSystemIntegration",
    "SelfOrganization",
    "CollectiveIntelligence",
    "AdaptiveComplexSystems",
    "SynergyDetection",
    "HolisticOptimization",
    "EmergentProblemSolving",
    # Integrated System
    "IntegratedEmergentIntelligenceSystem",
    # Data Classes
    "EmergentIntelligenceConfig",
    # Singleton Getters
    "get_multi_system_integration",
    "get_self_organization",
    "get_collective_intelligence",
    "get_adaptive_complex_systems",
    "get_synergy_detection",
    "get_holistic_optimization",
    "get_emergent_problem_solving",
    "get_emergent_intelligence_system",
]
