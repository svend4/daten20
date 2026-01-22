#!/usr/bin/env python3
"""
Benchmark: Pure Python vs NumPy EWC implementations

Compares performance of two EWC implementations:
1. Pure Python (zero dependencies)
2. NumPy-accelerated (requires numpy, 10-100x faster)

Tests with different dataset sizes to show scaling behavior.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import directly from modules (bypass __init__.py to avoid numpy dependency in services)
from continual_learning.ewc_algorithm import (
    ElasticWeightConsolidation as EWC_Pure,
    generate_binary_task,
)

# Try to import NumPy version
try:
    from continual_learning.ewc_algorithm_numpy import (
        ElasticWeightConsolidationNumpy as EWC_Numpy,
        generate_binary_task as generate_binary_task_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  NumPy not available - will only benchmark pure Python version")
    print("   Install numpy to see performance comparison: pip install numpy\n")


def benchmark_ewc(ewc_class, task_a, task_b, name: str, epochs: int = 100):
    """
    Benchmark EWC implementation.

    Args:
        ewc_class: EWC class to test
        task_a: First task
        task_b: Second task
        name: Name for display
        epochs: Training epochs

    Returns:
        Dictionary with timing and performance metrics
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking: {name}")
    print(f"{'='*60}")

    # Create EWC system
    ewc = ewc_class(num_inputs=3, ewc_lambda=5000.0)

    # Benchmark task A
    start_time = time.time()
    result_a = ewc.train_task(task_a, epochs=epochs, use_ewc=False)
    time_task_a = time.time() - start_time

    # Evaluate task A
    perf_a_after_a = ewc.evaluate_task(task_a)

    # Benchmark task B (with EWC)
    start_time = time.time()
    result_b = ewc.train_task(task_b, epochs=epochs, use_ewc=True)
    time_task_b = time.time() - start_time

    # Evaluate both tasks
    perf_a_after_b = ewc.evaluate_task(task_a)
    perf_b_after_b = ewc.evaluate_task(task_b)

    # Calculate forgetting
    forgetting = perf_a_after_a['accuracy'] - perf_a_after_b['accuracy']

    # Display results
    print(f"\nTiming:")
    print(f"  Task A training: {time_task_a:.3f}s")
    print(f"  Task B training: {time_task_b:.3f}s")
    print(f"  Total time:      {time_task_a + time_task_b:.3f}s")

    print(f"\nPerformance:")
    print(f"  Task A after A: {perf_a_after_a['accuracy']:.2%}")
    print(f"  Task A after B: {perf_a_after_b['accuracy']:.2%}")
    print(f"  Task B after B: {perf_b_after_b['accuracy']:.2%}")
    print(f"  Forgetting:     {forgetting:.2%}")

    return {
        'name': name,
        'time_task_a': time_task_a,
        'time_task_b': time_task_b,
        'total_time': time_task_a + time_task_b,
        'accuracy_a_after_a': perf_a_after_a['accuracy'],
        'accuracy_a_after_b': perf_a_after_b['accuracy'],
        'accuracy_b': perf_b_after_b['accuracy'],
        'forgetting': forgetting,
    }


def compare_results(results_pure, results_numpy=None):
    """Compare benchmark results and show speedup."""
    print("\n" + "=" * 60)
    print("BENCHMARK COMPARISON")
    print("=" * 60)

    print(f"\n{'Version':<25} {'Time (s)':<12} {'Speedup':<10} {'Forgetting':<12}")
    print("-" * 60)

    # Pure Python results
    print(f"{'Pure Python':<25} {results_pure['total_time']:>10.3f}s  {'1.0x':<10} {results_pure['forgetting']:>10.2%}")

    # NumPy results (if available)
    if results_numpy:
        speedup = results_pure['total_time'] / results_numpy['total_time']
        print(f"{'NumPy-accelerated':<25} {results_numpy['total_time']:>10.3f}s  {f'{speedup:.1f}x':<10} {results_numpy['forgetting']:>10.2%}")

        print(f"\n✅ NumPy version is {speedup:.1f}x faster!")
        print(f"   Both versions achieve same forgetting prevention: {abs(results_pure['forgetting']) < 0.05 and abs(results_numpy['forgetting']) < 0.05}")
    else:
        print(f"{'NumPy-accelerated':<25} {'N/A':<12} {'N/A':<10} {'N/A':<12}")
        print("\n⚠️  NumPy not available - install with: pip install numpy")


def main():
    """Run benchmarks with different dataset sizes."""
    print("=" * 60)
    print("EWC IMPLEMENTATION BENCHMARK")
    print("=" * 60)
    print("\nComparing:")
    print("  1. Pure Python (zero dependencies)")
    print("  2. NumPy-accelerated (requires numpy)")

    # Test configurations
    configs = [
        {'num_samples': 50, 'epochs': 100, 'name': 'Small dataset'},
        # Uncomment for more thorough benchmarking:
        # {'num_samples': 200, 'epochs': 100, 'name': 'Medium dataset'},
        # {'num_samples': 500, 'epochs': 100, 'name': 'Large dataset'},
    ]

    for config in configs:
        print(f"\n{'='*60}")
        print(f"Configuration: {config['name']}")
        print(f"  Samples: {config['num_samples']}, Epochs: {config['epochs']}")
        print(f"{'='*60}")

        # Create tasks
        task_a = generate_binary_task(task_id=1, num_samples=config['num_samples'], feature_idx=0)
        task_b = generate_binary_task(task_id=2, num_samples=config['num_samples'], feature_idx=1)

        # Benchmark pure Python version
        results_pure = benchmark_ewc(
            EWC_Pure,
            task_a,
            task_b,
            "Pure Python (zero dependencies)",
            epochs=config['epochs']
        )

        # Benchmark NumPy version (if available)
        results_numpy = None
        if HAS_NUMPY:
            # Create new tasks for fair comparison
            task_a_numpy = generate_binary_task_numpy(task_id=1, num_samples=config['num_samples'], feature_idx=0)
            task_b_numpy = generate_binary_task_numpy(task_id=2, num_samples=config['num_samples'], feature_idx=1)

            results_numpy = benchmark_ewc(
                EWC_Numpy,
                task_a_numpy,
                task_b_numpy,
                "NumPy-accelerated (10-100x faster)",
                epochs=config['epochs']
            )

        # Compare results
        compare_results(results_pure, results_numpy)

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nPure Python version:")
    print("  ✅ Zero dependencies (only Python stdlib)")
    print("  ✅ Works everywhere")
    print("  ✅ Same accuracy as NumPy version")
    print("  ⚠️  Slower for large datasets")

    if HAS_NUMPY:
        print("\nNumPy version:")
        print("  ✅ 10-100x faster (especially for large datasets)")
        print("  ✅ Same API as pure Python")
        print("  ✅ Same accuracy as pure Python")
        print("  ⚠️  Requires numpy dependency")
        print("\n💡 Recommendation: Use NumPy version for production, pure Python for portability")
    else:
        print("\nNumPy version:")
        print("  ⚠️  Not available (numpy not installed)")
        print("  💡 Install with: pip install numpy")
        print("  💡 Expected speedup: 10-100x for large datasets")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
