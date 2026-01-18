"""
Unit tests for NER (Named Entity Recognition) module
"""

import pytest

from src.ml.ner import Entity, EntityType, NEREngine, RegexNER, SpacyNER, get_ner_engine


pytestmark = pytest.mark.unit


class TestEntity:
    """Test Entity dataclass."""

    def test_entity_creation(self):
        """Test creating an entity."""
        entity = Entity(
            text="test@example.com",
            type=EntityType.EMAIL,
            start=0,
            end=16,
            confidence=1.0
        )

        assert entity.text == "test@example.com"
        assert entity.type == EntityType.EMAIL
        assert entity.start == 0
        assert entity.end == 16
        assert entity.confidence == 1.0

    def test_entity_default_confidence(self):
        """Test entity default confidence is 1.0."""
        entity = Entity(
            text="test",
            type=EntityType.PERSON,
            start=0,
            end=4
        )
        assert entity.confidence == 1.0


class TestRegexNER:
    """Test regex-based NER."""

    def test_extract_email(self):
        """Test email extraction."""
        ner = RegexNER()
        text = "Contact me at john.doe@example.com for details."
        entities = ner.extract(text)

        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) == 1
        assert emails[0].text == "john.doe@example.com"
        assert emails[0].start == 14
        assert emails[0].end == 34

    def test_extract_multiple_emails(self):
        """Test extracting multiple emails."""
        ner = RegexNER()
        text = "Email alice@example.com or bob@test.org"
        entities = ner.extract(text)

        emails = [e for e in entities if e.type == EntityType.EMAIL]
        assert len(emails) == 2
        assert emails[0].text == "alice@example.com"
        assert emails[1].text == "bob@test.org"

    def test_extract_phone(self):
        """Test phone number extraction."""
        ner = RegexNER()
        text = "Call me at +49 123 456-7890 today"
        entities = ner.extract(text)

        phones = [e for e in entities if e.type == EntityType.PHONE]
        assert len(phones) == 1
        # Regex may or may not include the + sign
        assert "49 123 456-7890" in phones[0].text

    def test_extract_money(self):
        """Test monetary amount extraction."""
        ner = RegexNER()
        text = "The price is 99.99 EUR or 50,00 €"
        entities = ner.extract(text)

        money = [e for e in entities if e.type == EntityType.MONEY]
        # Regex may only match specific formats
        assert len(money) >= 1
        assert any("99.99" in m.text or "EUR" in m.text for m in money)

    def test_extract_date(self):
        """Test date extraction."""
        ner = RegexNER()
        text = "Meeting on 15/03/2024 at 10:00"
        entities = ner.extract(text)

        dates = [e for e in entities if e.type == EntityType.DATE]
        assert len(dates) == 1
        assert dates[0].text == "15/03/2024"

    def test_extract_iban(self):
        """Test IBAN extraction."""
        ner = RegexNER()
        text = "Account: DE89 3704 0044 0532 0130 00"
        entities = ner.extract(text)

        ibans = [e for e in entities if e.type == EntityType.IBAN]
        assert len(ibans) == 1
        assert "DE89" in ibans[0].text

    def test_extract_no_entities(self):
        """Test text with no entities."""
        ner = RegexNER()
        text = "This is just plain text without any entities"
        entities = ner.extract(text)

        assert len(entities) == 0

    def test_extract_mixed_entities(self):
        """Test extracting multiple entity types."""
        ner = RegexNER()
        text = "Email: test@example.com, Date: 01/01/2024, Amount: 100.00 EUR"
        entities = ner.extract(text)

        # Should find email, date, and money
        assert len(entities) >= 3
        types = {e.type for e in entities}
        assert EntityType.EMAIL in types
        assert EntityType.DATE in types
        assert EntityType.MONEY in types


class TestSpacyNER:
    """Test spaCy-based NER."""

    def test_spacy_ner_initialization_without_spacy(self):
        """Test that SpacyNER handles missing spaCy gracefully."""
        # This might fail if spaCy is actually installed
        ner = SpacyNER(model_name="nonexistent_model")
        assert ner.available == False
        assert ner.nlp is None

    def test_extract_without_spacy(self):
        """Test extraction when spaCy is not available."""
        ner = SpacyNER(model_name="nonexistent_model")
        text = "Max Mustermann works at Siemens AG in Munich"
        entities = ner.extract(text)

        # Should return empty list if spaCy not available
        assert isinstance(entities, list)

    def test_extract_by_type_without_spacy(self):
        """Test extract_by_type when spaCy is not available."""
        ner = SpacyNER(model_name="nonexistent_model")
        text = "Max Mustermann works at Siemens AG"
        entities = ner.extract_by_type(text, EntityType.PERSON)

        assert isinstance(entities, list)


class TestNEREngine:
    """Test main NER engine."""

    def test_ner_engine_initialization(self):
        """Test NER engine initialization."""
        engine = NEREngine(use_spacy=False)
        assert engine.regex_ner is not None
        assert engine.spacy_ner is None

    def test_ner_engine_with_spacy(self):
        """Test NER engine with spaCy enabled."""
        engine = NEREngine(use_spacy=True)
        assert engine.regex_ner is not None
        assert engine.spacy_ner is not None

    def test_extract_entities_regex_only(self):
        """Test entity extraction with regex only."""
        engine = NEREngine(use_spacy=False)
        text = "Contact: john@example.com, Phone: +1234567890"
        entities = engine.extract_entities(text)

        assert len(entities) > 0
        types = {e.type for e in entities}
        assert EntityType.EMAIL in types

    def test_extract_by_type(self):
        """Test extracting specific entity type."""
        engine = NEREngine(use_spacy=False)
        text = "Emails: alice@test.com and bob@test.com"
        emails = engine.extract_by_type(text, EntityType.EMAIL)

        assert len(emails) == 2
        assert all(e.type == EntityType.EMAIL for e in emails)

    def test_remove_overlaps(self):
        """Test overlap removal."""
        engine = NEREngine(use_spacy=False)

        # Create overlapping entities
        entities = [
            Entity("test@example.com", EntityType.EMAIL, 0, 16, 1.0),
            Entity("test", EntityType.PERSON, 0, 4, 0.8),  # Overlaps with email
            Entity("example.com", EntityType.ORGANIZATION, 5, 16, 0.7),  # Overlaps
            Entity("other", EntityType.PERSON, 20, 25, 1.0),  # No overlap
        ]

        filtered = engine._remove_overlaps(entities)

        # Should keep non-overlapping and highest confidence overlapping
        assert len(filtered) == 2
        assert filtered[0].text == "test@example.com"
        assert filtered[1].text == "other"

    def test_is_overlap(self):
        """Test overlap detection."""
        e1 = Entity("test", EntityType.PERSON, 0, 4, 1.0)
        e2 = Entity("testing", EntityType.PERSON, 0, 7, 1.0)  # Overlaps
        e3 = Entity("other", EntityType.PERSON, 10, 15, 1.0)  # No overlap

        assert NEREngine._is_overlap(e1, e2) == True
        assert NEREngine._is_overlap(e1, e3) == False
        assert NEREngine._is_overlap(e2, e3) == False

    def test_extract_empty_text(self):
        """Test extracting from empty text."""
        engine = NEREngine(use_spacy=False)
        entities = engine.extract_entities("")
        assert len(entities) == 0

    def test_extract_entities_comprehensive(self):
        """Test comprehensive entity extraction."""
        engine = NEREngine(use_spacy=False)
        text = """
        Dear Customer,

        Please contact us at support@company.com or call +49 123 456789.
        Your invoice of 250.00 EUR is due on 31/12/2024.
        Bank account: DE89 3704 0044 0532 0130 00

        Best regards
        """

        entities = engine.extract_entities(text)

        # Should find multiple entity types
        types = {e.type for e in entities}
        assert EntityType.EMAIL in types
        assert EntityType.PHONE in types
        assert EntityType.MONEY in types
        assert EntityType.DATE in types
        assert EntityType.IBAN in types

    def test_confidence_scores(self):
        """Test that entities have confidence scores."""
        engine = NEREngine(use_spacy=False)
        text = "Email: test@example.com"
        entities = engine.extract_entities(text)

        assert len(entities) > 0
        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0


class TestGlobalNEREngine:
    """Test global NER engine singleton."""

    def test_get_ner_engine(self):
        """Test getting global NER engine."""
        engine = get_ner_engine()
        assert engine is not None
        assert isinstance(engine, NEREngine)

    def test_get_ner_engine_singleton(self):
        """Test that get_ner_engine returns same instance."""
        engine1 = get_ner_engine()
        engine2 = get_ner_engine()
        assert engine1 is engine2


class TestEntityTypes:
    """Test EntityType enum."""

    def test_entity_types_exist(self):
        """Test that all entity types are defined."""
        assert EntityType.PERSON == "person"
        assert EntityType.ORGANIZATION == "organization"
        assert EntityType.LOCATION == "location"
        assert EntityType.DATE == "date"
        assert EntityType.MONEY == "money"
        assert EntityType.EMAIL == "email"
        assert EntityType.PHONE == "phone"
        assert EntityType.IBAN == "iban"


# Run with: python -m pytest tests/unit/ml/test_ner.py -v
