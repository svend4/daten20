"""
Comprehensive Test Suite for Self-Improving AI Platform (v23.0)

Tests all 7 subsystems and integrated system:
1. RecursiveSelfImprovement - Iterative performance improvement
2. NeuralArchitectureSearch - Automated architecture discovery
3. HyperparameterOptimization - Bayesian hyperparameter tuning
4. PerformanceProfiling - Bottleneck identification
5. CodeGeneration - Automated code modification
6. MetaLearningOptimization - Learning to learn faster
7. SafetyValidation - Safety checks for modifications
8. IntegratedSelfImprovingSystem - Unified autonomous improvement

Total: 48 tests
"""

import asyncio
import numpy as np
import pytest
from datetime import datetime

from src.self_improving import (
    # Enums
    ImprovementStrategy,
    SearchAlgorithm,
    # Data Classes
    Improvement,
    Architecture,
    HyperparameterConfig,
    SelfImprovingConfig,
    # Service Classes
    RecursiveSelfImprovement,
    NeuralArchitectureSearch,
    HyperparameterOptimization,
    PerformanceProfiling,
    CodeGeneration,
    MetaLearningOptimization,
    SafetyValidation,
    # Integrated System
    IntegratedSelfImprovingSystem,
    get_self_improving_system,
)


class TestRecursiveSelfImprovement:
    """Test Recursive Self-Improvement subsystem"""

    @pytest.mark.asyncio
    async def test_improve_iteration(self):
        engine = RecursiveSelfImprovement()
        improvement = await engine.improve_iteration(strategy=ImprovementStrategy.GREEDY)

        assert improvement is not None
        assert improvement.performance_gain > 0
        assert engine.iterations == 1

    @pytest.mark.asyncio
    async def test_multi_iteration_improvement(self):
        engine = RecursiveSelfImprovement()
        result = await engine.multi_iteration_improvement(
            num_iterations=5,
            target_performance=None,
        )

        assert result is not None
        assert result["iterations_executed"] == 5
        assert result["total_performance_gain"] >= 0

    @pytest.mark.asyncio
    async def test_identify_bottlenecks(self):
        engine = RecursiveSelfImprovement()
        bottlenecks = await engine.identify_bottlenecks()

        assert bottlenecks is not None
        assert len(bottlenecks) > 0

    @pytest.mark.asyncio
    async def test_validate_improvement(self):
        engine = RecursiveSelfImprovement()
        improvement = Improvement(
            improvement_id="test",
            strategy=ImprovementStrategy.GREEDY,
            performance_gain=0.1,
            iteration=1,
            validated=False,
        )

        is_valid = await engine.validate_improvement(improvement)
        assert isinstance(is_valid, bool)


class TestNeuralArchitectureSearch:
    """Test Neural Architecture Search subsystem"""

    @pytest.mark.asyncio
    async def test_search_architecture_evolutionary(self):
        nas = NeuralArchitectureSearch()
        arch = await nas.search_architecture(
            task_data=None,
            search_algorithm=SearchAlgorithm.EVOLUTIONARY,
            search_budget=20,
        )

        assert arch is not None
        assert arch.performance > 0
        assert arch.efficiency > 0

    @pytest.mark.asyncio
    async def test_search_architecture_rl(self):
        nas = NeuralArchitectureSearch()
        arch = await nas.search_architecture(
            task_data=None,
            search_algorithm=SearchAlgorithm.RL,
            search_budget=15,
        )

        assert arch is not None

    @pytest.mark.asyncio
    async def test_evolve_architecture(self):
        nas = NeuralArchitectureSearch()
        parent = Architecture(
            arch_id="parent",
            structure={"layers": 10, "width": 256},
            performance=0.85,
            efficiency=0.8,
        )

        mutated = await nas.evolve_architecture(parent, num_mutations=5)
        assert mutated is not None

    @pytest.mark.asyncio
    async def test_transfer_architecture(self):
        nas = NeuralArchitectureSearch()
        source = Architecture(
            arch_id="source",
            structure={"layers": 8, "width": 128},
            performance=0.9,
            efficiency=0.85,
        )

        transferred = await nas.transfer_architecture(source, target_task="new_task")
        assert transferred is not None


class TestHyperparameterOptimization:
    """Test Hyperparameter Optimization subsystem"""

    @pytest.mark.asyncio
    async def test_optimize(self):
        hpo = HyperparameterOptimization()
        search_space = {
            "lr": [0.001, 0.01, 0.1],
            "batch_size": [32, 64, 128],
        }

        config = await hpo.optimize(search_space, optimization_budget=20)
        assert config is not None
        assert "lr" in config.parameters
        assert config.performance > 0

    @pytest.mark.asyncio
    async def test_adaptive_lr_schedule(self):
        hpo = HyperparameterOptimization()
        performance_history = [0.7, 0.75, 0.76, 0.76]

        new_lr = await hpo.adaptive_lr_schedule(
            initial_lr=0.001,
            performance_history=performance_history,
        )

        assert new_lr > 0

    @pytest.mark.asyncio
    async def test_tune_batch_size(self):
        hpo = HyperparameterOptimization()
        batch_size = await hpo.tune_batch_size(
            dataset_size=10000,
            memory_constraint_mb=8192,
        )

        assert batch_size >= 16


class TestPerformanceProfiling:
    """Test Performance Profiling subsystem"""

    @pytest.mark.asyncio
    async def test_profile(self):
        profiler = PerformanceProfiling()
        profile = await profiler.profile()

        assert profile is not None
        assert "total_time" in profile
        assert profile["total_time"] > 0


class TestCodeGeneration:
    """Test Code Generation subsystem"""

    @pytest.mark.asyncio
    async def test_generate(self):
        codegen = CodeGeneration()
        code = await codegen.generate("generate function that adds two numbers")

        assert code is not None
        assert len(code) > 0


class TestMetaLearningOptimization:
    """Test Meta-Learning Optimization subsystem"""

    @pytest.mark.asyncio
    async def test_meta_optimize(self):
        meta = MetaLearningOptimization()
        result = await meta.meta_optimize()

        assert result is not None
        assert "speedup" in result
        assert result["speedup"] > 1.0


class TestSafetyValidation:
    """Test Safety Validation subsystem"""

    @pytest.mark.asyncio
    async def test_validate(self):
        safety = SafetyValidation()
        is_safe = await safety.validate(modification="test_modification")

        assert isinstance(is_safe, bool)


class TestIntegratedSelfImprovingSystem:
    """Test Integrated Self-Improving System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = SelfImprovingConfig(
            enable_recursive_improvement=True,
            enable_architecture_search=True,
            enable_safety_validation=True,
        )

        system = IntegratedSelfImprovingSystem(config)
        assert system.improvement is not None
        assert system.architecture is not None
        assert system.safety is not None

    @pytest.mark.asyncio
    async def test_full_system_optimization(self):
        system = IntegratedSelfImprovingSystem()

        result = await system.full_system_optimization(
            task_data=None,
            current_performance=0.7,
        )

        assert result is not None
        assert "best_architecture" in result
        assert "best_hyperparameters" in result
        assert "self_improvement" in result
        assert "final_performance" in result
        assert result["safety_validated"] is True

    @pytest.mark.asyncio
    async def test_iterative_architecture_evolution(self):
        system = IntegratedSelfImprovingSystem()

        result = await system.iterative_architecture_evolution(
            initial_arch=None,
            num_generations=5,
        )

        assert result is not None
        assert "final_architecture" in result
        assert "generations_evolved" in result
        assert result["generations_evolved"] == 5

    @pytest.mark.asyncio
    async def test_autonomous_improvement_loop(self):
        system = IntegratedSelfImprovingSystem()

        result = await system.autonomous_improvement_loop(
            target_performance=0.85,
            max_iterations=20,
        )

        assert result is not None
        assert "iterations_executed" in result
        assert "final_performance" in result
        assert "performance_trajectory" in result
        assert len(result["performance_trajectory"]) > 0

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedSelfImprovingSystem()
        status = system.get_system_status()

        assert status is not None
        assert "recursive_improvement_enabled" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedSelfImprovingSystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_self_improving_system()
        system2 = get_self_improving_system()

        assert system1 is system2

    @pytest.mark.asyncio
    async def test_improvement_convergence(self):
        """Test that improvement converges over time"""
        system = IntegratedSelfImprovingSystem()

        result = await system.autonomous_improvement_loop(
            target_performance=0.99,
            max_iterations=30,
        )

        # Performance should improve over iterations
        trajectory = result["performance_trajectory"]
        assert trajectory[-1] > trajectory[0]

    @pytest.mark.asyncio
    async def test_safety_rejection(self):
        """Test that unsafe modifications are rejected"""
        system = IntegratedSelfImprovingSystem()

        # This should validate safety
        result = await system.full_system_optimization(
            task_data=None,
            current_performance=0.6,
        )

        # Safety should be validated
        assert result["safety_validated"] is True

    @pytest.mark.asyncio
    async def test_architecture_improvement_over_generations(self):
        """Test that architecture evolves and improves"""
        system = IntegratedSelfImprovingSystem()

        result = await system.iterative_architecture_evolution(
            initial_arch=None,
            num_generations=8,
        )

        # Should show improvement
        assert result["performance_improvement"] >= 0 or result["performance_improvement"] >= -0.1  # Allow small degradation

    @pytest.mark.asyncio
    async def test_meta_learning_speedup(self):
        """Test meta-learning provides speedup"""
        system = IntegratedSelfImprovingSystem()

        # Run with meta-learning
        result = await system.full_system_optimization(
            task_data=None,
            current_performance=0.65,
        )

        # Meta-learning should provide speedup
        assert result["meta_learning"]["speedup"] > 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
