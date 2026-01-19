"""
Notification Rules Engine

Provides a flexible rules engine for managing when and how notifications are sent.
Supports condition matching, event triggers, user/group targeting, scheduling, and throttling.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class RuleConditionOperator(str, Enum):
    """Rule condition operators"""

    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    IN = "in"
    NOT_IN = "not_in"


class RuleLogicOperator(str, Enum):
    """Logic operators for combining conditions"""

    AND = "and"
    OR = "or"
    NOT = "not"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    IN_APP = "in_app"


class RulePriority(str, Enum):
    """Rule priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ScheduleDay(str, Enum):
    """Days of the week"""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass
class RuleCondition:
    """Single condition in a rule"""

    field: str
    operator: RuleConditionOperator
    value: Any
    case_sensitive: bool = True


@dataclass
class RuleConditionGroup:
    """Group of conditions with logic operator"""

    operator: RuleLogicOperator
    conditions: List[RuleCondition] = field(default_factory=list)
    groups: List["RuleConditionGroup"] = field(default_factory=list)


@dataclass
class RuleSchedule:
    """Rule schedule configuration"""

    enabled: bool = True
    days: List[ScheduleDay] = field(default_factory=list)  # Empty = all days
    start_time: Optional[time] = None  # None = 00:00
    end_time: Optional[time] = None  # None = 23:59
    timezone: str = "UTC"


@dataclass
class RuleThrottling:
    """Rule throttling configuration"""

    enabled: bool = False
    max_per_user: int = 10  # Max notifications per user
    max_total: int = 100  # Max total notifications
    window_minutes: int = 60  # Time window in minutes
    reset_on_different_event: bool = False


@dataclass
class RuleDeduplication:
    """Rule deduplication configuration"""

    enabled: bool = False
    window_minutes: int = 60
    key_fields: List[str] = field(default_factory=list)  # Fields to use for dedup key


@dataclass
class NotificationRule:
    """Notification rule definition"""

    id: str
    name: str
    description: str
    enabled: bool = True
    priority: RulePriority = RulePriority.NORMAL

    # Conditions
    conditions: RuleConditionGroup = field(default_factory=lambda: RuleConditionGroup(operator=RuleLogicOperator.AND))

    # Targeting
    target_users: List[str] = field(default_factory=list)  # Empty = all users
    target_groups: List[str] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)

    # Channels
    channels: List[NotificationChannel] = field(default_factory=list)

    # Schedule
    schedule: RuleSchedule = field(default_factory=RuleSchedule)

    # Throttling & Deduplication
    throttling: RuleThrottling = field(default_factory=RuleThrottling)
    deduplication: RuleDeduplication = field(default_factory=RuleDeduplication)

    # Template
    template_id: Optional[str] = None
    template_variables: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


@dataclass
class NotificationEvent:
    """Event that triggers notification rules"""

    event_type: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    user_groups: List[str] = field(default_factory=list)
    user_roles: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationRuleExecution:
    """Result of rule execution"""

    rule_id: str
    matched: bool
    reason: str
    channels_used: List[NotificationChannel] = field(default_factory=list)
    throttled: bool = False
    deduplicated: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RuleEvaluator:
    """Evaluates rule conditions against events"""

    def evaluate_condition(self, condition: RuleCondition, event_data: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition

        Args:
            condition: Rule condition
            event_data: Event data to evaluate against

        Returns:
            True if condition matches
        """
        # Get field value from event data
        field_value = self._get_nested_value(event_data, condition.field)

        if field_value is None:
            return False

        # Apply case sensitivity for string comparisons
        if isinstance(field_value, str) and not condition.case_sensitive:
            field_value = field_value.lower()
            if isinstance(condition.value, str):
                condition.value = condition.value.lower()

        # Evaluate based on operator
        op = condition.operator

        if op == RuleConditionOperator.EQUALS:
            return field_value == condition.value
        elif op == RuleConditionOperator.NOT_EQUALS:
            return field_value != condition.value
        elif op == RuleConditionOperator.GREATER_THAN:
            return field_value > condition.value
        elif op == RuleConditionOperator.GREATER_THAN_OR_EQUAL:
            return field_value >= condition.value
        elif op == RuleConditionOperator.LESS_THAN:
            return field_value < condition.value
        elif op == RuleConditionOperator.LESS_THAN_OR_EQUAL:
            return field_value <= condition.value
        elif op == RuleConditionOperator.CONTAINS:
            return condition.value in field_value
        elif op == RuleConditionOperator.NOT_CONTAINS:
            return condition.value not in field_value
        elif op == RuleConditionOperator.STARTS_WITH:
            return str(field_value).startswith(str(condition.value))
        elif op == RuleConditionOperator.ENDS_WITH:
            return str(field_value).endswith(str(condition.value))
        elif op == RuleConditionOperator.REGEX:
            pattern = re.compile(condition.value)
            return bool(pattern.search(str(field_value)))
        elif op == RuleConditionOperator.IN:
            return field_value in condition.value
        elif op == RuleConditionOperator.NOT_IN:
            return field_value not in condition.value

        return False

    def evaluate_group(self, group: RuleConditionGroup, event_data: Dict[str, Any]) -> bool:
        """
        Evaluate a condition group

        Args:
            group: Rule condition group
            event_data: Event data to evaluate against

        Returns:
            True if group matches
        """
        if group.operator == RuleLogicOperator.AND:
            # All conditions must match
            for condition in group.conditions:
                if not self.evaluate_condition(condition, event_data):
                    return False

            # All nested groups must match
            for nested_group in group.groups:
                if not self.evaluate_group(nested_group, event_data):
                    return False

            return True

        elif group.operator == RuleLogicOperator.OR:
            # At least one condition must match
            for condition in group.conditions:
                if self.evaluate_condition(condition, event_data):
                    return True

            # At least one nested group must match
            for nested_group in group.groups:
                if self.evaluate_group(nested_group, event_data):
                    return True

            return False

        elif group.operator == RuleLogicOperator.NOT:
            # No conditions should match
            for condition in group.conditions:
                if self.evaluate_condition(condition, event_data):
                    return False

            # No nested groups should match
            for nested_group in group.groups:
                if self.evaluate_group(nested_group, event_data):
                    return False

            return True

        return False

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key.split(".")
        value = data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None

        return value


class NotificationRulesEngine:
    """Notification rules engine"""

    def __init__(self):
        self.rules: Dict[str, NotificationRule] = {}
        self.evaluator = RuleEvaluator()

        # Throttling tracking
        self._throttle_counters: Dict[str, Dict[str, List[datetime]]] = defaultdict(lambda: defaultdict(list))

        # Deduplication tracking
        self._dedup_keys: Dict[str, Set[str]] = defaultdict(set)

    def add_rule(self, rule: NotificationRule):
        """Add notification rule"""
        self.rules[rule.id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove notification rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def get_rule(self, rule_id: str) -> Optional[NotificationRule]:
        """Get notification rule by ID"""
        return self.rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> List[NotificationRule]:
        """List all rules"""
        rules = list(self.rules.values())

        if enabled_only:
            rules = [r for r in rules if r.enabled]

        return rules

    def evaluate_event(self, event: NotificationEvent) -> List[NotificationRuleExecution]:
        """
        Evaluate event against all rules

        Args:
            event: Notification event

        Returns:
            List of rule execution results
        """
        results = []

        for rule in self.list_rules(enabled_only=True):
            result = self._evaluate_rule(rule, event)
            results.append(result)

        return results

    def _evaluate_rule(self, rule: NotificationRule, event: NotificationEvent) -> NotificationRuleExecution:
        """Evaluate single rule against event"""

        # Check schedule
        if not self._check_schedule(rule.schedule):
            return NotificationRuleExecution(rule_id=rule.id, matched=False, reason="Outside schedule window")

        # Check conditions
        if not self.evaluator.evaluate_group(rule.conditions, event.data):
            return NotificationRuleExecution(rule_id=rule.id, matched=False, reason="Conditions not met")

        # Check targeting
        if not self._check_targeting(rule, event):
            return NotificationRuleExecution(rule_id=rule.id, matched=False, reason="Not targeted to this user/group")

        # Check deduplication
        if self._is_deduplicated(rule, event):
            return NotificationRuleExecution(
                rule_id=rule.id, matched=True, reason="Matched but deduplicated", deduplicated=True
            )

        # Check throttling
        if self._is_throttled(rule, event):
            return NotificationRuleExecution(
                rule_id=rule.id, matched=True, reason="Matched but throttled", throttled=True
            )

        # Rule matched!
        return NotificationRuleExecution(
            rule_id=rule.id, matched=True, reason="Rule matched successfully", channels_used=rule.channels
        )

    def _check_schedule(self, schedule: RuleSchedule) -> bool:
        """Check if current time is within schedule"""
        if not schedule.enabled:
            return True

        now = datetime.utcnow()

        # Check day of week
        if schedule.days:
            current_day = ScheduleDay(now.strftime("%A").lower())
            if current_day not in schedule.days:
                return False

        # Check time range
        current_time = now.time()

        if schedule.start_time and current_time < schedule.start_time:
            return False

        if schedule.end_time and current_time > schedule.end_time:
            return False

        return True

    def _check_targeting(self, rule: NotificationRule, event: NotificationEvent) -> bool:
        """Check if event matches targeting criteria"""

        # If no targeting specified, match all
        if not rule.target_users and not rule.target_groups and not rule.target_roles:
            return True

        # Check user targeting
        if rule.target_users and event.user_id in rule.target_users:
            return True

        # Check group targeting
        if rule.target_groups:
            for group in event.user_groups:
                if group in rule.target_groups:
                    return True

        # Check role targeting
        if rule.target_roles:
            for role in event.user_roles:
                if role in rule.target_roles:
                    return True

        return False

    def _is_throttled(self, rule: NotificationRule, event: NotificationEvent) -> bool:
        """Check if notification should be throttled"""
        if not rule.throttling.enabled:
            return False

        now = datetime.utcnow()
        window_start = now - timedelta(minutes=rule.throttling.window_minutes)

        # Clean old timestamps
        user_key = f"{rule.id}:{event.user_id or 'anonymous'}"
        total_key = f"{rule.id}:total"

        self._throttle_counters[user_key] = [ts for ts in self._throttle_counters[user_key] if ts > window_start]
        self._throttle_counters[total_key] = [ts for ts in self._throttle_counters[total_key] if ts > window_start]

        # Check per-user limit
        if len(self._throttle_counters[user_key]) >= rule.throttling.max_per_user:
            return True

        # Check total limit
        if len(self._throttle_counters[total_key]) >= rule.throttling.max_total:
            return True

        # Not throttled - record this notification
        self._throttle_counters[user_key].append(now)
        self._throttle_counters[total_key].append(now)

        return False

    def _is_deduplicated(self, rule: NotificationRule, event: NotificationEvent) -> bool:
        """Check if notification should be deduplicated"""
        if not rule.deduplication.enabled:
            return False

        # Build deduplication key
        key_parts = [rule.id]

        for field in rule.deduplication.key_fields:
            value = event.data.get(field, "")
            key_parts.append(str(value))

        dedup_key = ":".join(key_parts)

        # Check if we've seen this key recently
        if dedup_key in self._dedup_keys[rule.id]:
            return True

        # Not a duplicate - record this key
        self._dedup_keys[rule.id].add(dedup_key)

        # Clean old keys (simple implementation - in production use TTL cache)
        # For now, limit to 1000 keys per rule
        if len(self._dedup_keys[rule.id]) > 1000:
            # Remove oldest half
            keys_to_remove = list(self._dedup_keys[rule.id])[:500]
            for k in keys_to_remove:
                self._dedup_keys[rule.id].discard(k)

        return False


# Global rules engine instance
_rules_engine: Optional[NotificationRulesEngine] = None


def get_rules_engine() -> NotificationRulesEngine:
    """Get global rules engine instance"""
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = NotificationRulesEngine()
    return _rules_engine


def create_simple_rule(
    rule_id: str,
    name: str,
    event_type: str,
    channels: List[NotificationChannel],
    target_users: Optional[List[str]] = None,
) -> NotificationRule:
    """
    Create a simple notification rule

    Args:
        rule_id: Rule ID
        name: Rule name
        event_type: Event type to match
        channels: Notification channels
        target_users: Target users (all if None)

    Returns:
        Notification rule
    """
    condition = RuleCondition(field="event_type", operator=RuleConditionOperator.EQUALS, value=event_type)

    condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

    return NotificationRule(
        id=rule_id,
        name=name,
        description=f"Send notification for {event_type}",
        conditions=condition_group,
        channels=channels,
        target_users=target_users or [],
    )
