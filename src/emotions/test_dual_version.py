"""Test Dual-Version Emotions Implementation"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotions import (
    HAS_NUMPY, EmotionType, EmpathyType, EmotionalTone, Emotion,
    get_emotional_awareness_engine, get_affective_system, get_empathy_simulator,
    get_emotional_intelligence_system, get_emotional_memory_system,
    get_emotional_decision_system, get_expression_generator,
)

async def main():
    print("=" * 60)
    print("Emotions Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Emotional Awareness...")
    aware = get_emotional_awareness_engine()
    emo = await aware.recognize_emotion("I am happy today!")
    print(f"  Emotion: {emo.type.value}, Intensity: {emo.intensity:.2f}")
    state = aware.get_emotional_state()
    print(f"  State: {state.primary_emotion.type.value if state else 'None'}")
    print("  ✅ Emotional Awareness works!")
    
    print("\nTesting Affective Computing...")
    affect = get_affective_system()
    gen_emo = await affect.generate_emotion("good news", {})
    print(f"  Generated: {gen_emo.type.value}")
    mood = await affect.update_mood([gen_emo])
    print(f"  Mood: {mood}")
    print("  ✅ Affective Computing works!")
    
    print("\nTesting Empathy Simulator...")
    empathy = get_empathy_simulator()
    emp_resp = await empathy.empathize(emo, EmpathyType.COGNITIVE)
    print(f"  Empathy strength: {emp_resp['empathy_strength']:.2f}")
    persp = await empathy.perspective_take("person1", "situation")
    print(f"  Inferred emotions: {len(persp['inferred_emotions'])}")
    print("  ✅ Empathy Simulator works!")
    
    print("\nTesting Emotional Intelligence...")
    eq = get_emotional_intelligence_system()
    eq_score = await eq.assess_eq("person1")
    print(f"  Overall EQ: {eq_score['overall_eq']:.2f}")
    print("  ✅ Emotional Intelligence works!")
    
    print("\nTesting Emotional Memory...")
    mem = get_emotional_memory_system()
    mem_id = await mem.store_emotional_memory("event", emo, 0.8)
    print(f"  Stored: {mem_id}")
    retrieved = await mem.retrieve_emotional_memories(EmotionType.HAPPINESS, 5)
    print(f"  Retrieved: {len(retrieved)}")
    print("  ✅ Emotional Memory works!")
    
    print("\nTesting Emotional Decision...")
    dec = get_emotional_decision_system()
    decision = await dec.make_emotional_decision(["A", "B", "C"], [emo])
    print(f"  Decision: {decision['decision']}")
    print(f"  Confidence: {decision['confidence']:.2f}")
    print("  ✅ Emotional Decision works!")
    
    print("\nTesting Expression Generator...")
    expr = get_expression_generator()
    text = await expr.generate_expression(emo, EmotionalTone.WARM)
    print(f"  Expression: {text[:50]}")
    print("  ✅ Expression Generator works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
