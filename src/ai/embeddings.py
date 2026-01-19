"""
Embeddings & Vector Search Module

Vector embeddings for semantic search, document similarity, and clustering.
Supports multiple embedding models and vector databases.

Part of v3.5 AI/ML Services implementation.
"""

import hashlib
import logging
import math
import pickle
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class EmbeddingModel(Enum):
    """Embedding model types."""

    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"
    OPENAI_ADA = "text-embedding-ada-002"
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    CUSTOM = "custom"


@dataclass
class Embedding:
    """Vector embedding."""

    vector: List[float]
    model: str
    dimension: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Document for embedding."""

    doc_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Search result with similarity score."""

    doc_id: str
    score: float
    document: Optional[Document] = None
    distance: float = 0.0


@dataclass
class ClusterResult:
    """Clustering result."""

    cluster_id: int
    documents: List[str]
    centroid: List[float]
    size: int


class VectorMath:
    """Vector mathematics utilities."""

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    @staticmethod
    def manhattan_distance(vec1: List[float], vec2: List[float]) -> float:
        """Calculate Manhattan distance between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        return sum(abs(a - b) for a, b in zip(vec1, vec2))

    @staticmethod
    def dot_product(vec1: List[float], vec2: List[float]) -> float:
        """Calculate dot product of two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        return sum(a * b for a, b in zip(vec1, vec2))

    @staticmethod
    def normalize(vector: List[float]) -> List[float]:
        """Normalize vector to unit length."""
        magnitude = math.sqrt(sum(v * v for v in vector))

        if magnitude == 0:
            return vector

        return [v / magnitude for v in vector]

    @staticmethod
    def add(vec1: List[float], vec2: List[float]) -> List[float]:
        """Add two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        return [a + b for a, b in zip(vec1, vec2)]

    @staticmethod
    def subtract(vec1: List[float], vec2: List[float]) -> List[float]:
        """Subtract vec2 from vec1."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        return [a - b for a, b in zip(vec1, vec2)]

    @staticmethod
    def scale(vector: List[float], scalar: float) -> List[float]:
        """Scale vector by scalar."""
        return [v * scalar for v in vector]


class EmbeddingGenerator:
    """Generate embeddings for text."""

    def __init__(self, model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS):
        self.model = model
        self.dimension = self._get_dimension()

    def _get_dimension(self) -> int:
        """Get embedding dimension for model."""
        dimensions = {
            EmbeddingModel.OPENAI_SMALL: 1536,
            EmbeddingModel.OPENAI_LARGE: 3072,
            EmbeddingModel.OPENAI_ADA: 1536,
            EmbeddingModel.SENTENCE_TRANSFORMERS: 384,
            EmbeddingModel.CUSTOM: 768,
        }
        return dimensions.get(self.model, 384)

    async def embed(self, text: str) -> Embedding:
        """Generate embedding for text."""
        # Mock implementation - in production would use actual models
        vector = self._generate_mock_embedding(text)

        return Embedding(vector=vector, model=self.model.value, dimension=self.dimension)

    async def embed_batch(self, texts: List[str]) -> List[Embedding]:
        """Generate embeddings for multiple texts."""
        embeddings = []

        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)

        return embeddings

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding (deterministic based on text)."""
        # Hash text to generate deterministic vector
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to vector
        vector = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            value = (hash_bytes[byte_idx] / 255.0) * 2 - 1  # Normalize to [-1, 1]
            vector.append(value)

        # Add some variation based on text characteristics
        word_count = len(text.split())
        char_count = len(text)

        for i in range(min(10, self.dimension)):
            vector[i] += (word_count % 10) / 20.0
            vector[i] += (char_count % 10) / 20.0

        # Normalize
        return VectorMath.normalize(vector)


class VectorIndex:
    """Simple vector index for similarity search."""

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
        self.documents: Dict[str, Document] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def add(self, doc_id: str, vector: List[float], document: Optional[Document] = None):
        """Add vector to index."""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match index dimension {self.dimension}")

        self.vectors[doc_id] = vector

        if document:
            self.documents[doc_id] = document
            self.metadata[doc_id] = document.metadata

    def add_batch(self, doc_ids: List[str], vectors: List[List[float]], documents: Optional[List[Document]] = None):
        """Add multiple vectors to index."""
        for i, doc_id in enumerate(doc_ids):
            doc = documents[i] if documents else None
            self.add(doc_id, vectors[i], doc)

    def search(
        self, query_vector: List[float], top_k: int = 10, filter_fn: Optional[callable] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension doesn't match index dimension")

        # Calculate similarities
        results = []

        for doc_id, vector in self.vectors.items():
            # Apply filter if provided
            if filter_fn and not filter_fn(self.metadata.get(doc_id, {})):
                continue

            similarity = VectorMath.cosine_similarity(query_vector, vector)
            distance = VectorMath.euclidean_distance(query_vector, vector)

            results.append(
                SearchResult(doc_id=doc_id, score=similarity, document=self.documents.get(doc_id), distance=distance)
            )

        # Sort by similarity (descending)
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:top_k]

    def delete(self, doc_id: str):
        """Remove vector from index."""
        self.vectors.pop(doc_id, None)
        self.documents.pop(doc_id, None)
        self.metadata.pop(doc_id, None)

    def size(self) -> int:
        """Get number of vectors in index."""
        return len(self.vectors)

    def save(self, filepath: str):
        """Save index to file."""
        data = {
            "dimension": self.dimension,
            "vectors": self.vectors,
            "documents": self.documents,
            "metadata": self.metadata,
        }

        with open(filepath, "wb") as f:
            pickle.dump(data, f)

        logger.info(f"Index saved to {filepath}")

    def load(self, filepath: str):
        """Load index from file."""
        with open(filepath, "rb") as f:
            data = pickle.load(f)

        self.dimension = data["dimension"]
        self.vectors = data["vectors"]
        self.documents = data["documents"]
        self.metadata = data["metadata"]

        logger.info(f"Index loaded from {filepath} with {self.size()} vectors")


class SemanticSearch:
    """Semantic search using vector embeddings."""

    def __init__(self, embedding_model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS):
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.index = VectorIndex(self.embedding_generator.dimension)

    async def index_documents(self, documents: List[Document]):
        """Index documents for semantic search."""
        logger.info(f"Indexing {len(documents)} documents...")

        # Generate embeddings
        texts = [doc.text for doc in documents]
        embeddings = await self.embedding_generator.embed_batch(texts)

        # Add to index
        doc_ids = [doc.doc_id for doc in documents]
        vectors = [emb.vector for emb in embeddings]

        self.index.add_batch(doc_ids, vectors, documents)

        logger.info(f"Indexed {len(documents)} documents")

    async def search(
        self, query: str, top_k: int = 10, filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for documents similar to query."""
        # Generate query embedding
        query_embedding = await self.embedding_generator.embed(query)

        # Define filter function
        filter_fn = None
        if filter_metadata:

            def filter_fn(metadata):
                return all(metadata.get(key) == value for key, value in filter_metadata.items())

        # Search index
        results = self.index.search(query_embedding.vector, top_k=top_k, filter_fn=filter_fn)

        return results

    def save_index(self, filepath: str):
        """Save index to file."""
        self.index.save(filepath)

    def load_index(self, filepath: str):
        """Load index from file."""
        self.index.load(filepath)


class DocumentSimilarity:
    """Calculate similarity between documents."""

    def __init__(self, embedding_model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS):
        self.embedding_generator = EmbeddingGenerator(embedding_model)

    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Generate embeddings
        emb1 = await self.embedding_generator.embed(text1)
        emb2 = await self.embedding_generator.embed(text2)

        # Calculate cosine similarity
        similarity = VectorMath.cosine_similarity(emb1.vector, emb2.vector)

        return similarity

    async def find_similar_documents(
        self, target_text: str, candidate_texts: List[str], top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Find most similar documents from candidates."""
        # Generate embeddings
        target_emb = await self.embedding_generator.embed(target_text)
        candidate_embs = await self.embedding_generator.embed_batch(candidate_texts)

        # Calculate similarities
        similarities = []
        for i, candidate_emb in enumerate(candidate_embs):
            similarity = VectorMath.cosine_similarity(target_emb.vector, candidate_emb.vector)
            similarities.append((i, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]


class KMeansClustering:
    """K-means clustering for document vectors."""

    def __init__(self, n_clusters: int = 5, max_iterations: int = 100):
        self.n_clusters = n_clusters
        self.max_iterations = max_iterations
        self.centroids: List[List[float]] = []
        self.labels: List[int] = []

    def fit(self, vectors: List[List[float]]) -> List[ClusterResult]:
        """Cluster vectors using k-means."""
        if len(vectors) < self.n_clusters:
            raise ValueError("Number of vectors must be >= number of clusters")

        dimension = len(vectors[0])

        # Initialize centroids randomly
        import random

        self.centroids = random.sample(vectors, self.n_clusters)

        # Iterate
        for iteration in range(self.max_iterations):
            # Assign points to nearest centroid
            new_labels = []
            for vector in vectors:
                distances = [VectorMath.euclidean_distance(vector, centroid) for centroid in self.centroids]
                nearest_cluster = distances.index(min(distances))
                new_labels.append(nearest_cluster)

            # Check convergence
            if iteration > 0 and new_labels == self.labels:
                logger.info(f"K-means converged after {iteration} iterations")
                break

            self.labels = new_labels

            # Update centroids
            new_centroids = []
            for cluster_id in range(self.n_clusters):
                cluster_vectors = [vectors[i] for i, label in enumerate(self.labels) if label == cluster_id]

                if cluster_vectors:
                    # Calculate mean
                    centroid = [
                        sum(vec[dim] for vec in cluster_vectors) / len(cluster_vectors) for dim in range(dimension)
                    ]
                    new_centroids.append(centroid)
                else:
                    # Keep old centroid if cluster is empty
                    new_centroids.append(self.centroids[cluster_id])

            self.centroids = new_centroids

        # Create cluster results
        results = []
        for cluster_id in range(self.n_clusters):
            doc_ids = [str(i) for i, label in enumerate(self.labels) if label == cluster_id]

            results.append(
                ClusterResult(
                    cluster_id=cluster_id, documents=doc_ids, centroid=self.centroids[cluster_id], size=len(doc_ids)
                )
            )

        return results

    def predict(self, vector: List[float]) -> int:
        """Predict cluster for new vector."""
        if not self.centroids:
            raise ValueError("Model not trained yet")

        distances = [VectorMath.euclidean_distance(vector, centroid) for centroid in self.centroids]

        return distances.index(min(distances))


class DocumentClustering:
    """Cluster documents by semantic similarity."""

    def __init__(self, n_clusters: int = 5, embedding_model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS):
        self.n_clusters = n_clusters
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.clusterer = KMeansClustering(n_clusters)

    async def cluster_documents(self, documents: List[Document]) -> Dict[int, List[Document]]:
        """Cluster documents by content similarity."""
        logger.info(f"Clustering {len(documents)} documents into {self.n_clusters} clusters...")

        # Generate embeddings
        texts = [doc.text for doc in documents]
        embeddings = await self.embedding_generator.embed_batch(texts)
        vectors = [emb.vector for emb in embeddings]

        # Cluster
        cluster_results = self.clusterer.fit(vectors)

        # Group documents by cluster
        clusters: Dict[int, List[Document]] = defaultdict(list)

        for doc_idx, cluster_id in enumerate(self.clusterer.labels):
            clusters[cluster_id].append(documents[doc_idx])

        logger.info(f"Clustering complete. Cluster sizes: {[len(docs) for docs in clusters.values()]}")

        return dict(clusters)

    async def predict_cluster(self, document: Document) -> int:
        """Predict cluster for new document."""
        embedding = await self.embedding_generator.embed(document.text)
        return self.clusterer.predict(embedding.vector)


class EmbeddingService:
    """Main embedding service."""

    def __init__(self, embedding_model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS):
        self.embedding_model = embedding_model
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.semantic_search = SemanticSearch(embedding_model)
        self.similarity = DocumentSimilarity(embedding_model)

    async def embed_text(self, text: str) -> Embedding:
        """Generate embedding for text."""
        return await self.embedding_generator.embed(text)

    async def embed_texts(self, texts: List[str]) -> List[Embedding]:
        """Generate embeddings for multiple texts."""
        return await self.embedding_generator.embed_batch(texts)

    async def search_similar(self, query: str, documents: List[Document], top_k: int = 10) -> List[SearchResult]:
        """Search for similar documents."""
        # Index documents if not already indexed
        if self.semantic_search.index.size() == 0:
            await self.semantic_search.index_documents(documents)

        return await self.semantic_search.search(query, top_k=top_k)

    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between texts."""
        return await self.similarity.calculate_similarity(text1, text2)

    async def cluster_documents(self, documents: List[Document], n_clusters: int = 5) -> Dict[int, List[Document]]:
        """Cluster documents by similarity."""
        clusterer = DocumentClustering(n_clusters, self.embedding_model)
        return await clusterer.cluster_documents(documents)


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(embedding_model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS) -> EmbeddingService:
    """Get or create embedding service."""
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(embedding_model)

    return _embedding_service
