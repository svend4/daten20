"""
🌐 Social & Collective Intelligence Platform v8.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 10-50x faster, full features, requires numpy

Computational models of social cognition, group dynamics, collective
decision-making, swarm intelligence, and cultural adaptation.

Version: 8.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "8.0.0"

# ALWAYS import Pure Python version (baseline, always available)
from .social_services import (
    # Enums
    SocialRole,
    GroupStage,
    VotingMethod,
    SwarmAlgorithm,
    
    # Dataclasses
    SocialContext,
    BeliefChain,
    VotingResult,
    CulturalProfile,
    
    # Classes (Pure Python - simplified)
    SocialCognitionEngine as SocialCognitionEnginePython,
    GroupDynamicsSystem as GroupDynamicsSystemPython,
    CollectiveDecisionMaking as CollectiveDecisionMakingPython,
    SwarmIntelligenceSystem as SwarmIntelligenceSystemPython,
    CulturalIntelligenceSystem as CulturalIntelligenceSystemPython,
    SocialNetworkAnalysis as SocialNetworkAnalysisPython,
    CollaborativeIntelligenceOrchestrator as CollaborativeIntelligenceOrchestratorPython,
    
    # Singletons (Pure Python)
    get_social_cognition_engine as get_social_cognition_engine_python,
    get_group_dynamics_system as get_group_dynamics_system_python,
    get_collective_decision_system as get_collective_decision_system_python,
    get_swarm_intelligence_system as get_swarm_intelligence_system_python,
    get_cultural_intelligence_system as get_cultural_intelligence_system_python,
    get_social_network_analysis as get_social_network_analysis_python,
    get_collaboration_orchestrator as get_collaboration_orchestrator_python,
)

# TRY to import NumPy version (optional, faster, full features)
try:
    from .social_services_numpy import (
        # Classes (NumPy version - full features)
        SocialCognitionEngine as SocialCognitionEngineNumpy,
        GroupDynamicsSystem as GroupDynamicsSystemNumpy,
        CollectiveDecisionMaking as CollectiveDecisionMakingNumpy,
        SwarmIntelligenceSystem as SwarmIntelligenceSystemNumpy,
        CulturalIntelligenceSystem as CulturalIntelligenceSystemNumpy,
        SocialNetworkAnalysis as SocialNetworkAnalysisNumpy,
        CollaborativeIntelligenceOrchestrator as CollaborativeIntelligenceOrchestratorNumpy,
        
        # Singletons (NumPy version)
        get_social_cognition_engine as get_social_cognition_engine_numpy,
        get_group_dynamics_system as get_group_dynamics_system_numpy,
        get_collective_decision_system as get_collective_decision_system_numpy,
        get_swarm_intelligence_system as get_swarm_intelligence_system_numpy,
        get_cultural_intelligence_system as get_cultural_intelligence_system_numpy,
        get_social_network_analysis as get_social_network_analysis_numpy,
        get_collaboration_orchestrator as get_collaboration_orchestrator_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (10-50x faster, full features)
    SocialCognitionEngine = SocialCognitionEngineNumpy
    GroupDynamicsSystem = GroupDynamicsSystemNumpy
    CollectiveDecisionMaking = CollectiveDecisionMakingNumpy
    SwarmIntelligenceSystem = SwarmIntelligenceSystemNumpy
    CulturalIntelligenceSystem = CulturalIntelligenceSystemNumpy
    SocialNetworkAnalysis = SocialNetworkAnalysisNumpy
    CollaborativeIntelligenceOrchestrator = CollaborativeIntelligenceOrchestratorNumpy
    
    # Use NumPy getters
    get_social_cognition_engine = get_social_cognition_engine_numpy
    get_group_dynamics_system = get_group_dynamics_system_numpy
    get_collective_decision_system = get_collective_decision_system_numpy
    get_swarm_intelligence_system = get_swarm_intelligence_system_numpy
    get_cultural_intelligence_system = get_cultural_intelligence_system_numpy
    get_social_network_analysis = get_social_network_analysis_numpy
    get_collaboration_orchestrator = get_collaboration_orchestrator_numpy
else:
    # NumPy not available - use Pure Python (simplified)
    SocialCognitionEngine = SocialCognitionEnginePython
    GroupDynamicsSystem = GroupDynamicsSystemPython
    CollectiveDecisionMaking = CollectiveDecisionMakingPython
    SwarmIntelligenceSystem = SwarmIntelligenceSystemPython
    CulturalIntelligenceSystem = CulturalIntelligenceSystemPython
    SocialNetworkAnalysis = SocialNetworkAnalysisPython
    CollaborativeIntelligenceOrchestrator = CollaborativeIntelligenceOrchestratorPython
    
    # Use Pure Python getters
    get_social_cognition_engine = get_social_cognition_engine_python
    get_group_dynamics_system = get_group_dynamics_system_python
    get_collective_decision_system = get_collective_decision_system_python
    get_swarm_intelligence_system = get_swarm_intelligence_system_python
    get_cultural_intelligence_system = get_cultural_intelligence_system_python
    get_social_network_analysis = get_social_network_analysis_python
    get_collaboration_orchestrator = get_collaboration_orchestrator_python

__all__ = [
    # Version
    "__version__",
    
    # Enums
    "SocialRole",
    "GroupStage",
    "VotingMethod",
    "SwarmAlgorithm",
    
    # Dataclasses
    "SocialContext",
    "BeliefChain",
    "VotingResult",
    "CulturalProfile",
    
    # Core Systems (auto-select best version)
    "SocialCognitionEngine",
    "GroupDynamicsSystem",
    "CollectiveDecisionMaking",
    "SwarmIntelligenceSystem",
    "CulturalIntelligenceSystem",
    "SocialNetworkAnalysis",
    "CollaborativeIntelligenceOrchestrator",
    
    # Pure Python versions (always available)
    "SocialCognitionEnginePython",
    "GroupDynamicsSystemPython",
    "CollectiveDecisionMakingPython",
    "SwarmIntelligenceSystemPython",
    "CulturalIntelligenceSystemPython",
    "SocialNetworkAnalysisPython",
    "CollaborativeIntelligenceOrchestratorPython",
    
    # Singletons
    "get_social_cognition_engine",
    "get_group_dynamics_system",
    "get_collective_decision_system",
    "get_swarm_intelligence_system",
    "get_cultural_intelligence_system",
    "get_social_network_analysis",
    "get_collaboration_orchestrator",
    
    # Pure Python singleton getters
    "get_social_cognition_engine_python",
    "get_group_dynamics_system_python",
    "get_collective_decision_system_python",
    "get_swarm_intelligence_system_python",
    "get_cultural_intelligence_system_python",
    "get_social_network_analysis_python",
    "get_collaboration_orchestrator_python",
    
    # Dual-version flag
    "HAS_NUMPY",
]
