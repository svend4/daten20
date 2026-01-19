"""
Blockchain Module - v3.4

Immutable audit trail with blockchain technology.

Modules:
- blockchain_core: Block and chain management
- document_registry: Blockchain document registry with multi-chain support
- transaction_manager: Transaction handling and validation
- consensus: Proof of Authority consensus mechanism
- merkle_tree: Merkle tree for efficient verification
- audit_logger: Blockchain-based audit logging
- smart_contracts: Simple smart contract execution

Version: 3.4.0
"""

__version__ = "3.4.0"

from .blockchain_core import Block, Blockchain, BlockValidator, GenesisBlock, get_blockchain
from .document_registry import (
    BlockchainDocumentRegistry,
    BlockchainNetwork,
    BlockchainTransaction,
    DocumentEventType,
    DocumentHash,
    DocumentHasher,
    DocumentRegistryEntry,
    ProofOfExistence,
    SmartContractInterface,
)

__all__ = [
    "Block",
    "Blockchain",
    "BlockValidator",
    "GenesisBlock",
    "get_blockchain",
    "BlockchainDocumentRegistry",
    "DocumentHasher",
    "SmartContractInterface",
    "DocumentHash",
    "BlockchainTransaction",
    "DocumentRegistryEntry",
    "ProofOfExistence",
    "BlockchainNetwork",
    "DocumentEventType",
]
