"""
Example 3: Chain-of-Thought Reasoning

Demonstrates different reasoning types and how to analyze reasoning traces.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

from src.agi_universal import (
    UniversalProblemSolver,
    Problem,
    ProblemDomain,
    ChainOfThoughtReasoner,
    ReasoningType,
)


def main():
    print("=" * 60)
    print("AGI Universal v26.0 - Chain-of-Thought Reasoning")
    print("=" * 60)

    # Initialize solver
    print("\n[1] Initializing UniversalProblemSolver...")
    solver = UniversalProblemSolver()
    solver.initialize(quick_init=True)

    # Initialize reasoner directly for detailed analysis
    reasoner = ChainOfThoughtReasoner()

    # Test different reasoning types
    print("\n[2] Testing Different Reasoning Types...")
    print("=" * 60)

    # Deductive Reasoning
    print("\n[2.1] DEDUCTIVE REASONING")
    print("-" * 60)

    deductive_problem = Problem(
        description="All humans are mortal. Socrates is a human. Is Socrates mortal?",
        domain=ProblemDomain.LOGICAL
    )

    print(f"Problem: {deductive_problem.description}")
    print(f"Reasoning Type: {ReasoningType.DEDUCTIVE.value}")

    deductive_chain = reasoner.generate_reasoning_chain(
        deductive_problem,
        reasoning_type=ReasoningType.DEDUCTIVE,
        max_steps=5
    )

    print(f"\nReasoning Steps ({len(deductive_chain.steps)} steps):")
    for i, step in enumerate(deductive_chain.steps, 1):
        print(f"  {i}. {step.description}")
        print(f"     Type: {step.step_type.value}, Confidence: {step.confidence:.1%}")

    # Solve and get answer
    solution = solver.solve(deductive_problem)
    print(f"\nFinal Answer: {solution.answer}")
    print(f"Confidence: {solution.confidence:.1%}")

    # Inductive Reasoning
    print("\n" + "=" * 60)
    print("[2.2] INDUCTIVE REASONING")
    print("-" * 60)

    inductive_problem = Problem(
        description="The sun rose yesterday, the day before, and every day I can remember. Will the sun rise tomorrow?",
        domain=ProblemDomain.LOGICAL
    )

    print(f"Problem: {inductive_problem.description}")
    print(f"Reasoning Type: {ReasoningType.INDUCTIVE.value}")

    inductive_chain = reasoner.generate_reasoning_chain(
        inductive_problem,
        reasoning_type=ReasoningType.INDUCTIVE,
        max_steps=5
    )

    print(f"\nReasoning Steps ({len(inductive_chain.steps)} steps):")
    for i, step in enumerate(inductive_chain.steps, 1):
        print(f"  {i}. {step.description}")

    solution = solver.solve(inductive_problem)
    print(f"\nFinal Answer: {solution.answer}")
    print(f"Confidence: {solution.confidence:.1%}")

    # Abductive Reasoning
    print("\n" + "=" * 60)
    print("[2.3] ABDUCTIVE REASONING")
    print("-" * 60)

    abductive_problem = Problem(
        description="The grass is wet. What is the most likely explanation?",
        domain=ProblemDomain.CAUSAL
    )

    print(f"Problem: {abductive_problem.description}")
    print(f"Reasoning Type: {ReasoningType.ABDUCTIVE.value}")

    abductive_chain = reasoner.generate_reasoning_chain(
        abductive_problem,
        reasoning_type=ReasoningType.ABDUCTIVE,
        max_steps=5
    )

    print(f"\nReasoning Steps ({len(abductive_chain.steps)} steps):")
    for i, step in enumerate(abductive_chain.steps, 1):
        print(f"  {i}. {step.description}")

    solution = solver.solve(abductive_problem)
    print(f"\nFinal Answer: {solution.answer}")

    # Analogical Reasoning
    print("\n" + "=" * 60)
    print("[2.4] ANALOGICAL REASONING")
    print("-" * 60)

    analogical_problem = Problem(
        description="Just as a key opens a lock, what opens a door?",
        domain=ProblemDomain.LOGICAL
    )

    print(f"Problem: {analogical_problem.description}")
    print(f"Reasoning Type: {ReasoningType.ANALOGICAL.value}")

    analogical_chain = reasoner.generate_reasoning_chain(
        analogical_problem,
        reasoning_type=ReasoningType.ANALOGICAL,
        max_steps=5
    )

    print(f"\nReasoning Steps ({len(analogical_chain.steps)} steps):")
    for i, step in enumerate(analogical_chain.steps, 1):
        print(f"  {i}. {step.description}")

    solution = solver.solve(analogical_problem)
    print(f"\nFinal Answer: {solution.answer}")

    # Causal Reasoning
    print("\n" + "=" * 60)
    print("[2.5] CAUSAL REASONING")
    print("-" * 60)

    causal_problem = Problem(
        description="If I drop a ball, what will happen?",
        domain=ProblemDomain.CAUSAL
    )

    print(f"Problem: {causal_problem.description}")
    print(f"Reasoning Type: {ReasoningType.CAUSAL.value}")

    causal_chain = reasoner.generate_reasoning_chain(
        causal_problem,
        reasoning_type=ReasoningType.CAUSAL,
        max_steps=5
    )

    print(f"\nReasoning Steps ({len(causal_chain.steps)} steps):")
    for i, step in enumerate(causal_chain.steps, 1):
        print(f"  {i}. {step.description}")

    solution = solver.solve(causal_problem)
    print(f"\nFinal Answer: {solution.answer}")

    # Explain reasoning chain in natural language
    print("\n" + "=" * 60)
    print("[3] Reasoning Chain Explanation")
    print("=" * 60)

    explanation = reasoner.explain_reasoning_chain(causal_chain)

    print(f"\nChain ID: {explanation['chain_id']}")
    print(f"Reasoning Type: {explanation['reasoning_type']}")
    print(f"Total Steps: {explanation['total_steps']}")
    print(f"Average Confidence: {explanation['avg_confidence']:.1%}")

    print(f"\nStep-by-Step Explanation:")
    print(explanation['explanation'])

    # Solve complex problem with automatic reasoning
    print("\n" + "=" * 60)
    print("[4] Complex Problem with Automatic Reasoning")
    print("=" * 60)

    complex_problem = Problem(
        description="A farmer needs to cross a river with a fox, a chicken, and a sack of grain. "
                   "The boat can only carry the farmer and one item. If left alone, the fox will eat "
                   "the chicken, and the chicken will eat the grain. How does the farmer get everything across?",
        domain=ProblemDomain.LOGICAL
    )

    print(f"Problem: {complex_problem.description}")

    solution = solver.solve(complex_problem)

    print(f"\nSolution:")
    print(f"  Strategy: {solution.strategy_used.value}")
    print(f"  Success: {'✓' if solution.success else '✗'}")
    print(f"  Confidence: {solution.confidence:.1%}")

    print(f"\nAnswer: {solution.answer}")

    if solution.reasoning_trace:
        print(f"\nReasoning Trace ({len(solution.reasoning_trace)} steps):")
        for i, step in enumerate(solution.reasoning_trace, 1):
            print(f"  {i}. {step}")

    print("\n✓ Chain-of-thought reasoning example complete!")
    print("\nKey Takeaways:")
    print("  • 5 reasoning types: Deductive, Inductive, Abductive, Analogical, Causal")
    print("  • Each step has description, type, and confidence score")
    print("  • Reasoning chains provide transparent explanations")
    print("  • Automatic reasoning type selection for problems")


if __name__ == "__main__":
    main()
