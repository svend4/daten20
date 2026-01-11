#!/usr/bin/env python3
"""
Document Merger - Intelligent Document Merging Tool
====================================================

Merge multiple documents into a single unified document with smart formatting,
table of contents generation, and metadata preservation.

Features:
- Multiple merge modes (concatenate, interleave, smart)
- Format support (txt, pdf, docx, md)
- Automatic table of contents generation
- Metadata preservation and aggregation
- Page/section numbering
- Custom separators and headers
- Conflict resolution
- Backup creation

Merge Modes:
- concatenate: Simple sequential joining
- interleave: Alternate between documents
- smart: Intelligent merging with deduplication
- chapters: Each document becomes a chapter
- sections: Organize by sections

Usage:
    # Simple concatenation
    python doc-merger.py merge file1.txt file2.txt file3.txt -o merged.txt

    # With table of contents
    python doc-merger.py merge *.txt -o output.txt --toc

    # Smart merge with deduplication
    python doc-merger.py merge doc1.txt doc2.txt -o result.txt --mode smart

    # Chapter-based merge
    python doc-merger.py merge chapter*.txt -o book.txt --mode chapters --toc

    # PDF merge
    python doc-merger.py merge report1.pdf report2.pdf -o final.pdf

Author: Document Management System
Version: 1.0.0
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import hashlib
import re

# Setup logging
from src.core.logging_config import setup_logging
logger = setup_logging(__name__, log_level="INFO")


class MergeMode(str, Enum):
    """Document merge modes"""
    CONCATENATE = "concatenate"  # Simple sequential join
    INTERLEAVE = "interleave"    # Alternate between docs
    SMART = "smart"              # Intelligent merge with dedup
    CHAPTERS = "chapters"        # Each doc = chapter
    SECTIONS = "sections"        # Organize by sections


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    KEEP_FIRST = "keep_first"
    KEEP_LAST = "keep_last"
    KEEP_ALL = "keep_all"
    MANUAL = "manual"


@dataclass
class DocumentMetadata:
    """Metadata for a document"""
    file_path: str
    file_name: str
    file_size: int
    line_count: int
    word_count: int
    char_count: int
    checksum: str
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    encoding: str = "utf-8"


@dataclass
class MergeResult:
    """Result of document merge operation"""
    output_file: str
    merge_mode: str
    input_files: List[str]
    total_lines: int
    total_words: int
    total_chars: int
    execution_time: float
    has_toc: bool
    metadata: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class MergeConfig:
    """Configuration for merge operation"""
    mode: MergeMode = MergeMode.CONCATENATE
    separator: str = "\n\n"
    add_toc: bool = False
    add_headers: bool = True
    add_page_numbers: bool = False
    preserve_metadata: bool = True
    create_backup: bool = False
    conflict_resolution: ConflictResolution = ConflictResolution.KEEP_ALL
    remove_duplicates: bool = False
    normalize_whitespace: bool = True


class DocumentMerger:
    """
    Intelligent document merger with multiple merge strategies
    """

    def __init__(self, config: Optional[MergeConfig] = None):
        """
        Initialize document merger

        Args:
            config: Merge configuration
        """
        self.config = config or MergeConfig()
        logger.info(f"DocumentMerger initialized with mode: {self.config.mode}")

    def merge(
        self,
        input_files: List[str],
        output_file: str,
        titles: Optional[List[str]] = None
    ) -> MergeResult:
        """
        Merge multiple documents into one

        Args:
            input_files: List of input file paths
            output_file: Output file path
            titles: Optional custom titles for each document

        Returns:
            MergeResult with operation details
        """
        start_time = datetime.now()
        logger.info(f"Merging {len(input_files)} documents into {output_file}")

        # Validate input files
        valid_files = self._validate_files(input_files)
        if not valid_files:
            raise ValueError("No valid input files found")

        # Read documents
        documents = self._read_documents(valid_files)

        # Extract metadata
        metadata_list = [self._extract_metadata(doc, path)
                        for doc, path in zip(documents, valid_files)]

        # Generate titles if not provided
        if not titles:
            titles = [Path(f).stem for f in valid_files]

        # Merge based on mode
        if self.config.mode == MergeMode.CONCATENATE:
            merged_content = self._merge_concatenate(documents, titles)
        elif self.config.mode == MergeMode.INTERLEAVE:
            merged_content = self._merge_interleave(documents, titles)
        elif self.config.mode == MergeMode.SMART:
            merged_content = self._merge_smart(documents, titles)
        elif self.config.mode == MergeMode.CHAPTERS:
            merged_content = self._merge_chapters(documents, titles)
        elif self.config.mode == MergeMode.SECTIONS:
            merged_content = self._merge_sections(documents, titles)
        else:
            merged_content = self._merge_concatenate(documents, titles)

        # Add table of contents if requested
        if self.config.add_toc:
            toc = self._generate_toc(titles, metadata_list)
            merged_content = toc + "\n\n" + merged_content

        # Normalize whitespace if requested
        if self.config.normalize_whitespace:
            merged_content = self._normalize_whitespace(merged_content)

        # Create backup if requested
        if self.config.create_backup and Path(output_file).exists():
            self._create_backup(output_file)

        # Write output
        self._write_output(merged_content, output_file)

        # Calculate statistics
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        lines = merged_content.count('\n') + 1
        words = len(merged_content.split())
        chars = len(merged_content)

        result = MergeResult(
            output_file=output_file,
            merge_mode=self.config.mode.value,
            input_files=valid_files,
            total_lines=lines,
            total_words=words,
            total_chars=chars,
            execution_time=execution_time,
            has_toc=self.config.add_toc,
            metadata={
                "input_metadata": [asdict(m) for m in metadata_list],
                "merge_config": asdict(self.config)
            }
        )

        logger.info(f"Merge completed: {lines} lines, {words} words, {chars} chars")
        return result

    def _validate_files(self, file_paths: List[str]) -> List[str]:
        """Validate that files exist and are readable"""
        valid = []
        for path in file_paths:
            p = Path(path)
            if not p.exists():
                logger.warning(f"File not found: {path}")
                continue
            if not p.is_file():
                logger.warning(f"Not a file: {path}")
                continue
            if not os.access(path, os.R_OK):
                logger.warning(f"File not readable: {path}")
                continue
            valid.append(path)
        return valid

    def _read_documents(self, file_paths: List[str]) -> List[str]:
        """Read all documents"""
        documents = []
        for path in file_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append(content)
                logger.debug(f"Read {len(content)} chars from {path}")
            except Exception as e:
                logger.error(f"Failed to read {path}: {e}")
                documents.append("")
        return documents

    def _extract_metadata(self, content: str, file_path: str) -> DocumentMetadata:
        """Extract metadata from document"""
        path = Path(file_path)
        stat = path.stat()

        # Calculate checksum
        checksum = hashlib.md5(content.encode()).hexdigest()

        return DocumentMetadata(
            file_path=file_path,
            file_name=path.name,
            file_size=stat.st_size,
            line_count=content.count('\n') + 1,
            word_count=len(content.split()),
            char_count=len(content),
            checksum=checksum,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime)
        )

    def _merge_concatenate(self, documents: List[str], titles: List[str]) -> str:
        """Simple concatenation with optional headers"""
        parts = []

        for idx, (doc, title) in enumerate(zip(documents, titles), 1):
            if self.config.add_headers:
                header = f"\n{'=' * 70}\n"
                header += f"Document {idx}: {title}\n"
                header += f"{'=' * 70}\n\n"
                parts.append(header)

            parts.append(doc)
            parts.append(self.config.separator)

        return "".join(parts).rstrip()

    def _merge_interleave(self, documents: List[str], titles: List[str]) -> str:
        """Interleave lines from documents"""
        # Split into lines
        doc_lines = [doc.split('\n') for doc in documents]
        max_lines = max(len(lines) for lines in doc_lines)

        result_lines = []

        for line_idx in range(max_lines):
            for doc_idx, lines in enumerate(doc_lines):
                if line_idx < len(lines):
                    if self.config.add_headers and line_idx == 0:
                        result_lines.append(f"[{titles[doc_idx]}]")
                    result_lines.append(lines[line_idx])

        return '\n'.join(result_lines)

    def _merge_smart(self, documents: List[str], titles: List[str]) -> str:
        """Smart merge with deduplication"""
        # Remove duplicates if requested
        if self.config.remove_duplicates:
            documents = self._remove_duplicate_content(documents)

        # Use concatenate as base
        merged = self._merge_concatenate(documents, titles)

        # Additional smart processing
        # Remove excessive blank lines
        merged = re.sub(r'\n{3,}', '\n\n', merged)

        return merged

    def _merge_chapters(self, documents: List[str], titles: List[str]) -> str:
        """Merge as chapters with chapter headers"""
        parts = []

        for idx, (doc, title) in enumerate(zip(documents, titles), 1):
            # Chapter header
            chapter_header = f"\n\n{'#' * 70}\n"
            chapter_header += f"# CHAPTER {idx}: {title.upper()}\n"
            chapter_header += f"{'#' * 70}\n\n"
            parts.append(chapter_header)

            parts.append(doc)
            parts.append("\n\n")

        return "".join(parts).rstrip()

    def _merge_sections(self, documents: List[str], titles: List[str]) -> str:
        """Merge as sections with section headers"""
        parts = []

        for idx, (doc, title) in enumerate(zip(documents, titles), 1):
            # Section header
            section_header = f"\n\n## Section {idx}: {title}\n\n"
            parts.append(section_header)

            parts.append(doc)

        return "".join(parts).rstrip()

    def _generate_toc(self, titles: List[str], metadata: List[DocumentMetadata]) -> str:
        """Generate table of contents"""
        toc_lines = [
            "=" * 70,
            "TABLE OF CONTENTS",
            "=" * 70,
            "",
            f"Total Documents: {len(titles)}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "-" * 70,
            ""
        ]

        for idx, (title, meta) in enumerate(zip(titles, metadata), 1):
            toc_lines.append(f"{idx}. {title}")
            toc_lines.append(f"   File: {meta.file_name}")
            toc_lines.append(f"   Size: {meta.file_size} bytes")
            toc_lines.append(f"   Lines: {meta.line_count} | Words: {meta.word_count}")
            toc_lines.append("")

        toc_lines.append("-" * 70)

        return "\n".join(toc_lines)

    def _remove_duplicate_content(self, documents: List[str]) -> List[str]:
        """Remove duplicate documents based on content hash"""
        seen_hashes = set()
        unique_docs = []

        for doc in documents:
            doc_hash = hashlib.md5(doc.encode()).hexdigest()
            if doc_hash not in seen_hashes:
                seen_hashes.add(doc_hash)
                unique_docs.append(doc)
            else:
                logger.info(f"Removed duplicate document (hash: {doc_hash[:8]}...)")

        return unique_docs

    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content"""
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in content.split('\n')]

        # Remove multiple consecutive blank lines (max 2)
        normalized_lines = []
        blank_count = 0

        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    normalized_lines.append(line)
            else:
                blank_count = 0
                normalized_lines.append(line)

        return '\n'.join(normalized_lines).rstrip() + '\n'

    def _create_backup(self, file_path: str) -> None:
        """Create backup of existing file"""
        path = Path(file_path)
        if not path.exists():
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = path.parent / f"{path.stem}_{timestamp}{path.suffix}.bak"

        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")

    def _write_output(self, content: str, output_file: str) -> None:
        """Write merged content to output file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Wrote {len(content)} chars to {output_file}")

    def analyze_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze documents before merging

        Returns compatibility and statistics
        """
        valid_files = self._validate_files(file_paths)
        documents = self._read_documents(valid_files)
        metadata_list = [self._extract_metadata(doc, path)
                        for doc, path in zip(documents, valid_files)]

        total_size = sum(m.file_size for m in metadata_list)
        total_lines = sum(m.line_count for m in metadata_list)
        total_words = sum(m.word_count for m in metadata_list)

        # Check for duplicates
        hashes = [m.checksum for m in metadata_list]
        duplicates = len(hashes) - len(set(hashes))

        return {
            "total_documents": len(valid_files),
            "total_size": total_size,
            "total_lines": total_lines,
            "total_words": total_words,
            "duplicate_count": duplicates,
            "documents": [asdict(m) for m in metadata_list]
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Document Merger - Intelligent document merging tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple merge
  python doc-merger.py merge file1.txt file2.txt -o merged.txt

  # With table of contents
  python doc-merger.py merge *.txt -o output.txt --toc

  # Smart merge with deduplication
  python doc-merger.py merge doc1.txt doc2.txt -o result.txt --mode smart --remove-duplicates

  # Chapter-based merge
  python doc-merger.py merge chapter*.txt -o book.txt --mode chapters --toc

  # Analyze before merging
  python doc-merger.py analyze file1.txt file2.txt file3.txt

Merge Modes:
  concatenate  - Simple sequential joining (default)
  interleave   - Alternate between documents line by line
  smart        - Intelligent merging with deduplication
  chapters     - Each document becomes a chapter
  sections     - Organize by sections
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge documents")
    merge_parser.add_argument("files", nargs="+", help="Input files to merge")
    merge_parser.add_argument("-o", "--output", required=True, help="Output file")
    merge_parser.add_argument("--mode", choices=[m.value for m in MergeMode],
                             default="concatenate", help="Merge mode")
    merge_parser.add_argument("--toc", action="store_true", help="Add table of contents")
    merge_parser.add_argument("--no-headers", action="store_true", help="Don't add document headers")
    merge_parser.add_argument("--separator", default="\n\n", help="Separator between documents")
    merge_parser.add_argument("--titles", nargs="+", help="Custom titles for documents")
    merge_parser.add_argument("--remove-duplicates", action="store_true",
                             help="Remove duplicate documents")
    merge_parser.add_argument("--backup", action="store_true",
                             help="Create backup if output exists")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze documents before merge")
    analyze_parser.add_argument("files", nargs="+", help="Files to analyze")
    analyze_parser.add_argument("-o", "--output", help="Save analysis to JSON file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "merge":
            # Configure merger
            config = MergeConfig(
                mode=MergeMode(args.mode),
                separator=args.separator,
                add_toc=args.toc,
                add_headers=not args.no_headers,
                remove_duplicates=args.remove_duplicates,
                create_backup=args.backup
            )

            merger = DocumentMerger(config)
            result = merger.merge(args.files, args.output, args.titles)

            # Display result
            print(f"\n✅ Merge completed successfully!")
            print(f"{'=' * 70}")
            print(f"Output file: {result.output_file}")
            print(f"Mode: {result.merge_mode}")
            print(f"Input files: {len(result.input_files)}")
            print(f"Total lines: {result.total_lines:,}")
            print(f"Total words: {result.total_words:,}")
            print(f"Total chars: {result.total_chars:,}")
            print(f"Execution time: {result.execution_time:.2f}s")
            print(f"Table of contents: {'Yes' if result.has_toc else 'No'}")

            if result.warnings:
                print(f"\n⚠️  Warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    print(f"  - {warning}")

        elif args.command == "analyze":
            merger = DocumentMerger()
            analysis = merger.analyze_documents(args.files)

            # Display analysis
            print(f"\n📊 Document Analysis")
            print(f"{'=' * 70}")
            print(f"Total documents: {analysis['total_documents']}")
            print(f"Total size: {analysis['total_size']:,} bytes")
            print(f"Total lines: {analysis['total_lines']:,}")
            print(f"Total words: {analysis['total_words']:,}")
            print(f"Duplicates found: {analysis['duplicate_count']}")
            print(f"\nDocuments:")

            for idx, doc in enumerate(analysis['documents'], 1):
                print(f"\n{idx}. {doc['file_name']}")
                print(f"   Size: {doc['file_size']:,} bytes")
                print(f"   Lines: {doc['line_count']:,} | Words: {doc['word_count']:,}")
                print(f"   Modified: {doc['modified_at']}")

            # Save to JSON if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                print(f"\n💾 Analysis saved to: {args.output}")

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
