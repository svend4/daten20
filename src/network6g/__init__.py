"""
6G Network Optimization Services v4.2.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Mock 6G operations
- NumPy: Full network simulation

Version: 4.2.0
"""

__version__ = "4.2.0"

from .network6g_services import (
    SliceType,
    BeamformingType,
    NetworkSlice,
    IRSConfiguration,
    
    Network6GManager as Network6GManagerPython,
    TerahertzCommunication as TerahertzCommunicationPython,
    IntelligentReflectingSurface as IntelligentReflectingSurfacePython,
    EdgeIntelligence as EdgeIntelligencePython,
    HolographicCommunication as HolographicCommunicationPython,
    QuantumSecured6G as QuantumSecured6GPython,
    
    get_network6g_manager as get_network6g_manager_python,
    get_terahertz_communication as get_terahertz_communication_python,
    get_intelligent_reflecting_surface as get_intelligent_reflecting_surface_python,
    get_edge_intelligence as get_edge_intelligence_python,
    get_holographic_communication as get_holographic_communication_python,
    get_quantum_secured_6g as get_quantum_secured_6g_python,
)

try:
    from .network6g_services_numpy import (
        Network6GManager as Network6GManagerNumpy,
        TerahertzCommunication as TerahertzCommunicationNumpy,
        IntelligentReflectingSurface as IntelligentReflectingSurfaceNumpy,
        EdgeIntelligence as EdgeIntelligenceNumpy,
        HolographicCommunication as HolographicCommunicationNumpy,
        QuantumSecured6G as QuantumSecured6GNumpy,
        
        get_network6g_manager as get_network6g_manager_numpy,
        get_terahertz_communication as get_terahertz_communication_numpy,
        get_intelligent_reflecting_surface as get_intelligent_reflecting_surface_numpy,
        get_edge_intelligence as get_edge_intelligence_numpy,
        get_holographic_communication as get_holographic_communication_numpy,
        get_quantum_secured_6g as get_quantum_secured_6g_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if HAS_NUMPY:
    Network6GManager = Network6GManagerNumpy
    TerahertzCommunication = TerahertzCommunicationNumpy
    IntelligentReflectingSurface = IntelligentReflectingSurfaceNumpy
    EdgeIntelligence = EdgeIntelligenceNumpy
    HolographicCommunication = HolographicCommunicationNumpy
    QuantumSecured6G = QuantumSecured6GNumpy
    
    get_network6g_manager = get_network6g_manager_numpy
    get_terahertz_communication = get_terahertz_communication_numpy
    get_intelligent_reflecting_surface = get_intelligent_reflecting_surface_numpy
    get_edge_intelligence = get_edge_intelligence_numpy
    get_holographic_communication = get_holographic_communication_numpy
    get_quantum_secured_6g = get_quantum_secured_6g_numpy
else:
    Network6GManager = Network6GManagerPython
    TerahertzCommunication = TerahertzCommunicationPython
    IntelligentReflectingSurface = IntelligentReflectingSurfacePython
    EdgeIntelligence = EdgeIntelligencePython
    HolographicCommunication = HolographicCommunicationPython
    QuantumSecured6G = QuantumSecured6GPython
    
    get_network6g_manager = get_network6g_manager_python
    get_terahertz_communication = get_terahertz_communication_python
    get_intelligent_reflecting_surface = get_intelligent_reflecting_surface_python
    get_edge_intelligence = get_edge_intelligence_python
    get_holographic_communication = get_holographic_communication_python
    get_quantum_secured_6g = get_quantum_secured_6g_python

__all__ = [
    "__version__", "SliceType", "BeamformingType", "NetworkSlice", "IRSConfiguration",
    "Network6GManager", "TerahertzCommunication", "IntelligentReflectingSurface",
    "EdgeIntelligence", "HolographicCommunication", "QuantumSecured6G",
    "get_network6g_manager", "get_terahertz_communication", "get_intelligent_reflecting_surface",
    "get_edge_intelligence", "get_holographic_communication", "get_quantum_secured_6g",
    "HAS_NUMPY",
]
