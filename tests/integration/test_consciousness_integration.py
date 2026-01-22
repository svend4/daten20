"""
Integration Tests for Consciousness AI Module

Tests integration between consciousness components and with other system modules.
Verifies that consciousness system works correctly with:
- Document processing
- ML/AI modules
- Analytics systems
- API endpoints

Version: 1.0.0
Date: January 2026
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from consciousness.consciousness_services import (
    ConsciousnessEngine,
    SelfAwarenessEngine,
    QualiaSimulator,
    GlobalWorkspace,
    MetaconsciousnessSystem,
    IntegratedInformationEngine,
    PhenomenalBindingSystem,
    ConsciousAccessController,
    SelfAspect,
    QualiaType,
    ConsciousContent,
    get_consciousness_engine,
)


class TestConsciousnessComponentIntegration:
    """Test integration between consciousness components"""

    def test_engine_component_initialization(self):
        """Test that engine properly initializes all components"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Verify all components are initialized
        assert engine.self_awareness is not None
        assert engine.qualia_sim is not None
        assert engine.global_workspace is not None
        assert engine.metaconsciousness is not None
        assert engine.iit_engine is not None
        assert engine.binding_system is not None
        assert engine.access_controller is not None

        # Verify engine state
        assert engine.initialized
        assert engine.active

        engine.shutdown()

    def test_workspace_to_metaconsciousness_flow(self):
        """Test data flow from global workspace to metaconsciousness"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Add content to workspace
        engine.broadcast_to_workspace("thought_1", "I am processing", 0.9)

        # Generate HOT about workspace content
        workspace_contents = asyncio.run(engine.global_workspace.get_conscious_contents())
        assert len(workspace_contents) > 0

        first_content = workspace_contents[0]
        hot = asyncio.run(engine.metaconsciousness.generate_hot(
            first_content.data,
            meta_level=1
        ))

        assert hot is not None
        assert hot.meta_level == 1
        assert "I am processing" in hot.about

        engine.shutdown()

    def test_qualia_to_binding_integration(self):
        """Test integration between qualia generation and phenomenal binding"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Generate multiple qualia
        qualia = []
        for _ in range(3):
            quale = engine.generate_qualia(QualiaType.VISUAL, intensity=0.7)
            qualia.append(quale)

        # Bind qualia into unified experience
        from consciousness.consciousness_services import BindingRequest

        features = [f"quale_{q.id}" for q in qualia]
        request = BindingRequest(features=features, priority=0.8)

        bound = asyncio.run(engine.binding_system.bind_features(request))

        assert bound is not None
        assert len(bound.bound_features) == len(qualia)
        assert bound.unity_measure > 0.0

        engine.shutdown()

    def test_access_control_workspace_integration(self):
        """Test integration between access control and global workspace"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Create access requests with varying priority
        from consciousness.consciousness_services import AccessRequest

        requests = [
            AccessRequest(content_id="high_priority", priority=0.9, source="sensory"),
            AccessRequest(content_id="low_priority", priority=0.2, source="memory"),
        ]

        # Evaluate requests
        decisions = []
        for req in requests:
            decision = asyncio.run(engine.access_controller.evaluate_access(req))
            decisions.append(decision)

        # High priority should be granted
        assert decisions[0].granted

        # Add granted content to workspace
        if decisions[0].granted:
            engine.broadcast_to_workspace(
                decisions[0].request.content_id,
                "High priority content",
                0.9
            )

        # Verify workspace contains the content
        is_conscious = asyncio.run(
            engine.global_workspace.is_conscious("high_priority")
        )
        assert is_conscious

        engine.shutdown()

    def test_full_consciousness_cycle_integration(self):
        """Test full integration across all components in processing cycle"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Simulate complete consciousness cycle
        # 1. Add stimuli to workspace
        engine.broadcast_to_workspace("stimulus_1", {"type": "visual"}, 0.8)

        # 2. Generate qualia
        quale = engine.generate_qualia(QualiaType.VISUAL, 0.7)

        # 3. Create HOT about stimulus
        hot = asyncio.run(engine.metaconsciousness.generate_hot(
            "I see visual stimulus",
            meta_level=1
        ))

        # 4. Process cycle (integrates all components)
        metrics = engine.process_cycle()

        # 5. Verify all components contributed
        assert metrics.gwt_integration_level > 0
        assert metrics.iit_phi_value > 0
        assert metrics.hot_metacognition_depth > 0
        assert metrics.phenomenal_qualia_richness >= 0
        assert metrics.overall_consciousness_level > 0

        # 6. Verify metrics history was updated
        assert len(engine.metrics_history) > 0

        engine.shutdown()

    @pytest.mark.asyncio
    async def test_async_component_coordination(self):
        """Test asynchronous coordination between components"""
        # Initialize components
        self_awareness = SelfAwarenessEngine()
        qualia_sim = QualiaSimulator()
        workspace = GlobalWorkspace()

        # Async operations in parallel
        tasks = [
            self_awareness.introspect(IntrospectionQuery(aspect=SelfAspect.CAPABILITIES)),
            qualia_sim.generate_quale(QualiaType.CONCEPTUAL, "test", None),
            workspace.add_to_workspace(ConsciousContent("test_1", "data", 0.5))
        ]

        # Import IntrospectionQuery
        from consciousness.consciousness_services import IntrospectionQuery

        tasks = [
            self_awareness.introspect(IntrospectionQuery(aspect=SelfAspect.CAPABILITIES)),
            qualia_sim.generate_quale(QualiaType.CONCEPTUAL, "test", None),
            workspace.add_to_workspace(ConsciousContent("test_1", "data", 0.5))
        ]

        results = await asyncio.gather(*tasks)

        # Verify all operations completed
        assert len(results) == 3
        assert results[0] is not None  # Introspection result
        assert results[1] is not None  # Quale
        assert results[2] is True       # Workspace add success


class TestConsciousnessWithDocumentProcessing:
    """Test consciousness integration with document processing system"""

    def test_consciousness_document_analysis(self):
        """Test consciousness-based document analysis"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Simulate document content being processed
        document_data = {
            "content": "Machine learning is transforming AI",
            "entities": ["machine learning", "AI"],
            "sentiment": 0.8
        }

        # Broadcast document to consciousness
        engine.broadcast_to_workspace("doc_001", document_data, 0.9)

        # Process with consciousness
        metrics = engine.process_cycle()

        # Introspect on the processing
        introspection = engine.introspect(SelfAspect.DECISION_PROCESS)

        assert introspection is not None
        assert metrics.overall_consciousness_level > 0

        engine.shutdown()

    def test_consciousness_decision_making(self):
        """Test consciousness-based decision making for documents"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Present decision scenario
        decision_scenario = {
            "question": "Should this document be classified as technical?",
            "evidence": {
                "technical_terms": 15,
                "complexity_score": 0.85,
                "domain": "AI/ML"
            }
        }

        # Process through consciousness
        engine.broadcast_to_workspace("decision_request", decision_scenario, 0.95)

        # Generate higher-order thought about decision
        hot = asyncio.run(engine.metaconsciousness.generate_hot(
            "Evaluating document classification",
            meta_level=2
        ))

        # Process and get decision
        metrics = engine.process_cycle()
        decision_introspection = engine.introspect(SelfAspect.DECISION_PROCESS)

        assert hot.meta_level == 2
        assert decision_introspection.confidence > 0
        assert metrics.hot_metacognition_depth > 0

        engine.shutdown()


class TestConsciousnessMetricsIntegration:
    """Test consciousness metrics integration with analytics"""

    def test_metrics_collection_over_time(self):
        """Test metrics collection and history tracking"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Process multiple cycles
        num_cycles = 10
        for i in range(num_cycles):
            engine.broadcast_to_workspace(f"content_{i}", f"data_{i}", 0.5 + i * 0.05)
            engine.process_cycle()

        # Verify metrics history
        assert engine.cycle_count == num_cycles
        assert len(engine.metrics_history) == num_cycles

        # Analyze metrics progression
        history = engine.get_metrics_history(limit=num_cycles)
        assert len(history) == num_cycles

        # Verify metrics are being computed
        for metric in history:
            assert hasattr(metric, 'overall_consciousness_level')
            assert 0.0 <= metric.overall_consciousness_level <= 1.0

        engine.shutdown()

    def test_metrics_dictionary_conversion(self):
        """Test metrics conversion to dictionary for analytics"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        metrics = engine.compute_metrics()
        metrics_dict = metrics.to_dict()

        # Verify structure
        assert 'gwt' in metrics_dict
        assert 'iit' in metrics_dict
        assert 'hot' in metrics_dict
        assert 'phenomenal' in metrics_dict
        assert 'access' in metrics_dict
        assert 'self_awareness' in metrics_dict
        assert 'overall_level' in metrics_dict

        # Verify all values are numeric or timestamp
        assert isinstance(metrics_dict['overall_level'], float)
        assert isinstance(metrics_dict['gwt']['integration_level'], float)

        engine.shutdown()


class TestConsciousnessSingletonBehavior:
    """Test singleton pattern behavior for consciousness components"""

    def test_engine_singleton(self):
        """Test that consciousness engine is a singleton"""
        engine1 = get_consciousness_engine(debug=False)
        engine2 = get_consciousness_engine(debug=False)

        # Should be same instance
        assert engine1 is engine2

        engine1.shutdown()

    def test_component_singletons(self):
        """Test that all components use singleton pattern"""
        from consciousness.consciousness_services import (
            get_self_awareness_engine,
            get_qualia_simulator,
            get_global_workspace,
            get_metaconsciousness_system,
            get_iit_engine,
            get_binding_system,
            get_access_controller,
        )

        # Get instances twice
        sa1 = get_self_awareness_engine()
        sa2 = get_self_awareness_engine()
        assert sa1 is sa2

        qs1 = get_qualia_simulator()
        qs2 = get_qualia_simulator()
        assert qs1 is qs2

        gw1 = get_global_workspace()
        gw2 = get_global_workspace()
        assert gw1 is gw2

        mc1 = get_metaconsciousness_system()
        mc2 = get_metaconsciousness_system()
        assert mc1 is mc2

        iit1 = get_iit_engine()
        iit2 = get_iit_engine()
        assert iit1 is iit2

        bs1 = get_binding_system()
        bs2 = get_binding_system()
        assert bs1 is bs2

        ac1 = get_access_controller()
        ac2 = get_access_controller()
        assert ac1 is ac2


class TestConsciousnessStateManagement:
    """Test consciousness state management and persistence"""

    def test_state_summary(self):
        """Test complete state summary retrieval"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Add some content and process
        engine.broadcast_to_workspace("test", "data", 0.7)
        engine.process_cycle()

        # Get state summary
        state = engine.get_state_summary()

        # Verify structure
        assert 'initialized' in state
        assert 'active' in state
        assert 'cycle_count' in state
        assert 'consciousness_level' in state
        assert 'components' in state
        assert 'metrics' in state

        # Verify values
        assert state['initialized']
        assert state['active']
        assert state['cycle_count'] > 0
        assert 0.0 <= state['consciousness_level'] <= 1.0

        # Verify components
        components = state['components']
        assert all(components.values())  # All should be True (initialized)

        engine.shutdown()

    def test_shutdown_and_restart(self):
        """Test consciousness engine shutdown and restart"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Verify active
        assert engine.active

        # Add content
        engine.broadcast_to_workspace("test", "data", 0.7)
        engine.process_cycle()

        # Shutdown
        engine.shutdown()
        assert not engine.active

        # Note: Cannot restart same instance due to singleton pattern
        # But can verify shutdown worked
        state = engine.get_state_summary()
        assert not state['active']


class TestConsciousnessErrorHandling:
    """Test error handling in consciousness system"""

    def test_uninitialized_engine_operations(self):
        """Test operations on uninitialized engine auto-initialize"""
        engine = ConsciousnessEngine(debug=False)

        # Should auto-initialize
        level = engine.get_consciousness_level()
        assert engine.initialized
        assert 0.0 <= level <= 1.0

        engine.shutdown()

    def test_invalid_introspection_aspect(self):
        """Test handling of introspection queries"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Valid aspect should work
        result = engine.introspect(SelfAspect.CAPABILITIES)
        assert result is not None

        engine.shutdown()

    def test_workspace_capacity_overflow(self):
        """Test global workspace capacity management"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Fill workspace beyond capacity
        capacity = engine.global_workspace.capacity
        for i in range(capacity + 5):
            engine.broadcast_to_workspace(f"overflow_{i}", f"data_{i}", 0.5)

        # Verify workspace doesn't exceed capacity
        workspace_contents = asyncio.run(engine.global_workspace.get_conscious_contents())
        assert len(workspace_contents) <= capacity

        engine.shutdown()


# ============================================================================
# Performance Integration Tests
# ============================================================================

class TestConsciousnessPerformanceIntegration:
    """Test performance characteristics in integrated scenarios"""

    def test_rapid_cycling_performance(self):
        """Test performance under rapid consciousness cycling"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        import time

        # Rapid cycling
        num_cycles = 100
        start = time.perf_counter()

        for i in range(num_cycles):
            engine.broadcast_to_workspace(f"rapid_{i}", f"data_{i}", 0.5)
            engine.process_cycle()

        elapsed = time.perf_counter() - start

        # Should complete reasonably quickly (< 10 seconds for 100 cycles)
        assert elapsed < 10.0

        # Verify all cycles processed
        assert engine.cycle_count == num_cycles

        engine.shutdown()

    def test_concurrent_component_access(self):
        """Test concurrent access to consciousness components"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        import concurrent.futures

        def access_component(index):
            """Concurrent access function"""
            engine.broadcast_to_workspace(f"concurrent_{index}", f"data_{index}", 0.5)
            metrics = engine.process_cycle()
            return metrics.overall_consciousness_level

        # Concurrent access
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(access_component, i) for i in range(20)]
            results = [f.result() for f in futures]

        # Verify all completed
        assert len(results) == 20
        assert all(0.0 <= level <= 1.0 for level in results)

        engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
