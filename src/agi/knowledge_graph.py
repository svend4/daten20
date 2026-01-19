"""
Knowledge Graph System - v4.5

Semantic knowledge representation and graph-based reasoning.

Version: 4.5.0
"""

__version__ = '4.5.0'

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in knowledge graph"""
    ENTITY = "entity"
    CONCEPT = "concept"
    EVENT = "event"
    ATTRIBUTE = "attribute"
    RELATION = "relation"


class EdgeType(Enum):
    """Types of edges in knowledge graph"""
    IS_A = "is_a"              # Taxonomy
    PART_OF = "part_of"        # Meronymy
    HAS_PROPERTY = "has_property"
    CAUSES = "causes"
    SIMILAR_TO = "similar_to"
    LOCATED_AT = "located_at"
    TEMPORAL = "temporal"
    CUSTOM = "custom"


@dataclass
class Node:
    """Node in knowledge graph"""
    node_id: str
    label: str
    node_type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Edge:
    """Edge in knowledge graph"""
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Path:
    """Path through knowledge graph"""
    nodes: List[str]
    edges: List[str]
    total_weight: float
    path_type: str = "shortest"


class KnowledgeGraph:
    """
    Knowledge Graph System

    Semantic knowledge representation using graph structure:
    - Entities and concepts as nodes
    - Relationships as edges
    - Graph traversal and search
    - Semantic similarity
    - Path finding
    - Subgraph extraction

    Example:
        >>> kg = KnowledgeGraph()
        >>> kg.add_node("doc1", "Document", NodeType.ENTITY)
        >>> kg.add_node("pdf", "PDF Format", NodeType.CONCEPT)
        >>> kg.add_edge("doc1", "pdf", EdgeType.IS_A)
        >>> path = kg.find_path("doc1", "pdf")
    """

    def __init__(self):
        """Initialize Knowledge Graph"""
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency: Dict[str, List[str]] = {}  # node_id -> [edge_ids]

        logger.info("Knowledge Graph initialized")

    def add_node(self,
                node_id: str,
                label: str,
                node_type: NodeType,
                properties: Optional[Dict[str, Any]] = None) -> Node:
        """
        Add node to knowledge graph

        Args:
            node_id: Unique node identifier
            label: Node label
            node_type: Type of node
            properties: Optional properties

        Returns:
            Created node
        """
        if node_id in self.nodes:
            logger.warning(f"Node {node_id} already exists")
            return self.nodes[node_id]

        node = Node(
            node_id=node_id,
            label=label,
            node_type=node_type,
            properties=properties or {}
        )

        self.nodes[node_id] = node
        self.adjacency[node_id] = []

        logger.debug(f"Added node: {node_id} ({label})")
        return node

    def add_edge(self,
                source_id: str,
                target_id: str,
                edge_type: EdgeType,
                weight: float = 1.0,
                properties: Optional[Dict[str, Any]] = None) -> Optional[Edge]:
        """
        Add edge to knowledge graph

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of edge
            weight: Edge weight
            properties: Optional properties

        Returns:
            Created edge or None if nodes don't exist
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.error(f"Cannot add edge: nodes not found ({source_id}, {target_id})")
            return None

        edge_id = f"{source_id}-{edge_type.value}-{target_id}"

        edge = Edge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            properties=properties or {}
        )

        self.edges[edge_id] = edge
        self.adjacency[source_id].append(edge_id)

        logger.debug(f"Added edge: {source_id} -> {target_id} ({edge_type.value})")
        return edge

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[Node]:
        """
        Get neighboring nodes

        Args:
            node_id: Source node ID
            edge_type: Optional filter by edge type

        Returns:
            List of neighbor nodes
        """
        if node_id not in self.adjacency:
            return []

        neighbors = []
        for edge_id in self.adjacency[node_id]:
            edge = self.edges[edge_id]

            if edge_type is None or edge.edge_type == edge_type:
                target_node = self.nodes.get(edge.target_id)
                if target_node:
                    neighbors.append(target_node)

        return neighbors

    def find_path(self,
                 start_id: str,
                 end_id: str,
                 max_depth: int = 10) -> Optional[Path]:
        """
        Find path between two nodes (BFS)

        Args:
            start_id: Start node ID
            end_id: End node ID
            max_depth: Maximum search depth

        Returns:
            Path or None if no path found
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        # BFS
        queue = [(start_id, [start_id], [], 0.0)]
        visited = {start_id}

        while queue:
            current_id, path_nodes, path_edges, total_weight = queue.pop(0)

            if current_id == end_id:
                return Path(
                    nodes=path_nodes,
                    edges=path_edges,
                    total_weight=total_weight
                )

            if len(path_nodes) >= max_depth:
                continue

            # Explore neighbors
            for edge_id in self.adjacency.get(current_id, []):
                edge = self.edges[edge_id]
                neighbor_id = edge.target_id

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((
                        neighbor_id,
                        path_nodes + [neighbor_id],
                        path_edges + [edge_id],
                        total_weight + edge.weight
                    ))

        return None

    def find_semantic_similarity(self, node_id1: str, node_id2: str) -> float:
        """
        Compute semantic similarity between nodes

        Uses path-based similarity.

        Args:
            node_id1: First node ID
            node_id2: Second node ID

        Returns:
            Similarity score (0-1)
        """
        if node_id1 == node_id2:
            return 1.0

        # Find shortest path
        path = self.find_path(node_id1, node_id2)

        if path is None:
            return 0.0

        # Similarity inversely proportional to path length
        path_length = len(path.nodes) - 1
        similarity = 1.0 / (1.0 + path_length)

        return similarity

    def query_subgraph(self,
                      center_node_id: str,
                      radius: int = 2,
                      edge_types: Optional[List[EdgeType]] = None) -> Dict[str, Any]:
        """
        Extract subgraph around center node

        Args:
            center_node_id: Center node ID
            radius: How many hops from center
            edge_types: Optional filter by edge types

        Returns:
            Subgraph as dict with nodes and edges
        """
        if center_node_id not in self.nodes:
            return {'nodes': {}, 'edges': {}}

        subgraph_nodes = {center_node_id: self.nodes[center_node_id]}
        subgraph_edges = {}

        # BFS to explore neighborhood
        queue = [(center_node_id, 0)]
        visited = {center_node_id}

        while queue:
            current_id, depth = queue.pop(0)

            if depth >= radius:
                continue

            for edge_id in self.adjacency.get(current_id, []):
                edge = self.edges[edge_id]

                # Filter by edge type if specified
                if edge_types and edge.edge_type not in edge_types:
                    continue

                neighbor_id = edge.target_id

                # Add edge to subgraph
                subgraph_edges[edge_id] = edge

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    subgraph_nodes[neighbor_id] = self.nodes[neighbor_id]
                    queue.append((neighbor_id, depth + 1))

        return {
            'nodes': subgraph_nodes,
            'edges': subgraph_edges
        }

    def get_ancestors(self, node_id: str, max_depth: int = 10) -> List[Node]:
        """
        Get ancestor nodes (following IS_A relations)

        Args:
            node_id: Node ID
            max_depth: Maximum depth

        Returns:
            List of ancestor nodes
        """
        ancestors = []
        visited = {node_id}
        queue = [(node_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            for edge_id in self.adjacency.get(current_id, []):
                edge = self.edges[edge_id]

                if edge.edge_type == EdgeType.IS_A:
                    parent_id = edge.target_id

                    if parent_id not in visited:
                        visited.add(parent_id)
                        parent_node = self.nodes[parent_id]
                        ancestors.append(parent_node)
                        queue.append((parent_id, depth + 1))

        return ancestors

    def get_descendants(self, node_id: str) -> List[Node]:
        """
        Get descendant nodes (reverse IS_A relations)

        Args:
            node_id: Node ID

        Returns:
            List of descendant nodes
        """
        descendants = []

        for edge in self.edges.values():
            if edge.edge_type == EdgeType.IS_A and edge.target_id == node_id:
                child_node = self.nodes.get(edge.source_id)
                if child_node:
                    descendants.append(child_node)
                    # Recursively get descendants
                    descendants.extend(self.get_descendants(edge.source_id))

        return descendants

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge graph statistics

        Returns:
            Statistics dict
        """
        node_type_counts = {}
        for node in self.nodes.values():
            node_type = node.node_type.value
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

        edge_type_counts = {}
        for edge in self.edges.values():
            edge_type = edge.edge_type.value
            edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1

        return {
            'num_nodes': len(self.nodes),
            'num_edges': len(self.edges),
            'node_types': node_type_counts,
            'edge_types': edge_type_counts,
            'avg_degree': len(self.edges) / len(self.nodes) if self.nodes else 0
        }

    def visualize(self) -> str:
        """
        Generate text visualization of graph

        Returns:
            Text representation
        """
        lines = ["Knowledge Graph Visualization"]
        lines.append("=" * 40)

        stats = self.get_statistics()
        lines.append(f"Nodes: {stats['num_nodes']}, Edges: {stats['num_edges']}")
        lines.append("")

        # Show some nodes and edges
        for i, (node_id, node) in enumerate(list(self.nodes.items())[:10]):
            lines.append(f"[{node_id}] {node.label} ({node.node_type.value})")

            # Show outgoing edges
            for edge_id in self.adjacency.get(node_id, [])[:3]:
                edge = self.edges[edge_id]
                target = self.nodes.get(edge.target_id)
                if target:
                    lines.append(f"  -> {edge.edge_type.value} -> [{target.node_id}] {target.label}")

        if len(self.nodes) > 10:
            lines.append(f"... and {len(self.nodes) - 10} more nodes")

        return "\n".join(lines)


__all__ = [
    'KnowledgeGraph',
    'Node',
    'Edge',
    'Path',
    'NodeType',
    'EdgeType',
]
