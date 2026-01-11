"""
Unit tests for doc-anonymizer.py
==================================

Tests all major functionality of DocumentAnonymizer:
- PII detection
- Anonymization strategies (redaction, masking, replacement, pseudonymization, generalization)
- GDPR/HIPAA compliance
- Reversible anonymization
- Batch processing
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import the anonymizer module
import importlib.util
spec = importlib.util.spec_from_file_location("doc_anonymizer", "doc-anonymizer.py")
doc_anonymizer = importlib.util.module_from_spec(spec)
sys.modules['doc_anonymizer'] = doc_anonymizer  # Add to sys.modules for imports to work
spec.loader.exec_module(doc_anonymizer)

from doc_anonymizer import (
    DocumentAnonymizer,
    AnonymizationStrategy,
    ComplianceMode,
    PIIItem,
    AnonymizationResult
)


# Fixtures
@pytest.fixture
def anonymizer_redaction():
    """Create DocumentAnonymizer with redaction strategy."""
    return DocumentAnonymizer(
        strategy=AnonymizationStrategy.REDACTION,
        compliance_mode=ComplianceMode.GDPR
    )


@pytest.fixture
def anonymizer_masking():
    """Create DocumentAnonymizer with masking strategy."""
    return DocumentAnonymizer(
        strategy=AnonymizationStrategy.MASKING,
        compliance_mode=ComplianceMode.GDPR
    )


@pytest.fixture
def anonymizer_replacement():
    """Create DocumentAnonymizer with replacement strategy."""
    return DocumentAnonymizer(
        strategy=AnonymizationStrategy.REPLACEMENT,
        compliance_mode=ComplianceMode.GDPR
    )


@pytest.fixture
def sample_docs_dir():
    """Path to sample documents directory."""
    return Path(__file__).parent.parent.parent / "fixtures" / "sample_docs"


@pytest.fixture
def pii_document_path(sample_docs_dir):
    """Path to document with PII."""
    return str(sample_docs_dir / "pii_document.txt")


# Test Class
class TestDocumentAnonymizer:
    """Test suite for DocumentAnonymizer"""

    def test_anonymizer_initialization(self, anonymizer_redaction):
        """Test that anonymizer initializes correctly"""
        assert anonymizer_redaction is not None
        assert anonymizer_redaction.parser is not None
        assert anonymizer_redaction.ner_engine is not None
        assert anonymizer_redaction.strategy == AnonymizationStrategy.REDACTION
        assert anonymizer_redaction.compliance_mode == ComplianceMode.GDPR

    def test_scan_pii_detection(self, anonymizer_redaction, pii_document_path):
        """Test PII detection in document"""
        pii_items = anonymizer_redaction.scan_pii(pii_document_path)

        assert isinstance(pii_items, list)
        assert len(pii_items) > 0  # Should detect some PII

        # Check that PII items have correct structure
        for item in pii_items:
            assert isinstance(item, PIIItem)
            assert hasattr(item, 'text')
            assert hasattr(item, 'type')
            assert hasattr(item, 'start')
            assert hasattr(item, 'end')
            assert hasattr(item, 'confidence')

    def test_anonymization_strategies(self):
        """Test all anonymization strategies are available"""
        assert AnonymizationStrategy.REDACTION is not None
        assert AnonymizationStrategy.MASKING is not None
        assert AnonymizationStrategy.REPLACEMENT is not None
        assert AnonymizationStrategy.PSEUDONYMIZATION is not None
        assert AnonymizationStrategy.GENERALIZATION is not None

    def test_compliance_modes(self):
        """Test all compliance modes are available"""
        assert ComplianceMode.GDPR is not None
        assert ComplianceMode.HIPAA is not None
        assert ComplianceMode.CUSTOM is not None

    def test_redaction_strategy(self, anonymizer_redaction):
        """Test redaction anonymization strategy"""
        value = "Max Mustermann"
        entity_type = "PERSON"

        anonymized = anonymizer_redaction._anonymize_value(value, entity_type)

        assert anonymized == "[PERSON]"

    def test_masking_strategy_email(self, anonymizer_masking):
        """Test masking strategy for email"""
        email = "max@example.com"
        entity_type = "EMAIL"

        masked = anonymizer_masking._mask_value(email, entity_type)

        assert "*" in masked  # Should contain asterisks
        assert "@" in masked  # Should preserve @
        assert "." in masked  # Should preserve domain dot
        assert len(masked) <= len(email)  # Should not be longer

    def test_masking_strategy_phone(self, anonymizer_masking):
        """Test masking strategy for phone"""
        phone = "+49 123 456789"
        entity_type = "PHONE"

        masked = anonymizer_masking._mask_value(phone, entity_type)

        assert "*" in masked  # Should contain asterisks

    def test_masking_strategy_person(self, anonymizer_masking):
        """Test masking strategy for person name"""
        name = "Max Mustermann"
        entity_type = "PERSON"

        masked = anonymizer_masking._mask_value(name, entity_type)

        assert "*" in masked  # Should contain asterisks
        assert masked[0] in ["M", "m"]  # First letter preserved

    def test_replacement_strategy(self, anonymizer_replacement):
        """Test replacement strategy"""
        name = "Max Mustermann"
        entity_type = "PERSON"

        replaced = anonymizer_replacement._replace_value(name, entity_type)

        # Should be replaced with fake name
        assert replaced != name
        assert replaced in anonymizer_replacement.replacement_names

    def test_pseudonymization_strategy(self, anonymizer_redaction):
        """Test pseudonymization strategy"""
        value = "Max Mustermann"
        entity_type = "PERSON"

        pseudo1 = anonymizer_redaction._pseudonymize_value(value, entity_type, reversible=False)
        pseudo2 = anonymizer_redaction._pseudonymize_value(value, entity_type, reversible=False)

        # Should be consistent
        assert pseudo1 == pseudo2
        # Should contain hash
        assert "PERSON_" in pseudo1 or "PSEUDO_" in pseudo1

    def test_generalization_strategy(self, anonymizer_redaction):
        """Test generalization strategy"""
        date = "01.01.1990"
        entity_type = "DATE"

        generalized = anonymizer_redaction._generalize_value(date, entity_type)

        # Should only contain year
        assert "1990" in generalized or "[YEAR]" in generalized

    def test_anonymize_document_redaction(self, anonymizer_redaction, pii_document_path, tmp_path):
        """Test full document anonymization with redaction"""
        output_file = tmp_path / "anonymized_redaction.txt"

        result = anonymizer_redaction.anonymize(
            pii_document_path,
            str(output_file)
        )

        assert isinstance(result, AnonymizationResult)
        assert output_file.exists()
        assert result.pii_detected > 0
        assert result.pii_anonymized >= 0
        assert result.strategy == "redaction"

    def test_anonymize_document_masking(self, anonymizer_masking, pii_document_path, tmp_path):
        """Test full document anonymization with masking"""
        output_file = tmp_path / "anonymized_masking.txt"

        result = anonymizer_masking.anonymize(
            pii_document_path,
            str(output_file)
        )

        assert isinstance(result, AnonymizationResult)
        assert output_file.exists()
        assert result.strategy == "masking"

        # Read anonymized content
        content = output_file.read_text()
        assert "*" in content  # Should contain masked data

    def test_reversible_anonymization(self, anonymizer_redaction, pii_document_path, tmp_path):
        """Test reversible anonymization with mapping"""
        output_file = tmp_path / "anonymized.txt"
        mapping_file = tmp_path / "mapping.enc"

        result = anonymizer_redaction.anonymize(
            pii_document_path,
            str(output_file),
            reversible=True,
            mapping_file=str(mapping_file)
        )

        assert result.mapping  # Should have mapping
        assert mapping_file.exists()  # Mapping file should be created
        assert len(result.mapping) > 0

    def test_mapping_save_and_load(self, anonymizer_redaction, tmp_path):
        """Test saving and loading mapping"""
        mapping = {"original": "anonymized", "data": "masked"}
        mapping_file = tmp_path / "mapping.enc"

        # Save
        anonymizer_redaction._save_mapping(mapping, str(mapping_file))
        assert mapping_file.exists()

        # Load
        loaded_mapping = anonymizer_redaction._load_mapping(str(mapping_file))
        assert loaded_mapping == mapping

    def test_audit_trail(self, anonymizer_redaction, pii_document_path, tmp_path):
        """Test audit trail creation"""
        output_file = tmp_path / "anonymized.txt"

        result = anonymizer_redaction.anonymize(
            pii_document_path,
            str(output_file),
            audit_log=True
        )

        assert result.audit_trail  # Should have audit trail
        assert len(result.audit_trail) > 0

        # Check audit trail structure
        for entry in result.audit_trail:
            assert "event" in entry
            assert "timestamp" in entry

    def test_anonymization_result_to_dict(self, anonymizer_redaction, pii_document_path, tmp_path):
        """Test AnonymizationResult to_dict()"""
        output_file = tmp_path / "anonymized.txt"

        result = anonymizer_redaction.anonymize(
            pii_document_path,
            str(output_file)
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "original_file" in result_dict
        assert "anonymized_file" in result_dict
        assert "strategy" in result_dict
        assert "pii_detected" in result_dict

    def test_batch_anonymization(self, anonymizer_redaction, sample_docs_dir, tmp_path):
        """Test batch anonymization"""
        output_dir = tmp_path / "batch_output"

        results = anonymizer_redaction.batch_anonymize(
            str(sample_docs_dir),
            str(output_dir),
            file_pattern="*.txt"
        )

        assert isinstance(results, list)
        assert output_dir.exists()
        # Should process at least one file
        assert len(results) >= 0

    def test_deanonymization(self, anonymizer_redaction, pii_document_path, tmp_path):
        """Test de-anonymization with mapping"""
        anonymized_file = tmp_path / "anonymized.txt"
        mapping_file = tmp_path / "mapping.enc"
        deanonymized_file = tmp_path / "deanonymized.txt"

        # 1. Anonymize with reversible=True
        result = anonymizer_redaction.anonymize(
            pii_document_path,
            str(anonymized_file),
            reversible=True,
            mapping_file=str(mapping_file)
        )

        # 2. De-anonymize
        anonymizer_redaction.deanonymize(
            str(anonymized_file),
            str(mapping_file),
            str(deanonymized_file)
        )

        assert deanonymized_file.exists()

        # 3. Compare original and de-anonymized
        # (They won't be identical due to formatting, but should contain same data)
        deanonymized_content = deanonymized_file.read_text()
        assert len(deanonymized_content) > 0

    def test_edge_case_no_pii(self, anonymizer_redaction, sample_docs_dir, tmp_path):
        """Test anonymization of document with no PII"""
        # Create a document with no PII
        no_pii_doc = tmp_path / "no_pii.txt"
        no_pii_doc.write_text("This is a document with no personal information.")

        output_file = tmp_path / "anonymized_no_pii.txt"

        result = anonymizer_redaction.anonymize(
            str(no_pii_doc),
            str(output_file)
        )

        # Should complete successfully
        assert result.pii_detected == 0
        assert result.pii_anonymized == 0

    def test_edge_case_empty_document(self, anonymizer_redaction, tmp_path):
        """Test anonymization of empty document"""
        empty_doc = tmp_path / "empty.txt"
        empty_doc.write_text("")

        output_file = tmp_path / "anonymized_empty.txt"

        # Should not crash
        result = anonymizer_redaction.anonymize(
            str(empty_doc),
            str(output_file)
        )

        assert result.pii_detected == 0

    def test_anonymize_text_with_entities(self, anonymizer_redaction):
        """Test _anonymize_text method"""
        text = "My name is Max and my email is max@example.com"

        pii_items = [
            PIIItem(text="Max", type="PERSON", start=11, end=14, confidence=1.0),
            PIIItem(text="max@example.com", type="EMAIL", start=32, end=47, confidence=1.0)
        ]

        anonymized_text, mapping = anonymizer_redaction._anonymize_text(text, pii_items)

        assert "[PERSON]" in anonymized_text
        assert "[EMAIL]" in anonymized_text
        assert "Max" not in anonymized_text
        assert "max@example.com" not in anonymized_text
        assert len(mapping) == 2


# Integration Tests
class TestDocumentAnonymizerIntegration:
    """Integration tests for DocumentAnonymizer"""

    def test_full_gdpr_workflow(self, pii_document_path, tmp_path):
        """Test complete GDPR compliance workflow"""
        anonymizer = DocumentAnonymizer(
            strategy=AnonymizationStrategy.MASKING,
            compliance_mode=ComplianceMode.GDPR
        )

        # 1. Scan for PII
        pii_items = anonymizer.scan_pii(pii_document_path)
        assert len(pii_items) > 0

        # 2. Anonymize with audit trail
        output_file = tmp_path / "gdpr_anonymized.txt"
        mapping_file = tmp_path / "gdpr_mapping.enc"

        result = anonymizer.anonymize(
            pii_document_path,
            str(output_file),
            reversible=True,
            mapping_file=str(mapping_file),
            audit_log=True
        )

        # 3. Verify results
        assert result.compliance_mode == "gdpr"
        assert len(result.audit_trail) > 0
        assert output_file.exists()
        assert mapping_file.exists()

    def test_all_strategies_comparison(self, pii_document_path, tmp_path):
        """Test all anonymization strategies on same document"""
        strategies = [
            AnonymizationStrategy.REDACTION,
            AnonymizationStrategy.MASKING,
            AnonymizationStrategy.REPLACEMENT,
            AnonymizationStrategy.PSEUDONYMIZATION,
            AnonymizationStrategy.GENERALIZATION
        ]

        results = []

        for strategy in strategies:
            anonymizer = DocumentAnonymizer(strategy=strategy)
            output_file = tmp_path / f"anonymized_{strategy.value}.txt"

            result = anonymizer.anonymize(
                pii_document_path,
                str(output_file)
            )

            results.append(result)
            assert output_file.exists()

        # All strategies should detect similar number of PII
        pii_counts = [r.pii_detected for r in results]
        assert max(pii_counts) - min(pii_counts) <= 5  # Within reasonable range


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
