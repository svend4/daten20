"""
Data Retention Engine

Automated retention policy enforcement, disposition scheduling,
retention holds, and compliance reporting.

Part of v3.8 Governance & Compliance implementation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class TriggerEvent(Enum):
    """Retention trigger events."""
    CREATION_DATE = "creation_date"
    MODIFICATION_DATE = "modification_date"
    CLOSURE_DATE = "closure_date"
    LAST_ACCESS_DATE = "last_access_date"
    CUSTOM_DATE = "custom_date"


class DispositionAction(Enum):
    """Actions to take when retention period expires."""
    PERMANENT_DELETE = "permanent_delete"
    ARCHIVE = "archive"
    TRANSFER = "transfer"
    REVIEW = "review"


class HoldType(Enum):
    """Types of retention holds."""
    LEGAL = "legal"
    AUDIT = "audit"
    BUSINESS = "business"
    REGULATORY = "regulatory"


@dataclass
class RetentionPolicy:
    """Retention policy definition."""
    policy_id: str
    name: str
    description: str
    retention_period: timedelta
    trigger_event: TriggerEvent
    disposition_action: DispositionAction
    applies_to: Dict[str, Any]  # Criteria for which items this applies to
    auto_apply: bool = True
    requires_approval: bool = False
    notify_before_days: int = 30
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    active: bool = True


@dataclass
class AppliedRetention:
    """Retention policy applied to an item."""
    retention_id: str
    item_id: str
    policy_id: str
    trigger_date: datetime
    disposition_date: datetime
    holds: Set[str] = field(default_factory=set)  # hold_ids blocking disposition
    exceptions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    applied_date: datetime = field(default_factory=datetime.now)


@dataclass
class RetentionHold:
    """Retention hold preventing disposition."""
    hold_id: str
    hold_type: HoldType
    reason: str
    placed_by: str
    items: Set[str] = field(default_factory=set)  # item_ids on hold
    placed_date: datetime = field(default_factory=datetime.now)
    release_date: Optional[datetime] = None
    active: bool = True
    case_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DispositionQueueItem:
    """Item scheduled for disposition."""
    queue_item_id: str
    retention_id: str
    item_id: str
    policy_id: str
    scheduled_date: datetime
    action: DispositionAction
    requires_approval: bool
    approved: bool = False
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    executed: bool = False
    executed_by: Optional[str] = None
    executed_date: Optional[datetime] = None
    on_hold: bool = False
    hold_ids: Set[str] = field(default_factory=set)


@dataclass
class RetentionException:
    """Exception to retention policy."""
    exception_id: str
    item_id: str
    policy_id: str
    reason: str
    requested_by: str
    approved_by: Optional[str] = None
    new_disposition_date: Optional[datetime] = None
    permanent_exception: bool = False
    created_date: datetime = field(default_factory=datetime.now)


class PolicyEngine:
    """Retention policy engine."""

    def __init__(self):
        self.policies: Dict[str, RetentionPolicy] = {}

    async def create_policy(
        self,
        name: str,
        description: str,
        retention_period: timedelta,
        trigger_event: str,
        applies_to: Dict[str, Any],
        disposition_action: str = "permanent_delete",
        **kwargs
    ) -> RetentionPolicy:
        """Create retention policy."""
        await asyncio.sleep(0.05)

        policy = RetentionPolicy(
            policy_id=str(uuid4()),
            name=name,
            description=description,
            retention_period=retention_period,
            trigger_event=TriggerEvent(trigger_event),
            disposition_action=DispositionAction(disposition_action),
            applies_to=applies_to,
            created_by=kwargs.get("created_by", "system"),
            **{k: v for k, v in kwargs.items() if k != "created_by"}
        )

        self.policies[policy.policy_id] = policy

        logger.info(f"Created retention policy: {name}")
        return policy

    async def find_applicable_policy(
        self,
        item: Dict[str, Any]
    ) -> Optional[RetentionPolicy]:
        """Find policy that applies to item."""
        await asyncio.sleep(0.02)

        for policy in self.policies.values():
            if not policy.active or not policy.auto_apply:
                continue

            # Check if policy criteria match item
            matches = True
            for key, value in policy.applies_to.items():
                if key not in item or item[key] != value:
                    matches = False
                    break

            if matches:
                return policy

        return None

    async def get_active_policies(self) -> List[RetentionPolicy]:
        """Get all active policies."""
        return [p for p in self.policies.values() if p.active]


class DispositionQueue:
    """Manage disposition queue."""

    def __init__(self):
        self.queue: Dict[str, DispositionQueueItem] = {}

    async def schedule(
        self,
        retention: AppliedRetention,
        policy: RetentionPolicy
    ) -> DispositionQueueItem:
        """Schedule item for disposition."""
        await asyncio.sleep(0.02)

        item = DispositionQueueItem(
            queue_item_id=str(uuid4()),
            retention_id=retention.retention_id,
            item_id=retention.item_id,
            policy_id=policy.policy_id,
            scheduled_date=retention.disposition_date,
            action=policy.disposition_action,
            requires_approval=policy.requires_approval,
            on_hold=len(retention.holds) > 0,
            hold_ids=retention.holds.copy()
        )

        self.queue[item.queue_item_id] = item

        logger.info(f"Scheduled {item.item_id} for {item.action.value} on {item.scheduled_date}")
        return item

    async def get_due_items(
        self,
        days_ahead: int = 30,
        include_held: bool = False
    ) -> List[DispositionQueueItem]:
        """Get items due for disposition."""
        await asyncio.sleep(0.05)

        cutoff = datetime.now() + timedelta(days=days_ahead)

        items = [
            item for item in self.queue.values()
            if item.scheduled_date <= cutoff
            and not item.executed
            and (include_held or not item.on_hold)
        ]

        return sorted(items, key=lambda x: x.scheduled_date)

    async def approve(
        self,
        queue_item_id: str,
        approver: str,
        notes: Optional[str] = None
    ) -> bool:
        """Approve disposition."""
        await asyncio.sleep(0.05)

        if queue_item_id not in self.queue:
            return False

        item = self.queue[queue_item_id]

        if item.on_hold:
            logger.warning(f"Cannot approve {queue_item_id}: item on hold")
            return False

        item.approved = True
        item.approved_by = approver
        item.approved_date = datetime.now()

        logger.info(f"Approved disposition of {item.item_id}")
        return True

    async def execute(
        self,
        queue_item_id: str,
        executor: str
    ) -> bool:
        """Execute disposition."""
        await asyncio.sleep(0.1)

        if queue_item_id not in self.queue:
            return False

        item = self.queue[queue_item_id]

        if item.on_hold:
            logger.warning(f"Cannot execute {queue_item_id}: item on hold")
            return False

        if item.requires_approval and not item.approved:
            logger.warning(f"Cannot execute {queue_item_id}: not approved")
            return False

        item.executed = True
        item.executed_by = executor
        item.executed_date = datetime.now()

        logger.info(f"Executed {item.action.value} on {item.item_id}")
        return True

    async def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        total = len(self.queue)
        executed = sum(1 for i in self.queue.values() if i.executed)
        on_hold = sum(1 for i in self.queue.values() if i.on_hold and not i.executed)
        pending_approval = sum(
            1 for i in self.queue.values()
            if i.requires_approval and not i.approved and not i.on_hold and not i.executed
        )
        ready_to_execute = sum(
            1 for i in self.queue.values()
            if (not i.requires_approval or i.approved)
            and not i.on_hold and not i.executed
        )

        return {
            "total_items": total,
            "executed": executed,
            "on_hold": on_hold,
            "pending_approval": pending_approval,
            "ready_to_execute": ready_to_execute,
            "remaining": total - executed
        }


class HoldManager:
    """Manage retention holds."""

    def __init__(self):
        self.holds: Dict[str, RetentionHold] = {}

    async def place_hold(
        self,
        hold_type: str,
        reason: str,
        placed_by: str,
        items: Optional[List[str]] = None,
        **kwargs
    ) -> RetentionHold:
        """Place retention hold."""
        await asyncio.sleep(0.05)

        hold = RetentionHold(
            hold_id=str(uuid4()),
            hold_type=HoldType(hold_type),
            reason=reason,
            placed_by=placed_by,
            items=set(items or []),
            **kwargs
        )

        self.holds[hold.hold_id] = hold

        logger.info(f"Placed {hold_type} hold on {len(hold.items)} items: {reason}")
        return hold

    async def add_items_to_hold(
        self,
        hold_id: str,
        items: List[str]
    ) -> bool:
        """Add items to existing hold."""
        await asyncio.sleep(0.05)

        if hold_id not in self.holds:
            return False

        hold = self.holds[hold_id]
        hold.items.update(items)

        logger.info(f"Added {len(items)} items to hold {hold_id}")
        return True

    async def release_hold(
        self,
        hold_id: str
    ) -> bool:
        """Release retention hold."""
        await asyncio.sleep(0.05)

        if hold_id not in self.holds:
            return False

        hold = self.holds[hold_id]
        hold.active = False
        hold.release_date = datetime.now()

        logger.info(f"Released hold {hold_id}")
        return True

    async def get_active_holds_for_item(
        self,
        item_id: str
    ) -> List[RetentionHold]:
        """Get active holds for item."""
        return [
            hold for hold in self.holds.values()
            if hold.active and item_id in hold.items
        ]


class RetentionEngine:
    """Main data retention engine."""

    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.applied_retentions: Dict[str, AppliedRetention] = {}
        self.disposition_queue = DispositionQueue()
        self.hold_manager = HoldManager()
        self.exceptions: Dict[str, RetentionException] = {}

    async def create_policy(
        self,
        name: str,
        description: str,
        retention_period: timedelta,
        trigger_event: str,
        applies_to: Dict[str, Any],
        **kwargs
    ) -> RetentionPolicy:
        """Create retention policy."""
        return await self.policy_engine.create_policy(
            name, description, retention_period, trigger_event, applies_to, **kwargs
        )

    async def apply_retention(
        self,
        item_id: str,
        item_data: Dict[str, Any],
        policy_id: Optional[str] = None,
        trigger_date: Optional[datetime] = None
    ) -> AppliedRetention:
        """Apply retention policy to item."""
        await asyncio.sleep(0.05)

        # Find policy
        if policy_id:
            policy = self.policy_engine.policies.get(policy_id)
            if not policy:
                raise ValueError(f"Policy {policy_id} not found")
        else:
            policy = await self.policy_engine.find_applicable_policy(item_data)
            if not policy:
                raise ValueError("No applicable policy found")

        # Determine trigger date
        if not trigger_date:
            if policy.trigger_event == TriggerEvent.CREATION_DATE:
                trigger_date = item_data.get("created_date", datetime.now())
            elif policy.trigger_event == TriggerEvent.MODIFICATION_DATE:
                trigger_date = item_data.get("modified_date", datetime.now())
            else:
                trigger_date = datetime.now()

        # Calculate disposition date
        disposition_date = trigger_date + policy.retention_period

        # Create applied retention
        retention = AppliedRetention(
            retention_id=str(uuid4()),
            item_id=item_id,
            policy_id=policy.policy_id,
            trigger_date=trigger_date,
            disposition_date=disposition_date
        )

        self.applied_retentions[retention.retention_id] = retention

        # Schedule disposition
        await self.disposition_queue.schedule(retention, policy)

        logger.info(f"Applied retention to {item_id}, disposition on {disposition_date}")
        return retention

    async def place_hold(
        self,
        hold_type: str,
        reason: str,
        placed_by: str,
        items: Optional[List[str]] = None,
        **kwargs
    ) -> RetentionHold:
        """Place retention hold on items."""
        hold = await self.hold_manager.place_hold(
            hold_type, reason, placed_by, items, **kwargs
        )

        # Update affected retentions
        for item_id in hold.items:
            for retention in self.applied_retentions.values():
                if retention.item_id == item_id:
                    retention.holds.add(hold.hold_id)

            # Update queue items
            for queue_item in self.disposition_queue.queue.values():
                if queue_item.item_id == item_id:
                    queue_item.on_hold = True
                    queue_item.hold_ids.add(hold.hold_id)

        return hold

    async def release_hold(self, hold_id: str) -> bool:
        """Release retention hold."""
        success = await self.hold_manager.release_hold(hold_id)

        if success:
            # Update affected retentions
            for retention in self.applied_retentions.values():
                if hold_id in retention.holds:
                    retention.holds.remove(hold_id)

            # Update queue items
            for queue_item in self.disposition_queue.queue.values():
                if hold_id in queue_item.hold_ids:
                    queue_item.hold_ids.remove(hold_id)
                    if not queue_item.hold_ids:
                        queue_item.on_hold = False

        return success

    async def request_exception(
        self,
        item_id: str,
        policy_id: str,
        reason: str,
        requested_by: str,
        new_disposition_date: Optional[datetime] = None,
        permanent: bool = False
    ) -> RetentionException:
        """Request exception to retention policy."""
        await asyncio.sleep(0.05)

        exception = RetentionException(
            exception_id=str(uuid4()),
            item_id=item_id,
            policy_id=policy_id,
            reason=reason,
            requested_by=requested_by,
            new_disposition_date=new_disposition_date,
            permanent_exception=permanent
        )

        self.exceptions[exception.exception_id] = exception

        logger.info(f"Requested retention exception for {item_id}")
        return exception

    async def approve_exception(
        self,
        exception_id: str,
        approved_by: str
    ) -> bool:
        """Approve retention exception."""
        await asyncio.sleep(0.05)

        if exception_id not in self.exceptions:
            return False

        exception = self.exceptions[exception_id]
        exception.approved_by = approved_by

        # Update retention if new date specified
        if exception.new_disposition_date:
            for retention in self.applied_retentions.values():
                if retention.item_id == exception.item_id:
                    retention.disposition_date = exception.new_disposition_date
                    retention.exceptions.append(exception_id)

        logger.info(f"Approved retention exception {exception_id}")
        return True

    async def get_disposition_queue(
        self,
        days_ahead: int = 30,
        requires_approval: Optional[bool] = None
    ) -> List[DispositionQueueItem]:
        """Get disposition queue."""
        items = await self.disposition_queue.get_due_items(days_ahead)

        if requires_approval is not None:
            items = [i for i in items if i.requires_approval == requires_approval]

        return items

    async def approve_disposition(
        self,
        disposition_id: str,
        approver: str,
        notes: Optional[str] = None
    ) -> bool:
        """Approve disposition."""
        return await self.disposition_queue.approve(disposition_id, approver, notes)

    async def execute_disposition(
        self,
        disposition_id: str,
        executor: str
    ) -> bool:
        """Execute disposition."""
        return await self.disposition_queue.execute(disposition_id, executor)

    async def process_queue(
        self,
        auto_approve_simple: bool = False
    ) -> Dict[str, Any]:
        """Process disposition queue."""
        await asyncio.sleep(0.2)

        stats = {"processed": 0, "approved": 0, "executed": 0, "skipped": 0}

        due_items = await self.disposition_queue.get_due_items(days_ahead=0)

        for item in due_items:
            stats["processed"] += 1

            # Auto-approve if configured
            if auto_approve_simple and not item.requires_approval and not item.on_hold:
                await self.disposition_queue.approve(item.queue_item_id, "system")
                stats["approved"] += 1

            # Execute if approved and not on hold
            if item.approved and not item.on_hold:
                success = await self.disposition_queue.execute(item.queue_item_id, "system")
                if success:
                    stats["executed"] += 1
            else:
                stats["skipped"] += 1

        logger.info(f"Processed queue: {stats}")
        return stats

    async def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        await asyncio.sleep(0.1)

        queue_stats = await self.disposition_queue.get_statistics()
        active_policies = await self.policy_engine.get_active_policies()

        return {
            "total_policies": len(active_policies),
            "items_under_retention": len(self.applied_retentions),
            "disposition_queue": queue_stats,
            "active_holds": sum(1 for h in self.hold_manager.holds.values() if h.active),
            "pending_exceptions": sum(1 for e in self.exceptions.values() if not e.approved_by),
            "generated_at": datetime.now().isoformat()
        }


# Singleton instance
_retention_engine: Optional[RetentionEngine] = None


def get_retention_engine() -> RetentionEngine:
    """Get retention engine instance."""
    global _retention_engine
    if _retention_engine is None:
        _retention_engine = RetentionEngine()
    return _retention_engine
