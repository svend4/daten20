"""
Vector Store - Storage and retrieval for vector embeddings

Supports multiple vector database backends:
- ChromaDB: Persistent vector storage with metadata
- FAISS: Fast similarity search
- In-memory: For testing and small datasets
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np
import json
import os

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("chromadb not available. Install with: pip install chromadb")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("faiss not available. Install with: pip install faiss-cpu")


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def add(
        self,
        embeddings: np.ndarray,
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add embeddings and documents to store."""
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        pass
    
    @abstractmethod
    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get documents by IDs."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total number of documents."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all documents."""
        pass


class ChromaDBStore(VectorStore):
    """
    ChromaDB-based vector store.
    
    Features:
    - Persistent storage
    - Metadata filtering
    - Automatic indexing
    - HNSW algorithm for fast search
    """
    
    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: str = "./chroma_db",
        embedding_dim: int = 384
    ):
        """
        Initialize ChromaDB store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
            embedding_dim: Dimension of embeddings
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
        
        self.logger = logging.getLogger(__name__)
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_dim = embedding_dim
        
        # Create client
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        self.logger.info(f"ChromaDB collection '{collection_name}' initialized at {persist_directory}")
    
    def add(
        self,
        embeddings: np.ndarray,
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add embeddings and documents."""
        if embeddings.shape[0] != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}_{hash(str(doc))}" for i, doc in enumerate(documents)]
        
        # Prepare documents and metadata
        doc_texts = []
        metadatas = []
        
        for doc in documents:
            # Extract text content
            text = doc.get("content", doc.get("text", str(doc)))
            doc_texts.append(text)
            
            # Extract metadata (chromadb requires dict)
            metadata = {k: v for k, v in doc.items() if k not in ["content", "text"]}
            # Convert non-string values to JSON strings
            for key, value in metadata.items():
                if not isinstance(value, (str, int, float, bool)):
                    metadata[key] = json.dumps(value)
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=doc_texts,
            metadatas=metadatas,
            ids=ids
        )
        
        self.logger.info(f"Added {len(ids)} documents to ChromaDB")
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Query collection
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            where=filters  # Metadata filters
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            result = {
                "id": results['ids'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "score": 1.0 - results['distances'][0][i]  # Convert distance to similarity
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            self.collection.delete(ids=ids)
            self.logger.info(f"Deleted {len(ids)} documents from ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting documents: {e}")
            return False
    
    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get documents by IDs."""
        results = self.collection.get(ids=ids)
        
        formatted_results = []
        for i in range(len(results['ids'])):
            result = {
                "id": results['ids'][i],
                "document": results['documents'][i],
                "metadata": results['metadatas'][i],
                "embedding": results.get('embeddings', [None])[i]
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def count(self) -> int:
        """Get total number of documents."""
        return self.collection.count()
    
    def clear(self) -> bool:
        """Clear all documents."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info(f"Cleared collection '{self.collection_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing collection: {e}")
            return False


class FAISSStore(VectorStore):
    """
    FAISS-based vector store.
    
    Features:
    - Fast similarity search
    - Memory efficient
    - Multiple index types
    - GPU support (if available)
    """
    
    def __init__(
        self,
        embedding_dim: int = 384,
        index_type: str = "flat",  # 'flat', 'ivf', 'hnsw'
        persist_path: Optional[str] = None
    ):
        """
        Initialize FAISS store.
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of FAISS index
            persist_path: Path to save/load index
        """
        if not FAISS_AVAILABLE:
            raise ImportError("faiss not installed. Install with: pip install faiss-cpu")
        
        self.logger = logging.getLogger(__name__)
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.persist_path = persist_path
        
        # Create index
        if index_type == "flat":
            self.index = faiss.IndexFlatL2(embedding_dim)
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
        elif index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(embedding_dim, 32)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        # Storage for documents and IDs
        self.documents = []
        self.ids = []
        self.id_to_index = {}
        
        # Load existing index if available
        if persist_path and os.path.exists(persist_path):
            self._load()
        
        self.logger.info(f"FAISS index initialized ({index_type}, dim={embedding_dim})")
    
    def add(
        self,
        embeddings: np.ndarray,
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add embeddings and documents."""
        if embeddings.shape[0] != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{len(self.documents) + i}" for i in range(len(documents))]
        
        # Add to FAISS index
        embeddings = embeddings.astype(np.float32)
        self.index.add(embeddings)
        
        # Store documents and IDs
        start_idx = len(self.documents)
        for i, (doc, doc_id) in enumerate(zip(documents, ids)):
            self.documents.append(doc)
            self.ids.append(doc_id)
            self.id_to_index[doc_id] = start_idx + i
        
        self.logger.info(f"Added {len(ids)} documents to FAISS")
        
        # Persist if path provided
        if self.persist_path:
            self._save()
        
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_embedding = query_embedding.astype(np.float32)
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0 or idx >= len(self.documents):
                continue
            
            doc = self.documents[idx]
            doc_id = self.ids[idx]
            
            # Apply filters if provided
            if filters:
                skip = False
                for key, value in filters.items():
                    if doc.get(key) != value:
                        skip = True
                        break
                if skip:
                    continue
            
            result = {
                "id": doc_id,
                "document": doc,
                "distance": float(dist),
                "score": 1.0 / (1.0 + float(dist))  # Convert distance to score
            }
            results.append(result)
        
        return results
    
    def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs (FAISS doesn't support direct deletion)."""
        self.logger.warning("FAISS doesn't support efficient deletion. Rebuilding index...")
        
        # Remove documents
        indices_to_remove = set()
        for doc_id in ids:
            if doc_id in self.id_to_index:
                indices_to_remove.add(self.id_to_index[doc_id])
        
        # Rebuild without deleted docs
        new_documents = []
        new_ids = []
        new_embeddings = []
        
        for i, (doc, doc_id) in enumerate(zip(self.documents, self.ids)):
            if i not in indices_to_remove:
                new_documents.append(doc)
                new_ids.append(doc_id)
                # Note: We can't retrieve embeddings from FAISS easily
                # This is a limitation - consider using ChromaDB for better delete support
        
        self.documents = new_documents
        self.ids = new_ids
        self.id_to_index = {doc_id: i for i, doc_id in enumerate(new_ids)}
        
        # Note: Index would need to be rebuilt with new embeddings
        # This is a simplified implementation
        self.logger.warning(f"Deleted {len(ids)} document references (index needs rebuild)")
        return True
    
    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get documents by IDs."""
        results = []
        for doc_id in ids:
            if doc_id in self.id_to_index:
                idx = self.id_to_index[doc_id]
                results.append({
                    "id": doc_id,
                    "document": self.documents[idx],
                    "metadata": {}
                })
        return results
    
    def count(self) -> int:
        """Get total number of documents."""
        return self.index.ntotal
    
    def clear(self) -> bool:
        """Clear all documents."""
        self.index.reset()
        self.documents = []
        self.ids = []
        self.id_to_index = {}
        self.logger.info("Cleared FAISS index")
        return True
    
    def _save(self):
        """Save index and metadata to disk."""
        if not self.persist_path:
            return
        
        # Save FAISS index
        faiss.write_index(self.index, f"{self.persist_path}.index")
        
        # Save metadata
        metadata = {
            "documents": self.documents,
            "ids": self.ids,
            "id_to_index": self.id_to_index
        }
        with open(f"{self.persist_path}.meta", "w") as f:
            json.dump(metadata, f)
        
        self.logger.info(f"Saved FAISS index to {self.persist_path}")
    
    def _load(self):
        """Load index and metadata from disk."""
        if not self.persist_path or not os.path.exists(f"{self.persist_path}.index"):
            return
        
        # Load FAISS index
        self.index = faiss.read_index(f"{self.persist_path}.index")
        
        # Load metadata
        with open(f"{self.persist_path}.meta", "r") as f:
            metadata = json.load(f)
        
        self.documents = metadata["documents"]
        self.ids = metadata["ids"]
        self.id_to_index = metadata["id_to_index"]
        
        self.logger.info(f"Loaded FAISS index from {self.persist_path}")
