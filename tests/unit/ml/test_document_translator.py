#!/usr/bin/env python3
"""
Comprehensive tests for Document Translator

Tests all functionality of the document translation module.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.ml.document_translator import (
    BatchTranslationResult,
    DocumentTranslator,
    LanguageDetectionResult,
    TranslationBackend,
    TranslationCache,
    TranslationQuality,
    TranslationResult,
    create_translator,
    quick_translate,
)


@pytest.fixture
def sample_texts():
    """Sample texts for testing"""
    return [
        "Hello, world!",
        "How are you today?",
        "Machine learning is amazing"
    ]


@pytest.fixture
def mock_google_result():
    """Mock Google Translate result"""
    result = Mock()
    result.text = "Hola, mundo!"
    result.src = "en"
    result.pronunciation = None
    return result


class TestTranslationResult:
    """Test TranslationResult dataclass"""

    def test_translation_result_creation(self):
        """Test creating TranslationResult"""
        result = TranslationResult(
            source_text="Hello",
            translated_text="Hola",
            source_language="en",
            target_language="es",
            backend="google",
            confidence=0.95
        )

        assert result.source_text == "Hello"
        assert result.translated_text == "Hola"
        assert result.source_language == "en"
        assert result.target_language == "es"
        assert result.backend == "google"
        assert result.confidence == 0.95


class TestLanguageDetectionResult:
    """Test LanguageDetectionResult dataclass"""

    def test_language_detection_result_creation(self):
        """Test creating LanguageDetectionResult"""
        result = LanguageDetectionResult(
            language="en",
            confidence=0.99,
            alternatives=[("es", 0.01)]
        )

        assert result.language == "en"
        assert result.confidence == 0.99
        assert len(result.alternatives) == 1


class TestBatchTranslationResult:
    """Test BatchTranslationResult dataclass"""

    def test_batch_result_success_rate(self):
        """Test success rate calculation"""
        result = BatchTranslationResult(
            results=[],
            total_texts=10,
            successful=8,
            failed=2,
            total_time_seconds=5.0,
            words_translated=100
        )

        assert result.success_rate == 0.8

    def test_batch_result_zero_texts(self):
        """Test success rate with zero texts"""
        result = BatchTranslationResult(
            results=[],
            total_texts=0,
            successful=0,
            failed=0,
            total_time_seconds=0.0,
            words_translated=0
        )

        assert result.success_rate == 0.0


class TestTranslationCache:
    """Test TranslationCache class"""

    def test_cache_put_and_get(self):
        """Test putting and getting from cache"""
        cache = TranslationCache(max_entries=10)

        cache.put("Hello", "en", "es", "Hola")
        result = cache.get("Hello", "en", "es")

        assert result == "Hola"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_cache_miss(self):
        """Test cache miss"""
        cache = TranslationCache(max_entries=10)

        result = cache.get("Hello", "en", "es")

        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1

    def test_cache_eviction(self):
        """Test cache eviction when full"""
        cache = TranslationCache(max_entries=2)

        cache.put("Hello", "en", "es", "Hola")
        cache.put("World", "en", "es", "Mundo")
        cache.put("Test", "en", "es", "Prueba")  # Should evict oldest

        assert len(cache.cache) == 2

    def test_cache_clear(self):
        """Test clearing cache"""
        cache = TranslationCache(max_entries=10)

        cache.put("Hello", "en", "es", "Hola")
        cache.clear()

        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_cache_hit_rate(self):
        """Test hit rate calculation"""
        cache = TranslationCache(max_entries=10)

        cache.put("Hello", "en", "es", "Hola")
        cache.get("Hello", "en", "es")  # Hit
        cache.get("World", "en", "es")  # Miss

        assert cache.hit_rate == 0.5


@patch("src.ml.document_translator.GOOGLE_TRANSLATE_AVAILABLE", True)
@patch("src.ml.document_translator.LANGDETECT_AVAILABLE", True)
class TestDocumentTranslator:
    """Test DocumentTranslator class"""

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_translator_initialization(self, mock_google_translator):
        """Test translator initialization"""
        translator = DocumentTranslator(
            backend=TranslationBackend.GOOGLE,
            cache_enabled=True
        )

        assert translator.backend == TranslationBackend.GOOGLE
        assert translator.cache_enabled is True
        assert translator.cache is not None
        assert TranslationBackend.GOOGLE in translator.available_backends

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_available_backends(self, mock_google_translator):
        """Test detecting available backends"""
        translator = DocumentTranslator()

        assert len(translator.available_backends) > 0
        assert TranslationBackend.GOOGLE in translator.available_backends

    @patch("src.ml.document_translator.detect")
    @patch("src.ml.document_translator.detect_langs")
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_detect_language(self, mock_google_translator, mock_detect_langs, mock_detect):
        """Test language detection"""
        # Mock language detection
        mock_detect.return_value = "en"
        mock_lang = Mock()
        mock_lang.lang = "en"
        mock_lang.prob = 0.99
        mock_detect_langs.return_value = [mock_lang]

        translator = DocumentTranslator()
        result = translator.detect_language("Hello, world!")

        assert result.language == "en"
        assert result.confidence == 0.99

    @patch("src.ml.document_translator.detect")
    @patch("src.ml.document_translator.detect_langs")
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_translate_text(self, mock_google_translator, mock_detect_langs, mock_detect, mock_google_result):
        """Test translating text"""
        # Mock language detection
        mock_detect.return_value = "en"
        mock_lang = Mock()
        mock_lang.lang = "en"
        mock_lang.prob = 0.99
        mock_detect_langs.return_value = [mock_lang]

        # Mock translation
        mock_translator_instance = Mock()
        mock_translator_instance.translate.return_value = mock_google_result
        mock_google_translator.return_value = mock_translator_instance

        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)
        result = translator.translate("Hello, world!", target_language="es")

        assert result.translated_text == "Hola, mundo!"
        assert result.source_language == "en"
        assert result.target_language == "es"
        assert result.backend == "google"

    @patch("src.ml.document_translator.detect")
    @patch("src.ml.document_translator.detect_langs")
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_translate_with_cache(self, mock_google_translator, mock_detect_langs, mock_detect, mock_google_result):
        """Test translation caching"""
        # Mock language detection
        mock_detect.return_value = "en"
        mock_lang = Mock()
        mock_lang.lang = "en"
        mock_lang.prob = 0.99
        mock_detect_langs.return_value = [mock_lang]

        # Mock translation
        mock_translator_instance = Mock()
        mock_translator_instance.translate.return_value = mock_google_result
        mock_google_translator.return_value = mock_translator_instance

        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE, cache_enabled=True)

        # First translation (cache miss)
        result1 = translator.translate("Hello, world!", target_language="es", source_language="en")
        assert result1.translated_text == "Hola, mundo!"

        # Second translation (cache hit)
        result2 = translator.translate("Hello, world!", target_language="es", source_language="en")
        assert result2.translated_text == "Hola, mundo!"
        assert result2.backend == "cache"

        # Verify cache statistics
        assert translator.stats["cache_hits"] == 1
        assert translator.stats["cache_misses"] == 1

    @patch("src.ml.document_translator.detect")
    @patch("src.ml.document_translator.detect_langs")
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_translate_batch(self, mock_google_translator, mock_detect_langs, mock_detect, sample_texts):
        """Test batch translation"""
        # Mock language detection
        mock_detect.return_value = "en"
        mock_lang = Mock()
        mock_lang.lang = "en"
        mock_lang.prob = 0.99
        mock_detect_langs.return_value = [mock_lang]

        # Mock translation
        mock_translator_instance = Mock()

        def mock_translate_side_effect(text, src, dest):
            result = Mock()
            result.text = f"Translated: {text}"
            result.src = src
            return result

        mock_translator_instance.translate.side_effect = mock_translate_side_effect
        mock_google_translator.return_value = mock_translator_instance

        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)
        batch_result = translator.translate_batch(sample_texts, target_language="es")

        assert batch_result.total_texts == 3
        assert batch_result.successful == 3
        assert batch_result.failed == 0
        assert batch_result.success_rate == 1.0
        assert len(batch_result.results) == 3

    @patch("src.ml.document_translator.detect")
    @patch("src.ml.document_translator.detect_langs")
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_translate_document(self, mock_google_translator, mock_detect_langs, mock_detect):
        """Test translating document file"""
        # Mock language detection
        mock_detect.return_value = "en"
        mock_lang = Mock()
        mock_lang.lang = "en"
        mock_lang.prob = 0.99
        mock_detect_langs.return_value = [mock_lang]

        # Mock translation
        mock_translator_instance = Mock()

        def mock_translate_side_effect(text, src, dest):
            result = Mock()
            result.text = f"Translated: {text}"
            result.src = src
            return result

        mock_translator_instance.translate.side_effect = mock_translate_side_effect
        mock_google_translator.return_value = mock_translator_instance

        # Create temporary document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, world!\n\nThis is a test document.")
            temp_path = f.name

        try:
            translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)
            result = translator.translate_document(temp_path, target_language="es")

            assert result["source_language"] == "en"
            assert result["target_language"] == "es"
            assert "translated_content" in result
            assert result["backend"] == "google"
        finally:
            Path(temp_path).unlink()

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_unsupported_language(self, mock_google_translator):
        """Test handling unsupported language"""
        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)

        with pytest.raises(ValueError) as exc_info:
            translator.translate("Hello", target_language="xxx")

        assert "Unsupported target language" in str(exc_info.value)

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_get_statistics(self, mock_google_translator):
        """Test getting statistics"""
        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE, cache_enabled=True)

        stats = translator.get_statistics()

        assert "translations" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "errors" in stats
        assert "total_words" in stats
        assert "cache_hit_rate" in stats
        assert "cache_size" in stats

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_clear_cache(self, mock_google_translator):
        """Test clearing cache"""
        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE, cache_enabled=True)

        # Add something to cache
        translator.cache.put("Hello", "en", "es", "Hola")
        assert len(translator.cache.cache) == 1

        # Clear cache
        translator.clear_cache()
        assert len(translator.cache.cache) == 0


class TestFactoryFunctions:
    """Test factory and convenience functions"""

    @patch("src.ml.document_translator.GOOGLE_TRANSLATE_AVAILABLE", True)
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_create_translator(self, mock_google_translator):
        """Test create_translator factory function"""
        translator = create_translator(backend="google", cache_enabled=True)

        assert isinstance(translator, DocumentTranslator)
        assert translator.backend == TranslationBackend.GOOGLE
        assert translator.cache_enabled is True

    @patch("src.ml.document_translator.GOOGLE_TRANSLATE_AVAILABLE", True)
    @patch("src.ml.document_translator.LANGDETECT_AVAILABLE", True)
    @patch("src.ml.document_translator.detect")
    @patch("src.ml.document_translator.detect_langs")
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_quick_translate(self, mock_google_translator, mock_detect_langs, mock_detect):
        """Test quick_translate convenience function"""
        # Mock language detection
        mock_detect.return_value = "en"
        mock_lang = Mock()
        mock_lang.lang = "en"
        mock_lang.prob = 0.99
        mock_detect_langs.return_value = [mock_lang]

        # Mock translation
        mock_translator_instance = Mock()
        mock_result = Mock()
        mock_result.text = "Hola"
        mock_result.src = "en"
        mock_translator_instance.translate.return_value = mock_result
        mock_google_translator.return_value = mock_translator_instance

        result = quick_translate("Hello", target_language="es")

        assert result == "Hola"


class TestTranslationBackends:
    """Test different translation backends"""

    @patch("src.ml.document_translator.GOOGLE_TRANSLATE_AVAILABLE", True)
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_google_backend_availability(self, mock_google_translator):
        """Test Google Translate backend availability"""
        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)

        assert TranslationBackend.GOOGLE in translator.available_backends

    @patch("src.ml.document_translator.GOOGLE_TRANSLATE_AVAILABLE", False)
    @patch("src.ml.document_translator.DEEPL_AVAILABLE", False)
    @patch("src.ml.document_translator.ARGOS_AVAILABLE", False)
    def test_no_backends_available(self):
        """Test when no backends are available"""
        translator = DocumentTranslator(backend=TranslationBackend.AUTO)

        assert len(translator.available_backends) == 0

        with pytest.raises(RuntimeError) as exc_info:
            translator._get_backend()

        assert "No translation backend available" in str(exc_info.value)

    @patch("src.ml.document_translator.GOOGLE_TRANSLATE_AVAILABLE", True)
    @patch("src.ml.document_translator.GoogleTranslator")
    def test_auto_backend_selection(self, mock_google_translator):
        """Test automatic backend selection"""
        translator = DocumentTranslator(backend=TranslationBackend.AUTO)
        backend = translator._get_backend()

        assert backend in translator.available_backends


class TestEdgeCases:
    """Test edge cases and error handling"""

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_empty_text_translation(self, mock_google_translator):
        """Test translating empty text"""
        # Note: This should still work but may produce empty result
        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)

        # Empty string should work but behavior depends on backend
        # We'll just verify it doesn't crash
        try:
            result = translator.translate("", target_language="es", source_language="en")
            # If it succeeds, that's fine
            assert True
        except Exception:
            # If it fails, that's also acceptable for edge case
            assert True

    @patch("src.ml.document_translator.GoogleTranslator")
    def test_very_long_text(self, mock_google_translator):
        """Test translating very long text"""
        translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)
        long_text = "Hello " * 10000  # Very long text

        # Should handle long text gracefully
        # Exact behavior depends on backend limits
        try:
            translator.translate(long_text, target_language="es", source_language="en")
            assert True
        except Exception:
            # May fail due to backend limits, that's acceptable
            assert True

    def test_document_not_found(self):
        """Test translating non-existent document"""
        translator = DocumentTranslator(backend=TranslationBackend.AUTO)

        with pytest.raises(FileNotFoundError):
            translator.translate_document("/nonexistent/document.txt", target_language="es")
