"""
🧠 Consciousness Simulation Platform

Provides computational models of consciousness based on leading neuroscientific
and philosophical theories, including Global Workspace Theory, Integrated Information
Theory, Higher-Order Thought Theory, and phenomenal binding mechanisms.

IMPORTANT: This module simulates consciousness-like computational properties.
It does NOT create genuine phenomenal consciousness or subjective experience.
The philosophical "hard problem" of consciousness remains unsolved. This is a
functional simulation for research and advanced AI capabilities.

Version: 6.0.0
"""

__version__ = "6.0.0"

from .consciousness_services import (  # Self-Awareness Engine; Qualia Simulator; Global Workspace (Attention Consciousness); Metaconsciousness System; Integrated Information Engine (IIT); Phenomenal Binding System; Conscious Access Controller
    AccessDecision,
    AccessRequest,
    BindingRequest,
    BoundExperience,
    BroadcastEvent,
    CausalStructure,
    ConsciousAccessController,
    ConsciousContent,
    GlobalWorkspace,
    HigherOrderThought,
    IntegratedInformationEngine,
    IntrospectionQuery,
    IntrospectionResult,
    MetaconsciousnessSystem,
    PhenomenalBindingSystem,
    PhenomenalExperience,
    PhiCalculation,
    Quale,
    QualiaSimulator,
    QualiaType,
    ReflectiveState,
    SelfAspect,
    SelfAwarenessEngine,
    SelfModel,
    get_access_controller,
    get_binding_system,
    get_global_workspace,
    get_iit_engine,
    get_metaconsciousness_system,
    get_qualia_simulator,
    get_self_awareness_engine,
)

__all__ = [
    # Self-Awareness Engine
    "SelfAspect",
    "SelfModel",
    "IntrospectionQuery",
    "IntrospectionResult",
    "SelfAwarenessEngine",
    "get_self_awareness_engine",
    # Qualia Simulator
    "QualiaType",
    "Quale",
    "PhenomenalExperience",
    "QualiaSimulator",
    "get_qualia_simulator",
    # Global Workspace
    "ConsciousContent",
    "BroadcastEvent",
    "GlobalWorkspace",
    "get_global_workspace",
    # Metaconsciousness System
    "HigherOrderThought",
    "ReflectiveState",
    "MetaconsciousnessSystem",
    "get_metaconsciousness_system",
    # Integrated Information Engine
    "PhiCalculation",
    "CausalStructure",
    "IntegratedInformationEngine",
    "get_iit_engine",
    # Phenomenal Binding System
    "BindingRequest",
    "BoundExperience",
    "PhenomenalBindingSystem",
    "get_binding_system",
    # Conscious Access Controller
    "AccessRequest",
    "AccessDecision",
    "ConsciousAccessController",
    "get_access_controller",
]
