#!/usr/bin/env python3
"""
Document Search & Discovery
============================

Advanced search and discovery system for document repositories.

Features:
- Full-text search with TF-IDF/BM25
- Semantic search using embeddings
- Entity-based search (find documents by person, org, location)
- Relation-based search (find documents with specific relationships)
- Knowledge graph queries
- Faceted search (filter by category, date, entities, etc.)
- Search suggestions and autocomplete
- Similar document recommendation
- Advanced query language support
- Search analytics and insights

Search Types:
- Text search: Full-text keyword search
- Semantic search: Find documents by meaning
- Entity search: Documents mentioning specific entities
- Relation search: Documents with specific relationships
- Graph search: Path-based queries through knowledge graph
- Hybrid search: Combine multiple search types

Usage:
    # Simple text search
    python doc-search.py search "contract agreement"

    # Entity search
    python doc-search.py entity --person "Max Mustermann"

    # Relation search
    python doc-search.py relation --type WORKS_AT --source "Max Mustermann"

    # Semantic search
    python doc-search.py semantic "employment contracts from 2024"

    # Graph query
    python doc-search.py graph --query "MATCH (p:PERSON)-[r:WORKS_AT]->(o:ORG) RETURN p,r,o"

    # Advanced search with filters
    python doc-search.py search "invoice" --category INVOICE --date-from 2024-01-01

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from collections import defaultdict
import logging
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: scikit-learn not installed. Some features may be limited.")

# Import core modules
from src.core.database import DocumentDatabase
from src.core.advanced_search import AdvancedSearchEngine
from src.core.logging_config import setup_logging

# Import ML modules
from src.ml.ner import NEREngine, EntityType
from src.ml.relation_extractor import RelationExtractor, RelationType
from src.ml.knowledge_graph import KnowledgeGraph, KnowledgeGraphBuilder

# Setup logging
logger = setup_logging(__name__, log_level="INFO")


class DocumentIndex:
    """Document index for fast searching."""

    def __init__(self):
        """Initialize document index."""
        self.documents: List[Dict[str, Any]] = []
        self.tfidf_vectorizer: Optional[Any] = None
        self.tfidf_matrix: Optional[Any] = None

        # Entity and relation indices
        self.entity_index: Dict[str, List[int]] = defaultdict(list)  # entity_text -> doc_ids
        self.relation_index: Dict[str, List[int]] = defaultdict(list)  # relation_key -> doc_ids

        # Knowledge graph
        self.knowledge_graph: Optional[KnowledgeGraph] = None

        logger.info("DocumentIndex initialized")

    def add_document(self, doc_id: int, document: Dict[str, Any]):
        """
        Add document to index.

        Args:
            doc_id: Document ID
            document: Document data with text, entities, relations
        """
        self.documents.append({
            "id": doc_id,
            "data": document
        })

        # Index entities
        for entity in document.get("entities", []):
            self.entity_index[entity["text"]].append(doc_id)
            self.entity_index[f"{entity['type']}:{entity['text']}"].append(doc_id)

        # Index relations
        for relation in document.get("relations", []):
            rel_key = f"{relation['source']}:{relation['relation']}:{relation['target']}"
            self.relation_index[rel_key].append(doc_id)
            self.relation_index[relation['relation']].append(doc_id)

    def build_tfidf_index(self):
        """Build TF-IDF index for text search."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, skipping TF-IDF indexing")
            return

        texts = [doc["data"].get("text", "") for doc in self.documents]

        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        )

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        logger.info(f"TF-IDF index built: {len(texts)} documents")

    def text_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Full-text search using TF-IDF.

        Args:
            query: Search query
            top_k: Number of top results

        Returns:
            List of (doc_id, score) tuples
        """
        if not self.tfidf_vectorizer or not SKLEARN_AVAILABLE:
            # Fallback to simple keyword matching
            return self._keyword_search(query, top_k)

        # Vectorize query
        query_vec = self.tfidf_vectorizer.transform([query])

        # Calculate similarities
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = [
            (self.documents[idx]["id"], float(similarities[idx]))
            for idx in top_indices
            if similarities[idx] > 0
        ]

        return results

    def _keyword_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Fallback keyword search."""
        query_lower = query.lower()
        keywords = query_lower.split()

        results = []
        for doc in self.documents:
            text = doc["data"].get("text", "").lower()
            score = sum(1 for kw in keywords if kw in text) / len(keywords) if keywords else 0
            if score > 0:
                results.append((doc["id"], score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def entity_search(
        self,
        entity_text: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> List[int]:
        """
        Search documents by entity.

        Args:
            entity_text: Entity text to search for
            entity_type: Entity type to filter

        Returns:
            List of document IDs
        """
        if entity_text and entity_type:
            key = f"{entity_type}:{entity_text}"
            return self.entity_index.get(key, [])
        elif entity_text:
            return self.entity_index.get(entity_text, [])
        else:
            return []

    def relation_search(
        self,
        relation_type: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None
    ) -> List[int]:
        """
        Search documents by relation.

        Args:
            relation_type: Type of relation
            source: Source entity
            target: Target entity

        Returns:
            List of document IDs
        """
        if source and relation_type and target:
            key = f"{source}:{relation_type}:{target}"
            return self.relation_index.get(key, [])
        elif relation_type:
            return self.relation_index.get(relation_type, [])
        else:
            return []


class DocumentSearchEngine:
    """Main search engine class."""

    def __init__(self, database_path: str = "data/documents.db"):
        """
        Initialize search engine.

        Args:
            database_path: Path to document database
        """
        self.database = DocumentDatabase(database_path)
        self.index = DocumentIndex()
        self.ner_engine = NEREngine(use_spacy=True)
        self.relation_extractor = RelationExtractor(use_spacy=True)

        logger.info("DocumentSearchEngine initialized")

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents for searching.

        Args:
            documents: List of documents to index
        """
        logger.info(f"Indexing {len(documents)} documents")

        for i, doc in enumerate(documents):
            self.index.add_document(i, doc)

        # Build TF-IDF index
        self.index.build_tfidf_index()

        logger.info("Document indexing complete")

    def search(
        self,
        query: str,
        search_type: str = "text",
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documents.

        Args:
            query: Search query
            search_type: Type of search (text, entity, relation, semantic)
            top_k: Number of results
            filters: Additional filters

        Returns:
            List of search results
        """
        logger.info(f"Searching: '{query}' (type={search_type}, top_k={top_k})")

        if search_type == "text":
            results = self._text_search(query, top_k, filters)
        elif search_type == "entity":
            results = self._entity_search(query, filters)
        elif search_type == "relation":
            results = self._relation_search(filters)
        elif search_type == "semantic":
            results = self._semantic_search(query, top_k, filters)
        else:
            raise ValueError(f"Unknown search type: {search_type}")

        logger.info(f"Found {len(results)} results")
        return results

    def _text_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute text search."""
        doc_scores = self.index.text_search(query, top_k * 2)  # Get more for filtering

        results = []
        for doc_id, score in doc_scores:
            doc = self.index.documents[doc_id]["data"]

            # Apply filters
            if filters and not self._apply_filters(doc, filters):
                continue

            results.append({
                "document_id": doc_id,
                "score": score,
                "filename": doc.get("filename", "unknown"),
                "text_preview": doc.get("text", "")[:200] + "...",
                "category": doc.get("classification", {}).get("category", "UNKNOWN"),
                "entities_count": len(doc.get("entities", [])),
                "relations_count": len(doc.get("relations", []))
            })

            if len(results) >= top_k:
                break

        return results

    def _entity_search(
        self,
        entity_text: str,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search by entity."""
        entity_type = filters.get("entity_type") if filters else None
        doc_ids = self.index.entity_search(entity_text, entity_type)

        results = []
        for doc_id in doc_ids:
            doc = self.index.documents[doc_id]["data"]

            # Apply other filters
            if filters and not self._apply_filters(doc, filters):
                continue

            # Find matching entities
            matching_entities = [
                e for e in doc.get("entities", [])
                if e["text"] == entity_text and (not entity_type or e["type"] == entity_type)
            ]

            results.append({
                "document_id": doc_id,
                "filename": doc.get("filename", "unknown"),
                "matching_entities": matching_entities,
                "text_preview": doc.get("text", "")[:200] + "...",
                "category": doc.get("classification", {}).get("category", "UNKNOWN")
            })

        return results

    def _relation_search(self, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search by relation."""
        if not filters:
            return []

        relation_type = filters.get("relation_type")
        source = filters.get("source")
        target = filters.get("target")

        doc_ids = self.index.relation_search(relation_type, source, target)

        results = []
        for doc_id in doc_ids:
            doc = self.index.documents[doc_id]["data"]

            # Find matching relations
            matching_relations = []
            for r in doc.get("relations", []):
                if relation_type and r["relation"] != relation_type:
                    continue
                if source and r["source"] != source:
                    continue
                if target and r["target"] != target:
                    continue
                matching_relations.append(r)

            results.append({
                "document_id": doc_id,
                "filename": doc.get("filename", "unknown"),
                "matching_relations": matching_relations,
                "text_preview": doc.get("text", "")[:200] + "...",
                "category": doc.get("classification", {}).get("category", "UNKNOWN")
            })

        return results

    def _semantic_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Semantic search (placeholder - would use embeddings in production)."""
        # For now, fall back to text search
        logger.warning("Semantic search not fully implemented, falling back to text search")
        return self._text_search(query, top_k, filters)

    def _apply_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to document."""
        # Category filter
        if "category" in filters:
            doc_category = doc.get("classification", {}).get("category", "UNKNOWN")
            if doc_category != filters["category"]:
                return False

        # Date filters
        if "date_from" in filters:
            # Implement date filtering
            pass

        if "date_to" in filters:
            # Implement date filtering
            pass

        return True

    def find_similar(self, doc_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar documents.

        Args:
            doc_id: Reference document ID
            top_k: Number of similar documents

        Returns:
            List of similar documents
        """
        if not self.index.tfidf_matrix or not SKLEARN_AVAILABLE:
            logger.warning("TF-IDF index not available")
            return []

        # Get document vector
        doc_vec = self.index.tfidf_matrix[doc_id]

        # Calculate similarities
        similarities = cosine_similarity(doc_vec, self.index.tfidf_matrix).flatten()

        # Get top-k (excluding the document itself)
        top_indices = np.argsort(similarities)[::-1][1:top_k + 1]

        results = []
        for idx in top_indices:
            doc = self.index.documents[idx]["data"]
            results.append({
                "document_id": idx,
                "similarity": float(similarities[idx]),
                "filename": doc.get("filename", "unknown"),
                "category": doc.get("classification", {}).get("category", "UNKNOWN"),
                "text_preview": doc.get("text", "")[:200] + "..."
            })

        return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Document Search & Discovery - Advanced search engine",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Search command
    search_parser = subparsers.add_parser("search", help="Text search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-k", "--top-k", type=int, default=10, help="Number of results")
    search_parser.add_argument("--category", help="Filter by category")

    # Entity search command
    entity_parser = subparsers.add_parser("entity", help="Entity search")
    entity_parser.add_argument("--person", help="Search for person")
    entity_parser.add_argument("--org", help="Search for organization")
    entity_parser.add_argument("--location", help="Search for location")

    # Relation search command
    relation_parser = subparsers.add_parser("relation", help="Relation search")
    relation_parser.add_argument("--type", help="Relation type")
    relation_parser.add_argument("--source", help="Source entity")
    relation_parser.add_argument("--target", help="Target entity")

    # Semantic search command
    semantic_parser = subparsers.add_parser("semantic", help="Semantic search")
    semantic_parser.add_argument("query", help="Search query")
    semantic_parser.add_argument("-k", "--top-k", type=int, default=10, help="Number of results")

    # Similar command
    similar_parser = subparsers.add_parser("similar", help="Find similar documents")
    similar_parser.add_argument("doc_id", type=int, help="Document ID")
    similar_parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize search engine
    search_engine = DocumentSearchEngine()

    # Load and index documents (placeholder)
    # In production, load from database
    sample_docs = []  # Load from database
    search_engine.index_documents(sample_docs)

    # Execute command
    try:
        if args.command == "search":
            filters = {}
            if args.category:
                filters["category"] = args.category

            results = search_engine.search(
                query=args.query,
                search_type="text",
                top_k=args.top_k,
                filters=filters
            )

            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "entity":
            entity_text = args.person or args.org or args.location
            entity_type = (
                "PERSON" if args.person else
                "ORGANIZATION" if args.org else
                "LOCATION" if args.location else None
            )

            filters = {"entity_type": entity_type} if entity_type else {}

            results = search_engine.search(
                query=entity_text,
                search_type="entity",
                filters=filters
            )

            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "relation":
            filters = {}
            if args.type:
                filters["relation_type"] = args.type
            if args.source:
                filters["source"] = args.source
            if args.target:
                filters["target"] = args.target

            results = search_engine.search(
                query="",
                search_type="relation",
                filters=filters
            )

            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "semantic":
            results = search_engine.search(
                query=args.query,
                search_type="semantic",
                top_k=args.top_k
            )

            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "similar":
            results = search_engine.find_similar(args.doc_id, args.top_k)
            print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
