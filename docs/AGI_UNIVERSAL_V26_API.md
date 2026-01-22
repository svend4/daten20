# AGI Universal Framework v26.0 - API Documentation

## Overview

AGI Universal Framework v26.0 provides advanced reasoning, meta-learning, and universal problem-solving capabilities.

**Version:** 26.0.0 (EXPANDED)
**Status:** Production-ready

---

## Installation

```python
from agi_universal import (
    UniversalProblemSolver,
    MetaLearner,
    ChainOfThoughtReasoner,
    Problem,
    ProblemDomain,
    ReasoningType,
)
```

---

## Core Components

### 1. UniversalProblemSolver

Universal problem solver integrating all AGI capabilities.

#### Initialization

```python
from agi_universal import UniversalProblemSolver

solver = UniversalProblemSolver()
solver.initialize(quick_init=True)
```

#### Methods

##### `initialize(quick_init: bool = True) -> Dict[str, Any]`

Initialize all components (MTL, Meta-learning, Reasoning).

**Parameters:**
- `quick_init` (bool): If True, skip extensive initialization

**Returns:**
- Dictionary with initialization status

**Example:**
```python
init_result = solver.initialize(quick_init=True)
print(f"Status: {init_result['status']}")
print(f"Components: {init_result['components']}")
```

##### `solve(problem: Problem) -> Solution`

Solve a problem using the most appropriate strategy.

**Parameters:**
- `problem` (Problem): Problem to solve

**Returns:**
- Solution object with answer, reasoning trace, and metadata

**Example:**
```python
from agi_universal import Problem, ProblemDomain

problem = Problem(
    description="If A implies B, and B implies C, does A imply C?",
    domain=ProblemDomain.LOGICAL
)

solution = solver.solve(problem)
print(f"Answer: {solution.answer}")
print(f"Confidence: {solution.confidence}")
print(f"Success: {solution.success}")
```

##### `get_performance_statistics() -> Dict[str, Any]`

Get solver performance statistics.

**Returns:**
- Dictionary with performance metrics

---

### 2. MetaLearner

MAML-style meta-learning for few-shot adaptation.

#### Initialization

```python
from agi_universal import MetaLearner, MetaLearningConfig

config = MetaLearningConfig(
    inner_lr=0.01,
    meta_lr=0.001,
    inner_steps=5
)

meta_learner = MetaLearner(
    input_dim=10,
    output_dim=1,
    hidden_dim=32,
    config=config
)
```

#### Methods

##### `adapt_to_task(task_samples: TaskSample, initial_params: Optional[Dict] = None) -> Dict[str, Any]`

Adapt to a new task using few-shot examples.

**Parameters:**
- `task_samples` (TaskSample): Support and query sets
- `initial_params` (Optional[Dict]): Starting parameters

**Returns:**
- Dictionary with adapted parameters and metrics

**Example:**
```python
from agi_universal import TaskSample

# Create task samples
support_set = [
    ([1.0, 2.0], [3.0]),
    ([2.0, 3.0], [5.0]),
    ([3.0, 4.0], [7.0])
]
query_set = [
    ([4.0, 5.0], [9.0]),
    ([5.0, 6.0], [11.0])
]

task = TaskSample(support_set=support_set, query_set=query_set)

result = meta_learner.adapt_to_task(task)
print(f"Query loss: {result['query_loss']}")
print(f"Adaptation steps: {result['adaptation_steps']}")
```

##### `meta_train(tasks: List[TaskSample], num_iterations: int = 100) -> Dict[str, Any]`

Meta-train on multiple tasks to learn good initialization.

**Parameters:**
- `tasks` (List[TaskSample]): List of training tasks
- `num_iterations` (int): Number of meta-training iterations

**Returns:**
- Dictionary with training metrics

---

### 3. ChainOfThoughtReasoner

Step-by-step reasoning with multiple reasoning types.

#### Initialization

```python
from agi_universal import ChainOfThoughtReasoner

reasoner = ChainOfThoughtReasoner(max_steps=10)
```

#### Methods

##### `solve_problem(problem: str, reasoning_type: ReasoningType, context: Optional[Dict] = None) -> ReasoningChain`

Solve problem using chain-of-thought reasoning.

**Parameters:**
- `problem` (str): Problem description
- `reasoning_type` (ReasoningType): Type of reasoning to use
- `context` (Optional[Dict]): Additional context

**Returns:**
- ReasoningChain with steps and explanation

**Example:**
```python
from agi_universal import ReasoningType

# Deductive reasoning
chain = reasoner.solve_problem(
    "All humans are mortal. Socrates is human. Is Socrates mortal?",
    ReasoningType.DEDUCTIVE
)

print(f"Problem: {chain.problem}")
for step in chain.steps:
    print(f"Step {step.step_number}: {step.thought}")
    print(f"  Confidence: {step.confidence}")

# Inductive reasoning
chain = reasoner.solve_problem(
    "The sun rose yesterday, today, and every day before. Will it rise tomorrow?",
    ReasoningType.INDUCTIVE
)
```

##### `explain_reasoning_chain(chain: ReasoningChain) -> str`

Generate human-readable explanation of reasoning chain.

**Parameters:**
- `chain` (ReasoningChain): Reasoning chain to explain

**Returns:**
- String with formatted explanation

---

## Data Classes

### Problem

```python
@dataclass
class Problem:
    description: str
    domain: ProblemDomain
    examples: Optional[List[Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
```

### Solution

```python
@dataclass
class Solution:
    problem: Problem
    strategy_used: SolutionStrategy
    answer: str
    reasoning_trace: List[str]
    confidence: float
    execution_time: float
    success: bool
```

### ReasoningChain

```python
@dataclass
class ReasoningChain:
    problem: str
    steps: List[ReasoningStep]
```

### ReasoningStep

```python
@dataclass
class ReasoningStep:
    step_number: int
    reasoning_type: ReasoningType
    input_state: Dict[str, Any]
    thought: str
    action: str
    output_state: Dict[str, Any]
    confidence: float
```

---

## Enums

### ProblemDomain

```python
class ProblemDomain(Enum):
    LOGICAL = "logical"
    MATHEMATICAL = "mathematical"
    LINGUISTIC = "linguistic"
    CAUSAL = "causal"
    GENERAL = "general"
```

### ReasoningType

```python
class ReasoningType(Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"
```

### SolutionStrategy

```python
class SolutionStrategy(Enum):
    REASONING_CHAIN = "reasoning_chain"
    FEW_SHOT_LEARNING = "few_shot_learning"
    MULTI_TASK_TRANSFER = "multi_task_transfer"
    META_LEARNING = "meta_learning"
    DIRECT_INFERENCE = "direct_inference"
```

---

## Complete Example

```python
from agi_universal import (
    UniversalProblemSolver,
    Problem,
    ProblemDomain,
)

# Initialize solver
solver = UniversalProblemSolver()
solver.initialize(quick_init=True)

# Solve logical problem
logical_problem = Problem(
    description="If all A are B, and all B are C, are all A also C?",
    domain=ProblemDomain.LOGICAL
)

solution = solver.solve(logical_problem)

print(f"Problem: {solution.problem.description}")
print(f"Strategy: {solution.strategy_used.value}")
print(f"Answer: {solution.answer}")
print(f"Confidence: {solution.confidence:.2%}")
print(f"Success: {'✓' if solution.success else '✗'}")

print("\nReasoning trace:")
for i, step in enumerate(solution.reasoning_trace, 1):
    print(f"{i}. {step}")
```

---

## Performance Considerations

### Memory Usage
- MetaLearner: O(hidden_dim × input_dim)
- Reasoner: O(max_steps × state_size)
- Solver: Combines all components

### Execution Time
- Problem solving: 10-100ms (depends on strategy)
- Meta-adaptation: 50-200ms (depends on task complexity)
- Reasoning chains: 5-50ms (depends on max_steps)

### Scalability
- Supports problems of varying complexity
- Efficient caching of intermediate results
- Parallelizable meta-training

---

## Best Practices

### 1. Choose Appropriate Domain
```python
# For logic problems
problem = Problem("...", domain=ProblemDomain.LOGICAL)

# For math problems
problem = Problem("...", domain=ProblemDomain.MATHEMATICAL)
```

### 2. Provide Examples for Complex Problems
```python
problem = Problem(
    description="Complex problem",
    domain=ProblemDomain.GENERAL,
    examples=[
        {"input": "...", "output": "..."},
        {"input": "...", "output": "..."}
    ]
)
```

### 3. Use Quick Init for Production
```python
# Fast initialization
solver.initialize(quick_init=True)

# Full initialization (slower but more thorough)
solver.initialize(quick_init=False)
```

---

## Troubleshooting

### Low Confidence Scores
- Provide more examples in problem description
- Use appropriate domain classification
- Consider providing context

### Slow Performance
- Use quick_init=True
- Reduce max_steps in reasoner
- Simplify problem description

### Unexpected Strategies
- Check problem domain classification
- Verify example format
- Review constraints

---

## References

- **MAML:** Finn et al., "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks" (2017)
- **Chain-of-Thought:** Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022)
- **Multi-Task Learning:** Caruana, "Multitask Learning" (1997)

---

## Version History

- **v26.0** (2026-01): Added meta-learning, reasoning chains, universal solver
- **v25.0** (2025-12): Multi-task learning implementation
- **v24.0** (2025-11): Initial release

---

## Support

For issues, questions, or contributions:
- GitHub Issues: `https://github.com/yourusername/daten20/issues`
- Documentation: `docs/AGI_UNIVERSAL_V26_API.md`
