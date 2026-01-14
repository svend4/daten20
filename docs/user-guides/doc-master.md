# 🎛️ Doc-Master User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Unified control panel for all document management tools

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

**doc-master.py** is the master control panel that orchestrates all document management applications and provides unified CLI access.

### Key Features

- ✅ **Unified Interface** - Single CLI for all tools
- ✅ **Service Management** - Start/stop/status of services
- ✅ **Pre-built Pipelines** - Ready-to-use workflows
- ✅ **Health Checking** - System diagnostics
- ✅ **Quick Processing** - One-command document processing

### Managed Applications

| Application | Type | Description |
|-------------|------|-------------|
| doc-processor | Tool | Single document processing |
| doc-comparator | Tool | Document comparison |
| doc-anonymizer | Tool | PII anonymization |
| doc-quality | Tool | Quality assessment |
| doc-dashboard | Daemon | Web UI |
| doc-api-server | Daemon | REST API server |
| doc-batch-processor | Service | Batch processing |
| doc-search | Service | Search engine |

---

## ⚡ Quick Start

### 1. Check System Status

```bash
# View all components and their status
python doc-master.py status

# Output:
# 📊 Document Management System Status
# ======================================================================
# Platform: Linux
# Python: 3.10.12
#
# Components:
#   ✅ Document Processor        [tool     ] - Single document processing...
#   ✅ Batch Processor           [service  ] - Multi-threaded batch...
#   ✅ API Server                [daemon   ] - FastAPI REST API server
#   ✅ Web Dashboard             [daemon   ] - Interactive web dashboard...
#   ✅ Search Engine             [service  ] - Full-text and semantic...
#   ✅ Document Comparator       [tool     ] - Advanced document comparison
#   ✅ Document Anonymizer       [tool     ] - GDPR-compliant PII...
#   ✅ Quality Analyzer          [tool     ] - Comprehensive quality...
#
# Summary:
#   Total: 8
#   Available: 8
```

### 2. Health Check

```bash
# Comprehensive health check
python doc-master.py health

# Output:
# 🏥 System Health Check
# ======================================================================
# Overall Status: HEALTHY
#
# Checks:
#   ✅ python           : ok
#   ✅ scripts          : ok
#   ✅ src_directory    : ok
#   ✅ data_directory   : ok
```

### 3. Quick Process Document

```bash
# Process with all steps
python doc-master.py quick-process document.pdf --steps all

# Output:
# ⚡ Quick Process Complete
# ======================================================================
# Pipeline: quick-process
# Total steps: 3
# Completed: 3
# Failed: 0
# Time: 5.23s
#
# Results:
#   ✅ process      : output/document_processed.json
#   ✅ anonymize    : output/document_anonymized.txt
#   ✅ quality      : output/document_quality.json
```

---

## 📚 Commands

### Command: `status`

Show status of all components.

**Usage:**
```bash
python doc-master.py status
```

**No Options**

**Example:**
```bash
python doc-master.py status

# Shows:
# - Platform information
# - Python version
# - Component availability
# - Component types
# - Summary statistics
```

---

### Command: `health`

Perform comprehensive health check.

**Usage:**
```bash
python doc-master.py health
```

**No Options**

**Health Checks:**
- Python environment
- Required scripts
- Source directory
- Data directory

**Example:**
```bash
python doc-master.py health

# Output:
# Overall Status: HEALTHY (or DEGRADED, UNHEALTHY)
#
# Individual checks:
#   ✅ python: ok
#   ✅ scripts: ok (or warning if scripts missing)
#   ✅ src_directory: ok (or error if missing)
```

---

### Command: `quick-process`

Quick process document with multiple steps.

**Usage:**
```bash
python doc-master.py quick-process <file> --steps <steps...> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--steps STEPS` | Processing steps | process |
| `--output-dir DIR` | Output directory | output |

**Available Steps:**
- `process` - Extract text and metadata
- `anonymize` - Remove PII
- `quality` - Quality assessment
- `all` - All steps

**Examples:**

```bash
# Process only
python doc-master.py quick-process document.pdf --steps process

# Anonymize only
python doc-master.py quick-process document.pdf --steps anonymize

# Quality check only
python doc-master.py quick-process document.pdf --steps quality

# All steps
python doc-master.py quick-process document.pdf --steps all

# Multiple specific steps
python doc-master.py quick-process document.pdf \
  --steps process anonymize

# Custom output directory
python doc-master.py quick-process document.pdf \
  --steps all \
  --output-dir results/
```

**Output Example:**
```
⚡ Quick Process Complete
======================================================================
Pipeline: quick-process
Total steps: 3
Completed: 3
Failed: 0
Time: 5.23s

Results:
  ✅ process      : output/document_processed.json
  ✅ anonymize    : output/document_anonymized.txt
  ✅ quality      : output/document_quality.json
```

---

### Command: `pipeline`

Run pre-defined processing pipeline.

**Usage:**
```bash
python doc-master.py pipeline <name> --input <path>
```

**Options:**

| Option | Description |
|--------|-------------|
| `--input PATH` | Input file or directory (required) |

**Available Pipelines:**

1. **gdpr-compliance** - GDPR workflow
   - Scan for PII
   - Anonymize with masking
   - Quality check

2. **quality-assurance** - QA workflow
   - Quality analysis (threshold 80)
   - Full document processing

3. **full-analysis** - Complete analysis
   - Document processing
   - Quality assessment

**Examples:**

```bash
# GDPR compliance pipeline
python doc-master.py pipeline gdpr-compliance \
  --input sensitive_doc.pdf

# Quality assurance pipeline
python doc-master.py pipeline quality-assurance \
  --input report.pdf

# Full analysis pipeline
python doc-master.py pipeline full-analysis \
  --input document.pdf
```

**Output Example:**
```
🔧 Pipeline 'gdpr-compliance' Complete
======================================================================
Completed: 3/3
Time: 8.45s

Pipeline steps executed:
  ✅ anonymizer.scan
  ✅ anonymizer.anonymize
  ✅ quality.analyze
```

---

### Command: `pipelines`

List all available pipelines.

**Usage:**
```bash
python doc-master.py pipelines
```

**Example:**
```bash
python doc-master.py pipelines

# Output:
# 📋 Available Pipelines
# ======================================================================
#   • gdpr-compliance    : GDPR compliance workflow (scan → anonymize → quality check)
#   • quality-assurance  : Quality assurance workflow (quality check → process)
#   • full-analysis      : Full document analysis (process → quality check)
```

---

## 💼 Use Cases

### Use Case 1: System Diagnostics

**Scenario:** Check if document management system is properly set up.

```bash
# Step 1: Check overall status
python doc-master.py status

# Step 2: Run health check
python doc-master.py health

# Step 3: Test processing
python doc-master.py quick-process test_doc.pdf --steps process

# If all pass: System ready!
# If issues found: Review health check output
```

**Why it's useful:** Quick system validation.

---

### Use Case 2: One-Command Document Processing

**Scenario:** Process document through complete workflow.

```bash
# Single command for full workflow
python doc-master.py quick-process contract.pdf \
  --steps all \
  --output-dir processed/

# Runs:
# 1. Document processing (entities, classification)
# 2. Anonymization (PII removal)
# 3. Quality check

# Results in processed/ directory:
# - contract_processed.json
# - contract_anonymized.txt
# - contract_quality.json
```

**Why it's useful:** Simplified multi-step processing.

---

### Use Case 3: GDPR Compliance Workflow

**Scenario:** Prepare documents for GDPR compliance.

```bash
# Run GDPR compliance pipeline
python doc-master.py pipeline gdpr-compliance \
  --input personal_data.pdf

# Pipeline automatically:
# 1. Scans for PII
# 2. Anonymizes with appropriate strategy
# 3. Validates quality
# 4. Creates audit trail

# Output: GDPR-compliant anonymized document
```

**Why it's useful:** Automated compliance processing.

---

## ❗ Troubleshooting

### Issue: "Component not found"

**Symptom:** Status shows ❌ for some components

**Solutions:**

```bash
# Check which components missing
python doc-master.py status

# Verify files exist
ls -l doc-*.py

# If missing, check git repository
git status
git checkout doc-processor.py  # etc.
```

---

### Issue: "Health check fails"

**Error:** Overall Status: UNHEALTHY

**Solutions:**

```bash
# Check what failed
python doc-master.py health

# Common issues:

# 1. Missing src/ directory
mkdir -p src/core src/ml

# 2. Missing data/ directory
mkdir -p data

# 3. Python version too old
python --version  # Should be 3.9+

# 4. Missing dependencies
pip install -r requirements.txt
```

---

### Issue: "Quick-process fails"

**Error:** Command failed during execution

**Solutions:**

```bash
# Run steps individually for debugging
python doc-master.py quick-process doc.pdf --steps process
python doc-master.py quick-process doc.pdf --steps anonymize
python doc-master.py quick-process doc.pdf --steps quality

# Check error messages
# Fix underlying issues
# Then try again
```

---

## 💡 Tips & Best Practices

### 1. Start with Health Check

```bash
# Always check system health before important work
python doc-master.py health

# If healthy, proceed
# If issues, fix before processing
```

### 2. Use Pipelines for Common Workflows

```bash
# Don't chain multiple commands manually
# Instead use pre-built pipelines

# ❌ Don't do this:
python doc-anonymizer.py scan doc.pdf
python doc-anonymizer.py anonymize doc.pdf --output anon.pdf
python doc-quality.py analyze anon.pdf

# ✅ Do this:
python doc-master.py pipeline gdpr-compliance --input doc.pdf
```

### 3. Quick-Process for Ad-Hoc Tasks

```bash
# For one-off document processing
python doc-master.py quick-process doc.pdf --steps all

# Fast and simple
# All results in one directory
```

### 4. Monitor System Status Regularly

```bash
# Daily health check
python doc-master.py health > health_$(date +%Y%m%d).log

# Weekly status report
python doc-master.py status > status_weekly.log

# Track system health over time
```

### 5. Create Custom Wrapper Scripts

```bash
#!/bin/bash
# process_document.sh

DOC="$1"

# 1. Check health
python doc-master.py health || exit 1

# 2. Process
python doc-master.py quick-process "$DOC" \
  --steps all \
  --output-dir "processed/$(date +%Y%m%d)/"

# 3. Report
echo "Processed: $DOC"
```

---

## 🔧 Pipeline Customization

### Available Pipelines

#### 1. GDPR Compliance

```yaml
Steps:
  1. anonymizer.scan - Detect PII
  2. anonymizer.anonymize - Remove PII (masking)
  3. quality.analyze - Validate quality

Use for:
  - GDPR compliance
  - Data protection
  - Privacy requirements
```

#### 2. Quality Assurance

```yaml
Steps:
  1. quality.analyze - Check quality (threshold 80)
  2. processor.process - Full processing

Use for:
  - Document validation
  - Quality gates
  - Pre-publication checks
```

#### 3. Full Analysis

```yaml
Steps:
  1. processor.process - Extract everything
  2. quality.analyze - Assess quality

Use for:
  - Complete document analysis
  - Research purposes
  - Comprehensive insights
```

---

## 🔄 Related Tools

All document management tools are accessible through doc-master:

- **doc-processor.py** - Single document processing
- **doc-batch-processor.py** - Batch processing
- **doc-comparator.py** - Document comparison
- **doc-anonymizer.py** - PII anonymization
- **doc-quality.py** - Quality assessment
- **doc-search.py** - Search functionality
- **doc-dashboard.py** - Web interface
- **doc-api-server.py** - API server

---

## 📊 System Requirements

```bash
# Minimum:
# - Python 3.9+
# - 4GB RAM
# - 1GB disk space

# Recommended:
# - Python 3.10+
# - 8GB RAM
# - 5GB disk space (for data)
# - SSD storage

# Check your system:
python --version
free -h  # Check RAM
df -h    # Check disk space
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
