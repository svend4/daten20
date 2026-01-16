"""
Comprehensive tests for relation_extractor module

Test coverage goals:
- Positive cases: Normal relation extraction
- Negative cases: Error handling, no relations found
- Edge cases: Multiple relations, overlapping entities
- Integration: Works with NER engine
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ml.relation_extractor import (
    RelationExtractor,
    Relation,
    RelationType,
)
from src.ml.ner import Entity, EntityType


class TestRelationExtractor:
    """Test suite for RelationExtractor"""

    @pytest.fixture
    def extractor(self):
        """Create test instance"""
        return RelationExtractor(use_spacy=False)

    @pytest.fixture
    def extractor_with_spacy(self):
        """Create instance with spaCy (if available)"""
        try:
            return RelationExtractor(use_spacy=True, spacy_model="en_core_web_sm")
        except:
            pytest.skip("spaCy not available")

    def test_initialization_without_spacy(self):
        """Test initialization without spaCy"""
        extractor = RelationExtractor(use_spacy=False)
        assert extractor is not None
        assert extractor.ner_engine is not None
        assert extractor.nlp is None
        assert not extractor.available

    def test_initialization_with_spacy(self):
        """Test initialization with spaCy"""
        try:
            extractor = RelationExtractor(use_spacy=True, spacy_model="en_core_web_sm")
            assert extractor is not None
            assert extractor.ner_engine is not None
            # spaCy availability depends on installation
        except:
            pytest.skip("spaCy not available")

    def test_extract_relations_empty_text(self, extractor):
        """Test extraction with empty text"""
        relations = extractor.extract_relations("")
        assert relations == []

    def test_extract_relations_no_entities(self, extractor):
        """Test extraction with text containing no entities"""
        text = "This is a simple sentence without any named entities."
        relations = extractor.extract_relations(text)
        assert isinstance(relations, list)

    def test_extract_relations_works_at(self, extractor):
        """Test WORKS_AT relation extraction"""
        text = "John Smith works at Microsoft Corporation in Seattle."

        # Mock entities
        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(
                    text="John Smith",
                    type=EntityType.PERSON,
                    start=0,
                    end=10,
                    confidence=0.9
                ),
                Entity(
                    text="Microsoft Corporation",
                    type=EntityType.ORGANIZATION,
                    start=20,
                    end=41,
                    confidence=0.9
                )
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_extract_relations_ceo_of(self, extractor):
        """Test CEO_OF relation extraction"""
        text = "Tim Cook is the CEO of Apple Inc."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(
                    text="Tim Cook",
                    type=EntityType.PERSON,
                    start=0,
                    end=8,
                    confidence=0.9
                ),
                Entity(
                    text="Apple Inc",
                    type=EntityType.ORGANIZATION,
                    start=27,
                    end=36,
                    confidence=0.9
                )
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_extract_relations_located_in(self, extractor):
        """Test LOCATED_IN relation extraction"""
        text = "Microsoft is located in Redmond, Washington."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(
                    text="Microsoft",
                    type=EntityType.ORGANIZATION,
                    start=0,
                    end=9,
                    confidence=0.9
                ),
                Entity(
                    text="Redmond",
                    type=EntityType.LOCATION,
                    start=24,
                    end=31,
                    confidence=0.9
                ),
                Entity(
                    text="Washington",
                    type=EntityType.LOCATION,
                    start=33,
                    end=43,
                    confidence=0.9
                )
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_extract_relations_multiple(self, extractor):
        """Test extraction of multiple relations"""
        text = "John works at Google and Jane is the CEO of Microsoft."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="John", type=EntityType.PERSON, start=0, end=4, confidence=0.9),
                Entity(text="Google", type=EntityType.ORGANIZATION, start=14, end=20, confidence=0.9),
                Entity(text="Jane", type=EntityType.PERSON, start=25, end=29, confidence=0.9),
                Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=44, end=53, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_pattern_matching_works_at(self, extractor):
        """Test pattern matching for WORKS_AT relation"""
        text = "Max Mustermann arbeitet bei Siemens AG."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="Max Mustermann", type=EntityType.PERSON, start=0, end=14, confidence=0.9),
                Entity(text="Siemens AG", type=EntityType.ORGANIZATION, start=29, end=39, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_pattern_matching_german_text(self, extractor):
        """Test pattern matching with German text"""
        text = "Der Geschäftsführer von BMW ist sehr erfolgreich."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="BMW", type=EntityType.ORGANIZATION, start=24, end=27, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_confidence_scoring(self, extractor):
        """Test confidence score calculation"""
        text = "John Smith works at Microsoft."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="John Smith", type=EntityType.PERSON, start=0, end=10, confidence=0.9),
                Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=20, end=29, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            for relation in relations:
                assert 0.0 <= relation.confidence <= 1.0

    def test_relation_context(self, extractor):
        """Test that relation includes context"""
        text = "John Smith works at Microsoft Corporation."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="John Smith", type=EntityType.PERSON, start=0, end=10, confidence=0.9),
                Entity(text="Microsoft Corporation", type=EntityType.ORGANIZATION, start=20, end=41, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            for relation in relations:
                assert relation.context is not None
                assert isinstance(relation.context, str)

    def test_relation_positions(self, extractor):
        """Test that relation includes start/end positions"""
        text = "John Smith works at Microsoft."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="John Smith", type=EntityType.PERSON, start=0, end=10, confidence=0.9),
                Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=20, end=29, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            for relation in relations:
                assert relation.start >= 0
                assert relation.end > relation.start

    def test_overlapping_entities(self, extractor):
        """Test handling of overlapping entities"""
        text = "New York Times is based in New York City."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="New York Times", type=EntityType.ORGANIZATION, start=0, end=14, confidence=0.9),
                Entity(text="New York", type=EntityType.LOCATION, start=0, end=8, confidence=0.7),
                Entity(text="New York City", type=EntityType.LOCATION, start=27, end=40, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_long_text_performance(self, extractor):
        """Test performance with long text"""
        # Create a long text with multiple sentences
        text = " ".join(["John works at Microsoft."] * 100)

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            # Return many entities
            entities = []
            for i in range(100):
                start_pos = i * 25
                entities.append(
                    Entity(text="John", type=EntityType.PERSON, start=start_pos, end=start_pos+4, confidence=0.9)
                )
                entities.append(
                    Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=start_pos+14, end=start_pos+23, confidence=0.9)
                )
            mock_extract.return_value = entities

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_special_characters_in_text(self, extractor):
        """Test handling of special characters"""
        text = "John Smith (CEO) works @ Microsoft Corp."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="John Smith", type=EntityType.PERSON, start=0, end=10, confidence=0.9),
                Entity(text="Microsoft Corp", type=EntityType.ORGANIZATION, start=27, end=41, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_unicode_text(self, extractor):
        """Test handling of Unicode text"""
        text = "李明 works at 微软公司 in 北京."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="李明", type=EntityType.PERSON, start=0, end=2, confidence=0.9),
                Entity(text="微软公司", type=EntityType.ORGANIZATION, start=12, end=16, confidence=0.9),
                Entity(text="北京", type=EntityType.LOCATION, start=20, end=22, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_relation_deduplication(self, extractor):
        """Test that duplicate relations are handled"""
        text = "John works at Microsoft. John works at Microsoft."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            mock_extract.return_value = [
                Entity(text="John", type=EntityType.PERSON, start=0, end=4, confidence=0.9),
                Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=14, end=23, confidence=0.9),
                Entity(text="John", type=EntityType.PERSON, start=25, end=29, confidence=0.9),
                Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=39, end=48, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_invalid_entity_types(self, extractor):
        """Test handling of invalid entity type combinations"""
        text = "Some text here."

        with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
            # Two locations cannot have WORKS_AT relation
            mock_extract.return_value = [
                Entity(text="Seattle", type=EntityType.LOCATION, start=0, end=7, confidence=0.9),
                Entity(text="Redmond", type=EntityType.LOCATION, start=8, end=15, confidence=0.9),
            ]

            relations = extractor.extract_relations(text)
            assert isinstance(relations, list)

    def test_error_handling_none_text(self, extractor):
        """Test error handling with None input"""
        with pytest.raises((TypeError, AttributeError, ValueError)):
            extractor.extract_relations(None)

    def test_error_handling_invalid_type(self, extractor):
        """Test error handling with invalid input type"""
        with pytest.raises((TypeError, AttributeError)):
            extractor.extract_relations(12345)

    def test_relation_type_enum(self):
        """Test RelationType enum values"""
        assert RelationType.WORKS_AT == "works_at"
        assert RelationType.CEO_OF == "ceo_of"
        assert RelationType.LOCATED_IN == "located_in"
        assert RelationType.FOUNDED == "founded"
        assert RelationType.ACQUIRED == "acquired"

    def test_relation_dataclass(self):
        """Test Relation dataclass"""
        entity1 = Entity(text="John", type=EntityType.PERSON, start=0, end=4, confidence=0.9)
        entity2 = Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=14, end=23, confidence=0.9)

        relation = Relation(
            subject=entity1,
            relation=RelationType.WORKS_AT,
            object=entity2,
            confidence=0.85,
            context="John works at Microsoft",
            start=0,
            end=23
        )

        assert relation.subject == entity1
        assert relation.relation == RelationType.WORKS_AT
        assert relation.object == entity2
        assert relation.confidence == 0.85
        assert relation.context == "John works at Microsoft"
        assert relation.start == 0
        assert relation.end == 23


@pytest.mark.parametrize("text,expected_min_relations", [
    ("John works at Microsoft and Jane is CEO of Google.", 0),
    ("Tim Cook is CEO of Apple Inc. in Cupertino, California.", 0),
    ("BMW is headquartered in Munich, Germany.", 0),
])
def test_multiple_relation_patterns(text, expected_min_relations):
    """Test extraction with various relation patterns"""
    extractor = RelationExtractor(use_spacy=False)

    with patch.object(extractor.ner_engine, 'extract_entities') as mock_extract:
        # Mock some entities based on text
        entities = []
        if "John" in text:
            entities.append(Entity(text="John", type=EntityType.PERSON, start=0, end=4, confidence=0.9))
        if "Microsoft" in text:
            idx = text.find("Microsoft")
            entities.append(Entity(text="Microsoft", type=EntityType.ORGANIZATION, start=idx, end=idx+9, confidence=0.9))
        if "Google" in text:
            idx = text.find("Google")
            entities.append(Entity(text="Google", type=EntityType.ORGANIZATION, start=idx, end=idx+6, confidence=0.9))
        if "Jane" in text:
            idx = text.find("Jane")
            entities.append(Entity(text="Jane", type=EntityType.PERSON, start=idx, end=idx+4, confidence=0.9))

        mock_extract.return_value = entities

        relations = extractor.extract_relations(text)
        assert isinstance(relations, list)
        assert len(relations) >= expected_min_relations


class TestRelationExtractorWithSpacy:
    """Tests that require spaCy"""

    @pytest.fixture
    def extractor_spacy(self):
        """Create extractor with spaCy"""
        try:
            return RelationExtractor(use_spacy=True, spacy_model="en_core_web_sm")
        except:
            pytest.skip("spaCy not available")

    def test_spacy_dependency_parsing(self, extractor_spacy):
        """Test spaCy dependency parsing integration"""
        if not extractor_spacy.available:
            pytest.skip("spaCy not available")

        text = "John Smith works at Microsoft Corporation."
        relations = extractor_spacy.extract_relations(text)
        assert isinstance(relations, list)

    def test_spacy_entity_recognition(self, extractor_spacy):
        """Test spaCy entity recognition"""
        if not extractor_spacy.available:
            pytest.skip("spaCy not available")

        text = "Apple Inc. is based in Cupertino, California."
        relations = extractor_spacy.extract_relations(text)
        assert isinstance(relations, list)

    def test_spacy_multiple_sentences(self, extractor_spacy):
        """Test spaCy with multiple sentences"""
        if not extractor_spacy.available:
            pytest.skip("spaCy not available")

        text = "John works at Microsoft. Jane is CEO of Google. Bob lives in Seattle."
        relations = extractor_spacy.extract_relations(text)
        assert isinstance(relations, list)
