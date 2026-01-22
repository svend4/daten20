"""
AI Agents & Autonomous Tool Use Platform v19.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 10-50x faster, full features, requires numpy

Autonomous AI agents capable of using tools, planning multi-step tasks,
managing memory, and coordinating with other agents.

Version: 19.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "19.0.0"

# ALWAYS import Pure Python version (baseline, always available)
from .ai_agents_services import (
    # Enums
    MemoryType,
    PlanningFramework,
    AgentRole,
    
    # Dataclasses
    Memory,
    Tool,
    ToolCall,
    Plan,
    Task,
    Agent,
    Observation,
    AIAgentsConfig,
    
    # Classes (Pure Python - simplified)
    AgentArchitectureMemory as AgentArchitectureMemoryPython,
    ToolCallingExecution as ToolCallingExecutionPython,
    PlanningReasoningEngine as PlanningReasoningEnginePython,
    TaskDecompositionDelegation as TaskDecompositionDelegationPython,
    EnvironmentInteractionPerception as EnvironmentInteractionPerceptionPython,
    LearningAdaptationSystem as LearningAdaptationSystemPython,
    MultiAgentOrchestration as MultiAgentOrchestrationPython,
    IntegratedAIAgentsSystem as IntegratedAIAgentsSystemPython,
    
    # Singletons (Pure Python)
    get_agent_architecture_memory as get_agent_architecture_memory_python,
    get_tool_calling_execution as get_tool_calling_execution_python,
    get_planning_reasoning_engine as get_planning_reasoning_engine_python,
    get_task_decomposition_delegation as get_task_decomposition_delegation_python,
    get_environment_interaction_perception as get_environment_interaction_perception_python,
    get_learning_adaptation_system as get_learning_adaptation_system_python,
    get_multi_agent_orchestration as get_multi_agent_orchestration_python,
    get_ai_agents_system as get_ai_agents_system_python,
)

# TRY to import NumPy version (optional, faster, full features)
try:
    from .ai_agents_services_numpy import (
        # Classes (NumPy version - full features)
        AgentArchitectureMemory as AgentArchitectureMemoryNumpy,
        ToolCallingExecution as ToolCallingExecutionNumpy,
        PlanningReasoningEngine as PlanningReasoningEngineNumpy,
        TaskDecompositionDelegation as TaskDecompositionDelegationNumpy,
        EnvironmentInteractionPerception as EnvironmentInteractionPerceptionNumpy,
        LearningAdaptationSystem as LearningAdaptationSystemNumpy,
        MultiAgentOrchestration as MultiAgentOrchestrationNumpy,
        IntegratedAIAgentsSystem as IntegratedAIAgentsSystemNumpy,
        
        # Singletons (NumPy version)
        get_agent_architecture_memory as get_agent_architecture_memory_numpy,
        get_tool_calling_execution as get_tool_calling_execution_numpy,
        get_planning_reasoning_engine as get_planning_reasoning_engine_numpy,
        get_task_decomposition_delegation as get_task_decomposition_delegation_numpy,
        get_environment_interaction_perception as get_environment_interaction_perception_numpy,
        get_learning_adaptation_system as get_learning_adaptation_system_numpy,
        get_multi_agent_orchestration as get_multi_agent_orchestration_numpy,
        get_ai_agents_system as get_ai_agents_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (10-50x faster, full features)
    AgentArchitectureMemory = AgentArchitectureMemoryNumpy
    ToolCallingExecution = ToolCallingExecutionNumpy
    PlanningReasoningEngine = PlanningReasoningEngineNumpy
    TaskDecompositionDelegation = TaskDecompositionDelegationNumpy
    EnvironmentInteractionPerception = EnvironmentInteractionPerceptionNumpy
    LearningAdaptationSystem = LearningAdaptationSystemNumpy
    MultiAgentOrchestration = MultiAgentOrchestrationNumpy
    IntegratedAIAgentsSystem = IntegratedAIAgentsSystemNumpy
    
    # Use NumPy getters
    get_agent_architecture_memory = get_agent_architecture_memory_numpy
    get_tool_calling_execution = get_tool_calling_execution_numpy
    get_planning_reasoning_engine = get_planning_reasoning_engine_numpy
    get_task_decomposition_delegation = get_task_decomposition_delegation_numpy
    get_environment_interaction_perception = get_environment_interaction_perception_numpy
    get_learning_adaptation_system = get_learning_adaptation_system_numpy
    get_multi_agent_orchestration = get_multi_agent_orchestration_numpy
    get_ai_agents_system = get_ai_agents_system_numpy
else:
    # NumPy not available - use Pure Python (simplified)
    AgentArchitectureMemory = AgentArchitectureMemoryPython
    ToolCallingExecution = ToolCallingExecutionPython
    PlanningReasoningEngine = PlanningReasoningEnginePython
    TaskDecompositionDelegation = TaskDecompositionDelegationPython
    EnvironmentInteractionPerception = EnvironmentInteractionPerceptionPython
    LearningAdaptationSystem = LearningAdaptationSystemPython
    MultiAgentOrchestration = MultiAgentOrchestrationPython
    IntegratedAIAgentsSystem = IntegratedAIAgentsSystemPython
    
    # Use Pure Python getters
    get_agent_architecture_memory = get_agent_architecture_memory_python
    get_tool_calling_execution = get_tool_calling_execution_python
    get_planning_reasoning_engine = get_planning_reasoning_engine_python
    get_task_decomposition_delegation = get_task_decomposition_delegation_python
    get_environment_interaction_perception = get_environment_interaction_perception_python
    get_learning_adaptation_system = get_learning_adaptation_system_python
    get_multi_agent_orchestration = get_multi_agent_orchestration_python
    get_ai_agents_system = get_ai_agents_system_python

__all__ = [
    # Version
    "__version__",
    
    # Enums
    "MemoryType",
    "PlanningFramework",
    "AgentRole",
    
    # Dataclasses
    "Memory",
    "Tool",
    "ToolCall",
    "Plan",
    "Task",
    "Agent",
    "Observation",
    "AIAgentsConfig",
    
    # Core Systems (auto-select best version)
    "AgentArchitectureMemory",
    "ToolCallingExecution",
    "PlanningReasoningEngine",
    "TaskDecompositionDelegation",
    "EnvironmentInteractionPerception",
    "LearningAdaptationSystem",
    "MultiAgentOrchestration",
    "IntegratedAIAgentsSystem",
    
    # Pure Python versions (always available)
    "AgentArchitectureMemoryPython",
    "ToolCallingExecutionPython",
    "PlanningReasoningEnginePython",
    "TaskDecompositionDelegationPython",
    "EnvironmentInteractionPerceptionPython",
    "LearningAdaptationSystemPython",
    "MultiAgentOrchestrationPython",
    "IntegratedAIAgentsSystemPython",
    
    # Singletons
    "get_agent_architecture_memory",
    "get_tool_calling_execution",
    "get_planning_reasoning_engine",
    "get_task_decomposition_delegation",
    "get_environment_interaction_perception",
    "get_learning_adaptation_system",
    "get_multi_agent_orchestration",
    "get_ai_agents_system",
    
    # Pure Python singleton getters
    "get_agent_architecture_memory_python",
    "get_tool_calling_execution_python",
    "get_planning_reasoning_engine_python",
    "get_task_decomposition_delegation_python",
    "get_environment_interaction_perception_python",
    "get_learning_adaptation_system_python",
    "get_multi_agent_orchestration_python",
    "get_ai_agents_system_python",
    
    # Dual-version flag
    "HAS_NUMPY",
]
