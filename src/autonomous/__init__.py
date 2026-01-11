"""
Autonomous Agent Ecosystem Module (v12.0)

This module provides comprehensive autonomous agent capabilities for creating
intelligent, goal-oriented agents capable of reasoning, planning, acting,
learning, and collaborating.

Core Systems:
- Agent Orchestrator: Multi-agent coordination and task allocation
- Reasoning Engine: Symbolic and neural reasoning, planning
- Action Executor: Tool use, API integration, environment interaction
- Memory System: Episodic, semantic, procedural, and working memory
- Learning Module: Reinforcement learning, meta-learning, skill acquisition
- Communication Framework: Inter-agent messaging and negotiation
- Goal Management: Hierarchical planning and dynamic replanning

Example Usage:
    from autonomous import get_agent_orchestrator, get_reasoning_engine

    # Register an agent
    orchestrator = get_agent_orchestrator()
    profile = await orchestrator.register_agent(
        agent_id="agent_1",
        capabilities=["research", "coding"],
        skills={"python": 0.9, "analysis": 0.8},
        specializations=["data_science"]
    )

    # Reason about a problem
    reasoner = get_reasoning_engine()
    await reasoner.add_fact("has_data(sensor_1)")
    await reasoner.add_rule("r1", ["has_data(X)"], "can_analyze(X)")
    result = await reasoner.forward_chain("can_analyze(sensor_1)")
"""

from .autonomous_services import (
    # Enums
    AgentStatus,
    TaskPriority,
    ReasoningMode,
    MemoryType,
    LearningAlgorithm,
    MessageType,
    GoalType,
    GoalStatus,

    # Data Classes
    AgentProfile,
    Task,
    InferenceResult,
    Action,
    ActionResult,
    Memory,
    Episode,
    Experience,
    Policy,
    Message,
    Goal,
    Plan,

    # Service Classes
    AgentOrchestrator,
    ReasoningEngine,
    ActionExecutor,
    MemorySystem,
    LearningModule,
    CommunicationFramework,
    GoalManagementSystem,

    # Singleton Getters
    get_agent_orchestrator,
    get_reasoning_engine,
    get_action_executor,
    get_memory_system,
    get_learning_module,
    get_communication_framework,
    get_goal_management_system,
)

__version__ = '12.0.0'
__all__ = [
    # Enums
    'AgentStatus',
    'TaskPriority',
    'ReasoningMode',
    'MemoryType',
    'LearningAlgorithm',
    'MessageType',
    'GoalType',
    'GoalStatus',

    # Data Classes
    'AgentProfile',
    'Task',
    'InferenceResult',
    'Action',
    'ActionResult',
    'Memory',
    'Episode',
    'Experience',
    'Policy',
    'Message',
    'Goal',
    'Plan',

    # Service Classes
    'AgentOrchestrator',
    'ReasoningEngine',
    'ActionExecutor',
    'MemorySystem',
    'LearningModule',
    'CommunicationFramework',
    'GoalManagementSystem',

    # Singleton Getters
    'get_agent_orchestrator',
    'get_reasoning_engine',
    'get_action_executor',
    'get_memory_system',
    'get_learning_module',
    'get_communication_framework',
    'get_goal_management_system',
]
