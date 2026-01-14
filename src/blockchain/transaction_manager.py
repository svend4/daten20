"""
Transaction Manager - Handle blockchain transactions
Manages transaction lifecycle, validation, and execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Types of blockchain transactions"""
    DOCUMENT_CREATE = "document_create"
    DOCUMENT_UPDATE = "document_update"
    DOCUMENT_TRANSFER = "document_transfer"
    DOCUMENT_DELETE = "document_delete"
    SMART_CONTRACT = "smart_contract"
    TOKEN_MINT = "token_mint"
    TOKEN_TRANSFER = "token_transfer"


class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVERTED = "reverted"


@dataclass
class Transaction:
    """Blockchain transaction"""
    transaction_id: str
    transaction_type: TransactionType
    sender: str
    data: Dict
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: TransactionStatus = TransactionStatus.PENDING
    block_hash: Optional[str] = None
    gas_used: int = 0
    signature: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type.value,
            "sender": self.sender,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "block_hash": self.block_hash,
            "gas_used": self.gas_used,
        }

    def get_hash(self) -> str:
        """Get transaction hash"""
        tx_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_str.encode()).hexdigest()


class TransactionPool:
    """Pool of pending transactions (mempool)"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.transactions: Dict[str, Transaction] = {}
        self.pending_count = 0

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add transaction to pool"""
        if len(self.transactions) >= self.max_size:
            logger.warning("Transaction pool is full")
            return False

        self.transactions[transaction.transaction_id] = transaction
        self.pending_count += 1
        logger.info(f"Added transaction {transaction.transaction_id} to pool")
        return True

    def get_pending_transactions(self, limit: int = 100) -> List[Transaction]:
        """Get pending transactions for next block"""
        pending = [
            tx for tx in self.transactions.values()
            if tx.status == TransactionStatus.PENDING
        ]
        return sorted(pending, key=lambda x: x.timestamp)[:limit]

    def mark_confirmed(self, transaction_id: str, block_hash: str):
        """Mark transaction as confirmed"""
        if transaction_id in self.transactions:
            tx = self.transactions[transaction_id]
            tx.status = TransactionStatus.CONFIRMED
            tx.block_hash = block_hash
            self.pending_count -= 1


class TransactionManager:
    """Manages blockchain transactions"""

    def __init__(self):
        self.pool = TransactionPool()
        self.confirmed_transactions: Dict[str, Transaction] = {}
        self.transaction_history: List[Transaction] = []

    def create_transaction(
        self,
        transaction_type: TransactionType,
        sender: str,
        data: Dict,
        metadata: Optional[Dict] = None
    ) -> Transaction:
        """Create new transaction"""
        transaction_id = hashlib.sha256(
            f"{sender}{transaction_type.value}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        transaction = Transaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            sender=sender,
            data=data,
            metadata=metadata or {}
        )

        return transaction

    def submit_transaction(self, transaction: Transaction) -> bool:
        """Submit transaction to pool"""
        # Validate transaction
        if not self._validate_transaction(transaction):
            logger.error(f"Transaction validation failed: {transaction.transaction_id}")
            transaction.status = TransactionStatus.FAILED
            return False

        # Add to pool
        success = self.pool.add_transaction(transaction)
        if success:
            transaction.status = TransactionStatus.VALIDATED
            logger.info(f"Transaction submitted: {transaction.transaction_id}")

        return success

    def _validate_transaction(self, transaction: Transaction) -> bool:
        """Validate transaction"""
        # Basic validation
        if not transaction.sender:
            return False

        if not transaction.data:
            return False

        # Type-specific validation
        if transaction.transaction_type == TransactionType.DOCUMENT_CREATE:
            required_fields = ["document_id", "document_hash"]
            if not all(field in transaction.data for field in required_fields):
                return False

        return True

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        # Check pool first
        if transaction_id in self.pool.transactions:
            return self.pool.transactions[transaction_id]

        # Check confirmed
        return self.confirmed_transactions.get(transaction_id)

    def confirm_transactions(self, transaction_ids: List[str], block_hash: str):
        """Confirm transactions in block"""
        for tx_id in transaction_ids:
            tx = self.pool.transactions.get(tx_id)
            if tx:
                tx.status = TransactionStatus.CONFIRMED
                tx.block_hash = block_hash
                self.confirmed_transactions[tx_id] = tx
                self.transaction_history.append(tx)
                self.pool.mark_confirmed(tx_id, block_hash)

        logger.info(f"Confirmed {len(transaction_ids)} transactions in block {block_hash[:8]}")

    def get_transaction_history(
        self,
        sender: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transaction history with filters"""
        history = self.transaction_history

        if sender:
            history = [tx for tx in history if tx.sender == sender]

        if transaction_type:
            history = [tx for tx in history if tx.transaction_type == transaction_type]

        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_statistics(self) -> Dict:
        """Get transaction statistics"""
        return {
            "pending_transactions": self.pool.pending_count,
            "confirmed_transactions": len(self.confirmed_transactions),
            "total_transactions": len(self.transaction_history),
            "pool_size": len(self.pool.transactions),
            "by_type": {
                tx_type.value: sum(
                    1 for tx in self.transaction_history
                    if tx.transaction_type == tx_type
                )
                for tx_type in TransactionType
            }
        }


# Singleton
_transaction_manager = None

def get_transaction_manager() -> TransactionManager:
    """Get singleton transaction manager"""
    global _transaction_manager
    if _transaction_manager is None:
        _transaction_manager = TransactionManager()
    return _transaction_manager
