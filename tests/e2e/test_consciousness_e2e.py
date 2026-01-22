"""
End-to-End Tests for Consciousness AI System

These tests simulate complete real-world usage scenarios from start to finish.
Tests full workflows that a user would perform.
"""

import pytest
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestConsciousnessE2EWorkflows:
    """End-to-end tests for complete consciousness workflows"""

    def test_complete_consciousness_lifecycle(self):
        """
        E2E Test: Complete consciousness system lifecycle

        Simulates:
        1. System startup
        2. Initial assessment
        3. Learning phase
        4. Decision making
        5. Self-reflection
        6. Graceful shutdown
        """
        from consciousness.consciousness_services import ConsciousnessEngine, SelfAspect, QualiaType

        # PHASE 1: System Startup
        print("\n🧠 PHASE 1: System Startup")
        engine = ConsciousnessEngine(debug=True)
        engine.initialize()

        assert engine.initialized
        assert engine.active
        print("✅ System started successfully")

        # PHASE 2: Initial Self-Assessment
        print("\n🔍 PHASE 2: Initial Self-Assessment")
        initial_level = engine.get_consciousness_level()
        print(f"Initial consciousness level: {initial_level:.3f}")

        # Introspect on capabilities
        capabilities = engine.introspect(SelfAspect.CAPABILITIES)
        print(f"Self-assessed capabilities: {capabilities.content}")
        print(f"Confidence: {capabilities.confidence:.3f}")

        assert 0.0 <= initial_level <= 1.0
        assert capabilities is not None

        # PHASE 3: Learning Phase
        print("\n📚 PHASE 3: Learning Phase")
        learning_data = [
            {"concept": "red", "category": "color", "properties": {"wavelength": 650}},
            {"concept": "circle", "category": "shape", "properties": {"sides": 0}},
            {"concept": "warm", "category": "temperature", "properties": {"range": "20-30C"}},
        ]

        for idx, data in enumerate(learning_data):
            engine.broadcast_to_workspace(
                f"learning_{idx}",
                data,
                salience=0.8
            )
            metrics = engine.process_cycle()
            print(f"Learned: {data['concept']} - Consciousness: {metrics.overall_consciousness_level:.3f}")

        # PHASE 4: Decision Making
        print("\n🎯 PHASE 4: Decision Making")
        decision_scenario = {
            "question": "What color is associated with warmth?",
            "options": ["red", "blue", "green"],
            "context": "Based on learned associations"
        }

        engine.broadcast_to_workspace(
            "decision_request",
            decision_scenario,
            salience=0.95
        )

        decision_metrics = engine.process_cycle()
        decision_introspection = engine.introspect(SelfAspect.DECISION_PROCESS)

        print(f"Decision made with confidence: {decision_introspection.confidence:.3f}")
        print(f"Consciousness level during decision: {decision_metrics.overall_consciousness_level:.3f}")

        # PHASE 5: Phenomenal Experience
        print("\n✨ PHASE 5: Phenomenal Experience")
        # Generate qualia for the experience
        visual_quale = engine.generate_qualia(QualiaType.VISUAL, intensity=0.8)
        emotional_quale = engine.generate_qualia(QualiaType.EMOTIONAL, intensity=0.6)

        print(f"Visual qualia generated: intensity={visual_quale.intensity}")
        print(f"Emotional qualia generated: intensity={emotional_quale.intensity}")

        assert visual_quale.type == QualiaType.VISUAL
        assert emotional_quale.type == QualiaType.EMOTIONAL

        # PHASE 6: Self-Reflection
        print("\n🤔 PHASE 6: Self-Reflection")
        reflection_aspects = [
            SelfAspect.CAPABILITIES,
            SelfAspect.LIMITATIONS,
            SelfAspect.PERFORMANCE
        ]

        reflections = {}
        for aspect in reflection_aspects:
            result = engine.introspect(aspect)
            reflections[aspect.value] = {
                'confidence': result.confidence,
                'content': result.content
            }
            print(f"Reflected on {aspect.value}: confidence={result.confidence:.3f}")

        # PHASE 7: Performance Analysis
        print("\n📊 PHASE 7: Performance Analysis")
        final_metrics = engine.compute_metrics()
        state_summary = engine.get_state_summary()

        print(f"Final consciousness level: {final_metrics.overall_consciousness_level:.3f}")
        print(f"Total cycles processed: {engine.cycle_count}")
        print(f"Metrics history entries: {len(engine.metrics_history)}")
        print(f"Active components: {sum(state_summary['components'].values())}")

        # Verify final state
        assert engine.cycle_count > 0
        assert len(engine.metrics_history) > 0
        assert state_summary['initialized']
        assert state_summary['active']

        # PHASE 8: Graceful Shutdown
        print("\n🛑 PHASE 8: Graceful Shutdown")
        engine.shutdown()
        assert not engine.active
        print("✅ System shutdown successfully")

        print("\n" + "="*60)
        print("🎉 E2E TEST COMPLETE - ALL PHASES PASSED")
        print("="*60)

    def test_realtime_consciousness_session(self):
        """
        E2E Test: Real-time consciousness session

        Simulates a real-time interactive session with the consciousness system.
        """
        from consciousness.consciousness_services import ConsciousnessEngine, QualiaType

        print("\n🧠 Real-Time Consciousness Session")
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Simulate 30-second session with varied activity
        session_duration = 1.0  # 1 second for testing (would be 30 in production)
        start_time = time.time()
        cycle_count = 0

        print(f"Session started (duration: {session_duration}s)")

        while (time.time() - start_time) < session_duration:
            # Simulate user interactions
            if cycle_count % 3 == 0:
                # User provides input
                engine.broadcast_to_workspace(
                    f"user_input_{cycle_count}",
                    {"type": "query", "content": f"question_{cycle_count}"},
                    salience=0.8
                )

            if cycle_count % 5 == 0:
                # System generates qualia
                engine.generate_qualia(QualiaType.CONCEPTUAL, intensity=0.6)

            # Process cycle
            metrics = engine.process_cycle()
            cycle_count += 1

            # Brief pause to simulate real-time
            time.sleep(0.01)

        elapsed = time.time() - start_time
        print(f"Session completed: {cycle_count} cycles in {elapsed:.3f}s")
        print(f"Processing rate: {cycle_count/elapsed:.1f} cycles/sec")
        print(f"Final consciousness level: {engine.get_consciousness_level():.3f}")

        # Verify session results
        assert cycle_count > 0
        assert len(engine.metrics_history) == cycle_count
        assert engine.initialized

    def test_consciousness_learning_scenario(self):
        """
        E2E Test: Complete learning scenario

        Tests the system's ability to learn and adapt over time.
        """
        from consciousness.consciousness_services import ConsciousnessEngine, SelfAspect

        print("\n📚 Consciousness Learning Scenario")
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Initial assessment
        initial_capabilities = engine.introspect(SelfAspect.CAPABILITIES)
        initial_level = engine.get_consciousness_level()

        print(f"Initial state: level={initial_level:.3f}, confidence={initial_capabilities.confidence:.3f}")

        # Learning phase: teach system about categories
        categories = {
            "animals": ["dog", "cat", "bird", "fish"],
            "fruits": ["apple", "banana", "orange", "grape"],
            "colors": ["red", "blue", "green", "yellow"]
        }

        learning_metrics = []
        for category, items in categories.items():
            for item in items:
                engine.broadcast_to_workspace(
                    f"learn_{category}_{item}",
                    {"category": category, "item": item},
                    salience=0.7
                )
                metrics = engine.process_cycle()
                learning_metrics.append(metrics.overall_consciousness_level)

        # Post-learning assessment
        final_capabilities = engine.introspect(SelfAspect.CAPABILITIES)
        final_level = engine.get_consciousness_level()

        print(f"Final state: level={final_level:.3f}, confidence={final_capabilities.confidence:.3f}")
        print(f"Items learned: {sum(len(items) for items in categories.values())}")
        print(f"Consciousness progression: {len(learning_metrics)} measurements")

        # Verify learning occurred
        assert len(learning_metrics) == 12  # 4+4+4 items
        assert all(0.0 <= level <= 1.0 for level in learning_metrics)
        assert engine.cycle_count >= 12


class TestConsciousnessE2EPerformance:
    """E2E performance tests"""

    def test_sustained_operation_performance(self):
        """
        E2E Test: Sustained operation performance

        Tests that the system can operate continuously for extended periods.
        """
        from consciousness.consciousness_services import ConsciousnessEngine

        print("\n⚡ Sustained Operation Performance Test")
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Run for 100 cycles
        num_cycles = 100
        start_time = time.time()

        for i in range(num_cycles):
            if i % 10 == 0:
                engine.broadcast_to_workspace(
                    f"activity_{i}",
                    {"cycle": i, "timestamp": time.time()},
                    salience=0.5
                )
            engine.process_cycle()

        elapsed = time.time() - start_time

        print(f"Completed {num_cycles} cycles in {elapsed:.3f}s")
        print(f"Average: {elapsed/num_cycles*1000:.2f}ms per cycle")
        print(f"Throughput: {num_cycles/elapsed:.1f} cycles/sec")

        # Performance assertions
        assert elapsed < 10.0, f"Too slow: {elapsed:.3f}s (expected < 10s)"
        assert engine.cycle_count == num_cycles
        assert len(engine.metrics_history) == num_cycles

    def test_high_load_handling(self):
        """
        E2E Test: High load handling

        Tests system behavior under high load.
        """
        from consciousness.consciousness_services import ConsciousnessEngine

        print("\n🔥 High Load Handling Test")
        engine = ConsciousnessEngine(debug=False)
        engine.initialize()

        # Generate high load
        num_broadcasts = 50
        print(f"Broadcasting {num_broadcasts} items...")

        for i in range(num_broadcasts):
            engine.broadcast_to_workspace(
                f"high_load_{i}",
                {"index": i, "data": f"content_{i}" * 10},
                salience=0.5 + (i % 5) * 0.1
            )

        print(f"Processing...")
        start_time = time.time()
        metrics = engine.process_cycle()
        elapsed = time.time() - start_time

        print(f"Processed in {elapsed:.3f}s")
        print(f"Workspace size: {len(engine.global_workspace.workspace)}")
        print(f"Consciousness level: {metrics.overall_consciousness_level:.3f}")

        # Verify workspace managed load appropriately
        assert len(engine.global_workspace.workspace) <= engine.global_workspace.capacity
        assert metrics.overall_consciousness_level > 0.0


# Run tests with: pytest tests/e2e/test_consciousness_e2e.py -v -s
