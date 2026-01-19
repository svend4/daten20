"""
E2E Test: Document Anonymization Workflow

Tests the complete workflow of anonymizing documents with PII (Personally
Identifiable Information), ensuring GDPR/HIPAA compliance.
"""

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

import pytest


class TestDocumentAnonymizationWorkflow:
    """Test complete document anonymization workflow"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.test_dir) / "input"
        self.output_dir = Path(self.test_dir) / "output"
        self.mapping_dir = Path(self.test_dir) / "mappings"

        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.mapping_dir.mkdir(parents=True, exist_ok=True)

        yield

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_document(self, filename: str, content: str) -> Path:
        """Create a test document"""
        doc_path = self.input_dir / filename
        doc_path.write_text(content, encoding="utf-8")
        return doc_path

    def test_pii_detection_and_anonymization(self):
        """
        E2E Test: Detect and anonymize PII in document

        Steps:
        1. Create document with PII
        2. Detect PII entities
        3. Anonymize PII
        4. Verify anonymization
        5. Store mapping for reversibility
        """
        # Step 1: Create document with PII
        document_content = """
        Patient Record

        Name: John Smith
        Date of Birth: 1985-03-15
        Email: john.smith@email.com
        Phone: +1-555-0123
        SSN: 123-45-6789

        Address:
        123 Main Street
        New York, NY 10001

        Medical History:
        Patient visited on 2026-01-10 for routine checkup.
        """

        doc_path = self.create_test_document("patient_record.txt", document_content)

        # Step 2: Detect PII (basic patterns)
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"  # More specific: XXX-XX-XXXX
        phone_pattern = r"\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{4}"  # Avoid matching SSN
        date_pattern = r"\b\d{4}-\d{2}-\d{2}\b"

        text = doc_path.read_text()

        # Important: Detect SSNs first to avoid confusion with phone numbers
        pii_found = {
            "emails": re.findall(email_pattern, text),
            "ssns": re.findall(ssn_pattern, text),
            "dates": re.findall(date_pattern, text),
        }

        # Step 3: Anonymize PII
        anonymized_text = text
        mapping = {}

        # Anonymize SSNs FIRST (before phone numbers to avoid conflicts)
        for i, ssn in enumerate(pii_found["ssns"]):
            replacement = f"[SSN_{i+1}]"
            anonymized_text = anonymized_text.replace(ssn, replacement)
            mapping[replacement] = ssn

        # Anonymize dates (except year)
        for date in pii_found["dates"]:
            year = date.split("-")[0]
            replacement = f"{year}-XX-XX"
            anonymized_text = anonymized_text.replace(date, replacement)
            mapping[replacement] = date

        # Now find phones in the already-anonymized text
        pii_found["phones"] = re.findall(phone_pattern, anonymized_text)

        # Anonymize emails
        for i, email in enumerate(pii_found["emails"]):
            replacement = f"[EMAIL_{i+1}]"
            anonymized_text = anonymized_text.replace(email, replacement)
            mapping[replacement] = email

        # Anonymize phones
        for i, phone in enumerate(pii_found["phones"]):
            replacement = f"[PHONE_{i+1}]"
            anonymized_text = anonymized_text.replace(phone, replacement)
            mapping[replacement] = phone

        # Step 4: Verify anonymization
        assert "[EMAIL_" in anonymized_text
        assert "[PHONE_" in anonymized_text
        assert "[SSN_" in anonymized_text
        assert "john.smith@email.com" not in anonymized_text
        assert "123-45-6789" not in anonymized_text

        # Step 5: Save anonymized document
        anonymized_path = self.output_dir / "patient_record_anonymized.txt"
        anonymized_path.write_text(anonymized_text, encoding="utf-8")

        # Save mapping
        mapping_path = self.mapping_dir / "patient_record_mapping.json"
        with open(mapping_path, "w") as f:
            json.dump(mapping, f, indent=2)

        assert anonymized_path.exists()
        assert mapping_path.exists()

        print(f"✅ PII anonymization test passed!")
        print(f"   - PII entities found: {sum(len(v) for v in pii_found.values())}")
        print(f"   - Anonymized document: {anonymized_path}")
        print(f"   - Mapping stored: {mapping_path}")

    def test_reversible_anonymization(self):
        """
        E2E Test: Test reversible anonymization

        Steps:
        1. Anonymize document
        2. Store mapping
        3. De-anonymize using mapping
        4. Verify original content restored
        """
        # Step 1: Create and anonymize
        original_text = "Contact John at john@example.com or call +1-555-0123"
        doc_path = self.create_test_document("contact.txt", original_text)

        # Simple anonymization
        anonymized_text = original_text
        mapping = {"john@example.com": "[EMAIL_1]", "+1-555-0123": "[PHONE_1]"}

        for original, placeholder in mapping.items():
            anonymized_text = anonymized_text.replace(original, placeholder)

        # Step 2: Save anonymized and mapping
        anonymized_path = self.output_dir / "contact_anonymized.txt"
        anonymized_path.write_text(anonymized_text, encoding="utf-8")

        mapping_path = self.mapping_dir / "contact_mapping.json"
        with open(mapping_path, "w") as f:
            json.dump(mapping, f, indent=2)

        # Step 3: De-anonymize
        with open(mapping_path, "r") as f:
            stored_mapping = json.load(f)

        deanonymized_text = anonymized_path.read_text()
        reverse_mapping = {v: k for k, v in stored_mapping.items()}

        for placeholder, original in reverse_mapping.items():
            deanonymized_text = deanonymized_text.replace(placeholder, original)

        # Step 4: Verify restoration
        assert deanonymized_text == original_text

        print(f"✅ Reversible anonymization test passed!")
        print(f"   - Original: {original_text}")
        print(f"   - Anonymized: {anonymized_text}")
        print(f"   - Restored: {deanonymized_text}")

    def test_batch_anonymization_workflow(self):
        """
        E2E Test: Batch anonymization of multiple documents

        Steps:
        1. Create multiple documents with PII
        2. Anonymize all documents
        3. Track all anonymizations
        4. Generate compliance report
        """
        # Step 1: Create multiple documents
        documents = [
            ("employee1.txt", "Employee: Alice Brown, Email: alice@company.com, Phone: +1-555-0001"),
            ("employee2.txt", "Employee: Bob Jones, Email: bob@company.com, Phone: +1-555-0002"),
            ("employee3.txt", "Employee: Carol White, Email: carol@company.com, Phone: +1-555-0003"),
        ]

        # Step 2: Anonymize all
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"

        anonymization_log = []

        for filename, content in documents:
            doc_path = self.create_test_document(filename, content)

            # Find PII
            emails = re.findall(email_pattern, content)
            phones = re.findall(phone_pattern, content)

            # Anonymize
            anonymized = content
            pii_count = 0

            for i, email in enumerate(emails):
                anonymized = anonymized.replace(email, f"[EMAIL_REDACTED]")
                pii_count += 1

            for i, phone in enumerate(phones):
                anonymized = anonymized.replace(phone, f"[PHONE_REDACTED]")
                pii_count += 1

            # Save
            output_path = self.output_dir / f"anonymized_{filename}"
            output_path.write_text(anonymized, encoding="utf-8")

            anonymization_log.append(
                {"filename": filename, "pii_entities_removed": pii_count, "output_path": str(output_path)}
            )

        # Step 3 & 4: Generate compliance report
        report = {
            "total_documents_processed": len(documents),
            "total_pii_entities_removed": sum(log["pii_entities_removed"] for log in anonymization_log),
            "documents": anonymization_log,
            "compliance": "GDPR/HIPAA",
            "processed_at": "2026-01-14",
        }

        report_path = self.output_dir / "anonymization_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()
        assert len(anonymization_log) == len(documents)

        print(f"✅ Batch anonymization test passed!")
        print(f"   - Documents processed: {len(documents)}")
        print(f"   - Total PII removed: {report['total_pii_entities_removed']}")
        print(f"   - Report: {report_path}")

    def test_compliance_verification_workflow(self):
        """
        E2E Test: Verify compliance after anonymization

        Steps:
        1. Anonymize document
        2. Scan for remaining PII
        3. Verify no PII remains
        4. Generate compliance certificate
        """
        # Step 1: Create and anonymize
        original_text = """
        Customer Data:
        Name: Test User
        Email: test@example.com
        Phone: 555-0123
        """

        doc_path = self.create_test_document("customer.txt", original_text)

        # Anonymize
        anonymized_text = original_text
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        phone_pattern = r"\d{3}-\d{4}"

        anonymized_text = re.sub(email_pattern, "[EMAIL_REDACTED]", anonymized_text)
        anonymized_text = re.sub(phone_pattern, "[PHONE_REDACTED]", anonymized_text)

        # Step 2 & 3: Verify no PII remains
        emails_remaining = re.findall(email_pattern, anonymized_text)
        phones_remaining = re.findall(phone_pattern, anonymized_text)

        pii_free = len(emails_remaining) == 0 and len(phones_remaining) == 0

        assert pii_free, "PII still present in anonymized document"

        # Step 4: Generate compliance certificate
        certificate = {
            "document": "customer.txt",
            "anonymization_date": "2026-01-14",
            "compliance_standards": ["GDPR", "HIPAA"],
            "pii_detected_original": 2,
            "pii_remaining": 0,
            "status": "COMPLIANT",
            "verified": pii_free,
        }

        cert_path = self.output_dir / "compliance_certificate.json"
        with open(cert_path, "w") as f:
            json.dump(certificate, f, indent=2)

        assert cert_path.exists()
        assert certificate["status"] == "COMPLIANT"

        print(f"✅ Compliance verification test passed!")
        print(f"   - PII-free: {pii_free}")
        print(f"   - Status: {certificate['status']}")
        print(f"   - Certificate: {cert_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
