"""
v27.0: Cosmic Intelligence & Universal-Scale Platform

Intelligence operating at planetary to universal scales.
"""

from .cosmic_services import (
    CivilizationScale,
    CosmicIntelligenceConfig,
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

__version__ = "27.0.0"

__all__ = [
    # Services
    "PlanetaryIntelligenceService",
    "StellarEngineeringService",
    "GalacticCivilizationService",
    "UniversalComputationService",
    "PhysicsManipulationService",
    "TranscendentReasoningService",
    "OmegaPointService",
    # Integrated System
    "IntegratedCosmicSystem",
    # Enums
    "CivilizationScale",
    # Data Structures
    "PlanetaryState",
    "DysonStructure",
    "CosmicIntelligenceConfig",
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
