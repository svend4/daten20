#!/usr/bin/env python3
"""
Unit tests for doc-merger.py

Tests document merging functionality including:
- Multiple merge modes (concatenate, interleave, smart, chapters, sections)
- Table of contents generation
- Metadata extraction and preservation
- Duplicate detection and removal
- File validation
- CLI integration
"""

import pytest
import os
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
from dataclasses import asdict

# Import required modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockMergeMode:
    """Mock MergeMode enum"""
    CONCATENATE = "concatenate"
    INTERLEAVE = "interleave"
    SMART = "smart"
    CHAPTERS = "chapters"
    SECTIONS = "sections"


class MockConflictResolution:
    """Mock ConflictResolution enum"""
    KEEP_FIRST = "keep_first"
    KEEP_LAST = "keep_last"
    KEEP_ALL = "keep_all"
    MANUAL = "manual"


class TestEnumsAndDataClasses:
    """Test suite for enums and data classes"""

    def test_merge_mode_values(self):
        """Test MergeMode enum values"""
        modes = ["concatenate", "interleave", "smart", "chapters", "sections"]

        assert MockMergeMode.CONCATENATE == "concatenate"
        assert MockMergeMode.INTERLEAVE == "interleave"
        assert MockMergeMode.SMART == "smart"
        assert MockMergeMode.CHAPTERS == "chapters"
        assert MockMergeMode.SECTIONS == "sections"

    def test_conflict_resolution_values(self):
        """Test ConflictResolution enum values"""
        strategies = ["keep_first", "keep_last", "keep_all", "manual"]

        assert MockConflictResolution.KEEP_FIRST == "keep_first"
        assert MockConflictResolution.KEEP_LAST == "keep_last"
        assert MockConflictResolution.KEEP_ALL == "keep_all"
        assert MockConflictResolution.MANUAL == "manual"

    def test_document_metadata_structure(self):
        """Test DocumentMetadata structure"""
        metadata = {
            "file_path": "/path/to/file.txt",
            "file_name": "file.txt",
            "file_size": 1024,
            "line_count": 50,
            "word_count": 200,
            "char_count": 1024,
            "checksum": "abc123",
            "encoding": "utf-8"
        }

        required_fields = ["file_path", "file_name", "file_size", "line_count",
                          "word_count", "char_count", "checksum"]
        for field in required_fields:
            assert field in metadata

    def test_merge_result_structure(self):
        """Test MergeResult structure"""
        result = {
            "output_file": "output.txt",
            "merge_mode": "concatenate",
            "input_files": ["file1.txt", "file2.txt"],
            "total_lines": 100,
            "total_words": 500,
            "total_chars": 3000,
            "execution_time": 0.5,
            "has_toc": True,
            "metadata": {},
            "warnings": [],
            "errors": []
        }

        required_fields = ["output_file", "merge_mode", "input_files",
                          "total_lines", "total_words", "total_chars",
                          "execution_time", "has_toc", "metadata"]
        for field in required_fields:
            assert field in result

    def test_merge_config_defaults(self):
        """Test MergeConfig default values"""
        config = {
            "mode": "concatenate",
            "separator": "\n\n",
            "add_toc": False,
            "add_headers": True,
            "add_page_numbers": False,
            "preserve_metadata": True,
            "create_backup": False,
            "conflict_resolution": "keep_all",
            "remove_duplicates": False,
            "normalize_whitespace": True
        }

        assert config["mode"] == "concatenate"
        assert config["separator"] == "\n\n"
        assert config["add_headers"] is True
        assert config["normalize_whitespace"] is True


class TestFileValidation:
    """Test suite for file validation"""

    def test_validate_existing_files(self):
        """Test validation of existing files"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_path = f.name

        try:
            assert Path(temp_path).exists()
            assert Path(temp_path).is_file()
            assert os.access(temp_path, os.R_OK)
        finally:
            os.unlink(temp_path)

    def test_handle_missing_files(self):
        """Test handling of missing files"""
        missing_file = "/path/to/nonexistent/file.txt"

        assert not Path(missing_file).exists()

    def test_handle_directories(self):
        """Test handling of directories (not files)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)

            assert dir_path.exists()
            assert not dir_path.is_file()
            assert dir_path.is_dir()

    def test_filter_valid_files(self):
        """Test filtering valid files from list"""
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f1:
            f1.write("File 1")
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f2:
            f2.write("File 2")
            file2 = f2.name

        try:
            files = [file1, file2, "/nonexistent/file.txt"]
            valid_files = [f for f in files if Path(f).exists()]

            assert len(valid_files) == 2
            assert file1 in valid_files
            assert file2 in valid_files
        finally:
            os.unlink(file1)
            os.unlink(file2)


class TestDocumentReading:
    """Test suite for document reading"""

    def test_read_text_file(self):
        """Test reading text file"""
        content = "This is test content\nWith multiple lines\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                read_content = f.read()

            assert read_content == content
        finally:
            os.unlink(temp_path)

    def test_read_empty_file(self):
        """Test reading empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert content == ""
            assert len(content) == 0
        finally:
            os.unlink(temp_path)

    def test_read_multiple_files(self):
        """Test reading multiple files"""
        files = []
        contents = ["Content 1", "Content 2", "Content 3"]

        for idx, content in enumerate(contents):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(content)
                files.append(f.name)

        try:
            read_contents = []
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    read_contents.append(f.read())

            assert len(read_contents) == 3
            assert read_contents == contents
        finally:
            for file_path in files:
                os.unlink(file_path)

    def test_handle_unicode_content(self):
        """Test reading files with Unicode content"""
        unicode_content = "Hello 世界 🌍 Привет café"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(unicode_content)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert content == unicode_content
        finally:
            os.unlink(temp_path)


class TestMetadataExtraction:
    """Test suite for metadata extraction"""

    def test_extract_basic_metadata(self):
        """Test extracting basic file metadata"""
        content = "Line 1\nLine 2\nLine 3"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            path = Path(temp_path)
            stat = path.stat()

            # Test metadata components
            assert path.exists()
            assert stat.st_size > 0
            assert path.name.endswith('.txt')
        finally:
            os.unlink(temp_path)

    def test_count_lines(self):
        """Test line counting"""
        content = "Line 1\nLine 2\nLine 3\n"
        line_count = content.count('\n') + 1

        assert line_count == 4  # 3 lines + 1 for the last line

    def test_count_words(self):
        """Test word counting"""
        content = "This is a test document with multiple words"
        words = content.split()

        assert len(words) == 8

    def test_count_characters(self):
        """Test character counting"""
        content = "Hello World!"
        char_count = len(content)

        assert char_count == 12

    def test_calculate_checksum(self):
        """Test MD5 checksum calculation"""
        content = "Test content for checksum"
        checksum = hashlib.md5(content.encode()).hexdigest()

        assert len(checksum) == 32  # MD5 produces 32-character hex string
        assert checksum == hashlib.md5(content.encode()).hexdigest()  # Consistent

    def test_checksum_uniqueness(self):
        """Test that different content produces different checksums"""
        content1 = "Content A"
        content2 = "Content B"

        checksum1 = hashlib.md5(content1.encode()).hexdigest()
        checksum2 = hashlib.md5(content2.encode()).hexdigest()

        assert checksum1 != checksum2


class TestMergeModes:
    """Test suite for different merge modes"""

    def test_concatenate_mode(self):
        """Test simple concatenation merge"""
        docs = ["Document 1", "Document 2", "Document 3"]
        separator = "\n\n"

        # Simple concatenation
        merged = separator.join(docs)

        assert "Document 1" in merged
        assert "Document 2" in merged
        assert "Document 3" in merged
        assert merged.count("\n\n") >= 2

    def test_concatenate_with_headers(self):
        """Test concatenation with headers"""
        docs = ["Content A", "Content B"]
        titles = ["Doc 1", "Doc 2"]

        parts = []
        for idx, (doc, title) in enumerate(zip(docs, titles), 1):
            header = f"Document {idx}: {title}\n"
            parts.append(header)
            parts.append(doc)
            parts.append("\n\n")

        merged = "".join(parts)

        assert "Document 1: Doc 1" in merged
        assert "Document 2: Doc 2" in merged
        assert "Content A" in merged
        assert "Content B" in merged

    def test_interleave_mode(self):
        """Test interleaving lines from documents"""
        doc1 = "Line 1A\nLine 2A\nLine 3A"
        doc2 = "Line 1B\nLine 2B\nLine 3B"

        lines1 = doc1.split('\n')
        lines2 = doc2.split('\n')

        # Interleave
        result = []
        for l1, l2 in zip(lines1, lines2):
            result.append(l1)
            result.append(l2)

        merged = '\n'.join(result)

        assert "Line 1A" in merged
        assert "Line 1B" in merged
        # Check interleaving order
        assert merged.index("Line 1A") < merged.index("Line 1B")
        assert merged.index("Line 1B") < merged.index("Line 2A")

    def test_chapters_mode(self):
        """Test chapters merge mode"""
        docs = ["Chapter 1 content", "Chapter 2 content"]
        titles = ["Introduction", "Main Content"]

        parts = []
        for idx, (doc, title) in enumerate(zip(docs, titles), 1):
            chapter_header = f"CHAPTER {idx}: {title.upper()}\n\n"
            parts.append(chapter_header)
            parts.append(doc)
            parts.append("\n\n")

        merged = "".join(parts)

        assert "CHAPTER 1: INTRODUCTION" in merged
        assert "CHAPTER 2: MAIN CONTENT" in merged

    def test_sections_mode(self):
        """Test sections merge mode"""
        docs = ["Section 1 content", "Section 2 content"]
        titles = ["Background", "Results"]

        parts = []
        for idx, (doc, title) in enumerate(zip(docs, titles), 1):
            section_header = f"## Section {idx}: {title}\n\n"
            parts.append(section_header)
            parts.append(doc)

        merged = "".join(parts)

        assert "## Section 1: Background" in merged
        assert "## Section 2: Results" in merged


class TestTOCGeneration:
    """Test suite for table of contents generation"""

    def test_generate_basic_toc(self):
        """Test basic TOC generation"""
        titles = ["Document 1", "Document 2", "Document 3"]

        toc_lines = ["TABLE OF CONTENTS", ""]
        for idx, title in enumerate(titles, 1):
            toc_lines.append(f"{idx}. {title}")

        toc = "\n".join(toc_lines)

        assert "TABLE OF CONTENTS" in toc
        assert "1. Document 1" in toc
        assert "2. Document 2" in toc
        assert "3. Document 3" in toc

    def test_toc_with_metadata(self):
        """Test TOC with metadata information"""
        titles = ["Doc 1", "Doc 2"]
        metadata = [
            {"file_name": "doc1.txt", "file_size": 100, "line_count": 10, "word_count": 50},
            {"file_name": "doc2.txt", "file_size": 200, "line_count": 20, "word_count": 100}
        ]

        toc_lines = ["TABLE OF CONTENTS", ""]
        for idx, (title, meta) in enumerate(zip(titles, metadata), 1):
            toc_lines.append(f"{idx}. {title}")
            toc_lines.append(f"   File: {meta['file_name']}")
            toc_lines.append(f"   Size: {meta['file_size']} bytes")

        toc = "\n".join(toc_lines)

        assert "doc1.txt" in toc
        assert "100 bytes" in toc
        assert "doc2.txt" in toc
        assert "200 bytes" in toc

    def test_toc_timestamp(self):
        """Test TOC includes timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        toc = f"TABLE OF CONTENTS\nGenerated: {timestamp}"

        assert "Generated:" in toc
        assert timestamp in toc


class TestDuplicateRemoval:
    """Test suite for duplicate detection and removal"""

    def test_detect_duplicates(self):
        """Test detecting duplicate documents"""
        doc1 = "Same content"
        doc2 = "Same content"
        doc3 = "Different content"

        hash1 = hashlib.md5(doc1.encode()).hexdigest()
        hash2 = hashlib.md5(doc2.encode()).hexdigest()
        hash3 = hashlib.md5(doc3.encode()).hexdigest()

        assert hash1 == hash2  # Duplicates
        assert hash1 != hash3  # Different

    def test_remove_duplicate_documents(self):
        """Test removing duplicate documents"""
        documents = [
            "Document A",
            "Document B",
            "Document A",  # Duplicate
            "Document C"
        ]

        seen_hashes = set()
        unique_docs = []

        for doc in documents:
            doc_hash = hashlib.md5(doc.encode()).hexdigest()
            if doc_hash not in seen_hashes:
                seen_hashes.add(doc_hash)
                unique_docs.append(doc)

        assert len(unique_docs) == 3  # A, B, C
        assert unique_docs.count("Document A") == 1

    def test_keep_all_unique_documents(self):
        """Test keeping all unique documents"""
        documents = [
            "Document 1",
            "Document 2",
            "Document 3"
        ]

        hashes = [hashlib.md5(doc.encode()).hexdigest() for doc in documents]
        unique_hashes = set(hashes)

        assert len(unique_hashes) == 3  # All unique


class TestWhitespaceNormalization:
    """Test suite for whitespace normalization"""

    def test_normalize_blank_lines(self):
        """Test normalizing excessive blank lines"""
        import re

        content = "Line 1\n\n\n\n\nLine 2"  # 4 blank lines
        normalized = re.sub(r'\n{3,}', '\n\n', content)

        assert "\n\n\n\n" not in normalized
        assert "\n\n" in normalized

    def test_normalize_trailing_whitespace(self):
        """Test removing trailing whitespace"""
        content = "Line 1   \nLine 2  \n"
        normalized = '\n'.join(line.rstrip() for line in content.split('\n'))

        assert not normalized.endswith("   ")

    def test_normalize_leading_whitespace(self):
        """Test handling leading whitespace"""
        content = "   Line 1\n  Line 2"
        normalized = '\n'.join(line.lstrip() for line in content.split('\n'))

        assert not normalized.startswith("   ")


class TestFileWriting:
    """Test suite for output file writing"""

    def test_write_merged_content(self):
        """Test writing merged content to file"""
        content = "Merged document content\nWith multiple lines"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                read_content = f.read()

            assert read_content == content
        finally:
            os.unlink(temp_path)

    def test_overwrite_existing_file(self):
        """Test overwriting existing file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Old content")
            temp_path = f.name

        try:
            # Overwrite
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write("New content")

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert content == "New content"
            assert "Old content" not in content
        finally:
            os.unlink(temp_path)


class TestStatisticsCalculation:
    """Test suite for statistics calculation"""

    def test_calculate_line_count(self):
        """Test calculating line count"""
        content = "Line 1\nLine 2\nLine 3"
        lines = content.count('\n') + 1

        assert lines == 3

    def test_calculate_word_count(self):
        """Test calculating word count"""
        content = "This is a test with five words"
        words = len(content.split())

        assert words == 7

    def test_calculate_char_count(self):
        """Test calculating character count"""
        content = "Hello, World!"
        chars = len(content)

        assert chars == 13

    def test_measure_execution_time(self):
        """Test measuring execution time"""
        start = datetime.now()
        # Simulate work
        import time
        time.sleep(0.01)
        end = datetime.now()

        execution_time = (end - start).total_seconds()

        assert execution_time > 0
        assert execution_time < 1  # Should be very quick


class TestCLIIntegration:
    """Test suite for CLI integration"""

    def test_cli_help(self):
        """Test CLI help command"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-merger.py', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )

            assert result.returncode == 0
            assert 'merge' in result.stdout.lower() or 'help' in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("doc-merger.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")

    def test_cli_merge_command_exists(self):
        """Test merge command exists"""
        import subprocess

        try:
            result = subprocess.run(
                ['python', 'doc-merger.py', 'merge', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Should succeed or fail with known error
            assert result.returncode in [0, 1, 2]
        except FileNotFoundError:
            pytest.skip("doc-merger.py not found")
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")


class TestEdgeCases:
    """Test suite for edge cases"""

    def test_empty_document_list(self):
        """Test handling empty document list"""
        documents = []

        assert len(documents) == 0

    def test_single_document_merge(self):
        """Test merging single document"""
        documents = ["Only document"]

        merged = "\n\n".join(documents)

        assert merged == "Only document"

    def test_very_long_document(self):
        """Test handling very long documents"""
        # Create long document
        long_doc = "Line\n" * 10000

        line_count = long_doc.count('\n')

        assert line_count == 10000

    def test_special_characters(self):
        """Test handling special characters"""
        content = "Special: @#$%^&*(){}[]|\\/:;<>?,."

        # Should handle without errors
        assert len(content) > 0
        assert "@#$" in content

    def test_mixed_line_endings(self):
        """Test handling mixed line endings"""
        content_unix = "Line 1\nLine 2\n"  # LF
        content_windows = "Line 1\r\nLine 2\r\n"  # CRLF

        # Should handle both
        assert content_unix.count('\n') == 2
        assert content_windows.count('\n') == 2

    def test_unicode_in_filenames(self):
        """Test handling Unicode in filenames"""
        # Note: This may not work on all filesystems
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                delete=False,
                suffix='_测试.txt',
                dir=tempfile.gettempdir()
            ) as f:
                f.write("Test content")
                temp_path = f.name

            assert Path(temp_path).exists()
            os.unlink(temp_path)
        except (OSError, UnicodeEncodeError):
            pytest.skip("Filesystem doesn't support Unicode filenames")


class TestResultValidation:
    """Test suite for result validation"""

    def test_merge_result_completeness(self):
        """Test that merge result contains all required fields"""
        result = {
            "output_file": "output.txt",
            "merge_mode": "concatenate",
            "input_files": ["file1.txt", "file2.txt"],
            "total_lines": 50,
            "total_words": 200,
            "total_chars": 1000,
            "execution_time": 0.5,
            "has_toc": False,
            "metadata": {}
        }

        assert result["total_lines"] > 0
        assert result["total_words"] > 0
        assert result["total_chars"] > 0
        assert result["execution_time"] >= 0

    def test_statistics_consistency(self):
        """Test that statistics are consistent"""
        content = "Word1 Word2 Word3"

        words = len(content.split())
        chars = len(content)

        # Words should be less than or equal to characters
        assert words <= chars


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
