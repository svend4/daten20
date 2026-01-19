"""
Comprehensive tests for core.celery_app module
"""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestCeleryAppCreation:
    """Tests for Celery app creation"""

    @patch("src.core.celery_app.CELERY_AVAILABLE", True)
    @patch("src.core.celery_app.Celery")
    def test_create_celery_app_success(self, mock_celery_class):
        """Test successful Celery app creation"""
        from src.core.celery_app import create_celery_app

        mock_app = Mock()
        mock_app.conf.update = Mock()
        mock_celery_class.return_value = mock_app

        app = create_celery_app()

        assert app is not None
        mock_celery_class.assert_called_once()
        mock_app.conf.update.assert_called_once()

    @patch("src.core.celery_app.CELERY_AVAILABLE", False)
    def test_create_celery_app_unavailable(self):
        """Test Celery app creation when Celery unavailable"""
        from src.core.celery_app import create_celery_app

        app = create_celery_app()

        assert app is None


class TestCeleryConfiguration:
    """Tests for Celery configuration"""

    @patch("src.core.celery_app.CELERY_AVAILABLE", True)
    @patch("src.core.celery_app.Celery")
    def test_celery_app_configuration(self, mock_celery_class):
        """Test Celery app is configured with correct settings"""
        from src.core.celery_app import create_celery_app

        mock_app = Mock()
        config_updates = {}

        def capture_config(conf_dict):
            config_updates.update(conf_dict)

        mock_app.conf.update = capture_config
        mock_celery_class.return_value = mock_app

        create_celery_app()

        # Verify key configuration
        assert config_updates["task_serializer"] == "json"
        assert config_updates["result_serializer"] == "json"
        assert config_updates["task_acks_late"] is True
        assert config_updates["task_time_limit"] == 3600

    def test_task_routes_configured(self):
        """Test task routes are defined"""
        from src.core.celery_app import CELERY_TASK_ROUTES

        assert "src.core.celery_app.process_document_async" in CELERY_TASK_ROUTES
        assert "src.core.celery_app.extract_entities_async" in CELERY_TASK_ROUTES

    def test_task_queues_configured(self):
        """Test task queues are defined"""
        from src.core.celery_app import CELERY_TASK_QUEUES

        queue_names = [q.name for q in CELERY_TASK_QUEUES]

        assert "documents" in queue_names
        assert "ml" in queue_names
        assert "notifications" in queue_names


class TestLoggingTaskBase:
    """Tests for LoggingTask base class"""

    @patch("src.core.celery_app.CELERY_AVAILABLE", True)
    @patch("src.core.celery_app.Task", object)
    def test_logging_task_call(self):
        """Test LoggingTask logs on call"""
        from src.core.celery_app import LoggingTask

        # Create mock task instance
        task = LoggingTask()
        task.name = "test_task"

        # Mock parent __call__
        with patch.object(object, "__call__", return_value="result"):
            result = task()

        assert result == "result"

    @patch("src.core.celery_app.CELERY_AVAILABLE", True)
    def test_logging_task_on_retry(self):
        """Test LoggingTask on_retry callback"""
        from src.core.celery_app import LoggingTask

        task = LoggingTask()
        task.name = "test_task"

        # Should not raise error
        task.on_retry(exc=Exception("test"), task_id="123", args=(), kwargs={}, einfo=None)

    @patch("src.core.celery_app.CELERY_AVAILABLE", True)
    def test_logging_task_on_failure(self):
        """Test LoggingTask on_failure callback"""
        from src.core.celery_app import LoggingTask

        task = LoggingTask()
        task.name = "test_task"

        # Should not raise error
        task.on_failure(exc=Exception("test"), task_id="123", args=(), kwargs={}, einfo=None)


class TestDocumentProcessingTasks:
    """Tests for document processing tasks"""

    @patch("src.core.celery_app.DocumentParser")
    @patch("src.core.celery_app.NEREngine")
    @patch("src.core.celery_app.TfidfSVMClassifier")
    @patch("src.core.celery_app.RelationExtractor")
    @patch("src.core.celery_app.celery_app")
    def test_process_document_async_task(
        self, mock_app, mock_extractor, mock_classifier, mock_ner, mock_parser
    ):
        """Test process_document_async task"""
        # Skip if Celery not available
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import process_document_async

        # Mock components
        mock_parser_inst = Mock()
        mock_parser_inst.parse.return_value = {"text": "Document text"}
        mock_parser.return_value = mock_parser_inst

        mock_ner_inst = Mock()
        mock_ner_inst.extract_entities.return_value = []
        mock_ner.return_value = mock_ner_inst

        mock_class_inst = Mock()
        mock_class_result = Mock()
        mock_class_result.category.value = "INVOICE"
        mock_class_result.confidence = 0.9
        mock_class_inst.predict.return_value = mock_class_result
        mock_classifier.return_value = mock_class_inst

        mock_ext_inst = Mock()
        mock_ext_inst.extract_relations.return_value = []
        mock_extractor.return_value = mock_ext_inst

        # Create mock task with self parameter
        mock_self = Mock()

        result = process_document_async(mock_self, "test.pdf", build_graph=False)

        assert result["file_path"] == "test.pdf"
        assert result["status"] == "completed"
        assert "classification" in result

    @patch("src.core.celery_app.celery_app")
    @patch("src.core.celery_app.group")
    def test_batch_process_documents_task(self, mock_group, mock_app):
        """Test batch_process_documents task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import batch_process_documents

        # Mock group result
        mock_job = Mock()
        mock_result = Mock()
        mock_result.get.return_value = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "failed"},
        ]
        mock_job.apply_async.return_value = mock_result
        mock_group.return_value = mock_job

        mock_self = Mock()
        result = batch_process_documents(mock_self, ["doc1.pdf", "doc2.pdf", "doc3.pdf"])

        assert result["total"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1


class TestMLTasks:
    """Tests for ML tasks"""

    @patch("src.core.celery_app.NEREngine")
    @patch("src.core.celery_app.celery_app")
    def test_extract_entities_async_task(self, mock_app, mock_ner):
        """Test extract_entities_async task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import extract_entities_async

        # Mock entity
        mock_entity = Mock()
        mock_entity.text = "Berlin"
        mock_entity.type.value = "LOCATION"
        mock_entity.start = 0
        mock_entity.end = 6
        mock_entity.confidence = 0.95

        mock_ner_inst = Mock()
        mock_ner_inst.extract_entities.return_value = [mock_entity]
        mock_ner.return_value = mock_ner_inst

        entities = extract_entities_async("Text with Berlin")

        assert len(entities) == 1
        assert entities[0]["text"] == "Berlin"

    @patch("src.core.celery_app.TfidfSVMClassifier")
    @patch("src.core.celery_app.celery_app")
    def test_classify_document_async_task(self, mock_app, mock_classifier):
        """Test classify_document_async task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import classify_document_async

        mock_result = Mock()
        mock_result.category.value = "INVOICE"
        mock_result.confidence = 0.92

        mock_class_inst = Mock()
        mock_class_inst.predict.return_value = mock_result
        mock_classifier.return_value = mock_class_inst

        classification = classify_document_async("Document text")

        assert classification["category"] == "INVOICE"
        assert classification["confidence"] == 0.92

    @patch("src.core.celery_app.RelationExtractor")
    @patch("src.core.celery_app.celery_app")
    def test_extract_relations_async_task(self, mock_app, mock_extractor):
        """Test extract_relations_async task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import extract_relations_async

        mock_relation = Mock()
        mock_relation.source_entity = "John"
        mock_relation.source_type.value = "PERSON"
        mock_relation.relation_type.value = "WORKS_FOR"
        mock_relation.target_entity = "Company"
        mock_relation.target_type.value = "ORGANIZATION"
        mock_relation.confidence = 0.88

        mock_ext_inst = Mock()
        mock_ext_inst.extract_relations.return_value = [mock_relation]
        mock_extractor.return_value = mock_ext_inst

        relations = extract_relations_async("John works for Company")

        assert len(relations) == 1
        assert relations[0]["source"] == "John"

    @patch("src.core.celery_app.KnowledgeGraphBuilder")
    @patch("src.core.celery_app.celery_app")
    def test_build_knowledge_graph_async_task(self, mock_app, mock_builder):
        """Test build_knowledge_graph_async task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import build_knowledge_graph_async

        mock_graph = Mock()
        mock_graph.export.return_value = {"nodes": [], "edges": []}

        mock_builder_inst = Mock()
        mock_builder_inst.build_from_text.return_value = mock_graph
        mock_builder.return_value = mock_builder_inst

        result = build_knowledge_graph_async("Text", export_format="json")

        assert result["format"] == "json"
        assert "data" in result


class TestOCRTasks:
    """Tests for OCR tasks"""

    @patch("src.core.celery_app.OCRProcessor")
    @patch("src.core.celery_app.celery_app")
    def test_process_ocr_async_task(self, mock_app, mock_processor):
        """Test process_ocr_async task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import process_ocr_async

        mock_result = Mock()
        mock_result.text = "Extracted text"
        mock_result.confidence = 0.94
        mock_result.language = "eng"
        mock_result.engine = "tesseract"
        mock_result.processing_time = 1.23

        mock_proc_inst = Mock()
        mock_proc_inst.process_image.return_value = mock_result
        mock_processor.return_value = mock_proc_inst

        mock_self = Mock()
        result = process_ocr_async(mock_self, "image.png", language="eng")

        assert result["text"] == "Extracted text"
        assert result["status"] == "completed"


class TestReportGenerationTasks:
    """Tests for report generation tasks"""

    @patch("src.core.celery_app.PDFExporter")
    @patch("src.core.celery_app.celery_app")
    def test_generate_pdf_report_task(self, mock_app, mock_exporter):
        """Test generate_pdf_report task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import generate_pdf_report

        mock_exp_inst = Mock()
        mock_exp_inst.export_services.return_value = None
        mock_exporter.return_value = mock_exp_inst

        mock_self = Mock()
        mock_self.request.id = "task_123"

        result = generate_pdf_report(mock_self, {"services": []}, template="default")

        assert result["status"] == "completed"
        assert "output_path" in result


class TestNotificationTasks:
    """Tests for notification tasks"""

    @patch("src.core.celery_app.EmailNotifier")
    @patch("src.core.celery_app.celery_app")
    def test_send_email_notification_task(self, mock_app, mock_notifier):
        """Test send_email_notification task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import send_email_notification

        mock_notifier_inst = Mock()
        mock_notifier_inst.send.return_value = True
        mock_notifier.return_value = mock_notifier_inst

        result = send_email_notification(
            to="user@example.com", subject="Test", body="Test body", html=False
        )

        assert result["to"] == "user@example.com"
        assert result["sent"] is True
        assert result["status"] == "completed"


class TestMaintenanceTasks:
    """Tests for maintenance tasks"""

    @patch("src.core.celery_app.BackupManager")
    @patch("src.core.celery_app.celery_app")
    def test_create_backup_task(self, mock_app, mock_backup_mgr):
        """Test create_backup task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import create_backup

        mock_mgr_inst = Mock()
        mock_mgr_inst.create_backup.return_value = "/backups/backup_2026-01-18.zip"
        mock_backup_mgr.return_value = mock_mgr_inst

        result = create_backup()

        assert result["status"] == "completed"
        assert "backup_path" in result

    @patch("src.core.celery_app.celery_app")
    def test_cleanup_old_results_task(self, mock_app):
        """Test cleanup_old_results task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import cleanup_old_results

        result = cleanup_old_results()

        assert result["status"] == "completed"

    @patch("src.core.celery_app.celery_app")
    def test_system_health_check_task(self, mock_app):
        """Test system_health_check task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import system_health_check

        result = system_health_check()

        assert result["status"] == "healthy"


class TestDataExportTasks:
    """Tests for data export tasks"""

    @patch("src.core.celery_app.celery_app")
    def test_export_data_task(self, mock_app):
        """Test export_data task"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import export_data

        mock_self = Mock()
        mock_self.request.id = "export_456"

        result = export_data(mock_self, data_type="services", format="csv")

        assert result["status"] == "completed"
        assert result["data_type"] == "services"
        assert result["format"] == "csv"


class TestUtilityFunctions:
    """Tests for utility functions"""

    @patch("src.core.celery_app.celery_app")
    @patch("src.core.celery_app.AsyncResult")
    def test_get_task_status(self, mock_async_result, mock_app):
        """Test get_task_status function"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import get_task_status

        mock_result = Mock()
        mock_result.status = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = {"data": "result"}
        mock_async_result.return_value = mock_result

        status = get_task_status("task_123")

        assert status["task_id"] == "task_123"
        assert status["status"] == "SUCCESS"
        assert status["ready"] is True

    @patch("src.core.celery_app.celery_app")
    def test_revoke_task(self, mock_app):
        """Test revoke_task function"""
        if mock_app is None:
            pytest.skip("Celery not available")

        from src.core.celery_app import revoke_task

        mock_app.control.revoke = Mock()

        result = revoke_task("task_456", terminate=True)

        assert result["task_id"] == "task_456"
        assert result["revoked"] is True
        assert result["terminated"] is True
        mock_app.control.revoke.assert_called_once_with("task_456", terminate=True)

    def test_get_task_status_celery_unavailable(self):
        """Test get_task_status when Celery unavailable"""
        with patch("src.core.celery_app.celery_app", None):
            from src.core.celery_app import get_task_status

            status = get_task_status("task_123")

            assert "error" in status

    def test_revoke_task_celery_unavailable(self):
        """Test revoke_task when Celery unavailable"""
        with patch("src.core.celery_app.celery_app", None):
            from src.core.celery_app import revoke_task

            result = revoke_task("task_456")

            assert "error" in result
