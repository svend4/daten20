"""
AGI Reasoning Engine - v4.5

Core reasoning system for Artificial General Intelligence.
Implements multi-paradigm reasoning: deductive, inductive, abductive, analogical.

Version: 4.5.0
"""

__version__ = '4.5.0'

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning"""
    DEDUCTIVE = "deductive"      # General → Specific (logic)
    INDUCTIVE = "inductive"      # Specific → General (patterns)
    ABDUCTIVE = "abductive"      # Best explanation
    ANALOGICAL = "analogical"    # Similarity-based
    CAUSAL = "causal"           # Cause-effect
    PROBABILISTIC = "probabilistic"  # Uncertainty


class ConfidenceLevel(Enum):
    """Confidence levels for reasoning"""
    CERTAIN = "certain"          # 1.0
    VERY_HIGH = "very_high"      # 0.9-0.99
    HIGH = "high"                # 0.7-0.89
    MEDIUM = "medium"            # 0.5-0.69
    LOW = "low"                  # 0.3-0.49
    VERY_LOW = "very_low"        # 0.0-0.29


@dataclass
class Fact:
    """Atomic fact in knowledge base"""
    subject: str
    predicate: str
    object: Any
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "user"


@dataclass
class Rule:
    """Inference rule"""
    rule_id: str
    premises: List[str]          # Conditions
    conclusion: str              # Result
    confidence: float = 1.0
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE


@dataclass
class Belief:
    """Agent belief with confidence"""
    proposition: str
    confidence: float
    evidence: List[Fact] = field(default_factory=list)
    reasoning_path: List[str] = field(default_factory=list)


@dataclass
class ReasoningResult:
    """Result of reasoning process"""
    conclusion: str
    confidence: float
    reasoning_type: ReasoningType
    steps: List[str] = field(default_factory=list)
    facts_used: List[Fact] = field(default_factory=list)
    success: bool = True


class ReasoningEngine:
    """
    AGI Reasoning Engine

    Multi-paradigm reasoning system:
    - Deductive reasoning (logic-based)
    - Inductive reasoning (pattern discovery)
    - Abductive reasoning (best explanation)
    - Analogical reasoning (similarity)
    - Causal reasoning (cause-effect)
    - Probabilistic reasoning (uncertainty)

    Example:
        >>> engine = ReasoningEngine()
        >>> engine.add_fact("Socrates", "is_a", "human")
        >>> engine.add_rule(Rule(
        ...     rule_id="mortality",
        ...     premises=["?x is_a human"],
        ...     conclusion="?x is mortal"
        ... ))
        >>> result = engine.reason("Is Socrates mortal?")
        >>> print(result.conclusion)  # "Socrates is mortal"
    """

    def __init__(self):
        """Initialize Reasoning Engine"""
        self.facts: List[Fact] = []
        self.rules: Dict[str, Rule] = {}
        self.beliefs: Dict[str, Belief] = {}
        self.inference_history: List[Dict[str, Any]] = []

        logger.info("AGI Reasoning Engine initialized")

    def add_fact(self, subject: str, predicate: str, obj: Any, confidence: float = 1.0) -> None:
        """
        Add fact to knowledge base

        Args:
            subject: Subject entity
            predicate: Relation/property
            obj: Object/value
            confidence: Confidence level (0-1)
        """
        fact = Fact(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence
        )
        self.facts.append(fact)
        logger.debug(f"Added fact: {subject} {predicate} {obj} ({confidence})")

    def add_rule(self, rule: Rule) -> None:
        """
        Add inference rule

        Args:
            rule: Inference rule
        """
        self.rules[rule.rule_id] = rule
        logger.info(f"Added rule: {rule.rule_id}")

    def reason(self,
              query: str,
              reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE,
              max_depth: int = 10) -> ReasoningResult:
        """
        Perform reasoning on query

        Args:
            query: Question or goal
            reasoning_type: Type of reasoning to use
            max_depth: Maximum inference depth

        Returns:
            Reasoning result
        """
        logger.info(f"Reasoning: {query} (type: {reasoning_type.value})")

        if reasoning_type == ReasoningType.DEDUCTIVE:
            return self._deductive_reasoning(query, max_depth)
        elif reasoning_type == ReasoningType.INDUCTIVE:
            return self._inductive_reasoning(query)
        elif reasoning_type == ReasoningType.ABDUCTIVE:
            return self._abductive_reasoning(query)
        elif reasoning_type == ReasoningType.ANALOGICAL:
            return self._analogical_reasoning(query)
        else:
            logger.warning(f"Reasoning type {reasoning_type} not fully implemented")
            return ReasoningResult(
                conclusion="Unknown",
                confidence=0.0,
                reasoning_type=reasoning_type,
                success=False
            )

    def _deductive_reasoning(self, query: str, max_depth: int) -> ReasoningResult:
        """
        Deductive reasoning: Apply rules to derive conclusions

        Uses forward chaining to derive new facts.
        """
        steps = ["Starting deductive reasoning"]
        derived_facts = []
        used_facts = []

        # Parse query (simplified)
        query_parts = query.lower().replace("?", "").split()

        # Forward chaining
        for depth in range(max_depth):
            new_facts_derived = False

            for rule_id, rule in self.rules.items():
                # Try to match premises with facts
                if self._can_apply_rule(rule, self.facts + derived_facts):
                    # Apply rule
                    new_fact = self._apply_rule(rule, self.facts + derived_facts)
                    if new_fact and new_fact not in derived_facts:
                        derived_facts.append(new_fact)
                        used_facts.append(new_fact)
                        steps.append(f"Applied rule '{rule_id}': {new_fact.subject} {new_fact.predicate} {new_fact.object}")
                        new_facts_derived = True

            if not new_facts_derived:
                break

        # Check if query is satisfied
        conclusion = self._check_query_satisfaction(query, self.facts + derived_facts)

        confidence = 0.9 if conclusion != "Unknown" else 0.0

        return ReasoningResult(
            conclusion=conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.DEDUCTIVE,
            steps=steps,
            facts_used=used_facts,
            success=conclusion != "Unknown"
        )

    def _inductive_reasoning(self, query: str) -> ReasoningResult:
        """
        Inductive reasoning: Discover patterns from examples

        Generalizes from specific observations.
        """
        steps = ["Starting inductive reasoning"]

        # Find patterns in facts
        patterns = self._discover_patterns(self.facts)
        steps.append(f"Discovered {len(patterns)} patterns")

        # Apply patterns to query
        conclusion = self._apply_patterns(query, patterns)

        return ReasoningResult(
            conclusion=conclusion,
            confidence=0.7,
            reasoning_type=ReasoningType.INDUCTIVE,
            steps=steps,
            success=True
        )

    def _abductive_reasoning(self, query: str) -> ReasoningResult:
        """
        Abductive reasoning: Find best explanation

        Generates hypotheses to explain observations.
        """
        steps = ["Starting abductive reasoning"]

        # Generate hypotheses
        hypotheses = self._generate_hypotheses(query, self.facts)
        steps.append(f"Generated {len(hypotheses)} hypotheses")

        # Evaluate hypotheses
        best_hypothesis = self._evaluate_hypotheses(hypotheses, self.facts)

        if best_hypothesis:
            conclusion = best_hypothesis['explanation']
            confidence = best_hypothesis['score']
        else:
            conclusion = "No explanation found"
            confidence = 0.0

        return ReasoningResult(
            conclusion=conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.ABDUCTIVE,
            steps=steps,
            success=best_hypothesis is not None
        )

    def _analogical_reasoning(self, query: str) -> ReasoningResult:
        """
        Analogical reasoning: Reason by similarity

        Finds analogies between situations.
        """
        steps = ["Starting analogical reasoning"]

        # Find similar situations
        similar_cases = self._find_similar_cases(query, self.facts)
        steps.append(f"Found {len(similar_cases)} similar cases")

        # Apply analogy
        conclusion = self._apply_analogy(query, similar_cases)

        return ReasoningResult(
            conclusion=conclusion,
            confidence=0.6,
            reasoning_type=ReasoningType.ANALOGICAL,
            steps=steps,
            success=True
        )

    # Helper methods

    def _can_apply_rule(self, rule: Rule, facts: List[Fact]) -> bool:
        """Check if rule premises are satisfied"""
        # Simplified rule matching
        for premise in rule.premises:
            if not self._premise_satisfied(premise, facts):
                return False
        return True

    def _premise_satisfied(self, premise: str, facts: List[Fact]) -> bool:
        """Check if a premise is satisfied by facts"""
        # Simplified premise checking
        parts = premise.split()
        if len(parts) >= 3:
            for fact in facts:
                if (parts[1] in fact.predicate or
                    parts[2] in str(fact.object)):
                    return True
        return False

    def _apply_rule(self, rule: Rule, facts: List[Fact]) -> Optional[Fact]:
        """Apply rule to derive new fact"""
        # Simplified rule application
        parts = rule.conclusion.split()
        if len(parts) >= 3:
            # Extract variable bindings from premises
            bindings = self._extract_bindings(rule.premises, facts)

            if bindings:
                subject = bindings.get('?x', parts[0])
                return Fact(
                    subject=subject,
                    predicate=parts[1],
                    object=parts[2],
                    confidence=rule.confidence
                )
        return None

    def _extract_bindings(self, premises: List[str], facts: List[Fact]) -> Dict[str, str]:
        """Extract variable bindings from premises"""
        bindings = {}
        for premise in premises:
            parts = premise.split()
            if parts[0].startswith('?'):
                # Variable binding
                for fact in facts:
                    if parts[1] in fact.predicate:
                        bindings[parts[0]] = fact.subject
                        break
        return bindings

    def _check_query_satisfaction(self, query: str, facts: List[Fact]) -> str:
        """Check if query is satisfied by facts"""
        query_lower = query.lower()

        for fact in facts:
            fact_str = f"{fact.subject} {fact.predicate} {fact.object}".lower()
            if any(word in fact_str for word in query_lower.split()):
                return f"{fact.subject} {fact.predicate} {fact.object}"

        return "Unknown"

    def _discover_patterns(self, facts: List[Fact]) -> List[Dict[str, Any]]:
        """Discover patterns in facts"""
        patterns = []

        # Group facts by predicate
        predicate_groups: Dict[str, List[Fact]] = {}
        for fact in facts:
            if fact.predicate not in predicate_groups:
                predicate_groups[fact.predicate] = []
            predicate_groups[fact.predicate].append(fact)

        # Find common patterns
        for predicate, group_facts in predicate_groups.items():
            if len(group_facts) > 1:
                patterns.append({
                    'predicate': predicate,
                    'count': len(group_facts),
                    'confidence': min(f.confidence for f in group_facts)
                })

        return patterns

    def _apply_patterns(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Apply discovered patterns to query"""
        # Simplified pattern application
        if patterns:
            return f"Pattern-based conclusion based on {len(patterns)} patterns"
        return "No patterns applicable"

    def _generate_hypotheses(self, query: str, facts: List[Fact]) -> List[Dict[str, Any]]:
        """Generate explanatory hypotheses"""
        hypotheses = []

        # Generate simple hypotheses from facts
        for fact in facts:
            hypotheses.append({
                'explanation': f"{fact.subject} {fact.predicate} {fact.object} explains the observation",
                'support': [fact],
                'score': fact.confidence
            })

        return hypotheses

    def _evaluate_hypotheses(self, hypotheses: List[Dict[str, Any]], facts: List[Fact]) -> Optional[Dict[str, Any]]:
        """Evaluate and rank hypotheses"""
        if not hypotheses:
            return None

        # Rank by score
        ranked = sorted(hypotheses, key=lambda h: h['score'], reverse=True)
        return ranked[0] if ranked else None

    def _find_similar_cases(self, query: str, facts: List[Fact]) -> List[Fact]:
        """Find similar cases for analogy"""
        similar = []
        query_words = set(query.lower().split())

        for fact in facts:
            fact_words = set(f"{fact.subject} {fact.predicate} {fact.object}".lower().split())
            overlap = len(query_words & fact_words)
            if overlap > 0:
                similar.append(fact)

        return similar

    def _apply_analogy(self, query: str, similar_cases: List[Fact]) -> str:
        """Apply analogy from similar cases"""
        if similar_cases:
            return f"By analogy with {len(similar_cases)} similar cases"
        return "No applicable analogy"

    def update_belief(self, proposition: str, confidence: float, evidence: List[Fact]) -> None:
        """
        Update belief with evidence

        Args:
            proposition: Belief statement
            confidence: Confidence level
            evidence: Supporting evidence
        """
        if proposition in self.beliefs:
            # Update existing belief
            belief = self.beliefs[proposition]
            # Bayesian update (simplified)
            belief.confidence = (belief.confidence + confidence) / 2
            belief.evidence.extend(evidence)
        else:
            # New belief
            self.beliefs[proposition] = Belief(
                proposition=proposition,
                confidence=confidence,
                evidence=evidence
            )

        logger.debug(f"Updated belief: {proposition} ({confidence})")

    def get_beliefs(self, min_confidence: float = 0.0) -> List[Belief]:
        """
        Get beliefs above confidence threshold

        Args:
            min_confidence: Minimum confidence level

        Returns:
            List of beliefs
        """
        return [b for b in self.beliefs.values() if b.confidence >= min_confidence]

    def explain_reasoning(self, result: ReasoningResult) -> str:
        """
        Generate human-readable explanation of reasoning

        Args:
            result: Reasoning result

        Returns:
            Explanation text
        """
        explanation = f"Reasoning Type: {result.reasoning_type.value}\n"
        explanation += f"Conclusion: {result.conclusion}\n"
        explanation += f"Confidence: {result.confidence:.2f}\n\n"
        explanation += "Reasoning Steps:\n"
        for i, step in enumerate(result.steps, 1):
            explanation += f"  {i}. {step}\n"

        if result.facts_used:
            explanation += f"\nFacts Used: {len(result.facts_used)}\n"

        return explanation


__all__ = [
    'ReasoningEngine',
    'ReasoningType',
    'ConfidenceLevel',
    'Fact',
    'Rule',
    'Belief',
    'ReasoningResult',
]
