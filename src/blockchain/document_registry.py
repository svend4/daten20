#!/usr/bin/env python3
"""
Blockchain Document Registry Module

Provides blockchain-based document registry for immutable audit trails.

Key Features:
- Document hash storage on blockchain (Ethereum, Hyperledger, Polygon)
- Immutable audit trail
- Proof of existence with timestamps
- Chain of custody tracking
- Smart contract integration
- Multi-chain support
- Gas optimization
- Event logging
- Verification API
- Document provenance

Dependencies:
- web3 (for Ethereum integration)
- hashlib (for hashing)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import hashlib
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class BlockchainNetwork(str, Enum):
    """Supported blockchain networks"""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"  # Testnet
    POLYGON = "polygon"
    POLYGON_MUMBAI = "polygon_mumbai"  # Testnet
    HYPERLEDGER_FABRIC = "hyperledger_fabric"
    BINANCE_SMART_CHAIN = "binance_smart_chain"


class DocumentEventType(str, Enum):
    """Document event types"""
    CREATED = "created"
    MODIFIED = "modified"
    ACCESSED = "accessed"
    TRANSFERRED = "transferred"
    VERIFIED = "verified"
    DELETED = "deleted"


@dataclass
class DocumentHash:
    """Document hash information"""
    document_id: str
    file_hash: str  # SHA-256 hash of document
    metadata_hash: str  # Hash of metadata
    combined_hash: str  # Hash of file + metadata
    algorithm: str = "SHA-256"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BlockchainTransaction:
    """Blockchain transaction"""
    tx_hash: str
    block_number: int
    network: BlockchainNetwork
    from_address: str
    to_address: str
    gas_used: int
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentRegistryEntry:
    """Document registry entry on blockchain"""
    document_id: str
    document_hash: DocumentHash
    owner_address: str
    created_at: datetime
    blockchain_tx: Optional[BlockchainTransaction] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    chain_of_custody: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProofOfExistence:
    """Proof of existence certificate"""
    document_id: str
    document_hash: str
    blockchain_tx_hash: str
    timestamp: datetime
    network: BlockchainNetwork
    block_number: int
    verified: bool = True


class DocumentHasher:
    """
    Document hasher

    Creates cryptographic hashes of documents for blockchain storage.
    """

    @staticmethod
    def hash_file(file_path: str) -> str:
        """
        Hash file contents

        Args:
            file_path: Path to file

        Returns:
            SHA-256 hash of file
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)

        return sha256.hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """
        Hash bytes

        Args:
            data: Bytes to hash

        Returns:
            SHA-256 hash
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_string(text: str) -> str:
        """
        Hash string

        Args:
            text: String to hash

        Returns:
            SHA-256 hash
        """
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def hash_metadata(metadata: Dict[str, Any]) -> str:
        """
        Hash metadata dictionary

        Args:
            metadata: Metadata dictionary

        Returns:
            SHA-256 hash of sorted JSON
        """
        # Sort keys for consistent hashing
        sorted_json = json.dumps(metadata, sort_keys=True)
        return DocumentHasher.hash_string(sorted_json)

    @staticmethod
    def create_document_hash(
        file_path: str,
        metadata: Dict[str, Any]
    ) -> DocumentHash:
        """
        Create document hash with file and metadata

        Args:
            file_path: Path to file
            metadata: Document metadata

        Returns:
            Document hash object
        """
        file_hash = DocumentHasher.hash_file(file_path)
        metadata_hash = DocumentHasher.hash_metadata(metadata)

        # Combine hashes
        combined = f"{file_hash}:{metadata_hash}"
        combined_hash = DocumentHasher.hash_string(combined)

        return DocumentHash(
            document_id=metadata.get('document_id', ''),
            file_hash=file_hash,
            metadata_hash=metadata_hash,
            combined_hash=combined_hash
        )


class BlockchainDocumentRegistry:
    """
    Blockchain Document Registry

    Manages document registration and verification on blockchain.
    """

    def __init__(
        self,
        network: BlockchainNetwork = BlockchainNetwork.ETHEREUM_SEPOLIA,
        contract_address: Optional[str] = None
    ):
        """
        Initialize blockchain registry

        Args:
            network: Blockchain network to use
            contract_address: Smart contract address
        """
        self.network = network
        self.contract_address = contract_address
        self._registry: Dict[str, DocumentRegistryEntry] = {}
        self._tx_history: List[BlockchainTransaction] = []

    def register_document(
        self,
        document_id: str,
        document_hash: DocumentHash,
        owner_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentRegistryEntry:
        """
        Register document on blockchain

        Args:
            document_id: Document ID
            document_hash: Document hash
            owner_address: Owner's blockchain address
            metadata: Additional metadata

        Returns:
            Registry entry
        """
        # Create registry entry
        entry = DocumentRegistryEntry(
            document_id=document_id,
            document_hash=document_hash,
            owner_address=owner_address,
            created_at=datetime.now(),
            metadata=metadata or {},
            chain_of_custody=[owner_address]
        )

        # Simulate blockchain transaction
        tx = self._submit_to_blockchain(
            action='register_document',
            data={
                'document_id': document_id,
                'hash': document_hash.combined_hash,
                'owner': owner_address
            }
        )

        entry.blockchain_tx = tx

        # Add event
        entry.events.append({
            'type': DocumentEventType.CREATED,
            'timestamp': datetime.now().isoformat(),
            'actor': owner_address,
            'tx_hash': tx.tx_hash
        })

        # Store in registry
        self._registry[document_id] = entry

        logger.info(
            f"Registered document {document_id} on {self.network} "
            f"(tx: {tx.tx_hash})"
        )

        return entry

    def verify_document(
        self,
        document_id: str,
        document_hash: str
    ) -> bool:
        """
        Verify document hash against blockchain

        Args:
            document_id: Document ID
            document_hash: Document hash to verify

        Returns:
            True if hash matches blockchain record
        """
        entry = self._registry.get(document_id)

        if not entry:
            logger.warning(f"Document {document_id} not found in registry")
            return False

        verified = entry.document_hash.combined_hash == document_hash

        # Add verification event
        entry.events.append({
            'type': DocumentEventType.VERIFIED,
            'timestamp': datetime.now().isoformat(),
            'hash': document_hash,
            'verified': verified
        })

        logger.info(
            f"Document {document_id} verification: "
            f"{'PASSED' if verified else 'FAILED'}"
        )

        return verified

    def get_proof_of_existence(
        self,
        document_id: str
    ) -> Optional[ProofOfExistence]:
        """
        Get proof of existence certificate

        Args:
            document_id: Document ID

        Returns:
            Proof of existence or None
        """
        entry = self._registry.get(document_id)

        if not entry or not entry.blockchain_tx:
            return None

        return ProofOfExistence(
            document_id=document_id,
            document_hash=entry.document_hash.combined_hash,
            blockchain_tx_hash=entry.blockchain_tx.tx_hash,
            timestamp=entry.created_at,
            network=self.network,
            block_number=entry.blockchain_tx.block_number
        )

    def transfer_ownership(
        self,
        document_id: str,
        from_address: str,
        to_address: str
    ) -> bool:
        """
        Transfer document ownership

        Args:
            document_id: Document ID
            from_address: Current owner address
            to_address: New owner address

        Returns:
            True if transfer successful
        """
        entry = self._registry.get(document_id)

        if not entry:
            logger.error(f"Document {document_id} not found")
            return False

        if entry.owner_address != from_address:
            logger.error(
                f"Transfer denied: {from_address} is not owner of {document_id}"
            )
            return False

        # Submit transfer to blockchain
        tx = self._submit_to_blockchain(
            action='transfer_ownership',
            data={
                'document_id': document_id,
                'from': from_address,
                'to': to_address
            }
        )

        # Update ownership
        entry.owner_address = to_address
        entry.chain_of_custody.append(to_address)

        # Add event
        entry.events.append({
            'type': DocumentEventType.TRANSFERRED,
            'timestamp': datetime.now().isoformat(),
            'from': from_address,
            'to': to_address,
            'tx_hash': tx.tx_hash
        })

        logger.info(
            f"Transferred document {document_id} from {from_address} "
            f"to {to_address} (tx: {tx.tx_hash})"
        )

        return True

    def get_chain_of_custody(self, document_id: str) -> List[str]:
        """
        Get chain of custody for document

        Args:
            document_id: Document ID

        Returns:
            List of owner addresses in chronological order
        """
        entry = self._registry.get(document_id)
        return entry.chain_of_custody if entry else []

    def get_document_events(
        self,
        document_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all events for document

        Args:
            document_id: Document ID

        Returns:
            List of events
        """
        entry = self._registry.get(document_id)
        return entry.events if entry else []

    def get_document_entry(
        self,
        document_id: str
    ) -> Optional[DocumentRegistryEntry]:
        """
        Get document registry entry

        Args:
            document_id: Document ID

        Returns:
            Registry entry or None
        """
        return self._registry.get(document_id)

    def _submit_to_blockchain(
        self,
        action: str,
        data: Dict[str, Any]
    ) -> BlockchainTransaction:
        """
        Submit transaction to blockchain (simulated)

        Args:
            action: Action type
            data: Transaction data

        Returns:
            Blockchain transaction
        """
        # In production, this would interact with actual blockchain
        # For now, simulate transaction

        import random

        tx = BlockchainTransaction(
            tx_hash=f"0x{hashlib.sha256(str(data).encode()).hexdigest()}",
            block_number=random.randint(1000000, 9999999),
            network=self.network,
            from_address=data.get('owner', data.get('from', '0x0')),
            to_address=self.contract_address or '0x0',
            gas_used=random.randint(21000, 100000),
            timestamp=datetime.now(),
            data={'action': action, **data}
        )

        self._tx_history.append(tx)

        return tx

    def get_transaction_history(self) -> List[BlockchainTransaction]:
        """
        Get all blockchain transactions

        Returns:
            List of transactions
        """
        return self._tx_history


class SmartContractInterface:
    """
    Smart contract interface for document registry

    Provides interface for interacting with blockchain smart contracts.
    Supports both Ethereum (via Web3.py) and Hyperledger Fabric.
    """

    def __init__(
        self,
        contract_address: str,
        abi: List[Dict],
        network: BlockchainNetwork = BlockchainNetwork.ETHEREUM_SEPOLIA,
        provider_url: Optional[str] = None
    ):
        """
        Initialize smart contract interface

        Args:
            contract_address: Contract address
            abi: Contract ABI (Application Binary Interface)
            network: Blockchain network
            provider_url: RPC provider URL (e.g., Infura, Alchemy)
        """
        self.contract_address = contract_address
        self.abi = abi
        self.network = network
        self.provider_url = provider_url
        self._web3 = None
        self._contract = None
        self._fabric_client = None

        # Initialize based on network type
        if self._is_ethereum_network():
            self._init_web3()
        elif network == BlockchainNetwork.HYPERLEDGER_FABRIC:
            self._init_fabric()

    def _is_ethereum_network(self) -> bool:
        """Check if network is Ethereum-based"""
        return self.network in [
            BlockchainNetwork.ETHEREUM_MAINNET,
            BlockchainNetwork.ETHEREUM_SEPOLIA,
            BlockchainNetwork.POLYGON,
            BlockchainNetwork.POLYGON_MUMBAI,
            BlockchainNetwork.BINANCE_SMART_CHAIN
        ]

    def _init_web3(self):
        """Initialize Web3.py connection for Ethereum"""
        try:
            # Optional import - only needed if using Ethereum
            from web3 import Web3

            if not self.provider_url:
                # Default providers for different networks
                providers = {
                    BlockchainNetwork.ETHEREUM_MAINNET: "https://eth-mainnet.g.alchemy.com/v2/demo",
                    BlockchainNetwork.ETHEREUM_SEPOLIA: "https://eth-sepolia.g.alchemy.com/v2/demo",
                    BlockchainNetwork.POLYGON: "https://polygon-rpc.com",
                    BlockchainNetwork.POLYGON_MUMBAI: "https://rpc-mumbai.maticvigil.com",
                    BlockchainNetwork.BINANCE_SMART_CHAIN: "https://bsc-dataseed.binance.org"
                }
                self.provider_url = providers.get(self.network, "http://localhost:8545")

            self._web3 = Web3(Web3.HTTPProvider(self.provider_url))

            if self._web3.is_connected():
                logger.info(f"Connected to {self.network} at {self.provider_url}")
                self._contract = self._web3.eth.contract(
                    address=self.contract_address,
                    abi=self.abi
                )
            else:
                logger.warning(f"Failed to connect to {self.network}")

        except ImportError:
            logger.warning("web3 package not installed. Install with: pip install web3")
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")

    def _init_fabric(self):
        """Initialize Hyperledger Fabric connection"""
        try:
            # Optional import - only needed if using Fabric
            # Note: Hyperledger Fabric SDK for Python is complex
            # This is a placeholder for actual implementation
            logger.info("Initializing Hyperledger Fabric client")
            # from hfc.fabric import Client
            # self._fabric_client = Client(net_profile="network.json")
            self._fabric_client = None  # Placeholder
            logger.warning("Hyperledger Fabric SDK integration pending")
        except ImportError:
            logger.warning("Hyperledger Fabric SDK not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Fabric client: {e}")

    def register_document_on_chain(
        self,
        document_id: str,
        document_hash: str,
        owner_address: str,
        private_key: Optional[str] = None,
        gas_price: Optional[int] = None
    ) -> Optional[str]:
        """
        Register document on smart contract

        Args:
            document_id: Document identifier
            document_hash: Document hash
            owner_address: Owner's blockchain address
            private_key: Private key for signing transaction (optional)
            gas_price: Custom gas price in wei (optional, for optimization)

        Returns:
            Transaction hash or None if failed
        """
        if not self._web3 or not self._contract:
            logger.error("Web3 not initialized")
            return None

        try:
            # Build transaction
            tx_data = self._contract.functions.registerDocument(
                document_id,
                document_hash,
                owner_address
            )

            # Estimate gas
            estimated_gas = tx_data.estimate_gas({'from': owner_address})

            # Apply gas optimization (add 10% buffer)
            gas_limit = int(estimated_gas * 1.1)

            # Get optimal gas price if not provided
            if gas_price is None:
                gas_price = self._get_optimal_gas_price()

            # Build transaction
            transaction = tx_data.build_transaction({
                'from': owner_address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': self._web3.eth.get_transaction_count(owner_address)
            })

            # Sign and send transaction if private key provided
            if private_key:
                signed_tx = self._web3.eth.account.sign_transaction(
                    transaction,
                    private_key
                )
                tx_hash = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)

                logger.info(f"Document registered on-chain: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                # Return unsigned transaction for external signing
                logger.info(f"Prepared transaction (unsigned): {transaction}")
                return None

        except Exception as e:
            logger.error(f"Failed to register document on-chain: {e}")
            return None

    def verify_document_on_chain(
        self,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify document against smart contract

        Args:
            document_id: Document identifier

        Returns:
            Document data from blockchain or None
        """
        if not self._web3 or not self._contract:
            logger.error("Web3 not initialized")
            return None

        try:
            # Call smart contract view function
            result = self._contract.functions.getDocument(document_id).call()

            return {
                'document_id': document_id,
                'hash': result[0] if isinstance(result, (list, tuple)) else result,
                'exists': True
            }
        except Exception as e:
            logger.error(f"Failed to verify document on-chain: {e}")
            return None

    def transfer_ownership_on_chain(
        self,
        document_id: str,
        from_address: str,
        to_address: str,
        private_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Transfer document ownership on smart contract

        Args:
            document_id: Document identifier
            from_address: Current owner address
            to_address: New owner address
            private_key: Private key for signing (optional)

        Returns:
            Transaction hash or None
        """
        if not self._web3 or not self._contract:
            logger.error("Web3 not initialized")
            return None

        try:
            tx_data = self._contract.functions.transferOwnership(
                document_id,
                to_address
            )

            transaction = tx_data.build_transaction({
                'from': from_address,
                'gas': 100000,
                'gasPrice': self._get_optimal_gas_price(),
                'nonce': self._web3.eth.get_transaction_count(from_address)
            })

            if private_key:
                signed_tx = self._web3.eth.account.sign_transaction(
                    transaction,
                    private_key
                )
                tx_hash = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)

                logger.info(f"Ownership transferred on-chain: {tx_hash.hex()}")
                return tx_hash.hex()

            return None

        except Exception as e:
            logger.error(f"Failed to transfer ownership on-chain: {e}")
            return None

    def listen_to_events(
        self,
        event_name: str,
        from_block: int = 0,
        to_block: str = 'latest',
        callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Listen to smart contract events

        Args:
            event_name: Name of event to listen for
            from_block: Starting block number
            to_block: Ending block (default: 'latest')
            callback: Optional callback function for each event

        Returns:
            List of events
        """
        if not self._web3 or not self._contract:
            logger.error("Web3 not initialized")
            return []

        try:
            # Get event filter
            event = getattr(self._contract.events, event_name)
            event_filter = event.create_filter(
                from_block=from_block,
                to_block=to_block
            )

            # Get all events
            events = event_filter.get_all_entries()

            # Process events
            result = []
            for evt in events:
                event_data = {
                    'event': evt['event'],
                    'block_number': evt['blockNumber'],
                    'transaction_hash': evt['transactionHash'].hex(),
                    'args': dict(evt['args'])
                }
                result.append(event_data)

                # Call callback if provided
                if callback:
                    callback(event_data)

            logger.info(f"Found {len(result)} {event_name} events")
            return result

        except Exception as e:
            logger.error(f"Failed to listen to events: {e}")
            return []

    def _get_optimal_gas_price(self) -> int:
        """
        Get optimal gas price with optimization strategies

        Returns:
            Optimal gas price in wei
        """
        if not self._web3:
            return 0

        try:
            # Get current gas price from network
            current_price = self._web3.eth.gas_price

            # Apply optimization strategy:
            # - For testnets: use standard price
            # - For mainnet: use 90% of current price for cost savings
            if self.network in [
                BlockchainNetwork.ETHEREUM_SEPOLIA,
                BlockchainNetwork.POLYGON_MUMBAI
            ]:
                return current_price
            else:
                # Reduce gas price by 10% for mainnet (may take longer)
                return int(current_price * 0.9)

        except Exception as e:
            logger.error(f"Failed to get gas price: {e}")
            # Fallback to reasonable default (20 gwei)
            return 20_000_000_000

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction receipt or None
        """
        if not self._web3:
            return None

        try:
            receipt = self._web3.eth.get_transaction_receipt(tx_hash)
            return {
                'transaction_hash': receipt['transactionHash'].hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'status': receipt['status'],
                'logs': [dict(log) for log in receipt['logs']]
            }
        except Exception as e:
            logger.error(f"Failed to get transaction receipt: {e}")
            return None

    def get_block_timestamp(self, block_number: int) -> Optional[datetime]:
        """
        Get block timestamp

        Args:
            block_number: Block number

        Returns:
            Block timestamp or None
        """
        if not self._web3:
            return None

        try:
            block = self._web3.eth.get_block(block_number)
            return datetime.fromtimestamp(block['timestamp'])
        except Exception as e:
            logger.error(f"Failed to get block timestamp: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        if self._web3:
            return self._web3.is_connected()
        return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create hasher
    hasher = DocumentHasher()

    # Create registry
    registry = BlockchainDocumentRegistry(
        network=BlockchainNetwork.ETHEREUM_SEPOLIA
    )

    # Simulate document registration
    metadata = {
        'document_id': 'doc123',
        'title': 'Important Contract',
        'type': 'pdf'
    }

    # In production, would hash actual file
    doc_hash = DocumentHash(
        document_id='doc123',
        file_hash=hasher.hash_string('file content'),
        metadata_hash=hasher.hash_metadata(metadata),
        combined_hash=hasher.hash_string('combined')
    )

    # Register document
    entry = registry.register_document(
        document_id='doc123',
        document_hash=doc_hash,
        owner_address='0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
    )

    print(f"\nDocument registered:")
    print(f"  ID: {entry.document_id}")
    print(f"  Hash: {entry.document_hash.combined_hash}")
    print(f"  TX: {entry.blockchain_tx.tx_hash}")
    print(f"  Block: {entry.blockchain_tx.block_number}")

    # Verify document
    verified = registry.verify_document('doc123', doc_hash.combined_hash)
    print(f"\nVerification: {'PASSED' if verified else 'FAILED'}")

    # Get proof of existence
    proof = registry.get_proof_of_existence('doc123')
    if proof:
        print(f"\nProof of Existence:")
        print(f"  Document: {proof.document_id}")
        print(f"  Timestamp: {proof.timestamp}")
        print(f"  TX Hash: {proof.blockchain_tx_hash}")
        print(f"  Block: {proof.block_number}")

    # Transfer ownership
    registry.transfer_ownership(
        'doc123',
        from_address='0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        to_address='0x1234567890123456789012345678901234567890'
    )

    # Get chain of custody
    custody = registry.get_chain_of_custody('doc123')
    print(f"\nChain of Custody:")
    for i, address in enumerate(custody, 1):
        print(f"  {i}. {address}")
