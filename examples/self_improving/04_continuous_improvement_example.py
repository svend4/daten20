"""
Example 4: Continuous Improvement Orchestration

Demonstrates the full continuous improvement cycle with monitoring,
analysis, optimization, and self-improvement.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

import time
import random
from src.self_improving import (
    ContinuousImprovementOrchestrator,
    get_global_orchestrator,
)


def training_component(learning_rate: float = 0.01):
    """Simulate training component"""
    # Simulate work
    time.sleep(0.05 + random.uniform(0, 0.02))

    # Simulate loss (improves with better LR)
    optimal_lr = 0.01
    lr_quality = 1.0 - abs(learning_rate - optimal_lr) / optimal_lr
    loss = 0.5 * (1.0 - lr_quality * 0.5) + random.gauss(0, 0.05)

    return loss


def inference_component(batch_size: int = 32):
    """Simulate inference component"""
    # Larger batches are faster per sample
    time_per_sample = 0.001 * (40 / batch_size)
    time.sleep(time_per_sample * batch_size)

    throughput = batch_size / (time_per_sample * batch_size)
    return throughput


def main():
    print("=" * 60)
    print("Self-Improving AI v24.0 - Continuous Improvement")
    print("=" * 60)

    # Get global orchestrator
    print("\n[1] Initializing Continuous Improvement Orchestrator...")
    orchestrator = get_global_orchestrator()

    print(f"Orchestrator initialized: {orchestrator is not None}")
    print(f"Improvement cycle phases: 5 (Monitor → Analyze → Optimize → Validate → Adapt)")

    # Initial baseline performance
    print("\n[2] Measuring Baseline Performance")
    print("=" * 60)

    print("\nRunning initial performance tests...")

    # Test with default parameters
    baseline_lr = 0.02  # Suboptimal
    baseline_batch_size = 16  # Suboptimal

    baseline_results = {
        'training_loss': [],
        'inference_throughput': []
    }

    for i in range(5):
        loss = training_component(learning_rate=baseline_lr)
        throughput = inference_component(batch_size=baseline_batch_size)

        baseline_results['training_loss'].append(loss)
        baseline_results['inference_throughput'].append(throughput)

    avg_baseline_loss = sum(baseline_results['training_loss']) / len(baseline_results['training_loss'])
    avg_baseline_throughput = sum(baseline_results['inference_throughput']) / len(baseline_results['inference_throughput'])

    print(f"\nBaseline Results:")
    print(f"  Training Loss: {avg_baseline_loss:.4f}")
    print(f"  Inference Throughput: {avg_baseline_throughput:.2f} samples/sec")
    print(f"  Learning Rate: {baseline_lr}")
    print(f"  Batch Size: {baseline_batch_size}")

    # Run improvement cycle
    print("\n" + "=" * 60)
    print("[3] Running Continuous Improvement Cycle")
    print("=" * 60)

    # Cycle 1: Initial improvement
    print("\n[3.1] Improvement Cycle #1")
    print("-" * 60)

    result1 = orchestrator.run_improvement_cycle(
        enable_profiling=True,
        enable_adaptive_lr=True
    )

    print(f"\nCycle Results:")
    print(f"  Status: {result1['status']}")
    print(f"  Cycle number: {result1['cycle_number']}")
    print(f"  Improvements found: {result1['improvements_found']}")

    if 'recommendations' in result1:
        print(f"\nRecommendations ({len(result1['recommendations'])} total):")
        for i, rec in enumerate(result1['recommendations'][:3], 1):
            print(f"    {i}. {rec}")

    # Apply improvements and test
    if result1['improvements_found'] > 0:
        print("\n  Applying improvements...")

        # Simulate applying recommendations
        improved_lr = 0.01  # Closer to optimal
        improved_batch_size = 32  # Better batch size

        improved_results = {
            'training_loss': [],
            'inference_throughput': []
        }

        for i in range(5):
            loss = training_component(learning_rate=improved_lr)
            throughput = inference_component(batch_size=improved_batch_size)

            improved_results['training_loss'].append(loss)
            improved_results['inference_throughput'].append(throughput)

        avg_improved_loss = sum(improved_results['training_loss']) / len(improved_results['training_loss'])
        avg_improved_throughput = sum(improved_results['inference_throughput']) / len(improved_results['inference_throughput'])

        print(f"\n  Improved Results:")
        print(f"    Training Loss: {avg_improved_loss:.4f} (was {avg_baseline_loss:.4f})")
        print(f"    Inference Throughput: {avg_improved_throughput:.2f} (was {avg_baseline_throughput:.2f})")

        loss_improvement = ((avg_baseline_loss - avg_improved_loss) / avg_baseline_loss) * 100
        throughput_improvement = ((avg_improved_throughput - avg_baseline_throughput) / avg_baseline_throughput) * 100

        print(f"\n  Improvement:")
        print(f"    Loss: {loss_improvement:.1f}% better")
        print(f"    Throughput: {throughput_improvement:.1f}% better")

    # Cycle 2: Further optimization
    print("\n[3.2] Improvement Cycle #2")
    print("-" * 60)

    result2 = orchestrator.run_improvement_cycle(
        enable_profiling=True,
        enable_adaptive_lr=True
    )

    print(f"\nCycle Results:")
    print(f"  Status: {result2['status']}")
    print(f"  Cycle number: {result2['cycle_number']}")
    print(f"  Improvements found: {result2['improvements_found']}")

    # Get improvement statistics
    print("\n" + "=" * 60)
    print("[4] Improvement Statistics")
    print("=" * 60)

    stats = orchestrator.get_improvement_statistics()

    print(f"\nTotal cycles: {stats['total_cycles']}")
    print(f"Total improvements: {stats['total_improvements']}")
    print(f"Avg improvements per cycle: {stats['avg_improvements_per_cycle']:.2f}")
    print(f"Success rate: {stats['success_rate']:.1%}")

    if stats['cycle_history']:
        print(f"\nCycle History:")
        for i, cycle in enumerate(stats['cycle_history'], 1):
            print(f"  Cycle {i}: {cycle['improvements_found']} improvements, "
                  f"Status: {cycle['status']}")

    # Generate roadmap
    print("\n" + "=" * 60)
    print("[5] Optimization Roadmap")
    print("=" * 60)

    roadmap = orchestrator.generate_improvement_roadmap()

    print(f"\nRoadmap Status: {roadmap['status']}")
    print(f"Total optimization opportunities: {roadmap['total_opportunities']}")
    print(f"Estimated improvement potential: {roadmap['estimated_improvement_potential']:.1%}")

    if roadmap['prioritized_actions']:
        print(f"\nPrioritized Actions:")
        for i, action in enumerate(roadmap['prioritized_actions'], 1):
            print(f"\n{i}. {action['action']}")
            print(f"   Priority: {action['priority']}")
            print(f"   Expected impact: {action['expected_impact']}")
            print(f"   Estimated effort: {action['estimated_effort']}")

    # Long-term improvement demonstration
    print("\n" + "=" * 60)
    print("[6] Long-Term Improvement Tracking")
    print("=" * 60)

    print("\nRunning multiple improvement cycles...")

    num_cycles = 5
    improvement_history = []

    for cycle in range(num_cycles):
        result = orchestrator.run_improvement_cycle(
            enable_profiling=(cycle % 2 == 0),  # Profile every other cycle
            enable_adaptive_lr=True
        )

        improvement_history.append({
            'cycle': result['cycle_number'],
            'improvements': result['improvements_found'],
            'status': result['status']
        })

        print(f"  Cycle {result['cycle_number']}: "
              f"{result['improvements_found']} improvements, "
              f"Status: {result['status']}")

    # Final statistics
    final_stats = orchestrator.get_improvement_statistics()

    print(f"\nFinal Statistics (after {num_cycles} cycles):")
    print(f"  Total improvements: {final_stats['total_improvements']}")
    print(f"  Success rate: {final_stats['success_rate']:.1%}")
    print(f"  Avg improvements/cycle: {final_stats['avg_improvements_per_cycle']:.2f}")

    # Best practices summary
    print("\n" + "=" * 60)
    print("[7] Continuous Improvement Best Practices")
    print("=" * 60)

    print("""
**5-Phase Improvement Cycle:**

1. **MONITOR Phase**
   - Track key performance metrics
   - Detect anomalies and trends
   - Identify degradation early

2. **ANALYZE Phase**
   - Profile component execution
   - Identify bottlenecks
   - Calculate potential speedups

3. **OPTIMIZE Phase**
   - Apply adaptive learning rate
   - Adjust hyperparameters
   - Implement targeted optimizations

4. **VALIDATE Phase**
   - Test improvements
   - Measure actual vs expected gains
   - Rollback if needed

5. **ADAPT Phase**
   - Learn from results
   - Update optimization strategies
   - Plan next cycle

**Integration Guidelines:**

1. Run improvement cycles periodically (e.g., every N training steps)
2. Enable profiling intermittently (overhead consideration)
3. Always validate improvements before deployment
4. Track long-term trends across cycles
5. Use roadmap to prioritize high-impact optimizations

**Expected Results:**

- Initial cycles: 10-30% improvement
- Subsequent cycles: 5-15% incremental gains
- Diminishing returns after 5-10 cycles
- Focus shifts to maintaining performance
    """)

    print("\n✓ Continuous improvement example complete!")
    print("\nKey Takeaway:")
    print("  Self-improving systems automatically detect bottlenecks,")
    print("  apply optimizations, and adapt over time for sustained")
    print("  high performance without manual intervention.")


if __name__ == "__main__":
    main()
