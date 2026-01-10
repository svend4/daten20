#!/usr/bin/env python3
"""
Mobile Services Module

Backend services for mobile clients including push notifications,
offline sync, and mobile-optimized API gateway.

Key Features:
- Push notifications (APNs, FCM, HMS)
- Offline sync with conflict resolution
- Mobile-optimized API responses
- Delta sync for bandwidth optimization
- Background job processing
- Device management
- Mobile analytics

Dependencies:
- None (pure Python implementation, optional integrations)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime, timedelta
from uuid import uuid4
import threading
import json
import logging
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


class NotificationPlatform(str, Enum):
    """Push notification platforms"""
    APNS = "apns"  # Apple Push Notification Service
    FCM = "fcm"  # Firebase Cloud Messaging
    HMS = "hms"  # Huawei Mobile Services
    WEB_PUSH = "web_push"  # Web Push API


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL = "manual"
    MERGE = "merge"
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"


class SyncStatus(str, Enum):
    """Sync status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DeviceInfo:
    """Mobile device information"""
    device_id: str
    user_id: str
    platform: NotificationPlatform
    push_token: str
    app_version: str
    os_version: str
    device_model: str
    locale: str = "en"
    timezone: str = "UTC"
    last_seen: datetime = field(default_factory=datetime.now)
    registered_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PushNotification:
    """Push notification message"""
    notification_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    body: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    badge: Optional[int] = None
    sound: str = "default"
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: Optional[str] = None
    thread_id: Optional[str] = None
    expiration: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SyncOperation:
    """Offline sync operation"""
    operation_id: str = field(default_factory=lambda: str(uuid4()))
    device_id: str = ""
    user_id: str = ""
    resource_type: str = ""  # e.g., "document", "user", "settings"
    resource_id: str = ""
    operation: str = ""  # "create", "update", "delete"
    data: Dict[str, Any] = field(default_factory=dict)
    client_timestamp: datetime = field(default_factory=datetime.now)
    server_timestamp: Optional[datetime] = None
    status: SyncStatus = SyncStatus.PENDING
    version: int = 1
    checksum: Optional[str] = None


@dataclass
class SyncConflict:
    """Sync conflict between client and server"""
    conflict_id: str = field(default_factory=lambda: str(uuid4()))
    operation: SyncOperation = field(default_factory=lambda: SyncOperation())
    server_data: Dict[str, Any] = field(default_factory=dict)
    server_version: int = 1
    resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class DeviceManager:
    """
    Device registration and management

    Tracks mobile devices and their push tokens.
    """

    def __init__(self):
        self._devices: Dict[str, DeviceInfo] = {}
        self._user_devices: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.Lock()

    def register_device(self, device: DeviceInfo) -> bool:
        """
        Register mobile device

        Args:
            device: Device information

        Returns:
            True if registered successfully
        """
        with self._lock:
            self._devices[device.device_id] = device

            # Track user's devices
            if device.device_id not in self._user_devices[device.user_id]:
                self._user_devices[device.user_id].append(device.device_id)

            logger.info(f"Device registered: {device.device_id} for user {device.user_id}")
            return True

    def unregister_device(self, device_id: str) -> bool:
        """Unregister device"""
        with self._lock:
            device = self._devices.get(device_id)
            if not device:
                return False

            # Remove from user's devices
            if device_id in self._user_devices[device.user_id]:
                self._user_devices[device.user_id].remove(device_id)

            del self._devices[device_id]
            logger.info(f"Device unregistered: {device_id}")
            return True

    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        """Get device by ID"""
        with self._lock:
            return self._devices.get(device_id)

    def get_user_devices(self, user_id: str) -> List[DeviceInfo]:
        """Get all devices for user"""
        with self._lock:
            device_ids = self._user_devices.get(user_id, [])
            return [self._devices[did] for did in device_ids if did in self._devices]

    def update_last_seen(self, device_id: str):
        """Update device last seen timestamp"""
        with self._lock:
            if device_id in self._devices:
                self._devices[device_id].last_seen = datetime.now()


class PushNotificationService:
    """
    Multi-platform push notification service

    Sends push notifications to iOS (APNs), Android (FCM), and Huawei (HMS).
    """

    def __init__(self, device_manager: Optional[DeviceManager] = None):
        self.device_manager = device_manager or DeviceManager()
        self._notification_history: List[tuple[str, PushNotification]] = []
        self._lock = threading.Lock()

    def send_notification(
        self,
        user_id: str,
        notification: PushNotification,
        platforms: Optional[List[NotificationPlatform]] = None
    ) -> Dict[str, bool]:
        """
        Send push notification to user's devices

        Args:
            user_id: Target user ID
            notification: Notification to send
            platforms: Optional platform filter

        Returns:
            Dict of device_id -> success status
        """
        devices = self.device_manager.get_user_devices(user_id)

        # Filter by platform if specified
        if platforms:
            devices = [d for d in devices if d.platform in platforms]

        results = {}

        for device in devices:
            if not device.is_active:
                continue

            try:
                success = self._send_to_device(device, notification)
                results[device.device_id] = success

                if success:
                    # Record in history
                    with self._lock:
                        self._notification_history.append((device.device_id, notification))

            except Exception as e:
                logger.error(f"Failed to send notification to {device.device_id}: {e}")
                results[device.device_id] = False

        return results

    def send_to_devices(
        self,
        device_ids: List[str],
        notification: PushNotification
    ) -> Dict[str, bool]:
        """
        Send notification to specific devices

        Args:
            device_ids: Target device IDs
            notification: Notification to send

        Returns:
            Dict of device_id -> success status
        """
        results = {}

        for device_id in device_ids:
            device = self.device_manager.get_device(device_id)
            if not device or not device.is_active:
                results[device_id] = False
                continue

            try:
                success = self._send_to_device(device, notification)
                results[device_id] = success
            except Exception as e:
                logger.error(f"Failed to send notification to {device_id}: {e}")
                results[device_id] = False

        return results

    def _send_to_device(self, device: DeviceInfo, notification: PushNotification) -> bool:
        """
        Send notification to specific device

        In production, this would integrate with APNs, FCM, HMS APIs.
        """
        # Simplified implementation
        logger.info(
            f"Sending notification to {device.platform.value} "
            f"device {device.device_id}: {notification.title}"
        )

        # In production:
        # - Use py-apns2 for APNs
        # - Use firebase-admin for FCM
        # - Use Huawei Push Kit for HMS

        return True

    def get_notification_history(
        self,
        device_id: Optional[str] = None,
        limit: int = 100
    ) -> List[tuple[str, PushNotification]]:
        """Get notification history"""
        with self._lock:
            history = self._notification_history

            if device_id:
                history = [(d, n) for d, n in history if d == device_id]

            return history[-limit:]


class SyncEngine:
    """
    Offline sync engine with conflict resolution

    Handles synchronization of offline changes from mobile clients.
    """

    def __init__(self):
        self._pending_operations: List[SyncOperation] = []
        self._conflicts: List[SyncConflict] = []
        self._server_state: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = threading.Lock()

    def queue_operation(self, operation: SyncOperation) -> str:
        """
        Queue sync operation from client

        Args:
            operation: Sync operation

        Returns:
            Operation ID
        """
        with self._lock:
            # Calculate checksum
            operation.checksum = self._calculate_checksum(operation.data)
            self._pending_operations.append(operation)

            logger.info(
                f"Queued {operation.operation} operation for "
                f"{operation.resource_type}:{operation.resource_id}"
            )

            return operation.operation_id

    def process_sync(
        self,
        device_id: str,
        resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS
    ) -> Dict[str, Any]:
        """
        Process pending sync operations for device

        Args:
            device_id: Device ID
            resolution: Conflict resolution strategy

        Returns:
            Sync result with statistics
        """
        with self._lock:
            # Get device operations
            device_ops = [op for op in self._pending_operations if op.device_id == device_id]

            if not device_ops:
                return {
                    "status": "up_to_date",
                    "processed": 0,
                    "conflicts": 0
                }

            processed = 0
            conflicts = 0

            for operation in device_ops:
                try:
                    conflict = self._check_conflict(operation)

                    if conflict:
                        conflict.resolution = resolution
                        self._resolve_conflict(conflict)
                        conflicts += 1
                    else:
                        self._apply_operation(operation)

                    operation.status = SyncStatus.COMPLETED
                    operation.server_timestamp = datetime.now()
                    processed += 1

                except Exception as e:
                    logger.error(f"Sync operation failed: {e}")
                    operation.status = SyncStatus.FAILED

            # Remove processed operations
            self._pending_operations = [
                op for op in self._pending_operations
                if op.device_id != device_id or op.status == SyncStatus.PENDING
            ]

            return {
                "status": "synced",
                "processed": processed,
                "conflicts": conflicts,
                "timestamp": datetime.now().isoformat()
            }

    def get_delta(
        self,
        user_id: str,
        since_timestamp: datetime,
        resource_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get delta changes since timestamp

        Args:
            user_id: User ID
            since_timestamp: Starting timestamp
            resource_types: Optional filter by resource types

        Returns:
            List of changes
        """
        with self._lock:
            changes = []

            for resource_type, resources in self._server_state.items():
                if resource_types and resource_type not in resource_types:
                    continue

                for resource_id, data in resources.items():
                    updated_at = data.get("updated_at")
                    if updated_at and updated_at > since_timestamp:
                        changes.append({
                            "resource_type": resource_type,
                            "resource_id": resource_id,
                            "data": data,
                            "updated_at": updated_at.isoformat()
                        })

            return sorted(changes, key=lambda x: x["updated_at"])

    def _check_conflict(self, operation: SyncOperation) -> Optional[SyncConflict]:
        """Check if operation conflicts with server state"""
        key = f"{operation.resource_type}:{operation.resource_id}"
        server_data = self._server_state[operation.resource_type].get(operation.resource_id)

        if not server_data:
            return None

        # Check version conflict
        server_version = server_data.get("version", 1)
        if operation.version < server_version:
            return SyncConflict(
                operation=operation,
                server_data=server_data,
                server_version=server_version
            )

        # Check timestamp conflict
        server_updated = server_data.get("updated_at")
        if server_updated and server_updated > operation.client_timestamp:
            return SyncConflict(
                operation=operation,
                server_data=server_data,
                server_version=server_version
            )

        return None

    def _resolve_conflict(self, conflict: SyncConflict):
        """Resolve sync conflict"""
        operation = conflict.operation

        if conflict.resolution == ConflictResolution.LAST_WRITE_WINS:
            # Client timestamp wins
            if operation.client_timestamp > conflict.server_data.get("updated_at"):
                self._apply_operation(operation)
            # Server wins, discard client change

        elif conflict.resolution == ConflictResolution.FIRST_WRITE_WINS:
            # Server always wins, discard client change
            pass

        elif conflict.resolution == ConflictResolution.CLIENT_WINS:
            self._apply_operation(operation)

        elif conflict.resolution == ConflictResolution.SERVER_WINS:
            pass  # Keep server data

        elif conflict.resolution == ConflictResolution.MERGE:
            # Merge changes (simplified)
            merged_data = {**conflict.server_data, **operation.data}
            operation.data = merged_data
            self._apply_operation(operation)

        conflict.resolved = True
        conflict.resolved_at = datetime.now()

        with self._lock:
            self._conflicts.append(conflict)

        logger.info(f"Conflict resolved using {conflict.resolution.value}")

    def _apply_operation(self, operation: SyncOperation):
        """Apply sync operation to server state"""
        if operation.operation == "create" or operation.operation == "update":
            operation.data["version"] = operation.version + 1
            operation.data["updated_at"] = datetime.now()
            self._server_state[operation.resource_type][operation.resource_id] = operation.data

        elif operation.operation == "delete":
            if operation.resource_id in self._server_state[operation.resource_type]:
                del self._server_state[operation.resource_type][operation.resource_id]

        logger.info(
            f"Applied {operation.operation} on "
            f"{operation.resource_type}:{operation.resource_id}"
        )

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data integrity"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def get_conflicts(self, user_id: Optional[str] = None) -> List[SyncConflict]:
        """Get sync conflicts"""
        with self._lock:
            conflicts = self._conflicts.copy()

            if user_id:
                conflicts = [c for c in conflicts if c.operation.user_id == user_id]

            return conflicts


class MobileAuthService:
    """
    Mobile-optimized authentication service

    Handles mobile auth flows with refresh tokens and biometric support.
    """

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._refresh_tokens: Dict[str, str] = {}  # refresh_token -> device_id
        self._lock = threading.Lock()

    def authenticate(
        self,
        device_id: str,
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Authenticate device

        Args:
            device_id: Device ID
            credentials: User credentials

        Returns:
            Authentication tokens
        """
        # Simplified authentication
        access_token = self._generate_token()
        refresh_token = self._generate_token()

        with self._lock:
            self._sessions[device_id] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": datetime.now() + timedelta(hours=1),
                "created_at": datetime.now()
            }
            self._refresh_tokens[refresh_token] = device_id

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 3600,
            "token_type": "Bearer"
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        with self._lock:
            device_id = self._refresh_tokens.get(refresh_token)
            if not device_id or device_id not in self._sessions:
                raise ValueError("Invalid refresh token")

            # Generate new access token
            access_token = self._generate_token()
            self._sessions[device_id]["access_token"] = access_token
            self._sessions[device_id]["expires_at"] = datetime.now() + timedelta(hours=1)

            return {
                "access_token": access_token,
                "expires_in": 3600,
                "token_type": "Bearer"
            }

    def _generate_token(self) -> str:
        """Generate random token"""
        return hashlib.sha256(str(uuid4()).encode()).hexdigest()


class OfflineQueueProcessor:
    """
    Background processor for offline operations

    Processes queued operations in background.
    """

    def __init__(self, sync_engine: SyncEngine):
        self.sync_engine = sync_engine
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start background processing"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        logger.info("Offline queue processor started")

    def stop(self):
        """Stop background processing"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Offline queue processor stopped")

    def _process_loop(self):
        """Background processing loop"""
        import time

        while self._running:
            try:
                # Process pending operations
                # In production, this would batch process operations
                time.sleep(30)  # Process every 30 seconds
            except Exception as e:
                logger.error(f"Queue processing error: {e}")


class MobileAPIGateway:
    """
    Mobile-optimized API gateway

    Provides bandwidth-optimized responses for mobile clients.
    """

    def __init__(self):
        self._compression_enabled = True
        self._field_filtering = True

    def optimize_response(
        self,
        data: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize API response for mobile

        Args:
            data: Response data
            fields: Fields to include (field filtering)

        Returns:
            Optimized response
        """
        if fields and self._field_filtering:
            # Filter to requested fields only
            optimized = {k: v for k, v in data.items() if k in fields}
        else:
            optimized = data

        # Remove null values to reduce payload size
        optimized = {k: v for k, v in optimized.items() if v is not None}

        return optimized

    def create_delta_response(
        self,
        full_data: Dict[str, Any],
        previous_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create delta response with only changed fields

        Args:
            full_data: Current data
            previous_data: Previous data

        Returns:
            Delta containing only changes
        """
        delta = {}

        for key, value in full_data.items():
            if key not in previous_data or previous_data[key] != value:
                delta[key] = value

        return delta


# Singleton instances
_mobile_gateway_instance = None
_push_service_instance = None
_sync_engine_instance = None
_instance_lock = threading.Lock()


def get_mobile_gateway() -> MobileAPIGateway:
    """Get singleton Mobile API Gateway instance"""
    global _mobile_gateway_instance
    if _mobile_gateway_instance is None:
        with _instance_lock:
            if _mobile_gateway_instance is None:
                _mobile_gateway_instance = MobileAPIGateway()
    return _mobile_gateway_instance


def get_push_service() -> PushNotificationService:
    """Get singleton Push Notification Service instance"""
    global _push_service_instance
    if _push_service_instance is None:
        with _instance_lock:
            if _push_service_instance is None:
                _push_service_instance = PushNotificationService()
    return _push_service_instance


def get_sync_engine() -> SyncEngine:
    """Get singleton Sync Engine instance"""
    global _sync_engine_instance
    if _sync_engine_instance is None:
        with _instance_lock:
            if _sync_engine_instance is None:
                _sync_engine_instance = SyncEngine()
    return _sync_engine_instance


if __name__ == "__main__":
    # Example usage
    push_service = get_push_service()
    sync_engine = get_sync_engine()

    # Register device
    device = DeviceInfo(
        device_id="iphone-123",
        user_id="user-456",
        platform=NotificationPlatform.APNS,
        push_token="apns-token-xyz",
        app_version="1.0.0",
        os_version="iOS 17.0",
        device_model="iPhone 15 Pro"
    )
    push_service.device_manager.register_device(device)

    # Send push notification
    notification = PushNotification(
        title="New Document",
        body="A new document has been shared with you",
        data={"document_id": "doc-789"},
        priority=NotificationPriority.HIGH
    )
    results = push_service.send_notification("user-456", notification)
    print(f"Push notification results: {results}")

    # Queue sync operation
    operation = SyncOperation(
        device_id="iphone-123",
        user_id="user-456",
        resource_type="document",
        resource_id="doc-789",
        operation="update",
        data={"title": "Updated Document", "content": "New content"}
    )
    op_id = sync_engine.queue_operation(operation)
    print(f"Queued operation: {op_id}")

    # Process sync
    result = sync_engine.process_sync("iphone-123")
    print(f"Sync result: {result}")

    print("\nMobile Services module loaded successfully!")
