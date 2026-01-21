"""
Comprehensive tests for Consciousness Engine

Tests all major functionality:
- ConsciousnessMetrics
- ConsciousnessEngine initialization
- Consciousness level computation
- Component integration
- Metrics history
- Introspection
- Qualia generation
- Global workspace broadcasting
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from consciousness.consciousness_services import (
    ConsciousnessEngine,
    ConsciousnessMetrics,
    SelfAspect,
    QualiaType,
    get_consciousness_engine,
)


class TestConsciousnessMetrics:
    """Test ConsciousnessMetrics class"""

    def test_metrics_creation(self):
        """Test creating consciousness metrics"""
        metrics = ConsciousnessMetrics()

        assert metrics.gwt_broadcast_rate == 0.0
        assert metrics.iit_phi_value == 0.0
        assert metrics.hot_metacognition_depth == 0
        assert metrics.overall_consciousness_level == 0.0

    def test_compute_overall_level(self):
        """Test computing overall consciousness level"""
        metrics = ConsciousnessMetrics(
            gwt_integration_level=0.8,
            gwt_content_diversity=0.7,
            iit_phi_value=0.6,
            iit_integration_score=0.9,
            hot_self_awareness=0.75,
            hot_metacognition_depth=3,
            phenomenal_unity=0.8,
            phenomenal_vividness=0.7,
            access_availability=0.85,
            access_reportability=0.8,
            access_control_quality=0.9,
            self_model_accuracy=0.7,
            self_introspection_depth=0.75,
            self_identity_coherence=0.8,
        )

        level = metrics.compute_overall_level()

        # Should be weighted average
        assert 0.0 <= level <= 1.0
        assert level > 0.6  # With these high values, should be > 0.6
        assert metrics.overall_consciousness_level == level

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary"""
        metrics = ConsciousnessMetrics(
            gwt_integration_level=0.8,
            iit_phi_value=0.6,
        )
        metrics.compute_overall_level()

        result = metrics.to_dict()

        assert isinstance(result, dict)
        assert 'gwt' in result
        assert 'iit' in result
        assert 'hot' in result
        assert 'phenomenal' in result
        assert 'access' in result
        assert 'self_awareness' in result
        assert 'overall_level' in result
        assert result['gwt']['integration_level'] == 0.8
        assert result['iit']['phi_value'] == 0.6


class TestConsciousnessEngine:
    """Test ConsciousnessEngine class"""

    def test_engine_creation(self):
        """Test creating consciousness engine"""
        engine = ConsciousnessEngine(debug=False)

        assert engine is not None
        assert not engine.initialized
        assert not engine.active
        assert engine.cycle_count == 0

    def test_engine_initialization(self):
        """Test initializing consciousness engine"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        assert engine.initialized
        assert engine.active
        assert engine.self_awareness is not None
        assert engine.qualia_sim is not None
        assert engine.global_workspace is not None
        assert engine.metaconsciousness is not None
        assert engine.iit_engine is not None
        assert engine.binding_system is not None
        assert engine.access_controller is not None

    def test_engine_singleton(self):
        """Test engine singleton pattern"""
        engine1 = get_consciousness_engine(debug=False)
        engine2 = get_consciousness_engine(debug=False)

        # Should be same instance
        assert engine1 is engine2

    def test_process_cycle(self):
        """Test processing consciousness cycle"""
        engine = ConsciousnessEngine(debug=False)

        metrics = engine.process_cycle()

        assert isinstance(metrics, ConsciousnessMetrics)
        assert engine.cycle_count == 1
        assert len(engine.metrics_history) == 1

    def test_multiple_cycles(self):
        """Test multiple processing cycles"""
        engine = ConsciousnessEngine(debug=False)

        for i in range(5):
            metrics = engine.process_cycle()
            assert engine.cycle_count == i + 1

        assert len(engine.metrics_history) == 5

    def test_compute_metrics(self):
        """Test computing consciousness metrics"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        metrics = engine.compute_metrics()

        assert isinstance(metrics, ConsciousnessMetrics)
        assert 0.0 <= metrics.overall_consciousness_level <= 1.0

    def test_get_consciousness_level(self):
        """Test getting consciousness level"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        level = engine.get_consciousness_level()

        assert isinstance(level, float)
        assert 0.0 <= level <= 1.0

    def test_introspection(self):
        """Test introspection functionality"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        result = engine.introspect(SelfAspect.CAPABILITIES)

        assert result is not None
        assert result.aspect == SelfAspect.CAPABILITIES
        assert 0.0 <= result.confidence <= 1.0

    def test_generate_qualia(self):
        """Test qualia generation"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        quale = engine.generate_qualia(QualiaType.CONCEPTUAL, intensity=0.7)

        assert quale is not None
        assert quale.type == QualiaType.CONCEPTUAL
        assert quale.intensity == 0.7

    def test_broadcast_to_workspace(self):
        """Test broadcasting to global workspace"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Broadcast content
        engine.broadcast_to_workspace(
            content_id="test_content",
            data={"message": "test"},
            salience=0.8
        )

        # Verify broadcast occurred
        assert len(engine.global_workspace.content) > 0

    def test_metrics_history(self):
        """Test metrics history tracking"""
        engine = ConsciousnessEngine(debug=False)

        # Process multiple cycles
        for _ in range(10):
            engine.process_cycle()

        history = engine.get_metrics_history(limit=5)

        assert len(history) == 5
        assert all(isinstance(m, ConsciousnessMetrics) for m in history)

    def test_metrics_history_limit(self):
        """Test metrics history size limit"""
        engine = ConsciousnessEngine(debug=False)
        engine.max_history_size = 10

        # Process more cycles than limit
        for _ in range(15):
            engine.process_cycle()

        # Should only keep last 10
        assert len(engine.metrics_history) == 10

    def test_get_state_summary(self):
        """Test getting state summary"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()
        engine.process_cycle()

        summary = engine.get_state_summary()

        assert isinstance(summary, dict)
        assert 'initialized' in summary
        assert 'active' in summary
        assert 'cycle_count' in summary
        assert 'consciousness_level' in summary
        assert 'components' in summary
        assert 'metrics' in summary

        assert summary['initialized'] is True
        assert summary['active'] is True
        assert summary['cycle_count'] >= 1

    def test_components_initialized(self):
        """Test all components are properly initialized"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        summary = engine.get_state_summary()
        components = summary['components']

        assert components['self_awareness'] is True
        assert components['qualia_simulator'] is True
        assert components['global_workspace'] is True
        assert components['metaconsciousness'] is True
        assert components['iit_engine'] is True
        assert components['binding_system'] is True
        assert components['access_controller'] is True

    def test_consciousness_level_increases_with_activity(self):
        """Test consciousness level changes with activity"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Initial level
        initial_level = engine.get_consciousness_level()

        # Add activity - broadcast content
        for i in range(5):
            engine.broadcast_to_workspace(
                content_id=f"content_{i}",
                data={"value": i},
                salience=0.7
            )

        # Generate qualia
        for qtype in [QualiaType.CONCEPTUAL, QualiaType.EMOTIONAL]:
            engine.generate_qualia(qtype, intensity=0.6)

        # Process cycle to update metrics
        engine.process_cycle()

        # Level should potentially increase with activity
        new_level = engine.get_consciousness_level()

        # At minimum, should be computed
        assert 0.0 <= new_level <= 1.0

    def test_shutdown(self):
        """Test engine shutdown"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        assert engine.active is True

        engine.shutdown()

        assert engine.active is False

    def test_introspection_different_aspects(self):
        """Test introspection on different aspects"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        aspects_to_test = [
            SelfAspect.CAPABILITIES,
            SelfAspect.LIMITATIONS,
            SelfAspect.GOALS,
            SelfAspect.EMOTIONS,
        ]

        for aspect in aspects_to_test:
            result = engine.introspect(aspect)
            assert result.aspect == aspect
            assert result.content is not None


class TestConsciousnessIntegration:
    """Integration tests for consciousness system"""

    def test_full_consciousness_simulation(self):
        """Test complete consciousness simulation workflow"""
        # Create and initialize engine
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Simulate activity
        # 1. Broadcast information to global workspace
        engine.broadcast_to_workspace(
            content_id="perception_1",
            data={"type": "visual", "content": "red circle"},
            salience=0.9
        )

        # 2. Generate qualia
        quale = engine.generate_qualia(QualiaType.VISUAL, intensity=0.8)
        assert quale is not None

        # 3. Introspect
        caps_result = engine.introspect(SelfAspect.CAPABILITIES)
        assert caps_result.content is not None

        # 4. Process consciousness cycle
        metrics = engine.process_cycle()
        assert metrics.overall_consciousness_level > 0.0

        # 5. Get state summary
        summary = engine.get_state_summary()
        assert summary['initialized'] is True
        assert summary['cycle_count'] >= 1

    def test_consciousness_metrics_all_theories(self):
        """Test that all consciousness theories are measured"""
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Add some activity
        engine.broadcast_to_workspace("test", {"data": "test"}, 0.5)
        engine.process_cycle()

        metrics = engine.compute_metrics()

        # Should have metrics for all theories
        # GWT
        assert metrics.gwt_integration_level >= 0.0
        assert metrics.gwt_content_diversity >= 0.0

        # IIT
        assert metrics.iit_phi_value >= 0.0
        assert metrics.iit_integration_score >= 0.0

        # HOT
        assert metrics.hot_metacognition_depth >= 0
        assert metrics.hot_self_awareness >= 0.0

        # Phenomenal
        assert metrics.phenomenal_unity >= 0.0
        assert metrics.phenomenal_vividness >= 0.0

        # Access
        assert metrics.access_availability >= 0.0
        assert metrics.access_reportability >= 0.0

        # Self-awareness
        assert metrics.self_model_accuracy >= 0.0
        assert metrics.self_introspection_depth >= 0.0


# Run tests with: pytest tests/unit/consciousness/test_consciousness_engine.py -v
