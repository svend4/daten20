"""
Example 1: Basic Problem Solving with AGI Universal

Demonstrates basic usage of UniversalProblemSolver for different problem types.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

from src.agi_universal import (
    UniversalProblemSolver,
    Problem,
    ProblemDomain,
)


def main():
    print("=" * 60)
    print("AGI Universal v26.0 - Basic Problem Solving")
    print("=" * 60)

    # Initialize solver
    print("\n[1] Initializing UniversalProblemSolver...")
    solver = UniversalProblemSolver()
    init_result = solver.initialize(quick_init=True)

    print(f"Status: {init_result['status']}")
    print(f"Components: {', '.join(init_result['components'].keys())}")

    # Define problems
    problems = [
        Problem(
            description="If all A are B, and all B are C, are all A also C?",
            domain=ProblemDomain.LOGICAL
        ),
        Problem(
            description="What is the next number in sequence: 2, 4, 8, 16, ?",
            domain=ProblemDomain.MATHEMATICAL
        ),
        Problem(
            description="Explain the relationship between cause and effect",
            domain=ProblemDomain.CAUSAL
        ),
    ]

    # Solve each problem
    print("\n[2] Solving Problems...")
    print("-" * 60)

    for i, problem in enumerate(problems, 1):
        print(f"\nProblem {i}:")
        print(f"  Question: {problem.description}")
        print(f"  Domain: {problem.domain.value}")

        # Solve
        solution = solver.solve(problem)

        # Display results
        print(f"\n  Strategy Used: {solution.strategy_used.value}")
        print(f"  Success: {'✓' if solution.success else '✗'}")
        print(f"  Confidence: {solution.confidence:.1%}")
        print(f"  Execution Time: {solution.execution_time*1000:.2f}ms")

        print(f"\n  Answer: {solution.answer}")

        if solution.reasoning_trace:
            print(f"\n  Reasoning Trace:")
            for j, step in enumerate(solution.reasoning_trace[:3], 1):
                print(f"    {j}. {step}")
            if len(solution.reasoning_trace) > 3:
                print(f"    ... and {len(solution.reasoning_trace)-3} more steps")

        print("-" * 60)

    print("\n✓ Example complete!")


if __name__ == "__main__":
    main()
