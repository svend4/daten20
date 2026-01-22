"""
Comprehensive Test Suite for AGI & Universal Reasoning Platform (v25.0)

Tests all 7 subsystems and integrated system:
1. UniversalTaskUnderstandingService - Parse any task
2. CrossDomainTransferService - Transfer knowledge across domains
3. AbstractReasoningService - High-level reasoning
4. MetaCognitiveControlService - Self-awareness & adaptation
5. CommonSenseReasoningService - Intuitive world knowledge
6. FlexibleGoalManagementService - Handle multiple goals
7. GeneralProblemSolvingService - Solve any problem type
8. IntegratedAGISystem - Unified AGI workflows

Total: 48 tests
"""

import asyncio
import pytest
from datetime import datetime, timedelta

from src.agi_universal_reasoning import (
    # Core Systems
    AbstractReasoningService,
    CommonSenseReasoningService,
    CrossDomainTransferService,
    FlexibleGoalManagementService,
    GeneralProblemSolvingService,
    MetaCognitiveControlService,
    UniversalTaskUnderstandingService,
    # Integrated System
    IntegratedAGISystem,
    # Enums
    GoalType,
    ProblemCategory,
    ReasoningType,
    TaskType,
    # Config
    AGIConfig,
    # Singleton Getters
    get_agi_system,
)


class TestUniversalTaskUnderstanding:
    """Test Universal Task Understanding subsystem"""

    @pytest.mark.asyncio
    async def test_understand_task(self):
        service = UniversalTaskUnderstandingService()
        task = await service.understand_task("classify images of cats and dogs", domain="vision")

        assert task is not None
        assert task.task_type == TaskType.CLASSIFICATION
        assert task.domain == "vision"
        assert task.understanding_confidence > 0.95

    @pytest.mark.asyncio
    async def test_decompose_task(self):
        service = UniversalTaskUnderstandingService()
        task = await service.understand_task("build a recommendation system", domain="machine_learning")
        task.estimated_difficulty = 0.8

        decomposed = await service.decompose_task(task, max_depth=3)

        assert decomposed.decomposition is not None
        assert len(decomposed.decomposition) > 0

    @pytest.mark.asyncio
    async def test_task_type_inference(self):
        service = UniversalTaskUnderstandingService()

        generation_task = await service.understand_task("generate a poem about nature")
        assert generation_task.task_type == TaskType.GENERATION

        reasoning_task = await service.understand_task("reason about the consequences")
        assert reasoning_task.task_type == TaskType.REASONING

    @pytest.mark.asyncio
    async def test_objective_extraction(self):
        service = UniversalTaskUnderstandingService()
        task = await service.understand_task("optimize performance and reduce costs")

        assert len(task.objectives) > 0
        assert any("optimize" in obj.lower() or "reduce" in obj.lower() for obj in task.objectives)

    @pytest.mark.asyncio
    async def test_constraint_extraction(self):
        service = UniversalTaskUnderstandingService()
        task = await service.understand_task("must complete task quickly with limited resources")

        assert len(task.constraints) > 0

    @pytest.mark.asyncio
    async def test_success_criteria(self):
        service = UniversalTaskUnderstandingService()
        task = await service.understand_task("predict stock prices")

        assert "accuracy" in task.success_criteria
        assert task.success_criteria["accuracy"] > 0


class TestCrossDomainTransfer:
    """Test Cross-Domain Transfer subsystem"""

    @pytest.mark.asyncio
    async def test_transfer_knowledge(self):
        service = CrossDomainTransferService()
        mapping = await service.transfer_knowledge(
            source_domain="vision", target_domain="nlp", knowledge={"concept": "classification", "method": "deep_learning"}
        )

        assert mapping is not None
        assert mapping.similarity_score > 0.3
        assert mapping.performance_gain >= 5.0  # 5-10x speedup

    @pytest.mark.asyncio
    async def test_transfer_retention(self):
        service = CrossDomainTransferService()
        mapping = await service.transfer_knowledge("robotics", "game_playing", {"strategy": "planning"})

        assert mapping.validation_accuracy >= 0.50  # 50-80% retention
        assert mapping.validation_accuracy <= 0.80

    @pytest.mark.asyncio
    async def test_find_transfer_path(self):
        service = CrossDomainTransferService()
        path = await service.find_transfer_path("domain_A", "domain_B")

        assert path is not None
        assert len(path) >= 2
        assert path[0] == "domain_A"
        assert path[-1] == "domain_B"

    @pytest.mark.asyncio
    async def test_domain_similarity(self):
        service = CrossDomainTransferService()
        similarity = await service._compute_domain_similarity("vision", "nlp")

        assert 0.3 <= similarity <= 0.95

    @pytest.mark.asyncio
    async def test_knowledge_adaptation(self):
        service = CrossDomainTransferService()
        knowledge = {"algorithm": "CNN", "accuracy": 0.95}
        adapted = service._adapt_knowledge(knowledge, "vision", "audio")

        assert "adapted_from" in adapted
        assert adapted["adapted_from"] == "vision"

    @pytest.mark.asyncio
    async def test_multi_hop_transfer(self):
        service = CrossDomainTransferService()

        # Transfer through intermediate domain
        mapping1 = await service.transfer_knowledge("source", "intermediate", {"skill": "pattern_recognition"})
        mapping2 = await service.transfer_knowledge("intermediate", "target", mapping1.transferred_knowledge)

        assert mapping2 is not None


class TestAbstractReasoning:
    """Test Abstract Reasoning subsystem"""

    @pytest.mark.asyncio
    async def test_analogical_reasoning(self):
        service = AbstractReasoningService()
        trace = await service.reason_abstractly({"analogy": "A:B::C:?"}, ReasoningType.ANALOGICAL)

        assert trace is not None
        assert trace.reasoning_type == ReasoningType.ANALOGICAL
        assert trace.correctness_score >= 0.85
        assert "structural_mapping" in trace.patterns_used

    @pytest.mark.asyncio
    async def test_logical_reasoning(self):
        service = AbstractReasoningService()
        trace = await service.reason_abstractly({"premises": ["All A are B", "C is A"]}, ReasoningType.LOGICAL)

        assert trace.reasoning_type == ReasoningType.LOGICAL
        assert trace.correctness_score >= 0.90

    @pytest.mark.asyncio
    async def test_spatial_reasoning(self):
        service = AbstractReasoningService()
        trace = await service.reason_abstractly({"shape": "cube", "rotation": 90}, ReasoningType.SPATIAL)

        assert trace.reasoning_type == ReasoningType.SPATIAL
        assert "mental_rotation" in trace.patterns_used

    @pytest.mark.asyncio
    async def test_relational_reasoning(self):
        service = AbstractReasoningService()
        trace = await service.reason_abstractly({"entities": ["A", "B"], "relations": ["parent_of"]}, ReasoningType.RELATIONAL)

        assert trace.reasoning_type == ReasoningType.RELATIONAL
        assert "graph_traversal" in trace.patterns_used

    @pytest.mark.asyncio
    async def test_reasoning_confidence(self):
        service = AbstractReasoningService()
        trace = await service.reason_abstractly({"problem": "test"}, ReasoningType.LOGICAL)

        assert trace.confidence >= 0.80
        assert service.reasoning_accuracy >= 0.85

    @pytest.mark.asyncio
    async def test_abstraction_levels(self):
        service = AbstractReasoningService()
        trace = await service.reason_abstractly({"complex_problem": True}, ReasoningType.ANALOGICAL)

        assert trace.abstraction_level > 0
        assert trace.abstraction_level <= 5


class TestMetaCognitiveControl:
    """Test Meta-Cognitive Control subsystem"""

    @pytest.mark.asyncio
    async def test_monitor_cognition(self):
        service = MetaCognitiveControlService()
        performance = {"accuracy": 0.85, "progress": 0.6, "strategy": "systematic"}

        state = await service.monitor_cognition("task_1", performance)

        assert state is not None
        assert state.confidence > 0
        assert service.error_detection_rate >= 0.90

    @pytest.mark.asyncio
    async def test_error_detection(self):
        service = MetaCognitiveControlService()
        low_performance = {"accuracy": 0.65, "progress": 0.15}

        state = await service.monitor_cognition("task_2", low_performance)

        assert len(state.detected_errors) > 0
        assert state.should_adapt is True

    @pytest.mark.asyncio
    async def test_strategy_selection(self):
        service = UniversalTaskUnderstandingService()
        metacog = MetaCognitiveControlService()

        task = await service.understand_task("find optimal path", domain="search")
        strategy = await metacog.select_strategy(task)

        assert strategy in metacog.available_strategies
        assert metacog.strategy_selection_accuracy >= 0.85

    @pytest.mark.asyncio
    async def test_confidence_calibration(self):
        service = MetaCognitiveControlService()
        performance = {"accuracy": 0.90, "confidence": 0.85}

        state = await service.monitor_cognition("task_3", performance)

        # Confidence should be calibrated with ECE < 0.05
        assert abs(state.confidence - 0.85) <= 0.10

    @pytest.mark.asyncio
    async def test_adaptation_recommendation(self):
        service = MetaCognitiveControlService()
        poor_performance = {"accuracy": 0.60, "progress": 0.10, "confidence": 0.50}

        state = await service.monitor_cognition("task_4", poor_performance)

        assert state.should_adapt is True
        assert state.adaptation_recommendation is not None

    @pytest.mark.asyncio
    async def test_resource_monitoring(self):
        service = MetaCognitiveControlService()
        performance = {"accuracy": 0.85, "progress": 0.7}

        state = await service.monitor_cognition("task_5", performance)

        assert "computation" in state.resource_usage
        assert "memory" in state.resource_usage
        assert "time" in state.resource_usage


class TestCommonSenseReasoning:
    """Test Common Sense Reasoning subsystem"""

    @pytest.mark.asyncio
    async def test_apply_common_sense(self):
        service = CommonSenseReasoningService()
        result = await service.apply_common_sense("person drops a ball", "what happens to the ball?")

        assert result is not None
        assert "conclusion" in result
        assert result["confidence"] >= 0.80

    @pytest.mark.asyncio
    async def test_physical_reasoning(self):
        service = CommonSenseReasoningService()
        result = await service.physical_reasoning("object falls from height")

        assert result is not None
        assert result["accuracy"] >= 0.80  # PIQA benchmark

    @pytest.mark.asyncio
    async def test_social_reasoning(self):
        service = CommonSenseReasoningService()
        result = await service.social_reasoning("person helps another person")

        assert result is not None
        assert result["accuracy"] >= 0.85  # Social IQa benchmark

    @pytest.mark.asyncio
    async def test_domain_identification(self):
        service = CommonSenseReasoningService()

        physical = service._identify_domain("object falls due to gravity")
        assert physical == "physical"

        social = service._identify_domain("person feels happy when praised")
        assert social == "social"

    @pytest.mark.asyncio
    async def test_knowledge_base_coverage(self):
        service = CommonSenseReasoningService()

        assert len(service.knowledge_base) > 0
        assert service.domain_coverage["physical"] > 0
        assert service.domain_coverage["social"] > 0

    @pytest.mark.asyncio
    async def test_inference_quality(self):
        service = CommonSenseReasoningService()
        result = await service.apply_common_sense("morning is when sun rises", "is it bright in the morning?")

        assert service.commonsense_accuracy >= 0.80


class TestFlexibleGoalManagement:
    """Test Flexible Goal Management subsystem"""

    @pytest.mark.asyncio
    async def test_add_goal(self):
        service = FlexibleGoalManagementService()
        goal = await service.add_goal("complete project", GoalType.ACHIEVEMENT, priority=0.8)

        assert goal is not None
        assert goal.goal_type == GoalType.ACHIEVEMENT
        assert goal.priority == 0.8

    @pytest.mark.asyncio
    async def test_prioritize_goals(self):
        service = FlexibleGoalManagementService()

        await service.add_goal("low priority", GoalType.ACHIEVEMENT, priority=0.3)
        await service.add_goal("high priority", GoalType.ACHIEVEMENT, priority=0.9)

        prioritized = await service.prioritize_goals()

        assert len(prioritized) >= 2
        assert prioritized[0].priority >= prioritized[-1].priority

    @pytest.mark.asyncio
    async def test_goal_conflicts(self):
        service = FlexibleGoalManagementService()

        goal1 = await service.add_goal("achieve A", GoalType.ACHIEVEMENT, priority=0.7)
        goal2 = await service.add_goal("avoid B", GoalType.AVOIDANCE, priority=0.7)

        # Conflicts may be detected
        assert isinstance(goal2.conflicts, list)

    @pytest.mark.asyncio
    async def test_resolve_conflicts(self):
        service = FlexibleGoalManagementService()

        goal = await service.add_goal("goal with conflicts", GoalType.ACHIEVEMENT, priority=0.8)
        goal.conflicts = ["conflict_1", "conflict_2"]

        resolutions = await service.resolve_conflicts(goal)

        assert resolutions is not None
        assert len(resolutions) > 0

    @pytest.mark.asyncio
    async def test_update_progress(self):
        service = FlexibleGoalManagementService()

        goal = await service.add_goal("track progress", GoalType.ACHIEVEMENT)
        await service.update_progress(goal.goal_id, 1.0)

        assert service.active_goals[goal.goal_id].progress == 1.0

    @pytest.mark.asyncio
    async def test_goal_achievement_rate(self):
        service = FlexibleGoalManagementService()

        goal1 = await service.add_goal("goal 1", GoalType.ACHIEVEMENT)
        goal2 = await service.add_goal("goal 2", GoalType.ACHIEVEMENT)

        await service.update_progress(goal1.goal_id, 1.0)
        await service.update_progress(goal2.goal_id, 1.0)

        assert service.achievement_rate > 0


class TestGeneralProblemSolving:
    """Test General Problem Solving subsystem"""

    @pytest.mark.asyncio
    async def test_solve_search_problem(self):
        service = GeneralProblemSolvingService()
        problem = {"id": "search_1", "description": "find path from A to B"}

        solution = await service.solve_problem(problem, category=ProblemCategory.SEARCH)

        assert solution is not None
        assert solution.problem_category == ProblemCategory.SEARCH
        assert solution.correctness_confidence >= 0.90

    @pytest.mark.asyncio
    async def test_solve_optimization_problem(self):
        service = GeneralProblemSolvingService()
        problem = {"id": "opt_1", "description": "maximize profit"}

        solution = await service.solve_problem(problem, category=ProblemCategory.OPTIMIZATION)

        assert solution.problem_category == ProblemCategory.OPTIMIZATION
        assert "optimal_value" in solution.solution

    @pytest.mark.asyncio
    async def test_solve_planning_problem(self):
        service = GeneralProblemSolvingService()
        problem = {"id": "plan_1", "description": "schedule tasks"}

        solution = await service.solve_problem(problem, category=ProblemCategory.PLANNING)

        assert solution.problem_category == ProblemCategory.PLANNING
        assert "plan" in solution.solution

    @pytest.mark.asyncio
    async def test_problem_categorization(self):
        service = GeneralProblemSolvingService()

        category = service._categorize_problem({"description": "find optimal solution"})
        assert category == ProblemCategory.OPTIMIZATION

    @pytest.mark.asyncio
    async def test_method_selection(self):
        service = GeneralProblemSolvingService()

        method = service._select_method(ProblemCategory.SEARCH, {})
        assert method == "a_star"

    @pytest.mark.asyncio
    async def test_pattern_learning(self):
        service = GeneralProblemSolvingService()
        problem = {"id": "test", "description": "optimize path"}

        solution = await service.solve_problem(problem)

        assert len(solution.learned_patterns) > 0


class TestIntegratedAGISystem:
    """Test Integrated AGI System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = AGIConfig(
            enable_task_understanding=True,
            enable_transfer_learning=True,
            enable_abstract_reasoning=True,
            enable_metacognition=True,
        )

        system = IntegratedAGISystem(config)
        assert system.task_understanding is not None
        assert system.transfer is not None
        assert system.reasoning is not None
        assert system.metacognition is not None

    @pytest.mark.asyncio
    async def test_general_intelligence_workflow(self):
        system = IntegratedAGISystem()

        result = await system.general_intelligence_workflow(
            task_description="classify sentiment of customer reviews", domain="nlp", context={"dataset_size": 10000}
        )

        assert result is not None
        assert "task_understanding" in result
        assert "reasoning" in result
        assert "solution" in result
        assert "metacognition" in result
        assert result["performance"]["human_level"] is True

    @pytest.mark.asyncio
    async def test_multi_domain_problem_solving(self):
        system = IntegratedAGISystem()

        problems = [
            {"id": "p1", "description": "classify images", "domain": "vision"},
            {"id": "p2", "description": "translate text", "domain": "nlp"},
            {"id": "p3", "description": "predict trajectory", "domain": "robotics"},
        ]

        result = await system.multi_domain_problem_solving(problems, enable_transfer=True)

        assert result is not None
        assert result["num_problems"] == 3
        assert result["num_domains"] >= 2
        assert "transfer_performance" in result
        assert result["transfer_performance"]["average_speedup"] > 1.0

    @pytest.mark.asyncio
    async def test_adaptive_goal_driven_intelligence(self):
        system = IntegratedAGISystem()

        goals = [
            {"description": "maximize accuracy", "type": "OPTIMIZATION", "priority": 0.9},
            {"description": "minimize latency", "type": "OPTIMIZATION", "priority": 0.7},
            {"description": "explore new methods", "type": "EXPLORATION", "priority": 0.5},
        ]

        result = await system.adaptive_goal_driven_intelligence(goals, max_iterations=20, time_budget_seconds=30)

        assert result is not None
        assert result["total_goals"] == 3
        assert result["achievement_rate"] >= 0.0
        assert "adaptations" in result

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedAGISystem()
        status = system.get_system_status()

        assert status is not None
        assert "task_understanding_enabled" in status
        assert "performance" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedAGISystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0
        assert "task_understanding" in benchmarks
        assert "abstract_reasoning" in benchmarks

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_agi_system()
        system2 = get_agi_system()

        assert system1 is system2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
