"""
AI Agents & Autonomous Tool Use Platform v19.0

Autonomous AI agents capable of using tools, planning multi-step tasks,
managing memory, and coordinating with other agents.

Example usage:
    from ai_agents import get_tool_calling_execution, get_planning_reasoning_engine

    # Create tool system
    tools = get_tool_calling_execution()

    # Call a tool
    result = await tools.call_tool("calculator", {"expression": "2 + 2"})

    # Create and execute a plan
    planner = get_planning_reasoning_engine()
    plan = await planner.create_plan("Find information about AI agents")
    execution = await planner.execute_plan(plan.plan_id, tools)
"""

__version__ = '19.0.0'
__author__ = 'Document Management System Team'

from .ai_agents_services import (
    # Core Systems
    AgentArchitectureMemory,
    ToolCallingExecution,
    PlanningReasoningEngine,
    TaskDecompositionDelegation,
    EnvironmentInteractionPerception,
    LearningAdaptationSystem,
    MultiAgentOrchestration,

    # Enums
    MemoryType,
    PlanningFramework,
    AgentRole,

    # Data Classes
    Memory,
    Tool,
    ToolCall,
    Plan,
    Task,
    Agent,
    Observation,

    # Singleton Getters
    get_agent_architecture_memory,
    get_tool_calling_execution,
    get_planning_reasoning_engine,
    get_task_decomposition_delegation,
    get_environment_interaction_perception,
    get_learning_adaptation_system,
    get_multi_agent_orchestration,
)

__all__ = [
    '__version__',
    'AgentArchitectureMemory',
    'ToolCallingExecution',
    'PlanningReasoningEngine',
    'TaskDecompositionDelegation',
    'EnvironmentInteractionPerception',
    'LearningAdaptationSystem',
    'MultiAgentOrchestration',
    'MemoryType',
    'PlanningFramework',
    'AgentRole',
    'Memory',
    'Tool',
    'ToolCall',
    'Plan',
    'Task',
    'Agent',
    'Observation',
    'get_agent_architecture_memory',
    'get_tool_calling_execution',
    'get_planning_reasoning_engine',
    'get_task_decomposition_delegation',
    'get_environment_interaction_perception',
    'get_learning_adaptation_system',
    'get_multi_agent_orchestration',
]
