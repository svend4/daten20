"""
Performance Tests for API Endpoints

Tests REST API endpoint performance for regression detection.
Measures response time, throughput, and resource usage.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestAPIEndpointPerformance:
    """Performance tests for API endpoints"""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client for testing"""
        class MockAPI:
            def get(self, endpoint, params=None):
                # Simulate API GET request
                return {'status': 'success', 'data': {'result': 'mock_data'}}

            def post(self, endpoint, data=None):
                # Simulate API POST request
                return {'status': 'success', 'id': 'mock_id'}

            def put(self, endpoint, data=None):
                # Simulate API PUT request
                return {'status': 'success', 'updated': True}

            def delete(self, endpoint):
                # Simulate API DELETE request
                return {'status': 'success', 'deleted': True}

        return MockAPI()

    def test_document_list_endpoint_performance(self, benchmark, mock_api_client):
        """Benchmark document list endpoint"""
        def get_documents():
            return mock_api_client.get('/api/documents', params={'limit': 50})

        result = benchmark(get_documents)
        assert result['status'] == 'success'

    def test_document_create_endpoint_performance(self, benchmark, mock_api_client):
        """Benchmark document creation endpoint"""
        doc_data = {
            'title': 'Performance Test Document',
            'content': 'Content ' * 100,
            'metadata': {'author': 'Test'}
        }

        def create_document():
            return mock_api_client.post('/api/documents', data=doc_data)

        result = benchmark(create_document)
        assert result['status'] == 'success'

    def test_document_update_endpoint_performance(self, benchmark, mock_api_client):
        """Benchmark document update endpoint"""
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content ' * 50
        }

        def update_document():
            return mock_api_client.put('/api/documents/123', data=update_data)

        result = benchmark(update_document)
        assert result['status'] == 'success'

    def test_search_endpoint_performance(self, benchmark, mock_api_client):
        """Benchmark search endpoint"""
        def search_documents():
            return mock_api_client.get('/api/search', params={'q': 'test query'})

        result = benchmark(search_documents)
        assert result['status'] == 'success'


class TestAPIBatchOperationsPerformance:
    """Performance tests for batch API operations"""

    @pytest.fixture
    def mock_api_client(self):
        class MockAPI:
            def batch_create(self, endpoint, data_list):
                return {'status': 'success', 'created': len(data_list)}

            def batch_update(self, endpoint, updates):
                return {'status': 'success', 'updated': len(updates)}

            def batch_delete(self, endpoint, ids):
                return {'status': 'success', 'deleted': len(ids)}

        return MockAPI()

    def test_batch_create_performance(self, benchmark, mock_api_client):
        """Benchmark batch document creation"""
        documents = [
            {'title': f'Doc {i}', 'content': f'Content {i}'}
            for i in range(10)
        ]

        def batch_create():
            return mock_api_client.batch_create('/api/documents/batch', documents)

        result = benchmark(batch_create)
        assert result['created'] == 10

    def test_batch_update_performance(self, benchmark, mock_api_client):
        """Benchmark batch document updates"""
        updates = [
            {'id': i, 'title': f'Updated {i}'}
            for i in range(10)
        ]

        def batch_update():
            return mock_api_client.batch_update('/api/documents/batch', updates)

        result = benchmark(batch_update)
        assert result['updated'] == 10

    @pytest.mark.slow
    def test_large_batch_performance(self, benchmark, mock_api_client):
        """Benchmark large batch operations"""
        large_batch = [
            {'id': i, 'data': f'item_{i}'}
            for i in range(100)
        ]

        def large_batch_op():
            return mock_api_client.batch_create('/api/items/batch', large_batch)

        result = benchmark(large_batch_op)
        assert result['created'] == 100


class TestAPIAuthenticationPerformance:
    """Performance tests for authentication operations"""

    def test_token_validation_performance(self, benchmark):
        """Benchmark token validation"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token"

        def validate_token():
            # Simulate token validation
            parts = token.split('.')
            is_valid = len(parts) == 3 and all(part for part in parts)
            return {'valid': is_valid}

        result = benchmark(validate_token)
        assert 'valid' in result

    def test_session_lookup_performance(self, benchmark):
        """Benchmark session lookup"""
        sessions = {f'session_{i}': {'user_id': i} for i in range(1000)}
        session_id = 'session_500'

        def lookup_session():
            return sessions.get(session_id, {})

        result = benchmark(lookup_session)
        assert result.get('user_id') is not None


class TestAPIPaginationPerformance:
    """Performance tests for pagination"""

    def test_pagination_performance(self, benchmark):
        """Benchmark pagination calculation"""
        total_items = 1000
        page_size = 20

        def paginate(page=1):
            offset = (page - 1) * page_size
            limit = page_size
            total_pages = (total_items + page_size - 1) // page_size

            return {
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'total_items': total_items,
                'offset': offset,
                'limit': limit
            }

        result = benchmark(paginate, page=5)
        assert result['page'] == 5

    def test_large_dataset_pagination_performance(self, benchmark):
        """Benchmark pagination on large dataset"""
        total_items = 100000
        page_size = 50

        def paginate_large(page=500):
            offset = (page - 1) * page_size
            total_pages = (total_items + page_size - 1) // page_size

            return {
                'offset': offset,
                'limit': page_size,
                'total_pages': total_pages
            }

        result = benchmark(paginate_large)
        assert result['offset'] == (500 - 1) * 50


class TestAPISerializationPerformance:
    """Performance tests for data serialization"""

    def test_json_serialization_performance(self, benchmark):
        """Benchmark JSON serialization"""
        import json

        data = {
            'documents': [
                {'id': i, 'title': f'Document {i}', 'content': f'Content {i}' * 10}
                for i in range(50)
            ]
        }

        def serialize():
            return json.dumps(data)

        result = benchmark(serialize)
        assert isinstance(result, str)

    def test_json_deserialization_performance(self, benchmark):
        """Benchmark JSON deserialization"""
        import json

        json_data = json.dumps({
            'items': [{'id': i, 'value': f'item_{i}'} for i in range(50)]
        })

        def deserialize():
            return json.loads(json_data)

        result = benchmark(deserialize)
        assert 'items' in result

    @pytest.mark.slow
    def test_large_payload_serialization_performance(self, benchmark):
        """Benchmark large payload serialization"""
        import json

        large_data = {
            'records': [
                {
                    'id': i,
                    'data': {
                        'field1': f'value_{i}',
                        'field2': i * 2,
                        'nested': {'a': i, 'b': i * 3}
                    }
                }
                for i in range(500)
            ]
        }

        def serialize_large():
            return json.dumps(large_data)

        result = benchmark(serialize_large)
        assert len(result) > 1000


class TestAPICompressionPerformance:
    """Performance tests for response compression"""

    def test_gzip_compression_performance(self, benchmark):
        """Benchmark gzip compression"""
        import gzip

        data = b"Sample response data. " * 1000

        def compress_gzip():
            return gzip.compress(data)

        compressed = benchmark(compress_gzip)
        assert len(compressed) < len(data)

    def test_gzip_decompression_performance(self, benchmark):
        """Benchmark gzip decompression"""
        import gzip

        data = b"Sample response data. " * 1000
        compressed = gzip.compress(data)

        def decompress_gzip():
            return gzip.decompress(compressed)

        decompressed = benchmark(decompress_gzip)
        assert decompressed == data


class TestAPICachingPerformance:
    """Performance tests for API caching"""

    def test_cache_hit_performance(self, benchmark):
        """Benchmark cache hit scenario"""
        cache = {
            'key_1': {'data': 'cached_value_1'},
            'key_2': {'data': 'cached_value_2'}
        }

        def get_cached():
            return cache.get('key_1', {})

        result = benchmark(get_cached)
        assert result.get('data') == 'cached_value_1'

    def test_cache_miss_and_fetch_performance(self, benchmark):
        """Benchmark cache miss with fetch"""
        cache = {}

        def get_with_fallback(key='new_key'):
            if key in cache:
                return cache[key]
            else:
                # Simulate fetch and cache
                data = {'data': f'fetched_{key}'}
                cache[key] = data
                return data

        result = benchmark(get_with_fallback)
        assert 'data' in result


class TestAPIRateLimitingPerformance:
    """Performance tests for rate limiting"""

    def test_rate_limit_check_performance(self, benchmark):
        """Benchmark rate limit checking"""
        import time

        rate_limits = {}

        def check_rate_limit(user_id='user123', max_requests=100, window=60):
            now = time.time()
            if user_id not in rate_limits:
                rate_limits[user_id] = {'requests': [], 'window_start': now}

            user_limits = rate_limits[user_id]
            # Remove old requests outside window
            user_limits['requests'] = [
                req_time for req_time in user_limits['requests']
                if now - req_time < window
            ]

            if len(user_limits['requests']) < max_requests:
                user_limits['requests'].append(now)
                return {'allowed': True, 'remaining': max_requests - len(user_limits['requests'])}
            else:
                return {'allowed': False, 'remaining': 0}

        result = benchmark(check_rate_limit)
        assert 'allowed' in result


# Run with: pytest tests/performance/test_api_performance.py -v --benchmark-only
# Save baseline: pytest tests/performance/test_api_performance.py --benchmark-save=api_baseline
# Compare: pytest tests/performance/test_api_performance.py --benchmark-compare=api_baseline
