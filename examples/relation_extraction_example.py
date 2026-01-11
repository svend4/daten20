"""
Relation Extraction Examples

Demonstrates how to extract semantic relations between named entities.
"""

from src.ml.relation_extractor import RelationExtractor, RelationType, Relation


def example_basic_relations():
    """Basic relation extraction example"""
    print("\n=== Basic Relation Extraction ===")

    # Create relation extractor
    extractor = RelationExtractor(use_spacy=True, spacy_model="de_core_news_sm")

    text = """
    Max Mustermann arbeitet bei der Siemens AG in München.
    Angela Merkel war Bundeskanzlerin in Deutschland.
    """

    relations = extractor.extract_relations(text)

    print(f"Found {len(relations)} relations:")
    for rel in relations:
        print(f"\n{rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")
        print(f"  Confidence: {rel.confidence:.2f}")
        print(f"  Context: {rel.context[:80]}...")


def example_employment_relations():
    """Extract employment relationships"""
    print("\n=== Employment Relations (WORKS_AT) ===")

    extractor = RelationExtractor(use_spacy=True)

    text = """
    Max Mustermann ist Mitarbeiter der TechSolutions GmbH.
    Anna Schmidt arbeitet bei DataCorp AG.
    Tom Weber ist bei der Firma XYZ tätig.
    """

    # Extract only WORKS_AT relations
    relations = extractor.get_relations_by_type(text, RelationType.WORKS_AT)

    print(f"Found {len(relations)} employment relations:")
    for rel in relations:
        print(f"  • {rel.subject.text} works at {rel.object.text}")


def example_ceo_relations():
    """Extract CEO relationships"""
    print("\n=== CEO Relations ===")

    extractor = RelationExtractor(use_spacy=True)

    text = """
    Der Geschäftsführer Max Mustermann leitet die TechSolutions GmbH.
    Anna Schmidt ist Vorstand der DataCorp AG.
    Tim Cook ist CEO von Apple Inc.
    """

    # Extract CEO relations
    relations = extractor.get_relations_by_type(text, RelationType.CEO_OF)

    print(f"Found {len(relations)} CEO relations:")
    for rel in relations:
        print(f"  • {rel.subject.text} is CEO of {rel.object.text}")


def example_location_relations():
    """Extract location relationships"""
    print("\n=== Location Relations ===")

    extractor = RelationExtractor(use_spacy=True)

    text = """
    Die Siemens AG hat ihren Hauptsitz in München.
    Apple Inc. ist in Cupertino ansässig.
    Max Mustermann wohnt in Berlin.
    """

    # Extract location relations
    relations = extractor.extract_relations(text)
    location_rels = [r for r in relations if r.object.type.value == "location"]

    print(f"Found {len(location_rels)} location relations:")
    for rel in relations:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")


def example_contract_analysis():
    """Analyze contract for relationships"""
    print("\n=== Contract Analysis ===")

    extractor = RelationExtractor(use_spacy=True)

    contract = """
    DIENSTLEISTUNGSVERTRAG

    zwischen

    TechSolutions GmbH mit Sitz in München,
    vertreten durch den Geschäftsführer Max Mustermann,

    und

    DataCorp AG mit Hauptsitz in Berlin,
    vertreten durch die Vorständin Anna Schmidt.

    Die TechSolutions GmbH, gegründet von Max Mustermann im Jahr 2020,
    erbringt IT-Dienstleistungen für die DataCorp AG.
    """

    relations = extractor.extract_relations(contract)

    print(f"Contract contains {len(relations)} relationships:")

    # Group by relation type
    by_type = {}
    for rel in relations:
        if rel.relation not in by_type:
            by_type[rel.relation] = []
        by_type[rel.relation].append(rel)

    for rel_type, rels in sorted(by_type.items(), key=lambda x: x[0].value):
        print(f"\n{rel_type.value.upper()} ({len(rels)}):")
        for rel in rels:
            print(f"  • {rel.subject.text} → {rel.object.text}")


def example_entity_specific_relations():
    """Get all relations for specific entity"""
    print("\n=== Entity-Specific Relations ===")

    extractor = RelationExtractor(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei Siemens AG in München.
    Max Mustermann gründete TechSolutions GmbH im Jahr 2020.
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    """

    # Get all relations involving "Max Mustermann"
    relations = extractor.get_entity_relations(text, "Max Mustermann")

    print(f"Relations involving 'Max Mustermann': {len(relations)}")
    for rel in relations:
        if "Max Mustermann" in rel.subject.text:
            print(f"  • Max Mustermann --[{rel.relation.value}]--> {rel.object.text}")
        else:
            print(f"  • {rel.subject.text} --[{rel.relation.value}]--> Max Mustermann")


def example_multi_language():
    """Relation extraction in multiple languages"""
    print("\n=== Multi-Language Example ===")

    # German
    print("\nGerman:")
    extractor_de = RelationExtractor(use_spacy=True, spacy_model="de_core_news_sm")
    text_de = "Max Mustermann arbeitet bei Siemens AG in München."
    relations_de = extractor_de.extract_relations(text_de)
    for rel in relations_de:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")

    # English
    print("\nEnglish:")
    extractor_en = RelationExtractor(use_spacy=True, spacy_model="en_core_web_sm")
    text_en = "Tim Cook works at Apple Inc. in Cupertino."
    relations_en = extractor_en.extract_relations(text_en)
    for rel in relations_en:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")


def example_relation_graph():
    """Build a simple relation graph"""
    print("\n=== Relation Graph ===")

    extractor = RelationExtractor(use_spacy=True)

    text = """
    Die TechSolutions GmbH wurde von Max Mustermann gegründet.
    Max Mustermann ist Geschäftsführer der TechSolutions GmbH.
    Die TechSolutions GmbH hat ihren Sitz in München.
    Anna Schmidt arbeitet bei TechSolutions GmbH.
    DataCorp AG ist ein Kunde von TechSolutions GmbH.
    """

    relations = extractor.extract_relations(text)

    # Build adjacency list
    graph = {}
    for rel in relations:
        subj = rel.subject.text
        obj = rel.object.text
        relation = rel.relation.value

        if subj not in graph:
            graph[subj] = []
        graph[subj].append((relation, obj))

    # Print graph
    print("Relation Graph:")
    for entity, edges in sorted(graph.items()):
        print(f"\n{entity}:")
        for relation, target in edges:
            print(f"  --[{relation}]--> {target}")


def example_confidence_filtering():
    """Filter relations by confidence threshold"""
    print("\n=== Confidence Filtering ===")

    extractor = RelationExtractor(use_spacy=True)

    text = """
    Max Mustermann arbeitet bei Siemens AG.
    Anna Schmidt könnte bei DataCorp AG tätig sein.
    Tom Weber ist Mitarbeiter der XYZ GmbH.
    """

    relations = extractor.extract_relations(text)

    # Filter by confidence
    high_confidence = [r for r in relations if r.confidence >= 0.8]
    medium_confidence = [r for r in relations if 0.5 <= r.confidence < 0.8]

    print(f"High confidence (≥0.8): {len(high_confidence)}")
    for rel in high_confidence:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text} ({rel.confidence:.2f})")

    print(f"\nMedium confidence (0.5-0.8): {len(medium_confidence)}")
    for rel in medium_confidence:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text} ({rel.confidence:.2f})")


def example_pattern_based_vs_dependency():
    """Compare pattern-based vs dependency parsing"""
    print("\n=== Pattern-based vs Dependency Parsing ===")

    text = "Max Mustermann arbeitet bei der Siemens AG in München."

    # Pattern-based only (no spaCy)
    print("Pattern-based (no spaCy):")
    extractor_pattern = RelationExtractor(use_spacy=False)
    relations_pattern = extractor_pattern.extract_relations(text)
    print(f"  Found {len(relations_pattern)} relations")
    for rel in relations_pattern:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")

    # With dependency parsing
    print("\nWith dependency parsing (spaCy):")
    extractor_dep = RelationExtractor(use_spacy=True)
    relations_dep = extractor_dep.extract_relations(text)
    print(f"  Found {len(relations_dep)} relations")
    for rel in relations_dep:
        print(f"  • {rel.subject.text} --[{rel.relation.value}]--> {rel.object.text}")


def main():
    """Run all relation extraction examples"""
    print("=" * 70)
    print("Relation Extraction Examples")
    print("=" * 70)

    print("\nNOTE: These examples require spaCy models:")
    print("  German: python -m spacy download de_core_news_sm")
    print("  English: python -m spacy download en_core_web_sm")
    print()

    try:
        example_basic_relations()
        example_employment_relations()
        example_ceo_relations()
        example_location_relations()
        example_contract_analysis()
        example_entity_specific_relations()
        example_multi_language()
        example_relation_graph()
        example_confidence_filtering()
        example_pattern_based_vs_dependency()

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure spaCy and language models are installed:")
        print("  pip install spacy")
        print("  python -m spacy download de_core_news_sm")
        print("  python -m spacy download en_core_web_sm")

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
