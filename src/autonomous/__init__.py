"""
🚀 Fully Autonomous Platform Module

Provides complete system autonomy with self-learning, multi-agent coordination,
autonomous planning, self-monitoring, goal generation, and human-AI collaboration.

Version: 5.0.0
"""

__version__ = '5.0.0'

from .autonomous_services import (
    # Autonomous Decision Engine
    DecisionType,
    DecisionContext,
    DecisionResult,
    AutonomousDecisionEngine,
    get_decision_engine,

    # Self-Learning System
    LearningMode,
    LearningTask,
    LearningProgress,
    SelfLearningSystem,
    get_self_learning_system,

    # Multi-Agent Coordinator
    AgentRole,
    Agent,
    CollaborativeTask,
    MultiAgentCoordinator,
    get_multi_agent_coordinator,

    # Autonomous Planner
    PlanType,
    PlanningGoal,
    Plan,
    AutonomousPlanner,
    get_autonomous_planner,

    # Self-Monitor & Repair
    HealthStatus,
    SystemMetric,
    Anomaly,
    RepairAction,
    SelfMonitor,
    get_self_monitor,

    # Goal Generator
    GoalSource,
    Goal,
    GoalProgress,
    GoalGenerator,
    get_goal_generator,

    # Human-AI Collaborator
    AutonomyLevel,
    HumanRequest,
    CollaborationSession,
    HumanAICollaborator,
    get_human_ai_collaborator,
)

__all__ = [
    # Autonomous Decision Engine
    'DecisionType',
    'DecisionContext',
    'DecisionResult',
    'AutonomousDecisionEngine',
    'get_decision_engine',

    # Self-Learning System
    'LearningMode',
    'LearningTask',
    'LearningProgress',
    'SelfLearningSystem',
    'get_self_learning_system',

    # Multi-Agent Coordinator
    'AgentRole',
    'Agent',
    'CollaborativeTask',
    'MultiAgentCoordinator',
    'get_multi_agent_coordinator',

    # Autonomous Planner
    'PlanType',
    'PlanningGoal',
    'Plan',
    'AutonomousPlanner',
    'get_autonomous_planner',

    # Self-Monitor & Repair
    'HealthStatus',
    'SystemMetric',
    'Anomaly',
    'RepairAction',
    'SelfMonitor',
    'get_self_monitor',

    # Goal Generator
    'GoalSource',
    'Goal',
    'GoalProgress',
    'GoalGenerator',
    'get_goal_generator',

    # Human-AI Collaborator
    'AutonomyLevel',
    'HumanRequest',
    'CollaborationSession',
    'HumanAICollaborator',
    'get_human_ai_collaborator',
]
