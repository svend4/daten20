#!/usr/bin/env python3
"""
Document Applications Integration Examples
===========================================

Examples demonstrating how to use all document processing applications
programmatically and in combination.

Applications covered:
1. Document Processor CLI (doc-processor.py)
2. Document Dashboard (doc-dashboard.py)
3. Document Intelligence API (doc-api-server.py)
4. Batch Document Processor (doc-batch-processor.py)
5. Document Search & Discovery (doc-search.py)

Author: Document Management System
Version: 1.0.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import application components
from src.core.parser import DocumentParser
from src.core.database import DocumentDatabase
from src.ml.ner import NEREngine, EntityType
from src.ml.classifier import TfidfSVMClassifier
from src.ml.relation_extractor import RelationExtractor
from src.ml.knowledge_graph import KnowledgeGraphBuilder, GraphFormat


def example_1_single_document_processing():
    """
    Example 1: Process a single document with full analysis pipeline
    Demonstrates: CLI functionality
    """
    print("\n" + "=" * 70)
    print("Example 1: Single Document Processing")
    print("=" * 70)

    # Sample document text
    sample_text = """
    Arbeitsvertrag

    Zwischen der TechSolutions GmbH mit Sitz in München (Arbeitgeber)
    und Max Mustermann, wohnhaft in Berlin (Arbeitnehmer),
    wird folgender Arbeitsvertrag geschlossen:

    Herr Max Mustermann wird ab dem 01.01.2024 als Senior Developer
    bei der TechSolutions GmbH eingestellt.

    Das monatliche Bruttogehalt beträgt 5.500,00 EUR.

    München, den 15.12.2023
    """

    # Initialize components
    parser = DocumentParser()
    ner_engine = NEREngine(use_spacy=True)
    classifier = TfidfSVMClassifier()
    relation_extractor = RelationExtractor(use_spacy=True)
    graph_builder = KnowledgeGraphBuilder(use_spacy=True)

    print("\n1. Extract entities...")
    entities = ner_engine.extract_entities(sample_text)
    print(f"   Found {len(entities)} entities:")
    for entity in entities[:5]:  # Show first 5
        print(f"   - {entity.text:20} ({entity.type.value:15}) confidence: {entity.confidence:.2f}")

    print("\n2. Classify document...")
    classification = classifier.predict(sample_text)
    print(f"   Category: {getattr(classification, 'category', 'UNKNOWN')}")
    print(f"   Confidence: {getattr(classification, 'confidence', 0.0):.2%}")

    print("\n3. Extract relations...")
    relations = relation_extractor.extract_relations(sample_text)
    print(f"   Found {len(relations)} relations:")
    for relation in relations[:3]:  # Show first 3
        print(f"   - {relation.source_entity} --[{relation.relation_type.value}]--> {relation.target_entity}")
        print(f"     Confidence: {relation.confidence:.2f}")

    print("\n4. Build knowledge graph...")
    graph = graph_builder.build_from_text(sample_text)
    stats = graph.stats()
    print(f"   Nodes: {stats['num_nodes']}")
    print(f"   Edges: {stats['num_edges']}")
    print(f"   Entity types: {', '.join(stats['entity_types'])}")
    print(f"   Relation types: {', '.join(stats['relation_types'])}")

    print("\n5. Export knowledge graph...")
    # JSON export
    json_graph = json.loads(graph.export(GraphFormat.JSON))
    print(f"   JSON export: {len(json_graph['nodes'])} nodes, {len(json_graph['edges'])} edges")

    # Neo4j Cypher export
    cypher = graph.export(GraphFormat.CYPHER)
    print(f"   Cypher export: {len(cypher.splitlines())} statements")

    return {
        "entities": entities,
        "classification": classification,
        "relations": relations,
        "knowledge_graph": graph
    }


def example_2_batch_processing_simulation():
    """
    Example 2: Simulate batch processing workflow
    Demonstrates: Batch processor functionality
    """
    print("\n" + "=" * 70)
    print("Example 2: Batch Processing Workflow")
    print("=" * 70)

    # Sample documents
    documents = [
        {
            "filename": "contract_001.pdf",
            "text": "Max Mustermann arbeitet bei Siemens AG in München."
        },
        {
            "filename": "invoice_002.pdf",
            "text": "Rechnung Nr. 12345 für Dienstleistungen im Dezember 2023. Betrag: 1.500,00 EUR."
        },
        {
            "filename": "report_003.pdf",
            "text": "Jahresbericht 2023 der TechCorp AG. CEO Anna Schmidt präsentiert die Ergebnisse."
        }
    ]

    # Initialize components
    ner_engine = NEREngine(use_spacy=True)
    classifier = TfidfSVMClassifier()

    print(f"\nProcessing {len(documents)} documents...")

    results = []
    total_entities = 0
    total_relations = 0

    for i, doc in enumerate(documents, 1):
        print(f"\n[{i}/{len(documents)}] Processing: {doc['filename']}")

        # Extract entities
        entities = ner_engine.extract_entities(doc['text'])
        total_entities += len(entities)
        print(f"   Entities: {len(entities)}")

        # Classify
        classification = classifier.predict(doc['text'])
        print(f"   Category: {getattr(classification, 'category', 'UNKNOWN')}")

        # Store result
        results.append({
            "filename": doc["filename"],
            "entity_count": len(entities),
            "category": str(getattr(classification, 'category', 'UNKNOWN')),
            "confidence": getattr(classification, 'confidence', 0.0)
        })

    # Summary
    print("\n" + "-" * 70)
    print("Batch Processing Summary:")
    print(f"  Total documents: {len(documents)}")
    print(f"  Total entities: {total_entities}")
    print(f"  Avg entities/doc: {total_entities / len(documents):.1f}")

    return results


def example_3_search_and_discovery():
    """
    Example 3: Document search and discovery
    Demonstrates: Search engine functionality
    """
    print("\n" + "=" * 70)
    print("Example 3: Search and Discovery")
    print("=" * 70)

    # Sample document collection
    documents = [
        {
            "id": 1,
            "text": "Arbeitsvertrag zwischen Max Mustermann und Siemens AG. München, 2024.",
            "entities": [
                {"text": "Max Mustermann", "type": "PERSON"},
                {"text": "Siemens AG", "type": "ORGANIZATION"},
                {"text": "München", "type": "LOCATION"}
            ],
            "relations": [
                {"source": "Max Mustermann", "relation": "WORKS_AT", "target": "Siemens AG"}
            ]
        },
        {
            "id": 2,
            "text": "Rechnung für Softwareentwicklung. TechCorp AG, Berlin. Betrag: 5.000 EUR.",
            "entities": [
                {"text": "TechCorp AG", "type": "ORGANIZATION"},
                {"text": "Berlin", "type": "LOCATION"}
            ],
            "relations": []
        },
        {
            "id": 3,
            "text": "Anna Schmidt ist CEO der TechCorp AG mit Sitz in Berlin.",
            "entities": [
                {"text": "Anna Schmidt", "type": "PERSON"},
                {"text": "TechCorp AG", "type": "ORGANIZATION"},
                {"text": "Berlin", "type": "LOCATION"}
            ],
            "relations": [
                {"source": "Anna Schmidt", "relation": "CEO_OF", "target": "TechCorp AG"},
                {"source": "TechCorp AG", "relation": "HEADQUARTERED_IN", "target": "Berlin"}
            ]
        }
    ]

    print("\n1. Text search for 'Vertrag'...")
    matches = [doc for doc in documents if "Vertrag" in doc["text"] or "vertrag" in doc["text"].lower()]
    print(f"   Found {len(matches)} documents")
    for doc in matches:
        print(f"   - Document {doc['id']}: {doc['text'][:50]}...")

    print("\n2. Entity search for 'TechCorp AG'...")
    matches = [
        doc for doc in documents
        if any(e["text"] == "TechCorp AG" for e in doc.get("entities", []))
    ]
    print(f"   Found {len(matches)} documents")
    for doc in matches:
        print(f"   - Document {doc['id']}")

    print("\n3. Relation search for CEO_OF...")
    matches = [
        doc for doc in documents
        if any(r["relation"] == "CEO_OF" for r in doc.get("relations", []))
    ]
    print(f"   Found {len(matches)} documents")
    for doc in matches:
        ceo_relations = [r for r in doc["relations"] if r["relation"] == "CEO_OF"]
        for rel in ceo_relations:
            print(f"   - {rel['source']} is CEO of {rel['target']}")

    print("\n4. Find documents about specific location (Berlin)...")
    matches = [
        doc for doc in documents
        if any(e["text"] == "Berlin" and e["type"] == "LOCATION" for e in doc.get("entities", []))
    ]
    print(f"   Found {len(matches)} documents about Berlin")

    return documents


def example_4_knowledge_graph_queries():
    """
    Example 4: Knowledge graph construction and querying
    Demonstrates: Knowledge graph capabilities
    """
    print("\n" + "=" * 70)
    print("Example 4: Knowledge Graph Queries")
    print("=" * 70)

    # Sample text with multiple entities and relations
    sample_text = """
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    TechSolutions GmbH hat ihren Sitz in München.
    Anna Schmidt arbeitet als Senior Developer bei TechSolutions GmbH.
    Die Firma wurde von Max Mustermann im Jahr 2020 gegründet.
    """

    print("\n1. Building knowledge graph from text...")
    graph_builder = KnowledgeGraphBuilder(use_spacy=True)
    graph = graph_builder.build_from_text(sample_text)

    stats = graph.stats()
    print(f"   Nodes: {stats['num_nodes']}")
    print(f"   Edges: {stats['num_edges']}")

    print("\n2. Query: Find all persons...")
    persons = graph.query(node_type=EntityType.PERSON)
    print(f"   Found {len(persons)} persons:")
    for node in persons:
        print(f"   - {node.text}")

    print("\n3. Query: Find all WORKS_AT relations...")
    from src.ml.relation_extractor import RelationType
    works_at_relations = graph.query(relation_type=RelationType.WORKS_AT)
    print(f"   Found {len(works_at_relations)} WORKS_AT relations:")
    for edge in works_at_relations:
        source = graph.nodes[edge.source_id]
        target = graph.nodes[edge.target_id]
        print(f"   - {source.text} --[WORKS_AT]--> {target.text}")

    print("\n4. Find path between entities...")
    path = graph.find_path("Max Mustermann", "München")
    if path:
        print(f"   Path found: {' -> '.join(path)}")
    else:
        print("   No path found")

    print("\n5. Get neighbors of 'TechSolutions GmbH'...")
    neighbors = graph.get_neighbors("TechSolutions GmbH")
    print(f"   Found {len(neighbors)} neighbors:")
    for neighbor_id in neighbors:
        neighbor = graph.nodes[neighbor_id]
        print(f"   - {neighbor.text} ({neighbor.entity_type.value})")

    print("\n6. Export to Neo4j Cypher...")
    cypher = graph.export(GraphFormat.CYPHER)
    print(f"   Generated {len(cypher.splitlines())} Cypher statements")
    print("\n   Sample Cypher (first 5 lines):")
    for line in cypher.splitlines()[:5]:
        print(f"   {line}")

    return graph


def example_5_api_client():
    """
    Example 5: API client usage
    Demonstrates: How to interact with the API programmatically
    """
    print("\n" + "=" * 70)
    print("Example 5: API Client Usage")
    print("=" * 70)

    print("\nNOTE: This example shows how to use the API client.")
    print("To run this example, first start the API server:")
    print("  python doc-api-server.py")
    print()

    # Example API client code (requires requests library)
    example_code = '''
import requests
import json

# API endpoint
API_BASE = "http://localhost:8000"

# 1. Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{API_BASE}/api/v1/documents",
        files={"file": f},
        params={"build_graph": True}
    )
    result = response.json()
    print(f"Document processed: {result['document_id']}")

# 2. Extract entities from text
response = requests.post(
    f"{API_BASE}/api/v1/extract/entities",
    json={"text": "Max Mustermann arbeitet bei Siemens AG."}
)
entities = response.json()
print(f"Extracted {len(entities)} entities")

# 3. Classify document
response = requests.post(
    f"{API_BASE}/api/v1/classify",
    json={"text": "Rechnung Nr. 12345..."}
)
classification = response.json()
print(f"Category: {classification['category']}")

# 4. Build knowledge graph
response = requests.post(
    f"{API_BASE}/api/v1/graph/build",
    json={"text": "Max ist CEO von TechCorp."},
    params={"export_format": "json"}
)
graph = response.json()
print(f"Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

# 5. Health check
response = requests.get(f"{API_BASE}/api/v1/health")
health = response.json()
print(f"API Status: {health['status']}")
'''

    print("Example API client code:")
    print("-" * 70)
    print(example_code)
    print("-" * 70)


def example_6_complete_workflow():
    """
    Example 6: Complete document processing workflow
    Demonstrates: Integration of all components
    """
    print("\n" + "=" * 70)
    print("Example 6: Complete Document Processing Workflow")
    print("=" * 70)

    # Sample contract document
    contract_text = """
    ARBEITSVERTRAG

    zwischen
    TechSolutions GmbH, München (Arbeitgeber)
    vertreten durch Geschäftsführer Max Mustermann

    und
    Anna Schmidt, Berlin (Arbeitnehmerin)

    wird folgender Arbeitsvertrag geschlossen:

    § 1 Beginn und Art der Tätigkeit
    Frau Anna Schmidt wird ab dem 01.02.2024 als Senior Software Engineer eingestellt.
    Der Arbeitsort ist München.

    § 2 Vergütung
    Das Bruttomonatsgehalt beträgt 6.500,00 EUR.

    § 3 Arbeitszeit
    Die regelmäßige wöchentliche Arbeitszeit beträgt 40 Stunden.

    München, den 15.01.2024

    _______________________          _______________________
    Max Mustermann                   Anna Schmidt
    (TechSolutions GmbH)            (Arbeitnehmerin)
    """

    print("\n🔄 Complete Processing Pipeline:")
    print("=" * 70)

    # Step 1: Initialize all components
    print("\n[1/6] Initializing components...")
    ner_engine = NEREngine(use_spacy=True)
    classifier = TfidfSVMClassifier()
    relation_extractor = RelationExtractor(use_spacy=True)
    graph_builder = KnowledgeGraphBuilder(use_spacy=True)
    print("   ✓ All components initialized")

    # Step 2: Extract entities
    print("\n[2/6] Extracting entities...")
    entities = ner_engine.extract_entities(contract_text)
    print(f"   ✓ Found {len(entities)} entities")

    # Group entities by type
    entities_by_type = {}
    for entity in entities:
        entity_type = entity.type.value
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity.text)

    for entity_type, texts in entities_by_type.items():
        print(f"     {entity_type}: {', '.join(set(texts))}")

    # Step 3: Classify document
    print("\n[3/6] Classifying document...")
    classification = classifier.predict(contract_text)
    category = getattr(classification, 'category', 'UNKNOWN')
    confidence = getattr(classification, 'confidence', 0.0)
    print(f"   ✓ Category: {category}")
    print(f"     Confidence: {confidence:.2%}")

    # Step 4: Extract relations
    print("\n[4/6] Extracting relations...")
    relations = relation_extractor.extract_relations(contract_text)
    print(f"   ✓ Found {len(relations)} relations")
    for relation in relations[:5]:  # Show first 5
        print(f"     {relation.source_entity} --[{relation.relation_type.value}]--> {relation.target_entity}")

    # Step 5: Build knowledge graph
    print("\n[5/6] Building knowledge graph...")
    graph = graph_builder.build_from_text(contract_text)
    stats = graph.stats()
    print(f"   ✓ Graph built successfully")
    print(f"     Nodes: {stats['num_nodes']}")
    print(f"     Edges: {stats['num_edges']}")
    print(f"     Density: {stats['density']:.3f}")

    # Step 6: Generate comprehensive report
    print("\n[6/6] Generating comprehensive report...")
    report = {
        "document_type": "Contract",
        "processed_at": "2026-01-11T12:00:00",
        "classification": {
            "category": str(category),
            "confidence": confidence
        },
        "statistics": {
            "text_length": len(contract_text),
            "word_count": len(contract_text.split()),
            "entity_count": len(entities),
            "relation_count": len(relations),
            "graph_nodes": stats['num_nodes'],
            "graph_edges": stats['num_edges']
        },
        "entities_by_type": {
            k: list(set(v)) for k, v in entities_by_type.items()
        },
        "key_relations": [
            {
                "source": r.source_entity,
                "relation": r.relation_type.value,
                "target": r.target_entity,
                "confidence": r.confidence
            }
            for r in relations
        ],
        "knowledge_graph": json.loads(graph.export(GraphFormat.JSON))
    }

    print("   ✓ Report generated successfully")
    print(f"     Report size: {len(json.dumps(report))} bytes")

    # Save report
    output_file = "contract_analysis_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"     Saved to: {output_file}")

    print("\n" + "=" * 70)
    print("✅ Complete workflow finished successfully!")
    print("=" * 70)

    return report


def main():
    """Run all examples."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        Document Applications Integration Examples                 ║
║        Version 1.0.0                                               ║
║                                                                    ║
║  This script demonstrates all document processing applications    ║
║  and how to use them together.                                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Run all examples
        example_1_single_document_processing()
        example_2_batch_processing_simulation()
        example_3_search_and_discovery()
        example_4_knowledge_graph_queries()
        example_5_api_client()
        example_6_complete_workflow()

        print("\n" + "=" * 70)
        print("🎉 All examples completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Try the command-line tools: doc-processor.py, doc-search.py")
        print("  2. Start the dashboard: python doc-dashboard.py")
        print("  3. Start the API server: python doc-api-server.py")
        print("  4. Process documents in batch: python doc-batch-processor.py")
        print("\nFor more information, see: docs/DOCUMENT_APPLICATIONS_GUIDE.md")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
