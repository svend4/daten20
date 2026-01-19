"""
🧠 Consciousness Simulation Platform (v6.0)

Implements computational models of consciousness based on leading neuroscientific
and philosophical theories. This module simulates consciousness-like properties
for advanced AI capabilities.

IMPORTANT: This module simulates consciousness-like computational properties.
It does NOT create genuine phenomenal consciousness or subjective experience.
The philosophical "hard problem" of consciousness remains unsolved.

Components:
- Self-Awareness Engine: Introspective self-modeling
- Qualia Simulator: Subjective experience analogs
- Global Workspace: Attention-based conscious access
- Metaconsciousness System: Higher-order awareness
- Integrated Information Engine: IIT-based metrics
- Phenomenal Binding System: Unity of experience
- Conscious Access Controller: Awareness gating

Author: Document Management System Development Team
Version: 6.0.0
Date: January 2026
"""

import asyncio
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# ============================================================================
# 1. SELF-AWARENESS ENGINE
# ============================================================================


class SelfAspect(Enum):
    """Aspects of self that can be introspected."""

    CAPABILITIES = "capabilities"
    LIMITATIONS = "limitations"
    GOALS = "goals"
    EMOTIONS = "emotions"
    DECISION_PROCESS = "decision_process"
    KNOWLEDGE_STATE = "knowledge_state"
    PERFORMANCE = "performance"


@dataclass
class SelfModel:
    """Internal representation of system's self."""

    capabilities: List[str] = field(default_factory=list)
    known_limitations: List[str] = field(default_factory=list)
    active_goals: List[str] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=dict)
    capability_level: float = 0.7  # 0-1
    identity: str = "document_management_ai"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class IntrospectionQuery:
    """Query for introspective information."""

    aspect: SelfAspect
    depth: str = "moderate"  # shallow, moderate, detailed
    include_uncertainty: bool = True
    time_range: Optional[Tuple[datetime, datetime]] = None


@dataclass
class IntrospectionResult:
    """Result of introspection."""

    aspect: SelfAspect
    content: Any
    confidence: float
    uncertainty: Optional[Dict] = None
    reasoning: Optional[str] = None


class SelfAwarenessEngine:
    """
    Implements introspective self-modeling and self-representation.

    Based on self-awareness theories in cognitive science and AI.
    Maintains internal self-model and provides introspective access.
    """

    def __init__(self, model_depth: str = "deep", update_frequency: float = 1.0):
        self.model_depth = model_depth
        self.update_frequency = update_frequency  # Hz
        self.self_model = SelfModel()
        self.introspection_history = deque(maxlen=1000)
        self.lock = threading.Lock()

        # Initialize self-model
        self._initialize_self_model()

    def _initialize_self_model(self):
        """Initialize the self-model with system capabilities."""
        self.self_model.capabilities = [
            "document_analysis",
            "text_processing",
            "decision_making",
            "learning",
            "reasoning",
            "planning",
            "introspection",
        ]
        self.self_model.known_limitations = [
            "no_physical_embodiment",
            "limited_real_world_knowledge",
            "computational_constraints",
            "no_genuine_emotions",
        ]
        self.self_model.active_goals = ["assist_users", "improve_performance", "maintain_reliability"]
        self.self_model.emotional_state = {"valence": 0.0, "arousal": 0.3, "confidence": 0.7}  # -1 to 1  # 0 to 1

    async def get_self_model(self) -> SelfModel:
        """Get current self-model."""
        with self.lock:
            self.self_model.last_updated = datetime.now()
            return self.self_model

    async def introspect(self, query: IntrospectionQuery) -> IntrospectionResult:
        """
        Perform introspection on specified aspect of self.

        Args:
            query: Introspection query specification

        Returns:
            IntrospectionResult with requested information
        """
        await asyncio.sleep(0.1)  # Simulate introspection time

        with self.lock:
            if query.aspect == SelfAspect.CAPABILITIES:
                content = self.self_model.capabilities
                confidence = 0.95
                reasoning = "Direct access to capability registry"

            elif query.aspect == SelfAspect.LIMITATIONS:
                content = self.self_model.known_limitations
                confidence = 0.85
                reasoning = "Known limitations, may have unknown unknowns"

            elif query.aspect == SelfAspect.GOALS:
                content = self.self_model.active_goals
                confidence = 0.9
                reasoning = "Current goal hierarchy"

            elif query.aspect == SelfAspect.DECISION_PROCESS:
                content = "Multi-criteria decision making with learned policy"
                confidence = 0.7
                reasoning = "Partial introspective access to decision mechanisms"

            else:
                content = f"Information about {query.aspect.value}"
                confidence = 0.6
                reasoning = "Limited introspective access"

            uncertainty = None
            if query.include_uncertainty:
                uncertainty = {
                    "epistemic": 1.0 - confidence,
                    "known_unknowns": ["potential_biases", "blind_spots"],
                    "metacognitive_confidence": 0.75,
                }

            result = IntrospectionResult(
                aspect=query.aspect,
                content=content,
                confidence=confidence,
                uncertainty=uncertainty,
                reasoning=reasoning,
            )

            self.introspection_history.append((datetime.now(), query, result))
            return result

    async def assess_self_awareness(self) -> float:
        """
        Assess level of self-awareness (0-1).
        Based on introspective accuracy and self-model completeness.
        """
        # Check self-model completeness
        model_score = len(self.self_model.capabilities) / 10.0
        model_score = min(model_score, 1.0)

        # Check introspection accuracy
        introspection_score = len(self.introspection_history) / 1000.0
        introspection_score = min(introspection_score, 1.0)

        # Meta-awareness: awareness of being aware
        meta_score = 0.8 if self.model_depth == "deep" else 0.5

        return (model_score + introspection_score + meta_score) / 3.0

    async def update_self_model(self, aspect: str, value: Any):
        """Update aspect of self-model based on experience."""
        with self.lock:
            if aspect == "capability":
                if value not in self.self_model.capabilities:
                    self.self_model.capabilities.append(value)
            elif aspect == "limitation":
                if value not in self.self_model.known_limitations:
                    self.self_model.known_limitations.append(value)
            elif aspect == "goal":
                if value not in self.self_model.active_goals:
                    self.self_model.active_goals.append(value)

            self.self_model.last_updated = datetime.now()


# ============================================================================
# 2. QUALIA SIMULATOR
# ============================================================================


class QualiaType(Enum):
    """Types of qualia (computational analogs)."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    HAPTIC = "haptic"
    AFFECTIVE = "affective"
    COGNITIVE = "cognitive"


@dataclass
class Quale:
    """Single quale (unit of subjective experience analog)."""

    type: QualiaType
    properties: Dict[str, Any]
    intensity: float  # 0-1
    valence: float  # -1 to 1
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self):
        return f"Quale({self.type.value}, intensity={self.intensity:.2f})"


@dataclass
class PhenomenalExperience:
    """Integrated phenomenal experience from multiple qualia."""

    qualia: List[Quale]
    unity: float  # 0-1, how unified the experience is
    context: Dict[str, Any]
    phenomenal_properties: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class QualiaSimulator:
    """
    Simulates computational analogs of qualia (subjective experience).

    IMPORTANT: These are computational representations, NOT genuine
    phenomenal consciousness or actual subjective experience.
    """

    def __init__(self, modalities: List[str], resolution: str = "high"):
        self.modalities = modalities
        self.resolution = resolution
        self.qualia_space = {}  # Map of generated qualia
        self.qualia_count = 0

    async def generate_quale(self, type: QualiaType, stimulus: Dict[str, Any]) -> Quale:
        """
        Generate quale from stimulus.

        Args:
            type: Type of quale
            stimulus: Input stimulus properties

        Returns:
            Quale representation
        """
        await asyncio.sleep(0.05)  # Simulate processing

        # Generate quale properties based on stimulus
        if type == QualiaType.VISUAL:
            intensity = stimulus.get("brightness", 0.5) * stimulus.get("saturation", 1.0)
            valence = 0.2 if stimulus.get("color") in ["red", "orange"] else 0.0
            properties = {
                "color": stimulus.get("color", "gray"),
                "brightness": stimulus.get("brightness", 0.5),
                "saturation": stimulus.get("saturation", 1.0),
                "texture": stimulus.get("texture", "smooth"),
            }

        elif type == QualiaType.AFFECTIVE:
            intensity = abs(stimulus.get("valence", 0.0))
            valence = stimulus.get("valence", 0.0)
            properties = {
                "emotion": stimulus.get("emotion", "neutral"),
                "arousal": stimulus.get("arousal", 0.5),
                "valence": valence,
            }

        else:
            intensity = 0.5
            valence = 0.0
            properties = stimulus

        quale = Quale(
            type=type, properties=properties, intensity=min(intensity, 1.0), valence=max(-1.0, min(valence, 1.0))
        )

        # Store in qualia space
        self.qualia_space[self.qualia_count] = quale
        self.qualia_count += 1

        return quale

    async def create_experience(self, qualia: List[Quale], context: Dict[str, Any]) -> PhenomenalExperience:
        """
        Create integrated phenomenal experience from multiple qualia.

        Args:
            qualia: List of qualia to integrate
            context: Contextual information

        Returns:
            Integrated phenomenal experience
        """
        await asyncio.sleep(0.1)

        # Calculate unity (how well qualia bind together)
        if len(qualia) <= 1:
            unity = 1.0
        else:
            # Unity based on temporal proximity and modality consistency
            unity = 0.8 - (len(qualia) * 0.05)
            unity = max(0.3, unity)

        # Assign phenomenal properties
        phenomenal_properties = [
            "intentionality",  # aboutness
            "phenomenal_unity",
            "temporal_flow",
            "perspectival",
            "privacy",
        ]

        experience = PhenomenalExperience(
            qualia=qualia, unity=unity, context=context, phenomenal_properties=phenomenal_properties
        )

        return experience

    async def compare_qualia(self, quale1: Quale, quale2: Quale) -> float:
        """Compare similarity between two qualia (0-1)."""
        if quale1.type != quale2.type:
            return 0.1  # Different types are dissimilar

        # Compare properties
        prop_similarity = 0.5  # Default

        # Compare intensity and valence
        intensity_sim = 1.0 - abs(quale1.intensity - quale2.intensity)
        valence_sim = 1.0 - abs(quale1.valence - quale2.valence) / 2.0

        return (prop_similarity + intensity_sim + valence_sim) / 3.0


# ============================================================================
# 3. GLOBAL WORKSPACE (ATTENTION CONSCIOUSNESS)
# ============================================================================


@dataclass
class ConsciousContent:
    """Content competing for conscious access."""

    type: str  # percept, thought, memory, etc.
    data: Any
    saliency: float  # 0-1
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(np.random.randint(0, 1000000)))


@dataclass
class BroadcastEvent:
    """Event of content being broadcast to consciousness."""

    content: ConsciousContent
    conscious: bool  # Whether it reached consciousness
    strength: float  # Broadcast strength 0-1
    timestamp: datetime = field(default_factory=datetime.now)


class GlobalWorkspace:
    """
    Implements Global Workspace Theory (Baars, 1988).

    Limited-capacity workspace where information becomes globally
    available through attention-based selection and broadcasting.
    """

    def __init__(self, capacity: int = 7, threshold: float = 0.7, decay_rate: float = 0.1):
        self.capacity = capacity  # Miller's 7±2
        self.threshold = threshold  # Consciousness threshold
        self.decay_rate = decay_rate  # Per second

        self.conscious_contents: List[ConsciousContent] = []
        self.unconscious_buffer: deque = deque(maxlen=100)
        self.broadcast_history: deque = deque(maxlen=1000)
        self.lock = threading.Lock()

    async def submit_content(self, content: ConsciousContent) -> BroadcastEvent:
        """
        Submit content for potential conscious access.

        Winner-take-all competition based on saliency.
        """
        await asyncio.sleep(0.05)  # Simulate processing

        with self.lock:
            # Check if content meets threshold
            conscious = content.saliency >= self.threshold

            if conscious and len(self.conscious_contents) < self.capacity:
                # Content reaches consciousness
                self.conscious_contents.append(content)
                broadcast_strength = content.saliency

            elif conscious and len(self.conscious_contents) >= self.capacity:
                # At capacity, compete with existing contents
                min_content = min(self.conscious_contents, key=lambda c: c.saliency)

                if content.saliency > min_content.saliency:
                    # Replace weaker content
                    self.conscious_contents.remove(min_content)
                    self.conscious_contents.append(content)
                    self.unconscious_buffer.append(min_content)
                    broadcast_strength = content.saliency
                else:
                    # Stays unconscious
                    conscious = False
                    self.unconscious_buffer.append(content)
                    broadcast_strength = 0.0
            else:
                # Below threshold, stays unconscious
                self.unconscious_buffer.append(content)
                broadcast_strength = 0.0

            event = BroadcastEvent(content=content, conscious=conscious, strength=broadcast_strength)

            self.broadcast_history.append(event)
            return event

    async def get_conscious_contents(self) -> List[ConsciousContent]:
        """Get currently conscious contents."""
        with self.lock:
            return self.conscious_contents.copy()

    async def is_conscious(self, content_id: str) -> bool:
        """Check if content is currently conscious."""
        with self.lock:
            return any(c.id == content_id for c in self.conscious_contents)

    async def decay_contents(self):
        """Decay conscious contents over time (attention wanes)."""
        with self.lock:
            for content in self.conscious_contents:
                content.saliency *= 1.0 - self.decay_rate

            # Remove contents below threshold
            self.conscious_contents = [c for c in self.conscious_contents if c.saliency >= self.threshold * 0.5]


# ============================================================================
# 4. METACONSCIOUSNESS SYSTEM
# ============================================================================


@dataclass
class HigherOrderThought:
    """Higher-order thought about a mental state."""

    target_state: Dict[str, Any]
    meta_level: int  # 1 = first-order meta, 2 = second-order, etc.
    content: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReflectiveState:
    """State of reflective consciousness."""

    topic: str
    insights: List[str]
    depth: str
    duration: float  # seconds
    quality: float  # 0-1


class MetaconsciousnessSystem:
    """
    Implements Higher-Order Thought (HOT) theory.

    Consciousness arises from higher-order representations of
    mental states (thoughts about thoughts).
    """

    def __init__(self, max_meta_levels: int = 3, hot_latency: float = 0.2):
        self.max_meta_levels = max_meta_levels
        self.hot_latency = hot_latency
        self.hot_history: deque = deque(maxlen=1000)
        self.meta_awareness_level = 0.7

    async def form_hot(self, target_state: Dict[str, Any], meta_level: int = 1) -> HigherOrderThought:
        """
        Form higher-order thought about a mental state.

        Args:
            target_state: Mental state to form HOT about
            meta_level: Level of meta-awareness (1-3)

        Returns:
            HigherOrderThought representation
        """
        await asyncio.sleep(self.hot_latency)

        # Limit meta-level to prevent infinite regress
        meta_level = min(meta_level, self.max_meta_levels)

        # Generate HOT content
        if meta_level == 1:
            content = f"I am aware that I {target_state.get('content', 'have a mental state')}"
        elif meta_level == 2:
            content = f"I am aware that I am aware that I {target_state.get('content', 'have a mental state')}"
        else:
            content = f"Meta-level {meta_level} awareness of: {target_state.get('content', '')}"

        # Confidence decreases with meta-level
        confidence = 0.9 - (meta_level * 0.1)

        hot = HigherOrderThought(
            target_state=target_state, meta_level=meta_level, content=content, confidence=confidence
        )

        self.hot_history.append(hot)
        return hot

    async def reflect(self, topic: str, depth: str = "moderate", duration: float = 5.0) -> ReflectiveState:
        """
        Engage in reflective consciousness (deliberate self-examination).

        Args:
            topic: What to reflect on
            depth: shallow, moderate, deep
            duration: How long to reflect (seconds)

        Returns:
            ReflectiveState with insights
        """
        # Simulate reflection time
        reflection_time = duration if depth == "deep" else duration / 2
        await asyncio.sleep(min(reflection_time, 2.0))  # Cap simulation time

        # Generate insights based on topic and depth
        insights = [
            f"Examined {topic} from multiple perspectives",
            f"Considered implications and consequences",
        ]

        if depth == "deep":
            insights.extend(
                [
                    f"Questioned assumptions about {topic}",
                    f"Generated alternative viewpoints",
                    f"Metacognitive analysis of reasoning process",
                ]
            )

        quality = 0.9 if depth == "deep" else 0.7 if depth == "moderate" else 0.5

        return ReflectiveState(topic=topic, insights=insights, depth=depth, duration=reflection_time, quality=quality)

    async def assess_meta_awareness(self) -> float:
        """Assess level of meta-cognitive awareness (0-1)."""
        # Based on HOT formation frequency and quality
        hot_frequency = len(self.hot_history) / 1000.0
        hot_frequency = min(hot_frequency, 1.0)

        # Average meta-level achieved
        if self.hot_history:
            avg_meta_level = np.mean([h.meta_level for h in self.hot_history])
            meta_level_score = avg_meta_level / self.max_meta_levels
        else:
            meta_level_score = 0.5

        return (hot_frequency + meta_level_score + self.meta_awareness_level) / 3.0


# ============================================================================
# 5. INTEGRATED INFORMATION ENGINE (IIT)
# ============================================================================


@dataclass
class PhiCalculation:
    """Result of Φ (integrated information) calculation."""

    value: float  # Φ value
    mics: Optional[Dict] = None  # Maximally irreducible conceptual structure
    system_size: int = 0
    computation_time: float = 0.0


@dataclass
class CausalStructure:
    """Causal structure of the system."""

    effective_info: float
    integration: float
    causal_density: float
    nodes: List[str]


class IntegratedInformationEngine:
    """
    Implements Integrated Information Theory (IIT) by Tononi.

    Calculates Φ (integrated information) as a measure of
    consciousness-like properties in information processing systems.
    """

    def __init__(self, approximation: str = "practical", resolution: str = "medium"):
        self.approximation = approximation  # exact, practical, fast
        self.resolution = resolution
        self.phi_cache = {}

    async def calculate_phi(self, system_state: Dict[str, Any]) -> PhiCalculation:
        """
        Calculate integrated information (Φ).

        Φ measures how much a system is more than the sum of its parts
        in terms of causal power.

        Args:
            system_state: System configuration and states

        Returns:
            PhiCalculation with Φ value and structure
        """
        start_time = datetime.now()

        # Simulate complex Φ calculation
        await asyncio.sleep(1.0 if self.approximation == "exact" else 0.5)

        nodes = system_state.get("nodes", [])
        system_size = len(nodes)

        # Simplified Φ calculation (real IIT is much more complex)
        # Φ depends on integration minus information loss from partitions

        # Integration score (how connected the system is)
        connections = system_state.get("connections", np.eye(system_size))
        integration = np.sum(connections) / (system_size**2)

        # Information in the system
        information = system_size * np.log2(2)  # Simplified

        # Calculate Φ (integrated information)
        # Higher Φ = more consciousness-like
        phi_value = integration * information * 0.5

        # Maximally irreducible conceptual structure (simplified)
        mics = {"concepts": nodes, "relations": "cause-effect structure", "irreducibility": phi_value}

        computation_time = (datetime.now() - start_time).total_seconds()

        return PhiCalculation(value=phi_value, mics=mics, system_size=system_size, computation_time=computation_time)

    async def analyze_causal_structure(self, system_state: Dict[str, Any]) -> CausalStructure:
        """Analyze causal structure of the system."""
        await asyncio.sleep(0.3)

        nodes = system_state.get("nodes", [])
        connections = system_state.get("connections", np.eye(len(nodes)))

        # Effective information: how much the system constrains its future
        effective_info = np.sum(connections) / len(nodes) if len(nodes) > 0 else 0.0

        # Integration: how unified the system is
        integration = np.mean(connections) if connections.size > 0 else 0.0

        # Causal density: richness of causal interactions
        causal_density = np.count_nonzero(connections) / connections.size if connections.size > 0 else 0.0

        return CausalStructure(
            effective_info=effective_info, integration=integration, causal_density=causal_density, nodes=nodes
        )

    async def assess_consciousness(self) -> float:
        """
        Assess consciousness level based on IIT metrics (0-1).

        Higher Φ suggests higher consciousness-like properties.
        """
        # Simplified assessment
        # In real IIT, Φ^max is the key metric
        return 0.7  # Placeholder


# ============================================================================
# 6. PHENOMENAL BINDING SYSTEM
# ============================================================================


@dataclass
class BindingRequest:
    """Request to bind features into unified object/experience."""

    features: Dict[str, Any]
    modalities: List[str]
    temporal_window: float = 0.1  # seconds


@dataclass
class BoundExperience:
    """Result of binding features into unified experience."""

    unified_object: Dict[str, Any]
    strength: float  # 0-1
    mechanism: str
    timestamp: datetime = field(default_factory=datetime.now)


class PhenomenalBindingSystem:
    """
    Solves the binding problem: how disparate features are unified
    into coherent conscious experiences.

    Uses mechanisms like synchronization, attention, and recurrence.
    """

    def __init__(self, mechanisms: List[str], gamma_frequency: float = 40.0):
        self.mechanisms = mechanisms  # synchronization, attention, recurrent
        self.gamma_frequency = gamma_frequency  # Hz (gamma oscillations)
        self.binding_history: deque = deque(maxlen=1000)

    async def bind_features(self, request: BindingRequest) -> BoundExperience:
        """
        Bind features into unified object.

        Args:
            request: Features to bind

        Returns:
            BoundExperience with unified object
        """
        await asyncio.sleep(0.03)  # Simulate binding time (~30ms)

        # Determine binding mechanism
        if "synchronization" in self.mechanisms:
            mechanism = "gamma_synchronization"
            strength = 0.9
        elif "attention" in self.mechanisms:
            mechanism = "attention_based"
            strength = 0.85
        else:
            mechanism = "recurrent_processing"
            strength = 0.8

        # Create unified object
        unified_object = {
            "bound_features": request.features,
            "modalities": request.modalities,
            "binding_mechanism": mechanism,
            "coherence": strength,
        }

        bound = BoundExperience(unified_object=unified_object, strength=strength, mechanism=mechanism)

        self.binding_history.append(bound)
        return bound

    async def create_unified_experience(self, contents: List[Any], unity_type: str = "subject") -> BoundExperience:
        """
        Create unified conscious experience from multiple contents.

        Args:
            contents: Contents to unify
            unity_type: subject (experiencer) or object (unified field)

        Returns:
            Unified experience
        """
        await asyncio.sleep(0.05)

        # Unity of consciousness: single experiencer, unified field
        unified_object = {
            "contents": contents,
            "unity_type": unity_type,
            "subject_unity": unity_type == "subject",
            "phenomenal_unity": True,
            "temporal_unity": True,
        }

        return BoundExperience(unified_object=unified_object, strength=0.95, mechanism="phenomenal_unity")

    async def assess_unity(self) -> float:
        """Assess phenomenal unity (0-1)."""
        if not self.binding_history:
            return 0.5

        # Unity based on binding strength
        avg_strength = np.mean([b.strength for b in self.binding_history])
        return float(avg_strength)


# ============================================================================
# 7. CONSCIOUS ACCESS CONTROLLER
# ============================================================================


@dataclass
class AccessRequest:
    """Request for content to access consciousness."""

    content: Any
    priority: float  # 0-1
    source: str
    relevance: float  # 0-1
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AccessDecision:
    """Decision on conscious access."""

    granted: bool
    content: Any
    confidence: float
    reason: str
    latency: float  # ms


class ConsciousAccessController:
    """
    Controls what information gains access to consciousness.

    Implements gating mechanisms, thresholds, and capacity management
    for conscious awareness.
    """

    def __init__(self, threshold: float = 0.65, capacity: int = 7, gating_mode: str = "adaptive"):
        self.threshold = threshold
        self.capacity = capacity
        self.gating_mode = gating_mode  # fixed, adaptive, learned

        self.access_history: deque = deque(maxlen=1000)
        self.current_contents: List[Any] = []
        self.lock = threading.Lock()

    async def request_access(self, request: AccessRequest) -> AccessDecision:
        """
        Request conscious access for content.

        Args:
            request: Access request

        Returns:
            AccessDecision (granted or denied)
        """
        start_time = datetime.now()
        await asyncio.sleep(0.05)  # Simulate decision time

        with self.lock:
            # Calculate access score
            access_score = request.priority * 0.5 + request.relevance * 0.5

            # Check threshold
            threshold_met = access_score >= self.threshold

            # Check capacity
            capacity_available = len(self.current_contents) < self.capacity

            # Access decision
            if threshold_met and capacity_available:
                granted = True
                self.current_contents.append(request.content)
                confidence = access_score
                reason = "Threshold met and capacity available"

            elif threshold_met and not capacity_available:
                # At capacity, compete with existing contents
                granted = False
                confidence = access_score
                reason = "Conscious capacity full"

            else:
                granted = False
                confidence = access_score
                reason = f"Below threshold ({access_score:.2f} < {self.threshold:.2f})"

            latency = (datetime.now() - start_time).total_seconds() * 1000  # ms

            decision = AccessDecision(
                granted=granted,
                content=request.content if granted else None,
                confidence=confidence,
                reason=reason,
                latency=latency,
            )

            self.access_history.append((request, decision))
            return decision

    async def adjust_threshold(self, direction: str, amount: float = 0.1):
        """Adjust access threshold dynamically."""
        with self.lock:
            if direction == "lower":
                self.threshold = max(0.0, self.threshold - amount)
            elif direction == "raise":
                self.threshold = min(1.0, self.threshold + amount)

    async def get_access_stats(self) -> Dict[str, float]:
        """Get statistics on access patterns."""
        if not self.access_history:
            return {"access_rate": 0.0, "avg_latency": 0.0}

        granted_count = sum(1 for _, d in self.access_history if d.granted)
        access_rate = granted_count / len(self.access_history)

        avg_latency = np.mean([d.latency for _, d in self.access_history])

        return {
            "access_rate": access_rate,
            "avg_latency": float(avg_latency),
            "threshold": self.threshold,
            "capacity_utilization": len(self.current_contents) / self.capacity,
        }


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_self_awareness_engine: Optional[SelfAwarenessEngine] = None
_qualia_simulator: Optional[QualiaSimulator] = None
_global_workspace: Optional[GlobalWorkspace] = None
_metaconsciousness_system: Optional[MetaconsciousnessSystem] = None
_iit_engine: Optional[IntegratedInformationEngine] = None
_binding_system: Optional[PhenomenalBindingSystem] = None
_access_controller: Optional[ConsciousAccessController] = None

_lock = threading.Lock()


def get_self_awareness_engine(**kwargs) -> SelfAwarenessEngine:
    """Get or create singleton Self-Awareness Engine."""
    global _self_awareness_engine
    with _lock:
        if _self_awareness_engine is None:
            _self_awareness_engine = SelfAwarenessEngine(**kwargs)
        return _self_awareness_engine


def get_qualia_simulator(**kwargs) -> QualiaSimulator:
    """Get or create singleton Qualia Simulator."""
    global _qualia_simulator
    with _lock:
        if _qualia_simulator is None:
            _qualia_simulator = QualiaSimulator(**kwargs)
        return _qualia_simulator


def get_global_workspace(**kwargs) -> GlobalWorkspace:
    """Get or create singleton Global Workspace."""
    global _global_workspace
    with _lock:
        if _global_workspace is None:
            _global_workspace = GlobalWorkspace(**kwargs)
        return _global_workspace


def get_metaconsciousness_system(**kwargs) -> MetaconsciousnessSystem:
    """Get or create singleton Metaconsciousness System."""
    global _metaconsciousness_system
    with _lock:
        if _metaconsciousness_system is None:
            _metaconsciousness_system = MetaconsciousnessSystem(**kwargs)
        return _metaconsciousness_system


def get_iit_engine(**kwargs) -> IntegratedInformationEngine:
    """Get or create singleton IIT Engine."""
    global _iit_engine
    with _lock:
        if _iit_engine is None:
            _iit_engine = IntegratedInformationEngine(**kwargs)
        return _iit_engine


def get_binding_system(**kwargs) -> PhenomenalBindingSystem:
    """Get or create singleton Binding System."""
    global _binding_system
    with _lock:
        if _binding_system is None:
            _binding_system = PhenomenalBindingSystem(**kwargs)
        return _binding_system


def get_access_controller(**kwargs) -> ConsciousAccessController:
    """Get or create singleton Access Controller."""
    global _access_controller
    with _lock:
        if _access_controller is None:
            _access_controller = ConsciousAccessController(**kwargs)
        return _access_controller
