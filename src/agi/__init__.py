"""
AGI (Artificial General Intelligence) Foundation - v4.5

Foundation for AGI capabilities with reasoning, knowledge representation, and planning.

Features:
- Multi-paradigm reasoning (deductive, inductive, abductive, analogical)
- Semantic knowledge graphs
- Goal-oriented planning and execution
- Belief management
- Causal reasoning

Version: 4.5.0 (FULL IMPLEMENTATION)
"""

__version__ = '4.5.0'

from typing import Dict, List, Optional, Any
import logging

# Import from submodules
from agi.reasoning_engine import (
    ReasoningEngine,
    ReasoningType,
    ConfidenceLevel,
    Fact,
    Rule,
    Belief,
    ReasoningResult,
)

from agi.knowledge_graph import (
    KnowledgeGraph,
    Node,
    Edge,
    Path,
    NodeType,
    EdgeType,
)

from agi.planning_system import (
    PlanningSystem,
    Goal,
    Action,
    Plan,
    WorldState,
    GoalStatus,
    ActionStatus,
)

logger = logging.getLogger(__name__)


class AGISystem:
    """
    AGI System - Integrated artificial general intelligence

    Combines:
    - Reasoning engine (multi-paradigm reasoning)
    - Knowledge graph (semantic knowledge)
    - Planning system (goal-oriented behavior)

    Example:
        >>> from agi import AGISystem
        >>> agi = AGISystem()
        >>>
        >>> # Add knowledge
        >>> agi.add_fact("Socrates", "is_a", "human")
        >>> agi.add_fact("humans", "are", "mortal")
        >>>
        >>> # Reason
        >>> result = agi.reason("Is Socrates mortal?")
        >>> print(result.conclusion)
        >>>
        >>> # Set goal
        >>> goal = Goal(
        ...     goal_id="g1",
        ...     description="Process document",
        ...     postconditions=["document_processed"]
        ... )
        >>> agi.add_goal(goal)
        >>> plan = agi.plan_for_goal("g1")
        >>> agi.execute_plan(plan.plan_id)
    """

    def __init__(self):
        """Initialize AGI System"""
        self.reasoning = ReasoningEngine()
        self.knowledge = KnowledgeGraph()
        self.planning = PlanningSystem()

        logger.info("AGI System initialized")

    # Reasoning interface

    def add_fact(self, subject: str, predicate: str, obj: Any, confidence: float = 1.0) -> None:
        """
        Add fact to knowledge base

        Args:
            subject: Subject entity
            predicate: Relation/property
            obj: Object/value
            confidence: Confidence level
        """
        # Add to reasoning engine
        self.reasoning.add_fact(subject, predicate, obj, confidence)

        # Add to knowledge graph
        self.knowledge.add_node(subject, subject, NodeType.ENTITY)
        self.knowledge.add_node(str(obj), str(obj), NodeType.ENTITY)

        # Determine edge type
        if predicate in ["is_a", "isa", "is a"]:
            edge_type = EdgeType.IS_A
        elif predicate in ["part_of", "has_part"]:
            edge_type = EdgeType.PART_OF
        elif predicate in ["has_property", "has"]:
            edge_type = EdgeType.HAS_PROPERTY
        else:
            edge_type = EdgeType.CUSTOM

        self.knowledge.add_edge(subject, str(obj), edge_type, weight=confidence)

        logger.debug(f"Added fact: {subject} {predicate} {obj}")

    def add_rule(self, rule: Rule) -> None:
        """Add inference rule"""
        self.reasoning.add_rule(rule)

    def reason(self,
              query: str,
              reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE) -> ReasoningResult:
        """
        Perform reasoning on query

        Args:
            query: Question or goal
            reasoning_type: Type of reasoning

        Returns:
            Reasoning result
        """
        return self.reasoning.reason(query, reasoning_type)

    def explain_reasoning(self, result: ReasoningResult) -> str:
        """Generate explanation of reasoning"""
        return self.reasoning.explain_reasoning(result)

    # Knowledge graph interface

    def add_entity(self, entity_id: str, label: str, properties: Optional[Dict] = None) -> None:
        """Add entity to knowledge graph"""
        self.knowledge.add_node(entity_id, label, NodeType.ENTITY, properties)

    def add_relation(self,
                    entity1: str,
                    entity2: str,
                    relation_type: str,
                    weight: float = 1.0) -> None:
        """Add relation between entities"""
        # Map relation type to EdgeType
        edge_type_map = {
            'is_a': EdgeType.IS_A,
            'part_of': EdgeType.PART_OF,
            'has_property': EdgeType.HAS_PROPERTY,
            'causes': EdgeType.CAUSES,
            'similar_to': EdgeType.SIMILAR_TO,
        }

        edge_type = edge_type_map.get(relation_type, EdgeType.CUSTOM)
        self.knowledge.add_edge(entity1, entity2, edge_type, weight)

    def find_path(self, entity1: str, entity2: str) -> Optional[Path]:
        """Find path between entities"""
        return self.knowledge.find_path(entity1, entity2)

    def get_semantic_similarity(self, entity1: str, entity2: str) -> float:
        """Get semantic similarity between entities"""
        return self.knowledge.find_semantic_similarity(entity1, entity2)

    def query_knowledge(self, entity_id: str, radius: int = 2) -> Dict[str, Any]:
        """Query knowledge around entity"""
        return self.knowledge.query_subgraph(entity_id, radius)

    # Planning interface

    def add_goal(self, goal: Goal) -> None:
        """Add goal to system"""
        self.planning.add_goal(goal)

    def register_action(self, action: Action) -> None:
        """Register available action"""
        self.planning.register_action(action)

    def plan_for_goal(self, goal_id: str) -> Optional[Plan]:
        """Create plan to achieve goal"""
        return self.planning.plan(goal_id)

    def execute_plan(self, plan_id: str) -> bool:
        """Execute plan"""
        return self.planning.execute_plan(plan_id)

    def get_goal_status(self, goal_id: str) -> Optional[GoalStatus]:
        """Get goal status"""
        goal = self.planning.goals.get(goal_id)
        return goal.status if goal else None

    def monitor_goals(self) -> Dict[str, Any]:
        """Monitor all goals"""
        return self.planning.monitor_goals()

    # Integrated capabilities

    def learn_from_example(self, example: Dict[str, Any]) -> None:
        """
        Learn from example (inductive learning)

        Args:
            example: Example with input/output
        """
        # Add example as facts
        if 'input' in example and 'output' in example:
            self.add_fact(
                str(example['input']),
                'produces',
                str(example['output'])
            )

        logger.debug("Learned from example")

    def solve_problem(self, problem: str) -> Dict[str, Any]:
        """
        Solve problem using integrated reasoning and planning

        Args:
            problem: Problem description

        Returns:
            Solution with reasoning and plan
        """
        logger.info(f"Solving problem: {problem}")

        # Step 1: Reason about problem
        reasoning_result = self.reason(problem, ReasoningType.ABDUCTIVE)

        # Step 2: Create goal from reasoning
        goal = Goal(
            goal_id=f"goal_{int(datetime.now().timestamp())}",
            description=f"Solve: {problem}",
            postconditions=[reasoning_result.conclusion]
        )
        self.add_goal(goal)

        # Step 3: Plan to achieve goal
        plan = self.plan_for_goal(goal.goal_id)

        # Step 4: Return solution
        solution = {
            'problem': problem,
            'reasoning': reasoning_result,
            'goal': goal,
            'plan': plan,
            'success': plan is not None
        }

        return solution

    def get_system_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics

        Returns:
            Statistics dict
        """
        return {
            'reasoning': {
                'facts': len(self.reasoning.facts),
                'rules': len(self.reasoning.rules),
                'beliefs': len(self.reasoning.beliefs)
            },
            'knowledge': self.knowledge.get_statistics(),
            'planning': self.planning.monitor_goals()
        }


# Singleton instance
_agi_system = None

def get_agi_system() -> AGISystem:
    """
    Get singleton AGI System instance

    Returns:
        AGISystem instance
    """
    global _agi_system
    if _agi_system is None:
        _agi_system = AGISystem()
    return _agi_system


__all__ = [
    # Main system
    'AGISystem',
    'get_agi_system',

    # Reasoning
    'ReasoningEngine',
    'ReasoningType',
    'ConfidenceLevel',
    'Fact',
    'Rule',
    'Belief',
    'ReasoningResult',

    # Knowledge
    'KnowledgeGraph',
    'Node',
    'Edge',
    'Path',
    'NodeType',
    'EdgeType',

    # Planning
    'PlanningSystem',
    'Goal',
    'Action',
    'Plan',
    'WorldState',
    'GoalStatus',
    'ActionStatus',
]
