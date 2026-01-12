# 🔧 CLI Auto-Completion Guide
## Tab Completion for All doc-* Tools

---

## 🎯 Overview

The CLI auto-completion system provides intelligent tab completion for all 11 doc-* command-line tools in the daten20 document management system.

### Features

- ✅ **Complete Coverage** - All 11 doc-* tools with full command support
- ✅ **Command-Specific Completions** - Each tool's commands and subcommands
- ✅ **Option Completions** - Intelligent suggestions for command options
- ✅ **File Path Completions** - Auto-complete file and directory paths
- ✅ **Both Bash and Zsh** - Support for the two most popular shells
- ✅ **Easy Installation** - Automated installation script with auto-detection
- ✅ **System-Wide or User-Level** - Flexible installation options

---

## 🚀 Quick Start

### Installation

**Install for both shells (recommended):**
```bash
./scripts/install-completion.sh both
```

**Install for specific shell:**
```bash
./scripts/install-completion.sh bash    # Bash only
./scripts/install-completion.sh zsh     # Zsh only
```

**Activate in current session:**
```bash
# Bash
source completions/doc-tools-completion.bash

# Zsh
source completions/doc-tools-completion.zsh
```

**Test installation:**
```bash
./scripts/install-completion.sh test
```

---

## 📋 Supported Tools

### 1. doc-processor.py
**Document processing, NER, classification**

```bash
doc-processor.py <TAB>
# Shows: process ner classify relations batch analyze

doc-processor.py process --<TAB>
# Shows: --output --format --lang --entities --sentiment --summary --help

doc-processor.py --format <TAB>
# Shows: txt html markdown json
```

**Commands:**
- `process` - Process a single document
- `ner` - Extract named entities
- `classify` - Classify document
- `relations` - Extract entity relations
- `batch` - Batch process multiple documents
- `analyze` - Full analysis

**Options:**
- `--output, -o` - Output file path (with file completion)
- `--format` - Output format: txt, html, markdown, json
- `--lang` - Language: en, de, fr, es, it
- `--entities` - Extract named entities
- `--sentiment` - Analyze sentiment
- `--summary` - Generate summary
- `--help, -h` - Show help message

---

### 2. doc-comparator.py
**Document comparison and similarity analysis**

```bash
doc-comparator.py <TAB>
# Shows: compare

doc-comparator.py compare --metric <TAB>
# Shows: cosine jaccard levenshtein all
```

**Commands:**
- `compare` - Compare two documents

**Options:**
- `--output, -o` - Output file path
- `--metric` - Similarity metric: cosine, jaccard, levenshtein, all
- `--report` - Report format: html, json, txt
- `--threshold` - Similarity threshold (0.0-1.0)
- `--entities-only` - Compare entities only
- `--ignore-case` - Case-insensitive comparison

---

### 3. doc-anonymizer.py
**PII detection and anonymization**

```bash
doc-anonymizer.py <TAB>
# Shows: scan anonymize deanonymize batch

doc-anonymizer.py anonymize --strategy <TAB>
# Shows: redaction masking replacement pseudonymization generalization
```

**Commands:**
- `scan` - Scan for PII without anonymizing
- `anonymize` - Anonymize PII in document
- `deanonymize` - Reverse anonymization
- `batch` - Batch process multiple documents

**Options:**
- `--output, -o` - Output file path
- `--strategy` - Anonymization strategy:
  - `redaction` - Remove PII completely
  - `masking` - Replace with asterisks
  - `replacement` - Replace with generic values
  - `pseudonymization` - Replace with consistent pseudonyms
  - `generalization` - Replace with broader categories
- `--pii-types` - PII types to anonymize: email, phone, name, location, date, all
- `--mapping-file` - Mapping file for reversible anonymization
- `--report` - Generate PII detection report

---

### 4. doc-quality.py
**Document quality assessment**

```bash
doc-quality.py <TAB>
# Shows: analyze batch

doc-quality.py analyze --dimensions <TAB>
# Shows: completeness accuracy consistency readability timeliness all
```

**Commands:**
- `analyze` - Analyze document quality
- `batch` - Batch analyze multiple documents

**Options:**
- `--output, -o` - Output file path
- `--format` - Report format: json, html, txt
- `--dimensions` - Quality dimensions to assess:
  - `completeness` - Word count, sections, metadata
  - `accuracy` - Email/phone/URL/date validation
  - `consistency` - Terminology, formatting
  - `readability` - Flesch score, sentence length
  - `timeliness` - Document age, reference freshness
  - `all` - All dimensions
- `--threshold` - Quality threshold (0-100)
- `--detailed` - Include detailed breakdown

---

### 5. doc-merger.py
**Merge multiple documents**

```bash
doc-merger.py <TAB>
# Shows: merge analyze

doc-merger.py merge --mode <TAB>
# Shows: sequential interleaved smart
```

**Commands:**
- `merge` - Merge multiple documents
- `analyze` - Analyze merge candidates

**Options:**
- `--output, -o` - Output file path
- `--mode` - Merge mode:
  - `sequential` - Concatenate in order
  - `interleaved` - Alternate sections
  - `smart` - Intelligent merge based on structure
- `--toc` - Generate table of contents
- `--preserve-formatting` - Keep original formatting
- `--add-separators` - Add section separators

---

### 6. doc-splitter.py
**Split documents into parts**

```bash
doc-splitter.py <TAB>
# Shows: split preview

doc-splitter.py split --mode <TAB>
# Shows: pages sections size chunks
```

**Commands:**
- `split` - Split document
- `preview` - Preview split result

**Options:**
- `--output-dir, -o` - Output directory
- `--mode` - Split mode:
  - `pages` - Split by page count
  - `sections` - Split by sections/headings
  - `size` - Split by file size
  - `chunks` - Split into N equal chunks
- `--pages-per-file` - Pages per output file
- `--max-size` - Maximum file size
- `--num-chunks` - Number of chunks

---

### 7. doc-search.py
**Semantic and full-text search**

```bash
doc-search.py <TAB>
# Shows: search index

doc-search.py search --type <TAB>
# Shows: semantic fulltext hybrid
```

**Commands:**
- `search` - Search documents
- `index` - Build search index

**Options:**
- `--query, -q` - Search query
- `--type` - Search type: semantic, fulltext, hybrid
- `--limit` - Maximum results
- `--min-score` - Minimum similarity score
- `--output, -o` - Output file path

---

### 8. doc-batch-processor.py
**Batch process multiple documents**

```bash
doc-batch-processor.py <TAB>
# Shows: process status cancel

doc-batch-processor.py process --<TAB>
# Shows: --input-dir --output-dir --operation --workers --recursive
```

**Commands:**
- `process` - Start batch processing
- `status` - Check processing status
- `cancel` - Cancel batch job

**Options:**
- `--input-dir, -i` - Input directory
- `--output-dir, -o` - Output directory
- `--operation` - Operation: process, anonymize, quality, compare
- `--workers` - Number of parallel workers
- `--recursive` - Process subdirectories

---

### 9. doc-master.py
**Master orchestrator**

```bash
doc-master.py <TAB>
# Shows: status services health pipeline quick-process
```

**Commands:**
- `status` - Show system status
- `services` - Manage services (start, stop, restart)
- `health` - Health check
- `pipeline` - Run processing pipeline
- `quick-process` - Quick document processing

**Options:**
- `--verbose, -v` - Verbose output
- `--json` - JSON output format

---

### 10. doc-dashboard.py
**Web dashboard server**

```bash
doc-dashboard.py <TAB>
# Shows: start stop restart status
```

**Commands:**
- `start` - Start dashboard server
- `stop` - Stop dashboard server
- `restart` - Restart dashboard server
- `status` - Check server status

**Options:**
- `--host` - Server host (default: 0.0.0.0)
- `--port` - Server port (default: 8501)
- `--debug` - Enable debug mode

---

### 11. doc-api-server.py
**REST API server**

```bash
doc-api-server.py <TAB>
# Shows: start stop restart status
```

**Commands:**
- `start` - Start API server
- `stop` - Stop API server
- `restart` - Restart API server
- `status` - Check server status

**Options:**
- `--host` - Server host (default: 0.0.0.0)
- `--port` - Server port (default: 8000)
- `--reload` - Auto-reload on code changes
- `--workers` - Number of worker processes

---

## 🔧 Installation Details

### Automatic Installation

The `install-completion.sh` script provides:

1. **Shell Detection** - Automatically detects your current shell
2. **System-Wide Installation** - Installs to `/etc/bash_completion.d/` or `/usr/share/zsh/site-functions/`
3. **User-Level Fallback** - Falls back to `~/.bash_completion.d/` or `~/.zsh/completion/`
4. **Config Updates** - Automatically updates `.bashrc` or `.zshrc`
5. **Colored Output** - Clear status indicators and progress

### Manual Installation

**Bash:**
```bash
# Copy completion file
sudo cp completions/doc-tools-completion.bash /etc/bash_completion.d/doc-tools

# Or for user-level:
mkdir -p ~/.bash_completion.d
cp completions/doc-tools-completion.bash ~/.bash_completion.d/doc-tools

# Add to ~/.bashrc:
echo "source ~/.bash_completion.d/doc-tools" >> ~/.bashrc

# Reload
source ~/.bashrc
```

**Zsh:**
```bash
# Copy completion file
sudo cp completions/doc-tools-completion.zsh /usr/share/zsh/site-functions/_doc-tools

# Or for user-level:
mkdir -p ~/.zsh/completion
cp completions/doc-tools-completion.zsh ~/.zsh/completion/_doc-tools

# Add to ~/.zshrc:
echo 'fpath=(~/.zsh/completion $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc

# Reload
source ~/.zshrc
```

---

## 🧪 Testing Completion

### Test Commands

```bash
# Test tool completion
doc-<TAB><TAB>
# Should list all doc-* tools

# Test command completion
doc-processor.py <TAB>
# Should show: process ner classify relations batch analyze

# Test option completion
doc-processor.py process --<TAB>
# Should show all options

# Test value completion
doc-processor.py --format <TAB>
# Should show: txt html markdown json

# Test file completion
doc-processor.py process --output <TAB>
# Should show files in current directory
```

### Troubleshooting

**Completion not working?**

1. **Check installation:**
   ```bash
   ./scripts/install-completion.sh test
   ```

2. **Reload shell config:**
   ```bash
   # Bash
   source ~/.bashrc

   # Zsh
   source ~/.zshrc
   ```

3. **Check if completion is loaded:**
   ```bash
   # Bash
   complete -p | grep doc-

   # Zsh
   which _doc-processor.py
   ```

4. **Manual load:**
   ```bash
   # Bash
   source completions/doc-tools-completion.bash

   # Zsh
   source completions/doc-tools-completion.zsh
   ```

---

## 💡 Usage Examples

### Example 1: Process Document with Format

```bash
# Type:
doc-processor.py process document.txt --format <TAB>

# Completion suggests:
txt html markdown json

# Select:
doc-processor.py process document.txt --format html
```

### Example 2: Anonymize with Strategy

```bash
# Type:
doc-anonymizer.py anonymize sensitive.txt --strategy <TAB>

# Completion suggests:
redaction masking replacement pseudonymization generalization

# Select:
doc-anonymizer.py anonymize sensitive.txt --strategy pseudonymization
```

### Example 3: Compare Documents with Metric

```bash
# Type:
doc-comparator.py compare doc1.txt doc2.txt --metric <TAB>

# Completion suggests:
cosine jaccard levenshtein all

# Select:
doc-comparator.py compare doc1.txt doc2.txt --metric cosine
```

### Example 4: Quality Analysis with Dimensions

```bash
# Type:
doc-quality.py analyze report.pdf --dimensions <TAB>

# Completion suggests:
completeness accuracy consistency readability timeliness all

# Select:
doc-quality.py analyze report.pdf --dimensions completeness accuracy
```

---

## 🎨 Completion Features

### Intelligent File Completion

The completion system provides intelligent file path suggestions:

- Input file parameters complete with existing files
- Output file parameters complete with directory paths
- Directory parameters show only directories
- Respects relative and absolute paths

### Context-Aware Suggestions

Completions adapt based on context:

- After `--format`, only shows valid format options
- After `--lang`, only shows supported languages
- After `--metric`, only shows available metrics
- After `--strategy`, only shows anonymization strategies

### Command-Specific Options

Each command gets its own relevant options:

- `doc-processor.py process` shows processing options
- `doc-processor.py ner` shows NER-specific options
- `doc-anonymizer.py anonymize` shows anonymization options
- Options irrelevant to the command are not shown

---

## 🔄 Uninstallation

To remove the completion system:

```bash
./scripts/install-completion.sh uninstall
```

This removes:
- System-wide completion files
- User-level completion files

**Note:** You'll need to manually remove the source lines from `~/.bashrc` or `~/.zshrc`:

```bash
# Remove these lines from ~/.bashrc or ~/.zshrc:
# Doc-tools completion
source ~/.bash_completion.d/doc-tools
```

---

## 📊 Completion Statistics

- **Tools Covered**: 11
- **Total Commands**: 30+
- **Total Options**: 80+
- **File Types Supported**: All text formats
- **Shells Supported**: Bash, Zsh

---

## 🚀 Advanced Usage

### Custom Completion Functions

The completion files define custom functions for each tool:

```bash
# Bash
_doc_processor
_doc_comparator
_doc_anonymizer
_doc_quality
_doc_merger
_doc_splitter
_doc_search
_doc_batch_processor
_doc_master
_doc_dashboard
_doc_api_server

# Zsh
_doc-processor.py
_doc-comparator.py
_doc-anonymizer.py
# ... etc
```

### Helper Functions

**Bash:**
- `_doc_tools_help` - Get completion help

**Usage:**
```bash
doc-completion-help
# Shows quick usage guide
```

---

## 🎯 Best Practices

1. **Use TAB frequently** - Discover available commands and options
2. **Press TAB twice** - See all available completions
3. **Use partial matching** - Type first letters and press TAB
4. **Check help** - Use `--help` option to learn about commands
5. **Test before production** - Use `--help` and `--dry-run` flags

---

## 📚 Related Documentation

- [Project README](../README.md) - Main project documentation
- [Setup Guide](../README.md#installation) - Installation instructions
- [User Guide](USER_GUIDE.md) - Comprehensive usage guide
- [API Documentation](API_REFERENCE.md) - API reference

---

## 🐛 Troubleshooting

### Issue: Completion shows "command not found"

**Solution:**
```bash
# Check if tools are in PATH
which doc-processor.py

# If not, add to PATH in ~/.bashrc or ~/.zshrc:
export PATH="$PATH:/home/user/daten20"
```

### Issue: Old completions cached

**Solution:**
```bash
# Bash - clear completion cache
complete -r

# Zsh - rebuild completion cache
rm -f ~/.zcompdump*
compinit
```

### Issue: Completion too slow

**Solution:**
The completion system is designed to be fast, but if you experience slowness:

1. Use Zsh instead of Bash (generally faster completions)
2. Reduce number of files in current directory
3. Use absolute paths instead of relative paths

---

## 🎉 Summary

The CLI auto-completion system provides:

✅ **Productivity** - Faster command-line usage
✅ **Discoverability** - Learn commands and options through TAB
✅ **Accuracy** - Reduce typos and errors
✅ **Professional** - Polished command-line experience
✅ **Easy to Use** - Simple installation and usage
✅ **Well Documented** - Comprehensive guide and examples

---

**Version:** 1.0
**Date:** 2026-01-12
**Status:** ✅ Production-Ready
**Task:** Task 24 - CLI Auto-Completion
