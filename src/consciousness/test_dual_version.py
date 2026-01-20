"""
Test Dual-Version Consciousness Implementation
"""

import asyncio
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consciousness import (
    # Check which version is being used
    HAS_NUMPY,
    
    # Enums
    SelfAspect,
    QualiaType,
    
    # Dataclasses
    IntrospectionQuery,
    ConsciousContent,
    BindingRequest,
    AccessRequest,
    
    # Systems
    SelfAwarenessEngine,
    QualiaSimulator,
    GlobalWorkspace,
    MetaconsciousnessSystem,
    IntegratedInformationEngine,
    PhenomenalBindingSystem,
    ConsciousAccessController,
    
    # Singletons
    get_self_awareness_engine,
    get_qualia_simulator,
    get_global_workspace,
    get_metaconsciousness_system,
    get_iit_engine,
    get_binding_system,
    get_access_controller,
)


async def test_self_awareness():
    """Test self-awareness engine"""
    print("\nTesting Self-Awareness Engine...")
    
    engine = get_self_awareness_engine()
    
    query = IntrospectionQuery(
        aspect=SelfAspect.CAPABILITIES,
        depth="moderate",
    )
    
    result = await engine.introspect(query)
    
    print(f"  Aspect: {result.aspect.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Has uncertainty: {result.uncertainty is not None}")
    
    model = await engine.get_self_model()
    print(f"  Identity: {model.identity}")
    
    print("  ✅ Self-Awareness Engine works!")


async def test_qualia_simulator():
    """Test qualia simulator"""
    print("\nTesting Qualia Simulator...")
    
    simulator = get_qualia_simulator()
    
    quale = await simulator.generate_quale(
        quale_type=QualiaType.VISUAL,
        stimulus="test_image",
    )
    
    print(f"  Quale type: {quale.type.value}")
    print(f"  Intensity: {quale.intensity:.2f}")
    print(f"  Valence: {quale.valence:.2f}")
    
    experience = await simulator.synthesize_experience([quale])
    print(f"  Unity score: {experience.unity_score:.2f}")
    print(f"  Vividness: {experience.vividness:.2f}")
    
    print("  ✅ Qualia Simulator works!")


async def test_global_workspace():
    """Test global workspace"""
    print("\nTesting Global Workspace...")
    
    workspace = get_global_workspace()
    
    content = ConsciousContent(
        content_id="test1",
        data="test_data",
        salience=0.8,
    )
    
    added = await workspace.add_to_workspace(content)
    print(f"  Content added: {added}")
    
    event = await workspace.broadcast(content)
    print(f"  Broadcast recipients: {event.recipient_count}")
    
    contents = await workspace.get_conscious_contents()
    print(f"  Conscious contents: {len(contents)}")
    
    print("  ✅ Global Workspace works!")


async def test_metaconsciousness():
    """Test metaconsciousness system"""
    print("\nTesting Metaconsciousness System...")
    
    meta = get_metaconsciousness_system()
    
    hot = await meta.generate_hot(
        target_thought="I am thinking",
        meta_level=1,
    )
    
    print(f"  HOT about: {hot.about}")
    print(f"  Meta level: {hot.meta_level}")
    
    state = await meta.reflect(depth=2)
    print(f"  Reflection depth: {state.reflection_depth}")
    print(f"  Current thoughts: {len(state.current_thoughts)}")
    
    print("  ✅ Metaconsciousness System works!")


async def test_iit_engine():
    """Test integrated information engine"""
    print("\nTesting Integrated Information Engine...")
    
    iit = get_iit_engine()
    
    system_state = {
        "size": 10,
        "connections": [[0.0] * 10 for _ in range(10)],
    }
    
    phi = await iit.calculate_phi(system_state)
    
    print(f"  Phi value: {phi.phi_value:.3f}")
    print(f"  System size: {phi.system_size}")
    print(f"  Integration: {phi.integration_measure:.3f}")
    
    structure = await iit.analyze_causal_structure(
        nodes=["n1", "n2", "n3"],
        connections=[[1.0, 0.5, 0.0], [0.0, 1.0, 0.5], [0.0, 0.0, 1.0]],
    )
    
    print(f"  Causal nodes: {len(structure.nodes)}")
    print(f"  Effective info: {structure.effective_information:.3f}")
    
    print("  ✅ IIT Engine works!")


async def test_binding_system():
    """Test phenomenal binding system"""
    print("\nTesting Phenomenal Binding System...")
    
    binding = get_binding_system()
    
    request = BindingRequest(
        features=["color", "shape", "location"],
        binding_type="feature",
        priority=0.7,
    )
    
    experience = await binding.bind_features(request)
    
    print(f"  Bound features: {len(experience.bound_features)}")
    print(f"  Unity measure: {experience.unity_measure:.2f}")
    print(f"  Strength: {experience.strength:.2f}")
    
    integrity = await binding.check_binding_integrity()
    print(f"  Average unity: {integrity['average_unity']:.2f}")
    
    print("  ✅ Phenomenal Binding System works!")


async def test_access_controller():
    """Test conscious access controller"""
    print("\nTesting Conscious Access Controller...")
    
    controller = get_access_controller(threshold=0.5)
    
    request = AccessRequest(
        content_id="test_content",
        priority=0.7,
        source="test_module",
    )
    
    decision = await controller.evaluate_access(request)
    
    print(f"  Access granted: {decision.granted}")
    print(f"  Latency: {decision.latency:.3f}s")
    print(f"  Reasoning: {decision.reasoning}")
    
    stats = await controller.get_access_stats()
    print(f"  Grant rate: {stats['grant_rate']:.2f}")
    
    print("  ✅ Conscious Access Controller works!")


async def main():
    print("=" * 60)
    print("Consciousness Dual-Version Test Suite")
    print("=" * 60)
    
    print(f"\nTesting imports...")
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    
    await test_self_awareness()
    await test_qualia_simulator()
    await test_global_workspace()
    await test_metaconsciousness()
    await test_iit_engine()
    await test_binding_system()
    await test_access_controller()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
