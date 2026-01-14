# 📑 Doc-Merger User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Intelligent document merging with multiple strategies

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

**doc-merger.py** merges multiple documents into a single unified file with smart formatting, table of contents, and metadata preservation.

### Key Features

- ✅ **5 Merge Modes** - Concatenate, interleave, smart, chapters, sections
- ✅ **Auto Table of Contents** - Generate navigation index
- ✅ **Format Preservation** - Maintain structure and metadata
- ✅ **Deduplication** - Remove duplicate content
- ✅ **Smart Formatting** - Normalize whitespace and structure

### Merge Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **concatenate** | Simple sequential joining | Default, fastest |
| **interleave** | Alternate lines between docs | Parallel content |
| **smart** | Intelligent merge with dedup | Clean output |
| **chapters** | Each doc becomes a chapter | Books, reports |
| **sections** | Each doc becomes a section | Articles, guides |

---

## ⚡ Quick Start

### 1. Simple Merge

```bash
# Merge three documents
python doc-merger.py merge \
  file1.txt file2.txt file3.txt \
  -o combined.txt

# Output:
# ✅ Merge completed successfully!
# Output file: combined.txt
# Mode: concatenate
# Input files: 3
# Total lines: 1,245
# Total words: 8,932
```

### 2. With Table of Contents

```bash
# Add auto-generated TOC
python doc-merger.py merge *.txt \
  -o output.txt \
  --toc

# Result includes:
# ======================================================================
# TABLE OF CONTENTS
# ======================================================================
# Total Documents: 5
# Generated: 2026-01-14 10:30:00
#
# 1. introduction
#    File: introduction.txt
#    Size: 2,451 bytes
#    Lines: 45 | Words: 387
```

### 3. Chapter-Based Merge

```bash
# Merge as book chapters
python doc-merger.py merge \
  chapter1.txt chapter2.txt chapter3.txt \
  -o book.txt \
  --mode chapters \
  --toc
```

---

## 📚 Commands

### Command: `merge`

Merge multiple documents into one.

**Usage:**
```bash
python doc-merger.py merge <files...> -o <output> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output FILE` | Output file (required) | - |
| `--mode MODE` | Merge mode | concatenate |
| `--toc` | Add table of contents | false |
| `--no-headers` | Don't add document headers | false |
| `--separator TEXT` | Separator between documents | \n\n |
| `--titles TITLES` | Custom titles for documents | filenames |
| `--remove-duplicates` | Remove duplicate documents | false |
| `--backup` | Create backup if output exists | false |

**Merge Modes:**
- `concatenate` - Sequential joining (default)
- `interleave` - Alternate between documents
- `smart` - Intelligent with deduplication
- `chapters` - Chapter-based organization
- `sections` - Section-based organization

**Examples:**

```bash
# Basic concatenation
python doc-merger.py merge file1.txt file2.txt -o output.txt

# With table of contents
python doc-merger.py merge *.txt -o combined.txt --toc

# Chapter mode
python doc-merger.py merge ch*.txt \
  -o book.txt \
  --mode chapters \
  --toc

# Smart merge with deduplication
python doc-merger.py merge doc*.txt \
  -o output.txt \
  --mode smart \
  --remove-duplicates

# Custom titles
python doc-merger.py merge file1.txt file2.txt file3.txt \
  -o output.txt \
  --titles "Introduction" "Main Content" "Conclusion"

# Custom separator
python doc-merger.py merge *.txt \
  -o output.txt \
  --separator "---\n\n"

# Backup existing output
python doc-merger.py merge *.txt \
  -o existing_output.txt \
  --backup
# Creates: existing_output_20260114_103000.txt.bak
```

**Output Example:**
```
✅ Merge completed successfully!
======================================================================
Output file: combined_report.txt
Mode: chapters
Input files: 5
Total lines: 1,245
Total words: 8,932
Total chars: 52,341
Execution time: 0.15s
Table of contents: Yes
```

---

### Command: `analyze`

Analyze documents before merging.

**Usage:**
```bash
python doc-merger.py analyze <files...> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output FILE` | Save analysis to JSON | stdout |

**Examples:**

```bash
# Analyze before merging
python doc-merger.py analyze file1.txt file2.txt file3.txt

# Output:
# 📊 Document Analysis
# ======================================================================
# Total documents: 3
# Total size: 15,234 bytes
# Total lines: 287
# Total words: 1,945
# Duplicates found: 0
#
# Documents:
# 1. file1.txt
#    Size: 5,123 bytes
#    Lines: 95 | Words: 642

# Save to JSON for programmatic use
python doc-merger.py analyze *.txt -o analysis.json
cat analysis.json | jq '.total_words'
```

---

## 💼 Use Cases

### Use Case 1: Merge Report Chapters

**Scenario:** Combine individual chapter files into a complete report.

```bash
# Merge chapters with TOC
python doc-merger.py merge \
  01_executive_summary.txt \
  02_methodology.txt \
  03_findings.txt \
  04_recommendations.txt \
  05_conclusion.txt \
  -o annual_report.txt \
  --mode chapters \
  --toc \
  --titles "Executive Summary" "Methodology" "Findings" "Recommendations" "Conclusion"

# Result: Professional report with:
# - Auto-generated table of contents
# - Chapter headers
# - Consistent formatting
```

**Why it's useful:** Professional document assembly from components.

---

### Use Case 2: Combine Daily Logs

**Scenario:** Merge daily log files into weekly/monthly reports.

```bash
# Merge week's logs
python doc-merger.py merge \
  logs/2024-01-{01..07}.txt \
  -o weekly_log_week1.txt \
  --mode sections \
  --toc

# Merge month's logs
for week in {1..4}; do
  python doc-merger.py merge logs/week${week}_*.txt \
    -o weekly_summary_week${week}.txt
done

python doc-merger.py merge weekly_summary_*.txt \
  -o monthly_report_january.txt \
  --mode chapters \
  --toc
```

**Why it's useful:** Automated log consolidation and reporting.

---

### Use Case 3: Create Documentation Bundle

**Scenario:** Bundle multiple markdown docs into single file.

```bash
# Merge documentation
python doc-merger.py merge \
  docs/README.md \
  docs/installation.md \
  docs/usage.md \
  docs/api.md \
  docs/troubleshooting.md \
  docs/faq.md \
  -o complete_documentation.md \
  --mode sections \
  --toc \
  --no-headers

# Result: Complete docs in single file for offline use
```

**Why it's useful:** Offline documentation distribution.

---

## ❗ Troubleshooting

### Issue: "File not found"

**Error:**
```
ERROR: File not found: chapter5.txt
```

**Solutions:**

```bash
# Check file exists
ls -lh chapter5.txt

# Use absolute paths
python doc-merger.py merge \
  /full/path/to/file1.txt \
  /full/path/to/file2.txt \
  -o output.txt

# Use wildcards carefully
python doc-merger.py merge chapters/*.txt -o book.txt
# Note: Merged in alphabetical order
```

---

### Issue: "Output file too large"

**Symptom:** Merged file is unexpectedly large

**Causes & Solutions:**

1. **Check for duplicates:**
   ```bash
   python doc-merger.py analyze *.txt
   # Check "Duplicates found: N"

   # Merge with dedup
   python doc-merger.py merge *.txt \
     -o output.txt \
     --remove-duplicates
   ```

2. **Inspect input files:**
   ```bash
   # Check file sizes
   ls -lh *.txt | sort -k5 -rh

   # Remove large/unwanted files before merging
   ```

---

### Issue: "Formatting lost in merged document"

**Symptom:** Merged document has inconsistent spacing

**Solutions:**

```bash
# Use smart mode (normalizes whitespace)
python doc-merger.py merge *.txt \
  -o output.txt \
  --mode smart

# Smart mode automatically:
# - Removes trailing whitespace
# - Normalizes line breaks
# - Removes excessive blank lines
```

---

## 💡 Tips & Best Practices

### 1. Always Analyze First

```bash
# Step 1: Analyze inputs
python doc-merger.py analyze *.txt

# Review:
# - Total size (too large?)
# - Duplicates (need --remove-duplicates?)
# - File count (merging correctly?)

# Step 2: Merge with confidence
python doc-merger.py merge *.txt -o output.txt
```

### 2. Use Appropriate Mode

```bash
# Sequential content: concatenate (fast, simple)
python doc-merger.py merge *.txt -o output.txt

# Book/report: chapters (professional headers)
python doc-merger.py merge chapters/*.txt \
  -o book.txt --mode chapters --toc

# Article/guide: sections (lighter headers)
python doc-merger.py merge parts/*.txt \
  -o guide.txt --mode sections

# Clean output: smart (dedup + normalize)
python doc-merger.py merge *.txt \
  -o output.txt --mode smart --remove-duplicates
```

### 3. Add Table of Contents for Long Documents

```bash
# TOC recommended for:
# - 5+ input files
# - Result > 1000 lines
# - Reports and books

python doc-merger.py merge *.txt \
  -o report.txt \
  --toc \
  --mode chapters
```

### 4. Name Files for Correct Order

```bash
# Good: Alphabetical order matches logical order
01_intro.txt
02_chapter1.txt
03_chapter2.txt
04_conclusion.txt

python doc-merger.py merge *.txt -o book.txt

# Bad: Unordered files
intro.txt
chapter2.txt
chapter1.txt
conclusion.txt
# Results in wrong order!

# Fix: Use explicit list
python doc-merger.py merge \
  intro.txt chapter1.txt chapter2.txt conclusion.txt \
  -o book.txt
```

### 5. Backup Important Files

```bash
# Automatically backup if output exists
python doc-merger.py merge *.txt \
  -o important_output.txt \
  --backup

# Manual backup
cp important_output.txt important_output_$(date +%Y%m%d).bak

# Then merge
python doc-merger.py merge *.txt -o important_output.txt
```

### 6. Custom Titles for Better TOC

```bash
# Without custom titles (uses filenames)
python doc-merger.py merge file1.txt file2.txt file3.txt \
  -o output.txt --toc

# TOC shows: file1, file2, file3

# With custom titles (professional)
python doc-merger.py merge file1.txt file2.txt file3.txt \
  -o output.txt \
  --toc \
  --titles "Executive Summary" "Detailed Analysis" "Recommendations"

# TOC shows: Executive Summary, Detailed Analysis, Recommendations
```

### 7. Batch Merge Multiple Sets

```bash
# Merge multiple document sets
for dir in reports/*/; do
  dirname=$(basename "$dir")
  python doc-merger.py merge "$dir"/*.txt \
    -o "merged/${dirname}_complete.txt" \
    --mode chapters \
    --toc
done

# Result: One merged file per directory
```

---

## 🔄 Related Tools

- **doc-splitter.py** - Split documents (reverse operation)
- **doc-comparator.py** - Compare merged vs original
- **doc-quality.py** - Check quality of merged document

---

## 📊 Performance

### Expected Merge Times

| Total Input Size | Files | Time |
|------------------|-------|------|
| < 1 MB | 10 | < 0.1s |
| 1-10 MB | 50 | < 0.5s |
| 10-100 MB | 100 | < 3s |
| 100-500 MB | 500 | < 15s |

### Optimization Tips

```bash
# Fast merge (skip extras)
python doc-merger.py merge *.txt -o output.txt --no-headers

# Fastest mode
python doc-merger.py merge *.txt -o output.txt
# (concatenate mode is fastest)

# Avoid for large batches:
# - --toc (requires extra processing)
# - --remove-duplicates (hash checking)
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
