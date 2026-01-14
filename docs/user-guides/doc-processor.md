# 📄 Doc-Processor User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Comprehensive document processing with AI/ML capabilities

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Commands](#commands)
5. [Use Cases](#use-cases)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Overview

**doc-processor.py** is the main document processing tool in the DMS suite. It provides AI-powered document analysis, entity extraction, classification, and knowledge graph construction.

### Key Features

- ✅ **Text Extraction** - Extract text from PDF, DOCX, TXT, HTML files
- ✅ **Named Entity Recognition (NER)** - Extract persons, organizations, locations, dates
- ✅ **Document Classification** - Automatically categorize documents
- ✅ **Topic Modeling** - Discover topics using LDA
- ✅ **Relation Extraction** - Find relationships between entities
- ✅ **Knowledge Graphs** - Build graph representations
- ✅ **Batch Processing** - Process multiple documents at once
- ✅ **Multiple Export Formats** - JSON, CSV, Excel, PDF reports

### Supported File Types

| Format | Extension | Support Level |
|--------|-----------|---------------|
| PDF | `.pdf` | ✅ Full |
| Word | `.docx`, `.doc` | ✅ Full |
| Text | `.txt` | ✅ Full |
| HTML | `.html`, `.htm` | ✅ Full |
| Markdown | `.md` | ✅ Full |

---

## 🚀 Installation

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Install dependencies
pip install -r requirements.txt

# Download spaCy models for NER
python -m spacy download en_core_web_sm
python -m spacy download ru_core_news_sm
```

### Verify Installation

```bash
# Test if doc-processor is accessible
python doc-processor.py --help

# Should show command list
```

---

## ⚡ Quick Start

### 1. Process Your First Document

```bash
# Basic document processing
python doc-processor.py process sample.pdf

# Output:
# ✅ Document processed successfully
# - Text length: 5,234 characters
# - Word count: 856
# - Pages: 3
```

### 2. Extract Named Entities

```bash
# Extract all entities
python doc-processor.py ner document.pdf

# Extract specific entity types
python doc-processor.py ner document.pdf --entities PERSON ORG
```

### 3. Classify Document

```bash
# Classify into categories
python doc-processor.py classify document.pdf

# Output:
# Category: SOCIAL_SERVICES
# Confidence: 92.5%
```

### 4. Full Analysis

```bash
# Complete analysis with all features
python doc-processor.py analyze document.pdf --full --output results.json
```

---

## 📚 Commands

### Command: `process`

Process a single document and extract basic information.

**Usage:**
```bash
python doc-processor.py process <file> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output FILE` | Save results to file | stdout |
| `--format FORMAT` | Output format (json, text) | json |
| `--save-db` | Save to database | false |

**Examples:**
```bash
# Basic processing
python doc-processor.py process document.pdf

# Save to JSON file
python doc-processor.py process document.pdf --output results.json

# Process and save to database
python doc-processor.py process document.pdf --save-db
```

**Output Example:**
```json
{
  "filename": "document.pdf",
  "text_length": 5234,
  "word_count": 856,
  "pages": 3,
  "language": "en",
  "extracted_at": "2026-01-14T10:30:00Z"
}
```

---

### Command: `ner`

Extract named entities using spaCy NER engine.

**Usage:**
```bash
python doc-processor.py ner <file> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--entities TYPES` | Entity types to extract | ALL |
| `--output FILE` | Save results to file | stdout |
| `--format FORMAT` | Output format (json, csv, text) | json |
| `--min-confidence FLOAT` | Minimum confidence threshold | 0.5 |

**Entity Types:**
- `PERSON` - People, including fictional
- `ORG` - Organizations, companies, agencies
- `GPE` - Countries, cities, states
- `LOC` - Non-GPE locations
- `DATE` - Absolute or relative dates
- `TIME` - Times smaller than a day
- `MONEY` - Monetary values
- `PERCENT` - Percentage values

**Examples:**
```bash
# Extract all entities
python doc-processor.py ner document.pdf

# Extract only persons and organizations
python doc-processor.py ner document.pdf --entities PERSON ORG

# Extract with high confidence threshold
python doc-processor.py ner document.pdf --min-confidence 0.8

# Save to CSV
python doc-processor.py ner document.pdf --format csv --output entities.csv
```

**Output Example:**
```json
{
  "entities": [
    {
      "text": "John Doe",
      "type": "PERSON",
      "start": 0,
      "end": 8,
      "confidence": 0.95
    },
    {
      "text": "Acme Corporation",
      "type": "ORG",
      "start": 18,
      "end": 34,
      "confidence": 0.92
    }
  ],
  "total": 2
}
```

---

### Command: `classify`

Classify documents into predefined categories using TF-IDF + SVM.

**Usage:**
```bash
python doc-processor.py classify <file> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output FILE` | Save results to file | stdout |
| `--show-probabilities` | Show all category probabilities | false |

**Categories:**
- `SOCIAL_SERVICES` - Social service documents
- `HEALTHCARE` - Medical and healthcare
- `EDUCATION` - Educational materials
- `LEGAL` - Legal documents
- `FINANCIAL` - Financial reports
- `TECHNICAL` - Technical documentation
- `OTHER` - Uncategorized

**Examples:**
```bash
# Basic classification
python doc-processor.py classify document.pdf

# Show all probabilities
python doc-processor.py classify document.pdf --show-probabilities

# Save results
python doc-processor.py classify document.pdf --output classification.json
```

**Output Example:**
```json
{
  "category": "SOCIAL_SERVICES",
  "confidence": 0.925,
  "probabilities": {
    "SOCIAL_SERVICES": 0.925,
    "HEALTHCARE": 0.045,
    "EDUCATION": 0.020,
    "OTHER": 0.010
  }
}
```

---

### Command: `relations`

Extract relationships between entities and build knowledge graphs.

**Usage:**
```bash
python doc-processor.py relations <file> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output FILE` | Save results to file | stdout |
| `--graph FILE` | Build and save knowledge graph | none |
| `--graph-format FORMAT` | Graph format (json, cypher, graphml) | json |
| `--min-confidence FLOAT` | Minimum confidence threshold | 0.5 |

**Relation Types:**
- `WORKS_AT` - Employment relationship
- `LOCATED_IN` - Location relationship
- `OWNS` - Ownership
- `MANAGES` - Management
- `FOUNDED_BY` - Founder relationship
- `MEMBER_OF` - Membership

**Examples:**
```bash
# Extract relations
python doc-processor.py relations document.pdf

# Build knowledge graph
python doc-processor.py relations document.pdf --graph graph.json

# Export as Cypher (for Neo4j)
python doc-processor.py relations document.pdf --graph graph.cypher --graph-format cypher

# High confidence relations only
python doc-processor.py relations document.pdf --min-confidence 0.8
```

**Output Example:**
```json
{
  "relations": [
    {
      "source": "John Doe",
      "source_type": "PERSON",
      "relation": "WORKS_AT",
      "target": "Acme Corporation",
      "target_type": "ORG",
      "confidence": 0.85
    }
  ],
  "total": 1
}
```

---

### Command: `batch`

Process multiple documents in a directory.

**Usage:**
```bash
python doc-processor.py batch <directory> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir DIR` | Output directory for results | ./results |
| `--format FORMAT` | Output format | json |
| `--recursive` | Process subdirectories | false |
| `--pattern PATTERN` | File pattern to match | *.pdf |
| `--parallel` | Use parallel processing | false |
| `--workers N` | Number of parallel workers | 4 |

**Examples:**
```bash
# Process all PDFs in directory
python doc-processor.py batch /path/to/documents/ --output-dir results/

# Process all files recursively
python doc-processor.py batch /path/to/documents/ --recursive

# Parallel processing for speed
python doc-processor.py batch /path/to/documents/ --parallel --workers 8

# Process only specific files
python doc-processor.py batch /path/to/documents/ --pattern "report_*.pdf"
```

**Output:**
```
📁 Processing batch: /path/to/documents/
  ├─ ✅ document1.pdf (2.3s)
  ├─ ✅ document2.pdf (1.8s)
  ├─ ⚠️  document3.pdf (failed: invalid format)
  └─ ✅ document4.pdf (3.1s)

Summary:
  Total: 4 documents
  Success: 3
  Failed: 1
  Time: 7.2s
```

---

### Command: `analyze`

Complete document analysis with all features combined.

**Usage:**
```bash
python doc-processor.py analyze <file> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--full` | Enable all analysis features | false |
| `--output FILE` | Save results to file | stdout |
| `--export FORMAT` | Export format (json, excel, pdf) | json |
| `--save-db` | Save to database | false |

**Analysis Includes:**
- Text extraction and metadata
- Named entity recognition
- Document classification
- Topic modeling
- Relation extraction
- Knowledge graph construction

**Examples:**
```bash
# Full analysis
python doc-processor.py analyze document.pdf --full

# Export to Excel
python doc-processor.py analyze document.pdf --full --export excel --output report.xlsx

# Export to PDF report
python doc-processor.py analyze document.pdf --full --export pdf --output report.pdf

# Save everything to database
python doc-processor.py analyze document.pdf --full --save-db
```

**Output Structure:**
```json
{
  "document": {
    "filename": "document.pdf",
    "text_length": 5234,
    "word_count": 856
  },
  "entities": [...],
  "classification": {...},
  "topics": [...],
  "relations": [...],
  "knowledge_graph": {...}
}
```

---

## 💼 Use Cases

### Use Case 1: Extract Names from Legal Document

**Scenario:** You have a contract and need to extract all person and organization names.

```bash
# Extract persons and organizations
python doc-processor.py ner contract.pdf --entities PERSON ORG --output names.json

# Review the output
cat names.json

# Example output shows:
# - All parties mentioned in contract
# - Their roles (person vs organization)
# - Confidence scores
```

**Why it's useful:** Quickly identify all parties in legal documents without manual reading.

---

### Use Case 2: Categorize Incoming Documents

**Scenario:** You receive 100+ documents daily and need automatic categorization.

```bash
# Process directory of documents
python doc-processor.py batch /inbox/documents/ \
  --output-dir /categorized/ \
  --parallel \
  --workers 8

# Each document gets:
# - Classified into category
# - Saved to appropriate folder
# - Metadata extracted
```

**Why it's useful:** Automate document sorting and routing in your workflow.

---

### Use Case 3: Build Knowledge Base from Reports

**Scenario:** You have annual reports and want to build a knowledge graph.

```bash
# Process multiple reports and build unified graph
for report in reports/*.pdf; do
  python doc-processor.py relations "$report" \
    --graph "graphs/$(basename $report .pdf).json"
done

# Merge graphs (custom script or manual)
# Import to Neo4j or other graph database
```

**Why it's useful:** Discover hidden connections and relationships across documents.

---

### Use Case 4: Quality Analysis Pipeline

**Scenario:** Before publishing, analyze document quality and completeness.

```bash
# Full analysis with quality metrics
python doc-processor.py analyze draft.pdf \
  --full \
  --export excel \
  --output quality_report.xlsx

# Review:
# - Entity coverage (are key terms present?)
# - Classification confidence
# - Topic distribution
# - Relation completeness
```

**Why it's useful:** Ensure document quality before distribution.

---

## 🔧 Advanced Features

### Custom Entity Types

Train the NER engine on custom entity types:

```bash
# (Future feature - coming in v2.0)
python doc-processor.py ner document.pdf \
  --custom-entities PROJECT,SKILL,TOOL \
  --training-data custom_ner.json
```

### Pipeline Configuration

Create custom analysis pipelines:

```bash
# Custom pipeline YAML
cat > pipeline.yaml <<EOF
steps:
  - extract_text
  - ner:
      entities: [PERSON, ORG]
  - classify
  - export:
      format: excel
EOF

python doc-processor.py pipeline document.pdf --config pipeline.yaml
```

### Integration with Database

All commands support database integration:

```bash
# Save to database
python doc-processor.py analyze document.pdf --full --save-db

# Query database later
python -c "
from src.core.database import DocumentDatabase
db = DocumentDatabase()
docs = db.search_documents('social services')
print(f'Found {len(docs)} documents')
"
```

---

## ❗ Troubleshooting

### Issue: "spaCy model not found"

**Error:**
```
OSError: Can't find model 'en_core_web_sm'
```

**Solution:**
```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
```

---

### Issue: "Failed to parse PDF"

**Error:**
```
ParsingError: Failed to extract text from PDF
```

**Solutions:**
1. **Try OCR:** Some PDFs are scanned images
2. **Check file integrity:** Ensure PDF is not corrupted
3. **Update libraries:** `pip install --upgrade PyPDF2 pdfplumber`

```bash
# Alternative PDF libraries
pip install pdfminer.six pymupdf

# Test with different parser
python doc-processor.py process document.pdf --parser mupdf
```

---

### Issue: "Out of memory" during batch processing

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**
1. **Reduce parallel workers:**
```bash
python doc-processor.py batch documents/ --workers 2
```

2. **Process in smaller batches:**
```bash
# Split into chunks
find documents/ -name "*.pdf" | head -50 | xargs -I {} python doc-processor.py process {}
```

3. **Increase system memory or use swap**

---

### Issue: "Low classification confidence"

**Symptom:** Classification confidence below 60%

**Solutions:**
1. **Retrain classifier with more data**
2. **Use manual classification for ambiguous docs**
3. **Check if document fits predefined categories**

```bash
# Show all probabilities to see alternatives
python doc-processor.py classify document.pdf --show-probabilities

# Example output might show multiple similar scores:
# SOCIAL_SERVICES: 0.45
# HEALTHCARE: 0.42
# EDUCATION: 0.13
# -> Document spans multiple categories
```

---

### Issue: "No entities found"

**Symptom:** NER returns empty list

**Possible causes:**
1. **Document is too short** (< 50 words)
2. **Language mismatch** (non-English text with English model)
3. **Low-quality text extraction**

**Solutions:**
```bash
# Check extracted text quality
python doc-processor.py process document.pdf --format text | head -20

# Try Russian model if text is Russian
# (Configure in settings or code)

# Lower confidence threshold
python doc-processor.py ner document.pdf --min-confidence 0.3
```

---

## 💡 Tips & Best Practices

### 1. Start Simple, Scale Up

```bash
# ❌ Don't start with: Full pipeline on 1000 documents
# ✅ Do start with: Single document analysis

# Test on one document first
python doc-processor.py analyze test.pdf --full

# If good, scale to batch
python doc-processor.py batch documents/ --parallel
```

### 2. Use Appropriate Output Formats

```bash
# JSON for automation
python doc-processor.py ner doc.pdf --format json > entities.json

# CSV for Excel/spreadsheets
python doc-processor.py ner doc.pdf --format csv > entities.csv

# Text for quick review
python doc-processor.py process doc.pdf --format text | less
```

### 3. Set Confidence Thresholds

```bash
# High confidence for critical applications
python doc-processor.py ner doc.pdf --min-confidence 0.9

# Lower threshold for discovery
python doc-processor.py ner doc.pdf --min-confidence 0.5
```

### 4. Organize Batch Outputs

```bash
# Create organized directory structure
mkdir -p results/{entities,classifications,graphs}

# Process with appropriate outputs
python doc-processor.py batch documents/ \
  --output-dir results/entities \
  --format json
```

### 5. Monitor Performance

```bash
# Time your operations
time python doc-processor.py batch documents/

# Use verbose logging
export LOG_LEVEL=DEBUG
python doc-processor.py analyze doc.pdf
```

### 6. Combine with Other Tools

```bash
# Pipeline example: Extract, analyze, merge
python doc-processor.py ner doc.pdf --format json | \
  jq '.entities[] | select(.type == "PERSON")' | \
  python doc-merger.py --input - --output people.json
```

### 7. Backup Before Batch Operations

```bash
# Always backup before large batch operations
tar -czf backup_$(date +%Y%m%d).tar.gz documents/

# Then process
python doc-processor.py batch documents/ --save-db
```

---

## 📊 Performance Tips

### Expected Processing Times

| Document Size | Basic Processing | Full Analysis |
|---------------|------------------|---------------|
| 1 page | ~0.5s | ~2s |
| 10 pages | ~2s | ~8s |
| 100 pages | ~15s | ~60s |
| 1000 pages | ~2min | ~10min |

### Optimization Strategies

1. **Use parallel processing for batches:**
```bash
python doc-processor.py batch docs/ --parallel --workers 8
```

2. **Skip unnecessary analysis:**
```bash
# Only NER, skip classification
python doc-processor.py ner doc.pdf
```

3. **Use faster models:**
```bash
# Use smaller spaCy model (faster but less accurate)
python -m spacy download en_core_web_sm  # vs en_core_web_lg
```

---

## 📞 Getting Help

### Command Help

```bash
# General help
python doc-processor.py --help

# Command-specific help
python doc-processor.py ner --help
python doc-processor.py classify --help
```

### Logging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python doc-processor.py analyze doc.pdf

# Log to file
python doc-processor.py batch docs/ 2>&1 | tee processing.log
```

### Support Resources

- **Documentation**: `docs/README.md`
- **API Reference**: `docs/api/`
- **GitHub Issues**: https://github.com/svend4/daten20/issues
- **Email Support**: support@example.com

---

## 🔄 Related Tools

- **doc-comparator.py** - Compare documents
- **doc-quality.py** - Assess document quality
- **doc-search.py** - Search document database
- **doc-batch-processor.py** - Advanced batch operations
- **doc-dashboard.py** - Visual interface for processing

---

## 📝 Changelog

### v1.0.0 (2026-01-14)
- ✅ Initial release
- ✅ Basic processing commands
- ✅ NER with spaCy
- ✅ Document classification
- ✅ Relation extraction
- ✅ Knowledge graph construction
- ✅ Batch processing
- ✅ Multiple export formats

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
**Author:** DMS Team
