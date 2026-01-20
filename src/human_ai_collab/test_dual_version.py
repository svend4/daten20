"""Test Human-AI Collaboration Dual-Version"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from human_ai_collab import (
    HAS_NUMPY, TaskRole, IntentType,
    get_collaborative_task_manager, get_intent_understanding,
    get_ai_capability_matcher, get_shared_mental_model,
    get_mixed_initiative_controller, get_performance_augmentation,
    get_trust_transparency_system,
)

async def main():
    print("=" * 60)
    print("Human-AI Collaboration Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Task Manager...")
    tm = get_collaborative_task_manager()
    task = await tm.create_task("Test task", TaskRole.COLLABORATIVE)
    print(f"  Task ID: {task.task_id}")
    alloc = await tm.allocate_task(task.task_id)
    print(f"  Allocated to: {alloc['allocated_to']}")
    print("  ✅ Task Manager works!")
    
    print("\nTesting Intent Understanding...")
    intent_sys = get_intent_understanding()
    intent = await intent_sys.understand_intent("Do something")
    print(f"  Intent type: {intent.intent_type.value}")
    print(f"  Confidence: {intent.confidence:.2f}")
    print("  ✅ Intent Understanding works!")
    
    print("\nTesting AI Capability Matcher...")
    matcher = get_ai_capability_matcher()
    matches = await matcher.match_capabilities("Generate text")
    print(f"  Matched capabilities: {len(matches)}")
    print("  ✅ AI Capability Matcher works!")
    
    print("\nTesting Shared Mental Model...")
    smm = get_shared_mental_model()
    sync = await smm.synchronize_context({"h": 1}, {"a": 2})
    print(f"  Alignment score: {sync['alignment_score']:.2f}")
    print("  ✅ Shared Mental Model works!")
    
    print("\nTesting Mixed Initiative Controller...")
    mic = get_mixed_initiative_controller()
    control = await mic.negotiate_control(0.8, 0.6)
    print(f"  Control mode: {control['control_mode']}")
    print("  ✅ Mixed Initiative Controller works!")
    
    print("\nTesting Performance Augmentation...")
    aug = get_performance_augmentation()
    result = await aug.augment_human_capability("task", 0.7)
    print(f"  Improvement: {result['improvement']:.2f}")
    print("  ✅ Performance Augmentation works!")
    
    print("\nTesting Trust/Transparency...")
    trust = get_trust_transparency_system()
    expl = await trust.explain_ai_decision("decision", {})
    print(f"  Confidence: {expl['confidence']:.2f}")
    score = trust.get_trust_score()
    print(f"  Trust score: {score:.2f}")
    print("  ✅ Trust/Transparency works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
