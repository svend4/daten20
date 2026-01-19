"""
IoT Device Manager

Device registration, lifecycle management, firmware updates, and digital twins.
Manages device registry, shadows, grouping, and health monitoring.

Part of v3.6 IoT & Edge Computing implementation.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    """Device connection status."""

    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    PROVISIONING = "provisioning"
    DEACTIVATED = "deactivated"


class DeviceType(Enum):
    """Device types."""

    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    SCANNER = "scanner"
    TRACKER = "tracker"
    CAMERA = "camera"
    CONTROLLER = "controller"


class FirmwareStatus(Enum):
    """Firmware update status."""

    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    UPDATING = "updating"
    UPDATE_FAILED = "update_failed"


@dataclass
class Location:
    """Physical location of device."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    room: Optional[str] = None
    floor: Optional[int] = None
    building: Optional[str] = None
    address: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceShadow:
    """Digital twin - desired vs reported state."""

    desired: Dict[str, Any] = field(default_factory=dict)
    reported: Dict[str, Any] = field(default_factory=dict)
    delta: Dict[str, Any] = field(default_factory=dict)
    version: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def update_desired(self, state: Dict[str, Any]):
        """Update desired state and calculate delta."""
        self.desired.update(state)
        self.version += 1
        self.last_updated = datetime.now()
        self._calculate_delta()

    def update_reported(self, state: Dict[str, Any]):
        """Update reported state and calculate delta."""
        self.reported.update(state)
        self.version += 1
        self.last_updated = datetime.now()
        self._calculate_delta()

    def _calculate_delta(self):
        """Calculate difference between desired and reported."""
        self.delta = {}
        for key, value in self.desired.items():
            if key not in self.reported or self.reported[key] != value:
                self.delta[key] = value


@dataclass
class FirmwareVersion:
    """Firmware version information."""

    version: str
    release_date: datetime
    download_url: str
    checksum: str
    file_size: int
    release_notes: str = ""
    mandatory: bool = False


@dataclass
class Device:
    """IoT device representation."""

    device_id: str
    device_name: str
    device_type: DeviceType
    status: DeviceStatus = DeviceStatus.PROVISIONING
    firmware_version: str = "1.0.0"
    location: Optional[Location] = None
    last_seen: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    shadow: DeviceShadow = field(default_factory=DeviceShadow)
    groups: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def is_online(self, timeout_seconds: int = 300) -> bool:
        """Check if device is online based on last_seen."""
        if not self.last_seen:
            return False
        return (datetime.now() - self.last_seen).total_seconds() < timeout_seconds

    def update_status(self):
        """Update device status based on last_seen."""
        if self.is_online():
            self.status = DeviceStatus.ONLINE
        elif self.status == DeviceStatus.ONLINE:
            self.status = DeviceStatus.OFFLINE


@dataclass
class DeviceGroup:
    """Group of devices."""

    group_id: str
    group_name: str
    description: str = ""
    devices: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class DeviceRegistry:
    """Device registration and lookup."""

    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.groups: Dict[str, DeviceGroup] = {}
        self.device_by_name: Dict[str, str] = {}  # name -> device_id

    def register(self, device: Device) -> bool:
        """Register new device."""
        if device.device_id in self.devices:
            logger.warning(f"Device {device.device_id} already registered")
            return False

        self.devices[device.device_id] = device
        self.device_by_name[device.device_name] = device.device_id

        logger.info(f"Registered device {device.device_id} ({device.device_name})")
        return True

    def get(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
        return self.devices.get(device_id)

    def get_by_name(self, device_name: str) -> Optional[Device]:
        """Get device by name."""
        device_id = self.device_by_name.get(device_name)
        return self.devices.get(device_id) if device_id else None

    def list_devices(
        self,
        status: Optional[DeviceStatus] = None,
        device_type: Optional[DeviceType] = None,
        group: Optional[str] = None,
    ) -> List[Device]:
        """List devices with optional filters."""
        devices = list(self.devices.values())

        if status:
            devices = [d for d in devices if d.status == status]

        if device_type:
            devices = [d for d in devices if d.device_type == device_type]

        if group:
            devices = [d for d in devices if group in d.groups]

        return devices

    def deregister(self, device_id: str) -> bool:
        """Deregister device."""
        device = self.devices.pop(device_id, None)
        if device:
            self.device_by_name.pop(device.device_name, None)
            logger.info(f"Deregistered device {device_id}")
            return True
        return False

    def update_last_seen(self, device_id: str):
        """Update device last seen timestamp."""
        device = self.devices.get(device_id)
        if device:
            device.last_seen = datetime.now()
            device.update_status()

    def create_group(self, group_id: str, group_name: str, description: str = "") -> DeviceGroup:
        """Create device group."""
        if group_id in self.groups:
            raise ValueError(f"Group {group_id} already exists")

        group = DeviceGroup(group_id=group_id, group_name=group_name, description=description)
        self.groups[group_id] = group

        logger.info(f"Created device group {group_id}")
        return group

    def add_to_group(self, device_id: str, group_id: str) -> bool:
        """Add device to group."""
        device = self.devices.get(device_id)
        group = self.groups.get(group_id)

        if not device or not group:
            return False

        device.groups.add(group_id)
        group.devices.add(device_id)
        return True

    def remove_from_group(self, device_id: str, group_id: str) -> bool:
        """Remove device from group."""
        device = self.devices.get(device_id)
        group = self.groups.get(group_id)

        if not device or not group:
            return False

        device.groups.discard(group_id)
        group.devices.discard(device_id)
        return True


class DeviceLifecycle:
    """Device lifecycle management."""

    def __init__(self, registry: DeviceRegistry):
        self.registry = registry

    async def provision(self, device_id: str, device_name: str, device_type: DeviceType, **kwargs) -> Device:
        """Provision new device."""
        # Create device
        device = Device(device_id=device_id, device_name=device_name, device_type=device_type, **kwargs)

        # Register
        if not self.registry.register(device):
            raise ValueError(f"Failed to register device {device_id}")

        # Initialize shadow
        device.shadow = DeviceShadow()

        logger.info(f"Provisioned device {device_id}")
        return device

    async def activate(self, device_id: str) -> bool:
        """Activate provisioned device."""
        device = self.registry.get(device_id)
        if not device:
            return False

        device.status = DeviceStatus.ONLINE
        device.last_seen = datetime.now()

        logger.info(f"Activated device {device_id}")
        return True

    async def deactivate(self, device_id: str) -> bool:
        """Deactivate device."""
        device = self.registry.get(device_id)
        if not device:
            return False

        device.status = DeviceStatus.DEACTIVATED

        logger.info(f"Deactivated device {device_id}")
        return True

    async def deprovision(self, device_id: str) -> bool:
        """Deprovision and remove device."""
        device = self.registry.get(device_id)
        if not device:
            return False

        # Remove from all groups
        for group_id in list(device.groups):
            self.registry.remove_from_group(device_id, group_id)

        # Deregister
        self.registry.deregister(device_id)

        logger.info(f"Deprovisioned device {device_id}")
        return True


class FirmwareUpdater:
    """OTA firmware update manager."""

    def __init__(self):
        self.firmware_versions: Dict[str, List[FirmwareVersion]] = defaultdict(list)
        self.update_queue: Dict[str, FirmwareVersion] = {}
        self.update_status: Dict[str, FirmwareStatus] = {}

    def register_firmware(self, device_type: str, version: FirmwareVersion):
        """Register new firmware version."""
        self.firmware_versions[device_type].append(version)
        self.firmware_versions[device_type].sort(key=lambda v: v.release_date, reverse=True)

        logger.info(f"Registered firmware {version.version} for {device_type}")

    def get_latest_version(self, device_type: str) -> Optional[FirmwareVersion]:
        """Get latest firmware version for device type."""
        versions = self.firmware_versions.get(device_type, [])
        return versions[0] if versions else None

    def check_update_available(self, device: Device) -> bool:
        """Check if firmware update is available."""
        latest = self.get_latest_version(device.device_type.value)
        if not latest:
            return False

        return latest.version != device.firmware_version

    async def schedule_update(self, device_id: str, device: Device) -> bool:
        """Schedule firmware update for device."""
        latest = self.get_latest_version(device.device_type.value)
        if not latest:
            logger.warning(f"No firmware available for {device.device_type.value}")
            return False

        if latest.version == device.firmware_version:
            logger.info(f"Device {device_id} already has latest firmware")
            return False

        self.update_queue[device_id] = latest
        self.update_status[device_id] = FirmwareStatus.UPDATE_AVAILABLE

        logger.info(f"Scheduled update for {device_id} to version {latest.version}")
        return True

    async def perform_update(self, device_id: str, device: Device) -> bool:
        """Perform firmware update."""
        if device_id not in self.update_queue:
            return False

        firmware = self.update_queue[device_id]
        self.update_status[device_id] = FirmwareStatus.UPDATING

        try:
            # Simulate OTA update
            logger.info(f"Updating {device_id} to firmware {firmware.version}...")
            await asyncio.sleep(1)  # Simulate download/install

            # Update device firmware version
            device.firmware_version = firmware.version
            self.update_status[device_id] = FirmwareStatus.UP_TO_DATE

            # Remove from queue
            del self.update_queue[device_id]

            logger.info(f"Successfully updated {device_id} to {firmware.version}")
            return True

        except Exception as e:
            logger.error(f"Firmware update failed for {device_id}: {e}")
            self.update_status[device_id] = FirmwareStatus.UPDATE_FAILED
            return False


class DeviceGroupManager:
    """Device grouping and batch operations."""

    def __init__(self, registry: DeviceRegistry):
        self.registry = registry

    async def create_group(
        self, group_name: str, device_ids: Optional[List[str]] = None, description: str = ""
    ) -> DeviceGroup:
        """Create new device group."""
        group_id = str(uuid4())
        group = self.registry.create_group(group_id, group_name, description)

        # Add devices
        if device_ids:
            for device_id in device_ids:
                self.registry.add_to_group(device_id, group_id)

        return group

    async def batch_update_shadow(self, group_id: str, desired_state: Dict[str, Any]) -> int:
        """Update shadow for all devices in group."""
        group = self.registry.groups.get(group_id)
        if not group:
            return 0

        updated_count = 0
        for device_id in group.devices:
            device = self.registry.get(device_id)
            if device:
                device.shadow.update_desired(desired_state)
                updated_count += 1

        logger.info(f"Updated shadow for {updated_count} devices in group {group_id}")
        return updated_count

    async def batch_firmware_update(self, group_id: str, firmware_updater: FirmwareUpdater) -> Dict[str, bool]:
        """Schedule firmware updates for all devices in group."""
        group = self.registry.groups.get(group_id)
        if not group:
            return {}

        results = {}
        for device_id in group.devices:
            device = self.registry.get(device_id)
            if device:
                success = await firmware_updater.schedule_update(device_id, device)
                results[device_id] = success

        logger.info(f"Scheduled firmware updates for group {group_id}")
        return results


class DeviceHealthMonitor:
    """Monitor device health and detect issues."""

    def __init__(self, registry: DeviceRegistry):
        self.registry = registry
        self.health_checks: Dict[str, datetime] = {}
        self.alerts: List[Dict[str, Any]] = []

    async def check_device_health(self, device_id: str) -> Dict[str, Any]:
        """Check health of specific device."""
        device = self.registry.get(device_id)
        if not device:
            return {"status": "unknown", "error": "Device not found"}

        health = {
            "device_id": device_id,
            "status": device.status.value,
            "is_online": device.is_online(),
            "last_seen": device.last_seen,
            "issues": [],
        }

        # Check if device is offline
        if not device.is_online():
            health["issues"].append("Device offline")

        # Check shadow sync
        if device.shadow.delta:
            health["issues"].append("Shadow out of sync")

        # Check last seen
        if device.last_seen:
            hours_since_seen = (datetime.now() - device.last_seen).total_seconds() / 3600
            if hours_since_seen > 24:
                health["issues"].append(f"Not seen for {hours_since_seen:.1f} hours")

        self.health_checks[device_id] = datetime.now()
        return health

    async def check_all_devices(self) -> List[Dict[str, Any]]:
        """Check health of all devices."""
        results = []
        for device_id in self.registry.devices:
            health = await self.check_device_health(device_id)
            if health.get("issues"):
                results.append(health)

        return results

    def create_alert(self, device_id: str, alert_type: str, message: str, severity: str = "warning"):
        """Create device alert."""
        alert = {
            "device_id": device_id,
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now(),
        }

        self.alerts.append(alert)
        logger.warning(f"Device alert: {alert}")

    def get_alerts(self, device_id: Optional[str] = None, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get device alerts."""
        alerts = self.alerts

        if device_id:
            alerts = [a for a in alerts if a["device_id"] == device_id]

        if since:
            alerts = [a for a in alerts if a["timestamp"] >= since]

        return alerts


class DeviceManager:
    """Main device manager orchestrating all device operations."""

    def __init__(self):
        self.registry = DeviceRegistry()
        self.lifecycle = DeviceLifecycle(self.registry)
        self.firmware_updater = FirmwareUpdater()
        self.group_manager = DeviceGroupManager(self.registry)
        self.health_monitor = DeviceHealthMonitor(self.registry)

    async def register_device(self, device_id: str, device_name: str, device_type: str, **kwargs) -> Device:
        """Register new device."""
        return await self.lifecycle.provision(
            device_id=device_id, device_name=device_name, device_type=DeviceType(device_type), **kwargs
        )

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
        return self.registry.get(device_id)

    def list_devices(self, **filters) -> List[Device]:
        """List devices with filters."""
        return self.registry.list_devices(**filters)

    async def update_shadow(
        self, device_id: str, desired: Optional[Dict[str, Any]] = None, reported: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update device shadow."""
        device = self.registry.get(device_id)
        if not device:
            return False

        if desired:
            device.shadow.update_desired(desired)

        if reported:
            device.shadow.update_reported(reported)

        return True

    def get_shadow(self, device_id: str) -> Optional[DeviceShadow]:
        """Get device shadow."""
        device = self.registry.get(device_id)
        return device.shadow if device else None

    async def schedule_firmware_update(self, device_id: str) -> bool:
        """Schedule firmware update for device."""
        device = self.registry.get(device_id)
        if not device:
            return False

        return await self.firmware_updater.schedule_update(device_id, device)

    async def create_group(self, group_name: str, device_ids: Optional[List[str]] = None) -> DeviceGroup:
        """Create device group."""
        return await self.group_manager.create_group(group_name, device_ids)

    async def check_device_health(self, device_id: str) -> Dict[str, Any]:
        """Check device health."""
        return await self.health_monitor.check_device_health(device_id)

    def heartbeat(self, device_id: str):
        """Record device heartbeat."""
        self.registry.update_last_seen(device_id)


# Singleton instance
_device_manager: Optional[DeviceManager] = None


def get_device_manager() -> DeviceManager:
    """Get or create device manager."""
    global _device_manager

    if _device_manager is None:
        _device_manager = DeviceManager()

    return _device_manager
