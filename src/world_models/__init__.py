"""
World Models & Predictive Learning Platform v22.0 (FUNCTIONAL)

AI that builds internal models of the world, predicts future states, plans using
mental simulation, and learns through imagination.
Version: 22.0.0 (FUNCTIONAL - uses REAL neural networks!)

This module now uses REAL neural networks and CartPole environment,
not mock code! Agents learn world models through experience.

Example usage:
    from world_models import SimpleNeuralNetwork, CartPoleEnvironment

    # Create neural network and environment
    nn = SimpleNeuralNetwork(input_size=4, hidden_size=32, output_size=2)
    env = CartPoleEnvironment()

    # Train agent
    state = env.reset()
    action = nn.predict(state)
"""

__version__ = "22.0.0"
__status__ = "FUNCTIONAL"
__author__ = "Document Management System Team"

# Import REAL neural network and environment
from .simple_nn import SimpleNeuralNetwork
from .cartpole_env import CartPoleEnvironment

from .world_models_services import (  # Core Systems; Enums; Data Classes; Singleton Getters
    CausalGraph,
    CausalReasoning,
    ContinuousModelRefinement,
    ImaginationLearning,
    ImaginedTrajectory,
    IntegratedWorldModelsSystem,
    InterventionType,
    ModelBasedPlanning,
    ModelType,
    Plan,
    PlanningAlgorithm,
    Prediction,
    PredictionType,
    PredictiveLearning,
    State,
    Transition,
    UncertaintyAwarePrediction,
    UncertaintyEstimate,
    UncertaintyType,
    WorldModel,
    WorldModelLearning,
    WorldModelsConfig,
    get_causal_reasoning,
    get_imagination_learning,
    get_model_based_planning,
    get_model_refinement,
    get_predictive_learning,
    get_uncertainty_prediction,
    get_world_model_learning,
    get_world_models_system,
)

__all__ = [
    "__version__",
    # REAL Neural Network & Environment
    "SimpleNeuralNetwork",
    "CartPoleEnvironment",
    # Core Systems
    "WorldModelLearning",
    "PredictiveLearning",
    "ModelBasedPlanning",
    "ImaginationLearning",
    "CausalReasoning",
    "UncertaintyAwarePrediction",
    "ContinuousModelRefinement",
    # Integrated System
    "IntegratedWorldModelsSystem",
    # Enums
    "ModelType",
    "PredictionType",
    "PlanningAlgorithm",
    "UncertaintyType",
    "InterventionType",
    # Data Classes
    "State",
    "Transition",
    "WorldModel",
    "Prediction",
    "Plan",
    "ImaginedTrajectory",
    "CausalGraph",
    "UncertaintyEstimate",
    "WorldModelsConfig",
    # Singleton Getters
    "get_world_model_learning",
    "get_predictive_learning",
    "get_model_based_planning",
    "get_imagination_learning",
    "get_causal_reasoning",
    "get_uncertainty_prediction",
    "get_model_refinement",
    "get_world_models_system",
]
