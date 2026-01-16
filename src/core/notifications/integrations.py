"""
Notification Integrations

Provides integrations with Slack, Microsoft Teams, Discord, and Telegram
for sending rich notifications and interactive messages.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests


class IntegrationPlatform(str, Enum):
    """Notification platform types"""

    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class MessagePriority(str, Enum):
    """Message priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class MessageAttachment:
    """Message attachment (image, file, etc.)"""

    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None


@dataclass
class MessageAction:
    """Interactive message action (button, link)"""

    type: str  # button, link, menu
    text: str
    url: Optional[str] = None
    value: Optional[str] = None
    style: Optional[str] = None  # primary, danger, default


@dataclass
class NotificationMessage:
    """Generic notification message"""

    title: str
    text: str
    platform: IntegrationPlatform
    channel: Optional[str] = None
    user: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    color: Optional[str] = None
    attachments: List[MessageAttachment] = field(default_factory=list)
    actions: List[MessageAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SlackIntegration:
    """Slack webhook integration"""

    def __init__(self, webhook_url: str, default_channel: Optional[str] = None):
        self.webhook_url = webhook_url
        self.default_channel = default_channel

    def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        username: Optional[str] = "DMS Bot",
        icon_emoji: Optional[str] = ":robot_face:",
        attachments: Optional[List[Dict[str, Any]]] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Send message to Slack

        Args:
            text: Message text
            channel: Channel to send to (override default)
            username: Bot username
            icon_emoji: Bot icon emoji
            attachments: Slack attachments
            blocks: Slack blocks for rich formatting

        Returns:
            True if sent successfully
        """
        payload = {
            "text": text,
            "username": username,
            "icon_emoji": icon_emoji,
        }

        if channel or self.default_channel:
            payload["channel"] = channel or self.default_channel

        if attachments:
            payload["attachments"] = attachments

        if blocks:
            payload["blocks"] = blocks

        try:
            response = requests.post(
                self.webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def send_rich_message(self, message: NotificationMessage) -> bool:
        """
        Send rich formatted message to Slack

        Args:
            message: Notification message

        Returns:
            True if sent successfully
        """
        # Build Slack blocks
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": message.title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": message.text}},
        ]

        # Add actions if present
        if message.actions:
            action_elements = []
            for action in message.actions:
                if action.type == "button":
                    element = {
                        "type": "button",
                        "text": {"type": "plain_text", "text": action.text},
                        "value": action.value or action.text,
                    }
                    if action.url:
                        element["url"] = action.url
                    if action.style:
                        element["style"] = action.style
                    action_elements.append(element)

            if action_elements:
                blocks.append({"type": "actions", "elements": action_elements})

        # Add attachments as context
        if message.attachments:
            for attachment in message.attachments:
                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*{attachment.title or 'Attachment'}*"},
                        "accessory": {
                            "type": "image",
                            "image_url": attachment.url,
                            "alt_text": attachment.description or "attachment",
                        },
                    }
                )

        # Add color via attachment
        attachments = None
        if message.color:
            attachments = [{"color": message.color, "blocks": blocks}]
            blocks = None

        return self.send_message(text=message.text, channel=message.channel, blocks=blocks, attachments=attachments)


class TeamsIntegration:
    """Microsoft Teams webhook integration"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_message(
        self,
        title: str,
        text: str,
        color: Optional[str] = None,
        sections: Optional[List[Dict[str, Any]]] = None,
        potential_actions: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Send message to Microsoft Teams

        Args:
            title: Message title
            text: Message text
            color: Theme color (hex)
            sections: Message sections
            potential_actions: Action buttons

        Returns:
            True if sent successfully
        """
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "title": title,
            "text": text,
        }

        if color:
            payload["themeColor"] = color.lstrip("#")

        if sections:
            payload["sections"] = sections

        if potential_actions:
            payload["potentialAction"] = potential_actions

        try:
            response = requests.post(
                self.webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def send_rich_message(self, message: NotificationMessage) -> bool:
        """
        Send rich formatted message to Teams

        Args:
            message: Notification message

        Returns:
            True if sent successfully
        """
        sections = []

        # Add main content section
        main_section = {
            "activityTitle": message.title,
            "activityText": message.text,
        }

        if message.metadata:
            facts = []
            for key, value in message.metadata.items():
                facts.append({"name": key, "value": str(value)})
            main_section["facts"] = facts

        sections.append(main_section)

        # Add attachments
        if message.attachments:
            for attachment in message.attachments:
                sections.append({"title": attachment.title or "Attachment", "images": [{"image": attachment.url}]})

        # Add actions
        potential_actions = []
        if message.actions:
            for action in message.actions:
                if action.type == "button" and action.url:
                    potential_actions.append(
                        {"@type": "OpenUri", "name": action.text, "targets": [{"os": "default", "uri": action.url}]}
                    )

        return self.send_message(
            title=message.title,
            text=message.text,
            color=message.color,
            sections=sections,
            potential_actions=potential_actions if potential_actions else None,
        )


class DiscordIntegration:
    """Discord webhook integration"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_message(
        self,
        content: str,
        username: Optional[str] = "DMS Bot",
        avatar_url: Optional[str] = None,
        embeds: Optional[List[Dict[str, Any]]] = None,
        tts: bool = False,
    ) -> bool:
        """
        Send message to Discord

        Args:
            content: Message content
            username: Bot username
            avatar_url: Bot avatar URL
            embeds: Discord embeds
            tts: Use text-to-speech

        Returns:
            True if sent successfully
        """
        payload = {
            "content": content,
            "username": username,
            "tts": tts,
        }

        if avatar_url:
            payload["avatar_url"] = avatar_url

        if embeds:
            payload["embeds"] = embeds

        try:
            response = requests.post(
                self.webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10
            )
            return response.status_code in [200, 204]
        except Exception:
            return False

    def send_rich_message(self, message: NotificationMessage) -> bool:
        """
        Send rich formatted message to Discord

        Args:
            message: Notification message

        Returns:
            True if sent successfully
        """
        embed = {
            "title": message.title,
            "description": message.text,
            "timestamp": message.timestamp.isoformat(),
        }

        if message.color:
            # Convert hex color to integer
            color_int = int(message.color.lstrip("#"), 16)
            embed["color"] = color_int

        # Add fields from metadata
        if message.metadata:
            fields = []
            for key, value in message.metadata.items():
                fields.append({"name": key, "value": str(value), "inline": True})
            embed["fields"] = fields

        # Add first attachment as image
        if message.attachments:
            first_attachment = message.attachments[0]
            embed["image"] = {"url": first_attachment.url}
            if first_attachment.title:
                embed["footer"] = {"text": first_attachment.title}

        return self.send_message(content=f"**{message.title}**", embeds=[embed])


class TelegramIntegration:
    """Telegram bot integration"""

    def __init__(self, bot_token: str, default_chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send message to Telegram

        Args:
            text: Message text
            chat_id: Chat ID (override default)
            parse_mode: Parse mode (Markdown, HTML)
            disable_web_page_preview: Disable link previews
            disable_notification: Send silently
            reply_markup: Inline keyboard markup

        Returns:
            True if sent successfully
        """
        target_chat = chat_id or self.default_chat_id
        if not target_chat:
            return False

        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
        }

        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return response.status_code == 200 and response.json().get("ok", False)
        except Exception:
            return False

    def send_photo(self, photo_url: str, caption: Optional[str] = None, chat_id: Optional[str] = None) -> bool:
        """Send photo to Telegram"""
        target_chat = chat_id or self.default_chat_id
        if not target_chat:
            return False

        payload = {
            "chat_id": target_chat,
            "photo": photo_url,
        }

        if caption:
            payload["caption"] = caption

        try:
            response = requests.post(f"{self.api_url}/sendPhoto", json=payload, timeout=10)
            return response.status_code == 200 and response.json().get("ok", False)
        except Exception:
            return False

    def send_rich_message(self, message: NotificationMessage) -> bool:
        """
        Send rich formatted message to Telegram

        Args:
            message: Notification message

        Returns:
            True if sent successfully
        """
        # Build Markdown message
        text_parts = [f"*{message.title}*", "", message.text]

        # Add metadata
        if message.metadata:
            text_parts.append("")
            for key, value in message.metadata.items():
                text_parts.append(f"_{key}_: `{value}`")

        text = "\n".join(text_parts)

        # Build inline keyboard for actions
        reply_markup = None
        if message.actions:
            buttons = []
            for action in message.actions:
                if action.url:
                    buttons.append({"text": action.text, "url": action.url})
            if buttons:
                reply_markup = {"inline_keyboard": [buttons]}

        success = self.send_message(
            text=text,
            chat_id=message.channel or message.user,
            reply_markup=reply_markup,
            disable_notification=(message.priority == MessagePriority.LOW),
        )

        # Send attachments as separate photos
        if success and message.attachments:
            for attachment in message.attachments:
                self.send_photo(
                    photo_url=attachment.url,
                    caption=attachment.title or attachment.description,
                    chat_id=message.channel or message.user,
                )

        return success


class NotificationIntegrationManager:
    """Manager for notification integrations"""

    def __init__(self):
        self.integrations: Dict[IntegrationPlatform, Any] = {}

    def register_slack(self, webhook_url: str, default_channel: Optional[str] = None):
        """Register Slack integration"""
        self.integrations[IntegrationPlatform.SLACK] = SlackIntegration(webhook_url, default_channel)

    def register_teams(self, webhook_url: str):
        """Register Microsoft Teams integration"""
        self.integrations[IntegrationPlatform.TEAMS] = TeamsIntegration(webhook_url)

    def register_discord(self, webhook_url: str):
        """Register Discord integration"""
        self.integrations[IntegrationPlatform.DISCORD] = DiscordIntegration(webhook_url)

    def register_telegram(self, bot_token: str, default_chat_id: Optional[str] = None):
        """Register Telegram integration"""
        self.integrations[IntegrationPlatform.TELEGRAM] = TelegramIntegration(bot_token, default_chat_id)

    def send_notification(self, message: NotificationMessage) -> bool:
        """
        Send notification to specified platform

        Args:
            message: Notification message

        Returns:
            True if sent successfully
        """
        integration = self.integrations.get(message.platform)
        if not integration:
            return False

        return integration.send_rich_message(message)

    def broadcast(
        self, message: NotificationMessage, platforms: Optional[List[IntegrationPlatform]] = None
    ) -> Dict[IntegrationPlatform, bool]:
        """
        Broadcast message to multiple platforms

        Args:
            message: Notification message
            platforms: List of platforms (all if None)

        Returns:
            Dictionary mapping platforms to success status
        """
        target_platforms = platforms or list(self.integrations.keys())

        results = {}
        for platform in target_platforms:
            if platform in self.integrations:
                message_copy = NotificationMessage(
                    title=message.title,
                    text=message.text,
                    platform=platform,
                    channel=message.channel,
                    user=message.user,
                    priority=message.priority,
                    color=message.color,
                    attachments=message.attachments,
                    actions=message.actions,
                    metadata=message.metadata,
                    timestamp=message.timestamp,
                )
                results[platform] = self.send_notification(message_copy)

        return results


# Global integration manager instance
_integration_manager: Optional[NotificationIntegrationManager] = None


def get_integration_manager() -> NotificationIntegrationManager:
    """Get global integration manager instance"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = NotificationIntegrationManager()
    return _integration_manager


def configure_integrations(
    slack_webhook: Optional[str] = None,
    teams_webhook: Optional[str] = None,
    discord_webhook: Optional[str] = None,
    telegram_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
):
    """Configure notification integrations"""
    manager = get_integration_manager()

    if slack_webhook:
        manager.register_slack(slack_webhook)

    if teams_webhook:
        manager.register_teams(teams_webhook)

    if discord_webhook:
        manager.register_discord(discord_webhook)

    if telegram_token:
        manager.register_telegram(telegram_token, telegram_chat_id)
