"""
Comprehensive tests for core.auth module with AuthManager

Test coverage goals:
- User creation and management
- Authentication and authorization
- JWT token generation and verification
- Refresh tokens and token revocation
- Token blacklisting
- Permission and role-based access control
- Security features
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import jwt
import pytest

from src.core.auth import (
    AuthManager,
    Permission,
    Role,
    User,
    login_required,
    permission_required,
    role_required,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def temp_db_path(tmp_path):
    """Create temporary database path"""
    return str(tmp_path / "test_auth.db")


@pytest.fixture
def auth_manager(temp_db_path):
    """Create AuthManager instance with temporary database"""
    manager = AuthManager(app=None, db_path=temp_db_path)
    return manager


@pytest.fixture
def mock_app():
    """Create mock Flask app"""
    app = MagicMock()
    app.config = {"SECRET_KEY": "test_secret_key_12345"}
    return app


@pytest.fixture
def test_user(auth_manager):
    """Create test user"""
    user = auth_manager.create_user(
        username="testuser", email="test@example.com", password="TestPass123!", role=Role.EDITOR
    )
    return user


@pytest.fixture
def admin_user(auth_manager):
    """Get admin user"""
    user = auth_manager.authenticate("admin", "admin")
    return user


class TestUserModel:
    """Tests for User model"""

    def test_user_creation(self):
        """Test User model instantiation"""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            role=Role.EDITOR,
        )

        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == Role.EDITOR
        # is_active from UserMixin defaults to True
        assert user.is_active is True

    def test_user_has_permission(self):
        """Test user permission checking"""
        editor = User(id=1, username="editor", email="editor@example.com", password_hash="hash", role=Role.EDITOR)

        # Editor should have create, read, update permissions
        assert editor.has_permission(Permission.SERVICE_CREATE) is True
        assert editor.has_permission(Permission.SERVICE_READ) is True
        assert editor.has_permission(Permission.SERVICE_UPDATE) is True

        # Editor should NOT have delete permission
        assert editor.has_permission(Permission.SERVICE_DELETE) is False

    def test_user_has_any_permission(self):
        """Test checking if user has any of multiple permissions"""
        viewer = User(id=1, username="viewer", email="viewer@example.com", password_hash="hash", role=Role.VIEWER)

        # Viewer has SERVICE_READ
        assert (
            viewer.has_any_permission([Permission.SERVICE_READ, Permission.SERVICE_DELETE, Permission.SERVICE_UPDATE])
            is True
        )

        # Viewer doesn't have any of these
        assert (
            viewer.has_any_permission([Permission.SERVICE_DELETE, Permission.SERVICE_UPDATE, Permission.USER_CREATE])
            is False
        )

    def test_user_has_all_permissions(self):
        """Test checking if user has all specified permissions"""
        admin = User(id=1, username="admin", email="admin@example.com", password_hash="hash", role=Role.ADMIN)

        # Admin has all permissions
        assert (
            admin.has_all_permissions([Permission.SERVICE_CREATE, Permission.SERVICE_READ, Permission.USER_DELETE])
            is True
        )

        viewer = User(id=2, username="viewer", email="viewer@example.com", password_hash="hash", role=Role.VIEWER)

        # Viewer doesn't have all these permissions
        assert (
            viewer.has_all_permissions([Permission.SERVICE_READ, Permission.SERVICE_UPDATE, Permission.SERVICE_DELETE])
            is False
        )

    def test_user_to_dict(self):
        """Test User serialization to dictionary"""
        user = User(id=1, username="testuser", email="test@example.com", password_hash="hash", role=Role.EDITOR)

        user_dict = user.to_dict()

        assert user_dict["id"] == 1
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["role"] == "editor"
        assert user_dict["is_active"] is True
        assert "password_hash" not in user_dict  # Should not expose password


class TestAuthManagerInitialization:
    """Tests for AuthManager initialization"""

    def test_auth_manager_creation(self, auth_manager):
        """Test AuthManager can be created"""
        assert auth_manager is not None
        assert auth_manager.bcrypt is not None
        assert auth_manager.login_manager is not None

    def test_database_initialization(self, temp_db_path, auth_manager):
        """Test database is initialized correctly"""
        import sqlite3

        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Check users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None

        # Check refresh_tokens table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='refresh_tokens'")
        assert cursor.fetchone() is not None

        # Check token_blacklist table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='token_blacklist'")
        assert cursor.fetchone() is not None

        conn.close()

    def test_default_admin_created(self, auth_manager):
        """Test default admin user is created"""
        admin = auth_manager.authenticate("admin", "admin")
        assert admin is not None
        assert admin.role == Role.ADMIN


class TestUserManagement:
    """Tests for user creation and management"""

    def test_create_user_success(self, auth_manager):
        """Test successful user creation"""
        user = auth_manager.create_user(
            username="newuser", email="newuser@example.com", password="Password123!", role=Role.VIEWER
        )

        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.role == Role.VIEWER
        assert user.password_hash is not None
        assert "Password123!" not in user.password_hash  # Password should be hashed

    def test_create_user_duplicate_username(self, auth_manager, test_user):
        """Test creating user with duplicate username fails"""
        duplicate = auth_manager.create_user(
            username="testuser", email="different@example.com", password="Password123!"
        )

        assert duplicate is None  # Should fail

    def test_create_user_duplicate_email(self, auth_manager, test_user):
        """Test creating user with duplicate email fails"""
        duplicate = auth_manager.create_user(
            username="differentuser", email="test@example.com", password="Password123!"
        )

        assert duplicate is None  # Should fail

    def test_create_user_with_different_roles(self, auth_manager):
        """Test creating users with different roles"""
        admin = auth_manager.create_user(
            username="admin2", email="admin2@example.com", password="AdminPass123!", role=Role.ADMIN
        )
        manager = auth_manager.create_user(
            username="manager", email="manager@example.com", password="ManagerPass123!", role=Role.MANAGER
        )
        editor = auth_manager.create_user(
            username="editor", email="editor@example.com", password="EditorPass123!", role=Role.EDITOR
        )
        viewer = auth_manager.create_user(
            username="viewer", email="viewer@example.com", password="ViewerPass123!", role=Role.VIEWER
        )

        assert admin.role == Role.ADMIN
        assert manager.role == Role.MANAGER
        assert editor.role == Role.EDITOR
        assert viewer.role == Role.VIEWER


class TestAuthentication:
    """Tests for user authentication"""

    def test_authenticate_success_with_username(self, auth_manager, test_user):
        """Test successful authentication with username"""
        authenticated = auth_manager.authenticate("testuser", "TestPass123!")

        assert authenticated is not None
        assert authenticated.username == "testuser"
        assert authenticated.email == "test@example.com"

    def test_authenticate_success_with_email(self, auth_manager, test_user):
        """Test successful authentication with email"""
        authenticated = auth_manager.authenticate("test@example.com", "TestPass123!")

        assert authenticated is not None
        assert authenticated.username == "testuser"

    def test_authenticate_wrong_password(self, auth_manager, test_user):
        """Test authentication with wrong password fails"""
        authenticated = auth_manager.authenticate("testuser", "WrongPassword!")

        assert authenticated is None

    def test_authenticate_nonexistent_user(self, auth_manager):
        """Test authentication with nonexistent user fails"""
        authenticated = auth_manager.authenticate("nonexistent", "password")

        assert authenticated is None

    def test_authenticate_inactive_user(self, auth_manager, temp_db_path):
        """Test authentication with inactive user fails"""
        import sqlite3

        # Create user and mark as inactive
        user = auth_manager.create_user(
            username="inactive", email="inactive@example.com", password="Password123!"
        )

        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user.id,))
        conn.commit()
        conn.close()

        authenticated = auth_manager.authenticate("inactive", "Password123!")
        assert authenticated is None


class TestLoadUser:
    """Tests for loading users"""

    def test_load_user_success(self, auth_manager, test_user):
        """Test loading existing user"""
        loaded = auth_manager.load_user(test_user.id)

        assert loaded is not None
        assert loaded.id == test_user.id
        assert loaded.username == test_user.username

    def test_load_user_nonexistent(self, auth_manager):
        """Test loading nonexistent user returns None"""
        loaded = auth_manager.load_user(99999)

        assert loaded is None

    def test_load_user_inactive(self, auth_manager, temp_db_path):
        """Test loading inactive user returns None"""
        import sqlite3

        # Create user and mark as inactive
        user = auth_manager.create_user(
            username="inactive2", email="inactive2@example.com", password="Password123!"
        )

        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user.id,))
        conn.commit()
        conn.close()

        loaded = auth_manager.load_user(user.id)
        assert loaded is None


class TestJWTTokens:
    """Tests for JWT token generation and verification"""

    def test_generate_token(self, auth_manager, test_user):
        """Test JWT token generation"""
        secret_key = "test_secret_key_12345"
        token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    def test_verify_token_success(self, auth_manager, test_user):
        """Test successful token verification"""
        secret_key = "test_secret_key_12345"
        token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)

        payload = auth_manager.verify_token(token, secret_key)

        assert payload is not None
        assert payload["user_id"] == test_user.id
        assert payload["username"] == test_user.username
        assert payload["role"] == test_user.role.value

    def test_verify_token_invalid(self, auth_manager):
        """Test verification of invalid token"""
        secret_key = "test_secret_key_12345"
        invalid_token = "invalid.token.here"

        payload = auth_manager.verify_token(invalid_token, secret_key)

        assert payload is None

    def test_verify_token_expired(self, auth_manager, test_user):
        """Test verification of expired token"""
        secret_key = "test_secret_key_12345"
        token = auth_manager.generate_token(test_user, secret_key, expires_in=1)  # 1 second

        time.sleep(2)  # Wait for expiration

        payload = auth_manager.verify_token(token, secret_key)

        assert payload is None  # Should be expired

    def test_verify_token_wrong_secret(self, auth_manager, test_user):
        """Test verification with wrong secret key"""
        secret_key = "test_secret_key_12345"
        wrong_secret = "wrong_secret_key"

        token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)
        payload = auth_manager.verify_token(token, wrong_secret)

        assert payload is None


class TestRefreshTokens:
    """Tests for refresh token functionality"""

    def test_generate_refresh_token(self, auth_manager, test_user):
        """Test refresh token generation"""
        secret_key = "test_secret_key_12345"
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=2592000)

        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 50

    def test_verify_refresh_token_success(self, auth_manager, test_user):
        """Test successful refresh token verification"""
        secret_key = "test_secret_key_12345"
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=2592000)

        user = auth_manager.verify_refresh_token(refresh_token, secret_key)

        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    def test_verify_refresh_token_expired(self, auth_manager, test_user):
        """Test verification of expired refresh token"""
        secret_key = "test_secret_key_12345"
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=1)  # 1 second

        time.sleep(2)  # Wait for expiration

        user = auth_manager.verify_refresh_token(refresh_token, secret_key)

        assert user is None

    def test_revoke_refresh_token(self, auth_manager, test_user):
        """Test revoking refresh token"""
        secret_key = "test_secret_key_12345"
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=2592000)

        # Revoke token
        result = auth_manager.revoke_refresh_token(refresh_token)
        assert result is True

        # Verify token is revoked
        user = auth_manager.verify_refresh_token(refresh_token, secret_key)
        assert user is None

    def test_revoke_all_user_tokens(self, auth_manager, test_user):
        """Test revoking all tokens for a user"""
        secret_key = "test_secret_key_12345"

        # Generate multiple refresh tokens
        token1 = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=2592000)
        token2 = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=2592000)

        # Revoke all tokens
        result = auth_manager.revoke_all_user_tokens(test_user.id)
        assert result is True

        # Verify both tokens are revoked
        assert auth_manager.verify_refresh_token(token1, secret_key) is None
        assert auth_manager.verify_refresh_token(token2, secret_key) is None


class TestTokenBlacklist:
    """Tests for token blacklisting"""

    def test_blacklist_token(self, auth_manager, test_user):
        """Test adding token to blacklist"""
        secret_key = "test_secret_key_12345"
        token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)

        result = auth_manager.blacklist_token(token, reason="test", expires_in=3600)

        assert result is True

    def test_is_token_blacklisted(self, auth_manager, test_user):
        """Test checking if token is blacklisted"""
        secret_key = "test_secret_key_12345"
        token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)

        # Not blacklisted initially
        assert auth_manager.is_token_blacklisted(token) is False

        # Blacklist it
        auth_manager.blacklist_token(token, reason="test", expires_in=3600)

        # Should be blacklisted now
        assert auth_manager.is_token_blacklisted(token) is True

    def test_blacklist_duplicate_token(self, auth_manager, test_user):
        """Test blacklisting same token twice"""
        secret_key = "test_secret_key_12345"
        token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)

        # First blacklist
        result1 = auth_manager.blacklist_token(token, reason="test1", expires_in=3600)
        assert result1 is True

        # Second blacklist (implementation allows duplicates, returns True)
        result2 = auth_manager.blacklist_token(token, reason="test2", expires_in=3600)
        # Note: Current implementation returns True even for duplicates
        assert result2 is True

        # Token should still be blacklisted
        assert auth_manager.is_token_blacklisted(token) is True


class TestLogout:
    """Tests for logout functionality"""

    def test_logout_success(self, auth_manager, test_user):
        """Test successful logout"""
        secret_key = "test_secret_key_12345"
        access_token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key, expires_in=2592000)

        result = auth_manager.logout(access_token, refresh_token)

        assert result is True

        # Both tokens should be blacklisted/revoked
        assert auth_manager.is_token_blacklisted(access_token) is True
        assert auth_manager.verify_refresh_token(refresh_token, secret_key) is None

    def test_logout_access_token_only(self, auth_manager, test_user):
        """Test logout with only access token"""
        secret_key = "test_secret_key_12345"
        access_token = auth_manager.generate_token(test_user, secret_key, expires_in=3600)

        result = auth_manager.logout(access_token, None)

        assert result is True
        assert auth_manager.is_token_blacklisted(access_token) is True


class TestSecurity:
    """Security-related tests"""

    def test_password_hashing(self, auth_manager):
        """Test password is properly hashed"""
        password = "PlainTextPassword123!"
        user = auth_manager.create_user(
            username="hashtest", email="hashtest@example.com", password=password, role=Role.VIEWER
        )

        assert user.password_hash != password
        assert password not in user.password_hash
        assert len(user.password_hash) > len(password)

    def test_bcrypt_hashing(self, auth_manager):
        """Test bcrypt is used for hashing"""
        password = "TestPassword123!"
        hashed = auth_manager.bcrypt.generate_password_hash(password).decode("utf-8")

        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_password_verification(self, auth_manager):
        """Test password verification is correct"""
        password = "TestPassword123!"
        hashed = auth_manager.bcrypt.generate_password_hash(password).decode("utf-8")

        # Correct password
        assert auth_manager.bcrypt.check_password_hash(hashed, password) is True

        # Wrong password
        assert auth_manager.bcrypt.check_password_hash(hashed, "WrongPassword") is False


class TestPermissionsAndRoles:
    """Tests for permission and role system"""

    def test_admin_has_all_permissions(self):
        """Test admin role has all permissions"""
        from src.core.auth import ROLE_PERMISSIONS

        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]

        # Admin should have all permissions
        assert Permission.SERVICE_CREATE in admin_perms
        assert Permission.SERVICE_DELETE in admin_perms
        assert Permission.USER_CREATE in admin_perms
        assert Permission.USER_DELETE in admin_perms
        assert Permission.SYSTEM_CONFIG in admin_perms

    def test_viewer_limited_permissions(self):
        """Test viewer role has limited permissions"""
        from src.core.auth import ROLE_PERMISSIONS

        viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]

        # Viewer should only have read permissions
        assert Permission.SERVICE_READ in viewer_perms
        assert Permission.ANALYTICS_VIEW in viewer_perms

        # Viewer should NOT have write/delete permissions
        assert Permission.SERVICE_CREATE not in viewer_perms
        assert Permission.SERVICE_DELETE not in viewer_perms
        assert Permission.USER_DELETE not in viewer_perms

    def test_manager_permissions(self):
        """Test manager role has appropriate permissions"""
        from src.core.auth import ROLE_PERMISSIONS

        manager_perms = ROLE_PERMISSIONS[Role.MANAGER]

        # Manager can manage services
        assert Permission.SERVICE_CREATE in manager_perms
        assert Permission.SERVICE_DELETE in manager_perms

        # Manager can update users but not delete
        assert Permission.USER_UPDATE in manager_perms

        # Manager cannot access system config
        assert Permission.SYSTEM_CONFIG not in manager_perms


# Integration tests for decorators would require Flask context
# These are basic structure tests
class TestDecorators:
    """Basic tests for auth decorators"""

    def test_login_required_decorator_exists(self):
        """Test login_required decorator is defined"""
        assert login_required is not None
        assert callable(login_required)

    def test_permission_required_decorator_exists(self):
        """Test permission_required decorator is defined"""
        assert permission_required is not None
        assert callable(permission_required)

    def test_role_required_decorator_exists(self):
        """Test role_required decorator is defined"""
        assert role_required is not None
        assert callable(role_required)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
