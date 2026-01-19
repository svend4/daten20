"""
Example: Distributed Tracing Integration
Phase 4 - TASK 38

This example demonstrates how to integrate distributed tracing
into your DMS application using OpenTelemetry and Jaeger.

Usage:
    python examples/tracing_example.py

Requirements:
    - Jaeger running (via docker-compose.monitoring.yml)
    - OpenTelemetry packages installed

View traces at: http://localhost:16686 (Jaeger UI)

Author: DMS Development Team
Date: 2026-01-16
"""

import time
from flask import Flask, request, jsonify
from src.core.tracing import (
    init_tracing,
    traced,
    traced_api,
    traced_db,
    traced_ml,
    add_span_attribute,
    add_span_event,
    create_span,
    shutdown_tracing,
)

# ==================== FLASK APP SETUP ====================

app = Flask(__name__)

# Initialize tracing
# This should be called once at application startup
tracer = init_tracing(
    app_name="dms-api",
    environment="development",
    jaeger_host="localhost",
    jaeger_port=6831,
    enable_console=True,  # Also print traces to console
)

print("✅ Distributed tracing initialized!")
print("📊 View traces at: http://localhost:16686")


# ==================== EXAMPLE 1: API ENDPOINT TRACING ====================


@app.route("/api/documents", methods=["GET"])
@traced_api("/api/documents")
def list_documents():
    """
    Example API endpoint with tracing.

    Trace will include:
    - HTTP method, status code, duration
    - Custom attributes
    - Events
    """
    # Add custom attributes to the current span
    add_span_attribute("user.id", request.args.get("user_id", "anonymous"))
    add_span_attribute("page", request.args.get("page", 1))

    # Simulate database query
    documents = fetch_documents_from_db()

    # Add event to the span
    add_span_event("documents_fetched", {"count": len(documents)})

    return jsonify({
        "documents": documents,
        "total": len(documents)
    })


# ==================== EXAMPLE 2: DATABASE OPERATION TRACING ====================


@traced_db("SELECT", "documents")
def fetch_documents_from_db():
    """
    Example database operation with tracing.

    Trace will include:
    - Database operation type
    - Table name
    - Query duration
    """
    # Simulate database query
    time.sleep(0.1)  # Simulate DB latency

    # Add query details to span
    add_span_attribute("db.rows_returned", 10)
    add_span_attribute("db.query_time_ms", 100)

    return [
        {"id": 1, "title": "Document 1"},
        {"id": 2, "title": "Document 2"},
        # ... more documents
    ]


# ==================== EXAMPLE 3: ML OPERATION TRACING ====================


@app.route("/api/documents/<int:doc_id>/analyze", methods=["POST"])
@traced_api("/api/documents/analyze")
def analyze_document(doc_id):
    """
    Example ML endpoint with tracing.
    """
    add_span_attribute("document.id", doc_id)

    # Fetch document
    document = get_document(doc_id)

    # Extract entities
    entities = extract_entities(document["text"])

    # Classify document
    classification = classify_document(document["text"])

    return jsonify({
        "document_id": doc_id,
        "entities": entities,
        "classification": classification
    })


@traced_db("SELECT", "documents")
def get_document(doc_id):
    """Fetch document from database."""
    time.sleep(0.05)
    return {
        "id": doc_id,
        "title": "Sample Document",
        "text": "This is a sample document for NER analysis."
    }


@traced_ml("spacy", "ner")
def extract_entities(text):
    """Extract named entities using spaCy."""
    # Simulate NER processing
    time.sleep(0.2)

    entities = [
        {"text": "Sample", "label": "ORG"},
        {"text": "Document", "label": "PRODUCT"},
    ]

    add_span_attribute("entities.count", len(entities))
    add_span_event("ner_complete", {"model": "en_core_web_sm"})

    return entities


@traced_ml("sklearn", "classify")
def classify_document(text):
    """Classify document using ML model."""
    # Simulate classification
    time.sleep(0.15)

    result = {
        "category": "technical",
        "confidence": 0.95
    }

    add_span_attribute("classification.category", result["category"])
    add_span_attribute("classification.confidence", result["confidence"])

    return result


# ==================== EXAMPLE 4: MANUAL SPAN CREATION ====================


@app.route("/api/documents/<int:doc_id>/process", methods=["POST"])
@traced_api("/api/documents/process")
def process_document(doc_id):
    """
    Example with manual span creation for fine-grained tracing.
    """
    add_span_attribute("document.id", doc_id)

    # Phase 1: Fetch document
    with create_span("fetch_document", {"doc_id": doc_id}):
        time.sleep(0.05)
        document = {"id": doc_id, "content": "..."}

    # Phase 2: Parse document
    with create_span("parse_document", {"format": "pdf"}):
        time.sleep(0.1)
        parsed = {"text": "parsed content"}

    # Phase 3: Analyze document
    with create_span("analyze_document"):
        # Sub-span: Extract entities
        with create_span("extract_entities"):
            time.sleep(0.2)
            entities = []

        # Sub-span: Classify
        with create_span("classify"):
            time.sleep(0.15)
            classification = "technical"

    return jsonify({
        "status": "processed",
        "document_id": doc_id
    })


# ==================== EXAMPLE 5: ERROR TRACKING ====================


@app.route("/api/documents/<int:doc_id>/error", methods=["GET"])
@traced_api("/api/documents/error")
def error_example(doc_id):
    """
    Example showing how errors are automatically captured in traces.
    """
    add_span_attribute("document.id", doc_id)

    try:
        # Simulate an error
        if doc_id == 404:
            raise ValueError("Document not found")

        return jsonify({"status": "ok"})

    except ValueError as e:
        # Error is automatically recorded in the span
        # with full stack trace and exception details
        raise


# ==================== EXAMPLE 6: NESTED SERVICE CALLS ====================


@app.route("/api/workflow/<int:workflow_id>", methods=["POST"])
@traced_api("/api/workflow")
def execute_workflow(workflow_id):
    """
    Example showing distributed tracing across multiple service calls.

    This would create a trace tree showing:
    - Parent: execute_workflow
    - Child 1: fetch_workflow_config
    - Child 2: process_step_1
    - Child 3: process_step_2
    - Child 4: send_notification
    """
    add_span_attribute("workflow.id", workflow_id)

    # Step 1: Fetch workflow configuration
    config = fetch_workflow_config(workflow_id)

    # Step 2: Execute workflow steps
    result_1 = process_step("step1", config)
    result_2 = process_step("step2", config)

    # Step 3: Send notification
    send_notification(workflow_id, "completed")

    return jsonify({
        "workflow_id": workflow_id,
        "status": "completed"
    })


@traced(name="fetch_workflow_config")
def fetch_workflow_config(workflow_id):
    """Fetch workflow configuration."""
    time.sleep(0.05)
    return {"steps": ["step1", "step2"]}


@traced(name="process_workflow_step")
def process_step(step_name, config):
    """Process a workflow step."""
    add_span_attribute("step.name", step_name)
    time.sleep(0.1)
    return {"status": "completed"}


@traced(name="send_notification")
def send_notification(workflow_id, status):
    """Send workflow notification."""
    add_span_attribute("notification.type", "email")
    time.sleep(0.05)


# ==================== HEALTH CHECK ====================


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint (not traced to reduce noise)."""
    return jsonify({"status": "healthy"})


# ==================== APP TEARDOWN ====================


@app.teardown_appcontext
def cleanup(exception=None):
    """Cleanup function called at app shutdown."""
    # Flush all pending traces
    shutdown_tracing()


# ==================== MAIN ====================


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 DMS Tracing Example Server")
    print("="*60)
    print("\n📋 Available endpoints:")
    print("  GET  /api/documents              - List documents")
    print("  POST /api/documents/<id>/analyze - Analyze document")
    print("  POST /api/documents/<id>/process - Process document")
    print("  GET  /api/documents/<id>/error   - Error example")
    print("  POST /api/workflow/<id>          - Execute workflow")
    print("\n📊 Jaeger UI: http://localhost:16686")
    print("\n🧪 Test commands:")
    print("  curl http://localhost:5555/api/documents")
    print("  curl -X POST http://localhost:5555/api/documents/1/analyze")
    print("  curl -X POST http://localhost:5555/api/workflow/123")
    print("\n⚠️  Make sure Jaeger is running:")
    print("  docker-compose -f docker-compose.monitoring.yml up jaeger")
    print("="*60 + "\n")

    try:
        # Run Flask app
        app.run(host="0.0.0.0", port=5555, debug=True)
    finally:
        # Ensure traces are flushed on shutdown
        print("\n🛑 Shutting down tracing...")
        shutdown_tracing()
        print("✅ Tracing shutdown complete!")
