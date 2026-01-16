"""
Authentication and Authorization System

Comprehensive user authentication with role-based access control (RBAC).
Supports password hashing, session management, JWT tokens, and permissions.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional

import jwt
from flask import g, request, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user

logger = logging.getLogger("dms.auth")


class Role(str, Enum):
    """User roles with hierarchical privileges."""

    ADMIN = "admin"  # Full system access
    MANAGER = "manager"  # Manage services and users
    EDITOR = "editor"  # Create and edit services
    VIEWER = "viewer"  # Read-only access
    GUEST = "guest"  # Limited access


class Permission(str, Enum):
    """Granular permissions."""

    # Service permissions
    SERVICE_CREATE = "service:create"
    SERVICE_READ = "service:read"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"

    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # System permissions
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_BACKUP = "system:backup"

    # Export/Import permissions
    EXPORT_DATA = "export:data"
    IMPORT_DATA = "import:data"

    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"


# Role permissions mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: [p for p in Permission],  # All permissions
    Role.MANAGER: [
        Permission.SERVICE_CREATE,
        Permission.SERVICE_READ,
        Permission.SERVICE_UPDATE,
        Permission.SERVICE_DELETE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.EXPORT_DATA,
        Permission.IMPORT_DATA,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
    ],
    Role.EDITOR: [
        Permission.SERVICE_CREATE,
        Permission.SERVICE_READ,
        Permission.SERVICE_UPDATE,
        Permission.EXPORT_DATA,
        Permission.ANALYTICS_VIEW,
    ],
    Role.VIEWER: [
        Permission.SERVICE_READ,
        Permission.ANALYTICS_VIEW,
    ],
    Role.GUEST: [
        Permission.SERVICE_READ,
    ],
}


class User(UserMixin):
    """User model."""

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password_hash: str,
        role: Role = Role.VIEWER,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        # UserMixin provides is_active property, store in private variable
        self._is_active = is_active
        self.created_at = created_at or datetime.now()

    @property
    def is_active(self):
        """User active status."""
        return getattr(self, "_is_active", True)

    @is_active.setter
    def is_active(self, value):
        """Set user active status."""
        self._is_active = value

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in ROLE_PERMISSIONS.get(self.role, [])

    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(p) for p in permissions)

    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(self.has_permission(p) for p in permissions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuthManager:
    """Manage user authentication and authorization."""

    def __init__(self, app=None, db_path: str = "data/db/users.db"):
        """
        Initialize authentication manager.

        Args:
            app: Flask application instance
            db_path: Path to user database
        """
        self.app = app
        self.db_path = db_path
        self.bcrypt = Bcrypt()
        self.login_manager = LoginManager()

        if app:
            self.init_app(app)

        self._init_database()

    def init_app(self, app):
        """Initialize with Flask app."""
        self.app = app
        self.bcrypt.init_app(app)
        self.login_manager.init_app(app)
        self.login_manager.login_view = "auth.login"
        self.login_manager.user_loader(self.load_user)

    def _init_database(self):
        """Initialize user database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'viewer',
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create refresh tokens table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                revoked INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Create token blacklist table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS token_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                reason TEXT
            )
        """
        )

        # Create index for faster lookups
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_token_blacklist_token ON token_blacklist(token)
        """
        )

        # Create default admin user if none exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = ?", (Role.ADMIN.value,))
        if cursor.fetchone()[0] == 0:
            admin_password_hash = self.bcrypt.generate_password_hash("admin").decode("utf-8")
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """,
                ("admin", "admin@dms.local", admin_password_hash, Role.ADMIN.value),
            )
            logger.info("Created default admin user (username: admin, password: admin)")

        conn.commit()
        conn.close()

    def create_user(self, username: str, email: str, password: str, role: Role = Role.VIEWER) -> Optional[User]:
        """
        Create a new user.

        Args:
            username: Username
            email: Email address
            password: Plain text password
            role: User role

        Returns:
            Created user or None if failed
        """
        try:
            password_hash = self.bcrypt.generate_password_hash(password).decode("utf-8")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """,
                (username, email, password_hash, role.value),
            )

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Created user: {username} ({role.value})")

            return User(id=user_id, username=username, email=email, password_hash=password_hash, role=role)

        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to create user {username}: {e}")
            return None

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Authenticated user or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Find user by username or email
        cursor.execute(
            """
            SELECT * FROM users
            WHERE (username = ? OR email = ?) AND is_active = 1
        """,
            (username, username),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            logger.warning(f"Authentication failed: user not found: {username}")
            return None

        # Verify password
        if not self.bcrypt.check_password_hash(row["password_hash"], password):
            logger.warning(f"Authentication failed: invalid password for {username}")
            return None

        # Update last login
        self._update_last_login(row["id"])

        user = User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=Role(row["role"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )

        logger.info(f"User authenticated: {username}")
        return user

    def load_user(self, user_id: int) -> Optional[User]:
        """Load user by ID (for Flask-Login)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=Role(row["role"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )

    def _update_last_login(self, user_id: int):
        """Update user's last login timestamp."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        """,
            (user_id,),
        )

        conn.commit()
        conn.close()

    def generate_token(self, user: User, secret_key: str, expires_in: int = 3600) -> str:
        """
        Generate JWT token for user.

        Args:
            user: User object
            secret_key: Secret key for signing
            expires_in: Token expiration in seconds

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token

    def verify_token(self, token: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token.

        Args:
            token: JWT token
            secret_key: Secret key for verification

        Returns:
            Token payload or None if invalid
        """
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                logger.warning("Token is blacklisted")
                return None

            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def generate_refresh_token(self, user: User, secret_key: str, expires_in: int = 2592000) -> str:
        """
        Generate refresh token for user (default 30 days).

        Args:
            user: User object
            secret_key: Secret key for signing
            expires_in: Token expiration in seconds (default 30 days)

        Returns:
            Refresh token string
        """
        import secrets

        # Generate unique refresh token
        token_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        payload = {
            "user_id": user.id,
            "token_id": token_id,
            "type": "refresh",
            "exp": expires_at,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, secret_key, algorithm="HS256")

        # Store refresh token in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        """,
            (user.id, token, expires_at.isoformat()),
        )

        conn.commit()
        conn.close()

        logger.info(f"Generated refresh token for user {user.username}")
        return token

    def verify_refresh_token(self, token: str, secret_key: str) -> Optional[User]:
        """
        Verify refresh token and return user.

        Args:
            token: Refresh token
            secret_key: Secret key for verification

        Returns:
            User object or None if invalid
        """
        try:
            # Decode token
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])

            if payload.get("type") != "refresh":
                logger.warning("Token is not a refresh token")
                return None

            # Check if token exists and is not revoked
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT user_id, revoked, expires_at FROM refresh_tokens
                WHERE token = ?
            """,
                (token,),
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.warning("Refresh token not found in database")
                return None

            user_id, revoked, expires_at = row

            if revoked:
                logger.warning("Refresh token has been revoked")
                return None

            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                logger.warning("Refresh token expired")
                return None

            # Load and return user
            return self.load_user(user_id)

        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid refresh token: {e}")
            return None

    def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoke a refresh token.

        Args:
            token: Refresh token to revoke

        Returns:
            True if revoked successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked = 1
                WHERE token = ?
            """,
                (token,),
            )

            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            if rows_affected > 0:
                logger.info("Refresh token revoked")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to revoke refresh token: {e}")
            return False

    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked = 1
                WHERE user_id = ? AND revoked = 0
            """,
                (user_id,),
            )

            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"Revoked {rows_affected} refresh tokens for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return False

    def blacklist_token(self, token: str, reason: str = "logout", expires_in: int = 3600) -> bool:
        """
        Add access token to blacklist.

        Args:
            token: Access token to blacklist
            reason: Reason for blacklisting
            expires_in: How long to keep in blacklist (seconds)

        Returns:
            True if blacklisted successfully
        """
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR IGNORE INTO token_blacklist (token, expires_at, reason)
                VALUES (?, ?, ?)
            """,
                (token, expires_at.isoformat(), reason),
            )

            conn.commit()
            conn.close()

            logger.info(f"Token blacklisted: {reason}")
            return True

        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False

    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: Token to check

        Returns:
            True if blacklisted
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT expires_at FROM token_blacklist
                WHERE token = ?
            """,
                (token,),
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                return False

            # Check if blacklist entry expired
            expires_at = datetime.fromisoformat(row[0])
            if expires_at < datetime.utcnow():
                # Clean up expired entry
                self._remove_expired_blacklist_entries()
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to check blacklist: {e}")
            return False

    def _remove_expired_blacklist_entries(self):
        """Clean up expired blacklist entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM token_blacklist
                WHERE expires_at < ?
            """,
                (datetime.utcnow().isoformat(),),
            )

            rows_deleted = cursor.rowcount
            conn.commit()
            conn.close()

            if rows_deleted > 0:
                logger.debug(f"Cleaned up {rows_deleted} expired blacklist entries")

        except Exception as e:
            logger.error(f"Failed to clean blacklist: {e}")

    def logout(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        """
        Logout user by blacklisting tokens.

        Args:
            access_token: Access token to blacklist
            refresh_token: Optional refresh token to revoke

        Returns:
            True if successful
        """
        success = True

        # Blacklist access token
        if access_token:
            success = success and self.blacklist_token(access_token, reason="logout")

        # Revoke refresh token
        if refresh_token:
            success = success and self.revoke_refresh_token(refresh_token)

        logger.info("User logged out")
        return success


# Decorators for access control


def login_required(f):
    """Decorator to require authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthorized access attempt to {f.__name__}")
            return {"error": "Authentication required"}, 401
        return f(*args, **kwargs)

    return decorated_function


def permission_required(*permissions: Permission):
    """Decorator to require specific permissions."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning(f"Unauthorized access attempt to {f.__name__}")
                return {"error": "Authentication required"}, 401

            if not current_user.has_any_permission(list(permissions)):
                logger.warning(f"Permission denied for {current_user.username} on {f.__name__}")
                return {"error": "Permission denied"}, 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def role_required(*roles: Role):
    """Decorator to require specific roles."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return {"error": "Authentication required"}, 401

            if current_user.role not in roles:
                logger.warning(f"Role check failed for {current_user.username} on {f.__name__}")
                return {"error": "Insufficient privileges"}, 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# Alias for backward compatibility
AuthService = AuthManager
