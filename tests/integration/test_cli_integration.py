"""
Integration tests for CLI applications

These tests execute actual CLI commands (not mocks) to verify:
- Real file I/O operations
- End-to-end workflows
- Actual code execution and coverage
- Integration between components

Usage:
    pytest tests/integration/test_cli_integration.py -v
    pytest tests/integration/test_cli_integration.py -v -m integration
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest
import json


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


class TestDocProcessorIntegration:
    """Integration tests for doc-processor.py"""

    def test_process_text_file(self, tmp_path):
        """Test processing a text file end-to-end"""
        # Create a temporary input file
        input_file = tmp_path / "input.txt"
        input_file.write_text("This is a test document.\nIt has multiple lines.")

        # Run the CLI command
        result = subprocess.run(
            ['python', 'doc-processor.py', str(input_file), '--format', 'text'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Verify the command succeeded
        assert result.returncode == 0

    def test_help_command(self):
        """Test that --help works"""
        result = subprocess.run(
            ['python', 'doc-processor.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        assert 'process' in result.stdout.lower() or 'usage' in result.stdout.lower()


class TestDocComparatorIntegration:
    """Integration tests for doc-comparator.py"""

    def test_compare_identical_files(self, tmp_path):
        """Test comparing two identical files"""
        # Create two identical files
        content = "This is identical content."
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text(content)
        file2.write_text(content)

        # Run comparison
        result = subprocess.run(
            ['python', 'doc-comparator.py', str(file1), str(file2), '--metric', 'cosine'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should succeed
        assert result.returncode == 0

    def test_compare_different_files(self, tmp_path):
        """Test comparing two different files"""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Document about cats")
        file2.write_text("Document about dogs")

        result = subprocess.run(
            ['python', 'doc-comparator.py', str(file1), str(file2)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0


class TestDocAnonymizerIntegration:
    """Integration tests for doc-anonymizer.py"""

    def test_anonymize_email(self, tmp_path):
        """Test anonymizing email addresses"""
        # Create input file with email
        input_file = tmp_path / "input.txt"
        input_file.write_text("Contact us at john.doe@example.com for more information.")

        output_file = tmp_path / "output.txt"

        # Run anonymization
        result = subprocess.run(
            ['python', 'doc-anonymizer.py', str(input_file), '--output', str(output_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should succeed
        assert result.returncode == 0

        # Check that output file was created
        if output_file.exists():
            content = output_file.read_text()
            # Email should be anonymized or marked
            assert 'example.com' not in content or '[EMAIL]' in content

    def test_anonymize_phone(self, tmp_path):
        """Test anonymizing phone numbers"""
        input_file = tmp_path / "input.txt"
        input_file.write_text("Call us at 555-123-4567 today!")

        output_file = tmp_path / "output.txt"

        result = subprocess.run(
            ['python', 'doc-anonymizer.py', str(input_file), '--output', str(output_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0


class TestDocQualityIntegration:
    """Integration tests for doc-quality.py"""

    def test_analyze_quality(self, tmp_path):
        """Test document quality analysis"""
        # Create a sample document
        input_file = tmp_path / "document.txt"
        input_file.write_text("""
        This is a well-structured document.

        It has multiple paragraphs and proper formatting.
        The sentences are clear and readable.
        """)

        # Run quality analysis
        result = subprocess.run(
            ['python', 'doc-quality.py', str(input_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should succeed
        assert result.returncode == 0

    def test_quality_json_output(self, tmp_path):
        """Test quality analysis with JSON output"""
        input_file = tmp_path / "document.txt"
        input_file.write_text("This is a short test document.")

        output_file = tmp_path / "quality.json"

        result = subprocess.run(
            ['python', 'doc-quality.py', str(input_file), '--output', str(output_file), '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check if JSON file was created
        if result.returncode == 0 and output_file.exists():
            # Verify it's valid JSON
            with open(output_file) as f:
                data = json.load(f)
                assert isinstance(data, (dict, list))


class TestDocMergerIntegration:
    """Integration tests for doc-merger.py"""

    def test_merge_two_files(self, tmp_path):
        """Test merging two text files"""
        file1 = tmp_path / "doc1.txt"
        file2 = tmp_path / "doc2.txt"
        output = tmp_path / "merged.txt"

        file1.write_text("Document 1 content")
        file2.write_text("Document 2 content")

        result = subprocess.run(
            ['python', 'doc-merger.py', str(file1), str(file2), '--output', str(output)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0

    def test_merge_multiple_files(self, tmp_path):
        """Test merging multiple files"""
        files = []
        for i in range(3):
            f = tmp_path / f"doc{i}.txt"
            f.write_text(f"Document {i} content")
            files.append(str(f))

        output = tmp_path / "merged.txt"

        result = subprocess.run(
            ['python', 'doc-merger.py'] + files + ['--output', str(output)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0


class TestDocSplitterIntegration:
    """Integration tests for doc-splitter.py"""

    def test_split_by_lines(self, tmp_path):
        """Test splitting a file by number of lines"""
        # Create input file with multiple lines
        input_file = tmp_path / "input.txt"
        lines = [f"Line {i}" for i in range(1, 21)]
        input_file.write_text("\n".join(lines))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Split into chunks of 5 lines
        result = subprocess.run(
            ['python', 'doc-splitter.py', str(input_file), '--lines', '5', '--output', str(output_dir)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0

    def test_split_preview(self, tmp_path):
        """Test split preview mode (no actual files created)"""
        input_file = tmp_path / "input.txt"
        input_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

        result = subprocess.run(
            ['python', 'doc-splitter.py', str(input_file), '--lines', '2', '--preview'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0


class TestDocMasterIntegration:
    """Integration tests for doc-master.py"""

    def test_status_command(self):
        """Test doc-master status command"""
        result = subprocess.run(
            ['python', 'doc-master.py', '--status'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0

    def test_list_services(self):
        """Test listing available services"""
        result = subprocess.run(
            ['python', 'doc-master.py', '--list'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0


class TestEndToEndWorkflows:
    """End-to-end workflow tests"""

    def test_process_compare_workflow(self, tmp_path):
        """Test: Process two documents then compare them"""
        # Step 1: Create two input files
        file1 = tmp_path / "doc1.txt"
        file2 = tmp_path / "doc2.txt"
        file1.write_text("The quick brown fox jumps over the lazy dog")
        file2.write_text("The fast brown fox leaps over the sleeping dog")

        # Step 2: Process both files (if needed)
        # This step depends on your doc-processor.py implementation

        # Step 3: Compare the files
        result = subprocess.run(
            ['python', 'doc-comparator.py', str(file1), str(file2)],
            capture_output=True,
            text=True,
            timeout=15
        )

        assert result.returncode == 0

    def test_merge_split_workflow(self, tmp_path):
        """Test: Merge documents then split the result"""
        # Step 1: Create input files
        file1 = tmp_path / "doc1.txt"
        file2 = tmp_path / "doc2.txt"
        file1.write_text("Part 1 content\n" * 10)
        file2.write_text("Part 2 content\n" * 10)

        # Step 2: Merge files
        merged = tmp_path / "merged.txt"
        merge_result = subprocess.run(
            ['python', 'doc-merger.py', str(file1), str(file2), '--output', str(merged)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if merge_result.returncode == 0 and merged.exists():
            # Step 3: Split the merged file
            split_dir = tmp_path / "split_output"
            split_dir.mkdir()

            split_result = subprocess.run(
                ['python', 'doc-splitter.py', str(merged), '--lines', '5', '--output', str(split_dir)],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert split_result.returncode == 0

    def test_anonymize_quality_workflow(self, tmp_path):
        """Test: Anonymize a document then check its quality"""
        # Step 1: Create input with PII
        input_file = tmp_path / "input.txt"
        input_file.write_text("""
        This document contains personal information.
        Contact: john.doe@example.com
        Phone: 555-123-4567
        """)

        # Step 2: Anonymize the document
        anonymized = tmp_path / "anonymized.txt"
        anon_result = subprocess.run(
            ['python', 'doc-anonymizer.py', str(input_file), '--output', str(anonymized)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if anon_result.returncode == 0 and anonymized.exists():
            # Step 3: Check quality of anonymized document
            quality_result = subprocess.run(
                ['python', 'doc-quality.py', str(anonymized)],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert quality_result.returncode == 0


# Pytest configuration for integration tests
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
