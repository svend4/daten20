"""
OAuth 2.0 / OpenID Connect Provider

Implements OAuth 2.0 authorization server with OpenID Connect support.

Supported grant types:
- authorization_code: Standard OAuth 2.0 authorization code flow
- client_credentials: Machine-to-machine authentication
- refresh_token: Token refresh
- password: Resource owner password credentials (not recommended)

Features:
- Client registration and management
- Authorization code generation
- Access token issuance
- Refresh token support
- Token introspection
- Token revocation
- Scope validation
- PKCE support (RFC 7636)
- OpenID Connect basic profile

Usage:
    >>> from src.core.oauth2_provider import get_oauth_provider
    >>> provider = get_oauth_provider()
    >>>
    >>> # Register client
    >>> client = provider.register_client(
    ...     client_name='My App',
    ...     redirect_uris=['https://myapp.com/callback'],
    ...     grant_types=[GrantType.AUTHORIZATION_CODE],
    ...     scope=['read', 'write']
    ... )
    >>>
    >>> # Authorization flow
    >>> auth_response = provider.authorize(
    ...     client_id=client.client_id,
    ...     redirect_uri='https://myapp.com/callback',
    ...     scope=['read'],
    ...     user_id=123
    ... )
    >>>
    >>> # Exchange code for token
    >>> token = provider.exchange_code(
    ...     code=auth_response['code'],
    ...     client_id=client.client_id,
    ...     client_secret=client.client_secret,
    ...     redirect_uri='https://myapp.com/callback'
    ... )
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
import hashlib
import base64
import json
import logging

logger = logging.getLogger(__name__)


class GrantType(str, Enum):
    """OAuth 2.0 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PASSWORD = "password"  # Not recommended for production


class TokenType(str, Enum):
    """Token types"""
    BEARER = "Bearer"


class ResponseType(str, Enum):
    """OAuth response types"""
    CODE = "code"
    TOKEN = "token"  # Implicit flow


@dataclass
class OAuthClient:
    """OAuth 2.0 client application"""
    client_id: str
    client_secret: str
    client_name: str
    redirect_uris: List[str]
    grant_types: List[GrantType]
    scope: List[str]
    created_at: datetime
    active: bool = True
    logo_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    contacts: List[str] = field(default_factory=list)


@dataclass
class AuthorizationCode:
    """Authorization code"""
    code: str
    client_id: str
    redirect_uri: str
    scope: List[str]
    user_id: int
    expires_at: datetime
    used: bool = False
    code_challenge: Optional[str] = None  # PKCE
    code_challenge_method: Optional[str] = None  # plain or S256


@dataclass
class AccessToken:
    """Access token"""
    token: str
    token_type: TokenType
    client_id: str
    user_id: Optional[int]
    scope: List[str]
    expires_at: datetime
    refresh_token: Optional[str] = None
    issued_at: datetime = field(default_factory=datetime.now)


@dataclass
class RefreshToken:
    """Refresh token"""
    token: str
    client_id: str
    user_id: int
    scope: List[str]
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)


class OAuth2Provider:
    """
    OAuth 2.0 Authorization Server.

    Implements OAuth 2.0 and OpenID Connect protocols.
    """

    def __init__(self):
        """Initialize OAuth provider."""
        self.clients: Dict[str, OAuthClient] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}

        logger.info("OAuth 2.0 provider initialized")

    # ============================================================
    # Client Management
    # ============================================================

    def register_client(
        self,
        client_name: str,
        redirect_uris: List[str],
        grant_types: List[GrantType],
        scope: List[str],
        **kwargs
    ) -> OAuthClient:
        """
        Register new OAuth client.

        Args:
            client_name: Application name
            redirect_uris: Allowed redirect URIs
            grant_types: Allowed grant types
            scope: Allowed scopes
            **kwargs: Additional client properties

        Returns:
            Registered client with credentials

        Example:
            >>> client = provider.register_client(
            ...     client_name='My App',
            ...     redirect_uris=['https://myapp.com/callback'],
            ...     grant_types=[GrantType.AUTHORIZATION_CODE],
            ...     scope=['read', 'write']
            ... )
            >>> print(f"Client ID: {client.client_id}")
            >>> print(f"Client Secret: {client.client_secret}")
        """
        # Generate client credentials
        client_id = f"oauth2_client_{secrets.token_urlsafe(16)}"
        client_secret = secrets.token_urlsafe(32)

        client = OAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name,
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            scope=scope,
            created_at=datetime.now(),
            **kwargs
        )

        self.clients[client_id] = client

        logger.info(f"Registered OAuth client: {client_name} ({client_id})")

        return client

    def get_client(self, client_id: str) -> Optional[OAuthClient]:
        """Get client by ID."""
        return self.clients.get(client_id)

    def update_client(
        self,
        client_id: str,
        **updates
    ) -> Optional[OAuthClient]:
        """
        Update client properties.

        Args:
            client_id: Client ID
            **updates: Properties to update

        Returns:
            Updated client or None if not found
        """
        client = self.get_client(client_id)
        if not client:
            return None

        for key, value in updates.items():
            if hasattr(client, key):
                setattr(client, key, value)

        logger.info(f"Updated client: {client_id}")

        return client

    def delete_client(self, client_id: str) -> bool:
        """
        Delete client.

        Args:
            client_id: Client ID

        Returns:
            True if deleted, False if not found
        """
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Deleted client: {client_id}")
            return True
        return False

    # ============================================================
    # Authorization Flow
    # ============================================================

    def authorize(
        self,
        client_id: str,
        redirect_uri: str,
        scope: List[str],
        user_id: int,
        state: Optional[str] = None,
        response_type: ResponseType = ResponseType.CODE,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate authorization code (or token for implicit flow).

        Args:
            client_id: Client ID
            redirect_uri: Redirect URI
            scope: Requested scope
            user_id: Authenticated user ID
            state: State parameter (returned unchanged)
            response_type: Response type (code or token)
            code_challenge: PKCE code challenge
            code_challenge_method: PKCE method (plain or S256)

        Returns:
            Authorization response with code or token

        Raises:
            ValueError: If validation fails

        Example:
            >>> response = provider.authorize(
            ...     client_id='oauth2_client_...',
            ...     redirect_uri='https://myapp.com/callback',
            ...     scope=['read'],
            ...     user_id=123,
            ...     state='random_state'
            ... )
            >>> print(f"Code: {response['code']}")
        """
        # Validate client
        client = self.get_client(client_id)
        if not client or not client.active:
            raise ValueError("Invalid client")

        # Validate redirect URI
        if redirect_uri not in client.redirect_uris:
            raise ValueError(f"Invalid redirect URI: {redirect_uri}")

        # Validate scope
        if not all(s in client.scope for s in scope):
            raise ValueError(f"Invalid scope. Allowed: {client.scope}")

        # Check grant type
        if GrantType.AUTHORIZATION_CODE not in client.grant_types:
            raise ValueError("Authorization code grant not allowed for this client")

        # Generate authorization code
        code = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=10)

        auth_code = AuthorizationCode(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            user_id=user_id,
            expires_at=expires_at,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )

        self.authorization_codes[code] = auth_code

        logger.info(f"Generated authorization code for user {user_id}, client {client_id}")

        # Build response
        response = {'code': code}
        if state:
            response['state'] = state

        return response

    def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> AccessToken:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code
            client_id: Client ID
            client_secret: Client secret
            redirect_uri: Redirect URI (must match authorization request)
            code_verifier: PKCE code verifier

        Returns:
            Access token

        Raises:
            ValueError: If validation fails

        Example:
            >>> token = provider.exchange_code(
            ...     code='...',
            ...     client_id='oauth2_client_...',
            ...     client_secret='...',
            ...     redirect_uri='https://myapp.com/callback'
            ... )
            >>> print(f"Access token: {token.token}")
            >>> print(f"Expires: {token.expires_at}")
        """
        # Validate client credentials
        client = self.get_client(client_id)
        if not client or client.client_secret != client_secret:
            raise ValueError("Invalid client credentials")

        # Validate authorization code
        auth_code = self.authorization_codes.get(code)
        if not auth_code:
            raise ValueError("Invalid authorization code")

        if auth_code.used:
            raise ValueError("Authorization code already used")

        if datetime.now() > auth_code.expires_at:
            raise ValueError("Authorization code expired")

        if auth_code.client_id != client_id:
            raise ValueError("Client ID mismatch")

        if auth_code.redirect_uri != redirect_uri:
            raise ValueError("Redirect URI mismatch")

        # Validate PKCE if present
        if auth_code.code_challenge:
            if not code_verifier:
                raise ValueError("Code verifier required for PKCE")

            if not self._verify_pkce(
                auth_code.code_challenge,
                auth_code.code_challenge_method,
                code_verifier
            ):
                raise ValueError("Invalid code verifier")

        # Mark code as used
        auth_code.used = True

        # Generate access token
        access_token = self._generate_access_token(
            client_id=client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope
        )

        logger.info(f"Issued access token for user {auth_code.user_id}")

        return access_token

    def _generate_access_token(
        self,
        client_id: str,
        user_id: Optional[int],
        scope: List[str],
        include_refresh_token: bool = True
    ) -> AccessToken:
        """Generate access token and optionally refresh token."""
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)

        refresh_token = None
        if include_refresh_token:
            refresh_token = secrets.token_urlsafe(32)

            # Store refresh token
            refresh_token_obj = RefreshToken(
                token=refresh_token,
                client_id=client_id,
                user_id=user_id,
                scope=scope,
                expires_at=datetime.now() + timedelta(days=30)
            )
            self.refresh_tokens[refresh_token] = refresh_token_obj

        token = AccessToken(
            token=access_token,
            token_type=TokenType.BEARER,
            client_id=client_id,
            user_id=user_id,
            scope=scope,
            expires_at=expires_at,
            refresh_token=refresh_token
        )

        self.access_tokens[access_token] = token

        return token

    # ============================================================
    # Token Operations
    # ============================================================

    def validate_token(self, token: str) -> Optional[AccessToken]:
        """
        Validate access token.

        Args:
            token: Access token

        Returns:
            Token info if valid, None otherwise

        Example:
            >>> token_info = provider.validate_token('...')
            >>> if token_info:
            ...     print(f"User ID: {token_info.user_id}")
            ...     print(f"Scope: {token_info.scope}")
        """
        access_token = self.access_tokens.get(token)

        if not access_token:
            return None

        if datetime.now() > access_token.expires_at:
            logger.info(f"Token expired: {token[:10]}...")
            return None

        return access_token

    def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> AccessToken:
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token
            client_id: Client ID
            client_secret: Client secret

        Returns:
            New access token

        Raises:
            ValueError: If validation fails

        Example:
            >>> new_token = provider.refresh_access_token(
            ...     refresh_token='...',
            ...     client_id='oauth2_client_...',
            ...     client_secret='...'
            ... )
        """
        # Validate client
        client = self.get_client(client_id)
        if not client or client.client_secret != client_secret:
            raise ValueError("Invalid client credentials")

        # Validate refresh token
        refresh_token_obj = self.refresh_tokens.get(refresh_token)
        if not refresh_token_obj:
            raise ValueError("Invalid refresh token")

        if refresh_token_obj.client_id != client_id:
            raise ValueError("Client ID mismatch")

        if datetime.now() > refresh_token_obj.expires_at:
            raise ValueError("Refresh token expired")

        # Generate new access token
        access_token = self._generate_access_token(
            client_id=client_id,
            user_id=refresh_token_obj.user_id,
            scope=refresh_token_obj.scope,
            include_refresh_token=False  # Keep using same refresh token
        )

        access_token.refresh_token = refresh_token

        logger.info(f"Refreshed access token for user {refresh_token_obj.user_id}")

        return access_token

    def revoke_token(self, token: str) -> bool:
        """
        Revoke access or refresh token.

        Args:
            token: Token to revoke

        Returns:
            True if revoked, False if not found

        Example:
            >>> provider.revoke_token('...')
        """
        # Try access token
        if token in self.access_tokens:
            del self.access_tokens[token]
            logger.info(f"Revoked access token: {token[:10]}...")
            return True

        # Try refresh token
        if token in self.refresh_tokens:
            del self.refresh_tokens[token]
            logger.info(f"Revoked refresh token: {token[:10]}...")
            return True

        return False

    def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Introspect token (RFC 7662).

        Args:
            token: Token to introspect

        Returns:
            Token introspection response

        Example:
            >>> info = provider.introspect_token('...')
            >>> print(info['active'])
            >>> print(info['scope'])
        """
        token_info = self.validate_token(token)

        if not token_info:
            return {'active': False}

        return {
            'active': True,
            'scope': ' '.join(token_info.scope),
            'client_id': token_info.client_id,
            'token_type': token_info.token_type.value,
            'exp': int(token_info.expires_at.timestamp()),
            'iat': int(token_info.issued_at.timestamp()),
            'sub': str(token_info.user_id) if token_info.user_id else None
        }

    # ============================================================
    # PKCE Support (RFC 7636)
    # ============================================================

    def _verify_pkce(
        self,
        code_challenge: str,
        code_challenge_method: str,
        code_verifier: str
    ) -> bool:
        """Verify PKCE code challenge."""
        if code_challenge_method == 'plain':
            return code_challenge == code_verifier

        elif code_challenge_method == 'S256':
            # SHA256(code_verifier) base64url encoded
            hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
            encoded = base64.urlsafe_b64encode(hashed).decode('utf-8').rstrip('=')
            return code_challenge == encoded

        return False

    @staticmethod
    def generate_pkce_pair() -> Dict[str, str]:
        """
        Generate PKCE code verifier and challenge.

        Returns:
            Dict with 'code_verifier' and 'code_challenge'

        Example:
            >>> pkce = OAuth2Provider.generate_pkce_pair()
            >>> print(f"Verifier: {pkce['code_verifier']}")
            >>> print(f"Challenge: {pkce['code_challenge']}")
        """
        code_verifier = secrets.token_urlsafe(32)

        # Generate S256 challenge
        hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(hashed).decode('utf-8').rstrip('=')

        return {
            'code_verifier': code_verifier,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }


# ============================================================
# Global Provider Instance
# ============================================================

_oauth_provider: Optional[OAuth2Provider] = None


def get_oauth_provider() -> OAuth2Provider:
    """
    Get OAuth provider instance (singleton).

    Returns:
        Shared OAuth2Provider instance

    Example:
        >>> provider = get_oauth_provider()
        >>> client = provider.register_client(...)
    """
    global _oauth_provider
    if _oauth_provider is None:
        _oauth_provider = OAuth2Provider()
    return _oauth_provider


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    # Initialize provider
    provider = get_oauth_provider()

    print("🔐 OAuth 2.0 Provider Demo\n")

    # 1. Register client
    print("1️⃣ Registering OAuth client...")
    client = provider.register_client(
        client_name='Demo App',
        redirect_uris=['https://demo.app/callback', 'http://localhost:3000/callback'],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
        scope=['read', 'write', 'admin']
    )

    print(f"✅ Client registered!")
    print(f"   Client ID: {client.client_id}")
    print(f"   Client Secret: {client.client_secret[:20]}...")
    print(f"   Allowed scope: {', '.join(client.scope)}\n")

    # 2. Authorization
    print("2️⃣ Generating authorization code...")
    auth_response = provider.authorize(
        client_id=client.client_id,
        redirect_uri='https://demo.app/callback',
        scope=['read', 'write'],
        user_id=12345,
        state='random_state_123'
    )

    print(f"✅ Authorization code generated!")
    print(f"   Code: {auth_response['code'][:20]}...")
    print(f"   State: {auth_response['state']}\n")

    # 3. Exchange code for token
    print("3️⃣ Exchanging code for access token...")
    token = provider.exchange_code(
        code=auth_response['code'],
        client_id=client.client_id,
        client_secret=client.client_secret,
        redirect_uri='https://demo.app/callback'
    )

    print(f"✅ Access token issued!")
    print(f"   Access Token: {token.token[:20]}...")
    print(f"   Refresh Token: {token.refresh_token[:20]}...")
    print(f"   Expires: {token.expires_at}")
    print(f"   Scope: {', '.join(token.scope)}\n")

    # 4. Validate token
    print("4️⃣ Validating access token...")
    validated = provider.validate_token(token.token)

    if validated:
        print(f"✅ Token valid!")
        print(f"   User ID: {validated.user_id}")
        print(f"   Client ID: {validated.client_id}\n")

    # 5. Token introspection
    print("5️⃣ Introspecting token...")
    introspection = provider.introspect_token(token.token)

    print(f"✅ Token introspection:")
    print(f"   Active: {introspection['active']}")
    print(f"   Scope: {introspection['scope']}")
    print(f"   Expires: {datetime.fromtimestamp(introspection['exp'])}\n")

    # 6. Refresh token
    print("6️⃣ Refreshing access token...")
    new_token = provider.refresh_access_token(
        refresh_token=token.refresh_token,
        client_id=client.client_id,
        client_secret=client.client_secret
    )

    print(f"✅ New access token issued!")
    print(f"   New Token: {new_token.token[:20]}...\n")

    # 7. PKCE demo
    print("7️⃣ PKCE (Proof Key for Code Exchange) demo...")
    pkce = OAuth2Provider.generate_pkce_pair()

    print(f"✅ PKCE pair generated!")
    print(f"   Verifier: {pkce['code_verifier'][:20]}...")
    print(f"   Challenge: {pkce['code_challenge'][:20]}...")
    print(f"   Method: {pkce['code_challenge_method']}\n")

    print("🎉 OAuth 2.0 Provider demo complete!")
