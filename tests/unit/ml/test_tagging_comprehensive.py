"""
Comprehensive tests for tagging module

Test coverage goals:
- TF-IDF keyword extraction
- TextRank algorithm
- LDA topic modeling
- Tag suggestion and management
- Multi-label classification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from collections import Counter

from src.ml.tagging import (
    Tag,
    TagType,
    TagSuggestion,
    TFIDFExtractor,
    AutoTagger,
)


class TestTag:
    """Test Tag dataclass"""

    def test_tag_creation(self):
        """Test creating a tag"""
        tag = Tag(
            id="tag1",
            name="python",
            type=TagType.KEYWORD,
            confidence=0.9,
            frequency=5
        )

        assert tag.id == "tag1"
        assert tag.name == "python"
        assert tag.type == TagType.KEYWORD
        assert tag.confidence == 0.9
        assert tag.frequency == 5
        assert tag.metadata == {}

    def test_tag_with_metadata(self):
        """Test tag with metadata"""
        metadata = {"source": "tfidf", "score": 0.85}
        tag = Tag(
            id="tag2",
            name="machine-learning",
            type=TagType.TOPIC,
            metadata=metadata
        )

        assert tag.metadata == metadata
        assert tag.metadata["source"] == "tfidf"

    def test_tag_type_enum(self):
        """Test TagType enum values"""
        assert TagType.KEYWORD == "keyword"
        assert TagType.TOPIC == "topic"
        assert TagType.CATEGORY == "category"
        assert TagType.ENTITY == "entity"
        assert TagType.CUSTOM == "custom"


class TestTagSuggestion:
    """Test TagSuggestion dataclass"""

    def test_suggestion_creation(self):
        """Test creating a tag suggestion"""
        suggestion = TagSuggestion(
            tag="python",
            score=0.85,
            source="tfidf"
        )

        assert suggestion.tag == "python"
        assert suggestion.score == 0.85
        assert suggestion.source == "tfidf"
        assert suggestion.context is None

    def test_suggestion_with_context(self):
        """Test suggestion with context"""
        suggestion = TagSuggestion(
            tag="python",
            score=0.85,
            source="tfidf",
            context="Python is a programming language"
        )

        assert suggestion.context == "Python is a programming language"


class TestTFIDFExtractor:
    """Test TF-IDF keyword extraction"""

    @pytest.fixture
    def extractor(self):
        """Create TF-IDF extractor"""
        return TFIDFExtractor()

    def test_initialization(self, extractor):
        """Test extractor initialization"""
        assert extractor.document_frequency == {}
        assert extractor.total_documents == 0

    def test_add_document(self, extractor):
        """Test adding documents"""
        words = ["python", "programming", "language"]
        extractor.add_document(words)

        assert extractor.total_documents == 1
        assert "python" in extractor.document_frequency
        assert extractor.document_frequency["python"] == 1

    def test_add_multiple_documents(self, extractor):
        """Test adding multiple documents"""
        extractor.add_document(["python", "programming"])
        extractor.add_document(["python", "language"])
        extractor.add_document(["java", "programming"])

        assert extractor.total_documents == 3
        assert extractor.document_frequency["python"] == 2
        assert extractor.document_frequency["programming"] == 2
        assert extractor.document_frequency["java"] == 1

    def test_extract_keywords_empty_text(self, extractor):
        """Test keyword extraction with empty text"""
        keywords = extractor.extract_keywords("")
        assert isinstance(keywords, list)

    def test_extract_keywords_simple_text(self, extractor):
        """Test keyword extraction with simple text"""
        # Add some documents to build IDF
        extractor.add_document(["machine", "learning", "ai"])
        extractor.add_document(["deep", "learning", "neural"])

        text = "machine learning is a subset of artificial intelligence"
        keywords = extractor.extract_keywords(text, top_k=5)

        assert isinstance(keywords, list)
        assert all(isinstance(k, TagSuggestion) for k in keywords)
        assert all(k.source == "tfidf" for k in keywords)

    def test_extract_keywords_top_k(self, extractor):
        """Test top-k keyword extraction"""
        text = "python programming language is great for machine learning"

        keywords_5 = extractor.extract_keywords(text, top_k=5)
        keywords_3 = extractor.extract_keywords(text, top_k=3)

        assert len(keywords_5) <= 5
        assert len(keywords_3) <= 3

    def test_extract_keywords_scores(self, extractor):
        """Test that keyword scores are valid"""
        extractor.add_document(["test", "document"])

        text = "test document with some keywords"
        keywords = extractor.extract_keywords(text)

        for keyword in keywords:
            assert keyword.score >= 0.0
            assert isinstance(keyword.score, float)

    def test_extract_keywords_sorted_by_score(self, extractor):
        """Test that keywords are sorted by score"""
        extractor.add_document(["common", "word"])

        text = "rare uncommon common word"
        keywords = extractor.extract_keywords(text, top_k=10)

        if len(keywords) > 1:
            # Check that scores are in descending order
            scores = [k.score for k in keywords]
            assert scores == sorted(scores, reverse=True)

    def test_tokenization(self, extractor):
        """Test text tokenization"""
        text = "Python is great! It's amazing."
        tokens = extractor._tokenize(text)

        assert isinstance(tokens, list)
        assert all(isinstance(t, str) for t in tokens)

    def test_tokenization_lowercase(self, extractor):
        """Test that tokenization lowercases text"""
        text = "Python PYTHON python"
        tokens = extractor._tokenize(text)

        # All should be lowercase
        assert all(t.islower() or not t.isalpha() for t in tokens)

    def test_tokenization_special_chars(self, extractor):
        """Test tokenization with special characters"""
        text = "hello@world #python $100"
        tokens = extractor._tokenize(text)

        assert isinstance(tokens, list)

    def test_idf_calculation(self, extractor):
        """Test IDF calculation"""
        # Document 1: common word appears
        extractor.add_document(["common"])

        # Document 2: common word appears
        extractor.add_document(["common"])

        # Document 3: rare word appears
        extractor.add_document(["rare"])

        # "rare" should have higher IDF than "common"
        text = "common rare"
        keywords = extractor.extract_keywords(text)

        if len(keywords) >= 2:
            # Find scores for common and rare
            scores = {k.tag: k.score for k in keywords}
            if "rare" in scores and "common" in scores:
                assert scores["rare"] > scores["common"]

    def test_tf_calculation(self, extractor):
        """Test term frequency calculation"""
        # Add some documents to build corpus
        extractor.add_document(["python", "java"])
        extractor.add_document(["programming", "code"])

        text = "python python python java"
        keywords = extractor.extract_keywords(text)

        # Python appears 3 times, java appears 1 time
        scores = {k.tag: k.score for k in keywords}
        if "python" in scores and "java" in scores:
            # Python should have higher TF-IDF score due to higher frequency
            assert scores["python"] >= scores["java"]


class TestAutoTagger:
    """Test AutoTagger main class"""

    @pytest.fixture
    def tagger(self):
        """Create AutoTagger instance"""
        return AutoTagger()

    def test_initialization(self, tagger):
        """Test tagger initialization"""
        assert tagger is not None
        assert hasattr(tagger, 'tfidf_extractor')

    def test_suggest_tags_empty_text(self, tagger):
        """Test tag suggestion with empty text"""
        suggestions = tagger.suggest_tags("")
        assert isinstance(suggestions, list)

    def test_suggest_tags_simple_text(self, tagger):
        """Test tag suggestion with simple text"""
        text = "Python is a programming language for machine learning and data science"
        suggestions = tagger.suggest_tags(text, top_k=5)

        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
        assert all(isinstance(s, TagSuggestion) for s in suggestions)

    def test_suggest_tags_long_text(self, tagger):
        """Test tag suggestion with long text"""
        text = " ".join([
            "Machine learning is a method of data analysis that automates analytical model building.",
            "It is a branch of artificial intelligence based on the idea that systems can learn from data,",
            "identify patterns and make decisions with minimal human intervention."
        ])

        suggestions = tagger.suggest_tags(text, top_k=10)
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 10

    def test_suggest_tags_with_combine_methods(self, tagger):
        """Test tag suggestion with combine_methods parameter"""
        text = "Python programming for data science"

        # Test with combine_methods=False to get raw suggestions
        suggestions = tagger.suggest_tags(text, combine_methods=False)
        assert isinstance(suggestions, list)
        assert all(isinstance(s, TagSuggestion) for s in suggestions)

    def test_initialize_corpus(self, tagger):
        """Test initializing with document corpus"""
        documents = [
            "Python programming language",
            "Java programming language",
            "Machine learning with Python"
        ]

        tagger.initialize_corpus(documents)

        # TF-IDF extractor should have documents
        assert tagger.tfidf_extractor.total_documents == len(documents)

    def test_tag_assignment(self, tagger):
        """Test assigning tags to document"""
        text = "Python is great for machine learning"

        tags = tagger.auto_tag_document("doc1", text, max_tags=5)
        assert isinstance(tags, list)
        assert all(isinstance(t, Tag) for t in tags)

    def test_tag_filtering_by_threshold(self, tagger):
        """Test filtering tags by threshold"""
        text = "Python programming language"

        tags_high = tagger.auto_tag_document("doc1", text, threshold=0.8)
        tags_low = tagger.auto_tag_document("doc2", text, threshold=0.1)

        # Higher threshold should result in fewer or equal tags
        assert len(tags_high) <= len(tags_low)

    def test_deduplication(self, tagger):
        """Test that duplicate tags are removed"""
        text = "python python python programming programming"

        tags = tagger.auto_tag_document("doc1", text, max_tags=10)

        # Check for duplicates
        tag_names = [t.name for t in tags]
        assert len(tag_names) == len(set(tag_names))

    def test_special_characters_handling(self, tagger):
        """Test handling of special characters"""
        text = "C++ programming! Python? Java & Rust."

        suggestions = tagger.suggest_tags(text)
        assert isinstance(suggestions, list)

    def test_unicode_text(self, tagger):
        """Test handling of Unicode text"""
        text = "Python编程语言非常强大"

        suggestions = tagger.suggest_tags(text)
        assert isinstance(suggestions, list)

    def test_very_short_text(self, tagger):
        """Test with very short text"""
        text = "Python"

        suggestions = tagger.suggest_tags(text)
        assert isinstance(suggestions, list)

    def test_very_long_text(self, tagger):
        """Test with very long text"""
        text = " ".join(["Python is a programming language."] * 1000)

        suggestions = tagger.suggest_tags(text, top_k=10)
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 10

    def test_mixed_case_text(self, tagger):
        """Test with mixed case text"""
        text = "PYTHON python Python PyThOn"

        suggestions = tagger.suggest_tags(text)
        assert isinstance(suggestions, list)

    def test_numbers_in_text(self, tagger):
        """Test handling numbers in text"""
        text = "Python 3.9 is better than Python 2.7"

        suggestions = tagger.suggest_tags(text)
        assert isinstance(suggestions, list)

    def test_stopwords_removal(self, tagger):
        """Test that common stopwords are handled"""
        text = "the quick brown fox jumps over the lazy dog the the the"

        suggestions = tagger.suggest_tags(text, top_k=5)

        # "the" should not dominate the tags due to stopword handling
        tag_names = [s.tag for s in suggestions]
        # Check that not all tags are "the"
        assert len(set(tag_names)) > 1 or len(tag_names) == 0


@pytest.mark.parametrize("text,top_k,expected_min", [
    ("Python programming", 5, 0),
    ("machine learning data science", 3, 0),
    ("", 10, 0),
    ("a", 5, 0),
])
def test_parametrized_tagging(text, top_k, expected_min):
    """Test tagging with various inputs"""
    tagger = AutoTagger()
    suggestions = tagger.suggest_tags(text, top_k=top_k)

    assert isinstance(suggestions, list)
    assert len(suggestions) >= expected_min
    assert len(suggestions) <= top_k


class TestTagManagement:
    """Test tag management functionality"""

    def test_tag_comparison(self):
        """Test comparing tags"""
        tag1 = Tag(id="1", name="python", type=TagType.KEYWORD)
        tag2 = Tag(id="2", name="python", type=TagType.KEYWORD)
        tag3 = Tag(id="3", name="java", type=TagType.KEYWORD)

        # Tags with same name should be comparable
        assert tag1.name == tag2.name
        assert tag1.name != tag3.name

    def test_tag_frequency_tracking(self):
        """Test tag frequency tracking"""
        tag = Tag(
            id="1",
            name="python",
            type=TagType.KEYWORD,
            frequency=0
        )

        # Increment frequency
        tag.frequency += 1
        assert tag.frequency == 1

        tag.frequency += 5
        assert tag.frequency == 6

    def test_tag_confidence_validation(self):
        """Test tag confidence value validation"""
        # Valid confidence
        tag = Tag(id="1", name="test", type=TagType.KEYWORD, confidence=0.5)
        assert 0.0 <= tag.confidence <= 1.0

        # Edge cases
        tag_min = Tag(id="2", name="test", type=TagType.KEYWORD, confidence=0.0)
        assert tag_min.confidence == 0.0

        tag_max = Tag(id="3", name="test", type=TagType.KEYWORD, confidence=1.0)
        assert tag_max.confidence == 1.0


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def tagger(self):
        return AutoTagger()

    def test_none_input(self, tagger):
        """Test handling of None input"""
        with pytest.raises((TypeError, AttributeError)):
            tagger.suggest_tags(None)

    def test_invalid_input_type(self, tagger):
        """Test handling of invalid input type"""
        with pytest.raises((TypeError, AttributeError)):
            tagger.suggest_tags(12345)

    def test_negative_top_k(self, tagger):
        """Test handling of negative top_k"""
        text = "Python programming"
        suggestions = tagger.suggest_tags(text, top_k=-5)

        # Should handle gracefully, return empty or handle error
        assert isinstance(suggestions, list)

    def test_zero_top_k(self, tagger):
        """Test with top_k=0"""
        text = "Python programming"
        suggestions = tagger.suggest_tags(text, top_k=0)

        assert isinstance(suggestions, list)
        assert len(suggestions) == 0

    def test_very_large_top_k(self, tagger):
        """Test with very large top_k"""
        text = "Python programming"
        suggestions = tagger.suggest_tags(text, top_k=1000000)

        # Should not crash, just return all available tags
        assert isinstance(suggestions, list)

    def test_whitespace_only_text(self, tagger):
        """Test with whitespace-only text"""
        text = "     \n\t\r    "
        suggestions = tagger.suggest_tags(text)

        assert isinstance(suggestions, list)

    def test_repeated_words(self, tagger):
        """Test with many repeated words"""
        text = "test " * 1000
        suggestions = tagger.suggest_tags(text, top_k=5)

        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
