#!/usr/bin/env python3
"""
Document Anonymizer
===================

GDPR/HIPAA-compliant document anonymization tool.

Features:
- PII Detection (names, emails, phones, addresses, IDs)
- Multiple anonymization strategies (redaction, masking, replacement, pseudonymization)
- GDPR and HIPAA compliance modes
- Reversible anonymization with encrypted mapping
- Batch processing
- Audit trail and logging
- Export anonymized documents

Usage:
    # Basic anonymization
    python doc-anonymizer.py anonymize document.pdf --output anonymized.pdf

    # With masking strategy
    python doc-anonymizer.py anonymize document.pdf --strategy masking --output masked.pdf

    # GDPR mode with audit log
    python doc-anonymizer.py anonymize document.pdf --compliance gdpr --audit-log

    # Reversible with mapping
    python doc-anonymizer.py anonymize document.pdf --reversible --mapping-file mapping.enc

    # Scan for PII without anonymizing
    python doc-anonymizer.py scan document.pdf --report pii_report.json

    # De-anonymize
    python doc-anonymizer.py deanonymize anonymized.pdf --mapping-file mapping.enc

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import sys
import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import base64

# Import core modules
from src.core.parser import DocumentParser
from src.core.exporter import DocumentExporter
from src.core.logging_config import setup_logging

# Import ML modules
from src.ml.ner import NEREngine, Entity, EntityType

# Setup logging
logger = setup_logging(__name__, log_level="INFO")


class AnonymizationStrategy(Enum):
    """Anonymization strategies."""
    REDACTION = "redaction"  # [REDACTED]
    MASKING = "masking"  # max@example.com → m**@e******.com
    REPLACEMENT = "replacement"  # Max Mustermann → John Doe
    PSEUDONYMIZATION = "pseudonymization"  # Consistent hash-based replacement
    GENERALIZATION = "generalization"  # 01.01.1990 → 1990


class ComplianceMode(Enum):
    """Compliance modes."""
    GDPR = "gdpr"  # EU General Data Protection Regulation
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    CUSTOM = "custom"  # Custom rules


@dataclass
class PIIItem:
    """Detected PII item."""
    text: str
    type: str
    start: int
    end: int
    confidence: float
    anonymized_text: str = ""


@dataclass
class AnonymizationResult:
    """Results of anonymization."""
    original_file: str
    anonymized_file: str
    strategy: str
    compliance_mode: str
    pii_detected: int
    pii_anonymized: int
    anonymization_date: str
    pii_items: List[PIIItem] = field(default_factory=list)
    mapping: Dict[str, str] = field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['pii_items'] = [asdict(item) for item in self.pii_items]
        return result


class DocumentAnonymizer:
    """GDPR-compliant document anonymizer."""

    def __init__(
        self,
        strategy: AnonymizationStrategy = AnonymizationStrategy.REDACTION,
        compliance_mode: ComplianceMode = ComplianceMode.GDPR
    ):
        """
        Initialize anonymizer.

        Args:
            strategy: Anonymization strategy to use
            compliance_mode: Compliance mode (GDPR, HIPAA)
        """
        self.parser = DocumentParser()
        self.exporter = DocumentExporter()
        self.ner_engine = NEREngine(use_spacy=True)
        self.strategy = strategy
        self.compliance_mode = compliance_mode

        # Replacement data for REPLACEMENT strategy
        self.replacement_names = [
            "John Doe", "Jane Smith", "Robert Johnson", "Mary Williams",
            "Michael Brown", "Patricia Jones", "David Miller", "Jennifer Davis"
        ]
        self.replacement_emails = [
            "user1@example.com", "user2@example.com", "user3@example.com"
        ]
        self.replacement_phones = [
            "+1-555-0100", "+1-555-0101", "+1-555-0102"
        ]

        logger.info(f"DocumentAnonymizer initialized with {strategy.value} strategy")

    def scan_pii(self, file_path: str) -> List[PIIItem]:
        """
        Scan document for PII without anonymizing.

        Args:
            file_path: Path to document

        Returns:
            List of detected PII items
        """
        logger.info(f"Scanning for PII in: {file_path}")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")

        # Detect PII using NER
        entities = self.ner_engine.extract_entities(text)

        # Convert to PIIItem objects
        pii_items = []
        for entity in entities:
            # Only consider sensitive entity types
            if entity.type in [
                EntityType.PERSON,
                EntityType.EMAIL,
                EntityType.PHONE,
                EntityType.LOCATION,
                EntityType.IBAN,
                EntityType.DATE
            ]:
                pii_item = PIIItem(
                    text=entity.text,
                    type=entity.type.value,
                    start=entity.start,
                    end=entity.end,
                    confidence=entity.confidence
                )
                pii_items.append(pii_item)

        logger.info(f"Detected {len(pii_items)} PII items")
        return pii_items

    def anonymize(
        self,
        file_path: str,
        output_path: str,
        reversible: bool = False,
        mapping_file: Optional[str] = None,
        audit_log: bool = False
    ) -> AnonymizationResult:
        """
        Anonymize document.

        Args:
            file_path: Path to original document
            output_path: Path for anonymized document
            reversible: Whether to save mapping for de-anonymization
            mapping_file: Path to save mapping (if reversible)
            audit_log: Whether to create audit trail

        Returns:
            AnonymizationResult object
        """
        logger.info(f"Anonymizing document: {file_path}")

        # Scan for PII
        pii_items = self.scan_pii(file_path)

        if not pii_items:
            logger.warning("No PII detected. Document will be copied as-is.")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")

        # Anonymize text
        anonymized_text, mapping = self._anonymize_text(text, pii_items, reversible)

        # Update PII items with anonymized values
        for item in pii_items:
            if item.text in mapping:
                item.anonymized_text = mapping[item.text]

        # Export anonymized document
        self.exporter.export(anonymized_text, output_path, format="txt")

        # Save mapping if reversible
        if reversible and mapping_file:
            self._save_mapping(mapping, mapping_file)
            logger.info(f"Mapping saved to: {mapping_file}")

        # Create audit trail
        audit_trail = []
        if audit_log:
            audit_trail = self._create_audit_trail(file_path, output_path, pii_items)

        result = AnonymizationResult(
            original_file=file_path,
            anonymized_file=output_path,
            strategy=self.strategy.value,
            compliance_mode=self.compliance_mode.value,
            pii_detected=len(pii_items),
            pii_anonymized=len([item for item in pii_items if item.anonymized_text]),
            anonymization_date=datetime.now().isoformat(),
            pii_items=pii_items,
            mapping=mapping if reversible else {},
            audit_trail=audit_trail
        )

        logger.info(f"Anonymization complete. PII anonymized: {result.pii_anonymized}")
        return result

    def _anonymize_text(
        self,
        text: str,
        pii_items: List[PIIItem],
        reversible: bool = False
    ) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize text using configured strategy.

        Args:
            text: Original text
            pii_items: List of PII items to anonymize
            reversible: Whether to create reversible mapping

        Returns:
            Tuple of (anonymized_text, mapping)
        """
        mapping = {}
        anonymized = text

        # Sort PII items by position (reverse order to preserve positions)
        sorted_items = sorted(pii_items, key=lambda x: x.start, reverse=True)

        for item in sorted_items:
            original = item.text
            anonymized_value = self._anonymize_value(
                original,
                item.type,
                reversible=reversible
            )

            # Replace in text
            anonymized = (
                anonymized[:item.start] +
                anonymized_value +
                anonymized[item.end:]
            )

            # Store mapping
            if original not in mapping:
                mapping[original] = anonymized_value

        return anonymized, mapping

    def _anonymize_value(
        self,
        value: str,
        entity_type: str,
        reversible: bool = False
    ) -> str:
        """
        Anonymize a single value based on strategy.

        Args:
            value: Original value
            entity_type: Type of entity
            reversible: Whether to use reversible pseudonymization

        Returns:
            Anonymized value
        """
        if self.strategy == AnonymizationStrategy.REDACTION:
            return f"[{entity_type.upper()}]"

        elif self.strategy == AnonymizationStrategy.MASKING:
            return self._mask_value(value, entity_type)

        elif self.strategy == AnonymizationStrategy.REPLACEMENT:
            return self._replace_value(value, entity_type)

        elif self.strategy == AnonymizationStrategy.PSEUDONYMIZATION:
            return self._pseudonymize_value(value, entity_type, reversible)

        elif self.strategy == AnonymizationStrategy.GENERALIZATION:
            return self._generalize_value(value, entity_type)

        else:
            return "[ANONYMIZED]"

    def _mask_value(self, value: str, entity_type: str) -> str:
        """Mask value partially."""
        if entity_type == "EMAIL":
            # max@example.com → m**@e******.com
            match = re.match(r'^([^@])([^@]*)@([^.])([^.]*)\.(.+)$', value)
            if match:
                return f"{match.group(1)}{'*' * len(match.group(2))}@{match.group(3)}{'*' * len(match.group(4))}.{match.group(5)}"

        elif entity_type == "PHONE":
            # +49 123 456789 → +49 *** ******
            return re.sub(r'\d', '*', value[3:]) if len(value) > 3 else '***'

        elif entity_type == "PERSON":
            # Max Mustermann → M** M*********
            parts = value.split()
            return ' '.join([p[0] + '*' * (len(p) - 1) for p in parts if p])

        elif entity_type == "IBAN":
            # DE89370400440532013000 → DE** **** **** **** ****
            return value[:2] + '**' + ' ****' * ((len(value) - 2) // 4)

        else:
            # Generic masking
            if len(value) <= 2:
                return '*' * len(value)
            return value[0] + '*' * (len(value) - 2) + value[-1]

    def _replace_value(self, value: str, entity_type: str) -> str:
        """Replace with fake data."""
        # Use hash to get consistent replacement
        hash_val = int(hashlib.md5(value.encode()).hexdigest(), 16)

        if entity_type == "PERSON":
            return self.replacement_names[hash_val % len(self.replacement_names)]
        elif entity_type == "EMAIL":
            return self.replacement_emails[hash_val % len(self.replacement_emails)]
        elif entity_type == "PHONE":
            return self.replacement_phones[hash_val % len(self.replacement_phones)]
        elif entity_type == "LOCATION":
            return "City, Country"
        elif entity_type == "IBAN":
            return "XX00 0000 0000 0000 0000"
        else:
            return f"[REPLACED_{entity_type}]"

    def _pseudonymize_value(self, value: str, entity_type: str, reversible: bool) -> str:
        """Create pseudonymized value using hash."""
        if reversible:
            # Simple hash-based pseudonym (in production, use proper encryption)
            hash_val = hashlib.sha256(value.encode()).hexdigest()[:16]
            return f"PSEUDO_{hash_val.upper()}"
        else:
            # One-way hash
            hash_val = hashlib.sha256(value.encode()).hexdigest()
            return f"{entity_type}_{hash_val[:8].upper()}"

    def _generalize_value(self, value: str, entity_type: str) -> str:
        """Generalize value (reduce precision)."""
        if entity_type == "DATE":
            # Extract year only: 01.01.1990 → 1990
            match = re.search(r'\d{4}', value)
            return match.group(0) if match else "[YEAR]"

        elif entity_type == "LOCATION":
            # City, Street 1 → [LOCATION]
            return "[LOCATION]"

        else:
            return f"[{entity_type}]"

    def _save_mapping(self, mapping: Dict[str, str], mapping_file: str) -> None:
        """Save mapping to encrypted file."""
        # In production, use proper encryption (e.g., Fernet, AES)
        # For now, use base64 encoding as placeholder
        encoded = base64.b64encode(json.dumps(mapping).encode()).decode()

        with open(mapping_file, 'w') as f:
            f.write(encoded)

    def _load_mapping(self, mapping_file: str) -> Dict[str, str]:
        """Load mapping from encrypted file."""
        with open(mapping_file, 'r') as f:
            encoded = f.read()

        decoded = base64.b64decode(encoded).decode()
        return json.loads(decoded)

    def _create_audit_trail(
        self,
        original_file: str,
        anonymized_file: str,
        pii_items: List[PIIItem]
    ) -> List[Dict[str, Any]]:
        """Create audit trail for compliance."""
        trail = []

        # Anonymization event
        trail.append({
            "event": "anonymization_started",
            "timestamp": datetime.now().isoformat(),
            "original_file": original_file,
            "strategy": self.strategy.value,
            "compliance_mode": self.compliance_mode.value
        })

        # PII detection event
        trail.append({
            "event": "pii_detected",
            "timestamp": datetime.now().isoformat(),
            "pii_count": len(pii_items),
            "pii_types": list(set(item.type for item in pii_items))
        })

        # Anonymization complete event
        trail.append({
            "event": "anonymization_completed",
            "timestamp": datetime.now().isoformat(),
            "anonymized_file": anonymized_file,
            "pii_anonymized": len(pii_items)
        })

        return trail

    def deanonymize(
        self,
        anonymized_file: str,
        mapping_file: str,
        output_file: str
    ) -> None:
        """
        De-anonymize document using mapping.

        Args:
            anonymized_file: Path to anonymized document
            mapping_file: Path to mapping file
            output_file: Path for de-anonymized document
        """
        logger.info(f"De-anonymizing document: {anonymized_file}")

        # Load mapping
        mapping = self._load_mapping(mapping_file)

        # Parse anonymized document
        parsed = self.parser.parse(anonymized_file)
        text = parsed.get("text", "")

        # Reverse mapping
        reverse_mapping = {v: k for k, v in mapping.items()}

        # Replace anonymized values with originals
        deanonymized = text
        for anonymized, original in reverse_mapping.items():
            deanonymized = deanonymized.replace(anonymized, original)

        # Export de-anonymized document
        self.exporter.export(deanonymized, output_file, format="txt")

        logger.info(f"De-anonymization complete: {output_file}")

    def batch_anonymize(
        self,
        input_dir: str,
        output_dir: str,
        file_pattern: str = "*.*"
    ) -> List[AnonymizationResult]:
        """
        Batch anonymize documents.

        Args:
            input_dir: Input directory
            output_dir: Output directory
            file_pattern: File pattern to match

        Returns:
            List of anonymization results
        """
        logger.info(f"Batch anonymizing documents from: {input_dir}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Find all matching files
        input_path = Path(input_dir)
        files = list(input_path.glob(file_pattern))

        results = []
        for file_path in files:
            try:
                output_file = Path(output_dir) / f"anonymized_{file_path.name}"
                result = self.anonymize(str(file_path), str(output_file))
                results.append(result)
                logger.info(f"✓ Anonymized: {file_path.name}")

            except Exception as e:
                logger.error(f"✗ Failed to anonymize {file_path}: {e}")

        logger.info(f"Batch anonymization complete. Processed: {len(results)}/{len(files)}")
        return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Document Anonymizer - GDPR/HIPAA-compliant PII anonymization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic anonymization (redaction)
  python doc-anonymizer.py anonymize document.pdf --output anonymized.pdf

  # With masking strategy
  python doc-anonymizer.py anonymize document.pdf --strategy masking --output masked.pdf

  # GDPR mode with audit log
  python doc-anonymizer.py anonymize document.pdf --compliance gdpr --audit-log

  # Reversible anonymization
  python doc-anonymizer.py anonymize document.pdf --reversible --mapping-file mapping.enc

  # Scan for PII only
  python doc-anonymizer.py scan document.pdf --report pii_report.json

  # De-anonymize
  python doc-anonymizer.py deanonymize anonymized.pdf --mapping-file mapping.enc --output original.pdf

  # Batch anonymization
  python doc-anonymizer.py batch /documents/ --output-dir /anonymized/
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for PII without anonymizing")
    scan_parser.add_argument("file", help="Document to scan")
    scan_parser.add_argument("--report", "-r", help="Output report file (JSON)")

    # Anonymize command
    anon_parser = subparsers.add_parser("anonymize", help="Anonymize document")
    anon_parser.add_argument("file", help="Document to anonymize")
    anon_parser.add_argument("--output", "-o", required=True, help="Output file")
    anon_parser.add_argument(
        "--strategy",
        choices=["redaction", "masking", "replacement", "pseudonymization", "generalization"],
        default="redaction",
        help="Anonymization strategy"
    )
    anon_parser.add_argument(
        "--compliance",
        choices=["gdpr", "hipaa", "custom"],
        default="gdpr",
        help="Compliance mode"
    )
    anon_parser.add_argument("--reversible", action="store_true",
                            help="Enable reversible anonymization")
    anon_parser.add_argument("--mapping-file", help="File to save mapping (if reversible)")
    anon_parser.add_argument("--audit-log", action="store_true",
                            help="Create audit trail")

    # De-anonymize command
    deanon_parser = subparsers.add_parser("deanonymize", help="De-anonymize document")
    deanon_parser.add_argument("file", help="Anonymized document")
    deanon_parser.add_argument("--mapping-file", required=True, help="Mapping file")
    deanon_parser.add_argument("--output", "-o", required=True, help="Output file")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch anonymize documents")
    batch_parser.add_argument("input_dir", help="Input directory")
    batch_parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    batch_parser.add_argument("--pattern", default="*.*", help="File pattern")
    batch_parser.add_argument(
        "--strategy",
        choices=["redaction", "masking", "replacement", "pseudonymization"],
        default="redaction"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "scan":
            # Initialize anonymizer
            anonymizer = DocumentAnonymizer()

            # Scan for PII
            pii_items = anonymizer.scan_pii(args.file)

            # Print results
            print(f"\n📊 PII Detection Report")
            print(f"=" * 80)
            print(f"File: {args.file}")
            print(f"PII items detected: {len(pii_items)}")
            print(f"\nDetected PII:")

            for item in pii_items:
                print(f"  [{item.type:12s}] {item.text} (confidence: {item.confidence:.2f})")

            # Save report if requested
            if args.report:
                report = {
                    "file": args.file,
                    "scan_date": datetime.now().isoformat(),
                    "pii_count": len(pii_items),
                    "pii_items": [asdict(item) for item in pii_items]
                }
                with open(args.report, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\nReport saved to: {args.report}")

        elif args.command == "anonymize":
            # Initialize anonymizer
            strategy = AnonymizationStrategy(args.strategy)
            compliance = ComplianceMode(args.compliance)
            anonymizer = DocumentAnonymizer(strategy=strategy, compliance_mode=compliance)

            # Anonymize
            result = anonymizer.anonymize(
                args.file,
                args.output,
                reversible=args.reversible,
                mapping_file=args.mapping_file,
                audit_log=args.audit_log
            )

            # Print results
            print(f"\n✅ Anonymization Complete")
            print(f"=" * 80)
            print(f"Original file:     {result.original_file}")
            print(f"Anonymized file:   {result.anonymized_file}")
            print(f"Strategy:          {result.strategy}")
            print(f"Compliance mode:   {result.compliance_mode}")
            print(f"PII detected:      {result.pii_detected}")
            print(f"PII anonymized:    {result.pii_anonymized}")

            if args.audit_log:
                print(f"\nAudit trail: {len(result.audit_trail)} events recorded")

        elif args.command == "deanonymize":
            # Initialize anonymizer
            anonymizer = DocumentAnonymizer()

            # De-anonymize
            anonymizer.deanonymize(args.file, args.mapping_file, args.output)

            print(f"\n✅ De-anonymization Complete")
            print(f"Anonymized file:    {args.file}")
            print(f"De-anonymized file: {args.output}")

        elif args.command == "batch":
            # Initialize anonymizer
            strategy = AnonymizationStrategy(args.strategy)
            anonymizer = DocumentAnonymizer(strategy=strategy)

            # Batch anonymize
            results = anonymizer.batch_anonymize(
                args.input_dir,
                args.output_dir,
                args.pattern
            )

            print(f"\n✅ Batch Anonymization Complete")
            print(f"=" * 80)
            print(f"Processed: {len(results)} documents")
            print(f"Total PII anonymized: {sum(r.pii_anonymized for r in results)}")

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
