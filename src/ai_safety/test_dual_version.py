"""Quick test for AI Safety dual-version"""
import sys
import asyncio

def test_imports():
    print("Testing imports...")
    from ai_safety import (
        AdversarialRobustnessSystem,
        ModelAlignmentSystem,
        SafetyMonitoringRedTeaming,
        UncertaintyQuantification,
        FairnessBiasMitigation,
        PrivacyDifferentialPrivacy,
        AIGovernanceAuditing,
        IntegratedAISafetySystem,
        get_ai_safety_system,
        HAS_NUMPY,
        AttackType,
        AlignmentMethod,
    )
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    return HAS_NUMPY

async def test_adversarial_robustness():
    print("\nTesting Adversarial Robustness...")
    from ai_safety import get_adversarial_robustness_system, AttackType
    
    robustness = get_adversarial_robustness_system()
    
    # Mock input data
    input_data = [0.5, 0.3, 0.8, 0.2]
    
    # Generate adversarial example
    adv_example = await robustness.generate_adversarial_example(
        input_data=input_data,
        true_label=5,
        model_prediction=5,
        attack_type=AttackType.PGD,
    )
    
    print(f"  Attack type: {adv_example.attack_type.value}")
    print(f"  Attack success: {adv_example.attack_success}")
    print(f"  Perturbation norm: {adv_example.perturbation_norm:.4f}")
    print(f"  ✅ Adversarial Robustness works!")

async def test_model_alignment():
    print("\nTesting Model Alignment...")
    from ai_safety import get_model_alignment_system
    
    alignment = get_model_alignment_system()
    
    # Mock preference pairs
    preference_pairs = [
        ("response_a", "response_b", 1),
        ("response_c", "response_d", 0),
    ]
    
    # Train with RLHF
    result = await alignment.train_with_rlhf(
        model_id="test_model",
        preference_pairs=preference_pairs,
        num_epochs=3
    )
    
    print(f"  Helpfulness: {result.helpfulness_score:.2f}")
    print(f"  Harmlessness: {result.harmlessness_score:.2f}")
    print(f"  Honesty: {result.honesty_score:.2f}")
    print(f"  ✅ Model Alignment works!")

async def test_uncertainty_quantification():
    print("\nTesting Uncertainty Quantification...")
    from ai_safety import get_uncertainty_quantification
    
    uncertainty = get_uncertainty_quantification()
    
    # Mock probabilities
    probabilities = [0.1, 0.2, 0.6, 0.1]
    input_data = [0.5, 0.3, 0.8, 0.2]
    
    # Estimate uncertainty
    estimate = await uncertainty.estimate_uncertainty(
        probabilities=probabilities,
        input_data=input_data
    )
    
    print(f"  Prediction: {estimate.prediction}")
    print(f"  Total uncertainty: {estimate.total_uncertainty:.4f}")
    print(f"  Is OOD: {estimate.is_ood}")
    print(f"  ✅ Uncertainty Quantification works!")

async def test_system_status():
    print("\nTesting System Status...")
    from ai_safety import get_ai_safety_system, HAS_NUMPY
    
    system = get_ai_safety_system()
    status = system.get_system_status()
    print(f"  Implementation: {status['implementation']}")
    print(f"  Robustness enabled: {status['robustness_enabled']}")
    print(f"  Alignment enabled: {status['alignment_enabled']}")
    print(f"  ✅ System works!")

def main():
    print("=" * 60)
    print("AI SAFETY DUAL-VERSION QUICK TEST")
    print("=" * 60)
    
    has_numpy = test_imports()
    asyncio.run(test_adversarial_robustness())
    asyncio.run(test_model_alignment())
    asyncio.run(test_uncertainty_quantification())
    asyncio.run(test_system_status())
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print(f"Using: {'NumPy version' if has_numpy else 'Pure Python version'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
