"""
Comprehensive tests for BERT Semantic Search module.
"""

import pytest
import numpy as np

# Import modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.search.bert_embedder import MockBERTEmbedder
from src.search.semantic_search import SemanticSearch
from src.search.query_processor import QueryProcessor, ResultReranker


# ==================== Fixtures ====================

@pytest.fixture
def mock_embedder():
    """Mock BERT embedder for testing."""
    return MockBERTEmbedder(model_name="fast")


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {"content": "Python programming tutorial", "category": "tech"},
        {"content": "Machine learning basics", "category": "AI"},
        {"content": "Cooking recipes for beginners", "category": "food"}
    ]


# ==================== Tests ====================

@pytest.mark.small
def test_mock_embedder_initialization():
    """Test embedder initialization."""
    embedder = MockBERTEmbedder(model_name="test")
    assert embedder.model_name == "test"
    assert embedder.embedding_dim == 384


@pytest.mark.small
def test_embed_single_text(mock_embedder):
    """Test embedding single text."""
    embedding = mock_embedder.embed("Hello world")
    
    assert embedding.shape == (1, 384)
    assert np.isclose(np.linalg.norm(embedding[0]), 1.0, atol=1e-5)


@pytest.mark.small
def test_query_processor():
    """Test query processor."""
    processor = QueryProcessor()
    result = processor.process("Hello World!!!")
    
    assert result.lower() == "hello world"


@pytest.mark.medium
def test_semantic_search_add_documents(mock_embedder, sample_documents):
    """Test adding documents."""
    search = SemanticSearch(embedder=mock_embedder)
    doc_ids = search.add_documents(sample_documents)
    
    assert len(doc_ids) == len(sample_documents)
    assert search.count_documents() == len(sample_documents)


@pytest.mark.medium
def test_semantic_search(mock_embedder, sample_documents):
    """Test searching documents."""
    search = SemanticSearch(embedder=mock_embedder)
    search.add_documents(sample_documents)
    
    results = search.search("Python programming", top_k=2)
    
    assert len(results) <= 2
    assert all("score" in r for r in results)


@pytest.mark.medium
def test_clear_index(mock_embedder, sample_documents):
    """Test clearing index."""
    search = SemanticSearch(embedder=mock_embedder)
    search.add_documents(sample_documents)
    
    assert search.count_documents() > 0
    search.clear_index()
    assert search.count_documents() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
