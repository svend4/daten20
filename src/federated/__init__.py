"""
Federated Learning Platform Module

This module provides comprehensive privacy-preserving distributed machine learning
capabilities. It implements federated learning orchestration, differential privacy,
secure multi-party computation, Byzantine-resilient aggregation, edge model management,
federated analytics, and privacy-preserving training.

Version: 11.0.0
"""

from .federated_services import (
    # Enums
    FederationType,
    AggregationAlgorithm,
    PrivacyMechanism,
    ByzantineDefense,

    # Data Classes
    FederatedClient,
    GlobalModel,
    TrainingRound,
    PrivacyBudget,
    ClientUpdate,
    EdgeModel,
    SecretShare,
    FederatedQuery,

    # Services
    FederatedLearningOrchestrator,
    PrivacyPreservingTraining,
    ModelAggregationEngine,
    SecureMultiPartyComputation,
    EdgeModelManager,
    FederatedAnalyticsSystem,
    ByzantineResilientAggregator,

    # Singleton Getters
    get_fl_orchestrator,
    get_privacy_trainer,
    get_model_aggregator,
    get_secure_mpc,
    get_edge_model_manager,
    get_federated_analytics,
    get_byzantine_aggregator,
)

__all__ = [
    # Enums
    'FederationType',
    'AggregationAlgorithm',
    'PrivacyMechanism',
    'ByzantineDefense',

    # Data Classes
    'FederatedClient',
    'GlobalModel',
    'TrainingRound',
    'PrivacyBudget',
    'ClientUpdate',
    'EdgeModel',
    'SecretShare',
    'FederatedQuery',

    # Services
    'FederatedLearningOrchestrator',
    'PrivacyPreservingTraining',
    'ModelAggregationEngine',
    'SecureMultiPartyComputation',
    'EdgeModelManager',
    'FederatedAnalyticsSystem',
    'ByzantineResilientAggregator',

    # Singleton Getters
    'get_fl_orchestrator',
    'get_privacy_trainer',
    'get_model_aggregator',
    'get_secure_mpc',
    'get_edge_model_manager',
    'get_federated_analytics',
    'get_byzantine_aggregator',
]

__version__ = '11.0.0'
