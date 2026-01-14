"""
Blockchain Module - v3.4

Immutable audit trail with blockchain technology.

Modules:
- blockchain_core: Block and chain management ✅
- document_registry: Blockchain document registry with multi-chain support ✅
- smart_contracts: Simple smart contract execution ✅
- consensus: Proof of Authority consensus mechanism ✅
- merkle_tree: Merkle tree for efficient verification ✅
- transaction_manager: Transaction handling and validation ✅
- audit_logger: Blockchain-based audit logging ✅

Version: 3.4.0 (Complete)
"""

__version__ = '3.4.0'

from .blockchain_core import (
    Block,
    Blockchain,
    BlockValidator,
    GenesisBlock,
    get_blockchain
)

from .document_registry import (
    BlockchainDocumentRegistry,
    DocumentHasher,
    SmartContractInterface,
    DocumentHash,
    BlockchainTransaction,
    DocumentRegistryEntry,
    ProofOfExistence,
    BlockchainNetwork,
    DocumentEventType
)

from .smart_contracts import (
    SmartContract,
    SmartContractEngine,
    ContractCondition,
    ContractAction,
    ContractType,
    ContractState,
    get_contract_engine
)

from .consensus import (
    ProofOfAuthority,
    Validator,
    ValidatorStatus,
    ConsensusRound,
    get_consensus
)

from .merkle_tree import (
    MerkleTree,
    MerkleNode,
    MerkleTreeBatch,
    get_batch_processor,
    create_document_merkle_tree,
    verify_document_in_tree
)

from .transaction_manager import (
    Transaction,
    TransactionManager,
    TransactionPool,
    TransactionType,
    TransactionStatus,
    get_transaction_manager
)

from .audit_logger import (
    AuditEvent,
    BlockchainAuditLogger,
    AuditEventType,
    get_audit_logger
)

__all__ = [
    # Blockchain Core
    'Block',
    'Blockchain',
    'BlockValidator',
    'GenesisBlock',
    'get_blockchain',

    # Document Registry
    'BlockchainDocumentRegistry',
    'DocumentHasher',
    'SmartContractInterface',
    'DocumentHash',
    'BlockchainTransaction',
    'DocumentRegistryEntry',
    'ProofOfExistence',
    'BlockchainNetwork',
    'DocumentEventType',

    # Smart Contracts
    'SmartContract',
    'SmartContractEngine',
    'ContractAction',
    'ContractCondition',
    'ContractType',
    'ContractState',
    'get_contract_engine',

    # Consensus
    'ProofOfAuthority',
    'Validator',
    'ValidatorStatus',
    'ConsensusRound',
    'get_consensus',

    # Merkle Tree
    'MerkleTree',
    'MerkleNode',
    'MerkleTreeBatch',
    'get_batch_processor',
    'create_document_merkle_tree',
    'verify_document_in_tree',

    # Transaction Manager
    'Transaction',
    'TransactionManager',
    'TransactionPool',
    'TransactionType',
    'TransactionStatus',
    'get_transaction_manager',

    # Audit Logger
    'AuditEvent',
    'BlockchainAuditLogger',
    'AuditEventType',
    'get_audit_logger',
]
