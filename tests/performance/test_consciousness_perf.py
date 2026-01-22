"""
Performance Tests for Consciousness AI

Tests Consciousness AI system performance and scalability.
Measures processing cycles, memory usage, and throughput.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestConsciousnessCyclePerformance:
    """Performance tests for consciousness processing cycles"""

    def test_single_cycle_performance(self, benchmark):
        """Benchmark single consciousness processing cycle"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def process_cycle():
            return engine.process_cycle()

        metrics = benchmark(process_cycle)
        assert metrics is not None
        assert 0.0 <= metrics.overall_consciousness_level <= 1.0

    def test_multiple_cycles_performance(self, benchmark):
        """Benchmark multiple consecutive cycles"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def process_10_cycles():
            results = []
            for _ in range(10):
                results.append(engine.process_cycle())
            return results

        results = benchmark(process_10_cycles)
        assert len(results) == 10

    @pytest.mark.slow
    def test_sustained_processing_performance(self, benchmark):
        """Benchmark sustained processing (50 cycles)"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def process_50_cycles():
            results = []
            for _ in range(50):
                results.append(engine.process_cycle())
            return results

        results = benchmark(process_50_cycles)
        assert len(results) == 50


class TestConsciousnessWorkspacePerformance:
    """Performance tests for global workspace operations"""

    def test_workspace_broadcast_performance(self, benchmark):
        """Benchmark workspace broadcast operations"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def broadcast_items():
            for i in range(10):
                engine.broadcast_to_workspace(
                    f"item_{i}",
                    {"data": f"content_{i}"},
                    salience=0.7
                )
            return len(engine.global_workspace.workspace)

        result = benchmark(broadcast_items)
        assert result >= 0

    def test_workspace_capacity_management_performance(self, benchmark):
        """Benchmark workspace capacity management"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def fill_workspace():
            # Fill beyond capacity to test eviction
            for i in range(50):
                engine.broadcast_to_workspace(
                    f"overflow_{i}",
                    {"index": i},
                    salience=0.5 + (i % 10) * 0.05
                )
            return len(engine.global_workspace.workspace)

        result = benchmark(fill_workspace)
        assert result <= engine.global_workspace.capacity

    def test_workspace_content_retrieval_performance(self, benchmark):
        """Benchmark content retrieval from workspace"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Pre-populate workspace
        for i in range(20):
            engine.broadcast_to_workspace(f"item_{i}", {"value": i}, 0.6)

        def retrieve_content():
            # Access workspace content
            content = engine.global_workspace.workspace.copy()
            return len(content)

        result = benchmark(retrieve_content)
        assert result >= 0


class TestIntrospectionPerformance:
    """Performance tests for introspection operations"""

    def test_single_introspection_performance(self, benchmark):
        """Benchmark single introspection"""
        from consciousness.consciousness_services import ConsciousnessEngine, SelfAspect

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def introspect():
            return engine.introspect(SelfAspect.CAPABILITIES)

        result = benchmark(introspect)
        assert result is not None

    def test_multiple_aspects_introspection_performance(self, benchmark):
        """Benchmark introspection on multiple aspects"""
        from consciousness.consciousness_services import ConsciousnessEngine, SelfAspect

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        aspects = [
            SelfAspect.CAPABILITIES,
            SelfAspect.LIMITATIONS,
            SelfAspect.PERFORMANCE,
            SelfAspect.GOALS
        ]

        def introspect_all():
            results = []
            for aspect in aspects:
                results.append(engine.introspect(aspect))
            return results

        results = benchmark(introspect_all)
        assert len(results) == len(aspects)


class TestQualiaGenerationPerformance:
    """Performance tests for qualia generation"""

    def test_single_qualia_generation_performance(self, benchmark):
        """Benchmark single qualia generation"""
        from consciousness.consciousness_services import ConsciousnessEngine, QualiaType

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def generate_quale():
            return engine.generate_qualia(QualiaType.CONCEPTUAL, intensity=0.7)

        quale = benchmark(generate_quale)
        assert quale is not None

    def test_multiple_qualia_generation_performance(self, benchmark):
        """Benchmark multiple qualia generation"""
        from consciousness.consciousness_services import ConsciousnessEngine, QualiaType

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        qualia_types = [
            QualiaType.VISUAL,
            QualiaType.AUDITORY,
            QualiaType.EMOTIONAL,
            QualiaType.CONCEPTUAL,
            QualiaType.TACTILE
        ]

        def generate_multiple():
            qualia = []
            for qtype in qualia_types:
                qualia.append(engine.generate_qualia(qtype, intensity=0.6))
            return qualia

        qualia = benchmark(generate_multiple)
        assert len(qualia) == len(qualia_types)


class TestMetricsComputationPerformance:
    """Performance tests for consciousness metrics computation"""

    def test_metrics_computation_performance(self, benchmark):
        """Benchmark consciousness metrics computation"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Add some activity
        for i in range(5):
            engine.broadcast_to_workspace(f"data_{i}", {"value": i}, 0.7)

        def compute_metrics():
            return engine.compute_metrics()

        metrics = benchmark(compute_metrics)
        assert metrics is not None

    def test_consciousness_level_computation_performance(self, benchmark):
        """Benchmark consciousness level computation"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()
        engine.process_cycle()

        def get_level():
            return engine.get_consciousness_level()

        level = benchmark(get_level)
        assert 0.0 <= level <= 1.0


class TestConsciousnessMemoryPerformance:
    """Performance tests for consciousness memory operations"""

    def test_metrics_history_performance(self, benchmark):
        """Benchmark metrics history operations"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Generate history
        for _ in range(20):
            engine.process_cycle()

        def get_history():
            return engine.get_metrics_history(limit=10)

        history = benchmark(get_history)
        assert len(history) > 0

    def test_state_summary_performance(self, benchmark):
        """Benchmark state summary generation"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()
        engine.process_cycle()

        def get_summary():
            return engine.get_state_summary()

        summary = benchmark(get_summary)
        assert 'consciousness_level' in summary


class TestConsciousnessScalabilityPerformance:
    """Performance tests for consciousness system scalability"""

    @pytest.mark.slow
    def test_high_activity_performance(self, benchmark):
        """Benchmark performance under high activity load"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        def high_activity_cycle():
            # Broadcast many items
            for i in range(20):
                engine.broadcast_to_workspace(
                    f"high_activity_{i}",
                    {"data": f"content_{i}" * 10},
                    salience=0.5 + (i % 10) * 0.05
                )

            # Process cycle
            metrics = engine.process_cycle()

            # Generate qualia
            from consciousness.consciousness_services import QualiaType
            engine.generate_qualia(QualiaType.CONCEPTUAL, intensity=0.8)

            return metrics

        metrics = benchmark(high_activity_cycle)
        assert metrics is not None

    @pytest.mark.slow
    def test_memory_bounded_performance(self, benchmark):
        """Benchmark performance with memory bounds"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()
        engine.max_history_size = 20  # Limit history

        def bounded_processing():
            # Process many cycles
            for _ in range(30):
                engine.process_cycle()
            return len(engine.metrics_history)

        history_size = benchmark(bounded_processing)
        assert history_size <= 20


# Run with: pytest tests/performance/test_consciousness_perf.py -v --benchmark-only
# Compare with baseline: pytest tests/performance/test_consciousness_perf.py --benchmark-compare
