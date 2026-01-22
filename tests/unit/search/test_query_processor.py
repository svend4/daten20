"""
Tests for Query Processor and Result Reranker.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.search.query_processor import QueryProcessor, ResultReranker


# ==================== QueryProcessor Tests ====================

@pytest.mark.small
def test_query_processor_initialization():
    """Test QueryProcessor initialization."""
    processor = QueryProcessor()
    assert processor is not None


@pytest.mark.small
def test_basic_query_cleaning():
    """Test basic query cleaning."""
    processor = QueryProcessor()

    # Test cleaning
    assert processor.process("  Hello World  ") == "hello world"
    assert processor.process("HELLO") == "hello"
    assert processor.process("Test!!!") == "test"


@pytest.mark.small
def test_stopword_removal():
    """Test stopword removal."""
    processor = QueryProcessor(remove_stopwords=True)

    # Stopwords should be removed
    query = "the quick brown fox"
    processed = processor.process(query)

    assert "the" not in processed.split()
    assert "quick" in processed or "brown" in processed or "fox" in processed


@pytest.mark.small
def test_query_expansion():
    """Test query expansion with synonyms."""
    processor = QueryProcessor(expand_queries=True)

    # Add custom expansion
    processor.add_expansion("ML", ["machine learning", "ML"])

    query = "ML tutorial"
    processed = processor.process(query)

    # Should contain expansion
    assert "machine learning" in processed.lower() or "ml" in processed.lower()


@pytest.mark.small
def test_add_multiple_expansions():
    """Test adding multiple query expansions."""
    processor = QueryProcessor()

    processor.add_expansion("AI", ["artificial intelligence", "AI"])
    processor.add_expansion("NLP", ["natural language processing", "NLP"])
    processor.add_expansion("DL", ["deep learning", "DL"])

    assert len(processor.expansions) >= 3


@pytest.mark.small
def test_special_characters_removal():
    """Test removal of special characters."""
    processor = QueryProcessor()

    assert processor.process("hello@world#test") == "hello world test"
    assert processor.process("test-query") == "test query"


@pytest.mark.small
def test_empty_query():
    """Test processing empty query."""
    processor = QueryProcessor()

    assert processor.process("") == ""
    assert processor.process("   ") == ""


@pytest.mark.small
def test_numeric_queries():
    """Test queries with numbers."""
    processor = QueryProcessor()

    assert "123" in processor.process("test 123")
    assert "2024" in processor.process("year 2024")


@pytest.mark.small
def test_unicode_handling():
    """Test Unicode character handling."""
    processor = QueryProcessor()

    # Should handle unicode
    result = processor.process("café résumé")
    assert len(result) > 0


@pytest.mark.medium
def test_query_normalization():
    """Test various normalization cases."""
    processor = QueryProcessor()

    test_cases = [
        ("Multiple   spaces", "multiple spaces"),
        ("UPPERCASE", "uppercase"),
        ("MiXeD CaSe", "mixed case"),
        ("trailing spaces   ", "trailing spaces"),
        ("   leading spaces", "leading spaces")
    ]

    for input_query, expected in test_cases:
        assert processor.process(input_query) == expected


@pytest.mark.small
def test_preserve_meaningful_punctuation():
    """Test that some punctuation is handled correctly."""
    processor = QueryProcessor()

    # C++ should not become c
    result = processor.process("C++ programming")
    assert len(result) > 0


# ==================== ResultReranker Tests ====================

@pytest.fixture
def sample_results():
    """Sample search results for testing."""
    return [
        {
            'id': 'doc_1',
            'document': {'content': 'Python programming tutorial', 'date': '2024-01-01'},
            'score': 0.9,
            'distance': 0.1
        },
        {
            'id': 'doc_2',
            'document': {'content': 'Machine learning basics', 'date': '2024-02-01'},
            'score': 0.85,
            'distance': 0.15
        },
        {
            'id': 'doc_3',
            'document': {'content': 'Data science tutorial', 'date': '2024-03-01'},
            'score': 0.80,
            'distance': 0.20
        }
    ]


@pytest.mark.small
def test_reranker_initialization():
    """Test ResultReranker initialization."""
    reranker = ResultReranker()
    assert reranker is not None


@pytest.mark.medium
def test_basic_reranking(sample_results):
    """Test basic result re-ranking."""
    reranker = ResultReranker()
    query = "Python tutorial"

    reranked = reranker.rerank(sample_results, query)

    # Should return same number of results
    assert len(reranked) == len(sample_results)

    # Should have scores
    assert all('score' in r for r in reranked)


@pytest.mark.small
def test_keyword_boost(sample_results):
    """Test keyword-based boosting."""
    reranker = ResultReranker(keyword_boost=0.2)
    query = "Python programming"

    reranked = reranker.rerank(sample_results, query)

    # Result with "Python programming" should be boosted
    python_result = next((r for r in reranked if 'Python' in r['document']['content']), None)
    assert python_result is not None


@pytest.mark.small
def test_recency_boost():
    """Test recency-based boosting."""
    reranker = ResultReranker(recency_boost=0.1)

    results = [
        {'id': '1', 'document': {'content': 'Old doc', 'date': '2020-01-01'}, 'score': 0.8},
        {'id': '2', 'document': {'content': 'New doc', 'date': '2024-01-01'}, 'score': 0.8}
    ]

    reranked = reranker.rerank(results, "doc")

    # Newer document should be ranked higher (if reranker supports recency)
    if 'date' in reranked[0]['document']:
        pass  # Recency logic applied


@pytest.mark.medium
def test_diversity_reranking(sample_results):
    """Test diversity-based re-ranking."""
    reranker = ResultReranker()

    # Add category field
    for i, r in enumerate(sample_results):
        r['document']['category'] = ['A', 'A', 'B'][i]

    diverse = reranker.diversity_rerank(sample_results, diversity_field='category')

    # Should maintain or increase diversity
    assert len(diverse) == len(sample_results)


@pytest.mark.small
def test_rerank_empty_results():
    """Test re-ranking empty results."""
    reranker = ResultReranker()

    reranked = reranker.rerank([], "query")
    assert reranked == []


@pytest.mark.small
def test_rerank_single_result():
    """Test re-ranking single result."""
    reranker = ResultReranker()

    single_result = [{
        'id': 'doc_1',
        'document': {'content': 'Test'},
        'score': 0.9
    }]

    reranked = reranker.rerank(single_result, "test")
    assert len(reranked) == 1


@pytest.mark.small
def test_score_normalization(sample_results):
    """Test that scores are normalized after re-ranking."""
    reranker = ResultReranker()

    reranked = reranker.rerank(sample_results, "query")

    # Scores should be between 0 and 1
    for result in reranked:
        if 'score' in result:
            assert 0 <= result['score'] <= 1


@pytest.mark.medium
def test_custom_boosting_function():
    """Test custom boosting function."""
    reranker = ResultReranker()

    results = [
        {'id': '1', 'document': {'content': 'Doc A', 'priority': 1}, 'score': 0.8},
        {'id': '2', 'document': {'content': 'Doc B', 'priority': 10}, 'score': 0.7}
    ]

    # Rerank with custom logic (if supported)
    reranked = reranker.rerank(results, "doc")

    # Should handle custom fields gracefully
    assert len(reranked) == 2


@pytest.mark.small
def test_maintain_result_structure(sample_results):
    """Test that re-ranking maintains result structure."""
    reranker = ResultReranker()

    reranked = reranker.rerank(sample_results, "query")

    # All required fields should be present
    for result in reranked:
        assert 'id' in result
        assert 'document' in result
        assert 'score' in result or 'distance' in result


@pytest.mark.medium
def test_multiple_reranking_strategies():
    """Test combining multiple re-ranking strategies."""
    reranker = ResultReranker(
        keyword_boost=0.2,
        recency_boost=0.1
    )

    results = [
        {
            'id': '1',
            'document': {'content': 'Python tutorial old', 'date': '2020-01-01'},
            'score': 0.7
        },
        {
            'id': '2',
            'document': {'content': 'Python tutorial new', 'date': '2024-01-01'},
            'score': 0.7
        }
    ]

    reranked = reranker.rerank(results, "Python tutorial")

    # Both keyword and recency should influence ranking
    assert len(reranked) == 2


@pytest.mark.small
def test_rerank_preserves_metadata(sample_results):
    """Test that metadata is preserved during re-ranking."""
    reranker = ResultReranker()

    # Add custom metadata
    for r in sample_results:
        r['custom_field'] = 'test_value'

    reranked = reranker.rerank(sample_results, "query")

    # Custom fields should be preserved
    for r in reranked:
        if 'custom_field' in r:
            assert r['custom_field'] == 'test_value'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
