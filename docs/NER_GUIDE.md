# Named Entity Recognition (NER) Guide

Comprehensive guide for using the NER system in Daten20.

## Overview

The NER system extracts named entities from text using two complementary methods:

1. **Regex-based NER**: Fast pattern matching for structured entities
2. **spaCy NER**: ML-based extraction for persons, organizations, and locations

## Supported Entity Types

| Entity Type | Method | Examples |
|-------------|--------|----------|
| **Person** | spaCy | Max Mustermann, Angela Merkel |
| **Organization** | spaCy | Siemens AG, Apple Inc. |
| **Location** | spaCy | Berlin, München, New York |
| **Email** | Regex | max@example.com |
| **Phone** | Regex | +49 30 123456, (089) 123-456 |
| **Money** | Regex | 1500.00 EUR, $100 |
| **Date** | Regex | 15.03.2024, 03/15/2024 |
| **IBAN** | Regex | DE89 3704 0044 0532 0130 00 |

## Installation

### Basic (Regex only)
No additional dependencies required.

### With spaCy Support

```bash
# Install spaCy
pip install spacy

# Download language models
python -m spacy download de_core_news_sm  # German
python -m spacy download en_core_web_sm   # English
```

## Quick Start

### Basic Usage (Regex Only)

```python
from src.ml.ner import NEREngine

# Create NER engine without spaCy
ner = NEREngine(use_spacy=False)

text = "Contact: info@example.com, Phone: +49 30 123456"
entities = ner.extract_entities(text)

for entity in entities:
    print(f"{entity.type}: {entity.text}")
# Output:
# email: info@example.com
# phone: +49 30 123456
```

### With spaCy (Recommended)

```python
from src.ml.ner import NEREngine

# Create NER engine with spaCy
ner = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")

text = "Max Mustermann arbeitet bei Siemens AG in München."
entities = ner.extract_entities(text)

for entity in entities:
    print(f"{entity.type}: {entity.text}")
# Output:
# person: Max Mustermann
# organization: Siemens AG
# location: München
```

## Advanced Usage

### Extract Specific Entity Types

```python
from src.ml.ner import NEREngine, EntityType

ner = NEREngine(use_spacy=True)

text = "Max Mustermann (max@example.com) works at Apple Inc."

# Extract only persons
persons = ner.extract_by_type(text, EntityType.PERSON)
print([p.text for p in persons])  # ['Max Mustermann']

# Extract only organizations
orgs = ner.extract_by_type(text, EntityType.ORGANIZATION)
print([o.text for o in orgs])  # ['Apple Inc.']

# Extract only emails
emails = ner.extract_by_type(text, EntityType.EMAIL)
print([e.text for e in emails])  # ['max@example.com']
```

### Using Different Language Models

```python
# German text
ner_de = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")
entities_de = ner_de.extract_entities("Max Mustermann aus Berlin")

# English text
ner_en = NEREngine(use_spacy=True, spacy_model="en_core_web_sm")
entities_en = ner_en.extract_entities("John Smith from London")
```

### Document Processing

```python
from src.ml.ner import NEREngine, EntityType

ner = NEREngine(use_spacy=True)

# Process a contract document
document = """
DIENSTLEISTUNGSVERTRAG

zwischen TechSolutions GmbH, vertreten durch Max Mustermann,
und DataCorp AG, vertreten durch Anna Schmidt.

Kontakt: max@techsolutions.de, anna@datacorp.de
Betrag: 5.000,00 EUR
"""

entities = ner.extract_entities(document)

# Group entities by type
by_type = {}
for entity in entities:
    if entity.type not in by_type:
        by_type[entity.type] = []
    by_type[entity.type].append(entity.text)

# Extract contract parties
parties = by_type.get(EntityType.PERSON, [])
companies = by_type.get(EntityType.ORGANIZATION, [])
contacts = by_type.get(EntityType.EMAIL, [])
amounts = by_type.get(EntityType.MONEY, [])

print(f"Parties: {parties}")
print(f"Companies: {companies}")
print(f"Contacts: {contacts}")
print(f"Amount: {amounts}")
```

## Entity Object

Each extracted entity is represented as an `Entity` object:

```python
@dataclass
class Entity:
    text: str           # The entity text
    type: EntityType    # Entity type (PERSON, ORGANIZATION, etc.)
    start: int          # Start position in text
    end: int            # End position in text
    confidence: float   # Confidence score (0.0-1.0)
```

Example:
```python
entity = Entity(
    text="Max Mustermann",
    type=EntityType.PERSON,
    start=0,
    end=14,
    confidence=0.9
)
```

## Architecture

### How It Works

1. **Regex NER**: Uses predefined patterns to extract structured entities
   - Email: `r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'`
   - Phone: `r'\b\+?[\d\s\-\(\)]{10,20}\b'`
   - Money: `r'\b\d+[.,]\d{2}\s?(€|EUR|USD|\$)\b'`
   - Date: `r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b'`
   - IBAN: `r'\b[A-Z]{2}\d{2}[\s]?[\d\s]{10,30}\b'`

2. **spaCy NER**: Uses trained ML models to identify entities
   - Persons: PER, PERSON
   - Organizations: ORG
   - Locations: LOC, GPE (geopolitical entities), FAC (facilities)

3. **Combination**: Merges results from both methods
   - Removes overlapping entities
   - Prefers spaCy results when entities overlap
   - Returns deduplicated list

### Fallback Strategy

```python
# If spaCy model not available, automatically falls back to regex
ner = NEREngine(use_spacy=True, spacy_model="nonexistent_model")

# Will use regex-only, no error thrown
entities = ner.extract_entities(text)
```

## Performance Considerations

### Regex NER
- **Speed**: Very fast (< 1ms for typical documents)
- **Accuracy**: High for structured data, limited for unstructured
- **Memory**: Minimal

### spaCy NER
- **Speed**: Slower (~10-50ms for typical documents)
- **Accuracy**: High for persons, organizations, locations
- **Memory**: ~100-500 MB per model

### Recommendations

**Use regex-only when:**
- Only extracting structured entities (email, phone, IBAN)
- Processing large volumes of documents
- Limited memory/CPU resources

**Use spaCy when:**
- Need to extract persons, organizations, locations
- Document text is unstructured
- Accuracy is more important than speed

**Use combined (default) when:**
- Need both structured and unstructured entity extraction
- Processing mixed content (contracts, emails, reports)
- Best overall accuracy required

## spaCy Models

### Available Models

| Model | Language | Size | Speed | Accuracy |
|-------|----------|------|-------|----------|
| `de_core_news_sm` | German | ~15 MB | Fast | Good |
| `de_core_news_md` | German | ~45 MB | Medium | Better |
| `de_core_news_lg` | German | ~560 MB | Slow | Best |
| `en_core_web_sm` | English | ~15 MB | Fast | Good |
| `en_core_web_md` | English | ~45 MB | Medium | Better |
| `en_core_web_lg` | English | ~560 MB | Slow | Best |

### Installation

```bash
# Small models (recommended for production)
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm

# Medium models (better accuracy)
python -m spacy download de_core_news_md
python -m spacy download en_core_web_md

# Large models (best accuracy, slower)
python -m spacy download de_core_news_lg
python -m spacy download en_core_web_lg
```

## Integration Examples

### With Document Classifier

```python
from src.ml.ner import NEREngine, EntityType
from src.ml.classifier import DocumentClassifier

ner = NEREngine(use_spacy=True)
classifier = DocumentClassifier()

# Classify document
document = "..."
category = classifier.predict(document)

# Extract entities based on category
if category == "CONTRACT":
    # Extract contract parties
    parties = ner.extract_by_type(document, EntityType.PERSON)
    companies = ner.extract_by_type(document, EntityType.ORGANIZATION)

elif category == "INVOICE":
    # Extract financial information
    amounts = ner.extract_by_type(document, EntityType.MONEY)
    ibans = ner.extract_by_type(document, EntityType.IBAN)
```

### With Auto-Tagging

```python
from src.ml.ner import NEREngine, EntityType
from src.ml.tagging import AutoTagger

ner = NEREngine(use_spacy=True)
tagger = AutoTagger()

document = "..."

# Extract entities
entities = ner.extract_entities(document)

# Use entities as additional tags
entity_tags = [entity.text for entity in entities]

# Combine with auto-tags
auto_tags = tagger.suggest_tags(document)
all_tags = entity_tags + [tag.tag for tag in auto_tags]
```

## Troubleshooting

### Issue: spaCy model not found

**Error:**
```
OSError: [E050] Can't find model 'de_core_news_sm'
```

**Solution:**
```bash
python -m spacy download de_core_news_sm
```

### Issue: Entities not detected

**Problem**: spaCy not detecting expected entities

**Solutions:**
1. Try a larger model (md or lg instead of sm)
2. Check if entity is actually a named entity (common nouns won't be detected)
3. Ensure correct language model (de for German, en for English)

### Issue: Performance too slow

**Problem**: NER processing takes too long

**Solutions:**
1. Use smaller spaCy model (sm instead of lg)
2. Disable spaCy and use regex-only: `NEREngine(use_spacy=False)`
3. Process documents in batches with spaCy's `nlp.pipe()`

### Issue: Wrong language detected

**Problem**: German text processed with English model

**Solution:**
```python
# Explicitly specify German model
ner = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")
```

## API Reference

### `NEREngine`

```python
class NEREngine:
    def __init__(self, use_spacy: bool = True, spacy_model: str = "de_core_news_sm"):
        """
        Initialize NER engine

        Args:
            use_spacy: Whether to use spaCy NER
            spacy_model: spaCy model to use
        """

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all entities from text"""

    def extract_by_type(self, text: str, entity_type: EntityType) -> List[Entity]:
        """Extract specific entity type"""
```

### `Entity`

```python
@dataclass
class Entity:
    text: str           # Entity text
    type: EntityType    # Entity type
    start: int          # Start position
    end: int            # End position
    confidence: float   # Confidence score
```

### `EntityType`

```python
class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    EMAIL = "email"
    PHONE = "phone"
    IBAN = "iban"
```

## Best Practices

1. **Choose the right model**: Use small models for speed, large for accuracy
2. **Handle fallbacks**: Always check if spaCy is available before relying on it
3. **Validate results**: Post-process entities to filter false positives
4. **Use batching**: Process multiple documents with `nlp.pipe()` for better performance
5. **Cache models**: Load spaCy models once and reuse (NEREngine handles this)

## See Also

- [spaCy Documentation](https://spacy.io/usage)
- [spaCy Models](https://spacy.io/models)
- [Document Classification Guide](./CLASSIFIER_GUIDE.md)
- [Auto-Tagging Guide](./TAGGING_GUIDE.md)
