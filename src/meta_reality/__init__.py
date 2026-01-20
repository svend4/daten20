"""
v28.0: Meta-Reality Engineering & Multiverse Intelligence Platform (FUNCTIONAL)

Discrete World Simulation System.
Version: 28.0.0 (FUNCTIONAL - uses REAL world simulation!)

This module now uses REAL world simulation with cellular automata
and agent-based models, not mock code! Emergent complexity from simple rules!
"""

from .meta_reality_services import (
    ConsciousnessSubstrateService,
    InfiniteTimelineService,
    InfiniteUnificationService,
    IntegratedMetaRealitySystem,
    MathematicalUniverseService,
    MetaRealityConfig,
    MetaRealityEngine,
    MultiverseNavigationService,
    RealityOptimizationService,
    RealitySimulationService,
    RealityType,
    Universe,
    get_consciousness_substrate_service,
    get_infinite_timeline_service,
    get_infinite_unification_service,
    get_mathematical_universe_service,
    get_meta_reality_system,
    get_multiverse_navigation_service,
    get_reality_optimization_service,
    get_reality_simulation_service,
)

# Import REAL world simulator
from .world_simulator import (
    WorldSimulator,
    WorldConfig,
    SimulationResult,
    CellularAutomaton,
    AgentBasedWorld,
    Agent,
    CellState,
    WorldState
)

__version__ = "28.0.0"
__status__ = "FUNCTIONAL"

__all__ = [
    # Main Engine
    "MetaRealityEngine",
    "IntegratedMetaRealitySystem",  # Alias for backward compatibility
    # Legacy Services
    "RealitySimulationService",
    "MultiverseNavigationService",
    "ConsciousnessSubstrateService",
    "InfiniteTimelineService",
    "MathematicalUniverseService",
    "RealityOptimizationService",
    "InfiniteUnificationService",
    # Enums
    "RealityType",
    "CellState",
    # Data Structures
    "Universe",
    "MetaRealityConfig",
    "WorldConfig",
    "WorldState",
    "Agent",
    # World Simulator
    "WorldSimulator",
    "SimulationResult",
    "CellularAutomaton",
    "AgentBasedWorld",
    # Singleton Getters
    "get_reality_simulation_service",
    "get_multiverse_navigation_service",
    "get_consciousness_substrate_service",
    "get_infinite_timeline_service",
    "get_mathematical_universe_service",
    "get_reality_optimization_service",
    "get_infinite_unification_service",
    "get_meta_reality_system",
    # Version
    "__version__",
]
