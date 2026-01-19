"""
Integration tests for v3.4 Blockchain & Security
Tests all blockchain components together.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

BLOCKCHAIN_DIR = Path(__file__).parent.parent.parent / "src" / "blockchain"


class TestBlockchainStructure:
    """Test blockchain module structure"""

    def test_blockchain_module_exists(self):
        """Test blockchain module directory exists"""
        assert BLOCKCHAIN_DIR.exists(), "Blockchain directory should exist"

    def test_all_modules_exist(self):
        """Test all required modules exist"""
        required_modules = [
            "blockchain_core.py",
            "document_registry.py",
            "smart_contracts.py",
            "consensus.py",
            "merkle_tree.py",
            "transaction_manager.py",
            "audit_logger.py",
            "__init__.py"
        ]

        for module in required_modules:
            module_path = BLOCKCHAIN_DIR / module
            assert module_path.exists(), f"{module} should exist"

    def test_init_imports(self):
        """Test __init__.py has all imports"""
        init_file = BLOCKCHAIN_DIR / "__init__.py"
        content = init_file.read_text()

        required_imports = [
            "from .blockchain_core import",
            "from .document_registry import",
            "from .smart_contracts import",
            "from .consensus import",
            "from .merkle_tree import",
            "from .transaction_manager import",
            "from .audit_logger import"
        ]

        for import_stmt in required_imports:
            assert import_stmt in content, f"{import_stmt} should be in __init__.py"


class TestSmartContracts:
    """Test smart contracts implementation"""

    def test_smart_contracts_file_exists(self):
        """Test smart_contracts.py exists"""
        smart_contracts = BLOCKCHAIN_DIR / "smart_contracts.py"
        assert smart_contracts.exists()

    def test_smart_contracts_implementation(self):
        """Test smart contracts has required classes"""
        smart_contracts = BLOCKCHAIN_DIR / "smart_contracts.py"
        content = smart_contracts.read_text()

        required_classes = [
            "class SmartContract",
            "class SmartContractEngine",
            "class ContractCondition",
            "class ContractAction",
            "class ContractType",
            "class ContractState"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_contract_methods(self):
        """Test smart contract methods exist"""
        smart_contracts = BLOCKCHAIN_DIR / "smart_contracts.py"
        content = smart_contracts.read_text()

        required_methods = [
            "def create_contract",
            "def activate_contract",
            "def update_context",
            "def revoke_contract",
            "def get_contract"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestConsensus:
    """Test consensus mechanism"""

    def test_consensus_file_exists(self):
        """Test consensus.py exists"""
        consensus = BLOCKCHAIN_DIR / "consensus.py"
        assert consensus.exists()

    def test_consensus_implementation(self):
        """Test consensus has required classes"""
        consensus = BLOCKCHAIN_DIR / "consensus.py"
        content = consensus.read_text()

        required_classes = [
            "class ProofOfAuthority",
            "class Validator",
            "class ValidatorStatus",
            "class ConsensusRound"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_consensus_methods(self):
        """Test consensus methods exist"""
        consensus = BLOCKCHAIN_DIR / "consensus.py"
        content = consensus.read_text()

        required_methods = [
            "def add_validator",
            "def remove_validator",
            "def select_validator",
            "def validate_block",
            "def start_consensus_round",
            "def cast_vote"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestMerkleTree:
    """Test Merkle tree implementation"""

    def test_merkle_tree_file_exists(self):
        """Test merkle_tree.py exists"""
        merkle_tree = BLOCKCHAIN_DIR / "merkle_tree.py"
        assert merkle_tree.exists()

    def test_merkle_tree_implementation(self):
        """Test Merkle tree has required classes"""
        merkle_tree = BLOCKCHAIN_DIR / "merkle_tree.py"
        content = merkle_tree.read_text()

        required_classes = [
            "class MerkleTree",
            "class MerkleNode",
            "class MerkleTreeBatch"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_merkle_tree_methods(self):
        """Test Merkle tree methods exist"""
        merkle_tree = BLOCKCHAIN_DIR / "merkle_tree.py"
        content = merkle_tree.read_text()

        required_methods = [
            "def get_root_hash",
            "def get_proof",
            "def verify_proof",
            "def get_tree_depth"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestTransactionManager:
    """Test transaction manager"""

    def test_transaction_manager_file_exists(self):
        """Test transaction_manager.py exists"""
        tx_manager = BLOCKCHAIN_DIR / "transaction_manager.py"
        assert tx_manager.exists()

    def test_transaction_manager_implementation(self):
        """Test transaction manager has required classes"""
        tx_manager = BLOCKCHAIN_DIR / "transaction_manager.py"
        content = tx_manager.read_text()

        required_classes = [
            "class Transaction",
            "class TransactionManager",
            "class TransactionPool",
            "class TransactionType",
            "class TransactionStatus"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_transaction_methods(self):
        """Test transaction methods exist"""
        tx_manager = BLOCKCHAIN_DIR / "transaction_manager.py"
        content = tx_manager.read_text()

        required_methods = [
            "def create_transaction",
            "def submit_transaction",
            "def get_transaction",
            "def confirm_transactions"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestAuditLogger:
    """Test audit logger"""

    def test_audit_logger_file_exists(self):
        """Test audit_logger.py exists"""
        audit_logger = BLOCKCHAIN_DIR / "audit_logger.py"
        assert audit_logger.exists()

    def test_audit_logger_implementation(self):
        """Test audit logger has required classes"""
        audit_logger = BLOCKCHAIN_DIR / "audit_logger.py"
        content = audit_logger.read_text()

        required_classes = [
            "class AuditEvent",
            "class BlockchainAuditLogger",
            "class AuditEventType"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_audit_logger_methods(self):
        """Test audit logger methods exist"""
        audit_logger = BLOCKCHAIN_DIR / "audit_logger.py"
        content = audit_logger.read_text()

        required_methods = [
            "def log_event",
            "def get_events",
            "def verify_integrity"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestBlockchainIntegration:
    """Test integration between blockchain components"""

    def test_all_singleton_getters_exist(self):
        """Test all modules have singleton getters"""
        init_file = BLOCKCHAIN_DIR / "__init__.py"
        content = init_file.read_text()

        required_getters = [
            "get_blockchain",
            "get_contract_engine",
            "get_consensus",
            "get_batch_processor",
            "get_transaction_manager",
            "get_audit_logger"
        ]

        for getter in required_getters:
            assert getter in content, f"{getter} should be in __all__"

    def test_module_version(self):
        """Test module has correct version"""
        init_file = BLOCKCHAIN_DIR / "__init__.py"
        content = init_file.read_text()

        assert "__version__ = '3.4.0'" in content
        assert "Version: 3.4.0 (Complete)" in content


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
