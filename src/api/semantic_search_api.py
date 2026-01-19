#!/usr/bin/env python3
"""
Semantic Search API Endpoints

Provides REST API endpoints for semantic search functionality.

Endpoints:
- POST /api/semantic/index - Index documents
- POST /api/semantic/search - Search documents
- POST /api/semantic/hybrid-search - Hybrid semantic + keyword search
- GET /api/semantic/stats - Get index statistics
- DELETE /api/semantic/clear - Clear index
- POST /api/semantic/save - Save index to disk
- POST /api/semantic/load - Load index from disk
"""

import logging
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

from src.ml.semantic_search import SemanticSearchEngine, SearchQuery

logger = logging.getLogger("dms.semantic_search_api")

# Create Blueprint
semantic_search_bp = Blueprint("semantic_search", __name__, url_prefix="/api/semantic")

# Global search engine instance (can be replaced with app context)
_search_engine: Optional[SemanticSearchEngine] = None


def get_search_engine() -> SemanticSearchEngine:
    """Get or create semantic search engine"""
    global _search_engine
    if _search_engine is None:
        model_name = "all-MiniLM-L6-v2"  # Can be configured via env var
        _search_engine = SemanticSearchEngine(model_name=model_name, cache_embeddings=True)
        logger.info(f"Initialized semantic search engine with model: {model_name}")
    return _search_engine


@semantic_search_bp.route("/index", methods=["POST"])
def index_documents():
    """
    Index documents for semantic search

    Request JSON:
    {
        "documents": [
            {
                "id": "doc1",
                "text": "Document content...",
                "metadata": {"category": "AI", "author": "John"}
            }
        ],
        "text_field": "text",  # optional, default: "text"
        "id_field": "id",  # optional, default: "id"
        "batch_size": 32  # optional, default: 32
    }

    Response:
    {
        "success": true,
        "indexed_count": 100,
        "total_documents": 150,
        "message": "Successfully indexed 100 documents"
    }
    """
    try:
        data = request.get_json()

        if not data or "documents" not in data:
            return jsonify({"success": False, "error": "Missing 'documents' field"}), 400

        documents = data["documents"]
        text_field = data.get("text_field", "text")
        id_field = data.get("id_field", "id")
        batch_size = data.get("batch_size", 32)

        # Validate documents
        if not isinstance(documents, list) or len(documents) == 0:
            return jsonify({"success": False, "error": "Documents must be a non-empty list"}), 400

        # Index documents
        engine = get_search_engine()
        indexed_count = engine.index_documents(
            documents=documents, text_field=text_field, id_field=id_field, batch_size=batch_size
        )

        stats = engine.get_stats()

        return (
            jsonify(
                {
                    "success": True,
                    "indexed_count": indexed_count,
                    "total_documents": stats.total_documents,
                    "message": f"Successfully indexed {indexed_count} documents",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error indexing documents: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@semantic_search_bp.route("/search", methods=["POST"])
def search():
    """
    Search for similar documents

    Request JSON:
    {
        "query": "machine learning and AI",
        "top_k": 10,  # optional, default: 10
        "min_score": 0.5,  # optional, default: 0.0
        "filters": {"category": "AI"},  # optional
        "rerank": false  # optional, default: false
    }

    Response:
    {
        "success": true,
        "query": "machine learning and AI",
        "results": [
            {
                "document_id": "doc1",
                "score": 0.87,
                "rank": 1,
                "content": "Machine learning is...",
                "metadata": {"category": "AI"}
            }
        ],
        "count": 5,
        "search_time_ms": 45
    }
    """
    try:
        import time

        start_time = time.time()

        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"success": False, "error": "Missing 'query' field"}), 400

        # Parse search parameters
        query_text = data["query"]
        top_k = data.get("top_k", 10)
        min_score = data.get("min_score", 0.0)
        filters = data.get("filters", {})
        rerank = data.get("rerank", False)

        # Create search query
        query = SearchQuery(text=query_text, top_k=top_k, min_score=min_score, filters=filters, rerank=rerank)

        # Execute search
        engine = get_search_engine()
        results = engine.search(query)

        # Convert results to dict
        results_data = [
            {
                "document_id": r.document_id,
                "score": round(r.score, 4),
                "rank": r.rank,
                "content": r.content[:500],  # Truncate long content
                "metadata": r.metadata,
            }
            for r in results
        ]

        search_time_ms = int((time.time() - start_time) * 1000)

        return (
            jsonify(
                {
                    "success": True,
                    "query": query_text,
                    "results": results_data,
                    "count": len(results_data),
                    "search_time_ms": search_time_ms,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@semantic_search_bp.route("/hybrid-search", methods=["POST"])
def hybrid_search():
    """
    Hybrid search combining semantic and keyword search

    Request JSON:
    {
        "query": "machine learning",
        "keyword_results": [
            {"id": "doc1", "score": 0.9},
            {"id": "doc2", "score": 0.7}
        ],
        "top_k": 10,  # optional
        "semantic_weight": 0.7  # optional, default: 0.7
    }

    Response:
    {
        "success": true,
        "query": "machine learning",
        "results": [...],
        "count": 5
    }
    """
    try:
        data = request.get_json()

        if not data or "query" not in data or "keyword_results" not in data:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        query_text = data["query"]
        keyword_results = data["keyword_results"]
        top_k = data.get("top_k", 10)
        semantic_weight = data.get("semantic_weight", 0.7)

        # Execute hybrid search
        engine = get_search_engine()
        results = engine.hybrid_search(
            query=query_text, keyword_results=keyword_results, top_k=top_k, semantic_weight=semantic_weight
        )

        # Convert results to dict
        results_data = [
            {
                "document_id": r.document_id,
                "score": round(r.score, 4),
                "rank": r.rank,
                "content": r.content[:500],
                "metadata": r.metadata,
            }
            for r in results
        ]

        return (
            jsonify({"success": True, "query": query_text, "results": results_data, "count": len(results_data)}),
            200,
        )

    except Exception as e:
        logger.error(f"Error during hybrid search: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@semantic_search_bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Get index statistics

    Response:
    {
        "success": true,
        "stats": {
            "total_documents": 150,
            "embedding_dimension": 384,
            "index_size_bytes": 614400,
            "model_name": "all-MiniLM-L6-v2",
            "last_updated": "2026-01-16T12:30:00"
        }
    }
    """
    try:
        engine = get_search_engine()
        stats = engine.get_stats()

        return (
            jsonify(
                {
                    "success": True,
                    "stats": {
                        "total_documents": stats.total_documents,
                        "embedding_dimension": stats.embedding_dimension,
                        "index_size_bytes": stats.index_size_bytes,
                        "model_name": stats.model_name,
                        "last_updated": stats.last_updated.isoformat(),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@semantic_search_bp.route("/clear", methods=["DELETE"])
def clear_index():
    """
    Clear the search index

    Response:
    {
        "success": true,
        "message": "Index cleared successfully"
    }
    """
    try:
        global _search_engine
        _search_engine = None  # Force recreation on next request

        return jsonify({"success": True, "message": "Index cleared successfully"}), 200

    except Exception as e:
        logger.error(f"Error clearing index: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@semantic_search_bp.route("/save", methods=["POST"])
def save_index():
    """
    Save index to disk

    Request JSON:
    {
        "path": "/path/to/index"
    }

    Response:
    {
        "success": true,
        "message": "Index saved to /path/to/index"
    }
    """
    try:
        data = request.get_json()

        if not data or "path" not in data:
            return jsonify({"success": False, "error": "Missing 'path' field"}), 400

        path = data["path"]

        engine = get_search_engine()
        engine.save_index(path)

        return jsonify({"success": True, "message": f"Index saved to {path}"}), 200

    except Exception as e:
        logger.error(f"Error saving index: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@semantic_search_bp.route("/load", methods=["POST"])
def load_index():
    """
    Load index from disk

    Request JSON:
    {
        "path": "/path/to/index"
    }

    Response:
    {
        "success": true,
        "message": "Index loaded from /path/to/index",
        "stats": {...}
    }
    """
    try:
        data = request.get_json()

        if not data or "path" not in data:
            return jsonify({"success": False, "error": "Missing 'path' field"}), 400

        path = data["path"]

        engine = get_search_engine()
        engine.load_index(path)

        stats = engine.get_stats()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Index loaded from {path}",
                    "stats": {
                        "total_documents": stats.total_documents,
                        "embedding_dimension": stats.embedding_dimension,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error loading index: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


def register_semantic_search_routes(app):
    """
    Register semantic search routes with Flask app

    Args:
        app: Flask application instance
    """
    app.register_blueprint(semantic_search_bp)
    logger.info("Registered semantic search API routes")


if __name__ == "__main__":
    # Example Flask app setup
    from flask import Flask

    app = Flask(__name__)
    register_semantic_search_routes(app)

    print("Semantic Search API Endpoints:")
    print("=" * 60)
    for rule in app.url_map.iter_rules():
        if "/api/semantic" in rule.rule:
            methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            print(f"{methods:10} {rule.rule}")

    print("\nStarting development server on http://localhost:5001...")
    # Debug mode controlled by environment variable for security
    import os
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug_mode)
