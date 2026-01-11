# Relation Extraction Guide

Comprehensive guide for extracting semantic relations between named entities in Daten20.

## Overview

Relation Extraction identifies semantic relationships between named entities in text. This module combines **spaCy dependency parsing** with **pattern-based matching** to extract structured relationships.

### Example

**Input:**
```
Max Mustermann arbeitet bei Siemens AG in München.
```

**Output:**
```
Relation 1: Max Mustermann --[WORKS_AT]--> Siemens AG
Relation 2: Siemens AG --[HEADQUARTERED_IN]--> München
```

## Supported Relation Types

| Relation Type | Description | Example |
|---------------|-------------|---------|
| **WORKS_AT** | Person employed by Organization | "Max works at Siemens AG" |
| **CEO_OF** | Person is CEO of Organization | "Tim Cook is CEO of Apple" |
| **MANAGER_OF** | Person manages Organization | "Anna is manager of DataCorp" |
| **LOCATED_IN** | Entity located in Location | "Company is in Berlin" |
| **HEADQUARTERED_IN** | Organization HQ in Location | "Apple HQ in Cupertino" |
| **RESIDES_IN** | Person lives in Location | "Max lives in Munich" |
| **FOUNDED** | Person founded Organization | "Jobs founded Apple" |
| **PART_OF** | Organization part of another | "Subsidiary part of Parent Co" |
| **ACQUIRED** | Organization acquired another | "Google acquired YouTube" |
| **OWNS** | Person/Org owns Organization | "Investor owns startup" |
| **MEMBER_OF** | Person member of Organization | "Member of board" |

## Installation

### Basic (Pattern-based only)
No additional dependencies required - uses regex patterns.

### With spaCy (Recommended)

```bash
# Install spaCy
pip install spacy

# Download language models
python -m spacy download de_core_news_sm  # German
python -m spacy download en_core_web_sm   # English
```

## Quick Start

### Basic Usage

```python
from src.ml.relation_extractor import RelationExtractor

# Create extractor with spaCy
extractor = RelationExtractor(use_spacy=True, spacy_model="de_core_news_sm")

# Extract relations
text = "Max Mustermann arbeitet bei Siemens AG in München."
relations = extractor.extract_relations(text)

for rel in relations:
    print(f"{rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")

# Output:
# Max Mustermann --[works_at]--> Siemens AG
# Siemens AG --[headquartered_in]--> München
```

### Extract Specific Relation Types

```python
from src.ml.relation_extractor import RelationExtractor, RelationType

extractor = RelationExtractor(use_spacy=True)

text = """
Max Mustermann arbeitet bei Siemens AG.
Anna Schmidt ist Geschäftsführerin der DataCorp AG.
"""

# Extract only employment relations
employment_rels = extractor.get_relations_by_type(text, RelationType.WORKS_AT)

for rel in employment_rels:
    print(f"{rel.subject.text} works at {rel.object.text}")
```

### Get Relations for Specific Entity

```python
extractor = RelationExtractor(use_spacy=True)

text = """
Max Mustermann arbeitet bei Siemens AG.
Max Mustermann wohnt in München.
Max Mustermann gründete TechSolutions GmbH.
"""

# Get all relations involving "Max Mustermann"
relations = extractor.get_entity_relations(text, "Max Mustermann")

for rel in relations:
    print(f"{rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")

# Output:
# Max Mustermann --[works_at]--> Siemens AG
# Max Mustermann --[resides_in]--> München
# Max Mustermann --[founded]--> TechSolutions GmbH
```

## Advanced Usage

### Contract Analysis

```python
extractor = RelationExtractor(use_spacy=True)

contract = """
DIENSTLEISTUNGSVERTRAG

zwischen

TechSolutions GmbH mit Sitz in München,
vertreten durch den Geschäftsführer Max Mustermann,

und

DataCorp AG mit Hauptsitz in Berlin,
vertreten durch die Vorständin Anna Schmidt.
"""

relations = extractor.extract_relations(contract)

# Group by relation type
by_type = {}
for rel in relations:
    if rel.relation not in by_type:
        by_type[rel.relation] = []
    by_type[rel.relation].append(rel)

for rel_type, rels in by_type.items():
    print(f"\n{rel_type.value}:")
    for rel in rels:
        print(f"  • {rel.subject.text} → {rel.object.text}")

# Output:
# CEO_OF:
#   • Max Mustermann → TechSolutions GmbH
#   • Anna Schmidt → DataCorp AG
# HEADQUARTERED_IN:
#   • TechSolutions GmbH → München
#   • DataCorp AG → Berlin
```

### Multi-Language Support

```python
# German
extractor_de = RelationExtractor(use_spacy=True, spacy_model="de_core_news_sm")
text_de = "Max Mustermann arbeitet bei Siemens AG."
relations_de = extractor_de.extract_relations(text_de)

# English
extractor_en = RelationExtractor(use_spacy=True, spacy_model="en_core_web_sm")
text_en = "Tim Cook works at Apple Inc."
relations_en = extractor_en.extract_relations(text_en)
```

### Confidence Filtering

```python
extractor = RelationExtractor(use_spacy=True)

text = "Max Mustermann arbeitet bei Siemens AG."
relations = extractor.extract_relations(text)

# Filter high-confidence relations
high_confidence = [r for r in relations if r.confidence >= 0.8]

for rel in high_confidence:
    print(f"{rel.subject.text} → {rel.object.text} ({rel.confidence:.2%})")
```

### Building Knowledge Graphs

```python
extractor = RelationExtractor(use_spacy=True)

text = """
Max Mustermann gründete TechSolutions GmbH.
Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
TechSolutions GmbH hat ihren Sitz in München.
Anna Schmidt arbeitet bei TechSolutions GmbH.
"""

relations = extractor.extract_relations(text)

# Build adjacency list for knowledge graph
graph = {}
for rel in relations:
    subj = rel.subject.text
    if subj not in graph:
        graph[subj] = []
    graph[subj].append((rel.relation.value, rel.object.text))

# Export to Neo4j, NetworkX, etc.
```

## Relation Object

Each extracted relation is represented as:

```python
@dataclass
class Relation:
    subject: Entity          # Subject entity
    relation: RelationType   # Relation type
    object: Entity          # Object entity
    confidence: float       # Confidence score (0.0-1.0)
    context: str           # Original sentence/context
    start: int             # Start position in text
    end: int               # End position in text
```

Example:
```python
Relation(
    subject=Entity(text="Max Mustermann", type=EntityType.PERSON, ...),
    relation=RelationType.WORKS_AT,
    object=Entity(text="Siemens AG", type=EntityType.ORGANIZATION, ...),
    confidence=0.9,
    context="Max Mustermann arbeitet bei Siemens AG.",
    start=0,
    end=47
)
```

## How It Works

### 1. Dependency Parsing (spaCy)

Uses syntactic structure to identify relationships:

```
Max Mustermann arbeitet bei Siemens AG.
        ↓         ↓      ↓       ↓
     PERSON     VERB   PREP    ORG
        ↓         ↓              ↓
    [subject]--[verb]--[prep]--[object]
                   ↓
              WORKS_AT relation
```

### 2. Pattern-Based Matching

Uses keyword patterns when dependency parsing unavailable:

```python
# WORKS_AT patterns
Keywords: ["arbeitet bei", "works at", "tätig bei", "employed by"]

# CEO_OF patterns
Keywords: ["geschäftsführer", "ceo", "vorstand", "director"]

# LOCATED_IN patterns
Keywords: ["in", "sitz", "based in", "headquartered in"]
```

### 3. Entity Type Validation

Validates that entity types match expected relation:

```python
WORKS_AT: (PERSON, ORGANIZATION) ✅
WORKS_AT: (ORGANIZATION, PERSON) ❌

LOCATED_IN: (ORGANIZATION, LOCATION) ✅
LOCATED_IN: (LOCATION, ORGANIZATION) ❌
```

### 4. Deduplication

Removes duplicate relations, keeping highest confidence:

```python
# Input:
Relation 1: (Max, WORKS_AT, Siemens, confidence=0.8)
Relation 2: (Max, WORKS_AT, Siemens, confidence=0.9)

# Output:
Relation 2: (Max, WORKS_AT, Siemens, confidence=0.9)  # Higher confidence kept
```

## Performance Considerations

### Speed

| Method | Speed | Accuracy |
|--------|-------|----------|
| **Pattern-based** | Very fast (~1ms) | Good (70-80%) |
| **Dependency parsing** | Slower (~10-50ms) | Better (85-95%) |
| **Combined** | Medium (~20-60ms) | Best (90-98%) |

### Memory

- **Pattern-based**: ~1 MB
- **spaCy (sm model)**: ~100-200 MB
- **spaCy (lg model)**: ~500-700 MB

### Recommendations

**Use pattern-based when:**
- Processing large volumes quickly
- Limited memory/CPU resources
- Entity types are well-defined

**Use spaCy when:**
- Accuracy is critical
- Complex sentence structures
- Implicit relationships

**Use combined (default) when:**
- Best overall accuracy needed
- Mixed content types
- Production environments

## Troubleshooting

### Issue: No relations extracted

**Problem**: Extractor returns empty list

**Solutions:**
1. Ensure entities are detected first (run NER separately)
2. Check if text contains valid entity pairs
3. Try increasing context window (use full paragraphs)
4. Enable debug logging to see intermediate steps

### Issue: Low confidence scores

**Problem**: All relations have confidence < 0.5

**Solutions:**
1. Use larger spaCy model (md or lg instead of sm)
2. Add domain-specific patterns to `relation_patterns`
3. Pre-process text (remove noise, fix typos)
4. Validate entity boundaries

### Issue: Wrong relation types

**Problem**: Incorrect relation classification

**Solutions:**
1. Check entity type validation
2. Add more specific keywords to patterns
3. Use dependency parsing instead of patterns
4. Post-process with business rules

### Issue: Missing obvious relations

**Problem**: Clear relationships not extracted

**Solutions:**
1. Check if entities are detected correctly
2. Add missing patterns to `relation_patterns`
3. Verify entity proximity (too far apart?)
4. Use larger context window

## Integration Examples

### With Document Classifier

```python
from src.ml.classifier import DocumentClassifier
from src.ml.relation_extractor import RelationExtractor

classifier = DocumentClassifier()
extractor = RelationExtractor(use_spacy=True)

document = "..."

# Classify document
category = classifier.predict(document)

# Extract relations based on category
if category == "CONTRACT":
    # Focus on employment and CEO relations
    relations = extractor.extract_relations(document)
    ceo_rels = [r for r in relations if r.relation == RelationType.CEO_OF]
    work_rels = [r for r in relations if r.relation == RelationType.WORKS_AT]
```

### With Knowledge Graphs (Neo4j)

```python
from neo4j import GraphDatabase
from src.ml.relation_extractor import RelationExtractor

extractor = RelationExtractor(use_spacy=True)
text = "..."

relations = extractor.extract_relations(text)

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    for rel in relations:
        # Create nodes and relationships
        session.run("""
            MERGE (s:Entity {name: $subject, type: $subject_type})
            MERGE (o:Entity {name: $object, type: $object_type})
            MERGE (s)-[r:$relation {confidence: $confidence}]->(o)
        """,
            subject=rel.subject.text,
            subject_type=rel.subject.type.value,
            object=rel.object.text,
            object_type=rel.object.type.value,
            relation=rel.relation.value,
            confidence=rel.confidence
        )
```

### With NLP Pipeline

```python
from src.ml.ner import NEREngine
from src.ml.relation_extractor import RelationExtractor
from src.ml.classifier import DocumentClassifier

# Complete NLP pipeline
def analyze_document(text):
    # Step 1: Classify
    classifier = DocumentClassifier()
    category = classifier.predict(text)

    # Step 2: Extract entities
    ner = NEREngine(use_spacy=True)
    entities = ner.extract_entities(text)

    # Step 3: Extract relations
    extractor = RelationExtractor(use_spacy=True)
    relations = extractor.extract_relations(text)

    return {
        'category': category,
        'entities': entities,
        'relations': relations
    }
```

## API Reference

### `RelationExtractor`

```python
class RelationExtractor:
    def __init__(self, use_spacy: bool = True, spacy_model: str = "de_core_news_sm"):
        """
        Initialize relation extractor

        Args:
            use_spacy: Use spaCy dependency parsing
            spacy_model: spaCy model to load
        """

    def extract_relations(self, text: str) -> List[Relation]:
        """Extract all relations from text"""

    def get_relations_by_type(self, text: str, relation_type: RelationType) -> List[Relation]:
        """Extract only specific relation type"""

    def get_entity_relations(self, text: str, entity_text: str) -> List[Relation]:
        """Get all relations involving specific entity"""
```

### `RelationType` Enum

```python
class RelationType(str, Enum):
    WORKS_AT = "works_at"
    CEO_OF = "ceo_of"
    MANAGER_OF = "manager_of"
    LOCATED_IN = "located_in"
    HEADQUARTERED_IN = "headquartered_in"
    RESIDES_IN = "resides_in"
    FOUNDED = "founded"
    PART_OF = "part_of"
    ACQUIRED = "acquired"
    OWNS = "owns"
    MEMBER_OF = "member_of"
```

## Best Practices

1. **Always extract entities first**: Verify NER works before relation extraction
2. **Use appropriate spaCy model**: sm for speed, lg for accuracy
3. **Filter by confidence**: Set threshold based on use case (0.7-0.8 recommended)
4. **Validate relation semantics**: Post-process with business rules
5. **Handle negations**: Check for "not", "never" in context
6. **Use full context**: Provide complete sentences, not fragments
7. **Combine methods**: Use both dependency parsing and patterns
8. **Cache spaCy models**: Load once, reuse for multiple documents

## See Also

- [Named Entity Recognition Guide](./NER_GUIDE.md)
- [Knowledge Graph Guide](./KNOWLEDGE_GRAPH_GUIDE.md) (coming soon)
- [Document Classification Guide](./CLASSIFIER_GUIDE.md)
- [spaCy Dependency Parsing](https://spacy.io/usage/linguistic-features#dependency-parse)
