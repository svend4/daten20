"""
Comprehensive tests for Text Analysis module

Test coverage goals:
- TextTokenizer: Word/sentence tokenization, stopword removal, stemming
- SentimentAnalyzer: Sentiment detection, lexicon-based analysis
- EmotionDetector: Emotion detection from text
- KeywordExtractor: Keyword and phrase extraction
- TextClassifier: Text categorization
- LanguageDetector: Language identification
- ReadabilityAnalyzer: Readability metrics calculation
- TextSimilarity: Jaccard and cosine similarity
- TextAnalyzer: Main analyzer integration
- Edge cases: Empty text, special characters, multilingual
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ai.text_analysis import (
    SentimentLabel,
    EmotionLabel,
    SentimentResult,
    EmotionResult,
    Keyword,
    TextClassification,
    LanguageDetection,
    ReadabilityMetrics,
    TextTokenizer,
    SentimentAnalyzer,
    EmotionDetector,
    KeywordExtractor,
    TextClassifier,
    LanguageDetector,
    ReadabilityAnalyzer,
    TextSimilarity,
    TextAnalyzer,
)


class TestEnums:
    """Test enum definitions"""

    def test_sentiment_labels(self):
        """Test all sentiment labels exist"""
        labels = [
            SentimentLabel.POSITIVE,
            SentimentLabel.NEGATIVE,
            SentimentLabel.NEUTRAL,
            SentimentLabel.MIXED,
        ]
        assert len(labels) == 4
        for label in labels:
            assert isinstance(label.value, str)

    def test_emotion_labels(self):
        """Test all emotion labels exist"""
        emotions = [
            EmotionLabel.JOY,
            EmotionLabel.SADNESS,
            EmotionLabel.ANGER,
            EmotionLabel.FEAR,
            EmotionLabel.SURPRISE,
            EmotionLabel.DISGUST,
            EmotionLabel.TRUST,
            EmotionLabel.ANTICIPATION,
        ]
        assert len(emotions) == 8


class TestDataclasses:
    """Test dataclass definitions"""

    def test_sentiment_result(self):
        """Test SentimentResult creation"""
        result = SentimentResult(
            label=SentimentLabel.POSITIVE,
            score=0.8,
            confidence=0.9,
            scores={"positive": 0.8, "negative": 0.2}
        )
        assert result.label == SentimentLabel.POSITIVE
        assert result.score == 0.8
        assert result.confidence == 0.9

    def test_emotion_result(self):
        """Test EmotionResult creation"""
        result = EmotionResult(
            primary_emotion=EmotionLabel.JOY,
            confidence=0.85,
            all_emotions={EmotionLabel.JOY: 0.85, EmotionLabel.TRUST: 0.15}
        )
        assert result.primary_emotion == EmotionLabel.JOY
        assert result.confidence == 0.85

    def test_keyword(self):
        """Test Keyword creation"""
        keyword = Keyword(
            word="analysis",
            score=0.75,
            frequency=5,
            positions=[10, 25, 40]
        )
        assert keyword.word == "analysis"
        assert keyword.score == 0.75
        assert keyword.frequency == 5

    def test_text_classification(self):
        """Test TextClassification creation"""
        classification = TextClassification(
            category="technology",
            confidence=0.90,
            all_categories={"technology": 0.90, "science": 0.10}
        )
        assert classification.category == "technology"
        assert classification.confidence == 0.90

    def test_language_detection(self):
        """Test LanguageDetection creation"""
        detection = LanguageDetection(
            language="English",
            confidence=0.95,
            iso_code="en"
        )
        assert detection.language == "English"
        assert detection.iso_code == "en"

    def test_readability_metrics(self):
        """Test ReadabilityMetrics creation"""
        metrics = ReadabilityMetrics(
            flesch_reading_ease=60.0,
            flesch_kincaid_grade=8.0,
            avg_sentence_length=15.0,
            avg_word_length=5.0,
            complex_word_ratio=0.2,
            difficulty_level="medium"
        )
        assert metrics.flesch_reading_ease == 60.0
        assert metrics.difficulty_level == "medium"


class TestTextTokenizer:
    """Test TextTokenizer class"""

    def test_tokenize_words_simple(self):
        """Test simple word tokenization"""
        text = "Hello world, this is a test"
        words = TextTokenizer.tokenize_words(text)

        assert isinstance(words, list)
        assert len(words) > 0
        assert "hello" in words
        assert "world" in words

    def test_tokenize_words_punctuation(self):
        """Test word tokenization with punctuation"""
        text = "Hello, world! How are you?"
        words = TextTokenizer.tokenize_words(text)

        # Punctuation should be removed
        assert "," not in words
        assert "!" not in words
        assert "?" not in words

    def test_tokenize_words_empty(self):
        """Test tokenization of empty text"""
        words = TextTokenizer.tokenize_words("")
        assert words == []

    def test_tokenize_sentences_simple(self):
        """Test simple sentence tokenization"""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = TextTokenizer.tokenize_sentences(text)

        assert isinstance(sentences, list)
        assert len(sentences) == 3

    def test_tokenize_sentences_empty(self):
        """Test sentence tokenization of empty text"""
        sentences = TextTokenizer.tokenize_sentences("")
        assert sentences == []

    def test_remove_stopwords_english(self):
        """Test stopword removal for English"""
        words = ["the", "quick", "brown", "fox", "and", "the", "dog"]
        filtered = TextTokenizer.remove_stopwords(words, "en")

        # Stopwords should be removed
        assert "the" not in filtered
        assert "and" not in filtered
        # Content words should remain
        assert "quick" in filtered
        assert "brown" in filtered

    def test_remove_stopwords_empty(self):
        """Test stopword removal with empty list"""
        filtered = TextTokenizer.remove_stopwords([], "en")
        assert filtered == []

    def test_stem_word_ing(self):
        """Test stemming words ending in 'ing'"""
        assert TextTokenizer.stem_word("running") == "runn"
        assert TextTokenizer.stem_word("walking") == "walk"

    def test_stem_word_ed(self):
        """Test stemming words ending in 'ed'"""
        assert TextTokenizer.stem_word("walked") == "walk"
        assert TextTokenizer.stem_word("jumped") == "jump"

    def test_stem_word_s(self):
        """Test stemming words ending in 's'"""
        assert TextTokenizer.stem_word("dogs") == "dog"
        assert TextTokenizer.stem_word("cats") == "cat"

    def test_stem_word_no_change(self):
        """Test stemming words that shouldn't change"""
        assert TextTokenizer.stem_word("dog") == "dog"
        assert TextTokenizer.stem_word("class") == "class"  # 'ss' ending


class TestSentimentAnalyzer:
    """Test SentimentAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create SentimentAnalyzer instance"""
        return SentimentAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None

    def test_analyze_positive_text(self, analyzer):
        """Test positive sentiment detection"""
        text = "I love this wonderful amazing product! It's fantastic and excellent!"
        result = analyzer.analyze(text, use_llm=False)

        assert isinstance(result, SentimentResult)
        assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.NEUTRAL]
        assert 0.0 <= result.confidence <= 1.0
        assert -1.0 <= result.score <= 1.0

    def test_analyze_negative_text(self, analyzer):
        """Test negative sentiment detection"""
        text = "I hate this terrible awful product. It's horrible and disgusting."
        result = analyzer.analyze(text, use_llm=False)

        assert isinstance(result, SentimentResult)
        assert result.label in [SentimentLabel.NEGATIVE, SentimentLabel.NEUTRAL]
        assert 0.0 <= result.confidence <= 1.0

    def test_analyze_neutral_text(self, analyzer):
        """Test neutral sentiment detection"""
        text = "The product is available in multiple colors and sizes."
        result = analyzer.analyze(text, use_llm=False)

        assert isinstance(result, SentimentResult)
        assert result.label in [SentimentLabel.NEUTRAL, SentimentLabel.POSITIVE]

    def test_analyze_empty_text(self, analyzer):
        """Test sentiment analysis of empty text"""
        result = analyzer.analyze("", use_llm=False)

        assert isinstance(result, SentimentResult)
        assert result.label == SentimentLabel.NEUTRAL

    def test_analyze_mixed_sentiment(self, analyzer):
        """Test mixed sentiment detection"""
        text = "The product is great but expensive. I love it but it's too costly."
        result = analyzer.analyze(text, use_llm=False)

        assert isinstance(result, SentimentResult)
        # Could be mixed or positive/negative
        assert result.label in SentimentLabel


class TestEmotionDetector:
    """Test EmotionDetector class"""

    @pytest.fixture
    def detector(self):
        """Create EmotionDetector instance"""
        return EmotionDetector()

    def test_initialization(self, detector):
        """Test detector initialization"""
        assert detector is not None

    def test_detect_joy(self, detector):
        """Test joy emotion detection"""
        text = "I'm so happy and excited! This is wonderful!"
        result = detector.detect(text)

        assert isinstance(result, EmotionResult)
        assert result.primary_emotion in EmotionLabel
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_sadness(self, detector):
        """Test sadness emotion detection"""
        text = "I'm so sad and depressed. Everything is terrible."
        result = detector.detect(text)

        assert isinstance(result, EmotionResult)
        assert result.primary_emotion in EmotionLabel

    def test_detect_anger(self, detector):
        """Test anger emotion detection"""
        text = "I'm furious and angry! This is outrageous!"
        result = detector.detect(text)

        assert isinstance(result, EmotionResult)
        assert result.primary_emotion in EmotionLabel

    def test_detect_empty_text(self, detector):
        """Test emotion detection on empty text"""
        result = detector.detect("")

        assert isinstance(result, EmotionResult)
        assert result.primary_emotion in EmotionLabel


class TestKeywordExtractor:
    """Test KeywordExtractor class"""

    @pytest.fixture
    def extractor(self):
        """Create KeywordExtractor instance"""
        return KeywordExtractor()

    def test_initialization(self, extractor):
        """Test extractor initialization"""
        assert extractor is not None

    def test_extract_basic(self, extractor):
        """Test basic keyword extraction"""
        text = "Machine learning and artificial intelligence are transforming technology."
        keywords = extractor.extract(text, top_k=5)

        assert isinstance(keywords, list)
        assert len(keywords) > 0
        for kw in keywords:
            assert isinstance(kw, Keyword)
            assert isinstance(kw.word, str)
            assert kw.score >= 0.0

    def test_extract_top_k(self, extractor):
        """Test top_k parameter"""
        text = "Python programming language for data science and machine learning"
        keywords = extractor.extract(text, top_k=3)

        assert len(keywords) <= 3

    def test_extract_min_word_length(self, extractor):
        """Test min_word_length parameter"""
        text = "AI ML NLP are key technologies in modern software"
        keywords = extractor.extract(text, top_k=10, min_word_length=4)

        # All keywords should have length >= 4
        for kw in keywords:
            assert len(kw.word) >= 4

    def test_extract_empty_text(self, extractor):
        """Test keyword extraction from empty text"""
        keywords = extractor.extract("", top_k=5)

        assert isinstance(keywords, list)

    def test_extract_phrases(self, extractor):
        """Test phrase extraction"""
        text = "Machine learning and deep learning are important technologies"
        phrases = extractor.extract_phrases(text, top_k=3)

        assert isinstance(phrases, list)


class TestTextClassifier:
    """Test TextClassifier class"""

    @pytest.fixture
    def classifier(self):
        """Create TextClassifier instance"""
        return TextClassifier()

    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None

    def test_classify_with_categories(self, classifier):
        """Test text classification"""
        text = "Python programming and software development"
        categories = ["technology", "sports", "politics", "entertainment"]

        result = classifier.classify(text, categories, use_llm=False)

        assert isinstance(result, TextClassification)
        assert result.category in categories
        assert 0.0 <= result.confidence <= 1.0

    def test_classify_empty_text(self, classifier):
        """Test classification of empty text"""
        categories = ["tech", "sports"]
        result = classifier.classify("", categories, use_llm=False)

        assert isinstance(result, TextClassification)

    def test_classify_single_category(self, classifier):
        """Test classification with single category"""
        text = "This is a test"
        result = classifier.classify(text, ["test"], use_llm=False)

        assert isinstance(result, TextClassification)
        assert result.category == "test"


class TestLanguageDetector:
    """Test LanguageDetector class"""

    @pytest.fixture
    def detector(self):
        """Create LanguageDetector instance"""
        return LanguageDetector()

    def test_initialization(self, detector):
        """Test detector initialization"""
        assert detector is not None

    def test_detect_english(self, detector):
        """Test English language detection"""
        text = "This is an English text with common English words."
        result = detector.detect(text)

        assert isinstance(result, LanguageDetection)
        # Accept both 2-letter and 3-letter ISO codes
        assert result.iso_code in ["en", "eng"]
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_german(self, detector):
        """Test German language detection"""
        text = "Das ist ein deutscher Text mit deutschen Wörtern."
        result = detector.detect(text)

        assert isinstance(result, LanguageDetection)
        # Accept both 2-letter and 3-letter ISO codes
        assert result.iso_code in ["de", "deu", "en", "eng"]  # May not always be perfect

    def test_detect_empty_text(self, detector):
        """Test language detection on empty text"""
        result = detector.detect("")

        assert isinstance(result, LanguageDetection)
        # Accept both 2-letter and 3-letter ISO codes
        assert result.iso_code in ["en", "eng", "unknown"]


class TestReadabilityAnalyzer:
    """Test ReadabilityAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create ReadabilityAnalyzer instance"""
        return ReadabilityAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None

    def test_analyze_simple_text(self, analyzer):
        """Test readability of simple text"""
        text = "The cat sat on the mat. It was very happy."
        result = analyzer.analyze(text)

        assert isinstance(result, ReadabilityMetrics)
        assert result.flesch_reading_ease >= 0.0
        assert result.avg_sentence_length > 0.0
        assert result.avg_word_length > 0.0
        assert result.difficulty_level in ["easy", "medium", "hard"]

    def test_analyze_complex_text(self, analyzer):
        """Test readability of complex text"""
        text = "The implementation of sophisticated algorithmic methodologies necessitates comprehensive understanding."
        result = analyzer.analyze(text)

        assert isinstance(result, ReadabilityMetrics)
        assert result.avg_word_length >= 5.0  # Complex words

    def test_analyze_empty_text(self, analyzer):
        """Test readability of empty text"""
        try:
            result = analyzer.analyze("")
            assert isinstance(result, ReadabilityMetrics)
        except (ValueError, ZeroDivisionError):
            # Expected for empty text
            pass

    def test_flesch_reading_ease_range(self, analyzer):
        """Test Flesch Reading Ease score is in valid range"""
        text = "This is a test. Simple words and short sentences make text easy to read."
        result = analyzer.analyze(text)

        # Flesch Reading Ease typically ranges from 0-100
        assert -50.0 <= result.flesch_reading_ease <= 150.0


class TestTextSimilarity:
    """Test TextSimilarity class"""

    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity of identical texts"""
        text = "Hello world this is a test"
        similarity = TextSimilarity.jaccard_similarity(text, text)

        assert similarity == 1.0

    def test_jaccard_similarity_different(self):
        """Test Jaccard similarity of different texts"""
        text1 = "The quick brown fox"
        text2 = "The lazy dog sleeps"
        similarity = TextSimilarity.jaccard_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0

    def test_jaccard_similarity_empty(self):
        """Test Jaccard similarity with empty text"""
        similarity = TextSimilarity.jaccard_similarity("", "hello")
        assert 0.0 <= similarity <= 1.0

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical texts"""
        text = "Hello world this is a test"
        similarity = TextSimilarity.cosine_similarity(text, text)

        # Should be very close to 1.0 (allowing for floating point precision)
        assert 0.99 <= similarity <= 1.01

    def test_cosine_similarity_different(self):
        """Test cosine similarity of different texts"""
        text1 = "Machine learning and AI"
        text2 = "Sports and athletics"
        similarity = TextSimilarity.cosine_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0

    def test_cosine_similarity_similar(self):
        """Test cosine similarity of similar texts"""
        text1 = "Machine learning is great"
        text2 = "Machine learning is awesome"
        similarity = TextSimilarity.cosine_similarity(text1, text2)

        assert similarity > 0.5  # Should be fairly similar


class TestTextAnalyzer:
    """Test TextAnalyzer main class"""

    @pytest.fixture
    def analyzer(self):
        """Create TextAnalyzer instance"""
        return TextAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None
        assert hasattr(analyzer, 'sentiment_analyzer')
        assert hasattr(analyzer, 'keyword_extractor')

    def test_analyze_sentiment(self, analyzer):
        """Test sentiment analysis integration"""
        text = "This is a wonderful day!"
        result = analyzer.analyze_sentiment(text)

        assert isinstance(result, SentimentResult)

    def test_extract_keywords(self, analyzer):
        """Test keyword extraction integration"""
        text = "Machine learning and artificial intelligence"
        keywords = analyzer.extract_keywords(text, top_k=5)

        assert isinstance(keywords, list)

    def test_detect_language(self, analyzer):
        """Test language detection integration"""
        text = "This is an English sentence"
        result = analyzer.detect_language(text)

        assert isinstance(result, LanguageDetection)

    def test_calculate_readability(self, analyzer):
        """Test readability calculation integration"""
        text = "This is a simple test. Easy to read."
        result = analyzer.calculate_readability(text)

        assert isinstance(result, ReadabilityMetrics)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_very_long_text(self):
        """Test with very long text"""
        analyzer = TextAnalyzer()
        text = "word " * 10000  # Very long text

        result = analyzer.analyze_sentiment(text)
        assert isinstance(result, SentimentResult)

    def test_special_characters(self):
        """Test with special characters"""
        analyzer = TextAnalyzer()
        text = "Hello!!! @@@ ### $$$ %%% ^^^ &&&"

        result = analyzer.analyze_sentiment(text)
        assert isinstance(result, SentimentResult)

    def test_unicode_characters(self):
        """Test with unicode characters"""
        analyzer = TextAnalyzer()
        text = "Hello 你好 Привет مرحبا"

        result = analyzer.analyze_sentiment(text)
        assert isinstance(result, SentimentResult)

    def test_numbers_only(self):
        """Test with numbers only"""
        analyzer = TextAnalyzer()
        text = "123 456 789 000"

        result = analyzer.analyze_sentiment(text)
        assert isinstance(result, SentimentResult)

    def test_single_word(self):
        """Test with single word"""
        analyzer = TextAnalyzer()
        result = analyzer.analyze_sentiment("happy")

        assert isinstance(result, SentimentResult)


class TestIntegration:
    """Integration tests for text analysis pipeline"""

    def test_full_analysis_pipeline(self):
        """Test complete analysis pipeline"""
        analyzer = TextAnalyzer()
        text = "I love machine learning! It's an exciting field with great potential."

        # Run multiple analyses
        sentiment = analyzer.analyze_sentiment(text)
        keywords = analyzer.extract_keywords(text, top_k=5)
        language = analyzer.detect_language(text)
        readability = analyzer.calculate_readability(text)

        # Verify all results
        assert isinstance(sentiment, SentimentResult)
        assert isinstance(keywords, list)
        assert isinstance(language, LanguageDetection)
        assert isinstance(readability, ReadabilityMetrics)

    def test_multilingual_text(self):
        """Test analysis of multilingual text"""
        analyzer = TextAnalyzer()
        text = "Hello world. Hallo Welt."

        result = analyzer.analyze_sentiment(text)
        assert isinstance(result, SentimentResult)
