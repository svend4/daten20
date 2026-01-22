"""
Semantic Search REST API

Flask REST API endpoints for BERT-based semantic search.

Endpoints:
- POST /api/v1/semantic-search/index - Index documents
- POST /api/v1/semantic-search/search - Search documents
- GET  /api/v1/semantic-search/similar/{doc_id} - Find similar documents
- GET  /api/v1/semantic-search/stats - Get statistics
- DELETE /api/v1/semantic-search/documents/{doc_id} - Delete document
- DELETE /api/v1/semantic-search/clear - Clear index
"""

import logging
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify
from functools import wraps

try:
    from ..search import SemanticSearch, QueryProcessor, ResultReranker
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    logging.warning("Semantic search module not available")


# Create blueprint
semantic_search_bp = Blueprint('semantic_search', __name__, url_prefix='/api/v1/semantic-search')

# Global search instance (will be initialized on first use)
_search_instance = None
_query_processor = None
_reranker = None

logger = logging.getLogger(__name__)


def get_search_instance(
    model_name: str = "fast",
    store_type: str = "chroma",
    persist_directory: str = "./semantic_search_db"
) -> SemanticSearch:
    """Get or create search instance."""
    global _search_instance
    
    if _search_instance is None:
        if not SEARCH_AVAILABLE:
            raise ImportError("Semantic search module not available")
        
        logger.info(f"Initializing semantic search (model={model_name}, store={store_type})")
        _search_instance = SemanticSearch(
            model_name=model_name,
            store_type=store_type,
            persist_directory=persist_directory
        )
    
    return _search_instance


def get_query_processor() -> QueryProcessor:
    """Get or create query processor."""
    global _query_processor
    
    if _query_processor is None:
        _query_processor = QueryProcessor()
    
    return _query_processor


def get_reranker() -> ResultReranker:
    """Get or create result reranker."""
    global _reranker
    
    if _reranker is None:
        _reranker = ResultReranker()
    
    return _reranker


def handle_errors(f):
    """Decorator to handle errors and return JSON responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return jsonify({
                "error": "Semantic search not available",
                "message": str(e),
                "install": "pip install sentence-transformers chromadb faiss-cpu"
            }), 503
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({"error": "Validation error", "message": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return jsonify({"error": "Internal server error", "message": str(e)}), 500
    
    return decorated_function


@semantic_search_bp.route('/index', methods=['POST'])
@handle_errors
def index_documents():
    """
    Index documents for semantic search.
    
    Request body:
    {
        "documents": [
            {"content": "text...", "metadata": {...}},
            ...
        ],
        "text_field": "content",  // optional, default: "content"
        "batch_size": 32,          // optional, default: 32
        "model": "fast"            // optional, default: "fast"
    }
    
    Response:
    {
        "success": true,
        "indexed": 10,
        "document_ids": ["doc_1", "doc_2", ...],
        "total_documents": 100
    }
    """
    data = request.get_json()
    
    if not data or 'documents' not in data:
        return jsonify({"error": "Missing 'documents' in request body"}), 400
    
    documents = data['documents']
    text_field = data.get('text_field', 'content')
    batch_size = data.get('batch_size', 32)
    model_name = data.get('model', 'fast')
    
    if not isinstance(documents, list):
        return jsonify({"error": "'documents' must be a list"}), 400
    
    if not documents:
        return jsonify({"error": "'documents' list is empty"}), 400
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Index documents
    doc_ids = search.add_documents(
        documents,
        text_field=text_field,
        batch_size=batch_size
    )
    
    return jsonify({
        "success": True,
        "indexed": len(doc_ids),
        "document_ids": doc_ids,
        "total_documents": search.count_documents()
    }), 201


@semantic_search_bp.route('/search', methods=['POST'])
@handle_errors
def search():
    """
    Search for documents using semantic similarity.
    
    Request body:
    {
        "query": "search query",
        "top_k": 10,                // optional, default: 10
        "min_score": 0.5,           // optional
        "filters": {...},           // optional metadata filters
        "expand_query": true,       // optional, default: false
        "rerank": true,             // optional, default: false
        "model": "fast"             // optional, default: "fast"
    }
    
    Response:
    {
        "success": true,
        "query": "search query",
        "results": [
            {
                "id": "doc_1",
                "document": {...},
                "score": 0.95,
                "distance": 0.05
            },
            ...
        ],
        "count": 10,
        "total_time_ms": 150
    }
    """
    import time
    start_time = time.time()
    
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    query = data['query']
    top_k = data.get('top_k', 10)
    min_score = data.get('min_score')
    filters = data.get('filters')
    expand_query = data.get('expand_query', False)
    rerank = data.get('rerank', False)
    model_name = data.get('model', 'fast')
    
    # Validate query
    if not isinstance(query, str) or not query.strip():
        return jsonify({"error": "'query' must be a non-empty string"}), 400
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Process query if requested
    processed_query = query
    if expand_query:
        processor = get_query_processor()
        processed_query = processor.process(query)
    
    # Search
    results = search.search(
        processed_query,
        top_k=top_k,
        filters=filters,
        min_score=min_score
    )
    
    # Re-rank if requested
    if rerank:
        reranker = get_reranker()
        results = reranker.rerank(results, query)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        "success": True,
        "query": query,
        "processed_query": processed_query if expand_query else None,
        "results": results,
        "count": len(results),
        "total_time_ms": round(elapsed_ms, 2)
    }), 200


@semantic_search_bp.route('/similar/<doc_id>', methods=['GET'])
@handle_errors
def find_similar(doc_id: str):
    """
    Find documents similar to a given document.
    
    Query params:
    - top_k: Number of results (default: 10)
    - filters: JSON metadata filters
    - model: Model name (default: "fast")
    
    Response:
    {
        "success": true,
        "document_id": "doc_123",
        "results": [...],
        "count": 10
    }
    """
    top_k = request.args.get('top_k', 10, type=int)
    filters_json = request.args.get('filters')
    model_name = request.args.get('model', 'fast')
    
    filters = None
    if filters_json:
        import json
        try:
            filters = json.loads(filters_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON in 'filters' parameter"}), 400
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Find similar
    results = search.search_similar(
        doc_id,
        top_k=top_k,
        filters=filters
    )
    
    return jsonify({
        "success": True,
        "document_id": doc_id,
        "results": results,
        "count": len(results)
    }), 200


@semantic_search_bp.route('/stats', methods=['GET'])
@handle_errors
def get_stats():
    """
    Get semantic search statistics.
    
    Response:
    {
        "success": true,
        "stats": {
            "total_documents": 100,
            "embedder_info": {...},
            "vector_store_type": "ChromaDBStore"
        }
    }
    """
    model_name = request.args.get('model', 'fast')
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    stats = search.get_stats()
    
    return jsonify({
        "success": True,
        "stats": stats
    }), 200


@semantic_search_bp.route('/documents/<doc_id>', methods=['DELETE'])
@handle_errors
def delete_document(doc_id: str):
    """
    Delete a document by ID.
    
    Response:
    {
        "success": true,
        "deleted": ["doc_123"]
    }
    """
    model_name = request.args.get('model', 'fast')
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Delete
    success = search.delete_documents([doc_id])
    
    if success:
        return jsonify({
            "success": True,
            "deleted": [doc_id]
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "Failed to delete document"
        }), 500


@semantic_search_bp.route('/documents/batch', methods=['DELETE'])
@handle_errors
def delete_documents_batch():
    """
    Delete multiple documents by IDs.
    
    Request body:
    {
        "document_ids": ["doc_1", "doc_2", ...]
    }
    
    Response:
    {
        "success": true,
        "deleted": ["doc_1", "doc_2", ...]
    }
    """
    data = request.get_json()
    
    if not data or 'document_ids' not in data:
        return jsonify({"error": "Missing 'document_ids' in request body"}), 400
    
    doc_ids = data['document_ids']
    model_name = data.get('model', 'fast')
    
    if not isinstance(doc_ids, list):
        return jsonify({"error": "'document_ids' must be a list"}), 400
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Delete
    success = search.delete_documents(doc_ids)
    
    if success:
        return jsonify({
            "success": True,
            "deleted": doc_ids
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "Failed to delete documents"
        }), 500


@semantic_search_bp.route('/clear', methods=['DELETE'])
@handle_errors
def clear_index():
    """
    Clear all documents from index.
    
    Response:
    {
        "success": true,
        "message": "Index cleared"
    }
    """
    model_name = request.args.get('model', 'fast')
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Clear
    success = search.clear_index()
    
    if success:
        return jsonify({
            "success": True,
            "message": "Index cleared"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "Failed to clear index"
        }), 500


@semantic_search_bp.route('/batch-search', methods=['POST'])
@handle_errors
def batch_search():
    """
    Search for multiple queries in batch.
    
    Request body:
    {
        "queries": ["query 1", "query 2", ...],
        "top_k": 10,
        "model": "fast"
    }
    
    Response:
    {
        "success": true,
        "results": [
            [{"id": "doc_1", ...}, ...],  // results for query 1
            [{"id": "doc_2", ...}, ...],  // results for query 2
            ...
        ]
    }
    """
    data = request.get_json()
    
    if not data or 'queries' not in data:
        return jsonify({"error": "Missing 'queries' in request body"}), 400
    
    queries = data['queries']
    top_k = data.get('top_k', 10)
    model_name = data.get('model', 'fast')
    
    if not isinstance(queries, list):
        return jsonify({"error": "'queries' must be a list"}), 400
    
    # Get search instance
    search = get_search_instance(model_name=model_name)
    
    # Batch search
    results = search.batch_search(queries, top_k=top_k)
    
    return jsonify({
        "success": True,
        "queries": queries,
        "results": results,
        "count": len(queries)
    }), 200


# Health check endpoint
@semantic_search_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Response:
    {
        "status": "healthy",
        "semantic_search_available": true
    }
    """
    return jsonify({
        "status": "healthy",
        "semantic_search_available": SEARCH_AVAILABLE
    }), 200
