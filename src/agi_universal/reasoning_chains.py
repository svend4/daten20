"""
Reasoning Chains for AGI Universal

Chain-of-Thought reasoning, step-by-step problem solving.
Implements reasoning strategies for complex problems.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import time


class ReasoningType(Enum):
    """Types of reasoning"""
    DEDUCTIVE = "deductive"  # General → Specific
    INDUCTIVE = "inductive"  # Specific → General
    ABDUCTIVE = "abductive"  # Best explanation
    ANALOGICAL = "analogical"  # By analogy
    CAUSAL = "causal"  # Cause and effect


@dataclass
class ReasoningStep:
    """Single step in reasoning chain"""
    step_number: int
    reasoning_type: ReasoningType
    input_state: Dict[str, Any]
    thought: str
    action: str
    output_state: Dict[str, Any]
    confidence: float  # 0.0 to 1.0


@dataclass
class ReasoningChain:
    """Complete chain of reasoning"""
    problem: str
    steps: List[ReasoningStep] = field(default_factory=list)
    conclusion: Optional[str] = None
    success: bool = False
    execution_time: float = 0.0


class ChainOfThoughtReasoner:
    """
    Chain-of-Thought reasoning system.

    Breaks down complex problems into step-by-step reasoning.
    Inspired by how humans solve problems incrementally.

    Example:
        >>> reasoner = ChainOfThoughtReasoner()
        >>> chain = reasoner.solve_problem(
        ...     "If all humans are mortal, and Socrates is human, is Socrates mortal?",
        ...     reasoning_type=ReasoningType.DEDUCTIVE
        ... )
        >>> print(chain.conclusion)
    """

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.reasoning_strategies: Dict[ReasoningType, Callable] = {
            ReasoningType.DEDUCTIVE: self._deductive_reasoning,
            ReasoningType.INDUCTIVE: self._inductive_reasoning,
            ReasoningType.ABDUCTIVE: self._abductive_reasoning,
            ReasoningType.ANALOGICAL: self._analogical_reasoning,
            ReasoningType.CAUSAL: self._causal_reasoning
        }

    def solve_problem(self,
                     problem: str,
                     reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE,
                     context: Optional[Dict[str, Any]] = None) -> ReasoningChain:
        """
        Solve problem using chain-of-thought reasoning.

        Args:
            problem: Problem statement
            reasoning_type: Type of reasoning to use
            context: Additional context for problem

        Returns:
            Complete reasoning chain with conclusion
        """
        start_time = time.time()

        chain = ReasoningChain(problem=problem)
        state = context or {}

        # Apply reasoning strategy
        strategy = self.reasoning_strategies.get(reasoning_type, self._deductive_reasoning)
        chain = strategy(problem, chain, state)

        chain.execution_time = time.time() - start_time
        return chain

    def _deductive_reasoning(self,
                            problem: str,
                            chain: ReasoningChain,
                            state: Dict[str, Any]) -> ReasoningChain:
        """
        Deductive reasoning: Apply general rules to specific cases.

        Forma: Major premise → Minor premise → Conclusion
        """
        # Step 1: Identify general rule
        step1 = ReasoningStep(
            step_number=1,
            reasoning_type=ReasoningType.DEDUCTIVE,
            input_state=state.copy(),
            thought="Identify general rule or principle",
            action="Extract universal statement from problem",
            output_state={**state, 'general_rule': self._extract_general_rule(problem)},
            confidence=0.9
        )
        chain.steps.append(step1)

        # Step 2: Identify specific case
        step2 = ReasoningStep(
            step_number=2,
            reasoning_type=ReasoningType.DEDUCTIVE,
            input_state=step1.output_state.copy(),
            thought="Identify specific case to apply rule to",
            action="Extract specific instance from problem",
            output_state={**step1.output_state, 'specific_case': self._extract_specific_case(problem)},
            confidence=0.85
        )
        chain.steps.append(step2)

        # Step 3: Apply rule to case
        step3 = ReasoningStep(
            step_number=3,
            reasoning_type=ReasoningType.DEDUCTIVE,
            input_state=step2.output_state.copy(),
            thought="Apply general rule to specific case",
            action="Deduce conclusion",
            output_state={
                **step2.output_state,
                'conclusion': self._apply_deduction(
                    step2.output_state.get('general_rule'),
                    step2.output_state.get('specific_case')
                )
            },
            confidence=0.8
        )
        chain.steps.append(step3)

        # Set conclusion
        chain.conclusion = step3.output_state.get('conclusion', "Deductive conclusion reached")
        chain.success = True

        return chain

    def _inductive_reasoning(self,
                            problem: str,
                            chain: ReasoningChain,
                            state: Dict[str, Any]) -> ReasoningChain:
        """
        Inductive reasoning: Generalize from specific examples.

        Form: Observation 1, 2, 3... → General pattern
        """
        # Step 1: Collect observations
        step1 = ReasoningStep(
            step_number=1,
            reasoning_type=ReasoningType.INDUCTIVE,
            input_state=state.copy(),
            thought="Collect specific observations",
            action="Extract individual cases from problem",
            output_state={**state, 'observations': self._extract_observations(problem)},
            confidence=0.9
        )
        chain.steps.append(step1)

        # Step 2: Identify pattern
        step2 = ReasoningStep(
            step_number=2,
            reasoning_type=ReasoningType.INDUCTIVE,
            input_state=step1.output_state.copy(),
            thought="Identify common pattern across observations",
            action="Find regularities",
            output_state={
                **step1.output_state,
                'pattern': self._identify_pattern(step1.output_state.get('observations', []))
            },
            confidence=0.75  # Lower confidence - induction is uncertain
        )
        chain.steps.append(step2)

        # Step 3: Generalize
        step3 = ReasoningStep(
            step_number=3,
            reasoning_type=ReasoningType.INDUCTIVE,
            input_state=step2.output_state.copy(),
            thought="Generalize pattern to universal rule",
            action="Form general hypothesis",
            output_state={
                **step2.output_state,
                'hypothesis': self._generalize_pattern(step2.output_state.get('pattern'))
            },
            confidence=0.7
        )
        chain.steps.append(step3)

        chain.conclusion = step3.output_state.get('hypothesis', "Inductive hypothesis formed")
        chain.success = True

        return chain

    def _abductive_reasoning(self,
                            problem: str,
                            chain: ReasoningChain,
                            state: Dict[str, Any]) -> ReasoningChain:
        """
        Abductive reasoning: Inference to best explanation.

        Form: Observation → Most likely explanation
        """
        # Step 1: Observe phenomenon
        step1 = ReasoningStep(
            step_number=1,
            reasoning_type=ReasoningType.ABDUCTIVE,
            input_state=state.copy(),
            thought="Observe phenomenon requiring explanation",
            action="Extract observable fact",
            output_state={**state, 'phenomenon': self._extract_phenomenon(problem)},
            confidence=0.9
        )
        chain.steps.append(step1)

        # Step 2: Generate hypotheses
        step2 = ReasoningStep(
            step_number=2,
            reasoning_type=ReasoningType.ABDUCTIVE,
            input_state=step1.output_state.copy(),
            thought="Generate possible explanations",
            action="Enumerate candidate hypotheses",
            output_state={
                **step1.output_state,
                'hypotheses': self._generate_hypotheses(step1.output_state.get('phenomenon'))
            },
            confidence=0.8
        )
        chain.steps.append(step2)

        # Step 3: Select best explanation
        step3 = ReasoningStep(
            step_number=3,
            reasoning_type=ReasoningType.ABDUCTIVE,
            input_state=step2.output_state.copy(),
            thought="Select most likely explanation",
            action="Evaluate hypotheses by simplicity and fit",
            output_state={
                **step2.output_state,
                'best_explanation': self._select_best_explanation(
                    step2.output_state.get('hypotheses', [])
                )
            },
            confidence=0.7  # Abduction is uncertain
        )
        chain.steps.append(step3)

        chain.conclusion = step3.output_state.get('best_explanation', "Best explanation selected")
        chain.success = True

        return chain

    def _analogical_reasoning(self,
                             problem: str,
                             chain: ReasoningChain,
                             state: Dict[str, Any]) -> ReasoningChain:
        """
        Analogical reasoning: Reason by analogy to similar cases.

        Form: Source domain → Target domain
        """
        # Step 1: Identify target problem
        step1 = ReasoningStep(
            step_number=1,
            reasoning_type=ReasoningType.ANALOGICAL,
            input_state=state.copy(),
            thought="Understand target problem",
            action="Extract problem structure",
            output_state={**state, 'target': self._extract_problem_structure(problem)},
            confidence=0.9
        )
        chain.steps.append(step1)

        # Step 2: Find analogous case
        step2 = ReasoningStep(
            step_number=2,
            reasoning_type=ReasoningType.ANALOGICAL,
            input_state=step1.output_state.copy(),
            thought="Find similar solved problem (source domain)",
            action="Search for structural similarity",
            output_state={
                **step1.output_state,
                'source': self._find_analogous_case(step1.output_state.get('target'))
            },
            confidence=0.75
        )
        chain.steps.append(step2)

        # Step 3: Map solution
        step3 = ReasoningStep(
            step_number=3,
            reasoning_type=ReasoningType.ANALOGICAL,
            input_state=step2.output_state.copy(),
            thought="Map solution from source to target",
            action="Transfer solution structure",
            output_state={
                **step2.output_state,
                'mapped_solution': self._map_solution(
                    step2.output_state.get('source'),
                    step2.output_state.get('target')
                )
            },
            confidence=0.7
        )
        chain.steps.append(step3)

        chain.conclusion = step3.output_state.get('mapped_solution', "Solution mapped by analogy")
        chain.success = True

        return chain

    def _causal_reasoning(self,
                         problem: str,
                         chain: ReasoningChain,
                         state: Dict[str, Any]) -> ReasoningChain:
        """
        Causal reasoning: Reason about causes and effects.

        Form: Event → Causes / Causes → Effects
        """
        # Step 1: Identify event
        step1 = ReasoningStep(
            step_number=1,
            reasoning_type=ReasoningType.CAUSAL,
            input_state=state.copy(),
            thought="Identify event or effect",
            action="Extract observable event",
            output_state={**state, 'event': self._extract_event(problem)},
            confidence=0.9
        )
        chain.steps.append(step1)

        # Step 2: Trace causes
        step2 = ReasoningStep(
            step_number=2,
            reasoning_type=ReasoningType.CAUSAL,
            input_state=step1.output_state.copy(),
            thought="Trace potential causes",
            action="Identify causal factors",
            output_state={
                **step1.output_state,
                'causes': self._trace_causes(step1.output_state.get('event'))
            },
            confidence=0.8
        )
        chain.steps.append(step2)

        # Step 3: Predict effects
        step3 = ReasoningStep(
            step_number=3,
            reasoning_type=ReasoningType.CAUSAL,
            input_state=step2.output_state.copy(),
            thought="Predict downstream effects",
            action="Follow causal chain forward",
            output_state={
                **step2.output_state,
                'effects': self._predict_effects(step2.output_state.get('causes', []))
            },
            confidence=0.75
        )
        chain.steps.append(step3)

        chain.conclusion = f"Causal chain: {step3.output_state.get('causes')} → {step3.output_state.get('effects')}"
        chain.success = True

        return chain

    # Helper methods (simplified for demonstration)

    def _extract_general_rule(self, problem: str) -> str:
        # Simplified: Look for universal quantifiers
        if "all" in problem.lower():
            return "Universal rule identified in problem"
        return "General principle extracted"

    def _extract_specific_case(self, problem: str) -> str:
        # Simplified: Look for proper nouns
        words = problem.split()
        for word in words:
            if word[0].isupper() and word not in ["If", "And", "Then"]:
                return f"Specific case: {word}"
        return "Specific instance identified"

    def _apply_deduction(self, general_rule, specific_case) -> str:
        return f"Applying {general_rule} to {specific_case} yields logical conclusion"

    def _extract_observations(self, problem: str) -> List[str]:
        # Simplified: Split by commas or semicolons
        return [obs.strip() for obs in problem.replace(';', ',').split(',')]

    def _identify_pattern(self, observations: List[str]) -> str:
        return f"Pattern identified across {len(observations)} observations"

    def _generalize_pattern(self, pattern: str) -> str:
        return f"General hypothesis: {pattern} likely holds universally"

    def _extract_phenomenon(self, problem: str) -> str:
        return "Observable phenomenon extracted"

    def _generate_hypotheses(self, phenomenon: str) -> List[str]:
        return [
            "Hypothesis A: Natural cause",
            "Hypothesis B: External intervention",
            "Hypothesis C: Random occurrence"
        ]

    def _select_best_explanation(self, hypotheses: List[str]) -> str:
        # Simplified: Use Occam's Razor - prefer simpler
        if hypotheses:
            return hypotheses[0] + " (simplest explanation)"
        return "Best explanation selected"

    def _extract_problem_structure(self, problem: str) -> Dict[str, Any]:
        return {'structure': 'Problem structure extracted', 'elements': []}

    def _find_analogous_case(self, target: Dict) -> Dict[str, Any]:
        return {'structure': 'Analogous case found', 'solution': 'Known solution'}

    def _map_solution(self, source: Dict, target: Dict) -> str:
        return "Solution mapped from source to target domain"

    def _extract_event(self, problem: str) -> str:
        return "Event extracted from problem"

    def _trace_causes(self, event: str) -> List[str]:
        return ["Cause 1", "Cause 2", "Cause 3"]

    def _predict_effects(self, causes: List[str]) -> List[str]:
        return ["Effect 1", "Effect 2"]


def explain_reasoning_chain(chain: ReasoningChain) -> str:
    """Generate human-readable explanation of reasoning chain"""
    explanation = [
        f"Problem: {chain.problem}",
        f"\nReasoning Process ({len(chain.steps)} steps):",
        ""
    ]

    for step in chain.steps:
        explanation.append(f"Step {step.step_number}: {step.reasoning_type.value.title()}")
        explanation.append(f"  Thought: {step.thought}")
        explanation.append(f"  Action: {step.action}")
        explanation.append(f"  Confidence: {step.confidence:.1%}")
        explanation.append("")

    explanation.append(f"Conclusion: {chain.conclusion}")
    explanation.append(f"Success: {'✅' if chain.success else '❌'}")
    explanation.append(f"Execution time: {chain.execution_time:.4f}s")

    return "\n".join(explanation)


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("Reasoning Chains Test")
    print("="*70)

    reasoner = ChainOfThoughtReasoner()

    # Test deductive reasoning
    print("\n1. DEDUCTIVE REASONING:")
    problem1 = "If all humans are mortal, and Socrates is human, is Socrates mortal?"
    chain1 = reasoner.solve_problem(problem1, ReasoningType.DEDUCTIVE)
    print(explain_reasoning_chain(chain1))

    # Test inductive reasoning
    print("\n" + "="*70)
    print("\n2. INDUCTIVE REASONING:")
    problem2 = "The sun rose today, it rose yesterday, it rose the day before. Will it rise tomorrow?"
    chain2 = reasoner.solve_problem(problem2, ReasoningType.INDUCTIVE)
    print(explain_reasoning_chain(chain2))

    # Test abductive reasoning
    print("\n" + "="*70)
    print("\n3. ABDUCTIVE REASONING:")
    problem3 = "The grass is wet. What is the most likely explanation?"
    chain3 = reasoner.solve_problem(problem3, ReasoningType.ABDUCTIVE)
    print(explain_reasoning_chain(chain3))

    print("\n" + "="*70)
    print("\n✅ Chain-of-Thought reasoning enables systematic problem solving!")
    print("="*70)
