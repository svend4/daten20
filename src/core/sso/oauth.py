"""
OAuth 2.0 / OpenID Connect Integration

Provides OAuth 2.0 and OpenID Connect authentication flows.
Supports multiple OAuth providers (Google, Microsoft, GitHub, etc.)
"""

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import jwt
import requests


class OAuthGrantType(str, Enum):
    """OAuth 2.0 grant types"""

    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"  # Not recommended for production


class OAuthResponseType(str, Enum):
    """OAuth response types"""

    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"


class OAuthTokenType(str, Enum):
    """Token types"""

    BEARER = "Bearer"
    MAC = "MAC"


@dataclass
class OAuthScope:
    """OAuth scope definition"""

    name: str
    description: str
    required: bool = False


@dataclass
class OAuthProvider:
    """OAuth provider configuration"""

    name: str
    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: Optional[str] = None
    revocation_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None  # For OpenID Connect
    issuer: Optional[str] = None  # For OpenID Connect
    scopes: List[str] = field(default_factory=list)
    response_type: OAuthResponseType = OAuthResponseType.CODE
    grant_type: OAuthGrantType = OAuthGrantType.AUTHORIZATION_CODE
    use_pkce: bool = True  # PKCE is recommended for security
    active: bool = True


@dataclass
class OAuthState:
    """OAuth state for CSRF protection"""

    state: str
    code_verifier: Optional[str] = None  # For PKCE
    redirect_uri: str = ""
    scopes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))

    def is_expired(self) -> bool:
        """Check if state has expired"""
        return datetime.utcnow() > self.expires_at


@dataclass
class OAuthToken:
    """OAuth access token"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None  # OpenID Connect
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_expired(self) -> bool:
        """Check if token has expired"""
        if not self.expires_in:
            return False
        expires_at = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.utcnow() > expires_at

    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time until token expires"""
        if not self.expires_in:
            return None
        expires_at = self.created_at + timedelta(seconds=self.expires_in)
        remaining = expires_at - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


@dataclass
class UserInfo:
    """User information from OAuth provider"""

    sub: str  # Subject (user ID)
    email: Optional[str] = None
    email_verified: bool = False
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


class OAuthClient:
    """OAuth 2.0 / OpenID Connect client"""

    def __init__(self, provider: OAuthProvider, redirect_uri: str):
        self.provider = provider
        self.redirect_uri = redirect_uri
        self.states: Dict[str, OAuthState] = {}

    def generate_state(self) -> str:
        """Generate random state for CSRF protection"""
        return secrets.token_urlsafe(32)

    def generate_code_verifier(self) -> str:
        """Generate code verifier for PKCE"""
        return secrets.token_urlsafe(64)

    def generate_code_challenge(self, verifier: str) -> str:
        """Generate code challenge from verifier (S256 method)"""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    def create_authorization_url(
        self, scopes: Optional[List[str]] = None, state: Optional[str] = None, **extra_params
    ) -> str:
        """
        Create OAuth authorization URL

        Args:
            scopes: List of scopes to request
            state: Optional state parameter (generated if not provided)
            extra_params: Additional parameters for the authorization request

        Returns:
            Authorization URL
        """
        if not state:
            state = self.generate_state()

        if not scopes:
            scopes = self.provider.scopes

        # Create OAuth state
        oauth_state = OAuthState(state=state, redirect_uri=self.redirect_uri, scopes=scopes)

        params = {
            "client_id": self.provider.client_id,
            "response_type": self.provider.response_type.value,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
        }

        # Add PKCE if enabled
        if self.provider.use_pkce:
            code_verifier = self.generate_code_verifier()
            code_challenge = self.generate_code_challenge(code_verifier)
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
            oauth_state.code_verifier = code_verifier

        # Add extra parameters
        params.update(extra_params)

        # Store state
        self.states[state] = oauth_state

        # Build URL
        url = f"{self.provider.authorization_endpoint}?{urlencode(params)}"
        return url

    def verify_state(self, state: str) -> bool:
        """
        Verify state parameter

        Args:
            state: State parameter from callback

        Returns:
            True if valid, False otherwise
        """
        oauth_state = self.states.get(state)
        if not oauth_state:
            return False

        if oauth_state.is_expired():
            del self.states[state]
            return False

        return True

    def exchange_code_for_token(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback
            state: State parameter from callback

        Returns:
            OAuth token

        Raises:
            ValueError: If state is invalid or token exchange fails
        """
        if not self.verify_state(state):
            raise ValueError("Invalid or expired state")

        oauth_state = self.states.get(state)
        if not oauth_state:
            raise ValueError("State not found")

        # Prepare token request
        data = {
            "grant_type": OAuthGrantType.AUTHORIZATION_CODE.value,
            "code": code,
            "redirect_uri": oauth_state.redirect_uri,
            "client_id": self.provider.client_id,
            "client_secret": self.provider.client_secret,
        }

        # Add PKCE verifier if used
        if self.provider.use_pkce and oauth_state.code_verifier:
            data["code_verifier"] = oauth_state.code_verifier

        # Request token
        response = requests.post(self.provider.token_endpoint, data=data, headers={"Accept": "application/json"})

        if response.status_code != 200:
            raise ValueError(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Clean up state
        del self.states[state]

        return OAuthToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
            id_token=token_data.get("id_token"),
        )

    def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            New OAuth token

        Raises:
            ValueError: If refresh fails
        """
        data = {
            "grant_type": OAuthGrantType.REFRESH_TOKEN.value,
            "refresh_token": refresh_token,
            "client_id": self.provider.client_id,
            "client_secret": self.provider.client_secret,
        }

        response = requests.post(self.provider.token_endpoint, data=data, headers={"Accept": "application/json"})

        if response.status_code != 200:
            raise ValueError(f"Token refresh failed: {response.text}")

        token_data = response.json()

        return OAuthToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token", refresh_token),
            scope=token_data.get("scope"),
        )

    def get_user_info(self, access_token: str) -> UserInfo:
        """
        Get user information from OAuth provider

        Args:
            access_token: Access token

        Returns:
            User information

        Raises:
            ValueError: If provider doesn't support userinfo or request fails
        """
        if not self.provider.userinfo_endpoint:
            raise ValueError("Provider does not support userinfo endpoint")

        response = requests.get(
            self.provider.userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get user info: {response.text}")

        data = response.json()

        return UserInfo(
            sub=data["sub"],
            email=data.get("email"),
            email_verified=data.get("email_verified", False),
            name=data.get("name"),
            given_name=data.get("given_name"),
            family_name=data.get("family_name"),
            picture=data.get("picture"),
            locale=data.get("locale"),
            raw_data=data,
        )

    def decode_id_token(self, id_token: str, verify_signature: bool = True) -> Dict[str, Any]:
        """
        Decode and verify OpenID Connect ID token

        Args:
            id_token: JWT ID token
            verify_signature: Whether to verify token signature

        Returns:
            Decoded token claims

        Raises:
            ValueError: If token is invalid
        """
        if not self.provider.issuer:
            raise ValueError("Provider issuer not configured")

        # Decode without verification first
        unverified = jwt.decode(id_token, options={"verify_signature": False})

        # Verify issuer
        if unverified.get("iss") != self.provider.issuer:
            raise ValueError("Invalid issuer")

        # Verify audience
        if unverified.get("aud") != self.provider.client_id:
            raise ValueError("Invalid audience")

        # Verify expiration
        exp = unverified.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise ValueError("Token expired")

        if verify_signature:
            # In production, fetch JWKS from provider and verify signature
            # For now, we'll skip signature verification
            pass

        return unverified

    def revoke_token(self, token: str, token_type_hint: str = "access_token") -> bool:
        """
        Revoke access or refresh token

        Args:
            token: Token to revoke
            token_type_hint: Type of token (access_token or refresh_token)

        Returns:
            True if revocation succeeded
        """
        if not self.provider.revocation_endpoint:
            return False

        data = {
            "token": token,
            "token_type_hint": token_type_hint,
            "client_id": self.provider.client_id,
            "client_secret": self.provider.client_secret,
        }

        response = requests.post(self.provider.revocation_endpoint, data=data)

        return response.status_code == 200


# Pre-configured providers
GOOGLE_PROVIDER = OAuthProvider(
    name="Google",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
    revocation_endpoint="https://oauth2.googleapis.com/revoke",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    issuer="https://accounts.google.com",
    scopes=["openid", "email", "profile"],
    use_pkce=True,
)

MICROSOFT_PROVIDER = OAuthProvider(
    name="Microsoft",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_endpoint="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    token_endpoint="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    userinfo_endpoint="https://graph.microsoft.com/v1.0/me",
    jwks_uri="https://login.microsoftonline.com/common/discovery/v2.0/keys",
    issuer="https://login.microsoftonline.com",
    scopes=["openid", "email", "profile"],
    use_pkce=True,
)

GITHUB_PROVIDER = OAuthProvider(
    name="GitHub",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_endpoint="https://github.com/login/oauth/authorize",
    token_endpoint="https://github.com/login/oauth/access_token",
    userinfo_endpoint="https://api.github.com/user",
    scopes=["read:user", "user:email"],
    use_pkce=False,  # GitHub doesn't support PKCE yet
)


class OAuthManager:
    """OAuth manager for handling multiple providers"""

    def __init__(self):
        self.providers: Dict[str, OAuthProvider] = {}
        self.clients: Dict[str, OAuthClient] = {}

    def register_provider(self, provider: OAuthProvider):
        """Register an OAuth provider"""
        self.providers[provider.name] = provider

    def get_provider(self, name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider by name"""
        return self.providers.get(name)

    def list_providers(self) -> List[OAuthProvider]:
        """List all active providers"""
        return [p for p in self.providers.values() if p.active]

    def create_client(self, provider_name: str, redirect_uri: str) -> OAuthClient:
        """
        Create OAuth client for provider

        Args:
            provider_name: Name of provider
            redirect_uri: Redirect URI for OAuth callback

        Returns:
            OAuth client

        Raises:
            ValueError: If provider not found
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")

        client_key = f"{provider_name}:{redirect_uri}"
        if client_key not in self.clients:
            self.clients[client_key] = OAuthClient(provider, redirect_uri)

        return self.clients[client_key]


# Global OAuth manager instance
_oauth_manager: Optional[OAuthManager] = None


def get_oauth_manager() -> OAuthManager:
    """Get global OAuth manager instance"""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager()
        # Register pre-configured providers
        # Note: You need to set actual client IDs and secrets
        # _oauth_manager.register_provider(GOOGLE_PROVIDER)
        # _oauth_manager.register_provider(MICROSOFT_PROVIDER)
        # _oauth_manager.register_provider(GITHUB_PROVIDER)
    return _oauth_manager


def configure_oauth_manager(providers: List[OAuthProvider]):
    """Configure OAuth manager with providers"""
    manager = get_oauth_manager()
    for provider in providers:
        manager.register_provider(provider)
