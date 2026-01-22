"""
Smart Contracts Module - Simple smart contract execution for document operations
Provides basic smart contract functionality for automated document workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class ContractState(Enum):
    """Smart contract execution state"""
    PENDING = "pending"
    ACTIVE = "active"
    EXECUTED = "executed"
    FAILED = "failed"
    REVOKED = "revoked"


class ContractType(Enum):
    """Types of smart contracts"""
    DOCUMENT_APPROVAL = "document_approval"
    DOCUMENT_TRANSFER = "document_transfer"
    DOCUMENT_ARCHIVAL = "document_archival"
    DOCUMENT_SHARING = "document_sharing"
    AUTOMATED_WORKFLOW = "automated_workflow"
    ESCROW = "escrow"
    MULTI_SIGNATURE = "multi_signature"


@dataclass
class ContractCondition:
    """Condition that must be met for contract execution"""
    condition_type: str
    parameters: Dict[str, Any]
    is_met: bool = False

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if condition is met"""
        if self.condition_type == "approval_count":
            required = self.parameters.get("required_approvals", 1)
            current = context.get("approval_count", 0)
            self.is_met = current >= required

        elif self.condition_type == "time_elapsed":
            start_time = datetime.fromisoformat(self.parameters.get("start_time"))
            duration = self.parameters.get("duration_hours", 24)
            elapsed = (datetime.utcnow() - start_time).total_seconds() / 3600
            self.is_met = elapsed >= duration

        elif self.condition_type == "document_verified":
            self.is_met = context.get("document_verified", False)

        elif self.condition_type == "payment_received":
            self.is_met = context.get("payment_received", False)

        elif self.condition_type == "all_signatures":
            required_signers = set(self.parameters.get("required_signers", []))
            current_signers = set(context.get("signers", []))
            self.is_met = required_signers.issubset(current_signers)

        return self.is_met


@dataclass
class ContractAction:
    """Action to execute when conditions are met"""
    action_type: str
    parameters: Dict[str, Any]
    executed: bool = False
    execution_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class SmartContract:
    """Smart contract for automated document operations"""
    contract_id: str
    contract_type: ContractType
    title: str
    description: str
    creator: str
    participants: List[str]
    conditions: List[ContractCondition]
    actions: List[ContractAction]
    state: ContractState = ContractState.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type.value,
            "title": self.title,
            "description": self.description,
            "creator": self.creator,
            "participants": self.participants,
            "conditions": [
                {"type": c.condition_type, "parameters": c.parameters, "is_met": c.is_met}
                for c in self.conditions
            ],
            "actions": [
                {
                    "type": a.action_type,
                    "parameters": a.parameters,
                    "executed": a.executed,
                    "result": a.result
                }
                for a in self.actions
            ],
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "metadata": self.metadata,
        }

    def get_hash(self) -> str:
        """Get contract hash"""
        contract_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(contract_str.encode()).hexdigest()


class SmartContractEngine:
    """Smart contract execution engine"""

    def __init__(self):
        self.contracts: Dict[str, SmartContract] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default action handlers"""
        self.action_handlers["approve_document"] = self._handle_approve_document
        self.action_handlers["transfer_document"] = self._handle_transfer_document
        self.action_handlers["archive_document"] = self._handle_archive_document
        self.action_handlers["notify_user"] = self._handle_notify_user
        self.action_handlers["create_audit_log"] = self._handle_create_audit_log

    def create_contract(
        self,
        contract_type: ContractType,
        title: str,
        description: str,
        creator: str,
        participants: List[str],
        conditions: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> SmartContract:
        """Create new smart contract"""
        contract_id = hashlib.sha256(
            f"{creator}{title}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        contract_conditions = [
            ContractCondition(
                condition_type=c["type"],
                parameters=c.get("parameters", {})
            )
            for c in conditions
        ]

        contract_actions = [
            ContractAction(
                action_type=a["type"],
                parameters=a.get("parameters", {})
            )
            for a in actions
        ]

        contract = SmartContract(
            contract_id=contract_id,
            contract_type=contract_type,
            title=title,
            description=description,
            creator=creator,
            participants=participants,
            conditions=contract_conditions,
            actions=contract_actions,
            metadata=metadata or {}
        )

        self.contracts[contract_id] = contract
        logger.info(f"Created smart contract: {contract_id}")

        return contract

    def activate_contract(self, contract_id: str) -> bool:
        """Activate a smart contract"""
        contract = self.contracts.get(contract_id)
        if not contract:
            logger.error(f"Contract not found: {contract_id}")
            return False

        if contract.state != ContractState.PENDING:
            logger.error(f"Contract {contract_id} is not in PENDING state")
            return False

        contract.state = ContractState.ACTIVE
        contract.activated_at = datetime.utcnow()
        logger.info(f"Activated contract: {contract_id}")

        return True

    def update_context(self, contract_id: str, context_update: Dict[str, Any]) -> bool:
        """Update contract execution context"""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False

        contract.context.update(context_update)

        # Check if conditions are now met
        if contract.state == ContractState.ACTIVE:
            self._check_and_execute(contract)

        return True

    def _check_and_execute(self, contract: SmartContract):
        """Check conditions and execute if all are met"""
        # Evaluate all conditions
        all_met = all(condition.evaluate(contract.context) for condition in contract.conditions)

        if all_met and contract.state == ContractState.ACTIVE:
            logger.info(f"All conditions met for contract {contract.contract_id}, executing...")
            self._execute_contract(contract)

    def _execute_contract(self, contract: SmartContract):
        """Execute contract actions"""
        try:
            for action in contract.actions:
                if action.executed:
                    continue

                handler = self.action_handlers.get(action.action_type)
                if not handler:
                    logger.warning(f"No handler for action type: {action.action_type}")
                    continue

                # Execute action
                result = handler(action.parameters, contract.context)
                action.executed = True
                action.execution_time = datetime.utcnow()
                action.result = result

                logger.info(f"Executed action {action.action_type} in contract {contract.contract_id}")

            contract.state = ContractState.EXECUTED
            contract.executed_at = datetime.utcnow()
            logger.info(f"Contract {contract.contract_id} fully executed")

        except Exception as e:
            contract.state = ContractState.FAILED
            logger.error(f"Contract execution failed: {e}")

    def revoke_contract(self, contract_id: str, revoker: str) -> bool:
        """Revoke a contract"""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False

        if contract.creator != revoker:
            logger.error(f"Only creator can revoke contract")
            return False

        if contract.state in [ContractState.EXECUTED, ContractState.FAILED]:
            logger.error(f"Cannot revoke contract in {contract.state} state")
            return False

        contract.state = ContractState.REVOKED
        logger.info(f"Contract {contract_id} revoked by {revoker}")

        return True

    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get contract by ID"""
        return self.contracts.get(contract_id)

    def get_contracts_by_participant(self, user_id: str) -> List[SmartContract]:
        """Get all contracts involving a user"""
        return [
            contract for contract in self.contracts.values()
            if user_id in contract.participants or user_id == contract.creator
        ]

    def get_active_contracts(self) -> List[SmartContract]:
        """Get all active contracts"""
        return [
            contract for contract in self.contracts.values()
            if contract.state == ContractState.ACTIVE
        ]

    # Default action handlers

    def _handle_approve_document(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document approval action"""
        document_id = parameters.get("document_id")
        logger.info(f"Approving document: {document_id}")
        return {"success": True, "document_id": document_id, "approved": True}

    def _handle_transfer_document(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document transfer action"""
        document_id = parameters.get("document_id")
        from_user = parameters.get("from_user")
        to_user = parameters.get("to_user")
        logger.info(f"Transferring document {document_id} from {from_user} to {to_user}")
        return {"success": True, "document_id": document_id, "transferred": True}

    def _handle_archive_document(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document archival action"""
        document_id = parameters.get("document_id")
        logger.info(f"Archiving document: {document_id}")
        return {"success": True, "document_id": document_id, "archived": True}

    def _handle_notify_user(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user notification action"""
        user_id = parameters.get("user_id")
        message = parameters.get("message")
        logger.info(f"Notifying user {user_id}: {message}")
        return {"success": True, "user_id": user_id, "notified": True}

    def _handle_create_audit_log(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle audit log creation action"""
        event_type = parameters.get("event_type")
        details = parameters.get("details")
        logger.info(f"Creating audit log: {event_type}")
        return {"success": True, "event_type": event_type, "logged": True}

    def register_action_handler(self, action_type: str, handler: Callable):
        """Register custom action handler"""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered handler for action type: {action_type}")


# Singleton instance
_engine = None

def get_contract_engine() -> SmartContractEngine:
    """Get singleton contract engine instance"""
    global _engine
    if _engine is None:
        _engine = SmartContractEngine()
    return _engine
