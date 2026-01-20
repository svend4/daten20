# Tutorial 1: World Models Basics (v22.0)

**Level:** Beginner
**Duration:** 15 minutes
**Prerequisites:** Basic Python knowledge

## Introduction

World Models enable AI systems to learn predictive models of their environment, plan actions using imagination, and reason about cause-and-effect relationships.

## What You'll Learn

- How to create and learn a world model
- Make predictions about future states
- Use models for planning

## Setup

```python
import asyncio
from src.world_models import (
    WorldModelLearning,
    PredictiveLearning,
    ModelBasedPlanning,
    ModelType,
    Transition,
)
```

## Step 1: Learning a Simple World Model

```python
async def learn_simple_model():
    """Learn a deterministic world model from experiences."""

    # Create the learning service
    wm_service = WorldModelLearning()

    # Create some example experiences
    # Each transition represents: state -> action -> next_state
    experiences = [
        Transition(
            state=[1.0, 2.0, 3.0],  # Current state
            action="move_forward",   # Action taken
            next_state=[2.0, 3.0, 4.0],  # Resulting state
            reward=1.0,              # Reward received
            done=False               # Episode not finished
        ),
        Transition(
            state=[2.0, 3.0, 4.0],
            action="move_forward",
            next_state=[3.0, 4.0, 5.0],
            reward=1.0,
            done=False
        ),
    ]

    # Learn the model
    model = await wm_service.learn_world_model(
        model_id="simple_model",
        experiences=experiences,
        model_type=ModelType.DETERMINISTIC
    )

    print(f"✅ Learned model: {model.model_id}")
    print(f"   Model type: {model.model_type}")
    print(f"   Accuracy: {model.accuracy:.2f}")

    return model

# Run the example
model = asyncio.run(learn_simple_model())
```

**Output:**
```
✅ Learned model: simple_model
   Model type: ModelType.DETERMINISTIC
   Accuracy: 0.95
```

## Step 2: Making Predictions

```python
async def make_predictions():
    """Use the learned model to predict future states."""

    wm_service = WorldModelLearning()
    pred_service = PredictiveLearning(wm_service)

    # Predict what happens after taking actions
    current_state = [1.0, 2.0, 3.0]
    actions = ["move_forward", "turn_right", "move_forward"]

    prediction = await pred_service.predict_trajectory(
        initial_state=current_state,
        action_sequence=actions,
        horizon=len(actions),
        model_id="simple_model"
    )

    print(f"📊 Prediction Results:")
    print(f"   Predicted {len(prediction.predicted_states)} states")
    print(f"   Confidence: {prediction.confidence:.2f}")

    for i, state in enumerate(prediction.predicted_states):
        print(f"   Step {i+1}: {state}")

    return prediction

# Run the example
prediction = asyncio.run(make_predictions())
```

**Output:**
```
📊 Prediction Results:
   Predicted 3 states
   Confidence: 0.92
   Step 1: [2.0, 3.0, 4.0]
   Step 2: [2.5, 2.5, 4.0]
   Step 3: [3.5, 2.5, 5.0]
```

## Step 3: Planning with the Model

```python
async def plan_actions():
    """Use the model to plan optimal actions."""

    wm_service = WorldModelLearning()
    pred_service = PredictiveLearning(wm_service)
    planning = ModelBasedPlanning(wm_service, pred_service)

    # Define current and goal states
    current_state = {"position": [0.0, 0.0, 0.0]}
    goal_state = {"position": [10.0, 10.0, 0.0]}

    # Find a plan to reach the goal
    plan = await planning.plan(
        model_id="simple_model",
        current_state=current_state,
        goal_state=goal_state,
        horizon=10,
        num_simulations=100
    )

    print(f"🎯 Generated Plan:")
    print(f"   Plan ID: {plan.plan_id}")
    print(f"   Actions: {plan.actions}")
    print(f"   Expected return: {plan.expected_return:.2f}")
    print(f"   Success probability: {plan.success_probability:.2%}")

    return plan

# Run the example
plan = asyncio.run(plan_actions())
```

**Output:**
```
🎯 Generated Plan:
   Plan ID: plan_1234
   Actions: ['move_forward', 'move_forward', 'turn_right', ...]
   Expected return: 8.50
   Success probability: 87.00%
```

## Complete Example

```python
import asyncio
from src.world_models import (
    WorldModelLearning,
    PredictiveLearning,
    ModelBasedPlanning,
    ModelType,
    Transition,
    PlanningAlgorithm,
)

async def complete_workflow():
    """Complete world models workflow."""

    print("🌍 World Models Tutorial - Complete Workflow\n")

    # 1. Initialize services
    wm_service = WorldModelLearning()
    pred_service = PredictiveLearning(wm_service)
    planning = ModelBasedPlanning(wm_service, pred_service)

    # 2. Collect experiences
    print("📚 Step 1: Collecting experiences...")
    experiences = [
        Transition(
            state=[i, i+1, i+2],
            action=f"action_{i}",
            next_state=[i+1, i+2, i+3],
            reward=1.0,
            done=False
        )
        for i in range(10)
    ]
    print(f"   Collected {len(experiences)} experiences\n")

    # 3. Learn model
    print("🧠 Step 2: Learning world model...")
    model = await wm_service.learn_world_model(
        model_id="tutorial_model",
        experiences=experiences,
        model_type=ModelType.DETERMINISTIC
    )
    print(f"   Model accuracy: {model.accuracy:.2%}\n")

    # 4. Make predictions
    print("🔮 Step 3: Making predictions...")
    prediction = await pred_service.predict_trajectory(
        initial_state=[0, 1, 2],
        action_sequence=None,  # Let the model decide
        horizon=5,
        model_id="tutorial_model"
    )
    print(f"   Predicted {len(prediction.predicted_states)} future states\n")

    # 5. Plan actions
    print("🎯 Step 4: Planning optimal actions...")
    plan = await planning.plan(
        model_id="tutorial_model",
        current_state={"state": [0, 1, 2]},
        goal_state={"state": [10, 11, 12]},
        horizon=10,
        algorithm=PlanningAlgorithm.RANDOM_SHOOTING,
        num_simulations=50
    )
    print(f"   Generated plan with {len(plan.actions)} actions")
    print(f"   Expected success: {plan.success_probability:.2%}\n")

    print("✅ Tutorial complete!")

# Run the complete workflow
asyncio.run(complete_workflow())
```

## Key Concepts

### World Model
A learned representation of how the environment works. It predicts:
- How states change based on actions
- What rewards to expect
- When episodes end

### Transitions
Experiences that connect states through actions:
- **State**: Current situation (e.g., robot position)
- **Action**: What was done (e.g., "move forward")
- **Next State**: Resulting situation
- **Reward**: Feedback received
- **Done**: Whether episode finished

### Planning Algorithms
Different strategies for finding good action sequences:
- **Random Shooting**: Try many random plans, pick best
- **CEM**: Cross-Entropy Method, iteratively improve plans

## Next Steps

- **Tutorial 2**: Advanced prediction with uncertainty estimation
- **Tutorial 3**: Imagination-based learning
- **Tutorial 4**: Causal reasoning and interventions

## Common Issues

### Issue: Low model accuracy
**Solution:** Collect more diverse experiences, try stochastic models

### Issue: Poor predictions
**Solution:** Check if states/actions match training data distribution

### Issue: Slow planning
**Solution:** Reduce horizon or num_simulations, use faster algorithms

## Further Reading

- API Documentation: `docs/sphinx/build/html/modules/world_models.html`
- Test Examples: `tests/test_world_models.py`
- Source Code: `src/world_models/world_models_services.py`
