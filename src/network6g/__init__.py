"""
6G Network Optimization Module - v4.2

Next-generation 6G network capabilities with terahertz communication,
intelligent reflecting surfaces, and AI-driven optimization.

Modules:
- network6g_services: Complete 6G network implementation

Components:
- 6G Network Manager: Network resource allocation and orchestration
- Terahertz Communication: Ultra-high bandwidth THz communication
- Intelligent Reflecting Surfaces: Programmable radio environment
- Network Slicing 2.0: Dynamic virtual network creation
- Edge Intelligence: Distributed AI at network edge
- Holographic Communications: 3D hologram transmission
- Quantum-Secured 6G: Quantum-safe network security

Version: 4.2.0
"""

__version__ = "4.2.0"

from .network6g_services import (  # 6G Network Manager; Terahertz Communication; Intelligent Reflecting Surfaces; Network Slicing 2.0; Edge Intelligence; Holographic Communications; Quantum-Secured 6G
    AtmosphericModel,
    BeamformingController,
    ChannelEstimator,
    ContentCache,
    ContextManager,
    DynamicScaling,
    EdgeAI,
    EdgeNode,
    EntanglementManager,
    FederatedLearner,
    HologramEngine,
    HologramQuality,
    HolographicRenderer,
    IRSSurface,
    LinkBudget,
    MultiSensoryStream,
    MultiUserOptimizer,
    NetworkDigitalTwin,
    NetworkManager,
    NetworkSlice,
    OptimizationMethod,
    PhaseController,
    PresenceManager,
    QKDProtocol,
    QoSProfile,
    QuantumAuthenticator,
    QuantumKeyDistributor,
    QuantumRNG,
    ResourceAllocator,
    RoutingOptimizer,
    SecureChannel,
    SLAMonitor,
    SliceComposer,
    SliceOrchestrator,
    SliceTemplate,
    SliceType,
    SpectrumAnalyzer,
    TactileInternet,
    THzChannel,
    THzTransceiver,
    get_edge_intelligence,
    get_hologram_engine,
    get_irs_surface,
    get_network_manager,
    get_quantum_security,
    get_slice_orchestrator,
    get_thz_transceiver,
)

__all__ = [
    # 6G Network Manager
    "NetworkSlice",
    "SliceType",
    "QoSProfile",
    "NetworkManager",
    "ResourceAllocator",
    "NetworkDigitalTwin",
    "get_network_manager",
    # Terahertz Communication
    "THzChannel",
    "THzTransceiver",
    "BeamformingController",
    "AtmosphericModel",
    "SpectrumAnalyzer",
    "LinkBudget",
    "get_thz_transceiver",
    # Intelligent Reflecting Surfaces
    "IRSSurface",
    "PhaseController",
    "MultiUserOptimizer",
    "ChannelEstimator",
    "OptimizationMethod",
    "get_irs_surface",
    # Network Slicing 2.0
    "SliceTemplate",
    "SliceOrchestrator",
    "SLAMonitor",
    "DynamicScaling",
    "SliceComposer",
    "get_slice_orchestrator",
    # Edge Intelligence
    "EdgeNode",
    "EdgeAI",
    "FederatedLearner",
    "ContentCache",
    "RoutingOptimizer",
    "ContextManager",
    "get_edge_intelligence",
    # Holographic Communications
    "HologramEngine",
    "MultiSensoryStream",
    "HolographicRenderer",
    "TactileInternet",
    "PresenceManager",
    "HologramQuality",
    "get_hologram_engine",
    # Quantum-Secured 6G
    "QuantumKeyDistributor",
    "QKDProtocol",
    "QuantumAuthenticator",
    "EntanglementManager",
    "QuantumRNG",
    "SecureChannel",
    "get_quantum_security",
]
