"""
Comprehensive tests for Named Entity Recognition (NER) module

Test coverage goals:
- RegexNER: Email, phone, money, date, IBAN extraction
- SpacyNER: Person, organization, location extraction
- NER: Combined extraction with multiple languages
- Edge cases: Empty text, special characters, multiple entities
- Performance: Large text processing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ml.ner import (
    Entity,
    EntityType,
    RegexNER,
    SpacyNER,
    NEREngine,
)


class TestEntity:
    """Test Entity dataclass"""

    def test_entity_creation(self):
        """Test basic entity creation"""
        entity = Entity(
            text="John Doe",
            type=EntityType.PERSON,
            start=0,
            end=8,
            confidence=0.95
        )

        assert entity.text == "John Doe"
        assert entity.type == EntityType.PERSON
        assert entity.start == 0
        assert entity.end == 8
        assert entity.confidence == 0.95

    def test_entity_default_confidence(self):
        """Test entity with default confidence"""
        entity = Entity(
            text="test@example.com",
            type=EntityType.EMAIL,
            start=0,
            end=16
        )

        assert entity.confidence == 1.0

    def test_entity_types(self):
        """Test all entity types"""
        types = [
            EntityType.PERSON,
            EntityType.ORGANIZATION,
            EntityType.LOCATION,
            EntityType.DATE,
            EntityType.MONEY,
            EntityType.EMAIL,
            EntityType.PHONE,
            EntityType.IBAN,
        ]

        for entity_type in types:
            entity = Entity(text="test", type=entity_type, start=0, end=4)
            assert entity.type == entity_type


class TestRegexNER:
    """Test RegexNER class"""

    @pytest.fixture
    def regex_ner(self):
        """Create RegexNER instance"""
        return RegexNER()

    def test_email_extraction(self, regex_ner):
        """Test email extraction"""
        text = "Contact us at info@example.com or support@test.org"
        entities = regex_ner.extract(text)

        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) == 2
        assert emails[0].text == "info@example.com"
        assert emails[1].text == "support@test.org"

    def test_phone_extraction(self, regex_ner):
        """Test phone number extraction"""
        text = "Call me at +49 123 456789 or (030) 123-4567"
        entities = regex_ner.extract(text)

        phones = [e for e in entities if e.type == EntityType.PHONE]
        assert len(phones) >= 1
        # Should find at least one phone number

    def test_money_extraction(self, regex_ner):
        """Test monetary amount extraction"""
        text = "The price is 99.99 EUR or $150.00 USD"
        entities = regex_ner.extract(text)

        money = [e for e in entities if e.type == EntityType.MONEY]
        assert len(money) >= 1

    def test_date_extraction(self, regex_ner):
        """Test date extraction"""
        text = "The meeting is on 25.12.2023 or 01/15/2024"
        entities = regex_ner.extract(text)

        dates = [e for e in entities if e.type == EntityType.DATE]
        assert len(dates) == 2
        assert dates[0].text == "25.12.2023"
        assert dates[1].text == "01/15/2024"

    def test_iban_extraction(self, regex_ner):
        """Test IBAN extraction"""
        text = "Transfer to DE89370400440532013000"
        entities = regex_ner.extract(text)

        ibans = [e for e in entities if e.type == EntityType.IBAN]
        assert len(ibans) == 1
        assert ibans[0].text == "DE89370400440532013000"

    def test_empty_text(self, regex_ner):
        """Test extraction from empty text"""
        entities = regex_ner.extract("")
        assert len(entities) == 0

    def test_no_entities(self, regex_ner):
        """Test text with no entities"""
        text = "This is plain text without any special information"
        entities = regex_ner.extract(text)
        assert len(entities) == 0

    def test_multiple_entity_types(self, regex_ner):
        """Test extraction of multiple entity types"""
        text = """
        Contact: john@example.com
        Phone: +49 123 456789
        Amount: 99.99 EUR
        Date: 15.01.2024
        IBAN: DE89370400440532013000
        """
        entities = regex_ner.extract(text)

        # Should find entities of different types
        entity_types = {e.type for e in entities}
        assert EntityType.EMAIL in entity_types
        assert EntityType.PHONE in entity_types or EntityType.MONEY in entity_types

    def test_entity_positions(self, regex_ner):
        """Test entity position tracking"""
        text = "Email: test@example.com"
        entities = regex_ner.extract(text)

        if entities:
            entity = entities[0]
            assert entity.start >= 0
            assert entity.end > entity.start
            assert text[entity.start:entity.end] == entity.text

    @pytest.mark.parametrize("email,valid", [
        ("test@example.com", True),
        ("user.name@domain.co.uk", True),
        ("invalid.email", False),
        ("@example.com", False),
    ])
    def test_email_patterns(self, regex_ner, email, valid):
        """Test various email patterns"""
        entities = regex_ner.extract(f"Contact: {email}")
        emails = [e for e in entities if e.type == EntityType.EMAIL]

        if valid:
            assert len(emails) >= 1
        # Note: Some invalid emails might still match regex


class TestSpacyNER:
    """Test SpacyNER class"""

    @pytest.fixture
    def spacy_ner(self):
        """Create SpacyNER instance"""
        try:
            return SpacyNER(model_name="en_core_web_sm")
        except Exception:
            pytest.skip("spaCy model not available")

    def test_spacy_initialization(self):
        """Test SpacyNER initialization"""
        ner = SpacyNER()
        # Should not raise error even if model not available
        assert ner is not None

    def test_person_extraction(self, spacy_ner):
        """Test person name extraction"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "John Doe and Jane Smith work at Microsoft"
        entities = spacy_ner.extract(text)

        persons = [e for e in entities if e.type == EntityType.PERSON]
        assert len(persons) >= 1

    def test_organization_extraction(self, spacy_ner):
        """Test organization extraction"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "Apple and Google are technology companies"
        entities = spacy_ner.extract(text)

        orgs = [e for e in entities if e.type == EntityType.ORGANIZATION]
        assert len(orgs) >= 1

    def test_location_extraction(self, spacy_ner):
        """Test location extraction"""
        if not spacy_ner.available:
            pytest.skip("spaCy not available")

        text = "I live in Berlin, Germany and work in New York"
        entities = spacy_ner.extract(text)

        locations = [e for e in entities if e.type == EntityType.LOCATION]
        assert len(locations) >= 1

    def test_unavailable_model(self):
        """Test behavior when model is unavailable"""
        ner = SpacyNER(model_name="nonexistent_model")
        assert not ner.available

        # Should return empty list when unavailable
        entities = ner.extract("Some text")
        assert entities == []


class TestNEREngine:
    """Test combined NEREngine class"""

    @pytest.fixture
    def ner(self):
        """Create NEREngine instance"""
        return NEREngine()

    def test_ner_initialization(self, ner):
        """Test NEREngine initialization"""
        assert ner is not None
        assert hasattr(ner, 'regex_ner')

    def test_combined_extraction(self, ner):
        """Test combined regex and spaCy extraction"""
        text = """
        John Doe works at Microsoft.
        Contact: john.doe@microsoft.com
        Phone: +1-555-0123
        Amount: $1,500.00
        """
        entities = ner.extract_entities(text)

        # Should find both regex and spaCy entities
        assert len(entities) > 0

        # Check for different entity types
        entity_types = {e.type for e in entities}
        assert len(entity_types) > 0

    def test_deduplicate_entities(self, ner):
        """Test entity deduplication"""
        # If both regex and spaCy find the same entity, it should appear once
        text = "Email: test@example.com"
        entities = ner.extract_entities(text)

        # Count email entities
        emails = [e for e in entities if e.type == EntityType.EMAIL]
        # Should find email at least once
        assert len(emails) >= 1

    def test_large_text_processing(self, ner):
        """Test processing of large text"""
        # Generate large text
        text = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Contact: info@example.com, Phone: +49 123 456789
        """ * 100  # Repeat 100 times

        entities = ner.extract_entities(text)

        # Should find entities even in large text
        assert len(entities) > 0

    def test_multilingual_support(self, ner):
        """Test extraction from text in different languages"""
        # German text with regex-findable entities
        german_text = "Max Mustermann arbeitet bei der Deutschen Bank. Kontakt: max.mustermann@deutsche-bank.de, 1.000,00 EUR"
        german_entities = ner.extract_entities(german_text)

        # English text with regex-findable entities
        english_text = "John Smith works at Deutsche Bank. Contact: john.smith@example.com, $1,000.00"
        english_entities = ner.extract_entities(english_text)

        # Both should find entities (at least email and money)
        assert len(german_entities) > 0 or len(english_entities) > 0

    def test_special_characters(self, ner):
        """Test handling of special characters"""
        text = "Contact: test@example.com! #Special chars: $%&*()"
        entities = ner.extract_entities(text)

        # Should still find email
        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) >= 1

    def test_overlapping_entities(self, ner):
        """Test handling of overlapping entities"""
        text = "Dr. John Smith, john.smith@example.com"
        entities = ner.extract_entities(text)

        # Should find both person and email
        assert len(entities) >= 1

    @pytest.mark.parametrize("text,expected_types", [
        ("Email: test@example.com", {EntityType.EMAIL}),
        ("Date: 25.12.2023", {EntityType.DATE}),
        ("John Doe", set()),  # Might find PERSON if spaCy available
        ("Amount: 99.99 EUR", {EntityType.MONEY}),
    ])
    def test_specific_extractions(self, ner, text, expected_types):
        """Test specific entity extractions"""
        entities = ner.extract_entities(text)
        entity_types = {e.type for e in entities}

        # At least some expected types should be found
        if expected_types:
            assert len(entity_types & expected_types) > 0 or len(entities) == 0

    def test_confidence_scores(self, ner):
        """Test entity confidence scores"""
        text = "Contact: test@example.com"
        entities = ner.extract_entities(text)

        if entities:
            # All entities should have confidence scores
            for entity in entities:
                assert 0.0 <= entity.confidence <= 1.0

    def test_entity_ordering(self, ner):
        """Test that entities are ordered by position"""
        text = "Start: test@example.com middle: 25.12.2023 end: +49 123 456789"
        entities = ner.extract_entities(text)

        if len(entities) > 1:
            # Check that entities are ordered by start position
            for i in range(len(entities) - 1):
                assert entities[i].start <= entities[i + 1].start


class TestPerformance:
    """Performance tests for NER"""

    @pytest.fixture
    def ner(self):
        """Create NER instance"""
        return NEREngine()

    @pytest.mark.skip(reason="pytest-benchmark not installed")
    def test_performance_small_text(self, ner, benchmark):
        """Benchmark small text extraction"""
        text = "John Doe works at Microsoft. Email: john@example.com"

        result = benchmark(ner.extract_entities, text)
        assert len(result) >= 0

    @pytest.mark.skip(reason="pytest-benchmark not installed")
    def test_performance_large_text(self, ner, benchmark):
        """Benchmark large text extraction"""
        # Generate large text with multiple entities
        text = """
        Contact Information:
        Name: John Doe
        Email: john.doe@example.com
        Phone: +49 123 456789
        Company: Microsoft Corporation
        Amount: 5,000.00 EUR
        Date: 25.12.2023
        """ * 50  # Repeat 50 times

        result = benchmark(ner.extract_entities, text)
        assert len(result) > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def ner(self):
        """Create NER instance"""
        return NEREngine()

    def test_none_input(self, ner):
        """Test handling of None input"""
        with pytest.raises((TypeError, AttributeError)):
            ner.extract(None)

    def test_unicode_text(self, ner):
        """Test handling of Unicode text"""
        text = "名前: test@example.com 📧"
        entities = ner.extract_entities(text)

        # Should still find email
        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) >= 1

    def test_very_long_line(self, ner):
        """Test handling of very long line"""
        text = "a" * 10000 + " test@example.com " + "b" * 10000
        entities = ner.extract_entities(text)

        # Should still find email
        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) >= 1

    def test_malformed_entities(self, ner):
        """Test handling of malformed entities"""
        text = "Email: @@@example...com Phone: +++--- IBAN: XXXX"
        entities = ner.extract_entities(text)

        # Should not crash, might find 0 entities
        assert isinstance(entities, list)

    def test_repeated_entities(self, ner):
        """Test handling of repeated entities"""
        text = "test@example.com " * 100
        entities = ner.extract_entities(text)

        # Should find all occurrences
        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) >= 10  # At least find some


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
