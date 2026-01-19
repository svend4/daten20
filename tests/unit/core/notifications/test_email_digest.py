"""
Tests for Advanced Email Digest System

Tests email digest generation, scheduling, and delivery.
"""

import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call

from src.core.notifications.email_digest import (
    DigestFrequency,
    DigestFormat,
    DigestContent,
    DigestSubscription,
    EmailDigestManager,
    get_digest_manager,
    configure_digest_manager,
)


class TestDigestFrequency:
    """Test DigestFrequency enum"""

    def test_daily_frequency(self):
        """Test DAILY frequency"""
        assert DigestFrequency.DAILY == "daily"
        assert DigestFrequency.DAILY.value == "daily"

    def test_weekly_frequency(self):
        """Test WEEKLY frequency"""
        assert DigestFrequency.WEEKLY == "weekly"
        assert DigestFrequency.WEEKLY.value == "weekly"

    def test_monthly_frequency(self):
        """Test MONTHLY frequency"""
        assert DigestFrequency.MONTHLY == "monthly"
        assert DigestFrequency.MONTHLY.value == "monthly"

    def test_custom_frequency(self):
        """Test CUSTOM frequency"""
        assert DigestFrequency.CUSTOM == "custom"
        assert DigestFrequency.CUSTOM.value == "custom"


class TestDigestFormat:
    """Test DigestFormat enum"""

    def test_html_format(self):
        """Test HTML format"""
        assert DigestFormat.HTML == "html"
        assert DigestFormat.HTML.value == "html"

    def test_plain_format(self):
        """Test PLAIN format"""
        assert DigestFormat.PLAIN == "plain"
        assert DigestFormat.PLAIN.value == "plain"

    def test_both_format(self):
        """Test BOTH format"""
        assert DigestFormat.BOTH == "both"
        assert DigestFormat.BOTH.value == "both"


class TestDigestContent:
    """Test DigestContent dataclass"""

    def test_content_creation_minimal(self):
        """Test creating content with minimal fields"""
        content = DigestContent(
            title="Daily Digest",
            summary="Today's summary",
            sections=[],
            statistics={},
            highlights=[],
        )
        assert content.title == "Daily Digest"
        assert content.summary == "Today's summary"
        assert content.sections == []
        assert content.footer is None

    def test_content_creation_full(self):
        """Test creating content with all fields"""
        sections = [{"title": "New Services", "content": "5 new services", "items": []}]
        statistics = {"total": 100, "new": 5}
        highlights = ["Great day!", "Milestone reached"]

        content = DigestContent(
            title="Daily Digest",
            summary="Today's summary",
            sections=sections,
            statistics=statistics,
            highlights=highlights,
            footer="Unsubscribe here",
        )

        assert content.title == "Daily Digest"
        assert len(content.sections) == 1
        assert content.statistics["total"] == 100
        assert len(content.highlights) == 2
        assert content.footer == "Unsubscribe here"


class TestDigestSubscription:
    """Test DigestSubscription dataclass"""

    def test_subscription_creation_minimal(self):
        """Test creating subscription with minimal fields"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )
        assert sub.user_id == 1
        assert sub.email == "user@example.com"
        assert sub.frequency == DigestFrequency.DAILY
        assert sub.format == DigestFormat.HTML
        assert sub.enabled is True
        assert sub.last_sent is None

    def test_subscription_default_preferences(self):
        """Test subscription has default preferences"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )
        assert sub.preferences is not None
        assert sub.preferences["include_statistics"] is True
        assert sub.preferences["include_new_services"] is True
        assert sub.preferences["include_updates"] is True
        assert sub.preferences["include_analytics"] is True
        assert sub.preferences["include_recommendations"] is True

    def test_subscription_custom_preferences(self):
        """Test subscription with custom preferences"""
        custom_prefs = {"include_statistics": False, "include_analytics": False}
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            preferences=custom_prefs,
        )
        assert sub.preferences["include_statistics"] is False
        assert sub.preferences["include_analytics"] is False

    def test_subscription_disabled(self):
        """Test disabled subscription"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            enabled=False,
        )
        assert sub.enabled is False

    def test_subscription_with_last_sent(self):
        """Test subscription with last_sent timestamp"""
        now = datetime.now()
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            last_sent=now,
        )
        assert sub.last_sent == now


class TestEmailDigestManager:
    """Test EmailDigestManager class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.manager = EmailDigestManager(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_password="password",
            from_email="noreply@example.com",
            from_name="Test Digest",
        )

    def test_manager_initialization(self):
        """Test manager initialization"""
        assert self.manager.smtp_host == "smtp.example.com"
        assert self.manager.smtp_port == 587
        assert self.manager.smtp_user == "user@example.com"
        assert self.manager.from_email == "noreply@example.com"
        assert self.manager.from_name == "Test Digest"
        assert self.manager.subscriptions == {}

    def test_subscribe_user(self):
        """Test subscribing a user"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )
        self.manager.subscribe(sub)
        assert 1 in self.manager.subscriptions
        assert self.manager.subscriptions[1] == sub

    def test_subscribe_multiple_users(self):
        """Test subscribing multiple users"""
        sub1 = DigestSubscription(
            user_id=1,
            email="user1@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )
        sub2 = DigestSubscription(
            user_id=2,
            email="user2@example.com",
            frequency=DigestFrequency.WEEKLY,
            format=DigestFormat.PLAIN,
        )
        self.manager.subscribe(sub1)
        self.manager.subscribe(sub2)
        assert len(self.manager.subscriptions) == 2

    def test_unsubscribe_user(self):
        """Test unsubscribing a user"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )
        self.manager.subscribe(sub)
        self.manager.unsubscribe(1)
        assert self.manager.subscriptions[1].enabled is False

    def test_unsubscribe_nonexistent_user(self):
        """Test unsubscribing nonexistent user"""
        # Should not raise error
        self.manager.unsubscribe(999)

    def test_update_preferences(self):
        """Test updating user preferences"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )
        self.manager.subscribe(sub)

        new_prefs = {"include_statistics": False, "include_analytics": False}
        self.manager.update_preferences(1, new_prefs)

        assert self.manager.subscriptions[1].preferences["include_statistics"] is False
        assert self.manager.subscriptions[1].preferences["include_analytics"] is False

    def test_update_preferences_nonexistent_user(self):
        """Test updating preferences for nonexistent user"""
        # Should not raise error
        self.manager.update_preferences(999, {"include_statistics": False})

    def test_generate_daily_digest(self):
        """Test generating daily digest"""
        # Mock database
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        # Mock cursor.fetchone() calls
        mock_cursor.fetchone.side_effect = [
            (5,),  # new services count
            (3,),  # updated services count
            (100,),  # total services
        ]

        # Mock cursor.fetchall() for recent services
        mock_cursor.fetchall.return_value = [
            ("Service 1", "North", 45.50, "2024-01-15 10:00:00"),
            ("Service 2", "South", 55.00, "2024-01-15 11:00:00"),
        ]

        content = self.manager.generate_daily_digest(mock_db)

        assert content.title.startswith("Daily Digest")
        assert content.summary is not None
        assert "total_services" in content.statistics
        assert content.statistics["total_services"] == 100
        assert content.statistics["new_today"] == 5

    def test_generate_daily_digest_no_new_services(self):
        """Test generating daily digest with no new services"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(0,), (0,), (100,)]
        mock_cursor.fetchall.return_value = []

        content = self.manager.generate_daily_digest(mock_db)

        assert content.statistics["new_today"] == 0
        assert len(content.sections) == 0

    def test_generate_daily_digest_with_highlights(self):
        """Test generating daily digest with highlights"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(15,), (0,), (1001,)]
        mock_cursor.fetchall.return_value = []

        content = self.manager.generate_daily_digest(mock_db)

        assert len(content.highlights) >= 2
        assert any("15 new services" in h for h in content.highlights)
        assert any("1001 total services" in h for h in content.highlights)

    def test_generate_weekly_digest(self):
        """Test generating weekly digest"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [
            (35,),  # new services week
            (10,),  # updated services week
            (42.50,),  # average rate
        ]

        mock_cursor.fetchall.return_value = [
            ("North", 15),
            ("South", 10),
            ("East", 8),
        ]

        content = self.manager.generate_weekly_digest(mock_db)

        assert content.title.startswith("Weekly Digest")
        assert "new_this_week" in content.statistics
        assert content.statistics["new_this_week"] == 35
        assert "42.50€" in content.statistics["avg_rate"]

    def test_generate_weekly_digest_with_top_regions(self):
        """Test weekly digest includes top regions"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(20,), (5,), (45.00,)]
        mock_cursor.fetchall.return_value = [("North", 12), ("South", 8)]

        content = self.manager.generate_weekly_digest(mock_db)

        # Check for top regions section
        assert any(s["title"] == "🏆 Top Regions" for s in content.sections)

    def test_generate_monthly_digest(self):
        """Test generating monthly digest"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [
            (120,),  # new services month
            (500,),  # total services
        ]

        # Daily counts for trend calculation
        mock_cursor.fetchall.return_value = [
            ("2024-01-01", 4),
            ("2024-01-02", 5),
            ("2024-01-03", 3),
        ]

        content = self.manager.generate_monthly_digest(mock_db)

        assert content.title.startswith("Monthly Digest")
        assert "new_this_month" in content.statistics
        assert content.statistics["new_this_month"] == 120
        assert content.statistics["total_services"] == 500

    def test_generate_monthly_digest_empty_trends(self):
        """Test monthly digest with no daily data"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(0,), (100,)]
        mock_cursor.fetchall.return_value = []

        content = self.manager.generate_monthly_digest(mock_db)

        assert content.statistics["avg_daily"] == "0.0"

    def test_render_html_template(self):
        """Test rendering HTML template"""
        content = DigestContent(
            title="Test Digest",
            summary="Test summary",
            sections=[{"title": "Section 1", "content": "Content here", "items": []}],
            statistics={"total": 100, "new": 5},
            highlights=["Highlight 1", "Highlight 2"],
            footer="Footer text",
        )

        html = self.manager.render_html_template(content)

        assert "Test Digest" in html
        assert "Test summary" in html
        assert "Section 1" in html
        assert "Content here" in html
        assert "Highlight 1" in html
        assert "Footer text" in html
        assert "<html>" in html
        assert "</html>" in html

    def test_render_html_template_with_statistics(self):
        """Test HTML template includes statistics"""
        content = DigestContent(
            title="Test", summary="Test", sections=[], statistics={"total_services": 100, "new_today": 5}, highlights=[]
        )

        html = self.manager.render_html_template(content)

        assert "100" in html
        assert "5" in html
        assert "Total Services" in html

    def test_render_html_template_with_service_items(self):
        """Test HTML template with service items"""
        content = DigestContent(
            title="Test",
            summary="Test",
            sections=[
                {
                    "title": "New Services",
                    "content": "Services added",
                    "items": [{"name": "Service 1", "region": "North", "rate": 45.50}],
                }
            ],
            statistics={},
            highlights=[],
        )

        html = self.manager.render_html_template(content)

        assert "Service 1" in html
        assert "North" in html
        assert "45.50" in html

    def test_render_html_template_with_region_items(self):
        """Test HTML template with region items"""
        content = DigestContent(
            title="Test",
            summary="Test",
            sections=[{"title": "Top Regions", "content": "Active regions", "items": [{"region": "North", "count": 15}]}],
            statistics={},
            highlights=[],
        )

        html = self.manager.render_html_template(content)

        assert "North" in html
        assert "15" in html

    def test_render_plain_template(self):
        """Test rendering plain text template"""
        content = DigestContent(
            title="Test Digest",
            summary="Test summary",
            sections=[{"title": "Section 1", "content": "Content here", "items": []}],
            statistics={"total": 100},
            highlights=["Highlight 1"],
            footer="Footer text",
        )

        text = self.manager.render_plain_template(content)

        assert "Test Digest" in text
        assert "Test summary" in text
        assert "Section 1" in text
        assert "Highlight 1" in text
        assert "Footer text" in text
        assert "===" in text  # Title underline

    def test_render_plain_template_with_items(self):
        """Test plain text template with items"""
        content = DigestContent(
            title="Test",
            summary="Test",
            sections=[
                {
                    "title": "Services",
                    "content": "List",
                    "items": [{"name": "Service 1", "region": "North", "rate": 45.50}],
                }
            ],
            statistics={},
            highlights=[],
        )

        text = self.manager.render_plain_template(content)

        assert "Service 1" in text
        assert "North" in text
        assert "45.50" in text

    @patch("src.core.notifications.email_digest.smtplib.SMTP")
    def test_send_digest_html_format(self, mock_smtp_class):
        """Test sending digest in HTML format"""
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )

        content = DigestContent(
            title="Test Digest", summary="Test", sections=[], statistics={}, highlights=[]
        )

        result = self.manager.send_digest(sub, content)

        assert result is True
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@example.com", "password")
        mock_smtp.send_message.assert_called_once()
        assert sub.last_sent is not None

    @patch("src.core.notifications.email_digest.smtplib.SMTP")
    def test_send_digest_plain_format(self, mock_smtp_class):
        """Test sending digest in plain text format"""
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.PLAIN,
        )

        content = DigestContent(
            title="Test Digest", summary="Test", sections=[], statistics={}, highlights=[]
        )

        result = self.manager.send_digest(sub, content)

        assert result is True
        mock_smtp.send_message.assert_called_once()

    @patch("src.core.notifications.email_digest.smtplib.SMTP")
    def test_send_digest_both_format(self, mock_smtp_class):
        """Test sending digest in both formats"""
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.BOTH,
        )

        content = DigestContent(
            title="Test Digest", summary="Test", sections=[], statistics={}, highlights=[]
        )

        result = self.manager.send_digest(sub, content)

        assert result is True

    @patch("src.core.notifications.email_digest.smtplib.SMTP")
    def test_send_digest_failure(self, mock_smtp_class):
        """Test handling digest send failure"""
        mock_smtp_class.return_value.__enter__.side_effect = Exception("SMTP error")

        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
        )

        content = DigestContent(
            title="Test Digest", summary="Test", sections=[], statistics={}, highlights=[]
        )

        result = self.manager.send_digest(sub, content)

        assert result is False

    @patch("src.core.notifications.email_digest.datetime")
    def test_process_pending_digests_daily(self, mock_datetime):
        """Test processing pending daily digests"""
        # Mock datetime.now()
        mock_now = datetime(2024, 1, 15, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Subscribe user
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            last_sent=None,  # Never sent
        )
        self.manager.subscribe(sub)

        # Mock database
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(0,), (0,), (100,)]
        mock_cursor.fetchall.return_value = []

        # Mock send_digest
        self.manager.send_digest = Mock(return_value=True)

        count = self.manager.process_pending_digests(mock_db)

        assert count == 1
        self.manager.send_digest.assert_called_once()

    @patch("src.core.notifications.email_digest.datetime")
    def test_process_pending_digests_daily_already_sent_today(self, mock_datetime):
        """Test not sending daily digest if already sent today"""
        mock_now = datetime(2024, 1, 15, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # User already received digest today
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            last_sent=datetime(2024, 1, 15, 8, 0, 0),  # Earlier today
        )
        self.manager.subscribe(sub)

        mock_db = Mock()
        self.manager.send_digest = Mock(return_value=True)

        count = self.manager.process_pending_digests(mock_db)

        assert count == 0
        self.manager.send_digest.assert_not_called()

    @patch("src.core.notifications.email_digest.datetime")
    def test_process_pending_digests_weekly(self, mock_datetime):
        """Test processing pending weekly digests"""
        mock_now = datetime(2024, 1, 15, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.WEEKLY,
            format=DigestFormat.HTML,
            last_sent=datetime(2024, 1, 1, 10, 0, 0),  # 14 days ago
        )
        self.manager.subscribe(sub)

        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(10,), (5,), (45.0,)]
        mock_cursor.fetchall.return_value = []

        self.manager.send_digest = Mock(return_value=True)

        count = self.manager.process_pending_digests(mock_db)

        assert count == 1

    @patch("src.core.notifications.email_digest.datetime")
    def test_process_pending_digests_monthly(self, mock_datetime):
        """Test processing pending monthly digests"""
        mock_now = datetime(2024, 2, 1, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.MONTHLY,
            format=DigestFormat.HTML,
            last_sent=datetime(2024, 1, 1, 10, 0, 0),  # 31 days ago
        )
        self.manager.subscribe(sub)

        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(50,), (200,)]
        mock_cursor.fetchall.return_value = [("2024-01-15", 2)]

        self.manager.send_digest = Mock(return_value=True)

        count = self.manager.process_pending_digests(mock_db)

        assert count == 1

    def test_process_pending_digests_disabled_subscription(self):
        """Test disabled subscriptions are skipped"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            enabled=False,
        )
        self.manager.subscribe(sub)

        mock_db = Mock()
        self.manager.send_digest = Mock(return_value=True)

        count = self.manager.process_pending_digests(mock_db)

        assert count == 0
        self.manager.send_digest.assert_not_called()

    def test_process_pending_digests_send_failure(self):
        """Test handling send failures during processing"""
        sub = DigestSubscription(
            user_id=1,
            email="user@example.com",
            frequency=DigestFrequency.DAILY,
            format=DigestFormat.HTML,
            last_sent=None,
        )
        self.manager.subscribe(sub)

        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(0,), (0,), (100,)]
        mock_cursor.fetchall.return_value = []

        # Simulate send failure
        self.manager.send_digest = Mock(return_value=False)

        count = self.manager.process_pending_digests(mock_db)

        assert count == 0


class TestGlobalFunctions:
    """Test global functions"""

    def setup_method(self):
        """Reset global state"""
        import src.core.notifications.email_digest as email_digest_module

        email_digest_module._digest_manager = None

    def teardown_method(self):
        """Clean up global state"""
        import src.core.notifications.email_digest as email_digest_module

        email_digest_module._digest_manager = None

    def test_get_digest_manager_creates_instance(self):
        """Test get_digest_manager creates default instance"""
        manager = get_digest_manager()
        assert isinstance(manager, EmailDigestManager)
        assert manager.smtp_host == "smtp.gmail.com"
        assert manager.smtp_port == 587

    def test_get_digest_manager_returns_singleton(self):
        """Test get_digest_manager returns singleton"""
        manager1 = get_digest_manager()
        manager2 = get_digest_manager()
        assert manager1 is manager2

    def test_configure_digest_manager(self):
        """Test configuring digest manager"""
        configure_digest_manager(
            smtp_host="smtp.custom.com",
            smtp_port=465,
            smtp_user="custom@example.com",
            smtp_password="custompass",
            from_email="custom@example.com",
            from_name="Custom Digest",
        )

        manager = get_digest_manager()
        assert manager.smtp_host == "smtp.custom.com"
        assert manager.smtp_port == 465
        assert manager.from_name == "Custom Digest"

    def test_configure_digest_manager_replaces_instance(self):
        """Test configuring replaces existing instance"""
        manager1 = get_digest_manager()

        configure_digest_manager(
            smtp_host="smtp.new.com",
            smtp_port=587,
            smtp_user="new@example.com",
            smtp_password="newpass",
            from_email="new@example.com",
        )

        manager2 = get_digest_manager()
        assert manager1 is not manager2
        assert manager2.smtp_host == "smtp.new.com"
