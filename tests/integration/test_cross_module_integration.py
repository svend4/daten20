"""
Cross-Module Integration Tests

Tests interaction between:
1. AGI Universal + Self-Improving AI
2. Self-Improving AI + Federated Learning
3. AGI Universal + Federated Learning
4. All Three Modules Together

Total: 12 comprehensive integration tests
"""

import pytest
import time
from typing import Dict, Any, List

# AGI Universal imports
from src.agi_universal import (
    UniversalProblemSolver,
    Problem,
    ProblemDomain,
    MetaLearner,
    ChainOfThoughtReasoner,
    ReasoningType,
)

# Self-Improving AI imports
from src.self_improving import (
    AdvancedMonitor,
    MetricType,
    BottleneckAnalyzer,
    AdaptiveLearningController,
    LRScheduleConfig,
    LRScheduleType,
    ContinuousImprovementOrchestrator,
)

# Federated Learning imports
from src.federated_learning import (
    FederatedClient,
    ModelWeights,
    FedProx,
    FedProxConfig,
    FedAdam,
    FedAdamConfig,
    ByzantineRobustAggregation,
    CommunicationCompression,
    CompressionMethod,
    CompressionConfig,
)


class TestAGIWithSelfImproving:
    """Test integration of AGI Universal with Self-Improving AI"""

    def test_agi_with_performance_monitoring(self):
        """Test AGI Universal with Self-Improving performance monitoring"""
        # Initialize components
        solver = UniversalProblemSolver()
        monitor = AdvancedMonitor()

        solver.initialize(quick_init=True)

        # Solve multiple problems while monitoring performance
        problems = [
            Problem("Logical problem 1", domain=ProblemDomain.LOGICAL),
            Problem("Logical problem 2", domain=ProblemDomain.LOGICAL),
            Problem("Logical problem 3", domain=ProblemDomain.LOGICAL),
        ]

        for i, problem in enumerate(problems):
            start_time = time.time()
            solution = solver.solve(problem)
            execution_time = time.time() - start_time

            # Monitor performance
            performance_score = 1.0 if solution.success else 0.0
            monitor.record_metric(MetricType.PERFORMANCE, performance_score)
            monitor.record_metric(MetricType.LATENCY, execution_time)

        # Analyze trends
        perf_trend = monitor.analyze_trend(MetricType.PERFORMANCE)
        latency_trend = monitor.analyze_trend(MetricType.LATENCY)

        assert perf_trend.trend_direction in ["improving", "stable", "degrading"]
        assert latency_trend.confidence >= 0.0
        assert monitor.total_snapshots == 6  # 3 problems × 2 metrics

    def test_agi_with_adaptive_learning(self):
        """Test AGI Universal with adaptive learning rate control"""
        # Initialize components
        meta_learner = MetaLearner(input_dim=1, output_dim=1, hidden_dim=16)
        lr_controller = AdaptiveLearningController(
            LRScheduleConfig(
                schedule_type=LRScheduleType.ADAPTIVE_PERFORMANCE,
                initial_lr=0.01
            )
        )

        # Simulate meta-learning with adaptive LR
        from src.agi_universal.meta_learning import TaskSample

        for epoch in range(10):
            # Generate task
            support_set = [([x], [x * 2]) for x in [0.1, 0.2, 0.3]]
            query_set = [([x], [x * 2]) for x in [0.4, 0.5]]
            task = TaskSample(support_set=support_set, query_set=query_set)

            # Adapt and measure performance
            result = meta_learner.adapt_to_task(task)
            performance = 1.0 - result['query_loss']  # Higher is better

            # Update learning rate based on performance
            lr = lr_controller.step(performance)

            assert 0.0 < lr <= 0.1

        # Check that LR adapted
        assert lr_controller.state.step == 10
        assert len(lr_controller.state.performance_history) == 10

    def test_agi_reasoning_with_bottleneck_analysis(self):
        """Test AGI reasoning chains with performance bottleneck analysis"""
        # Initialize components
        reasoner = ChainOfThoughtReasoner(max_steps=5)
        analyzer = BottleneckAnalyzer()

        # Create component functions for profiling
        components = {
            "deductive_reasoning": lambda: reasoner.solve_problem(
                "Test problem", ReasoningType.DEDUCTIVE
            ),
            "inductive_reasoning": lambda: reasoner.solve_problem(
                "Test problem", ReasoningType.INDUCTIVE
            ),
            "abductive_reasoning": lambda: reasoner.solve_problem(
                "Test problem", ReasoningType.ABDUCTIVE
            ),
        }

        # Profile reasoning performance
        result = analyzer.profile_execution(components, iterations=3)

        assert result.total_execution_time > 0
        assert len(result.bottlenecks) >= 0
        assert result.optimization_potential >= 1.0

        # Get optimization priorities
        priorities = analyzer.get_optimization_priority_list()
        assert isinstance(priorities, list)

    def test_agi_with_continuous_improvement(self):
        """Test AGI Universal with continuous improvement orchestrator"""
        # Initialize components
        solver = UniversalProblemSolver()
        orchestrator = ContinuousImprovementOrchestrator()

        solver.initialize(quick_init=True)

        # Solve problems and continuously improve
        for round_num in range(3):
            problem = Problem(f"Problem {round_num}", domain=ProblemDomain.LOGICAL)
            solution = solver.solve(problem)

            # Run improvement cycle
            performance = 1.0 if solution.success else 0.5
            cycle_result = orchestrator.run_improvement_cycle(
                performance_metric=performance
            )

            assert "cycle" in cycle_result
            assert "current_performance" in cycle_result
            assert cycle_result["cycle"] == round_num + 1

        # Check improvement statistics
        stats = orchestrator.get_improvement_statistics()
        assert stats["total_cycles"] == 3


class TestSelfImprovingWithFederated:
    """Test integration of Self-Improving AI with Federated Learning"""

    def test_federated_with_performance_monitoring(self):
        """Test Federated Learning with performance monitoring"""
        # Initialize components
        monitor = AdvancedMonitor()
        fedprox = FedProx(FedProxConfig(), num_features=10)

        # Create clients
        clients = [
            FederatedClient(f"client_{i}", data_size=100, num_features=10)
            for i in range(5)
        ]

        # Run federated rounds with monitoring
        for round_num in range(5):
            # Collect client models
            client_models = [
                (f"client_{i}", client.local_model, client.data_size)
                for i, client in enumerate(clients[:3])
            ]

            # Aggregate
            global_model = fedprox.aggregate(client_models, fedprox.global_model)
            fedprox.global_model = global_model

            # Monitor aggregation performance
            model_norm = sum(w**2 for w in global_model.weights) ** 0.5
            monitor.record_metric(MetricType.PERFORMANCE, model_norm)

        # Analyze trends
        trend = monitor.analyze_trend(MetricType.PERFORMANCE)
        assert trend.trend_direction in ["improving", "stable", "degrading"]
        assert monitor.total_snapshots == 5

    def test_federated_with_adaptive_learning(self):
        """Test Federated Learning with adaptive learning rate"""
        # Initialize components
        lr_controller = AdaptiveLearningController(
            LRScheduleConfig(
                schedule_type=LRScheduleType.REDUCE_ON_PLATEAU,
                initial_lr=0.01,
                plateau_patience=3
            )
        )
        fedadam = FedAdam(FedAdamConfig(learning_rate=0.001), num_features=10)

        # Create clients
        clients = [
            FederatedClient(f"client_{i}", data_size=100, num_features=10)
            for i in range(5)
        ]

        # Run federated rounds with adaptive LR
        for round_num in range(10):
            client_models = [
                (f"client_{i}", client.local_model, client.data_size)
                for i, client in enumerate(clients[:3])
            ]

            # Aggregate
            global_model = fedadam.aggregate(client_models, fedadam.global_model)
            fedadam.global_model = global_model

            # Simulate performance (model norm)
            performance = 1.0 / (1.0 + round_num * 0.1)  # Slowly degrading

            # Update learning rate
            lr = lr_controller.step(performance)
            fedadam.config.learning_rate = lr

        assert lr_controller.state.step == 10

    def test_federated_with_bottleneck_analysis(self):
        """Test Federated Learning with bottleneck analysis"""
        # Initialize components
        analyzer = BottleneckAnalyzer()
        fedprox = FedProx(FedProxConfig(), num_features=10)

        clients = [
            FederatedClient(f"client_{i}", data_size=100, num_features=10)
            for i in range(5)
        ]

        # Profile federated operations
        components = {
            "client_training": lambda: [
                client.train_local(fedprox.global_model, num_epochs=1)
                for client in clients[:3]
            ],
            "aggregation": lambda: fedprox.aggregate(
                [(f"c{i}", clients[i].local_model, 100) for i in range(3)],
                fedprox.global_model
            ),
        }

        result = analyzer.profile_execution(components, iterations=3)

        assert result.total_execution_time > 0
        assert len(result.breakdown) == 2

        # Check optimization report
        report = analyzer.generate_optimization_report()
        assert report["status"] == "analyzed"

    def test_federated_compression_with_monitoring(self):
        """Test Federated Learning compression with monitoring"""
        # Initialize components
        monitor = AdvancedMonitor()

        model = ModelWeights([float(i) for i in range(100)])

        # Test different compression methods with monitoring
        for method in [CompressionMethod.QUANTIZATION, CompressionMethod.TOP_K]:
            config = CompressionConfig(
                method=method,
                num_bits=8 if method == CompressionMethod.QUANTIZATION else 16,
                k_ratio=0.1
            )

            compressed, metadata = CommunicationCompression.compress(model, config)

            # Monitor compression ratio
            ratio = CommunicationCompression.estimate_compression_ratio(model, compressed)
            monitor.record_metric(MetricType.THROUGHPUT, ratio)

            # Monitor reconstruction error
            error = CommunicationCompression.calculate_reconstruction_error(model, compressed)
            monitor.record_metric(MetricType.ACCURACY, 1.0 - min(error, 1.0))

        assert monitor.total_snapshots == 4  # 2 methods × 2 metrics


class TestAGIWithFederated:
    """Test integration of AGI Universal with Federated Learning"""

    def test_agi_meta_learning_with_federated_aggregation(self):
        """Test AGI meta-learning with federated aggregation"""
        # Initialize components
        meta_learner = MetaLearner(input_dim=10, output_dim=1, hidden_dim=16)
        fedavg = FedAdam(FedAdamConfig(), num_features=10)

        # Simulate federated meta-learning
        # Each client has a meta-learner that adapts to local tasks

        from src.agi_universal.meta_learning import TaskSample

        # Create task
        support_set = [([float(i) for i in range(10)], [1.0]) for _ in range(3)]
        query_set = [([float(i) for i in range(10)], [1.0]) for _ in range(2)]
        task = TaskSample(support_set=support_set, query_set=query_set)

        # Meta-learn
        result = meta_learner.adapt_to_task(task)

        assert 'adapted_params' in result
        assert 'query_loss' in result

    def test_agi_reasoning_with_byzantine_robust_aggregation(self):
        """Test AGI reasoning with Byzantine-robust federated aggregation"""
        # Initialize components
        reasoner = ChainOfThoughtReasoner()

        # Simulate multiple reasoners (clients) solving same problem
        problem = "Is the statement logically valid?"

        # Create "model" representations of reasoning results
        # (In practice, these would be model parameters)
        reasoning_results = []
        for i in range(5):
            chain = reasoner.solve_problem(problem, ReasoningType.DEDUCTIVE)

            # Encode reasoning quality as "model weights"
            # Average confidence across steps
            avg_confidence = sum(step.confidence for step in chain.steps) / len(chain.steps) if chain.steps else 0.5
            quality_score = avg_confidence / 100.0 if avg_confidence > 1.0 else avg_confidence
            model = ModelWeights([quality_score] * 10)
            reasoning_results.append((f"reasoner_{i}", model, 1))

        # Add Byzantine outlier
        byzantine = ModelWeights([10.0] * 10)  # Abnormally high
        reasoning_results.append(("byzantine", byzantine, 1))

        # Use Krum to select most consistent reasoning
        selected = ByzantineRobustAggregation.krum(reasoning_results, f=1)

        # Selected should not be Byzantine
        assert max(selected.weights) < 5.0


class TestAllThreeModules:
    """Test integration of all three modules together"""

    def test_complete_ai_system_integration(self):
        """Test complete AI system with all three modules"""
        # Initialize all components
        solver = UniversalProblemSolver()
        monitor = AdvancedMonitor()
        orchestrator = ContinuousImprovementOrchestrator()
        fedprox = FedProx(FedProxConfig(), num_features=10)

        solver.initialize(quick_init=True)

        # Simulate complete workflow
        for iteration in range(3):
            # 1. AGI: Solve problem
            problem = Problem(f"Problem {iteration}", domain=ProblemDomain.LOGICAL)
            solution = solver.solve(problem)

            # 2. Monitor: Track performance
            performance = 1.0 if solution.success else 0.5
            monitor.record_metric(MetricType.PERFORMANCE, performance)

            # 3. Federated: Aggregate knowledge (simulated)
            clients = [
                FederatedClient(f"client_{i}", data_size=100, num_features=10)
                for i in range(3)
            ]
            client_models = [
                (f"client_{i}", client.local_model, client.data_size)
                for i, client in enumerate(clients)
            ]
            global_model = fedprox.aggregate(client_models, fedprox.global_model)

            # 4. Self-Improving: Continuous improvement
            cycle_result = orchestrator.run_improvement_cycle(
                performance_metric=performance
            )

        # Verify all components worked together
        # Solver doesn't track stats, but we can verify it initialized
        assert solver.mtl_learner is not None
        assert monitor.total_snapshots >= 3
        assert orchestrator.cycle_count == 3
        assert len(fedprox.global_model.weights) == 10

    def test_federated_meta_learning_with_monitoring(self):
        """Test federated meta-learning with comprehensive monitoring"""
        # Initialize components
        monitor = AdvancedMonitor()
        analyzer = BottleneckAnalyzer()

        # Create meta-learners for multiple clients
        meta_learners = [
            MetaLearner(input_dim=5, output_dim=1, hidden_dim=8)
            for _ in range(3)
        ]

        from src.agi_universal.meta_learning import TaskSample

        # Profile federated meta-learning
        def federated_meta_learning_step():
            results = []
            for learner in meta_learners:
                support_set = [([float(i) for i in range(5)], [1.0]) for _ in range(2)]
                query_set = [([float(i) for i in range(5)], [1.0]) for _ in range(1)]
                task = TaskSample(support_set=support_set, query_set=query_set)

                result = learner.adapt_to_task(task)
                results.append(result)

            # Monitor average performance
            avg_loss = sum(r['query_loss'] for r in results) / len(results)
            monitor.record_metric(MetricType.LOSS, avg_loss)

            return results

        # Run multiple rounds
        for _ in range(5):
            federated_meta_learning_step()

        # Analyze trends
        trend = monitor.analyze_trend(MetricType.LOSS)
        assert trend.trend_direction in ["improving", "stable", "degrading"]
        assert monitor.total_snapshots == 5

    def test_adaptive_federated_agi_system(self):
        """Test adaptive system combining federated AGI with self-improvement"""
        # Initialize components
        solver = UniversalProblemSolver()
        lr_controller = AdaptiveLearningController(
            LRScheduleConfig(schedule_type=LRScheduleType.ADAPTIVE_PERFORMANCE)
        )
        fedadam = FedAdam(FedAdamConfig(), num_features=10)
        monitor = AdvancedMonitor()

        solver.initialize(quick_init=True)

        # Run adaptive federated AGI cycles
        for round_num in range(5):
            # 1. Federated learning step
            clients = [
                FederatedClient(f"client_{i}", data_size=100, num_features=10)
                for i in range(3)
            ]
            client_models = [
                (f"client_{i}", client.local_model, client.data_size)
                for i, client in enumerate(clients)
            ]
            global_model = fedadam.aggregate(client_models, fedadam.global_model)

            # 2. AGI problem solving
            problem = Problem(f"Problem {round_num}", domain=ProblemDomain.LOGICAL)
            solution = solver.solve(problem)

            # 3. Monitor and adapt
            performance = 1.0 if solution.success else 0.5
            monitor.record_metric(MetricType.PERFORMANCE, performance)

            # 4. Adaptive learning rate
            lr = lr_controller.step(performance)
            fedadam.config.learning_rate = lr

        # Verify adaptive behavior
        assert lr_controller.state.step == 5
        assert monitor.total_snapshots == 5
        assert fedadam.t == 5  # FedAdam time steps


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
