"""
AGI Planning System - v4.5

Goal-oriented planning and action execution for AGI.

Version: 4.5.0
"""

__version__ = '4.5.0'

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GoalStatus(Enum):
    """Goal status"""
    PENDING = "pending"
    ACTIVE = "active"
    ACHIEVED = "achieved"
    FAILED = "failed"
    PAUSED = "paused"


class ActionStatus(Enum):
    """Action execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Goal:
    """Goal representation"""
    goal_id: str
    description: str
    priority: int = 5        # 1-10, higher = more important
    deadline: Optional[datetime] = None
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    parent_goal_id: Optional[str] = None


@dataclass
class Action:
    """Executable action"""
    action_id: str
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    cost: float = 1.0
    duration: float = 1.0    # seconds
    executor: Optional[Callable] = None


@dataclass
class Plan:
    """Action plan"""
    plan_id: str
    goal_id: str
    actions: List[Action] = field(default_factory=list)
    total_cost: float = 0.0
    estimated_duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorldState:
    """Current world state"""
    facts: Dict[str, bool] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class PlanningSystem:
    """
    AGI Planning System

    Goal-oriented planning using STRIPS-like planning:
    - Goal decomposition
    - Action planning (STRIPS, HTN)
    - Plan execution and monitoring
    - Replanning on failure
    - Multi-goal management

    Example:
        >>> planner = PlanningSystem()
        >>> goal = Goal(
        ...     goal_id="g1",
        ...     description="Process document",
        ...     postconditions=["document_processed"]
        ... )
        >>> planner.add_goal(goal)
        >>> plan = planner.plan(goal.goal_id)
        >>> planner.execute_plan(plan.plan_id)
    """

    def __init__(self):
        """Initialize Planning System"""
        self.goals: Dict[str, Goal] = {}
        self.actions: Dict[str, Action] = {}
        self.plans: Dict[str, Plan] = {}
        self.world_state = WorldState()
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("AGI Planning System initialized")

    def add_goal(self, goal: Goal) -> None:
        """
        Add goal to system

        Args:
            goal: Goal to add
        """
        self.goals[goal.goal_id] = goal
        logger.info(f"Added goal: {goal.goal_id} - {goal.description}")

    def register_action(self, action: Action) -> None:
        """
        Register available action

        Args:
            action: Action to register
        """
        self.actions[action.action_id] = action
        logger.debug(f"Registered action: {action.action_id}")

    def plan(self, goal_id: str, max_depth: int = 10) -> Optional[Plan]:
        """
        Create plan to achieve goal

        Uses forward search with heuristic guidance.

        Args:
            goal_id: Goal identifier
            max_depth: Maximum planning depth

        Returns:
            Plan or None if no plan found
        """
        if goal_id not in self.goals:
            logger.error(f"Goal not found: {goal_id}")
            return None

        goal = self.goals[goal_id]
        logger.info(f"Planning for goal: {goal.description}")

        # Decompose goal if needed
        subgoals = self._decompose_goal(goal)

        if subgoals:
            logger.debug(f"Decomposed into {len(subgoals)} subgoals")

        # STRIPS-like planning
        plan = self._strips_planning(goal, max_depth)

        if plan:
            plan.goal_id = goal_id
            self.plans[plan.plan_id] = plan
            logger.info(f"Created plan: {len(plan.actions)} actions")
        else:
            logger.warning(f"Failed to create plan for goal: {goal_id}")

        return plan

    def _strips_planning(self, goal: Goal, max_depth: int) -> Optional[Plan]:
        """
        STRIPS planning algorithm

        Args:
            goal: Goal to achieve
            max_depth: Maximum depth

        Returns:
            Plan or None
        """
        plan_id = f"plan_{goal.goal_id}_{int(datetime.now().timestamp())}"

        # Start with current world state
        current_state = self.world_state.facts.copy()

        # Forward search
        action_sequence = []
        for depth in range(max_depth):
            # Check if goal achieved
            if self._goal_satisfied(goal, current_state):
                # Create plan
                plan = Plan(
                    plan_id=plan_id,
                    goal_id=goal.goal_id,
                    actions=action_sequence,
                    total_cost=sum(a.cost for a in action_sequence),
                    estimated_duration=sum(a.duration for a in action_sequence)
                )
                return plan

            # Find applicable actions
            applicable = self._find_applicable_actions(current_state)

            if not applicable:
                break

            # Select best action (heuristic: closest to goal)
            best_action = self._select_best_action(applicable, goal, current_state)

            if not best_action:
                break

            # Apply action
            action_sequence.append(best_action)
            current_state = self._apply_action(best_action, current_state)

        return None

    def execute_plan(self, plan_id: str) -> bool:
        """
        Execute plan

        Args:
            plan_id: Plan identifier

        Returns:
            True if execution successful
        """
        if plan_id not in self.plans:
            logger.error(f"Plan not found: {plan_id}")
            return False

        plan = self.plans[plan_id]
        goal = self.goals.get(plan.goal_id)

        if not goal:
            logger.error(f"Goal not found for plan: {plan_id}")
            return False

        logger.info(f"Executing plan: {plan_id} ({len(plan.actions)} actions)")
        goal.status = GoalStatus.ACTIVE

        # Execute actions sequentially
        for i, action in enumerate(plan.actions):
            logger.info(f"Executing action {i+1}/{len(plan.actions)}: {action.name}")

            success = self._execute_action(action)

            if not success:
                logger.error(f"Action failed: {action.name}")
                goal.status = GoalStatus.FAILED

                # Attempt replanning
                logger.info("Attempting replanning...")
                new_plan = self.plan(plan.goal_id)

                if new_plan:
                    return self.execute_plan(new_plan.plan_id)
                else:
                    return False

        # Check if goal achieved
        if self._goal_satisfied(goal, self.world_state.facts):
            goal.status = GoalStatus.ACHIEVED
            logger.info(f"Goal achieved: {goal.description}")
            return True
        else:
            goal.status = GoalStatus.FAILED
            logger.warning(f"Goal not achieved after plan execution: {goal.description}")
            return False

    def _decompose_goal(self, goal: Goal) -> List[Goal]:
        """Decompose complex goal into subgoals"""
        subgoals = []

        # Simple decomposition based on postconditions
        for i, postcondition in enumerate(goal.postconditions):
            subgoal = Goal(
                goal_id=f"{goal.goal_id}_sub{i}",
                description=f"Achieve: {postcondition}",
                postconditions=[postcondition],
                parent_goal_id=goal.goal_id
            )
            subgoals.append(subgoal)
            self.add_goal(subgoal)

        return subgoals

    def _goal_satisfied(self, goal: Goal, state: Dict[str, bool]) -> bool:
        """Check if goal is satisfied in given state"""
        for postcondition in goal.postconditions:
            if not state.get(postcondition, False):
                return False
        return True

    def _find_applicable_actions(self, state: Dict[str, bool]) -> List[Action]:
        """Find actions whose preconditions are satisfied"""
        applicable = []

        for action in self.actions.values():
            if self._preconditions_satisfied(action, state):
                applicable.append(action)

        return applicable

    def _preconditions_satisfied(self, action: Action, state: Dict[str, bool]) -> bool:
        """Check if action preconditions are satisfied"""
        for precondition in action.preconditions:
            if not state.get(precondition, False):
                return False
        return True

    def _select_best_action(self,
                           actions: List[Action],
                           goal: Goal,
                           state: Dict[str, bool]) -> Optional[Action]:
        """Select best action using heuristic"""
        if not actions:
            return None

        # Heuristic: action that achieves most goal postconditions
        best_action = None
        best_score = -1

        for action in actions:
            score = 0
            for effect in action.effects:
                if effect in goal.postconditions:
                    score += 1

            # Prefer lower cost
            score -= action.cost * 0.1

            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def _apply_action(self, action: Action, state: Dict[str, bool]) -> Dict[str, bool]:
        """Apply action effects to state"""
        new_state = state.copy()

        for effect in action.effects:
            new_state[effect] = True

        return new_state

    def _execute_action(self, action: Action) -> bool:
        """Execute single action"""
        try:
            if action.executor:
                # Call action executor
                result = action.executor(action.parameters)

                # Record execution
                self.execution_history.append({
                    'action': action.name,
                    'timestamp': datetime.now(),
                    'success': result,
                    'parameters': action.parameters
                })

                # Update world state
                if result:
                    for effect in action.effects:
                        self.world_state.facts[effect] = True

                return result
            else:
                # Simulate execution
                logger.debug(f"Simulated execution: {action.name}")
                for effect in action.effects:
                    self.world_state.facts[effect] = True
                return True

        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return False

    def monitor_goals(self) -> Dict[str, Any]:
        """
        Monitor status of all goals

        Returns:
            Goal status summary
        """
        status_counts = {
            'pending': 0,
            'active': 0,
            'achieved': 0,
            'failed': 0,
            'paused': 0
        }

        for goal in self.goals.values():
            status_counts[goal.status.value] += 1

        return {
            'total_goals': len(self.goals),
            'status_counts': status_counts,
            'active_goals': [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        }

    def get_next_goal(self) -> Optional[Goal]:
        """
        Get next goal to pursue (highest priority pending goal)

        Returns:
            Next goal or None
        """
        pending_goals = [g for g in self.goals.values() if g.status == GoalStatus.PENDING]

        if not pending_goals:
            return None

        # Sort by priority (descending)
        pending_goals.sort(key=lambda g: g.priority, reverse=True)

        return pending_goals[0]


__all__ = [
    'PlanningSystem',
    'Goal',
    'Action',
    'Plan',
    'WorldState',
    'GoalStatus',
    'ActionStatus',
]
