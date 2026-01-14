# 📊 Doc-Dashboard User Guide

**Version:** 1.0.0
**Type:** Web Application
**Purpose:** Interactive web dashboard for document analysis and visualization

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [Use Cases](#use-cases)
5. [Troubleshooting](#troubleshooting)
6. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Overview

**doc-dashboard.py** provides an interactive web interface for document upload, analysis, and visualization with real-time processing.

### Key Features

- ✅ **Drag & Drop Upload** - Easy document upload interface
- ✅ **Real-Time Processing** - See results as documents process
- ✅ **Interactive Visualizations** - Charts for entities, topics, classification
- ✅ **Knowledge Graph Viewer** - Interactive D3.js graph visualization
- ✅ **RESTful API** - Backend API for integrations
- ✅ **No Database Required** - Stateless processing

### Tech Stack

- **Backend:** Flask, Python
- **Frontend:** Bootstrap 5, JavaScript
- **Visualization:** Chart.js, D3.js
- **Supported:** PDF, DOCX, TXT (Max 50MB)

---

## ⚡ Quick Start

### 1. Start Dashboard Server

```bash
# Start on default port (5000)
python doc-dashboard.py

# Output:
# ╔════════════════════════════════════════════════════════════════╗
# ║        Document Analysis Dashboard v1.0.0                      ║
# ╠════════════════════════════════════════════════════════════════╣
# ║  📊 Interactive document analysis and visualization            ║
# ║  🕸️  Knowledge graph explorer                                  ║
# ╠════════════════════════════════════════════════════════════════╣
# ║  Server: http://127.0.0.1:5000
# ║  Mode: Development
# ╚════════════════════════════════════════════════════════════════╝
#
# * Running on http://127.0.0.1:5000
```

### 2. Access Dashboard

```bash
# Open browser and navigate to:
http://localhost:5000

# Or use curl to test:
curl http://localhost:5000/api/v1/health
```

### 3. Upload and Analyze

1. Open dashboard in browser
2. Drag document to upload area
3. Wait for processing (progress indicator shown)
4. View results:
   - Entity extraction
   - Document classification
   - Relations found
   - Knowledge graph

---

## 📚 Features

### Dashboard Interface

The dashboard provides several interactive sections:

#### Statistics Cards

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total Documents │ Entities        │ Relations Found │ Processing Time │
│      1          │     45          │      12         │     2.3s        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

#### Upload Section

```
╔════════════════════════════════════════════════════════════════════╗
║                     📤 Upload Document                             ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║              Click or drag document here to upload                 ║
║              Supported: PDF, TXT, DOCX (Max 50MB)                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

#### Extracted Entities Panel

Shows entities grouped by type:

```
🏷️ Extracted Entities

PERSON
[Max Mustermann (95%)] [Jane Doe (92%)]

ORGANIZATION
[Acme Corp (88%)] [TechStart GmbH (85%)]

LOCATION
[Berlin (90%)] [Hamburg (87%)]
```

#### Relations Panel

Shows extracted relationships:

```
🔗 Relations

[Max Mustermann] → WORKS_AT → [Acme Corp] (85%)
[Jane Doe] → LOCATED_IN → [Berlin] (90%)
```

#### Classification Chart

Doughnut chart showing classification confidence:

```
📂 Document Classification

Category: LEGAL
Confidence: 87%

[Pie chart showing 87% confident, 13% uncertain]
```

#### Knowledge Graph

Interactive force-directed graph:

```
🕸️ Knowledge Graph

[Interactive D3.js visualization showing:]
- Nodes: Entities (color-coded by type)
- Edges: Relations (labeled)
- Draggable nodes
- Zoom/pan support
```

---

## 💼 Use Cases

### Use Case 1: Quick Document Analysis

**Scenario:** Quickly analyze a contract without CLI.

```bash
# 1. Start dashboard
python doc-dashboard.py

# 2. Open browser: http://localhost:5000

# 3. Upload contract.pdf via drag & drop

# 4. View results:
#    - Extracted parties (persons, organizations)
#    - Contract type (classification)
#    - Relationships between parties
#    - Visual knowledge graph

# 5. Export results (copy JSON from API)
```

**Why it's useful:** Non-technical users can analyze documents.

---

### Use Case 2: Presentation/Demo

**Scenario:** Demonstrate document intelligence to stakeholders.

```bash
# Start dashboard for presentation
python doc-dashboard.py --host 0.0.0.0 --port 80

# Share URL with stakeholders
# They can upload their own documents
# See real-time analysis

# Features to highlight:
# - Real-time entity extraction
# - Automatic classification
# - Interactive knowledge graph
# - Professional visualizations
```

**Why it's useful:** Interactive demos more engaging than static reports.

---

### Use Case 3: Rapid Prototyping

**Scenario:** Test document processing on various documents.

```bash
# Start dashboard
python doc-dashboard.py --debug

# Test different documents:
# 1. Upload legal contract → Check if classified as LEGAL
# 2. Upload medical record → Check PII detection
# 3. Upload financial report → Check entity extraction

# Iterate and refine ML models based on results
```

**Why it's useful:** Visual feedback speeds up development.

---

## 🌐 API Endpoints

### POST /api/v1/documents

Upload and process document.

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/documents \
  -F "file=@document.pdf"

# Response:
{
  "document_id": "abc123",
  "filename": "document.pdf",
  "processed_at": "2026-01-14T10:30:00Z",
  "statistics": {
    "text_length": 5234,
    "word_count": 856,
    "entity_count": 23,
    "relation_count": 7
  },
  "classification": {
    "category": "LEGAL",
    "confidence": 0.87
  },
  "entities": [...],
  "relations": [...]
}
```

### GET /api/v1/health

Health check endpoint.

**Example:**
```bash
curl http://localhost:5000/api/v1/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "parser": "operational",
    "ner": "operational",
    "classifier": "operational"
  }
}
```

### GET /api/v1/stats

Get statistics.

**Example:**
```bash
curl http://localhost:5000/api/v1/stats

# Response:
{
  "total_documents": 0,
  "total_entities": 0,
  "total_relations": 0
}
```

---

## ❗ Troubleshooting

### Issue: "Dashboard not accessible"

**Error:** Browser shows "Connection refused"

**Solutions:**

```bash
# 1. Check if server is running
ps aux | grep doc-dashboard

# 2. Check if port is available
lsof -i :5000

# 3. Try different port
python doc-dashboard.py --port 8080

# 4. Allow external access
python doc-dashboard.py --host 0.0.0.0
```

---

### Issue: "File upload fails"

**Error:** "Failed to process document"

**Causes & Solutions:**

1. **File too large (> 50MB):**
   ```bash
   # Increase size limit in code or split file first
   python doc-splitter.py split large.pdf -o parts/
   # Upload parts individually
   ```

2. **Unsupported format:**
   ```bash
   # Convert to supported format first
   # Supported: PDF, TXT, DOCX
   ```

3. **Corrupted file:**
   ```bash
   # Verify file integrity
   file document.pdf
   ```

---

### Issue: "Knowledge graph not displaying"

**Symptom:** Graph section is empty

**Solutions:**

1. **Enable graph in upload:**
   - Dashboard builds graph by default
   - Check browser console for errors (F12)

2. **Document has no relations:**
   - Graph only shows if relations found
   - Try document with clear relationships

3. **Browser compatibility:**
   - Use modern browser (Chrome, Firefox, Edge)
   - D3.js requires JavaScript enabled

---

## 💡 Tips & Best Practices

### 1. Run in Development Mode for Testing

```bash
# Development mode (auto-reload on code changes)
python doc-dashboard.py --debug

# Production mode (stable, no auto-reload)
python doc-dashboard.py --production
```

### 2. Secure Production Deployments

```bash
# Don't expose dashboard publicly without authentication!

# For production:
# 1. Use reverse proxy (nginx)
# 2. Add authentication (API keys, OAuth)
# 3. Use HTTPS
# 4. Restrict access by IP

# Example with nginx:
# location /dashboard/ {
#     proxy_pass http://localhost:5000/;
#     allow 10.0.0.0/8;
#     deny all;
# }
```

### 3. Use Custom Port for Multiple Instances

```bash
# Run multiple dashboards on different ports
python doc-dashboard.py --port 5001  # Instance 1
python doc-dashboard.py --port 5002  # Instance 2
python doc-dashboard.py --port 5003  # Instance 3

# Useful for:
# - Testing different configurations
# - Team members with separate instances
# - A/B testing different models
```

### 4. Integrate with Other Services

```bash
# Dashboard provides REST API
# Integrate with other tools:

# Example: Upload via script
curl -X POST http://localhost:5000/api/v1/documents \
  -F "file=@document.pdf" \
  > results.json

# Parse results
cat results.json | jq '.entities[] | select(.type=="PERSON")'
```

### 5. Monitor Performance

```bash
# Check dashboard logs
python doc-dashboard.py 2>&1 | tee dashboard.log

# Monitor requests
tail -f dashboard.log | grep "POST /api"

# Monitor system resources
htop  # Watch memory/CPU usage
```

### 6. Clear Browser Cache for Updates

```bash
# After updating dashboard code:
# 1. Stop server (Ctrl+C)
# 2. Clear browser cache (Ctrl+Shift+Delete)
# 3. Restart server
python doc-dashboard.py

# Or use hard refresh: Ctrl+Shift+R
```

---

## 🚀 Command-Line Options

### All Options

```bash
python doc-dashboard.py [options]

Options:
  --host HOST          Host address (default: 127.0.0.1)
  --port PORT          Port number (default: 5000)
  --production         Run in production mode
  --debug              Enable debug mode (auto-reload)
```

### Examples

```bash
# Default (localhost only)
python doc-dashboard.py

# Allow external access
python doc-dashboard.py --host 0.0.0.0

# Custom port
python doc-dashboard.py --port 8080

# Production mode
python doc-dashboard.py --production --host 0.0.0.0 --port 80

# Development with debug
python doc-dashboard.py --debug
```

---

## 🔄 Related Tools

- **doc-api-server.py** - FastAPI server for production
- **doc-processor.py** - CLI equivalent
- **doc-batch-processor.py** - Batch processing

---

## 📊 Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully supported |
| Firefox | 88+ | ✅ Fully supported |
| Safari | 14+ | ✅ Fully supported |
| Edge | 90+ | ✅ Fully supported |
| IE 11 | - | ❌ Not supported |

---

## 🔒 Security Notes

**IMPORTANT:** The dashboard is intended for local/internal use.

### Security Considerations

```bash
# ⚠️  DO NOT expose to internet without:
# 1. Authentication
# 2. Rate limiting
# 3. Input validation
# 4. HTTPS
# 5. Firewall rules

# For internal network only:
python doc-dashboard.py --host 0.0.0.0

# Behind reverse proxy with auth:
python doc-dashboard.py --host 127.0.0.1
# (Nginx handles external access + auth)
```

---

**Last Updated:** 2026-01-14
**Version:** 1.0.0
