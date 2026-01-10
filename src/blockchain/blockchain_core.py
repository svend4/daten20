#!/usr/bin/env python3
"""
Blockchain Core Module

Core blockchain implementation with blocks, chain validation,
and immutable audit trail.

Key Features:
- Block structure with hash chaining
- SHA-256 cryptographic hashing
- Chain validation and integrity checks
- Genesis block initialization
- Transaction storage and retrieval
- Fork resolution
- State snapshots

Dependencies:
- hashlib for SHA-256
- json for serialization
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4
import hashlib
import json
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Blockchain transaction"""
    tx_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    tx_type: str = "audit"  # audit, document, access, config
    sender: str = "system"
    data: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "tx_id": self.tx_id,
            "timestamp": self.timestamp.isoformat(),
            "tx_type": self.tx_type,
            "sender": self.sender,
            "data": self.data,
            "signature": self.signature,
            "metadata": self.metadata
        }

    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()


@dataclass
class Block:
    """Blockchain block"""
    index: int
    timestamp: datetime
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: Optional[str] = None
    merkle_root: Optional[str] = None
    validator: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate hash and merkle root after initialization"""
        if self.merkle_root is None:
            self.merkle_root = self._calculate_merkle_root()
        if self.hash is None:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "transactions": [tx.calculate_hash() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root,
            "validator": self.validator
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def _calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions"""
        if not self.transactions:
            return hashlib.sha256(b"").hexdigest()

        # Get transaction hashes
        tx_hashes = [tx.calculate_hash() for tx in self.transactions]

        # Build Merkle tree
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])  # Duplicate last hash if odd

            next_level = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                hash_value = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(hash_value)

            tx_hashes = next_level

        return tx_hashes[0]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "merkle_root": self.merkle_root,
            "validator": self.validator,
            "metadata": self.metadata
        }


class GenesisBlock:
    """Genesis block factory"""

    @staticmethod
    def create() -> Block:
        """Create genesis block"""
        genesis_tx = Transaction(
            tx_id="genesis",
            tx_type="genesis",
            sender="system",
            data={"message": "Genesis Block - Daten Blockchain v3.4"}
        )

        return Block(
            index=0,
            timestamp=datetime.now(),
            transactions=[genesis_tx],
            previous_hash="0" * 64,
            validator="genesis"
        )


class BlockValidator:
    """Block validation rules"""

    @staticmethod
    def validate_block(block: Block, previous_block: Optional[Block] = None) -> bool:
        """
        Validate block

        Args:
            block: Block to validate
            previous_block: Previous block in chain

        Returns:
            True if valid
        """
        # Validate hash
        if block.hash != block.calculate_hash():
            logger.error(f"Block {block.index}: Invalid hash")
            return False

        # Validate merkle root
        if block.merkle_root != block._calculate_merkle_root():
            logger.error(f"Block {block.index}: Invalid Merkle root")
            return False

        # Validate against previous block
        if previous_block:
            if block.index != previous_block.index + 1:
                logger.error(f"Block {block.index}: Invalid index")
                return False

            if block.previous_hash != previous_block.hash:
                logger.error(f"Block {block.index}: Invalid previous hash")
                return False

            if block.timestamp < previous_block.timestamp:
                logger.error(f"Block {block.index}: Timestamp before previous block")
                return False

        # Validate transactions
        for tx in block.transactions:
            if not BlockValidator.validate_transaction(tx):
                return False

        return True

    @staticmethod
    def validate_transaction(transaction: Transaction) -> bool:
        """Validate transaction"""
        # Basic validation
        if not transaction.tx_id:
            return False
        if not transaction.tx_type:
            return False
        if not transaction.sender:
            return False

        # Signature validation would go here
        # For now, simplified version

        return True

    @staticmethod
    def validate_chain(chain: List[Block]) -> bool:
        """Validate entire chain"""
        if not chain:
            return False

        # Validate genesis block
        if chain[0].index != 0:
            return False

        # Validate each block
        for i in range(1, len(chain)):
            if not BlockValidator.validate_block(chain[i], chain[i - 1]):
                return False

        return True


class Blockchain:
    """
    Blockchain implementation

    Maintains chain of blocks with cryptographic linking.
    """

    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self._lock = threading.Lock()
        self._transaction_index: Dict[str, Tuple[int, int]] = {}  # tx_id -> (block_index, tx_index)

        # Initialize with genesis block
        self._initialize_genesis()

    def _initialize_genesis(self):
        """Initialize blockchain with genesis block"""
        genesis = GenesisBlock.create()
        self.chain.append(genesis)
        self._index_block(genesis)
        logger.info("Blockchain initialized with genesis block")

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add transaction to pending pool

        Args:
            transaction: Transaction to add

        Returns:
            True if added successfully
        """
        with self._lock:
            if not BlockValidator.validate_transaction(transaction):
                logger.error(f"Invalid transaction: {transaction.tx_id}")
                return False

            self.pending_transactions.append(transaction)
            logger.debug(f"Transaction added: {transaction.tx_id}")
            return True

    def mine_block(self, validator: str = "system") -> Block:
        """
        Mine new block with pending transactions

        Args:
            validator: Validator address

        Returns:
            Newly mined block
        """
        with self._lock:
            if not self.pending_transactions:
                raise ValueError("No pending transactions to mine")

            previous_block = self.chain[-1]

            new_block = Block(
                index=len(self.chain),
                timestamp=datetime.now(),
                transactions=self.pending_transactions.copy(),
                previous_hash=previous_block.hash,
                validator=validator
            )

            # Validate block
            if not BlockValidator.validate_block(new_block, previous_block):
                raise ValueError("Block validation failed")

            self.chain.append(new_block)
            self._index_block(new_block)

            # Clear pending transactions
            self.pending_transactions = []

            logger.info(f"Block {new_block.index} mined with {len(new_block.transactions)} transactions")
            return new_block

    def _index_block(self, block: Block):
        """Index transactions in block for fast lookup"""
        for tx_idx, tx in enumerate(block.transactions):
            self._transaction_index[tx.tx_id] = (block.index, tx_idx)

    def get_block(self, index: int) -> Optional[Block]:
        """Get block by index"""
        with self._lock:
            if 0 <= index < len(self.chain):
                return self.chain[index]
        return None

    def get_latest_block(self) -> Block:
        """Get latest block"""
        with self._lock:
            return self.chain[-1]

    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        with self._lock:
            location = self._transaction_index.get(tx_id)
            if location:
                block_idx, tx_idx = location
                return self.chain[block_idx].transactions[tx_idx]
        return None

    def get_audit_trail(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        from_block: int = 0
    ) -> List[Transaction]:
        """
        Get audit trail for entity

        Args:
            entity_id: Entity ID to filter by
            entity_type: Entity type to filter by
            from_block: Starting block index

        Returns:
            List of matching transactions
        """
        with self._lock:
            audit_trail = []

            for block in self.chain[from_block:]:
                for tx in block.transactions:
                    # Filter by entity
                    if entity_id and tx.data.get("entity_id") != entity_id:
                        continue
                    if entity_type and tx.data.get("entity_type") != entity_type:
                        continue

                    audit_trail.append(tx)

            return audit_trail

    def verify_transaction(self, tx_id: str) -> bool:
        """Verify transaction exists and is valid"""
        with self._lock:
            location = self._transaction_index.get(tx_id)
            if not location:
                return False

            block_idx, _ = location
            block = self.chain[block_idx]

            # Verify block is valid
            previous_block = self.chain[block_idx - 1] if block_idx > 0 else None
            return BlockValidator.validate_block(block, previous_block)

    def is_valid(self) -> bool:
        """Validate entire blockchain"""
        with self._lock:
            return BlockValidator.validate_chain(self.chain)

    def get_chain_length(self) -> int:
        """Get number of blocks in chain"""
        with self._lock:
            return len(self.chain)

    def get_statistics(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        with self._lock:
            total_transactions = sum(len(block.transactions) for block in self.chain)

            return {
                "chain_length": len(self.chain),
                "total_transactions": total_transactions,
                "pending_transactions": len(self.pending_transactions),
                "latest_block_hash": self.chain[-1].hash if self.chain else None,
                "is_valid": self.is_valid(),
                "genesis_timestamp": self.chain[0].timestamp.isoformat() if self.chain else None,
                "latest_timestamp": self.chain[-1].timestamp.isoformat() if self.chain else None
            }

    def export_chain(self, file_path: str):
        """Export blockchain to JSON file"""
        with self._lock:
            chain_data = [block.to_dict() for block in self.chain]

            with open(file_path, 'w') as f:
                json.dump(chain_data, f, indent=2)

            logger.info(f"Blockchain exported to {file_path}")

    def import_chain(self, file_path: str) -> bool:
        """Import blockchain from JSON file"""
        try:
            with open(file_path, 'r') as f:
                chain_data = json.load(f)

            # Reconstruct chain
            imported_chain = []
            for block_data in chain_data:
                transactions = [
                    Transaction(
                        tx_id=tx["tx_id"],
                        timestamp=datetime.fromisoformat(tx["timestamp"]),
                        tx_type=tx["tx_type"],
                        sender=tx["sender"],
                        data=tx["data"],
                        signature=tx.get("signature"),
                        metadata=tx.get("metadata", {})
                    )
                    for tx in block_data["transactions"]
                ]

                block = Block(
                    index=block_data["index"],
                    timestamp=datetime.fromisoformat(block_data["timestamp"]),
                    transactions=transactions,
                    previous_hash=block_data["previous_hash"],
                    nonce=block_data["nonce"],
                    validator=block_data["validator"],
                    metadata=block_data.get("metadata", {})
                )

                imported_chain.append(block)

            # Validate imported chain
            if not BlockValidator.validate_chain(imported_chain):
                logger.error("Imported chain validation failed")
                return False

            # Replace current chain
            with self._lock:
                self.chain = imported_chain
                self._rebuild_index()

            logger.info(f"Blockchain imported from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False

    def _rebuild_index(self):
        """Rebuild transaction index"""
        self._transaction_index = {}
        for block in self.chain:
            self._index_block(block)


# Singleton instance
_blockchain_instance = None
_instance_lock = threading.Lock()


def get_blockchain() -> Blockchain:
    """Get singleton Blockchain instance"""
    global _blockchain_instance

    if _blockchain_instance is None:
        with _instance_lock:
            if _blockchain_instance is None:
                _blockchain_instance = Blockchain()

    return _blockchain_instance


if __name__ == "__main__":
    # Example usage
    blockchain = get_blockchain()

    # Add some transactions
    tx1 = Transaction(
        tx_type="document_created",
        sender="user-123",
        data={
            "entity_id": "doc-456",
            "entity_type": "document",
            "title": "Sample Document",
            "action": "created"
        }
    )

    tx2 = Transaction(
        tx_type="document_updated",
        sender="user-123",
        data={
            "entity_id": "doc-456",
            "entity_type": "document",
            "title": "Updated Document",
            "action": "updated"
        }
    )

    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)

    # Mine block
    block = blockchain.mine_block(validator="validator-1")
    print(f"Block mined: {block.index}")
    print(f"Block hash: {block.hash}")
    print(f"Merkle root: {block.merkle_root}")

    # Get audit trail
    audit_trail = blockchain.get_audit_trail(entity_id="doc-456")
    print(f"\nAudit trail for doc-456: {len(audit_trail)} entries")

    # Verify chain
    is_valid = blockchain.is_valid()
    print(f"\nBlockchain valid: {is_valid}")

    # Statistics
    stats = blockchain.get_statistics()
    print(f"\nBlockchain statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nBlockchain Core module loaded successfully!")
