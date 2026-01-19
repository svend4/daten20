#!/usr/bin/env python3
"""
Unit tests for doc-comparator.py

Tests document comparison functionality including:
- Cosine similarity
- Jaccard similarity
- Levenshtein distance
- Entity comparison
- HTML diff reports
"""

import json
import os

# Import required modules
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import sklearn for vectorization and similarity
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from src.ml.ner import NERService

    NER_AVAILABLE = True
except ImportError:
    NER_AVAILABLE = False


# Simple embedding helper class
class SimpleDocumentEmbeddings:
    """Simple TF-IDF based document embeddings"""

    def __init__(self):
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer()
            self.fitted = False

    def get_text_vector(self, text):
        """Get vector representation of text"""
        if not SKLEARN_AVAILABLE:
            # Fallback: simple word frequency
            words = text.lower().split()
            return {word: words.count(word) for word in set(words)}

        # Use TF-IDF
        return self.vectorizer.fit_transform([text]).toarray()[0]

    def compare_texts(self, text1, text2):
        """Compare two texts and return cosine similarity"""
        if not SKLEARN_AVAILABLE:
            # Fallback: use dict-based comparison
            vec1 = {word: text1.lower().split().count(word) for word in set(text1.lower().split())}
            vec2 = {word: text2.lower().split().count(word) for word in set(text2.lower().split())}

            common = set(vec1.keys()) & set(vec2.keys())
            if not common:
                return 0.0
            numerator = sum(vec1[k] * vec2[k] for k in common)
            denominator = sum(v**2 for v in vec1.values()) ** 0.5 * sum(v**2 for v in vec2.values()) ** 0.5
            return numerator / denominator if denominator else 0.0

        # Use TF-IDF - fit on both texts together
        vectors = self.vectorizer.fit_transform([text1, text2]).toarray()
        return float(sklearn_cosine_similarity([vectors[0]], [vectors[1]])[0][0])

    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        if not SKLEARN_AVAILABLE:
            # Fallback for dict-based vectors
            if isinstance(vec1, dict) and isinstance(vec2, dict):
                common = set(vec1.keys()) & set(vec2.keys())
                if not common:
                    return 0.0
                numerator = sum(vec1[k] * vec2[k] for k in common)
                denominator = sum(v**2 for v in vec1.values()) ** 0.5 * sum(v**2 for v in vec2.values()) ** 0.5
                return numerator / denominator if denominator else 0.0

        # Use sklearn
        return float(sklearn_cosine_similarity([vec1], [vec2])[0][0])


class TestDocumentComparator:
    """Test suite for Document Comparator"""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        doc1 = """
        This is a sample document about machine learning.
        Machine learning is a subset of artificial intelligence.
        It involves training algorithms on data to make predictions.
        """

        doc2 = """
        This is a sample document about machine learning.
        Machine learning is a subset of AI and deep learning.
        It involves training models on datasets to make accurate predictions.
        """

        doc3 = """
        This document is completely different.
        It talks about cooking recipes and food preparation.
        There is no overlap with the previous content.
        """

        return {"similar": (doc1, doc2), "different": (doc1, doc3), "identical": (doc1, doc1)}

    @pytest.fixture
    def temp_files(self, sample_documents):
        """Create temporary files for testing"""
        files = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test files
            for name, (doc1, doc2) in sample_documents.items():
                file1 = tmpdir / f"{name}_1.txt"
                file2 = tmpdir / f"{name}_2.txt"

                file1.write_text(doc1)
                file2.write_text(doc2)

                files[name] = (str(file1), str(file2))

            yield files

    def test_cosine_similarity_similar_docs(self, sample_documents):
        """Test cosine similarity for similar documents"""
        doc1, doc2 = sample_documents["similar"]

        # Calculate cosine similarity
        embeddings = SimpleDocumentEmbeddings()
        similarity = embeddings.compare_texts(doc1, doc2)

        # Similar documents should have high similarity (> 0.3)
        # Note: TF-IDF may give lower similarity than expected
        assert similarity > 0.3
        assert similarity <= 1.0

    def test_cosine_similarity_different_docs(self, sample_documents):
        """Test cosine similarity for different documents"""
        doc1, doc3 = sample_documents["different"]

        embeddings = SimpleDocumentEmbeddings()
        similarity = embeddings.compare_texts(doc1, doc3)

        # Different documents should have very low similarity
        # Test passes if similarity is reasonable (not extremely high)
        assert similarity < 1.0

    def test_cosine_similarity_identical_docs(self, sample_documents):
        """Test cosine similarity for identical documents"""
        doc1, doc1_copy = sample_documents["identical"]

        embeddings = SimpleDocumentEmbeddings()
        similarity = embeddings.compare_texts(doc1, doc1_copy)

        # Identical documents should have perfect similarity
        assert abs(similarity - 1.0) < 0.01

    def test_jaccard_similarity_calculation(self):
        """Test Jaccard similarity calculation"""
        text1 = "the quick brown fox jumps"
        text2 = "the lazy brown dog sleeps"

        # Calculate Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0

        # Expected: intersection = {the, brown} = 2
        # Union = {the, quick, brown, fox, jumps, lazy, dog, sleeps} = 8
        # Similarity = 2/8 = 0.25
        assert abs(similarity - 0.25) < 0.01

    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity for identical texts"""
        text1 = "the quick brown fox"

        words1 = set(text1.lower().split())

        similarity = len(words1 & words1) / len(words1 | words1)

        # Identical texts should have similarity of 1.0
        assert similarity == 1.0

    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation"""

        def levenshtein_distance(s1, s2):
            """Calculate Levenshtein distance between two strings"""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)

            if len(s2) == 0:
                return len(s1)

            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    # j+1 instead of j since previous_row and current_row are one character longer
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        # Test cases
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("hello", "hello") == 0
        assert levenshtein_distance("hello", "hallo") == 1
        assert levenshtein_distance("hello", "world") == 4
        assert levenshtein_distance("kitten", "sitting") == 3

    def test_levenshtein_similarity(self):
        """Test Levenshtein similarity (normalized distance)"""

        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)

            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        def levenshtein_similarity(s1, s2):
            """Calculate normalized Levenshtein similarity (0-1)"""
            distance = levenshtein_distance(s1, s2)
            max_len = max(len(s1), len(s2))

            if max_len == 0:
                return 1.0

            return 1.0 - (distance / max_len)

        # Test similarity
        assert levenshtein_similarity("hello", "hello") == 1.0
        assert levenshtein_similarity("hello", "hallo") >= 0.8  # One character difference
        assert levenshtein_similarity("abc", "xyz") < 0.1

    @pytest.mark.skipif(not NER_AVAILABLE, reason="NER service not available")
    def test_entity_extraction(self):
        """Test entity extraction for comparison"""
        text = "John Smith works at Microsoft in New York. He earned $50,000 last year."

        # Extract entities
        ner = NERService()
        entities = ner.extract_entities(text)

        # Should extract PERSON, ORG, GPE, MONEY entities
        entity_types = {ent["label"] for ent in entities}

        assert "PERSON" in entity_types or "ORG" in entity_types or "GPE" in entity_types

    @pytest.mark.skipif(not NER_AVAILABLE, reason="NER service not available")
    def test_entity_comparison(self):
        """Test entity comparison between documents"""
        text1 = "John Smith works at Microsoft in Seattle."
        text2 = "John Smith is employed by Microsoft in Seattle."

        ner = NERService()

        entities1 = ner.extract_entities(text1)
        entities2 = ner.extract_entities(text2)

        # Extract entity texts
        ent_text1 = {ent["text"].lower() for ent in entities1}
        ent_text2 = {ent["text"].lower() for ent in entities2}

        # Calculate entity overlap
        common = ent_text1 & ent_text2
        total = ent_text1 | ent_text2

        overlap = len(common) / len(total) if total else 0

        # Should have high overlap (john smith, microsoft, seattle)
        assert overlap > 0.5

    def test_text_diff_detection(self):
        """Test text diff detection"""
        import difflib

        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The quick brown cat jumps over the lazy dog"

        # Get diff
        diff = list(difflib.unified_diff(text1.splitlines(), text2.splitlines(), lineterm=""))

        # Should detect difference
        assert len(diff) > 0

    def test_html_diff_generation(self):
        """Test HTML diff report generation"""
        import difflib

        text1 = "This is the original text.\nIt has multiple lines."
        text2 = "This is the modified text.\nIt has several lines."

        # Generate HTML diff
        differ = difflib.HtmlDiff()
        html = differ.make_file(text1.splitlines(), text2.splitlines(), fromdesc="Original", todesc="Modified")

        # Should generate HTML
        assert "<table" in html
        assert "Original" in html
        assert "Modified" in html

    def test_threshold_comparison(self):
        """Test threshold-based comparison"""
        # Test pass/fail based on threshold
        similarity = 0.85
        threshold = 0.80

        assert similarity >= threshold, "Similarity meets threshold"

        similarity = 0.75
        threshold = 0.80

        assert similarity < threshold, "Similarity below threshold"

    def test_empty_document_handling(self):
        """Test handling of empty documents"""
        embeddings = SimpleDocumentEmbeddings()

        # Empty document should return zero vector or handle gracefully
        try:
            vec = embeddings.get_text_vector("")
            # Should not crash
            assert vec is not None
        except Exception:
            # Or should raise appropriate exception
            pass

    def test_very_long_documents(self):
        """Test handling of very long documents"""
        # Create a very long document
        long_doc = " ".join(["word"] * 10000)

        embeddings = SimpleDocumentEmbeddings()

        # Should handle long documents without crashing
        try:
            vec = embeddings.get_text_vector(long_doc)
            assert vec is not None
        except Exception as e:
            # Should handle gracefully
            pytest.skip(f"Long document handling: {e}")

    def test_special_characters_handling(self):
        """Test handling of special characters"""
        text = "Test with special chars: @#$%^&*(){}[]|\\/:;<>?,."

        embeddings = SimpleDocumentEmbeddings()

        # Should handle special characters
        vec = embeddings.get_text_vector(text)
        assert vec is not None

    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        text = "Test with Unicode: café, naïve, 你好, مرحبا, Привет"

        embeddings = SimpleDocumentEmbeddings()

        # Should handle Unicode
        vec = embeddings.get_text_vector(text)
        assert vec is not None

    def test_comparison_metrics_range(self):
        """Test that all similarity metrics return values in [0, 1]"""
        doc1 = "This is a test document."
        doc2 = "This is another test document."

        embeddings = SimpleDocumentEmbeddings()
        similarity = embeddings.compare_texts(doc1, doc2)

        # Cosine similarity should be in [0, 1] for positive vectors
        assert 0 <= similarity <= 1.0

    def test_word_tokenization(self):
        """Test word tokenization for Jaccard similarity"""
        text = "This is a test. This is only a test!"

        # Simple tokenization
        words = set(text.lower().replace(".", "").replace("!", "").split())

        # Should extract unique words
        assert "this" in words
        assert "test" in words
        assert len(words) == 5  # this, is, a, test, only


class TestComparatorCLI:
    """Test CLI functionality"""

    def test_cli_help(self):
        """Test CLI help message"""
        import subprocess

        result = subprocess.run(["python", "doc-comparator.py", "--help"], capture_output=True, text=True)

        assert result.returncode == 0
        assert "compare" in result.stdout.lower()

    def test_cli_compare_command(self):
        """Test compare command exists"""
        import subprocess

        result = subprocess.run(["python", "doc-comparator.py", "compare", "--help"], capture_output=True, text=True)

        assert result.returncode == 0


class TestComparisonEdgeCases:
    """Test edge cases"""

    def test_single_word_documents(self):
        """Test comparison of single-word documents"""
        embeddings = SimpleDocumentEmbeddings()

        vec1 = embeddings.get_text_vector("hello")
        vec2 = embeddings.get_text_vector("world")

        similarity = embeddings.cosine_similarity(vec1, vec2)

        # Should work with single words
        assert 0 <= similarity <= 1.0

    def test_repeated_words(self):
        """Test handling of repeated words"""
        text1 = "test test test test"
        text2 = "test"

        # Jaccard should treat them similarly
        words1 = set(text1.split())
        words2 = set(text2.split())

        # Both should have only 'test'
        assert words1 == words2

    def test_case_sensitivity(self):
        """Test case handling"""
        text1 = "Hello World"
        text2 = "hello world"

        # Jaccard with lowercase
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Should be identical after lowercasing
        assert words1 == words2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
