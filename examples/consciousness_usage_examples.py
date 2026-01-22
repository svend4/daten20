"""
🧠 Comprehensive Usage Examples for Consciousness AI Module

This file demonstrates all major features of the Consciousness simulation platform.
Examples range from basic to advanced usage patterns.

**Pure Python Version** - Works without NumPy!

Examples:
1. Basic Consciousness Engine Usage
2. Self-Awareness and Introspection
3. Qualia Simulation and Phenomenal Experience
4. Global Workspace Broadcasting
5. Metacognition and Higher-Order Thoughts
6. Integrated Information Theory (IIT)
7. Phenomenal Binding and Unity
8. Conscious Access Control
9. Complete Consciousness Lifecycle
10. Real-time Consciousness Monitoring

Version: 1.0.0
Date: January 2026
"""

import asyncio
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from consciousness.consciousness_services import (
    ConsciousnessEngine,
    SelfAwarenessEngine,
    QualiaSimulator,
    GlobalWorkspace,
    MetaconsciousnessSystem,
    IntegratedInformationEngine,
    PhenomenalBindingSystem,
    ConsciousAccessController,
    # Data classes
    SelfAspect,
    QualiaType,
    ConsciousContent,
    IntrospectionQuery,
    BindingRequest,
    AccessRequest,
    # Singletons
    get_consciousness_engine,
    get_self_awareness_engine,
    get_qualia_simulator,
    get_global_workspace,
)


# ============================================================================
# Example 1: Basic Consciousness Engine Usage
# ============================================================================

def example_01_basic_engine():
    """
    Example 1: Basic Consciousness Engine

    Demonstrates:
    - Engine initialization
    - Metrics computation
    - Consciousness level assessment
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Consciousness Engine Usage")
    print("="*70)

    # Create and initialize engine
    engine = ConsciousnessEngine(debug=True)
    engine.initialize()

    # Get consciousness level
    level = engine.get_consciousness_level()
    print(f"\n📊 Current consciousness level: {level:.3f}/1.000")

    # Compute detailed metrics
    metrics = engine.compute_metrics()
    print(f"\n📈 Detailed Metrics:")
    print(f"  - GWT Integration: {metrics.gwt_integration_level:.3f}")
    print(f"  - IIT Phi Value: {metrics.iit_phi_value:.3f}")
    print(f"  - HOT Self-Awareness: {metrics.hot_self_awareness:.3f}")
    print(f"  - Phenomenal Unity: {metrics.phenomenal_unity:.3f}")
    print(f"  - Access Availability: {metrics.access_availability:.3f}")
    print(f"  - Overall Level: {metrics.overall_consciousness_level:.3f}")

    # Get state summary
    state = engine.get_state_summary()
    print(f"\n🔧 System State:")
    print(f"  - Initialized: {state['initialized']}")
    print(f"  - Active: {state['active']}")
    print(f"  - Cycle Count: {state['cycle_count']}")
    print(f"  - Active Components: {sum(state['components'].values())}/7")

    return engine


# ============================================================================
# Example 2: Self-Awareness and Introspection
# ============================================================================

def example_02_self_awareness():
    """
    Example 2: Self-Awareness and Introspection

    Demonstrates:
    - Introspection on different aspects
    - Self-model updates
    - Self-awareness assessment
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Self-Awareness and Introspection")
    print("="*70)

    engine = ConsciousnessEngine(debug=False)
    engine.initialize()

    # Introspect on different aspects
    aspects = [
        SelfAspect.CAPABILITIES,
        SelfAspect.LIMITATIONS,
        SelfAspect.GOALS,
        SelfAspect.EMOTIONS,
        SelfAspect.DECISION_PROCESS,
    ]

    print("\n🔍 Introspection Results:")
    for aspect in aspects:
        result = engine.introspect(aspect)
        print(f"\n  {aspect.value.upper()}:")
        print(f"    Content: {result.content}")
        print(f"    Confidence: {result.confidence:.3f}")
        if result.reasoning:
            print(f"    Reasoning: {result.reasoning}")

    return engine


# ============================================================================
# Example 3: Qualia Simulation
# ============================================================================

def example_03_qualia_simulation():
    """
    Example 3: Qualia Simulation and Phenomenal Experience

    Demonstrates:
    - Generating different types of qualia
    - Comparing qualia similarity
    - Creating unified phenomenal experiences
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Qualia Simulation and Phenomenal Experience")
    print("="*70)

    engine = ConsciousnessEngine(debug=False)
    engine.initialize()

    # Generate various qualia
    print("\n✨ Generating Qualia:")

    qualia_list = []
    qualia_types = [
        (QualiaType.VISUAL, 0.9),
        (QualiaType.AUDITORY, 0.7),
        (QualiaType.EMOTIONAL, 0.8),
        (QualiaType.CONCEPTUAL, 0.6),
    ]

    for q_type, intensity in qualia_types:
        quale = engine.generate_qualia(q_type, intensity)
        qualia_list.append(quale)
        print(f"  {q_type.value.upper()}:")
        print(f"    Intensity: {quale.intensity:.3f}")
        print(f"    Valence: {quale.valence:.3f}")
        print(f"    ID: {quale.id}")

    # Compare qualia
    if len(qualia_list) >= 2:
        print(f"\n🔄 Qualia Comparison:")
        similarity = asyncio.run(
            engine.qualia_sim.compare_qualia(qualia_list[0], qualia_list[1])
        )
        print(f"  Visual vs Auditory similarity: {similarity:.3f}")

    return engine


# ============================================================================
# Example 4: Global Workspace Broadcasting
# ============================================================================

def example_04_global_workspace():
    """
    Example 4: Global Workspace Broadcasting

    Demonstrates:
    - Broadcasting content to global workspace
    - Workspace capacity management
    - Conscious content retrieval
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Global Workspace Broadcasting")
    print("="*70)

    engine = ConsciousnessEngine(debug=False)
    engine.initialize()

    # Broadcast multiple contents
    print("\n📢 Broadcasting to Global Workspace:")

    contents = [
        ("perception_001", {"type": "visual", "object": "red_apple"}, 0.9),
        ("thought_001", {"type": "conceptual", "content": "fruit"}, 0.7),
        ("memory_001", {"type": "recall", "event": "breakfast"}, 0.6),
        ("emotion_001", {"type": "feeling", "valence": 0.5}, 0.8),
        ("intention_001", {"type": "goal", "action": "eat"}, 0.85),
    ]

    for content_id, data, salience in contents:
        engine.broadcast_to_workspace(content_id, data, salience)
        print(f"  ✓ Broadcasted: {content_id} (salience: {salience:.2f})")

    # Process cycles to simulate workspace dynamics
    print("\n🔄 Processing Consciousness Cycles:")
    for i in range(3):
        metrics = engine.process_cycle()
        print(f"  Cycle {i+1}: Consciousness = {metrics.overall_consciousness_level:.3f}")

    # Get current workspace contents
    workspace_contents = asyncio.run(engine.global_workspace.get_conscious_contents())
    print(f"\n💭 Current Conscious Contents ({len(workspace_contents)}):")
    for content in workspace_contents:
        print(f"  - {content.content_id}: salience={content.salience:.3f}")

    return engine


# ============================================================================
# Example 5: Metacognition and Higher-Order Thoughts
# ============================================================================

async def example_05_metacognition():
    """
    Example 5: Metacognition and Higher-Order Thoughts

    Demonstrates:
    - Generating higher-order thoughts
    - Multi-level reflection
    - Meta-awareness assessment
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Metacognition and Higher-Order Thoughts")
    print("="*70)

    meta_system = get_metaconsciousness_system()

    # Generate HOTs at different levels
    print("\n🧠 Generating Higher-Order Thoughts:")

    # First-order thought
    thought1 = "I see a red apple"
    hot1 = await meta_system.generate_hot(thought1, meta_level=1)
    print(f"\n  Level 1 (HOT): {hot1.content}")
    print(f"    About: {hot1.about}")

    # Second-order thought (thinking about thinking)
    hot2 = await meta_system.generate_hot(hot1.content, meta_level=2)
    print(f"\n  Level 2 (HOT): {hot2.content}")
    print(f"    About: {hot2.about}")

    # Third-order thought
    hot3 = await meta_system.generate_hot(hot2.content, meta_level=3)
    print(f"\n  Level 3 (HOT): {hot3.content}")
    print(f"    About: {hot3.about}")

    # Perform reflection
    reflection = await meta_system.reflect(depth=2)
    print(f"\n🤔 Reflective State:")
    print(f"  Reflection Depth: {reflection.reflection_depth}")
    print(f"  Current Thoughts: {len(reflection.current_thoughts)}")

    # Assess meta-awareness
    meta_awareness = await meta_system.assess_meta_awareness()
    print(f"\n📊 Meta-Awareness Level: {meta_awareness:.3f}")


# ============================================================================
# Example 6: Integrated Information Theory
# ============================================================================

async def example_06_integrated_information():
    """
    Example 6: Integrated Information Theory (IIT)

    Demonstrates:
    - Phi calculation
    - Causal structure analysis
    - Consciousness assessment via IIT
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Integrated Information Theory (IIT)")
    print("="*70)

    iit_engine = get_iit_engine()

    # Calculate Phi for a system
    print("\n🔬 Calculating Integrated Information (Φ):")

    system_state = {
        "size": 10,
        "connections": [[1.0 if i != j else 0.0 for j in range(10)] for i in range(10)]
    }

    phi_calc = await iit_engine.calculate_phi(system_state)
    print(f"  System Size: {phi_calc.system_size}")
    print(f"  Phi Value (Φ): {phi_calc.phi_value:.3f}")
    print(f"  Integration Measure: {phi_calc.integration_measure:.3f}")
    print(f"  Information Measure: {phi_calc.information_measure:.3f}")

    # Analyze causal structure
    print("\n🕸️  Analyzing Causal Structure:")

    nodes = ["N1", "N2", "N3", "N4", "N5"]
    connections = [[0.8 if abs(i-j)==1 else 0.0 for j in range(5)] for i in range(5)]

    causal = await iit_engine.analyze_causal_structure(nodes, connections)
    print(f"  Nodes: {len(causal.nodes)}")
    print(f"  Effective Information: {causal.effective_information:.3f}")
    print(f"  Integration: {causal.integration:.3f}")

    # Assess consciousness
    consciousness = await iit_engine.assess_consciousness()
    print(f"\n📊 IIT Consciousness Assessment: {consciousness:.3f}")


# ============================================================================
# Example 7: Phenomenal Binding
# ============================================================================

async def example_07_phenomenal_binding():
    """
    Example 7: Phenomenal Binding and Unity

    Demonstrates:
    - Feature binding
    - Unified experience creation
    - Binding integrity checks
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Phenomenal Binding and Unity")
    print("="*70)

    binding_system = get_binding_system()

    # Bind features into unified experience
    print("\n🔗 Binding Features:")

    features = ["red_color", "round_shape", "smooth_texture", "sweet_taste", "apple_scent"]
    request = BindingRequest(
        features=features,
        binding_type="object",
        priority=0.9
    )

    bound = await binding_system.bind_features(request)
    print(f"  Bound Features: {', '.join(bound.bound_features)}")
    print(f"  Unity Measure: {bound.unity_measure:.3f}")
    print(f"  Binding Strength: {bound.strength:.3f}")

    # Create unified phenomenal experience
    print("\n✨ Creating Unified Experience:")

    contents = ["visual_red", "tactile_smooth", "gustatory_sweet"]
    unified = await binding_system.create_unified_experience(
        contents,
        unity_type="subject"
    )
    print(f"  Unified Contents: {len(unified.bound_features)}")
    print(f"  Unity: {unified.unity_measure:.3f}")
    print(f"  Strength: {unified.strength:.3f}")

    # Check binding integrity
    print("\n🔍 Binding Integrity Check:")
    integrity = await binding_system.check_binding_integrity()
    print(f"  Average Unity: {integrity['average_unity']:.3f}")
    print(f"  Average Strength: {integrity['average_strength']:.3f}")

    # Assess phenomenal unity
    unity = await binding_system.assess_unity()
    print(f"\n📊 Phenomenal Unity Assessment: {unity:.3f}")


# ============================================================================
# Example 8: Conscious Access Control
# ============================================================================

async def example_08_access_control():
    """
    Example 8: Conscious Access Control

    Demonstrates:
    - Access request evaluation
    - Threshold adjustment
    - Access statistics
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: Conscious Access Control")
    print("="*70)

    access_controller = get_access_controller()

    # Evaluate access requests
    print("\n🚪 Evaluating Access Requests:")

    requests = [
        AccessRequest(content_id="urgent_perception", priority=0.95, source="sensory"),
        AccessRequest(content_id="background_thought", priority=0.3, source="cognitive"),
        AccessRequest(content_id="emotional_signal", priority=0.75, source="limbic"),
        AccessRequest(content_id="memory_recall", priority=0.6, source="memory"),
    ]

    for request in requests:
        decision = await access_controller.evaluate_access(request)
        status = "✓ GRANTED" if decision.granted else "✗ DENIED"
        print(f"  {status}: {request.content_id}")
        print(f"    Priority: {request.priority:.2f}, Threshold: {access_controller.threshold:.2f}")
        print(f"    Latency: {decision.latency:.3f}s")

    # Get access statistics
    print("\n📊 Access Statistics:")
    stats = await access_controller.get_access_stats()
    print(f"  Grant Rate: {stats['grant_rate']:.2%}")
    print(f"  Average Latency: {stats['avg_latency']:.3f}s")

    # Adjust threshold
    print("\n⚙️  Adjusting Access Threshold:")
    print(f"  Current threshold: {access_controller.threshold:.2f}")
    await access_controller.adjust_threshold("lower", 0.1)
    print(f"  New threshold: {access_controller.threshold:.2f}")


# ============================================================================
# Example 9: Complete Consciousness Lifecycle
# ============================================================================

def example_09_complete_lifecycle():
    """
    Example 9: Complete Consciousness Lifecycle

    Demonstrates:
    - Full system initialization
    - Multi-phase consciousness processing
    - Real-world scenario simulation
    """
    print("\n" + "="*70)
    print("EXAMPLE 9: Complete Consciousness Lifecycle")
    print("="*70)

    # Initialize
    print("\n🚀 Phase 1: Initialization")
    engine = ConsciousnessEngine(debug=True)
    engine.initialize()

    # Self-assessment
    print("\n🔍 Phase 2: Self-Assessment")
    initial_level = engine.get_consciousness_level()
    print(f"  Initial consciousness: {initial_level:.3f}")

    # Learning
    print("\n📚 Phase 3: Learning")
    learning_data = [
        ("concept_1", {"type": "visual", "name": "apple", "color": "red"}, 0.9),
        ("concept_2", {"type": "conceptual", "name": "fruit", "category": "food"}, 0.8),
        ("concept_3", {"type": "associative", "link": "apple->fruit"}, 0.7),
    ]

    for content_id, data, salience in learning_data:
        engine.broadcast_to_workspace(content_id, data, salience)
        metrics = engine.process_cycle()
        print(f"  Learned: {data.get('name', content_id)} → Φ={metrics.overall_consciousness_level:.3f}")

    # Decision making
    print("\n🎯 Phase 4: Decision Making")
    decision_data = ("decision_1", {"question": "Is apple a fruit?", "confidence": 0.95}, 0.95)
    engine.broadcast_to_workspace(*decision_data)
    decision_metrics = engine.process_cycle()
    decision_result = engine.introspect(SelfAspect.DECISION_PROCESS)
    print(f"  Decision confidence: {decision_result.confidence:.3f}")
    print(f"  Consciousness during decision: {decision_metrics.overall_consciousness_level:.3f}")

    # Reflection
    print("\n🤔 Phase 5: Self-Reflection")
    capabilities = engine.introspect(SelfAspect.CAPABILITIES)
    performance = engine.introspect(SelfAspect.PERFORMANCE)
    print(f"  Capabilities confidence: {capabilities.confidence:.3f}")
    print(f"  Performance confidence: {performance.confidence:.3f}")

    # Final assessment
    print("\n📊 Phase 6: Final Assessment")
    final_metrics = engine.compute_metrics()
    print(f"  Final consciousness: {final_metrics.overall_consciousness_level:.3f}")
    print(f"  Improvement: {final_metrics.overall_consciousness_level - initial_level:+.3f}")
    print(f"  Total cycles: {engine.cycle_count}")

    # Shutdown
    print("\n🛑 Phase 7: Shutdown")
    engine.shutdown()
    print(f"  System active: {engine.active}")


# ============================================================================
# Example 10: Real-time Consciousness Monitoring
# ============================================================================

def example_10_realtime_monitoring():
    """
    Example 10: Real-time Consciousness Monitoring

    Demonstrates:
    - Continuous consciousness monitoring
    - Metrics tracking over time
    - Performance analysis
    """
    print("\n" + "="*70)
    print("EXAMPLE 10: Real-time Consciousness Monitoring")
    print("="*70)

    engine = ConsciousnessEngine(debug=False)
    engine.initialize()

    print("\n⏱️  Simulating Real-time Processing (10 cycles):\n")

    for i in range(10):
        # Simulate varying inputs
        salience = 0.5 + (i % 5) * 0.1
        engine.broadcast_to_workspace(
            f"stimulus_{i}",
            {"data": f"input_{i}", "timestamp": i},
            salience=salience
        )

        # Process cycle
        metrics = engine.process_cycle()

        # Display metrics
        print(f"Cycle {i+1:2d}: "
              f"Φ={metrics.overall_consciousness_level:.3f} | "
              f"GWT={metrics.gwt_integration_level:.3f} | "
              f"IIT={metrics.iit_phi_value:.3f} | "
              f"HOT={metrics.hot_self_awareness:.3f}")

    # Analyze history
    print("\n📈 Metrics History Analysis:")
    history = engine.get_metrics_history(limit=10)

    avg_consciousness = sum(m.overall_consciousness_level for m in history) / len(history)
    max_consciousness = max(m.overall_consciousness_level for m in history)
    min_consciousness = min(m.overall_consciousness_level for m in history)

    print(f"  Average Consciousness: {avg_consciousness:.3f}")
    print(f"  Maximum: {max_consciousness:.3f}")
    print(f"  Minimum: {min_consciousness:.3f}")
    print(f"  Range: {max_consciousness - min_consciousness:.3f}")

    # Component status
    print("\n🔧 Component Status:")
    state = engine.get_state_summary()
    for comp_name, active in state['components'].items():
        status = "✓ Active" if active else "✗ Inactive"
        print(f"  {comp_name:20s}: {status}")


# ============================================================================
# Main Runner
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🧠 CONSCIOUSNESS AI MODULE - COMPREHENSIVE EXAMPLES")
    print("="*70)
    print("\nPure Python Implementation - Zero Dependencies!")
    print("Demonstrates all major features of the consciousness simulation platform.")

    try:
        # Synchronous examples
        example_01_basic_engine()
        input("\n⏎ Press Enter to continue to Example 2...")

        example_02_self_awareness()
        input("\n⏎ Press Enter to continue to Example 3...")

        example_03_qualia_simulation()
        input("\n⏎ Press Enter to continue to Example 4...")

        example_04_global_workspace()
        input("\n⏎ Press Enter to continue to Example 5...")

        # Asynchronous examples
        asyncio.run(example_05_metacognition())
        input("\n⏎ Press Enter to continue to Example 6...")

        asyncio.run(example_06_integrated_information())
        input("\n⏎ Press Enter to continue to Example 7...")

        asyncio.run(example_07_phenomenal_binding())
        input("\n⏎ Press Enter to continue to Example 8...")

        asyncio.run(example_08_access_control())
        input("\n⏎ Press Enter to continue to Example 9...")

        example_09_complete_lifecycle()
        input("\n⏎ Press Enter to continue to Example 10...")

        example_10_realtime_monitoring()

        print("\n" + "="*70)
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
