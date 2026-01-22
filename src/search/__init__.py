"""
BERT-based Semantic Search Module

This module provides advanced semantic search capabilities using BERT embeddings
and vector databases for intelligent document retrieval.

Features:
- Dense vector embeddings with Sentence-BERT
- Semantic similarity search
- Multi-lingual support
- Real-time indexing
- Query expansion and re-ranking
"""

__version__ = "1.0.0"
__author__ = "Document Management System Team"

from .bert_embedder import BERTEmbedder
from .vector_store import VectorStore, ChromaDBStore, FAISSStore
from .semantic_search import SemanticSearch
from .query_processor import QueryProcessor

__all__ = [
    "BERTEmbedder",
    "VectorStore",
    "ChromaDBStore",
    "FAISSStore",
    "SemanticSearch",
    "QueryProcessor",
]
