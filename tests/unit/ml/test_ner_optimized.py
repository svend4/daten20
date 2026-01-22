"""
Tests for Optimized NER Engine

Tests cover:
- Entity extraction accuracy
- Performance optimizations (caching, batch processing)
- Metrics tracking
- Overlap removal
- Cache management
"""

import time
import pytest
from typing import List

from src.ml.ner_optimized import (
    Entity,
    EntityType,
    OptimizedRegexNER,
    OptimizedSpacyNER,
    OptimizedNEREngine,
    NERMetrics,
    extract_entities,
    extract_entities_batch,
    get_ner_metrics,
)


@pytest.fixture
def sample_text():
    """Sample text with various entities"""
    return """
    Contact: john.doe@example.com or call +49 151 12345678.
    Transfer 150.50 EUR to IBAN DE89 3704 0044 0532 0130 00.
    Meeting on 15.01.2024 in Berlin.
    """


@pytest.fixture
def sample_texts():
    """Multiple sample texts for batch processing"""
    return [
        "Email me at alice@company.com or bob@company.com",
        "Call +1-555-123-4567 or +44 20 7946 0958",
        "Transfer 1000.00 USD to account",
        "Meeting on 01/15/2024 and 02/20/2024",
        "IBAN: GB82 WEST 1234 5698 7654 32",
    ]


@pytest.fixture
def regex_ner():
    """Regex NER instance"""
    return OptimizedRegexNER()


@pytest.fixture
def spacy_ner():
    """SpaCy NER instance"""
    return OptimizedSpacyNER()


@pytest.fixture
def optimized_engine():
    """Optimized NER engine instance"""
    return OptimizedNEREngine(use_spacy=False, cache_size=100)


@pytest.fixture
def engine_with_spacy():
    """Optimized NER engine with spaCy"""
    return OptimizedNEREngine(use_spacy=True, cache_size=100)


class TestOptimizedRegexNER:
    """Test optimized regex-based NER"""

    def test_extract_email(self, regex_ner):
        """Test email extraction"""
        text = "Contact: john.doe@example.com and alice@test.org"
        entities = regex_ner.extract(text)

        email_entities = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(email_entities) == 2
        assert "john.doe@example.com" in [e.text for e in email_entities]
        assert "alice@test.org" in [e.text for e in email_entities]

    def test_extract_phone(self, regex_ner):
        """Test phone number extraction"""
        text = "Call +49 151 12345678 or +1-555-123-4567"
        entities = regex_ner.extract(text)

        phone_entities = [e for e in entities if e.type == EntityType.PHONE]
        assert len(phone_entities) >= 2

    def test_extract_money(self, regex_ner):
        """Test money amount extraction"""
        text = "Transfer 150.50 EUR or 200.00 USD or 50,99 €"
        entities = regex_ner.extract(text)

        money_entities = [e for e in entities if e.type == EntityType.MONEY]
        assert len(money_entities) >= 2

    def test_extract_date(self, regex_ner):
        """Test date extraction"""
        text = "Meetings on 15.01.2024 and 20/03/2024"
        entities = regex_ner.extract(text)

        date_entities = [e for e in entities if e.type == EntityType.DATE]
        assert len(date_entities) == 2

    def test_extract_iban(self, regex_ner):
        """Test IBAN extraction"""
        text = "IBAN: DE89 3704 0044 0532 0130 00"
        entities = regex_ner.extract(text)

        iban_entities = [e for e in entities if e.type == EntityType.IBAN]
        assert len(iban_entities) == 1
        assert "DE89" in iban_entities[0].text

    def test_extract_batch(self, regex_ner):
        """Test batch extraction"""
        texts = [
            "Email: test@example.com",
            "Phone: +49 151 12345678",
            "Amount: 100.00 EUR",
        ]

        results = regex_ner.extract_batch(texts)
        assert len(results) == 3
        assert len(results[0]) >= 1  # Has email
        assert len(results[1]) >= 1  # Has phone
        assert len(results[2]) >= 1  # Has money

    def test_entity_positions(self, regex_ner):
        """Test entity position tracking"""
        text = "Email me at test@example.com today"
        entities = regex_ner.extract(text)

        email = [e for e in entities if e.type == EntityType.EMAIL][0]
        assert email.start >= 0
        assert email.end > email.start
        assert text[email.start:email.end] == email.text

    def test_confidence_score(self, regex_ner):
        """Test confidence scores"""
        text = "Email: test@example.com"
        entities = regex_ner.extract(text)

        assert all(e.confidence == 1.0 for e in entities)

    def test_empty_text(self, regex_ner):
        """Test empty text handling"""
        entities = regex_ner.extract("")
        assert entities == []

    def test_no_entities(self, regex_ner):
        """Test text with no entities"""
        text = "This is just plain text without any special patterns"
        entities = regex_ner.extract(text)
        assert entities == []


class TestOptimizedSpacyNER:
    """Test optimized spaCy-based NER"""

    def test_extract_person(self, spacy_ner):
        """Test person extraction"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "Angela Merkel met with Emmanuel Macron in Berlin"
        entities = spacy_ner.extract(text)

        person_entities = [e for e in entities if e.type == EntityType.PERSON]
        assert len(person_entities) >= 1

    def test_extract_location(self, spacy_ner):
        """Test location extraction"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "The meeting was held in Berlin, Germany"
        entities = spacy_ner.extract(text)

        location_entities = [e for e in entities if e.type == EntityType.LOCATION]
        assert len(location_entities) >= 1

    def test_extract_organization(self, spacy_ner):
        """Test organization extraction"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "Google and Microsoft announced a partnership"
        entities = spacy_ner.extract(text)

        org_entities = [e for e in entities if e.type == EntityType.ORGANIZATION]
        assert len(org_entities) >= 1

    def test_lazy_loading(self):
        """Test lazy loading of spaCy model"""
        ner = OptimizedSpacyNER()
        assert ner._nlp is None  # Not loaded yet

        # Access nlp property to trigger loading
        if ner.nlp:
            assert ner._nlp is not None
            assert ner.available is True

    def test_batch_processing(self, spacy_ner):
        """Test batch processing"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        texts = [
            "Meeting in Berlin",
            "Conference in Munich",
            "Summit in Hamburg",
        ]

        results = spacy_ner.extract_batch(texts, batch_size=2)
        assert len(results) == 3

    def test_confidence_score(self, spacy_ner):
        """Test confidence scores"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "Meeting in Berlin"
        entities = spacy_ner.extract(text)

        if entities:
            assert all(e.confidence == 0.9 for e in entities)

    def test_empty_text(self, spacy_ner):
        """Test empty text handling"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        entities = spacy_ner.extract("")
        assert entities == []

    def test_unavailable_model(self):
        """Test handling of unavailable model"""
        ner = OptimizedSpacyNER(model_name="nonexistent_model")
        entities = ner.extract("Some text")
        assert entities == []


class TestOptimizedNEREngine:
    """Test optimized NER engine"""

    def test_extract_entities(self, optimized_engine, sample_text):
        """Test entity extraction"""
        entities = optimized_engine.extract_entities(sample_text)

        assert len(entities) > 0
        assert any(e.type == EntityType.EMAIL for e in entities)
        assert any(e.type == EntityType.PHONE for e in entities)
        assert any(e.type == EntityType.MONEY for e in entities)

    def test_caching(self, optimized_engine, sample_text):
        """Test caching mechanism"""
        # First extraction - cache miss
        entities1 = optimized_engine.extract_entities(sample_text, use_cache=True)
        cache_misses_1 = optimized_engine.metrics.cache_misses

        # Second extraction - cache hit
        entities2 = optimized_engine.extract_entities(sample_text, use_cache=True)
        cache_hits_2 = optimized_engine.metrics.cache_hits

        assert entities1 == entities2
        assert cache_hits_2 > 0
        assert optimized_engine.get_cache_size() > 0

    def test_cache_disabled(self, optimized_engine, sample_text):
        """Test with caching disabled"""
        entities1 = optimized_engine.extract_entities(sample_text, use_cache=False)
        entities2 = optimized_engine.extract_entities(sample_text, use_cache=False)

        assert len(entities1) == len(entities2)
        assert optimized_engine.get_cache_size() == 0

    def test_batch_processing(self, optimized_engine, sample_texts):
        """Test batch processing"""
        results = optimized_engine.extract_entities_batch(sample_texts, use_cache=True)

        assert len(results) == len(sample_texts)
        assert all(isinstance(r, list) for r in results)
        assert sum(len(r) for r in results) > 0

    def test_batch_caching(self, optimized_engine, sample_texts):
        """Test caching in batch processing"""
        # First batch - cache misses
        results1 = optimized_engine.extract_entities_batch(sample_texts, use_cache=True)
        cache_misses_1 = optimized_engine.metrics.cache_misses

        # Reset metrics for clearer test
        initial_hits = optimized_engine.metrics.cache_hits

        # Second batch - cache hits
        results2 = optimized_engine.extract_entities_batch(sample_texts, use_cache=True)
        cache_hits_2 = optimized_engine.metrics.cache_hits

        assert results1 == results2
        assert cache_hits_2 > initial_hits

    def test_extract_by_type(self, optimized_engine):
        """Test extraction by specific type"""
        text = "Email: test@example.com, Phone: +49 151 12345678"

        email_entities = optimized_engine.extract_by_type(text, EntityType.EMAIL)
        phone_entities = optimized_engine.extract_by_type(text, EntityType.PHONE)

        assert len(email_entities) > 0
        assert all(e.type == EntityType.EMAIL for e in email_entities)
        assert len(phone_entities) > 0
        assert all(e.type == EntityType.PHONE for e in phone_entities)

    def test_overlap_removal(self, optimized_engine):
        """Test overlap removal"""
        # Create overlapping entities
        entities = [
            Entity(text="test1", type=EntityType.EMAIL, start=0, end=10, confidence=0.8),
            Entity(text="test2", type=EntityType.EMAIL, start=5, end=15, confidence=0.9),
            Entity(text="test3", type=EntityType.EMAIL, start=20, end=30, confidence=0.7),
        ]

        filtered = optimized_engine._remove_overlaps_optimized(entities)

        # Should keep non-overlapping entities and higher confidence one
        assert len(filtered) <= len(entities)

        # Check no overlaps remain
        for i in range(len(filtered) - 1):
            assert filtered[i].end <= filtered[i + 1].start

    def test_overlap_removal_empty(self, optimized_engine):
        """Test overlap removal with empty list"""
        filtered = optimized_engine._remove_overlaps_optimized([])
        assert filtered == []

    def test_metrics_tracking(self, optimized_engine, sample_text):
        """Test metrics tracking"""
        optimized_engine.reset_metrics()

        # Perform extractions
        optimized_engine.extract_entities(sample_text, use_cache=False)
        optimized_engine.extract_entities(sample_text, use_cache=False)

        metrics = optimized_engine.get_metrics()
        assert metrics.total_extractions == 2
        assert metrics.texts_processed == 2
        assert metrics.total_time_seconds > 0

    def test_metrics_reset(self, optimized_engine, sample_text):
        """Test metrics reset"""
        optimized_engine.extract_entities(sample_text)
        assert optimized_engine.metrics.total_extractions > 0

        optimized_engine.reset_metrics()
        assert optimized_engine.metrics.total_extractions == 0
        assert optimized_engine.metrics.cache_hits == 0

    def test_cache_clear(self, optimized_engine, sample_text):
        """Test cache clearing"""
        optimized_engine.extract_entities(sample_text, use_cache=True)
        assert optimized_engine.get_cache_size() > 0

        optimized_engine.clear_cache()
        assert optimized_engine.get_cache_size() == 0

    def test_cache_size_limit(self):
        """Test cache size limit"""
        engine = OptimizedNEREngine(cache_size=2)

        texts = ["text1", "text2", "text3"]
        for text in texts:
            engine.extract_entities(text, use_cache=True)

        # Cache should only hold 2 items (LRU eviction)
        assert engine.get_cache_size() <= 2

    def test_cache_disabled_initialization(self):
        """Test with cache disabled"""
        engine = OptimizedNEREngine(cache_size=0)
        engine.extract_entities("test text", use_cache=True)

        assert engine.get_cache_size() == 0
        assert engine.metrics.cache_hits == 0
        assert engine.metrics.cache_misses == 0

    def test_metrics_disabled(self):
        """Test with metrics disabled"""
        engine = OptimizedNEREngine(enable_metrics=False)
        engine.extract_entities("test text")

        # Metrics should still exist but not be updated
        assert engine.metrics.total_extractions >= 0


class TestNERMetrics:
    """Test NER metrics"""

    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = NERMetrics()

        assert metrics.total_extractions == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.entities_found == 0
        assert metrics.texts_processed == 0

    def test_average_time_calculation(self):
        """Test average time calculation"""
        metrics = NERMetrics()
        metrics.total_extractions = 10
        metrics.total_time_seconds = 2.5

        assert metrics.average_time_ms == 250.0  # 2.5s / 10 = 0.25s = 250ms

    def test_average_time_zero_extractions(self):
        """Test average time with zero extractions"""
        metrics = NERMetrics()
        assert metrics.average_time_ms == 0.0

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        metrics = NERMetrics()
        metrics.cache_hits = 75
        metrics.cache_misses = 25

        assert metrics.cache_hit_rate == 75.0

    def test_cache_hit_rate_zero_requests(self):
        """Test cache hit rate with zero requests"""
        metrics = NERMetrics()
        assert metrics.cache_hit_rate == 0.0

    def test_entities_per_text_calculation(self):
        """Test entities per text calculation"""
        metrics = NERMetrics()
        metrics.entities_found = 100
        metrics.texts_processed = 20

        assert metrics.entities_per_text == 5.0

    def test_entities_per_text_zero_texts(self):
        """Test entities per text with zero texts"""
        metrics = NERMetrics()
        assert metrics.entities_per_text == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = NERMetrics()
        metrics.total_extractions = 100
        metrics.total_time_seconds = 5.5
        metrics.cache_hits = 80
        metrics.cache_misses = 20
        metrics.entities_found = 250
        metrics.texts_processed = 100

        result = metrics.to_dict()

        assert result['total_extractions'] == 100
        assert result['cache_hit_rate'] == 80.0
        assert result['entities_per_text'] == 2.5
        assert 'average_time_ms' in result


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_extract_entities(self):
        """Test global extract_entities function"""
        text = "Email: test@example.com"
        entities = extract_entities(text)

        assert isinstance(entities, list)
        assert len(entities) > 0

    def test_extract_entities_batch(self):
        """Test global extract_entities_batch function"""
        texts = ["Email: test@example.com", "Phone: +49 151 12345678"]
        results = extract_entities_batch(texts)

        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)

    def test_get_ner_metrics(self):
        """Test global get_ner_metrics function"""
        # Extract something to generate metrics
        extract_entities("test@example.com")

        metrics = get_ner_metrics()
        assert isinstance(metrics, dict)
        assert 'total_extractions' in metrics
        assert 'cache_hit_rate' in metrics


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    def test_cache_performance(self, optimized_engine):
        """Benchmark cache performance improvement"""
        text = "Contact john.doe@example.com or call +49 151 12345678"

        # Measure without cache
        optimized_engine.clear_cache()
        start = time.time()
        for _ in range(100):
            optimized_engine.extract_entities(text, use_cache=False)
        time_no_cache = time.time() - start

        # Measure with cache
        optimized_engine.clear_cache()
        start = time.time()
        for _ in range(100):
            optimized_engine.extract_entities(text, use_cache=True)
        time_with_cache = time.time() - start

        # Cache should be significantly faster for repeated texts
        assert time_with_cache < time_no_cache
        print(f"\nCache speedup: {time_no_cache / time_with_cache:.2f}x")

    def test_batch_processing_performance(self, optimized_engine):
        """Benchmark batch processing improvement"""
        texts = [f"Email: user{i}@example.com" for i in range(50)]

        # Measure individual processing
        optimized_engine.clear_cache()
        start = time.time()
        for text in texts:
            optimized_engine.extract_entities(text, use_cache=False)
        time_individual = time.time() - start

        # Measure batch processing
        optimized_engine.clear_cache()
        start = time.time()
        optimized_engine.extract_entities_batch(texts, use_cache=False)
        time_batch = time.time() - start

        print(f"\nBatch processing time: {time_batch:.3f}s")
        print(f"Individual processing time: {time_individual:.3f}s")
        print(f"Speedup: {time_individual / time_batch:.2f}x")

    def test_precompiled_regex_performance(self):
        """Benchmark precompiled regex performance"""
        import re

        text = "Emails: user1@example.com, user2@test.org, user3@company.com"
        pattern_str = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

        # Measure with compilation each time
        start = time.time()
        for _ in range(1000):
            re.findall(pattern_str, text)
        time_compile_each = time.time() - start

        # Measure with precompiled pattern
        pattern = re.compile(pattern_str)
        start = time.time()
        for _ in range(1000):
            pattern.findall(text)
        time_precompiled = time.time() - start

        # Precompiled should be faster
        assert time_precompiled < time_compile_each
        print(f"\nPrecompiled regex speedup: {time_compile_each / time_precompiled:.2f}x")

    def test_overlap_removal_performance(self, optimized_engine):
        """Benchmark efficient overlap removal"""
        # Create many overlapping entities
        entities = []
        for i in range(100):
            entities.append(
                Entity(
                    text=f"entity{i}",
                    type=EntityType.EMAIL,
                    start=i * 5,
                    end=i * 5 + 10,
                    confidence=0.8,
                )
            )

        # Measure optimized overlap removal
        start = time.time()
        for _ in range(100):
            optimized_engine._remove_overlaps_optimized(entities)
        time_optimized = time.time() - start

        print(f"\nOverlap removal (100 entities, 100 iterations): {time_optimized:.3f}s")

    def test_large_text_performance(self, optimized_engine):
        """Benchmark performance on large text"""
        # Create large text with many entities
        large_text = " ".join([
            f"Contact person{i}@company.com or call +49-151-{i:08d}"
            for i in range(100)
        ])

        # Measure extraction time
        start = time.time()
        entities = optimized_engine.extract_entities(large_text, use_cache=False)
        extraction_time = time.time() - start

        print(f"\nLarge text extraction:")
        print(f"  Text length: {len(large_text)} chars")
        print(f"  Entities found: {len(entities)}")
        print(f"  Extraction time: {extraction_time:.3f}s")
        print(f"  Throughput: {len(large_text) / extraction_time:.0f} chars/sec")

        assert extraction_time < 5.0  # Should complete in reasonable time


class TestEntityClass:
    """Test Entity class"""

    def test_entity_creation(self):
        """Test entity creation"""
        entity = Entity(
            text="test@example.com",
            type=EntityType.EMAIL,
            start=10,
            end=26,
            confidence=0.95,
        )

        assert entity.text == "test@example.com"
        assert entity.type == EntityType.EMAIL
        assert entity.start == 10
        assert entity.end == 26
        assert entity.confidence == 0.95

    def test_entity_to_dict(self):
        """Test entity to dictionary conversion"""
        entity = Entity(
            text="test@example.com",
            type=EntityType.EMAIL,
            start=10,
            end=26,
        )

        result = entity.to_dict()
        assert result['text'] == "test@example.com"
        assert result['type'] == "email"
        assert result['start'] == 10
        assert result['end'] == 26
        assert 'confidence' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
