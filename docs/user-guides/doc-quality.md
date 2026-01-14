# 📊 Doc-Quality User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Comprehensive document quality assessment and validation

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

**doc-quality.py** analyzes documents across 5 quality dimensions, providing actionable insights and recommendations for improvement.

### Key Features

- ✅ **5 Quality Dimensions** - Completeness, Accuracy, Consistency, Readability, Timeliness
- ✅ **Readability Metrics** - Flesch Reading Ease, sentence complexity
- ✅ **Accuracy Validation** - Check emails, phones, dates, IBANs
- ✅ **Quality Scoring** - 0-100 score with pass/fail thresholds
- ✅ **Actionable Recommendations** - Specific improvement suggestions

### Quality Dimensions

| Dimension | What It Checks | Score Factors |
|-----------|----------------|---------------|
| **Completeness** | Sufficient content, required fields | Text length, entity coverage |
| **Accuracy** | Valid data formats | Email/phone/date validation |
| **Consistency** | Internal coherence | Entity mentions, formatting |
| **Readability** | Easy to understand | Flesch score, sentence length |
| **Timeliness** | Up-to-date information | Date recency |

---

## ⚡ Quick Start

### 1. Basic Quality Check

```bash
# Analyze document quality
python doc-quality.py analyze document.pdf

# Output:
# 📊 Document Quality Report
# Overall Quality: 78.5/100
# Status: ✅ PASSED
#
# Dimension Scores:
#   ✅ Completeness:    85.0/100
#   ✅ Accuracy:        92.3/100
#   ✅ Consistency:     88.0/100
#   ⚠️  Readability:     65.2/100
#   ✅ Timeliness:      80.0/100
```

### 2. Full Analysis with Threshold

```bash
# Fail if quality below 80%
python doc-quality.py analyze report.pdf \
  --full \
  --threshold 80 \
  --fail-on-low-quality

# Exit code 0 if quality >= 80
# Exit code 2 if quality < 80
```

### 3. Check Specific Dimension

```bash
# Check only readability
python doc-quality.py analyze article.pdf \
  --dimension readability \
  --output readability_report.json
```

---

## 📚 Commands

### Command: `analyze`

Analyze document quality across all or specific dimensions.

**Usage:**
```bash
python doc-quality.py analyze <file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--full` | Run full analysis (all dimensions) | false |
| `--dimension DIM` | Check specific dimension(s) | all |
| `--threshold SCORE` | Quality threshold (0-100) | 0 |
| `--fail-on-low-quality` | Exit with error if below threshold | false |
| `--output FILE` | Save report to JSON file | stdout |

**Dimensions:**
- `completeness` - Content completeness
- `accuracy` - Data accuracy
- `consistency` - Internal consistency
- `readability` - Text readability
- `timeliness` - Information recency

**Examples:**

```bash
# Full quality analysis
python doc-quality.py analyze document.pdf --full

# Check specific dimensions
python doc-quality.py analyze report.pdf \
  --dimension completeness \
  --dimension accuracy

# Quality gate (CI/CD)
python doc-quality.py analyze output.pdf \
  --threshold 85 \
  --fail-on-low-quality \
  --output quality_check.json

# Exit code 2 if quality < 85

# Multiple documents
for doc in docs/*.pdf; do
  python doc-quality.py analyze "$doc" --threshold 70
  if [ $? -eq 2 ]; then
    echo "FAIL: $doc"
  fi
done
```

**Output Example:**
```
📊 Document Quality Report
================================================================================
File: technical_report.pdf
Overall Quality: 78.5/100
Status: ✅ PASSED

Dimension Scores:
  ✅ Completeness      :  85.0/100
  ✅ Accuracy          :  92.3/100
  ✅ Consistency       :  88.0/100
  ⚠️  Readability       :  65.2/100
  ✅ Timeliness        :  80.0/100

Issues Found: 3
  Critical: 0
  High:     0
  Medium:   2
  Low:      1

Recommendations:
  • Improve Readability: Current score 65.2/100
  • Document has many long sentences (15/50)
    - Break long sentences into shorter ones for better readability
```

---

### Command: `batch`

Batch quality check multiple documents.

**Usage:**
```bash
python doc-quality.py batch <input_dir> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output FILE` | Save batch report to file | stdout |
| `--threshold SCORE` | Quality threshold | 70.0 |

**Examples:**

```bash
# Check all documents in directory
python doc-quality.py batch /documents/ \
  --threshold 80 \
  --output batch_quality_report.json

# Review results
cat batch_quality_report.json | jq '.passed, .failed'
```

**Output Example:**
```
✅ report1.pdf: 85.2/100
❌ report2.pdf: 68.5/100
✅ report3.pdf: 92.1/100

Batch report saved to: batch_quality_report.json
```

---

## 💼 Use Cases

### Use Case 1: Quality Gate for Publishing

**Scenario:** Ensure documents meet quality standards before publication.

```bash
# Pre-publish quality check
python doc-quality.py analyze draft_article.pdf \
  --full \
  --threshold 85 \
  --fail-on-low-quality \
  --output quality_report.json

# In CI/CD pipeline:
if [ $? -eq 0 ]; then
  echo "✅ Quality check passed - ready for publication"
  ./publish.sh draft_article.pdf
else
  echo "❌ Quality check failed - needs revision"
  cat quality_report.json | jq '.recommendations'
  exit 1
fi
```

**Why it's useful:** Automated quality assurance before content goes live.

---

### Use Case 2: Content Improvement Workflow

**Scenario:** Systematically improve document quality based on analysis.

```bash
# 1. Initial analysis
python doc-quality.py analyze draft.pdf --full --output v1_quality.json

# Review recommendations
cat v1_quality.json | jq '.recommendations[]'

# Example output:
# - "Improve Readability: Current score 62.1/100"
# - "Document has many long sentences (25/80)"
# - "Complex word ratio: 15.3% (reduce to <10%)"

# 2. Make improvements
# ... edit document ...

# 3. Re-analyze
python doc-quality.py analyze draft_v2.pdf --full --output v2_quality.json

# 4. Compare scores
echo "V1 Quality: $(jq '.overall_quality' v1_quality.json)"
echo "V2 Quality: $(jq '.overall_quality' v2_quality.json)"
```

**Why it's useful:** Data-driven document improvement.

---

### Use Case 3: Batch Quality Audit

**Scenario:** Audit quality of entire document repository.

```bash
# Analyze all documents
python doc-quality.py batch /document_repository/ \
  --threshold 75 \
  --output audit_report.json

# Generate summary
jq -r '.results[] | "\(.file_path): \(.overall_quality)"' audit_report.json | \
  sort -t: -k2 -n > quality_summary.txt

# Find low-quality documents
jq -r '.results[] | select(.overall_quality < 70) | .file_path' audit_report.json

# Calculate average quality
jq '[.results[].overall_quality] | add / length' audit_report.json
```

**Why it's useful:** Identify documents needing attention.

---

## ❗ Troubleshooting

### Issue: "Low readability score but document seems fine"

**Symptom:** Readability score < 50 for professional documents

**Explanation:** Flesch Reading Ease scale:
- 90-100: Very easy (5th grade)
- 60-70: Standard (8th-9th grade)
- 30-50: Difficult (college)
- 0-30: Very difficult (professional)

**Solutions:**

```bash
# Technical/legal documents naturally score lower
# This is expected and OK for professional content

# Check actual metrics
python doc-quality.py analyze technical_doc.pdf --output metrics.json
cat metrics.json | jq '.dimensions.readability.metrics'

# Example output:
# {
#   "flesch_reading_ease": 45.2,  # Normal for technical docs
#   "avg_sentence_length": 22.5,
#   "complex_word_ratio": 0.18
# }

# For general audience, target 60-70
# For technical audience, 30-50 is acceptable
```

---

### Issue: "False accuracy warnings"

**Symptom:** Valid emails/phones reported as invalid

**Causes:**

1. **Non-standard formats:** International phones
2. **Context-dependent:** Partial emails in examples

**Solutions:**

```bash
# Check what was flagged
python doc-quality.py analyze doc.pdf --output report.json
cat report.json | jq '.dimensions.accuracy.issues[]'

# Review false positives manually
# Accuracy validation is conservative - some warnings OK
```

---

### Issue: "Empty or missing dimension scores"

**Error:** Some dimensions show 0 or null scores

**Solutions:**

```bash
# Ensure full analysis mode
python doc-quality.py analyze doc.pdf --full

# Check if document has enough content
python doc-quality.py analyze doc.pdf --dimension completeness

# Minimum requirements:
# - At least 100 characters
# - At least 20 words
# - Valid text extraction
```

---

## 💡 Tips & Best Practices

### 1. Use Quality Gates in CI/CD

```bash
# .gitlab-ci.yml or similar
quality-check:
  script:
    - python doc-quality.py analyze output.pdf \
        --threshold 80 \
        --fail-on-low-quality
  artifacts:
    reports:
      quality: quality_report.json
```

### 2. Set Appropriate Thresholds

```bash
# Different thresholds for different content types

# Marketing materials (high readability required)
python doc-quality.py analyze marketing.pdf --threshold 80

# Technical documentation (lower readability OK)
python doc-quality.py analyze technical_doc.pdf --threshold 65

# Legal documents (focus on completeness/accuracy)
python doc-quality.py analyze contract.pdf \
  --dimension completeness \
  --dimension accuracy \
  --threshold 90
```

### 3. Focus on Actionable Issues

```bash
# Get specific recommendations
python doc-quality.py analyze doc.pdf --output report.json

# Filter high-priority issues
cat report.json | jq '.dimensions[].issues[] | select(.severity == "high")'

# Focus on:
# 1. Critical/High severity issues first
# 2. Dimensions below 70/100
# 3. Issues with suggestions
```

### 4. Track Quality Over Time

```bash
# Save quality reports with timestamps
python doc-quality.py analyze doc.pdf \
  --output "quality_reports/$(date +%Y%m%d_%H%M%S)_quality.json"

# Generate trend chart
ls quality_reports/*.json | while read file; do
  echo "$(basename $file): $(jq '.overall_quality' $file)"
done | sort
```

### 5. Combine with Other Tools

```bash
# Quality pipeline
# 1. Process document
python doc-processor.py process doc.pdf --output processed.json

# 2. Check quality
python doc-quality.py analyze doc.pdf --full --output quality.json

# 3. If quality good, anonymize and publish
if [ $(jq '.overall_quality' quality.json | cut -d. -f1) -ge 80 ]; then
  python doc-anonymizer.py anonymize doc.pdf --output public.pdf
  echo "✅ Published: public.pdf"
fi
```

---

## 📐 Quality Score Interpretation

### Overall Quality Score

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Ready for publication |
| 80-89 | Good | Minor improvements |
| 70-79 | Acceptable | Consider revision |
| 60-69 | Fair | Needs improvement |
| 0-59 | Poor | Major revision needed |

### Dimension-Specific Thresholds

```bash
# Completeness: 80+ (ensure sufficient content)
# Accuracy: 90+ (data must be correct)
# Consistency: 75+ (internal coherence)
# Readability: 60+ general, 40+ technical
# Timeliness: 70+ (avoid outdated info)
```

---

## 🔄 Related Tools

- **doc-processor.py** - Process documents before quality check
- **doc-comparator.py** - Compare quality between versions
- **doc-anonymizer.py** - Ensure anonymization doesn't hurt quality

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
