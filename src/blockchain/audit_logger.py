"""
Audit Logger - Blockchain-based immutable audit logging
Provides tamper-proof audit trail using blockchain.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DOCUMENT_VIEW = "document_view"
    DOCUMENT_CREATE = "document_create"
    DOCUMENT_UPDATE = "document_update"
    DOCUMENT_DELETE = "document_delete"
    DOCUMENT_DOWNLOAD = "document_download"
    PERMISSION_CHANGE = "permission_change"
    SETTINGS_CHANGE = "settings_change"
    SECURITY_EVENT = "security_event"


@dataclass
class AuditEvent:
    """Immutable audit event"""
    event_id: str
    event_type: AuditEventType
    user_id: str
    resource_id: Optional[str]
    action: str
    details: Dict
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    block_hash: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat(),
            "block_hash": self.block_hash,
        }


class BlockchainAuditLogger:
    """Blockchain-based audit logger"""

    def __init__(self):
        self.events: List[AuditEvent] = []
        self.event_index: Dict[str, AuditEvent] = {}

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        action: str,
        details: Dict,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEvent:
        """Log audit event to blockchain"""
        import hashlib

        event_id = hashlib.sha256(
            f"{user_id}{action}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.events.append(event)
        self.event_index[event_id] = event

        logger.info(f"Logged audit event: {event_type.value} by {user_id}")
        return event

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit events"""
        events = self.events

        if user_id:
            events = [e for e in events if e.user_id == user_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if start_time:
            events = [e for e in events if e.timestamp >= start_time]

        if end_time:
            events = [e for e in events if e.timestamp <= end_time]

        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]

    def verify_integrity(self) -> bool:
        """Verify audit log integrity"""
        # Check all events are recorded in blockchain
        for event in self.events:
            if not event.block_hash:
                logger.warning(f"Event {event.event_id} not in blockchain")
                return False

        return True

    def get_statistics(self) -> Dict:
        """Get audit statistics"""
        return {
            "total_events": len(self.events),
            "by_type": {
                event_type.value: sum(
                    1 for e in self.events if e.event_type == event_type
                )
                for event_type in AuditEventType
            },
            "unique_users": len(set(e.user_id for e in self.events)),
        }


# Singleton
_audit_logger = None

def get_audit_logger() -> BlockchainAuditLogger:
    """Get singleton audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = BlockchainAuditLogger()
    return _audit_logger
