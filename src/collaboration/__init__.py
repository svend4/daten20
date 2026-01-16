"""
Collaboration Module

Provides team collaboration and real-time editing features.
"""

from .realtime import ConnectionStatus, OperationType, RealtimeEngine, configure_realtime_engine, get_realtime_engine
from .teams import (
    ChannelType,
    CollaborationEngine,
    Permission,
    TeamRole,
    configure_collaboration_engine,
    get_collaboration_engine,
)

__all__ = [
    "CollaborationEngine",
    "get_collaboration_engine",
    "configure_collaboration_engine",
    "RealtimeEngine",
    "get_realtime_engine",
    "configure_realtime_engine",
    "TeamRole",
    "ChannelType",
    "Permission",
    "OperationType",
    "ConnectionStatus",
]
