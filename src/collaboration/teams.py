"""
Collaboration Tools - Team Spaces

Provides team collaboration features:
- Team spaces and channels
- Comments and discussions
- @mentions and notifications
- Activity feed
- File sharing within teams
- Permission management
- Real-time updates
"""

from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import re


class TeamRole(str, Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class ChannelType(str, Enum):
    """Channel types"""
    PUBLIC = "public"
    PRIVATE = "private"
    DIRECT = "direct"


class ActivityType(str, Enum):
    """Activity types for feed"""
    COMMENT = "comment"
    MENTION = "mention"
    FILE_UPLOAD = "file_upload"
    SERVICE_CREATED = "service_created"
    SERVICE_UPDATED = "service_updated"
    MEMBER_JOINED = "member_joined"
    MEMBER_LEFT = "member_left"


class Permission(str, Enum):
    """Team permissions"""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    DELETE = "delete"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_SETTINGS = "manage_settings"


@dataclass
class Team:
    """Team space"""
    id: str
    name: str
    description: str
    created_by: int
    created_at: datetime = field(default_factory=datetime.now)
    avatar: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamMember:
    """Team member"""
    team_id: str
    user_id: int
    role: TeamRole
    joined_at: datetime = field(default_factory=datetime.now)
    invited_by: Optional[int] = None
    nickname: Optional[str] = None


@dataclass
class Channel:
    """Team channel for discussions"""
    id: str
    team_id: str
    name: str
    description: str
    type: ChannelType
    created_by: int
    created_at: datetime = field(default_factory=datetime.now)
    members: List[int] = field(default_factory=list)  # For private channels


@dataclass
class Message:
    """Chat message"""
    id: str
    channel_id: str
    user_id: int
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    edited_at: Optional[datetime] = None
    parent_id: Optional[str] = None  # For threaded replies
    mentions: List[int] = field(default_factory=list)
    reactions: Dict[str, List[int]] = field(default_factory=dict)  # emoji -> user_ids
    attachments: List[str] = field(default_factory=list)


@dataclass
class Comment:
    """Comment on service/document"""
    id: str
    resource_type: str  # service, document, workflow, etc.
    resource_id: str
    user_id: int
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    edited_at: Optional[datetime] = None
    parent_id: Optional[str] = None  # For nested comments
    mentions: List[int] = field(default_factory=list)
    resolved: bool = False


@dataclass
class Activity:
    """Activity feed item"""
    id: str
    team_id: str
    type: ActivityType
    user_id: int
    title: str
    description: str
    resource_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SharedFile:
    """Shared file in team"""
    id: str
    team_id: str
    channel_id: Optional[str]
    name: str
    file_path: str
    size_bytes: int
    mime_type: str
    uploaded_by: int
    uploaded_at: datetime = field(default_factory=datetime.now)
    description: str = ""


class MentionParser:
    """Parses @mentions from text"""

    def parse_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        # Match @username or @user_id
        pattern = r'@(\w+)'
        matches = re.findall(pattern, text)
        return matches

    def resolve_mentions(
        self,
        text: str,
        team_members: Dict[str, int]  # username -> user_id
    ) -> List[int]:
        """Resolve mentions to user IDs"""
        mentions = self.parse_mentions(text)
        user_ids = []

        for mention in mentions:
            # Try to find user by username
            if mention in team_members:
                user_ids.append(team_members[mention])
            # Try to parse as user ID
            elif mention.isdigit():
                user_ids.append(int(mention))

        return list(set(user_ids))  # Remove duplicates


class PermissionManager:
    """Manages team permissions"""

    def __init__(self):
        # Role-based permissions
        self.role_permissions = {
            TeamRole.OWNER: [
                Permission.VIEW,
                Permission.COMMENT,
                Permission.EDIT,
                Permission.DELETE,
                Permission.MANAGE_MEMBERS,
                Permission.MANAGE_SETTINGS
            ],
            TeamRole.ADMIN: [
                Permission.VIEW,
                Permission.COMMENT,
                Permission.EDIT,
                Permission.DELETE,
                Permission.MANAGE_MEMBERS
            ],
            TeamRole.MEMBER: [
                Permission.VIEW,
                Permission.COMMENT,
                Permission.EDIT
            ],
            TeamRole.GUEST: [
                Permission.VIEW,
                Permission.COMMENT
            ]
        }

    def has_permission(
        self,
        member_role: TeamRole,
        required_permission: Permission
    ) -> bool:
        """Check if role has permission"""
        return required_permission in self.role_permissions.get(member_role, [])

    def get_permissions(self, member_role: TeamRole) -> List[Permission]:
        """Get all permissions for role"""
        return self.role_permissions.get(member_role, [])


class TeamManager:
    """Manages teams and members"""

    def __init__(self, database=None):
        self.database = database
        self.teams: Dict[str, Team] = {}
        self.members: Dict[str, List[TeamMember]] = {}  # team_id -> members
        self.permission_manager = PermissionManager()

    def create_team(
        self,
        name: str,
        description: str,
        created_by: int
    ) -> str:
        """Create new team"""
        team_id = str(uuid.uuid4())

        team = Team(
            id=team_id,
            name=name,
            description=description,
            created_by=created_by
        )

        self.teams[team_id] = team

        # Add creator as owner
        self.add_member(team_id, created_by, TeamRole.OWNER)

        return team_id

    def add_member(
        self,
        team_id: str,
        user_id: int,
        role: TeamRole,
        invited_by: Optional[int] = None
    ) -> bool:
        """Add member to team"""
        if team_id not in self.teams:
            return False

        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by
        )

        if team_id not in self.members:
            self.members[team_id] = []

        self.members[team_id].append(member)
        return True

    def remove_member(self, team_id: str, user_id: int) -> bool:
        """Remove member from team"""
        if team_id not in self.members:
            return False

        self.members[team_id] = [
            m for m in self.members[team_id]
            if m.user_id != user_id
        ]

        return True

    def update_member_role(
        self,
        team_id: str,
        user_id: int,
        new_role: TeamRole
    ) -> bool:
        """Update member role"""
        if team_id not in self.members:
            return False

        for member in self.members[team_id]:
            if member.user_id == user_id:
                member.role = new_role
                return True

        return False

    def get_member(self, team_id: str, user_id: int) -> Optional[TeamMember]:
        """Get team member"""
        if team_id not in self.members:
            return None

        for member in self.members[team_id]:
            if member.user_id == user_id:
                return member

        return None

    def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all team members"""
        return self.members.get(team_id, [])

    def get_user_teams(self, user_id: int) -> List[Team]:
        """Get all teams user is member of"""
        user_teams = []

        for team_id, members in self.members.items():
            if any(m.user_id == user_id for m in members):
                if team_id in self.teams:
                    user_teams.append(self.teams[team_id])

        return user_teams


class ChannelManager:
    """Manages team channels"""

    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.messages: Dict[str, List[Message]] = {}  # channel_id -> messages

    def create_channel(
        self,
        team_id: str,
        name: str,
        description: str,
        channel_type: ChannelType,
        created_by: int,
        members: Optional[List[int]] = None
    ) -> str:
        """Create new channel"""
        channel_id = str(uuid.uuid4())

        channel = Channel(
            id=channel_id,
            team_id=team_id,
            name=name,
            description=description,
            type=channel_type,
            created_by=created_by,
            members=members or []
        )

        self.channels[channel_id] = channel
        self.messages[channel_id] = []

        return channel_id

    def send_message(
        self,
        channel_id: str,
        user_id: int,
        content: str,
        parent_id: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> str:
        """Send message to channel"""
        if channel_id not in self.channels:
            return ""

        message_id = str(uuid.uuid4())

        # Parse mentions
        mention_parser = MentionParser()
        mentions = mention_parser.parse_mentions(content)

        message = Message(
            id=message_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            mentions=[],  # Would resolve to user IDs
            attachments=attachments or []
        )

        self.messages[channel_id].append(message)

        return message_id

    def add_reaction(
        self,
        channel_id: str,
        message_id: str,
        user_id: int,
        emoji: str
    ) -> bool:
        """Add reaction to message"""
        if channel_id not in self.messages:
            return False

        for message in self.messages[channel_id]:
            if message.id == message_id:
                if emoji not in message.reactions:
                    message.reactions[emoji] = []
                if user_id not in message.reactions[emoji]:
                    message.reactions[emoji].append(user_id)
                return True

        return False

    def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50
    ) -> List[Message]:
        """Get recent messages from channel"""
        if channel_id not in self.messages:
            return []

        messages = self.messages[channel_id]
        return messages[-limit:]  # Most recent

    def get_thread_messages(
        self,
        channel_id: str,
        parent_message_id: str
    ) -> List[Message]:
        """Get threaded replies"""
        if channel_id not in self.messages:
            return []

        return [
            m for m in self.messages[channel_id]
            if m.parent_id == parent_message_id
        ]


class CommentManager:
    """Manages comments on resources"""

    def __init__(self):
        self.comments: Dict[str, List[Comment]] = {}  # resource_id -> comments

    def add_comment(
        self,
        resource_type: str,
        resource_id: str,
        user_id: int,
        content: str,
        parent_id: Optional[str] = None
    ) -> str:
        """Add comment to resource"""
        comment_id = str(uuid.uuid4())

        # Parse mentions
        mention_parser = MentionParser()
        mentions = mention_parser.parse_mentions(content)

        comment = Comment(
            id=comment_id,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            mentions=[]  # Would resolve to user IDs
        )

        key = f"{resource_type}:{resource_id}"
        if key not in self.comments:
            self.comments[key] = []

        self.comments[key].append(comment)

        return comment_id

    def edit_comment(
        self,
        resource_type: str,
        resource_id: str,
        comment_id: str,
        new_content: str
    ) -> bool:
        """Edit comment"""
        key = f"{resource_type}:{resource_id}"
        if key not in self.comments:
            return False

        for comment in self.comments[key]:
            if comment.id == comment_id:
                comment.content = new_content
                comment.edited_at = datetime.now()
                return True

        return False

    def delete_comment(
        self,
        resource_type: str,
        resource_id: str,
        comment_id: str
    ) -> bool:
        """Delete comment"""
        key = f"{resource_type}:{resource_id}"
        if key not in self.comments:
            return False

        self.comments[key] = [
            c for c in self.comments[key]
            if c.id != comment_id
        ]

        return True

    def resolve_comment(
        self,
        resource_type: str,
        resource_id: str,
        comment_id: str
    ) -> bool:
        """Mark comment as resolved"""
        key = f"{resource_type}:{resource_id}"
        if key not in self.comments:
            return False

        for comment in self.comments[key]:
            if comment.id == comment_id:
                comment.resolved = True
                return True

        return False

    def get_comments(
        self,
        resource_type: str,
        resource_id: str,
        include_resolved: bool = False
    ) -> List[Comment]:
        """Get comments for resource"""
        key = f"{resource_type}:{resource_id}"
        comments = self.comments.get(key, [])

        if not include_resolved:
            comments = [c for c in comments if not c.resolved]

        return comments


class ActivityFeed:
    """Activity feed for team"""

    def __init__(self):
        self.activities: Dict[str, List[Activity]] = {}  # team_id -> activities

    def add_activity(
        self,
        team_id: str,
        activity_type: ActivityType,
        user_id: int,
        title: str,
        description: str,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add activity to feed"""
        activity_id = str(uuid.uuid4())

        activity = Activity(
            id=activity_id,
            team_id=team_id,
            type=activity_type,
            user_id=user_id,
            title=title,
            description=description,
            resource_id=resource_id,
            metadata=metadata or {}
        )

        if team_id not in self.activities:
            self.activities[team_id] = []

        self.activities[team_id].append(activity)

        # Keep only last 1000 activities
        if len(self.activities[team_id]) > 1000:
            self.activities[team_id] = self.activities[team_id][-1000:]

        return activity_id

    def get_team_feed(
        self,
        team_id: str,
        limit: int = 50
    ) -> List[Activity]:
        """Get team activity feed"""
        if team_id not in self.activities:
            return []

        activities = self.activities[team_id]
        return activities[-limit:]  # Most recent

    def get_user_feed(
        self,
        team_id: str,
        user_id: int,
        limit: int = 50
    ) -> List[Activity]:
        """Get activities for specific user"""
        if team_id not in self.activities:
            return []

        user_activities = [
            a for a in self.activities[team_id]
            if a.user_id == user_id
        ]

        return user_activities[-limit:]


class FileManager:
    """Manages file sharing in teams"""

    def __init__(self):
        self.files: Dict[str, List[SharedFile]] = {}  # team_id -> files

    def upload_file(
        self,
        team_id: str,
        channel_id: Optional[str],
        name: str,
        file_path: str,
        size_bytes: int,
        mime_type: str,
        uploaded_by: int,
        description: str = ""
    ) -> str:
        """Upload file to team"""
        file_id = str(uuid.uuid4())

        shared_file = SharedFile(
            id=file_id,
            team_id=team_id,
            channel_id=channel_id,
            name=name,
            file_path=file_path,
            size_bytes=size_bytes,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            description=description
        )

        if team_id not in self.files:
            self.files[team_id] = []

        self.files[team_id].append(shared_file)

        return file_id

    def get_team_files(
        self,
        team_id: str,
        channel_id: Optional[str] = None
    ) -> List[SharedFile]:
        """Get files for team or channel"""
        if team_id not in self.files:
            return []

        files = self.files[team_id]

        if channel_id:
            files = [f for f in files if f.channel_id == channel_id]

        return files


class CollaborationEngine:
    """Main collaboration engine"""

    def __init__(self, database=None):
        self.database = database
        self.team_manager = TeamManager(database)
        self.channel_manager = ChannelManager()
        self.comment_manager = CommentManager()
        self.activity_feed = ActivityFeed()
        self.file_manager = FileManager()

    def create_team(self, name: str, description: str, created_by: int) -> str:
        """Create team and default channels"""
        team_id = self.team_manager.create_team(name, description, created_by)

        # Create default channels
        self.channel_manager.create_channel(
            team_id=team_id,
            name="general",
            description="General discussion",
            channel_type=ChannelType.PUBLIC,
            created_by=created_by
        )

        self.channel_manager.create_channel(
            team_id=team_id,
            name="announcements",
            description="Team announcements",
            channel_type=ChannelType.PUBLIC,
            created_by=created_by
        )

        # Log activity
        self.activity_feed.add_activity(
            team_id=team_id,
            activity_type=ActivityType.MEMBER_JOINED,
            user_id=created_by,
            title="Team Created",
            description=f"Team '{name}' was created"
        )

        return team_id

    def invite_member(
        self,
        team_id: str,
        user_id: int,
        role: TeamRole,
        invited_by: int
    ) -> bool:
        """Invite member to team"""
        success = self.team_manager.add_member(team_id, user_id, role, invited_by)

        if success:
            # Log activity
            self.activity_feed.add_activity(
                team_id=team_id,
                activity_type=ActivityType.MEMBER_JOINED,
                user_id=user_id,
                title="Member Joined",
                description=f"User {user_id} joined the team"
            )

        return success

    def get_statistics(self, team_id: str) -> Dict[str, Any]:
        """Get team statistics"""
        members = self.team_manager.get_team_members(team_id)
        channels = [c for c in self.channel_manager.channels.values() if c.team_id == team_id]

        total_messages = 0
        for channel in channels:
            channel_messages = self.channel_manager.get_channel_messages(channel.id, limit=999999)
            total_messages += len(channel_messages)

        files = self.file_manager.get_team_files(team_id)

        return {
            'team_id': team_id,
            'members_count': len(members),
            'channels_count': len(channels),
            'messages_count': total_messages,
            'files_count': len(files),
            'activity_count': len(self.activity_feed.get_team_feed(team_id, limit=999999))
        }


# Global instance
_collaboration_engine: Optional[CollaborationEngine] = None


def get_collaboration_engine(database=None) -> CollaborationEngine:
    """Get global collaboration engine instance"""
    global _collaboration_engine

    if _collaboration_engine is None:
        _collaboration_engine = CollaborationEngine(database)

    return _collaboration_engine


def configure_collaboration_engine(database):
    """Configure collaboration engine"""
    global _collaboration_engine
    _collaboration_engine = CollaborationEngine(database)
