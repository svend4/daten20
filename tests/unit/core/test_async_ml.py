"""
Comprehensive tests for core.async_ml module
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestMLExecutor:
    """Tests for ML executor management"""

    def test_get_ml_executor_creates_instance(self):
        """Test get_ml_executor creates ThreadPoolExecutor"""
        from src.core.async_ml import get_ml_executor

        executor = get_ml_executor()
        assert executor is not None
        assert hasattr(executor, "submit")

    def test_get_ml_executor_returns_same_instance(self):
        """Test get_ml_executor returns singleton"""
        from src.core.async_ml import get_ml_executor

        executor1 = get_ml_executor()
        executor2 = get_ml_executor()
        assert executor1 is executor2

    def test_shutdown_ml_executor(self):
        """Test shutdown_ml_executor shuts down gracefully"""
        from src.core.async_ml import get_ml_executor, shutdown_ml_executor

        executor = get_ml_executor()
        assert executor is not None

        shutdown_ml_executor()

        # Get new executor after shutdown
        new_executor = get_ml_executor()
        assert new_executor is not None
        assert new_executor is not executor


class TestRunInExecutor:
    """Tests for run_in_executor"""

    @pytest.mark.asyncio
    async def test_run_in_executor_basic(self):
        """Test run_in_executor executes function"""
        from src.core.async_ml import run_in_executor

        def sync_func(x, y):
            return x + y

        result = await run_in_executor(sync_func, 3, 5)
        assert result == 8

    @pytest.mark.asyncio
    async def test_run_in_executor_with_kwargs(self):
        """Test run_in_executor with keyword arguments"""
        from src.core.async_ml import run_in_executor

        def sync_func(a, b=10):
            return a * b

        result = await run_in_executor(sync_func, 5, b=3)
        assert result == 15


class TestExtractEntitiesAsync:
    """Tests for async entity extraction"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.NEREngine")
    async def test_extract_entities_async_basic(self, mock_ner_class):
        """Test basic entity extraction"""
        from src.core.async_ml import extract_entities_async

        # Mock entity
        mock_entity = Mock()
        mock_entity.text = "Berlin"
        mock_entity.type.value = "LOCATION"
        mock_entity.start = 0
        mock_entity.end = 6
        mock_entity.confidence = 0.95

        # Mock NER engine
        mock_ner = Mock()
        mock_ner.extract_entities.return_value = [mock_entity]
        mock_ner_class.return_value = mock_ner

        entities = await extract_entities_async("Text with Berlin")

        assert len(entities) == 1
        assert entities[0]["text"] == "Berlin"
        assert entities[0]["type"] == "LOCATION"

    @pytest.mark.asyncio
    @patch("src.core.async_ml.NEREngine")
    async def test_extract_entities_async_with_timeout(self, mock_ner_class):
        """Test entity extraction with timeout"""
        from src.core.async_ml import extract_entities_async

        mock_ner = Mock()
        mock_ner.extract_entities.return_value = []
        mock_ner_class.return_value = mock_ner

        # Should complete without timeout
        entities = await extract_entities_async("Short text", timeout=5.0)
        assert isinstance(entities, list)

    @pytest.mark.asyncio
    @patch("src.core.async_ml.NEREngine")
    async def test_extract_entities_async_timeout_error(self, mock_ner_class):
        """Test entity extraction timeout"""
        from src.core.async_ml import extract_entities_async

        # Mock slow extraction
        def slow_extract(text):
            import time

            time.sleep(3)
            return []

        mock_ner = Mock()
        mock_ner.extract_entities.side_effect = slow_extract
        mock_ner_class.return_value = mock_ner

        with pytest.raises(asyncio.TimeoutError):
            await extract_entities_async("Text", timeout=0.1)


class TestClassifyDocumentAsync:
    """Tests for async document classification"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.TfidfSVMClassifier")
    async def test_classify_document_async_basic(self, mock_classifier_class):
        """Test basic document classification"""
        from src.core.async_ml import classify_document_async

        # Mock classification result
        mock_result = Mock()
        mock_result.category.value = "INVOICE"
        mock_result.confidence = 0.92
        mock_result.probabilities = {"INVOICE": 0.92, "CONTRACT": 0.08}

        mock_classifier = Mock()
        mock_classifier.predict.return_value = mock_result
        mock_classifier_class.return_value = mock_classifier

        classification = await classify_document_async("Document text")

        assert classification["category"] == "INVOICE"
        assert classification["confidence"] == 0.92
        assert classification["probabilities"] is not None

    @pytest.mark.asyncio
    @patch("src.core.async_ml.TfidfSVMClassifier")
    async def test_classify_document_async_with_timeout(self, mock_classifier_class):
        """Test classification with timeout"""
        from src.core.async_ml import classify_document_async

        mock_result = Mock()
        mock_result.category.value = "UNKNOWN"
        mock_result.confidence = 0.5

        mock_classifier = Mock()
        mock_classifier.predict.return_value = mock_result
        mock_classifier_class.return_value = mock_classifier

        result = await classify_document_async("Text", timeout=5.0)
        assert result["category"] == "UNKNOWN"


class TestExtractRelationsAsync:
    """Tests for async relation extraction"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.RelationExtractor")
    async def test_extract_relations_async_basic(self, mock_extractor_class):
        """Test basic relation extraction"""
        from src.core.async_ml import extract_relations_async

        # Mock relation
        mock_relation = Mock()
        mock_relation.source_entity = "John"
        mock_relation.source_type.value = "PERSON"
        mock_relation.relation_type.value = "WORKS_FOR"
        mock_relation.target_entity = "Company"
        mock_relation.target_type.value = "ORGANIZATION"
        mock_relation.confidence = 0.88

        mock_extractor = Mock()
        mock_extractor.extract_relations.return_value = [mock_relation]
        mock_extractor_class.return_value = mock_extractor

        relations = await extract_relations_async("John works for Company")

        assert len(relations) == 1
        assert relations[0]["source"] == "John"
        assert relations[0]["relation"] == "WORKS_FOR"
        assert relations[0]["target"] == "Company"


class TestBuildKnowledgeGraphAsync:
    """Tests for async knowledge graph building"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.KnowledgeGraphBuilder")
    async def test_build_knowledge_graph_async_json(self, mock_builder_class):
        """Test building knowledge graph with JSON export"""
        from src.core.async_ml import build_knowledge_graph_async

        # Mock graph
        mock_graph = Mock()
        mock_graph.export.return_value = {"nodes": [], "edges": []}

        mock_builder = Mock()
        mock_builder.build_from_text.return_value = mock_graph
        mock_builder_class.return_value = mock_builder

        result = await build_knowledge_graph_async("Text", export_format="json")

        assert result["format"] == "json"
        assert "data" in result
        mock_graph.export.assert_called_once()


class TestProcessOCRAsync:
    """Tests for async OCR processing"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.OCRProcessor")
    async def test_process_ocr_async_basic(self, mock_processor_class):
        """Test basic OCR processing"""
        from src.core.async_ml import process_ocr_async

        # Mock OCR result
        mock_result = Mock()
        mock_result.text = "Extracted text"
        mock_result.confidence = 0.94
        mock_result.language = "eng"
        mock_result.engine = "tesseract"
        mock_result.processing_time = 1.23

        mock_processor = Mock()
        mock_processor.process_image.return_value = mock_result
        mock_processor_class.return_value = mock_processor

        result = await process_ocr_async("image.png", language="eng")

        assert result["text"] == "Extracted text"
        assert result["confidence"] == 0.94
        assert result["language"] == "eng"


class TestProcessDocumentAsync:
    """Tests for async document processing pipeline"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.DocumentParser")
    @patch("src.core.async_ml.extract_entities_async")
    @patch("src.core.async_ml.classify_document_async")
    @patch("src.core.async_ml.extract_relations_async")
    async def test_process_document_async_without_graph(
        self,
        mock_relations,
        mock_classify,
        mock_entities,
        mock_parser_class,
    ):
        """Test full document processing without graph"""
        from src.core.async_ml import process_document_async

        # Mock parser
        mock_parser = Mock()
        mock_parser.parse.return_value = {"text": "Document text content"}
        mock_parser_class.return_value = mock_parser

        # Mock async functions
        mock_entities.return_value = [{"text": "Entity1", "type": "PERSON"}]
        mock_classify.return_value = {"category": "INVOICE", "confidence": 0.9}
        mock_relations.return_value = []

        result = await process_document_async("doc.pdf", build_graph=False)

        assert result["file_path"] == "doc.pdf"
        assert result["status"] == "completed"
        assert result["entity_count"] == 1
        assert result["knowledge_graph"] is None

    @pytest.mark.asyncio
    @patch("src.core.async_ml.DocumentParser")
    @patch("src.core.async_ml.extract_entities_async")
    @patch("src.core.async_ml.classify_document_async")
    @patch("src.core.async_ml.extract_relations_async")
    @patch("src.core.async_ml.build_knowledge_graph_async")
    async def test_process_document_async_with_graph(
        self,
        mock_graph,
        mock_relations,
        mock_classify,
        mock_entities,
        mock_parser_class,
    ):
        """Test document processing with knowledge graph"""
        from src.core.async_ml import process_document_async

        mock_parser = Mock()
        mock_parser.parse.return_value = {"text": "Text"}
        mock_parser_class.return_value = mock_parser

        mock_entities.return_value = []
        mock_classify.return_value = {"category": "UNKNOWN"}
        mock_relations.return_value = []
        mock_graph.return_value = {"format": "json", "data": {}}

        result = await process_document_async("doc.pdf", build_graph=True)

        assert result["knowledge_graph"] is not None
        mock_graph.assert_called_once()


class TestBatchProcessing:
    """Tests for batch processing functions"""

    @pytest.mark.asyncio
    @patch("src.core.async_ml.extract_entities_async")
    async def test_extract_entities_batch_async(self, mock_extract):
        """Test batch entity extraction"""
        from src.core.async_ml import extract_entities_batch_async

        mock_extract.side_effect = [
            [{"text": "Entity1"}],
            [{"text": "Entity2"}],
            [{"text": "Entity3"}],
        ]

        results = await extract_entities_batch_async(["Text 1", "Text 2", "Text 3"])

        assert len(results) == 3
        assert all(isinstance(r, list) for r in results)

    @pytest.mark.asyncio
    @patch("src.core.async_ml.classify_document_async")
    async def test_classify_batch_async(self, mock_classify):
        """Test batch classification"""
        from src.core.async_ml import classify_batch_async

        mock_classify.side_effect = [
            {"category": "INVOICE"},
            {"category": "CONTRACT"},
        ]

        results = await classify_batch_async(["Doc 1", "Doc 2"])

        assert len(results) == 2


class TestUtilityFunctions:
    """Tests for utility functions"""

    @pytest.mark.asyncio
    async def test_with_retry_success_first_attempt(self):
        """Test with_retry succeeds on first attempt"""
        from src.core.async_ml import with_retry

        async def successful_func(x):
            return x * 2

        result = await with_retry(successful_func, 5, max_retries=3)
        assert result == 10

    @pytest.mark.asyncio
    async def test_with_retry_success_after_failures(self):
        """Test with_retry succeeds after retries"""
        from src.core.async_ml import with_retry

        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = await with_retry(flaky_func, max_retries=3, delay=0.1)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_with_retry_all_attempts_fail(self):
        """Test with_retry raises after all retries"""
        from src.core.async_ml import with_retry

        async def failing_func():
            raise ValueError("Permanent error")

        with pytest.raises(ValueError, match="Permanent error"):
            await with_retry(failing_func, max_retries=2, delay=0.1)

    @pytest.mark.asyncio
    async def test_gather_with_progress(self):
        """Test gather_with_progress tracks progress"""
        from src.core.async_ml import gather_with_progress

        async def task(x):
            await asyncio.sleep(0.01)
            return x * 2

        progress_calls = []

        def progress_callback(completed, total):
            progress_calls.append((completed, total))

        tasks = [task(i) for i in range(5)]
        results = await gather_with_progress(tasks, progress_callback)

        assert len(results) == 5
        assert len(progress_calls) == 5
        assert progress_calls[-1] == (5, 5)
