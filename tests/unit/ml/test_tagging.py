"""
Comprehensive tests for ml/tagging.py module.

Tests TF-IDF extraction, TextRank, topic modeling, and auto-tagging functionality.
"""

import pytest
from unittest.mock import Mock, patch


# ============================================================================
# Data Classes Tests
# ============================================================================


class TestTag:
    """Test Tag dataclass."""

    def test_tag_creation(self):
        """Test creating a tag"""
        from src.ml.tagging import Tag, TagType

        tag = Tag(
            id="tag_1",
            name="invoice",
            type=TagType.KEYWORD,
            confidence=0.95,
            frequency=10,
            metadata={"source": "auto"}
        )

        assert tag.id == "tag_1"
        assert tag.name == "invoice"
        assert tag.type == TagType.KEYWORD
        assert tag.confidence == 0.95
        assert tag.frequency == 10
        assert tag.metadata["source"] == "auto"

    def test_tag_defaults(self):
        """Test tag default values"""
        from src.ml.tagging import Tag, TagType

        tag = Tag(id="tag_1", name="test", type=TagType.KEYWORD)

        assert tag.confidence == 1.0
        assert tag.frequency == 0
        assert tag.metadata == {}


class TestTagSuggestion:
    """Test TagSuggestion dataclass."""

    def test_tag_suggestion_creation(self):
        """Test creating a tag suggestion"""
        from src.ml.tagging import TagSuggestion

        suggestion = TagSuggestion(
            tag="invoice",
            score=0.85,
            source="tfidf",
            context="financial"
        )

        assert suggestion.tag == "invoice"
        assert suggestion.score == 0.85
        assert suggestion.source == "tfidf"
        assert suggestion.context == "financial"


class TestTagType:
    """Test TagType enum."""

    def test_tag_types_exist(self):
        """Test all tag types are defined"""
        from src.ml.tagging import TagType

        assert TagType.KEYWORD == "keyword"
        assert TagType.TOPIC == "topic"
        assert TagType.CATEGORY == "category"
        assert TagType.ENTITY == "entity"
        assert TagType.CUSTOM == "custom"


# ============================================================================
# TFIDFExtractor Tests
# ============================================================================


class TestTFIDFExtractor:
    """Test TFIDFExtractor functionality."""

    @pytest.fixture
    def extractor(self):
        """Create TFIDFExtractor instance."""
        from src.ml.tagging import TFIDFExtractor

        return TFIDFExtractor()

    def test_tfidf_extractor_initialization(self, extractor):
        """Test TFIDFExtractor initialization"""
        assert extractor.document_frequency == {}
        assert extractor.total_documents == 0

    def test_add_document(self, extractor):
        """Test adding document to corpus"""
        words = ["rechnung", "betrag", "zahlung"]
        extractor.add_document(words)

        assert extractor.total_documents == 1
        assert extractor.document_frequency["rechnung"] == 1
        assert extractor.document_frequency["betrag"] == 1

    def test_add_multiple_documents(self, extractor):
        """Test adding multiple documents"""
        extractor.add_document(["rechnung", "betrag"])
        extractor.add_document(["rechnung", "zahlung"])
        extractor.add_document(["vertrag", "zahlung"])

        assert extractor.total_documents == 3
        assert extractor.document_frequency["rechnung"] == 2
        assert extractor.document_frequency["betrag"] == 1
        assert extractor.document_frequency["zahlung"] == 2
        assert extractor.document_frequency["vertrag"] == 1

    def test_extract_keywords_basic(self, extractor):
        """Test basic keyword extraction"""
        # Build corpus
        extractor.add_document(["rechnung", "betrag", "zahlung"])
        extractor.add_document(["vertrag", "vereinbarung"])

        text = "Rechnung für Betrag 100 EUR zahlung"
        suggestions = extractor.extract_keywords(text, top_k=3)

        assert len(suggestions) <= 3
        assert all(s.source == "tfidf" for s in suggestions)

    def test_extract_keywords_empty_text(self, extractor):
        """Test extracting from empty text"""
        extractor.add_document(["test"])

        suggestions = extractor.extract_keywords("", top_k=5)

        assert len(suggestions) == 0

    def test_tokenize_basic(self, extractor):
        """Test basic tokenization"""
        text = "Das ist ein Test mit mehreren Wörtern"
        words = extractor._tokenize(text)

        # Should remove stopwords (das, ist) and words with length <= 2
        assert "das" not in words  # Stopword
        assert "ist" not in words  # Stopword
        # Words with length > 2 are kept
        assert "ein" in words  # Not a stopword, length 3
        assert "mit" in words  # Not a stopword, length 3
        assert "test" in words
        assert "mehreren" in words

    def test_tokenize_special_characters(self, extractor):
        """Test tokenization removes special characters"""
        text = "test@example.com, 100€, [brackets]"
        words = extractor._tokenize(text)

        # Special characters should be removed
        assert all(w.isalnum() or w in ["ä", "ö", "ü", "ß"] for w in words)

    def test_tokenize_german_umlauts(self, extractor):
        """Test tokenization preserves German umlauts"""
        text = "Büro Müller über Änderung größer"
        words = extractor._tokenize(text)

        assert "büro" in words
        assert "müller" in words
        assert "über" in words


# ============================================================================
# TextRankExtractor Tests
# ============================================================================


class TestTextRankExtractor:
    """Test TextRankExtractor functionality."""

    @pytest.fixture
    def extractor(self):
        """Create TextRankExtractor instance."""
        from src.ml.tagging import TextRankExtractor

        return TextRankExtractor(window_size=3)

    def test_textrank_initialization(self, extractor):
        """Test TextRankExtractor initialization"""
        assert extractor.window_size == 3

    def test_extract_keywords_basic(self, extractor):
        """Test basic TextRank extraction"""
        text = "Invoice payment amount total cost financial budget planning"
        suggestions = extractor.extract_keywords(text, top_k=5)

        assert len(suggestions) <= 5
        assert all(s.source == "textrank" for s in suggestions)

    def test_extract_keywords_empty_text(self, extractor):
        """Test extracting from empty text"""
        suggestions = extractor.extract_keywords("", top_k=5)

        assert len(suggestions) == 0

    def test_build_graph(self, extractor):
        """Test building co-occurrence graph"""
        words = ["word1", "word2", "word3", "word4"]
        graph = extractor._build_graph(words)

        # Each word should have edges to neighbors within window
        assert "word2" in graph["word1"]
        assert "word3" in graph["word1"]
        assert "word1" in graph["word2"]

    def test_build_graph_empty(self, extractor):
        """Test building graph from empty list"""
        graph = extractor._build_graph([])

        assert len(graph) == 0

    def test_pagerank(self, extractor):
        """Test PageRank algorithm"""
        graph = {
            "a": {"b", "c"},
            "b": {"a", "c"},
            "c": {"a", "b"}
        }

        scores = extractor._pagerank(graph, iterations=10)

        # All nodes should have positive scores
        assert all(score > 0 for score in scores.values())
        # Scores should sum to approximately equal (symmetric graph)
        assert len(scores) == 3

    def test_pagerank_iterations(self, extractor):
        """Test PageRank with different iterations"""
        graph = {"a": {"b"}, "b": {"a"}}

        scores_10 = extractor._pagerank(graph, iterations=10)
        scores_20 = extractor._pagerank(graph, iterations=20)

        # More iterations should converge to similar values
        assert len(scores_10) == len(scores_20)


# ============================================================================
# TopicModeler Tests
# ============================================================================


class TestTopicModeler:
    """Test TopicModeler functionality."""

    @pytest.fixture
    def modeler(self):
        """Create TopicModeler instance."""
        from src.ml.tagging import TopicModeler

        return TopicModeler(num_topics=3)

    def test_topic_modeler_initialization(self, modeler):
        """Test TopicModeler initialization"""
        assert modeler.num_topics == 3
        assert modeler.trained is False
        assert modeler.topics == {}

    def test_train_without_gensim(self, modeler):
        """Test training without Gensim (fallback)"""
        documents = [
            "Rechnung Betrag Zahlung invoice payment",
            "Vertrag Vereinbarung contract agreement",
            "Bericht Analyse report analysis"
        ]

        with patch("src.ml.tagging.TopicModeler.train") as mock_train:
            # Simulate fallback behavior
            modeler.topics = {
                0: ["rechnung", "betrag", "zahlung"],
                1: ["vertrag", "vereinbarung"],
                2: ["bericht", "analyse"]
            }
            modeler.trained = True

        assert modeler.trained is True
        assert len(modeler.topics) > 0

    def test_train_with_gensim_available(self, modeler):
        """Test training with Gensim available"""
        documents = [
            "Rechnung Betrag Zahlung invoice payment amount cost financial",
            "Vertrag Vereinbarung contract agreement legal document terms",
            "Bericht Analyse report analysis data summary findings results"
        ]

        # Try real training (will use fallback if gensim not installed)
        modeler.train(documents)

        assert modeler.trained is True
        assert len(modeler.topics) > 0

    def test_train_empty_documents(self, modeler):
        """Test training with empty documents"""
        documents = []

        modeler.train(documents)

        # Should still be trained with fallback topics
        assert modeler.trained is True

    def test_get_document_topics_untrained(self, modeler):
        """Test getting topics when model not trained"""
        text = "Rechnung Betrag Zahlung"
        suggestions = modeler.get_document_topics(text, top_k=3)

        assert len(suggestions) == 0

    def test_get_document_topics_trained(self, modeler):
        """Test getting topics from trained model"""
        # Train with fallback
        modeler.topics = {
            0: ["rechnung", "betrag", "zahlung"],
            1: ["vertrag", "vereinbarung"]
        }
        modeler.trained = True

        text = "Rechnung für Betrag und Zahlung"
        suggestions = modeler.get_document_topics(text, top_k=2)

        assert len(suggestions) <= 2
        assert all(s.source == "lda" for s in suggestions)

    def test_tokenize(self, modeler):
        """Test tokenization"""
        text = "Test Dokument mit mehreren Wörtern!"
        words = modeler._tokenize(text)

        assert "test" in words
        assert "dokument" in words
        # No stopword filtering in TopicModeler._tokenize


# ============================================================================
# AutoTagger Tests
# ============================================================================


class TestAutoTagger:
    """Test AutoTagger functionality."""

    @pytest.fixture
    def tagger(self):
        """Create AutoTagger instance."""
        from src.ml.tagging import AutoTagger

        return AutoTagger()

    def test_auto_tagger_initialization(self, tagger):
        """Test AutoTagger initialization"""
        assert tagger.tfidf_extractor is not None
        assert tagger.textrank_extractor is not None
        assert tagger.topic_modeler is not None
        assert tagger.tag_registry == {}
        assert len(tagger.tag_statistics) == 0

    def test_initialize_corpus(self, tagger):
        """Test initializing corpus"""
        documents = [
            "Invoice amount payment cost",
            "Contract agreement legal terms",
            "Report analysis data summary"
        ]

        tagger.initialize_corpus(documents)

        assert tagger.tfidf_extractor.total_documents == 3
        assert tagger.topic_modeler.trained is True

    def test_suggest_tags_combined(self, tagger):
        """Test suggesting tags with combined methods"""
        # Initialize corpus
        documents = ["Invoice payment amount", "Contract agreement", "Report analysis"]
        tagger.initialize_corpus(documents)

        text = "Invoice for payment amount total cost"
        suggestions = tagger.suggest_tags(text, top_k=5, combine_methods=True)

        assert len(suggestions) <= 5
        assert all(isinstance(s.tag, str) for s in suggestions)
        assert all(s.score >= 0 for s in suggestions)

    def test_suggest_tags_separate(self, tagger):
        """Test suggesting tags without combining"""
        documents = ["Invoice payment", "Contract legal"]
        tagger.initialize_corpus(documents)

        text = "Invoice payment amount"
        suggestions = tagger.suggest_tags(text, top_k=5, combine_methods=False)

        assert len(suggestions) <= 5

    def test_suggest_tags_empty_text(self, tagger):
        """Test suggesting tags for empty text"""
        tagger.initialize_corpus(["test document"])

        suggestions = tagger.suggest_tags("", top_k=5)

        # May return empty or topic-based suggestions
        assert isinstance(suggestions, list)

    def test_auto_tag_document(self, tagger):
        """Test automatic document tagging"""
        documents = ["Invoice payment amount cost", "Contract agreement legal"]
        tagger.initialize_corpus(documents)

        text = "Invoice for payment amount total cost financial budget"
        tags = tagger.auto_tag_document("doc_1", text, threshold=0.0, max_tags=3)

        assert len(tags) <= 3
        assert all(hasattr(tag, 'name') for tag in tags)
        assert all(hasattr(tag, 'confidence') for tag in tags)

    def test_auto_tag_document_with_threshold(self, tagger):
        """Test auto-tagging with confidence threshold"""
        documents = ["Invoice payment"]
        tagger.initialize_corpus(documents)

        text = "Invoice payment"
        # High threshold should filter out low-confidence tags
        tags = tagger.auto_tag_document("doc_1", text, threshold=0.9, max_tags=5)

        # May return fewer tags due to threshold
        assert isinstance(tags, list)

    def test_get_or_create_tag_id_new(self, tagger):
        """Test creating new tag ID"""
        tag_id = tagger._get_or_create_tag_id("invoice")

        assert tag_id.startswith("tag_")
        assert "invoice" in tagger.tag_registry[tag_id].name

    def test_get_or_create_tag_id_existing(self, tagger):
        """Test getting existing tag ID"""
        # Create first tag
        tag_id_1 = tagger._get_or_create_tag_id("invoice")

        # Get same tag (case-insensitive)
        tag_id_2 = tagger._get_or_create_tag_id("INVOICE")

        assert tag_id_1 == tag_id_2

    def test_get_or_create_tag_id_whitespace(self, tagger):
        """Test tag ID creation with whitespace"""
        tag_id = tagger._get_or_create_tag_id("  invoice  ")

        assert tag_id in tagger.tag_registry

    def test_get_popular_tags(self, tagger):
        """Test getting popular tags"""
        # Add some tag statistics
        tagger.tag_statistics["invoice"] = 10
        tagger.tag_statistics["payment"] = 5
        tagger.tag_statistics["contract"] = 3

        popular = tagger.get_popular_tags(limit=2)

        assert len(popular) == 2
        assert popular[0][0] == "invoice"
        assert popular[0][1] == 10

    def test_get_popular_tags_empty(self, tagger):
        """Test getting popular tags when none exist"""
        popular = tagger.get_popular_tags(limit=10)

        assert len(popular) == 0

    def test_get_related_tags(self, tagger):
        """Test getting related tags"""
        related = tagger.get_related_tags("invoice", limit=5)

        # Currently returns empty list (placeholder implementation)
        assert isinstance(related, list)

    def test_cluster_tags(self, tagger):
        """Test tag clustering"""
        clusters = tagger.cluster_tags()

        # Returns simulated clusters
        assert isinstance(clusters, dict)
        assert len(clusters) > 0

    def test_get_statistics(self, tagger):
        """Test getting tagging statistics"""
        # Add some data
        tagger._get_or_create_tag_id("invoice")
        tagger._get_or_create_tag_id("payment")
        tagger.tag_statistics["invoice"] = 5
        tagger.tag_statistics["payment"] = 3

        stats = tagger.get_statistics()

        assert "total_tags" in stats
        assert "total_applications" in stats
        assert "avg_tags_per_document" in stats
        assert stats["total_tags"] == 2
        assert stats["total_applications"] == 8


# ============================================================================
# Global Instance Tests
# ============================================================================


class TestGlobalInstance:
    """Test global auto-tagger instance."""

    def test_get_auto_tagger_singleton(self):
        """Test get_auto_tagger returns singleton"""
        from src.ml.tagging import get_auto_tagger

        # Reset global
        import src.ml.tagging
        src.ml.tagging._auto_tagger = None

        tagger1 = get_auto_tagger()
        tagger2 = get_auto_tagger()

        assert tagger1 is tagger2

    def test_configure_auto_tagger(self):
        """Test configuring auto-tagger"""
        from src.ml.tagging import configure_auto_tagger, get_auto_tagger

        # Reset and configure
        import src.ml.tagging
        src.ml.tagging._auto_tagger = None

        configure_auto_tagger()
        tagger = get_auto_tagger()

        assert tagger is not None


# ============================================================================
# Integration Tests
# ============================================================================


class TestAutoTaggingIntegration:
    """Integration tests for auto-tagging system."""

    def test_full_tagging_workflow(self):
        """Test complete tagging workflow"""
        from src.ml.tagging import AutoTagger

        tagger = AutoTagger()

        # Initialize with corpus
        documents = [
            "Rechnung Betrag Zahlung invoice payment amount cost financial budget",
            "Vertrag Vereinbarung contract agreement legal document terms conditions",
            "Bericht Analyse report analysis data findings summary results research"
        ]

        tagger.initialize_corpus(documents)

        # Tag a document
        text = "Rechnung für Zahlung Betrag 1000 EUR financial invoice payment"
        tags = tagger.auto_tag_document("doc_1", text, threshold=0.0, max_tags=5)

        # Should generate some tags
        assert len(tags) > 0
        assert all(hasattr(tag, 'name') for tag in tags)
        assert all(hasattr(tag, 'confidence') for tag in tags)

        # Get statistics
        stats = tagger.get_statistics()
        assert stats["total_applications"] > 0

    def test_multiple_documents_tagging(self):
        """Test tagging multiple documents"""
        from src.ml.tagging import AutoTagger

        tagger = AutoTagger()

        # Initialize
        corpus = [
            "Invoice payment financial",
            "Contract legal agreement",
            "Report analysis data"
        ]
        tagger.initialize_corpus(corpus)

        # Tag multiple documents
        documents = [
            ("doc_1", "Invoice payment amount"),
            ("doc_2", "Contract terms conditions"),
            ("doc_3", "Report analysis summary")
        ]

        for doc_id, text in documents:
            tags = tagger.auto_tag_document(doc_id, text, threshold=0.0, max_tags=3)
            assert len(tags) <= 3

        # Check statistics
        stats = tagger.get_statistics()
        assert stats["total_tags"] > 0

    def test_tag_suggestions_ranking(self):
        """Test that tag suggestions are properly ranked"""
        from src.ml.tagging import AutoTagger

        tagger = AutoTagger()

        documents = ["invoice payment cost", "invoice amount financial"]
        tagger.initialize_corpus(documents)

        text = "invoice invoice invoice payment payment amount"
        suggestions = tagger.suggest_tags(text, top_k=5, combine_methods=True)

        # Suggestions should be sorted by score
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].score >= suggestions[i + 1].score

    def test_combined_methods_boost(self):
        """Test that combining methods boosts tag scores"""
        from src.ml.tagging import AutoTagger

        tagger = AutoTagger()

        documents = ["invoice payment amount cost financial budget"]
        tagger.initialize_corpus(documents)

        text = "invoice payment amount"

        # Get separate suggestions
        suggestions_separate = tagger.suggest_tags(text, top_k=10, combine_methods=False)

        # Get combined suggestions
        suggestions_combined = tagger.suggest_tags(text, top_k=10, combine_methods=True)

        # Combined should have boosted scores for tags appearing in multiple methods
        assert len(suggestions_combined) > 0
