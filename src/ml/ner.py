"""
Named Entity Recognition (NER)

Extracts entities from text:
- Person names
- Organizations
- Locations
- Dates
- Monetary amounts
- Custom entities
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import re


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
            EntityType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            EntityType.PHONE: r'\b\+?[\d\s\-\(\)]{10,20}\b',
            EntityType.MONEY: r'\b\d+[.,]\d{2}\s?(€|EUR|USD|\$)\b',
            EntityType.DATE: r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b',
            EntityType.IBAN: r'\b[A-Z]{2}\d{2}[\s]?[\d\s]{10,30}\b'
        }

    def extract(self, text: str) -> List[Entity]:
        """Extract entities"""
        entities = []

        for entity_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    text=match.group(),
                    type=entity_type,
                    start=match.start(),
                    end=match.end()
                ))

        return entities


class NEREngine:
    """Main NER engine"""

    def __init__(self):
        self.regex_ner = RegexNER()

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all entities"""
        return self.regex_ner.extract(text)

    def extract_by_type(self, text: str, entity_type: EntityType) -> List[Entity]:
        """Extract specific entity type"""
        all_entities = self.extract_entities(text)
        return [e for e in all_entities if e.type == entity_type]


# Global instance
_ner_engine: Optional[NEREngine] = None


def get_ner_engine() -> NEREngine:
    """Get global NER engine"""
    global _ner_engine

    if _ner_engine is None:
        _ner_engine = NEREngine()

    return _ner_engine
