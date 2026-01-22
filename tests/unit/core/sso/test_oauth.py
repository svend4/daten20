"""Comprehensive tests for OAuth 2.0 / OpenID Connect module"""

import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# Mock jwt and requests before importing
mock_jwt = Mock()
mock_requests = Mock()

sys.modules["jwt"] = mock_jwt
sys.modules["requests"] = mock_requests

from src.core.sso.oauth import (
    GITHUB_PROVIDER,
    GOOGLE_PROVIDER,
    MICROSOFT_PROVIDER,
    OAuthClient,
    OAuthGrantType,
    OAuthManager,
    OAuthProvider,
    OAuthResponseType,
    OAuthScope,
    OAuthState,
    OAuthToken,
    OAuthTokenType,
    UserInfo,
    configure_oauth_manager,
    get_oauth_manager,
)


class TestOAuthGrantType:
    """Test OAuthGrantType enum"""

    def test_authorization_code_grant(self):
        """Test AUTHORIZATION_CODE grant type"""
        assert OAuthGrantType.AUTHORIZATION_CODE == "authorization_code"

    def test_refresh_token_grant(self):
        """Test REFRESH_TOKEN grant type"""
        assert OAuthGrantType.REFRESH_TOKEN == "refresh_token"

    def test_client_credentials_grant(self):
        """Test CLIENT_CREDENTIALS grant type"""
        assert OAuthGrantType.CLIENT_CREDENTIALS == "client_credentials"

    def test_password_grant(self):
        """Test PASSWORD grant type"""
        assert OAuthGrantType.PASSWORD == "password"


class TestOAuthResponseType:
    """Test OAuthResponseType enum"""

    def test_code_response_type(self):
        """Test CODE response type"""
        assert OAuthResponseType.CODE == "code"

    def test_token_response_type(self):
        """Test TOKEN response type"""
        assert OAuthResponseType.TOKEN == "token"

    def test_id_token_response_type(self):
        """Test ID_TOKEN response type"""
        assert OAuthResponseType.ID_TOKEN == "id_token"


class TestOAuthTokenType:
    """Test OAuthTokenType enum"""

    def test_bearer_token_type(self):
        """Test BEARER token type"""
        assert OAuthTokenType.BEARER == "Bearer"

    def test_mac_token_type(self):
        """Test MAC token type"""
        assert OAuthTokenType.MAC == "MAC"


class TestOAuthScope:
    """Test OAuthScope dataclass"""

    def test_scope_creation(self):
        """Test creating OAuth scope"""
        scope = OAuthScope(name="read:user", description="Read user information")
        assert scope.name == "read:user"
        assert scope.description == "Read user information"
        assert scope.required is False

    def test_scope_required(self):
        """Test required scope"""
        scope = OAuthScope(name="openid", description="OpenID scope", required=True)
        assert scope.required is True


class TestOAuthProvider:
    """Test OAuthProvider dataclass"""

    def test_provider_creation_minimal(self):
        """Test creating provider with minimal parameters"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )
        assert provider.name == "Test"
        assert provider.client_id == "client123"

    def test_provider_default_values(self):
        """Test provider default values"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )
        assert provider.userinfo_endpoint is None
        assert provider.revocation_endpoint is None
        assert provider.response_type == OAuthResponseType.CODE
        assert provider.grant_type == OAuthGrantType.AUTHORIZATION_CODE
        assert provider.use_pkce is True
        assert provider.active is True

    def test_provider_with_openid_connect(self):
        """Test provider with OpenID Connect endpoints"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            userinfo_endpoint="https://auth.test.com/userinfo",
            jwks_uri="https://auth.test.com/jwks",
            issuer="https://auth.test.com",
            scopes=["openid", "email", "profile"],
        )
        assert provider.userinfo_endpoint is not None
        assert provider.jwks_uri is not None
        assert provider.issuer is not None
        assert len(provider.scopes) == 3

    def test_provider_without_pkce(self):
        """Test provider without PKCE"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            use_pkce=False,
        )
        assert provider.use_pkce is False


class TestOAuthState:
    """Test OAuthState dataclass"""

    def test_state_creation(self):
        """Test creating OAuth state"""
        state = OAuthState(state="random_state", redirect_uri="https://app.test.com/callback")
        assert state.state == "random_state"
        assert state.redirect_uri == "https://app.test.com/callback"
        assert state.code_verifier is None
        assert isinstance(state.created_at, datetime)

    def test_state_with_pkce(self):
        """Test state with PKCE verifier"""
        state = OAuthState(state="random_state", redirect_uri="https://app.test.com/callback", code_verifier="verifier123")
        assert state.code_verifier == "verifier123"

    def test_state_not_expired(self):
        """Test state not expired"""
        state = OAuthState(state="random_state", redirect_uri="https://app.test.com/callback")
        assert state.is_expired() is False

    def test_state_expired(self):
        """Test expired state"""
        expires_at = datetime.utcnow() - timedelta(minutes=1)
        state = OAuthState(
            state="random_state",
            redirect_uri="https://app.test.com/callback",
            expires_at=expires_at,
        )
        assert state.is_expired() is True


class TestOAuthToken:
    """Test OAuthToken dataclass"""

    def test_token_creation(self):
        """Test creating OAuth token"""
        token = OAuthToken(access_token="access123", token_type="Bearer")
        assert token.access_token == "access123"
        assert token.token_type == "Bearer"
        assert token.expires_in is None
        assert token.refresh_token is None

    def test_token_with_expiration(self):
        """Test token with expiration"""
        token = OAuthToken(access_token="access123", expires_in=3600)
        assert token.expires_in == 3600

    def test_token_not_expired(self):
        """Test token not expired"""
        token = OAuthToken(access_token="access123", expires_in=3600)
        assert token.is_expired() is False

    def test_token_expired(self):
        """Test expired token"""
        created_at = datetime.utcnow() - timedelta(hours=2)
        token = OAuthToken(access_token="access123", expires_in=3600, created_at=created_at)
        assert token.is_expired() is True

    def test_token_no_expiration(self):
        """Test token without expiration never expires"""
        token = OAuthToken(access_token="access123")
        assert token.is_expired() is False

    def test_time_until_expiry(self):
        """Test time until token expiry"""
        token = OAuthToken(access_token="access123", expires_in=3600)
        remaining = token.time_until_expiry()
        assert remaining is not None
        assert remaining.total_seconds() > 0

    def test_time_until_expiry_no_expiration(self):
        """Test time until expiry for token without expiration"""
        token = OAuthToken(access_token="access123")
        remaining = token.time_until_expiry()
        assert remaining is None

    def test_token_with_refresh_token(self):
        """Test token with refresh token"""
        token = OAuthToken(access_token="access123", refresh_token="refresh123")
        assert token.refresh_token == "refresh123"

    def test_token_with_id_token(self):
        """Test token with ID token (OpenID Connect)"""
        token = OAuthToken(access_token="access123", id_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
        assert token.id_token is not None


class TestUserInfo:
    """Test UserInfo dataclass"""

    def test_userinfo_creation(self):
        """Test creating user info"""
        userinfo = UserInfo(sub="user123", email="user@example.com")
        assert userinfo.sub == "user123"
        assert userinfo.email == "user@example.com"

    def test_userinfo_with_all_fields(self):
        """Test user info with all fields"""
        userinfo = UserInfo(
            sub="user123",
            email="user@example.com",
            email_verified=True,
            name="John Doe",
            given_name="John",
            family_name="Doe",
            picture="https://example.com/photo.jpg",
            locale="en_US",
            raw_data={"custom_field": "value"},
        )
        assert userinfo.email_verified is True
        assert userinfo.name == "John Doe"
        assert userinfo.given_name == "John"
        assert userinfo.family_name == "Doe"
        assert userinfo.picture is not None
        assert userinfo.locale == "en_US"
        assert "custom_field" in userinfo.raw_data


class TestOAuthClient:
    """Test OAuthClient class"""

    def setup_method(self):
        """Setup OAuth client for testing"""
        self.provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            userinfo_endpoint="https://auth.test.com/userinfo",
            scopes=["read:user", "write:user"],
        )
        self.client = OAuthClient(self.provider, "https://app.test.com/callback")

    def test_client_initialization(self):
        """Test OAuth client initialization"""
        assert self.client.provider == self.provider
        assert self.client.redirect_uri == "https://app.test.com/callback"
        assert self.client.states == {}

    def test_generate_state(self):
        """Test state generation"""
        state = self.client.generate_state()
        assert len(state) > 0
        assert isinstance(state, str)

    def test_generate_code_verifier(self):
        """Test code verifier generation"""
        verifier = self.client.generate_code_verifier()
        assert len(verifier) > 0
        assert isinstance(verifier, str)

    def test_generate_code_challenge(self):
        """Test code challenge generation from verifier"""
        verifier = "test_verifier_12345"
        challenge = self.client.generate_code_challenge(verifier)
        assert len(challenge) > 0
        assert isinstance(challenge, str)
        # Challenge should be different from verifier
        assert challenge != verifier

    def test_create_authorization_url_basic(self):
        """Test creating basic authorization URL"""
        url = self.client.create_authorization_url()
        assert "https://auth.test.com/auth?" in url
        assert "client_id=client123" in url
        assert "response_type=code" in url
        assert "redirect_uri=" in url
        assert "state=" in url

    def test_create_authorization_url_with_scopes(self):
        """Test creating authorization URL with custom scopes"""
        url = self.client.create_authorization_url(scopes=["openid", "email"])
        assert "scope=openid+email" in url or "scope=openid%20email" in url

    def test_create_authorization_url_with_pkce(self):
        """Test creating authorization URL with PKCE"""
        url = self.client.create_authorization_url()
        assert "code_challenge=" in url
        assert "code_challenge_method=S256" in url

    def test_create_authorization_url_stores_state(self):
        """Test that creating URL stores state"""
        initial_states = len(self.client.states)
        url = self.client.create_authorization_url()
        assert len(self.client.states) == initial_states + 1

    def test_verify_state_valid(self):
        """Test verifying valid state"""
        url = self.client.create_authorization_url()
        # Extract state from URL
        state = url.split("state=")[1].split("&")[0]
        assert self.client.verify_state(state) is True

    def test_verify_state_invalid(self):
        """Test verifying invalid state"""
        assert self.client.verify_state("invalid_state") is False

    def test_verify_state_expired(self):
        """Test verifying expired state"""
        state_value = "expired_state"
        expires_at = datetime.utcnow() - timedelta(minutes=1)
        oauth_state = OAuthState(
            state=state_value,
            redirect_uri=self.client.redirect_uri,
            expires_at=expires_at,
        )
        self.client.states[state_value] = oauth_state

        assert self.client.verify_state(state_value) is False
        # Expired state should be removed
        assert state_value not in self.client.states

    def test_exchange_code_for_token_success(self):
        """Test successful code exchange"""
        # Create state
        url = self.client.create_authorization_url()
        state = url.split("state=")[1].split("&")[0]

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "access123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh123",
        }
        mock_requests.post = Mock(return_value=mock_response)

        token = self.client.exchange_code_for_token("auth_code", state)

        assert token.access_token == "access123"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "refresh123"

    def test_exchange_code_for_token_invalid_state(self):
        """Test code exchange with invalid state"""
        with pytest.raises(ValueError, match="Invalid or expired state"):
            self.client.exchange_code_for_token("auth_code", "invalid_state")

    def test_exchange_code_for_token_failed(self):
        """Test failed code exchange"""
        # Create state
        url = self.client.create_authorization_url()
        state = url.split("state=")[1].split("&")[0]

        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid code"
        mock_requests.post = Mock(return_value=mock_response)

        with pytest.raises(ValueError, match="Token exchange failed"):
            self.client.exchange_code_for_token("invalid_code", state)

    def test_refresh_access_token_success(self):
        """Test successful token refresh"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_requests.post = Mock(return_value=mock_response)

        token = self.client.refresh_access_token("refresh123")

        assert token.access_token == "new_access123"
        assert token.expires_in == 3600

    def test_refresh_access_token_failed(self):
        """Test failed token refresh"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"
        mock_requests.post = Mock(return_value=mock_response)

        with pytest.raises(ValueError, match="Token refresh failed"):
            self.client.refresh_access_token("invalid_refresh")

    def test_get_user_info_success(self):
        """Test getting user info successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "user123",
            "email": "user@example.com",
            "email_verified": True,
            "name": "John Doe",
        }
        mock_requests.get = Mock(return_value=mock_response)

        userinfo = self.client.get_user_info("access123")

        assert userinfo.sub == "user123"
        assert userinfo.email == "user@example.com"
        assert userinfo.email_verified is True
        assert userinfo.name == "John Doe"

    def test_get_user_info_no_endpoint(self):
        """Test getting user info when provider doesn't support it"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            userinfo_endpoint=None,
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        with pytest.raises(ValueError, match="does not support userinfo endpoint"):
            client.get_user_info("access123")

    def test_get_user_info_failed(self):
        """Test failed user info request"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_requests.get = Mock(return_value=mock_response)

        with pytest.raises(ValueError, match="Failed to get user info"):
            self.client.get_user_info("invalid_token")

    def test_decode_id_token_success(self):
        """Test successful ID token decoding"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            issuer="https://auth.test.com",
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        # Mock jwt.decode
        mock_jwt.decode = Mock(
            return_value={
                "iss": "https://auth.test.com",
                "aud": "client123",
                "sub": "user123",
                "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            }
        )

        claims = client.decode_id_token("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

        assert claims["sub"] == "user123"
        assert claims["iss"] == "https://auth.test.com"

    def test_decode_id_token_no_issuer(self):
        """Test decoding ID token when issuer not configured"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            issuer=None,
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        with pytest.raises(ValueError, match="Provider issuer not configured"):
            client.decode_id_token("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

    def test_decode_id_token_invalid_issuer(self):
        """Test decoding ID token with invalid issuer"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            issuer="https://auth.test.com",
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        mock_jwt.decode = Mock(return_value={"iss": "https://evil.com", "aud": "client123"})

        with pytest.raises(ValueError, match="Invalid issuer"):
            client.decode_id_token("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

    def test_decode_id_token_invalid_audience(self):
        """Test decoding ID token with invalid audience"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            issuer="https://auth.test.com",
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        mock_jwt.decode = Mock(
            return_value={"iss": "https://auth.test.com", "aud": "wrong_client"}
        )

        with pytest.raises(ValueError, match="Invalid audience"):
            client.decode_id_token("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

    def test_decode_id_token_expired(self):
        """Test decoding expired ID token"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            issuer="https://auth.test.com",
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        expired_timestamp = int((datetime.utcnow() - timedelta(hours=1)).timestamp())
        mock_jwt.decode = Mock(
            return_value={
                "iss": "https://auth.test.com",
                "aud": "client123",
                "exp": expired_timestamp,
            }
        )

        with pytest.raises(ValueError, match="Token expired"):
            client.decode_id_token("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

    def test_revoke_token_success(self):
        """Test successful token revocation"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            revocation_endpoint="https://auth.test.com/revoke",
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post = Mock(return_value=mock_response)

        result = client.revoke_token("access123")
        assert result is True

    def test_revoke_token_no_endpoint(self):
        """Test revoking token when provider doesn't support it"""
        result = self.client.revoke_token("access123")
        assert result is False

    def test_revoke_token_failed(self):
        """Test failed token revocation"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
            revocation_endpoint="https://auth.test.com/revoke",
        )
        client = OAuthClient(provider, "https://app.test.com/callback")

        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post = Mock(return_value=mock_response)

        result = client.revoke_token("invalid_token")
        assert result is False


class TestPreConfiguredProviders:
    """Test pre-configured OAuth providers"""

    def test_google_provider(self):
        """Test Google provider configuration"""
        assert GOOGLE_PROVIDER.name == "Google"
        assert "google" in GOOGLE_PROVIDER.authorization_endpoint.lower()
        assert GOOGLE_PROVIDER.use_pkce is True
        assert "openid" in GOOGLE_PROVIDER.scopes

    def test_microsoft_provider(self):
        """Test Microsoft provider configuration"""
        assert MICROSOFT_PROVIDER.name == "Microsoft"
        assert "microsoft" in MICROSOFT_PROVIDER.authorization_endpoint.lower()
        assert MICROSOFT_PROVIDER.use_pkce is True

    def test_github_provider(self):
        """Test GitHub provider configuration"""
        assert GITHUB_PROVIDER.name == "GitHub"
        assert "github" in GITHUB_PROVIDER.authorization_endpoint.lower()
        assert GITHUB_PROVIDER.use_pkce is False


class TestOAuthManager:
    """Test OAuthManager class"""

    def setup_method(self):
        """Setup OAuth manager for testing"""
        self.manager = OAuthManager()

    def test_manager_initialization(self):
        """Test OAuth manager initialization"""
        assert self.manager.providers == {}
        assert self.manager.clients == {}

    def test_register_provider(self):
        """Test registering provider"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )
        self.manager.register_provider(provider)

        assert len(self.manager.providers) == 1
        assert "Test" in self.manager.providers

    def test_get_provider(self):
        """Test getting provider"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )
        self.manager.register_provider(provider)

        retrieved = self.manager.get_provider("Test")
        assert retrieved == provider

    def test_get_nonexistent_provider(self):
        """Test getting non-existent provider"""
        result = self.manager.get_provider("NonExistent")
        assert result is None

    def test_list_providers(self):
        """Test listing all providers"""
        provider1 = OAuthProvider(
            name="Provider1",
            client_id="client1",
            client_secret="secret1",
            authorization_endpoint="https://auth1.test.com/auth",
            token_endpoint="https://auth1.test.com/token",
        )
        provider2 = OAuthProvider(
            name="Provider2",
            client_id="client2",
            client_secret="secret2",
            authorization_endpoint="https://auth2.test.com/auth",
            token_endpoint="https://auth2.test.com/token",
            active=False,
        )

        self.manager.register_provider(provider1)
        self.manager.register_provider(provider2)

        active_providers = self.manager.list_providers()
        assert len(active_providers) == 1
        assert active_providers[0].name == "Provider1"

    def test_create_client_success(self):
        """Test creating OAuth client"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )
        self.manager.register_provider(provider)

        client = self.manager.create_client("Test", "https://app.test.com/callback")

        assert client.provider == provider
        assert client.redirect_uri == "https://app.test.com/callback"

    def test_create_client_provider_not_found(self):
        """Test creating client for non-existent provider"""
        with pytest.raises(ValueError, match="Provider not found"):
            self.manager.create_client("NonExistent", "https://app.test.com/callback")

    def test_create_client_caching(self):
        """Test that clients are cached"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )
        self.manager.register_provider(provider)

        client1 = self.manager.create_client("Test", "https://app.test.com/callback")
        client2 = self.manager.create_client("Test", "https://app.test.com/callback")

        assert client1 is client2


class TestGlobalFunctions:
    """Test global OAuth functions"""

    def test_get_oauth_manager_creates_instance(self):
        """Test get_oauth_manager creates global instance"""
        # Reset global instance
        import src.core.sso.oauth as oauth_module

        oauth_module._oauth_manager = None

        manager = get_oauth_manager()
        assert manager is not None
        assert isinstance(manager, OAuthManager)

    def test_get_oauth_manager_returns_singleton(self):
        """Test get_oauth_manager returns same instance"""
        manager1 = get_oauth_manager()
        manager2 = get_oauth_manager()
        assert manager1 is manager2

    def test_configure_oauth_manager(self):
        """Test configure_oauth_manager"""
        provider = OAuthProvider(
            name="Test",
            client_id="client123",
            client_secret="secret",
            authorization_endpoint="https://auth.test.com/auth",
            token_endpoint="https://auth.test.com/token",
        )

        configure_oauth_manager([provider])

        manager = get_oauth_manager()
        retrieved = manager.get_provider("Test")
        assert retrieved == provider
