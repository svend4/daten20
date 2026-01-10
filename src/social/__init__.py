"""
🌐 Social & Collective Intelligence Platform

Provides computational models of social cognition, group dynamics, collective
decision-making, swarm intelligence, cultural adaptation, and collaborative AI.

Version: 8.0.0
"""

__version__ = '8.0.0'

from .social_services import (
    # Social Cognition Engine
    SocialRole,
    SocialContext,
    AppropriatenessAssessment,
    BeliefChain,
    SocialCognitionEngine,
    get_social_cognition_engine,

    # Group Dynamics System
    GroupStage,
    LeadershipStyle,
    GroupStageAssessment,
    GroupthinkRisk,
    TeamComposition,
    GroupDynamicsSystem,
    get_group_dynamics_system,

    # Collective Decision Making
    VotingMethod,
    VotingResult,
    ConsensusResult,
    CollectiveAccuracy,
    CollectiveDecisionMaking,
    get_collective_decision_system,

    # Swarm Intelligence System
    SwarmAlgorithm,
    SwarmSolution,
    TaskAllocation,
    SwarmIntelligenceSystem,
    get_swarm_intelligence_system,

    # Cultural Intelligence System
    CulturalProfile,
    AdaptedCommunication,
    CulturalCompatibility,
    CulturalIntelligenceSystem,
    get_cultural_intelligence_system,

    # Social Network Analysis
    CentralityMeasure,
    NetworkAnalysis,
    SpreadPrediction,
    SocialNetworkAnalysis,
    get_social_network_analysis,

    # Collaborative Intelligence Orchestrator
    TaskGraph,
    AllocationResult,
    CollaborationHealth,
    CollaborativeIntelligenceOrchestrator,
    get_collaboration_orchestrator,
)

__all__ = [
    # Social Cognition Engine
    'SocialRole',
    'SocialContext',
    'AppropriatenessAssessment',
    'BeliefChain',
    'SocialCognitionEngine',
    'get_social_cognition_engine',

    # Group Dynamics System
    'GroupStage',
    'LeadershipStyle',
    'GroupStageAssessment',
    'GroupthinkRisk',
    'TeamComposition',
    'GroupDynamicsSystem',
    'get_group_dynamics_system',

    # Collective Decision Making
    'VotingMethod',
    'VotingResult',
    'ConsensusResult',
    'CollectiveAccuracy',
    'CollectiveDecisionMaking',
    'get_collective_decision_system',

    # Swarm Intelligence System
    'SwarmAlgorithm',
    'SwarmSolution',
    'TaskAllocation',
    'SwarmIntelligenceSystem',
    'get_swarm_intelligence_system',

    # Cultural Intelligence System
    'CulturalProfile',
    'AdaptedCommunication',
    'CulturalCompatibility',
    'CulturalIntelligenceSystem',
    'get_cultural_intelligence_system',

    # Social Network Analysis
    'CentralityMeasure',
    'NetworkAnalysis',
    'SpreadPrediction',
    'SocialNetworkAnalysis',
    'get_social_network_analysis',

    # Collaborative Intelligence Orchestrator
    'TaskGraph',
    'AllocationResult',
    'CollaborationHealth',
    'CollaborativeIntelligenceOrchestrator',
    'get_collaboration_orchestrator',
]
