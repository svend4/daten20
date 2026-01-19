"""
Named Entity Recognition (NER)

Extracts entities from text:
- Person names (regex + spaCy)
- Organizations (spaCy)
- Locations (spaCy)
- Dates
- Monetary amounts
- Custom entities
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class EntityType(str, Enum):
    """Entity types"""

    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    EMAIL = "email"
    PHONE = "phone"
    IBAN = "iban"


@dataclass
class Entity:
    """Named entity"""

    text: str
    type: EntityType
    start: int
    end: int
    confidence: float = 1.0


class RegexNER:
    """Regex-based NER"""

    def __init__(self):
        self.patterns = {
            EntityType.EMAIL: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            EntityType.PHONE: r"\b\+?[\d\s\-\(\)]{10,20}\b",
            EntityType.MONEY: r"\b\d+[.,]\d{2}\s?(€|EUR|USD|\$)\b",
            EntityType.DATE: r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
            EntityType.IBAN: r"\b[A-Z]{2}\d{2}[\s]?[\d\s]{10,30}\b",
        }

    def extract(self, text: str) -> List[Entity]:
        """Extract entities"""
        entities = []

        for entity_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(Entity(text=match.group(), type=entity_type, start=match.start(), end=match.end()))

        return entities


class SpacyNER:
    """spaCy-based NER for persons, organizations, and locations"""

    def __init__(self, model_name: str = "de_core_news_sm"):
        """
        Initialize spaCy NER

        Args:
            model_name: spaCy model to use (de_core_news_sm for German, en_core_web_sm for English)
        """
        self.nlp = None
        self.model_name = model_name
        self.available = False

        try:
            import spacy

            self.nlp = spacy.load(model_name)
            self.available = True
        except (ImportError, OSError):
            # spaCy not installed or model not available
            # Will fall back to regex-based extraction
            self.available = False

        # Map spaCy entity labels to our EntityType
        self.label_mapping = {
            # German model labels
            "PER": EntityType.PERSON,
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "LOC": EntityType.LOCATION,
            "GPE": EntityType.LOCATION,  # Geopolitical entity (city, country, etc.)
            # English model labels
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "GPE": EntityType.LOCATION,
            "LOC": EntityType.LOCATION,
            "FAC": EntityType.LOCATION,  # Facility (buildings, airports, etc.)
        }

    def extract(self, text: str) -> List[Entity]:
        """Extract entities using spaCy"""
        if not self.available or self.nlp is None:
            return []

        entities = []

        try:
            # Process text with spaCy
            doc = self.nlp(text)

            # Extract named entities
            for ent in doc.ents:
                # Map spaCy label to our EntityType
                entity_type = self.label_mapping.get(ent.label_)

                if entity_type:
                    entities.append(
                        Entity(
                            text=ent.text,
                            type=entity_type,
                            start=ent.start_char,
                            end=ent.end_char,
                            confidence=0.9,  # spaCy doesn't provide confidence scores by default
                        )
                    )

        except Exception:
            # If spaCy processing fails, return empty list
            return []

        return entities

    def extract_by_type(self, text: str, entity_type: EntityType) -> List[Entity]:
        """Extract specific entity type using spaCy"""
        all_entities = self.extract(text)
        return [e for e in all_entities if e.type == entity_type]


class NEREngine:
    """Main NER engine combining regex and spaCy"""

    def __init__(self, use_spacy: bool = True, spacy_model: str = "de_core_news_sm"):
        """
        Initialize NER engine

        Args:
            use_spacy: Whether to use spaCy NER (in addition to regex)
            spacy_model: spaCy model to use (de_core_news_sm for German, en_core_web_sm for English)
        """
        self.regex_ner = RegexNER()
        self.spacy_ner = None

        if use_spacy:
            self.spacy_ner = SpacyNER(model_name=spacy_model)

    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract all entities using both regex and spaCy

        Returns entities from both methods, with spaCy results preferred for overlapping entities
        """
        entities = []

        # Get regex entities (email, phone, money, date, IBAN)
        regex_entities = self.regex_ner.extract(text)

        # Get spaCy entities (person, organization, location) if available
        spacy_entities = []
        if self.spacy_ner and self.spacy_ner.available:
            spacy_entities = self.spacy_ner.extract(text)

        # Combine entities, removing duplicates
        # Priority: spaCy entities > regex entities for overlapping spans
        all_entities = regex_entities + spacy_entities

        # Remove overlapping entities (keep the one with higher confidence or from spaCy)
        filtered_entities = self._remove_overlaps(all_entities, prefer_spacy=True)

        return filtered_entities

    def extract_by_type(self, text: str, entity_type: EntityType) -> List[Entity]:
        """Extract specific entity type"""
        all_entities = self.extract_entities(text)
        return [e for e in all_entities if e.type == entity_type]

    def _remove_overlaps(self, entities: List[Entity], prefer_spacy: bool = True) -> List[Entity]:
        """
        Remove overlapping entities

        Args:
            entities: List of entities to filter
            prefer_spacy: If True, prefer spaCy entities over regex entities for overlaps

        Returns:
            Filtered list without overlaps
        """
        if not entities:
            return []

        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: (e.start, -e.confidence))

        filtered = []
        for entity in sorted_entities:
            # Check if this entity overlaps with any already added
            overlaps = False
            for existing in filtered:
                if self._is_overlap(entity, existing):
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(entity)

        return filtered

    @staticmethod
    def _is_overlap(e1: Entity, e2: Entity) -> bool:
        """Check if two entities overlap"""
        return not (e1.end <= e2.start or e2.end <= e1.start)


# Global instance
_ner_engine: Optional[NEREngine] = None


def get_ner_engine() -> NEREngine:
    """Get global NER engine"""
    global _ner_engine

    if _ner_engine is None:
        _ner_engine = NEREngine()

    return _ner_engine
