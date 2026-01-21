"""
Example 2: Meta-Learning with Few-Shot Adaptation

Demonstrates how UniversalProblemSolver adapts to new tasks with minimal examples
using Model-Agnostic Meta-Learning (MAML).
"""

import sys
sys.path.insert(0, '/home/user/daten20')

from src.agi_universal import (
    UniversalProblemSolver,
    Problem,
    ProblemDomain,
    MetaLearner,
    MetaTask,
)


def main():
    print("=" * 60)
    print("AGI Universal v26.0 - Meta-Learning Example")
    print("=" * 60)

    # Initialize solver
    print("\n[1] Initializing UniversalProblemSolver...")
    solver = UniversalProblemSolver()
    init_result = solver.initialize(quick_init=False)

    print(f"Status: {init_result['status']}")
    print(f"Meta-learner enabled: {solver.mtl_learner is not None}")

    # Define a new task type with support set (few examples)
    print("\n[2] Creating Meta-Learning Task (Mathematical Sequences)...")

    # Support set: Few examples to learn from
    support_set = [
        {
            'input': [2, 4, 6, 8],
            'output': 10,
            'pattern': 'arithmetic progression +2'
        },
        {
            'input': [1, 3, 5, 7],
            'output': 9,
            'pattern': 'arithmetic progression +2'
        },
        {
            'input': [10, 20, 30, 40],
            'output': 50,
            'pattern': 'arithmetic progression +10'
        },
    ]

    # Create meta-task
    meta_task = MetaTask(
        task_id="sequence_prediction",
        domain=ProblemDomain.MATHEMATICAL,
        support_examples=support_set,
        query_examples=[]
    )

    print(f"Support set size: {len(support_set)} examples")
    print("Learning pattern: Arithmetic sequences")

    # Adapt to this new task
    print("\n[3] Adapting to Task (Few-Shot Learning)...")

    if solver.mtl_learner:
        adaptation_result = solver.mtl_learner.adapt_to_task(meta_task)

        print(f"Adaptation success: {adaptation_result['success']}")
        print(f"Adaptation steps: {adaptation_result['adaptation_steps']}")
        print(f"Final loss: {adaptation_result['final_loss']:.6f}")
        print(f"Task performance: {adaptation_result['task_performance']:.1%}")

    # Now test on new sequences (query set)
    print("\n[4] Testing on New Sequences...")
    print("-" * 60)

    test_problems = [
        Problem(
            description="What is the next number: 5, 10, 15, 20, ?",
            domain=ProblemDomain.MATHEMATICAL
        ),
        Problem(
            description="What is the next number: 100, 200, 300, 400, ?",
            domain=ProblemDomain.MATHEMATICAL
        ),
        Problem(
            description="What is the next number: 3, 6, 9, 12, ?",
            domain=ProblemDomain.MATHEMATICAL
        ),
    ]

    for i, problem in enumerate(test_problems, 1):
        print(f"\nTest {i}: {problem.description}")

        solution = solver.solve(problem)

        print(f"  Answer: {solution.answer}")
        print(f"  Confidence: {solution.confidence:.1%}")
        print(f"  Strategy: {solution.strategy_used.value}")
        print(f"  Execution Time: {solution.execution_time*1000:.2f}ms")

    # Meta-training: Improve across multiple tasks
    print("\n" + "=" * 60)
    print("[5] Meta-Training Across Multiple Tasks")
    print("=" * 60)

    # Define multiple task types for meta-training
    meta_tasks = [
        MetaTask(
            task_id="arithmetic_sequences",
            domain=ProblemDomain.MATHEMATICAL,
            support_examples=[
                {'input': [2, 4, 6], 'output': 8},
                {'input': [5, 10, 15], 'output': 20},
            ],
            query_examples=[]
        ),
        MetaTask(
            task_id="geometric_sequences",
            domain=ProblemDomain.MATHEMATICAL,
            support_examples=[
                {'input': [2, 4, 8], 'output': 16},
                {'input': [3, 9, 27], 'output': 81},
            ],
            query_examples=[]
        ),
        MetaTask(
            task_id="fibonacci_like",
            domain=ProblemDomain.MATHEMATICAL,
            support_examples=[
                {'input': [1, 1, 2, 3], 'output': 5},
                {'input': [0, 1, 1, 2], 'output': 3},
            ],
            query_examples=[]
        ),
    ]

    print(f"\nMeta-training on {len(meta_tasks)} task types...")

    if solver.mtl_learner:
        meta_train_result = solver.mtl_learner.meta_train(
            meta_tasks=meta_tasks,
            num_iterations=10
        )

        print(f"\nMeta-training complete:")
        print(f"  Final meta-loss: {meta_train_result['final_meta_loss']:.6f}")
        print(f"  Avg task performance: {meta_train_result['avg_task_performance']:.1%}")
        print(f"  Convergence indicator: {meta_train_result['convergence_indicator']:.1%}")
        print(f"  Total iterations: {meta_train_result['total_iterations']}")

    # Get performance statistics
    print("\n[6] Performance Statistics")
    print("-" * 60)

    stats = solver.get_performance_statistics()

    print(f"Total problems solved: {stats['total_problems_solved']}")
    print(f"Success rate: {stats['success_rate']:.1%}")
    print(f"Average confidence: {stats['avg_confidence']:.1%}")
    print(f"Average execution time: {stats['avg_execution_time']*1000:.2f}ms")

    if 'strategy_distribution' in stats:
        print("\nStrategy usage:")
        for strategy, count in stats['strategy_distribution'].items():
            print(f"  {strategy}: {count} times")

    print("\n✓ Meta-learning example complete!")
    print("\nKey Takeaways:")
    print("  • Meta-learning enables fast adaptation to new tasks")
    print("  • MAML learns how to learn from few examples")
    print("  • Transfer learning across task distributions")
    print("  • Improves generalization to unseen problems")


if __name__ == "__main__":
    main()
