"""
v26.0: ASI & Beyond-Human Reasoning Platform

Artificial Superintelligence exceeding human cognitive capabilities
by 100-10,000x across all domains with robust safety and alignment.
"""

from .asi_services import (  # Services; Enums; Data Structures; Singleton Getters
    AlignmentState,
    CodeModification,
    CreativeWork,
    DeepUnderstanding,
    DiscoveryField,
    ImprovementCycle,
    ImprovementType,
    NovelCapability,
    NovelCapabilityEmergenceService,
    RecursiveSelfImprovementService,
    ScientificBreakthrough,
    ScientificDiscoveryAccelerationService,
    StrategicDomain,
    SuperhumanCreativityService,
    SuperhumanStrategicPlanningService,
    SuperhumanStrategy,
    UltraDeepUnderstandingService,
    ValueAlignmentService,
    get_novel_capability_service,
    get_scientific_discovery_service,
    get_self_improvement_service,
    get_strategic_planning_service,
    get_superhuman_creativity_service,
    get_ultra_understanding_service,
    get_value_alignment_service,
)

__version__ = "26.0.0"

__all__ = [
    # Services
    "RecursiveSelfImprovementService",
    "SuperhumanStrategicPlanningService",
    "ScientificDiscoveryAccelerationService",
    "NovelCapabilityEmergenceService",
    "UltraDeepUnderstandingService",
    "SuperhumanCreativityService",
    "ValueAlignmentService",
    # Enums
    "ImprovementType",
    "StrategicDomain",
    "DiscoveryField",
    # Data Structures
    "CodeModification",
    "ImprovementCycle",
    "SuperhumanStrategy",
    "ScientificBreakthrough",
    "NovelCapability",
    "DeepUnderstanding",
    "CreativeWork",
    "AlignmentState",
    # Singleton Getters
    "get_self_improvement_service",
    "get_strategic_planning_service",
    "get_scientific_discovery_service",
    "get_novel_capability_service",
    "get_ultra_understanding_service",
    "get_superhuman_creativity_service",
    "get_value_alignment_service",
    # Version
    "__version__",
]
