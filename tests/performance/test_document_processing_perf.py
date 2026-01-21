"""
Performance Tests for Document Processing

Tests document processing operations for performance regressions.
Uses pytest-benchmark to track metrics over time.
"""

import pytest
import sys
from pathlib import Path
from io import BytesIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestDocumentProcessingPerformance:
    """Performance tests for document processing operations"""

    @pytest.fixture
    def sample_text_content(self):
        """Generate sample text content for testing"""
        return "Sample document content. " * 1000

    @pytest.fixture
    def sample_pdf_content(self):
        """Generate sample PDF bytes"""
        # Minimal PDF structure
        return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF"

    def test_text_extraction_performance(self, benchmark, sample_text_content):
        """Benchmark text extraction from string"""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        def extract_text():
            return processor.extract_text_from_string(sample_text_content)

        result = benchmark(extract_text)
        assert len(result) > 0

    def test_document_validation_performance(self, benchmark):
        """Benchmark document validation"""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        doc_data = {
            'title': 'Test Document',
            'content': 'Content ' * 100,
            'metadata': {'author': 'Test Author'}
        }

        def validate_doc():
            return processor.validate_document(doc_data)

        result = benchmark(validate_doc)
        assert result is True or isinstance(result, dict)

    def test_metadata_extraction_performance(self, benchmark):
        """Benchmark metadata extraction"""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        doc_content = "Title: Test\nAuthor: John Doe\nDate: 2024-01-01\n" + "Content. " * 500

        def extract_metadata():
            return processor.extract_metadata(doc_content)

        result = benchmark(extract_metadata)
        assert result is not None

    def test_batch_processing_performance(self, benchmark):
        """Benchmark batch document processing"""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        documents = [
            {'id': i, 'content': f'Document {i} content ' * 50}
            for i in range(10)
        ]

        def process_batch():
            results = []
            for doc in documents:
                results.append(processor.process_document(doc))
            return results

        results = benchmark(process_batch)
        assert len(results) == 10

    @pytest.mark.slow
    def test_large_document_processing_performance(self, benchmark):
        """Benchmark large document processing"""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        large_content = "Large document content. " * 10000  # ~250KB

        def process_large():
            return processor.process_document({'content': large_content})

        result = benchmark(process_large)
        assert result is not None


class TestPDFProcessingPerformance:
    """Performance tests for PDF processing"""

    def test_pdf_text_extraction_performance(self, benchmark):
        """Benchmark PDF text extraction (mocked)"""
        # Mock PDF processing since we don't have real PDFs in tests
        def extract_pdf_text():
            # Simulate PDF text extraction work
            text = ""
            for i in range(1000):
                text += f"Page {i % 10} content. "
            return text

        result = benchmark(extract_pdf_text)
        assert len(result) > 0

    def test_pdf_metadata_extraction_performance(self, benchmark):
        """Benchmark PDF metadata extraction"""
        def extract_pdf_metadata():
            # Simulate metadata extraction
            metadata = {
                'title': 'Test Document',
                'author': 'Test Author',
                'pages': 10,
                'created': '2024-01-01'
            }
            # Simulate processing work
            for _ in range(100):
                metadata['processed'] = True
            return metadata

        result = benchmark(extract_pdf_metadata)
        assert 'title' in result


class TestSearchPerformance:
    """Performance tests for search operations"""

    def test_full_text_search_performance(self, benchmark):
        """Benchmark full-text search"""
        # Create sample documents
        documents = [
            {'id': i, 'content': f'Document {i} with searchable content about topic {i % 5}'}
            for i in range(100)
        ]

        def search_documents(query='topic'):
            results = []
            for doc in documents:
                if query.lower() in doc['content'].lower():
                    results.append(doc)
            return results

        results = benchmark(search_documents)
        assert len(results) > 0

    def test_fuzzy_search_performance(self, benchmark):
        """Benchmark fuzzy search"""
        documents = [
            {'id': i, 'title': f'Document Title {i}'}
            for i in range(50)
        ]

        def fuzzy_search(query='Docment'):
            # Simple fuzzy matching simulation
            results = []
            for doc in documents:
                title_lower = doc['title'].lower()
                query_lower = query.lower()
                # Simple character overlap check
                overlap = sum(1 for c in query_lower if c in title_lower)
                if overlap >= len(query_lower) * 0.7:
                    results.append(doc)
            return results

        results = benchmark(fuzzy_search)
        assert isinstance(results, list)

    @pytest.mark.slow
    def test_indexed_search_performance(self, benchmark):
        """Benchmark indexed search (simulated)"""
        # Simulate indexed search structure
        index = {
            'topic': [1, 5, 10, 15, 20],
            'document': list(range(100)),
            'content': list(range(50, 100))
        }

        def indexed_search(term='topic'):
            return index.get(term, [])

        results = benchmark(indexed_search)
        assert isinstance(results, list)


class TestCachingPerformance:
    """Performance tests for caching mechanisms"""

    def test_cache_write_performance(self, benchmark):
        """Benchmark cache write operations"""
        cache = {}

        def write_to_cache():
            for i in range(100):
                cache[f'key_{i}'] = f'value_{i}' * 10
            return len(cache)

        result = benchmark(write_to_cache)
        assert result == 100

    def test_cache_read_performance(self, benchmark):
        """Benchmark cache read operations"""
        cache = {f'key_{i}': f'value_{i}' for i in range(100)}

        def read_from_cache():
            results = []
            for i in range(100):
                results.append(cache.get(f'key_{i}'))
            return results

        results = benchmark(read_from_cache)
        assert len(results) == 100

    def test_cache_hit_rate_performance(self, benchmark):
        """Benchmark cache with realistic hit/miss pattern"""
        cache = {f'key_{i}': f'value_{i}' for i in range(50)}

        def cache_access_pattern():
            hits = 0
            misses = 0
            for i in range(100):
                key = f'key_{i % 60}'  # Some hits, some misses
                if key in cache:
                    hits += 1
                    value = cache[key]
                else:
                    misses += 1
                    cache[key] = f'new_value_{i}'
            return {'hits': hits, 'misses': misses}

        result = benchmark(cache_access_pattern)
        assert 'hits' in result and 'misses' in result


# Run with: pytest tests/performance/test_document_processing_perf.py -v --benchmark-only
# Compare: pytest tests/performance/test_document_processing_perf.py --benchmark-compare
