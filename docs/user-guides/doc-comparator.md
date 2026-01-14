# 🔄 Doc-Comparator User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Professional document comparison with advanced similarity metrics

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

**doc-comparator.py** compares documents using multiple similarity algorithms, entity analysis, and generates detailed comparison reports with visualizations.

### Key Features

- ✅ **Multiple Similarity Metrics** - Cosine, Jaccard, Levenshtein distance
- ✅ **Entity Comparison** - Compare named entities across documents
- ✅ **Visual Diff Reports** - HTML reports with side-by-side comparison
- ✅ **Structural Analysis** - Track added, removed, and modified lines
- ✅ **Change Detection** - Identify and highlight document changes

### Comparison Metrics

| Metric | Description | Best For |
|--------|-------------|----------|
| **Cosine Similarity** | Word-frequency based similarity (0-1) | Overall content similarity |
| **Jaccard Similarity** | Set intersection/union ratio (0-1) | Vocabulary overlap |
| **Levenshtein Distance** | Edit distance (character changes) | Precise text differences |

---

## ⚡ Quick Start

### 1. Basic Comparison

```bash
# Compare two documents
python doc-comparator.py compare document_v1.pdf document_v2.pdf

# Output:
# ✅ Comparison Complete
# Cosine Similarity: 87.3%
# Jaccard Similarity: 72.1%
# Levenshtein Similarity: 85.4%
```

### 2. Generate HTML Report

```bash
# Create visual HTML report
python doc-comparator.py compare doc1.pdf doc2.pdf \
  --report html \
  --output comparison_report.html

# Opens in browser to view side-by-side comparison
```

### 3. Entity Comparison

```bash
# Compare entities between documents
python doc-comparator.py compare contract_v1.pdf contract_v2.pdf \
  --report text

# Shows:
# - Common entities: John Doe, Acme Corp
# - Added entities: Jane Smith
# - Removed entities: Bob Wilson
```

---

## 📚 Commands

### Command: `compare`

Compare two documents with multiple similarity metrics.

**Usage:**
```bash
python doc-comparator.py compare <file1> <file2> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--report FORMAT` | Report format (html, json, text) | text |
| `--output FILE` | Save report to file | stdout |
| `--no-entities` | Skip entity comparison | false |
| `--no-diff` | Skip detailed diff generation | false |
| `--threshold FLOAT` | Similarity threshold (0.0-1.0) | none |

**Examples:**

```bash
# Text comparison with results
python doc-comparator.py compare original.pdf modified.pdf

# HTML report with visualizations
python doc-comparator.py compare v1.txt v2.txt \
  --report html \
  --output diff.html

# Skip entity comparison for speed
python doc-comparator.py compare large1.pdf large2.pdf --no-entities

# Fail if similarity below threshold
python doc-comparator.py compare doc1.pdf doc2.pdf \
  --threshold 0.9
# Exit code 2 if similarity < 90%
```

**Output Example (Text):**
```
================================================================================
DOCUMENT COMPARISON REPORT
================================================================================
Document 1: original.pdf
Document 2: modified.pdf
Compared at: 2026-01-14T10:30:00Z

SIMILARITY METRICS
--------------------------------------------------------------------------------
Cosine Similarity:       87.3%
Jaccard Similarity:      72.1%
Levenshtein Similarity:  85.4%
Levenshtein Distance:    142

STRUCTURAL CHANGES
--------------------------------------------------------------------------------
Added Lines:        12
Removed Lines:       8
Modified Lines:      5
Unchanged Lines:   245

ENTITY COMPARISON
--------------------------------------------------------------------------------
Document 1 Entities:   23
Document 2 Entities:   25
Common Entities:       20
Unique to Doc 1:        3
Unique to Doc 2:        5
Entity Overlap:      74.1%
```

---

## 💼 Use Cases

### Use Case 1: Version Control for Contracts

**Scenario:** Compare contract versions to identify changes before signing.

```bash
# Compare versions
python doc-comparator.py compare \
  contracts/agreement_v1.pdf \
  contracts/agreement_v2.pdf \
  --report html \
  --output contract_changes.html

# Review HTML report:
# - Highlighted added/removed clauses
# - Entity changes (parties, dates, amounts)
# - Structural modifications
```

**Why it's useful:** Quickly identify what changed between contract drafts without manual reading.

---

### Use Case 2: Document Plagiarism Detection

**Scenario:** Check if two documents are too similar (potential plagiarism).

```bash
# Check similarity with threshold
python doc-comparator.py compare \
  student_paper1.pdf \
  student_paper2.pdf \
  --threshold 0.8 \
  --report json \
  --output similarity_report.json

# If similarity > 80%, exit code 0 (potential issue)
# If similarity < 80%, exit code 2 (acceptable)
```

**Why it's useful:** Automated similarity checking for academic integrity.

---

### Use Case 3: Track Document Changes Over Time

**Scenario:** Compare multiple versions of a document to track evolution.

```bash
# Compare versions in sequence
for i in {1..5}; do
  python doc-comparator.py compare \
    report_v$i.pdf \
    report_v$((i+1)).pdf \
    --report json \
    --output changes_v${i}_to_v$((i+1)).json
done

# Generate change summary
echo "Version changes:"
jq -r '.cosine_similarity' changes_*.json
```

**Why it's useful:** Understand how documents evolved through multiple revisions.

---

## ❗ Troubleshooting

### Issue: "Very low similarity scores for similar documents"

**Symptom:** Documents are similar but show < 50% similarity

**Causes & Solutions:**

1. **Different formatting/whitespace:**
   - Documents have different line breaks or spacing
   - Solution: Pre-process documents to normalize whitespace

2. **Different document formats:**
   - Comparing PDF to DOCX extracts text differently
   - Solution: Convert to same format first

3. **Language mismatch:**
   - One document in English, another in German
   - Solution: Use entity comparison instead of text

```bash
# Focus on entity comparison for formatted docs
python doc-comparator.py compare doc1.pdf doc2.docx \
  --no-diff  # Skip line-by-line diff
```

---

### Issue: "Out of memory with large documents"

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

```bash
# 1. Skip detailed diff for large files
python doc-comparator.py compare large1.pdf large2.pdf --no-diff

# 2. Compare smaller sections
python doc-splitter.py split large1.pdf -o parts1/
python doc-splitter.py split large2.pdf -o parts2/
# Then compare corresponding parts
```

---

### Issue: "HTML report not displaying correctly"

**Symptom:** HTML report looks broken in browser

**Solutions:**

1. **Check file size:** Large diffs may not render well
   ```bash
   # Limit diff size with --no-diff and focus on metrics
   python doc-comparator.py compare doc1.pdf doc2.pdf \
     --report html --no-diff
   ```

2. **Use text format for large reports:**
   ```bash
   python doc-comparator.py compare doc1.pdf doc2.pdf --report text
   ```

---

## 💡 Tips & Best Practices

### 1. Choose the Right Similarity Metric

```bash
# For general similarity: Use Cosine
# Good for: Overall content comparison

# For vocabulary overlap: Use Jaccard
# Good for: Checking if documents cover same topics

# For exact changes: Use Levenshtein
# Good for: Finding precise text modifications
```

### 2. Use Thresholds for Automation

```bash
# Fail CI/CD if documents are too different
python doc-comparator.py compare \
  expected_output.txt actual_output.txt \
  --threshold 0.95

# In CI script:
if [ $? -eq 2 ]; then
  echo "Output differs from expected!"
  exit 1
fi
```

### 3. Generate HTML Reports for Stakeholders

```bash
# Create visual reports for non-technical reviewers
python doc-comparator.py compare \
  proposal_draft.pdf proposal_final.pdf \
  --report html \
  --output "Proposal Changes - $(date +%Y%m%d).html"

# Email the HTML file to stakeholders
```

### 4. Batch Compare Multiple Documents

```bash
# Compare all documents in a directory
for file1 in docs/v1/*.pdf; do
  filename=$(basename "$file1")
  file2="docs/v2/$filename"

  if [ -f "$file2" ]; then
    python doc-comparator.py compare "$file1" "$file2" \
      --report json \
      --output "results/${filename%.pdf}_comparison.json"
  fi
done
```

### 5. Combine with Other Tools

```bash
# 1. Anonymize both documents before comparison
python doc-anonymizer.py anonymize doc1.pdf --output doc1_anon.txt
python doc-anonymizer.py anonymize doc2.pdf --output doc2_anon.txt

# 2. Compare anonymized versions
python doc-comparator.py compare doc1_anon.txt doc2_anon.txt

# Useful for: Comparing sensitive documents while hiding PII
```

### 6. JSON Output for Programmatic Use

```bash
# Get JSON output for scripting
python doc-comparator.py compare doc1.pdf doc2.pdf \
  --report json \
  --output comparison.json

# Parse with jq
jq '.cosine_similarity' comparison.json
jq '.entity_changes.added' comparison.json
```

---

## 🔄 Related Tools

- **doc-processor.py** - Process documents before comparison
- **doc-quality.py** - Assess quality of both documents
- **doc-anonymizer.py** - Remove PII before comparing
- **doc-splitter.py** - Split large documents for comparison

---

## 📊 Performance Tips

### Expected Comparison Times

| Document Size | Basic Compare | With HTML Diff |
|---------------|---------------|----------------|
| 1 page | ~0.5s | ~1s |
| 10 pages | ~2s | ~5s |
| 100 pages | ~15s | ~45s |

### Optimization Strategies

```bash
# Fast comparison (skip diff)
python doc-comparator.py compare doc1.pdf doc2.pdf --no-diff --no-entities

# Balanced (entities only, no diff)
python doc-comparator.py compare doc1.pdf doc2.pdf --no-diff

# Full analysis (slower but complete)
python doc-comparator.py compare doc1.pdf doc2.pdf --report html
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
