"""
Named Entity Recognition (NER) Examples

Demonstrates how to use the enhanced NER system with spaCy support.
"""

from src.ml.ner import NEREngine, EntityType, Entity


def example_basic_ner():
    """Basic NER example with regex-only"""
    print("\n=== Basic NER (Regex Only) ===")

    # Create NER engine without spaCy
    ner = NEREngine(use_spacy=False)

    text = """
    Kontakt: max.mustermann@firma.de
    Telefon: +49 30 123456789
    Betrag: 1500.00 EUR
    Datum: 15.03.2024
    IBAN: DE89 3704 0044 0532 0130 00
    """

    entities = ner.extract_entities(text)

    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.type.value:15} | {entity.text:30} | pos: {entity.start}-{entity.end}")


def example_spacy_ner():
    """spaCy NER example for persons, organizations, locations"""
    print("\n=== spaCy NER (Persons, Organizations, Locations) ===")

    # Create NER engine with spaCy (German model)
    ner = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")

    text = """
    Max Mustermann arbeitet bei der Firma GmbH in Berlin.
    Angela Merkel war Bundeskanzlerin in Deutschland.
    Die Siemens AG hat ihren Hauptsitz in München.
    """

    entities = ner.extract_entities(text)

    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.type.value:15} | {entity.text:30} | confidence: {entity.confidence:.2f}")


def example_combined_ner():
    """Combined NER example with both regex and spaCy"""
    print("\n=== Combined NER (Regex + spaCy) ===")

    # Create NER engine with both methods
    ner = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")

    text = """
    Sehr geehrter Herr Schmidt,

    vielen Dank für Ihre Anfrage. Die Firma TechSolutions GmbH mit Sitz in München
    kann Ihnen ein Angebot über 25.000,00 EUR unterbreiten.

    Für Rückfragen stehen wir unter info@techsolutions.de oder +49 89 123456 zur Verfügung.
    Bitte überweisen Sie den Betrag auf unser Konto: DE12 5001 0517 0648 4898 90.

    Mit freundlichen Grüßen
    Anna Weber
    Geschäftsführerin
    """

    entities = ner.extract_entities(text)

    print(f"Found {len(entities)} entities:")

    # Group by type
    by_type = {}
    for entity in entities:
        if entity.type not in by_type:
            by_type[entity.type] = []
        by_type[entity.type].append(entity)

    # Print grouped
    for entity_type, entities_list in sorted(by_type.items(), key=lambda x: x[0].value):
        print(f"\n{entity_type.value.upper()}:")
        for entity in entities_list:
            print(f"  - {entity.text}")


def example_entity_by_type():
    """Extract specific entity types"""
    print("\n=== Extract Specific Entity Types ===")

    ner = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")

    text = """
    Apple Inc. hat einen neuen Store in New York eröffnet.
    Tim Cook war bei der Eröffnung anwesend.
    Kontakt: info@apple.com
    """

    # Extract only persons
    persons = ner.extract_by_type(text, EntityType.PERSON)
    print(f"\nPersons ({len(persons)}):")
    for person in persons:
        print(f"  - {person.text}")

    # Extract only organizations
    orgs = ner.extract_by_type(text, EntityType.ORGANIZATION)
    print(f"\nOrganizations ({len(orgs)}):")
    for org in orgs:
        print(f"  - {org.text}")

    # Extract only locations
    locations = ner.extract_by_type(text, EntityType.LOCATION)
    print(f"\nLocations ({len(locations)}):")
    for location in locations:
        print(f"  - {location.text}")

    # Extract only emails
    emails = ner.extract_by_type(text, EntityType.EMAIL)
    print(f"\nEmails ({len(emails)}):")
    for email in emails:
        print(f"  - {email.text}")


def example_english_ner():
    """NER example with English text"""
    print("\n=== English NER Example ===")

    # Create NER engine with English spaCy model
    ner = NEREngine(use_spacy=True, spacy_model="en_core_web_sm")

    text = """
    Apple Inc. CEO Tim Cook announced new products in San Francisco.
    The company, headquartered in Cupertino, California, reported revenue of $100 billion.
    Contact: investor.relations@apple.com or call +1 408-996-1010.
    """

    entities = ner.extract_entities(text)

    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.type.value:15} | {entity.text:30}")


def example_fallback_behavior():
    """Demonstrate fallback when spaCy not available"""
    print("\n=== Fallback Behavior (spaCy not available) ===")

    # This will try to load spaCy, but fall back to regex if unavailable
    ner = NEREngine(use_spacy=True, spacy_model="nonexistent_model")

    text = """
    Email: test@example.com
    Phone: +49 30 123456
    Amount: 500.00 EUR
    """

    entities = ner.extract_entities(text)

    if ner.spacy_ner and ner.spacy_ner.available:
        print("spaCy is available and being used")
    else:
        print("spaCy not available, using regex-only fallback")

    print(f"\nFound {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.type.value:15} | {entity.text}")


def example_document_processing():
    """Real-world document processing example"""
    print("\n=== Document Processing Example ===")

    ner = NEREngine(use_spacy=True, spacy_model="de_core_news_sm")

    # Simulate a service agreement document
    document = """
    DIENSTLEISTUNGSVERTRAG

    zwischen

    TechSolutions GmbH
    Hauptstraße 123
    80331 München
    vertreten durch den Geschäftsführer Max Mustermann

    und

    DataCorp AG
    Bahnhofstraße 45
    10115 Berlin
    vertreten durch die Vorständin Anna Schmidt

    1. Vertragsgegenstand
    Die TechSolutions GmbH erbringt IT-Dienstleistungen für die DataCorp AG.

    2. Vergütung
    Die monatliche Vergütung beträgt 5.000,00 EUR zzgl. MwSt.

    3. Kontakt
    Bei Fragen kontaktieren Sie bitte:
    - Max Mustermann: max.mustermann@techsolutions.de, +49 89 123456
    - Anna Schmidt: anna.schmidt@datacorp.de, +49 30 789012

    Zahlungen bitte an: DE89 3704 0044 0532 0130 00

    München, den 15.03.2024
    """

    entities = ner.extract_entities(document)

    # Analyze document structure
    print(f"Document Analysis: Found {len(entities)} entities\n")

    # Extract key information
    persons = [e for e in entities if e.type == EntityType.PERSON]
    organizations = [e for e in entities if e.type == EntityType.ORGANIZATION]
    locations = [e for e in entities if e.type == EntityType.LOCATION]
    emails = [e for e in entities if e.type == EntityType.EMAIL]
    phones = [e for e in entities if e.type == EntityType.PHONE]
    money = [e for e in entities if e.type == EntityType.MONEY]

    print(f"Key Parties:")
    print(f"  Persons: {', '.join([p.text for p in persons])}")
    print(f"  Organizations: {', '.join([o.text for o in organizations])}")
    print(f"  Locations: {', '.join([l.text for l in locations])}")

    print(f"\nContact Information:")
    for email in emails:
        print(f"  Email: {email.text}")
    for phone in phones:
        print(f"  Phone: {phone.text}")

    print(f"\nFinancial Information:")
    for amount in money:
        print(f"  Amount: {amount.text}")


def main():
    """Run all NER examples"""
    print("=" * 70)
    print("Named Entity Recognition (NER) Examples")
    print("=" * 70)

    print("\nNOTE: Some examples require spaCy models to be installed:")
    print("  German: python -m spacy download de_core_news_sm")
    print("  English: python -m spacy download en_core_web_sm")
    print()

    try:
        example_basic_ner()
        example_spacy_ner()
        example_combined_ner()
        example_entity_by_type()
        example_english_ner()
        example_fallback_behavior()
        example_document_processing()

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure to install spaCy and download language models:")
        print("  pip install spacy")
        print("  python -m spacy download de_core_news_sm")
        print("  python -m spacy download en_core_web_sm")

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
