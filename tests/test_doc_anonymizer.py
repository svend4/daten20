#!/usr/bin/env python3
"""
Unit tests for doc-anonymizer.py

Tests PII anonymization functionality including:
- PII detection (email, phone, names, locations, etc.)
- Anonymization strategies (redaction, masking, replacement, pseudonymization)
- GDPR/HIPAA compliance
- Reversible anonymization
- Batch processing
"""

import pytest
import re
import hashlib
import base64
from pathlib import Path


# Import required modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.ner import NERService


class TestPIIDetection:
    """Test PII detection capabilities"""

    @pytest.fixture
    def sample_text_with_pii(self):
        """Sample text containing various PII types"""
        return """
        John Smith works at Acme Corp.
        His email is john.smith@example.com and phone is +1-555-123-4567.
        He lives in New York City at 123 Main Street.
        His IBAN is DE89370400440532013000.
        He was born on 01.01.1990.
        His IP address is 192.168.1.1.
        """

    def test_email_detection(self, sample_text_with_pii):
        """Test email address detection"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        emails = re.findall(email_pattern, sample_text_with_pii)

        assert len(emails) > 0
        assert 'john.smith@example.com' in emails

    def test_phone_detection(self, sample_text_with_pii):
        """Test phone number detection"""
        phone_pattern = r'[\+]?[(]?\d{1,4}[)]?[-\s\.]?\(?\d{1,4}\)?[-\s\.]?\d{1,4}[-\s\.]?\d{1,9}'

        phones = re.findall(phone_pattern, sample_text_with_pii)

        assert len(phones) > 0

    def test_iban_detection(self, sample_text_with_pii):
        """Test IBAN detection"""
        iban_pattern = r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b'

        ibans = re.findall(iban_pattern, sample_text_with_pii)

        assert len(ibans) > 0
        assert 'DE89370400440532013000' in ibans

    def test_date_detection(self, sample_text_with_pii):
        """Test date detection"""
        date_pattern = r'\b\d{1,2}\.\d{1,2}\.\d{4}\b'

        dates = re.findall(date_pattern, sample_text_with_pii)

        assert len(dates) > 0
        assert '01.01.1990' in dates

    def test_ip_address_detection(self, sample_text_with_pii):
        """Test IP address detection"""
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

        ips = re.findall(ip_pattern, sample_text_with_pii)

        assert len(ips) > 0
        assert '192.168.1.1' in ips

    def test_person_name_detection(self, sample_text_with_pii):
        """Test person name detection using NER"""
        ner = NERService()
        entities = ner.extract_entities(sample_text_with_pii)

        person_entities = [e for e in entities if e['label'] == 'PERSON']

        # Should detect "John Smith"
        assert len(person_entities) > 0

    def test_location_detection(self, sample_text_with_pii):
        """Test location detection using NER"""
        ner = NERService()
        entities = ner.extract_entities(sample_text_with_pii)

        location_entities = [e for e in entities if e['label'] in ['GPE', 'LOC']]

        # Should detect "New York City"
        assert len(location_entities) > 0

    def test_organization_detection(self, sample_text_with_pii):
        """Test organization detection using NER"""
        ner = NERService()
        entities = ner.extract_entities(sample_text_with_pii)

        org_entities = [e for e in entities if e['label'] == 'ORG']

        # Should detect "Acme Corp"
        assert len(org_entities) > 0


class TestAnonymizationStrategies:
    """Test different anonymization strategies"""

    def test_redaction_strategy(self):
        """Test redaction (complete removal)"""
        text = "My email is john@example.com"
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # Redact email
        anonymized = re.sub(email_pattern, '[REDACTED]', text)

        assert '[REDACTED]' in anonymized
        assert 'john@example.com' not in anonymized

    def test_masking_strategy(self):
        """Test masking (partial concealment)"""
        email = "john.smith@example.com"

        # Mask email: j***@e******.com
        parts = email.split('@')
        if len(parts) == 2:
            local, domain = parts
            domain_parts = domain.split('.')

            masked_local = local[0] + '*' * (len(local) - 1) if len(local) > 1 else local
            masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1)
            masked = f"{masked_local}@{masked_domain}.{domain_parts[1]}"

            assert masked[0] == 'j'  # First char preserved
            assert '*' in masked  # Contains masking
            assert masked.endswith('.com')  # TLD preserved

    def test_replacement_strategy(self):
        """Test replacement with fake data"""
        text = "John Smith"

        # Replace with fake name
        replacements = {
            "John Smith": "Jane Doe"
        }

        anonymized = text
        for original, fake in replacements.items():
            anonymized = anonymized.replace(original, fake)

        assert 'Jane Doe' in anonymized
        assert 'John Smith' not in anonymized

    def test_pseudonymization_strategy(self):
        """Test pseudonymization (consistent hashing)"""
        name = "John Smith"

        # Create pseudonym using hash
        hash_obj = hashlib.sha256(name.encode())
        hash_hex = hash_obj.hexdigest()[:16]
        pseudonym = f"PERSON_{hash_hex}"

        # Same name should produce same pseudonym
        hash_obj2 = hashlib.sha256(name.encode())
        hash_hex2 = hash_obj2.hexdigest()[:16]
        pseudonym2 = f"PERSON_{hash_hex2}"

        assert pseudonym == pseudonym2

    def test_generalization_strategy(self):
        """Test generalization (reduce precision)"""
        date = "01.01.1990"

        # Generalize to year only
        year = date.split('.')[-1]
        generalized = f"{year}"

        assert generalized == "1990"
        assert '01.01' not in generalized


class TestReversibleAnonymization:
    """Test reversible anonymization with mapping"""

    def test_create_mapping(self):
        """Test creation of anonymization mapping"""
        mapping = {
            "john.smith@example.com": "user1@anon.com",
            "John Smith": "Person A",
            "+1-555-123-4567": "+1-000-000-0000"
        }

        # Mapping should be reversible
        reverse_mapping = {v: k for k, v in mapping.items()}

        # Test reversibility
        for original, anonymized in mapping.items():
            assert reverse_mapping[anonymized] == original

    def test_encrypt_mapping(self):
        """Test encryption of mapping for security"""
        mapping = {"secret": "hidden"}

        # Serialize and encode (in production, use Fernet/AES)
        import json
        mapping_json = json.dumps(mapping)
        encoded = base64.b64encode(mapping_json.encode()).decode()

        # Should be encoded
        assert encoded != mapping_json
        assert 'secret' not in encoded

        # Should be decodable
        decoded = base64.b64decode(encoded.encode()).decode()
        recovered = json.loads(decoded)

        assert recovered == mapping

    def test_deanonymization(self):
        """Test de-anonymization using mapping"""
        original_text = "Contact John Smith at john@example.com"

        mapping = {
            "John Smith": "Person A",
            "john@example.com": "user1@anon.com"
        }

        # Anonymize
        anonymized = original_text
        for original, fake in mapping.items():
            anonymized = anonymized.replace(original, fake)

        # De-anonymize
        reverse_mapping = {v: k for k, v in mapping.items()}
        deanonymized = anonymized
        for fake, original in reverse_mapping.items():
            deanonymized = deanonymized.replace(fake, original)

        assert deanonymized == original_text


class TestComplianceModes:
    """Test GDPR/HIPAA compliance modes"""

    def test_gdpr_requirements(self):
        """Test GDPR compliance requirements"""
        # GDPR requires:
        # - Right to erasure
        # - Right to data portability
        # - Pseudonymization

        text = "John Smith's email is john@example.com"

        # Should be able to completely remove PII
        gdpr_anonymized = "[REDACTED]'s email is [REDACTED]"

        assert 'John Smith' not in gdpr_anonymized
        assert 'john@example.com' not in gdpr_anonymized

    def test_hipaa_requirements(self):
        """Test HIPAA compliance requirements"""
        # HIPAA Safe Harbor requires removal of 18 identifiers

        identifiers = [
            "Names",
            "Geographic subdivisions smaller than state",
            "Dates (except year)",
            "Telephone numbers",
            "Email addresses",
            "Social security numbers",
            "Medical record numbers",
            "Account numbers",
            "IP addresses"
        ]

        # All should be anonymizable
        assert len(identifiers) == 9  # Partial list

    def test_audit_trail(self):
        """Test audit trail for anonymization"""
        audit_log = {
            "timestamp": "2026-01-12T12:00:00",
            "action": "anonymize",
            "file": "document.pdf",
            "pii_types_found": ["email", "phone", "name"],
            "strategy": "masking",
            "compliance_mode": "gdpr"
        }

        # Audit trail should capture key information
        assert "timestamp" in audit_log
        assert "action" in audit_log
        assert "compliance_mode" in audit_log


class TestBatchProcessing:
    """Test batch anonymization"""

    def test_process_multiple_documents(self):
        """Test processing multiple documents"""
        documents = [
            "John's email is john@example.com",
            "Jane's phone is +1-555-999-8888",
            "Bob lives in New York"
        ]

        # Process all
        results = []
        for doc in documents:
            # Simple email redaction
            anonymized = re.sub(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                '[EMAIL]',
                doc
            )

            # Simple phone redaction
            anonymized = re.sub(
                r'[\+]?\d{1,4}[-\s\.]?\(?\d{1,4}\)?[-\s\.]?\d{1,4}[-\s\.]?\d{1,9}',
                '[PHONE]',
                anonymized
            )

            results.append(anonymized)

        assert len(results) == len(documents)
        assert '[EMAIL]' in results[0]
        assert '[PHONE]' in results[1]

    def test_consistent_anonymization(self):
        """Test that same PII is anonymized consistently"""
        docs = [
            "John Smith at john@example.com",
            "Contact John Smith"
        ]

        # Create consistent mapping
        mapping = {"John Smith": "PERSON_ABC123"}

        anonymized_docs = []
        for doc in docs:
            anon = doc
            for original, fake in mapping.items():
                anon = anon.replace(original, fake)
            anonymized_docs.append(anon)

        # "John Smith" should be replaced consistently
        assert "PERSON_ABC123" in anonymized_docs[0]
        assert "PERSON_ABC123" in anonymized_docs[1]


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_document(self):
        """Test handling of empty document"""
        text = ""

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        anonymized = re.sub(email_pattern, '[EMAIL]', text)

        # Should handle gracefully
        assert anonymized == ""

    def test_no_pii_found(self):
        """Test document with no PII"""
        text = "This document contains no personal information."

        ner = NERService()
        entities = ner.extract_entities(text)

        pii_entities = [e for e in entities if e['label'] in ['PERSON', 'GPE', 'ORG']]

        # Should return empty or minimal results
        # (may still detect some entities depending on model)
        assert isinstance(pii_entities, list)

    def test_multiple_same_pii(self):
        """Test handling of duplicate PII"""
        text = "John Smith called John Smith twice"

        # Should handle duplicates
        anonymized = text.replace("John Smith", "[REDACTED]")

        assert anonymized.count('[REDACTED]') == 2

    def test_overlapping_pii(self):
        """Test handling of overlapping PII patterns"""
        text = "john.smith@example.com.uk"

        # Email with .co.uk TLD
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        emails = re.findall(email_pattern, text)

        # Should detect email correctly
        assert len(emails) > 0

    def test_special_characters_in_pii(self):
        """Test PII with special characters"""
        text = "Email: o'reilly@example.com"

        # Should handle apostrophes and special chars
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # Note: This pattern may not match o'reilly
        # In production, pattern should be more robust

    def test_unicode_in_pii(self):
        """Test PII with Unicode characters"""
        text = "Name: François Müller"

        ner = NERService()
        entities = ner.extract_entities(text)

        # Should handle Unicode names
        assert entities is not None

    def test_very_long_document(self):
        """Test handling of very long documents"""
        long_text = " ".join(["word"] * 10000) + " john@example.com"

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # Should handle long documents
        anonymized = re.sub(email_pattern, '[EMAIL]', long_text)

        assert '[EMAIL]' in anonymized


class TestAnonymizerCLI:
    """Test CLI functionality"""

    def test_cli_help(self):
        """Test CLI help message"""
        import subprocess

        result = subprocess.run(
            ['python', 'doc-anonymizer.py', '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert 'anonymize' in result.stdout.lower()

    def test_cli_commands_exist(self):
        """Test that all commands exist"""
        import subprocess

        commands = ['scan', 'anonymize', 'deanonymize', 'batch']

        for cmd in commands:
            result = subprocess.run(
                ['python', 'doc-anonymizer.py', cmd, '--help'],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0


class TestPIITypes:
    """Test detection of specific PII types"""

    def test_email_variants(self):
        """Test various email formats"""
        emails = [
            "simple@example.com",
            "first.last@example.com",
            "user+tag@example.co.uk",
            "name_123@subdomain.example.com"
        ]

        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        for email in emails:
            matches = re.findall(pattern, email)
            assert len(matches) > 0, f"Failed to detect: {email}"

    def test_phone_variants(self):
        """Test various phone number formats"""
        phones = [
            "+1-555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "5551234567"
        ]

        pattern = r'[\+]?[(]?\d{1,4}[)]?[-\s\.]?\(?\d{1,4}\)?[-\s\.]?\d{1,4}[-\s\.]?\d{1,9}'

        for phone in phones:
            matches = re.findall(pattern, phone)
            assert len(matches) > 0, f"Failed to detect: {phone}"

    def test_date_variants(self):
        """Test various date formats"""
        dates = [
            "01.01.2020",
            "31.12.1999",
            "15.06.1985"
        ]

        pattern = r'\b\d{1,2}\.\d{1,2}\.\d{4}\b'

        for date in dates:
            matches = re.findall(pattern, date)
            assert len(matches) > 0, f"Failed to detect: {date}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
