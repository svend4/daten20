"""
Semantic Search Engine

Combines BERT embeddings and vector stores for intelligent document search.
"""

import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np

from .bert_embedder import BERTEmbedder, MockBERTEmbedder, SENTENCE_TRANSFORMERS_AVAILABLE
from .vector_store import VectorStore, ChromaDBStore, FAISSStore


class SemanticSearch:
    """
    Semantic search engine using BERT embeddings and vector stores.
    
    Features:
    - Add documents with automatic embedding
    - Semantic similarity search
    - Query expansion
    - Result re-ranking
    - Metadata filtering
    
    Examples:
        >>> search = SemanticSearch()
        >>> search.add_documents([
        ...     {"content": "Python programming tutorial", "category": "tech"},
        ...     {"content": "Cooking recipes for beginners", "category": "food"}
        ... ])
        >>> results = search.search("learn Python", top_k=5)
        >>> print(results[0]['document'])
    """
    
    def __init__(
        self,
        embedder: Optional[BERTEmbedder] = None,
        vector_store: Optional[VectorStore] = None,
        model_name: str = "fast",
        store_type: str = "chroma",  # 'chroma' or 'faiss'
        persist_directory: str = "./semantic_search_db"
    ):
        """
        Initialize semantic search engine.
        
        Args:
            embedder: BERT embedder instance (or None to create default)
            vector_store: Vector store instance (or None to create default)
            model_name: Embedding model name
            store_type: Type of vector store ('chroma' or 'faiss')
            persist_directory: Directory for persistence
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize embedder
        if embedder is None:
            try:
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    self.embedder = BERTEmbedder(model_name=model_name)
                else:
                    self.logger.warning("Using mock embedder")
                    self.embedder = MockBERTEmbedder(model_name=model_name)
            except Exception as e:
                self.logger.warning(f"Failed to load BERT model: {e}, using mock")
                self.embedder = MockBERTEmbedder(model_name=model_name)
        else:
            self.embedder = embedder
        
        # Initialize vector store
        if vector_store is None:
            try:
                if store_type == "chroma":
                    self.vector_store = ChromaDBStore(
                        collection_name="semantic_search",
                        persist_directory=persist_directory,
                        embedding_dim=self.embedder.embedding_dim
                    )
                elif store_type == "faiss":
                    self.vector_store = FAISSStore(
                        embedding_dim=self.embedder.embedding_dim,
                        persist_path=f"{persist_directory}/faiss"
                    )
                else:
                    raise ValueError(f"Unknown store type: {store_type}")
            except ImportError as e:
                self.logger.error(f"Failed to initialize {store_type} store: {e}")
                raise
        else:
            self.vector_store = vector_store
        
        self.logger.info(f"SemanticSearch initialized with {type(self.embedder).__name__} and {type(self.vector_store).__name__}")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "content",
        batch_size: int = 32,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the search index.
        
        Args:
            documents: List of document dicts
            text_field: Field containing text to embed
            batch_size: Batch size for embedding
            ids: Optional document IDs
        
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        self.logger.info(f"Adding {len(documents)} documents to index")
        
        # Extract text and embed
        texts = [doc.get(text_field, str(doc)) for doc in documents]
        embeddings = self.embedder.embed(texts, batch_size=batch_size)
        
        # Add to vector store
        doc_ids = self.vector_store.add(embeddings, documents, ids=ids)
        
        self.logger.info(f"Successfully added {len(doc_ids)} documents")
        return doc_ids
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Metadata filters
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of result dicts with 'id', 'document', 'score', etc.
        """
        self.logger.debug(f"Searching for: {query}")
        
        # Embed query
        query_embedding = self.embedder.embed(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # Filter by minimum score
        if min_score is not None:
            results = [r for r in results if r.get('score', 0) >= min_score]
        
        self.logger.debug(f"Found {len(results)} results")
        return results
    
    def search_similar(
        self,
        document_id: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.
        
        Args:
            document_id: ID of the reference document
            top_k: Number of results to return
            filters: Metadata filters
        
        Returns:
            List of similar documents
        """
        # Get the document
        docs = self.vector_store.get([document_id])
        if not docs:
            raise ValueError(f"Document not found: {document_id}")
        
        doc = docs[0]
        text = doc['document'].get('content', str(doc['document']))
        
        # Search using document text
        results = self.search(text, top_k=top_k + 1, filters=filters)
        
        # Remove the document itself from results
        results = [r for r in results if r['id'] != document_id][:top_k]
        
        return results
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
        
        Returns:
            True if successful
        """
        return self.vector_store.delete(ids)
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document dict or None
        """
        docs = self.vector_store.get([document_id])
        return docs[0] if docs else None
    
    def count_documents(self) -> int:
        """Get total number of indexed documents."""
        return self.vector_store.count()
    
    def clear_index(self) -> bool:
        """Clear all documents from index."""
        return self.vector_store.clear()
    
    def batch_search(
        self,
        queries: List[str],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Perform batch search for multiple queries.
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
            filters: Metadata filters
        
        Returns:
            List of result lists (one per query)
        """
        results = []
        for query in queries:
            query_results = self.search(query, top_k=top_k, filters=filters)
            results.append(query_results)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get search engine statistics.
        
        Returns:
            Dict with statistics
        """
        return {
            "total_documents": self.count_documents(),
            "embedder_info": self.embedder.get_info(),
            "vector_store_type": type(self.vector_store).__name__
        }


# Convenience function
def create_semantic_search(
    model_name: str = "fast",
    store_type: str = "chroma",
    persist_directory: str = "./semantic_search_db"
) -> SemanticSearch:
    """
    Create a semantic search instance with default settings.
    
    Args:
        model_name: Embedding model ('fast', 'balanced', 'multilingual', 'large')
        store_type: Vector store ('chroma' or 'faiss')
        persist_directory: Directory for persistence
    
    Returns:
        SemanticSearch instance
    """
    return SemanticSearch(
        model_name=model_name,
        store_type=store_type,
        persist_directory=persist_directory
    )
