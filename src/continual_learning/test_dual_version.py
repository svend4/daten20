"""Quick test for continual_learning dual-version"""
import asyncio

def test_imports():
    print("Testing imports...")
    from continual_learning import (
        ContinualLearningAlgorithms,
        LifelongMemorySystem,
        KnowledgeTransferSystem,
        MetaLearningSystem,
        IntegratedContinualLearningSystem,
        get_integrated_continual_learning_system,
        HAS_NUMPY,
        Task,
        ContinualLearningMethod,
    )
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    return HAS_NUMPY

async def test_continual_learning():
    print("\nTesting Continual Learning...")
    from continual_learning import get_continual_learning_algorithms, Task, ContinualLearningMethod
    from datetime import datetime
    
    cl = get_continual_learning_algorithms()
    
    task = Task(
        task_id="task1",
        name="Binary Classification",
        description="Test task",
        created_at=datetime.now(),
        task_type="classification",
        difficulty=0.5,
    )
    
    data = [(i, i % 2) for i in range(10)]
    result = await cl.learn_task(task, data, ContinualLearningMethod.EWC)
    
    print(f"  Task: {result['task_id']}")
    print(f"  Performance: {result['performance']:.2f}")
    print(f"  Method: {result['method']}")
    print(f"  ✅ Continual Learning works!")

async def test_memory():
    print("\nTesting Lifelong Memory...")
    from continual_learning import get_lifelong_memory_system, MemoryType
    
    memory_sys = get_lifelong_memory_system()
    
    mem = await memory_sys.store_memory(
        content="Test experience",
        memory_type=MemoryType.EPISODIC
    )
    
    print(f"  Memory ID: {mem.memory_id}")
    print(f"  Type: {mem.memory_type.value}")
    print(f"  Embedding dim: {len(mem.embedding)}")
    print(f"  ✅ Lifelong Memory works!")

async def test_transfer():
    print("\nTesting Knowledge Transfer...")
    from continual_learning import get_knowledge_transfer_system, TransferType
    
    transfer = get_knowledge_transfer_system()
    
    result = await transfer.transfer_knowledge(
        source_task="task1",
        target_task="task2",
        transfer_type=TransferType.FEW_SHOT
    )
    
    print(f"  Source: {result['source_task']}")
    print(f"  Target: {result['target_task']}")
    print(f"  Quality: {result['transfer_quality']:.2f}")
    print(f"  ✅ Knowledge Transfer works!")

async def test_system_status():
    print("\nTesting System Status...")
    from continual_learning import get_integrated_continual_learning_system, HAS_NUMPY
    
    system = get_integrated_continual_learning_system()
    status = system.get_system_status()
    print(f"  Implementation: {'NumPy' if HAS_NUMPY else 'Pure Python'}")
    print(f"  Tasks: {status['num_tasks']}")
    print(f"  Memories: {status['num_memories']}")
    print(f"  ✅ System works!")

def main():
    print("=" * 60)
    print("CONTINUAL LEARNING DUAL-VERSION QUICK TEST")
    print("=" * 60)
    
    has_numpy = test_imports()
    asyncio.run(test_continual_learning())
    asyncio.run(test_memory())
    asyncio.run(test_transfer())
    asyncio.run(test_system_status())
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print(f"Using: {'NumPy version' if has_numpy else 'Pure Python version'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
