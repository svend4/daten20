"""
Automation Module

Provides automation capabilities:
- RPA (Robotic Process Automation)
- ETL (Extract, Transform, Load) pipelines
"""

from .etl import DataSource, ETLEngine, PipelineStatus, TransformationType, get_etl_engine
from .rpa import ActionType, BotStatus, BotType, RPAEngine, configure_rpa_engine, get_rpa_engine

__all__ = [
    "RPAEngine",
    "get_rpa_engine",
    "configure_rpa_engine",
    "ETLEngine",
    "get_etl_engine",
    "BotType",
    "BotStatus",
    "ActionType",
    "DataSource",
    "TransformationType",
    "PipelineStatus",
]
