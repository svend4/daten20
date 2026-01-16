"""
Comprehensive tests for Knowledge Graph module

Test coverage goals:
- Node: Creation, properties, hashing, equality
- Edge: Creation, relations, confidence scores
- KnowledgeGraph: Graph construction, node/edge management
- Graph traversal: Neighbors, paths, shortest paths
- Graph analysis: Centrality, communities, statistics
- Export formats: JSON, Cypher, GraphML, Adjacency
- Performance: Large graphs, complex queries
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from src.ml.knowledge_graph import (
    GraphFormat,
    Node,
    Edge,
    KnowledgeGraph,
    GraphBuilder,
    GraphAnalyzer,
)
from src.ml.ner import Entity, EntityType
from src.ml.relation_extractor import Relation, RelationType


class TestGraphFormat:
    """Test GraphFormat enum"""

    def test_all_formats(self):
        """Test all graph export formats"""
        formats = [
            GraphFormat.JSON,
            GraphFormat.CYPHER,
            GraphFormat.GRAPHML,
            GraphFormat.ADJACENCY,
        ]

        assert len(formats) == 4
        for fmt in formats:
            assert isinstance(fmt.value, str)


class TestNode:
    """Test Node dataclass"""

    def test_node_creation(self):
        """Test basic node creation"""
        node = Node(
            id="person_1",
            text="John Doe",
            type=EntityType.PERSON,
            properties={"age": 30, "occupation": "Engineer"}
        )

        assert node.id == "person_1"
        assert node.text == "John Doe"
        assert node.type == EntityType.PERSON
        assert node.properties["age"] == 30

    def test_node_default_properties(self):
        """Test node with default properties"""
        node = Node(
            id="org_1",
            text="Microsoft",
            type=EntityType.ORGANIZATION
        )

        assert node.properties == {}

    def test_node_hashing(self):
        """Test node hashing"""
        node1 = Node("id_1", "Text", EntityType.PERSON)
        node2 = Node("id_1", "Different Text", EntityType.PERSON)
        node3 = Node("id_2", "Text", EntityType.PERSON)

        # Same ID should hash equally
        assert hash(node1) == hash(node2)
        # Different ID should hash differently
        assert hash(node1) != hash(node3)

    def test_node_equality(self):
        """Test node equality"""
        node1 = Node("id_1", "Text", EntityType.PERSON)
        node2 = Node("id_1", "Different Text", EntityType.PERSON)
        node3 = Node("id_2", "Text", EntityType.PERSON)

        assert node1 == node2  # Same ID
        assert node1 != node3  # Different ID

    def test_node_in_set(self):
        """Test using nodes in sets"""
        node1 = Node("id_1", "Text", EntityType.PERSON)
        node2 = Node("id_1", "Text", EntityType.PERSON)
        node3 = Node("id_2", "Other", EntityType.ORGANIZATION)

        node_set = {node1, node2, node3}
        # node1 and node2 have same ID, so only 2 unique nodes
        assert len(node_set) == 2


class TestEdge:
    """Test Edge dataclass"""

    def test_edge_creation(self):
        """Test basic edge creation"""
        edge = Edge(
            source="person_1",
            target="org_1",
            relation=RelationType.WORKS_AT,
            confidence=0.95,
            properties={"since": "2020"}
        )

        assert edge.source == "person_1"
        assert edge.target == "org_1"
        assert edge.relation == RelationType.WORKS_AT
        assert edge.confidence == 0.95

    def test_edge_default_properties(self):
        """Test edge with default properties"""
        edge = Edge(
            source="person_1",
            target="person_2",
            relation=RelationType.KNOWS,
            confidence=0.80
        )

        assert edge.properties == {}

    def test_edge_hashing(self):
        """Test edge hashing"""
        edge1 = Edge("src", "tgt", RelationType.WORKS_AT, 0.9)
        edge2 = Edge("src", "tgt", RelationType.WORKS_AT, 0.8)  # Different confidence
        edge3 = Edge("src", "tgt", RelationType.KNOWS, 0.9)  # Different relation

        # Same source, target, relation should hash equally
        assert hash(edge1) == hash(edge2)
        # Different relation should hash differently
        assert hash(edge1) != hash(edge3)


class TestKnowledgeGraph:
    """Test KnowledgeGraph class"""

    @pytest.fixture
    def graph(self):
        """Create empty knowledge graph"""
        return KnowledgeGraph()

    @pytest.fixture
    def sample_nodes(self):
        """Create sample nodes"""
        return [
            Node("person_1", "John Doe", EntityType.PERSON),
            Node("person_2", "Jane Smith", EntityType.PERSON),
            Node("org_1", "Microsoft", EntityType.ORGANIZATION),
            Node("loc_1", "Seattle", EntityType.LOCATION),
        ]

    def test_initialization(self, graph):
        """Test graph initialization"""
        assert graph is not None
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_add_node(self, graph, sample_nodes):
        """Test adding nodes"""
        for node in sample_nodes:
            graph.add_node(node)

        assert len(graph.nodes) == 4
        assert "person_1" in graph.nodes

    def test_add_duplicate_node(self, graph):
        """Test adding duplicate node"""
        node = Node("id_1", "Test", EntityType.PERSON)
        graph.add_node(node)
        graph.add_node(node)

        # Should only have one node
        assert len(graph.nodes) == 1

    def test_add_edge(self, graph, sample_nodes):
        """Test adding edges"""
        # Add nodes first
        for node in sample_nodes:
            graph.add_node(node)

        # Add edge
        edge = Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95)
        graph.add_edge(edge)

        assert len(graph.edges) == 1
        assert len(graph.adjacency["person_1"]) == 1

    def test_add_edge_without_nodes(self, graph):
        """Test adding edge without nodes raises error"""
        edge = Edge("nonexistent_1", "nonexistent_2", RelationType.KNOWS, 0.8)

        with pytest.raises(ValueError):
            graph.add_edge(edge)

    def test_get_node(self, graph, sample_nodes):
        """Test getting node by ID"""
        for node in sample_nodes:
            graph.add_node(node)

        node = graph.get_node("person_1")
        assert node is not None
        assert node.text == "John Doe"

        # Non-existent node
        assert graph.get_node("nonexistent") is None

    def test_get_neighbors(self, graph, sample_nodes):
        """Test getting neighboring nodes"""
        # Build graph
        for node in sample_nodes:
            graph.add_node(node)

        edges = [
            Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95),
            Edge("person_1", "loc_1", RelationType.LOCATED_IN, 0.90),
            Edge("person_2", "org_1", RelationType.WORKS_AT, 0.92),
        ]

        for edge in edges:
            graph.add_edge(edge)

        # Get neighbors of person_1
        neighbors = graph.get_neighbors("person_1")
        assert len(neighbors) == 2

        # Filter by relation type
        work_neighbors = graph.get_neighbors("person_1", RelationType.WORKS_AT)
        assert len(work_neighbors) == 1
        assert work_neighbors[0].id == "org_1"

    def test_adjacency_list(self, graph, sample_nodes):
        """Test adjacency list structure"""
        for node in sample_nodes:
            graph.add_node(node)

        edge = Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95)
        graph.add_edge(edge)

        # Check adjacency
        assert "person_1" in graph.adjacency
        assert len(graph.adjacency["person_1"]) == 1

        # Check reverse adjacency
        assert "org_1" in graph.reverse_adjacency
        assert len(graph.reverse_adjacency["org_1"]) == 1

    def test_node_degree(self, graph, sample_nodes):
        """Test calculating node degree"""
        for node in sample_nodes:
            graph.add_node(node)

        edges = [
            Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95),
            Edge("person_1", "loc_1", RelationType.LOCATED_IN, 0.90),
            Edge("person_2", "person_1", RelationType.KNOWS, 0.85),
        ]

        for edge in edges:
            graph.add_edge(edge)

        # person_1 has out-degree 2, in-degree 1
        out_degree = len(graph.adjacency["person_1"])
        in_degree = len(graph.reverse_adjacency["person_1"])

        assert out_degree == 2
        assert in_degree == 1

    def test_find_path(self, graph, sample_nodes):
        """Test finding path between nodes"""
        for node in sample_nodes:
            graph.add_node(node)

        edges = [
            Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95),
            Edge("org_1", "loc_1", RelationType.LOCATED_IN, 0.90),
        ]

        for edge in edges:
            graph.add_edge(edge)

        # Find path from person_1 to loc_1
        path = graph.find_path("person_1", "loc_1")

        if path:
            assert len(path) >= 2
            assert path[0] == "person_1"
            assert path[-1] == "loc_1"

    def test_export_json(self, graph, sample_nodes):
        """Test export to JSON format"""
        for node in sample_nodes:
            graph.add_node(node)

        edge = Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95)
        graph.add_edge(edge)

        json_output = graph.export(GraphFormat.JSON)

        # Should be valid JSON
        data = json.loads(json_output)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 4
        assert len(data["edges"]) == 1

    def test_export_cypher(self, graph, sample_nodes):
        """Test export to Cypher queries"""
        for node in sample_nodes:
            graph.add_node(node)

        edge = Edge("person_1", "org_1", RelationType.WORKS_AT, 0.95)
        graph.add_edge(edge)

        cypher_output = graph.export(GraphFormat.CYPHER)

        # Should contain CREATE statements
        assert "CREATE" in cypher_output
        assert isinstance(cypher_output, str)


class TestGraphBuilder:
    """Test GraphBuilder class"""

    @pytest.fixture
    def builder(self):
        """Create GraphBuilder instance"""
        return GraphBuilder()

    @pytest.fixture
    def sample_entities(self):
        """Create sample entities"""
        return [
            Entity("John Doe", EntityType.PERSON, 0, 8),
            Entity("Microsoft", EntityType.ORGANIZATION, 18, 27),
            Entity("Seattle", EntityType.LOCATION, 31, 38),
        ]

    @pytest.fixture
    def sample_relations(self):
        """Create sample relations"""
        return [
            Relation(
                subject=Entity("John Doe", EntityType.PERSON, 0, 8),
                predicate=RelationType.WORKS_AT,
                object=Entity("Microsoft", EntityType.ORGANIZATION, 18, 27),
                confidence=0.95
            ),
        ]

    def test_build_from_entities(self, builder, sample_entities, sample_relations):
        """Test building graph from entities and relations"""
        graph = builder.build(sample_entities, sample_relations)

        assert len(graph.nodes) == 3
        assert len(graph.edges) >= 1

    def test_build_with_no_relations(self, builder, sample_entities):
        """Test building graph with only entities"""
        graph = builder.build(sample_entities, [])

        assert len(graph.nodes) == 3
        assert len(graph.edges) == 0

    def test_build_empty_graph(self, builder):
        """Test building empty graph"""
        graph = builder.build([], [])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


class TestGraphAnalyzer:
    """Test GraphAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create GraphAnalyzer instance"""
        return GraphAnalyzer()

    @pytest.fixture
    def sample_graph(self):
        """Create sample graph"""
        graph = KnowledgeGraph()

        # Add nodes
        nodes = [
            Node("p1", "Person 1", EntityType.PERSON),
            Node("p2", "Person 2", EntityType.PERSON),
            Node("o1", "Org 1", EntityType.ORGANIZATION),
        ]

        for node in nodes:
            graph.add_node(node)

        # Add edges
        edges = [
            Edge("p1", "o1", RelationType.WORKS_AT, 0.95),
            Edge("p2", "o1", RelationType.WORKS_AT, 0.90),
        ]

        for edge in edges:
            graph.add_edge(edge)

        return graph

    def test_calculate_statistics(self, analyzer, sample_graph):
        """Test calculating graph statistics"""
        stats = analyzer.calculate_statistics(sample_graph)

        assert "num_nodes" in stats
        assert "num_edges" in stats
        assert stats["num_nodes"] == 3
        assert stats["num_edges"] == 2

    def test_find_central_nodes(self, analyzer, sample_graph):
        """Test finding central nodes"""
        central_nodes = analyzer.find_central_nodes(sample_graph, top_k=2)

        assert len(central_nodes) <= 2
        # Organization should be central (has 2 incoming edges)
        if central_nodes:
            assert central_nodes[0][0] in ["o1"]  # Most central


class TestPerformance:
    """Performance tests for knowledge graph"""

    @pytest.fixture
    def large_graph(self):
        """Create large graph"""
        graph = KnowledgeGraph()

        # Add 1000 nodes
        for i in range(1000):
            node = Node(f"node_{i}", f"Entity {i}", EntityType.PERSON)
            graph.add_node(node)

        # Add edges
        for i in range(0, 999, 2):
            edge = Edge(f"node_{i}", f"node_{i+1}", RelationType.KNOWS, 0.9)
            graph.add_edge(edge)

        return graph

    def test_large_graph_creation(self, benchmark):
        """Benchmark large graph creation"""
        def create_graph():
            graph = KnowledgeGraph()
            for i in range(100):
                node = Node(f"node_{i}", f"Entity {i}", EntityType.PERSON)
                graph.add_node(node)
            for i in range(0, 99, 2):
                edge = Edge(f"node_{i}", f"node_{i+1}", RelationType.KNOWS, 0.9)
                graph.add_edge(edge)
            return graph

        result = benchmark(create_graph)
        assert len(result.nodes) == 100

    def test_neighbor_query_performance(self, large_graph, benchmark):
        """Benchmark neighbor queries"""
        result = benchmark(large_graph.get_neighbors, "node_0")

    def test_export_performance(self, large_graph, benchmark):
        """Benchmark export to JSON"""
        result = benchmark(large_graph.export, GraphFormat.JSON)
        assert isinstance(result, str)


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def graph(self):
        """Create graph"""
        return KnowledgeGraph()

    def test_get_neighbors_nonexistent_node(self, graph):
        """Test getting neighbors of nonexistent node"""
        neighbors = graph.get_neighbors("nonexistent")
        assert neighbors == []

    def test_circular_references(self, graph):
        """Test handling circular references"""
        # Add nodes
        node1 = Node("n1", "Node 1", EntityType.PERSON)
        node2 = Node("n2", "Node 2", EntityType.PERSON)
        graph.add_node(node1)
        graph.add_node(node2)

        # Add circular edges
        edge1 = Edge("n1", "n2", RelationType.KNOWS, 0.9)
        edge2 = Edge("n2", "n1", RelationType.KNOWS, 0.9)
        graph.add_edge(edge1)
        graph.add_edge(edge2)

        # Should handle circular references
        assert len(graph.edges) == 2

    def test_self_loop(self, graph):
        """Test self-loop edge"""
        node = Node("n1", "Node 1", EntityType.PERSON)
        graph.add_node(node)

        # Self-loop
        edge = Edge("n1", "n1", RelationType.KNOWS, 0.9)
        graph.add_edge(edge)

        assert len(graph.edges) == 1

    def test_multiple_edges_same_nodes(self, graph):
        """Test multiple edges between same nodes"""
        node1 = Node("n1", "Node 1", EntityType.PERSON)
        node2 = Node("n2", "Node 2", EntityType.ORGANIZATION)
        graph.add_node(node1)
        graph.add_node(node2)

        # Multiple relations between same nodes
        edges = [
            Edge("n1", "n2", RelationType.WORKS_AT, 0.9),
            Edge("n1", "n2", RelationType.FOUNDED, 0.8),
        ]

        for edge in edges:
            graph.add_edge(edge)

        assert len(graph.edges) == 2

    def test_empty_node_properties(self, graph):
        """Test node with empty properties"""
        node = Node("n1", "", EntityType.PERSON)
        graph.add_node(node)

        assert "n1" in graph.nodes
        assert graph.nodes["n1"].text == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
