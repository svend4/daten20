"""
Comprehensive Test Suite for Self-Improving AI (v23.0) - FUNCTIONAL

Tests the REAL genetic algorithm implementation, not mock code!

Test coverage:
1. GeneticAlgorithm - Real evolutionary optimization
2. SelfImprovingAIEngine - Engine using REAL GA
3. Benchmark functions - Optimization problems
4. Integration tests - Full optimization workflows

Total: 15 functional tests
"""

import pytest
import random
from src.self_improving_ai import (
    # Genetic Algorithm
    GeneticAlgorithm,
    GAConfig,
    GAResult,
    SelectionMethod,
    CrossoverMethod,
    MutationMethod,
    # Engine
    SelfImprovingAIEngine,
    SelfImprovementConfig,
    ImprovementStrategy,
    get_self_improving_ai_engine,
    # Benchmark functions
    sphere_function,
    rastrigin_function,
    rosenbrock_function,
    ackley_function
)


class TestGeneticAlgorithm:
    """Test REAL Genetic Algorithm implementation"""

    def test_ga_initialization(self):
        """Test GA initializes correctly"""
        ga = GeneticAlgorithm(
            fitness_function=sphere_function,
            dimensions=5,
            bounds=(-5.0, 5.0),
            maximize=False
        )

        assert ga.dimensions == 5
        assert ga.bounds == (-5.0, 5.0)
        assert ga.maximize == False
        assert len(ga.population) == 0  # Not initialized yet

    def test_population_initialization(self):
        """Test population initialization"""
        ga = GeneticAlgorithm(
            fitness_function=sphere_function,
            dimensions=10,
            bounds=(-5.0, 5.0),
            config=GAConfig(population_size=20)
        )

        ga.initialize_population()

        assert len(ga.population) == 20
        # All individuals should have correct gene length
        assert all(len(ind.genes) == 10 for ind in ga.population)
        # All genes should be within bounds
        assert all(
            all(-5.0 <= gene <= 5.0 for gene in ind.genes)
            for ind in ga.population
        )
        # All individuals should have fitness evaluated
        assert all(ind.fitness != 0.0 or ind.genes == [0.0]*10 for ind in ga.population)

    def test_real_evolution_sphere(self):
        """FUNCTIONAL: Test REAL evolution on sphere function"""
        ga = GeneticAlgorithm(
            fitness_function=sphere_function,
            dimensions=10,
            bounds=(-5.0, 5.0),
            config=GAConfig(
                population_size=30,
                num_generations=50,
                mutation_rate=0.1,
                crossover_rate=0.8
            ),
            maximize=False
        )

        result = ga.evolve()

        # Verify result structure
        assert isinstance(result, GAResult)
        assert result.generations == 50
        assert len(result.fitness_history) == 50

        # Verify REAL improvement (not random)
        initial_fitness = result.fitness_history[0]
        final_fitness = result.fitness_history[-1]

        assert final_fitness < initial_fitness  # Minimization - should decrease
        improvement = (initial_fitness - final_fitness) / initial_fitness * 100
        assert improvement > 50.0, f"Expected >50% improvement, got {improvement:.1f}%"

        print(f"✅ Sphere: {improvement:.1f}% improvement")

    def test_real_evolution_rastrigin(self):
        """FUNCTIONAL: Test REAL evolution on challenging Rastrigin function"""
        ga = GeneticAlgorithm(
            fitness_function=rastrigin_function,
            dimensions=5,
            bounds=(-5.12, 5.12),
            config=GAConfig(
                population_size=50,
                num_generations=100,
                mutation_rate=0.15,
                crossover_rate=0.9
            ),
            maximize=False
        )

        result = ga.evolve()

        # Rastrigin is multimodal - harder to optimize
        initial_fitness = result.fitness_history[0]
        final_fitness = result.fitness_history[-1]

        improvement = (initial_fitness - final_fitness) / initial_fitness * 100
        assert improvement > 30.0, f"Expected >30% improvement, got {improvement:.1f}%"

        print(f"✅ Rastrigin: {improvement:.1f}% improvement")

    def test_selection_methods(self):
        """Test different selection methods work"""
        for method in [SelectionMethod.TOURNAMENT, SelectionMethod.ROULETTE, SelectionMethod.RANK]:
            ga = GeneticAlgorithm(
                fitness_function=sphere_function,
                dimensions=3,
                bounds=(-1.0, 1.0),
                config=GAConfig(
                    population_size=20,
                    num_generations=20,
                    selection_method=method
                )
            )

            result = ga.evolve()
            assert result.best_fitness >= 0.0  # Sphere function minimum is 0
            print(f"✅ Selection {method.value} works")

    def test_crossover_methods(self):
        """Test different crossover methods work"""
        for method in [CrossoverMethod.SINGLE_POINT, CrossoverMethod.TWO_POINT, CrossoverMethod.UNIFORM]:
            ga = GeneticAlgorithm(
                fitness_function=sphere_function,
                dimensions=5,
                bounds=(-2.0, 2.0),
                config=GAConfig(
                    population_size=15,
                    num_generations=15,
                    crossover_method=method
                )
            )

            result = ga.evolve()
            assert len(result.fitness_history) == 15
            print(f"✅ Crossover {method.value} works")

    def test_diversity_tracking(self):
        """Test population diversity is tracked"""
        ga = GeneticAlgorithm(
            fitness_function=sphere_function,
            dimensions=5,
            bounds=(-3.0, 3.0),
            config=GAConfig(population_size=30, num_generations=50)
        )

        result = ga.evolve()

        # Diversity should be tracked
        assert len(result.diversity_history) == 50
        # Initial diversity should be higher than final (convergence)
        assert result.diversity_history[0] > result.diversity_history[-1]

        print(f"✅ Diversity tracking: {result.diversity_history[0]:.3f} → {result.diversity_history[-1]:.3f}")


class TestSelfImprovingAIEngine:
    """Test FUNCTIONAL Self-Improving AI Engine"""

    def test_engine_initialization(self):
        """Test engine initializes"""
        engine = SelfImprovingAIEngine()

        assert engine.config is not None
        assert engine.improvement_history == []
        assert engine.optimization_runs == []

    def test_optimize_function_sphere(self):
        """FUNCTIONAL: Test optimization using REAL GA"""
        engine = SelfImprovingAIEngine()

        result = engine.optimize_function(
            function="sphere",
            dimensions=5,
            generations=50,
            population_size=30
        )

        # Verify result structure
        assert "function" in result
        assert "dimensions" in result
        assert "improvement_percentage" in result
        assert "best_solution" in result

        # Verify REAL improvement
        assert result["improvement_percentage"] > 80.0
        assert len(result["best_solution"]) == 5

        print(f"✅ Engine optimization: {result['improvement_percentage']:.1f}% improvement")

    def test_analyze_performance(self):
        """Test performance analysis tracks runs"""
        engine = SelfImprovingAIEngine()

        # No runs yet
        analysis = engine.analyze_performance()
        assert analysis["total_runs"] == 0
        assert analysis["status"] == "no_runs_yet"

        # Run optimizations
        engine.optimize_function("sphere", dimensions=3, generations=20)
        engine.optimize_function("rastrigin", dimensions=3, generations=20)

        # Analyze again
        analysis = engine.analyze_performance()
        assert analysis["total_runs"] == 2
        assert analysis["status"] == "functional"
        assert analysis["average_improvement"] > 0.0

        print(f"✅ Performance tracking: {analysis['total_runs']} runs, {analysis['average_improvement']:.1f}% avg")

    def test_propose_improvement(self):
        """Test improvement proposals use GA"""
        engine = SelfImprovingAIEngine()

        # Test hyperparameter tuning proposal
        proposal = engine.propose_improvement(ImprovementStrategy.HYPERPARAMETER_TUNING)

        assert proposal["strategy"] == "hyperparameter_tuning"
        assert proposal["method"] == "genetic_algorithm"
        assert proposal["status"] == "functional"
        assert proposal["expected_gain"] > 0.0

        # Test architecture search proposal
        proposal = engine.propose_improvement(ImprovementStrategy.ARCHITECTURE_SEARCH)

        assert proposal["method"] == "genetic_algorithm"
        assert proposal["status"] == "functional"

        print(f"✅ Proposals use genetic_algorithm method")

    def test_apply_improvement(self):
        """FUNCTIONAL: Test applying improvement runs REAL optimization"""
        engine = SelfImprovingAIEngine()

        result = engine.apply_improvement("test_improvement_1")

        assert result["success"] == True
        assert result["method"] == "genetic_algorithm"
        assert result["status"] == "functional"
        assert result["performance_delta"] > 0.0  # Should show real improvement

        print(f"✅ Apply improvement: {result['performance_delta']:.1%} gain")

    def test_multiple_optimizations_consistency(self):
        """Test multiple optimizations show consistent improvement"""
        engine = SelfImprovingAIEngine()

        results = []
        for _ in range(3):
            r = engine.optimize_function(
                function="sphere",
                dimensions=4,
                generations=30,
                population_size=20
            )
            results.append(r["improvement_percentage"])

        # All should show significant improvement
        assert all(imp > 70.0 for imp in results)

        print(f"✅ Consistency: {[f'{r:.1f}%' for r in results]}")


class TestBenchmarkFunctions:
    """Test benchmark optimization functions"""

    def test_sphere_function(self):
        """Test sphere function computation"""
        # Test zero vector (global minimum)
        assert sphere_function([0.0, 0.0, 0.0]) == 0.0

        # Test non-zero vector
        result = sphere_function([1.0, 1.0, 1.0])
        assert result == 3.0  # 1^2 + 1^2 + 1^2 = 3

    def test_rastrigin_function(self):
        """Test Rastrigin function computation"""
        # Test zero vector (global minimum)
        result = rastrigin_function([0.0, 0.0])
        assert abs(result - 0.0) < 1e-10  # Should be very close to 0

        # Test non-zero vector
        result = rastrigin_function([1.0, 1.0])
        assert result > 0.0  # Should be positive

    def test_rosenbrock_function(self):
        """Test Rosenbrock function computation"""
        # Test optimal point [1, 1, ..., 1]
        result = rosenbrock_function([1.0, 1.0, 1.0])
        assert abs(result - 0.0) < 1e-10  # Should be very close to 0

        # Test non-optimal point
        result = rosenbrock_function([0.0, 0.0])
        assert result > 0.0

    def test_ackley_function(self):
        """Test Ackley function computation"""
        # Test zero vector (global minimum)
        result = ackley_function([0.0, 0.0, 0.0])
        assert abs(result - 0.0) < 1e-10  # Should be very close to 0


class TestIntegration:
    """Integration tests for v23"""

    def test_full_optimization_workflow(self):
        """FUNCTIONAL: Test complete optimization workflow"""
        engine = SelfImprovingAIEngine()

        # Step 1: Optimize a function
        opt_result = engine.optimize_function(
            function="rastrigin",
            dimensions=5,
            generations=50,
            population_size=30
        )

        assert opt_result["improvement_percentage"] > 30.0

        # Step 2: Analyze performance
        analysis = engine.analyze_performance()
        assert analysis["total_runs"] == 1

        # Step 3: Propose improvement
        proposal = engine.propose_improvement(ImprovementStrategy.HYPERPARAMETER_TUNING)
        assert proposal["method"] == "genetic_algorithm"

        # Step 4: Apply improvement
        apply_result = engine.apply_improvement("test")
        assert apply_result["success"] == True

        # Step 5: Check final state
        final_analysis = engine.analyze_performance()
        assert final_analysis["total_runs"] == 2  # 1 optimize + 1 apply

        print(f"✅ Full workflow: {final_analysis['average_improvement']:.1f}% avg improvement")

    def test_singleton_accessor(self):
        """Test singleton engine accessor"""
        engine1 = get_self_improving_ai_engine()
        engine2 = get_self_improving_ai_engine()

        assert engine1 is engine2

        print(f"✅ Singleton works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
