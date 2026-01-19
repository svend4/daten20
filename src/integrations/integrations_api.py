"""
Unified Integrations API - v3.7

Single interface for all enterprise integration operations.
Provides simplified API for cloud storage, productivity, communication, e-signature, calendar.
"""

from typing import Dict, List, Optional, Any, BinaryIO
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

from .cloud_storage import get_storage_manager, StorageProvider
from .productivity import get_productivity_client, ProductivitySuite
from .communication import get_communication_client, Platform
from .esignature import get_esignature_client, SignatureProvider
from .calendar import get_calendar_client, CalendarProvider
from .file_conversion import get_file_converter, FileFormat

logger = logging.getLogger(__name__)


class IntegrationOperation(Enum):
    """Integration operation types"""
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    SEND_MESSAGE = "send_message"
    CREATE_DOCUMENT = "create_document"
    REQUEST_SIGNATURE = "request_signature"
    CREATE_EVENT = "create_event"
    CONVERT_FILE = "convert_file"
    SHARE_FILE = "share_file"
    SEND_EMAIL = "send_email"


@dataclass
class IntegrationsConfig:
    """Configuration for Integrations API"""
    default_storage: StorageProvider = StorageProvider.GOOGLE_DRIVE
    default_productivity: ProductivitySuite = ProductivitySuite.GOOGLE_WORKSPACE
    default_communication: Platform = Platform.SLACK
    default_signature: SignatureProvider = SignatureProvider.DOCUSIGN
    default_calendar: CalendarProvider = CalendarProvider.GOOGLE_CALENDAR
    enable_auto_retry: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30


class IntegrationsAPI:
    """
    Unified Integrations API - Single interface for all integration operations

    This class provides a simplified, unified interface to all integration services:
    - Cloud storage (Google Drive, Dropbox, OneDrive, S3, Azure Blob)
    - Productivity suites (Google Workspace, Microsoft 365)
    - Communication platforms (Slack, Microsoft Teams, Discord)
    - E-signature services (DocuSign, Adobe Sign, HelloSign)
    - Calendar & scheduling (Google Calendar, Outlook)
    - File conversion (documents, images, spreadsheets)

    Example:
        api = get_integrations_api()

        # Upload to cloud storage
        file_id = api.upload_file("document.pdf", storage="google_drive")

        # Send Slack message
        api.send_message("Hello team!", channel="#general", platform="slack")

        # Request e-signature
        request_id = api.request_signature("contract.pdf", signers=["user@example.com"])
    """

    def __init__(
        self,
        config: Optional[IntegrationsConfig] = None,
        enable_storage: bool = True,
        enable_productivity: bool = True,
        enable_communication: bool = True,
        enable_esignature: bool = True,
        enable_calendar: bool = True,
        enable_conversion: bool = True
    ):
        """Initialize Integrations API with services"""
        self.config = config or IntegrationsConfig()

        # Initialize services
        self.storage_manager = get_storage_manager() if enable_storage else None
        self.productivity_client = get_productivity_client() if enable_productivity else None
        self.communication_client = get_communication_client() if enable_communication else None
        self.esignature_client = get_esignature_client() if enable_esignature else None
        self.calendar_client = get_calendar_client() if enable_calendar else None
        self.file_converter = get_file_converter() if enable_conversion else None

        # Statistics
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in IntegrationOperation},
            "files_uploaded": 0,
            "messages_sent": 0,
            "signatures_requested": 0,
            "events_created": 0,
            "files_converted": 0,
        }

        logger.info("Integrations API initialized with all services")

    # ==================== Cloud Storage ====================

    def upload_file(
        self,
        file_path: str,
        folder: Optional[str] = None,
        storage: Optional[StorageProvider] = None,
        **kwargs
    ) -> str:
        """
        Upload file to cloud storage

        Args:
            file_path: Path to file to upload
            folder: Destination folder
            storage: Storage provider (default: from config)

        Returns:
            File ID in cloud storage
        """
        if not self.storage_manager:
            raise ValueError("Storage manager not enabled")

        self._track_operation(IntegrationOperation.UPLOAD_FILE)

        provider = storage or self.config.default_storage
        file_id = self.storage_manager.upload(
            provider=provider,
            file_path=file_path,
            folder=folder,
            **kwargs
        )

        self.stats["files_uploaded"] += 1
        logger.info(f"Uploaded file to {provider.value}: {file_id}")

        return file_id

    def download_file(
        self,
        file_id: str,
        destination: str,
        storage: Optional[StorageProvider] = None,
        **kwargs
    ) -> str:
        """Download file from cloud storage"""
        if not self.storage_manager:
            raise ValueError("Storage manager not enabled")

        self._track_operation(IntegrationOperation.DOWNLOAD_FILE)

        provider = storage or self.config.default_storage
        local_path = self.storage_manager.download(
            provider=provider,
            file_id=file_id,
            destination=destination,
            **kwargs
        )

        return local_path

    def list_files(
        self,
        folder: Optional[str] = None,
        storage: Optional[StorageProvider] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List files in cloud storage"""
        if not self.storage_manager:
            raise ValueError("Storage manager not enabled")

        provider = storage or self.config.default_storage
        files = self.storage_manager.list_files(
            provider=provider,
            folder=folder,
            **kwargs
        )

        return [
            {
                "file_id": f.file_id,
                "name": f.name,
                "size": f.size,
                "modified": f.modified.isoformat(),
                "mime_type": f.mime_type
            }
            for f in files
        ]

    def share_file(
        self,
        file_id: str,
        email: str,
        permission: str = "reader",
        storage: Optional[StorageProvider] = None,
        **kwargs
    ) -> str:
        """
        Share file with user

        Args:
            file_id: File ID
            email: User email
            permission: Permission level (reader, writer, commenter)
            storage: Storage provider

        Returns:
            Share link
        """
        if not self.storage_manager:
            raise ValueError("Storage manager not enabled")

        self._track_operation(IntegrationOperation.SHARE_FILE)

        provider = storage or self.config.default_storage
        share_link = self.storage_manager.share(
            provider=provider,
            file_id=file_id,
            email=email,
            permission=permission,
            **kwargs
        )

        return share_link

    def create_folder(
        self,
        folder_name: str,
        parent_folder: Optional[str] = None,
        storage: Optional[StorageProvider] = None,
        **kwargs
    ) -> str:
        """Create folder in cloud storage"""
        if not self.storage_manager:
            raise ValueError("Storage manager not enabled")

        provider = storage or self.config.default_storage
        folder_id = self.storage_manager.create_folder(
            provider=provider,
            folder_name=folder_name,
            parent_folder=parent_folder,
            **kwargs
        )

        return folder_id

    # ==================== Productivity Suite ====================

    def create_document(
        self,
        title: str,
        content: Optional[str] = None,
        suite: Optional[ProductivitySuite] = None,
        **kwargs
    ) -> str:
        """
        Create document in productivity suite

        Args:
            title: Document title
            content: Initial content
            suite: Productivity suite (Google Workspace, Microsoft 365)

        Returns:
            Document ID
        """
        if not self.productivity_client:
            raise ValueError("Productivity client not enabled")

        self._track_operation(IntegrationOperation.CREATE_DOCUMENT)

        suite = suite or self.config.default_productivity
        doc_id = self.productivity_client.create_document(
            suite=suite,
            title=title,
            content=content,
            **kwargs
        )

        logger.info(f"Created document in {suite.value}: {doc_id}")
        return doc_id

    def create_spreadsheet(
        self,
        title: str,
        data: Optional[List[List[Any]]] = None,
        suite: Optional[ProductivitySuite] = None,
        **kwargs
    ) -> str:
        """Create spreadsheet in productivity suite"""
        if not self.productivity_client:
            raise ValueError("Productivity client not enabled")

        suite = suite or self.config.default_productivity
        sheet_id = self.productivity_client.create_spreadsheet(
            suite=suite,
            title=title,
            data=data,
            **kwargs
        )

        return sheet_id

    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        suite: Optional[ProductivitySuite] = None,
        **kwargs
    ) -> str:
        """
        Send email via productivity suite

        Args:
            to: Recipient email addresses
            subject: Email subject
            body: Email body
            attachments: File paths to attach
            cc: CC recipients
            bcc: BCC recipients
            suite: Productivity suite

        Returns:
            Message ID
        """
        if not self.productivity_client:
            raise ValueError("Productivity client not enabled")

        self._track_operation(IntegrationOperation.SEND_EMAIL)

        suite = suite or self.config.default_productivity
        message_id = self.productivity_client.send_email(
            suite=suite,
            to=to,
            subject=subject,
            body=body,
            attachments=attachments,
            cc=cc,
            bcc=bcc,
            **kwargs
        )

        logger.info(f"Sent email via {suite.value}: {message_id}")
        return message_id

    # ==================== Communication Platforms ====================

    def send_message(
        self,
        text: str,
        channel: str,
        platform: Optional[Platform] = None,
        attachments: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Send message to communication platform

        Args:
            text: Message text
            channel: Channel/chat ID
            platform: Communication platform (Slack, Teams, Discord)
            attachments: File attachments

        Returns:
            Message ID
        """
        if not self.communication_client:
            raise ValueError("Communication client not enabled")

        self._track_operation(IntegrationOperation.SEND_MESSAGE)

        platform = platform or self.config.default_communication
        message_id = self.communication_client.send_message(
            platform=platform,
            channel=channel,
            text=text,
            attachments=attachments,
            **kwargs
        )

        self.stats["messages_sent"] += 1
        logger.info(f"Sent message to {platform.value}: {message_id}")

        return message_id

    def create_channel(
        self,
        name: str,
        is_private: bool = False,
        platform: Optional[Platform] = None,
        **kwargs
    ) -> str:
        """Create channel in communication platform"""
        if not self.communication_client:
            raise ValueError("Communication client not enabled")

        platform = platform or self.config.default_communication
        channel_id = self.communication_client.create_channel(
            platform=platform,
            name=name,
            is_private=is_private,
            **kwargs
        )

        return channel_id

    def upload_file_to_chat(
        self,
        file_path: str,
        channel: str,
        comment: Optional[str] = None,
        platform: Optional[Platform] = None,
        **kwargs
    ) -> str:
        """Upload file to chat platform"""
        if not self.communication_client:
            raise ValueError("Communication client not enabled")

        platform = platform or self.config.default_communication
        file_id = self.communication_client.upload_file(
            platform=platform,
            channel=channel,
            file_path=file_path,
            comment=comment,
            **kwargs
        )

        return file_id

    def send_notification(
        self,
        title: str,
        message: str,
        channels: List[str],
        platform: Optional[Platform] = None,
        **kwargs
    ) -> List[str]:
        """Send notification to multiple channels"""
        if not self.communication_client:
            raise ValueError("Communication client not enabled")

        platform = platform or self.config.default_communication
        message_ids = []

        for channel in channels:
            msg_id = self.send_message(
                text=f"**{title}**\n{message}",
                channel=channel,
                platform=platform,
                **kwargs
            )
            message_ids.append(msg_id)

        return message_ids

    # ==================== E-Signature ====================

    def request_signature(
        self,
        document_path: str,
        signers: List[str],
        subject: Optional[str] = None,
        message: Optional[str] = None,
        provider: Optional[SignatureProvider] = None,
        **kwargs
    ) -> str:
        """
        Request e-signature for document

        Args:
            document_path: Path to document
            signers: List of signer email addresses
            subject: Email subject
            message: Message to signers
            provider: E-signature provider (DocuSign, Adobe Sign)

        Returns:
            Signature request ID
        """
        if not self.esignature_client:
            raise ValueError("E-signature client not enabled")

        self._track_operation(IntegrationOperation.REQUEST_SIGNATURE)

        provider = provider or self.config.default_signature
        request_id = self.esignature_client.request_signature(
            provider=provider,
            document_path=document_path,
            signers=signers,
            subject=subject,
            message=message,
            **kwargs
        )

        self.stats["signatures_requested"] += 1
        logger.info(f"Requested signature via {provider.value}: {request_id}")

        return request_id

    def get_signature_status(
        self,
        request_id: str,
        provider: Optional[SignatureProvider] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get status of signature request"""
        if not self.esignature_client:
            raise ValueError("E-signature client not enabled")

        provider = provider or self.config.default_signature
        status = self.esignature_client.get_status(
            provider=provider,
            request_id=request_id,
            **kwargs
        )

        return {
            "request_id": status.request_id,
            "status": status.status.value,
            "signed_count": status.signed_count,
            "total_signers": status.total_signers,
            "completed_at": status.completed_at.isoformat() if status.completed_at else None
        }

    def download_signed_document(
        self,
        request_id: str,
        destination: str,
        provider: Optional[SignatureProvider] = None,
        **kwargs
    ) -> str:
        """Download signed document"""
        if not self.esignature_client:
            raise ValueError("E-signature client not enabled")

        provider = provider or self.config.default_signature
        file_path = self.esignature_client.download_signed(
            provider=provider,
            request_id=request_id,
            destination=destination,
            **kwargs
        )

        return file_path

    # ==================== Calendar & Scheduling ====================

    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: Optional[List[str]] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar: Optional[CalendarProvider] = None,
        **kwargs
    ) -> str:
        """
        Create calendar event

        Args:
            title: Event title
            start_time: Start datetime
            end_time: End datetime
            attendees: List of attendee emails
            description: Event description
            location: Event location
            calendar: Calendar provider (Google Calendar, Outlook)

        Returns:
            Event ID
        """
        if not self.calendar_client:
            raise ValueError("Calendar client not enabled")

        self._track_operation(IntegrationOperation.CREATE_EVENT)

        calendar = calendar or self.config.default_calendar
        event_id = self.calendar_client.create_event(
            calendar=calendar,
            title=title,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            description=description,
            location=location,
            **kwargs
        )

        self.stats["events_created"] += 1
        logger.info(f"Created event in {calendar.value}: {event_id}")

        return event_id

    def list_events(
        self,
        start_date: datetime,
        end_date: datetime,
        calendar: Optional[CalendarProvider] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List calendar events in date range"""
        if not self.calendar_client:
            raise ValueError("Calendar client not enabled")

        calendar = calendar or self.config.default_calendar
        events = self.calendar_client.list_events(
            calendar=calendar,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

        return [
            {
                "event_id": e.event_id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "attendees": e.attendees,
                "location": e.location
            }
            for e in events
        ]

    def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any],
        calendar: Optional[CalendarProvider] = None,
        **kwargs
    ) -> bool:
        """Update calendar event"""
        if not self.calendar_client:
            raise ValueError("Calendar client not enabled")

        calendar = calendar or self.config.default_calendar
        success = self.calendar_client.update_event(
            calendar=calendar,
            event_id=event_id,
            **updates,
            **kwargs
        )

        return success

    def delete_event(
        self,
        event_id: str,
        calendar: Optional[CalendarProvider] = None,
        **kwargs
    ) -> bool:
        """Delete calendar event"""
        if not self.calendar_client:
            raise ValueError("Calendar client not enabled")

        calendar = calendar or self.config.default_calendar
        success = self.calendar_client.delete_event(
            calendar=calendar,
            event_id=event_id,
            **kwargs
        )

        return success

    # ==================== File Conversion ====================

    def convert_file(
        self,
        file_path: str,
        target_format: FileFormat,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Convert file to different format

        Args:
            file_path: Source file path
            target_format: Target file format
            output_path: Output file path (optional)

        Returns:
            Converted file path
        """
        if not self.file_converter:
            raise ValueError("File converter not enabled")

        self._track_operation(IntegrationOperation.CONVERT_FILE)

        result = self.file_converter.convert(
            file_path=file_path,
            target_format=target_format,
            output_path=output_path,
            **kwargs
        )

        self.stats["files_converted"] += 1
        logger.info(f"Converted file to {target_format.value}: {result.output_path}")

        return result.output_path

    def batch_convert(
        self,
        file_paths: List[str],
        target_format: FileFormat,
        **kwargs
    ) -> List[str]:
        """Batch convert multiple files"""
        if not self.file_converter:
            raise ValueError("File converter not enabled")

        output_paths = []
        for file_path in file_paths:
            output_path = self.convert_file(
                file_path=file_path,
                target_format=target_format,
                **kwargs
            )
            output_paths.append(output_path)

        return output_paths

    # ==================== Utility Methods ====================

    def _track_operation(self, operation: IntegrationOperation):
        """Track operation statistics"""
        self.stats["total_operations"] += 1
        self.stats["by_operation"][operation.value] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get API usage statistics

        Returns:
            Dict with usage statistics
        """
        return {
            **self.stats,
            "services_enabled": {
                "storage": self.storage_manager is not None,
                "productivity": self.productivity_client is not None,
                "communication": self.communication_client is not None,
                "esignature": self.esignature_client is not None,
                "calendar": self.calendar_client is not None,
                "conversion": self.file_converter is not None,
            }
        }

    def test_connection(self, service: str) -> bool:
        """Test connection to service"""
        try:
            if service == "storage" and self.storage_manager:
                return self.storage_manager.test_connection()
            elif service == "productivity" and self.productivity_client:
                return self.productivity_client.test_connection()
            elif service == "communication" and self.communication_client:
                return self.communication_client.test_connection()
            elif service == "esignature" and self.esignature_client:
                return self.esignature_client.test_connection()
            elif service == "calendar" and self.calendar_client:
                return self.calendar_client.test_connection()
            else:
                return False
        except Exception as e:
            logger.error(f"Connection test failed for {service}: {e}")
            return False


# Singleton
_integrations_api = None


def get_integrations_api(config: Optional[IntegrationsConfig] = None) -> IntegrationsAPI:
    """
    Get singleton Integrations API instance

    Args:
        config: Optional configuration

    Returns:
        Integrations API instance
    """
    global _integrations_api
    if _integrations_api is None:
        _integrations_api = IntegrationsAPI(config=config)
    return _integrations_api


# Convenience functions

def upload_file(file_path: str, storage: Optional[str] = None, **kwargs) -> str:
    """Convenience function for uploading files"""
    api = get_integrations_api()
    provider = StorageProvider(storage) if storage else None
    return api.upload_file(file_path, storage=provider, **kwargs)


def send_message(text: str, channel: str, platform: Optional[str] = None, **kwargs) -> str:
    """Convenience function for sending messages"""
    api = get_integrations_api()
    plat = Platform(platform) if platform else None
    return api.send_message(text, channel, platform=plat, **kwargs)


def request_signature(document_path: str, signers: List[str], **kwargs) -> str:
    """Convenience function for requesting signatures"""
    api = get_integrations_api()
    return api.request_signature(document_path, signers, **kwargs)
