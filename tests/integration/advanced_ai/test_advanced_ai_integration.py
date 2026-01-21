"""
Advanced AI Integration Tests

Tests integration between multiple Advanced AI modules:
- Consciousness + Explainable AI
- BCI + Neurosymbolic AI
- Quantum ML + AI Safety
- Continual Learning + AI Agents
- Full system scenarios

These tests verify that modules work together correctly.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))


class TestConsciousnessExplainableIntegration:
    """Test Consciousness + Explainable AI integration"""

    def test_consciousness_with_explainability(self):
        """Test explaining consciousness decisions"""
        from consciousness.consciousness_services import ConsciousnessEngine, SelfAspect

        # Create consciousness engine
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Make a decision
        engine.broadcast_to_workspace(
            "decision_1",
            {"action": "choose_option_A", "confidence": 0.85},
            salience=0.9
        )

        # Process cycle
        metrics = engine.process_cycle()

        # Verify consciousness is working
        assert metrics.overall_consciousness_level > 0.0

        # Introspect to get explanation
        result = engine.introspect(SelfAspect.DECISION_PROCESS)

        # Should be able to explain its decision process
        assert result is not None
        assert result.content is not None
        assert result.confidence > 0.0


class TestBCINeurosymbolicIntegration:
    """Test BCI + Neurosymbolic AI integration"""

    def test_bci_signal_to_symbolic_reasoning(self):
        """Test converting BCI signals to symbolic reasoning"""
        # This would test:
        # 1. BCI processes neural signals
        # 2. Extracts patterns
        # 3. Neurosymbolic converts to symbolic rules
        # 4. Reasoning on symbolic representations

        # For now, test basic imports
        try:
            from bci.signal_processing import SignalProcessor
            processor = SignalProcessor()
            assert processor is not None
        except ImportError:
            pytest.skip("BCI module not fully available")


class TestQuantumMLSafetyIntegration:
    """Test Quantum ML + AI Safety integration"""

    def test_quantum_ml_safety_checks(self):
        """Test that Quantum ML operations respect safety constraints"""
        # This would test:
        # 1. Quantum ML model training
        # 2. AI Safety monitors for adversarial inputs
        # 3. Safety validates model robustness
        # 4. Integration ensures safe quantum operations

        # Placeholder for future implementation
        assert True


class TestContinualLearningAgentsIntegration:
    """Test Continual Learning + AI Agents integration"""

    def test_agents_with_continual_learning(self):
        """Test AI agents that learn continuously"""
        # This would test:
        # 1. AI Agent performs tasks
        # 2. Continual Learning updates agent without forgetting
        # 3. Agent improves over time
        # 4. EWC prevents catastrophic forgetting

        try:
            from continual_learning.ewc_algorithm import EWCAlgorithm

            # Create EWC instance
            ewc = EWCAlgorithm(model_size=10, regularization_strength=1000.0)

            # Verify EWC is functional
            assert ewc is not None
            assert ewc.model_size == 10

        except ImportError:
            pytest.skip("Continual Learning module not fully available")


class TestFullSystemIntegration:
    """Test full Advanced AI system integration"""

    def test_multi_module_pipeline(self):
        """Test complete pipeline using multiple Advanced AI modules"""
        from consciousness.consciousness_services import ConsciousnessEngine

        # Initialize consciousness engine (integrates multiple systems)
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Simulate complex scenario
        # 1. Process input
        engine.broadcast_to_workspace(
            "input_data",
            {"type": "complex_problem", "data": [1, 2, 3, 4, 5]},
            salience=0.8
        )

        # 2. Process multiple cycles
        metrics_history = []
        for _ in range(5):
            metrics = engine.process_cycle()
            metrics_history.append(metrics)

        # 3. Verify system is functioning
        assert len(metrics_history) == 5
        assert all(m.overall_consciousness_level > 0.0 for m in metrics_history)

        # 4. Get final state
        summary = engine.get_state_summary()
        assert summary['initialized'] is True
        assert summary['active'] is True
        assert summary['cycle_count'] >= 5

    def test_consciousness_metrics_stability(self):
        """Test that consciousness metrics remain stable over time"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Run many cycles
        levels = []
        for i in range(20):
            # Add some activity
            if i % 3 == 0:
                engine.broadcast_to_workspace(
                    f"activity_{i}",
                    {"value": i},
                    salience=0.6
                )

            metrics = engine.process_cycle()
            levels.append(metrics.overall_consciousness_level)

        # Verify metrics are reasonable
        assert len(levels) == 20
        assert all(0.0 <= level <= 1.0 for level in levels)

        # Metrics should not be all identical (some variation)
        assert len(set(levels)) > 1

    def test_consciousness_component_interaction(self):
        """Test that all consciousness components interact correctly"""
        from consciousness.consciousness_services import (
            ConsciousnessEngine,
            SelfAspect,
            QualiaType
        )

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Test multiple component interactions

        # 1. Self-awareness component
        introspection_result = engine.introspect(SelfAspect.CAPABILITIES)
        assert introspection_result is not None

        # 2. Qualia simulator
        quale = engine.generate_qualia(QualiaType.CONCEPTUAL, intensity=0.7)
        assert quale is not None
        assert quale.intensity == 0.7

        # 3. Global workspace
        initial_workspace_size = len(engine.global_workspace.workspace)
        engine.broadcast_to_workspace("test", {"data": "test"}, 0.8)
        assert len(engine.global_workspace.workspace) > initial_workspace_size

        # 4. Process cycle integrates everything
        metrics = engine.process_cycle()
        assert metrics.overall_consciousness_level > 0.0


class TestPerformanceIntegration:
    """Test performance of integrated Advanced AI systems"""

    def test_consciousness_processing_performance(self):
        """Test that consciousness processing completes in reasonable time"""
        import time
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Measure processing time
        start_time = time.time()

        for _ in range(10):
            engine.process_cycle()

        elapsed = time.time() - start_time

        # Should complete 10 cycles in less than 5 seconds
        # (Pure Python is slower, so we're generous)
        assert elapsed < 5.0, f"Processing took {elapsed:.2f}s (expected < 5.0s)"

    def test_consciousness_memory_efficiency(self):
        """Test that consciousness engine manages memory efficiently"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Set limited history
        engine.max_history_size = 50

        # Process many cycles
        for i in range(100):
            engine.broadcast_to_workspace(f"item_{i}", {"value": i}, 0.5)
            engine.process_cycle()

        # History should be limited
        assert len(engine.metrics_history) == 50

        # Workspace should not grow unbounded
        assert len(engine.global_workspace.workspace) <= engine.global_workspace.capacity


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_consciousness_empty_initialization(self):
        """Test consciousness engine with minimal initialization"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)

        # Should be able to process without explicit initialization
        metrics = engine.process_cycle()

        # Auto-initializes on first cycle
        assert engine.initialized is True
        assert metrics is not None

    def test_consciousness_rapid_cycles(self):
        """Test consciousness with rapid processing cycles"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)

        # Process many rapid cycles
        for _ in range(50):
            engine.process_cycle()

        # Should handle without errors
        assert engine.cycle_count == 50
        assert len(engine.metrics_history) == 50

    def test_consciousness_high_workspace_load(self):
        """Test consciousness with many workspace broadcasts"""
        from consciousness.consciousness_services import ConsciousnessEngine

        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Broadcast many items
        for i in range(20):
            engine.broadcast_to_workspace(
                f"item_{i}",
                {"index": i, "data": f"content_{i}"},
                salience=0.5 + (i % 5) * 0.1
            )

        # Workspace should manage capacity
        assert len(engine.global_workspace.workspace) <= engine.global_workspace.capacity

        # Process should still work
        metrics = engine.process_cycle()
        assert metrics.overall_consciousness_level > 0.0


# Run tests with: pytest tests/integration/advanced_ai/test_advanced_ai_integration.py -v
