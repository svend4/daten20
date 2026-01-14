"""
Records Management System

Comprehensive document lifecycle management with retention policies,
disposition scheduling, and vital records tracking.

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


class RecordClass(Enum):
    """Standard record classifications."""
    FINANCIAL_RECORDS = "financial_records"
    TAX_RECORDS = "tax_records"
    LEGAL_CONTRACTS = "legal_contracts"
    HR_PERSONNEL = "hr_personnel"
    CUSTOMER_RECORDS = "customer_records"
    EMAIL_CORRESPONDENCE = "email_correspondence"
    BUSINESS_RECORDS = "business_records"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    COMPLIANCE_RECORDS = "compliance_records"
    OPERATIONAL_RECORDS = "operational_records"


class LifecycleState(Enum):
    """Record lifecycle states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DISPOSED = "disposed"
    LEGAL_HOLD = "legal_hold"


class TriggerEvent(Enum):
    """Retention trigger events."""
    CREATION_DATE = "creation_date"
    MODIFICATION_DATE = "modification_date"
    CLOSURE_DATE = "closure_date"
    FISCAL_YEAR_END = "fiscal_year_end"
    CONTRACT_END = "contract_end"
    EMPLOYEE_TERMINATION = "employee_termination"


@dataclass
class RetentionSchedule:
    """Retention policy configuration."""
    schedule_id: str
    record_class: RecordClass
    retention_years: int
    trigger_event: TriggerEvent
    disposition_action: str = "permanent_delete"
    legal_review_required: bool = False
    vital_record: bool = False
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Record:
    """Managed record."""
    record_id: str
    document_id: str
    record_class: RecordClass
    title: str
    lifecycle_state: LifecycleState
    retention_schedule_id: Optional[str] = None
    declared_date: datetime = field(default_factory=datetime.now)
    retention_trigger_date: Optional[datetime] = None
    disposition_date: Optional[datetime] = None
    legal_holds: Set[str] = field(default_factory=set)
    is_vital: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    exceptions: List[str] = field(default_factory=list)


@dataclass
class LegalHold:
    """Legal hold on record."""
    hold_id: str
    case_id: str
    case_name: str
    reason: str
    placed_date: datetime = field(default_factory=datetime.now)
    released_date: Optional[datetime] = None
    active: bool = True


@dataclass
class DispositionItem:
    """Scheduled disposition."""
    disposition_id: str
    record_id: str
    scheduled_date: datetime
    action: str
    requires_approval: bool
    approved: bool = False
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    executed: bool = False
    executed_date: Optional[datetime] = None


@dataclass
class VitalRecord:
    """Critical/vital record designation."""
    record_id: str
    designation_reason: str
    recovery_priority: int  # 1=highest
    backup_location: str
    last_backup: Optional[datetime] = None
    designated_date: datetime = field(default_factory=datetime.now)


class RecordLifecycle:
    """Record lifecycle state machine."""

    def __init__(self):
        self.transitions = {
            LifecycleState.ACTIVE: [LifecycleState.INACTIVE, LifecycleState.LEGAL_HOLD],
            LifecycleState.INACTIVE: [LifecycleState.ACTIVE, LifecycleState.ARCHIVED, LifecycleState.LEGAL_HOLD],
            LifecycleState.ARCHIVED: [LifecycleState.DISPOSED, LifecycleState.LEGAL_HOLD],
            LifecycleState.LEGAL_HOLD: [LifecycleState.ACTIVE, LifecycleState.INACTIVE, LifecycleState.ARCHIVED],
            LifecycleState.DISPOSED: []
        }

    def can_transition(self, current: LifecycleState, target: LifecycleState) -> bool:
        """Check if state transition is allowed."""
        return target in self.transitions.get(current, [])

    async def transition(
        self,
        record: Record,
        target_state: LifecycleState,
        reason: Optional[str] = None
    ) -> bool:
        """Execute state transition."""
        if not self.can_transition(record.lifecycle_state, target_state):
            logger.warning(f"Invalid transition from {record.lifecycle_state} to {target_state}")
            return False

        old_state = record.lifecycle_state
        record.lifecycle_state = target_state

        logger.info(f"Record {record.record_id} transitioned: {old_state} -> {target_state}")
        return True

    async def auto_transition(self, record: Record) -> bool:
        """Automatically transition based on age and activity."""
        await asyncio.sleep(0.01)  # Simulate processing

        # Active -> Inactive (after 1 year of no modification)
        if record.lifecycle_state == LifecycleState.ACTIVE:
            age_days = (datetime.now() - record.declared_date).days
            if age_days > 365:
                return await self.transition(record, LifecycleState.INACTIVE, "Auto: 1 year inactive")

        # Inactive -> Archived (after 2 years total)
        elif record.lifecycle_state == LifecycleState.INACTIVE:
            age_days = (datetime.now() - record.declared_date).days
            if age_days > 730:
                return await self.transition(record, LifecycleState.ARCHIVED, "Auto: 2 years old")

        return False


class DispositionManager:
    """Automated disposition scheduling and execution."""

    def __init__(self):
        self.queue: List[DispositionItem] = []

    async def schedule_disposition(
        self,
        record: Record,
        retention_schedule: RetentionSchedule
    ) -> DispositionItem:
        """Schedule record for disposition."""
        await asyncio.sleep(0.05)

        # Calculate disposition date
        if record.retention_trigger_date:
            trigger_date = record.retention_trigger_date
        else:
            trigger_date = record.declared_date

        disposition_date = trigger_date + timedelta(days=365 * retention_schedule.retention_years)

        disposition = DispositionItem(
            disposition_id=str(uuid4()),
            record_id=record.record_id,
            scheduled_date=disposition_date,
            action=retention_schedule.disposition_action,
            requires_approval=retention_schedule.legal_review_required
        )

        self.queue.append(disposition)
        record.disposition_date = disposition_date

        logger.info(f"Scheduled disposition for {record.record_id} on {disposition_date}")
        return disposition

    async def get_disposition_queue(
        self,
        days_ahead: int = 30,
        requires_approval: Optional[bool] = None
    ) -> List[DispositionItem]:
        """Get upcoming dispositions."""
        await asyncio.sleep(0.05)

        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        queue = [
            d for d in self.queue
            if d.scheduled_date <= cutoff_date and not d.executed
        ]

        if requires_approval is not None:
            queue = [d for d in queue if d.requires_approval == requires_approval]

        return sorted(queue, key=lambda x: x.scheduled_date)

    async def approve_disposition(
        self,
        disposition_id: str,
        approver: str,
        notes: Optional[str] = None
    ) -> bool:
        """Approve scheduled disposition."""
        await asyncio.sleep(0.05)

        for disposition in self.queue:
            if disposition.disposition_id == disposition_id:
                disposition.approved = True
                disposition.approved_by = approver
                disposition.approved_date = datetime.now()
                logger.info(f"Disposition {disposition_id} approved by {approver}")
                return True

        return False

    async def execute_disposition(
        self,
        disposition_id: str,
        executor: str
    ) -> bool:
        """Execute approved disposition."""
        await asyncio.sleep(0.1)

        for disposition in self.queue:
            if disposition.disposition_id == disposition_id:
                if disposition.requires_approval and not disposition.approved:
                    logger.error(f"Disposition {disposition_id} not approved")
                    return False

                disposition.executed = True
                disposition.executed_date = datetime.now()

                logger.info(f"Executed disposition {disposition_id}: {disposition.action}")
                return True

        return False

    async def process_queue(self, auto_approve_simple: bool = False) -> Dict[str, int]:
        """Process disposition queue."""
        await asyncio.sleep(0.2)

        stats = {
            "processed": 0,
            "approved": 0,
            "executed": 0,
            "skipped": 0
        }

        today = datetime.now()

        for disposition in self.queue:
            if disposition.executed or disposition.scheduled_date > today:
                continue

            stats["processed"] += 1

            # Auto-approve if configured and doesn't require legal review
            if auto_approve_simple and not disposition.requires_approval:
                disposition.approved = True
                disposition.approved_by = "system"
                disposition.approved_date = today
                stats["approved"] += 1

            # Execute if approved
            if disposition.approved and not disposition.executed:
                disposition.executed = True
                disposition.executed_date = today
                stats["executed"] += 1
            else:
                stats["skipped"] += 1

        logger.info(f"Processed disposition queue: {stats}")
        return stats


class VitalRecordsManager:
    """Vital records program management."""

    def __init__(self):
        self.vital_records: Dict[str, VitalRecord] = {}

    async def designate_vital(
        self,
        record_id: str,
        reason: str,
        priority: int = 1,
        backup_location: str = "offsite_vault"
    ) -> VitalRecord:
        """Designate record as vital."""
        await asyncio.sleep(0.05)

        vital = VitalRecord(
            record_id=record_id,
            designation_reason=reason,
            recovery_priority=priority,
            backup_location=backup_location
        )

        self.vital_records[record_id] = vital

        logger.info(f"Designated {record_id} as vital record (priority {priority})")
        return vital

    async def backup_vital_record(self, record_id: str) -> bool:
        """Backup vital record."""
        await asyncio.sleep(0.2)

        if record_id not in self.vital_records:
            return False

        vital = self.vital_records[record_id]
        vital.last_backup = datetime.now()

        logger.info(f"Backed up vital record {record_id} to {vital.backup_location}")
        return True

    async def get_vital_records(
        self,
        priority: Optional[int] = None
    ) -> List[VitalRecord]:
        """Get vital records list."""
        records = list(self.vital_records.values())

        if priority is not None:
            records = [r for r in records if r.recovery_priority == priority]

        return sorted(records, key=lambda x: x.recovery_priority)

    async def verify_backups(self) -> Dict[str, Any]:
        """Verify vital records backup status."""
        await asyncio.sleep(0.1)

        total = len(self.vital_records)
        backed_up = sum(1 for v in self.vital_records.values() if v.last_backup is not None)
        outdated = sum(
            1 for v in self.vital_records.values()
            if v.last_backup and (datetime.now() - v.last_backup).days > 30
        )

        return {
            "total_vital_records": total,
            "backed_up": backed_up,
            "never_backed_up": total - backed_up,
            "outdated_backups": outdated,
            "compliance_rate": (backed_up / total * 100) if total > 0 else 100.0
        }


class RecordsManager:
    """Main records management system."""

    def __init__(self):
        self.records: Dict[str, Record] = {}
        self.schedules: Dict[str, RetentionSchedule] = {}
        self.legal_holds: Dict[str, LegalHold] = {}
        self.lifecycle = RecordLifecycle()
        self.disposition_manager = DispositionManager()
        self.vital_records_manager = VitalRecordsManager()
        self._initialize_default_schedules()

    def _initialize_default_schedules(self):
        """Initialize default retention schedules."""
        defaults = [
            RetentionSchedule(
                schedule_id="fin-001",
                record_class=RecordClass.FINANCIAL_RECORDS,
                retention_years=7,
                trigger_event=TriggerEvent.FISCAL_YEAR_END,
                legal_review_required=True,
                description="Financial records - 7 years per IRS requirements"
            ),
            RetentionSchedule(
                schedule_id="tax-001",
                record_class=RecordClass.TAX_RECORDS,
                retention_years=7,
                trigger_event=TriggerEvent.FISCAL_YEAR_END,
                legal_review_required=True,
                vital_record=True,
                description="Tax records - 7 years"
            ),
            RetentionSchedule(
                schedule_id="legal-001",
                record_class=RecordClass.LEGAL_CONTRACTS,
                retention_years=10,
                trigger_event=TriggerEvent.CONTRACT_END,
                legal_review_required=True,
                description="Legal contracts - 10 years after termination"
            ),
            RetentionSchedule(
                schedule_id="hr-001",
                record_class=RecordClass.HR_PERSONNEL,
                retention_years=7,
                trigger_event=TriggerEvent.EMPLOYEE_TERMINATION,
                legal_review_required=True,
                description="HR personnel files - 7 years after termination"
            ),
            RetentionSchedule(
                schedule_id="email-001",
                record_class=RecordClass.EMAIL_CORRESPONDENCE,
                retention_years=3,
                trigger_event=TriggerEvent.CREATION_DATE,
                legal_review_required=False,
                description="Email retention - 3 years"
            ),
        ]

        for schedule in defaults:
            self.schedules[schedule.schedule_id] = schedule

    async def declare_record(
        self,
        document_id: str,
        record_class: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None,
        trigger_date: Optional[datetime] = None
    ) -> Record:
        """Declare document as formal record."""
        await asyncio.sleep(0.05)

        record_class_enum = RecordClass(record_class)

        record = Record(
            record_id=str(uuid4()),
            document_id=document_id,
            record_class=record_class_enum,
            title=title,
            lifecycle_state=LifecycleState.ACTIVE,
            retention_trigger_date=trigger_date,
            metadata=metadata or {}
        )

        self.records[record.record_id] = record

        # Apply default retention schedule
        await self.auto_apply_retention(record)

        logger.info(f"Declared record {record.record_id}: {title}")
        return record

    async def auto_apply_retention(self, record: Record) -> bool:
        """Automatically apply retention schedule to record."""
        # Find matching schedule
        for schedule in self.schedules.values():
            if schedule.record_class == record.record_class:
                await self.apply_retention(record.record_id, schedule.schedule_id)
                return True

        return False

    async def apply_retention(
        self,
        record_id: str,
        schedule_id: str,
        trigger_date: Optional[datetime] = None
    ) -> bool:
        """Apply retention schedule to record."""
        await asyncio.sleep(0.05)

        if record_id not in self.records or schedule_id not in self.schedules:
            return False

        record = self.records[record_id]
        schedule = self.schedules[schedule_id]

        record.retention_schedule_id = schedule_id
        if trigger_date:
            record.retention_trigger_date = trigger_date

        # Schedule disposition
        await self.disposition_manager.schedule_disposition(record, schedule)

        # Mark as vital if schedule indicates
        if schedule.vital_record:
            record.is_vital = True
            await self.vital_records_manager.designate_vital(
                record_id,
                f"Vital per retention schedule: {schedule.description}"
            )

        logger.info(f"Applied retention schedule {schedule_id} to {record_id}")
        return True

    async def place_legal_hold(
        self,
        record_id: str,
        case_id: str,
        case_name: str,
        reason: str
    ) -> LegalHold:
        """Place legal hold on record."""
        await asyncio.sleep(0.05)

        hold = LegalHold(
            hold_id=str(uuid4()),
            case_id=case_id,
            case_name=case_name,
            reason=reason
        )

        self.legal_holds[hold.hold_id] = hold

        if record_id in self.records:
            record = self.records[record_id]
            record.legal_holds.add(hold.hold_id)
            await self.lifecycle.transition(record, LifecycleState.LEGAL_HOLD, reason)

        logger.info(f"Placed legal hold on {record_id}: {case_name}")
        return hold

    async def release_legal_hold(
        self,
        hold_id: str,
        restore_state: Optional[LifecycleState] = None
    ) -> bool:
        """Release legal hold."""
        await asyncio.sleep(0.05)

        if hold_id not in self.legal_holds:
            return False

        hold = self.legal_holds[hold_id]
        hold.active = False
        hold.released_date = datetime.now()

        # Remove hold from records
        for record in self.records.values():
            if hold_id in record.legal_holds:
                record.legal_holds.remove(hold_id)

                # Restore state if no other holds
                if not record.legal_holds and restore_state:
                    await self.lifecycle.transition(record, restore_state, "Legal hold released")

        logger.info(f"Released legal hold {hold_id}")
        return True

    async def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        await asyncio.sleep(0.1)

        total_records = len(self.records)
        by_class = {}
        by_state = {}

        for record in self.records.values():
            class_name = record.record_class.value
            state_name = record.lifecycle_state.value

            by_class[class_name] = by_class.get(class_name, 0) + 1
            by_state[state_name] = by_state.get(state_name, 0) + 1

        vital_status = await self.vital_records_manager.verify_backups()
        disposition_queue = await self.disposition_manager.get_disposition_queue(days_ahead=90)

        return {
            "total_records": total_records,
            "by_class": by_class,
            "by_state": by_state,
            "legal_holds_active": sum(1 for h in self.legal_holds.values() if h.active),
            "vital_records": vital_status,
            "upcoming_dispositions": len(disposition_queue),
            "retention_schedules": len(self.schedules),
            "generated_at": datetime.now().isoformat()
        }


# Singleton instance
_records_manager: Optional[RecordsManager] = None


def get_records_manager() -> RecordsManager:
    """Get records manager instance."""
    global _records_manager
    if _records_manager is None:
        _records_manager = RecordsManager()
    return _records_manager
