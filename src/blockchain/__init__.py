"""
Blockchain Module - v3.4

Immutable audit trail with blockchain technology.

Modules:
- blockchain_core: Block and chain management
- transaction_manager: Transaction handling and validation
- consensus: Proof of Authority consensus mechanism
- merkle_tree: Merkle tree for efficient verification
- audit_logger: Blockchain-based audit logging
- smart_contracts: Simple smart contract execution

Version: 3.4.0
"""

__version__ = '3.4.0'

from .blockchain_core import (
    Block,
    Blockchain,
    BlockValidator,
    GenesisBlock,
    get_blockchain
)

__all__ = [
    'Block',
    'Blockchain',
    'BlockValidator',
    'GenesisBlock',
    'get_blockchain',
]
