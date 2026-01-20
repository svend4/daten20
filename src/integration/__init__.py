"""
Integration Pipeline for DATEN20 Advanced AI Services.

This module provides unified access to all DATEN20 modules (v22-v27) through
an integrated pipeline that enables cross-module workflows and complex AI tasks.

Usage:
    from src.integration import IntegratedPipeline

    pipeline = IntegratedPipeline()
    result = await pipeline.solve_complex_task(task_spec)
"""

from .pipeline import IntegratedPipeline, PipelineConfig, PipelineResult, PipelineMode

__all__ = [
    'IntegratedPipeline',
    'PipelineConfig',
    'PipelineResult',
    'PipelineMode',
]

__version__ = '1.0.0'
