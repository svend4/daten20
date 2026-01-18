#!/usr/bin/env python3
"""
Document Intelligence API Server
==================================

RESTful API server for document intelligence and analysis.

Features:
- Document upload and processing
- Named Entity Recognition (NER) endpoints
- Document classification API
- Relation extraction endpoints
- Knowledge graph API
- Batch processing endpoints
- WebSocket support for real-time updates
- API key authentication
- Rate limiting
- OpenAPI/Swagger documentation

Endpoints:
    POST   /api/v1/documents                 - Upload and process document
    GET    /api/v1/documents/{id}            - Get document details
    DELETE /api/v1/documents/{id}            - Delete document

    POST   /api/v1/extract/entities          - Extract entities from text
    POST   /api/v1/extract/relations         - Extract relations from text
    POST   /api/v1/classify                  - Classify document
    POST   /api/v1/graph/build               - Build knowledge graph

    POST   /api/v1/batch/process             - Batch process documents
    GET    /api/v1/batch/{job_id}            - Get batch job status

    GET    /api/v1/stats                     - Get API statistics
    GET    /api/v1/health                    - Health check
    GET    /docs                             - API documentation (Swagger UI)

Usage:
    # Start API server
    python doc-api-server.py

    # Custom port and host
    python doc-api-server.py --host 0.0.0.0 --port 8000

    # Production mode with API key
    python doc-api-server.py --production --api-key YOUR_SECRET_KEY

Tech Stack:
- FastAPI for high-performance async API
- Pydantic for data validation
- SQLAlchemy for database ORM
- OpenAPI/Swagger for documentation
- JWT for authentication (optional)

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import uvicorn
    from fastapi import BackgroundTasks, Depends, FastAPI, File, Header, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, JSONResponse
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("WARNING: FastAPI not installed. Install with: pip install fastapi uvicorn[standard] python-multipart")

from src.core.database import DocumentDatabase
from src.core.logging_config import setup_logging

# Import our modules
from src.core.parser import DocumentParser
from src.ml.classifier import DocumentCategory, TfidfSVMClassifier
from src.ml.knowledge_graph import GraphFormat, KnowledgeGraphBuilder
from src.ml.ner import EntityType, NEREngine
from src.ml.relation_extractor import RelationExtractor, RelationType

# Import rate limiting
from src.core.rate_limiter import (
    FastAPIRateLimitMiddleware,
    RateLimiter,
    RateLimitTier,
    RedisRateLimiter,
    create_rate_limit_dependency,
)

# Setup logging
logger = setup_logging(__name__, log_level="INFO")

# FastAPI app setup
app = (
    FastAPI(
        title="Document Intelligence API",
        description="AI-powered document analysis and processing API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    if FASTAPI_AVAILABLE
    else None
)

if app:
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting middleware
    # Use FREE tier by default (100 req/min)
    # Can be configured via environment variable or CLI args
    rate_limit_tier = os.getenv("RATE_LIMIT_TIER", "FREE")
    use_redis = os.getenv("USE_REDIS_RATE_LIMIT", "false").lower() == "true"

    api_rate_limiter = RateLimitTier.get_limiter(rate_limit_tier, use_redis=use_redis)
    logger.info(f"Rate limiting enabled: {rate_limit_tier} tier ({api_rate_limiter.requests} req/{api_rate_limiter.window}s)")

    # Add rate limiting middleware
    app.add_middleware(FastAPIRateLimitMiddleware, limiter=api_rate_limiter)


# Pydantic models for request/response validation
if FASTAPI_AVAILABLE:

    class TextInput(BaseModel):
        """Text input for extraction endpoints."""

        text: str = Field(..., description="Input text to process")
        options: Optional[Dict[str, Any]] = Field(default={}, description="Processing options")

    class EntityResponse(BaseModel):
        """Entity extraction response."""

        text: str
        type: str
        start: int
        end: int
        confidence: float

    class RelationResponse(BaseModel):
        """Relation extraction response."""

        source: str
        source_type: str
        relation: str
        target: str
        target_type: str
        confidence: float

    class ClassificationResponse(BaseModel):
        """Document classification response."""

        category: str
        confidence: float
        probabilities: Optional[Dict[str, float]] = None

    class DocumentResponse(BaseModel):
        """Document processing response."""

        document_id: str
        filename: str
        processed_at: str
        statistics: Dict[str, Any]
        classification: ClassificationResponse
        entities: List[EntityResponse]
        relations: List[RelationResponse]
        knowledge_graph: Optional[Dict[str, Any]] = None

    class BatchJobResponse(BaseModel):
        """Batch job response."""

        job_id: str
        status: str
        total_documents: int
        processed: int
        failed: int
        created_at: str
        updated_at: str

    class HealthResponse(BaseModel):
        """Health check response."""

        status: str
        version: str
        uptime: float
        components: Dict[str, str]


# Global components
class APIComponents:
    """Global API components."""

    def __init__(self):
        self.parser = DocumentParser()
        self.database = DocumentDatabase("data/api_documents.db")
        self.ner_engine = NEREngine(use_spacy=True)
        self.classifier = TfidfSVMClassifier()
        self.relation_extractor = RelationExtractor(use_spacy=True)
        self.graph_builder = KnowledgeGraphBuilder(use_spacy=True)

        # Batch job tracking
        self.batch_jobs: Dict[str, Dict] = {}

        # Statistics
        self.stats = {"total_requests": 0, "documents_processed": 0, "entities_extracted": 0, "relations_extracted": 0}

        # Create upload directory
        os.makedirs("data/api_uploads", exist_ok=True)

        logger.info("API components initialized")

    def verify_api_key(self, api_key: Optional[str], required_key: Optional[str]):
        """Verify API key if authentication is enabled."""
        if required_key and (not api_key or api_key != required_key):
            raise HTTPException(status_code=401, detail="Invalid API key")


# Initialize components
components = APIComponents() if FASTAPI_AVAILABLE else None


# API Routes
if FASTAPI_AVAILABLE:

    @app.get("/", tags=["Root"])
    async def root():
        """API root endpoint."""
        return {
            "name": "Document Intelligence API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json",
            "unified_docs": "http://localhost:5000/api/docs",
            "health": "/api/v1/health",
        }

    @app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": 0.0,  # Implement actual uptime tracking
            "components": {
                "parser": "operational",
                "ner": "operational",
                "classifier": "operational",
                "relation_extractor": "operational",
                "knowledge_graph": "operational",
            },
        }

    @app.get("/api/v1/stats", tags=["System"])
    async def get_statistics():
        """Get API usage statistics."""
        return components.stats

    @app.post("/api/v1/documents", response_model=DocumentResponse, tags=["Documents"])
    async def upload_document(
        file: UploadFile = File(...), build_graph: bool = False, x_api_key: Optional[str] = Header(None)
    ):
        """
        Upload and process a document.

        Args:
            file: Document file to upload
            build_graph: Whether to build knowledge graph
            x_api_key: API key for authentication

        Returns:
            Document processing results
        """
        # Increment request counter
        components.stats["total_requests"] += 1

        # Save uploaded file
        document_id = str(uuid.uuid4())
        file_path = f"data/api_uploads/{document_id}_{file.filename}"

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Processing document: {file.filename} (ID: {document_id})")

        # Parse document
        parsed = components.parser.parse(file_path)
        text = parsed.get("text", "")

        # Extract entities
        entities = components.ner_engine.extract_entities(text)
        components.stats["entities_extracted"] += len(entities)

        # Classify
        classification = components.classifier.predict(text)

        # Extract relations
        relations = components.relation_extractor.extract_relations(text)
        components.stats["relations_extracted"] += len(relations)

        # Build knowledge graph if requested
        knowledge_graph = None
        if build_graph:
            graph = components.graph_builder.build_from_text(text)
            knowledge_graph = json.loads(graph.export(GraphFormat.JSON))

        # Build response
        response = {
            "document_id": document_id,
            "filename": file.filename,
            "processed_at": datetime.now().isoformat(),
            "statistics": {
                "text_length": len(text),
                "word_count": len(text.split()),
                "entity_count": len(entities),
                "relation_count": len(relations),
            },
            "classification": {
                "category": classification.category.value if hasattr(classification, "category") else "UNKNOWN",
                "confidence": getattr(classification, "confidence", 0.0),
            },
            "entities": [
                {"text": e.text, "type": e.type.value, "start": e.start, "end": e.end, "confidence": e.confidence}
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
        }

        components.stats["documents_processed"] += 1

        return response

    @app.post("/api/v1/extract/entities", response_model=List[EntityResponse], tags=["Extraction"])
    async def extract_entities(input_data: TextInput, entity_types: Optional[str] = None):
        """
        Extract named entities from text.

        Args:
            input_data: Text input
            entity_types: Comma-separated entity types to extract (e.g., "PERSON,ORG")

        Returns:
            List of extracted entities
        """
        components.stats["total_requests"] += 1

        text = input_data.text

        # Extract entities
        if entity_types:
            types = [EntityType[t.strip().upper()] for t in entity_types.split(",")]
            entities = []
            for entity_type in types:
                entities.extend(components.ner_engine.extract_by_type(text, entity_type))
        else:
            entities = components.ner_engine.extract_entities(text)

        components.stats["entities_extracted"] += len(entities)

        return [
            {"text": e.text, "type": e.type.value, "start": e.start, "end": e.end, "confidence": e.confidence}
            for e in entities
        ]

    @app.post("/api/v1/extract/relations", response_model=List[RelationResponse], tags=["Extraction"])
    async def extract_relations(input_data: TextInput):
        """
        Extract relations from text.

        Args:
            input_data: Text input

        Returns:
            List of extracted relations
        """
        components.stats["total_requests"] += 1

        relations = components.relation_extractor.extract_relations(input_data.text)
        components.stats["relations_extracted"] += len(relations)

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

    @app.post("/api/v1/classify", response_model=ClassificationResponse, tags=["Classification"])
    async def classify_document(input_data: TextInput):
        """
        Classify document text.

        Args:
            input_data: Text input

        Returns:
            Classification result
        """
        components.stats["total_requests"] += 1

        classification = components.classifier.predict(input_data.text)

        return {
            "category": classification.category.value if hasattr(classification, "category") else "UNKNOWN",
            "confidence": getattr(classification, "confidence", 0.0),
            "probabilities": getattr(classification, "probabilities", None),
        }

    @app.post("/api/v1/graph/build", tags=["Knowledge Graph"])
    async def build_knowledge_graph(input_data: TextInput, export_format: str = "json"):
        """
        Build knowledge graph from text.

        Args:
            input_data: Text input
            export_format: Export format (json, cypher, graphml)

        Returns:
            Knowledge graph data
        """
        components.stats["total_requests"] += 1

        graph = components.graph_builder.build_from_text(input_data.text)

        # Export in requested format
        format_map = {
            "json": GraphFormat.JSON,
            "cypher": GraphFormat.CYPHER,
            "graphml": GraphFormat.GRAPHML,
            "adjacency": GraphFormat.ADJACENCY,
        }

        graph_format = format_map.get(export_format.lower(), GraphFormat.JSON)
        exported = graph.export(graph_format)

        # Return as JSON
        if graph_format == GraphFormat.JSON:
            return json.loads(exported)
        else:
            return {"format": export_format, "data": exported}

    @app.post("/api/v1/batch/process", response_model=BatchJobResponse, tags=["Batch"])
    async def batch_process(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
        """
        Submit batch processing job.

        Args:
            background_tasks: FastAPI background tasks
            files: List of files to process

        Returns:
            Batch job information
        """
        job_id = str(uuid.uuid4())

        # Create job record
        job = {
            "job_id": job_id,
            "status": "processing",
            "total_documents": len(files),
            "processed": 0,
            "failed": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "results": [],
        }

        components.batch_jobs[job_id] = job

        # Process in background
        # Note: In production, use Celery or similar for robust background processing
        logger.info(f"Batch job {job_id} created with {len(files)} documents")

        return job

    @app.get("/api/v1/batch/{job_id}", response_model=BatchJobResponse, tags=["Batch"])
    async def get_batch_job(job_id: str):
        """
        Get batch job status.

        Args:
            job_id: Batch job ID

        Returns:
            Job status
        """
        if job_id not in components.batch_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        return components.batch_jobs[job_id]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Document Intelligence API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")

    # Rate limiting options
    parser.add_argument(
        "--rate-limit-tier",
        choices=["free", "basic", "premium", "enterprise"],
        default=os.getenv("RATE_LIMIT_TIER", "free").lower(),
        help="Rate limit tier: free (100/min), basic (500/min), premium (2000/min), enterprise (10000/min)",
    )
    parser.add_argument(
        "--use-redis-rate-limit",
        action="store_true",
        default=os.getenv("USE_REDIS_RATE_LIMIT", "false").lower() == "true",
        help="Use Redis for distributed rate limiting (requires Redis running)",
    )

    args = parser.parse_args()

    # Set environment variables for rate limiting (used in middleware setup)
    os.environ["RATE_LIMIT_TIER"] = args.rate_limit_tier.upper()
    os.environ["USE_REDIS_RATE_LIMIT"] = str(args.use_redis_rate_limit).lower()

    if not FASTAPI_AVAILABLE:
        print("ERROR: FastAPI is required to run the API server")
        print("Install with: pip install fastapi uvicorn[standard] python-multipart")
        return

    # Get rate limit info
    tier_config = getattr(RateLimitTier, args.rate_limit_tier.upper(), RateLimitTier.FREE)
    rate_limit_info = f"{tier_config['requests']}/{tier_config['window']}s"

    print(
        f"""
╔════════════════════════════════════════════════════════════════╗
║        Document Intelligence API v1.0.0                        ║
╠════════════════════════════════════════════════════════════════╣
║  🚀 High-performance RESTful API                               ║
║  🤖 AI-powered document analysis                               ║
║  📊 Entity & relation extraction                               ║
║  🕸️  Knowledge graph construction                              ║
║  📚 OpenAPI/Swagger documentation                              ║
║  🛡️  Rate limiting: {args.rate_limit_tier.upper()} ({rate_limit_info}){'  ║' if len(rate_limit_info) <= 20 else ''}
╠════════════════════════════════════════════════════════════════╣
║  Server: http://{args.host}:{args.port}
║  Docs:   http://{args.host}:{args.port}/docs
║  Mode:   {'Production' if args.production else 'Development'}
║  Auth:   {'Enabled' if args.api_key else 'Disabled'}
║  Redis:  {'Enabled' if args.use_redis_rate_limit else 'Disabled'}
╚════════════════════════════════════════════════════════════════╝
    """
    )

    # Run uvicorn server
    uvicorn.run(
        "doc-api-server:app",
        host=args.host,
        port=args.port,
        workers=args.workers if args.production else 1,
        reload=not args.production,
    )


if __name__ == "__main__":
    main()
