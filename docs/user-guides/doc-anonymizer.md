# 🔒 Doc-Anonymizer User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** GDPR/HIPAA-compliant document anonymization and PII protection

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

**doc-anonymizer.py** automatically detects and removes personally identifiable information (PII) from documents, ensuring GDPR and HIPAA compliance.

### Key Features

- ✅ **PII Detection** - Automatically find names, emails, phones, addresses, IBANs
- ✅ **Multiple Strategies** - Redaction, masking, replacement, pseudonymization
- ✅ **GDPR/HIPAA Compliance** - Built-in compliance modes
- ✅ **Reversible Anonymization** - Optional encrypted mapping for de-anonymization
- ✅ **Audit Trail** - Complete logging for compliance requirements
- ✅ **Batch Processing** - Anonymize entire directories

### Anonymization Strategies

| Strategy | Example | Use Case |
|----------|---------|----------|
| **Redaction** | Max Müller → `[PERSON]` | Complete removal |
| **Masking** | max@email.com → `m**@e******.com` | Partial visibility |
| **Replacement** | Max Müller → `John Doe` | Fake data substitution |
| **Pseudonymization** | Max Müller → `PSEUDO_A1B2C3D4` | Consistent hash |
| **Generalization** | 01.01.1990 → `1990` | Reduced precision |

---

## ⚡ Quick Start

### 1. Scan for PII

```bash
# Detect PII without anonymizing
python doc-anonymizer.py scan contract.pdf

# Output:
# 📊 PII Detection Report
# PII items detected: 15
#   [PERSON     ] Max Mustermann (confidence: 0.95)
#   [EMAIL      ] max@example.com (confidence: 0.98)
#   [PHONE      ] +49 123 456789 (confidence: 0.92)
```

### 2. Basic Anonymization (Redaction)

```bash
# Anonymize with default redaction strategy
python doc-anonymizer.py anonymize document.pdf \
  --output anonymized.pdf

# Result: All PII replaced with [PERSON], [EMAIL], etc.
```

### 3. Masking Strategy

```bash
# Partially mask PII for readability
python doc-anonymizer.py anonymize document.pdf \
  --strategy masking \
  --output masked.pdf

# Result:
# Max Mustermann → M** M*********
# max@email.com → m**@e*****.com
```

---

## 📚 Commands

### Command: `scan`

Scan document for PII without anonymizing.

**Usage:**
```bash
python doc-anonymizer.py scan <file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--report FILE` | Save report to JSON file | stdout |

**Examples:**

```bash
# Basic scan
python doc-anonymizer.py scan sensitive_doc.pdf

# Save detailed report
python doc-anonymizer.py scan employee_data.pdf \
  --report pii_report.json

# Review report
cat pii_report.json | jq '.pii_items[] | select(.type=="PERSON")'
```

**Output Example:**
```json
{
  "file": "document.pdf",
  "scan_date": "2026-01-14T10:30:00Z",
  "pii_count": 15,
  "pii_items": [
    {
      "text": "Max Mustermann",
      "type": "PERSON",
      "start": 0,
      "end": 14,
      "confidence": 0.95
    },
    {
      "text": "max@example.com",
      "type": "EMAIL",
      "start": 45,
      "end": 60,
      "confidence": 0.98
    }
  ]
}
```

---

### Command: `anonymize`

Anonymize document with PII removal.

**Usage:**
```bash
python doc-anonymizer.py anonymize <file> --output <output_file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output FILE` | Output file path (required) | - |
| `--strategy STRATEGY` | Anonymization strategy | redaction |
| `--compliance MODE` | Compliance mode (gdpr, hipaa, custom) | gdpr |
| `--reversible` | Enable reversible anonymization | false |
| `--mapping-file FILE` | Save mapping for de-anonymization | none |
| `--audit-log` | Create audit trail | false |

**Strategies:**
- `redaction` - Complete replacement with tags
- `masking` - Partial masking with asterisks
- `replacement` - Fake data substitution
- `pseudonymization` - Hash-based pseudonyms
- `generalization` - Reduce precision (dates → years)

**Examples:**

```bash
# GDPR-compliant redaction
python doc-anonymizer.py anonymize gdpr_doc.pdf \
  --output anonymized.pdf \
  --compliance gdpr \
  --audit-log

# Masking with partial visibility
python doc-anonymizer.py anonymize contract.pdf \
  --output masked_contract.pdf \
  --strategy masking

# Reversible anonymization (with encrypted mapping)
python doc-anonymizer.py anonymize sensitive.pdf \
  --output anonymized.pdf \
  --reversible \
  --mapping-file mapping.enc \
  --audit-log

# HIPAA compliance for medical records
python doc-anonymizer.py anonymize medical_record.pdf \
  --output anon_record.pdf \
  --compliance hipaa \
  --strategy replacement
```

**Output Example:**
```
✅ Anonymization Complete
================================================================================
Original file:     sensitive.pdf
Anonymized file:   anonymized.pdf
Strategy:          masking
Compliance mode:   gdpr
PII detected:      18
PII anonymized:    18

Audit trail: 3 events recorded
```

---

### Command: `deanonymize`

Reverse anonymization using mapping file.

**Usage:**
```bash
python doc-anonymizer.py deanonymize <file> --mapping-file <mapping> --output <output_file>
```

**Examples:**

```bash
# Restore original data
python doc-anonymizer.py deanonymize anonymized.pdf \
  --mapping-file mapping.enc \
  --output restored.pdf

# Only works if original anonymization used --reversible
```

---

### Command: `batch`

Batch anonymize multiple documents.

**Usage:**
```bash
python doc-anonymizer.py batch <input_dir> --output-dir <output_dir> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir DIR` | Output directory (required) | - |
| `--pattern PATTERN` | File pattern to match | *.* |
| `--strategy STRATEGY` | Anonymization strategy | redaction |

**Examples:**

```bash
# Anonymize all documents in directory
python doc-anonymizer.py batch /documents/ \
  --output-dir /anonymized/ \
  --strategy masking

# Specific file pattern
python doc-anonymizer.py batch /contracts/ \
  --output-dir /anon_contracts/ \
  --pattern "*.pdf" \
  --strategy replacement
```

---

## 💼 Use Cases

### Use Case 1: GDPR Data Subject Request

**Scenario:** Customer requests data erasure under GDPR Article 17.

```bash
# 1. Scan all customer documents
for doc in customer_123/*.pdf; do
  python doc-anonymizer.py scan "$doc" --report "scans/$(basename $doc).json"
done

# 2. Anonymize documents
python doc-anonymizer.py batch customer_123/ \
  --output-dir customer_123_anonymized/ \
  --compliance gdpr \
  --audit-log

# 3. Review audit logs for compliance proof
ls customer_123_anonymized/*_audit.log
```

**Why it's useful:** Automate GDPR compliance with full audit trail.

---

### Use Case 2: Share Medical Records (HIPAA)

**Scenario:** Share patient records with researchers while protecting PHI.

```bash
# Anonymize medical records with replacement
python doc-anonymizer.py anonymize patient_record.pdf \
  --output research_record.pdf \
  --compliance hipaa \
  --strategy replacement \
  --audit-log

# Result:
# - Patient names replaced with John Doe, Jane Smith, etc.
# - Dates generalized to years
# - Phone/email masked
# - Full audit trail for compliance
```

**Why it's useful:** Enable research while maintaining HIPAA compliance.

---

### Use Case 3: Reversible Anonymization for Testing

**Scenario:** Test production data in staging environment, restore if needed.

```bash
# 1. Anonymize for staging
python doc-anonymizer.py anonymize production_data.pdf \
  --output staging_data.pdf \
  --reversible \
  --mapping-file prod_mapping.enc \
  --strategy pseudonymization

# 2. Use in staging environment
# ... run tests with staging_data.pdf ...

# 3. De-anonymize if needed
python doc-anonymizer.py deanonymize staging_data.pdf \
  --mapping-file prod_mapping.enc \
  --output restored_data.pdf

# IMPORTANT: Keep mapping.enc files secure!
```

**Why it's useful:** Safe testing with production data.

---

## ❗ Troubleshooting

### Issue: "No PII detected in document"

**Symptom:** Scan returns 0 PII items but you know there's personal data

**Causes & Solutions:**

1. **Language mismatch:** NER model is English-only
   ```bash
   # Check extracted text first
   python doc-processor.py process doc.pdf --format text | head -20
   ```

2. **Poor text extraction:** Scanned PDFs or images
   - Solution: Use OCR before anonymization

3. **Non-standard PII format:** Custom IDs not detected
   - Solution: Use custom patterns (future feature)

---

### Issue: "Mapping file cannot be loaded"

**Error:**
```
ERROR: Failed to load mapping file
```

**Solutions:**

```bash
# Ensure mapping file exists
ls -lh mapping.enc

# Check file wasn't corrupted
file mapping.enc

# Mapping files are base64-encoded JSON
# DO NOT edit manually

# Create new anonymization with new mapping
python doc-anonymizer.py anonymize doc.pdf \
  --output new_anon.pdf \
  --reversible \
  --mapping-file new_mapping.enc
```

---

### Issue: "Over-anonymization or under-anonymization"

**Symptom:** Too much or too little data removed

**Solutions:**

```bash
# 1. Review scan first
python doc-anonymizer.py scan doc.pdf --report scan.json

# 2. Check what will be anonymized
cat scan.json | jq '.pii_items[] | .text'

# 3. Adjust strategy
# Under-anonymization: Use redaction (most aggressive)
python doc-anonymizer.py anonymize doc.pdf --strategy redaction

# Over-anonymization: Use masking (partial visibility)
python doc-anonymizer.py anonymize doc.pdf --strategy masking
```

---

## 💡 Tips & Best Practices

### 1. Always Scan Before Anonymizing

```bash
# Step 1: Scan and review
python doc-anonymizer.py scan document.pdf --report scan.json
cat scan.json | jq '.pii_count'

# Step 2: Review what will be anonymized
cat scan.json | jq '.pii_items[] | "\(.type): \(.text)"'

# Step 3: Anonymize with confidence
python doc-anonymizer.py anonymize document.pdf --output anon.pdf
```

### 2. Choose Strategy Based on Use Case

```bash
# Public release: Use redaction (most secure)
python doc-anonymizer.py anonymize doc.pdf \
  --strategy redaction \
  --output public_doc.pdf

# Internal use: Use masking (readable)
python doc-anonymizer.py anonymize doc.pdf \
  --strategy masking \
  --output internal_doc.pdf

# Testing: Use pseudonymization (reversible)
python doc-anonymizer.py anonymize doc.pdf \
  --strategy pseudonymization \
  --reversible \
  --mapping-file test_mapping.enc
```

### 3. Enable Audit Logs for Compliance

```bash
# GDPR/HIPAA require audit trails
python doc-anonymizer.py anonymize document.pdf \
  --output anonymized.pdf \
  --compliance gdpr \
  --audit-log

# Creates audit trail showing:
# - When anonymization occurred
# - How many PII items removed
# - What compliance mode used
```

### 4. Secure Mapping Files

```bash
# Mapping files contain PII mapping - treat as sensitive!

# 1. Restrict permissions
chmod 600 mapping.enc

# 2. Encrypt at rest (if needed)
gpg --encrypt --recipient you@example.com mapping.enc

# 3. Store securely (not in git!)
echo "*.enc" >> .gitignore
```

### 5. Batch Processing Pipeline

```bash
# Create full anonymization pipeline
mkdir -p input output scans

# 1. Scan all documents
for doc in input/*.pdf; do
  python doc-anonymizer.py scan "$doc" \
    --report "scans/$(basename $doc .pdf).json"
done

# 2. Review scans
echo "Total PII items found:"
jq -s 'map(.pii_count) | add' scans/*.json

# 3. Batch anonymize
python doc-anonymizer.py batch input/ \
  --output-dir output/ \
  --strategy masking \
  --audit-log

# 4. Archive originals securely
tar -czf originals_backup_$(date +%Y%m%d).tar.gz input/
```

---

## 🔄 Related Tools

- **doc-processor.py** - Process documents before anonymization
- **doc-quality.py** - Check quality of anonymized documents
- **doc-comparator.py** - Compare original vs anonymized
- **doc-batch-processor.py** - Large-scale anonymization

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
