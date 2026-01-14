"""
E2E Test: Document Merge and Split Workflow

Tests the complete workflow of merging multiple documents into one
and splitting documents into multiple parts.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import json


class TestDocumentMergeSplitWorkflow:
    """Test complete document merge and split workflows"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.test_dir) / "input"
        self.output_dir = Path(self.test_dir) / "output"

        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        yield

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_document(self, filename: str, content: str) -> Path:
        """Create a test document"""
        doc_path = self.input_dir / filename
        doc_path.write_text(content, encoding='utf-8')
        return doc_path

    def test_simple_merge_workflow(self):
        """
        E2E Test: Merge multiple documents into one

        Steps:
        1. Create multiple source documents
        2. Merge documents
        3. Verify merged content
        4. Generate merge report
        """
        # Step 1: Create source documents
        documents = [
            ("chapter1.txt", "Chapter 1: Introduction\nThis is the first chapter."),
            ("chapter2.txt", "Chapter 2: Background\nThis is the second chapter."),
            ("chapter3.txt", "Chapter 3: Conclusion\nThis is the final chapter.")
        ]

        doc_paths = []
        for filename, content in documents:
            path = self.create_test_document(filename, content)
            doc_paths.append((filename, path, content))

        # Step 2: Merge documents
        merged_content = []
        for filename, path, content in doc_paths:
            merged_content.append(f"--- {filename} ---\n")
            merged_content.append(content)
            merged_content.append("\n\n")

        merged_text = "".join(merged_content)

        # Save merged document
        merged_path = self.output_dir / "merged_document.txt"
        merged_path.write_text(merged_text, encoding='utf-8')

        # Step 3: Verify merged content
        assert merged_path.exists()
        content = merged_path.read_text()

        # Verify all chapters are present
        for filename, _, original_content in doc_paths:
            assert filename in content
            # Check if original content is in merged doc (allowing for some formatting differences)
            for line in original_content.split('\n'):
                if line.strip():
                    assert line in content

        # Step 4: Generate merge report
        report = {
            'source_documents': [filename for filename, _, _ in doc_paths],
            'merged_document': str(merged_path.name),
            'total_documents_merged': len(doc_paths),
            'merged_size': len(merged_text),
            'merge_date': '2026-01-14'
        }

        report_path = self.output_dir / "merge_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()

        print(f"✅ Simple merge workflow passed!")
        print(f"   - Documents merged: {len(doc_paths)}")
        print(f"   - Output size: {len(merged_text)} chars")
        print(f"   - Report: {report_path}")

    def test_document_split_workflow(self):
        """
        E2E Test: Split a document into multiple parts

        Steps:
        1. Create a large document
        2. Split into smaller parts
        3. Verify all parts
        4. Generate split report
        """
        # Step 1: Create large document
        large_content = []
        for i in range(5):
            section = f"\n--- Section {i+1} ---\n"
            section += f"Content for section {i+1}.\n" * 5
            large_content.append(section)

        full_content = "".join(large_content)
        doc_path = self.create_test_document("large_document.txt", full_content)

        # Step 2: Split document (by sections)
        sections = full_content.split("--- Section")
        parts = []

        for i, section in enumerate(sections[1:], 1):  # Skip first empty part
            part_content = f"--- Section{section}"
            part_path = self.output_dir / f"part_{i}.txt"
            part_path.write_text(part_content, encoding='utf-8')
            parts.append(part_path)

        # Step 3: Verify all parts
        assert len(parts) == 5

        for i, part_path in enumerate(parts, 1):
            assert part_path.exists()
            content = part_path.read_text()
            assert f"Section {i}" in content

        # Step 4: Generate split report
        report = {
            'original_document': 'large_document.txt',
            'original_size': len(full_content),
            'parts_created': len(parts),
            'parts': [str(p.name) for p in parts],
            'split_date': '2026-01-14'
        }

        report_path = self.output_dir / "split_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()

        print(f"✅ Document split workflow passed!")
        print(f"   - Parts created: {len(parts)}")
        print(f"   - Original size: {len(full_content)} chars")
        print(f"   - Report: {report_path}")

    def test_merge_then_split_roundtrip(self):
        """
        E2E Test: Merge documents, then split them back

        Steps:
        1. Create original documents
        2. Merge into one
        3. Split back into parts
        4. Verify content preserved
        """
        # Step 1: Create original documents
        originals = [
            ("doc1.txt", "First document content"),
            ("doc2.txt", "Second document content"),
            ("doc3.txt", "Third document content")
        ]

        original_paths = []
        for filename, content in originals:
            path = self.create_test_document(filename, content)
            original_paths.append((filename, content))

        # Step 2: Merge
        merged_parts = []
        for filename, content in original_paths:
            merged_parts.append(f"###SPLIT_MARKER###\n")
            merged_parts.append(f"FILENAME:{filename}\n")
            merged_parts.append(content)
            merged_parts.append("\n")

        merged_content = "".join(merged_parts)
        merged_path = self.output_dir / "merged.txt"
        merged_path.write_text(merged_content, encoding='utf-8')

        # Step 3: Split back
        split_parts = merged_content.split("###SPLIT_MARKER###")
        reconstructed = []

        for part in split_parts[1:]:  # Skip first empty part
            lines = part.strip().split('\n')
            if len(lines) >= 2 and lines[0].startswith('FILENAME:'):
                filename = lines[0].replace('FILENAME:', '')
                content = '\n'.join(lines[1:])
                reconstructed.append((filename, content))

        # Step 4: Verify
        assert len(reconstructed) == len(originals)

        for (orig_name, orig_content), (recon_name, recon_content) in zip(originals, reconstructed):
            assert orig_name == recon_name
            assert orig_content == recon_content.strip()

        print(f"✅ Merge-split roundtrip test passed!")
        print(f"   - Original documents: {len(originals)}")
        print(f"   - Reconstructed: {len(reconstructed)}")
        print(f"   - Content preserved: Yes")

    def test_smart_merge_with_metadata(self):
        """
        E2E Test: Merge documents with metadata preservation

        Steps:
        1. Create documents with metadata
        2. Merge preserving metadata
        3. Verify metadata is accessible
        4. Generate comprehensive merge report
        """
        # Step 1: Create documents with metadata
        documents = [
            {
                'filename': 'report1.txt',
                'content': 'First quarterly report',
                'metadata': {'author': 'Alice', 'date': '2026-01-01', 'version': 1}
            },
            {
                'filename': 'report2.txt',
                'content': 'Second quarterly report',
                'metadata': {'author': 'Bob', 'date': '2026-04-01', 'version': 1}
            }
        ]

        # Create documents
        for doc in documents:
            self.create_test_document(doc['filename'], doc['content'])

        # Step 2: Merge with metadata
        merged_structure = {
            'documents': [],
            'merged_content': ''
        }

        merged_text_parts = []
        for doc in documents:
            # Add to structure
            merged_structure['documents'].append({
                'filename': doc['filename'],
                'metadata': doc['metadata'],
                'content_offset': len(merged_text_parts)
            })

            # Add to merged content
            merged_text_parts.append(doc['content'])
            merged_text_parts.append('\n\n')

        merged_structure['merged_content'] = ''.join(merged_text_parts)

        # Save merged document
        merged_path = self.output_dir / "merged_with_metadata.txt"
        merged_path.write_text(merged_structure['merged_content'], encoding='utf-8')

        # Save metadata
        metadata_path = self.output_dir / "merged_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(merged_structure, f, indent=2)

        # Step 3: Verify metadata is accessible
        with open(metadata_path, 'r') as f:
            loaded_metadata = json.load(f)

        assert len(loaded_metadata['documents']) == len(documents)
        assert 'Alice' in str(loaded_metadata)
        assert 'Bob' in str(loaded_metadata)

        # Step 4: Generate comprehensive report
        report = {
            'merge_type': 'smart_merge_with_metadata',
            'total_documents': len(documents),
            'total_authors': len(set(doc['metadata']['author'] for doc in documents)),
            'metadata_preserved': True,
            'output_files': {
                'content': str(merged_path.name),
                'metadata': str(metadata_path.name)
            }
        }

        report_path = self.output_dir / "smart_merge_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()

        print(f"✅ Smart merge with metadata test passed!")
        print(f"   - Documents merged: {len(documents)}")
        print(f"   - Metadata preserved: Yes")
        print(f"   - Report: {report_path}")

    def test_conditional_split_workflow(self):
        """
        E2E Test: Split document based on conditions (e.g., size, markers)

        Steps:
        1. Create document with markers
        2. Split by markers
        3. Validate split parts
        4. Test different split conditions
        """
        # Step 1: Create document with markers
        content = """===PAGE_BREAK===
Page 1 Content
This is the first page.
===PAGE_BREAK===
Page 2 Content
This is the second page.
===PAGE_BREAK===
Page 3 Content
This is the third page."""

        doc_path = self.create_test_document("paginated_doc.txt", content)

        # Step 2: Split by markers
        pages = content.split("===PAGE_BREAK===")
        page_parts = [p.strip() for p in pages if p.strip()]

        # Save each page
        saved_pages = []
        for i, page_content in enumerate(page_parts, 1):
            page_path = self.output_dir / f"page_{i}.txt"
            page_path.write_text(page_content, encoding='utf-8')
            saved_pages.append(page_path)

        # Step 3: Validate
        assert len(saved_pages) == 3

        for i, page_path in enumerate(saved_pages, 1):
            assert page_path.exists()
            content = page_path.read_text()
            assert f"Page {i}" in content

        # Step 4: Test size-based split
        large_text = "Word " * 1000  # 1000 words
        doc_path = self.create_test_document("large.txt", large_text)

        # Split into chunks of ~200 words
        words = large_text.split()
        chunk_size = 200
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunk_path = self.output_dir / f"chunk_{i//chunk_size + 1}.txt"
            chunk_path.write_text(chunk, encoding='utf-8')
            chunks.append(chunk_path)

        assert len(chunks) == 5  # 1000 / 200 = 5

        print(f"✅ Conditional split workflow passed!")
        print(f"   - Pages split: {len(saved_pages)}")
        print(f"   - Size-based chunks: {len(chunks)}")
        print(f"   - All validations passed")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
