#!/usr/bin/env python3
"""
Document Processor CLI
======================

Comprehensive command-line tool for document processing with AI/ML capabilities.

Features:
- Text extraction and parsing
- Named Entity Recognition (NER) with spaCy
- Document classification (TF-IDF + SVM)
- Topic modeling and auto-tagging (LDA)
- Relation extraction and knowledge graphs
- Batch processing
- Multiple export formats (JSON, CSV, PDF, Excel)
- Integration with database

Usage:
    # Process single document
    python doc-processor.py process document.pdf --output results.json

    # Extract entities
    python doc-processor.py ner document.pdf --entities PERSON,ORG,LOCATION

    # Classify document
    python doc-processor.py classify document.pdf

    # Extract relations and build knowledge graph
    python doc-processor.py relations document.pdf --graph output.json

    # Batch process directory
    python doc-processor.py batch /path/to/documents/ --output-dir results/

    # Full analysis pipeline
    python doc-processor.py analyze document.pdf --full --export excel

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Import core modules
from src.core.parser import DocumentParser
from src.core.validator import DocumentValidator
from src.core.database import DocumentDatabase
from src.core.exporter import DocumentExporter
from src.core.excel_export import ExcelExporter
from src.core.pdf_exporter import PDFReportExporter
from src.core.logging_config import setup_logging

# Import ML modules
from src.ml.ner import NEREngine, EntityType
from src.ml.classifier import TfidfSVMClassifier, DocumentCategory
from src.ml.tagging import TopicModeler
from src.ml.relation_extractor import RelationExtractor, RelationType
from src.ml.knowledge_graph import KnowledgeGraphBuilder, GraphFormat

# Setup logging
logger = setup_logging(__name__, log_level="INFO")


class DocumentProcessorCLI:
    """Main CLI application for document processing."""

    def __init__(self, db_path: str = "data/documents.db"):
        """Initialize document processor with all components."""
        self.parser = DocumentParser()
        self.validator = DocumentValidator()
        self.database = DocumentDatabase(db_path)
        self.exporter = DocumentExporter()
        self.excel_exporter = ExcelExporter()
        self.pdf_exporter = PDFReportExporter()

        # ML components
        self.ner_engine = NEREngine(use_spacy=True)
        self.classifier = TfidfSVMClassifier()
        self.topic_modeler = TopicModeler(num_topics=10)
        self.relation_extractor = RelationExtractor(use_spacy=True)
        self.graph_builder = KnowledgeGraphBuilder(use_spacy=True)

        logger.info("DocumentProcessorCLI initialized successfully")

    def process_document(self, file_path: str, output: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a single document with full analysis pipeline.

        Args:
            file_path: Path to document file
            output: Optional output file path

        Returns:
            Processing results dictionary
        """
        logger.info(f"Processing document: {file_path}")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")
        metadata = parsed.get("metadata", {})

        # Validate
        validation = self.validator.validate(text, metadata)

        # Extract entities
        entities = self.ner_engine.extract_entities(text)

        # Classify document
        classification = self.classifier.predict(text)

        # Extract topics
        topics = self.topic_modeler.get_document_topics(text)

        # Extract relations
        relations = self.relation_extractor.extract_relations(text)

        # Build results
        results = {
            "file_path": file_path,
            "processed_at": datetime.now().isoformat(),
            "validation": {
                "is_valid": validation.is_valid,
                "errors": validation.errors,
                "warnings": validation.warnings
            },
            "metadata": metadata,
            "statistics": {
                "text_length": len(text),
                "word_count": len(text.split()),
                "entity_count": len(entities),
                "relation_count": len(relations)
            },
            "classification": {
                "category": classification.category.value if hasattr(classification, 'category') else "UNKNOWN",
                "confidence": getattr(classification, 'confidence', 0.0)
            },
            "entities": [
                {
                    "text": e.text,
                    "type": e.type.value,
                    "confidence": e.confidence
                }
                for e in entities
            ],
            "topics": [
                {
                    "tag": t.tag,
                    "score": t.score,
                    "keywords": t.keywords[:5]
                }
                for t in topics[:5]
            ],
            "relations": [
                {
                    "source": r.source_entity,
                    "relation": r.relation_type.value,
                    "target": r.target_entity,
                    "confidence": r.confidence
                }
                for r in relations
            ]
        }

        # Save to output if specified
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output}")

        return results

    def extract_entities(
        self,
        file_path: str,
        entity_types: Optional[List[str]] = None,
        output: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract named entities from document.

        Args:
            file_path: Path to document
            entity_types: Filter by entity types (e.g., ['PERSON', 'ORG'])
            output: Optional output file path

        Returns:
            List of extracted entities
        """
        logger.info(f"Extracting entities from: {file_path}")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")

        # Extract entities
        if entity_types:
            # Filter by specific types
            entities = []
            for entity_type_str in entity_types:
                try:
                    entity_type = EntityType[entity_type_str.upper()]
                    entities.extend(self.ner_engine.extract_by_type(text, entity_type))
                except KeyError:
                    logger.warning(f"Unknown entity type: {entity_type_str}")
        else:
            entities = self.ner_engine.extract_entities(text)

        # Build results
        results = [
            {
                "text": e.text,
                "type": e.type.value,
                "start": e.start,
                "end": e.end,
                "confidence": e.confidence
            }
            for e in entities
        ]

        # Save to output if specified
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Entities saved to: {output}")

        return results

    def classify_document(self, file_path: str) -> Dict[str, Any]:
        """
        Classify document into categories.

        Args:
            file_path: Path to document

        Returns:
            Classification result
        """
        logger.info(f"Classifying document: {file_path}")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")

        # Classify
        classification = self.classifier.predict(text)

        result = {
            "file_path": file_path,
            "category": classification.category.value if hasattr(classification, 'category') else "UNKNOWN",
            "confidence": getattr(classification, 'confidence', 0.0),
            "probabilities": getattr(classification, 'probabilities', {})
        }

        return result

    def extract_relations(
        self,
        file_path: str,
        build_graph: bool = False,
        graph_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract relations and optionally build knowledge graph.

        Args:
            file_path: Path to document
            build_graph: Whether to build knowledge graph
            graph_output: Path to save graph (JSON format)

        Returns:
            Relations and optional graph data
        """
        logger.info(f"Extracting relations from: {file_path}")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")

        # Extract relations
        relations = self.relation_extractor.extract_relations(text)

        results = {
            "file_path": file_path,
            "relation_count": len(relations),
            "relations": [
                {
                    "source": r.source_entity,
                    "source_type": r.source_type.value,
                    "relation": r.relation_type.value,
                    "target": r.target_entity,
                    "target_type": r.target_type.value,
                    "confidence": r.confidence
                }
                for r in relations
            ]
        }

        # Build knowledge graph if requested
        if build_graph:
            graph = self.graph_builder.build_from_text(text)
            graph_data = json.loads(graph.export(GraphFormat.JSON))
            results["knowledge_graph"] = graph_data
            results["graph_statistics"] = graph.stats()

            # Save graph if output specified
            if graph_output:
                with open(graph_output, 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Knowledge graph saved to: {graph_output}")

        return results

    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        file_pattern: str = "*.*"
    ) -> Dict[str, Any]:
        """
        Process multiple documents in batch.

        Args:
            input_dir: Input directory containing documents
            output_dir: Output directory for results
            file_pattern: File pattern to match (e.g., "*.pdf")

        Returns:
            Batch processing summary
        """
        logger.info(f"Batch processing documents from: {input_dir}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Find all matching files
        input_path = Path(input_dir)
        files = list(input_path.glob(file_pattern))

        results = {
            "processed_at": datetime.now().isoformat(),
            "input_dir": input_dir,
            "output_dir": output_dir,
            "total_files": len(files),
            "processed": 0,
            "failed": 0,
            "files": []
        }

        # Process each file
        for file_path in files:
            try:
                output_file = Path(output_dir) / f"{file_path.stem}_results.json"
                file_results = self.process_document(str(file_path), str(output_file))

                results["files"].append({
                    "file": str(file_path),
                    "status": "success",
                    "output": str(output_file)
                })
                results["processed"] += 1

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results["files"].append({
                    "file": str(file_path),
                    "status": "failed",
                    "error": str(e)
                })
                results["failed"] += 1

        # Save summary
        summary_file = Path(output_dir) / "batch_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Batch processing complete. Processed: {results['processed']}, Failed: {results['failed']}")

        return results

    def full_analysis(
        self,
        file_path: str,
        export_format: str = "json",
        output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run full document analysis with all features.

        Args:
            file_path: Path to document
            export_format: Export format (json, excel, pdf)
            output: Output file path

        Returns:
            Complete analysis results
        """
        logger.info(f"Running full analysis on: {file_path}")

        # Run full processing
        results = self.process_document(file_path)

        # Add knowledge graph
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")
        graph = self.graph_builder.build_from_text(text)
        results["knowledge_graph"] = json.loads(graph.export(GraphFormat.JSON))
        results["graph_statistics"] = graph.stats()

        # Export in requested format
        if output:
            if export_format == "json":
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)

            elif export_format == "excel":
                # Create Excel workbook with multiple sheets
                self.excel_exporter.export_analysis(results, output)

            elif export_format == "pdf":
                # Create PDF report
                self.pdf_exporter.export_analysis(results, output)

            logger.info(f"Analysis exported to: {output}")

        return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Document Processor CLI - AI-powered document analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single document
  python doc-processor.py process document.pdf --output results.json

  # Extract entities
  python doc-processor.py ner document.pdf --entities PERSON ORG LOCATION

  # Classify document
  python doc-processor.py classify document.pdf

  # Extract relations and build knowledge graph
  python doc-processor.py relations document.pdf --graph output.json

  # Batch process directory
  python doc-processor.py batch /path/to/documents/ --output-dir results/

  # Full analysis with Excel export
  python doc-processor.py analyze document.pdf --full --export excel --output report.xlsx
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process single document")
    process_parser.add_argument("file", help="Path to document file")
    process_parser.add_argument("-o", "--output", help="Output file path (JSON)")

    # NER command
    ner_parser = subparsers.add_parser("ner", help="Extract named entities")
    ner_parser.add_argument("file", help="Path to document file")
    ner_parser.add_argument("-e", "--entities", nargs="+", help="Entity types to extract")
    ner_parser.add_argument("-o", "--output", help="Output file path (JSON)")

    # Classify command
    classify_parser = subparsers.add_parser("classify", help="Classify document")
    classify_parser.add_argument("file", help="Path to document file")

    # Relations command
    relations_parser = subparsers.add_parser("relations", help="Extract relations")
    relations_parser.add_argument("file", help="Path to document file")
    relations_parser.add_argument("-g", "--graph", help="Build and save knowledge graph")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch process documents")
    batch_parser.add_argument("input_dir", help="Input directory")
    batch_parser.add_argument("-o", "--output-dir", required=True, help="Output directory")
    batch_parser.add_argument("-p", "--pattern", default="*.*", help="File pattern")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Full document analysis")
    analyze_parser.add_argument("file", help="Path to document file")
    analyze_parser.add_argument("--full", action="store_true", help="Include knowledge graph")
    analyze_parser.add_argument("--export", choices=["json", "excel", "pdf"], default="json")
    analyze_parser.add_argument("-o", "--output", help="Output file path")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = DocumentProcessorCLI()

    # Execute command
    try:
        if args.command == "process":
            results = cli.process_document(args.file, args.output)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "ner":
            results = cli.extract_entities(args.file, args.entities, args.output)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "classify":
            results = cli.classify_document(args.file)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "relations":
            results = cli.extract_relations(
                args.file,
                build_graph=bool(args.graph),
                graph_output=args.graph
            )
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "batch":
            results = cli.batch_process(args.input_dir, args.output_dir, args.pattern)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "analyze":
            results = cli.full_analysis(args.file, args.export, args.output)
            if not args.output:
                print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
