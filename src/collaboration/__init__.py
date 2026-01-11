"""
Collaboration Module

Provides team collaboration and real-time editing features.
"""

from .teams import (
    CollaborationEngine,
    get_collaboration_engine,
    configure_collaboration_engine,
    TeamRole,
    ChannelType,
    Permission
)

from .realtime import (
    RealtimeEngine,
    get_realtime_engine,
    configure_realtime_engine,
    OperationType,
    ConnectionStatus
)

__all__ = [
    'CollaborationEngine',
    'get_collaboration_engine',
    'configure_collaboration_engine',
    'RealtimeEngine',
    'get_realtime_engine',
    'configure_realtime_engine',
    'TeamRole',
    'ChannelType',
    'Permission',
    'OperationType',
    'ConnectionStatus'
]
