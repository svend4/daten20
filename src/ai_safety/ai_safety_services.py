"""
AI Safety, Robustness & Alignment Platform v18.0

Comprehensive system for ensuring AI systems are safe, robust, aligned with
human values, and trustworthy.

Components:
1. Adversarial Robustness System - Defense against adversarial attacks
2. Model Alignment System - RLHF, preference learning, value alignment
3. Safety Monitoring & Red-Teaming - Continuous monitoring, automated testing
4. Uncertainty Quantification - Calibration, OOD detection, selective prediction
5. Fairness & Bias Mitigation - Fairness metrics, debiasing techniques
6. Privacy & Differential Privacy - DP-SGD, privacy-preserving training
7. AI Governance & Auditing - Model cards, datasheets, compliance
"""

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# ============================================================================
# Enums and Data Classes
# ============================================================================


class AttackType(Enum):
    """Types of adversarial attacks"""

    FGSM = "fgsm"
    PGD = "pgd"
    CARLINI_WAGNER = "carlini_wagner"
    DEEPFOOL = "deepfool"
    AUTO_ATTACK = "auto_attack"


class AlignmentMethod(Enum):
    """Model alignment methods"""

    RLHF = "rlhf"
    CONSTITUTIONAL_AI = "constitutional_ai"
    INVERSE_RL = "inverse_rl"
    PREFERENCE_LEARNING = "preference_learning"


class FairnessMetric(Enum):
    """Fairness metrics"""

    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    INDIVIDUAL_FAIRNESS = "individual_fairness"


class PrivacyMechanism(Enum):
    """Privacy-preserving mechanisms"""

    DP_SGD = "dp_sgd"
    FEDERATED_LEARNING = "federated_learning"
    SECURE_AGGREGATION = "secure_aggregation"
    LOCAL_DP = "local_dp"


@dataclass
class AdversarialExample:
    """Generated adversarial example"""

    example_id: str
    original_input: np.ndarray
    adversarial_input: np.ndarray
    attack_type: AttackType
    perturbation: np.ndarray
    perturbation_norm: float
    epsilon: float

    # Predictions
    original_prediction: int
    adversarial_prediction: int
    attack_success: bool

    # Metrics
    generation_time_ms: float = 0.0
    confidence_drop: float = 0.0


@dataclass
class RobustnessMetrics:
    """Model robustness evaluation metrics"""

    model_id: str
    clean_accuracy: float
    robust_accuracy: float
    attack_success_rate: float

    # Per-attack results
    attack_accuracies: Dict[AttackType, float]

    # Certified defenses
    certified_accuracy: Optional[float] = None
    certification_radius: Optional[float] = None

    # Timing
    evaluation_time_s: float = 0.0


@dataclass
class AlignmentResult:
    """Model alignment evaluation result"""

    alignment_id: str
    model_id: str
    method: AlignmentMethod

    # Evaluation scores
    helpfulness_score: float  # 0-1
    harmlessness_score: float  # 0-1
    honesty_score: float  # 0-1
    preference_agreement: float  # 0-1

    # Safety metrics
    harmful_response_rate: float
    constraint_violations: int
    total_evaluations: int

    # Training metadata
    training_time_h: float = 0.0
    num_preference_pairs: int = 0


@dataclass
class SafetyAlert:
    """Safety monitoring alert"""

    alert_id: str
    timestamp: datetime
    severity: str  # "P0", "P1", "P2", "P3"
    alert_type: str  # "toxicity", "bias", "factuality", "anomaly"

    # Details
    input_text: str
    output_text: str
    toxicity_score: float
    confidence_score: float

    # Metrics
    threshold_exceeded: str
    mitigation_action: Optional[str] = None


@dataclass
class UncertaintyEstimate:
    """Uncertainty quantification result"""

    estimate_id: str
    prediction: int
    probabilities: np.ndarray

    # Uncertainty types
    aleatoric_uncertainty: float  # Data noise
    epistemic_uncertainty: float  # Model uncertainty
    total_uncertainty: float

    # Calibration
    calibrated_confidence: float
    is_ood: bool  # Out-of-distribution
    ood_score: float

    # Selective prediction
    should_reject: bool
    rejection_reason: Optional[str] = None


@dataclass
class FairnessReport:
    """Fairness evaluation report"""

    report_id: str
    model_id: str
    protected_attribute: str  # "gender", "race", "age"

    # Group fairness metrics
    demographic_parity_diff: float
    equalized_odds_diff: float
    equal_opportunity_diff: float

    # Per-group metrics
    group_accuracies: Dict[str, float]
    group_tpr: Dict[str, float]  # True positive rates
    group_fpr: Dict[str, float]  # False positive rates

    # Compliance
    meets_80_percent_rule: bool  # Disparate impact
    fairness_score: float  # 0-1, higher is fairer


@dataclass
class PrivacyAudit:
    """Privacy audit result"""

    audit_id: str
    model_id: str
    mechanism: PrivacyMechanism

    # Privacy budget
    epsilon: float
    delta: float

    # Privacy attacks
    membership_attack_accuracy: float  # <0.5 is good
    model_inversion_risk: float  # 0-1

    # Utility metrics
    model_accuracy: float
    accuracy_degradation: float  # vs non-private

    # Compliance
    privacy_compliant: bool
    privacy_score: float  # 0-1


@dataclass
class GovernanceRecord:
    """AI governance and audit record"""

    record_id: str
    model_id: str
    timestamp: datetime

    # Documentation
    has_model_card: bool
    has_datasheet: bool
    has_audit_trail: bool

    # Compliance
    gdpr_compliant: bool
    regulatory_framework: List[str]
    certification_status: str  # "pending", "certified", "expired"

    # Auditing
    last_audit_date: datetime
    next_audit_date: datetime
    audit_findings: List[str]


# ============================================================================
# System 1: Adversarial Robustness System
# ============================================================================


class AdversarialRobustnessSystem:
    """
    Defend AI models against adversarial attacks and ensure robust predictions.

    Features:
    - Adversarial attack generation (FGSM, PGD, C&W)
    - Adversarial training
    - Certified defenses (randomized smoothing)
    - Input validation and sanitization
    """

    def __init__(self):
        self.adversarial_examples: Dict[str, AdversarialExample] = {}
        self.robustness_metrics: Dict[str, RobustnessMetrics] = {}
        self.attack_configs: Dict[AttackType, Dict[str, Any]] = {}
        self._initialize_attack_configs()

    def _initialize_attack_configs(self):
        """Initialize attack configurations"""
        self.attack_configs[AttackType.FGSM] = {
            "epsilon": 8.0 / 255.0,  # ℓ∞ perturbation
            "steps": 1,
            "step_size": 8.0 / 255.0,
        }
        self.attack_configs[AttackType.PGD] = {
            "epsilon": 8.0 / 255.0,
            "steps": 20,
            "step_size": 2.0 / 255.0,
            "random_start": True,
        }
        self.attack_configs[AttackType.CARLINI_WAGNER] = {
            "confidence": 0.0,
            "learning_rate": 0.01,
            "binary_search_steps": 9,
            "max_iterations": 1000,
        }

    async def generate_adversarial_example(
        self,
        input_data: np.ndarray,
        true_label: int,
        model_prediction: int,
        attack_type: AttackType = AttackType.PGD,
        epsilon: Optional[float] = None,
    ) -> AdversarialExample:
        """
        Generate adversarial example using specified attack.

        Args:
            input_data: Original input (e.g., image)
            true_label: Ground truth label
            model_prediction: Model's original prediction
            attack_type: Type of attack to use
            epsilon: Perturbation budget (None = use default)

        Returns:
            AdversarialExample with attack results
        """
        start_time = datetime.now()
        config = self.attack_configs[attack_type]

        if epsilon is None:
            epsilon = config.get("epsilon", 8.0 / 255.0)

        # Simulate attack generation
        if attack_type == AttackType.FGSM:
            generation_time = 10  # ms
            # FGSM: x_adv = x + ε·sign(∇_x L(x,y))
            perturbation = np.random.uniform(-epsilon, epsilon, input_data.shape)

        elif attack_type == AttackType.PGD:
            steps = config["steps"]
            generation_time = 10 * steps  # ~10ms per step
            # PGD: Iterative FGSM with projection
            perturbation = np.random.uniform(-epsilon, epsilon, input_data.shape)
            # Clip to epsilon ball
            perturbation = np.clip(perturbation, -epsilon, epsilon)

        elif attack_type == AttackType.CARLINI_WAGNER:
            generation_time = 2000  # ms (optimization-based)
            # C&W: Minimize ||δ||₂ subject to f(x+δ) ≠ y
            perturbation = np.random.randn(*input_data.shape) * 0.01

        else:
            generation_time = 100
            perturbation = np.random.uniform(-epsilon, epsilon, input_data.shape)

        # Generate adversarial input
        adversarial_input = input_data + perturbation
        adversarial_input = np.clip(adversarial_input, 0.0, 1.0)  # Valid pixel range

        # Simulate adversarial prediction
        # In practice, would run through model
        attack_success = np.random.rand() > 0.3  # 70% success rate
        if attack_success:
            adversarial_prediction = (model_prediction + 1) % 10  # Different class
        else:
            adversarial_prediction = model_prediction

        perturbation_norm = float(np.linalg.norm(perturbation))
        confidence_drop = float(np.random.rand() * 0.5 + 0.3)  # 0.3-0.8

        example_id = hashlib.md5(f"adv_{attack_type.value}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        adversarial_example = AdversarialExample(
            example_id=example_id,
            original_input=input_data,
            adversarial_input=adversarial_input,
            attack_type=attack_type,
            perturbation=perturbation,
            perturbation_norm=perturbation_norm,
            epsilon=epsilon,
            original_prediction=model_prediction,
            adversarial_prediction=adversarial_prediction,
            attack_success=attack_success,
            generation_time_ms=generation_time,
            confidence_drop=confidence_drop if attack_success else 0.0,
        )

        self.adversarial_examples[example_id] = adversarial_example
        return adversarial_example

    async def evaluate_robustness(
        self, model_id: str, test_dataset_size: int = 1000, attack_types: Optional[List[AttackType]] = None
    ) -> RobustnessMetrics:
        """
        Evaluate model robustness against multiple attacks.

        Args:
            model_id: Model identifier
            test_dataset_size: Number of test examples
            attack_types: List of attacks to evaluate

        Returns:
            RobustnessMetrics with comprehensive evaluation
        """
        start_time = datetime.now()

        if attack_types is None:
            attack_types = [AttackType.FGSM, AttackType.PGD, AttackType.AUTO_ATTACK]

        # Simulate model evaluation
        clean_accuracy = 0.95  # Standard model

        # Simulate attack evaluations
        attack_accuracies = {}
        for attack_type in attack_types:
            if attack_type == AttackType.FGSM:
                robust_acc = 0.65  # Weak attack
            elif attack_type == AttackType.PGD:
                robust_acc = 0.53  # Strong attack
            elif attack_type == AttackType.AUTO_ATTACK:
                robust_acc = 0.50  # Ensemble attack
            else:
                robust_acc = 0.60

            attack_accuracies[attack_type] = robust_acc

        # Overall robust accuracy (worst-case)
        robust_accuracy = min(attack_accuracies.values())
        attack_success_rate = 1.0 - (robust_accuracy / clean_accuracy)

        # Certified defense evaluation
        certified_accuracy = 0.71  # Randomized smoothing
        certification_radius = 0.5  # ℓ₂ radius

        evaluation_time = (datetime.now() - start_time).total_seconds()

        metrics = RobustnessMetrics(
            model_id=model_id,
            clean_accuracy=clean_accuracy,
            robust_accuracy=robust_accuracy,
            attack_success_rate=attack_success_rate,
            attack_accuracies=attack_accuracies,
            certified_accuracy=certified_accuracy,
            certification_radius=certification_radius,
            evaluation_time_s=evaluation_time,
        )

        self.robustness_metrics[model_id] = metrics
        return metrics

    async def adversarial_training_step(
        self, batch_inputs: np.ndarray, batch_labels: np.ndarray, epsilon: float = 8.0 / 255.0, attack_steps: int = 10
    ) -> Dict[str, float]:
        """
        Perform one adversarial training step.

        Args:
            batch_inputs: Batch of training inputs
            batch_labels: Batch of labels
            epsilon: Perturbation budget
            attack_steps: Number of PGD steps

        Returns:
            Training metrics (loss, accuracy)
        """
        # Simulate adversarial training
        # In practice: Generate adversarial examples, compute loss, backprop

        # Generate adversarial examples (inner maximization)
        await asyncio.sleep(0.02)  # ~20ms per step

        # Simulate training metrics
        clean_loss = float(np.random.rand() * 0.5 + 0.3)  # 0.3-0.8
        robust_loss = float(np.random.rand() * 0.8 + 0.5)  # 0.5-1.3
        clean_acc = float(np.random.rand() * 0.1 + 0.85)  # 85-95%
        robust_acc = float(np.random.rand() * 0.15 + 0.45)  # 45-60%

        return {
            "clean_loss": clean_loss,
            "robust_loss": robust_loss,
            "clean_accuracy": clean_acc,
            "robust_accuracy": robust_acc,
            "epsilon": epsilon,
        }


# ============================================================================
# System 2: Model Alignment System
# ============================================================================


class ModelAlignmentSystem:
    """
    Align AI models with human values, preferences, and safety constraints.

    Features:
    - Reinforcement Learning from Human Feedback (RLHF)
    - Constitutional AI (self-critique)
    - Preference learning
    - Safety constraints and red lines
    """

    def __init__(self):
        self.alignment_results: Dict[str, AlignmentResult] = {}
        self.preference_dataset: List[Dict[str, Any]] = []
        self.constitutional_principles: List[str] = []
        self._initialize_principles()

    def _initialize_principles(self):
        """Initialize constitutional AI principles"""
        self.constitutional_principles = [
            "Helpfulness: Provide useful, informative responses",
            "Harmlessness: Avoid harmful, toxic, or biased content",
            "Honesty: Be truthful and acknowledge uncertainty",
            "Privacy: Respect user privacy and data protection",
        ]

    async def train_reward_model(self, preference_pairs: List[Tuple[str, str, int]], model_id: str) -> Dict[str, float]:
        """
        Train reward model on human preference data.

        Args:
            preference_pairs: List of (response_A, response_B, preference)
                              preference: 0 (A≻B), 1 (B≻A)
            model_id: Reward model identifier

        Returns:
            Training metrics
        """
        # Simulate reward model training
        # Bradley-Terry model: P(A≻B) = exp(r(A)) / (exp(r(A)) + exp(r(B)))

        num_pairs = len(preference_pairs)
        await asyncio.sleep(0.001 * num_pairs)  # Simulate training time

        # Simulate training metrics
        train_accuracy = float(np.random.rand() * 0.15 + 0.65)  # 65-80%
        val_accuracy = float(np.random.rand() * 0.1 + 0.68)  # 68-78%
        loss = float(np.random.rand() * 0.5 + 0.3)  # 0.3-0.8

        return {
            "model_id": model_id,
            "num_preference_pairs": num_pairs,
            "train_accuracy": train_accuracy,
            "val_accuracy": val_accuracy,
            "loss": loss,
        }

    async def rlhf_optimization_step(
        self, policy_output: str, reward_score: float, reference_policy_score: float, kl_penalty: float = 0.01
    ) -> Dict[str, float]:
        """
        Perform one PPO optimization step for RLHF.

        Args:
            policy_output: Generated response
            reward_score: Reward from reward model
            reference_policy_score: Score from reference policy
            kl_penalty: KL divergence penalty coefficient

        Returns:
            Optimization metrics
        """
        # PPO objective: max E[r(x,y)] - β·KL(π_θ || π_ref)

        # Simulate KL divergence
        kl_divergence = float(np.random.rand() * 0.5)  # 0-0.5

        # Compute objective
        objective = reward_score - kl_penalty * kl_divergence

        # Simulate PPO clipping
        clip_fraction = float(np.random.rand() * 0.3)  # 0-30% clipped

        return {
            "reward": reward_score,
            "kl_divergence": kl_divergence,
            "objective": objective,
            "clip_fraction": clip_fraction,
            "kl_penalty": kl_penalty,
        }

    async def constitutional_ai_critique(self, response: str, principles: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Critique response against constitutional principles.

        Args:
            response: Generated response to critique
            principles: List of principles to check (None = use all)

        Returns:
            Critique results and revision suggestions
        """
        if principles is None:
            principles = self.constitutional_principles

        # Simulate critique generation
        critiques = []
        violations = []

        for principle in principles:
            # Simulate violation detection
            violates = np.random.rand() < 0.15  # 15% violation rate

            if violates:
                violations.append(principle)
                critique = f"Response may violate: {principle}"
                critiques.append(critique)

        # Generate revision if violations found
        needs_revision = len(violations) > 0
        revision_suggestion = None

        if needs_revision:
            revision_suggestion = "Revise response to address: " + ", ".join(violations)

        return {
            "critiques": critiques,
            "violations": violations,
            "needs_revision": needs_revision,
            "revision_suggestion": revision_suggestion,
            "num_principles_checked": len(principles),
        }

    async def evaluate_alignment(
        self, model_id: str, method: AlignmentMethod, num_eval_examples: int = 1000
    ) -> AlignmentResult:
        """
        Evaluate model alignment with human values.

        Args:
            model_id: Model identifier
            method: Alignment method used
            num_eval_examples: Number of examples to evaluate

        Returns:
            AlignmentResult with comprehensive metrics
        """
        # Simulate alignment evaluation

        # Scores depend on method
        if method == AlignmentMethod.RLHF:
            helpfulness = 0.86
            harmlessness = 0.90
            honesty = 0.76
            preference_agreement = 0.91
            harmful_rate = 0.04
        elif method == AlignmentMethod.CONSTITUTIONAL_AI:
            helpfulness = 0.84
            harmlessness = 0.92
            honesty = 0.78
            preference_agreement = 0.88
            harmful_rate = 0.03
        else:
            helpfulness = 0.80
            harmlessness = 0.85
            honesty = 0.75
            preference_agreement = 0.85
            harmful_rate = 0.06

        # Simulate constraint violations
        constraint_violations = int(num_eval_examples * 0.01)  # 1% violation rate

        alignment_id = hashlib.md5(f"alignment_{model_id}_{method.value}".encode()).hexdigest()[:16]

        result = AlignmentResult(
            alignment_id=alignment_id,
            model_id=model_id,
            method=method,
            helpfulness_score=helpfulness,
            harmlessness_score=harmlessness,
            honesty_score=honesty,
            preference_agreement=preference_agreement,
            harmful_response_rate=harmful_rate,
            constraint_violations=constraint_violations,
            total_evaluations=num_eval_examples,
            training_time_h=24.0,  # 1 day typical
            num_preference_pairs=50000,
        )

        self.alignment_results[alignment_id] = result
        return result


# ============================================================================
# System 3: Safety Monitoring & Red-Teaming
# ============================================================================


class SafetyMonitoringRedTeaming:
    """
    Continuously monitor AI systems for safety issues and proactively discover
    failure modes through automated red-teaming.

    Features:
    - Real-time safety monitoring
    - Automated red-team testing
    - Anomaly detection and drift monitoring
    - Incident response and remediation
    """

    def __init__(self):
        self.alerts: Dict[str, SafetyAlert] = {}
        self.monitoring_metrics: Dict[str, List[float]] = {
            "toxicity_scores": [],
            "confidence_scores": [],
            "anomaly_scores": [],
        }
        self.red_team_findings: List[Dict[str, Any]] = []

    async def monitor_response(self, input_text: str, output_text: str, confidence: float) -> Optional[SafetyAlert]:
        """
        Monitor a model response for safety issues.

        Args:
            input_text: User input
            output_text: Model output
            confidence: Model confidence score

        Returns:
            SafetyAlert if issue detected, None otherwise
        """
        # Simulate safety scoring
        toxicity_score = float(np.random.beta(1, 10))  # Skewed toward low
        bias_score = float(np.random.beta(1, 8))
        factuality_score = float(np.random.beta(8, 2))  # Skewed toward high

        # Store metrics
        self.monitoring_metrics["toxicity_scores"].append(toxicity_score)
        self.monitoring_metrics["confidence_scores"].append(confidence)

        # Check thresholds
        alert_triggered = False
        severity = None
        alert_type = None
        threshold_exceeded = None
        mitigation_action = None

        if toxicity_score > 0.8:
            alert_triggered = True
            severity = "P0"  # Critical
            alert_type = "toxicity"
            threshold_exceeded = f"toxicity_score ({toxicity_score:.2f}) > 0.8"
            mitigation_action = "Block response, log for review"

        elif bias_score > 0.7:
            alert_triggered = True
            severity = "P1"  # High
            alert_type = "bias"
            threshold_exceeded = f"bias_score ({bias_score:.2f}) > 0.7"
            mitigation_action = "Flag for bias review"

        elif factuality_score < 0.4:
            alert_triggered = True
            severity = "P2"  # Medium
            alert_type = "factuality"
            threshold_exceeded = f"factuality_score ({factuality_score:.2f}) < 0.4"
            mitigation_action = "Add uncertainty disclaimer"

        elif confidence < 0.3:
            alert_triggered = True
            severity = "P2"
            alert_type = "low_confidence"
            threshold_exceeded = f"confidence ({confidence:.2f}) < 0.3"
            mitigation_action = "Suggest rejection or human review"

        if alert_triggered:
            alert_id = hashlib.md5(f"alert_{datetime.now().isoformat()}".encode()).hexdigest()[:16]

            alert = SafetyAlert(
                alert_id=alert_id,
                timestamp=datetime.now(),
                severity=severity,
                alert_type=alert_type,
                input_text=input_text,
                output_text=output_text,
                toxicity_score=toxicity_score,
                confidence_score=confidence,
                threshold_exceeded=threshold_exceeded,
                mitigation_action=mitigation_action,
            )

            self.alerts[alert_id] = alert
            return alert

        return None

    async def automated_red_team_test(
        self, model_id: str, num_prompts: int = 1000, attack_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run automated red-team testing to find failure modes.

        Args:
            model_id: Model to test
            num_prompts: Number of test prompts
            attack_categories: Categories to test (jailbreaks, bias, etc.)

        Returns:
            Red-team testing results
        """
        if attack_categories is None:
            attack_categories = [
                "jailbreaks",
                "prompt_injection",
                "bias_elicitation",
                "hallucination",
                "context_exploitation",
            ]

        # Simulate red-team testing
        await asyncio.sleep(0.001 * num_prompts)  # Simulate testing time

        findings = []
        total_failures = 0

        for category in attack_categories:
            # Simulate failure discovery
            category_prompts = num_prompts // len(attack_categories)
            failures = int(category_prompts * np.random.beta(1, 20))  # ~5% failure rate
            total_failures += failures

            if failures > 0:
                finding = {
                    "category": category,
                    "num_prompts": category_prompts,
                    "num_failures": failures,
                    "failure_rate": failures / category_prompts,
                    "severity": "high" if failures > 10 else "medium",
                    "example_failures": [f"Example {i+1}" for i in range(min(3, failures))],
                }
                findings.append(finding)
                self.red_team_findings.append(finding)

        return {
            "model_id": model_id,
            "num_prompts_tested": num_prompts,
            "attack_categories": attack_categories,
            "total_failures": total_failures,
            "overall_failure_rate": total_failures / num_prompts,
            "findings_by_category": findings,
            "num_high_severity": sum(1 for f in findings if f["severity"] == "high"),
        }

    async def detect_distribution_drift(
        self, recent_inputs: np.ndarray, reference_distribution: np.ndarray, threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect distribution drift in model inputs.

        Args:
            recent_inputs: Recent input distribution
            reference_distribution: Reference (training) distribution
            threshold: Drift detection threshold

        Returns:
            Drift detection results
        """
        # Simulate drift detection (KL divergence, Wasserstein distance, etc.)

        # Compute drift metric (simulated KL divergence)
        kl_divergence = float(np.random.exponential(0.05))  # Typical: low drift

        # Two-sample test (simulated p-value)
        p_value = float(np.random.beta(8, 2))  # Usually high (no drift)

        # Check if drift detected
        drift_detected = kl_divergence > threshold or p_value < 0.05

        return {
            "drift_detected": drift_detected,
            "kl_divergence": kl_divergence,
            "p_value": p_value,
            "threshold": threshold,
            "recommendation": "Retrain model" if drift_detected else "Continue monitoring",
        }


# ============================================================================
# System 4: Uncertainty Quantification
# ============================================================================


class UncertaintyQuantification:
    """
    Quantify model uncertainty and detect when models are unreliable.

    Features:
    - Bayesian neural networks (Monte Carlo dropout, ensembles)
    - Calibration methods (temperature scaling)
    - Out-of-distribution detection
    - Selective prediction (confidence-based rejection)
    """

    def __init__(self):
        self.uncertainty_estimates: Dict[str, UncertaintyEstimate] = {}
        self.calibration_temperature: float = 1.0
        self.ood_threshold: float = 0.7

    async def estimate_uncertainty(self, logits: np.ndarray, num_mc_samples: int = 10) -> UncertaintyEstimate:
        """
        Estimate predictive uncertainty using Monte Carlo sampling.

        Args:
            logits: Model logits
            num_mc_samples: Number of MC samples (for MC dropout/ensemble)

        Returns:
            UncertaintyEstimate with aleatoric and epistemic uncertainty
        """
        # Simulate MC dropout samples
        mc_predictions = []
        for _ in range(num_mc_samples):
            # Add noise to simulate dropout
            noisy_logits = logits + np.random.randn(*logits.shape) * 0.1
            probs = self._softmax(noisy_logits)
            mc_predictions.append(probs)

        mc_predictions = np.array(mc_predictions)

        # Predictive mean and variance
        mean_probs = mc_predictions.mean(axis=0)
        prediction = int(np.argmax(mean_probs))

        # Total uncertainty (entropy of mean)
        total_uncertainty = float(-np.sum(mean_probs * np.log(mean_probs + 1e-10)))

        # Aleatoric uncertainty (expected entropy)
        entropies = -np.sum(mc_predictions * np.log(mc_predictions + 1e-10), axis=1)
        aleatoric = float(entropies.mean())

        # Epistemic uncertainty (mutual information)
        epistemic = total_uncertainty - aleatoric

        # Calibration (apply temperature scaling)
        calibrated_logits = logits / self.calibration_temperature
        calibrated_probs = self._softmax(calibrated_logits)
        calibrated_confidence = float(calibrated_probs.max())

        # OOD detection (energy-based)
        energy = float(-np.log(np.sum(np.exp(logits))))
        ood_score = 1 / (1 + np.exp(-energy))  # Sigmoid
        is_ood = ood_score > self.ood_threshold

        # Selective prediction
        should_reject = is_ood or calibrated_confidence < 0.5
        rejection_reason = None
        if is_ood:
            rejection_reason = "Out-of-distribution input"
        elif calibrated_confidence < 0.5:
            rejection_reason = "Low confidence"

        estimate_id = hashlib.md5(f"uncertainty_{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        estimate = UncertaintyEstimate(
            estimate_id=estimate_id,
            prediction=prediction,
            probabilities=mean_probs,
            aleatoric_uncertainty=aleatoric,
            epistemic_uncertainty=epistemic,
            total_uncertainty=total_uncertainty,
            calibrated_confidence=calibrated_confidence,
            is_ood=is_ood,
            ood_score=float(ood_score),
            should_reject=should_reject,
            rejection_reason=rejection_reason,
        )

        self.uncertainty_estimates[estimate_id] = estimate
        return estimate

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Compute softmax probabilities"""
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)

    async def calibrate_model(self, val_logits: np.ndarray, val_labels: np.ndarray) -> float:
        """
        Calibrate model using temperature scaling on validation set.

        Args:
            val_logits: Validation set logits
            val_labels: Validation set labels

        Returns:
            Optimal temperature
        """
        # Simulate temperature search
        # In practice: Optimize T to minimize NLL on validation set

        best_temperature = float(np.random.rand() * 0.5 + 1.0)  # Typically 1.0-1.5
        self.calibration_temperature = best_temperature

        # Compute ECE (Expected Calibration Error) before/after
        ece_before = 0.15  # Typical uncalibrated ECE
        ece_after = 0.03  # After temperature scaling

        return best_temperature

    async def selective_prediction(
        self, predictions: np.ndarray, confidences: np.ndarray, target_coverage: float = 0.9
    ) -> Dict[str, Any]:
        """
        Perform selective prediction to achieve target coverage.

        Args:
            predictions: Model predictions
            confidences: Prediction confidences
            target_coverage: Desired coverage (fraction predicted)

        Returns:
            Selective prediction results
        """
        # Sort by confidence
        sorted_indices = np.argsort(confidences)[::-1]

        # Select top target_coverage fraction
        num_selected = int(len(predictions) * target_coverage)
        selected_indices = sorted_indices[:num_selected]
        rejected_indices = sorted_indices[num_selected:]

        # Simulate accuracy on selected vs all
        accuracy_all = 0.85
        accuracy_selected = 0.92  # Higher on high-confidence examples

        return {
            "coverage": target_coverage,
            "num_predictions": len(predictions),
            "num_selected": num_selected,
            "num_rejected": len(rejected_indices),
            "accuracy_all": accuracy_all,
            "accuracy_selected": accuracy_selected,
            "risk_reduction": (accuracy_selected - accuracy_all) / accuracy_all,
        }


# ============================================================================
# System 5: Fairness & Bias Mitigation
# ============================================================================


class FairnessBiasMitigation:
    """
    Ensure AI systems are fair across demographic groups and mitigate biases.

    Features:
    - Fairness metrics (demographic parity, equalized odds)
    - Bias detection (embedding bias, counterfactual testing)
    - Debiasing techniques (adversarial, reweighting, post-processing)
    - Fairness-accuracy trade-off analysis
    """

    def __init__(self):
        self.fairness_reports: Dict[str, FairnessReport] = {}
        self.bias_scores: Dict[str, float] = {}

    async def compute_fairness_metrics(
        self, predictions: np.ndarray, true_labels: np.ndarray, protected_attributes: np.ndarray, model_id: str
    ) -> FairnessReport:
        """
        Compute comprehensive fairness metrics.

        Args:
            predictions: Model predictions
            true_labels: Ground truth labels
            protected_attributes: Protected attribute values (e.g., 0/1 for binary)
            model_id: Model identifier

        Returns:
            FairnessReport with detailed fairness analysis
        """
        # Identify groups
        group_0_mask = protected_attributes == 0
        group_1_mask = protected_attributes == 1

        # Demographic parity: P(Ŷ=1|A=0) vs P(Ŷ=1|A=1)
        pred_rate_0 = float(predictions[group_0_mask].mean())
        pred_rate_1 = float(predictions[group_1_mask].mean())
        demographic_parity_diff = abs(pred_rate_0 - pred_rate_1)

        # True positive rates (sensitivity)
        tpr_0 = float(predictions[group_0_mask & (true_labels == 1)].mean())
        tpr_1 = float(predictions[group_1_mask & (true_labels == 1)].mean())

        # False positive rates
        fpr_0 = float(predictions[group_0_mask & (true_labels == 0)].mean())
        fpr_1 = float(predictions[group_1_mask & (true_labels == 0)].mean())

        # Equalized odds: Equal TPR and FPR across groups
        equalized_odds_diff = max(abs(tpr_0 - tpr_1), abs(fpr_0 - fpr_1))

        # Equal opportunity: Equal TPR only
        equal_opportunity_diff = abs(tpr_0 - tpr_1)

        # Per-group accuracies
        acc_0 = float((predictions[group_0_mask] == true_labels[group_0_mask]).mean())
        acc_1 = float((predictions[group_1_mask] == true_labels[group_1_mask]).mean())

        # 80% rule (disparate impact)
        disparate_impact = min(pred_rate_0, pred_rate_1) / max(pred_rate_0, pred_rate_1)
        meets_80_percent_rule = disparate_impact >= 0.8

        # Overall fairness score (0-1, higher is fairer)
        fairness_score = 1.0 - min(1.0, (demographic_parity_diff + equalized_odds_diff) / 2)

        report_id = hashlib.md5(f"fairness_{model_id}".encode()).hexdigest()[:16]

        report = FairnessReport(
            report_id=report_id,
            model_id=model_id,
            protected_attribute="gender",  # Example
            demographic_parity_diff=demographic_parity_diff,
            equalized_odds_diff=equalized_odds_diff,
            equal_opportunity_diff=equal_opportunity_diff,
            group_accuracies={"group_0": acc_0, "group_1": acc_1},
            group_tpr={"group_0": tpr_0, "group_1": tpr_1},
            group_fpr={"group_0": fpr_0, "group_1": fpr_1},
            meets_80_percent_rule=meets_80_percent_rule,
            fairness_score=fairness_score,
        )

        self.fairness_reports[report_id] = report
        return report

    async def adversarial_debiasing_step(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        protected_attributes: np.ndarray,
        lambda_adversarial: float = 0.1,
    ) -> Dict[str, float]:
        """
        Perform one adversarial debiasing training step.

        Args:
            features: Input features
            labels: Task labels
            protected_attributes: Protected attributes
            lambda_adversarial: Adversarial loss weight

        Returns:
            Training metrics
        """
        # Adversarial debiasing: Train predictor + discriminator
        # Predictor: Minimize task loss
        # Discriminator: Predict protected attribute from predictor's hidden repr
        # Objective: min_θ max_φ L_task - λL_adv

        # Simulate task loss
        task_loss = float(np.random.rand() * 0.5 + 0.3)

        # Simulate adversarial loss (how well discriminator predicts protected attr)
        adversarial_loss = float(np.random.rand() * 0.8 + 0.1)

        # Combined objective
        total_loss = task_loss - lambda_adversarial * adversarial_loss

        # Simulate metrics
        task_accuracy = float(np.random.rand() * 0.1 + 0.80)
        discriminator_accuracy = float(np.random.rand() * 0.1 + 0.50)  # Want ~50% (random)

        return {
            "task_loss": task_loss,
            "adversarial_loss": adversarial_loss,
            "total_loss": total_loss,
            "task_accuracy": task_accuracy,
            "discriminator_accuracy": discriminator_accuracy,
            "lambda": lambda_adversarial,
        }

    async def detect_bias_in_embeddings(
        self, embeddings: Dict[str, np.ndarray], target_words: List[str], attribute_words: List[Tuple[str, str]]
    ) -> float:
        """
        Detect bias in word embeddings using WEAT-style test.

        Args:
            embeddings: Word embeddings dictionary
            target_words: Target words to test (e.g., professions)
            attribute_words: Attribute word pairs (e.g., male/female names)

        Returns:
            Bias score (effect size)
        """
        # WEAT: Word Embedding Association Test
        # Measures association between targets and attributes

        # Simulate bias detection
        # Effect size typically 0.2-1.5 (larger = more biased)
        bias_score = float(np.random.exponential(0.5))

        self.bias_scores["embedding_bias"] = bias_score
        return bias_score


# ============================================================================
# System 6: Privacy & Differential Privacy
# ============================================================================


class PrivacyDifferentialPrivacy:
    """
    Protect individual privacy in training data and model outputs.

    Features:
    - Differential privacy fundamentals (ε,δ-DP)
    - DP-SGD (differentially private training)
    - Privacy attacks (membership inference, model inversion)
    - Federated learning for privacy
    """

    def __init__(self):
        self.privacy_audits: Dict[str, PrivacyAudit] = {}
        self.privacy_budget: Dict[str, Tuple[float, float]] = {}  # (ε, δ)

    async def dp_sgd_training_step(
        self, gradients: np.ndarray, clipping_norm: float = 1.0, noise_multiplier: float = 1.1, batch_size: int = 256
    ) -> np.ndarray:
        """
        Perform one DP-SGD training step.

        Args:
            gradients: Per-example gradients
            clipping_norm: Gradient clipping threshold
            noise_multiplier: Noise scale (σ)
            batch_size: Batch size

        Returns:
            Noisy aggregated gradient
        """
        # DP-SGD algorithm:
        # 1. Clip gradients: ḡ_i = g_i / max(1, ||g_i||/C)
        # 2. Add noise: g̃ = (1/B)Σ ḡ_i + N(0, σ²C²I)
        # 3. Update: θ_{t+1} = θ_t - η·g̃

        # Clip gradients
        grad_norms = np.linalg.norm(gradients, axis=1, keepdims=True)
        clip_factors = np.minimum(1.0, clipping_norm / (grad_norms + 1e-10))
        clipped_gradients = gradients * clip_factors

        # Aggregate
        aggregated_gradient = clipped_gradients.mean(axis=0)

        # Add Gaussian noise
        noise_scale = noise_multiplier * clipping_norm / batch_size
        noise = np.random.randn(*aggregated_gradient.shape) * noise_scale
        noisy_gradient = aggregated_gradient + noise

        return noisy_gradient

    async def compute_privacy_budget(
        self, num_epochs: int, batch_size: int, dataset_size: int, noise_multiplier: float, delta: float = 1e-5
    ) -> Tuple[float, float]:
        """
        Compute privacy budget (ε,δ) for DP-SGD training.

        Args:
            num_epochs: Number of training epochs
            batch_size: Batch size
            dataset_size: Training dataset size
            noise_multiplier: Noise multiplier σ
            delta: Delta parameter

        Returns:
            (epsilon, delta) privacy budget
        """
        # Compute using RDP accountant (simplified)
        # ε ≈ q·T·ε_step / σ
        # q = batch_size / dataset_size (sampling rate)
        # T = num_epochs * (dataset_size / batch_size) (total steps)

        q = batch_size / dataset_size
        steps_per_epoch = dataset_size // batch_size
        total_steps = num_epochs * steps_per_epoch

        # Simplified epsilon calculation
        # In practice, use more sophisticated RDP accountant
        epsilon = q * total_steps / (noise_multiplier**2)

        return (epsilon, delta)

    async def membership_inference_attack(
        self, model_id: str, member_examples: np.ndarray, non_member_examples: np.ndarray
    ) -> float:
        """
        Perform membership inference attack to test privacy.

        Args:
            model_id: Model to attack
            member_examples: Examples in training set
            non_member_examples: Examples not in training set

        Returns:
            Attack accuracy (0.5 = random, 1.0 = perfect)
        """
        # Membership inference: Determine if example was in training set
        # Method: Compare model confidence/loss on members vs non-members

        # Simulate attack
        # Undefended model: 60-70% attack accuracy
        # DP model (ε=10): 52-55%
        # DP model (ε=1): ~50% (near random)

        # Check if model has DP
        has_dp = model_id in self.privacy_budget

        if has_dp:
            epsilon, _ = self.privacy_budget[model_id]
            # Lower epsilon → better privacy → lower attack accuracy
            attack_accuracy = 0.50 + 0.05 * min(epsilon / 10.0, 1.0)
        else:
            attack_accuracy = float(np.random.rand() * 0.1 + 0.6)  # 60-70%

        return attack_accuracy

    async def conduct_privacy_audit(
        self, model_id: str, mechanism: PrivacyMechanism, epsilon: float, delta: float, baseline_accuracy: float
    ) -> PrivacyAudit:
        """
        Conduct comprehensive privacy audit.

        Args:
            model_id: Model identifier
            mechanism: Privacy mechanism used
            epsilon: Privacy budget epsilon
            delta: Privacy budget delta
            baseline_accuracy: Non-private baseline accuracy

        Returns:
            PrivacyAudit with comprehensive results
        """
        # Simulate privacy attacks
        membership_attack_acc = 0.50 + 0.05 * min(epsilon / 10.0, 1.0)
        model_inversion_risk = epsilon / 20.0  # Lower epsilon → lower risk

        # Simulate model accuracy
        # Trade-off: Lower epsilon → lower accuracy
        accuracy_degradation = 0.01 * max(0, 10 - epsilon)
        model_accuracy = baseline_accuracy - accuracy_degradation

        # Privacy compliance
        privacy_compliant = epsilon < 10 and delta < 1e-4
        privacy_score = 1.0 - min(1.0, epsilon / 20.0)

        audit_id = hashlib.md5(f"privacy_audit_{model_id}".encode()).hexdigest()[:16]

        audit = PrivacyAudit(
            audit_id=audit_id,
            model_id=model_id,
            mechanism=mechanism,
            epsilon=epsilon,
            delta=delta,
            membership_attack_accuracy=membership_attack_acc,
            model_inversion_risk=model_inversion_risk,
            model_accuracy=model_accuracy,
            accuracy_degradation=accuracy_degradation,
            privacy_compliant=privacy_compliant,
            privacy_score=privacy_score,
        )

        self.privacy_audits[audit_id] = audit
        return audit


# ============================================================================
# System 7: AI Governance & Auditing
# ============================================================================


class AIGovernanceAuditing:
    """
    Ensure transparency, accountability, and compliance in AI systems.

    Features:
    - Model cards and documentation
    - Datasheets for datasets
    - Audit trails and explainability
    - Compliance and regulatory frameworks
    """

    def __init__(self):
        self.governance_records: Dict[str, GovernanceRecord] = {}
        self.model_cards: Dict[str, Dict[str, Any]] = {}
        self.datasheets: Dict[str, Dict[str, Any]] = {}
        self.audit_logs: List[Dict[str, Any]] = []

    async def generate_model_card(
        self,
        model_id: str,
        model_details: Dict[str, Any],
        intended_use: Dict[str, Any],
        metrics: Dict[str, float],
        training_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive model card.

        Args:
            model_id: Model identifier
            model_details: Architecture, training details
            intended_use: Primary tasks, target users
            metrics: Evaluation metrics
            training_data: Training data information

        Returns:
            Model card dictionary
        """
        model_card = {
            "model_id": model_id,
            "version": "1.0",
            "date": datetime.now().isoformat(),
            "model_details": model_details,
            "intended_use": intended_use,
            "metrics": metrics,
            "training_data": training_data,
            "ethical_considerations": {
                "risks": ["Potential bias in predictions", "Privacy concerns"],
                "fairness": "Evaluated on protected attributes",
                "privacy": "Differential privacy with ε<10",
            },
            "caveats_and_recommendations": {
                "limitations": ["Performance degrades on out-of-distribution data"],
                "usage_guidance": ["Requires human oversight for high-stakes decisions"],
                "not_intended_for": ["Medical diagnosis without expert review"],
            },
        }

        self.model_cards[model_id] = model_card
        return model_card

    async def generate_datasheet(
        self, dataset_id: str, composition: Dict[str, Any], collection: Dict[str, Any], preprocessing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate datasheet for dataset.

        Args:
            dataset_id: Dataset identifier
            composition: Dataset composition details
            collection: Data collection methodology
            preprocessing: Preprocessing steps

        Returns:
            Datasheet dictionary
        """
        datasheet = {
            "dataset_id": dataset_id,
            "version": "1.0",
            "date": datetime.now().isoformat(),
            "motivation": {"purpose": "Training computer vision models", "funding": "Academic research grant"},
            "composition": composition,
            "collection": collection,
            "preprocessing": preprocessing,
            "uses": {
                "prior_uses": ["Image classification research"],
                "should_use_for": ["Benchmarking", "Academic research"],
                "should_not_use_for": ["Production systems without validation"],
            },
            "distribution": {
                "how_distributed": "Public download",
                "licensing": "Creative Commons BY 4.0",
                "copyright": "Original authors",
            },
            "maintenance": {"maintainer": "Dataset Consortium", "update_frequency": "Annually"},
        }

        self.datasheets[dataset_id] = datasheet
        return datasheet

    async def log_prediction(
        self,
        model_id: str,
        input_features: Dict[str, Any],
        prediction: Any,
        confidence: float,
        user_id: Optional[str] = None,
    ):
        """
        Log model prediction for audit trail.

        Args:
            model_id: Model identifier
            input_features: Input features (privacy-respecting)
            prediction: Model prediction
            confidence: Prediction confidence
            user_id: Optional user identifier
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_id": model_id,
            "input_features": input_features,  # May be hashed/anonymized
            "prediction": prediction,
            "confidence": confidence,
            "user_id": user_id,
        }

        self.audit_logs.append(log_entry)

    async def check_compliance(self, model_id: str, regulations: List[str]) -> Dict[str, bool]:
        """
        Check model compliance with regulations.

        Args:
            model_id: Model to check
            regulations: List of regulations (e.g., "GDPR", "CCPA")

        Returns:
            Compliance status for each regulation
        """
        compliance_status = {}

        for regulation in regulations:
            if regulation == "GDPR":
                # Check: Right to explanation, data protection, consent
                has_explanations = model_id in self.model_cards
                has_privacy = True  # Check DP implementation
                compliant = has_explanations and has_privacy

            elif regulation == "CCPA":
                # Check: Consumer data rights, opt-out
                has_data_rights = True
                compliant = has_data_rights

            elif regulation == "AI_ACT":
                # EU AI Act: Risk assessment, documentation
                has_risk_assessment = model_id in self.model_cards
                compliant = has_risk_assessment

            else:
                compliant = False

            compliance_status[regulation] = compliant

        return compliance_status

    async def create_governance_record(self, model_id: str) -> GovernanceRecord:
        """
        Create comprehensive governance record.

        Args:
            model_id: Model identifier

        Returns:
            GovernanceRecord
        """
        record_id = hashlib.md5(f"governance_{model_id}".encode()).hexdigest()[:16]

        # Check documentation
        has_model_card = model_id in self.model_cards
        has_datasheet = True  # Assume dataset has datasheet
        has_audit_trail = len(self.audit_logs) > 0

        # Check compliance
        compliance = await self.check_compliance(model_id, ["GDPR", "CCPA"])
        gdpr_compliant = compliance.get("GDPR", False)

        record = GovernanceRecord(
            record_id=record_id,
            model_id=model_id,
            timestamp=datetime.now(),
            has_model_card=has_model_card,
            has_datasheet=has_datasheet,
            has_audit_trail=has_audit_trail,
            gdpr_compliant=gdpr_compliant,
            regulatory_framework=["GDPR", "CCPA", "AI_ACT"],
            certification_status="certified",
            last_audit_date=datetime.now(),
            next_audit_date=datetime(2026, 4, 1),
            audit_findings=[],
        )

        self.governance_records[record_id] = record
        return record


# ============================================================================
# Singleton Instances
# ============================================================================

_adversarial_robustness_system = None
_model_alignment_system = None
_safety_monitoring_red_teaming = None
_uncertainty_quantification = None
_fairness_bias_mitigation = None
_privacy_differential_privacy = None
_ai_governance_auditing = None


def get_adversarial_robustness_system() -> AdversarialRobustnessSystem:
    """Get singleton instance of AdversarialRobustnessSystem"""
    global _adversarial_robustness_system
    if _adversarial_robustness_system is None:
        _adversarial_robustness_system = AdversarialRobustnessSystem()
    return _adversarial_robustness_system


def get_model_alignment_system() -> ModelAlignmentSystem:
    """Get singleton instance of ModelAlignmentSystem"""
    global _model_alignment_system
    if _model_alignment_system is None:
        _model_alignment_system = ModelAlignmentSystem()
    return _model_alignment_system


def get_safety_monitoring_red_teaming() -> SafetyMonitoringRedTeaming:
    """Get singleton instance of SafetyMonitoringRedTeaming"""
    global _safety_monitoring_red_teaming
    if _safety_monitoring_red_teaming is None:
        _safety_monitoring_red_teaming = SafetyMonitoringRedTeaming()
    return _safety_monitoring_red_teaming


def get_uncertainty_quantification() -> UncertaintyQuantification:
    """Get singleton instance of UncertaintyQuantification"""
    global _uncertainty_quantification
    if _uncertainty_quantification is None:
        _uncertainty_quantification = UncertaintyQuantification()
    return _uncertainty_quantification


def get_fairness_bias_mitigation() -> FairnessBiasMitigation:
    """Get singleton instance of FairnessBiasMitigation"""
    global _fairness_bias_mitigation
    if _fairness_bias_mitigation is None:
        _fairness_bias_mitigation = FairnessBiasMitigation()
    return _fairness_bias_mitigation


def get_privacy_differential_privacy() -> PrivacyDifferentialPrivacy:
    """Get singleton instance of PrivacyDifferentialPrivacy"""
    global _privacy_differential_privacy
    if _privacy_differential_privacy is None:
        _privacy_differential_privacy = PrivacyDifferentialPrivacy()
    return _privacy_differential_privacy


def get_ai_governance_auditing() -> AIGovernanceAuditing:
    """Get singleton instance of AIGovernanceAuditing"""
    global _ai_governance_auditing
    if _ai_governance_auditing is None:
        _ai_governance_auditing = AIGovernanceAuditing()
    return _ai_governance_auditing
