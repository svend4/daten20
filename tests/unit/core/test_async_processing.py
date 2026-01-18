"""
Tests for Async Processing

Tests Celery tasks and async ML operations.
"""

import asyncio
import os
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

# Test async ML operations
class TestAsyncML:
    """Tests for async ML operations"""

    @pytest.mark.asyncio
    async def test_extract_entities_async(self):
        """Test async entity extraction"""
        from src.core.async_ml import extract_entities_async

        text = "John Doe works at Google in California."

        entities = await extract_entities_async(text)

        assert isinstance(entities, list)
        assert len(entities) > 0

        # Check entity structure
        for entity in entities:
            assert "text" in entity
            assert "type" in entity
            assert "start" in entity
            assert "end" in entity
            assert "confidence" in entity

    @pytest.mark.asyncio
    async def test_extract_entities_with_types(self):
        """Test async entity extraction with specific types"""
        from src.core.async_ml import extract_entities_async

        text = "John Doe lives in New York."

        entities = await extract_entities_async(text, entity_types=["PERSON"])

        assert isinstance(entities, list)
        # Should only contain PERSON entities
        for entity in entities:
            assert entity["type"] == "PERSON"

    @pytest.mark.asyncio
    async def test_extract_entities_timeout(self):
        """Test async entity extraction with timeout"""
        from src.core.async_ml import extract_entities_async

        text = "Test text" * 1000  # Long text

        # Very short timeout should cause timeout error
        with pytest.raises(asyncio.TimeoutError):
            await extract_entities_async(text, timeout=0.001)

    @pytest.mark.asyncio
    async def test_extract_entities_batch_async(self):
        """Test batch async entity extraction"""
        from src.core.async_ml import extract_entities_batch_async

        texts = [
            "John Doe works at Google.",
            "Jane Smith lives in New York.",
            "Microsoft was founded by Bill Gates.",
        ]

        results = await extract_entities_batch_async(texts)

        assert isinstance(results, list)
        assert len(results) == len(texts)

        # Each result should be a list of entities
        for result in results:
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_batch_with_progress_callback(self):
        """Test batch processing with progress callback"""
        from src.core.async_ml import extract_entities_batch_async

        texts = ["Test text " + str(i) for i in range(5)]

        progress_calls = []

        def progress_callback(completed, total):
            progress_calls.append((completed, total))

        results = await extract_entities_batch_async(
            texts, progress_callback=progress_callback
        )

        assert len(results) == 5
        # Progress callback should have been called
        assert len(progress_calls) > 0

    @pytest.mark.asyncio
    async def test_classify_document_async(self):
        """Test async document classification"""
        from src.core.async_ml import classify_document_async

        text = "This is a technical document about machine learning and artificial intelligence."

        result = await classify_document_async(text)

        assert isinstance(result, dict)
        assert "category" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_extract_relations_async(self):
        """Test async relation extraction"""
        from src.core.async_ml import extract_relations_async

        text = "John Doe works at Google. Google is located in California."

        relations = await extract_relations_async(text)

        assert isinstance(relations, list)
        # Check relation structure
        for relation in relations:
            assert "source" in relation
            assert "source_type" in relation
            assert "relation" in relation
            assert "target" in relation
            assert "target_type" in relation
            assert "confidence" in relation

    @pytest.mark.asyncio
    async def test_build_knowledge_graph_async(self):
        """Test async knowledge graph building"""
        from src.core.async_ml import build_knowledge_graph_async

        text = "John Doe works at Google. Google is a technology company."

        graph = await build_knowledge_graph_async(text)

        assert isinstance(graph, dict)
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) > 0

    @pytest.mark.asyncio
    async def test_concurrent_async_operations(self):
        """Test concurrent async operations"""
        from src.core.async_ml import extract_entities_async, classify_document_async

        text1 = "John Doe works at Google."
        text2 = "This is a technical document."

        # Run operations concurrently
        entities_task = extract_entities_async(text1)
        classification_task = classify_document_async(text2)

        entities, classification = await asyncio.gather(entities_task, classification_task)

        assert isinstance(entities, list)
        assert isinstance(classification, dict)

    @pytest.mark.asyncio
    async def test_ml_executor_shutdown(self):
        """Test ML executor shutdown"""
        from src.core.async_ml import get_ml_executor, shutdown_ml_executor

        # Get executor
        executor = get_ml_executor()
        assert executor is not None

        # Shutdown
        shutdown_ml_executor()

        # Should create new executor on next get
        new_executor = get_ml_executor()
        assert new_executor is not None
        assert new_executor != executor

        # Cleanup
        shutdown_ml_executor()


class TestCeleryTasks:
    """Tests for Celery tasks"""

    def setup_method(self):
        """Setup for each test"""
        # Mock Celery if not available
        try:
            from src.core.celery_app import CELERY_AVAILABLE
            self.celery_available = CELERY_AVAILABLE
        except ImportError:
            self.celery_available = False

    def test_celery_app_creation(self):
        """Test Celery app creation"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import celery_app

        assert celery_app is not None

    def test_process_document_task_definition(self):
        """Test process_document_async task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import process_document_async

        assert process_document_async is not None
        assert hasattr(process_document_async, "delay")
        assert hasattr(process_document_async, "apply_async")

    def test_batch_process_task_definition(self):
        """Test batch_process_documents task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import batch_process_documents

        assert batch_process_documents is not None

    def test_extract_entities_task_definition(self):
        """Test extract_entities_async task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import extract_entities_async

        assert extract_entities_async is not None

    def test_classify_document_task_definition(self):
        """Test classify_document_async task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import classify_document_async

        assert classify_document_async is not None

    def test_ocr_task_definition(self):
        """Test process_ocr_async task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import process_ocr_async

        assert process_ocr_async is not None

    def test_email_notification_task_definition(self):
        """Test send_email_notification task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import send_email_notification

        assert send_email_notification is not None

    def test_backup_task_definition(self):
        """Test create_backup task is defined"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import create_backup

        assert create_backup is not None

    def test_task_routes_configuration(self):
        """Test task routes are configured"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import CELERY_TASK_ROUTES

        assert isinstance(CELERY_TASK_ROUTES, dict)
        assert len(CELERY_TASK_ROUTES) > 0

        # Check key routes
        assert "src.core.celery_app.process_document_async" in CELERY_TASK_ROUTES
        assert "src.core.celery_app.extract_entities_async" in CELERY_TASK_ROUTES

    def test_task_queues_configuration(self):
        """Test task queues are configured"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import CELERY_TASK_QUEUES

        assert isinstance(CELERY_TASK_QUEUES, tuple)
        assert len(CELERY_TASK_QUEUES) >= 8

        # Check queue names
        queue_names = [q.name for q in CELERY_TASK_QUEUES]
        assert "documents" in queue_names
        assert "ml" in queue_names
        assert "ocr" in queue_names
        assert "notifications" in queue_names

    def test_get_task_status_utility(self):
        """Test get_task_status utility"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import get_task_status

        # Test with fake task ID
        status = get_task_status("fake-task-id")

        assert isinstance(status, dict)
        assert "task_id" in status
        assert "status" in status

    def test_revoke_task_utility(self):
        """Test revoke_task utility"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import revoke_task

        # Test with fake task ID
        result = revoke_task("fake-task-id")

        assert isinstance(result, dict)
        assert "task_id" in result
        assert "revoked" in result


class TestCeleryIntegration:
    """Integration tests for Celery tasks"""

    def setup_method(self):
        """Setup for each test"""
        try:
            from src.core.celery_app import CELERY_AVAILABLE
            self.celery_available = CELERY_AVAILABLE
        except ImportError:
            self.celery_available = False

    @pytest.mark.skipif(
        os.getenv("CELERY_BROKER_URL") is None,
        reason="Celery broker not configured"
    )
    def test_process_document_task_execution(self):
        """Test process_document_async task execution (requires broker)"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import process_document_async

        # Create temp test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document with John Doe at Google")
            test_file = f.name

        try:
            # Submit task (async)
            result = process_document_async.delay(test_file)

            # Wait for result (with timeout)
            output = result.get(timeout=30)

            assert isinstance(output, dict)
            assert "status" in output
            assert output["status"] in ["completed", "failed"]

        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.skipif(
        os.getenv("CELERY_BROKER_URL") is None,
        reason="Celery broker not configured"
    )
    def test_extract_entities_task_execution(self):
        """Test extract_entities_async task execution (requires broker)"""
        if not self.celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import extract_entities_async

        text = "John Doe works at Google in California."

        # Submit task
        result = extract_entities_async.delay(text)

        # Wait for result
        entities = result.get(timeout=30)

        assert isinstance(entities, list)
        assert len(entities) > 0


class TestAsyncPerformance:
    """Performance tests for async operations"""

    @pytest.mark.asyncio
    async def test_async_vs_sync_performance(self):
        """Compare async vs sync performance"""
        from src.core.async_ml import extract_entities_async
        from src.ml.ner import NEREngine

        text = "This is a test document with John Doe at Google in California."

        # Measure sync performance
        sync_start = time.time()
        ner_engine = NEREngine()
        for _ in range(5):
            ner_engine.extract_entities(text)
        sync_time = time.time() - sync_start

        # Measure async performance (parallel)
        async_start = time.time()
        tasks = [extract_entities_async(text) for _ in range(5)]
        await asyncio.gather(*tasks)
        async_time = time.time() - async_start

        print(f"\nSync time: {sync_time:.2f}s")
        print(f"Async time: {async_time:.2f}s")
        print(f"Speedup: {sync_time / async_time:.2f}x")

        # Async should be faster for parallel operations
        # (unless running on single-core CPU)
        assert async_time <= sync_time * 1.5  # Allow some overhead

    @pytest.mark.asyncio
    async def test_batch_processing_performance(self):
        """Test batch processing performance"""
        from src.core.async_ml import extract_entities_batch_async

        texts = ["Test document " + str(i) for i in range(10)]

        start = time.time()
        results = await extract_entities_batch_async(texts)
        elapsed = time.time() - start

        assert len(results) == 10
        print(f"\nBatch processing time: {elapsed:.2f}s for 10 texts")
        print(f"Average per text: {elapsed/10:.2f}s")

        # Should complete in reasonable time
        assert elapsed < 60  # Less than 60 seconds for 10 texts


class TestAsyncErrorHandling:
    """Error handling tests for async operations"""

    @pytest.mark.asyncio
    async def test_async_entity_extraction_error_handling(self):
        """Test error handling in async entity extraction"""
        from src.core.async_ml import extract_entities_async

        # Empty text should not crash
        entities = await extract_entities_async("")
        assert isinstance(entities, list)

    @pytest.mark.asyncio
    async def test_invalid_entity_type_handling(self):
        """Test handling of invalid entity types"""
        from src.core.async_ml import extract_entities_async

        text = "Test text"

        # Should handle invalid entity type gracefully
        with pytest.raises(Exception):
            await extract_entities_async(text, entity_types=["INVALID_TYPE"])

    @pytest.mark.asyncio
    async def test_concurrent_error_handling(self):
        """Test error handling in concurrent operations"""
        from src.core.async_ml import extract_entities_async

        # Mix of valid and invalid inputs
        tasks = [
            extract_entities_async("Valid text"),
            extract_entities_async(""),  # Empty text
            extract_entities_async("Another valid text"),
        ]

        # Should handle errors without crashing all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
        # At least some should succeed
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful >= 2


class TestCeleryConfiguration:
    """Tests for Celery configuration"""

    def test_celery_broker_url(self):
        """Test Celery broker URL configuration"""
        from src.core.celery_app import CELERY_BROKER_URL

        assert CELERY_BROKER_URL is not None
        assert isinstance(CELERY_BROKER_URL, str)
        assert "redis://" in CELERY_BROKER_URL or "amqp://" in CELERY_BROKER_URL

    def test_celery_result_backend(self):
        """Test Celery result backend configuration"""
        from src.core.celery_app import CELERY_RESULT_BACKEND

        assert CELERY_RESULT_BACKEND is not None
        assert isinstance(CELERY_RESULT_BACKEND, str)

    def test_celery_app_configuration(self):
        """Test Celery app configuration"""
        try:
            from src.core.celery_app import CELERY_AVAILABLE
            celery_available = CELERY_AVAILABLE
        except ImportError:
            pytest.skip("Celery not available")

        if not celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import celery_app

        assert celery_app is not None
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.task_acks_late is True


class TestAsyncMLExecutor:
    """Tests for async ML executor"""

    def test_ml_executor_creation(self):
        """Test ML executor is created"""
        from src.core.async_ml import get_ml_executor

        executor = get_ml_executor()

        assert executor is not None
        assert executor._max_workers == 4

    def test_ml_executor_singleton(self):
        """Test ML executor is singleton"""
        from src.core.async_ml import get_ml_executor

        executor1 = get_ml_executor()
        executor2 = get_ml_executor()

        assert executor1 is executor2

    def test_ml_executor_shutdown_and_recreate(self):
        """Test ML executor can be shutdown and recreated"""
        from src.core.async_ml import get_ml_executor, shutdown_ml_executor

        executor1 = get_ml_executor()

        shutdown_ml_executor()

        executor2 = get_ml_executor()

        assert executor1 != executor2

        # Cleanup
        shutdown_ml_executor()

    @pytest.mark.asyncio
    async def test_run_in_executor(self):
        """Test run_in_executor utility"""
        from src.core.async_ml import run_in_executor

        def sync_function(x, y):
            return x + y

        result = await run_in_executor(sync_function, 2, 3)

        assert result == 5


class TestTaskPriorities:
    """Tests for task priorities"""

    def test_queue_priorities_configured(self):
        """Test that queue priorities are configured"""
        try:
            from src.core.celery_app import CELERY_AVAILABLE
            celery_available = CELERY_AVAILABLE
        except ImportError:
            pytest.skip("Celery not available")

        if not celery_available:
            pytest.skip("Celery not available")

        from src.core.celery_app import CELERY_TASK_QUEUES

        # Check all queues have priorities
        for queue in CELERY_TASK_QUEUES:
            assert hasattr(queue, "priority")
            assert queue.priority > 0

        # Check priority ordering
        priorities = {q.name: q.priority for q in CELERY_TASK_QUEUES}

        # Notifications should have high priority
        assert priorities.get("notifications", 0) >= 7

        # Maintenance should have lower priority
        assert priorities.get("maintenance", 10) <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
