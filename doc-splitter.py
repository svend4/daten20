#!/usr/bin/env python3
"""
Document Splitter - Intelligent Document Splitting Tool
========================================================

Split large documents into smaller, manageable parts with smart boundary
detection, context preservation, and metadata tracking.

Features:
- Multiple split modes (size, delimiter, chapter, section, smart)
- Smart boundary detection (preserve paragraphs, sentences)
- Context preservation across splits
- Automatic file naming and numbering
- Metadata generation for each part
- Preview mode before splitting
- Various output formats

Split Modes:
- size: Split by lines, words, or characters
- delimiter: Split by custom patterns or regex
- chapter: Split by chapter markers
- section: Split by section headers
- page: Split by page markers
- smart: Intelligent splitting with context preservation

Usage:
    # Split by number of lines
    python doc-splitter.py split large_doc.txt -o parts/ --mode size --lines 100

    # Split by chapters
    python doc-splitter.py split book.txt -o chapters/ --mode chapter

    # Split by custom delimiter
    python doc-splitter.py split data.txt -o output/ --mode delimiter --pattern "---"

    # Smart split with context preservation
    python doc-splitter.py split document.txt -o parts/ --mode smart --max-size 1000

    # Preview split without creating files
    python doc-splitter.py preview large_doc.txt --mode size --lines 50

Author: Document Management System
Version: 1.0.0
"""

import argparse
import hashlib
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

# Setup logging
from src.core.logging_config import setup_logging

logger = setup_logging(__name__, log_level="INFO")


class SplitMode(str, Enum):
    """Document split modes"""

    SIZE = "size"  # Split by size (lines/words/chars)
    DELIMITER = "delimiter"  # Split by custom delimiter
    CHAPTER = "chapter"  # Split by chapter markers
    SECTION = "section"  # Split by section headers
    PAGE = "page"  # Split by page markers
    SMART = "smart"  # Intelligent splitting


class SizeUnit(str, Enum):
    """Size units for splitting"""

    LINES = "lines"
    WORDS = "words"
    CHARS = "chars"


@dataclass
class DocumentPart:
    """A part of a split document"""

    part_number: int
    content: str
    line_count: int
    word_count: int
    char_count: int
    start_line: int
    end_line: int
    file_name: str
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SplitResult:
    """Result of document split operation"""

    input_file: str
    output_dir: str
    split_mode: str
    total_parts: int
    parts: List[DocumentPart]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SplitConfig:
    """Configuration for split operation"""

    mode: SplitMode = SplitMode.SIZE
    size_unit: SizeUnit = SizeUnit.LINES
    size_value: int = 100
    delimiter: str = "\n\n"
    pattern: Optional[str] = None
    preserve_context: bool = True
    numbered_output: bool = True
    prefix: str = "part"
    extension: str = ".txt"
    create_index: bool = True


class DocumentSplitter:
    """
    Intelligent document splitter with multiple split strategies
    """

    def __init__(self, config: Optional[SplitConfig] = None):
        """
        Initialize document splitter

        Args:
            config: Split configuration
        """
        self.config = config or SplitConfig()
        logger.info(f"DocumentSplitter initialized with mode: {self.config.mode}")

    def split(self, input_file: str, output_dir: str, preview: bool = False) -> SplitResult:
        """
        Split document into parts

        Args:
            input_file: Input file path
            output_dir: Output directory for parts
            preview: If True, don't write files (preview only)

        Returns:
            SplitResult with operation details
        """
        start_time = datetime.now()
        logger.info(f"Splitting {input_file} into {output_dir}")

        # Read document
        content = self._read_document(input_file)

        # Split based on mode
        if self.config.mode == SplitMode.SIZE:
            parts = self._split_by_size(content)
        elif self.config.mode == SplitMode.DELIMITER:
            parts = self._split_by_delimiter(content)
        elif self.config.mode == SplitMode.CHAPTER:
            parts = self._split_by_chapter(content)
        elif self.config.mode == SplitMode.SECTION:
            parts = self._split_by_section(content)
        elif self.config.mode == SplitMode.PAGE:
            parts = self._split_by_page(content)
        elif self.config.mode == SplitMode.SMART:
            parts = self._split_smart(content)
        else:
            parts = self._split_by_size(content)

        # Generate file names
        parts_with_names = self._generate_file_names(parts)

        # Write parts to files (unless preview)
        if not preview:
            self._write_parts(parts_with_names, output_dir)

            # Create index file if requested
            if self.config.create_index:
                self._create_index(parts_with_names, output_dir, input_file)

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        result = SplitResult(
            input_file=input_file,
            output_dir=output_dir if not preview else "(preview)",
            split_mode=self.config.mode.value,
            total_parts=len(parts_with_names),
            parts=parts_with_names,
            execution_time=execution_time,
            metadata={"split_config": asdict(self.config), "preview": preview},
        )

        logger.info(f"Split completed: {len(parts_with_names)} parts created")
        return result

    def _read_document(self, file_path: str) -> str:
        """Read document content"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Read {len(content)} chars from {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            raise

    def _split_by_size(self, content: str) -> List[DocumentPart]:
        """Split by size (lines, words, or chars)"""
        parts = []

        if self.config.size_unit == SizeUnit.LINES:
            lines = content.split("\n")
            chunk_size = self.config.size_value

            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i : i + chunk_size]
                chunk_content = "\n".join(chunk_lines)

                part = self._create_part(
                    part_number=len(parts) + 1,
                    content=chunk_content,
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                )
                parts.append(part)

        elif self.config.size_unit == SizeUnit.WORDS:
            words = content.split()
            chunk_size = self.config.size_value

            for i in range(0, len(words), chunk_size):
                chunk_words = words[i : i + chunk_size]
                chunk_content = " ".join(chunk_words)

                part = self._create_part(
                    part_number=len(parts) + 1,
                    content=chunk_content,
                    start_line=0,  # Not applicable for word-based split
                    end_line=0,
                )
                parts.append(part)

        elif self.config.size_unit == SizeUnit.CHARS:
            chunk_size = self.config.size_value

            for i in range(0, len(content), chunk_size):
                chunk_content = content[i : i + chunk_size]

                part = self._create_part(part_number=len(parts) + 1, content=chunk_content, start_line=0, end_line=0)
                parts.append(part)

        return parts

    def _split_by_delimiter(self, content: str) -> List[DocumentPart]:
        """Split by custom delimiter or pattern"""
        if self.config.pattern:
            # Use regex pattern
            pattern = re.compile(self.config.pattern)
            chunks = pattern.split(content)
        else:
            # Use simple delimiter
            chunks = content.split(self.config.delimiter)

        parts = []
        current_line = 1

        for idx, chunk in enumerate(chunks, 1):
            if not chunk.strip():  # Skip empty chunks
                continue

            lines_in_chunk = chunk.count("\n") + 1

            part = self._create_part(
                part_number=len(parts) + 1,
                content=chunk,
                start_line=current_line,
                end_line=current_line + lines_in_chunk - 1,
            )
            parts.append(part)

            current_line += lines_in_chunk

        return parts

    def _split_by_chapter(self, content: str) -> List[DocumentPart]:
        """Split by chapter markers"""
        # Common chapter patterns
        chapter_patterns = [r"^CHAPTER\s+\d+", r"^Chapter\s+\d+", r"^# CHAPTER", r"^#{1,2}\s+\d+\.", r"^\d+\.\s+[A-Z]"]

        # Find chapter boundaries
        lines = content.split("\n")
        chapter_starts = []

        for idx, line in enumerate(lines):
            for pattern in chapter_patterns:
                if re.match(pattern, line.strip()):
                    chapter_starts.append(idx)
                    break

        # If no chapters found, return whole document
        if not chapter_starts:
            logger.warning("No chapter markers found, returning whole document")
            part = self._create_part(1, content, 1, len(lines))
            return [part]

        # Split into chapters
        parts = []
        chapter_starts.append(len(lines))  # Add end marker

        for idx in range(len(chapter_starts) - 1):
            start = chapter_starts[idx]
            end = chapter_starts[idx + 1]

            chapter_lines = lines[start:end]
            chapter_content = "\n".join(chapter_lines)

            part = self._create_part(
                part_number=len(parts) + 1, content=chapter_content, start_line=start + 1, end_line=end
            )
            part.metadata["chapter_title"] = chapter_lines[0].strip()
            parts.append(part)

        return parts

    def _split_by_section(self, content: str) -> List[DocumentPart]:
        """Split by section headers (markdown-style)"""
        # Section patterns (## or ###)
        section_pattern = re.compile(r"^#{2,3}\s+.+$", re.MULTILINE)

        lines = content.split("\n")
        section_starts = []

        for idx, line in enumerate(lines):
            if section_pattern.match(line.strip()):
                section_starts.append(idx)

        if not section_starts:
            logger.warning("No section markers found")
            part = self._create_part(1, content, 1, len(lines))
            return [part]

        parts = []
        section_starts.append(len(lines))

        for idx in range(len(section_starts) - 1):
            start = section_starts[idx]
            end = section_starts[idx + 1]

            section_lines = lines[start:end]
            section_content = "\n".join(section_lines)

            part = self._create_part(
                part_number=len(parts) + 1, content=section_content, start_line=start + 1, end_line=end
            )
            part.metadata["section_title"] = section_lines[0].strip()
            parts.append(part)

        return parts

    def _split_by_page(self, content: str) -> List[DocumentPart]:
        """Split by page markers (\\f or custom)"""
        # Form feed character or custom page marker
        page_marker = "\f"
        pages = content.split(page_marker)

        parts = []
        current_line = 1

        for idx, page in enumerate(pages, 1):
            if not page.strip():
                continue

            lines_in_page = page.count("\n") + 1

            part = self._create_part(
                part_number=len(parts) + 1,
                content=page,
                start_line=current_line,
                end_line=current_line + lines_in_page - 1,
            )
            part.metadata["page_number"] = idx
            parts.append(part)

            current_line += lines_in_page

        return parts

    def _split_smart(self, content: str) -> List[DocumentPart]:
        """Intelligent splitting with context preservation"""
        lines = content.split("\n")
        max_size = self.config.size_value
        parts = []

        current_chunk = []
        current_size = 0
        current_start_line = 1

        for idx, line in enumerate(lines, 1):
            line_length = len(line)

            # Check if adding this line exceeds max size
            if current_size + line_length > max_size and current_chunk:
                # Try to find a good break point (empty line)
                if not line.strip() or self._is_paragraph_boundary(line):
                    # Good break point found
                    chunk_content = "\n".join(current_chunk)
                    part = self._create_part(
                        part_number=len(parts) + 1,
                        content=chunk_content,
                        start_line=current_start_line,
                        end_line=idx - 1,
                    )
                    parts.append(part)

                    current_chunk = []
                    current_size = 0
                    current_start_line = idx

            current_chunk.append(line)
            current_size += line_length

        # Add remaining chunk
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            part = self._create_part(
                part_number=len(parts) + 1, content=chunk_content, start_line=current_start_line, end_line=len(lines)
            )
            parts.append(part)

        return parts

    def _is_paragraph_boundary(self, line: str) -> bool:
        """Check if line is a paragraph boundary"""
        # Empty line or line starting with common paragraph markers
        if not line.strip():
            return True

        # Check for common section/chapter markers
        markers = [r"^#", r"^\d+\.", r"^CHAPTER", r"^Section", r"^\*\*"]
        for marker in markers:
            if re.match(marker, line.strip()):
                return True

        return False

    def _create_part(self, part_number: int, content: str, start_line: int, end_line: int) -> DocumentPart:
        """Create DocumentPart with statistics"""
        checksum = hashlib.md5(content.encode()).hexdigest()

        return DocumentPart(
            part_number=part_number,
            content=content,
            line_count=content.count("\n") + 1,
            word_count=len(content.split()),
            char_count=len(content),
            start_line=start_line,
            end_line=end_line,
            file_name="",  # Will be set later
            checksum=checksum,
        )

    def _generate_file_names(self, parts: List[DocumentPart]) -> List[DocumentPart]:
        """Generate file names for parts"""
        num_digits = len(str(len(parts)))

        for part in parts:
            if self.config.numbered_output:
                number_str = str(part.part_number).zfill(num_digits)
                part.file_name = f"{self.config.prefix}_{number_str}{self.config.extension}"
            else:
                part.file_name = f"{self.config.prefix}_{part.part_number}{self.config.extension}"

        return parts

    def _write_parts(self, parts: List[DocumentPart], output_dir: str) -> None:
        """Write parts to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for part in parts:
            file_path = output_path / part.file_name

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(part.content)

            logger.debug(f"Wrote part {part.part_number} to {file_path}")

    def _create_index(self, parts: List[DocumentPart], output_dir: str, input_file: str) -> None:
        """Create index file with metadata"""
        index_path = Path(output_dir) / "index.txt"

        index_lines = [
            "=" * 70,
            "DOCUMENT SPLIT INDEX",
            "=" * 70,
            "",
            f"Source File: {input_file}",
            f"Split Mode: {self.config.mode.value}",
            f"Total Parts: {len(parts)}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "-" * 70,
            "",
        ]

        for part in parts:
            index_lines.append(f"Part {part.part_number}: {part.file_name}")
            index_lines.append(f"  Lines: {part.start_line}-{part.end_line} ({part.line_count} lines)")
            index_lines.append(f"  Words: {part.word_count} | Chars: {part.char_count}")
            index_lines.append(f"  Checksum: {part.checksum}")

            if part.metadata:
                for key, value in part.metadata.items():
                    index_lines.append(f"  {key.title()}: {value}")

            index_lines.append("")

        index_lines.append("-" * 70)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines))

        logger.info(f"Created index file: {index_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Document Splitter - Intelligent document splitting tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split by lines
  python doc-splitter.py split large_doc.txt -o parts/ --lines 100

  # Split by chapters
  python doc-splitter.py split book.txt -o chapters/ --mode chapter

  # Split by delimiter
  python doc-splitter.py split data.txt -o output/ --mode delimiter --pattern "---"

  # Smart split
  python doc-splitter.py split document.txt -o parts/ --mode smart --max-size 1000

  # Preview without writing
  python doc-splitter.py preview large_doc.txt --lines 50

Split Modes:
  size       - Split by lines, words, or characters
  delimiter  - Split by custom delimiter or regex pattern
  chapter    - Split by chapter markers
  section    - Split by section headers (##, ###)
  page       - Split by page markers (\\f)
  smart      - Intelligent splitting with context preservation
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Split command
    split_parser = subparsers.add_parser("split", help="Split document")
    split_parser.add_argument("file", help="Input file to split")
    split_parser.add_argument("-o", "--output", required=True, help="Output directory")
    split_parser.add_argument("--mode", choices=[m.value for m in SplitMode], default="size", help="Split mode")
    split_parser.add_argument("--lines", type=int, default=100, help="Lines per part (size mode)")
    split_parser.add_argument("--words", type=int, help="Words per part (size mode)")
    split_parser.add_argument("--chars", type=int, help="Characters per part (size mode)")
    split_parser.add_argument("--max-size", type=int, help="Max size for smart mode")
    split_parser.add_argument("--delimiter", help="Delimiter for delimiter mode")
    split_parser.add_argument("--pattern", help="Regex pattern for delimiter mode")
    split_parser.add_argument("--prefix", default="part", help="Output file prefix")
    split_parser.add_argument("--no-index", action="store_true", help="Don't create index file")

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview split without writing")
    preview_parser.add_argument("file", help="Input file")
    preview_parser.add_argument("--mode", choices=[m.value for m in SplitMode], default="size", help="Split mode")
    preview_parser.add_argument("--lines", type=int, default=100, help="Lines per part")
    preview_parser.add_argument("--pattern", help="Regex pattern for delimiter mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Configure splitter
        config = SplitConfig(
            mode=SplitMode(args.mode),
            prefix=getattr(args, "prefix", "part"),
            create_index=not getattr(args, "no_index", False),
        )

        # Set size parameters
        if args.mode == "size":
            if getattr(args, "words", None):
                config.size_unit = SizeUnit.WORDS
                config.size_value = args.words
            elif getattr(args, "chars", None):
                config.size_unit = SizeUnit.CHARS
                config.size_value = args.chars
            else:
                config.size_unit = SizeUnit.LINES
                config.size_value = getattr(args, "lines", 100)

        if args.mode == "smart" and getattr(args, "max_size", None):
            config.size_value = args.max_size

        if args.mode == "delimiter":
            if getattr(args, "pattern", None):
                config.pattern = args.pattern
            elif getattr(args, "delimiter", None):
                config.delimiter = args.delimiter

        splitter = DocumentSplitter(config)

        if args.command == "split":
            result = splitter.split(args.file, args.output, preview=False)

            # Display result
            print(f"\n✅ Split completed successfully!")
            print(f"{'=' * 70}")
            print(f"Input file: {result.input_file}")
            print(f"Output dir: {result.output_dir}")
            print(f"Split mode: {result.split_mode}")
            print(f"Total parts: {result.total_parts}")
            print(f"Execution time: {result.execution_time:.2f}s")
            print(f"\nParts created:")

            for part in result.parts[:10]:  # Show first 10
                print(f"  {part.file_name}: {part.line_count} lines, {part.word_count} words")

            if len(result.parts) > 10:
                print(f"  ... and {len(result.parts) - 10} more")

        elif args.command == "preview":
            result = splitter.split(args.file, "(preview)", preview=True)

            # Display preview
            print(f"\n📋 Split Preview")
            print(f"{'=' * 70}")
            print(f"File: {result.input_file}")
            print(f"Mode: {result.split_mode}")
            print(f"Would create: {result.total_parts} parts")
            print(f"\nPart details:")

            for part in result.parts:
                print(f"\nPart {part.part_number}:")
                print(f"  Lines: {part.start_line}-{part.end_line} ({part.line_count} lines)")
                print(f"  Words: {part.word_count} | Chars: {part.char_count}")

                if part.metadata:
                    for key, value in part.metadata.items():
                        print(f"  {key.title()}: {value}")

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
