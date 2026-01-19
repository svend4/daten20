"""
Advanced Email Digest System

Sends scheduled email digests with customizable content and templates.
"""

import json
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class DigestFrequency(str, Enum):
    """Digest frequency options"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class DigestFormat(str, Enum):
    """Digest format options"""

    HTML = "html"
    PLAIN = "plain"
    BOTH = "both"


@dataclass
class DigestContent:
    """Content for email digest"""

    title: str
    summary: str
    sections: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    highlights: List[str]
    footer: Optional[str] = None


@dataclass
class DigestSubscription:
    """User digest subscription"""

    user_id: int
    email: str
    frequency: DigestFrequency
    format: DigestFormat
    enabled: bool = True
    preferences: Dict[str, bool] = None
    last_sent: Optional[datetime] = None

    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                "include_statistics": True,
                "include_new_services": True,
                "include_updates": True,
                "include_analytics": True,
                "include_recommendations": True,
            }


class EmailDigestManager:
    """Manages email digest generation and sending"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "DMS Digest",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name

        self.subscriptions: Dict[int, DigestSubscription] = {}
        self.templates_dir = Path("templates/email_digests")
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def subscribe(self, subscription: DigestSubscription):
        """Subscribe user to digest"""
        self.subscriptions[subscription.user_id] = subscription

    def unsubscribe(self, user_id: int):
        """Unsubscribe user from digest"""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].enabled = False

    def update_preferences(self, user_id: int, preferences: Dict[str, bool]):
        """Update user digest preferences"""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].preferences.update(preferences)

    def generate_daily_digest(self, database) -> DigestContent:
        """Generate content for daily digest"""
        # Get today's data
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Query database for today's statistics
        cursor = database.conn.cursor()

        # New services created today
        cursor.execute("SELECT COUNT(*) FROM services WHERE DATE(created_at) = ?", (today.isoformat(),))
        new_services_count = cursor.fetchone()[0]

        # Services updated today
        cursor.execute(
            "SELECT COUNT(*) FROM services WHERE DATE(updated_at) = ? AND DATE(created_at) != ?",
            (today.isoformat(), today.isoformat()),
        )
        updated_services_count = cursor.fetchone()[0]

        # Total services
        cursor.execute("SELECT COUNT(*) FROM services")
        total_services = cursor.fetchone()[0]

        # Recent services
        cursor.execute(
            """
            SELECT service_name, region, brutto_rate, created_at
            FROM services
            WHERE DATE(created_at) = ?
            ORDER BY created_at DESC
            LIMIT 5
        """,
            (today.isoformat(),),
        )

        recent_services = []
        for row in cursor.fetchall():
            recent_services.append({"name": row[0], "region": row[1], "rate": row[2], "created_at": row[3]})

        # Build digest content
        sections = []

        if new_services_count > 0:
            sections.append(
                {
                    "title": "🆕 New Services",
                    "content": f"{new_services_count} new services were created today.",
                    "items": recent_services,
                }
            )

        if updated_services_count > 0:
            sections.append(
                {
                    "title": "📝 Updates",
                    "content": f"{updated_services_count} services were updated today.",
                    "items": [],
                }
            )

        statistics = {
            "total_services": total_services,
            "new_today": new_services_count,
            "updated_today": updated_services_count,
            "growth_rate": f"+{(new_services_count / max(total_services - new_services_count, 1) * 100):.1f}%",
        }

        highlights = []
        if new_services_count > 10:
            highlights.append(f"🎉 Great day! {new_services_count} new services added!")
        if total_services > 1000:
            highlights.append(f"🏆 Milestone reached: {total_services} total services!")

        return DigestContent(
            title=f"Daily Digest - {today.strftime('%B %d, %Y')}",
            summary=f"Here's your daily summary for {today.strftime('%A, %B %d')}.",
            sections=sections,
            statistics=statistics,
            highlights=highlights,
            footer="You're receiving this because you subscribed to daily digests.",
        )

    def generate_weekly_digest(self, database) -> DigestContent:
        """Generate content for weekly digest"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        cursor = database.conn.cursor()

        # Weekly statistics
        cursor.execute("SELECT COUNT(*) FROM services WHERE DATE(created_at) >= ?", (week_ago.isoformat(),))
        new_services_week = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM services WHERE DATE(updated_at) >= ? AND DATE(created_at) < ?",
            (week_ago.isoformat(), week_ago.isoformat()),
        )
        updated_services_week = cursor.fetchone()[0]

        # Top regions this week
        cursor.execute(
            """
            SELECT region, COUNT(*) as count
            FROM services
            WHERE DATE(created_at) >= ?
            GROUP BY region
            ORDER BY count DESC
            LIMIT 5
        """,
            (week_ago.isoformat(),),
        )

        top_regions = [{"region": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Average rate this week
        cursor.execute(
            """
            SELECT AVG(brutto_rate)
            FROM services
            WHERE DATE(created_at) >= ?
        """,
            (week_ago.isoformat(),),
        )

        avg_rate = cursor.fetchone()[0] or 0

        sections = [
            {
                "title": "📊 Weekly Overview",
                "content": f"This week saw {new_services_week} new services and {updated_services_week} updates.",
                "items": [],
            },
            {"title": "🏆 Top Regions", "content": "Most active regions this week:", "items": top_regions},
        ]

        statistics = {
            "new_this_week": new_services_week,
            "updated_this_week": updated_services_week,
            "avg_rate": f"{avg_rate:.2f}€",
            "active_regions": len(top_regions),
        }

        highlights = [f"📈 {new_services_week} services added this week", f"💰 Average rate: {avg_rate:.2f}€"]

        return DigestContent(
            title=f"Weekly Digest - Week of {week_ago.strftime('%B %d')}",
            summary=f"Your weekly summary for {week_ago.strftime('%B %d')} - {today.strftime('%B %d, %Y')}.",
            sections=sections,
            statistics=statistics,
            highlights=highlights,
            footer="You're receiving this because you subscribed to weekly digests.",
        )

    def generate_monthly_digest(self, database) -> DigestContent:
        """Generate content for monthly digest"""
        today = datetime.now().date()
        month_ago = today - timedelta(days=30)

        cursor = database.conn.cursor()

        # Monthly statistics
        cursor.execute("SELECT COUNT(*) FROM services WHERE DATE(created_at) >= ?", (month_ago.isoformat(),))
        new_services_month = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM services")
        total_services = cursor.fetchone()[0]

        # Monthly trends
        cursor.execute(
            """
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM services
            WHERE DATE(created_at) >= ?
            GROUP BY day
            ORDER BY day
        """,
            (month_ago.isoformat(),),
        )

        daily_counts = [row[1] for row in cursor.fetchall()]
        avg_daily = sum(daily_counts) / len(daily_counts) if daily_counts else 0

        sections = [
            {
                "title": "📅 Monthly Summary",
                "content": f"In the past month, {new_services_month} services were created.",
                "items": [],
            },
            {"title": "📈 Growth Trends", "content": f"Average of {avg_daily:.1f} services per day.", "items": []},
        ]

        statistics = {
            "new_this_month": new_services_month,
            "total_services": total_services,
            "avg_daily": f"{avg_daily:.1f}",
            "growth_rate": f"+{(new_services_month / max(total_services - new_services_month, 1) * 100):.1f}%",
        }

        highlights = [
            f"🎯 {new_services_month} services added this month",
            f"📊 {total_services} total services in system",
        ]

        return DigestContent(
            title=f"Monthly Digest - {month_ago.strftime('%B %Y')}",
            summary=f"Your monthly summary for {month_ago.strftime('%B %Y')}.",
            sections=sections,
            statistics=statistics,
            highlights=highlights,
            footer="You're receiving this because you subscribed to monthly digests.",
        )

    def render_html_template(self, content: DigestContent) -> str:
        """Render digest content as HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #0d6efd;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #0d6efd;
            margin: 0 0 10px 0;
            font-size: 24px;
        }}
        .summary {{
            color: #666;
            font-size: 14px;
            margin: 0;
        }}
        .highlights {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .highlights ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        .section-content {{
            color: #666;
            margin-bottom: 15px;
        }}
        .statistics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 30px 0;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: #0d6efd;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            font-size: 12px;
            color: #999;
        }}
        .item-list {{
            list-style: none;
            padding: 0;
        }}
        .item-list li {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .item-list li:last-child {{
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{content.title}</h1>
            <p class="summary">{content.summary}</p>
        </div>
"""

        # Highlights
        if content.highlights:
            html += """
        <div class="highlights">
            <ul>
"""
            for highlight in content.highlights:
                html += f"                <li>{highlight}</li>\n"
            html += """
            </ul>
        </div>
"""

        # Statistics
        if content.statistics:
            html += """
        <div class="statistics">
"""
            for label, value in content.statistics.items():
                formatted_label = label.replace("_", " ").title()
                html += f"""
            <div class="stat-card">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{formatted_label}</div>
            </div>
"""
            html += """
        </div>
"""

        # Sections
        for section in content.sections:
            html += f"""
        <div class="section">
            <div class="section-title">{section['title']}</div>
            <div class="section-content">{section['content']}</div>
"""
            if section.get("items"):
                html += """
            <ul class="item-list">
"""
                for item in section["items"]:
                    if isinstance(item, dict):
                        if "name" in item:
                            html += f"                <li><strong>{item['name']}</strong> - {item.get('region', 'N/A')} ({item.get('rate', 0):.2f}€)</li>\n"
                        elif "region" in item:
                            html += f"                <li><strong>{item['region']}</strong> - {item['count']} services</li>\n"
                    else:
                        html += f"                <li>{item}</li>\n"
                html += """
            </ul>
"""
            html += """
        </div>
"""

        # Footer
        if content.footer:
            html += f"""
        <div class="footer">
            {content.footer}
        </div>
"""

        html += """
    </div>
</body>
</html>
"""
        return html

    def render_plain_template(self, content: DigestContent) -> str:
        """Render digest content as plain text"""
        text = f"{content.title}\n"
        text += "=" * len(content.title) + "\n\n"
        text += f"{content.summary}\n\n"

        if content.highlights:
            text += "HIGHLIGHTS:\n"
            for highlight in content.highlights:
                text += f"  • {highlight}\n"
            text += "\n"

        if content.statistics:
            text += "STATISTICS:\n"
            for label, value in content.statistics.items():
                formatted_label = label.replace("_", " ").title()
                text += f"  {formatted_label}: {value}\n"
            text += "\n"

        for section in content.sections:
            text += f"{section['title']}\n"
            text += "-" * len(section["title"]) + "\n"
            text += f"{section['content']}\n"

            if section.get("items"):
                for item in section["items"]:
                    if isinstance(item, dict):
                        if "name" in item:
                            text += f"  • {item['name']} - {item.get('region', 'N/A')} ({item.get('rate', 0):.2f}€)\n"
                        elif "region" in item:
                            text += f"  • {item['region']} - {item['count']} services\n"
                    else:
                        text += f"  • {item}\n"
            text += "\n"

        if content.footer:
            text += f"\n---\n{content.footer}\n"

        return text

    def send_digest(self, subscription: DigestSubscription, content: DigestContent) -> bool:
        """Send digest email to subscriber"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = content.title
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = subscription.email

            # Plain text version
            plain_text = self.render_plain_template(content)
            part_plain = MIMEText(plain_text, "plain", "utf-8")
            msg.attach(part_plain)

            # HTML version (if requested)
            if subscription.format in [DigestFormat.HTML, DigestFormat.BOTH]:
                html_text = self.render_html_template(content)
                part_html = MIMEText(html_text, "html", "utf-8")
                msg.attach(part_html)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            # Update last sent timestamp
            subscription.last_sent = datetime.now()

            return True

        except Exception as e:
            print(f"Failed to send digest to {subscription.email}: {e}")
            return False

    def process_pending_digests(self, database):
        """Process all pending digest subscriptions"""
        now = datetime.now()
        sent_count = 0

        for subscription in self.subscriptions.values():
            if not subscription.enabled:
                continue

            # Check if digest is due
            should_send = False

            if subscription.frequency == DigestFrequency.DAILY:
                if subscription.last_sent is None or (now - subscription.last_sent).days >= 1:
                    content = self.generate_daily_digest(database)
                    should_send = True

            elif subscription.frequency == DigestFrequency.WEEKLY:
                if subscription.last_sent is None or (now - subscription.last_sent).days >= 7:
                    content = self.generate_weekly_digest(database)
                    should_send = True

            elif subscription.frequency == DigestFrequency.MONTHLY:
                if subscription.last_sent is None or (now - subscription.last_sent).days >= 30:
                    content = self.generate_monthly_digest(database)
                    should_send = True

            if should_send:
                if self.send_digest(subscription, content):
                    sent_count += 1

        return sent_count


# Global instance
_digest_manager: Optional[EmailDigestManager] = None


def get_digest_manager() -> EmailDigestManager:
    """Get global email digest manager instance"""
    global _digest_manager

    if _digest_manager is None:
        # Default SMTP configuration
        _digest_manager = EmailDigestManager(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="noreply@example.com",
            smtp_password="password",
            from_email="noreply@example.com",
            from_name="DMS Digest",
        )

    return _digest_manager


def configure_digest_manager(
    smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str, from_email: str, from_name: str = "DMS Digest"
):
    """Configure email digest manager"""
    global _digest_manager
    _digest_manager = EmailDigestManager(smtp_host, smtp_port, smtp_user, smtp_password, from_email, from_name)
