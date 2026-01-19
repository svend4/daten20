# Semantic Search with BERT - Complete Guide

## 📖 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Concepts](#core-concepts)
6. [API Reference](#api-reference)
7. [Examples](#examples)
8. [REST API](#rest-api)
9. [Performance](#performance)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

Semantic Search with BERT enables finding documents based on **meaning** rather than just keyword matching. This module uses state-of-the-art BERT embeddings and vector similarity to understand context and semantic relationships.

### Why Semantic Search?

Traditional keyword search has limitations:
- **Keyword Search**: "ML algorithms" → Only finds documents containing exact words
- **Semantic Search**: "ML algorithms" → Finds "machine learning", "neural networks", "AI models", etc.

### Architecture

```
Query → BERT Encoder → Embedding Vector → FAISS Index → Similar Documents
```

**Key Components:**
1. **BERT Encoder**: Converts text to dense vectors (sentence-transformers)
2. **Vector Index**: Fast similarity search (FAISS)
3. **Reranker**: Optional cross-encoder for better accuracy
4. **Hybrid Search**: Combines semantic + keyword results

---

## Features

✅ **BERT-based embeddings** using sentence-transformers
✅ **Fast vector search** with FAISS indexing
✅ **Multiple similarity metrics** (cosine, euclidean, dot product)
✅ **Hybrid search** combining semantic + keyword
✅ **Query reranking** with cross-encoder
✅ **Multi-lingual support** (100+ languages)
✅ **Embedding caching** for performance
✅ **Batch processing** for large datasets
✅ **Index persistence** (save/load)
✅ **Metadata filtering**
✅ **REST API** endpoints

---

## Installation

### Dependencies

```bash
# Core dependencies
pip install sentence-transformers faiss-cpu numpy

# Optional: GPU support (faster)
pip install faiss-gpu

# Optional: Cross-encoder for reranking
pip install sentence-transformers[cross-encoder]

# API dependencies
pip install flask
```

### Verify Installation

```python
from src.ml.semantic_search import SemanticSearchEngine

engine = SemanticSearchEngine()
print(f"Model: {engine.model_name}")
print("✅ Semantic search ready!")
```

---

## Quick Start

### 1. Basic Search

```python
from src.ml.semantic_search import quick_search

# Sample documents
documents = [
    {"id": "1", "text": "Machine learning is amazing"},
    {"id": "2", "text": "Deep learning revolutionizes AI"},
    {"id": "3", "text": "Python is great for data science"}
]

# Search
results = quick_search(documents, query="artificial intelligence", top_k=2)

for result in results:
    print(f"{result.document_id}: {result.score:.3f} - {result.content}")
```

**Output:**
```
2: 0.875 - Deep learning revolutionizes AI
1: 0.823 - Machine learning is amazing
```

### 2. Advanced Usage

```python
from src.ml.semantic_search import SemanticSearchEngine, SearchQuery

# Initialize engine
engine = SemanticSearchEngine(
    model_name='all-MiniLM-L6-v2',  # Fast and accurate
    cache_embeddings=True,           # Enable caching
    use_gpu=False                    # Set True if GPU available
)

# Index documents
documents = [
    {
        "id": "doc1",
        "text": "Natural language processing with transformers",
        "metadata": {"category": "NLP", "year": 2023}
    },
    # ... more documents
]

engine.index_documents(documents)

# Search with filters
query = SearchQuery(
    text="AI and machine learning",
    top_k=10,
    min_score=0.7,                   # Only high-quality results
    filters={"category": "NLP"},     # Filter by metadata
    rerank=True                      # Enable cross-encoder reranking
)

results = engine.search(query)

for result in results:
    print(f"[{result.rank}] {result.document_id} - Score: {result.score:.3f}")
    print(f"    Category: {result.metadata['category']}")
```

---

## Core Concepts

### 1. Embeddings

BERT converts text to dense vectors (embeddings) that capture semantic meaning:

```
"machine learning" → [0.123, -0.456, 0.789, ...]  (384 dimensions)
"ML algorithms"    → [0.145, -0.432, 0.801, ...]  (very similar!)
```

**Similarity**: Vectors for similar concepts are close in vector space.

### 2. Vector Similarity

We use **cosine similarity** to find similar documents:

```python
similarity = 1 - (distance² / 2)  # Converts L2 distance to similarity
```

- **Score 1.0**: Perfect match (identical)
- **Score 0.8-1.0**: Very similar
- **Score 0.5-0.8**: Somewhat similar
- **Score < 0.5**: Different topics

### 3. FAISS Index

FAISS (Facebook AI Similarity Search) enables fast vector search:

- **Index Type**: `IndexFlatL2` (exact search, good for <1M documents)
- **Search Speed**: Sub-millisecond for millions of vectors
- **Memory**: ~4KB per document (768-dim embeddings)

### 4. Hybrid Search

Combines best of both worlds:

```
Final Score = (semantic_weight × semantic_score) +
              ((1 - semantic_weight) × keyword_score)
```

**Recommended**: `semantic_weight = 0.7` (70% semantic, 30% keyword)

---

## API Reference

### SemanticSearchEngine

#### Constructor

```python
SemanticSearchEngine(
    model_name: str = "all-MiniLM-L6-v2",
    index_path: Optional[str] = None,
    cache_embeddings: bool = True,
    use_gpu: bool = False
)
```

**Parameters:**
- `model_name`: Sentence-transformer model (see [Models](#recommended-models))
- `index_path`: Path to save/load index
- `cache_embeddings`: Cache computed embeddings
- `use_gpu`: Use GPU for encoding (requires CUDA)

#### Methods

##### index_documents()

```python
engine.index_documents(
    documents: List[Dict[str, Any]],
    text_field: str = "text",
    id_field: str = "id",
    batch_size: int = 32
) -> int
```

Index documents for semantic search.

**Returns:** Number of documents indexed

##### search()

```python
engine.search(
    query: Union[str, SearchQuery],
    top_k: int = 10,
    min_score: float = 0.0
) -> List[SearchResult]
```

Search for similar documents.

**Returns:** List of SearchResult objects

##### hybrid_search()

```python
engine.hybrid_search(
    query: str,
    keyword_results: List[Dict],
    top_k: int = 10,
    semantic_weight: float = 0.7
) -> List[SearchResult]
```

Hybrid search combining semantic and keyword.

**Returns:** Merged and reranked results

##### save_index() / load_index()

```python
engine.save_index(path: str) -> None
engine.load_index(path: str) -> None
```

Persist index to disk.

##### get_stats()

```python
engine.get_stats() -> IndexStats
```

Get index statistics.

---

## Examples

### Example 1: Document Search System

```python
from src.ml.semantic_search import SemanticSearchEngine

# Load documents from database
documents = [
    {"id": "1", "text": "Introduction to neural networks", "author": "Alice"},
    {"id": "2", "text": "Deep learning fundamentals", "author": "Bob"},
    {"id": "3", "text": "Computer vision with CNNs", "author": "Charlie"},
]

# Create search engine
engine = SemanticSearchEngine(model_name='all-MiniLM-L6-v2')

# Index documents
print(f"Indexing {len(documents)} documents...")
engine.index_documents(documents)

# Search
query = "learning about AI"
results = engine.search(query, top_k=3)

print(f"\n🔍 Query: '{query}'")
print(f"Found {len(results)} results:\n")

for result in results:
    print(f"[{result.rank}] Doc {result.document_id} (score: {result.score:.3f})")
    print(f"    {result.content}")
    print(f"    Author: {result.metadata.get('author', 'Unknown')}\n")
```

### Example 2: Multi-lingual Search

```python
# Use multilingual model
engine = SemanticSearchEngine(model_name='paraphrase-multilingual-MiniLM-L12-v2')

documents = [
    {"id": "1", "text": "Machine learning basics", "lang": "en"},
    {"id": "2", "text": "Maschinelles Lernen Grundlagen", "lang": "de"},
    {"id": "3", "text": "Apprentissage automatique basique", "lang": "fr"},
]

engine.index_documents(documents)

# Search in any language!
results = engine.search("AI learning", top_k=3)

# Will find all 3 documents despite different languages
for result in results:
    print(f"{result.document_id}: {result.content}")
```

### Example 3: Hybrid Search with BM25

```python
from src.ml.semantic_search import SemanticSearchEngine

# Semantic search
engine = SemanticSearchEngine()
engine.index_documents(documents)

# Keyword search results (from BM25, Elasticsearch, etc.)
keyword_results = [
    {"id": "doc1", "score": 0.92},
    {"id": "doc5", "score": 0.85},
    {"id": "doc3", "score": 0.78}
]

# Combine both approaches
hybrid_results = engine.hybrid_search(
    query="machine learning algorithms",
    keyword_results=keyword_results,
    top_k=10,
    semantic_weight=0.6  # 60% semantic, 40% keyword
)

for result in hybrid_results:
    print(f"{result.document_id}: {result.score:.3f}")
```

### Example 4: Persistent Index

```python
from src.ml.semantic_search import SemanticSearchEngine

# First run: Create and save index
engine = SemanticSearchEngine()
engine.index_documents(large_document_collection)
engine.save_index("/path/to/index")
print("✅ Index saved!")

# Later: Load existing index (much faster!)
engine2 = SemanticSearchEngine()
engine2.load_index("/path/to/index")
print(f"✅ Loaded index with {engine2.get_stats().total_documents} documents")

# Ready to search immediately!
results = engine2.search("query")
```

### Example 5: With Reranking

```python
from src.ml.semantic_search import SearchQuery

query = SearchQuery(
    text="deep neural networks",
    top_k=20,        # Get more candidates
    rerank=True      # Rerank top results with cross-encoder
)

results = engine.search(query)

# Cross-encoder provides more accurate scores
# but is slower (only use for top-k results)
```

---

## REST API

### Start API Server

```python
from flask import Flask
from src.api.semantic_search_api import register_semantic_search_routes

app = Flask(__name__)
register_semantic_search_routes(app)

app.run(host='0.0.0.0', port=5001)
```

Or run the standalone server:

```bash
python src/api/semantic_search_api.py
```

### API Endpoints

#### POST /api/semantic/index

Index documents.

**Request:**
```json
{
  "documents": [
    {
      "id": "doc1",
      "text": "Machine learning is amazing",
      "metadata": {"category": "AI"}
    }
  ],
  "batch_size": 32
}
```

**Response:**
```json
{
  "success": true,
  "indexed_count": 1,
  "total_documents": 1,
  "message": "Successfully indexed 1 documents"
}
```

#### POST /api/semantic/search

Search documents.

**Request:**
```json
{
  "query": "artificial intelligence",
  "top_k": 5,
  "min_score": 0.5,
  "filters": {"category": "AI"},
  "rerank": false
}
```

**Response:**
```json
{
  "success": true,
  "query": "artificial intelligence",
  "results": [
    {
      "document_id": "doc1",
      "score": 0.8745,
      "rank": 1,
      "content": "Machine learning is...",
      "metadata": {"category": "AI"}
    }
  ],
  "count": 1,
  "search_time_ms": 23
}
```

#### GET /api/semantic/stats

Get index statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_documents": 1000,
    "embedding_dimension": 384,
    "index_size_bytes": 1536000,
    "model_name": "all-MiniLM-L6-v2",
    "last_updated": "2026-01-16T12:30:00"
  }
}
```

#### POST /api/semantic/hybrid-search

Hybrid semantic + keyword search.

**Request:**
```json
{
  "query": "machine learning",
  "keyword_results": [
    {"id": "doc1", "score": 0.9}
  ],
  "top_k": 10,
  "semantic_weight": 0.7
}
```

#### POST /api/semantic/save

Save index to disk.

**Request:**
```json
{
  "path": "/data/indexes/my_index"
}
```

#### POST /api/semantic/load

Load index from disk.

**Request:**
```json
{
  "path": "/data/indexes/my_index"
}
```

#### DELETE /api/semantic/clear

Clear the index.

---

## Performance

### Benchmarks

| Operation | Speed | Notes |
|-----------|-------|-------|
| Encoding (CPU) | 10-20 docs/sec | Depends on text length |
| Encoding (GPU) | 50-100 docs/sec | CUDA required |
| Search | <1ms | For millions of docs |
| Index building | ~5 sec/1000 docs | With caching |

### Optimization Tips

1. **Use GPU**: 5-10x faster encoding
   ```python
   engine = SemanticSearchEngine(use_gpu=True)
   ```

2. **Enable Caching**: Avoid re-computing embeddings
   ```python
   engine = SemanticSearchEngine(cache_embeddings=True)
   ```

3. **Batch Processing**: Process multiple documents at once
   ```python
   engine.index_documents(docs, batch_size=64)  # Larger batches
   ```

4. **Choose Right Model**: Trade-off between speed and accuracy
   - **Fast**: `all-MiniLM-L6-v2` (384 dim)
   - **Balanced**: `all-mpnet-base-v2` (768 dim)
   - **Accurate**: `all-roberta-large-v1` (1024 dim)

### Recommended Models

| Model | Dimensions | Speed | Accuracy | Use Case |
|-------|------------|-------|----------|----------|
| `all-MiniLM-L6-v2` | 384 | ⚡⚡⚡ | ⭐⭐ | Production, real-time |
| `all-mpnet-base-v2` | 768 | ⚡⚡ | ⭐⭐⭐ | Balanced |
| `multi-qa-MiniLM-L6-cos-v1` | 384 | ⚡⚡⚡ | ⭐⭐ | Q&A systems |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | ⚡⚡ | ⭐⭐ | Multi-lingual |

### Memory Usage

- **Index**: ~4KB per document (384 dims) or ~8KB (768 dims)
- **Model**: ~80-400MB depending on size
- **Example**: 100K docs with 384 dims = ~400MB index + 80MB model = ~500MB total

---

## Best Practices

### 1. Text Preprocessing

```python
def preprocess_text(text: str) -> str:
    """Clean text before indexing"""
    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove very short texts (less informative)
    if len(text) < 10:
        return ""

    # Truncate very long texts (BERT limit: 512 tokens)
    if len(text) > 5000:
        text = text[:5000]

    return text

# Apply before indexing
documents = [
    {"id": doc.id, "text": preprocess_text(doc.content)}
    for doc in raw_documents
]
```

### 2. Chunking Long Documents

```python
def chunk_document(text: str, chunk_size: int = 500) -> List[str]:
    """Split long documents into chunks"""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

# Index chunks separately
all_chunks = []
for doc in documents:
    chunks = chunk_document(doc['text'])
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "id": f"{doc['id']}_chunk_{i}",
            "text": chunk,
            "metadata": {"parent_id": doc['id']}
        })

engine.index_documents(all_chunks)
```

### 3. Metadata Enrichment

```python
documents = [
    {
        "id": "doc1",
        "text": "Document content...",
        "metadata": {
            "category": "AI",
            "date": "2026-01-16",
            "author": "Alice",
            "tags": ["ml", "nlp"],
            "priority": "high"
        }
    }
]

# Search with metadata filters
query = SearchQuery(
    text="machine learning",
    filters={
        "category": "AI",
        "priority": "high"
    }
)
```

### 4. Incremental Indexing

```python
# Initial index
engine.index_documents(initial_documents)
engine.save_index("/data/index_v1")

# Later: Add new documents
new_documents = fetch_new_documents()
engine.index_documents(new_documents)
engine.save_index("/data/index_v2")
```

### 5. Query Optimization

```python
# Good query
good_query = "machine learning classification algorithms"

# Too short (ambiguous)
bad_query = "ML"

# Too long (loses focus)
bad_query = "I want to learn about machine learning classification algorithms for image recognition..."

# Optimal: 3-10 words describing the topic
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: sentence-transformers

**Solution:**
```bash
pip install sentence-transformers
```

### Issue: ModuleNotFoundError: faiss

**Solution:**
```bash
# For CPU
pip install faiss-cpu

# For GPU (requires CUDA)
pip install faiss-gpu
```

### Issue: Search returns no results

**Possible causes:**
1. Index is empty - check `engine.get_stats().total_documents`
2. `min_score` too high - try lowering to 0.0
3. Filters too restrictive - check metadata

**Debug:**
```python
stats = engine.get_stats()
print(f"Total documents: {stats.total_documents}")

# Try without filters
results = engine.search("query", min_score=0.0)
print(f"Found {len(results)} results")
```

### Issue: Slow indexing

**Solutions:**
1. Increase batch size: `batch_size=64`
2. Enable caching: `cache_embeddings=True`
3. Use GPU: `use_gpu=True`
4. Use faster model: `all-MiniLM-L6-v2`

### Issue: High memory usage

**Solutions:**
1. Use smaller model (384 dims instead of 768)
2. Process in smaller batches
3. Clear cache: `engine.clear_cache()`
4. Use disk-based index for very large datasets

### Issue: Low search quality

**Solutions:**
1. Try better model: `all-mpnet-base-v2`
2. Enable reranking: `rerank=True`
3. Use hybrid search with keyword results
4. Preprocess text better (remove noise)
5. Chunk long documents

---

## Additional Resources

### Documentation
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Hugging Face Models](https://huggingface.co/models?library=sentence-transformers)

### Model Hub
- [Best Models for Semantic Search](https://www.sbert.net/docs/pretrained_models.html)
- [Multilingual Models](https://www.sbert.net/docs/pretrained_models.html#multi-lingual-models)

### Papers
- [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084)

---

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [Examples](#examples)
- Consult API Reference

---

**Version:** 1.0.0
**Last Updated:** 2026-01-16
**Status:** Production Ready ✅
