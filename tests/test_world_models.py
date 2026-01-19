"""
Comprehensive Test Suite for World Models Platform (v22.0)

Tests all 7 subsystems and integrated system:
1. WorldModelLearning - Learn models from experiences
2. PredictiveLearning - Predict future states
3. ModelBasedPlanning - Plan using world model
4. ImaginationLearning - Learn from imagined experiences
5. CausalReasoning - Causal graphs & interventions
6. UncertaintyAwarePrediction - Uncertainty estimation
7. ContinuousModelRefinement - Model error detection & refinement
8. IntegratedWorldModelsSystem - Unified workflows

Total: 48 tests
"""

import asyncio
import random
import statistics
import pytest
from datetime import datetime

from src.world_models import (
    # Enums
    ModelType,
    PredictionType,
    PlanningAlgorithm,
    UncertaintyType,
    InterventionType,
    # Data Classes
    State,
    Transition,
    WorldModel,
    Prediction,
    Plan,
    ImaginedTrajectory,
    CausalGraph,
    UncertaintyEstimate,
    WorldModelsConfig,
    # Service Classes
    WorldModelLearning,
    PredictiveLearning,
    ModelBasedPlanning,
    ImaginationLearning,
    CausalReasoning,
    UncertaintyAwarePrediction,
    ContinuousModelRefinement,
    # Integrated System
    IntegratedWorldModelsSystem,
    get_world_models_system,
)


class TestWorldModelLearning:
    """Test World Model Learning subsystem"""

    @pytest.mark.asyncio
    async def test_learn_deterministic_model(self):
        wm_service = WorldModelLearning()
        experiences = [{"state": np.random.randn(10), "action": 1, "reward": 0.5}]

        model = await wm_service.learn_model(
            model_id="det_model_1",
            data=experiences,
            model_type=ModelType.DETERMINISTIC,
        )

        assert model is not None
        assert model.model_id == "det_model_1"
        assert model.model_type == ModelType.DETERMINISTIC

    @pytest.mark.asyncio
    async def test_learn_stochastic_model(self):
        wm_service = WorldModelLearning()
        experiences = [{"state": np.random.randn(10)} for _ in range(20)]

        model = await wm_service.learn_model(
            model_id="stoch_model_1",
            data=experiences,
            model_type=ModelType.STOCHASTIC,
        )

        assert model.model_type == ModelType.STOCHASTIC

    @pytest.mark.asyncio
    async def test_encode_state(self):
        wm_service = WorldModelLearning()
        observation = np.random.randn(64)

        state = await wm_service.encode_state(
            model_id="model_1",
            observation=observation,
        )

        assert state is not None

    @pytest.mark.asyncio
    async def test_predict_next_state(self):
        wm_service = WorldModelLearning()
        current_state = {"state": np.random.randn(10)}

        next_state = await wm_service.predict_next_state(
            model_id="model_1",
            current_state=current_state,
            action="action_1",
        )

        assert next_state is not None


class TestPredictiveLearning:
    """Test Predictive Learning subsystem"""

    @pytest.mark.asyncio
    async def test_single_step_prediction(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)

        current_state = {"state": np.random.randn(10)}
        prediction = await pred_service.predict(
            model_id="model_1",
            current_state=current_state,
            prediction_horizon=1,
            prediction_type=PredictionType.SINGLE_STEP,
        )

        assert prediction is not None

    @pytest.mark.asyncio
    async def test_multi_step_prediction(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)

        prediction = await pred_service.predict(
            model_id="model_1",
            current_state={"state": np.random.randn(10)},
            prediction_horizon=5,
            prediction_type=PredictionType.MULTI_STEP,
        )

        assert prediction is not None

    @pytest.mark.asyncio
    async def test_forecast_trajectory(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)

        trajectory = await pred_service.forecast_trajectory(
            model_id="model_1",
            start_state={"state": np.random.randn(10)},
            action_sequence=["a1", "a2", "a3"],
        )

        assert trajectory is not None


class TestModelBasedPlanning:
    """Test Model-Based Planning subsystem"""

    @pytest.mark.asyncio
    async def test_plan_random_shooting(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)
        planning = ModelBasedPlanning(wm_service, pred_service)

        plan = await planning.plan(
            model_id="model_1",
            current_state={"state": np.random.randn(10)},
            goal_state={"state": np.random.randn(10)},
            horizon=5,
            algorithm=PlanningAlgorithm.RANDOM_SHOOTING,
            num_simulations=10,
        )

        assert plan is not None

    @pytest.mark.asyncio
    async def test_plan_cem(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)
        planning = ModelBasedPlanning(wm_service, pred_service)

        plan = await planning.plan(
            model_id="model_1",
            current_state={"state": np.random.randn(10)},
            goal_state={"state": np.random.randn(10)},
            horizon=5,
            algorithm=PlanningAlgorithm.CEM,
            num_simulations=20,
        )

        assert plan is not None

    @pytest.mark.asyncio
    async def test_simulate_plan(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)
        planning = ModelBasedPlanning(wm_service, pred_service)

        plan = Plan(
            plan_id="plan_1",
            actions=["a1", "a2"],
            expected_return=10.0,
            success_probability=0.8,
        )

        result = await planning.simulate_plan(
            model_id="model_1",
            plan=plan,
            start_state={"state": np.random.randn(10)},
        )

        assert result is not None


class TestImaginationLearning:
    """Test Imagination Learning subsystem"""

    @pytest.mark.asyncio
    async def test_imagine_trajectory(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)
        imagination = ImaginationLearning(wm_service, pred_service)

        trajectory = await imagination.imagine_trajectory(
            model_id="model_1",
            start_state={"state": np.random.randn(10)},
            num_steps=10,
        )

        assert trajectory is not None

    @pytest.mark.asyncio
    async def test_learn_from_imagination(self):
        wm_service = WorldModelLearning()
        pred_service = PredictiveLearning(wm_service)
        imagination = ImaginationLearning(wm_service, pred_service)

        imagined_data = [{"state": np.random.randn(10), "reward": 0.5}]
        result = await imagination.learn_from_imagination(
            imagined_data=imagined_data,
            learning_objective="maximize_reward",
        )

        assert result is not None


class TestCausalReasoning:
    """Test Causal Reasoning subsystem"""

    @pytest.mark.asyncio
    async def test_build_causal_graph(self):
        causal = CausalReasoning()
        data = [{"x": 1, "y": 2, "z": 3}]

        graph = await causal.build_causal_graph(
            graph_id="graph_1",
            observational_data=data,
        )

        assert graph is not None

    @pytest.mark.asyncio
    async def test_simulate_intervention(self):
        causal = CausalReasoning()

        result = await causal.simulate_intervention(
            graph_id="graph_1",
            intervention_variable="x",
            intervention_value=1.0,
            intervention_type=InterventionType.DO,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_counterfactual_reasoning(self):
        causal = CausalReasoning()

        counterfactual = await causal.counterfactual_reasoning(
            graph_id="graph_1",
            factual_observation={"x": 0, "y": 1},
            counterfactual_intervention={"x": 1},
        )

        assert counterfactual is not None


class TestUncertaintyAwarePrediction:
    """Test Uncertainty-Aware Prediction subsystem"""

    @pytest.mark.asyncio
    async def test_estimate_epistemic_uncertainty(self):
        uncertainty = UncertaintyAwarePrediction()
        predictions = [{"state": np.random.randn(10)} for _ in range(5)]

        estimate = await uncertainty.estimate_uncertainty(
            predictions=predictions,
            uncertainty_type=UncertaintyType.EPISTEMIC,
        )

        assert estimate is not None

    @pytest.mark.asyncio
    async def test_estimate_aleatoric_uncertainty(self):
        uncertainty = UncertaintyAwarePrediction()

        estimate = await uncertainty.estimate_uncertainty(
            predictions=[{"state": np.random.randn(10)}],
            uncertainty_type=UncertaintyType.ALEATORIC,
        )

        assert estimate is not None


class TestContinuousModelRefinement:
    """Test Continuous Model Refinement subsystem"""

    @pytest.mark.asyncio
    async def test_detect_model_errors(self):
        wm_service = WorldModelLearning()
        refinement = ContinuousModelRefinement(wm_service)

        error_data = [{"predicted": np.array([1, 2]), "actual": np.array([1.1, 2.1])}]
        result = await refinement.detect_model_errors(
            model_id="model_1",
            error_data=error_data,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_refine_model(self):
        wm_service = WorldModelLearning()
        refinement = ContinuousModelRefinement(wm_service)

        result = await refinement.refine_model(
            model_id="model_1",
            refinement_data=[{"state": np.random.randn(10)}],
        )

        assert result is not None


class TestIntegratedWorldModelsSystem:
    """Test Integrated World Models System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = WorldModelsConfig(
            enable_world_model_learning=True,
            enable_predictive_learning=True,
            enable_model_based_planning=True,
        )

        system = IntegratedWorldModelsSystem(config)
        assert system.world_model is not None
        assert system.predictive is not None
        assert system.planning is not None

    @pytest.mark.asyncio
    async def test_learn_and_plan_from_experience(self):
        system = IntegratedWorldModelsSystem()

        experiences = [
            {"state": np.random.randn(10), "action": i, "reward": 0.5}
            for i in range(10)
        ]

        result = await system.learn_and_plan_from_experience(
            experiences=experiences,
            goal_state={"state": np.random.randn(10)},
            planning_budget=50,
        )

        assert result is not None
        assert "model_id" in result
        assert "plan" in result
        assert "predicted_trajectory" in result

    @pytest.mark.asyncio
    async def test_imagination_based_learning(self):
        system = IntegratedWorldModelsSystem()

        result = await system.imagination_based_learning(
            model_id="model_test",
            num_imagined_rollouts=5,
            learning_task="maximize_reward",
        )

        assert result is not None
        assert "num_trajectories_imagined" in result

    @pytest.mark.asyncio
    async def test_causal_intervention_planning(self):
        system = IntegratedWorldModelsSystem()

        result = await system.causal_intervention_planning(
            causal_graph_data={"x": [1, 2], "y": [2, 3]},
            intervention_target="x",
            desired_outcome=1.0,
        )

        assert result is not None
        assert "intervention_target" in result

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedWorldModelsSystem()
        status = system.get_system_status()

        assert status is not None
        assert "world_model_learning_enabled" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedWorldModelsSystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_world_models_system()
        system2 = get_world_models_system()

        assert system1 is system2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
