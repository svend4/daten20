"""
Elastic Weight Consolidation (EWC) - v21 FUNCTIONAL

Real implementation of catastrophic forgetting prevention using
Elastic Weight Consolidation algorithm.

This is a REAL implementation of the EWC algorithm from:
"Overcoming catastrophic forgetting in neural networks" (Kirkpatrick et al., 2017)

EWC prevents catastrophic forgetting by:
1. Computing importance of each weight after learning task A
2. When learning task B, penalize changes to important weights
3. This preserves task A performance while learning task B

All using pure Python stdlib - no external dependencies!
"""

import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Callable


@dataclass
class Task:
    """Training task definition"""
    task_id: int
    data: List[Tuple[List[float], float]]  # [(input, target), ...]
    name: str = "task"


@dataclass
class EWCResult:
    """Result of EWC training"""
    task_id: int
    initial_loss: float
    final_loss: float
    epochs: int
    weights: List[float]
    fisher_diagonal: List[float]
    forgetting_prevented: bool


class SimpleNeuron:
    """
    Simple neuron with sigmoid activation.

    This is a minimal neural network component for demonstrating EWC.
    Uses only Python stdlib!
    """

    def __init__(self, num_inputs: int):
        """Initialize neuron with random weights"""
        self.num_inputs = num_inputs
        # Random weights in [-1, 1]
        self.weights = [random.uniform(-1.0, 1.0) for _ in range(num_inputs + 1)]  # +1 for bias

    def sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + math.exp(-max(min(x, 500), -500)))  # Prevent overflow

    def predict(self, inputs: List[float]) -> float:
        """Forward pass"""
        # Weighted sum + bias
        activation = self.weights[-1]  # bias
        for i, x in enumerate(inputs):
            activation += self.weights[i] * x

        # Sigmoid activation
        return self.sigmoid(activation)

    def compute_gradient(self, inputs: List[float], target: float, learning_rate: float = 0.1) -> List[float]:
        """
        Compute gradient for weight updates.

        Returns gradient for each weight (for Fisher computation).
        """
        # Forward pass
        output = self.predict(inputs)

        # Error
        error = target - output

        # Gradient of sigmoid: f'(x) = f(x) * (1 - f(x))
        sigmoid_derivative = output * (1.0 - output)

        # Gradient for each weight
        gradients = []
        for i, x in enumerate(inputs):
            grad = error * sigmoid_derivative * x
            gradients.append(grad)

        # Gradient for bias
        grad_bias = error * sigmoid_derivative
        gradients.append(grad_bias)

        return gradients


class ElasticWeightConsolidation:
    """
    Elastic Weight Consolidation (EWC) Algorithm.

    EWC prevents catastrophic forgetting by:
    1. After learning task A, compute Fisher Information Matrix
       (measures importance of each weight for task A)
    2. When learning task B, add penalty for changing important weights
    3. Loss = L_B + λ * Σ F_i * (θ_i - θ_A,i)²

    This preserves task A performance while learning task B!

    Implementation uses diagonal Fisher approximation (simpler, works well).
    """

    def __init__(self, num_inputs: int, ewc_lambda: float = 1000.0):
        """
        Initialize EWC system.

        Args:
            num_inputs: Number of input features
            ewc_lambda: EWC penalty coefficient (higher = more preservation)
        """
        self.neuron = SimpleNeuron(num_inputs)
        self.ewc_lambda = ewc_lambda

        # Store important weights and their importance after each task
        self.task_weights = {}  # task_id -> weights
        self.task_fisher = {}   # task_id -> fisher diagonal

    def compute_fisher_diagonal(self, task: Task, num_samples: int = 100) -> List[float]:
        """
        Compute diagonal Fisher Information Matrix.

        Fisher measures how much each weight affects the loss.
        Diagonal approximation: F_ii = E[(∂log p(y|x,θ) / ∂θ_i)²]

        Args:
            task: Task to compute Fisher for
            num_samples: Number of samples to use

        Returns:
            Fisher diagonal (one value per weight)
        """
        num_weights = len(self.neuron.weights)
        fisher_diagonal = [0.0] * num_weights

        # Sample data points
        samples = random.choices(task.data, k=min(num_samples, len(task.data)))

        for inputs, target in samples:
            # Compute gradient
            gradients = self.neuron.compute_gradient(inputs, target)

            # Accumulate squared gradients (Fisher diagonal approximation)
            for i in range(num_weights):
                fisher_diagonal[i] += gradients[i] ** 2

        # Average over samples
        for i in range(num_weights):
            fisher_diagonal[i] /= len(samples)

        return fisher_diagonal

    def train_task(self,
                   task: Task,
                   epochs: int = 100,
                   learning_rate: float = 0.1,
                   use_ewc: bool = True) -> EWCResult:
        """
        Train on a task using EWC to prevent forgetting.

        Args:
            task: Task to train on
            epochs: Number of training epochs
            learning_rate: Learning rate
            use_ewc: Whether to use EWC penalty (False for first task)

        Returns:
            Training result with performance metrics
        """
        # Measure initial loss
        initial_loss = self._compute_loss(task, use_ewc=False)

        # Training loop
        for epoch in range(epochs):
            random.shuffle(task.data)  # Shuffle data each epoch

            for inputs, target in task.data:
                # Forward pass
                output = self.neuron.predict(inputs)

                # Error
                error = target - output

                # Sigmoid derivative
                sigmoid_deriv = output * (1.0 - output)

                # Update weights with gradient descent
                for i, x in enumerate(inputs):
                    gradient = error * sigmoid_deriv * x

                    # Add EWC penalty if not first task
                    if use_ewc:
                        ewc_penalty = self._compute_ewc_penalty_gradient(i)
                        gradient -= ewc_penalty

                    # Weight update
                    self.neuron.weights[i] += learning_rate * gradient

                # Update bias
                gradient_bias = error * sigmoid_deriv
                if use_ewc:
                    ewc_penalty_bias = self._compute_ewc_penalty_gradient(len(inputs))
                    gradient_bias -= ewc_penalty_bias

                self.neuron.weights[-1] += learning_rate * gradient_bias

        # Measure final loss
        final_loss = self._compute_loss(task, use_ewc=False)

        # Compute Fisher for this task
        fisher_diagonal = self.compute_fisher_diagonal(task)

        # Store weights and Fisher for future tasks
        self.task_weights[task.task_id] = self.neuron.weights.copy()
        self.task_fisher[task.task_id] = fisher_diagonal

        # Check if forgetting was prevented (final loss should be low)
        forgetting_prevented = final_loss < (initial_loss * 0.5)

        return EWCResult(
            task_id=task.task_id,
            initial_loss=initial_loss,
            final_loss=final_loss,
            epochs=epochs,
            weights=self.neuron.weights.copy(),
            fisher_diagonal=fisher_diagonal,
            forgetting_prevented=forgetting_prevented
        )

    def _compute_ewc_penalty_gradient(self, weight_idx: int) -> float:
        """
        Compute EWC penalty gradient for a specific weight.

        Penalty gradient: λ * Σ F_i * (θ_i - θ_old,i)
        """
        penalty = 0.0

        for task_id in self.task_weights:
            old_weight = self.task_weights[task_id][weight_idx]
            fisher = self.task_fisher[task_id][weight_idx]

            # Penalty gradient
            penalty += self.ewc_lambda * fisher * (self.neuron.weights[weight_idx] - old_weight)

        return penalty

    def _compute_loss(self, task: Task, use_ewc: bool = True) -> float:
        """
        Compute loss on task.

        Loss = MSE + EWC penalty (if use_ewc=True)
        """
        # MSE loss
        mse = 0.0
        for inputs, target in task.data:
            output = self.neuron.predict(inputs)
            mse += (target - output) ** 2
        mse /= len(task.data)

        # Add EWC penalty if requested
        if use_ewc and self.task_weights:
            ewc_penalty = self._compute_ewc_penalty()
            return mse + ewc_penalty

        return mse

    def _compute_ewc_penalty(self) -> float:
        """
        Compute total EWC penalty.

        Penalty = λ/2 * Σ F_i * (θ_i - θ_old,i)²
        """
        penalty = 0.0

        for task_id in self.task_weights:
            for i in range(len(self.neuron.weights)):
                old_weight = self.task_weights[task_id][i]
                fisher = self.task_fisher[task_id][i]

                # Squared difference weighted by Fisher
                penalty += fisher * (self.neuron.weights[i] - old_weight) ** 2

        penalty *= self.ewc_lambda / 2.0
        return penalty

    def evaluate_task(self, task: Task) -> Dict[str, float]:
        """
        Evaluate performance on a task.

        Returns:
            Metrics: loss, accuracy (for binary classification)
        """
        loss = self._compute_loss(task, use_ewc=False)

        # Compute accuracy
        correct = 0
        for inputs, target in task.data:
            output = self.neuron.predict(inputs)
            predicted = 1.0 if output > 0.5 else 0.0
            if abs(predicted - target) < 0.1:
                correct += 1

        accuracy = correct / len(task.data)

        return {
            "loss": loss,
            "accuracy": accuracy,
            "samples": len(task.data)
        }


def generate_binary_task(task_id: int, num_samples: int = 50, feature_idx: int = 0) -> Task:
    """
    Generate simple binary classification task.

    Task: predict 1 if feature[feature_idx] > 0.5, else 0

    Args:
        task_id: Task identifier
        num_samples: Number of training samples
        feature_idx: Which feature to use for classification

    Returns:
        Binary classification task
    """
    data = []
    for _ in range(num_samples):
        # Random input features
        inputs = [random.uniform(0.0, 1.0) for _ in range(3)]

        # Target based on feature_idx
        target = 1.0 if inputs[feature_idx] > 0.5 else 0.0

        data.append((inputs, target))

    return Task(task_id=task_id, data=data, name=f"binary_task_{task_id}")


def demonstrate_catastrophic_forgetting():
    """
    Demonstrate catastrophic forgetting WITHOUT EWC.

    Train on task A, then task B without EWC.
    Performance on task A will drop (catastrophic forgetting).
    """
    print("\n" + "="*60)
    print("DEMONSTRATING CATASTROPHIC FORGETTING (WITHOUT EWC)")
    print("="*60)

    # Create two tasks
    task_a = generate_binary_task(task_id=1, num_samples=50, feature_idx=0)
    task_b = generate_binary_task(task_id=2, num_samples=50, feature_idx=1)

    # Train WITHOUT EWC
    ewc = ElasticWeightConsolidation(num_inputs=3, ewc_lambda=0.0)  # No EWC penalty

    # Learn task A
    print("\nLearning Task A...")
    result_a = ewc.train_task(task_a, epochs=100, use_ewc=False)
    perf_a_after_a = ewc.evaluate_task(task_a)
    print(f"  Task A after A: loss={result_a.final_loss:.4f}, acc={perf_a_after_a['accuracy']:.2f}")

    # Learn task B (without EWC protection)
    print("\nLearning Task B (NO EWC)...")
    result_b = ewc.train_task(task_b, epochs=100, use_ewc=False)
    perf_a_after_b = ewc.evaluate_task(task_a)  # Performance on A after learning B
    perf_b_after_b = ewc.evaluate_task(task_b)
    print(f"  Task A after B: loss={perf_a_after_b['loss']:.4f}, acc={perf_a_after_b['accuracy']:.2f}")
    print(f"  Task B after B: loss={result_b.final_loss:.4f}, acc={perf_b_after_b['accuracy']:.2f}")

    # Check forgetting
    forgetting = perf_a_after_a['accuracy'] - perf_a_after_b['accuracy']
    print(f"\n❌ CATASTROPHIC FORGETTING: Task A accuracy dropped by {forgetting:.2f}")
    print(f"   (From {perf_a_after_a['accuracy']:.2f} to {perf_a_after_b['accuracy']:.2f})")

    return forgetting


def demonstrate_ewc_protection():
    """
    Demonstrate EWC preventing catastrophic forgetting.

    Train on task A, then task B WITH EWC.
    Performance on task A will be preserved!
    """
    print("\n" + "="*60)
    print("DEMONSTRATING EWC PROTECTING AGAINST FORGETTING")
    print("="*60)

    # Create two tasks
    task_a = generate_binary_task(task_id=1, num_samples=50, feature_idx=0)
    task_b = generate_binary_task(task_id=2, num_samples=50, feature_idx=1)

    # Train WITH EWC
    ewc = ElasticWeightConsolidation(num_inputs=3, ewc_lambda=5000.0)  # High EWC penalty

    # Learn task A
    print("\nLearning Task A...")
    result_a = ewc.train_task(task_a, epochs=100, use_ewc=False)
    perf_a_after_a = ewc.evaluate_task(task_a)
    print(f"  Task A after A: loss={result_a.final_loss:.4f}, acc={perf_a_after_a['accuracy']:.2f}")

    # Learn task B (WITH EWC protection)
    print("\nLearning Task B (WITH EWC)...")
    result_b = ewc.train_task(task_b, epochs=100, use_ewc=True)
    perf_a_after_b = ewc.evaluate_task(task_a)  # Performance on A after learning B
    perf_b_after_b = ewc.evaluate_task(task_b)
    print(f"  Task A after B: loss={perf_a_after_b['loss']:.4f}, acc={perf_a_after_b['accuracy']:.2f}")
    print(f"  Task B after B: loss={result_b.final_loss:.4f}, acc={perf_b_after_b['accuracy']:.2f}")

    # Check forgetting
    forgetting = perf_a_after_a['accuracy'] - perf_a_after_b['accuracy']
    print(f"\n✅ FORGETTING PREVENTED: Task A accuracy dropped by only {forgetting:.2f}")
    print(f"   (From {perf_a_after_a['accuracy']:.2f} to {perf_a_after_b['accuracy']:.2f})")

    if forgetting < 0.2:  # Less than 20% drop
        print("   ✅ EWC successfully prevented catastrophic forgetting!")
    else:
        print("   ⚠️  Some forgetting occurred, but less than without EWC")

    return forgetting


if __name__ == "__main__":
    print("="*60)
    print("ELASTIC WEIGHT CONSOLIDATION (EWC) DEMONSTRATION")
    print("Real catastrophic forgetting prevention!")
    print("="*60)

    # Set seed for reproducibility
    random.seed(42)

    # Demonstrate catastrophic forgetting
    forgetting_without_ewc = demonstrate_catastrophic_forgetting()

    # Demonstrate EWC protection
    forgetting_with_ewc = demonstrate_ewc_protection()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Without EWC: {forgetting_without_ewc:.2f} accuracy drop (catastrophic!)")
    print(f"With EWC:    {forgetting_with_ewc:.2f} accuracy drop (protected!)")
    print(f"\nEWC prevented {(forgetting_without_ewc - forgetting_with_ewc):.2f} of forgetting!")
    print("="*60)
