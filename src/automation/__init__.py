"""
Automation Module

Provides automation capabilities:
- RPA (Robotic Process Automation)
- ETL (Extract, Transform, Load) pipelines
"""

from .rpa import (
    RPAEngine,
    get_rpa_engine,
    configure_rpa_engine,
    BotType,
    BotStatus,
    ActionType
)

from .etl import (
    ETLEngine,
    get_etl_engine,
    DataSource,
    TransformationType,
    PipelineStatus
)

__all__ = [
    'RPAEngine',
    'get_rpa_engine',
    'configure_rpa_engine',
    'ETLEngine',
    'get_etl_engine',
    'BotType',
    'BotStatus',
    'ActionType',
    'DataSource',
    'TransformationType',
    'PipelineStatus'
]
