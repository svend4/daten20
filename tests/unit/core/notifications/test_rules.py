"""Comprehensive tests for notification rules engine"""

from datetime import datetime, time, timedelta
from unittest.mock import patch

import pytest

from src.core.notifications.rules import (
    NotificationChannel,
    NotificationEvent,
    NotificationRule,
    NotificationRuleExecution,
    NotificationRulesEngine,
    RuleCondition,
    RuleConditionGroup,
    RuleConditionOperator,
    RuleDeduplication,
    RuleEvaluator,
    RuleLogicOperator,
    RulePriority,
    RuleSchedule,
    RuleThrottling,
    ScheduleDay,
    create_simple_rule,
    get_rules_engine,
)


class TestRuleConditionOperator:
    """Test RuleConditionOperator enum"""

    def test_equals_operator(self):
        """Test EQUALS operator value"""
        assert RuleConditionOperator.EQUALS == "eq"

    def test_not_equals_operator(self):
        """Test NOT_EQUALS operator value"""
        assert RuleConditionOperator.NOT_EQUALS == "ne"

    def test_comparison_operators(self):
        """Test comparison operators"""
        assert RuleConditionOperator.GREATER_THAN == "gt"
        assert RuleConditionOperator.GREATER_THAN_OR_EQUAL == "gte"
        assert RuleConditionOperator.LESS_THAN == "lt"
        assert RuleConditionOperator.LESS_THAN_OR_EQUAL == "lte"

    def test_string_operators(self):
        """Test string operators"""
        assert RuleConditionOperator.CONTAINS == "contains"
        assert RuleConditionOperator.NOT_CONTAINS == "not_contains"
        assert RuleConditionOperator.STARTS_WITH == "starts_with"
        assert RuleConditionOperator.ENDS_WITH == "ends_with"

    def test_regex_operator(self):
        """Test REGEX operator value"""
        assert RuleConditionOperator.REGEX == "regex"

    def test_membership_operators(self):
        """Test membership operators"""
        assert RuleConditionOperator.IN == "in"
        assert RuleConditionOperator.NOT_IN == "not_in"


class TestRuleLogicOperator:
    """Test RuleLogicOperator enum"""

    def test_and_operator(self):
        """Test AND operator value"""
        assert RuleLogicOperator.AND == "and"

    def test_or_operator(self):
        """Test OR operator value"""
        assert RuleLogicOperator.OR == "or"

    def test_not_operator(self):
        """Test NOT operator value"""
        assert RuleLogicOperator.NOT == "not"


class TestNotificationChannel:
    """Test NotificationChannel enum"""

    def test_channel_values(self):
        """Test all channel values"""
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.PUSH == "push"
        assert NotificationChannel.SLACK == "slack"
        assert NotificationChannel.TEAMS == "teams"
        assert NotificationChannel.DISCORD == "discord"
        assert NotificationChannel.TELEGRAM == "telegram"
        assert NotificationChannel.IN_APP == "in_app"


class TestRulePriority:
    """Test RulePriority enum"""

    def test_priority_values(self):
        """Test all priority values"""
        assert RulePriority.LOW == "low"
        assert RulePriority.NORMAL == "normal"
        assert RulePriority.HIGH == "high"
        assert RulePriority.CRITICAL == "critical"


class TestScheduleDay:
    """Test ScheduleDay enum"""

    def test_day_values(self):
        """Test all day values"""
        assert ScheduleDay.MONDAY == "monday"
        assert ScheduleDay.TUESDAY == "tuesday"
        assert ScheduleDay.WEDNESDAY == "wednesday"
        assert ScheduleDay.THURSDAY == "thursday"
        assert ScheduleDay.FRIDAY == "friday"
        assert ScheduleDay.SATURDAY == "saturday"
        assert ScheduleDay.SUNDAY == "sunday"


class TestRuleCondition:
    """Test RuleCondition dataclass"""

    def test_condition_creation(self):
        """Test creating a rule condition"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        assert condition.field == "status"
        assert condition.operator == RuleConditionOperator.EQUALS
        assert condition.value == "active"
        assert condition.case_sensitive is True

    def test_condition_case_insensitive(self):
        """Test case insensitive condition"""
        condition = RuleCondition(
            field="name", operator=RuleConditionOperator.EQUALS, value="test", case_sensitive=False
        )
        assert condition.case_sensitive is False


class TestRuleConditionGroup:
    """Test RuleConditionGroup dataclass"""

    def test_group_creation(self):
        """Test creating a condition group"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])
        assert group.operator == RuleLogicOperator.AND
        assert len(group.conditions) == 1
        assert len(group.groups) == 0

    def test_nested_groups(self):
        """Test nested condition groups"""
        condition1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        condition2 = RuleCondition(field="priority", operator=RuleConditionOperator.EQUALS, value="high")

        inner_group = RuleConditionGroup(operator=RuleLogicOperator.OR, conditions=[condition2])
        outer_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition1], groups=[inner_group])

        assert len(outer_group.conditions) == 1
        assert len(outer_group.groups) == 1


class TestRuleSchedule:
    """Test RuleSchedule dataclass"""

    def test_schedule_defaults(self):
        """Test default schedule values"""
        schedule = RuleSchedule()
        assert schedule.enabled is True
        assert schedule.days == []
        assert schedule.start_time is None
        assert schedule.end_time is None
        assert schedule.timezone == "UTC"

    def test_schedule_with_days(self):
        """Test schedule with specific days"""
        schedule = RuleSchedule(days=[ScheduleDay.MONDAY, ScheduleDay.FRIDAY])
        assert len(schedule.days) == 2

    def test_schedule_with_time_range(self):
        """Test schedule with time range"""
        schedule = RuleSchedule(start_time=time(9, 0), end_time=time(17, 0))
        assert schedule.start_time == time(9, 0)
        assert schedule.end_time == time(17, 0)


class TestRuleThrottling:
    """Test RuleThrottling dataclass"""

    def test_throttling_defaults(self):
        """Test default throttling values"""
        throttling = RuleThrottling()
        assert throttling.enabled is False
        assert throttling.max_per_user == 10
        assert throttling.max_total == 100
        assert throttling.window_minutes == 60
        assert throttling.reset_on_different_event is False

    def test_throttling_custom_values(self):
        """Test custom throttling values"""
        throttling = RuleThrottling(enabled=True, max_per_user=5, max_total=50, window_minutes=30)
        assert throttling.enabled is True
        assert throttling.max_per_user == 5
        assert throttling.max_total == 50
        assert throttling.window_minutes == 30


class TestRuleDeduplication:
    """Test RuleDeduplication dataclass"""

    def test_deduplication_defaults(self):
        """Test default deduplication values"""
        dedup = RuleDeduplication()
        assert dedup.enabled is False
        assert dedup.window_minutes == 60
        assert dedup.key_fields == []

    def test_deduplication_with_fields(self):
        """Test deduplication with key fields"""
        dedup = RuleDeduplication(enabled=True, window_minutes=30, key_fields=["user_id", "document_id"])
        assert dedup.enabled is True
        assert len(dedup.key_fields) == 2


class TestNotificationRule:
    """Test NotificationRule dataclass"""

    def test_rule_creation_minimal(self):
        """Test creating rule with minimal parameters"""
        rule = NotificationRule(id="rule1", name="Test Rule", description="Test description")
        assert rule.id == "rule1"
        assert rule.name == "Test Rule"
        assert rule.enabled is True
        assert rule.priority == RulePriority.NORMAL

    def test_rule_with_channels(self):
        """Test rule with notification channels"""
        rule = NotificationRule(
            id="rule1", name="Test Rule", description="Test", channels=[NotificationChannel.EMAIL, NotificationChannel.SMS]
        )
        assert len(rule.channels) == 2

    def test_rule_with_targeting(self):
        """Test rule with targeting"""
        rule = NotificationRule(
            id="rule1",
            name="Test Rule",
            description="Test",
            target_users=["user1", "user2"],
            target_groups=["admin"],
            target_roles=["manager"],
        )
        assert len(rule.target_users) == 2
        assert len(rule.target_groups) == 1
        assert len(rule.target_roles) == 1


class TestNotificationEvent:
    """Test NotificationEvent dataclass"""

    def test_event_creation(self):
        """Test creating notification event"""
        event = NotificationEvent(event_type="document.created", data={"document_id": "doc123"})
        assert event.event_type == "document.created"
        assert event.data["document_id"] == "doc123"
        assert event.user_id is None

    def test_event_with_user_info(self):
        """Test event with user information"""
        event = NotificationEvent(
            event_type="document.created",
            data={"document_id": "doc123"},
            user_id="user123",
            user_groups=["admin", "users"],
            user_roles=["editor"],
        )
        assert event.user_id == "user123"
        assert len(event.user_groups) == 2
        assert len(event.user_roles) == 1


class TestNotificationRuleExecution:
    """Test NotificationRuleExecution dataclass"""

    def test_execution_matched(self):
        """Test matched execution result"""
        result = NotificationRuleExecution(
            rule_id="rule1",
            matched=True,
            reason="Rule matched successfully",
            channels_used=[NotificationChannel.EMAIL],
        )
        assert result.matched is True
        assert result.throttled is False
        assert result.deduplicated is False

    def test_execution_throttled(self):
        """Test throttled execution result"""
        result = NotificationRuleExecution(rule_id="rule1", matched=True, reason="Throttled", throttled=True)
        assert result.throttled is True


class TestRuleEvaluatorConditions:
    """Test RuleEvaluator condition evaluation"""

    def setup_method(self):
        """Setup evaluator for each test"""
        self.evaluator = RuleEvaluator()

    def test_equals_operator(self):
        """Test EQUALS operator"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        event_data = {"status": "active"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

        event_data = {"status": "inactive"}
        assert self.evaluator.evaluate_condition(condition, event_data) is False

    def test_not_equals_operator(self):
        """Test NOT_EQUALS operator"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.NOT_EQUALS, value="deleted")
        event_data = {"status": "active"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_greater_than_operator(self):
        """Test GREATER_THAN operator"""
        condition = RuleCondition(field="count", operator=RuleConditionOperator.GREATER_THAN, value=5)
        event_data = {"count": 10}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

        event_data = {"count": 3}
        assert self.evaluator.evaluate_condition(condition, event_data) is False

    def test_greater_than_or_equal_operator(self):
        """Test GREATER_THAN_OR_EQUAL operator"""
        condition = RuleCondition(field="count", operator=RuleConditionOperator.GREATER_THAN_OR_EQUAL, value=5)
        event_data = {"count": 5}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_less_than_operator(self):
        """Test LESS_THAN operator"""
        condition = RuleCondition(field="count", operator=RuleConditionOperator.LESS_THAN, value=10)
        event_data = {"count": 5}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_less_than_or_equal_operator(self):
        """Test LESS_THAN_OR_EQUAL operator"""
        condition = RuleCondition(field="count", operator=RuleConditionOperator.LESS_THAN_OR_EQUAL, value=5)
        event_data = {"count": 5}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_contains_operator(self):
        """Test CONTAINS operator"""
        condition = RuleCondition(field="title", operator=RuleConditionOperator.CONTAINS, value="test")
        event_data = {"title": "this is a test document"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_not_contains_operator(self):
        """Test NOT_CONTAINS operator"""
        condition = RuleCondition(field="title", operator=RuleConditionOperator.NOT_CONTAINS, value="error")
        event_data = {"title": "this is a test document"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_starts_with_operator(self):
        """Test STARTS_WITH operator"""
        condition = RuleCondition(field="title", operator=RuleConditionOperator.STARTS_WITH, value="Test")
        event_data = {"title": "Test Document"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_ends_with_operator(self):
        """Test ENDS_WITH operator"""
        condition = RuleCondition(field="filename", operator=RuleConditionOperator.ENDS_WITH, value=".pdf")
        event_data = {"filename": "document.pdf"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_regex_operator(self):
        """Test REGEX operator"""
        condition = RuleCondition(field="email", operator=RuleConditionOperator.REGEX, value=r".*@example\.com")
        event_data = {"email": "user@example.com"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

        event_data = {"email": "user@other.com"}
        assert self.evaluator.evaluate_condition(condition, event_data) is False

    def test_in_operator(self):
        """Test IN operator"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.IN, value=["active", "pending"])
        event_data = {"status": "active"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_not_in_operator(self):
        """Test NOT_IN operator"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.NOT_IN, value=["deleted", "archived"])
        event_data = {"status": "active"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_case_insensitive_comparison(self):
        """Test case insensitive comparison"""
        condition = RuleCondition(
            field="status", operator=RuleConditionOperator.EQUALS, value="ACTIVE", case_sensitive=False
        )
        event_data = {"status": "active"}
        assert self.evaluator.evaluate_condition(condition, event_data) is True

    def test_missing_field(self):
        """Test condition with missing field"""
        condition = RuleCondition(field="nonexistent", operator=RuleConditionOperator.EQUALS, value="test")
        event_data = {"status": "active"}
        assert self.evaluator.evaluate_condition(condition, event_data) is False

    def test_nested_field_access(self):
        """Test nested field access with dot notation"""
        condition = RuleCondition(field="user.name", operator=RuleConditionOperator.EQUALS, value="John")
        event_data = {"user": {"name": "John", "age": 30}}
        assert self.evaluator.evaluate_condition(condition, event_data) is True


class TestRuleEvaluatorGroups:
    """Test RuleEvaluator group evaluation"""

    def setup_method(self):
        """Setup evaluator for each test"""
        self.evaluator = RuleEvaluator()

    def test_and_group_all_match(self):
        """Test AND group with all conditions matching"""
        cond1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        cond2 = RuleCondition(field="count", operator=RuleConditionOperator.GREATER_THAN, value=5)
        group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[cond1, cond2])

        event_data = {"status": "active", "count": 10}
        assert self.evaluator.evaluate_group(group, event_data) is True

    def test_and_group_one_fails(self):
        """Test AND group with one condition failing"""
        cond1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        cond2 = RuleCondition(field="count", operator=RuleConditionOperator.GREATER_THAN, value=5)
        group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[cond1, cond2])

        event_data = {"status": "active", "count": 3}
        assert self.evaluator.evaluate_group(group, event_data) is False

    def test_or_group_one_matches(self):
        """Test OR group with one condition matching"""
        cond1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        cond2 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="pending")
        group = RuleConditionGroup(operator=RuleLogicOperator.OR, conditions=[cond1, cond2])

        event_data = {"status": "active"}
        assert self.evaluator.evaluate_group(group, event_data) is True

    def test_or_group_none_match(self):
        """Test OR group with no conditions matching"""
        cond1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        cond2 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="pending")
        group = RuleConditionGroup(operator=RuleLogicOperator.OR, conditions=[cond1, cond2])

        event_data = {"status": "deleted"}
        assert self.evaluator.evaluate_group(group, event_data) is False

    def test_not_group(self):
        """Test NOT group"""
        cond1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="deleted")
        group = RuleConditionGroup(operator=RuleLogicOperator.NOT, conditions=[cond1])

        event_data = {"status": "active"}
        assert self.evaluator.evaluate_group(group, event_data) is True

        event_data = {"status": "deleted"}
        assert self.evaluator.evaluate_group(group, event_data) is False

    def test_nested_groups_and_or(self):
        """Test nested groups with AND and OR"""
        cond1 = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        cond2 = RuleCondition(field="priority", operator=RuleConditionOperator.EQUALS, value="high")
        cond3 = RuleCondition(field="priority", operator=RuleConditionOperator.EQUALS, value="critical")

        inner_group = RuleConditionGroup(operator=RuleLogicOperator.OR, conditions=[cond2, cond3])
        outer_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[cond1], groups=[inner_group])

        event_data = {"status": "active", "priority": "high"}
        assert self.evaluator.evaluate_group(outer_group, event_data) is True


class TestNotificationRulesEngine:
    """Test NotificationRulesEngine"""

    def setup_method(self):
        """Setup engine for each test"""
        self.engine = NotificationRulesEngine()

    def test_add_rule(self):
        """Test adding a rule"""
        rule = NotificationRule(id="rule1", name="Test Rule", description="Test")
        self.engine.add_rule(rule)
        assert len(self.engine.rules) == 1

    def test_remove_rule(self):
        """Test removing a rule"""
        rule = NotificationRule(id="rule1", name="Test Rule", description="Test")
        self.engine.add_rule(rule)
        result = self.engine.remove_rule("rule1")
        assert result is True
        assert len(self.engine.rules) == 0

    def test_remove_nonexistent_rule(self):
        """Test removing nonexistent rule"""
        result = self.engine.remove_rule("nonexistent")
        assert result is False

    def test_get_rule(self):
        """Test getting a rule"""
        rule = NotificationRule(id="rule1", name="Test Rule", description="Test")
        self.engine.add_rule(rule)
        retrieved = self.engine.get_rule("rule1")
        assert retrieved == rule

    def test_get_nonexistent_rule(self):
        """Test getting nonexistent rule"""
        result = self.engine.get_rule("nonexistent")
        assert result is None

    def test_list_rules(self):
        """Test listing all rules"""
        rule1 = NotificationRule(id="rule1", name="Rule 1", description="Test")
        rule2 = NotificationRule(id="rule2", name="Rule 2", description="Test", enabled=False)
        self.engine.add_rule(rule1)
        self.engine.add_rule(rule2)

        all_rules = self.engine.list_rules()
        assert len(all_rules) == 2

    def test_list_rules_enabled_only(self):
        """Test listing enabled rules only"""
        rule1 = NotificationRule(id="rule1", name="Rule 1", description="Test")
        rule2 = NotificationRule(id="rule2", name="Rule 2", description="Test", enabled=False)
        self.engine.add_rule(rule1)
        self.engine.add_rule(rule2)

        enabled_rules = self.engine.list_rules(enabled_only=True)
        assert len(enabled_rules) == 1

    def test_evaluate_event_simple(self):
        """Test evaluating event with simple rule"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test Rule", description="Test", conditions=condition_group, channels=[NotificationChannel.EMAIL]
        )
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="document.created", data={"status": "active"})
        results = self.engine.evaluate_event(event)

        assert len(results) == 1
        assert results[0].matched is True
        assert NotificationChannel.EMAIL in results[0].channels_used

    def test_evaluate_event_not_matched(self):
        """Test evaluating event that doesn't match"""
        condition = RuleCondition(field="status", operator=RuleConditionOperator.EQUALS, value="active")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(id="rule1", name="Test Rule", description="Test", conditions=condition_group)
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="document.created", data={"status": "deleted"})
        results = self.engine.evaluate_event(event)

        assert len(results) == 1
        assert results[0].matched is False
        assert "Conditions not met" in results[0].reason


class TestScheduling:
    """Test rule scheduling"""

    def setup_method(self):
        """Setup engine for each test"""
        self.engine = NotificationRulesEngine()

    def test_schedule_disabled(self):
        """Test rule with scheduling disabled"""
        schedule = RuleSchedule(enabled=False)
        rule = NotificationRule(id="rule1", name="Test", description="Test", schedule=schedule)
        self.engine.add_rule(rule)

        with patch("src.core.notifications.rules.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 1, 0, 0)  # 1 AM
            event = NotificationEvent(event_type="test", data={})
            results = self.engine.evaluate_event(event)

        # Should match since schedule is disabled
        assert results[0].matched is True

    def test_schedule_wrong_day(self):
        """Test rule outside scheduled days"""
        schedule = RuleSchedule(enabled=True, days=[ScheduleDay.MONDAY, ScheduleDay.FRIDAY])
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, schedule=schedule
        )
        self.engine.add_rule(rule)

        # Tuesday
        with patch("src.core.notifications.rules.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 2, 12, 0, 0)  # Jan 2, 2024 is Tuesday
            event = NotificationEvent(event_type="test", data={"test": "test"})
            results = self.engine.evaluate_event(event)

        assert results[0].matched is False
        assert "Outside schedule window" in results[0].reason

    def test_schedule_outside_time_range(self):
        """Test rule outside scheduled time range"""
        schedule = RuleSchedule(enabled=True, start_time=time(9, 0), end_time=time(17, 0))
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, schedule=schedule
        )
        self.engine.add_rule(rule)

        # 8 AM - before start time
        with patch("src.core.notifications.rules.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 8, 0, 0)
            event = NotificationEvent(event_type="test", data={"test": "test"})
            results = self.engine.evaluate_event(event)

        assert results[0].matched is False


class TestTargeting:
    """Test rule targeting"""

    def setup_method(self):
        """Setup engine for each test"""
        self.engine = NotificationRulesEngine()

    def test_no_targeting_matches_all(self):
        """Test rule with no targeting matches all"""
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(id="rule1", name="Test", description="Test", conditions=condition_group)
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="test", data={"test": "test"})
        results = self.engine.evaluate_event(event)

        assert results[0].matched is True

    def test_target_specific_users(self):
        """Test targeting specific users"""
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, target_users=["user1", "user2"]
        )
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="test", data={"test": "test"}, user_id="user1")
        results = self.engine.evaluate_event(event)
        assert results[0].matched is True

        event = NotificationEvent(event_type="test", data={"test": "test"}, user_id="user3")
        results = self.engine.evaluate_event(event)
        assert results[0].matched is False

    def test_target_groups(self):
        """Test targeting groups"""
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, target_groups=["admin"]
        )
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="test", data={"test": "test"}, user_groups=["admin", "users"])
        results = self.engine.evaluate_event(event)
        assert results[0].matched is True

    def test_target_roles(self):
        """Test targeting roles"""
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, target_roles=["manager"]
        )
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="test", data={"test": "test"}, user_roles=["manager"])
        results = self.engine.evaluate_event(event)
        assert results[0].matched is True


class TestThrottling:
    """Test rule throttling"""

    def setup_method(self):
        """Setup engine for each test"""
        self.engine = NotificationRulesEngine()

    def test_throttling_per_user_limit(self):
        """Test per-user throttling limit"""
        throttling = RuleThrottling(enabled=True, max_per_user=2, window_minutes=60)
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, throttling=throttling
        )
        self.engine.add_rule(rule)

        event = NotificationEvent(event_type="test", data={"test": "test"}, user_id="user1")

        # First two should pass
        result1 = self.engine.evaluate_event(event)
        assert result1[0].matched is True
        assert result1[0].throttled is False

        result2 = self.engine.evaluate_event(event)
        assert result2[0].matched is True
        assert result2[0].throttled is False

        # Third should be throttled
        result3 = self.engine.evaluate_event(event)
        assert result3[0].matched is True
        assert result3[0].throttled is True


class TestDeduplication:
    """Test rule deduplication"""

    def setup_method(self):
        """Setup engine for each test"""
        self.engine = NotificationRulesEngine()

    def test_deduplication_enabled(self):
        """Test deduplication with key fields"""
        dedup = RuleDeduplication(enabled=True, key_fields=["document_id"])
        condition = RuleCondition(field="test", operator=RuleConditionOperator.EQUALS, value="test")
        condition_group = RuleConditionGroup(operator=RuleLogicOperator.AND, conditions=[condition])

        rule = NotificationRule(
            id="rule1", name="Test", description="Test", conditions=condition_group, deduplication=dedup
        )
        self.engine.add_rule(rule)

        # First event should pass
        event1 = NotificationEvent(event_type="test", data={"test": "test", "document_id": "doc123"})
        result1 = self.engine.evaluate_event(event1)
        assert result1[0].matched is True
        assert result1[0].deduplicated is False

        # Second event with same document_id should be deduplicated
        event2 = NotificationEvent(event_type="test", data={"test": "test", "document_id": "doc123"})
        result2 = self.engine.evaluate_event(event2)
        assert result2[0].matched is True
        assert result2[0].deduplicated is True

        # Event with different document_id should pass
        event3 = NotificationEvent(event_type="test", data={"test": "test", "document_id": "doc456"})
        result3 = self.engine.evaluate_event(event3)
        assert result3[0].matched is True
        assert result3[0].deduplicated is False


class TestGlobalFunctions:
    """Test global functions"""

    def test_get_rules_engine_creates_instance(self):
        """Test get_rules_engine creates global instance"""
        # Reset global instance
        import src.core.notifications.rules as rules_module

        rules_module._rules_engine = None

        engine = get_rules_engine()
        assert engine is not None
        assert isinstance(engine, NotificationRulesEngine)

    def test_get_rules_engine_returns_singleton(self):
        """Test get_rules_engine returns same instance"""
        engine1 = get_rules_engine()
        engine2 = get_rules_engine()
        assert engine1 is engine2

    def test_create_simple_rule(self):
        """Test create_simple_rule helper"""
        rule = create_simple_rule(
            rule_id="rule1",
            name="Test Rule",
            event_type="document.created",
            channels=[NotificationChannel.EMAIL],
            target_users=["user1"],
        )

        assert rule.id == "rule1"
        assert rule.name == "Test Rule"
        assert len(rule.channels) == 1
        assert len(rule.target_users) == 1
        assert len(rule.conditions.conditions) == 1

    def test_create_simple_rule_no_users(self):
        """Test create_simple_rule without target users"""
        rule = create_simple_rule(
            rule_id="rule1",
            name="Test Rule",
            event_type="document.created",
            channels=[NotificationChannel.EMAIL],
        )

        assert rule.target_users == []
