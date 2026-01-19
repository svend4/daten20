"""
Security Module - v3.4

Advanced security features for document management.

Modules:
- digital_signatures: X.509 certificates, RSA/ECDSA signatures, PDF signing
- zero_knowledge: zk-SNARKs, range proofs, selective disclosure
- threat_detection: AI-powered threat detection, IDS, DDoS protection

Version: 3.4.0
"""

__version__ = "3.4.0"

from .digital_signatures import (
    CertificateAuthority,
    DigitalSignature,
    DigitalSigner,
    KeyGenerator,
    MultiSignatureManager,
    PDFSigner,
    RevocationStatus,
    SignatureAlgorithm,
    SignatureLevel,
    SignatureValidator,
    X509Certificate,
)
from .threat_detection import (
    SIEM,
    AnomalyDetector,
    BotDetector,
    BruteForceDetector,
    DDoSProtection,
    InjectionDetector,
    IPReputation,
    SecurityEvent,
    ThreatAlert,
    ThreatIntelligence,
    ThreatLevel,
    ThreatType,
)
from .zero_knowledge import (
    HashCommitment,
    PedersenCommitment,
    Proof,
    ProofSystem,
    RangeProof,
    RangeProofSystem,
    SelectiveDisclosure,
    SelectiveDisclosureProver,
    VerifiableCredential,
    VerifiableCredentialIssuer,
    ZKSNARKProver,
    ZKSNARKVerifier,
)

__all__ = [
    # Digital Signatures
    "DigitalSigner",
    "SignatureValidator",
    "CertificateAuthority",
    "KeyGenerator",
    "PDFSigner",
    "MultiSignatureManager",
    "X509Certificate",
    "DigitalSignature",
    "SignatureAlgorithm",
    "SignatureLevel",
    "RevocationStatus",
    # Zero-Knowledge Proofs
    "ZKSNARKProver",
    "ZKSNARKVerifier",
    "RangeProofSystem",
    "SelectiveDisclosureProver",
    "VerifiableCredentialIssuer",
    "HashCommitment",
    "PedersenCommitment",
    "Proof",
    "RangeProof",
    "SelectiveDisclosure",
    "VerifiableCredential",
    "ProofSystem",
    # Threat Detection
    "SIEM",
    "AnomalyDetector",
    "BruteForceDetector",
    "InjectionDetector",
    "DDoSProtection",
    "BotDetector",
    "ThreatIntelligence",
    "ThreatAlert",
    "SecurityEvent",
    "ThreatLevel",
    "ThreatType",
    "IPReputation",
]
