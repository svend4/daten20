"""
Next-Generation Platform - v4.0

Future-ready architecture with serverless, multi-cloud, quantum crypto,
edge AI, voice interfaces, and AR/VR/metaverse.

Modules:
- nextgen_services: Next-generation platform services

Components:
- Serverless Platform: Function-as-a-Service with auto-scaling
- Multi-Cloud Manager: Cloud-agnostic deployment across AWS, Azure, GCP
- Quantum Cryptography: Post-quantum algorithms and hybrid encryption
- Edge AI Platform: AI inference at the edge with federated learning
- Voice Interface: Voice commands and conversational AI
- AR/VR Metaverse: Virtual spaces and augmented reality

Version: 4.0.0
"""

__version__ = "4.0.0"

from .nextgen_services import (  # Serverless Platform; Multi-Cloud; Quantum Cryptography; Edge AI; Voice Interface; AR/VR Metaverse
    CloudProvider,
    CloudResource,
    EdgeAI,
    EdgeAIModel,
    FunctionRuntime,
    MetaversePlatform,
    MultiCloudPlatform,
    QuantumAlgorithm,
    QuantumCrypto,
    ServerlessFunction,
    ServerlessPlatform,
    TriggerType,
    VoiceCommand,
    VoiceInterface,
    VRSpaceType,
    get_edge_ai,
    get_metaverse_platform,
    get_multicloud_platform,
    get_quantum_crypto,
    get_serverless_platform,
    get_voice_interface,
)

__all__ = [
    # Serverless Platform
    "ServerlessFunction",
    "FunctionRuntime",
    "TriggerType",
    "ServerlessPlatform",
    "get_serverless_platform",
    # Multi-Cloud
    "CloudProvider",
    "CloudResource",
    "MultiCloudPlatform",
    "get_multicloud_platform",
    # Quantum Cryptography
    "QuantumAlgorithm",
    "QuantumCrypto",
    "get_quantum_crypto",
    # Edge AI
    "EdgeAIModel",
    "EdgeAI",
    "get_edge_ai",
    # Voice Interface
    "VoiceCommand",
    "VoiceInterface",
    "get_voice_interface",
    # AR/VR Metaverse
    "VRSpaceType",
    "MetaversePlatform",
    "get_metaverse_platform",
]
