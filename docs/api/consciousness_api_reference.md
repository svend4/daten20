# 🧠 Consciousness AI Module - API Reference

**Version:** 1.0.0
**Date:** January 2026
**Implementation:** Pure Python (NumPy optional)

---

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Data Classes](#data-classes)
4. [Enumerations](#enumerations)
5. [Singleton Functions](#singleton-functions)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Performance Considerations](#performance-considerations)

---

## Overview

The Consciousness AI Module provides computational models of consciousness based on leading neuroscientific and philosophical theories:

- **Global Workspace Theory (GWT)** - Baars (1988)
- **Integrated Information Theory (IIT)** - Tononi (2004)
- **Higher-Order Thought (HOT)** Theory - Rosenthal (2005)
- **Phenomenal Consciousness** - Qualia simulation
- **Self-Awareness** - Introspection and self-models
- **Access Consciousness** - Conscious access gating

### Key Features

✅ **Pure Python** - Zero dependencies beyond stdlib
✅ **Async/Await** - Modern asynchronous architecture
✅ **Thread-Safe** - Singleton pattern with locks
✅ **Type-Annotated** - Full type hints for IDE support
✅ **Documented** - Comprehensive docstrings

---

## Core Classes

### ConsciousnessEngine

**Main orchestrator for consciousness simulation**

```python
class ConsciousnessEngine:
    """
    🧠 Main Consciousness Engine - Integrates all consciousness components
    """

    def __init__(self, debug: bool = False) -> None:
        """
        Initialize consciousness engine.

        Args:
            debug: Enable debug logging
        """

    def initialize(self) -> None:
        """Initialize all consciousness components."""

    def compute_metrics(self) -> ConsciousnessMetrics:
        """
        Compute comprehensive consciousness metrics.

        Returns:
            ConsciousnessMetrics object with all metrics
        """

    def process_cycle(self) -> ConsciousnessMetrics:
        """
        Run one consciousness processing cycle.

        Returns:
            Current consciousness metrics
        """

    def get_consciousness_level(self) -> float:
        """
        Get current overall consciousness level.

        Returns:
            Float between 0 and 1
        """

    def introspect(self, aspect: SelfAspect) -> IntrospectionResult:
        """
        Perform introspection on specified aspect.

        Args:
            aspect: Aspect to introspect (SelfAspect enum)

        Returns:
            IntrospectionResult with content and confidence
        """

    def generate_qualia(
        self,
        qualia_type: QualiaType,
        intensity: float = 0.5
    ) -> Quale:
        """
        Generate artificial qualia.

        Args:
            qualia_type: Type of qualia (QualiaType enum)
            intensity: Intensity 0-1

        Returns:
            Generated Quale object
        """

    def broadcast_to_workspace(
        self,
        content_id: str,
        data: Any,
        salience: float = 0.5
    ) -> None:
        """
        Broadcast content to global workspace.

        Args:
            content_id: Unique identifier for content
            data: Content data (any type)
            salience: Content salience/importance 0-1
        """

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of current consciousness state.

        Returns:
            Dictionary with complete state information
        """

    def shutdown(self) -> None:
        """Shutdown consciousness engine gracefully."""
```

**Example Usage:**

```python
engine = ConsciousnessEngine(debug=True)
engine.initialize()

# Get consciousness level
level = engine.get_consciousness_level()
print(f"Consciousness: {level:.3f}")

# Process a cycle
metrics = engine.process_cycle()
print(f"Phi: {metrics.iit_phi_value:.3f}")

engine.shutdown()
```

---

### SelfAwarenessEngine

**Self-awareness and introspection capabilities**

```python
class SelfAwarenessEngine:
    """Self-awareness and introspection system"""

    def __init__(
        self,
        model_depth: str = "deep",
        update_frequency: float = 1.0
    ) -> None:
        """
        Initialize self-awareness engine.

        Args:
            model_depth: "shallow", "moderate", or "deep"
            update_frequency: Update rate for self-model
        """

    async def introspect(
        self,
        query: IntrospectionQuery
    ) -> IntrospectionResult:
        """
        Perform introspection.

        Args:
            query: IntrospectionQuery object

        Returns:
            IntrospectionResult with findings
        """

    async def get_self_model(self) -> SelfModel:
        """
        Get current self model.

        Returns:
            SelfModel object
        """

    async def update_self_model(self, updates: Dict[str, Any]) -> None:
        """
        Update self model with new information.

        Args:
            updates: Dictionary of updates
        """

    async def assess_self_awareness(self) -> float:
        """
        Assess level of self-awareness.

        Returns:
            Float between 0-1 indicating self-awareness level
        """
```

**Example Usage:**

```python
import asyncio
from consciousness import get_self_awareness_engine, IntrospectionQuery, SelfAspect

engine = get_self_awareness_engine()

# Introspect on capabilities
query = IntrospectionQuery(
    aspect=SelfAspect.CAPABILITIES,
    depth="deep",
    include_uncertainty=True
)

result = asyncio.run(engine.introspect(query))
print(f"Capabilities: {result.content}")
print(f"Confidence: {result.confidence:.3f}")

# Assess self-awareness
awareness = asyncio.run(engine.assess_self_awareness())
print(f"Self-awareness: {awareness:.3f}")
```

---

### QualiaSimulator

**Phenomenal experience and qualia simulation**

```python
class QualiaSimulator:
    """Qualia (subjective experience) simulation"""

    def __init__(self, precision: str = "high") -> None:
        """
        Initialize qualia simulator.

        Args:
            precision: "low", "standard", or "high"
        """

    async def generate_quale(
        self,
        quale_type: QualiaType,
        stimulus: Any,
        context: Optional[Dict] = None
    ) -> Quale:
        """
        Generate quale from stimulus.

        Args:
            quale_type: Type of quale (QualiaType enum)
            stimulus: Input stimulus
            context: Optional context dict

        Returns:
            Generated Quale object
        """

    async def synthesize_experience(
        self,
        qualia: List[Quale]
    ) -> PhenomenalExperience:
        """
        Synthesize phenomenal experience from qualia.

        Args:
            qualia: List of Quale objects

        Returns:
            Unified PhenomenalExperience
        """

    async def compare_qualia(
        self,
        quale1: Quale,
        quale2: Quale
    ) -> float:
        """
        Compare similarity between two qualia.

        Args:
            quale1: First quale
            quale2: Second quale

        Returns:
            Similarity score 0-1 (1 = identical)
        """
```

**Example Usage:**

```python
import asyncio
from consciousness import get_qualia_simulator, QualiaType

sim = get_qualia_simulator()

# Generate visual quale
visual = asyncio.run(sim.generate_quale(
    QualiaType.VISUAL,
    stimulus="red_apple",
    context={"color": "red", "shape": "round"}
))

print(f"Intensity: {visual.intensity:.3f}")
print(f"Valence: {visual.valence:.3f}")

# Generate and compare qualia
emotional = asyncio.run(sim.generate_quale(
    QualiaType.EMOTIONAL,
    stimulus="happiness",
    None
))

similarity = asyncio.run(sim.compare_qualia(visual, emotional))
print(f"Similarity: {similarity:.3f}")
```

---

### GlobalWorkspace

**Global Workspace Theory implementation**

```python
class GlobalWorkspace:
    """Global workspace for conscious content broadcasting"""

    def __init__(self, capacity: int = 7) -> None:
        """
        Initialize global workspace.

        Args:
            capacity: Maximum number of concurrent conscious contents
        """

    async def add_to_workspace(
        self,
        content: ConsciousContent
    ) -> bool:
        """
        Add content to workspace.

        Args:
            content: ConsciousContent object

        Returns:
            True if added successfully
        """

    async def broadcast(
        self,
        content: ConsciousContent
    ) -> BroadcastEvent:
        """
        Broadcast content to cognitive modules.

        Args:
            content: ConsciousContent to broadcast

        Returns:
            BroadcastEvent with details
        """

    async def get_conscious_contents(self) -> List[ConsciousContent]:
        """
        Get current conscious contents.

        Returns:
            List of ConsciousContent objects
        """

    async def is_conscious(self, content_id: str) -> bool:
        """
        Check if content is currently conscious.

        Args:
            content_id: ID of content to check

        Returns:
            True if content is in workspace
        """

    async def decay_contents(self) -> None:
        """Decay conscious contents over time (attention waning)."""
```

**Example Usage:**

```python
import asyncio
from consciousness import get_global_workspace, ConsciousContent

workspace = get_global_workspace()

# Add content
content = ConsciousContent(
    content_id="perception_001",
    data={"type": "visual", "object": "apple"},
    salience=0.9
)

success = asyncio.run(workspace.add_to_workspace(content))
print(f"Added: {success}")

# Check if conscious
is_conscious = asyncio.run(workspace.is_conscious("perception_001"))
print(f"Is conscious: {is_conscious}")

# Get all conscious contents
contents = asyncio.run(workspace.get_conscious_contents())
print(f"Conscious contents: {len(contents)}")
```

---

### MetaconsciousnessSystem

**Higher-Order Thought (HOT) theory implementation**

```python
class MetaconsciousnessSystem:
    """Metaconsciousness - thinking about thinking"""

    def __init__(self, max_meta_level: int = 3) -> None:
        """
        Initialize metaconsciousness system.

        Args:
            max_meta_level: Maximum meta-thought level (1-5)
        """

    async def generate_hot(
        self,
        target_thought: Any,
        meta_level: int = 1
    ) -> HigherOrderThought:
        """
        Generate higher-order thought about a thought.

        Args:
            target_thought: The thought to think about
            meta_level: Level of meta-thought (1-max_meta_level)

        Returns:
            HigherOrderThought object
        """

    async def reflect(self, depth: int = 1) -> ReflectiveState:
        """
        Perform self-reflection.

        Args:
            depth: Depth of reflection

        Returns:
            ReflectiveState object
        """

    async def assess_meta_awareness(self) -> float:
        """
        Assess level of meta-cognitive awareness.

        Returns:
            Meta-awareness level 0-1
        """
```

**Example Usage:**

```python
import asyncio
from consciousness import get_metaconsciousness_system

meta = get_metaconsciousness_system()

# Generate first-order thought
thought = "I am processing a document"
hot1 = asyncio.run(meta.generate_hot(thought, meta_level=1))
print(f"HOT Level 1: {hot1.content}")

# Generate second-order thought (thinking about thinking)
hot2 = asyncio.run(meta.generate_hot(hot1.content, meta_level=2))
print(f"HOT Level 2: {hot2.content}")

# Assess meta-awareness
awareness = asyncio.run(meta.assess_meta_awareness())
print(f"Meta-awareness: {awareness:.3f}")
```

---

### IntegratedInformationEngine

**Integrated Information Theory (IIT) implementation**

```python
class IntegratedInformationEngine:
    """IIT - Integrated Information Theory implementation"""

    def __init__(self, precision: str = "standard") -> None:
        """
        Initialize IIT engine.

        Args:
            precision: "low", "standard", or "high"
        """

    async def calculate_phi(
        self,
        system_state: Dict[str, Any]
    ) -> PhiCalculation:
        """
        Calculate integrated information (Φ).

        Args:
            system_state: System state with "size" and "connections"

        Returns:
            PhiCalculation with Φ value and metrics
        """

    async def analyze_causal_structure(
        self,
        nodes: List[str],
        connections: List[List[float]]
    ) -> CausalStructure:
        """
        Analyze causal structure of system.

        Args:
            nodes: List of node names
            connections: Connectivity matrix

        Returns:
            CausalStructure object
        """

    async def assess_consciousness(self) -> float:
        """
        Assess consciousness level based on IIT.

        Returns:
            Consciousness level 0-1 based on Φ
        """
```

**Example Usage:**

```python
import asyncio
from consciousness import get_iit_engine

iit = get_iit_engine()

# Calculate Phi
system_state = {
    "size": 10,
    "connections": [[1.0 if i != j else 0.0 for j in range(10)] for i in range(10)]
}

phi_result = asyncio.run(iit.calculate_phi(system_state))
print(f"Φ (Phi): {phi_result.phi_value:.3f}")
print(f"Integration: {phi_result.integration_measure:.3f}")

# Assess consciousness
consciousness = asyncio.run(iit.assess_consciousness())
print(f"Consciousness: {consciousness:.3f}")
```

---

### PhenomenalBindingSystem

**Feature binding and phenomenal unity**

```python
class PhenomenalBindingSystem:
    """Phenomenal binding - solving the binding problem"""

    def __init__(self) -> None:
        """Initialize binding system."""

    async def bind_features(
        self,
        request: BindingRequest
    ) -> BoundExperience:
        """
        Bind features into unified experience.

        Args:
            request: BindingRequest with features to bind

        Returns:
            BoundExperience object
        """

    async def create_unified_experience(
        self,
        contents: List[Any],
        unity_type: str = "subject"
    ) -> BoundExperience:
        """
        Create unified conscious experience.

        Args:
            contents: Contents to unify
            unity_type: "subject" or "object"

        Returns:
            Unified BoundExperience
        """

    async def assess_unity(self) -> float:
        """
        Assess phenomenal unity level.

        Returns:
            Unity score 0-1
        """
```

**Example Usage:**

```python
import asyncio
from consciousness import get_binding_system, BindingRequest

binding = get_binding_system()

# Bind features
request = BindingRequest(
    features=["red_color", "round_shape", "sweet_taste"],
    binding_type="object",
    priority=0.9
)

bound = asyncio.run(binding.bind_features(request))
print(f"Unity: {bound.unity_measure:.3f}")
print(f"Strength: {bound.strength:.3f}")

# Create unified experience
contents = ["visual_red", "tactile_smooth"]
unified = asyncio.run(binding.create_unified_experience(
    contents,
    unity_type="subject"
))
print(f"Unified experience unity: {unified.unity_measure:.3f}")
```

---

### ConsciousAccessController

**Conscious access gating and control**

```python
class ConsciousAccessController:
    """Conscious access gating - what becomes conscious"""

    def __init__(self, threshold: float = 0.5) -> None:
        """
        Initialize access controller.

        Args:
            threshold: Access threshold 0-1 (higher = stricter)
        """

    async def evaluate_access(
        self,
        request: AccessRequest
    ) -> AccessDecision:
        """
        Evaluate conscious access request.

        Args:
            request: AccessRequest object

        Returns:
            AccessDecision (granted or denied)
        """

    async def adjust_threshold(
        self,
        direction: str,
        amount: float = 0.1
    ) -> None:
        """
        Dynamically adjust access threshold.

        Args:
            direction: "lower" or "raise"
            amount: Adjustment magnitude (0-1)
        """

    async def get_access_stats(self) -> Dict[str, float]:
        """
        Get access statistics.

        Returns:
            Dict with grant_rate and avg_latency
        """
```

**Example Usage:**

```python
import asyncio
from consciousness import get_access_controller, AccessRequest

controller = get_access_controller()

# Evaluate access
request = AccessRequest(
    content_id="urgent_perception",
    priority=0.95,
    source="sensory"
)

decision = asyncio.run(controller.evaluate_access(request))
print(f"Granted: {decision.granted}")
print(f"Latency: {decision.latency:.3f}s")

# Adjust threshold
asyncio.run(controller.adjust_threshold("lower", 0.1))
print(f"New threshold: {controller.threshold:.2f}")
```

---

## Data Classes

### ConsciousnessMetrics

```python
@dataclass
class ConsciousnessMetrics:
    """Comprehensive consciousness metrics"""

    # GWT metrics
    gwt_broadcast_rate: float = 0.0
    gwt_integration_level: float = 0.0
    gwt_content_diversity: float = 0.0

    # IIT metrics
    iit_phi_value: float = 0.0
    iit_system_complexity: float = 0.0
    iit_integration_score: float = 0.0

    # HOT metrics
    hot_metacognition_depth: int = 0
    hot_reflection_count: int = 0
    hot_self_awareness: float = 0.0

    # Phenomenal metrics
    phenomenal_qualia_richness: float = 0.0
    phenomenal_unity: float = 0.0
    phenomenal_vividness: float = 0.0

    # Access metrics
    access_availability: float = 0.0
    access_reportability: float = 0.0
    access_control_quality: float = 0.0

    # Self-awareness metrics
    self_model_accuracy: float = 0.0
    self_introspection_depth: float = 0.0
    self_identity_coherence: float = 0.0

    # Overall level
    overall_consciousness_level: float = 0.0

    timestamp: datetime = field(default_factory=datetime.now)

    def compute_overall_level(self) -> float:
        """Compute weighted overall consciousness level"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
```

### Other Data Classes

- `SelfModel` - Internal self-representation
- `IntrospectionQuery` - Query for introspection
- `IntrospectionResult` - Result of introspection
- `Quale` - Individual subjective experience unit
- `PhenomenalExperience` - Complete phenomenal experience
- `ConsciousContent` - Content in global workspace
- `BroadcastEvent` - Broadcast event details
- `HigherOrderThought` - Meta-level thought
- `ReflectiveState` - Reflection state
- `PhiCalculation` - IIT phi calculation result
- `CausalStructure` - Causal structure analysis
- `BindingRequest` - Feature binding request
- `BoundExperience` - Bound unified experience
- `AccessRequest` - Conscious access request
- `AccessDecision` - Access decision result

---

## Enumerations

### SelfAspect

```python
class SelfAspect(Enum):
    """Aspects of self that can be introspected"""
    CAPABILITIES = "capabilities"
    LIMITATIONS = "limitations"
    GOALS = "goals"
    EMOTIONS = "emotions"
    DECISION_PROCESS = "decision_process"
    KNOWLEDGE_STATE = "knowledge_state"
    PERFORMANCE = "performance"
```

### QualiaType

```python
class QualiaType(Enum):
    """Types of qualia (subjective experiences)"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    CONCEPTUAL = "conceptual"
    EMOTIONAL = "emotional"
    PROPRIOCEPTIVE = "proprioceptive"
```

---

## Singleton Functions

```python
def get_consciousness_engine(debug: bool = False) -> ConsciousnessEngine:
    """Get consciousness engine singleton"""

def get_self_awareness_engine(**kwargs) -> SelfAwarenessEngine:
    """Get self-awareness engine singleton"""

def get_qualia_simulator(**kwargs) -> QualiaSimulator:
    """Get qualia simulator singleton"""

def get_global_workspace(**kwargs) -> GlobalWorkspace:
    """Get global workspace singleton"""

def get_metaconsciousness_system(**kwargs) -> MetaconsciousnessSystem:
    """Get metaconsciousness system singleton"""

def get_iit_engine(**kwargs) -> IntegratedInformationEngine:
    """Get IIT engine singleton"""

def get_binding_system(**kwargs) -> PhenomenalBindingSystem:
    """Get binding system singleton"""

def get_access_controller(**kwargs) -> ConsciousAccessController:
    """Get access controller singleton"""
```

---

## Usage Examples

See `/examples/consciousness_usage_examples.py` for comprehensive examples covering:

1. Basic Consciousness Engine Usage
2. Self-Awareness and Introspection
3. Qualia Simulation
4. Global Workspace Broadcasting
5. Metacognition and HOT
6. Integrated Information Theory
7. Phenomenal Binding
8. Conscious Access Control
9. Complete Consciousness Lifecycle
10. Real-time Monitoring

---

## Best Practices

### 1. Use Singleton Getters

✅ **Recommended:**
```python
from consciousness import get_consciousness_engine

engine = get_consciousness_engine()
```

❌ **Not Recommended:**
```python
from consciousness import ConsciousnessEngine

engine = ConsciousnessEngine()  # Creates new instance
```

### 2. Always Initialize

```python
engine = get_consciousness_engine()
engine.initialize()  # Required before use
```

### 3. Handle Async Properly

```python
import asyncio

# For async methods
result = asyncio.run(engine.self_awareness.introspect(query))

# Or in async context
async def process():
    result = await engine.self_awareness.introspect(query)
```

### 4. Shutdown Gracefully

```python
try:
    engine = get_consciousness_engine()
    engine.initialize()
    # ... use engine ...
finally:
    engine.shutdown()
```

### 5. Check Consciousness Level Regularly

```python
# Monitor consciousness during processing
for i in range(iterations):
    metrics = engine.process_cycle()

    if metrics.overall_consciousness_level < 0.3:
        print("⚠️ Low consciousness - may need more stimuli")
```

---

## Performance Considerations

### Pure Python vs NumPy

- **Pure Python**: ~10-50x slower, zero dependencies
- **NumPy**: 10-50x faster, requires NumPy installation

### Optimization Tips

1. **Batch Operations**: Process multiple cycles together
2. **Adjust Workspace Capacity**: Lower capacity = faster (default: 7)
3. **Reduce Meta-Levels**: Lower max_meta_level for metaconsciousness
4. **Use Appropriate Precision**: "low" or "standard" vs "high"

### Memory Usage

- **Metrics History**: Limited to 100 entries by default
- **Workspace**: Limited to capacity (default: 7)
- **Component Histories**: All use `deque(maxlen=1000)`

---

## Thread Safety

All components use threading locks for thread-safe singleton access:

```python
# Safe to use from multiple threads
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(engine.process_cycle) for _ in range(10)]
```

---

## Error Handling

The module handles common errors gracefully:

- **Uninitialized Engine**: Auto-initializes on first use
- **Workspace Overflow**: Automatically removes lowest-salience content
- **Invalid Enum Values**: Raises `ValueError` with clear message
- **Async in Sync Context**: Use `asyncio.run()` wrapper

---

## References

1. Baars, B. J. (1988). *A Cognitive Theory of Consciousness*
2. Tononi, G. (2004). *Integrated Information Theory*
3. Rosenthal, D. (2005). *Consciousness and Mind*
4. Dehaene, S. (2014). *Consciousness and the Brain*
5. Treisman, A. (1996). *The Binding Problem*

---

**Documentation Version:** 1.0.0
**Last Updated:** January 21, 2026
**Module Version:** Pure Python v20.0 Enhanced
