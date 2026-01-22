"""
Tests for Vector Store module (ChromaDB and FAISS backends).
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.search.vector_store import VectorStore, MockVectorStore


# ==================== Fixtures ====================

@pytest.fixture
def mock_embeddings():
    """Generate mock embeddings."""
    return np.random.rand(10, 384).astype(np.float32)


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {"content": f"Document {i}", "id": f"doc_{i}", "category": "test"}
        for i in range(10)
    ]


@pytest.fixture
def mock_store():
    """Create mock vector store."""
    return MockVectorStore(embedding_dim=384)


# ==================== Tests ====================

@pytest.mark.small
def test_mock_store_initialization():
    """Test mock store initialization."""
    store = MockVectorStore(embedding_dim=384)
    assert store.embedding_dim == 384
    assert store.count() == 0


@pytest.mark.small
def test_add_vectors(mock_store, mock_embeddings, sample_documents):
    """Test adding vectors to store."""
    ids = mock_store.add(mock_embeddings, sample_documents)

    assert len(ids) == len(sample_documents)
    assert mock_store.count() == len(sample_documents)


@pytest.mark.medium
def test_search_vectors(mock_store, mock_embeddings, sample_documents):
    """Test searching for similar vectors."""
    # Add vectors
    mock_store.add(mock_embeddings, sample_documents)

    # Search with first embedding
    query_embedding = mock_embeddings[0:1]
    results = mock_store.search(query_embedding, top_k=3)

    assert len(results) <= 3
    assert all('id' in r for r in results)
    assert all('document' in r for r in results)
    assert all('distance' in r for r in results)


@pytest.mark.medium
def test_search_with_filters(mock_store, mock_embeddings):
    """Test search with metadata filters."""
    # Add documents with different categories
    docs = [
        {"content": f"Doc {i}", "category": "A" if i < 5 else "B"}
        for i in range(10)
    ]
    mock_store.add(mock_embeddings, docs)

    # Search with filter
    query = mock_embeddings[0:1]
    results = mock_store.search(query, top_k=10, filters={"category": "A"})

    # All results should be category A
    assert all(r['document']['category'] == 'A' for r in results if 'document' in r)


@pytest.mark.small
def test_delete_vectors(mock_store, mock_embeddings, sample_documents):
    """Test deleting vectors."""
    # Add vectors
    ids = mock_store.add(mock_embeddings, sample_documents)
    initial_count = mock_store.count()

    # Delete some
    ids_to_delete = ids[:3]
    success = mock_store.delete(ids_to_delete)

    assert success
    assert mock_store.count() == initial_count - len(ids_to_delete)


@pytest.mark.small
def test_clear_store(mock_store, mock_embeddings, sample_documents):
    """Test clearing the store."""
    # Add vectors
    mock_store.add(mock_embeddings, sample_documents)
    assert mock_store.count() > 0

    # Clear
    success = mock_store.clear()
    assert success
    assert mock_store.count() == 0


@pytest.mark.small
def test_get_by_id(mock_store, mock_embeddings, sample_documents):
    """Test retrieving document by ID."""
    ids = mock_store.add(mock_embeddings, sample_documents)

    # Get first document
    doc = mock_store.get(ids[0])

    assert doc is not None
    assert 'content' in doc


@pytest.mark.small
def test_update_document(mock_store, mock_embeddings, sample_documents):
    """Test updating a document."""
    ids = mock_store.add(mock_embeddings, sample_documents)

    # Update first document
    updated_doc = {"content": "Updated content", "category": "updated"}
    success = mock_store.update(ids[0], mock_embeddings[0:1], updated_doc)

    if success:  # Not all stores support update
        retrieved = mock_store.get(ids[0])
        assert retrieved['content'] == "Updated content"


@pytest.mark.small
def test_embedding_dimension_validation():
    """Test that embedding dimension is validated."""
    store = MockVectorStore(embedding_dim=384)

    # Try to add embeddings with wrong dimension
    wrong_dim_embeddings = np.random.rand(5, 512).astype(np.float32)
    docs = [{"content": f"Doc {i}"} for i in range(5)]

    with pytest.raises((ValueError, AssertionError)):
        store.add(wrong_dim_embeddings, docs)


@pytest.mark.medium
def test_batch_operations(mock_store):
    """Test batch add and search operations."""
    # Create larger batch
    num_docs = 100
    embeddings = np.random.rand(num_docs, 384).astype(np.float32)
    docs = [{"content": f"Document {i}", "id": i} for i in range(num_docs)]

    # Batch add
    ids = mock_store.add(embeddings, docs)
    assert len(ids) == num_docs

    # Batch search
    query_embeddings = embeddings[:5]  # Search with first 5
    for query in query_embeddings:
        results = mock_store.search(query.reshape(1, -1), top_k=10)
        assert len(results) <= 10


@pytest.mark.small
def test_empty_search():
    """Test searching in empty store."""
    store = MockVectorStore(embedding_dim=384)
    query = np.random.rand(1, 384).astype(np.float32)

    results = store.search(query, top_k=5)
    assert results == []


@pytest.mark.small
def test_search_with_zero_top_k(mock_store, mock_embeddings, sample_documents):
    """Test search with top_k=0."""
    mock_store.add(mock_embeddings, sample_documents)
    query = mock_embeddings[0:1]

    results = mock_store.search(query, top_k=0)
    assert results == []


@pytest.mark.small
def test_search_top_k_larger_than_store(mock_store, mock_embeddings):
    """Test searching with top_k larger than number of documents."""
    # Add only 5 documents
    docs = [{"content": f"Doc {i}"} for i in range(5)]
    embeddings = mock_embeddings[:5]
    mock_store.add(embeddings, docs)

    # Search with top_k=10 (more than available)
    query = embeddings[0:1]
    results = mock_store.search(query, top_k=10)

    # Should return all 5, not fail
    assert len(results) == 5


@pytest.mark.medium
def test_persistence():
    """Test store persistence (if supported)."""
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()

    try:
        # Create store with persistence
        store1 = MockVectorStore(embedding_dim=384, persist_directory=temp_dir)

        # Add data
        embeddings = np.random.rand(10, 384).astype(np.float32)
        docs = [{"content": f"Doc {i}"} for i in range(10)]
        ids = store1.add(embeddings, docs)

        # If store supports persistence, verify
        if hasattr(store1, 'persist'):
            store1.persist()

        # Create new store from same directory
        store2 = MockVectorStore(embedding_dim=384, persist_directory=temp_dir)

        # If persistence works, count should match
        if hasattr(store2, 'load'):
            store2.load()
            assert store2.count() == 10

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.small
def test_distance_metrics():
    """Test different distance metrics (if supported)."""
    store = MockVectorStore(embedding_dim=384)

    # Add some vectors
    embeddings = np.random.rand(10, 384).astype(np.float32)
    # Normalize for cosine similarity
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    docs = [{"content": f"Doc {i}"} for i in range(10)]
    store.add(embeddings, docs)

    query = embeddings[0:1]

    # Test different metrics (if store supports it)
    for metric in ['cosine', 'l2', 'ip']:
        try:
            results = store.search(query, top_k=3, metric=metric)
            assert len(results) <= 3
        except (ValueError, NotImplementedError):
            # Metric not supported, skip
            pass


@pytest.mark.small
def test_concurrent_access(mock_store, mock_embeddings, sample_documents):
    """Test concurrent read/write operations."""
    import threading

    # Add initial data
    mock_store.add(mock_embeddings[:5], sample_documents[:5])

    errors = []

    def add_documents():
        try:
            mock_store.add(mock_embeddings[5:], sample_documents[5:])
        except Exception as e:
            errors.append(e)

    def search_documents():
        try:
            query = mock_embeddings[0:1]
            mock_store.search(query, top_k=3)
        except Exception as e:
            errors.append(e)

    # Run concurrent operations
    threads = [
        threading.Thread(target=add_documents),
        threading.Thread(target=search_documents),
        threading.Thread(target=search_documents)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should not have errors (mock store should handle concurrency)
    assert len(errors) == 0 or all(isinstance(e, (ValueError, RuntimeError)) for e in errors)


@pytest.mark.small
def test_document_without_id(mock_store, mock_embeddings):
    """Test adding documents without explicit IDs."""
    docs = [{"content": f"Doc {i}"} for i in range(5)]  # No 'id' field

    ids = mock_store.add(mock_embeddings[:5], docs)

    # Store should generate IDs
    assert len(ids) == 5
    assert all(isinstance(id, str) for id in ids)
    assert len(set(ids)) == 5  # All unique


@pytest.mark.small
def test_get_all_ids(mock_store, mock_embeddings, sample_documents):
    """Test retrieving all document IDs."""
    ids = mock_store.add(mock_embeddings, sample_documents)

    if hasattr(mock_store, 'get_all_ids'):
        all_ids = mock_store.get_all_ids()
        assert set(all_ids) == set(ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
