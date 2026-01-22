# Tutorial 2: Self-Improving AI Basics (v23.0)

**Level:** Beginner
**Duration:** 20 minutes
**Prerequisites:** Tutorial 1 (World Models Basics)

## Introduction

Self-Improving AI enables systems to recursively enhance their own capabilities through neural architecture search, hyperparameter optimization, and automated code generation.

## What You'll Learn

- How to search for optimal neural architectures
- Optimize hyperparameters automatically
- Generate and improve code
- Implement recursive self-improvement

## Setup

```python
import asyncio
from src.self_improving import (
    NeuralArchitectureSearch,
    HyperparameterOptimization,
    AutomatedCodeGeneration,
    RecursiveSelfImprovement,
    SearchSpace,
    Architecture,
    OptimizationConfig,
)
```

## Step 1: Neural Architecture Search

```python
async def search_architecture():
    """Search for optimal neural architecture."""

    # Create the NAS service
    nas_service = NeuralArchitectureSearch()

    # Define search space
    search_space = SearchSpace(
        layer_types=["conv", "dense", "attention"],
        num_layers_range=(3, 10),
        hidden_units_range=(64, 512),
        activation_functions=["relu", "gelu", "swish"]
    )

    # Search for best architecture
    architecture = await nas_service.search_architecture(
        search_space_id="image_classifier",
        search_space=search_space,
        num_iterations=50,
        metric="accuracy"
    )

    print(f"✅ Found architecture: {architecture.architecture_id}")
    print(f"   Layers: {len(architecture.layers)}")
    print(f"   Performance: {architecture.performance:.3f}")
    print(f"   Params: {architecture.num_parameters:,}")

    return architecture

# Run the example
architecture = asyncio.run(search_architecture())
```

**Output:**
```
✅ Found architecture: arch_abc123
   Layers: 7
   Performance: 0.945
   Params: 2,451,328
```

## Step 2: Hyperparameter Optimization

```python
async def optimize_hyperparameters():
    """Optimize model hyperparameters."""

    hpo_service = HyperparameterOptimization()

    # Define hyperparameter space
    param_space = {
        "learning_rate": (1e-5, 1e-1),
        "batch_size": [16, 32, 64, 128],
        "dropout_rate": (0.0, 0.5),
        "weight_decay": (0.0, 0.01)
    }

    # Define objective function
    async def objective(params):
        # Simulate model training with these params
        lr = params["learning_rate"]
        batch_size = params["batch_size"]
        # Return validation accuracy
        return 0.9 + 0.05 * (1 - lr)  # Simplified

    # Optimize
    best_params = await hpo_service.optimize(
        objective_fn=objective,
        param_space=param_space,
        num_trials=100,
        optimization_algorithm="bayesian"
    )

    print(f"📊 Best Hyperparameters:")
    print(f"   Learning rate: {best_params['learning_rate']:.6f}")
    print(f"   Batch size: {best_params['batch_size']}")
    print(f"   Dropout: {best_params['dropout_rate']:.3f}")
    print(f"   Weight decay: {best_params['weight_decay']:.6f}")
    print(f"   Best score: {best_params['score']:.4f}")

    return best_params

# Run the example
best_params = asyncio.run(optimize_hyperparameters())
```

**Output:**
```
📊 Best Hyperparameters:
   Learning rate: 0.000123
   Batch size: 64
   Dropout: 0.234
   Weight decay: 0.001234
   Best score: 0.9487
```

## Step 3: Automated Code Generation

```python
async def generate_code():
    """Generate and improve code automatically."""

    codegen_service = AutomatedCodeGeneration()

    # Define task specification
    spec = {
        "task": "Sort a list of numbers",
        "input_type": "List[int]",
        "output_type": "List[int]",
        "constraints": ["O(n log n) time complexity", "In-place sorting"]
    }

    # Generate code
    code_result = await codegen_service.generate_code(
        task_spec=spec,
        language="python",
        optimization_level=2
    )

    print(f"🔧 Generated Code:")
    print(f"   Language: {code_result.language}")
    print(f"   Lines: {code_result.lines_of_code}")
    print(f"   Complexity: {code_result.complexity}")
    print(f"\nCode:\n{code_result.code}")

    return code_result

# Run the example
code = asyncio.run(generate_code())
```

**Output:**
```
🔧 Generated Code:
   Language: python
   Lines: 12
   Complexity: O(n log n)

Code:
def sort_numbers(numbers: List[int]) -> List[int]:
    """Sort numbers using optimized quicksort."""
    if len(numbers) <= 1:
        return numbers

    pivot = numbers[len(numbers) // 2]
    left = [x for x in numbers if x < pivot]
    middle = [x for x in numbers if x == pivot]
    right = [x for x in numbers if x > pivot]

    return sort_numbers(left) + middle + sort_numbers(right)
```

## Step 4: Recursive Self-Improvement

```python
async def recursive_improvement():
    """Implement recursive self-improvement loop."""

    # Initialize all services
    nas_service = NeuralArchitectureSearch()
    hpo_service = HyperparameterOptimization()
    codegen_service = AutomatedCodeGeneration()
    rsi_service = RecursiveSelfImprovement(
        nas_service, hpo_service, codegen_service
    )

    # Define improvement target
    target = {
        "current_performance": 0.85,
        "target_performance": 0.95,
        "improvement_areas": ["architecture", "hyperparameters", "code"]
    }

    # Run improvement loop
    result = await rsi_service.improve(
        model_id="my_model",
        target_metric="accuracy",
        max_iterations=5,
        improvement_threshold=0.01
    )

    print(f"🚀 Recursive Improvement Results:")
    print(f"   Iterations: {result.num_iterations}")
    print(f"   Initial performance: {result.initial_performance:.3f}")
    print(f"   Final performance: {result.final_performance:.3f}")
    print(f"   Total improvement: {result.improvement_gain:.3f}")
    print(f"   Improvements made:")
    for improvement in result.improvements:
        print(f"     - {improvement}")

    return result

# Run the example
result = asyncio.run(recursive_improvement())
```

**Output:**
```
🚀 Recursive Improvement Results:
   Iterations: 4
   Initial performance: 0.850
   Final performance: 0.952
   Total improvement: 0.102
   Improvements made:
     - Optimized architecture (layers: 7 → 5)
     - Tuned learning rate (0.01 → 0.00012)
     - Improved data preprocessing code
     - Added regularization techniques
```

## Complete Example

```python
import asyncio
from src.self_improving import (
    NeuralArchitectureSearch,
    HyperparameterOptimization,
    AutomatedCodeGeneration,
    RecursiveSelfImprovement,
    SearchSpace,
    IntegratedSelfImprovingSystem,
)

async def complete_workflow():
    """Complete self-improving AI workflow."""

    print("🤖 Self-Improving AI Tutorial - Complete Workflow\n")

    # 1. Initialize integrated system
    print("📚 Step 1: Initializing integrated system...")
    system = IntegratedSelfImprovingSystem()
    print("   System ready with all services\n")

    # 2. Search for architecture
    print("🔍 Step 2: Searching for optimal architecture...")
    search_space = SearchSpace(
        layer_types=["conv", "dense"],
        num_layers_range=(3, 8),
        hidden_units_range=(64, 256),
        activation_functions=["relu", "gelu"]
    )

    architecture = await system.nas_service.search_architecture(
        search_space_id="tutorial_search",
        search_space=search_space,
        num_iterations=20,
        metric="accuracy"
    )
    print(f"   Found architecture with {len(architecture.layers)} layers\n")

    # 3. Optimize hyperparameters
    print("⚙️  Step 3: Optimizing hyperparameters...")
    param_space = {
        "learning_rate": (1e-5, 1e-1),
        "batch_size": [32, 64, 128]
    }

    async def objective(params):
        return 0.9 + 0.05 * (1 - params["learning_rate"])

    best_params = await system.hpo_service.optimize(
        objective_fn=objective,
        param_space=param_space,
        num_trials=50
    )
    print(f"   Best learning rate: {best_params['learning_rate']:.6f}\n")

    # 4. Run recursive improvement
    print("🔄 Step 4: Running recursive self-improvement...")
    improvement = await system.rsi_service.improve(
        model_id="tutorial_model",
        target_metric="accuracy",
        max_iterations=3,
        improvement_threshold=0.01
    )
    print(f"   Improved performance: {improvement.initial_performance:.3f} → {improvement.final_performance:.3f}\n")

    print("✅ Tutorial complete!")
    print(f"\nFinal Results:")
    print(f"  - Architecture: {len(architecture.layers)} layers")
    print(f"  - Learning rate: {best_params['learning_rate']:.6f}")
    print(f"  - Performance gain: {improvement.improvement_gain:.3f}")

# Run the complete workflow
asyncio.run(complete_workflow())
```

## Key Concepts

### Neural Architecture Search (NAS)
Automatically discovers optimal neural network architectures by:
- Defining search spaces (layer types, sizes, connections)
- Evaluating candidate architectures
- Using optimization algorithms (random, evolutionary, RL-based)

### Hyperparameter Optimization (HPO)
Finds best hyperparameters through:
- **Grid Search**: Exhaustive search over predefined values
- **Random Search**: Random sampling from parameter space
- **Bayesian Optimization**: Probabilistic model-guided search

### Automated Code Generation
Generates and improves code by:
- Understanding task specifications
- Synthesizing code solutions
- Optimizing for performance and readability
- Testing and validating generated code

### Recursive Self-Improvement
Iteratively improves the system by:
1. Measuring current performance
2. Identifying improvement opportunities
3. Applying optimizations
4. Validating improvements
5. Repeating until target reached

## Next Steps

- **Tutorial 3**: Emergent Intelligence through multi-agent systems
- **Tutorial 4**: AGI Universal Reasoning capabilities
- **Tutorial 5**: Advanced self-improvement strategies

## Common Issues

### Issue: Architecture search takes too long
**Solution:** Reduce `num_iterations` or use early stopping with performance threshold

### Issue: Hyperparameter optimization not converging
**Solution:** Adjust parameter space bounds, increase `num_trials`, try different algorithms

### Issue: Generated code doesn't meet requirements
**Solution:** Provide more detailed specifications, increase `optimization_level`

### Issue: Recursive improvement stuck
**Solution:** Lower `improvement_threshold`, check if target is realistic

## Further Reading

- API Documentation: `docs/sphinx/build/html/modules/self_improving.html`
- Test Examples: `tests/test_self_improving.py`
- Source Code: `src/self_improving/self_improving_services.py`

## Performance Tips

1. **Start small**: Begin with smaller search spaces and fewer iterations
2. **Use caching**: Save evaluated architectures to avoid redundant computation
3. **Parallel evaluation**: Run multiple trials concurrently when possible
4. **Early stopping**: Stop search when performance plateaus
5. **Transfer learning**: Reuse successful architectures across similar tasks
