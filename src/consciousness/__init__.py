"""
Consciousness AI Module - v6.0.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 10-50x faster, full features, requires numpy

Computational models of consciousness based on leading neuroscientific
and philosophical theories.

IMPORTANT DISCLAIMER:
This module simulates consciousness-like computational properties.
It does NOT create genuine phenomenal consciousness or subjective experience.

Version: 6.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "6.0.0"

# ALWAYS import Pure Python version (baseline, always available)
from .consciousness_services import (
    # Enums
    SelfAspect,
    QualiaType,
    
    # Dataclasses
    SelfModel,
    IntrospectionQuery,
    IntrospectionResult,
    Quale,
    PhenomenalExperience,
    ConsciousContent,
    BroadcastEvent,
    HigherOrderThought,
    ReflectiveState,
    PhiCalculation,
    CausalStructure,
    BindingRequest,
    BoundExperience,
    AccessRequest,
    AccessDecision,
    
    # Classes (Pure Python - simplified)
    SelfAwarenessEngine as SelfAwarenessEnginePython,
    QualiaSimulator as QualiaSimulatorPython,
    GlobalWorkspace as GlobalWorkspacePython,
    MetaconsciousnessSystem as MetaconsciousnessSystemPython,
    IntegratedInformationEngine as IntegratedInformationEnginePython,
    PhenomenalBindingSystem as PhenomenalBindingSystemPython,
    ConsciousAccessController as ConsciousAccessControllerPython,
    
    # Singletons (Pure Python)
    get_self_awareness_engine as get_self_awareness_engine_python,
    get_qualia_simulator as get_qualia_simulator_python,
    get_global_workspace as get_global_workspace_python,
    get_metaconsciousness_system as get_metaconsciousness_system_python,
    get_iit_engine as get_iit_engine_python,
    get_binding_system as get_binding_system_python,
    get_access_controller as get_access_controller_python,
)

# TRY to import NumPy version (optional, faster, full features)
try:
    from .consciousness_services_numpy import (
        # Classes (NumPy version - full features)
        SelfAwarenessEngine as SelfAwarenessEngineNumpy,
        QualiaSimulator as QualiaSimulatorNumpy,
        GlobalWorkspace as GlobalWorkspaceNumpy,
        MetaconsciousnessSystem as MetaconsciousnessSystemNumpy,
        IntegratedInformationEngine as IntegratedInformationEngineNumpy,
        PhenomenalBindingSystem as PhenomenalBindingSystemNumpy,
        ConsciousAccessController as ConsciousAccessControllerNumpy,
        
        # Singletons (NumPy version)
        get_self_awareness_engine as get_self_awareness_engine_numpy,
        get_qualia_simulator as get_qualia_simulator_numpy,
        get_global_workspace as get_global_workspace_numpy,
        get_metaconsciousness_system as get_metaconsciousness_system_numpy,
        get_iit_engine as get_iit_engine_numpy,
        get_binding_system as get_binding_system_numpy,
        get_access_controller as get_access_controller_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (10-50x faster, full features)
    SelfAwarenessEngine = SelfAwarenessEngineNumpy
    QualiaSimulator = QualiaSimulatorNumpy
    GlobalWorkspace = GlobalWorkspaceNumpy
    MetaconsciousnessSystem = MetaconsciousnessSystemNumpy
    IntegratedInformationEngine = IntegratedInformationEngineNumpy
    PhenomenalBindingSystem = PhenomenalBindingSystemNumpy
    ConsciousAccessController = ConsciousAccessControllerNumpy
    
    # Use NumPy getters
    get_self_awareness_engine = get_self_awareness_engine_numpy
    get_qualia_simulator = get_qualia_simulator_numpy
    get_global_workspace = get_global_workspace_numpy
    get_metaconsciousness_system = get_metaconsciousness_system_numpy
    get_iit_engine = get_iit_engine_numpy
    get_binding_system = get_binding_system_numpy
    get_access_controller = get_access_controller_numpy
else:
    # NumPy not available - use Pure Python (simplified)
    SelfAwarenessEngine = SelfAwarenessEnginePython
    QualiaSimulator = QualiaSimulatorPython
    GlobalWorkspace = GlobalWorkspacePython
    MetaconsciousnessSystem = MetaconsciousnessSystemPython
    IntegratedInformationEngine = IntegratedInformationEnginePython
    PhenomenalBindingSystem = PhenomenalBindingSystemPython
    ConsciousAccessController = ConsciousAccessControllerPython
    
    # Use Pure Python getters
    get_self_awareness_engine = get_self_awareness_engine_python
    get_qualia_simulator = get_qualia_simulator_python
    get_global_workspace = get_global_workspace_python
    get_metaconsciousness_system = get_metaconsciousness_system_python
    get_iit_engine = get_iit_engine_python
    get_binding_system = get_binding_system_python
    get_access_controller = get_access_controller_python

__all__ = [
    # Version
    "__version__",
    
    # Enums
    "SelfAspect",
    "QualiaType",
    
    # Dataclasses
    "SelfModel",
    "IntrospectionQuery",
    "IntrospectionResult",
    "Quale",
    "PhenomenalExperience",
    "ConsciousContent",
    "BroadcastEvent",
    "HigherOrderThought",
    "ReflectiveState",
    "PhiCalculation",
    "CausalStructure",
    "BindingRequest",
    "BoundExperience",
    "AccessRequest",
    "AccessDecision",
    
    # Core Systems (auto-select best version)
    "SelfAwarenessEngine",
    "QualiaSimulator",
    "GlobalWorkspace",
    "MetaconsciousnessSystem",
    "IntegratedInformationEngine",
    "PhenomenalBindingSystem",
    "ConsciousAccessController",
    
    # Pure Python versions (always available)
    "SelfAwarenessEnginePython",
    "QualiaSimulatorPython",
    "GlobalWorkspacePython",
    "MetaconsciousnessSystemPython",
    "IntegratedInformationEnginePython",
    "PhenomenalBindingSystemPython",
    "ConsciousAccessControllerPython",
    
    # Singletons
    "get_self_awareness_engine",
    "get_qualia_simulator",
    "get_global_workspace",
    "get_metaconsciousness_system",
    "get_iit_engine",
    "get_binding_system",
    "get_access_controller",
    
    # Pure Python singleton getters
    "get_self_awareness_engine_python",
    "get_qualia_simulator_python",
    "get_global_workspace_python",
    "get_metaconsciousness_system_python",
    "get_iit_engine_python",
    "get_binding_system_python",
    "get_access_controller_python",
    
    # Dual-version flag
    "HAS_NUMPY",
]
