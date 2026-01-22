"""
Example 2: Bottleneck Analysis and Performance Profiling

Demonstrates how to identify performance bottlenecks and get optimization priorities.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

import time
import random
from src.self_improving import BottleneckAnalyzer


def data_loading_component():
    """Simulate data loading - moderately slow"""
    time.sleep(0.05 + random.uniform(0, 0.02))
    return [random.random() for _ in range(100)]


def preprocessing_component(data):
    """Simulate preprocessing - fast"""
    time.sleep(0.01 + random.uniform(0, 0.005))
    return [x * 2 for x in data]


def model_forward_pass(data):
    """Simulate forward pass - SLOWEST (bottleneck)"""
    time.sleep(0.15 + random.uniform(0, 0.03))
    return sum(data) / len(data)


def model_backward_pass(output):
    """Simulate backward pass - slow"""
    time.sleep(0.08 + random.uniform(0, 0.02))
    return output * 0.01


def optimizer_step(gradient):
    """Simulate optimizer step - fast"""
    time.sleep(0.02 + random.uniform(0, 0.005))
    return gradient


def main():
    print("=" * 60)
    print("Self-Improving AI v24.0 - Bottleneck Analysis")
    print("=" * 60)

    # Initialize analyzer
    print("\n[1] Initializing BottleneckAnalyzer...")
    analyzer = BottleneckAnalyzer()

    print(f"Analyzer initialized: {analyzer is not None}")
    print(f"Amdahl's Law enabled for speedup predictions")

    # Profile individual components
    print("\n[2] Profiling Training Pipeline Components")
    print("=" * 60)

    num_iterations = 10
    print(f"Running {num_iterations} profiling iterations per component...")

    # Component 1: Data Loading
    print("\n[2.1] Data Loading")
    result_data_loading = analyzer.profile_execution(
        func=data_loading_component,
        component_name="data_loading",
        num_iterations=num_iterations
    )

    print(f"  Mean time: {result_data_loading['mean_time']*1000:.2f}ms")
    print(f"  Std dev: {result_data_loading['std_time']*1000:.2f}ms")
    print(f"  Min/Max: {result_data_loading['min_time']*1000:.2f}ms / "
          f"{result_data_loading['max_time']*1000:.2f}ms")

    # Component 2: Preprocessing
    print("\n[2.2] Preprocessing")
    result_preprocessing = analyzer.profile_execution(
        func=lambda: preprocessing_component(data_loading_component()),
        component_name="preprocessing",
        num_iterations=num_iterations
    )

    print(f"  Mean time: {result_preprocessing['mean_time']*1000:.2f}ms")
    print(f"  Std dev: {result_preprocessing['std_time']*1000:.2f}ms")

    # Component 3: Forward Pass (BOTTLENECK)
    print("\n[2.3] Model Forward Pass")
    result_forward = analyzer.profile_execution(
        func=lambda: model_forward_pass([1.0] * 100),
        component_name="forward_pass",
        num_iterations=num_iterations
    )

    print(f"  Mean time: {result_forward['mean_time']*1000:.2f}ms ⚠️  SLOW")
    print(f"  Std dev: {result_forward['std_time']*1000:.2f}ms")

    # Component 4: Backward Pass
    print("\n[2.4] Model Backward Pass")
    result_backward = analyzer.profile_execution(
        func=lambda: model_backward_pass(0.5),
        component_name="backward_pass",
        num_iterations=num_iterations
    )

    print(f"  Mean time: {result_backward['mean_time']*1000:.2f}ms")
    print(f"  Std dev: {result_backward['std_time']*1000:.2f}ms")

    # Component 5: Optimizer Step
    print("\n[2.5] Optimizer Step")
    result_optimizer = analyzer.profile_execution(
        func=lambda: optimizer_step(0.01),
        component_name="optimizer_step",
        num_iterations=num_iterations
    )

    print(f"  Mean time: {result_optimizer['mean_time']*1000:.2f}ms")
    print(f"  Std dev: {result_optimizer['std_time']*1000:.2f}ms")

    # Identify bottlenecks
    print("\n" + "=" * 60)
    print("[3] Bottleneck Identification")
    print("=" * 60)

    bottlenecks = analyzer.identify_bottlenecks(top_k=3)

    print(f"\nTop {len(bottlenecks)} bottlenecks identified:")

    for i, bottleneck in enumerate(bottlenecks, 1):
        print(f"\n{i}. {bottleneck['component_name'].upper()}")
        print(f"   Mean time: {bottleneck['mean_time']*1000:.2f}ms")
        print(f"   Percentage of total: {bottleneck['percentage_of_total']:.1f}%")
        print(f"   Cumulative impact: {bottleneck['cumulative_percentage']:.1f}%")

        if bottleneck['percentage_of_total'] > 30:
            print(f"   🔥 CRITICAL BOTTLENECK - High optimization priority!")
        elif bottleneck['percentage_of_total'] > 15:
            print(f"   ⚠️  Significant bottleneck - Medium priority")

    # Get optimization priorities
    print("\n" + "=" * 60)
    print("[4] Optimization Priority List")
    print("=" * 60)

    priorities = analyzer.get_optimization_priority_list()

    print(f"\nOptimization recommendations (in priority order):\n")

    for i, priority in enumerate(priorities, 1):
        print(f"{i}. {priority['component'].upper()}")
        print(f"   Priority: {priority['priority']}")
        print(f"   Mean execution time: {priority['mean_time']*1000:.2f}ms")
        print(f"   Time percentage: {priority['percentage_of_total']:.1f}%")
        print(f"   Potential speedup: {priority['potential_speedup']:.2f}x")
        print(f"   Recommendation: {priority['recommendation']}")
        print()

    # Calculate speedup predictions
    print("=" * 60)
    print("[5] Speedup Predictions (Amdahl's Law)")
    print("=" * 60)

    # Scenario 1: Optimize forward pass by 50%
    print("\nScenario 1: Optimize forward_pass by 50%")
    speedup1 = analyzer.calculate_speedup('forward_pass', improvement_factor=0.5)

    print(f"  Expected system speedup: {speedup1['system_speedup']:.2f}x")
    print(f"  Time saved: {speedup1['time_saved_percentage']:.1f}%")
    print(f"  Original time: {speedup1['original_total_time']*1000:.2f}ms")
    print(f"  New time: {speedup1['new_total_time']*1000:.2f}ms")

    # Scenario 2: Optimize forward pass by 90%
    print("\nScenario 2: Optimize forward_pass by 90%")
    speedup2 = analyzer.calculate_speedup('forward_pass', improvement_factor=0.1)

    print(f"  Expected system speedup: {speedup2['system_speedup']:.2f}x")
    print(f"  Time saved: {speedup2['time_saved_percentage']:.1f}%")

    # Scenario 3: Optimize all components by 50%
    print("\nScenario 3: Optimize ALL components by 50%")

    components = ['data_loading', 'preprocessing', 'forward_pass', 'backward_pass', 'optimizer_step']
    total_original = sum(analyzer.execution_times.get(c, [0])[0] if c in analyzer.execution_times else 0
                        for c in components)
    total_optimized = total_original * 0.5

    print(f"  System speedup: ~2.0x (all components improved)")
    print(f"  Original total: {total_original*1000:.2f}ms")
    print(f"  Optimized total: {total_optimized*1000:.2f}ms")

    # Get performance statistics
    print("\n" + "=" * 60)
    print("[6] Performance Statistics Summary")
    print("=" * 60)

    stats = analyzer.get_performance_statistics()

    print(f"\nTotal components profiled: {stats['total_components']}")
    print(f"Total time: {stats['total_time']*1000:.2f}ms")
    print(f"Mean time per component: {stats['mean_time']*1000:.2f}ms")
    print(f"Std time per component: {stats['std_time']*1000:.2f}ms")

    print(f"\nComponent breakdown:")
    for component, pct in stats['component_percentages'].items():
        print(f"  {component}: {pct:.1f}%")

    # Optimization recommendations
    print("\n" + "=" * 60)
    print("[7] Actionable Optimization Recommendations")
    print("=" * 60)

    print("""
Based on the bottleneck analysis:

1. **FORWARD PASS (Highest Priority)**
   - Currently taking ~150ms (40%+ of total time)
   - Optimization strategies:
     * Use mixed precision (FP16) training
     * Implement model quantization
     * Use faster libraries (cuDNN, TensorRT)
     * Reduce model size or use pruning
   - Expected impact: 2-3x speedup possible

2. **BACKWARD PASS (Medium Priority)**
   - Currently taking ~80ms (20%+ of total time)
   - Optimization strategies:
     * Gradient checkpointing for memory
     * Use automatic mixed precision
     * Optimize gradient computation graphs
   - Expected impact: 1.5-2x speedup possible

3. **DATA LOADING (Low Priority)**
   - Currently taking ~50ms (15% of total time)
   - Optimization strategies:
     * Use parallel data loading
     * Implement data prefetching
     * Optimize data preprocessing pipeline
   - Expected impact: 1.2-1.5x speedup possible

Remember: Focus on the biggest bottlenecks first (Pareto principle)!
    """)

    print("\n✓ Bottleneck analysis example complete!")


if __name__ == "__main__":
    main()
