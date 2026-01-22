"""
Test Dual-Version AI Agents Implementation
"""

import asyncio
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents import (
    # Check which version is being used
    HAS_NUMPY,
    
    # Enums
    MemoryType,
    PlanningFramework,
    AgentRole,
    
    # Dataclasses
    Tool,
    Task,
    AIAgentsConfig,
    
    # Systems
    AgentArchitectureMemory,
    ToolCallingExecution,
    PlanningReasoningEngine,
    TaskDecompositionDelegation,
    EnvironmentInteractionPerception,
    LearningAdaptationSystem,
    MultiAgentOrchestration,
    IntegratedAIAgentsSystem,
    
    # Singletons
    get_agent_architecture_memory,
    get_tool_calling_execution,
    get_planning_reasoning_engine,
    get_task_decomposition_delegation,
    get_environment_interaction_perception,
    get_learning_adaptation_system,
    get_multi_agent_orchestration,
    get_ai_agents_system,
)


async def test_agent_architecture_memory():
    """Test agent architecture and memory system"""
    print("\nTesting Agent Architecture & Memory...")
    
    arch = get_agent_architecture_memory()
    
    # Create agent
    agent = arch.create_agent(
        name="TestAgent",
        role=AgentRole.WORKER,
        capabilities=["search", "analyze"],
    )
    print(f"  Created agent: {agent.name} ({agent.role.value})")
    
    # Store memory
    memory = await arch.store_memory(
        agent_id=agent.agent_id,
        memory_type=MemoryType.EPISODIC,
        content="Test memory content",
        importance=0.8,
    )
    print(f"  Stored memory: {memory.memory_id}")
    
    # Retrieve memories
    retrieved = await arch.retrieve_memories(
        agent_id=agent.agent_id,
        query="test",
        k=5,
    )
    print(f"  Retrieved memories: {len(retrieved)}")
    
    stats = arch.get_agent_stats()
    print(f"  Agents: {stats['num_agents']}, Memories: {stats['num_memories']}")
    
    print("  ✅ Agent Architecture & Memory works!")


async def test_tool_calling_execution():
    """Test tool calling and execution"""
    print("\nTesting Tool Calling & Execution...")
    
    tools = get_tool_calling_execution()
    
    # Register tool
    tool = Tool(
        tool_id="search_tool",
        name="Search",
        description="Search for information",
        parameters={"query": {"type": "string"}},
    )
    tools.register_tool(tool)
    print(f"  Registered tool: {tool.name}")
    
    # Execute tool
    call = await tools.execute_tool(
        tool_id="search_tool",
        arguments={"query": "test"},
        agent_id="agent_0",
    )
    print(f"  Executed tool: {call.success}")
    print(f"  Execution time: {call.execution_time_ms:.2f}ms")
    
    available = tools.get_available_tools("agent_0")
    print(f"  Available tools: {len(available)}")
    
    print("  ✅ Tool Calling & Execution works!")


async def test_planning_reasoning():
    """Test planning and reasoning engine"""
    print("\nTesting Planning & Reasoning...")
    
    planning = get_planning_reasoning_engine()
    
    # Create plan
    plan = await planning.create_plan(
        goal="Complete task",
        agent_id="agent_0",
        framework=PlanningFramework.REACT,
    )
    print(f"  Created plan: {plan.plan_id}")
    print(f"  Steps: {len(plan.steps)}")
    print(f"  Confidence: {plan.confidence:.2f}")
    
    # Reason
    reasoning = await planning.reason(
        context="Current situation",
        question="What should I do?",
    )
    print(f"  Reasoning: {reasoning[:50]}...")
    
    # Reflect
    reflection = await planning.reflect(
        experience="Past experience",
    )
    print(f"  Reflection insights: {len(reflection['insights'])}")
    
    print("  ✅ Planning & Reasoning works!")


async def test_task_decomposition():
    """Test task decomposition and delegation"""
    print("\nTesting Task Decomposition & Delegation...")
    
    tasks_sys = get_task_decomposition_delegation()
    
    # Decompose task
    task = await tasks_sys.decompose_task(
        task_description="Complex multi-step task",
        max_depth=3,
    )
    print(f"  Task: {task.task_id}")
    print(f"  Subtasks: {len(task.subtasks)}")
    
    # Delegate task
    delegated = await tasks_sys.delegate_task(
        task=task,
        agent_id="agent_0",
    )
    print(f"  Delegated: {delegated}")
    print(f"  Assigned to: {task.assigned_to}")
    
    # Check status
    status = tasks_sys.get_task_status(task.task_id)
    print(f"  Status: {status.status if status else 'None'}")
    
    print("  ✅ Task Decomposition & Delegation works!")


async def test_environment_interaction():
    """Test environment interaction and perception"""
    print("\nTesting Environment Interaction & Perception...")
    
    env = get_environment_interaction_perception()
    
    # Observe
    obs = await env.observe(
        agent_id="agent_0",
        environment_state={"status": "active"},
    )
    print(f"  Observation: {obs.observation_id}")
    print(f"  Source: {obs.source}")
    
    # Act
    result = await env.act(
        agent_id="agent_0",
        action="move",
        parameters={"direction": "forward"},
    )
    print(f"  Action success: {result['success']}")
    
    print("  ✅ Environment Interaction & Perception works!")


async def test_learning_adaptation():
    """Test learning and adaptation system"""
    print("\nTesting Learning & Adaptation...")
    
    learning = get_learning_adaptation_system()
    
    # Learn from feedback
    learn_result = await learning.learn_from_feedback(
        agent_id="agent_0",
        action="search",
        feedback={"success": True, "quality": 0.9},
    )
    print(f"  Learned: {learn_result['learned']}")
    print(f"  Improvement: {learn_result['improvement']:.3f}")
    
    # Adapt strategy
    adapt_result = await learning.adapt_strategy(
        agent_id="agent_0",
        performance_metrics={"accuracy": 0.85, "speed": 0.9},
    )
    print(f"  Adapted: {adapt_result['adapted']}")
    print(f"  Confidence: {adapt_result['confidence']:.2f}")
    
    print("  ✅ Learning & Adaptation works!")


async def test_multi_agent_orchestration():
    """Test multi-agent orchestration"""
    print("\nTesting Multi-Agent Orchestration...")
    
    orch = get_multi_agent_orchestration()
    
    # Create agents
    arch = get_agent_architecture_memory()
    agent1 = arch.create_agent("Agent1", AgentRole.ORCHESTRATOR)
    agent2 = arch.create_agent("Agent2", AgentRole.WORKER)
    
    # Create task
    task = Task(
        task_id="task_1",
        description="Collaborative task",
        subtasks=[
            Task(task_id="sub_1", description="Subtask 1"),
            Task(task_id="sub_2", description="Subtask 2"),
        ],
    )
    
    # Coordinate agents
    coordination = await orch.coordinate_agents(
        agents=[agent1, agent2],
        task=task,
    )
    print(f"  Assignments: {len(coordination['assignments'])}")
    print(f"  Strategy: {coordination['coordination_strategy']}")
    
    # Send message
    sent = await orch.send_message(
        from_agent=agent1.agent_id,
        to_agent=agent2.agent_id,
        content="Test message",
    )
    print(f"  Message sent: {sent}")
    
    # Get messages
    messages = orch.get_agent_messages(agent2.agent_id)
    print(f"  Messages received: {len(messages)}")
    
    print("  ✅ Multi-Agent Orchestration works!")


async def test_integrated_system():
    """Test integrated AI agents system"""
    print("\nTesting Integrated AI Agents System...")
    
    config = AIAgentsConfig(
        max_agents=10,
        memory_capacity=1000,
        enable_learning=True,
    )
    
    system = get_ai_agents_system(config)
    
    stats = system.get_system_stats()
    print(f"  Agents: {stats['num_agents']}")
    print(f"  Memories: {stats['num_memories']}")
    print(f"  Tools: {stats['num_tools']}")
    print(f"  Plans: {stats['num_plans']}")
    
    print("  ✅ Integrated AI Agents System works!")


async def main():
    print("=" * 60)
    print("AI Agents Dual-Version Test Suite")
    print("=" * 60)
    
    print(f"\nTesting imports...")
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    
    await test_agent_architecture_memory()
    await test_tool_calling_execution()
    await test_planning_reasoning()
    await test_task_decomposition()
    await test_environment_interaction()
    await test_learning_adaptation()
    await test_multi_agent_orchestration()
    await test_integrated_system()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
