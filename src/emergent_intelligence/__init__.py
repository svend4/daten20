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
    AdaptiveSystemEvolution,
    CollectiveIntelligence,
    EmergentBehaviorDetection,
    HolisticSystemOptimization,
    IntegratedEmergentIntelligenceSystem,
    SelfOrganization,
    SwarmIntelligence,
    SynergyDetection,
    # Data Classes
    EmergentIntelligenceConfig,
    # Singleton Getters
    get_adaptive_evolution,
    get_collective_intelligence,
    get_emergent_behavior_detection,
    get_emergent_intelligence_system,
    get_holistic_optimization,
    get_self_organization,
    get_swarm_intelligence,
    get_synergy_detection,
)

__all__ = [
    "__version__",
    # Core Systems
    "SwarmIntelligence",
    "CollectiveIntelligence",
    "SelfOrganization",
    "EmergentBehaviorDetection",
    "SynergyDetection",
    "AdaptiveSystemEvolution",
    "HolisticSystemOptimization",
    # Integrated System
    "IntegratedEmergentIntelligenceSystem",
    # Data Classes
    "EmergentIntelligenceConfig",
    # Singleton Getters
    "get_swarm_intelligence",
    "get_collective_intelligence",
    "get_self_organization",
    "get_emergent_behavior_detection",
    "get_synergy_detection",
    "get_adaptive_evolution",
    "get_holistic_optimization",
    "get_emergent_intelligence_system",
]
