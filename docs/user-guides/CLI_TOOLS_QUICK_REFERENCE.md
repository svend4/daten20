# 🚀 CLI Tools Quick Reference

**Fast reference for all DMS command-line tools**

---

## 📋 Tool Index

| # | Tool | Purpose | Common Command |
|---|------|---------|----------------|
| 1 | [doc-comparator](#1-doc-comparator) | Compare documents | `compare doc1.pdf doc2.pdf` |
| 2 | [doc-anonymizer](#2-doc-anonymizer) | Remove PII | `anonymize doc.pdf --output anon.pdf` |
| 3 | [doc-quality](#3-doc-quality) | Quality check | `analyze doc.pdf` |
| 4 | [doc-master](#4-doc-master) | Create documents | `create --template letter` |
| 5 | [doc-processor](#5-doc-processor) | Process documents | `process doc.pdf --operation extract` |
| 6 | [doc-merger](#6-doc-merger) | Merge documents | `merge *.pdf --output combined.pdf` |
| 7 | [doc-splitter](#7-doc-splitter) | Split documents | `split large.pdf --pages-per-file 10` |
| 8 | [doc-batch-processor](#8-doc-batch-processor) | Batch operations | `batch convert /docs/ --format pdf` |
| 9 | [doc-search](#9-doc-search) | Search documents | `search "query" --limit 20` |
| 10 | [doc-dashboard](#10-doc-dashboard) | Web interface | `--port 5000` |
| 11 | [doc-api-server](#11-doc-api-server) | API server | `--host 0.0.0.0 --port 8000` |
| 12 | [dms-admin](#12-dms-admin) | Administration | `users list` |
| 13 | [enterprise-admin](#13-enterprise-admin) | Enterprise admin | `tenants list` |

---

## 1. doc-comparator

**Compare two documents**

```bash
# Basic comparison
python doc-comparator.py compare doc1.pdf doc2.pdf

# HTML report
python doc-comparator.py compare doc1.pdf doc2.pdf \
    --report html --output diff.html

# High threshold
python doc-comparator.py compare doc1.pdf doc2.pdf --threshold 0.9

# Entities only
python doc-comparator.py compare doc1.pdf doc2.pdf --entities-only
```

**Methods:** cosine, jaccard, levenshtein, entity, all

---

## 2. doc-anonymizer

**Anonymize PII in documents**

```bash
# Scan for PII
python doc-anonymizer.py scan document.pdf

# Basic anonymization (redaction)
python doc-anonymizer.py anonymize document.pdf --output anon.pdf

# Masking
python doc-anonymizer.py anonymize doc.pdf \
    --strategy masking --output masked.pdf

# GDPR compliant with audit
python doc-anonymizer.py anonymize doc.pdf \
    --compliance gdpr --audit-log --output anon.pdf

# Reversible
python doc-anonymizer.py anonymize doc.pdf \
    --reversible --mapping-file map.enc --output anon.pdf

# De-anonymize
python doc-anonymizer.py deanonymize anon.pdf \
    --mapping-file map.enc --output original.pdf

# Batch
python doc-anonymizer.py batch /docs/ --output-dir /anon/
```

**Strategies:** redaction, masking, replacement, encryption

---

## 3. doc-quality

**Check document quality**

```bash
# Full analysis
python doc-quality.py analyze document.pdf --full

# Specific dimension
python doc-quality.py analyze doc.pdf --dimension completeness

# With threshold
python doc-quality.py analyze doc.pdf --threshold 80 --fail-on-low-quality

# HTML report
python doc-quality.py analyze doc.pdf --report html --output quality.html

# Batch check
python doc-quality.py batch /docs/ --output report.json
```

**Dimensions:** completeness, consistency, accuracy, readability, compliance, formatting

---

## 4. doc-master

**Create documents with wizard**

```bash
# Interactive wizard
python doc-master.py create

# Use template
python doc-master.py create --template business_letter --output letter.pdf

# Non-interactive
python doc-master.py create \
    --non-interactive --config doc_config.yaml --output report.pdf
```

---

## 5. doc-processor

**Process documents**

```bash
# Extract text
python doc-processor.py process doc.pdf \
    --operation extract --output text.txt

# Convert format
python doc-processor.py process doc.pdf \
    --operation convert --format docx --output doc.docx

# OCR
python doc-processor.py process scanned.pdf \
    --operation ocr --language eng --output text.txt

# Extract metadata
python doc-processor.py process doc.pdf \
    --operation metadata --output metadata.json

# Extract images
python doc-processor.py process doc.pdf \
    --operation images --output ./images/
```

**Operations:** extract, convert, ocr, metadata, images

---

## 6. doc-merger

**Merge multiple documents**

```bash
# Basic merge
python doc-merger.py merge doc1.pdf doc2.pdf doc3.pdf --output combined.pdf

# With TOC
python doc-merger.py merge *.pdf \
    --output report.pdf --toc --page-numbers

# With bookmarks
python doc-merger.py merge chapter*.pdf \
    --output book.pdf --bookmarks --toc
```

---

## 7. doc-splitter

**Split large documents**

```bash
# Split by pages
python doc-splitter.py split large.pdf \
    --method pages --pages-per-file 10 --output-dir ./parts/

# Split by bookmarks
python doc-splitter.py split book.pdf \
    --method bookmarks --output-dir ./chapters/

# Extract specific pages
python doc-splitter.py split doc.pdf \
    --pages "1-5,10-15,20" --output-dir ./extracts/
```

**Methods:** pages, bookmarks, sections, size

---

## 8. doc-batch-processor

**Batch process documents**

```bash
# Batch convert
python doc-batch-processor.py batch convert /docs/ \
    --output-dir /pdfs/ --format pdf --parallel 8

# Batch anonymize
python doc-batch-processor.py batch anonymize /docs/ \
    --output-dir /anon/ --recursive

# Batch quality check
python doc-batch-processor.py batch quality /docs/ \
    --log-file report.json --recursive

# Resume
python doc-batch-processor.py batch convert /docs/ \
    --resume --log-file batch.log
```

**Operations:** convert, extract, anonymize, quality, compress

---

## 9. doc-search

**Search documents**

```bash
# Basic search
python doc-search.py search "document management"

# Semantic search
python doc-search.py search "contract agreements" \
    --method semantic --limit 20

# With filters
python doc-search.py search "financial report" \
    --filters "type:pdf,date:2024-*" --limit 50

# Export results
python doc-search.py search "meeting notes" \
    --format json --output results.json
```

**Methods:** fulltext, semantic, fuzzy, phrase

---

## 10. doc-dashboard

**Start web dashboard**

```bash
# Default
python doc-dashboard.py

# Custom port
python doc-dashboard.py --host 0.0.0.0 --port 8080

# Development mode
python doc-dashboard.py --debug --reload

# Production
python doc-dashboard.py --host 0.0.0.0 --port 80 --config production.yaml
```

**Access:** http://localhost:5000

---

## 11. doc-api-server

**Start REST API server**

```bash
# Default
python doc-api-server.py

# Custom configuration
python doc-api-server.py --host 0.0.0.0 --port 8080 --workers 8

# Development
python doc-api-server.py --debug --reload

# Production
python doc-api-server.py --host 0.0.0.0 --port 8000 --workers 16
```

**Docs:**
- Swagger: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## 12. dms-admin

**DMS administration**

```bash
# User management
python dms-admin.py users list
python dms-admin.py users create --username john --email john@example.com
python dms-admin.py users reset-password john

# Database
python dms-admin.py database migrate
python dms-admin.py database backup --output backup.sql
python dms-admin.py database restore backup.sql

# System
python dms-admin.py system status
python dms-admin.py system config --show
python dms-admin.py system logs --tail 100
python dms-admin.py system cleanup --older-than 30d
```

---

## 13. enterprise-admin

**Enterprise administration**

```bash
# Tenant management
python enterprise-admin.py tenants list
python enterprise-admin.py tenants create --name "Acme" --plan enterprise
python enterprise-admin.py tenants configure acme --setting "quota=1TB"

# Security
python enterprise-admin.py security audit --days 7 --export audit.json
python enterprise-admin.py security compliance --standard GDPR --output report.pdf
python enterprise-admin.py security scan

# Analytics
python enterprise-admin.py analytics usage --month 2024-01
python enterprise-admin.py analytics performance --output perf.html
python enterprise-admin.py analytics export --format csv --output analytics.csv
```

---

## 🔧 Common Options

All tools support:

```bash
-h, --help              # Show help
--version               # Show version
-v, --verbose           # Verbose output
-q, --quiet             # Quiet mode
--log-level LEVEL       # Logging level
--log-file FILE         # Log to file
--config FILE           # Configuration file
```

---

## 💡 Quick Tips

### 1. Use Config Files

```yaml
# config.yaml
input_dir: /documents
output_dir: /processed
format: pdf
```

```bash
python doc-batch-processor.py --config config.yaml
```

### 2. Chain Commands

```bash
# Quality check, then process
python doc-quality.py analyze doc.pdf --threshold 80 && \
python doc-processor.py process doc.pdf --operation extract
```

### 3. Batch Operations

```bash
# Process multiple files
python doc-anonymizer.py batch /documents/ --output-dir /anonymized/
```

### 4. Export Results

```bash
# Save to JSON for automation
python doc-search.py search "query" --format json --output results.json
```

### 5. Enable Logging

```bash
# Log everything
python doc-processor.py process doc.pdf --log-file processing.log --log-level DEBUG
```

---

## 📊 Comparison Matrix

| Feature | Comparator | Anonymizer | Quality | Processor | Search |
|---------|-----------|------------|---------|-----------|--------|
| Read PDF | ✅ | ✅ | ✅ | ✅ | ✅ |
| Write PDF | ❌ | ✅ | ❌ | ✅ | ❌ |
| Batch | ❌ | ✅ | ✅ | ❌ | ❌ |
| Reports | ✅ | ✅ | ✅ | ❌ | ✅ |
| OCR | ❌ | ❌ | ❌ | ✅ | ✅ |
| NLP | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Import error | `pip install -r requirements.txt` |
| Permission denied | `chmod +x *.py` |
| Module not found | `export PYTHONPATH="$(pwd)"` |
| Database error | `python dms-admin.py database migrate --reset` |
| Port in use | Use different port: `--port 5001` |

---

## 📚 Full Documentation

For detailed documentation, see:
- **Master Guide:** `docs/user-guides/CLI_TOOLS_MASTER_GUIDE.md`
- **API Docs:** `docs/API_DOCUMENTATION_GUIDE.md`
- **Deployment:** `docs/DEPLOYMENT_GUIDE.md`

---

**Version:** 4.1.0
**Last Updated:** 2026-01-16
**Quick Reference for:** All 13 CLI Tools
