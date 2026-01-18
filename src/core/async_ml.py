#!/usr/bin/env python3
"""
Asynchronous ML Operations
===========================

Async wrappers for machine learning operations to enable non-blocking processing.

This module provides asyncio-compatible wrappers for CPU-intensive ML operations,
allowing them to run in background threads without blocking the event loop.

Features:
- Async NER (Named Entity Recognition)
- Async document classification
- Async relation extraction
- Async knowledge graph building
- Async OCR processing
- Thread pool management
- Progress tracking
- Timeout handling
- Error recovery

Usage:
    # Using asyncio.to_thread (Python 3.9+)
    entities = await extract_entities_async(text)

    # Using ThreadPoolExecutor
    entities = await run_in_executor(ner_engine.extract_entities, text)

    # Batch processing with progress
    results = await batch_process_async(texts, callback=progress_callback)

Tech Stack:
- asyncio for async/await
- concurrent.futures.ThreadPoolExecutor for CPU-bound tasks
- functools for partial application
- typing for type hints

Author: Document Management System
Version: 1.0.0
"""

import asyncio
import functools
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Global thread pool executor for ML operations
_ml_executor: Optional[ThreadPoolExecutor] = None
_ml_executor_size = 4  # Number of worker threads


def get_ml_executor() -> ThreadPoolExecutor:
    """
    Get or create the global ThreadPoolExecutor for ML operations.

    Returns:
        ThreadPoolExecutor instance
    """
    global _ml_executor
    if _ml_executor is None:
        _ml_executor = ThreadPoolExecutor(
            max_workers=_ml_executor_size, thread_name_prefix="ml_worker"
        )
        logger.info(f"Created ML ThreadPoolExecutor with {_ml_executor_size} workers")
    return _ml_executor


def shutdown_ml_executor():
    """Shutdown the ML executor gracefully"""
    global _ml_executor
    if _ml_executor is not None:
        _ml_executor.shutdown(wait=True)
        _ml_executor = None
        logger.info("ML ThreadPoolExecutor shut down")


async def run_in_executor(func: Callable, *args, **kwargs) -> Any:
    """
    Run a synchronous function in the ML executor.

    Args:
        func: Function to run
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    executor = get_ml_executor()

    # Use functools.partial to bind arguments
    partial_func = functools.partial(func, *args, **kwargs)

    return await loop.run_in_executor(executor, partial_func)


# =============================================================================
# ASYNC NER OPERATIONS
# =============================================================================


async def extract_entities_async(
    text: str,
    entity_types: Optional[List[str]] = None,
    timeout: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Extract named entities asynchronously.

    Args:
        text: Input text
        entity_types: Optional list of entity types to extract
        timeout: Optional timeout in seconds

    Returns:
        List of extracted entities

    Raises:
        asyncio.TimeoutError: If operation times out
        Exception: If extraction fails
    """
    from src.ml.ner import EntityType, NEREngine

    logger.debug(f"Starting async entity extraction (text length: {len(text)})")
    start_time = time.time()

    try:
        ner_engine = NEREngine()

        # Define extraction function
        def _extract():
            if entity_types:
                types = [EntityType[t.upper()] for t in entity_types]
                entities = []
                for entity_type in types:
                    entities.extend(ner_engine.extract_by_type(text, entity_type))
                return entities
            else:
                return ner_engine.extract_entities(text)

        # Run in executor with optional timeout
        if timeout:
            entities = await asyncio.wait_for(
                run_in_executor(_extract), timeout=timeout
            )
        else:
            entities = await run_in_executor(_extract)

        elapsed = time.time() - start_time
        logger.debug(f"Entity extraction completed in {elapsed:.2f}s ({len(entities)} entities)")

        return [
            {
                "text": e.text,
                "type": e.type.value,
                "start": e.start,
                "end": e.end,
                "confidence": e.confidence,
            }
            for e in entities
        ]

    except asyncio.TimeoutError:
        logger.error(f"Entity extraction timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Entity extraction failed: {str(e)}")
        raise


async def extract_entities_batch_async(
    texts: List[str],
    entity_types: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[List[Dict[str, Any]]]:
    """
    Extract entities from multiple texts asynchronously.

    Args:
        texts: List of input texts
        entity_types: Optional list of entity types
        progress_callback: Optional callback(completed, total)

    Returns:
        List of entity lists (one per input text)
    """
    logger.info(f"Starting batch entity extraction ({len(texts)} texts)")
    start_time = time.time()

    # Create tasks for all texts
    tasks = [
        extract_entities_async(text, entity_types)
        for text in texts
    ]

    # Process with progress tracking
    results = []
    for i, task in enumerate(asyncio.as_completed(tasks)):
        result = await task
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, len(texts))

    elapsed = time.time() - start_time
    logger.info(f"Batch entity extraction completed in {elapsed:.2f}s")

    return results


# =============================================================================
# ASYNC CLASSIFICATION
# =============================================================================


async def classify_document_async(
    text: str,
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """
    Classify document asynchronously.

    Args:
        text: Document text
        timeout: Optional timeout in seconds

    Returns:
        Classification result with category and confidence

    Raises:
        asyncio.TimeoutError: If operation times out
    """
    from src.ml.classifier import TfidfSVMClassifier

    logger.debug(f"Starting async document classification (text length: {len(text)})")
    start_time = time.time()

    try:
        classifier = TfidfSVMClassifier()

        # Run classification in executor
        if timeout:
            classification = await asyncio.wait_for(
                run_in_executor(classifier.predict, text),
                timeout=timeout
            )
        else:
            classification = await run_in_executor(classifier.predict, text)

        elapsed = time.time() - start_time
        logger.debug(f"Classification completed in {elapsed:.2f}s")

        return {
            "category": classification.category.value if hasattr(classification, "category") else "UNKNOWN",
            "confidence": getattr(classification, "confidence", 0.0),
            "probabilities": getattr(classification, "probabilities", None),
        }

    except asyncio.TimeoutError:
        logger.error(f"Classification timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise


async def classify_batch_async(
    texts: List[str],
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Dict[str, Any]]:
    """
    Classify multiple documents asynchronously.

    Args:
        texts: List of document texts
        progress_callback: Optional progress callback

    Returns:
        List of classification results
    """
    logger.info(f"Starting batch classification ({len(texts)} documents)")
    start_time = time.time()

    tasks = [classify_document_async(text) for text in texts]

    results = []
    for i, task in enumerate(asyncio.as_completed(tasks)):
        result = await task
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, len(texts))

    elapsed = time.time() - start_time
    logger.info(f"Batch classification completed in {elapsed:.2f}s")

    return results


# =============================================================================
# ASYNC RELATION EXTRACTION
# =============================================================================


async def extract_relations_async(
    text: str,
    timeout: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Extract relations asynchronously.

    Args:
        text: Input text
        timeout: Optional timeout in seconds

    Returns:
        List of extracted relations
    """
    from src.ml.relation_extractor import RelationExtractor

    logger.debug(f"Starting async relation extraction (text length: {len(text)})")
    start_time = time.time()

    try:
        extractor = RelationExtractor()

        if timeout:
            relations = await asyncio.wait_for(
                run_in_executor(extractor.extract_relations, text),
                timeout=timeout
            )
        else:
            relations = await run_in_executor(extractor.extract_relations, text)

        elapsed = time.time() - start_time
        logger.debug(f"Relation extraction completed in {elapsed:.2f}s ({len(relations)} relations)")

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

    except asyncio.TimeoutError:
        logger.error(f"Relation extraction timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Relation extraction failed: {str(e)}")
        raise


# =============================================================================
# ASYNC KNOWLEDGE GRAPH
# =============================================================================


async def build_knowledge_graph_async(
    text: str,
    export_format: str = "json",
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """
    Build knowledge graph asynchronously.

    Args:
        text: Input text
        export_format: Export format (json, cypher, graphml)
        timeout: Optional timeout in seconds

    Returns:
        Knowledge graph data
    """
    from src.ml.knowledge_graph import GraphFormat, KnowledgeGraphBuilder

    logger.debug(f"Starting async knowledge graph building (text length: {len(text)})")
    start_time = time.time()

    try:
        builder = KnowledgeGraphBuilder()

        # Build graph
        if timeout:
            graph = await asyncio.wait_for(
                run_in_executor(builder.build_from_text, text),
                timeout=timeout
            )
        else:
            graph = await run_in_executor(builder.build_from_text, text)

        # Export
        format_map = {
            "json": GraphFormat.JSON,
            "cypher": GraphFormat.CYPHER,
            "graphml": GraphFormat.GRAPHML,
            "adjacency": GraphFormat.ADJACENCY,
        }

        graph_format = format_map.get(export_format.lower(), GraphFormat.JSON)
        exported = graph.export(graph_format)

        elapsed = time.time() - start_time
        logger.debug(f"Knowledge graph building completed in {elapsed:.2f}s")

        return {"format": export_format, "data": exported}

    except asyncio.TimeoutError:
        logger.error(f"Knowledge graph building timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Knowledge graph building failed: {str(e)}")
        raise


# =============================================================================
# ASYNC OCR
# =============================================================================


async def process_ocr_async(
    image_path: str,
    language: str = "eng",
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """
    Process OCR asynchronously.

    Args:
        image_path: Path to image file
        language: OCR language code
        timeout: Optional timeout in seconds

    Returns:
        OCR results
    """
    from src.ml.ocr import OCREngine, OCRProcessor

    logger.debug(f"Starting async OCR processing: {image_path}")
    start_time = time.time()

    try:
        processor = OCRProcessor(engine=OCREngine.AUTO)

        if timeout:
            result = await asyncio.wait_for(
                run_in_executor(processor.process_image, image_path, language),
                timeout=timeout
            )
        else:
            result = await run_in_executor(processor.process_image, image_path, language)

        elapsed = time.time() - start_time
        logger.debug(f"OCR processing completed in {elapsed:.2f}s")

        return {
            "text": result.text,
            "confidence": result.confidence,
            "language": result.language,
            "engine": result.engine,
            "processing_time": result.processing_time,
        }

    except asyncio.TimeoutError:
        logger.error(f"OCR processing timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise


# =============================================================================
# ASYNC DOCUMENT PROCESSING
# =============================================================================


async def process_document_async(
    file_path: str,
    build_graph: bool = False,
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """
    Process document with full pipeline asynchronously.

    Args:
        file_path: Path to document file
        build_graph: Whether to build knowledge graph
        timeout: Optional timeout in seconds

    Returns:
        Complete processing results
    """
    from src.core.parser import DocumentParser

    logger.info(f"Starting async document processing: {file_path}")
    start_time = time.time()

    try:
        # Parse document
        parser = DocumentParser()
        parsed = await run_in_executor(parser.parse, file_path)
        text = parsed.get("text", "")

        # Run ML operations in parallel
        tasks = [
            extract_entities_async(text, timeout=timeout),
            classify_document_async(text, timeout=timeout),
            extract_relations_async(text, timeout=timeout),
        ]

        if build_graph:
            tasks.append(build_knowledge_graph_async(text, timeout=timeout))

        # Wait for all tasks
        if timeout:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=timeout
            )
        else:
            results = await asyncio.gather(*tasks)

        # Unpack results
        entities = results[0]
        classification = results[1]
        relations = results[2]
        knowledge_graph = results[3] if build_graph else None

        elapsed = time.time() - start_time
        logger.info(f"Document processing completed in {elapsed:.2f}s")

        return {
            "file_path": file_path,
            "text_length": len(text),
            "word_count": len(text.split()),
            "entity_count": len(entities),
            "relation_count": len(relations),
            "classification": classification,
            "entities": entities,
            "relations": relations,
            "knowledge_graph": knowledge_graph,
            "processing_time": elapsed,
            "status": "completed",
        }

    except asyncio.TimeoutError:
        logger.error(f"Document processing timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        raise


async def process_documents_batch_async(
    file_paths: List[str],
    build_graph: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    Process multiple documents asynchronously with concurrency limit.

    Args:
        file_paths: List of document file paths
        build_graph: Whether to build knowledge graphs
        progress_callback: Optional progress callback
        max_concurrent: Maximum concurrent operations

    Returns:
        List of processing results
    """
    logger.info(f"Starting batch document processing ({len(file_paths)} files, max_concurrent={max_concurrent})")
    start_time = time.time()

    # Use semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(file_path: str) -> Dict[str, Any]:
        async with semaphore:
            return await process_document_async(file_path, build_graph)

    # Create tasks
    tasks = [process_with_semaphore(fp) for fp in file_paths]

    # Process with progress tracking
    results = []
    completed = 0

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed += 1

        if progress_callback:
            progress_callback(completed, len(file_paths))

    elapsed = time.time() - start_time
    successful = sum(1 for r in results if r.get("status") == "completed")
    failed = len(results) - successful

    logger.info(
        f"Batch processing completed in {elapsed:.2f}s "
        f"(successful: {successful}, failed: {failed})"
    )

    return results


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


async def with_retry(
    coro_func: Callable,
    *args,
    max_retries: int = 3,
    delay: float = 1.0,
    **kwargs
) -> Any:
    """
    Execute async function with retry logic.

    Args:
        coro_func: Async function to execute
        *args: Positional arguments
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        **kwargs: Keyword arguments

    Returns:
        Function result

    Raises:
        Exception: If all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    raise last_exception


async def gather_with_progress(
    tasks: List[asyncio.Task],
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Any]:
    """
    Gather async tasks with progress tracking.

    Args:
        tasks: List of async tasks
        progress_callback: Optional callback(completed, total)

    Returns:
        List of task results
    """
    total = len(tasks)
    completed = 0
    results = []

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed += 1

        if progress_callback:
            progress_callback(completed, total)

    return results


# Export public API
__all__ = [
    "get_ml_executor",
    "shutdown_ml_executor",
    "run_in_executor",
    "extract_entities_async",
    "extract_entities_batch_async",
    "classify_document_async",
    "classify_batch_async",
    "extract_relations_async",
    "build_knowledge_graph_async",
    "process_ocr_async",
    "process_document_async",
    "process_documents_batch_async",
    "with_retry",
    "gather_with_progress",
]
