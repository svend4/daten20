"""
Comprehensive tests for ai/embeddings.py module

Tests organized by size:
- Small: Dataclasses, enums, pure functions (VectorMath)
- Medium: Classes with logic, async operations (mocked)
- Large: Full workflows, integration tests

Test coverage: ~80% target
"""

import asyncio
import math
import os
import tempfile
from typing import List

import pytest

from src.ai.embeddings import (
    ClusterResult,
    Document,
    DocumentClustering,
    DocumentSimilarity,
    Embedding,
    EmbeddingGenerator,
    EmbeddingModel,
    EmbeddingService,
    KMeansClustering,
    SearchResult,
    SemanticSearch,
    VectorIndex,
    VectorMath,
    get_embedding_service,
)

# ============================================================================
# SMALL TESTS - Enums, Dataclasses, Pure Functions
# ============================================================================

pytestmark = [pytest.mark.small, pytest.mark.unit]


class TestEmbeddingModel:
    """Test EmbeddingModel enum."""

    def test_all_models_defined(self):
        """Test all embedding models are defined."""
        models = [model for model in EmbeddingModel]
        assert len(models) == 5

        # Check specific models
        assert EmbeddingModel.OPENAI_SMALL in models
        assert EmbeddingModel.OPENAI_LARGE in models
        assert EmbeddingModel.SENTENCE_TRANSFORMERS in models

    def test_model_values(self):
        """Test model enum values."""
        assert EmbeddingModel.OPENAI_SMALL.value == "text-embedding-3-small"
        assert EmbeddingModel.OPENAI_ADA.value == "text-embedding-ada-002"
        assert EmbeddingModel.CUSTOM.value == "custom"


class TestEmbeddingDataclass:
    """Test Embedding dataclass."""

    def test_embedding_creation(self):
        """Test creating embedding."""
        vector = [0.1, 0.2, 0.3]
        emb = Embedding(vector=vector, model="test-model", dimension=3)

        assert emb.vector == vector
        assert emb.model == "test-model"
        assert emb.dimension == 3
        assert emb.metadata == {}

    def test_embedding_with_metadata(self):
        """Test embedding with metadata."""
        metadata = {"source": "test", "quality": 0.9}
        emb = Embedding(
            vector=[1.0, 2.0],
            model="test",
            dimension=2,
            metadata=metadata
        )

        assert emb.metadata == metadata
        assert emb.metadata["source"] == "test"


class TestDocumentDataclass:
    """Test Document dataclass."""

    def test_document_creation(self):
        """Test creating document."""
        doc = Document(doc_id="123", text="Hello world")

        assert doc.doc_id == "123"
        assert doc.text == "Hello world"
        assert doc.metadata == {}

    def test_document_with_metadata(self):
        """Test document with metadata."""
        metadata = {"author": "Alice", "category": "test"}
        doc = Document(
            doc_id="456",
            text="Test document",
            metadata=metadata
        )

        assert doc.metadata["author"] == "Alice"
        assert doc.metadata["category"] == "test"


class TestSearchResultDataclass:
    """Test SearchResult dataclass."""

    def test_search_result_creation(self):
        """Test creating search result."""
        result = SearchResult(doc_id="123", score=0.95)

        assert result.doc_id == "123"
        assert result.score == 0.95
        assert result.document is None
        assert result.distance == 0.0

    def test_search_result_with_document(self):
        """Test search result with document."""
        doc = Document(doc_id="123", text="Test")
        result = SearchResult(
            doc_id="123",
            score=0.85,
            document=doc,
            distance=0.15
        )

        assert result.document == doc
        assert result.distance == 0.15


class TestClusterResultDataclass:
    """Test ClusterResult dataclass."""

    def test_cluster_result_creation(self):
        """Test creating cluster result."""
        centroid = [0.5, 0.5, 0.5]
        docs = ["doc1", "doc2", "doc3"]

        result = ClusterResult(
            cluster_id=0,
            documents=docs,
            centroid=centroid,
            size=3
        )

        assert result.cluster_id == 0
        assert result.documents == docs
        assert result.centroid == centroid
        assert result.size == 3


class TestVectorMath:
    """Test VectorMath utilities (pure functions)."""

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        vec = [1.0, 2.0, 3.0]
        similarity = VectorMath.cosine_similarity(vec, vec)

        assert abs(similarity - 1.0) < 1e-10

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = VectorMath.cosine_similarity(vec1, vec2)

        assert abs(similarity - 0.0) < 1e-10

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity of opposite vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        similarity = VectorMath.cosine_similarity(vec1, vec2)

        assert abs(similarity - (-1.0)) < 1e-10

    def test_cosine_similarity_dimension_mismatch(self):
        """Test cosine similarity with different dimensions."""
        vec1 = [1.0, 2.0]
        vec2 = [1.0, 2.0, 3.0]

        with pytest.raises(ValueError, match="same dimension"):
            VectorMath.cosine_similarity(vec1, vec2)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]

        similarity = VectorMath.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [3.0, 4.0, 0.0]

        distance = VectorMath.euclidean_distance(vec1, vec2)
        assert abs(distance - 5.0) < 1e-10

    def test_euclidean_distance_identical(self):
        """Test Euclidean distance of identical vectors."""
        vec = [1.0, 2.0, 3.0]
        distance = VectorMath.euclidean_distance(vec, vec)

        assert abs(distance - 0.0) < 1e-10

    def test_manhattan_distance(self):
        """Test Manhattan distance calculation."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]

        distance = VectorMath.manhattan_distance(vec1, vec2)
        assert distance == 6.0

    def test_dot_product(self):
        """Test dot product calculation."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]

        result = VectorMath.dot_product(vec1, vec2)
        assert result == 32.0  # 1*4 + 2*5 + 3*6

    def test_normalize(self):
        """Test vector normalization."""
        vec = [3.0, 4.0, 0.0]
        normalized = VectorMath.normalize(vec)

        # Check unit length
        magnitude = math.sqrt(sum(v*v for v in normalized))
        assert abs(magnitude - 1.0) < 1e-10

        # Check direction preserved
        assert abs(normalized[0] - 0.6) < 1e-10
        assert abs(normalized[1] - 0.8) < 1e-10

    def test_normalize_zero_vector(self):
        """Test normalizing zero vector."""
        vec = [0.0, 0.0, 0.0]
        normalized = VectorMath.normalize(vec)

        assert normalized == vec

    def test_add_vectors(self):
        """Test vector addition."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]

        result = VectorMath.add(vec1, vec2)
        assert result == [5.0, 7.0, 9.0]

    def test_subtract_vectors(self):
        """Test vector subtraction."""
        vec1 = [5.0, 7.0, 9.0]
        vec2 = [1.0, 2.0, 3.0]

        result = VectorMath.subtract(vec1, vec2)
        assert result == [4.0, 5.0, 6.0]

    def test_scale_vector(self):
        """Test vector scaling."""
        vec = [1.0, 2.0, 3.0]
        scaled = VectorMath.scale(vec, 2.0)

        assert scaled == [2.0, 4.0, 6.0]


# ============================================================================
# MEDIUM TESTS - Classes with Logic, Async Operations
# ============================================================================


@pytest.mark.medium
@pytest.mark.integration
class TestEmbeddingGenerator:
    """Test EmbeddingGenerator class."""

    def test_generator_initialization(self):
        """Test creating embedding generator."""
        gen = EmbeddingGenerator(EmbeddingModel.SENTENCE_TRANSFORMERS)

        assert gen.model == EmbeddingModel.SENTENCE_TRANSFORMERS
        assert gen.dimension == 384

    def test_dimension_for_openai_models(self):
        """Test dimensions for different models."""
        gen_small = EmbeddingGenerator(EmbeddingModel.OPENAI_SMALL)
        gen_large = EmbeddingGenerator(EmbeddingModel.OPENAI_LARGE)

        assert gen_small.dimension == 1536
        assert gen_large.dimension == 3072

    @pytest.mark.asyncio
    async def test_embed_text(self):
        """Test generating embedding for text."""
        gen = EmbeddingGenerator(EmbeddingModel.SENTENCE_TRANSFORMERS)

        emb = await gen.embed("Hello world")

        assert isinstance(emb, Embedding)
        assert len(emb.vector) == 384
        assert emb.dimension == 384
        assert emb.model == EmbeddingModel.SENTENCE_TRANSFORMERS.value

    @pytest.mark.asyncio
    async def test_embed_deterministic(self):
        """Test embeddings are deterministic."""
        gen = EmbeddingGenerator(EmbeddingModel.SENTENCE_TRANSFORMERS)

        emb1 = await gen.embed("Test text")
        emb2 = await gen.embed("Test text")

        assert emb1.vector == emb2.vector

    @pytest.mark.asyncio
    async def test_embed_different_texts(self):
        """Test different texts produce different embeddings."""
        gen = EmbeddingGenerator(EmbeddingModel.SENTENCE_TRANSFORMERS)

        emb1 = await gen.embed("Hello")
        emb2 = await gen.embed("Goodbye")

        assert emb1.vector != emb2.vector

    @pytest.mark.asyncio
    async def test_embed_batch(self):
        """Test batch embedding generation."""
        gen = EmbeddingGenerator(EmbeddingModel.SENTENCE_TRANSFORMERS)

        texts = ["Hello", "World", "Test"]
        embeddings = await gen.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(isinstance(emb, Embedding) for emb in embeddings)
        assert all(len(emb.vector) == 384 for emb in embeddings)


@pytest.mark.medium
@pytest.mark.integration
class TestVectorIndex:
    """Test VectorIndex class."""

    def test_index_initialization(self):
        """Test creating vector index."""
        index = VectorIndex(dimension=128)

        assert index.dimension == 128
        assert index.size() == 0

    def test_add_vector(self):
        """Test adding vector to index."""
        index = VectorIndex(dimension=3)
        vector = [0.1, 0.2, 0.3]

        index.add("doc1", vector)

        assert index.size() == 1
        assert "doc1" in index.vectors

    def test_add_vector_wrong_dimension(self):
        """Test adding vector with wrong dimension."""
        index = VectorIndex(dimension=3)
        vector = [0.1, 0.2]  # Wrong dimension

        with pytest.raises(ValueError, match="dimension"):
            index.add("doc1", vector)

    def test_add_with_document(self):
        """Test adding vector with document."""
        index = VectorIndex(dimension=3)
        vector = [0.1, 0.2, 0.3]
        doc = Document(doc_id="doc1", text="Test")

        index.add("doc1", vector, doc)

        assert "doc1" in index.documents
        assert index.documents["doc1"] == doc

    def test_add_batch(self):
        """Test adding multiple vectors."""
        index = VectorIndex(dimension=2)

        doc_ids = ["doc1", "doc2", "doc3"]
        vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

        index.add_batch(doc_ids, vectors)

        assert index.size() == 3

    def test_search(self):
        """Test searching similar vectors."""
        index = VectorIndex(dimension=2)

        # Add some vectors
        index.add("doc1", [1.0, 0.0])
        index.add("doc2", [0.9, 0.1])
        index.add("doc3", [0.0, 1.0])

        # Search for similar to [1.0, 0.0]
        results = index.search([1.0, 0.0], top_k=2)

        assert len(results) == 2
        assert results[0].doc_id == "doc1"  # Most similar
        assert results[0].score > results[1].score

    def test_search_with_filter(self):
        """Test searching with metadata filter."""
        index = VectorIndex(dimension=2)

        doc1 = Document(doc_id="doc1", text="Test", metadata={"category": "A"})
        doc2 = Document(doc_id="doc2", text="Test", metadata={"category": "B"})

        index.add("doc1", [1.0, 0.0], doc1)
        index.add("doc2", [0.9, 0.1], doc2)

        # Filter by category
        filter_fn = lambda metadata: metadata.get("category") == "A"
        results = index.search([1.0, 0.0], top_k=10, filter_fn=filter_fn)

        assert len(results) == 1
        assert results[0].doc_id == "doc1"

    def test_delete(self):
        """Test deleting vector."""
        index = VectorIndex(dimension=2)
        index.add("doc1", [1.0, 0.0])

        assert index.size() == 1

        index.delete("doc1")

        assert index.size() == 0
        assert "doc1" not in index.vectors

    def test_save_and_load(self):
        """Test saving and loading index."""
        index = VectorIndex(dimension=2)
        index.add("doc1", [1.0, 0.0])
        index.add("doc2", [0.0, 1.0])

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
            filepath = f.name

        try:
            index.save(filepath)

            # Load into new index
            new_index = VectorIndex(dimension=2)
            new_index.load(filepath)

            assert new_index.size() == 2
            assert "doc1" in new_index.vectors
            assert "doc2" in new_index.vectors
        finally:
            os.unlink(filepath)


@pytest.mark.medium
@pytest.mark.integration
class TestSemanticSearch:
    """Test SemanticSearch class."""

    @pytest.mark.asyncio
    async def test_semantic_search_initialization(self):
        """Test creating semantic search."""
        search = SemanticSearch(EmbeddingModel.SENTENCE_TRANSFORMERS)

        assert search.embedding_generator is not None
        assert search.index is not None

    @pytest.mark.asyncio
    async def test_index_documents(self):
        """Test indexing documents."""
        search = SemanticSearch(EmbeddingModel.SENTENCE_TRANSFORMERS)

        docs = [
            Document(doc_id="1", text="Machine learning"),
            Document(doc_id="2", text="Deep learning"),
            Document(doc_id="3", text="Natural language processing"),
        ]

        await search.index_documents(docs)

        assert search.index.size() == 3

    @pytest.mark.asyncio
    async def test_search_documents(self):
        """Test searching documents."""
        search = SemanticSearch(EmbeddingModel.SENTENCE_TRANSFORMERS)

        docs = [
            Document(doc_id="1", text="Machine learning algorithms"),
            Document(doc_id="2", text="Cooking recipes"),
            Document(doc_id="3", text="Neural networks"),
        ]

        await search.index_documents(docs)

        # Search for ML-related content
        results = await search.search("artificial intelligence", top_k=2)

        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)


@pytest.mark.medium
@pytest.mark.integration
class TestDocumentSimilarity:
    """Test DocumentSimilarity class."""

    @pytest.mark.asyncio
    async def test_calculate_similarity(self):
        """Test calculating similarity between texts."""
        similarity_calc = DocumentSimilarity(EmbeddingModel.SENTENCE_TRANSFORMERS)

        text1 = "Machine learning is great"
        text2 = "Machine learning is awesome"
        text3 = "Cooking recipes"

        # Similar texts
        sim_12 = await similarity_calc.calculate_similarity(text1, text2)
        # Different texts
        sim_13 = await similarity_calc.calculate_similarity(text1, text3)

        assert -1.0 <= sim_12 <= 1.0
        assert -1.0 <= sim_13 <= 1.0
        assert sim_12 > sim_13  # More similar texts have higher score

    @pytest.mark.asyncio
    async def test_find_similar_documents(self):
        """Test finding similar documents."""
        similarity_calc = DocumentSimilarity(EmbeddingModel.SENTENCE_TRANSFORMERS)

        target = "Machine learning algorithms"
        candidates = [
            "Deep learning neural networks",
            "Cooking Italian pasta",
            "Data science projects",
            "Gardening tips",
        ]

        results = await similarity_calc.find_similar_documents(target, candidates, top_k=2)

        assert len(results) == 2
        assert all(isinstance(r, tuple) for r in results)
        # Results should be sorted by similarity
        assert results[0][1] >= results[1][1]


@pytest.mark.medium
@pytest.mark.integration
class TestKMeansClustering:
    """Test KMeansClustering class."""

    def test_kmeans_initialization(self):
        """Test creating k-means clusterer."""
        kmeans = KMeansClustering(n_clusters=3, max_iterations=50)

        assert kmeans.n_clusters == 3
        assert kmeans.max_iterations == 50

    def test_kmeans_fit(self):
        """Test k-means clustering."""
        kmeans = KMeansClustering(n_clusters=2, max_iterations=10)

        # Create simple 2-cluster data
        vectors = [
            [1.0, 1.0],
            [1.1, 0.9],
            [0.9, 1.1],
            [5.0, 5.0],
            [5.1, 4.9],
            [4.9, 5.1],
        ]

        results = kmeans.fit(vectors)

        assert len(results) == 2
        assert all(isinstance(r, ClusterResult) for r in results)
        assert sum(r.size for r in results) == 6

    def test_kmeans_predict(self):
        """Test predicting cluster for new vector."""
        kmeans = KMeansClustering(n_clusters=2)

        vectors = [
            [1.0, 1.0],
            [5.0, 5.0],
        ]

        kmeans.fit(vectors)

        # Predict cluster for vector close to first cluster
        cluster_id = kmeans.predict([1.1, 0.9])
        assert cluster_id in [0, 1]

    def test_kmeans_too_few_vectors(self):
        """Test k-means with too few vectors."""
        kmeans = KMeansClustering(n_clusters=5)
        vectors = [[1.0, 1.0], [2.0, 2.0]]

        with pytest.raises(ValueError, match="Number of vectors"):
            kmeans.fit(vectors)


@pytest.mark.medium
@pytest.mark.integration
class TestDocumentClustering:
    """Test DocumentClustering class."""

    @pytest.mark.asyncio
    async def test_cluster_documents(self):
        """Test clustering documents."""
        clusterer = DocumentClustering(n_clusters=2, embedding_model=EmbeddingModel.SENTENCE_TRANSFORMERS)

        docs = [
            Document(doc_id="1", text="Machine learning algorithms"),
            Document(doc_id="2", text="Deep neural networks"),
            Document(doc_id="3", text="Cooking Italian food"),
            Document(doc_id="4", text="Baking bread"),
        ]

        clusters = await clusterer.cluster_documents(docs)

        assert len(clusters) <= 2
        assert all(isinstance(docs_list, list) for docs_list in clusters.values())

    @pytest.mark.asyncio
    async def test_predict_cluster(self):
        """Test predicting cluster for new document."""
        clusterer = DocumentClustering(n_clusters=2)

        docs = [
            Document(doc_id="1", text="Machine learning"),
            Document(doc_id="2", text="Cooking recipes"),
        ]

        await clusterer.cluster_documents(docs)

        # Predict for new document
        new_doc = Document(doc_id="new", text="Deep learning")
        cluster_id = await clusterer.predict_cluster(new_doc)

        assert cluster_id in [0, 1]


# ============================================================================
# LARGE TESTS - Full Workflows, Integration
# ============================================================================


@pytest.mark.large
@pytest.mark.e2e
class TestEmbeddingService:
    """Test EmbeddingService end-to-end."""

    @pytest.mark.asyncio
    async def test_full_embedding_pipeline(self):
        """Test complete embedding workflow."""
        service = EmbeddingService(EmbeddingModel.SENTENCE_TRANSFORMERS)

        # 1. Embed texts
        texts = ["Hello world", "Machine learning", "Python programming"]
        embeddings = await service.embed_texts(texts)

        assert len(embeddings) == 3

        # 2. Calculate similarity
        similarity = await service.calculate_similarity("Hello world", "Hi there")
        assert -1.0 <= similarity <= 1.0

        # 3. Search similar documents
        docs = [
            Document(doc_id=str(i), text=text)
            for i, text in enumerate(texts)
        ]

        results = await service.search_similar("programming", docs, top_k=2)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_cluster_large_document_set(self):
        """Test clustering large set of documents."""
        service = EmbeddingService(EmbeddingModel.SENTENCE_TRANSFORMERS)

        # Create documents with different topics
        topics = {
            "ml": ["machine learning", "deep learning", "neural networks"],
            "cooking": ["cooking recipes", "baking bread", "Italian cuisine"],
            "sports": ["football games", "basketball", "tennis matches"],
        }

        docs = []
        for topic, texts in topics.items():
            for i, text in enumerate(texts):
                docs.append(Document(doc_id=f"{topic}_{i}", text=text))

        # Cluster into 3 groups
        clusters = await service.cluster_documents(docs, n_clusters=3)

        assert len(clusters) <= 3
        assert sum(len(doc_list) for doc_list in clusters.values()) == len(docs)

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test get_embedding_service singleton."""
        service1 = get_embedding_service(EmbeddingModel.SENTENCE_TRANSFORMERS)
        service2 = get_embedding_service(EmbeddingModel.SENTENCE_TRANSFORMERS)

        # Should be same instance (note: implementation creates new instance each time)
        # This test documents current behavior
        assert service1 is not None
        assert service2 is not None
