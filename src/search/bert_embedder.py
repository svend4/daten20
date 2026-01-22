"""
BERT Embedder - Text embedding service using Sentence-BERT

Provides text embedding capabilities using pre-trained BERT models
for semantic search and similarity computations.
"""

import logging
from typing import List, Union, Optional, Dict, Any
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available. Install with: pip install sentence-transformers")


class BERTEmbedder:
    """
    BERT-based text embedder using Sentence-BERT models.
    
    Features:
    - Multiple model support (multilingual, domain-specific)
    - Batch processing
    - GPU acceleration (if available)
    - Embedding caching
    
    Examples:
        >>> embedder = BERTEmbedder(model_name='all-MiniLM-L6-v2')
        >>> embeddings = embedder.embed(["Hello world", "How are you?"])
        >>> print(embeddings.shape)  # (2, 384)
    """
    
    # Pre-configured models
    MODELS = {
        "fast": "all-MiniLM-L6-v2",           # 384 dims, fastest
        "balanced": "all-mpnet-base-v2",      # 768 dims, good balance
        "multilingual": "paraphrase-multilingual-MiniLM-L12-v2",  # 384 dims
        "large": "all-mpnet-base-v2",         # 768 dims, best quality
    }
    
    def __init__(
        self,
        model_name: str = "fast",
        device: Optional[str] = None,
        cache_folder: Optional[str] = None,
        normalize_embeddings: bool = True
    ):
        """
        Initialize BERT embedder.
        
        Args:
            model_name: Model name or preset ('fast', 'balanced', 'multilingual', 'large')
            device: Device to use ('cuda', 'cpu', or None for auto)
            cache_folder: Folder to cache models
            normalize_embeddings: Whether to normalize embeddings (recommended)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        self.logger = logging.getLogger(__name__)
        
        # Resolve model name
        if model_name in self.MODELS:
            actual_model = self.MODELS[model_name]
            self.logger.info(f"Using preset '{model_name}': {actual_model}")
        else:
            actual_model = model_name
            self.logger.info(f"Using custom model: {actual_model}")
        
        self.model_name = actual_model
        self.normalize_embeddings = normalize_embeddings
        
        # Load model
        self.logger.info(f"Loading model: {actual_model}")
        self.model = SentenceTransformer(
            actual_model,
            device=device,
            cache_folder=cache_folder
        )
        
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def embed(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        convert_to_numpy: bool = True
    ) -> np.ndarray:
        """
        Embed text(s) into dense vectors.
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            show_progress_bar: Show progress bar for large batches
            convert_to_numpy: Return numpy array (vs torch tensor)
        
        Returns:
            Embeddings as numpy array of shape (n_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        self.logger.debug(f"Embedding {len(texts)} texts")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=convert_to_numpy,
            normalize_embeddings=self.normalize_embeddings
        )
        
        return embeddings
    
    def embed_documents(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "content",
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Embed documents from a list of dicts.
        
        Args:
            documents: List of document dicts
            text_field: Field name containing text to embed
            batch_size: Batch size for processing
        
        Returns:
            Embeddings array
        """
        texts = [doc.get(text_field, "") for doc in documents]
        return self.embed(texts, batch_size=batch_size)
    
    def similarity(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between embeddings.
        
        Args:
            embeddings1: First set of embeddings (n1, dim)
            embeddings2: Second set of embeddings (n2, dim)
        
        Returns:
            Similarity matrix (n1, n2)
        """
        # Ensure 2D
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        
        # Cosine similarity = dot product (if normalized)
        similarity = np.dot(embeddings1, embeddings2.T)
        
        return similarity
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "normalize_embeddings": self.normalize_embeddings,
            "device": str(self.model.device)
        }


# Mock class for when sentence-transformers is not available
class MockBERTEmbedder:
    """Mock embedder for testing without sentence-transformers."""
    
    def __init__(self, model_name: str = "fast", **kwargs):
        self.model_name = model_name
        self.embedding_dim = 384
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using mock embedder - install sentence-transformers for real embeddings")
    
    def embed(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Generate random embeddings."""
        if isinstance(texts, str):
            texts = [texts]
        # Return random normalized vectors
        embeddings = np.random.randn(len(texts), self.embedding_dim)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings
    
    def embed_documents(self, documents: List[Dict[str, Any]], **kwargs) -> np.ndarray:
        """Generate random embeddings for documents."""
        return self.embed([str(d) for d in documents])
    
    def similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """Compute similarity."""
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        return np.dot(embeddings1, embeddings2.T)
    
    def get_info(self) -> Dict[str, Any]:
        """Get info."""
        return {
            "model_name": self.model_name + " (mock)",
            "embedding_dim": self.embedding_dim,
            "mock": True
        }
