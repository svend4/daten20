"""
🤖 Autonomous Agent Ecosystem - v12.0

Comprehensive autonomous agent platform providing intelligent, goal-oriented agents
capable of reasoning, planning, acting, learning, and collaborating.

Version: 12.0.0 (FULL IMPLEMENTATION)
"""

from .autonomous_agents_services import (
    # Enumerations
    AgentArchitecture,
    ReasoningType,
    ActionType,
    MemoryType,
    LearningStrategy,
    CommunicationProtocol,
    GoalType,
    GoalStatus,
    # Dataclasses
    AgentProfile,
    AgentState,
    Task,
    Action,
    ReasoningTrace,
    Memory,
    Skill,
    Message,
    Goal,
    Plan,
    AutonomousAgentConfig,
    # Subsystems
    AgentOrchestrator,
    ReasoningEngine,
    ActionExecutor,
    MemorySystem,
    LearningModule,
    CommunicationFramework,
    GoalManagement,
    # Integrated System
    IntegratedAutonomousAgentSystem,
    # Singleton
    get_autonomous_agent_system
)

__all__ = [
    # Enumerations
    'AgentArchitecture',
    'ReasoningType',
    'ActionType',
    'MemoryType',
    'LearningStrategy',
    'CommunicationProtocol',
    'GoalType',
    'GoalStatus',
    # Dataclasses
    'AgentProfile',
    'AgentState',
    'Task',
    'Action',
    'ReasoningTrace',
    'Memory',
    'Skill',
    'Message',
    'Goal',
    'Plan',
    'AutonomousAgentConfig',
    # Subsystems
    'AgentOrchestrator',
    'ReasoningEngine',
    'ActionExecutor',
    'MemorySystem',
    'LearningModule',
    'CommunicationFramework',
    'GoalManagement',
    # Integrated System
    'IntegratedAutonomousAgentSystem',
    # Singleton
    'get_autonomous_agent_system'
]

__version__ = '12.0.0'
