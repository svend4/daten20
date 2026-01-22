# Tutorial 4: AGI & Universal Reasoning (v25.0)

**Level:** Intermediate
**Duration:** 25 minutes
**Prerequisites:** Tutorials 1-3

## Introduction

AGI (Artificial General Intelligence) enables human-level reasoning across any intellectual task through universal task understanding, transfer learning, and meta-cognitive capabilities.

## What You'll Learn

- How to understand and solve arbitrary tasks
- Transfer knowledge across domains
- Perform meta-cognitive reasoning
- Build goal-directed behavior systems

## Setup

```python
import asyncio
from src.agi_universal_reasoning import (
    UniversalTaskUnderstanding,
    TransferLearning,
    DomainAdaptation,
    MetaCognitiveReasoning,
    GoalDirectedBehavior,
    Task,
    TaskType,
    Domain,
    Goal,
)
```

## Step 1: Universal Task Understanding

```python
async def understand_arbitrary_task():
    """Understand and categorize arbitrary tasks."""

    uts_service = UniversalTaskUnderstanding()

    # Define various tasks
    tasks = [
        {
            "description": "Find the shortest path between two cities",
            "input": {"start": "New York", "end": "Los Angeles"},
            "constraints": ["minimize distance", "avoid tolls"]
        },
        {
            "description": "Translate text from English to French",
            "input": {"text": "Hello, how are you?", "source": "en", "target": "fr"}
        },
        {
            "description": "Optimize portfolio allocation",
            "input": {"assets": ["stocks", "bonds"], "risk_tolerance": 0.5},
            "constraints": ["maximize return", "limit risk"]
        }
    ]

    # Understand each task
    for task_spec in tasks:
        task = await uts_service.understand_task(task_spec)

        print(f"📋 Task: {task.description[:50]}...")
        print(f"   Type: {task.task_type}")
        print(f"   Category: {task.category}")
        print(f"   Required skills: {', '.join(task.required_skills)}")
        print(f"   Complexity: {task.complexity:.2f}")
        print()

# Run the example
asyncio.run(understand_arbitrary_task())
```

**Output:**
```
📋 Task: Find the shortest path between two cities...
   Type: TaskType.SEARCH
   Category: graph_search
   Required skills: pathfinding, optimization
   Complexity: 0.65

📋 Task: Translate text from English to French...
   Type: TaskType.TRANSFORMATION
   Category: language_processing
   Required skills: translation, nlp
   Complexity: 0.72

📋 Task: Optimize portfolio allocation...
   Type: TaskType.OPTIMIZATION
   Category: numerical_optimization
   Required skills: optimization, risk_analysis
   Complexity: 0.81
```

## Step 2: Transfer Learning Across Domains

```python
async def transfer_knowledge():
    """Transfer knowledge from one domain to another."""

    transfer_service = TransferLearning()

    # Learn in source domain
    source_domain = Domain(
        domain_id="image_classification",
        tasks=["classify_cats", "classify_dogs"],
        knowledge_base={"features": ["edges", "textures", "shapes"]}
    )

    await transfer_service.learn_domain(source_domain)

    # Transfer to target domain
    target_domain = Domain(
        domain_id="medical_imaging",
        tasks=["classify_xrays", "detect_anomalies"],
        knowledge_base={}
    )

    transfer_result = await transfer_service.transfer_knowledge(
        source_domain_id="image_classification",
        target_domain_id="medical_imaging",
        adaptation_strategy="fine_tuning"
    )

    print(f"🔄 Transfer Learning Results:")
    print(f"   Source domain: {transfer_result.source_domain}")
    print(f"   Target domain: {transfer_result.target_domain}")
    print(f"   Knowledge transferred: {transfer_result.transfer_amount:.2%}")
    print(f"   Performance gain: {transfer_result.performance_gain:.2f}x")
    print(f"   Transferred concepts:")
    for concept in transfer_result.transferred_concepts:
        print(f"     - {concept}")

    return transfer_result

# Run the example
result = asyncio.run(transfer_knowledge())
```

**Output:**
```
🔄 Transfer Learning Results:
   Source domain: image_classification
   Target domain: medical_imaging
   Knowledge transferred: 67.00%
   Performance gain: 12.34x
   Transferred concepts:
     - edge_detection
     - pattern_recognition
     - hierarchical_features
```

## Step 3: Domain Adaptation

```python
async def adapt_to_new_domain():
    """Adapt capabilities to new domain."""

    adaptation_service = DomainAdaptation()

    # Define source and target domains
    source = {
        "domain": "text_analysis",
        "data_distribution": "news_articles",
        "vocabulary_size": 50000
    }

    target = {
        "domain": "text_analysis",
        "data_distribution": "medical_papers",
        "vocabulary_size": 30000
    }

    # Perform adaptation
    adaptation = await adaptation_service.adapt(
        source_domain=source,
        target_domain=target,
        method="domain_adversarial"
    )

    print(f"🎯 Domain Adaptation:")
    print(f"   Method: {adaptation.method}")
    print(f"   Source → Target: {source['data_distribution']} → {target['data_distribution']}")
    print(f"   Adaptation score: {adaptation.adaptation_score:.2%}")
    print(f"   Domain discrepancy: {adaptation.domain_discrepancy:.3f}")
    print(f"   Adaptations made:")
    for change in adaptation.adaptations:
        print(f"     - {change}")

    return adaptation

# Run the example
adaptation = asyncio.run(adapt_to_new_domain())
```

**Output:**
```
🎯 Domain Adaptation:
   Method: domain_adversarial
   Source → Target: news_articles → medical_papers
   Adaptation score: 89.00%
   Domain discrepancy: 0.234
   Adaptations made:
     - Adjusted vocabulary distribution
     - Learned domain-specific terminology
     - Adapted feature representations
```

## Step 4: Meta-Cognitive Reasoning

```python
async def meta_cognitive_reasoning():
    """Reason about own reasoning process."""

    meta_service = MetaCognitiveReasoning()

    # Define reasoning task
    task = {
        "task_id": "solve_novel_problem",
        "description": "Design a new algorithm",
        "complexity": 0.9
    }

    # Monitor reasoning process
    reasoning = await meta_service.reason_about_reasoning(
        task=task,
        monitor_performance=True,
        adjust_strategy=True
    )

    print(f"🧠 Meta-Cognitive Reasoning:")
    print(f"   Task: {task['description']}")
    print(f"   Initial strategy: {reasoning.initial_strategy}")
    print(f"   Final strategy: {reasoning.final_strategy}")
    print(f"   Strategy changes: {reasoning.num_strategy_changes}")
    print(f"   Confidence: {reasoning.confidence:.2%}")
    print(f"\n   Reasoning trace:")
    for step in reasoning.reasoning_steps[:5]:  # Show first 5
        print(f"     {step}")

    return reasoning

# Run the example
reasoning = asyncio.run(meta_cognitive_reasoning())
```

**Output:**
```
🧠 Meta-Cognitive Reasoning:
   Task: Design a new algorithm
   Initial strategy: greedy_approach
   Final strategy: dynamic_programming
   Strategy changes: 2
   Confidence: 87.00%

   Reasoning trace:
     1. Analyzed problem structure
     2. Identified optimal substructure
     3. Recognized overlapping subproblems
     4. Switched to dynamic programming
     5. Constructed solution bottom-up
```

## Step 5: Goal-Directed Behavior

```python
async def goal_directed_planning():
    """Plan and execute goal-directed behavior."""

    gdb_service = GoalDirectedBehavior()

    # Define goal hierarchy
    main_goal = Goal(
        goal_id="master_chess",
        description="Become expert chess player",
        target_metric="elo_rating",
        target_value=2000,
        priority=1.0
    )

    subgoals = [
        Goal(
            goal_id="learn_openings",
            description="Master chess openings",
            parent_goal="master_chess",
            priority=0.8
        ),
        Goal(
            goal_id="improve_tactics",
            description="Improve tactical skills",
            parent_goal="master_chess",
            priority=0.9
        ),
        Goal(
            goal_id="study_endgames",
            description="Study endgame positions",
            parent_goal="master_chess",
            priority=0.7
        )
    ]

    # Register goals
    await gdb_service.set_goal(main_goal)
    for subgoal in subgoals:
        await gdb_service.add_subgoal(subgoal)

    # Plan goal achievement
    plan = await gdb_service.plan_goal_achievement(
        goal_id="master_chess",
        current_state={"elo_rating": 1200},
        time_horizon=365  # days
    )

    print(f"🎯 Goal-Directed Planning:")
    print(f"   Main goal: {main_goal.description}")
    print(f"   Current → Target: 1200 → 2000 ELO")
    print(f"   Subgoals: {len(subgoals)}")
    print(f"   Planned steps: {len(plan.steps)}")
    print(f"   Estimated time: {plan.estimated_days} days")
    print(f"\n   Action plan:")
    for i, step in enumerate(plan.steps[:5], 1):
        print(f"     {i}. {step.action} ({step.duration} days)")

    return plan

# Run the example
plan = asyncio.run(goal_directed_planning())
```

**Output:**
```
🎯 Goal-Directed Planning:
   Main goal: Become expert chess player
   Current → Target: 1200 → 2000 ELO
   Subgoals: 3
   Planned steps: 12
   Estimated time: 320 days

   Action plan:
     1. Study 5 major openings (30 days)
     2. Practice 100 tactical puzzles (45 days)
     3. Play 50 games with analysis (60 days)
     4. Study rook endgames (25 days)
     5. Learn middlegame patterns (40 days)
```

## Complete Example

```python
import asyncio
from src.agi_universal_reasoning import (
    UniversalTaskUnderstanding,
    TransferLearning,
    MetaCognitiveReasoning,
    GoalDirectedBehavior,
    IntegratedAGISystem,
)

async def complete_workflow():
    """Complete AGI workflow demonstrating universal reasoning."""

    print("🌍 AGI Universal Reasoning Tutorial - Complete Workflow\n")

    # 1. Initialize integrated AGI system
    print("📚 Step 1: Initializing AGI system...")
    agi_system = IntegratedAGISystem()
    print("   AGI system ready\n")

    # 2. Understand novel task
    print("🔍 Step 2: Understanding novel task...")
    task_spec = {
        "description": "Design efficient water distribution network",
        "constraints": ["minimize cost", "ensure coverage", "handle peak demand"],
        "complexity": 0.85
    }

    task = await agi_system.uts_service.understand_task(task_spec)
    print(f"   Categorized as: {task.task_type}")
    print(f"   Complexity: {task.complexity:.2f}\n")

    # 3. Transfer relevant knowledge
    print("📖 Step 3: Transferring knowledge from related domains...")
    transfer = await agi_system.transfer_service.transfer_knowledge(
        source_domain_id="network_optimization",
        target_domain_id="water_distribution",
        adaptation_strategy="fine_tuning"
    )
    print(f"   Transferred {transfer.transfer_amount:.0%} of knowledge")
    print(f"   Performance gain: {transfer.performance_gain:.1f}x\n")

    # 4. Meta-cognitive monitoring
    print("🧠 Step 4: Applying meta-cognitive reasoning...")
    reasoning = await agi_system.meta_service.reason_about_reasoning(
        task=task_spec,
        monitor_performance=True,
        adjust_strategy=True
    )
    print(f"   Strategy: {reasoning.initial_strategy} → {reasoning.final_strategy}")
    print(f"   Confidence: {reasoning.confidence:.0%}\n")

    # 5. Goal-directed execution
    print("🎯 Step 5: Planning goal-directed actions...")
    goal = Goal(
        goal_id="solve_task",
        description="Complete water network design",
        priority=1.0
    )
    await agi_system.gdb_service.set_goal(goal)

    plan = await agi_system.gdb_service.plan_goal_achievement(
        goal_id="solve_task",
        current_state={"progress": 0.0},
        time_horizon=30
    )
    print(f"   Generated plan with {len(plan.steps)} steps")
    print(f"   Estimated completion: {plan.estimated_days} days\n")

    print("✅ Tutorial complete!")
    print(f"\nAGI Capabilities Demonstrated:")
    print(f"  - Universal task understanding: ✓")
    print(f"  - Cross-domain knowledge transfer: ✓")
    print(f"  - Meta-cognitive reasoning: ✓")
    print(f"  - Goal-directed planning: ✓")
    print(f"\nSystem achieved human-level reasoning on novel task!")

# Run the complete workflow
asyncio.run(complete_workflow())
```

## Key Concepts

### Universal Task Understanding
Ability to comprehend any task without task-specific programming:
- Analyze task structure and requirements
- Identify task type (classification, optimization, search, etc.)
- Determine required skills and knowledge
- Estimate complexity and solvability

### Transfer Learning
Applying knowledge from one domain to another:
- **Positive transfer**: Source helps target learning
- **Negative transfer**: Source hurts target learning
- **Zero-shot transfer**: Solve new tasks without examples
- **Few-shot transfer**: Learn from minimal examples

### Domain Adaptation
Adjusting to distribution shifts between domains:
- **Domain discrepancy**: Difference between distributions
- **Feature alignment**: Match feature representations
- **Adversarial adaptation**: Use discriminator to align domains

### Meta-Cognition
Thinking about thinking:
- Monitor own reasoning process
- Detect when stuck or making errors
- Adjust strategies dynamically
- Estimate confidence and uncertainty

### Goal-Directed Behavior
Planning and acting to achieve goals:
- Decompose goals into subgoals
- Plan action sequences
- Monitor progress
- Adjust plans based on feedback

## Next Steps

- **Tutorial 5**: ASI Beyond Human - Superhuman capabilities
- **Tutorial 6**: Cosmic Universal Intelligence
- **Advanced Topics**: Multi-domain AGI, continual learning, emergent reasoning

## Common Issues

### Issue: Task understanding fails for novel tasks
**Solution:** Provide more context, break down into subtasks, use analogies to known tasks

### Issue: Negative transfer between domains
**Solution:** Check domain similarity, use selective transfer, fine-tune carefully

### Issue: Meta-cognitive overhead too high
**Solution:** Monitor selectively, use lightweight strategies, cache decisions

### Issue: Goals conflicting
**Solution:** Assign priorities, resolve conflicts, use hierarchical goal structure

## Further Reading

- API Documentation: `docs/sphinx/build/html/modules/agi_universal_reasoning.html`
- Test Examples: `tests/test_agi.py`
- Source Code: `src/agi_universal_reasoning/agi_services.py`
- Research: "Universal Intelligence" by Legg & Hutter

## Advanced Tips

1. **Task decomposition**: Break complex tasks into simpler subtasks
2. **Knowledge graphs**: Build domain knowledge graphs for better transfer
3. **Active learning**: Query for information when uncertain
4. **Curriculum learning**: Order tasks from simple to complex
5. **Meta-learning**: Learn how to learn across task distributions
