"""
Merkle Tree Module - Efficient verification of large datasets
Provides Merkle tree implementation for document integrity verification.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class MerkleNode:
    """Node in Merkle tree"""
    hash_value: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    is_leaf: bool = False
    data: Optional[str] = None


class MerkleTree:
    """Merkle tree for efficient data verification"""

    def __init__(self, data_list: List[str]):
        """
        Initialize Merkle tree from list of data items

        Args:
            data_list: List of data items to create tree from
        """
        if not data_list:
            raise ValueError("Data list cannot be empty")

        self.leaves = [self._hash(data) for data in data_list]
        self.root = self._build_tree(self.leaves)

    def _hash(self, data: str) -> str:
        """Hash a data item"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _build_tree(self, hashes: List[str]) -> MerkleNode:
        """Recursively build Merkle tree"""
        # Create leaf nodes
        nodes = [
            MerkleNode(hash_value=h, is_leaf=True, data=h)
            for h in hashes
        ]

        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []

            # Process pairs of nodes
            for i in range(0, len(nodes), 2):
                left = nodes[i]

                # If odd number of nodes, duplicate last one
                if i + 1 < len(nodes):
                    right = nodes[i + 1]
                else:
                    right = nodes[i]

                # Create parent node
                combined_hash = self._hash(left.hash_value + right.hash_value)
                parent = MerkleNode(
                    hash_value=combined_hash,
                    left=left,
                    right=right
                )
                next_level.append(parent)

            nodes = next_level

        return nodes[0]

    def get_root_hash(self) -> str:
        """Get Merkle root hash"""
        return self.root.hash_value

    def get_proof(self, index: int) -> List[Tuple[str, str]]:
        """
        Get Merkle proof for element at index

        Returns list of (hash, position) tuples where position is 'left' or 'right'
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of range")

        proof = []
        current_index = index
        current_level_size = len(self.leaves)

        # Build proof by traversing from leaf to root
        current_hashes = self.leaves[:]

        while current_level_size > 1:
            # Find sibling
            if current_index % 2 == 0:  # Left node
                if current_index + 1 < current_level_size:
                    sibling = current_hashes[current_index + 1]
                    proof.append((sibling, 'right'))
                else:
                    sibling = current_hashes[current_index]
                    proof.append((sibling, 'right'))
            else:  # Right node
                sibling = current_hashes[current_index - 1]
                proof.append((sibling, 'left'))

            # Move up to parent level
            next_level = []
            for i in range(0, current_level_size, 2):
                left_hash = current_hashes[i]
                right_hash = current_hashes[i + 1] if i + 1 < current_level_size else left_hash
                parent_hash = self._hash(left_hash + right_hash)
                next_level.append(parent_hash)

            current_hashes = next_level
            current_index = current_index // 2
            current_level_size = len(current_hashes)

        return proof

    def verify_proof(
        self,
        data: str,
        index: int,
        proof: List[Tuple[str, str]],
        root_hash: str
    ) -> bool:
        """
        Verify Merkle proof for data at index

        Args:
            data: Original data
            index: Index in original data list
            proof: Merkle proof (list of sibling hashes and positions)
            root_hash: Expected root hash

        Returns:
            True if proof is valid
        """
        current_hash = self._hash(data)

        # Reconstruct path to root
        for sibling_hash, position in proof:
            if position == 'left':
                current_hash = self._hash(sibling_hash + current_hash)
            else:  # right
                current_hash = self._hash(current_hash + sibling_hash)

        return current_hash == root_hash

    def get_tree_depth(self) -> int:
        """Get depth of Merkle tree"""
        def _depth(node: Optional[MerkleNode]) -> int:
            if node is None or node.is_leaf:
                return 0
            return 1 + max(_depth(node.left), _depth(node.right))

        return _depth(self.root)

    def get_leaf_count(self) -> int:
        """Get number of leaves in tree"""
        return len(self.leaves)

    def to_dict(self) -> dict:
        """Convert tree to dictionary"""
        def _node_to_dict(node: Optional[MerkleNode]) -> Optional[dict]:
            if node is None:
                return None

            result = {
                "hash": node.hash_value,
                "is_leaf": node.is_leaf
            }

            if node.left:
                result["left"] = _node_to_dict(node.left)
            if node.right:
                result["right"] = _node_to_dict(node.right)

            return result

        return {
            "root_hash": self.root.hash_value,
            "leaf_count": len(self.leaves),
            "depth": self.get_tree_depth(),
            "tree": _node_to_dict(self.root)
        }


class MerkleTreeBatch:
    """Batch processor for multiple Merkle trees"""

    def __init__(self):
        self.trees: dict[str, MerkleTree] = {}

    def create_tree(self, tree_id: str, data_list: List[str]) -> MerkleTree:
        """Create and store new Merkle tree"""
        tree = MerkleTree(data_list)
        self.trees[tree_id] = tree
        logger.info(f"Created Merkle tree {tree_id} with {len(data_list)} leaves")
        return tree

    def get_tree(self, tree_id: str) -> Optional[MerkleTree]:
        """Get Merkle tree by ID"""
        return self.trees.get(tree_id)

    def verify_membership(
        self,
        tree_id: str,
        data: str,
        index: int,
        proof: List[Tuple[str, str]]
    ) -> bool:
        """Verify data membership in tree"""
        tree = self.trees.get(tree_id)
        if not tree:
            logger.error(f"Tree not found: {tree_id}")
            return False

        return tree.verify_proof(data, index, proof, tree.get_root_hash())

    def get_combined_root(self, tree_ids: List[str]) -> str:
        """Get combined root hash of multiple trees"""
        root_hashes = []

        for tree_id in tree_ids:
            tree = self.trees.get(tree_id)
            if tree:
                root_hashes.append(tree.get_root_hash())

        if not root_hashes:
            return ""

        # Create meta-tree from root hashes
        meta_tree = MerkleTree(root_hashes)
        return meta_tree.get_root_hash()

    def get_statistics(self) -> dict:
        """Get batch processing statistics"""
        total_leaves = sum(tree.get_leaf_count() for tree in self.trees.values())
        total_depth = sum(tree.get_tree_depth() for tree in self.trees.values())

        return {
            "total_trees": len(self.trees),
            "total_leaves": total_leaves,
            "average_depth": total_depth / len(self.trees) if self.trees else 0,
            "trees": {
                tree_id: {
                    "root_hash": tree.get_root_hash(),
                    "leaf_count": tree.get_leaf_count(),
                    "depth": tree.get_tree_depth()
                }
                for tree_id, tree in self.trees.items()
            }
        }


# Utility functions

def create_document_merkle_tree(documents: List[dict]) -> MerkleTree:
    """Create Merkle tree from list of documents"""
    data_list = [
        f"{doc.get('id', '')}:{doc.get('hash', '')}"
        for doc in documents
    ]
    return MerkleTree(data_list)


def verify_document_in_tree(
    document: dict,
    index: int,
    proof: List[Tuple[str, str]],
    root_hash: str
) -> bool:
    """Verify document is in Merkle tree"""
    tree = MerkleTree([])  # Dummy tree for verification
    data = f"{document.get('id', '')}:{document.get('hash', '')}"
    return tree.verify_proof(data, index, proof, root_hash)


# Singleton batch processor
_batch_processor = None

def get_batch_processor() -> MerkleTreeBatch:
    """Get singleton batch processor"""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = MerkleTreeBatch()
    return _batch_processor
