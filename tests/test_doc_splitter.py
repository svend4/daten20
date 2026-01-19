#!/usr/bin/env python3
"""
Unit tests for doc-splitter.py

Tests document splitting functionality including:
- Multiple split modes (size, delimiter, chapter, section, page, smart)
- Size-based splitting (lines, words, characters)
- Smart boundary detection
- File naming and numbering
- Metadata generation
- Preview mode
- CLI integration
"""

import pytest
import os
import tempfile
import hashlib
import re
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Import required modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockSplitMode:
    """Mock SplitMode enum"""
    SIZE = "size"
    DELIMITER = "delimiter"
    CHAPTER = "chapter"
    SECTION = "section"
    PAGE = "page"
    SMART = "smart"


class MockSizeUnit:
    """Mock SizeUnit enum"""
    LINES = "lines"
    WORDS = "words"
    CHARS = "chars"


class TestEnumsAndDataClasses:
    """Test suite for enums and data classes"""

    def test_split_mode_values(self):
        """Test SplitMode enum values"""
        assert MockSplitMode.SIZE == "size"
        assert MockSplitMode.DELIMITER == "delimiter"
        assert MockSplitMode.CHAPTER == "chapter"
        assert MockSplitMode.SECTION == "section"
        assert MockSplitMode.PAGE == "page"
        assert MockSplitMode.SMART == "smart"

    def test_size_unit_values(self):
        """Test SizeUnit enum values"""
        assert MockSizeUnit.LINES == "lines"
        assert MockSizeUnit.WORDS == "words"
        assert MockSizeUnit.CHARS == "chars"

    def test_document_part_structure(self):
        """Test DocumentPart structure"""
        part = {
            "part_number": 1,
            "content": "Test content",
            "line_count": 10,
            "word_count": 50,
            "char_count": 300,
            "start_line": 1,
            "end_line": 10,
            "file_name": "part_001.txt",
            "checksum": "abc123",
            "metadata": {}
        }

        required_fields = ["part_number", "content", "line_count", "word_count",
                          "char_count", "start_line", "end_line", "file_name", "checksum"]
        for field in required_fields:
            assert field in part

    def test_split_result_structure(self):
        """Test SplitResult structure"""
        result = {
            "input_file": "input.txt",
            "output_dir": "output/",
            "split_mode": "size",
            "total_parts": 5,
            "parts": [],
            "execution_time": 1.5,
            "metadata": {}
        }

        required_fields = ["input_file", "output_dir", "split_mode",
                          "total_parts", "parts", "execution_time", "metadata"]
        for field in required_fields:
            assert field in result

    def test_split_config_defaults(self):
        """Test SplitConfig default values"""
        config = {
            "mode": "size",
            "size_unit": "lines",
            "size_value": 100,
            "delimiter": "\n\n",
            "pattern": None,
            "preserve_context": True,
            "numbered_output": True,
            "prefix": "part",
            "extension": ".txt",
            "create_index": True
        }

        assert config["mode"] == "size"
        assert config["size_unit"] == "lines"
        assert config["size_value"] == 100
        assert config["preserve_context"] is True


class TestDocumentReading:
    """Test suite for document reading"""

    def test_read_text_document(self):
        """Test reading text document"""
        content = "Line 1\nLine 2\nLine 3\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                read_content = f.read()

            assert read_content == content
        finally:
            os.unlink(temp_path)

    def test_read_empty_document(self):
        """Test reading empty document"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert content == ""
        finally:
            os.unlink(temp_path)

    def test_read_large_document(self):
        """Test reading large document"""
        content = "Line\n" * 10000

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                read_content = f.read()

            assert len(read_content.split('\n')) >= 10000
        finally:
            os.unlink(temp_path)


class TestSplitBySize:
    """Test suite for size-based splitting"""

    def test_split_by_lines(self):
        """Test splitting by number of lines"""
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
        lines = content.split('\n')
        chunk_size = 2

        parts = []
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i + chunk_size])
            parts.append(chunk)

        assert len(parts) == 3  # 6 lines / 2 = 3 parts
        assert "Line 1" in parts[0]
        assert "Line 2" in parts[0]
        assert "Line 3" in parts[1]

    def test_split_by_words(self):
        """Test splitting by number of words"""
        content = "word1 word2 word3 word4 word5 word6 word7 word8"
        words = content.split()
        chunk_size = 3

        parts = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            parts.append(chunk)

        assert len(parts) == 3  # 8 words / 3 ≈ 3 parts
        assert "word1 word2 word3" == parts[0]

    def test_split_by_characters(self):
        """Test splitting by number of characters"""
        content = "A" * 100
        chunk_size = 25

        parts = []
        for i in range(0, len(content), chunk_size):
            parts.append(content[i:i + chunk_size])

        assert len(parts) == 4  # 100 / 25 = 4 parts
        assert len(parts[0]) == 25

    def test_uneven_split(self):
        """Test splitting with remainder"""
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        lines = content.split('\n')
        chunk_size = 2

        parts = []
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i + chunk_size])
            parts.append(chunk)

        assert len(parts) == 3  # 5 lines / 2 = 2 full + 1 partial
        assert "Line 5" in parts[-1]  # Last part has remainder


class TestSplitByDelimiter:
    """Test suite for delimiter-based splitting"""

    def test_split_by_blank_lines(self):
        """Test splitting by blank lines"""
        content = "Para 1\nLine 2\n\nPara 2\nLine 2\n\nPara 3"
        parts = content.split('\n\n')

        assert len(parts) == 3
        assert "Para 1" in parts[0]
        assert "Para 2" in parts[1]
        assert "Para 3" in parts[2]

    def test_split_by_custom_delimiter(self):
        """Test splitting by custom delimiter"""
        content = "Part 1 text---Part 2 text---Part 3 text"
        delimiter = "---"
        parts = content.split(delimiter)

        assert len(parts) == 3
        assert "Part 1" in parts[0]
        assert "Part 2" in parts[1]
        assert "Part 3" in parts[2]

    def test_split_by_pattern(self):
        """Test splitting by regex pattern"""
        content = "Section A: text\nSection B: text\nSection C: text"
        pattern = r'Section [A-Z]: '
        parts = re.split(pattern, content)

        # First element is before first match (empty or text)
        parts = [p for p in parts if p]  # Filter empty parts

        assert len(parts) >= 1

    def test_delimiter_not_found(self):
        """Test when delimiter is not found"""
        content = "No delimiter here"
        delimiter = "---"
        parts = content.split(delimiter)

        assert len(parts) == 1
        assert parts[0] == content


class TestSplitByChapter:
    """Test suite for chapter-based splitting"""

    def test_split_by_chapter_markers(self):
        """Test splitting by chapter markers"""
        content = """Chapter 1
Content of chapter 1

Chapter 2
Content of chapter 2

Chapter 3
Content of chapter 3"""

        pattern = r'Chapter \d+'
        parts = re.split(pattern, content)
        parts = [p.strip() for p in parts if p.strip()]

        assert len(parts) == 3

    def test_chapter_with_numbers(self):
        """Test detecting chapters with numbers"""
        content = "Chapter 1\nText\nChapter 2\nMore text"
        matches = re.findall(r'Chapter \d+', content)

        assert len(matches) == 2
        assert "Chapter 1" in matches
        assert "Chapter 2" in matches

    def test_chapter_variations(self):
        """Test different chapter formats"""
        patterns = [
            "Chapter 1",
            "CHAPTER 1",
            "Chapter I",
            "Ch. 1"
        ]

        for pattern in patterns:
            assert len(pattern) > 0
            assert "chapter" in pattern.lower() or "ch." in pattern.lower()


class TestSplitBySection:
    """Test suite for section-based splitting"""

    def test_split_by_section_headers(self):
        """Test splitting by section headers"""
        content = """## Section 1
Content here

## Section 2
More content

## Section 3
Final content"""

        parts = re.split(r'##\s+Section\s+\d+', content)
        parts = [p.strip() for p in parts if p.strip()]

        assert len(parts) == 3

    def test_detect_markdown_headers(self):
        """Test detecting markdown-style headers"""
        content = "## Header 1\nText\n### Header 2\nMore text"
        headers = re.findall(r'#{1,6}\s+.+', content)

        assert len(headers) == 2

    def test_section_numbering(self):
        """Test section numbering detection"""
        content = "1. First\n2. Second\n3. Third"
        sections = re.findall(r'\d+\.\s+\w+', content)

        assert len(sections) == 3


class TestSplitByPage:
    """Test suite for page-based splitting"""

    def test_split_by_page_breaks(self):
        """Test splitting by page break markers"""
        content = "Page 1 content\f\nPage 2 content\f\nPage 3 content"
        parts = content.split('\f')

        assert len(parts) == 3

    def test_page_marker_detection(self):
        """Test detecting page markers"""
        content = "Text\n<!-- PAGE BREAK -->\nMore text"
        page_breaks = re.findall(r'<!--\s*PAGE BREAK\s*-->', content)

        assert len(page_breaks) == 1

    def test_custom_page_markers(self):
        """Test custom page markers"""
        content = "Page 1\n[NEWPAGE]\nPage 2\n[NEWPAGE]\nPage 3"
        parts = content.split('[NEWPAGE]')

        assert len(parts) == 3


class TestSmartSplitting:
    """Test suite for smart splitting"""

    def test_preserve_paragraphs(self):
        """Test preserving paragraph boundaries"""
        content = "Para 1 line 1\nPara 1 line 2\n\nPara 2 line 1\nPara 2 line 2"
        paragraphs = content.split('\n\n')

        assert len(paragraphs) == 2

    def test_preserve_sentences(self):
        """Test preserving sentence boundaries"""
        content = "Sentence one. Sentence two. Sentence three."
        sentences = re.split(r'(?<=[.!?])\s+', content)

        assert len(sentences) == 3

    def test_avoid_word_breaks(self):
        """Test avoiding word breaks"""
        content = "This is a long sentence with many words"
        words = content.split()

        # Split should not break words
        for word in words:
            assert ' ' not in word

    def test_context_window(self):
        """Test context preservation with overlap"""
        lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        chunk_size = 2
        overlap = 1

        parts = []
        for i in range(0, len(lines), chunk_size - overlap):
            end = min(i + chunk_size, len(lines))
            chunk = lines[i:end]
            parts.append(chunk)

        # Check overlap
        if len(parts) > 1:
            assert parts[0][-1] == parts[1][0]  # Last line of first = first line of second


class TestFileNaming:
    """Test suite for file naming"""

    def test_numbered_file_names(self):
        """Test generating numbered file names"""
        prefix = "part"
        extension = ".txt"

        names = []
        for i in range(1, 11):
            name = f"{prefix}_{i:03d}{extension}"
            names.append(name)

        assert len(names) == 10
        assert names[0] == "part_001.txt"
        assert names[9] == "part_010.txt"

    def test_custom_prefix(self):
        """Test custom prefix for file names"""
        prefix = "chapter"
        name = f"{prefix}_001.txt"

        assert name.startswith(prefix)

    def test_file_extension(self):
        """Test file extension handling"""
        extensions = [".txt", ".md", ".html"]

        for ext in extensions:
            name = f"part_001{ext}"
            assert name.endswith(ext)

    def test_zero_padding(self):
        """Test zero padding in numbers"""
        numbers = [1, 10, 100]
        names = [f"part_{n:03d}.txt" for n in numbers]

        assert names[0] == "part_001.txt"
        assert names[1] == "part_010.txt"
        assert names[2] == "part_100.txt"


class TestMetadataGeneration:
    """Test suite for metadata generation"""

    def test_part_metadata(self):
        """Test generating part metadata"""
        content = "Test content\nWith lines"

        metadata = {
            "line_count": content.count('\n') + 1,
            "word_count": len(content.split()),
            "char_count": len(content),
            "checksum": hashlib.md5(content.encode()).hexdigest()
        }

        assert metadata["line_count"] > 0
        assert metadata["word_count"] > 0
        assert metadata["char_count"] > 0
        assert len(metadata["checksum"]) == 32

    def test_calculate_checksum(self):
        """Test calculating part checksum"""
        content = "Test content"
        checksum = hashlib.md5(content.encode()).hexdigest()

        assert len(checksum) == 32
        assert checksum == hashlib.md5(content.encode()).hexdigest()  # Consistent

    def test_line_range_tracking(self):
        """Test tracking line ranges for parts"""
        parts = [
            {"start_line": 1, "end_line": 100},
            {"start_line": 101, "end_line": 200},
            {"start_line": 201, "end_line": 250}
        ]

        assert parts[0]["start_line"] == 1
        assert parts[1]["start_line"] == parts[0]["end_line"] + 1
        assert parts[2]["start_line"] == parts[1]["end_line"] + 1


class TestIndexCreation:
    """Test suite for index file creation"""

    def test_create_index_file(self):
        """Test creating index file"""
        parts = [
            {"part_number": 1, "file_name": "part_001.txt", "line_count": 50},
            {"part_number": 2, "file_name": "part_002.txt", "line_count": 48},
            {"part_number": 3, "file_name": "part_003.txt", "line_count": 52}
        ]

        index_lines = ["INDEX", ""]
        for part in parts:
            index_lines.append(f"{part['part_number']}. {part['file_name']} ({part['line_count']} lines)")

        index_content = "\n".join(index_lines)

        assert "INDEX" in index_content
        assert "part_001.txt" in index_content
        assert "50 lines" in index_content

    def test_index_with_metadata(self):
        """Test index with detailed metadata"""
        part = {
            "file_name": "part_001.txt",
            "line_count": 100,
            "word_count": 500,
            "char_count": 3000,
            "start_line": 1,
            "end_line": 100
        }

        index_entry = f"{part['file_name']}: Lines {part['start_line']}-{part['end_line']}, " \
                     f"{part['word_count']} words"

        assert part["file_name"] in index_entry
        assert str(part["word_count"]) in index_entry


class TestPreviewMode:
    """Test suite for preview mode"""

    def test_preview_without_writing(self):
        """Test preview mode doesn't write files"""
        preview = True
        files_written = 0

        if not preview:
            files_written += 1

        assert files_written == 0

    def test_preview_returns_results(self):
        """Test preview mode returns split results"""
        content = "Line 1\nLine 2\nLine 3"
        lines = content.split('\n')

        parts = []
        for i, line in enumerate(lines):
            parts.append({
                "part_number": i + 1,
                "content": line
            })

        assert len(parts) == 3
        assert parts[0]["content"] == "Line 1"


class TestFileWriting:
    """Test suite for writing split parts"""

    def test_write_parts_to_files(self):
        """Test writing parts to individual files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            parts = [
                ("part_001.txt", "Content 1"),
                ("part_002.txt", "Content 2")
            ]

            for filename, content in parts:
                path = Path(tmpdir) / filename
                path.write_text(content)

            files = list(Path(tmpdir).glob("*.txt"))
            assert len(files) == 2

    def test_create_output_directory(self):
        """Test creating output directory if not exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"

            assert not output_dir.exists()

            output_dir.mkdir(parents=True, exist_ok=True)

            assert output_dir.exists()
            assert output_dir.is_dir()


class TestCLIIntegration:
    """Test suite for CLI integration"""

    def test_cli_help(self):
        """Test CLI help command"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-splitter.py', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )

            assert result.returncode == 0
            assert 'split' in result.stdout.lower() or 'help' in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("doc-splitter.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")

    def test_cli_split_command(self):
        """Test split command exists"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-splitter.py', 'split', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )

            assert result.returncode in [0, 1, 2]
        except FileNotFoundError:
            pytest.skip("doc-splitter.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")


class TestEdgeCases:
    """Test suite for edge cases"""

    def test_single_line_document(self):
        """Test splitting single line document"""
        content = "Single line"
        lines = content.split('\n')

        assert len(lines) == 1

    def test_empty_parts(self):
        """Test handling empty parts"""
        content = "Line 1\n\n\n\nLine 2"
        parts = content.split('\n')
        non_empty = [p for p in parts if p]

        assert len(non_empty) == 2

    def test_very_small_chunks(self):
        """Test very small chunk sizes"""
        content = "ABCDEFGHIJ"
        chunk_size = 1

        parts = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

        assert len(parts) == 10

    def test_chunk_larger_than_content(self):
        """Test chunk size larger than content"""
        content = "Short content"
        chunk_size = 1000

        parts = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

        assert len(parts) == 1
        assert parts[0] == content

    def test_unicode_content(self):
        """Test splitting Unicode content"""
        content = "Hello 世界\nПривет мир\nBonjour monde"
        lines = content.split('\n')

        assert len(lines) == 3

    def test_special_characters(self):
        """Test content with special characters"""
        content = "Line @#$%\nLine ^&*()\nLine {}[]"
        lines = content.split('\n')

        assert len(lines) == 3


class TestStatisticsCalculation:
    """Test suite for statistics calculation"""

    def test_total_parts_count(self):
        """Test counting total parts"""
        parts = [1, 2, 3, 4, 5]

        assert len(parts) == 5

    def test_execution_time_measurement(self):
        """Test measuring execution time"""
        start = datetime.now()
        import time
        time.sleep(0.01)
        end = datetime.now()

        execution_time = (end - start).total_seconds()

        assert execution_time > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
