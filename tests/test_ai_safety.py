"""
Comprehensive Test Suite for AI Safety Platform (v18.0)

Tests all 7 subsystems and integrated system:
1. AdversarialRobustnessSystem - Attack generation & defense
2. ModelAlignmentSystem - RLHF & constitutional AI
3. SafetyMonitoringRedTeaming - Continuous monitoring
4. UncertaintyQuantification - OOD detection
5. FairnessBiasMitigation - Fairness metrics & mitigation
6. PrivacyDifferentialPrivacy - DP-SGD training
7. AIGovernanceAuditing - Model cards & compliance
8. IntegratedAISafetySystem - Unified integration

Total: 46 tests
"""

import asyncio
import numpy as np
import pytest
from datetime import datetime

from src.ai_safety import (
    # Enums
    AttackType,
    AlignmentMethod,
    FairnessMetric,
    PrivacyMechanism,
    # Data Classes
    AISafetyConfig,
    # Service Classes
    AdversarialRobustnessSystem,
    ModelAlignmentSystem,
    SafetyMonitoringRedTeaming,
    UncertaintyQuantification,
    FairnessBiasMitigation,
    PrivacyDifferentialPrivacy,
    AIGovernanceAuditing,
    # Integrated System
    IntegratedAISafetySystem,
    get_ai_safety_system,
)


# Test AI Safety subsystems and integrated system
class TestAdversarialRobustnessSystem:
    """Test Adversarial Robustness subsystem"""

    @pytest.mark.asyncio
    async def test_generate_fgsm_attack(self):
        robustness = AdversarialRobustnessSystem()
        image = np.random.randn(224, 224, 3)

        adv_example = await robustness.generate_adversarial_example(
            input_data=image,
            true_label=5,
            model_prediction=5,
            attack_type=AttackType.FGSM,
        )

        assert adv_example is not None
        assert adv_example.attack_type == AttackType.FGSM
        assert adv_example.perturbation_norm >= 0

    @pytest.mark.asyncio
    async def test_generate_pgd_attack(self):
        robustness = AdversarialRobustnessSystem()
        image = np.random.randn(224, 224, 3)

        adv_example = await robustness.generate_adversarial_example(
            input_data=image,
            true_label=3,
            model_prediction=3,
            attack_type=AttackType.PGD,
        )

        assert adv_example.attack_type == AttackType.PGD

    @pytest.mark.asyncio
    async def test_evaluate_robustness(self):
        robustness = AdversarialRobustnessSystem()

        metrics = await robustness.evaluate_robustness(
            model_id="test_model",
            test_dataset_size=100,
        )

        assert metrics is not None
        assert 0 <= metrics.certified_accuracy <= 1.0

    @pytest.mark.asyncio
    async def test_defend_adversarial(self):
        robustness = AdversarialRobustnessSystem()
        adv_input = np.random.randn(224, 224, 3)

        result = await robustness.defend_adversarial(
            adversarial_input=adv_input,
            defense_method="adversarial_training",
        )

        assert result is not None


class TestModelAlignmentSystem:
    """Test Model Alignment subsystem"""

    @pytest.mark.asyncio
    async def test_rlhf_alignment(self):
        alignment = ModelAlignmentSystem()

        result = await alignment.align_model(
            model_id="alignment_model",
            alignment_method=AlignmentMethod.RLHF,
            human_feedback={"quality": 0.8, "safety": 0.9},
        )

        assert result is not None
        assert result.alignment_method == AlignmentMethod.RLHF
        assert 0 <= result.alignment_score <= 1.0

    @pytest.mark.asyncio
    async def test_constitutional_ai(self):
        alignment = ModelAlignmentSystem()

        result = await alignment.align_model(
            model_id="constitutional_model",
            alignment_method=AlignmentMethod.CONSTITUTIONAL_AI,
            human_feedback={"constraints": ["harmless", "helpful", "honest"]},
        )

        assert result.alignment_method == AlignmentMethod.CONSTITUTIONAL_AI

    @pytest.mark.asyncio
    async def test_verify_alignment(self):
        alignment = ModelAlignmentSystem()

        verification = await alignment.verify_alignment(
            model_id="verify_model",
            test_scenarios=["safety", "honesty", "helpfulness"],
        )

        assert verification is not None


class TestSafetyMonitoringRedTeaming:
    """Test Safety Monitoring & Red Teaming subsystem"""

    @pytest.mark.asyncio
    async def test_start_monitoring(self):
        monitoring = SafetyMonitoringRedTeaming()

        result = await monitoring.start_monitoring(
            model_id="monitored_model",
            monitoring_interval_sec=60,
        )

        assert result.get("status") == "success"
        assert "monitoring_id" in result

    @pytest.mark.asyncio
    async def test_conduct_red_team_test(self):
        monitoring = SafetyMonitoringRedTeaming()

        result = await monitoring.conduct_red_team_test(
            model_id="redteam_model",
            attack_scenarios=["adversarial_prompts", "jailbreak_attempts"],
        )

        assert result is not None
        assert "safety_score" in result

    @pytest.mark.asyncio
    async def test_detect_safety_violation(self):
        monitoring = SafetyMonitoringRedTeaming()

        alert = await monitoring.detect_safety_violation(
            model_id="violation_model",
            model_output="unsafe output",
        )

        assert alert is not None


class TestUncertaintyQuantification:
    """Test Uncertainty Quantification subsystem"""

    @pytest.mark.asyncio
    async def test_quantify_uncertainty(self):
        uncertainty = UncertaintyQuantification()
        input_data = np.random.randn(10, 224, 224, 3)

        estimate = await uncertainty.quantify_uncertainty(
            model_id="uncertain_model",
            input_data=input_data,
            method="mc_dropout",
        )

        assert estimate is not None
        assert estimate.epistemic_uncertainty >= 0
        assert estimate.aleatoric_uncertainty >= 0

    @pytest.mark.asyncio
    async def test_detect_ood(self):
        uncertainty = UncertaintyQuantification()
        input_data = np.random.randn(224, 224, 3)

        is_ood = await uncertainty.detect_out_of_distribution(
            model_id="ood_model",
            input_data=input_data,
        )

        assert isinstance(is_ood, bool)


class TestFairnessBiasMitigation:
    """Test Fairness & Bias Mitigation subsystem"""

    @pytest.mark.asyncio
    async def test_compute_fairness_metrics(self):
        fairness = FairnessBiasMitigation()
        test_data = {
            "features": np.random.randn(100, 10),
            "labels": np.random.randint(0, 2, 100),
            "sensitive": np.random.randint(0, 2, 100),
        }

        report = await fairness.compute_fairness_metrics(
            model_id="fairness_model",
            test_data=test_data,
            sensitive_attributes=["gender", "race"],
        )

        assert report is not None
        assert report.max_disparity >= 0

    @pytest.mark.asyncio
    async def test_mitigate_bias(self):
        fairness = FairnessBiasMitigation()

        result = await fairness.mitigate_bias(
            model_id="bias_model",
            mitigation_strategy="reweighting",
            protected_attributes=["gender"],
        )

        assert result is not None


class TestPrivacyDifferentialPrivacy:
    """Test Privacy & Differential Privacy subsystem"""

    @pytest.mark.asyncio
    async def test_apply_differential_privacy(self):
        privacy = PrivacyDifferentialPrivacy()

        result = await privacy.apply_differential_privacy(
            model_id="private_model",
            training_data_size=10000,
            epsilon=1.0,
            delta=1e-5,
        )

        assert result is not None
        assert result.privacy_budget == 1.0

    @pytest.mark.asyncio
    async def test_audit_privacy(self):
        privacy = PrivacyDifferentialPrivacy()

        audit = await privacy.audit_privacy(
            model_id="audit_model",
            training_data_size=10000,
        )

        assert audit is not None
        assert isinstance(audit.is_private, bool)


class TestAIGovernanceAuditing:
    """Test AI Governance & Auditing subsystem"""

    @pytest.mark.asyncio
    async def test_create_model_card(self):
        governance = AIGovernanceAuditing()

        card = await governance.create_model_card(
            model_id="governed_model",
            model_type="classifier",
            intended_use="Production deployment",
            training_data="Internal dataset",
        )

        assert card is not None
        assert card.model_id == "governed_model"

    @pytest.mark.asyncio
    async def test_audit_compliance(self):
        governance = AIGovernanceAuditing()

        result = await governance.audit_compliance(
            model_id="compliance_model",
            regulatory_framework="GDPR",
        )

        assert result is not None


class TestIntegratedAISafetySystem:
    """Test Integrated AI Safety System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = AISafetyConfig(
            enable_adversarial_robustness=True,
            enable_alignment=True,
            enable_fairness=True,
        )

        system = IntegratedAISafetySystem(config)
        assert system.adversarial_robustness is not None
        assert system.alignment is not None
        assert system.fairness is not None

    @pytest.mark.asyncio
    async def test_comprehensive_safety_audit(self):
        system = IntegratedAISafetySystem()
        test_data = np.random.randn(100, 10)

        audit = await system.comprehensive_safety_audit(
            model_id="audit_test_model",
            test_data=test_data,
        )

        assert audit is not None
        assert "overall_safety_score" in audit
        assert 0 <= audit["overall_safety_score"] <= 1.0
        assert "subsystem_scores" in audit

    @pytest.mark.asyncio
    async def test_adversarial_stress_test(self):
        system = IntegratedAISafetySystem()
        input_data = np.random.randn(224, 224, 3)

        result = await system.adversarial_stress_test(
            model_id="stress_model",
            input_data=input_data,
            attack_types=[AttackType.FGSM, AttackType.PGD],
        )

        assert result is not None
        assert "overall_robustness" in result
        assert result["attacks_tested"] == 2

    @pytest.mark.asyncio
    async def test_align_with_human_values(self):
        system = IntegratedAISafetySystem()

        result = await system.align_with_human_values(
            model_id="values_model",
            human_feedback={"quality": 0.8},
            value_constraints=["harmless", "helpful"],
        )

        assert result is not None
        assert "alignment_score" in result
        assert "alignment_methods_applied" in result

    @pytest.mark.asyncio
    async def test_deploy_with_safety_monitoring(self):
        system = IntegratedAISafetySystem()

        result = await system.deploy_with_safety_monitoring(
            model_id="deploy_model",
            deployment_environment="production",
        )

        assert result is not None
        assert result["monitoring_enabled"] is True

    @pytest.mark.asyncio
    async def test_enforce_fairness_constraints(self):
        system = IntegratedAISafetySystem()
        test_data = {
            "features": np.random.randn(100, 10),
            "labels": np.random.randint(0, 2, 100),
        }

        result = await system.enforce_fairness_constraints(
            model_id="fair_model",
            test_data=test_data,
            protected_attributes=["gender", "race"],
            fairness_threshold=0.1,
        )

        assert result is not None
        assert "fairness_achieved" in result

    @pytest.mark.asyncio
    async def test_privacy_preserving_training(self):
        system = IntegratedAISafetySystem()

        result = await system.privacy_preserving_training(
            model_id="private_train_model",
            training_data_size=10000,
            epsilon=1.0,
        )

        assert result is not None
        assert result["epsilon"] == 1.0
        assert "privacy_audit_passed" in result

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedAISafetySystem()
        status = system.get_system_status()

        assert status is not None
        assert "adversarial_robustness_enabled" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedAISafetySystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_ai_safety_system()
        system2 = get_ai_safety_system()

        assert system1 is system2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
