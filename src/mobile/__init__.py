"""
Mobile Module - v3.3

Mobile backend services for native and cross-platform SDKs.

Modules:
- mobile_services: Push notifications, sync engine, mobile API gateway
- offline_sync: Offline-first sync with conflict resolution
- push_notifications: Multi-platform push notification service

Version: 3.3.0
"""

__version__ = "3.3.0"

from .mobile_services import (
    ConflictResolution,
    DeviceInfo,
    MobileAPIGateway,
    MobileAuthService,
    NotificationPlatform,
    OfflineQueueProcessor,
    PushNotification,
    PushNotificationService,
    SyncConflict,
    SyncEngine,
    SyncStatus,
    get_mobile_gateway,
    get_push_service,
    get_sync_engine,
)

__all__ = [
    "MobileAPIGateway",
    "PushNotificationService",
    "SyncEngine",
    "MobileAuthService",
    "OfflineQueueProcessor",
    "PushNotification",
    "SyncConflict",
    "ConflictResolution",
    "DeviceInfo",
    "SyncStatus",
    "NotificationPlatform",
    "get_mobile_gateway",
    "get_push_service",
    "get_sync_engine",
]
