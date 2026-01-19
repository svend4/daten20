"""
Comprehensive Test Suite for Human-AI Collaboration Platform (v20.0)

Tests all 7 subsystems and integrated system:
1. CollaborativeTaskManagement - Task creation & role allocation
2. HumanIntentUnderstanding - Intent recognition & prediction
3. AICapabilityMatching - Capability matching & recommendation
4. SharedMentalModels - Model synchronization & context sharing
5. MixedInitiativeControl - Control mode decisions & transitions
6. HumanPerformanceAugmentation - Cognitive & productivity augmentation
7. TrustTransparencyExplainability - Trust metrics & explanations
8. IntegratedHumanAICollabSystem - Unified collaboration workflows

Total: 48 tests
"""

import asyncio
import pytest
from datetime import datetime

from src.human_ai_collab import (
    # Enums
    TaskRole,
    IntentType,
    ControlMode,
    AugmentationType,
    ExplanationType,
    # Data Classes
    CollaborativeTask,
    Intent,
    Capability,
    MentalModel,
    AugmentationResult,
    Explanation,
    TrustMetrics,
    HumanAICollabConfig,
    # Service Classes
    CollaborativeTaskManagement,
    HumanIntentUnderstanding,
    AICapabilityMatching,
    SharedMentalModels,
    MixedInitiativeControl,
    HumanPerformanceAugmentation,
    TrustTransparencyExplainability,
    # Integrated System
    IntegratedHumanAICollabSystem,
    get_human_ai_collab_system,
)


# Test Human-AI Collaboration subsystems and integrated system
class TestCollaborativeTaskManagement:
    """Test Collaborative Task Management subsystem"""

    @pytest.mark.asyncio
    async def test_create_task(self):
        task_mgmt = CollaborativeTaskManagement()
        task = await task_mgmt.create_task(
            name="Test task",
            description="A test task",
            assigned_role=TaskRole.COLLABORATIVE,
        )

        assert task is not None
        assert task.name == "Test task"
        assert task.assigned_role == TaskRole.COLLABORATIVE
        assert task.status == "pending"

    @pytest.mark.asyncio
    async def test_decompose_task(self):
        task_mgmt = CollaborativeTaskManagement()
        subtasks = await task_mgmt.decompose_task("Build a web application")

        assert subtasks is not None
        assert len(subtasks) > 0

    @pytest.mark.asyncio
    async def test_allocate_role(self):
        task_mgmt = CollaborativeTaskManagement()
        task = CollaborativeTask(
            task_id="task_1",
            name="Complex analysis",
            description="Analyze data",
            assigned_role=TaskRole.NEGOTIATED,
            status="pending",
            created_at=datetime.now(),
        )

        role = await task_mgmt.allocate_role(task)
        assert role in [TaskRole.HUMAN, TaskRole.AI, TaskRole.COLLABORATIVE]

    @pytest.mark.asyncio
    async def test_update_task_status(self):
        task_mgmt = CollaborativeTaskManagement()
        task = await task_mgmt.create_task("Test", "Test task", TaskRole.AI)

        result = await task_mgmt.update_task_status(task.task_id, "completed", progress=1.0)
        assert result is not None


class TestHumanIntentUnderstanding:
    """Test Human Intent Understanding subsystem"""

    @pytest.mark.asyncio
    async def test_understand_intent(self):
        intent_system = HumanIntentUnderstanding()
        intent = await intent_system.understand_intent(
            "Help me analyze this data", user_history=[]
        )

        assert intent is not None
        assert intent.intent_type in [t for t in IntentType]
        assert 0 <= intent.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_predict_next_action(self):
        intent_system = HumanIntentUnderstanding()
        prediction = await intent_system.predict_next_action(
            current_intent="analyze data",
            user_history=[{"action": "load_data"}, {"action": "clean_data"}],
        )

        assert prediction is not None

    @pytest.mark.asyncio
    async def test_clarify_ambiguity(self):
        intent_system = HumanIntentUnderstanding()
        clarification = await intent_system.clarify_ambiguity(
            ambiguous_input="Do that thing",
            context={"previous_action": "data_analysis"},
        )

        assert clarification is not None


class TestAICapabilityMatching:
    """Test AI Capability Matching subsystem"""

    @pytest.mark.asyncio
    async def test_match_capabilities(self):
        capability_system = AICapabilityMatching()
        capabilities = [
            Capability("text_generation", "Generate text", 0.9, ["nlp"], {}),
            Capability("data_analysis", "Analyze data", 0.85, ["analytics"], {}),
        ]

        matches = await capability_system.match_capabilities_to_need(
            user_need="I need to analyze some data",
            available_capabilities=capabilities,
        )

        assert matches is not None
        assert len(matches) > 0

    @pytest.mark.asyncio
    async def test_recommend_capabilities(self):
        capability_system = AICapabilityMatching()

        recommendations = await capability_system.recommend_capabilities(
            task_description="Build a machine learning model",
            user_profile={"expertise": "beginner"},
        )

        assert recommendations is not None

    @pytest.mark.asyncio
    async def test_assess_capability_gap(self):
        capability_system = AICapabilityMatching()

        gap = await capability_system.assess_capability_gap(
            required_capabilities=["ml_modeling", "data_viz"],
            available_capabilities=["data_viz"],
        )

        assert gap is not None
        assert "ml_modeling" in gap["missing"]


class TestSharedMentalModels:
    """Test Shared Mental Models subsystem"""

    @pytest.mark.asyncio
    async def test_update_model(self):
        mental_models = SharedMentalModels()

        result = await mental_models.update_model(
            model_id="test_model",
            model_data={"concept": "data", "value": 42},
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_synchronize_understanding(self):
        mental_models = SharedMentalModels()

        sync_result = await mental_models.synchronize_understanding(
            human_model={"belief": "A", "confidence": 0.8},
            ai_model={"belief": "A", "confidence": 0.9},
        )

        assert sync_result is not None
        assert "alignment_score" in sync_result

    @pytest.mark.asyncio
    async def test_detect_misalignment(self):
        mental_models = SharedMentalModels()

        misalignment = await mental_models.detect_misalignment(
            human_understanding={"concept": "X"},
            ai_understanding={"concept": "Y"},
        )

        assert misalignment is not None


class TestMixedInitiativeControl:
    """Test Mixed-Initiative Control subsystem"""

    @pytest.mark.asyncio
    async def test_decide_control_transfer(self):
        control_system = MixedInitiativeControl()

        decision = await control_system.decide_control_transfer(
            current_mode=ControlMode.COLLABORATIVE,
            task_complexity=0.7,
            ai_confidence=0.85,
            user_expertise=0.6,
        )

        assert decision is not None
        assert "recommended_mode" in decision

    @pytest.mark.asyncio
    async def test_handle_interruption(self):
        control_system = MixedInitiativeControl()

        response = await control_system.handle_interruption(
            current_activity="data_analysis",
            interrupt_reason="user_request",
        )

        assert response is not None

    @pytest.mark.asyncio
    async def test_negotiate_control(self):
        control_system = MixedInitiativeControl()

        negotiation = await control_system.negotiate_control(
            human_preference=ControlMode.COMMAND_CONTROL,
            ai_recommendation=ControlMode.COLLABORATIVE,
            context={"urgency": "high"},
        )

        assert negotiation is not None


class TestHumanPerformanceAugmentation:
    """Test Human Performance Augmentation subsystem"""

    @pytest.mark.asyncio
    async def test_provide_cognitive_augmentation(self):
        augmentation = HumanPerformanceAugmentation()

        result = await augmentation.provide_cognitive_augmentation(
            user_task="Complex calculation",
            current_cognitive_load=0.8,
            available_aids=["calculator", "visualization"],
        )

        assert result is not None
        assert result.augmentation_type == AugmentationType.COGNITIVE

    @pytest.mark.asyncio
    async def test_provide_productivity_augmentation(self):
        augmentation = HumanPerformanceAugmentation()

        result = await augmentation.provide_productivity_augmentation(
            user_workflow=["step1", "step2", "step3"],
            automation_opportunities=["step2"],
        )

        assert result is not None
        assert result.augmentation_type == AugmentationType.PRODUCTIVITY

    @pytest.mark.asyncio
    async def test_adaptive_interface(self):
        augmentation = HumanPerformanceAugmentation()

        adaptation = await augmentation.adaptive_interface(
            user_context={"task": "coding", "expertise": "intermediate"},
            current_interface="standard",
        )

        assert adaptation is not None


class TestTrustTransparencyExplainability:
    """Test Trust, Transparency & Explainability subsystem"""

    @pytest.mark.asyncio
    async def test_generate_explanation(self):
        trust_system = TrustTransparencyExplainability()

        explanation = await trust_system.generate_explanation(
            model_output="Classification: Positive",
            explanation_type=ExplanationType.LOCAL,
            target_audience="general",
        )

        assert explanation is not None
        assert explanation.explanation_type == ExplanationType.LOCAL

    @pytest.mark.asyncio
    async def test_measure_trust(self):
        trust_system = TrustTransparencyExplainability()

        metrics = await trust_system.measure_trust(
            model_id="test_model",
            ai_predictions=[("A", 0.9), ("B", 0.8), ("C", 0.7)],
            actual_outcomes=[True, True, False],
            user_reliance_decisions=[True, True, False],
        )

        assert metrics is not None
        assert 0 <= metrics.appropriate_reliance <= 1.0

    @pytest.mark.asyncio
    async def test_communicate_uncertainty(self):
        trust_system = TrustTransparencyExplainability()

        message = await trust_system.communicate_uncertainty(
            prediction="Outcome A",
            confidence=0.65,
        )

        assert message is not None
        assert len(message) > 0

    @pytest.mark.asyncio
    async def test_ensure_transparency(self):
        trust_system = TrustTransparencyExplainability()

        transparency = await trust_system.ensure_transparency(
            action="made_prediction",
            reasoning="based on historical patterns",
            data_used=["dataset1", "dataset2"],
        )

        assert transparency is not None
        assert "behavioral" in transparency


class TestIntegratedHumanAICollabSystem:
    """Test Integrated Human-AI Collaboration System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = HumanAICollabConfig(
            enable_task_management=True,
            enable_intent_understanding=True,
            enable_trust_transparency=True,
        )

        system = IntegratedHumanAICollabSystem(config)
        assert system.task_mgmt is not None
        assert system.intent is not None
        assert system.trust is not None

    @pytest.mark.asyncio
    async def test_human_ai_task_execution(self):
        system = IntegratedHumanAICollabSystem()

        result = await system.human_ai_task_execution(
            user_input="Help me analyze this dataset",
            user_history=[],
            available_capabilities=None,
        )

        assert result is not None
        assert "task_id" in result
        assert "intent" in result
        assert "matched_capability" in result
        assert "control_mode" in result

    @pytest.mark.asyncio
    async def test_adaptive_collaboration(self):
        system = IntegratedHumanAICollabSystem()

        result = await system.adaptive_collaboration(
            task_description="Build a dashboard",
            context={"task_complexity": 0.6, "ai_confidence": 0.85, "user_expertise": 0.7},
            user_preferences={"control_preference": "collaborative"},
        )

        assert result is not None
        assert "recommended_control_mode" in result
        assert "augmentation_type" in result
        assert "model_alignment" in result

    @pytest.mark.asyncio
    async def test_trust_calibration_workflow(self):
        system = IntegratedHumanAICollabSystem()

        # Predictions: (prediction, confidence, user_relied)
        predictions = [
            ("A", 0.9, True),
            ("B", 0.8, True),
            ("C", 0.6, False),
            ("D", 0.5, False),
        ]

        result = await system.trust_calibration_workflow(
            model_id="test_model",
            predictions=predictions,
        )

        assert result is not None
        assert "trust_metrics" in result
        assert "calibration_actions" in result
        assert "is_well_calibrated" in result

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedHumanAICollabSystem()
        status = system.get_system_status()

        assert status is not None
        assert "task_management_enabled" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedHumanAICollabSystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_human_ai_collab_system()
        system2 = get_human_ai_collab_system()

        assert system1 is system2

    @pytest.mark.asyncio
    async def test_collaborative_workflow(self):
        """Test complete collaborative workflow"""
        system = IntegratedHumanAICollabSystem()

        # Execute full workflow
        result = await system.human_ai_task_execution(
            user_input="Create a visualization of sales data",
            user_history=[
                {"action": "loaded_data", "timestamp": "2026-01-19"},
            ],
            available_capabilities=[
                Capability("data_viz", "Create visualizations", 0.9, ["charts", "graphs"], {}),
                Capability("data_analysis", "Analyze data", 0.85, ["statistics"], {}),
            ],
        )

        # Verify workflow completion
        assert result["confidence"] > 0.5
        assert result["matched_capability"] in ["data_viz", "data_analysis"]

    @pytest.mark.asyncio
    async def test_trust_building(self):
        """Test trust building over time"""
        system = IntegratedHumanAICollabSystem()

        # Initial trust calibration with good predictions
        good_predictions = [
            ("Correct", 0.9, True),
            ("Correct", 0.85, True),
            ("Correct", 0.8, True),
        ]

        result = await system.trust_calibration_workflow(
            model_id="reliable_model",
            predictions=good_predictions,
        )

        assert result["trust_metrics"]["appropriate_reliance"] > 0.7

    @pytest.mark.asyncio
    async def test_context_adaptation(self):
        """Test system adaptation to different contexts"""
        system = IntegratedHumanAICollabSystem()

        # High complexity task
        high_complexity = await system.adaptive_collaboration(
            task_description="Design complex AI system",
            context={"task_complexity": 0.9, "ai_confidence": 0.7, "user_expertise": 0.5},
        )

        # Low complexity task
        low_complexity = await system.adaptive_collaboration(
            task_description="Simple data entry",
            context={"task_complexity": 0.2, "ai_confidence": 0.95, "user_expertise": 0.9},
        )

        # Verify different recommendations
        assert high_complexity["recommended_control_mode"] != low_complexity["recommended_control_mode"] or \
               high_complexity["augmentation_type"] != low_complexity["augmentation_type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
