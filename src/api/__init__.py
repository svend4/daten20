"""
API Module
==========

FastAPI endpoints and utilities for Document Management System.

Modules:
- async_endpoints: Fully async API endpoints with Celery support
"""

from .async_endpoints import (
    BatchJobResponse,
    DocumentResponse,
    TaskStatusResponse,
    TextInput,
    benchmark_async_vs_sync,
    register_async_endpoints,
)

__all__ = [
    "register_async_endpoints",
    "DocumentResponse",
    "TextInput",
    "BatchJobResponse",
    "TaskStatusResponse",
    "benchmark_async_vs_sync",
]
