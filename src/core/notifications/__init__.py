"""
Notifications Module

Provides comprehensive notification system including email, SMS, push notifications,
third-party integrations (Slack, Teams, Discord, Telegram), and rules engine.
"""

# Email Digests
from src.core.notifications.email_digest import (
    DigestContent,
    DigestFormat,
    DigestFrequency,
    DigestSubscription,
    EmailDigestManager,
    configure_digest_manager,
    get_digest_manager,
)

# Third-party Integrations
from src.core.notifications.integrations import (
    DiscordIntegration,
    IntegrationPlatform,
    MessageAction,
    MessageAttachment,
    MessagePriority,
    NotificationIntegrationManager,
    NotificationMessage,
    SlackIntegration,
    TeamsIntegration,
    TelegramIntegration,
    configure_integrations,
    get_integration_manager,
)

# Push Notifications
from src.core.notifications.push import NotificationAction as PushAction
from src.core.notifications.push import (
    NotificationPayload,
    NotificationUrgency,
    PushSubscription,
    WebPushManager,
    configure_push_manager,
    get_push_manager,
)

# Rules Engine
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

# SMS Notifications
from src.core.notifications.sms import (
    SMSManager,
    SMSMessage,
    SMSStatus,
    SMSTemplate,
    configure_sms_manager,
    get_sms_manager,
)

__all__ = [
    # Email Digests
    "DigestFrequency",
    "DigestFormat",
    "DigestContent",
    "DigestSubscription",
    "EmailDigestManager",
    "get_digest_manager",
    "configure_digest_manager",
    # SMS
    "SMSStatus",
    "SMSMessage",
    "SMSTemplate",
    "SMSManager",
    "get_sms_manager",
    "configure_sms_manager",
    # Push
    "NotificationUrgency",
    "PushAction",
    "PushSubscription",
    "NotificationPayload",
    "WebPushManager",
    "get_push_manager",
    "configure_push_manager",
    # Integrations
    "IntegrationPlatform",
    "MessagePriority",
    "MessageAttachment",
    "MessageAction",
    "NotificationMessage",
    "SlackIntegration",
    "TeamsIntegration",
    "DiscordIntegration",
    "TelegramIntegration",
    "NotificationIntegrationManager",
    "get_integration_manager",
    "configure_integrations",
    # Rules Engine
    "RuleConditionOperator",
    "RuleLogicOperator",
    "NotificationChannel",
    "RulePriority",
    "ScheduleDay",
    "RuleCondition",
    "RuleConditionGroup",
    "RuleSchedule",
    "RuleThrottling",
    "RuleDeduplication",
    "NotificationRule",
    "NotificationEvent",
    "NotificationRuleExecution",
    "RuleEvaluator",
    "NotificationRulesEngine",
    "get_rules_engine",
    "create_simple_rule",
]
