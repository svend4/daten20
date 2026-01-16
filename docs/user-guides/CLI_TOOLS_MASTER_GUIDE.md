# 🛠️ CLI Tools Master Guide

**Document Management System - Complete CLI Reference**

Comprehensive guide for all 13 command-line tools in the DMS system.

**Version:** 4.1.0
**Last Updated:** 2026-01-16
**Status:** Production Ready

---

## 📋 Table of Contents

### Document Processing Tools
1. [doc-comparator.py](#1-doc-comparator) - Document comparison
2. [doc-anonymizer.py](#2-doc-anonymizer) - PII anonymization
3. [doc-quality.py](#3-doc-quality) - Quality assessment
4. [doc-master.py](#4-doc-master) - Document creation wizard
5. [doc-processor.py](#5-doc-processor) - Document processing
6. [doc-merger.py](#6-doc-merger) - Document merging
7. [doc-splitter.py](#7-doc-splitter) - Document splitting
8. [doc-batch-processor.py](#8-doc-batch-processor) - Batch operations
9. [doc-search.py](#9-doc-search) - Advanced search

### System Tools
10. [doc-dashboard.py](#10-doc-dashboard) - Web dashboard
11. [doc-api-server.py](#11-doc-api-server) - API server

### Administration Tools
12. [dms-admin.py](#12-dms-admin) - DMS administration
13. [enterprise-admin.py](#13-enterprise-admin) - Enterprise administration

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/svend4/daten20.git
cd daten20

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Make CLI tools executable (Unix/Linux/Mac)
chmod +x *.py

# Verify installation
python doc-comparator.py --help
```

### First Steps

```bash
# 1. Compare two documents
python doc-comparator.py compare doc1.pdf doc2.pdf

# 2. Anonymize a document
python doc-anonymizer.py anonymize document.pdf --output anonymized.pdf

# 3. Check document quality
python doc-quality.py analyze document.pdf

# 4. Start web dashboard
python doc-dashboard.py --port 5000

# 5. Start API server
python doc-api-server.py --host 0.0.0.0 --port 8000
```

---

## 📚 Tool Categories

### Document Processing (Tools 1-9)
**Purpose:** Process, analyze, and transform documents
**Use Cases:**
- Compare documents for similarity
- Remove PII for compliance
- Assess document quality
- Merge/split documents
- Batch processing

### System Tools (Tools 10-11)
**Purpose:** Run web interfaces and APIs
**Use Cases:**
- Web-based document management
- REST API access
- Real-time monitoring

### Administration (Tools 12-13)
**Purpose:** System administration and configuration
**Use Cases:**
- User management
- System configuration
- Database management
- Enterprise features

---

# 📖 Detailed Tool Documentation

## 1. doc-comparator

**Compare two documents with multiple algorithms**

### Purpose
Professional document comparison tool that detects similarities and differences using multiple comparison methods.

### Key Features
- ✅ Multiple comparison algorithms (cosine, jaccard, levenshtein, entity-based)
- ✅ Visual diff reports (HTML, JSON, Text)
- ✅ Entity-level comparison
- ✅ Configurable similarity threshold
- ✅ Color-coded differences

### Commands

#### `compare` - Compare two documents

**Basic Usage:**
```bash
python doc-comparator.py compare <file1> <file2>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--method` | Comparison method | all |
| `--threshold` | Similarity threshold (0-1) | 0.7 |
| `--report` | Report format (html/json/text) | text |
| `--output` | Output file path | stdout |
| `--entities-only` | Compare entities only | False |
| `--verbose` | Verbose output | False |

**Comparison Methods:**
- `cosine` - Cosine similarity (best for overall similarity)
- `jaccard` - Jaccard index (good for word overlap)
- `levenshtein` - Edit distance (character-level changes)
- `entity` - Entity-based comparison (semantic similarity)
- `all` - All methods combined

**Examples:**

```bash
# Basic comparison
python doc-comparator.py compare doc1.pdf doc2.pdf

# With HTML report
python doc-comparator.py compare doc1.pdf doc2.pdf \
    --report html \
    --output diff_report.html

# High similarity threshold
python doc-comparator.py compare doc1.pdf doc2.pdf \
    --threshold 0.9

# Entity comparison only
python doc-comparator.py compare doc1.pdf doc2.pdf \
    --entities-only

# Specific comparison method
python doc-comparator.py compare doc1.pdf doc2.pdf \
    --method cosine \
    --verbose

# JSON output for automation
python doc-comparator.py compare doc1.pdf doc2.pdf \
    --report json \
    --output comparison.json
```

**Output:**
```
Document Comparison Report
==========================

Files:
  - File 1: doc1.pdf (1234 bytes)
  - File 2: doc2.pdf (1456 bytes)

Similarity Scores:
  - Cosine Similarity:      0.89
  - Jaccard Index:          0.75
  - Levenshtein Distance:   0.82
  - Entity Similarity:      0.91

Overall Similarity: 0.84 (High)

Differences Found: 12
  - Added:    5 sections
  - Removed:  3 sections
  - Changed:  4 sections
```

**Use Cases:**
- ✅ Version comparison
- ✅ Plagiarism detection
- ✅ Change tracking
- ✅ Document verification
- ✅ Quality assurance

---

## 2. doc-anonymizer

**GDPR/HIPAA-compliant PII anonymization**

### Purpose
Remove or mask personally identifiable information (PII) from documents for compliance with GDPR, HIPAA, and other privacy regulations.

### Key Features
- ✅ Multiple anonymization strategies (redaction, masking, replacement)
- ✅ GDPR and HIPAA compliance modes
- ✅ Reversible anonymization
- ✅ Audit logging
- ✅ Batch processing
- ✅ Entity detection (names, emails, phones, SSNs, etc.)

### Commands

#### `scan` - Scan for PII without anonymizing

**Usage:**
```bash
python doc-anonymizer.py scan <document>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--report` | Report output file | stdout |
| `--format` | Report format (json/text) | text |
| `--entity-types` | Specific entity types to scan | all |

**Examples:**
```bash
# Basic PII scan
python doc-anonymizer.py scan document.pdf

# Save scan report
python doc-anonymizer.py scan document.pdf \
    --report pii_report.json \
    --format json

# Scan for specific entities
python doc-anonymizer.py scan document.pdf \
    --entity-types "PERSON,EMAIL,PHONE"
```

#### `anonymize` - Anonymize document

**Usage:**
```bash
python doc-anonymizer.py anonymize <document> --output <output_file>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output` | Output file path | Required |
| `--strategy` | Anonymization strategy | redaction |
| `--compliance` | Compliance mode (gdpr/hipaa) | gdpr |
| `--reversible` | Enable reversible anonymization | False |
| `--mapping-file` | Encryption mapping file | auto |
| `--audit-log` | Enable audit logging | False |
| `--entity-types` | Entities to anonymize | all |

**Anonymization Strategies:**
- `redaction` - Remove PII (black boxes)
- `masking` - Replace with asterisks (****)
- `replacement` - Replace with fake data
- `encryption` - Encrypt PII (reversible)

**Examples:**
```bash
# Basic redaction
python doc-anonymizer.py anonymize document.pdf \
    --output anonymized.pdf

# Masking strategy
python doc-anonymizer.py anonymize document.pdf \
    --strategy masking \
    --output masked.pdf

# HIPAA compliant with audit log
python doc-anonymizer.py anonymize medical.pdf \
    --compliance hipaa \
    --audit-log \
    --output anonymized_medical.pdf

# Reversible anonymization
python doc-anonymizer.py anonymize document.pdf \
    --reversible \
    --mapping-file secure_mapping.enc \
    --output anonymized.pdf

# Anonymize specific entities only
python doc-anonymizer.py anonymize document.pdf \
    --entity-types "PERSON,EMAIL" \
    --output anonymized.pdf
```

#### `deanonymize` - Restore original content

**Usage:**
```bash
python doc-anonymizer.py deanonymize <anonymized_doc> \
    --mapping-file <mapping> \
    --output <output_file>
```

**Examples:**
```bash
# Restore original document
python doc-anonymizer.py deanonymize anonymized.pdf \
    --mapping-file secure_mapping.enc \
    --output original.pdf
```

#### `batch` - Batch anonymize directory

**Usage:**
```bash
python doc-anonymizer.py batch <input_dir> --output-dir <output_dir>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir` | Output directory | Required |
| `--strategy` | Anonymization strategy | redaction |
| `--recursive` | Process subdirectories | False |
| `--file-types` | File extensions to process | pdf,docx,txt |

**Examples:**
```bash
# Batch anonymize directory
python doc-anonymizer.py batch /documents/ \
    --output-dir /anonymized/ \
    --recursive

# Batch with specific file types
python doc-anonymizer.py batch /documents/ \
    --output-dir /anonymized/ \
    --file-types "pdf,docx" \
    --strategy masking
```

**Use Cases:**
- ✅ GDPR compliance
- ✅ HIPAA compliance
- ✅ Data sharing
- ✅ Document publishing
- ✅ Research data preparation

---

## 3. doc-quality

**Comprehensive document quality assessment**

### Purpose
Analyze and assess document quality across multiple dimensions: completeness, consistency, accuracy, readability, and compliance.

### Key Features
- ✅ Multi-dimensional quality analysis
- ✅ Quality scoring (0-100)
- ✅ Detailed quality reports
- ✅ Batch quality checks
- ✅ Configurable thresholds
- ✅ HTML/JSON reports

### Commands

#### `analyze` - Full quality analysis

**Usage:**
```bash
python doc-quality.py analyze <document>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--full` | Full analysis (all dimensions) | True |
| `--dimension` | Specific dimension | all |
| `--threshold` | Minimum quality score | 70 |
| `--fail-on-low-quality` | Exit with error if below threshold | False |
| `--report` | Report format (text/html/json) | text |
| `--output` | Output file path | stdout |

**Quality Dimensions:**
- `completeness` - Document completeness
- `consistency` - Internal consistency
- `accuracy` - Content accuracy
- `readability` - Text readability
- `compliance` - Standards compliance
- `formatting` - Formatting quality

**Examples:**
```bash
# Full quality analysis
python doc-quality.py analyze document.pdf --full

# Check specific dimension
python doc-quality.py analyze document.pdf \
    --dimension completeness

# With quality threshold
python doc-quality.py analyze document.pdf \
    --threshold 80 \
    --fail-on-low-quality

# Generate HTML report
python doc-quality.py analyze document.pdf \
    --report html \
    --output quality_report.html

# JSON output for CI/CD
python doc-quality.py analyze document.pdf \
    --report json \
    --output quality.json
```

#### `batch` - Batch quality check

**Usage:**
```bash
python doc-quality.py batch <directory>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output` | Report output file | quality_report.json |
| `--threshold` | Minimum quality score | 70 |
| `--recursive` | Process subdirectories | False |
| `--summary-only` | Show summary only | False |

**Examples:**
```bash
# Batch quality check
python doc-quality.py batch /documents/ \
    --output quality_report.json

# Recursive with threshold
python doc-quality.py batch /documents/ \
    --recursive \
    --threshold 80 \
    --summary-only
```

**Output:**
```
Document Quality Report
=======================

File: document.pdf
Size: 1.2 MB
Pages: 15

Quality Scores:
  - Completeness:   85/100  ✓
  - Consistency:    78/100  ✓
  - Accuracy:       92/100  ✓
  - Readability:    88/100  ✓
  - Compliance:     95/100  ✓
  - Formatting:     81/100  ✓

Overall Quality: 86/100 (Good)

Issues Found: 3
  ⚠ Missing metadata fields
  ⚠ Inconsistent heading styles
  ⚠ One broken internal link

Recommendations:
  1. Add document metadata (author, date, version)
  2. Standardize heading hierarchy
  3. Fix broken reference on page 12
```

**Use Cases:**
- ✅ Quality assurance
- ✅ Document validation
- ✅ Compliance checking
- ✅ Pre-publication review
- ✅ Automated quality gates

---

## 4. doc-master

**Interactive document creation wizard**

### Purpose
Guide users through document creation with templates, validation, and best practices.

### Key Features
- ✅ Interactive wizard interface
- ✅ Template-based creation
- ✅ Step-by-step guidance
- ✅ Real-time validation
- ✅ Multiple output formats
- ✅ Custom templates

### Commands

#### `create` - Create new document

**Usage:**
```bash
python doc-master.py create
```

**Interactive Mode:**
The wizard will guide you through:
1. Template selection
2. Content entry
3. Formatting options
4. Metadata configuration
5. Output format selection

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--template` | Template file or name | default |
| `--output` | Output file path | auto |
| `--format` | Output format | pdf |
| `--non-interactive` | Use config file | False |
| `--config` | Configuration file | None |

**Examples:**
```bash
# Interactive wizard
python doc-master.py create

# Use specific template
python doc-master.py create \
    --template "business_letter" \
    --output letter.pdf

# Non-interactive with config
python doc-master.py create \
    --non-interactive \
    --config document_config.yaml \
    --output report.pdf
```

**Use Cases:**
- ✅ Standardized document creation
- ✅ Template-based workflows
- ✅ Guided content entry
- ✅ Consistent formatting
- ✅ Quality assurance

---

## 5. doc-processor

**Advanced document processing**

### Purpose
Process documents with various operations: extraction, conversion, OCR, and transformation.

### Key Features
- ✅ Text extraction
- ✅ Format conversion
- ✅ OCR for scanned documents
- ✅ Metadata extraction
- ✅ Image extraction
- ✅ Batch processing

### Commands

#### `process` - Process document

**Usage:**
```bash
python doc-processor.py process <document> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--operation` | Processing operation | extract |
| `--output` | Output file/directory | auto |
| `--format` | Output format | text |
| `--ocr` | Enable OCR | False |
| `--language` | OCR language | eng |

**Operations:**
- `extract` - Extract text
- `convert` - Convert format
- `ocr` - Optical character recognition
- `metadata` - Extract metadata
- `images` - Extract images

**Examples:**
```bash
# Extract text
python doc-processor.py process document.pdf \
    --operation extract \
    --output text.txt

# Convert to DOCX
python doc-processor.py process document.pdf \
    --operation convert \
    --format docx \
    --output document.docx

# OCR scanned document
python doc-processor.py process scanned.pdf \
    --operation ocr \
    --language eng \
    --output ocr_text.txt

# Extract metadata
python doc-processor.py process document.pdf \
    --operation metadata \
    --output metadata.json

# Extract images
python doc-processor.py process document.pdf \
    --operation images \
    --output ./images/
```

**Use Cases:**
- ✅ Text extraction
- ✅ Format conversion
- ✅ Scanned document digitization
- ✅ Metadata management
- ✅ Content analysis

---

## 6. doc-merger

**Merge multiple documents into one**

### Purpose
Combine multiple documents into a single unified document with proper formatting and structure.

### Key Features
- ✅ Merge PDFs, DOCX, TXT files
- ✅ Preserve formatting
- ✅ Table of contents generation
- ✅ Page numbering
- ✅ Bookmarks and links

### Commands

#### `merge` - Merge documents

**Usage:**
```bash
python doc-merger.py merge <file1> <file2> [file3...] --output <output>
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output` | Output file path | merged.pdf |
| `--toc` | Generate table of contents | False |
| `--bookmarks` | Add bookmarks | False |
| `--page-numbers` | Add page numbers | False |
| `--format` | Output format | pdf |

**Examples:**
```bash
# Basic merge
python doc-merger.py merge doc1.pdf doc2.pdf doc3.pdf \
    --output combined.pdf

# With table of contents
python doc-merger.py merge *.pdf \
    --output report.pdf \
    --toc \
    --page-numbers

# Merge with bookmarks
python doc-merger.py merge chapter*.pdf \
    --output book.pdf \
    --bookmarks \
    --toc
```

**Use Cases:**
- ✅ Report compilation
- ✅ Book assembly
- ✅ Document consolidation
- ✅ Archive creation

---

## 7. doc-splitter

**Split documents into parts**

### Purpose
Split large documents into smaller parts based on pages, sections, or bookmarks.

### Key Features
- ✅ Split by page ranges
- ✅ Split by bookmarks
- ✅ Split by sections
- ✅ Extract specific pages
- ✅ Batch splitting

### Commands

#### `split` - Split document

**Usage:**
```bash
python doc-splitter.py split <document> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--method` | Split method | pages |
| `--output-dir` | Output directory | ./split/ |
| `--pages-per-file` | Pages per output file | 10 |
| `--prefix` | Output file prefix | part_ |

**Split Methods:**
- `pages` - Split by page count
- `bookmarks` - Split at bookmarks
- `sections` - Split by sections
- `size` - Split by file size

**Examples:**
```bash
# Split by pages
python doc-splitter.py split large_document.pdf \
    --method pages \
    --pages-per-file 10 \
    --output-dir ./parts/

# Split by bookmarks
python doc-splitter.py split book.pdf \
    --method bookmarks \
    --output-dir ./chapters/

# Extract specific pages
python doc-splitter.py split document.pdf \
    --pages "1-5,10-15,20" \
    --output-dir ./extracts/
```

**Use Cases:**
- ✅ Large file management
- ✅ Chapter extraction
- ✅ Page extraction
- ✅ Document distribution

---

## 8. doc-batch-processor

**Batch process multiple documents**

### Purpose
Perform operations on multiple documents simultaneously with parallel processing.

### Key Features
- ✅ Parallel processing
- ✅ Progress tracking
- ✅ Error handling
- ✅ Resume capability
- ✅ Detailed logging
- ✅ Multiple operations

### Commands

#### `batch` - Batch process

**Usage:**
```bash
python doc-batch-processor.py batch <operation> <directory> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir` | Output directory | ./processed/ |
| `--recursive` | Process subdirectories | False |
| `--parallel` | Number of parallel jobs | 4 |
| `--resume` | Resume interrupted batch | False |
| `--log-file` | Log file path | batch.log |

**Operations:**
- `convert` - Format conversion
- `extract` - Text extraction
- `anonymize` - Anonymization
- `quality` - Quality check
- `compress` - Compression

**Examples:**
```bash
# Batch convert to PDF
python doc-batch-processor.py batch convert /documents/ \
    --output-dir /pdfs/ \
    --format pdf \
    --parallel 8

# Batch anonymize
python doc-batch-processor.py batch anonymize /documents/ \
    --output-dir /anonymized/ \
    --recursive

# Batch quality check
python doc-batch-processor.py batch quality /documents/ \
    --log-file quality_report.json \
    --recursive

# Resume interrupted batch
python doc-batch-processor.py batch convert /documents/ \
    --resume \
    --log-file batch.log
```

**Use Cases:**
- ✅ Bulk processing
- ✅ Data migration
- ✅ Archive processing
- ✅ Automated workflows

---

## 9. doc-search

**Advanced document search**

### Purpose
Search documents using full-text search, semantic search, and advanced filters.

### Key Features
- ✅ Full-text search
- ✅ Semantic search
- ✅ Faceted search
- ✅ Advanced filters
- ✅ Ranking and relevance
- ✅ Export results

### Commands

#### `search` - Search documents

**Usage:**
```bash
python doc-search.py search <query> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--method` | Search method | fulltext |
| `--limit` | Max results | 10 |
| `--format` | Output format | text |
| `--filters` | Search filters | None |
| `--highlight` | Highlight matches | True |

**Search Methods:**
- `fulltext` - Full-text search
- `semantic` - Semantic/AI search
- `fuzzy` - Fuzzy matching
- `phrase` - Exact phrase

**Examples:**
```bash
# Basic search
python doc-search.py search "document management"

# Semantic search
python doc-search.py search "contract agreements" \
    --method semantic \
    --limit 20

# With filters
python doc-search.py search "financial report" \
    --filters "type:pdf,date:2024-*" \
    --limit 50

# Export results
python doc-search.py search "meeting notes" \
    --format json \
    --output search_results.json
```

**Use Cases:**
- ✅ Document discovery
- ✅ Content research
- ✅ Knowledge retrieval
- ✅ Compliance search

---

## 10. doc-dashboard

**Web-based dashboard**

### Purpose
Launch web interface for document management with visual analytics and interactive tools.

### Key Features
- ✅ Web UI interface
- ✅ Real-time analytics
- ✅ Document preview
- ✅ User management
- ✅ API integration
- ✅ Responsive design

### Commands

#### `start` - Start dashboard server

**Usage:**
```bash
python doc-dashboard.py [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Server host | 127.0.0.1 |
| `--port` | Server port | 5000 |
| `--debug` | Debug mode | False |
| `--reload` | Auto-reload | False |
| `--config` | Config file | None |

**Examples:**
```bash
# Start on default port
python doc-dashboard.py

# Custom host and port
python doc-dashboard.py --host 0.0.0.0 --port 8080

# Development mode
python doc-dashboard.py --debug --reload

# Production mode
python doc-dashboard.py \
    --host 0.0.0.0 \
    --port 80 \
    --config production.yaml
```

**Access:**
Open browser: http://localhost:5000

**Features:**
- 📊 Dashboard home
- 📁 Document browser
- 🔍 Search interface
- 👥 User management
- ⚙️ Settings
- 📈 Analytics

**Use Cases:**
- ✅ Web-based document management
- ✅ Team collaboration
- ✅ Visual analytics
- ✅ Remote access

---

## 11. doc-api-server

**REST API server**

### Purpose
Launch REST API server for programmatic access to DMS functionality.

### Key Features
- ✅ RESTful API
- ✅ OpenAPI/Swagger documentation
- ✅ Authentication (API keys, JWT)
- ✅ Rate limiting
- ✅ Versioned endpoints
- ✅ Real-time monitoring

### Commands

#### `start` - Start API server

**Usage:**
```bash
python doc-api-server.py [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Server host | 127.0.0.1 |
| `--port` | Server port | 8000 |
| `--workers` | Number of workers | 4 |
| `--debug` | Debug mode | False |
| `--reload` | Auto-reload | False |

**Examples:**
```bash
# Start API server
python doc-api-server.py

# Custom configuration
python doc-api-server.py \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 8

# Development mode
python doc-api-server.py --debug --reload

# Production mode
python doc-api-server.py \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 16
```

**API Documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI spec: http://localhost:8000/api/openapi.yaml

**Use Cases:**
- ✅ API integrations
- ✅ Automation
- ✅ Third-party apps
- ✅ Microservices

---

## 12. dms-admin

**DMS administration tool**

### Purpose
System administration, configuration, and management of DMS installation.

### Key Features
- ✅ User management
- ✅ Database management
- ✅ Configuration management
- ✅ System monitoring
- ✅ Backup/restore
- ✅ Maintenance tasks

### Commands

#### `users` - User management

**Usage:**
```bash
python dms-admin.py users <action> [options]
```

**Actions:**
- `list` - List all users
- `create` - Create new user
- `delete` - Delete user
- `update` - Update user
- `reset-password` - Reset password

**Examples:**
```bash
# List users
python dms-admin.py users list

# Create user
python dms-admin.py users create \
    --username john \
    --email john@example.com \
    --role admin

# Reset password
python dms-admin.py users reset-password john
```

#### `database` - Database management

**Usage:**
```bash
python dms-admin.py database <action> [options]
```

**Actions:**
- `migrate` - Run migrations
- `backup` - Backup database
- `restore` - Restore database
- `vacuum` - Optimize database
- `stats` - Database statistics

**Examples:**
```bash
# Run migrations
python dms-admin.py database migrate

# Backup
python dms-admin.py database backup \
    --output backup_20260116.sql

# Restore
python dms-admin.py database restore backup_20260116.sql
```

#### `system` - System management

**Usage:**
```bash
python dms-admin.py system <action> [options]
```

**Actions:**
- `status` - System status
- `config` - View/edit configuration
- `logs` - View system logs
- `cleanup` - Clean temporary files
- `monitor` - Real-time monitoring

**Examples:**
```bash
# System status
python dms-admin.py system status

# View configuration
python dms-admin.py system config --show

# Update configuration
python dms-admin.py system config \
    --set "max_file_size=100MB"

# View logs
python dms-admin.py system logs --tail 100

# Cleanup
python dms-admin.py system cleanup --older-than 30d
```

**Use Cases:**
- ✅ System administration
- ✅ User management
- ✅ Database maintenance
- ✅ Configuration management

---

## 13. enterprise-admin

**Enterprise administration**

### Purpose
Enterprise-level administration including multi-tenancy, advanced security, and enterprise features.

### Key Features
- ✅ Multi-tenant management
- ✅ Enterprise security
- ✅ Advanced analytics
- ✅ Compliance reporting
- ✅ Audit management
- ✅ License management

### Commands

#### `tenants` - Tenant management

**Usage:**
```bash
python enterprise-admin.py tenants <action> [options]
```

**Actions:**
- `list` - List all tenants
- `create` - Create new tenant
- `delete` - Delete tenant
- `configure` - Configure tenant
- `stats` - Tenant statistics

**Examples:**
```bash
# List tenants
python enterprise-admin.py tenants list

# Create tenant
python enterprise-admin.py tenants create \
    --name "Acme Corp" \
    --plan enterprise \
    --max-users 100

# Configure tenant
python enterprise-admin.py tenants configure acme-corp \
    --setting "storage_quota=1TB"
```

#### `security` - Security management

**Usage:**
```bash
python enterprise-admin.py security <action> [options]
```

**Actions:**
- `audit` - View audit logs
- `policies` - Manage security policies
- `compliance` - Compliance reports
- `scan` - Security scan

**Examples:**
```bash
# View audit logs
python enterprise-admin.py security audit \
    --days 7 \
    --export audit_report.json

# Compliance report
python enterprise-admin.py security compliance \
    --standard GDPR \
    --output compliance_report.pdf

# Security scan
python enterprise-admin.py security scan
```

#### `analytics` - Enterprise analytics

**Usage:**
```bash
python enterprise-admin.py analytics <action> [options]
```

**Actions:**
- `usage` - Usage statistics
- `performance` - Performance metrics
- `reports` - Generate reports
- `export` - Export analytics

**Examples:**
```bash
# Usage statistics
python enterprise-admin.py analytics usage --month 2024-01

# Performance report
python enterprise-admin.py analytics performance \
    --output performance.html

# Export analytics
python enterprise-admin.py analytics export \
    --format csv \
    --output analytics.csv
```

**Use Cases:**
- ✅ Multi-tenant management
- ✅ Enterprise security
- ✅ Compliance management
- ✅ Advanced analytics

---

## 🔧 Common Options

All tools support these common options:

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `--version` | Show version |
| `--verbose, -v` | Verbose output |
| `--quiet, -q` | Quiet mode |
| `--log-level` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `--log-file` | Log to file |
| `--config` | Configuration file |

---

## 📊 Best Practices

### 1. Use Configuration Files

Instead of long command lines:

```yaml
# config.yaml
input_dir: /documents
output_dir: /processed
format: pdf
quality_threshold: 80
```

```bash
python doc-batch-processor.py --config config.yaml
```

### 2. Enable Logging

Always log important operations:

```bash
python doc-processor.py process document.pdf \
    --log-file processing.log \
    --log-level INFO
```

### 3. Use Batch Operations

For multiple files:

```bash
# Instead of:
python doc-anonymizer.py anonymize doc1.pdf --output out1.pdf
python doc-anonymizer.py anonymize doc2.pdf --output out2.pdf
python doc-anonymizer.py anonymize doc3.pdf --output out3.pdf

# Use batch:
python doc-anonymizer.py batch /documents/ --output-dir /anonymized/
```

### 4. Check Quality First

Before processing:

```bash
# Check quality
python doc-quality.py analyze document.pdf

# Then process if quality is good
python doc-processor.py process document.pdf
```

### 5. Use CI/CD Integration

Integrate in pipelines:

```bash
# In .gitlab-ci.yml or .github/workflows
python doc-quality.py analyze document.pdf --threshold 80 --fail-on-low-quality
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Install missing dependencies
pip install -r requirements.txt
```

**2. Permission Denied**

```bash
# Make executable
chmod +x doc-*.py
```

**3. Module Not Found**

```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**4. Database Errors**

```bash
# Reset database
python dms-admin.py database migrate --reset
```

**5. Port Already in Use**

```bash
# Use different port
python doc-dashboard.py --port 5001
```

---

## 📚 Additional Resources

### Documentation
- API Documentation: `docs/API_DOCUMENTATION_GUIDE.md`
- Deployment Guide: `docs/DEPLOYMENT_GUIDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING_GUIDE.md`

### Examples
- Code examples: `examples/`
- Configuration templates: `config/templates/`
- Test files: `tests/fixtures/`

### Support
- GitHub Issues: https://github.com/svend4/daten20/issues
- Documentation: https://docs.daten20.example.com
- Email: support@daten20.example.com

---

## 📝 Changelog

### Version 4.1.0 (2026-01-16)
- ✅ Created comprehensive CLI tools master guide
- ✅ Documented all 13 CLI tools
- ✅ Added usage examples for each tool
- ✅ Added best practices and troubleshooting

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Maintained by:** DMS Development Team
**Status:** Production Ready

For questions or feedback, please visit: https://github.com/svend4/daten20
