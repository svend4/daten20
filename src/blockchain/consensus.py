"""
Consensus Module - Proof of Authority consensus mechanism
Implements PoA consensus for enterprise blockchain with authorized validators.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class ValidatorStatus(Enum):
    """Validator node status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class Validator:
    """Authorized validator node"""
    validator_id: str
    public_key: str
    name: str
    organization: str
    status: ValidatorStatus = ValidatorStatus.ACTIVE
    stake: int = 0
    blocks_validated: int = 0
    reputation_score: float = 100.0
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "validator_id": self.validator_id,
            "public_key": self.public_key,
            "name": self.name,
            "organization": self.organization,
            "status": self.status.value,
            "stake": self.stake,
            "blocks_validated": self.blocks_validated,
            "reputation_score": self.reputation_score,
            "joined_at": self.joined_at.isoformat(),
            "last_active": self.last_active.isoformat(),
        }


@dataclass
class ConsensusRound:
    """Consensus voting round"""
    round_id: str
    block_hash: str
    proposed_by: str
    votes: Dict[str, bool] = field(default_factory=dict)  # validator_id -> approved
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_consensus_reached: bool = False
    required_votes: int = 1


class ProofOfAuthority:
    """Proof of Authority consensus mechanism"""

    def __init__(self, min_validators: int = 1, consensus_threshold: float = 0.66):
        """
        Initialize PoA consensus

        Args:
            min_validators: Minimum number of validators required
            consensus_threshold: Percentage of validators needed for consensus (0-1)
        """
        self.validators: Dict[str, Validator] = {}
        self.min_validators = min_validators
        self.consensus_threshold = consensus_threshold
        self.consensus_rounds: Dict[str, ConsensusRound] = {}
        self.block_validators: Dict[str, str] = {}  # block_hash -> validator_id

    def add_validator(
        self,
        validator_id: str,
        public_key: str,
        name: str,
        organization: str,
        stake: int = 0
    ) -> Validator:
        """Add new authorized validator"""
        validator = Validator(
            validator_id=validator_id,
            public_key=public_key,
            name=name,
            organization=organization,
            stake=stake
        )

        self.validators[validator_id] = validator
        logger.info(f"Added validator: {validator_id} ({organization})")

        return validator

    def remove_validator(self, validator_id: str) -> bool:
        """Remove validator"""
        if validator_id in self.validators:
            self.validators[validator_id].status = ValidatorStatus.REVOKED
            logger.info(f"Revoked validator: {validator_id}")
            return True
        return False

    def suspend_validator(self, validator_id: str, reason: str) -> bool:
        """Suspend validator temporarily"""
        if validator_id in self.validators:
            self.validators[validator_id].status = ValidatorStatus.SUSPENDED
            logger.info(f"Suspended validator {validator_id}: {reason}")
            return True
        return False

    def activate_validator(self, validator_id: str) -> bool:
        """Activate suspended validator"""
        if validator_id in self.validators:
            validator = self.validators[validator_id]
            if validator.status == ValidatorStatus.SUSPENDED:
                validator.status = ValidatorStatus.ACTIVE
                logger.info(f"Activated validator: {validator_id}")
                return True
        return False

    def get_active_validators(self) -> List[Validator]:
        """Get list of active validators"""
        return [
            v for v in self.validators.values()
            if v.status == ValidatorStatus.ACTIVE
        ]

    def select_validator(self, block_data: str) -> Optional[Validator]:
        """
        Select validator for next block using deterministic selection

        Uses round-robin based on block data hash
        """
        active_validators = self.get_active_validators()

        if not active_validators:
            logger.error("No active validators available")
            return None

        # Deterministic selection based on block data
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        index = int(block_hash, 16) % len(active_validators)

        selected = active_validators[index]
        selected.last_active = datetime.utcnow()

        logger.info(f"Selected validator: {selected.validator_id}")
        return selected

    def validate_block(
        self,
        block_hash: str,
        validator_id: str,
        signature: Optional[str] = None
    ) -> bool:
        """Validate that block is from authorized validator"""
        validator = self.validators.get(validator_id)

        if not validator:
            logger.error(f"Unknown validator: {validator_id}")
            return False

        if validator.status != ValidatorStatus.ACTIVE:
            logger.error(f"Validator {validator_id} is not active")
            return False

        # TODO: Verify signature with validator's public key
        # For now, accept if validator is active

        # Record validation
        self.block_validators[block_hash] = validator_id
        validator.blocks_validated += 1
        validator.last_active = datetime.utcnow()

        logger.info(f"Block {block_hash[:8]} validated by {validator_id}")
        return True

    def start_consensus_round(
        self,
        block_hash: str,
        proposed_by: str
    ) -> ConsensusRound:
        """Start new consensus voting round"""
        round_id = hashlib.sha256(
            f"{block_hash}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        active_validators = self.get_active_validators()
        required_votes = max(
            1,
            int(len(active_validators) * self.consensus_threshold)
        )

        consensus_round = ConsensusRound(
            round_id=round_id,
            block_hash=block_hash,
            proposed_by=proposed_by,
            required_votes=required_votes
        )

        self.consensus_rounds[round_id] = consensus_round
        logger.info(f"Started consensus round {round_id} for block {block_hash[:8]}")

        return consensus_round

    def cast_vote(
        self,
        round_id: str,
        validator_id: str,
        approved: bool
    ) -> bool:
        """Cast validator vote in consensus round"""
        consensus_round = self.consensus_rounds.get(round_id)

        if not consensus_round:
            logger.error(f"Consensus round not found: {round_id}")
            return False

        if consensus_round.is_consensus_reached:
            logger.warning(f"Consensus already reached for round {round_id}")
            return False

        validator = self.validators.get(validator_id)
        if not validator or validator.status != ValidatorStatus.ACTIVE:
            logger.error(f"Invalid or inactive validator: {validator_id}")
            return False

        # Record vote
        consensus_round.votes[validator_id] = approved
        logger.info(f"Validator {validator_id} voted {'Yes' if approved else 'No'} for round {round_id}")

        # Check if consensus reached
        approvals = sum(1 for vote in consensus_round.votes.values() if vote)

        if approvals >= consensus_round.required_votes:
            consensus_round.is_consensus_reached = True
            consensus_round.completed_at = datetime.utcnow()
            logger.info(f"Consensus reached for round {round_id}")

        return True

    def check_consensus(self, round_id: str) -> bool:
        """Check if consensus has been reached"""
        consensus_round = self.consensus_rounds.get(round_id)

        if not consensus_round:
            return False

        return consensus_round.is_consensus_reached

    def get_validator_reputation(self, validator_id: str) -> float:
        """Get validator reputation score"""
        validator = self.validators.get(validator_id)
        if not validator:
            return 0.0

        return validator.reputation_score

    def update_validator_reputation(
        self,
        validator_id: str,
        delta: float,
        reason: str
    ):
        """Update validator reputation score"""
        validator = self.validators.get(validator_id)
        if not validator:
            return

        validator.reputation_score = max(0.0, min(100.0, validator.reputation_score + delta))
        logger.info(f"Updated reputation for {validator_id}: {delta:+.2f} ({reason})")

    def get_validator_statistics(self, validator_id: str) -> Dict:
        """Get validator statistics"""
        validator = self.validators.get(validator_id)
        if not validator:
            return {}

        return {
            "validator_id": validator_id,
            "status": validator.status.value,
            "blocks_validated": validator.blocks_validated,
            "reputation_score": validator.reputation_score,
            "stake": validator.stake,
            "uptime_days": (datetime.utcnow() - validator.joined_at).days,
            "last_active": validator.last_active.isoformat(),
        }

    def get_network_statistics(self) -> Dict:
        """Get overall network consensus statistics"""
        active_validators = self.get_active_validators()

        return {
            "total_validators": len(self.validators),
            "active_validators": len(active_validators),
            "min_validators": self.min_validators,
            "consensus_threshold": self.consensus_threshold,
            "total_blocks_validated": sum(v.blocks_validated for v in self.validators.values()),
            "average_reputation": sum(v.reputation_score for v in active_validators) / len(active_validators) if active_validators else 0,
        }


# Singleton instance
_poa_consensus = None

def get_consensus() -> ProofOfAuthority:
    """Get singleton PoA consensus instance"""
    global _poa_consensus
    if _poa_consensus is None:
        _poa_consensus = ProofOfAuthority()
    return _poa_consensus
