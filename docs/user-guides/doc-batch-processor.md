# ⚡ Doc-Batch-Processor User Guide

**Version:** 1.0.0
**Type:** Command-Line Interface (CLI)
**Purpose:** High-performance parallel document processing at scale

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

**doc-batch-processor.py** processes hundreds or thousands of documents in parallel with progress tracking, error handling, and resume capability.

### Key Features

- ✅ **Parallel Processing** - Multi-threaded/multi-process execution
- ✅ **Progress Tracking** - Real-time progress bar with statistics
- ✅ **Resume Capability** - Resume interrupted jobs
- ✅ **Error Handling** - Continue processing despite errors
- ✅ **Custom Pipelines** - NER, classification, relations, graphs
- ✅ **Checkpoint System** - Save state every 10 documents

### Processing Pipeline

| Step | Description | Output |
|------|-------------|--------|
| **ner** | Named entity recognition | Entities list |
| **classify** | Document classification | Category + confidence |
| **relations** | Relation extraction | Relations list |
| **graph** | Knowledge graph | Graph structure |

---

## ⚡ Quick Start

### 1. Process Directory (Basic)

```bash
# Process all documents with default pipeline
python doc-batch-processor.py process /documents/

# Output:
# Processing documents: 100%|████████████| 150/150 [01:23<00:00, 1.8doc/s]
# Processed: 148, Failed: 2, Entities: 3,452, Relations: 892
#
# ✅ Batch job completed: 148 processed, 2 failed
```

### 2. Custom Pipeline with Parallel Workers

```bash
# Process with 8 parallel workers
python doc-batch-processor.py process /documents/ \
  --pipeline ner,classify,relations \
  --workers 8 \
  --output results/

# Processes 8 documents simultaneously
# Speeds up large batches significantly
```

### 3. Resume Interrupted Job

```bash
# If processing was interrupted (Ctrl+C, crash, etc.)
python doc-batch-processor.py resume batch_20260114_103000_abc123

# Continues from where it left off
# Uses saved checkpoint
```

---

## 📚 Commands

### Command: `process`

Process all documents in a directory.

**Usage:**
```bash
python doc-batch-processor.py process <input_dir> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output-dir DIR` | Output directory | data/batch_results |
| `-p, --pipeline STEPS` | Pipeline steps (comma-separated) | ner,classify,relations |
| `-w, --workers N` | Number of parallel workers | 4 |
| `--multiprocess` | Use multiprocessing (not threading) | false |
| `--pattern PATTERN` | File pattern to match | *.* |

**Pipeline Steps:**
- `ner` - Named entity recognition
- `classify` - Document classification
- `relations` - Relation extraction
- `graph` - Knowledge graph construction

**Examples:**

```bash
# Basic processing (default pipeline)
python doc-batch-processor.py process /documents/

# Full pipeline with graph
python doc-batch-processor.py process /documents/ \
  --pipeline ner,classify,relations,graph \
  --output results/

# Fast processing (8 workers)
python doc-batch-processor.py process /documents/ \
  --workers 8 \
  --output results/

# Multiprocessing (for CPU-intensive tasks)
python doc-batch-processor.py process /documents/ \
  --multiprocess \
  --workers 4

# Specific file pattern
python doc-batch-processor.py process /documents/ \
  --pattern "*.pdf" \
  --output pdf_results/

# Minimal pipeline (fastest)
python doc-batch-processor.py process /documents/ \
  --pipeline ner \
  --workers 8
```

**Output Example:**
```
Processing documents: 100%|██████████████████| 150/150 [01:23<00:00, 1.8doc/s]
Processed: 148, Failed: 2, Entities: 3,452, Relations: 892

✅ Batch job completed: 148 processed, 2 failed

Job Summary:
{
  "job_id": "batch_20260114_103000_abc123",
  "status": "completed",
  "statistics": {
    "total_files": 150,
    "processed": 148,
    "failed": 2,
    "success_rate": "98.7%",
    "total_entities": 3452,
    "total_relations": 892
  },
  "timing": {
    "elapsed_seconds": 83.5,
    "elapsed_formatted": "1.4m",
    "avg_per_document": 0.56
  }
}
```

---

### Command: `resume`

Resume interrupted batch job.

**Usage:**
```bash
python doc-batch-processor.py resume <job_id> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output-dir DIR` | Output directory | data/batch_results |

**Examples:**

```bash
# Resume job
python doc-batch-processor.py resume batch_20260114_103000_abc123

# Output:
# ℹ️  Resuming job batch_20260114_103000_abc123
# ℹ️  Already processed: 85/150
# ℹ️  Remaining: 65 documents
#
# Processing documents: 100%|████████| 65/65 [00:42<00:00, 1.5doc/s]
```

---

### Command: `status`

Check status of batch job.

**Usage:**
```bash
python doc-batch-processor.py status <job_id> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output-dir DIR` | Output directory | data/batch_results |

**Examples:**

```bash
# Get job status
python doc-batch-processor.py status batch_20260114_103000_abc123

# Output:
# Job Status:
# {
#   "job_id": "batch_20260114_103000_abc123",
#   "status": "completed",
#   "statistics": {
#     "total_files": 150,
#     "processed": 148,
#     "failed": 2,
#     "success_rate": "98.7%"
#   }
# }
```

---

### Command: `report`

Generate batch processing report.

**Usage:**
```bash
python doc-batch-processor.py report <job_id> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output-dir DIR` | Output directory | data/batch_results |
| `--format FORMAT` | Report format (excel, json, csv) | excel |

**Examples:**

```bash
# Generate Excel report
python doc-batch-processor.py report batch_20260114_103000_abc123 \
  --format excel

# Generate JSON report
python doc-batch-processor.py report batch_20260114_103000_abc123 \
  --format json
```

---

## 💼 Use Cases

### Use Case 1: Process Large Document Repository

**Scenario:** Process 10,000 documents overnight.

```bash
# Start batch processing
nohup python doc-batch-processor.py process /repository/ \
  --pipeline ner,classify,relations \
  --workers 16 \
  --output /results/ \
  > batch.log 2>&1 &

# Check progress
tail -f batch.log

# If interrupted, resume
python doc-batch-processor.py resume batch_20260114_103000_abc123

# Generate report when complete
python doc-batch-processor.py report batch_20260114_103000_abc123 \
  --format excel \
  --output batch_report.xlsx
```

**Why it's useful:** Automated large-scale document processing.

---

### Use Case 2: Monthly Archive Processing

**Scenario:** Process monthly document archives systematically.

```bash
#!/bin/bash
# monthly_batch.sh

MONTH="2024-01"
INPUT_DIR="/archives/${MONTH}/"
OUTPUT_DIR="/processed/${MONTH}/"

# Process
python doc-batch-processor.py process "$INPUT_DIR" \
  --output-dir "$OUTPUT_DIR" \
  --pipeline ner,classify,relations \
  --workers 8

# Generate report
JOB_ID=$(ls -t "$OUTPUT_DIR"/*_checkpoint.pkl | head -1 | \
         grep -oP 'batch_\d+_\d+_[a-f0-9]+')

python doc-batch-processor.py report "$JOB_ID" \
  --output-dir "$OUTPUT_DIR" \
  --format excel

echo "Monthly processing complete: $MONTH"
```

**Why it's useful:** Automated monthly processing workflow.

---

### Use Case 3: Incremental Processing

**Scenario:** Process only new documents daily.

```bash
#!/bin/bash
# daily_incremental.sh

# Find documents added today
TODAY=$(date +%Y-%m-%d)
find /documents/ -type f -newermt "$TODAY" > today_files.txt

# Process only today's files
mkdir -p daily_results/${TODAY}/
while read file; do
  cp "$file" "daily_results/${TODAY}/"
done < today_files.txt

python doc-batch-processor.py process "daily_results/${TODAY}/" \
  --output-dir "daily_results/${TODAY}_processed/" \
  --workers 4

echo "Processed $(wc -l < today_files.txt) new documents"
```

**Why it's useful:** Efficient incremental processing.

---

## ❗ Troubleshooting

### Issue: "Out of memory"

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

```bash
# 1. Reduce workers
python doc-batch-processor.py process /documents/ \
  --workers 2  # Down from 4+

# 2. Use threading instead of multiprocessing
python doc-batch-processor.py process /documents/ \
  --workers 4
# (Default uses threading, which shares memory)

# 3. Process in smaller batches
for dir in /documents/batch_*; do
  python doc-batch-processor.py process "$dir" \
    --workers 2
done
```

---

### Issue: "Processing is slow"

**Symptom:** < 1 doc/second throughput

**Causes & Solutions:**

1. **Too few workers:**
   ```bash
   # Increase workers (up to CPU cores)
   python doc-batch-processor.py process /documents/ \
     --workers 8
   ```

2. **I/O bottleneck:**
   ```bash
   # Use multiprocessing for CPU-bound tasks
   python doc-batch-processor.py process /documents/ \
     --multiprocess \
     --workers 4
   ```

3. **Heavy pipeline:**
   ```bash
   # Reduce pipeline steps
   python doc-batch-processor.py process /documents/ \
     --pipeline ner,classify  # Skip relations,graph
   ```

---

### Issue: "Cannot resume job"

**Error:**
```
ERROR: Job batch_xxx not found
```

**Solutions:**

```bash
# Check checkpoint file exists
ls data/batch_results/batch_*_checkpoint.pkl

# Ensure correct output directory
python doc-batch-processor.py resume JOB_ID \
  --output-dir /correct/path/

# If checkpoint corrupted, restart
python doc-batch-processor.py process /documents/
```

---

## 💡 Tips & Best Practices

### 1. Choose Appropriate Worker Count

```bash
# CPU cores: Get with `nproc` or `lscpu`
CORES=$(nproc)

# General guideline:
# Threading: workers = cores * 2 (I/O-bound)
# Multiprocessing: workers = cores (CPU-bound)

# For most document processing (I/O-bound):
python doc-batch-processor.py process /documents/ \
  --workers $((CORES * 2))

# For heavy ML processing (CPU-bound):
python doc-batch-processor.py process /documents/ \
  --multiprocess \
  --workers $CORES
```

### 2. Use Minimal Pipeline for Speed

```bash
# Full pipeline (slowest, most features)
python doc-batch-processor.py process /documents/ \
  --pipeline ner,classify,relations,graph

# Recommended (balanced)
python doc-batch-processor.py process /documents/ \
  --pipeline ner,classify,relations

# Fastest (minimal)
python doc-batch-processor.py process /documents/ \
  --pipeline ner
```

### 3. Monitor Progress

```bash
# Run in background with logging
nohup python doc-batch-processor.py process /documents/ \
  --workers 8 \
  > batch.log 2>&1 &

# Monitor in real-time
tail -f batch.log

# Check job status
python doc-batch-processor.py status JOB_ID
```

### 4. Organize Output by Date

```bash
# Use date-based output directories
TODAY=$(date +%Y%m%d)
python doc-batch-processor.py process /documents/ \
  --output-dir results/${TODAY}/

# Easy to find recent results
ls -lt results/
```

### 5. Always Enable Checkpoints (Default)

```bash
# Checkpoints are automatic (every 10 documents)
# This allows resuming if interrupted

# After interruption:
python doc-batch-processor.py resume JOB_ID

# Checkpoints stored in output directory:
# batch_JOB_ID_checkpoint.pkl
```

### 6. Handle Failed Documents

```bash
# Process completes even with errors
# Check summary for failed count

# Review failed documents
python doc-batch-processor.py report JOB_ID \
  --format json | jq '.errors[]'

# Reprocess failed documents
# Extract failed file paths and reprocess
```

### 7. Resource-Aware Processing

```bash
# Monitor system resources
htop  # or top

# If system under heavy load:
# 1. Reduce workers
# 2. Process during off-hours
# 3. Use nice for lower priority:
nice -n 10 python doc-batch-processor.py process /documents/
```

---

## 📊 Performance Benchmarks

### Throughput by Pipeline

| Pipeline | Workers | Throughput | Use Case |
|----------|---------|------------|----------|
| ner | 8 | 5-8 doc/s | Fast extraction |
| ner,classify | 8 | 3-5 doc/s | Standard |
| ner,classify,relations | 8 | 2-3 doc/s | Complete |
| ner,classify,relations,graph | 4 | 0.5-1 doc/s | Full analysis |

### System Requirements

```bash
# Recommended:
# - CPU: 4+ cores
# - RAM: 8+ GB
# - Storage: SSD for fast I/O

# Minimum:
# - CPU: 2 cores
# - RAM: 4 GB
# - Use fewer workers (--workers 2)
```

---

## 🔄 Related Tools

- **doc-processor.py** - Single document processing
- **doc-dashboard.py** - Web UI for monitoring
- **doc-api-server.py** - REST API for batch processing

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
