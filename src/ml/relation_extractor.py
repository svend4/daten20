"""
Relation Extraction

Extracts semantic relationships between named entities using:
- spaCy dependency parsing
- Pattern-based relation templates
- Entity pair analysis

Supported relations:
- WORKS_AT: Person works at Organization
- LOCATED_IN: Organization/Person located in Location
- CEO_OF: Person is CEO of Organization
- PART_OF: Organization part of Organization
- FOUNDED: Person founded Organization
- ACQUIRED: Organization acquired Organization
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .ner import Entity, EntityType, NEREngine


class RelationType(str, Enum):
    """Types of relations between entities"""

    WORKS_AT = "works_at"  # Person works at Organization
    LOCATED_IN = "located_in"  # Entity located in Location
    CEO_OF = "ceo_of"  # Person is CEO of Organization
    MANAGER_OF = "manager_of"  # Person manages Organization
    PART_OF = "part_of"  # Organization part of Organization
    FOUNDED = "founded"  # Person founded Organization
    ACQUIRED = "acquired"  # Organization acquired Organization
    OWNS = "owns"  # Person/Org owns Organization
    MEMBER_OF = "member_of"  # Person member of Organization
    RESIDES_IN = "resides_in"  # Person resides in Location
    HEADQUARTERED_IN = "headquartered_in"  # Organization HQ in Location


@dataclass
class Relation:
    """Semantic relation between two entities"""

    subject: Entity  # Subject entity (e.g., "Max Mustermann")
    relation: RelationType  # Relation type (e.g., WORKS_AT)
    object: Entity  # Object entity (e.g., "Siemens AG")
    confidence: float  # Confidence score (0.0-1.0)
    context: str  # Original sentence/context
    start: int  # Start position in text
    end: int  # End position in text


class RelationExtractor:
    """Extract relations between entities using spaCy dependency parsing"""

    def __init__(self, use_spacy: bool = True, spacy_model: str = "de_core_news_sm"):
        """
        Initialize relation extractor

        Args:
            use_spacy: Whether to use spaCy for dependency parsing
            spacy_model: spaCy model to use
        """
        self.ner_engine = NEREngine(use_spacy=use_spacy, spacy_model=spacy_model)
        self.nlp = None
        self.available = False

        if use_spacy:
            try:
                import spacy

                self.nlp = spacy.load(spacy_model)
                self.available = True
            except (ImportError, OSError):
                self.available = False

        # Define relation patterns (verb/preposition patterns)
        self.relation_patterns = {
            RelationType.WORKS_AT: {
                "verbs": ["arbeiten", "work", "arbeitet", "tätig"],
                "preps": ["bei", "at", "für", "for"],
                "nouns": ["mitarbeiter", "employee", "angestellter"],
            },
            RelationType.CEO_OF: {
                "nouns": ["geschäftsführer", "ceo", "vorstand", "direktor", "director", "chief"],
                "preps": ["von", "of", "der", "des"],
            },
            RelationType.LOCATED_IN: {
                "verbs": ["befinden", "locate", "liegen", "sitzen"],
                "preps": ["in", "at", "zu"],
                "nouns": ["sitz", "standort", "location", "headquarters"],
            },
            RelationType.FOUNDED: {
                "verbs": ["gründen", "found", "establish", "gründete"],
                "nouns": ["gründer", "founder"],
            },
            RelationType.PART_OF: {
                "preps": ["von", "of"],
                "nouns": ["teil", "part", "tochter", "subsidiary", "sparte", "division"],
            },
        }

    def extract_relations(self, text: str) -> List[Relation]:
        """
        Extract all relations from text

        Args:
            text: Input text

        Returns:
            List of extracted relations
        """
        relations = []

        # Extract entities first
        entities = self.ner_engine.extract_entities(text)

        if not entities or len(entities) < 2:
            return relations

        # Use spaCy dependency parsing if available
        if self.available and self.nlp:
            relations.extend(self._extract_with_dependency_parsing(text, entities))

        # Use pattern-based extraction as fallback or complement
        relations.extend(self._extract_with_patterns(text, entities))

        # Remove duplicates
        relations = self._deduplicate_relations(relations)

        return relations

    def _extract_with_dependency_parsing(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations using spaCy dependency parsing"""
        relations = []

        try:
            doc = self.nlp(text)

            # Create entity map (token index -> entity)
            entity_map = {}
            for ent in doc.ents:
                for token in ent:
                    entity_map[token.i] = ent

            # Analyze dependency relations
            for token in doc:
                # Look for verb relations
                if token.pos_ == "VERB":
                    # Find subject and object
                    subject = None
                    obj = None

                    for child in token.children:
                        if child.dep_ in ["sb", "nsubj", "nsubjpass"]:  # Subject
                            if child.i in entity_map:
                                subject = entity_map[child.i]
                        elif child.dep_ in ["oa", "dobj", "pobj"]:  # Object
                            if child.i in entity_map:
                                obj = entity_map[child.i]

                    # If we found subject and object, try to determine relation type
                    if subject and obj:
                        relation_type = self._classify_relation(token.lemma_, subject, obj)
                        if relation_type:
                            # Find corresponding Entity objects
                            subj_entity = self._find_matching_entity(subject.text, entities)
                            obj_entity = self._find_matching_entity(obj.text, entities)

                            if subj_entity and obj_entity:
                                relations.append(
                                    Relation(
                                        subject=subj_entity,
                                        relation=relation_type,
                                        object=obj_entity,
                                        confidence=0.8,
                                        context=token.sent.text,
                                        start=token.sent.start_char,
                                        end=token.sent.end_char,
                                    )
                                )

        except Exception:
            # If dependency parsing fails, return empty list
            pass

        return relations

    def _extract_with_patterns(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations using pattern matching"""
        relations = []

        # Group entities by type
        persons = [e for e in entities if e.type == EntityType.PERSON]
        orgs = [e for e in entities if e.type == EntityType.ORGANIZATION]
        locations = [e for e in entities if e.type == EntityType.LOCATION]

        # Extract person-organization relations
        for person in persons:
            for org in orgs:
                relation = self._find_relation_between(text, person, org)
                if relation:
                    relations.append(relation)

        # Extract organization-location relations
        for org in orgs:
            for loc in locations:
                relation = self._find_relation_between(text, org, loc)
                if relation:
                    relations.append(relation)

        # Extract person-location relations
        for person in persons:
            for loc in locations:
                relation = self._find_relation_between(text, person, loc)
                if relation:
                    relations.append(relation)

        return relations

    def _find_relation_between(self, text: str, entity1: Entity, entity2: Entity) -> Optional[Relation]:
        """Find relation between two entities using pattern matching"""
        text_lower = text.lower()

        # Get text between entities
        if entity1.start < entity2.start:
            between_text = text[entity1.end : entity2.start].lower()
            subject = entity1
            obj = entity2
        else:
            between_text = text[entity2.end : entity1.start].lower()
            subject = entity2
            obj = entity1

        # Check for relation patterns
        relation_type = None
        confidence = 0.6

        # WORKS_AT pattern (Person -> Organization)
        if subject.type == EntityType.PERSON and obj.type == EntityType.ORGANIZATION:
            works_at_keywords = ["arbeitet bei", "works at", "tätig bei", "employed by", "mitarbeiter"]
            if any(kw in between_text for kw in works_at_keywords):
                relation_type = RelationType.WORKS_AT
                confidence = 0.9

        # CEO_OF pattern
        if subject.type == EntityType.PERSON and obj.type == EntityType.ORGANIZATION:
            ceo_keywords = ["geschäftsführer", "ceo", "vorstand", "director", "leiter"]
            if any(
                kw in between_text or kw in text_lower[max(0, subject.start - 20) : subject.end] for kw in ceo_keywords
            ):
                relation_type = RelationType.CEO_OF
                confidence = 0.85

        # LOCATED_IN pattern (Organization/Person -> Location)
        if obj.type == EntityType.LOCATION:
            location_keywords = ["in", "aus", "from", "based in", "sitz", "standort"]
            if any(kw in between_text for kw in location_keywords):
                if subject.type == EntityType.ORGANIZATION:
                    relation_type = RelationType.HEADQUARTERED_IN
                    confidence = 0.8
                elif subject.type == EntityType.PERSON:
                    relation_type = RelationType.RESIDES_IN
                    confidence = 0.75

        # FOUNDED pattern
        if subject.type == EntityType.PERSON and obj.type == EntityType.ORGANIZATION:
            founded_keywords = ["gründete", "founded", "gründer", "founder"]
            if any(kw in between_text for kw in founded_keywords):
                relation_type = RelationType.FOUNDED
                confidence = 0.85

        if relation_type:
            # Find sentence containing both entities
            sentences = text.split(".")
            context = text
            start = 0
            end = len(text)

            for sentence in sentences:
                if subject.text in sentence and obj.text in sentence:
                    context = sentence.strip()
                    start = text.find(sentence)
                    end = start + len(sentence)
                    break

            return Relation(
                subject=subject,
                relation=relation_type,
                object=obj,
                confidence=confidence,
                context=context,
                start=start,
                end=end,
            )

        return None

    def _classify_relation(self, verb: str, subject_ent, object_ent) -> Optional[RelationType]:
        """Classify relation type based on verb and entity types"""
        verb_lower = verb.lower()

        # Check against relation patterns
        for rel_type, patterns in self.relation_patterns.items():
            if "verbs" in patterns and verb_lower in [v.lower() for v in patterns["verbs"]]:
                # Validate entity types
                if self._valid_entity_types_for_relation(rel_type, subject_ent.label_, object_ent.label_):
                    return rel_type

        return None

    def _valid_entity_types_for_relation(self, relation: RelationType, subj_label: str, obj_label: str) -> bool:
        """Check if entity types are valid for given relation"""
        valid_combinations = {
            RelationType.WORKS_AT: [("PERSON", "ORG"), ("PER", "ORG")],
            RelationType.CEO_OF: [("PERSON", "ORG"), ("PER", "ORG")],
            RelationType.LOCATED_IN: [("ORG", "LOC"), ("ORG", "GPE"), ("PERSON", "LOC")],
            RelationType.FOUNDED: [("PERSON", "ORG"), ("PER", "ORG")],
        }

        if relation in valid_combinations:
            return (subj_label, obj_label) in valid_combinations[relation]

        return True

    def _find_matching_entity(self, text: str, entities: List[Entity]) -> Optional[Entity]:
        """Find entity matching given text"""
        for entity in entities:
            if entity.text == text or text in entity.text or entity.text in text:
                return entity
        return None

    def _deduplicate_relations(self, relations: List[Relation]) -> List[Relation]:
        """Remove duplicate relations"""
        seen = set()
        unique_relations = []

        for rel in relations:
            # Create signature for relation
            signature = (rel.subject.text, rel.relation.value, rel.object.text)

            if signature not in seen:
                seen.add(signature)
                unique_relations.append(rel)
            else:
                # If duplicate, keep the one with higher confidence
                for i, existing in enumerate(unique_relations):
                    if (existing.subject.text, existing.relation.value, existing.object.text) == signature:
                        if rel.confidence > existing.confidence:
                            unique_relations[i] = rel
                        break

        return unique_relations

    def get_relations_by_type(self, text: str, relation_type: RelationType) -> List[Relation]:
        """Extract only specific relation type"""
        all_relations = self.extract_relations(text)
        return [r for r in all_relations if r.relation == relation_type]

    def get_entity_relations(self, text: str, entity_text: str) -> List[Relation]:
        """Get all relations involving a specific entity"""
        all_relations = self.extract_relations(text)
        return [r for r in all_relations if entity_text in r.subject.text or entity_text in r.object.text]


# Global instance
_relation_extractor: Optional[RelationExtractor] = None


def get_relation_extractor(use_spacy: bool = True, spacy_model: str = "de_core_news_sm") -> RelationExtractor:
    """Get global relation extractor instance"""
    global _relation_extractor

    if _relation_extractor is None:
        _relation_extractor = RelationExtractor(use_spacy=use_spacy, spacy_model=spacy_model)

    return _relation_extractor
