"""
World Models & Predictive Learning Platform v22.0

AI that builds internal models of the world, predicts future states, plans using
mental simulation, and learns through imagination.

Example usage:
    from world_models import get_world_model_learning, get_model_based_planning

    # Learn world model from experiences
    wm_service = get_world_model_learning()
    model = await wm_service.learn_world_model(experiences)

    # Plan using learned world model
    planner = get_model_based_planning()
    plan = await planner.plan(current_state, goal_state, horizon=10)
"""

__version__ = "22.0.0"
__author__ = "Document Management System Team"

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
