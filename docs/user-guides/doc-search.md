# 🔍 Doc-Search User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Advanced document search with full-text and semantic capabilities

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Commands](#commands)
4. [Use Cases](#use-cases)
5. [Troubleshooting](#troubleshooting)
6. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Overview

**doc-search.py** provides powerful search capabilities across document repositories using TF-IDF, entity-based search, and relation queries.

### Key Features

- ✅ **Full-Text Search** - TF-IDF and BM25 ranking
- ✅ **Semantic Search** - Find documents by meaning
- ✅ **Entity Search** - Find by person, organization, location
- ✅ **Relation Search** - Query document relationships
- ✅ **Faceted Search** - Filter by category, date, entities
- ✅ **Similar Documents** - Find related content

### Search Types

| Type | Description | Example Query |
|------|-------------|---------------|
| **Text** | Keyword matching | "employment contract" |
| **Semantic** | Meaning-based | "documents about hiring" |
| **Entity** | Find by entities | person:"Max Mustermann" |
| **Relation** | Relationship-based | "works_at Acme Corp" |

---

## ⚡ Quick Start

### 1. Basic Text Search

```bash
# Search for documents
python doc-search.py search "employment contract"

# Output:
# Found 5 results
#
# 1. contract_2024.pdf (score: 0.87)
#    Preview: "This employment contract between..."
#    Category: LEGAL
#    Entities: 12, Relations: 5
#
# 2. agreement_v2.pdf (score: 0.73)
#    Preview: "Employment agreement for the position..."
```

### 2. Entity Search

```bash
# Find documents mentioning a person
python doc-search.py entity --person "Max Mustermann"

# Find documents about an organization
python doc-search.py entity --org "Acme Corporation"
```

### 3. Relation Search

```bash
# Find documents with specific relationship
python doc-search.py relation \
  --type WORKS_AT \
  --source "Max Mustermann" \
  --target "Acme Corp"
```

---

## 📚 Commands

### Command: `search`

Full-text keyword search across documents.

**Usage:**
```bash
python doc-search.py search <query> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-k, --top-k N` | Number of results | 10 |
| `--category CAT` | Filter by category | all |

**Examples:**

```bash
# Basic search
python doc-search.py search "invoice 2024"

# Top 20 results
python doc-search.py search "social services" -k 20

# Filter by category
python doc-search.py search "report" --category FINANCIAL

# Complex query
python doc-search.py search "employment contract benefits" -k 5
```

**Output Format:**
```json
[
  {
    "document_id": 123,
    "score": 0.87,
    "filename": "contract_2024.pdf",
    "text_preview": "This employment contract...",
    "category": "LEGAL",
    "entities_count": 12,
    "relations_count": 5
  }
]
```

---

### Command: `entity`

Search documents by entity mentions.

**Usage:**
```bash
python doc-search.py entity [options]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--person NAME` | Search for person |
| `--org NAME` | Search for organization |
| `--location NAME` | Search for location |

**Examples:**

```bash
# Find all documents mentioning a person
python doc-search.py entity --person "Max Mustermann"

# Find documents about an organization
python doc-search.py entity --org "Acme Corporation"

# Find documents referencing a location
python doc-search.py entity --location "Berlin"

# Multiple entity types (combines with OR)
python doc-search.py entity \
  --person "Max Mustermann" \
  --org "Acme Corp"
```

**Output Example:**
```json
[
  {
    "document_id": 456,
    "filename": "employment_contract.pdf",
    "matching_entities": [
      {
        "text": "Max Mustermann",
        "type": "PERSON",
        "confidence": 0.95
      }
    ],
    "text_preview": "This agreement between...",
    "category": "LEGAL"
  }
]
```

---

### Command: `relation`

Search documents containing specific relationships.

**Usage:**
```bash
python doc-search.py relation [options]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--type TYPE` | Relation type |
| `--source ENTITY` | Source entity |
| `--target ENTITY` | Target entity |

**Relation Types:**
- `WORKS_AT` - Employment
- `LOCATED_IN` - Location
- `OWNS` - Ownership
- `MANAGES` - Management
- `MEMBER_OF` - Membership

**Examples:**

```bash
# Find employment relationships
python doc-search.py relation --type WORKS_AT

# Find specific relationship
python doc-search.py relation \
  --type WORKS_AT \
  --source "Max Mustermann" \
  --target "Acme Corp"

# Find all documents where entity is source
python doc-search.py relation --source "Max Mustermann"

# Find all documents where entity is target
python doc-search.py relation --target "Acme Corporation"
```

**Output Example:**
```json
[
  {
    "document_id": 789,
    "filename": "org_chart.pdf",
    "matching_relations": [
      {
        "source": "Max Mustermann",
        "relation": "WORKS_AT",
        "target": "Acme Corp",
        "confidence": 0.88
      }
    ],
    "text_preview": "Organization structure...",
    "category": "ORGANIZATIONAL"
  }
]
```

---

### Command: `semantic`

Semantic search based on meaning, not just keywords.

**Usage:**
```bash
python doc-search.py semantic <query> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-k, --top-k N` | Number of results | 10 |

**Examples:**

```bash
# Find by meaning
python doc-search.py semantic "documents about hiring employees"

# Results include documents with:
# - "employment contracts"
# - "recruitment policies"
# - "onboarding procedures"
# Even without exact keyword matches

# More examples
python doc-search.py semantic "financial reports from last year" -k 20
python doc-search.py semantic "customer complaints and feedback"
```

---

### Command: `similar`

Find documents similar to a given document.

**Usage:**
```bash
python doc-search.py similar <doc_id> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-k, --top-k N` | Number of results | 5 |

**Examples:**

```bash
# Find similar documents
python doc-search.py similar 123 -k 5

# Use case: "More like this" feature
# Given a contract, find similar contracts
```

---

## 💼 Use Cases

### Use Case 1: Legal Document Discovery

**Scenario:** Find all contracts mentioning a specific party.

```bash
# Find all employment contracts
python doc-search.py search "employment contract" -k 50 > employment_docs.json

# Filter by entity
python doc-search.py entity --person "Max Mustermann" > max_docs.json

# Find contracts between specific parties
python doc-search.py relation \
  --type WORKS_AT \
  --source "Max Mustermann" \
  --target "Acme Corp"
```

**Why it's useful:** Quick legal research and due diligence.

---

### Use Case 2: Knowledge Base Search

**Scenario:** Build searchable knowledge base of documents.

```bash
# 1. Index documents (one-time)
python doc-batch-processor.py process /documents/ \
  --pipeline ner,classify,relations \
  --output-dir /indexed/

# 2. Search indexed documents
python doc-search.py search "technical specification" -k 10

# 3. Find related documents
python doc-search.py similar 456 -k 5

# 4. Entity-based navigation
python doc-search.py entity --org "Engineering Team"
```

**Why it's useful:** Turn document repository into searchable knowledge base.

---

### Use Case 3: Compliance Auditing

**Scenario:** Find all documents related to specific regulations.

```bash
# Search for GDPR-related documents
python doc-search.py search "GDPR data processing" -k 100 > gdpr_docs.json

# Find documents mentioning specific data subjects
python doc-search.py entity --person "John Citizen" > subject_docs.json

# Cross-reference
jq -r '.[] | .filename' gdpr_docs.json | sort > gdpr_list.txt
jq -r '.[] | .filename' subject_docs.json | sort > subject_list.txt
comm -12 gdpr_list.txt subject_list.txt > compliance_docs.txt
```

**Why it's useful:** Rapid compliance auditing and document discovery.

---

## ❗ Troubleshooting

### Issue: "No results found for valid query"

**Symptom:** Search returns 0 results but documents exist

**Causes & Solutions:**

1. **Documents not indexed:**
   ```bash
   # Check if documents are indexed
   # Document search requires prior indexing via batch processor
   python doc-batch-processor.py process /documents/ \
     --pipeline ner,classify
   ```

2. **Query too specific:**
   ```bash
   # Try broader query
   python doc-search.py search "contract"  # Instead of exact phrase
   ```

3. **Wrong search type:**
   ```bash
   # Use entity search for names
   python doc-search.py entity --person "Name"  # Not text search
   ```

---

### Issue: "Search is slow"

**Symptom:** Search takes > 5 seconds

**Solutions:**

```bash
# 1. Build TF-IDF index (one-time, speeds up searches)
python doc-search.py index /documents/

# 2. Limit result count
python doc-search.py search "query" -k 10  # Instead of 100

# 3. Use filters to narrow scope
python doc-search.py search "query" --category LEGAL
```

---

### Issue: "Semantic search not working"

**Warning:**
```
WARNING: Semantic search not fully implemented, falling back to text search
```

**Explanation:** Semantic search requires embeddings model (not yet implemented)

**Workaround:**
```bash
# Use text search with synonyms
python doc-search.py search "employment OR hiring OR recruitment"
```

---

## 💡 Tips & Best Practices

### 1. Index Documents First

```bash
# IMPORTANT: Index documents before searching
# One-time indexing step:
python doc-batch-processor.py process /documents/ \
  --pipeline ner,classify,relations \
  --output-dir /indexed/

# Then search works efficiently
python doc-search.py search "query"
```

### 2. Combine Search Types

```bash
# Start broad, then narrow down

# Step 1: Text search
python doc-search.py search "contract" -k 50 > results.json

# Step 2: Filter by entity
cat results.json | jq '.[] | select(.entities_count > 5)'

# Step 3: Entity search for specific party
python doc-search.py entity --person "Max Mustermann"
```

### 3. Use Categories for Filtering

```bash
# Search within specific categories
python doc-search.py search "report" --category FINANCIAL
python doc-search.py search "contract" --category LEGAL
python doc-search.py search "memo" --category INTERNAL
```

### 4. Build Search Scripts

```bash
#!/bin/bash
# search_wrapper.sh

QUERY="$1"
LIMIT="${2:-10}"

# Search
echo "=== Text Search ==="
python doc-search.py search "$QUERY" -k "$LIMIT"

# Entity search (if query looks like a name)
if [[ "$QUERY" =~ [A-Z][a-z]+[[:space:]][A-Z] ]]; then
  echo "=== Entity Search ==="
  python doc-search.py entity --person "$QUERY"
fi

# Usage: ./search_wrapper.sh "Max Mustermann" 5
```

### 5. Export Results for Analysis

```bash
# Search and export
python doc-search.py search "invoice 2024" -k 100 > invoices.json

# Analyze results
jq -r '.[] | "\(.filename)\t\(.score)"' invoices.json | \
  sort -t$'\t' -k2 -rn | \
  head -20
```

---

## 🔄 Related Tools

- **doc-batch-processor.py** - Index documents for search
- **doc-processor.py** - Process individual documents
- **doc-dashboard.py** - Web UI for search

---

## 📊 Search Performance

### Expected Search Times

| Operation | < 100 docs | < 1000 docs | < 10000 docs |
|-----------|------------|-------------|--------------|
| Text search | < 0.1s | < 0.5s | < 2s |
| Entity search | < 0.2s | < 1s | < 5s |
| Relation search | < 0.3s | < 1.5s | < 7s |

### Optimization Tips

```bash
# Build index once
python doc-search.py index /documents/

# Use filters to reduce search space
python doc-search.py search "query" --category LEGAL

# Limit results
python doc-search.py search "query" -k 10  # Not -k 1000
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
