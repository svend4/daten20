# 📚 Document Management System - User Guides

**Version:** 4.1.0
**Last Updated:** 2026-01-16
**Total Guides:** 13 CLI Tools

Welcome to the comprehensive user guide collection for the Document Management System (DMS). This guide helps you choose the right tool for your task.

## 📚 New: Complete Documentation

- **[Master Guide](CLI_TOOLS_MASTER_GUIDE.md)** - Complete documentation for all 13 CLI tools (1200+ lines)
- **[Quick Reference](CLI_TOOLS_QUICK_REFERENCE.md)** - Fast reference guide with examples (300+ lines)

These comprehensive guides include detailed usage examples, best practices, and troubleshooting for every tool.

---

## 🎯 Quick Tool Selector

**"I want to..."** → **Use this tool:**

| Task | Tool | Guide |
|------|------|-------|
| Extract text from documents | [doc-processor.py](doc-processor.md) | Basic processing |
| Compare two documents | [doc-comparator.py](doc-comparator.md) | Similarity metrics |
| Remove sensitive data (GDPR) | [doc-anonymizer.py](doc-anonymizer.md) | PII removal |
| Check document quality | [doc-quality.py](doc-quality.md) | Quality assessment |
| Search through documents | [doc-search.py](doc-search.md) | Full-text & semantic search |
| Combine multiple documents | [doc-merger.py](doc-merger.md) | Document merging |
| Split large documents | [doc-splitter.py](doc-splitter.md) | Document splitting |
| Process many files at once | [doc-batch-processor.py](doc-batch-processor.md) | Batch operations |
| Use visual interface | [doc-dashboard.py](doc-dashboard.md) | Web UI |
| Manage all services | [doc-master.py](doc-master.md) | Service orchestration |
| Access via API | [doc-api-server.py](doc-api-server.md) | REST API |
| Administer system | [dms-admin.py](CLI_TOOLS_MASTER_GUIDE.md#12-dms-admin) | DMS administration |
| Enterprise management | [enterprise-admin.py](CLI_TOOLS_MASTER_GUIDE.md#13-enterprise-admin) | Enterprise admin |

---

## 📖 Available Tools

### 1. doc-processor.py - Core Document Processing

**Purpose:** Main document processing tool with AI/ML capabilities

**Key Features:**
- ✅ Text extraction from PDF, DOCX, TXT, HTML
- ✅ Named Entity Recognition (NER)
- ✅ Document classification
- ✅ Topic modeling
- ✅ Relation extraction
- ✅ Knowledge graph construction

**When to use:**
- Processing individual documents
- Extracting entities (persons, organizations, locations)
- Classifying documents into categories
- Building knowledge graphs

**Quick Example:**
```bash
# Extract all entities from a document
python doc-processor.py ner contract.pdf --entities PERSON ORG

# Full analysis with all AI features
python doc-processor.py analyze report.pdf --full --export excel
```

**[📄 Full Guide →](doc-processor.md)**

---

### 2. doc-comparator.py - Document Comparison

**Purpose:** Compare documents using various similarity metrics

**Key Features:**
- ✅ Cosine similarity (semantic comparison)
- ✅ Jaccard similarity (word overlap)
- ✅ Levenshtein distance (edit distance)
- ✅ Side-by-side diff visualization
- ✅ Batch comparison mode

**When to use:**
- Finding duplicate documents
- Detecting plagiarism
- Version comparison
- Quality assurance

**Quick Example:**
```bash
# Compare two versions of a document
python doc-comparator.py doc_v1.pdf doc_v2.pdf --metric cosine

# Batch compare all documents in folder
python doc-comparator.py compare-batch folder/ --threshold 0.8
```

**[📄 Full Guide →](doc-comparator.md)**

---

### 3. doc-anonymizer.py - Data Anonymization

**Purpose:** GDPR-compliant removal of personally identifiable information (PII)

**Key Features:**
- ✅ Automatic PII detection (emails, phones, names, addresses)
- ✅ GDPR compliance
- ✅ Reversible anonymization with mapping
- ✅ Detailed anonymization reports
- ✅ Multiple anonymization strategies

**When to use:**
- Preparing documents for public release
- GDPR compliance requirements
- Privacy protection
- Data sharing scenarios

**Quick Example:**
```bash
# Anonymize all PII in document
python doc-anonymizer.py sensitive.pdf --output clean.pdf

# Keep mapping for reversibility
python doc-anonymizer.py data.pdf --output anonymized.pdf --keep-mapping map.json
```

**[📄 Full Guide →](doc-anonymizer.md)**

---

### 4. doc-quality.py - Quality Assessment

**Purpose:** Assess document quality across 5 dimensions

**Key Features:**
- ✅ Readability analysis (Flesch Reading Ease)
- ✅ Grammar checking
- ✅ Structure assessment
- ✅ Completeness evaluation
- ✅ Consistency checking

**When to use:**
- Quality control before publishing
- Comparing document versions
- Identifying improvement areas
- Ensuring professional standards

**Quick Example:**
```bash
# Quick quality check
python doc-quality.py document.pdf

# Detailed analysis with recommendations
python doc-quality.py document.pdf --detailed --recommendations
```

**[📄 Full Guide →](doc-quality.md)**

---

### 5. doc-search.py - Document Search

**Purpose:** Search and retrieve documents using full-text or semantic search

**Key Features:**
- ✅ Full-text search with indexing
- ✅ Semantic search with embeddings
- ✅ Faceted search (filter by metadata)
- ✅ Search history and saved queries
- ✅ Result ranking and relevance

**When to use:**
- Finding specific documents
- Exploring document collections
- Research and discovery
- Building search interfaces

**Quick Example:**
```bash
# Semantic search across documents
python doc-search.py "social services planning" --semantic

# Full-text search with filters
python doc-search.py "budget" --region Bavaria --type financial
```

**[📄 Full Guide →](doc-search.md)**

---

### 6. doc-merger.py - Document Merging

**Purpose:** Combine multiple documents into one

**Key Features:**
- ✅ Intelligent merging with TOC
- ✅ Format preservation
- ✅ Page numbering
- ✅ Metadata consolidation
- ✅ Multiple output formats

**When to use:**
- Combining reports
- Creating compilations
- Merging related documents
- Generating master documents

**Quick Example:**
```bash
# Merge PDFs with table of contents
python doc-merger.py doc1.pdf doc2.pdf doc3.pdf --output merged.pdf --toc

# Merge and reformat
python doc-merger.py *.pdf --output combined.docx
```

**[📄 Full Guide →](doc-merger.md)**

---

### 7. doc-splitter.py - Document Splitting

**Purpose:** Split large documents into smaller parts

**Key Features:**
- ✅ Split by pages, sections, size
- ✅ Intelligent chapter detection
- ✅ Metadata preservation
- ✅ Automatic naming
- ✅ Parallel splitting

**When to use:**
- Breaking up large files
- Extracting specific sections
- Creating chapter-wise documents
- Size optimization

**Quick Example:**
```bash
# Split PDF into 10-page chunks
python doc-splitter.py large.pdf --pages 10 --output chunks/

# Smart split by chapters
python doc-splitter.py book.pdf --smart --output chapters/
```

**[📄 Full Guide →](doc-splitter.md)**

---

### 8. doc-batch-processor.py - Batch Operations

**Purpose:** Advanced batch processing with parallel execution

**Key Features:**
- ✅ Parallel processing
- ✅ Job queuing and scheduling
- ✅ Progress tracking
- ✅ Error recovery
- ✅ Custom pipelines

**When to use:**
- Processing hundreds/thousands of documents
- Scheduled processing jobs
- Complex multi-step workflows
- High-performance requirements

**Quick Example:**
```bash
# Parallel batch processing
python doc-batch-processor.py process documents/ --workers 8 --output results/

# Scheduled job with pipeline
python doc-batch-processor.py schedule pipeline.yaml --cron "0 2 * * *"
```

**[📄 Full Guide →](doc-batch-processor.md)**

---

### 9. doc-dashboard.py - Web Dashboard

**Purpose:** Interactive web interface for document management

**Key Features:**
- ✅ Visual document browser
- ✅ Drag-and-drop upload
- ✅ Real-time analytics
- ✅ Interactive visualizations
- ✅ User management

**When to use:**
- Visual document management
- Team collaboration
- Non-technical users
- Real-time monitoring

**Quick Example:**
```bash
# Start dashboard
python doc-dashboard.py

# Access at: http://localhost:5000
```

**[📄 Full Guide →](doc-dashboard.md)**

---

### 10. doc-master.py - Service Orchestration

**Purpose:** Master control panel for managing all DMS services

**Key Features:**
- ✅ Service status monitoring
- ✅ Start/stop/restart services
- ✅ Health checks
- ✅ Resource monitoring
- ✅ Configuration management

**When to use:**
- Managing multiple services
- System administration
- Deployment and operations
- Troubleshooting

**Quick Example:**
```bash
# Check all services status
python doc-master.py status

# Start all services
python doc-master.py start --all

# Health check with auto-restart
python doc-master.py health --auto-restart
```

**[📄 Full Guide →](doc-master.md)**

---

### 11. doc-api-server.py - REST API

**Purpose:** FastAPI REST API server for programmatic access

**Key Features:**
- ✅ RESTful API endpoints
- ✅ OpenAPI/Swagger documentation
- ✅ Authentication and rate limiting
- ✅ Async processing
- ✅ WebSocket support

**When to use:**
- Building integrations
- Automation scripts
- External applications
- Microservices architecture

**Quick Example:**
```bash
# Start API server
python doc-api-server.py --port 8000

# API docs at: http://localhost:8000/docs
```

**[📄 Full Guide →](doc-api-server.md)**

---

## 🔄 Common Workflows

### Workflow 1: Document Quality Pipeline

**Goal:** Ensure document quality before publication

```bash
# Step 1: Check quality
python doc-quality.py draft.pdf --detailed

# Step 2: Anonymize if needed
python doc-anonymizer.py draft.pdf --output clean.pdf

# Step 3: Final quality check
python doc-quality.py clean.pdf

# Step 4: Publish
# (if quality > 80%)
```

---

### Workflow 2: Batch Processing Pipeline

**Goal:** Process large document collection

```bash
# Step 1: Batch process all documents
python doc-batch-processor.py process documents/ --workers 8

# Step 2: Search and filter results
python doc-search.py "important" --semantic

# Step 3: Merge selected documents
python doc-merger.py selected/*.pdf --output compilation.pdf
```

---

### Workflow 3: Knowledge Discovery

**Goal:** Extract insights from document collection

```bash
# Step 1: Process documents with NER
python doc-processor.py batch documents/ --ner --save-db

# Step 2: Build knowledge graph
python doc-processor.py relations documents/ --graph knowledge.json

# Step 3: Search by entities
python doc-search.py "John Doe" --entity-search

# Step 4: Visualize in dashboard
python doc-dashboard.py
# Navigate to Knowledge Graph view
```

---

### Workflow 4: Compliance & Privacy

**Goal:** Ensure GDPR compliance for documents

```bash
# Step 1: Scan for PII
python doc-anonymizer.py scan documents/ --report pii_report.csv

# Step 2: Anonymize documents
python doc-anonymizer.py anonymize documents/ --output clean/ --keep-mapping

# Step 3: Quality check anonymized docs
python doc-quality.py clean/sample.pdf

# Step 4: Store with audit trail
python doc-processor.py process clean/ --save-db --audit
```

---

## 💡 Tips & Best Practices

### 1. Start Small, Scale Up

```bash
# ❌ Don't: Process 1000 documents immediately
# ✅ Do: Test on 10 documents first

python doc-processor.py batch test_batch/ --workers 2
# If good, scale up:
python doc-batch-processor.py process all_documents/ --workers 8
```

### 2. Use Pipelines for Complex Tasks

```bash
# Create reusable pipeline
cat > pipeline.yaml <<EOF
steps:
  - doc-processor: { command: ner }
  - doc-quality: { command: check }
  - doc-anonymizer: { command: anonymize }
EOF

python doc-batch-processor.py pipeline documents/ --config pipeline.yaml
```

### 3. Monitor Performance

```bash
# Enable detailed logging
export LOG_LEVEL=INFO

# Track processing time
time python doc-batch-processor.py process large_batch/

# Use dashboard for real-time monitoring
python doc-dashboard.py &
# Monitor at http://localhost:5000/metrics
```

### 4. Backup Before Batch Operations

```bash
# Always backup
tar -czf backup_$(date +%Y%m%d).tar.gz documents/

# Then process
python doc-batch-processor.py process documents/
```

### 5. Combine Tools for Power

```bash
# Powerful one-liner combining tools
python doc-search.py "financial" --format json | \
  jq '.results[].path' | \
  xargs python doc-merger.py --output financial_reports.pdf
```

---

## 📊 Tool Comparison

### Processing Speed

| Tool | Single Doc | Batch (100 docs) | Parallel Support |
|------|------------|------------------|------------------|
| doc-processor | ~2s | ~200s | ❌ No |
| doc-batch-processor | ~2s | ~25s | ✅ Yes (8x faster) |
| doc-comparator | ~1s | ~100s | ✅ Yes |
| doc-anonymizer | ~3s | ~300s | ❌ No |
| doc-quality | ~4s | ~400s | ❌ No |

**Recommendation:** Use `doc-batch-processor.py` for processing > 10 documents.

---

### Feature Matrix

| Feature | Processor | Comparator | Anonymizer | Quality | Search |
|---------|-----------|------------|------------|---------|--------|
| NER | ✅ | ❌ | ❌ | ❌ | ✅ |
| Classification | ✅ | ❌ | ❌ | ❌ | ✅ |
| PII Detection | ❌ | ❌ | ✅ | ❌ | ❌ |
| Similarity | ❌ | ✅ | ❌ | ❌ | ✅ |
| Quality Metrics | ❌ | ❌ | ❌ | ✅ | ❌ |
| Batch Mode | ✅ | ✅ | ✅ | ✅ | ✅ |
| API Access | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🆘 Getting Help

### General Help

```bash
# Any tool help
python <tool-name>.py --help

# Command-specific help
python doc-processor.py ner --help
```

### Logging & Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python doc-processor.py analyze doc.pdf

# View logs
tail -f logs/dms.log
```

### Documentation

- **User Guides:** `docs/user-guides/` (This directory)
- **API Docs:** `docs/api/` or http://localhost:5000/api/docs
- **Architecture:** `docs/ARCHITECTURE.md`
- **Development:** `docs/DEVELOPMENT.md`

### Support Resources

- **GitHub Issues:** https://github.com/svend4/daten20/issues
- **Documentation:** http://localhost:5000/docs
- **Email:** support@example.com

---

## 📦 Installation & Setup

### Quick Setup

```bash
# Clone repository
git clone https://github.com/svend4/daten20.git
cd daten20

# Install dependencies
pip install -r requirements.txt

# Download NER models
python -m spacy download en_core_web_sm
python -m spacy download ru_core_news_sm

# Initialize database
python -c "from src.core.database import Database; Database().init_db()"

# Test installation
python doc-processor.py --help
```

### Docker Setup

```bash
# Build image
docker build -t dms:latest .

# Run container
docker run -it -p 5000:5000 -v $(pwd)/data:/app/data dms:latest

# All tools available inside container
docker exec -it <container-id> python doc-processor.py --help
```

---

## 🔍 Tool Selection Guide

### By Task Type

**Document Analysis & Extraction:**
- Use: `doc-processor.py`
- Capabilities: NER, classification, relations, knowledge graphs

**Document Quality & Compliance:**
- Use: `doc-quality.py` + `doc-anonymizer.py`
- Capabilities: Quality metrics + PII removal

**Document Organization:**
- Use: `doc-search.py` + `doc-merger.py` + `doc-splitter.py`
- Capabilities: Find, combine, split documents

**Bulk Operations:**
- Use: `doc-batch-processor.py`
- Capabilities: Parallel processing, job scheduling

**Visual Interface:**
- Use: `doc-dashboard.py`
- Capabilities: Web UI for all operations

**Programmatic Access:**
- Use: `doc-api-server.py`
- Capabilities: REST API for integrations

**System Management:**
- Use: `doc-master.py`
- Capabilities: Service orchestration

---

## 📝 Version History

### v4.1.0 (2026-01-16) - Phase 4 Task 42 ✅
- ✅ Complete Master Guide for all 13 CLI tools (1200+ lines)
- ✅ Quick Reference Guide (300+ lines)
- ✅ Comprehensive tool documentation with examples
- ✅ Best practices and troubleshooting included
- ✅ Added dms-admin.py and enterprise-admin.py documentation

### v4.0.0 (2026-01-10)
- ✅ All 13 CLI tools production-ready
- ✅ Web dashboard launched
- ✅ API server with OpenAPI docs
- ✅ 172/172 tests passing

---

## 🎓 Learning Path

### Beginner (Week 1)
1. Start with `doc-processor.py` - [Guide](doc-processor.md)
2. Try `doc-search.py` - [Guide](doc-search.md)
3. Explore `doc-dashboard.py` - [Guide](doc-dashboard.md)

### Intermediate (Week 2)
4. Use `doc-comparator.py` - [Guide](doc-comparator.md)
5. Learn `doc-quality.py` - [Guide](doc-quality.md)
6. Try `doc-merger.py` & `doc-splitter.py` - [Guide](doc-merger.md) / [Guide](doc-splitter.md)

### Advanced (Week 3)
7. Master `doc-batch-processor.py` - [Guide](doc-batch-processor.md)
8. Set up `doc-api-server.py` - [Guide](doc-api-server.md)
9. Manage with `doc-master.py` - [Guide](doc-master.md)

### Expert (Week 4)
10. Build custom pipelines
11. Create integrations via API
12. Optimize for production deployment

---

**Last Updated:** 2026-01-14
**Total Documentation:** 142KB (11 guides)
**Maintained By:** DMS Team
