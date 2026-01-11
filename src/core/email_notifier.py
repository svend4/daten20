"""Email notification system for Document Management System"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from datetime import datetime


class EmailNotifier:
    """Email notification system"""

    def __init__(self, smtp_host: str = 'localhost', smtp_port: int = 587,
                 smtp_user: str = '', smtp_password: str = '',
                 from_email: str = 'noreply@dms.local'):
        """
        Initialize email notifier

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: From email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.enabled = bool(smtp_user and smtp_password)

    def send_email(self, to_emails: List[str], subject: str, body: str,
                   html: bool = False, attachments: Optional[List[str]] = None) -> bool:
        """
        Send email

        Args:
            to_emails: List of recipient emails
            subject: Email subject
            body: Email body
            html: Whether body is HTML
            attachments: List of file paths to attach

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            print("Email notifications are disabled (SMTP not configured)")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Add body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition',
                                          f'attachment; filename={os.path.basename(filepath)}')
                            msg.attach(part)
                    except Exception as e:
                        print(f"Failed to attach {filepath}: {e}")

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"Email sent successfully to {', '.join(to_emails)}")
            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_service_created_notification(self, service_name: str, to_emails: List[str]) -> bool:
        """
        Send notification when new service is created

        Args:
            service_name: Name of created service
            to_emails: List of recipient emails

        Returns:
            True if sent successfully
        """
        subject = f"Новая услуга создана: {service_name}"

        body = f"""
Здравствуйте!

В системе управления документами была создана новая услуга:

Название: {service_name}
Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Вы можете просмотреть детали услуги в системе.

--
Document Management System
Автоматическое уведомление
        """

        return self.send_email(to_emails, subject, body)

    def send_document_generated_notification(self, service_name: str, format: str,
                                            to_emails: List[str], attachment: Optional[str] = None) -> bool:
        """
        Send notification when document is generated

        Args:
            service_name: Name of service
            format: Document format
            to_emails: List of recipient emails
            attachment: Path to generated document

        Returns:
            True if sent successfully
        """
        subject = f"Документ сгенерирован: {service_name}"

        body = f"""
Здравствуйте!

Документ успешно сгенерирован:

Услуга: {service_name}
Формат: {format.upper()}
Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}

{"Документ прикреплен к письму." if attachment else ""}

--
Document Management System
Автоматическое уведомление
        """

        attachments = [attachment] if attachment else None
        return self.send_email(to_emails, subject, body, attachments=attachments)

    def send_calculation_report(self, service_name: str, hourly_rate: float,
                               to_emails: List[str], report_file: Optional[str] = None) -> bool:
        """
        Send financial calculation report

        Args:
            service_name: Name of service
            hourly_rate: Calculated hourly rate
            to_emails: List of recipient emails
            report_file: Path to detailed report

        Returns:
            True if sent successfully
        """
        subject = f"Финансовый расчет: {service_name}"

        body = f"""
Здравствуйте!

Выполнен финансовый расчет для услуги:

Услуга: {service_name}
Итоговая ставка: {hourly_rate:.2f} €/час
Дата расчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}

{"Детальный отчет прикреплен к письму." if report_file else ""}

--
Document Management System
Автоматическое уведомление
        """

        attachments = [report_file] if report_file else None
        return self.send_email(to_emails, subject, body, attachments=attachments)

    def send_weekly_report(self, stats: dict, to_emails: List[str]) -> bool:
        """
        Send weekly statistics report

        Args:
            stats: Statistics dictionary
            to_emails: List of recipient emails

        Returns:
            True if sent successfully
        """
        subject = "Еженедельный отчет - Document Management System"

        body = f"""
Здравствуйте!

Еженедельный отчет по системе управления документами:

СТАТИСТИКА:
- Всего услуг: {stats.get('total_services', 0)}
- Средняя ставка: {stats.get('avg_brutto_rate', 0):.2f} €/час
- Регионов: {len(stats.get('by_region', {}))}
- Типов услуг: {len(stats.get('by_type', {}))}

УСЛУГИ ПО РЕГИОНАМ:
"""

        if 'by_region' in stats:
            for region, count in stats['by_region'].items():
                body += f"- {region or 'Не указан'}: {count}\n"

        body += f"""

Период: {datetime.now().strftime('%d.%m.%Y')}

--
Document Management System
Автоматическое уведомление
        """

        return self.send_email(to_emails, subject, body)

    def send_error_notification(self, error_message: str, to_emails: List[str]) -> bool:
        """
        Send error notification

        Args:
            error_message: Error message
            to_emails: List of recipient emails (admins)

        Returns:
            True if sent successfully
        """
        subject = "ОШИБКА в Document Management System"

        body = f"""
ВНИМАНИЕ!

В системе произошла ошибка:

{error_message}

Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

Требуется проверка системы.

--
Document Management System
Автоматическое уведомление
        """

        return self.send_email(to_emails, subject, body)


# Singleton instance
_notifier_instance = None


def get_notifier() -> EmailNotifier:
    """Get singleton notifier instance"""
    global _notifier_instance

    if _notifier_instance is None:
        # Load from environment or config
        import os

        smtp_host = os.getenv('SMTP_HOST', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        from_email = os.getenv('FROM_EMAIL', 'noreply@dms.local')

        _notifier_instance = EmailNotifier(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_email=from_email
        )

    return _notifier_instance
