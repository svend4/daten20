"""
Security Module - v3.4

Advanced security features for document management.

Modules:
- digital_signatures: X.509 certificates, RSA/ECDSA signatures, PDF signing
- zero_knowledge: zk-SNARKs, range proofs, selective disclosure
- threat_detection: AI-powered threat detection, IDS, DDoS protection

Version: 3.4.0
"""

__version__ = '3.4.0'

from .digital_signatures import (
    DigitalSigner,
    SignatureValidator,
    CertificateAuthority,
    KeyGenerator,
    PDFSigner,
    MultiSignatureManager,
    X509Certificate,
    DigitalSignature,
    SignatureAlgorithm,
    SignatureLevel,
    RevocationStatus
)

from .zero_knowledge import (
    ZKSNARKProver,
    ZKSNARKVerifier,
    RangeProofSystem,
    SelectiveDisclosureProver,
    VerifiableCredentialIssuer,
    HashCommitment,
    PedersenCommitment,
    Proof,
    RangeProof,
    SelectiveDisclosure,
    VerifiableCredential,
    ProofSystem
)

from .threat_detection import (
    SIEM,
    AnomalyDetector,
    BruteForceDetector,
    InjectionDetector,
    DDoSProtection,
    BotDetector,
    ThreatIntelligence,
    ThreatAlert,
    SecurityEvent,
    ThreatLevel,
    ThreatType,
    IPReputation
)

__all__ = [
    # Digital Signatures
    'DigitalSigner',
    'SignatureValidator',
    'CertificateAuthority',
    'KeyGenerator',
    'PDFSigner',
    'MultiSignatureManager',
    'X509Certificate',
    'DigitalSignature',
    'SignatureAlgorithm',
    'SignatureLevel',
    'RevocationStatus',
    # Zero-Knowledge Proofs
    'ZKSNARKProver',
    'ZKSNARKVerifier',
    'RangeProofSystem',
    'SelectiveDisclosureProver',
    'VerifiableCredentialIssuer',
    'HashCommitment',
    'PedersenCommitment',
    'Proof',
    'RangeProof',
    'SelectiveDisclosure',
    'VerifiableCredential',
    'ProofSystem',
    # Threat Detection
    'SIEM',
    'AnomalyDetector',
    'BruteForceDetector',
    'InjectionDetector',
    'DDoSProtection',
    'BotDetector',
    'ThreatIntelligence',
    'ThreatAlert',
    'SecurityEvent',
    'ThreatLevel',
    'ThreatType',
    'IPReputation',
]
