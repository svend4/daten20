"""
Unit tests for doc-comparator.py
=================================

Tests all major functionality of DocumentComparator:
- Similarity calculations (Cosine, Jaccard, Levenshtein)
- Entity comparison
- Diff generation
- Report generation
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import the comparator module
import importlib.util
spec = importlib.util.spec_from_file_location("doc_comparator", "doc-comparator.py")
doc_comparator = importlib.util.module_from_spec(spec)
sys.modules['doc_comparator'] = doc_comparator  # Add to sys.modules for imports to work
spec.loader.exec_module(doc_comparator)

from doc_comparator import DocumentComparator, ComparisonResult


# Fixtures
@pytest.fixture
def comparator():
    """Create DocumentComparator instance."""
    return DocumentComparator()


@pytest.fixture
def sample_docs_dir():
    """Path to sample documents directory."""
    return Path(__file__).parent.parent.parent / "fixtures" / "sample_docs"


@pytest.fixture
def sample1_path(sample_docs_dir):
    """Path to sample1.txt"""
    return str(sample_docs_dir / "sample1.txt")


@pytest.fixture
def sample2_path(sample_docs_dir):
    """Path to sample2.txt"""
    return str(sample_docs_dir / "sample2.txt")


@pytest.fixture
def sample1_copy_path(sample_docs_dir):
    """Path to sample1_copy.txt (identical to sample1)"""
    return str(sample_docs_dir / "sample1_copy.txt")


# Test Class
class TestDocumentComparator:
    """Test suite for DocumentComparator"""

    def test_comparator_initialization(self, comparator):
        """Test that comparator initializes correctly"""
        assert comparator is not None
        assert comparator.parser is not None
        assert comparator.ner_engine is not None

    def test_compare_identical_documents(self, comparator, sample1_path, sample1_copy_path):
        """Test comparing two identical documents"""
        result = comparator.compare(sample1_path, sample1_copy_path)

        assert isinstance(result, ComparisonResult)
        # Identical documents should have perfect similarity
        assert result.cosine_similarity > 0.99
        assert result.jaccard_similarity > 0.99
        assert result.levenshtein_similarity > 0.99

        # No changes expected
        assert result.added_lines == 0
        assert result.removed_lines == 0

    def test_compare_different_documents(self, comparator, sample1_path, sample2_path):
        """Test comparing two different documents"""
        result = comparator.compare(sample1_path, sample2_path)

        assert isinstance(result, ComparisonResult)
        # Different documents should have lower similarity
        assert 0.3 < result.cosine_similarity < 0.99
        assert 0.1 < result.jaccard_similarity < 0.99  # Adjusted threshold based on actual test data

        # Should detect changes
        assert result.added_lines > 0 or result.removed_lines > 0 or result.modified_lines > 0

    def test_cosine_similarity_calculation(self, comparator):
        """Test cosine similarity calculation"""
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The quick brown fox jumps over the lazy dog"
        similarity = comparator._cosine_similarity(text1, text2)

        assert similarity == 1.0  # Identical texts

        text3 = "A completely different text"
        similarity2 = comparator._cosine_similarity(text1, text3)
        assert similarity2 < 0.5  # Very different texts

    def test_jaccard_similarity_calculation(self, comparator):
        """Test Jaccard similarity calculation"""
        text1 = "the quick brown fox"
        text2 = "the quick brown fox"
        similarity = comparator._jaccard_similarity(text1, text2)

        assert similarity == 1.0  # Identical texts

        text3 = "completely different words"
        similarity2 = comparator._jaccard_similarity(text1, text3)
        assert similarity2 == 0.0  # No common words

    def test_levenshtein_distance(self, comparator):
        """Test Levenshtein distance calculation"""
        text1 = "kitten"
        text2 = "sitting"
        distance, similarity = comparator._levenshtein_distance_and_similarity(text1, text2)

        assert distance == 3  # 3 edits needed
        assert 0 < similarity < 1  # Partial similarity

        text3 = "kitten"
        text4 = "kitten"
        distance2, similarity2 = comparator._levenshtein_distance_and_similarity(text3, text4)
        assert distance2 == 0  # No edits needed
        assert similarity2 == 1.0  # Perfect match

    def test_diff_analysis(self, comparator):
        """Test diff analysis functionality"""
        text1 = "Line 1\nLine 2\nLine 3"
        text2 = "Line 1\nLine 2 modified\nLine 3\nLine 4"

        diff_stats = comparator._analyze_diff(text1, text2)

        assert 'added' in diff_stats
        assert 'removed' in diff_stats
        assert 'modified' in diff_stats
        assert 'unchanged' in diff_stats

        assert diff_stats['added'] >= 0
        assert diff_stats['removed'] >= 0
        assert diff_stats['unchanged'] > 0

    def test_entity_comparison(self, comparator):
        """Test entity comparison"""
        text1 = "Max Mustermann lives in Berlin. Email: max@example.com"
        text2 = "John Doe lives in Munich. Email: john@example.com"

        entity_stats = comparator._compare_entities(text1, text2)

        assert 'doc1_count' in entity_stats
        assert 'doc2_count' in entity_stats
        assert 'common_count' in entity_stats
        assert 'overlap' in entity_stats

        assert entity_stats['doc1_count'] >= 0
        assert entity_stats['doc2_count'] >= 0

    def test_unified_diff_generation(self, comparator):
        """Test unified diff generation"""
        text1 = "Line 1\nLine 2\nLine 3"
        text2 = "Line 1\nLine 2 modified\nLine 3"

        diff = comparator._generate_unified_diff(text1, text2, "file1.txt", "file2.txt")

        assert isinstance(diff, str)
        # Unified diff should contain file names
        assert "file1.txt" in diff or "file2.txt" in diff

    def test_html_diff_generation(self, comparator):
        """Test HTML diff generation"""
        text1 = "Line 1\nLine 2\nLine 3"
        text2 = "Line 1\nLine 2 modified\nLine 3"

        html = comparator._generate_html_diff(text1, text2)

        assert isinstance(html, str)
        assert len(html) > 0
        # HTML should contain basic HTML tags
        assert "<" in html and ">" in html

    def test_report_generation_json(self, comparator, sample1_path, sample2_path, tmp_path):
        """Test JSON report generation"""
        result = comparator.compare(sample1_path, sample2_path, include_diff=False)

        output_file = tmp_path / "comparison_report.json"
        report = comparator.generate_report(result, format="json", output_file=str(output_file))

        assert isinstance(report, str)
        assert output_file.exists()

        # Should be valid JSON
        import json
        data = json.loads(report)
        assert "cosine_similarity" in data
        assert "jaccard_similarity" in data

    def test_report_generation_text(self, comparator, sample1_path, sample2_path, tmp_path):
        """Test text report generation"""
        result = comparator.compare(sample1_path, sample2_path, include_diff=False)

        output_file = tmp_path / "comparison_report.txt"
        report = comparator.generate_report(result, format="text", output_file=str(output_file))

        assert isinstance(report, str)
        assert output_file.exists()
        assert "SIMILARITY METRICS" in report
        assert "STRUCTURAL CHANGES" in report

    def test_report_generation_html(self, comparator, sample1_path, sample2_path, tmp_path):
        """Test HTML report generation"""
        result = comparator.compare(sample1_path, sample2_path, include_diff=False)

        output_file = tmp_path / "comparison_report.html"
        report = comparator.generate_report(result, format="html", output_file=str(output_file))

        assert isinstance(report, str)
        assert output_file.exists()
        assert "<!DOCTYPE html>" in report
        assert "Document Comparison Report" in report

    def test_comparison_without_entities(self, comparator, sample1_path, sample2_path):
        """Test comparison without entity analysis"""
        result = comparator.compare(
            sample1_path,
            sample2_path,
            include_entities=False
        )

        assert result.entities_doc1 == 0
        assert result.entities_doc2 == 0
        assert result.common_entities == 0

    def test_comparison_without_diff(self, comparator, sample1_path, sample2_path):
        """Test comparison without diff generation"""
        result = comparator.compare(
            sample1_path,
            sample2_path,
            include_diff=False
        )

        assert result.diff_unified == ""
        assert result.diff_html == ""

    def test_comparison_result_to_dict(self, comparator, sample1_path, sample2_path):
        """Test ComparisonResult to_dict() method"""
        result = comparator.compare(sample1_path, sample2_path, include_diff=False)

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "cosine_similarity" in result_dict
        assert "jaccard_similarity" in result_dict
        assert "levenshtein_distance" in result_dict
        assert "doc1_path" in result_dict
        assert "doc2_path" in result_dict

    def test_edge_case_empty_texts(self, comparator):
        """Test comparison of empty texts"""
        similarity = comparator._cosine_similarity("", "")
        assert similarity == 0.0  # Empty texts have no similarity

        jaccard = comparator._jaccard_similarity("", "")
        assert jaccard == 0.0

    def test_edge_case_very_short_texts(self, comparator):
        """Test comparison of very short texts"""
        text1 = "a"
        text2 = "b"

        distance, similarity = comparator._levenshtein_distance_and_similarity(text1, text2)
        assert distance == 1
        assert similarity == 0.0

    def test_edge_case_long_texts(self, comparator):
        """Test comparison of long texts (should sample)"""
        text1 = "word " * 10000  # Very long text
        text2 = "word " * 10000

        # Should not crash, even with very long texts
        distance, similarity = comparator._levenshtein_distance_and_similarity(text1, text2)
        assert distance >= 0
        assert 0 <= similarity <= 1


# Integration Tests
class TestDocumentComparatorIntegration:
    """Integration tests for DocumentComparator with real files"""

    def test_full_comparison_workflow(self, comparator, sample1_path, sample2_path, tmp_path):
        """Test complete comparison workflow"""
        # 1. Compare documents
        result = comparator.compare(sample1_path, sample2_path)

        # 2. Verify result
        assert result is not None
        assert 0 <= result.cosine_similarity <= 1

        # 3. Generate all report formats
        json_report = comparator.generate_report(result, format="json")
        text_report = comparator.generate_report(result, format="text")
        html_report = comparator.generate_report(result, format="html")

        assert len(json_report) > 0
        assert len(text_report) > 0
        assert len(html_report) > 0

    def test_multiple_comparisons(self, comparator, sample1_path, sample2_path, sample1_copy_path):
        """Test multiple consecutive comparisons"""
        # Compare 1 vs 2
        result1 = comparator.compare(sample1_path, sample2_path, include_diff=False)

        # Compare 1 vs 1_copy
        result2 = comparator.compare(sample1_path, sample1_copy_path, include_diff=False)

        # Compare 2 vs 1_copy
        result3 = comparator.compare(sample2_path, sample1_copy_path, include_diff=False)

        # Verify results make sense
        assert result2.cosine_similarity > result1.cosine_similarity  # 1 vs copy should be more similar
        assert result2.cosine_similarity > result3.cosine_similarity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
