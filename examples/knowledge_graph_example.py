"""
Knowledge Graph Examples

Demonstrates how to build and query knowledge graphs from text.
"""

from src.ml.knowledge_graph import (
    KnowledgeGraphBuilder,
    KnowledgeGraph,
    GraphFormat,
    Node,
    Edge
)
from src.ml.ner import EntityType
from src.ml.relation_extractor import RelationType


def example_basic_graph():
    """Build a basic knowledge graph from text"""
    print("\n=== Basic Knowledge Graph ===" )

    builder = KnowledgeGraphBuilder(use_spacy=True, spacy_model="de_core_news_sm")

    text = """
    Max Mustermann arbeitet bei der Siemens AG in München.
    Anna Schmidt ist Geschäftsführerin der DataCorp AG.
    DataCorp AG hat ihren Hauptsitz in Berlin.
    """

    graph = builder.build_from_text(text)

    print(f"Graph Statistics:")
    stats = graph.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print(f"\nNodes ({len(graph.nodes)}):")
    for node in graph.nodes.values():
        print(f"  • {node.text} ({node.type.value})")

    print(f"\nEdges ({len(graph.edges)}):")
    for edge in graph.edges:
        print(f"  • {edge.source} --[{edge.relation.value}]--> {edge.target}")


def example_contract_graph():
    """Build knowledge graph from contract"""
    print("\n=== Contract Knowledge Graph ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    contract = """
    DIENSTLEISTUNGSVERTRAG

    zwischen

    TechSolutions GmbH mit Sitz in München,
    vertreten durch den Geschäftsführer Max Mustermann,

    und

    DataCorp AG mit Hauptsitz in Berlin,
    vertreten durch die Vorständin Anna Schmidt.

    Die TechSolutions GmbH, gegründet von Max Mustermann im Jahr 2020,
    erbringt IT-Dienstleistungen für die DataCorp AG.
    """

    graph = builder.build_from_text(contract, min_confidence=0.6)

    print(f"Contract entities: {len(graph.nodes)}")
    print(f"Contract relations: {len(graph.edges)}")

    # Find CEOs
    print("\nCEO Relations:")
    ceo_results = graph.query(relation_type=RelationType.CEO_OF)
    for source, edge, target in ceo_results:
        print(f"  • {source.text} is CEO of {target.text}")

    # Find locations
    print("\nLocation Relations:")
    location_results = graph.query(relation_type=RelationType.HEADQUARTERED_IN)
    for source, edge, target in location_results:
        print(f"  • {source.text} headquartered in {target.text}")


def example_graph_traversal():
    """Graph traversal and path finding"""
    print("\n=== Graph Traversal ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei TechSolutions GmbH.
    TechSolutions GmbH hat ihren Sitz in München.
    München liegt in Deutschland.
    Anna Schmidt arbeitet bei TechSolutions GmbH.
    """

    graph = builder.build_from_text(text)

    # Find neighbors
    print("\nNeighbors of 'TechSolutions GmbH':")
    neighbors = graph.get_neighbors("TechSolutions GmbH")
    for neighbor in neighbors:
        print(f"  • {neighbor.text} ({neighbor.type.value})")

    # Find incoming neighbors (who works at TechSolutions)
    print("\nWho works at TechSolutions GmbH:")
    incoming = graph.get_incoming_neighbors("TechSolutions GmbH")
    for node in incoming:
        print(f"  • {node.text}")

    # Find path
    if "Max Mustermann" in graph.nodes and "Deutschland" in graph.nodes:
        path = graph.find_path("Max Mustermann", "Deutschland")
        if path:
            print(f"\nPath from Max Mustermann to Deutschland:")
            print(f"  {' → '.join(path)}")


def example_subgraph_extraction():
    """Extract subgraph around entity"""
    print("\n=== Subgraph Extraction ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    TechSolutions GmbH hat ihren Sitz in München.
    Anna Schmidt arbeitet bei TechSolutions GmbH.
    Tom Weber arbeitet bei DataCorp AG.
    DataCorp AG hat ihren Sitz in Berlin.
    """

    graph = builder.build_from_text(text)

    print(f"Full graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Extract subgraph around TechSolutions
    subgraph = graph.get_subgraph("TechSolutions GmbH", depth=1)

    print(f"\nSubgraph around 'TechSolutions GmbH':")
    print(f"  Nodes: {len(subgraph.nodes)}")
    for node in subgraph.nodes.values():
        print(f"    • {node.text}")

    print(f"  Edges: {len(subgraph.edges)}")
    for edge in subgraph.edges:
        print(f"    • {edge.source} --[{edge.relation.value}]--> {edge.target}")


def example_centrality_analysis():
    """Analyze node centrality"""
    print("\n=== Centrality Analysis ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    Max Mustermann gründete TechSolutions GmbH.
    Max Mustermann wohnt in München.
    TechSolutions GmbH hat ihren Sitz in München.
    Anna Schmidt arbeitet bei TechSolutions GmbH.
    Tom Weber arbeitet bei TechSolutions GmbH.
    DataCorp AG ist Kunde von TechSolutions GmbH.
    """

    graph = builder.build_from_text(text)

    # Get central nodes
    central_nodes = graph.get_central_nodes(top_n=5)

    print("Most central nodes (by degree):")
    for node, degree in central_nodes:
        in_deg, out_deg, total_deg = graph.get_node_degree(node.id)
        print(f"  • {node.text}: {total_deg} connections (in: {in_deg}, out: {out_deg})")


def example_querying():
    """Advanced graph querying"""
    print("\n=== Graph Querying ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei Siemens AG.
    Anna Schmidt ist Geschäftsführerin der DataCorp AG.
    Tom Weber arbeitet bei TechSolutions GmbH.
    Siemens AG hat ihren Sitz in München.
    DataCorp AG hat ihren Sitz in Berlin.
    """

    graph = builder.build_from_text(text)

    # Query all PERSON entities
    print("All persons:")
    person_results = graph.query(node_type=EntityType.PERSON)
    for node, _, _ in person_results:
        print(f"  • {node.text}")

    # Query all employment relations
    print("\nAll employment relations:")
    work_results = graph.query(relation_type=RelationType.WORKS_AT)
    for source, edge, target in work_results:
        print(f"  • {source.text} works at {target.text} (confidence: {edge.confidence:.2f})")

    # Query organizations in specific location
    print("\nOrganizations:")
    org_results = graph.query(node_type=EntityType.ORGANIZATION)
    for node, _, _ in org_results:
        # Find location
        neighbors = graph.get_neighbors(node.text, relation_type=RelationType.HEADQUARTERED_IN)
        if neighbors:
            print(f"  • {node.text} in {neighbors[0].text}")
        else:
            print(f"  • {node.text}")


def example_neo4j_export():
    """Export to Neo4j Cypher format"""
    print("\n=== Neo4j Export ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    TechSolutions GmbH hat ihren Sitz in München.
    """

    graph = builder.build_from_text(text)

    # Export to Cypher
    cypher = graph.export(GraphFormat.CYPHER)

    print("Neo4j Cypher queries:")
    print(cypher)
    print("\nTo import into Neo4j:")
    print("  1. Start Neo4j: neo4j console")
    print("  2. Open browser: http://localhost:7474")
    print("  3. Run the Cypher queries above")


def example_json_export():
    """Export to JSON format"""
    print("\n=== JSON Export ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei Siemens AG.
    Siemens AG hat ihren Sitz in München.
    """

    graph = builder.build_from_text(text)

    # Export to JSON
    json_data = graph.export(GraphFormat.JSON)

    print("JSON export:")
    print(json_data)


def example_graphml_export():
    """Export to GraphML format"""
    print("\n=== GraphML Export ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei Siemens AG in München.
    """

    graph = builder.build_from_text(text)

    # Export to GraphML
    graphml = graph.export(GraphFormat.GRAPHML)

    print("GraphML export:")
    print(graphml)
    print("\nCompatible with: Gephi, yEd, Cytoscape, NetworkX")


def example_multi_document_graph():
    """Build graph from multiple documents"""
    print("\n=== Multi-Document Graph ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    documents = [
        "Max Mustermann ist Geschäftsführer der TechSolutions GmbH.",
        "TechSolutions GmbH wurde 2020 gegründet.",
        "TechSolutions GmbH hat ihren Sitz in München.",
        "Anna Schmidt arbeitet bei TechSolutions GmbH.",
        "DataCorp AG ist ein Kunde von TechSolutions GmbH."
    ]

    # Build combined graph
    combined_graph = KnowledgeGraph()

    for doc in documents:
        doc_graph = builder.build_from_text(doc)

        # Merge into combined graph
        for node in doc_graph.nodes.values():
            combined_graph.add_node(node)

        for edge in doc_graph.edges:
            combined_graph.add_edge(edge)

    print(f"Combined graph from {len(documents)} documents:")
    stats = combined_graph.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Find central entity
    central = combined_graph.get_central_nodes(top_n=1)
    if central:
        node, degree = central[0]
        print(f"\nMost central entity: {node.text} ({degree} connections)")


def example_graph_statistics():
    """Comprehensive graph statistics"""
    print("\n=== Graph Statistics ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    Max Mustermann gründete TechSolutions GmbH im Jahr 2020.
    TechSolutions GmbH hat ihren Sitz in München.
    Anna Schmidt arbeitet bei TechSolutions GmbH.
    Tom Weber arbeitet bei TechSolutions GmbH.
    DataCorp AG mit Sitz in Berlin ist Kunde von TechSolutions GmbH.
    """

    graph = builder.build_from_text(text)

    stats = graph.stats()

    print("Graph Statistics:")
    print(f"  Nodes: {stats['num_nodes']}")
    print(f"  Edges: {stats['num_edges']}")
    print(f"  Average degree: {stats['avg_degree']}")
    print(f"  Max degree: {stats['max_degree']}")
    print(f"  Graph density: {stats['density']}")

    print("\nEntity type distribution:")
    for entity_type, count in stats['entity_types'].items():
        print(f"  • {entity_type}: {count}")

    print("\nRelation type distribution:")
    for relation_type, count in stats['relation_types'].items():
        print(f"  • {relation_type}: {count}")


def example_confidence_filtering():
    """Filter relations by confidence"""
    print("\n=== Confidence Filtering ===")

    builder = KnowledgeGraphBuilder(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei Siemens AG.
    Anna Schmidt könnte bei DataCorp AG tätig sein.
    Tom Weber ist definitiv Mitarbeiter der TechSolutions GmbH.
    """

    # High confidence threshold
    print("High confidence graph (≥0.8):")
    graph_high = builder.build_from_text(text, min_confidence=0.8)
    print(f"  Edges: {len(graph_high.edges)}")
    for edge in graph_high.edges:
        print(f"    • {edge.source} → {edge.target} ({edge.confidence:.2f})")

    # Low confidence threshold
    print("\nLow confidence graph (≥0.5):")
    graph_low = builder.build_from_text(text, min_confidence=0.5)
    print(f"  Edges: {len(graph_low.edges)}")
    for edge in graph_low.edges:
        print(f"    • {edge.source} → {edge.target} ({edge.confidence:.2f})")


def main():
    """Run all knowledge graph examples"""
    print("=" * 70)
    print("Knowledge Graph Examples")
    print("=" * 70)

    print("\nNOTE: These examples require spaCy models:")
    print("  German: python -m spacy download de_core_news_sm")
    print("  English: python -m spacy download en_core_web_sm")
    print()

    try:
        example_basic_graph()
        example_contract_graph()
        example_graph_traversal()
        example_subgraph_extraction()
        example_centrality_analysis()
        example_querying()
        example_neo4j_export()
        example_json_export()
        example_graphml_export()
        example_multi_document_graph()
        example_graph_statistics()
        example_confidence_filtering()

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure spaCy and language models are installed:")
        print("  pip install spacy")
        print("  python -m spacy download de_core_news_sm")
        print("  python -m spacy download en_core_web_sm")

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
