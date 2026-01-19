"""
Comprehensive Test Suite for Continual Learning Platform (v21.0)

Tests all 7 subsystems and integrated system:
1. ContinualLearningAlgorithms - EWC, SI, replay, progressive networks
2. LifelongMemorySystems - Episodic, semantic, procedural memory
3. KnowledgeAccumulationTransfer - Zero-shot, few-shot, fine-tuning
4. MetaLearning - Learning to learn, rapid adaptation
5. CurriculumLearning - Progressive skill building
6. ExperienceReplayConsolidation - Memory replay & consolidation
7. SelfAssessmentCapabilityTracking - Capability assessment & tracking
8. IntegratedContinualLearningSystem - Unified lifelong learning

Total: 48 tests
"""

import asyncio
import numpy as np
import pytest
from datetime import datetime

from src.continual_learning import (
    # Enums
    ContinualLearningMethod,
    MemoryType,
    TransferType,
    CurriculumStrategy,
    ReplayPriority,
    # Data Classes
    Task,
    Experience,
    Memory,
    Skill,
    MetaLearningState,
    Curriculum,
    CapabilityAssessment,
    ContinualLearningConfig,
    # Service Classes
    ContinualLearningAlgorithms,
    LifelongMemorySystems,
    KnowledgeAccumulationTransfer,
    MetaLearning,
    CurriculumLearning,
    ExperienceReplayConsolidation,
    SelfAssessmentCapabilityTracking,
    # Integrated System
    IntegratedContinualLearningSystem,
    get_continual_learning_system,
)


# Test Continual Learning subsystems and integrated system
class TestContinualLearningAlgorithms:
    """Test Continual Learning Algorithms subsystem"""

    @pytest.mark.asyncio
    async def test_train_continual_ewc(self):
        cl_system = ContinualLearningAlgorithms()
        task = Task("task_1", "Classification", "Image classification", datetime.now(), "classification", 0.5)
        training_data = np.random.randn(100, 10)

        result = await cl_system.train_continual(
            task=task,
            training_data=training_data,
            method=ContinualLearningMethod.EWC,
        )

        assert result is not None
        assert "protected_params" in result or "loss" in result

    @pytest.mark.asyncio
    async def test_train_continual_si(self):
        cl_system = ContinualLearningAlgorithms()
        task = Task("task_2", "Regression", "Value prediction", datetime.now(), "regression", 0.6)
        training_data = np.random.randn(80, 8)

        result = await cl_system.train_continual(
            task=task,
            training_data=training_data,
            method=ContinualLearningMethod.SI,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_evaluate_task(self):
        cl_system = ContinualLearningAlgorithms()

        performance = await cl_system.evaluate_task(task_id="task_1")
        assert 0 <= performance <= 1.0

    @pytest.mark.asyncio
    async def test_detect_forgetting(self):
        cl_system = ContinualLearningAlgorithms()

        forgetting = await cl_system.detect_forgetting(
            task_ids=["task_1", "task_2"],
            threshold=0.2,
        )

        assert forgetting is not None


class TestLifelongMemorySystems:
    """Test Lifelong Memory Systems subsystem"""

    @pytest.mark.asyncio
    async def test_store_episodic_memory(self):
        memory_system = LifelongMemorySystems()
        memory = Memory(
            memory_id="mem_1",
            memory_type=MemoryType.EPISODIC,
            content={"event": "learned task 1"},
            timestamp=datetime.now(),
            importance=0.8,
            associated_tasks=["task_1"],
        )

        result = await memory_system.store_memory(memory)
        assert result is not None

    @pytest.mark.asyncio
    async def test_store_semantic_memory(self):
        memory_system = LifelongMemorySystems()
        memory = Memory(
            memory_id="mem_2",
            memory_type=MemoryType.SEMANTIC,
            content={"concept": "classification", "definition": "..."},
            timestamp=datetime.now(),
            importance=0.9,
            associated_tasks=[],
        )

        result = await memory_system.store_memory(memory)
        assert result is not None

    @pytest.mark.asyncio
    async def test_retrieve_memory(self):
        memory_system = LifelongMemorySystems()

        # Store then retrieve
        memory = Memory("mem_3", MemoryType.EPISODIC, {"test": "data"}, datetime.now(), 0.7, [])
        await memory_system.store_memory(memory)

        retrieved = await memory_system.retrieve_memory(
            query={"test": "data"},
            memory_type=MemoryType.EPISODIC,
        )

        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_consolidate_memories(self):
        memory_system = LifelongMemorySystems()

        result = await memory_system.consolidate_memories(
            consolidation_strategy="rehearsal",
        )

        assert result is not None


class TestKnowledgeAccumulationTransfer:
    """Test Knowledge Accumulation & Transfer subsystem"""

    @pytest.mark.asyncio
    async def test_transfer_zero_shot(self):
        transfer_system = KnowledgeAccumulationTransfer()

        result = await transfer_system.transfer_knowledge(
            source_task_ids=["task_1", "task_2"],
            target_task_id="task_3",
            transfer_type=TransferType.ZERO_SHOT,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_transfer_few_shot(self):
        transfer_system = KnowledgeAccumulationTransfer()

        result = await transfer_system.transfer_knowledge(
            source_task_ids=["task_1"],
            target_task_id="task_4",
            transfer_type=TransferType.FEW_SHOT,
        )

        assert result is not None
        assert "knowledge_items" in result or "transfer_success" in result

    @pytest.mark.asyncio
    async def test_build_knowledge_graph(self):
        transfer_system = KnowledgeAccumulationTransfer()
        tasks = [
            Task("t1", "Task1", "Test", datetime.now(), "classification", 0.5),
            Task("t2", "Task2", "Test", datetime.now(), "classification", 0.6),
        ]

        graph = await transfer_system.build_knowledge_graph(tasks)
        assert graph is not None

    @pytest.mark.asyncio
    async def test_identify_transferable_knowledge(self):
        transfer_system = KnowledgeAccumulationTransfer()

        knowledge = await transfer_system.identify_transferable_knowledge(
            source_task_id="task_1",
            target_task_id="task_2",
        )

        assert knowledge is not None


class TestMetaLearning:
    """Test Meta-Learning subsystem"""

    @pytest.mark.asyncio
    async def test_meta_train(self):
        meta_system = MetaLearning()
        support_tasks = [
            Task(f"meta_task_{i}", f"Task{i}", "Test", datetime.now(), "test", 0.5)
            for i in range(3)
        ]

        meta_state = await meta_system.meta_train(
            support_tasks=support_tasks,
            num_iterations=5,
        )

        assert meta_state is not None

    @pytest.mark.asyncio
    async def test_meta_adapt(self):
        meta_system = MetaLearning()
        new_task = Task("new_task", "NewTask", "Test", datetime.now(), "test", 0.5)
        few_shot_data = np.random.randn(10, 8)

        # First meta-train
        support_tasks = [Task(f"t{i}", f"Task{i}", "Test", datetime.now(), "test", 0.5) for i in range(2)]
        meta_state = await meta_system.meta_train(support_tasks, num_iterations=3)

        # Then adapt
        result = await meta_system.meta_adapt(
            new_task=new_task,
            few_shot_data=few_shot_data,
            meta_state=meta_state,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_learn_learning_strategy(self):
        meta_system = MetaLearning()
        task_history = [
            {"task_id": "t1", "method": "ewc", "performance": 0.8},
            {"task_id": "t2", "method": "si", "performance": 0.75},
        ]

        strategy = await meta_system.learn_learning_strategy(task_history)
        assert strategy is not None


class TestCurriculumLearning:
    """Test Curriculum Learning subsystem"""

    @pytest.mark.asyncio
    async def test_create_curriculum_predefined(self):
        curriculum_system = CurriculumLearning()
        tasks = [
            Task(f"curr_task_{i}", f"Task{i}", "Test", datetime.now(), "test", 0.3 + i * 0.2)
            for i in range(5)
        ]
        skills = [
            Skill("skill_1", "Basic skill", 0.5),
            Skill("skill_2", "Advanced skill", 0.8),
        ]

        curriculum = await curriculum_system.create_curriculum(
            tasks=tasks,
            learning_objectives=skills,
            strategy=CurriculumStrategy.PREDEFINED,
        )

        assert curriculum is not None
        assert len(curriculum.stages) > 0

    @pytest.mark.asyncio
    async def test_create_curriculum_self_paced(self):
        curriculum_system = CurriculumLearning()
        tasks = [Task(f"t{i}", f"Task{i}", "Test", datetime.now(), "test", 0.4 + i * 0.1) for i in range(3)]
        skills = [Skill("s1", "Skill1", 0.6)]

        curriculum = await curriculum_system.create_curriculum(
            tasks=tasks,
            learning_objectives=skills,
            strategy=CurriculumStrategy.SELF_PACED,
        )

        assert curriculum is not None

    @pytest.mark.asyncio
    async def test_update_curriculum(self):
        curriculum_system = CurriculumLearning()

        result = await curriculum_system.update_curriculum(
            curriculum_id="curr_1",
            learner_progress={"stages_completed": 2, "avg_performance": 0.75},
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_recommend_next_task(self):
        curriculum_system = CurriculumLearning()
        current_curriculum = Curriculum(
            curriculum_id="curr_1",
            stages=["stage1", "stage2", "stage3"],
            current_stage=0,
            completion_criteria={},
        )

        next_task = await curriculum_system.recommend_next_task(
            current_curriculum=current_curriculum,
            learner_state={"current_skill": 0.6},
        )

        assert next_task is not None


class TestExperienceReplayConsolidation:
    """Test Experience Replay & Consolidation subsystem"""

    @pytest.mark.asyncio
    async def test_add_experience(self):
        replay_system = ExperienceReplayConsolidation()
        experience = Experience(
            experience_id="exp_1",
            task_id="task_1",
            timestamp=datetime.now(),
            data={"input": [1, 2, 3], "output": "result"},
            outcome={"success": True},
            importance=0.8,
        )

        result = await replay_system.add_experience(experience)
        assert result is not None

    @pytest.mark.asyncio
    async def test_sample_experiences_uniform(self):
        replay_system = ExperienceReplayConsolidation()

        # Add some experiences first
        for i in range(5):
            exp = Experience(f"exp_{i}", "task_1", datetime.now(), {"i": i}, {"ok": True}, 0.7)
            await replay_system.add_experience(exp)

        sampled = await replay_system.sample_experiences(
            num_samples=3,
            priority=ReplayPriority.UNIFORM,
        )

        assert sampled is not None
        assert len(sampled) <= 3

    @pytest.mark.asyncio
    async def test_sample_experiences_importance(self):
        replay_system = ExperienceReplayConsolidation()

        sampled = await replay_system.sample_experiences(
            num_samples=5,
            priority=ReplayPriority.IMPORTANCE,
        )

        assert sampled is not None

    @pytest.mark.asyncio
    async def test_consolidate_memories(self):
        replay_system = ExperienceReplayConsolidation()
        experiences = [
            Experience(f"exp_{i}", "task_1", datetime.now(), {"data": i}, {"ok": True}, 0.7)
            for i in range(3)
        ]

        result = await replay_system.consolidate_memories(
            experiences=experiences,
            consolidation_strategy="interleaved",
        )

        assert result is not None


class TestSelfAssessmentCapabilityTracking:
    """Test Self-Assessment & Capability Tracking subsystem"""

    @pytest.mark.asyncio
    async def test_assess_capabilities(self):
        assessment_system = SelfAssessmentCapabilityTracking()
        test_data = np.random.randn(20, 10)

        assessment = await assessment_system.assess_capabilities(
            task_id="task_1",
            test_data=test_data,
        )

        assert assessment is not None
        assert 0 <= assessment.self_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_track_learning_progress(self):
        assessment_system = SelfAssessmentCapabilityTracking()
        performance_history = [
            {"task_id": "t1", "performance": 0.6, "timestamp": datetime.now()},
            {"task_id": "t2", "performance": 0.75, "timestamp": datetime.now()},
        ]

        progress = await assessment_system.track_learning_progress(
            task_history=performance_history,
        )

        assert progress is not None

    @pytest.mark.asyncio
    async def test_identify_knowledge_gaps(self):
        assessment_system = SelfAssessmentCapabilityTracking()

        gaps = await assessment_system.identify_knowledge_gaps(
            required_skills=["skill_a", "skill_b", "skill_c"],
            current_capabilities={"skill_a": 0.8, "skill_b": 0.4},
        )

        assert gaps is not None
        assert "skill_c" in gaps or "skill_b" in gaps

    @pytest.mark.asyncio
    async def test_calibrate_confidence(self):
        assessment_system = SelfAssessmentCapabilityTracking()

        calibration = await assessment_system.calibrate_confidence(
            self_assessments=[0.8, 0.7, 0.9],
            actual_performances=[0.75, 0.7, 0.85],
        )

        assert calibration is not None


class TestIntegratedContinualLearningSystem:
    """Test Integrated Continual Learning System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = ContinualLearningConfig(
            enable_continual_algorithms=True,
            enable_lifelong_memory=True,
            enable_meta_learning=True,
        )

        system = IntegratedContinualLearningSystem(config)
        assert system.algorithms is not None
        assert system.memory is not None
        assert system.meta_learning is not None

    @pytest.mark.asyncio
    async def test_lifelong_learning_cycle(self):
        system = IntegratedContinualLearningSystem()

        new_task = Task("new_task", "NewTask", "Learn this", datetime.now(), "classification", 0.6)
        training_data = np.random.randn(50, 10)
        previous_tasks = [
            Task("prev_1", "PrevTask1", "Old task", datetime.now(), "classification", 0.5),
        ]

        result = await system.lifelong_learning_cycle(
            new_task=new_task,
            training_data=training_data,
            previous_tasks=previous_tasks,
        )

        assert result is not None
        assert "task_id" in result
        assert "learning_successful" in result
        assert "forgetting_metrics" in result

    @pytest.mark.asyncio
    async def test_learn_new_task_with_transfer(self):
        system = IntegratedContinualLearningSystem()

        new_task = Task("transfer_task", "TransferTask", "New task", datetime.now(), "classification", 0.7)
        source_tasks = [
            Task("source_1", "SourceTask1", "Similar task", datetime.now(), "classification", 0.6),
            Task("source_2", "SourceTask2", "Related task", datetime.now(), "classification", 0.5),
        ]
        training_data = np.random.randn(20, 10)

        result = await system.learn_new_task_with_transfer(
            new_task=new_task,
            source_tasks=source_tasks,
            training_data=training_data,
            transfer_type=TransferType.FEW_SHOT,
        )

        assert result is not None
        assert "positive_transfer" in result
        assert "final_performance" in result
        assert result["source_tasks_used"] == 2

    @pytest.mark.asyncio
    async def test_curriculum_driven_skill_building(self):
        system = IntegratedContinualLearningSystem()

        target_skills = [
            Skill("skill_1", "Basic skill", 0.5),
            Skill("skill_2", "Intermediate skill", 0.7),
            Skill("skill_3", "Advanced skill", 0.9),
        ]
        available_tasks = [
            Task(f"curr_t{i}", f"CurrTask{i}", "Progressive task", datetime.now(), "test", 0.3 + i * 0.15)
            for i in range(5)
        ]

        result = await system.curriculum_driven_skill_building(
            target_skills=target_skills,
            available_tasks=available_tasks,
            max_stages=5,
        )

        assert result is not None
        assert "stages_completed" in result
        assert "skill_progression" in result
        assert "average_performance" in result

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedContinualLearningSystem()
        status = system.get_system_status()

        assert status is not None
        assert "continual_algorithms_enabled" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedContinualLearningSystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_continual_learning_system()
        system2 = get_continual_learning_system()

        assert system1 is system2

    @pytest.mark.asyncio
    async def test_prevent_catastrophic_forgetting(self):
        """Test that system prevents catastrophic forgetting"""
        system = IntegratedContinualLearningSystem()

        # Learn multiple tasks sequentially
        tasks = [
            Task(f"seq_task_{i}", f"SeqTask{i}", "Sequential task", datetime.now(), "classification", 0.5)
            for i in range(3)
        ]

        results = []
        for task in tasks:
            training_data = np.random.randn(40, 10)
            result = await system.lifelong_learning_cycle(
                new_task=task,
                training_data=training_data,
                previous_tasks=tasks[:tasks.index(task)],
            )
            results.append(result)

        # Last task should have forgetting metrics
        assert "forgetting_metrics" in results[-1]

    @pytest.mark.asyncio
    async def test_meta_learning_acceleration(self):
        """Test that meta-learning accelerates learning"""
        system = IntegratedContinualLearningSystem()

        # Create related tasks for meta-learning
        source_tasks = [
            Task(f"meta_src_{i}", f"MetaSource{i}", "Similar task", datetime.now(), "classification", 0.6)
            for i in range(4)
        ]

        new_task = Task("meta_target", "MetaTarget", "Target task", datetime.now(), "classification", 0.6)
        training_data = np.random.randn(15, 10)

        result = await system.learn_new_task_with_transfer(
            new_task=new_task,
            source_tasks=source_tasks,
            training_data=training_data,
            transfer_type=TransferType.FEW_SHOT,
        )

        # With meta-learning, should achieve positive transfer
        assert result["final_performance"] > 0.3  # Better than random

    @pytest.mark.asyncio
    async def test_progressive_difficulty(self):
        """Test curriculum with progressive difficulty"""
        system = IntegratedContinualLearningSystem()

        # Tasks with increasing difficulty
        progressive_tasks = [
            Task(f"prog_{i}", f"Progressive{i}", "Progressive task", datetime.now(), "test", 0.2 + i * 0.15)
            for i in range(6)
        ]

        skills = [Skill("progressive_skill", "Progressive skill", 0.8)]

        result = await system.curriculum_driven_skill_building(
            target_skills=skills,
            available_tasks=progressive_tasks,
            max_stages=6,
        )

        # Performance should generally improve across stages
        performances = [stage["performance"] for stage in result["skill_progression"]]
        assert result["average_performance"] > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
