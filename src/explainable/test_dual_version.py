"""Quick test for explainable dual-version"""
import sys
import asyncio

def test_imports():
    print("Testing imports...")
    from explainable import (
        IntegratedExplainableSystem,
        get_explainable_system,
        ExplanationMethod,
        HAS_NUMPY,
    )
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    return HAS_NUMPY

async def test_explainer():
    print("\nTesting Explainable System...")
    from explainable import get_explainable_system, ExplanationMethod
    
    system = get_explainable_system()
    
    # Mock model and instance
    model = lambda x: sum(x) / len(x)
    instance = [0.5, 0.3, 0.8, 0.2]
    
    # Test SHAP explanation
    explanation = await system.explain_prediction(
        model=model,
        instance=instance,
        method=ExplanationMethod.SHAP
    )
    
    print(f"  Method: {explanation.method.value}")
    print(f"  Features explained: {len(explanation.feature_importance)}")
    print(f"  Confidence: {explanation.confidence:.2f}")
    print(f"  ✅ Explainer works!")

async def test_system():
    print("\nTesting System Status...")
    from explainable import get_explainable_system
    
    system = get_explainable_system()
    status = system.get_system_status()
    print(f"  Implementation: {status['implementation']}")
    print(f"  SHAP enabled: {status['shap_enabled']}")
    print(f"  ✅ System works!")

def main():
    print("=" * 60)
    print("EXPLAINABLE DUAL-VERSION QUICK TEST")
    print("=" * 60)
    
    has_numpy = test_imports()
    asyncio.run(test_explainer())
    asyncio.run(test_system())
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print(f"Using: {'NumPy version' if has_numpy else 'Pure Python version'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
