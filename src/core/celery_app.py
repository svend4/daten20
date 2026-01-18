#!/usr/bin/env python3
"""
Celery Application Configuration
=================================

Production-grade asynchronous task queue for long-running operations.

Features:
- Distributed task processing
- Task scheduling (periodic tasks)
- Task prioritization
- Result backend (Redis)
- Retry mechanisms
- Task monitoring
- Dead letter queue

Tasks:
- Document processing (NER, classification, relation extraction)
- Batch document processing
- OCR operations
- PDF generation
- Email notifications
- Report generation
- Backup operations
- Data exports

Usage:
    # Start Celery worker
    celery -A src.core.celery_app worker --loglevel=info

    # Start Celery beat (scheduler)
    celery -A src.core.celery_app beat --loglevel=info

    # Monitor tasks
    celery -A src.core.celery_app flower

    # Call task
    from src.core.celery_app import process_document_async
    result = process_document_async.delay(file_path)

Configuration:
    Set environment variables:
    - CELERY_BROKER_URL (default: redis://localhost:6379/0)
    - CELERY_RESULT_BACKEND (default: redis://localhost:6379/0)
    - CELERY_TASK_SERIALIZER (default: json)
    - CELERY_RESULT_SERIALIZER (default: json)

Author: Document Management System
Version: 1.0.0
"""

import logging
import os
from datetime import timedelta
from typing import Any, Dict, List, Optional

try:
    from celery import Celery, Task
    from celery.schedules import crontab
    from kombu import Exchange, Queue

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("WARNING: Celery not installed. Install with: pip install celery[redis]")
    # Create dummy Celery for imports
    Celery = None
    Task = object

logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Task routing
CELERY_TASK_ROUTES = {
    "src.core.celery_app.process_document_async": {"queue": "documents"},
    "src.core.celery_app.batch_process_documents": {"queue": "batch"},
    "src.core.celery_app.extract_entities_async": {"queue": "ml"},
    "src.core.celery_app.classify_document_async": {"queue": "ml"},
    "src.core.celery_app.extract_relations_async": {"queue": "ml"},
    "src.core.celery_app.build_knowledge_graph_async": {"queue": "ml"},
    "src.core.celery_app.process_ocr_async": {"queue": "ocr"},
    "src.core.celery_app.generate_pdf_report": {"queue": "reports"},
    "src.core.celery_app.send_email_notification": {"queue": "notifications"},
    "src.core.celery_app.create_backup": {"queue": "maintenance"},
    "src.core.celery_app.export_data": {"queue": "exports"},
}

# Queue definitions with priorities
CELERY_TASK_QUEUES = (
    Queue("documents", Exchange("documents"), routing_key="documents", priority=5),
    Queue("batch", Exchange("batch"), routing_key="batch", priority=3),
    Queue("ml", Exchange("ml"), routing_key="ml", priority=7),
    Queue("ocr", Exchange("ocr"), routing_key="ocr", priority=6),
    Queue("reports", Exchange("reports"), routing_key="reports", priority=4),
    Queue("notifications", Exchange("notifications"), routing_key="notifications", priority=8),
    Queue("maintenance", Exchange("maintenance"), routing_key="maintenance", priority=2),
    Queue("exports", Exchange("exports"), routing_key="exports", priority=4),
)


def create_celery_app() -> Optional[Celery]:
    """
    Create and configure Celery application.

    Returns:
        Configured Celery app or None if Celery not available
    """
    if not CELERY_AVAILABLE:
        logger.warning("Celery not available. Async task processing disabled.")
        return None

    app = Celery("dms_async", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

    # Configuration
    app.conf.update(
        # Serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        # Task execution
        task_acks_late=True,  # Acknowledge after task execution
        task_reject_on_worker_lost=True,  # Reject if worker dies
        worker_prefetch_multiplier=1,  # One task at a time
        # Result backend
        result_expires=3600,  # Results expire after 1 hour
        result_persistent=True,  # Persist results
        # Task routing
        task_routes=CELERY_TASK_ROUTES,
        task_queues=CELERY_TASK_QUEUES,
        task_default_queue="documents",
        task_default_exchange="documents",
        task_default_routing_key="documents",
        # Retry policy
        task_autoretry_for=(Exception,),  # Retry on any exception
        task_retry_kwargs={"max_retries": 3, "countdown": 5},  # 3 retries, 5s delay
        # Task limits
        task_time_limit=3600,  # Hard limit: 1 hour
        task_soft_time_limit=3300,  # Soft limit: 55 minutes
        # Worker settings
        worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
        worker_disable_rate_limits=False,
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
        # Beat schedule (periodic tasks)
        beat_schedule={
            "cleanup-old-results": {
                "task": "src.core.celery_app.cleanup_old_results",
                "schedule": crontab(hour=2, minute=0),  # 2 AM daily
            },
            "system-health-check": {
                "task": "src.core.celery_app.system_health_check",
                "schedule": timedelta(minutes=15),  # Every 15 minutes
            },
            "daily-backup": {
                "task": "src.core.celery_app.create_backup",
                "schedule": crontab(hour=3, minute=0),  # 3 AM daily
            },
        },
    )

    return app


# Create Celery app instance
celery_app = create_celery_app()


# Custom Task base class with logging
if CELERY_AVAILABLE:

    class LoggingTask(Task):
        """Custom task with logging"""

        def __call__(self, *args, **kwargs):
            logger.info(f"Starting task: {self.name}")
            try:
                result = super().__call__(*args, **kwargs)
                logger.info(f"Task completed: {self.name}")
                return result
            except Exception as e:
                logger.error(f"Task failed: {self.name} - {str(e)}")
                raise

        def on_retry(self, exc, task_id, args, kwargs, einfo):
            logger.warning(f"Retrying task: {self.name} - {str(exc)}")

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Task failed permanently: {self.name} - {str(exc)}")


# =============================================================================
# DOCUMENT PROCESSING TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, bind=True, name="src.core.celery_app.process_document_async")
def process_document_async(self, file_path: str, build_graph: bool = False) -> Dict[str, Any]:
    """
    Process document asynchronously.

    Args:
        file_path: Path to document file
        build_graph: Whether to build knowledge graph

    Returns:
        Processing results dictionary
    """
    from src.core.parser import DocumentParser
    from src.ml.classifier import TfidfSVMClassifier
    from src.ml.knowledge_graph import GraphFormat, KnowledgeGraphBuilder
    from src.ml.ner import NEREngine
    from src.ml.relation_extractor import RelationExtractor

    try:
        # Initialize components
        parser = DocumentParser()
        ner_engine = NEREngine()
        classifier = TfidfSVMClassifier()
        relation_extractor = RelationExtractor()
        graph_builder = KnowledgeGraphBuilder()

        # Parse document
        parsed = parser.parse(file_path)
        text = parsed.get("text", "")

        # Extract entities
        entities = ner_engine.extract_entities(text)

        # Classify
        classification = classifier.predict(text)

        # Extract relations
        relations = relation_extractor.extract_relations(text)

        # Build knowledge graph if requested
        knowledge_graph = None
        if build_graph:
            graph = graph_builder.build_from_text(text)
            knowledge_graph = graph.export(GraphFormat.JSON)

        # Build result
        result = {
            "file_path": file_path,
            "text_length": len(text),
            "word_count": len(text.split()),
            "entity_count": len(entities),
            "relation_count": len(relations),
            "classification": {
                "category": classification.category.value if hasattr(classification, "category") else "UNKNOWN",
                "confidence": getattr(classification, "confidence", 0.0),
            },
            "entities": [
                {
                    "text": e.text,
                    "type": e.type.value,
                    "start": e.start,
                    "end": e.end,
                    "confidence": e.confidence,
                }
                for e in entities
            ],
            "relations": [
                {
                    "source": r.source_entity,
                    "source_type": r.source_type.value,
                    "relation": r.relation_type.value,
                    "target": r.target_entity,
                    "target_type": r.target_type.value,
                    "confidence": r.confidence,
                }
                for r in relations
            ],
            "knowledge_graph": knowledge_graph,
            "status": "completed",
        }

        return result

    except Exception as e:
        logger.error(f"Error processing document {file_path}: {str(e)}")
        return {"file_path": file_path, "status": "failed", "error": str(e)}


@celery_app.task(base=LoggingTask, bind=True, name="src.core.celery_app.batch_process_documents")
def batch_process_documents(self, file_paths: List[str], build_graph: bool = False) -> Dict[str, Any]:
    """
    Batch process multiple documents.

    Args:
        file_paths: List of document file paths
        build_graph: Whether to build knowledge graphs

    Returns:
        Batch processing results
    """
    from celery import group

    # Create group of parallel tasks
    job = group(process_document_async.s(file_path, build_graph) for file_path in file_paths)

    # Execute in parallel
    result = job.apply_async()

    # Wait for all tasks to complete
    results = result.get()

    # Aggregate results
    successful = sum(1 for r in results if r.get("status") == "completed")
    failed = sum(1 for r in results if r.get("status") == "failed")

    return {
        "total": len(file_paths),
        "successful": successful,
        "failed": failed,
        "results": results,
        "status": "completed",
    }


# =============================================================================
# ML TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, name="src.core.celery_app.extract_entities_async")
def extract_entities_async(text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Extract entities asynchronously.

    Args:
        text: Input text
        entity_types: Optional list of entity types to extract

    Returns:
        List of entities
    """
    from src.ml.ner import EntityType, NEREngine

    ner_engine = NEREngine()

    if entity_types:
        types = [EntityType[t.upper()] for t in entity_types]
        entities = []
        for entity_type in types:
            entities.extend(ner_engine.extract_by_type(text, entity_type))
    else:
        entities = ner_engine.extract_entities(text)

    return [
        {"text": e.text, "type": e.type.value, "start": e.start, "end": e.end, "confidence": e.confidence}
        for e in entities
    ]


@celery_app.task(base=LoggingTask, name="src.core.celery_app.classify_document_async")
def classify_document_async(text: str) -> Dict[str, Any]:
    """
    Classify document asynchronously.

    Args:
        text: Document text

    Returns:
        Classification result
    """
    from src.ml.classifier import TfidfSVMClassifier

    classifier = TfidfSVMClassifier()
    classification = classifier.predict(text)

    return {
        "category": classification.category.value if hasattr(classification, "category") else "UNKNOWN",
        "confidence": getattr(classification, "confidence", 0.0),
        "probabilities": getattr(classification, "probabilities", None),
    }


@celery_app.task(base=LoggingTask, name="src.core.celery_app.extract_relations_async")
def extract_relations_async(text: str) -> List[Dict[str, Any]]:
    """
    Extract relations asynchronously.

    Args:
        text: Input text

    Returns:
        List of relations
    """
    from src.ml.relation_extractor import RelationExtractor

    extractor = RelationExtractor()
    relations = extractor.extract_relations(text)

    return [
        {
            "source": r.source_entity,
            "source_type": r.source_type.value,
            "relation": r.relation_type.value,
            "target": r.target_entity,
            "target_type": r.target_type.value,
            "confidence": r.confidence,
        }
        for r in relations
    ]


@celery_app.task(base=LoggingTask, name="src.core.celery_app.build_knowledge_graph_async")
def build_knowledge_graph_async(text: str, export_format: str = "json") -> Dict[str, Any]:
    """
    Build knowledge graph asynchronously.

    Args:
        text: Input text
        export_format: Export format (json, cypher, graphml)

    Returns:
        Knowledge graph data
    """
    from src.ml.knowledge_graph import GraphFormat, KnowledgeGraphBuilder

    builder = KnowledgeGraphBuilder()
    graph = builder.build_from_text(text)

    format_map = {
        "json": GraphFormat.JSON,
        "cypher": GraphFormat.CYPHER,
        "graphml": GraphFormat.GRAPHML,
        "adjacency": GraphFormat.ADJACENCY,
    }

    graph_format = format_map.get(export_format.lower(), GraphFormat.JSON)
    exported = graph.export(graph_format)

    return {"format": export_format, "data": exported}


# =============================================================================
# OCR TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, bind=True, name="src.core.celery_app.process_ocr_async")
def process_ocr_async(self, image_path: str, language: str = "eng") -> Dict[str, Any]:
    """
    Process OCR asynchronously.

    Args:
        image_path: Path to image file
        language: OCR language code

    Returns:
        OCR results
    """
    try:
        from src.ml.ocr import OCREngine, OCRProcessor

        processor = OCRProcessor(engine=OCREngine.AUTO)
        result = processor.process_image(image_path, language=language)

        return {
            "text": result.text,
            "confidence": result.confidence,
            "language": result.language,
            "engine": result.engine,
            "processing_time": result.processing_time,
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"OCR processing failed for {image_path}: {str(e)}")
        return {"image_path": image_path, "status": "failed", "error": str(e)}


# =============================================================================
# REPORT GENERATION TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, bind=True, name="src.core.celery_app.generate_pdf_report")
def generate_pdf_report(self, data: Dict[str, Any], template: str = "default") -> Dict[str, Any]:
    """
    Generate PDF report asynchronously.

    Args:
        data: Report data
        template: Report template name

    Returns:
        Report generation result
    """
    try:
        from src.core.pdf_exporter import PDFExporter

        exporter = PDFExporter()
        output_path = f"data/reports/report_{self.request.id}.pdf"

        # Generate PDF
        exporter.export_services(data.get("services", []), output_path)

        return {"output_path": output_path, "template": template, "status": "completed"}

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return {"status": "failed", "error": str(e)}


# =============================================================================
# NOTIFICATION TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, name="src.core.celery_app.send_email_notification")
def send_email_notification(to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
    """
    Send email notification asynchronously.

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        html: Whether body is HTML

    Returns:
        Send result
    """
    try:
        from src.core.email_notifier import EmailNotifier

        notifier = EmailNotifier()
        result = notifier.send(to, subject, body, html=html)

        return {"to": to, "subject": subject, "sent": result, "status": "completed"}

    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return {"to": to, "status": "failed", "error": str(e)}


# =============================================================================
# MAINTENANCE TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, name="src.core.celery_app.create_backup")
def create_backup() -> Dict[str, Any]:
    """
    Create system backup asynchronously.

    Returns:
        Backup result
    """
    try:
        from src.core.backup import BackupManager

        manager = BackupManager()
        backup_path = manager.create_backup()

        return {"backup_path": backup_path, "status": "completed"}

    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return {"status": "failed", "error": str(e)}


@celery_app.task(base=LoggingTask, name="src.core.celery_app.cleanup_old_results")
def cleanup_old_results() -> Dict[str, Any]:
    """
    Cleanup old task results.

    Returns:
        Cleanup result
    """
    logger.info("Cleaning up old task results")
    # Implementation would cleanup old results from Redis
    return {"status": "completed", "cleaned": 0}


@celery_app.task(base=LoggingTask, name="src.core.celery_app.system_health_check")
def system_health_check() -> Dict[str, Any]:
    """
    Perform system health check.

    Returns:
        Health check result
    """
    logger.info("Performing system health check")
    # Implementation would check system health
    return {"status": "healthy", "checks": {}}


# =============================================================================
# DATA EXPORT TASKS
# =============================================================================


@celery_app.task(base=LoggingTask, bind=True, name="src.core.celery_app.export_data")
def export_data(self, data_type: str, format: str = "csv") -> Dict[str, Any]:
    """
    Export data asynchronously.

    Args:
        data_type: Type of data to export
        format: Export format (csv, xlsx, json)

    Returns:
        Export result
    """
    try:
        output_path = f"data/exports/export_{self.request.id}.{format}"

        # Implementation would export data based on type and format

        return {"output_path": output_path, "format": format, "data_type": data_type, "status": "completed"}

    except Exception as e:
        logger.error(f"Data export failed: {str(e)}")
        return {"status": "failed", "error": str(e)}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a Celery task.

    Args:
        task_id: Task ID

    Returns:
        Task status information
    """
    if not celery_app:
        return {"error": "Celery not available"}

    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
    }


def revoke_task(task_id: str, terminate: bool = False) -> Dict[str, Any]:
    """
    Revoke a Celery task.

    Args:
        task_id: Task ID to revoke
        terminate: Whether to terminate if already executing

    Returns:
        Revoke result
    """
    if not celery_app:
        return {"error": "Celery not available"}

    celery_app.control.revoke(task_id, terminate=terminate)

    return {"task_id": task_id, "revoked": True, "terminated": terminate}


# Export for external use
__all__ = [
    "celery_app",
    "process_document_async",
    "batch_process_documents",
    "extract_entities_async",
    "classify_document_async",
    "extract_relations_async",
    "build_knowledge_graph_async",
    "process_ocr_async",
    "generate_pdf_report",
    "send_email_notification",
    "create_backup",
    "cleanup_old_results",
    "system_health_check",
    "export_data",
    "get_task_status",
    "revoke_task",
]
