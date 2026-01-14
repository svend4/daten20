# ✂️ Doc-Splitter User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** Intelligent document splitting with smart boundary detection

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

**doc-splitter.py** splits large documents into manageable parts with smart boundary detection and context preservation.

### Key Features

- ✅ **6 Split Modes** - Size, delimiter, chapter, section, page, smart
- ✅ **Smart Boundaries** - Preserve paragraphs and sentences
- ✅ **Auto Numbering** - Generate sequential file names
- ✅ **Index Generation** - Create index file with metadata
- ✅ **Preview Mode** - Test split without creating files

### Split Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **size** | Split by lines/words/chars | Large text files |
| **delimiter** | Split by custom pattern | Structured data |
| **chapter** | Split by chapter markers | Books, reports |
| **section** | Split by section headers | Articles, guides |
| **page** | Split by page markers | Formatted documents |
| **smart** | Preserve context at boundaries | Clean splits |

---

## ⚡ Quick Start

### 1. Split by Lines

```bash
# Split into 100-line chunks
python doc-splitter.py split large_file.txt \
  -o parts/ \
  --lines 100

# Output:
# ✅ Split completed successfully!
# Input file: large_file.txt
# Output dir: parts/
# Split mode: size
# Total parts: 25
# Parts created:
#   part_01.txt: 100 lines, 645 words
#   part_02.txt: 100 lines, 678 words
#   ...
```

### 2. Split by Chapters

```bash
# Auto-detect and split chapters
python doc-splitter.py split book.txt \
  -o chapters/ \
  --mode chapter

# Detects patterns like:
# - "CHAPTER 1"
# - "Chapter 1:"
# - "# CHAPTER 1"
```

### 3. Preview Before Splitting

```bash
# Test split without creating files
python doc-splitter.py preview large_doc.txt \
  --lines 50

# Output:
# 📋 Split Preview
# Would create: 48 parts
# Part details:
# Part 1: Lines 1-50 (50 lines, 342 words)
# Part 2: Lines 51-100 (50 lines, 389 words)
```

---

## 📚 Commands

### Command: `split`

Split document into parts.

**Usage:**
```bash
python doc-splitter.py split <file> -o <output_dir> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output DIR` | Output directory (required) | - |
| `--mode MODE` | Split mode | size |
| `--lines N` | Lines per part (size mode) | 100 |
| `--words N` | Words per part (size mode) | - |
| `--chars N` | Characters per part (size mode) | - |
| `--max-size N` | Max size for smart mode | - |
| `--delimiter TEXT` | Delimiter for delimiter mode | - |
| `--pattern REGEX` | Regex pattern for delimiter mode | - |
| `--prefix TEXT` | Output file prefix | part |
| `--no-index` | Don't create index file | false |

**Split Modes:**
- `size` - Split by lines/words/characters
- `delimiter` - Split by custom delimiter
- `chapter` - Split by chapter markers
- `section` - Split by section headers
- `page` - Split by page markers
- `smart` - Intelligent splitting

**Examples:**

```bash
# Split by lines
python doc-splitter.py split document.txt -o parts/ --lines 100

# Split by words
python doc-splitter.py split document.txt -o parts/ --words 500

# Split by characters
python doc-splitter.py split document.txt -o parts/ --chars 5000

# Split by chapters
python doc-splitter.py split book.txt -o chapters/ --mode chapter

# Split by sections (markdown headers)
python doc-splitter.py split guide.md -o sections/ --mode section

# Split by custom delimiter
python doc-splitter.py split data.txt -o parts/ \
  --mode delimiter \
  --delimiter "---"

# Split by regex pattern
python doc-splitter.py split log.txt -o daily/ \
  --mode delimiter \
  --pattern "^\d{4}-\d{2}-\d{2}"

# Smart split (preserves context)
python doc-splitter.py split document.txt -o parts/ \
  --mode smart \
  --max-size 1000

# Custom prefix
python doc-splitter.py split report.txt -o parts/ \
  --lines 50 \
  --prefix report_section

# Skip index file
python doc-splitter.py split doc.txt -o parts/ --no-index
```

**Output Example:**
```
✅ Split completed successfully!
======================================================================
Input file: large_document.txt
Output dir: parts/
Split mode: size
Total parts: 25
Execution time: 0.23s

Parts created:
  part_01.txt: 100 lines, 645 words
  part_02.txt: 100 lines, 678 words
  part_03.txt: 100 lines, 623 words
  ... and 22 more
```

---

### Command: `preview`

Preview split without creating files.

**Usage:**
```bash
python doc-splitter.py preview <file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--mode MODE` | Split mode | size |
| `--lines N` | Lines per part | 100 |
| `--pattern REGEX` | Pattern for delimiter mode | - |

**Examples:**

```bash
# Preview line-based split
python doc-splitter.py preview large_doc.txt --lines 50

# Preview chapter split
python doc-splitter.py preview book.txt --mode chapter

# Preview section split
python doc-splitter.py preview guide.md --mode section

# Preview delimiter split
python doc-splitter.py preview data.txt \
  --mode delimiter \
  --pattern "^Section"
```

**Output Example:**
```
📋 Split Preview
======================================================================
File: large_document.txt
Mode: size
Would create: 48 parts

Part details:

Part 1:
  Lines: 1-50 (50 lines)
  Words: 342 | Chars: 2,145

Part 2:
  Lines: 51-100 (50 lines)
  Words: 389 | Chars: 2,456

Part 3:
  Lines: 101-150 (50 lines)
  Words: 367 | Chars: 2,301
  ...
```

---

## 💼 Use Cases

### Use Case 1: Split Large Log File

**Scenario:** Split multi-GB log file into daily files.

```bash
# Split by date pattern
python doc-splitter.py split application.log \
  -o daily_logs/ \
  --mode delimiter \
  --pattern "^\d{4}-\d{2}-\d{2}" \
  --prefix daily_log

# Result: One file per day
# daily_log_01.txt (2024-01-01)
# daily_log_02.txt (2024-01-02)
# ...
```

**Why it's useful:** Make large logs manageable and searchable.

---

### Use Case 2: Extract Book Chapters

**Scenario:** Split ebook into individual chapter files.

```bash
# Auto-detect chapters
python doc-splitter.py split ebook.txt \
  -o chapters/ \
  --mode chapter \
  --prefix chapter

# Review what was found
cat chapters/index.txt

# Result:
# chapter_01.txt: "CHAPTER 1: INTRODUCTION"
# chapter_02.txt: "CHAPTER 2: THE BEGINNING"
# ...
```

**Why it's useful:** Study or translate one chapter at a time.

---

### Use Case 3: Chunk Document for Processing

**Scenario:** Split large document to process in parallel.

```bash
# Split into processable chunks
python doc-splitter.py split large_corpus.txt \
  -o chunks/ \
  --mode smart \
  --max-size 5000

# Process chunks in parallel
for chunk in chunks/*.txt; do
  python doc-processor.py process "$chunk" &
done
wait

# Merge results
python doc-merger.py merge chunks/*.json -o final_results.json
```

**Why it's useful:** Parallel processing for speed.

---

## ❗ Troubleshooting

### Issue: "No chapters/sections detected"

**Symptom:**
```
WARNING: No chapter markers found, returning whole document
```

**Causes & Solutions:**

1. **Non-standard chapter format:**
   ```bash
   # Preview first to see content
   head -100 book.txt

   # Try different mode
   python doc-splitter.py split book.txt -o parts/ --mode section

   # Or use custom delimiter
   python doc-splitter.py split book.txt -o parts/ \
     --mode delimiter \
     --pattern "^Chapter \d+"
   ```

2. **Document needs preprocessing:**
   ```bash
   # Add chapter markers manually or via script
   sed -i 's/^Chapter \([0-9]\+\)/CHAPTER \1/g' book.txt

   # Then split
   python doc-splitter.py split book.txt -o chapters/ --mode chapter
   ```

---

### Issue: "Parts are too large or too small"

**Symptom:** Part sizes vary significantly

**Solutions:**

```bash
# Preview first to check sizes
python doc-splitter.py preview doc.txt --lines 100

# Adjust split size
python doc-splitter.py split doc.txt -o parts/ --lines 50  # Smaller

# Or use smart mode (balances sizes)
python doc-splitter.py split doc.txt -o parts/ \
  --mode smart \
  --max-size 1000
```

---

### Issue: "Split cuts in middle of paragraph"

**Symptom:** Context lost at split boundaries

**Solutions:**

```bash
# Use smart mode (preserves paragraphs)
python doc-splitter.py split doc.txt -o parts/ \
  --mode smart \
  --max-size 1000

# Smart mode:
# - Finds paragraph boundaries
# - Avoids mid-sentence splits
# - Preserves context
```

---

## 💡 Tips & Best Practices

### 1. Always Preview First

```bash
# Step 1: Preview
python doc-splitter.py preview large_doc.txt --lines 100

# Review:
# - Number of parts (too many/few?)
# - Part sizes (balanced?)
# - Split points (logical?)

# Step 2: Adjust if needed
python doc-splitter.py preview large_doc.txt --lines 200

# Step 3: Split
python doc-splitter.py split large_doc.txt -o parts/ --lines 200
```

### 2. Use Smart Mode for Clean Splits

```bash
# Size mode: Fast but may cut mid-paragraph
python doc-splitter.py split doc.txt -o parts/ --lines 100

# Smart mode: Slower but preserves context
python doc-splitter.py split doc.txt -o parts/ \
  --mode smart \
  --max-size 1000

# Use smart mode for:
# - Human-readable splits
# - Context-dependent processing
# - Quality over speed
```

### 3. Create Descriptive Output Directories

```bash
# Bad: Generic names
python doc-splitter.py split doc.txt -o parts/

# Good: Descriptive names
python doc-splitter.py split annual_report_2024.txt \
  -o annual_report_2024_sections/ \
  --mode section \
  --prefix section
```

### 4. Keep Index Files

```bash
# Index file contains:
# - Part metadata
# - Line ranges
# - Word/character counts
# - Checksums

# Don't skip index (helps with merging later)
python doc-splitter.py split doc.txt -o parts/

# Index helps with:
# - Verification (checksums)
# - Selective processing (line ranges)
# - Merging back (order, metadata)
```

### 5. Use Appropriate Mode for Content Type

```bash
# Logs: Delimiter with date pattern
python doc-splitter.py split app.log -o daily/ \
  --mode delimiter --pattern "^\d{4}-\d{2}-\d{2}"

# Books: Chapter mode
python doc-splitter.py split book.txt -o chapters/ --mode chapter

# Markdown docs: Section mode
python doc-splitter.py split guide.md -o sections/ --mode section

# General text: Smart mode
python doc-splitter.py split doc.txt -o parts/ \
  --mode smart --max-size 5000

# Structured data: Delimiter with custom pattern
python doc-splitter.py split data.txt -o parts/ \
  --mode delimiter --delimiter "###"
```

### 6. Batch Split Multiple Files

```bash
# Split all files in directory
for file in documents/*.txt; do
  basename=$(basename "$file" .txt)
  mkdir -p "split/${basename}_parts"

  python doc-splitter.py split "$file" \
    -o "split/${basename}_parts" \
    --lines 100 \
    --prefix "${basename}_part"
done

# Result: Each document split into its own directory
```

### 7. Combine with Merger for Round-Trip

```bash
# Split
python doc-splitter.py split original.txt -o parts/ --lines 50

# Process parts
for part in parts/*.txt; do
  python doc-processor.py process "$part"
done

# Merge back
python doc-merger.py merge parts/*.txt -o processed_complete.txt
```

---

## 🔄 Related Tools

- **doc-merger.py** - Merge split parts back (reverse operation)
- **doc-processor.py** - Process individual parts
- **doc-batch-processor.py** - Process all parts in parallel

---

## 📊 Performance

### Expected Split Times

| Input Size | Parts | Mode | Time |
|------------|-------|------|------|
| 1 MB | 10 | size | < 0.1s |
| 10 MB | 100 | size | < 0.5s |
| 100 MB | 1000 | size | < 3s |
| 100 MB | 50 | chapter | < 5s |
| 100 MB | 100 | smart | < 10s |

### Optimization Tips

```bash
# Fastest: Size mode
python doc-splitter.py split doc.txt -o parts/ --lines 100

# Slower but cleaner: Smart mode
python doc-splitter.py split doc.txt -o parts/ --mode smart

# For very large files:
# 1. Use size mode (fastest)
# 2. Skip index (--no-index)
# 3. Increase chunk size (fewer parts)
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
