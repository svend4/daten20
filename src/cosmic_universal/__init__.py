"""
v27.0: Cosmic Intelligence & Universal-Scale Platform (FUNCTIONAL)

Multi-Scale Hierarchical Coordination System.
Version: 27.0.0 (FUNCTIONAL - uses REAL multi-level optimization!)

This module now uses REAL multi-scale coordination algorithms,
not mock code! Hierarchical optimization creates emergent behavior!
"""

from .cosmic_services import (
    CivilizationScale,
    CosmicIntelligenceConfig,
    CosmicUniversalEngine,
    DysonStructure,
    GalacticCivilizationService,
    IntegratedCosmicSystem,
    OmegaPointService,
    PhysicsManipulationService,
    PlanetaryIntelligenceService,
    PlanetaryState,
    StellarEngineeringService,
    TranscendentReasoningService,
    UniversalComputationService,
    get_cosmic_system,
    get_galactic_service,
    get_omega_point_service,
    get_physics_manipulation_service,
    get_planetary_service,
    get_stellar_service,
    get_transcendent_reasoning_service,
    get_universal_computation_service,
)

# Import REAL multi-scale coordinator
from .multi_scale_coordinator import (
    UniversalCoordinator,
    MultiScaleConfig,
    CoordinationResult,
    CoordinationLevel,
    LocalOptimizer,
    RegionalCoordinator,
    GlobalOptimizer,
    Agent,
    Region
)

__version__ = "27.0.0"
__status__ = "FUNCTIONAL"

__all__ = [
    # Main Engine
    "CosmicUniversalEngine",
    "IntegratedCosmicSystem",  # Alias for backward compatibility
    # Legacy Services
    "PlanetaryIntelligenceService",
    "StellarEngineeringService",
    "GalacticCivilizationService",
    "UniversalComputationService",
    "PhysicsManipulationService",
    "TranscendentReasoningService",
    "OmegaPointService",
    # Enums
    "CivilizationScale",
    "CoordinationLevel",
    # Data Structures
    "PlanetaryState",
    "DysonStructure",
    "CosmicIntelligenceConfig",
    # Multi-Scale Coordinator
    "UniversalCoordinator",
    "MultiScaleConfig",
    "CoordinationResult",
    "LocalOptimizer",
    "RegionalCoordinator",
    "GlobalOptimizer",
    "Agent",
    "Region",
    # Singleton Getters
    "get_planetary_service",
    "get_stellar_service",
    "get_galactic_service",
    "get_universal_computation_service",
    "get_physics_manipulation_service",
    "get_transcendent_reasoning_service",
    "get_omega_point_service",
    "get_cosmic_system",
    # Version
    "__version__",
]
