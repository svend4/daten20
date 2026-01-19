"""
Knowledge Graph Construction

Builds knowledge graphs from extracted entities and relations:
- Graph construction from NER + Relation Extraction
- Neo4j export (Cypher queries)
- Graph traversal and querying
- Graph analysis (centrality, paths, communities)
- Multiple export formats (JSON, GraphML, Cypher)

Integrates with:
- NEREngine for entity extraction
- RelationExtractor for relation extraction
- Neo4j for graph database storage
"""

import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .ner import Entity, EntityType, NEREngine
from .relation_extractor import Relation, RelationExtractor, RelationType


class GraphFormat(str, Enum):
    """Supported graph export formats"""

    JSON = "json"
    CYPHER = "cypher"
    GRAPHML = "graphml"
    ADJACENCY = "adjacency"


@dataclass
class Node:
    """Graph node representing an entity"""

    id: str  # Unique node identifier
    text: str  # Entity text
    type: EntityType  # Entity type (PERSON, ORG, LOCATION)
    properties: Dict[str, Any] = field(default_factory=dict)  # Additional properties

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False


@dataclass
class Edge:
    """Graph edge representing a relation"""

    source: str  # Source node ID
    target: str  # Target node ID
    relation: RelationType  # Relation type
    confidence: float  # Confidence score
    properties: Dict[str, Any] = field(default_factory=dict)  # Additional properties

    def __hash__(self):
        return hash((self.source, self.relation, self.target))


class KnowledgeGraph:
    """Knowledge graph built from entities and relations"""

    def __init__(self):
        """Initialize empty knowledge graph"""
        self.nodes: Dict[str, Node] = {}  # node_id -> Node
        self.edges: List[Edge] = []  # List of edges
        self.adjacency: Dict[str, List[Edge]] = defaultdict(list)  # node_id -> outgoing edges
        self.reverse_adjacency: Dict[str, List[Edge]] = defaultdict(list)  # node_id -> incoming edges

    def add_node(self, node: Node) -> None:
        """Add node to graph"""
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        """Add edge to graph"""
        # Ensure nodes exist
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(f"Source or target node not found: {edge.source} -> {edge.target}")

        # Add edge
        self.edges.append(edge)
        self.adjacency[edge.source].append(edge)
        self.reverse_adjacency[edge.target].append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, relation_type: Optional[RelationType] = None) -> List[Node]:
        """
        Get neighboring nodes

        Args:
            node_id: Node ID
            relation_type: Filter by relation type (optional)

        Returns:
            List of neighboring nodes
        """
        neighbors = []
        for edge in self.adjacency.get(node_id, []):
            if relation_type is None or edge.relation == relation_type:
                neighbor = self.nodes.get(edge.target)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def get_incoming_neighbors(self, node_id: str, relation_type: Optional[RelationType] = None) -> List[Node]:
        """Get nodes with incoming edges to this node"""
        neighbors = []
        for edge in self.reverse_adjacency.get(node_id, []):
            if relation_type is None or edge.relation == relation_type:
                neighbor = self.nodes.get(edge.source)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """
        Find shortest path between two nodes (BFS)

        Args:
            start_id: Start node ID
            end_id: End node ID
            max_depth: Maximum path length

        Returns:
            List of node IDs representing path, or None if no path found
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        if start_id == end_id:
            return [start_id]

        # BFS
        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            current_id, path = queue.popleft()

            if len(path) > max_depth:
                continue

            # Check neighbors
            for edge in self.adjacency.get(current_id, []):
                neighbor_id = edge.target

                if neighbor_id == end_id:
                    return path + [neighbor_id]

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    def get_subgraph(self, node_id: str, depth: int = 1) -> "KnowledgeGraph":
        """
        Extract subgraph around a node

        Args:
            node_id: Center node ID
            depth: Number of hops to include

        Returns:
            New KnowledgeGraph containing subgraph
        """
        subgraph = KnowledgeGraph()

        if node_id not in self.nodes:
            return subgraph

        # BFS to collect nodes within depth
        visited = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            current_id, current_depth = queue.popleft()

            # Add node
            subgraph.add_node(self.nodes[current_id])

            if current_depth < depth:
                # Add outgoing neighbors
                for edge in self.adjacency.get(current_id, []):
                    if edge.target not in visited:
                        visited.add(edge.target)
                        queue.append((edge.target, current_depth + 1))

                # Add incoming neighbors
                for edge in self.reverse_adjacency.get(current_id, []):
                    if edge.source not in visited:
                        visited.add(edge.source)
                        queue.append((edge.source, current_depth + 1))

        # Add edges between nodes in subgraph
        for edge in self.edges:
            if edge.source in subgraph.nodes and edge.target in subgraph.nodes:
                subgraph.add_edge(edge)

        return subgraph

    def query(
        self,
        node_type: Optional[EntityType] = None,
        relation_type: Optional[RelationType] = None,
        min_confidence: float = 0.0,
    ) -> List[Tuple[Node, Optional[Edge], Optional[Node]]]:
        """
        Query graph for nodes/edges matching criteria

        Args:
            node_type: Filter nodes by type
            relation_type: Filter edges by relation type
            min_confidence: Minimum edge confidence

        Returns:
            List of (source_node, edge, target_node) tuples
        """
        results = []

        if relation_type is not None:
            # Query edges
            for edge in self.edges:
                if edge.relation == relation_type and edge.confidence >= min_confidence:
                    source = self.nodes[edge.source]
                    target = self.nodes[edge.target]

                    if node_type is None or source.type == node_type or target.type == node_type:
                        results.append((source, edge, target))
        else:
            # Query nodes only
            for node in self.nodes.values():
                if node_type is None or node.type == node_type:
                    results.append((node, None, None))

        return results

    def get_node_degree(self, node_id: str) -> Tuple[int, int, int]:
        """
        Get node degree (in, out, total)

        Returns:
            Tuple of (in_degree, out_degree, total_degree)
        """
        in_degree = len(self.reverse_adjacency.get(node_id, []))
        out_degree = len(self.adjacency.get(node_id, []))
        return in_degree, out_degree, in_degree + out_degree

    def get_central_nodes(self, top_n: int = 10) -> List[Tuple[Node, int]]:
        """
        Get most central nodes by degree centrality

        Args:
            top_n: Number of nodes to return

        Returns:
            List of (node, degree) tuples, sorted by degree descending
        """
        node_degrees = []
        for node_id, node in self.nodes.items():
            _, _, total_degree = self.get_node_degree(node_id)
            node_degrees.append((node, total_degree))

        # Sort by degree descending
        node_degrees.sort(key=lambda x: x[1], reverse=True)
        return node_degrees[:top_n]

    def export(self, format: GraphFormat = GraphFormat.JSON) -> str:
        """
        Export graph to specified format

        Args:
            format: Export format

        Returns:
            Serialized graph string
        """
        if format == GraphFormat.JSON:
            return self._export_json()
        elif format == GraphFormat.CYPHER:
            return self._export_cypher()
        elif format == GraphFormat.GRAPHML:
            return self._export_graphml()
        elif format == GraphFormat.ADJACENCY:
            return self._export_adjacency()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(self) -> str:
        """Export as JSON"""
        data = {
            "nodes": [
                {"id": node.id, "text": node.text, "type": node.type.value, "properties": node.properties}
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "relation": edge.relation.value,
                    "confidence": edge.confidence,
                    "properties": edge.properties,
                }
                for edge in self.edges
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _export_cypher(self) -> str:
        """Export as Neo4j Cypher queries"""
        queries = []

        # Create nodes
        for node in self.nodes.values():
            props = {"text": node.text, "type": node.type.value, **node.properties}
            props_str = ", ".join(f"{k}: {json.dumps(v)}" for k, v in props.items())
            queries.append(f"CREATE (n{node.id.replace(' ', '_')}:Entity {{id: {json.dumps(node.id)}, {props_str}}})")

        # Create relationships
        for edge in self.edges:
            source_id = edge.source.replace(" ", "_")
            target_id = edge.target.replace(" ", "_")
            props = {"confidence": edge.confidence, **edge.properties}
            props_str = ", ".join(f"{k}: {json.dumps(v)}" for k, v in props.items())

            queries.append(
                f"MATCH (s:Entity {{id: {json.dumps(edge.source)}}}), "
                f"(t:Entity {{id: {json.dumps(edge.target)}}}) "
                f"CREATE (s)-[:{edge.relation.value.upper()} {{{props_str}}}]->(t)"
            )

        return "\n".join(queries) + "\n"

    def _export_graphml(self) -> str:
        """Export as GraphML XML"""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
        lines.append('  <graph id="KnowledgeGraph" edgedefault="directed">')

        # Nodes
        for node in self.nodes.values():
            node_id_safe = node.id.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
            lines.append(f'    <node id="{node_id_safe}">')
            lines.append(f'      <data key="text">{node.text}</data>')
            lines.append(f'      <data key="type">{node.type.value}</data>')
            lines.append("    </node>")

        # Edges
        for i, edge in enumerate(self.edges):
            source_safe = edge.source.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
            target_safe = edge.target.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
            lines.append(f'    <edge id="e{i}" source="{source_safe}" target="{target_safe}">')
            lines.append(f'      <data key="relation">{edge.relation.value}</data>')
            lines.append(f'      <data key="confidence">{edge.confidence}</data>')
            lines.append("    </edge>")

        lines.append("  </graph>")
        lines.append("</graphml>")

        return "\n".join(lines)

    def _export_adjacency(self) -> str:
        """Export as adjacency list (JSON)"""
        adjacency_data = {}
        for node_id, edges in self.adjacency.items():
            adjacency_data[node_id] = [
                {"target": edge.target, "relation": edge.relation.value, "confidence": edge.confidence}
                for edge in edges
            ]
        return json.dumps(adjacency_data, indent=2, ensure_ascii=False)

    def stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        # Count entity types
        entity_counts = defaultdict(int)
        for node in self.nodes.values():
            entity_counts[node.type.value] += 1

        # Count relation types
        relation_counts = defaultdict(int)
        for edge in self.edges:
            relation_counts[edge.relation.value] += 1

        # Calculate degree statistics
        degrees = [self.get_node_degree(nid)[2] for nid in self.nodes.keys()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        return {
            "num_nodes": len(self.nodes),
            "num_edges": len(self.edges),
            "entity_types": dict(entity_counts),
            "relation_types": dict(relation_counts),
            "avg_degree": round(avg_degree, 2),
            "max_degree": max(degrees) if degrees else 0,
            "density": (
                round(len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1)), 4) if len(self.nodes) > 1 else 0
            ),
        }


class KnowledgeGraphBuilder:
    """Build knowledge graphs from text using NER + Relation Extraction"""

    def __init__(self, use_spacy: bool = True, spacy_model: str = "de_core_news_sm"):
        """
        Initialize knowledge graph builder

        Args:
            use_spacy: Whether to use spaCy
            spacy_model: spaCy model to use
        """
        self.ner_engine = NEREngine(use_spacy=use_spacy, spacy_model=spacy_model)
        self.relation_extractor = RelationExtractor(use_spacy=use_spacy, spacy_model=spacy_model)

    def build_from_text(self, text: str, min_confidence: float = 0.5) -> KnowledgeGraph:
        """
        Build knowledge graph from text

        Args:
            text: Input text
            min_confidence: Minimum relation confidence threshold

        Returns:
            KnowledgeGraph
        """
        graph = KnowledgeGraph()

        # Extract entities
        entities = self.ner_engine.extract_entities(text)

        # Add entities as nodes
        for entity in entities:
            node = Node(
                id=entity.text,
                text=entity.text,
                type=entity.type,
                properties={"start": entity.start, "end": entity.end, "confidence": entity.confidence},
            )
            graph.add_node(node)

        # Extract relations
        relations = self.relation_extractor.extract_relations(text)

        # Add relations as edges
        for relation in relations:
            if relation.confidence >= min_confidence:
                edge = Edge(
                    source=relation.subject.text,
                    target=relation.object.text,
                    relation=relation.relation,
                    confidence=relation.confidence,
                    properties={"context": relation.context, "start": relation.start, "end": relation.end},
                )

                # Only add edge if both nodes exist
                if edge.source in graph.nodes and edge.target in graph.nodes:
                    graph.add_edge(edge)

        return graph

    def build_from_entities_and_relations(
        self, entities: List[Entity], relations: List[Relation], min_confidence: float = 0.5
    ) -> KnowledgeGraph:
        """
        Build knowledge graph from pre-extracted entities and relations

        Args:
            entities: List of entities
            relations: List of relations
            min_confidence: Minimum relation confidence threshold

        Returns:
            KnowledgeGraph
        """
        graph = KnowledgeGraph()

        # Add entities as nodes
        for entity in entities:
            node = Node(
                id=entity.text,
                text=entity.text,
                type=entity.type,
                properties={"start": entity.start, "end": entity.end, "confidence": entity.confidence},
            )
            graph.add_node(node)

        # Add relations as edges
        for relation in relations:
            if relation.confidence >= min_confidence:
                edge = Edge(
                    source=relation.subject.text,
                    target=relation.object.text,
                    relation=relation.relation,
                    confidence=relation.confidence,
                    properties={"context": relation.context, "start": relation.start, "end": relation.end},
                )

                # Only add edge if both nodes exist
                if edge.source in graph.nodes and edge.target in graph.nodes:
                    graph.add_edge(edge)

        return graph


# Global instance
_kg_builder: Optional[KnowledgeGraphBuilder] = None


def get_kg_builder(use_spacy: bool = True, spacy_model: str = "de_core_news_sm") -> KnowledgeGraphBuilder:
    """Get global knowledge graph builder instance"""
    global _kg_builder

    if _kg_builder is None:
        _kg_builder = KnowledgeGraphBuilder(use_spacy=use_spacy, spacy_model=spacy_model)

    return _kg_builder
