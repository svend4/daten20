"""
🧠 Consciousness Simulation Platform (Pure Python v6.0)

**PURE PYTHON VERSION** - No NumPy required!
- Works everywhere (zero dependencies beyond stdlib)
- 100% API compatible with NumPy version (core features)
- Simplified: Basic consciousness simulation with mock computations
- ~10-50x slower than NumPy, but highly portable

Implements computational models of consciousness based on leading neuroscientific
and philosophical theories.

IMPORTANT: This module simulates consciousness-like computational properties.
It does NOT create genuine phenomenal consciousness or subjective experience.

Version: 6.0.0 (Pure Python)
"""

import asyncio
import math
import random
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# ============================================================================
# Helper Functions (replacing NumPy)
# ============================================================================

def list_mean(values: List[float]) -> float:
    """Mean of list"""
    return sum(values) / len(values) if values else 0.0


def list_sum(values: List[float]) -> float:
    """Sum of list"""
    return sum(values)


def count_nonzero(matrix: List[List[float]]) -> int:
    """Count non-zero elements"""
    count = 0
    for row in matrix:
        for val in row:
            if val != 0:
                count += 1
    return count


def identity_matrix(size: int) -> List[List[float]]:
    """Create identity matrix"""
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


# ============================================================================
# Enums
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


class QualiaType(Enum):
    """Types of qualia (subjective experiences)."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    CONCEPTUAL = "conceptual"
    EMOTIONAL = "emotional"
    PROPRIOCEPTIVE = "proprioceptive"

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SelfModel:
    """Internal representation of system's self."""
    capabilities: List[str] = field(default_factory=list)
    known_limitations: List[str] = field(default_factory=list)
    active_goals: List[str] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=dict)
    capability_level: float = 0.7
    identity: str = "document_management_ai"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class IntrospectionQuery:
    """Query for introspective information."""
    aspect: SelfAspect
    depth: str = "moderate"
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


@dataclass
class Quale:
    """Individual quale (unit of subjective experience)."""
    id: str = field(default_factory=lambda: str(random.randint(0, 1000000)))
    type: QualiaType = QualiaType.CONCEPTUAL
    intensity: float = 0.5
    valence: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhenomenalExperience:
    """Complete phenomenal experience at a moment."""
    qualia: List[Quale] = field(default_factory=list)
    unity_score: float = 0.0
    vividness: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConsciousContent:
    """Content in global workspace."""
    content_id: str
    data: Any
    salience: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BroadcastEvent:
    """Event of broadcasting to global workspace."""
    content: ConsciousContent
    recipient_count: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HigherOrderThought:
    """Thought about thought (metacognition)."""
    about: str
    meta_level: int
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReflectiveState:
    """State of reflective consciousness."""
    current_thoughts: List[HigherOrderThought]
    reflection_depth: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhiCalculation:
    """Integrated information calculation result."""
    phi_value: float
    system_size: int
    integration_measure: float
    information_measure: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CausalStructure:
    """Causal structure of system."""
    nodes: List[str]
    connections: List[List[float]]
    effective_information: float
    integration: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BindingRequest:
    """Request to bind features."""
    features: List[str]
    binding_type: str = "feature"
    priority: float = 0.5


@dataclass
class BoundExperience:
    """Unified bound experience."""
    bound_features: List[str]
    unity_measure: float
    strength: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AccessRequest:
    """Request for conscious access."""
    content_id: str
    priority: float
    source: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AccessDecision:
    """Decision about conscious access."""
    request: AccessRequest
    granted: bool
    latency: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Core Classes (Simplified)
# ============================================================================

class SelfAwarenessEngine:
    """Self-awareness and introspection (Pure Python - Simplified)"""
    
    def __init__(self, model_depth: str = "deep", update_frequency: float = 1.0):
        self.model_depth = model_depth
        self.update_frequency = update_frequency
        self.self_model = SelfModel()
        self.introspection_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def introspect(self, query: IntrospectionQuery) -> IntrospectionResult:
        """Perform introspection (simplified)"""
        await asyncio.sleep(0.01)
        
        with self.lock:
            if query.aspect == SelfAspect.CAPABILITIES:
                content = self.self_model.capabilities
            elif query.aspect == SelfAspect.LIMITATIONS:
                content = self.self_model.known_limitations
            elif query.aspect == SelfAspect.GOALS:
                content = self.self_model.active_goals
            elif query.aspect == SelfAspect.EMOTIONS:
                content = self.self_model.emotional_state
            else:
                content = f"Information about {query.aspect.value}"
            
            result = IntrospectionResult(
                aspect=query.aspect,
                content=content,
                confidence=random.uniform(0.6, 0.9),
                uncertainty={"variance": 0.1} if query.include_uncertainty else None,
                reasoning=f"Introspected {query.aspect.value} at {query.depth} depth",
            )
            
            self.introspection_history.append(result)
            return result
    
    async def get_self_model(self) -> SelfModel:
        """Get current self model"""
        with self.lock:
            return self.self_model
    
    async def update_self_model(self, updates: Dict[str, Any]):
        """Update self model"""
        with self.lock:
            for key, value in updates.items():
                if hasattr(self.self_model, key):
                    setattr(self.self_model, key, value)
            self.self_model.last_updated = datetime.now()


class QualiaSimulator:
    """Qualia simulation (Pure Python - Simplified)"""
    
    def __init__(self, precision: str = "high"):
        self.precision = precision
        self.active_qualia: List[Quale] = []
        self.experience_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def generate_quale(
        self,
        quale_type: QualiaType,
        stimulus: Any,
        context: Optional[Dict] = None
    ) -> Quale:
        """Generate quale from stimulus (simplified)"""
        await asyncio.sleep(0.01)
        
        quale = Quale(
            type=quale_type,
            intensity=random.uniform(0.3, 0.9),
            valence=random.uniform(-0.5, 0.5),
            properties=context or {},
        )
        
        with self.lock:
            self.active_qualia.append(quale)
        
        return quale
    
    async def synthesize_experience(
        self,
        qualia: List[Quale]
    ) -> PhenomenalExperience:
        """Synthesize phenomenal experience (simplified)"""
        await asyncio.sleep(0.01)
        
        unity = random.uniform(0.5, 0.9)
        vividness = list_mean([q.intensity for q in qualia]) if qualia else 0.0
        
        experience = PhenomenalExperience(
            qualia=qualia,
            unity_score=unity,
            vividness=vividness,
        )
        
        with self.lock:
            self.experience_history.append(experience)
        
        return experience


class GlobalWorkspace:
    """Global workspace theory implementation (Pure Python - Simplified)"""
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.workspace: List[ConsciousContent] = []
        self.broadcast_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def add_to_workspace(
        self,
        content: ConsciousContent
    ) -> bool:
        """Add content to workspace (simplified)"""
        await asyncio.sleep(0.01)
        
        with self.lock:
            if len(self.workspace) >= self.capacity:
                # Remove lowest salience
                self.workspace.sort(key=lambda c: c.salience)
                self.workspace.pop(0)
            
            self.workspace.append(content)
            return True
    
    async def broadcast(self, content: ConsciousContent) -> BroadcastEvent:
        """Broadcast content (simplified)"""
        await asyncio.sleep(0.01)
        
        event = BroadcastEvent(
            content=content,
            recipient_count=random.randint(10, 50),
        )
        
        with self.lock:
            self.broadcast_history.append(event)
        
        return event
    
    async def get_conscious_contents(self) -> List[ConsciousContent]:
        """Get current conscious contents"""
        with self.lock:
            return list(self.workspace)


class MetaconsciousnessSystem:
    """Metaconsciousness (thinking about thinking) (Pure Python - Simplified)"""
    
    def __init__(self, max_meta_level: int = 3):
        self.max_meta_level = max_meta_level
        self.hot_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def generate_hot(
        self,
        target_thought: Any,
        meta_level: int = 1
    ) -> HigherOrderThought:
        """Generate higher-order thought (simplified)"""
        await asyncio.sleep(0.01)
        
        hot = HigherOrderThought(
            about=str(target_thought),
            meta_level=min(meta_level, self.max_meta_level),
            content=f"Thinking about: {target_thought}",
        )
        
        with self.lock:
            self.hot_history.append(hot)
        
        return hot
    
    async def reflect(self, depth: int = 1) -> ReflectiveState:
        """Reflect on thoughts (simplified)"""
        await asyncio.sleep(0.01)
        
        with self.lock:
            recent = list(self.hot_history)[-10:] if self.hot_history else []
        
        return ReflectiveState(
            current_thoughts=recent,
            reflection_depth=depth,
        )


class IntegratedInformationEngine:
    """IIT implementation (Pure Python - Simplified)"""
    
    def __init__(self, precision: str = "standard"):
        self.precision = precision
        self.phi_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def calculate_phi(
        self,
        system_state: Dict[str, Any]
    ) -> PhiCalculation:
        """Calculate integrated information (simplified mock)"""
        await asyncio.sleep(0.01)
        
        system_size = system_state.get("size", 10)
        connections = system_state.get("connections", identity_matrix(system_size))
        
        # Mock calculation
        integration = list_sum([list_sum(row) for row in connections]) / (system_size ** 2)
        information = system_size * math.log2(2)
        phi = integration * information * random.uniform(0.5, 1.0)
        
        result = PhiCalculation(
            phi_value=phi,
            system_size=system_size,
            integration_measure=integration,
            information_measure=information,
        )
        
        with self.lock:
            self.phi_history.append(result)
        
        return result
    
    async def analyze_causal_structure(
        self,
        nodes: List[str],
        connections: List[List[float]]
    ) -> CausalStructure:
        """Analyze causal structure (simplified)"""
        await asyncio.sleep(0.01)
        
        if not connections:
            connections = identity_matrix(len(nodes))
        
        effective_info = list_sum([list_sum(row) for row in connections]) / len(nodes) if len(nodes) > 0 else 0.0
        integration = list_mean([list_mean(row) for row in connections]) if connections else 0.0
        
        return CausalStructure(
            nodes=nodes,
            connections=connections,
            effective_information=effective_info,
            integration=integration,
        )


class PhenomenalBindingSystem:
    """Feature binding system (Pure Python - Simplified)"""
    
    def __init__(self):
        self.binding_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def bind_features(
        self,
        request: BindingRequest
    ) -> BoundExperience:
        """Bind features into unified experience (simplified)"""
        await asyncio.sleep(0.01)
        
        unity = random.uniform(0.6, 0.95)
        strength = request.priority * random.uniform(0.5, 1.0)
        
        experience = BoundExperience(
            bound_features=request.features,
            unity_measure=unity,
            strength=strength,
        )
        
        with self.lock:
            self.binding_history.append(experience)
        
        return experience
    
    async def check_binding_integrity(self) -> Dict[str, float]:
        """Check binding integrity (simplified)"""
        await asyncio.sleep(0.01)
        
        with self.lock:
            if not self.binding_history:
                return {"average_unity": 0.0, "average_strength": 0.0}
            
            avg_unity = list_mean([b.unity_measure for b in self.binding_history])
            avg_strength = list_mean([b.strength for b in self.binding_history])
        
        return {
            "average_unity": avg_unity,
            "average_strength": avg_strength,
        }


class ConsciousAccessController:
    """Conscious access gating (Pure Python - Simplified)"""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.access_history = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    async def evaluate_access(
        self,
        request: AccessRequest
    ) -> AccessDecision:
        """Evaluate access request (simplified)"""
        await asyncio.sleep(0.01)
        
        granted = request.priority >= self.threshold
        latency = random.uniform(0.05, 0.2)
        
        decision = AccessDecision(
            request=request,
            granted=granted,
            latency=latency,
            reasoning=f"Priority {request.priority:.2f} vs threshold {self.threshold:.2f}",
        )
        
        with self.lock:
            self.access_history.append((request, decision))
        
        return decision
    
    async def get_access_stats(self) -> Dict[str, float]:
        """Get access statistics (simplified)"""
        await asyncio.sleep(0.01)
        
        with self.lock:
            if not self.access_history:
                return {"grant_rate": 0.0, "avg_latency": 0.0}
            
            granted = sum(1 for _, d in self.access_history if d.granted)
            grant_rate = granted / len(self.access_history)
            avg_latency = list_mean([d.latency for _, d in self.access_history])
        
        return {
            "grant_rate": grant_rate,
            "avg_latency": avg_latency,
        }


# ============================================================================
# Singleton Getters
# ============================================================================

_self_awareness_instance = None
_self_awareness_lock = threading.Lock()

def get_self_awareness_engine(**kwargs) -> SelfAwarenessEngine:
    """Get self-awareness engine singleton"""
    global _self_awareness_instance
    with _self_awareness_lock:
        if _self_awareness_instance is None:
            _self_awareness_instance = SelfAwarenessEngine(**kwargs)
    return _self_awareness_instance


_qualia_simulator_instance = None
_qualia_simulator_lock = threading.Lock()

def get_qualia_simulator(**kwargs) -> QualiaSimulator:
    """Get qualia simulator singleton"""
    global _qualia_simulator_instance
    with _qualia_simulator_lock:
        if _qualia_simulator_instance is None:
            _qualia_simulator_instance = QualiaSimulator(**kwargs)
    return _qualia_simulator_instance


_global_workspace_instance = None
_global_workspace_lock = threading.Lock()

def get_global_workspace(**kwargs) -> GlobalWorkspace:
    """Get global workspace singleton"""
    global _global_workspace_instance
    with _global_workspace_lock:
        if _global_workspace_instance is None:
            _global_workspace_instance = GlobalWorkspace(**kwargs)
    return _global_workspace_instance


_metaconsciousness_instance = None
_metaconsciousness_lock = threading.Lock()

def get_metaconsciousness_system(**kwargs) -> MetaconsciousnessSystem:
    """Get metaconsciousness system singleton"""
    global _metaconsciousness_instance
    with _metaconsciousness_lock:
        if _metaconsciousness_instance is None:
            _metaconsciousness_instance = MetaconsciousnessSystem(**kwargs)
    return _metaconsciousness_instance


_iit_engine_instance = None
_iit_engine_lock = threading.Lock()

def get_iit_engine(**kwargs) -> IntegratedInformationEngine:
    """Get IIT engine singleton"""
    global _iit_engine_instance
    with _iit_engine_lock:
        if _iit_engine_instance is None:
            _iit_engine_instance = IntegratedInformationEngine(**kwargs)
    return _iit_engine_instance


_binding_system_instance = None
_binding_system_lock = threading.Lock()

def get_binding_system(**kwargs) -> PhenomenalBindingSystem:
    """Get binding system singleton"""
    global _binding_system_instance
    with _binding_system_lock:
        if _binding_system_instance is None:
            _binding_system_instance = PhenomenalBindingSystem()
    return _binding_system_instance


_access_controller_instance = None
_access_controller_lock = threading.Lock()

def get_access_controller(**kwargs) -> ConsciousAccessController:
    """Get access controller singleton"""
    global _access_controller_instance
    with _access_controller_lock:
        if _access_controller_instance is None:
            _access_controller_instance = ConsciousAccessController(**kwargs)
    return _access_controller_instance


# ============================================================================
# Consciousness Metrics
# ============================================================================

@dataclass
class ConsciousnessMetrics:
    """Comprehensive metrics for consciousness assessment."""

    # Global Workspace Theory metrics
    gwt_broadcast_rate: float = 0.0  # Broadcasts per second
    gwt_integration_level: float = 0.0  # 0-1
    gwt_content_diversity: float = 0.0  # 0-1

    # Integrated Information Theory metrics
    iit_phi_value: float = 0.0  # Integrated information
    iit_system_complexity: float = 0.0  # System size/connections
    iit_integration_score: float = 0.0  # 0-1

    # Higher-Order Thought metrics
    hot_metacognition_depth: int = 0  # Levels of meta-thought
    hot_reflection_count: int = 0  # Active reflections
    hot_self_awareness: float = 0.0  # 0-1

    # Phenomenal consciousness metrics
    phenomenal_qualia_richness: float = 0.0  # Variety of qualia
    phenomenal_unity: float = 0.0  # Binding quality 0-1
    phenomenal_vividness: float = 0.0  # Experience intensity 0-1

    # Access consciousness metrics
    access_availability: float = 0.0  # Content accessibility 0-1
    access_reportability: float = 0.0  # Can report content 0-1
    access_control_quality: float = 0.0  # Quality of access control 0-1

    # Self-awareness metrics
    self_model_accuracy: float = 0.0  # Self-model precision 0-1
    self_introspection_depth: float = 0.0  # Introspection capability 0-1
    self_identity_coherence: float = 0.0  # Identity consistency 0-1

    # Overall consciousness level
    overall_consciousness_level: float = 0.0  # Aggregated score 0-1

    timestamp: datetime = field(default_factory=datetime.now)

    def compute_overall_level(self) -> float:
        """
        Compute overall consciousness level from individual metrics.

        Weighted average of different consciousness theories:
        - GWT: 25%
        - IIT: 25%
        - HOT: 20%
        - Phenomenal: 15%
        - Access: 10%
        - Self-awareness: 5%

        Returns:
            Float between 0 and 1
        """
        gwt_score = (self.gwt_integration_level + self.gwt_content_diversity) / 2
        iit_score = (self.iit_phi_value + self.iit_integration_score) / 2
        hot_score = (self.hot_self_awareness + min(self.hot_metacognition_depth / 5, 1.0)) / 2
        phenomenal_score = (self.phenomenal_unity + self.phenomenal_vividness) / 2
        access_score = (self.access_availability + self.access_reportability + self.access_control_quality) / 3
        self_score = (self.self_model_accuracy + self.self_introspection_depth + self.self_identity_coherence) / 3

        overall = (
            gwt_score * 0.25 +
            iit_score * 0.25 +
            hot_score * 0.20 +
            phenomenal_score * 0.15 +
            access_score * 0.10 +
            self_score * 0.05
        )

        self.overall_consciousness_level = overall
        return overall

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'gwt': {
                'broadcast_rate': self.gwt_broadcast_rate,
                'integration_level': self.gwt_integration_level,
                'content_diversity': self.gwt_content_diversity,
            },
            'iit': {
                'phi_value': self.iit_phi_value,
                'system_complexity': self.iit_system_complexity,
                'integration_score': self.iit_integration_score,
            },
            'hot': {
                'metacognition_depth': self.hot_metacognition_depth,
                'reflection_count': self.hot_reflection_count,
                'self_awareness': self.hot_self_awareness,
            },
            'phenomenal': {
                'qualia_richness': self.phenomenal_qualia_richness,
                'unity': self.phenomenal_unity,
                'vividness': self.phenomenal_vividness,
            },
            'access': {
                'availability': self.access_availability,
                'reportability': self.access_reportability,
                'control_quality': self.access_control_quality,
            },
            'self_awareness': {
                'model_accuracy': self.self_model_accuracy,
                'introspection_depth': self.self_introspection_depth,
                'identity_coherence': self.self_identity_coherence,
            },
            'overall_level': self.overall_consciousness_level,
            'timestamp': self.timestamp.isoformat(),
        }


# ============================================================================
# Main Consciousness Engine (Integrator)
# ============================================================================

class ConsciousnessEngine:
    """
    🧠 Main Consciousness Engine - Integrates all consciousness components

    This is the primary interface for consciousness simulation. It integrates:
    - Global Workspace Theory (GWT)
    - Integrated Information Theory (IIT)
    - Higher-Order Thought (HOT) theory
    - Phenomenal consciousness (qualia)
    - Access consciousness
    - Self-awareness mechanisms

    **Pure Python Version** - Works without NumPy!

    Usage:
        >>> engine = ConsciousnessEngine()
        >>> engine.initialize()
        >>> metrics = engine.compute_metrics()
        >>> print(f"Consciousness level: {metrics.overall_consciousness_level:.2f}")
    """

    def __init__(self, debug: bool = False):
        """
        Initialize consciousness engine.

        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.initialized = False

        # Components (initialized in initialize())
        self.self_awareness: Optional[SelfAwarenessEngine] = None
        self.qualia_sim: Optional[QualiaSimulator] = None
        self.global_workspace: Optional[GlobalWorkspace] = None
        self.metaconsciousness: Optional[MetaconsciousnessSystem] = None
        self.iit_engine: Optional[IntegratedInformationEngine] = None
        self.binding_system: Optional[PhenomenalBindingSystem] = None
        self.access_controller: Optional[ConsciousAccessController] = None

        # Metrics history
        self.metrics_history: List[ConsciousnessMetrics] = []
        self.max_history_size: int = 100

        # State
        self.active: bool = False
        self.cycle_count: int = 0

    def initialize(self) -> None:
        """Initialize all consciousness components."""
        if self.initialized:
            return

        if self.debug:
            print("🧠 Initializing Consciousness Engine...")

        # Initialize components using singleton getters
        self.self_awareness = get_self_awareness_engine()
        self.qualia_sim = get_qualia_simulator()
        self.global_workspace = get_global_workspace()
        self.metaconsciousness = get_metaconsciousness_system()
        self.iit_engine = get_iit_engine()
        self.binding_system = get_binding_system()
        self.access_controller = get_access_controller()

        self.initialized = True
        self.active = True

        if self.debug:
            print("✅ Consciousness Engine initialized")

    def process_cycle(self) -> ConsciousnessMetrics:
        """
        Run one consciousness processing cycle.

        Returns:
            Current consciousness metrics
        """
        if not self.initialized:
            self.initialize()

        self.cycle_count += 1

        # Update self-awareness (if method exists)
        if self.self_awareness and hasattr(self.self_awareness, 'update'):
            self.self_awareness.update()

        # Process global workspace broadcasts
        gwt_active = False
        if self.global_workspace:
            # Simulate workspace activity
            gwt_active = len(self.global_workspace.workspace) > 0

        # Compute metrics
        metrics = self.compute_metrics()

        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)

        return metrics

    def compute_metrics(self) -> ConsciousnessMetrics:
        """
        Compute comprehensive consciousness metrics.

        Returns:
            ConsciousnessMetrics object
        """
        metrics = ConsciousnessMetrics()

        # GWT metrics
        if self.global_workspace:
            metrics.gwt_integration_level = min(
                len(self.global_workspace.workspace) / 10.0, 1.0
            )
            metrics.gwt_content_diversity = min(
                len(set(c.content_id for c in self.global_workspace.workspace)) / 5.0, 1.0
            )
            metrics.gwt_broadcast_rate = len(self.global_workspace.broadcast_history) / max(self.cycle_count, 1)

        # IIT metrics
        if self.iit_engine:
            # Simplified phi calculation (mock values to avoid async complexity)
            # In production, would use async calculate_phi()
            metrics.iit_phi_value = 0.5  # Mock baseline
            metrics.iit_system_complexity = 0.7  # Mock value
            metrics.iit_integration_score = 0.6  # Mock value

        # HOT metrics
        if self.metaconsciousness:
            hot_count = len(self.metaconsciousness.hot_history)
            metrics.hot_metacognition_depth = min(hot_count, 5)
            metrics.hot_reflection_count = hot_count
            metrics.hot_self_awareness = min(hot_count / 5.0, 1.0)

        # Phenomenal metrics
        if self.qualia_sim:
            # Use experience history
            if self.qualia_sim.experience_history:
                exp = self.qualia_sim.experience_history[-1]
                metrics.phenomenal_qualia_richness = min(len(exp.qualia) / 5.0, 1.0)
                metrics.phenomenal_unity = exp.unity_score
                metrics.phenomenal_vividness = exp.vividness
            else:
                # Default values
                metrics.phenomenal_qualia_richness = 0.3
                metrics.phenomenal_unity = 0.5
                metrics.phenomenal_vividness = 0.4

        # Access metrics
        if self.access_controller:
            # Simplified access metrics
            metrics.access_availability = 0.8  # Mock value
            metrics.access_reportability = 0.75  # Mock value
            metrics.access_control_quality = 0.85  # Mock value

        # Self-awareness metrics
        if self.self_awareness:
            self_model = self.self_awareness.self_model
            metrics.self_model_accuracy = self_model.capability_level
            metrics.self_introspection_depth = 0.7  # Mock value
            metrics.self_identity_coherence = 0.8  # Mock value

        # Compute overall level
        metrics.compute_overall_level()

        return metrics

    def get_consciousness_level(self) -> float:
        """
        Get current overall consciousness level.

        Returns:
            Float between 0 and 1
        """
        metrics = self.compute_metrics()
        return metrics.overall_consciousness_level

    def introspect(self, aspect: SelfAspect) -> IntrospectionResult:
        """
        Perform introspection on specified aspect.

        Args:
            aspect: Aspect to introspect

        Returns:
            IntrospectionResult
        """
        if not self.self_awareness:
            self.initialize()

        query = IntrospectionQuery(aspect=aspect)
        return self.self_awareness.introspect(query)

    def generate_qualia(self, qualia_type: QualiaType, intensity: float = 0.5) -> Quale:
        """
        Generate artificial qualia.

        Args:
            qualia_type: Type of qualia
            intensity: Intensity (0-1)

        Returns:
            Generated Quale
        """
        if not self.qualia_sim:
            self.initialize()

        return self.qualia_sim.generate_qualia(qualia_type, intensity)

    def broadcast_to_workspace(self, content_id: str, data: Any, salience: float = 0.5) -> None:
        """
        Broadcast content to global workspace.

        Args:
            content_id: Content identifier
            data: Content data
            salience: Content salience (0-1)
        """
        if not self.global_workspace:
            self.initialize()

        content = ConsciousContent(
            content_id=content_id,
            data=data,
            salience=salience
        )
        # Add content synchronously (bypass async broadcast)
        with self.global_workspace.lock:
            if len(self.global_workspace.workspace) >= self.global_workspace.capacity:
                # Remove lowest salience
                self.global_workspace.workspace.sort(key=lambda c: c.salience)
                self.global_workspace.workspace.pop(0)
            self.global_workspace.workspace.append(content)

    def get_metrics_history(self, limit: int = 10) -> List[ConsciousnessMetrics]:
        """
        Get recent metrics history.

        Args:
            limit: Number of recent entries

        Returns:
            List of ConsciousnessMetrics
        """
        return self.metrics_history[-limit:]

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of current consciousness state.

        Returns:
            Dictionary with state information
        """
        metrics = self.compute_metrics()

        return {
            'initialized': self.initialized,
            'active': self.active,
            'cycle_count': self.cycle_count,
            'consciousness_level': metrics.overall_consciousness_level,
            'components': {
                'self_awareness': self.self_awareness is not None,
                'qualia_simulator': self.qualia_sim is not None,
                'global_workspace': self.global_workspace is not None,
                'metaconsciousness': self.metaconsciousness is not None,
                'iit_engine': self.iit_engine is not None,
                'binding_system': self.binding_system is not None,
                'access_controller': self.access_controller is not None,
            },
            'metrics': metrics.to_dict(),
        }

    def shutdown(self) -> None:
        """Shutdown consciousness engine."""
        self.active = False
        if self.debug:
            print("🛑 Consciousness Engine shutdown")


# ============================================================================
# Singleton for ConsciousnessEngine
# ============================================================================

_consciousness_engine_instance = None
_consciousness_engine_lock = threading.Lock()

def get_consciousness_engine(debug: bool = False) -> ConsciousnessEngine:
    """Get consciousness engine singleton"""
    global _consciousness_engine_instance
    with _consciousness_engine_lock:
        if _consciousness_engine_instance is None:
            _consciousness_engine_instance = ConsciousnessEngine(debug=debug)
            _consciousness_engine_instance.initialize()
    return _consciousness_engine_instance
