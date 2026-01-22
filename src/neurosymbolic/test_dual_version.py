"""Quick test for neurosymbolic dual-version"""
import sys
import asyncio

def test_imports():
    print("Testing imports...")
    from neurosymbolic import (
        KnowledgeGraph,
        LogicTensorNetwork,
        IntegratedNeurosymbolicSystem,
        get_neurosymbolic_system,
        HAS_NUMPY,
        Triple,
    )
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    return HAS_NUMPY

async def test_knowledge_graph():
    print("\nTesting KnowledgeGraph...")
    from neurosymbolic import KnowledgeGraph, EmbeddingModel
    
    kg = KnowledgeGraph(embedding_dim=50, embedding_model=EmbeddingModel.TRANSE)
    kg.add_triple("Alice", "knows", "Bob")
    kg.add_triple("Bob", "likes", "Python")
    
    score = await kg.predict_link("Alice", "knows", "Charlie")
    print(f"  Link prediction score: {score:.4f}")
    print(f"  Stats: {kg.get_stats()}")
    print(f"  ✅ KnowledgeGraph works!")

async def test_system():
    print("\nTesting IntegratedSystem...")
    from neurosymbolic import get_neurosymbolic_system
    
    system = get_neurosymbolic_system()
    status = system.get_system_status()
    print(f"  Implementation: {status['implementation']}")
    print(f"  ✅ System works!")

def main():
    print("=" * 60)
    print("NEUROSYMBOLIC DUAL-VERSION QUICK TEST")
    print("=" * 60)
    
    has_numpy = test_imports()
    asyncio.run(test_knowledge_graph())
    asyncio.run(test_system())
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print(f"Using: {'NumPy version' if has_numpy else 'Pure Python version'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
