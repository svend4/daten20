# Knowledge Graph Guide

Comprehensive guide for building and querying knowledge graphs in Daten20.

## Overview

The Knowledge Graph module constructs graph-based knowledge representations from unstructured text by combining:

1. **Named Entity Recognition (NER)** - Extracts entities (persons, organizations, locations)
2. **Relation Extraction** - Identifies relationships between entities
3. **Graph Construction** - Builds directed graph with entities as nodes and relations as edges
4. **Graph Analysis** - Provides querying, traversal, and analytics capabilities
5. **Export** - Supports multiple formats (JSON, Neo4j Cypher, GraphML)

### Example

**Input:**
```
Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
TechSolutions GmbH hat ihren Sitz in München.
```

**Output Knowledge Graph:**
```
Nodes:
  • Max Mustermann (PERSON)
  • TechSolutions GmbH (ORGANIZATION)
  • München (LOCATION)

Edges:
  • Max Mustermann --[CEO_OF]--> TechSolutions GmbH
  • TechSolutions GmbH --[HEADQUARTERED_IN]--> München
```

## Installation

### Basic Requirements
```bash
pip install spacy
python -m spacy download de_core_news_sm  # German
python -m spacy download en_core_web_sm   # English
```

### Optional (for Neo4j integration)
```bash
pip install neo4j
```

## Quick Start

### Build Graph from Text

```python
from src.ml.knowledge_graph import KnowledgeGraphBuilder

# Create builder
builder = KnowledgeGraphBuilder(use_spacy=True, spacy_model="de_core_news_sm")

# Build graph from text
text = """
Max Mustermann arbeitet bei Siemens AG in München.
Anna Schmidt ist Geschäftsführerin der DataCorp AG.
"""

graph = builder.build_from_text(text)

# View nodes
print(f"Nodes: {len(graph.nodes)}")
for node in graph.nodes.values():
    print(f"  • {node.text} ({node.type.value})")

# View edges
print(f"Edges: {len(graph.edges)}")
for edge in graph.edges:
    print(f"  • {edge.source} --[{edge.relation.value}]--> {edge.target}")
```

### Query Graph

```python
from src.ml.relation_extractor import RelationType
from src.ml.ner import EntityType

# Find all persons
persons = graph.query(node_type=EntityType.PERSON)
for node, _, _ in persons:
    print(f"Person: {node.text}")

# Find employment relations
employment = graph.query(relation_type=RelationType.WORKS_AT)
for source, edge, target in employment:
    print(f"{source.text} works at {target.text}")
```

### Export to Neo4j

```python
from src.ml.knowledge_graph import GraphFormat

# Export as Cypher queries
cypher = graph.export(GraphFormat.CYPHER)
print(cypher)

# Import into Neo4j:
# 1. Start Neo4j
# 2. Run the Cypher queries in Neo4j Browser
```

## Core Classes

### `KnowledgeGraph`

Main graph data structure.

```python
class KnowledgeGraph:
    nodes: Dict[str, Node]              # Node ID -> Node
    edges: List[Edge]                   # List of edges
    adjacency: Dict[str, List[Edge]]    # Outgoing edges
    reverse_adjacency: Dict[str, List[Edge]]  # Incoming edges
```

**Methods:**
- `add_node(node)` - Add node to graph
- `add_edge(edge)` - Add edge to graph
- `get_neighbors(node_id)` - Get outgoing neighbors
- `get_incoming_neighbors(node_id)` - Get incoming neighbors
- `find_path(start, end)` - Find shortest path (BFS)
- `get_subgraph(node_id, depth)` - Extract subgraph
- `query(node_type, relation_type, min_confidence)` - Query graph
- `get_central_nodes(top_n)` - Get most central nodes
- `export(format)` - Export graph
- `stats()` - Get graph statistics

### `Node`

Represents an entity in the graph.

```python
@dataclass
class Node:
    id: str                    # Unique identifier
    text: str                  # Entity text
    type: EntityType           # PERSON, ORGANIZATION, LOCATION
    properties: Dict[str, Any] # Additional properties
```

### `Edge`

Represents a relation in the graph.

```python
@dataclass
class Edge:
    source: str                # Source node ID
    target: str                # Target node ID
    relation: RelationType     # Relation type
    confidence: float          # Confidence score (0.0-1.0)
    properties: Dict[str, Any] # Additional properties
```

### `KnowledgeGraphBuilder`

Builds graphs from text.

```python
class KnowledgeGraphBuilder:
    def build_from_text(text: str, min_confidence: float = 0.5) -> KnowledgeGraph
    def build_from_entities_and_relations(entities, relations, min_confidence) -> KnowledgeGraph
```

## Graph Construction

### From Text

Automatically extracts entities and relations:

```python
builder = KnowledgeGraphBuilder(use_spacy=True)

text = """
Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
TechSolutions GmbH hat ihren Sitz in München.
"""

graph = builder.build_from_text(text, min_confidence=0.6)
```

### From Pre-extracted Entities/Relations

Use when you already have entities and relations:

```python
from src.ml.ner import NEREngine
from src.ml.relation_extractor import RelationExtractor

# Extract separately
ner = NEREngine(use_spacy=True)
extractor = RelationExtractor(use_spacy=True)

entities = ner.extract_entities(text)
relations = extractor.extract_relations(text)

# Build graph
builder = KnowledgeGraphBuilder()
graph = builder.build_from_entities_and_relations(entities, relations)
```

### From Multiple Documents

Merge graphs from multiple sources:

```python
from src.ml.knowledge_graph import KnowledgeGraph

documents = [
    "Max Mustermann arbeitet bei Siemens AG.",
    "Siemens AG hat ihren Sitz in München.",
    "Anna Schmidt ist CEO von DataCorp AG."
]

combined_graph = KnowledgeGraph()

for doc in documents:
    doc_graph = builder.build_from_text(doc)

    # Merge nodes
    for node in doc_graph.nodes.values():
        combined_graph.add_node(node)

    # Merge edges
    for edge in doc_graph.edges:
        combined_graph.add_edge(edge)
```

## Graph Querying

### Query by Node Type

```python
from src.ml.ner import EntityType

# Find all persons
persons = graph.query(node_type=EntityType.PERSON)
for node, _, _ in persons:
    print(f"Person: {node.text}")

# Find all organizations
orgs = graph.query(node_type=EntityType.ORGANIZATION)
for node, _, _ in orgs:
    print(f"Organization: {node.text}")
```

### Query by Relation Type

```python
from src.ml.relation_extractor import RelationType

# Find CEO relations
ceo_rels = graph.query(relation_type=RelationType.CEO_OF)
for source, edge, target in ceo_rels:
    print(f"{source.text} is CEO of {target.text}")

# Find location relations
location_rels = graph.query(relation_type=RelationType.HEADQUARTERED_IN)
for source, edge, target in location_rels:
    print(f"{source.text} is located in {target.text}")
```

### Query with Confidence Threshold

```python
# High-confidence relations only
high_conf = graph.query(relation_type=RelationType.WORKS_AT, min_confidence=0.8)
for source, edge, target in high_conf:
    print(f"{source.text} → {target.text} ({edge.confidence:.2f})")
```

### Combined Queries

```python
# Find persons in employment relations
employment = graph.query(
    node_type=EntityType.PERSON,
    relation_type=RelationType.WORKS_AT,
    min_confidence=0.7
)
```

## Graph Traversal

### Get Neighbors

```python
# Outgoing neighbors
neighbors = graph.get_neighbors("TechSolutions GmbH")
for neighbor in neighbors:
    print(f"  → {neighbor.text}")

# Incoming neighbors
incoming = graph.get_incoming_neighbors("TechSolutions GmbH")
for node in incoming:
    print(f"  ← {node.text}")

# Neighbors by relation type
employees = graph.get_neighbors(
    "TechSolutions GmbH",
    relation_type=RelationType.WORKS_AT
)
```

### Find Paths

```python
# Find shortest path between two entities
path = graph.find_path("Max Mustermann", "München")

if path:
    print(f"Path: {' → '.join(path)}")
    # Output: Max Mustermann → TechSolutions GmbH → München
```

### Extract Subgraph

```python
# Get subgraph within N hops
subgraph = graph.get_subgraph("TechSolutions GmbH", depth=1)

print(f"Subgraph: {len(subgraph.nodes)} nodes, {len(subgraph.edges)} edges")

# Subgraph contains:
# - TechSolutions GmbH (center)
# - All nodes 1 hop away
# - All edges between these nodes
```

## Graph Analysis

### Node Degree

```python
# Get node degree (in, out, total)
in_deg, out_deg, total_deg = graph.get_node_degree("TechSolutions GmbH")

print(f"Incoming: {in_deg}")
print(f"Outgoing: {out_deg}")
print(f"Total: {total_deg}")
```

### Centrality Analysis

```python
# Find most central nodes
central_nodes = graph.get_central_nodes(top_n=5)

for node, degree in central_nodes:
    print(f"{node.text}: {degree} connections")
```

### Graph Statistics

```python
stats = graph.stats()

print(f"Nodes: {stats['num_nodes']}")
print(f"Edges: {stats['num_edges']}")
print(f"Average degree: {stats['avg_degree']}")
print(f"Max degree: {stats['max_degree']}")
print(f"Graph density: {stats['density']}")

print("\nEntity types:")
for entity_type, count in stats['entity_types'].items():
    print(f"  {entity_type}: {count}")

print("\nRelation types:")
for relation_type, count in stats['relation_types'].items():
    print(f"  {relation_type}: {count}")
```

## Export Formats

### JSON Export

```python
from src.ml.knowledge_graph import GraphFormat

json_data = graph.export(GraphFormat.JSON)

# Output:
# {
#   "nodes": [
#     {"id": "Max Mustermann", "text": "Max Mustermann", "type": "person", ...},
#     ...
#   ],
#   "edges": [
#     {"source": "Max Mustermann", "target": "Siemens AG", "relation": "works_at", ...},
#     ...
#   ]
# }
```

**Use cases:**
- Web visualization (D3.js, vis.js, Cytoscape.js)
- Data interchange
- API responses

### Neo4j Cypher Export

```python
cypher = graph.export(GraphFormat.CYPHER)

# Output:
# CREATE (nMax_Mustermann:Entity {id: "Max Mustermann", text: "Max Mustermann", type: "person"})
# CREATE (nSiemens_AG:Entity {id: "Siemens AG", text: "Siemens AG", type: "organization"})
# MATCH (s:Entity {id: "Max Mustermann"}), (t:Entity {id: "Siemens AG"})
# CREATE (s)-[:WORKS_AT {confidence: 0.9}]->(t)
```

**Import into Neo4j:**
```bash
# Start Neo4j
neo4j console

# Open Neo4j Browser: http://localhost:7474
# Paste and run the Cypher queries
```

### GraphML Export

```python
graphml = graph.export(GraphFormat.GRAPHML)

# Output: XML format compatible with graph visualization tools
```

**Compatible tools:**
- Gephi
- yEd
- Cytoscape
- NetworkX

**Example usage with NetworkX:**
```python
import networkx as nx

# Save GraphML
with open('graph.graphml', 'w') as f:
    f.write(graphml)

# Load in NetworkX
G = nx.read_graphml('graph.graphml')
```

### Adjacency List Export

```python
adjacency = graph.export(GraphFormat.ADJACENCY)

# Output:
# {
#   "Max Mustermann": [
#     {"target": "Siemens AG", "relation": "works_at", "confidence": 0.9}
#   ],
#   ...
# }
```

**Use cases:**
- Custom graph algorithms
- Graph analysis libraries
- Machine learning features

## Use Cases

### Contract Analysis

```python
builder = KnowledgeGraphBuilder(use_spacy=True)

contract = """
DIENSTLEISTUNGSVERTRAG

zwischen TechSolutions GmbH, vertreten durch Max Mustermann,
und DataCorp AG, vertreten durch Anna Schmidt.
"""

graph = builder.build_from_text(contract)

# Extract contract parties
print("Contract Parties:")
parties = graph.query(node_type=EntityType.PERSON)
for node, _, _ in parties:
    print(f"  • {node.text}")

# Find CEOs
ceos = graph.query(relation_type=RelationType.CEO_OF)
for source, edge, target in ceos:
    print(f"  • {source.text} represents {target.text}")
```

### Document Network Analysis

```python
# Build graph from multiple documents
documents = load_documents()  # Your document loader

combined_graph = KnowledgeGraph()
for doc in documents:
    doc_graph = builder.build_from_text(doc.content)
    # Merge graphs...

# Find key entities
central = combined_graph.get_central_nodes(top_n=10)
print("Key entities across all documents:")
for node, degree in central:
    print(f"  {node.text}: {degree} connections")
```

### Semantic Search

```python
def find_related_entities(graph, entity_name, max_hops=2):
    """Find all entities related to given entity"""
    subgraph = graph.get_subgraph(entity_name, depth=max_hops)
    return [node.text for node in subgraph.nodes.values()]

# Find all entities related to "Siemens AG"
related = find_related_entities(graph, "Siemens AG", max_hops=2)
print(f"Entities related to Siemens AG: {related}")
```

### Knowledge Base Construction

```python
# Build knowledge base from corpus
corpus = ["doc1.txt", "doc2.txt", "doc3.txt", ...]

kb = KnowledgeGraph()
for doc_path in corpus:
    with open(doc_path) as f:
        text = f.read()

    doc_graph = builder.build_from_text(text)

    # Merge into knowledge base
    for node in doc_graph.nodes.values():
        kb.add_node(node)
    for edge in doc_graph.edges:
        kb.add_edge(edge)

# Export to Neo4j for persistent storage
cypher = kb.export(GraphFormat.CYPHER)
# Import into Neo4j...
```

## Integration with Neo4j

### Setup Neo4j

```bash
# Install Neo4j Desktop or Community Edition
# https://neo4j.com/download/

# Start Neo4j
neo4j console

# Default credentials:
# URL: bolt://localhost:7687
# Username: neo4j
# Password: neo4j (change on first login)
```

### Export and Import

```python
from src.ml.knowledge_graph import GraphFormat

# Build graph
graph = builder.build_from_text(text)

# Export Cypher queries
cypher = graph.export(GraphFormat.CYPHER)

# Save to file
with open('import.cypher', 'w') as f:
    f.write(cypher)

# Import via Neo4j Browser or cypher-shell:
# cat import.cypher | cypher-shell -u neo4j -p password
```

### Direct Neo4j Integration (Optional)

```python
from neo4j import GraphDatabase

# Connect to Neo4j
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Import graph
with driver.session() as session:
    # Create nodes
    for node in graph.nodes.values():
        session.run(
            "CREATE (n:Entity {id: $id, text: $text, type: $type})",
            id=node.id,
            text=node.text,
            type=node.type.value
        )

    # Create relationships
    for edge in graph.edges:
        session.run(
            f"MATCH (s:Entity {{id: $source}}), (t:Entity {{id: $target}}) "
            f"CREATE (s)-[:{edge.relation.value.upper()} {{confidence: $conf}}]->(t)",
            source=edge.source,
            target=edge.target,
            conf=edge.confidence
        )

driver.close()
```

### Query Neo4j

```cypher
// Find all persons
MATCH (n:Entity {type: 'person'})
RETURN n

// Find employment relationships
MATCH (p:Entity)-[r:WORKS_AT]->(o:Entity)
RETURN p.text, o.text

// Find all entities connected to "Siemens AG"
MATCH (n:Entity {text: 'Siemens AG'})-[r]-(m:Entity)
RETURN n, r, m

// Find paths between two entities
MATCH path = shortestPath(
  (a:Entity {text: 'Max Mustermann'})-[*]-(b:Entity {text: 'München'})
)
RETURN path
```

## Performance Considerations

### Graph Size

| Nodes | Edges | Build Time | Memory |
|-------|-------|------------|--------|
| 100 | 200 | ~1s | ~10 MB |
| 1,000 | 2,000 | ~5s | ~50 MB |
| 10,000 | 20,000 | ~30s | ~200 MB |
| 100,000 | 200,000 | ~5min | ~1.5 GB |

### Optimization Tips

**For large documents:**
1. Split into chunks and process separately
2. Use higher confidence threshold to reduce edges
3. Consider Neo4j for persistent storage

**For graph queries:**
1. Use specific query filters (node_type, relation_type)
2. Limit subgraph depth (depth=1 or 2)
3. Cache frequently accessed subgraphs

**For export:**
1. JSON: Fast, best for small-medium graphs
2. Cypher: Slower, best for Neo4j import
3. GraphML: Medium speed, best for visualization tools

## Troubleshooting

### Issue: Graph is empty

**Problem:** `build_from_text()` returns empty graph

**Solutions:**
1. Check if entities are detected: Run NER separately
2. Check if relations are found: Run RelationExtractor separately
3. Lower `min_confidence` threshold
4. Verify spaCy model is installed

### Issue: Missing expected relations

**Problem:** Some obvious relations not extracted

**Solutions:**
1. Check relation extraction guide for supported patterns
2. Lower confidence threshold: `min_confidence=0.5`
3. Add custom relation patterns to RelationExtractor
4. Verify entity types are correct

### Issue: Duplicate nodes

**Problem:** Same entity appears multiple times

**Solutions:**
1. Normalize entity text (case, whitespace)
2. Implement entity resolution/merging
3. Use consistent entity IDs

### Issue: Neo4j import fails

**Problem:** Cypher queries fail in Neo4j

**Solutions:**
1. Check Neo4j is running: `neo4j status`
2. Verify credentials
3. Clear database if needed: `MATCH (n) DETACH DELETE n`
4. Check for special characters in entity names

## Best Practices

1. **Entity Resolution**: Normalize entity names before building graph
2. **Confidence Threshold**: Start with 0.6-0.7, adjust based on precision/recall
3. **Graph Size**: For large graphs (>10k nodes), use Neo4j instead of in-memory
4. **Incremental Updates**: Build graphs incrementally for document streams
5. **Validation**: Always check graph statistics after construction
6. **Persistence**: Export to Neo4j or JSON for long-term storage
7. **Querying**: Use specific filters to improve query performance
8. **Visualization**: Use GraphML export for exploratory analysis

## See Also

- [Named Entity Recognition Guide](./NER_GUIDE.md)
- [Relation Extraction Guide](./RELATION_EXTRACTION_GUIDE.md)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [NetworkX Documentation](https://networkx.org/documentation/)
