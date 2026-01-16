"""
E2E Test: Document Comparison Workflow

Tests the complete workflow of comparing documents, including
similarity analysis, diff generation, and report creation.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest


class TestDocumentComparisonWorkflow:
    """Test complete document comparison workflow"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = Path(self.test_dir) / "documents"
        self.reports_dir = Path(self.test_dir) / "reports"

        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        yield

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_document(self, filename: str, content: str) -> Path:
        """Create a test document"""
        doc_path = self.docs_dir / filename
        doc_path.write_text(content, encoding="utf-8")
        return doc_path

    def test_similar_documents_comparison(self):
        """
        E2E Test: Compare two similar documents

        Steps:
        1. Create two similar documents
        2. Run comparison
        3. Verify similarity metrics
        4. Generate comparison report
        """
        # Step 1: Create documents
        doc1_content = """
        Product Description:
        Our premium coffee maker features:
        - Automatic brewing
        - Temperature control
        - 12-cup capacity
        Price: $99.99
        """

        doc2_content = """
        Product Description:
        Our deluxe coffee maker features:
        - Automatic brewing
        - Temperature control
        - 12-cup capacity
        - Timer function
        Price: $119.99
        """

        doc1_path = self.create_test_document("product_v1.txt", doc1_content)
        doc2_path = self.create_test_document("product_v2.txt", doc2_content)

        # Step 2: Read documents
        text1 = doc1_path.read_text()
        text2 = doc2_path.read_text()

        # Step 3: Calculate similarity (basic implementation)
        # Using simple word overlap for this E2E test
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        similarity = intersection / union if union > 0 else 0

        assert similarity > 0.5  # Should be fairly similar

        # Step 4: Generate comparison report
        report = {
            "document1": str(doc1_path.name),
            "document2": str(doc2_path.name),
            "similarity_score": similarity,
            "common_words": intersection,
            "total_unique_words": union,
            "differences": {"doc1_only_words": len(words1 - words2), "doc2_only_words": len(words2 - words1)},
        }

        report_path = self.reports_dir / "comparison_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()

        print(f"✅ Similar documents comparison passed!")
        print(f"   - Similarity score: {similarity:.2%}")
        print(f"   - Common words: {intersection}")
        print(f"   - Report: {report_path}")

    def test_different_documents_comparison(self):
        """
        E2E Test: Compare two different documents

        Steps:
        1. Create two completely different documents
        2. Run comparison
        3. Verify low similarity
        """
        # Step 1: Create different documents
        doc1_content = "This document is about machine learning and artificial intelligence."
        doc2_content = "This recipe explains how to bake a chocolate cake with butter and eggs."

        doc1_path = self.create_test_document("ml_doc.txt", doc1_content)
        doc2_path = self.create_test_document("recipe.txt", doc2_content)

        # Step 2: Read and compare
        text1 = doc1_path.read_text()
        text2 = doc2_path.read_text()

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        similarity = intersection / union if union > 0 else 0

        # Step 3: Verify low similarity
        assert similarity < 0.5  # Should be quite different

        print(f"✅ Different documents comparison passed!")
        print(f"   - Similarity score: {similarity:.2%}")
        print(f"   - These documents are appropriately different")

    def test_version_comparison_workflow(self):
        """
        E2E Test: Compare multiple versions of a document

        Steps:
        1. Create multiple versions of a document
        2. Compare each version to the next
        3. Track changes across versions
        4. Generate version history report
        """
        # Step 1: Create document versions
        versions = [
            ("v1.txt", "Initial draft of the document."),
            ("v2.txt", "Initial draft of the document with minor edits."),
            ("v3.txt", "Initial draft of the document with minor edits and new section."),
        ]

        version_paths = []
        for filename, content in versions:
            path = self.create_test_document(filename, content)
            version_paths.append((filename, path, content))

        # Step 2 & 3: Compare versions
        changes = []

        for i in range(len(version_paths) - 1):
            curr_name, curr_path, curr_content = version_paths[i]
            next_name, next_path, next_content = version_paths[i + 1]

            # Read documents
            text_curr = curr_path.read_text()
            text_next = next_path.read_text()

            # Calculate changes
            words_curr = set(text_curr.lower().split())
            words_next = set(text_next.lower().split())

            added_words = words_next - words_curr
            removed_words = words_curr - words_next

            changes.append(
                {
                    "from_version": curr_name,
                    "to_version": next_name,
                    "words_added": len(added_words),
                    "words_removed": len(removed_words),
                    "total_changes": len(added_words) + len(removed_words),
                }
            )

        # Step 4: Generate version history report
        report = {"total_versions": len(version_paths), "version_history": changes}

        report_path = self.reports_dir / "version_history.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()
        assert len(changes) == len(version_paths) - 1

        print(f"✅ Version comparison workflow passed!")
        print(f"   - Versions tracked: {len(version_paths)}")
        print(f"   - Comparisons made: {len(changes)}")
        print(f"   - Report: {report_path}")

    def test_batch_comparison_workflow(self):
        """
        E2E Test: Batch comparison of multiple documents

        Steps:
        1. Create multiple documents
        2. Compare all pairs
        3. Find most similar documents
        4. Generate similarity matrix
        """
        # Step 1: Create documents
        documents = [
            ("doc1.txt", "Python programming language for data science"),
            ("doc2.txt", "Python programming language for web development"),
            ("doc3.txt", "Java object-oriented programming language"),
            ("doc4.txt", "JavaScript language for web browsers"),
        ]

        doc_paths = []
        for filename, content in documents:
            path = self.create_test_document(filename, content)
            doc_paths.append((filename, path, content))

        # Step 2: Compare all pairs
        similarity_matrix = []

        for i, (name1, path1, content1) in enumerate(doc_paths):
            text1 = path1.read_text()
            words1 = set(text1.lower().split())

            row = []
            for j, (name2, path2, content2) in enumerate(doc_paths):
                if i == j:
                    row.append(1.0)  # Same document
                else:
                    text2 = path2.read_text()
                    words2 = set(text2.lower().split())

                    intersection = len(words1.intersection(words2))
                    union = len(words1.union(words2))
                    similarity = intersection / union if union > 0 else 0

                    row.append(round(similarity, 3))

            similarity_matrix.append(row)

        # Step 3: Find most similar pair
        max_similarity = 0
        most_similar_pair = (0, 0)

        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                if similarity_matrix[i][j] > max_similarity:
                    max_similarity = similarity_matrix[i][j]
                    most_similar_pair = (i, j)

        # Step 4: Generate report
        report = {
            "total_documents": len(doc_paths),
            "similarity_matrix": similarity_matrix,
            "most_similar_pair": {
                "documents": [doc_paths[most_similar_pair[0]][0], doc_paths[most_similar_pair[1]][0]],
                "similarity": max_similarity,
            },
        }

        report_path = self.reports_dir / "batch_comparison.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        assert report_path.exists()

        print(f"✅ Batch comparison workflow passed!")
        print(f"   - Documents compared: {len(doc_paths)}")
        print(f"   - Most similar: {report['most_similar_pair']['documents']}")
        print(f"   - Similarity: {max_similarity:.2%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
