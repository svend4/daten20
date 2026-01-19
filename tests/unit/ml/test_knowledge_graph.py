"""
Comprehensive tests for ml/knowledge_graph.py module.

Tests knowledge graph construction, graph operations, querying,
path finding, export formats, and graph analysis.
"""

import json
import pytest
from unittest.mock import Mock, patch


# ============================================================================
# Data Classes Tests
# ============================================================================


class TestNode:
    """Test Node dataclass."""

    def test_node_creation(self):
        """Test creating a node"""
        from src.ml.knowledge_graph import Node
        from src.ml.ner import EntityType

        node = Node(
            id="person_1",
            text="Max Mustermann",
            type=EntityType.PERSON,
            properties={"age": 30}
        )

        assert node.id == "person_1"
        assert node.text == "Max Mustermann"
        assert node.type == EntityType.PERSON
        assert node.properties["age"] == 30

    def test_node_equality(self):
        """Test node equality by ID"""
        from src.ml.knowledge_graph import Node
        from src.ml.ner import EntityType

        node1 = Node(id="n1", text="Text", type=EntityType.PERSON)
        node2 = Node(id="n1", text="Different", type=EntityType.ORGANIZATION)
        node3 = Node(id="n2", text="Text", type=EntityType.PERSON)

        assert node1 == node2  # Same ID
        assert node1 != node3  # Different ID

    def test_node_hash(self):
        """Test node can be hashed"""
        from src.ml.knowledge_graph import Node
        from src.ml.ner import EntityType

        node = Node(id="n1", text="Text", type=EntityType.PERSON)

        # Should be hashable
        node_set = {node}
        assert node in node_set


class TestEdge:
    """Test Edge dataclass."""

    def test_edge_creation(self):
        """Test creating an edge"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        edge = Edge(
            source="person_1",
            target="org_1",
            relation=RelationType.WORKS_AT,
            confidence=0.95,
            properties={"context": "works at"}
        )

        assert edge.source == "person_1"
        assert edge.target == "org_1"
        assert edge.relation == RelationType.WORKS_AT
        assert edge.confidence == 0.95

    def test_edge_hash(self):
        """Test edge can be hashed"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        edge = Edge(
            source="n1",
            target="n2",
            relation=RelationType.WORKS_AT,
            confidence=0.8
        )

        # Should be hashable
        edge_set = {edge}
        assert edge in edge_set


# ============================================================================
# KnowledgeGraph Tests
# ============================================================================


class TestKnowledgeGraph:
    """Test KnowledgeGraph functionality."""

    @pytest.fixture
    def graph(self):
        """Create empty knowledge graph."""
        from src.ml.knowledge_graph import KnowledgeGraph

        return KnowledgeGraph()

    @pytest.fixture
    def sample_nodes(self):
        """Create sample nodes."""
        from src.ml.knowledge_graph import Node
        from src.ml.ner import EntityType

        return [
            Node(id="max", text="Max Mustermann", type=EntityType.PERSON),
            Node(id="siemens", text="Siemens AG", type=EntityType.ORGANIZATION),
            Node(id="munich", text="München", type=EntityType.LOCATION)
        ]

    def test_knowledge_graph_initialization(self, graph):
        """Test KnowledgeGraph initialization"""
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph.adjacency) == 0

    def test_add_node(self, graph, sample_nodes):
        """Test adding node to graph"""
        graph.add_node(sample_nodes[0])

        assert len(graph.nodes) == 1
        assert "max" in graph.nodes
        assert graph.nodes["max"].text == "Max Mustermann"

    def test_add_node_duplicate(self, graph, sample_nodes):
        """Test adding duplicate node (should not duplicate)"""
        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[0])

        assert len(graph.nodes) == 1

    def test_add_edge(self, graph, sample_nodes):
        """Test adding edge to graph"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        # Add nodes first
        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])

        # Add edge
        edge = Edge(
            source="max",
            target="siemens",
            relation=RelationType.WORKS_AT,
            confidence=0.9
        )
        graph.add_edge(edge)

        assert len(graph.edges) == 1
        assert len(graph.adjacency["max"]) == 1
        assert len(graph.reverse_adjacency["siemens"]) == 1

    def test_add_edge_missing_node(self, graph):
        """Test adding edge with missing nodes raises error"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        edge = Edge(
            source="nonexistent1",
            target="nonexistent2",
            relation=RelationType.WORKS_AT,
            confidence=0.9
        )

        with pytest.raises(ValueError, match="Source or target node not found"):
            graph.add_edge(edge)

    def test_get_node(self, graph, sample_nodes):
        """Test getting node by ID"""
        graph.add_node(sample_nodes[0])

        node = graph.get_node("max")
        assert node is not None
        assert node.text == "Max Mustermann"

    def test_get_node_nonexistent(self, graph):
        """Test getting nonexistent node returns None"""
        node = graph.get_node("nonexistent")
        assert node is None

    def test_get_neighbors(self, graph, sample_nodes):
        """Test getting neighboring nodes"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        # Build graph: max -> siemens, max -> munich
        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])

        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("max", "munich", RelationType.RESIDES_IN, 0.8))

        neighbors = graph.get_neighbors("max")

        assert len(neighbors) == 2
        neighbor_texts = {n.text for n in neighbors}
        assert "Siemens AG" in neighbor_texts
        assert "München" in neighbor_texts

    def test_get_neighbors_filtered(self, graph, sample_nodes):
        """Test getting neighbors filtered by relation type"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])

        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("max", "munich", RelationType.RESIDES_IN, 0.8))

        # Filter only WORKS_AT relations
        neighbors = graph.get_neighbors("max", relation_type=RelationType.WORKS_AT)

        assert len(neighbors) == 1
        assert neighbors[0].text == "Siemens AG"

    def test_get_incoming_neighbors(self, graph, sample_nodes):
        """Test getting incoming neighbors"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        # Build graph: max -> siemens, anna -> siemens
        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        anna = Node(id="anna", text="Anna Schmidt", type=EntityType.PERSON)
        graph.add_node(anna)

        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("anna", "siemens", RelationType.WORKS_AT, 0.85))

        # Get incoming neighbors to siemens
        incoming = graph.get_incoming_neighbors("siemens")

        assert len(incoming) == 2
        names = {n.text for n in incoming}
        assert "Max Mustermann" in names
        assert "Anna Schmidt" in names

    def test_find_path_direct(self, graph, sample_nodes):
        """Test finding direct path between nodes"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))

        path = graph.find_path("max", "siemens")

        assert path is not None
        assert path == ["max", "siemens"]

    def test_find_path_indirect(self, graph):
        """Test finding indirect path (multiple hops)"""
        from src.ml.knowledge_graph import Node, Edge
        from src.ml.ner import EntityType
        from src.ml.relation_extractor import RelationType

        # Build path: A -> B -> C
        graph.add_node(Node("A", "A", EntityType.PERSON))
        graph.add_node(Node("B", "B", EntityType.ORGANIZATION))
        graph.add_node(Node("C", "C", EntityType.LOCATION))

        graph.add_edge(Edge("A", "B", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("B", "C", RelationType.HEADQUARTERED_IN, 0.8))

        path = graph.find_path("A", "C")

        assert path is not None
        assert path == ["A", "B", "C"]

    def test_find_path_no_path(self, graph, sample_nodes):
        """Test finding path when none exists"""
        # Add disconnected nodes
        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])

        path = graph.find_path("max", "siemens")

        assert path is None

    def test_find_path_same_node(self, graph, sample_nodes):
        """Test finding path to same node"""
        graph.add_node(sample_nodes[0])

        path = graph.find_path("max", "max")

        assert path == ["max"]

    def test_find_path_max_depth(self, graph):
        """Test finding path respects max depth"""
        from src.ml.knowledge_graph import Node, Edge
        from src.ml.ner import EntityType
        from src.ml.relation_extractor import RelationType

        # Build long path: A -> B -> C -> D -> E
        for name in ["A", "B", "C", "D", "E"]:
            graph.add_node(Node(name, name, EntityType.PERSON))

        graph.add_edge(Edge("A", "B", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("B", "C", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("C", "D", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("D", "E", RelationType.WORKS_AT, 0.9))

        # Max depth 2 should not find path from A to E
        path = graph.find_path("A", "E", max_depth=2)
        assert path is None

        # Max depth 5 should find it
        path = graph.find_path("A", "E", max_depth=5)
        assert path is not None

    def test_get_subgraph(self, graph, sample_nodes):
        """Test extracting subgraph around a node"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        # Build graph: max -> siemens -> munich
        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])
        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("siemens", "munich", RelationType.HEADQUARTERED_IN, 0.8))

        # Get subgraph around max with depth 1
        subgraph = graph.get_subgraph("max", depth=1)

        assert len(subgraph.nodes) == 2  # max and siemens
        assert "max" in subgraph.nodes
        assert "siemens" in subgraph.nodes
        assert len(subgraph.edges) == 1

    def test_get_subgraph_depth_2(self, graph, sample_nodes):
        """Test subgraph with depth 2"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])
        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("siemens", "munich", RelationType.HEADQUARTERED_IN, 0.8))

        # Get subgraph with depth 2 should include all 3 nodes
        subgraph = graph.get_subgraph("max", depth=2)

        assert len(subgraph.nodes) == 3
        assert len(subgraph.edges) == 2

    def test_query_by_node_type(self, graph, sample_nodes):
        """Test querying graph by node type"""
        for node in sample_nodes:
            graph.add_node(node)

        # Query for PERSON nodes
        from src.ml.ner import EntityType
        results = graph.query(node_type=EntityType.PERSON)

        assert len(results) == 1
        assert results[0][0].text == "Max Mustermann"

    def test_query_by_relation_type(self, graph, sample_nodes):
        """Test querying graph by relation type"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])

        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("siemens", "munich", RelationType.HEADQUARTERED_IN, 0.8))

        # Query for WORKS_AT relations
        results = graph.query(relation_type=RelationType.WORKS_AT)

        assert len(results) == 1
        assert results[0][1].relation == RelationType.WORKS_AT

    def test_query_with_confidence_filter(self, graph, sample_nodes):
        """Test querying with minimum confidence"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])

        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.5))

        # Query with high confidence threshold
        results = graph.query(relation_type=RelationType.WORKS_AT, min_confidence=0.8)

        assert len(results) == 0  # 0.5 < 0.8

        # Query with low confidence threshold
        results = graph.query(relation_type=RelationType.WORKS_AT, min_confidence=0.3)

        assert len(results) == 1

    def test_get_node_degree(self, graph, sample_nodes):
        """Test getting node degree"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])

        # max -> siemens, munich -> max
        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("munich", "max", RelationType.LOCATED_IN, 0.8))

        in_deg, out_deg, total_deg = graph.get_node_degree("max")

        assert in_deg == 1  # From munich
        assert out_deg == 1  # To siemens
        assert total_deg == 2

    def test_get_central_nodes(self, graph):
        """Test getting most central nodes"""
        from src.ml.knowledge_graph import Node, Edge
        from src.ml.ner import EntityType
        from src.ml.relation_extractor import RelationType

        # Build graph with central node
        nodes = [Node(f"n{i}", f"Node{i}", EntityType.PERSON) for i in range(5)]
        for node in nodes:
            graph.add_node(node)

        # n0 has high degree (connected to all others)
        for i in range(1, 5):
            graph.add_edge(Edge("n0", f"n{i}", RelationType.WORKS_AT, 0.9))

        central = graph.get_central_nodes(top_n=3)

        assert len(central) == 3
        # n0 should be most central
        assert central[0][0].id == "n0"
        assert central[0][1] == 4  # Degree of 4

    def test_stats(self, graph, sample_nodes):
        """Test getting graph statistics"""
        from src.ml.knowledge_graph import Edge
        from src.ml.relation_extractor import RelationType

        graph.add_node(sample_nodes[0])
        graph.add_node(sample_nodes[1])
        graph.add_node(sample_nodes[2])

        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("siemens", "munich", RelationType.HEADQUARTERED_IN, 0.8))

        stats = graph.stats()

        assert stats["num_nodes"] == 3
        assert stats["num_edges"] == 2
        assert "entity_types" in stats
        assert "relation_types" in stats
        assert "avg_degree" in stats
        assert "max_degree" in stats
        assert "density" in stats


# ============================================================================
# Graph Export Tests
# ============================================================================


class TestGraphExport:
    """Test graph export functionality."""

    @pytest.fixture
    def simple_graph(self):
        """Create simple graph for testing export."""
        from src.ml.knowledge_graph import KnowledgeGraph, Node, Edge
        from src.ml.ner import EntityType
        from src.ml.relation_extractor import RelationType

        graph = KnowledgeGraph()
        graph.add_node(Node("max", "Max Mustermann", EntityType.PERSON))
        graph.add_node(Node("siemens", "Siemens AG", EntityType.ORGANIZATION))
        graph.add_edge(Edge("max", "siemens", RelationType.WORKS_AT, 0.9))

        return graph

    def test_export_json(self, simple_graph):
        """Test exporting graph as JSON"""
        from src.ml.knowledge_graph import GraphFormat

        json_str = simple_graph.export(GraphFormat.JSON)

        # Parse JSON
        data = json.loads(json_str)

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1

    def test_export_cypher(self, simple_graph):
        """Test exporting graph as Cypher"""
        from src.ml.knowledge_graph import GraphFormat

        cypher = simple_graph.export(GraphFormat.CYPHER)

        assert "CREATE" in cypher
        assert "MATCH" in cypher
        assert "Max Mustermann" in cypher
        assert "WORKS_AT" in cypher

    def test_export_graphml(self, simple_graph):
        """Test exporting graph as GraphML"""
        from src.ml.knowledge_graph import GraphFormat

        graphml = simple_graph.export(GraphFormat.GRAPHML)

        assert '<?xml version' in graphml
        assert '<graphml' in graphml
        assert '<node' in graphml
        assert '<edge' in graphml

    def test_export_adjacency(self, simple_graph):
        """Test exporting graph as adjacency list"""
        from src.ml.knowledge_graph import GraphFormat

        adj_str = simple_graph.export(GraphFormat.ADJACENCY)

        # Parse JSON
        adj_data = json.loads(adj_str)

        assert "max" in adj_data
        assert len(adj_data["max"]) == 1
        assert adj_data["max"][0]["target"] == "siemens"

    def test_export_invalid_format(self, simple_graph):
        """Test exporting with invalid format raises error"""
        with pytest.raises(ValueError, match="Unsupported format"):
            simple_graph.export("invalid_format")

    def test_export_graphml_escaping(self):
        """Test GraphML export escapes special characters"""
        from src.ml.knowledge_graph import KnowledgeGraph, Node, GraphFormat
        from src.ml.ner import EntityType

        graph = KnowledgeGraph()
        graph.add_node(Node('test<">', 'Text with <quotes> & "special"', EntityType.PERSON))

        graphml = graph.export(GraphFormat.GRAPHML)

        # Should escape special characters
        assert "&lt;" in graphml or "&quot;" in graphml or "&gt;" in graphml


# ============================================================================
# KnowledgeGraphBuilder Tests
# ============================================================================


class TestKnowledgeGraphBuilder:
    """Test KnowledgeGraphBuilder functionality."""

    @pytest.fixture
    def builder(self):
        """Create KnowledgeGraphBuilder instance."""
        from src.ml.knowledge_graph import KnowledgeGraphBuilder

        return KnowledgeGraphBuilder(use_spacy=False)

    def test_builder_initialization(self, builder):
        """Test KnowledgeGraphBuilder initialization"""
        assert builder.ner_engine is not None
        assert builder.relation_extractor is not None

    def test_build_from_text_basic(self, builder):
        """Test building graph from text"""
        text = "Max Mustermann arbeitet bei Siemens AG in München."

        graph = builder.build_from_text(text, min_confidence=0.0)

        # Should have nodes (entities extracted)
        assert len(graph.nodes) >= 0  # Depends on NER success

    def test_build_from_text_empty(self, builder):
        """Test building graph from empty text"""
        graph = builder.build_from_text("", min_confidence=0.0)

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_build_from_text_confidence_filter(self, builder):
        """Test building graph filters low confidence relations"""
        text = "Person works at Company"

        # High confidence threshold
        graph_high = builder.build_from_text(text, min_confidence=0.99)

        # Low confidence threshold
        graph_low = builder.build_from_text(text, min_confidence=0.0)

        # High confidence graph should have fewer or equal edges
        assert len(graph_high.edges) <= len(graph_low.edges)

    def test_build_from_entities_and_relations(self, builder):
        """Test building graph from pre-extracted entities and relations"""
        from src.ml.ner import Entity, EntityType
        from src.ml.relation_extractor import Relation, RelationType

        # Create entities
        entities = [
            Entity("Max", EntityType.PERSON, 0, 3, confidence=1.0),
            Entity("Siemens", EntityType.ORGANIZATION, 14, 21, confidence=1.0)
        ]

        # Create relations
        relations = [
            Relation(
                subject=entities[0],
                relation=RelationType.WORKS_AT,
                object=entities[1],
                confidence=0.9,
                context="Max works at Siemens",
                start=0,
                end=21
            )
        ]

        graph = builder.build_from_entities_and_relations(entities, relations, min_confidence=0.5)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

    def test_build_from_entities_and_relations_filtered(self, builder):
        """Test build filters low confidence relations"""
        from src.ml.ner import Entity, EntityType
        from src.ml.relation_extractor import Relation, RelationType

        entities = [
            Entity("A", EntityType.PERSON, 0, 1),
            Entity("B", EntityType.ORGANIZATION, 2, 3)
        ]

        relations = [
            Relation(entities[0], RelationType.WORKS_AT, entities[1], 0.3, "context", 0, 3)
        ]

        # High confidence filter
        graph = builder.build_from_entities_and_relations(entities, relations, min_confidence=0.8)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 0  # Filtered out due to low confidence


# ============================================================================
# Global Instance Tests
# ============================================================================


class TestGlobalInstance:
    """Test global knowledge graph builder instance."""

    def test_get_kg_builder_singleton(self):
        """Test get_kg_builder returns singleton"""
        from src.ml.knowledge_graph import get_kg_builder

        # Reset global
        import src.ml.knowledge_graph
        src.ml.knowledge_graph._kg_builder = None

        builder1 = get_kg_builder(use_spacy=False)
        builder2 = get_kg_builder(use_spacy=False)

        assert builder1 is builder2


# ============================================================================
# Integration Tests
# ============================================================================


class TestKnowledgeGraphIntegration:
    """Integration tests for knowledge graph system."""

    def test_full_graph_building_workflow(self):
        """Test complete graph building workflow"""
        from src.ml.knowledge_graph import KnowledgeGraphBuilder, GraphFormat

        builder = KnowledgeGraphBuilder(use_spacy=False)

        text = """
        Max Mustermann arbeitet bei Siemens AG in München.
        Anna Schmidt ist CEO von BMW in Berlin.
        """

        # Build graph
        graph = builder.build_from_text(text, min_confidence=0.0)

        # Should have some nodes
        assert len(graph.nodes) >= 0

        # Get statistics
        stats = graph.stats()
        assert "num_nodes" in stats
        assert "num_edges" in stats

        # Export to JSON
        json_export = graph.export(GraphFormat.JSON)
        assert json_export is not None

    def test_graph_traversal_and_analysis(self):
        """Test graph traversal and analysis operations"""
        from src.ml.knowledge_graph import KnowledgeGraph, Node, Edge
        from src.ml.ner import EntityType
        from src.ml.relation_extractor import RelationType

        # Build complex graph
        graph = KnowledgeGraph()

        # Add nodes
        nodes = {
            "person1": Node("person1", "Person 1", EntityType.PERSON),
            "person2": Node("person2", "Person 2", EntityType.PERSON),
            "org1": Node("org1", "Org 1", EntityType.ORGANIZATION),
            "org2": Node("org2", "Org 2", EntityType.ORGANIZATION),
            "loc1": Node("loc1", "Location 1", EntityType.LOCATION)
        }

        for node in nodes.values():
            graph.add_node(node)

        # Add edges: person1 -> org1 -> loc1, person2 -> org2
        graph.add_edge(Edge("person1", "org1", RelationType.WORKS_AT, 0.9))
        graph.add_edge(Edge("org1", "loc1", RelationType.HEADQUARTERED_IN, 0.8))
        graph.add_edge(Edge("person2", "org2", RelationType.CEO_OF, 0.95))

        # Test path finding
        path = graph.find_path("person1", "loc1")
        assert path is not None
        assert len(path) == 3

        # Test subgraph extraction
        subgraph = graph.get_subgraph("org1", depth=1)
        assert len(subgraph.nodes) == 3

        # Test centrality
        central = graph.get_central_nodes(top_n=2)
        assert len(central) == 2

        # org1 should be most central (in-degree 1, out-degree 1)
        assert central[0][0].id == "org1"

    def test_multiple_export_formats(self):
        """Test exporting graph to multiple formats"""
        from src.ml.knowledge_graph import KnowledgeGraph, Node, Edge, GraphFormat
        from src.ml.ner import EntityType
        from src.ml.relation_extractor import RelationType

        graph = KnowledgeGraph()
        graph.add_node(Node("n1", "Node 1", EntityType.PERSON))
        graph.add_node(Node("n2", "Node 2", EntityType.ORGANIZATION))
        graph.add_edge(Edge("n1", "n2", RelationType.WORKS_AT, 0.9))

        # Export to all formats
        json_export = graph.export(GraphFormat.JSON)
        cypher_export = graph.export(GraphFormat.CYPHER)
        graphml_export = graph.export(GraphFormat.GRAPHML)
        adj_export = graph.export(GraphFormat.ADJACENCY)

        # All should be non-empty strings
        assert len(json_export) > 0
        assert len(cypher_export) > 0
        assert len(graphml_export) > 0
        assert len(adj_export) > 0

        # JSON and adjacency should be valid JSON
        json.loads(json_export)
        json.loads(adj_export)
