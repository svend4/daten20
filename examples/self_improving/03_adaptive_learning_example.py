"""
Example 3: Adaptive Learning Rate Scheduling

Demonstrates all 7 learning rate schedules and adaptive momentum control.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

import random
from src.self_improving import (
    AdaptiveLearningController,
    AdaptiveMomentumController,
    LRScheduleType,
)


def simulate_training_with_schedule(controller: AdaptiveLearningController,
                                   schedule_name: str,
                                   num_steps: int = 100):
    """Simulate training with a specific LR schedule"""

    print(f"\n{schedule_name}")
    print("-" * 60)

    # Sample learning rates at different steps
    sample_steps = [0, 10, 25, 50, 75, 90, 99]

    print(f"Initial LR: {controller.base_lr:.6f}")

    for step in range(num_steps):
        # Simulate performance (generally improving)
        performance = 0.5 + (step / num_steps) * 0.4 + random.gauss(0, 0.05)
        performance = max(0.0, min(1.0, performance))

        # Step with performance feedback
        controller.step(performance_metric=performance)

        # Print samples
        if step in sample_steps:
            current_lr = controller.get_current_lr()
            print(f"  Step {step:3d}: LR={current_lr:.6f}, Performance={performance:.4f}")

    final_lr = controller.get_current_lr()
    print(f"Final LR: {final_lr:.6f}")

    return controller


def main():
    print("=" * 60)
    print("Self-Improving AI v24.0 - Adaptive Learning Rate")
    print("=" * 60)

    base_lr = 0.01
    num_steps = 100

    # Test all 7 schedule types
    print("\n[1] Learning Rate Schedules Overview")
    print("=" * 60)

    schedules = [
        (LRScheduleType.CONSTANT, "1. CONSTANT - Fixed learning rate"),
        (LRScheduleType.STEP_DECAY, "2. STEP DECAY - Drops at intervals"),
        (LRScheduleType.EXPONENTIAL, "3. EXPONENTIAL - Smooth exponential decay"),
        (LRScheduleType.COSINE_ANNEALING, "4. COSINE ANNEALING - Smooth cosine curve"),
        (LRScheduleType.LINEAR, "5. LINEAR - Linear decrease"),
        (LRScheduleType.POLYNOMIAL, "6. POLYNOMIAL - Polynomial decay"),
        (LRScheduleType.ADAPTIVE, "7. ADAPTIVE - Performance-based adjustment"),
    ]

    for schedule_type, description in schedules:
        print(f"{description}")

    # Detailed examples for each schedule
    print("\n" + "=" * 60)
    print("[2] Schedule Demonstrations")
    print("=" * 60)

    # 1. Constant Schedule
    print("\n[2.1] CONSTANT SCHEDULE")
    controller_constant = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.CONSTANT,
        total_steps=num_steps
    )
    simulate_training_with_schedule(controller_constant, "Constant LR", num_steps)

    # 2. Step Decay Schedule
    print("\n[2.2] STEP DECAY SCHEDULE")
    controller_step = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.STEP_DECAY,
        total_steps=num_steps,
        step_size=20,  # Drop every 20 steps
        gamma=0.5      # Multiply by 0.5 at each drop
    )
    simulate_training_with_schedule(controller_step, "Step Decay (every 20 steps, γ=0.5)", num_steps)

    # 3. Exponential Decay
    print("\n[2.3] EXPONENTIAL DECAY SCHEDULE")
    controller_exp = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.EXPONENTIAL,
        total_steps=num_steps,
        gamma=0.95  # Decay factor per step
    )
    simulate_training_with_schedule(controller_exp, "Exponential Decay (γ=0.95)", num_steps)

    # 4. Cosine Annealing
    print("\n[2.4] COSINE ANNEALING SCHEDULE")
    controller_cosine = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.COSINE_ANNEALING,
        total_steps=num_steps,
        min_lr=0.0001
    )
    simulate_training_with_schedule(controller_cosine, "Cosine Annealing (min_lr=0.0001)", num_steps)

    # 5. Linear Schedule
    print("\n[2.5] LINEAR SCHEDULE")
    controller_linear = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.LINEAR,
        total_steps=num_steps,
        final_lr=0.001
    )
    simulate_training_with_schedule(controller_linear, "Linear Decay (final_lr=0.001)", num_steps)

    # 6. Polynomial Schedule
    print("\n[2.6] POLYNOMIAL SCHEDULE")
    controller_poly = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.POLYNOMIAL,
        total_steps=num_steps,
        power=2.0
    )
    simulate_training_with_schedule(controller_poly, "Polynomial Decay (power=2.0)", num_steps)

    # 7. Adaptive Schedule (Performance-based)
    print("\n[2.7] ADAPTIVE SCHEDULE (Performance-Based)")
    controller_adaptive = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.ADAPTIVE,
        total_steps=num_steps,
        adaptation_rate=0.1
    )
    simulate_training_with_schedule(controller_adaptive, "Adaptive (performance-based)", num_steps)

    # Warmup demonstration
    print("\n" + "=" * 60)
    print("[3] Warmup Phase Demonstration")
    print("=" * 60)

    controller_warmup = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.COSINE_ANNEALING,
        total_steps=num_steps,
        warmup_steps=20
    )

    print("\nCosine Annealing with 20-step warmup:")
    print("-" * 60)

    warmup_sample_steps = [0, 5, 10, 15, 20, 30, 50, 99]

    for step in range(num_steps):
        controller_warmup.step()

        if step in warmup_sample_steps:
            current_lr = controller_warmup.get_current_lr()
            phase = "WARMUP" if step < 20 else "NORMAL"
            print(f"  Step {step:3d}: LR={current_lr:.6f} [{phase}]")

    # Plateau handling
    print("\n" + "=" * 60)
    print("[4] Plateau Handling")
    print("=" * 60)

    controller_plateau = AdaptiveLearningController(
        base_lr=base_lr,
        schedule_type=LRScheduleType.ADAPTIVE,
        total_steps=200,
        patience=10  # Wait 10 steps before reducing LR
    )

    print("\nAdaptive schedule with plateau detection:")
    print("-" * 60)

    # Simulate plateau (performance stops improving)
    plateau_performance = 0.85

    for step in range(50):
        # Performance plateaus after step 20
        if step < 20:
            performance = 0.5 + (step / 20) * 0.35
        else:
            performance = plateau_performance + random.gauss(0, 0.01)

        controller_plateau.step(performance_metric=performance)

        if step in [10, 20, 25, 30, 35, 40]:
            current_lr = controller_plateau.get_current_lr()
            print(f"  Step {step:2d}: LR={current_lr:.6f}, Perf={performance:.4f}")

    print(f"\nNote: LR reduced when performance plateaued around step 30")

    # Adaptive Momentum
    print("\n" + "=" * 60)
    print("[5] Adaptive Momentum Control")
    print("=" * 60)

    momentum_controller = AdaptiveMomentumController(
        base_momentum=0.9,
        adaptation_rate=0.05
    )

    print("\nAdaptive momentum based on gradient variance:")
    print("-" * 60)

    for step in range(50):
        # Simulate gradient with varying variance
        if step < 20:
            # High variance (noisy gradients)
            gradient_variance = 0.5
        else:
            # Low variance (stable gradients)
            gradient_variance = 0.1

        momentum_controller.update(gradient_variance)

        if step in [0, 10, 20, 30, 40, 49]:
            current_momentum = momentum_controller.get_current_momentum()
            print(f"  Step {step:2d}: Momentum={current_momentum:.4f}, "
                  f"Gradient Variance={gradient_variance:.4f}")

    print(f"\nNote: Momentum increased when gradients became more stable")

    # Best Practices
    print("\n" + "=" * 60)
    print("[6] Schedule Selection Guidelines")
    print("=" * 60)

    print("""
**When to use each schedule:**

1. CONSTANT
   - Short training runs
   - Already tuned learning rate
   - Simple baseline experiments

2. STEP DECAY
   - Traditional training paradigm
   - When you want discrete LR drops
   - Example: Drop LR every 30 epochs

3. EXPONENTIAL
   - Smooth, continuous decay
   - Long training runs
   - Natural decay behavior

4. COSINE ANNEALING
   - State-of-the-art for many tasks
   - Smooth convergence
   - Popular in transformers/ResNets
   - Recommended default

5. LINEAR
   - Simple, predictable decay
   - Fine-tuning scenarios
   - When you want to reach specific final LR

6. POLYNOMIAL
   - Flexible decay rate (via power parameter)
   - Fast initial decay, slower later
   - Good for RL applications

7. ADAPTIVE
   - Automated tuning
   - When performance plateaus
   - Research/exploratory training
   - Requires performance metric

**General Tips:**
- Use warmup (5-10% of total steps) for stability
- Cosine annealing works well for most tasks
- Adaptive is good when you're unsure
- Monitor LR during training
- Combine with momentum adaptation for best results
    """)

    print("\n✓ Adaptive learning rate example complete!")


if __name__ == "__main__":
    main()
