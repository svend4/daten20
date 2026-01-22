"""
Tests for Notification Integrations

Tests Slack, Microsoft Teams, Discord, and Telegram integrations.
"""

import sys
from datetime import datetime
from unittest.mock import Mock, patch

# Mock requests before importing
mock_requests = Mock()
sys.modules["requests"] = mock_requests

from src.core.notifications.integrations import (
    IntegrationPlatform,
    MessagePriority,
    MessageAttachment,
    MessageAction,
    NotificationMessage,
    SlackIntegration,
    TeamsIntegration,
    DiscordIntegration,
    TelegramIntegration,
    NotificationIntegrationManager,
    get_integration_manager,
    configure_integrations,
)


class TestIntegrationPlatform:
    """Test IntegrationPlatform enum"""

    def test_slack_platform(self):
        """Test SLACK platform"""
        assert IntegrationPlatform.SLACK == "slack"
        assert IntegrationPlatform.SLACK.value == "slack"

    def test_teams_platform(self):
        """Test TEAMS platform"""
        assert IntegrationPlatform.TEAMS == "teams"
        assert IntegrationPlatform.TEAMS.value == "teams"

    def test_discord_platform(self):
        """Test DISCORD platform"""
        assert IntegrationPlatform.DISCORD == "discord"
        assert IntegrationPlatform.DISCORD.value == "discord"

    def test_telegram_platform(self):
        """Test TELEGRAM platform"""
        assert IntegrationPlatform.TELEGRAM == "telegram"
        assert IntegrationPlatform.TELEGRAM.value == "telegram"


class TestMessagePriority:
    """Test MessagePriority enum"""

    def test_low_priority(self):
        """Test LOW priority"""
        assert MessagePriority.LOW == "low"
        assert MessagePriority.LOW.value == "low"

    def test_normal_priority(self):
        """Test NORMAL priority"""
        assert MessagePriority.NORMAL == "normal"
        assert MessagePriority.NORMAL.value == "normal"

    def test_high_priority(self):
        """Test HIGH priority"""
        assert MessagePriority.HIGH == "high"
        assert MessagePriority.HIGH.value == "high"

    def test_urgent_priority(self):
        """Test URGENT priority"""
        assert MessagePriority.URGENT == "urgent"
        assert MessagePriority.URGENT.value == "urgent"


class TestMessageAttachment:
    """Test MessageAttachment dataclass"""

    def test_attachment_creation_minimal(self):
        """Test creating attachment with minimal fields"""
        attachment = MessageAttachment(url="https://example.com/image.png")
        assert attachment.url == "https://example.com/image.png"
        assert attachment.title is None
        assert attachment.description is None
        assert attachment.mime_type is None
        assert attachment.size is None

    def test_attachment_creation_full(self):
        """Test creating attachment with all fields"""
        attachment = MessageAttachment(
            url="https://example.com/image.png",
            title="Test Image",
            description="A test image",
            mime_type="image/png",
            size=1024,
        )
        assert attachment.url == "https://example.com/image.png"
        assert attachment.title == "Test Image"
        assert attachment.description == "A test image"
        assert attachment.mime_type == "image/png"
        assert attachment.size == 1024


class TestMessageAction:
    """Test MessageAction dataclass"""

    def test_action_creation_minimal(self):
        """Test creating action with minimal fields"""
        action = MessageAction(type="button", text="Click me")
        assert action.type == "button"
        assert action.text == "Click me"
        assert action.url is None
        assert action.value is None
        assert action.style is None

    def test_action_creation_full(self):
        """Test creating action with all fields"""
        action = MessageAction(
            type="button",
            text="Click me",
            url="https://example.com",
            value="action_value",
            style="primary",
        )
        assert action.type == "button"
        assert action.text == "Click me"
        assert action.url == "https://example.com"
        assert action.value == "action_value"
        assert action.style == "primary"


class TestNotificationMessage:
    """Test NotificationMessage dataclass"""

    def test_message_creation_minimal(self):
        """Test creating message with minimal fields"""
        message = NotificationMessage(
            title="Test Message",
            text="This is a test",
            platform=IntegrationPlatform.SLACK,
        )
        assert message.title == "Test Message"
        assert message.text == "This is a test"
        assert message.platform == IntegrationPlatform.SLACK
        assert message.channel is None
        assert message.priority == MessagePriority.NORMAL
        assert message.attachments == []
        assert message.actions == []
        assert message.metadata == {}

    def test_message_creation_full(self):
        """Test creating message with all fields"""
        attachment = MessageAttachment(url="https://example.com/image.png")
        action = MessageAction(type="button", text="Click")

        message = NotificationMessage(
            title="Test Message",
            text="This is a test",
            platform=IntegrationPlatform.SLACK,
            channel="#general",
            user="@user",
            priority=MessagePriority.HIGH,
            color="#FF0000",
            attachments=[attachment],
            actions=[action],
            metadata={"key": "value"},
        )

        assert message.channel == "#general"
        assert message.user == "@user"
        assert message.priority == MessagePriority.HIGH
        assert message.color == "#FF0000"
        assert len(message.attachments) == 1
        assert len(message.actions) == 1
        assert message.metadata["key"] == "value"


class TestSlackIntegration:
    """Test SlackIntegration class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.integration = SlackIntegration(
            webhook_url="https://hooks.slack.com/services/TEST",
            default_channel="#general",
        )

    def test_slack_initialization(self):
        """Test Slack integration initialization"""
        assert self.integration.webhook_url == "https://hooks.slack.com/services/TEST"
        assert self.integration.default_channel == "#general"

    def test_send_message_success(self):
        """Test sending message successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test message")

        assert result is True
        mock_requests.post.assert_called_once()

    def test_send_message_with_channel(self):
        """Test sending message to specific channel"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test", channel="#test")

        assert result is True
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["channel"] == "#test"

    def test_send_message_with_attachments(self):
        """Test sending message with attachments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        attachments = [{"text": "Attachment text", "color": "good"}]
        result = self.integration.send_message("Test", attachments=attachments)

        assert result is True
        call_args = mock_requests.post.call_args
        assert "attachments" in call_args[1]["json"]

    def test_send_message_with_blocks(self):
        """Test sending message with blocks"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        blocks = [{"type": "section", "text": {"type": "plain_text", "text": "Block"}}]
        result = self.integration.send_message("Test", blocks=blocks)

        assert result is True
        call_args = mock_requests.post.call_args
        assert "blocks" in call_args[1]["json"]

    def test_send_message_failure(self):
        """Test handling message send failure"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test")

        assert result is False

    def test_send_message_exception(self):
        """Test handling exception during send"""
        mock_requests.post = Mock(side_effect=Exception("Network error"))

        result = self.integration.send_message("Test")

        assert result is False

    def test_send_rich_message_basic(self):
        """Test sending rich message"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test Title",
            text="Test message",
            platform=IntegrationPlatform.SLACK,
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_actions(self):
        """Test rich message with actions"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        action = MessageAction(type="button", text="Click", url="https://example.com", style="primary")
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
            actions=[action],
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_attachments(self):
        """Test rich message with attachments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        attachment = MessageAttachment(
            url="https://example.com/image.png",
            title="Image",
            description="Test image",
        )
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
            attachments=[attachment],
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_color(self):
        """Test rich message with color"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
            color="#FF0000",
        )

        result = self.integration.send_rich_message(message)

        assert result is True


class TestTeamsIntegration:
    """Test TeamsIntegration class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.integration = TeamsIntegration(webhook_url="https://outlook.office.com/webhook/TEST")

    def test_teams_initialization(self):
        """Test Teams integration initialization"""
        assert self.integration.webhook_url == "https://outlook.office.com/webhook/TEST"

    def test_send_message_success(self):
        """Test sending message successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test Title", "Test message")

        assert result is True
        mock_requests.post.assert_called_once()

    def test_send_message_with_color(self):
        """Test sending message with theme color"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Title", "Message", color="#FF0000")

        assert result is True
        call_args = mock_requests.post.call_args
        assert "themeColor" in call_args[1]["json"]
        assert call_args[1]["json"]["themeColor"] == "FF0000"

    def test_send_message_with_sections(self):
        """Test sending message with sections"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        sections = [{"title": "Section 1", "text": "Section text"}]
        result = self.integration.send_message("Title", "Message", sections=sections)

        assert result is True

    def test_send_message_with_actions(self):
        """Test sending message with actions"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        actions = [{"@type": "OpenUri", "name": "View", "targets": [{"os": "default", "uri": "https://example.com"}]}]
        result = self.integration.send_message("Title", "Message", potential_actions=actions)

        assert result is True

    def test_send_message_failure(self):
        """Test handling send failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Title", "Message")

        assert result is False

    def test_send_rich_message_basic(self):
        """Test sending rich message"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test Title",
            text="Test message",
            platform=IntegrationPlatform.TEAMS,
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_metadata(self):
        """Test rich message with metadata as facts"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TEAMS,
            metadata={"Status": "Active", "Count": "5"},
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_attachments(self):
        """Test rich message with attachments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        attachment = MessageAttachment(url="https://example.com/image.png", title="Image")
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TEAMS,
            attachments=[attachment],
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_actions(self):
        """Test rich message with button actions"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        action = MessageAction(type="button", text="View", url="https://example.com")
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TEAMS,
            actions=[action],
        )

        result = self.integration.send_rich_message(message)

        assert result is True


class TestDiscordIntegration:
    """Test DiscordIntegration class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.integration = DiscordIntegration(webhook_url="https://discord.com/api/webhooks/TEST")

    def test_discord_initialization(self):
        """Test Discord integration initialization"""
        assert self.integration.webhook_url == "https://discord.com/api/webhooks/TEST"

    def test_send_message_success(self):
        """Test sending message successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test message")

        assert result is True

    def test_send_message_no_content_success(self):
        """Test Discord accepts 204 status"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test")

        assert result is True

    def test_send_message_with_username(self):
        """Test sending message with custom username"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test", username="Custom Bot")

        assert result is True
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["username"] == "Custom Bot"

    def test_send_message_with_avatar(self):
        """Test sending message with avatar URL"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test", avatar_url="https://example.com/avatar.png")

        assert result is True
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["avatar_url"] == "https://example.com/avatar.png"

    def test_send_message_with_embeds(self):
        """Test sending message with embeds"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        embeds = [{"title": "Embed", "description": "Description"}]
        result = self.integration.send_message("Test", embeds=embeds)

        assert result is True

    def test_send_message_with_tts(self):
        """Test sending message with TTS"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test", tts=True)

        assert result is True
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["tts"] is True

    def test_send_message_failure(self):
        """Test handling send failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test")

        assert result is False

    def test_send_rich_message_basic(self):
        """Test sending rich message"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test Title",
            text="Test message",
            platform=IntegrationPlatform.DISCORD,
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_color(self):
        """Test rich message with color (hex to int)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.DISCORD,
            color="#FF0000",
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_metadata(self):
        """Test rich message with metadata as fields"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.DISCORD,
            metadata={"Status": "Active", "Count": 5},
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_attachment(self):
        """Test rich message with attachment as image"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        attachment = MessageAttachment(url="https://example.com/image.png", title="Footer text")
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.DISCORD,
            attachments=[attachment],
        )

        result = self.integration.send_rich_message(message)

        assert result is True


class TestTelegramIntegration:
    """Test TelegramIntegration class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.integration = TelegramIntegration(bot_token="123456:ABC-DEF", default_chat_id="12345")

    def test_telegram_initialization(self):
        """Test Telegram integration initialization"""
        assert self.integration.bot_token == "123456:ABC-DEF"
        assert self.integration.default_chat_id == "12345"
        assert self.integration.api_url == "https://api.telegram.org/bot123456:ABC-DEF"

    def test_send_message_success(self):
        """Test sending message successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test message")

        assert result is True

    def test_send_message_to_specific_chat(self):
        """Test sending message to specific chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test", chat_id="67890")

        assert result is True
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["chat_id"] == "67890"

    def test_send_message_no_chat_id(self):
        """Test sending message without chat ID"""
        integration = TelegramIntegration(bot_token="123456:ABC", default_chat_id=None)

        result = integration.send_message("Test")

        assert result is False

    def test_send_message_with_parse_mode(self):
        """Test sending message with HTML parse mode"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test", parse_mode="HTML")

        assert result is True

    def test_send_message_with_options(self):
        """Test sending message with various options"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message(
            "Test",
            disable_web_page_preview=True,
            disable_notification=True,
        )

        assert result is True

    def test_send_message_with_reply_markup(self):
        """Test sending message with inline keyboard"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        markup = {"inline_keyboard": [[{"text": "Button", "url": "https://example.com"}]]}
        result = self.integration.send_message("Test", reply_markup=markup)

        assert result is True

    def test_send_message_api_error(self):
        """Test handling API error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": False}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test")

        assert result is False

    def test_send_message_failure(self):
        """Test handling send failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_message("Test")

        assert result is False

    def test_send_photo_success(self):
        """Test sending photo successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_photo("https://example.com/image.png")

        assert result is True

    def test_send_photo_with_caption(self):
        """Test sending photo with caption"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        result = self.integration.send_photo("https://example.com/image.png", caption="Test caption")

        assert result is True

    def test_send_photo_no_chat_id(self):
        """Test sending photo without chat ID"""
        integration = TelegramIntegration(bot_token="123456:ABC", default_chat_id=None)

        result = integration.send_photo("https://example.com/image.png")

        assert result is False

    def test_send_rich_message_basic(self):
        """Test sending rich message"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test Title",
            text="Test message",
            platform=IntegrationPlatform.TELEGRAM,
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_metadata(self):
        """Test rich message with metadata"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TELEGRAM,
            metadata={"Status": "Active", "Count": 5},
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_actions(self):
        """Test rich message with actions"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        action = MessageAction(type="button", text="Click", url="https://example.com")
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TELEGRAM,
            actions=[action],
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_low_priority(self):
        """Test rich message with low priority (silent)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TELEGRAM,
            priority=MessagePriority.LOW,
        )

        result = self.integration.send_rich_message(message)

        assert result is True

    def test_send_rich_message_with_attachments(self):
        """Test rich message with attachments sent as photos"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_requests.post = Mock(return_value=mock_response)

        attachment = MessageAttachment(url="https://example.com/image.png", title="Image")
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.TELEGRAM,
            attachments=[attachment],
        )

        result = self.integration.send_rich_message(message)

        assert result is True
        # Should be called twice: once for message, once for photo
        assert mock_requests.post.call_count == 2


class TestNotificationIntegrationManager:
    """Test NotificationIntegrationManager class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.manager = NotificationIntegrationManager()

    def test_manager_initialization(self):
        """Test manager initialization"""
        assert self.manager.integrations == {}

    def test_register_slack(self):
        """Test registering Slack integration"""
        self.manager.register_slack("https://hooks.slack.com/TEST", "#general")
        assert IntegrationPlatform.SLACK in self.manager.integrations
        assert isinstance(self.manager.integrations[IntegrationPlatform.SLACK], SlackIntegration)

    def test_register_teams(self):
        """Test registering Teams integration"""
        self.manager.register_teams("https://outlook.office.com/webhook/TEST")
        assert IntegrationPlatform.TEAMS in self.manager.integrations
        assert isinstance(self.manager.integrations[IntegrationPlatform.TEAMS], TeamsIntegration)

    def test_register_discord(self):
        """Test registering Discord integration"""
        self.manager.register_discord("https://discord.com/api/webhooks/TEST")
        assert IntegrationPlatform.DISCORD in self.manager.integrations
        assert isinstance(self.manager.integrations[IntegrationPlatform.DISCORD], DiscordIntegration)

    def test_register_telegram(self):
        """Test registering Telegram integration"""
        self.manager.register_telegram("123456:ABC", "12345")
        assert IntegrationPlatform.TELEGRAM in self.manager.integrations
        assert isinstance(self.manager.integrations[IntegrationPlatform.TELEGRAM], TelegramIntegration)

    def test_send_notification_success(self):
        """Test sending notification to registered platform"""
        self.manager.register_slack("https://hooks.slack.com/TEST")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
        )

        result = self.manager.send_notification(message)

        assert result is True

    def test_send_notification_unregistered_platform(self):
        """Test sending notification to unregistered platform"""
        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
        )

        result = self.manager.send_notification(message)

        assert result is False

    def test_broadcast_all_platforms(self):
        """Test broadcasting to all registered platforms"""
        self.manager.register_slack("https://hooks.slack.com/TEST")
        self.manager.register_discord("https://discord.com/api/webhooks/TEST")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,  # Will be overridden
        )

        results = self.manager.broadcast(message)

        assert len(results) == 2
        assert IntegrationPlatform.SLACK in results
        assert IntegrationPlatform.DISCORD in results
        assert results[IntegrationPlatform.SLACK] is True
        assert results[IntegrationPlatform.DISCORD] is True

    def test_broadcast_specific_platforms(self):
        """Test broadcasting to specific platforms"""
        self.manager.register_slack("https://hooks.slack.com/TEST")
        self.manager.register_teams("https://outlook.office.com/webhook/TEST")
        self.manager.register_discord("https://discord.com/api/webhooks/TEST")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
        )

        results = self.manager.broadcast(message, platforms=[IntegrationPlatform.SLACK, IntegrationPlatform.DISCORD])

        assert len(results) == 2
        assert IntegrationPlatform.SLACK in results
        assert IntegrationPlatform.DISCORD in results
        assert IntegrationPlatform.TEAMS not in results

    def test_broadcast_skips_unregistered(self):
        """Test broadcast skips unregistered platforms"""
        self.manager.register_slack("https://hooks.slack.com/TEST")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        message = NotificationMessage(
            title="Test",
            text="Message",
            platform=IntegrationPlatform.SLACK,
        )

        results = self.manager.broadcast(message, platforms=[IntegrationPlatform.SLACK, IntegrationPlatform.TEAMS])

        assert len(results) == 1
        assert IntegrationPlatform.SLACK in results
        assert IntegrationPlatform.TEAMS not in results


class TestGlobalFunctions:
    """Test global functions"""

    def setup_method(self):
        """Reset global state"""
        import src.core.notifications.integrations as integrations_module

        integrations_module._integration_manager = None

    def teardown_method(self):
        """Clean up global state"""
        import src.core.notifications.integrations as integrations_module

        integrations_module._integration_manager = None

    def test_get_integration_manager_creates_instance(self):
        """Test get_integration_manager creates instance"""
        manager = get_integration_manager()
        assert isinstance(manager, NotificationIntegrationManager)

    def test_get_integration_manager_returns_singleton(self):
        """Test get_integration_manager returns singleton"""
        manager1 = get_integration_manager()
        manager2 = get_integration_manager()
        assert manager1 is manager2

    def test_configure_integrations_slack(self):
        """Test configuring Slack integration"""
        configure_integrations(slack_webhook="https://hooks.slack.com/TEST")

        manager = get_integration_manager()
        assert IntegrationPlatform.SLACK in manager.integrations

    def test_configure_integrations_teams(self):
        """Test configuring Teams integration"""
        configure_integrations(teams_webhook="https://outlook.office.com/webhook/TEST")

        manager = get_integration_manager()
        assert IntegrationPlatform.TEAMS in manager.integrations

    def test_configure_integrations_discord(self):
        """Test configuring Discord integration"""
        configure_integrations(discord_webhook="https://discord.com/api/webhooks/TEST")

        manager = get_integration_manager()
        assert IntegrationPlatform.DISCORD in manager.integrations

    def test_configure_integrations_telegram(self):
        """Test configuring Telegram integration"""
        configure_integrations(telegram_token="123456:ABC", telegram_chat_id="12345")

        manager = get_integration_manager()
        assert IntegrationPlatform.TELEGRAM in manager.integrations

    def test_configure_integrations_multiple(self):
        """Test configuring multiple integrations"""
        configure_integrations(
            slack_webhook="https://hooks.slack.com/TEST",
            teams_webhook="https://outlook.office.com/webhook/TEST",
            discord_webhook="https://discord.com/api/webhooks/TEST",
            telegram_token="123456:ABC",
            telegram_chat_id="12345",
        )

        manager = get_integration_manager()
        assert len(manager.integrations) == 4
