#!/usr/bin/env python3
"""
Comprehensive tests for Semantic Search with BERT

Tests all functionality of the semantic search engine.
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from src.ml.semantic_search import (
    IndexStats,
    SearchQuery,
    SearchResult,
    SemanticSearchEngine,
    create_search_engine,
    quick_search,
)


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "id": "doc1",
            "text": "Machine learning is a subset of artificial intelligence",
            "metadata": {"category": "AI", "author": "Alice"},
        },
        {
            "id": "doc2",
            "text": "Deep learning uses neural networks with multiple layers",
            "metadata": {"category": "AI", "author": "Bob"},
        },
        {
            "id": "doc3",
            "text": "Python is a popular programming language for data science",
            "metadata": {"category": "Programming", "author": "Charlie"},
        },
    ]


class TestSearchResult:
    """Test SearchResult dataclass"""

    def test_search_result_creation(self):
        """Test creating SearchResult"""
        result = SearchResult(document_id="doc1", score=0.95, content="Test content", rank=1)

        assert result.document_id == "doc1"
        assert result.score == 0.95
        assert result.content == "Test content"
        assert result.rank == 1


class TestSearchQuery:
    """Test SearchQuery dataclass"""

    def test_search_query_defaults(self):
        """Test SearchQuery default values"""
        query = SearchQuery(text="test query")

        assert query.text == "test query"
        assert query.top_k == 10
        assert query.min_score == 0.0


@patch("src.ml.semantic_search.TRANSFORMERS_AVAILABLE", True)
@patch("src.ml.semantic_search.FAISS_AVAILABLE", True)
class TestSemanticSearchEngine:
    """Test SemanticSearchEngine class"""

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_engine_initialization(self, mock_faiss, mock_st):
        """Test engine initialization"""
        mock_st.return_value = Mock(get_sentence_embedding_dimension=Mock(return_value=384))
        mock_faiss.IndexFlatL2.return_value = Mock()

        engine = SemanticSearchEngine(model_name="test-model")

        assert engine.model_name == "test-model"
        assert engine.cache_embeddings is True

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_index_documents(self, mock_faiss, mock_st, sample_documents):
        """Test indexing documents"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.side_effect = lambda texts, **kwargs: np.random.rand(len(texts), 384).astype(np.float32)
        mock_st.return_value = mock_model

        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.add = Mock(side_effect=lambda x: setattr(mock_index, "ntotal", 3))
        mock_faiss.IndexFlatL2.return_value = mock_index

        engine = SemanticSearchEngine()
        indexed_count = engine.index_documents(sample_documents)

        assert indexed_count == 3
        assert len(engine._document_store) == 3

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_search_basic(self, mock_faiss, mock_st, sample_documents):
        """Test basic search"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        # Make encode return correct number of embeddings based on input
        mock_model.encode.side_effect = lambda texts, **kwargs: np.random.rand(len(texts), 384).astype(np.float32)
        mock_st.return_value = mock_model

        mock_index = Mock()
        mock_index.ntotal = 3
        mock_index.add = Mock()
        mock_index.search = Mock(return_value=(np.array([[0.1, 0.2]]), np.array([[0, 1]])))
        mock_faiss.IndexFlatL2.return_value = mock_index

        engine = SemanticSearchEngine()
        engine.index_documents(sample_documents)
        results = engine.search("AI", top_k=2)

        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_get_stats(self, mock_faiss, mock_st, sample_documents):
        """Test getting index statistics"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.side_effect = lambda texts, **kwargs: np.random.rand(len(texts), 384).astype(np.float32)
        mock_st.return_value = mock_model

        mock_index = Mock()
        mock_index.ntotal = 3
        mock_index.add = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_index

        engine = SemanticSearchEngine(model_name="test-model")
        engine.index_documents(sample_documents)
        stats = engine.get_stats()

        assert isinstance(stats, IndexStats)
        assert stats.total_documents == 3
        assert stats.model_name == "test-model"

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_save_index(self, mock_faiss, mock_st, sample_documents):
        """Test saving index"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.side_effect = lambda texts, **kwargs: np.random.rand(len(texts), 384).astype(np.float32)
        mock_st.return_value = mock_model

        mock_index = Mock()
        mock_index.ntotal = 3
        mock_index.add = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.write_index = Mock()

        engine = SemanticSearchEngine()
        engine.index_documents(sample_documents)

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "test_index")
            engine.save_index(index_path)

            # Verify write_index was called
            mock_faiss.write_index.assert_called_once()

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_clear_cache(self, mock_faiss, mock_st):
        """Test clearing embedding cache"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.side_effect = lambda texts, **kwargs: np.random.rand(len(texts), 384).astype(np.float32)
        mock_st.return_value = mock_model
        mock_faiss.IndexFlatL2.return_value = Mock()

        engine = SemanticSearchEngine(cache_embeddings=True)
        engine.encode_texts(["text1", "text2"])

        # Check cache has items (use memory_cache.size())
        assert engine._embedding_cache.memory_cache.size() > 0

        engine.clear_cache()
        assert engine._embedding_cache.memory_cache.size() == 0


@patch("src.ml.semantic_search.TRANSFORMERS_AVAILABLE", True)
@patch("src.ml.semantic_search.FAISS_AVAILABLE", True)
class TestFactoryFunctions:
    """Test factory and convenience functions"""

    @patch("src.ml.semantic_search.SentenceTransformer")
    @patch("src.ml.semantic_search.faiss")
    def test_create_search_engine(self, mock_faiss, mock_st):
        """Test create_search_engine factory"""
        mock_st.return_value = Mock(get_sentence_embedding_dimension=Mock(return_value=384))
        mock_faiss.IndexFlatL2.return_value = Mock()

        engine = create_search_engine(model_name="test-model", use_gpu=True)

        assert isinstance(engine, SemanticSearchEngine)
        assert engine.model_name == "test-model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
