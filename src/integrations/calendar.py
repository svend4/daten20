"""
Calendar & Scheduling Integration

Integration with Google Calendar and Outlook Calendar for event management.

Part of v3.7 Advanced Integrations implementation.

Configuration required:
- Google Calendar: access_token (OAuth 2.0)
- Outlook Calendar: access_token (Microsoft Graph API OAuth 2.0)
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Optional HTTP library
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.warning("requests library not available - calendar will be simulated. Install: pip install requests")


class CalendarProvider(Enum):
    """Calendar providers."""

    GOOGLE_CALENDAR = "google_calendar"
    OUTLOOK_CALENDAR = "outlook_calendar"


@dataclass
class CalendarEvent:
    """Calendar event."""

    event_id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str] = field(default_factory=list)
    location: Optional[str] = None
    description: Optional[str] = None
    video_conference_link: Optional[str] = None
    reminders: List[int] = field(default_factory=list)
    provider: Optional[CalendarProvider] = None


class BaseCalendarProvider(ABC):
    """Base calendar provider."""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.connected = False

    @abstractmethod
    async def create_event(self, title: str, start_time: datetime, end_time: datetime, **kwargs) -> CalendarEvent:
        """Create calendar event."""
        pass

    @abstractmethod
    async def list_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """List events."""
        pass


class GoogleCalendarClient(BaseCalendarProvider):
    """Google Calendar integration via Google Calendar API v3.

    Requires credentials:
    - access_token: OAuth 2.0 access token
    - calendar_id: Calendar ID (default: 'primary')
    """

    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.access_token = credentials.get('access_token')
        self.calendar_id = credentials.get('calendar_id', 'primary')
        self.base_url = 'https://www.googleapis.com/calendar/v3'

        if not self.access_token:
            logger.warning("Google Calendar access token missing - operations will be simulated")

    async def create_event(self, title: str, start_time: datetime, end_time: datetime, **kwargs) -> CalendarEvent:
        """Create Google Calendar event via API."""

        if not HAS_REQUESTS or not self.access_token:
            # Fallback to simulation
            logger.warning("Simulating Google Calendar event creation (missing requests or credentials)")
            event = CalendarEvent(
                event_id=str(uuid4()),
                title=title,
                start_time=start_time,
                end_time=end_time,
                attendees=kwargs.get("attendees", []),
                location=kwargs.get("location"),
                video_conference_link=kwargs.get("video_conference") and "https://meet.google.com/xyz",
                provider=CalendarProvider.GOOGLE_CALENDAR,
            )
            return event

        # Build event definition
        event_body = {
            "summary": title,
            "description": kwargs.get("description", ""),
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            }
        }

        # Add location if provided
        if kwargs.get("location"):
            event_body["location"] = kwargs["location"]

        # Add attendees if provided
        if kwargs.get("attendees"):
            event_body["attendees"] = [{"email": email} for email in kwargs["attendees"]]

        # Add Google Meet if requested
        if kwargs.get("video_conference"):
            event_body["conferenceData"] = {
                "createRequest": {
                    "requestId": str(uuid4()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }

        # Add reminders if provided
        if kwargs.get("reminders"):
            event_body["reminders"] = {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": m} for m in kwargs["reminders"]]
            }

        # Make API request
        try:
            url = f"{self.base_url}/calendars/{self.calendar_id}/events"
            params = {"conferenceDataVersion": 1} if kwargs.get("video_conference") else {}
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=event_body, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            event_id = result.get('id', str(uuid4()))
            meet_link = None

            if result.get('conferenceData'):
                meet_link = result['conferenceData'].get('entryPoints', [{}])[0].get('uri')

            logger.info(f"Created Google Calendar event {event_id}: {title}")

            event = CalendarEvent(
                event_id=event_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                attendees=kwargs.get("attendees", []),
                location=kwargs.get("location"),
                description=kwargs.get("description"),
                video_conference_link=meet_link,
                reminders=kwargs.get("reminders", []),
                provider=CalendarProvider.GOOGLE_CALENDAR,
            )

            return event

        except requests.exceptions.HTTPError as e:
            logger.error(f"Google Calendar API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Google Calendar API error: {e.response.status_code}")

        except Exception as e:
            logger.exception(f"Error creating Google Calendar event: {e}")
            raise

    async def list_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """List Google Calendar events via API."""

        if not HAS_REQUESTS or not self.access_token:
            logger.warning("Simulating Google Calendar event list (missing requests or credentials)")
            return []

        try:
            url = f"{self.base_url}/calendars/{self.calendar_id}/events"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            params = {
                "timeMin": start_date.isoformat() + 'Z',
                "timeMax": end_date.isoformat() + 'Z',
                "singleEvents": True,
                "orderBy": "startTime"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            items = result.get('items', [])

            events = []
            for item in items:
                start = item['start'].get('dateTime', item['start'].get('date'))
                end = item['end'].get('dateTime', item['end'].get('date'))

                event = CalendarEvent(
                    event_id=item['id'],
                    title=item.get('summary', 'No Title'),
                    start_time=datetime.fromisoformat(start.rstrip('Z')),
                    end_time=datetime.fromisoformat(end.rstrip('Z')),
                    attendees=[a['email'] for a in item.get('attendees', [])],
                    location=item.get('location'),
                    description=item.get('description'),
                    provider=CalendarProvider.GOOGLE_CALENDAR,
                )
                events.append(event)

            logger.info(f"Listed {len(events)} Google Calendar events")
            return events

        except requests.exceptions.HTTPError as e:
            logger.error(f"Google Calendar API error: {e.response.status_code}")
            raise Exception(f"Google Calendar API error: {e.response.status_code}")

        except Exception as e:
            logger.exception(f"Error listing Google Calendar events: {e}")
            raise


class OutlookCalendarClient(BaseCalendarProvider):
    """Outlook Calendar integration via Microsoft Graph API.

    Requires credentials:
    - access_token: OAuth 2.0 access token (Microsoft identity platform)
    - user_id: User ID or email (default: 'me')
    """

    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.access_token = credentials.get('access_token')
        self.user_id = credentials.get('user_id', 'me')
        self.base_url = 'https://graph.microsoft.com/v1.0'

        if not self.access_token:
            logger.warning("Outlook Calendar access token missing - operations will be simulated")

    async def create_event(self, title: str, start_time: datetime, end_time: datetime, **kwargs) -> CalendarEvent:
        """Create Outlook Calendar event via Microsoft Graph API."""

        if not HAS_REQUESTS or not self.access_token:
            # Fallback to simulation
            logger.warning("Simulating Outlook Calendar event creation (missing requests or credentials)")
            event = CalendarEvent(
                event_id=str(uuid4()),
                title=title,
                start_time=start_time,
                end_time=end_time,
                attendees=kwargs.get("attendees", []),
                location=kwargs.get("location"),
                provider=CalendarProvider.OUTLOOK_CALENDAR,
            )
            return event

        # Build event definition
        event_body = {
            "subject": title,
            "body": {
                "contentType": "text",
                "content": kwargs.get("description", "")
            },
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            }
        }

        # Add location if provided
        if kwargs.get("location"):
            event_body["location"] = {
                "displayName": kwargs["location"]
            }

        # Add attendees if provided
        if kwargs.get("attendees"):
            event_body["attendees"] = [
                {
                    "emailAddress": {"address": email},
                    "type": "required"
                }
                for email in kwargs["attendees"]
            ]

        # Add Teams meeting if requested
        if kwargs.get("video_conference"):
            event_body["isOnlineMeeting"] = True
            event_body["onlineMeetingProvider"] = "teamsForBusiness"

        # Add reminders if provided
        if kwargs.get("reminders"):
            event_body["isReminderOn"] = True
            event_body["reminderMinutesBeforeStart"] = kwargs["reminders"][0] if kwargs["reminders"] else 15

        # Make API request
        try:
            url = f"{self.base_url}/users/{self.user_id}/calendar/events"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=event_body, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()
            event_id = result.get('id', str(uuid4()))
            teams_link = None

            if result.get('onlineMeeting'):
                teams_link = result['onlineMeeting'].get('joinUrl')

            logger.info(f"Created Outlook Calendar event {event_id}: {title}")

            event = CalendarEvent(
                event_id=event_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                attendees=kwargs.get("attendees", []),
                location=kwargs.get("location"),
                description=kwargs.get("description"),
                video_conference_link=teams_link,
                reminders=kwargs.get("reminders", []),
                provider=CalendarProvider.OUTLOOK_CALENDAR,
            )

            return event

        except requests.exceptions.HTTPError as e:
            logger.error(f"Outlook Calendar API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Outlook Calendar API error: {e.response.status_code}")

        except Exception as e:
            logger.exception(f"Error creating Outlook Calendar event: {e}")
            raise

    async def list_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """List Outlook Calendar events via Microsoft Graph API."""

        if not HAS_REQUESTS or not self.access_token:
            logger.warning("Simulating Outlook Calendar event list (missing requests or credentials)")
            return []

        try:
            # Use calendarView endpoint with date filter
            url = f"{self.base_url}/users/{self.user_id}/calendar/calendarView"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Prefer": "outlook.timezone=\"UTC\""
            }
            params = {
                "startDateTime": start_date.isoformat(),
                "endDateTime": end_date.isoformat(),
                "$orderby": "start/dateTime"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            items = result.get('value', [])

            events = []
            for item in items:
                start = item['start']['dateTime']
                end = item['end']['dateTime']

                attendees = [a['emailAddress']['address'] for a in item.get('attendees', [])]
                location = item.get('location', {}).get('displayName')
                description = item.get('body', {}).get('content', '')

                event = CalendarEvent(
                    event_id=item['id'],
                    title=item.get('subject', 'No Title'),
                    start_time=datetime.fromisoformat(start),
                    end_time=datetime.fromisoformat(end),
                    attendees=attendees,
                    location=location,
                    description=description,
                    provider=CalendarProvider.OUTLOOK_CALENDAR,
                )
                events.append(event)

            logger.info(f"Listed {len(events)} Outlook Calendar events")
            return events

        except requests.exceptions.HTTPError as e:
            logger.error(f"Outlook Calendar API error: {e.response.status_code}")
            raise Exception(f"Outlook Calendar API error: {e.response.status_code}")

        except Exception as e:
            logger.exception(f"Error listing Outlook Calendar events: {e}")
            raise


class CalendarManager:
    """Main calendar manager."""

    def __init__(self):
        self.providers: Dict[CalendarProvider, BaseCalendarProvider] = {}

    def register_provider(self, provider: CalendarProvider, credentials: Dict[str, str]):
        """Register calendar provider."""
        if provider == CalendarProvider.GOOGLE_CALENDAR:
            self.providers[provider] = GoogleCalendarClient(credentials)
        elif provider == CalendarProvider.OUTLOOK_CALENDAR:
            self.providers[provider] = OutlookCalendarClient(credentials)

    async def create_event(
        self, provider: str, title: str, start_time: datetime, end_time: datetime, **kwargs
    ) -> CalendarEvent:
        """Create calendar event."""
        provider_enum = CalendarProvider(provider)
        client = self.providers[provider_enum]
        return await client.create_event(title, start_time, end_time, **kwargs)


_calendar_manager: Optional[CalendarManager] = None


def get_calendar_client(provider: str = "google_calendar") -> CalendarManager:
    """Get calendar manager."""
    global _calendar_manager
    if _calendar_manager is None:
        _calendar_manager = CalendarManager()
    return _calendar_manager
