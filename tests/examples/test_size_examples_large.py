"""
Примеры расширенных (large) тестов

Large тесты могут:
- Выполняться длительное время (> 5 минут)
- Использовать реальные внешние сервисы (с осторожностью)
- Тестировать полные end-to-end сценарии
- Быть недетерминированными
- Требовать специального окружения
"""

import pytest
import time
import os
from datetime import datetime

# Пометить весь модуль как large тесты
pytestmark = [pytest.mark.large, pytest.mark.e2e, pytest.mark.slow]


class TestCompleteDocumentLifecycle:
    """Примеры large тестов для полного жизненного цикла документа"""

    def test_document_upload_process_export_workflow(
        self, client, auth_headers, test_db, tmp_path
    ):
        """
        Test complete document workflow:
        Upload -> OCR -> AI Analysis -> Export -> Archive
        """
        # 1. Upload document
        with open('tests/fixtures/sample_docs/complex_document.pdf', 'rb') as f:
            upload_response = client.post(
                '/api/documents/upload',
                data={'file': (f, 'complex_document.pdf')},
                content_type='multipart/form-data',
                headers=auth_headers
            )

        assert upload_response.status_code == 201
        doc_id = upload_response.get_json()['document_id']

        # 2. Start OCR processing (long-running operation)
        ocr_response = client.post(
            f'/api/documents/{doc_id}/ocr',
            headers=auth_headers
        )
        assert ocr_response.status_code == 202

        # 3. Wait for OCR completion (may take several minutes)
        max_wait = 300  # 5 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_response = client.get(
                f'/api/documents/{doc_id}/status',
                headers=auth_headers
            )
            status = status_response.get_json()

            if status['ocr_status'] == 'completed':
                break
            elif status['ocr_status'] == 'failed':
                pytest.fail("OCR processing failed")

            time.sleep(5)  # Check every 5 seconds

        assert status['ocr_status'] == 'completed'

        # 4. Start AI analysis (another long-running operation)
        analysis_response = client.post(
            f'/api/documents/{doc_id}/analyze',
            headers=auth_headers
        )
        assert analysis_response.status_code == 202

        # 5. Wait for analysis completion
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status_response = client.get(
                f'/api/documents/{doc_id}/status',
                headers=auth_headers
            )
            status = status_response.get_json()

            if status['analysis_status'] == 'completed':
                break

            time.sleep(5)

        assert status['analysis_status'] == 'completed'

        # 6. Retrieve analysis results
        results_response = client.get(
            f'/api/documents/{doc_id}/analysis',
            headers=auth_headers
        )
        assert results_response.status_code == 200
        results = results_response.get_json()

        # Verify analysis results
        assert 'entities' in results
        assert 'sentiment' in results
        assert 'categories' in results
        assert 'summary' in results

        # 7. Export to multiple formats
        for export_format in ['pdf', 'docx', 'html', 'json']:
            export_response = client.get(
                f'/api/documents/{doc_id}/export?format={export_format}',
                headers=auth_headers
            )
            assert export_response.status_code == 200
            assert len(export_response.data) > 0

        # 8. Archive document
        archive_response = client.post(
            f'/api/documents/{doc_id}/archive',
            headers=auth_headers
        )
        assert archive_response.status_code == 200

        # 9. Verify final state
        final_response = client.get(
            f'/api/documents/{doc_id}',
            headers=auth_headers
        )
        final_doc = final_response.get_json()
        assert final_doc['status'] == 'archived'
        assert final_doc['archived_at'] is not None


class TestMultiUserCollaboration:
    """Примеры large тестов для совместной работы пользователей"""

    def test_concurrent_document_editing(
        self, client, test_db, create_test_users
    ):
        """
        Test multiple users editing same document concurrently
        """
        # Create 5 test users
        users = [create_test_users(f'user{i}') for i in range(5)]
        tokens = []

        # Login all users
        for user in users:
            response = client.post('/api/auth/login', json={
                'username': user.username,
                'password': 'password123'
            })
            tokens.append(response.get_json()['access_token'])

        # User 0 creates document
        headers_0 = {'Authorization': f'Bearer {tokens[0]}'}
        doc_response = client.post(
            '/api/documents/',
            headers=headers_0,
            json={'title': 'Shared Doc', 'content': 'Initial content'}
        )
        doc_id = doc_response.get_json()['document_id']

        # Share with all users
        for i in range(1, 5):
            share_response = client.post(
                f'/api/documents/{doc_id}/share',
                headers=headers_0,
                json={'user_id': users[i].id, 'permission': 'edit'}
            )
            assert share_response.status_code == 200

        # All users edit simultaneously
        import threading

        def edit_document(user_index, token):
            headers = {'Authorization': f'Bearer {token}'}
            for j in range(10):  # 10 edits per user
                client.patch(
                    f'/api/documents/{doc_id}',
                    headers=headers,
                    json={'content': f'Edit by user{user_index} #{j}'}
                )
                time.sleep(0.1)

        threads = []
        for i, token in enumerate(tokens):
            thread = threading.Thread(
                target=edit_document,
                args=(i, token)
            )
            threads.append(thread)
            thread.start()

        # Wait for all edits to complete
        for thread in threads:
            thread.join()

        # Verify document history
        history_response = client.get(
            f'/api/documents/{doc_id}/history',
            headers=headers_0
        )
        history = history_response.get_json()

        # Should have initial version + 50 edits (5 users * 10 edits)
        assert len(history['versions']) >= 50

        # Verify no data corruption
        final_response = client.get(
            f'/api/documents/{doc_id}',
            headers=headers_0
        )
        final_doc = final_response.get_json()
        assert final_doc['content'] is not None


class TestBatchProcessing:
    """Примеры large тестов для пакетной обработки"""

    def test_process_large_document_batch(
        self, client, auth_headers, test_db
    ):
        """
        Test processing 100+ documents in batch
        """
        num_documents = 100

        # 1. Upload batch of documents
        document_ids = []
        for i in range(num_documents):
            response = client.post(
                '/api/documents/upload',
                data={
                    'file': (
                        f'document_{i}.txt'.encode(),
                        f'Content of document {i}' * 100
                    )
                },
                headers=auth_headers
            )
            document_ids.append(response.get_json()['document_id'])

        assert len(document_ids) == num_documents

        # 2. Start batch processing
        batch_response = client.post(
            '/api/batch/process',
            headers=auth_headers,
            json={
                'document_ids': document_ids,
                'operations': ['ocr', 'analyze', 'categorize']
            }
        )
        batch_id = batch_response.get_json()['batch_id']

        # 3. Monitor batch progress
        max_wait = 1800  # 30 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_response = client.get(
                f'/api/batch/{batch_id}/status',
                headers=auth_headers
            )
            status = status_response.get_json()

            print(f"Batch progress: {status['completed']}/{status['total']}")

            if status['state'] == 'completed':
                break
            elif status['state'] == 'failed':
                pytest.fail(f"Batch processing failed: {status['error']}")

            time.sleep(10)  # Check every 10 seconds

        assert status['state'] == 'completed'
        assert status['completed'] == num_documents
        assert status['failed'] == 0

        # 4. Verify all documents processed
        for doc_id in document_ids:
            doc_response = client.get(
                f'/api/documents/{doc_id}',
                headers=auth_headers
            )
            doc = doc_response.get_json()
            assert doc['processing_status'] == 'completed'


class TestSystemStressAndLoad:
    """Примеры large тестов для нагрузочного тестирования"""

    def test_concurrent_user_load(self, client, test_db):
        """
        Simulate 50 concurrent users performing various operations
        """
        import concurrent.futures

        num_users = 50
        operations_per_user = 20

        def simulate_user(user_id):
            """Simulate one user's activity"""
            results = {
                'user_id': user_id,
                'successful': 0,
                'failed': 0
            }

            # Register
            reg_response = client.post('/api/auth/register', json={
                'username': f'loaduser{user_id}',
                'email': f'loaduser{user_id}@example.com',
                'password': 'Password123!'
            })

            if reg_response.status_code != 201:
                results['failed'] += 1
                return results

            # Login
            login_response = client.post('/api/auth/login', json={
                'username': f'loaduser{user_id}',
                'password': 'Password123!'
            })

            if login_response.status_code != 200:
                results['failed'] += 1
                return results

            token = login_response.get_json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}

            # Perform operations
            for _ in range(operations_per_user):
                # Create document
                doc_response = client.post(
                    '/api/documents/',
                    headers=headers,
                    json={'title': f'Doc by user{user_id}', 'content': 'Test'}
                )

                if doc_response.status_code == 201:
                    results['successful'] += 1

                    # Read document
                    doc_id = doc_response.get_json()['document_id']
                    get_response = client.get(
                        f'/api/documents/{doc_id}',
                        headers=headers
                    )

                    if get_response.status_code == 200:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                else:
                    results['failed'] += 1

                time.sleep(0.1)  # Small delay between operations

            return results

        # Execute concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [
                executor.submit(simulate_user, i)
                for i in range(num_users)
            ]

            all_results = [
                future.result()
                for future in concurrent.futures.as_completed(futures)
            ]

        # Analyze results
        total_successful = sum(r['successful'] for r in all_results)
        total_failed = sum(r['failed'] for r in all_results)

        print(f"\nLoad Test Results:")
        print(f"Total successful operations: {total_successful}")
        print(f"Total failed operations: {total_failed}")
        print(f"Success rate: {total_successful/(total_successful+total_failed)*100:.2f}%")

        # Assert acceptable failure rate (< 5%)
        failure_rate = total_failed / (total_successful + total_failed)
        assert failure_rate < 0.05, f"Failure rate too high: {failure_rate*100:.2f}%"

    def test_memory_leak_detection(self, client, auth_headers):
        """
        Test for memory leaks during extended operation
        """
        import psutil
        import gc

        process = psutil.Process()

        # Baseline memory
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform many operations
        num_iterations = 1000

        for i in range(num_iterations):
            # Create and delete documents
            response = client.post(
                '/api/documents/',
                headers=auth_headers,
                json={'title': f'Leak test {i}', 'content': 'x' * 10000}
            )

            if response.status_code == 201:
                doc_id = response.get_json()['document_id']
                client.delete(f'/api/documents/{doc_id}', headers=auth_headers)

            # Check memory periodically
            if i % 100 == 0:
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"Iteration {i}: Memory {current_memory:.2f} MB")

        # Final memory check
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024

        memory_increase = final_memory - initial_memory
        print(f"\nMemory Analysis:")
        print(f"Initial: {initial_memory:.2f} MB")
        print(f"Final: {final_memory:.2f} MB")
        print(f"Increase: {memory_increase:.2f} MB")

        # Memory increase should be reasonable (< 100MB for 1000 operations)
        assert memory_increase < 100, f"Potential memory leak detected: {memory_increase:.2f} MB increase"


class TestDataMigration:
    """Примеры large тестов для миграции данных"""

    def test_large_scale_data_migration(self, test_db):
        """
        Test migrating large amount of data
        """
        from src.services.migration import MigrationService
        from src.models import Document, User

        migration = MigrationService()

        # Create large dataset
        print("Creating test dataset...")
        num_users = 100
        docs_per_user = 50

        users = []
        for i in range(num_users):
            user = User(
                username=f'migrate_user{i}',
                email=f'migrate{i}@example.com',
                password_hash='hash'
            )
            users.append(user)

        test_db.session.bulk_save_objects(users)
        test_db.session.commit()

        documents = []
        for user in users:
            for j in range(docs_per_user):
                doc = Document(
                    title=f'Doc {j} by {user.username}',
                    content='x' * 1000,
                    owner_id=user.id
                )
                documents.append(doc)

        test_db.session.bulk_save_objects(documents)
        test_db.session.commit()

        total_docs = num_users * docs_per_user
        print(f"Created {total_docs} documents")

        # Perform migration (e.g., add new fields, transform data)
        print("Starting migration...")
        start_time = time.time()

        migration.migrate_documents_v1_to_v2()

        duration = time.time() - start_time
        print(f"Migration completed in {duration:.2f} seconds")

        # Verify migration
        migrated_count = Document.query.filter(
            Document.schema_version == 2
        ).count()

        assert migrated_count == total_docs
        print(f"Successfully migrated {migrated_count} documents")


class TestDisasterRecovery:
    """Примеры large тестов для восстановления после сбоев"""

    def test_database_backup_and_restore(self, test_db, tmp_path):
        """
        Test complete database backup and restore process
        """
        from src.services.backup import BackupService
        from src.models import User, Document

        backup_service = BackupService(backup_dir=str(tmp_path))

        # Create test data
        users = [
            User(username=f'backup_user{i}', email=f'backup{i}@test.com', password_hash='hash')
            for i in range(10)
        ]
        test_db.session.bulk_save_objects(users)
        test_db.session.commit()

        # Create backup
        print("Creating backup...")
        backup_file = backup_service.create_full_backup()
        assert backup_file.exists()

        # Simulate data loss
        print("Simulating data loss...")
        test_db.session.query(User).delete()
        test_db.session.commit()

        assert User.query.count() == 0

        # Restore from backup
        print("Restoring from backup...")
        backup_service.restore_from_backup(backup_file)

        # Verify restoration
        restored_users = User.query.count()
        assert restored_users == 10
        print(f"Successfully restored {restored_users} users")

    @pytest.mark.skipif(
        not os.getenv('TEST_DISASTER_RECOVERY'),
        reason="Disaster recovery tests disabled by default"
    )
    def test_failover_to_replica(self, test_db_primary, test_db_replica):
        """
        Test automatic failover to replica database
        """
        # This would test your failover mechanism
        # Only runs if explicitly enabled
        pass


# Примечание: для запуска large тестов используйте:
# pytest -m large
# или через скрипт:
# ./scripts/run_tests_by_size.sh large
