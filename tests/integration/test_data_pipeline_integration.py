"""
Data Pipeline Integration Tests

Tests ETL (Extract, Transform, Load) pipelines:
- Data ingestion from multiple sources
- Data transformation & cleaning
- Data validation & quality checks
- Data loading to destinations
- Pipeline orchestration
"""

import pytest
import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestETLPipelineIntegration:
    """Integration tests for ETL pipelines"""

    def test_complete_etl_workflow(self):
        """Test complete ETL pipeline from extraction to loading"""
        # EXTRACT
        raw_data = [
            {'id': '1', 'name': 'John Doe', 'email': 'john@example.com', 'age': '30'},
            {'id': '2', 'name': 'Jane Smith', 'email': 'JANE@EXAMPLE.COM', 'age': '25'},
            {'id': '3', 'name': '', 'email': 'invalid-email', 'age': 'unknown'},  # Bad data
        ]

        # TRANSFORM
        transformed_data = []
        for record in raw_data:
            # Data cleaning
            if not record.get('name') or not record.get('email'):
                continue  # Skip invalid records

            # Normalize email
            email = record['email'].lower().strip()

            # Validate email format
            if '@' not in email or '.' not in email:
                continue

            # Convert age to integer
            try:
                age = int(record['age'])
            except ValueError:
                continue

            # Create transformed record
            transformed = {
                'id': record['id'],
                'name': record['name'].strip(),
                'email': email,
                'age': age,
                'processed_at': datetime.now().isoformat()
            }
            transformed_data.append(transformed)

        # LOAD
        destination_db = {}
        for record in transformed_data:
            destination_db[record['id']] = record

        # VALIDATE
        assert len(destination_db) == 2  # Only 2 valid records
        assert '1' in destination_db
        assert '2' in destination_db
        assert '3' not in destination_db  # Invalid record excluded

        # Verify transformations
        assert destination_db['2']['email'] == 'jane@example.com'  # Lowercased

    def test_incremental_data_pipeline(self):
        """Test incremental data loading pipeline"""
        # Simulated state tracking
        pipeline_state = {'last_processed_id': 0}

        # Source data
        source_data = [
            {'id': 1, 'data': 'item_1', 'timestamp': '2024-01-01T10:00:00'},
            {'id': 2, 'data': 'item_2', 'timestamp': '2024-01-01T11:00:00'},
            {'id': 3, 'data': 'item_3', 'timestamp': '2024-01-01T12:00:00'},
            {'id': 4, 'data': 'item_4', 'timestamp': '2024-01-01T13:00:00'},
        ]

        def process_incremental_batch():
            """Process only new records since last run"""
            last_id = pipeline_state['last_processed_id']
            new_records = [r for r in source_data if r['id'] > last_id]

            # Process new records
            processed = []
            for record in new_records:
                processed.append({
                    **record,
                    'processed': True
                })

            # Update state
            if new_records:
                pipeline_state['last_processed_id'] = max(r['id'] for r in new_records)

            return processed

        # First run - process all
        batch1 = process_incremental_batch()
        assert len(batch1) == 4
        assert pipeline_state['last_processed_id'] == 4

        # Second run - no new data
        batch2 = process_incremental_batch()
        assert len(batch2) == 0

        # Add new data
        source_data.extend([
            {'id': 5, 'data': 'item_5', 'timestamp': '2024-01-01T14:00:00'},
            {'id': 6, 'data': 'item_6', 'timestamp': '2024-01-01T15:00:00'},
        ])

        # Third run - process only new records
        batch3 = process_incremental_batch()
        assert len(batch3) == 2
        assert pipeline_state['last_processed_id'] == 6

    def test_data_quality_pipeline(self):
        """Test data quality checks in pipeline"""
        def validate_record(record):
            """Validate record quality"""
            errors = []

            # Required fields
            required_fields = ['id', 'name', 'email']
            for field in required_fields:
                if field not in record or not record[field]:
                    errors.append(f"Missing required field: {field}")

            # Email format
            if 'email' in record:
                email = record['email']
                if '@' not in email or '.' not in email.split('@')[-1]:
                    errors.append("Invalid email format")

            # Age range
            if 'age' in record:
                try:
                    age = int(record['age'])
                    if age < 0 or age > 150:
                        errors.append("Age out of valid range")
                except (ValueError, TypeError):
                    errors.append("Age must be a number")

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'record': record
            }

        # Test data with various quality issues
        test_records = [
            {'id': '1', 'name': 'Valid User', 'email': 'valid@example.com', 'age': '30'},
            {'id': '2', 'name': '', 'email': 'no-name@example.com', 'age': '25'},  # Missing name
            {'id': '3', 'name': 'Bad Email', 'email': 'invalid-email', 'age': '35'},  # Bad email
            {'id': '4', 'name': 'Old Person', 'email': 'old@example.com', 'age': '200'},  # Invalid age
        ]

        # Validate all records
        validation_results = [validate_record(r) for r in test_records]

        # Check validation results
        assert validation_results[0]['valid'] is True
        assert validation_results[1]['valid'] is False  # Missing name
        assert validation_results[2]['valid'] is False  # Bad email
        assert validation_results[3]['valid'] is False  # Invalid age

        # Filter valid records
        valid_records = [r['record'] for r in validation_results if r['valid']]
        assert len(valid_records) == 1


class TestDataTransformationIntegration:
    """Integration tests for data transformations"""

    def test_data_normalization_pipeline(self):
        """Test data normalization transformations"""
        raw_data = [
            {'name': 'John DOE', 'country': 'usa', 'zip': '12345'},
            {'name': 'jane smith', 'country': 'USA', 'zip': '67890'},
            {'name': 'Bob JOHNSON', 'country': 'United States', 'zip': '11111'},
        ]

        def normalize_data(records):
            """Normalize data to consistent format"""
            normalized = []

            # Country code mapping
            country_map = {
                'usa': 'US',
                'united states': 'US',
                'us': 'US'
            }

            for record in records:
                # Title case for names
                name = record['name'].title()

                # Normalize country
                country = country_map.get(record['country'].lower(), record['country'].upper())

                # Ensure 5-digit zip
                zip_code = record['zip'].zfill(5)

                normalized.append({
                    'name': name,
                    'country': country,
                    'zip': zip_code
                })

            return normalized

        # Apply normalization
        normalized = normalize_data(raw_data)

        # Verify normalization
        assert all(r['name'][0].isupper() for r in normalized)  # Title case
        assert all(r['country'] == 'US' for r in normalized)  # Consistent country code
        assert all(len(r['zip']) == 5 for r in normalized)  # 5-digit zip

    def test_data_enrichment_pipeline(self):
        """Test data enrichment workflow"""
        # Original data
        users = [
            {'id': 'user_1', 'email': 'john@example.com'},
            {'id': 'user_2', 'email': 'jane@example.com'}
        ]

        # Enrichment sources (simulated external APIs)
        profile_data = {
            'user_1': {'name': 'John Doe', 'location': 'New York'},
            'user_2': {'name': 'Jane Smith', 'location': 'San Francisco'}
        }

        activity_data = {
            'user_1': {'last_login': '2024-01-15', 'login_count': 42},
            'user_2': {'last_login': '2024-01-20', 'login_count': 38}
        }

        def enrich_user_data(users):
            """Enrich user data from multiple sources"""
            enriched = []

            for user in users:
                user_id = user['id']

                # Merge data from all sources
                enriched_user = {
                    **user,
                    **profile_data.get(user_id, {}),
                    **activity_data.get(user_id, {})
                }

                enriched.append(enriched_user)

            return enriched

        # Apply enrichment
        enriched_users = enrich_user_data(users)

        # Verify enrichment
        assert len(enriched_users) == 2
        assert 'name' in enriched_users[0]
        assert 'location' in enriched_users[0]
        assert 'last_login' in enriched_users[0]
        assert 'login_count' in enriched_users[0]

    def test_data_aggregation_pipeline(self):
        """Test data aggregation transformations"""
        # Transaction data
        transactions = [
            {'user_id': 'user_1', 'amount': 100, 'date': '2024-01-01'},
            {'user_id': 'user_1', 'amount': 200, 'date': '2024-01-02'},
            {'user_id': 'user_2', 'amount': 150, 'date': '2024-01-01'},
            {'user_id': 'user_1', 'amount': 50, 'date': '2024-01-03'},
            {'user_id': 'user_2', 'amount': 300, 'date': '2024-01-02'},
        ]

        def aggregate_by_user(transactions):
            """Aggregate transactions by user"""
            aggregated = {}

            for txn in transactions:
                user_id = txn['user_id']

                if user_id not in aggregated:
                    aggregated[user_id] = {
                        'user_id': user_id,
                        'total_amount': 0,
                        'transaction_count': 0,
                        'transactions': []
                    }

                aggregated[user_id]['total_amount'] += txn['amount']
                aggregated[user_id]['transaction_count'] += 1
                aggregated[user_id]['transactions'].append(txn)

            # Calculate averages
            for user_id in aggregated:
                count = aggregated[user_id]['transaction_count']
                total = aggregated[user_id]['total_amount']
                aggregated[user_id]['average_amount'] = total / count if count > 0 else 0

            return list(aggregated.values())

        # Apply aggregation
        aggregated = aggregate_by_user(transactions)

        # Verify aggregation
        user1_agg = next(a for a in aggregated if a['user_id'] == 'user_1')
        assert user1_agg['total_amount'] == 350  # 100 + 200 + 50
        assert user1_agg['transaction_count'] == 3
        assert user1_agg['average_amount'] == 350 / 3

        user2_agg = next(a for a in aggregated if a['user_id'] == 'user_2')
        assert user2_agg['total_amount'] == 450  # 150 + 300
        assert user2_agg['transaction_count'] == 2


class TestDataPipelineOrchestration:
    """Integration tests for pipeline orchestration"""

    def test_multi_stage_pipeline(self):
        """Test multi-stage data pipeline"""
        # Stage 1: Extract
        def extract_data():
            return [
                {'id': 1, 'value': '100'},
                {'id': 2, 'value': '200'},
                {'id': 3, 'value': 'invalid'},
            ]

        # Stage 2: Validate
        def validate_data(records):
            valid = []
            for record in records:
                try:
                    int(record['value'])
                    valid.append(record)
                except ValueError:
                    pass
            return valid

        # Stage 3: Transform
        def transform_data(records):
            transformed = []
            for record in records:
                transformed.append({
                    'id': record['id'],
                    'value': int(record['value']),
                    'doubled': int(record['value']) * 2
                })
            return transformed

        # Stage 4: Load
        def load_data(records):
            return {r['id']: r for r in records}

        # Execute pipeline
        data = extract_data()
        data = validate_data(data)
        data = transform_data(data)
        result = load_data(data)

        # Verify pipeline execution
        assert len(result) == 2  # Invalid record filtered out
        assert result[1]['doubled'] == 200
        assert result[2]['doubled'] == 400

    def test_parallel_pipeline_execution(self):
        """Test parallel pipeline execution"""
        # Data batches
        batch1 = [{'id': 1, 'value': 'A'}, {'id': 2, 'value': 'B'}]
        batch2 = [{'id': 3, 'value': 'C'}, {'id': 4, 'value': 'D'}]
        batch3 = [{'id': 5, 'value': 'E'}, {'id': 6, 'value': 'F'}]

        def process_batch(batch):
            """Process a single batch"""
            return [{'id': r['id'], 'processed': r['value'].lower()} for r in batch]

        # Process batches (simulated parallel execution)
        results = []
        for batch in [batch1, batch2, batch3]:
            results.extend(process_batch(batch))

        # Verify all batches processed
        assert len(results) == 6
        assert all('processed' in r for r in results)

    def test_pipeline_error_handling(self):
        """Test pipeline error handling and recovery"""
        # Simulated pipeline state
        pipeline_state = {
            'failed_records': [],
            'success_count': 0,
            'error_count': 0
        }

        def process_with_error_handling(record):
            """Process record with error handling"""
            try:
                # Simulate processing that might fail
                if record.get('id') == 3:
                    raise ValueError("Simulated processing error")

                # Process successfully
                result = {
                    **record,
                    'processed': True
                }
                pipeline_state['success_count'] += 1
                return result

            except Exception as e:
                # Log error and continue
                pipeline_state['error_count'] += 1
                pipeline_state['failed_records'].append({
                    'record': record,
                    'error': str(e)
                })
                return None

        # Process records
        records = [
            {'id': 1, 'data': 'value1'},
            {'id': 2, 'data': 'value2'},
            {'id': 3, 'data': 'value3'},  # Will fail
            {'id': 4, 'data': 'value4'},
        ]

        results = []
        for record in records:
            result = process_with_error_handling(record)
            if result:
                results.append(result)

        # Verify error handling
        assert pipeline_state['success_count'] == 3
        assert pipeline_state['error_count'] == 1
        assert len(pipeline_state['failed_records']) == 1
        assert len(results) == 3  # Failed record excluded


class TestDataPipelineMonitoring:
    """Integration tests for pipeline monitoring"""

    def test_pipeline_metrics_collection(self):
        """Test collection of pipeline metrics"""
        metrics = {
            'records_processed': 0,
            'records_failed': 0,
            'processing_time': 0,
            'stages': {}
        }

        def process_with_metrics(records, stage_name):
            """Process records while collecting metrics"""
            import time

            start_time = time.time()

            processed = []
            failed = 0

            for record in records:
                try:
                    # Simulate processing
                    processed.append({**record, 'processed': True})
                    metrics['records_processed'] += 1
                except Exception:
                    failed += 1
                    metrics['records_failed'] += 1

            elapsed = time.time() - start_time

            # Record stage metrics
            metrics['stages'][stage_name] = {
                'processed': len(processed),
                'failed': failed,
                'time': elapsed
            }

            metrics['processing_time'] += elapsed

            return processed

        # Execute pipeline with metrics
        data = [{'id': i} for i in range(100)]
        data = process_with_metrics(data, 'stage_1')
        data = process_with_metrics(data, 'stage_2')

        # Verify metrics collected
        assert metrics['records_processed'] == 200  # 100 per stage
        assert 'stage_1' in metrics['stages']
        assert 'stage_2' in metrics['stages']
        assert metrics['processing_time'] > 0

    def test_pipeline_health_checks(self):
        """Test pipeline health monitoring"""
        def check_pipeline_health(pipeline_state):
            """Check pipeline health status"""
            health = {
                'status': 'healthy',
                'issues': []
            }

            # Check success rate
            total = pipeline_state['success'] + pipeline_state['failed']
            if total > 0:
                success_rate = pipeline_state['success'] / total
                if success_rate < 0.95:
                    health['status'] = 'degraded'
                    health['issues'].append(f"Low success rate: {success_rate:.2%}")

            # Check processing time
            if pipeline_state['avg_processing_time'] > 1.0:
                health['status'] = 'degraded'
                health['issues'].append("High processing time")

            # Check queue depth
            if pipeline_state['queue_depth'] > 1000:
                health['status'] = 'unhealthy'
                health['issues'].append("Queue backlog")

            return health

        # Test different states
        # Healthy state
        healthy_state = {
            'success': 950,
            'failed': 50,
            'avg_processing_time': 0.5,
            'queue_depth': 100
        }
        health = check_pipeline_health(healthy_state)
        assert health['status'] == 'healthy'

        # Degraded state (low success rate)
        degraded_state = {
            'success': 850,
            'failed': 150,
            'avg_processing_time': 0.5,
            'queue_depth': 100
        }
        health = check_pipeline_health(degraded_state)
        assert health['status'] == 'degraded'
        assert len(health['issues']) > 0

        # Unhealthy state (queue backlog)
        unhealthy_state = {
            'success': 900,
            'failed': 100,
            'avg_processing_time': 0.5,
            'queue_depth': 2000
        }
        health = check_pipeline_health(unhealthy_state)
        assert health['status'] == 'unhealthy'


# Run with: pytest tests/integration/test_data_pipeline_integration.py -v
