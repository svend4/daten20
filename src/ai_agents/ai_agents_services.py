"""
AI Agents & Autonomous Tool Use Platform (Pure Python v19.0)

**PURE PYTHON VERSION** - No NumPy required!
- Works everywhere (zero dependencies beyond stdlib)
- 100% API compatible with NumPy version (core features)
- Simplified: Mock embeddings, basic memory retrieval
- ~10-50x slower than NumPy, but highly portable

Version: 19.0.0 (Pure Python)
"""

import asyncio
import hashlib
import json
import math
import random
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# ============================================================================
# Helper Functions (replacing NumPy)
# ============================================================================

def list_mean(values: List[float]) -> float:
    """Mean of list"""
    return sum(values) / len(values) if values else 0.0


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors"""
    if not a or not b or len(a) != len(b):
        return 0.0
    
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot / (norm_a * norm_b)


def mock_embedding(text: str, dim: int = 128) -> List[float]:
    """Generate mock embedding from text"""
    # Use hash for deterministic but varied embeddings
    h = hashlib.md5(text.encode()).hexdigest()
    random.seed(int(h, 16))
    embedding = [random.gauss(0, 1) for _ in range(dim)]
    random.seed()  # Reset seed
    return embedding


# ============================================================================
# Enums and Data Classes
# ============================================================================

class MemoryType(Enum):
    """Types of agent memory"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class PlanningFramework(Enum):
    """Planning and reasoning frameworks"""
    REACT = "react"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REFLEXION = "reflexion"


class AgentRole(Enum):
    """Agent roles in multi-agent systems"""
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    WORKER = "worker"
    REVIEWER = "reviewer"


@dataclass
class Memory:
    """Agent memory entry"""
    memory_id: str
    memory_type: MemoryType
    content: str
    embedding: List[float]
    timestamp: datetime
    importance: float
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """Tool definition"""
    tool_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None
    requires_confirmation: bool = False
    max_execution_time: float = 30.0
    allowed_users: List[str] = field(default_factory=list)


@dataclass
class ToolCall:
    """Tool execution result"""
    call_id: str
    tool_id: str
    arguments: Dict[str, Any]
    result: Any
    success: bool
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class Plan:
    """Agent plan"""
    plan_id: str
    goal: str
    steps: List[str]
    framework: PlanningFramework
    confidence: float
    estimated_cost: float = 0.0


@dataclass
class Task:
    """Task for agent"""
    task_id: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "pending"
    result: Any = None
    subtasks: List['Task'] = field(default_factory=list)


@dataclass
class Agent:
    """AI Agent"""
    agent_id: str
    name: str
    role: AgentRole
    tools: List[Tool] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)


@dataclass
class Observation:
    """Environment observation"""
    observation_id: str
    content: str
    timestamp: datetime
    source: str


@dataclass
class AIAgentsConfig:
    """Configuration for AI agents system"""
    max_agents: int = 10
    memory_capacity: int = 1000
    enable_learning: bool = True


# ============================================================================
# Core Classes (Simplified)
# ============================================================================

class AgentArchitectureMemory:
    """Agent architecture with memory system (Pure Python - Simplified)"""
    
    def __init__(self, memory_capacity: int = 1000):
        self.memory_capacity = memory_capacity
        self.memories: List[Memory] = []
        self.agents: Dict[str, Agent] = {}
        self._lock = threading.Lock()
    
    async def store_memory(
        self,
        agent_id: str,
        memory_type: MemoryType,
        content: str,
        importance: float = 0.5
    ) -> Memory:
        """Store memory (simplified)"""
        await asyncio.sleep(0.01)
        
        embedding = mock_embedding(content)
        
        memory = Memory(
            memory_id=f"mem_{len(self.memories)}",
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            timestamp=datetime.now(),
            importance=importance,
        )
        
        with self._lock:
            self.memories.append(memory)
            if len(self.memories) > self.memory_capacity:
                # Remove least important
                self.memories.sort(key=lambda m: m.importance)
                self.memories.pop(0)
        
        return memory
    
    async def retrieve_memories(
        self,
        agent_id: str,
        query: str,
        k: int = 5
    ) -> List[Memory]:
        """Retrieve relevant memories (simplified)"""
        await asyncio.sleep(0.01)
        
        query_embedding = mock_embedding(query)
        
        with self._lock:
            if not self.memories:
                return []
            
            # Calculate similarities
            scored = []
            for mem in self.memories:
                sim = cosine_similarity(query_embedding, mem.embedding)
                scored.append((sim, mem))
            
            # Sort by similarity and return top k
            scored.sort(key=lambda x: x[0], reverse=True)
            return [mem for _, mem in scored[:k]]
    
    def create_agent(
        self,
        name: str,
        role: AgentRole,
        tools: List[Tool] = None,
        capabilities: List[str] = None
    ) -> Agent:
        """Create new agent"""
        agent = Agent(
            agent_id=f"agent_{len(self.agents)}",
            name=name,
            role=role,
            tools=tools or [],
            capabilities=capabilities or [],
        )
        
        with self._lock:
            self.agents[agent.agent_id] = agent
        
        return agent
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        with self._lock:
            return {
                "num_agents": len(self.agents),
                "num_memories": len(self.memories),
                "memory_capacity": self.memory_capacity,
            }


class ToolCallingExecution:
    """Tool calling and function execution (Pure Python - Simplified)"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.call_history: List[ToolCall] = []
        self._lock = threading.Lock()
    
    def register_tool(self, tool: Tool) -> bool:
        """Register tool"""
        with self._lock:
            self.tools[tool.tool_id] = tool
        return True
    
    async def execute_tool(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        agent_id: str
    ) -> ToolCall:
        """Execute tool (simplified)"""
        start_time = asyncio.get_event_loop().time()
        
        with self._lock:
            tool = self.tools.get(tool_id)
        
        if not tool:
            return ToolCall(
                call_id=f"call_{len(self.call_history)}",
                tool_id=tool_id,
                arguments=arguments,
                result=None,
                success=False,
                execution_time_ms=0.0,
                error_message="Tool not found",
            )
        
        # Mock execution
        await asyncio.sleep(0.1)
        result = {"status": "success", "output": "mock_result"}
        
        exec_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        call = ToolCall(
            call_id=f"call_{len(self.call_history)}",
            tool_id=tool_id,
            arguments=arguments,
            result=result,
            success=True,
            execution_time_ms=exec_time,
        )
        
        with self._lock:
            self.call_history.append(call)
        
        return call
    
    def get_available_tools(self, agent_id: str) -> List[Tool]:
        """Get available tools for agent"""
        with self._lock:
            return list(self.tools.values())


class PlanningReasoningEngine:
    """Planning and reasoning engine (Pure Python - Simplified)"""
    
    def __init__(self, framework: PlanningFramework = PlanningFramework.REACT):
        self.framework = framework
        self.plans: List[Plan] = []
        self._lock = threading.Lock()
    
    async def create_plan(
        self,
        goal: str,
        agent_id: str,
        framework: Optional[PlanningFramework] = None
    ) -> Plan:
        """Create plan (simplified)"""
        await asyncio.sleep(0.01)
        
        framework = framework or self.framework
        
        # Simplified planning
        num_steps = random.randint(3, 7)
        steps = [f"Step {i+1}: Action for {goal}" for i in range(num_steps)]
        
        plan = Plan(
            plan_id=f"plan_{len(self.plans)}",
            goal=goal,
            steps=steps,
            framework=framework,
            confidence=random.uniform(0.6, 0.9),
            estimated_cost=len(steps) * 0.1,
        )
        
        with self._lock:
            self.plans.append(plan)
        
        return plan
    
    async def reason(
        self,
        context: str,
        question: str
    ) -> str:
        """Reasoning (simplified)"""
        await asyncio.sleep(0.01)
        return f"Reasoning: Based on {context}, {question}"
    
    async def reflect(
        self,
        experience: str
    ) -> Dict[str, Any]:
        """Self-reflection (simplified)"""
        await asyncio.sleep(0.01)
        return {
            "insights": ["Insight 1", "Insight 2"],
            "improvements": ["Improvement 1"],
            "confidence": random.uniform(0.5, 0.8),
        }


class TaskDecompositionDelegation:
    """Task decomposition and delegation (Pure Python - Simplified)"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
    
    async def decompose_task(
        self,
        task_description: str,
        max_depth: int = 3
    ) -> Task:
        """Decompose task into subtasks (simplified)"""
        await asyncio.sleep(0.01)
        
        task = Task(
            task_id=f"task_{len(self.tasks)}",
            description=task_description,
            status="decomposed",
        )
        
        # Create subtasks
        num_subtasks = random.randint(2, 4)
        for i in range(num_subtasks):
            subtask = Task(
                task_id=f"{task.task_id}_sub{i}",
                description=f"Subtask {i+1}: {task_description[:30]}",
                status="pending",
            )
            task.subtasks.append(subtask)
        
        with self._lock:
            self.tasks[task.task_id] = task
        
        return task
    
    async def delegate_task(
        self,
        task: Task,
        agent_id: str
    ) -> bool:
        """Delegate task to agent (simplified)"""
        await asyncio.sleep(0.01)
        
        task.assigned_to = agent_id
        task.status = "assigned"
        
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get task status"""
        with self._lock:
            return self.tasks.get(task_id)


class EnvironmentInteractionPerception:
    """Environment interaction and perception (Pure Python - Simplified)"""
    
    def __init__(self):
        self.observations: List[Observation] = []
        self._lock = threading.Lock()
    
    async def observe(
        self,
        agent_id: str,
        environment_state: Dict[str, Any]
    ) -> Observation:
        """Observe environment (simplified)"""
        await asyncio.sleep(0.01)
        
        obs = Observation(
            observation_id=f"obs_{len(self.observations)}",
            content=str(environment_state),
            timestamp=datetime.now(),
            source=agent_id,
        )
        
        with self._lock:
            self.observations.append(obs)
        
        return obs
    
    async def act(
        self,
        agent_id: str,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute action in environment (simplified)"""
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "result": f"Executed {action}",
            "new_state": {"status": "changed"},
        }


class LearningAdaptationSystem:
    """Learning and adaptation system (Pure Python - Simplified)"""
    
    def __init__(self):
        self.experience_buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    async def learn_from_feedback(
        self,
        agent_id: str,
        action: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Learn from feedback (simplified)"""
        await asyncio.sleep(0.01)
        
        experience = {
            "agent_id": agent_id,
            "action": action,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
        }
        
        with self._lock:
            self.experience_buffer.append(experience)
        
        return {
            "learned": True,
            "improvement": random.uniform(0.01, 0.1),
        }
    
    async def adapt_strategy(
        self,
        agent_id: str,
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Adapt strategy based on performance (simplified)"""
        await asyncio.sleep(0.01)
        
        return {
            "adapted": True,
            "new_strategy": "adjusted",
            "confidence": random.uniform(0.6, 0.9),
        }


class MultiAgentOrchestration:
    """Multi-agent orchestration (Pure Python - Simplified)"""
    
    def __init__(self):
        self.active_agents: Dict[str, Agent] = {}
        self.messages: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    async def coordinate_agents(
        self,
        agents: List[Agent],
        task: Task
    ) -> Dict[str, Any]:
        """Coordinate multiple agents (simplified)"""
        await asyncio.sleep(0.01)
        
        # Assign subtasks
        assignments = {}
        for i, agent in enumerate(agents):
            if i < len(task.subtasks):
                assignments[agent.agent_id] = task.subtasks[i].task_id
        
        return {
            "assignments": assignments,
            "coordination_strategy": "round_robin",
        }
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str
    ) -> bool:
        """Send message between agents (simplified)"""
        await asyncio.sleep(0.01)
        
        message = {
            "from": from_agent,
            "to": to_agent,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        
        with self._lock:
            self.messages.append(message)
        
        return True
    
    def get_agent_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get messages for agent"""
        with self._lock:
            return [m for m in self.messages if m["to"] == agent_id]


class IntegratedAIAgentsSystem:
    """Integrated AI agents system (Pure Python - Simplified)"""
    
    def __init__(self, config: Optional[AIAgentsConfig] = None):
        self.config = config or AIAgentsConfig()
        self.architecture = AgentArchitectureMemory(self.config.memory_capacity)
        self.tools = ToolCallingExecution()
        self.planning = PlanningReasoningEngine()
        self.tasks = TaskDecompositionDelegation()
        self.environment = EnvironmentInteractionPerception()
        self.learning = LearningAdaptationSystem()
        self.orchestration = MultiAgentOrchestration()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "num_agents": len(self.architecture.agents),
            "num_memories": len(self.architecture.memories),
            "num_tools": len(self.tools.tools),
            "num_plans": len(self.planning.plans),
            "num_tasks": len(self.tasks.tasks),
        }


# ============================================================================
# Singleton Getters
# ============================================================================

_architecture_instance = None
_architecture_lock = threading.Lock()

def get_agent_architecture_memory() -> AgentArchitectureMemory:
    """Get agent architecture singleton"""
    global _architecture_instance
    with _architecture_lock:
        if _architecture_instance is None:
            _architecture_instance = AgentArchitectureMemory()
    return _architecture_instance


_tools_instance = None
_tools_lock = threading.Lock()

def get_tool_calling_execution() -> ToolCallingExecution:
    """Get tool calling singleton"""
    global _tools_instance
    with _tools_lock:
        if _tools_instance is None:
            _tools_instance = ToolCallingExecution()
    return _tools_instance


_planning_instance = None
_planning_lock = threading.Lock()

def get_planning_reasoning_engine() -> PlanningReasoningEngine:
    """Get planning engine singleton"""
    global _planning_instance
    with _planning_lock:
        if _planning_instance is None:
            _planning_instance = PlanningReasoningEngine()
    return _planning_instance


_tasks_instance = None
_tasks_lock = threading.Lock()

def get_task_decomposition_delegation() -> TaskDecompositionDelegation:
    """Get task decomposition singleton"""
    global _tasks_instance
    with _tasks_lock:
        if _tasks_instance is None:
            _tasks_instance = TaskDecompositionDelegation()
    return _tasks_instance


_environment_instance = None
_environment_lock = threading.Lock()

def get_environment_interaction_perception() -> EnvironmentInteractionPerception:
    """Get environment interaction singleton"""
    global _environment_instance
    with _environment_lock:
        if _environment_instance is None:
            _environment_instance = EnvironmentInteractionPerception()
    return _environment_instance


_learning_instance = None
_learning_lock = threading.Lock()

def get_learning_adaptation_system() -> LearningAdaptationSystem:
    """Get learning system singleton"""
    global _learning_instance
    with _learning_lock:
        if _learning_instance is None:
            _learning_instance = LearningAdaptationSystem()
    return _learning_instance


_orchestration_instance = None
_orchestration_lock = threading.Lock()

def get_multi_agent_orchestration() -> MultiAgentOrchestration:
    """Get orchestration singleton"""
    global _orchestration_instance
    with _orchestration_lock:
        if _orchestration_instance is None:
            _orchestration_instance = MultiAgentOrchestration()
    return _orchestration_instance


_ai_agents_system_instance = None
_ai_agents_system_lock = threading.Lock()

def get_ai_agents_system(config: Optional[AIAgentsConfig] = None) -> IntegratedAIAgentsSystem:
    """Get AI agents system singleton"""
    global _ai_agents_system_instance
    with _ai_agents_system_lock:
        if _ai_agents_system_instance is None:
            _ai_agents_system_instance = IntegratedAIAgentsSystem(config)
    return _ai_agents_system_instance
