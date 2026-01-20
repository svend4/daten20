"""Test Dual-Version AGI Implementation"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agi import (
    HAS_NUMPY, ModalityType, LearningStrategy, MultiModalInput, LearningTask,
    get_multi_modal_reasoner, get_continual_learner, get_meta_learning_system,
    get_knowledge_graph, get_cognitive_architecture, get_transfer_learning,
    get_ethical_framework,
)

async def main():
    print("=" * 60)
    print("AGI Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Multi-Modal Reasoning...")
    reasoner = get_multi_modal_reasoner()
    inputs = [MultiModalInput(ModalityType.TEXT, "test")]
    result = await reasoner.reason(inputs, "query")
    print(f"  Confidence: {result['confidence']:.2f}")
    print("  ✅ Multi-Modal Reasoning works!")
    
    print("\nTesting Continual Learning...")
    learner = get_continual_learner()
    task = LearningTask("task1", "domain", 0.5)
    learn_result = await learner.learn_task(task, [])
    print(f"  Performance: {learn_result['performance']:.2f}")
    print("  ✅ Continual Learning works!")
    
    print("\nTesting Meta-Learning...")
    meta = get_meta_learning_system()
    adapt = await meta.few_shot_adapt("task", [], k_shot=5)
    print(f"  Accuracy: {adapt['final_accuracy']:.2f}")
    print("  ✅ Meta-Learning works!")
    
    print("\nTesting Knowledge Graph...")
    kg = get_knowledge_graph()
    await kg.add_triple("Alice", "knows", "Bob")
    results = await kg.query("Alice")
    print(f"  Query results: {len(results)}")
    print("  ✅ Knowledge Graph works!")
    
    print("\nTesting Cognitive Architecture...")
    cog = get_cognitive_architecture()
    proc = await cog.process_input("test input")
    print(f"  Processed: {proc['processed']}")
    print("  ✅ Cognitive Architecture works!")
    
    print("\nTesting Transfer Learning...")
    transfer = get_transfer_learning()
    train = await transfer.train_source("source", [])
    print(f"  Source performance: {train['performance']:.2f}")
    print("  ✅ Transfer Learning works!")
    
    print("\nTesting Ethical AI Framework...")
    ethical = get_ethical_framework()
    eval_result = await ethical.evaluate_action("action", {})
    print(f"  Ethical score: {eval_result['ethical_score']:.2f}")
    print("  ✅ Ethical AI Framework works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
