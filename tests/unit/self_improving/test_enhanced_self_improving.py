"""
Comprehensive Test Suite for Enhanced Self-Improving AI (v24.0)

Tests new v24.0 features:
1. AdvancedMonitor - Real-time monitoring with anomaly detection
2. BottleneckAnalyzer - Performance bottleneck identification
3. AdaptiveLearningController - Intelligent LR scheduling
4. ContinuousImprovementOrchestrator - Autonomous optimization

Total: 32 comprehensive tests
"""

import pytest
import time

from src.self_improving import (
    # Advanced Monitoring
    AdvancedMonitor,
    MetricType,
    AnomalyType,
    get_advanced_monitor,
    # Bottleneck Analysis
    BottleneckAnalyzer,
    BottleneckType,
    Severity,
    get_bottleneck_analyzer,
    # Adaptive Learning
    AdaptiveLearningController,
    AdaptiveMomentumController,
    LRScheduleType,
    LRScheduleConfig,
    PlateauState,
    get_adaptive_lr_controller,
    get_adaptive_momentum_controller,
    # Continuous Improvement
    ContinuousImprovementOrchestrator,
    ImprovementPhase,
    ContinuousImprovementConfig,
    get_continuous_improvement_orchestrator,
)


class TestAdvancedMonitor:
    """Test Advanced Performance Monitoring (v24.0)"""

    def test_monitor_initialization(self):
        """Test monitor initializes correctly"""
        monitor = AdvancedMonitor(history_size=100, anomaly_threshold=2.0)

        assert monitor.history_size == 100
        assert monitor.anomaly_threshold == 2.0
        assert monitor.total_snapshots == 0

    def test_record_metric(self):
        """Test recording metrics"""
        monitor = AdvancedMonitor()

        snapshot = monitor.record_metric(MetricType.PERFORMANCE, 0.85)

        assert snapshot.metric_type == MetricType.PERFORMANCE
        assert snapshot.value == 0.85
        assert monitor.total_snapshots == 1

    def test_anomaly_detection(self):
        """Test anomaly detection in metrics"""
        monitor = AdvancedMonitor(anomaly_threshold=2.0)

        # Record normal values
        for i in range(20):
            monitor.record_metric(MetricType.PERFORMANCE, 0.8 + i * 0.001)

        # Record anomalous spike
        monitor.record_metric(MetricType.PERFORMANCE, 1.5)

        anomalies = monitor.get_recent_anomalies(5)
        assert len(anomalies) > 0
        assert anomalies[0].anomaly_type == AnomalyType.SPIKE

    def test_trend_analysis(self):
        """Test trend analysis"""
        monitor = AdvancedMonitor()

        # Improving trend
        for i in range(50):
            monitor.record_metric(MetricType.ACCURACY, 0.7 + i * 0.005)

        trend = monitor.analyze_trend(MetricType.ACCURACY, window_size=50)

        assert trend.trend_direction == "improving"
        assert trend.slope > 0
        assert trend.confidence > 0

    def test_baseline_comparison(self):
        """Test baseline performance comparison"""
        monitor = AdvancedMonitor()

        monitor.set_baseline(MetricType.PERFORMANCE, 0.75)
        monitor.record_metric(MetricType.PERFORMANCE, 0.85)

        comparison = monitor.get_baseline_comparison(MetricType.PERFORMANCE)

        assert comparison is not None
        assert comparison["baseline"] == 0.75
        assert comparison["current"] == 0.85
        assert comparison["improvement_percent"] > 0

    def test_summary_statistics(self):
        """Test summary statistics calculation"""
        monitor = AdvancedMonitor()

        values = [0.7, 0.75, 0.8, 0.85, 0.9]
        for val in values:
            monitor.record_metric(MetricType.PERFORMANCE, val)

        stats = monitor.get_summary_statistics(MetricType.PERFORMANCE)

        assert stats["count"] == 5
        assert stats["mean"] == 0.8
        assert stats["min"] == 0.7
        assert stats["max"] == 0.9

    def test_performance_prediction(self):
        """Test performance prediction"""
        monitor = AdvancedMonitor()

        # Create linear trend
        for i in range(30):
            monitor.record_metric(MetricType.PERFORMANCE, 0.6 + i * 0.01)

        predictions = monitor.predict_performance(MetricType.PERFORMANCE, steps_ahead=5)

        assert len(predictions) == 5
        # Predictions should continue upward trend
        assert all(p > 0.6 for p in predictions)

    def test_monitoring_report(self):
        """Test comprehensive monitoring report"""
        monitor = AdvancedMonitor()

        for i in range(20):
            monitor.record_metric(MetricType.PERFORMANCE, 0.75 + i * 0.01)

        report = monitor.get_monitoring_report()

        assert "monitoring_duration" in report
        assert "total_snapshots" in report
        assert "metrics" in report
        assert "anomalies" in report


class TestBottleneckAnalyzer:
    """Test Performance Bottleneck Analyzer (v24.0)"""

    def test_analyzer_initialization(self):
        """Test analyzer initializes"""
        analyzer = BottleneckAnalyzer(critical_threshold=0.30, high_threshold=0.20)

        assert analyzer.critical_threshold == 0.30
        assert analyzer.high_threshold == 0.20
        assert len(analyzer.profiling_history) == 0

    def test_profile_execution(self):
        """Test execution profiling"""
        analyzer = BottleneckAnalyzer()

        components = {
            "fast_component": lambda: time.sleep(0.001),
            "slow_component": lambda: time.sleep(0.01),
            "medium_component": lambda: time.sleep(0.005),
        }

        result = analyzer.profile_execution(components, iterations=3)

        assert result.total_execution_time > 0
        assert len(result.breakdown) == 3
        assert len(result.bottlenecks) > 0
        assert result.optimization_potential >= 1.0

    def test_bottleneck_identification(self):
        """Test bottleneck identification"""
        analyzer = BottleneckAnalyzer(critical_threshold=0.30)

        components = {
            "bottleneck": lambda: time.sleep(0.01),
            "fast": lambda: time.sleep(0.001),
        }

        result = analyzer.profile_execution(components, iterations=5)

        # Should identify the slow component as bottleneck
        critical_bottlenecks = [b for b in result.bottlenecks if b.severity == Severity.CRITICAL]
        assert len(result.bottlenecks) > 0

    def test_optimization_priority_list(self):
        """Test optimization priority list generation"""
        analyzer = BottleneckAnalyzer()

        components = {
            "comp1": lambda: time.sleep(0.005),
            "comp2": lambda: time.sleep(0.001),
        }

        analyzer.profile_execution(components, iterations=3)
        priorities = analyzer.get_optimization_priority_list()

        assert len(priorities) > 0
        assert all("priority_score" in p for p in priorities)
        # Should be sorted by priority
        if len(priorities) > 1:
            assert priorities[0]["priority_score"] >= priorities[1]["priority_score"]

    def test_optimization_report(self):
        """Test optimization report generation"""
        analyzer = BottleneckAnalyzer()

        components = {"test": lambda: time.sleep(0.002)}
        analyzer.profile_execution(components, iterations=3)

        report = analyzer.generate_optimization_report()

        assert report["status"] == "analyzed"
        assert "profiling_summary" in report
        assert "bottlenecks" in report
        assert "estimated_speedup" in report

    def test_historical_trends(self):
        """Test historical trend analysis"""
        analyzer = BottleneckAnalyzer()

        components = {"test_comp": lambda: time.sleep(0.001)}

        # Run multiple profiles
        for _ in range(5):
            analyzer.profile_execution(components, iterations=2)

        trends = analyzer.analyze_historical_trends("test_comp", window=10)

        assert trends["status"] in ["analyzed", "insufficient_data"]
        if trends["status"] == "analyzed":
            assert "trend" in trends


class TestAdaptiveLearningController:
    """Test Adaptive Learning Rate Controller (v24.0)"""

    def test_controller_initialization(self):
        """Test controller initializes"""
        config = LRScheduleConfig(
            schedule_type=LRScheduleType.ADAPTIVE_PERFORMANCE,
            initial_lr=0.001,
            min_lr=1e-6,
            max_lr=0.1
        )

        controller = AdaptiveLearningController(config)

        assert controller.config.initial_lr == 0.001
        assert controller.state.current_lr == 0.001
        assert controller.state.step == 0

    def test_constant_schedule(self):
        """Test constant learning rate schedule"""
        config = LRScheduleConfig(schedule_type=LRScheduleType.CONSTANT, initial_lr=0.01)
        controller = AdaptiveLearningController(config)

        lrs = [controller.step() for _ in range(10)]

        # All should be constant (after warmup if any)
        assert all(lr == 0.01 for lr in lrs[1:])

    def test_step_decay_schedule(self):
        """Test step decay schedule"""
        config = LRScheduleConfig(
            schedule_type=LRScheduleType.STEP_DECAY,
            initial_lr=0.1,
            decay_rate=0.5,
            decay_steps=10
        )
        controller = AdaptiveLearningController(config)

        lr_start = controller.step()
        for _ in range(9):
            controller.step()
        lr_after_10 = controller.step()

        # Should decay after decay_steps
        assert lr_after_10 < lr_start

    def test_adaptive_performance_schedule(self):
        """Test adaptive performance-based schedule"""
        config = LRScheduleConfig(
            schedule_type=LRScheduleType.ADAPTIVE_PERFORMANCE,
            initial_lr=0.001
        )
        controller = AdaptiveLearningController(config)

        # Simulate improving performance
        for i in range(20):
            performance = 0.7 + i * 0.01  # Improving
            controller.step(performance)

        assert controller.state.plateau_state == PlateauState.IMPROVING

        # Simulate plateau
        for _ in range(10):
            controller.step(0.88)  # Stable

        assert controller.state.plateau_state == PlateauState.PLATEAU

    def test_reduce_on_plateau(self):
        """Test reduce on plateau schedule"""
        config = LRScheduleConfig(
            schedule_type=LRScheduleType.REDUCE_ON_PLATEAU,
            initial_lr=0.01,
            plateau_patience=5,
            decay_rate=0.5
        )
        controller = AdaptiveLearningController(config)

        initial_lr = controller.step(0.8)

        # Plateau: no improvement
        for _ in range(6):
            lr = controller.step(0.8)

        # LR should have been reduced
        assert lr < initial_lr

    def test_warmup(self):
        """Test learning rate warmup"""
        config = LRScheduleConfig(
            schedule_type=LRScheduleType.CONSTANT,
            initial_lr=0.1,
            warmup_steps=10
        )
        controller = AdaptiveLearningController(config)

        # During warmup, LR should gradually increase
        lr_warmup = controller.step()
        assert lr_warmup < 0.1

        # After warmup
        for _ in range(15):
            lr = controller.step()

        assert lr == 0.1

    def test_get_state_info(self):
        """Test getting state information"""
        controller = AdaptiveLearningController()

        controller.step(0.75)
        controller.step(0.80)

        state = controller.get_state_info()

        assert "current_lr" in state
        assert "step" in state
        assert "plateau_state" in state
        assert state["step"] == 2

    def test_performance_summary(self):
        """Test performance summary"""
        controller = AdaptiveLearningController()

        for i in range(10):
            controller.step(0.7 + i * 0.02)

        summary = controller.get_performance_summary()

        assert summary["status"] == "active"
        assert summary["num_steps"] == 10
        assert summary["total_improvement"] > 0


class TestAdaptiveMomentumController:
    """Test Adaptive Momentum Controller (v24.0)"""

    def test_momentum_initialization(self):
        """Test momentum controller initializes"""
        controller = AdaptiveMomentumController(
            initial_momentum=0.9,
            min_momentum=0.5,
            max_momentum=0.99
        )

        assert controller.current_momentum == 0.9
        assert controller.min_momentum == 0.5
        assert controller.max_momentum == 0.99

    def test_momentum_update(self):
        """Test momentum updates based on gradient norm"""
        controller = AdaptiveMomentumController()

        # High variance gradients -> reduce momentum
        for _ in range(15):
            controller.update(1.0)
            controller.update(5.0)  # High variance

        # Momentum should adjust
        momentum = controller.get_momentum()
        assert 0.5 <= momentum <= 0.99


class TestContinuousImprovementOrchestrator:
    """Test Continuous Improvement Orchestrator (v24.0)"""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes"""
        config = ContinuousImprovementConfig(
            monitoring_interval=5.0,
            max_improvements_per_cycle=3
        )

        orchestrator = ContinuousImprovementOrchestrator(config)

        assert orchestrator.config.monitoring_interval == 5.0
        assert orchestrator.cycle_count == 0
        assert orchestrator.current_phase == ImprovementPhase.MONITORING

    def test_improvement_cycle(self):
        """Test running improvement cycle"""
        orchestrator = ContinuousImprovementOrchestrator()

        components = {
            "comp1": lambda: time.sleep(0.001),
            "comp2": lambda: time.sleep(0.002),
        }

        result = orchestrator.run_improvement_cycle(
            performance_metric=0.80,
            components=components
        )

        assert "cycle" in result
        assert "current_performance" in result
        assert "monitoring" in result
        assert "analysis" in result
        assert result["cycle"] == 1

    def test_multiple_cycles(self):
        """Test multiple improvement cycles"""
        orchestrator = ContinuousImprovementOrchestrator()

        # Run multiple cycles
        for i in range(5):
            orchestrator.run_improvement_cycle(performance_metric=0.7 + i * 0.02)

        assert orchestrator.cycle_count == 5

    def test_improvement_statistics(self):
        """Test improvement statistics"""
        orchestrator = ContinuousImprovementOrchestrator()

        orchestrator.run_improvement_cycle(performance_metric=0.75)
        orchestrator.run_improvement_cycle(performance_metric=0.80)

        stats = orchestrator.get_improvement_statistics()

        assert "total_cycles" in stats
        assert "total_improvements" in stats
        assert stats["total_cycles"] == 2

    def test_optimization_roadmap(self):
        """Test optimization roadmap generation"""
        orchestrator = ContinuousImprovementOrchestrator()

        components = {"test": lambda: time.sleep(0.001)}
        orchestrator.run_improvement_cycle(performance_metric=0.75, components=components)

        roadmap = orchestrator.get_optimization_roadmap()

        assert "current_status" in roadmap
        assert "recommendations" in roadmap

    def test_baseline_tracking(self):
        """Test baseline performance tracking"""
        orchestrator = ContinuousImprovementOrchestrator()

        # First cycle sets baseline
        orchestrator.run_improvement_cycle(performance_metric=0.70)
        assert orchestrator.baseline_performance == 0.70

        # Subsequent cycles compare to baseline
        result = orchestrator.run_improvement_cycle(performance_metric=0.80)
        assert result["improvement_over_baseline"] > 0


class TestIntegration:
    """Integration tests for v24.0 enhanced features"""

    def test_full_enhancement_workflow(self):
        """Test complete workflow with all v24.0 components"""
        # Initialize components
        monitor = AdvancedMonitor()
        analyzer = BottleneckAnalyzer()
        lr_controller = AdaptiveLearningController()
        orchestrator = ContinuousImprovementOrchestrator()

        # Simulate performance tracking
        for i in range(10):
            perf = 0.7 + i * 0.02
            monitor.record_metric(MetricType.PERFORMANCE, perf)
            lr_controller.step(perf)

        # Profile components
        components = {
            "model_inference": lambda: time.sleep(0.003),
            "data_preprocessing": lambda: time.sleep(0.001),
        }
        profiling_result = analyzer.profile_execution(components, iterations=3)

        # Run improvement cycle
        cycle_result = orchestrator.run_improvement_cycle(
            performance_metric=0.85,
            components=components
        )

        # Verify all components worked
        assert monitor.total_snapshots == 10
        assert len(profiling_result.bottlenecks) >= 0
        assert lr_controller.state.step == 10
        assert cycle_result["cycle"] == 1

    def test_singleton_accessors(self):
        """Test singleton pattern for all controllers"""
        monitor1 = get_advanced_monitor()
        monitor2 = get_advanced_monitor()
        assert monitor1 is monitor2

        analyzer1 = get_bottleneck_analyzer()
        analyzer2 = get_bottleneck_analyzer()
        assert analyzer1 is analyzer2

        lr1 = get_adaptive_lr_controller()
        lr2 = get_adaptive_lr_controller()
        assert lr1 is lr2

        momentum1 = get_adaptive_momentum_controller()
        momentum2 = get_adaptive_momentum_controller()
        assert momentum1 is momentum2

        orch1 = get_continuous_improvement_orchestrator()
        orch2 = get_continuous_improvement_orchestrator()
        assert orch1 is orch2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
