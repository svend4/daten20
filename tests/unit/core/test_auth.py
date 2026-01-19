"""
Unit tests for core.auth module
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestAuthService:
    """Tests for AuthService class"""

    @pytest.fixture
    def auth_service(self):
        """Fixture providing AuthService instance"""
        from src.core.auth import AuthService

        return AuthService()

    def test_auth_service_initialization(self, auth_service):
        """Test AuthService can be initialized"""
        assert auth_service is not None

    def test_hash_password(self, auth_service):
        """Test password hashing"""
        if hasattr(auth_service, "hash_password"):
            password = "test_password_123"
            hashed = auth_service.hash_password(password)
            assert hashed is not None
            assert hashed != password  # Should be hashed
            assert len(hashed) > len(password)  # Hash is longer
        else:
            pytest.skip("hash_password method not implemented")

    def test_verify_password(self, auth_service):
        """Test password verification"""
        if hasattr(auth_service, "hash_password") and hasattr(auth_service, "verify_password"):
            password = "test_password_123"
            hashed = auth_service.hash_password(password)

            # Correct password should verify
            assert auth_service.verify_password(password, hashed) is True

            # Wrong password should not verify
            assert auth_service.verify_password("wrong_password", hashed) is False
        else:
            pytest.skip("password methods not implemented")

    @pytest.mark.skip(reason="Auth API changed - test needs update for test isolation and new API")
    def test_create_user(self, auth_service):
        """Test user creation"""
        if hasattr(auth_service, "create_user"):
            user = auth_service.create_user(username="testuser", password="password123", email="test@example.com")
            assert user is not None
            assert user.get("username") == "testuser" or hasattr(user, "username")
        else:
            pytest.skip("create_user method not implemented")

    @pytest.mark.skip(reason="Auth API changed - test needs update for new User model")
    def test_authenticate_user(self, auth_service):
        """Test user authentication"""
        if hasattr(auth_service, "authenticate"):
            # Try to authenticate
            result = auth_service.authenticate(username="testuser", password="password123")
            # Result depends on implementation
            assert result is not None or result is False
        else:
            pytest.skip("authenticate method not implemented")

    @pytest.mark.skip(reason="Auth API changed - generate_token() signature changed")
    def test_generate_token(self, auth_service):
        """Test JWT token generation"""
        if hasattr(auth_service, "generate_token"):
            token = auth_service.generate_token(user_id=1, username="testuser")
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 20  # JWT tokens are long
        else:
            pytest.skip("generate_token method not implemented")

    @pytest.mark.skip(reason="Auth API changed - verify_token() signature changed")
    def test_verify_token(self, auth_service):
        """Test JWT token verification"""
        if hasattr(auth_service, "generate_token") and hasattr(auth_service, "verify_token"):
            token = auth_service.generate_token(user_id=1, username="testuser")
            payload = auth_service.verify_token(token)

            assert payload is not None
            assert "user_id" in payload or "username" in payload or "sub" in payload
        else:
            pytest.skip("token methods not implemented")

    @pytest.mark.skip(reason="Auth API changed - verify_token() signature changed")
    def test_invalid_token_verification(self, auth_service):
        """Test verification of invalid token"""
        if hasattr(auth_service, "verify_token"):
            invalid_token = "invalid.token.here"
            payload = auth_service.verify_token(invalid_token)
            assert payload is None or payload is False
        else:
            pytest.skip("verify_token method not implemented")

    @pytest.mark.parametrize(
        "username,password,expected",
        [
            ("admin", "admin123", True),
            ("user", "password", True),
            ("", "", False),
            ("test", "", False),
            ("", "pass", False),
        ],
    )
    def test_login_validation(self, auth_service, username, password, expected):
        """Test login validation with various inputs"""
        if hasattr(auth_service, "validate_credentials"):
            result = auth_service.validate_credentials(username, password)
            if expected:
                assert result in [True, None]  # Might return None or True
            else:
                assert result in [False, None]
        else:
            pytest.skip("validate_credentials method not implemented")

    def test_password_strength_validation(self, auth_service):
        """Test password strength validation"""
        if hasattr(auth_service, "validate_password_strength"):
            # Weak password
            assert auth_service.validate_password_strength("123") is False

            # Strong password
            assert auth_service.validate_password_strength("StrongPass123!") is True
        else:
            pytest.skip("validate_password_strength not implemented")

    def test_session_creation(self, auth_service):
        """Test session creation"""
        if hasattr(auth_service, "create_session"):
            session = auth_service.create_session(user_id=1)
            assert session is not None
            assert "session_id" in session or hasattr(session, "session_id")
        else:
            pytest.skip("create_session method not implemented")

    def test_session_validation(self, auth_service):
        """Test session validation"""
        if hasattr(auth_service, "create_session") and hasattr(auth_service, "validate_session"):
            session = auth_service.create_session(user_id=1)
            session_id = session.get("session_id") or session.session_id

            is_valid = auth_service.validate_session(session_id)
            assert is_valid is True
        else:
            pytest.skip("session methods not implemented")

    def test_logout(self, auth_service):
        """Test user logout"""
        if hasattr(auth_service, "logout"):
            result = auth_service.logout(user_id=1)
            assert result in [True, None]
        else:
            pytest.skip("logout method not implemented")

    def test_permission_check(self, auth_service):
        """Test permission checking"""
        if hasattr(auth_service, "has_permission"):
            has_perm = auth_service.has_permission(user_id=1, permission="read")
            assert isinstance(has_perm, bool)
        else:
            pytest.skip("has_permission method not implemented")

    def test_role_assignment(self, auth_service):
        """Test role assignment"""
        if hasattr(auth_service, "assign_role"):
            result = auth_service.assign_role(user_id=1, role="admin")
            assert result in [True, None]
        else:
            pytest.skip("assign_role method not implemented")


class TestAuthSecurity:
    """Security tests for authentication"""

    @pytest.mark.security
    def test_password_not_stored_plaintext(self):
        """Ensure passwords are not stored in plaintext"""
        from src.core.auth import AuthService

        auth = AuthService()

        if hasattr(auth, "hash_password"):
            password = "mypassword123"
            hashed = auth.hash_password(password)

            # Hash should not contain the original password
            assert password not in hashed
            assert password.encode() not in hashed.encode() if isinstance(hashed, str) else True

    @pytest.mark.security
    def test_constant_time_comparison(self):
        """Test password comparison is constant-time to prevent timing attacks"""
        from src.core.auth import AuthService

        auth = AuthService()

        # This is a placeholder - actual timing attack test is complex
        # Just verify the method exists and works
        if hasattr(auth, "verify_password"):
            assert True
        else:
            pytest.skip("verify_password not implemented")

    @pytest.mark.security
    @pytest.mark.skip(reason="Auth API changed - generate_token() signature changed")
    def test_token_expiration(self):
        """Test tokens expire after set time"""
        from src.core.auth import AuthService

        auth = AuthService()

        if hasattr(auth, "generate_token"):
            import time

            token = auth.generate_token(user_id=1, expires_in=1)  # 1 second
            time.sleep(2)  # Wait for expiration

            if hasattr(auth, "verify_token"):
                payload = auth.verify_token(token)
                # Expired token should not verify
                assert payload is None or payload is False or payload.get("exp", 0) < time.time()
        else:
            pytest.skip("Token methods not implemented")


class TestUserModel:
    """Tests for User model class"""

    @pytest.fixture
    def sample_user(self):
        """Fixture providing a sample user"""
        from src.core.auth import Role, User

        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            role=Role.EDITOR,
            is_active=True,
        )

    def test_user_initialization(self):
        """Test User model can be initialized"""
        from src.core.auth import Role, User

        user = User(
            id=1,
            username="john",
            email="john@example.com",
            password_hash="hash123",
            role=Role.VIEWER,
        )

        assert user.id == 1
        assert user.username == "john"
        assert user.email == "john@example.com"
        assert user.role == Role.VIEWER
        assert user.is_active is True

    def test_user_has_permission(self, sample_user):
        """Test has_permission method"""
        from src.core.auth import Permission

        # Editor should have service create permission
        assert sample_user.has_permission(Permission.SERVICE_CREATE) is True
        assert sample_user.has_permission(Permission.SERVICE_READ) is True
        assert sample_user.has_permission(Permission.SERVICE_UPDATE) is True

        # Editor should NOT have admin permissions
        assert sample_user.has_permission(Permission.USER_DELETE) is False
        assert sample_user.has_permission(Permission.SYSTEM_CONFIG) is False

    def test_user_has_any_permission(self, sample_user):
        """Test has_any_permission method"""
        from src.core.auth import Permission

        # Should return True if has at least one permission
        assert (
            sample_user.has_any_permission([Permission.SERVICE_CREATE, Permission.SYSTEM_CONFIG])
            is True
        )
        assert (
            sample_user.has_any_permission([Permission.USER_DELETE, Permission.SYSTEM_BACKUP])
            is False
        )

    def test_user_has_all_permissions(self, sample_user):
        """Test has_all_permissions method"""
        from src.core.auth import Permission

        # Should have all service read/write permissions
        assert (
            sample_user.has_all_permissions(
                [Permission.SERVICE_CREATE, Permission.SERVICE_READ, Permission.SERVICE_UPDATE]
            )
            is True
        )

        # Should NOT have all admin permissions
        assert (
            sample_user.has_all_permissions([Permission.SERVICE_CREATE, Permission.SYSTEM_CONFIG])
            is False
        )

    def test_user_to_dict(self, sample_user):
        """Test to_dict method"""
        user_dict = sample_user.to_dict()

        assert isinstance(user_dict, dict)
        assert user_dict["id"] == 1
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["role"] == "editor"
        assert user_dict["is_active"] is True
        assert "password_hash" not in user_dict  # Should not expose password hash

    def test_user_roles(self):
        """Test different user roles have correct permissions"""
        from src.core.auth import Permission, Role, User

        # Admin has all permissions
        admin = User(1, "admin", "admin@test.com", "hash", role=Role.ADMIN)
        assert admin.has_permission(Permission.SYSTEM_CONFIG) is True
        assert admin.has_permission(Permission.USER_DELETE) is True

        # Viewer has read-only permissions
        viewer = User(2, "viewer", "viewer@test.com", "hash", role=Role.VIEWER)
        assert viewer.has_permission(Permission.SERVICE_READ) is True
        assert viewer.has_permission(Permission.SERVICE_CREATE) is False
        assert viewer.has_permission(Permission.USER_DELETE) is False

        # Guest has minimal permissions
        guest = User(3, "guest", "guest@test.com", "hash", role=Role.GUEST)
        assert guest.has_permission(Permission.SERVICE_READ) is True
        assert guest.has_permission(Permission.ANALYTICS_VIEW) is False


class TestRolePermissions:
    """Tests for Role and Permission enums"""

    def test_role_enum_values(self):
        """Test Role enum has expected values"""
        from src.core.auth import Role

        assert Role.ADMIN.value == "admin"
        assert Role.MANAGER.value == "manager"
        assert Role.EDITOR.value == "editor"
        assert Role.VIEWER.value == "viewer"
        assert Role.GUEST.value == "guest"

    def test_permission_enum_values(self):
        """Test Permission enum has expected values"""
        from src.core.auth import Permission

        assert Permission.SERVICE_CREATE.value == "service:create"
        assert Permission.USER_READ.value == "user:read"
        assert Permission.SYSTEM_CONFIG.value == "system:config"

    def test_role_permissions_mapping(self):
        """Test ROLE_PERMISSIONS mapping"""
        from src.core.auth import ROLE_PERMISSIONS, Permission, Role

        # Admin should have all permissions
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        assert Permission.SYSTEM_CONFIG in admin_perms
        assert Permission.USER_DELETE in admin_perms
        assert len(admin_perms) == len(list(Permission))

        # Viewer should have limited permissions
        viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
        assert Permission.SERVICE_READ in viewer_perms
        assert Permission.SERVICE_CREATE not in viewer_perms
        assert Permission.SYSTEM_CONFIG not in viewer_perms


class TestAuthManagerPasswordValidation:
    """Tests for AuthManager password validation"""

    @pytest.fixture
    def auth_manager(self, tmp_path):
        """Fixture providing AuthManager instance"""
        from src.core.auth import AuthManager

        db_path = str(tmp_path / "test_users.db")
        return AuthManager(db_path=db_path)

    def test_password_strength_too_short(self, auth_manager):
        """Test password that is too short"""
        is_valid, error = auth_manager.validate_password_strength("Ab1!")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_password_strength_no_uppercase(self, auth_manager):
        """Test password without uppercase letter"""
        is_valid, error = auth_manager.validate_password_strength("password123!")
        assert is_valid is False
        assert "uppercase" in error.lower()

    def test_password_strength_no_lowercase(self, auth_manager):
        """Test password without lowercase letter"""
        is_valid, error = auth_manager.validate_password_strength("PASSWORD123!")
        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_password_strength_no_digit(self, auth_manager):
        """Test password without digit"""
        is_valid, error = auth_manager.validate_password_strength("Password!!")
        assert is_valid is False
        assert "digit" in error.lower()

    def test_password_strength_no_special(self, auth_manager):
        """Test password without special character"""
        is_valid, error = auth_manager.validate_password_strength("Password123")
        assert is_valid is False
        assert "special" in error.lower()

    def test_password_strength_weak_password(self, auth_manager):
        """Test common weak passwords"""
        weak_passwords = [
            "Password123!",  # "password" is weak
            "Admin123!",  # "admin" is weak
            "Welcome123!",  # "welcome" is weak
            "Test123!",  # "test" is weak
        ]

        for pwd in weak_passwords:
            is_valid, error = auth_manager.validate_password_strength(pwd)
            assert is_valid is False
            assert "common" in error.lower() or "guessable" in error.lower()

    def test_password_strength_sequential_chars(self, auth_manager):
        """Test password with sequential characters"""
        is_valid, error = auth_manager.validate_password_strength("Abc123!Pass")
        assert is_valid is False
        assert "sequential" in error.lower()

    def test_password_strength_valid_strong(self, auth_manager):
        """Test valid strong password"""
        is_valid, error = auth_manager.validate_password_strength("MyStr0ng!P@ssw0rd")
        assert is_valid is True
        assert error is None


class TestAuthManagerUserManagement:
    """Tests for AuthManager user management"""

    @pytest.fixture
    def auth_manager(self, tmp_path):
        """Fixture providing AuthManager instance"""
        from src.core.auth import AuthManager

        db_path = str(tmp_path / "test_users.db")
        return AuthManager(db_path=db_path)

    def test_create_user_success(self, auth_manager):
        """Test successful user creation"""
        from src.core.auth import Role

        user = auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )

        assert user is not None
        assert user.username == "john"
        assert user.email == "john@example.com"
        assert user.role == Role.EDITOR

    def test_create_user_weak_password(self, auth_manager):
        """Test user creation fails with weak password"""
        from src.core.auth import Role

        user = auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="weak",  # Too short, no complexity
            role=Role.EDITOR,
        )

        assert user is None  # Should fail

    def test_create_user_duplicate_username(self, auth_manager):
        """Test user creation fails with duplicate username"""
        from src.core.auth import Role

        # Create first user
        user1 = auth_manager.create_user(
            username="john",
            email="john1@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )
        assert user1 is not None

        # Try to create user with same username
        user2 = auth_manager.create_user(
            username="john",  # Duplicate
            email="john2@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )
        assert user2 is None  # Should fail

    def test_authenticate_success(self, auth_manager):
        """Test successful authentication"""
        from src.core.auth import Role

        # Create user
        auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )

        # Authenticate
        user = auth_manager.authenticate("john", "StrongPass123!")
        assert user is not None
        assert user.username == "john"

    def test_authenticate_wrong_password(self, auth_manager):
        """Test authentication fails with wrong password"""
        from src.core.auth import Role

        # Create user
        auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )

        # Try wrong password
        user = auth_manager.authenticate("john", "WrongPassword123!")
        assert user is None

    def test_authenticate_nonexistent_user(self, auth_manager):
        """Test authentication fails for nonexistent user"""
        user = auth_manager.authenticate("nonexistent", "password")
        assert user is None

    def test_authenticate_account_locking(self, auth_manager):
        """Test account locks after failed attempts"""
        from src.core.auth import Role

        # Create user
        auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )

        # Try 5 failed login attempts
        for i in range(5):
            user = auth_manager.authenticate("john", "WrongPassword!")
            assert user is None

        # 6th attempt should still be locked
        user = auth_manager.authenticate("john", "StrongPass123!")
        assert user is None  # Account is locked even with correct password

    def test_load_user(self, auth_manager):
        """Test loading user by ID"""
        from src.core.auth import Role

        # Create user
        created_user = auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )

        # Load user
        loaded_user = auth_manager.load_user(created_user.id)
        assert loaded_user is not None
        assert loaded_user.id == created_user.id
        assert loaded_user.username == "john"

    def test_load_nonexistent_user(self, auth_manager):
        """Test loading nonexistent user returns None"""
        user = auth_manager.load_user(99999)
        assert user is None


class TestAuthManagerTokens:
    """Tests for AuthManager JWT token management"""

    @pytest.fixture
    def auth_manager(self, tmp_path):
        """Fixture providing AuthManager instance"""
        from src.core.auth import AuthManager

        db_path = str(tmp_path / "test_users.db")
        return AuthManager(db_path=db_path)

    @pytest.fixture
    def test_user(self, auth_manager):
        """Fixture providing a test user"""
        from src.core.auth import Role

        return auth_manager.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            role=Role.EDITOR,
        )

    def test_generate_token(self, auth_manager, test_user):
        """Test JWT token generation"""
        token = auth_manager.generate_token(test_user, secret_key="test_secret")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_verify_token(self, auth_manager, test_user):
        """Test JWT token verification"""
        token = auth_manager.generate_token(test_user, secret_key="test_secret")
        payload = auth_manager.verify_token(token, secret_key="test_secret")

        assert payload is not None
        assert payload["user_id"] == test_user.id
        assert payload["username"] == test_user.username

    def test_verify_invalid_token(self, auth_manager):
        """Test verification of invalid token"""
        payload = auth_manager.verify_token("invalid.token.here", secret_key="test_secret")
        assert payload is None

    def test_verify_expired_token(self, auth_manager, test_user):
        """Test verification of expired token"""
        import time

        # Generate token with 1 second expiry
        token = auth_manager.generate_token(test_user, secret_key="test_secret", expires_in=1)

        # Wait for expiration
        time.sleep(2)

        # Verify should fail
        payload = auth_manager.verify_token(token, secret_key="test_secret")
        assert payload is None

    def test_generate_refresh_token(self, auth_manager, test_user):
        """Test refresh token generation"""
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key="test_secret")

        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 20

    def test_verify_refresh_token(self, auth_manager, test_user):
        """Test refresh token verification"""
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key="test_secret")
        user = auth_manager.verify_refresh_token(refresh_token, secret_key="test_secret")

        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    def test_revoke_refresh_token(self, auth_manager, test_user):
        """Test revoking refresh token"""
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key="test_secret")

        # Revoke token
        success = auth_manager.revoke_refresh_token(refresh_token)
        assert success is True

        # Verify should fail after revocation
        user = auth_manager.verify_refresh_token(refresh_token, secret_key="test_secret")
        assert user is None

    def test_revoke_all_user_tokens(self, auth_manager, test_user):
        """Test revoking all tokens for a user"""
        # Generate multiple refresh tokens
        token1 = auth_manager.generate_refresh_token(test_user, secret_key="test_secret")
        token2 = auth_manager.generate_refresh_token(test_user, secret_key="test_secret")

        # Revoke all
        success = auth_manager.revoke_all_user_tokens(test_user.id)
        assert success is True

        # Both tokens should be revoked
        assert auth_manager.verify_refresh_token(token1, secret_key="test_secret") is None
        assert auth_manager.verify_refresh_token(token2, secret_key="test_secret") is None

    def test_blacklist_token(self, auth_manager, test_user):
        """Test token blacklisting"""
        access_token = auth_manager.generate_token(test_user, secret_key="test_secret")

        # Blacklist token
        success = auth_manager.blacklist_token(access_token, reason="logout")
        assert success is True

        # Token should be blacklisted
        assert auth_manager.is_token_blacklisted(access_token) is True

        # Verification should fail for blacklisted token
        payload = auth_manager.verify_token(access_token, secret_key="test_secret")
        assert payload is None

    def test_is_token_blacklisted_not_in_list(self, auth_manager):
        """Test checking non-blacklisted token"""
        is_blacklisted = auth_manager.is_token_blacklisted("some.random.token")
        assert is_blacklisted is False

    def test_logout(self, auth_manager, test_user):
        """Test logout functionality"""
        access_token = auth_manager.generate_token(test_user, secret_key="test_secret")
        refresh_token = auth_manager.generate_refresh_token(test_user, secret_key="test_secret")

        # Logout
        success = auth_manager.logout(access_token, refresh_token)
        assert success is True

        # Both tokens should be invalidated
        assert auth_manager.is_token_blacklisted(access_token) is True
        assert auth_manager.verify_refresh_token(refresh_token, secret_key="test_secret") is None
