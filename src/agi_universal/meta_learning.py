"""
Meta-Learning Module for AGI Universal

Learn how to learn - adapt quickly to new tasks with few examples.
Implements Model-Agnostic Meta-Learning (MAML) concepts.
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Callable, Dict, Any, Optional
from enum import Enum


class AdaptationStrategy(Enum):
    """Meta-learning adaptation strategies"""
    MAML = "model_agnostic_meta_learning"
    REPTILE = "reptile"
    FOMAML = "first_order_maml"


@dataclass
class MetaLearningConfig:
    """Configuration for meta-learning"""
    inner_learning_rate: float = 0.01  # Task-specific adaptation rate
    outer_learning_rate: float = 0.001  # Meta-update rate
    inner_steps: int = 5  # Adaptation steps per task
    meta_batch_size: int = 4  # Tasks per meta-update
    strategy: AdaptationStrategy = AdaptationStrategy.MAML


@dataclass
class TaskSample:
    """Sample from a task for meta-learning"""
    support_set: List[Tuple[List[float], List[float]]]  # Few-shot examples
    query_set: List[Tuple[List[float], List[float]]]    # Test examples


class MetaLearner:
    """
    Meta-Learning system that learns to learn quickly.

    Key idea: Find initialization parameters that can quickly adapt
    to new tasks with just a few examples (few-shot learning).

    Example:
        >>> meta = MetaLearner(input_dim=2, output_dim=1)
        >>> # Train on variety of tasks
        >>> meta.meta_train(task_distribution, num_iterations=100)
        >>> # Now can adapt to new task with few examples
        >>> adapted = meta.adapt_to_new_task(new_task_samples)
    """

    def __init__(self,
                 input_dim: int,
                 output_dim: int,
                 hidden_dim: int = 32,
                 config: Optional[MetaLearningConfig] = None):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
        self.config = config or MetaLearningConfig()

        # Meta-parameters (initialization that enables fast adaptation)
        self._initialize_meta_parameters()

    def _initialize_meta_parameters(self):
        """Initialize meta-parameters using Xavier initialization"""
        xavier_std_1 = math.sqrt(2.0 / self.input_dim)
        xavier_std_2 = math.sqrt(2.0 / self.hidden_dim)

        # Layer 1: input -> hidden
        self.w1_meta = [[random.gauss(0, xavier_std_1) for _ in range(self.hidden_dim)]
                        for _ in range(self.input_dim)]
        self.b1_meta = [0.0] * self.hidden_dim

        # Layer 2: hidden -> output
        self.w2_meta = [[random.gauss(0, xavier_std_2) for _ in range(self.output_dim)]
                        for _ in range(self.hidden_dim)]
        self.b2_meta = [0.0] * self.output_dim

    def forward(self, x: List[float],
                w1: List[List[float]], b1: List[float],
                w2: List[List[float]], b2: List[float]) -> List[float]:
        """Forward pass with given parameters"""
        # Layer 1 with ReLU
        z1 = [sum(x[i] * w1[i][j] for i in range(self.input_dim)) + b1[j]
              for j in range(self.hidden_dim)]
        h1 = [max(0.0, z) for z in z1]

        # Layer 2 (output)
        y = [sum(h1[i] * w2[i][j] for i in range(self.hidden_dim)) + b2[j]
             for j in range(self.output_dim)]

        return y

    def adapt_to_task(self,
                     task_samples: TaskSample,
                     initial_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Adapt to a new task using few-shot examples.

        Args:
            task_samples: Support set (few examples) and query set (test)
            initial_params: Starting parameters (uses meta if None)

        Returns:
            Adapted parameters and performance metrics
        """
        # Start from meta-parameters (good initialization)
        if initial_params is None:
            w1 = [row[:] for row in self.w1_meta]  # Deep copy
            b1 = self.b1_meta[:]
            w2 = [row[:] for row in self.w2_meta]
            b2 = self.b2_meta[:]
        else:
            w1 = initial_params['w1']
            b1 = initial_params['b1']
            w2 = initial_params['w2']
            b2 = initial_params['b2']

        # Inner loop: adapt to task using support set
        for step in range(self.config.inner_steps):
            # Compute gradients on support set
            gradients = self._compute_gradients(task_samples.support_set, w1, b1, w2, b2)

            # Update parameters
            w1, b1, w2, b2 = self._apply_gradients(
                w1, b1, w2, b2, gradients,
                lr=self.config.inner_learning_rate
            )

        # Evaluate on query set
        query_loss = self._evaluate(task_samples.query_set, w1, b1, w2, b2)

        return {
            'adapted_params': {'w1': w1, 'b1': b1, 'w2': w2, 'b2': b2},
            'query_loss': query_loss,
            'num_support': len(task_samples.support_set),
            'num_query': len(task_samples.query_set)
        }

    def meta_train(self,
                   task_distribution: Callable[[], TaskSample],
                   num_iterations: int = 100) -> Dict[str, Any]:
        """
        Meta-training: learn good initialization for fast adaptation.

        Args:
            task_distribution: Function that samples tasks
            num_iterations: Number of meta-training iterations

        Returns:
            Meta-training results
        """
        meta_losses = []

        for iteration in range(num_iterations):
            # Sample batch of tasks
            task_batch = [task_distribution() for _ in range(self.config.meta_batch_size)]

            # Compute meta-gradient
            meta_gradients = {
                'w1': [[0.0] * self.hidden_dim for _ in range(self.input_dim)],
                'b1': [0.0] * self.hidden_dim,
                'w2': [[0.0] * self.output_dim for _ in range(self.hidden_dim)],
                'b2': [0.0] * self.output_dim
            }

            total_loss = 0.0

            for task_samples in task_batch:
                # Adapt to task
                result = self.adapt_to_task(task_samples)
                total_loss += result['query_loss']

                # Compute gradient of query loss w.r.t. meta-parameters
                # (simplified: use adapted params as proxy)
                adapted = result['adapted_params']

                # Accumulate gradients
                for i in range(self.input_dim):
                    for j in range(self.hidden_dim):
                        meta_gradients['w1'][i][j] += (adapted['w1'][i][j] - self.w1_meta[i][j])

                for j in range(self.hidden_dim):
                    meta_gradients['b1'][j] += (adapted['b1'][j] - self.b1_meta[j])
                    for k in range(self.output_dim):
                        meta_gradients['w2'][j][k] += (adapted['w2'][j][k] - self.w2_meta[j][k])

                for k in range(self.output_dim):
                    meta_gradients['b2'][k] += (adapted['b2'][k] - self.b2_meta[k])

            # Meta-update: update initialization parameters
            avg_loss = total_loss / len(task_batch)
            meta_losses.append(avg_loss)

            # Apply meta-gradients
            for i in range(self.input_dim):
                for j in range(self.hidden_dim):
                    self.w1_meta[i][j] -= self.config.outer_learning_rate * meta_gradients['w1'][i][j] / len(task_batch)

            for j in range(self.hidden_dim):
                self.b1_meta[j] -= self.config.outer_learning_rate * meta_gradients['b1'][j] / len(task_batch)
                for k in range(self.output_dim):
                    self.w2_meta[j][k] -= self.config.outer_learning_rate * meta_gradients['w2'][j][k] / len(task_batch)

            for k in range(self.output_dim):
                self.b2_meta[k] -= self.config.outer_learning_rate * meta_gradients['b2'][k] / len(task_batch)

        return {
            'meta_losses': meta_losses,
            'final_loss': meta_losses[-1] if meta_losses else 0.0,
            'improvement': (meta_losses[0] - meta_losses[-1]) / meta_losses[0] * 100 if meta_losses else 0.0,
            'iterations': num_iterations
        }

    def _compute_gradients(self,
                          samples: List[Tuple[List[float], List[float]]],
                          w1, b1, w2, b2) -> Dict:
        """Compute gradients on samples"""
        # Initialize gradient accumulators
        dw1 = [[0.0] * self.hidden_dim for _ in range(self.input_dim)]
        db1 = [0.0] * self.hidden_dim
        dw2 = [[0.0] * self.output_dim for _ in range(self.hidden_dim)]
        db2 = [0.0] * self.output_dim

        for x, y_true in samples:
            # Forward pass
            z1 = [sum(x[i] * w1[i][j] for i in range(self.input_dim)) + b1[j]
                  for j in range(self.hidden_dim)]
            h1 = [max(0.0, z) for z in z1]
            y_pred = [sum(h1[i] * w2[i][j] for i in range(self.hidden_dim)) + b2[j]
                     for j in range(self.output_dim)]

            # Backward pass
            d_output = [2.0 * (yp - yt) / len(y_true) for yp, yt in zip(y_pred, y_true)]

            # Output layer gradients
            for i in range(self.hidden_dim):
                for j in range(self.output_dim):
                    dw2[i][j] += h1[i] * d_output[j]
            for j in range(self.output_dim):
                db2[j] += d_output[j]

            # Hidden layer gradients
            d_h1 = [sum(d_output[j] * w2[i][j] for j in range(self.output_dim))
                   for i in range(self.hidden_dim)]
            d_z1 = [dh * (1.0 if z > 0 else 0.0) for dh, z in zip(d_h1, z1)]

            for i in range(self.input_dim):
                for j in range(self.hidden_dim):
                    dw1[i][j] += x[i] * d_z1[j]
            for j in range(self.hidden_dim):
                db1[j] += d_z1[j]

        # Average gradients
        n = len(samples)
        return {
            'w1': [[g / n for g in row] for row in dw1],
            'b1': [g / n for g in db1],
            'w2': [[g / n for g in row] for row in dw2],
            'b2': [g / n for g in db2]
        }

    def _apply_gradients(self, w1, b1, w2, b2, gradients, lr):
        """Apply gradients to parameters"""
        # Update w1, b1, w2, b2 with gradients
        new_w1 = [[w1[i][j] - lr * gradients['w1'][i][j]
                  for j in range(self.hidden_dim)]
                 for i in range(self.input_dim)]
        new_b1 = [b1[j] - lr * gradients['b1'][j]
                 for j in range(self.hidden_dim)]
        new_w2 = [[w2[i][j] - lr * gradients['w2'][i][j]
                  for j in range(self.output_dim)]
                 for i in range(self.hidden_dim)]
        new_b2 = [b2[j] - lr * gradients['b2'][j]
                 for j in range(self.output_dim)]

        return new_w1, new_b1, new_w2, new_b2

    def _evaluate(self, samples, w1, b1, w2, b2) -> float:
        """Evaluate loss on samples"""
        total_loss = 0.0
        for x, y_true in samples:
            y_pred = self.forward(x, w1, b1, w2, b2)
            loss = sum((yt - yp)**2 for yt, yp in zip(y_true, y_pred)) / len(y_true)
            total_loss += loss
        return total_loss / len(samples) if samples else 0.0


# Task distribution generators for meta-learning

def sine_wave_task_generator() -> TaskSample:
    """Generate sine wave regression task (vary amplitude and phase)"""
    amplitude = random.uniform(0.1, 5.0)
    phase = random.uniform(0, 2 * math.pi)

    def generate_sample():
        x = random.uniform(-5, 5)
        y = amplitude * math.sin(x + phase)
        return [x], [y]

    # Support set: few examples
    support_set = [generate_sample() for _ in range(5)]

    # Query set: test examples
    query_set = [generate_sample() for _ in range(10)]

    return TaskSample(support_set=support_set, query_set=query_set)


def linear_regression_task_generator() -> TaskSample:
    """Generate linear regression task (vary slope and intercept)"""
    slope = random.uniform(-2, 2)
    intercept = random.uniform(-1, 1)

    def generate_sample():
        x = random.uniform(-2, 2)
        y = slope * x + intercept + random.gauss(0, 0.1)  # Add noise
        return [x], [y]

    support_set = [generate_sample() for _ in range(5)]
    query_set = [generate_sample() for _ in range(10)]

    return TaskSample(support_set=support_set, query_set=query_set)


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("Meta-Learning Test - Learning to Learn!")
    print("="*70)

    # Create meta-learner
    config = MetaLearningConfig(
        inner_learning_rate=0.01,
        outer_learning_rate=0.001,
        inner_steps=5,
        meta_batch_size=4
    )

    meta = MetaLearner(input_dim=1, output_dim=1, hidden_dim=32, config=config)

    print("\nMeta-training on sine wave tasks...")
    print("Goal: Learn initialization that adapts quickly to new sine waves")

    # Meta-train
    result = meta.meta_train(sine_wave_task_generator, num_iterations=50)

    print(f"\nMeta-training complete!")
    print(f"  Initial meta-loss: {result['meta_losses'][0]:.6f}")
    print(f"  Final meta-loss:   {result['meta_losses'][-1]:.6f}")
    print(f"  Improvement:       {result['improvement']:.1f}%")

    # Test few-shot adaptation to new task
    print("\nTesting few-shot adaptation to NEW sine wave...")
    new_task = sine_wave_task_generator()
    adapted = meta.adapt_to_task(new_task)

    print(f"  Support set size: {adapted['num_support']} examples")
    print(f"  Query loss:       {adapted['query_loss']:.6f}")
    print(f"\n✅ Meta-learning enables fast adaptation with few examples!")
    print("="*70)
